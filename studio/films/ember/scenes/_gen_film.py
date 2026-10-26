#!/usr/bin/env python3
"""EMBER — the whole film as data -> scenes/film.json, audio/cues.json, audio/timeline.json."""
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

# ================================================================= EMBER — narration timeline
ORDER = [('a1', .25), ('a2', .1), ('a3', .1),
         ('b1', .6), ('b2', .1), ('b3', .05),
         ('c1', .6), ('c2', .1), ('c3', .05), ('c4', .05), ('c5', .2),
         ('d1', .6), ('d2', .2), ('d3', .3),
         ('e1', .6), ('e2', .2), ('e3', .05), ('e4', .3), ('e5', .1),
         ('f1', .6), ('f2', .3), ('f3', .3), ('f4', .2), ('f5', .2),
         ('h1', .6), ('h2', .35), ('h3', .4), ('h4', .35), ('h5', .4), ('h6', .35),
         ('i1', 1.6), ('i2', .2),
         ('j1', .8), ('j2', .7), ('j3', .4)]
T = {}; t = 0.0; prev_end = 0.0
for k, gap in ORDER:
    t0 = max(prev_end + gap, t); t0 = round(math.ceil(t0 / SIX - 1e-9) * SIX, 4)
    T[k] = t0; d = VO[k]; t = t0 + max(1.8, d + .6); prev_end = t0 + d
END = lambda k: T[k] + VO[k]
DUR = round(END('j3') + 3.6, 3)

def circ(cx, cy, r, n=40, a0=0.0, a1=2 * math.pi):
    return R([[cx + r * math.cos(a0 + (a1 - a0) * i / n), cy + r * math.sin(a0 + (a1 - a0) * i / n)] for i in range(n + 1)])
def ball(cx, cy, r, t0, idp, col='red', rays=8, lw=10):
    """ball lightning: a circle, an inner ring, short rays"""
    el(type='ink', kind='line', id=idp + '_o', points=circ(cx, cy, r), lw=lw, color=col, t=t0, d=.45)
    el(type='ink', kind='line', id=idp + '_i', points=circ(cx, cy, r * .55, 28), lw=max(4, lw - 4), color='blue', t=round(t0 + .4, 3), d=.3)
    st = []
    for k in range(rays):
        a = 2 * math.pi * k / rays + .3
        st.append(dict(points=R([[cx + r * 1.18 * math.cos(a), cy + r * 1.18 * math.sin(a)], [cx + r * 1.45 * math.cos(a), cy + r * 1.45 * math.sin(a)]]),
                       t=round(t0 + .7 + k * .04, 3), d=.06, lw=max(4, lw - 3), color=col))
    el(type='ink', kind='hatch', id=idp + '_r', strokes=st, lw=max(4, lw - 3), color=col, alpha=.9)

# ================================================================= S1 hook: a ball of fire (y 200-1100)
ball(1150, 700, 230, -.6, 'b0')
ev(-.3, 'ink', d=.9, kind='line', v=.7)
el(type='ink', kind='write', id='w_fire', text='ball of fire', xy=[440, 1130], size=110, color='graphite', t=snap(T['a1'] + .3), d=.5)
ev(T['a1'] + .3, 'ink', d=.5, kind='write', v=.9)
el(type='ink', kind='line', id='drift', points=R([[1520, 900], [1680, 850], [1840, 890], [1980, 820]]), lw=7, color='grey', dash=[16, 12], arrow=True, t=snap(T['a2']), d=.5)
el(type='ink', kind='write', id='w_1s', text='~1 s', xy=[1640, 1060], size=100, color='blue', t=snap(T['a2'] + .4), d=.3)
ev(T['a2'], 'dimzip', d=.5, v=.7)
el(type='stamp', id='st_hook', text='GONE', xy=[1150, 700], size=120, rot=-8, t=snap(T['a3']), seed=3)
ev(T['a3'], 'stamp', v=.9)
el(type='tag', id='tag_q', text='1 SECOND?', xy=[1300, 210], size=92, rot=-3, magnetColor='red', arrive=dict(t=snap(T['a3'] + .5), kind='swing', d=.8, amp=10),
   strike=dict(t=round(T['j3'] + .05, 3), d=.25, color='red'))
ev(T['a3'] + .5, 'tag', v=.8)

