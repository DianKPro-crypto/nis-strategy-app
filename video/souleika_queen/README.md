# SOULEIKA QUEEN — L’amour en lumière

Clip anniversaire (31 octobre) monté par programme à partir des photos et du chant fournis par Dr Dian Sidibé.
Format vertical 1080 × 1920, 30 i/s, H.264 + AAC. Durée 185,5 s : le chant complet (179,2 s) puis une fin en douceur
(queue de réverbération du chant, « Je te MOUA… » tenu, fondu au noir). Réglages de cette fin : `audio_ending` dans
`config/timeline.json`, rendu par `src/audio_master.py`.

## Deux versions

| Version | Commande | Sorties |
|---|---|---|
| Actuelle (« L'amour en lumière ») | `python3 src/export.py` | `exports/` |
| Nuit enchantée (« Il était une fois… ») | `python3 src/matte.py` puis `python3 src/export.py --style enchante` | `exports/enchante/` |

La version « Nuit enchantée » reprend exactement le même montage, les mêmes paroles et le même son. Elle remplace la
première version rêve (pastel), jugée décolorée.

**Ce qui change.** Chaque photo est séparée en deux calques par un détourage local (`src/matte.py`, modèle
BiRefNet-portrait exécuté sur cette machine, aucune photo envoyée à l'extérieur) :

- La personne garde ses pixels d'origine. Seul son étalonnage change, comme dans la version actuelle.
- Le décor change de lumière selon la séquence (nuit étoilée, crépuscule, heure dorée, bal royal, clair de lune,
  aurore, jardin de nuit) : profondeur de champ, lampes réelles devenues bokeh, couleurs riches et noirs profonds.
- La magie se place **derrière** elle : feux d'artifice éclatant sur les temps, lanternes célestes, étoiles,
  rayons de contre-jour.
- Elle passe aussi **devant** elle, pour la profondeur : spirales d'étincelles autour du buste, gerbes sur les
  coupes, cœur d'étoiles du baiser final. Ces éléments s'effacent toujours à l'approche des visages et des mains.
- Le décor glisse moins vite qu'elle, ce qui crée un effet de profondeur. Chaque calque ne subit qu'une échelle et
  une translation : aucune déformation.

Les objets à garder tels quels au premier plan (téléphone de la page d'accueil, bandeau « SOULEIKA ») sont déclarés
dans `config/photos.json` (`garder`).

Tout se règle dans `config/style_enchante.json` : mondes (lumière du décor), feux (instant, position, type),
spirales, lanternes, étoiles filantes, cœurs, parallaxe, finition. Moteur : `src/enchant.py`.

Contrôles propres à cette version :

- `python3 src/qc_enchante.py` : couleurs et contraste face à la version actuelle, calage des coupes, des feux
  et des spirales.
- `python3 src/compare.py` : planche avant/après.

## Carte surprise « L'Enveloppe enchantée »

Petite page web pour téléphone, partagée par WhatsApp, qui s'ouvre le 31 octobre à minuit (heure de Djibouti).

- **Avant l'heure :** un compte à rebours s'affiche sous l'enveloppe scellée.
- **À l'heure :** Souleika brise le sceau de cire DK. La voix de Karim lit la lettre sur un fond de kora, et chaque mot
  apparaît quand il est prononcé. Certains mots déclenchent la magie : « Souleika », « étoiles », « lanternes »,
  « feux d'artifice », « Waan ku jeclahay » (cœurs), puis la signature « Karim » scintille.
- **Ensuite :** le film « Nuit enchantée » (version téléphone). La chanson reste la surprise du film. Un bouton
  « Envoyer un baiser à Karim » ouvre WhatsApp ; « Relire ma lettre » rejoue la lecture (voix, kora, mots et magie).

Dans WhatsApp, le lien s'affiche avec une image figée (WhatsApp ne fait tourner aucune page dans la conversation) :
l'enveloppe scellée et « Touche pour voir le compte à rebours ». Le compte à rebours tourne en direct dès que le
lien est ouvert. Après un changement d'image d'aperçu, changer `?v=` dans `og:image` (carte/index.html) pour que
WhatsApp ne ressorte pas l'ancienne de son cache.

Sans enregistrement de voix, la lettre s'affiche mot à mot en silence, au rythme d'une lecture posée.

| Fichier | Rôle |
|---|---|
| `carte/index.html` | la carte (code, textes, effets déclenchés par les mots) |
| `carte/apercu.html` | image d'aperçu du lien WhatsApp (composée comme l'écran d'attente, sans photo) |
| `carte/teaser.html`, `carte/teaser.js` | animation de 5 s en boucle à envoyer juste avant le lien (étoiles, étoiles filantes, sceau qui brille) |
| `carte/build.py` | assemble le site dans `work/carte_site/` (portrait, voix de la lettre, film, polices) |
| `carte/capture.js` | aperçu WhatsApp, captures iPhone et Android, contrôle de synchronisation, démonstration (`work/carte_qa/`) |
| `carte/voix.py` | voix de Karim : instant de chaque mot (transcription locale, débuts re-mesurés), son de la carte |

Le numéro WhatsApp est lu dans `carte/prive.json`, qui reste hors Git.

```bash
python3 carte/voix.py --melange sources/audio/Soul-Kora.mp3   # voix + kora déjà mixées (Suno) : raccourcie, mots minutés
#   ou : python3 carte/voix.py voix_lettre.m4a kora.mp3       # voix seule, posée ici sur la kora
python3 carte/build.py --url https://lettre-souleika-2026.netlify.app
node carte/capture.js
python3 carte/build.py --zip exports/enchante/Carte_Souleika_Netlify.zip
node carte/teaser.js     # animation WhatsApp : Souleika_Animation_WhatsApp.gif (à envoyer tel quel) et .mp4
node carte/teaser.js --cycles 3   # boucle de 15 s : WhatsApp ne joue un GIF qu'une fois, à sa première apparition
```

Minutage des mots : la transcription locale donne l'instant de chaque mot, mais sur un fond musical elle avance
jusqu'à 2 s les mots dits après un silence. Le début de ces mots est donc re-mesuré par le modèle lui-même (on rend
muet le son juste avant le mot, de plus en plus loin, jusqu'à ce que le mot ne soit plus reconnu) ; le détail est
dans `work/carte_voix/alignement.txt`, et `node carte/capture.js` vérifie que chaque mot s'affiche quand le son
atteint son instant.

Le lien d'aperçu `?apercu=dk3110` ouvre la carte avant l'heure, pour les vérifications. Il ne doit jamais être transmis
à Souleika.

## Refaire le rendu

```bash
cd video/souleika_queen
pip install opencv-python-headless scipy librosa numpy pillow   # une seule fois
python3 src/export.py              # rendu complet + exports + planche + CSV + contrôle qualité (~15 min, 4 cœurs)
python3 src/export.py --encode     # ré-encoder et refaire les livrables sans recalculer les images
```

Les photos et le chant ne sont pas versionnés dans Git (confidentialité). Placez-les dans `sources/photos/` et
`sources/audio/` avec les noms indiqués dans `config/photos.json` et `config/timeline.json`.

## Modifier sans toucher au code

| Pour changer… | Fichier | Champ |
|---|---|---|
| un texte, sa position, son moment | `config/texts.json` | `lines[].text`, `pos`, `start`, `end` |
| un plan, sa photo, son minutage | `config/timeline.json` | `shots[].photo`, `start`, `end` |
| un cadrage | `config/timeline.json` | `z0`/`z1` (zoom), `c0`/`c1` (point de la photo au centre) |
| une transition | `config/timeline.json` | `trans` : `cut`, `dissolve`, `light`, `zoom` |
| l’ambiance d’une séquence | `config/timeline.json` | `sections` : étalonnage et effets |
| un point focal, une zone protégée | `config/photos.json` | `focus`, `protect` |

Vérifications rapides après modification :

```bash
python3 src/render.py --qc                    # textes : zone de sécurité, aucun texte sur visage/yeux/bouche/mains
python3 src/render.py --stills 0 64.2 121     # images de contrôle dans work/stills/ (ajouter --style enchante)
bash src/control.sh                           # extrait de contrôle de 34 s avec le son (work/controle.mp4)
```

## Organisation

```
config/    photos.json (identification, points focaux, zones protégées) · timeline.json (plans) · texts.json (textes)
src/       render.py (moteur) · photos.py (cadrage, calques) · fx.py (lumière, étalonnage) · textfx.py (typographie)
           enchant.py, matte.py, dream.py (version Nuit enchantée) · livefx.py (effets des photos artistiques)
           export.py (chaîne complète) · analyze_audio.py, refine_beats.py, transcribe.py (analyse du chant)
analysis/  analyse rythmique, transcription locale, paroles alignées, rapport de contrôle qualité
assets/    polices (Playfair Display, Inter — licence OFL) et monogramme DK
exports/   livrables
```

## Méthode de synchronisation

1. Transcription locale (faster-whisper small, CPU, aucun envoi externe) pour horodater les paroles réellement chantées.
2. Suivi du tempo (112,3 BPM) puis recalage de chaque temps sur l’attaque percussive la plus proche.
3. Coupes sur les temps forts mesurés (entrée du groove 29,50 s, refrain 63,80 s, refrain final 157,03 s) ;
   textes affichés au moment où le mot est chanté (`sung` dans `texts.json`).

L’enregistrement ne contient pas l’outro des paroles de référence. « Waan ku jeclahay » et « Je te MOUA… » sont donc
affichés en dédicace finale, sur la dernière phrase réellement chantée, sans prétendre à une synchronisation labiale.
