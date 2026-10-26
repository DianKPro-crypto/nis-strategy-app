"""Effets « vivants » des quatre photos artistiques (P13 à P16).

Seuls les éléments surnaturels bougent (papillons, pétales, lumière dorée, éclats d'or et cendres) ;
le visage, le corps et les cheveux restent intacts. Chaque élément est une fonction pure du temps
(rendu parallèle par segments sans raccord visible) et vit dans les coordonnées de la photo, pour
suivre les mouvements de caméra. Papillons et pétales sont découpés dans les photos elles-mêmes.
Le tempo et les mots du chant pilotent les battements d'ailes, les pulsations et les envols.
"""
import math

import cv2
import numpy as np

from common import H, W, clamp

GOLD = np.float32([1.0, 0.78, 0.40])
GLINT = np.float32([1.0, 0.92, 0.70])


def _hash(*v):
    x = math.sin(sum(a * b for a, b in zip(v, (12.9898, 78.233, 37.719, 94.673))) + 0.5) * 43758.5453
    return x - math.floor(x)


def _smooth(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def put(img, rgb, a, cx, cy, sx, sy, ang, alpha, add=False):
    """Pose un sprite (rgb HxWx3, a HxW) centré en (cx, cy), échelles sx/sy, rotation ang (rad)."""
    if alpha <= 0.004 or sx <= 0.01 or sy <= 0.01:
        return
    h, w = a.shape
    ca, sa = math.cos(ang), math.sin(ang)
    m00, m01, m10, m11 = ca * sx, -sa * sy, sa * sx, ca * sy
    ex = (abs(m00) * w + abs(m01) * h) / 2 + 2
    ey = (abs(m10) * w + abs(m11) * h) / 2 + 2
    x0, y0 = int(cx - ex), int(cy - ey)
    bw, bh = int(2 * ex) + 2, int(2 * ey) + 2
    X0, Y0, X1, Y1 = max(0, x0), max(0, y0), min(img.shape[1], x0 + bw), min(img.shape[0], y0 + bh)
    if X1 <= X0 or Y1 <= Y0:
        return
    tx = cx - x0 - (m00 * w / 2 + m01 * h / 2)
    ty = cy - y0 - (m10 * w / 2 + m11 * h / 2)
    A = np.float32([[m00, m01, tx], [m10, m11, ty]])
    aw = cv2.warpAffine(a, A, (bw, bh), flags=cv2.INTER_LINEAR, borderValue=0)[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0]
    reg = img[Y0:Y1, X0:X1]
    if rgb.ndim == 1:
        col = rgb
    else:
        col = cv2.warpAffine(rgb, A, (bw, bh), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0]
    k = (aw * alpha)[..., None]
    if add:
        reg += col * k
    else:
        reg += (col - reg) * k


def _dot(r):
    n = int(r * 4) * 2 + 3
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32) - n // 2
    d2 = xx * xx + yy * yy
    a = np.exp(-d2 / (2 * (r * 0.45) ** 2)) + 0.3 * np.exp(-d2 / (2 * (r * 1.4) ** 2))
    return (a / a.max()).astype(np.float32)


def _star(r):
    """Étoile à quatre branches (scintillement)."""
    n = int(r * 6) * 2 + 3
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32) - n // 2
    core = np.exp(-(xx * xx + yy * yy) / (2 * (r * 0.35) ** 2))
    arms = np.exp(-np.abs(yy) / (r * 0.10)) * np.exp(-np.abs(xx) / (r * 1.6)) + \
        np.exp(-np.abs(xx) / (r * 0.10)) * np.exp(-np.abs(yy) / (r * 1.6))
    a = core + 0.7 * arms
    return np.clip(a / a.max(), 0, 1).astype(np.float32)


