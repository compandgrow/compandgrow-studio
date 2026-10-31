"""Score for the game Reel, numpy only: pad bed + pulse, whoosh per card, ticks, stamp thuds, REAL hit."""
import json, sys, wave, numpy as np
SR = 44100
st = json.load(open('out/stamps.json')); DUR = 28.0
n = int(SR * DUR); t = np.arange(n) / SR; mix = np.zeros(n)
rng = np.random.default_rng(7)
def lp(x, a):  # one-pole low-pass
    y = np.empty_like(x); acc = 0.0
    for i in range(len(x)): acc += a * (x[i] - acc); y[i] = acc
    return y
def add(sig, at, g=1.0):
    i = int(at * SR); j = min(n, i + len(sig)); mix[i:j] += g * sig[:j - i]
# pad: A minor-ish chords, detuned saws, fades
chords = [[110, 164.8, 220, 261.6], [98, 146.8, 196, 246.9], [87.3, 130.8, 174.6, 220], [98, 146.8, 196, 246.9]]
seg = 4 * 60 / 100 * 2  # 2 bars at 100 bpm
pad = np.zeros(n)
for k in range(int(DUR / seg) + 1):
    a, b = int(k * seg * SR), min(n, int((k + 1) * seg * SR))
    if a >= n: break
    tt = t[a:b]
    for f in chords[k % 4]:
        for d in (-0.6, 0.6):
            pad[a:b] += ((tt * (f + d)) % 1 * 2 - 1)
pad = lp(pad[::4], 0.05).repeat(4)[:n] * 0.05
env = np.clip(t / 1.0, 0, 1) * np.where((t > 18.0) & (t < 19.0), 0.25, 1.0) * np.clip((DUR - t) / 1.5, 0, 1)
mix += pad * env
# pulse: soft kick on each beat (100 bpm), silent during the riser gap
beat = 0.6
kick_t = np.arange(int(0.25 * SR)) / SR
kick = np.sin(2 * np.pi * (45 + 100 * np.exp(-kick_t * 30)) * kick_t) * np.exp(-kick_t * 14)
for k in np.arange(0.0, DUR, beat):
    if not (18.0 < k < 19.2) and k < 25.6: add(kick, k, 0.35)
# whoosh
wl = int(0.45 * SR); w = rng.standard_normal(wl); w = lp(w, 0.15) * np.sin(np.linspace(0, np.pi, wl)) ** 2
for at in st['whoosh']: add(w, at - 0.2, 0.6)
# ticks
tl = int(0.06 * SR); tick = np.sin(2 * np.pi * 1200 * np.arange(tl) / SR) * np.exp(-np.arange(tl) / SR * 60)
for at in st['tick']: add(tick, at, 0.5)
# riser into reveal
r0, r1 = 17.8, 19.0; rl = int((r1 - r0) * SR); rt = np.arange(rl) / SR
riser = (lp(rng.standard_normal(rl), 0.3) * 0.5 + np.sin(2 * np.pi * (200 + 600 * rt / (r1 - r0)) * rt) * 0.3) * (rt / (r1 - r0)) ** 2
add(riser, r0, 0.5)
# stamp thuds
sl = int(0.35 * SR); stt = np.arange(sl) / SR
thud = (np.sin(2 * np.pi * (60 + 80 * np.exp(-stt * 25)) * stt) * np.exp(-stt * 10) + lp(rng.standard_normal(sl), 0.4) * np.exp(-stt * 30) * 0.6)
for at in st['stamp']: add(thud, at, 0.9)
# REAL hit: thud + bright chord
hl = int(1.6 * SR); ht = np.arange(hl) / SR
hit = thud.copy(); bright = sum(np.sin(2 * np.pi * f * ht) for f in (440, 554.4, 659.3, 880)) * np.exp(-ht * 2.5) * 0.25
add(hit, st['real'][0], 1.1); add(bright, st['real'][0], 0.8)
# pop at start
add(thud * 0.6, 0.02, 0.6)
mix /= np.max(np.abs(mix)) * 1.1
pcm = (np.stack([mix, mix], 1) * 32767).astype('<i2')
with wave.open('out/score.wav', 'wb') as f:
    f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR); f.writeframes(pcm.tobytes())
print('score ok', DUR)