# ================================================================= S2 1638 Dartmoor church (y 1250-1900)
el(type='ink', kind='write', id='w1638', text='1638', xy=[330, 1360], size=150, color='graphite', t=snap(T['b1']), d=.4)
el(type='tag', id='tag_dm', text='DARTMOOR', xy=[880, 1310], size=74, rot=2, arrive=dict(t=snap(T['b1'] + 1.4), kind='swing', d=.8, amp=8))
ev(T['b1'], 'ink', d=.4, kind='write', v=.9); ev(T['b1'] + 1.4, 'tag', v=.6)
CX, CB = 620, 1860
el(type='ink', kind='line', id='church', points=R([[CX - 220, CB], [CX - 220, CB - 260], [CX, CB - 400], [CX + 220, CB - 260], [CX + 220, CB]]), lw=10, color='graphite', t=snap(T['b1'] + .6), d=.5)
el(type='ink', kind='line', id='tower_c', points=R([[CX + 220, CB], [CX + 220, CB - 420], [CX + 330, CB - 420], [CX + 330, CB]]), lw=10, color='graphite', t=round(snap(T['b1'] + .6) + .45, 3), d=.3)
el(type='ink', kind='line', id='window', points=R([[CX - 50, CB - 120], [CX - 50, CB - 220], [CX, CB - 270], [CX + 50, CB - 220], [CX + 50, CB - 120], [CX - 50, CB - 120]]), lw=7, color='graphite', t=round(snap(T['b2']), 3), d=.3)
ev(T['b1'] + .6, 'ink', d=.8, kind='line', v=.6)
ball(CX - 300, CB - 520, 60, round(snap(T['b3']), 3), 'b1638', lw=8, rays=6)
el(type='ink', kind='line', id='into', points=R([[CX - 230, CB - 470], [CX - 120, CB - 330], [CX - 60, CB - 230]]), lw=8, color='red', arrow=True, t=round(snap(T['b3']) + .7, 3), d=.3)
ev(T['b3'] + .7, 'arrow', v=.8)
el(type='card', id='quote', xy=[1700, 1640], w=1050, h=340, rot=-1.2, z=8, magnetR=22, magnets=[[-470, -130, 'graphite'], [470, -130, 'graphite']],
   arrive=dict(t=round(snap(T['b2']) + .2, 3), kind='drop', d=.3, lift=220, land=.9),
   lines=[dict(text='WIDECOMBE, 1638', font='mono', weight=600, size=46, x=60, y=-70, color='grey', track=2),
          dict(text='"a great ball of fire"', font='sans', weight=900, size=74, x=60, y=30, color='graphite'),
          dict(text='through the church window', font='marker', size=60, x=60, y=120, color='grey')])
ev(T['b2'] + .5, 'land', size='mid', v=.8); ev(T['b2'] + .62, 'pin', v=.5); ev(T['b2'] + .75, 'pin', v=.5)

# ================================================================= S3 2012 the spectrometer (y 2050-2700)
el(type='ink', kind='write', id='w2012', text='2012', xy=[330, 2160], size=150, color='graphite', t=snap(T['c2']), d=.4)
ev(T['c2'], 'ink', d=.4, kind='write', v=.9)
el(type='tag', id='tag_qh', text='QINGHAI PLATEAU', xy=[1000, 2110], size=70, rot=-2, arrive=dict(t=snap(T['c3'] + .6), kind='swing', d=.8, amp=9))
ev(T['c3'] + .6, 'tag', v=.7)
SX, SY = 560, 2480
el(type='ink', kind='line', id='spec_box', points=R([[SX - 200, SY - 110], [SX + 200, SY - 110], [SX + 200, SY + 110], [SX - 200, SY + 110], [SX - 200, SY - 110]]), lw=10, color='graphite', t=snap(T['c4']), d=.35)
el(type='ink', kind='line', id='spec_lens', points=R([[SX + 200, SY - 60], [SX + 290, SY - 90], [SX + 290, SY + 90], [SX + 200, SY + 60]]), lw=9, color='graphite', t=round(snap(T['c4']) + .35, 3), d=.2)
el(type='ink', kind='line', id='tripod', points=R([[SX - 120, SY + 260], [SX, SY + 110], [SX + 120, SY + 260]]), lw=8, color='grey', t=round(snap(T['c4']) + .5, 3), d=.2)
ev(T['c4'], 'ink', d=.6, kind='line', v=.6)
ball(1950, 2420, 70, round(snap(T['c4']) + .4, 3), 'b2012', lw=8, rays=6)
el(type='ink', kind='dim', id='dim900', **{'from': [SX + 330, SY + 200], 'to': [1880, SY + 200]}, lw=8, color='blue', t=snap(T['c5']), d=.5)
el(type='ink', kind='write', id='w900', text='900 m', xy=[1160, SY + 320], size=90, color='blue', align='center', t=round(snap(T['c5']) + .3, 3), d=.3)
el(type='ink', kind='write', id='w_1s2', text='~1 s', xy=[1870, 2250], size=86, color='red', t=round(snap(T['c5']) + 1.2, 3), d=.3)
ev(T['c5'], 'dimzip', d=.5, v=.7); ev(T['c5'] + 1.2, 'ink', d=.3, kind='write', v=.7)

