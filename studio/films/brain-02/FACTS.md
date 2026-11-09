# brain-02 · How many turns does gear C make?

Engineering brain test (format v3 trial `tunable.brain_test`, type "calc"). No real-world historical claims; the
puzzle is generated and solved by `puzzle.py` (geometry helpers in `studio/kits/cards/brain/gears.py`).

## Answer
**10 full turns.**

## Working (computed with exact fractions, `python3 puzzle.py`)
- Gears that mesh move the same number of teeth past the contact point, so turns x teeth is the same for every
  gear in the train.
- Gear A: 3 turns x 40 teeth = 120 teeth pass the mesh.
- Gear B (idler): 120 / 30 = 4 turns. It passes the same 120 teeth on to C.
- Gear C: 120 / 12 = **10 turns**. The idler B changes direction, not the count:
  3 x 40/30 x 30/12 = 3 x 40/12 = 10.
- Directions (not asked): A clockwise, B anticlockwise, C clockwise.

## Drawing matches the maths
- One module (12 px) for all gears; pitch radius = 6 px per tooth: A 240, B 180, C 72 px.
- Each gear is drawn with exactly its stated tooth count (40, 30, 12).
- Meshes measured from the coordinates: A-B centre distance 420.00 = 240 + 180; B-C 252.00 = 180 + 72;
  A-C 501.0, far more than the tip radii 252 + 84, so A and C do not touch.
- Tooth interleave check: worst error 6.7e-16 of a tooth pitch.
