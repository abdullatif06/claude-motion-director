#!/usr/bin/env bash
# Put the mixed soundtrack onto one or more rendered videos (video stream copied, no re-encode).
# Usage (from the project root): bash <skill>/scripts/audio/mux.sh out/vertical.mp4 [out/wide.mp4 ...]
# Each input gets a sibling with sound: out/vertical.mp4 -> out/vertical.final.mp4
set -euo pipefail
[ -f out/mix.wav ] || { echo "out/mix.wav missing: run mix.py first" >&2; exit 1; }
[ "$#" -ge 1 ] || { echo "Usage: mux.sh <video.mp4> [more.mp4 ...]" >&2; exit 1; }
for V in "$@"; do
  OUT="${V%.mp4}.final.mp4"
  ffmpeg -v error -y -i "$V" -i out/mix.wav -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 256k -shortest "$OUT"
  echo "wrote $OUT"
done
