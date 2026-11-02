#!/usr/bin/env python3
"""STILLWING — narration timeline -> scenes/timeline.json (line start times, subtitles, duration) and audio/cues.json.
The picture (index.html), the mix (audio/mix.py) and out/timing.json all read this file. Re-run after TTS."""
import json, math, os
HERE = os.path.dirname(os.path.abspath(__file__)); FILM = os.path.dirname(HERE)
VO = json.load(open(os.path.join(FILM, 'audio', 'vo', 'dur.json')))
SUB = json.load(open(os.path.join(FILM, 'audio', 'subs.json')))
FR = 1 / 24
# (line, gap before it in s). Big gaps = near-silences (room tone) and new sections.
ORDER = [('a1', .25), ('a2', .15), ('a3', .25), ('a4', .3), ('a5', .25),
         ('b1', .9), ('b2', .2), ('b3', .2),                       # 1.0 after a5 = first near-silence + the separation hit
         ('c1', .55), ('c2', .2), ('c3', .25), ('c4', .4), ('c5', .2), ('c6', .2), ('c7', .2), ('c8', .35), ('c9', .3),
         ('c10', .5), ('c11', .2),
         ('d1', .85), ('d2', .2), ('d3', .25), ('d4', .2),            # 1.0 after c11 = second near-silence
         ('e1', .55), ('e2', .15), ('e3', .45), ('e4', .15), ('e5', .45), ('e6', .25),
         ('f1', .75), ('f2', .2), ('f3', .2), ('f4', .25), ('f5', .3),
         ('g1', .9), ('g2', .25), ('g3', .25),                         # 1.0 before g1 = third near-silence, then the stamp
         ('h1', .6), ('h2', .35)]
T = {}; prev_end = 0.0; prev_t = -9
for k, gap in ORDER:
    t0 = max(prev_end + gap, prev_t + 1.8)          # subtitles hold at least 1.8 s
    t0 = round(math.ceil(t0 / FR - 1e-9) * FR, 4)
    T[k] = t0; prev_end = t0 + VO[k]; prev_t = t0
T['a1'] = 0.25
END = lambda k: T[k] + VO[k]
DUR = round(math.ceil((END('h2') + 2.8) / FR) * FR, 4)
subs = []; keys = [k for k, _ in ORDER]
for i, k in enumerate(keys):
    t0 = T[k]; t1 = t0 + max(1.8, VO[k] + .6)
    if i + 1 < len(keys): t1 = min(t1, T[keys[i + 1]] - .04)
    if t1 - t0 < 1.76: print('WARNING short subtitle', k, round(t1 - t0, 2))
    subs.append(dict(id=k, t0=round(t0, 3), t1=round(t1, 3), text=SUB[k]))
json.dump(dict(T=T, VO=VO, DUR=DUR, subs=subs), open(os.path.join(HERE, 'timeline.json'), 'w'), indent=1)
json.dump([dict(t0=s['t0'], t1=s['t1'], text=s['text'].replace('*', '')) for s in subs], open(os.path.join(FILM, 'audio', 'cues.json'), 'w'), indent=1)
# measured spoken windows of every line, for the cutdown editor
os.makedirs(os.path.join(FILM, 'out'), exist_ok=True)
json.dump(dict(fps=24, dur=DUR, note='start = voice onset, end = voice end (s, film time); sub_t1 = subtitle off',
               lines={k: dict(start=T[k], end=round(END(k), 3), sub_t1=s['t1']) for k, s in zip(keys, subs)}),
          open(os.path.join(FILM, 'out', 'timing.json'), 'w'), indent=1)
print('DUR', DUR, {k: T[k] for k in ('b1', 'c1', 'c10', 'd1', 'e1', 'e6', 'f1', 'g1', 'h1', 'h2')})
