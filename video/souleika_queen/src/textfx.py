"""Typographie animée : Playfair Display (titres) + Inter (mentions). Deux familles maximum.

Chaque caractère est un sprite positionné avec le crénage de la police ; l'animation déplace et fond
les caractères (apparition lettre à lettre, resserrement de l'interlettrage), puis un reflet doré
balaie les titres. Un dégradé sombre localisé (scrim) garantit la lisibilité sans voiler la photo.
"""
import math

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from common import EASE, ROOT, clamp, rgb
from livefx import _dot, _hash, _star, put

FONT_DIR = ROOT / "assets" / "fonts"
FONTS = {
    ("display", 700): FONT_DIR / "playfair-display-latin-700-normal.woff",
    ("display", 500): FONT_DIR / "playfair-display-latin-500-normal.woff",
    ("display_italic", 500): FONT_DIR / "playfair-display-latin-500-italic.woff",
    ("serif", 500): FONT_DIR / "playfair-display-latin-500-normal.woff",
    ("caption", 600): FONT_DIR / "Inter-SemiBold.otf",
}
DEFAULT_WEIGHT = {"display": 700, "display_italic": 500, "serif": 500, "caption": 600}
GOLD_STOPS = [(0.0, rgb("#FBEFD2")), (0.45, rgb("#E4C886")), (1.0, rgb("#B88E4A"))]
ROSE_STOPS = [(0.0, rgb("#FFF7EE")), (0.45, rgb("#F6D6B4")), (1.0, rgb("#DCA486"))]   # version rêve : or rosé
GLOW = np.float32([1.0, 0.84, 0.74])
IVORY_STOPS = [(0.0, rgb("#FFFBF4")), (1.0, rgb("#EDE3D2"))]
SHINE = np.float32(rgb("#FFF8E6"))
_font_cache = {}


