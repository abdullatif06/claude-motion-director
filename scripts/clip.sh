#!/usr/bin/env bash
# Render ONE scene as its own clip, with its slice of the music and effects.
# Build and judge each scene alone before joining them: when a clip is wrong,
# you know exactly which part broke.
# Usage (from the project root): bash <skill>/scripts/clip.sh <scene-id> [draft|looks|delivery] [format]
# Writes out/clips/<scene-id>.mp4 (and .final.mp4 with sound).
set -euo pipefail
ID="${1:?Usage: clip.sh <scene-id> [quality] [format]}"
QUALITY="${2:-draft}"
HF_VERSION="${HF_VERSION:-0.8.86}"
HF="npx --yes hyperframes@${HF_VERSION}"
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PRIMARY=$(node -e 'console.log(require("./project.json").formats[0])')
FORMAT="${3:-$PRIMARY}"

restore() { node "$SKILL_DIR/scripts/shells.mjs" "$PRIMARY" >/dev/null; }
trap restore EXIT

mkdir -p out/clips
node "$SKILL_DIR/scripts/shells.mjs" "$FORMAT" --solo "$ID"
echo "== Checking scene $ID"
$HF check
echo "== Rendering scene $ID"
$HF render -q "$QUALITY" -o "out/clips/${ID}.mp4"

HAS_MUSIC=$(node -e 'console.log(require("./project.json").music ? 1 : 0)')
HAS_CUES=$(node -e 'try { console.log(require("./docs/cues.json").length > 0 ? 1 : 0) } catch { console.log(0) }')
if [ "$HAS_MUSIC" = 1 ] || [ "$HAS_CUES" = 1 ]; then
  python3 "$SKILL_DIR/scripts/audio/mix.py" --solo "$ID"
  bash "$SKILL_DIR/scripts/audio/mux.sh" "out/clips/${ID}.mp4"
  if [ "$HAS_CUES" = 1 ]; then python3 "$SKILL_DIR/scripts/audio/verify.py" "out/clips/${ID}.final.mp4" --solo "$ID"; fi
fi
echo "Next: bash $SKILL_DIR/scripts/review/sheets.sh out/clips/${ID}$( [ "$HAS_MUSIC$HAS_CUES" != 00 ] && echo .final).mp4"
