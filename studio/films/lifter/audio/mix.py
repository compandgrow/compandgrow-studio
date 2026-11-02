"""STILLWING score, foley, voice and mix -> out/mix.wav (48 kHz stereo).
Exploded Teardown palette (adapted from Lemo-Opuscar styles/teardown/demo/mix.py): 96 BPM in D minor, marimba / electric bass /
synth kick / claves / hi-hat outside the object, bowed vibraphone + glass + a sub pulse inside it, three near-silences
(room tone only) before the separation, before STILLWING and before the verdict; "Silent." (e6) sits on room tone.
Reads scenes/timeline.json (line times), audio/sfx.json (cues exported by the picture: node studio/tools/sfxdump.mjs) and audio/vo/*.wav.
Run:  "$LIB/.venv/bin/python" audio/mix.py      (LIB = Lemo-Opuscar library folder, or run from inside $LIB/films/lifter)
"""
import os, sys, json
import numpy as np, soundfile as sf, soxr
from scipy.ndimage import uniform_filter1d, maximum_filter1d
HERE = os.path.dirname(os.path.abspath(__file__)); FILM = os.path.dirname(HERE)
LIB = os.environ.get('LIB') or os.path.abspath(os.path.join(FILM, '../..'))
sys.path.insert(0, LIB)
from core.audio import sampler as S
from core.audio.sfx import SR, add, noise, lp, hp, bp, env_exp, t_, norm, compress, limit

S.seed(6)
TL = json.load(open(os.path.join(FILM, 'scenes', 'timeline.json'))); T, VOD, DUR = TL['T'], TL['VO'], TL['DUR']
CUES = json.load(open(os.path.join(HERE, 'sfx.json'))); FX = CUES['sfx']; X = CUES['cut']
END = lambda k: T[k] + VOD[k]
N = int((DUR + 1.0) * SR)
def buf(): return np.zeros((N, 2), np.float32)
BPM = 96; BEAT = 60 / BPM; BAR = 4 * BEAT
rng = np.random.default_rng(6)

# ---------------- sections (film seconds) ----------------
SIL = [(END('a5') + .15, T['b1'] - .02),          # near-silence 1 (after "Take it apart.")
       (END('c11') + .15, T['d1'] - .02),         # near-silence 2 (before STILLWING)
       (X['flew3'] + .05, T['f1'] - .02),         # "Silent." — room tone only
       (END('f5') + .15, T['g1'] - .02)]          # near-silence 3 (before the verdict)
def section(t):
    if t < END('a5'): return 'hook'
    if t < T['c1']: return 'soft'
    if t < T['c4'] - .3: return 'groove'
    if t < T['c10'] - .1: return 'inside'
    if t < T['d1']: return 'light'
    if t < X['flew3']: return 'drive'
    if t < T['g1']: return 'inside'
    if t < T['h2']: return 'soft'
    return 'card'
