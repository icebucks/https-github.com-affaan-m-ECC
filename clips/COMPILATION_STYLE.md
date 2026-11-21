# GTA-6-Compilations – Stil-Leitfaden (Stand 21.11.2026)

Ziel der Person: **hochwertige GTA-6-Compilations, die unser Standardformat („go-to“) werden.**
Technik: `clips/compile.py` (v2), Thumbnail `clips/thumb.py`, Protokoll `clips/compilations.md`.

## Was erfolgreiche Compilations ausmacht (Recherche 21.11.)
- **Jeder Clip folgt Aufbau → Steigerung → Pointe** – und endet direkt nach der Pointe. Häufigster Fehler: nur den Crash zeigen; ohne Aufbau versteht niemand, warum er lustig ist. Nach der Pointe nicht weiterlaufen lassen. (eklipse.gg, WatchMojo)
- **Totzeit raus, bevor sie auffällt:** Karten, Menüs, Ladebildschirme, ereignislose Fahrten. Bei Highlight-Videos etwa alle 5–10 s ein neuer Reiz (Schnitt, Text, Ereignis). (veo3ai, kapwing)
- **Übergänge kurz: 0,2–0,5 s.** Lange Blenden und viele Spielereien bremsen. Wenige, gleichbleibende Übergangsarten wirken professioneller. (eklipse.gg)
- **Hook in den ersten Sekunden:** Die stärkste Szene zuerst anteasern. YouTube bewertet vor allem, wie viele nach 30 s noch schauen.
- **Ton ist die halbe Miete:** Spielsound sauber, Übergänge mit Whoosh, Treffer mit Hit.
- **Format, das bei GTA funktioniert:** nummerierte Folgen („Fails & Epic Moments #138“), gemischt aus Fails, Wins, Verfolgungsjagden, NPC-Chaos und Stunts. Ein gescheiterter Stunt ist lustiger als ein gelungener; ein gelungener, der eigentlich nicht klappen kann, wirkt durch Ungläubigkeit.
- **Größtes Interesse aktuell:** Launch-Phase von GTA 6 (Streams von IShowSpeed mit 65 Mio. Aufrufen, Shorts wie „World's First Stolen Plane in GTA 6“ mit 3,6 Mio.) → „Erste/Neue/Krasseste X in GTA 6“ zieht.

## Inhaltliche Genres (Reihen, die sich abwechseln)
| Reihe | Inhalt | Titelmuster |
|---|---|---|
| **Police Chases** | Verfolgungen, 5–6 Sterne, Fluchten | `GTA 6 – Craziest Police Chases #N (No Commentary)` |
| **Heists & Robberies** | Überfälle, Einbrüche, Shootouts | `GTA 6 Pure Gameplay – Pawn Shop Robbery & …` |
| **Fails & Wins** | Unfälle, WASTED, Glück, Physik-Chaos | `GTA 6 Fails & Epic Moments #N` |
| **NPC Chaos / Funny** | absurde NPC-Reaktionen, Dialoge | `GTA 6 NPCs Are Insane #N` |
| **Night / Cinematic** | Neon-Fahrten, Sonnenuntergang, Wetter, Vice City | `GTA 6 Night Missions / Cinematic Drive (No Commentary)` |

## Schnitt-Regeln (compile.py v2)
1. **Cold Open** (automatisch): 3–4 × 1,8 s der lautesten/stärksten Momente vor dem Intro, „COMING UP“, Weißblitz-Schnitte, Bass-Drop. Bessere Momente per `"teaser": [{"seg": i, "t": s}]` von Hand setzen.
2. **Kapitel 60–120 s**, je Kapitel genau eine Geschichte (Aufbau → Pointe). Mindestens 8 Min. gesamt, Ziel 9–11 Min.
3. **Totzeit schneiden** mit `"cont": true`: Ein Kapitel aus mehreren Stücken zusammensetzen; dazwischen sitzt ein 0,18-s-Blitzschnitt. Karten, Menüs, Handy-Bildschirme und ereignislose Fahrten > 10 s immer raus.
4. **Übergänge zwischen Kapiteln** (0,45 s, rotierend): Wischer links, Weißblitz, Zoom, Wischer rechts – jeweils mit Whoosh.
5. **Countdown** (`"countdown": true`): beste Szene zuletzt als #1 → Leute bleiben bis zum Ende.
6. **Punch-Text** sparsam (höchstens 1 pro Kapitel, 1–3 Wörter, ehrlich): `"text": [{"at": 12, "text": "5 STARS."}]`.
7. **Ton:** Originaler Spielsound bleibt Hauptsache („Pure Gameplay“). Musik nur in Intro/Outro (eigene Synthwave aus `music.py` – keine fremden Tracks). Phonk/Synthwave sind auch nur dann sicher, wenn die Lizenz schriftlich vorliegt; fremde Musik und Radiosender aus dem Spiel nie unterlegen.
8. **−14 LUFS**, Peak ≤ −1,5 dBTP (macht compile.py).

## Packaging
- **Titel:** Genre/Ereignis vorn, „GTA 6“ im ersten Drittel, „(No Commentary)“ hinten. ≤ 70 Zeichen.
- **Thumbnail** (`clips/thumb.py`): echtes Spielbild mit klarer Aktion (kein Menü, keine Karte, nicht zu dunkel), 2 Zeilen à 1–2 Wörter, Zeile 2 neonrot. Kanal muss für eigene Thumbnails verifiziert sein (youtube.com/verify).
- **Beschreibung:** 1 Satz mit Suchbegriff („GTA 6 gameplay no commentary …“), Kapitel, Credits „🎥 Gameplay via <Kanal> (Twitch)“, 3 Hashtags.
- **Rhythmus (ab 22.11.):** täglich **Short 13:00 · Short 17:00 · Compilation 19:00** (MEZ) – passt zum Banner „2 new videos every day“.
- **Shorts:** 1–2 pro Compilation, aus deren stärksten Momenten (#1/#2), `clipper.py cut <block> <a> <b> --gameplay --raw --hook "…|…" --credit "via <kanal>"`, 25–35 s, Pointe am Ende. Nicht in den ersten ~8 s eines Aufnahmeblocks starten (Standbild bis zum ersten Keyframe). Beschreibung mit Link zur Compilation; in YouTube Studio zusätzlich „Ähnliches Video“ = Compilation setzen (geht nicht per API). Protokoll: `yt_shorts.json`.
- **Warum Shorts:** Reichweite bei Nicht-Abonnenten (neuer Kanal), GTA-6-Launch-Welle, schnelle Rückmeldung, welche Szenen ziehen; Shorts schaden langen Videos nicht. Nach 2 Wochen in den Analysen prüfen, ob sie Abonnenten bringen.

## Quellen
- https://blog.eklipse.gg/streaming-tips/gta-5-funny-moments.html
- https://blog.eklipse.gg/beginner-guide-2/how-to-use-transitions-effectively-in-short-form-video-editing.html
- https://www.veo3ai.io/blog/gaming-video-edit
- https://www.kapwing.com/resources/how-to-edit-videos-like-a-youtuber/
- https://watchmojo.com/articles/top-5-gta-5-stunt-videos-let-s-play-countdown
- https://streamscharts.com/news/gta-6s-most-viewed-youtube-streams
- https://streamscharts.com/news/most-viewed-gta-6-clips
- https://www.epidemicsound.com/music/genres/phonk/
