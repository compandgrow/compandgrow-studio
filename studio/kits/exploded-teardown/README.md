# Exploded Teardown kit (1080×1920)

Adapted from Lemo-Opuscar `styles/teardown/demo/` (src/main.js + src/overlay.js) for @compandgrow: three.js PBR object on a graphite
seamless, anchored labels (accent two-digit index · name · one spec line, on a dark plate), perspective dimension lines, monotone camera
keys `[t, eye, target, fov, shiftX, shiftY]`, stamps and title blocks in screen space, English one-line subtitles centred at y 1500
(auto-fit to 960 px, `*stars*` = accent words), `window.SFX` cues for the mix (dump with `studio/tools/sfxdump.mjs`).
Fonts: Archivo (names, captions, stamps) and IBM Plex Mono (specs, numbers), both OFL, from `studio/kit/fonts`.

Render budget changes vs the demo (this machine has software GL only, SwiftShader on 2 cores):
no GTAO / depth of field / bloom / 2× supersampling (MSAA at 1×, additive glow meshes for emitters, a 2D vignette),
RoomEnvironment PMREM instead of the studio HDRI, one 2048 shadow map that follows the camera target,
`window.MBCAP` caps motion-blur sub-frames (the film can lower it per shot with `mbAt(t)`), low-detail InstancedMesh for repeated parts.
Measured: 0.45–1.6 s per frame single page; SwiftShader already uses both cores, so render with `--workers 1`.

A film imports `./kit/teardown.js`, builds its scene in `build()`, poses it in `update(t)` (returns the camera from `camTrack`),
draws marks in `marks(t)` and calls `K.boot({ dur, build, update, marks, cam })`. Set `KIT` = `exploded-teardown` in the film folder.
First used by `studio/films/lifter` (film #6, STILLWING).
