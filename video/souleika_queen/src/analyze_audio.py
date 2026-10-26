"""Analyse musicale locale : tempo, temps forts, énergie, nouveautés spectrales (changements de section).

Usage : python3 src/analyze_audio.py <audio.wav> <out.json> [<plot.png>]
"""
import json
import sys

import librosa
import numpy as np

audio, out = sys.argv[1:3]
plot = sys.argv[3] if len(sys.argv) > 3 else None

y, sr = librosa.load(audio, sr=22050, mono=True)
hop = 512
dur = len(y) / sr

tempo, beats = librosa.beat.beat_track(y=y, sr=sr, hop_length=hop, units="time")
onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop)
onsets = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr, hop_length=hop, units="time")

# Énergie globale et énergie grave (log drum Amapiano : ~40-120 Hz).
S = np.abs(librosa.stft(y, n_fft=2048, hop_length=hop))
freqs = librosa.fft_frequencies(sr=sr, n_fft=2048)
rms = librosa.feature.rms(S=S)[0]
low = S[(freqs >= 35) & (freqs <= 120)].mean(axis=0)
mid_voice = S[(freqs >= 250) & (freqs <= 3500)].mean(axis=0)
t = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=hop)

def per_second(x):
    n = int(np.ceil(dur))
    return [float(np.mean(x[(t >= i) & (t < i + 1)])) if np.any((t >= i) & (t < i + 1)) else 0.0 for i in range(n)]

# Nouveauté spectrale (matrice d'auto-similarité sur chroma + MFCC) pour repérer les changements de section.
chroma = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=hop)
mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13, hop_length=hop)
feat = np.vstack([librosa.util.normalize(chroma, axis=1), librosa.util.normalize(mfcc, axis=1)])
# moyenne par battement pour la robustesse
beat_frames = librosa.time_to_frames(beats, sr=sr, hop_length=hop)
fs = librosa.util.sync(feat, beat_frames, aggregate=np.median)
R = librosa.segment.recurrence_matrix(fs, mode="affinity", sym=True)
# noyau en damier
k = 16
g = np.outer(np.r_[np.ones(k), -np.ones(k)], np.r_[np.ones(k), -np.ones(k)])
g *= np.outer(np.hanning(2 * k), np.hanning(2 * k))
Rp = np.pad(R, k, mode="constant")
nov = np.array([np.sum(Rp[i:i + 2 * k, i:i + 2 * k] * g) for i in range(R.shape[0])])
nov = (nov - nov.min()) / (np.ptp(nov) + 1e-9)
bt = np.r_[0.0, beats][: len(nov)]
peaks = librosa.util.peak_pick(nov, pre_max=8, post_max=8, pre_avg=8, post_avg=8, delta=0.05, wait=8)
boundaries = [{"t": round(float(bt[p]), 2), "strength": round(float(nov[p]), 3)} for p in peaks if p < len(bt)]

res = {
    "duration": round(dur, 3),
    "tempo_bpm": float(np.atleast_1d(tempo)[0]),
    "beats": [round(float(b), 3) for b in beats],
    "onsets": [round(float(o), 3) for o in onsets],
    "rms_per_s": [round(v, 4) for v in per_second(rms)],
    "low_per_s": [round(v, 4) for v in per_second(low)],
    "voice_band_per_s": [round(v, 4) for v in per_second(mid_voice)],
    "section_boundaries": boundaries,
}
json.dump(res, open(out, "w"), indent=1)
print(f"durée {dur:.3f}s  tempo {res['tempo_bpm']:.1f} BPM  {len(beats)} temps  {len(onsets)} attaques")
print("frontières probables :", [(b["t"], b["strength"]) for b in boundaries])

if plot:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(4, 1, figsize=(22, 11), sharex=True)
    ax[0].plot(t, rms, lw=.6); ax[0].set_ylabel("RMS")
    ax[1].plot(t, low, lw=.6, c="tab:red"); ax[1].set_ylabel("grave 35-120 Hz")
    ax[2].plot(t, mid_voice, lw=.6, c="tab:green"); ax[2].set_ylabel("médium 250-3500")
    ax[3].plot(bt, nov, lw=.8, c="k"); ax[3].set_ylabel("nouveauté")
    for b in boundaries:
        for a in ax:
            a.axvline(b["t"], c="orange", lw=.8)
    ax[3].set_xticks(np.arange(0, dur, 5))
    for a in ax:
        a.grid(alpha=.3)
    plt.tight_layout(); plt.savefig(plot, dpi=70)
