#!/usr/bin/env python3
"""Aussprache-Prüfung VOR dem Rendern.

Listet jedes Wort mit der Aussprache, die die Stimme wirklich bekommt, und markiert,
was kontrolliert werden muss:
  EIGEN    = aus pipeline/aussprache.json (bereits korrigiert)            ok
  GEPRÜFT  = als korrekt bestätigt (Liste 'geprueft')                       ok
  GRUUT    = Wörterbuch und espeak-ng stimmen überein                      ok
  ESPEAK   = Wörterbuch weicht ab -> espeak-ng wird benutzt                 ok
  PRÜFEN   = Wort steht in keinem Wörterbuch (Namen, Fremdwörter, seltene Komposita) -> kontrollieren
Aufruf:  python3 aussprache_check.py <script.json> [--strict]   (Exit 2 bei offenen Wörtern)
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from g2p_de import PUNCT, in_gruut_lexicon, load_lexicon, word_phonemes  # noqa: E402


def main():
    script = json.load(open(sys.argv[1], encoding="utf-8"))
    strict = "--strict" in sys.argv
    own, ok = load_lexicon()
    seen, todo = set(), []
    for raw in script["erzaehltext"].split():
        w = raw.strip(PUNCT)
        if not re.search(r"\w", w) or w.lower() in seen:
            continue
        seen.add(w.lower())
        ph, src, g, e = word_phonemes(w, own)
        flag = src != "EIGEN" and not in_gruut_lexicon(w) and w.lower() not in ok
        if src != "EIGEN" and w.lower() in ok:
            src = "GEPRÜFT"
        extra = f"   (gruut: /{g}/)" if src == "ESPEAK" else ""
        print(f"{'PRÜFEN' if flag else '':7}{src:8} {w:24} /{ph}/{extra}")
        if flag:
            todo.append(w)
    print()
    if todo:
        print(f"{len(todo)} Wort/Wörter prüfen: {', '.join(todo)}")
        print("Richtig -> in pipeline/aussprache.json unter 'geprueft' eintragen.")
        print("Falsch  -> unter 'woerter' korrigieren (Notation: ei='aeː', au='aoː', eu='ɔɔʏ', -er='ɐ', ch='ç'/'x', sch='ʃ', z='ts').")
        if strict:
            sys.exit(2)
    else:
        print("Aussprache: alles geprüft.")


if __name__ == "__main__":
    main()
