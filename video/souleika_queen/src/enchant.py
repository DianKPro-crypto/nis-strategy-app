"""Version « Nuit enchantée » : un conte de fées de cinéma autour de photos réelles, sans jamais toucher au visage.

Principe. Chaque photo est séparée en deux calques (src/matte.py, détourage local) :
- la personne garde ses pixels d'origine (seul l'étalonnage change, comme dans la version actuelle) ;
- le décor change de lumière selon le « monde » de la séquence (nuit étoilée, crépuscule, heure dorée, bal royal,
  clair de lune, aurore) : profondeur de champ, lampes réelles transformées en bokeh, ciel en dégradé, couleurs
  riches et noirs profonds (aucun voile laiteux).
La magie vit DERRIÈRE elle (étoiles, bokeh, feux d'artifice calés sur les temps, lanternes, rayons de contre-jour,
moitié arrière des spirales d'étincelles), puis DEVANT elle pour la profondeur (moitié avant des spirales,
étincelles des coupes, grands bokeh flous, traînées d'étoiles), toujours effacée à l'approche des visages et des mains.
Un liseré doré (aura) et le reflet du décor sur ses contours l'intègrent à la scène. Parallaxe : le décor glisse
moins vite qu'elle (profondeur « 3D ») ; chaque calque ne subit qu'une échelle et une translation (aucune déformation).
Tout est fonction pure du temps : rendu parallèle par segments sans raccord visible.
"""
import bisect
import math

import cv2
import numpy as np

import fx
from common import BAND_GAP, EASE, FPS, H, W, clamp, rgb
from dream import Comet, _bokeh, _heart
from livefx import _hash, _smooth, _star, put
from photos import _ramp, place

LUMA = np.float32([0.2126, 0.7152, 0.0722])
Q = 4                                  # passes de lumière au quart de la résolution
QW, QH = W // Q, H // Q
_qy, _qx = np.mgrid[0:QH, 0:QW].astype(np.float32)


def C(h):
    return np.float32(rgb(h))


def _disc(r):
    n = int(math.ceil(r)) * 2 + 1
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32) - n // 2
    k = np.clip(r + 0.5 - np.sqrt(xx * xx + yy * yy), 0, 1)
    return k / k.sum()


def add_rgb(img, spr, cx, cy, alpha):
    """Ajout lumineux d'un sprite couleur centré (sans rotation)."""
    if alpha <= 0.004:
        return
    h, w = spr.shape[:2]
    x0, y0 = int(round(cx - w / 2)), int(round(cy - h / 2))
    X0, Y0, X1, Y1 = max(0, x0), max(0, y0), min(img.shape[1], x0 + w), min(img.shape[0], y0 + h)
    if X1 > X0 and Y1 > Y0:
        img[Y0:Y1, X0:X1] += spr[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0] * alpha


def add_alpha(img, spr, cx, cy, col, alpha):
    if alpha <= 0.004:
        return
    h, w = spr.shape
    x0, y0 = int(round(cx - w / 2)), int(round(cy - h / 2))
    X0, Y0, X1, Y1 = max(0, x0), max(0, y0), min(img.shape[1], x0 + w), min(img.shape[0], y0 + h)
    if X1 > X0 and Y1 > Y0:
        img[Y0:Y1, X0:X1] += spr[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0, None] * (col * alpha)


def guard_vec(boxes, x, y, ramp=110.0):
    """Atténuation (0-1) près des zones protégées, pour des tableaux de points."""
    f = np.ones_like(x)
    for x0, y0, x1, y1, st in boxes:
        dx = np.maximum(np.maximum(x0 - x, 0), x - x1)
        dy = np.maximum(np.maximum(y0 - y, 0), y - y1)
        s = np.clip(np.hypot(dx, dy) / ramp, 0, 1)
        f = np.minimum(f, 1 - st * (1 - s * s * (3 - 2 * s)))
    return f


def guard_pt(boxes, x, y, r=0.0, ramp=110.0):
    f = 1.0
    for x0, y0, x1, y1, st in boxes:
        d = math.hypot(max(x0 - x, 0, x - x1), max(y0 - y, 0, y - y1)) - r
        f = min(f, 1 - st * (1 - _smooth(d / ramp)))
    return f


class Splat:
    """Points lumineux (étoiles, étincelles) accumulés puis rendus en une passe : cœur net + halos."""

    def __init__(self, core=1.0, glows=()):
        self.core, self.glows = core, glows
        self.x, self.y, self.c = [], [], []

    def add(self, x, y, c):
        if len(x):
            self.x.append(np.asarray(x, np.float32))
            self.y.append(np.asarray(y, np.float32))
            self.c.append(np.asarray(c, np.float32))

    def render(self):
        core, glows = self.core, self.glows
        if not self.x:
            return None
        x, y, c = np.concatenate(self.x), np.concatenate(self.y), np.concatenate(self.c)
        ok = (x >= 0) & (x < W - 1) & (y >= 0) & (y < H - 1) & (c.max(axis=1) > 2e-3)
        if not ok.any():
            return None
        x, y, c = x[ok], y[ok], c[ok]
        x0, y0 = x.astype(np.int64), y.astype(np.int64)
        fx_, fy = x - x0, y - y0
        base = y0 * W + x0
        idx = np.concatenate([base, base + 1, base + W, base + W + 1])
        wts = np.concatenate([(1 - fx_) * (1 - fy), fx_ * (1 - fy), (1 - fx_) * fy, fx_ * fy])
        buf = np.empty((H, W, 3), np.float32)
        for k in range(3):
            buf[..., k] = np.bincount(idx, wts * np.tile(c[:, k], 4), minlength=H * W).reshape(H, W)
        out = cv2.GaussianBlur(buf, (0, 0), core) * np.float32(2 * math.pi * core * core)
        if glows:
            small = cv2.resize(buf, (QW, QH), interpolation=cv2.INTER_AREA) * np.float32(Q * Q)
            acc = None
            for sg, gain in glows:
                g = cv2.GaussianBlur(small, (0, 0), sg) * np.float32(2 * math.pi * sg * sg * gain / (Q * Q))
                acc = g if acc is None else acc + g
            out += cv2.resize(acc, (W, H), interpolation=cv2.INTER_LINEAR)
        return out


# ============================================================================ sprites

