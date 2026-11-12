# Le fil de la paix — clip 9:16 (motion design)

Chant soufi « Un fil de paix », signé Dian K. Pro. Format vertical 1080 × 1920, 30 i/s, 3 min 17,6 s.

## Livrables
| Fichier | Rôle |
| --- | --- |
| `Le_fil_de_la_paix_9x16.mp4` | Film final (H.264 yuv420p, AAC 48 kHz, faststart) |
| `Le_fil_de_la_paix_audio_edit.wav` | Montage sonore (chant intégral, aucune coupe) — régénéré par le script, non versionné |
| `Storyboard_final.csv` | 12 séquences, 39 plans, timecodes, paroles à l’écran |
| `Coupes_audio.csv` | Journal des coupes (aucune : durée source dans la cible) |
| `Planche_controle_9x16.jpg` | Planche de contrôle extraite du film rendu |
| `Le_fil_de_la_paix_paroles.srt` | Paroles calées (vers par vers) — non incrustées |

## Reproduire
```bash
python3 scripts/01_extract_vignettes.py          # 12 vignettes sans bordures ni numéros
python3 scripts/02_upscale.py RealESRGAN_x4plus.pth   # agrandissement local (CPU)
ffmpeg -i sources/Un_fil_de_paix.mp3 -c:a pcm_s16le -ar 48000 Le_fil_de_la_paix_audio_edit.wav
mkdir -p assets/audio && cp Le_fil_de_la_paix_audio_edit.wav assets/audio/
python3 scripts/03_assets.py                      # images du film + fonds
python3 scripts/04_build.py                       # index.html, compositions/, CSV, SRT
npx hyperframes check && npx hyperframes render -o work/render_9x16.mp4 -f 30
bash scripts/06_finalize.sh work/render_9x16.mp4  # encodage de livraison + contrôles
```
Tout le montage (plans, cadrages, paroles, timecodes) se règle dans `scripts/04_build.py`.

## Sources
`sources/a.png` photo du personnage principal · `sources/b.png` planche 01–12 · `sources/Un_fil_de_paix.mp3` chant Suno (197,59 s).
