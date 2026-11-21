"""Connect the YouTube channel with more rights (upload + manage videos/comments + read analytics), like tiktok_upload.py:
  python3 clips/yt_auth.py login <link_file>          -> writes the Google sign-in link into <link_file> (it contains the client id)
  python3 clips/yt_auth.py exchange "<redirect address or code>" <token_file>
        -> exchanges the code, stores the new refresh token in ~/.config/youtube/refresh_token (chmod 600) for THIS session
           and writes it into <token_file> so the owner can put it into the environment variable YOUTUBE_REFRESH_TOKEN
  python3 clips/yt_auth.py scopes                      -> shows which rights the active token has
Values are never printed. Client id/secret come from YOUTUBE_CLIENT_ID / YOUTUBE_CLIENT_SECRET.
Redirect: http://localhost:8080 (works for "Desktop app" OAuth clients; a "Web" client needs this URI added in the
Google Cloud console). The page after sign-in will not load – that is fine, copy its full address."""
import base64, hashlib, json, os, secrets, sys, urllib.parse
import requests

SCOPES = ["https://www.googleapis.com/auth/youtube.upload",
          "https://www.googleapis.com/auth/youtube.force-ssl",
          "https://www.googleapis.com/auth/yt-analytics.readonly"]
REDIRECT = os.environ.get("YOUTUBE_REDIRECT_URI", "http://localhost:8080")
DIR = os.path.expanduser("~/.config/youtube")
PKCE = os.path.join(DIR, "pkce.json")
LOCAL_RT = os.path.join(DIR, "refresh_token")


def env(k):
    v = os.environ.get(k)
    if not v: sys.exit(f"missing environment variable {k}")
    return v


def login(link_file):
    os.makedirs(DIR, exist_ok=True)
    verifier = secrets.token_urlsafe(64)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    state = secrets.token_urlsafe(12)
    json.dump({"verifier": verifier, "state": state}, open(PKCE, "w")); os.chmod(PKCE, 0o600)
    q = {"client_id": env("YOUTUBE_CLIENT_ID"), "redirect_uri": REDIRECT, "response_type": "code", "scope": " ".join(SCOPES),
         "access_type": "offline", "prompt": "consent", "include_granted_scopes": "true", "state": state,
         "code_challenge": challenge, "code_challenge_method": "S256"}
    with open(link_file, "w") as f: f.write("https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(q) + "\n")
    print(f"sign-in link written to {link_file}")


def exchange(arg, token_file):
    code = arg
    if "code=" in arg:
        qs = urllib.parse.parse_qs(urllib.parse.urlparse(arg if "://" in arg else "http://" + arg).query)
        if "error" in qs: sys.exit(f"Google returned an error: {qs['error'][0]}")
        code = qs["code"][0]
    if not os.path.exists(PKCE): sys.exit("no pending login: run 'login' first")
    pk = json.load(open(PKCE))
    r = requests.post("https://oauth2.googleapis.com/token", timeout=30, data={
        "client_id": env("YOUTUBE_CLIENT_ID"), "client_secret": env("YOUTUBE_CLIENT_SECRET"), "code": code,
        "code_verifier": pk["verifier"], "grant_type": "authorization_code", "redirect_uri": REDIRECT})
    j = r.json()
    if r.status_code != 200 or "refresh_token" not in j:
        sys.exit(f"token exchange failed: HTTP {r.status_code} {j.get('error', '')} {j.get('error_description', '')}")
    for p in (LOCAL_RT, token_file):
        with open(p, "w") as f: f.write(j["refresh_token"] + "\n")
        os.chmod(p, 0o600)
    os.remove(PKCE)
    print(f"connected. rights: {j.get('scope', '')}")
    print(f"refresh token stored for this session and written to {token_file}")


def scopes():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import yt_upload
    r = requests.get("https://oauth2.googleapis.com/tokeninfo", params={"access_token": yt_upload.access_token()}, timeout=30).json()
    print(r.get("scope", r))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "login": login(sys.argv[2])
    elif cmd == "exchange": exchange(sys.argv[2], sys.argv[3])
    elif cmd == "scopes": scopes()
    else: sys.exit(__doc__)
