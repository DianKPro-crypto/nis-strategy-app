# SOULEIKA QUEEN — L’amour en lumière

Clip anniversaire (31 octobre) monté par programme à partir des photos et du chant fournis par Dr Dian Sidibé.
Format vertical 1080 × 1920, 30 i/s, H.264 + AAC, durée calée sur l’enregistrement (179,2 s).

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
python3 src/render.py --stills 0 64.2 121     # images de contrôle dans work/stills/
bash src/control.sh                           # extrait de contrôle de 34 s avec le son (work/controle.mp4)
```

## Organisation

```
config/    photos.json (identification, points focaux, zones protégées) · timeline.json (plans) · texts.json (textes)
src/       render.py (moteur) · photos.py (cadrage) · fx.py (lumière, étalonnage) · textfx.py (typographie)
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