def font(style, size, weight=None):
    w = weight or DEFAULT_WEIGHT[style]
    key = (style, w, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(str(FONTS[(style, w)]), size)
    return _font_cache[key]


def gradient(stops, n):
    t = np.linspace(0, 1, n, dtype=np.float32)
    out = np.zeros((n, 3), np.float32)
    for c in range(3):
        out[:, c] = np.interp(t, [s[0] for s in stops], [s[1][c] for s in stops])
    return out


def blend(img, x, y, color, alpha):
    """Mélange alpha d'un sprite (color HxWx3 ou couleur unique) à la position entière (x, y)."""
    h, w = alpha.shape
    H, W = img.shape[:2]
    x0, y0, x1, y1 = max(0, x), max(0, y), min(W, x + w), min(H, y + h)
    if x1 <= x0 or y1 <= y0:
        return
    a = alpha[y0 - y:y1 - y, x0 - x:x1 - x, None]
    c = color[y0 - y:y1 - y, x0 - x:x1 - x] if color.ndim == 3 else color
    reg = img[y0:y1, x0:x1]
    reg += (c - reg) * a


def heart_sprite(size):
    """Petit cœur vectoriel (courbe paramétrique), dégradé or, suréchantillonné x4."""
    S = size * 4
    t = np.linspace(0, 2 * np.pi, 400)
    x = 16 * np.sin(t) ** 3
    y = -(13 * np.cos(t) - 5 * np.cos(2 * t) - 2 * np.cos(3 * t) - np.cos(4 * t))
    x = (x - x.min()) / (x.max() - x.min()) * (S - 8) + 4
    y = (y - y.min()) / (y.max() - y.min()) * (S * 0.92 - 8) + 4
    im = Image.new("L", (S, S), 0)
    ImageDraw.Draw(im).polygon(list(zip(x, y)), fill=255)
    im = im.resize((size, size), Image.LANCZOS)
    a = np.asarray(im, np.float32) / 255
    col = gradient(GOLD_STOPS, size)[:, None, :].repeat(size, 1)
    return col, a


class TextBlock:
    def __init__(self, cfg, beats=None, look=None):
        """look (version rêve) : {"palette": "or_rose", "halo": True} ; anim « baguette » disponible."""
        self.look = look or {}
        self.cfg = cfg
        self.id = cfg["id"]
        self.start, self.end = cfg["start"], cfg["end"]
        self.anim = cfg.get("anim", "rise")
        self.speed = cfg.get("speed", 1.0)
        self.fade_out = cfg.get("fade_out", 0.45)
        self.beats = beats or []
        self.glyphs = []          # dict: x, y, col, a, sh (ombre), order, t_in, line
        self.extras = []
        cx, cy = cfg["pos"]
        lines = cfg["lines"]
        metrics = []
        for ln in lines:
            st = ln["style"]
            f = font(st, ln["size"], ln.get("weight"))
            text = ln["text"]
            segs = text.split("|")
            if st == "caption":
                segs = [s.upper() for s in segs]
            full = "".join(segs)
            track = ln.get("tracking", 0.0) * ln["size"]
            width = f.getlength(full) + track * max(0, len(full) - 1)
            lh = ln["size"] * (1.55 if st == "caption" else 1.16)
            metrics.append((f, segs, full, track, width, lh))
        total_h = sum(m[5] for m in metrics)
        y = cy - total_h / 2
        order = 0
        heart = None
        for li, (ln, (f, segs, full, track, width, lh)) in enumerate(zip(lines, metrics)):
            size = ln["size"]
            asc, desc = f.getmetrics()
            baseline = y + lh / 2 + (asc - desc) / 2 - (0.06 * size if ln["style"] != "caption" else 0)
            x_left = cx - width / 2
            gold = ROSE_STOPS if self.look.get("palette") == "or_rose" else GOLD_STOPS
            stops = IVORY_STOPS if (ln["style"] in ("caption", "serif") or ln.get("color") == "ivory") else gold
            grad_top = baseline - size * 0.78
            grad = gradient(stops, int(size * 1.05) + 2)
            seg_times = ln.get("times")
            delay = ln.get("delay", 0.0)
            ci = 0
            for si, seg in enumerate(segs):
                for ch in seg:
                    gx = x_left + f.getlength(full[:ci]) + ci * track
                    ci += 1
                    if ch == " ":
                        continue
                    pad = int(size * 0.6)
                    m = Image.new("L", (int(size * 2.2) + 2 * pad, int(size * 2.2)), 0)
                    ox, oy = pad, int(size * 1.5)
                    ImageDraw.Draw(m).text((ox, oy), ch, font=f, fill=255, anchor="ls")
                    bb = m.getbbox()
                    if not bb:
                        continue
                    m = m.crop(bb)
                    a = np.asarray(m, np.float32) / 255
                    gx0 = int(round(gx + bb[0] - ox))
                    gy0 = int(round(baseline + bb[1] - oy))
                    rows = np.clip(np.arange(gy0, gy0 + a.shape[0]) - grad_top, 0, len(grad) - 1).astype(int)
                    col = grad[rows][:, None, :].repeat(a.shape[1], 1)
                    # ombre portée douce (lisibilité) : sprite élargi et flouté
                    sp = int(size * 0.14) + 4
                    shm = Image.fromarray((a * 255).astype(np.uint8)).crop((-sp, -sp, a.shape[1] + sp, a.shape[0] + sp))
                    shm = shm.filter(ImageFilter.GaussianBlur(size * 0.055 + 1.5))
                    sh = np.asarray(shm, np.float32) / 255
                    gl, gp = None, 0
                    if self.look.get("halo"):
                        gp = int(size * 0.32) + 4
                        glm = Image.fromarray((a * 255).astype(np.uint8)).crop((-gp, -gp, a.shape[1] + gp, a.shape[0] + gp))
                        gl = np.asarray(glm.filter(ImageFilter.GaussianBlur(size * 0.13 + 2)), np.float32) / 255
                    t_in = self.start + delay
                    if seg_times:
                        t_in = seg_times[si]
                    self.glyphs.append(dict(x=gx0, y=gy0, col=col, a=a, sh=sh, sp=sp, gl=gl, gp=gp, order=order,
                                            t_in=t_in, line=li, cx=gx0 + a.shape[1] / 2, size=size, base=baseline))
                    order += 1
            if ln.get("rules"):
                for side in (-1, 1):
                    L = int(size * 1.8)
                    xx = int(cx - width / 2 - size * 0.7 - L) if side < 0 else int(cx + width / 2 + size * 0.7)
                    yy = int(baseline - size * 0.36)
                    a = np.ones((2, L), np.float32)
                    a[:, : L // 5] *= np.linspace(0, 1, L // 5)[None] if side < 0 else 1
                    a[:, -(L // 5):] *= np.linspace(1, 0, L // 5)[None] if side > 0 else 1
                    self.glyphs.append(dict(x=xx, y=yy, col=np.float32(rgb("gold")), a=a, sh=np.zeros((2, L), np.float32),
                                            sp=0, gl=None, gp=0, order=order, t_in=self.start + delay, line=li,
                                            cx=xx + L / 2, size=size, base=baseline))
                    order += 1
            if ln.get("heart"):
                hs = int(size * 0.5)
                hc, ha = heart_sprite(hs)
                heart = dict(x=int(cx + width / 2 + size * 0.28), y=int(baseline - size * 0.62), col=hc, a=ha, size=hs)
            y += lh
        self.n = order
        # lignes (pour l'animation « baguette ») : étendue, ligne de base, taille, instant d'apparition
        self.lines = {}
        for g in self.glyphs:
            L = self.lines.setdefault(g["line"], dict(x0=1e9, x1=-1e9, base=g["base"], size=g["size"], t_in=g["t_in"]))
            L["x0"], L["x1"] = min(L["x0"], g["x"]), max(L["x1"], g["x"] + g["a"].shape[1])
            L["t_in"] = min(L["t_in"], g["t_in"])
        xs = [g["x"] for g in self.glyphs] + [g["x"] + g["a"].shape[1] for g in self.glyphs]
        ys = [g["y"] for g in self.glyphs] + [g["y"] + g["a"].shape[0] for g in self.glyphs]
        self.bbox = [min(xs), min(ys), max(xs), max(ys)]
        if heart:
            self.heart = heart
            self.bbox = [self.bbox[0], min(self.bbox[1], heart["y"]), max(self.bbox[2], heart["x"] + heart["size"]),
                         max(self.bbox[3], heart["y"] + heart["size"])]
        else:
            self.heart = None
        self.route = None
        if cfg.get("route"):
            self._build_route()
        self.sig = None
        if cfg.get("signature"):
            self._build_signature()
        self._build_scrim(cfg.get("scrim", 0.0))

    # ---------------------------------------------------------------- éléments graphiques
    def _build_route(self):
        x0, x1 = 170, 910
        yb = self.bbox[3] + 46
        n = x1 - x0
        xs = np.arange(n, dtype=np.float32)
        u = xs / (n - 1)
        yline = yb - 26 * np.sin(np.pi * u)                 # arc abstrait (pas une carte)
        hgt = 90
        top = int(yb - 26 - hgt / 2)
        yy = np.arange(hgt, dtype=np.float32)[:, None] + top
        d = np.abs(yy - yline[None, :])
        a = np.exp(-d ** 2 / (2 * 1.1 ** 2)) + 0.28 * np.exp(-d ** 2 / (2 * 6.0 ** 2))
        self.route = dict(x=x0, y=top, a=a.astype(np.float32), yline=yline, n=n)
        self.bbox[3] = max(self.bbox[3], top + hgt)

    def _build_signature(self):
        mono = Image.open(ROOT / "assets" / "dk_monogram.png").convert("RGBA")
        hgt = 62
        mono = mono.resize((int(mono.width * hgt / mono.height), hgt), Image.LANCZOS)
        arr = np.asarray(mono, np.float32) / 255
        width = arr.shape[1]
        gap = 22
        # décaler le texte vers la droite pour centrer l'ensemble monogramme + nom
        shift = (width + gap) / 2
        for g in self.glyphs:
            g["x"] += int(shift)
            g["cx"] += shift
        xmin = min(g["x"] for g in self.glyphs)
        ymid = (min(g["y"] for g in self.glyphs) + max(g["y"] + g["a"].shape[0] for g in self.glyphs)) / 2
        self.sig = dict(x=int(xmin - gap - width), y=int(ymid - hgt / 2), col=arr[..., :3].copy(), a=arr[..., 3].copy())
        self.bbox = [self.sig["x"], min(self.bbox[1], self.sig["y"]), self.bbox[2] + int(shift), max(self.bbox[3], self.sig["y"] + hgt)]

    def _build_scrim(self, opacity):
        self.scrim = None
        if opacity <= 0:
            return
        x0, y0, x1, y1 = self.bbox
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        if self.cfg.get("scrim_shape", "band" if abs(self.cfg["pos"][0] - 540) < 40 else "ellipse") == "band":
            # bande pleine largeur à profil doux (comme un dégradé de tiers inférieur), sans forme visible
            half = (y1 - y0) / 2 + 26
            sig = 150.0
            Y0 = int(cy - half - 3 * sig)
            yy = np.arange(int(2 * (half + 3 * sig)), dtype=np.float32) + Y0
            dist = np.maximum(np.abs(yy - cy) - half, 0)
            prof = np.exp(-(dist / sig) ** 2) * opacity
            a = np.repeat(prof[:, None], 1080, axis=1)
            self.scrim = dict(x=0, y=Y0, a=a.astype(np.float32), col=np.float32(rgb("night")))
            return
        # dégradé localisé à profil gaussien pour les titres en colonne
        rx, ry = (x1 - x0) / 2 + 240, (y1 - y0) / 2 + 200
        X0, Y0 = int(cx - rx), int(cy - ry)
        yy, xx = np.mgrid[0:int(2 * ry), 0:int(2 * rx)].astype(np.float32)
        ex, ey = ((x1 - x0) / 2 + 40) / rx, ((y1 - y0) / 2 + 30) / ry
        d2 = (np.maximum(np.abs(xx / rx - 1) - ex * 0.55, 0) / (1 - ex * 0.55)) ** 2 + \
             (np.maximum(np.abs(yy / ry - 1) - ey * 0.55, 0) / (1 - ey * 0.55)) ** 2
        a = np.exp(-d2 * 5.0) * opacity
        self.scrim = dict(x=X0, y=Y0, a=a.astype(np.float32), col=np.float32(rgb("night")))

    # ---------------------------------------------------------------- animation
    def active(self, t):
        return self.start - 0.02 <= t <= self.end + 0.02

    def _glyph_state(self, g, t):
        sp = self.speed
        if self.anim == "static":
            return 1.0, 0.0, 0.0
        if self.anim == "fade":
            e = EASE["inOutSine"](clamp((t - g["t_in"]) / (0.8 / sp)))
            return e, 0.0, 0.0
        if self.anim == "track":
            p = clamp((t - g["t_in"]) / (1.1 / sp))
            e = EASE["outCubic"](p)
            k = 0.45 * (1 - e)
            line_cx = self.cfg["pos"][0]
            return min(1.0, p * 1.8), 0.0, (g["cx"] - line_cx) * k
        if self.anim == "wand":
            # baguette : une étincelle parcourt la ligne et fait naître les lettres sur son passage
            L = self.lines[g["line"]]
            head = self._wand_head(L, t)[0]
            p = clamp((head - g["cx"] + 30) / 70)
            e = p * p * (3 - 2 * p)
            return e, (1 - e) * g["size"] * 0.10, 0.0
        # rise : apparition lettre à lettre
        t0 = g["t_in"] + g["order_in_line"] * (0.034 / sp)
        p = clamp((t - t0) / (0.62 / sp))
        e = EASE["outCubic"](p)
        return min(1.0, p * 1.7), (1 - e) * g["size"] * 0.32, 0.0

    def _wand_head(self, L, t):
        dur = (0.55 + 0.45 * min(1.0, (L["x1"] - L["x0"]) / 700)) / self.speed
        prog = clamp((t - L["t_in"]) / dur)
        head = L["x0"] - 40 + (L["x1"] - L["x0"] + 80) * EASE["inOutSine"](prog)
        return head, prog, dur

    def _glitter(self, img, t, A):
        """Paillettes semées par la baguette le long de chaque ligne, puis tête étincelante."""
        for li, L in self.lines.items():
            head, prog, dur = self._wand_head(L, t)
            if t < L["t_in"] or t > L["t_in"] + dur + 1.0:
                continue
            span = L["x1"] - L["x0"] + 80
            K = int(12 + (L["x1"] - L["x0"]) / 32)
            for k in range(K):
                xk = L["x0"] - 20 + (L["x1"] - L["x0"] + 40) * _hash(li, k, 41.3)
                yk = L["base"] - L["size"] * (0.05 + 0.75 * _hash(li, k, 42.7))
                te = L["t_in"] + dur * clamp((xk - (L["x0"] - 40)) / span)
                age = t - te
                if not 0 <= age <= 0.9:
                    continue
                tw = 0.55 + 0.45 * math.sin(17 * t + 6.28 * _hash(li, k, 43.1))
                a = (1 - age / 0.9) ** 1.5 * tw * A
                star = _hash(li, k, 44.9) < 0.35
                sc = 0.55 + 0.5 * _hash(li, k, 45.5)
                put(img, np.float32([1.0, 0.96, 0.9]) if star else GLOW, _STAR if star else _DOT,
                    xk + (_hash(li, k, 46) - 0.5) * 20 * age, yk + 24 * age, sc, sc, age * 3, a, add=True)
            if 0 < prog < 1:
                put(img, np.float32([1.0, 0.97, 0.92]), _STAR, head, L["base"] - L["size"] * 0.38, 1.5, 1.5, 3 * t, A, add=True)

    def draw(self, img, t, global_alpha=1.0):
        if not self.active(t):
            return
        if not hasattr(self, "_prepared"):
            counters = {}
            for g in self.glyphs:
                key = (g["line"], g["t_in"])
                g["order_in_line"] = counters.get(key, 0)
                counters[key] = g["order_in_line"] + 1
            self._prepared = True
        out = 1.0
        if self.fade_out > 0:
            out = 1 - EASE["inCubic"](clamp((t - (self.end - self.fade_out)) / self.fade_out))
        drift = -10 * (1 - out)
        states = [self._glyph_state(g, t) for g in self.glyphs]
        reveal = sum(s[0] for s in states) / max(1, len(states))
        A = out * global_alpha
        if A <= 0.002:
            return
        if self.scrim:
            sc = self.scrim
            blend(img, sc["x"], sc["y"], sc["col"], sc["a"] * min(1.0, reveal * 1.4) * A)
        shine_pos = None
        if self.cfg.get("shine") is not None:
            u = (t - (self.start + self.cfg["shine"])) / 1.0
            if 0 <= u <= 1:
                x0, _, x1, _ = self.bbox
                shine_pos = x0 - 160 + (x1 - x0 + 320) * EASE["inOutSine"](u)
        black = np.float32(rgb("black"))
        for g, (a, dy, dx) in zip(self.glyphs, states):
            a *= A
            if a <= 0.003:
                continue
            x = int(round(g["x"] + dx))
            y = int(round(g["y"] + dy + drift))
            if g["sp"]:
                blend(img, x - g["sp"], y - g["sp"], black, g["sh"] * ((0.48 if self.look else 0.62) * a))
            if g.get("gl") is not None:
                _add_glow(img, x - g["gp"], y - g["gp"], g["gl"], 0.45 * a)
            col = g["col"]
            if shine_pos is not None and col.ndim == 3:
                hh, ww = g["a"].shape
                X = np.arange(ww, dtype=np.float32)[None, :] + x
                Y = np.arange(hh, dtype=np.float32)[:, None] + y
                band = np.exp(-((X + 0.35 * (Y - y)) - shine_pos) ** 2 / (2 * 38.0 ** 2))[..., None]
                col = col + (SHINE - col) * band * 0.9
            blend(img, x, y, col, g["a"] * a)
        if self.heart:
            h = self.heart
            p = clamp((t - (self.start + 0.75)) / 0.5)
            if p > 0:
                pulse = 0.0
                for b in self.beats:
                    if 0 <= t - b < 0.35:
                        pulse = 0.09 * (1 - (t - b) / 0.35)
                sc = EASE["outBack"](p) * (1 + pulse)
                sz = max(4, int(h["size"] * sc))
                a = cv2.resize(h["a"], (sz, sz), interpolation=cv2.INTER_AREA)
                c = cv2.resize(h["col"], (sz, sz), interpolation=cv2.INTER_AREA)
                ox = h["x"] + (h["size"] - sz) // 2
                oy = int(h["y"] + (h["size"] - sz) // 2 + drift)
                glow = cv2.GaussianBlur(a, (0, 0), sz * 0.25)
                blend(img, ox, oy, np.float32([1.0, 0.85, 0.55]), glow * 0.35 * A * min(1, p * 2))
                blend(img, ox, oy, c, a * A * min(1, p * 2))
        if self.route:
            r = self.route
            p = EASE["inOutSine"](clamp((t - (self.start + 0.35)) / 1.5))
            if p > 0:
                head = int(r["n"] * p)
                a = r["a"][:, :max(head, 1)] * (0.9 * A)
                blend(img, r["x"], r["y"], np.float32(rgb("gold")), a)
                for ex in (0, head - 1):
                    yy = r["yline"][max(ex, 0)]
                    _dot(img, r["x"] + ex, yy, 7 if ex else 5, A)
        if self.sig:
            s = self.sig
            p = EASE["inOutSine"](clamp((t - self.start) / 0.9))
            blend(img, s["x"], s["y"], s["col"], s["a"] * p * A)
        if self.anim == "wand":
            self._glitter(img, t, A)


_STAR = _star(6.0)
_DOT = _dot(2.4)


def _add_glow(img, x, y, a, k):
    """Halo lumineux chaud autour des lettres (version rêve)."""
    h, w = a.shape
    H_, W_ = img.shape[:2]
    x0, y0, x1, y1 = max(0, x), max(0, y), min(W_, x + w), min(H_, y + h)
    if x1 <= x0 or y1 <= y0:
        return
    img[y0:y1, x0:x1] += a[y0 - y:y1 - y, x0 - x:x1 - x, None] * (GLOW * k)


def _dot(img, x, y, r, A):
    n = int(r * 6)
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32) - n / 2
    d = np.sqrt(xx ** 2 + yy ** 2)
    a = np.clip(r * 0.45 - d, 0, 1) + 0.5 * np.exp(-d ** 2 / (2 * (r * 0.9) ** 2))
    blend(img, int(x - n / 2), int(y - n / 2), np.float32([1.0, 0.93, 0.75]), np.clip(a, 0, 1) * A)
