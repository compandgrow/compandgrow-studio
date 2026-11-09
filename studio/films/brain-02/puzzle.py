"""brain-02: gear-ratio calc. Gear A (40 teeth) turns 3 full turns; it drives an idler B (30 teeth), which drives
gear C (12 teeth). How many full turns does C make? Builds the geometry, measures the meshes, solves the speeds and
writes puzzle.js (drawing, every gear drawn with its real tooth count) + FACTS.md.   python3 puzzle.py"""
import json, math, os, sys
from fractions import Fraction
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'kits', 'cards', 'brain'))
from gears import chain, solve, phase_chain, mesh_check, svg_gear, arrow_arc, bbox

M = 12
TURNS_A = 3
SPEC = [('A', 40, 0), ('B', 30, 35), ('C', 12, 122)]
gs = chain(SPEC, M, 0, 0)
sol, E = solve(gs, 0, +1)
phase_chain(gs, E)
err = mesh_check(gs, E); assert err < 1e-9, err
assert sorted(E) == [(0, 1), (1, 2)], E          # A-B and B-C mesh, A and C do not touch

# exact arithmetic for the answer: turns_j = turns_A * N_A / N_j along a simple chain (idlers cancel)
tB = Fraction(TURNS_A) * Fraction(gs[0].n, gs[1].n)
tC = tB * Fraction(gs[1].n, gs[2].n)
assert tC.denominator == 1 and abs(float(tC) - TURNS_A * sol[2][1]) < 1e-9
ANSWER = int(tC)

FONT = 'font-family="Alfa" fill="#111318" text-anchor="middle"'
A, B, C = gs
A.style['plain'] = B.style['plain'] = C.style['plain'] = True
partA = svg_gear(A, '#f2c230',
                 '<g class="pulse">' + arrow_arc(A.x, A.y, A.r * 0.74, -205, -25, w=16, head=34) + '</g>'
                 f'<text x="{A.x:.1f}" y="{A.y - 72:.1f}" {FONT} font-size="100">A</text>'
                 f'<text x="{A.x:.1f}" y="{A.y + 108:.1f}" text-anchor="middle" font-family="Mono" font-size="44" fill="#111318">40 TEETH</text>'
                 f'<text x="{A.x:.1f}" y="{A.y + 160:.1f}" text-anchor="middle" font-family="Mono" font-size="44" fill="#b8321c">3 TURNS</text>')
partB = svg_gear(B, '#8fa0cf',
                 f'<text x="{B.x:.1f}" y="{B.y - 58:.1f}" {FONT} font-size="84">B</text>'
                 f'<text x="{B.x:.1f}" y="{B.y + 98:.1f}" text-anchor="middle" font-family="Mono" font-size="40" fill="#111318">30 TEETH</text>')
lx, ly = C.x - C.tip - 24, C.y + 16
partC = svg_gear(C, '#e0533a',
                 f'<g class="bob"><circle cx="{C.x:.1f}" cy="{C.y:.1f}" r="{C.r * 0.58:.1f}" fill="#f1e6d0" stroke="#111318" stroke-width="5"/>'
                 f'<text x="{C.x:.1f}" y="{C.y + 22:.1f}" {FONT} font-size="62">C</text></g>'
                 f'<rect x="{lx - 222:.1f}" y="{ly - 66:.1f}" width="234" height="116" rx="14" fill="#f1e6d0" stroke="#111318" stroke-width="5"/>'
                 f'<text x="{lx:.1f}" y="{ly - 18:.1f}" text-anchor="end" font-family="Mono" font-size="42" fill="#111318">12 TEETH</text>'
                 f'<text x="{lx:.1f}" y="{ly + 34:.1f}" text-anchor="end" font-family="Mono" font-size="42" fill="#b8321c">? TURNS</text>')
x, y, w, h = bbox(gs, 16)
x0 = min(x, lx - 240); w += x - x0; x = x0      # room for C's label on the left
s = max(w, h); x -= (s - w) / 2; y -= (s - h) / 2
P = {'view': f'{x:.1f} {y:.1f} {s:.1f} {s:.1f}', 'svg': partA + partB + partC}
open(os.path.join(HERE, 'puzzle.js'), 'w').write('window.PUZZLE = ' + json.dumps(P) + ';\n')

d = lambda a, b: math.hypot(a.x - b.x, a.y - b.y)
facts = f"""# brain-02 · How many turns does gear C make?

Engineering brain test (format v3 trial `tunable.brain_test`, type "calc"). No real-world historical claims; the
puzzle is generated and solved by `puzzle.py` (geometry helpers in `studio/kits/cards/brain/gears.py`).

## Answer
**{ANSWER} full turns.**

## Working (computed with exact fractions, `python3 puzzle.py`)
- Gears that mesh move the same number of teeth past the contact point, so turns x teeth is the same for every
  gear in the train.
- Gear A: {TURNS_A} turns x {A.n} teeth = {TURNS_A * A.n} teeth pass the mesh.
- Gear B (idler): {TURNS_A * A.n} / {B.n} = {tB} turns. It passes the same {TURNS_A * A.n} teeth on to C.
- Gear C: {TURNS_A * A.n} / {C.n} = **{tC} turns**. The idler B changes direction, not the count:
  {TURNS_A} x {A.n}/{B.n} x {B.n}/{C.n} = {TURNS_A} x {A.n}/{C.n} = {tC}.
- Directions (not asked): A {'clockwise' if sol[0][0] > 0 else 'anticlockwise'}, B {'clockwise' if sol[1][0] > 0 else 'anticlockwise'}, C {'clockwise' if sol[2][0] > 0 else 'anticlockwise'}.

## Drawing matches the maths
- One module ({M} px) for all gears; pitch radius = 6 px per tooth: A {A.r:.0f}, B {B.r:.0f}, C {C.r:.0f} px.
- Each gear is drawn with exactly its stated tooth count ({A.n}, {B.n}, {C.n}).
- Meshes measured from the coordinates: A-B centre distance {d(A, B):.2f} = {A.r:.0f} + {B.r:.0f}; B-C {d(B, C):.2f} = {B.r:.0f} + {C.r:.0f};
  A-C {d(A, C):.1f}, far more than the tip radii {A.tip:.0f} + {C.tip:.0f}, so A and C do not touch.
- Tooth interleave check: worst error {err:.1e} of a tooth pitch.
"""
open(os.path.join(HERE, 'FACTS.md'), 'w').write(facts)
json.dump({'answer': ANSWER, 'working': f'{TURNS_A} x {A.n} / {C.n} = {ANSWER}'}, open(os.path.join(HERE, 'answer.json'), 'w'), indent=1)
print('answer:', ANSWER, '| B turns', tB, '| err', err, '| view', P['view'])