CH = [['D3', 'F3', 'A3', 'C4', 'E4'], ['A#2', 'D3', 'F3', 'A3', 'C4'], ['F2', 'A2', 'C3', 'E3', 'G3'], ['C3', 'E3', 'G3', 'B3', 'D4']]
ROOT = ['D2', 'A#1', 'F1', 'C2']
def up(p, n): return S.name(S.midi(p) + 12 * n)
ev, kick_t = [], []
nb = int(np.ceil(DUR / BAR))
for bar in range(nb):
    t0 = bar * BAR; c = CH[bar % 4]; r = ROOT[bar % 4]
    for i in range(16):
        t = t0 + i * BEAT / 4; s = section(t)
        if s == 'hook' and i % 2 == 0:
            ev.append((t, 'marimba', up(c[(i // 2 * 2) % 5], 1), .4, .3 + .08 * (i % 4 == 0), -.25 + .5 * (i % 4 == 0), 1.5))
        if s in ('groove', 'drive', 'light'):
            if s == 'light' and i % 2: continue
            p = up(c[[0, 2, 4, 2, 1, 3, 4, 3][i % 8]], 1 + (i % 8 == 2))
            ev.append((t, 'marimba', p, .3, .4 + .2 * (i % 4 == 0), [-.35, .35][i % 2], .9 if s != 'light' else .7))
            ev.append((t, 'hihat', 'closed', None, .25 + .15 * (i % 2 == 0), -.3, .32 if s != 'light' else .2))
            if i % 4 == 0:
                k = i // 4
                if s == 'drive' or k in (0, 2): kick_t.append((t, .9 if s != 'light' else .6))
                if k in (1, 3): ev.append((t, 'claves', None, None, .5, .2, .5))
            if i in (0, 6, 8, 12, 14) and s != 'light': ev.append((t, 'electric_bass', r, BEAT * .9, .7, 0, 1.1))
        if s == 'inside' and i % 4 == 0:
            ev.append((t, 'hihat', 'pedal', None, .2, .35, .2))
            if i == 0: kick_t.append((t, .5))
        if s == 'soft' and i == 0 and t > T['b1'] - .1:
            ev.append((t, 'marimba', up(c[0], 1), 1.0, .35, -.2, 1.0))
    s0 = section(t0 + .01)
    if s0 in ('hook', 'soft', 'inside'):
        for j, p in enumerate(c[1:4]): ev.append((t0 + j * .05, 'vibraphone_bowed', up(p, 1), BAR * 1.02, .4, -.4 + .4 * j, .7))
    if s0 == 'inside':
        for k, idx in [(0, 4), (1.5, 2), (2.5, 3)]: ev.append((t0 + k * BEAT, 'glass', up(c[idx], 2 if idx < 3 else 1), 1.2, .36, .3 - .1 * k, .45))
# end card (D major): rolled chord, bowed vibes, glockenspiel answer
tc = X['endcard']; kick_t.append((tc, 1.1))
for j, p in enumerate(['D3', 'A3', 'D4', 'F#4', 'A4', 'D5']): ev.append((tc + j * .045, 'marimba', p, 2.5, .6, -.5 + .2 * j, 1.0))
for p in ['D4', 'F#4', 'A4']: ev.append((tc, 'vibraphone_bowed', p, 5.0, .45, 0, .8))
ev.append((tc, 'electric_bass', 'D2', 3.0, .75, 0, 1.0))
for k, p in [(1.0, 'A5'), (1.6, 'F#5'), (2.2, 'D6')]: ev.append((tc + k, 'glockenspiel', p, 2, .4, .25, .45))
# glockenspiel pings on the trial numbers and the STILLWING title
for t, p in [(T['d1'], 'D6'), (X['tr1'], 'A5'), (X['tr2'], 'C6'), (X['tr3'], 'E6')]: ev.append((t, 'glockenspiel', p, 2, .5, .15, .55))

music = np.asarray(S.render([e for e in ev if e[0] < DUR], dur=N / SR, master=False), np.float32)
music = np.pad(music, ((0, max(0, N - len(music))), (0, 0)))[:N]
def kick(v=1.0):
    d = .45; tt = t_(d); f = 54 + 90 * np.exp(-tt / .035); ph = 2 * np.pi * np.cumsum(f) / SR
    return norm(np.sin(ph) * env_exp(d, .16) + np.sin(2 * ph) * .25 * env_exp(d, .05) + hp(noise(d), 3000) * env_exp(d, .003) * .25) * v
pulse = buf()
for t, v in kick_t: add(pulse, kick(v), t, .55)

# ---------------- foley (from the picture's cues) ----------------
fol = buf()
def foil_clack(v=1.0, d=.08):              # foil cell landing: crinkly tick + small hollow knock
    tt = t_(d); x = bp(noise(d), 2500, 9000) * env_exp(d, .006) + np.sin(2 * np.pi * (700 + rng.random() * 300) * tt) * env_exp(d, .012) * .5
    return norm(x) * v
def thud(v=1.0):
    d = .45; tt = t_(d); return norm(np.sin(2 * np.pi * 70 * tt * (1 - .2 * tt)) * env_exp(d, .1) + lp(noise(d), 400) * env_exp(d, .025) * .6) * v
def stampsnd(big=False):
    d = .9; tt = t_(d); f = 40 + 90 * np.exp(-tt * 18)
    x = np.tanh((np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * (4 if big else 7)) * 1.4 + lp(noise(d), 3000) * np.exp(-tt * 55) * .9) * 1.5)
    if big: x = x + hp(noise(d), 4000) * np.exp(-tt * 3.2) * .3
    return norm(x)
def swoosh(d=.6, v=1.0, rise=True):
    n = noise(d); out = np.zeros_like(n); tt = t_(d)
    for i in range(0, len(n), 480):
        hi = min(len(n), i + 480); u = i / len(n); u = u if rise else 1 - u
        f = 300 + 3600 * u ** 1.5; out[i:hi] = bp(n[max(0, i - 2400):hi], f * .6, f * 1.4)[-(hi - i):]
    return norm(out * np.sin(np.pi * tt / d) ** 1.5) * v
def tick(v=1.0, f=5200):
    d = .03; tt = t_(d); return norm(np.sin(2 * np.pi * f * tt) * env_exp(d, .003) + hp(noise(d), 6000) * env_exp(d, .001) * .4) * v
def pen(v=1.0, d=.5):
    tt = t_(d); return norm(bp(noise(d), 3000, 9000) * np.sin(np.pi * tt / d) ** 2 * (1 + .3 * np.sin(2 * np.pi * 31 * tt))) * v
def humsnd(d):                              # high-voltage corona: 50 Hz buzz + faint hiss
    tt = t_(d); x = np.sign(np.sin(2 * np.pi * 100 * tt)) * .2 + np.sin(2 * np.pi * 100 * tt) * .5
    x = lp(x, 900) + hp(noise(d), 6000) * .25
    return norm(x) * np.clip(tt / .6, 0, 1) * np.clip((d - tt) / .6, 0, 1)
def crackle(d):
    x = np.zeros(int(d * SR))
    for k in range(int(d * 28)):
        i = rng.integers(0, len(x) - 400); x[i:i + 400] += hp(noise(400 / SR), 3000) * np.exp(-np.arange(400) / 50) * rng.random()
    return norm(x)
def windsnd(d, fade=0):
    tt = t_(d); x = lp(noise(d), 700) * (1 + .3 * np.sin(2 * np.pi * .7 * tt))
    e = np.clip(tt / .8, 0, 1) * np.clip((d - tt) / .6, 0, 1) * (1 - .85 * fade * tt / d)
    return norm(x) * e
def glass(v=1.0):
    d = 1.2; tt = t_(d)
    return norm(sum(a * np.sin(2 * np.pi * f * tt) * env_exp(d, tau) for f, a, tau in [(1900, 1, .5), (4300, .5, .25), (6900, .25, .12)])) * v
def paper(v=1.0):
    d = .35; tt = t_(d); return norm(bp(noise(d), 800, 6000) * np.exp(-tt * 12) * np.minimum(1, tt / .02)) * v
for s in FX:
    k, t, gn = s['kind'], s['t'], s.get('gain', 1)
    if k == 'clack': add(fol, foil_clack(1), t, .13 * gn / .3, rng.uniform(-.6, .6))
    elif k == 'tick': add(fol, tick(1, 4800 + 400 * rng.random()), t, .08 * gn, .5)
    elif k == 'stamp': add(fol, stampsnd(s.get('big', False)), t, (.6 if s.get('big') else .42) * gn)
    elif k == 'strike': add(fol, swoosh(.25, 1, True), t, .15)
    elif k == 'pen': add(fol, pen(1, .55), t, .1 * gn, .3)
    elif k == 'lift': add(fol, swoosh(.6, 1, True), t - .05, .22 * gn)
    elif k == 'land': add(fol, thud(1), t, .35 * gn); add(fol, foil_clack(1), t, .2 * gn)
    elif k == 'whoosh': add(fol, swoosh(s.get('d', .6), 1, False), t, .26 * gn)
    elif k == 'dive': add(fol, swoosh(1.4, 1, False), t - .3, .26 * gn)
    elif k == 'hit': add(fol, thud(1), t, .4 * gn); add(fol, glass(.6), t, .05 * gn)
    elif k == 'hum': add(fol, humsnd(s['d']), t, .05 * gn)
    elif k == 'crackle': add(fol, crackle(s['d']), t, .05 * gn)
    elif k == 'wind': add(fol, windsnd(s['d'], s.get('fade', 0)), t, .12 * gn)
    elif k == 'glass': add(fol, glass(1), t, .12 * gn)
    elif k == 'paper': add(fol, paper(1), t, .2 * gn)
# room tone bed
tt = np.arange(N) / SR
bed = lp(np.cumsum(noise(N / SR)) * .002, 300); bed -= np.convolve(bed, np.ones(4800) / 4800, 'same'); bed = norm(bed) * .5
bedmix = (bed * .035)[:, None] * np.ones((1, 2))

# ---------------- near-silences: music and pulse out ----------------
def gate(a, z, fade=.12):
    g = np.ones(N, np.float32); i0, i1, f = int(a * SR), int(z * SR), int(fade * SR)
    g[i0:i1] = 0; g[max(0, i0 - f):i0] *= np.linspace(1, 0, min(f, i0)); g[i1:i1 + f] *= np.linspace(0, 1, f); return g[:, None]
sil = np.ones((N, 1), np.float32)
for a, z in SIL: sil *= gate(a, z)
music *= sil; pulse *= sil
fol *= gate(X['flew3'] + .5, T['f1'] - .02, .3)      # "Silent." keeps only room tone (after the FLEW stamp's tail)

# ---------------- voice ----------------
voice = buf()
for k, t0 in T.items():
    x, sr = sf.read(os.path.join(HERE, 'vo', f'{k}.wav'), dtype='float32')
    if x.ndim > 1: x = x.mean(1)
    if sr != SR: x = soxr.resample(x, sr, SR)
    x = hp(x, 80); x = compress(x / (np.abs(x).max() + 1e-9) * .9, thr=.22, ratio=3.0)
    add(voice, x, t0, .5, 0)
venv = uniform_filter1d(maximum_filter1d(np.abs(voice).mean(1), int(.25 * SR)), int(.2 * SR))
duck = 1 - .55 * np.clip(venv / (venv.max() + 1e-9) * 4, 0, 1)
mus = music * .9 + pulse
for c in range(2): mus[:, c] = hp(mus[:, c], 44, 4); fol[:, c] = hp(fol[:, c], 36, 2)
mus *= duck[:, None]
mix = voice * 1.0 + mus * .42 + fol * .9 + bedmix
for c in range(2): mix[:, c] = limit(mix[:, c], .92)
end = int(DUR * SR); tail = int(.6 * SR)
mix = mix[:end]; mix[-tail:] *= np.linspace(1, 0, tail)[:, None] ** 2
os.makedirs(os.path.join(FILM, 'out'), exist_ok=True)
sf.write(os.path.join(FILM, 'out', 'mix.wav'), mix, SR, subtype='PCM_24')
print(f'mix {DUR:.2f}s  peak {np.abs(mix).max():.2f}')
