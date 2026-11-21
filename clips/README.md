# GTA 6 Clip-Kanal (TikTok) – Playbook

Neuer Account der Person, nur echtes Gameplay aus englischen Twitch-Streams. Ziel: in der Launch-Phase (ab 18.11.2026, zuerst nur Neuseeland) möglichst schnell viele virale Szenen posten, bevor andere Clip-Kanäle sie haben.

## Grundregel (19.11.2026, Wunsch der Person)
**Nur noch reines Gameplay** von No-Commentary-Kanälen (kein Streamer im Bild, keine Streamer-Stimme): besserer Ton und besseres Bild, nichts muss mehr herausgerechnet werden.
- Suche: Twitch-GQL `streams(options: {freeformTags: ["NoCommentary"]})`, Kategorie GTA VI, Sprache en. Bewährt: **skrimskeez** (Free Roam, Lucia), **mrperfectog91** (Story, Jason). Meiden: Kanäle mit fremdsprachiger Spiel-Oberfläche.
  Suche mit `python3 clips/twitch_find.py --tag NoCommentary`. **Vor dem Aufnehmen 20 s probeweise ziehen** (`streamlink --hls-duration 00:00:20`) und 3 Standbilder ansehen: Facecam? Rahmen/schwarze Ränder? **Sprache der Spiel-Oberfläche** (21.11.: steinbrandt = Deutsch, kuzmanix_v = Russisch → ungeeignet; 00mute und optimus_789 = Englisch).
- Schnitt mit `--gameplay --raw` (Originalton, keine Stimmtrennung).
- **Speicher:** compile.py braucht für Zwischendateien etwa so viel Platz wie das ganze Rohmaterial der benutzten Blöcke (am 21.11. lief die Platte voll). Darum die gewählten Fenster vorher verlustfrei ausschneiden (`ffmpeg -ss <start-15> -i block.ts -t <dauer> -c copy cut.ts`), die Zeiten in der Spec umrechnen und die großen Blöcke löschen. optimus_789 sendet ~700 MB pro 15 min.
- **YouTube-Compilations mindestens 8 Minuten**, Abschnitte 60–120 s (`compile.py` v2, `"audio": "raw"`), Kapitel aus `<out>.chapters.txt`. **Stil-Leitfaden: `clips/COMPILATION_STYLE.md`** (Cold Open, kurze Übergänge, Totzeit schneiden, Countdown, Genres).

## Werkzeuge
- `twitch_find.py` – Live-Streams einer Kategorie (Standard „Grand Theft Auto VI“, Sprache en) nach Zuschauern.
- `pick_streamer.py` – hört bei den Top-Streams 30–45 s rein, misst den Sprechanteil, speichert ein Standbild je Stream (Facecam-Check).
- `record_loop.sh <kanal> <ordner> [min] [anzahl]` – Daueraufnahme in Blöcken; fertiger Block bekommt `.done`.
- `clipper.py cats <video>` – beste Momente je Kategorie (funny / action / secrets).
- `clipper.py cut <video> <start> <ende> --gameplay --raw --hook "Zeile" --credit "via <kanal>" --out <datei>` – fertiger 9:16-Clip aus No-Commentary-Material (`--dialog` nur noch für alte Streamer-Aufnahmen).
- `compile.py <spec.json> <out.mp4>` – 16:9-Compilation mit Intro/Outro, Kapiteln, Logo, −14 LUFS (2 Durchgänge).

## Clip-Regeln
- **Bild (v2, 18.11. nach Feedback „schneidet zu viel aus“):** breites 1,2:1-Fenster (67 % der Breite, volle Höhe, fast ohne Hochskalierung) mittig im 9:16-Bild, dunkel-unscharfer Rand. Die echten GTA-Untertitel bleiben im Bild. Overlays, die ins Fenster ragen (`HIDE`, z. B. Peanut-Avatar), werden unscharf gemacht und mit einem weichen Badge „GTA 6 DAILY CLIPS“ überdeckt; bei Facecams am Rand wird das Fenster verschoben (`CX`: xqc 0.66, darkviperau 0.37).
- **Ton (`--dialog`, v2, nach Feedback „Dialoge abgehackt“):** KI-Stimmtrennung (UVR-MDX); die Stimmspur bleibt offen, solange ein GTA-Untertitel im Bild steht (OCR 4×/s, 0,35 s vorher, 0,6 s nachher, Lücken < 0,8 s überbrückt, 150-ms-Blenden) – sonst stumm (= Streamer). Ohne Dialog: nur Musik/Effekte. −14 LUFS.
- **Keine eigenen Untertitel** im Gameplay-Modus (die Spiel-Untertitel sind vollständig im Bild).
- **Hook:** 2 Zeilen, ehrlich (nur was im Clip passiert), Zeile 1 kurz (≤ 24 Zeichen = volle Größe). Schriftgröße passt sich automatisch an.
- **Prüfen vor dem Abliefern:** Whisper (small.en) auf den fertigen Ton – darf keine Streamer-Sätze enthalten; Kontaktblatt 1 Bild / 3 s ansehen (Hook passt zum Inhalt, nichts abgeschnitten).
- Länge 25–35 s, Pointe in den letzten 5 s, Start direkt in der Aktion.

## Kategorien (Priorität)
1. **Lustig & unerwartet:** NPC-Reaktionen, absurde Dialoge, Unfälle, verrückte Situationen.
2. **Polizei & Action:** Verfolgungsjagden, Fluchten, Schießereien, Carjacks, Polizeikontrollen.
3. **Geheimnisse & Details:** Easter Eggs, versteckte Details, Map-Entdeckungen, Theorien.
Story-Zwischensequenzen nur mit ⚠️-Spoiler-Hinweis in der Caption.

## Streamer-Wahl
1. **theburntpeanut** (keine Facecam, nur Avatar unten links).
2. Wenn er offline ist: `pick_streamer.py` → wenig Sprechanteil + Facecam in einer Ecke (nicht in der Bildmitte). Kandidaten 18.11.: lacy (29 % Sprechanteil), jasontheween (67 %).
3. Twitch liefert Video über wechselnde CloudFront-Server (`<id>.j.cloudfront.hls.ttvnw.net`). Meldet `pick_streamer.py`/streamlink einen blockierten Server → mit `update_environment` freigeben lassen.

## Caption-Vorlage (TikTok)
```
<Hook-Satz mit 1–2 Emojis>
<Frage an die Zuschauer> 👇
🎥 via <streamer>
#gta6 #gtavi #gta #gaming #rockstargames
```
KI-Label: nicht nötig (echtes Material). Quelle nennen senkt das Strike-Risiko.

## Speicher
Ein 15-min-Block ≈ 400 MB (skrimskeez) bis 700 MB (mrperfectog91). Die Platte fasst nur wenige Blöcke: höchstens 2 Kanäle × 4 Blöcke aufnehmen, dann schneiden und löschen. Nach dem Schneiden Block löschen, `/tmp/tmp*` (Stimmtrennung) leeren. Unter 2 GB frei → Aufnahme pausieren.
