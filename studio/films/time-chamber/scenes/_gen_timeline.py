#!/usr/bin/env python3
"""LONGHOUR — narration timeline -> scenes/timeline.json (line start times, subtitles, duration), audio/cues.json and out/timing.json.
The picture (index.html), the mix (audio/mix.py) and the cutdown editor all read these. Re-run after TTS."""
import json, math, os
HERE = os.path.dirname(os.path.abspath(__file__)); FILM = os.path.dirname(HERE)
VO = json.load(open(os.path.join(FILM, 'audio', 'vo', 'dur.json')))
SUB = json.load(open(os.path.join(FILM, 'audio', 'subs.json')))
FR = 1 / 24
# (line, gap before it in s). Big gaps = near-silences (room tone), separations and visual payoffs.
ORDER = [('a1', .25), ('a2', .15), ('a3', .25),
         ('b1', .4), ('b2', .3),
         ('c1', 1.0),                                 # 1.0 after "Take it apart." = near-silence 1 + the separation
         ('c2', .3), ('c3', 1.7),                     # 1.7 = the two bench clocks drift apart on screen (payoff before physics)
         ('c4', .3), ('c5', .5), ('c6', .2),
         ('d1', .9),                                  # near-silence 2 before LONGHOUR
         ('d2', .3), ('d3', .4),
         ('e1', .6), ('e2', .5), ('e3', .5), ('e4', .2),
         ('f1', .7), ('f2', .8),                      # "One catch." then near-silence 3
         ('f3', .3), ('f4', .3), ('f5', .3), ('f6', .6),
         ('f7', 1.0), ('f8', .2),                     # near-silence 4, then the stamp
         ('g1', .8)]
T = {}; prev_end = 0.0; prev_t = -9
for k, gap in ORDER:
    t0 = max(prev_end + gap, prev_t + 1.8)            # subtitles hold at least 1.8 s
    t0 = round(math.ceil(t0 / FR - 1e-9) * FR, 4)
    T[k] = t0; prev_end = t0 + VO[k]; prev_t = t0
END = lambda k: T[k] + VO[k]
DUR = round(math.ceil((END('g1') + 2.6) / FR) * FR, 4)
subs = []; keys = [k for k, _ in ORDER]
for i, k in enumerate(keys):
    t0 = T[k]; t1 = t0 + max(1.8, VO[k] + .6)
    if i + 1 < len(keys): t1 = min(t1, T[keys[i + 1]] - .04)
    if t1 - t0 < 1.76: print('WARNING short subtitle', k, round(t1 - t0, 2))
    subs.append(dict(id=k, t0=round(t0, 3), t1=round(t1, 3), text=SUB[k]))
VOD = {k: VO[k] for k in keys}
json.dump(dict(T=T, VO=VOD, V={}, VS={}, DUR=DUR, subs=subs), open(os.path.join(HERE, 'timeline.json'), 'w'), indent=1)
json.dump([dict(t0=s['t0'], t1=s['t1'], text=s['text'].replace('*', '')) for s in subs], open(os.path.join(FILM, 'audio', 'cues.json'), 'w'), indent=1)
os.makedirs(os.path.join(FILM, 'out'), exist_ok=True)
json.dump(dict(fps=24, dur=DUR, note='start = voice onset, end = voice end (s, film time); sub_t1 = subtitle off',
               lines={k: dict(start=T[k], end=round(END(k), 3), sub_t1=s['t1']) for k, s in zip(keys, subs)}),
          open(os.path.join(FILM, 'out', 'timing.json'), 'w'), indent=1)
print('DUR', DUR, {k: T[k] for k in ('b1', 'c1', 'c3', 'd1', 'e1', 'e3', 'f1', 'f7', 'g1')})
