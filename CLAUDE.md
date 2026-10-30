# compandgrow-studio — playbook

This repo runs Jazzy's Instagram account **@compandgrow**. Claude has full control of content and posting. Read `plan/CONTENT_PLAN.md` first: target, cadence, topic queue, post log, and the never-list.

## Weekly run (Monday, scheduled) — run by the reel team
Run the **`weekly-run` skill** (`.claude/skills/weekly-run/SKILL.md`). It runs the agents in `.claude/agents/` in order:
performance-analyst → slot-planner → topic-scout → researcher → scriptwriter → producer → cutdown-editor → reviewer → publisher, then reports to Jazzy.
- Format (length, hook rule, slots, cut hook types, style tests, posting time): `config/format.json`. The performance-analyst may tune `tunable`, one change per version; `locked` changes need Jazzy.
- Account + media hosting: `config/account.json`. Post records: `data/posts.json` (machine-readable) mirrored in the post log in `plan/CONTENT_PLAN.md`.
- 24 h reviews and learnings: `data/performance/` (`python3 studio/tools/performance.py due|save|table`).
- Media hosting details the publisher follows: commit to `media/<YYYY>-w<WW>/` on `main`, jsDelivr URL pinned to the commit
  (`https://cdn.jsdelivr.net/gh/compandgrow/compandgrow-studio@<commit>/media/<dir>/<file>.mp4`); 20 MB limit (`studio/tools/cutdown.py --full`);
  raw.githubusercontent serves the wrong type and GitHub Releases are blocked; if `validate_media` 403s, try the `sexyjazzy/...` alias or another commit seen in `git log`.

**Before producing anything:** check the post log and `posts_list` for slots already filled in the coming week. Never double-book a slot. If this week's Sunday film is already scheduled, use the run to fill open cutdown slots and get ahead on next week's film.

## Producing a film
- `sh studio/setup.sh` → prints `LIB=` and `PLAYWRIGHT_CHROME=`; export both.
- Style for the film: see "Style testing" in CONTENT_PLAN.md. For a new Lemo-Opuscar style, read `$LIB/styles/<slug>/STYLE.md` (and its demo only after writing the treatment), adapt the demo engine to 1080×1920 the way `studio/kit/board.js` was adapted (W/H constants, Latin fonts, English one-line subtitles, `window.MBCAP`), and save the adapted kit as `studio/kits/<slug>/` so later runs reuse it.
- New film = copy the closest `studio/films/<film>/` to a new folder, then:
  - fact-check every historical claim on the web and write `FACTS.md` (claim → source URL);
  - write `audio/lines.json` (TTS text, numbers spelled out, voice `bm_george`, speed .95) and `audio/subs.json` (subtitle text, digits);
  - `"$LIB/.venv/bin/python" "$LIB/core/tts/tts.py" <film>/audio/lines.json <film>/audio/vo`;
  - adapt `scenes/_gen_film.py` (layout + camera; helpers in `studio/tools/helpers.py`); keep the right third (x > 2700) unseen until the final pull-back; key content inside the 9:16 safe area, above the subtitle strip.
- Storyboard: `node core/render/still.mjs films/<n> <t1> <t2> ... --size 1080x1920` from `$LIB`; tile, look, fix collisions/crops.
- Render: `node core/render/video.mjs films/<n> --fps 24 --workers 2 --size 1080x1920 --out films/<n>/out/video.mp4` (index.html sets `window.MBCAP = 8` — keeps renders ~45 min on 2 cores). If a run is cut short, `studio/tools/tail.mjs` / `fwd.mjs` render frame ranges to JPEGs.
- Cutdowns / full-film upload encode: `python3 studio/tools/cutdown.py <film.mp4> <out.mp4> a:b [c:d ...]` and `--full <film.mp4> <out.mp4>`.
- Mix: `"$LIB/.venv/bin/python" films/<n>/audio/mix.py` (edit section times + section keys); `sh core/render/mux.sh video.mp4 mix.wav <n>.mp4 24 1`.
- Check: contact sheet (`fps=0.5,tile`), loudness ≈ −14 LUFS, no black frames, subtitles readable.

## Rules
- Every real-world claim sourced; the fictional program, specs and trials are invented and never attributed to real agencies or people.
- Never-list in CONTENT_PLAN.md. No logos, no player/celebrity photos, no AI video.
- Ask Jazzy before: changing the account's niche, renaming the handle, anything involving money, or a topic near the never-list.
- Commit messages end with the session attribution lines given in the session.
