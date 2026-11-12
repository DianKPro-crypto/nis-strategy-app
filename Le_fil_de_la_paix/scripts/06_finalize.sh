#!/usr/bin/env bash
# Encodage de livraison + controles. Usage : bash scripts/06_finalize.sh work/render_9x16.mp4
set -euo pipefail
IN="$1"; OUT=Le_fil_de_la_paix_9x16.mp4
ffmpeg -v error -y -i "$IN" -i Le_fil_de_la_paix_audio_edit.wav -map 0:v:0 -map 1:a:0 \
  -c:v libx264 -preset slow -crf 19 -pix_fmt yuv420p -r 30 -vsync cfr -profile:v high -level 4.2 \
  -c:a aac -b:a 256k -ar 48000 -ac 2 -movflags +faststart -t 197.6 "$OUT"
ffprobe -v error -show_entries format=duration,size:stream=codec_name,width,height,pix_fmt,r_frame_rate,avg_frame_rate,sample_rate -of default=nw=1 "$OUT"
echo "--- images noires (hors fondu final) :"
ffmpeg -v info -i "$OUT" -vf "blackdetect=d=0.2:pix_th=0.08" -an -f null - 2>&1 | grep blackdetect || echo "aucune"
echo "--- silences :"
ffmpeg -v info -i "$OUT" -af "silencedetect=n=-50dB:d=0.4" -vn -f null - 2>&1 | grep silence_ || echo "aucun"
rm -rf work/qc && mkdir -p work/qc
python3 - <<'P'
import csv, subprocess
r = list(csv.DictReader(open('Storyboard_final.csv', encoding='utf-8-sig')))
ts = [0.0] + [round(float(x['debut_s']) + 0.7 * float(x['duree_s']), 2) for x in r][1:] + [192.5, 197.2]
for t in ts:
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(t), '-i', 'Le_fil_de_la_paix_9x16.mp4', '-frames:v', '1', '-q:v', '3', f'work/qc/f_{t:07.2f}.jpg'], check=True)
P
python3 scripts/05_sheet.py work/qc work/qc/sheet 14 200
python3 - <<'P'
import cv2, glob, numpy as np
s = [cv2.imread(f) for f in sorted(glob.glob('work/qc/sheet_*.jpg'))]
w = max(i.shape[1] for i in s); s = [cv2.copyMakeBorder(i, 0, 0, 0, w - i.shape[1], cv2.BORDER_CONSTANT, value=(12, 12, 12)) for i in s]
cv2.imwrite('Planche_controle_9x16.jpg', np.vstack(s), [cv2.IMWRITE_JPEG_QUALITY, 88])
P
echo "planche : Planche_controle_9x16.jpg"
