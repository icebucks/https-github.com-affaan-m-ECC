# By The Numbers – Kanal-Handbuch

Englischsprachiger Kanal für animierte Vergleiche: Zahlen, Größen und Zeit, ohne Sprecher. Dunkles Navy, Gold als Akzent, Poppins und Inter.
Läuft auf TikTok und YouTube Shorts. Jedes Video hat eine eigene Recherche oder eigene Mathematik (keine Massenware, wegen der YouTube-Regeln zu „inauthentic content“).

## Werkzeuge
- `../../beyondexcuses/lib.py`: Rendering (skia), Text, `series_overlay` (Hook, Label, Folgen-Aufruf), `finish_v2` (Video + Ton + Mux), `stills`, `figure` (Menschen-Maßstab).
- `dlib.py`: `flag(c, "us", x, y, w)` zeichnet Länderflaggen (lipis/flag-icons, MIT; fehlende Flaggen werden automatisch von jsdelivr geladen und in `assets/flags` gespeichert). `sfx(t, id, gain_db)` erzeugt ein Sound-Ereignis.
- `dsound.py`: eigene Musik aus `sound.py` + CC0-Soundeffekte aus `assets/sfx` (wyzowl/sfx-kit), punktgenau auf ihren Sync-Punkt gelegt, −14 LUFS. Wird über `dlib` automatisch benutzt.
- Verfügbare Sounds: `assets/sfx/sounds.json` (Felder `use_for`, `avoid_for`, `sync`). Wichtig sind `data-countup-*`, `data-number-land`, `data-bar-grow`, `data-chart-reveal`, `riser-*`, `cinematic-drum-big`, `cinematic-slam-big`, `whoosh-*`, `pop-*`, `shimmer-*`, `money-*`, `tone-step-1…5`, `time-clock*`, `celebration-*`.

## Hook-Regeln (Pflicht, jedes Video)
Ziel: In den ersten 1–2 Sekunden darf niemand weiterwischen, und es braucht einen Grund, bis zum Ende zu schauen.
Umsetzung mit `dlib.finish_data(...)` (Rendern) und `dlib.preview(...)` (Kontaktblatt) statt `finish_v2`/`series_overlay`:
1. **Kein ruhiger Start:** Ab Frame 0 bewegt sich etwas (Zähler läuft, Kamera fährt, Objekt springt ins Bild). Dazu kommen automatisch ein Blitz und ein Bass-Schlag. Keine leere Bildhälfte in den ersten 3 s, sonst ein großes „Hero“-Element dort (siehe `hero()` in `bn1.py`).
2. **Hook-Text = Neugier-Lücke**, 2 Zeilen, Zeile 1 max. ca. 30 Zeichen, ein Schlüsselwort in *Sternchen* (wird gold):
   - Rate-Hook: „Guess how tall *#1* is“ / „before it's revealed!“
   - Schock-Hook: „How long to earn *$1 BILLION*?“ / „The last one is *insane*.“
   - Widerspruch: „Everyone gets *#1* wrong“ / „Do you?“
   Nie die Antwort im Hook verraten.
