"""Gear geometry for cards-kit brain tests: place spur gears, derive the mesh graph from the geometry, solve directions,
and draw them as flat SVG whose teeth really interleave.

All gears share one module m (px per tooth on the pitch diameter), so pitch radius r = m*N/2 and two gears mesh
exactly when the distance between centres equals r1 + r2. Directions are NOT typed in by hand: they come from a BFS
over the contact graph measured from the coordinates, so the drawing and the answer cannot disagree.
"""
import math

ADD, DED = 1.0, 1.25          # addendum / dedendum in modules
TOL = 0.5                     # px tolerance for "touching" (pitch circles tangent)


class Gear:
    def __init__(self, name, teeth, x, y, m):
        self.name, self.n, self.x, self.y, self.m = name, teeth, x, y, m
        self.r = m * teeth / 2
        self.phase = 0.0          # angle (rad) of tooth 0 centre; set by phase_chain()
        self.style = {}

    @property
    def tip(self): return self.r + ADD * self.m


def chain(spec, m, x0, y0):
    """spec = [(name, teeth, heading_deg_from_previous), ...]; first heading ignored. Each gear is placed tangent to
    the previous one along the given heading (screen degrees, 0 = right, 90 = down)."""
    gs = []
    for i, (name, n, hd) in enumerate(spec):
        if i == 0:
            gs.append(Gear(name, n, x0, y0, m)); continue
        p = gs[-1]; r = m * n / 2; d = p.r + r; a = math.radians(hd)
        gs.append(Gear(name, n, p.x + d * math.cos(a), p.y + d * math.sin(a), m))
    return gs


def contacts(gs):
    """Mesh graph measured from the geometry. Raises if any pair is ambiguous (teeth overlap without proper mesh,
    or a visible gap smaller than min_gap that a viewer could read as touching)."""
    E, min_gap = [], 2.5 * gs[0].m
    for i in range(len(gs)):
        for j in range(i + 1, len(gs)):
            a, b = gs[i], gs[j]; d = math.hypot(a.x - b.x, a.y - b.y)
            if abs(d - (a.r + b.r)) < TOL:
                E.append((i, j))
            elif d < a.tip + b.tip + min_gap:
                raise ValueError(f'{a.name}-{b.name}: centre distance {d:.1f} neither meshes ({a.r + b.r:.1f}) '
                                 f'nor clears ({a.tip + b.tip + min_gap:.1f})')
    return E


def solve(gs, driver, driver_dir):
    """driver_dir: +1 clockwise on screen, -1 anticlockwise. Returns {index: (dir, turns_per_driver_turn)}.
    Meshing external gears turn opposite ways; speed ratio = -N_driver/N_driven. Fails on a locked loop."""
    E = contacts(gs); adj = {i: [] for i in range(len(gs))}
    for i, j in E: adj[i].append(j); adj[j].append(i)
    sol, q = {driver: (driver_dir, 1.0)}, [driver]
    while q:
        i = q.pop(0)
        for j in adj[i]:
            d, w = -sol[i][0], sol[i][1] * gs[i].n / gs[j].n
            if j in sol:
                if sol[j][0] != d: raise ValueError('odd loop: the train would lock')
                continue
            sol[j] = (d, w); q.append(j)
    return sol, E


def phase_chain(gs, E, root=0):
    """Rotate each gear so its teeth interleave with its neighbour's: if gear i sits a fraction u_i of a tooth pitch
    off the line of centres, the mate needs u_j = 0.5 - u_i (a gap opposite a tooth)."""
    adj = {i: [] for i in range(len(gs))}
    for i, j in E: adj[i].append(j); adj[j].append(i)
    done, q = {root}, [root]
    while q:
        i = q.pop(0); a = gs[i]
        for j in adj[i]:
            if j in done: continue
            b = gs[j]; th = math.atan2(b.y - a.y, b.x - a.x); P_a, P_b = 2 * math.pi / a.n, 2 * math.pi / b.n
            u_a = ((th - a.phase) / P_a) % 1.0
            b.phase = (th + math.pi) - (0.5 - u_a) * P_b
            done.add(j); q.append(j)


