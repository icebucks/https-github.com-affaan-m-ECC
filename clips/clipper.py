"""Stream clipper: find the best moments in a recorded stream and turn them into 9:16 shorts.

  python3 clips/clipper.py find  <video> [--top 8] [--len 35]
      transcribe (faster-whisper), score every window by loudness peaks, excitement words and speech density,
      write <video>.moments.json with the best non-overlapping windows
  python3 clips/clipper.py cut   <video> <start_s> <end_s> --hook "LINE 1|LINE 2" --credit "twitch.tv/name" [--cam x,y,w,h] [--out file.mp4]
      9:16 short: facecam on top (if --cam, source pixels) + gameplay below, or blurred fill + gameplay in the middle;
      hook text in the first 3 s (y 300–520), word-by-word captions above the TikTok caption zone (< y 1450),
      streamer credit under the top tabs, −14 LUFS.

Layout follows the TikTok safe zones used by the other channels: nothing below y 1450, nothing important under the
right-hand buttons (x > 880, y 760–1660), nothing above y 210."""
import argparse, json, math, os, re, subprocess, sys, tempfile
import numpy as np

W, H = 1080, 1920
HYPE = re.compile(r"\b(oh my god|omg|no way|what the|bro|let'?s go|holy|wtf|insane|crazy|run|chat|yo+|dude|damn|wow|help|nooo*|yes+|wait)\b", re.I)


def sh(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode: sys.exit(r.stderr[-2000:])
    return r.stdout


def audio(path, sr=16000, start=None, dur=None):
    cmd = ["ffmpeg", "-v", "error"] + (["-ss", str(start)] if start is not None else []) + ["-i", path] + \
          (["-t", str(dur)] if dur is not None else []) + ["-ac", "1", "-ar", str(sr), "-f", "f32le", "-"]
    return np.frombuffer(subprocess.run(cmd, capture_output=True).stdout, dtype=np.float32)


def transcribe(a, model="base.en"):
    from faster_whisper import WhisperModel
    m = WhisperModel(model, device="cpu", compute_type="int8")
    segs, _ = m.transcribe(a, language="en", word_timestamps=True, vad_filter=True)
    return [(w.word.strip(), w.start, w.end) for s in segs for w in (s.words or [])]


def find(path, top=8, length=35.0):
    a = audio(path)
    sr = 16000
    sec = len(a) // sr
    rms = np.array([np.sqrt(np.mean(a[i * sr:(i + 1) * sr] ** 2) + 1e-12) for i in range(sec)])
    db = 20 * np.log10(rms)
    z = (db - np.median(db)) / (np.std(db) + 1e-6)
    words = transcribe(a)
    hype = np.zeros(sec); dens = np.zeros(sec)
    for w, s, e in words:
        i = min(sec - 1, int(s))
        dens[i] += 1
        if HYPE.search(w): hype[i] += 1
    L = int(length)
    score = np.array([np.clip(z[i:i + L], 0, None).sum() * 1.0 + hype[i:i + L].sum() * 2.5 + 0.15 * dens[i:i + L].sum()
                      for i in range(max(1, sec - L))])
    picks = []
    for i in np.argsort(-score):
        if all(abs(i - p) >= L for p in picks): picks.append(int(i))
        if len(picks) >= top: break
    out = []
    for i in sorted(picks):
        peak = i + int(np.argmax(z[i:i + L]))
        st = max(0, peak - int(L * 0.6))                       # build-up before the peak, payoff after
        text = " ".join(w for w, s, e in words if st <= s < st + L)
        out.append(dict(start=st, end=min(sec, st + L), peak=peak, score=round(float(score[i]), 1), text=text))
    js = path + ".moments.json"
    json.dump(dict(video=path, moments=out), open(js, "w"), indent=1)
    for m in out: print(f"{m['start']:6d}s–{m['end']:6d}s  score {m['score']:6.1f}  {m['text'][:110]}")
    return js


CATS = {   # viral categories: keywords the streamer says + how much loudness / on-screen motion count
    "funny":   (re.compile(r"\b(ha(ha)+|lol|lmao|bro+|why|what the|no way|dude|bruh|oh my god|omg|wtf|hell|crazy|insane|funny|weird|wait what|he just|she just)\b", re.I), 1.0, 0.4),
    "action":  (re.compile(r"\b(cops?|police|run+|go go|shoot|shot|gun|chase|wanted|stars?|drive|crash|dead|die|kill|explo\w*|heli\w*|swat|escape|get out|floor it)\b", re.I), 1.0, 1.4),
    "secrets": (re.compile(r"\b(look at (this|that)|did you see|easter egg|detail|hidden|secret|notice|reference|map|you can (even|actually)|they (added|put)|that'?s sick|wait look)\b", re.I), 0.3, 0.2),
}


def motion(path, sec, fps=2):
    """mean frame difference per second (tiny grey frames) – chases, crashes and explosions move a lot"""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vf", f"fps={fps},scale=64:36,format=gray", "-f", "rawvideo", "-"],
                         capture_output=True).stdout
    f = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 36, 64).astype(np.float32)
    d = np.abs(np.diff(f, axis=0)).mean((1, 2)) if len(f) > 1 else np.zeros(1)
    per = np.array([d[i * fps:(i + 1) * fps].mean() if i * fps < len(d) else 0 for i in range(sec)])
    return (per - np.median(per)) / (per.std() + 1e-6)


