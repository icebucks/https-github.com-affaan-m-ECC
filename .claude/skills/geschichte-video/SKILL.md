---
name: geschichte-video
description: Produziert TikTok-Videos für den Kanal „Ich war dabei“ (Geschichte aus der Ich-Sicht einer einfachen Person) mit der HyperFrames-Pipeline dieses Repos – neue Geschichten erfinden und recherchieren, Skript-JSON schreiben, Aussprache prüfen, Motive bauen, rendern, Upload-Paket. Verwenden bei jeder Anfrage nach neuen Videos, Teil 2, der täglichen Produktion, Stimme/Aussprache oder neuen Epochen/Motiven.
---

# Kanal „Ich war dabei“ – Produktions-Skill

Ein Video = ein Skript `scripts/<id>.json` → `npm run build -- <id>` → `output/<id>.mp4` + `output/<id>_upload.txt`.
Alles läuft lokal und kostenlos. Kein automatisches Hochladen.

## 0. Einrichtung (jede frische Umgebung)
```bash
npm run setup        # Node-Pakete, Python (Coqui, gruut, piper, torch), Stimmen, Chrome – idempotent
```

## 1. Tagesproduktion (2 Videos pro Tag)
1. **Video A = Teil 2** der ältesten Geschichte mit `status: "teil1"` in `ideen/backlog.json`
   (das Versprechen „Teil 2 folgt“ wird am nächsten Tag eingelöst).
2. **Video B = neuer Teil 1** aus `ideen/backlog.json` (`status: "offen"`). Wähle eine **andere Epoche**
   als Video A und als die letzten 2 Tage (Abwechslung gegen „unoriginellen Massen-Content“).
3. Ist der Vorrat < 8 offene Ideen: **5 neue Ideen recherchieren und ergänzen** (gleiches Format, mit `fakten`/`vorsicht`).
4. Danach `status` aktualisieren (`teil1` → `fertig` mit `teil2: "<id>"`; `offen` → `teil1` mit `teil1: "<id>"`).
5. IDs fortlaufend: `NN-slug` bzw. `NN-slug-teil2` (NN = nächste freie Nummer in `scripts/`).

## 2. Geschichte schreiben – Regeln (strikt)
- Ich-Perspektive einer **einfachen Person**, die dabei war (kein König, kein Feldherr als Erzähler).
- **Historisch korrekt**: keine erfundenen Zahlen, Namen, Zitate. Unsicheres allgemeiner formulieren.
  Vor dem Schreiben Fakten mit WebSearch gegenprüfen, wenn verfügbar. Zitate nur dokumentierte, als „soll gesagt haben“, wenn überliefert.
- **Keine Gewalt im Detail** – Spannung über Andeutung, Ton, Licht. Kein Blut, keine Leichen.
- **Zahlen und Abkürzungen ausschreiben** („dreißig“, „neunzehnten“, „um vier“). `build` bricht bei Ziffern im Sprechtext ab.
  Jahreszahlen/Abkürzungen („n. Chr.“) stehen NUR in `jahr_ort` (Einblendung), nie im `erzaehltext`.
- Aufbau: Satz 1 = „Ich bin …“ (Rolle + Ort). Alltag in kurzen Sätzen → Wendepunkt („Dann: …“) → Cliffhanger → letzter Satz exakt **„Teil zwei folgt.“**
  Teil 2: Satz 1 knüpft an („Das Wasser steht mir bis zu den Knien.“), Ende mit Auflösung oder offenem Bild, letzter Satz z. B. „Folge mir für die nächste Geschichte.“ und `"endkarte": "Neue Geschichte morgen"`.
