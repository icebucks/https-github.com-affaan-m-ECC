# Stage 7: Build the picture, scene by scene

Start only when the sound is locked. Then every cut, text entrance and camera move is keyed
to a measured time: a word from `words.json` or a hit from the song map.

**All code, commands, previews, checks and renders follow the `fframes-video` skill.** Load it
now and read its `references/design.md` (including "Matching an existing video") before the
first scene. This file adds only the process around it. Build every shot in fframes; use
Python or other tools only to prepare media (cut footage, trace images, make sprites). Two
render paths in one film drift apart in look and timing.

## Order of work

1. **Style bible** (`STYLE.md`): palette (hex), fonts with licences, textures, frame rate,
   aspect ratios, and the keep/change/never rules from the breakdown plus every rule in
   `DECISIONS.md`.
2. **Style frames:** 3-5 still frames of key moments, in every aspect ratio you will ship.
   Gate before any motion.
3. **Scene by scene, in film order.** For each scene:
   - Build ~4-5 real options behind command-line switches (`--peek-look a|b|c|d`), render a
     short clip of each (with sound, a little lead-in), and put them side by side on the page.
   - Recommend one, wait for the pick.
   - Make the pick the default, delete the losing options from the code and the page (keep
     clips on disk), record the decision, render the film so far, move on.
   - If all options are rejected, the next round should come from the reference breakdown
     (which shot, which move, which texture), not from newly invented ideas.
4. **Finish:** full render, delivery files, second aspect ratio, thumbnail.

## Picture rules that came from real rejections

- **Redraw, never paste.** Characters, logos and art are redrawn into the scene in the film's
  style; a pasted banner or screenshot looks pasted.
- **Mix real and illustrated.** Real footage or realistic UI next to a few illustrated or
  pixel elements looks crafted; everything stylized (pixel fonts on every UI) looks cheap.
  Reserve the stylized look for a small cast of signature elements.
- **Effects on part of the frame.** Footage treatments (negative, thermal, duotone) read best
  cut into the page, not filling the screen.
- **Invented UI uses the film palette.** No saturated gradients or glow blobs; they read as
  generated filler.
- **Keep character rules consistent** (the same shadow, scale and line weight in every scene).
- **No dead time.** A character standing still for half a second after a line reads as a
  mistake; end the shot or give it a move.
- **No camera shake under narration**; it fights the words.
- **Sync:** cut on the music attack or up to 2 frames before it; voice first, text 0-0.3 s
  after; an exit or transition counts as part of the next shot's timing.
- **Sound effects in the picture stage** follow stage 6 rules: few, quiet, never several per
  second; key them to the same constants as the animation.
- **Invented names** (fake products, accounts, brands) must not match real ones; search before
  using them. No real people's accounts or logos without permission.

## Showing clips on the page

Embedded video fullscreen can render tiny inside an artifact frame. Give each clip a
page-drawn overlay viewer (fixed, 16:9 fit, Esc closes, keeps time) plus an "open file" link.
Use small web copies on the page (CRF ~23) and keep masters on disk.

## Delivery

- Keep a lossless archive master (FFV1 in MKV). It is large; it is not for upload.
- H.264 for upload, per platform. For QuickTime/Apple compatibility avoid settings that push
  the H.264 level too high (for example `-tune animation` at 4K60); use
  `-profile:v high -level:v 5.2 -x264-params ref=4:bframes=3` (level 4.2 for 1080p), then
  verify hardware decoding: `ffmpeg -hwaccel videotoolbox -i out.mp4 -f null -` (no errors).
- Re-encoding AAC can raise the true peak; measure the final file, and remux the master's
  audio when possible. `-shortest` can drop the last frame; check frame counts.
- Heavy grain inflates file size and suffers at low bitrates; make a lower-grain variant for
  size-limited places and compare with SSIM.
- Second aspect ratio (for example 4:5 or 9:16): give each shot camera keys (centre, scale)
  rather than re-laying out every scene, then fix the few shots where text or details fall
  outside. Check platform UI safe zones.
- Thumbnail: a strong frame from the film itself, chosen by the human from 3-5 candidates.
- Credits: name every source of footage, music, voice and art on the end card or in the
  description.

**Gate:** the human approves the final film and every delivery file.
