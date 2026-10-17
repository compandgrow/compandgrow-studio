#!/usr/bin/env python3
"""HULL 7 — the whole film as data: one tall briefing wall (9:16), one continuous camera, timed ink,
tags, magnets, stamps and cards, sound events and subtitles -> scenes/film.json, audio/cues.json, audio/timeline.json.
Timed on the narration (audio/vo/dur.json) and snapped to a 104 BPM sixteenth grid for hits.
Board px; at zoom 1 the 1080 x 1920 frame shows 1,080 x 1,920 board px.
"""
import json, math, os

HERE = os.path.dirname(os.path.abspath(__file__)); FILM = os.path.dirname(HERE)
VO = json.load(open(os.path.join(FILM, 'audio', 'vo', 'dur.json')))
SUBTXT = json.load(open(os.path.join(FILM, 'audio', 'subs.json')))

BW, BH = 3600, 6400
RIGHT_ZONE = [2700, 0, BW, BH]          # secondary layer: never in shot before the reveal
BPM = 104; BEAT = 60 / BPM; SIX = BEAT / 4
snap = lambda t: round(round(t / SIX) * SIX, 4)

E, EV = [], []
def el(**k): E.append(k); return k
def ev(t, type, **k): EV.append(dict(t=round(t, 4), type=type, **k)); return t

class Cam:
    def __init__(s, x, y, z, roll=0):
        s.base = dict(x=x, y=y, z=z, roll=roll); s.cur = dict(x=x, y=y, lz=math.log(z), roll=roll); s.moves = []; s.shakes = []
    def to(s, t, d, x=None, y=None, z=None, roll=None, a=2, b=2):
        m = dict(t=round(t, 4), d=round(d, 4), a=a, b=b)
        if x is not None: m['dx'] = round(x - s.cur['x'], 2); s.cur['x'] = x
        if y is not None: m['dy'] = round(y - s.cur['y'], 2); s.cur['y'] = y
        if z is not None: m['dl'] = math.log(z) - s.cur['lz']; s.cur['lz'] = math.log(z)
        if roll is not None: m['dr'] = roll - s.cur['roll']; s.cur['roll'] = roll
        s.moves.append(m); return t + d
    def shake(s, t, amp=6, f=9, k=7, dir=(0, 1), roll=0):
        s.shakes.append(dict(t=t, amp=amp, f=f, k=k, dir=list(dir), roll=roll))
    def json(s):
        return dict(x=s.base['x'], y=s.base['y'], z=s.base['z'], roll=s.base['roll'], moves=s.moves, shakes=s.shakes)

def wavy(x0, y0, x1, y1, amp, n, seed):
    pts = []
    for i in range(n + 1):
        u = i / n; w = amp * (math.sin(u * 7.3 + seed) * .6 + math.sin(u * 17.1 + seed * 2) * .4) * math.sin(u * math.pi) ** .5
        nx, ny = -(y1 - y0), (x1 - x0); L = math.hypot(nx, ny); nx, ny = nx / L, ny / L
        pts.append([round(x0 + (x1 - x0) * u + nx * w, 1), round(y0 + (y1 - y0) * u + ny * w, 1)])
    return pts
R = lambda p: [[round(a, 1), round(b, 1)] for a, b in p]

# ================================================================= narration timeline
# (line id, pause before it). Each line holds its subtitle for max(1.8, speech + .6) s; the next line never starts earlier.
ORDER = [('a1', .25), ('a2', .1), ('a3', .15),
         ('b1', .7), ('b2', .05), ('b3', .05), ('b4', .35),
         ('c1', .9), ('c2', .2), ('c3', .1), ('c4', .3),
         ('d1', .9), ('d2', .2),
         ('e1', 1.0), ('e2', .2), ('e3', .05), ('e4', .3),
         ('f1', 1.0), ('f2', .5), ('f3', .2), ('f4', .6),
         ('g1', .9), ('g2', .1), ('g3', .2), ('g4', .6), ('g5', .05),
         ('h1', .9), ('h2', .45), ('h3', .5), ('h4', .45), ('h5', .5), ('h6', .45),
         ('i1', 2.1), ('i2', .3), ('i3', .05),
         ('j1', 1.2), ('j2', 1.2), ('j3', .9)]
T = {}; t = 0.0; prev_end = 0.0
for k, gap in ORDER:
    t0 = max(prev_end + gap, t)
    t0 = round(math.ceil(t0 / SIX - 1e-9) * SIX, 4)  # every line starts on the sixteenth grid
    T[k] = t0; d = VO[k]
    hold = max(1.8, d + .6)
    t = t0 + hold                                    # earliest next start: this subtitle has been read
    prev_end = t0 + d
END = lambda k: T[k] + VO[k]
DUR = round(END('j3') + 4.2, 3)

