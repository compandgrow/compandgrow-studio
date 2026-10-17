#!/usr/bin/env python3
"""LONGSHOT — the whole film as data -> scenes/film.json, audio/cues.json, audio/timeline.json."""
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

# ================================================================= LONGSHOT — narration timeline
ORDER = [('a1', .25), ('a2', .1), ('a3', .1),
         ('b1', .5), ('b2', .1), ('b3', .05), ('b4', .05), ('b5', .05),
         ('c1', .5), ('c2', .05), ('c3', .3),
         ('d1', .5), ('d2', .15), ('d3', .3),
         ('e2', .6), ('e3', .05), ('e4', .25), ('e5', .5), ('e6', .1),
         ('f1', .6), ('f2', .3), ('f3', .1), ('f4', .3), ('f5', .05), ('f6', .3),
         ('g1', .5),
         ('h1', .6), ('h2', .35), ('h3', .4), ('h4', .35), ('h5', .4), ('h6', .35),
         ('i1', 1.6), ('i2', .2), ('i3', .05),
         ('j1', .8), ('j2', .7), ('j3', .4)]
T = {}; t = 0.0; prev_end = 0.0
for k, gap in ORDER:
    t0 = max(prev_end + gap, t); t0 = round(math.ceil(t0 / SIX - 1e-9) * SIX, 4)
    T[k] = t0; d = VO[k]; t = t0 + max(1.8, d + .6); prev_end = t0 + d
END = lambda k: T[k] + VO[k]
DUR = round(END('j3') + 3.6, 3)

def eye(c, w, t0, idp, col='graphite'):
    cx, cy = c; up = [[cx - w / 2 + w * u, cy - math.sin(u * math.pi) * w * .32] for u in [i / 16 for i in range(17)]]
    dn = [[cx - w / 2 + w * u, cy + math.sin(u * math.pi) * w * .26] for u in [i / 16 for i in range(17)]]
    el(type='ink', kind='line', id=idp + '_u', points=R(up), lw=10, color=col, t=t0, d=.25)
    el(type='ink', kind='line', id=idp + '_d', points=R(dn), lw=10, color=col, t=t0 + .12, d=.25)
    el(type='ink', kind='ring', id=idp + '_p', c=[cx, cy - 2], r=w * .16, lw=10, color=col, t=t0 + .3, d=.22)
def plane(cx, cy, s, t0, idp, col='graphite', lw=8, d=.12):
    """a side-view aircraft sketch, nose to the left"""
    L = 200 * s
    parts = [[[cx - L / 2, cy], [cx - L / 2 + 22 * s, cy - 14 * s], [cx + L / 2 - 20 * s, cy - 14 * s], [cx + L / 2, cy - 48 * s], [cx + L / 2 + 6 * s, cy + 2 * s], [cx - L / 2 + 18 * s, cy + 12 * s], [cx - L / 2, cy]],
             [[cx - 10 * s, cy - 6 * s], [cx + 30 * s, cy + 46 * s], [cx + 52 * s, cy + 46 * s], [cx + 34 * s, cy - 6 * s]],
             [[cx + L / 2 - 30 * s, cy - 6 * s], [cx + L / 2 - 10 * s, cy + 18 * s]]]
    for i, p in enumerate(parts):
        el(type='ink', kind='line', id=f'{idp}_{i}', points=R(p), lw=lw, color=col, t=round(t0 + i * d * .8, 3), d=d)
def tower(x, base, h, t0, idp):
    """the emitter: a lattice mast with a dish on top"""
    w0, w1 = 150, 60
    legs = [[[x - w0, base], [x - w1, base - h]], [[x + w0, base], [x + w1, base - h]]]
    for i, p in enumerate(legs): el(type='ink', kind='line', id=f'{idp}_l{i}', points=R(p), lw=11, color='graphite', t=round(t0 + i * .1, 3), d=.3)
    bra = []
    for k in range(5):
        y0 = base - h * k / 5; y1 = base - h * (k + 1) / 5
        xa = lambda y: x - (w0 + (w1 - w0) * (base - y) / h); xb = lambda y: x + (w0 + (w1 - w0) * (base - y) / h)
        bra.append(dict(points=R([[xa(y0), y0], [xb(y1), y1]]), t=round(t0 + .4 + k * .06, 3), d=.08, lw=6, color='grey'))
        bra.append(dict(points=R([[xb(y0), y0], [xa(y1), y1]]), t=round(t0 + .43 + k * .06, 3), d=.08, lw=6, color='grey'))
    el(type='ink', kind='hatch', id=f'{idp}_br', strokes=bra, lw=6, color='grey', alpha=.85)
    dish = [[x - 120 + 240 * u, base - h - 30 - 70 * math.sin(u * math.pi)] for u in [i / 16 for i in range(17)]]
    el(type='ink', kind='line', id=f'{idp}_dish', points=R(dish), lw=11, color='graphite', t=round(t0 + .8, 3), d=.25)
    el(type='ink', kind='line', id=f'{idp}_mast', points=[[x, base - h], [x, base - h - 60]], lw=9, color='graphite', t=round(t0 + .75, 3), d=.08)
    return (x + 125, base - h - 60)

