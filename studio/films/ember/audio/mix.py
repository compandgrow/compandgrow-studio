"""Score, sound design and mix for "EMBER" -> out/mix.wav (48 kHz stereo), plus stems.
Reads the picture's timeline: scenes/film.json (dur, sound events), audio/timeline.json (line times, silence) and audio/vo/.
Run:  $LIB/.venv/bin/python audio/mix.py
Score: 104 BPM, E minor turning to E major at the verdict. Electric bass, MuldjordKit, claves and woodblock,
marimba under the light rays, low brass stabs (trombone, tuba) and timpani on the stamps, tubular bell at the end. No piano, no string pad.
"""
import json, os, sys
import numpy as np, soundfile as sf, soxr
HERE = os.path.dirname(os.path.abspath(__file__)); DEMO = os.path.dirname(HERE)
LIB = os.environ.get('LIB') or os.path.abspath(os.path.join(DEMO, '../..'))
sys.path.insert(0, LIB)
from core.audio import sampler as S
from core.audio.sfx import SR, add, compress, noise, bp, lp, hp, t_, env_exp, norm, whoosh, thump, clack, brown

S.seed(17); rng = np.random.default_rng(19)
scene = json.load(open(os.path.join(DEMO, 'scenes/film.json'))); TL = json.load(open(os.path.join(HERE, 'timeline.json')))
DUR = scene['dur']; EV = scene['ev']; T = TL['T']; VO = json.load(open(os.path.join(HERE, 'vo', 'dur.json')))
N = int((DUR + 1) * SR)
B = 60 / 104
SIL = [tuple(s) for s in TL['sil']]
VERD = T['j1'] + .35            # the CLEARED stamp
END_GROOVE = DUR - 2.0
def silent(t, pad=0): return any(a - pad <= t < b for a, b in SIL)
music = np.zeros((N, 2), np.float32); fx = np.zeros((N, 2), np.float32); amb = np.zeros((N, 2), np.float32); vo = np.zeros((N, 2), np.float32)

ev = []
def note(t, inst, p, d, v, pan=0, **k):
    if t < 0 or t >= DUR: return
    for a, b in SIL:
        if t < a < t + d: d = max(.05, a - t - .03)
        if a <= t < b: return
    ev.append(dict(t=t, inst=inst, pitch=p, dur=d, vel=v, pan=pan, **k))
def hit(t, inst, var, v, gain=1.0, pan=0):
    if silent(t) or t < 0 or t >= DUR: return
    x = S.hit(inst, var, v); add(music, x, t, gain, pan)
def kit(t, var, v, gain=.8, pan=0): hit(t, 'drum_kit', var, v, gain, pan)

# sections (seconds)
A0, B0, C0, D0, E0 = 0.0, T['b1'] - .4, T['e1'] - .3, T['f1'] - .4, T['h1'] - .5
F0, F1 = SIL[0]; G0 = F1; V0 = VERD
# chord plan, one chord per bar (4 beats), cycling per section
PROG = {'A': [('E2', 'Em'), ('E2', 'Em'), ('C2', 'C'), ('D2', 'D')], 'B': [('E2', 'Em'), ('C2', 'C'), ('G1', 'G'), ('D2', 'D')],
        'C': [('A1', 'Am'), ('C2', 'C'), ('E2', 'Em'), ('B1', 'B')], 'D': [('E2', 'Em'), ('G1', 'G'), ('C2', 'C'), ('B1', 'B')],
        'E': [('E2', 'Em'), ('C2', 'C'), ('A1', 'Am'), ('B1', 'B')], 'G': [('C2', 'C'), ('B1', 'B')], 'V': [('E2', 'E'), ('A1', 'A'), ('E2', 'E'), ('B1', 'B')]}
def sec(t):
    if t < B0: return 'A'
    if t < C0: return 'B'
    if t < D0: return 'C'
    if t < E0: return 'D'
    if t < F0: return 'E'
    if t < V0: return 'G'
    return 'V'