# ================================================================= S1 the hook: a hull, an eye, a question (y 250-1250)
HX0, HX1, WL1 = 480, 1700, 1040
def hull_side(x0, x1, wl, s=1.0):
    L = x1 - x0; dk = wl - 120 * s
    hull = [[x0 + L * .06, dk], [x1 - L * .02, dk - 18 * s], [x1, dk - 30 * s], [x1 - L * .05, wl + 10 * s], [x0 + L * .09, wl + 10 * s], [x0, dk + 14 * s], [x0 + L * .06, dk]]
    sup = [[x0 + L * .34, dk], [x0 + L * .34, dk - 120 * s], [x0 + L * .58, dk - 120 * s], [x0 + L * .58, dk]]
    br = [[x0 + L * .40, dk - 120 * s], [x0 + L * .40, dk - 190 * s], [x0 + L * .53, dk - 190 * s], [x0 + L * .53, dk - 120 * s]]
    mast = [[x0 + L * .47, dk - 190 * s], [x0 + L * .47, dk - 330 * s]]
    yard = [[x0 + L * .43, dk - 290 * s], [x0 + L * .51, dk - 290 * s]]
    gun = [[x0 + L * .74, dk], [x0 + L * .74, dk - 46 * s], [x0 + L * .8, dk - 46 * s], [x0 + L * .8, dk]]
    barrel = [[x0 + L * .8, dk - 30 * s], [x0 + L * .9, dk - 42 * s]]
    return [R(hull), R(sup), R(br), R(mast), R(yard), R(gun), R(barrel)]
h1 = hull_side(HX0, HX1, WL1)
for i, pts in enumerate(h1):
    el(type='ink', kind='line', id=f'h1_{i}', points=pts, lw=13 if i == 0 else 10, color='graphite', t=round(-.9 + i * .16, 3), d=.5 if i == 0 else .22, ea=1.5, eb=2.4,
       erase=dict(t=round(T['b4'] + 1.25, 3), d=.6))
el(type='ink', kind='line', id='wl1', points=wavy(HX0 - 180, WL1 + 22, HX1 + 220, WL1 + 22, 7, 40, 1.1), lw=8, color='water', t=.15, d=.55, ea=1.6, eb=2.2)
ev(-.2, 'ink', d=.6, kind='line'); ev(.15, 'ink', d=.5, kind='line', v=.5)
EYE1 = (2120, 760)
def eye(c, w, t0, idp, col='graphite'):
    cx, cy = c; up = [[cx - w / 2 + w * u, cy - math.sin(u * math.pi) * w * .32] for u in [i / 16 for i in range(17)]]
    dn = [[cx - w / 2 + w * u, cy + math.sin(u * math.pi) * w * .26] for u in [i / 16 for i in range(17)]]
    el(type='ink', kind='line', id=idp + '_u', points=R(up), lw=10, color=col, t=t0, d=.25)
    el(type='ink', kind='line', id=idp + '_d', points=R(dn), lw=10, color=col, t=t0 + .12, d=.25)
    el(type='ink', kind='ring', id=idp + '_p', c=[cx, cy - 2], r=w * .16, lw=10, color=col, t=t0 + .3, d=.22)
    ev(t0, 'ink', d=.55, kind='line', v=.5)
eye(EYE1, 220, snap(T['a2'] - .1), 'eye1')
el(type='ink', kind='line', id='sight1', points=[[EYE1[0] - 140, EYE1[1] + 10], [HX1 - 220, WL1 - 170]], lw=8, color='grey', dash=[24, 18], arrow=True, t=snap(T['a2'] + .7), d=.5)
ev(T['a2'] + .7, 'ink', d=.5, kind='line', v=.4)
el(type='tag', id='tag_seen', text='SEEN?', xy=[1960, 470], size=92, rot=-3, magnetColor='red', arrive=dict(t=snap(T['a3'] + .05), kind='swing', d=.8, amp=10),
   strike=dict(t=round(T['j3'] + .05, 3), d=.25, color='red'))
ev(T['a3'] + .05, 'tag', v=.9)

# ================================================================= S2 light's path (sun -> hull -> eye); break it, the ship is gone
SUN = (420, 330)
el(type='ink', kind='ring', id='sun', c=list(SUN), r=88, lw=11, color='graphite', t=snap(T['b1']), d=.35)
for i in range(8):
    a = i * math.pi / 4
    el(type='ink', kind='line', id=f'sun_r{i}', points=R([[SUN[0] + 118 * math.cos(a), SUN[1] + 118 * math.sin(a)], [SUN[0] + 168 * math.cos(a), SUN[1] + 168 * math.sin(a)]]),
       lw=9, color='graphite', t=round(T['b1'] + .35 + i * .04, 3), d=.08)
ev(T['b1'], 'ink', d=.7, kind='line', v=.6)
HIT1 = (HX0 + (HX1 - HX0) * .44, WL1 - 250)
el(type='ink', kind='line', id='ray_in', points=R([[SUN[0] + 120, SUN[1] + 110], HIT1]), lw=11, color='blue', arrow=True, t=snap(T['b1'] + .9), d=.5, ea=1.4, eb=2.4)
el(type='ink', kind='line', id='ray_out', points=R([HIT1, [EYE1[0] - 150, EYE1[1] - 10]]), lw=11, color='blue', arrow=True, t=snap(T['b3']), d=.75, ea=1.4, eb=2.4)
ev(T['b1'] + .9, 'dimzip', d=.5, v=.6); ev(T['b1'] + 1.4, 'arrow', v=.7); ev(T['b3'], 'dimzip', d=.75, v=.7); ev(T['b3'] + .75, 'arrow', v=.9)
BRK = ((HIT1[0] + EYE1[0] - 150) / 2 + 120, (HIT1[1] + EYE1[1]) / 2 - 10)
el(type='ink', kind='line', id='break1', points=R([[BRK[0] - 70, BRK[1] - 70], [BRK[0] + 70, BRK[1] + 70]]), lw=14, color='red', t=snap(T['b4'] + .2), d=.18)
el(type='ink', kind='line', id='break2', points=R([[BRK[0] + 70, BRK[1] - 70], [BRK[0] - 70, BRK[1] + 70]]), lw=14, color='red', t=snap(T['b4'] + .45), d=.18)
ev(T['b4'] + .2, 'ink', d=.18, kind='line', v=.9); ev(T['b4'] + .45, 'ink', d=.18, kind='line', v=.9)
ev(T['b4'] + 1.25, 'erase', d=.6)
for e in E:
    if e.get('id') in ('ray_in', 'ray_out', 'sight1'): e['erase'] = dict(t=round(T['b4'] + 1.3, 3), d=.5)