# ================================================================= S1 hook: 250 miles, 10,000 aircraft, one beam (y 250-1050)
el(type='ink', kind='dim', id='dim250', **{'from': [330, 520], 'to': [2380, 520]}, lw=13, color='blue', t=-.05, d=.45, ea=1.2, eb=2.4)
ev(0, 'dimzip', d=.45, v=1.0); ev(.45, 'arrow', v=1.0)
el(type='ink', kind='write', id='w250', text='250 miles', xy=[1355, 450], size=150, color='blue', align='center', t=snap(T['a1'] + .2), d=.5)
ev(T['a1'] + .2, 'ink', d=.5, kind='write', v=.9)
for i in range(10):
    plane(470 + i * 200, 770 + (i % 2) * 70, .62, round(T['a2'] + .05 + i * SIX, 3), f'pl{i}', lw=6, d=.06)
    ev(T['a2'] + .05 + i * SIX, 'tick', v=.35)
el(type='ink', kind='write', id='w10k', text='× 1,000 each', xy=[1355, 1000], size=78, color='grey', align='center', t=snap(T['a2'] + 1.0), d=.4)
el(type='tag', id='tag_q', text='250 MI?', xy=[1880, 260], size=92, rot=-3, magnetColor='red', arrive=dict(t=snap(T['a3'] + .1), kind='swing', d=.8, amp=10),
   strike=dict(t=round(T['j3'] + .05, 3), d=.25, color='red'))
ev(T['a3'] + .1, 'tag', v=.9)

# ================================================================= S2 1934 (y 1200-1950)
el(type='ink', kind='write', id='w1934', text='July 11, 1934', xy=[330, 1330], size=130, color='graphite', t=snap(T['b1']), d=.6)
ev(T['b1'], 'ink', d=.6, kind='write', v=.9)
el(type='card', id='paper', xy=[1250, 1640], w=1700, h=380, rot=-1.4, z=8, magnetR=22, magnets=[[-780, -150, 'graphite'], [780, -150, 'graphite']],
   arrive=dict(t=round(snap(T['b3']) - .3, 3), kind='drop', d=.3, lift=220, land=.9),
   lines=[dict(text='NEWSPAPER · JULY 11, 1934', font='mono', weight=600, size=46, x=60, y=-90, color='grey', track=2),
          dict(text='"TESLA, AT 78,', font='sans', weight=900, size=104, x=60, y=30, color='graphite', track=1),
          dict(text='BARES NEW \'DEATH-BEAM\'"', font='sans', weight=900, size=104, x=60, y=140, color='graphite', track=1)])
ev(T['b3'], 'land', size='mid', v=.8); ev(T['b3'] + .12, 'pin', v=.5); ev(T['b3'] + .25, 'pin', v=.5)
el(type='tag', id='tag_78', text='AGE 78', xy=[1830, 1290], size=74, rot=2, arrive=dict(t=snap(T['b2'] + .3), kind='swing', d=.8, amp=8))
ev(T['b2'] + .3, 'tag', v=.6)
el(type='ink', kind='ring', id='ring250', c=[1255, 450 - 50], r=[330, 105], lw=10, color='red', t=snap(T['b5'] + .2), d=.4)   # back up to the hook's number (seen in the reveal)

