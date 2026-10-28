"""Version rêve : diffusion lumineuse, bords oniriques, bokeh pastel et cœurs, étoiles de fée,
traînées magiques (poussière d'étoiles) et lanternes flottantes.

Inspiré du langage visuel des grandes romances de cinéma, sans aucun logo ni élément de marque.
Chaque élément est une fonction pure du temps (rendu parallèle par segments sans raccord visible)
et s'efface à l'approche des visages et des mains (zones protégées de la photo à l'écran).
"""
import math

import cv2
import numpy as np

from common import EASE, H, W, clamp, rgb
from livefx import _dot, _hash, _smooth, _star, put

LUMA = np.float32([0.2126, 0.7152, 0.0722])


def screen(a, b):
    return 1 - (1 - a) * (1 - np.clip(b, 0, 1))


def add(img, spr, cx, cy, col, alpha):
    """Ajout lumineux d'un sprite centré (sans rotation)."""
    if alpha <= 0.004:
        return
    h, w = spr.shape
    x0, y0 = int(round(cx - w / 2)), int(round(cy - h / 2))
    X0, Y0, X1, Y1 = max(0, x0), max(0, y0), min(W, x0 + w), min(H, y0 + h)
    if X1 <= X0 or Y1 <= Y0:
        return
    img[Y0:Y1, X0:X1] += spr[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0, None] * (col * alpha)


def guard(boxes, x, y, r=0.0, ramp=90.0):
    f = 1.0
    for x0, y0, x1, y1, st in boxes:
        dx = max(x0 - x, 0, x - x1)
        dy = max(y0 - y, 0, y - y1)
        d = math.hypot(dx, dy) - r
        f = min(f, 1 - st * (1 - _smooth(d / ramp)))
    return f


def _bokeh(r):
    """Disque de bokeh : remplissage doux, liseré plus lumineux, léger halo."""
    n = int(r * 2.8) // 2 * 2 + 1
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32) - n // 2
    d = np.sqrt(xx * xx + yy * yy)
    edge = np.clip((r - d) / max(1.5, r * 0.07), 0, 1)
    rim = np.exp(-((d - r * 0.86) ** 2) / (2 * (r * 0.07) ** 2)) * edge
    a = 0.55 * edge + 0.45 * rim + 0.16 * np.exp(-(d ** 2) / (2 * (r * 0.95) ** 2))
    return (a / a.max()).astype(np.float32)


def _heart(r):
    """Cœur de bokeh (forme douce, liseré lumineux)."""
    S = int(r * 2.6) // 2 * 2 + 1
    t = np.linspace(0, 2 * np.pi, 360)
    x = 16 * np.sin(t) ** 3
    y = -(13 * np.cos(t) - 5 * np.cos(2 * t) - 2 * np.cos(3 * t) - np.cos(4 * t))
    x = x / 16 * r * 0.95 + S / 2
    y = (y - 2.5) / 14.5 * r * 0.95 + S / 2
    m = np.zeros((S, S), np.uint8)
    cv2.fillPoly(m, [np.round(np.stack([x, y], 1) * 4).astype(np.int32)], 255, lineType=cv2.LINE_AA, shift=2)
    a = cv2.GaussianBlur(m.astype(np.float32) / 255, (0, 0), max(1.0, r * 0.06))
    rim = np.clip(a - cv2.GaussianBlur(a, (0, 0), max(1.0, r * 0.12)), 0, 1)
    a = 0.55 * a + 1.2 * rim
    return (a / a.max()).astype(np.float32)


def _halo(r):
    n = int(r * 3) // 2 * 2 + 1
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32) - n // 2
    d2 = xx * xx + yy * yy
    a = np.exp(-d2 / (2 * (r * 0.55) ** 2))
    return (a / a.max()).astype(np.float32)


def _lantern(r):
    """Cœur lumineux d'une lanterne (forme légèrement allongée)."""
    n = int(r * 3) // 2 * 2 + 1
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32) - n // 2
    d2 = (xx / 0.75) ** 2 + (yy / 1.0) ** 2
    a = np.exp(-d2 / (2 * (r * 0.42) ** 2))
    return (a / a.max()).astype(np.float32)


