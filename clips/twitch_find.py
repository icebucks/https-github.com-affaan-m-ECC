"""List live Twitch streams in a category (default: Grand Theft Auto VI), filtered by language, sorted by viewers.
  python3 clips/twitch_find.py [--game "Grand Theft Auto VI"] [--lang en] [--n 25] [--tag NoCommentary]"""
import argparse, json, urllib.request

CLIENT_ID = "kimne78kx3ncx6brgo4mv6wki5h1ko"     # Twitch's public web client id (what twitch.tv itself sends)
Q = """query($name: String!, $n: Int!, $tags: [String!]) { game(name: $name) { id displayName viewersCount
  streams(first: $n, options: {freeformTags: $tags}) { edges { node { title viewersCount createdAt
    broadcaster { login displayName broadcastSettings { language } } } } } } }"""


def live(game, n, tags=None):
    body = json.dumps({"query": Q, "variables": {"name": game, "n": n, "tags": tags}}).encode()
    req = urllib.request.Request("https://gql.twitch.tv/gql", body, {"Client-Id": CLIENT_ID, "Content-Type": "application/json"})
    d = json.load(urllib.request.urlopen(req, timeout=20))
    if d.get("errors"): raise SystemExit(d["errors"])
    return d["data"]["game"]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--game", default="Grand Theft Auto VI")
    ap.add_argument("--lang", default="en")
    ap.add_argument("--n", type=int, default=100)
    ap.add_argument("--tag", action="append", help="freeform tag filter, e.g. NoCommentary (repeatable)")
    A = ap.parse_args()
    g = live(A.game, A.n, A.tag)
    if not g: raise SystemExit(f"category not found: {A.game}")
    print(f"{g['displayName']}: {g['viewersCount']:,} viewers total")
    for e in g["streams"]["edges"]:
        s = e["node"]; b = s["broadcaster"]
        lang = (b.get("broadcastSettings") or {}).get("language", "")
        if A.lang and lang.lower() != A.lang.lower(): continue
        print(f"{s['viewersCount']:>8,}  {b['login']:<22} {lang:<3} since {s['createdAt'][11:16]} UTC | {s['title'][:80]}")
