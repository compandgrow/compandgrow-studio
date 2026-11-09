# Cards kit

Code-rendered 1080x1920 Reels in the halftone look (navy, cream cards, yellow/red, Alfa Slab + JetBrains Mono + Archivo).
Four modes, chosen by `mode` in the piece's `data.js` (`window.DATA = {...}`):

| mode | what it is | length |
|---|---|---|
| `game` | "Real or fake?": 3 exhibits, vote countdown, **answer held back** ("ANSWER TOMORROW"), follow card | ~24 s |
| `reveal` | next day: "Yesterday, one of these was real", FAKE/REAL stamps, the real story + sources, follow card | ~14 s |
| `fact` | "Sounds fake. It's real.": hook card, 2-4 beat cards, payoff card + sources, follow card | 20-30 s |
| `brain` | Engineering brain test: moving challenge opener (tag + title + puzzle), puzzle card with countdown ring, "COMMENT YOUR ANSWER" 3-2-1, "ANSWER TOMORROW" follow card | 12-25 s (hook 2.6 + timer + 0.4 + 3.6 + 3.2) |

Examples: `studio/films/brain-01/` (gear direction), `studio/films/brain-02/` (gear-ratio calc), `studio/films/game-pigeon/data.js`, `studio/films/reveal-pigeon/data.js`, `studio/films/fact-01/data.js`.
Icons are SVG `<g id>` defs in `index.html` (ship, carrier, tower, wheel, lamp, pigeon, icecity, bagger, drill, bat, funnel, ...); add new ones there (flat shapes, 260x230 box, #111318 5px outline, no logos or real photos).
Icon parts can move on their own (hook + every card): put `data-a` on an element inside the def: `spin cx cy deg/s`, `flap cx cy deg hz`, `bob px hz`, `drip cx cy period` (slow stretch), `dash px/s` (moving stroke dashes). Fact beats take an optional `size` (h2 px) for long lines; payoff takes `size`, `bodyTop`, `dur`.

Card transitions are a push: the next card slides in during the last 0.3 s of the current one (`XF` in index.html), so there is no empty navy gap; timeline and audio stamps are unchanged (whoosh centred on the push).

Build (render ~1-2 min on 2 cores, score composed in numpy, loudness about -14 LUFS):
```
PROBE="0 3 8 12" sh studio/kits/cards/build.sh studio/films/<piece>   # stills -> <piece>/out/probe.jpg
sh studio/kits/cards/build.sh studio/films/<piece>                     # -> <piece>/out/<piece>.mp4 + out/review.jpg
```
Every real claim on screen needs a row in the piece's FACTS.md. Fake items in a game must be labelled FAKE in the reveal with the briefing they come from.

## Brain tests (`mode: 'brain'`)
The drawing is not hand-made: the piece's `puzzle.py` builds the geometry, computes the answer and writes `puzzle.js`
(`window.PUZZLE = {view, svg}`), `FACTS.md` (answer + working) and `answer.json`. Run `python3 puzzle.py` before build.sh.
`brain/gears.py` places spur gears with one shared module, measures the mesh graph from the coordinates (touch = centre
distance equals sum of pitch radii; any other pair must clear by 2.5 modules or it raises), solves directions/speeds by BFS
and phases the teeth so they interleave. SVG classes `pulse` (scale pulse) and `bob` (float) animate during the puzzle;
never animate gear rotation (it gives the answer away).
`data.js` fields: `tag` (pill above the title), `hook`, `hookSize`, `question`, `timer` (s), `options` ([{k, t, icon: 'cw'|'ccw'}])
or `prompt` (single pill, e.g. 'COMMENT A NUMBER'), optional `chip` (yellow pill under the A/B options for the whole puzzle scene, e.g. 'COMMENT A OR B'; `chipTop` default 1515), `end`. Captions: `captions/main.txt` (never the answer) + `captions/answer.txt`.