def find_cats(path, per_cat=4, length=30.0):
    """best moments per viral category (funny / action / secrets) -> <video>.cats.json, printed for review"""
    a = audio(path); sr = 16000; sec = len(a) // sr
    rms = np.array([np.sqrt(np.mean(a[i * sr:(i + 1) * sr] ** 2) + 1e-12) for i in range(sec)])
    db = 20 * np.log10(rms); z = np.clip((db - np.median(db)) / (np.std(db) + 1e-6), 0, None)
    mo = np.clip(motion(path, sec), 0, None)
    words = transcribe(a)
    L = int(length); res = {}; used = []
    for cat, (rx, wl, wm) in CATS.items():
        kw = np.zeros(sec)
        text_by_sec = [""] * sec
        for w, s, e in words:
            text_by_sec[min(sec - 1, int(s))] += " " + w
        for i in range(sec):
            ctx = " ".join(text_by_sec[max(0, i - 1):i + 2])
            kw[i] = len(rx.findall(text_by_sec[i])) + 0.5 * (len(rx.findall(ctx)) > 0)
        score = np.array([kw[i:i + L].sum() * 2.0 + z[i:i + L].sum() * wl * 0.3 + mo[i:i + L].sum() * wm * 0.3 for i in range(max(1, sec - L))])
        picks = []
        for i in np.argsort(-score):
            if all(abs(i - p) >= L for p in picks + used): picks.append(int(i))
            if len(picks) >= per_cat: break
        used += picks
        res[cat] = [dict(start=i, end=min(sec, i + L), score=round(float(score[i]), 1),
                         text=" ".join(w for w, s, e in words if i <= s < i + L)) for i in sorted(picks, key=lambda p: -score[p])]
    json.dump(dict(video=path, cats=res), open(path + ".cats.json", "w"), indent=1)
    for cat, ms in res.items():
        print(f"== {cat}")
        for m in ms: print(f"  {m['start']:5d}–{m['end']:5d}s  {m['score']:6.1f}  {m['text'][:110]}")
    return res


