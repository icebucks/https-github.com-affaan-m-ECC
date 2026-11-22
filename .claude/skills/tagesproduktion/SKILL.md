---
name: tagesproduktion
description: Tägliche Produktion und Veröffentlichung für Virlix (YouTube, GTA-6-Gameplay ohne Kommentar) und BeyondExcuses (TikTok, Mindset-Serie) – jeden Tag 1 Compilation + 1–2 Shorts auf YouTube und 3 neue TikTok-Folgen als Entwurf, mit Qualitätsprüfung, Protokoll und laufender Verbesserung von Reichweite, Viralität und Videoqualität. Verwenden bei „Tagesproduktion“, „mach die Videos für heute/morgen“, „Compilation“, „Shorts“, „neue Folgen“, „wie läuft der Kanal“, „was können wir verbessern“ und bei jedem geplanten Tageslauf.
---

# Tagesproduktion Virlix + BeyondExcuses

**Auftrag der Person (neu 22.11.2026, ersetzt 21.11.):** Ziel ist **Monetarisierung** von Virlix, bei schonendem Umgang
mit dem Claude-Wochenlimit („nur das Nötigste“, keine Doppelarbeit, kein Blackout durch zu viel auf einmal):
- **BeyondExcuses (TikTok):** 2–3 Shorts pro Tag (Entwürfe).
- **Virlix (YouTube):** 1–2 Shorts pro Tag · **Compilations 2× pro Woche** · **Walkthroughs 3× pro Woche** · **Ambient 1× pro Woche**.
- **VirlixYT (TikTok):** 1–2 GTA-Shorts pro Tag (Entwürfe).
Laufen lassen, Resonanz beobachten, nebenbei verbessern. Antworten und Protokolle auf Deutsch.

**Budget-Regeln (Wochenlimit):** pro Lauf nur das, was laut Wochenplan heute fällig ist. Kontaktbögen klein (≤ 1600 px breit)
und nur so viele wie nötig ansehen; Material aus einer Aufnahme mehrfach nutzen (Compilation-/Walkthrough-Aufnahme liefert
auch die Shorts). Lieber einen Teil sauber liefern und den Rest im Bericht nennen, als alles halb.

## 0. Regeln, die nie gebrochen werden
- **Geheimnisse:** Werte von `YOUTUBE_*` / `TIKTOK_*` nie ausgeben – auch nicht Login-Links (enthalten den Client-Key).
  Geprüft wird nur Länge/Format. Links/Tokens für die Person nur als Datei im Scratchpad.
- **TikTok: nur Entwürfe** (`tiktok_upload.py draft` → Inbox). Nie direkt posten. Die Person postet selbst mit Caption.
- **YouTube: immer `--privacy private` + `--publish-at`** (Termin), nie sofort öffentlich. Ein Upload lässt sich per API
  nicht löschen/ändern (Token hat nur `youtube.upload`) → **vor dem Upload prüfen**, nicht danach.
  Muss eine Version ersetzt werden: neue Version **privat ohne Termin** hochladen, Person löscht die alte und setzt den Termin.
- **Keine Szene zweimal** in Compilations (Protokoll `clips/compilations.md`). Nur No-Commentary-Quellen, Credit nennen.
- Branch: `claude/focused-lovelace-4vw9gu` (kein PR). Commit + Push am Ende jedes Laufs.

## 1. Wochenplan (MEZ)
| Tag | YouTube Virlix (19:00 Langvideo) | Shorts |
|---|---|---|
| Mo | **Walkthrough** (1 Mission) | täglich: YouTube 1–2 Shorts (13:00 / 17:00), VirlixYT-TikTok 1–2 Entwürfe (12:30 / 16:30), BeyondExcuses 2–3 Entwürfe (Mo–Fr 12:30 · 17:00 · 21:00 / Sa–So 11:00 · 15:00 · 20:00) |
| Di | – | ″ |
| Mi | **Walkthrough** + **Compilation** (Compilation 19:00, Walkthrough 21:00) | ″ |
| Do | – | ″ |
| Fr | **Walkthrough** | ″ |
| Sa | **Compilation** | ″ |
| So | **Ambient** (30–60 min, ruhig) | ″ |

Ein Lauf produziert für den **nächsten** Tag laut dieser Tabelle. Shorts kommen bevorzugt aus der Aufnahme des
Langvideos (eine Aufnahme, mehrere Videos).

