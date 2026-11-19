"""YouTube compilation (16:9, 1920x1080) from stream recordings.
  python3 clips/compile.py <spec.json> <out.mp4>
spec.json:
  {"title": "GTA 6 FUNNIEST MOMENTS", "subtitle": "Day 1 · No Commentary",
   "segments": [{"file": "...ts", "start": 120, "end": 150, "label": "SHARK ENCOUNTER", "audio": "raw|dialog|novoice"}, ...]}
audio: raw = keep the game sound (no-commentary sources) · dialog = drop the streamer, keep subtitled game dialogue
       · novoice = drop all voices.  Overlays of known streamers (clipper.HIDE) are blurred and covered by the logo.
Writes <out>.chapters.txt with YouTube chapter timestamps (first one 0:00)."""
import json, os, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import clipper

FADE = 0.3
INTRO = 3.0
OUTRO = 4.0
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
Style: Sub,%s,52,&H0050C8FF,&H0050C8FF,&H00000000,&H80000000,1,0,0,0,100,100,2,0,1,5,2,5,60,60,0,1
Style: Lower,%s,46,&H00FFFFFF,&H00FFFFFF,&H00000000,&H90000000,1,0,0,0,100,100,1,0,3,14,0,7,70,60,60,1
Style: Num,%s,46,&H00141414,&H00141414,&H0050C8FF,&H0050C8FF,1,0,0,0,100,100,0,0,3,14,0,7,70,60,60,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" % (FONT, FONT, FONT, FONT)


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
    ass = os.path.join(tmp, f"s{n}.ass")
    with open(ass, "w") as f:
        f.write(ass_header())
        pop = r"{\fad(250,250)}"
        f.write(f"Dialogue: 1,{t(0.3)},{t(3.6)},Num,,0,0,0,,{pop} #{n} \n")
        f.write(f"Dialogue: 1,{t(0.3)},{t(3.6)},Lower,,190,0,0,,{pop} {seg['label'].upper()} \n")
    pr = clipper.sh(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "default=nw=1", path])
    import re
    iw, ih = int(re.search(r"width=(\d+)", pr).group(1)), int(re.search(r"height=(\d+)", pr).group(1))
    sx, sy = 1920 / iw, 1080 / ih
    src = "[0:v]scale=1920:1080,setsar=1[s0];"
    for k, (x, y, w, h) in enumerate(boxes):
        X, Y, Wb, Hb = int(x * sx), int(y * sy), int(w * sx), int(h * sy)
        src += f"[s{k}]split[s{k}a][s{k}b];[s{k}b]crop={Wb}:{Hb}:{X}:{Y},gblur=sigma=26[h{k}];[s{k}a][h{k}]overlay={X}:{Y}[s{k + 1}];"
    cur = f"[s{len(boxes)}]"
    ins = ["-ss", str(a), "-t", str(dur), "-i", path] + (["-i", aud] if aud else []) + ["-i", clipper.LOGO_BADGE, "-i", clipper.LOGO_WM]
    li = 2 if aud else 1
    fc = src
    for k, (x, y, w, h) in enumerate(boxes):                 # logo over each hidden overlay
        sz = int(min(w * sx, h * sy, 200)) // 2 * 2
        cx, cy = int((x + w / 2) * sx - sz / 2), int((y + h / 2) * sy - sz / 2)
        fc += f"[{li}:v]scale={sz}:{sz}[lb{k}];{cur}[lb{k}]overlay={cx}:{cy}[c{k}];"; cur = f"[c{k}]"
    fc += (f"[{li}:v]scale=110:110,format=rgba,colorchannelmixer=aa=0.85[cl];{cur}[cl]overlay=W-150:40[cc];"       # corner logo
           f"[{li + 1}:v]scale=170:170,format=rgba,colorchannelmixer=aa=0.22[wm];"
           f"[cc][wm]overlay=x='200+1350*(0.5+0.5*sin(t*0.17))':y='200+550*(0.5+0.5*sin(t*0.11+1.1))'[w1];"           # drifting watermark
           f"[w1]ass={ass},fade=t=in:st=0:d={FADE},fade=t=out:st={dur - FADE}:d={FADE},fps=30,format=yuv420p[v]")
    am = "1:a" if aud else "0:a"
    out = os.path.join(tmp, f"seg{n:02d}.mp4")
    clipper.sh(["ffmpeg", "-v", "error", "-y"] + ins + ["-filter_complex", fc, "-map", "[v]", "-map", am, "-shortest",
                "-af", f"aresample=48000,afade=t=in:st=0:d={FADE},afade=t=out:st={dur - FADE}:d={FADE}",
                "-c:v", "libx264", "-crf", "20", "-preset", "veryfast", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", out])
    return out, dur


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


def main(spec_path, out):
    spec = json.load(open(spec_path))
    tmp = tempfile.mkdtemp()
    segs = spec["segments"]
    first = segs[0]
    parts = [card(spec["title"], spec.get("subtitle", ""), INTRO, first["file"], first["start"] + 2, tmp, "intro")]
    chapters = [("0:00", "Intro")]
    pos = INTRO
    for n, s in enumerate(segs, 1):
        p, d = render_segment(s, n, len(segs), tmp)
        chapters.append((f"{int(pos // 60)}:{int(pos % 60):02d}", f"#{n} {s['label']}"))
        parts.append(p); pos += d
        print(f"segment {n}/{len(segs)} ok", file=sys.stderr)
    parts.append(card("SUBSCRIBE FOR MORE", "new GTA 6 moments every day", OUTRO, segs[-1]["file"], segs[-1]["start"] + 2, tmp, "outro"))
    lst = os.path.join(tmp, "list.txt")
    open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
    joined = ["-f", "concat", "-safe", "0", "-i", lst]      # read the parts directly: no extra full-length copy on disk
    # two-pass loudness normalisation (one pass lands ~1 LU off on long files)
    import re as _re
    r = subprocess.run(["ffmpeg", "-hide_banner"] + joined + ["-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    m = json.loads(r[r.rindex("{"):r.rindex("}") + 1])
    ln = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
          f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    clipper.sh(["ffmpeg", "-v", "error", "-y"] + joined + ["-c:v", "copy", "-af", ln,
                "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", out])
    open(out + ".chapters.txt", "w").write("\n".join(f"{a} {b}" for a, b in chapters) + "\n")
    print(out)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