# ================================================================= S3 the precedent: degaussing (y 1400-2300)
HX2a, HX2b, WL2 = 420, 1560, 2020
h2 = hull_side(HX2a, HX2b, WL2, .8)
t3 = snap(T['c1'] - .2)
for i, pts in enumerate(h2):
    el(type='ink', kind='line', id=f'h2_{i}', points=pts, lw=12 if i == 0 else 9, color='graphite', t=round(t3 + i * .12, 3), d=.4 if i == 0 else .18, ea=1.5, eb=2.4)
ev(t3, 'ink', d=1.0, kind='line', v=.7)
el(type='ink', kind='line', id='wl2', points=wavy(HX2a - 160, WL2 + 22, 2300, WL2 + 22, 7, 44, 2.7), lw=8, color='water', t=round(t3 + .5, 3), d=.6)
# the cable: a coil wound along the hull, drawn as the narrator says "wrapped in cable"
coil = []; L2 = HX2b - HX2a; dk2 = WL2 - 96
for i in range(0, 241):
    u = i / 240; x = HX2a + L2 * (.08 + .86 * u); ph = u * 2 * math.pi * 14
    coil.append([x + 10 * math.cos(ph), dk2 + 52 + 50 * math.sin(ph)])
el(type='ink', kind='line', id='coil2', points=R(coil), lw=7, color='graphite', t=snap(T['c2'] + .5), d=2.2, ea=1.2, eb=1.6)
ev(T['c2'] + .5, 'scribble', d=2.2, v=.5)
el(type='tag', id='tag_degauss', text='DEGAUSSING · 1940', xy=[700, 1500], size=74, rot=1.5, arrive=dict(t=snap(T['c2'] + .2), kind='swing', d=.8, amp=8))
ev(T['c2'] + .2, 'tag', v=.6)
MINE = (2020, 2280)
el(type='ink', kind='ring', id='mine', c=list(MINE), r=70, lw=11, color='graphite', t=snap(T['c3'] - .1), d=.3)
for i in range(8):
    a = i * math.pi / 4 + .3
    el(type='ink', kind='line', id=f'mine_s{i}', points=R([[MINE[0] + 72 * math.cos(a), MINE[1] + 72 * math.sin(a)], [MINE[0] + 108 * math.cos(a), MINE[1] + 108 * math.sin(a)]]),
       lw=9, color='graphite', t=round(T['c3'] + .22 + i * .035, 3), d=.06)
el(type='ink', kind='line', id='mine_chain', points=[[MINE[0], MINE[1] + 110], [MINE[0], MINE[1] + 230]], lw=6, color='grey', dash=[12, 10], t=round(T['c3'] + .5, 3), d=.3)
ev(T['c3'] - .1, 'ink', d=.7, kind='line', v=.6)
el(type='ink', kind='write', id='w_mine', text='mine', xy=[MINE[0] + 150, MINE[1] + 30], size=78, color='graphite', t=round(T['c3'] + .5, 3), d=.3)
# the hull's magnetic field reaching the mine: dashed grey arcs, wiped to a ghost when the coils cancel it
for j in range(4):
    r_ = 260 + j * 150; cx, cy = (HX2a + HX2b) / 2, WL2 - 40
    arc = [[cx + r_ * 1.25 * math.cos(a), cy + r_ * .62 * math.sin(a)] for a in [math.radians(-10 + q * 6) for q in range(0, 21)]]
    el(type='ink', kind='line', id=f'field{j}', points=R(arc), lw=7, color='grey', dash=[20, 14], t=round(T['c3'] + .6 + j * .14, 3), d=.4,
       erase=dict(t=round(T['c4'] + .3 + j * .08, 3), d=.4))
ev(T['c3'] + .6, 'ink', d=.9, kind='line', v=.4); ev(T['c4'] + .3, 'erase', d=.7)
el(type='ink', kind='write', id='w_field', text='magnetic field', xy=[1560, 2440], size=78, color='grey', t=round(T['c3'] + 1.0, 3), d=.5, erase=dict(t=round(T['c4'] + .5, 3), d=.4))

