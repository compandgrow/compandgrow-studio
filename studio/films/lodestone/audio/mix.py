"""LODESTONE score, sound design and mix -> out/mix.wav (48 kHz stereo).
Synth pop-print toolkit adapted from Lemo-Opuscar styles/halftone-dossier/demo/music.py: 120 BPM, one bar = 2 s.
Reads scenes/timeline.json (line times), audio/sfx.json (cues exported by the picture: node studio/tools/sfxdump.mjs) and audio/vo/*.wav.
Run:  "$LIB/.venv/bin/python" audio/mix.py
"""
import json, os
import numpy as np
from scipy.signal import lfilter, butter
import soundfile as sf
HERE = os.path.dirname(os.path.abspath(__file__)); FILM = os.path.dirname(HERE)
TL = json.load(open(os.path.join(FILM, 'scenes', 'timeline.json'))); T = TL['T']; VO = TL['VO']
CUES = json.load(open(os.path.join(HERE, 'sfx.json'))); CUT = CUES['cut']
SR = 48000
DUR = TL['DUR']; N = int(SR * (DUR + .5))
L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(7)
BEAT = 0.5; BAR = 2.0
def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)
def add(sig, t0, gain=1.0, pan=0.0, buf=None):
    bl, br = buf if buf else (L, R)
    i = int(t0 * SR)
    if i >= N or i < 0: return
    sig = sig[: N - i] * gain
    l = np.cos((pan + 1) * np.pi / 4); r = np.sin((pan + 1) * np.pi / 4)
    bl[i:i + len(sig)] += sig * l * 1.414; br[i:i + len(sig)] += sig * r * 1.414
def env(n, a=0.002, d=0.2, s=0.0, rel=0.05, hold=None):
    t = np.arange(n) / SR
    e = np.minimum(1, t / max(a, 1e-4))
    if hold is None: e = e * np.exp(-np.maximum(0, t - a) / d)
    else: e = np.where(t < hold, e, e * np.exp(-(t - hold) / rel))
    return e
def lp(x, fc, order=2):
    b, a = butter(order, min(fc / (SR / 2), 0.99)); return lfilter(b, a, x)
def hp(x, fc, order=2):
    b, a = butter(order, fc / (SR / 2), 'high'); return lfilter(b, a, x)
def bp(x, lo, hi, order=2):
    b, a = butter(order, [lo / (SR / 2), hi / (SR / 2)], 'band'); return lfilter(b, a, x)

# ---------- instruments (from the Halftone Dossier demo score) ----------
def kick(g=1.0):
    n = int(0.35 * SR); t = np.arange(n) / SR
    f = 48 + 110 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) * np.exp(-t * 9) + 0.25 * np.exp(-t * 300) * rng.standard_normal(n) * 0.3
    return np.tanh(s * 1.6) * g

def snare():
    n = int(0.22 * SR); t = np.arange(n) / SR
    noise = bp(rng.standard_normal(n), 1500, 8000) * np.exp(-t * 18)
    tone = np.sin(2 * np.pi * 190 * t) * np.exp(-t * 30)
    return noise * 0.7 + tone * 0.5

def clap():
    n = int(0.25 * SR); out = np.zeros(n)
    for k, off in enumerate([0, 0.011, 0.022]):
        i = int(off * SR); m = n - i; t = np.arange(m) / SR
        out[i:] += bp(rng.standard_normal(m), 900, 5000) * np.exp(-t * (60 if k < 2 else 16))
    return out * 0.6

def snap():
    n = int(0.08 * SR); t = np.arange(n) / SR
    return bp(rng.standard_normal(n), 2000, 7000) * np.exp(-t * 70) * 0.8

def hat(open_=False):
    n = int((0.18 if open_ else 0.05) * SR); t = np.arange(n) / SR
    return hp(rng.standard_normal(n), 7000) * np.exp(-t * (18 if open_ else 90)) * 0.35

def pluck(m, dur=0.35, bright=1.0):
    
    n = int(dur * SR); t = np.arange(n) / SR; f = mtof(m)
    s = (np.sin(2 * np.pi * f * t) * np.exp(-t * 7)
         + 0.35 * bright * np.sin(2 * np.pi * f * 3.99 * t) * np.exp(-t * 30)
         + 0.12 * np.sin(2 * np.pi * f * 2 * t) * np.exp(-t * 12))
    return s * np.minimum(1, t / 0.002)

def bell(m, dur=1.6):
    
    n = int(dur * SR); t = np.arange(n) / SR; f = mtof(m)
    s = (np.sin(2 * np.pi * f * t) * np.exp(-t * 2.6)
         + 0.4 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 6)
         + 0.2 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t * 11))
    return s * np.minimum(1, t / 0.001)

