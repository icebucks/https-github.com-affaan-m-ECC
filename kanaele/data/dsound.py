"""Soundtrack for the data channel: own music bed (beyondexcuses/sound.py) + CC0 sound effects from wyzowl/sfx-kit.
Usage: dsound.py events.json duration turn_time out.wav
Events: everything sound.py knows, plus ["sfx", time, sound_id, gain_db] – the sound's sync point lands exactly on `time`."""
import json, os, subprocess, sys, wave
import numpy as np
import soundfile as sf
from scipy.signal import resample_poly

HERE = os.path.dirname(os.path.abspath(__file__))
SFX = os.path.join(HERE, "assets", "sfx")
SOUND_PY = os.path.join(HERE, "..", "..", "beyondexcuses", "sound.py")
SR = 44100

ev_file, DUR, TURN, OUT = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
events = json.load(open(ev_file))
bed_ev = [e for e in events if e[0] != "sfx"]
fx_ev = [e for e in events if e[0] == "sfx"]
bed_ev = [e for e in bed_ev if e[0] != "music"]

# 1. music bed: own procedural track (music.py) if the video asks for one, else the shared sound engine
mus = [e for e in events if e[0] == "music"]
tmp_ev = OUT + ".bed.json"
if mus:
    sys.path.insert(0, HERE)
    import music
    _, style, bpm, build, drop, outro, seed = mus[0]
    bed = music.render(style, bpm, DUR, dict(build=build, drop=drop, outro=outro), seed)
    mix = bed * 0.55
else:
    json.dump(bed_ev, open(tmp_ev, "w"))
    subprocess.run(["python3", SOUND_PY, tmp_ev, str(DUR), str(TURN), OUT + ".bed.wav"], check=True)
    bed, sr = sf.read(OUT + ".bed.wav.raw.wav", dtype="float32")
    assert sr == SR
    mix = bed * 0.5

# 2. sound effects on their sync points
meta = {s["id"]: s for s in json.load(open(os.path.join(SFX, "sounds.json")))["sounds"]}
for _, t, sid, gain_db in fx_ev:
    s = meta[sid]
    x, xsr = sf.read(os.path.join(SFX, s["file"]), dtype="float32")
    if x.ndim == 1: x = np.stack([x, x], 1)
    if xsr != SR: x = resample_poly(x, SR, xsr, axis=0).astype(np.float32)
    start = int(round((t - s["sync"]["at"]) * SR))
    if start < 0: x = x[-start:]; start = 0
    end = min(len(mix), start + len(x))
    if end > start: mix[start:end] += x[: end - start] * (10 ** (gain_db / 20))

mix = np.tanh(mix * 1.1) / 1.1                      # soft limiter
with wave.open(OUT + ".raw.wav", "wb") as f:
    f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR); f.writeframes((np.clip(mix, -1, 1) * 32767).astype(np.int16).tobytes())
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", OUT + ".raw.wav", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "44100", OUT], check=True)
for f in (tmp_ev, OUT + ".bed.wav", OUT + ".bed.wav.raw.wav"):
    if os.path.exists(f): os.remove(f)