class Path:
    """Courbe lissée (Catmull-Rom) paramétrée par l'abscisse curviligne (en pixels), avec cœur optionnel."""

    def __init__(self, pts, aspect, heart=None):
        P = np.asarray(pts, np.float64)
        P = np.vstack([P[0], P, P[-1]])
        dense = []
        for i in range(1, len(P) - 2):
            p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
            for u in np.linspace(0, 1, 28, endpoint=False):
                u2, u3 = u * u, u * u * u
                dense.append(0.5 * ((2 * p1) + (-p0 + p2) * u + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u2 + (-p0 + 3 * p1 - 3 * p2 + p3) * u3))
        dense.append(P[-2])
        self.heart_from = None
        if heart:
            cx, cy = heart["centre"]
            hw, hh = heart["demi_largeur"], heart["demi_hauteur"]
            th = np.linspace(0, -2 * np.pi, 220)                     # du creux du cœur, par le lobe gauche
            hx = cx + hw * 16 * np.sin(th) ** 3 / 16
            hy = cy + hh * (-(13 * np.cos(th) - 5 * np.cos(2 * th) - 2 * np.cos(3 * th) - np.cos(4 * th)) - 2.5) / 14.5
            start_heart = len(dense)
            dense += list(np.stack([hx, hy], 1))
        D = np.asarray(dense)
        seg = np.hypot(np.diff(D[:, 0]) * aspect[0], np.diff(D[:, 1]) * aspect[1])
        cum = np.r_[0, np.cumsum(seg)]
        self.s = cum / cum[-1]
        self.D = D
        if heart:
            self.heart_from = float(self.s[start_heart])

    def at(self, s):
        return float(np.interp(s, self.s, self.D[:, 0])), float(np.interp(s, self.s, self.D[:, 1]))


class Comet:
    """Traînée de poussière d'étoiles : une tête brillante suit la courbe et sème des paillettes qui
    scintillent, tombent doucement et s'éteignent (ou persistent pour dessiner une forme)."""

    def __init__(self, cfg, aspect):
        self.cfg = cfg
        self.t0, self.dur = cfg["t0"], cfg["dur"]
        self.n, self.life = cfg["particules"], cfg["vie"]
        self.space, self.photo = cfg["espace"], cfg.get("photo")
        self.persist = cfg.get("persiste_jusqua")
        self.path = Path(cfg["points"], aspect, cfg.get("coeur"))
        self.star = _star(7.0)
        self.dot = _dot(2.6)
        self.head = _halo(26)
        self.glow_s = _halo(11)
        self.seed = sum(ord(c) for c in cfg["nom"])

    def active(self, t):
        end = self.persist if self.persist else self.t0 + self.dur + self.life + 0.3
        return self.t0 - 0.05 <= t <= end

    def draw(self, img, t, tomap):
        if not self.active(t):
            return
        tau = clamp((t - self.t0) / self.dur)
        s_head = 0.5 - 0.5 * math.cos(math.pi * tau)
        sd = self.seed
        for k in range(self.n):
            s_k = k / (self.n - 1)
            if s_k > s_head + 1e-6:
                break
            te = self.t0 + self.dur * math.acos(clamp(1 - 2 * s_k, -1, 1)) / math.pi
            age = t - te
            keep = self.persist is not None and self.path.heart_from is not None and s_k >= self.path.heart_from
            life = (self.persist - te) if keep else self.life * (0.6 + 0.8 * _hash(sd, k, 3))
            if age < 0 or age > life:
                continue
            u, v = self.path.at(s_k)
            x, y = tomap(u, v)
            jx, jy = (_hash(sd, k, 4) - 0.5) * 18, (_hash(sd, k, 5) - 0.5) * 18
            tw = 0.55 + 0.45 * math.sin(13 * t + 6.28 * _hash(sd, k, 6))
            if keep:
                x += jx * 0.35
                y += jy * 0.35 + 3 * math.sin(1.7 * t + k)
                a = min(1.0, age / 0.15) * (0.55 + 0.45 * tw)
            else:
                x += jx + (_hash(sd, k, 7) - 0.5) * 50 * age
                y += jy + 26 * age + 18 * age * age
                a = (1 - age / life) ** 1.4 * tw * min(1.0, age / 0.06)
            star = _hash(sd, k, 8) < 0.32
            sc = 0.7 + 0.6 * _hash(sd, k, 9)
            col = np.float32([1.0, 0.96, 0.90]) if star else np.float32([1.0, 0.84, 0.76])
            put(img, col, self.star if star else self.dot, x, y, sc, sc, 0.6 * age + k, a, add=True)
        if self.persist and self.path.heart_from is not None and s_head > self.path.heart_from:
            done = t - (self.t0 + self.dur)
            beat = 0.0
            if done > 0:                                 # battement de cœur (double pulsation, 64 / min)
                ph = (done % 0.94)
                beat = math.exp(-ph / 0.10) + 0.6 * math.exp(-max(0.0, ph - 0.24) / 0.10) * (ph >= 0.24)
            for j, sh in enumerate(np.linspace(self.path.heart_from, 1.0, 110)):
                if sh > s_head:
                    break
                u, v = self.path.at(sh)
                x, y = tomap(u, v)
                fl = 0.75 + 0.25 * math.sin(5 * t + j)
                put(img, np.float32([1.0, 0.78, 0.80]), self.glow_s, x, y, 1.0, 1.0, 0, (0.16 + 0.16 * beat) * fl, add=True)
        if 0 < tau < 1:
            u, v = self.path.at(s_head)
            x, y = tomap(u, v)
            put(img, np.float32([1.0, 0.86, 0.78]), self.head, x, y, 1.0, 1.0, 0, 0.55, add=True)
            put(img, np.float32([1.0, 0.98, 0.94]), self.star, x, y, 1.9, 1.9, 2.0 * t, 1.0, add=True)


