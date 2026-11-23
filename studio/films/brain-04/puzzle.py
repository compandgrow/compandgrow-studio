"""brain-04: pipe split (track + calc). 120 L enter at the top. Every junction splits its flow equally between its
outgoing pipes. J1 (inlet) -> 2 pipes; one goes to a 3-way junction feeding tanks A, B, C, the other to a 2-way junction
feeding tanks C, D. Tank C is fed from both sides and the pipes cross over each other (no joint at a crossing).
How many litres reach tank C?  Builds the pipe graph + orthogonal routes, checks that crossings never touch a junction
or another pipe's bend, solves the flow with exact fractions, writes puzzle.js, FACTS.md, answer.json.  python3 puzzle.py"""
import json, os
from fractions import Fraction
HERE = os.path.dirname(os.path.abspath(__file__))

INFLOW = 120
INK, CREAM, YEL, RED, BLUE, PIPE = '#111318', '#f1e6d0', '#f2c230', '#e0533a', '#8fa0cf', '#5d8fd0'

# nodes: junctions (dots) and tanks. The 3-way junction sits on the RIGHT and the 2-way on the LEFT, so the pipes to
# their tanks have to cross each other (the eye has to follow them).
TANK_Y, TANK_W, TANK_H = 690, 150, 150
NODES = {
    'IN': (450, 40), 'J1': (450, 130),
    'J2': (670, 250),            # 3-way: A, B, C
    'J3': (230, 250),            # 2-way: C, D
    'A': (125, TANK_Y), 'B': (335, TANK_Y), 'C': (565, TANK_Y), 'D': (775, TANK_Y),
}
# edges with explicit orthogonal routes (list of points). Each pipe from a junction leaves from its own port and
# runs down to its own horizontal level, so every crossing is vertical-over-horizontal.
EDGES = [
    ('IN', 'J1', [(450, 40), (450, 130)]),
    ('J1', 'J3', [(450, 130), (230, 130), (230, 250)]),
    ('J1', 'J2', [(450, 130), (670, 130), (670, 250)]),
    ('J2', 'A', [(670, 250), (620, 250), (620, 330), (125, 330), (125, TANK_Y)]),
    ('J2', 'B', [(670, 250), (670, 400), (335, 400), (335, TANK_Y)]),
    ('J2', 'C', [(670, 250), (720, 250), (720, 470), (590, 470), (590, TANK_Y)]),
    ('J3', 'D', [(230, 250), (270, 250), (270, 540), (775, 540), (775, TANK_Y)]),
    ('J3', 'C', [(230, 250), (190, 250), (190, 610), (540, 610), (540, TANK_Y)]),
]
TANKS = ['A', 'B', 'C', 'D']

# ---------- flow: every node splits its inflow equally between its outgoing pipes ----------
out = {n: [b for a, b, _ in EDGES if a == n] for n in NODES}
flow = {n: Fraction(0) for n in NODES}; flow['IN'] = Fraction(INFLOW)
order = ['IN', 'J1', 'J3', 'J2'] + TANKS        # topological (checked below)
pos = {n: i for i, n in enumerate(order)}
assert all(pos[a] < pos[b] for a, b, _ in EDGES)
pipe_flow = {}
for n in order:
    for b in out[n]:
        q = flow[n] / len(out[n]); pipe_flow[(n, b)] = q; flow[b] += q
assert sum(flow[t] for t in TANKS) == INFLOW
assert len(out['J2']) == 3 and len(out['J3']) == 2 and len(out['J1']) == 2
ANSWER = flow['C']
assert ANSWER == 50, ANSWER
ANSWER = int(ANSWER)

# ---------- geometry checks: crossings are only between a vertical and a horizontal run, away from bends/junctions ----
def segs(route):
    return [(route[i], route[i + 1]) for i in range(len(route) - 1)]
crossings = []
for i, (a1, b1, r1) in enumerate(EDGES):
    for j, (a2, b2, r2) in enumerate(EDGES):
        if j <= i:
            continue
        for (p, q) in segs(r1):
            for (u, v) in segs(r2):
                h1, h2 = p[1] == q[1], u[1] == v[1]
                if h1 == h2:            # parallel runs: they may only share a junction point, never overlap
                    if h1 and p[1] == u[1]:
                        lo, hi = max(min(p[0], q[0]), min(u[0], v[0])), min(max(p[0], q[0]), max(u[0], v[0]))
                        assert hi <= lo, ('horizontal overlap', a1, b1, a2, b2)
                    if not h1 and p[0] == u[0]:
                        lo, hi = max(min(p[1], q[1]), min(u[1], v[1])), min(max(p[1], q[1]), max(u[1], v[1]))
                        assert hi <= lo, ('vertical overlap', a1, b1, a2, b2)
                    continue
                H, V = ((p, q), (u, v)) if h1 else ((u, v), (p, q))
                x, y = V[0][0], H[0][1]
                if min(H[0][0], H[1][0]) < x < max(H[0][0], H[1][0]) and min(V[0][1], V[1][1]) < y < max(V[0][1], V[1][1]):
                    for n, (nx, ny) in NODES.items():
                        assert abs(nx - x) + abs(ny - y) > 40, ('crossing near node', n, x, y)
                    crossings.append(((x, y), f'{a1}->{b1}', f'{a2}->{b2}'))
