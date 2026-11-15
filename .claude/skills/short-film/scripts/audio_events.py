#!/usr/bin/env python3
"""Measure an audio file: tempo, beats, onsets, level envelope, and 1 s listening windows.

Usage: audio_events.py AUDIO OUT_DIR [--cuts cuts.tsv] [--fps 24000/1001] [--automation]

Writes OUT_DIR/events.json (tempo, beats, onsets with strength, events, cut sync stats),
OUT_DIR/windows/wNNN_<time>.wav (one 1 s window per event, the event at 0.25 s, for
labelling by audio models or by ear) and, with --automation, OUT_DIR/automation.png +
automation.json (level, brightness, wetness proxy and pitch drift over time: what an editor
did to the music). offset_frames = onset - cut in frames: positive means the sound comes after the cut.
Run it on the mix for cut sync, and on each stem for that layer's events.
Times come from signal processing; never take times from model replies.
Needs: numpy scipy librosa soundfile (matplotlib for --automation)
"""
import argparse, json, os
from fractions import Fraction
import numpy as np, librosa, soundfile as sf

ap = argparse.ArgumentParser()
ap.add_argument("audio"); ap.add_argument("out")
ap.add_argument("--cuts", help="cuts.tsv from frames_and_cuts.py (adds cut sync stats)")
ap.add_argument("--fps", help="the video's exact frame rate (ffprobe r_frame_rate, e.g. 24000/1001); required with --cuts")
ap.add_argument("--delta", type=float, default=0.07, help="onset sensitivity (lower = more onsets)")
ap.add_argument("--automation", action="store_true")
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)
if a.cuts and not a.fps: ap.error("--fps is required with --cuts (use the rational rate from ffprobe)")
fps = float(Fraction(a.fps or "24")); sr, hop = 48000, 256
y, _ = librosa.load(a.audio, sr=sr, mono=True)

tempo, beats = librosa.beat.beat_track(y=y, sr=sr, hop_length=hop, units="time")
oenv = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop)
ons = librosa.onset.onset_detect(onset_envelope=oenv, sr=sr, hop_length=hop, units="time", delta=a.delta)
strength = [float(oenv[librosa.time_to_frames(t, sr=sr, hop_length=hop)]) for t in ons]
rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=1200)[0]
env_db = 20 * np.log10(np.maximum(rms, 1e-6))

events = []  # onsets closer than 100 ms are one event
for t, s in zip(ons, strength):
    if events and t - events[-1]["onsets"][-1] < 0.10:
        events[-1]["onsets"].append(round(float(t), 3)); events[-1]["strength"] = max(events[-1]["strength"], round(float(s), 2))
    else: events.append({"t": round(float(t), 3), "onsets": [round(float(t), 3)], "strength": round(float(s), 2)})

out = {"file": os.path.abspath(a.audio), "duration_s": round(len(y) / sr, 3),
       "tempo_bpm": round(float(np.atleast_1d(tempo)[0]), 1),
       "beats": [round(float(b), 3) for b in beats], "onsets": [round(float(t), 3) for t in ons],
       "events": events, "level_db_every_25ms": [round(float(v), 1) for v in env_db]}
if len(beats) > 4:
    ibi = np.diff(beats); out["beat_interval_s"] = {"median": round(float(np.median(ibi)), 4),
                                                     "min": round(float(ibi.min()), 4), "max": round(float(ibi.max()), 4)}
    out["frames_per_beat"] = round(float(np.median(ibi)) * fps, 2)

cuts = []
if a.cuts:
    with open(a.cuts) as fh:
        next(fh); rows = [l.rstrip("\n").split("\t") for l in fh if l.strip()]
    # keeps only peak rows from frames_and_cuts.py; after checking by eye, edit cuts.tsv by hand
    cuts = [float(r[1]) for r in rows if len(r) < 4 or r[3] == "1"]
    sync = []
    for c in cuts:
        near = min(ons, key=lambda t: abs(t - c)) if len(ons) else c
        sync.append({"cut_s": round(c, 3), "nearest_onset_s": round(float(near), 3),
                     "offset_frames": round(float(near - c) * fps, 2)})
    within2 = int(sum(abs(s["offset_frames"]) <= 2 for s in sync))
    out["cut_sync"] = {"cuts": len(cuts), "within_2_frames_of_onset": within2, "detail": sync}
    for c in cuts:  # a window for every cut with no onset near it, so silent cuts get checked too
        if not any(abs(e["t"] - c) < 0.06 for e in events):
            events.append({"t": round(c, 3), "onsets": [], "strength": 0.0, "cut_only": True})
    events.sort(key=lambda e: e["t"])

