# BeyondExcuses – Mindset Series

Format: 1080×1920, 30 fps, 15–18 s, −14 LUFS, own sounds only (`sound.py`). Mark as AI-generated on TikTok.
Render: `VID_LANG=en python3 epN.py render` → `FolgeN_<Name>_EN.mp4`. Stills: `python3 epN.py still`.

## Episodes

| # | Theme (grey vs. amber) | Location / light | Hook | Closing line (amber) | File |
|---|---|---|---|---|---|
| 1 | Planner vs. Doer | night → sunrise | – | – | `ep1.py` |
| 2 | Overthinker vs. Doer | river with stepping stones, sunset → night | Denkst du auch zu viel nach? | Nur den nächsten Schritt. | `ep2.py` |
| 3 | Ego vs. Humility | desert pit, stranger throws a rope | Würdest du das Seil nehmen? | Stolz hält dich unten. | `ep3.py` |
| 4 | Excuses vs. Discipline | rain on a running track → sun + rainbow | Welche Ausrede nutzt du? | Fang trotzdem an. | `ep4.py` |
| 5 | Envy vs. Contentment | two gardens and a fence, morning → golden evening | Schaust du auch ständig rüber? | Kümmer dich um deins. | `ep5.py` |
| 6 | Comfort zone vs. Growth | warm bubble in a snowstorm | Wie gemütlich ist deine Blase? | Geh raus. | `ep6.py` |
| 7 | People Pleaser vs. Boundaries | autumn forest hike, tracking camera | Sagst du auch zu allem Ja? | Nein ist ein ganzer Satz. | `ep7.py` |
| 8 | Impatience vs. Patience | spring meadow, time-lapse of days and nights | Do you want results NOW? | Plant. Wait. Trust. | `ep8.py` → `Folge8_Patience_EN.mp4` |
| 9 | Scroller vs. Learner | city rooftop, night → sunrise | Did you scroll all night? | One of them built stairs. | `ep9.py` → `Folge9_Scroller_EN.mp4` |
| 10 | Grudge vs. Letting Go | stormy lake → golden dusk | What are you still holding onto? | Let it go. Swim. | `ep10.py` → `Folge10_LettingGo_EN.mp4` |
| 11 | Victim vs. Owner | leaking attic in a rainstorm, flickering bare bulb → sun shaft through the window | If you blame the rain, you never fix the roof. Watch what 2 people do before it floods. (hookscore 72) | Own it. | `ep11.py` → `Folge11_Owner_EN.mp4` |

## Ideas (not made yet)

- **Victim vs. Owner (Part 2) – after the storm**: SEQUEL to #11 (1,424 views in the first hour). Same attic (exception to the new-location rule), new light: grey dawn after the storm, water on the floor. The victim finally *turns around* – clearly facing the ladder (answers the comment „which way is the victim facing?“) – takes the hammer the owner left and fixes the second hole himself. Hook again as a statement, not a question. Ending: „Blame is comfortable. / Fixing is freedom. / Own it.“
- **Perfectionist vs. Finisher**: a workshop. One sands the same chair forever; the other builds ten imperfect chairs.
- **Talker vs. Walker**: a mountain path. One tells everyone about the summit; the other is quietly already up there.
- **Fear of Failure vs. Courage**: a high diving board at a pool. One climbs down again; the other jumps and comes up laughing.
- **Comparer vs. Own Path**: a race on separate lanes. One keeps looking sideways and trips; the other only looks ahead.
- **Excuse Clock vs. Early Riser**: a bedroom at dawn. One hits snooze; the other is already on the sunrise run.
- **Lone Wolf vs. Team**: a heavy boulder on a hill. One pushes alone and fails; the other calls friends.
- **Consumer vs. Creator**: a market. One buys everything; the other builds a stall and sells.

## Graphics upgrades (from #8)

Soft ground shadows, rim light on the figures in the scene's light colour, atmospheric haze at the horizon, light film grain, dark plates behind labels, bubbles that pop in, and figures at 1.3–1.45× scale. The style is unchanged.

## Figures v2 + smoother motion (lib.py)