3. **Grund zum Bleiben:** `sticky` (z. B. „WAIT FOR #1“) und Fortschrittsbalken (`step_fn`, `steps`) einschalten. Die stärkste Zahl kommt zuletzt.
4. **Wucht:** Jede Zahl, die landet, mit `punch()` aufspringen lassen und mit dem Sound `data-number-land` unterlegen. Höhepunkt mit `riser-*` davor, dann `cinematic-drum-big` + `shake()` + kurzer Blitz + `burst()`.
5. **Tempo:** Alle 0,8–2,5 s passiert etwas Neues. Keine Pause über 1,5 s.
6. **Loop:** Wenn möglich endet das Video im Bild des Anfangs (siehe `LOOP` in `bn2.py`). Dann schauen viele es ein zweites Mal.
7. **Kommentar-Köder:** Der Abschlusstext endet mit einer Frage an die Zuschauer („Where would your city rank?“, „What's your number?“).

## Musik & Timing (Pflicht)
- Eigene Musik aus `music.py` über das Ereignis `dlib.music(style, bpm, build, drop, outro, seed)`. Stile: `trap` (140–150), `synthwave` (120–140), `upbeat` (115–125), `lofi` (80–90), `cinematic` (90–105).
- **Rotation:** Stil nie gleich wie in einer der beiden letzten Folgen. Stil, Tempo und Seed in die Tabelle in `plan.md` (Spalte „Musik“) eintragen. Passend zum Thema wählen (Geld → trap, Städte/Technik/Weltall → synthwave, Tiere/Natur → upbeat oder lofi, Rekorde/Geschichte/Größe → cinematic).
- **Alles sitzt auf dem Beat:** `set_bpm(BPM)`, Zeiten mit `beats(n)` setzen. Neue Elemente kommen alle 2–6 Beats, Zahlen landen auf einem Beat.
- **Dramaturgie:** `build` = Beginn des Höhepunkts (Drums fallen weg, Snare-Wirbel), `drop` = Moment, in dem die stärkste Zahl landet (Trommelschlag, `shake`, Blitz), `outro` = Abschlusstext. Den Drop möglichst auf einen Taktanfang legen (Vielfaches von `beats(4)`).
- Licht und Glow mit `pulse(t)` auf den Beat pulsieren lassen.
- Titelbild: `dlib.cover(frame, t, [(Zeile, Größe), …], "Cover_BN<N>.jpg", N)` mit einem Bild vom Höhepunkt, 2–3 Zeilen, ein *goldenes* Wort.

## Hashtags (Formel, immer genau 5)
`#bythenumbers` + 2 Nischen-Tags + 2 Themen-Tags. Kein #fyp, #viral oder #foryou (laut den meisten Analysen fast wirkungslos, sie verwässern die Einordnung).
- **Marke (immer):** `#bythenumbers`, damit die Serie unter einem eigenen Tag sammelt.
- **Nische (2 aus):** `#facts` `#didyouknow` `#learnontiktok` `#comparison` `#datavisualization`. Zum Format passend wählen: Ranking/Vergleich → `#comparison`, Zahlen/Grafik → `#datavisualization`, Wissen → `#didyouknow` oder `#learnontiktok`.
- **Thema (2):** konkret und suchbar, siehe Tabelle in `plan.md` (z. B. `#skyscraper #burjkhalifa`, `#money #billionaire`, `#geography #flags`, `#space #planets`, `#animals #wildlife`).
- Die Hashtags müssen zu den Wörtern in Caption und Bildtext passen. Das Hauptsuchwort steht vorne in der Caption UND einmal groß im Video.
- Nie `#` vor Zahlen schreiben („#1“, „#10“): TikTok und YouTube machen daraus Hashtags. Stattdessen „No. 1“.
- YouTube: dieselben Tags am Ende der Beschreibung, `#shorts` statt `#learnontiktok`. Die ersten 3 erscheinen über dem Titel, deshalb `#bythenumbers` zuerst.

## YouTube-Skill-Workflow (Pflicht, `.claude/skills/yt-*`, MIT, Jake Schincariol)
0. Vorher `mkdir -p ~/.claude/youtube && cp kanaele/youtube/voice_bythenumbers.md ~/.claude/youtube/voice.md` – alle yt-Skills lesen dieses Stimm-Profil.
1. **Hook (`/yt-script`):** 5 Hook-Varianten aus mindestens 3 verschiedenen Formeln in `.claude/skills/yt-script/hooks.json` schreiben (nicht immer „The Question“!), alle mit `python3 .claude/skills/yt-script/hookscore.py hooks.txt` bewerten. Die beste EHRLICHE nehmen: Ziel ≥ 55 (WORKABLE), besser ≥ 72 (STRONG). Hebel laut Werkzeug: „you“ in den ersten 6 Wörtern, eine konkrete Zahl, was auf dem Spiel steht (lose, cost, never, before …), ein offenes Fragewort, 9–24 Wörter, nicht selbst beantworten. Nie Zahlen oder Behauptungen erfinden. Auf dem Bildschirm in 2 kurze Zeilen teilen.
2. **Titel + Titelbild (`/yt-package`):** 10 YouTube-Titel schreiben, alle mit `python3 .claude/skills/yt-package/title.py titles.txt` prüfen, den besten nehmen (Ziel ≥ 90). Hauptsuchwort vorne (z. B. „Tallest buildings in the world, to scale (2026)“), kein „insane/crazy“, höchstens 2 Wörter in Großbuchstaben. Titelbild: höchstens 3 Wörter, andere Wörter als der Titel (gleiches Versprechen), am besten eine Zahl. Paar mit `title.py --title "…" --thumb "…"` prüfen; die Titelbild-Wörter kommen ins Cover.
3. **Suche (`/yt-seo`):** die 3 Suchanfragen aufschreiben, die das Video gewinnen soll. Titel und die ERSTEN ZWEI Zeilen der Beschreibung müssen deren Wörter enthalten. Tags sind unwichtig.
4. **Kommentare (`/yt-comment`):** Wenn die Person Kommentare schickt: in Fragen / Korrekturen / Lob / Köder sortieren, Antworten unter 30 Wörtern, EINEN Kommentar zum Anpinnen empfehlen (die Frage, die die meisten haben). Fragen = Themen für nächste Folgen.
5. **Retention (`/yt-retention`):** Exportierte Retention-CSV aus YouTube Studio (Video → Analytics → Engagement → Download) in `kanaele/data/analytics/` legen und mit `python3 .claude/skills/yt-retention/retention.py <csv> --duration <s>` auswerten. Größtes Leck zuerst.
6. **Konkurrenz (`/yt-viral`):** `python3 kanaele/youtube/viral_collect.py out.json "<suchbegriff>" …` und `python3 .claude/skills/yt-viral/swipe.py out.json --min 2.0`. Gewertet wird das Vielfache des eigenen Kanal-Medians, nicht die Rohaufrufe. Nur öffentliche Listen.

## Formate (abwechseln, nie zweimal hintereinander dasselbe)
| Format | Vorlage | Idee |
|---|---|---|
| A · Zählerkarten | `bn1.py` | 4–6 Karten, Zähler laufen hoch, Logarithmus-Balken; die letzte Karte ist die Pointe |
| B · Maßstabs-Zoom | `bn2.py` | Kamera startet beim Menschen und zoomt Objekt für Objekt heraus; Flaggen, Höhenzähler, Gesamtansicht am Ende |
| C · Ranking-Countdown | neu | Platz 10 → 1 mit Flaggen und Balken, Riser vor Platz 1, damit bis zum Ende geschaut wird |
| D · Duell | neu | zwei Dinge im direkten Vergleich (Länder, Tiere, Planeten), 3–4 Runden, Punktestand |
| E · Zeitvergleich | neu | eine Uhr oder Zeitleiste: „Was passiert in 1 Sekunde / 1 Minute weltweit“, „Wie lange dauert …“ |

## Regeln
- 1080×1920, 30 fps, 15–18 s (Kurzversion). −14 LUFS. Nur Englisch, kein Sprecher.
- Hook nach den Hook-Regeln oben (`finish_data`). Die stärkste Zahl kommt zuletzt. „Follow for part N+1“ kommt automatisch am Ende.
- Sicherheitszonen (gemessen mit `audit.py`, vorsichtige Werte aus TikToks Safe-Zone-Vorlage):
  - Oben: unter y 210 nur Deko, keine Info.
  - Rechts: wichtige Texte und Zahlen enden bei x 880 (y 760–1660 = Button-Spalte).
  - Unten: ab y 1450 liegen Caption, Benutzername und Sound. Dort nichts Wichtiges. Abschlusstext mit `dlib.end_card(..., y=1110)` oder höher, NIE `end_text` (lag unter der Caption).
- Erste Sekunde hell und farbig (Audit: Helligkeit ≥ 60/255, Farbigkeit ≥ 30). Hintergründe in Indigo, Violett und Dämmerung statt Fast-Schwarz.
- Schrift mindestens 28 px.
- Nach dem Rendern `python3 audit.py BN<N>_..._EN.mp4` ausführen. Alle ⚠️ beheben (Ausnahme: dekorative Partikel unter den Top-Tabs) und erneut rendern.
- **Jede Zahl prüfen:** mit WebSearch aus einer verlässlichen Quelle (Wikipedia, Weltbank, UN, NASA, statistische Ämter, Hersteller). Lieber exakte Mathematik als Schätzungen. Quelle und Stand (Monat/Jahr) gehören in die YouTube-Beschreibung. Keine Zahl erfinden. Ist etwas unklar, ein anderes Thema wählen.
- Keine politischen, religiösen oder tragischen Themen (Kriege, Katastrophen, Todeszahlen). Keine Markenlogos.
- Ablauf: `bnN.py` schreiben → `python3 bnN.py still` (nutzt `dlib.preview`, Bilder bei 0,05 s, 0,5 s, 2 s und über das ganze Video) ansehen → Überschneidungen mit Hook, Sticky-Chip und Fortschrittsbalken (y 200–560) beheben → `VID_LANG=en python3 bnN.py render` → Dauer und LUFS messen, Kontaktblatt aus der MP4 mit 1 Bild pro Sekunde ansehen.

## Themen-Backlog (oben = als Nächstes)
**Ab 16.11.2026: keine Weltall-Themen mehr in dieser Reihe.** Weltall läuft als eigene Short-Reihe mit Sprecher (`../space/shorts/SHORTS.md`), und die langen Videos (`../space/LONGFORM.md`) haben Vorrang. Vor jedem neuen Thema prüfen: `python3 ../space/overlap.py bnN.py` muss ohne Treffer durchlaufen.
1. **C** · Largest countries by area – Top 10 mit Flaggen (Wikipedia, km²) – ⚠️ Platz 3/4 USA vs. China je nach Quelle umstritten (9,83 vs. 9,37/9,53 Mio. km²); nur mit klarer Definition (Landfläche) oder als Top 10 ohne die beiden bauen
2. ~~**E** · How long would it take to walk around the Earth?~~ → erledigt als BN3
3. **B** · Animals to scale: from an ant to the blue whale (Längen aus Wikipedia)
5. **A** · How much is $1 million in different currencies? (Wechselkurse mit Datum)
6. **C** · Most visited countries by tourists (UN Tourism, neuestes Jahr)
7. **B** · Deepest places on Earth: from a swimming pool to the Mariana Trench
8. **E** · What happens on the internet in one minute (nur mit aktueller, belegter Quelle)
9. **D** · Your heart vs. a whale's heart: beats, weight, size
10. **C** · Longest rivers in the world (Wikipedia, km)
12. **A** · How long to count to 1 million / 1 billion (1 Zahl pro Sekunde, exakte Mathematik)
13. **C** · Highest mountains – the Seven Summits with flags
15. **D** · Cheetah vs. Usain Bolt vs. car: 100 m

Wenn weniger als 5 Themen übrig sind: 5 neue im selben Stil ergänzen.
