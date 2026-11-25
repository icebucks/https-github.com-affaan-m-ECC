"""Postiz public API client (schedule posts for TikTok / YouTube / Instagram … from one place).
Field names checked against the postiz-app source (gitroomhq/postiz-app, 25.11.2026):
  apps/backend/src/public-api/routes/v1/public.integrations.controller.ts, dtos/posts/create.post.dto.ts,
  dtos/posts/providers-settings/tiktok.dto.ts, youtube.settings.dto.ts

Auth: header `Authorization: <API key>` (raw key, NO "Bearer"). The key is never in this repo or in env vars:
it is a network secret on the environment for host api.postiz.com (the proxy adds the header).
Cloud: https://api.postiz.com/public/v1 (needs a paid/trial subscription) · self-hosted: set POSTIZ_URL.

  python3 clips/postiz.py me                       # check the key
  python3 clips/postiz.py integrations             # connected accounts: id | provider | name
  python3 clips/postiz.py upload <file>            # -> media id + path
  python3 clips/postiz.py tiktok <integration-id> <video.mp4> --caption-file c.txt --at 2026-11-26T12:30:00+01:00 [--direct] [--ai]
  python3 clips/postiz.py posts --from 2026-11-25 --to 2026-11-30
  python3 clips/postiz.py delete <post-id>

TikTok default = content_posting_method UPLOAD → lands as a DRAFT in the TikTok inbox at the scheduled time
(TikTok then ignores everything except the caption). `--direct` = DIRECT_POST (really publishes, with privacy,
AI label, comments on) – only use it when the person has agreed to automatic posting for that account."""
import argparse, json, os, sys
from datetime import datetime, timezone
import requests

BASE = os.environ.get("POSTIZ_URL", "https://api.postiz.com/public/v1").rstrip("/")
S = requests.Session()
S.headers["Authorization"] = os.environ.get("POSTIZ_DUMMY_KEY", "proxy-injects-the-real-key")   # replaced by the proxy


def call(method, path, **kw):
    r = S.request(method, BASE + path, timeout=kw.pop("timeout", 120), **kw)
    if r.status_code >= 400:
        sys.exit(f"HTTP {r.status_code} {method} {path}: {r.text[:400]}")
    return r.json() if r.text else {}


def upload(path):
    with open(path, "rb") as f:
        m = call("POST", "/upload", files={"file": (os.path.basename(path), f)}, timeout=900)
    return {"id": m["id"], "path": m["path"]}


def iso(at):
    return datetime.fromisoformat(at).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")


def tiktok(integration, video, caption, at, direct=False, ai=False, title=""):
    media = upload(video)
    settings = {"__type": "tiktok", "title": title[:90], "privacy_level": "PUBLIC_TO_EVERYONE",
                "duet": False, "stitch": False, "comment": True, "autoAddMusic": "no",
                "brand_content_toggle": False, "brand_organic_toggle": False,
                "video_made_with_ai": bool(ai), "content_posting_method": "DIRECT_POST" if direct else "UPLOAD"}
    body = {"type": "schedule", "date": iso(at), "shortLink": False, "tags": [],
            "posts": [{"integration": {"id": integration},
                       "value": [{"content": caption, "image": [media]}],
                       "settings": settings}]}
    return call("POST", "/posts", json=body)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["me", "integrations", "upload", "tiktok", "posts", "delete"])
    ap.add_argument("args", nargs="*")
    ap.add_argument("--caption-file"); ap.add_argument("--at"); ap.add_argument("--title", default="")
    ap.add_argument("--direct", action="store_true"); ap.add_argument("--ai", action="store_true")
    ap.add_argument("--from", dest="frm"); ap.add_argument("--to")
    x = ap.parse_args()
    if x.cmd == "me": print(json.dumps(call("GET", "/me"), indent=1))
    elif x.cmd == "integrations":
        for i in call("GET", "/integrations"):
            print(f"{i.get('id')} | {i.get('identifier') or i.get('providerIdentifier')} | {i.get('name')} | disabled={i.get('disabled')}")
    elif x.cmd == "upload": print(json.dumps(upload(x.args[0])))
    elif x.cmd == "tiktok":
        cap = open(x.caption_file).read().strip()
        print(json.dumps(tiktok(x.args[0], x.args[1], cap, x.at, x.direct, x.ai, x.title), indent=1))
    elif x.cmd == "posts":
        print(json.dumps(call("GET", "/posts", params={"startDate": iso(x.frm + "T00:00:00+00:00"),
                                                       "endDate": iso(x.to + "T23:59:59+00:00")}), indent=1)[:4000])
    elif x.cmd == "delete": print(call("DELETE", f"/posts/{x.args[0]}"))