def bass(m, dur=0.22):
    n = int(dur * SR); t = np.arange(n) / SR; f = mtof(m)
    ph = 2 * np.pi * f * t
    s = np.sin(ph) + 0.3 * np.sign(np.sin(ph)) * 0.5
    s = lp(s, 900)
    return s * env(n, 0.004, 0.18, hold=dur * 0.7, rel=0.03)

def pizz(m, dur=0.18):
    n = int(dur * SR); t = np.arange(n) / SR; f = mtof(m)
    s = lp(np.sign(np.sin(2 * np.pi * f * t)) * 0.6 + np.sin(2 * np.pi * f * t), 1400)
    return s * np.exp(-t * 16) * np.minimum(1, t / 0.003)

def pad(ms, dur):
    n = int(dur * SR); t = np.arange(n) / SR; s = np.zeros(n)
    for m in ms:
        f = mtof(m)
        for det in (-0.12, 0.12):
            ph = 2 * np.pi * f * (1 + det / 100) * t
            s += 2 / np.pi * np.arcsin(np.sin(ph))  
    s = lp(s / (len(ms) * 2), 2200)
    a = np.minimum(1, t / 0.08); r = np.minimum(1, (dur - t) / 0.15)
    return s * a * np.clip(r, 0, 1)

# ---------- sound effects ----------
def stamp(big=False):
    n = int(0.9 * SR); t = np.arange(n) / SR
    f = 40 + 90 * np.exp(-t * 18)
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * (4 if big else 7))
    click = lp(rng.standard_normal(n), 3000) * np.exp(-t * 55)
    s = np.tanh((boom * 1.4 + click * 0.9) * 1.5)
    if big:
        cr = hp(rng.standard_normal(n), 4000) * np.exp(-t * 3.2) * 0.35
        s = s + cr
    return s

def shutter():
    n = int(0.16 * SR); out = np.zeros(n)
    for off in (0, 0.06):
        i = int(off * SR); m = n - i; t = np.arange(m) / SR
        out[i:] += bp(rng.standard_normal(m), 1200, 6000) * np.exp(-t * 110)
    return out * 0.9

def boing(f0=220, f1=520, dur=0.4):
    n = int(dur * SR); t = np.arange(n) / SR
    f = f0 + (f1 - f0) * (1 - np.exp(-t * 14)) + 25 * np.sin(2 * np.pi * 18 * t) * np.exp(-t * 6)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7) * 0.7

def pop(f=900):
    n = int(0.12 * SR); t = np.arange(n) / SR
    fr = f * (1 + 1.2 * np.exp(-t * 60))
    return np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t * 35)

def clink(f=2600):
    n = int(0.3 * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 2.3 * t)) * np.exp(-t * 22) * 0.4

def crash_glass():
    n = int(1.1 * SR); t = np.arange(n) / SR
    s = hp(rng.standard_normal(n), 2500) * np.exp(-t * 7) * 0.6
    s += lp(rng.standard_normal(n), 400) * np.exp(-t * 25) * 0.8
    for k in range(14):
        f = rng.uniform(2200, 7500); d = rng.uniform(0, 0.25)
        i = int(d * SR); m = n - i; tt = np.arange(m) / SR
        s[i:] += np.sin(2 * np.pi * f * tt) * np.exp(-tt * rng.uniform(10, 25)) * 0.18
    return s

def whoosh(dur=0.55, up=True):
    n = int(dur * SR); t = np.arange(n) / SR
    x = rng.standard_normal(n); out = np.zeros(n)
    seg = 512
    for i in range(0, n, seg):
        p = i / n; fc = 400 + 3500 * (p if up else 1 - p)
        out[i:i + seg] = bp(x[max(0, i - 2048):i + seg], fc * 0.7, fc * 1.3)[-len(x[i:i + seg]):]
    return out * np.sin(np.pi * t / dur) ** 2 * 1.2

def plop():
    n = int(0.25 * SR); t = np.arange(n) / SR
    f = 260 * np.exp(-t * 6) + 80
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 14) * 0.9

def key_click():
    n = int(0.04 * SR); t = np.arange(n) / SR
    return bp(rng.standard_normal(n), 2500, 9000) * np.exp(-t * 160) * 0.5

def sparkle():
    out = np.zeros(int(0.9 * SR))
    for k, m in enumerate([84, 88, 91, 96, 100]):
        b = bell(m, 0.7) * 0.35; i = int(k * 0.045 * SR)
        out[i:i + len(b)] += b[: len(out) - i]
    return out

