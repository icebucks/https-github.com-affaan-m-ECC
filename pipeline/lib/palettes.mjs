// Eine Farbpalette pro Epoche. Neue Epoche = neuer Eintrag.
// sky: Verlauf oben→unten; far/mid/near/fg: Ebenen von hinten nach vorn (immer dunkler);
// fog: RGB für Nebel; accent: Lichtquelle (Fackel, Glut, Kessel) = Farbe des aktiven Wortes.
export const PALETTES = {
  roemer: {
    name: "Römer – Grün-Grau + Fackelorange",
    sky: ["#1b2420", "#3e4c44", "#5f6e64"],
    far: "#33423a",
    mid: "#1f2a24",
    near: "#121a16",
    fg: "#070b09",
    fog: "150,168,156",
    accent: "#ff8a2b",
    accent2: "#ffc27a",
    cold: "#9fb7b0",
    rain: "rgba(190,210,205,1)",
    caption: "#ffffff",
    grade: "rgba(30,60,45,0.18)",
  },
  pompeji: {
    name: "Pompeji – Ocker + Aschgrau + Glutrot",
    sky: ["#2a1d17", "#6b4a2e", "#b07a45"],
    far: "#5a3f2c",
    mid: "#3a281d",
    near: "#221710",
    fg: "#0d0806",
    fog: "150,140,130",
    accent: "#ff4a1c",
    accent2: "#ffb347",
    cold: "#a9a29a",
    rain: "rgba(170,165,160,1)",
    caption: "#ffffff",
    grade: "rgba(90,50,20,0.2)",
  },
  titanic: {
    name: "Titanic – Stahlblau + Kesselorange",
    sky: ["#0b1520", "#1d3346", "#3a5a72"],
    far: "#2a4256",
    mid: "#17283a",
    near: "#0d1824",
    fg: "#04080d",
    fog: "120,150,175",
    accent: "#ff7a1f",
    accent2: "#ffd08a",
    cold: "#8fb3cf",
    rain: "rgba(190,215,235,1)",
    caption: "#ffffff",
    grade: "rgba(20,45,70,0.2)",
  },
};

export function palette(epoche) {
  const p = PALETTES[epoche];
  if (!p) throw new Error(`Unbekannte Epoche "${epoche}". Verfügbar: ${Object.keys(PALETTES).join(", ")}`);
  return p;
}