assert len(crossings) >= 3, crossings

# ---------- drawing (900 x 900 view) ----------
svg = []
def pipe(route, w_out=30, w_in=18):
    d = 'M' + ' L'.join(f'{x} {y}' for x, y in route)
    return (f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="{w_out}" stroke-linejoin="round"/>'
            f'<path d="{d}" fill="none" stroke="{PIPE}" stroke-width="{w_in}" stroke-linejoin="round"/>')
# tanks first (pipes enter from the top)
for t in TANKS:
    x, y = NODES[t]
    fill = RED if t == 'C' else '#dfe9f2'
    svg.append(f'<rect x="{x - TANK_W / 2}" y="{y}" width="{TANK_W}" height="{TANK_H}" rx="12" fill="{fill}" stroke="{INK}" stroke-width="6"/>'
               f'<text x="{x}" y="{y + 95}" text-anchor="middle" font-family="Alfa" font-size="80" fill="{CREAM if t == "C" else INK}">{t}</text>')
svg.append(f'<g class="bob"><rect x="{NODES["C"][0] - 70}" y="{TANK_Y + TANK_H + 14}" width="140" height="62" rx="14" fill="{CREAM}" stroke="{INK}" stroke-width="5"/>'
           f'<text x="{NODES["C"][0]}" y="{TANK_Y + TANK_H + 60}" text-anchor="middle" font-family="Alfa" font-size="42" fill="{RED}">? L</text></g>')
# pipes in an order where each crossing draws a clear over/under (later pipe passes over the earlier one)
for a, b, r in EDGES:
    svg.append(pipe(r))
# junction dots (only real joints get a dot; crossings never do)
for n in ['J1', 'J2', 'J3']:
    x, y = NODES[n]
    svg.append(f'<circle cx="{x}" cy="{y}" r="24" fill="{YEL}" stroke="{INK}" stroke-width="6"/>')
# inlet label
x, y = NODES['IN']
svg.append(f'<g class="pulse"><rect x="{x + 34}" y="{y - 30}" width="200" height="70" rx="14" fill="{YEL}" stroke="{INK}" stroke-width="5"/>'
           f'<text x="{x + 134}" y="{y + 20}" text-anchor="middle" font-family="Alfa" font-size="46" fill="{INK}">120 L</text></g>')
P = {'view': '0 -10 930 930', 'svg': ''.join(svg)}
open(os.path.join(HERE, 'puzzle.js'), 'w').write('window.PUZZLE = ' + json.dumps(P) + ';\n')

rows = '\n'.join(f'| {a} -> {b} | {pipe_flow[(a, b)]} L |' for a, b, _ in EDGES if (a, b) in pipe_flow)
xs = '\n'.join(f'- ({x}, {y}): {e1} passes {e2} (a crossing, not a joint: no dot)' for (x, y), e1, e2 in crossings)
facts = f"""# brain-04 · 120 litres in. How many reach tank C?

Engineering brain test (format v4 trial `tunable.brain_test`, type "track + calc"). No real-world historical claims;
the pipe graph and routes are built, checked and solved by `puzzle.py`. Rule on screen: "Every junction splits the flow
equally." Junctions are yellow dots; pipes that cross without a dot do not connect.

## Answer
**{ANSWER} litres.**

## Working (exact fractions, `python3 puzzle.py`)
- J1 splits {INFLOW} L two ways: {INFLOW} / 2 = 60 L to each side (the 3-way junction is drawn on the right, the 2-way on the left).
- The 3-way junction (feeds A, B, C): 60 / 3 = 20 L each, so 20 L to C.
- The 2-way junction (feeds C, D): 60 / 2 = 30 L each, so 30 L to C.
- Tank C: 20 + 30 = **{ANSWER} L**. Check: A {flow['A']} + B {flow['B']} + C {flow['C']} + D {flow['D']} = {sum(flow[t] for t in TANKS)} L.

| pipe | flow |
|---|---|
{rows}

## Drawing matches the maths
- The 3-way junction is drawn on the right and the 2-way on the left, so the pipes to A, B, C and to C, D cross.
- Every crossing is a vertical run over a horizontal run, more than 40 px from any junction or tank:
{xs}
- Likely wrong answers: 30 (right side only), 20 (left side only), 40 (120 / 3), 60 (one side's whole flow).
"""
open(os.path.join(HERE, 'FACTS.md'), 'w').write(facts)
json.dump({'answer': ANSWER, 'unit': 'L', 'working': '120 / 2 = 60 per side; 60 / 3 = 20 and 60 / 2 = 30 reach C; 20 + 30 = 50'},
          open(os.path.join(HERE, 'answer.json'), 'w'), indent=1)
print('answer:', ANSWER, 'L | tanks', {t: str(flow[t]) for t in TANKS}, '| crossings', len(crossings))
