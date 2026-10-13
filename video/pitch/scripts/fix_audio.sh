#!/usr/bin/env bash
# All versions share the same music mix. Re-normalise it once to -14 LUFS with a
# -2 dBTP limiter target (AAC encoding adds up to ~1 dB of overshoot, so the
# delivered files stay ≤ -1 dBTP) and remux it into every MP4 (video copied).
# Usage: scripts/fix_audio.sh [reference.mp4]
set -euo pipefail
cd "$(dirname "$0")/.."
ref="${1:-out/Pitch-EN-16x9.mp4}"
tmp=$(mktemp -d)
ffmpeg -hide_banner -loglevel error -y -i "$ref" -vn -c:a pcm_s24le "$tmp/mix.wav"
stats=$(ffmpeg -hide_banner -nostats -i "$tmp/mix.wav" -af loudnorm=I=-14:TP=-2:LRA=11:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
get() { echo "$stats" | python3 -c "import json,sys; print(json.load(sys.stdin)['$1'])"; }
ffmpeg -hide_banner -loglevel error -y -i "$tmp/mix.wav" \
  -af "loudnorm=I=-14:TP=-2:LRA=11:measured_I=$(get input_i):measured_TP=$(get input_tp):measured_LRA=$(get input_lra):measured_thresh=$(get input_thresh):offset=$(get target_offset):linear=true" \
  -ar 48000 -c:a aac -b:a 192k "$tmp/mix.m4a"
ffmpeg -hide_banner -nostats -i "$tmp/mix.m4a" -af ebur128=peak=true -f null - 2>&1 | grep -E "I:|Peak:" | tail -2
for f in out/Pitch-*.mp4; do
  ffmpeg -hide_banner -loglevel error -y -i "$f" -i "$tmp/mix.m4a" -map 0:v:0 -map 1:a:0 -c copy -shortest -movflags +faststart "$tmp/out.mp4"
  mv "$tmp/out.mp4" "$f"
  echo "remuxed $f"
done
rm -rf "$tmp"