# ================================================================= S4 the spectrum: Si Fe Ca = soil (y 2800-3350)
AX0, AX1, AY = 330, 1900, 3250
el(type='ink', kind='line', id='axis', points=[[AX0, AY], [AX1, AY]], lw=10, color='graphite', arrow=True, t=snap(T['d1'] - .2), d=.4)
ev(T['d1'] - .2, 'ink', d=.4, kind='line', v=.6)
for i, (x, h, lab) in enumerate([(560, 300, 'Si'), (1020, 230, 'Fe'), (1480, 340, 'Ca')]):
    tk = round(snap(T['d1']) + .5 + i * .6, 3)
    el(type='ink', kind='line', id=f'pk{i}', points=[[x, AY], [x, AY - h]], lw=12, color='red', t=tk, d=.15)
    el(type='ink', kind='write', id=f'wl{i}', text=lab, xy=[x - 40, AY - h - 40], size=84, color='graphite', t=round(tk + .15, 3), d=.25)
    ev(tk, 'tick', v=.6)
el(type='tag', id='tag_soil', text='= SOIL', xy=[2020, 2950], size=92, rot=3, magnetColor='blue', arrive=dict(t=snap(T['d2'] + .1), kind='swing', d=.8, amp=9))
ev(T['d2'] + .1, 'tag', v=.8)
el(type='ink', kind='write', id='w_burn', text='the ground burns in the air', xy=[330, 3360], size=72, color='grey', t=snap(T['d3'] + 1.0), d=.6)
ev(T['d3'] + 1.0, 'ink', d=.6, kind='write', v=.6)

# ================================================================= S5 2007 lab: arc on a silicon wafer (y 3450-4150)
el(type='ink', kind='write', id='w2007', text='2007', xy=[330, 3560], size=140, color='graphite', t=snap(T['e2']), d=.4)
el(type='tag', id='tag_br', text='LAB · BRAZIL', xy=[900, 3510], size=70, rot=2, arrive=dict(t=snap(T['e2'] + .9), kind='swing', d=.8, amp=8))
ev(T['e2'], 'ink', d=.4, kind='write', v=.9); ev(T['e2'] + .9, 'tag', v=.6)
WY = 4020
el(type='ink', kind='line', id='plate', points=[[330, WY + 40], [1300, WY + 40]], lw=16, color='graphite', t=snap(T['e3']), d=.3)
el(type='ink', kind='line', id='wafer', points=R([[480, WY + 30], [480, WY], [1150, WY], [1150, WY + 30]]), lw=9, color='blue', t=round(snap(T['e3']) + .3, 3), d=.3)
el(type='ink', kind='write', id='w_si', text='silicon wafer', xy=[1350, WY + 30], size=64, color='blue', t=round(snap(T['e3']) + .6, 3), d=.4)
el(type='ink', kind='line', id='electrode', points=[[815, WY - 420], [815, WY - 140]], lw=14, color='graphite', t=round(snap(T['e3']) + .5, 3), d=.25)
el(type='ink', kind='line', id='arc', points=R([[815, WY - 140], [790, WY - 110], [840, WY - 80], [795, WY - 50], [830, WY - 20], [815, WY]]), lw=8, color='red', t=round(snap(T['e3']) + 1.1, 3), d=.15)
ev(T['e3'] + .3, 'ink', d=.6, kind='line', v=.6); ev(T['e3'] + 1.1, 'rattle', v=.5)
for i, (x, y, r) in enumerate([(1050, 3800, 46), (1250, 3690, 58), (1480, 3790, 40)]):
    ball(x, y, r, round(snap(T['e4']) + i * .25, 3), f'b07_{i}', lw=7, rays=6)
