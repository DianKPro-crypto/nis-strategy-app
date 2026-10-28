"""Éléments magiques partagés : traînées de poussière d'étoiles (comètes, cœur du baiser final),
disques de bokeh et cœurs lumineux. Utilisés par la version « Nuit enchantée » (src/enchant.py).

Chaque élément est une fonction pure du temps (rendu parallèle par segments sans raccord visible).
"""
import math

import cv2
import numpy as np

from common import clamp
from livefx import _dot, _hash, _star, put

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
