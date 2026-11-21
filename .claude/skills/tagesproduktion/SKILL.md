---
name: tagesproduktion
description: Tägliche Produktion und Veröffentlichung für Virlix (YouTube, GTA-6-Gameplay ohne Kommentar) und BeyondExcuses (TikTok, Mindset-Serie) – jeden Tag 1 Compilation + 1–2 Shorts auf YouTube und 3 neue TikTok-Folgen als Entwurf, mit Qualitätsprüfung, Protokoll und laufender Verbesserung von Reichweite, Viralität und Videoqualität. Verwenden bei „Tagesproduktion“, „mach die Videos für heute/morgen“, „Compilation“, „Shorts“, „neue Folgen“, „wie läuft der Kanal“, „was können wir verbessern“ und bei jedem geplanten Tageslauf.
---

# Tagesproduktion Virlix + BeyondExcuses

**Auftrag der Person (21.11.2026):** Jeden Tag **1 neue Compilation + 1–2 Shorts** auf YouTube (Virlix) und
**3 neue TikTok-Videos** (BeyondExcuses). Laufen lassen, Resonanz beobachten, und nebenbei laufend verbessern:
Reichweite, Viralität, Videoqualität. Antworten und Protokolle auf Deutsch.

## 0. Regeln, die nie gebrochen werden
- **Geheimnisse:** Werte von `YOUTUBE_*` / `TIKTOK_*` nie ausgeben – auch nicht Login-Links (enthalten den Client-Key).
  Geprüft wird nur Länge/Format. Links/Tokens für die Person nur als Datei im Scratchpad.
- **TikTok: nur Entwürfe** (`tiktok_upload.py draft` → Inbox). Nie direkt posten. Die Person postet selbst mit Caption.
- **YouTube: immer `--privacy private` + `--publish-at`** (Termin), nie sofort öffentlich. Ein Upload lässt sich per API
  nicht löschen/ändern (Token hat nur `youtube.upload`) → **vor dem Upload prüfen**, nicht danach.
  Muss eine Version ersetzt werden: neue Version **privat ohne Termin** hochladen, Person löscht die alte und setzt den Termin.
- **Keine Szene zweimal** in Compilations (Protokoll `clips/compilations.md`). Nur No-Commentary-Quellen, Credit nennen.
- Branch: `claude/focused-lovelace-4vw9gu` (kein PR). Commit + Push am Ende jedes Laufs.

## 1. Tagesplan (MEZ)
| Zeit | Kanal | Was |
|---|---|---|
| 13:00 | YouTube | Short 1 (aus der Compilation des Tages) |
| 17:00 | YouTube | Short 2 |
| 19:00 | YouTube | Compilation (9–11 min) |
| Mo–Fr 12:30 · 17:00 · 21:00 / Sa–So 11:00 · 15:00 · 20:00 | TikTok | 3 BeyondExcuses-Folgen (Entwürfe; Person postet) |

Produktion am Vortag oder bis spätestens 11:30 am selben Tag. Ein Tageslauf dauert ~2–3 h (Aufnahme 1 h, Render, Upload).

## 2. Einrichtung in einer frischen Sitzung
```bash
python3 -m pip install -q streamlink            # Twitch-Aufnahme
python3 clips/tiktok_upload.py whoami           # muss "BeyondExcuses" ausgeben
```
- TikTok-Login kommt aus `TIKTOK_REFRESH_TOKEN` (Umgebungseinstellungen, 365 Tage gültig). Fehlt er:
  `login` → Link als Datei an die Person → Weiterleitungsadresse → `exchange "<Adresse>"` (PKCE ist eingebaut).
  Danach `export-refresh <scratchpad-datei>` und die Person bitten, den Wert als `TIKTOK_REFRESH_TOKEN` einzutragen.
- YouTube: `YOUTUBE_CLIENT_ID/SECRET/REFRESH_TOKEN` = **Virlix**-Kanal (GTA). BeyondExcuses hat keinen YouTube-Token.
- Gesperrter Host (Proxy-403 im Log): `update_environment` mit genau diesem Host (z. B. TikTok-Upload
  `open-upload-i18n.tiktokapis.com`, Twitch-CDN `<id>.j.cloudfront.hls.ttvnw.net`). In einem unbeaufsichtigten Lauf
  kann niemand freigeben → Kanal wählen, dessen Server schon erlaubt ist, und den Host im Tagesbericht nennen.