el(type='ink', kind='write', id='w4cm', text='≤ 4 cm', xy=[1700, 3720], size=84, color='blue', t=snap(T['e4'] + 1.0), d=.3)
el(type='ink', kind='write', id='w8s', text='≤ 8 s', xy=[1700, 3860], size=84, color='red', t=snap(T['e5']), d=.3)
ev(T['e4'] + 1.0, 'ink', d=.3, kind='write', v=.7); ev(T['e5'], 'ink', d=.3, kind='write', v=.8)

# ================================================================= S6 the leap: a magnetic cage (y 4250-4900)
el(type='ink', kind='write', id='w_emb', text='EMBER', xy=[300, 4330], size=130, color='graphite', t=snap(T['f1']), d=.5)
ev(T['f1'], 'ink', d=.5, kind='write', v=.9)
MX, MY = 1250, 4640
ball(MX, MY, 120, snap(T['f2'] + .2), 'bcage', lw=9, rays=8)
for side in (-1, 1):
    x = MX + side * 330
    el(type='ink', kind='line', id=f'coil{side}', points=R([[x - 45, MY - 200], [x + 45, MY - 200], [x + 45, MY + 200], [x - 45, MY + 200], [x - 45, MY - 200]]), lw=10, color='graphite', t=round(snap(T['f4']) + (0 if side < 0 else .3), 3), d=.3)
    el(type='ink', kind='hatch', id=f'wind{side}', strokes=[dict(points=R([[x - 45, MY - 160 + 40 * k], [x + 45, MY - 140 + 40 * k]]), t=round(snap(T['f4']) + .5 + k * .04, 3), d=.05, lw=5, color='blue') for k in range(8)], lw=5, color='blue', alpha=.85)
    el(type='ink', kind='line', id=f'field{side}', points=circ(MX, MY, 230 + 40 * (side > 0), 36, -math.pi / 2.6 if side > 0 else math.pi - math.pi / 2.6, math.pi / 2.6 if side > 0 else math.pi + math.pi / 2.6), lw=6, color='blue', dash=[14, 10], t=round(snap(T['f4']) + .9, 3), d=.4)
ev(T['f4'], 'ink', d=.6, kind='line', v=.6); ev(T['f4'] + .9, 'dimzip', d=.4, v=.5)
el(type='ink', kind='line', id='feed', points=[[400, 4560], [800, 4620]], lw=9, color='graphite', arrow=True, t=snap(T['f3'] + .2), d=.3)
el(type='ink', kind='write', id='w_dust', text='Si dust', xy=[330, 4500], size=72, color='graphite', t=snap(T['f3'] + .4), d=.3)
el(type='ink', kind='line', id='out', points=[[1700, 4640], [2150, 4640]], lw=11, color='red', arrow=True, t=snap(T['f5'] + .2), d=.35)
el(type='ink', kind='write', id='w_pow', text='power', xy=[1760, 4580], size=76, color='red', t=snap(T['f5'] + .5), d=.3)
ev(T['f3'] + .2, 'arrow', v=.7); ev(T['f5'] + .2, 'arrow', v=.9)

# ================================================================= S7 trials: 8 s / 90 s / 6 h (y 5550-6250)
TB = 6050
TRS = [('h1', 'h2', '8 s', 70, 520), ('h3', 'h4', '90 s', 105, 1150), ('h5', 'h6', '6 h', 145, 1830)]
for i, (la, lb, txt, r, x) in enumerate(TRS):
    tl = snap(T[la] + .1)
    ball(x, TB - 160, r, tl, f'tr{i}', lw=9, rays=8)
    el(type='ink', kind='line', id=f'tc{i}', points=R([[x - r - 80, TB - 160 - r - 70], [x - r - 80, TB - 160 + r + 70]]), lw=9, color='graphite', t=round(tl + .3, 3), d=.15)
    el(type='ink', kind='line', id=f'td{i}', points=R([[x + r + 80, TB - 160 - r - 70], [x + r + 80, TB - 160 + r + 70]]), lw=9, color='graphite', t=round(tl + .4, 3), d=.15)
    el(type='ink', kind='write', id=f'wT{i}', text=txt, xy=[x, TB + 120], size=84, color='blue', align='center', t=round(tl + .5, 3), d=.3)
    ts = snap(T[lb] - .02)
    el(type='stamp', id=f'stT{i}', text='HELD', xy=[x, TB - 160], size=76, rot=(-8, 5, -4)[i], t=ts, seed=11 + i)
    ev(tl, 'ink', d=.6, kind='line', v=.6); ev(ts, 'stamp', v=.8 + .1 * i)

