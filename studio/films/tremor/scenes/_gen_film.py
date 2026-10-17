#!/usr/bin/env python3
"""TREMOR — the whole film as data -> scenes/film.json, audio/cues.json, audio/timeline.json."""
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

# ================================================================= TREMOR — narration timeline
ORDER = [('a1', .25), ('a2', .1), ('a3', .1),
         ('b1', .6), ('b2', .1), ('b3', .1), ('b4', .05), ('b5', .05),
         ('c1', .6), ('c2', .1), ('c3', .2), ('c4', .2),
         ('d1', .6), ('d2', .3),
         ('e1', .7), ('e2', .3), ('e3', .1), ('e4', .4), ('e5', .05), ('e6', .4),
         ('f1', .6), ('f2', .3), ('f3', .2), ('f4', .3), ('f5', .2),
         ('g1', .6), ('g2', .1),
         ('h1', .6), ('h2', .35), ('h3', .4), ('h4', .35), ('h5', .4), ('h6', .35),
         ('i1', 1.6), ('i2', .2),
         ('j1', .8), ('j2', .7), ('j3', .4)]
T = {}; t = 0.0; prev_end = 0.0
for k, gap in ORDER:
    t0 = max(prev_end + gap, t); t0 = round(math.ceil(t0 / SIX - 1e-9) * SIX, 4)
    T[k] = t0; d = VO[k]; t = t0 + max(1.8, d + .6); prev_end = t0 + d
END = lambda k: T[k] + VO[k]
DUR = round(END('j3') + 3.6, 3)

def tower(x, base, w, h, t0, idp, floors=None, col='graphite', lw=10):
    """a skyscraper sketch: outline, a spire, window rows"""
    floors = floors or max(3, int(h / 70))
    el(type='ink', kind='line', id=idp + '_o', points=R([[x - w / 2, base], [x - w / 2, base - h], [x + w / 2, base - h], [x + w / 2, base]]), lw=lw, color=col, t=t0, d=.4)
    el(type='ink', kind='line', id=idp + '_s', points=R([[x, base - h], [x, base - h - h * .12]]), lw=lw - 2, color=col, t=round(t0 + .38, 3), d=.08)
    st = []
    for k in range(1, floors):
        y = base - h * k / floors
        st.append(dict(points=R([[x - w / 2 + 14, y], [x + w / 2 - 14, y]]), t=round(t0 + .45 + k * .025, 3), d=.05, lw=4, color='grey'))
    el(type='ink', kind='hatch', id=idp + '_f', strokes=st, lw=4, color='grey', alpha=.7)
def wave(x0, x1, y, amp0, amp1, cycles, t0, d, idp, col='blue', lw=10, n=240, arrow=False):
    pts = []
    for i in range(n + 1):
        u = i / n; a = amp0 + (amp1 - amp0) * u
        pts.append([x0 + (x1 - x0) * u, y - a * math.sin(u * cycles * 2 * math.pi)])
    el(type='ink', kind='line', id=idp, points=R(pts), lw=lw, color=col, t=t0, d=d, ea=1.2, eb=1.6, arrow=arrow)

# ================================================================= S1 hook: 5 psi, one skyscraper, down (y 200-1100)
tower(1350, 1060, 300, 760, -.6, 'sky0')
ev(-.3, 'ink', d=.8, kind='line', v=.7)
el(type='ink', kind='write', id='w5psi', text='5 psi', xy=[380, 520], size=170, color='blue', t=snap(T['a1'] + .2), d=.4)
ev(T['a1'] + .2, 'ink', d=.4, kind='write', v=.9)
el(type='ink', kind='line', id='arr5', points=[[700, 560], [1180, 760]], lw=10, color='blue', arrow=True, t=snap(T['a2']), d=.4)
ev(T['a2'], 'dimzip', d=.4, v=.7); ev(T['a2'] + .4, 'arrow', v=.8)
for side in (-1, 1):
    pts = []
    for i in range(13):
        y = 1060 - 760 * i / 12; pts.append([1350 + side * (175 + 30 * math.sin(i * 1.5)), y])
    el(type='ink', kind='line', id=f'sway{side}', points=R(pts), lw=6, color='grey', dash=[16, 12], t=snap(T['a2'] + .5), d=.4)
