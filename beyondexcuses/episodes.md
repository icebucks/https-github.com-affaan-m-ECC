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

## Ideas (not made yet)

- **Victim vs. Owner**: a flooded room. One complains about the rain; the other picks up a bucket and fixes the roof.
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

