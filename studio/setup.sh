#!/bin/sh
# Rebuild the @compandgrow film studio in a fresh workspace (about 5 minutes).
#   sh studio/setup.sh            -> prints LIB=<path> on its last line
# Needs: node 20+, ffmpeg, python3.11+, git. Chromium: set PLAYWRIGHT_CHROME if the library can't download its own.
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
LIB=${LIB:-/tmp/lemo-opuscar}
if [ ! -d "$LIB/.git" ]; then git clone -q --depth 1 https://github.com/lemomo-ai/lemo-opuscar.git "$LIB"; fi
cd "$LIB"
[ -d node_modules/playwright-core ] || npm install --silent --no-audit --no-fund
if [ ! -x .venv/bin/python ]; then python3 -m venv .venv; fi
.venv/bin/python -m pip install --quiet --disable-pip-version-check -r requirements.txt -r requirements-voice.txt
[ -f core/tts/kokoro-v1.0.onnx ] || sh tools/fetch.sh voice
for l in freepats vsco2ce vcsl; do [ -d "core/audio/instruments/$l" ] || sh tools/fetch.sh instruments $l; done
# headless shell: prefer a preinstalled one
if [ -z "$PLAYWRIGHT_CHROME" ]; then
  for c in /opt/pw-browsers/chromium_headless_shell-*/chrome-linux/headless_shell; do [ -x "$c" ] && PLAYWRIGHT_CHROME=$c; done
fi
[ -n "$PLAYWRIGHT_CHROME" ] || node node_modules/playwright-core/cli.js install chromium-headless-shell
# link every film into the library, each with its own copy of its kit (studio/kit, or studio/kits/<slug> when the film has a KIT file)
mkdir -p "$LIB/films"
for f in "$HERE"/films/*/; do
  n=$(basename "$f"); rm -rf "$LIB/films/$n"; cp -r "$f" "$LIB/films/$n"; k="$HERE/kit"; [ -f "$f/KIT" ] && k="$HERE/kits/$(cat "$f/KIT")"; cp -r "$k" "$LIB/films/$n/kit"
  mkdir -p "$LIB/films/$n/out" "$LIB/films/$n/stills"
done
echo "PLAYWRIGHT_CHROME=$PLAYWRIGHT_CHROME"
echo "LIB=$LIB"
