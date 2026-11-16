# By The Numbers – Kanal-Handbuch

Englischsprachiger Kanal für animierte Vergleiche: Zahlen, Größen und Zeit, ohne Sprecher. Dunkles Navy, Gold als Akzent, Poppins und Inter.
Läuft auf TikTok und YouTube Shorts. Jedes Video hat eine eigene Recherche oder eigene Mathematik (keine Massenware, wegen der YouTube-Regeln zu „inauthentic content“).

## Werkzeuge
- `../../beyondexcuses/lib.py`: Rendering (skia), Text, `series_overlay` (Hook, Label, Folgen-Aufruf), `finish_v2` (Video + Ton + Mux), `stills`, `figure` (Menschen-Maßstab).
- `dlib.py`: `flag(c, "us", x, y, w)` zeichnet Länderflaggen (lipis/flag-icons, MIT; fehlende Flaggen werden automatisch von jsdelivr geladen und in `assets/flags` gespeichert). `sfx(t, id, gain_db)` erzeugt ein Sound-Ereignis.
- `dsound.py`: eigene Musik aus `sound.py` + CC0-Soundeffekte aus `assets/sfx` (wyzowl/sfx-kit), punktgenau auf ihren Sync-Punkt gelegt, −14 LUFS. Wird über `dlib` automatisch benutzt.
- Verfügbare Sounds: `assets/sfx/sounds.json` (Felder `use_for`, `avoid_for`, `sync`). Wichtig sind `data-countup-*`, `data-number-land`, `data-bar-grow`, `data-chart-reveal`, `riser-*`, `cinematic-drum-big`, `cinematic-slam-big`, `whoosh-*`, `pop-*`, `shimmer-*`, `money-*`, `tone-step-1…5`, `time-clock*`, `celebration-*`.

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
- Hook-Frage ab 0 s (`finish_v2`, series="BY THE NUMBERS"). Die stärkste Zahl kommt zuletzt. „Follow for part N+1“ am Ende.
- Sicherheitszonen: nichts unter y 1600, nichts bei x ≥ 950 zwischen y 900 und 1500, nichts über y 150.
- **Jede Zahl prüfen:** mit WebSearch aus einer verlässlichen Quelle (Wikipedia, Weltbank, UN, NASA, statistische Ämter, Hersteller). Lieber exakte Mathematik als Schätzungen. Quelle und Stand (Monat/Jahr) gehören in die YouTube-Beschreibung. Keine Zahl erfinden. Ist etwas unklar, ein anderes Thema wählen.
- Keine politischen, religiösen oder tragischen Themen (Kriege, Katastrophen, Todeszahlen). Keine Markenlogos.
- Ablauf: `bnN.py` schreiben → `stills()` mit `series_overlay` ansehen → Überschneidungen beheben → `VID_LANG=en python3 bnN.py render` → Dauer und LUFS messen, Kontaktblatt aus der MP4 mit 1 Bild pro Sekunde ansehen.

## Themen-Backlog (oben = als Nächstes)
1. **C** · Largest countries by area – Top 10 mit Flaggen (Wikipedia, km²)
2. **E** · How long would it take to walk around the Earth? (Umfang 40.075 km, 5 km/h, 8 h pro Tag)
3. **B** · Animals to scale: from an ant to the blue whale (Längen aus Wikipedia)
4. **D** · Sun vs. Earth vs. Moon – size, mass, distance (NASA Fact Sheets)
5. **A** · How much is $1 million in different currencies? (Wechselkurse mit Datum)
6. **C** · Most visited countries by tourists (UN Tourism, neuestes Jahr)
7. **B** · Deepest places on Earth: from a swimming pool to the Mariana Trench
8. **E** · What happens on the internet in one minute (nur mit aktueller, belegter Quelle)
9. **D** · Your heart vs. a whale's heart: beats, weight, size
10. **C** · Longest rivers in the world (Wikipedia, km)
11. **B** · Planets to scale, ending with the Sun
12. **A** · How long to count to 1 million / 1 billion (1 Zahl pro Sekunde, exakte Mathematik)
13. **C** · Highest mountains – the Seven Summits with flags
14. **E** · Light speed: how long light takes to the Moon, Sun, Mars (NASA)
15. **D** · Cheetah vs. Usain Bolt vs. car: 100 m

Wenn weniger als 5 Themen übrig sind: 5 neue im selben Stil ergänzen.
