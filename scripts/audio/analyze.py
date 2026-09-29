#!/usr/bin/env python3
"""Measure a music track: tempo, beat grid, downbeats and the drop.

Usage (from the project root):
  python3 <skill>/scripts/audio/analyze.py assets/audio/music.mp3
  python3 <skill>/scripts/audio/analyze.py assets/audio/music.mp3 --drop-at-beat 16
  python3 <skill>/scripts/audio/analyze.py assets/audio/music.mp3 --drop-at-beat proof:0   # beat 0 of scene "proof"
  python3 <skill>/scripts/audio/analyze.py music.mp3 --bpm 120        # override a wrong tempo
  python3 <skill>/scripts/audio/analyze.py music.mp3 --drop 64.06     # override a wrong drop

Writes docs/beats.json and docs/beats.png (waveform with beats and the drop marked).
With --drop-at-beat N it also lines the song up with the film: the drop lands on
film beat N, and project.json gets bpm, beatOffset and music.start.

Never trust an automatic beat grid blindly: open docs/beats.png and listen. The drop
is found from bass energy, not from the beat tracker, because trackers are often a
beat or two off. Assumes a steady tempo (true for almost all stock music).
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
from scipy.signal import stft

sys.path.insert(0, str(Path(__file__).parent))
from common import SR, load, lowpass, rms_db, read_project, write_project  # noqa: E402

HOP = 480  # 10 ms at 48 kHz


def onset_envelope(y):
    _, _, Z = stft(y, fs=SR, nperseg=2048, noverlap=2048 - HOP, boundary=None, padded=False)
    mag = np.log1p(np.abs(Z) * 100)
    flux = np.maximum(0, np.diff(mag, axis=1)).sum(axis=0)
    flux = np.concatenate([[0], flux])
    flux -= np.convolve(flux, np.ones(50) / 50, mode="same")  # remove slow trend
    return np.maximum(flux, 0)


def estimate_tempo(env, lo=70, hi=180):
    fps = SR / HOP
    env = env - env.mean()
    ac = np.correlate(env, env, mode="full")[len(env) - 1:]
    best, best_score = 120.0, -np.inf
    for bpm in np.arange(lo, hi, 0.1):
        lag = fps * 60 / bpm
        score = 0.0
        for m in (1, 2, 4):  # a true tempo also correlates at 2 and 4 beats
            l = lag * m
            i = int(l)
            if i + 1 >= len(ac):
                break
            score += ac[i] + (ac[i + 1] - ac[i]) * (l - i)
        score *= np.exp(-0.5 * (np.log2(bpm / 120) / 0.9) ** 2)  # gentle prior against octave errors
        if score > best_score:
            best, best_score = bpm, score
    return round(best, 2)


FRAME_CENTER = 1024 / SR  # an STFT frame describes the middle of its window


def comb(env, period_frames):
    """Best phase for a beat period, and how well the grid fits the onsets."""
    idx = np.arange(len(env))
    phases = np.arange(0, period_frames, 0.25)
    k = np.arange(0, (len(env) - 1) / period_frames)
    pos = phases[:, None] + k[None, :] * period_frames
    valid = pos < len(env) - 1
    vals = np.where(valid, np.interp(np.minimum(pos, len(env) - 1), idx, env), 0)
    scores = vals.sum(axis=1)
    i = int(np.argmax(scores))
    return phases[i], scores[i]


def refine_tempo(env, coarse):
    """Search tempo finely around the coarse estimate, jointly with the beat phase.
    A tempo off by 0.3 BPM drifts ~70 ms over 30 s and lands the drop on the wrong beat."""
    fps = SR / HOP
    best = (coarse, 0.0, -np.inf)
    for bpm in np.arange(coarse - 1.5, coarse + 1.5, 0.01):
        phase, score = comb(env, fps * 60 / bpm)
        if score > best[2]:
            best = (bpm, phase, score)
    bpm, phase, _ = best
    return round(float(bpm), 2), phase * HOP / SR + FRAME_CENTER


def find_drop(y_low, period):
    """The drop: the jump in bass energy INTO THE LOUDEST SECTION, refined to 20 ms.

    Independent of the beat grid. The biggest relative jump is often not the drop (a
    kick entering over silence jumps more in dB than the real drop), so among all
    jumps of 6 dB or more, pick the one whose following bar is loudest.
    Returns (time, jump_db, candidates) where candidates = [(time, jump_db, level_after)].
    """
    bar = 4 * period
    step = 0.02
    n = len(y_low) / SR
    ts = np.arange(bar, n - bar, step)
    if len(ts) == 0:
        return None
    before = np.array([rms_db(y_low[int((t - bar) * SR):int(t * SR)]) for t in ts])
    after = np.array([rms_db(y_low[int(t * SR):int((t + bar) * SR)]) for t in ts])
    jump = after - before
    cands = []
    i = 0
    while i < len(ts):  # one candidate per region where the jump exceeds 6 dB
        if jump[i] >= 6:
            j = i
            while j + 1 < len(ts) and jump[j + 1] >= 6:
                j += 1
            k = i + int(np.argmax(jump[i:j + 1]))
            cands.append((float(ts[k]), float(jump[k]), float(after[k])))
            i = j + 1
        else:
            i += 1
    if not cands:
        k = int(np.argmax(jump))
        cands = [(float(ts[k]), float(jump[k]), float(after[k]))]
    coarse, best_jump, _ = max(cands, key=lambda c: c[2])
    b = rms_db(y_low[int((coarse - bar) * SR):int(coarse * SR)])
    a = rms_db(y_low[int(coarse * SR):int((coarse + bar) * SR)])
    mid = (a + b) / 2
    drop = coarse
    for t in np.arange(coarse - 0.3, coarse + 0.3, 0.02):
        if t >= 0 and rms_db(y_low[int(t * SR):int((t + 0.02) * SR)]) >= mid:
            drop = t
            break
    return round(float(drop), 3), round(best_jump, 1), cands


def plot(y, beats, downbeats, drop, path):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("  (matplotlib not installed: skipping beats.png)")
        return
    t = np.arange(len(y)) / SR
    step = max(1, len(y) // 20000)
    fig, ax = plt.subplots(figsize=(16, 3), dpi=100)
    ax.plot(t[::step], y[::step], lw=0.4, color="#555")
    for b in beats:
        ax.axvline(b, color="#9ab", lw=0.4)
    for b in downbeats:
        ax.axvline(b, color="#357", lw=1)
    if drop is not None:
        ax.axvline(drop, color="#e0673f", lw=2.5, label=f"drop {drop:.2f}s")
        ax.legend(loc="upper right")
    ax.set_xlim(0, t[-1]); ax.set_yticks([]); ax.set_xlabel("seconds")
    fig.tight_layout(); fig.savefig(path); plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("track")
    ap.add_argument("--bpm", type=float, help="override the detected tempo")
    ap.add_argument("--drop", type=float, help="override the detected drop time (seconds)")
    ap.add_argument("--drop-at-beat", help="line the song up so its drop lands on this film beat, or scene:beat")
    ap.add_argument("--out", default="docs")
    a = ap.parse_args()

    y = load(a.track)
    dur = len(y) / SR
    env = onset_envelope(y)
    if a.bpm:
        bpm = a.bpm
        phase = comb(env, SR / HOP * 60 / bpm)[0] * HOP / SR + FRAME_CENTER
    else:
        bpm, phase = refine_tempo(env, estimate_tempo(env))
    period = 60 / bpm
    y_low = lowpass(y, 150)

    # The comb can lock onto off-beats (hi-hats are the sharpest onsets). Beats carry
    # the kick, so keep whichever grid, on-beat or half a beat later, has more bass.
    def grid_bass(p0):
        return np.mean([rms_db(y_low[int(b * SR):int((b + 0.05) * SR)]) for b in np.arange(p0 % period, dur - 0.1, period)])
    if grid_bass(phase + period / 2) > grid_bass(phase):
        phase += period / 2
    beats = np.arange(phase % period, dur, period)

    bass = [rms_db(y_low[int(b * SR):int((b + 0.05) * SR)]) for b in beats]
    best = int(np.argmax([np.mean(bass[i::4]) for i in range(4)]))
    downbeats = beats[best::4]

    cands = []
    if a.drop:
        drop, jump = a.drop, None
    else:
        found = find_drop(y_low, period)
        drop, jump, cands = found if found else (None, None, [])
    if drop is not None and not a.drop:
        near = beats[np.argmin(np.abs(beats - drop))]
        if abs(near - drop) <= 0.05:  # energy says "about here", the grid says exactly where
            drop = round(float(near), 3)

    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    data = {
        "track": a.track, "duration": round(dur, 3), "bpm": bpm, "beat_period": round(period, 4),
        "first_beat": round(float(beats[0]), 3), "first_downbeat": round(float(downbeats[0]), 3),
        "drop": drop, "drop_jump_db": jump,
        "drop_candidates": [{"t": round(t, 3), "jump_db": round(j, 1)} for t, j, _ in cands],
        "beats": [round(float(b), 3) for b in beats],
        "downbeats": [round(float(b), 3) for b in downbeats],
    }
    (out / "beats.json").write_text(json.dumps(data, indent=1) + "\n")
    plot(y, beats, downbeats, drop, out / "beats.png")

    print(f"tempo {bpm} BPM (beat = {period:.3f}s), first downbeat {data['first_downbeat']}s")
    print(f"drop  {drop}s" + (f" (bass +{jump} dB, into the loudest section)" if jump else ""))
    others = [c for c in cands if abs(c[0] - (drop or -99)) > 1]
    if others:
        print("      other bass jumps (not the drop?): " + ", ".join(f"{t:.2f}s (+{j:.0f} dB)" for t, j, _ in others)
              + "  -> override with --drop <seconds> if one of these is the real drop")
    print(f"wrote {out/'beats.json'} and {out/'beats.png'}: check the drop by eye and by ear")

    if a.drop_at_beat is not None:
        if drop is None:
            sys.exit("No drop found: pass --drop <seconds> first.")
        cfg = read_project()
        target = str(a.drop_at_beat)
        if ":" in target:  # beat counted from the start of a scene
            sid, b = target.split(":")
            beats_before = 0
            for sc in cfg.get("scenes", []):
                if sc["id"] == sid:
                    break
                beats_before += sc["beats"]
            else:
                sys.exit(f"No scene '{sid}' in project.json")
            film_beat = beats_before + float(b)
        else:
            film_beat = float(target)
        start = drop - film_beat * period
        if start < 0:
            sys.exit(f"The drop is at {drop}s: film beat {film_beat:g} would need the song to start before 0. Aim it later in the film.")
        cfg["bpm"] = bpm
        cfg["beatOffset"] = 0
        cfg["music"] = {"file": a.track, "start": round(start, 3)}
        write_project(cfg)
        print(f"aligned: song starts at {start:.3f}s, so its drop lands on film beat {film_beat:g} "
              f"({film_beat * period:.3f}s). project.json updated; re-run shells.mjs.")


if __name__ == "__main__":
    main()