def _shard(seed, r):
    """Éclat de cendre : polygone irrégulier sombre."""
    rng = np.random.default_rng(seed)
    n = int(r * 2.6) + 4
    k = rng.integers(5, 8)
    ang = np.sort(rng.uniform(0, 2 * np.pi, k))
    rad = r * rng.uniform(0.55, 1.0, k)
    pts = np.stack([n / 2 + rad * np.cos(ang), n / 2 + rad * np.sin(ang)], 1).astype(np.int32)
    m = np.zeros((n, n), np.uint8)
    cv2.fillPoly(m, [pts], 255, lineType=cv2.LINE_AA)
    return (m / 255.0).astype(np.float32)


def _curve(pts, r):
    """Point sur une polyligne (paramètre 0-1, extrapolée au-delà)."""
    pts = np.asarray(pts, np.float32)
    seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
    L = seg.sum()
    d = r * L
    if d <= 0:
        dirv = (pts[1] - pts[0]) / seg[0]
        return pts[0] + dirv * d, dirv
    acc = 0.0
    for i, l in enumerate(seg):
        if d <= acc + l or i == len(seg) - 1:
            u = (d - acc) / l
            dirv = (pts[i + 1] - pts[i]) / l
            return pts[i] + (pts[i + 1] - pts[i]) * u, dirv
        acc += l


class Live:
    """Classe de base : conversion photo -> cadre, protection du visage et des mains, tempo."""

    def __init__(self, photo, cfg, beats):
        self.ph, self.cfg = photo, cfg
        self.beats = np.asarray(beats)
        self.period = float(np.median(np.diff(self.beats)))

    def prepare(self, tr):
        s, tx, ty = tr
        self.s, self.tx, self.ty = s, tx, ty
        self.boxes = []
        zones = {**self.ph.protect, **self.cfg.get("zones", {})}       # zones resserrées propres aux effets
        guard = self.cfg.get("garde", {})
        for name, (x0, y0, x1, y1) in zones.items():
            strength = guard.get(name, 1.0 if name.startswith(("visage", "lunettes", "bouche")) else 0.65)
            self.boxes.append((x0 * self.ph.w * s + tx, y0 * self.ph.h * s + ty,
                               x1 * self.ph.w * s + tx, y1 * self.ph.h * s + ty, strength))

    def xy(self, u, v):
        return u * self.ph.w * self.s + self.tx, v * self.ph.h * self.s + self.ty

    def guard(self, x, y, r=0.0):
        """1 loin des zones protégées, tend vers 0 dessus (fondu sur ~80 px)."""
        f = 1.0
        for x0, y0, x1, y1, st in self.boxes:
            dx = max(x0 - x, 0, x - x1)
            dy = max(y0 - y, 0, y - y1)
            d = math.hypot(dx, dy) - r - 12
            f = min(f, 1 - st * (1 - _smooth(d / 80.0)))
        return f

    def beat_info(self, t):
        i = int(np.searchsorted(self.beats, t, side="right")) - 1
        if i < 0:
            return t / self.period, 1e9
        frac = (t - self.beats[i]) / self.period
        return i + frac, t - self.beats[i]

    def pulse(self, t, decay=0.22):
        _, since = self.beat_info(t)
        return math.exp(-since / decay)


def _key_sprites(src, boxes, alpha_fn, pad=6):
    out = []
    a_full = alpha_fn(src)
    for x, y, w, h in boxes:
        crop = src[y - pad:y + h + pad, x - pad:x + w + pad].astype(np.float32) / 255
        a = a_full[y - pad:y + h + pad, x - pad:x + w + pad].astype(np.float32)
        out.append((np.ascontiguousarray(crop), np.ascontiguousarray(a)))
    return out