# ================================================================= S8 side effect: radio static (right of trials)
GX, GY = 2380, 5700
el(type='ink', kind='line', id='radio', points=R([[GX - 200, GY - 120], [GX + 200, GY - 120], [GX + 200, GY + 150], [GX - 200, GY + 150], [GX - 200, GY - 120]]), lw=10, color='graphite', t=snap(T['i2'] - .2), d=.35)
el(type='ink', kind='line', id='ant', points=[[GX + 120, GY - 120], [GX + 220, GY - 300]], lw=8, color='graphite', t=round(snap(T['i2']) + .15, 3), d=.15)
el(type='ink', kind='line', id='spk', points=circ(GX - 80, GY + 15, 80, 30), lw=8, color='graphite', t=round(snap(T['i2']) + .3, 3), d=.25)
stat = [[GX + 20 + 16 * k, GY - 40 + (35 if k % 2 else -35) * (1 + .3 * math.sin(k))] for k in range(10)]
el(type='ink', kind='line', id='static', points=R(stat), lw=7, color='red', t=snap(T['i2'] + .6), d=.3)
ev(T['i2'] + .6, 'rattle', v=1.0)
el(type='ink', kind='write', id='w_stat', text='static', xy=[GX - 170, GY + 290], size=76, color='blue', t=snap(T['i2'] + 1.1), d=.3)

# ================================================================= right zone (seen in the reveal)
VER = (3150, 5450)
el(type='stamp', id='stamp_cleared', text='CLEARED', xy=[VER[0], VER[1] - 130], size=150, rot=-7, t=snap(T['j1'] + .35), seed=31)
el(type='ink', kind='write', id='w_field', text='for field trials', xy=[VER[0], VER[1] + 80], size=80, color='graphite', align='center', t=snap(T['j1'] + .8), d=.6)
ev(T['j1'] + .35, 'stamp', v=1.0, big=1); ev(T['j1'] + .8, 'ink', d=.6, kind='write', v=.7)
el(type='card', id='title', xy=[3120, 320], w=820, h=440, rot=.6, z=8, magnetR=24, magnets=[[-350, -170, 'red'], [350, -170, 'graphite']],
   lines=[dict(text='EMBER', font='sans', weight=900, size=150, x=56, y=0, color='graphite', track=4),
          dict(rule=True, x=58, y=40, w=160, h=10, color='red'),
          dict(text='CAGED BALL LIGHTNING', font='mono', weight=600, size=46, x=58, y=120, color='graphite', track=2),
          dict(text='POWER CELL PROGRAM', font='mono', weight=500, size=42, x=58, y=180, color='grey', track=2)])
el(type='card', id='spec', xy=[3120, 2900], w=820, h=560, rot=-.8, z=7, magnetR=20, magnets=[[-360, -240, 'graphite'], [360, -240, 'graphite']],
   lines=[dict(text='SPEC SHEET', font='mono', weight=600, size=60, x=48, y=-160, color='graphite', track=2),
          dict(text='Fuel      Si dust', font='mono', weight=500, size=52, x=48, y=-70, color='graphite'),
          dict(text='Cage      magnetic', font='mono', weight=500, size=52, x=48, y=0, color='graphite'),
          dict(text='Output    the glow', font='mono', weight=500, size=52, x=48, y=70, color='graphite'),
          dict(text='Ball      Ø 30 cm', font='mono', weight=500, size=52, x=48, y=140, color='graphite'),
          dict(text='Trials    8 s/90 s/6 h', font='mono', weight=500, size=52, x=48, y=210, color='graphite')])
el(type='card', id='note_r', xy=[3080, 4300], w=720, h=280, rot=-2.5, z=7, magnetR=18, magnets=[[0, -110, 'blue']],
   lines=[dict(rule=True, x=30, y=-55, w=660, h=3, color='blue'), dict(text='storm: 1 second', font='marker', size=64, x=40, y=30, color='blue'),
          dict(text='Ember: all night', font='marker', size=64, x=40, y=110, color='graphite')])
el(type='tag', id='tag_a', text='ALL NIGHT', xy=[1500, 350], size=92, rot=2.5, magnetColor='red', arrive=dict(t=snap(T['j3'] + .1), kind='swing', d=.9, amp=12))
ev(T['j3'] + .1, 'tag', v=1.0); ev(T['j3'] + .05, 'strike', v=.8)