### Walkthroughs (Mo/Mi/Fr) – Titel `GTA 6 Walkthrough – Mission: <Name> (No Commentary)`, Playlist „GTA 6 Walkthrough“
1. Quelle: Story-Stream ohne Kommentar mit englischer Oberfläche (21.11. gut: **itzradflemix** „Walkthrough 4K PS5 Pro“).
   Aufnahme 4 × 15 min reicht meist für eine Mission.
2. `python3 clips/walkthrough.py scan <block.ts>` (≈ 1,5 min pro Block): MENU-Zeiten (Karte/Pause/Brief), NAME (Missionsname
   aus Spielstand „Pipework (6%)“), PASS/FAIL, TEXT (Titelkarten). **Missionsname nur vom Bildschirm**, nie raten; ist keiner
   lesbar, Titel nach dem Ort/Ziel der Mission („Airboat Escape“) und im Bericht nennen.
3. Missionsgrenzen festlegen (Start = Missionsbeginn/Titelkarte, Ende = PASS bzw. Abschluss-Szene), dann
   `python3 clips/walkthrough.py clean <block.ts> <start> <ende> --label "<NAME>"` → Segmente ohne Menüs für compile.py.
   Fehlversuche (FAIL) und Wiederholungen herausschneiden. Kapitel = Missionsabschnitte (`"cont": false` mit Label je Ziel).
4. Länge = Missionslänge (ohne Totzeit), mindestens 8 min; kürzere Missionen zu „Mission X & Y“ zusammenfassen.
5. Prüfen wie Compilations (Kontaktbogen, freezedetect, −14 LUFS), Beschreibung mit Kapiteln + Credit, privat mit Termin.

### Ambient (So) – Titel `GTA 6 Relaxing <Night Drive|Ocean|Sunset> – <Dauer> (No Commentary)`, Playlist „GTA 6 Ambient“
Nur ruhige Fahrten/Natur ohne Menüs, Schießereien, Dialog-Zwischensequenzen; lange Stücke, weiche Übergänge, keine
Punch-Texte, kein Countdown. 30–60 min. Gleiche Marke (Intro/Outro), damit der Kanal einheitlich bleibt.

## 2. Einrichtung in einer frischen Sitzung
```bash
python3 -m pip install -q streamlink            # Twitch-Aufnahme
apt-get install -y -qq tesseract-ocr tesseract-ocr-eng   # OCR für walkthrough.py scan
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
7. **Shorts – Auswahl (Daten 22.11.: Fail-Clip 503 Aufrufe vs. ruhige Nachtszene 3):** zuerst **Fails, Crashes, Fahrzeug-Missgeschicke, NPC-Chaos** suchen, hell und klar; Hook = Spannungssatz („…then the bus showed up“), nicht Beschreibung.
7. **Shorts:** 2 Momente aus der Compilation (#1/#2): `python3 clips/clipper.py cut <block.ts> <a> <b> --gameplay --raw
   --hook "Zeile 1|Zeile 2" --credit "via <kanal>" --out …` – 25–35 s, Pointe am Ende, Clip endet kurz nach der Pointe,
   Hook ehrlich (nur was passiert). Prüfen: Bild ab Sekunde 0 in Bewegung, Hook sichtbar, freezedetect leer.
8. **Thumbnail:** `python3 clips/thumb.py <video> <sek> "ZEILE 1" "ZEILE 2" out.jpg` – Bild mit klarer Aktion (kein Menü,
   keine Karte, nicht zu dunkel). Mehrere Sekunden testen und ansehen. `--thumbnail` nur, wenn der Kanal verifiziert ist
   (sonst 403 → Datei der Person geben).
9. **Upload:** `clips/yt_upload.py … --privacy private --publish-at <Datum>T19:00:00+01:00` (Shorts 13:00 / 17:00,
   Titel mit `#Shorts`, Beschreibung mit Link zur Compilation). Ausgabe **nicht** abschneiden – die Video-ID steht darin.
9b. **Cover für jeden Short (Pflicht):** `python3 clips/thumb.py <short.mp4> <sek> "ZEILE 1" "ZEILE 2" clips/covers/Cover_<name>.jpg --vertical`
    (Text oben im dunklen Band, Logo unten; ansehen!). Im Paket nennen + der Person schicken – sie wählt es beim Posten auf TikTok.
