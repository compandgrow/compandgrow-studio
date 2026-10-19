#!/usr/bin/env python3
"""LODESTONE — narration timeline -> scenes/timeline.json (line start times, subtitles, duration).
The picture (index.html) and the mix (audio/mix.py) both read this file."""
import json, math, os
HERE = os.path.dirname(os.path.abspath(__file__)); FILM = os.path.dirname(HERE)
VO = json.load(open(os.path.join(FILM, 'audio', 'vo', 'dur.json')))
SUB = json.load(open(os.path.join(FILM, 'audio', 'subs.json')))
BPM = 120; BEAT = 60 / BPM; SIX = BEAT / 4
# (line, gap before it). Bigger gaps open a new exhibit (room for the dot wipe and the headline).
ORDER = [('a1', .5), ('a2', .15), ('a3', .15),
         ('b1', .8), ('b2', .2), ('b3', .2),
         ('c1', .9), ('c2', .2), ('c3', .15),
         ('d1', .9), ('d2', .05), ('d3', .5),
         ('e1', .9), ('e2', .3), ('e3', .2), ('e4', .25), ('e5', .25),
         ('f2', .8),
         ('g1', .8), ('g2', .7), ('g3', .3), ('g4', .7), ('g5', .3), ('g6', .7), ('g7', .4),
         ('h1', .8), ('h2', .3),
         ('i1', .8), ('i2', .2),
         ('j1', .8), ('j2', .3)]
T = {}; t = 0.0; prev_end = 0.0
for k, gap in ORDER:
    t0 = max(prev_end + gap, t); t0 = round(math.ceil(t0 / SIX - 1e-9) * SIX, 4)
    T[k] = t0; prev_end = t0 + VO[k]; t = t0 + max(1.8, VO[k] + .5)
END = lambda k: T[k] + VO[k]
DUR = round(END('j2') + 3.0, 3)
subs = []; keys = [k for k, _ in ORDER]
for i, k in enumerate(keys):
    t0 = T[k]; t1 = t0 + max(1.8, VO[k] + .6)
    if i + 1 < len(keys): t1 = min(t1, T[keys[i + 1]] - .02)
    if t1 - t0 < 1.78: print('WARNING short subtitle', k, round(t1 - t0, 2))
    subs.append(dict(id=k, t0=round(t0, 3), t1=round(t1, 3), text=SUB[k]))
json.dump(dict(T=T, VO=VO, DUR=DUR, BPM=BPM, subs=subs), open(os.path.join(HERE, 'timeline.json'), 'w'), indent=1)
json.dump([dict(t0=s['t0'], t1=s['t1'], text=s['text'].replace('*', '')) for s in subs], open(os.path.join(FILM, 'audio', 'cues.json'), 'w'), indent=1)
print('DUR', DUR, {k: T[k] for k in ('b1', 'c1', 'd1', 'e1', 'f2', 'g1', 'g2', 'g4', 'g6', 'h1', 'i1', 'j1')})