# ================================================================= S4 the question (y 2550-2850)
el(type='ink', kind='write', id='w_hull7', text='HULL 7', xy=[300, 2700], size=230, color='graphite', t=snap(T['d1']), d=.55)
ev(T['d1'], 'ink', d=.55, kind='write', v=1.0)
el(type='ink', kind='line', id='ul_hull7', points=[[300, 2740], [1050, 2730]], lw=11, color='graphite', t=snap(T['d1'] + .65), d=.2)
el(type='ink', kind='write', id='w_q', text='coils vs. light?', xy=[1170, 2700], size=120, color='graphite', t=snap(T['d2'] + .1), d=.7)
ev(T['d1'] + .65, 'ink', d=.2, kind='line', v=.5); ev(T['d2'] + .1, 'ink', d=.7, kind='write', v=.8)

# ================================================================= S5 the mirage (y 2950-3550)
ROAD = 3460
el(type='ink', kind='line', id='road', points=[[260, ROAD], [2350, ROAD]], lw=12, color='graphite', t=snap(T['e1'] - .1), d=.5, ea=1.5, eb=2.4)
for i in range(9):
    x0 = 300 + i * 230
    el(type='ink', kind='line', id=f'dash{i}', points=[[x0, ROAD + 40], [x0 + 110, ROAD + 40]], lw=8, color='grey', t=round(T['e1'] + .2 + i * .04, 3), d=.06)
ev(T['e1'] - .1, 'ink', d=.8, kind='line', v=.6)
heat = []
for j, y in enumerate((ROAD - 34, ROAD - 72, ROAD - 110)):
    for i in range(5):
        x0 = 520 + i * 360 + (j % 2) * 120
        heat.append(dict(points=wavy(x0, y, x0 + 210, y, 9, 10, i + j * 3), t=round(T['e2'] + .3 + (i + j * 5) * .05, 3), d=.12, lw=6, color='grey'))
el(type='ink', kind='hatch', id='heat', strokes=heat, lw=6, color='grey', alpha=.8)
ev(T['e2'] + .3, 'scribble', d=.8, v=.35)
el(type='ink', kind='write', id='w_hot', text='hot air', xy=[1900, ROAD - 150], size=78, color='grey', t=snap(T['e2'] + .8), d=.35)
EYE2 = (360, ROAD - 330)
eye(EYE2, 170, snap(T['e3'] - .15), 'eye2')
# a ray from the sky dips toward the road, bends in the hot layer and rises to the eye
ray = []
for i in range(41):
    u = i / 40; x = 2250 - (2250 - EYE2[0] - 110) * u
    y = (ROAD - 760) + (EYE2[1] - (ROAD - 760)) * u + 640 * math.sin(u * math.pi) ** 1.35 * .78
    ray.append([x, y])
el(type='ink', kind='line', id='mirage_ray', points=R(ray), lw=11, color='blue', arrow=True, t=snap(T['e3'] + .2), d=1.4, ea=1.3, eb=2.2)
ev(T['e3'] + .2, 'dimzip', d=1.4, v=.6); ev(T['e3'] + 1.6, 'arrow', v=.8)
el(type='tag', id='tag_mirage', text='MIRAGE', xy=[1460, 3050], size=80, rot=-2, arrive=dict(t=snap(T['e4']), kind='swing', d=.8, amp=9))
ev(T['e4'], 'tag', v=.7)

# ================================================================= S6 the signature: light goes around the hull (y 3700-4450)
SC = (1250, 4080); RX0, RY0 = 330, 170
sec = hull_side(SC[0] - 300, SC[0] + 300, SC[1] + 95, .55)
for i, pts in enumerate(sec[:5]):
    el(type='ink', kind='line', id=f'h3_{i}', points=pts, lw=11 if i == 0 else 8, color='graphite', t=round(snap(T['f1']) + i * .1, 3), d=.32 if i == 0 else .15)
ev(T['f1'], 'ink', d=.8, kind='line', v=.6)
for j in range(3):
    el(type='ink', kind='ring', id=f'shell{j}', c=list(SC), r=[RX0 + j * 70, RY0 + j * 52], lw=7, color='blue', dash=[22, 16], t=round(T['f1'] + .9 + j * .22, 3), d=.5)
ev(T['f1'] + .9, 'ink', d=1.1, kind='line', v=.5)
el(type='ink', kind='write', id='w_layer', text='graded layer', xy=[SC[0] + RX0 + 200, SC[1] - RY0 - 120], size=74, color='blue', t=round(T['f1'] + 1.6, 3), d=.45)
# five rays from the sea behind (left) curve around the shell and leave on their original lines
OUTX = RX0 + 140 + 60; OUTY = RY0 + 104 + 50
rays = []
for k, yo in enumerate((-150, -75, 0, 75, 150)):
    y = SC[1] + yo; pts = []
    for i in range(121):
        x = 230 + (2200 - 230) * i / 120; dx = (x - SC[0]) / (OUTX * 1.05)
        if abs(dx) < 1:
            bump = math.sqrt(1 - dx * dx); sgn = -1 if yo < 0 else (1 if yo > 0 else (-1))
            push = (OUTY * bump - abs(yo) * bump) if abs(yo) < OUTY else 0
            yy = y + sgn * max(0, push) * (1 if yo != 0 else 1.0)
        else: yy = y
        pts.append([x, yy])
    rays.append(pts)
for k, pts in enumerate(rays):
    t0 = round(T['f2'] + .3 + k * .28, 3)
    el(type='ink', kind='line', id=f'cray{k}', points=R(pts), lw=10, color='blue', arrow=True, t=t0, d=1.5, ea=1.3, eb=2.0)
    ev(t0, 'dimzip', d=1.5, v=.45)