def ass_time(t):
    t = max(0.0, t); h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def make_ass(words, hook, credit, dur, out):
    l1, _, l2 = hook.partition("|")
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Hook,Poppins,78,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,1,0,0,0,100,100,0,0,1,7,2,8,60,60,272,1
Style: Hook2,Poppins,66,&H0050C8FF,&H0050C8FF,&H00000000,&H64000000,1,0,0,0,100,100,0,0,1,7,2,8,60,60,362,1
Style: Cap,Poppins,74,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,1,0,0,0,100,100,0,0,1,8,2,2,90,200,560,1
Style: Credit,Poppins,30,&H00E6E6E6,&H00E6E6E6,&H00000000,&H64000000,1,0,0,0,100,100,1,0,1,4,1,8,90,90,222,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev = []
    pop = r"{\fscx112\fscy112\t(0,120,\fscx100\fscy100)}"
    def fit(txt, size):   # Poppins Bold caps ≈ 0.68 em per character; keep each line inside ~940 px (clear of the button column)
        return min(size, int(940 / (0.68 * max(1, len(txt)))))
    ev.append(f"Dialogue: 2,{ass_time(0)},{ass_time(3.2)},Hook,,0,0,0,,{pop}{{\\fs{fit(l1, 78)}}}{l1.upper()}")
    if l2: ev.append(f"Dialogue: 2,{ass_time(0.45)},{ass_time(3.2)},Hook2,,0,0,0,,{pop}{{\\fs{fit(l2, 66)}}}{l2.upper()}")
    ev.append(f"Dialogue: 1,{ass_time(0)},{ass_time(dur)},Credit,,0,0,0,,{credit}")
    # captions: groups of up to 3 words, the spoken word in gold
    groups = []; g = []
    for w in words:
        g.append(w)
        if len(g) == 3 or re.search(r"[.!?]$", w[0]): groups.append(g); g = []
    if g: groups.append(g)
    for gi, g in enumerate(groups):
        g_end = groups[gi + 1][0][1] if gi + 1 < len(groups) else g[-1][2] + 0.4
        for k, (w, s, e) in enumerate(g):
            nxt = g[k + 1][1] if k + 1 < len(g) else min(g_end, e + 0.6)
            txt = " ".join((r"{\c&H0050C8FF&}" + x.upper() + r"{\c&H00FFFFFF&}") if j == k else x.upper() for j, (x, _, _) in enumerate(g))
            ev.append(f"Dialogue: 0,{ass_time(s)},{ass_time(max(nxt, s + 0.05))},Cap,,0,0,0,,{txt}")
    open(out, "w").write(head + "\n".join(ev) + "\n")


def remove_voices(path, start, dur, tmp, model="UVR-MDX-NET-Inst_HQ_4.onnx"):
    """AI source separation: keep music, engines, shots, ambience – drop ALL voices (streamer and in-game dialogue)"""
    from audio_separator.separator import Separator
    wav = os.path.join(tmp, "src.wav")
    sh(["ffmpeg", "-v", "error", "-y", "-ss", str(start), "-t", str(dur), "-i", path, "-vn", "-ac", "2", "-ar", "44100", wav])
    sep = Separator(output_dir=tmp, model_file_dir=os.path.expanduser("~/.cache/audio-separator"), output_format="WAV")
    sep.load_model(model)
    files = sep.separate(wav)
    inst = next(f for f in files if "Instrumental" in f)
    return inst if os.path.isabs(inst) else os.path.join(tmp, inst)


_ECAPA = []


def ecapa():
    if not _ECAPA:
        from speechbrain.inference.speaker import EncoderClassifier
        _ECAPA.append(EncoderClassifier.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb",
                                                     savedir=os.path.expanduser("~/.cache/spkrec-ecapa"), run_opts={"device": "cpu"}))
    return _ECAPA[0]


def separate(path, start, dur, tmp, model="UVR-MDX-NET-Inst_HQ_4.onnx"):
    """returns (vocals.wav, instrumental.wav) for a section of the video"""
    from audio_separator.separator import Separator
    wav = os.path.join(tmp, f"src_{int(start)}.wav")
    sh(["ffmpeg", "-v", "error", "-y", "-ss", str(start), "-t", str(dur), "-i", path, "-vn", "-ac", "2", "-ar", "44100", wav])
    sep = Separator(output_dir=tmp, model_file_dir=os.path.expanduser("~/.cache/audio-separator"), output_format="WAV")
    sep.load_model(model)
    files = [f if os.path.isabs(f) else os.path.join(tmp, f) for f in sep.separate(wav)]
    return next(f for f in files if "(Vocals)" in f), next(f for f in files if "Instrumental" in f)