- Figure: tapered limbs, chest/waist/hip torso, neck, round hands, small feet, soft shading away from the light, egg-shaped faceless head with a highlight. The returned joints are the same as before, so old episodes still render.
- `smooth(fn, t)`: temporal blend of character functions, so hard pose switches become ~0.2 s transitions. Use `x = smooth(char, t)` instead of `x = char(t)`.
- Natural walk cycle (hip sway, knee lift), idle breathing (`lib.NOW`), and motion blur in `render()` (`MBLUR=3`, 180° shutter; `MBLUR=1` for fast drafts).
- **Facing cue (from #12):** a small nose and one eye on the side the figure faces (`facing=1` right, `-1` left), so viewers always see where someone looks – even with crossed arms (comment on #11: „which way is the victim facing?“). Default on; `FACE_CUE=0` restores the old faceless look. Already uploaded episodes are not re-rendered. Use it in scenes: the negative figure faces away from the solution, turning toward it is a visible turning point.
- **Arms v3 (from #12):** arms hang from a real shoulder joint (`ARM_ROOT` = 90 % of the torso), not from the neck. Walk: fuller counter-swing (32°), arms trail the legs slightly (follow-through), elbow bends more on the forward swing. `arms_crossed()` / `think()`: forearms fold *into* the chest – no hand poking out of the back. `cheer()`: arms in a V that frames the head. Rules for custom poses in episodes: keep a small elbow bend (≥ 8°) unless the arm is reaching or pulling; raised arms at most ~150° forward / −150° back so the head stays visible; folded forearms must end inside the torso silhouette; check every new pose on a pose sheet before rendering.
- **Joints bend only the right way (from #12):** `elb_x` and `knee_x` are FLEXION angles – positive only (elbow 0…155, knee 0…160). Forearm angle = `arm_x + elb_x`, shin angle = `leg_x - knee_x`; 0° = hanging down, +90° = forward (where the figure looks), 180° = up. A negative elbow bent the arm backwards like a broken joint (old poses: carry, hammer, sit-and-type …); `lib.JOINT_LIMITS` now clamps it, so write every new pose with positive elbows: carrying a box = `arm 25, elb 70`; arm reaching forward with the hand up = `arm 70, elb 40`; hammer wind-up overhead = `arm 150, elb 60` → strike = `arm 100, elb 10`; sprint = `elb 88`. For forearms pointing at the camera (crossed arms, hands on hips, phone in hand) use `fore_x` 0.4–0.6 instead of bending backwards.
- **Hands and feet grab things (IK, from #12):** `figure(..., reach={'f': (x, y), 'b': (x, y)})` puts the hands exactly on world points (ladder rungs, bucket handle, a hammer being handed over, a plank held against the roof) and bends the elbows the right way automatically. Feet: `figure(..., mode='hip', plant={'f': (x, y), 'b': (x, y)})` (hip position given, feet on rungs/steps). Template: `ep11.py` → `climbing()` (rung by rung: each hand/foot holds 70 % of the cycle, then moves one rung), hammering = hand moves along a wind-up→strike path, hand-over = both figures reach the same point. Never let hands float next to an object they hold.
- **Turning around:** `smooth()` now blends `f` continuously (−1 … 1 through 0), so a figure turns (squeezes through a front view) instead of flipping – the flip used to leave a ghost double image with motion blur (#11, 2.9 s). Keep `f` changes at least 0.25 s apart.
- **Head:** tilt is limited to ±30° (`HEAD_TILT`) – no broken-neck look when a figure looks up at the roof.
- **Ready-made gestures:** `hands_on_hips()`, `shrug(k)` (palms up, for complaining), `offer()` (hand held out), `arms_crossed()` (forearms drawn across the chest), `cheer()`, `think()`. Use these instead of inventing arm angles.
- **Check before rendering:** render stills at every gesture change and look at the arms, hands and feet up close (crop the figures) – #11 v1 had floating hands on the ladder, backwards elbows while complaining and hammering, a ghost on the turn and two hands missing each other at the hand-over.

## Reichweite & Qualität (Audit, Stand 16.11.2026)
Jedes Video wird nach dem Rendern mit `python3 ../kanaele/data/audit.py FolgeN_..._EN.mp4` gemessen (Ergebnis in `audit/`). Regeln daraus:
- **Abschlusstext über der TikTok-Caption:** `end_text` setzt die letzte Zeile automatisch auf höchstens y 1442 (`END_Y_MAX`). Ab y 1450 liegen bei TikTok Caption, Benutzername und Sound.
- **Rechte Button-Spalte frei:** Figuren, Schilder, Sprechblasen und Anzeigen enden auf dem Bildschirm bei x 880 (y 760–1660). In der Szene mit Faktor 1,45 heißt das: Welt-x höchstens etwa 680–700 für Figuren mit Schild.
- **Erste Sekunde hörbar und in Bewegung:** `finish_v2` macht das automatisch (Bass-Schlag + Whoosh aus dem CC0-Kit, kein langsames Einblenden, Kamera-Punch-in in den ersten 0,7 s, danach leichter Zoom bis zum Ende, damit es keine toten Sekunden gibt).
- **Leichte Farbkorrektur** (+12 % Sättigung, etwas heller) automatisch in `finish_v2`. Nacht- und Sturmszenen trotzdem nicht fast schwarz anlegen.
- Schrift: Bei Schildern in der skalierten Szene zählt die Bildschirmgröße (24 px × 1,45 ≈ 35 px). Text außerhalb der Szene mindestens 28 px.

## Hashtags (TikTok)
Format: `#thema #mindset #psychology #motivation #beyondexcuses`. Das Marken-Tag `#beyondexcuses` ersetzt `#fyp`, weil #fyp laut den meisten 2026-Analysen kaum etwas bringt und ein eigenes Tag die Serie sammelt. Genau 5 Hashtags, nie „#“ vor Zahlen.
YouTube: dieselben Themen-Tags am Ende der Beschreibung, `#beyondexcuses` zuerst, `#shorts` am Ende.

## YouTube-Skill-Workflow (Pflicht, `.claude/skills/yt-*`, MIT, Jake Schincariol)
0. Vorher `mkdir -p ~/.claude/youtube && cp kanaele/youtube/voice_beyondexcuses.md ~/.claude/youtube/voice.md` – alle yt-Skills lesen dieses Stimm-Profil.
1. **Hook (`/yt-script`):** 5 Hook-Varianten aus mindestens 3 verschiedenen Formeln in `.claude/skills/yt-script/hooks.json` schreiben (nicht immer „The Question“!), alle mit `python3 .claude/skills/yt-script/hookscore.py hooks.txt` bewerten. Die beste EHRLICHE nehmen: Ziel ≥ 55 (WORKABLE), besser ≥ 72 (STRONG). Hebel laut Werkzeug: „you“ in den ersten 6 Wörtern, eine konkrete Zahl, was auf dem Spiel steht (lose, cost, never, before …), ein offenes Fragewort, 9–24 Wörter, nicht selbst beantworten. Nie Zahlen oder Behauptungen erfinden. Auf dem Bildschirm in 2 kurze Zeilen teilen.
2. **Titel + Titelbild (`/yt-package`):** 10 YouTube-Titel schreiben, alle mit `python3 .claude/skills/yt-package/title.py titles.txt` prüfen, den besten nehmen (Ziel ≥ 90). Muster: „<Negativ> vs <Positiv> (Part N): <Hook-Frage>“ – das Thema vorne überlebt den 40-Zeichen-Schnitt im mobilen Feed, die Teil-Nummer ist die ehrliche Zahl; kein #mindset im Titel (gehört in die Beschreibung). Titelbild: höchstens 3 Wörter, andere Wörter als der Titel (gleiches Versprechen), am besten eine Zahl. Paar mit `title.py --title "…" --thumb "…"` prüfen; die Titelbild-Wörter kommen ins Cover.
3. **Suche (`/yt-seo`):** die 3 Suchanfragen aufschreiben, die das Video gewinnen soll. Titel und die ERSTEN ZWEI Zeilen der Beschreibung müssen deren Wörter enthalten. Tags sind unwichtig.
4. **Kommentare (`/yt-comment`):** Wenn die Person Kommentare schickt: in Fragen / Korrekturen / Lob / Köder sortieren, Antworten unter 30 Wörtern, EINEN Kommentar zum Anpinnen empfehlen (die Frage, die die meisten haben). Fragen = Themen für nächste Folgen.
5. **Retention (`/yt-retention`):** Exportierte Retention-CSV aus YouTube Studio (Video → Analytics → Engagement → Download) in `beyondexcuses/analytics/` legen und mit `python3 .claude/skills/yt-retention/retention.py <csv> --duration <s>` auswerten. Größtes Leck zuerst.
6. **Konkurrenz (`/yt-viral`):** `python3 kanaele/youtube/viral_collect.py out.json "<suchbegriff>" …` und `python3 .claude/skills/yt-viral/swipe.py out.json --min 2.0`. Gewertet wird das Vielfache des eigenen Kanal-Medians, nicht die Rohaufrufe. Nur öffentliche Listen.
