"""YouTube thumbnail (1280x720 JPEG, < 2 MB) from one gameplay frame: darkened left side, 2 big text lines, logo badge.
  python3 clips/thumb.py <video> <second> "LINE ONE" "LINE TWO" <out.jpg>
Line 1 white, line 2 neon red (Virlix style, see banner.py). Keep it to ≤ 4 words in total – it must read at phone size."""
import os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
if not os.path.exists(FONT): FONT = os.path.join(HERE, "..", "beyondexcuses", "fonts", "Poppins-Bold.ttf")
W, H = 1280, 720


def grab(video, sec):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(sec), "-i", video, "-frames:v", "1", "-vf", f"scale={W}:{H}",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    return Image.frombytes("RGB", (W, H), raw)


def fit(draw, s, maxw, size):
    while size > 40 and draw.textlength(s, font=ImageFont.truetype(FONT, size)) > maxw: size -= 4
    return ImageFont.truetype(FONT, size)


def main(video, sec, l1, l2, out):
    im = grab(video, float(sec))
    # punchier image: a bit more contrast and saturation
    a = np.asarray(im).astype(np.float32) / 255
    a = np.clip((a - 0.5) * 1.15 + 0.5, 0, 1)
    g = a.mean(2, keepdims=True); a = np.clip(g + (a - g) * 1.25, 0, 1)
    # dark gradient on the left for the text
    ramp = np.clip(1 - np.linspace(0, 1, W) / 0.62, 0, 1) ** 1.3
    a *= (1 - 0.72 * ramp)[None, :, None]
    im = Image.fromarray((a * 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    f1 = fit(d, l1, 700, 150); f2 = fit(d, l2, 700, 150)
    y = 190
    for s, f, col in ((l1, f1, (255, 255, 255)), (l2, f2, (255, 59, 92))):
        glow = Image.new("L", (W, H), 0); ImageDraw.Draw(glow).text((60, y), s, font=f, fill=255)
        im.paste(Image.new("RGB", (W, H), (0, 0, 0)), (0, 0), glow.filter(ImageFilter.GaussianBlur(14)).point(lambda v: int(v * 0.9)))
        d = ImageDraw.Draw(im)
        d.text((60, y), s, font=f, fill=col, stroke_width=8, stroke_fill=(0, 0, 0))
        y += f.size + 20
    logo = os.path.join(HERE, "assets", "logo_badge.png")
    if os.path.exists(logo):
        lg = Image.open(logo).convert("RGBA"); lg.thumbnail((150, 150))
        im.paste(lg, (W - lg.width - 30, H - lg.height - 30), lg)
    im.save(out, quality=90)
    print(out, os.path.getsize(out) // 1024, "KB")


if __name__ == "__main__":
    main(*sys.argv[1:6])