def meow(dur=0.5, f0=640, gain=0.6):
    n = int(dur * SR); t = np.arange(n) / SR; p = t / dur
    f = f0 * (0.9 + 0.45 * np.sin(np.pi * np.clip(p * 1.25, 0, 1)) - 0.25 * p) * (1 + 0.012 * np.sin(2 * np.pi * 6 * t))
    ph = 2 * np.pi * np.cumsum(f) / SR
    
    F1 = np.interp(p, [0, .35, 1], [350, 850, 400]); F2 = np.interp(p, [0, .35, 1], [2300, 1400, 900])
    s = np.zeros(n)
    for h in range(1, 16):
        fh = f * h
        a = np.exp(-((fh - F1) / 260) ** 2) + 0.7 * np.exp(-((fh - F2) / 380) ** 2) + 0.05
        s += a * np.sin(ph * h) / h ** 0.3
    s += 0.02 * hp(rng.standard_normal(n), 3000)
    e = np.minimum(1, t / 0.03) * np.clip((dur - t) / 0.12, 0, 1)
    return s / 6 * e * gain

def roll(t0, t1):
    
    t = t0
    while t < t1:
        p = (t - t0) / (t1 - t0)
        add(snare(), t, 0.15 + 0.5 * p, pan=rng.uniform(-.2, .2))
        t += 0.125 * (1 - p) + 0.03 * p


def tick():
    n = int(0.06 * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 1800 * t) * .5 + bp(rng.standard_normal(n), 2000, 6000) * .6) * np.exp(-t * 90)
def clunk():
    n = int(0.5 * SR); t = np.arange(n) / SR
    f = 90 + 60 * np.exp(-t * 30)
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 12) + bp(rng.standard_normal(n), 300, 2500) * np.exp(-t * 40) * .7) * .9
def rollsnd(d):
    n = int(d * SR); t = np.arange(n) / SR
    x = lp(rng.standard_normal(n), 500) * (1 + .4 * np.sin(2 * np.pi * 11 * t))
    return x * np.minimum(1, t / .08) * np.clip((d - t) / .1, 0, 1) * .8
def zap():
    n = int(0.16 * SR); t = np.arange(n) / SR
    s = np.sign(np.sin(2 * np.pi * (900 + 1400 * np.exp(-t * 30)) * t)) * .25 + hp(rng.standard_normal(n), 3000) * .4
    return s * np.exp(-t * 28)
def paper():
    n = int(0.35 * SR); t = np.arange(n) / SR
    return bp(rng.standard_normal(n), 800, 6000) * np.exp(-t * 12) * np.minimum(1, t / .02) * .7

# ---------- arrangement ----------
C, Am, F, G, E7, Dm = [60, 64, 67], [57, 60, 64], [53, 57, 60], [55, 59, 62], [52, 56, 59, 62], [50, 53, 57]
MEL = {
    'C':  [72, 0, 76, 79, 81, 79, 76, 0], 'Am': [81, 0, 84, 81, 79, 0, 76, 74],
    'F':  [72, 74, 77, 0, 81, 0, 79, 77], 'G':  [79, 0, 74, 0, 71, 74, 79, 0],
    'C2': [84, 0, 83, 84, 79, 0, 76, 79], 'Am2': [81, 84, 0, 88, 86, 84, 81, 0],
    'F2': [77, 0, 81, 84, 86, 84, 81, 77], 'G2': [79, 81, 83, 86, 0, 83, 86, 0],
}
CYC = [(C, 'C'), (Am, 'Am'), (F, 'F'), (G, 'G')]
CYC2 = [(C, 'C2'), (Am, 'Am2'), (F, 'F2'), (G, 'G2')]
VERD = T['i1'] + 1.05
def mode_at(t):
    if t < CUT['s1']: return 'full'
    if t < CUT['s5']: return 'light'      # exhibits under narration
    if t < CUT['s6']: return 'sneak'      # the physics
    if t < CUT['s7']: return 'full'       # title card
    if t < CUT['s11']: return 'drive'     # trials
    if t < VERD - 2.0: return 'sneak'     # one catch
    if t < VERD: return 'build'
    if t < CUT['s13']: return 'full2'
    if t < DUR - 2.4: return 'outro'
    return 'end'
