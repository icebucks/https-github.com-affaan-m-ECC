#!/usr/bin/env python3
"""Erzählerstimme mit OmniVoice (k2-fsa, Engine aus VoiceStudio; lokal, kostenlos, Apache 2.0).

Die Stimme wird von unserer festen Erzähler-Referenz geklont (pipeline/voices/erzaehler_ref.wav),
Satz für Satz erzeugt (kontrollierte Pausen) und anschließend mit Whisper Wort für Wort
zeitgestempelt; die erkannten Wörter werden auf die Skript-Wörter ausgerichtet.

Aufruf: python3 tts_omni.py <request.json>
request = { "sentences": [...], "out_wav": ..., "out_words": ..., "lead_in": 0.5, "pause": 0.34,
            "pause_short": 0.6, "pause_before_last": 0.8, "speed": 0.92, "num_step": 32 }
"""
import difflib
import json
import os
import re
import subprocess
import sys
import tempfile
import warnings

warnings.filterwarnings("ignore")
import numpy as np  # noqa: E402
import soundfile as sf  # noqa: E402
import torch  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
REF_WAV = os.path.join(HERE, "voices", "erzaehler_ref.wav")
REF_TXT = open(os.path.join(HERE, "voices", "erzaehler_ref.txt"), encoding="utf-8").read().strip()
PUNCT = ",.;:!?…–—\"'«»„“”()"
SR = 24000


def tokens(sentence):
    return [w.strip(PUNCT) for w in sentence.split() if re.search(r"[\wÄÖÜäöüß]", w.strip(PUNCT))]


def norm(w):
    return re.sub(r"[^\wäöü]", "", w.lower().replace("ß", "ss"))


def align(script_toks, rec_words, dur):
    """Whisper-Wörter (text,start,end) auf Skript-Wörter abbilden; Lücken interpolieren."""
    a = [norm(t) for t in script_toks]
    b = [norm(w[0]) for w in rec_words]
    times = [None] * len(a)
    sm = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
    for blk in sm.get_matching_blocks():
        for k in range(blk.size):
            times[blk.a + k] = (rec_words[blk.b + k][1], rec_words[blk.b + k][2])
    # ersetzte Bereiche (z. B. Komposita anders getrennt) gleichmäßig aufteilen
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "replace" and j2 > j1:
            s, e = rec_words[j1][1], rec_words[j2 - 1][2]
            n = i2 - i1
            for k in range(n):
                times[i1 + k] = (s + (e - s) * k / n, s + (e - s) * (k + 1) / n)
    # verbleibende Lücken: zwischen Nachbarn interpolieren
    known = [i for i, t in enumerate(times) if t]
    if not known:
        step = dur / max(1, len(a))
        return [(i * step, (i + 1) * step) for i in range(len(a))], len(a)
    missing = 0
    for i, t in enumerate(times):
        if t:
            continue
        missing += 1
        prev = max([k for k in known if k < i], default=None)
        nxt = min([k for k in known if k > i], default=None)
        s = times[prev][1] if prev is not None else 0.0
        e = times[nxt][0] if nxt is not None else dur
        gap_i = (nxt if nxt is not None else len(a)) - (prev if prev is not None else -1) - 1
        pos = i - (prev if prev is not None else -1) - 1
        times[i] = (s + (e - s) * pos / gap_i, s + (e - s) * (pos + 1) / gap_i)
    return times, missing


def main():
    req = json.load(open(sys.argv[1], encoding="utf-8"))
    torch.set_num_threads(int(os.environ.get("OMNI_THREADS", "4")))
    from omnivoice import OmniVoice
    from faster_whisper import WhisperModel
    model = OmniVoice.from_pretrained("k2-fsa/OmniVoice", device_map="cpu", dtype=torch.float32)
    prompt = model.create_voice_clone_prompt(ref_audio=REF_WAV, ref_text=REF_TXT)
    asr = WhisperModel(os.environ.get("WHISPER_MODEL", "medium"), device="cpu", compute_type="int8")

    sentences = req["sentences"]
    pieces = [np.zeros(int(SR * req.get("lead_in", 0.5)), dtype=np.float32)]
    t = len(pieces[0]) / SR
    words, warn = [], []
    for si, sent in enumerate(sentences):
        audio = model.generate(text=sent, language="de", voice_clone_prompt=prompt,
                               speed=req.get("speed", 0.92), num_step=req.get("num_step", 32))[0].astype(np.float32)
        # Stille am Rand kappen (gleichmäßige Pausen)
        thr = 0.01 * (np.max(np.abs(audio)) or 1)
        idx = np.where(np.abs(audio) > thr)[0]
        if len(idx):
            audio = audio[max(0, idx[0] - int(0.04 * SR)): min(len(audio), idx[-1] + int(0.08 * SR))]
        dur = len(audio) / SR
        a16 = np.interp(np.arange(0, len(audio), SR / 16000), np.arange(len(audio)), audio).astype(np.float32)
        segs, _ = asr.transcribe(a16, language="de", word_timestamps=True, beam_size=5, vad_filter=False)
        rec = [(w.word.strip(), w.start, w.end) for s in segs for w in (s.words or [])]
        toks = tokens(sent)
        tt, missing = align(toks, rec, dur)
        heard = " ".join(r[0] for r in rec)
        ratio = difflib.SequenceMatcher(a=[norm(x) for x in toks], b=[norm(r[0]) for r in rec]).ratio()
        if ratio < 0.85:
            warn.append(f"Satz {si}: Whisper hört „{heard}“ (Übereinstimmung {ratio:.0%})")
        for w, (s, e) in zip(toks, tt):
            words.append({"text": w, "start": round(t + s, 3), "end": round(t + e, 3), "satz": si})
        pieces.append(audio)
        t += dur
        if si < len(sentences) - 1:
            p = req.get("pause_before_last", 0.8) if si == len(sentences) - 2 else (req.get("pause_short", 0.6) if len(toks) <= 3 else req.get("pause", 0.34))
            pieces.append(np.zeros(int(SR * p), dtype=np.float32))
            t += p
        print(f"  Satz {si + 1}/{len(sentences)} ({dur:.1f} s, Whisper {ratio:.0%})", file=sys.stderr, flush=True)
    pieces.append(np.zeros(int(SR * 0.3), dtype=np.float32))
    audio = np.concatenate(pieces)
    audio = audio / (np.max(np.abs(audio)) or 1) * 0.89
    with tempfile.TemporaryDirectory() as td:
        raw = os.path.join(td, "raw.wav")
        sf.write(raw, audio, SR)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-ar", "44100", req["out_wav"]], check=True)
    json.dump({"duration": round(len(audio) / SR, 3), "words": words, "warnings": warn},
              open(req["out_words"], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for m in warn:
        print("WARN", m, file=sys.stderr)


if __name__ == "__main__":
    main()