EYE3 = (2330, SC[1])
eye(EYE3, 190, snap(T['f3'] + .4), 'eye3')
el(type='tag', id='tag_sea', text='SEES: OPEN SEA', xy=[1500, SC[1] + 330], size=76, rot=1.5, arrive=dict(t=snap(T['f4'] + 1.1), kind='swing', d=.8, amp=9))
ev(T['f4'] + 1.1, 'tag', v=.8)

# ================================================================= S7 the build: 46 coil bands along a 93 m hull (y 4650-5250)
BX0, BX1, WL4 = 360, 2160, 5000
h4 = hull_side(BX0, BX1, WL4, 1.15)
for i, pts in enumerate(h4):
    el(type='ink', kind='line', id=f'h4_{i}', points=pts, lw=13 if i == 0 else 9, color='graphite', t=round(snap(T['g1'] - .5) + i * .1, 3), d=.45 if i == 0 else .18, ea=1.5, eb=2.4)
ev(T['g1'] - .5, 'ink', d=1.0, kind='line', v=.7)
PXM = (BX1 - BX0) / 93.0
DKY = WL4 - 138 + 60
t_mag0 = snap(T['g1'] + .35)
for n in range(46):
    x = BX0 + (1.25 + n * 2) * PXM; tn = round(t_mag0 + n * SIX, 4)
    el(type='magnet', id=f'band{n}', xy=[round(x, 1), DKY], r=15, color='blue' if n % 5 == 0 else 'graphite', z=14, arrive=dict(t=round(tn - .05, 4), kind='snap', d=.3, lift=60))
    ev(tn, 'pin', v=.35 + .3 * ((n % 4) == 0), n=n)
el(type='ink', kind='dim', id='dim93', **{'from': [BX0, WL4 + 150], 'to': [BX1, WL4 + 150]}, lw=11, color='blue',
   ext=[[BX0, WL4 + 20, WL4 + 180], [BX1, WL4 + 20, WL4 + 180]], extColor='grey', t=snap(T['g3']), d=.7, ea=1.5, eb=2.6)
ev(T['g3'], 'dimzip', d=.7, v=.9); ev(T['g3'] + .7, 'arrow', v=1.0)
el(type='ink', kind='write', id='w93', text='93 m', xy=[(BX0 + BX1) / 2, WL4 + 290], size=120, color='blue', align='center', t=snap(T['g3'] + .7), d=.4)
el(type='ink', kind='write', id='w46', text='46 bands', xy=[BX0, 4560], size=110, color='graphite', t=snap(T['g1'] + .1), d=.5)
el(type='ink', kind='write', id='w2m', text='every 2 m', xy=[BX0 + 1200, 4560], size=100, color='blue', t=snap(T['g2'] + .4), d=.5)
ev(T['g1'] + .1, 'ink', d=.5, kind='write'); ev(T['g2'] + .4, 'ink', d=.5, kind='write', v=.6); ev(T['g3'] + .7, 'ink', d=.4, kind='write', v=.7)
# power: a card for the generators, and a dimension line that climbs
el(type='card', id='gen', xy=[800, 5560], w=860, h=320, rot=-1.2, z=8, magnetR=20, magnets=[[-380, -130, 'graphite'], [380, -130, 'graphite']],
   arrive=dict(t=round(snap(T['g4']) - .3, 3), kind='drop', d=.3, lift=200, land=.9),
   lines=[dict(text='GENERATORS', font='mono', weight=600, size=56, x=48, y=-40, color='graphite', track=2),
          dict(text='4 × 1.2 MW', font='sans', weight=800, size=96, x=48, y=80, color='graphite')])
ev(T['g4'], 'land', size='mid', v=.8); ev(T['g4'] + .12, 'pin', v=.5); ev(T['g4'] + .25, 'pin', v=.5)
el(type='ink', kind='dim', id='dimP', **{'from': [1420, 5700], 'to': [1420, 5330]}, lw=11, color='blue', t=snap(T['g5'] + .1), d=.45, ea=1.4, eb=2.8)
el(type='ink', kind='write', id='wP', text='4.8 MW', xy=[1500, 5560], size=120, color='blue', t=snap(T['g5'] + .55), d=.45)
ev(T['g5'] + .1, 'dimzip', d=.45, v=.8); ev(T['g5'] + .55, 'arrow', v=.9); ev(T['g5'] + .55, 'ink', d=.45, kind='write', v=.7)

# ================================================================= S8 the trials: three ranges, three stamps (y 5850-6250 is too low: use the left column below)
TR = [('h1', 'h2', '500 m', 520), ('h3', 'h4', '2 km', 1000), ('h5', 'h6', '8 km', 1520)]
TRY = [5860, 6060, 6260]
for i, ((la, lb, txt, L), y) in enumerate(zip(TR, TRY)):
    tl = snap(T[la] + .15)
    eye((300, y), 120, round(tl - .25, 3), f'eyeT{i}')
    el(type='ink', kind='dim', id=f'dimT{i}', **{'from': [390, y], 'to': [390 + L, y]}, lw=10, color='blue', t=tl, d=.5 + .15 * i, ea=1.4, eb=2.6)
    ev(tl, 'dimzip', d=.5 + .15 * i, v=.6 + .15 * i); ev(tl + .5 + .15 * i, 'arrow', v=.8)
    el(type='ink', kind='write', id=f'wT{i}', text=txt, xy=[390 + L / 2, y - 34], size=86, color='blue', align='center', t=round(tl + .3, 3), d=.3)
    ts = snap(T[lb] - .02)
    el(type='stamp', id=f'stampT{i}', text='NOT SEEN', xy=[390 + L + 250, y - 6], size=74, rot=(-6, 4, -3)[i], t=ts, seed=11 + i)
    ev(ts, 'stamp', v=.8 + .1 * i)

