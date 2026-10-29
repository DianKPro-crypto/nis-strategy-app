"""Voix de Karim pour la carte : minutage de chaque mot de la lettre, puis le son de la carte.

Deux cas :
  python3 carte/voix.py <voix.m4a> [<kora.mp3>]       voix seule : nettoyée, puis posée sur la kora (atténuée sous la voix)
  python3 carte/voix.py --melange <voix_kora.mp3>     voix et kora déjà mixées (Suno) : la piste est raccourcie, pas remixée
puis : python3 carte/build.py --url https://lettre-souleika-2026.netlify.app
       node carte/capture.js --apercu
       python3 carte/build.py --zip exports/enchante/Carte_Souleika_Netlify.zip

Sorties dans work/carte_voix/ (hors Git) :
  lettre.mp3       la kora accompagne l'ouverture de l'enveloppe, la voix lit la lettre, la kora s'efface
  mots.json        instant de chaque mot de la carte (secondes depuis le début de lettre.mp3)
  alignement.txt   mot de la carte → mot entendu → instant, et comment il a été mesuré (contrôle)

Minutage : faster-whisper donne l'instant de chaque mot. Sur un fond musical, il avance jusqu'à 2 s les mots
dits après un silence (il leur attribue la pause) : le début de ces mots est re-mesuré par le même modèle.
On rend muet le son depuis le début présumé, de plus en plus loin ; tant que le mot n'est pas entamé, sa
probabilité ne bouge pas ; elle chute dès que le silence le mord (méthode « refine » de stable-ts). Un mot bref
que le contexte suffit à deviner (« Il », « Que ») est placé juste avant le mot suivant quand il ouvre une phrase
(règles détaillées dans instants()).
Tout reste sur cette machine : transcription sur CPU, aucun envoi externe.
"""
import argparse
import difflib
import json
import re
import subprocess
import unicodedata
from pathlib import Path

import numpy as np
from scipy.io import wavfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = ROOT / "work" / "carte_voix"
MODELE = ROOT / "work" / "models" / "whisper-small"
AVANT = 2.6        # voix seule : secondes de kora avant la première parole (ouverture de l'enveloppe)
APRES = 6.0        # voix seule : secondes de kora après la dernière parole
SIGNATURE = 1.2    # un mot écrit mais pas lu (la signature) apparaît 1,2 s après le dernier mot dit
HALLUCINATIONS = ("amara", "sous-titr")      # phrases que whisper invente sur la musique seule
SR = 16000


def mots_carte():
    """Mots de la carte dans l'ordre de lecture : data-lire (mot à mot) et data-mot (un mot) ;
    avec l'indice du premier mot de chaque élément (titre, prénom, ligne de la lettre, signature)."""
    html = (HERE / "index.html").read_text(encoding="utf-8")
    trouves = [(m.start(), m.group(2).split()) for m in re.finditer(r"<(\w+)[^>]*\bdata-lire\b[^>]*>([^<]*)</\1>", html)]
    trouves += [(m.start(), [m.group(1)]) for m in re.finditer(r'data-mot="([^"]+)"', html)]
    mots, tetes = [], set()
    for _, ws in sorted(trouves):
        tetes.add(len(mots))
        mots += ws
    return mots, tetes


