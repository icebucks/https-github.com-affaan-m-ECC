"""Hybride deutsche Aussprache (Text -> Phoneme) für die Coqui-Thorsten-Stimme.

Reihenfolge pro Wort:
  1. eigenes Lexikon  pipeline/aussprache.json  ("woerter")           -> Quelle EIGEN
  2. gruut-Wörterbuch, WENN es mit espeak-ng übereinstimmt             -> Quelle GRUUT
     (gruut ist die Notation, mit der das Modell trainiert wurde = klingt am natürlichsten)
  3. sonst espeak-ng (zuverlässiger, ins Modell-Alphabet übersetzt)     -> Quelle ESPEAK
Warum: Das gruut-Wörterbuch enthält kaputte Einträge (Speere=/ʃpəɐə/, Schnee=/ʃnəə/,
Feldherr=/fɛltɛʁʁ/, kilometerweit=/...vəiːt/). Genau das war die „unsaubere Aussprache“.
"""
import json
import os
import glob
import re
import sqlite3
import unicodedata
import warnings
from functools import lru_cache

warnings.filterwarnings("ignore")

HERE = os.path.dirname(os.path.abspath(__file__))
LEXICON = os.path.join(HERE, "aussprache.json")
PUNCT = ",.;:!?…–—\"'«»„“”()"
VOWELS = set("iyɨʉɯuɪʏʊeøɘəɵɤoɛœɜɞʌɔæɐaɶɑɒː")
MAX_DIST = 0.25


def load_lexicon(path=LEXICON):
    if not os.path.exists(path):
        return {}, set()
    data = json.load(open(path, encoding="utf-8"))
    own = {k.lower(): v.replace(" ", "") for k, v in data.get("woerter", {}).items()}
    ok = {w.lower() for w in data.get("geprueft", [])}
    return own, ok


@lru_cache(maxsize=1)
def _espeak():
    from piper.phonemize_espeak import ESPEAK_DATA_DIR, EspeakPhonemizer
    return EspeakPhonemizer(ESPEAK_DATA_DIR)


def map_espeak(p: str) -> str:
    p = re.sub(r"[ˈˌʲ]", "", p)
    p = p.replace("ɔø", "ɔɔʏ").replace("ɔʏ", "ɔɔʏ").replace("ɔɔɔʏ", "ɔɔʏ")
    p = p.replace("aɪ", "aeː").replace("aʊ", "aoː").replace("ɜ", "ɐ").replace("ɑ", "a").replace("r", "ʁ")
    out = []
    for i, ch in enumerate(p):
        if ch == "ɾ":
            nxt = p[i + 1] if i + 1 < len(p) else ""
            prev = p[i - 1] if i else ""
            out.append("ɐ" if (prev in VOWELS and (not nxt or nxt not in VOWELS)) else "ʁ")
        else:
            out.append(ch)
    return "".join(out)


@lru_cache(maxsize=4096)
def espeak_word(word: str) -> str:
    sents = _espeak().phonemize("de", word)
    return unicodedata.normalize("NFC", map_espeak("".join("".join(s) for s in sents).replace(" ", "")))


@lru_cache(maxsize=4096)
def gruut_word(word: str) -> str:
    import gruut
    ph = []
    for s in gruut.sentences(word, lang="de-de"):
        for w in s:
            if not w.is_break and w.phonemes:
                ph.extend(w.phonemes)
    p = unicodedata.normalize("NFC", "".join(ph))  # ç kommt sonst als c + Cedille -> Modell hört 'c'
    p = p.replace("̯", "").replace("͡", "").replace("g", "ɡ")
    return re.sub(r"[ˈˌ]", "", p)


def dist(a: str, b: str) -> float:
    """normalisierte Levenshtein-Distanz"""
    if a == b:
        return 0.0
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1] / max(len(a), len(b), 1)


def _norm(p: str) -> str:
    """Schreibvarianten angleichen, damit nur echte Unterschiede zählen."""
    p = p.replace("ʔ", "").replace("aeː", "A").replace("aɪ", "A").replace("aoː", "O").replace("aʊ", "O")
    p = p.replace("ɔɔʏ", "Y").replace("ɔʏ", "Y").replace("ʁ", "R").replace("ɐ", "R").replace("r", "R")
    return p.replace("ː", "")


@lru_cache(maxsize=1)
def _db():
    import gruut_lang_de
    path = glob.glob(os.path.dirname(gruut_lang_de.__file__) + "/**/lexicon.db", recursive=True)[0]
    return sqlite3.connect(path, check_same_thread=False)


def in_gruut_lexicon(word: str) -> bool:
    return _db().execute("select 1 from word_phonemes where word=? limit 1", (word.lower(),)).fetchone() is not None


def word_phonemes(word: str, own=None):
    """-> (phoneme, quelle, gruut, espeak)"""
    key = word.lower()
    own = own if own is not None else load_lexicon()[0]
    if key in own:
        return own[key], "EIGEN", None, None
    g = gruut_word(word)
    e = espeak_word(word)
    # gruut macht aus ß/ss oft /sz/ (dreißig -> dʁaeːszɪç): dann immer espeak
    if g and "sz" not in g and "ß" not in word and dist(_norm(g), _norm(e)) <= MAX_DIST:
        return g, "GRUUT", g, e
    return e, "ESPEAK", g, e


def sentence_phonemes(sentence: str, own=None) -> str:
    own = own if own is not None else load_lexicon()[0]
    parts = []
    for raw in sentence.split():
        m = re.match(r"^([" + re.escape(PUNCT) + r"]*)(.*?)([" + re.escape(PUNCT) + r"]*)$", raw)
        _, core, trail = m.groups()
        if not re.search(r"[\wÄÖÜäöüß]", core):
            # alleinstehender Gedankenstrich o. ä. -> kurze Pause
            if parts:
                parts[-1] += ","
            continue
        ph, *_ = word_phonemes(core, own)
        trail = trail.replace("–", ",").replace("—", ",").replace("…", ".").replace("„", "").replace("“", "").replace("”", "").replace('"', "")
        parts.append(ph + trail)
    return " ".join(parts)
