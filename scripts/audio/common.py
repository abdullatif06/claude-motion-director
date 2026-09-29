"""Shared audio helpers for Motion Studio. Needs numpy, scipy and ffmpeg."""
import json
import subprocess
from pathlib import Path

import numpy as np

SR = 48000


def load(path, sr=SR, mono=True):
    """Decode any audio file through ffmpeg to float32 at `sr`.

    Decoding with ffmpeg (instead of reading MP3 frames directly) removes the
    encoder delay some MP3s hide (~25 ms), so beats don't land a hair late.
    Returns an array of shape (n,) if mono, else (n, 2).
    """
    ch = 1 if mono else 2
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(path), "-f", "f32le", "-acodec", "pcm_f32le",
         "-ac", str(ch), "-ar", str(sr), "-"],
        check=True, capture_output=True,
    ).stdout
    a = np.frombuffer(raw, dtype=np.float32).copy()
    return a if mono else a.reshape(-1, 2)


def save_wav(path, audio, sr=SR):
    """Write float audio (n,) or (n, 2) as 24-bit WAV via ffmpeg."""
    audio = np.asarray(audio, dtype=np.float32)
    ch = 1 if audio.ndim == 1 else audio.shape[1]
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(sr), "-ac", str(ch), "-i", "-",
         "-c:a", "pcm_s24le", str(path)],
        input=audio.tobytes(), check=True,
    )


def lowpass(x, cutoff, sr=SR):
    from scipy.signal import butter, sosfiltfilt
    return sosfiltfilt(butter(4, cutoff, "low", fs=sr, output="sos"), x)


def rms_db(seg):
    return 10 * np.log10(np.mean(seg.astype(np.float64) ** 2) + 1e-12)


def loud_regions(x, sr=SR, rel=0.8):
    """Loud regions of a sound: [(start_s, end_s, hit_s), ...].

    Loudness is a 25 ms RMS envelope (smooth enough for noisy sounds like whooshes); a region is where it stays above `rel` of its
    maximum, and a dip longer than 30 ms ends it. The hit is the loudest raw sample
    within 10 ms of the region's envelope peak.
    """
    x = np.asarray(x, dtype=np.float64)
    win = max(1, int(0.025 * sr))
    env = np.sqrt(np.convolve(x ** 2, np.ones(win) / win, mode="same"))
    idx = np.nonzero(env >= env.max() * rel)[0]
    if len(idx) == 0:
        return []
    splits = np.nonzero(np.diff(idx) > int(0.03 * sr))[0]
    groups = np.split(idx, splits + 1)
    out = []
    for g in groups:
        a, b = g[0], g[-1]
        p = a + int(np.argmax(env[a:b + 1]))
        r = int(0.01 * sr)
        lo, hi = max(0, p - r), min(len(x), p + r)
        hit = lo + int(np.argmax(np.abs(x[lo:hi])))
        out.append((a / sr, b / sr, hit / sr))
    return out


def first_peak(x, sr=SR):
    """Time of the sound's first strong hit, in seconds.

    The FIRST loud region, not the loudest overall: a click has a press and a release
    at similar volume, and the press must land on the event. Loudness follows the
    envelope, so a whoosh's hit is where it is loudest, not where its noise starts.
    """
    r = loud_regions(x, sr)
    return r[0][2] if r else 0.0


def scene_windows(cfg):
    """{scene_id: (start_s, length_s)} on the film clock, from project.json scenes."""
    bl = 60 / float(cfg.get("bpm", 120))
    t = float(cfg.get("beatOffset", 0))
    out = {}
    for sc in cfg.get("scenes", []):
        out[sc["id"]] = (t, sc["beats"] * bl)
        t += sc["beats"] * bl
    return out


def cue_time(c, cfg):
    """Film time of a cue: {"t": s} | {"beat": n} (film beats) | {"scene": id, "beat": n} (beats into that scene)."""
    if "t" in c:
        return float(c["t"])
    bl = 60 / float(cfg.get("bpm", 120))
    if "scene" in c:
        win = scene_windows(cfg).get(c["scene"])
        if win is None:
            raise SystemExit(f"Cue refers to scene '{c['scene']}', which is not in project.json")
        return win[0] + c["beat"] * bl
    return float(cfg.get("beatOffset", 0)) + c["beat"] * bl


def clock(cfg, solo=None):
    """(shift, duration): the window of the film being rendered. Solo = one scene from 0."""
    if solo:
        win = scene_windows(cfg).get(solo)
        if win is None:
            raise SystemExit(f"No scene '{solo}' in project.json")
        return win
    return 0.0, float(cfg["duration"])


def read_project(path="project.json"):
    return json.loads(Path(path).read_text())


def write_project(cfg, path="project.json"):
    Path(path).write_text(json.dumps(cfg, indent=2) + "\n")
