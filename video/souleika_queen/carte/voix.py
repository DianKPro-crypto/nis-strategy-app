"""Voix de Karim pour la carte : nettoyage, minutage de chaque mot, mélange avec un fond de kora.

Usage :
  python3 carte/voix.py <voix.m4a> [<kora.mp3>]
puis : python3 carte/build.py --url https://lettre-souleika-2026.netlify.app
       node carte/capture.js --apercu
       python3 carte/build.py --zip exports/enchante/Carte_Souleika_Netlify.zip

Sorties dans work/carte_voix/ (hors Git) :
  lettre.mp3   la kora s'installe pendant l'ouverture de l'enveloppe, la voix lit la lettre, la kora s'efface
  mots.json    instant de chaque mot de la carte (secondes depuis le début de lettre.mp3)
  alignement.txt   mot de la carte → mot entendu → instant (contrôle)
Tout reste sur cette machine : transcription faster-whisper sur CPU, aucun envoi externe.
"""
import difflib
import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

import numpy as np
from scipy.io import wavfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = ROOT / "work" / "carte_voix"
MODELE = ROOT / "work" / "models" / "whisper-small"
AVANT = 2.6        # secondes de kora avant la première parole (ouverture de l'enveloppe)
APRES = 6.0        # secondes de kora après la dernière parole


def mots_carte():
    """Mots de la carte dans l'ordre de lecture : data-lire (mot à mot) et data-mot (un mot)."""
    html = (HERE / "index.html").read_text(encoding="utf-8")
    trouves = [(m.start(), m.group(2).split()) for m in re.finditer(r"<(\w+)[^>]*\bdata-lire\b[^>]*>([^<]*)</\1>", html)]
    trouves += [(m.start(), [m.group(1)]) for m in re.finditer(r'data-mot="([^"]+)"', html)]
    return [w for _, ws in sorted(trouves) for w in ws]


