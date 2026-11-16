# Cosmic Scale – long-form channel with narrator (Konzept)

## Nische & Begründung (16.11.2026)
**Weltall & Größenordnungen, erzählt:** „How long / how far / how big“ – Reise-, Distanz- und Zeitfragen zu konkreten Himmelskörpern, mit Maßstabs-Animationen.
- Konkurrenz-Analyse (`/yt-viral`, 319 lange Videos aus 12 Kanälen, Rohdaten `../youtube/long_space.json`): stärkste Ausreißer sind genau diese Fragen – „How Long Would It Actually Take to Travel to Pluto“ 30×, „Why It's Impossible to Reach Neptune“ 26×, „The Distance Between Galaxies…“ 13×, „…Traveling 1 Light-Year“ 9× über dem eigenen Kanal-Median. 4,4 % aller Videos schaffen ≥ 10×; mittelgroße Kanäle (Median 15.500 Aufrufe) haben 30×-Ausreißer → die Nische belohnt Ideen, nicht Kanalgröße.
- Dieselbe Struktur gewinnt bei Shorts (Daten-Nische: „Time to reach the moon?“ 28×) → By The Numbers liefert passende Shorts als Zubringer.
- Werbeerlös laut Creator-Guides ca. 5–12 $ RPM (Science/Space); Finanzen wären höher (10–40 $), aber mit Finanzberatungs-Risiko und härterer Konkurrenz (`../youtube/long_finance.json`). Entscheidung: Space – prüfbare Fakten (NASA), kaum Regelrisiko, passt zu unserer Animations-Engine.

## Kanal
- **Name (Arbeitstitel):** `Cosmic Scale` · Handle-Ideen: `@cosmicscale`, `@cosmicscalehq`, `@thecosmicscale` (Verfügbarkeit nur bei der Anmeldung prüfbar)
- **Profilbild:** `profil_cosmic_scale.jpg`
- **Beschreibung:**
```
How long would it take you to get there? How big is it really?
Calm, exact, narrated videos about the scale of space – every number sourced, every comparison you can feel.
🎬 A new long video every week + Shorts.
```
- **Stimm-Profil:** `../youtube/voice_cosmicscale.md`
- **Sprecher:** Kokoro-82M (Apache-2.0, lokal, kommerziell nutzbar), Proben in `voice/`. Empfehlung: `bm_george` (britischer Doku-Ton) oder `am_michael` (warm, amerikanisch). Whisper-Verständlichkeit aller Proben 80–82 % (Abweichungen = Zahlen als Ziffern).

## Rhythmus (`/yt-plan`)
- **1 langes Video pro Woche** (Anker, 8–12 min, Mid-Roll-Werbung ab 8 min möglich), immer am selben Tag.
- **3 Shorts pro Woche aus dem langen Video geschnitten** (`/yt-shorts`: neue erste Zeile, Loop-Punkt) – auf diesem Kanal, mit Verweis aufs lange Video.
- By The Numbers macht zum selben Thema einen eigenen Short (Zubringer).

## Produktions-Pipeline (aufzubauen nach Freigabe)
1. Thema → Recherche (NASA/ESA/JPL, Datum notieren) → Skript nach `/yt-script` (5 Hooks, `hookscore.py` ≥ 72, Wendepunkt bis 0:35, Beats mit `[ON SCREEN]`, Auflösung, eine Aufforderung).
2. Sprecher: Kokoro (kokoro-onnx), Absatz für Absatz → Whisper-Wortzeiten → Zeitachse.
3. Bild: By-The-Numbers-Engine (Maßstabs-Zoom, Renn-Bahnen, Zähler, Zeitleisten, Flaggen), alle 4–8 s ein neues Element, Kapitel-Karten.
4. Ton: eigene Musik (`music.py`, cinematic/synthwave/lofi, unter der Stimme abgesenkt) + CC0-Effekte, −14 LUFS.
5. Kapitel mit `/yt-chapters` (chapters.py prüft YouTubes Regeln), Untertitel als SRT aus Whisper.
6. Verpackung `/yt-package` (10 Titel, ≥ 90; Titelbild 3 Wörter), Beschreibung `/yt-seo` (3 Suchanfragen in Titel + 2 ersten Zeilen).
7. Audit (`../data/audit.py`) + Retention-Auswertung (`/yt-retention`) nach dem Upload.

## Pilot
`pilot_script.md` – „How long to travel to the nearest star? 5 ways compared“ (title.py 98/100, Titelbild „46 MILLION YEARS“), Hook 82/100 STRONG mit aktuellem Aufhänger (Voyager 1 erreicht am 18.11.2026 einen Lichttag Entfernung). Entwurf: 593 Wörter ≈ 4 min → für ≥ 8 min um 3 Beats erweitern (z. B. „Was wir von Proxima aus sehen würden“, „Proxima b“, „Warum schneller = Energieproblem“), Fakten vorher prüfen.

## Themen-Backlog (lange Videos)
1. How long to travel to the nearest star? (Pilot)
2. How far has Voyager 1 really gone – and what will it reach first? (aktuell: 1 Lichttag)
3. How fast are you moving right now? Rotation, orbit, the Sun around the galaxy
4. How long is a day on every planet?
5. How long would it take to travel to every planet in the Solar System?
6. How cold can space get? From Antarctica to the coldest place we know
7. How big is the Milky Way if the Sun were a grain of sand?
8. How long does light take to reach us from the things we see at night?

## Geld (Fahrplan)
YouTube-Partnerprogramm: 1.000 Abonnenten + 4.000 Stunden Wiedergabezeit in 12 Monaten. Bei 10-min-Videos und 50 % durchschnittlicher Wiedergabe ≈ 48.000 Aufrufe insgesamt. Danach Werbung (Mid-Rolls ab 8 min), später Sponsoring (Lern-/Wissenschafts-Apps passen).