- Länge: 90–120 Wörter ≈ 35–40 s. Für >60 s (Creator-Programm): 160–200 Wörter, gleiche Struktur.
- Kurze Sätze (3–12 Wörter). Ein Satz = ein Bild. Sehr kurze Sätze („Kein Wind.“) bekommen automatisch längere Pausen.
- `bildunterschrift`: 1–2 Sätze + `frage` an die Zuschauer. `hashtags`: 5–8, Mischung aus groß (#geschichte #history) und speziell.

## 3. Skript-Format (`scripts/<id>.json`)
```json
{ "id": "04-hannibal", "titel": "…", "jahr_ort": "218 v. Chr. – Alpen", "epoche": "antike_berge", "figur": "elefantentreiber",
  "erzaehltext": "Ich bin … Teil zwei folgt.",
  "szenen": [ { "ab_satz": 0, "motiv": "<motiv>", "beschreibung": "…", "effekte": ["schnee"] },
              { "ab_satz": 7, "motiv": "<motiv>", "beschreibung": "…", "wendepunkt": true },
              { "ab_satz": 9, "motiv": "<motiv>", "ton": "stille" } ],
  "endkarte": "Teil 2 folgt", "atmo": ["wind"], "musik": "drone_moll",
  "bildunterschrift": "…", "frage": "…?", "hashtags": ["#geschichte", "…"] }
```
- `ab_satz` = Index des Satzes (0-basiert), ab dem die Szene beginnt (oder `start` in Sekunden).
- Szenen > 5,2 s werden automatisch in zwei Einstellungen geteilt (neuer Ausschnitt, gleiche Szene).
- `ton: "stille"` = Atmo und Musik fallen weg (starker Effekt vor dem Wendepunkt).
- `atmo`: regen, wald, feuer, stadt, maschine, wasser. `musik`: drone_moll, drone_dunkel, drone_stahl.

## 4. Aussprache – IMMER vor dem Rendern (gelernt aus Feedback „unsaubere Aussprache“)
Stimme: **Coqui VITS „Thorsten“** (lokal, 22 kHz, auf ~108 Hz abgesenkt). Phoneme kommen aus `pipeline/g2p_de.py`:
eigenes Lexikon > gruut (nur wenn es mit espeak-ng übereinstimmt) > espeak-ng.
Bekannte Fehlerquellen, die behoben sind und nie wieder auftreten dürfen:
- gruut-Wörterbuch hat kaputte Einträge (Speere=/ʃpəɐə/, Schnee=/ʃnəə/, Feldherr ohne h, „-weit“=/vəiːt/, Endungen „-en“=/ŋ/).
- gruut liefert „ç“ zerlegt (c + Cedille) → Modell hörte „ic“ statt „ich“ → NFC-Normalisierung.
- „ß“/„ss“ wird bei gruut zu /sz/ → solche Wörter immer über espeak.
- Lateinische Namen: „-us“ = /ʊs/ (Varus /vaːʁʊs/), „-ius“ = /iʊs/ (Arminius); Fremdwörter/Orte (Pompeji /pɔmpeːjiː/, Titanic /tiːtaːnɪk/) gehören ins Lexikon.

Ablauf:
```bash
npm run aussprache -- scripts/<id>.json
```
- Zeilen mit `PRÜFEN` = Wort steht in keinem Wörterbuch (Namen, Fremdwörter, seltene Komposita). Jede Zeile lesen:
  - Phoneme korrekt → Wort in `pipeline/aussprache.json` unter `"geprueft"` eintragen.
  - Falsch → unter `"woerter"` korrigieren. Notation (Modell-Alphabet): ei=`a eː`, au=`a oː`, eu/äu=`ɔ ɔʏ`, -er=`ɐ`,
    ch=`ç` (nach e/i/ä/ü/ö/Konsonant) bzw. `x` (nach a/o/u), sch=`ʃ`, z=`t s`, st/sp am Wortanfang=`ʃ t`/`ʃ p`, langes i=`iː`, ä=`ɛ`/`ɛː`.
- Ein Wort, das in mehreren Videos vorkommt, nur einmal eintragen – das Lexikon wächst und wird immer besser.
- Die Automatisierung baut mit `--strict`: offene `PRÜFEN`-Wörter brechen den Build ab.
- Ohne Hören prüfen: Phoneme lesen, Silben zählen, Betonung egal (Modell ohne Betonungszeichen).
- Nach dem Render: `assets/<id>/words.json` → `warnings` muss leer sein (sonst Wortzeiten geschätzt).

## 5. Visuelle Regeln
- 1080×1920, 30 fps. Stil „animiertes Gemälde“: Silhouetten-Ebenen (SVG) + Partikel (Canvas) + Licht + Kamerafahrt.
- **Ich-Figur** = Silhouette mit **Rim-Light in der Akzentfarbe** (`rimmed(...)` in `figures.mjs`) – in jeder Szene, in der sie vorkommt.
- **Jede Epoche eigene Palette** (`pipeline/lib/palettes.mjs`). Neue Epoche → neuen Eintrag anlegen (Farben deutlich anders als bestehende).
- **Jedes Video sichtbar anders**: eigene Motive, eigene Partikel-Kombination, eigene Kamerabewegungen. Motive aus anderen Epochen nicht 1:1 wiederverwenden.
- Safe-Zone: Untertitel auf ~60–70 % Höhe (fest im Generator), oben 168 px und rechts ~150 px frei halten; keine Schrift im unteren Fünftel.

### Neue Motive bauen (`pipeline/lib/motifs/<epoche>.mjs`, im `index.mjs` registrieren)
Ein Motiv ist `function(ctx) -> { layers, lights, fxBack, fxFront, camera, … }`:
- `layers`: `[{ name, depth (0 hinten … 1 vorn), svg }]` – Kamera-Raum 1260×2240 (Bildausschnitt ≈ x 90–1170, y 160–2080).
  Bausteine: `svg.mjs` (treeline, trunk, hills, ferns, rect, path, g) und `figures.mjs` (person, legionary, bustProfile, bustCivil, …).
- `lights`: `[{ x, y, r, color, intensity, flicker, fast }]` (Glühen, flackernd).
- `fxBack` / `fxFront`: Partikel `regen | nebel | asche | steine | schnee | funken | staub | rauch | tropfen | gischt` (Parameter siehe `runtime.js`), optional `ramp: [t0, t1, von, bis]`.
- `camera: { from:{scale,x,y}, to:{scale,x,y}, ease }`, `shake` (+ `shakeFrom`), `march: { name, dx }`.
- `objects` (+ `anims` mit GSAP-Zeilen auf `#${sid}-<name>`, optional `before: "<ebene>"`), `spears`, `labels` (Namen einblenden).
- `events: [{ dt, typ }]` → Soundeffekte (`boom, whoosh, riser, speer, glocke, kratzen, beben, einbruch, steine`).
- `ctx.satz(i)` = Startzeit von Satz i relativ zur Szene → Effekte genau auf das gesprochene Wort legen.
- Deterministisch bleiben: nur `ctx.r()` als Zufall, keine Zeitfunktionen.

## 6. Bauen, prüfen, rendern
```bash
npm run build -- <id> --no-render --strict   # Stimme, Plan, Komposition, Audio, Lint
cd compositions/<id> && ../../node_modules/.bin/hyperframes snapshot --at 1,5,10,…   # Bilder ansehen!
npm run build -- <id> --strict                # rendern (≈ 8 min pro 40 s)
npm run batch -- --strict                     # alle Skripte ohne fertiges MP4
```
Snapshot-Checkliste: Hook ab Frame 0 lesbar · Ich-Figur erkennbar · Motiv klar zu erkennen (nicht zu dunkel) ·
Untertitel nicht über wichtigen Details · keine Objekte vor falscher Ebene · Wendepunkt sichtbar dynamischer · Endkarte.
Fertig-Kriterien: Lint 0 Fehler · Dauer 25–40 s (bzw. > 60 s) · Lautheit −14 ± 1 LUFS (Build gibt sie aus) · Upload-Text vorhanden.

## 7. Abschluss einer Produktion
- `ideen/backlog.json` aktualisieren, `git add -A && git commit` (MP4s sind in `.gitignore`), pushen.
- Die MP4s dem Nutzer schicken (SendUserFile) mit Bildunterschrift + Hashtags aus `output/<id>_upload.txt`.
- Erinnerung im Bericht: **KI-Label beim Upload aktivieren**.
