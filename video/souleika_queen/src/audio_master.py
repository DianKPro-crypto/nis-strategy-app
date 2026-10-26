"""Master audio : gain mesuré + fin en douceur.

L'enregistrement Suno s'arrête net en plein temps (179,18 s). Pour finir en douceur sans ajouter de musique :
  1. la musique s'adoucit (filtre passe-bas progressif) puis s'éteint ;
  2. une queue de réverbération du chant lui-même (dernières mesures) prend le relais et s'éteint naturellement ;
  3. le silence est atteint exactement à la fin de l'image.

Usage : python3 src/audio_master.py   (écrit work/audio_master.wav, 48 kHz stéréo float)
"""
import subprocess

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, fftconvolve, sosfiltfilt

from common import ROOT, load_json

SR = 48000


def ramp(n, a, b, kind="cos"):
    """Rampe 0 -> 1 entre les échantillons a et b (cosinus : sans cassure)."""
    x = np.clip((np.arange(n) - a) / max(1, b - a), 0, 1)
    return (0.5 - 0.5 * np.cos(np.pi * x)) if kind == "cos" else x


def build():
    tl = load_json("config/timeline.json")
    p = tl["audio_ending"]
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(ROOT / tl["audio"]), "-map", "0:a", "-ac", "2", "-ar", str(SR),
                          "-f", "f32le", "-"], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32).reshape(-1, 2).astype(np.float64)
    x *= 10 ** (tl["audio_gain_db"] / 20)
    n_src = len(x)
    n = int(round(tl["shots"][-1]["end"] * SR))
    s = lambda t: int(round(t * SR))

    # 1. musique : passe-bas progressif puis extinction (courbe en cosinus)
    lp = sosfiltfilt(butter(4, p["lowpass_hz"], btype="low", fs=SR, output="sos"), x, axis=0)
    r = ramp(n_src, s(p["soften_start"]), s(p["dry_fade_end"]))[:, None] * p["soften_amount"]
    dry = x * (1 - r) + lp * r
    dry *= (1 - ramp(n_src, s(p["dry_fade_start"]), s(p["dry_fade_end"])))[:, None]

    # 2. queue de réverbération : envoi des dernières mesures dans une réverbération synthétique stéréo
    send = x * ramp(n_src, s(p["send_start"]), s(p["send_full"]))[:, None]
    send *= (1 - ramp(n_src, n_src - s(0.03), n_src))[:, None]          # pas de clic à la coupure d'origine
    rng = np.random.default_rng(31)
    L = s(p["rt60"] * 1.3)
    t = np.arange(L) / SR
    env = np.exp(-6.91 * t / p["rt60"]) * np.clip(t / 0.012, 0, 1)
    ir = rng.normal(0, 1, (L, 2)) * env[:, None]
    ir = np.vstack([np.zeros((s(0.025), 2)), ir])                          # pré-délai 25 ms
    ir = sosfiltfilt(butter(2, [p["wet_hp_hz"], p["wet_lp_hz"]], btype="band", fs=SR, output="sos"), ir, axis=0)
    ir /= np.sqrt((ir ** 2).sum(axis=0, keepdims=True))                    # énergie unitaire par canal
    wet = np.stack([fftconvolve(send[:, c], ir[:, c])[:n] for c in range(2)], axis=1)
    wet = np.pad(wet, ((0, max(0, n - len(wet))), (0, 0)))
    wet *= 10 ** (p["wet_db"] / 20)

    y = np.zeros((n, 2))
    y[:n_src] = dry
    y += wet
    # 3. extinction finale : silence exact à la dernière image
    y *= (1 - ramp(n, s(p["final_fade_start"]), n))[:, None]

    # sécurité : la fin ajoutée ne doit jamais dépasser la crête du morceau lui-même (aucune compression du chant)
    ref = np.abs(x).max()
    tail = slice(s(p["send_start"]), n)
    if np.abs(y[tail]).max() > ref:
        y[tail] *= ref / np.abs(y[tail]).max()
    out = ROOT / "work" / "audio_master.wav"
    wavfile.write(out, SR, y.astype(np.float32))

    # enveloppe de contrôle (RMS par 250 ms) sur la fin
    rms = lambda a, b: 20 * np.log10(np.sqrt(np.mean(y[s(a):s(b)] ** 2)) + 1e-12)
    print(f"écrit {out} : {n / SR:.3f} s, crête {20 * np.log10(np.abs(y).max()):.2f} dBFS")
    print("fin (dBFS par 250 ms) :", " ".join(f"{t0:.2f}:{rms(t0, t0 + 0.25):.0f}" for t0 in np.arange(175.0, n / SR - 0.2, 0.75)))
    return out


if __name__ == "__main__":
    build()