def windows(x, sr, win=1.5, hop=0.5, min_db=-42):
    """speech-active windows of a vocal stem: (start_s, end_s, samples)"""
    out = []
    for i in range(0, max(1, len(x) - int(win * sr)), int(hop * sr)):
        seg = x[i:i + int(win * sr)]
        if 20 * np.log10(np.sqrt(np.mean(seg ** 2)) + 1e-9) > min_db: out.append((i / sr, i / sr + win, seg))
    return out


def embed(segs):
    import torch
    m = ecapa(); E = []
    same = len({len(s) for s in segs}) == 1
    for k in range(0, len(segs), 32 if same else 1):      # variable-length utterances are embedded one by one
        b = torch.tensor(np.stack(segs[k:k + (32 if same else 1)]), dtype=torch.float32)
        E.append(m.encode_batch(b).squeeze(1).numpy())
    E = np.concatenate(E) if E else np.zeros((0, 192))
    return E / (np.linalg.norm(E, axis=1, keepdims=True) + 1e-9)


def streamer_profile(path, sample=420.0):
    """voice print of the streamer = the voice that talks most across the recording (cached next to the video)"""
    npy = path + ".streamer.npy"
    if os.path.exists(npy): return np.load(npy)
    tmp = tempfile.mkdtemp()
    voc, _ = separate(path, 0, sample, tmp)
    x = audio(voc)
    E = embed([s for _, _, s in windows(x, 16000, hop=1.5)])
    sim = E @ E.T
    best = int(np.argmax((sim > 0.55).sum(1)))                   # the window with the most look-alikes
    prof = E[sim[best] > 0.55].mean(0); prof /= np.linalg.norm(prof)
    share = float((E @ prof > 0.55).mean())
    print(f"streamer voice print: {share:.0%} of speech windows match", file=sys.stderr)
    np.save(npy, prof)
    return prof


SUB_BOX = (0.23, 0.80, 0.87, 0.975)     # GTA subtitle band (x0, y0, x1, y1 as fractions of the frame): bottom centre


def ocr_subtitles(path, start, dur, tmp, fps=4):
    """read the in-game subtitle band fps times a second -> [(t, text)]"""
    x0, y0, x1, y1 = SUB_BOX
    d = os.path.join(tmp, "sub"); os.makedirs(d, exist_ok=True)
    sh(["ffmpeg", "-v", "error", "-y", "-ss", str(start), "-t", str(dur), "-i", path, "-vf",
        f"fps={fps},crop=iw*{x1 - x0}:ih*{y1 - y0}:iw*{x0}:ih*{y0},scale=iw*2:-1,format=gray,lutyuv=y='if(gt(val,200),0,255)'",
        os.path.join(d, "%05d.png")])
    out = []
    for k, f in enumerate(sorted(os.listdir(d))):
        r = subprocess.run(["tesseract", os.path.join(d, f), "-", "--psm", "6"], capture_output=True, text=True)
        txt = re.sub(r"[^a-z' ]", " ", r.stdout.lower())
        txt = " ".join(w for w in txt.split() if len(w) > 1 or w in ("i", "a"))
        if len(txt) >= 4: out.append((k / fps, txt))
    return out