nb = int(np.ceil(DUR / BAR))
for b in range(nb):
    t0 = b * BAR
    md = mode_at(t0 + .01)
    ch, mel = (CYC2 if md in ('full2', 'drive') else CYC)[b % 4]
    root = ch[0] - 24
    if md in ('full', 'full2', 'drive', 'light'):
        lvl = .55 if md == 'light' else 1.0
        for k in range(4):
            if md == 'light' and k % 2: continue
            add(kick(), t0 + k * BEAT, .85 * lvl)
        for k in (1, 3):
            if md == 'light': add(snap(), t0 + k * BEAT, .35, .3)
            else: add(snare(), t0 + k * BEAT, .45); add(clap(), t0 + k * BEAT, .3, .15)
        for k in range(8): add(hat(k == 7), t0 + k * BEAT / 2 + (0.012 if k % 2 else 0), .45 * lvl, .35)
        for k, o in enumerate([0, None, 12, 0, None, 0, 12, None]):
            if o is not None: add(bass(root + o), t0 + k * BEAT / 2, .5 * lvl)
        add(pad([m + 12 for m in ch], BAR), t0, .13 * lvl)
        if md != 'light' or b % 2 == 0:
            for k, m in enumerate(MEL[mel]):
                if m: add(pluck(m), t0 + k * BEAT / 2, .26 * lvl, pan=.2 if k % 2 else -.2)
    elif md == 'sneak':
        line = [45, 0, 48, 0, 49, 50, 0, 0] if b % 2 == 0 else [52, 0, 51, 50, 49, 0, 47, 0]
        for k, m in enumerate(line):
            if m: add(pizz(m), t0 + k * BEAT / 2, .65)
        for k in (1, 3): add(snap(), t0 + k * BEAT, .45, .3)
        add(kick(.6), t0, .6); add(kick(.6), t0 + 2 * BEAT, .45)
        add(pad([57 + 12, 60 + 12, 64 + 12] if b % 2 == 0 else [56 + 12, 59 + 12, 64 + 12], BAR), t0, .08)
    elif md == 'build':
        add(pad([m + 12 for m in G], BAR), t0, .18)
        tt = t0
        while tt < min(t0 + BAR, VERD - .35):
            p = (tt - t0) / BAR; add(snare(), tt, .12 + .4 * p, pan=rng.uniform(-.2, .2)); tt += .125 * (1 - p) + .03 * p
        n = int(BAR * SR); x = np.arange(n) / SR
        add(np.sin(2 * np.pi * np.cumsum(300 + 900 * (x / BAR) ** 2) / SR) * (x / BAR) ** 2 * .07, t0)
    elif md == 'outro':
        add(pad([m + 12 for m in ch], BAR), t0, .12)
        for k, m in enumerate([84, 79, 76, 79, 84, 0, 86, 0]):
            if m: add(bell(m), t0 + k * BEAT / 2, .18, pan=-.3 + .08 * k)
        add(bass(36, 1.2), t0, .3)
# end bell arpeggio + the final hit
for k, m in enumerate([72, 76, 79, 84, 88]): add(bell(m, 2.2), DUR - 2.4 + k * .035, .2, pan=-.4 + .2 * k)

# carve silence before the big stamps (hook + verdict) and before each trial stamp
music = np.stack([L.copy(), R.copy()]); L[:] = 0; R[:] = 0
gate = np.ones(N)
tt = np.arange(N) / SR
for s in CUES['sfx']:
    if s['kind'] == 'stamp':
        a, b = s['t'] - (.55 if s.get('big') else .25), s['t'] + .02
        m = (tt > a) & (tt < b); gate[m] = np.minimum(gate[m], .12 if s.get('big') else .4)
gate = lfilter([1 - .9995], [1, -.9995], gate)
music *= gate

# ---------- narration + ducking ----------
vo = np.zeros((2, N)); vact = np.zeros(N)
for k, t0 in T.items():
    x, sr = sf.read(os.path.join(HERE, 'vo', f'{k}.wav'), dtype='float32')
    if x.ndim > 1: x = x.mean(1)
    if sr != SR:
        import soxr; x = soxr.resample(x, sr, SR)
    i = int(t0 * SR); x = x[: N - i]
    vo[0, i:i + len(x)] += x; vo[1, i:i + len(x)] += x; vact[i:i + len(x) + int(.15 * SR)] = 1
duck = 1 - .62 * lfilter([1 - .9993], [1, -.9993], vact)
music *= duck

# ---------- sound effects from the picture ----------
fxL = np.zeros(N); fxR = np.zeros(N)
for s in CUES['sfx']:
    k, t0, g = s['kind'], s['t'], s['gain']
    sig = {'pop': lambda: pop(s.get('f', 900)), 'whoosh': lambda: whoosh(.4), 'stamp': lambda: stamp(big=s.get('big', False)),
           'paper': paper, 'roll': lambda: rollsnd(s.get('d', 1.0)), 'clunk': clunk, 'tick': tick, 'plop': plop, 'boing': lambda: boing(220, 520),
           'shutter': shutter, 'sparkle': sparkle, 'zap': zap}[k]()
    add(sig, t0, g * .8, 0, (fxL, fxR))
fx = np.stack([fxL, fxR])

mix = music * .55 + fx * .7 + vo * 1.0
mix *= np.clip((DUR + .3 - tt) / 1.2, 0, 1)
pk = np.max(np.abs(mix)); mix = np.tanh(mix / pk * 1.9) * .8
os.makedirs(os.path.join(FILM, 'out'), exist_ok=True)
sf.write(os.path.join(FILM, 'out', 'mix.wav'), mix.T.astype(np.float32), SR, subtype='PCM_16')
print('mix.wav', round(N / SR, 2), 's · peak', round(float(pk), 2))
