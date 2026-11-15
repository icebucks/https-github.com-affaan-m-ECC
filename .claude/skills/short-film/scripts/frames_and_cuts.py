#!/usr/bin/env python3
"""Extract every frame of a video, write labelled contact sheets and a cut list.

Usage: frames_and_cuts.py VIDEO OUT_DIR [--width 480] [--cols 6] [--rows 6] [--thresh 2.5] [--review]

Writes OUT_DIR/frames/f00000.png ..., OUT_DIR/sheets/sheet_000.png ... (frame number + time on
each tile), OUT_DIR/frame_diff.tsv (mean absolute difference to the previous frame) and
OUT_DIR/cuts.tsv (frames whose difference is a spike against the local median: candidate
hard cuts; check soft cuts and dissolves by eye on the sheets).
Needs ffmpeg/ffprobe on PATH and: numpy pillow
"""
import argparse, json, os, subprocess
from fractions import Fraction
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ap = argparse.ArgumentParser()
ap.add_argument("video"); ap.add_argument("out")
ap.add_argument("--width", type=int, default=480, help="frame width to extract (small is enough)")
ap.add_argument("--cols", type=int, default=6); ap.add_argument("--rows", type=int, default=6)
ap.add_argument("--thresh", type=float, default=2.5, help="spike factor over the local median diff")
ap.add_argument("--review", action="store_true", help="also write review.mp4: frame number + time burned in, "
                "a red bar on candidate cuts, original audio (no ffmpeg drawtext needed)")
a = ap.parse_args()

probe = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
    "stream=r_frame_rate,width,height", "-of", "json", a.video]))["streams"][0]
fps = Fraction(probe["r_frame_rate"])
fdir = os.path.join(a.out, "frames"); os.makedirs(fdir, exist_ok=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.video, "-vf", f"scale={a.width}:-2", "-vsync", "0",
                os.path.join(fdir, "f%05d.png")], check=True)
files = sorted(f for f in os.listdir(fdir) if f.endswith(".png")); n = len(files)

def t_of(i): return float(i / fps)

prev, diff = None, []
for f in files:
    g = np.asarray(Image.open(os.path.join(fdir, f)).convert("L").resize((160, 90)), dtype=np.float32)
    diff.append(0.0 if prev is None else float(np.abs(g - prev).mean())); prev = g
d = np.array(diff)
with open(os.path.join(a.out, "frame_diff.tsv"), "w") as fh:
    fh.write("frame\ttime_s\tmean_abs_diff\n")
    for i, v in enumerate(d): fh.write(f"{i}\t{t_of(i):.3f}\t{v:.2f}\n")

cuts = []
for i in range(1, n):
    lo, hi = max(1, i - 6), min(n, i + 7)
    med = np.median(np.delete(d[lo:hi], i - lo)) if hi - lo > 1 else 0
    if d[i] > max(8.0, a.thresh * max(med, 1.0)): cuts.append(i)
with open(os.path.join(a.out, "cuts.tsv"), "w") as fh:
    # peak = 1 when the spike is the largest within +-1 frame. Fast motion right after a cut
    # also spikes (peak = 0); one-frame flashes can be peak = 0 too, so check every row by eye.
    fh.write("frame\ttime_s\tdiff\tpeak\tframes_to_next\n")
    for k, c in enumerate(cuts):
        nxt = cuts[k + 1] if k + 1 < len(cuts) else n
        peak = int(d[c] >= d[max(0, c - 1):c + 2].max())
        fh.write(f"{c}\t{t_of(c):.3f}\t{d[c]:.1f}\t{peak}\t{nxt - c}\n")

sdir = os.path.join(a.out, "sheets"); os.makedirs(sdir, exist_ok=True)
try: font = ImageFont.truetype("DejaVuSansMono.ttf", 16)
except OSError:
    try: font = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 16)
    except OSError: font = ImageFont.load_default()
per, cutset = a.cols * a.rows, set(cuts)
for s0 in range(0, n, per):
    tiles = [Image.open(os.path.join(fdir, files[i])).convert("RGB") for i in range(s0, min(s0 + per, n))]
    tw, th = tiles[0].size
    sheet = Image.new("RGB", (a.cols * tw, a.rows * th), (40, 40, 40))
    for k, im in enumerate(tiles):
        i = s0 + k; dr = ImageDraw.Draw(im)
        dr.rectangle([0, 0, 150, 20], fill=(200, 0, 0) if i in cutset else (0, 0, 0))
        dr.text((3, 1), f"{i} {t_of(i):.2f}s", fill=(255, 255, 0), font=font)
        sheet.paste(im, ((k % a.cols) * tw, (k // a.cols) * th))
    sheet.save(os.path.join(sdir, f"sheet_{s0:05d}.png"))

if a.review:
    rdir = os.path.join(a.out, "review_frames"); os.makedirs(rdir, exist_ok=True)
    for i, f in enumerate(files):
        im = Image.open(os.path.join(fdir, f)).convert("RGB"); dr = ImageDraw.Draw(im)
        dr.rectangle([0, 0, 170, 22], fill=(200, 0, 0) if i in cutset else (0, 0, 0))
        dr.text((4, 2), f"{i} {t_of(i):.3f}s", fill=(255, 255, 0), font=font)
        im.save(os.path.join(rdir, f"r{i:05d}.png"))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(fps), "-i", os.path.join(rdir, "r%05d.png"),
                    "-i", a.video, "-map", "0:v", "-map", "1:a?", "-c:v", "libx264", "-pix_fmt", "yuv420p",
                    "-crf", "20", "-c:a", "aac", "-shortest", os.path.join(a.out, "review.mp4")], check=True)

print(f"{n} frames at {fps} fps ({float(fps):.3f}); {len(cuts)} candidate cuts "
      f"({sum(int(d[c] >= d[max(0, c - 1):c + 2].max()) for c in cuts)} local peaks); "
      f"{-(-n // per)} sheets (red label = candidate cut)")
