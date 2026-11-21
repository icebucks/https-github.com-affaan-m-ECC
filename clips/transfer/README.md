# Übergabe an neue Sitzungen (Videos > 100 MB in Teilen)

GitHub nimmt nur Dateien bis 100 MB, darum liegen große Videos hier in 95-MB-Teilen.

| Datei | Länge | Größe | sha256 |
|---|---|---|---|
| (leer – NightMissions am 21.11. hochgeladen und gelöscht) | | | |

Zusammensetzen und prüfen:
```
cat clips/transfer/GTA6_NightMissions_11min.mp4.part* > /tmp/GTA6_NightMissions_11min.mp4
sha256sum /tmp/GTA6_NightMissions_11min.mp4   # muss mit der Tabelle übereinstimmen
```
Kapitel: `GTA6_NightMissions_11min.mp4.chapters.txt`. Titel und Beschreibung: `clips/compilations.md` (Abschnitt 21.11.).
Nach dem Upload die Teile wieder löschen (git rm), damit das Repo nicht weiter wächst.
