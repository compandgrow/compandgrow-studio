"""brain-03: pulley calc. A 150 kg crate hangs from a block and tackle: fixed block with 3 sheaves (F1-F3), moving block
with 2 sheaves (M1, M2), rope's dead end tied to the MOVING block, free end comes off F3 straight down to the hand.
Ideal pulleys, weightless rope and blocks, no friction. How many kg of pull holds the crate?
Builds the rope path, measures which strands hold the moving block from the coordinates, solves the force with exact
fractions and writes puzzle.js (window.PUZZLE = {view, svg}), FACTS.md and answer.json.   python3 puzzle.py"""
import json, os
from fractions import Fraction
HERE = os.path.dirname(os.path.abspath(__file__))

LOAD_KG = 150
R = 52                      # sheave radius (all equal, so every strand is vertical)
X0 = 230                    # centre of F1
YF, YM = 170, 500           # sheave centre heights: fixed block, moving block
INK, CREAM, YEL, RED, BLUE, ROPE = '#111318', '#f1e6d0', '#f2c230', '#e0533a', '#8fa0cf', '#b0783a'

# sheaves: F1 M1 F2 M2 F3 alternate, each one sheave-diameter to the right of the last, so the rope drops straight
SHEAVES = []
for k, name in enumerate(['F1', 'M1', 'F2', 'M2', 'F3']):
    SHEAVES.append({'name': name, 'block': 'fixed' if name[0] == 'F' else 'moving', 'x': X0 + 2 * R * k, 'y': YF if name[0] == 'F' else YM})
S = {s['name']: s for s in SHEAVES}

# rope path, walked from the dead end to the hand: dead end (moving block) -> F1 -> M1 -> F2 -> M2 -> F3 -> hand
DEAD = {'name': 'DEAD END', 'block': 'moving', 'x': S['F1']['x'] - R, 'y': YM + R + 40}
HAND = {'name': 'HAND', 'block': 'free', 'x': S['F3']['x'] + R, 'y': 800}
path = [DEAD] + SHEAVES + [HAND]

# strands = straight rope pieces between consecutive path items; record each strand's x and its two ends
strands = []
for a, b in zip(path, path[1:]):
    # the strand leaves a on the side facing b; sheaves are R wide on each side
    xa = a['x'] + (R if a in SHEAVES and b['x'] > a['x'] else -R if a in SHEAVES else 0)
    xb = b['x'] + (-R if b in SHEAVES and a['x'] < b['x'] else R if b in SHEAVES else 0)
    assert abs(xa - xb) < 1e-9, (a['name'], b['name'], xa, xb)   # every strand is vertical
    strands.append({'from': a['name'], 'to': b['name'], 'x': xa, 'ends': (a['block'], b['block'])})

# a strand pulls up on the moving block if one of its ends is on the moving block and the other on the fixed block
holding = [s for s in strands if sorted(s['ends']) == ['fixed', 'moving']]
hand_strand = [s for s in strands if 'free' in s['ends']]
assert len(hand_strand) == 1 and hand_strand[0]['ends'] == ('fixed', 'free')
N = len(holding)
T = Fraction(LOAD_KG, N)    # ideal rope: one tension T everywhere; moving block in equilibrium: N * T = load
ANSWER = int(T) if T.denominator == 1 else float(T)
assert N == 5 and T == 30, (N, T)

# ---------- drawing (900 x 900 view) ----------
def sheave(s, fill):
    x, y = s['x'], s['y']
    return (f'<circle cx="{x}" cy="{y}" r="{R}" fill="{fill}" stroke="{INK}" stroke-width="5"/>'
            f'<circle cx="{x}" cy="{y}" r="{R - 12}" fill="none" stroke="{INK}" stroke-width="2.5" opacity=".5"/>'
            f'<circle cx="{x}" cy="{y}" r="9" fill="{INK}"/>')

svg = []
# ceiling beam + hatching
bx0, bx1 = DEAD['x'] - 60, HAND['x'] + 60
svg.append(f'<rect x="{bx0}" y="40" width="{bx1 - bx0}" height="34" fill="#8a8fa3" stroke="{INK}" stroke-width="5"/>')
svg += [f'<path d="M{x} 40 l-22 -26" stroke="{INK}" stroke-width="4"/>' for x in range(bx0 + 30, bx1, 40)]
# fixed block straps: one plate from F1 to F3 hung from the beam
svg.append(f'<rect x="{S["F1"]["x"] - 14}" y="74" width="{S["F3"]["x"] - S["F1"]["x"] + 28}" height="22" rx="6" fill="#5d6fa3" stroke="{INK}" stroke-width="5"/>')
for n in ['F1', 'F2', 'F3']:
    svg.append(f'<path d="M{S[n]["x"]} 96 V{YF}" stroke="{INK}" stroke-width="10"/>')
