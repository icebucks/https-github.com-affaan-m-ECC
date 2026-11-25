"""Download only a time range of a Twitch VOD (yt-dlp finds the stream, Python fetches the HLS segments).
Why not `yt-dlp --download-sections`: that path runs ffmpeg, and ffmpeg cannot use this environment's HTTPS proxy.

  python3 clips/vod_cut.py list <channel> [--n 10]                 # latest VODs: id | length | title
  python3 clips/vod_cut.py cut <vod-id> <start> <end> <out.ts> [--quality 1080p]
      start/end in seconds or hh:mm:ss; the output starts at the segment boundary just before <start>
      (≤ 10 s earlier) – use clipper.exact_src / compile.py for frame-exact cuts.

Only for no-commentary sources (credit the channel), same rules as live recordings (clips/COMPILATION_STYLE.md).
Proxy note: the VOD CDN host (e.g. d2nvs31859zcd8.cloudfront.net) must be in the environment's allowed hosts."""
import argparse, os, re, sys, urllib.parse
import requests
import yt_dlp


def secs(s):
    if re.fullmatch(r"[\d.]+", str(s)): return float(s)
    p = [float(x) for x in str(s).split(":")]
    while len(p) < 3: p.insert(0, 0.0)
    return p[0] * 3600 + p[1] * 60 + p[2]


def ydl(): return yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True})


def list_vods(channel, n):
    info = yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True, "extract_flat": True, "playlistend": n}).extract_info(
        f"https://www.twitch.tv/{channel}/videos?filter=archives&sort=time", download=False)
    for e in info.get("entries", [])[:n]:
        d = int(e.get("duration") or 0)
        print(f"{str(e.get('id')).lstrip('v')} | {d // 3600}:{d % 3600 // 60:02d}:{d % 60:02d} | {e.get('title', '')[:90]}")


def cut(vod, start, end, out, quality):
    info = ydl().extract_info(f"https://www.twitch.tv/videos/{str(vod).lstrip('v')}", download=False)
    fmts = [f for f in info["formats"] if f.get("vcodec") not in (None, "none")]
    pick = next((f for f in fmts if f.get("format_id") == quality), None) or max(fmts, key=lambda f: f.get("height") or 0)
    url = pick["url"]
    s = requests.Session(); s.headers["User-Agent"] = "Mozilla/5.0"
    pl = s.get(url, timeout=60); pl.raise_for_status()
    base = url.rsplit("/", 1)[0] + "/"
    t, dur, segs = 0.0, None, []
    for line in pl.text.splitlines():
        if line.startswith("#EXTINF:"):
            dur = float(line[8:].split(",")[0])
        elif line and not line.startswith("#") and dur is not None:
            if t + dur > start and t < end: segs.append((t, urllib.parse.urljoin(base, line)))
            t += dur; dur = None
    if not segs: sys.exit(f"no segments in {start}-{end} (VOD length {t:.0f} s)")
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out + ".part", "wb") as f:
        for i, (t0, u) in enumerate(segs):
            r = s.get(u, timeout=120)
            if r.status_code == 403 and "-unmuted" in u:          # Twitch renames muted parts
                r = s.get(u.replace("-unmuted", "-muted"), timeout=120)
            r.raise_for_status(); f.write(r.content)
            print(f"\r{i + 1}/{len(segs)} segments", end="", file=sys.stderr)
    os.replace(out + ".part", out)
    print(f"\n{out}  (starts at {segs[0][0]:.1f} s of the VOD = {start - segs[0][0]:.1f} s before the requested start; "
          f"channel {info.get('uploader') or info.get('channel')}, {pick.get('format_id')})", file=sys.stderr)
    print(out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["list", "cut"])
    ap.add_argument("a"); ap.add_argument("b", nargs="?"); ap.add_argument("c", nargs="?"); ap.add_argument("d", nargs="?")
    ap.add_argument("--n", type=int, default=10); ap.add_argument("--quality", default="1080p")
    x = ap.parse_args()
    if x.cmd == "list": list_vods(x.a, x.n)
    else: cut(x.a, secs(x.b), secs(x.c), x.d, x.quality)
