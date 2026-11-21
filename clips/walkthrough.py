"""Walkthrough helper for no-commentary STORY streams (GTA 6 missions, one video per mission).
  python3 clips/walkthrough.py scan <block.ts> [--step 3]
      OCR every <step> s (tesseract) -> <block>.scan.json and a printed timeline:
        MENU   pause menu / map / save screen (cut these out)
        NAME   mission name seen on screen (save slot "Pipework (6%)", mission title card)
        PASS   "mission passed/complete"      FAIL  "mission failed", "wasted", "busted"
        TEXT   other large on-screen text (objectives, chapter cards) – check by eye
  python3 clips/walkthrough.py clean <block.ts> <start> <end>
      prints the gameplay pieces between start and end with menus/maps removed, as compile.py segments
      ("cont": true after the first) – paste them into a spec, then render with clips/compile.py.
Mission names are taken ONLY from the screen (never guessed). Check every cut with a contact sheet before rendering."""
import json, os, re, subprocess, sys, tempfile
from concurrent.futures import ThreadPoolExecutor

MENU_WORDS = ("brief", "progress", "save game", "load game", "new game", "recenter", "add marker", "2d view",
              "remove destination", "empty slot", "objective text", "help text", "dialogue")
PASS_RE = re.compile(r"mission\s+(passed|complete)|\bpassed\b", re.I)
FAIL_RE = re.compile(r"mission\s+failed|\bwasted\b|\bbusted\b", re.I)
SLOT_RE = re.compile(r"([A-Z][A-Za-z' &\-]{2,40}?)\s*\((\d{1,3})%\)")


def frames(path, step, tmp):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", path, "-vf", f"fps=1/{step},scale=1280:-1",
                    os.path.join(tmp, "f%05d.png")], check=True)
    return sorted(f for f in os.listdir(tmp) if f.endswith(".png"))


def ocr(png):
    r = subprocess.run(["tesseract", png, "-", "--psm", "11", "-l", "eng"], capture_output=True, text=True)
    return " ".join(r.stdout.split())


def scan(path, step=3.0):
    tmp = tempfile.mkdtemp()
    fs = frames(path, step, tmp)
    with ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as ex:
        texts = list(ex.map(lambda f: ocr(os.path.join(tmp, f)), fs))
    for f in fs: os.remove(os.path.join(tmp, f))
    os.rmdir(tmp)
    events = []
    for i, t in enumerate(texts):
        at = round(i * step, 1); low = t.lower()
        if any(w in low for w in MENU_WORDS): events.append({"t": at, "kind": "MENU", "text": t[:120]})
        for m in SLOT_RE.finditer(t): events.append({"t": at, "kind": "NAME", "text": f"{m.group(1).strip()} ({m.group(2)}%)"})
        if PASS_RE.search(t): events.append({"t": at, "kind": "PASS", "text": t[:120]})
        if FAIL_RE.search(t): events.append({"t": at, "kind": "FAIL", "text": t[:120]})
    out = {"file": path, "step": step, "texts": texts, "events": events}
    json.dump(out, open(path + ".scan.json", "w"), indent=1)
    return out


def menu_spans(scanj, pad=1.5):
    step = scanj["step"]; spans = []
    for e in scanj["events"]:
        if e["kind"] != "MENU": continue
        a, b = e["t"] - pad, e["t"] + step + pad
        if spans and a <= spans[-1][1]: spans[-1][1] = max(spans[-1][1], b)
        else: spans.append([a, b])
    return spans


def clean(path, start, end, min_piece=6.0):
    sj = json.load(open(path + ".scan.json"))
    pieces, cur = [], start
    for a, b in menu_spans(sj):
        if b <= start or a >= end: continue
        if a - cur >= min_piece: pieces.append((cur, a))
        cur = max(cur, b)
    if end - cur >= min_piece: pieces.append((cur, end))
    segs = [{"file": path, "start": round(a, 1), "end": round(b, 1), "audio": "raw", **({"cont": True} if i else {"label": "MISSION"})}
            for i, (a, b) in enumerate(pieces)]
    print(json.dumps(segs, indent=1))
    print(f"# {len(pieces)} pieces, {sum(b - a for a, b in pieces):.0f} s of {end - start:.0f} s kept", file=sys.stderr)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "scan":
        step = float(sys.argv[sys.argv.index("--step") + 1]) if "--step" in sys.argv else 3.0
        s = scan(sys.argv[2], step)
        for e in s["events"]:
            print(f"{int(e['t'] // 60):3d}:{e['t'] % 60:04.1f}  {e['kind']:<5} {e['text']}")
        print(f"# {len(s['events'])} events, {len(s['texts'])} frames")
    elif cmd == "clean":
        clean(sys.argv[2], float(sys.argv[3]), float(sys.argv[4]))
    else:
        print(__doc__)
