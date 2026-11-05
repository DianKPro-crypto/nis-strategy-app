#!/usr/bin/env bash
# Finalisation : grain très léger + encodage H.264 yuv420p + audio original en AAC 320k.
# L'audio est repris directement du fichier source (aucune modification de la chanson).
set -euo pipefail
cd "$(dirname "$0")/.."
AUDIO=project/public/audio/ici_commence_le_voyage.mp3
for f in 16x9 9x16; do
  ffmpeg -hide_banner -y -i "exports/_raw_${f}.mp4" -i "$AUDIO" \
    -map 0:v:0 -map 1:a:0 \
    -vf "noise=c0s=5:c0f=t+u" \
    -c:v libx264 -preset slow -crf 17 -profile:v high -pix_fmt yuv420p -r 25 \
    -c:a aac -b:a 320k -ar 48000 \
    -movflags +faststart -t 266.28 \
    -metadata title="Ici commence le voyage" \
    "exports/Ici_commence_le_voyage_${f}.mp4"
done
