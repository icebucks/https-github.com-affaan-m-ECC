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
Zeilen nach Nummer sortiert. Nächster Uploadtermin = Tag nach dem **spätesten** Datum in der Tabelle.
| # | Datum | Thema | Format | Musik | tint | Hook-Formel (Score) | Kernzahlen | Datei |
|---|---|---|---|---|---|---|---|---|
| 1 | Di 17.11. | How many Earths fit in the Sun? | FILL | cinematic 100 | warm | Contrarian Flip (73) | 1.3 Mio Erden (Volumen), 109 Erden breit, ~10 Jupiter breit, 1.000 Erden in Jupiter, 99,8 % Masse | `ss1.py` → `SS1_SunEarths_EN.mp4` |
| 2 | Mo 16.11. (vorgezogen, heute Nacht) | The 5 biggest moons in the Solar System | RANK | synthwave 112 | blau | The Question (76) | Durchmesser Ganymed 5.268, Titan 5.150, Kallisto 4.821, Io 3.643, Mond 3.475 km; Merkur 4.879 km | `ss2.py` → `SS2_BiggestMoons_EN.mp4` |
| 3 | Mi 18.11. | Earth vs. the Moon in 3 rounds | VS | trap 144 | grün-türkis | The Comparison (76) | ≈ 49 Monde füllen das Erdvolumen (Verhältnis 0,0203), ≈ 81 Monde = Erdmasse (0,0123), Dichte Mond 3.344 vs. Erde 5.514 kg/m³ (≈ 60 %), Schwerkraft 1,62 vs. 9,80 m/s² (≈ 1/6) → gleicher Wurf ≈ 6× höher | `ss3.py` → `SS3_EarthVsMoon_EN.mp4` |
| 4 | Do 19.11. | Saturn would float in water | WHAT IF | lofi 86 | violett | The Question (82) | Dichte Saturn 0,687 g/cm³ (687 kg/m³) vs. Wasser 1,0 → schwimmt mit 68,7 % unter Wasser, Masse 95 Erden, Volumen ≈ 764 Erden, Durchmesser 120.536 km ≈ 9,4 Erden, einziger Planet leichter als Wasser, v. a. Wasserstoff + Helium | `ss4.py` → `SS4_SaturnFloats_EN.mp4` |
| 5 | Fr 20.11. | A sugar cube of neutron star | ZOOM | cinematic 100 | rot | The Statistic (75) | 1 Zuckerwürfel Neutronenstern ≈ 1 Billion kg (1 Mrd. t) ≈ ein Berg, Neutronenstern ≈ 20 km breit (Größe einer Stadt), ≈ Sonnenmasse, Sonne ≈ 1,4 Mio. km breit → 70.000× schmaler | `ss5.py` → `SS5_NeutronSugarCube_EN.mp4` |

