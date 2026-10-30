#!/usr/bin/env python3
"""Make a short Reel from a full film: one or more time ranges joined, plus a 2.2 s end card.
    python3 studio/tools/cutdown.py <film.mp4> <out.mp4> 0:24.6 [60.6:95.8 ...] [--card-y 1240] [--crf 22]
    --line2 'Sunday on @compandgrow': second line of the end card
    --card-y: top of the end card (1395 covers a caption bar centred at y 1500, as in the Halftone Dossier kit)
Also:  python3 studio/tools/cutdown.py --full <film.mp4> <out.mp4>   (re-encode a full film under 20 MB for jsDelivr)
"""
import subprocess, sys, os

FONT = '/usr/share/fonts/opentype/inter/Inter-Bold.otf'
if not os.path.exists(FONT):
    FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
CARD = 2.2

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode: sys.exit(r.stderr[-2000:])

def probe(p):
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p], capture_output=True, text=True)
    return float(r.stdout.strip())

def cutdown(src, out, segs, cy=1240, crf=22, line2='on @compandgrow'):
    fc, cat, tot = [], '', 0.0
    for i, s in enumerate(segs):
        a, b = map(float, s.split(':')); d = b - a
        fc.append(f'[0:v]trim={a}:{b},setpts=PTS-STARTPTS[v{i}]')
        fc.append(f'[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.06,afade=t=out:st={d - .25:.3f}:d=0.25[a{i}]')
        cat += f'[v{i}][a{i}]'; tot += d
    en = f"enable='gte(t,{tot:.3f})'"
    card = (f"drawbox=x=90:y={cy}:w=900:h=230:color=0x111318@0.88:t=fill:{en},"
            f"drawtext=fontfile={FONT}:text='FULL BRIEFING':fontsize=78:fontcolor=0xF4F1EB:x=(w-tw)/2:y={cy + 35}:{en},"
            f"drawtext=fontfile={FONT}:text='{line2}':fontsize=50:fontcolor=0xE0533A:x=(w-tw)/2:y={cy + 145}:{en}")
    fc.append(f'{cat}concat=n={len(segs)}:v=1:a=1[vc][ac]')
    fc.append(f'[vc]tpad=stop_mode=clone:stop_duration={CARD},{card}[v]')
    fc.append(f'[ac]apad=pad_dur={CARD}[a]')
    run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-filter_complex', ';'.join(fc), '-map', '[v]', '-map', '[a]',
         '-c:v', 'libx264', '-crf', str(crf), '-preset', 'medium', '-maxrate', '5M', '-bufsize', '10M', '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', out])

def full(src, out):
    run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-c:v', 'libx264', '-crf', '26', '-preset', 'slow', '-maxrate', '1.1M', '-bufsize', '2.2M',
         '-c:a', 'aac', '-b:a', '112k', '-movflags', '+faststart', out])

if __name__ == '__main__':
    a = sys.argv[1:]
    if a and a[0] == '--full': full(a[1], a[2]); out = a[2]
    else:
        opt = lambda k, d: (lambda i: (a.pop(i), a.pop(i))[1] if i >= 0 else d)(a.index(k) if k in a else -1)
        cy = int(opt('--card-y', 1240)); crf = int(opt('--crf', 22)); l2 = opt('--line2', 'on @compandgrow')
        cutdown(a[0], a[1], a[2:], cy, crf, l2); out = a[1]
    print(f'{os.path.basename(out)}  {probe(out):.1f} s  {os.path.getsize(out) / 1e6:.1f} MB')
