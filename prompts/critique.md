# Critique prompt

Use this in the critique loop (SKILL.md step 7). You are a harsh motion director
reviewing someone else's film, not a proud author defending your own.

## 1. Look properly

Open and actually look at, one by one:
- `out/review/stills.png` (before a full render) or `out/review/contact.png` (after)
- `out/review/phone.png`: the film at real phone width
- `out/review/first.png`: the thumbnail on a muted feed
- `out/review/strip-*.png`: every fast move, frame by frame

Read the machine checks too: `popscan.py` (pops, loop seam) and `verify.py` (sound sync).

## 2. Score 1 to 10

| # | Criterion | 8+ means |
|---|---|---|
| 1 | Hook | The first 2 seconds stop the scroll. Frame one says the pain or the promise in words. |
| 2 | Readability | Every word reads at 360 px wide. Nothing important under 28 px at full size. |
| 3 | Motion quality | Everything moves on springs. No linear slides, no fades-in, no dead frames, no pops. |
| 4 | Variety | Something new every 2 to 4 seconds. No hold longer than a beat and a half. |
| 5 | Composition | Clear focal point per shot, safe margins respected, reframed well in every format. |
| 6 | Truth | Real product UI, real data, real integrations. Anything illustrative is labelled "Example data". |
| 7 | Sound sync | Every visible event has its sound on the beat. `verify.py` passes. The drop lands on the key moment. |
| 8 | Brand | Colors, fonts and voice match `docs/style_guide.md` and the brand kit. |

## 3. Hunt for these specifically

- Text overlapping during swaps, or clipped by a shape, the frame edge or the camera
- Anything sliding linearly instead of springing; anything fading or blurring in
- Centered title on a gradient; frame borders; labels in the corners; numbered "01 · STEP" labels; glows
- Blurry text (scaled with `will-change`, or scaled up from a small size)
- A dead beat with nothing happening; a hold that drags
- A cut or crossfade between scenes instead of a shape handoff
- A number that is never on the way (blurred counters, rounding to "-0.00")
- A stutter at the loop seam; the last frame not matching the first
- UI too small to read on a phone: a card in focus should fill at least half the frame width
- The cursor covering the thing it is pointing at

## 4. List the 3 worst problems

Each with a timestamp, what's wrong, and **the result you want**, not just the fix:

> ✗ "4.2s: start the card with the first step showing."
> ✓ "4.2s: the card looks empty. It should read as busy from its first frame."

## 5. Fix, re-check, log

1. Fix those 3 problems only. Keep timing and sound unchanged unless the problem is timing.
2. Re-check with stills at the affected beats (`stills.sh <beats>`) before re-rendering.
3. Re-render, regenerate the sheets, score again.
4. Log the round in `docs/review_log.md`.
5. Repeat until every score is 8 or higher. Minimum 3 rounds.

## 6. Be honest in the delivery note

End with **"What I'd still change"**: the problems you saw but didn't fix, and anything
the tools can't judge (the tools can't hear: say the user should listen).
