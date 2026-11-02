#!/bin/sh
# One command, from this folder: rebuilds STILLWING from source (LIB = Lemo-Opuscar library folder; this film linked as $LIB/films/lifter with kit = studio/kits/exploded-teardown).
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
LIB=${LIB:-$(cd "$HERE/../.." && pwd)}
export LIB
[ -f "$LIB/core/render/video.mjs" ] || { echo "set LIB to the Lemo-Opuscar library folder"; exit 1; }
cd "$LIB"
"$LIB/.venv/bin/python" core/tts/tts.py "$HERE/audio/lines.json" "$HERE/audio/vo"
python3 "$HERE/scenes/_gen_timeline.py"
node "${STUDIO:?set STUDIO to the repo studio/ folder}/tools/sfxdump.mjs" "$HERE" "$HERE/audio/sfx.json"
node core/render/video.mjs "$HERE" --fps 24 --workers 1 --size 1080x1920 --out "$HERE/out/video.mp4"
"$LIB/.venv/bin/python" "$HERE/audio/mix.py"
"$LIB/.venv/bin/python" core/render/srt.py "$HERE/audio/cues.json" "$HERE/lifter.srt"
sh core/render/mux.sh "$HERE/out/video.mp4" "$HERE/out/mix.wav" "$HERE/out/lifter.mp4" 24 1
