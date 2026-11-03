# Cards kit

Code-rendered 1080x1920 Reels in the halftone look (navy, cream cards, yellow/red, Alfa Slab + JetBrains Mono + Archivo).
Three modes, chosen by `mode` in the piece's `data.js` (`window.DATA = {...}`):

| mode | what it is | length |
|---|---|---|
| `game` | "Real or fake?": 3 exhibits, vote countdown, **answer held back** ("ANSWER TOMORROW"), follow card | ~24 s |
| `reveal` | next day: "Yesterday, one of these was real", FAKE/REAL stamps, the real story + sources, follow card | ~14 s |
| `fact` | "Sounds fake. It's real.": hook card, 2-4 beat cards, payoff card + sources, follow card | 20-30 s |

Examples: `studio/films/game-pigeon/data.js`, `studio/films/reveal-pigeon/data.js`, `studio/films/fact-01/data.js`.
Icons are SVG `<g id>` defs in `index.html` (ship, carrier, tower, wheel, lamp, pigeon, ...); add new ones there (flat shapes, 260x230 box, #111318 5px outline, no logos or real photos).

Build (render ~1-2 min on 2 cores, score composed in numpy, loudness about -14 LUFS):
```
PROBE="0 3 8 12" sh studio/kits/cards/build.sh studio/films/<piece>   # stills -> <piece>/out/probe.jpg
sh studio/kits/cards/build.sh studio/films/<piece>                     # -> <piece>/out/<piece>.mp4 + out/review.jpg
```
Every real claim on screen needs a row in the piece's FACTS.md. Fake items in a game must be labelled FAKE in the reveal with the briefing they come from.
