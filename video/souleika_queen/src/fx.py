"""Effets de lumière et étalonnage. Tout est procédural et déterministe (même rendu à chaque exécution).

Les effets travaillent sur des images float32 RGB dans [0, 1], au format 1080x1920.
Ils animent la lumière et le cadre, jamais l'anatomie.
"""
import math

import cv2
import numpy as np

from common import H, W, clamp, rgb

# --------------------------------------------------------------------------- étalonnage

GRADES = {
    # exposure (diaph), contrast (0-1), warmth (+ = chaud), sat, lift (ombres teintées)
    "warm": dict(exposure=0.0, contrast=0.10, warmth=0.45, sat=1.03, lift=(0.018, 0.026, 0.048)),
    "gold": dict(exposure=0.03, contrast=0.13, warmth=0.70, sat=1.06, lift=(0.020, 0.024, 0.040)),
    "mint": dict(exposure=0.10, contrast=0.04, warmth=-0.05, sat=0.93, lift=(0.030, 0.052, 0.046),
                 gain=(0.985, 1.0, 0.985)),
}
_LUTS = {}


def grade_lut(name, exposure=0.0):
    key = (name, round(exposure, 3))
    if key not in _LUTS:
        g = GRADES[name]
        x = np.linspace(0, 1, 256, dtype=np.float32)
        luts = []
        warm = (0.045, 0.012, -0.05)
        gain = g.get("gain", (1, 1, 1))
        for c in range(3):
            v = np.clip(x * 2 ** (g["exposure"] + exposure), 0, 1)
            s = v * v * (3 - 2 * v)
            v = (1 - g["contrast"]) * v + g["contrast"] * s
            v = v + g["warmth"] * warm[c] * v * v                # chaleur surtout dans les hautes lumières
            v = v + g["lift"][c] * (1 - v) ** 3                   # ombres légèrement bleu nuit / menthe
            v = v * gain[c]
            luts.append(np.clip(v * 255 + 0.5, 0, 255).astype(np.uint8))
        _LUTS[key] = (np.stack(luts, axis=1)[None], g["sat"])
    return _LUTS[key]


def apply_grade(img_u8, name, exposure=0.0):
    lut, sat = grade_lut(name, exposure)
    out = cv2.LUT(img_u8, lut)
    f = out.astype(np.float32) * (1 / 255)
    if abs(sat - 1) > 1e-3:
        lum = f @ np.float32([0.2126, 0.7152, 0.0722])
        f = lum[..., None] + sat * (f - lum[..., None])
    return f


# --------------------------------------------------------------------------- calques fixes

def make_vignette(strength=0.26):
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    dx = (x - W / 2) / (W / 2)
    dy = (y - H / 2) / (H / 2)
    r = np.sqrt(dx * dx * 0.9 + dy * dy * 0.75)
    t = np.clip((r - 0.45) / 0.75, 0, 1)
    return (1 - strength * t * t * (3 - 2 * t))[..., None].astype(np.float32)


