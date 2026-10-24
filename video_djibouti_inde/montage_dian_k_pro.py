#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
montage_dian_k_pro.py
=====================
Habillage « campagne de luxe » d'une vidéo client — Coopération Djibouti x Inde.
Signature finale : Dian K. Pro.

Architecture hybride (pensée pour une vidéo de 56 s comme de 56 min) :
  1. MoviePy  -> page de garde et outro animées
                 (VideoClip, ImageClip, ColorClip, CompositeVideoClip, vfx).
  2. FFmpeg   -> corps de la vidéo traité en flux continu (étalonnage, netteté,
                 drapeaux, fondus), puis assemblage page de garde + vidéo + outro
                 en UN SEUL encodage H.264. Mémoire constante quelle que soit la durée.

Usage (dans le dossier qui contient la vidéo et les drapeaux) :
    python montage_dian_k_pro.py                 # rendu complet
    python montage_dian_k_pro.py --preview 20    # aperçu rapide (20 premières secondes)
    python montage_dian_k_pro.py --format 16:9   # version projection / comité de pilotage
    python montage_dian_k_pro.py --help          # toutes les options
"""
from __future__ import annotations

import argparse
import math
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

try:
    import numpy as np
    from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps
    from moviepy import ColorClip, CompositeVideoClip, ImageClip, VideoClip, vfx
    from moviepy.video.io.ffmpeg_reader import ffmpeg_parse_infos
except ImportError as exc:  # MoviePy 1.x ou dépendance absente
    sys.exit(
        f"Dépendance manquante ou trop ancienne : {exc}\n"
        "Installez-les avec :  python -m pip install -r requirements.txt   (MoviePy >= 2.1)"
    )

# --------------------------------------------------------------------------------------
# Charte Dian K. Pro
# --------------------------------------------------------------------------------------
BLACK = (11, 11, 12)      # #0B0B0C
GOLD = (227, 179, 76)     # #E3B34C
IVORY = (246, 241, 232)   # #F6F1E8 — blanc chaud, contraste > 15:1 sur le noir de la charte
FADE_COLOR = "0x0B0B0C"

SCRIPT_DIR = Path(__file__).resolve().parent

# Textes à l'écran (en anglais, comme la vidéo) — modifiables en ligne de commande
DEFAULT_KICKER = "DJIBOUTI · INDIA COOPERATION"
DEFAULT_TITLE = "Two Shores, One Ocean"
DEFAULT_SUBTITLE = "Voices of a shared future"
DEFAULT_SIGNATURE = "Dian K. Pro"
DEFAULT_TAGLINE = "PUBLIC HEALTH & DIGITAL STRATEGIST"

# Étalonnage 100 % YUV (aucun aller-retour RGB : 3x plus rapide, couleurs exactes) :
#   eq           -> luminosité, contraste, saturation
#   colorcorrect -> ombres légèrement teal, hautes lumières chaudes (neutralise aussi
#                   les dominantes vertes des téléphones : mur blanc -> ivoire chaud)
#   glow         -> diffusion lumineuse type filtre « Pro-Mist » sur les hautes lumières
GRADES = {
    "luxe": {
        "eq": "eq=brightness=0.015:contrast=1.05:saturation=1.08",
        "cc": "colorcorrect=rl=-0.02:bl=0.025:rh=0.05:bh=-0.02",
        "glow": 0.14,
    },
    "subtil": {
        "eq": "eq=brightness=0.01:contrast=1.03:saturation=1.05",
        "cc": "colorcorrect=rl=-0.01:bl=0.015:rh=0.03:bh=-0.01",
        "glow": 0.08,
    },
    "aucun": {"eq": "", "cc": "", "glow": 0.0},
}

FONT_FILES = {
    "serif": ["PlayfairDisplay[wght].ttf", "PlayfairDisplay-VariableFont_wght.ttf",
              "PlayfairDisplay-Regular.ttf"],
    "serif-italic": ["PlayfairDisplay-Italic[wght].ttf",
                     "PlayfairDisplay-Italic-VariableFont_wght.ttf", "PlayfairDisplay-Italic.ttf"],
    "sans": ["Inter[opsz,wght].ttf", "Inter-VariableFont_opsz,wght.ttf", "Inter-Regular.ttf"],
}
FONT_URLS = {
    "serif": "https://raw.githubusercontent.com/google/fonts/main/ofl/playfairdisplay/"
             "PlayfairDisplay%5Bwght%5D.ttf",
    "serif-italic": "https://raw.githubusercontent.com/google/fonts/main/ofl/playfairdisplay/"
                    "PlayfairDisplay-Italic%5Bwght%5D.ttf",
    "sans": "https://raw.githubusercontent.com/google/fonts/main/ofl/inter/Inter%5Bopsz,wght%5D.ttf",
}
FONT_FALLBACKS = {
    "serif": ["georgia.ttf", "Georgia.ttf", "times.ttf", "Times New Roman.ttf",
              "DejaVuSerif.ttf", "LiberationSerif-Regular.ttf"],
    "serif-italic": ["georgiai.ttf", "Georgia Italic.ttf", "timesi.ttf",
                     "DejaVuSerif-Italic.ttf", "LiberationSerif-Italic.ttf"],
    "sans": ["arial.ttf", "Arial.ttf", "Helvetica.ttc", "DejaVuSans.ttf",
             "LiberationSans-Regular.ttf"],
}


def log(msg: str = "") -> None:
    print(msg, flush=True)


# --------------------------------------------------------------------------------------
# Fichiers, FFmpeg, analyse de la source
# --------------------------------------------------------------------------------------
def find_file(name: str, required: bool = True) -> Path | None:
    """Cherche `name` tel quel, puis dans le dossier du script, en tolérant l'extension
    (drapeau_inde.jpg au lieu de .png, video_client.mov au lieu de .mp4...)."""
    p = Path(name)
    candidates = [p] if p.is_absolute() else [Path.cwd() / p, SCRIPT_DIR / p]
    for c in candidates:
        if c.is_file():
            return c
    exts = [".png", ".jpg", ".jpeg", ".webp", ".mp4", ".mov", ".m4v", ".mkv",
            ".mp3", ".wav", ".m4a"]
    for c in candidates:
        for ext in exts:
            alt = c.with_suffix(ext)
            if alt.is_file():
                return alt
    if required:
        where = " et ".join(dict.fromkeys(str(d) for d in (Path.cwd(), SCRIPT_DIR)))
        sys.exit(f"Fichier introuvable : « {name} » (cherché dans {where}).")
    return None


def ffmpeg_exe() -> str:
    """FFmpeg fourni par imageio-ffmpeg (installé avec MoviePy), sinon celui du système."""
    try:
        import imageio_ffmpeg
        exe = imageio_ffmpeg.get_ffmpeg_exe()
        if exe and Path(exe).exists():
            return exe
    except Exception:
        pass
    exe = shutil.which("ffmpeg")
    if not exe:
        sys.exit("FFmpeg introuvable. Réinstallez MoviePy (pip install moviepy) ou installez FFmpeg.")
    return exe


STANDARD_FPS = [(24000, 1001), (24, 1), (25, 1), (30000, 1001), (30, 1),
                (50, 1), (60000, 1001), (60, 1)]


def pick_fps(fps: float | None) -> tuple[int, int]:
    """Cadence de sortie : la cadence source si elle est standard, sinon 30 i/s
    (cas des vidéos de smartphone / WhatsApp à cadence variable)."""
    if fps:
        for n, d in STANDARD_FPS:
            if abs(fps - n / d) / (n / d) < 0.006:
                return n, d
    return 30, 1


def probe(path: Path) -> dict:
    info = ffmpeg_parse_infos(str(path))
    if not info.get("video_found"):
        sys.exit(f"Aucune piste vidéo lisible dans {path}.")
    w, h = info["video_size"]
    if abs(int(info.get("video_rotation", 0) or 0)) % 180 == 90:  # vidéo de téléphone pivotée
        w, h = h, w
    duration = float(info.get("video_duration") or info.get("duration") or 0)
    if duration <= 0:
        sys.exit("Durée de la vidéo illisible : le fichier est peut-être incomplet ou corrompu.")
    return {"w": w, "h": h, "duration": duration, "fps": info.get("video_fps"),
            "audio": bool(info.get("audio_found"))}


# --------------------------------------------------------------------------------------
# Typographie (Pillow) : Playfair Display + Inter, avec interlettrage
# --------------------------------------------------------------------------------------
_font_paths: dict[str, str] = {}


def font_path(kind: str) -> str:
    if kind in _font_paths:
        return _font_paths[kind]
    dirs = [SCRIPT_DIR / "fonts", Path.cwd() / "fonts"]
    for d in dirs:
        for name in FONT_FILES[kind]:
            if (d / name).is_file():
                _font_paths[kind] = str(d / name)
                return _font_paths[kind]
    target = SCRIPT_DIR / "fonts" / FONT_FILES[kind][0]
    try:  # téléchargement unique depuis Google Fonts (licence OFL)
        target.parent.mkdir(exist_ok=True)
        log(f"  - Téléchargement de la police {target.name}...")
        with urllib.request.urlopen(FONT_URLS[kind], timeout=30) as r:
            target.write_bytes(r.read())
        _font_paths[kind] = str(target)
        return _font_paths[kind]
    except Exception:
        pass
    for name in FONT_FALLBACKS[kind]:
        try:
            ImageFont.truetype(name, 20)
            log(f"  ! Police de la charte absente : repli sur {name}.")
            _font_paths[kind] = name
            return name
        except OSError:
            continue
    log("  ! Aucune police TrueType trouvée : police par défaut de Pillow (rendu dégradé).")
    _font_paths[kind] = ""
    return ""


def get_font(kind: str, size: int, weight: int = 400, opsz: float | None = None):
    path = font_path(kind)
    if not path:
        return ImageFont.load_default(size)
    font = ImageFont.truetype(path, size)
    try:  # polices variables : graisse et taille optique
        values = []
        for axis in font.get_variation_axes():
            name = axis["name"].decode() if isinstance(axis["name"], bytes) else str(axis["name"])
            if name.lower().startswith("weight"):
                v = weight
            elif name.lower().startswith("optical"):
                v = opsz if opsz is not None else axis["default"]
            else:
                v = axis["default"]
            values.append(min(max(v, axis["minimum"]), axis["maximum"]))
        font.set_variation_by_axes(values)
    except Exception:
        pass  # police statique : on garde sa graisse
    return font


def _line_width(line: str, font, tracking_px: float) -> float:
    if not tracking_px:
        return font.getlength(line)
    return sum(font.getlength(c) for c in line) + tracking_px * max(len(line) - 1, 0)


def wrap(text: str, font, max_w: float, tracking: float = 0.0) -> str:
    """Retour à la ligne automatique (sauf si le texte contient déjà '\\n' ou '|')."""
    text = text.replace("|", "\n")
    if "\n" in text or _line_width(text, font, tracking * font.size) <= max_w:
        return text
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if cur and _line_width(trial, font, tracking * font.size) > max_w:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    lines.append(cur)
    return "\n".join(lines)


def text_image(text: str, font, fill, tracking: float = 0.0, line_height: float = 1.08) -> Image.Image:
    """Texte -> image RGBA recadrée sur l'encre, lignes centrées.
    `tracking` est exprimé en fraction du corps (0.2 = interlettrage de 20 %)."""
    lines = text.split("\n")
    tpx = tracking * font.size
    asc, desc = font.getmetrics()
    lh = font.size * line_height
    widths = [_line_width(line, font, tpx) for line in lines]
    cw = int(max(widths) + 4 * font.size)
    ch = int(asc + desc + lh * (len(lines) - 1) + 4 * font.size)
    img = Image.new("RGBA", (cw, ch), tuple(fill) + (0,))  # fond transparent de la couleur du texte
    draw = ImageDraw.Draw(img)
    for i, line in enumerate(lines):
        x = (cw - widths[i]) / 2
        y = 2 * font.size + asc + i * lh
        if not tpx:
            draw.text((x, y), line, font=font, fill=tuple(fill) + (255,), anchor="ls")
        else:
            for c in line:
                draw.text((x, y), c, font=font, fill=tuple(fill) + (255,), anchor="ls")
                x += font.getlength(c) + tpx
    bbox = img.getchannel("A").getbbox()
    return img.crop(bbox) if bbox else img


def hairline(width: int, thickness: int, color=GOLD) -> Image.Image:
    """Filet doré aux extrémités adoucies."""
    a = np.zeros((thickness, width), np.float32) + 1.0
    ramp = np.clip(np.minimum(np.arange(width), np.arange(width)[::-1]) / max(width * 0.18, 1), 0, 1)
    a *= ramp[None, :]
    img = Image.new("RGBA", (width, thickness), tuple(color) + (0,))
    img.putalpha(Image.fromarray((a * 255).astype(np.uint8)))
    return img


# --------------------------------------------------------------------------------------
# Drapeaux : détection de l'emblème, panneaux, médaillons
# --------------------------------------------------------------------------------------
def load_flag(path: Path) -> Image.Image:
    return ImageOps.exif_transpose(Image.open(path)).convert("RGB")


def emblem_center(img: Image.Image, kind: str) -> tuple[float, float]:
    """Position (fractions) de l'étoile rouge (Djibouti) ou de l'Ashoka Chakra (Inde)."""
    small = img.resize((240, max(1, round(240 * img.height / img.width))))
    a = np.asarray(small).astype(np.int16)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    if kind == "dj":
        m = (r > 150) & (g < 100) & (b < 100)
        default = (0.22, 0.45)
    else:
        m = (b > r + 15) & (b > g + 5) & (r < 130) & (b < 200)
        default = (0.50, 0.50)
    if m.sum() < 20:
        return default
    ys, xs = np.nonzero(m)
    return float(xs.mean() / small.width), float(ys.mean() / small.height)


def flag_panel(img: Image.Image, focus, w: int, h: int, target, zoom: float = 1.0) -> Image.Image:
    """Remplit w x h avec le drapeau en plaçant l'emblème `focus` au point `target`
    (fractions du panneau), dans la limite de l'image. Jamais de miroir (protocole)."""
    s = max(w / img.width, h / img.height) * zoom
    sw, sh = img.width * s, img.height * s
    x0 = min(max(focus[0] * sw - target[0] * w, 0), sw - w)
    y0 = min(max(focus[1] * sh - target[1] * h, 0), sh - h)
    big = img.resize((max(w, round(sw)), max(h, round(sh))), Image.LANCZOS)
    return big.crop((round(x0), round(y0), round(x0) + w, round(y0) + h))