def _glow(r):
    """Halo gaussien (lumière locale : éclatements, ciel qui s'illumine)."""
    n = int(r * 2.4) // 2 * 2 + 1
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32) - n // 2
    return np.exp(-(xx * xx + yy * yy) / (2 * (r / 2.2) ** 2)).astype(np.float32)


def _lantern_rgb(hh, blur=0.0):
    """Lanterne céleste en papier : corps trapézoïdal plus lumineux vers la flamme, halo chaud."""
    S = int(hh * 5.2) // 2 * 2 + 1
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32) - S // 2
    u = np.clip((yy + hh) / (2 * hh), 0, 1)
    half = hh * (0.64 - 0.20 * u)
    body = np.clip((half - np.abs(xx)) / 1.1 + 0.5, 0, 1) * np.clip((hh - np.abs(yy)) / 1.1 + 0.5, 0, 1)
    top = np.clip(1 - ((yy + hh) < 0.18 * hh) * (np.abs(xx) / np.maximum(half, 1)) ** 6, 0, 1)
    body *= top
    colb = C("#FF6A24")[None, None] * (1 - u[..., None]) + C("#FFD27A")[None, None] * u[..., None]
    out = body[..., None] * (0.45 + 0.55 * u[..., None] ** 1.3) * colb
    flame = np.exp(-(xx ** 2 + (yy - 0.80 * hh) ** 2) / (2 * (0.24 * hh) ** 2))
    out += flame[..., None] * C("#FFF1C2") * 0.9
    halo = np.exp(-(xx ** 2 + (yy - 0.25 * hh) ** 2) / (2 * (1.35 * hh) ** 2))
    out += halo[..., None] * C("#FF8A30") * 0.20
    if blur > 0.5:
        out = cv2.GaussianBlur(out, (0, 0), blur)
    return out.astype(np.float32)


# ============================================================================ éléments animés

class Shell:
    """Bombe de feu d'artifice : montée (traînée) puis éclatement calé sur un temps de la musique.
    Types : pivoine (sphère), anneau, coeur, saule (pluie d'or lente). Le ciel s'illumine à l'éclatement."""

    def __init__(self, cfg, t_burst, seed):
        rng = np.random.default_rng(seed)
        self.t = t_burst
        self.x, self.y = cfg["x"] * W, cfg["y"] * H
        self.kind = cfg.get("type", "pivoine")
        n = int(cfg.get("n", 160))
        saule = self.kind == "saule"
        self.v = 640.0 * cfg.get("taille", 1.0) * (0.8 if saule else 1.0)
        if self.kind == "coeur":
            th = np.linspace(0, 2 * np.pi, n, endpoint=False) + rng.uniform(-0.02, 0.02, n)
            d = np.stack([np.sin(th) ** 3, -(13 * np.cos(th) - 5 * np.cos(2 * th) - 2 * np.cos(3 * th) - np.cos(4 * th)) / 16], 1)
            d = d * 0.95 + rng.normal(0, 0.025, (n, 2))
        elif self.kind == "anneau":
            th = rng.uniform(0, 2 * np.pi, n)
            a = rng.uniform(0, np.pi)
            e = np.stack([np.cos(th), 0.38 * np.sin(th)], 1)
            d = e @ np.float32([[math.cos(a), math.sin(a)], [-math.sin(a), math.cos(a)]])
            d *= rng.uniform(0.95, 1.05, (n, 1))
        else:
            z = rng.uniform(-1, 1, n)
            ph = rng.uniform(0, 2 * np.pi, n)
            r = np.sqrt(1 - z * z)
            d = np.stack([r * np.cos(ph), r * np.sin(ph)], 1) * rng.uniform(0.85, 1.06, (n, 1))
        self.d = d.astype(np.float32)
        self.life = (rng.uniform(1.6, 2.3, n) * (1.5 if saule else 1.0)).astype(np.float32)
        self.k = 2.1 if saule else 1.6
        self.g = 170.0 if saule else 95.0
        pal = [C(h) for h in cfg.get("couleurs", ["#FFD27A"])]
        self.col = np.stack([pal[i % len(pal)] for i in rng.integers(0, 64, n)])
        self.crackle = rng.random(n) < (0.5 if saule else 0.3)
        self.cph = rng.uniform(0, 6.28, n).astype(np.float32)
        self.x0 = self.x + rng.uniform(-80, 80)
        self.rise = 0.85
        self.tl = 0.24 if saule else 0.11                 # durée de la traînée de chaque étincelle
        self.glow = C(cfg.get("couleurs", ["#FFD27A"])[0])

    def points(self, sp, t):
        hot = C("#FFF6E2")
        if self.t - self.rise <= t < self.t + 0.05:                  # montée
            j = np.arange(22, dtype=np.float32)
            tj = t - j * 0.008
            u = np.clip((tj - (self.t - self.rise)) / self.rise, 0, 1)
            e = 1 - (1 - u) ** 3
            x = self.x0 + (self.x - self.x0) * e + 3 * np.sin(40 * tj)
            y = H * 1.04 + (self.y - H * 1.04) * e
            inten = np.where(u > 0, 1.8 * (1 - j / 22) ** 1.6, 0)
            sp.add(x, y, C("#FFE2A8")[None] * inten[:, None])
        tau = t - self.t
        if tau < 0 or tau > float(self.life.max()) + 0.5:
            return
        m = 22 if self.kind == "saule" else 14
        j = np.arange(m, dtype=np.float32)[None, :]
        tj = tau - j * (self.tl / m)                                  # (1, m)
        ok = tj > 0
        tjc = np.maximum(tj, 0)
        f = (1 - np.exp(-self.k * tjc)) / self.k
        px = self.x + self.d[:, :1] * self.v * f
        py = self.y + self.d[:, 1:] * self.v * f + 0.5 * self.g * tjc * tjc
        u = tjc / self.life[:, None]
        fade = np.clip(1 - u, 0, 1) ** 1.4
        mix = np.clip(tjc / 0.30, 0, 1)[..., None]
        col = hot[None, None] * (1 - mix) + self.col[:, None, :] * mix
        fl = np.where(self.crackle[:, None] & (u > 0.55), (0.45 + 0.55 * np.sin(36 * tjc + self.cph[:, None])) ** 2, 1.0)
        inten = 2.6 * fade * fl * ok * (1 - j / m) ** 1.6
        sp.add(px.ravel(), py.ravel(), (col * inten[..., None]).reshape(-1, 3))

    def sky(self, img, t, halo):
        """Le ciel s'illumine autour de l'éclatement (lumière locale et chaude, jamais un flash plein cadre)."""
        tau = t - self.t
        if 0 <= tau < 1.6:
            a = (0.08 if self.kind == "saule" else 0.16) * math.exp(-tau / 0.4)
            add_alpha(img, halo, self.x, self.y, self.glow, a)


