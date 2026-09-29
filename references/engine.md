# Engine: HyperFrames conventions

How Motion Director projects are wired on top of HyperFrames. Tested with HyperFrames 0.8.86.
For anything not covered here, use the HyperFrames skills (`/hyperframes`) or `npx hyperframes docs <topic>`.

## Project layout

```
my-film/
  index.html        generated per format by scripts/shells.mjs — never edit by hand
  project.json      fps, bpm, beatOffset, formats (first = primary), scenes [{id, beats}],
                    music; duration is computed from the scenes
  src/motion.js     motion toolkit (springs, beats, camera) — see references/motion.md
  src/film.js       builds the film from project.json scenes; the scene API is documented at its top
  src/scenes/       one file per scene (NN-id.js), shared by every format
  src/style.css     brand tokens (:root) and base styles
  fonts.css         @font-face rules (root-relative paths) — linked automatically when present
  assets/fonts/     font files (licensed for video, e.g. OFL)
  assets/vendor/    gsap.min.js served locally
  assets/refs/      reference frames and videos
  assets/audio/     music + sfx/ (real recordings)
  docs/             BRIEF.md, style_guide.md, shotlist.md, review_log.md,
                    beats.json/png, kit.json, AUDIO.md, cues.json
  out/              renders and review stills
```

## Scripts

| Script | Run from | Does |
|---|---|---|
| `scripts/new-project.sh <name>` | anywhere | HyperFrames init + local GSAP + Motion Director template |
| `scripts/doctor.sh` | project root | environment and project checks |
| `scripts/smoke-test.sh` | project root | proves check + determinism before real work; writes `out/smoke.png` |
| `scripts/shells.mjs [format] [--solo id]` | project root | writes index.html for a format (default: primary), optionally one scene alone |
| `scripts/clip.sh <id> [quality] [format]` | project root | renders one scene as its own clip with its slice of sound |
| `scripts/render-all.sh [draft\|looks\|delivery]` | project root | check + render every format to `out/<format>.mp4` |
| `scripts/audio/*` | project root | measure music and effects, mix, attach, verify (see `references/sound.md`) |
| `scripts/review/*` | project root | stills preview, review sheets, pop scan (see `prompts/critique.md`) |
| `scripts/blur-render.sh <out.mp4> [4\|8] [quality]` | project root | renders the current `index.html` with motion blur |

Use `draft` while iterating, `delivery` only for the final render.

## Rules that break renders if ignored

1. **One root composition.** HyperFrames rejects several root HTML files with `data-composition-id`. That is why formats are rendered one at a time by regenerating `index.html`, never kept side by side.
2. **One paused root timeline**, registered as `window.__timelines["main"]`. Child timelines added to it must not be paused.
3. **Timed elements** need `data-start` and `data-duration`, plus `class="clip"`. `film.js` does this for every scene.
4. **Build inside a scene function**, never at a file's top level. `index.html` calls `MS.build()` after every scene file has loaded, and it waits for the DOM: HyperFrames can run scripts before `<body>` is parsed.
5. **Read size from the root element** (`data-width`, `data-height`, `data-ms-format`), not from globals set in other scripts. Script order is not guaranteed.
6. **No CDNs.** Serve GSAP and any other library from `assets/vendor/`. A blocked or slow CDN makes the timeline silently stop advancing (`Timeline did not advance under seek`).
7. **Determinism.** No `Math.random()`, `Date.now()`, timers or network. Use seeded noise if you need randomness.
8. **Scene sections live in `index.html`.** `shells.mjs` writes one timed `<section id="scene-<id>">`
   per scene, and `film.js` fills it. HyperFrames' runtime shows and hides clips it finds at load,
   and its timeline tools list them.
9. **Never set `visibility: visible` on anything inside a scene.** In CSS a child set to
   "visible" shows even while its scene is hidden, so it bleeds into every other scene. To show
   something again, set `visibility` to `""` (inherit).
10. **Fonts in `fonts.css` at the project root**, with paths like `assets/fonts/x.woff2`. The browser
   resolves CSS paths from the CSS file, HyperFrames' check from the root: only a root file agrees with both.
11. **Rising text uses clip-path, not an `overflow: hidden` mask** (`s.rise`). A masked word sits
   physically below its line, and the check reports it as occluded or overflowing.
12. **Content inside a morphing shape appears once the shape is open** (`MS.contentWhenOpen`). The
   check counts text clipped by a growing card as visible and fails its contrast.
13. **Two labels that swap in one grid cell** need `grid-template-columns: minmax(0, 1fr)` on the
   container, or the wider hidden label pushes the visible one off-centre.
14. **Run `npx hyperframes check` before every render.** It covers lint, runtime errors, layout, motion and contrast. `render-all.sh` runs it for every format.

## Layout across formats (reframe, don't crop)

Each scene gets a layout object `s.L` and two size helpers:

- `s.u(n)`: n% of the short side. Use for shapes, spacing, strokes.
- `s.w(n)`: n% of the width. Use for lines of text, so they never wrap unexpectedly.
- `s.L.wide`, `s.L.portrait`, `s.L.name` (`vertical` / `square` / `wide`) to change composition per format.

Lessons from testing:
- Sizing a title by the short side made it wrap in vertical, and in square once side margins
  were added. Text that spans the frame must scale with width.
- Product UI needs its own base font per format (e.g. 30 px vertical, 27 px wide) and cards
  sized per format; check each format's stills, since wide frames make UI look small.
- When checking handoffs, make test scenes look different: two demo scenes that both started
  as a centred dot once hid a bug where every scene stayed visible.

## Rendering without a downloadable Chrome

If `npx hyperframes browser ensure` cannot download Chrome (offline machines, locked-down networks), point HyperFrames at any installed Chrome or Chromium:

```bash
export HYPERFRAMES_BROWSER_PATH="/path/to/chrome"
```

Rendering then uses the slower screenshot path, which is fine for most films.