def smoothstep(x):
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3 - 2 * x)


def diptych(dj, ind, fdj, fin, W: int, H: int, portrait: bool) -> np.ndarray:
    """Diptyque Djibouti | Inde avec raccord fondu au centre (les bandes vertes se rejoignent).
    En 9:16, les drapeaux occupent les 70 % supérieurs puis plongent dans le noir de la charte :
    étoile et chakra restent entiers, le texte repose sur un fond sombre."""
    fh = round(0.70 * H) if portrait else H
    F = int(0.06 * W)
    half = W // 2
    ty = 0.5 if portrait else 0.33
    left = np.asarray(flag_panel(dj, fdj, half + F, fh, (0.38, ty)), np.float32)
    right = np.asarray(flag_panel(ind, fin, W - half + F, fh, (0.55 if portrait else 0.5, ty)),
                       np.float32)
    L = np.zeros((fh, W, 3), np.float32)
    R = np.zeros((fh, W, 3), np.float32)
    L[:, : half + F] = left
    R[:, half - F:] = right
    alpha = smoothstep((np.arange(W) - (half - F)) / (2 * F))[None, :, None]
    out = np.zeros((H, W, 3), np.float32) + np.array(BLACK, np.float32)
    out[:fh] = L * (1 - alpha) + R * alpha
    return out


