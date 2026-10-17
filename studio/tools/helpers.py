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
