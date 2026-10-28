"""Contrôle objectif de la version « Nuit enchantée » sur les MP4 finaux.

1. Signature visuelle comparée à la version actuelle (et à la première version rêve si elle est présente),
   aux mêmes instants : contraste, profondeur des noirs, saturation, « colorfulness » (Hasler & Süsstrunk, 2003).
2. Calage : coupes franches à l'image près, éclatements des feux d'artifice et des spirales sur les temps du chant.

Usage : python3 src/qc_enchante.py   (écrit analysis/qc_enchante.md)
"""
import subprocess
import sys

import numpy as np

from common import FPS, ROOT, W, H

CLASSIC = ROOT / "exports" / "Souleika_Queen_Anniversaire_1080x1920.mp4"
REVE_V1 = ROOT / "exports" / "reve" / "Souleika_Queen_Reve_1080x1920.mp4"


def rgb_frame(path, t, w=270, h=480):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t}", "-i", str(path), "-frames:v", "1",
                          "-vf", f"scale={w}:{h},format=rgb24", "-f", "rawvideo", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(h, w, 3).astype(np.float32) / 255


def gray(path, t0, dur, w=216, h=384):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t0}", "-i", str(path), "-t", f"{dur}",
                          "-vf", f"scale={w}:{h},format=gray", "-f", "rawvideo", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w).astype(np.float32)


def look(img):
    lum = img @ np.float32([0.2126, 0.7152, 0.0722])
    mx, mn = img.max(axis=2), img.min(axis=2)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    R, G, B = img[..., 0] * 255, img[..., 1] * 255, img[..., 2] * 255
    rg, yb = R - G, 0.5 * (R + G) - B
    colorful = np.hypot(rg.std(), yb.std()) + 0.3 * np.hypot(rg.mean(), yb.mean())
    return lum.std(), np.percentile(lum, 5), sat.mean(), colorful


def main():
    sys.path.insert(0, str(ROOT / "src"))
    from render import Renderer
    r = Renderer("enchante")
    st = r.style
    so = st["sorties"]
    mp4 = ROOT / so["dossier"] / f"{so['prefixe']}_1080x1920.mp4"
    lines = [f"# Contrôle de la version « Nuit enchantée » ({mp4.name})", ""]

    # 1. signature visuelle, milieu de chaque plan
    vers = [("Actuelle", CLASSIC), ("Nuit enchantée", mp4)] + ([("Rêve v1 (écartée)", REVE_V1)] if REVE_V1.exists() else [])
    acc = {k: [] for k, _ in vers}
    for s in r.shots:
        t = s["start"] + 0.55 * (s["end"] - s["start"])
        for k, p in vers:
            acc[k].append(look(rgb_frame(p, t)))
    m = {k: np.mean(v, axis=0) for k, v in acc.items()}
    lines += ["## Signature visuelle (milieu de chaque plan, moyennes sur 41 plans)", "",
              "| Mesure | " + " | ".join(k for k, _ in vers) + " |", "|---|" + "---|" * len(vers)]
    names = ["Contraste (écart-type de luminance)", "Noirs (5e centile de luminance ; plus bas = plus profonds)",
             "Saturation moyenne", "Colorfulness (Hasler & Süsstrunk)"]
    for i, nm in enumerate(names):
        ref = m["Actuelle"][i]
        cells = [f"{m[k][i]:.3f}" + ("" if k == "Actuelle" else f" ({(m[k][i] / ref - 1) * 100:+.0f} %)") for k, _ in vers]
        lines.append(f"| {nm} | " + " | ".join(cells) + " |")

    # 2a. coupes franches à l'image près
    errs = []
    for i, s in enumerate(r.shots[1:], 1):
        if s["trans"]["type"] != "cut" or s.get("layout") == "bands" or r.shots[i - 1].get("layout") == "bands":
            continue
        T = s["start"]
        f = gray(mp4, T - 0.3, 0.6)
        d = np.abs(np.diff(f, axis=0)).mean(axis=(1, 2))
        k = int(np.argmax(d))
        errs.append(abs(T - 0.3 + (k + 1) / FPS - T))
    errs = np.array(errs)
    lines += ["", "## Calage", f"- Coupes franches : {len(errs)} coupes, {int((errs <= 1.01 / FPS).sum())}/{len(errs)} "
              f"à l'image près (écart max {errs.max() * 1000:.0f} ms)"]

    # 2b. feux d'artifice : instant d'éclatement recalé sur le temps mesuré le plus proche
    beats = np.array(r.beats)
    off = [abs(beats[np.argmin(abs(beats - sh.t))] - sh.t) for sh in r.enchant.shells]
    moved = [abs(sh.t - f["t"]) for sh, f in zip(r.enchant.shells, st["feux"])]
    lines.append(f"- Feux d'artifice : {len(off)} éclatements, tous sur un temps mesuré du chant "
                 f"(écart max {max(off) * 1000:.0f} ms ; recalage max par rapport à la configuration {max(moved) * 1000:.0f} ms)")
    # vérification sur l'image : la lumière de la zone de l'éclatement monte à l'instant prévu
    meas = []
    for sh in r.enchant.shells:
        f = gray(mp4, sh.t - 0.4, 0.8)
        x, y = sh.x / W * f.shape[2], sh.y / H * f.shape[1]
        x0, x1 = int(max(0, x - 20)), int(min(f.shape[2], x + 20))
        y0, y1 = int(max(0, y - 20)), int(min(f.shape[1], y + 20))
        lum = f[:, y0:y1, x0:x1].mean(axis=(1, 2))
        k = int(np.argmax(np.diff(lum)))
        meas.append(abs(sh.t - 0.4 + (k + 1) / FPS - sh.t))
    meas = np.array(meas)
    lines.append(f"- Vérification sur l'image (montée de lumière la plus forte au point d'éclatement) : "
                 f"{int((meas <= 2.01 / FPS).sum())}/{len(meas)} à ±2 images, écart médian {np.median(meas) * 1000:.0f} ms")
    cuts = {round(s["start"], 2) for s in r.shots}
    sp = [v.c for v in r.enchant.vortex]
    lines.append(f"- Spirales : {len(sp)} éclatements, sur " + ", ".join(
        f"{c['t1']:.2f} s ({'coupe sur le temps' if round(c['t1'], 2) in cuts else 'temps'})" for c in sp))
    (ROOT / "analysis" / "qc_enchante.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
