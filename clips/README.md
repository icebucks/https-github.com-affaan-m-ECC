# GTA 6 Clip-Kanal (TikTok) – Playbook

Neuer Account der Person, nur echtes Gameplay aus englischen Twitch-Streams. Ziel: in der Launch-Phase (ab 18.11.2026, zuerst nur Neuseeland) möglichst schnell viele virale Szenen posten, bevor andere Clip-Kanäle sie haben.

## Werkzeuge
- `twitch_find.py` – Live-Streams einer Kategorie (Standard „Grand Theft Auto VI“, Sprache en) nach Zuschauern.
- `pick_streamer.py` – hört bei den Top-Streams 30–45 s rein, misst den Sprechanteil, speichert ein Standbild je Stream (Facecam-Check).
- `record_loop.sh <kanal> <ordner> [min] [anzahl]` – Daueraufnahme in Blöcken; fertiger Block bekommt `.done`.
- `clipper.py cats <video>` – beste Momente je Kategorie (funny / action / secrets).
- `clipper.py cut <video> <start> <ende> --gameplay --dialog --hook "ZEILE 1|zeile 2" --out <datei>` – fertiger 9:16-Clip.

## Clip-Regeln
- **Bild:** 4:5-Fenster aus der Bildmitte, über dem Untertitelband (Facecam, Chat, Minimap und der Peanut-Avatar liegen in den Ecken und fallen raus), unscharfer Rand, 1080×1920.
- **Ton (`--dialog`):** KI-Stimmtrennung (UVR-MDX) → Wörter der Stimmspur (Whisper) gegen die GTA-Untertitel (OCR) prüfen → nur Sätze, die als Untertitel im Bild stehen, bleiben (Spieldialog); alles andere = Streamer → stumm. Ohne Dialog: nur Musik/Effekte. −14 LUFS.
- **Untertitel:** eigene Wort-für-Wort-Untertitel aus dem bereinigten Dialog (Halluzinationsfilter: Wörter > 1,5 s und Einzelwörter fliegen raus).
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
Ein 15-min-Block 720p ≈ 500 MB. Nach dem Schneiden Block löschen, `/tmp/tmp*` (Stimmtrennung) leeren. Unter 2 GB frei → Aufnahme pausieren.
