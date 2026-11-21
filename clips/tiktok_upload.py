"""Send a video to the TikTok inbox as a DRAFT (Content Posting API, FILE_UPLOAD, scope video.upload).
The owner finishes and posts it in the TikTok app (inbox notification) – nothing is published automatically.

  python3 clips/tiktok_upload.py login                 -> prints the authorization link (open it, allow, copy the address it redirects to)
  python3 clips/tiktok_upload.py exchange "<redirect address or code>"   -> stores the tokens (never printed)
  python3 clips/tiktok_upload.py whoami                -> shows the connected account's display name
  python3 clips/tiktok_upload.py draft <video.mp4>     -> uploads as draft, polls the status
Config from environment variables: TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET (owner sets it in the environment settings),
TIKTOK_REDIRECT_URI (default http://localhost:8080/callback). Tokens: ~/.config/tiktok/token.json (chmod 600, never in git).
Access tokens last 24 h and are refreshed automatically with the refresh token (valid ~365 days)."""
import hashlib, json, os, secrets, sys, time, urllib.parse
import requests

API = "https://open.tiktokapis.com/v2"
TOKEN_FILE = os.path.expanduser("~/.config/tiktok/token.json")
PKCE_FILE = os.path.expanduser("~/.config/tiktok/pkce.json")   # code_verifier between login and exchange
SCOPES = "user.info.basic,video.upload"


def cfg(name, default=None):
    v = os.environ.get(name, default)
    if not v: sys.exit(f"missing environment variable {name} (set it in the environment settings)")
    return v


def redirect(): return os.environ.get("TIKTOK_REDIRECT_URI", "http://localhost:8080/callback")


def save(tok):
    os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
    tok["obtained_at"] = int(time.time())
    with open(TOKEN_FILE, "w") as f: json.dump(tok, f)
    os.chmod(TOKEN_FILE, 0o600)


def token_request(data):
    data = dict(data, client_key=cfg("TIKTOK_CLIENT_KEY"), client_secret=cfg("TIKTOK_CLIENT_SECRET"))
    r = requests.post(f"{API}/oauth/token/", data=data, headers={"Content-Type": "application/x-www-form-urlencoded"}, timeout=30)
    j = r.json()
    if r.status_code != 200 or "access_token" not in j:
        sys.exit(f"token request failed: HTTP {r.status_code} {j.get('error', '')} {j.get('error_description', '')}")
    return j


def access_token():
    if not os.path.exists(TOKEN_FILE): sys.exit("not logged in yet: run 'login' and 'exchange' first")
    tok = json.load(open(TOKEN_FILE))
    if time.time() > tok["obtained_at"] + tok.get("expires_in", 86400) - 300:
        tok = token_request({"grant_type": "refresh_token", "refresh_token": tok["refresh_token"]}); save(tok)
    return tok["access_token"]


def login():
    # TikTok requires PKCE (S256). Its docs use the HEX-encoded SHA256 of the verifier as code_challenge.
    verifier = secrets.token_urlsafe(48)[:64]
    os.makedirs(os.path.dirname(PKCE_FILE), exist_ok=True)
    with open(PKCE_FILE, "w") as f: json.dump({"code_verifier": verifier}, f)
    os.chmod(PKCE_FILE, 0o600)
    q = {"client_key": cfg("TIKTOK_CLIENT_KEY"), "scope": SCOPES, "response_type": "code", "redirect_uri": redirect(),
         "state": secrets.token_urlsafe(12), "code_challenge": hashlib.sha256(verifier.encode()).hexdigest(),
         "code_challenge_method": "S256"}
    print("https://www.tiktok.com/v2/auth/authorize/?" + urllib.parse.urlencode(q))


def exchange(arg):
    code = arg
    if "code=" in arg:
        code = urllib.parse.parse_qs(urllib.parse.urlparse(arg).query)["code"][0]
    if not os.path.exists(PKCE_FILE): sys.exit("no pending login: run 'login' first and use the new link")
    verifier = json.load(open(PKCE_FILE))["code_verifier"]
    tok = token_request({"grant_type": "authorization_code", "code": code, "redirect_uri": redirect(), "code_verifier": verifier})
    save(tok); os.remove(PKCE_FILE)
    print(f"logged in (scopes: {tok.get('scope')}); tokens stored in {TOKEN_FILE}")


def whoami():
    r = requests.get(f"{API}/user/info/", params={"fields": "display_name"}, headers={"Authorization": f"Bearer {access_token()}"}, timeout=30)
    print(r.json().get("data", {}).get("user", {}).get("display_name") or r.text[:300])


def draft(path):
    size = os.path.getsize(path)
    MB = 1024 * 1024
    if size <= 64 * MB: chunk, n = size, 1                     # small files: one chunk
    else: chunk = 10 * MB; n = size // chunk                    # last chunk carries the remainder
    h = {"Authorization": f"Bearer {access_token()}", "Content-Type": "application/json; charset=UTF-8"}
    r = requests.post(f"{API}/post/publish/inbox/video/init/", headers=h, timeout=60,
                      json={"source_info": {"source": "FILE_UPLOAD", "video_size": size, "chunk_size": chunk, "total_chunk_count": n}})
    j = r.json()
    if r.status_code != 200 or j.get("error", {}).get("code") not in (None, "ok"):
        sys.exit(f"init failed: HTTP {r.status_code} {j.get('error')}")
    pid, url = j["data"]["publish_id"], j["data"]["upload_url"]
    with open(path, "rb") as f:
        for i in range(n):
            start = i * chunk; end = size - 1 if i == n - 1 else start + chunk - 1
            f.seek(start); data = f.read(end - start + 1)
            for attempt in range(4):
                try:
                    u = requests.put(url, data=data, timeout=300, headers={"Content-Type": "video/mp4", "Content-Length": str(len(data)),
                                                                           "Content-Range": f"bytes {start}-{end}/{size}"})
                    break
                except requests.RequestException:
                    time.sleep(2 ** attempt)
            else:
                sys.exit("upload failed: network errors")
            if u.status_code not in (200, 201, 206): sys.exit(f"chunk {i + 1}/{n} failed: HTTP {u.status_code} {u.text[:200]}")
    for _ in range(30):                                          # wait until TikTok has the file
        s = requests.post(f"{API}/post/publish/status/fetch/", headers=h, json={"publish_id": pid}, timeout=30).json()
        st = s.get("data", {}).get("status")
        if st in ("SEND_TO_USER_INBOX", "PUBLISH_COMPLETE"): print(f"draft sent to the TikTok inbox ({os.path.basename(path)})"); return pid
        if st == "FAILED": sys.exit(f"TikTok rejected the video: {s['data'].get('fail_reason')}")
        time.sleep(5)
    print(f"uploaded, status still processing (publish_id {pid})"); return pid


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "login": login()
    elif cmd == "exchange": exchange(sys.argv[2])
    elif cmd == "whoami": whoami()
    elif cmd == "draft": draft(sys.argv[2])
    else: print(__doc__)
