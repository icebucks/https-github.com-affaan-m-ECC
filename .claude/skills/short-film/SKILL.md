---
name: short-film
description: >-
  A staged method for making a short, high-quality film (15-90 s: product film, trailer,
  explainer, title sequence, social clip) with Claude: study a reference film you love, break it
  down shot by shot and sound by sound, design the hook, pick the spoken part from many options,
  generate the voice, design the music, and only then build the picture scene by scene (in
  fframes). Every taste decision is a side-by-side page with play buttons and the human picks.
  Use this skill whenever someone wants to make a video or film that should look and sound like
  a real motion designer made it, wants to recreate the feel of a reference video, asks to
  break down or analyze a video's cuts, music and sound, wants hook ideas or voice-over options
  for a video, wants to edit or remix music for a video, or says their generated video looks like
  "AI slop" and wants it better, even if they never say "film" or name a stage.
---

# Short film, the staged way

Generated videos usually fail for the same reasons: no reference, sound added last, one
version of everything, and the agent deciding taste. This method fixes that with seven stages
and a human gate after each one. Sound comes before picture, because a cut that lands on a
music hit and a word looks designed, and a cut that does not looks random.

## The seven stages

| # | Stage | Output | Gate (the human decides) | Read |
|---|---|---|---|---|
| 1 | Find a reference | one film the human loves, saved locally | "this is the one" | `references/01-reference.md` |
| 2 | Break it down | `BREAKDOWN.md`: every shot, cut, sound, word, colour, plus an ear checklist | ear checks done, breakdown approved | `references/01-reference.md` |
| 3 | Idea, then hook | one-sentence idea, hook options as mock frames, a timing sheet | hook picked | `references/03-hook.md` |
| 4 | Spoken-part options | a page with ~50 scripts in families, each with ▶ | one script picked | `references/04-voice-options.md` |
| 5 | Generate the voice | final takes from the best current speech model | take picked by ear | `references/05-voice.md` |
| 6 | Design the music | edited music with effects on the music itself, mixed with the voice | mix locked | `references/06-music.md` |
| 7 | Build the picture | scene by scene in fframes, ~5 options per scene, then masters | each scene picked; final film approved | `references/07-picture.md` |

Read only the reference file for the stage you are in. Stages 1 and 2 share one file.

Stages 4-6 can loop: the music often gets re-cut to fit the chosen words, and a line may move
to land on a music hit. Lock the sound (voice + music + mix) before stage 7. Changing the sound
after the picture exists means re-timing every cut.

## Rules that hold in every stage

**The human decides taste; you prepare options.** Never pick for them silently. Give 3-5
real options (built, rendered, playable), your recommendation with a one-line reason, and wait.
A choice described in words is not an option; a choice they can play is.

**Every choice is a page.** Put options side by side on one HTML page with play buttons: a
Claude artifact if the Artifact tool is available, otherwise a local HTML file opened in the
browser. After a pick, make the pick the default, delete the losing options from the page and
from the code, and keep the page short. A page full of old options hides the current state.

**You cannot hear, and you cannot watch a video.** Measure instead: onsets, levels, loudness,
frame differences, contact sheets, single frames. Audio-capable models can label sounds, but
their timestamps drift and they disagree; times come from signal processing, names come from
2-3 models voting, and the human's ear settles every disagreement. Say plainly which values are
measured and which are guesses.

**Keep every version.** Number versions (`v1`, `v2` ...), never overwrite a render the human
has seen, and keep the losing options on disk (not on the page) in case they change their mind.

**Keep a decision log.** One `DECISIONS.md` in the project: each pick, each rejected idea with
the human's reason, each rule they state ("no camera shake under narration"). Read it at the
start of every session. Rejections are the most valuable lines in it: the same mistake twice
costs more trust than any bug.

**One stage at a time.** Finish the gate before you start the next stage. If the human asks
for the next stage early, say what the open gate is, then do what they ask.

**Ask before anything leaves the machine**: publishing, uploading, emailing, posting, paid API
calls above a few dollars. Show the cost estimate first.

## Project layout

```
my-film/
  DECISIONS.md            # picks, rejections, rules (read first every session)
  reference/<name>/       # the reference file, frames/, sheets/, audio/, BREAKDOWN.md
  hook/                   # hook options, SCENARIO.md (timing sheet)
  voice/options/          # scripts.json, preview takes, the options page
  voice/final/            # chosen takes, word timings
  music/                  # source, SONG-MAP.md, edit scripts, versions, final mix
  film/                   # the fframes project (stage 7)
  out/                    # renders: film_v1.mp4, film_v2.mp4 ...
```

## Tools you will need

- `ffmpeg` / `ffprobe` for frames, loudness (`ebur128`), encoding.
- Python 3.10+ with `numpy scipy librosa soundfile pillow pedalboard` (one virtual environment
  for the project). Optional: `demucs` (stems), `faster-whisper` (local speech-to-text),
  `praat-parselmouth` (vowel checks). Run every helper script with that environment's
  `python`; a system Python usually lacks numpy.
- The `fframes-video` skill for stage 7 (install: `npx skills add https://fframes.studio`).
- Helper scripts in `scripts/` (run with `python scripts/<name>.py --help`):
  - `frames_and_cuts.py` — every frame, labelled contact sheets, a cut list from frame differences.
  - `audio_events.py` — tempo, beats, onsets, level envelope, 1 s listening windows per event.
  - `music_fx.py` — automation curves on the music itself: level, filter, reverb send,
    varispeed, fades, loudness and limiter.
  - `speech_margin.py` — how far the voice sits above the music in the speech band, over time.
