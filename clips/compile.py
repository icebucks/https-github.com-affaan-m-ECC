"""YouTube compilation (16:9, 1920x1080) from stream recordings.
  python3 clips/compile.py <spec.json> <out.mp4>
spec.json:
  {"title": "GTA 6 FUNNIEST MOMENTS", "subtitle": "Day 1 · No Commentary",
   "segments": [{"file": "...ts", "start": 120, "end": 150, "label": "SHARK ENCOUNTER", "audio": "raw|dialog|novoice"}, ...]}
audio: raw = keep the game sound (no-commentary sources) · dialog = drop the streamer, keep subtitled game dialogue
       · novoice = drop all voices.  Overlays of known streamers (clipper.HIDE) are blurred and covered by the logo.
Writes <out>.chapters.txt with YouTube chapter timestamps (first one 0:00).

v2 (21.11., "hochwertige Compilations", see clips/COMPILATION_STYLE.md):
  - cold open: 3–4 x ~1.8 s of the strongest moments BEFORE the intro ("COMING UP"), flash cuts, sub-drop hit
  - transitions: short (0.15–0.45 s) xfade between all parts – whip (smoothleft/right), white flash, zoom – each with a whoosh
  - "cont": true on a segment = jump cut inside the same chapter (cuts out maps/menus/dead driving), no new number/label
  - "countdown": true in the spec = numbers count down (#6 … #1, best moment last)
  - "teaser": [{"seg": i, "t": s}, ...] picks cold-open moments (t = seconds after that segment's start); default: loudest moments
  - "text" on a segment: optional 2-3 word punch line shown big for 1.5 s mid-segment ({"at": s, "text": "..."})"""
import json, os, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import clipper

FADE = 0.3
INTRO = 4.0                     # (old static card, no longer used)
TEASE = 1.5                     # cold-open clip length
TITLE = 2.2                     # live title card length
OUTRO = 12.0                    # room for YouTube end-screen elements (5–20 s)
FONT = "Poppins"


def esc(s):
    return s.replace("\\", "\\\\").replace(":", "\\:").replace("'", "’")