class Papillons(Live):
    """P13 : les papillons prennent leur envol ; deux battements d'ailes par temps."""

    def __init__(self, photo, cfg, beats):
        super().__init__(photo, cfg, beats)

        def alpha(img):
            L = img.astype(np.float32) @ np.float32([0.2126, 0.7152, 0.0722])
            bg = cv2.erode(cv2.GaussianBlur(L, (0, 0), 25), np.ones((31, 31)))
            return np.clip((L - bg - 22) / 60, 0, 1)
        self.sharp = _key_sprites(photo.src, cfg["nets"], alpha)
        self.soft = _key_sprites(photo.src, cfg["flous"], alpha)
        self.stream = cfg["courant"]
        self.events = cfg.get("envols", [])
        self.glint = _dot(3.0)

    def _butterfly(self, img, t, u, v, age, life, k, spr, ph, tilt):
        x, y = self.xy(u, v)
        rgb, a = spr
        size = self.s * k
        fade = _smooth(age / 0.5) * _smooth((life - age) / 0.8)
        g = self.guard(x, y, 0.4 * a.shape[1] * size)
        beat_pos, _ = self.beat_info(t)
        flap = 0.5 + 0.5 * math.cos(2 * math.pi * 2 * beat_pos + ph)      # deux battements par temps
        put(img, rgb, a, x, y, size * (0.22 + 0.78 * flap), size, tilt, 0.95 * fade * g)

    def draw(self, img, t, tr):
        self.prepare(tr)
        for i in range(13):
            P = 4.0 + 2.5 * _hash(i, 1)
            age = (t + P * _hash(i, 2)) % P
            n = math.floor((t + P * _hash(i, 2)) / P)
            r = _hash(i, n, 3)
            (u0, v0), _ = _curve(self.stream, r)
            depth = 0.55 + 0.6 * _hash(i, n, 4)
            spr = (self.soft if depth < 0.75 else self.sharp)[int(_hash(i, n, 5) * 97) % (len(self.soft) if depth < 0.75 else len(self.sharp))]
            ph = 6.28 * _hash(i, 6)
            u = u0 + (0.02 + 0.04 * _hash(i, n, 7)) * age + 0.015 * math.sin(2 * math.pi * 0.6 * age + ph)
            v = v0 - (0.05 + 0.05 * _hash(i, n, 8)) * age + 0.010 * math.sin(2 * math.pi * 0.9 * age + ph)
            tilt = -0.25 + 0.15 * math.sin(1.3 * age + ph)
            self._butterfly(img, t, u, v, age, P, depth * 0.62, spr, 0.5 * _hash(i, 9), tilt)
        # envol sur le mot chanté (« grandisse », « bénisse ») : un vol part des mains vers le haut
        for e, te in enumerate(self.events):
            age = t - te
            if not 0 <= age <= 3.6:
                continue
            for j in range(8):
                u0 = 0.60 + 0.14 * _hash(e, j, 11)          # depuis la manche, d'où part le courant de papillons
                v0 = 0.48 + 0.24 * _hash(e, j, 12)
                delay = 0.08 * j
                a2 = age - delay
                if a2 <= 0:
                    continue
                u = u0 + (0.05 + 0.06 * _hash(e, j, 13)) * a2
                v = v0 - (0.11 + 0.08 * _hash(e, j, 14)) * a2 - 0.02 * a2 * a2
                k = (0.50 + 0.40 * _smooth(a2 / 1.2)) * (0.8 + 0.4 * _hash(e, j, 15))
                spr = self.sharp[j % len(self.sharp)]
                self._butterfly(img, t, u, v, a2, 3.6 - delay, k, spr, 0.4 * _hash(e, j, 16), -0.35)
        # poussière scintillante qui suit le courant
        for i in range(26):
            P = 2.5 + 2.0 * _hash(i, 21)
            age = (t + P * _hash(i, 22)) % P
            n = math.floor((t + P * _hash(i, 22)) / P)
            (u0, v0), _ = _curve(self.stream, _hash(i, n, 23))
            x, y = self.xy(u0 + 0.03 * age, v0 - 0.06 * age)
            tw = 0.5 + 0.5 * math.sin(9 * t + 6.28 * _hash(i, 24))
            a = 0.55 * tw * _smooth(age / 0.4) * _smooth((P - age) / 0.6) * self.guard(x, y)
            put(img, np.float32([1.0, 0.86, 0.92]), self.glint, x, y, self.s * 0.8, self.s * 0.8, 0, a, add=True)


