#!/usr/bin/env python3
"""Prove every sound effect lands on its cue in a finished video.

Usage (from the project root):
  python3 <skill>/scripts/audio/verify.py out/vertical.final.mp4
  python3 <skill>/scripts/audio/verify.py out/clips/hook.final.mp4 --solo hook

For each cue in docs/cues.json, finds where that effect actually sits in the video's
soundtrack (cross-correlation with the effect file, so music underneath doesn't fool
it) and reports the error. Fails if any effect is more than 10 ms off.
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from common import SR, clock, cue_time, load, read_project  # noqa: E402

TOLERANCE_MS = 10


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    y = load(sys.argv[1])
    cfg = read_project()
    solo = sys.argv[sys.argv.index("--solo") + 1] if "--solo" in sys.argv else None
    shift, dur = clock(cfg, solo)
    cues = json.loads(Path("docs/cues.json").read_text())
    kit = json.loads(Path("docs/kit.json").read_text())

    worst = 0.0
    for c in cues:
        t = cue_time(c, cfg) - shift
        if not (0 <= t < dur):
            continue  # belongs to another scene
        k = kit[c["sound"]]
        tpl = load(k["file"])
        expected_start = t - k["hit"]
        pad = 0.15
        a = max(0, int((expected_start - pad) * SR))
        seg = y[a:a + len(tpl) + int(2 * pad * SR)]
        if len(seg) < len(tpl):
            print(f"{c['sound']:12s} at {t:7.3f}s  ✗ outside the video")
            worst = max(worst, 1e9)
            continue
        corr = np.correlate(seg, tpl, mode="valid")
        found_start = (a + int(np.argmax(np.abs(corr)))) / SR
        err = (found_start - expected_start) * 1000
        worst = max(worst, abs(err))
        mark = "✓" if abs(err) <= TOLERANCE_MS else "✗"
        print(f"{c['sound']:12s} cue {t:7.3f}s  landed {found_start + k['hit']:7.3f}s  error {err:+6.1f} ms  {mark}")

    if worst <= TOLERANCE_MS:
        print(f"All effects within {TOLERANCE_MS} ms of their cues.")
    else:
        sys.exit(f"Some effects are off by more than {TOLERANCE_MS} ms.")


if __name__ == "__main__":
    main()