def norme(w):
    w = unicodedata.normalize("NFKD", w.lower().replace("’", "'"))
    w = "".join(c for c in w if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9']", "", w)


def aligner(carte, entendus):
    """Alignement global (Needleman-Wunsch) tolérant aux mots mal transcrits (somali, élisions)."""
    a, b = [norme(w) for w in carte], [norme(w) for w, _ in entendus]
    n, m, gap = len(a), len(b), -0.45
    S = np.zeros((n + 1, m + 1))
    P = np.zeros((n + 1, m + 1), np.int8)
    S[1:, 0] = gap * np.arange(1, n + 1)
    S[0, 1:] = gap * np.arange(1, m + 1)
    P[1:, 0], P[0, 1:] = 1, 2
    sim = np.zeros((n, m))
    for i in range(n):
        for j in range(m):
            sim[i, j] = difflib.SequenceMatcher(None, a[i], b[j]).ratio()
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            opts = (S[i - 1, j - 1] + 2 * sim[i - 1, j - 1] - 0.8, S[i - 1, j] + gap, S[i, j - 1] + gap)
            k = int(np.argmax(opts))
            S[i, j], P[i, j] = opts[k], k
    paires, i, j = {}, n, m
    while i > 0 or j > 0:
        k = P[i, j] if i > 0 and j > 0 else (1 if i > 0 else 2)
        if k == 0:
            if sim[i - 1, j - 1] >= 0.45:
                paires[i - 1] = j - 1
            i, j = i - 1, j - 1
        elif k == 1:
            i -= 1
        else:
            j -= 1
    return paires


def instants(carte, entendus, paires):
    """Instant de chaque mot de la carte ; les mots non reconnus sont placés entre leurs voisins."""
    t = [entendus[paires[i]][1] if i in paires else None for i in range(len(carte))]
    connus = [i for i, v in enumerate(t) if v is not None]
    assert connus, "aucun mot reconnu : vérifier l'enregistrement"
    for i in range(len(t)):
        if t[i] is None:
            avant = max((k for k in connus if k < i), default=None)
            apres = min((k for k in connus if k > i), default=None)
            if avant is None:
                t[i] = t[apres] - 0.4 * (apres - i)
            elif apres is None:
                t[i] = t[avant] + 0.45 * (i - avant)
            else:
                t[i] = t[avant] + (t[apres] - t[avant]) * (i - avant) / (apres - avant)
    for i in range(1, len(t)):                       # jamais de retour en arrière
        t[i] = max(t[i], t[i - 1] + 0.05)
    return t


def run(cmd):
    subprocess.run([str(c) for c in cmd], check=True)


def main():
    voix = Path(sys.argv[1])
    kora = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    OUT.mkdir(parents=True, exist_ok=True)
    propre = OUT / "voix_propre.wav"
    # 1. voix nettoyée : grave inutile coupé, souffle atténué, dynamique tenue, niveau de parole
    run(["ffmpeg", "-v", "error", "-y", "-i", voix, "-ac", "1", "-ar", "48000", "-af",
         "highpass=f=80,afftdn=nf=-25,acompressor=threshold=-20dB:ratio=3:attack=10:release=160:makeup=2,"
         "loudnorm=I=-16:TP=-1.5:LRA=7", propre])
    # 2. transcription locale avec l'heure de chaque mot (le texte de la carte guide la reconnaissance)
    run(["ffmpeg", "-v", "error", "-y", "-i", propre, "-ac", "1", "-ar", "16000", OUT / "voix16k.wav"])
    sr, pcm = wavfile.read(OUT / "voix16k.wav")
    from faster_whisper import WhisperModel
    carte = mots_carte()
    modele = WhisperModel(str(MODELE), device="cpu", compute_type="int8", cpu_threads=4)
    segs, _ = modele.transcribe(pcm.astype(np.float32) / 32768, language="fr", beam_size=5, word_timestamps=True,
                                condition_on_previous_text=False, initial_prompt=" ".join(carte))
    entendus = [(w.word.strip(), w.start) for s in segs for w in (s.words or [])]
    paires = aligner(carte, entendus)
    t = instants(carte, entendus, paires)
    debut = max(0.0, min(t[0], entendus[0][1]) - 0.3)            # silence de tête retiré
    fin = max(w for _, w in entendus) + 1.2
    duree = fin - debut
    # 3. mélange : la kora s'installe, baisse quand la voix parle, puis s'efface
    total = AVANT + duree + APRES
    voix_seule = f"[0:a]atrim={debut:.3f}:{fin:.3f},asetpts=PTS-STARTPTS,adelay={int(AVANT * 1000)}|{int(AVANT * 1000)},apad=whole_dur={total:.3f}[v]"
    if kora:
        filtre = (f"{voix_seule};[v]asplit=2[v1][v2];"
                  f"[1:a]aformat=channel_layouts=stereo,atrim=0:{total:.3f},loudnorm=I=-26:TP=-3,"
                  f"afade=t=in:d=2.2,afade=t=out:st={total - 5:.3f}:d=5[k];"
                  f"[k][v1]sidechaincompress=threshold=0.02:ratio=5:attack=30:release=500[kd];"
                  f"[kd][v2]amix=inputs=2:normalize=0,alimiter=limit=0.89[m]")
        entrees = ["-i", propre, "-stream_loop", "-1", "-i", kora]
    else:
        filtre = f"{voix_seule};[v]anull[m]"
        entrees = ["-i", propre]
    run(["ffmpeg", "-v", "error", "-y", *entrees, "-filter_complex", filtre, "-map", "[m]", "-t", f"{total:.3f}",
         "-c:a", "libmp3lame", "-b:a", "128k", "-ar", "44100", "-ac", "2", OUT / "lettre.mp3"])
    mots = [round(AVANT + x - debut, 3) for x in t]
    (OUT / "mots.json").write_text(json.dumps({"mots": mots}, ensure_ascii=False), encoding="utf-8")
    lignes = [f"{w:16s} → {entendus[paires[i]][0] if i in paires else '(placé entre ses voisins)':20s} {mots[i]:7.2f} s"
              for i, w in enumerate(carte)]
    (OUT / "alignement.txt").write_text("\n".join(lignes) + "\n", encoding="utf-8")
    print("\n".join(lignes))
    print(f"{len(paires)}/{len(carte)} mots reconnus ; lettre.mp3 : {total:.1f} s (voix {duree:.1f} s)")


if __name__ == "__main__":
    main()
