# By The Numbers · SPACE – tägliche Shorts mit Sprecher (George)

Zweite tägliche Short-Reihe auf **By The Numbers**, neben den Daten-Shorts ohne Sprecher (`kanaele/data`). Englisch, 1080×1920, 30–42 s, Sprecher Kokoro `bm_george` (Apache-2.0, lokal, kostenlos), Untertitel Wort für Wort, eigene Musik (`music.py`) + CC0-Effekte, −14 LUFS. KI-Label beim Upload aktivieren (synthetische Stimme).

Bauen: `python3 shorts/ssN.py still` (Kontaktblatt ansehen) → `python3 shorts/ssN.py render` → `python3 shorts/ssN.py cover`.
Engine: `vshort.py` (Layout, Kamera, Hook, Untertitel, Ton) · Stimme + Wortzeiten: `voice.py` · Sperrliste: `reserved.json` + `overlap.py`.

## Regel 1 – keine Überschneidung mit den langen Videos (Pflicht)
- Die langen Videos (`../LONGFORM.md`) haben Vorrang. Jede Frage aus dem Long-Backlog ist für Shorts **gesperrt**: Shorts beantworten sie nicht, verwenden ihre Zahlen nicht und zeigen nicht dieselben Vergleiche.
- Die Sperre ist automatisch: `vshort.main()` ruft `overlap.check()` auf und bricht ab, wenn ein Short ein Suchmuster aus `reserved.json` trifft. Von Hand prüfen: `python3 overlap.py shorts/ssN.py`.
- Kommt ein neues langes Video in den Backlog → **zuerst** ein Eintrag in `reserved.json` (Thema + Suchmuster), dann erst der nächste Short.
- Ein Short darf auf ein langes Video nur über YouTubes Funktion „Ähnliches Video“ und im Pin-Kommentar verweisen – nie inhaltlich.
- Weltall-Themen gehören ab jetzt dieser Reihe. Die Daten-Shorts ohne Sprecher machen Erde, Geld, Länder, Tiere, Gebäude (siehe `../../data/README.md`).

## Regel 2 – jeder Short anders (Abwechslung)
Vor jedem neuen Short die letzten 3 Zeilen der Tabelle unten lesen. Der neue Short muss sich bei **Format, Musikstil, Farbton (tint) und Hook-Formel** von der direkt vorherigen Folge unterscheiden; Format und Musikstil dürfen sich frühestens nach 2 anderen Folgen wiederholen. Kein Fakt, keine Zahl darf in zwei Shorts der Reihe vorkommen (Spalte „Kernzahlen“ prüfen).

**Formate** (jedes Format hat eigene Szenen-Funktionen in der Episode, gemeinsame Bausteine in `vshort.py`):
| Kürzel | Format | Aufbau |
|---|---|---|
| FILL | Wie oft passt X in Y? | Füll-/Reihen-Animation, Zähler, Überraschung zum Schluss |
| RANK | Top 5, Stärkstes zuletzt | Countdown 5→1, Balken/Kugeln wachsen, Sticky „wait for No. 1“ im Text |
| VS | Duell in 3 Runden | zwei Objekte nebeneinander, 3 Zahlen, Sieger-Burst |
| YOU | Du an einem anderen Ort | Figur/Waage/Uhr mit „du“-Werten, Zuschauer rechnet mit |
| WHAT IF | Gedankenexperiment mit echten Zahlen | Szenario Schritt für Schritt, Wendepunkt in der Mitte |
| ZOOM | Maßstabs-Zoom | Kamera fährt von klein nach riesig (oder umgekehrt), Größe pro Stufe |

**Musikstile** rotieren: cinematic, synthwave, lofi, trap, upbeat (BPM passend: lofi 80–90, cinematic 90–105, synthwave 100–120, upbeat 110–124, trap 140–150 halbtaktig). **Farbton (tint)** rotiert: warm (70,36,30) · violett (50,30,90) · blau (24,40,96) · grün-türkis (20,70,70) · rot (90,24,40).

