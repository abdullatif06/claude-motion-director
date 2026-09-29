#!/usr/bin/env bash
# Create a new Motion Studio project on top of HyperFrames.
# Usage: bash <skill>/scripts/new-project.sh <project-name>
set -euo pipefail

NAME="${1:?Usage: new-project.sh <project-name>}"
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HF_VERSION="${HF_VERSION:-0.8.86}"
GSAP_VERSION="${GSAP_VERSION:-3.14.2}"

# 1. Requirements
node -e 'const m=+process.versions.node.split(".")[0]; if(m<22){console.error("Node 22+ required, found "+process.versions.node);process.exit(1)}'
command -v ffmpeg >/dev/null || { echo "FFmpeg is required (brew install ffmpeg / apt install ffmpeg)"; exit 1; }

# 2. HyperFrames project (also installs the HyperFrames agent skills)
npx --yes "hyperframes@${HF_VERSION}" init "$NAME" --non-interactive --resolution portrait
cd "$NAME"

# 3. GSAP served locally: renders never depend on a CDN
npm i --silent "gsap@${GSAP_VERSION}"
mkdir -p assets/vendor
cp node_modules/gsap/dist/gsap.min.js assets/vendor/gsap.min.js

# 4. Motion Studio template
cp -R "$SKILL_DIR/templates/project/src" ./src
cp "$SKILL_DIR/templates/project/project.json" ./project.json
mkdir -p docs out assets/refs assets/audio/sfx assets/fonts
cat > fonts.css <<'CSS'
/* Fonts live here, at the project root, with root-relative paths (assets/fonts/...).
   Paths in src/style.css would resolve from src/ in the browser but from the root in
   HyperFrames' check, so @font-face rules must not go there. Example:
@font-face { font-family: Inter; font-weight: 700; src: url(assets/fonts/inter-latin-700-normal.woff2); }
*/
CSS
echo "[]" > docs/cues.json
cp "$SKILL_DIR/templates/brief.md" docs/BRIEF.md
cp "$SKILL_DIR/templates/review_log.md" docs/review_log.md
cp "$SKILL_DIR/templates/LOOK.md" docs/LOOK.md
cp "$SKILL_DIR/templates/shotlist.md" docs/shotlist.md
node "$SKILL_DIR/scripts/shells.mjs"

# 5. Point the project's CLAUDE.md at Motion Studio
cat >> CLAUDE.md <<EOF

## Motion Studio
This project is directed with the motion-studio skill ($SKILL_DIR).
- One file per scene in src/scenes/ (API at the top of src/film.js); order and beats in project.json. Styles in src/style.css.
- Render one scene alone: bash $SKILL_DIR/scripts/clip.sh <scene-id>
- Never edit index.html by hand: change project.json, then run node $SKILL_DIR/scripts/shells.mjs [format]
- Follow $SKILL_DIR/references/house-rules.md on every video.
- Render all formats with: bash $SKILL_DIR/scripts/render-all.sh
EOF

echo
echo "Motion Studio project ready: $(pwd)"
echo "Next: bash $SKILL_DIR/scripts/doctor.sh"
