"""Chargement des photos (EXIF, ICC -> sRGB), maîtres agrandis, fonds flous et cadrage caméra.

Principe : la photo n'est jamais déformée. Seuls l'échelle (uniforme) et la position changent.
Quand l'image ne couvre pas le cadre, une copie floutée et assombrie de la même photo remplit le fond,
avec des bords adoucis (pas de cadre visible).
"""
import io

import cv2
import numpy as np
from PIL import Image, ImageCms, ImageOps

from common import ROOT, clamp, rgb


def load_rgb(path):
    im = Image.open(path)
    im = ImageOps.exif_transpose(im)          # orientation EXIF corrigée avant tout traitement
    icc = im.info.get("icc_profile")
    if icc:
        try:
            src = ImageCms.ImageCmsProfile(io.BytesIO(icc))
            im = ImageCms.profileToProfile(im.convert("RGB"), src, ImageCms.createProfile("sRGB"), outputMode="RGB")
        except Exception:
            pass
    return np.ascontiguousarray(np.asarray(im.convert("RGB")))


def place(w, h, cw, ch, zoom, center, anchor=(0.5, 0.5)):
    """Échelle et translation (canevas = source * s + t). zoom relatif au cadrage plein cadre."""
    s = zoom * max(cw / w, ch / h)
    dw, dh = w * s, h * s
    cx, cy = center
    ax, ay = anchor
    if dw >= cw - 0.5:   # l'image couvre en largeur : pas de bord visible
        cx = clamp(cx, ax * cw / dw, 1 - (1 - ax) * cw / dw)
    if dh >= ch - 0.5:
        cy = clamp(cy, ay * ch / dh, 1 - (1 - ay) * ch / dh)
    return s, ax * cw - cx * dw, ay * ch - cy * dh, dw, dh


def _ramp(n, lo, hi, feather):
    """Masque 1D adouci : 0 hors de [lo, hi]. Le fondu grandit avec la distance du bord à l'intérieur
    du cadre, pour qu'aucun saut n'apparaisse quand un bord de l'image entre dans le champ."""
    x = np.arange(n, dtype=np.float32) + 0.5
    m = np.ones(n, np.float32)
    if lo > 0:
        f = min(feather, 1.0 + lo)
        m *= np.clip((x - lo) / f, 0, 1)
    if hi < n:
        f = min(feather, 1.0 + (n - hi))
        m *= np.clip((hi - x) / f, 0, 1)
    return m * m * (3 - 2 * m)


class Photo:
    def __init__(self, pid, cfg, max_scale):
        self.id = pid
        self.cfg = cfg
        self.src = load_rgb(ROOT / cfg["file"])
        self.h, self.w = self.src.shape[:2]
        self.focus = cfg.get("focus", [0.5, 0.5])
        self.protect = cfg.get("protect", {})
        k = clamp(max_scale * 1.02, 1.0, 3.2)
        if k > 1.05:
            m = cv2.resize(self.src, (round(self.w * k), round(self.h * k)), interpolation=cv2.INTER_LANCZOS4)
            # accentuation douce après agrandissement (texture de peau préservée)
            f = m.astype(np.float32)
            blur = cv2.GaussianBlur(f, (0, 0), 0.9 * k)
            m = np.clip(f + 0.32 * (f - blur), 0, 255).astype(np.uint8)
        else:
            k, m = 1.0, self.src
        self.levels = [(k, m)]
        while self.levels[-1][0] > 0.3:
            pk, pm = self.levels[-1]
            self.levels.append((pk / 2, cv2.resize(pm, (pm.shape[1] // 2, pm.shape[0] // 2), interpolation=cv2.INTER_AREA)))

    def level_for(self, s):
        best = self.levels[0]
        for lk, lm in self.levels:
            if lk >= s:
                best = (lk, lm)
        return best

    def background(self, cw, ch, s, tx, ty, tint=None):
        """Fond de remplissage : prolongement flouté des bords de la photo (pas de visage « fantôme »),
        qui s'assombrit vers le bleu nuit en s'éloignant de l'image."""
        q = 8
        lk, lm = self.level_for(s / q)
        r = s / q / lk
        sw, sh = max(cw // q, 8), max(ch // q, 8)
        A = np.float32([[r, 0, tx / q], [0, r, ty / q]])
        b = cv2.warpAffine(lm, A, (sw, sh), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        b = cv2.GaussianBlur(b.astype(np.float32) / 255, (0, 0), 9)
        lum = b @ np.float32([0.2126, 0.7152, 0.0722])
        b = lum[..., None] + 0.8 * (b - lum[..., None])
        # distance au bord de l'image (en pixels du canevas) -> assombrissement progressif
        yy, xx = np.mgrid[0:sh, 0:sw].astype(np.float32) * q
        dx = np.maximum(np.maximum(tx - xx, xx - (tx + self.w * s)), 0)
        dy = np.maximum(np.maximum(ty - yy, yy - (ty + self.h * s)), 0)
        d = np.sqrt(dx * dx + dy * dy)
        k = np.clip(d / 520.0, 0, 1)[..., None]
        base = np.float32(rgb("mint") if tint == "mint" else rgb("night"))
        dark = base * (0.30 if tint == "mint" else 0.55)
        b = b * (0.80 - 0.25 * k) * (1 - 0.55 * k) + dark * (0.55 * k) + base * 0.05
        return cv2.resize(b, (cw, ch), interpolation=cv2.INTER_CUBIC)

    def render(self, cw, ch, zoom, center, anchor=(0.5, 0.5), tint=None):
        """Retourne (image uint8 HxWx3, transformation (s, tx, ty)) pour un canevas cw x ch."""
        s, tx, ty, dw, dh = place(self.w, self.h, cw, ch, zoom, center, anchor)
        lk, lm = self.level_for(s)
        r = s / lk
        A = np.float32([[r, 0, tx + 0.5 * r - 0.5], [0, r, ty + 0.5 * r - 0.5]])
        fg = cv2.warpAffine(lm, A, (cw, ch), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
        covers = tx <= 0 and ty <= 0 and tx + dw >= cw and ty + dh >= ch
        if not covers:
            feather = clamp(0.10 * min(dw, dh), 40, 150)
            ax = _ramp(cw, tx, tx + dw, feather)
            ay = _ramp(ch, ty, ty + dh, feather)
            a = (ay[:, None] * ax[None, :])[..., None]
            bg = self.background(cw, ch, s, tx, ty, tint) * 255
            fg = np.clip(bg + (fg.astype(np.float32) - bg) * a, 0, 255).astype(np.uint8)
        return fg, (s, tx, ty)

    def protected_boxes(self, transform, offset=(0, 0)):
        """Zones protégées projetées dans le cadre (pixels)."""
        s, tx, ty = transform
        ox, oy = offset
        out = {}
        for name, (x0, y0, x1, y1) in self.protect.items():
            out[name] = (x0 * self.w * s + tx + ox, y0 * self.h * s + ty + oy,
                         x1 * self.w * s + tx + ox, y1 * self.h * s + ty + oy)
        return out
