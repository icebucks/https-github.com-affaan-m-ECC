#!/usr/bin/env python3
"""Deutsche Erzählstimme mit Coqui VITS „Thorsten“ (22 kHz, lokal, kostenlos)
+ eigenes Aussprache-Lexikon + exakte Wort-Zeitstempel aus den Phonem-Dauern.

Aufruf:  python3 tts_coqui.py <request.json>
request = { "sentences": [...], "model_dir": ".../tts_models--de--thorsten--vits",
            "lexicon": "pipeline/aussprache.json", "out_wav": ..., "out_words": ...,
            "length_scale": 1.05, "pitch": 0.91, "lead_in": 0.5, "pause": 0.34,
            "pause_short": 0.6, "pause_before_last": 0.8 }
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import wave
import warnings

warnings.filterwarnings("ignore")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")

import numpy as np  # noqa: E402
import torch  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from g2p_de import load_lexicon as _load_lex, sentence_phonemes  # noqa: E402

PUNCT = ",.;:!?…–—\"'«»„“”()"


def tokens(sentence):
    out = []
    for raw in sentence.split():
        w = raw.strip(PUNCT)
        if re.search(r"[\wÄÖÜäöüß]", w):
            out.append(w)
    return out


def load_lexicon(path):
    if not path or not os.path.exists(path):
        return {}
    data = json.load(open(path, encoding="utf-8"))
    return {k.lower(): v.replace(" ", "") for k, v in data.get("woerter", {}).items()}


class Voice:
    def __init__(self, model_dir, lexicon):
        from TTS.tts.configs.vits_config import VitsConfig
        from TTS.tts.models.vits import Vits
        cfg = VitsConfig()
        cfg.load_json(os.path.join(model_dir, "config.json"))
        self.model = Vits.init_from_config(cfg)
        self.model.load_checkpoint(cfg, os.path.join(model_dir, "model_file.pth"), eval=True)
        self.tok = self.model.tokenizer
        self.sr = cfg.audio.sample_rate
        self.lex = lexicon
        self.space_id = self.tok.characters.char_to_id(" ")
        self.blank_id = self.tok.characters.char_to_id(self.tok.characters.blank) if self.tok.add_blank else None
        punct_ids = set()
        for p in PUNCT:
            try:
                punct_ids.add(self.tok.characters.char_to_id(p))
            except KeyError:
                pass
        self.punct_ids = punct_ids

    def native(self, text):
        t = self.tok.text_cleaner(text, lang="de") if self.tok.text_cleaner else text
        return self.tok.phonemizer.phonemize(t, separator="", language="de-de")

    def phonemes(self, sentence):
        """Satz -> Phonem-String (hybride Aussprache, siehe g2p_de.py)."""
        return sentence_phonemes(sentence, self.lex)

    def synth(self, sentence, length_scale):
        phon = self.phonemes(sentence)
        ids = self.tok.encode(phon)
        if self.tok.add_blank:
            ids = self.tok.intersperse_blank_char(ids)
        if self.tok.use_eos_bos:
            ids = self.tok.pad_with_bos_eos(ids)
        self.model.length_scale = length_scale
        x = torch.LongTensor(ids).unsqueeze(0)
        with torch.no_grad():
            out = self.model.inference(x)
        audio = out["model_outputs"][0, 0].numpy()
        dur = out["durations"][0, 0].numpy()  # Frames pro Token
        hop = len(audio) / max(1.0, float(dur.sum()))
        # Wortgrenzen über die Leerzeichen-Token
        groups, in_word, s, e, pos = [], False, 0, 0, 0.0
        for tid, d in zip(ids, dur):
            n = float(d) * hop
            if tid == self.space_id:
                if in_word:
                    groups.append((s, e))
                in_word = False
            elif tid in self.punct_ids or tid == self.blank_id:
                pass
            else:
                if not in_word:
                    s, in_word = pos, True
                e = pos + n
            pos += n
        if in_word:
            groups.append((s, e))
        return audio, groups, phon


def main():
    req = json.load(open(sys.argv[1], encoding="utf-8"))
    v = Voice(req["model_dir"], _load_lex()[0])
    sr = v.sr
    pieces = [np.zeros(int(sr * req.get("lead_in", 0.5)), dtype=np.float32)]
    t = len(pieces[0]) / sr
    words, warnings_, phon_log = [], [], []
    sentences = req["sentences"]
    for si, sentence in enumerate(sentences):
        toks = tokens(sentence)
        audio, groups, phon = v.synth(sentence, req.get("length_scale", 1.05))
        phon_log.append(phon)
        dur = len(audio) / sr
        if len(groups) != len(toks):
            warnings_.append(f"Satz {si}: {len(toks)} Wörter / {len(groups)} Gruppen -> proportional")
            total = sum(len(w) + 1 for w in toks)
            acc, groups = 0, []
            for w in toks:
                a = 0.03 * len(audio) + 0.94 * len(audio) * acc / total
                acc += len(w) + 1
                groups.append((a, 0.03 * len(audio) + 0.94 * len(audio) * (acc - 1) / total))
        for w, (s, e) in zip(toks, groups):
            words.append({"text": w, "start": round(t + s / sr, 3), "end": round(t + e / sr, 3), "satz": si})
        pieces.append(audio.astype(np.float32))
        t += dur
        if si < len(sentences) - 1:
            if si == len(sentences) - 2:
                p = req.get("pause_before_last", 0.8)
            elif len(toks) <= 3:
                p = req.get("pause_short", 0.6)
            else:
                p = req.get("pause", 0.34)
            pieces.append(np.zeros(int(sr * p), dtype=np.float32))
            t += p
    pieces.append(np.zeros(int(sr * 0.3), dtype=np.float32))
    audio = np.concatenate(pieces)
    audio = audio / (np.max(np.abs(audio)) or 1) * 0.89

    with tempfile.TemporaryDirectory() as td:
        raw = os.path.join(td, "raw.wav")
        with wave.open(raw, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(sr)
            w.writeframes((audio * 32767).astype(np.int16).tobytes())
        # tiefere Stimmlage bei gleichem Tempo (Wortzeiten bleiben exakt)
        pitch = req.get("pitch", 0.91)
        af = f"rubberband=pitch={pitch}:formant=preserved" if pitch != 1 else "anull"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-af", af, "-ar", "44100", req["out_wav"]], check=True)

    json.dump({"duration": round(len(audio) / sr, 3), "words": words, "warnings": warnings_, "phoneme": phon_log},
              open(req["out_words"], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for m in warnings_:
        print("WARN", m, file=sys.stderr)


if __name__ == "__main__":
    main()