def make_grain(n=8, sigma=0.010, seed=7):
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(n):
        g = rng.normal(0, 1, (H // 2, W // 2)).astype(np.float32)
        g = cv2.resize(g, (W, H), interpolation=cv2.INTER_LINEAR)   # grain fin, légèrement adouci
        out.append((g * sigma)[..., None])
    return out


# --------------------------------------------------------------------------- particules dorées

def _sprite(r, bokeh):
    n = int(r * 3) * 2 + 1
    y, x = np.mgrid[0:n, 0:n].astype(np.float32) - n // 2
    d = np.sqrt(x * x + y * y)
    if bokeh:
        disc = np.clip((r - d) / 1.6, 0, 1)
        ring = np.exp(-((d - r * 0.86) ** 2) / (2 * (r * 0.09 + 0.6) ** 2)) * 0.35
        glow = np.exp(-(d ** 2) / (2 * (r * 1.1) ** 2)) * 0.25
        a = disc * 0.55 + ring * disc + glow
    else:
        a = np.exp(-(d ** 2) / (2 * (r * 0.5) ** 2)) + 0.25 * np.exp(-(d ** 2) / (2 * (r * 1.6) ** 2))
    return (a / a.max()).astype(np.float32)


class Particles:
    """Poussière d'or et bokeh discrets, essentiellement en périphérie (colonnes latérales)."""

    def __init__(self, n=72, seed=11):
        rng = np.random.default_rng(seed)
        self.p = []
        for i in range(n):
            near = rng.random() < 0.28
            r = rng.uniform(9, 22) if near else rng.uniform(1.6, 4.2)
            side = rng.random() < 0.5
            x0 = W * (rng.uniform(0.0, 0.23) if side else rng.uniform(0.77, 1.0))
            self.p.append(dict(
                x0=x0, y0=rng.uniform(0, H), vy=-rng.uniform(14, 46) * (1.4 if near else 1.0),
                amp=rng.uniform(5, 22), fq=rng.uniform(0.04, 0.16), ph=rng.uniform(0, 6.28),
                tw=rng.uniform(0.3, 1.1), tph=rng.uniform(0, 6.28),
                a=rng.uniform(0.18, 0.34) if near else rng.uniform(0.45, 0.95),
                spr=_sprite(r, near), rank=rng.random(), warm=rng.uniform(-1, 1)))
        self.bursts = []

    def add_burst(self, t0, n, seed):
        rng = np.random.default_rng(seed)
        for _ in range(n):
            side = rng.random() < 0.5
            r = rng.uniform(1.8, 5.0)
            self.bursts.append(dict(
                t0=t0, x0=W * (rng.uniform(0.0, 0.2) if side else rng.uniform(0.8, 1.0)),
                y0=H * rng.uniform(0.55, 1.0), vx=(1 if side else -1) * rng.uniform(-40, 120),
                vy=-rng.uniform(260, 620), life=rng.uniform(1.0, 1.9), a=rng.uniform(0.6, 1.0),
                spr=_sprite(r, False)))

    @staticmethod
    def _add(img, spr, x, y, col, a):
        n = spr.shape[0]
        x0, y0 = int(x) - n // 2, int(y) - n // 2
        x1, y1 = x0 + n, y0 + n
        if x1 <= 0 or y1 <= 0 or x0 >= W or y0 >= H:
            return
        sx0, sy0 = max(0, -x0), max(0, -y0)
        sx1, sy1 = n - max(0, x1 - W), n - max(0, y1 - H)
        reg = img[max(0, y0):min(H, y1), max(0, x0):min(W, x1)]
        reg += spr[sy0:sy1, sx0:sx1, None] * (col * a)

    def draw(self, img, t, density, tint="gold"):
        base = np.float32(rgb("#EBD39C") if tint == "gold" else rgb("#EAF4EC"))
        warm = np.float32([1.0, 0.86, 0.62])
        if density > 0.01:
            for q in self.p:
                if q["rank"] > density:
                    continue
                fade = clamp((density - q["rank"]) / 0.08)
                y = (q["y0"] + q["vy"] * t) % (H + 120) - 60
                x = q["x0"] + q["amp"] * math.sin(2 * math.pi * q["fq"] * t + q["ph"])
                tw = 0.65 + 0.35 * math.sin(2 * math.pi * q["tw"] * t + q["tph"])
                col = base * (1 + 0.06 * q["warm"]) if tint != "gold" else base + (warm - base) * max(0.0, q["warm"]) * 0.3
                self._add(img, q["spr"], x, y, col, q["a"] * tw * fade)
        for b in self.bursts:
            u = (t - b["t0"]) / b["life"]
            if 0 <= u <= 1:
                dt = t - b["t0"]
                x = b["x0"] + b["vx"] * dt
                y = b["y0"] + b["vy"] * dt + 120 * dt * dt
                a = b["a"] * (1 - u) ** 1.5 * min(1.0, u * 12)
                self._add(img, b["spr"], x, y, base, a)


# --------------------------------------------------------------------------- lumières

_LW, _LH = W // 8, H // 8
_ly, _lx = np.mgrid[0:_LH, 0:_LW].astype(np.float32)


def light_leaks(t, intensity):
    """Fuites de lumière chaudes qui dérivent lentement sur les bords (fusion écran)."""
    if intensity <= 0.01:
        return None
    blobs = [
        ((-0.08 + 0.10 * math.sin(0.11 * t), 0.18 + 0.22 * math.sin(0.07 * t + 1.0)), 0.42, (1.0, 0.62, 0.26), 0.55),
        ((1.06 + 0.08 * math.sin(0.09 * t + 2.0), 0.72 + 0.18 * math.sin(0.06 * t + 2.5)), 0.46, (1.0, 0.74, 0.42), 0.45),
        ((0.5 + 0.45 * math.sin(0.05 * t + 4.0), -0.10 + 0.05 * math.sin(0.13 * t)), 0.38, (1.0, 0.55, 0.38), 0.25),
    ]
    acc = np.zeros((_LH, _LW, 3), np.float32)
    for (bx, by), rad, col, amp in blobs:
        d2 = ((_lx / _LW - bx) * _LW / _LH) ** 2 + (_ly / _LH - by) ** 2
        acc += np.exp(-d2 / (2 * (rad * 0.62) ** 2))[..., None] * (np.float32(col) * amp)
    return cv2.resize(acc * intensity, (W, H), interpolation=cv2.INTER_CUBIC)


def god_rays(t, intensity):
    """Rayons de lumière très doux venant du haut (séquence spirituelle)."""
    if intensity <= 0.01:
        return None
    sx, sy = 0.72 * _LW, -0.18 * _LH
    ang = np.arctan2(_ly - sy, _lx - sx)
    r = np.sqrt((_lx - sx) ** 2 + (_ly - sy) ** 2) / _LH
    rays = (0.5 + 0.5 * np.sin(23 * ang + 0.25 * t)) * (0.5 + 0.5 * np.sin(41 * ang - 0.17 * t + 1.3))
    rays += 0.6 * (0.5 + 0.5 * np.sin(11 * ang + 0.11 * t + 2.0))
    rays *= np.exp(-r * 1.25) * (0.75 + 0.25 * math.sin(0.6 * t))
    rays = cv2.GaussianBlur(rays.astype(np.float32), (0, 0), 1.6)
    col = np.float32(rgb("#FFF8E8")) * 0.85 + np.float32(rgb("mint")) * 0.15
    return cv2.resize(rays[..., None] * col * intensity, (W, H), interpolation=cv2.INTER_CUBIC)


def bloom(img, strength):
    """Halo doux sur les hautes lumières (rendu « pellicule »)."""
    if strength <= 0.01:
        return img
    small = cv2.resize(img, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    lum = small @ np.float32([0.2126, 0.7152, 0.0722])
    m = np.clip((lum - 0.62) / 0.38, 0, 1)[..., None]
    hi = small * m
    hi = cv2.GaussianBlur(hi, (0, 0), 9) + 0.5 * cv2.GaussianBlur(hi, (0, 0), 22)
    hi = cv2.resize(hi, (W, H), interpolation=cv2.INTER_LINEAR)
    return img + hi * np.float32([1.0, 0.86, 0.66]) * strength


def screen(img, layer):
    return 1 - (1 - img) * (1 - np.clip(layer, 0, 1))


_ys = np.arange(H, dtype=np.float32)
_xs = np.arange(W, dtype=np.float32)


def flare(img, t, ev):
    """Traînée anamorphique dorée qui traverse le cadre horizontalement (lumière, pas de flash blanc)."""
    u = (t - ev["t"]) / ev["dur"]
    if not 0 <= u <= 1:
        return img
    env = math.sin(math.pi * u) ** 1.5 * ev["strength"]
    cx = W * (-0.15 + 1.3 * u)
    cy = H * ev["y"]
    y0, y1 = int(max(0, cy - 160)), int(min(H, cy + 160))
    dy = _ys[y0:y1] - cy
    core = np.exp(-dy ** 2 / (2 * 3.0 ** 2)) + 0.35 * np.exp(-dy ** 2 / (2 * 22.0 ** 2)) + 0.12 * np.exp(-dy ** 2 / (2 * 70.0 ** 2))
    horiz = np.exp(-np.abs(_xs - cx) / 330.0)
    band = core[:, None] * horiz[None, :] * env
    col = np.float32([1.0, 0.82, 0.52])
    img[y0:y1] = screen(img[y0:y1], band[..., None] * col)
    # point lumineux
    gy0, gy1 = int(max(0, cy - 140)), int(min(H, cy + 140))
    gx0, gx1 = int(max(0, cx - 140)), int(min(W, cx + 140))
    if gx1 > gx0 and gy1 > gy0:
        gy = _ys[gy0:gy1, None] - cy
        gx = _xs[None, gx0:gx1] - cx
        g = np.exp(-(gx ** 2 + gy ** 2) / (2 * 42.0 ** 2)) * env * 0.9
        img[gy0:gy1, gx0:gx1] = screen(img[gy0:gy1, gx0:gx1], g[..., None] * col)
    return img


def zoom_blur(img, strength, center=(0.5, 0.5)):
    """Flou radial (transition « traversée ») : moyenne de copies légèrement agrandies."""
    if strength <= 0.02:
        return img
    n = 6
    acc = img.copy()
    cx, cy = W * center[0], H * center[1]
    for i in range(1, n):
        k = 1 + 0.07 * strength * i / (n - 1)
        A = np.float32([[k, 0, cx - k * cx], [0, k, cy - k * cy]])
        acc += cv2.warpAffine(img, A, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    return acc / n
