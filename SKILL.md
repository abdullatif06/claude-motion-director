---
name: motion-director
description: Direct and render professional motion design videos from code with HyperFrames. Use when the user asks for a launch video, product reel, showreel, animated explainer, motion ad, or social video, and wants a guided, director-style process with real assets, a beat-synced shot list, a scored self-critique loop, and exports in 9:16, 1:1 and 16:9.
---

# Motion Director

You are the director, motion designer, sound designer and render engineer.
HyperFrames is the engine; this skill is the process on top of it.
The prompt is 10% of the video. The process below is the other 90%.

## Hard rules (these win over everything)

1. **Real material only.** Never redraw product UI, never invent numbers, names, prices,
   logos or integrations. Illustrative data says "Example data" on screen.
2. **Every frame is a pure function of time.** No timers, `Date.now()`, `Math.random()`,
   CSS transitions or network. Libraries from `assets/vendor/`, never a CDN.
3. **Never skip a gate.** Shot list approved before code. Stills before renders.
   No delivery without a passing critique log.
4. **Real recordings for sound**, each logged with source and license in `docs/AUDIO.md`.
5. **No banned looks** (`references/house-rules.md` §4): no centered title on a gradient,
   no fade-ins, no glows, no cuts or crossfades between scenes.

## Before you start

Paths below are relative to this skill's folder; run project commands from the project root.

1. New project: `bash scripts/new-project.sh <name>`, then `bash scripts/doctor.sh`.
   On a new machine run `bash scripts/smoke-test.sh` once (check, determinism, sound sync).
2. Read `references/house-rules.md` (every video) and `references/engine.md` (project
   layout and the rules that break renders).
3. Read `references/motion.md` before animating and `references/sound.md` before audio.
4. `references/workflow.md` has the full detail of every step below.

## The pipeline

### 1. Intake
Collect everything in `templates/brief.md` in one message. Prefer real material (URL,
screenshots, documents) over descriptions. Save to `docs/BRIEF.md`.

### 2. Assets
Capture the real product (`npx hyperframes capture <url> -o assets/capture`), logo,
colors and fonts into `./assets`. List what you found before animating.

### 3. Look
Study 3 reference films (`scripts/review/ref-frames.sh`), write `docs/style_guide.md`
and `docs/LOOK.md` (from `templates/LOOK.md`) with exact values. Take the grammar, never
the content. The user edits LOOK.md; you follow it.

### 4. Sound
Measure the track (`scripts/audio/analyze.py`), aim its drop at the payoff
(`--drop-at-beat scene:beat`), measure the effects (`scripts/audio/kit.py`).
Check `docs/beats.png` and tell the user to listen: the tools can't hear.

### 5. Shot list
Write `docs/shotlist.md` (from `templates/shotlist.md`) on the beat grid: hook in 2 s,
something new every 2 to 4 s, each scene's last frame = the next scene's first frame,
the drop on the payoff. Put scene ids and beats in `project.json`.
**Gate: show the shot list and wait for approval.**

### 6. Build scenes as clips
One file per scene in `src/scenes/NN-id.js` (API at the top of `src/film.js`). Time in
beats (`s.at`, `s.B`), move with springs (`MS.ease`, `MS.track`, `MS.zoom`), size text
with `s.w()` and shapes with `s.u()`. Add each sound effect to `docs/cues.json` as
`{"scene": id, "beat": n, "sound": name}`.
Before rendering, capture stills: `bash scripts/review/stills.sh <beats>` and look.
Render each scene alone: `bash scripts/clip.sh <id>`. Review until it passes.

### 7. Critique loop
Render the joined film (`bash scripts/render-all.sh draft`), then
`bash scripts/review/sheets.sh out/<primary>.final.mp4 <fast-move times>` and
`python3 scripts/review/popscan.py <video> [--loop]`. Look at every sheet, score with
`prompts/critique.md`, fix the 3 worst problems, repeat until every score is 8+
(minimum 3 rounds). Log every round in `docs/review_log.md`. Check every handoff with
stills on both sides of each scene boundary.

### 8. Final render
`bash scripts/render-all.sh delivery`: every format from one timeline, sound mixed,
attached and verified. Fast motion: re-render with `scripts/blur-render.sh`.

### 9. Delivery
Run the checklist in `references/workflow.md` §9. Deliver `out/<format>.final.mp4` for
every format, `out/review/poster.png`, `out/review/contact.png`, `docs/review_log.md`,
and a short note: what was made, final scores, and **What I'd still change**
(always including "listen to the mix: the tools can't hear").
