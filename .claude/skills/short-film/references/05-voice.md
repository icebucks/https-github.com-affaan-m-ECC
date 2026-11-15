# Stage 5: Generate the voice

## Choose the model now, not from memory

Speech models change every few months. At this stage, web-search for the current best
text-to-speech and voice-design models, and compare on what this script needs: naturalness,
the accent or persona, word-level timestamps, emotion tags, and licence for commercial use.
Prefer a local model when its quality is close; it costs nothing per take and keeps the
script private. Show the human 2-3 candidates with a short sample each before committing.

## Takes

- Generate several takes per script (different seeds or settings). The human picks by ear on
  the page: ▶ With music / ▶ Voice only for each take.
- **A whole read from one generation beats patched lines.** A take is one performance; a line
  regenerated later is a new performance with a slightly different timbre, pace and accent,
  and listeners hear the seam. To change a line, regenerate the whole script and pick again.
- **Persona and accents:** library voices often sound generic or lose the accent. Voice-design
  models (a new voice from a text description) usually do better; in some services the design
  preview itself is the best take, and a saved copy of that voice reads differently. Test both.
- **Spell sounds to steer pronunciation** ("tsiper" for a heavy accent's "cheaper", a stress
  mark on the right syllable). Then check the result, not the spelling.

## Check takes by measurement, then by ear

- **Words:** run local speech-to-text on every take; flag any word that does not match.
- **Vowels and stress:** a transcript cannot judge them. Measure vowel formants with
  `parselmouth` when a vowel matters (for example /iː/ has F1 ≈ 300-400 Hz and F2 ≈ 2300-2900 Hz
  for a female voice; a short /e/ has a higher F1).
- **Level:** loudness of every take; a quiet take hides inside the mix.

## Cutting and splicing

- Model timestamps drift 0.1-0.2 s. Never cut at the timestamp; cut at the quietest frame
  between the words near it, or the neighbour word bleeds in.
- If you must splice one word: take only that word (not the pause around it), match loudness
  (RMS), cut at quiet points, 10-20 ms crossfades. Then listen-check with speech-to-text and
  let the human hear it.
- **Real recordings stay whole.** Never cut, tighten or speed up an archival quote; its pauses
  are its character. Play it as one unbroken piece and move the music around it.

## Word timing file

When the take is picked, measure word start/end times from the final voice stem (speech-to-
text word timestamps, then snap to energy onsets) and save `voice/final/words.json`. Stage 6
places music hits around these words, and stage 7 keys every cut and text entrance to them.

**Gate:** the human picks the take(s).
