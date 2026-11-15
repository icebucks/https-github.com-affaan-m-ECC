#!/usr/bin/env python3
"""Edit the music itself with automation curves: level, high/low-pass, reverb send, varispeed,
fade, then loudness-normalise and limit. The DJ moves, not added sound effects.

Usage: music_fx.py SPEC.json         (writes the WAV named in the spec, prints LUFS + true peak)
       music_fx.py --example         (prints an example spec)

All automation keys are [source_time_seconds, value] pairs, linearly interpolated, and keyed in
SOURCE time (seconds in the original song), so a move stays on its beat when you change the
excerpt. Speed is applied last (tape style: pitch follows speed). Make two specs, "strong" and
"subtle", so the listener can say more or less.
Needs: numpy scipy soundfile pedalboard
"""
import json, sys
import numpy as np, soundfile as sf
from scipy.signal import resample_poly
from pedalboard import Pedalboard, Reverb, HighpassFilter, LowpassFilter

EXAMPLE = {
    "source": "song.wav", "out": "edit_strong.wav",
    "start": 12.7, "end": 42.2, "tail": 2.6,
    "level_db":    [[12.7, -16], [14.9, -8], [15.6, -3], [15.67, -4], [22.35, -3.5], [22.36, 0]],
    "highpass_hz": [[12.7, 940], [15.0, 290], [15.62, 40]],
    "lowpass_hz":  [[38.9, 20000], [42.2, 700]],
    "reverb_send_db": [[12.7, -3], [15.57, -6], [15.67, -12], [22.35, -12], [22.36, -22], [38.9, -20], [42.2, -2]],
    "reverb": {"room_size": 0.85, "damping": 0.4},
    "speed": [[12.7, 1.0], [21.9, 1.0], [22.3, 1.015], [22.36, 1.0]],
    "fade_out": [38.9, 42.2],
    "lufs": -14.0, "ceiling_dbtp": -1.0,
}

def curve(keys, t, default):
    if not keys: return np.full(len(t), float(default))
    k = np.array(keys, float); return np.interp(t, k[:, 0], k[:, 1])

def fx(x, board, sr): return board(x.T.astype(np.float32), sr).T.astype(np.float64)

def auto_filter(x, kind, hz, sr, k=18):
    """Time-varying filter: crossfade between k fixed-cutoff copies (no zipper noise)."""
    lo, hi = float(hz.min()), float(hz.max())
    mk = (lambda c: LowpassFilter(c)) if kind == "lp" else (lambda c: HighpassFilter(c))
    if hi / lo < 1.01: return fx(x, Pedalboard([mk(lo)]), sr)
    cuts = lo * (hi / lo) ** np.linspace(0, 1, k)
    vers = np.stack([fx(x, Pedalboard([mk(c)]), sr) for c in cuts])
    pos = np.log(hz / lo) / np.log(hi / lo) * (k - 1); i0 = np.floor(pos).astype(int).clip(0, k - 2)
    w = (pos - i0)[:, None]; idx = np.arange(len(x))
    return vers[i0, idx] * (1 - w) + vers[i0 + 1, idx] * w

def varispeed(x, rate):
    """rate[n] = source samples consumed per output sample."""
    up = 4; xu = resample_poly(x, up, 1, axis=0)
    pos = np.concatenate([[0], np.cumsum(rate[:-1])]); n = int(np.searchsorted(pos, len(x) - 2))
    p = pos[:n] * up; return np.stack([np.interp(p, np.arange(len(xu)), xu[:, c]) for c in range(x.shape[1])], 1)

