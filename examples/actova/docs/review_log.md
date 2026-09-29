# Review log

One entry per critique round. Copied to docs/review_log.md in each project.

## Round 1 (stills | full render)

| Hook | Read | Motion | Variety | Composition | Truth | Sound | Brand |
|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |  |

Machine checks: pops ☐ none · loop ☐ n/a / ☐ matches · sound ☐ within 10 ms

3 worst problems:
1. `0.0s`: problem. Wanted result.
2.
3.

Fixed:
-

<!-- Copy the block above for each round. Stop when every score is 8+ (minimum 3 rounds). -->

## Actova round 1 (full render, draft)

| Hook | Read | Motion | Variety | Composition | Truth | Sound | Brand |
|---|---|---|---|---|---|---|---|
| 7 | 8 | 8 | 7 | 8 | 9 | 8 | 8 |

Machine checks: pops ☑ none (both formats) · loop ☑ matches (diff 0.00) · sound ☑ 27/27 within 0.0 ms

3 worst problems:
1. `13-15s`: task board sits empty ~2 s before the drop. Wanted: the board visibly builds up to the drop.
2. `0.0s`: frame one is only the orange dot. Wanted: a first frame that says the pain on a muted feed (conflicts with the seamless loop: decision for the user).
3. `wide`: product UI reads small (24 px). Wanted: UI as readable in wide as in vertical.

Fixed:
- 1: owner columns grow in one by one on beats 1-2.2.
- 3: wide base font 24 → 27 px, cards 60% → 64% of the width.
- 2: open; poster frame offered as the thumbnail where the platform allows.

## Actova round 2 (full render, draft)

| Hook | Read | Motion | Variety | Composition | Truth | Sound | Brand |
|---|---|---|---|---|---|---|---|
| 7 | 8 | 8 | 8 | 8 | 9 | 8 | 8 |

Machine checks: pops ☑ none · loop ☑ matches (0.00) · sound ☑ 27/27 within 0.0 ms

3 worst problems:
1. `0.0s`: frame one is the dot (open decision, see round 1).
2. `vertical`: task titles and recap lines ~26 px, under the 28 px phone rule. Wanted: every UI line readable at phone size.
3. `13.3-15s`: four empty columns hold ~0.8 s before the drop. Wanted: acceptable as tension before the drop; no change.

Fixed:
- 2: task titles and recap lines 0.86em → 0.95em (28.5 px in vertical).

## Actova round 3 (stills at the changed beats + final render)

| Hook | Read | Motion | Variety | Composition | Truth | Sound | Brand |
|---|---|---|---|---|---|---|---|
| 7* | 8 | 8 | 8 | 8 | 9 | 8 | 8 |

\* Hook is 8 in motion (words from 0.25 s, pain stated by 2 s) but frame one is the loop dot:
open decision for the user. Thumbnail frame provided (out/review/thumbnail.png).

Machine checks: see final render.

3 worst problems:
1. `0.0s`: frame one = dot (open decision).
2. `22s`: "Send recap" label off-centre (hidden wider label stretched the shared grid cell). Wanted: centred label.
3. Audio is a generated placeholder: not release quality (listen before any real use).

Fixed:
- 2: shared label cell pinned to the button/pill width.
