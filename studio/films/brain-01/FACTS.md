# brain-01 · Which way does the last gear turn?

Engineering brain test (format v3 trial `tunable.brain_test`, type "focus"). No real-world historical claims; the
puzzle is generated and solved by `puzzle.py` (geometry helpers in `studio/kits/cards/brain/gears.py`).

## Answer
**CLOCKWISE** (option A).

## Working (computed, `python3 puzzle.py`)
- Rule: two external spur gears in mesh always turn in opposite directions.
- The mesh graph is measured from the drawn coordinates (gears mesh only where the centre distance equals the sum of
  the pitch radii; every other pair is checked to have a clearly visible gap of at least 2.5 modules between tooth tips):
- G1-G2: centre distance 150.00 px = 90 + 60 (pitch circles touch)
- G2-G3: centre distance 138.00 px = 60 + 78 (pitch circles touch)
- G3-G4: centre distance 132.00 px = 78 + 54 (pitch circles touch)
- G4-G5: centre distance 150.00 px = 54 + 96 (pitch circles touch)
- G5-G6: centre distance 156.00 px = 96 + 60 (pitch circles touch)
- G6-G7: centre distance 144.00 px = 60 + 84 (pitch circles touch)
- That is one open chain G1-G2-G3-G4-G5-G6-G7, no branches, no loops (a loop of 3 would lock).
- G1 (yellow) turns clockwise, so directions alternate along the chain: G1 cw, G2 acw, G3 cw, G4 acw, G5 cw, G6 acw,
  G7 cw. G7 (red, marked "?") is 6 meshes from G1; 6 is even, so G7 turns the same way as G1.
- Tooth interleave check (a tooth faces a gap on every line of centres): worst error 6.7e-16 of a tooth pitch.

| gear | teeth | centre (px) | pitch r | meshes with | turns |
|---|---|---|---|---|---|
| G1 | 15 | (0.0, 0.0) | 90 | G2 | clockwise |
| G2 | 10 | (142.7, 46.4) | 60 | G1, G3 | anticlockwise |
| G3 | 13 | (207.4, 168.2) | 78 | G2, G4 | clockwise |
| G4 | 9 | (126.2, 272.2) | 54 | G3, G5 | anticlockwise |
| G5 | 16 | (-18.7, 311.0) | 96 | G4, G6 | clockwise |
| G6 | 10 | (-59.1, 461.7) | 60 | G5, G7 | anticlockwise |
| G7 | 14 | (65.6, 533.7) | 84 | G6 | clockwise |

Module 12 px for every gear, so teeth sizes match and the pitch radius is 6 px per tooth. The chain changes heading
at every joint (18, 62, 128, 165, 105, 30 degrees), so it is not a straight line.