def chord_at(t):
    s = sec(t); return PROG[s][int(t // (4 * B)) % len(PROG[s])]
CH = {'Em': ['E3', 'G3', 'B3'], 'C': ['C3', 'E3', 'G3'], 'D': ['D3', 'F#3', 'A3'], 'G': ['G2', 'B2', 'D3'], 'Am': ['A2', 'C3', 'E3'],
      'B': ['B2', 'D#3', 'F#3'], 'E': ['E3', 'G#3', 'B3'], 'A': ['A2', 'C#3', 'E3']}
def stab(t, ch, v=.6, root=None):
    for j, p in enumerate(CH[ch]): note(t + j * .008, 'trombone_stac', p, .3, v, -.25 + .25 * j)
    if root: note(t, 'tuba_stac', root, .35, v)

FIG = [0, 0, 12, 0, 7, 0, 10, 12]
nb = int(DUR / (4 * B)) + 1
for i in range(nb):
    t0 = i * 4 * B
    for s in range(16):
        t = t0 + s * B / 4
        if t >= END_GROOVE: break
        S_ = sec(t)
        if F0 - .05 <= t < G0: continue
        root, _ = chord_at(t)
        if s % 2 == 0:                                         # bass eighths
            k = s // 2; quiet = S_ in ('C', 'G')
            if S_ == 'G' and k % 4: pass
            elif not (S_ == 'A' and t < 1.0):
                note(t, 'electric_bass', S.midi(root) + (FIG[k] if not quiet else 0), .22 if k % 2 else .34, (.5 if quiet else .62) * (1 if k % 2 == 0 else .8))
        if S_ in ('A', 'B', 'D', 'E', 'V'):
            if s in (0, 10) or (S_ in ('D', 'E', 'V') and s == 8): kit(t, 'kick_drum_left', .6 if S_ != 'A' else .45, .85)
            if S_ in ('D', 'E', 'V') and s in (4, 12): kit(t, 'snare_1', .45, .5, -.05)
            if s % 2 == 0 and t > 1.0: hit(t, 'hihat', 'closed', .3 if s % 4 == 0 else .2, .28, .35)
            if S_ == 'B' and s in (3, 11): hit(t, 'woodblock', 'a', .45, .35, .3)
            if S_ == 'A' and s in (3, 7, 14): hit(t, 'claves', None, .4, .3, .3)
        elif S_ == 'C':                                        # the light section: rim and mallets only
            if s in (4, 12): hit(t, 'claves', None, .35, .3, .25)
            if s in (0, 6, 8, 14):
                ch = CH[chord_at(t)[1]]; p = S.midi(ch[(s // 2) % 3]) + 12
                note(t, 'marimba', p, .5, .4, .2)
        elif S_ == 'G':
            if s == 0: hit(t, 'toms', 'low_mallet', .45, .6, -.2)
# brass and timpani on the picture's stamps; a stab for the hook and each section head
for e in [e for e in EV if e['type'] == 'stamp']:
    root, ch = chord_at(e['t'])
    if e.get('big'):
        stab(e['t'], 'E', .9, 'E2'); hit(e['t'], 'timpani', 'drum1', .85, .9); hit(e['t'], 'gran_cassa', 'hit', .75, .8)
    else:
        stab(e['t'], ch, .65, root); hit(e['t'], 'timpani', 'drum2', .55, .6)
stab(T['a3'] + .05, 'Em', .6, 'E2')
for t_s in (B0, C0, D0, E0):
    hit(t_s, 'gran_cassa', 'hit', .4, .45)
# the reveal: held brass chord, tubular bell, a marimba line to the end
RV = scene['reveal']
for j, p in enumerate(['E2', 'B2', 'E3', 'G#3']): note(RV + .2 + j * .02, 'trombone' if j else 'tuba', p, 3.4, .45, -.2 + .15 * j)
note(T['j3'] + .1, 'tubular_bells', 'E4', 4.0, .55, .1)
for k, p in enumerate(['E5', 'G#5', 'B5', 'E6']): note(T['j3'] + .1 + .29 * k, 'glockenspiel' if k == 3 else 'marimba', p, 1.2, .4, .2)
for j, p in enumerate(['E2', 'B2', 'E3', 'G#3', 'B3']): note(END_GROOVE, 'trombone' if j else 'tuba', p, 2.0, .5, -.2 + .1 * j)

mus = S.render([(e['t'], e['inst'], e['pitch'], e['dur'], e['vel'], e['pan']) for e in ev], dur=N / SR, master=False)
music[:len(mus)] += mus[:N]
music = S.room(music, size=.35, mix=.14)
for a, b in SIL: music[int(a * SR):int(b * SR)] *= 0.0

# ================================================================= sound design (procedural, on the picture's events)
def marker(d, kind='line', seed=0, v=1.0):
    r = np.random.default_rng(abs(int(seed))); n = int(d * SR); tt = np.arange(n) / SR
    bed = bp(r.standard_normal(n), 1800, 6500) * (.5 + .5 * np.sin(2 * np.pi * (7 + r.random() * 5) * tt)) * .35
    x = bed.copy(); count = int(d * (10 if kind == 'write' else 4)) + 1
    for k in range(count):
        st = r.uniform(0, max(.01, d - .1)); ln = r.uniform(.035, .12); m = int(ln * SR); s0 = int(st * SR)
        f0 = r.uniform(1900, 3400); f = f0 * (1 + .18 * np.sin(np.linspace(0, np.pi * r.uniform(1, 3), m))) + 40 * np.sin(2 * np.pi * 30 * np.arange(m) / SR)
        ph = 2 * np.pi * np.cumsum(f) / SR
        sq = (np.sin(ph) + .35 * np.sin(2 * ph) + .15 * np.sin(3 * ph)) * np.sin(np.linspace(0, np.pi, m)) ** 1.5
        x[s0:s0 + m] += sq[:max(0, min(m, n - s0))] * r.uniform(.25, .6)
    fade = np.minimum(1, np.minimum(tt / .015, (d - tt) / .03))
    return (x * fade * v).astype(np.float32)
def tap(v=1.0, f=1.0):     # marker nib tapping the enamel
    d = .06; tt = t_(d)
    return (norm(hp(noise(d), 2500) * env_exp(d, .002) + np.sin(2 * np.pi * 900 * f * tt) * env_exp(d, .008) * .6 + np.sin(2 * np.pi * 180 * tt) * env_exp(d, .02) * .4) * v).astype(np.float32)
def magnet_snap(v=1.0, heavy=False, pitch=1.0):
    d = .14; tt = t_(d)
    tr = hp(noise(d), 3000) * env_exp(d, .0012)
    ring = sum(a * np.sin(2 * np.pi * f * pitch * tt) * env_exp(d, tau) for f, a, tau in [(3400, .35, .006), (1850, .3, .01)])
    body = np.sin(2 * np.pi * (140 if heavy else 210) * pitch * tt) * env_exp(d, .025) * (.9 if heavy else .45)
    return (norm(tr + ring + body) * v).astype(np.float32)
def pop_off(v=1.0, pitch=1.0):  # a magnet pulled off: suction release + a light tick
    d = .12; tt = t_(d); f = (300 + 900 * tt / d) * pitch
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(d, .03) * .7 + hp(noise(d), 4000) * env_exp(d, .003) * .5
    return (norm(x) * v).astype(np.float32)
def landing(v=1.0, size='mid'):
    d = .8; tt = t_(d); f = 48 if size == 'big' else 66
    low = np.sin(2 * np.pi * f * tt * (1 - .25 * tt)) * env_exp(d, .13 if size == 'big' else .08)
    board = bp(noise(d), 150, 520) * env_exp(d, .06) * .8
    slap = hp(noise(d), 1200) * env_exp(d, .006) * .55
    rattle = np.zeros_like(tt)
    if size == 'big':
        for k in range(5): s0 = int((.03 + k * .045) * SR); c_ = clack(.7 + .1 * k, .25 / (k + 1)); rattle[s0:s0 + len(c_)] += c_[:len(rattle) - s0]
    return (norm(low * 1.15 + board + slap + rattle) * v).astype(np.float32)
def friction(d, low=False):
    n = len(t_(d)); tt = np.arange(n) / SR
    x = bp(rng.standard_normal(n), 250 if low else 600, 1800 if low else 4000) * (.6 + .4 * np.sin(2 * np.pi * 13 * tt))
    return (x * np.sin(np.pi * tt / d) ** .7 * .6).astype(np.float32)
def steel_ruler(v=1.0):
    d = 1.1; tt = t_(d)
    ring = sum(a * np.sin(2 * np.pi * f * tt + p) * env_exp(d, tau) for f, a, tau, p in [(523, .5, .35, 0), (1391, .4, .22, 1), (2716, .3, .14, 2), (4107, .2, .08, .5), (6150, .1, .05, 1.5)])
    ld = landing(1, 'mid'); ld = np.pad(ld, (0, max(0, len(tt) - len(ld))))[:len(tt)]
    x = ring * .6 + ld * .8
    out = norm(x) * v
    m2 = magnet_snap(.7, True); out[int(.035 * SR):int(.035 * SR) + len(m2)] += m2[:len(out) - int(.035 * SR)]
    return out.astype(np.float32)
def stamp_sfx(v=1.0):
    d = .6; tt = t_(d)
    low = np.sin(2 * np.pi * 58 * tt * (1 - .3 * tt)) * env_exp(d, .09)
    squish = lp(noise(d), 900) * env_exp(d, .025) * .9
    slap = hp(noise(d), 1500) * env_exp(d, .004) * .7
    return (norm(low * 1.2 + squish + slap) * v).astype(np.float32)
def ship_horn(dur=2.2, f0=73.42, far=False, v=1.0):
    n = int((dur + .8) * SR); tt = np.arange(n) / SR
    env = np.minimum(1, tt / .18) * np.clip((dur + .6 - tt) / .6, 0, 1) ** 1.5
    bend = 1 - .018 * np.exp(-tt / .25)
    x = np.zeros(n)
    for f, a in ((f0, 1.0), (f0 * 1.5, .7)):              # two-tone horn: root and fifth
        ph = 2 * np.pi * np.cumsum(f * bend * (1 + .002 * np.sin(2 * np.pi * 4.3 * tt))) / SR
        for h in range(1, 14):
            x += a * np.sin(h * ph) / h ** .9 * (1.6 if 3 <= h <= 7 else 1)   # brassy middle harmonics
    x = bp(x, 60, 1400 if far else 3200) * env + bp(rng.standard_normal(n), 300, 1800) * env * .03
    y = np.stack([x, x], 1).astype(np.float32); y = S.room(y, size=.85 if far else .6, mix=.5 if far else .3)
    return (y[:, 0] / (np.abs(y).max() + 1e-9) * v).astype(np.float32)
def engine(d, v=1.0):
    d = round(d * SR) / SR; n = len(t_(d)); tt = np.arange(n) / SR
    x = lp(brown(d), 160) * (1 + .55 * np.sin(2 * np.pi * 6.5 * tt)) + np.sin(2 * np.pi * 44 * tt) * .25 * (1 + .5 * np.sin(2 * np.pi * 6.5 * tt))
    e = np.minimum(1, tt / .5) * np.minimum(1, (d - tt) / .4)
    return (norm(x) * e * v).astype(np.float32)
def water(d, v=1.0, seed=3):
    r = np.random.default_rng(abs(int(seed))); n = int(d * SR); out = np.zeros(n); t = 0.0
    while t < d - .2:
        ln = r.uniform(.15, .4); m = int(ln * SR); s0 = int(t * SR); seg = bp(r.standard_normal(m), r.uniform(250, 500), r.uniform(900, 1600)) * np.sin(np.linspace(0, np.pi, m)) ** 2
        out[s0:s0 + m] += seg[:n - s0] * r.uniform(.4, 1.0); t += r.uniform(.18, .45)
    e = np.minimum(1, np.arange(n) / SR / .4) * np.minimum(1, (d - np.arange(n) / SR) / .5)
    return (norm(out) * e * v).astype(np.float32)
def room_tone(d):
    """the room: air conditioning (a broadband wash, the fan's hum) and, through the window, a traffic bed with cars passing"""
    d = round(d * SR) / SR; n = len(t_(d)); tt = np.arange(n) / SR
    hvac = bp(rng.standard_normal(n), 120, 1500) * .5 + lp(brown(d), 300) * .3 + (np.sin(2 * np.pi * 118 * tt) + .4 * np.sin(2 * np.pi * 236 * tt)) * .06
    traffic = lp(brown(d), 260) * .45
    r = np.random.default_rng(41); t = .8
    while t < d - 2:
        ln = r.uniform(2.2, 3.6); m = int(ln * SR); s0 = int(t * SR)
        sw = bp(r.standard_normal(m), r.uniform(160, 280), r.uniform(1100, 2200)) * np.sin(np.linspace(0, np.pi, m)) ** 2 * r.uniform(.6, 1.1)
        traffic[s0:s0 + m] += sw[:max(0, min(m, n - s0))]
        t += r.uniform(3.0, 6.0)
    return hvac.astype(np.float32), traffic.astype(np.float32)

for e in EV:
    t, ty, v = e['t'], e['type'], e.get('v', 1.0)
    if ty == 'ink': add(fx, marker(e['d'], e.get('kind', 'line'), int(t * 100) + 1, v), t, .17 if e.get('kind') == 'write' else .13, pan=.08)
    elif ty == 'dimzip': add(fx, marker(e['d'], 'line', int(t * 100) + 7, 1.2), t, .16 * v, pan=.1)
    elif ty == 'scribble': add(fx, marker(e['d'], 'write', int(t * 100) + 3, .7), t, .1 * v, pan=-.1)
    elif ty == 'arrow': add(fx, tap(v), t, .3, pan=.1)
    elif ty == 'pin': add(fx, magnet_snap(v, True, 1.0 + .03 * (e.get('n', 0) % 4)), t, .26, pan=-.3 + .6 * (e.get('n', 23) / 46))
    elif ty == 'tag': add(fx, magnet_snap(v), t, .38 * v, pan=rng.uniform(-.2, .2))
    elif ty == 'land': add(fx, landing(v, e.get('size', 'mid')), t - .01, .55 * v)
    elif ty == 'erase': add(fx, friction(e['d']), t, .32)
    elif ty == 'strike': add(fx, marker(.25, 'line', 77, 1.4), t, .22)
    elif ty == 'stamp': add(fx, stamp_sfx(1.0), t, .85 * v)
    elif ty == 'rattle':
        for q in range(5): add(fx, clack(1.6 + .2 * q, .5 / (q + 1)), t + q * .035, .25 * v, pan=.2)
    elif ty == 'tick': add(fx, tap(v, 1.3), t, .22, pan=rng.uniform(-.3, .3))
    elif ty == 'thunder':
        d_ = 2.6; tt_ = t_(d_); boom = np.sin(2 * np.pi * 46 * tt_ * (1 - .2 * tt_)) * env_exp(d_, .35)
        crack = hp(noise(d_), 2200) * env_exp(d_, .05); roll_ = lp(brown(d_), 220) * env_exp(d_, .9)
        add(fx, norm(boom * 1.1 + crack * .8 + roll_ * .9).astype(np.float32) * v, t, .9)
    elif ty == 'glass':
        d_ = 1.2; tt_ = t_(d_); tink = sum(np.sin(2 * np.pi * f * tt_) * env_exp(d_, tau) * a for f, a, tau in [(3100, .5, .12), (4700, .4, .08), (6900, .3, .05), (2300, .3, .2)])
        crk = hp(noise(d_), 3000) * env_exp(d_, .02)
        add(fx, norm(tink + crk * 1.2).astype(np.float32) * v, t, .55)
    elif ty == 'whoosh': add(fx, whoosh(.45, 1.0), t - .08, .2 * v)
    elif ty == 'reveal': add(fx, thump(.9, 42), t, .45); add(fx, whoosh(.9, .6), t, .12)
# the silences: everything but the room drops away (40 ms fades); the first sound after each is the stamp / the horn
gate = np.ones(N, np.float32)
for a, b in SIL:
    i0, i1, f = int(a * SR), int(b * SR), int(.04 * SR)
    gate[i0:i1] = .03; gate[i0 - f:i0] = np.linspace(1, .03, f); gate[i1 - 2:i1] = .03
fx *= gate[:, None]; amb *= gate[:, None]

# ================================================================= voice
for e in EV:
    if e['type'] != 'vo': continue
    x, sr = sf.read(os.path.join(HERE, 'vo', e['id'] + '.wav'), dtype='float32')
    if x.ndim > 1: x = x.mean(1)
    x = soxr.resample(x, sr, SR) if sr != SR else x
    x = hp(x, 80); x = compress(x / (np.abs(x).max() + 1e-9), thr=.3, ratio=3.0)
    add(vo, x, e['t'], 1.0)

def rms(x): return float(np.sqrt(np.mean(x ** 2) + 1e-12))
vmask = np.abs(vo).max(1) > 1e-4; v_rms = rms(vo[vmask])
# room tone under everything, about 20 dB under the voice: the AC on the right, the window (traffic) on the left.
# Added after the gate, so the silences keep exactly this and nothing else.
hv_, tr_ = room_tone(DUR + .5); room = np.zeros_like(amb); add(room, hv_, 0, 1.0, .25); add(room, tr_, 0, 1.0, -.5)
room *= v_rms * 10 ** (-20 / 20) / rms(room); amb += room
music *= (v_rms / rms(music[np.abs(music).max(1) > 1e-4])) * 10 ** (-8.5 / 20)      # music ~8.5 dB under the voice
win = int(.12 * SR); venv = np.convolve(np.abs(vo).max(1), np.ones(win) / win, 'same')
duck = 1 - .4 * np.clip(venv / (venv.max() * .25 + 1e-9), 0, 1)
music *= duck[:, None]; fx *= (1 - .3 * (1 - duck))[:, None]
music = hp(music.T, 36).T.astype(np.float32)
mix = music + fx * .78 + amb + vo
# low end: a 30 Hz high-pass keeps the sub tidy (measured: 20–120 Hz sits about 11 dB under 120 Hz–2 kHz by band energy)
mix = hp(mix.T, 30).T.astype(np.float32)
from scipy.ndimage import maximum_filter1d, uniform_filter1d
def bus_limit(x, ceil, look=.006, rel=.06):
    n = int(look * SR); pk = np.abs(x).max(1)
    m = maximum_filter1d(pk, size=2 * n + 1); g = np.minimum(1, ceil / np.maximum(m, 1e-9))
    g = uniform_filter1d(g, size=n); g = np.minimum(g, uniform_filter1d(g, size=int(rel * SR)))
    return x * g[:, None]
peak_rms = np.sqrt(np.mean(mix[np.abs(mix).max(1) > 1e-4] ** 2))
mix = bus_limit(mix, peak_rms * 4.5)
mix = mix / np.abs(mix).max() * .7
end = int(DUR * SR); fo = int(1.2 * SR); mix[end - fo:end] *= np.linspace(1, 0, fo)[:, None] ** 1.5
os.makedirs(os.path.join(DEMO, 'out'), exist_ok=True)
sf.write(os.path.join(DEMO, 'out/mix.wav'), mix[:end], SR)
os.makedirs(os.path.join(HERE, 'stems'), exist_ok=True)
for nm, s in (('music', music), ('fx', fx), ('amb', amb), ('vo', vo)): sf.write(os.path.join(HERE, 'stems', nm + '.wav'), s[:end], SR)
print('out/mix.wav', round(DUR, 2), 's ·', len(ev), 'score notes')
