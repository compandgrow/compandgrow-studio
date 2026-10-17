#!/bin/sh
# One command, from this folder: rebuilds LONGSHOT from source.
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
LIB=${LIB:-$(cd "$HERE/../.." && pwd)}
export LIB
[ -f "$LIB/core/render/video.mjs" ] || { echo "set LIB to the Lemo-Opuscar library folder"; exit 1; }
cd "$LIB"
"$LIB/.venv/bin/python" core/tts/tts.py "$HERE/audio/lines.json" "$HERE/audio/vo"
python3 "$HERE/scenes/_gen_film.py"
node core/render/events.mjs "$HERE" --size 1080x1920
node core/render/video.mjs "$HERE" --fps 24 --workers 2 --size 1080x1920 --out "$HERE/out/video.mp4"
"$LIB/.venv/bin/python" "$HERE/audio/mix.py"
"$LIB/.venv/bin/python" core/render/srt.py "$HERE/audio/cues.json" "$HERE/longshot.srt"
sh core/render/mux.sh "$HERE/out/video.mp4" "$HERE/out/mix.wav" "$HERE/longshot.mp4" 24 1
