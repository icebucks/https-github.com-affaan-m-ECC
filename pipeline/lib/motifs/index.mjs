import { motifs as roemer } from "./roemer.mjs";
import { motifs as pompeji } from "./pompeji.mjs";
import { motifs as titanic } from "./titanic.mjs";

// Alle Motive in einem Register. Neue Epoche: Datei anlegen und hier ergänzen.
export const MOTIFS = { ...roemer, ...pompeji, ...titanic };

export function motif(name) {
  const m = MOTIFS[name];
  if (!m) throw new Error(`Unbekanntes Motiv "${name}". Verfügbar: ${Object.keys(MOTIFS).join(", ")}`);
  return m;
}