def remove_streamer(path, start, dur, tmp, pre=0.35, post=0.6, bridge=0.8):
    """drop only the streamer's voice, keep in-game dialogue – smoothly.
    GTA shows a subtitle while a character speaks: the voice stem stays open for the whole time a subtitle is on screen
    (plus a little before/after, short gaps bridged, 150 ms fades); outside subtitles the voice stem is muted (= streamer)."""
    import soundfile as sf
    voc, inst = separate(path, start, dur, tmp)
    v, sr = sf.read(voc); ins, _ = sf.read(inst)
    subs = [(t, x) for t, x in ocr_subtitles(path, start, dur, tmp)
            if sum(1 for w in x.split() if len(w) >= 3) >= 2]          # real subtitle lines, not OCR noise on bright skies
    keep = np.zeros(int(dur * 100) + 1)
    for t, _ in subs:
        keep[max(0, int((t - pre) * 100)):int((t + 0.25 + post) * 100)] = 1.0
    on = np.where(keep > 0)[0]                                          # bridge short gaps between subtitle lines
    if len(on):
        gaps = np.where(np.diff(on) > 1)[0]
        for g in gaps:
            a, b = on[g], on[g + 1]
            if (b - a) / 100 < bridge: keep[a:b] = 1.0
    # each open stretch stays open as a whole (smooth), but only if what is SAID there matches what the subtitles SAY –
    # mission hints and objective text are subtitled too, while the streamer talks over them
    from rapidfuzz import fuzz
    words = transcribe(audio(voc))
    on = np.concatenate([[0], keep, [0]]); d = np.diff(on)
    starts, ends = np.where(d == 1)[0], np.where(d == -1)[0]
    dropped = 0
    for a, b in zip(starts, ends):
        t0, t1 = a / 100, b / 100
        ws = [re.sub(r"[^a-z']", "", w.lower()) for w, s, e in words if t0 <= s < t1]
        ws = [w for w in ws if len(w) >= 3]
        if not ws: continue
        txt = " ".join(x for t, x in subs if t0 - 1 <= t <= t1 + 1).split()
        hit = sum(1 for w in ws if any(fuzz.ratio(w, c) >= 80 for c in txt)) / len(ws)
        if hit < 0.4: keep[a:b] = 0.0; dropped += 1
    k = np.hanning(31); k /= k.sum()                                    # ~150 ms soft fades
    gain = np.clip(np.convolve(keep, k, mode="same"), 0, 1)
    g = np.interp(np.arange(len(v)) / sr, np.arange(len(gain)) / 100, gain)
    mix = ins + v * (g[:, None] if v.ndim == 2 else g)
    out = os.path.join(tmp, "dialog_mix.wav"); sf.write(out, mix, sr)
    print(f"subtitle lines read: {len(subs)}, dialogue open {keep.mean():.0%} of the clip, {dropped} stretch(es) dropped (streamer over hints)", file=sys.stderr)
    return out, []


def remove_streamer_by_voiceprint(path, start, dur, tmp, thr=0.5):
    """drop only the streamer's voice, keep in-game dialogue: separate -> voice print per window -> mute the streamer -> remix"""
    import soundfile as sf
    prof = streamer_profile(path)
    voc, inst = separate(path, start, dur, tmp)
    v, sr = sf.read(voc); ins, _ = sf.read(inst)
    v16 = audio(voc)
    W_ = windows(v16, 16000)
    sims = embed([s for _, _, s in W_]) @ prof if W_ else np.zeros(0)
    gain = np.ones(len(v16) // 160 + 1)                         # 10 ms resolution
    kept = 0
    for (a, b, _), s in zip(W_, sims):
        if s > thr: gain[int(a * 100):int(b * 100)] = 0.0
        else: kept += 1
    k = np.ones(8) / 8                                            # ~80 ms fades instead of hard cuts
    gain = np.convolve(gain, k, mode="same")
    g = np.interp(np.arange(len(v)) / sr, np.arange(len(gain)) / 100, gain)
    mix = ins + v * g[:, None] if v.ndim == 2 else ins + v * g
    out = os.path.join(tmp, "dialog_mix.wav"); sf.write(out, mix, sr)
    muted = float((sims > thr).mean()) if len(sims) else 0.0
    print(f"voice windows: {len(sims)}, streamer muted {muted:.0%}, other voices kept {kept}", file=sys.stderr)
    return out


HIDE = {   # overlays that reach into the centred 1.3:1 window (720p source pixels: x, y, w, h) -> blurred
    "theburntpeanut": [(200, 500, 178, 220)],      # peanut avatar, bottom left
    "xqc": [(0, 0, 270, 440)],                     # facecam + chat, top left
    "darkviperau": [(1025, 110, 255, 260)],        # facecam + chat, top right
}


LOGO_BADGE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "logo_badge.png")
LOGO_WM = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "logo_watermark.png")
CX = {"xqc": 0.66, "darkviperau": 0.37}     # window position per streamer (0 = left … 1 = right) to dodge the facecam


