# STILLWING — pitch
Device: the antigravity "lifter" (ionocraft / asymmetric capacitor): a foil-and-wire triangle that rises when you put about 30,000 volts across it.
Style: exploded-teardown (test style, film #6)   For slot: Sun 2026-11-15 16:28 PT
Kit: `studio/kits/exploded-teardown/` does NOT exist yet. The producer has to build it from `$LIB/styles/exploded-teardown/` (adapt to 1080x1920 the way `studio/kit/board.js` was adapted: W/H constants, Latin fonts, one-line English subtitles, `window.MBCAP`), then set `KIT` in the film folder. (`$LIB` was not cloned during scouting, so I have not checked that the style folder exists. Check it first.)

## Angle
"Is it antigravity?" asked on screen inside 10 s, then answered by a teardown. The style fits: the lifter really is three parts (thin wire, air gap, foil skirt), and the teardown shows that the missing fourth part is *the air*. Real part: one dated beat (the 1928 patent), then the physics (corona, ions, ion wind). Fictional part: STILLWING, a program that scales the lifter into a silent craft with no moving parts, ending on the honest catch: it pushes on air, so it can never leave the air.

Script shape (learnings rule 1: question or payoff tease within 10 s, then at most one dated beat before the physics):
- 0–3 s: subject plus visual payoff. The foil triangle lifts off the bench with nothing spinning.
- 3–9 s: the question. "No wings. No rotor. No fuel. So what's lifting it?" with ANTIGRAVITY? as a stamp.
- 9–20 s: ONE dated beat. 1928, a British patent: "Method of Producing Force or Motion".
- 20–45 s: teardown physics. Exploded view: wire / gap / foil. Sharp wire ionises the air, the ions race to the foil and drag neutral air with them, the wind pushes down and the lifter goes up. ANTIGRAVITY struck out, ION WIND lands.
- (Optional proof beat after the physics, not before it: 2018, a 5 m plane flew 60 m on this, with no moving parts.)
- 45–95 s: STILLWING (fiction): title card, exploded spec sheet, 3 trials, the catch, the stamp.
- Outro: series hook instead of a yes/no question (learnings rule 4): "Case 7 next Sunday."

## True core leads (researcher must verify each, claim -> source URL in FACTS.md)
- **1928 British patent GB 300311, "Method of Producing Force or Motion"** (Thomas Townsend Brown; applied 15 Apr 1927, accepted 15 Nov 1928). Lead: Wikipedia "Biefeld–Brown effect" (https://en.wikipedia.org/wiki/Biefeld%E2%80%93Brown_effect). Confirm on Espacenet / Google Patents. This is the film's ONE dated history beat.
- **The effect is named "Biefeld–Brown"** after Brown and Denison University physics professor Paul Alfred Biefeld. The Wikipedia lead says the record of the two working together is thin, and Denison said in 2004 it had no record of their experiments. If this is used at all, say only "the effect got named after him". Better to leave it out.
- **Later US patents**, e.g. US 1,974,483 "Electrostatic motor" (1934) and US 2,949,550 "Electrokinetic apparatus" (1960). Same Wikipedia lead, plus Google Patents. Background only; do not put more than one date on screen.
- **Physics: corona discharge / ion wind (electrohydrodynamics)** at the sharp wire. Ions collide with neutral air and transfer momentum, and thrust falls sharply at low pressure. Leads: Wikipedia (as above); Tajmar, AIAA Journal 2004 (corona wind, no thrust when the device is enclosed); Talley 1988–1990, USAF report (no thrust at 10^-6 torr under DC). Sources: Wikipedia citations, possibly https://documents2.theblackvault.com/documents/usaf/2018-01638-F.pdf.
- **US Army Research Laboratory study, "Force on an Asymmetric Capacitor"** (Bahder & Fazi, ARL, 2002/2003; voltage about 30 kV). The abstract says an ion-drift model gives the right order of magnitude for the force and ion wind alone is about 1,000x too small. Sources: https://arxiv.org/abs/physics/0211001 ; https://www.govinfo.gov/content/pkg/GOVPUB-D101-PURL-LPS125022/pdf/GOVPUB-D101-PURL-LPS125022.pdf. Use carefully: it is a real study by a real agency. Only state what it measured or concluded, and keep it well away from the fiction.
- **NASA contractor report "Asymmetrical Capacitors for Propulsion"**, NASA/CR-2004-213312, 1 Oct 2004 (Canning, Melcher, Winet; Institute for Scientific Research). It ran tests at atmospheric pressure and at reduced pressures, and its model puts thrust on ion collisions with air. Source: https://ntrs.nasa.gov/citations/20040171929 (PDF at https://ntrs.nasa.gov/archive/nasa/casi.ntrs.nasa.gov/20040171929.pdf). The vacuum result has to be read from the PDF. The abstract does not state it.
- **2018 MIT ion-wind plane**: 5 m wingspan, about 5 lb (2.45 kg), 40,000 V, flew 60 m (the length of the gym), repeated 10 times, Nature, 21 Nov 2018, no moving parts. Source: https://news.mit.edu/2018/first-ionic-wind-plane-no-moving-parts-1121. Best candidate for the "this was real" cut. It is a positive, non-villain story.
- **2024 Scientific Reports** (Tajmar, Kößling, Neunzig, 21 Aug 2024): an in-depth search for any thrust beyond ion wind. Lead: Wikipedia. It could carry the line "still being tested in 2024", but only if the paper's conclusion is verified.

## Fictional program sketch (invented. Never attribute to any real agency, lab, university or person, including NASA, ARL, MIT or Brown)
**STILLWING**: a program to scale the lifter into a silent craft with no moving parts, by stacking lifter cells into a tile and tiles into a wing.
Exploded spec sheet: emitter wire 0.1 mm · air gap 30 mm · foil skirt · 30 kV per cell · 0 moving parts.
Trials (escalating):
- TRIAL 01: one cell, 20 cm triangle. Lifts its own 3 g and hovers 60 s on a tether. FLEW.
- TRIAL 02: 64-cell tile. Carries a 2 kg payload and hovers 4 min at 2 m. FLEW.
- TRIAL 03: 1,200-cell wing. 12 km of silent flight, carrying its own batteries. FLEW.
- Honest catch: "One catch. It pushes on air." The altitude run loses thrust as the air thins and it stalls out at 3 km. In a vacuum chamber it reads 0.
- Stamp: **CLEARED: BELOW 3 KM. NOT ANTIGRAVITY.** (Same twist shape as LODESTONE's "CLEARED AS AN ELECTRIC MOTOR", which keeps the series voice.)

## Hook candidates (film open, <= 10 words, payoff first, subject in the first line per rule 2)
1. "This foil triangle flies. Nothing on it moves." (8). **Best**: device + payoff, with the visual doing the work. The question "So what's lifting it?" lands by about 5 s.
2. "Plug in this triangle of foil, and it rises." (9)
3. "No wings, no rotor, no fuel. What lifts this?" (9). Question-first fallback.

## Cutdown hooks (Tue 17 / Fri 20 / Sat 21; no question cut this week because Thu is the game)
- **this_was_real (Tue Nov 17):** "In 2018 a plane flew with zero moving parts." Then 60 m, 40,000 V and the 1928 patent as the root. Splice rule 3: the second segment opens on "So what pushed it?" and not on an explanation.
- **number (Fri Nov 20):** "A foil lifter carried 3 grams. Then 2 kilos." Then "Then 12 kilometres. Silent." The subject comes first, because a bare number lost: LONGSHOT's "250 miles." had 68% skip.
- **stamp (Sat Nov 21):** "It flew 12 km silently. Then the catch." The catch (pushes on air, 0 in vacuum) leads to CLEARED: BELOW 3 KM.
- question (spare, not scheduled): "If it's not antigravity, what's lifting it?"
- End card on all three: "FULL BRIEFING on @compandgrow", plus the series hook "new case every Sunday".

## Outliers seen
vidIQ outlier search was not available in this session (the tool was not exposed to the scout). One general web search found no current Reel/TikTok outlier data on lifters, only old hobby and forum pages (rimstar.org, Gizmodo "antigravity lifters"). The lifter has been a classic YouTube DIY "antigravity" clip since the 2000s, and the shape that sells it is *visual first*: the craft lifts off in frame 1 and the claim comes after. The pitch keeps that shape. Re-run the vidIQ search ("ionocraft", "plane with no moving parts", "antigravity explained") next run if the tool is available.

## Risk check
Never-list: **clear, with guardrails.** There is no health, election, disaster or logo angle. Guardrails for the scriptwriter, researcher and reviewer:
- **No real named villains.** Brown appears only as the 1928 patent holder, and the film says "the effect turned out to be wind", not "he was wrong / a fraud". Do not use the Biefeld-mentor doubt as a dig at him.
- **No conspiracy framing.** Lifter and "electrogravitics" lore includes UFO, cover-up and secret-bomber rumours (the same flavour as the off-format "not ours" Reels of Oct 24–25). Do not mention or hint at any of it: no "the Navy hid it", no "what they don't want you to know". The film debunks "antigravity" and does not sell it.
- **Real agencies only for what they actually published** (ARL 2003, NASA CR 2004, MIT 2018). STILLWING must never be shown near their names, seals or report covers. No logos (MIT/NASA/Army marks), and no photos of real people.
- **Safety:** real lifters run on 20–40 kV. Show no build steps and no supply wiring. A small "high voltage, do not try" line in the caption is advisable. This is not a never-list item, so no need to ask Jazzy.

---

# GAME #2 — "Real or fake?" (Thu 2026-11-19 16:28 PT)
Game #1 used HULL 7 (fake), Project Habakkuk ice carrier (real) and TREMOR (fake), with the real one in position 2. This game repeats none of those, and the real one moves to position 3.
Theme line: **"Only one of these was really built. Which?"**

| # | Card (<= 8 words on screen) | Truth | From |
|---|---|---|---|
| 1 | A foil wing that flew 12 km. Silent. | FAKE | STILLWING (lifter film, aired 4 days earlier). The 12 km trial is invented |
| 2 | A power cell running on caught ball lightning. | FAKE | EMBER (film Nov 8): the 6 h cell is invented |
| 3 | A flying saucer built for the US military. | **REAL** | Avro Canada VZ-9 **Avrocar**, first flew 1959, cancelled 1961. It could barely climb above a few feet (ground effect) |

Real-device lead for the researcher: Avrocar (VZ-9AV), Avro Canada, a US Army/USAF-funded VTOL "flying saucer". First hover in 1959. It was unstable out of ground effect and was cancelled around 1961. One airframe survives in a museum. Sources to check: https://www.airspacemag.com/military-aviation/the-pentagons-flying-saucer-problem-4613827 ; https://flyingmag.com/avro-canada-vz-9-avrocar-resembling-a-small-flying-saucer-it-first-flew-in-1959 ; https://www.globalsecurity.org/military/systems/aircraft/vz-9.htm ; https://ar5iv.labs.arxiv.org/html/1507.06916. Put on screen only the points all sources agree on (built, flew in 1959, couldn't fly high, cancelled). Drop any height, speed or cost figures where the sources differ.
Why it works: the real one *sounds* the most fake (a Pentagon saucer). It also picks up the lifter week's flight theme, and the STILLWING card plants a doubt because a real ion plane exists. The reveal must make clear that the 12 km wing is ours and the real 2018 ion plane flew 60 m. Alternate fake if that is too confusing: LODESTONE, "A magnet wheel that ran 40 days, no fuel."

Tighter structure (20–22 s). Game #1's average viewer left at about 8.4 s, during card 2, before the vote:
- **0.0–1.5 s:** all 3 cards visible at once as a numbered strip, with "ONE IS REAL. COMMENT 1, 2 OR 3" on screen **from frame 0** together with the theme line. The vote prompt is on screen before anyone can leave.
- **1.5–9.5 s:** each card goes full screen for about 2.5 s (one line + one picture), with the "1 / 2 / 3?" prompt staying on screen in the corner.
- **9.5–11.5 s:** "LOCK IT IN" over the strip with a 3-2-1 counter. This is the comment beat, and it lands before about 12 s.
- **11.5–19 s:** reveal. FAKE stamps on 1 and 2, each with a one-line "from our STILLWING / EMBER briefing". Then REAL on 3 with "Avrocar, 1959" and a source caption.
- **19–21 s:** a reason to follow instead of a question: "New case every Sunday. Game every Thursday."
- Caption: "One of these is real. Number in the comments before you watch the end." #whatif #realorfake
