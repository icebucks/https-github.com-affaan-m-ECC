"""Upload a video to YouTube with the YouTube Data API v3 (resumable upload).
  python3 clips/yt_upload.py <video.mp4> --title "..." --description-file desc.txt [--tags a,b] [--privacy private|unlisted|public]
                             [--publish-at 2026-11-20T18:00:00+01:00] [--thumbnail cover.jpg] [--playlist PLAYLIST_ID]
Credentials come ONLY from environment variables (set by the owner in the environment settings, never in chat or in git):
  YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_REFRESH_TOKEN  (OAuth 2.0, scope https://www.googleapis.com/auth/youtube.upload)
Default privacy is "private". --publish-at needs privacy "private" (YouTube publishes at that time).
Note: projects that have not passed YouTube's API audit can only upload private videos."""
import argparse, json, os, sys, time
import requests

TOKEN_URL = "https://oauth2.googleapis.com/token"
UPLOAD_URL = "https://www.googleapis.com/upload/youtube/v3/videos"
CHUNK = 16 * 1024 * 1024


def access_token():
    need = ["YOUTUBE_CLIENT_ID", "YOUTUBE_CLIENT_SECRET", "YOUTUBE_REFRESH_TOKEN"]
    missing = [k for k in need if not os.environ.get(k)]
    if missing:
        sys.exit(f"missing environment variables: {', '.join(missing)} (set them in the environment settings)")
    local = os.path.expanduser("~/.config/youtube/refresh_token")      # newer token from clips/yt_auth.py (this session)
    rt = open(local).read().strip() if os.path.exists(local) else os.environ["YOUTUBE_REFRESH_TOKEN"]
    r = requests.post(TOKEN_URL, data={"client_id": os.environ["YOUTUBE_CLIENT_ID"], "client_secret": os.environ["YOUTUBE_CLIENT_SECRET"],
                                       "refresh_token": rt, "grant_type": "refresh_token"}, timeout=30)
    if r.status_code != 200:
        sys.exit(f"token refresh failed: HTTP {r.status_code} {r.json().get('error', '')} {r.json().get('error_description', '')}")
    return r.json()["access_token"]


def upload(path, title, description, tags, privacy, publish_at, category="20"):     # 20 = Gaming
    tok = access_token()
    status = {"privacyStatus": privacy, "selfDeclaredMadeForKids": False}
    if publish_at: status["publishAt"] = publish_at
    meta = {"snippet": {"title": title[:100], "description": description[:5000], "tags": tags, "categoryId": category}, "status": status}
    size = os.path.getsize(path)
    r = requests.post(UPLOAD_URL, params={"uploadType": "resumable", "part": "snippet,status"},
                      headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json; charset=UTF-8",
                               "X-Upload-Content-Length": str(size), "X-Upload-Content-Type": "video/mp4"},
                      data=json.dumps(meta), timeout=60)
    if r.status_code != 200: sys.exit(f"upload start failed: HTTP {r.status_code} {r.text[:300]}")
    loc = r.headers["Location"]
    pos = 0
    with open(path, "rb") as f:
        while pos < size:
            f.seek(pos); chunk = f.read(CHUNK)
            end = pos + len(chunk) - 1
            for attempt in range(5):
                try:
                    r = requests.put(loc, headers={"Authorization": f"Bearer {tok}", "Content-Range": f"bytes {pos}-{end}/{size}"}, data=chunk, timeout=300)
                    break
                except requests.RequestException:
                    time.sleep(2 ** attempt)
            else:
                sys.exit("upload failed: network errors")
            if r.status_code in (200, 201):
                vid = r.json()["id"]; print(f"uploaded: https://youtu.be/{vid} ({privacy})"); return vid
            if r.status_code == 308:
                rng = r.headers.get("Range"); pos = int(rng.split("-")[1]) + 1 if rng else 0
                print(f"  {pos / size:5.1%}", file=sys.stderr)
            elif r.status_code == 401:
                tok = access_token()
            else:
                sys.exit(f"upload failed: HTTP {r.status_code} {r.text[:300]}")
    sys.exit("upload ended without a video id")


def set_thumbnail(vid, path):
    r = requests.post("https://www.googleapis.com/upload/youtube/v3/thumbnails/set", params={"videoId": vid},
                      headers={"Authorization": f"Bearer {access_token()}", "Content-Type": "image/jpeg"}, data=open(path, "rb").read(), timeout=120)
    print("thumbnail:", "ok" if r.status_code == 200 else f"HTTP {r.status_code} {r.text[:200]}")


def add_to_playlist(vid, playlist):
    r = requests.post("https://www.googleapis.com/youtube/v3/playlistItems", params={"part": "snippet"},
                      headers={"Authorization": f"Bearer {access_token()}"},
                      json={"snippet": {"playlistId": playlist, "resourceId": {"kind": "youtube#video", "videoId": vid}}}, timeout=60)
    print("playlist:", "ok" if r.status_code == 200 else f"HTTP {r.status_code} {r.text[:200]}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("video"); ap.add_argument("--title", required=True); ap.add_argument("--description-file", required=True)
    ap.add_argument("--tags", default=""); ap.add_argument("--privacy", default="private", choices=["private", "unlisted", "public"])
    ap.add_argument("--publish-at", default=None); ap.add_argument("--thumbnail", default=None); ap.add_argument("--playlist", default=None)
    ap.add_argument("--category", default="20")
    A = ap.parse_args()
    vid = upload(A.video, A.title, open(A.description_file).read(), [t.strip() for t in A.tags.split(",") if t.strip()],
                 A.privacy, A.publish_at, A.category)
    if A.thumbnail: set_thumbnail(vid, A.thumbnail)
    if A.playlist: add_to_playlist(vid, A.playlist)