def cut(path, start, end, hook, credit, cam=None, out=None, gameplay=False, cx=0.5, dialog=False, hide=None):
    dur = end - start
    out = out or os.path.splitext(path)[0] + f"_clip_{int(start)}.mp4"
    tmp = tempfile.mkdtemp()
    if gameplay:     # pure gameplay: no facecam, no chat, no streamer voice; the game's own subtitles stay in the picture
        aud = remove_streamer(path, start, dur, tmp)[0] if dialog else remove_voices(path, start, dur, tmp)
        words = []
    else:
        a = audio(path, start=start, dur=dur)
        words = [(w, s, e) for w, s, e in transcribe(a) if s < dur]
        aud = None
    ass = os.path.join(tmp, "c.ass"); make_ass(words, hook, credit, dur, ass)
    extra = []
    bg = ("[0:v]scale=270:480:force_original_aspect_ratio=increase,crop=270:480,gblur=sigma=10,eq=brightness=-0.32,"
          "scale=1080:1920:flags=bilinear[bg];")          # blur at 1/4 size: same look, many times faster
    if gameplay:   # wide 1.3:1 window (73 % of the width, full height, near-native sharpness), overlays in it blurred away
        who = os.path.basename(path).split("_")[0].split(".")[0]
        boxes = hide if hide is not None else HIDE.get(who, [])
        if cx == 0.5 and who in CX: cx = CX[who]           # shift the window so a corner facecam falls outside it
        src = "[0:v]null[s0];"
        for n, (x, y, w, h) in enumerate(boxes):
            src += f"[s{n}]split[s{n}a][s{n}b];[s{n}b]crop={w}:{h}:{x}:{y},gblur=sigma=22,eq=brightness=-0.08[h{n}];[s{n}a][h{n}]overlay={x}:{y}[s{n + 1}];"
        last = f"[s{len(boxes)}]"
        pr = sh(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "default=nw=1", path])
        iw, ih = int(re.search(r"width=(\d+)", pr).group(1)), int(re.search(r"height=(\d+)", pr).group(1))
        A = 1.2; cw = int(ih * A) // 2 * 2; x0 = int((iw - cw) * cx); sc = 1080 / cw; gh = int(ih * sc) // 2 * 2
        gy = (1920 - gh) // 2 + 40
        badges = []
        for (x, y, w, h) in boxes:      # where the hidden overlay lands in the 9:16 frame -> a soft branded badge on top
            bx0, bx1 = max(0, (x - x0) * sc), min(1080, (x + w - x0) * sc)
            if bx1 - bx0 < 10: continue
            badges.append((bx0, gy + y * sc, bx1, gy + (y + h) * sc))
        with open(ass, "a") as fa:
            for bx0, by0, bx1, by1 in badges:
                fa.write(f"Dialogue: 3,{ass_time(0)},{ass_time(dur)},Credit,,0,0,0,,{{\\an7\\pos(0,0)\\bord0\\shad0\\blur14\\1c&H1A1410&\\1a&H18&\\p1}}"
                         f"m {bx0 - 6:.0f} {by0 - 6:.0f} l {bx1 + 6:.0f} {by0 - 6:.0f} {bx1 + 6:.0f} {by1 + 6:.0f} {bx0 - 6:.0f} {by1 + 6:.0f}{{\\p0}}\n")
        fc = (bg + src + f"{last}crop={cw}:{ih}:{x0}:0,scale=1080:{gh},setsar=1[game];"
              f"[bg][game]overlay=0:{gy}[b1];[b1]ass={ass}[a0];")
        # the creator's logo: (1) as the badge over every hidden overlay, (2) as a faint watermark drifting slowly
        # through the picture, so the clip cannot simply be cropped and re-uploaded
        li = 2 if aud else 1
        extra += ["-i", LOGO_BADGE, "-i", LOGO_WM]
        cur = "[a0]"
        for n, (bx0, by0, bx1, by1) in enumerate(badges):
            sz = int(min(bx1 - bx0, by1 - by0, 230)) // 2 * 2
            fc += (f"[{li}:v]scale={sz}:{sz}[lb{n}];{cur}[lb{n}]overlay={(bx0 + bx1 - sz) / 2:.0f}:{(by0 + by1 - sz) / 2:.0f}[a{n + 1}];")
            cur = f"[a{n + 1}]"
        ws, wy0, wy1 = 150, gy + 30, gy + gh - 150 - 60
        fc += (f"[{li + 1}:v]scale={ws}:{ws},format=rgba,colorchannelmixer=aa=0.32[wm];"
               f"{cur}[wm]overlay=x='70+(1080-{ws}-140)*(0.5+0.5*sin(t*0.21))':y='{wy0}+({wy1 - wy0})*(0.5+0.5*sin(t*0.13+1.3))'[v]")
    elif cam:   # small source facecams: a 600 px box (no blurry 4x upscale), gameplay large underneath
        x, y, w, h = cam
        ch = int(round(600 * h / w / 2)) * 2
        gy = 460 + ch + 16
        fc = (bg + f"[0:v]crop={w}:{h}:{x}:{y},scale=600:{ch},setsar=1,pad=608:{ch + 8}:4:4:color=0xFFC850[cam];"
              f"[0:v]scale=-2:{1720 - gy},crop=1080:{1720 - gy},setsar=1[game];"
              f"[bg][game]overlay=0:{gy}[b1];[b1][cam]overlay=236:456[b2];[b2]ass={ass}[v]")
    else:     # no facecam: big gameplay window
        fc = (bg + f"[0:v]scale=-2:1000,crop=1080:1000,setsar=1[game];[bg][game]overlay=0:460[b1];[b1]ass={ass}[v]")
    ins = ["-ss", str(start), "-t", str(dur), "-i", path] + (["-i", aud] if aud else []) + extra
    sh(["ffmpeg", "-v", "error", "-y"] + ins + ["-filter_complex", fc, "-map", "[v]", "-map", "1:a" if aud else "0:a", "-shortest",
        "-c:v", "libx264", "-crf", "20", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-r", "30",
        "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out])
    print(out)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["find", "cats", "cut"])
    ap.add_argument("video")
    ap.add_argument("start", nargs="?", type=float)
    ap.add_argument("end", nargs="?", type=float)
    ap.add_argument("--top", type=int, default=8)
    ap.add_argument("--len", type=float, default=35.0)
    ap.add_argument("--hook", default="")
    ap.add_argument("--credit", default="")
    ap.add_argument("--cam", default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--gameplay", action="store_true", help="pure gameplay: crop out facecam/chat, remove all voices, no captions")
    ap.add_argument("--cx", type=float, default=0.5, help="horizontal position of the gameplay window (0 = left … 1 = right)")
    ap.add_argument("--dialog", action="store_true", help="with --gameplay: mute only the streamer's voice, keep in-game dialogue")
    A = ap.parse_args()
    if A.cmd == "find": find(A.video, A.top, A.len)
    elif A.cmd == "cats": find_cats(A.video, max(1, A.top // 2), A.len)
    else: cut(A.video, A.start, A.end, A.hook, A.credit, [int(v) for v in A.cam.split(",")] if A.cam else None, A.out, A.gameplay, A.cx, A.dialog)