## Hook und Aufbau (je Short)
- 5 Hook-Varianten aus ≥ 3 Formeln (`.claude/skills/yt-script/hooks.json`), mit `hookscore.py` bewerten, die beste ehrliche nehmen (Ziel ≥ 72). Gesprochener Hook ≤ 24 Wörter, Bildschirm-Hook in 2 kurzen Zeilen mit *goldenen* Wörtern.
- 5–7 Beats à 4–8 s. Jeder Beat bekommt eine Kopfzeile (`head`) mit der Zahl in Gold – stumm schauende Zuschauer verstehen alles.
- Wendepunkt („Now the weird part …“) mit `drop=True` etwa in der Mitte: Trommelschlag, Blitz, Shake, Musik-Drop.
- Letzter Beat = Frage an die Zuschauer, End-Karte mit 2 weißen + 1 goldenen Zeile (Kommentar-Köder). Antwort in den Pin-Kommentar, die Auflösung darf Thema eines späteren Shorts sein (Fortsetzung = Grund zum Folgen).
- Zahlen im Sprechtext mit `{Anzeige|gesprochen}` schreiben: `{1.3 million|one point three million}`. Untertitel zeigen Ziffern, George spricht Wörter.
- Länge 30–42 s (Sprechtempo `speed` 1.0–1.06).

## Sicherheitszonen (wie `../../data/audit.py`)
y < 210 nichts · Tag y 238 · Hook/Kopfzeile y 300–520 · Bühne y 560–1180 · Untertitel y ≈ 1330 · ab y 1450 nichts Wichtiges · wichtige Texte enden bei x 880 (y 760–1660). Nach dem Rendern: `python3 ../data/audit.py shorts/SSN_..._EN.mp4`.

## Fakten
Jede Zahl mit WebSearch aus NASA / ESA / JPL / IAU-Quellen prüfen, Quelle und Stand in den Kopf der Episodendatei schreiben. Volumen-Vergleiche ehrlich formulieren („fill the volume“, nicht „pack inside“). Unsichere oder umstrittene Werte (größter Stern, Diamantenregen …) nicht verwenden.

## Uploadzeiten (deutsche Zeit) – mind. 3 h Abstand zu den Daten-Shorts
| Tag | TikTok | YouTube Shorts |
|---|---|---|
| Mo–Fr | 17:00 | 16:30 |
| Sa | 13:00 | 12:30 |
| So | 19:00 | 19:30 |

Samstag 17:30 kommt das lange Video – den Samstags-Short in YouTube Studio per „Ähnliches Video“ mit dem neuesten langen Video verknüpfen.

## Hashtags
TikTok genau 5: `#bythenumbers #space #astronomy` + 2 Thema (z. B. `#sun #solarsystem`). Kein #fyp, nie „#“ vor Zahlen. YouTube: dieselben am Ende der Beschreibung, `#shorts` zuletzt.

## Folgen
| # | Datum | Thema | Format | Musik | tint | Hook-Formel (Score) | Kernzahlen | Datei |
|---|---|---|---|---|---|---|---|---|
| 1 | Di 17.11. | How many Earths fit in the Sun? | FILL | cinematic 100 | warm | Contrarian Flip (73) | 1.3 Mio Erden (Volumen), 109 Erden breit, ~10 Jupiter breit, 1.000 Erden in Jupiter, 99,8 % Masse | `ss1.py` → `SS1_SunEarths_EN.mp4` |

