# compandgrow-studio — playbook

This repo runs Jazzy's Instagram account **@compandgrow**. Claude has full control of content and posting. Read `plan/CONTENT_PLAN.md` first: target, cadence, topic queue, post log, and the never-list.

## Weekly run (Monday, scheduled)
1. **Analyze.** Zernio connector: `analytics_get_analytics` (account `6ad2b0ba41b89dd24d24a501`, last 14 days), `accounts_get_follower_stats`. Per Reel: views, reach, avg watch time, skip rate, saves, shares, follows. Compare against the pace line.
2. **Report** to Jazzy (5–8 lines): followers vs pace, best and worst Reel and why, what changes this week.
3. **Decide** this week's film topic and the 4 cutdown hooks; update the topic queue.
4. **Produce** the film (below), then 4 cutdowns with ffmpeg (trim + 2.2 s end card "FULL BRIEFING / on @compandgrow").
5. **Publish media**: commit to `media/<YYYY>-w<WW>/` and push to `main`. Use the jsDelivr URL pinned to the commit:
   `https://cdn.jsdelivr.net/gh/sexyjazzy/compandgrow-studio@<commit>/media/<dir>/<file>.mp4`
   - jsDelivr serves `video/mp4` (raw.githubusercontent serves octet-stream: don't use it). **jsDelivr's GitHub file limit is 20 MB**: encode full films for upload with `python3 studio/tools/cutdown.py --full <film.mp4> <out.mp4>` (CRF 26, maxrate 1.1M, AAC 112k ≈ 14 MB for 2 min) to stay under it; check with `validate_media` before scheduling.
   - GitHub Releases are blocked for these sessions; don't try them.
6. **Schedule** 5 posts with `posts_create` (`account_id` above, `schedule_minutes`), default 4:28 pm PT; adjust with `analytics_get_best_time_to_post` once there is data.
7. **Log** every post in the post log, commit, push.

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
