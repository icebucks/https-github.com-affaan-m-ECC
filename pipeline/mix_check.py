#!/usr/bin/env python3
"""Verständlichkeits-Prüfung des FERTIGEN Mixes (Stimme + Atmo + Musik + Effekte):
Whisper transkribiert den Mix, verglichen wird mit dem Sprechtext (Wortfehlerrate).
Aufruf: python3 mix_check.py <mix.wav> <script.json> [max_wer_prozent=8]
Exit 3, wenn der Erzähler nicht sauber verständlich ist.
"""
import json, re, subprocess, sys, warnings
warnings.filterwarnings("ignore")
import numpy as np
import jiwer
from faster_whisper import WhisperModel

def norm(s):
    s = s.lower().replace("ß", "ss")
    s = re.sub(r"[^\wäöü ]", " ", s)
    return re.sub(r"\s+", " ", s).strip()

mix, script = sys.argv[1], json.load(open(sys.argv[2], encoding="utf-8"))
limit = float(sys.argv[3]) if len(sys.argv) > 3 else 8.0
raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", mix, "-ar", "16000", "-ac", "1", "-f", "f32le", "-"], capture_output=True, check=True).stdout
audio = np.frombuffer(raw, dtype=np.float32)
m = WhisperModel("medium", device="cpu", compute_type="int8")
segs, _ = m.transcribe(audio, language="de", beam_size=5, vad_filter=False)
hyp = " ".join(s.text for s in segs)
o = jiwer.process_words(norm(script["erzaehltext"]), norm(hyp))
wer = o.wer * 100
print(f"Verständlichkeit im Mix: {wer:.1f} % Wortfehler (Grenze {limit:.0f} %)")
print("Whisper hört:", hyp.strip())
sys.exit(3 if wer > limit else 0)
