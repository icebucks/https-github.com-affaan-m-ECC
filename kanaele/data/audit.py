"""Quality audit for finished videos (reach factors that can be measured without platform data).
Usage: python3 audit.py BN1_Billion_EN.mp4 [BN2_Tallest_EN.mp4 ...]  ->  audit/<name>_report.md + audit/<name>_ui.jpg

Measures
- UI overlap: bright text-like pixels (white/gold) under the TikTok interface (top tabs, right button column,
  bottom caption/username area). Conservative zones from TikTok's safe-zone template and 2026 creator guides.
- Motion per second (mean frame difference) -> "dead" seconds where people swipe away.
- Thumb-stop power of the first second: brightness, contrast, colourfulness (Hasler–Süsstrunk).
- Audio: loudness of the first 0.5 s vs. the rest, silent gaps, overall LUFS.
- Loop: how close the last frame is to the first.
- Smallest font sizes used in the episode script (phone legibility: >= 30 px at 1080 wide)."""
import os, re, subprocess, sys, json
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "audit")
W, H = 1080, 1920
ZONES = {   # name: (x0, y0, x1, y1) – content inside these is hidden or crowded on TikTok
    "top tabs": (0, 0, W, 210),
    "right buttons": (900, 760, W, 1660),
    "bottom caption": (0, 1450, 900, H),
}
SW, SH = 270, 480     # analysis resolution


