#!/usr/bin/env bash
# Stills preview: capture a few frames BEFORE any full render and tile them into one sheet.
# Catching a problem on a still takes 2 minutes; catching it on a full render costs a re-render.
# Usage (from the project root):
#   bash <skill>/scripts/review/stills.sh              -> 4 evenly spaced stills
#   bash <skill>/scripts/review/stills.sh 2 8 14 20    -> stills at those BEATS
# Writes out/review/stills/*.png and out/review/stills.png
set -euo pipefail
HF_VERSION="${HF_VERSION:-0.8.86}"
OUTDIR=out/review/stills
rm -rf "$OUTDIR"; mkdir -p "$OUTDIR"

TIMES=$(node -e '
const c = require("./project.json");
const bpm = c.bpm || 120, off = c.beatOffset || 0, dur = c.duration;
const beats = process.argv.slice(1).map(Number);
const ts = beats.length ? beats.map(b => off + b * 60 / bpm)
                        : [0.15, 0.4, 0.65, 0.9].map(p => p * dur);
console.log(ts.map(t => Math.min(dur - 0.02, Math.max(0, t)).toFixed(3)).join(","));
' "$@")

echo "== Stills at ${TIMES//,/s, }s"
npx --yes "hyperframes@${HF_VERSION}" snapshot --at "$TIMES" --no-end -o "$OUTDIR" >/dev/null
N=$(ls "$OUTDIR"/*.png | wc -l)
COLS=$(( N < 4 ? N : 4 ))
ffmpeg -v error -y -pattern_type glob -i "$OUTDIR/*.png" -vf "scale=480:-2,tile=${COLS}x$(( (N + COLS - 1) / COLS )):padding=12:margin=12:color=0x333333" -frames:v 1 out/review/stills.png
echo "wrote out/review/stills.png ($N stills). Look at it before rendering."
