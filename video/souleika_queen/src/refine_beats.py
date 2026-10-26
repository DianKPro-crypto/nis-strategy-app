"""Affinage de la grille rythmique : recale chaque temps sur l'attaque percussive la plus proche (±120 ms).

Usage : python3 src/refine_beats.py <audio.wav> <analysis.json>   (ajoute 'beats_refined' et 'accents' au JSON)
"""
import json
import sys

import librosa
import numpy as np

audio, path = sys.argv[1:3]
a = json.load(open(path))
y, sr = librosa.load(audio, sr=22050)
yh, yp = librosa.effects.hpss(y, margin=2.0)
hop = 110  # 5 ms
env = librosa.onset.onset_strength(y=yp, sr=sr, hop_length=hop, lag=1, max_size=3)
t = np.arange(len(env)) * hop / sr
beats = np.array(a["beats"])
ref, shifts = [], []
for b in beats:
    m = (t >= b - 0.12) & (t <= b + 0.12)
    i = np.where(m)[0]
    k = i[np.argmax(env[i])]
    # on ne recale que si l'attaque est nette ; sinon on garde le temps du suivi
    if env[k] > 0.25 * np.percentile(env, 99):
        ref.append(float(t[k])); shifts.append(float(t[k] - b))
    else:
        ref.append(float(b)); shifts.append(0.0)
ref = np.array(ref)
# accents forts (attaques percussives au-dessus du 97e centile)
thr = np.percentile(env, 97)
pk = librosa.util.peak_pick(env, pre_max=20, post_max=20, pre_avg=40, post_avg=40, delta=thr * 0.3, wait=40)
acc = [round(float(t[p]), 3) for p in pk if env[p] > thr]
a["beats_refined"] = [round(float(x), 3) for x in ref]
a["accents"] = acc
json.dump(a, open(path, "w"), indent=1)
s = np.array(shifts)
print(f"décalage médian {np.median(s)*1000:.0f} ms, |décalage| moyen {np.mean(np.abs(s))*1000:.0f} ms")
for lo, hi in [(0, 30), (30, 64), (62, 90), (90, 115), (115, 133), (133, 158), (158, 180)]:
    m = (beats >= lo) & (beats < hi)
    print(f"  {lo:5.0f}-{hi:5.0f}s : médian {np.median(s[m])*1000:+.0f} ms")
