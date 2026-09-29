# Sound: real recordings, measured, on the beat

Sound is where "AI video" starts feeling like a film. Picture and sound share one
clock: scenes use `s.at(n)`, cues use `{"scene": id, "beat": n}`, both read `bpm` and
`beatOffset` from `project.json`.

## Rule 1: real recordings, not code-made beeps

Synthesized clicks and music are the fastest way to make a good video feel cheap.
Default to real recordings with a license that allows commercial use:

- **Mixkit** (mixkit.co): free music and sound effects, commercial use allowed.
- Any track the user owns or has licensed.

Record every file's source URL and license in `docs/AUDIO.md` (created by `kit.py`).
Only synthesize sound when the user explicitly asks for it, or no recording can be
used; say so in the delivery note.

## The workflow

```bash
# 1. Put the files in place
#    assets/audio/music.mp3        one track, ideally 110-125 BPM with a clear drop
#    assets/audio/sfx/*.wav|mp3    one short sound per event type: click, whoosh, pop, ding...

# 2. Measure the music: tempo, beat grid, downbeats, drop
python3 <skill>/scripts/audio/analyze.py assets/audio/music.mp3

# 3. Line the song up so the drop lands on the key visual moment (film beat N)
python3 <skill>/scripts/audio/analyze.py assets/audio/music.mp3 --drop-at-beat proof:0   # drop on beat 0 of scene "proof"
node <skill>/scripts/shells.mjs                # picks up the new bpm

# 4. Measure the effects
python3 <skill>/scripts/audio/kit.py assets/audio/sfx

# 5. Write docs/cues.json while building scenes (same beats as the picture)
#    [{"scene": "demo", "beat": 3, "sound": "click"}, {"scene": "proof", "beat": 0, "sound": "whoosh", "gain": -6}]

# 6. Render: render-all.sh mixes, attaches sound to every format, and verifies sync
bash <skill>/scripts/render-all.sh draft
```

Tools on their own: `mix.py` (writes `out/mix.wav`), `mux.sh` (attaches it to videos
as `*.final.mp4`), `verify.py` (proves every effect landed within 10 ms).

## Rule 2: never trust an automatic beat grid blindly

- `analyze.py` finds the drop from **bass energy**, not from the beat tracker: the jump into
  the loudest section (a kick entering over silence jumps more in dB but isn't the drop). It
  lists the other big jumps, and snaps to the grid only when they agree within 50 ms.
- Always open `docs/beats.png` (waveform with beats and the drop marked).
- If the tempo or drop is wrong, override it: `--bpm 120` or `--drop 64.06`.
- The tools measure; they never hear. Tell the user to listen before building on the
  music, and say so in the delivery note.

## Rule 3: every effect lands on its hit, not its start

Sounds peak late: a whoosh can hit its loudest 400-700 ms in. `kit.py` measures each
file's first strong hit, and `mix.py` shifts the effect so that hit lands on the cue.

`kit.py` also warns about:
- **Two equal hits** (a click's press and release): it syncs on the first. Check that's right.
- **Long files**: trim to the part you need.
- **Quiet files.**

MP3s can hide ~25 ms of decoder delay; every tool decodes through ffmpeg, which removes it.

## Rule 4: timing

- Start the music on a downbeat. Big moments on downbeats (every 4 beats).
- The drop lands on the key visual moment (the payoff, the product reveal, the number).
- One effect per visible event: a click when the cursor clicks, a whoosh when something
  crosses the frame, a pop when something appears. No effect without a visible cause.
- Keep effects under the music: start around -3 to -6 dB (`"gain"` in a cue), then adjust.

## Rule 5: loudness

The mix is normalised to **-14 LUFS**, true peak -1 dB (what social platforms
normalise to). If loud peaks cap the gain, `mix.py` uses a latency-compensated peak
limiter (at 4x sample rate) so sync is untouched. It prints the final loudness.

## Assume no sound

Most feeds autoplay muted. Every beat must also work as text on screen: sound makes
the film better, it must never carry information alone.