# ================================================================= S3 1937: six governments (y 2050-2550)
el(type='ink', kind='write', id='w1937', text='1937', xy=[330, 2170], size=150, color='graphite', t=snap(T['c1']), d=.4)
el(type='ink', kind='write', id='w_plans', text='plans sent to:', xy=[800, 2170], size=96, color='grey', t=snap(T['c1'] + .6), d=.5)
ev(T['c1'], 'ink', d=.4, kind='write', v=.9); ev(T['c1'] + .6, 'ink', d=.5, kind='write', v=.6)
GOV = ['U.S.', 'CANADA', 'BRITAIN', 'FRANCE', 'U.S.S.R.', 'YUGOSLAVIA']
for i, g in enumerate(GOV):
    x = 380 + (i % 3) * 720; y = 2330 + (i // 3) * 170; tg = round(snap(T['c2']) + i * BEAT / 2, 4)
    el(type='tag', id=f'gov{i}', text=g, xy=[x, y], size=70, rot=(-2, 1.5, -1, 2, -1.5, 1)[i], arrive=dict(t=tg, kind='snap', d=.5, amp=6))
    ev(tg, 'tag', v=.55)
el(type='ink', kind='write', id='w_noBeam', text='no working beam shown', xy=[380, 2720], size=84, color='red', t=snap(T['c3'] + .2), d=.7)
ev(T['c3'] + .2, 'ink', d=.7, kind='write', v=.7)

# ================================================================= S4 1943 review (y 2850-3300)
el(type='ink', kind='write', id='w1943', text='Jan 1943', xy=[330, 2960], size=130, color='graphite', t=snap(T['d1']), d=.5)
ev(T['d1'], 'ink', d=.5, kind='write', v=.9)
el(type='card', id='review', xy=[1500, 3140], w=1100, h=300, rot=1.2, z=8, magnetR=20, magnets=[[-500, -120, 'graphite'], [500, -120, 'graphite']],
   arrive=dict(t=round(snap(T['d2']) - .3, 3), kind='drop', d=.3, lift=200, land=.9),
   lines=[dict(text='PAPERS SEIZED · REVIEWED', font='mono', weight=600, size=50, x=60, y=-40, color='graphite', track=2),
          dict(text='finding:', font='marker', size=70, x=60, y=70, color='grey')])
ev(T['d2'], 'land', size='mid', v=.8); ev(T['d2'] + .12, 'pin', v=.5); ev(T['d2'] + .25, 'pin', v=.5)
el(type='stamp', id='st_nw', text='NOTHING WORKABLE', xy=[1500, 3345], size=72, rot=-4, t=snap(T['d3'] + .55), seed=5)
ev(T['d3'] + .55, 'stamp', v=.8)

# ================================================================= S5 the principle: accelerator works, air scatters (y 3450-4050)
TY = 3700
tube = [[300, TY - 90], [1250, TY - 90], [1250, TY + 90], [300, TY + 90], [300, TY - 90]]
el(type='ink', kind='line', id='tube', points=tube, lw=12, color='graphite', t=snap(T['e2'] - .3), d=.6)
for i, x in enumerate((420, 640, 860, 1080)):
    el(type='ink', kind='line', id=f'ring{i}', points=[[x, TY - 120], [x, TY + 120]], lw=9, color='graphite', t=round(T['e2'] + .2 + i * .1, 3), d=.12)
ev(T['e2'] - .3, 'ink', d=.9, kind='line', v=.7)
el(type='ink', kind='write', id='w_vac', text='vacuum', xy=[320, TY + 190], size=74, color='grey', t=snap(T['e2'] + .6), d=.3)
el(type='ink', kind='line', id='beam_in', points=[[330, TY], [1250, TY]], lw=11, color='blue', arrow=True, t=snap(T['e3']), d=.6, ea=1.2, eb=2.4)
ev(T['e3'], 'dimzip', d=.6, v=.8)
el(type='ink', kind='write', id='w_c', text='≈ light speed', xy=[760, TY + 190], size=72, color='blue', t=snap(T['e3'] + .9), d=.4)
el(type='tag', id='tag_acc', text='EVERY ACCELERATOR', xy=[360, 3470], size=66, rot=-1.5, arrive=dict(t=snap(T['e4']), kind='swing', d=.8, amp=8))
ev(T['e4'], 'tag', v=.6)
fan = []
for k, a in enumerate((-.32, -.16, 0, .16, .32)):
    L = 900; fan.append(dict(points=R([[1260, TY], [1260 + L * math.cos(a), TY + L * math.sin(a) * 1.4]]), t=round(T['e6'] + .1 + k * .07, 3), d=.35, lw=8, color='grey'))
el(type='ink', kind='hatch', id='fan', strokes=fan, lw=8, color='grey', alpha=.85)
ev(T['e6'] + .1, 'scribble', d=.7, v=.5)
el(type='ink', kind='write', id='w_air', text='air', xy=[1760, TY - 200], size=110, color='graphite', t=snap(T['e5'] + .1), d=.3)
el(type='ink', kind='write', id='w_scat', text='scatters', xy=[1900, TY + 120], size=84, color='red', t=snap(T['e6'] + .8), d=.5)
ev(T['e5'] + .1, 'ink', d=.3, kind='write'); ev(T['e6'] + .8, 'ink', d=.5, kind='write', v=.7)

# ================================================================= S6 the leap: pulse-bored channel (y 4200-4900)
BY = 4560; TX0 = 520
tip = tower(TX0, 4880, 420, round(snap(T['f1']) - .2, 3), 'tw')
ev(T['f1'] - .2, 'ink', d=1.1, kind='line', v=.7)
el(type='ink', kind='write', id='w_long', text='LONGSHOT', xy=[260, 4230], size=120, color='graphite', t=snap(T['f1'] + .5), d=.5)
ev(T['f1'] + .5, 'ink', d=.5, kind='write', v=.9)
CH0, CH1 = tip[0] + 20, 2150
el(type='ink', kind='line', id='chanA', points=[[CH0, tip[1] - 34], [CH1, tip[1] - 34]], lw=7, color='blue', dash=[22, 16], t=snap(T['f2'] + .3), d=1.0, ea=1.4, eb=2.2)
el(type='ink', kind='line', id='chanB', points=[[CH0, tip[1] + 34], [CH1, tip[1] + 34]], lw=7, color='blue', dash=[22, 16], t=snap(T['f2'] + .45), d=1.0, ea=1.4, eb=2.2)
ev(T['f2'] + .3, 'dimzip', d=1.1, v=.5)
el(type='ink', kind='write', id='w_hot', text='heated channel', xy=[1150, tip[1] - 90], size=70, color='blue', t=snap(T['f3']), d=.45)
pulses = []
for k in range(9):
    x0 = CH0 + 40 + k * 205; tp = round(T['f4'] + .2 + k * SIX * 2, 3)
    pulses.append(dict(points=R([[x0, tip[1]], [x0 + 150, tip[1]]]), t=tp, d=.1, lw=14, color='blue'))
el(type='ink', kind='hatch', id='pulses', strokes=pulses, lw=14, color='blue', alpha=1)
for k in range(9): ev(T['f4'] + .2 + k * SIX * 2, 'tick', v=.45)
el(type='ink', kind='line', id='beam_tight', points=[[CH0, tip[1]], [CH1 + 20, tip[1]]], lw=9, color='blue', arrow=True, t=snap(T['f6'] + .1), d=.6, ea=1.3, eb=2.6)
ev(T['f6'] + .1, 'dimzip', d=.6, v=1.0); ev(T['f6'] + .7, 'arrow', v=1.0)
el(type='ink', kind='dim', id='dim4cm', **{'from': [CH1 + 110, tip[1] - 34], 'to': [CH1 + 110, tip[1] + 34]}, lw=8, color='blue', t=snap(T['g1'] + .2), d=.3)
el(type='ink', kind='write', id='w4cm', text='4 cm', xy=[CH1 + 160, tip[1] + 30], size=96, color='blue', t=snap(T['g1'] + .5), d=.3)
ev(T['g1'] + .2, 'arrow', v=.8); ev(T['g1'] + .5, 'ink', d=.3, kind='write', v=.7)

# ================================================================= S7 trials: 50 / 200 / 400 km (y 5050-5600)
TR = [('h1', 'h2', '50 km', 420), ('h3', 'h4', '200 km', 980), ('h5', 'h6', '400 km', 1640)]
TRY = [5130, 5320, 5510]
for i, ((la, lb, txt, L), y) in enumerate(zip(TR, TRY)):
    tl = snap(T[la] + .15)
    el(type='ink', kind='line', id=f'mast{i}', points=[[300, y + 50], [300, y - 40]], lw=10, color='graphite', t=round(tl - .3, 3), d=.15)
    el(type='ink', kind='dim', id=f'dimT{i}', **{'from': [330, y], 'to': [330 + L, y]}, lw=10, color='blue', t=tl, d=.45 + .15 * i, ea=1.4, eb=2.6)
    ev(tl, 'dimzip', d=.45 + .15 * i, v=.6 + .15 * i); ev(tl + .45 + .15 * i, 'arrow', v=.8)
    el(type='ink', kind='write', id=f'wT{i}', text=txt, xy=[330 + L / 2, y - 30], size=80, color='blue', align='center', t=round(tl + .3, 3), d=.3)
    plane(330 + L + 150, y - 10, .55, round(tl + .2, 3), f'tp{i}', lw=7, d=.08)
    ts = snap(T[lb] - .02)
    el(type='stamp', id=f'stampT{i}', text='DOWN', xy=[330 + L + 420, y - 6], size=76, rot=(-6, 4, -3)[i], t=ts, seed=11 + i)
    ev(ts, 'stamp', v=.8 + .1 * i)

# ================================================================= S8 side effect: thunderclap and dead radios (y 5750-6150)
BOLT = [[400, 5720], [330, 5860], [420, 5860], [340, 6020]]
el(type='ink', kind='line', id='bolt', points=BOLT, lw=12, color='graphite', t=snap(T['i2'] + .1), d=.25)
ev(T['i2'] + .1, 'thunder', v=1.0)
el(type='ink', kind='write', id='w_clap', text='thunderclap', xy=[520, 5900], size=84, color='graphite', t=snap(T['i2'] + .5), d=.5)
RX = 1450
el(type='ink', kind='line', id='radio', points=[[RX, 5860], [RX + 300, 5860], [RX + 300, 6040], [RX, 6040], [RX, 5860]], lw=10, color='graphite', t=snap(T['i3'] - .1), d=.35)
el(type='ink', kind='line', id='radio_ant', points=[[RX + 60, 5860], [RX + 10, 5740]], lw=8, color='graphite', t=round(T['i3'] + .2, 3), d=.1)
el(type='ink', kind='ring', id='radio_dial', c=[RX + 210, 5950], r=50, lw=8, color='graphite', t=round(T['i3'] + .3, 3), d=.15)
el(type='ink', kind='line', id='radio_x1', points=[[RX - 30, 5800], [RX + 330, 6080]], lw=13, color='red', t=snap(T['i3'] + .7), d=.16)
el(type='ink', kind='line', id='radio_x2', points=[[RX + 330, 5800], [RX - 30, 6080]], lw=13, color='red', t=round(snap(T['i3'] + .7) + .2, 3), d=.16)
el(type='ink', kind='write', id='w_10km', text='< 10 km', xy=[RX + 380, 5990], size=80, color='blue', t=snap(T['i3'] + 1.0), d=.3)
ev(T['i3'] - .1, 'ink', d=.5, kind='line', v=.6); ev(T['i3'] + .7, 'ink', d=.4, kind='line', v=.9)

# ================================================================= right zone (seen in the reveal)
VER = (3150, 5600)
el(type='stamp', id='stamp_cleared', text='CLEARED', xy=[VER[0], VER[1] - 130], size=150, rot=-7, t=snap(T['j1'] + .35), seed=31)
el(type='ink', kind='write', id='w_field', text='for field trials', xy=[VER[0], VER[1] + 90], size=92, color='graphite', align='center', t=snap(T['j1'] + .8), d=.6)
ev(T['j1'] + .35, 'stamp', v=1.0, big=1); ev(T['j1'] + .8, 'ink', d=.6, kind='write', v=.7)
el(type='ink', kind='line', id='leader', points=[[2380, 5560], [2620, 5520], [2800, 5480]], lw=10, color='graphite', arrow=True, t=snap(T['j1'] - .2), d=.5)
el(type='card', id='title', xy=[3120, 320], w=820, h=440, rot=.6, z=8, magnetR=24, magnets=[[-350, -170, 'red'], [350, -170, 'graphite']],
   lines=[dict(text='LONGSHOT', font='sans', weight=900, size=136, x=56, y=0, color='graphite', track=3),
          dict(rule=True, x=58, y=40, w=160, h=10, color='red'),
          dict(text='DIRECTED BEAM STUDY', font='mono', weight=600, size=46, x=58, y=120, color='graphite', track=2),
          dict(text='AFTER TESLA, 1937', font='mono', weight=500, size=42, x=58, y=180, color='grey', track=2)])
el(type='card', id='note_mi', xy=[3100, 1200], w=720, h=280, rot=3, z=7, magnetR=18, magnets=[[0, -110, 'blue']],
   lines=[dict(rule=True, x=30, y=-55, w=660, h=3, color='blue'), dict(text='250 mi ≈ 402 km', font='marker', size=76, x=40, y=30, color='blue'),
          dict(text='Tesla\'s number', font='marker', size=60, x=40, y=105, color='graphite')])
el(type='card', id='spec', xy=[3120, 2900], w=820, h=560, rot=-.8, z=7, magnetR=20, magnets=[[-360, -240, 'graphite'], [360, -240, 'graphite']],
   lines=[dict(text='SPEC SHEET', font='mono', weight=600, size=60, x=48, y=-160, color='graphite', track=2),
          dict(text='Mode      pulsed', font='mono', weight=500, size=52, x=48, y=-70, color='graphite'),
          dict(text='Channel   heated air', font='mono', weight=500, size=52, x=48, y=0, color='graphite'),
          dict(text='Spot      4 cm', font='mono', weight=500, size=52, x=48, y=70, color='graphite'),
          dict(text='Reach     400 km', font='mono', weight=500, size=52, x=48, y=140, color='graphite'),
          dict(text='Mast      1 tower', font='mono', weight=500, size=52, x=48, y=210, color='graphite')])
el(type='card', id='note_air', xy=[3080, 4300], w=720, h=280, rot=-2.5, z=7, magnetR=18, magnets=[[0, -110, 'blue']],
   lines=[dict(rule=True, x=30, y=-55, w=660, h=3, color='blue'), dict(text='1934: air seal', font='marker', size=70, x=40, y=30, color='graphite'),
          dict(text='now: air channel', font='marker', size=70, x=40, y=110, color='blue')])
el(type='tag', id='tag_a', text='400 KM', xy=[1880, 420], size=92, rot=2.5, magnetColor='red', arrive=dict(t=snap(T['j3'] + .1), kind='swing', d=.9, amp=12))
ev(T['j3'] + .1, 'tag', v=1.0); ev(T['j3'] + .05, 'strike', v=.8)

# ================================================================= camera
def fit(x0, x1, y0, y1, m=70, at=.40, zmax=1.4):
    w, h = x1 - x0 + 2 * m, y1 - y0 + 2 * m
    z = min(1080 / w, 1500 / h, zmax); Hv = 1920 / z
    return dict(x=(x0 + x1) / 2, y=(y0 + y1) / 2 + (.5 - at) * Hv, z=round(z, 4))
def go(t, d, f, a=2, b=2.6, roll=None): return c.to(t, d, x=f['x'], y=f['y'], z=f['z'], roll=roll, a=a, b=b)
F0 = fit(300, 2420, 220, 1060, at=.42)
c = Cam(F0['x'] - 500, F0['y'], F0['z'] * 1.6, roll=-2.0)
c.to(0, .6, x=F0['x'] + 60, a=1.4, b=2.8); c.to(0, 1.1, z=F0['z'], roll=0, a=1.6, b=2.8)    # whip with the snapping 250-mile line
c.to(.6, .7, x=F0['x'], a=2, b=2.4)
go(T['b1'] - .4, 1.6, fit(300, 2300, 1180, 1880, at=.42))                                   # down to 1934
go(T['c1'] - .4, 1.5, fit(300, 2500, 2020, 2780, at=.42))                                   # 1937: six governments
go(T['d1'] - .4, 1.5, fit(300, 2100, 2860, 3480, at=.42))                                    # 1943: the review
c.to(T['d3'], 1.4, z=math.exp(c.cur['lz']) * 1.03, roll=-1.0, a=2, b=2.2)                  # push on "nothing workable"
go(T['e2'] - .5, 1.5, fit(280, 1400, 3420, 3950, at=.42), roll=0)                          # the tube
go(T['e5'] - .2, 1.4, fit(280, 2400, 3380, 4050, at=.42))                                   # out into the air
go(T['f1'] - .5, 1.6, fit(240, 1500, 4180, 4900, at=.42))                                   # the tower
go(T['f4'] + .1, 2.6, fit(700, 2300, 4180, 4900, at=.42))                                   # ride the pulses
go(T['f6'], .9, fit(1150, 2620, 4300, 4800, at=.42), a=1.4, b=3.2)                          # whip with the tight beam
go(T['g1'] + VO['g1'] + .4, 1.2, fit(240, 2600, 4180, 4900, at=.42))                                   # the whole channel
go(T['h1'] - .5, 1.3, fit(280, 1400, 5040, 5200, at=.45))                                    # trial one
go(T['h3'] - .4, 1.0, fit(280, 1900, 5040, 5390, at=.45))
go(T['h5'] - .4, 1.1, fit(280, 2600, 5040, 5580, m=50, at=.45))
go(T['h6'] + .8, 1.8, fit(220, 2100, 5680, 6100, at=.42))                                    # silence: the side effect
c.to(T['i1'] + .1, 2.6, z=math.exp(c.cur['lz']) * 1.0, roll=-1.0, a=2, b=2.2)
go(T['i3'] + 1.4, 1.4, fit(2300, 3500, 5300, 5850, at=.42), roll=0)                         # to the verdict
c.shake(T['j1'] + .35, amp=7, f=8.5, k=6.5, dir=(0, 1), roll=.02)
WALL = dict(x=BW / 2, y=BH / 2, z=min(1080 / BW, 1920 / BH) * .985)
c.to(T['j2'] - .4, 2.6, x=WALL['x'], y=WALL['y'], a=1.5, b=3.2); c.to(T['j2'] - .4, 2.9, z=WALL['z'], a=1.4, b=3.2)
c.to(T['j2'] + 2.6, DUR - T['j2'] - 2.6, z=WALL['z'] * 1.02, a=1.6, b=1.2)
ev(T['j2'] - .4, 'reveal')
for t_ in (T['b1'] - .4, T['c1'] - .4, T['d1'] - .4, T['e2'] - .5, T['e5'] - .2, T['f1'] - .5, T['f6'], T['h1'] - .5, T['h5'] - .4, T['i3'] + 1.4, T['j2'] - .4):
    ev(t_, 'whoosh', v=.45)
MB = []

# ================================================================= subtitles and output
subs = []; keys = [k for k, _ in ORDER]
for i, k in enumerate(keys):
    t0 = T[k]; d = VO[k]; t1 = t0 + max(1.8, d + .6)
    if i + 1 < len(keys): t1 = min(t1, T[keys[i + 1]] - .02)
    subs.append(dict(t0=round(t0, 3), t1=round(t1, 3), zh='', en=SUBTXT[k], speech=d)); ev(t0, 'vo', id=k)
for s in subs:
    if s['t1'] - s['t0'] < 1.78: print('WARNING short subtitle', s['en'], round(s['t1'] - s['t0'], 2))
scene = dict(dur=DUR, reveal=T['j2'] - .4, board=dict(w=BW, h=BH, seed=37, texScale=.42, ghosts=120), hand=1.0, sheen=.07,
             light=dict(x=-1600, y=-2600, r=19000, min=.8),
             tray=[dict(kind='marker', color='graphite', x=700, rot=-2), dict(kind='marker', color='blue', x=1100, rot=1.5),
                   dict(kind='marker', color='red', x=1450, rot=-1), dict(kind='eraser', x=2500, rot=.5)],
             cam=c.json(), mb=MB, elements=E, ev=sorted(EV, key=lambda e: e['t']), subs=subs, right_zone=RIGHT_ZONE)
json.dump(scene, open(os.path.join(HERE, 'film.json'), 'w'), indent=1)
json.dump([dict(t0=s['t0'], t1=s['t1'], text=s['en']) for s in subs], open(os.path.join(FILM, 'audio', 'cues.json'), 'w'), indent=1)
json.dump(dict(T=T, DUR=DUR, BPM=BPM, reveal=T['j2'] - .4, sil=[[END('h6') + .2, T['i1'] - .05]]), open(os.path.join(FILM, 'audio', 'timeline.json'), 'w'), indent=1)
print('film.json', DUR, 's ·', len(E), 'elements ·', len(EV), 'events ·', len(subs), 'subtitles')