def medallion(img: Image.Image, center, radius_frac: float, d: int) -> Image.Image:
    """Médaillon circulaire du drapeau cerclé d'or (sur-échantillonné x4)."""
    D = d * 4
    r = radius_frac * img.width
    cx = min(max(center[0] * img.width, r), img.width - r)
    cy = min(max(center[1] * img.height, r), img.height - r)
    disc = img.crop((round(cx - r), round(cy - r), round(cx + r), round(cy + r)))
    disc = disc.resize((D, D), Image.LANCZOS).convert("RGBA")
    mask = Image.new("L", (D, D), 0)
    ImageDraw.Draw(mask).ellipse((2, 2, D - 3, D - 3), fill=255)
    disc.putalpha(mask)
    ring = Image.new("RGBA", (D, D), GOLD + (0,))
    ImageDraw.Draw(ring).ellipse((2, 2, D - 3, D - 3), outline=GOLD + (255,),
                                 width=max(6, round(0.06 * D)))
    return Image.alpha_composite(disc, ring).resize((d, d), Image.LANCZOS)


def build_emblem(dj, ind, fdj, fin, d: int) -> Image.Image:
    """Deux médaillons qui se chevauchent : symbole sobre du partenariat."""
    m_dj = medallion(dj, (fdj[0] + 0.19, fdj[1]), 0.33, d)  # étoile + bandes bleue et verte
    m_in = medallion(ind, fin, 0.42, d)
    step = round(d * 0.74)
    pad = round(d * 0.16)
    W, H = d + step + 2 * pad, d + 2 * pad
    art = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    art.alpha_composite(m_in, (pad + step, pad))
    art.alpha_composite(m_dj, (pad, pad))
    shadow_a = art.getchannel("A").filter(ImageFilter.GaussianBlur(d * 0.07))
    shadow_a = shadow_a.point(lambda v: int(v * 0.55))
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shadow.putalpha(shadow_a)
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    out.alpha_composite(shadow, (0, max(1, round(d * 0.04))))
    out.alpha_composite(art)
    return out