def mesh_check(gs, E, samples=720):
    """Pixel-free interference test: along each line of centres, a tooth of one gear must face a gap of the other."""
    worst = 0.0
    for i, j in E:
        a, b = gs[i], gs[j]; th = math.atan2(b.y - a.y, b.x - a.x)
        u_a = ((th - a.phase) / (2 * math.pi / a.n)) % 1.0
        u_b = ((th + math.pi - b.phase) / (2 * math.pi / b.n)) % 1.0
        err = abs(((u_a + u_b) % 1.0) - 0.5); worst = max(worst, err)
    return worst   # 0 = perfect interleave


def outline(g):
    """Tooth outline path: trapezoid teeth, 0.56 pitch at the root, 0.24 at the tip."""
    P = 2 * math.pi / g.n; rr, rt = g.r - DED * g.m, g.tip; pts = []
    for k in range(g.n):
        c = g.phase + k * P
        for f, rad in ((-0.5, rr), (-0.28, rr), (-0.12, rt), (0.12, rt), (0.28, rr)):
            a = c + f * P; pts.append((g.x + rad * math.cos(a), g.y + rad * math.sin(a)))
    return 'M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in pts) + 'Z'


def arrow_arc(x, y, r, a0, a1, color='#111318', w=12, head=26):
    """Curved arrow from a0 to a1 (degrees, screen; a1 > a0 = clockwise). Arrowhead at a1."""
    A0, A1 = math.radians(a0), math.radians(a1); s = 1 if a1 > a0 else -1
    p0 = (x + r * math.cos(A0), y + r * math.sin(A0)); p1 = (x + r * math.cos(A1), y + r * math.sin(A1))
    large = 1 if abs(a1 - a0) > 180 else 0; sweep = 1 if s > 0 else 0
    tx, ty = -math.sin(A1) * s, math.cos(A1) * s; nx, ny = math.cos(A1), math.sin(A1)
    tip = (p1[0] + tx * head, p1[1] + ty * head)
    b1 = (p1[0] + nx * head * 0.8, p1[1] + ny * head * 0.8); b2 = (p1[0] - nx * head * 0.8, p1[1] - ny * head * 0.8)
    return (f'<path d="M{p0[0]:.1f} {p0[1]:.1f} A{r} {r} 0 {large} {sweep} {p1[0]:.1f} {p1[1]:.1f}" fill="none" '
            f'stroke="{color}" stroke-width="{w}" stroke-linecap="round"/>'
            f'<path d="M{tip[0]:.1f} {tip[1]:.1f} L{b1[0]:.1f} {b1[1]:.1f} L{b2[0]:.1f} {b2[1]:.1f}Z" fill="{color}"/>')


def svg_gear(g, fill='#5d6fa3', mark=''):
    """One gear: teeth body, lightening holes on big gears, hub. `mark` is extra SVG drawn on top (arrow, '?', label)."""
    s = [f'<path d="{outline(g)}" fill="{fill}" stroke="#111318" stroke-width="5" stroke-linejoin="round"/>']
    hub = max(14, g.r * 0.22)
    if g.r >= 70 and not g.style.get('plain'):
        rh, ch = (g.r - DED * g.m + hub) / 2, (g.r - DED * g.m - hub) * 0.28
        for k in range(5):
            a = g.phase + k * 2 * math.pi / 5 + math.pi / 5
            s.append(f'<circle cx="{g.x + rh * math.cos(a):.1f}" cy="{g.y + rh * math.sin(a):.1f}" r="{ch:.1f}" '
                     f'fill="#f1e6d0" stroke="#111318" stroke-width="4"/>')
    s.append(f'<circle cx="{g.x:.1f}" cy="{g.y:.1f}" r="{hub:.1f}" fill="#111318"/>'
             f'<circle cx="{g.x:.1f}" cy="{g.y:.1f}" r="{hub * 0.4:.1f}" fill="#f1e6d0"/>')
    return '<g>' + ''.join(s) + mark + '</g>'


def bbox(gs, pad):
    x0 = min(g.x - g.tip for g in gs) - pad; y0 = min(g.y - g.tip for g in gs) - pad
    x1 = max(g.x + g.tip for g in gs) + pad; y1 = max(g.y + g.tip for g in gs) + pad
    return x0, y0, x1 - x0, y1 - y0