el(type='stamp', id='st_hook', text='DOWN?', xy=[1350, 640], size=110, rot=-8, t=snap(T['a3']), seed=3)
ev(T['a3'], 'stamp', v=.9)
el(type='tag', id='tag_q', text='5 PSI?', xy=[1880, 260], size=92, rot=-3, magnetColor='red', arrive=dict(t=snap(T['a3'] + .5), kind='swing', d=.8, amp=10),
   strike=dict(t=round(T['j3'] + .05, 3), d=.25, color='red'))
ev(T['a3'] + .5, 'tag', v=.8)

# ================================================================= S2 1935 claim (y 1250-1900)
el(type='ink', kind='write', id='w1935', text='1935', xy=[330, 1360], size=150, color='graphite', t=snap(T['b1']), d=.4)
el(type='tag', id='tag_79', text='AGE 79', xy=[860, 1310], size=74, rot=2, arrive=dict(t=snap(T['b1'] + 1.2), kind='swing', d=.8, amp=8))
ev(T['b1'], 'ink', d=.4, kind='write', v=.9); ev(T['b1'] + 1.2, 'tag', v=.6)
# the oscillator: a piston in a cylinder, clamped to a girder
OX, OY = 520, 1640
el(type='ink', kind='line', id='girder', points=[[300, OY + 90], [1000, OY + 90]], lw=16, color='graphite', t=snap(T['b3'] - .2), d=.35)
el(type='ink', kind='line', id='cyl', points=R([[OX - 90, OY + 80], [OX - 90, OY - 80], [OX + 90, OY - 80], [OX + 90, OY + 80]]), lw=10, color='graphite', t=snap(T['b2'] + .3), d=.35)
el(type='ink', kind='line', id='piston', points=[[OX - 70, OY], [OX + 70, OY]], lw=12, color='blue', t=round(T['b2'] + .7, 3), d=.15)
el(type='ink', kind='line', id='rod', points=[[OX, OY], [OX, OY - 160]], lw=8, color='graphite', t=round(T['b2'] + .85, 3), d=.12)
ev(T['b2'] + .3, 'ink', d=.7, kind='line', v=.6)
el(type='card', id='quote', xy=[1600, 1640], w=1050, h=380, rot=-1.2, z=8, magnetR=22, magnets=[[-470, -150, 'graphite'], [470, -150, 'graphite']],
   arrive=dict(t=round(snap(T['b4']) - .3, 3), kind='drop', d=.3, lift=220, land=.9),
   lines=[dict(text='TESLA, 1935', font='mono', weight=600, size=46, x=60, y=-90, color='grey', track=2),
          dict(text='"5 lb of air pressure', font='sans', weight=900, size=74, x=60, y=10, color='graphite'),
          dict(text='could bring down the', font='sans', weight=900, size=74, x=60, y=95, color='graphite'),
          dict(text='Empire State Building"', font='sans', weight=900, size=74, x=60, y=180, color='graphite')])
ev(T['b4'], 'land', size='mid', v=.8); ev(T['b4'] + .12, 'pin', v=.5); ev(T['b4'] + .25, 'pin', v=.5)

# ================================================================= S3 the lab story (y 2050-2650)
el(type='ink', kind='write', id='w_hou', text='Houston St. lab', xy=[330, 2140], size=100, color='graphite', t=snap(T['c2']), d=.6)
ev(T['c2'], 'ink', d=.6, kind='write', v=.8)
LB = 2560
tower(640, LB, 330, 320, round(snap(T['c2']) + .4, 3), 'lab', floors=4)
for k in range(3):
    xs = 640 + (k - 1) * 30; amp = 18 + 14 * k
    el(type='ink', kind='line', id=f'shake{k}', points=R([[460 - 40 * k, LB - 340 - 20 * k], [460 - 40 * k - amp, LB - 200], [460 - 40 * k, LB - 60]]), lw=6, color='grey', t=round(T['c2'] + 1.2 + k * .15, 3), d=.15)
    el(type='ink', kind='line', id=f'shakeR{k}', points=R([[820 + 40 * k, LB - 340 - 20 * k], [820 + 40 * k + amp, LB - 200], [820 + 40 * k, LB - 60]]), lw=6, color='grey', t=round(T['c2'] + 1.25 + k * .15, 3), d=.15)