def frames(path, fps):
    cmd = ["ffmpeg", "-v", "error", "-i", path, "-vf", f"fps={fps},scale={SW}:{SH}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, SH, SW, 3).astype(np.float32)


def text_mask(f):
    """bright white or gold pixels ~ text, numbers, labels"""
    r, g, b = f[..., 0], f[..., 1], f[..., 2]
    white = (r > 200) & (g > 200) & (b > 200)
    gold = (r > 210) & (g > 160) & (b < 140)
    return white | gold


def colourfulness(f):
    r, g, b = f[..., 0], f[..., 1], f[..., 2]
    rg = r - g; yb = 0.5 * (r + g) - b
    return float(np.sqrt(rg.std() ** 2 + yb.std() ** 2) + 0.3 * np.sqrt(rg.mean() ** 2 + yb.mean() ** 2))


def audio_stats(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vn", "-ac", "1", "-ar", "22050", "-f", "f32le", "-"], capture_output=True).stdout
    x = np.frombuffer(raw, np.float32)
    if len(x) == 0: return None
    w = int(0.25 * 22050)
    rms = np.array([np.sqrt(np.mean(x[i:i + w] ** 2)) + 1e-9 for i in range(0, len(x) - w, w)])
    db = 20 * np.log10(rms)
    lufs = subprocess.run(["ffmpeg", "-nostats", "-i", path, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", lufs)
    return dict(first_half_s_db=float(db[:2].mean()), median_db=float(np.median(db)), silent_windows=int((db < -45).sum()),
                lufs=float(m[-1]) if m else None)


def font_sizes(script):
    if not script or not os.path.exists(script): return []
    src = open(script).read()
    sizes = [int(float(s)) for s in re.findall(r"F_(?:CAP|SANS),\s*([\d.]+)", src)]
    return sorted(set(sizes))


def audit(path):
    name = os.path.splitext(os.path.basename(path))[0]
    fps = 4
    F = frames(path, fps)
    n = len(F); dur = n / fps
    sx, sy = SW / W, SH / H
    # UI overlap per zone (share of frames where text-like pixels sit in the zone)
    overlap = {}
    worst = {}
    for zn, (x0, y0, x1, y1) in ZONES.items():
        a = [text_mask(f[int(y0 * sy):int(y1 * sy), int(x0 * sx):int(x1 * sx)]).mean() for f in F]
        a = np.array(a)
        hit = a > 0.004
        overlap[zn] = dict(share_of_frames=float(hit.mean()), seconds=[float(round(i / fps, 2)) for i in np.where(hit)[0]][:40])
        worst[zn] = int(np.argmax(a))
    # motion
    diff = np.abs(np.diff(F.mean(-1), axis=0)).mean(axis=(1, 2))
    per_s = [float(diff[int(s * fps):int((s + 1) * fps)].mean()) for s in range(int(dur))]
    dead = [s for s, v in enumerate(per_s) if v < 1.2]
    # first second
    f0 = F[: fps]
    thumb = dict(brightness=float(f0.mean()), contrast=float(f0.mean(-1).std()), colourfulness=float(np.mean([colourfulness(f) for f in f0])))
    loop = float(np.abs(F[-1] - F[min(1, n - 1)]).mean())   # frame 0 carries the opening flash
    num = re.search(r"BN(\d+)", name)
    script = os.path.join(HERE, f"bn{num.group(1)}.py") if num else None
    fonts = font_sizes(script)
    au = audio_stats(path)
    # visual: worst frames with zones drawn
    os.makedirs(OUT, exist_ok=True)
    tiles = []
    for zn, idx in worst.items():
        im = Image.fromarray(F[idx].astype(np.uint8)).resize((360, 640))
        d = ImageDraw.Draw(im, "RGBA")
        for z, (x0, y0, x1, y1) in ZONES.items():
            d.rectangle([x0 / 3, y0 / 3, x1 / 3, y1 / 3], fill=(255, 0, 60, 70) if z == zn else (255, 0, 60, 35), outline=(255, 40, 80, 200))
        d.text((6, 620), f"{zn} @ {idx / fps:.2f}s", fill=(255, 255, 255, 255))
        tiles.append(im)
    sheet = Image.new("RGB", (360 * len(tiles), 640))
    for i, im in enumerate(tiles): sheet.paste(im, (360 * i, 0))
    sheet.save(os.path.join(OUT, f"{name}_ui.jpg"), quality=88)
    rep = dict(video=name, duration=round(dur, 2), ui_overlap=overlap, motion_per_second=[round(v, 2) for v in per_s], dead_seconds=dead,
               first_second=thumb, loop_difference=round(loop, 1), font_sizes=fonts, audio=au)
    json.dump(rep, open(os.path.join(OUT, f"{name}_report.json"), "w"), indent=1)
    # short markdown verdict
    L = [f"# Audit {name} ({dur:.1f} s)", ""]
    for zn, o in overlap.items():
        flag = "⚠️" if o["share_of_frames"] > 0.05 else "✅"
        L.append(f"- {flag} Text unter **{zn}**: {o['share_of_frames'] * 100:.0f} % der Frames" + (f" (z. B. {o['seconds'][:6]} s)" if o["seconds"] else ""))
    L.append(f"- {'⚠️' if dead else '✅'} Bewegungsarme Sekunden: {dead or 'keine'}")
    L.append(f"- Erste Sekunde: Helligkeit {thumb['brightness']:.0f}/255, Kontrast {thumb['contrast']:.0f}, Farbigkeit {thumb['colourfulness']:.0f} "
             f"({'⚠️ eher dunkel/blass' if thumb['brightness'] < 60 or thumb['colourfulness'] < 25 else '✅'})")
    L.append(f"- Loop-Abstand letztes→erstes Bild: {loop:.1f} ({'✅ nahtlos' if loop < 25 else 'kein Loop'})")
    small = [s for s in fonts if s < 28]
    L.append(f"- {'⚠️' if small else '✅'} Kleinste Schriftgrößen: {fonts[:6]} (unter 28 px auf dem Handy schwer lesbar: {small or 'keine'})")
    if au:
        L.append(f"- Ton: {au['lufs']} LUFS, erste 0,5 s {au['first_half_s_db']:.0f} dB vs. Median {au['median_db']:.0f} dB, stille Fenster: {au['silent_windows']}")
    open(os.path.join(OUT, f"{name}_report.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))
    return rep


if __name__ == "__main__":
    for p in sys.argv[1:]: audit(p)
