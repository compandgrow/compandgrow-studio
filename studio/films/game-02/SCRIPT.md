format_version: 2 · experiment: Game #2. "COMMENT 1, 2 OR 3" on screen from frame 0 and ~2.5 s cards, so the vote prompt lands before ~8 s (game #1 lost its average viewer at ~8.4 s, during card 2)

# GAME #2 — "Real or fake?" · Thu 2026-11-19 16:28 PT · 21.0 s

Build it like `studio/films/game-01/` (index.html scenes + `T` timing table + `window.STAMPS` for `audio.py`). There is no voice-over, as in game #1: score and foley only, and all text is on screen. Same top bar: `CASE FILES · REAL OR FAKE?` / `@compandgrow`. Same tile / card / stamp CSS. The real one sits in **position 3** (game #1 had it in 2). Drawings are in-house SVG only: no photos, no logos, no museum or military marks.

| scene | time (s) | on screen |
|---|---|---|
| hook | 0.0–1.5 | **Frame 0 = cover**: big `ONLY ONE WAS` / `REALLY BUILT.` (REALLY BUILT in yellow). The numbered 3-tile strip shows the tiles as `1 SILENT WING` · `2 LIGHTNING CELL` · `3 SAUCER`. Bar under the strip: `ONE IS REAL · COMMENT 1, 2 OR 3`. All of it is visible on frame 0, with no fade-in. |
| c1 | 1.5–4.0 | Card 1 (EXHIBIT 1 OF 3), drawing of a flat foil wing over a seamless with faint downward wind lines. h2: `A foil wing that flew 12 km. Silent.` stat: `TRIAL 03: 12 KM` |
| c2 | 4.0–6.5 | Card 2 (EXHIBIT 2 OF 3), drawing of a glowing ball in a ring cage. h2: `A power cell running on caught ball lightning.` stat: `TRIAL 03: 6 HOURS` |
| c3 | 6.5–9.0 | Card 3 (EXHIBIT 3 OF 3), drawing of a flat round saucer silhouette hovering just off the ground. h2: `A flying saucer built for the US military.` stat: `TWO PROTOTYPES` |
| vote | 9.0–11.5 | Strip returns. `LOCK IT IN` with a counter 3 → 2 → 1 (ticks at 9.6, 10.3, 11.0) and `COMMENT 1, 2 OR 3` |
| reveal | 11.5–19.0 | Stamps hit in order 1, 2, 3 (below). The fake tiles dim to 55%. Tile 3 scales up 8%. |
| end | 19.0–21.0 | `NEW CASE EVERY SUNDAY.` / `GAME EVERY THURSDAY.` / `FULL BRIEFINGS on @compandgrow` |

Corner prompt `1 / 2 / 3?` stays visible in the top-right of every card scene (1.5–9.0 s). The vote prompt is therefore on screen for the whole first 11.5 s.

## Reveal text (11.5–19.0)
- 12.0 s **FAKE** stamp on tile 1. Under it: `from our STILLWING briefing` / `the real 2018 ion plane flew ~60 m`. The 12 km wing is ours. Do **not** name MIT here, because it would sit next to STILLWING.
- 12.7 s **FAKE** stamp on tile 2. Under it: `from our EMBER briefing`.
- 13.8 s **REAL** stamp on tile 3, then:
  - title: `AVROCAR · 1959`, small line `Avro Canada VZ-9`
  - body (3 lines): `Built for the US Army and Air Force.` / `It never got more than a few feet` / `off the ground. Cancelled in 1961.`
  - source: `Source: National Museum of the U.S. Air Force` (text only, no logo)
- Body text holds about 5 s (to 19.0), which is enough to read 17 words.

## STAMPS for audio.py (DUR = 21.0)
`whoosh: [1.5, 4.0, 6.5, 9.0, 11.5, 19.0] · tick: [9.6, 10.3, 11.0] · stamp: [12.0, 12.7] · real: [13.8] · pop: [0.0]`. Riser 11.0→11.5, kick stops after 19.0 (scale game-01's fixed times: riser 17.8–19.0 → 11.0–11.5, pad dip 18–19 → 11.0–11.5, kick cut 25.6 → 19.0, DUR 28 → 21).

## Devices
| # | card | truth | source |
|---|---|---|---|
| 1 | A foil wing that flew 12 km. Silent. | FAKE | STILLWING (lifter film, Nov 15). The 12 km trial is invented (lifter/FACTS.md). The real 2018 ion plane flew about 60 m (lifter/FACTS.md, MIT News / MIT Technology Review). |
| 2 | A power cell running on caught ball lightning. | FAKE | EMBER (film, Nov 8). The 6 h trial is invented (ember/FACTS.md). |
| 3 | A flying saucer built for the US military. | **REAL** | Avro Canada VZ-9 Avrocar (game-02/FACTS.md). Built for the US Army and Air Force (took over in 1958), first free flight in 1959, never more than a few feet off the ground, cancelled 1961, two built (NMUSAF fact sheet, arXiv 1507.06916, Flying, Wikipedia). |

Rules kept: no exact height (3 ft vs 2 m), no speed, no money, cancellation year only. No UFO, cover-up or "secret" framing anywhere. The card says "built for the US military", nothing more.
