#!/usr/bin/env python3
"""24-hour performance data for @compandgrow Reels (the judging is done by the performance-analyst agent).

  python3 studio/tools/performance.py due                   -> posts 24 h+ old with no review yet (JSON)
  python3 studio/tools/performance.py save <post_id> <file> -> data/performance/<post_id>.json from a saved
                                                               Zernio analytics_get_analytics response (one post)
  python3 studio/tools/performance.py table                 -> every reviewed Reel: metrics, features, medians,
                                                               plus medians per hook type, style and kind

<post_id> is the `id` in data/posts.json (e.g. ember-cut-number), not the Zernio id.
Metrics come from Zernio (Instagram insights). Features come from data/posts.json and the film folder
(subtitles .srt, KIT, lines.json) so the analyst can compare what was made with how it did.
"""
import ast, datetime as dt, glob, json, os, re, statistics, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA = os.path.join(ROOT, "data")
PERF = os.path.join(DATA, "performance")
FILMS = os.path.join(ROOT, "studio", "films")
NUM_WORDS = r"\b(zero|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|hundred|thousand|million)\b"
KEYS = ["views", "reach", "avg_watch_s", "watch_ratio", "skip_rate", "completion_rate",
        "engagements_per_1k_reach", "shares_saves_per_1k_reach", "follows", "follows_per_1k_reach"]


def now():
    return dt.datetime.now(dt.timezone.utc).replace(tzinfo=None)


def ts(s):
    if not s:
        return None
    t = dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
    return t.astimezone(dt.timezone.utc).replace(tzinfo=None) if t.tzinfo else t


def load(path, default=None):
    try:
        return json.load(open(path))
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def posts():
    return load(os.path.join(DATA, "posts.json"), {"posts": []})["posts"]


def srt(film):
    """Subtitle cues of a film: [(start_s, end_s, text)]."""
    files = glob.glob(os.path.join(FILMS, film, "*.srt"))
    if not files:
        return []
    cues = []
    for block in re.split(r"\n\s*\n", open(files[0], encoding="utf-8").read().strip()):
        m = re.search(r"(\d+):(\d+):(\d+)[,.](\d+)\s*-->\s*(\d+):(\d+):(\d+)[,.](\d+)\s*\n(.*)", block, re.S)
        if m:
            g = [int(x) for x in m.groups()[:8]]
            a = g[0] * 3600 + g[1] * 60 + g[2] + g[3] / 1000
            b = g[4] * 3600 + g[5] * 60 + g[6] + g[7] / 1000
            cues.append((a, b, " ".join(m.group(9).split())))
    return cues


def features(p):
    film = p.get("film") or ""
    kit = os.path.join(FILMS, film, "KIT")
    cues = srt(film)
    start = 0.0
    if p.get("kind") == "cut" and p.get("segments"):
        start = float(str(p["segments"][0]).split(":")[0])
    opening = [c for c in cues if c[1] > start][:3]
    first = opening[0][2] if opening else ""
    first3s = " ".join(c[2] for c in opening if c[0] < start + 3)
    caption = ""
    for f in glob.glob(os.path.join(FILMS, film, "captions", f"{p['id']}.txt")):
        caption = open(f, encoding="utf-8").read()
    return {
        "kind": p.get("kind"),
        "film": film,
        "hook_type": p.get("hook_type"),
        "style": p.get("style") or (open(kit).read().strip() if os.path.exists(kit) else "board"),
        "label": p.get("label"),
        "first_line": first,
        "words_in_first_3s": len(first3s.split()),
        "first_line_has_number": bool(re.search(r"\d", first) or re.search(NUM_WORDS, first, re.I)),
        "first_line_is_question": first.strip().endswith("?"),
        "segments": p.get("segments"),
        "format_version": p.get("format_version"),
        "experiment": p.get("experiment"),
        "caption_first_line": caption.strip().split("\n")[0] if caption else None,
    }


def cmd_due():
    out = []
    for p in posts():
        if not p.get("zernio_post") or p.get("status") in ("failed", "cancelled"):
            continue
        t = ts(p.get("published_at") or p.get("scheduled_for"))
        if not t or now() - t < dt.timedelta(hours=24):
            continue
        if os.path.exists(os.path.join(PERF, f"{p['id']}.review.md")):
            continue
        out.append({"id": p["id"], "zernio_post": p["zernio_post"], "kind": p["kind"], "posted": t.isoformat() + "Z",
                    "hours_since": round((now() - t).total_seconds() / 3600, 1)})
    print(json.dumps(out, indent=1))


