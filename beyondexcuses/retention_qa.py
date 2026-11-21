"""Retention standard v2 check for a finished episode MP4 (see episodes.md "Retention-Standard v2").
  python3 retention_qa.py Folge29_..._EN.mp4 [--payoff 6.5]
Checks (all must be ✅ before delivery):
  length 11–13.5 s · motion in the first 0.5 s · no static span > 1.0 s · loop: last frame ≈ first frame
  · payoff (turn) at or before 7.0 s (pass --payoff = TURN from the episode file)
Background: Part 19 (Waiter vs Builder, 21.11.) lost 47 % of viewers in the first 3 s, then ~2–3 %/s,
then a second drop on the static end card (15–17 s)."""
import subprocess, sys
import numpy as np

W, H, FPS = 108, 192, 10


def frames(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vf", f"fps={FPS},scale={W}:{H},format=gray",
                          "-f", "rawvideo", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, H, W).astype(float)


def main(path, payoff=None):
    f = frames(path); n = len(f); dur = n / FPS
    diff = np.abs(np.diff(f, axis=0)).mean(axis=(1, 2))           # change between frames (0–255)
    still = diff < 0.6
    spans, run = [], 0
    for i, s in enumerate(still):
        run = run + 1 if s else 0
        if run == int(1.0 * FPS) + 1: spans.append(i / FPS)
    first_motion = diff[: int(0.5 * FPS)].max() if n > 5 else 0
    loop = np.abs(f[-1] - f[0]).mean()
    ok = lambda b: "✅" if b else "⚠️"
    print(f"{ok(11 <= dur <= 13.5)} length {dur:.1f} s (target 11–13.5)")
    print(f"{ok(first_motion >= 1.5)} motion in first 0.5 s: {first_motion:.1f} (≥ 1.5)")
    print(f"{ok(not spans)} static spans > 1 s: {', '.join(f'{s:.1f}s' for s in spans) or 'none'}")
    print(f"{ok(loop <= 12)} loop: last vs first frame difference {loop:.1f} (≤ 12)")
    if payoff is not None: print(f"{ok(payoff <= 7.0)} payoff at {payoff:.1f} s (≤ 7.0)")
    return dur


if __name__ == "__main__":
    p = float(sys.argv[sys.argv.index("--payoff") + 1]) if "--payoff" in sys.argv else None
    main(sys.argv[1], p)
