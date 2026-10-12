#!/usr/bin/env bash
# Splice re-rendered passages into an existing 60 fps render without re-rendering the whole film.
#   ./patch.sh <in.mp4> <out.mp4> <patch.mp4>:<start_s> [...]
set -euo pipefail
IN=$1; OUT=$2; shift 2
inputs=(-i "$IN"); filt=""; segs=""; cur=0; n=0; k=1
for p in "$@"; do
  file=${p%%:*}; start=$(python3 -c "print(round(${p#*:}*60))")
  frames=$(ffprobe -v error -count_frames -select_streams v -show_entries stream=nb_read_frames -of csv=p=0 "$file")
  inputs+=(-i "$file")
  filt+="[0:v]trim=start_frame=${cur}:end_frame=${start},setpts=PTS-STARTPTS[s$n];[${k}:v]setpts=PTS-STARTPTS[p$n];"
  segs+="[s$n][p$n]"; cur=$((start+frames)); n=$((n+1)); k=$((k+1))
done
filt+="[0:v]trim=start_frame=${cur},setpts=PTS-STARTPTS[tail];${segs}[tail]concat=n=$((2*n+1)):v=1:a=0[v]"
ffmpeg -y -loglevel error "${inputs[@]}" -filter_complex "$filt" -map "[v]" -c:v libx264 -preset medium -crf 12 -pix_fmt yuv420p "$OUT"
