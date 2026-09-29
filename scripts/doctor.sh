#!/usr/bin/env bash
# Check that a Motion Director project can render.
# Usage (from the project root): bash <skill>/scripts/doctor.sh
set -uo pipefail
HF_VERSION="${HF_VERSION:-0.8.86}"
ok=1

echo "== HyperFrames doctor"
npx --yes "hyperframes@${HF_VERSION}" doctor || true

echo
echo "== Motion Director checks"
[ -f assets/vendor/gsap.min.js ] && echo "  ✓ GSAP served locally" || { echo "  ✗ assets/vendor/gsap.min.js missing (re-run new-project.sh or copy it from node_modules/gsap/dist)"; ok=0; }
[ -f project.json ] && echo "  ✓ project.json" || { echo "  ✗ project.json missing"; ok=0; }
[ -f src/film.js ] && [ -d src/scenes ] && echo "  ✓ src/film.js + src/scenes/" || { echo "  ✗ src/film.js or src/scenes/ missing"; ok=0; }
if python3 -c "import numpy, scipy" 2>/dev/null; then echo "  ✓ python3 with numpy + scipy (audio tools)"; else echo "  ✗ audio tools need: pip install -r <skill>/scripts/requirements.txt"; ok=0; fi
if grep -q "cdn.jsdelivr\|cdnjs\|unpkg" index.html src/*.js 2>/dev/null; then
  echo "  ✗ CDN script found: serve libraries from assets/vendor so renders work offline"; ok=0
else
  echo "  ✓ no CDN scripts"
fi

cat <<'EOF'

If Chrome is reported missing and `npx hyperframes browser ensure` cannot download it,
point HyperFrames at any installed Chrome or Chromium:
  export HYPERFRAMES_BROWSER_PATH="/path/to/chrome"
EOF

[ "$ok" = 1 ] && echo "Ready." || { echo "Fix the ✗ items above."; exit 1; }
