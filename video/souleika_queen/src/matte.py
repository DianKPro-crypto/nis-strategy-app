"""Détourage local des photos (version « Nuit enchantée ») : la personne est séparée de son arrière-plan
pour que la lumière du décor change sans jamais toucher au visage ni au corps.

Tout tourne sur cette machine (modèle BiRefNet-portrait au format ONNX, onnxruntime sur CPU) :
aucune photo n'est envoyée à un service externe.

Pour chaque photo, on produit dans work/mattes/ :
  Pxx_alpha.png   masque de la personne (0 = décor, 255 = personne), à la résolution de la photo
  Pxx_fg.png      couleurs de la personne débarrassées du reflet de l'ancien décor sur les cheveux et les bords
  Pxx_plate.png   décor seul : la place de la personne est comblée par le décor voisin (servira flou et assombri,
                  uniquement pour l'effet de profondeur ; jamais à l'écran sans la personne devant)

Usage :
  python3 src/matte.py              calcule ce qui manque (un processus par photo : mémoire maîtrisée)
  python3 src/matte.py --force P04  recalcule une photo
  python3 src/matte.py --prepare    refait couleurs et décor seul (sans relancer le modèle)
"""
import argparse
import subprocess
import sys

import cv2
import numpy as np

from common import ROOT, load_json
from photos import load_rgb

MODEL = ROOT / "work" / "models" / "BiRefNet-portrait-epoch_150.onnx"
OUT = ROOT / "work" / "mattes"


def segment(pid, cfg):
    import onnxruntime as ort
    so = ort.SessionOptions()
    so.intra_op_num_threads = 4
    so.enable_cpu_mem_arena = False
    sess = ort.InferenceSession(str(MODEL), so, providers=["CPUExecutionProvider"])
    im = load_rgb(ROOT / cfg["file"])
    h, w = im.shape[:2]
    x = cv2.resize(im, (1024, 1024), interpolation=cv2.INTER_AREA if max(h, w) > 1024 else cv2.INTER_CUBIC)
    x = (x.astype(np.float32) / 255 - np.float32([0.485, 0.456, 0.406])) / np.float32([0.229, 0.224, 0.225])
    logit = sess.run(None, {sess.get_inputs()[0].name: x.transpose(2, 0, 1)[None]})[0][0, 0]
    a = 1 / (1 + np.exp(-logit))
    a = cv2.resize(a, (w, h), interpolation=cv2.INTER_CUBIC)
    a = np.clip((a - 0.03) / 0.94, 0, 1)                 # résidus quasi nuls / quasi pleins nettoyés
    cv2.imwrite(str(OUT / f"{pid}_alpha.png"), (a * 255 + 0.5).astype(np.uint8))


def _fb_blur_fusion(image, F, B, alpha, r):
    """Estimation rapide des couleurs de premier plan (Forte & Pitié, 2021, « blur fusion »)."""
    a = alpha[..., None]
    ba = cv2.blur(alpha, (r, r))[..., None]
    bF = cv2.blur(F * a, (r, r)) / (ba + 1e-5)
    bB = cv2.blur(B * (1 - a), (r, r)) / ((1 - ba) + 1e-5)
    F = bF + a * (image - a * bF - (1 - a) * bB)
    return np.clip(F, 0, 1), bB


def _push_pull(img, valid):
    """Comble les zones invalides par la couleur moyenne du décor voisin, de plus en plus large (sans traînées)."""
    out = img.copy()
    todo = valid < 0.5
    for sigma in (4, 8, 16, 32, 64, 128):
        num = cv2.GaussianBlur(img * valid[..., None], (0, 0), sigma)
        den = cv2.GaussianBlur(valid, (0, 0), sigma)
        take = todo & (den > 0.12)
        out[take] = (num / (den[..., None] + 1e-6))[take]
        todo &= ~take
    if todo.any():
        out[todo] = (img * valid[..., None]).sum((0, 1)) / max(1.0, valid.sum())
    hole = cv2.GaussianBlur((valid < 0.5).astype(np.float32), (0, 0), 6)[..., None]
    return img * (1 - hole) + cv2.GaussianBlur(out, (0, 0), 6) * hole


def prepare(pid, cfg):
    im = load_rgb(ROOT / cfg["file"]).astype(np.float32) / 255
    a = cv2.imread(str(OUT / f"{pid}_alpha.png"), cv2.IMREAD_GRAYSCALE).astype(np.float32) / 255
    h, w = a.shape
    # 1. couleurs de la personne (bords et cheveux) : l'ancien décor ne « bave » plus sur le nouveau
    F, bB = _fb_blur_fusion(im, im, im, a, max(9, int(0.06 * max(h, w))))
    F, _ = _fb_blur_fusion(im, F, bB, a, max(3, int(0.004 * max(h, w))) | 1)
    F = np.where(a[..., None] > 0.995, im, F)            # intérieur : pixels d'origine, strictement inchangés
    cv2.imwrite(str(OUT / f"{pid}_fg.png"), cv2.cvtColor((F * 255 + 0.5).astype(np.uint8), cv2.COLOR_RGB2BGR))
    # 2. décor seul : la silhouette (élargie) est comblée par le décor voisin, à basse résolution
    q = 512 / max(h, w)
    sw, sh = max(8, round(w * q)), max(8, round(h * q))
    small = cv2.resize(im, (sw, sh), interpolation=cv2.INTER_AREA)
    m = cv2.resize(a, (sw, sh), interpolation=cv2.INTER_AREA)
    m = cv2.dilate((m > 0.06).astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (13, 13)))
    fill = _push_pull(small, 1 - m.astype(np.float32))
    fill = cv2.resize(fill, (w, h), interpolation=cv2.INTER_CUBIC)
    mk = cv2.GaussianBlur(cv2.resize(m.astype(np.float32), (w, h), interpolation=cv2.INTER_LINEAR), (0, 0), 0.006 * max(h, w))
    mk = np.clip(mk * 1.6, 0, 1)[..., None]
    plate = im * (1 - mk) + fill * mk
    cv2.imwrite(str(OUT / f"{pid}_plate.png"), cv2.cvtColor((np.clip(plate, 0, 1) * 255 + 0.5).astype(np.uint8), cv2.COLOR_RGB2BGR))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--one")
    ap.add_argument("--force", nargs="*", default=[])
    ap.add_argument("--prepare", action="store_true", help="refaire couleurs et décor seul à partir des masques existants")
    args = ap.parse_args()
    pcfg = {k: v for k, v in load_json("config/photos.json").items() if k.startswith("P")}
    OUT.mkdir(parents=True, exist_ok=True)
    if args.prepare:
        for pid in sorted(pcfg):
            if (OUT / f"{pid}_alpha.png").exists():
                prepare(pid, pcfg[pid])
        return
    if args.one:
        segment(args.one, pcfg[args.one])
        prepare(args.one, pcfg[args.one])
        return
    for pid in sorted(pcfg):
        if (OUT / f"{pid}_plate.png").exists() and pid not in args.force:
            continue
        print("détourage", pid, flush=True)
        subprocess.run([sys.executable, __file__, "--one", pid], check=True)   # un processus par photo


if __name__ == "__main__":
    main()
