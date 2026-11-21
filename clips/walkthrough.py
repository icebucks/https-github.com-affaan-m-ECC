"""Walkthrough helper for no-commentary STORY streams (GTA 6 missions, one video per mission).
  python3 clips/walkthrough.py scan <block.ts>
      fast scan (~1–2 min per 15-min block) -> <block>.scan.json + printed timeline:
        MENU   map / pause / brief / save screen  (menu header "MAP · BRIEF · PROGRESS" read by OCR every 2 s,
               purple full-screen menus by colour) – these get cut out
        NAME   mission name from a save slot ("Pipework (6%)")
        PASS   "mission passed / complete"       FAIL  "mission failed", "wasted", "busted"
        TEXT   other large centred text (mission title cards, chapter cards) – check by eye
  python3 clips/walkthrough.py clean <block.ts> <start> <end> [--label "MISSION NAME"]
      prints compile.py segments for start–end with all MENU spans removed (first piece labelled, rest "cont")
Mission names are taken ONLY from the screen, never guessed. Look at a contact sheet of every cut before rendering."""
import json, os, re, subprocess, sys, tempfile
from concurrent.futures import ThreadPoolExecutor
import numpy as np

HEADER_WORDS = ("brief", "progress", "jason & lucia", "jason &", "& lucia")
MENU_WORDS = ("save game", "load game", "new game", "recenter", "add marker", "empty slot")
PASS_RE = re.compile(r"mission\s+(passed|complete)|\bpassed\b", re.I)
FAIL_RE = re.compile(r"mission\s+failed|\bwasted\b|\bbusted\b", re.I)
SLOT_RE = re.compile(r"([A-Z][A-Za-z' &\-]{2,40}?)\s*\((\d{1,3})%\)")
HDR_STEP, MID_STEP = 2.0, 4.0


def grab_all(path, tmp):
    """ONE decode pass (720p is plenty): header strip every 2 s, centre band every 4 s, 160x90 colour thumbs every 2 s"""
    fc = (f"[0:v]scale=1280:720,split=3[a][b][c];"
          f"[a]fps=1/{HDR_STEP},crop=640:54:384:22,format=gray[h];"
          f"[b]fps=1/{MID_STEP},crop=1024:288:128:216,scale=768:216,format=gray[m];"
          f"[c]fps=1/{HDR_STEP},scale=160:90[t]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", path, "-filter_complex", fc,
                    "-map", "[h]", os.path.join(tmp, "h%05d.png"), "-map", "[m]", os.path.join(tmp, "m%05d.png"),
                    "-map", "[t]", "-f", "rawvideo", "-pix_fmt", "rgb24", os.path.join(tmp, "thumbs.rgb")], check=True)
    ls = sorted(os.listdir(tmp))
    return ([os.path.join(tmp, f) for f in ls if f.startswith("h")], [os.path.join(tmp, f) for f in ls if f.startswith("m")],
            os.path.join(tmp, "thumbs.rgb"))


def ocr(png, psm):
    env = dict(os.environ, OMP_THREAD_LIMIT="1")                     # tesseract's own threads fight the pool otherwise
    r = subprocess.run(["tesseract", png, "-", "--psm", str(psm), "-l", "eng"], capture_output=True, text=True, env=env)
    return " ".join(r.stdout.split())


def purple_share(thumbs):
    a = np.fromfile(thumbs, np.uint8).reshape(-1, 90, 160, 3).astype(float) / 255
    mx, mn = a.max(-1), a.min(-1); d = mx - mn + 1e-6
    R, G, B = a[..., 0], a[..., 1], a[..., 2]
    h = np.where(mx == R, (G - B) / d % 6, np.where(mx == G, (B - R) / d + 2, (R - G) / d + 4)) * 60
    return ((h > 250) & (h < 330) & (d / (mx + 1e-6) > 0.3) & (mx > 0.2)).mean(axis=(1, 2))


def scan(path):
    tmp = tempfile.mkdtemp()
    hdr, mid, thumbs = grab_all(path, tmp)
    pur = purple_share(thumbs)
    with ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as ex:
        th = list(ex.map(lambda p: ocr(p, 7), hdr))
        tm = list(ex.map(lambda p: ocr(p, 6), mid))
    for p in hdr + mid + [thumbs]: os.remove(p)
    os.rmdir(tmp)
    events = []
    for i, t in enumerate(th):
        low = t.lower(); at = i * HDR_STEP
        if any(w in low for w in HEADER_WORDS) or (i < len(pur) and pur[i] > 0.3):
            events.append({"t": at, "kind": "MENU", "text": t[:80] or f"purple {pur[i]:.2f}"})
    for i, t in enumerate(tm):
        at = i * MID_STEP; low = t.lower()
        if any(w in low for w in MENU_WORDS): events.append({"t": at, "kind": "MENU", "text": t[:80]})
        for m in SLOT_RE.finditer(t): events.append({"t": at, "kind": "NAME", "text": f"{m.group(1).strip()} ({m.group(2)}%)"})
        if PASS_RE.search(t): events.append({"t": at, "kind": "PASS", "text": t[:100]})
        elif FAIL_RE.search(t): events.append({"t": at, "kind": "FAIL", "text": t[:100]})
        elif len(re.findall(r"[A-Z]{3,}", t)) >= 2 and len(t) < 60: events.append({"t": at, "kind": "TEXT", "text": t})
    events.sort(key=lambda e: e["t"])
    out = {"file": path, "events": events, "header_text": th, "mid_text": tm}
    json.dump(out, open(path + ".scan.json", "w"), indent=1)
    return out


def menu_spans(scanj, pad=1.0):
    spans = []
    for e in scanj["events"]:
        if e["kind"] != "MENU": continue
        a, b = e["t"] - pad, e["t"] + HDR_STEP + pad
        if spans and a <= spans[-1][1]: spans[-1][1] = max(spans[-1][1], b)
        else: spans.append([a, b])
    return spans


def clean(path, start, end, label="MISSION", min_piece=6.0):
    sj = json.load(open(path + ".scan.json"))
    pieces, cur = [], start
    for a, b in menu_spans(sj):
        if b <= start or a >= end: continue
        if a - cur >= min_piece: pieces.append((cur, a))
        cur = max(cur, b)
    if end - cur >= min_piece: pieces.append((cur, end))
    segs = [{"file": path, "start": round(a, 1), "end": round(b, 1), "audio": "raw", **({"cont": True} if i else {"label": label})}
            for i, (a, b) in enumerate(pieces)]
    print(json.dumps(segs, indent=1))
    print(f"# {len(pieces)} pieces, {sum(b - a for a, b in pieces):.0f} s of {end - start:.0f} s kept", file=sys.stderr)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "scan":
        s = scan(sys.argv[2])
        for e in s["events"]:
            print(f"{int(e['t'] // 60):3d}:{e['t'] % 60:04.1f}  {e['kind']:<5} {e['text']}")
        print(f"# {len(s['events'])} events")
    elif cmd == "clean":
        lab = sys.argv[sys.argv.index("--label") + 1] if "--label" in sys.argv else "MISSION"
        clean(sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), lab)
    else:
        print(__doc__)