wdir = os.path.join(a.out, "windows"); os.makedirs(wdir, exist_ok=True)
ys, ssr = sf.read(a.audio)
for i, e in enumerate(events):
    s = max(0.0, e["t"] - 0.25); seg = ys[int(s * ssr):int(min(len(ys) / ssr, s + 1.0) * ssr)]
    e["window"] = f"w{i:03d}_{e['t']:07.3f}.wav"; e["event_offset_in_window_s"] = round(e["t"] - s, 3)
    if cuts:
        near = min(cuts, key=lambda c: abs(c - e["t"])); e["nearest_cut_s"] = round(near, 3)
        e["cut_offset_frames"] = round((e["t"] - near) * fps, 2)
    sf.write(os.path.join(wdir, e["window"]), seg, ssr, subtype="PCM_16")
json.dump(out, open(os.path.join(a.out, "events.json"), "w"), indent=1)
msg = f"tempo ~{out['tempo_bpm']} BPM, {len(ons)} onsets, {len(events)} events/windows"
if cuts: msg += f", {out['cut_sync']['within_2_frames_of_onset']}/{len(cuts)} cuts within 2 frames of an onset"
print(msg)

if a.automation:
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    from scipy.ndimage import minimum_filter1d, maximum_filter1d, uniform_filter1d
    h = 1200; t = np.arange(len(env_db)) * h / sr
    cen = librosa.feature.spectral_centroid(y=y, sr=sr, n_fft=4096, hop_length=h)[0]
    w = int(0.5 * sr / h)  # wetness proxy: level floor between notes vs local peak (higher = longer tails)
    wet = uniform_filter1d(minimum_filter1d(env_db, w) - maximum_filter1d(env_db, w), 8)
    C = np.abs(librosa.cqt(y, sr=sr, hop_length=hop, fmin=librosa.note_to_hz("C3"), n_bins=48 * 8, bins_per_octave=96))
    ft = librosa.time_to_frames(np.array(ons) + 0.06, sr=sr, hop_length=hop).clip(0, C.shape[1] - 1)
    midi = librosa.note_to_midi("C3") + C[:, ft].argmax(0) / 8.0; cents = (midi - np.round(midi)) * 100
    fig, ax = plt.subplots(4, 1, figsize=(20, 11), sharex=True)
    ax[0].plot(t, env_db); ax[0].set_ylabel("level dB"); ax[0].set_ylim(-60, 0)
    ax[1].plot(t, cen[:len(t)]); ax[1].set_yscale("log"); ax[1].set_ylabel("brightness Hz")
    ax[2].plot(t, wet); ax[2].set_ylabel("wetness (floor-peak dB)")
    ax[3].plot(ons, cents, "o", ms=4); ax[3].set_ylabel("pitch dev. cents"); ax[3].set_ylim(-60, 60); ax[3].axhline(0, color="k", lw=.5)
    for x in ax:
        for c in cuts: x.axvline(c, color="r", lw=.6, alpha=.6)
        x.grid(axis="x", alpha=.3)
    plt.tight_layout(); plt.savefig(os.path.join(a.out, "automation.png"), dpi=60)
    json.dump({"t": t.round(3).tolist(), "level_db": env_db.round(1).tolist(), "centroid_hz": cen.round(0).tolist(),
               "wetness": wet.round(2).tolist(), "onsets": [round(float(o), 3) for o in ons], "cents": cents.round(0).tolist()},
              open(os.path.join(a.out, "automation.json"), "w"))
    print("automation.png written (red lines = cuts)")
