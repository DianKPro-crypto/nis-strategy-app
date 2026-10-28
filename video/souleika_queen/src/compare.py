"""Planche « avant / après » : mêmes instants du film, version actuelle et version « Nuit enchantée ».

Usage :
  python3 src/compare.py            images extraites des deux MP4 finaux
  python3 src/compare.py --stills   version enchantée calculée image par image (aperçu avant le rendu complet)
"""
import argparse
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from common import ROOT, load_json, tc

MOMENTS = [
    (0.0, "Page d'accueil", "Nuit étoilée"),
    (29.3, "Avant le groove", "Crépuscule · spirale"),
    (50.0, "Ton sourire", "Heure dorée"),
    (64.6, "Souleika Queen", "Bal royal · feux"),
    (86.2, "Waan ku jeclahay", "Cœur de feu d'artifice"),
    (128.5, "Paix et lumière", "Clair de lune · lanternes"),
    (152.5, "Hambalyo !", "Bal royal · feux"),
    (179.0, "Je te MOUA…", "Jardin de nuit · cœur"),
]
CLASSIC = ROOT / "exports" / "Souleika_Queen_Anniversaire_1080x1920.mp4"


def grab(path, t):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t}", "-i", str(path), "-frames:v", "1",
                         "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    return Image.fromarray(np.frombuffer(raw, np.uint8).reshape(1920, 1080, 3))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stills", action="store_true")
    args = ap.parse_args()
    st = load_json("config/style_enchante.json")
    so = st["sorties"]
    dream = ROOT / so["dossier"] / f"{so['prefixe']}_1080x1920.mp4"
    if args.stills:
        import sys
        sys.path.insert(0, str(ROOT / "src"))
        from render import Renderer
        r = Renderer("enchante")
        new = {t: Image.fromarray(r.frame(t)) for t, _, _ in MOMENTS}
    else:
        new = {t: grab(dream, t) for t, _, _ in MOMENTS}
    tw, th, gap, cols = 340, 604, 18, 4
    head, lab = 170, 64
    rows = (len(MOMENTS) + cols - 1) // cols
    Wb = cols * tw + (cols + 1) * gap
    Hb = head + rows * (2 * th + 2 * lab + 2 * gap) + gap
    board = Image.new("RGB", (Wb, Hb), (11, 11, 12))
    d = ImageDraw.Draw(board)
    fdir = ROOT / "assets" / "fonts"
    ft = ImageFont.truetype(str(fdir / "playfair-display-latin-700-normal.woff"), 50)
    fs = ImageFont.truetype(str(fdir / "Inter-Medium.otf"), 24)
    fl = ImageFont.truetype(str(fdir / "Inter-SemiBold.otf"), 22)
    gold, ivory, grey = (227, 179, 76), (245, 239, 229), (190, 184, 172)
    d.text((gap + 4, 34), "Souleika Queen — Nuit enchantée", font=ft, fill=gold)
    d.text((gap + 6, 108), "Mêmes instants, même montage, même chant · en haut : version actuelle · en bas : Nuit enchantée",
           font=fs, fill=ivory)
    for k, (t, moment, world) in enumerate(MOMENTS):
        r_, c = divmod(k, cols)
        x = gap + c * (tw + gap)
        y = head + r_ * (2 * th + 2 * lab + 2 * gap)
        for j, (img, label, col) in enumerate(((grab(CLASSIC, t), f"Actuelle · {tc(t)[:5]}", grey),
                                               (new[t], world, gold))):
            yy = y + j * (th + lab + gap)
            board.paste(img.resize((tw, th), Image.LANCZOS), (x, yy))
            d.rectangle([x - 1, yy - 1, x + tw, yy + th], outline=col, width=2 if j else 1)
            d.text((x + 2, yy + th + 8), label, font=fl, fill=col)
            if j == 0:
                d.text((x + 2, yy + th + 34), moment, font=fs, fill=ivory)
    dst = ROOT / so["dossier"] / f"{so['prefixe']}_Avant_Apres.jpg"
    dst.parent.mkdir(parents=True, exist_ok=True)
    board.save(dst, quality=90)
    print("écrit", dst)


if __name__ == "__main__":
    main()
