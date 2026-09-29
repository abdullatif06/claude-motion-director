# Example: Actova launch film

A complete Motion Director run on **Actova**, a fictional AI meeting assistant built for this
case study. Every person, meeting and number is example data.

- 30 s, 120 BPM, 5 scenes (hook, listen, tasks, recap, week), vertical + wide, seamless loop
- `product/index.html`: the product itself (its real screens; the film reuses its markup and CSS)
- `docs/`: the brief, LOOK card, shot list, cue sheet, audio kit and the full critique log
- `src/scenes/`: one file per scene; `00-ui.js` holds the product data and shared helpers
- `review/`: thumbnail, contact sheet and phone sheet from the final render

## Run it

```bash
bash <skill>/scripts/new-project.sh actova-film
cp -R examples/actova/{src,docs,project.json,fonts.css} actova-film/
cd actova-film
# fonts (OFL): npm i @fontsource/inter @fontsource/instrument-serif, copy the latin woff2 files
#   (inter 400-800 normal, instrument-serif 400 italic) into assets/fonts/
# audio: put a track in assets/audio/music.mp3 and effects (pop, click, whoosh, ding) in
#   assets/audio/sfx/, then analyze.py --drop-at-beat tasks:4 and kit.py (see references/sound.md)
bash <skill>/scripts/render-all.sh draft
```

## What the run caught (and the skill learned)

- A child set to `visibility: visible` showed through every other scene
- Fonts must be declared at the project root; masked words and half-open cards fooled the checker
- The brand orange (#FF5A1F) and three avatar colors failed contrast: fixed in the film AND the product
- The drop detector picked the kick entry (8.5 s) over the real drop (16.5 s): it now picks the
  jump into the loudest section and lists the alternatives
- A count-up keyed at its end time never reached "5h 20m" on screen: keyframes mark move starts
- Audio in this example is a generated placeholder, not release quality