ev(T['c2'] + 1.2, 'rattle', v=.7)
el(type='tag', id='tag_cops', text='POLICE', xy=[1230, 2290], size=74, rot=-2, arrive=dict(t=snap(T['c3'] + 1.0), kind='swing', d=.8, amp=9))
ev(T['c3'] + 1.0, 'tag', v=.7)
# the sledgehammer
HX, HY = 1500, 2480
el(type='ink', kind='line', id='ham_h', points=[[HX, HY], [HX + 380, HY - 220]], lw=12, color='graphite', t=snap(T['c4'] + .2), d=.2)
el(type='ink', kind='line', id='ham_head', points=R([[HX + 330, HY - 300], [HX + 470, HY - 220], [HX + 420, HY - 140], [HX + 280, HY - 220], [HX + 330, HY - 300]]), lw=12, color='graphite', t=round(T['c4'] + .4, 3), d=.2)
ev(T['c4'] + .5, 'stamp', v=.6)
el(type='ink', kind='write', id='w_told', text='(as he told it)', xy=[1250, 2620], size=64, color='grey', t=snap(T['c4'] + 1.0), d=.4)

# ================================================================= S4 2006 test (y 2750-3150)
el(type='ink', kind='write', id='w2006', text='2006', xy=[330, 2870], size=140, color='graphite', t=snap(T['d1']), d=.4)
ev(T['d1'], 'ink', d=.4, kind='write', v=.9)
el(type='card', id='tv', xy=[1300, 3020], w=1000, h=260, rot=1.2, z=8, magnetR=20, magnets=[[-450, -100, 'graphite'], [450, -100, 'graphite']],
   arrive=dict(t=round(snap(T['d1'] + 1.2) - .3, 3), kind='drop', d=.3, lift=200, land=.9),
   lines=[dict(text='TV TEST · REBUILT OSCILLATOR', font='mono', weight=600, size=46, x=60, y=-20, color='graphite', track=2),
          dict(text='bridge vibrated, did not fail', font='marker', size=60, x=60, y=70, color='grey')])
ev(T['d1'] + 1.2, 'land', size='mid', v=.8)
el(type='stamp', id='st_busted', text='BUSTED', xy=[1450, 3240], size=96, rot=-6, t=snap(T['d2'] + .5), seed=5)
ev(T['d2'] + .5, 'stamp', v=.85)

# ================================================================= S5 resonance is real: two bridges (y 3300-4100)
BY1 = 3520
el(type='ink', kind='write', id='w1831', text='1831', xy=[330, 3400], size=110, color='graphite', t=snap(T['e2']), d=.35)
el(type='ink', kind='line', id='br1_deck', points=[[330, BY1], [1250, BY1]], lw=11, color='graphite', t=round(T['e2'] + .3, 3), d=.4)
cab = [[330 + 920 * u, BY1 - 150 + 150 * (2 * u - 1) ** 2] for u in [i / 20 for i in range(21)]]
el(type='ink', kind='line', id='br1_cab', points=R(cab), lw=8, color='graphite', t=round(T['e2'] + .5, 3), d=.4)
for i in range(6):
    el(type='ink', kind='line', id=f'sold{i}', points=[[480 + i * 130, BY1 - 10], [480 + i * 130, BY1 - 70]], lw=9, color='graphite', t=round(T['e2'] + 1.0 + i * BEAT / 2, 3), d=.06)
    ev(T['e2'] + 1.0 + i * BEAT / 2, 'tick', v=.5)
wave(330, 1250, BY1 + 80, 4, 40, 6, snap(T['e3']), 1.0, 'bounce1', col='blue', lw=7)
el(type='ink', kind='write', id='w_bolt', text='bolt snaps', xy=[1300, BY1 + 30], size=74, color='red', t=snap(T['e3'] + 1.2), d=.4)
ev(T['e3'] + 1.2, 'stamp', v=.5)
BY2 = 3900
el(type='ink', kind='write', id='w1940', text='1940', xy=[330, 3780], size=110, color='graphite', t=snap(T['e4']), d=.35)
el(type='ink', kind='write', id='w_tac', text='Tacoma Narrows', xy=[700, 3780], size=84, color='grey', t=round(T['e4'] + .4, 3), d=.5)
twist = [[330 + 920 * u, BY2 + 50 * math.sin(u * 4 * math.pi) * u] for u in [i / 60 for i in range(61)]]
twist2 = [[330 + 920 * u, BY2 + 40 - 50 * math.sin(u * 4 * math.pi) * u] for u in [i / 60 for i in range(61)]]
el(type='ink', kind='line', id='tac1', points=R(twist), lw=10, color='graphite', t=snap(T['e4'] + 1.0), d=1.2)
el(type='ink', kind='line', id='tac2', points=R(twist2), lw=10, color='graphite', t=snap(T['e4'] + 1.1), d=1.2)
for i, x in enumerate((420, 640, 860)):
    el(type='ink', kind='line', id=f'wind{i}', points=R([[x - 60, BY2 - 120], [x + 60, BY2 - 135], [x + 140, BY2 - 110]]), lw=6, color='grey', arrow=True, t=round(T['e4'] + .8 + i * .1, 3), d=.2)