class Vortex:
    """Spirale de conte de fées : trois rubans de poussière d'étoiles montent en hélice autour d'elle (derrière
    puis devant elle), forment une couronne au-dessus de sa tête et éclatent en étoiles sur le temps fort."""

    def __init__(self, cfg, seed):
        self.c = cfg
        self.K = int(cfg.get("n", 270)) // 3 * 2               # particules par ruban
        rng = np.random.default_rng(seed)
        n = 3 * self.K
        self.rib = np.repeat(np.arange(3), self.K)
        self.k = np.tile(np.arange(self.K), 3).astype(np.float32)
        self.jx = rng.normal(0, 9, n).astype(np.float32)
        self.jy = rng.normal(0, 9, n).astype(np.float32)
        self.tw = rng.uniform(5, 14, n).astype(np.float32)
        self.twp = rng.uniform(0, 6.28, n).astype(np.float32)
        cols = np.stack([C("#FFF3D6"), C("#FFD27A"), C("#FFB3CC"), C("#FFE6A0")])
        self.col = cols[rng.integers(0, 4, n)]
        self.out = rng.uniform(0.5, 1.5, n).astype(np.float32)
        self.dir = rng.uniform(-0.5, 0.5, n).astype(np.float32)

    def _pos(self, t):
        """Hélice autour du buste (du bas jusqu'au cou), puis montée derrière la tête vers le point d'éclatement."""
        c = self.c
        dur = c["t1"] - c["t0"]
        head = clamp((t - c["t0"]) / (0.9 * dur))
        head = head * head * (3 - 2 * head)
        h = head - self.k * (0.55 / self.K)                  # la queue du ruban suit la tête le long du trajet
        live = (h >= 0).astype(np.float32)
        h = np.clip(h, 0, 1)
        hc = 0.78                                           # part du trajet en hélice autour du buste
        u = np.clip(h / hc, 0, 1)
        th = self.rib * (2 * np.pi / 3) + 2 * np.pi * c.get("tours", 1.6) * u + 0.8 * (t - c["t0"])
        r = c["rayon"] * W * (1 - 0.30 * u)
        x = c["axe"] * W + r * np.sin(th) + self.jx * 0.6
        y = c["bas"] * H + (c["cou"] - c["bas"]) * H * u + self.jy * 0.6
        v = np.clip((h - hc) / (1 - hc), 0, 1)              # puis gerbe qui monte derrière elle vers le haut
        e = v * v * (3 - 2 * v)
        bow = np.sin(np.pi * e) * (self.rib - 1) * 90        # trois arcs (gauche, centre, droite) qui se rejoignent
        x = x + (c["axe"] * W - x) * e + bow + self.jx * 3.5 * np.sin(np.pi * e)
        y = y + (c["haut"] * H - y) * e + self.jy * 3.5 * np.sin(np.pi * e)
        th = np.where(v > 0, np.pi, th)                     # derrière elle pendant la montée
        return x, y, th, live

    def points(self, sp, t, front, boxes=None):
        c = self.c
        t0, t1 = c["t0"], c["t1"]
        if not (t0 <= t <= t1 + 1.5):
            return
        x, y, th, live = self._pos(min(t, t1))
        z = np.cos(th)
        tail = (1 - self.k / self.K) ** 1.15
        inten = 3.2 * live * tail * (0.45 + 0.55 * (z + 1) / 2) * (0.55 + 0.45 * np.sin(self.tw * t + self.twp))
        inten = inten * np.where(self.k < 3, 2.0, 1.0)            # têtes plus brillantes
        inten = inten * np.where(th == np.pi, 0.55, 1.0)          # gerbe montante : plus légère que les rubans
        if t > t1:                                                  # éclatement en étoiles sur le temps fort
            tau = t - t1
            d = 620 * (1 - math.exp(-2.4 * tau)) / 2.4
            x = x + (np.sin(th) + self.dir) * self.out * d
            y = y + (-0.55 + 0.4 * np.cos(th)) * self.out * d + 85 * tau * tau
            inten = inten * max(0.0, 1 - tau / 1.5) ** 1.3 * (1.3 if tau < 0.3 else 1.0)
        sel = (z >= 0) if front else (z < 0)
        inten = inten * sel
        if front and boxes:                                         # devant elle : jamais sur le visage ni les mains
            inten = inten * guard_vec(boxes, x, y, ramp=70.0)
        sp.add(x, y, self.col * inten[:, None])
        if t <= t1:                                                 # paillettes semées par les rubans
            for lag in (0.08, 0.16, 0.26):
                xs, ys, ths, lv = self._pos(t - lag)
                zs = np.cos(ths)
                ss = ((zs >= 0) if front else (zs < 0)) & (self.k % 3 == 0)
                a = 1.6 * lv * (1 - lag / 0.3) * (0.5 + 0.5 * np.sin(self.tw * t * 1.7 + self.twp)) ** 2 * ss
                ys = ys + 140 * lag * lag + 30 * lag
                if front and boxes:
                    a = a * guard_vec(boxes, xs, ys, ramp=70.0)
                sp.add(xs, ys, self.col * a[:, None])

    def stars(self, img, t, front, star, boxes=None):
        c = self.c
        if not (c["t0"] <= t <= c["t1"]):
            return
        x, y, th, live = self._pos(t)
        for i in np.nonzero((self.k == 0) & (live > 0))[0]:
            z = math.cos(th[i])
            if (z >= 0) != front:
                continue
            g = guard_pt(boxes, x[i], y[i], 20, 70) if (front and boxes) else 1.0
            put(img, C("#FFF6E0"), star, float(x[i]), float(y[i]), 2.2, 2.2, 3.0 * t + i, 0.9 * g * (0.6 + 0.4 * (z + 1) / 2), add=True)

    def flash(self, img, t, halo, boxes):
        c = self.c
        tau = t - c["t1"]
        if 0 <= tau < 1.0:
            x, y = c["axe"] * W, c["haut"] * H
            add_alpha(img, halo, x, y, C("#FFE6B0"), 0.32 * math.exp(-tau / 0.20) * guard_pt(boxes, x, y, 60))


