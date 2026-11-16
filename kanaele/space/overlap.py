"""Guard: a narrated Short must not answer or reuse a long video's topic (reserved.json).
python3 overlap.py shorts/ssN.py   -> exit 1 with the hits.  vshort.main() calls check(spec) before every still/render."""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))


def texts(spec):
    out = list(spec.get("hook", ())) + list(spec.get("question", ())) + [spec.get("title", "")]
    for b in spec["beats"]:
        out.append(b[1]); out.append(b[2].get("head", ""))
    return re.sub(r"[*{}|]", " ", " ".join(out)).lower()


def hits(text):
    res = json.load(open(os.path.join(HERE, "reserved.json")))
    return [(t["long"], p) for t in res["topics"] for p in t["patterns"] if re.search(p, text)]


def check(spec):
    h = hits(texts(spec))
    if h:
        msg = "\n".join(f"  ✗ '{p}'  ->  reserved for long video: {l}" for l, p in h)
        sys.exit(f"OVERLAP – this Short touches a long video's topic. Pick another topic or angle:\n{msg}")
    print("overlap check: OK (no long-video topic touched)", file=sys.stderr)


if __name__ == "__main__":
    t = open(sys.argv[1]).read().lower()
    h = hits(re.sub(r"[*{}|]", " ", t))
    for l, p in h: print(f"✗ {p} -> {l}")
    sys.exit(1 if h else 0)