## Themen-Backlog (oben = als Nächstes; vor dem Bauen gegen `reserved.json` prüfen)
1. **FILL** · How many Moons would fill the Earth? – Auflösung der Frage aus #1 (≈ 49, NASA Fact Sheets: Volumen 108,321 vs 2,1958 × 10¹⁰ km³), Einstieg „Yesterday you guessed …“
2. **VS** · Olympus Mons vs. Mount Everest (Höhe, Fläche, Vulkan) – NASA Mars
3. **YOU** · What would you weigh on every planet? – NASA Planetary Fact Sheet (Oberflächen-Schwerkraft)
4. **RANK** · The 5 biggest moons in the Solar System – Ganymede größer als Merkur (NASA)
5. **WHAT IF** · Saturn would float in water – Dichte 0,687 g/cm³ (NASA)
6. **ZOOM** · A teaspoon of neutron star – Masse aus NASA-Quelle, Vergleich mit Bergen/Gebäuden
7. **VS** · The Great Red Spot vs. Earth – aktuelle Breite (NASA/Hubble, Jahr angeben), schrumpft
8. **RANK** · Planets by number of moons – IAU/NASA-Zählung mit Datum (Saturn vorn)
9. **YOU** · Astronauts on the ISS see 16 sunrises a day – NASA (Umläufe pro Tag)
10. **FILL** · Valles Marineris vs. the width of the USA – NASA (≈ 4.000 km)
11. **WHAT IF** · The Moon drifts away 3.8 cm per year – NASA/Lunar Laser Ranging, Vergleich Fingernagel
12. **VS** · Pluto vs. the United States – Durchmesser 2.377 km (NASA)
13. **RANK** · Only 12 people have walked on the Moon – Namen/Jahre (NASA)
14. **ZOOM** · Planets to scale, ending with the Sun (aus dem Daten-Backlog übernommen; keine Werte aus #1 wiederholen – Schwerpunkt Uranus/Neptun/Erde)
15. **WHAT IF** · A plane flight around every planet – Umfang ÷ 900 km/h (NASA Fact Sheets; nur *um* den Planeten, nie *zu* ihm)
16. **FILL** · Saturn's rings: 280,000 km wide, about 10 m thick – NASA; „thinner than paper“-Vergleich
17. **RANK** · Space junk: tracked objects in orbit – ESA Space Environment Report (neuestes Jahr)
18. **ZOOM** · Sagittarius A*: our black hole's mass and size – EHT/NASA

Sind weniger als 6 Themen übrig: 6 neue ergänzen (gleiche Regeln, gegen `reserved.json` prüfen).

---

## SS1 Upload – Di 17.11. · TikTok 17:00 · YouTube 16:30
Datei `SS1_SunEarths_EN.mp4` (40,9 s, −14,3 LUFS, Audit: keine Überschneidung mit der TikTok-Oberfläche, Loop nahtlos), Titelbild `Cover_SS1.jpg`. Hook 73/100 STRONG. Überschneidungs-Check mit den langen Videos: OK.

**TikTok-Caption**
> How many Earths fit inside the Sun? 1.3 million – and that's not even the weird part ☀️🌍
> Guess: how many Moons would fill the Earth? 👇
> #bythenumbers #space #astronomy #sun #solarsystem

**Pin-Kommentar:** About 49 Moons would fill the Earth (by volume). Who guessed closest? 🌕

**YouTube-Titel (title.py 98/100):** Sun vs Earth size comparison: 109 Earths across
**Titelbild-Text:** 1.3 MILLION / INSIDE

**YouTube-Beschreibung**
> How many Earths fit inside the Sun? About 1.3 million would fill its volume – a Sun vs Earth size comparison you can see.
> How big is the Sun compared to Earth and Jupiter, and why it holds 99.8% of the Solar System's mass.
>
> 1.3 million Earths fill the Sun's volume · 109 Earths across its face · about 10 Jupiters across · ~1,000 Earths fit inside Jupiter · the Sun holds 99.8% of all mass in the Solar System.
> Sources: NASA Science – Sun Facts; NASA Science – Jupiter Facts; NASA Planetary Fact Sheets (checked 16 Nov 2026). Narration: synthetic voice.
>
> #bythenumbers #space #astronomy #sun #solarsystem #shorts

Suchanfragen: „how many earths fit in the sun“, „sun vs earth size comparison“, „how big is the sun“.
