#!/usr/bin/env bash
# Render every composition, normalise loudness to -14 LUFS (limiter target -2 dBTP,
# so the AAC output stays ≤ -1 dBTP) and keep
# each MP4 ≤ 25 MB (H.264, yuv420p, +faststart).
# Usage: scripts/render_all.sh [CompositionId ...]
set -euo pipefail
cd "$(dirname "$0")/.."
IDS=("$@")
[ ${#IDS[@]} -eq 0 ] && IDS=(Pitch-EN-16x9 Pitch-EN-1x1 Pitch-EN-9x16 Pitch-FR-16x9 Pitch-FR-1x1 Pitch-FR-9x16)
MAX_BYTES=$((24 * 1024 * 1024))
mkdir -p out
for id in "${IDS[@]}"; do
  raw="out/${id}.raw.mp4"
  final="out/${id}.mp4"
  echo "== ${id}: render"
  npx remotion render "$id" "$raw" --crf=14 --concurrency=4 --log=error
  echo "== ${id}: loudness pass 1"
  stats=$(ffmpeg -hide_banner -nostats -i "$raw" -vn -af loudnorm=I=-14:TP=-2:LRA=11:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
  get() { echo "$stats" | python3 -c "import json,sys; print(json.load(sys.stdin)['$1'])"; }
  LN="loudnorm=I=-14:TP=-2:LRA=11:measured_I=$(get input_i):measured_TP=$(get input_tp):measured_LRA=$(get input_lra):measured_thresh=$(get input_thresh):offset=$(get target_offset):linear=true"
  echo "== ${id}: encode (CRF 20)"
  ffmpeg -hide_banner -loglevel error -y -i "$raw" -c:v libx264 -preset slow -crf 20 -pix_fmt yuv420p \
    -af "$LN" -ar 48000 -c:a aac -b:a 192k -movflags +faststart "$final"
  size=$(stat -c %s "$final")
  if [ "$size" -gt "$MAX_BYTES" ]; then
    echo "== ${id}: $((size / 1048576)) MB > 24 MB -> two-pass at 2.1 Mb/s"
    ffmpeg -hide_banner -loglevel error -y -i "$raw" -c:v libx264 -preset slow -b:v 2100k -pass 1 -passlogfile "out/${id}" -an -f mp4 /dev/null
    ffmpeg -hide_banner -loglevel error -y -i "$raw" -c:v libx264 -preset slow -b:v 2100k -pass 2 -passlogfile "out/${id}" -pix_fmt yuv420p \
      -af "$LN" -ar 48000 -c:a aac -b:a 192k -movflags +faststart "$final"
    rm -f "out/${id}"-0.log*
  fi
  rm -f "$raw"
  echo "== ${id}: done $(du -h "$final" | cut -f1)"
done
