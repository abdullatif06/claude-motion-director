#!/usr/bin/env python3
"""Mix music and sound effects on the film's clock, normalised to -14 LUFS.

Usage (from the project root):
  python3 <skill>/scripts/audio/mix.py                    -> out/mix.wav (whole film)
  python3 <skill>/scripts/audio/mix.py --solo hook        -> out/mix.wav for one scene's clip

Reads:
  project.json   duration, bpm, beatOffset, and optional
                 "music": {"file": ..., "start": seconds into the song, "gain": dB}
  docs/cues.json [{"scene": "hook", "beat": 3, "sound": "click"},   <- beats into a scene (preferred)
                  {"beat": 6, "sound": "pop"},                     <- film beats
                  {"t": 3.2, "sound": "whoosh", "gain": -4}, ...]  <- seconds
                 Beats use the same clock as the scenes (s.at(n)), so picture and
                 sound can't drift. "sound" is a name from docs/kit.json (run kit.py first).
Each effect is shifted so its measured hit lands exactly on its cue.
Loudness: two-pass ffmpeg loudnorm to -14 LUFS, true peak -1 dB (what social platforms
normalise to).
"""
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from common import SR, clock, cue_time, load, read_project, save_wav  # noqa: E402

TARGET_LUFS, TRUE_PEAK = -14, -1


def db(g):
    return 10 ** (g / 20)


def main():
    cfg = read_project()
    solo = sys.argv[sys.argv.index("--solo") + 1] if "--solo" in sys.argv else None
    shift, dur = clock(cfg, solo)
    n = int(round(dur * SR))
    mix = np.zeros((n, 2), dtype=np.float64)

    music = cfg.get("music")
    if music:
        m = load(music["file"], mono=False)
        s = int(round((float(music.get("start", 0)) + shift) * SR))
        seg = m[s:s + n] * db(float(music.get("gain", -6)))
        mix[:len(seg)] += seg
        fade = int(0.5 * SR)  # short fade at the end so the film never cuts mid-note
        mix[max(0, n - fade):] *= np.linspace(1, 0, min(fade, n))[:, None]
        print(f"music: {music['file']} from {float(music.get('start', 0)):.3f}s")

    cues_path = Path("docs/cues.json")
    cues = json.loads(cues_path.read_text()) if cues_path.exists() else []
    kit = json.loads(Path("docs/kit.json").read_text()) if cues else {}
    cache = {}
    for c in cues:
        t = cue_time(c, cfg) - shift
        if not (-0.5 < t < dur + 0.5):
            continue  # belongs to another scene
        k = kit.get(c["sound"])
        if not k:
            sys.exit(f"Cue sound '{c['sound']}' not in docs/kit.json. Run kit.py or fix the name.")
        if c["sound"] not in cache:
            cache[c["sound"]] = load(k["file"], mono=False)
        sfx = cache[c["sound"]] * db(float(c.get("gain", -3)))
        start = int(round((t - k["hit"]) * SR))  # the hit, not the file start, lands on t
        a, b = max(0, start), min(n, start + len(sfx))
        if b > a:
            mix[a:b] += sfx[a - start:b - start]
        print(f"cue {c['sound']:12s} at {t:7.3f}s")

    Path("out").mkdir(exist_ok=True)
    raw = Path("out/.mix_raw.wav")
    save_wav(raw, mix.astype(np.float32))

    # Two-pass loudnorm: measure, then apply with the measured values (linear, no pumping).
    probe = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", str(raw), "-af",
         f"loudnorm=I={TARGET_LUFS}:TP={TRUE_PEAK}:LRA=11:print_format=json", "-f", "null", "-"],
        capture_output=True, text=True,
    ).stderr
    stats = json.loads(re.findall(r"\{[^{}]*\}", probe, re.S)[-1])
    if float(stats["input_i"]) < -70:
        print("warning: the mix is silent (no music and no cues?)")
        raw.rename("out/mix.wav")
        return
    af = (f"loudnorm=I={TARGET_LUFS}:TP={TRUE_PEAK}:LRA=11:measured_I={stats['input_i']}:"
          f"measured_TP={stats['input_tp']}:measured_LRA={stats['input_lra']}:"
          f"measured_thresh={stats['input_thresh']}:offset={stats['target_offset']}:linear=true")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-af", af, "-ar", str(SR),
                    "-c:a", "pcm_s24le", "out/mix.wav"], check=True)
    lufs = measure("out/mix.wav")
    if lufs < TARGET_LUFS - 1:
        # Linear gain was capped by peaks (loud kicks, sharp effects). Apply the gain
        # directly with a peak limiter (latency-compensated, so sync is untouched),
        # then correct once for what the limiter took away.
        gain = TARGET_LUFS - float(stats["input_i"])
        for _ in range(2):
            limit(raw, "out/mix.wav", gain)
            got = measure("out/mix.wav")
            gain += TARGET_LUFS - got
        lufs = got
        print("note: peaks capped the gain, so a peak limiter was used")
    raw.unlink()
    print(f"wrote out/mix.wav ({dur:.2f}s, {lufs:.1f} LUFS, target {TARGET_LUFS})")


def limit(src, dst, gain_db):
    ceiling = 10 ** ((TRUE_PEAK - 0.5) / 20)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-af",
                    f"volume={gain_db:.2f}dB,aresample={SR * 4},"  # limit at 4x so peaks between samples are caught too
                    f"alimiter=limit={ceiling:.4f}:attack=2:release=60:level=0:latency=1,aresample={SR}",
                    "-ar", str(SR), "-c:a", "pcm_s24le", str(dst)], check=True)


def measure(path):
    out = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-af", "ebur128", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", out)[-1])


if __name__ == "__main__":
    main()