## Themen-Backlog (oben = als Nächstes; vor dem Bauen gegen `reserved.json` prüfen)
2. **VS** · Olympus Mons vs. Mount Everest (Höhe, Fläche, Vulkan) – Achtung: Höhenangaben schwanken je nach Bezugslinie (NASA/ESA ≈ 25 km über der Ebene, andere 21,9–27 km). Nur „about 25 km above the plains around it“ sagen und die Bezugslinie nennen; Fläche „about the size of Arizona“ (NASA-Grafik „How big is it“).
3. **YOU** · What would you weigh on every planet? *(19.11. erneut übersprungen: Jupiter 23,1 vs. 24,79, Saturn 9,0 vs. 10,44 m/s² je nach Quelle) (18.11. übersprungen: Saturn-Wert kippt je nach NASA-Konvention 9,0 vs. 10,44 m/s² – nur ohne Saturn oder mit erklärter Konvention bauen)* – Mond weglassen (≈ 1/6 schon in #3). Achtung: NASA nennt zwei Schwerkraft-Konventionen (Übersichtstabelle mit Rotation, z. B. Jupiter 23,1 / Saturn 9,0 m/s²; Einzelblätter ohne Rotation, 24,79 / 10,44). EINE Quelle durchgehend nehmen und nennen; keine Pointe, die nur in einer Konvention stimmt (z. B. „auf Saturn wiegst du weniger“). Skala unitless: „if your scale shows 100 at home …“.
6. ~~**ZOOM** · A teaspoon of neutron star~~ → erledigt als SS5 (NASA-Zuckerwürfel statt Teelöffel: Teelöffel-Werte schwanken zwischen 10 Mio. und mehreren Mrd. t)
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

---

## SS2 Upload – Mo 16.11. (heute Nacht) · TikTok 22:30 · YouTube 22:00
Datei `SS2_BiggestMoons_EN.mp4` (42,4 s, −14,2 LUFS, Audit: nichts unter der TikTok-Oberfläche, Loop nahtlos), Titelbild `Cover_SS2.jpg`. Hook 76/100 STRONG. Überschneidungs-Check mit den langen Videos: OK.

**TikTok-Caption**
> Biggest moons in the Solar System, ranked 🌕 Our Moon is only No. 5 – and 2 moons beat a whole planet 🤯
> 3 of these 5 orbit the same planet. Which one? 👇
> #bythenumbers #space #astronomy #moons #solarsystem

**Pin-Kommentar:** Jupiter! 🪐 Io, Callisto and Ganymede all orbit Jupiter. Titan orbits Saturn.

**YouTube-Titel (title.py 94/100):** Biggest moons in the Solar System: 2 beat a planet
**Titelbild-Text:** OURS IS / 5TH

**YouTube-Beschreibung**
> The biggest moons in the Solar System, ranked by size: our Moon is only No. 5, and two moons are bigger than the planet Mercury.
> Which moon is the biggest? Ganymede, Titan, Callisto, Io and the Moon compared.
>
> Diameters: Ganymede 5,268 km · Titan 5,150 km · Callisto 4,821 km · Io 3,643 km · Moon 3,475 km · (planet Mercury 4,879 km).
> Sources: NASA JPL Ganymede fact sheet; NASA Science – Titan, Callisto, Io, Moon and Mercury facts (checked 16 Nov 2026). Narration: synthetic voice.
>
> #bythenumbers #space #astronomy #moons #solarsystem #shorts

Suchanfragen: „biggest moons in the solar system“, „which moon is the biggest“, „moons bigger than mercury“.

---

## SS3 Upload – Mi 18.11. · TikTok 17:00 · YouTube 16:30
Datei `SS3_EarthVsMoon_EN.mp4` (41,8 s, −14,2 LUFS, Audit: alles ✅ – nichts unter der TikTok-Oberfläche, keine bewegungsarmen Sekunden, Loop nahtlos), Titelbild `Cover_SS3.jpg`. Hook 76/100 STRONG (The Comparison). Überschneidungs-Check mit den langen Videos: OK.

**TikTok-Caption**
> Earth vs Moon size comparison 🌍🌕 49 Moons fill the Earth – but it takes 81 to match its weight. Why?
> Your guess: how many Mars-size planets would fill the Earth? 👇
> #bythenumbers #space #astronomy #moon #earth

**Pin-Kommentar:** Only about 6.6! Mars has about 15% of Earth's volume (NASA Mars Fact Sheet), so not even 7 Mars-size planets would fill the Earth. Who got closest? 🔴

**YouTube-Titel (title.py 98/100):** Earth vs Moon size comparison: round 2 is weird
**Titelbild-Text:** 81 / NOT 49

**YouTube-Beschreibung**
> Earth vs Moon size comparison in 3 rounds: how many Moons fit in Earth? About 49 fill its volume – but you need 81 to match its weight.
> How big is the Moon compared to Earth, why Moon rock is so light, and how gravity on the Moon changes a simple throw.
>
> About 49 Moons fill Earth's volume · about 81 Moons match Earth's mass · the Moon is about 60% as dense (3,344 vs 5,514 kg/m³) · Moon gravity is about 1/6 of Earth's (1.62 vs 9.80 m/s²), so the same throw goes about 6 times higher.
> Sources: NASA NSSDC Moon Fact Sheet (updated 11 Jan 2024); NASA NSSDC Mars Fact Sheet (updated 19 May 2025) – checked 17 Nov 2026. Narration: synthetic voice.
>
> #bythenumbers #space #astronomy #moon #earth #shorts

Suchanfragen: „earth vs moon size comparison“, „how big is the moon compared to earth“, „how many moons fit in earth“.
Mittwoch – kein Samstags-Hinweis nötig.

---

## SS4 Upload – Do 19.11. · TikTok 17:00 · YouTube 16:30
Datei `SS4_SaturnFloats_EN.mp4` (38,9 s, −14,2 LUFS, Audit: alles ✅ – nichts unter der TikTok-Oberfläche, keine bewegungsarmen Sekunden, Loop nahtlos), Titelbild `Cover_SS4.jpg`. Hook 82/100 STRONG (The Question). Whisper-Transkript geprüft: alle Zahlen richtig gesprochen. Überschneidungs-Check mit den langen Videos: OK.

**TikTok-Caption**
> Would Saturn float in water? It weighs 95 Earths – and it still wouldn't sink 🪐🌊
> Guess: which planet is the densest of all? 👇
> #bythenumbers #space #astronomy #saturn #solarsystem

**Pin-Kommentar:** Earth! 🌍 It's the densest planet in the Solar System – Mercury is a close second (NASA). Saturn is the only one less dense than water. Who got it? 🪐

**YouTube-Titel (title.py 98/100, mit Titelbild 100/100):** Why would Saturn float in water if it weighs 95 Earths?
**Titelbild-Text:** IT / FLOATS

**YouTube-Beschreibung**
> Would Saturn float in water? Saturn's density is only 0.687 g/cm³ – less than water's 1.0 – so in a big enough ocean it would float.
> How big is Saturn compared to Earth: about 9.4 Earths across and 764 Earths of volume, yet only 95 Earths of mass.
>
> Saturn is over 120,000 km wide (120,536 km at the equator) · about 764 Earths would fill its volume · its mass is about 95 Earths · average density 0.687 g/cm³ vs. water 1.0 g/cm³ · the only planet less dense than water, made mostly of hydrogen and helium. A floating object sinks by its density ratio: about 69% of Saturn would sit below the waterline. Hypothetical – no ocean is that big.
> Sources: NASA NSSDC Saturn Fact Sheet (updated 18 Mar 2025); JPL Horizons physical data (Saturn 699); NASA Science – Saturn Facts; NASA Science – Mercury Facts (checked 18 Nov 2026). Narration: synthetic voice.
>
> #bythenumbers #space #astronomy #saturn #solarsystem #shorts

Suchanfragen: „would saturn float in water“, „saturn density“, „how big is saturn compared to earth“.
Donnerstag – kein Samstags-Hinweis nötig.

---

## SS5 Upload – Fr 20.11. · TikTok 17:00 · YouTube 16:30
Datei `SS5_NeutronSugarCube_EN.mp4` (39,2 s, −14,4 LUFS, Audit: alles ✅ – nichts unter der TikTok-Oberfläche, keine bewegungsarmen Sekunden, Loop nahtlos), Titelbild `Cover_SS5.jpg`. Hook 75/100 STRONG (The Statistic). Whisper-Transkript geprüft: alle Zahlen richtig gesprochen. Überschneidungs-Check mit den langen Videos: OK.

**TikTok-Caption**
> Neutron star density: you'd lose any bet against this sugar cube 🧊⚖️ About 1 trillion kg – as much as a mountain
> What's the heaviest thing you've ever lifted? 👇
> #bythenumbers #space #astronomy #neutronstar #stars

**Pin-Kommentar:** Whatever you lifted – one sugar cube of neutron star beats it by about a billion tons (NASA) 😅 What was yours? 🏋️

**YouTube-Titel (title.py 94/100, mit Titelbild 98/100):** How dense is a neutron star? 1 sugar cube = 1 trillion kg
**Titelbild-Text:** ONE / MOUNTAIN

**YouTube-Beschreibung**
> How dense is a neutron star? Neutron star density in one picture: a single sugar cube of it would weigh about 1 trillion kg on Earth.
> The neutron star sugar cube weighs about as much as a mountain – and the whole star packs about the Sun's mass into a ball 20 km across.
>
> One sugar cube of neutron star material ≈ 1 trillion kilograms (1 billion tons) on Earth, about as much as a mountain · a neutron star is about 20 km across – the size of a city – with about the mass of the Sun · the Sun is about 1.4 million km wide, so that's squeezing it about 70,000 times narrower.
> Sources: NASA Goddard – Imagine the Universe: Neutron Stars; NASA Science – Sun Facts (checked 19 Nov 2026). Narration: synthetic voice.
>
> #bythenumbers #space #astronomy #neutronstar #stars #shorts

Suchanfragen: „neutron star density“, „how dense is a neutron star“, „neutron star sugar cube“.
Freitag – kein Samstags-Hinweis nötig.
