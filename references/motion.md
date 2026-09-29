# Motion: springs, timing, camera, blur

The toolkit in `src/motion.js` (exposed as `window.MS`). Every function is a pure
function of time, so any frame renders directly and every render is identical.

## The one rule

Cheap motion goes from A to B on a fixed curve. Expensive motion has mass: it
accelerates, overshoots a hair, and settles. **Move everything with springs.**
Never use `linear`, `power*`, `back`, `elastic` or CSS transitions for on-screen motion.

## Spring presets

| Preset | Overshoot | Use for |
|---|---|---|
| `snappy` | ~3% | buttons, toggles, cursors, leading edges |
| `default` | ~1% | cards, containers, camera |
| `heavy` | none | big type, logo lockups, anything that must feel solid |
| `playful` | visible | mascots, stickers. Never on UI or body text |

## Which tool when

| Situation | Use |
|---|---|
| A normal move from one state to another | `ease: MS.ease("preset")` on a GSAP tween |
| A value that changes target several times (cursor, container width) | `MS.track(t, [[time, value], ...], preset)` inside `s.frame` |
| A tab indicator that stretches as it moves | `MS.indicator(t, stops, width)` |
| Text inside a shape that is morphing | `MS.swapAlpha(t, tIn, tOut)`: enters after the morph starts, leaves before the next |
| Camera zoom | `MS.zoom(t, [[time, scale], ...])`: interpolated in log space, so 1x to 2x feels as fast as 2x to 4x |
| Timing | `s.at(n)`: time of beat n counted from the scene's start; `s.B(n)`: a length of n beats |
| Randomness | `MS.rng(seed)`: seeded, never `Math.random()` |

`s.frame((t, local) => ...)` runs on every frame the timeline is seeked to (`t` = film time,
`local` = seconds into the scene). It must derive everything from `t` and remember nothing
between calls.

**Keyframe times are when a move STARTS**, not when it ends. A spring then settles over about
0.5 s (`heavy` about 0.6 s). A count-up keyed to "reach 320 at beat 4" actually starts at beat 4
and finishes after the card has already moved on. Start moves early, and let the payoff hold.

**Morphing shapes:** `MS.box(el, t, { w, h, cx, cy, r }, preset)` drives a box from keyframe
tracks. The pattern that reads best: a dot grows into a pill, the pill into a card, the card's
content appears when it lands (`MS.contentWhenOpen`), and the card folds back into the next
scene's shape.

**Why `track` instead of chained tweens:** chaining tweens restarts the motion at every
change. `track` adds one spring per change, so the motion stays continuous and you can
still render any frame directly.

## Text

- Text rises out of a mask line, one word per beat (`s.rise(el, beat, step, outBeat)`).
- Headlines: `s.headline("The work *didn't* start.")`; the accent may span words: `"in *12 seconds.*"`.
- Give every headline time to be read: fully in, then at least 1.5 beats before it leaves.
  Nothing fades in and nothing blurs in.
- Text inside a morphing container uses `swapAlpha`.
- Never put `will-change` on anything the camera scales: it makes text blurry.

## Timing

- Time everything in beats: `s.at(4)`, not `2.0`. Picture and sound read the same clock.
- Start big moments on downbeats (every 4 beats). The music drop lands on the key visual moment.
- Something new every 2 to 4 seconds. No hold longer than a beat and a half.

## Motion blur

HyperFrames has no built-in motion blur. `scripts/blur-render.sh` renders several
subframes per output frame and blends them, like a real camera shutter.

```bash
bash <skill>/scripts/blur-render.sh out/wide.mp4 8 delivery
bash <skill>/scripts/audio/mux.sh out/wide.mp4     # blur renders are silent: attach the mix
```

- 4 subframes: default. 8: fast moves (anything moving more than about 15 px per frame).
- HyperFrames renders at most 240 fps, so at 30 fps the maximum is 8, and at 60 fps it is 4.
- If a move still shows steps at the maximum, slow the move down. That is usually the better fix anyway.
- Blur is slow (about 25 seconds of rendering per second of film on a laptop CPU, more
  with software graphics). Use it for the final render only, never while iterating.
- Blur must never show a value that doesn't exist. A counter blurred between 939 and 1,039
  displays a fake number: keep counters and changing numbers sharp and move them by whole values.
