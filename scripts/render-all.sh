#!/usr/bin/env bash
# Check, then render every format listed in project.json, then add the sound.
# Silent renders: out/<format>.mp4. With sound: out/<format>.final.mp4
# Usage (from the project root): bash <skill>/scripts/render-all.sh [draft|looks|delivery]
#   draft    fast preview renders
#   looks    default quality (CRF 16)
#   delivery final high-quality renders
set -euo pipefail
QUALITY="${1:-looks}"
HF_VERSION="${HF_VERSION:-0.8.86}"
HF="npx --yes hyperframes@${HF_VERSION}"
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

mkdir -p out
FORMATS=$(node -e 'console.log(require("./project.json").formats.join(" "))')
PRIMARY=${FORMATS%% *}

for NAME in $FORMATS; do
  node "$SKILL_DIR/scripts/shells.mjs" "$NAME"
  echo "== Checking $NAME"
  $HF check
  echo "== Rendering $NAME"
  $HF render -q "$QUALITY" -o "out/${NAME}.mp4"
done

# Leave the project on its primary format
node "$SKILL_DIR/scripts/shells.mjs" "$PRIMARY"

# Sound: mix once (same clock for every format), attach to each render, verify sync
HAS_MUSIC=$(node -e 'console.log(require("./project.json").music ? 1 : 0)')
HAS_CUES=$(node -e 'try { console.log(require("./docs/cues.json").length > 0 ? 1 : 0) } catch { console.log(0) }')
if [ "$HAS_MUSIC" = 1 ] || [ "$HAS_CUES" = 1 ]; then
  echo "== Mixing sound"
  python3 "$SKILL_DIR/scripts/audio/mix.py"
  for NAME in $FORMATS; do bash "$SKILL_DIR/scripts/audio/mux.sh" "out/${NAME}.mp4"; done
  if [ "$HAS_CUES" = 1 ]; then python3 "$SKILL_DIR/scripts/audio/verify.py" "out/${PRIMARY}.final.mp4"; fi
fi
echo
ls -lh out/*.mp4