# ================================================================= S9 the side effect: a compass that can't be trusted
CP = (2250, 5480)
el(type='ink', kind='ring', id='compass', c=list(CP), r=150, lw=11, color='graphite', t=snap(T['i1'] - .1), d=.4)
el(type='ink', kind='ring', id='compass_i', c=list(CP), r=118, lw=5, color='grey', t=round(T['i1'] + .2, 3), d=.3)
for i, a in enumerate((0, 90, 180, 270)):
    r_ = math.radians(a - 90)
    el(type='ink', kind='line', id=f'cmp_t{i}', points=R([[CP[0] + 118 * math.cos(r_), CP[1] + 118 * math.sin(r_)], [CP[0] + 140 * math.cos(r_), CP[1] + 140 * math.sin(r_)]]), lw=7, color='graphite', t=round(T['i1'] + .5 + i * .05, 3), d=.06)
el(type='ink', kind='write', id='w_N', text='N', xy=[CP[0], CP[1] - 175], size=70, color='graphite', align='center', t=round(T['i1'] + .7, 3), d=.15)
# the needle points the wrong way: drawn, wiped to a ghost, drawn again rotated
for j, ang in enumerate((-20, 75, 160)):
    a = math.radians(ang - 90); tip = [CP[0] + 105 * math.cos(a), CP[1] + 105 * math.sin(a)]; tail = [CP[0] - 70 * math.cos(a), CP[1] - 70 * math.sin(a)]
    tn = round(T['i2'] + j * .5, 3)
    el(type='ink', kind='line', id=f'needle{j}', points=R([tail, tip]), lw=12, color='red' if j == 2 else 'graphite', arrow=True, t=tn, d=.18,
       **({'erase': dict(t=round(tn + .45, 3), d=.2)} if j < 2 else {}))
    ev(tn, 'rattle', v=.7 - .15 * j)
el(type='ink', kind='write', id='w_side', text='compasses: unreliable', xy=[CP[0] - 360, CP[1] + 290], size=64, color='red', t=snap(T['i3'] + .1), d=.6)
el(type='ink', kind='write', id='w_200', text='< 200 m', xy=[CP[0] - 360, CP[1] + 380], size=64, color='blue', t=snap(T['i3'] + .8), d=.3)
ev(T['i3'] + .1, 'ink', d=.6, kind='write', v=.7)

# ================================================================= the right zone: seen whole only in the reveal
VER = (3150, 5900)
el(type='stamp', id='stamp_cleared', text='CLEARED', xy=[VER[0], VER[1] - 130], size=150, rot=-7, t=snap(T['j1'] + .35), seed=31)
el(type='ink', kind='write', id='w_trials', text='for sea trials', xy=[VER[0], VER[1] + 90], size=96, color='graphite', align='center', t=snap(T['j1'] + .8), d=.6)
ev(T['j1'] + .35, 'stamp', v=1.0, big=1); ev(T['j1'] + .8, 'ink', d=.6, kind='write', v=.7)
el(type='ink', kind='line', id='leader', points=[[2600, 6200], [2780, 6120], [2880, 6010]], lw=10, color='graphite', arrow=True, t=snap(T['j1'] - .2), d=.5)
ev(T['j1'] - .2, 'ink', d=.5, kind='line', v=.6)
el(type='card', id='note_sum', xy=[3100, 2300], w=760, h=300, rot=3, z=7, magnetR=18, magnets=[[0, -120, 'blue']],
   lines=[dict(rule=True, x=30, y=-60, w=700, h=3, color='blue'), dict(text='46 × 2 m = 92 m', font='marker', size=74, x=40, y=30, color='blue'),
          dict(text='fits a 93 m hull', font='marker', size=60, x=40, y=110, color='graphite')])
el(type='card', id='note_pow', xy=[3080, 4700], w=720, h=300, rot=-2.5, z=7, magnetR=18, magnets=[[0, -120, 'blue']],
   lines=[dict(rule=True, x=30, y=-60, w=660, h=3, color='blue'), dict(text='4 × 1.2 = 4.8 MW', font='marker', size=72, x=40, y=30, color='blue'),
          dict(text='field + losses', font='marker', size=60, x=40, y=110, color='graphite')])
