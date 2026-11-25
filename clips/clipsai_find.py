"""ClipsAI: find self-contained clips in a long video by its spoken text (topic changes in the transcript).
Useful for story walkthroughs with in-game dialogue (cutscene moments for Shorts); useless for silent gameplay.
Run with the separate Python 3.11 venv (ClipsAI pins old Pillow/torch – kept away from the render/voice stack):
  /home/user/.venv-clipsai/bin/python clips/clipsai_find.py <video_or_audio> [--min 20] [--max 60] [--model small]
Prints: start–end (s) | length | first words – then cut with clipper.py (`cut <file> <start> <end> --gameplay --raw …`)."""
import argparse, os, subprocess, tempfile

ap = argparse.ArgumentParser()
ap.add_argument("video"); ap.add_argument("--min", type=float, default=20); ap.add_argument("--max", type=float, default=60)
ap.add_argument("--model", default="small")
x = ap.parse_args()

from clipsai import ClipFinder, Transcriber

wav = os.path.join(tempfile.mkdtemp(), "a.wav")          # audio only: faster, and avoids container quirks of .ts files
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", x.video, "-vn", "-ac", "1", "-ar", "16000", wav], check=True)
tr = Transcriber(model_size=x.model, device="cpu", precision="int8")
transcription = tr.transcribe(audio_file_path=wav, iso6391_lang_code="en")
clips = ClipFinder(min_clip_duration=int(x.min), max_clip_duration=int(x.max)).find_clips(transcription=transcription)
words = transcription.get_word_info() if hasattr(transcription, "get_word_info") else []
for c in clips:
    txt = " ".join(w["word"] for w in words if c.start_time <= w["start_time"] < c.end_time)[:90] if words else ""
    print(f"{c.start_time:7.1f}–{c.end_time:7.1f} | {c.end_time - c.start_time:5.1f} s | {txt}")
print(f"{len(clips)} clips")
