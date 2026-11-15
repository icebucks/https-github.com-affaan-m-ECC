import { motifs as roemer } from "./roemer.mjs";

// Alle Motive in einem Register. Neue Epochen: Datei anlegen und hier ergänzen.
export const MOTIFS = { ...roemer };

export function motif(name) {
  const m = MOTIFS[name];
  if (!m) throw new Error(`Unbekanntes Motiv "${name}". Verfügbar: ${Object.keys(MOTIFS).join(", ")}`);
  return m;
}
