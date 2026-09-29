#!/usr/bin/env bash
# Study a reference film: extract frames and a contact sheet so its grammar (pacing,
# type, transitions, camera) can be written into docs/style_guide.md and LOOK.md.
# Take the grammar, never the content, logos or characters.
# Usage (from the project root): bash <skill>/scripts/review/ref-frames.sh assets/refs/launch.mp4 [every-seconds]
# Writes assets/refs/<name>/frame_*.png, contact.png and cuts.txt (detected scene changes).
set -euo pipefail
V="${1:?Usage: ref-frames.sh <video> [every-seconds]}"
EVERY="${2:-0.5}"
NAME=$(basename "${V%.*}")
O="assets/refs/$NAME"; mkdir -p "$O"
FPS=$(node -e "console.log(1/$EVERY)")
ffmpeg -v error -y -i "$V" -vf "fps=$FPS,scale=640:-2" "$O/frame_%03d.png"
N=$(ls "$O"/frame_*.png | wc -l)
ffmpeg -v error -y -i "$V" -vf "fps=$FPS,scale=320:-2,tile=6x$(( (N + 5) / 6 )):padding=4:color=0x333333" -frames:v 1 "$O/contact.png"
# Scene changes: where the reference cuts (or doesn't) tells you its pacing.
ffmpeg -v info -i "$V" -vf "select='gt(scene,0.3)',showinfo" -f null - 2>&1 | grep -o "pts_time:[0-9.]*" | cut -d: -f2 > "$O/cuts.txt" || true
echo "wrote $N frames (every ${EVERY}s), $O/contact.png, and $(wc -l < "$O/cuts.txt") detected cuts in $O/cuts.txt"
