# brain-04 · 120 litres in. How many reach tank C?

Engineering brain test (format v4 trial `tunable.brain_test`, type "track + calc"). No real-world historical claims;
the pipe graph and routes are built, checked and solved by `puzzle.py`. Rule on screen: "Every junction splits the flow
equally." Junctions are yellow dots; pipes that cross without a dot do not connect.

## Answer
**50 litres.**

## Working (exact fractions, `python3 puzzle.py`)
- J1 splits 120 L two ways: 120 / 2 = 60 L to each side (the 3-way junction is drawn on the right, the 2-way on the left).
- The 3-way junction (feeds A, B, C): 60 / 3 = 20 L each, so 20 L to C.
- The 2-way junction (feeds C, D): 60 / 2 = 30 L each, so 30 L to C.
- Tank C: 20 + 30 = **50 L**. Check: A 20 + B 20 + C 50 + D 30 = 120 L.

| pipe | flow |
|---|---|
| IN -> J1 | 120 L |
| J1 -> J3 | 60 L |
| J1 -> J2 | 60 L |
| J2 -> A | 20 L |
| J2 -> B | 20 L |
| J2 -> C | 20 L |
| J3 -> D | 30 L |
| J3 -> C | 30 L |

## Drawing matches the maths
- The 3-way junction is drawn on the right and the 2-way on the left, so the pipes to A, B, C and to C, D cross.
- Every crossing is a vertical run over a horizontal run, more than 40 px from any junction or tank:
- (270, 330): J2->A passes J3->D (a crossing, not a joint: no dot)
- (190, 330): J2->A passes J3->C (a crossing, not a joint: no dot)
- (335, 540): J2->B passes J3->D (a crossing, not a joint: no dot)
- (335, 610): J2->B passes J3->C (a crossing, not a joint: no dot)
- (590, 540): J2->C passes J3->D (a crossing, not a joint: no dot)
- Likely wrong answers: 30 (right side only), 20 (left side only), 40 (120 / 3), 60 (one side's whole flow).
