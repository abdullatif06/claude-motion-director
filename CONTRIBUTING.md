# Contributing

Thanks for helping make Motion Director better. Issues and pull requests are welcome.

## Good first contributions

- **Try it and report back.** Make a film with the skill and open an issue with what worked,
  what broke, and your `docs/review_log.md`. Real runs are how this skill improves.
- **Website capture.** `npx hyperframes capture` is documented but untested in our runs.
- **Right-to-left text** (Arabic, Hebrew) for headlines and product UI.
- **New examples** in `examples/`: a brief, LOOK card, shot list, scenes and review sheets.

## Before you open a pull request

1. Run the smoke test on a fresh project:
   ```bash
   bash scripts/new-project.sh pr-test && cd pr-test && bash ../scripts/smoke-test.sh
   ```
2. If you changed the engine, motion or sound scripts, render the template demo in all formats
   (`bash ../scripts/render-all.sh draft`) and run `python3 ../scripts/review/popscan.py out/wide.mp4 --loop`.
3. If you found a new rule that breaks renders, add it to `references/engine.md` with the
   symptom and the fix, so the next person doesn't hit it.

## Principles

- **Truth first:** nothing in the skill should encourage invented UI, numbers or claims.
- **Every frame is a pure function of time:** no timers, randomness or network in renders.
- **Measure, don't guess:** prefer a check that proves something over a note that hopes for it.

By contributing you agree your work is released under the MIT License.