# ================================================================= camera
def fit(x0, x1, y0, y1, m=70, at=.40, zmax=1.4):
    w, h = x1 - x0 + 2 * m, y1 - y0 + 2 * m
    z = min(1080 / w, 1500 / h, zmax); Hv = 1920 / z
    return dict(x=(x0 + x1) / 2, y=(y0 + y1) / 2 + (.5 - at) * Hv, z=round(z, 4))
def go(t, d, f, a=2, b=2.6, roll=None): return c.to(t, d, x=f['x'], y=f['y'], z=f['z'], roll=roll, a=a, b=b)
F0 = dict(x=1250, y=1560, z=.62)
c = Cam(F0['x'], F0['y'] + 300, F0['z'] * 1.5, roll=-2.0)
c.to(0, 1.4, y=F0['y'], z=F0['z'], roll=0, a=1.6, b=2.8)
go(T['b1'] - .4, 1.6, fit(300, 2250, 1250, 1900, at=.42))
go(T['c1'] - .3, 1.5, fit(300, 2100, 2050, 2780, at=.42))
go(T['d1'] - .4, 1.4, fit(300, 2350, 2820, 3400, at=.42))
go(T['e1'] - .2, 1.5, fit(300, 1950, 3450, 4100, at=.42))
go(T['f1'] - .4, 1.5, fit(280, 2250, 4260, 4880, at=.42))
c.to(T['f4'], 3.0, z=math.exp(c.cur['lz']) * 1.05, roll=-1.0, a=2, b=2.2)
go(T['h1'] - .5, 1.3, fit(280, 800, 5650, 6200, at=.45), roll=0)
go(T['h3'] - .4, 1.0, fit(280, 1400, 5650, 6200, at=.45))
go(T['h5'] - .4, 1.1, fit(280, 2100, 5580, 6200, m=50, at=.45))
go(T['h6'] + .8, 1.8, fit(1850, 2650, 5440, 6060, at=.42, zmax=1.0))
c.to(T['i1'] + .1, 2.4, z=math.exp(c.cur['lz']) * 1.0, roll=-1.0, a=2, b=2.2)
go(T['i2'] + 1.6, 1.4, fit(2350, 3550, 5250, 5600, at=.42), roll=0)
c.shake(T['j1'] + .35, amp=7, f=8.5, k=6.5, dir=(0, 1), roll=.02)
WALL = dict(x=BW / 2, y=BH / 2, z=min(1080 / BW, 1920 / BH) * .985)
c.to(T['j2'] - .4, 2.6, x=WALL['x'], y=WALL['y'], a=1.5, b=3.2); c.to(T['j2'] - .4, 2.9, z=WALL['z'], a=1.4, b=3.2)
c.to(T['j2'] + 2.6, DUR - T['j2'] - 2.6, z=WALL['z'] * 1.02, a=1.6, b=1.2)
ev(T['j2'] - .4, 'reveal')
for t_ in (T['b1'] - .4, T['c1'] - .3, T['d1'] - .4, T['e1'] - .2, T['f1'] - .4, T['h1'] - .5, T['h5'] - .4, T['i2'] + 1.6, T['j2'] - .4):
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
scene = dict(dur=DUR, reveal=T['j2'] - .4, board=dict(w=BW, h=BH, seed=53, texScale=.42, ghosts=120), hand=1.0, sheen=.07,
             light=dict(x=-1600, y=-2600, r=19000, min=.8),
             tray=[dict(kind='marker', color='graphite', x=700, rot=-2), dict(kind='marker', color='blue', x=1100, rot=1.5),
                   dict(kind='marker', color='red', x=1450, rot=-1), dict(kind='eraser', x=2500, rot=.5)],
             cam=c.json(), mb=MB, elements=E, ev=sorted(EV, key=lambda e: e['t']), subs=subs, right_zone=RIGHT_ZONE)
json.dump(scene, open(os.path.join(HERE, 'film.json'), 'w'), indent=1)
json.dump([dict(t0=s['t0'], t1=s['t1'], text=s['en']) for s in subs], open(os.path.join(FILM, 'audio', 'cues.json'), 'w'), indent=1)
json.dump(dict(T=T, DUR=DUR, BPM=BPM, reveal=T['j2'] - .4, sil=[[END('h6') + .2, T['i1'] - .05]]), open(os.path.join(FILM, 'audio', 'timeline.json'), 'w'), indent=1)
print('film.json', DUR, 's ·', len(E), 'elements ·', len(EV), 'events ·', len(subs), 'subtitles')
