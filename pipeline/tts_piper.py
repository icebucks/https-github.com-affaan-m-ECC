#!/usr/bin/env python3
"""Lokale deutsche Sprachausgabe mit Piper + exakte Wort-Zeitstempel.

Aufruf:  python3 tts_piper.py <request.json>
request = {
  "sentences": ["Satz eins.", ...],
  "voice": "/pfad/de-karlsson-low.onnx",
  "length_scale": 1.08,          # >1 = langsamer, ruhiger
  "lead_in": 0.5,                # Stille vor dem ersten Wort (Hook)
  "pause": 0.32,                 # Pause zwischen Sätzen
  "pause_short": 0.6,            # Pause nach sehr kurzen Sätzen (Dramatik)
  "pause_before_last": 0.8,
  "out_wav": "voice_raw.wav",
  "out_words": "words.json"
}
Die Wortzeiten kommen direkt aus Pipers Phonem-Dauern (keine Transkription nötig,
dadurch exakt und ohne Erkennungsfehler).
"""
import json
import re
import sys
import wave

import numpy as np
from piper import PiperVoice, SynthesisConfig

PUNCT = set(",.;:!?…–—\"'«»„“”()")


def tokens(sentence: str) -> list[str]:
    out = []
    for raw in sentence.split():
        word = raw.strip("".join(PUNCT))
        if re.search(r"[\wÄÖÜäöüß]", word):
            out.append(word)
    return out


def main() -> None:
    req = json.load(open(sys.argv[1], encoding="utf-8"))
    voice = PiperVoice.load(req["voice"], include_alignments=True)
    cfg = SynthesisConfig(
        length_scale=req.get("length_scale", 1.08),
        noise_scale=req.get("noise_scale", 0.6),
        noise_w_scale=req.get("noise_w_scale", 0.7),
        normalize_audio=False,
    )
    sr = voice.config.sample_rate
    id_map = voice.config.phoneme_id_map
    space_ids = set(id_map.get(" ", []))
    punct_ids = set()
    for p in PUNCT:
        punct_ids.update(id_map.get(p, []))

    sentences = req["sentences"]
    pieces = [np.zeros(int(sr * req.get("lead_in", 0.5)), dtype=np.float32)]
    t = len(pieces[0]) / sr
    words = []
    warnings = []

    for si, sentence in enumerate(sentences):
        toks = tokens(sentence)
        ph_sentences = voice.phonemize(sentence)
        audio_parts = []
        groups = []  # (start_s, end_s) pro Wort, relativ zum Satz
        offset = 0
        for phonemes in ph_sentences:
            ids = voice.phonemes_to_ids(phonemes)
            res = voice.phoneme_ids_to_audio(ids, cfg, include_alignments=True)
            if not isinstance(res, tuple) or res[1] is None:
                raise SystemExit("Piper-Modell liefert keine Alignments")
            audio, samples = res
            samples = np.asarray(samples).astype(int)
            # Wortgruppen: zwischen Leerzeichen-IDs; Wortende vor Satzzeichen
            cur_start, cur_end, in_word = None, None, False
            pos = offset
            for pid, n in zip(ids, samples):
                if pid in space_ids:
                    if in_word:
                        groups.append((cur_start, cur_end))
                    in_word = False
                elif pid in punct_ids:
                    pass
                elif pid in (0, 1, 2) and not in_word:
                    pass  # PAD/BOS/EOS ausserhalb eines Wortes
                else:
                    if not in_word:
                        cur_start, in_word = pos, True
                    if pid not in (0, 1, 2):
                        cur_end = pos + n
                pos += n
            if in_word:
                groups.append((cur_start, cur_end))
            audio_parts.append(audio.astype(np.float32))
            offset += len(audio)
        sent_audio = np.concatenate(audio_parts)
        dur = len(sent_audio) / sr

        if len(groups) != len(toks):
            warnings.append(f"Satz {si}: {len(toks)} Wörter, {len(groups)} Phonemgruppen -> proportional")
            # Fallback: Zeit proportional zur Wortlänge über den Sprechbereich verteilen
            total = sum(len(w) + 1 for w in toks)
            a, b = 0.03 * dur, 0.97 * dur
            acc = 0
            groups = []
            for w in toks:
                s = a + (b - a) * acc / total
                acc += len(w) + 1
                e = a + (b - a) * (acc - 1) / total
                groups.append((s * sr, e * sr))

        for wi, (w, (s, e)) in enumerate(zip(toks, groups)):
            words.append({
                "text": w,
                "start": round(t + s / sr, 3),
                "end": round(t + e / sr, 3),
                "satz": si,
            })
        pieces.append(sent_audio)
        t += dur

        if si < len(sentences) - 1:
            if si == len(sentences) - 2:
                p = req.get("pause_before_last", 0.8)
            elif len(toks) <= 3:
                p = req.get("pause_short", 0.6)
            else:
                p = req.get("pause", 0.32)
            pieces.append(np.zeros(int(sr * p), dtype=np.float32))
            t += p

    pieces.append(np.zeros(int(sr * 0.3), dtype=np.float32))
    audio = np.concatenate(pieces)
    peak = float(np.max(np.abs(audio))) or 1.0
    audio = audio / peak * 0.89
    with wave.open(req["out_wav"], "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((audio * 32767).astype(np.int16).tobytes())

    json.dump({"duration": round(len(audio) / sr, 3), "words": words, "warnings": warnings},
              open(req["out_words"], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for msg in warnings:
        print("WARN", msg, file=sys.stderr)


if __name__ == "__main__":
    main()
