#!/usr/bin/env bash
# Render one format with motion blur: render SUB frames per output frame, then
# blend each group into one (ffmpeg tmix) and keep one frame per group.
# Usage (from the project root): bash <skill>/scripts/blur-render.sh <out.mp4> [subframes] [quality]
#   subframes: 4 (default), 8 or 16. fps x subframes must be <= 240 (HyperFrames' max),
#   so at 30 fps use up to 8; at 60 fps use up to 4. For very fast moves, slowing the
#   move down is often better than more subframes.
set -euo pipefail
OUT="${1:?Usage: blur-render.sh <out.mp4> [subframes] [quality]}"
SUB="${2:-4}"
QUALITY="${3:-looks}"
HF_VERSION="${HF_VERSION:-0.8.86}"

FPS=$(node -e 'const r=require("fs").readFileSync("index.html","utf8").match(/data-fps="(\d+)"/);console.log(r?r[1]:30)')
HI=$((FPS * SUB))
if [ "$HI" -gt 240 ]; then
  echo "fps ($FPS) x subframes ($SUB) = $HI, above HyperFrames' 240 fps limit. Use fewer subframes." >&2
  exit 1
fi

TMP="$(dirname "$OUT")/.blur-$$.mp4"
mkdir -p "$(dirname "$OUT")"
echo "== Rendering $HI fps ($SUB subframes per frame)"
npx --yes "hyperframes@${HF_VERSION}" render -f "$HI" --crf 10 -o "$TMP"

CRF=16; [ "$QUALITY" = "delivery" ] && CRF=14; [ "$QUALITY" = "draft" ] && CRF=23
echo "== Blending to $FPS fps"
ffmpeg -v error -y -i "$TMP" \
  -vf "tmix=frames=${SUB},select='eq(mod(n\,${SUB})\,${SUB}-1)',setpts=N/${FPS}/TB" \
  -r "$FPS" -c:v libx264 -crf "$CRF" -pix_fmt yuv420p -an "$OUT"
rm -f "$TMP"
echo "wrote $OUT"
