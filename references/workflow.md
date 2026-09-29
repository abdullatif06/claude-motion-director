# Workflow detail

Full instructions for each step of the pipeline in SKILL.md.

## 1. Intake

Collect everything in `templates/brief.md` **in one message** before any work starts,
and save the answers to `docs/BRIEF.md` so later sessions never re-ask.

- **Warm start beats cold start.** A URL, real screenshots, a document or a transcript
  produces a far better film than a description, because the film is built from real
  material instead of invented copy. Ask for real material first.
- If the user says "your call" on something, decide, and list what you decided.
- Ask the truth-check questions every time: which numbers are real, which claims and
  integrations may be shown.

## 2. Assets

Everything goes in `./assets`. List what you found before animating.

- **Website capture:** `npx hyperframes capture <url> -o assets/capture` saves the site's
  screenshots, images, SVGs and fonts. Use `--max-screenshots` for long sites.
- **Specific states:** screenshot the real page with a headless browser. If a state the
  film needs doesn't exist (a switch off, an empty list), change a local copy of the real
  page and screenshot that. Never draw the UI from imagination.
- **Crops for morphing shapes** need transparent backgrounds: a crop with the page
  background baked in shows as a grey rectangle on a moving shape. Re-shoot elements
  individually rather than cropping full-page screenshots.
- **Brand:** real logo file (SVG preferred), exact hex colors from the site's CSS,
  fonts copied into `assets/fonts` (and declared in `src/style.css`).
- Record every source in `docs/assets.md`.

## 3. Style

1. Get 3 reference films the user would be jealous of (whatships.com catalogues launch
   films; competitors' launch videos work well).
2. Study each: `bash scripts/review/ref-frames.sh assets/refs/<file>.mp4` extracts frames,
   a contact sheet and the cut points. Look at them.
3. Write `docs/style_guide.md` (what the references share: palette, type, shot lengths,
   transitions, camera, texture, how text enters and exits) and fill in `docs/LOOK.md`
   from `templates/LOOK.md`, with exact values.
4. **Take the grammar, never the content**: no copied logos, characters, footage or copy.
5. Show the user LOOK.md. They edit it; you follow it.

Without a reference, Opus falls back to its defaults (the banned looks). A reference is
the cheapest fix there is.

## 4. Sound kit and beat grid

See `references/sound.md`.

## 5. Shot list

Write `docs/shotlist.md` from `templates/shotlist.md`, on the beat grid:

- Structure that works for product films: **hook** (the pain, in words), **demo** (the
  real product doing the job), **morph** (one shape carrying the story), **proof** (the
  number people pause on, landing on the drop), **end card** (logo + call to action,
  folding back into frame one so it loops). Adapt it; don't force it.
- Every scene: id, length in beats, beat-by-beat action, on-screen text, sound cues, and
  its handoff shape (its last frame = the next scene's first frame).
- Put the scene ids and beats into `project.json` `"scenes"`.
- **Gate:** show the shot list and wait for approval.

## 6. Build: scenes as clips, then one film

Build each scene as its own clip before joining them. When a 30-second film comes back
wrong you can't tell which part broke; when one scene is its own clip, you can.

1. One file per scene in `src/scenes/NN-id.js`, registered with `MS.scene("id", (s) => {...})`.
   The scene API is documented at the top of `src/film.js`.
2. Render a scene alone: `bash scripts/clip.sh <id>` → `out/clips/<id>.final.mp4`, with its
   slice of the music and effects. Review it (stills, sheets, pop scan) until it passes.
3. Scenes can be built in parallel (separate sessions or subagents), because each one only
   touches its own file. Write `docs/ANIMATION_GUIDE.md` first (the LOOK plus shared helpers)
   so every scene is coded the same way.
4. **Join:** once every clip passes, render the whole film (`render-all.sh`). Check every
   handoff with stills on each boundary: the last beat of scene N and beat 0 of scene N+1
   must look identical.
5. Trim scenes by whole beats if needed; never stretch time.

Project layout, engine rules: `references/engine.md`. Springs, beats, camera, blur:
`references/motion.md`.

## 7. Critique loop

The single habit that separates good films from "it's a bit mid": look at your own frames.

| Tool | When | Catches |
|---|---|---|
| `scripts/review/stills.sh [beats]` | before every full render | layout, text size, clipping, off-frame elements |
| `scripts/review/sheets.sh <video> [times]` | after every render | pacing (contact), phone readability (phone), thumbnail (first), fast-move glitches (strip-*) |
| `scripts/review/popscan.py <video> [--loop]` | after every render | single-frame pops, loop seam |
| `scripts/audio/verify.py <video> [--solo id]` | after every render with cues | effects off their beat |

Score with `prompts/critique.md`, log in `docs/review_log.md`, repeat until all scores
are 8+ (minimum 3 rounds).

### Notes from the user

Treat them like notes to a freelancer. Change only what the notes need; keep timing and
sound unless a note is about them. Read notes as problem plus wanted result: if a note
describes a fix ("start with the first step showing"), check that the fix achieves the
result the user wants ("it should look busy"), and say so if it doesn't. Every clip's
"What I'd still change" list is where the next round of notes starts.

## 8. Final render

`bash scripts/render-all.sh delivery` checks and renders every format from the same
timeline, mixes the sound, attaches it and verifies sync. For fast motion, re-render the
final with motion blur (`references/motion.md`). Each format is reframed by its own
layout, never cropped: check each format's contact sheet.

## 9. Delivery

Checklist before handing over:

- [ ] Every critique score is 8+, logged in `docs/review_log.md`
- [ ] `popscan.py` finds no pops; with `--loop`, the seam matches (if the film should loop)
- [ ] `verify.py` passes: every effect within 10 ms
- [ ] Final render at `delivery` quality (with motion blur if there is fast motion), all formats
- [ ] Every format checked on its own contact sheet (reframed, not cropped)
- [ ] Frame one works as a muted thumbnail
- [ ] No invented UI, numbers or integrations; illustrative data labelled "Example data"
- [ ] `docs/AUDIO.md` lists source and license for every sound

Deliver:
- `out/<format>.final.mp4` for every format
- `out/review/poster.png` and `out/review/contact.png`
- `docs/review_log.md`
- A short note: what was made, final scores, and **What I'd still change**

Posting tips to pass on: frame one is the thumbnail, so make it say the pain in words;
assume no sound; wide for X, YouTube and websites, vertical for Reels, TikTok and Shorts;
put the link in the first reply, not the video; write the post around the payoff
("Invoices that chase themselves"), not the launch ("Introducing v1.0").