class Petales(Live):
    """P15 : les pétales tourbillonnent le long du courant ; une vague vole vers la caméra sur « mille » et « cœur »."""

    def __init__(self, photo, cfg, beats):
        super().__init__(photo, cfg, beats)

        def alpha(img):
            f = img.astype(np.float32)
            return np.clip((f[..., 0] - f[..., 1] - 45) / 60, 0, 1)
        self.spr = _key_sprites(photo.src, cfg["petales"], alpha)
        self.stream = cfg["courant"]
        self.events = cfg.get("vers_camera", [])

    def _petal(self, img, t, u, v, k, ang, tumble, alpha, spr):
        x, y = self.xy(u, v)
        rgb, a = spr
        size = self.s * k
        put(img, rgb, a, x, y, size, size * tumble, ang, alpha * self.guard(x, y, 0.4 * a.shape[1] * size))

    def draw(self, img, t, tr):
        self.prepare(tr)
        for i in range(22):
            P = 3.4 + 2.4 * _hash(i, 31)
            age = (t + P * _hash(i, 32)) % P
            n = math.floor((t + P * _hash(i, 32)) / P)
            r = -0.05 + 0.5 * _hash(i, n, 33) + (0.10 + 0.08 * _hash(i, n, 34)) * age
            (u, v), d = _curve(self.stream, r)
            off = 0.05 * math.sin(2 * math.pi * 0.45 * age + 6.28 * _hash(i, n, 35)) + 0.06 * (_hash(i, n, 36) - 0.5)
            u, v = u - d[1] * off, v + d[0] * off
            k = 0.6 + 0.8 * _hash(i, n, 37)
            ang = 6.28 * _hash(i, n, 38) + (2.5 * _hash(i, 39) - 1.25) * age
            tumble = 0.30 + 0.70 * abs(math.cos(1.8 * age + 6.28 * _hash(i, n, 40)))
            fade = _smooth(age / 0.5) * _smooth((P - age) / 0.7)
            self._petal(img, t, u, v, k, ang, tumble, 0.97 * fade, self.spr[(i + n) % len(self.spr)])
        # « mille années d'amour », « je t'offre mon cœur » : des pétales s'envolent vers nous
        for e, te in enumerate(self.events):
            age = t - te
            if not 0 <= age <= 1.9:
                continue
            for j in range(11):
                a2 = age - 0.04 * j
                if a2 <= 0:
                    continue
                th = -1.7 + 3.3 * _hash(e, j, 41)        # vers le haut, la droite et le bas, jamais vers le visage
                sp = 0.06 + 0.08 * _hash(e, j, 42)
                u = 0.64 + math.cos(th) * sp * a2
                v = 0.44 + math.sin(th) * sp * a2 * 0.7
                k = (0.9 + 0.5 * _hash(e, j, 43)) * (1 + 2.6 * _smooth(a2 / 1.7))
                alpha = _smooth(a2 / 0.25) * (1 - _smooth((a2 - 0.9) / 0.9))
                ang = 6.28 * _hash(e, j, 44) + 3.0 * a2
                tumble = 0.35 + 0.65 * abs(math.cos(2.2 * a2 + j))
                self._petal(img, t, u, v, k, ang, tumble, alpha, self.spr[j % len(self.spr)])


