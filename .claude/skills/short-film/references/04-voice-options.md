# Stage 4: Many spoken-part options, each playable

The spoken part carries the film. The first idea is rarely the best one, and the human cannot
judge a script by reading it; they judge it by hearing it over the music. So: many options,
whole ideas (not variations of one line), each with a play button.

## Write ~50 full scripts in families

Each script is the whole spoken part for the film, timed to the timing sheet (and to the
music grid, if a music sketch exists). Quality bar: each script is a different whole idea
that could carry the film alone; 30 strong ideas beat 50 rewordings. Aim for ~50 because
the first 20 are usually the obvious ones. Spread them over 8-10 families so whole concepts differ:

| Family | What it is |
|---|---|
| Straight | Plain, confident lines that say what the thing is and why it matters. Always include a few; they are the baseline. |
| The problem | The viewer's pain in their own words, then the turn. |
| Real recordings | A real archival voice (a speech, a mission recording, an interview) that fits the idea, followed by your narrator. |
| Historical metaphor | A short true story from history that mirrors the idea. |
| Famous words | A real quote whose meaning matches the idea. |
| Parody | The shape of a known genre or format (nature documentary, movie trailer, breakup letter, safety briefing). |
| Character voice | A narrator with a strong persona or accent. |
| Local or cultural | A line from the makers' own language or culture, with a translation in text. |
| Genre | Noir, sports commentary, ASMR, poetry. |
| Wild cards | Anything that does not fit above. |

For each script store: id, family, title, lines with start times, voice brief (age, accent,
energy), sources for any quote or recording, and a rights note. Keep the data in one
`scripts.json` and generate the page from it, so changes stay cheap.

## Check facts and rights before the human falls in love

- **Quotes:** verify the exact wording against a primary source (the original book, letter,
  newspaper, transcript). Many famous quotes are misattributed; check a quote-investigation
  source. Translations are often still under copyright even when the original is not; use an
  old public-domain translation or your own.
- **Public domain differs by country.** A work can be free in one country and protected in
  another for decades more. Note the countries where the film will be shown.
- **Recordings:** government recordings are often public domain in their own country, but the
  speaker may still have publicity rights; check whether the use implies endorsement.
  Find the original archive copy, not a re-upload.
- **Famous speeches in commercial films** have drawn public backlash before. Say so when you
  offer one.
- **Real names, brands and logos:** avoid them, or get permission.

Put a short rights line on each card (green / check / risky, with the reason).

## Preview audio

Every card needs sound. Generate cheap previews first:

- A local speech model or an inexpensive API tier is fine for previews; spend the best model
  on the chosen script only (stage 5).
- For real recordings, find the archive copy now (national archives, agency media libraries,
  the Internet Archive), note its source and timecode, and cut the real audio for the
  preview; never a speech-model imitation. If no source copy is found, mark the card
  "recording not found" instead of faking it.
- Mix each preview with a music sketch (gentle ducking) so the human hears it in context.
  Music is designed in stage 6, but a rough excerpt of the likely track (or any neutral bed
  at a similar tempo) is enough here; say which one you used. Offer "voice only" too.
- Estimate characters × price before generating; ask if it exceeds the budget.

## The page

- Cards grouped by family, with a family filter at the top.
- Each card: title, family, full script with times, voice brief, rights line, and two buttons:
  ▶ With music and ▶ Voice only.
- While playing, highlight the line being spoken; one player at a time; optional autoplay-next
  so the human can lie back and listen to a whole family.
- Mark 3-5 as your picks with one-line reasons.

**Gate:** the human picks one script (they will often merge two: a recording from one card,
the narrator lines from another). Remove all other cards from the page; keep the files on disk.
Write the pick and the reasons in `DECISIONS.md`.
