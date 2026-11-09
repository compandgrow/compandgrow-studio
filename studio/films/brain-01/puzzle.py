"""brain-01: 7-gear chain. Builds the geometry, measures which gears mesh, solves the turning directions and writes
puzzle.js (drawing) + FACTS.md (answer + working).   python3 puzzle.py"""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'kits', 'cards', 'brain'))
from gears import chain, solve, phase_chain, mesh_check, svg_gear, arrow_arc, bbox

M = 12  # module, px
# (name, teeth, heading from previous gear in screen degrees: 0 right, 90 down)
SPEC = [('G1', 15, 0), ('G2', 10, 18), ('G3', 13, 62), ('G4', 9, 128), ('G5', 16, 165),
        ('G6', 10, 105), ('G7', 14, 30)]
gs = chain(SPEC, M, 0, 0)
sol, E = solve(gs, 0, +1)              # G1 driven clockwise
phase_chain(gs, E)
err = mesh_check(gs, E)
assert err < 1e-9, err

# it must be one open chain: 6 meshes, every gear reached, degrees 1-2-2-2-2-2-1 in order
assert len(gs) == 7 and len(sol) == 7
assert sorted(E) == [(i, i + 1) for i in range(6)], f'mesh graph is not the drawn chain: {E}'
heads = [h for _, _, h in SPEC[1:]]
assert len(set(round(h) for h in heads)) > 1, 'chain must not be straight'

YEL, RED, STEEL = '#f2c230', '#e0533a', '#5d6fa3'
parts = []
for i, g in enumerate(gs):
    mark = ''
    if i == 0:
        g.style['plain'] = True
        mark = '<g class="pulse">' + arrow_arc(g.x, g.y, g.r * 0.6, -170, 75, w=16, head=34) + '</g>'
        parts.append(svg_gear(g, YEL, mark))
    elif i == len(gs) - 1:
        g.style['plain'] = True
        mark = (f'<g class="bob"><circle cx="{g.x:.1f}" cy="{g.y:.1f}" r="{g.r * 0.5:.1f}" fill="#f1e6d0" stroke="#111318" stroke-width="5"/>'
                f'<text x="{g.x:.1f}" y="{g.y + g.r * 0.3:.1f}" text-anchor="middle" font-family="Alfa" font-size="{g.r * 0.85:.0f}" fill="#111318">?</text></g>')
        parts.append(svg_gear(g, RED, mark))
    else:
        parts.append(svg_gear(g, STEEL))
x, y, w, h = bbox(gs, 14)
s = max(w, h); x -= (s - w) / 2; y -= (s - h) / 2   # square viewBox, centred
P = {'view': f'{x:.1f} {y:.1f} {s:.1f} {s:.1f}', 'svg': ''.join(parts)}
open(os.path.join(HERE, 'puzzle.js'), 'w').write('window.PUZZLE = ' + json.dumps(P) + ';\n')

word = {1: 'CLOCKWISE', -1: 'ANTICLOCKWISE'}
ans = sol[len(gs) - 1][0]
rows = []
for i, g in enumerate(gs):
    nb = [b.name if a == i else gs[a].name for a, b in [(a, gs[b]) for a, b in E] if i in (a, gs.index(b))]
    rows.append(f'| {g.name} | {g.n} | ({g.x:.1f}, {g.y:.1f}) | {g.r:.0f} | {", ".join(nb)} | {word[sol[i][0]].lower()} |')
meshes = '\n'.join(f'- {gs[a].name}-{gs[b].name}: centre distance {math.hypot(gs[a].x - gs[b].x, gs[a].y - gs[b].y):.2f} px = '
                   f'{gs[a].r:.0f} + {gs[b].r:.0f} (pitch circles touch)' for a, b in E)
facts = f"""# brain-01 · Which way does the last gear turn?

Engineering brain test (format v3 trial `tunable.brain_test`, type "focus"). No real-world historical claims; the
puzzle is generated and solved by `puzzle.py` (geometry helpers in `studio/kits/cards/brain/gears.py`).

## Answer
**{word[ans]}** (option {'A' if ans == 1 else 'B'}).

## Working (computed, `python3 puzzle.py`)
- Rule: two external spur gears in mesh always turn in opposite directions.
- The mesh graph is measured from the drawn coordinates (gears mesh only where the centre distance equals the sum of
  the pitch radii; every other pair is checked to have a clearly visible gap of at least 2.5 modules between tooth tips):
{meshes}
- That is one open chain G1-G2-G3-G4-G5-G6-G7, no branches, no loops (a loop of 3 would lock).
- G1 (yellow) turns clockwise, so directions alternate along the chain: G1 cw, G2 acw, G3 cw, G4 acw, G5 cw, G6 acw,
  G7 cw. G7 (red, marked "?") is 6 meshes from G1; 6 is even, so G7 turns the same way as G1.
- Tooth interleave check (a tooth faces a gap on every line of centres): worst error {err:.1e} of a tooth pitch.

| gear | teeth | centre (px) | pitch r | meshes with | turns |
|---|---|---|---|---|---|
""" + '\n'.join(rows) + """

Module 12 px for every gear, so teeth sizes match and the pitch radius is 6 px per tooth. The chain changes heading
at every joint (18, 62, 128, 165, 105, 30 degrees), so it is not a straight line.
"""
open(os.path.join(HERE, 'FACTS.md'), 'w').write(facts)
json.dump({'answer': word[ans], 'option': 'A' if ans == 1 else 'B', 'meshes': [[gs[a].name, gs[b].name] for a, b in E]},
          open(os.path.join(HERE, 'answer.json'), 'w'), indent=1)
print('answer:', word[ans], '| meshes:', len(E), '| interleave err', err, '| view', P['view'])
