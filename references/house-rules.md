# House rules

These apply to every film made with Motion Director. When a brief contradicts a rule,
follow the brief, and say so in the delivery note. When LOOK.md contradicts a rule,
LOOK.md wins for style; these rules still win for truth and the render contract.

## 1. Truth (never broken)

- **Never redraw product UI.** Every product pixel comes from a real screenshot or crop
  of the real product, or from the product's own front-end code (same markup, CSS and data),
  which lets real components animate. Need a state the screenshots don't show? Change a copy of the real
  page and screenshot it; never invent the screen.
- **No invented numbers, names, prices, logos or integrations.** Only what is on the
  real pages. Illustrative data must say "Example data" on screen.
- **Don't tidy the story with fake data.** If two real screens don't line up (different
  invoice numbers, say), leave them and flag it. Showing a flaw beats faking a fix.
- **Captions and posts stay true.** No "made in 10 minutes" if it wasn't.

## 2. Render contract

- Every frame is a pure function of time. No `Math.random()` (use `MS.rng(seed)`),
  no `Date.now()`, timers, CSS transitions/animations, `requestAnimationFrame`, or network.
- Libraries served from `assets/vendor/`, never a CDN.
- One timeline, one clock, written in beats. Picture and sound read the same file.
- Details and the rules that break renders: `references/engine.md`.

## 3. Look

Defaults when LOOK.md doesn't say otherwise:

- One display face, one UI face. One accent color. One accent word (or phrase) per headline, at most.
- Contrast is part of the brand: many brand accents fail 3:1 as text. Use a text-safe
  shade (`--accent-ink`) for accent words, and fix colors that fail in the product too, so the
  film and the product stay identical.
- Text rises out of a mask line, one word per beat. Nothing fades in, nothing blurs in.
- Everything moves on springs (`references/motion.md`). No stock eases.
- Things change shape into the next thing instead of cutting: a dot grows into a button,
  a button stretches into a card. A color change is a shape change (a circle floods the
  button from the cursor), not a crossfade.
- The camera is one transform on one container, one move at a time, zoom in log space.
- UI in focus fills at least half the frame width. No on-screen text below 28 px at full size.

## 4. Banned looks

These are the tells of generic AI video. Never use them unless the brief asks:

- Centered title on a gradient background
- Everything fading in; blur-in text reveals; crossfades between scenes
- Dark scene with a green or purple glow; glows on UI chrome
- Generic particle bursts, lens flares, 3D for its own sake
- Frame borders, corner labels, numbered "01 · STEP" section labels
- Invented logos or placeholder brand names on screen
- Synthesized "microwave beep" sound effects
- Holds longer than a beat and a half; dead beats with nothing happening

## 5. Pacing

- Hook in the first 2 seconds. On a muted feed that means words, not UI.
- Loop vs thumbnail: a seamless loop starts on its handoff shape, so frame one may not say the
  pain. Decide with the user; offer a thumbnail frame for platforms that allow one.
- Something new every 2 to 4 seconds.
- Every scene starts on a beat; big moments on downbeats; the music drop lands on the
  payoff (the number, the reveal, "Paid").
- Scenes hand over through a shared shape: **a scene's last frame equals the next
  scene's first frame.** Never a cut, never a fade.
- If the film will loop (X, Instagram), the last frame equals the first.

## 6. Sound

- Real recordings with commercial licenses, logged in `docs/AUDIO.md`.
- Every effect's measured hit lands on its visible event. No effect without a visible cause.
- -14 LUFS. Details: `references/sound.md`.

## 7. Before you show anything

- Stills before renders. Review sheets and pop scan after every render.
- Critique loop until every score is 8+ (`prompts/critique.md`).
- End every delivery with **What I'd still change**.
