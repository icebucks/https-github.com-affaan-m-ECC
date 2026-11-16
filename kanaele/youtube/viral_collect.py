"""Collect public YouTube Shorts listings for /yt-viral (swipe.py): search queries -> top channels -> their last 30 Shorts.
Usage: python3 viral_collect.py out.json "query one" "query two" ...  then: python3 ../../.claude/skills/yt-viral/swipe.py out.json --min 2.0
Reads public listings only (yt-dlp --flat-playlist), never logs in."""
import json, subprocess, sys, collections
OUT, QUERIES = sys.argv[1], sys.argv[2:]
def yd(url, n):
    r = subprocess.run(["yt-dlp", url, "--flat-playlist", "-J", "--playlist-end", str(n)], capture_output=True, text=True, timeout=180)
    try: return json.loads(r.stdout) or {"entries": []}
    except Exception: return {"entries": []}
chans = collections.Counter()
for q in QUERIES:
    for e in (x for x in yd(f"ytsearch20:{q}", 20).get("entries", []) if x):
        if e.get("channel_id"): chans[e["channel_id"]] += 1
rows = []
for cid, _ in chans.most_common(12):
    d = yd(f"https://www.youtube.com/channel/{cid}/shorts", 30)
    name = d.get("channel") or d.get("uploader") or cid; n0 = len(rows); seen = set()
    for e in (x for x in d.get("entries", []) if x):
        if e.get("view_count") is None or e.get("id") in seen: continue
        seen.add(e.get("id"))
        rows.append(dict(channel=name, title=e.get("title") or "", views=e["view_count"],
                         url=e.get("url") or f"https://www.youtube.com/shorts/{e.get('id')}", duration=e.get("duration") or 0))
    print(name, len(rows) - n0, file=sys.stderr)
json.dump(rows, open(OUT, "w"), indent=1)
