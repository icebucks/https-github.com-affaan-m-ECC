"""Pick streamers that suit gameplay-only clips: English, live in the category, talk little.
  python3 clips/pick_streamer.py [--game "Grand Theft Auto VI"] [--n 8] [--sample 45] [--out DIR]
Samples the top N English streams for --sample seconds each, measures how much of the time someone is speaking
(Whisper VAD on the original audio) and saves a frame per stream (<out>/<login>.png) to check for facecams.
Prints the ranking: least talking first. Facecams in a corner are fine (the 9:16 window takes the centre)."""
import argparse, os, subprocess, sys, tempfile
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import twitch_find, clipper


def speech_share(wav_path):
    from faster_whisper import WhisperModel
    m = WhisperModel("base.en", device="cpu", compute_type="int8")
    a = clipper.audio(wav_path)
    segs, _ = m.transcribe(a, language="en", vad_filter=True)
    talk = sum(s.end - s.start for s in segs)
    return talk / max(1.0, len(a) / 16000)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--game", default="Grand Theft Auto VI")
    ap.add_argument("--n", type=int, default=8)
    ap.add_argument("--sample", type=int, default=45)
    ap.add_argument("--out", default=tempfile.mkdtemp())
    A = ap.parse_args()
    os.makedirs(A.out, exist_ok=True)
    g = twitch_find.live(A.game, 100)
    cands = [e["node"] for e in g["streams"]["edges"]
             if ((e["node"]["broadcaster"].get("broadcastSettings") or {}).get("language", "").lower() == "en")][:A.n]
    rows = []
    for s in cands:
        login = s["broadcaster"]["login"]
        ts = os.path.join(A.out, f"{login}.ts")
        r = subprocess.run(["streamlink", "--stream-segmented-duration", f"00:00:{A.sample:02d}", "-f", "-o", ts,
                            f"twitch.tv/{login}", "720p60,720p,best"], capture_output=True, text=True)
        if not os.path.exists(ts) or os.path.getsize(ts) < 100000:
            import re
            hosts = sorted(set(re.findall(r"https://([a-z0-9]+\.j\.cloudfront\.hls\.ttvnw\.net)", r.stdout + r.stderr)))
            print(f"{login:<20} could not record – blocked video server(s): {hosts or 'unknown'}", file=sys.stderr); continue
        subprocess.run(["ffmpeg", "-v", "quiet", "-y", "-ss", "5", "-i", ts, "-frames:v", "1", "-vf", "scale=640:-1",
                        os.path.join(A.out, f"{login}.png")])
        sh = speech_share(ts)
        rows.append((sh, login, s["viewersCount"]))
        os.remove(ts)
    print(f"frames for the facecam check: {A.out}")
    for sh, login, v in sorted(rows):
        print(f"{login:<20} talks {sh:4.0%} of the time   {v:>8,} viewers")
