"""Contrôle de la version rêve sur les MP4 finaux : calage des transitions sur les temps et signature visuelle
(comparée à la version actuelle, aux mêmes instants).

Usage : python3 src/qc_reve.py   (écrit analysis/qc_reve.md)
"""
import subprocess
import sys

import numpy as np

from common import FPS, ROOT

CLASSIC = ROOT / "exports" / "Souleika_Queen_Anniversaire_1080x1920.mp4"
DREAM = ROOT / "exports" / "reve" / "Souleika_Queen_Reve_1080x1920.mp4"


def gray(path, t0, dur, w=216, h=384):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t0}", "-i", str(path), "-t", f"{dur}",
                          "-vf", f"scale={w}:{h},format=gray", "-f", "rawvideo", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w).astype(np.float32)


def rgb_frame(path, t, w=270, h=480):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t}", "-i", str(path), "-frames:v", "1",
                          "-vf", f"scale={w}:{h},format=rgb24", "-f", "rawvideo", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(h, w, 3).astype(np.float32) / 255


def look(img):
    lum = img @ np.float32([0.2126, 0.7152, 0.0722])
    mx, mn = img.max(axis=2), img.min(axis=2)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    return lum.std(), np.percentile(lum, 5), sat.mean()


def main():
    sys.path.insert(0, str(ROOT / "src"))
    from render import Renderer
    r = Renderer("reve")
    lines = ["# Contrôle de la version rêve", ""]
    # 1. calage : chaque micro-fondu lumineux est centré sur le temps de la musique
    errs = []
    for s in r.shots:
        if s["trans"]["type"] != "eclat":
            continue
        T = s["start"]
        f = gray(DREAM, T - 0.4, 0.8)
        d = np.abs(np.diff(f, axis=0)).mean(axis=(1, 2))
        k = int(np.argmax(d))                         # plus forte variation : entre les images k et k+1
        t_peak = T - 0.4 + (k + 1) / FPS
        errs.append(abs(t_peak - T))
    errs = np.array(errs)
    lines.append("## Calage des micro-fondus lumineux (coupes rythmées) sur les temps")
    lines.append(f"- {len(errs)} transitions ; variation maximale à {np.median(errs) * 1000:.0f} ms du temps prévu en médiane, "
                 f"{np.max(errs) * 1000:.0f} ms au pire ; {int((errs <= 2.5 / FPS).sum())}/{len(errs)} à ±2,5 images")
    # 2. signature visuelle : mêmes instants, version actuelle vs rêve
    lines += ["", "## Signature visuelle (milieu de chaque plan, moyennes)"]
    acc = {"cl": [], "dr": []}
    for s in r.shots:
        t = s["start"] + 0.55 * (s["end"] - s["start"])
        acc["cl"].append(look(rgb_frame(CLASSIC, t)))
        acc["dr"].append(look(rgb_frame(DREAM, t)))
    cl, dr = np.mean(acc["cl"], axis=0), np.mean(acc["dr"], axis=0)
    lines.append(f"- Contraste (écart-type de luminance) : {cl[0]:.3f} → {dr[0]:.3f} ({(dr[0] / cl[0] - 1) * 100:+.0f} %)")
    lines.append(f"- Noirs (5e centile de luminance, « noirs laiteux ») : {cl[1]:.3f} → {dr[1]:.3f}")
    lines.append(f"- Saturation moyenne : {cl[2]:.3f} → {dr[2]:.3f} ({(dr[2] / cl[2] - 1) * 100:+.0f} %)")
    (ROOT / "analysis" / "qc_reve.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
