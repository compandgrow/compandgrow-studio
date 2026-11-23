# brain-03 · How many kg of pull holds the 150 kg crate?

Engineering brain test (format v4 trial `tunable.brain_test`, type "calc"). No real-world historical claims; the
puzzle is generated and solved by `puzzle.py` (no kit helper; the rope path is built and checked in the script).
Stated on screen: ideal pulleys, weightless rope and blocks, no friction, pull straight down.

## Answer
**30 kg** (of pull).

## Working (exact fractions, `python3 puzzle.py`)
- An ideal rope has one tension T along its whole length.
- Rope path, dead end to hand: dead end (tied to the moving block) -> F1 -> M1 -> F2 -> M2 -> F3 -> hand.
- Strands (every one vertical, checked from the coordinates):

| # | strand | position | ends | holds the moving block |
|---|---|---|---|---|
| 1 | DEAD END -> F1 | x = 178 | moving / fixed | yes |
| 2 | F1 -> M1 | x = 282 | fixed / moving | yes |
| 3 | M1 -> F2 | x = 386 | moving / fixed | yes |
| 4 | F2 -> M2 | x = 490 | fixed / moving | yes |
| 5 | M2 -> F3 | x = 594 | moving / fixed | yes |
| 6 | F3 -> HAND | x = 698 | fixed / free | no |

- 5 strands pull up on the moving block, so 5 x T = 150 kg and T = 150 / 5 = **30 kg**.
- The hand strand comes down off a fixed sheave (F3), so it does not hold the moving block. It only carries T.
- Likely wrong answers: 37.5 (4 strands: the dead-end strand on the moving block is forgotten), 25 (6 strands: the
  hand strand is counted), 50 (3 fixed sheaves), 75 (2 moving sheaves).
