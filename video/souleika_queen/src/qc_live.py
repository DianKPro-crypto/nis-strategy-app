"""Contrôle objectif des effets animés sur le MP4 final : mouvement réel et calage sur les temps du chant.

Usage : python3 src/qc_live.py   (écrit analysis/qc_live.md)
"""
import subprocess

import numpy as np

from common import FPS, ROOT, load_json

MP4 = ROOT / "exports" / "Souleika_Queen_Anniversaire_1080x1920.mp4"
SW, SH = 270, 480


def frames(t0, t1):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t0}", "-i", str(MP4), "-t", f"{t1 - t0}",
                          "-vf", f"scale={SW}:{SH},format=gray", "-f", "rawvideo", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, SH, SW).astype(np.float32)


def motion(t0, t1, box):
    """Différence moyenne image à image dans une zone (fractions du cadre), sans les 4 premières images (coupe)."""
    f = frames(t0, t1)
    x0, y0, x1, y1 = (int(box[0] * SW), int(box[1] * SH), int(box[2] * SW), int(box[3] * SH))
    d = np.abs(np.diff(f[:, y0:y1, x0:x1], axis=0)).mean(axis=(1, 2))
    return float(np.median(d[4:]))


def peaks_vs_beats(t0, t1, box, beats):
    """Pics de luminosité d'une zone comparés aux temps de la musique."""
    f = frames(t0, t1)
    x0, y0, x1, y1 = (int(box[0] * SW), int(box[1] * SH), int(box[2] * SW), int(box[3] * SH))
    lum = f[:, y0:y1, x0:x1].mean(axis=(1, 2))
    lum = lum - np.convolve(lum, np.ones(9) / 9, mode="same")          # retire la dérive lente
    pk = [i for i in range(2, len(lum) - 2) if lum[i] == lum[i - 2:i + 3].max() and lum[i] > 0.25 * lum.max()]
    times = [t0 + i / FPS for i in pk]
    bs = [b for b in beats if t0 + 0.1 < b < t1 - 0.1]
    err = [min(abs(t - b) for t in times) for b in bs] if times else []
    return times, bs, err


def main():
    an = load_json("analysis/audio_analysis.json")
    beats = an["beats_refined"]
    tl = load_json("config/timeline.json")
    lines = ["# Contrôle des effets animés (MP4 final)", ""]
    lines.append("## Mouvement dans les zones d'effets (différence moyenne image à image, 0-255)")
    lines.append("Référence : plans de photos non animées avec un mouvement de caméra comparable.")
    shots = {(s["photo"], round(s["start"], 2)): s for s in tl["shots"] if "photo" in s}
    rows = [
        ("P13 papillons (« Que ton bonheur grandisse »)", "P13", 67.82, (0.62, 0.05, 1.0, 0.75)),
        ("P15 pétales (« mille années d'amour »)", "P15", 76.36, (0.60, 0.0, 1.0, 0.65)),
        ("P14 lumière dorée (« étoile scintille »)", "P14", 36.87, (0.0, 0.0, 1.0, 0.25)),
        ("P16 éclats d'or (entrée du groove, plan serré)", "P16", 33.51, (0.0, 0.0, 0.25, 1.0)),
        ("Référence P11 (non animée, même cadrage serré)", "P11", 72.1, (0.0, 0.0, 0.25, 1.0)),
        ("Référence P12 (non animée)", "P12", 18.2, (0.62, 0.05, 1.0, 0.75)),
    ]
    for label, pid, start, box in rows:
        s = shots[(pid, start)]
        a, b = s["start"] + 0.5, s["end"] - 0.5
        lines.append(f"- {label} [{a:.1f}–{b:.1f} s] : {motion(a, b, box):.2f}")
    lines += ["", "## Calage sur les temps de la musique"]
    for label, a, b, box in [("Pulsation des rayons dorés P14 (haut du cadre)", 37.3, 41.2, (0.25, 0.0, 0.75, 0.18)),
                             ("Explosions d'or P16 (« Log drum… fais-la vibrer »)", 143.55, 145.3, (0.0, 0.0, 0.5, 1.0))]:
        times, bs, err = peaks_vs_beats(a, b, box, beats)
        if err:
            ok = sum(e <= 1.5 / FPS for e in err)
            lines.append(f"- {label} : {len(times)} pics de lumière pour {len(bs)} temps ; "
                         f"{ok}/{len(bs)} temps ont un pic à ±1,5 image ; écart médian {np.median(err) * 1000:.0f} ms")
    (ROOT / "analysis" / "qc_live.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