# moving block: yoke under M1 and M2, extended left to the dead-end eye
yy = YM + R + 40
svg.append(f'<path d="M{S["M1"]["x"]} {YM} V{yy} M{S["M2"]["x"]} {YM} V{yy}" stroke="{INK}" stroke-width="10"/>')
svg.append(f'<rect x="{DEAD["x"] - 18}" y="{yy - 12}" width="{S["M2"]["x"] - DEAD["x"] + 36}" height="26" rx="8" fill="{RED}" stroke="{INK}" stroke-width="5"/>')
svg.append(f'<circle cx="{DEAD["x"]}" cy="{yy}" r="9" fill="{CREAM}" stroke="{INK}" stroke-width="4"/>')
# rope: one path, dead end -> over F1 -> under M1 -> over F2 -> under M2 -> over F3 -> hand
d = f'M{DEAD["x"]} {yy} V{YF}'
for s in SHEAVES:
    x = s['x']
    if s['block'] == 'fixed':
        d += f' A{R} {R} 0 0 1 {x + R} {YF}' + (f' V{YM}' if s['name'] != 'F3' else f' V{HAND["y"]}')
    else:
        d += f' A{R} {R} 0 0 0 {x + R} {YM} V{YF}'
svg.append(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="13" stroke-linejoin="round"/>')
svg.append(f'<path d="{d}" fill="none" stroke="{ROPE}" stroke-width="7" stroke-linejoin="round"/>')
for s in SHEAVES:
    svg.append(sheave(s, YEL if s['block'] == 'fixed' else BLUE))
# crate on a hook under the middle of the yoke
cx = (DEAD['x'] + S['M2']['x']) / 2
svg.append(f'<path d="M{cx} {yy + 14} V{yy + 60}" stroke="{INK}" stroke-width="8"/>')
cw, ch, cy0 = 300, 170, yy + 60
svg.append(f'<rect x="{cx - cw / 2}" y="{cy0}" width="{cw}" height="{ch}" rx="10" fill="#c99a5b" stroke="{INK}" stroke-width="6"/>'
           f'<path d="M{cx - cw / 2} {cy0} L{cx + cw / 2} {cy0 + ch} M{cx + cw / 2} {cy0} L{cx - cw / 2} {cy0 + ch}" stroke="{INK}" stroke-width="3" opacity=".35"/>'
           f'<text x="{cx}" y="{cy0 + ch / 2 + 30}" text-anchor="middle" font-family="Alfa" font-size="68" fill="{INK}">{LOAD_KG} kg</text>')
assert cx + cw / 2 < HAND['x'] - 40       # crate stays clear of the hand strand
# hand grip + pull arrow + "? kg"
hx, hy = HAND['x'], HAND['y']
svg.append(f'<g class="pulse"><rect x="{hx - 26}" y="{hy - 8}" width="52" height="64" rx="18" fill="{RED}" stroke="{INK}" stroke-width="5"/>'
           f'<path d="M{hx} {hy + 64} V{hy + 112}" stroke="{INK}" stroke-width="10"/><path d="M{hx - 26} {hy + 100} L{hx} {hy + 136} L{hx + 26} {hy + 100}Z" fill="{INK}"/></g>')
svg.append(f'<rect x="{hx - 140}" y="{hy - 150}" width="124" height="72" rx="14" fill="{CREAM}" stroke="{INK}" stroke-width="5"/>'
           f'<text x="{hx - 78}" y="{hy - 98}" text-anchor="middle" font-family="Alfa" font-size="46" fill="{RED}">? kg</text>')
cxv = (bx0 + bx1) / 2
P = {'view': f'{cxv - 480:.0f} 0 960 960', 'svg': ''.join(svg)}
open(os.path.join(HERE, 'puzzle.js'), 'w').write('window.PUZZLE = ' + json.dumps(P) + ';\n')

rows = '\n'.join(f"| {i + 1} | {s['from']} -> {s['to']} | x = {s['x']} | {s['ends'][0]} / {s['ends'][1]} | "
                 f"{'yes' if s in holding else 'no'} |" for i, s in enumerate(strands))
facts = f"""# brain-03 · How many kg of pull holds the 150 kg crate?

Engineering brain test (format v4 trial `tunable.brain_test`, type "calc"). No real-world historical claims; the
puzzle is generated and solved by `puzzle.py` (no kit helper; the rope path is built and checked in the script).
Stated on screen: ideal pulleys, weightless rope and blocks, no friction, pull straight down.

## Answer
**{ANSWER} kg** (of pull).

## Working (exact fractions, `python3 puzzle.py`)
- An ideal rope has one tension T along its whole length.
- Rope path, dead end to hand: dead end (tied to the moving block) -> F1 -> M1 -> F2 -> M2 -> F3 -> hand.
- Strands (every one vertical, checked from the coordinates):

| # | strand | position | ends | holds the moving block |
|---|---|---|---|---|
{rows}

- {N} strands pull up on the moving block, so {N} x T = {LOAD_KG} kg and T = {LOAD_KG} / {N} = **{T} kg**.
- The hand strand comes down off a fixed sheave (F3), so it does not hold the moving block. It only carries T.
- Likely wrong answers: 37.5 (4 strands: the dead-end strand on the moving block is forgotten), 25 (6 strands: the
  hand strand is counted), 50 (3 fixed sheaves), 75 (2 moving sheaves).
"""
open(os.path.join(HERE, 'FACTS.md'), 'w').write(facts)
json.dump({'answer': ANSWER, 'unit': 'kg', 'working': f'{N} strands hold the moving block: {LOAD_KG} / {N} = {T}'},
          open(os.path.join(HERE, 'answer.json'), 'w'), indent=1)
print('answer:', ANSWER, 'kg | strands holding', N, '| view', P['view'])
