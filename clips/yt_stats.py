"""Virlix status + performance report (needs the token from clips/yt_auth.py: youtube.force-ssl + yt-analytics.readonly).
  python3 clips/yt_stats.py                 -> all uploads: type, status/schedule, views, likes, comments, + analytics (28 days)
  python3 clips/yt_stats.py --md out.md     -> same as a Markdown table (for clips/stats/<date>.md)
Analytics per video: views, average view duration, average % viewed, subscribers gained (YouTube needs ~1–2 days to fill these).
Shorts are detected by duration ≤ 60 s (or ≤ 180 s with #Shorts in the title)."""
import argparse, datetime as dt, os, re, sys
import requests
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import yt_upload

API = "https://www.googleapis.com/youtube/v3"


def get(url, tok, **params):
    r = requests.get(url, params=params, headers={"Authorization": f"Bearer {tok}"}, timeout=30)
    j = r.json()
    if r.status_code != 200: sys.exit(f"{url.split('/')[-1]}: HTTP {r.status_code} {j.get('error', {}).get('message', '')}")
    return j


def seconds(iso):
    m = re.fullmatch(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso or "")
    return sum(int(x or 0) * k for x, k in zip(m.groups(), (3600, 60, 1))) if m else 0


def uploads(tok):
    ch = get(f"{API}/channels", tok, part="contentDetails,snippet,statistics", mine="true")["items"][0]
    pl = ch["contentDetails"]["relatedPlaylists"]["uploads"]
    ids, page = [], None
    while True:
        j = get(f"{API}/playlistItems", tok, part="contentDetails", playlistId=pl, maxResults=50, **({"pageToken": page} if page else {}))
        ids += [i["contentDetails"]["videoId"] for i in j["items"]]
        page = j.get("nextPageToken")
        if not page: break
    vids = []
    for k in range(0, len(ids), 50):
        vids += get(f"{API}/videos", tok, part="snippet,status,statistics,contentDetails,liveStreamingDetails", id=",".join(ids[k:k + 50]))["items"]
    return ch, vids


def analytics(tok, ids, start, end):
    if not ids: return {}
    r = requests.get("https://youtubeanalytics.googleapis.com/v2/reports", headers={"Authorization": f"Bearer {tok}"}, timeout=30,
                     params={"ids": "channel==MINE", "startDate": start, "endDate": end, "dimensions": "video",
                             "metrics": "views,averageViewDuration,averageViewPercentage,subscribersGained",
                             "filters": "video==" + ",".join(ids), "maxResults": 200})
    j = r.json()
    if r.status_code != 200: return {"_error": j.get("error", {}).get("message", r.text[:200])}
    return {row[0]: row[1:] for row in j.get("rows", [])}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--md", default=None); ap.add_argument("--days", type=int, default=28)
    A = ap.parse_args()
    tok = yt_upload.access_token()
    ch, vids = uploads(tok)
    today = dt.date.today()
    an = analytics(tok, [v["id"] for v in vids], str(today - dt.timedelta(days=A.days)), str(today))
    rows = []
    for v in sorted(vids, key=lambda v: v["status"].get("publishAt") or v["snippet"]["publishedAt"]):
        d = seconds(v.get("contentDetails", {}).get("duration"))
        short = "#shorts" in v["snippet"]["title"].lower() or 0 < d <= 60
        st = v["status"]
        when = st.get("publishAt") or v["snippet"]["publishedAt"]
        state = "geplant" if st["privacyStatus"] == "private" and st.get("publishAt") else st["privacyStatus"]
        prem = v.get("liveStreamingDetails", {}).get("scheduledStartTime")
        if v["snippet"].get("liveBroadcastContent") == "upcoming" and prem:     # premiere: "public" but not live yet
            state, when = "Premiere", prem
        s = v.get("statistics", {})
        a = an.get(v["id"], [None] * 4) if "_error" not in an else [None] * 4
        rows.append(["Short" if short else "Video", v["snippet"]["title"][:48], state, when[:16].replace("T", " ") + " UTC",
                     s.get("viewCount", "0"), s.get("likeCount", "0"), s.get("commentCount", "0"),
                     f"{a[1]:.0f}s" if a[1] is not None else "–", f"{a[2]:.0f}%" if a[2] is not None else "–",
                     a[3] if a[3] is not None else "–", f"https://youtu.be/{v['id']}"])
    head = ["Typ", "Titel", "Status", "Termin/Veröffentlicht", "Aufrufe", "Likes", "Komm.", "Ø Dauer", "Ø gesehen", "+Abos", "Link"]
    cs = ch["statistics"]
    title = f"Virlix – {cs.get('subscriberCount')} Abos · {cs.get('viewCount')} Aufrufe gesamt · {cs.get('videoCount')} öffentliche Videos ({today})"
    if A.md:
        with open(A.md, "w") as f:
            f.write(f"# {title}\n\n| " + " | ".join(head) + " |\n|" + "---|" * len(head) + "\n")
            for r in rows: f.write("| " + " | ".join(str(x) for x in r) + " |\n")
            if "_error" in an: f.write(f"\nAnalytics: {an['_error']}\n")
        print(A.md)
    print(title)
    for r in rows: print(" · ".join(str(x) for x in r))
    if "_error" in an: print("Analytics:", an["_error"])


if __name__ == "__main__":
    main()