10. **Shorts zusätzlich auf TikTok (VirlixYT):** jeden Short auch als Entwurf: `python3 clips/tiktok_upload.py --account virlix
    draft <short.mp4>` (Login aus `TIKTOK_REFRESH_TOKEN_VIRLIX`; `--account virlix whoami` muss VirlixYT zeigen). Captions nach
    Vorlage in `clips/README.md` (Hook + Frage + „🎥 via <kanal>“ + 5 Hashtags), kein KI-Label, Zeiten 30 min vor dem YouTube-Short,
    Paket in `clips/tiktok_paket/<YYYY-MM-DD>.md`.
11. **Link-Kommentar unter Shorts, die heute online gingen** (vorher geht es nicht: private/geplante Videos → HTTP 403):
    `commentThreads.insert` mit „Full 10-minute GTA 6 compilation (<Name>) 👉 https://youtu.be/<id> \nWhat should we clip next? 👇“.
    In `clips/yt_shorts.json` beim Short `"comment": "<comment-id>"` eintragen (nie doppelt kommentieren). Anpinnen geht nur in der App →
    Person im Bericht daran erinnern. Erledigt: IMTOsLca1og (21.11.). Offen: lUSvzl9VYss (ab 21.11. 17:00), ZK8HhemFBWo, Ed42CNBR8Ng (ab 22.11.).
12. **Protokoll:** `clips/compilations.md` (Quellen, Link, Termin), `clips/yt_shorts.json`. Person erinnern:
    „Ähnliches Video“ bei den Shorts setzen (nicht per API möglich).

## 4. BeyondExcuses (TikTok): 2–3 Folgen pro Tag
Serie und Regeln: **`beyondexcuses/episodes.md`** (Nummerierung, Look, Ideen, **Retention-Standard v2 = PFLICHT ab Part 26**),
Captions: `beyondexcuses/youtube_shorts_plan.md`.
1. **Thema:** Die letzte Folge verspricht die nächste („Part N next: …“) → die MUSS kommen. Dann Ideenliste in
   `episodes.md`; jede neue Folge verspricht die übernächste. Angezeigte Nummer = letzte TikTok-Nummer + 1.
2. **Bauen nach Retention-Standard v2** (`episodes.md`): Hook als offene Frage (nie die Pointe), erstes Bild mit Aktion,
   Auflösung ≤ 7 s, 11–13 s, Zähler/Zeitraffer, Kamera ≈ 1,7× näher (Figuren ≥ 35 % Bildhöhe), ≤ 3 Blasen à ≤ 4 Wörter
   (`size=44`), Ende mit `lib.end_line` über laufender Handlung, CTA-Chip ≤ 1,2 s, Loop ins Anfangsbild. Grau = negativ,
   amber = positiv; CTA `"Part N next:\n…"` – nie „tomorrow“. Die erste v2-Folge dient als Vorlage für die nächsten.
   Prüfung zusätzlich: `python3 retention_qa.py FolgeNN_*_EN.mp4 --payoff <TURN>` → alles ✅.
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
- **Daten (Virlix, automatisch):** jeder Lauf zuerst `python3 clips/yt_stats.py --md clips/stats/<YYYY-MM-DD>.md` (Status, Termine,
  Aufrufe, Likes, Kommentare, Ø Wiedergabedauer, Ø gesehen %, +Abos je Video; Analytics hängen 1–2 Tage nach) und committen.
  Daraus ableiten: welches Genre/welcher Hook/welche Uhrzeit zieht → im Tagesbericht 1–2 Sätze dazu.
  **TikTok** hat keine Statistik-API → die Person um Screenshots bitten (Aufrufe, Wiedergabedauer, Shares). Auswertung mit
  `yt-retention`, `yt-audit`, `yt-package`, `tiktok-viral-creator`. Größere Auswertung nach ~2 Wochen (ab 05.12.).
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
- **Premieren:** Die Person plant Compilations teils als Premiere. Die API zeigt dann `privacyStatus: public` + `liveBroadcastContent: upcoming` + `liveStreamingDetails.scheduledStartTime` – das ist **noch nicht live**. `yt_stats.py` zeigt „Premiere <Zeit>“. Premieren nicht per `publishAt` umplanen (HTTP 503). Am 21.11. führte das fast zu einer doppelten Compilation.
- **Status-Check:** `python3 clips/yt_stats.py` zeigt alle Uploads mit Status/Termin/Zahlen (Token mit `youtube.force-ssl` + `yt-analytics.readonly`, siehe `clips/yt_auth.py`). Termine/Status lassen sich jetzt per `videos.update` korrigieren – nur bei Videos, die noch nie öffentlich waren.
- Schwarzes Bild in Quellen (Licht aus im Spiel) und Waffen-/Masken-Menüs sind Totzeit → schneiden.