def metrics(resp):
    a = resp.get("analytics", resp)
    dur = a.get("videoDurationSeconds")
    curve = a.get("retentionCurve") or None
    completion = a.get("completionRate")
    if completion == 0 and not curve:
        completion = None           # Instagram often sends 0 when it has no completion data
    watch = (a.get("igReelsAvgWatchTime") or 0) / 1000
    views, reach = a.get("views") or 0, a.get("reach") or 0
    eng = sum((a.get(k) or 0) for k in ("likes", "comments", "shares", "saves"))
    per1k = lambda x: round(x * 1000 / reach, 1) if reach else None
    return {
        "views": views, "reach": reach, "likes": a.get("likes"), "comments": a.get("comments"),
        "shares": a.get("shares"), "saves": a.get("saves"), "follows": a.get("follows"),
        "profile_views": a.get("profileViews"), "replays": a.get("replays"),
        "avg_watch_s": round(watch, 2), "video_s": dur,
        "watch_ratio": round(watch / dur, 3) if dur else None,
        "skip_rate": a.get("reelsSkipRate"), "completion_rate": completion,
        "engagements_per_1k_reach": per1k(eng),
        "shares_saves_per_1k_reach": per1k((a.get("shares") or 0) + (a.get("saves") or 0)),
        "follows_per_1k_reach": per1k(a.get("follows")) if isinstance(a.get("follows"), (int, float)) else None,
        "retention_curve": curve,
        "url": a.get("platformPostUrl") or resp.get("platformPostUrl"),
        "last_updated": a.get("lastUpdated"),
    }


def cmd_save(pid, path):
    raw = open(path).read().strip()
    try:
        resp = json.loads(raw)
    except json.JSONDecodeError:
        resp = ast.literal_eval(raw)        # the MCP tool can return a Python-style dict string
    if isinstance(resp, dict) and isinstance(resp.get("result"), str):
        try:
            resp = json.loads(resp["result"])
        except json.JSONDecodeError:
            resp = ast.literal_eval(resp["result"])
    p = next((x for x in posts() if x["id"] == pid), None)
    if not p:
        sys.exit(f"{pid} is not in data/posts.json")
    posted = ts(resp.get("publishedAt") or p.get("published_at") or p.get("scheduled_for"))
    m = metrics(resp)
    upd = ts(m.get("last_updated"))
    pt = posted.replace(tzinfo=dt.timezone.utc).astimezone(__import__("zoneinfo").ZoneInfo("America/Los_Angeles")) if posted else None
    out = {"id": pid, "zernio_post": p.get("zernio_post"),
           "posted_at": posted.isoformat() + "Z" if posted else None,
           "post_hour_pt": pt.hour if pt else None, "post_weekday": pt.strftime("%a") if pt else None,
           "snapshot_at": now().isoformat(timespec="seconds") + "Z",
           "hours_since_post": round((now() - posted).total_seconds() / 3600, 1) if posted else None,
           "data_age_h": round((upd - posted).total_seconds() / 3600, 1) if upd and posted else None,
           "metrics": m, "features": features(p)}
    os.makedirs(PERF, exist_ok=True)
    json.dump(out, open(os.path.join(PERF, f"{pid}.json"), "w"), indent=1, ensure_ascii=False)
    print(json.dumps({**{k: v for k, v in m.items() if k != "retention_curve"}, "data_age_h": out["data_age_h"]}, indent=1))


def medians(rows):
    med = {}
    for k in KEYS:
        vals = [r["metrics"][k] for r in rows if isinstance(r["metrics"].get(k), (int, float))]
        med[k] = round(statistics.median(vals), 3) if vals else None
    return med


def cmd_table():
    rows = [load(os.path.join(PERF, f)) for f in sorted(os.listdir(PERF))
            if f.endswith(".json") and not f.startswith("_")] if os.path.isdir(PERF) else []
    rows = [r for r in rows if r and "metrics" in r]
    groups = {}
    for dim in ("kind", "hook_type", "style"):
        g = {}
        for r in rows:
            g.setdefault(str(r["features"].get(dim)), []).append(r)
        groups[dim] = {k: {"n": len(v), **medians(v)} for k, v in g.items()}
    print(json.dumps({
        "reels_reviewed": len(rows), "channel_median": medians(rows), "by": groups,
        "reels": [{"id": r["id"], "posted_at": r["posted_at"], "hour_pt": r["post_hour_pt"], "weekday": r["post_weekday"],
                   "data_age_h": r.get("data_age_h"), "metrics": {k: r["metrics"].get(k) for k in KEYS},
                   **{k: r["features"].get(k) for k in ("kind", "film", "style", "hook_type", "first_line", "words_in_first_3s", "format_version", "experiment")}}
                  for r in rows]}, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "due":
        cmd_due()
    elif cmd == "save" and len(sys.argv) == 4:
        cmd_save(sys.argv[2], sys.argv[3])
    elif cmd == "table":
        cmd_table()
    else:
        sys.exit(__doc__)
