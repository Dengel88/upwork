#!/usr/bin/env bash
# Склейка клипов A-D в один 15с ролик 1080p без звука + вотермарк.
# Клипы стыкуются по общим ключевым кадрам, на стыке 4 кадра xfade, чтобы скрыть микроскачок.
set -euo pipefail
cd "$(dirname "$0")"
OUT=${OUT:-wisberg_screening_15s.mp4}
WM=${WM-}
CD=${CD:-clips}; W=${W:-1920}; H=${H:-1080}
clips=($CD/A.mp4 $CD/B.mp4 $CD/C.mp4 $CD/D.mp4)
present=(); for c in "${clips[@]}"; do [ -f "$c" ] && present+=("$c"); done
n=${#present[@]}; [ "$n" -ge 1 ] || { echo "no clips"; exit 1; }

inputs=(); for c in "${present[@]}"; do inputs+=(-i "$c"); done
F=0.16   # длительность кроссфейда, с
fc=""
for i in $(seq 0 $((n-1))); do
  fc+="[$i:v]scale=${W}:${H}:flags=lanczos,fps=24,format=yuv420p,setsar=1[v$i];"
done
prev="v0"; off=0
for i in $(seq 1 $((n-1))); do
  d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "${present[$((i-1))]}")
  off=$(python3 -c "print(round($off + $d - $F, 3))")
  fc+="[$prev][v$i]xfade=transition=fade:duration=$F:offset=$off[x$i];"
  prev="x$i"
done
if [ -n "$WM" ]; then
  fc+="[$prev]drawtext=text='$WM':fontcolor=white@0.55:fontsize=26:x=w-tw-36:y=h-th-30:shadowcolor=black@0.4:shadowx=1:shadowy=1[out]"
else
  fc+="[$prev]null[out]"
fi
ffmpeg -loglevel error -y "${inputs[@]}" -filter_complex "$fc" -map "[out]" -an \
  -c:v libx264 -preset slow -crf 14 -pix_fmt yuv420p -movflags +faststart "$OUT"
ffprobe -v error -show_entries format=duration:stream=width,height -of default=nw=1 "$OUT"
