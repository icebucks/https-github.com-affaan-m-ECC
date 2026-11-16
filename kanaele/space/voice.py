"""Narrator for By The Numbers: Kokoro-82M (Apache-2.0, local, free) voice bm_george, plus word timings.

Script markup: {display|spoken}  ->  captions show "display", George says "spoken".
    e.g. "You could pour {1.3 million|one point three million} Earths into the Sun."

    synth(text, out_wav, speed)  -> seconds          (cached by text + speed)
    words(text, wav)             -> [(display, t0, t1), ...]   word timings from faster-whisper, mapped onto the script
"""
import os, re, json, hashlib, difflib
import numpy as np
import soundfile as sf

MODEL = os.path.expanduser("~/.cache/kokoro/kokoro-v1.0.onnx")
VOICES = os.path.expanduser("~/.cache/kokoro/voices-v1.0.bin")
VOICE, LANG = "bm_george", "en-gb"
_k = [None]; _w = [None]
TOK = re.compile(r"\{([^|}]*)\|([^}]*)\}|(\S+)")


def spoken(text):
    return TOK.sub(lambda m: m.group(2) if m.group(1) is not None else m.group(3), text)


def tokens(text):
    """[(display_token, [spoken words])] – one display token can be several spoken words"""
    out = []
    for m in TOK.finditer(text):
        if m.group(1) is not None:
            disp, sp = m.group(1), m.group(2)
            # keep punctuation that directly follows the braces on the display token
            rest = text[m.end():m.end() + 1]
            if rest in ",.!?;:": disp += rest
            out.append((disp, sp.split()))
        else:
            w = m.group(3)
            if out and w in (",", ".", "!", "?"): continue
            if re.fullmatch(r"[,.!?;:]", w): continue
            out.append((w, [w]))
    # drop tokens that are only the punctuation already glued to a brace token
    return [(d, s) for d, s in out if not re.fullmatch(r"[,.!?;:]+", d)]


def norm(w): return re.sub(r"[^a-z0-9]", "", w.lower())


def synth(text, out, speed=1.0):
    key = hashlib.sha1(f"{VOICE}|{speed}|{spoken(text)}".encode()).hexdigest()[:12]
    meta = out + ".json"
    if os.path.exists(out) and os.path.exists(meta) and json.load(open(meta)).get("key") == key:
        return json.load(open(meta))["dur"]
    if _k[0] is None:
        from kokoro_onnx import Kokoro
        _k[0] = Kokoro(MODEL, VOICES)
    x, sr = _k[0].create(spoken(text), voice=VOICE, speed=speed, lang=LANG)
    x = np.asarray(x, np.float32)
    # trim silence at both ends, keep 40 ms
    nz = np.where(np.abs(x) > 0.01)[0]
    if len(nz): x = x[max(0, nz[0] - int(0.04 * sr)): nz[-1] + int(0.04 * sr)]
    sf.write(out, x, sr)
    dur = len(x) / sr
    json.dump(dict(key=key, dur=dur, sr=sr, text=text), open(meta, "w"))
    return dur


def words(text, wav):
    """display tokens with start/end seconds inside the wav (cached next to it)"""
    cache = wav + ".words.json"
    key = hashlib.sha1((text + str(os.path.getmtime(wav))).encode()).hexdigest()[:12]
    if os.path.exists(cache):
        d = json.load(open(cache))
        if d.get("key") == key: return [tuple(x) for x in d["words"]]
    if _w[0] is None:
        from faster_whisper import WhisperModel
        _w[0] = WhisperModel("medium", device="cpu", compute_type="int8")
    import subprocess
    pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", wav, "-f", "s16le", "-ac", "1", "-ar", "16000", "-"], capture_output=True, check=True).stdout
    audio = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768
    segs, _ = _w[0].transcribe(audio, language="en", word_timestamps=True, beam_size=1, initial_prompt=spoken(text))
    heard = [(w.word, w.start, w.end) for s in segs for w in s.words]
    toks = tokens(text)
    flat = [(i, sw) for i, (_, sws) in enumerate(toks) for sw in sws]          # spoken words with their token index
    a = [norm(sw) for _, sw in flat]; b = [norm(h[0]) for h in heard]
    times = [None] * len(flat)
    for blk in difflib.SequenceMatcher(None, a, b, autojunk=False).get_matching_blocks():
        for k in range(blk.size):
            times[blk.a + k] = heard[blk.b + k][1:]
    dur = sf.info(wav).duration
    # fill gaps: share the time between the known neighbours by character count
    i = 0
    while i < len(flat):
        if times[i] is not None: i += 1; continue
        j = i
        while j < len(flat) and times[j] is None: j += 1
        t0 = times[i - 1][1] if i > 0 else 0.0
        t1 = times[j][0] if j < len(flat) else dur
        L = [max(1, len(a[k])) for k in range(i, j)]; tot = sum(L); acc = t0
        for k, l in zip(range(i, j), L):
            d = (t1 - t0) * l / tot; times[k] = (acc, acc + d); acc += d
        i = j
    out = []
    for ti, (disp, sws) in enumerate(toks):
        ks = [k for k, (i2, _) in enumerate(flat) if i2 == ti]
        out.append((disp, times[ks[0]][0], times[ks[-1]][1]))
    json.dump(dict(key=key, words=out), open(cache, "w"))
    return out


if __name__ == "__main__":
    import sys
    txt = sys.argv[1]; o = sys.argv[2]; sp = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
    print(synth(txt, o, sp)); print(words(txt, o))