el(type='card', id='spec', xy=[3120, 3500], w=820, h=560, rot=-.8, z=7, magnetR=20, magnets=[[-360, -240, 'graphite'], [360, -240, 'graphite']],
   lines=[dict(text='SPEC SHEET', font='mono', weight=600, size=60, x=48, y=-160, color='graphite', track=2),
          dict(text='Hull      93 m', font='mono', weight=500, size=52, x=48, y=-70, color='graphite'),
          dict(text='Bands     46', font='mono', weight=500, size=52, x=48, y=0, color='graphite'),
          dict(text='Pitch     2 m', font='mono', weight=500, size=52, x=48, y=70, color='graphite'),
          dict(text='Power     4.8 MW', font='mono', weight=500, size=52, x=48, y=140, color='graphite'),
          dict(text='Layer     3 shells', font='mono', weight=500, size=52, x=48, y=210, color='graphite')])
# section A-A sketch, top right (drawn before the film starts; seen only in the reveal)
AX, AY = 3150, 1150
el(type='ink', kind='write', id='w_AA', text='SECTION A–A', xy=[AX - 330, AY - 330], size=78, color='graphite', t=-5, d=.1)
el(type='ink', kind='line', id='aa_hull', points=R([[AX - 230, AY - 120], [AX - 200, AY + 120], [AX, AY + 190], [AX + 200, AY + 120], [AX + 230, AY - 120], [AX - 230, AY - 120]]), lw=9, color='graphite', t=-5, d=.1)
for j in range(3): el(type='ink', kind='ring', id=f'aa_sh{j}', c=[AX, AY + 20], r=[300 + j * 55, 250 + j * 50], lw=6, color='blue', dash=[18, 14], t=-5, d=.1)
el(type='ink', kind='line', id='aa_wl', points=wavy(AX - 450, AY + 60, AX + 450, AY + 60, 5, 24, 4.4), lw=7, color='water', t=-5, d=.1)
# title block, bottom right
el(type='card', id='title', xy=[3120, 300], w=820, h=420, rot=.6, z=8, magnetR=24, magnets=[[-350, -160, 'red'], [350, -160, 'graphite']],
   lines=[dict(text='HULL 7', font='sans', weight=900, size=150, x=56, y=0, color='graphite', track=4),
          dict(rule=True, x=58, y=40, w=160, h=10, color='red'),
          dict(text='REFRACTIVE FIELD STUDY', font='mono', weight=600, size=46, x=58, y=120, color='graphite', track=2),
          dict(text='BRIEFING · SEA TRIALS', font='mono', weight=500, size=42, x=58, y=180, color='grey', track=2)])
# the opening question answered: a second tag lands beside the struck one
el(type='tag', id='tag_notseen', text='NOT SEEN', xy=[1960, 610], size=92, rot=2.5, magnetColor='red', arrive=dict(t=snap(T['j3'] + .1), kind='swing', d=.9, amp=12))
ev(T['j3'] + .1, 'tag', v=1.0); ev(T['j3'] + .05, 'strike', v=.8)

# ================================================================= camera
def fit(x0, x1, y0, y1, m=70, at=.40, zmax=1.4):
    w, h = x1 - x0 + 2 * m, y1 - y0 + 2 * m
    z = min(1080 / w, 1500 / h, zmax); Hv = 1920 / z
    return dict(x=(x0 + x1) / 2, y=(y0 + y1) / 2 + (.5 - at) * Hv, z=round(z, 4))
