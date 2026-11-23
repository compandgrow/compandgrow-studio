# BRAIN TEST #4 — pipe split (type: track + calc)
For slot: Sat 2026-11-28 16:28 PT · style: motion3d (cards `brain` mode fallback) · answer in the film #7 caption Sun Nov 29 (or pinned comment)
Learnings rule 4: number answer, "COMMENT A NUMBER" on the hook card, timer <= 8 s. Last test of the brain trial.

Hook card (frame 0, moving): **"120 litres in. How many reach tank C? COMMENT A NUMBER"**
Puzzle: water enters at the top (120 L). Rule on screen: "Every junction splits the flow equally."
- Junction J1 at the inlet splits 2 ways: left pipe and right pipe.
- Left pipe -> junction J2, splits 3 ways: tank A, tank B, tank C.
- Right pipe -> junction J3, splits 2 ways: tank C, tank D.
Tanks A, B, C, D sit along the bottom; C is fed from both sides, and its two pipes should cross or loop so the eye has to follow them. Animated water fronts run down the pipes during the timer and stop just before the tanks.

Answer: **50 litres.**
Working (compute in `puzzle.py` from the pipe graph, write `answer.json` + FACTS.md): 120 / 2 = 60 per side. Left: 60 / 3 = 20 each to A, B, C. Right: 60 / 2 = 30 each to C, D. C = 20 + 30 = 50. Check: A 20 + B 20 + C 50 + D 30 = 120. Verified in code.
Common wrong answers: 30 (right side only), 20 (left side only), 40 (120 / 3), so comments split.
Lock: "LOCK IT IN" 3-2-1 by ~12 s. End: "Answer Sunday with the new film · FOLLOW". Caption never gives the answer.