class Lanternes:
    """Lanternes célestes qui s'élèvent lentement (pont spirituel) : lointaines derrière elle, quelques-unes
    proches et floues devant (profondeur)."""

    def __init__(self, cfg):
        self.t0, self.t1, n = cfg["debut"], cfg["fin"], cfg["nombre"]
        rng = np.random.default_rng(77)
        self.d = rng.random(n) ** 1.5
        self.x0 = rng.uniform(0.03, 0.97, n)
        self.birth = rng.uniform(-14.0, (self.t1 - self.t0) - 3.0, n)
        self.v = 30 + 75 * self.d
        self.sw = rng.uniform(5, 20, n)
        self.sf = rng.uniform(0.12, 0.35, n)
        self.sp = rng.uniform(0, 6.28, n)
        self.fl = rng.uniform(0, 6.28, n)
        self.bins = [7, 9, 12, 15, 19, 24, 30, 38, 48, 60]
        self.spr = {b: _lantern_rgb(b) for b in self.bins}
        self.blur = {b: _lantern_rgb(b, blur=0.22 * b) for b in self.bins[-4:]}

    def draw(self, img, t, front, boxes=None):
        win = _smooth((t - self.t0) / 2.0) * _smooth((self.t1 - t) / 2.5)
        if win <= 0.01:
            return
        for i in range(len(self.d)):
            age = t - self.t0 - self.birth[i]
            if age < 0:
                continue
            y = H + 90 - age * self.v[i]
            if y < -120:
                continue
            near = self.d[i] > 0.88
            if near != front:
                continue
            x = self.x0[i] * W + self.sw[i] * math.sin(2 * math.pi * self.sf[i] * t + self.sp[i])
            hh = 9 + 51 * self.d[i] ** 1.3
            b = min(self.bins, key=lambda v: abs(v - hh))
            fl = 0.86 + 0.14 * math.sin(8.3 * t + self.fl[i]) * math.sin(3.1 * t + 2 * self.fl[i])
            a = win * fl * (0.75 + 0.35 * self.d[i])
            if near:
                a *= 0.8 * guard_pt(boxes or [], x, y, hh)
            add_rgb(img, (self.blur if near else self.spr)[b], x, y, a)


# ============================================================================ moteur

