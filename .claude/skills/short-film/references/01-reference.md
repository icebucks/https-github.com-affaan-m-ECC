# Stages 1-2: Find a reference, then break it down

## Stage 1: find a reference

A reference is one finished film, made by a human motion designer or editor, that the human
loves and would be proud to have made. It sets the bar. Without one, every decision drifts
toward the generic look that generated video already has.

- Ask the human for it. If they have none, show them 5-10 candidates (designer portfolios,
  award sites, recent work by motion designers they follow) and let them pick.
- Length 15-60 s is ideal. Longer works, but break down only the part they love.
- Download the best available copy for local study (e.g. `yt-dlp -f bv*+ba`). It is for study
  only: never reuse its footage, sprites, music or traced shapes in your film.
- Ask the human what they love in it, in their words. Write that in `DECISIONS.md`; it tells
  you which layers of the breakdown matter most.

**Gate:** the human confirms the reference.

## Stage 2: break it down

Goal: write the reference down so precisely that someone could rebuild its timing without
seeing it. Picture, music, sound effects, voice and text, each with times. This is the most
useful document in the whole project: later, when an idea is rejected, new options that come
from the breakdown land far more often than invented ones.

### 2a. Measure the source

```bash
ffprobe -v error -show_entries stream=codec_type,width,height,r_frame_rate,nb_frames,duration -of compact ref.mp4
ffmpeg -i ref.mp4 -af ebur128=peak=true -f null - 2>&1 | tail -12      # integrated LUFS, LRA, true peak
```

Record the rational frame rate (24000/1001, not "24") and the exact frame count. Every time in
the breakdown is `frame × den / num`.

### 2b. Picture: frames, sheets, cuts

```bash
python scripts/frames_and_cuts.py ref.mp4 work/
```

It writes every frame, labelled contact sheets (frame number + time), `frame_diff.tsv` and
`cuts.tsv`. Then:

- Look at every sheet. Fast films hide single-frame flashes; a threshold misses soft cuts and
  dissolves, so check the frames around every candidate and around every big visual change.
- Count hard cuts. Note the rhythm (for example: slow, fast, slow, very fast, hold).
- Separate camera motion (push-in, drift, shake) from object motion (a sprite spins, text types).
- For type: case, weight, size relative to frame height, how words appear (typed, cut in,
  revealed), cursor, guide lines. For colour: extract a few full-size frames
  (`ffmpeg -ss <t> -i ref.mp4 -frames:v 1 f.png`) and take the median of a region, not
  single pixels; grain and compression shift single pixels a lot.
- Textures: paper grain, vignette, halftone, film grain, footage treatments (negative,
  thermal, duotone). Note which part of the frame they cover.

### 2c. Sound: stems, events, voice

```bash
ffmpeg -i ref.mp4 -vn -ac 2 -ar 48000 work/audio/mix.wav
python -m demucs -n htdemucs -o work/audio/stems work/audio/mix.wav        # vocals/drums/bass/other
python scripts/audio_events.py work/audio/mix.wav work/audio/ --cuts work/cuts.tsv --fps 24000/1001 --automation
# then once per stem (drums, bass, other, vocals) for that layer's events, e.g.
python scripts/audio_events.py work/audio/stems/htdemucs/mix/drums.wav work/audio/drums/ --cuts work/cuts.tsv --fps 24000/1001
```

- **Voice:** transcribe the vocals stem with a small local speech-to-text model with word
  timestamps (faster-whisper `small` or `medium`, or whisper.cpp). Some faster-whisper and
  PyAV version pairs fail on a file path (`TypeError ... metadata_errors`); load the audio
  yourself (`librosa.load(path, sr=16000)`) and pass the array instead. Note who speaks, the tone,
  and where the voice sits against the text: in good films the voice says the word and the
  text confirms it 0-0.3 s later.
- **Music:** tempo, sections (intro / main / break / climax / tail), where it starts and stops.
  Measure what the editor did TO the music: level over time, brightness (filter), wetness
  (reverb), speed and pitch drift. `audio_events.py --automation` plots this (also run it on
  the `no_vocals` stem, so the voice does not hide the moves). Real editors ride
  the song itself (quiet wet intro, push into the drop, dips before cuts, a near-silent break
  before the climax, a dark wet tail); that is what makes the sound feel designed.
- **Sound effects:** usually few, and only at the big changes. List each with start, peak,
  the cut it serves, and the stem it shows up in.
- **Sync:** count how many cuts land within 2 frames of a music or effect attack, and whether
  the picture changes before or after the sound.
- **Mix:** integrated loudness of the mix and of voice and music alone; does the music duck
  under the voice or not. Separated stems bleed into each other, so treat stem loudness as
  approximate and say so.

### 2d. Labels: models vote, the ear decides

`audio_events.py` cuts a 1 s window around each event (`windows/*.wav`). Send the windows to
2-3 audio-capable models from different vendors (web-search which ones currently accept
audio; check that the model really takes audio input before paying). Ask each for a label
only ("deep sub-bass impact", "whoosh", "piano chord", "breath"), never for times. Keep raw
replies. Two or three agree → accepted. All differ → goes on the ear checklist.

A prompt that works, sent with one window at a time:

> This is a 1-second audio clip. The event of interest starts at 0.25 s. Name what you hear
> at that moment in a few words (instrument, sound effect, voice, or silence), say whether it
> is part of the music or a separate effect, and describe its character (low/high, short/long,
> dry/wet). Do not give timestamps. Answer as JSON:
> {"label": "...", "layer": "music|effect|voice|silence", "character": "...", "confidence": "low|medium|high"}

Estimate the cost first (windows × models × price per call) and ask before running it. If no
audio model is available, skip this step and put every effect on the ear checklist.

### 2e. Write BREAKDOWN.md

Use this structure:

1. **Summary** — 5-8 bullets: voice yes/no, shot count and rhythm, sync rate, music shape,
   effects count, loudness.
2. **Source facts** — table: resolution, rational fps, frames, duration, audio format, loudness.
3. **Method** — how each value was found, which files hold the raw data.
4. **Picture, one row per shot** — `# | in-out (frames) | ground | subject and text | motion | into next`.
   Then a shot-length table with the feel of each group.
5. **Audio** — voice table (time, words, agreement, picture at that moment); music table
   (time, what, source of the value); effects table (start-end, sound, what it hits, agreement, stem).
6. **Cut map** — each cut with the nearest attack and the offset in frames.
7. **Type and colour** — fonts (or "unknown"), sizes, hex swatches, textures.
8. **Motion** — camera vs object, per shot group.
9. **For your ear** — numbered checklist: time, question, window file to play. Keep it to
   ~10 minutes of listening. Give them a timecode review copy so they can find each moment:
   `python scripts/frames_and_cuts.py ref.mp4 work/ --review` writes `work/review.mp4`.
10. **Keep, change, never** — draft rules for your film. Keep: what makes the reference good.
    Change: what must differ for your story and audience. Never: the reference's signature
    elements (its exact sentence shape, its cast, its ending) so you learn from it without
    cloning it.
11. **Open points.**

Also put the breakdown on a page (timeline strip of shots, voice, music and effects lanes,
with cut lines) so the human can read it at a glance.

**Gate:** the human does the ear checks and approves the breakdown. Record which model agreed
with their ear most often; use that model first next time.
