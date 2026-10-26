#!/usr/bin/env bash
# Rendu de contrôle : 4 extraits (portrait horizontal en vertical, passage festif, pont spirituel, miroir final)
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p work/control
i=0
for seg in "28.5 37.0" "62.0 68.5" "113.0 121.5" "169.0 179.2"; do
  set -- $seg
  a=$(python3 -c "print(round($1*30))"); b=$(python3 -c "print(round($2*30))")
  python3 src/render.py --range $a $b --out work/control/v$i.mkv
  ffmpeg -v error -y -i work/control/v$i.mkv -ss $1 -to $2 -i sources/audio/SOULEIKA_QUEEN.mp3 \
    -map 0:v -map 1:a -c:v libx264 -crf 18 -preset fast -pix_fmt yuv420p -c:a aac -b:a 192k -shortest work/control/c$i.mp4
  echo "file 'c$i.mp4'" >> work/control/list.txt
  i=$((i+1))
done
ffmpeg -v error -y -f concat -safe 0 -i work/control/list.txt -c copy work/controle.mp4
ffprobe -v error -show_entries format=duration -of csv=p=0 work/controle.mp4