class Dream:
    def __init__(self, style, sections_order):
        self.st = style
        d = style["diffusion"]
        self.halo, self.voile, self.bords = d["halo"], d["voile"], d["bords"]
        y, x = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((x - W / 2) / (W / 2)) ** 2 * 0.9 + ((y - H / 2) / (H / 2)) ** 2 * 0.7)
        e = np.clip((r - 0.62) / 0.60, 0, 1)
        self.edge = (e * e * (3 - 2 * e))[..., None].astype(np.float32)
        self.rose = np.float32(rgb("#FFE6E6"))
        self.sec = style["sections"]
        self.bokeh = {r: _bokeh(r) for r in (16, 24, 34, 48, 66, 90)}
        self.hearts = {r: _heart(r) for r in (16, 24, 34, 48, 66, 90)}
        self.star = _star(6.0)
        self.halo_l, self.lant = _halo(60), _lantern(9)
        lt = style.get("lanternes")
        self.lant_win = (lt["debut"], lt["fin"], lt["nombre"]) if lt else None
        self.comets = []
        for c in style.get("cometes", []):
            self.comets.append(c)          # Path construit à la première utilisation (dépend de l'aspect)
        self._built = {}

    # ---------------------------------------------------------------- paramètres de section mélangés
    def params(self, lays):
        dens = {"bokeh": 0.0, "etoiles": 0.0, "coeurs": 0.0}
        pal = np.zeros((4, 3), np.float32)
        tot = 0.0
        for s, w, _, _ in lays:
            p = self.sec[s["section"]]
            for k in dens:
                dens[k] += p[k] * w
            pal += np.float32([rgb(c) for c in p["palette"]]) * w
            tot += w
        tot = max(tot, 1e-6)
        dens = {k: v / tot for k, v in dens.items()}
        return dens, pal / tot

    # ---------------------------------------------------------------- diffusion et bords
    def diffuse(self, img, extra=0.0):
        small = cv2.resize(img, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
        g1 = cv2.GaussianBlur(small, (0, 0), 4)
        g2 = cv2.GaussianBlur(small, (0, 0), 12)
        hi = np.clip((g1 @ LUMA - 0.28) / 0.62, 0, 1)[..., None]
        glow = (0.6 * g1 + 0.4 * g2) * (0.30 + 0.70 * hi) * np.float32([1.0, 0.95, 0.92])
        up = cv2.resize(glow, (W, H), interpolation=cv2.INTER_LINEAR)
        out = screen(img, up * (self.halo + extra))
        g2u = cv2.resize(g2, (W, H), interpolation=cv2.INTER_LINEAR)
        out = out * (1 - self.voile) + g2u * self.voile
        out += (g2u + self.rose * 0.04 - out) * (self.edge * self.bords)
        return out

    # ---------------------------------------------------------------- bokeh, cœurs, lanternes (avant diffusion)
    def lights(self, img, t, dens, pal, boxes):
        n = 38
        for i in range(n):
            rank = _hash(i, 101)
            if rank > dens["bokeh"]:
                continue
            fade = clamp((dens["bokeh"] - rank) / 0.08)
            depth = _hash(i, 102)
            r = 16 + 74 * depth ** 1.4
            key = min(self.bokeh, key=lambda k: abs(k - r))
            side = _hash(i, 103)
            x0 = W * (0.02 + 0.24 * _hash(i, 104)) if side < 0.38 else (W * (0.74 + 0.24 * _hash(i, 104)) if side < 0.76 else W * (0.15 + 0.7 * _hash(i, 104)))
            v = 5 + 16 * depth
            span = H + 2 * key * 1.4
            y = H + key * 1.4 - ((t * v + _hash(i, 105) * span) % span)
            x = x0 + 16 * math.sin(0.21 * t + 6.28 * _hash(i, 106))
            breath = 0.85 + 0.15 * math.sin(0.9 * t + 6.28 * _hash(i, 107))
            a = (0.26 - 0.13 * depth) * breath * fade * guard(boxes, x, y, key * 0.6)
            col = pal[i % 4]
            hk = 1.0 if _hash(i, 108) < dens["coeurs"] else 0.0
            if hk < 1:
                add(img, self.bokeh[key], x, y, col, a * (1 - hk))
            if hk > 0:
                add(img, self.hearts[key], x, y, col, a * hk * 1.15)
        if self.lant_win:
            t0, t1, nl = self.lant_win
            win = _smooth((t - t0) / 1.5) * _smooth((t1 - t) / 1.5)
            if win > 0.01:
                for i in range(nl):
                    depth = _hash(i, 201)
                    v = 18 + 26 * depth
                    span = H + 500
                    y = H + 250 - ((t * v + _hash(i, 202) * span) % span)
                    side = _hash(i, 203)
                    x = W * (0.03 + 0.22 * _hash(i, 204)) if side < 0.42 else (W * (0.75 + 0.22 * _hash(i, 204)) if side < 0.84 else W * (0.3 + 0.4 * _hash(i, 204)))
                    x += 18 * math.sin(0.4 * t + 6.28 * _hash(i, 205))
                    fl = 0.82 + 0.18 * math.sin(7.3 * t + 6.28 * _hash(i, 206)) * math.sin(3.1 * t + _hash(i, 207))
                    sc = 0.7 + 0.7 * depth
                    a = win * fl * guard(boxes, x, y, 40)
                    put(img, np.float32([1.0, 0.62, 0.30]), self.halo_l, x, y, sc, sc, 0, 0.45 * a, add=True)
                    put(img, np.float32([1.0, 0.86, 0.58]), self.lant, x, y, sc * 1.4, sc * 1.4, 0, 0.95 * a, add=True)

    # ---------------------------------------------------------------- étoiles de fée et comètes (après diffusion)
    def sparkles(self, img, t, dens, boxes, transforms):
        n = 42
        for i in range(n):
            rank = _hash(i, 301)
            if rank > dens["etoiles"]:
                continue
            fade = clamp((dens["etoiles"] - rank) / 0.08)
            side = _hash(i, 302)
            if side < 0.35:
                x, y = W * (0.02 + 0.22 * _hash(i, 303)), H * (0.05 + 0.9 * _hash(i, 304))
            elif side < 0.7:
                x, y = W * (0.76 + 0.22 * _hash(i, 303)), H * (0.05 + 0.9 * _hash(i, 304))
            else:
                x, y = W * (0.1 + 0.8 * _hash(i, 303)), H * (0.03 + 0.10 * _hash(i, 304)) if _hash(i, 305) < 0.5 else H * (0.86 + 0.12 * _hash(i, 304))
            x += 10 * math.sin(0.3 * t + i)
            y += 8 * math.sin(0.25 * t + 1.7 * i)
            P = 0.9 + 1.4 * _hash(i, 306)
            ph = (t / P + _hash(i, 307)) % 1.0
            tw = max(0.0, math.sin(math.pi * ph)) ** 4
            a = tw * fade * guard(boxes, x, y, 10)
            sc = 0.7 + 0.9 * _hash(i, 308)
            col = [np.float32([1.0, 0.97, 0.92]), np.float32([1.0, 0.86, 0.80]), np.float32([1.0, 0.92, 0.72])][i % 3]
            put(img, col, self.star, x, y, sc, sc, 0.3 * t + i, a, add=True)
        for c in self.comets:
            key = c["nom"]
            if c["espace"] == "photo":
                tr = transforms.get(c["photo"])
                if tr is None:
                    continue
                s, tx, ty, pw, ph_ = tr
                if key not in self._built:
                    self._built[key] = Comet(c, (pw, ph_))
                self._built[key].draw(img, t, lambda u, v: (u * pw * s + tx, v * ph_ * s + ty))
            else:
                if key not in self._built:
                    self._built[key] = Comet(c, (W, H))
                self._built[key].draw(img, t, lambda u, v: (u * W, v * H))
