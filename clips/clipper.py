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


def remove_streamer(path, start, dur, tmp, pad=0.12):
    """drop only the streamer's voice, keep in-game dialogue.
    Game dialogue is subtitled: a spoken word that shows up in the subtitle band (±1.2 s) is the game, everything else is
    the streamer -> separate voices from the rest, mute the streamer's words, remix."""
    import soundfile as sf
    from rapidfuzz import fuzz
    voc, inst = separate(path, start, dur, tmp)
    v, sr = sf.read(voc); ins, _ = sf.read(inst)
    subs = ocr_subtitles(path, start, dur, tmp)
    words = transcribe(audio(voc))
    keep = np.zeros(int(dur * 100) + 1)                          # 10 ms grid, 1 = game voice
    n_keep = 0; kept = []
    norm = [re.sub(r"[^a-z']", "", w.lower()) for w, _, _ in words]
    hits = []
    for i, (w, s, e) in enumerate(words):        # a word counts as game dialogue only if its 3-word phrase is in the subtitles
        near = " ".join(t for ts, t in subs if s - 1.2 <= ts <= e + 1.2)
        phrase = " ".join(x for x in norm[max(0, i - 1):i + 2] if x)
        hits.append(bool(near) and len(phrase) >= 6 and fuzz.partial_ratio(phrase, near) >= 85
                    and (len(norm[i]) < 3 or any(fuzz.ratio(norm[i], c) >= 80 for c in near.split())))
    for i, (w, s, e) in enumerate(words):
        if hits[i] or (0 < i < len(words) - 1 and hits[i - 1] and hits[i + 1]):
            keep[max(0, int((s - pad) * 100)):int((e + pad) * 100)] = 1.0; n_keep += 1; kept.append((w, s, e))
    k = np.ones(8) / 8
    gain = np.convolve(keep, k, mode="same")
    g = np.interp(np.arange(len(v)) / sr, np.arange(len(gain)) / 100, gain)
    mix = ins + v * (g[:, None] if v.ndim == 2 else g)
    out = os.path.join(tmp, "dialog_mix.wav"); sf.write(out, mix, sr)
    print(f"words: {len(words)}, kept as game dialogue: {n_keep}, muted (streamer): {len(words) - n_keep}, subtitle reads: {len(subs)}",
          file=sys.stderr)
    return out, kept


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


def cut(path, start, end, hook, credit, cam=None, out=None, gameplay=False, cx=0.5, dialog=False):
    dur = end - start
    out = out or os.path.splitext(path)[0] + f"_clip_{int(start)}.mp4"
    tmp = tempfile.mkdtemp()
    if gameplay:     # pure gameplay: no facecam, no chat overlay, no streamer voice, no captions
        if dialog:                                   # captions = the game's own dialogue, read from the cleaned mix
            aud, _ = remove_streamer(path, start, dur, tmp)
            words = [(w, s, e) for w, s, e in transcribe(audio(aud)) if s < dur and e - s < 1.5]   # long "words" = hallucination
            if len(words) < 4: words = []                                                      # stray words on a silent track
        else: aud, words = remove_voices(path, start, dur, tmp), []
    else:
        a = audio(path, start=start, dur=dur)
        words = [(w, s, e) for w, s, e in transcribe(a) if s < dur]
        aud = None
    ass = os.path.join(tmp, "c.ass"); make_ass(words, hook, credit, dur, ass)
    bg = "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,gblur=sigma=30,eq=brightness=-0.18[bg];"
    if gameplay:   # 4:5 window from the middle (overlays sit in the corners), above the game's subtitle band -> 1080x1350
        fc = (bg + f"[0:v]crop=ih*0.64:ih*0.8:(iw-ih*0.64)*{cx}:0,scale=1080:1350,setsar=1[game];"
              f"[bg][game]overlay=0:330[b1];[b1]ass={ass}[v]")
    elif cam:   # small source facecams: a 600 px box (no blurry 4x upscale), gameplay large underneath
        x, y, w, h = cam
        ch = int(round(600 * h / w / 2)) * 2
        gy = 460 + ch + 16
        fc = (bg + f"[0:v]crop={w}:{h}:{x}:{y},scale=600:{ch},setsar=1,pad=608:{ch + 8}:4:4:color=0xFFC850[cam];"
              f"[0:v]scale=-2:{1720 - gy},crop=1080:{1720 - gy},setsar=1[game];"
              f"[bg][game]overlay=0:{gy}[b1];[b1][cam]overlay=236:456[b2];[b2]ass={ass}[v]")
    else:     # no facecam: big gameplay window
        fc = (bg + f"[0:v]scale=-2:1000,crop=1080:1000,setsar=1[game];[bg][game]overlay=0:460[b1];[b1]ass={ass}[v]")
    ins = ["-ss", str(start), "-t", str(dur), "-i", path] + (["-i", aud] if aud else [])
    sh(["ffmpeg", "-v", "error", "-y"] + ins + ["-filter_complex", fc, "-map", "[v]", "-map", "1:a" if aud else "0:a", "-shortest",
        "-c:v", "libx264", "-crf", "19", "-preset", "medium", "-pix_fmt", "yuv420p", "-r", "30",
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