def build_backdrop(dj, ind, fdj, fin, W: int, H: int, vw: int, vh: int) -> Image.Image:
    """Fond pour une vidéo qui ne remplit pas le cadre (ex. portrait en 16:9) :
    les deux drapeaux en panneaux latéraux, assombris, avec ombre portée et filet doré."""
    canvas = np.zeros((H, W, 3), np.float32) + np.array(BLACK, np.float32)
    x0, y0 = (W - vw) // 2, (H - vh) // 2
    if W * vh > H * vw:  # panneaux gauche / droite
        pw = x0 + 60
        canvas[:, :pw] = np.asarray(flag_panel(dj, fdj, pw, H, (0.42, 0.45)), np.float32)
        canvas[:, W - pw:] = np.asarray(flag_panel(ind, fin, pw, H, (0.5, 0.45)), np.float32)
    else:  # panneaux haut / bas
        ph = y0 + 60
        canvas[:ph] = np.asarray(flag_panel(dj, fdj, W, ph, (0.4, 0.5)), np.float32)
        canvas[H - ph:] = np.asarray(flag_panel(ind, fin, W, ph, (0.5, 0.5)), np.float32)
    # flou de profondeur de champ + voile : les drapeaux restent un décor, pas un sujet
    soft = Image.fromarray(np.clip(canvas, 0, 255).astype(np.uint8))
    canvas = np.asarray(soft.filter(ImageFilter.GaussianBlur(0.004 * max(W, H))), np.float32)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    vig = 1 - 0.35 * (((xx / W - 0.5) * 2) ** 2 + ((yy / H - 0.5) * 2) ** 2) / 2
    canvas *= 0.50 * vig[..., None]
    img = Image.fromarray(np.clip(canvas, 0, 255).astype(np.uint8)).convert("RGBA")
    sh = Image.new("L", (W, H), 0)
    ImageDraw.Draw(sh).rectangle((x0 - 6, y0 - 6, x0 + vw + 6, y0 + vh + 6), fill=210)
    sh = sh.filter(ImageFilter.GaussianBlur(28))
    shadow = Image.new("RGBA", (W, H), BLACK + (0,))
    shadow.putalpha(sh)
    img.alpha_composite(shadow)
    ImageDraw.Draw(img).rectangle((x0 - 3, y0 - 3, x0 + vw + 2, y0 + vh + 2),
                                  outline=GOLD + (230,), width=2)
    return img.convert("RGB")


# --------------------------------------------------------------------------------------
# Calques animés MoviePy (mouvements sous-pixel, sans saccade)
# --------------------------------------------------------------------------------------
def ease(x: float) -> float:
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3  # ease-out cubique


def anim_layer(rgba: Image.Image, center_xy, duration: float, t_in: float, d_in: float,
               rise: float = 0.0, zoom_from: float = 1.0, shine: tuple | None = None) -> VideoClip:
    """Calque RGBA qui apparaît en fondu (t_in, d_in), avec montée et zoom doux,
    et éventuellement un reflet lumineux (shine=(t_debut, durée))."""
    w, h = rgba.size
    pad = int(abs(rise) + 0.08 * max(w, h)) + 4
    cw, ch = w + 2 * pad, h + 2 * pad
    yy, xx = np.mgrid[0:ch, 0:cw].astype(np.float32)
    diag = (xx + 0.45 * yy) / (cw + 0.45 * ch)
    cache: dict = {}

    def render(t: float):
        if cache.get("t") == t:
            return cache["v"]
        p = ease((t - t_in) / d_in) if d_in > 0 else 1.0
        s = zoom_from + (1 - zoom_from) * p
        dy = rise * (1 - p)
        data = (1 / s, 0, w / 2 - (cw / 2) / s, 0, 1 / s, h / 2 - (ch / 2 + dy) / s)
        out = np.asarray(rgba.transform((cw, ch), Image.AFFINE, data, resample=Image.BICUBIC),
                         np.float32)
        rgb, alpha = out[..., :3], out[..., 3] / 255.0
        if shine is not None and shine[0] <= t <= shine[0] + shine[1]:
            c = -0.25 + 1.5 * (t - shine[0]) / shine[1]
            band = np.exp(-(((diag - c) / 0.06) ** 2))[..., None]
            rgb = rgb + band * (255 - rgb) * 0.7
        op = min(max((t - t_in) / d_in, 0.0), 1.0) if d_in > 0 else 1.0
        cache["t"], cache["v"] = t, (rgb.astype(np.uint8), alpha * op)
        return cache["v"]

    clip = VideoClip(frame_function=lambda t: render(t)[0], duration=duration)
    mask = VideoClip(frame_function=lambda t: render(t)[1], is_mask=True, duration=duration)
    return clip.with_mask(mask).with_position((round(center_xy[0] - cw / 2),
                                               round(center_xy[1] - ch / 2)))


def drawn_line(width: int, thickness: int, center_xy, duration: float, t_in: float,
               d_in: float) -> VideoClip:
    """Filet doré qui se dessine depuis le centre."""
    xs = np.abs(np.arange(width, dtype=np.float32) - (width - 1) / 2)
    ramp = np.clip((width / 2 - xs) / (width * 0.12), 0, 1)
    rgb = np.zeros((thickness, width, 3), np.uint8) + np.array(GOLD, np.uint8)

    def mask_at(t):
        half = ease((t - t_in) / d_in) * width / 2
        a = np.clip(half - xs + 0.5, 0, 1) * ramp
        return np.repeat(a[None, :], thickness, axis=0)

    clip = VideoClip(frame_function=lambda t: rgb, duration=duration)
    mask = VideoClip(frame_function=mask_at, is_mask=True, duration=duration)
    return clip.with_mask(mask).with_position((round(center_xy[0] - width / 2),
                                               round(center_xy[1] - thickness / 2)))


def ken_burns_with_sheen(bg: np.ndarray, W: int, H: int, duration: float,
                         zoom: float = 0.05) -> VideoClip:
    """Fond en lente poussée (sous-pixel) + reflet satiné qui traverse l'image."""
    src = Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8))
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    diag = (xx / W + 0.35 * yy / H) / 1.35

    def frame(t):
        s = 1 + zoom * ease(t / duration * 0.9)
        data = (1 / s, 0, W / 2 - (W / 2) / s, 0, 1 / s, H / 2 - (H / 2) / s)
        f = np.asarray(src.transform((W, H), Image.AFFINE, data, resample=Image.BICUBIC),
                       np.float32)
        c = -0.3 + 1.9 * min(max((t - 0.5) / 3.2, 0.0), 1.0)  # invisible à t=0 (vignette propre)
        band = np.exp(-(((diag - c) / 0.11) ** 2))[..., None]
        f = f + band * (255 - f) * 0.16
        return np.clip(f, 0, 255).astype(np.uint8)

    return VideoClip(frame_function=frame, duration=duration)


