#!/usr/bin/env bash
# Review sheets for a rendered video: what Claude looks at in the critique loop.
# Usage (from the project root):
#   bash <skill>/scripts/review/sheets.sh out/vertical.final.mp4 [fast-move-time ...]
# Writes to out/review/:
#   contact.png    2 frames per second: layout, pacing, variety, dead beats
#   phone.png      1 frame per second at 360 px wide: can it be read on a phone?
#   first.png      frame one = the thumbnail on a muted feed: does it say the pain in words?
#   poster.png     a full-size frame from 40% in, for sharing
#   strip-<t>.png  12 consecutive frames around each fast move: pops, overlaps, ghosting
set -euo pipefail
V="${1:?Usage: sheets.sh <video.mp4> [fast-move-time ...]}"; shift || true
O=out/review; mkdir -p "$O"
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$V")
W=$(ffprobe -v error -select_streams v:0 -show_entries stream=width -of csv=p=0 "$V")
H=$(ffprobe -v error -select_streams v:0 -show_entries stream=height -of csv=p=0 "$V")

rows() { node -e "console.log(Math.max(1, Math.ceil($1 / $2)))"; }
COLS=6; [ "$W" -gt "$H" ] && COLS=5
ffmpeg -v error -y -i "$V" -vf "fps=2,scale=320:-2,tile=${COLS}x$(rows "$(node -e "console.log(Math.ceil($DUR*2))")" $COLS):padding=6:color=0x333333" -frames:v 1 "$O/contact.png"
ffmpeg -v error -y -i "$V" -vf "fps=1,scale=360:-2,tile=5x$(rows "$(node -e "console.log(Math.ceil($DUR))")" 5):padding=6:color=0x333333" -frames:v 1 "$O/phone.png"
ffmpeg -v error -y -i "$V" -frames:v 1 "$O/first.png"
ffmpeg -v error -y -ss "$(node -e "console.log(($DUR*0.4).toFixed(3))")" -i "$V" -frames:v 1 "$O/poster.png"
for T in "$@"; do
  START=$(node -e "console.log(Math.max(0, $T - 0.2).toFixed(3))")
  ffmpeg -v error -y -ss "$START" -i "$V" -vf "scale=320:-2,tile=12x1:padding=4:color=0x333333" -frames:v 1 "$O/strip-$T.png"
done
echo "wrote $O/contact.png, phone.png, first.png, poster.png$( [ $# -gt 0 ] && echo ', strip-*.png')"