ev(T['e4'] + .8, 'whoosh', v=.4)
el(type='ink', kind='write', id='w_tear', text='deck tears', xy=[1300, BY2 + 30], size=74, color='red', t=snap(T['e5'] + .3), d=.4)
el(type='tag', id='tag_beat', text='EVERY STRUCTURE HAS A BEAT', xy=[380, 4080], size=62, rot=-1, arrive=dict(t=snap(T['e6'] + .2), kind='swing', d=.8, amp=8))
ev(T['e6'] + .2, 'tag', v=.7)

# ================================================================= S6 the leap: push on the beat, sway grows (y 4250-4900)
el(type='ink', kind='write', id='w_trem', text='TREMOR', xy=[300, 4330], size=130, color='graphite', t=snap(T['f1']), d=.5)
ev(T['f1'], 'ink', d=.5, kind='write', v=.9)
WY = 4640; WX0, WX1 = 330, 2200; CYC = 7
wave(WX0, WX1, WY, 10, 210, CYC, snap(T['f3']), 4.6, 'grow', col='blue', lw=10, n=420, arrow=True)
ev(T['f3'], 'dimzip', d=4.6, v=.5)
for k in range(CYC):
    u = (k + .25) / CYC; x = WX0 + (WX1 - WX0) * u; a = 10 + 200 * u
    tk = round(T['f3'] + 4.6 * u ** .8, 3)
    el(type='ink', kind='line', id=f'push{k}', points=R([[x, WY - a - 120], [x, WY - a - 30]]), lw=8, color='red', arrow=True, t=tk, d=.1)
    ev(tk, 'tick', v=.45 + .05 * k)
el(type='ink', kind='write', id='w_push', text='push on the beat', xy=[900, 4330], size=74, color='red', t=snap(T['f3'] + .3), d=.5)
el(type='ink', kind='dim', id='dimSway', **{'from': [WX1 + 90, WY + 210], 'to': [WX1 + 90, WY - 210]}, lw=9, color='blue', t=snap(T['f5'] + .3), d=.4)
el(type='ink', kind='write', id='w_sway', text='sway', xy=[WX1 + 140, WY + 20], size=80, color='blue', t=snap(T['f5'] + .7), d=.3)
ev(T['f5'] + .3, 'arrow', v=.9)

# ================================================================= S7 the build: 8 drivers on the foundation (y 5000-5450)
FY = 5380
el(type='ink', kind='line', id='found', points=[[330, FY], [2200, FY]], lw=16, color='graphite', t=snap(T['g1'] - .3), d=.4)
ev(T['g1'] - .3, 'ink', d=.4, kind='line', v=.6)
for i in range(8):
    x = 430 + i * 240; tg = round(snap(T['g1'] + .3) + i * SIX * 2, 4)
    el(type='magnet', id=f'drv{i}', xy=[x, FY - 40], r=34, color='blue' if i % 2 == 0 else 'graphite', z=14, arrive=dict(t=round(tg - .05, 4), kind='snap', d=.3, lift=70))
    ev(tg, 'pin', v=.55, n=i * 5)
el(type='ink', kind='write', id='w8', text='8 drivers', xy=[330, 5180], size=100, color='graphite', t=snap(T['g1'] + .2), d=.4)
el(type='ink', kind='line', id='laser', points=[[2200, 5080], [430, 5300]], lw=6, color='red', dash=[18, 12], t=snap(T['g2'] + .3), d=.6)
el(type='ink', kind='write', id='w_laser', text='laser-tuned', xy=[1400, 5150], size=74, color='red', t=snap(T['g2'] + .8), d=.4)
ev(T['g2'] + .3, 'dimzip', d=.6, v=.6)

