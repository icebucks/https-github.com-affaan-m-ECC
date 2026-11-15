# Vergleich KI-Werkzeuge (Testvorlagen) – Stand 15.11.2026

## Testvorlagen
- Bild/Video: „Legionär im Regen, 9 n. Chr.“ und „Bäcker am Ofen, Pompeji“ (Prompts identisch für alle Werkzeuge)
- Stimme: schwierige Sätze aus allen 3 Skripten (Namen, Komposita, ß), Bewertung per Whisper-medium (Wortfehlerrate)

## Stimme
| Variante | Wortfehler (WER) | Tonhöhe | Fehler | CPU-Zeit |
| --- | --- | --- | --- | --- |
| Coqui Thorsten (bisher) | 11,4 % | ~109 Hz | Feldherr Varus → „Feldhervarus“, Arminius → „Aminus“, Stille → „stehle“, Türen → „Führen“ | ~0,2× Echtzeit |
| **OmniVoice (VoiceStudio), Klon unserer Erzählerstimme** | **0,0 %** | ~103 Hz | keine | ~18× Echtzeit (CPU, parallel belastet) |
| OmniVoice, Stimmentwurf „male, low pitch, middle-aged“ | 4,5 % | ~147 Hz | Speere → „Späre“, wasserdichten → „wasserdichtenden“ | ~16× Echtzeit |
Lizenz OmniVoice: Apache 2.0 (Code), Modell basiert auf Qwen3-0.6B.

## Bild / Video
| Werkzeug | Ergebnis | Kosten | Automatisierbar |
| --- | --- | --- | --- |
| Helios (PKU) | nicht lauffähig: braucht NVIDIA-GPU; Demo verlangt 135 s GPU/Run, Gratis-HF-Konto hat weniger | HF PRO ~9 $/Monat → ~10 Clips/Tag | ja (mit PRO) |
| LTX-Video 13B (Demo) | Gratis-Kontingent zu klein (120 s/Run) | HF PRO | ja (mit PRO) |
| Seedance (ElevenLabs) | Video nur mit bezahltem Tarif | bezahlt | ja |
| Seedream-Bilder (ElevenLabs) | ~818 Credits/Bild → ~10 Bilder/Monat gratis | bezahlt für Produktion | ja |
| OpenHiggsfield (beide Repos) | nur Oberfläche für bezahlte Anbieter-Schlüssel | bezahlt | ja |
| MovieFlow / Cantina | kein API, Login im Browser/App; Cantina nicht fotorealistisch | gratis mit Wasserzeichen / unklar | nein (manuell) |
| **RealVisXL V5 Lightning, lokal (CPU)** | fotorealistisch, gute Gesichter/Hände; Kostüm teils ungenau | **0 €**, ~4–5 min/Bild | **ja** |
