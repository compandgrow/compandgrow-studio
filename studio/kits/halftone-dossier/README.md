# Halftone Dossier kit (1080×1920)

Adapted from Lemo-Opuscar `styles/halftone-dossier/demo/index.html` for @compandgrow: vertical frame, Latin fonts
(Alfa Slab One headlines, Bagel Fat One numerals, JetBrains Mono 800 HUD, Archivo 900 captions/stamps, Chewy bubbles),
narration-driven caption bar (`buildCaptions(subs)`; mark keywords with `*stars*`, wraps to two balanced lines),
HUD below the Reels top bar, captions centred at y 1500 (above the Reels bottom UI), SFX cue export (`sfx()` → `window.SFX`,
dump with `studio/tools/sfxdump.mjs`). A film imports `./kit/dossier.js`, builds scenes with `scene(t0, t1, build)` and calls `boot()`.
Set `KIT` = `halftone-dossier` in the film folder so `studio/setup.sh` copies this kit in as `kit/`.
First used by `studio/films/lodestone` (film #4).
