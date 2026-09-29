#!/usr/bin/env python3
"""Measure the sound-effect kit so every effect can land exactly on its event.

Usage (from the project root):
  python3 <skill>/scripts/audio/kit.py assets/audio/sfx

For each file: length, the time of its first strong hit (the part that must land on
the event), and warnings. Writes docs/kit.json (used by mix.py) and docs/AUDIO.md
(a table to keep with the project; fill in source and license for every file).

Why this matters: sounds peak late. A whoosh can hit its loudest 700 ms in, so
starting it on the event makes it land late. mix.py shifts every effect so its
measured hit lands on the cue.
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from common import SR, first_peak, load, loud_regions  # noqa: E402

EXT = {".wav", ".mp3", ".m4a", ".aac", ".ogg", ".flac", ".aif", ".aiff"}


def warnings_for(y, hit):
    w = []
    dur = len(y) / SR
    if dur > 3:
        w.append(f"long file ({dur:.1f}s): trim it to the part you need")
    regions = loud_regions(y)
    if len(regions) > 1:
        w.append(f"second hit at {regions[1][2]*1000:.0f} ms, as loud as the first (press/release?): synced on the first")
    if np.abs(y).max() < 0.05:
        w.append("very quiet file")
    return w


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    folder = Path(sys.argv[1])
    files = sorted(p for p in folder.iterdir() if p.suffix.lower() in EXT)
    if not files:
        sys.exit(f"No audio files in {folder}")

    kit, rows = {}, []
    for p in files:
        y = load(p)
        hit = first_peak(y)
        warn = warnings_for(y, hit)
        kit[p.stem] = {"file": str(p), "length": round(len(y) / SR, 3), "hit": round(hit, 4)}
        rows.append((p.name, len(y) / SR, hit, "; ".join(warn)))
        print(f"{p.name:32s} {len(y)/SR:6.2f}s  hit at {hit*1000:6.1f} ms  {'⚠ ' + '; '.join(warn) if warn else ''}")

    Path("docs").mkdir(exist_ok=True)
    Path("docs/kit.json").write_text(json.dumps(kit, indent=1) + "\n")
    md = ["# Audio kit", "", "Every file must be a real recording with a license that allows commercial use.", "",
          "| File | Source (URL) | License | Length | Hit | Notes |", "|---|---|---|---|---|---|"]
    md += [f"| {n} | | | {l:.2f}s | {h*1000:.0f} ms | {w} |" for n, l, h, w in rows]
    Path("docs/AUDIO.md").write_text("\n".join(md) + "\n")
    print("wrote docs/kit.json and docs/AUDIO.md (fill in source and license)")


if __name__ == "__main__":
    main()