def norme(w):
    w = unicodedata.normalize("NFKD", w.lower().replace("’", "'"))
    w = "".join(c for c in w if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9']", "", w)


def entendre(modele, pcm, carte):
    """Mots entendus [(mot, début, fin)] ; le texte de la carte guide la reconnaissance."""
    import ctranslate2
    ctranslate2.set_random_seed(31)           # nouvel essai à température plus haute quand un passage résiste : reproductible
    # no_speech_threshold relevé : sur la kora, le seuil par défaut (0,6) prend la fin de la lecture pour de la musique seule
    segs, _ = modele.transcribe(pcm, language="fr", beam_size=5, word_timestamps=True, no_speech_threshold=0.9,
                                condition_on_previous_text=False, initial_prompt=" ".join(carte))
    mots = []
    for s in segs:
        if any(h in s.text.lower() for h in HALLUCINATIONS):
            continue
        for w in s.words or []:
            texte = w.word.strip()
            if mots and texte[:1] in "'’-":                     # « t » + « 'accorde » → « t'accorde »
                mots[-1] = (mots[-1][0] + texte, mots[-1][1], w.end)
            else:
                mots.append((texte, w.start, w.end))
    return mots


def aligner(carte, entendus):
    """Alignement global (Needleman-Wunsch) tolérant aux mots mal transcrits : un mot de la carte peut répondre
    à deux mots entendus (« je » + « clahais » = jeclahay), qui sont alors réunis ; entre deux mots sûrs, autant
    de mots de part et d'autre se répondent dans l'ordre (somali entendu comme du français : « Moins que » = Waan ku).
    Renvoie {indice du mot de la carte: indice du mot entendu} et la liste des mots entendus (réunis)."""
    a, b = [norme(w) for w in carte], [norme(w) for w, _, _ in entendus]
    n, m, gap = len(a), len(b), -0.45
    r = lambda x, y: difflib.SequenceMatcher(None, x, y).ratio()
    sim = np.array([[r(x, y) for y in b] for x in a])
    sim2 = np.array([[r(x, b[j] + b[j + 1]) if j + 1 < m else 0.0 for j in range(m)] for x in a])
    S = np.zeros((n + 1, m + 1))
    P = np.zeros((n + 1, m + 1), np.int8)
    S[1:, 0] = gap * np.arange(1, n + 1)
    S[0, 1:] = gap * np.arange(1, m + 1)
    P[1:, 0], P[0, 1:] = 1, 2
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            opts = (S[i - 1, j - 1] + 2 * sim[i - 1, j - 1] - 0.8, S[i - 1, j] + gap, S[i, j - 1] + gap,
                    S[i - 1, j - 2] + 2 * sim2[i - 1, j - 2] - 0.8 + gap / 2 if j > 1 else -np.inf)
            k = int(np.argmax(opts))
            S[i, j], P[i, j] = opts[k], k
    paires, doubles, i, j = {}, [], n, m
    while i > 0 or j > 0:
        k = P[i, j] if i > 0 and j > 0 else (1 if i > 0 else 2)
        if k == 0:
            if sim[i - 1, j - 1] >= 0.45:
                paires[i - 1] = j - 1
            i, j = i - 1, j - 1
        elif k == 3:
            if sim2[i - 1, j - 2] >= 0.45:
                doubles.append(j - 2)
            i, j = i - 1, j - 2
        elif k == 1:
            i -= 1
        else:
            j -= 1
    if doubles:                                   # deux mots entendus pour un mot de la carte : réunis, puis réalignés
        entendus = list(entendus)
        for j in sorted(doubles, reverse=True):
            entendus[j:j + 2] = [(entendus[j][0] + entendus[j + 1][0], entendus[j][1], entendus[j + 1][2])]
        return aligner(carte, entendus)
    bornes = [(-1, -1)] + sorted(paires.items()) + [(n, m)]
    for (i0, j0), (i1, j1) in zip(bornes, bornes[1:]):
        nc, nh = i1 - i0 - 1, j1 - j0 - 1
        if nc > 0 and nh > 0 and (nc == nh or i1 == n):       # en fin de lettre, la signature peut ne pas être lue
            for d in range(min(nc, nh)):
                paires[i0 + 1 + d] = j0 + 1 + d
    return paires, entendus


def affiner(modele, pcm, entendus, paires, chute=1.2):
    """Plages de 0,5 s ou plus (une pause y est peut-être comptée) : son rendu muet depuis le début de la plage,
    de 0,25 s en 0,25 s puis au 1/6 du pas, jusqu'à ce que le mot cesse d'être reconnu (± 0,04 s). On s'arrête
    0,12 s avant la fin de la plage pour ne pas entamer le mot suivant.
    Renvoie {indice du mot entendu: (début de plage, fin de plage, instant mesuré ou None si le contexte
    suffit au modèle pour deviner le mot sans l'entendre)}."""
    from faster_whisper.tokenizer import Tokenizer
    tok = Tokenizer(modele.hf_tokenizer, modele.model.is_multilingual, task="transcribe", language="fr")

    def logp(signaux, ids, n0, n1):
        feats = []
        for x in signaux:
            f = modele.feature_extractor(x)
            feats.append(np.pad(f, ((0, 0), (0, max(0, 3000 - f.shape[1]))))[:, :3000])
        res = modele.model.align(modele.encode(np.stack(feats).astype(np.float32)), tok.sot_sequence,
                                 [ids] * len(signaux), [min(3000, len(x) // 160) for x in signaux])
        return [float(np.log(np.maximum(r.text_token_probs[n0:n1], 1e-9)).sum()) for r in res]

    retenus = sorted(paires.values())
    mesures = {}
    for k, j in enumerate(retenus):
        prec = retenus[k - 1] if k else -1
        s0, e0 = entendus[prec + 1][1], entendus[j][2]      # mots entendus en trop juste avant : même plage
        if e0 - s0 < 0.5:
            continue
        ja = max(0, min(j, prec + 1) - 3)                   # contexte : quelques mots autour, moins de 30 s
        a = max(0.0, entendus[ja][1] - 0.15)
        jb = max(i for i in range(j, min(len(entendus), j + 5)) if i == j or entendus[i][2] + 0.3 - a <= 29.5)
        b = entendus[jb][2] + 0.3
        ids, n0, n1 = [], 0, 0
        for i in range(ja, jb + 1):
            t = tok.encode(" " + entendus[i][0])
            if i == j:
                n0, n1 = len(ids), len(ids) + len(t)
            ids += t
        base = pcm[int(a * SR):int(b * SR)]

        def muet(ts):                             # son rendu muet de s0 à t, pour chaque t
            signaux = []
            for t in ts:
                x = base.copy()
                x[int((s0 - a) * SR):int((t - a) * SR)] = 0
                signaux.append(x)
            return [s for c in range(0, len(signaux), 8) for s in logp(signaux[c:c + 8], ids, n0, n1)]

        fin = e0 - 0.12
        grille, haut, debut, mesure = [s0, *np.arange(s0 + 0.25, fin, 0.25), fin], -np.inf, s0, None
        for passe in range(2):
            coupe = None
            for t, s in zip(grille, muet(grille)):
                if s < haut - chute:              # le silence vient de mordre sur le mot
                    coupe = t
                    break
                haut, debut = max(haut, s), t
            if coupe is None:
                break
            mesure = debut
            grille = list(np.linspace(debut, coupe, 7)[1:-1])
        mesures[j] = (s0, e0, None if mesure is None else round(float(debut), 3))
    return mesures


def instants(carte, tetes, entendus, paires, mesures):
    """Instant de chaque mot de la carte, et comment il a été établi.
    Mot entendu : début donné par whisper, sauf
      - si la mesure (affiner) le place 0,5 s ou plus après le début de sa plage : une pause y était comptée ;
        la mesure tombe en moyenne 0,05 s après le vrai début (contrôlé au spectrogramme) ;
      - si le modèle devine le mot sans l'entendre et que le mot ouvre une phrase : mot bref dit juste avant
        le suivant, placé avant la fin de sa plage selon sa longueur.
    Mot non entendu : juste avant le mot suivant (pas au milieu d'une pause) ; la signature non lue,
    1,2 s après le dernier mot dit."""
    t, notes = [None] * len(carte), [""] * len(carte)
    for i, j in paires.items():
        t[i], notes[i] = entendus[j][1], f"whisper {entendus[j][1]:6.2f} s"
        if j not in mesures:
            continue
        s0, e0, m = mesures[j]
        k = max((x for x in paires if x < i), default=-1)
        tete = k < 0 or any(x in tetes for x in range(k + 1, i + 1)) or carte[k].endswith((".", "…", "!", "?"))
        if m is not None and m - s0 >= 0.5:
            t[i] = m - 0.05
            notes[i] += f", pause comptée dans le mot : début mesuré {t[i]:6.2f} s"
        elif m is None and tete:
            t[i] = max(s0, e0 - 0.12 - 0.045 * len(norme(carte[i])))
            notes[i] += f", deviné par le contexte en tête de phrase : juste avant le mot suivant {t[i]:6.2f} s"
        elif s0 < entendus[j][1]:
            t[i] = s0
            notes[i] += f", plage commencée à {s0:6.2f} s (mot entendu en trop)"
    connus = [i for i, v in enumerate(t) if v is not None]
    assert connus, "aucun mot reconnu : vérifier l'enregistrement"
    for i in range(len(t)):
        if t[i] is None:
            avant = max((k for k in connus if k < i), default=None)
            apres = min((k for k in connus if k > i), default=None)
            if avant is None:
                t[i] = t[apres] - 0.4 * (apres - i)
            elif apres is None:
                t[i] = t[avant] + SIGNATURE * (i - avant)
            else:                                 # juste avant le mot suivant, pas au milieu d'une pause
                t[i] = max(t[avant] + (t[apres] - t[avant]) * (i - avant) / (apres - avant), t[apres] - 0.22 * (apres - i))
            notes[i] = "non entendu : " + ("signature, après le dernier mot dit" if apres is None else "juste avant le mot suivant")
    for i in range(1, len(t)):                    # jamais de retour en arrière
        t[i] = max(t[i], t[i - 1] + 0.05)
    return t, notes


def coupes(chemin, premier, dernier):
    """Raccourcir une piste mixée sans heurt : début sur l'attaque de kora la plus nette 2,6 à 4 s avant
    la première parole, fin au creux musical le plus calme 14 à 20 s après la dernière."""
    import librosa
    y, sr = librosa.load(str(chemin), sr=22050, mono=True)
    hop = 256
    rms = librosa.feature.rms(y=y, frame_length=1024, hop_length=hop)[0]
    db = 20 * np.log10(rms + 1e-9)
    fr = lambda s: int(s * sr / hop)
    attaques = librosa.onset.onset_detect(y=y, sr=sr, hop_length=hop, units="time", backtrack=True)
    cand = [a for a in attaques if premier - 4.0 <= a <= premier - 2.6]
    if cand:
        a = max(cand, key=lambda x: db[fr(x):fr(x + 0.15)].max() - db[fr(x - 0.3):fr(x)].mean()) - 0.03
    else:
        a = premier - 3.0
    lisse = np.convolve(db, np.ones(fr(0.3)) / fr(0.3), "same")
    zone = slice(fr(dernier + 14), min(len(lisse), fr(dernier + 20)))
    b = (zone.start + int(np.argmin(lisse[zone]))) * hop / sr if zone.start < len(lisse) else len(y) / sr
    return round(float(a), 3), round(float(min(b, len(y) / sr)), 3), not cand


def run(cmd):
    subprocess.run([str(c) for c in cmd], check=True)


def main():
    ap = argparse.ArgumentParser(description="Voix de Karim : minutage des mots et son de la carte")
    ap.add_argument("voix", help="voix seule, ou piste voix + kora avec --melange")
    ap.add_argument("kora", nargs="?", help="fond de kora à poser sous la voix seule")
    ap.add_argument("--melange", action="store_true", help="voix et kora déjà mixées : raccourcir sans remixer")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    source = Path(args.voix)
    if not args.melange:
        # voix nettoyée : grave inutile coupé, souffle atténué, dynamique tenue, niveau de parole
        propre = OUT / "voix_propre.wav"
        run(["ffmpeg", "-v", "error", "-y", "-i", source, "-ac", "1", "-ar", "48000", "-af",
             "highpass=f=80,afftdn=nf=-25,acompressor=threshold=-20dB:ratio=3:attack=10:release=160:makeup=2,"
             "loudnorm=I=-16:TP=-1.5:LRA=7", propre])
        source = propre
    run(["ffmpeg", "-v", "error", "-y", "-i", source, "-map", "0:a", "-ac", "1", "-ar", str(SR), OUT / "voix16k.wav"])
    _, pcm = wavfile.read(OUT / "voix16k.wav")
    pcm = pcm.astype(np.float32) / 32768

    from faster_whisper import WhisperModel
    carte, tetes = mots_carte()
    modele = WhisperModel(str(MODELE), device="cpu", compute_type="int8", cpu_threads=4)
    entendus = entendre(modele, pcm, carte)
    (OUT / "transcription.json").write_text(json.dumps(entendus, ensure_ascii=False), encoding="utf-8")
    paires, entendus = aligner(carte, entendus)
    mesures = affiner(modele, pcm, entendus, paires)
    t, notes = instants(carte, tetes, entendus, paires, mesures)
    dits = [t[i] for i in paires]

    if args.melange:
        # la piste est gardée telle quelle (voix et kora de Karim) : seulement raccourcie, fondus aux coupes
        debut, fin, approx = coupes(source, min(dits), max(dits))
        duree = fin - debut
        run(["ffmpeg", "-v", "error", "-y", "-i", source, "-map", "0:a", "-af",
             f"atrim={debut}:{fin},asetpts=PTS-STARTPTS,afade=t=in:d={1.5 if approx else 0.03},"
             f"afade=t=out:st={duree - 3:.3f}:d=3", "-c:a", "libmp3lame", "-b:a", "128k", "-ar", "44100", "-ac", "2",
             OUT / "lettre.mp3"])
        mots = [round(x - debut, 3) for x in t]
        bilan = f"lettre.mp3 : {duree:.1f} s (extrait {debut:.2f} → {fin:.2f} s de la piste)"
    else:
        debut = max(0.0, min(t[0], entendus[0][1]) - 0.3)            # silence de tête retiré
        fin = max(e for _, _, e in entendus) + 1.2
        duree = fin - debut
        total = AVANT + duree + APRES
        # mélange : la kora s'installe, baisse quand la voix parle, puis s'efface
        voix_seule = (f"[0:a]atrim={debut:.3f}:{fin:.3f},asetpts=PTS-STARTPTS,"
                      f"adelay={int(AVANT * 1000)}|{int(AVANT * 1000)},apad=whole_dur={total:.3f}[v]")
        if args.kora:
            filtre = (f"{voix_seule};[v]asplit=2[v1][v2];"
                      f"[1:a]aformat=channel_layouts=stereo,atrim=0:{total:.3f},loudnorm=I=-26:TP=-3,"
                      f"afade=t=in:d=2.2,afade=t=out:st={total - 5:.3f}:d=5[k];"
                      f"[k][v1]sidechaincompress=threshold=0.02:ratio=5:attack=30:release=500[kd];"
                      f"[kd][v2]amix=inputs=2:normalize=0,alimiter=limit=0.89[m]")
            entrees = ["-i", source, "-stream_loop", "-1", "-i", args.kora]
        else:
            filtre = f"{voix_seule};[v]anull[m]"
            entrees = ["-i", source]
        run(["ffmpeg", "-v", "error", "-y", *entrees, "-filter_complex", filtre, "-map", "[m]", "-t", f"{total:.3f}",
             "-c:a", "libmp3lame", "-b:a", "128k", "-ar", "44100", "-ac", "2", OUT / "lettre.mp3"])
        mots = [round(AVANT + x - debut, 3) for x in t]
        bilan = f"lettre.mp3 : {total:.1f} s (voix {duree:.1f} s)"

    (OUT / "mots.json").write_text(json.dumps({"mots": mots}, ensure_ascii=False), encoding="utf-8")
    lignes = [f"{w:16s} → {entendus[paires[i]][0] if i in paires else '—':16s} {mots[i]:7.2f} s   ({notes[i]})"
              for i, w in enumerate(carte)]
    (OUT / "alignement.txt").write_text("\n".join(lignes) + "\n", encoding="utf-8")
    print("\n".join(lignes))
    corriges = sum(", pause" in n or ", deviné" in n for n in notes)
    print(f"{len(paires)}/{len(carte)} mots entendus, {len(mesures)} plages sondées, {corriges} débuts corrigés ; {bilan}")


if __name__ == "__main__":
    main()