## 3. Virlix (YouTube): Compilation + Shorts
Leitfaden mit Recherche und Genres: **`clips/COMPILATION_STYLE.md`** – vor jedem Schnitt lesen.
1. **Quelle finden:** Twitch-GQL `streams(options:{freeformTags:["NoCommentary"]})`, GTA VI, Sprache EN.
   Bewährt: **00mute** (24h-Stream, kein Kommentar, gute Action). Vorher `clips/compilations.md` prüfen (Kanalwechsel = frische Szenen).
2. **Aufnehmen:** `bash clips/record_loop.sh <kanal> /home/user/rec 15 4` (Hintergrund, ~1 h). Log auf 403 prüfen.
3. **Sichten:** Kontaktbogen je Block (`fps=1/30,tile=5x6`), dann dichter um Kandidaten. Whisper (small.en) auf
   eine Stichprobe: nur Spieldialog/Polizeifunk, keine Streamer-Stimme.
4. **Spec** (`compile.py` v2): 6–7 Kapitel à 60–120 s, je eine Geschichte (Aufbau → Pointe), `"countdown": true`
   (beste Szene als #1 zuletzt), Totzeit (Karte, Menü, Handy, schwarzes Bild, leere Fahrt > 10 s) per `"cont": true`
   herausschneiden, höchstens 1 Punch-Text pro Kapitel, ehrliche Labels. Genre-Reihen abwechseln (Leitfaden).
5. **Render:** `python3 clips/compile.py spec.json out.mp4` (~10 min).
6. **Prüfen vor Upload (Pflicht):** Kontaktbogen 1 Bild / 25 s; `freezedetect=n=0.003:d=1` (nur Intro/Outro dürfen
   stehen); −14 LUFS ±1; Kapitel aus `<out>.chapters.txt` stimmen mit Bild überein.
7. **Shorts:** 2 Momente aus der Compilation (#1/#2): `python3 clips/clipper.py cut <block.ts> <a> <b> --gameplay --raw
   --hook "Zeile 1|Zeile 2" --credit "via <kanal>" --out …` – 25–35 s, Pointe am Ende, Clip endet kurz nach der Pointe,
   Hook ehrlich (nur was passiert). Prüfen: Bild ab Sekunde 0 in Bewegung, Hook sichtbar, freezedetect leer.
8. **Thumbnail:** `python3 clips/thumb.py <video> <sek> "ZEILE 1" "ZEILE 2" out.jpg` – Bild mit klarer Aktion (kein Menü,
   keine Karte, nicht zu dunkel). Mehrere Sekunden testen und ansehen. `--thumbnail` nur, wenn der Kanal verifiziert ist
   (sonst 403 → Datei der Person geben).
9. **Upload:** `clips/yt_upload.py … --privacy private --publish-at <Datum>T19:00:00+01:00` (Shorts 13:00 / 17:00,
   Titel mit `#Shorts`, Beschreibung mit Link zur Compilation). Ausgabe **nicht** abschneiden – die Video-ID steht darin.
10. **Protokoll:** `clips/compilations.md` (Quellen, Link, Termin), `clips/yt_shorts.json`. Person erinnern:
    „Ähnliches Video“ bei den Shorts setzen (nicht per API möglich).

## 4. BeyondExcuses (TikTok): 3 Folgen pro Tag
Serie und Regeln: **`beyondexcuses/episodes.md`** (Nummerierung, Look, Ideen), Captions: `beyondexcuses/youtube_shorts_plan.md`.
1. **Thema:** Die letzte Folge verspricht die nächste („Part N next: …“) → die MUSS kommen. Dann Ideenliste in
   `episodes.md`; jede neue Folge verspricht die übernächste. Angezeigte Nummer = letzte TikTok-Nummer + 1.
2. **Bauen:** `beyondexcuses/epNN.py` nach Vorlage `ep21.py`–`ep23.py` (grau = negativ, amber = positiv, Hook 2 Zeilen,
   TALK-Blasen, Zeitsprung-Chip, TURN-Moment, `end_text`, CTA `"Part N next:\n…"` – bei 3/Tag nie „tomorrow“).
3. **Standbilder prüfen:** `VID_LANG=en python3 epNN.py still` → `check/epNN_sheet.jpg` ansehen: nichts abgeschnitten,
   keine Blase über Schild/Label/anderer Blase, Szene nicht zu klein, nichts über x > 900 (rechte TikTok-Buttons).
4. **Render:** `VID_LANG=en python3 epNN.py render` (~4 min, 3 parallel ok bei 4 Kernen). Sound-Ereignis `"step"`
   braucht 3 Felder (`["step", t, 0]`).
5. **Audit:** `python3 ../kanaele/data/audit.py FolgeNN_*_EN.mp4` (Berichte landen in `kanaele/data/audit/` → nach
   `beyondexcuses/audit/` verschieben). Warnungen ansehen (`_ui.jpg`): Regen/Licht/Buchrücken = Fehlalarm, echter
   Text unter den Buttons = korrigieren.
6. **Cover:** Eintrag in `covers.py` (Szene, in der der Kontrast sichtbar ist), `VID_LANG=en python3 covers.py NN`, ansehen.
7. **Upload:** `python3 clips/tiktok_upload.py draft beyondexcuses/FolgeNN_*_EN.mp4`; Status später prüfen
   (`SEND_TO_USER_INBOX`).
8. **Tagespaket für die Person:** `beyondexcuses/tagespaket/<YYYY-MM-DD>.md` – je Folge Uhrzeit, Cover-Datei,
   Caption, Pin-Kommentar (Format wie `youtube_shorts_plan.md`), Hinweis „KI-generiert“ einschalten. Committen.
9. **Protokoll:** `episodes.md` (Tabelle + „Stand“-Zeile + neues Versprechen), Caption-Abschnitt in `youtube_shorts_plan.md`.

## 5. Qualitäts-Checkliste (vor jedem Upload abhaken)
- [ ] Erste Sekunde bewegt sich, Hook sofort lesbar (Shorts/TikTok) bzw. Cold Open (Compilation)
- [ ] Kein Standbild außer Intro/Outro (freezedetect)
- [ ] −14 LUFS, kein Clipping
- [ ] Texte ehrlich, Labels passen zum Bild, Credits drin
- [ ] Nichts unter TikTok-UI (oben < 210, rechts x > 900 bei y 760–1660, unten y > 1450)
- [ ] Thumbnail/Cover angesehen, nicht nur erzeugt

## 6. Laufend verbessern (Reichweite, Viralität, Qualität)
- **Jeder Lauf:** eine konkrete Verbesserung ausprobieren und in `.claude/skills/tagesproduktion/learnings.md`
  eintragen (Datum, was, warum, woran gemessen). Bewährtes in diesen Skill bzw. die Leitfäden übernehmen.
- **Daten:** Die API hat keinen Analytics-Zugriff → die Person um Screenshots bitten (YouTube Studio: Aufrufe,
  Zuschauerbindung, CTR, Abos je Video; TikTok: Aufrufe, Wiedergabedauer, Shares). Auswertung mit den Skills
  `yt-retention`, `yt-audit`, `yt-package`, `tiktok-viral-creator`. Erste Auswertung nach ~2 Wochen (ab 05.12.).
- **Hebel, die zu testen sind:** Hook-Formulierungen, Titel-/Thumbnail-Varianten, Genre-Reihen, Shorts-Länge
  (20 vs. 35 s), Countdown vs. chronologisch, Uhrzeiten, Serien-Cliffhanger, Pin-Kommentare.
- **Trends:** GTA-6-Launch-Phase – „Erste/Neue/Krasseste X in GTA 6“ zieht (Recherche im Leitfaden). Wöchentlich kurz
  recherchieren, was im Nischen-Umfeld läuft (`yt-viral`).

## 7. Bekannte Stolperfallen (aus echten Fehlern)
- **Standbild am Clip-Anfang:** Twitch-.ts nur alle paar Sekunden ein Keyframe → `clipper.exact_src` (8 s Vorlauf)
  ist eingebaut; trotzdem immer freezedetect.
- **Ausgabe von `yt_upload.py` nicht mit `tail` kürzen** – sonst ist die Video-ID weg (passiert am 21.11.).
- Push abgelehnt → `git fetch origin <branch> && git merge --no-edit FETCH_HEAD` (andere Sitzungen schreiben mit).
- `clips/transfer/`: große Videos für andere Sitzungen in 95-MB-Teilen; nach Upload löschen.
- Schwarzes Bild in Quellen (Licht aus im Spiel) und Waffen-/Masken-Menüs sind Totzeit → schneiden.