class LumiereDoree(Live):
    """P14 : rayons qui pulsent sur les temps, étincelles qui montent, volutes dorées qui ondulent ;
    scintillement d'étoiles sur « scintille », montée de lumière sur « jour de lumière »."""

    def __init__(self, photo, cfg, beats):
        super().__init__(photo, cfg, beats)
        self.dot = _dot(3.2)
        self.bokeh = _dot(9.0)
        self.star = _star(9.0)
        self.twinkles = cfg.get("scintille", [])
        self.swells = cfg.get("lumiere", [])
        self.qy, self.qx = np.mgrid[0:H // 4, 0:W // 4].astype(np.float32) * 4

    def draw(self, img, t, tr):
        self.prepare(tr)
        # 1. rayons venus d'en haut
        sx, sy = self.xy(0.50, -0.06)
        swell = sum(math.exp(-max(0.0, t - te) / 1.4) * _smooth((t - te + 0.3) / 0.3) for te in self.swells)
        inten = 0.10 + 0.11 * self.pulse(t, 0.25) + 0.28 * swell
        ang = np.arctan2(self.qx - sx, self.qy - sy)
        rays = (0.5 + 0.5 * np.sin(31 * ang + 0.7 * t)) ** 3 + 0.7 * (0.5 + 0.5 * np.sin(17 * ang - 0.45 * t + 1.7)) ** 2
        r = np.sqrt((self.qx - sx) ** 2 + (self.qy - sy) ** 2)
        vsrc = (self.qy - self.ty) / (self.ph.h * self.s)
        mask = np.exp(-(ang / 0.55) ** 2) * np.exp(-r / (0.75 * H)) * (1 - np.clip((vsrc - 0.16) / 0.22, 0, 1))
        layer = cv2.resize((rays * mask * inten).astype(np.float32), (W, H), interpolation=cv2.INTER_CUBIC)
        img[:] = 1 - (1 - img) * (1 - np.clip(layer[..., None] * GOLD, 0, 1))
        # 2. volutes dorées sur les côtés
        core = np.zeros((H, W), np.uint8)
        for k, (u0, v0, v1) in enumerate(((0.06, 0.30, 0.98), (0.14, 0.45, 1.02), (0.88, 0.28, 0.95), (0.95, 0.50, 1.02))):
            ss = np.linspace(0, 1, 60)
            uu = u0 + 0.05 * np.sin(2 * np.pi * (1.1 * ss + 0.07 * t + k * 0.3)) + 0.025 * np.sin(2 * np.pi * (2.3 * ss - 0.11 * t + k))
            vv = v0 + (v1 - v0) * ss
            pts = np.stack([uu * self.ph.w * self.s + self.tx, vv * self.ph.h * self.s + self.ty], 1)
            cv2.polylines(core, [np.round(pts * 4).astype(np.int32)], False, 200, 2, cv2.LINE_AA, shift=2)
        c = core.astype(np.float32) / 255
        glow = cv2.resize(cv2.GaussianBlur(cv2.resize(c, (W // 4, H // 4), interpolation=cv2.INTER_AREA), (0, 0), 3), (W, H))
        w = (0.22 * cv2.GaussianBlur(c, (0, 0), 1.0) + 1.6 * glow) * (0.7 + 0.3 * self.pulse(t, 0.3))
        img += w[..., None] * GOLD * 0.55
        # 3. étincelles qui montent dans le halo
        for i in range(48):
            P = 2.2 + 2.6 * _hash(i, 51)
            age = (t + P * _hash(i, 52)) % P
            n = math.floor((t + P * _hash(i, 52)) / P)
            side = _hash(i, n, 53)
            u0 = 0.02 + 0.22 * _hash(i, n, 54) if side < 0.4 else (0.66 + 0.32 * _hash(i, n, 54) if side < 0.8 else 0.25 + 0.5 * _hash(i, n, 54))
            v0 = 0.25 + 0.75 * _hash(i, n, 55) if side < 0.8 else 0.02 + 0.18 * _hash(i, n, 55)
            u = u0 + (0.012 * (1 if u0 > 0.5 else -1)) * age
            v = v0 - (0.03 + 0.05 * _hash(i, 56)) * age
            x, y = self.xy(u, v)
            big = _hash(i, 57) < 0.18
            tw = 0.55 + 0.45 * math.sin(7 * t + 6.28 * _hash(i, 58))
            a = (0.45 if big else 1.0) * tw * _smooth(age / 0.4) * _smooth((P - age) / 0.6) * self.guard(x, y)
            spr = self.bokeh if big else self.dot
            put(img, GOLD if big else GLINT, spr, x, y, self.s * 0.9, self.s * 0.9, 0, a, add=True)
        # 4. « une étoile scintille », « jour de lumière » : cascade d'étoiles
        for e, te in enumerate(self.twinkles + self.swells):
            age = t - te
            if not -0.1 <= age <= 1.6:
                continue
            for j in range(20):
                a2 = age - 0.045 * j
                if not 0 <= a2 <= 0.75:
                    continue
                u = 0.05 + 0.9 * _hash(e, j, 61)
                v = 0.04 + 0.45 * _hash(e, j, 62) if _hash(e, j, 63) < 0.6 else 0.6 + 0.35 * _hash(e, j, 62)
                x, y = self.xy(u, v)
                k = math.sin(math.pi * a2 / 0.75)
                put(img, GLINT, self.star, x, y, self.s * 0.9 * k, self.s * 0.9 * k, 0.4 * a2, 0.95 * k * self.guard(x, y), add=True)


class EclatsOr(Live):
    """P16 : la poussière d'or s'échappe vers la gauche et explose sur les temps ;
    à droite, éclats de cendre et fumée dérivent lentement."""

    def __init__(self, photo, cfg, beats):
        super().__init__(photo, cfg, beats)
        self.dot = _dot(2.6)
        self.flake = np.ones((5, 9), np.float32)
        self.flake[0, :] = self.flake[-1, :] = 0.4
        self.star = _star(7.0)
        self.shards = [_shard(70 + i, 6 + 5 * (i % 4)) for i in range(8)]
        self.explosions = cfg.get("explosions", [])
        rng = np.random.default_rng(5)
        nz = cv2.GaussianBlur(rng.normal(0, 1, (384, 384)).astype(np.float32), (0, 0), 14)
        nz2 = cv2.GaussianBlur(rng.normal(0, 1, (384, 384)).astype(np.float32), (0, 0), 6)
        self.noise = [(n - n.min()) / (n.max() - n.min()) for n in (nz, nz2)]

    def _smoke(self, img, t):
        # fumée claire qui s'étire vers la droite (zone u > 0,78, hors visage)
        x0, _ = self.xy(0.78, 0)
        x0 = int(max(0, x0))
        if x0 >= W:
            return
        _, ytop = self.xy(0, 0)
        _, ybot = self.xy(0, 1)
        y0, y1 = int(max(0, ytop)), int(min(H, ybot))
        if y1 - y0 < 8:
            return
        rw, rh = W - x0, y1 - y0
        layers = 0
        for k, nz in enumerate(self.noise):
            sh = int(t * (22 if k == 0 else 37)) % nz.shape[1]
            tile = np.roll(np.roll(nz, sh, axis=1), int(t * 9) % nz.shape[0], axis=0)
            layers = layers + (0.65 if k == 0 else 0.35) * cv2.resize(tile[:192, :192], (rw, rh), interpolation=cv2.INTER_LINEAR)
        ramp = np.clip((np.arange(rw, dtype=np.float32)) / 140.0, 0, 1)[None, :]
        a = np.clip((layers - 0.45) * 2.0, 0, 1) * ramp * 0.30
        reg = img[y0:y1, x0:W]
        reg[:] = 1 - (1 - reg) * (1 - a[..., None] * np.float32([0.62, 0.62, 0.66]))

    def draw(self, img, t, tr):
        self.prepare(tr)
        self._smoke(img, t)
        # éclats de cendre qui dérivent vers la droite en tournoyant
        for i in range(24):
            P = 3.0 + 2.5 * _hash(i, 71)
            age = (t + P * _hash(i, 72)) % P
            n = math.floor((t + P * _hash(i, 72)) / P)
            u = 0.79 + 0.08 * _hash(i, n, 73) + (0.03 + 0.07 * _hash(i, n, 74)) * age
            v = 0.20 + 0.75 * _hash(i, n, 75) + (0.035 * _hash(i, n, 76) - 0.01) * age
            x, y = self.xy(u, v)
            spr = self.shards[(i + n) % len(self.shards)]
            a = 0.9 * _smooth(age / 0.4) * _smooth((P - age) / 0.6) * self.guard(x, y, 10)
            put(img, np.float32([0.05, 0.05, 0.06]), spr, x, y, self.s * 0.9, self.s * 0.9 * (0.4 + 0.6 * abs(math.cos(2 * age + i))),
                 6.28 * _hash(i, n, 77) + 1.6 * age, a)
        # poussière d'or qui s'échappe des cheveux et de la main vers la gauche
        for i in range(70):
            P = 1.8 + 1.8 * _hash(i, 81)
            age = (t + P * _hash(i, 82)) % P
            n = math.floor((t + P * _hash(i, 82)) / P)
            hand = _hash(i, n, 83) < 0.35
            u0 = (0.10 + 0.24 * _hash(i, n, 84)) if hand else (0.36 + 0.12 * _hash(i, n, 84))
            v0 = 0.08 + 0.80 * _hash(i, n, 85)
            u = u0 - (0.04 + 0.12 * _hash(i, n, 86)) * age
            v = v0 - (0.01 + 0.05 * _hash(i, n, 87)) * age + 0.01 * math.sin(3 * age + i)
            x, y = self.xy(u, v)
            tw = 0.55 + 0.45 * math.sin(11 * t + 6.28 * _hash(i, 88))
            a = 0.9 * tw * _smooth(age / 0.3) * _smooth((P - age) / 0.5) * self.guard(x, y)
            if _hash(i, 89) < 0.3:
                put(img, GOLD, self.flake, x, y, self.s * 0.9, self.s * 0.9, 6.28 * _hash(i, n, 90) + 2 * age, a, add=True)
            else:
                put(img, GLINT, self.dot, x, y, self.s * 0.7, self.s * 0.7, 0, a, add=True)
        # explosions d'or : sur chaque temps du plan, et en grand sur l'entrée du groove et « fais-la vibrer »
        bursts = [(b, 18, 1.0) for b in self.beats if t - 1.3 <= b <= t]
        bursts += [(te, 46, 1.6) for te in self.explosions if t - 1.6 <= te <= t]
        for b, cnt, power in bursts:
            age = t - b
            for j in range(cnt):
                from_hand = _hash(b, j, 95) < 0.4
                th = math.pi * (0.55 + 0.9 * _hash(b, j, 91))          # éventail vers la gauche
                sp = power * (0.10 + 0.22 * _hash(b, j, 92))
                dist = sp * (1 - math.exp(-age * 2.4)) / 2.4               # freinage
                if from_hand:
                    u0, v0 = 0.12 + 0.20 * _hash(b, j, 96), 0.15 + 0.55 * _hash(b, j, 93)
                else:                                                       # bord visible de la chevelure
                    u0, v0 = 0.48 + 0.05 * _hash(b, j, 96), 0.04 + 0.70 * _hash(b, j, 93)
                u = u0 + math.cos(th) * dist
                v = v0 + math.sin(th) * dist * 0.6
                x, y = self.xy(u, v)
                a = (1 - _smooth(age / (0.9 * power))) * self.guard(x, y)
                spr = self.star if _hash(b, j, 94) < 0.4 else self.dot
                put(img, GLINT, spr, x, y, self.s * 1.1, self.s * 1.1, 0.5 * age, a, add=True)


KINDS = {"papillons": Papillons, "petales": Petales, "lumiere_doree": LumiereDoree, "eclats_or": EclatsOr}


def build(photos, cfgs, beats):
    out = {}
    for pid, ph in photos.items():
        live = cfgs[pid].get("live")
        if live:
            out[pid] = KINDS[live["type"]](ph, live, beats)
    return out