def ass_header():
    return """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Big,%s,110,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,8,3,5,60,60,0,1
Style: Tease,%s,96,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,1,0,0,0,100,100,1,0,1,9,4,2,60,60,0,1
Style: TeaseR,%s,96,&H005C3BFF,&H005C3BFF,&H00000000,&H80000000,1,0,0,0,100,100,1,0,1,9,4,2,60,60,0,1
Style: Title,%s,150,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,1,0,0,0,100,100,1,0,1,11,5,4,90,60,0,1
Style: TitleR,%s,150,&H005C3BFF,&H005C3BFF,&H00000000,&H80000000,1,0,0,0,100,100,1,0,1,11,5,4,90,60,0,1
Style: Sub,%s,52,&H0050C8FF,&H0050C8FF,&H00000000,&H80000000,1,0,0,0,100,100,2,0,1,5,2,5,60,60,0,1
Style: Lower,%s,46,&H00FFFFFF,&H00FFFFFF,&H00000000,&H90000000,1,0,0,0,100,100,1,0,3,14,0,7,70,60,60,1
Style: Num,%s,46,&H00141414,&H00141414,&H0050C8FF,&H0050C8FF,1,0,0,0,100,100,0,0,3,14,0,7,70,60,60,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" % ((FONT,) * 8)


def t(x):
    h = int(x // 3600); m = int(x % 3600 // 60); s = x % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def render_segment(seg, n, total, tmp):
    """one 1920x1080 segment: (blurred + logo-covered) overlays, cleaned audio, lower-third chapter label, fades"""
    path, a, b = seg["file"], float(seg["start"]), float(seg["end"])
    dur = b - a
    mode = seg.get("audio", "raw")
    if mode == "dialog": aud = clipper.remove_streamer(path, a, dur, tmp)[0]
    elif mode == "novoice": aud = clipper.remove_voices(path, a, dur, tmp)
    else: aud = None
    who = os.path.basename(path).split("_")[0].split(".")[0]
    boxes = clipper.HIDE.get(who, [])
    ass = os.path.join(tmp, f"s{n}{seg.get('tag', '')}.ass")
    with open(ass, "w") as f:
        f.write(ass_header())
        pop = r"{\fad(250,250)}"
        if seg.get("label") and not seg.get("cont"):
            f.write(f"Dialogue: 1,{t(0.5)},{t(3.8)},Num,,0,0,0,,{pop} #{seg.get('shown', n)} \n")
            f.write(f"Dialogue: 1,{t(0.5)},{t(3.8)},Lower,,190,0,0,,{pop} {seg['label'].upper()} \n")
        for x in seg.get("text", []):                       # punch line (e.g. "5 STARS.")
            f.write(f"Dialogue: 2,{t(x['at'])},{t(x['at'] + 1.5)},Big,,0,0,0,,{{\\pos(960,540)\\fad(80,200)\\t(0,120,\\fscx112\\fscy112)\\t(120,240,\\fscx100\\fscy100)}}{x['text']}\n")
        if seg.get("big"):                                  # teaser caption: small "COMING UP" + the chapter name big, red
            f.write(f"Dialogue: 3,{t(0.0)},{t(dur)},Sub,,0,0,0,,{{\\an8\\pos(960,70)\\fad(40,60)}}COMING UP\n")
            f.write(f"Dialogue: 3,{t(0.0)},{t(dur)},TeaseR,,0,0,0,,{{\\an2\\pos(960,1010)\\fad(40,60)\\t(0,140,\\fscx108\\fscy108)\\t(140,260,\\fscx100\\fscy100)}}{seg['big']}\n")
        if seg.get("title"):                                # title card over live gameplay (dark band left, 2 big lines)
            l1, l2 = seg["title"]
            f.write(f"Dialogue: 0,{t(0.0)},{t(dur)},Big,,0,0,0,,{{\\an7\\pos(0,0)\\bord0\\shad0\\1c&H101010&\\1a&H50&\\fad(120,120)\\p1}}m 0 0 l 1250 0 1050 1080 0 1080{{\\p0}}\n")
            f.write(f"Dialogue: 3,{t(0.08)},{t(dur)},Title,,0,0,0,,{{\\an1\\pos(90,520)\\fad(80,120)\\move(40,520,90,520,0,220)}}{l1}\n")
            f.write(f"Dialogue: 3,{t(0.22)},{t(dur)},TitleR,,0,0,0,,{{\\an1\\pos(90,700)\\fad(80,120)\\move(40,700,90,700,0,220)}}{l2}\n")
            f.write(f"Dialogue: 3,{t(0.4)},{t(dur)},Sub,,0,0,0,,{{\\an1\\pos(96,800)\\fad(100,120)}}{seg.get('subtitle', 'Pure Gameplay · No Commentary')}\n")
    pr = clipper.sh(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "default=nw=1", path])
    import re
    iw, ih = int(re.search(r"width=(\d+)", pr).group(1)), int(re.search(r"height=(\d+)", pr).group(1))
    sx, sy = 1920 / iw, 1080 / ih
    src = "[0:v]setpts=PTS-STARTPTS,scale=1920:1080,setsar=1[s0];"
    for k, (x, y, w, h) in enumerate(boxes):
        X, Y, Wb, Hb = int(x * sx), int(y * sy), int(w * sx), int(h * sy)
        src += f"[s{k}]split[s{k}a][s{k}b];[s{k}b]crop={Wb}:{Hb}:{X}:{Y},gblur=sigma=26[h{k}];[s{k}a][h{k}]overlay={X}:{Y}[s{k + 1}];"
    cur = f"[s{len(boxes)}]"
    ins = ["-i", clipper.exact_src(path, a, dur, tmp)] + (["-i", aud] if aud else []) + ["-i", clipper.LOGO_BADGE, "-i", clipper.LOGO_WM]   # exact: no frozen start
    li = 2 if aud else 1
    fc = src
    for k, (x, y, w, h) in enumerate(boxes):                 # logo over each hidden overlay
        sz = int(min(w * sx, h * sy, 200)) // 2 * 2
        cx, cy = int((x + w / 2) * sx - sz / 2), int((y + h / 2) * sy - sz / 2)
        fc += f"[{li}:v]scale={sz}:{sz}[lb{k}];{cur}[lb{k}]overlay={cx}:{cy}[c{k}];"; cur = f"[c{k}]"
    fc += (f"[{li}:v]scale=110:110,format=rgba,colorchannelmixer=aa=0.85[cl];{cur}[cl]overlay=W-150:40[cc];"       # corner logo
           f"[{li + 1}:v]scale=170:170,format=rgba,colorchannelmixer=aa=0.22[wm];"
           f"[cc][wm]overlay=x='200+1350*(0.5+0.5*sin(t*0.17))':y='200+550*(0.5+0.5*sin(t*0.11+1.1))'[w1];"           # drifting watermark
           f"[w1]ass={ass},fps=30,format=yuv420p[v]")
    am = "1:a" if aud else "0:a"
    out = os.path.join(tmp, f"seg{n:02d}{seg.get('tag', '')}.mp4")
    clipper.sh(["ffmpeg", "-v", "error", "-y"] + ins + ["-filter_complex", fc, "-map", "[v]", "-map", am, "-shortest",
                "-af", f"aresample=48000,afade=t=in:st=0:d=0.03,afade=t=out:st={dur - 0.03}:d=0.03",
                "-c:v", "libx264", "-crf", "20", "-preset", "veryfast", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", out])
    # use the REAL length: a source that starts late (cut file with start_time > 0, stream gap) gives a shorter part, and an
    # xfade offset past the end of a part silently ends the whole video there (21.11.: 9:48 planned, 7:36 written)
    real = float(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=duration",
                                 "-of", "csv=p=0", out], capture_output=True, text=True).stdout.strip() or dur)
    if real < dur - 0.2: print(f"  segment {n}: {real:.2f} s instead of {dur:.2f} s (source shorter)", file=sys.stderr)
    return out, min(dur, real)


def card(text1, text2, dur, still_src, still_t, tmp, name):
    """intro / outro card: blurred game frame, big title, gold subtitle, logo"""
    ass = os.path.join(tmp, name + ".ass")
    with open(ass, "w") as f:
        f.write(ass_header())
        f.write(f"Dialogue: 1,{t(0.2)},{t(dur)},Big,,0,0,0,,{{\\pos(960,520)\\fad(300,300)}}{text1}\n")
        f.write(f"Dialogue: 1,{t(0.6)},{t(dur)},Sub,,0,0,0,,{{\\pos(960,650)\\fad(300,300)}}{text2}\n")
    out = os.path.join(tmp, name + ".mp4")
    clipper.sh(["ffmpeg", "-v", "error", "-y", "-ss", str(still_t), "-i", still_src, "-i", clipper.LOGO_BADGE,
                "-f", "lavfi", "-t", str(dur), "-i", "anullsrc=r=48000:cl=stereo",
                "-filter_complex", f"[0:v]trim=end_frame=1,loop=loop={int(dur * 30)}:size=1,setpts=N/30/TB,scale=1920:1080,"
                f"gblur=sigma=18,eq=brightness=-0.25[bg];[1:v]scale=200:200[lg];[bg][lg]overlay=860:200[b1];"
                f"[b1]ass={ass},fade=t=in:st=0:d=0.3,fade=t=out:st={dur - 0.3}:d=0.3,fps=30,format=yuv420p[v]",
                "-map", "[v]", "-map", "2:a", "-t", str(dur), "-c:v", "libx264", "-crf", "20", "-preset", "veryfast",
                "-c:a", "aac", "-b:a", "192k", out])
    return out


TRANS = ["smoothleft", "fadewhite", "zoomin", "smoothright"]     # rotated between chapters
D_CHAPTER, D_CUT, D_TEASE = 0.45, 0.18, 0.15                       # transition lengths (s): chapter change, jump cut, cold open


def loudest(path, a, b, win=1.8):
    """start of the loudest ~win s inside [a, b] (game audio peak = gunshot, crash, explosion)"""
    import numpy as np
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(a), "-t", str(b - a), "-i", path, "-vn", "-ac", "1", "-ar", "8000",
                          "-f", "f32le", "-"], capture_output=True).stdout
    x = np.frombuffer(raw, np.float32)
    if len(x) < 8000 * (win + 1): return a
    e = np.convolve(x * x, np.ones(int(8000 * 0.25)), "same")
    k = int(np.argmax(e[int(8000 * win / 2): -int(8000 * win)])) + int(8000 * win / 2)
    return a + max(0.0, k / 8000 - win * 0.45)


def strongest(path, a, b, win=1.5):
    """best ~win s window in [a, b]: z(motion) + z(loudness) (a gunshot in a dark room loses to a crash in daylight)"""
    import numpy as np
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(a), "-t", str(b - a), "-i", path, "-vf", "fps=4,scale=64:36,format=gray",
                          "-f", "rawvideo", "-"], capture_output=True).stdout
    v = np.frombuffer(raw, np.uint8).reshape(-1, 36, 64).astype(np.float32)
    if len(v) < 10: return a, 0.0
    mot = np.abs(np.diff(v, axis=0)).mean((1, 2)); bright = v.mean((1, 2))[1:]
    au = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-ss", str(a), "-t", str(b - a), "-i", path, "-vn", "-ac", "1", "-ar", "8000",
                                       "-f", "f32le", "-"], capture_output=True).stdout, np.float32)
    n = len(mot); loud = np.array([np.sqrt(np.mean(au[int(i * 2000):int((i + 1) * 2000)] ** 2) + 1e-9) for i in range(n)])
    z = lambda x: (x - x.mean()) / (x.std() + 1e-6)
    score = z(mot) + z(loud) + 0.5 * z(bright)                       # prefer action that can be SEEN
    w = max(1, int(win * 4)); s_ = np.convolve(score, np.ones(w) / w, "valid")
    k = int(np.argmax(s_))
    return a + k / 4, float(s_[k])


def sfx_track(path, dur, hits):
    """whooshes / hits at the transition times, mixed under the game audio"""
    import numpy as np, soundfile as sf
    from scipy.signal import resample_poly
    import cards
    SR = 48000
    meta = {m["id"]: m for m in json.load(open(os.path.join(cards.SFX, "sounds.json")))["sounds"]}
    mix = np.zeros((int(dur * SR) + SR, 2), np.float32)
    for sid, at, g in hits:
        x, sr = sf.read(os.path.join(cards.SFX, meta[sid]["file"]), dtype="float32")
        if x.ndim == 1: x = np.stack([x, x], 1)
        if sr != SR: x = resample_poly(x, SR, sr, axis=0).astype(np.float32)
        i = max(0, int((at - meta[sid]["sync"]["at"]) * SR))
        n = min(len(x), len(mix) - i)
        if n > 0: mix[i:i + n] += x[:n] * 10 ** (g / 20)
    sf.write(path, mix, SR)


def main(spec_path, out):
    spec = json.load(open(spec_path))
    tmp = tempfile.mkdtemp()
    segs = spec["segments"]
    chapters_n = [s for s in segs if not s.get("cont")]
    if spec.get("countdown"):                                       # #N … #1, best moment last
        k = len(chapters_n)
        for s in chapters_n: s["shown"] = k; k -= 1
    else:
        for i, s in enumerate(chapters_n, 1): s["shown"] = i
    import cards
    # ---- cold open: strongest moments first ("COMING UP")
    picks = spec.get("teaser")
    if not picks:                                                   # strongest moments = motion + loudness, from different chapters
        cands = []
        for i, sg in enumerate(segs):
            if sg["end"] - sg["start"] > 12:
                t0, sc = strongest(sg["file"], sg["start"] + 3, sg["end"] - 2)
                cands.append((sc, i, t0))
        cands.sort(reverse=True)
        picks = [{"seg": i, "abs": t0} for sc, i, t0 in cands[:3]]
    parts = []                                                       # (file, duration, transition into it, length)
    for k, p in enumerate(picks):
        sg = segs[p["seg"]]
        lab = next((x.get("label") for x in segs[:p["seg"] + 1][::-1] if x.get("label")), "")   # chapter of this moment
        t0 = p["abs"] if "abs" in p else sg["start"] + p["t"]
        clip = dict(sg, start=t0, end=t0 + TEASE, label=None, cont=True, text=[], tag=f"t{k}", big=(lab or "COMING UP").upper())
        f, d = render_segment(clip, 90 + k, 0, tmp)
        parts.append((f, d, "fadewhite", D_TEASE))
    # title card: the title over LIVE gameplay (start of chapter 1), 2 lines like the thumbnail
    first = segs[0]
    if "|" in spec["title"]:                                                # explicit line break: "LINE 1|LINE 2"
        l1, l2 = [x.strip() for x in spec["title"].split("|", 1)]
    else:
        words = spec["title"].replace("GTA 6 ", "").split()
        cut = words.index("&") if "&" in words[1:] else (max(1, len(words) // 2) if len(words) > 1 else 1)   # break before "&"
        l1, l2 = ("GTA 6 " + " ".join(words[:cut])).strip(), " ".join(words[cut:]) or words[-1]
    tclip = dict(first, start=first["start"] + 1, end=first["start"] + 1 + TITLE, label=None, cont=True, text=[], tag="title",
                 title=(l1, l2), subtitle=spec.get("subtitle", "Pure Gameplay · No Commentary"))
    f, d = render_segment(tclip, 99, 0, tmp)
    parts.append((f, d, "fadewhite", D_TEASE))
    chap_idx = []                                                    # part index where each chapter starts
    ci = 0
    for n, s in enumerate(segs, 1):
        f, d = render_segment(s, n, len(segs), tmp)
        if s.get("cont"): tr = ("fadewhite", D_CUT)
        else: tr = (TRANS[ci % len(TRANS)], D_CHAPTER); ci += 1; chap_idx.append((len(parts), s))
        parts.append((f, d, tr[0], tr[1]))
        print(f"segment {n}/{len(segs)} ok", file=sys.stderr)
    bright = max(segs, key=lambda s: s["end"] - s["start"])
    parts.append((cards.outro(bright["file"], bright["start"] + 5, os.path.join(tmp, "outro.mp4"), OUTRO), OUTRO, "fade", 0.6))
    # ---- one pass: xfade video + acrossfade audio between all parts
    ins, fc = [], []
    for f, d, _, _ in parts: ins += ["-i", f]
    starts = [0.0]; cur_v, cur_a, end = "[0:v]", "[0:a]", parts[0][1]
    hits = [("bass-sub-drop-medium", 0.02, -4)]
    for i in range(1, len(parts)):
        f, d, tr, td = parts[i]
        off = end - td
        fc.append(f"{cur_v}[{i}:v]xfade=transition={tr}:duration={td}:offset={off:.3f}[v{i}]")
        fc.append(f"{cur_a}[{i}:a]acrossfade=d={td}:c1=tri:c2=tri[a{i}]")
        cur_v, cur_a = f"[v{i}]", f"[a{i}]"
        starts.append(off); end = off + d
        if td >= D_CHAPTER: hits.append(("whoosh-fast-medium", off + td / 2, -9))
        elif i <= len(picks): hits.append(("boom-hit-medium" if i == len(picks) else "whoosh-fast-medium", off + td / 2, -10))
        else: hits.append(("whoosh-medium-soft", off + td / 2, -16))
    sfx = os.path.join(tmp, "sfx.wav"); sfx_track(sfx, end, hits)
    ins += ["-i", sfx]
    fc.append(f"{cur_a}[{len(parts)}:a]amix=inputs=2:duration=first:normalize=0[aout]")
    mid = os.path.join(tmp, "mid.mp4")
    clipper.sh(["ffmpeg", "-v", "error", "-y"] + ins + ["-filter_complex", ";".join(fc), "-map", cur_v, "-map", "[aout]",
                "-c:v", "libx264", "-crf", "19", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-c:a", "pcm_s16le", mid])
    got = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", mid],
                               capture_output=True, text=True).stdout.strip() or 0)
    if abs(got - end) > 1.0:                                         # never ship a silently truncated video
        sys.exit(f"joined video is {got:.1f} s, expected {end:.1f} s – check the parts in {tmp}")
    # two-pass loudness normalisation (one pass lands ~1 LU off on long files)
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", mid, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    m = json.loads(r[r.rindex("{"):r.rindex("}") + 1])
    ln = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
          f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true"
          ",alimiter=limit=0.84:level=false,aresample=48000")      # hard ceiling: without it the 21.11 file peaked at +2.4 dBFS
    clipper.sh(["ffmpeg", "-v", "error", "-y", "-i", mid, "-c:v", "copy", "-af", ln,
                "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", out])
    os.remove(mid)
    # chapters: YouTube needs 0:00 first; the cold open + intro count as "Intro"
    chapters = [("0:00", "Intro")]
    for pi, s in chap_idx:
        x = starts[pi] + parts[pi][3]
        chapters.append((f"{int(x // 60)}:{int(x % 60):02d}", f"#{s['shown']} {s['label']}"))
    open(out + ".chapters.txt", "w").write("\n".join(f"{a} {b}" for a, b in chapters) + "\n")
    print(out)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
