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
    ev.append(f"Dialogue: 2,{ass_time(0)},{ass_time(3.2)},Hook,,0,0,0,,{pop}{l1.upper()}")
    if l2: ev.append(f"Dialogue: 2,{ass_time(0.45)},{ass_time(3.2)},Hook2,,0,0,0,,{pop}{l2.upper()}")
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


def cut(path, start, end, hook, credit, cam=None, out=None, gameplay=False, cx=0.5):
    dur = end - start
    out = out or os.path.splitext(path)[0] + f"_clip_{int(start)}.mp4"
    tmp = tempfile.mkdtemp()
    if gameplay:     # pure gameplay: no facecam, no chat overlay, no streamer voice, no captions
        words = []
        aud = remove_voices(path, start, dur, tmp)
    else:
        a = audio(path, start=start, dur=dur)
        words = [(w, s, e) for w, s, e in transcribe(a) if s < dur]
        aud = None
    ass = os.path.join(tmp, "c.ass"); make_ass(words, hook, credit, dur, ass)
    bg = "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,gblur=sigma=30,eq=brightness=-0.18[bg];"
    if gameplay:   # 3:4 window from the middle of the screen (overlays sit in the corners), 2x scale -> 1080x1440
        fc = (bg + f"[0:v]crop=ih*3/4:ih:(iw-ih*3/4)*{cx}:0,scale=1080:1440,setsar=1[game];"
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
    ap.add_argument("cmd", choices=["find", "cut"])
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
    A = ap.parse_args()
    if A.cmd == "find": find(A.video, A.top, A.len)
    else: cut(A.video, A.start, A.end, A.hook, A.credit, [int(v) for v in A.cam.split(",")] if A.cam else None, A.out, A.gameplay, A.cx)
