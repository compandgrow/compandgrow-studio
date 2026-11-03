#!/bin/sh
# Build a cards-kit piece:  sh studio/kits/cards/build.sh studio/films/<piece>   (the folder holds data.js)
# Writes <piece>/out/<piece>.mp4 (1080x1920, ~-14 LUFS). Probe stills first: PROBE="0 3 8" sh build.sh <piece>
set -e
KIT=$(cd "$(dirname "$0")" && pwd); P=$(cd "$1" && pwd); N=$(basename "$P")
cp "$KIT/index.html" "$KIT/render.mjs" "$KIT/audio.py" "$P/"; rm -rf "$P/fonts"; cp -r "$KIT/fonts" "$P/fonts"
export PW=$(node -e "console.log(require.resolve('playwright'))")
cd "$P"
if [ -n "$PROBE" ]; then node render.mjs probe $PROBE; echo "$P/out/probe.jpg"; exit 0; fi
node render.mjs full && python3 audio.py
ffmpeg -v error -y -i out/video.mp4 -i out/score.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k \
  -af "loudnorm=I=-14:TP=-1.3:LRA=11,volume=1.4dB,alimiter=limit=0.89" -shortest -movflags +faststart "out/$N.mp4"
ffmpeg -i "out/$N.mp4" -af ebur128 -f null - 2>&1 | grep "I:" | tail -1
ffmpeg -v error -y -i "out/$N.mp4" -vf fps=1,scale=180:-1,tile=10x3 -frames:v 1 out/review.jpg
echo "$P/out/$N.mp4"
