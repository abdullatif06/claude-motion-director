#!/usr/bin/env bash
# Smoke test: prove the pipeline before building a real film.
# Usage (from the project root): bash <skill>/scripts/smoke-test.sh
#   1. Determinism: the same frame rendered twice is byte-identical.
#   2. Check: HyperFrames check passes.
#   3. Sound sync: a test beep placed at 1.0s lands within 10 ms in the final MP4.
# Writes out/smoke.png (first, middle and last frames side by side).
set -euo pipefail
HF_VERSION="${HF_VERSION:-0.8.86}"
HF="npx --yes hyperframes@${HF_VERSION}"
mkdir -p out/.smoke
pass=1

echo "== 1/3 HyperFrames check"
if $HF check >/dev/null 2>&1; then echo "  ✓ check passed"; else echo "  ✗ check failed (run: npx hyperframes check)"; pass=0; fi

echo "== 2/3 Determinism (render twice, compare the middle frame)"
DUR=$(node -e 'console.log(require("./project.json").duration)')
MID=$(node -e "console.log(($DUR/2).toFixed(3))")
for i in 1 2; do
  $HF render -q draft -o "out/.smoke/run$i.mp4" >/dev/null 2>&1
  ffmpeg -v error -y -ss "$MID" -i "out/.smoke/run$i.mp4" -frames:v 1 -f rawvideo -pix_fmt rgb24 "out/.smoke/frame$i.raw"
done
H1=$(md5sum out/.smoke/frame1.raw | cut -d' ' -f1); H2=$(md5sum out/.smoke/frame2.raw | cut -d' ' -f1)
if [ "$H1" = "$H2" ]; then echo "  ✓ frame at ${MID}s identical across renders"; else echo "  ✗ frame at ${MID}s differs between renders: something depends on time, randomness or the network"; pass=0; fi

LAST=$(node -e "console.log(Math.max(0,$DUR-0.05).toFixed(3))")
for t in 0 "$MID" "$LAST"; do ffmpeg -v error -y -ss "$t" -i out/.smoke/run1.mp4 -frames:v 1 -vf "scale=-1:360" "out/.smoke/f_$t.png"; done
ffmpeg -v error -y -i "out/.smoke/f_0.png" -i "out/.smoke/f_$MID.png" -i "out/.smoke/f_$LAST.png" -filter_complex hstack=inputs=3 out/smoke.png
rm -f out/.smoke/*.raw
echo "  first / middle / last frames: out/smoke.png"

echo "== 3/3 Sound sync (test beep at 1.0s)"
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
S=out/.smoke/audio; rm -rf "$S"; mkdir -p "$S/docs" "$S/out"
python3 - "$S" "$DUR" <<'PY'
import json, sys, numpy as np, subprocess
d, dur = sys.argv[1], float(sys.argv[2])
sr = 48000; t = np.arange(int(0.12 * sr)) / sr
beep = (np.sin(2 * np.pi * 1000 * t) * np.exp(-t * 25) * 0.8).astype(np.float32)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(sr), "-ac", "1", "-i", "-", f"{d}/beep.wav"], input=beep.tobytes(), check=True)
json.dump({"duration": dur, "fps": 30, "bpm": 120, "beatOffset": 0}, open(f"{d}/project.json", "w"))
json.dump([{"t": 1.0, "sound": "beep"}], open(f"{d}/docs/cues.json", "w"))
PY
if (cd "$S" && python3 "$SKILL_DIR/scripts/audio/kit.py" . >/dev/null && python3 "$SKILL_DIR/scripts/audio/mix.py" >/dev/null \
    && cp ../run1.mp4 out/v.mp4 && bash "$SKILL_DIR/scripts/audio/mux.sh" out/v.mp4 >/dev/null \
    && python3 "$SKILL_DIR/scripts/audio/verify.py" out/v.final.mp4 | sed 's/^/  /'); then
  echo "  ✓ sound lands on time"
else
  echo "  ✗ sound sync failed (needs python3 with numpy and scipy: pip install -r <skill>/scripts/requirements.txt)"; pass=0
fi

[ "$pass" = 1 ] && echo "Smoke test passed." || { echo "Smoke test failed."; exit 1; }
