"""Highlight windows in a no-commentary recording: motion + loudness z-scores per 20 s window.
python3 clips/highlights.py <video.ts> -> top 6 windows (start s, z-score, motion, dB). Always check the windows visually afterwards."""
import sys, subprocess, numpy as np
p, win = sys.argv[1], 20
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-vf", "fps=2,scale=64:36,format=gray", "-f", "rawvideo", "-"], capture_output=True).stdout
v = np.frombuffer(raw, np.uint8).reshape(-1, 36, 64).astype(np.float32)
mot = np.abs(np.diff(v, axis=0)).mean((1, 2))
a = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-vn", "-ac", "1", "-ar", "8000", "-f", "f32le", "-"], capture_output=True).stdout, np.float32)
n = int(min(len(mot) / 2, len(a) / 8000)) // win
rows = []
for i in range(n):
    m = mot[i * win * 2:(i + 1) * win * 2].mean()
    seg = a[i * win * 8000:(i + 1) * win * 8000]
    l = 20 * np.log10(np.sqrt((seg ** 2).mean()) + 1e-9)
    rows.append((i * win, m, l))
r = np.array(rows)
z = (r[:, 1] - r[:, 1].mean()) / (r[:, 1].std() + 1e-6) + (r[:, 2] - r[:, 2].mean()) / (r[:, 2].std() + 1e-6)
for k in np.argsort(-z)[:6]: print(f"{int(r[k,0])} z={z[k]:.2f} mot={r[k,1]:.1f} dB={r[k,2]:.1f}")
