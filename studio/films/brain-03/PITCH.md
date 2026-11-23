# BRAIN TEST #3 — pulley sum (type: calc)
For slot: Wed 2026-11-25 16:28 PT · style: motion3d (cards `brain` mode fallback) · answer in Thu fact-04 caption (Bagger 288) or pinned comment
Learnings rule 4: number answer, "COMMENT A NUMBER" on the hook card from frame 0, timer <= 8 s.

Hook card (frame 0, moving): **"How many kg to lift 150 kg? COMMENT A NUMBER"**
Puzzle: a 150 kg crate hangs from a block and tackle. Fixed block at the top with 3 sheaves; moving block on the crate with 2 sheaves; the rope's dead end is tied to the **moving** block; the free end comes down off the top block to a hand pulling straight down. On screen: "Ideal pulleys, no friction, pull straight down."
Camera: slow 3D orbit so every rope strand is visible once, then hold front-on for the 8 s timer.

Answer: **30 kg** (of force).
Working (compute in `puzzle.py`, write to `answer.json` + FACTS.md): walk the rope path dead end (moving block) -> F1 -> M1 -> F2 -> M2 -> F3 -> hand. Strands holding the moving block = 5 (dead-end strand, F1-M1, M1-F2, F2-M2, M2-F3); the hand strand comes off a fixed sheave and does not hold the block. Force = 150 / 5 = 30. Checked in code (strands 5, force 30).
Why it's a good test: the common wrong answers are 37.5 (counting only 4 strands, forgetting the dead end on the moving block) and 25 (counting the hand strand), so comments will disagree, which drives more comments. One correct answer, no trick wording.
Lock: "LOCK IT IN" 3-2-1 by ~12 s. End: "Answer tomorrow · FOLLOW for the next test". Caption never gives the answer.