def vertical_gradient(W: int, H: int, y_start: int, y_full: int, max_alpha: float) -> ImageClip:
    """Dégradé localisé (noir de la charte) derrière le texte — pas de voile global."""
    a = np.zeros((H, W), np.float32)
    ramp = smoothstep((np.arange(H) - y_start) / max(y_full - y_start, 1)) * max_alpha
    a[:] = ramp[:, None]
    rgba = np.zeros((H, W, 4), np.uint8)
    rgba[..., :3] = BLACK
    rgba[..., 3] = (a * 255).astype(np.uint8)
    return ImageClip(rgba)


# --------------------------------------------------------------------------------------
# Page de garde et outro
# --------------------------------------------------------------------------------------
def make_cover(args, dj, ind, fdj, fin, W, H, portrait) -> CompositeVideoClip:
    D = args.cover_seconds
    bg = ken_burns_with_sheen(diptych(dj, ind, fdj, fin, W, H, portrait), W, H, D)
    k = 1.0 if portrait else 0.96
    f_kicker = get_font("sans", round(34 * k), 600, opsz=20)
    f_title = get_font("serif", round((128 if portrait else 118) * k), 500)
    f_sub = get_font("serif-italic", round((48 if portrait else 46) * k), 400)

    title = args.title
    if portrait and "|" not in title and "\n" not in title:
        title = title.replace(", ", ",\n")  # « Two Shores, / One Ocean » sur deux lignes en 9:16
    title = wrap(title, f_title, 0.86 * W)
    kicker = text_image(args.kicker, f_kicker, GOLD, tracking=0.24)
    title_img = text_image(title, f_title, IVORY, line_height=1.06)
    sub = text_image(wrap(args.subtitle, f_sub, 0.86 * W), f_sub, IVORY)
    rule = hairline(round(W * (0.16 if portrait else 0.09)), 3)

    gaps = [round(H * g) for g in ((0.020, 0.030, 0.026) if portrait else (0.030, 0.042, 0.036))]
    block_h = kicker.height + gaps[0] + title_img.height + gaps[1] + rule.height + gaps[2] + sub.height
    bottom = round(H * 0.83) if portrait else round(H * 0.915)  # zone sûre 9:16 : y <= 1600
    y = bottom - block_h
    if portrait:  # drapeaux -> noir de la charte, sous les emblèmes
        grad = vertical_gradient(W, H, round(H * 0.50), round(H * 0.70), 1.0)
    else:
        grad = vertical_gradient(W, H, y - round(H * 0.30), y + round(H * 0.06), 0.86)
    grad = grad.with_duration(D)
    layers = [bg, grad]
    for img in (kicker, title_img, rule, sub):
        layers.append(ImageClip(np.asarray(img)).with_duration(D)
                      .with_position(((W - img.width) // 2, y)))
        y += img.height + (gaps.pop(0) if gaps else 0)
    cover = CompositeVideoClip(layers, size=(W, H), bg_color=BLACK).with_duration(D)
    return cover.with_effects([vfx.FadeOut(0.6, final_color=list(BLACK))])


def make_outro(args, W, H, portrait) -> CompositeVideoClip:
    D = args.outro_seconds
    sig = text_image(args.signature, get_font("serif", 132 if portrait else 124, 500),
                     GOLD, tracking=0.02)
    f_tag = get_font("sans", 32, 500, opsz=20)
    tag = text_image(wrap(args.tagline, f_tag, 0.9 * W, 0.26), f_tag, IVORY, tracking=0.26,
                     line_height=1.5)
    logo_path = find_file(args.logo, required=False) if args.logo else None
    mono = None
    if logo_path:
        mono = ImageOps.exif_transpose(Image.open(logo_path)).convert("RGBA")
        mh = round(H * (0.15 if portrait else 0.24))
        mono = mono.resize((round(mono.width * mh / mono.height), mh), Image.LANCZOS)
    line_w = round(W * (0.40 if portrait else 0.24))
    g1, g2, g3 = round(H * 0.035), round(H * 0.026), round(H * 0.024)
    block = (mono.height + g1 if mono else 0) + sig.height + g2 + 3 + g3 + tag.height
    y = round(H * 0.48 - block / 2)
    cx = W / 2
    layers = [ColorClip((W, H), color=BLACK).with_duration(D)]
    if mono:
        layers.append(anim_layer(mono, (cx, y + mono.height / 2), D, 0.25, 1.1, zoom_from=0.94))
        y += mono.height + g1
    layers.append(anim_layer(sig, (cx, y + sig.height / 2), D, 0.85 if mono else 0.35, 1.1,
                             rise=18, shine=(2.3, 1.0)))
    y += sig.height + g2
    layers.append(drawn_line(line_w, 3, (cx, y + 1.5), D, 1.5, 0.8))
    y += 3 + g3
    layers.append(anim_layer(tag, (cx, y + tag.height / 2), D, 1.9, 0.8))
    outro = CompositeVideoClip(layers, size=(W, H), bg_color=BLACK).with_duration(D)
    return outro.with_effects([vfx.FadeOut(0.9, final_color=list(BLACK))])


def write_segment(clip, path: Path, fps: float) -> None:
    """Intermédiaire très haute qualité, encodé en BT.709 comme le corps de la vidéo."""
    clip.write_videofile(
        str(path), fps=fps, codec="libx264", audio=False, preset="medium", logger=None,
        ffmpeg_params=["-crf", "12", "-vf", "scale=out_color_matrix=bt709:out_range=tv",
                       "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709"],
    )


# --------------------------------------------------------------------------------------
# Graphe FFmpeg : corps de la vidéo + assemblage final
# --------------------------------------------------------------------------------------
def even(x: float) -> int:
    return max(2, int(round(x / 2)) * 2)


def build_ffmpeg(args, ff, src, info, D, fps, W, H, fill, cover_p, outro_p, emblem_p,
                 emblem_xy, backdrop_p, music_p, out_tmp):
    fps_s = f"{fps[0]}/{fps[1]}"
    grade = GRADES[args.grade]
    glow = grade["glow"] if args.glow is None else args.glow
    Dc, Do = args.cover_seconds, args.outro_seconds
    vf = min(args.fade, D / 3)
    af = min(args.audio_fade, D / 3)

    cmd = [ff, "-hide_banner", "-y", "-i", str(cover_p)]
    if args.preview:
        cmd += ["-t", f"{D:.3f}"]
    cmd += ["-i", str(src), "-i", str(outro_p)]
    idx = 3
    i_emb = i_bd = i_mus = None
    if emblem_p:
        cmd += ["-loop", "1", "-framerate", fps_s, "-t", f"{D:.3f}", "-i", str(emblem_p)]
        i_emb, idx = idx, idx + 1
    if backdrop_p:
        cmd += ["-loop", "1", "-framerate", fps_s, "-t", f"{D:.3f}", "-i", str(backdrop_p)]
        i_bd, idx = idx, idx + 1
    if music_p:
        cmd += ["-i", str(music_p)]
        i_mus, idx = idx, idx + 1

    sw, sh = info["w"], info["h"]
    s = max(W / sw, H / sh) if fill else min(W / sw, H / sh)
    tw, th = even(sw * s), even(sh * s)
    if fill:
        tw, th = max(tw, W), max(th, H)

    g = []
    # 1) Corps : cadence constante, débruitage léger (seulement si la source sera agrandie :
    #    on évite d'amplifier les blocs de compression), mise à l'échelle Lanczos en BT.709
    denoise = "hqdn3d=1.5:1.5:3:3," if min(sw, sh) < 1000 else ""
    chain = (f"[1:v]setpts=PTS-STARTPTS,fps={fps_s},{denoise}"
             f"scale={tw}:{th}:flags=lanczos+accurate_rnd+full_chroma_int"
             f":out_color_matrix=bt709:out_range=tv")
    if fill:
        chain += f",crop={W}:{H}"
    chain += ",setsar=1,format=yuv420p"
    # 2) Étalonnage teal / or, entièrement en YUV
    for f in (grade["eq"], grade["cc"]):
        if f:
            chain += "," + f
    if glow > 0:  # diffusion lumineuse sur la luminance seule (la chrominance est préservée)
        vw, vh = (W, H) if fill else (tw, th)
        g.append(chain + ",split[gb][gs]")
        g.append(f"[gs]scale={even(vw / 4)}:{even(vh / 4)}:flags=fast_bilinear,"
                 f"lutyuv=y='clip((val-150)*3\\,0\\,255)',gblur=sigma=9:planes=1,"
                 f"scale={vw}:{vh}:flags=bilinear[gl]")
        chain = (f"[gb][gl]blend=c0_mode=screen:c0_opacity={glow:.3f}"
                 f":c1_opacity=0:c2_opacity=0")
    # 3) Netteté (luminance uniquement : pas de bruit coloré amplifié)
    if args.sharpen > 0:
        chain += f",unsharp=5:5:{args.sharpen:.2f}:5:5:0"
    g.append(chain + "[mv0]")
    cur = "mv0"
    # 4) Fond drapeaux si la vidéo ne remplit pas le cadre
    if i_bd is not None:
        g.append(f"[{i_bd}:v]scale=out_color_matrix=bt709:out_range=tv,format=yuv420p,"
                 f"setsar=1[bd]")
        g.append(f"[bd][{cur}]overlay=(W-w)/2:(H-h)/2:shortest=1[mv1]")
        cur = "mv1"
    # 5) Médaillons des drapeaux : apparition après le fondu d'ouverture, retrait avant la fin
    if i_emb is not None:
        e_in = min(vf + 0.6, D / 4)
        e_out = max(e_in + 1.6, D - vf - 1.6)
        g.append(f"[{i_emb}:v]format=rgba,colorchannelmixer=aa={args.emblem_opacity:.2f},"
                 f"fade=t=in:st={e_in:.2f}:d=1.4:alpha=1,fade=t=out:st={e_out:.2f}:d=1.0:alpha=1,"
                 f"scale=out_color_matrix=bt709:out_range=tv,format=yuva420p[em]")
        g.append(f"[{cur}][em]overlay={emblem_xy[0]}:{emblem_xy[1]}:eof_action=pass[mv2]")
        cur = "mv2"
    # 6) Fondus au noir de la charte (entrée et sortie du corps de la vidéo)
    g.append(f"[{cur}]fade=t=in:st=0:d={vf:.2f}:color={FADE_COLOR},"
             f"fade=t=out:st={D - vf:.3f}:d={vf:.2f}:color={FADE_COLOR},"
             f"setsar=1,format=yuv420p[mv]")
    g.append(f"[0:v]fps={fps_s},setsar=1,format=yuv420p[cv]")
    g.append(f"[2:v]fps={fps_s},setsar=1,format=yuv420p[ov]")

    # Audio : stéréo 48 kHz, volume normalisé (-16 LUFS), fondus courts pour ne pas couper la voix
    fmt = "aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo"
    if info["audio"]:
        a = f"[1:a]asetpts=PTS-STARTPTS,{fmt}"
        if args.loudnorm:
            a += ",loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000"
        a += (f",afade=t=in:st=0:d={af:.2f},afade=t=out:st={D - af:.3f}:d={af:.2f},"
              f"atrim=end={D:.3f},apad=whole_dur={D:.3f}[ma]")
        g.append(a)
    else:
        g.append(f"anullsrc=r=48000:cl=stereo,atrim=duration={D:.3f}[ma]")
    if i_mus is not None:  # musique (Suno) sous la page de garde et l'outro
        g.append(f"[{i_mus}:a]{fmt},asplit=2[m1][m2]")
        g.append(f"[m1]atrim=0:{Dc:.3f},asetpts=PTS-STARTPTS,volume=0.8,"
                 f"afade=t=out:st={max(Dc - 1.2, 0):.3f}:d=1.2,apad=whole_dur={Dc:.3f}[ca]")
        g.append(f"[m2]atrim=0:{Do:.3f},asetpts=PTS-STARTPTS,volume=0.8,afade=t=in:st=0:d=0.8,"
                 f"afade=t=out:st={max(Do - 1.5, 0):.3f}:d=1.5,apad=whole_dur={Do:.3f}[oa]")
    else:
        g.append(f"anullsrc=r=48000:cl=stereo,atrim=duration={Dc:.3f}[ca]")
        g.append(f"anullsrc=r=48000:cl=stereo,atrim=duration={Do:.3f}[oa]")
    g.append("[cv][ca][mv][ma][ov][oa]concat=n=3:v=1:a=1[vout][aout]")

    gop = 2 * round(fps[0] / fps[1])
    cmd += [
        "-filter_complex", ";".join(g), "-map", "[vout]", "-map", "[aout]",
        "-c:v", "libx264", "-preset", args.preset, "-crf", str(args.crf),
        "-maxrate", "16M", "-bufsize", "32M", "-profile:v", "high", "-pix_fmt", "yuv420p",
        "-g", str(gop), "-colorspace", "bt709", "-color_primaries", "bt709",
        "-color_trc", "bt709", "-color_range", "tv",
        "-c:a", "aac", "-b:a", args.audio_bitrate, "-ar", "48000",
        "-movflags", "+faststart", "-max_muxing_queue_size", "4096",
        "-metadata", f"title={args.title.replace('|', ' ')} - {args.kicker}",
        "-metadata", f"artist={args.signature}",
        "-progress", "pipe:1", "-nostats", str(out_tmp),
    ]
    return cmd


def run_ffmpeg(cmd, total: float, log_path: Path) -> None:
    t0 = time.time()
    with open(log_path, "w", encoding="utf-8", errors="replace") as lf:
        lf.write(" ".join(f'"{c}"' if " " in c else c for c in cmd) + "\n\n")
        lf.flush()
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=lf, stdin=subprocess.DEVNULL,
                                text=True, bufsize=1)
        try:
            done, last = 0.0, 0.0
            for line in proc.stdout:
                key, _, val = line.strip().partition("=")
                if key in ("out_time_us", "out_time_ms") and val.isdigit():  # microsecondes
                    done = int(val) / 1e6
                elif key == "progress" and (time.time() - last > 1 or val == "end"):
                    last = time.time()
                    pct = min(done / total, 1.0) if total else 0.0
                    el = last - t0
                    eta = el * (1 - pct) / pct if pct > 0.02 else 0
                    bar = "#" * int(pct * 30) + "-" * (30 - int(pct * 30))
                    rt = done / el if el > 0 else 0
                    print(f"\r  [{bar}] {pct * 100:5.1f} %  | reste ~{int(eta // 60):3d} min "
                          f"{int(eta % 60):02d} s  | {rt:4.2f}x temps réel ", end="", flush=True)
            proc.wait()
        except KeyboardInterrupt:
            proc.terminate()
            proc.wait()
            raise
    print()
    if proc.returncode != 0:
        tail = log_path.read_text(encoding="utf-8", errors="replace").splitlines()[-15:]
        sys.exit("Échec de FFmpeg. Dernières lignes du journal (" + str(log_path) + ") :\n  "
                 + "\n  ".join(tail))


# --------------------------------------------------------------------------------------
# Programme principal
# --------------------------------------------------------------------------------------
def parse_args():
    p = argparse.ArgumentParser(
        description="Habillage premium d'une vidéo client (Djibouti x Inde) — Dian K. Pro",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument("--video", default="video_client.mp4", help="vidéo source")
    p.add_argument("--flag-dj", default="drapeau_djibouti.png", help="drapeau de Djibouti")
    p.add_argument("--flag-in", default="drapeau_inde.png", help="drapeau de l'Inde")
    p.add_argument("--output", default="video_client_final.mp4", help="fichier de sortie")
    p.add_argument("--format", default="auto", choices=["auto", "9:16", "16:9"],
                   help="auto = orientation de la source (portrait -> 1080x1920, paysage -> 1920x1080)")
    p.add_argument("--kicker", default=DEFAULT_KICKER, help="surtitre de la page de garde")
    p.add_argument("--title", default=DEFAULT_TITLE, help="titre (| pour forcer un retour à la ligne)")
    p.add_argument("--subtitle", default=DEFAULT_SUBTITLE, help="sous-titre de la page de garde")
    p.add_argument("--signature", default=DEFAULT_SIGNATURE, help="texte de l'outro")
    p.add_argument("--tagline", default=DEFAULT_TAGLINE, help="ligne sous la signature")
    p.add_argument("--logo", default="dk_monogramme.png",
                   help="monogramme de l'outro (ignoré s'il est absent ; '' pour le désactiver)")
    p.add_argument("--music", default=None, help="musique (Suno) sous la page de garde et l'outro")
    p.add_argument("--cover-seconds", type=float, default=5.0, help="durée de la page de garde")
    p.add_argument("--outro-seconds", type=float, default=5.0, help="durée de l'outro")
    p.add_argument("--fade", type=float, default=2.0, help="fondus au noir de l'image (s)")
    p.add_argument("--audio-fade", type=float, default=0.5,
                   help="fondus du son (s) — courts pour ne pas avaler le premier et le dernier mot")
    p.add_argument("--grade", default="luxe", choices=list(GRADES), help="intensité de l'étalonnage")
    p.add_argument("--glow", type=float, default=None,
                   help="diffusion lumineuse 0-0.3, 0 = désactivée (défaut : selon l'étalonnage)")
    p.add_argument("--sharpen", type=float, default=0.7, help="netteté 0-1.5 (0 = désactivée)")
    p.add_argument("--emblem", default="top-left",
                   choices=["top-left", "top-right", "bottom-left", "bottom-right", "off"],
                   help="position des médaillons des drapeaux")
    p.add_argument("--emblem-opacity", type=float, default=0.9, help="opacité des médaillons")
    p.add_argument("--crf", type=int, default=18, help="qualité H.264 (16 = master, 18 = haute, 21 = web)")
    p.add_argument("--preset", default="medium",
                   help="preset x264 : faster = brouillon rapide, slow = master (~1,7x plus lent)")
    p.add_argument("--audio-bitrate", default="192k")
    p.add_argument("--no-loudnorm", dest="loudnorm", action="store_false",
                   help="ne pas normaliser le volume à -16 LUFS")
    p.add_argument("--preview", type=float, default=None,
                   help="ne traiter que les N premières secondes (validation rapide du rendu)")
    p.add_argument("--keep-temp", action="store_true", help="conserver les fichiers intermédiaires")
    return p.parse_args()


def main() -> None:
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    args = parse_args()
    t_start = time.time()
    log("\n=== Dian K. Pro — habillage vidéo Djibouti x Inde ===\n")

    src = find_file(args.video)
    dj_p, in_p = find_file(args.flag_dj), find_file(args.flag_in)
    music_p = find_file(args.music, required=False) if args.music else None
    if args.music and not music_p:
        log(f"  ! Musique « {args.music} » introuvable : page de garde et outro sans musique.")
    ff = ffmpeg_exe()

    info = probe(src)
    D = min(info["duration"], args.preview) if args.preview else info["duration"]
    fps = pick_fps(info["fps"])
    fps_f = fps[0] / fps[1]
    src_portrait = info["h"] > info["w"]
    portrait = src_portrait if args.format == "auto" else args.format == "9:16"
    W, H = (1080, 1920) if portrait else (1920, 1080)
    fill = abs((info["w"] / info["h"]) / (W / H) - 1) <= 0.04  # même format à 4 % près

    out = Path(args.output)
    if args.preview and args.output == "video_client_final.mp4":
        out = Path("video_client_final_apercu.mp4")
    out = out if out.is_absolute() else Path.cwd() / out
    total = args.cover_seconds + D + args.outro_seconds

    log(f"Source   : {src.name} — {info['w']}x{info['h']}, {info['duration']:.1f} s, "
        f"{info['fps'] or '?'} i/s, son : {'oui' if info['audio'] else 'non'}")
    log(f"Sortie   : {out.name} — {W}x{H} ({'9:16' if portrait else '16:9'}), {fps_f:.3f} i/s, "
        f"durée totale {total:.1f} s" + (f"  [APERÇU {D:.0f} s]" if args.preview else ""))
    if min(info["w"], info["h"]) < 720:
        log("  ! Source en basse définition (< 720p, typique d'un envoi WhatsApp) : "
            "demandez le fichier original pour un rendu net.")
    est = (16e6 + 192e3) / 8 * total
    free = shutil.disk_usage(out.parent).free
    if free < est * 1.3:
        log(f"  ! Espace disque faible : {free / 1e9:.1f} Go libres pour ~{est / 1e9:.1f} Go max.")

    work = Path(tempfile.mkdtemp(prefix=".dkpro_", dir=out.parent))
    try:
        dj, ind = load_flag(dj_p), load_flag(in_p)
        fdj, fin = emblem_center(dj, "dj"), emblem_center(ind, "in")

        log("\n[1/4] Page de garde (MoviePy)...")
        cover = make_cover(args, dj, ind, fdj, fin, W, H, portrait)
        thumb = out.with_name(out.stem + "_vignette.png")
        cover.save_frame(str(thumb), t=0)
        cover_p = work / "cover.mp4"
        write_segment(cover, cover_p, fps_f)

        log("[2/4] Outro Dian K. Pro (MoviePy)...")
        outro_p = work / "outro.mp4"
        write_segment(make_outro(args, W, H, portrait), outro_p, fps_f)

        log("[3/4] Drapeaux...")
        emblem_p = backdrop_p = None
        emblem_xy = (0, 0)
        if not fill:
            s = min(W / info["w"], H / info["h"])
            backdrop_p = work / "backdrop.png"
            build_backdrop(dj, ind, fdj, fin, W, H, even(info["w"] * s),
                           even(info["h"] * s)).save(backdrop_p)
            log("      vidéo plus étroite que le cadre : drapeaux en panneaux latéraux.")
        elif args.emblem != "off":
            emb = build_emblem(dj, ind, fdj, fin, round(0.08 * min(W, H)))
            emblem_p = work / "emblem.png"
            emb.save(emblem_p)
            m = round(0.045 * min(W, H))
            top = 270 if portrait else m                   # sous l'en-tête WhatsApp / Stories
            bottom = (1600 if portrait else H - m) - emb.height
            x = m if "left" in args.emblem else W - m - emb.width
            emblem_xy = (x, top if "top" in args.emblem else bottom)
            log(f"      médaillons {args.emblem}, opacité {args.emblem_opacity:.0%}.")

        log("[4/4] Étalonnage, netteté, fondus et assemblage (FFmpeg)...")
        out_tmp = work / ("rendu" + out.suffix)
        cmd = build_ffmpeg(args, ff, src, info, D, fps, W, H, fill, cover_p, outro_p, emblem_p,
                           emblem_xy, backdrop_p, music_p, out_tmp)
        log_path = out.with_suffix(".log")
        run_ffmpeg(cmd, total, log_path)
        os.replace(out_tmp, out)  # le fichier final n'apparaît que s'il est complet
    except KeyboardInterrupt:
        sys.exit("\nInterrompu : aucun fichier final n'a été écrit.")
    finally:
        if not args.keep_temp:
            shutil.rmtree(work, ignore_errors=True)

    res = ffmpeg_parse_infos(str(out))
    dur = float(res.get("duration") or 0)
    log(f"\nTerminé en {(time.time() - t_start) / 60:.1f} min.")
    log(f"  Vidéo    : {out}  ({out.stat().st_size / 1e6:.1f} Mo, {dur:.1f} s, "
        f"{res['video_size'][0]}x{res['video_size'][1]})")
    log(f"  Vignette : {thumb}")
    if portrait and dur > 90:
        log(f"  ! {dur:.0f} s > 90 s : trop long pour un Statut WhatsApp — à découper.")


if __name__ == "__main__":
    main()
