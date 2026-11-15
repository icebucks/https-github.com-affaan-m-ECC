# Stage 6: Design the music

The music is half the film. What makes a designer's soundtrack feel alive is not extra sound
effects laid on top; it is the song itself being played like an instrument: level rides,
reverb throws, filter sweeps, a push in speed into the drop, a near-silent break before the
climax, a wet dark tail. Stacking synthetic whooshes and risers on a plain song sounds cheap
("spaceship effects"). Work on the music; add very few effects.

## Source and rights

- Options: a licensed commercial song, production-library music, a commissioned piece, or
  music the makers wrote. A commercial song needs written sync (composition) AND master
  (recording) permission before the film is published anywhere, plus a plan for automated
  copyright matching on video platforms. Have a plan-B track if permission is slow.
- Prefer an instrumental or a clean source with no voice; a karaoke or live upload has
  tempo drift and unknown provenance.

## Map the song (SONG-MAP.md)

Measure with `scripts/audio_events.py song.wav out/` and listen-check with the human:

- Tempo (and drift), bar grid, frames per beat at the film's frame rate.
- Sections with source times: intro, the first big hit, riffs and their repeats, breaks,
  verse, climax, ending.
- Good start points (a hit after a short silence) and good end points (a phrase end).

## Cut an excerpt

- **Start on a strong moment.** A short riser or the song's own soft intro that releases on
  the first loud hit works; starting mid-phrase or on a drum fill does not.
- **Prefer continuous excerpts.** Every internal cut is a risk; when you must repeat a cycle,
  cut on the bar line at the same point in the pattern.
- **End with a smooth fade over the last ~2 bars** (or a reverb wash). Never paste an
  earlier section back at the end as a "bang" ending; it sounds pasted.
- Fit the voice: let a key line end before the drop, and leave ≥2 s of music with no voice
  after a big moment so the music can breathe. Move the music, not the voice, when a real
  recording is involved; lengthen the intro rather than leaving silence.

## Effects on the music itself

`scripts/music_fx.py` gives automation curves keyed in source time:

| Move | Typical use |
|---|---|
| Level ride | quiet charge that swells into the first hit; small dips just before cuts; lift in gaps between lines |
| High-pass sweep | thin, distant intro that opens to full on the first hit |
| Low-pass sweep | darken the ending; a short dip before a section change |
| Reverb send | very wet intro, a throw on the last beat before a drop, a wash at the end |
| Varispeed | a slight push in speed (and pitch) into the drop, a slow-down at the end |
| Near-silent break | ~1 beat to 1 s of almost nothing right before the climax |

Build 2 depths of the same edit (strong and subtle) so the human can say "more" or "less"
by ear. If a DAW is preferred, REAPER renders headless (`reaper -nosplash -renderproject x.rpp`).
fframes itself can only place, gain, pan, fade and duck tracks, so all processing happens
before the picture stage.

Sound effects: only at the few biggest picture changes, quiet, and never several per second.
Real recorded or well-made library effects (CC0 packs, licensed libraries) beat synthesized
ones. Check every effect's licence.

## Mix voice and music for phone speakers

A mix that sounds fine on studio speakers often loses the voice on a phone. Measure:

```bash
python scripts/speech_margin.py voice.wav music.wav      # speech-band margin over time
```

- Aim for the voice to sit about +12 dB above the music in the speech band (1-4 kHz) while
  someone speaks. Good references often reach this without obvious ducking.
- Use slow phrase-level rides (down ~0.8 s before a phrase, back up ~1.4 s after it; hold
  through short pauses), not fast ducking that pumps on every word. Bring the music back to
  full level in gaps and before drops.
- A gentle mid-band dip in the music under the voice helps; aggressive exciters and
  "clarity" processing add buzz and are often disliked.
- Archival recordings may sound best with the music clearly audible under them; the
  narrator usually needs more space.
- Listen-test in mono through a band-limited (≈450 Hz-7 kHz) copy as a phone simulation.
- Master: about -14 LUFS integrated, true peak at most -1 dBTP. Measure after EVERY change;
  a level bug (a stem at the wrong scale) can bury a voice silently. Some limiters add
  make-up gain; check the output, not the setting.

## The studio page

One player for all versions: the raw song, the reference's audio, and every edit or mix.
Use Web Audio so switching (keys 1-9) keeps the same playback position; add a waveform with
a playhead, a "phone" toggle (band-limited mono) and a "quiet" toggle (-20 dB). Only the
current candidates stay on the page.

**Gate:** the human locks the mix. Export the final stems (voice, music, effects) and the
mix, and save the hit and word times the picture will use.