# ================================================================= S8 trials: 10 / 30 / 60 m towers (y 5550-6250)
TB = 6200
TRS = [('h1', 'h2', '10 m', 120, 520), ('h3', 'h4', '30 m', 330, 1150), ('h5', 'h6', '60 m', 620, 1830)]
for i, (la, lb, txt, H, x) in enumerate(TRS):
    tl = snap(T[la] + .1)
    tower(x, TB, 170 + 40 * i, H, tl, f'tt{i}', floors=max(2, H // 90), lw=9)
    el(type='ink', kind='dim', id=f'dimH{i}', **{'from': [x - 150 - 20 * i, TB], 'to': [x - 150 - 20 * i, TB - H]}, lw=8, color='blue', t=round(tl + .4, 3), d=.3)
    el(type='ink', kind='write', id=f'wH{i}', text=txt, xy=[x, TB + 90], size=76, color='blue', align='center', t=round(tl + .5, 3), d=.3)
    ts = snap(T[lb] - .02)
    el(type='stamp', id=f'stT{i}', text='DOWN', xy=[x, TB - H / 2], size=72, rot=(-8, 5, -4)[i], t=ts, seed=11 + i)
    ev(tl, 'ink', d=.6, kind='line', v=.6); ev(ts, 'stamp', v=.8 + .1 * i)

# ================================================================= S9 side effect: cracked glass (y 5550-5950, right of trials)
GX, GY = 2380, 5700
el(type='ink', kind='line', id='pane', points=R([[GX - 180, GY - 180], [GX + 180, GY - 180], [GX + 180, GY + 180], [GX - 180, GY + 180], [GX - 180, GY - 180]]), lw=10, color='graphite', t=snap(T['i2'] - .2), d=.35)
crack = [[GX - 20, GY - 10], [GX - 120, GY - 140], [GX - 20, GY - 10], [GX + 150, GY - 60], [GX - 20, GY - 10], [GX + 60, GY + 160], [GX - 20, GY - 10], [GX - 160, GY + 90]]
el(type='ink', kind='line', id='crack', points=crack, lw=7, color='red', t=snap(T['i2'] + .6), d=.3)
ev(T['i2'] + .6, 'glass', v=1.0)
el(type='ink', kind='write', id='w_3bl', text='3 blocks', xy=[GX - 170, GY + 290], size=76, color='blue', t=snap(T['i2'] + 1.1), d=.3)

# ================================================================= right zone (seen in the reveal)
VER = (3150, 5450)
el(type='stamp', id='stamp_cleared', text='CLEARED', xy=[VER[0], VER[1] - 130], size=150, rot=-7, t=snap(T['j1'] + .35), seed=31)
el(type='ink', kind='write', id='w_demo', text='for demolition trials', xy=[VER[0], VER[1] + 80], size=80, color='graphite', align='center', t=snap(T['j1'] + .8), d=.6)
ev(T['j1'] + .35, 'stamp', v=1.0, big=1); ev(T['j1'] + .8, 'ink', d=.6, kind='write', v=.7)
el(type='card', id='title', xy=[3120, 320], w=820, h=440, rot=.6, z=8, magnetR=24, magnets=[[-350, -170, 'red'], [350, -170, 'graphite']],
   lines=[dict(text='TREMOR', font='sans', weight=900, size=150, x=56, y=0, color='graphite', track=4),
          dict(rule=True, x=58, y=40, w=160, h=10, color='red'),
          dict(text='STRUCTURAL RESONANCE', font='mono', weight=600, size=46, x=58, y=120, color='graphite', track=2),
          dict(text='AFTER TESLA, 1935', font='mono', weight=500, size=42, x=58, y=180, color='grey', track=2)])
el(type='card', id='spec', xy=[3120, 2900], w=820, h=560, rot=-.8, z=7, magnetR=20, magnets=[[-360, -240, 'graphite'], [360, -240, 'graphite']],
   lines=[dict(text='SPEC SHEET', font='mono', weight=600, size=60, x=48, y=-160, color='graphite', track=2),
          dict(text='Drivers   8', font='mono', weight=500, size=52, x=48, y=-70, color='graphite'),
          dict(text='Mount     foundation', font='mono', weight=500, size=52, x=48, y=0, color='graphite'),
          dict(text='Tuning    laser', font='mono', weight=500, size=52, x=48, y=70, color='graphite'),
          dict(text='Mode      on the beat', font='mono', weight=500, size=52, x=48, y=140, color='graphite'),
          dict(text='Trials    10/30/60 m', font='mono', weight=500, size=52, x=48, y=210, color='graphite')])
el(type='card', id='note_r', xy=[3080, 4300], w=720, h=280, rot=-2.5, z=7, magnetR=18, magnets=[[0, -110, 'blue']],
   lines=[dict(rule=True, x=30, y=-55, w=660, h=3, color='blue'), dict(text='small push × right beat', font='marker', size=64, x=40, y=30, color='blue'),
          dict(text='= big sway', font='marker', size=64, x=40, y=110, color='graphite')])
el(type='tag', id='tag_a', text='RIGHT BEAT', xy=[1880, 420], size=92, rot=2.5, magnetColor='red', arrive=dict(t=snap(T['j3'] + .1), kind='swing', d=.9, amp=12))
ev(T['j3'] + .1, 'tag', v=1.0); ev(T['j3'] + .05, 'strike', v=.8)

# ================================================================= camera
def fit(x0, x1, y0, y1, m=70, at=.40, zmax=1.4):
    w, h = x1 - x0 + 2 * m, y1 - y0 + 2 * m
    z = min(1080 / w, 1500 / h, zmax); Hv = 1920 / z
    return dict(x=(x0 + x1) / 2, y=(y0 + y1) / 2 + (.5 - at) * Hv, z=round(z, 4))
def go(t, d, f, a=2, b=2.6, roll=None): return c.to(t, d, x=f['x'], y=f['y'], z=f['z'], roll=roll, a=a, b=b)
F0 = fit(300, 2300, 160, 1120, at=.42)
c = Cam(F0['x'], F0['y'] + 300, F0['z'] * 1.5, roll=-2.0)
c.to(0, 1.4, y=F0['y'], z=F0['z'], roll=0, a=1.6, b=2.8)
go(T['b1'] - .4, 1.6, fit(300, 2200, 1250, 1880, at=.42))
go(T['c1'] - .3, 1.5, fit(300, 2000, 2050, 2660, at=.42))
go(T['d1'] - .4, 1.4, fit(300, 2000, 2760, 3320, at=.42))
go(T['e1'] - .2, 1.5, fit(300, 1900, 3320, 3600, at=.42))
go(T['e4'] - .4, 1.4, fit(300, 1900, 3720, 4130, at=.42))
go(T['f1'] - .4, 1.5, fit(280, 2450, 4280, 4900, at=.42))
c.to(T['f4'], 3.0, z=math.exp(c.cur['lz']) * 1.05, roll=-1.0, a=2, b=2.2)
go(T['g1'] - .5, 1.4, fit(300, 2250, 5080, 5420, at=.42), roll=0)
go(T['h1'] - .5, 1.3, fit(280, 800, 5980, 6300, at=.45))
go(T['h3'] - .4, 1.0, fit(280, 1400, 5800, 6300, at=.45))
go(T['h5'] - .4, 1.1, fit(280, 2100, 5500, 6300, m=50, at=.45))
go(T['h6'] + .8, 1.8, fit(1850, 2650, 5440, 6060, at=.42, zmax=1.0))
c.to(T['i1'] + .1, 2.4, z=math.exp(c.cur['lz']) * 1.0, roll=-1.0, a=2, b=2.2)
go(T['i2'] + 1.6, 1.4, fit(2350, 3550, 5250, 5600, at=.42), roll=0)
c.shake(T['j1'] + .35, amp=7, f=8.5, k=6.5, dir=(0, 1), roll=.02)
WALL = dict(x=BW / 2, y=BH / 2, z=min(1080 / BW, 1920 / BH) * .985)
c.to(T['j2'] - .4, 2.6, x=WALL['x'], y=WALL['y'], a=1.5, b=3.2); c.to(T['j2'] - .4, 2.9, z=WALL['z'], a=1.4, b=3.2)
c.to(T['j2'] + 2.6, DUR - T['j2'] - 2.6, z=WALL['z'] * 1.02, a=1.6, b=1.2)
ev(T['j2'] - .4, 'reveal')
for t_ in (T['b1'] - .4, T['c1'] - .3, T['d1'] - .4, T['e1'] - .2, T['e4'] - .4, T['f1'] - .4, T['g1'] - .5, T['h1'] - .5, T['h5'] - .4, T['i2'] + 1.6, T['j2'] - .4):
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
