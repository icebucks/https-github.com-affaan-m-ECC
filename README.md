# „Ich war dabei“ – automatische TikTok-Videos: Geschichte aus der Ich-Sicht

Aus einem kurzen Skript (JSON) entsteht automatisch ein fertiges, animiertes Hochkant-Video
(1080×1920, 30 fps, MP4) mit Erzählerstimme, Wort-für-Wort-Untertiteln, Atmo, Musik und Endkarte.
Alles läuft lokal und kostenlos – keine bezahlten APIs. Rendering mit [HyperFrames](https://hyperframes.heygen.com).

## Schnellstart
```bash
npm run setup     # einmalig: HyperFrames, Python-Pakete, Stimmen (idempotent)
npm run batch     # rendert alle Skripte in scripts/, für die es noch kein output/<id>.mp4 gibt
```
Ergebnis pro Video:
- `output/<id>.mp4` – fertiges Video (−14 LUFS)
- `output/<id>_upload.txt` – Bildunterschrift mit Frage, Hashtags und Hinweis „KI-Label beim Upload aktivieren“

Es wird **nichts automatisch hochgeladen**.

## Neues Video hinzufügen
1. Datei `scripts/<nr>-<name>.json` anlegen (am besten ein bestehendes Skript kopieren):
   ```json
   {
     "id": "04-hannibal",
     "titel": "Hannibal – Über die Alpen",
     "jahr_ort": "218 v. Chr. – Alpen",
     "epoche": "roemer",
     "erzaehltext": "Ich bin Elefantentreiber … Teil zwei folgt.",
     "szenen": [
       { "ab_satz": 0, "motiv": "kolonne_wald", "beschreibung": "…" },
       { "ab_satz": 6, "motiv": "speere", "beschreibung": "…", "wendepunkt": true }
     ],
     "endkarte": "Teil 2 folgt",
     "atmo": ["wind"], "musik": "drone_moll",
     "bildunterschrift": "…", "frage": "…?",
     "hashtags": ["#geschichte", "#history", "…"]
   }
   ```
   - **Zahlen ausschreiben** („dreißig“, nicht „30“) – sonst bricht der Build ab. Jahreszahlen nur in `jahr_ort`.
   - `ab_satz` = ab welchem Satz (0 = erster Satz) die Szene beginnt. Lange Szenen werden automatisch geteilt.
   - Verfügbare `motiv`e: siehe `pipeline/lib/motifs/*.mjs` (Römer, Pompeji, Titanic). Neue Epochen brauchen
     neue Motive + Palette – das übernimmt Claude mit dem Skill `.claude/skills/geschichte-video`.
2. Aussprache prüfen: `npm run aussprache -- scripts/04-hannibal.json`
   Zeilen mit `PRÜFEN` kontrollieren und in `pipeline/aussprache.json` eintragen (Anleitung steht in der Ausgabe).
3. Vorschau ohne Rendern: `npm run build -- 04-hannibal --no-render`, dann
   `cd compositions/04-hannibal && npx hyperframes preview` (Studio im Browser).
4. Rendern: `npm run build -- 04-hannibal` oder einfach `npm run batch`.

## Tägliche Automatisierung (2 Videos pro Tag)
Ein geplanter Claude-Task startet jeden Morgen eine Cloud-Sitzung in der Umgebung **ich-war-dabei** und
1. liefert **Teil 2** der Geschichte vom Vortag,
2. schreibt eine **neue Geschichte (Teil 1)** aus `ideen/backlog.json` – in einer anderen Epoche,
3. recherchiert neue Ideen, wenn der Vorrat knapp wird,
4. prüft Aussprache und Bilder, rendert, committet auf den Branch und schickt dir die MP4s mit Upload-Text.

Die Regeln dafür (Geschichten, Aussprache, Stil, Prüfungen) stehen in `.claude/skills/geschichte-video/SKILL.md`.

## Kanal
Name, Bio und Profilbild: `account/profil.md`, `account/profilbild.png`.

## Wie es funktioniert
| Schritt | Datei | Was passiert |
| --- | --- | --- |
| Aussprache | `pipeline/g2p_de.py`, `pipeline/aussprache.json` | eigenes Lexikon > gruut (nur wenn plausibel) > espeak-ng |
| Stimme | `pipeline/tts_coqui.py` | Coqui VITS „Thorsten“ (lokal), etwas tiefer gelegt; Wort-Zeitstempel exakt aus den Phonem-Dauern. Mit `ELEVENLABS_API_KEY` wird ElevenLabs genutzt (1 Take, gecacht). `TTS_ENGINE=piper` = Reserve-Stimme |
| Zeitplan | `pipeline/lib/compose.mjs` | Sätze → Szenen, Hook 0–2 s, Wendepunkt, Endkarte |
| Bild | `pipeline/lib/motifs/`, `figures.mjs`, `svg.mjs`, `runtime.js` | SVG-Parallax-Ebenen, Silhouetten, Partikel (Regen, Nebel, Asche, Funken, Gischt …), Licht, Kamerafahrt; GSAP, deterministisch |
| Untertitel | `compose.mjs` | Wort für Wort, aktives Wort in der Epochen-Akzentfarbe, TikTok-Safe-Zone |
| Audio | `pipeline/audio_mix.py` | Atmo, Musik-Drone, Trommeln, Effekte – alles prozedural erzeugt (keine Lizenzfragen); Ducking; −14 LUFS |
| Render | HyperFrames-CLI | Lint → Render → x264-Endkodierung |

Ordner: `scripts/` (Skripte) · `assets/<id>/` (Stimme, Wortzeiten, Transkript, Audio-Mix) ·
`compositions/<id>/` (HyperFrames-Projekt) · `output/` (Videos + Upload-Texte) · `ideen/` (Story-Vorrat).

## Anforderungen
Node.js ≥ 22, FFmpeg (mit rubberband), Python ≥ 3.10. `npm run setup` installiert den Rest.
Rendern dauert ca. 8 Minuten pro 40-Sekunden-Video (CPU).
