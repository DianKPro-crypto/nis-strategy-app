#!/bin/bash
set -e
cd /home/user/nis-strategy-app/video/dian-k-pro-promo
export NODE_PATH=$(npm root -g)
for L in fr en; do
  D=$( [ $L = en ] && echo 46.4 || echo 53.6 )
  LU=$(echo $L | tr a-z A-Z)
  node render/render.js --lang $L --fmt h --fps 30 --dur $D --workers 4 --audio audio/final_${L}_h.wav --out build/final/DianKPro_${LU}_16x9.mp4
  node render/render.js --lang $L --fmt v --fps 30 --dur $D --workers 4 --audio audio/final_${L}_v.wav --out build/final/DianKPro_${LU}_9x16.mp4
done
echo TERMINE
