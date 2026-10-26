"""Transcription locale (faster-whisper small, CPU int8) pour vérifier ce qui est réellement chanté.

Usage : python3 src/transcribe.py <model_dir> <audio.wav> <out.json>
Aucune donnée n'est envoyée à l'extérieur : le modèle est chargé depuis un dossier local.
"""
import json
import sys

import numpy as np
from scipy.io import wavfile

from faster_whisper import WhisperModel

model_dir, audio, out = sys.argv[1:4]
sr, pcm = wavfile.read(audio)  # WAV mono 16 kHz préparé par ffmpeg
assert sr == 16000, sr
samples = pcm.astype(np.float32) / 32768.0
model = WhisperModel(model_dir, device="cpu", compute_type="int8", cpu_threads=4)

# Vocabulaire du chant pour guider la reconnaissance (noms propres, somali).
prompt = ("Souleika Soultan, Gacaliso, Dhalasho wacan, Hambalyo, Waan ku jeclahay, "
          "Djibouti, Bamako, Mali, Ambouli, Balbala, kora, Amapiano, Ya Allah.")

segments, info = model.transcribe(
    samples, language="fr", beam_size=5, word_timestamps=True,
    vad_filter=False, condition_on_previous_text=False, initial_prompt=prompt,
    no_speech_threshold=0.9,
)
res = []
for s in segments:
    res.append({
        "start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip(),
        "words": [{"w": w.word, "s": round(w.start, 2), "e": round(w.end, 2), "p": round(w.probability, 2)}
                  for w in (s.words or [])],
    })
    print(f"[{s.start:7.2f} → {s.end:7.2f}] {s.text.strip()}", flush=True)

json.dump({"language": info.language, "duration": info.duration, "segments": res},
          open(out, "w"), ensure_ascii=False, indent=1)
