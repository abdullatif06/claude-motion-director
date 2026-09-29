#!/usr/bin/env python3
"""Pop scan and loop check: find glitches the eye misses at full speed.

Usage (from the project root):
  python3 <skill>/scripts/review/popscan.py out/vertical.final.mp4 [--loop]

Pop: a single frame that jumps far more than its neighbours (frame i differs from both
i-1 and i+1, while i-1 and i+1 are close to each other). Viewers notice these on the
third loop even when you don't at full speed.
--loop: also checks that the last frame equals the first, so an X/Instagram loop is seamless.

Prints every pop with its time and writes out/review/pops.png (each pop with its
neighbours) when any are found. Needs numpy and ffmpeg.
"""
import subprocess
import sys
from pathlib import Path

import numpy as np

SMALL = 160  # analyse at 160 px wide: fast, and pops are big by definition


def frames(path):
    info = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                           "stream=width,height,r_frame_rate", "-of", "csv=p=0", path],
                          capture_output=True, text=True, check=True).stdout.strip().split(",")
    w, h = int(info[0]), int(info[1])
    num, den = map(int, info[2].split("/"))
    fps = num / den
    sh = int(round(h * SMALL / w / 2)) * 2
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vf", f"scale={SMALL}:{sh}",
                          "-f", "rawvideo", "-pix_fmt", "gray", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, sh, SMALL).astype(np.float32), fps


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    path, loop = sys.argv[1], "--loop" in sys.argv
    f, fps = frames(path)
    d = lambda a, b: float(np.mean(np.abs(a - b)))
    pops = []
    for i in range(1, len(f) - 1):
        a, b, skip = d(f[i - 1], f[i]), d(f[i], f[i + 1]), d(f[i - 1], f[i + 1])
        jump = min(a, b)
        if jump > 6 and jump > 3 * (skip + 1):
            pops.append((i, jump))

    ok = True
    if pops:
        ok = False
        print(f"✗ {len(pops)} single-frame pop(s):")
        for i, j in pops:
            print(f"  frame {i} at {i / fps:.3f}s (jump {j:.1f})")
        Path("out/review").mkdir(parents=True, exist_ok=True)
        i = pops[0][0]
        t0 = max(0, (i - 1) / fps)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t0:.3f}", "-i", path, "-vf",
                        "scale=480:-2,tile=3x1:padding=6:color=0x333333", "-frames:v", "1", "out/review/pops.png"])
        print("  first pop with its neighbours: out/review/pops.png")
    else:
        print(f"✓ no single-frame pops in {len(f)} frames")

    if loop:
        seam = d(f[0], f[-1])
        if seam < 1.0:
            print(f"✓ loop seam: last frame matches the first (difference {seam:.2f})")
        else:
            ok = False
            print(f"✗ loop seam: last frame differs from the first (difference {seam:.2f}); the loop will jump")

    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