def lufs(x, sr):
    """ITU-R BS.1770 integrated loudness (K-weighting, 400 ms blocks, absolute + relative gate)."""
    import math
    from scipy.signal import lfilter
    # high-shelf pre-filter and RLB high-pass, computed for any sample rate
    f0, G, Q = 1681.974450955533, 3.999843853973347, 0.7071752369554196
    K = math.tan(math.pi * f0 / sr); Vh = 10 ** (G / 20); Vb = Vh ** 0.4996667741545416
    a0 = 1 + K / Q + K * K
    pb = [(Vh + Vb * K / Q + K * K) / a0, 2 * (K * K - Vh) / a0, (Vh - Vb * K / Q + K * K) / a0]
    pa = [1, 2 * (K * K - 1) / a0, (1 - K / Q + K * K) / a0]
    f0, Q = 38.13547087602444, 0.5003270373238773; K = math.tan(math.pi * f0 / sr)
    rb = [1, -2, 1]; ra = [1, 2 * (K * K - 1) / (1 + K / Q + K * K), (1 - K / Q + K * K) / (1 + K / Q + K * K)]
    y = lfilter(rb, ra, lfilter(pb, pa, x, axis=0), axis=0)
    blk, hop = int(0.4 * sr), int(0.1 * sr)
    ms = np.array([(y[i:i + blk] ** 2).mean(0).sum() for i in range(0, len(y) - blk, hop)])
    l = -0.691 + 10 * np.log10(np.maximum(ms, 1e-12)); g = ms[l > -70]
    if not len(g): return -70.0
    rel = -0.691 + 10 * np.log10(g.mean()) - 10; g2 = g[(-0.691 + 10 * np.log10(g)) > rel]
    return float(-0.691 + 10 * np.log10(g2.mean()))

def true_peak_db(x):
    return float(20 * np.log10(max(1e-9, np.abs(resample_poly(x, 4, 1, axis=0)).max())))

def limit(x, sr, ceiling_db, look=0.005, release=0.08):
    """Look-ahead peak limiter with no make-up gain (some library limiters add gain silently)."""
    c = 10 ** (ceiling_db / 20) * 0.97
    peak = np.abs(resample_poly(x, 4, 1, axis=0)).max(1).reshape(-1, 4).max(1)[:len(x)]
    need = np.minimum(1.0, c / np.maximum(peak, 1e-9))
    L = int(look * sr); need = np.concatenate([need[L:], np.ones(L)])
    from scipy.ndimage import minimum_filter1d
    need = minimum_filter1d(need, 2 * L + 1)
    g = np.empty_like(need); cur = 1.0; r = np.exp(-1 / (release * sr))
    for i, v in enumerate(need):
        cur = v if v < cur else v + (cur - v) * r; g[i] = cur
    return x * g[:, None]

def build(spec):
    x, sr = sf.read(spec["source"], always_2d=True)
    s0, s1, tail = spec["start"], spec["end"], spec.get("tail", 0.0)
    x = np.concatenate([x[int(s0 * sr):int(s1 * sr)], np.zeros((int(tail * sr), x.shape[1]))])
    t = s0 + np.arange(len(x)) / sr
    dry = x
    if spec.get("highpass_hz"): dry = auto_filter(dry, "hp", curve(spec["highpass_hz"], t, 20), sr)
    if spec.get("lowpass_hz"): dry = auto_filter(dry, "lp", curve(spec["lowpass_hz"], t, 20000), sr)
    if spec.get("reverb_send_db"):
        rv = spec.get("reverb", {})
        wet = fx(dry, Pedalboard([Reverb(room_size=rv.get("room_size", 0.85), damping=rv.get("damping", 0.4),
                                         wet_level=1.0, dry_level=0.0, width=1.0)]), sr)
        dry = dry + wet * (10 ** (curve(spec["reverb_send_db"], t, -60) / 20))[:, None]
    y = dry * (10 ** (curve(spec.get("level_db"), t, 0) / 20))[:, None]
    if spec.get("fade_out"):
        f0, f1 = spec["fade_out"]; u = np.clip((t - f0) / (f1 - f0), 0, 1)
        y = y * (np.cos(u * np.pi / 2) ** 2)[:, None] * (t <= f1 + tail)[:, None]
    if spec.get("speed"): y = varispeed(y, curve(spec["speed"], t, 1.0))
    if spec.get("lufs") is not None:
        y = y * 10 ** ((spec["lufs"] - lufs(y, sr)) / 20)
        y = limit(y, sr, spec.get("ceiling_dbtp", -1.0))
    sf.write(spec["out"], y.astype(np.float32), sr, subtype="PCM_24")
    print(f"{spec['out']}: {len(y) / sr:.2f} s, {lufs(y, sr):.1f} LUFS, true peak {true_peak_db(y):.1f} dBTP")

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"): print(__doc__); sys.exit(0)
    if sys.argv[1] == "--example": print(json.dumps(EXAMPLE, indent=1)); sys.exit(0)
    build(json.load(open(sys.argv[1])))