def go(t, d, f, a=2, b=2.6, roll=None): return c.to(t, d, x=f['x'], y=f['y'], z=f['z'], roll=roll, a=a, b=b)
F_hook = fit(380, 1800, 560, 1140, at=.42)
c = Cam(F_hook['x'], F_hook['y'], F_hook['z'] * 1.12, roll=-2.0)
c.to(0, 1.6, z=F_hook['z'], roll=0, a=1.6, b=2.8)                                     # settle off the hull
go(T['a2'] - .2, 1.6, fit(420, 2300, 380, 1140, at=.42))                               # widen to the eye and the question
go(T['a3'] + .1, 1.4, fit(1150, 2300, 380, 1100, at=.42))                    # push on "it can be seen"
go(T['b1'] - .3, 1.3, fit(230, 2320, 150, 1150, at=.42))                               # pull back and up: the sun comes in
c.to(T['b3'] - .1, 1.6, x=fit(230, 2320, 150, 1150)['x'] + 60, a=2, b=2.2)             # ride the ray toward the eye
c.to(T['b4'] + .1, .9, roll=-1.0, a=2, b=2.4)                                           # the break
go(T['c1'] - .5, 1.9, fit(300, 1700, 1420, 2120, at=.42), roll=0)                       # tilt down to the precedent
go(T['c3'] - .2, 1.6, fit(250, 2300, 1420, 2470, at=.42))                               # widen to the mine and its field
go(T['d1'] - .45, 1.4, fit(260, 1150, 2450, 2780, at=.45))                              # down to the question
go(T['d2'], 1.4, fit(260, 2050, 2450, 2780, at=.45))                                    # ride the question
go(T['e1'] - .45, 1.6, fit(230, 2400, 2950, 3520, at=.42), roll=-1.2)                   # the mirage: slight Dutch tilt
c.to(T['e3'], 2.2, z=c.cur and math.exp(c.cur['lz']) * 1.06, a=2, b=2.2)                # slow push as the ray bends
go(T['f1'] - .55, 1.7, fit(820, 1980, 3780, 4380, at=.42), roll=0)                      # down to the hull and its layer
go(T['f2'] + .2, 2.2, fit(200, 1800, 3780, 4380, at=.42))                               # ride the rays from the sea behind
go(T['f3'] + .3, .8, fit(1100, 2460, 3780, 4380, at=.42), a=1.4, b=3.2)                 # whip with the rays to the eye
go(T['f4'] + .6, 1.4, fit(200, 2460, 3740, 4560, at=.42))                               # the whole picture: the eye sees the sea
go(T['g1'] - .7, 1.5, fit(300, 1300, 4440, 5100, at=.42))                               # the bow end as the bands start
c.to(T['g1'] + .35, 6.6, x=fit(1200, 2200, 4440, 5100)['x'], a=1.6, b=1.6)             # track along the bands, one per sixteenth
go(T['g3'] - .4, 1.2, fit(300, 2220, 4440, 5340, at=.42))                               # pull out: the whole 93 m
go(T['g4'] - .5, 1.4, fit(340, 1960, 5280, 5760, at=.42))                               # down to the power
c.to(T['g5'], .7, y=fit(340, 1960, 5240, 5720, at=.42)['y'], a=1.4, b=3.0)              # rise with the line
go(T['h1'] - .5, 1.3, fit(200, 1380, 5780, 6000, at=.45))                               # trial one
go(T['h3'] - .4, 1.0, fit(200, 1900, 5780, 6180, at=.45))                               # trial two, with trial one above
go(T['h5'] - .4, 1.1, fit(200, 2420, 5780, 6360, m=40, at=.45))                         # trial three, the widest
go(T['h6'] + .8, 1.8, fit(1760, 2660, 5260, 5800, at=.42))                              # silence: move to the compass
c.to(T['i1'] + .1, 2.6, z=math.exp(c.cur['lz']) * 1.04, roll=-1.2, a=2, b=2.2)          # slow push, Dutch tilt
go(T['i3'] + 1.2, 1.4, fit(2250, 3450, 5600, 6250, at=.42), roll=0)                     # rise along the leader to the verdict
c.shake(T['j1'] + .35, amp=7, f=8.5, k=6.5, dir=(0, 1), roll=.02)
WALL = dict(x=BW / 2, y=BH / 2, z=min(1080 / BW, 1920 / BH) * .985)
c.to(T['j2'] - .4, 2.6, x=WALL['x'], y=WALL['y'], a=1.5, b=3.2); c.to(T['j2'] - .4, 2.9, z=WALL['z'], a=1.4, b=3.2)   # the only pull-back: the whole wall
c.to(T['j2'] + 2.6, DUR - T['j2'] - 2.6, z=WALL['z'] * 1.02, a=1.6, b=1.2)
ev(T['j2'] - .4, 'reveal')
for t_ in (T['b1'] - .3, T['c1'] - .5, T['d1'] - .45, T['e1'] - .45, T['f1'] - .55, T['f3'] + .3, T['g1'] - .7, T['g3'] - .4, T['g4'] - .5, T['h1'] - .5, T['h5'] - .4, T['i3'] + 1.2, T['j2'] - .4):
    ev(t_, 'whoosh', v=.45)
MB = [dict(t0=T['g1'] + .35, t1=T['g1'] + 7, n=3)]

# ================================================================= subtitles
subs = []
keys = [k for k, _ in ORDER]
for i, k in enumerate(keys):
    t0 = T[k]; d = VO[k]; t1 = t0 + max(1.8, d + .6)
    if i + 1 < len(keys): t1 = min(t1, T[keys[i + 1]] - .02)
    subs.append(dict(t0=round(t0, 3), t1=round(t1, 3), zh='', en=SUBTXT[k], speech=d)); ev(t0, 'vo', id=k)
for s in subs:
    if s['t1'] - s['t0'] < 1.78: print('WARNING short subtitle', s['en'], round(s['t1'] - s['t0'], 2))

scene = dict(dur=DUR, reveal=T['j2'] - .4, board=dict(w=BW, h=BH, seed=23, texScale=.42, ghosts=120), hand=1.0, sheen=.07,
             light=dict(x=-1600, y=-2600, r=19000, min=.8),
             tray=[dict(kind='marker', color='graphite', x=700, rot=-2), dict(kind='marker', color='blue', x=1100, rot=1.5),
                   dict(kind='marker', color='red', x=1450, rot=-1), dict(kind='eraser', x=2500, rot=.5)],
             cam=c.json(), mb=MB, elements=[e for e in E if e], ev=sorted(EV, key=lambda e: e['t']), subs=subs, right_zone=RIGHT_ZONE)
json.dump(scene, open(os.path.join(HERE, 'film.json'), 'w'), indent=1)
json.dump([dict(t0=s['t0'], t1=s['t1'], text=s['en']) for s in subs], open(os.path.join(FILM, 'audio', 'cues.json'), 'w'), indent=1)
json.dump(dict(T=T, DUR=DUR, BPM=BPM, reveal=T['j2'] - .4, sil=[[END('h6') + .2, T['i1'] - .05]]), open(os.path.join(FILM, 'audio', 'timeline.json'), 'w'), indent=1)
print('film.json', DUR, 's ·', len(E), 'elements ·', len(EV), 'events ·', len(subs), 'subtitles')
for k in ('a1', 'b1', 'c1', 'd1', 'e1', 'f1', 'g1', 'h1', 'i1', 'j1', 'j3'): print(' ', k, T[k])
