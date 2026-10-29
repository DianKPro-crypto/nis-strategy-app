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
- **À l'heure :** Souleika brise le sceau de cire DK et la chanson démarre. La lettre se révèle au rythme du chant :
  le prénom sur « Souleika Queen », la ligne « Waan ku jeclahay » au moment où elle est chantée, avec des cœurs en
  feu d'artifice.
- **Ensuite :** le film « Nuit enchantée » (version téléphone), puis un bouton « Envoyer un baiser à Karim » qui
  ouvre WhatsApp.

| Fichier | Rôle |
|---|---|
| `carte/index.html` | la carte (code, textes, minutage sur le chant) |
| `carte/apercu.html` | image d'aperçu du lien WhatsApp (enveloppe scellée, sans photo) |
| `carte/build.py` | assemble le site dans `work/carte_site/` (portrait, extrait du chant, film, polices) |
| `carte/capture.js` | aperçu WhatsApp, captures iPhone et Android, vidéo de démonstration (`work/carte_qa/`) |

Le numéro WhatsApp est lu dans `carte/prive.json`, qui reste hors Git.

```bash
python3 carte/build.py --url https://<site>.netlify.app
node carte/capture.js
```

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
