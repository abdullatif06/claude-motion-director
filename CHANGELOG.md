# Changelog

## 0.1.0 (2026-09-29)

First release.

- Director workflow on HyperFrames: intake, assets, LOOK, sound, shot list gate, scenes as
  clips, critique loop, multi-format render, delivery checklist
- Motion toolkit: closed-form springs (4 presets), multi-target tracks, stretching
  indicators, log-space camera zoom, morphing boxes, clip-path word rises, motion blur render
- Sound toolkit: tempo and beat grid, drop detection from bass energy, effect hit measuring,
  mixing to -14 LUFS with a latency-compensated peak limiter, sync verification
- Review toolkit: stills preview, contact / phone / strip sheets, pop scan, loop check,
  reference-film study, 8-criterion critique prompt
- Worked example: the Actova launch film

### Known limitations

- `npx hyperframes capture` (website capture) is documented but was not exercised in our test
  runs: our build environment could not reach external sites. Please report issues.
- The beat analyzer assumes a steady tempo. Override with `--bpm` / `--drop` for live music.
- English only. Right-to-left scripts (Arabic, Hebrew) are not handled yet.
- Motion blur rendering is slow on CPUs without a GPU (about 25 s of rendering per second of film).
- The Actova example ships with generated placeholder audio.