class Enchant:
    def __init__(self, R):
        self.R = R
        st = self.st = R.style
        self.worlds = st["mondes"]
        self.sec_world = {k: v["monde"] for k, v in st["sections"].items()}
        self.photo_world = st.get("mondes_photos", {})
        self.beats = R.beats
        self.down = set(range(1, len(self.beats), 4))
        self._plates = {}
        self.vignette = fx.make_vignette(st["finition"]["vignette"])
        self.grain = fx.make_grain(sigma=0.010 * st["finition"]["grain"])
        x = np.linspace(0, 2, 2048, dtype=np.float32)          # courbe « pellicule » : épaule douce, contraste
        kn, sc = st["finition"]["epaule"]
        y = np.where(x < kn, x, kn + (x - kn) / (1 + (x - kn) / sc))
        y = np.clip(y, 0, 1)
        y = y + st["finition"]["contraste"] * (y * y * (3 - 2 * y) - y)
        self.tone = y.astype(np.float32)
        self.shells = []
        for k, f in enumerate(st.get("feux", [])):
            tb = self.snap(f["t"])
            self.shells.append(Shell(f, tb, seed=500 + k))
        self.vortex = [Vortex(v, seed=900 + k) for k, v in enumerate(st.get("spirales", []))]
        self.lanternes = Lanternes(st["lanternes"]) if st.get("lanternes") else None
        self.filantes = st.get("filantes", [])
        self.coeurs = st.get("coeurs", [])
        self.comets = [Comet(c, (W, H)) if c["espace"] == "cadre" else c for c in st.get("cometes", [])]
        self._cbuilt = {}
        self.star = _star(6.0)
        self.halo_sky = _glow(340)
        self.halo_top = _glow(150)
        self.bk = {r: _bokeh(r) for r in (16, 24, 34, 48, 66, 90, 120, 150)}
        self.hearts = {r: _heart(r) for r in (24, 34, 48, 66)}
        self.cuts = [s["start"] for s in R.shots if s.get("punch") and s["trans"]["type"] == "cut"]

    # ---------------------------------------------------------------- temps
    def snap(self, t, tol=0.12):
        """Recale un instant sur le temps mesuré le plus proche (feux d'artifice synchronisés)."""
        i = bisect.bisect_left(self.beats, t)
        best = min((b for b in self.beats[max(0, i - 1):i + 1]), key=lambda b: abs(b - t), default=t)
        return best if abs(best - t) <= tol else t

    def accent(self, t):
        i = bisect.bisect_right(self.beats, t) - 1
        if i < 0:
            return 0.0
        return math.exp(-(t - self.beats[i]) / 0.26) * (1.0 if i in self.down else 0.5)

    # ---------------------------------------------------------------- mondes (décors ré-éclairés)
    def world_of(self, s, photo=None):
        name = self.photo_world.get(photo or s.get("photo"), self.sec_world[s["section"]])
        return name, self.worlds[name]

    def plate(self, ph, name):
        key = (ph.id, name)
        if key not in self._plates:
            self._plates[key] = self._build(ph, self.worlds[name], seed=sum(map(ord, ph.id + name)))
        return self._plates[key]

    def _build(self, ph, m, seed):
        P = ph.plate.astype(np.float32) * (1 / 255)
        h, w = P.shape[:2]
        q = min(1.0, 1280 / max(h, w))
        if q < 1:
            P = cv2.resize(P, (round(w * q), round(h * q)), interpolation=cv2.INTER_AREA)
        A = cv2.resize(ph.alpha, (P.shape[1], P.shape[0]), interpolation=cv2.INTER_AREA)
        L = P @ LUMA
        Lb = cv2.GaussianBlur(L, (0, 0), 0.03 * max(P.shape[:2]))
        lamp = np.clip((L - m.get("seuil_lampes", 0.72)) / 0.25, 0, 1) * np.clip((L - Lb - 0.05) / 0.18, 0, 1)
        lamp = lamp * (1 - np.clip(A * 3, 0, 1))
        r = m["flou"] * max(P.shape[:2])
        if r >= 1.0:
            k = _disc(r)
            B = cv2.filter2D(P * (1 + 2.5 * lamp[..., None]), -1, k, borderType=cv2.BORDER_REFLECT)
            lam = cv2.filter2D(lamp, -1, k, borderType=cv2.BORDER_REFLECT) * 2.2
        else:
            B, lam = P, lamp
        Lb = np.clip(B @ LUMA, 0, 1)
        base = B * np.float32(2.0 ** m["expo"]) * np.float32(m.get("teinte", (1, 1, 1)))
        if m.get("compression", 0) > 0:          # nuit américaine : les grandes surfaces claires s'assombrissent
            hl = np.clip((Lb - 0.5) / 0.45, 0, 1)
            base *= (1 - m["compression"] * hl * hl * (3 - 2 * hl))[..., None]
        if m.get("melange", 0) > 0:
            duo = C(m["ombre"]) + (C(m["lumiere"]) - C(m["ombre"])) * (Lb ** m.get("gamma", 1.0))[..., None]
            base = base * (1 - m["melange"]) + duo * m["melange"]
        if m.get("lampes", 0) > 0:
            base += np.clip(lam, 0, 1.5)[..., None] * C(m["couleur_lampes"]) * m["lampes"]
        if m.get("ciel", 0) > 0:
            v = np.linspace(0, 1, base.shape[0], dtype=np.float32)[:, None, None]
            base = base * (1 - m["ciel"]) + (C(m["ciel_haut"]) * (1 - v) + C(m["ciel_bas"]) * v) * m["ciel"]
        if m.get("contraste", 0):
            o = np.clip(base, 0, 1)
            base = base + m["contraste"] * (o * o * (3 - 2 * o) - o)
        lum = base @ LUMA
        base = np.clip(lum[..., None] + m.get("sat", 1.0) * (base - lum[..., None]), 0, None).astype(np.float32)
        return base, q, self._stars(base, A, int(m.get("etoiles", 0)), seed), self._lucioles(P, A, int(m.get("lucioles", 0)), seed)

    @staticmethod
    def _lucioles(P, A, n, seed):
        """Guirlandes de lumière posées sur le feuillage réel de la photo (zones vertes)."""
        if n <= 0:
            return None
        rng = np.random.default_rng(seed + 7)
        r, g, b = P[..., 0], P[..., 1], P[..., 2]
        mx, mn = P.max(2), P.min(2)
        green = (g > r * 1.05) & (g > b * 1.08) & ((mx - mn) / np.maximum(mx, 1e-3) > 0.22) & (A < 0.05)
        ys, xs = np.nonzero(green)
        if len(xs) < 50:
            return None
        k = rng.choice(len(xs), size=min(n, len(xs)), replace=False)
        h, w = P.shape[:2]
        return dict(u=((xs[k] + rng.random(len(k))) / w).astype(np.float32), v=((ys[k] + rng.random(len(k))) / h).astype(np.float32),
                    f=rng.uniform(0.25, 0.9, len(k)).astype(np.float32), ph=rng.uniform(0, 6.28, len(k)).astype(np.float32),
                    mag=(0.5 + 0.9 * rng.random(len(k)) ** 2).astype(np.float32),
                    col=np.where(rng.random((len(k), 1)) < 0.75, C("#FFD27A"), C("#FFF1D0")).astype(np.float32))

    @staticmethod
    def _stars(img, A, n, seed):
        if n <= 0:
            return None
        rng = np.random.default_rng(seed)
        h, w = img.shape[:2]
        dark = 1 - np.clip((img @ LUMA - 0.03) / 0.28, 0, 1)
        sub = cv2.dilate((A > 0.04).astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25)))
        v = np.linspace(0, 1, h, dtype=np.float32)[:, None]
        wgt = dark * (1 - sub) * np.clip(1.12 - v, 0, 1) ** 1.6
        g = 4
        gw, gh = w // g, h // g
        ws = cv2.resize(wgt, (gw, gh), interpolation=cv2.INTER_AREA).ravel().astype(np.float64)
        if ws.sum() < 1e-3:
            return None
        i = rng.choice(ws.size, size=n, p=ws / ws.sum())
        u = ((i % gw) + rng.random(n)) / gw
        vv = ((i // gw) + rng.random(n)) / gh
        kind = rng.random(n)
        col = np.where(kind[:, None] < 0.22, C("#FFE0A8"), np.where(kind[:, None] < 0.7, C("#FFFFFF"), C("#CFE0FF")))
        return dict(u=u.astype(np.float32), v=vv.astype(np.float32), mag=(0.35 + 1.25 * rng.random(n) ** 3).astype(np.float32),
                    col=col.astype(np.float32), f=rng.uniform(0.3, 1.4, n).astype(np.float32),
                    ph=rng.uniform(0, 6.28, n).astype(np.float32), big=np.nonzero(rng.random(n) < 0.06)[0])

    def background(self, ph, name, sb, tbx, tby, cw, ch):
        plate, q = self.plate(ph, name)[:2]
        r = sb / q
        M = np.float32([[r, 0, tbx + 0.5 * r - 0.5], [0, r, tby + 0.5 * r - 0.5]])
        bg = cv2.warpAffine(plate, M, (cw, ch), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        dw, dh = ph.w * sb, ph.h * sb
        if not (tbx <= 0 and tby <= 0 and tbx + dw >= cw and tby + dh >= ch):
            # au-delà de la photo : prolongement flou de son propre décor, qui s'assombrit vers le ciel du monde
            k = 8
            sw, sh = max(cw // k, 8), max(ch // k, 8)
            Mk = np.float32([[r / k, 0, tbx / k], [0, r / k, tby / k]])
            ext = cv2.warpAffine(plate, Mk, (sw, sh), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
            ext = cv2.GaussianBlur(ext, (0, 0), 9)
            yy, xx = np.mgrid[0:sh, 0:sw].astype(np.float32) * k
            d = np.hypot(np.maximum(np.maximum(tbx - xx, xx - (tbx + dw)), 0), np.maximum(np.maximum(tby - yy, yy - (tby + dh)), 0))
            fade = np.clip(d / 600.0, 0, 1)[..., None]
            m = self.worlds[name]
            v = (yy / ch)[..., None]
            sky = (C(m.get("ciel_haut", "#0B1030")) * (1 - v) + C(m.get("ciel_bas", "#101827")) * v) * 0.35
            ext = ext * (0.85 - 0.45 * fade) + sky * fade
            ext = cv2.resize(ext, (cw, ch), interpolation=cv2.INTER_CUBIC)
            feather = clamp(0.10 * min(dw, dh), 40, 150)
            a = (_ramp(ch, tby, tby + dh, feather)[:, None] * _ramp(cw, tbx, tbx + dw, feather)[None, :])[..., None]
            bg = ext + (bg - ext) * a
        return bg

    def parallax(self, s, ph, sf, tx, ty, m):
        depth = m.get("profondeur", 1.0) * self.st["parallaxe"]["force"]
        if depth <= 0:
            return sf, tx, ty
        z0, c0, a0 = self.R.camera(s, s["vs"])
        s0, tx0, ty0, _, _ = place(ph.w, ph.h, W, H, z0, c0, a0)
        px, py = ph.focus[0] * ph.w, ph.focus[1] * ph.h
        fx_, fy = sf * px + tx, sf * py + ty
        f0x, f0y = s0 * px + tx0, s0 * py + ty0
        sb = s0 * (sf / s0) ** (1 - self.st["parallaxe"]["zoom"] * depth)       # le décor zoome moins qu'elle
        lag = self.st["parallaxe"]["glisse"] * depth                              # et glisse moins qu'elle
        bx, by = fx_ - lag * (fx_ - f0x), fy - lag * (fy - f0y)
        return sb, bx - sb * px, by - sb * py

    # ---------------------------------------------------------------- lumière autour d'elle
    @staticmethod
    def aura(bg, A, col, force):
        if force <= 0:
            return
        h, w = A.shape
        Ah = cv2.resize(A, (w // 2, h // 2), interpolation=cv2.INTER_AREA)
        ring = np.clip(cv2.GaussianBlur(Ah, (0, 0), 4) - Ah, 0, 1) * 1.5
        ring2 = np.clip(cv2.GaussianBlur(Ah, (0, 0), 16) - Ah, 0, 1) * 0.45
        ring = cv2.resize(ring + ring2, (w, h), interpolation=cv2.INTER_LINEAR)
        bg += ring[..., None] * (col * force)

    @staticmethod
    def wrap(img, A, bg, force):
        if force <= 0:
            return
        h, w = A.shape
        qs = (w // 4, h // 4)
        Aq = cv2.resize(A, qs, interpolation=cv2.INTER_AREA)
        edge = Aq * np.clip(cv2.GaussianBlur(1 - Aq, (0, 0), 2.2) * 2.0, 0, 1)
        bq = cv2.GaussianBlur(cv2.resize(bg, qs, interpolation=cv2.INTER_AREA), (0, 0), 3)
        img += cv2.resize(bq * edge[..., None], (w, h), interpolation=cv2.INTER_LINEAR) * force

    @staticmethod
    def rays(A, bg, r, t):
        """Rayons de contre-jour : la source est derrière elle, sa silhouette découpe la lumière."""
        sx, sy = r["source"][0] * QW, r["source"][1] * QH
        Aq = cv2.resize(A, (QW, QH), interpolation=cv2.INTER_AREA)
        blob = np.exp(-((_qx - sx) ** 2 + (_qy - sy) ** 2) / (2 * (0.10 * QH) ** 2))
        bq = cv2.resize(bg, (QW, QH), interpolation=cv2.INTER_AREA)
        bright = np.clip((bq @ LUMA - 0.30) / 0.5, 0, 1)
        src = ((blob * 1.5 + bright * 0.45) * (1 - Aq))[..., None] * C(r["couleur"])
        acc = np.zeros_like(src)
        tot = 0.0
        for i in range(22):
            k = 1 - 0.03 * i
            wgt = 0.93 ** i
            M = np.float32([[k, 0, sx * (1 - k)], [0, k, sy * (1 - k)]])
            acc += cv2.warpAffine(src, M, (QW, QH), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP) * wgt
            tot += wgt
        acc *= r["intensite"] / tot * (0.85 + 0.15 * math.sin(0.45 * t))
        return cv2.resize(acc, (W, H), interpolation=cv2.INTER_LINEAR)

    # ---------------------------------------------------------------- magie derrière elle
    def _behind(self, img, s, ph, name, m, sb, tbx, tby, t, acc):
        sp = Splat(1.0, ((2.5, 0.16), (10.0, 0.05)))
        spf = Splat(1.4, ((2.5, 0.22), (10.0, 0.06)))
        spv = Splat(2.2, ((3.0, 0.30), (10.0, 0.08)))
        st, lu = self.plate(ph, name)[2:]
        if lu is not None:
            x = lu["u"] * ph.w * sb + tbx
            y = lu["v"] * ph.h * sb + tby
            tw = 0.5 + 0.5 * np.sin(2 * np.pi * lu["f"] * t + lu["ph"])
            sp.add(x, y, lu["col"] * (lu["mag"] * (0.3 + 0.7 * tw ** 3) * 2.4)[:, None])
        for sh in self.shells:
            sh.sky(img, t, self.halo_sky)
        if st is not None:
            x = st["u"] * ph.w * sb + tbx
            y = st["v"] * ph.h * sb + tby
            tw = 0.5 + 0.5 * np.sin(2 * np.pi * st["f"] * t + st["ph"])
            inten = st["mag"] * (0.35 + 0.65 * tw * tw) * m.get("eclat_etoiles", 1.0)
            sp.add(x, y, st["col"] * inten[:, None])
            for i in st["big"]:
                put(img, np.float32(st["col"][i]), self.star, float(x[i]), float(y[i]), 0.8, 0.8,
                    0.2 * t + i, float(0.55 * tw[i] * st["mag"][i]), add=True)
        self._bokeh(img, s, m, t, acc)
        for sh in self.shells:
            sh.points(spf, t)
        for v in self.vortex:
            v.points(spv, t, front=False)
            v.stars(img, t, front=False, star=self.star)
        self._filantes(spf, t)
        for k in (sp, spf, spv):
            L = k.render()
            if L is not None:
                img += L
        if self.lanternes:
            self.lanternes.draw(img, t, front=False)
        self._coeurs(img, t, m)

    def _bokeh(self, img, s, m, t, acc):
        n = int(m.get("bokeh", 0))
        if n <= 0:
            return
        sid = sum(map(ord, s["id"]))
        pal = [C(h) for h in m["palette"]]
        for i in range(n):
            hs = lambda k: _hash(i, sid, k)
            r = 16 + 74 * hs(1) ** 1.6
            key = min((16, 24, 34, 48, 66, 90), key=lambda k: abs(k - r))
            x = W * (0.02 + 0.96 * hs(2)) + 22 * math.sin(0.23 * t + 6.28 * hs(3))
            span = H + 2 * key * 1.4
            y = H + key * 1.4 - ((t * (6 + 14 * hs(4)) + hs(5) * span) % span)
            br = (0.85 + 0.15 * math.sin(0.8 * t + 6.28 * hs(6))) * (1 + 0.35 * acc)
            a = (0.30 - 0.14 * hs(1)) * br * m.get("eclat_bokeh", 1.0)
            add_alpha(img, self.bk[key], x, y, pal[i % len(pal)], a)

    def _filantes(self, sp, t):
        for f in self.filantes:
            u = (t - f["t"]) / f["dur"]
            if not 0 <= u <= 1.35:
                continue
            x0, y0, x1, y1 = f["de"][0] * W, f["de"][1] * H, f["vers"][0] * W, f["vers"][1] * H
            k = np.arange(48, dtype=np.float32)
            uh = min(1.0, EASE["outCubic"](min(u, 1.0)))
            uk = np.clip(uh - k * 0.010, 0, 1)
            fade = max(0.0, 1 - max(0.0, u - 1.0) / 0.35)
            inten = (1 - k / 48) ** 2 * 2.2 * fade * (uk > 0)
            inten[0] *= 2.0
            sp.add(x0 + (x1 - x0) * uk, y0 + (y1 - y0) * uk, C("#FFF4DC")[None] * inten[:, None])

    def _coeurs(self, img, t, m):
        for c in self.coeurs:
            win = _smooth((t - c["debut"]) / 1.2) * _smooth((c["fin"] - t) / 1.5)
            if win <= 0.01:
                continue
            pal = [C(h) for h in c.get("couleurs", ["#FF8FB4", "#FFD27A", "#FFB3C8"])]
            for i in range(c["nombre"]):
                hs = lambda k: _hash(i, 41, k)
                r = (24, 34, 48, 66)[int(hs(1) * 4) % 4]
                x = W * (0.06 + 0.88 * hs(2)) + 26 * math.sin(0.5 * t + 6.28 * hs(3))
                span = H + 300
                y = H + 150 - ((t - c["debut"]) * (40 + 50 * hs(4)) + hs(5) * span) % span
                a = win * (0.32 + 0.2 * hs(6)) * (0.85 + 0.15 * math.sin(2.1 * t + 6.28 * hs(7)))
                add_alpha(img, self.hearts[r], x, y, pal[i % len(pal)], a)

    # ---------------------------------------------------------------- un plan
    def render_shot(self, s, t, role, p):
        R = self.R
        acc = self.accent(t)
        if s.get("layout") == "bands":
            img = self._bands(s, t, acc)
        else:
            ph = R.photos[s["photo"]]
            name, m = self.world_of(s)
            z, c, a = R.camera(s, t, role, p)
            fg, A, (sf, tx, ty), Ap = ph.render_layers(W, H, z, c, a)
            sb, tbx, tby = self.parallax(s, ph, sf, tx, ty, m)
            bg = self.background(ph, name, sb, tbx, tby, W, H)
            self._behind(bg, s, ph, name, m, sb, tbx, tby, t, acc)
            if m.get("rayons"):
                bg += self.rays(A, bg, m["rayons"], t)
            Aa = A if Ap is None or ph.cfg.get("aura_objets") else Ap
            self.aura(bg, Aa, C(m["aura"]), m["aura_force"] * (1 + 0.3 * acc))
            subj = fx.apply_grade(fg, s["grade"], s.get("exposure", 0.0))
            img = bg + (subj - bg) * A[..., None]
            self.wrap(img, A, bg, m.get("enveloppe", 0.4))
            live = R.live.get(s["photo"])
            if live:
                live.draw(img, t, (sf, tx, ty))
        base = role.split(":")[0] if role else None
        if base in ("reve", "magie"):                 # la mise au point glisse d'une image à l'autre
            e = p * p * (3 - 2 * p)
            img = fx.defocus(img, {"reve": 6.0, "magie": 9.0}[base] * (e if role.endswith(":out") else 1 - e))
        return img

    def _bands(self, s, t, acc):
        R = self.R
        name, m = self.world_of(s, photo="")
        img = np.empty((H, W, 3), np.float32)
        img[:] = C(m.get("ciel_haut", "#0B1030")) * 0.8
        n = len(s["bands"])
        bh = (H - BAND_GAP * (n - 1)) // n
        for i, b in enumerate(s["bands"]):
            prog = clamp((t - b["t_in"]) / b.get("slide", 0.6))
            if prog <= 0:
                continue
            z, c = R._interp(b, s, t)
            ph = R.photos[b["photo"]]
            bname, bm = self.world_of(s, photo=b["photo"])
            fg, A, (sf, tx, ty), Ap = ph.render_layers(W, bh, z, c)
            bg = self.background(ph, bname, sf, tx, ty, W, bh)
            self.aura(bg, A if Ap is None else Ap, C(bm["aura"]), bm["aura_force"] * (1 + 0.3 * acc))
            subj = fx.apply_grade(fg, s["grade"], s.get("exposure", 0.0))
            band = bg + (subj - bg) * A[..., None]
            self.wrap(band, A, bg, bm.get("enveloppe", 0.4))
            dx = int(round((1 - EASE["outCubic"](prog)) * W * (-1 if b["from"] == "left" else 1)))
            y0 = i * (bh + BAND_GAP)
            xs0, xs1 = max(0, dx), min(W, W + dx)
            img[y0:y0 + bh, xs0:xs1] = band[:, xs0 - dx:xs1 - dx]
        gold = C("#E3B34C")
        for i in range(1, n):
            y = i * (bh + BAND_GAP) - BAND_GAP
            img[y:y + BAND_GAP] = img[y:y + BAND_GAP] * 0.25 + gold * 0.75
            img[y + 2:y + BAND_GAP - 2] = np.float32([1.0, 0.92, 0.72])
        return img

    # ---------------------------------------------------------------- image complète
    def frame(self, t):
        R = self.R
        lays = R.layers(t)
        img = None
        for s, w, role, p in lays:
            if w <= 0.001:
                continue
            layer = self.render_shot(s, t, role, p)
            img = layer * w if img is None else img + layer * w
        prm = R.fx_params(lays)
        cur = R.shots[R.shot_index(t)]
        name, m = self.world_of(cur, photo=cur.get("photo", ""))
        fin = self.st["finition"]

        boost = 0.0                                   # lumière chaude des transitions et des temps forts
        for s, w, role, p in lays:
            base = role.split(":")[0] if role else None
            if base == "light":
                boost = max(boost, 0.16 * math.sin(math.pi * p))
            elif base == "magie":
                boost = max(boost, 0.10 * math.sin(math.pi * p))
            elif base == "reve":
                boost = max(boost, 0.04 * math.sin(math.pi * p))
        for ev in R.events:
            if ev["type"] == "flash" and 0 <= t - ev["t"] < 1.2:
                boost += ev["strength"] * fin["eclairs"] * math.exp(-(t - ev["t"]) / ev["decay"])
        for T in self.cuts:
            if 0 <= t - T < 0.5:
                boost += fin["pulsation_coupes"] * math.exp(-(t - T) / 0.12)
        if boost > 0:
            img = img * (1 + boost * np.float32([1.0, 0.88, 0.70]))
        leaks = prm["leaks"] * m.get("fuites", 0.0)
        if cur.get("reveal"):
            leaks += 0.2 * (1 - clamp((t - cur["start"]) / 5.0))
        Lk = fx.light_leaks(t, leaks, [rgb(h) for h in fin["couleurs_fuites"]])
        if Lk is not None:
            img = fx.screen(img, Lk)
        img = fx.bloom(img, prm["bloom"] * fin["bloom"])
        for ev in R.events:
            if ev["type"] == "flare":
                img = fx.flare(img, t, ev)

        boxes = R.guard_boxes(lays, t)                # magie devant elle : jamais sur un visage ni une main
        spv = Splat(2.2, ((3.0, 0.30), (10.0, 0.08)))
        sps = Splat(1.6, ((2.5, 0.25), (9.0, 0.06)))
        for v in self.vortex:
            v.points(spv, t, front=True, boxes=boxes)
            v.stars(img, t, front=True, star=self.star, boxes=boxes)
        self._cut_sparks(sps, t, boxes)
        for k in (spv, sps):
            L = k.render()
            if L is not None:
                img += L
        for v in self.vortex:
            v.flash(img, t, self.halo_top, boxes)
        if self.lanternes:
            self.lanternes.draw(img, t, front=True, boxes=boxes)
        self._front_bokeh(img, t, m, boxes)
        img *= self.vignette
        R.particles.draw(img, t, prm["particles"] * fin["poussiere"], "gold")
        tr = R.transforms(lays, t)
        for c in self.comets:
            if isinstance(c, Comet):
                c.draw(img, t, lambda u, v: (u * W, v * H))
            else:
                tf = tr.get(c["photo"])
                if tf is None:
                    continue
                sc, tx, ty, pw, ph_ = tf
                if c["nom"] not in self._cbuilt:
                    self._cbuilt[c["nom"]] = Comet(c, (pw, ph_))
                self._cbuilt[c["nom"]].draw(img, t, lambda u, v: (u * pw * sc + tx, v * ph_ * sc + ty))
        img = self.tone[np.clip(img * 1023.5, 0, 2047).astype(np.int32)]
        for tb in R.texts:
            tb.draw(img, t)
        g = 1.0
        if cur.get("fade_in"):
            g *= EASE["inOutSine"](clamp((t - cur["start"]) / cur["fade_in"]))
        if cur.get("fade_out"):
            g *= 1 - EASE["inOutSine"](clamp((t - (cur["end"] - cur["fade_out"])) / cur["fade_out"]))
        if g < 1:
            img *= g
        img += self.grain[int(t * FPS) // 2 % len(self.grain)] * (0.35 + 0.65 * g)
        return (np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)

    def _cut_sparks(self, sp, t, boxes):
        for k, T in enumerate(self.cuts):
            tau = t - T
            if not 0 <= tau < 0.85:
                continue
            n = 56
            i = np.arange(n, dtype=np.float32)
            hs = lambda j: (np.sin((i + 1) * (12.9898 + j) + T * 78.233) * 43758.5453) % 1.0
            side = np.where(hs(1) < 0.5, -1.0, 1.0)
            x0 = np.where(side < 0, W * 0.10 * hs(2), W * (1 - 0.10 * hs(2)))
            y0 = H * (0.30 + 0.55 * hs(3))
            vx = -side * (180 + 420 * hs(4))
            vy = -(120 + 380 * hs(5))
            f = (1 - math.exp(-2.8 * tau)) / 2.8
            x = x0 + vx * f
            y = y0 + vy * f + 110 * tau * tau
            u = tau / (0.55 + 0.3 * hs(6))
            inten = np.clip(1 - u, 0, 1) ** 1.3 * (0.7 + 0.3 * np.sin(30 * tau + 6.28 * hs(7))) * 1.6
            col = np.where(hs(8)[:, None] < 0.7, C("#FFE2A0"), C("#FFF6E8"))
            sp.add(x, y, col * (inten * guard_vec(boxes, x, y))[:, None])

    def _front_bokeh(self, img, t, m, boxes):
        n = int(m.get("bokeh_avant", 0))
        pal = [C(h) for h in m["palette"]]
        for i in range(n):
            hs = lambda k: _hash(i, 73, k)
            key = (90, 120, 150)[int(hs(1) * 3) % 3]
            x = W * (0.05 + 0.9 * hs(2)) + 40 * math.sin(0.11 * t + 6.28 * hs(3))
            span = H + 2 * key * 1.4
            y = H + key * 1.4 - ((t * (10 + 12 * hs(4)) + hs(5) * span) % span)
            a = (0.07 + 0.05 * hs(6)) * guard_pt(boxes, x, y, key * 0.7, 140)
            add_alpha(img, self.bk[key], x, y, pal[(i + 1) % len(pal)], a)
