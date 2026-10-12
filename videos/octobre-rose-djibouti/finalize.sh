#!/usr/bin/env bash
# Assemble rendered segments + Suno track into the two delivery files.
#   ./finalize.sh <audio.mp3>
set -euo pipefail
cd "$(dirname "$0")"
AUDIO="${1:-assets/ensemble_protegeons_la_vie.mp3}"
printf "file 'segA.mp4'\nfile 'segB.mp4'\n" > out/list.txt
ffmpeg -y -loglevel error -f concat -safe 0 -i out/list.txt -c copy out/video_60.mp4

# Master 60 fps (Reels / Shorts / projection)
ffmpeg -y -loglevel error -i out/video_60.mp4 -i "$AUDIO" -map 0:v -map 1:a:0 \
  -c:v libx264 -preset slow -crf 18 -profile:v high -level 4.2 -pix_fmt yuv420p \
  -color_primaries bt709 -color_trc bt709 -colorspace bt709 \
  -c:a aac -b:a 192k -ar 48000 -shortest -movflags +faststart \
  out/OctobreRose_Djibouti_2026_9x16_master60.mp4

# WhatsApp Status: 30 fps, <= 16 MB, two-pass
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 out/video_60.mp4)
VBR=$(python3 -c "print(int((15.2*8*1024*1024/${DUR} - 128000)/1000))")
ffmpeg -y -loglevel error -i out/video_60.mp4 -vf fps=30 -c:v libx264 -preset slow -b:v ${VBR}k -pass 1 -passlogfile out/x264 -an -f mp4 /dev/null
ffmpeg -y -loglevel error -i out/video_60.mp4 -i "$AUDIO" -map 0:v -map 1:a:0 -vf fps=30 \
  -c:v libx264 -preset slow -b:v ${VBR}k -maxrate $((VBR*2))k -bufsize $((VBR*4))k -pass 2 -passlogfile out/x264 \
  -profile:v high -level 4.0 -pix_fmt yuv420p -color_primaries bt709 -color_trc bt709 -colorspace bt709 \
  -c:a aac -b:a 128k -ar 44100 -shortest -movflags +faststart \
  out/OctobreRose_Djibouti_2026_9x16_WhatsApp.mp4
ls -la out/*.mp4
