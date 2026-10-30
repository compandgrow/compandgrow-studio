---
name: weekly-run
description: Run the @compandgrow reel team — review last week's Reels, plan open slots, pick and research the next what-if film, script, render, cut 4 cutdowns, review, schedule on Instagram, and report to Jazzy. Use when asked to run the week, make the next film or cutdowns, or when the Monday scheduled run fires.
---
# Weekly run — @compandgrow reel team

Arguments: none (full run), `review` (steps 0–1 only: performance + slots, no production), `cuts <film>` (cut and schedule an existing film), or `film <topic>` (make one specific film).

Account: Instagram @compandgrow, Zernio `6ad2b0ba41b89dd24d24a501`. **Never** @thescoutbrief (`6ad5bc58ea5889c95a4c443b`).

## 0. Preflight (no setup needed)
- Read `plan/CONTENT_PLAN.md`, `config/format.json`, `config/account.json`.
- Run **`performance-analyst`** first, always, even if nothing will be produced.
- Run **`slot-planner`**. If `data/queue.json` has nothing to make and nothing to repair → commit records, report, stop.
- Only if a film must be made: `sh studio/setup.sh` (~5 min) and export `LIB` / `PLAYWRIGHT_CHROME`.

## 1. Team flow
| Step | Agent | Output | Gate |
|---|---|---|---|
| 1 | `performance-analyst` | `data/performance/*.review.md`, `learnings.md`, maybe `config/format.json` | — |
| 2 | `slot-planner` | `data/queue.json`, `data/posts.json` statuses | Zernio reachable, else schedule nothing |
| 3 | `topic-scout` | `studio/films/<slug>/PITCH.md` | never-list clear; else ask Jazzy and stop the film |
| 4 | `researcher` | `FACTS.md` (claim → URL + quote, fiction disclaimer) | every real claim sourced; unverifiable ones dropped |
| 5 | `scriptwriter` | `TREATMENT.md`, `audio/lines.json`, `audio/subs.json`, `captions/*.txt` | follows `format.json` (length, hook in 3 s, slot order) |
| 6 | `producer` | `out/<slug>.mp4`, `.srt`, scene sources | stills checked first; duration within format |
| 7 | `cutdown-editor` | `media/<YYYY>-w<WW>/<slug>-full.mp4` + 4 cuts, `cuts.json` | each cut opens on its hook, < 20 MB |
| 8 | `reviewer` | `studio/films/<slug>/review.md` | PASS per file. FIX → back to 5/6/7, max 2 rounds, then escalate |
| 9 | `publisher` | scheduled Zernio posts, repairs, `data/posts.json`, post log | PASS only; `validate_media` on every URL; no double-booking |

Files are the hand-off between agents; pass each agent the film slug and the paths it needs. Run agents one at a time in this order. For `cuts <film>` start at step 7; for `review` stop after step 2.

If a render can't finish in this run, schedule what passed (e.g. cuts of the previous film for open slots), leave the film folder committed, and say exactly where to resume.

## 2. Approval (`config/account.json → approval`, currently "auto")
- `auto`: after PASS the publisher schedules into the planned slot (4:28 pm PT). Jazzy can cancel in Zernio before it goes out.
- `ask`: Zernio drafts only.
- No Zernio tools in this session → post nothing; send the MP4s with SendUserFile and say so.

## 3. Finish
- Commit and push to `main`: `data/`, `config/`, `plan/CONTENT_PLAN.md` (post log, topic queue, Open work), `studio/films/<slug>/` sources (not `out/`, `vo/`, `stills/`), `studio/kits/` if a kit was built, and `media/` (already pushed by the publisher). Never force-push.
- Report to Jazzy (5–8 lines): followers vs pace line; best and worst Reel last week and the main reason; hook-type and style scoreboard in one line; any format change; what is scheduled next (dates); anything blocked or needing Jazzy.

## Rules
- Facts first: every real-world claim in FACTS.md with a source. The fiction is never attributed to real agencies or people.
- Never-list in CONTENT_PLAN.md. No logos, no real-person photos, no AI video.
- Ask Jazzy before changing the niche, renaming the handle, anything involving money, or a topic near the never-list.
