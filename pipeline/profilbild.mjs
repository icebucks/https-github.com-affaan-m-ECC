// Erzeugt account/profilbild.png (1080×1080): die rim-beleuchtete Profil-Silhouette = Markenzeichen des Kanals.
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
const { chromium } = createRequire(import.meta.url)("playwright"); // vorinstalliert; lokal: npm i -D playwright
import { bustCivil, rimFilter, rimmed } from "./lib/figures.mjs";
import { mulberry } from "./lib/svg.mjs";

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
const r = mulberry(42);
let embers = "";
for (let i = 0; i < 46; i++) {
  const x = 120 + r() * 420, y = 260 + r() * 700, s = 2 + r() * 5;
  embers += `<circle cx="${x.toFixed(0)}" cy="${y.toFixed(0)}" r="${s.toFixed(1)}" fill="#ffb15a" opacity="${(0.25 + r() * 0.6).toFixed(2)}"/>`;
}
const hero = (c) => bustCivil(c) + `<rect x="40" y="790" width="700" height="500" fill="${c}"/><path d="M600,560 Q700,640 740,800 L600,800Z" fill="${c}"/>`;
const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1080" viewBox="0 0 1080 1080">
<defs>
  <radialGradient id="bg" cx="38%" cy="52%" r="75%"><stop offset="0%" stop-color="#7a3a12"/><stop offset="35%" stop-color="#2a1a12"/><stop offset="100%" stop-color="#07090a"/></radialGradient>
  <radialGradient id="fire2" gradientUnits="userSpaceOnUse" cx="300" cy="580" r="520"><stop offset="0%" stop-color="#ff8a2b" stop-opacity="0.55"/><stop offset="60%" stop-color="#ff6a1b" stop-opacity="0.12"/><stop offset="100%" stop-color="#ff6a1b" stop-opacity="0"/></radialGradient>
  ${rimFilter("rim", 9)}
  <filter id="glow"><feGaussianBlur stdDeviation="3"/></filter>
</defs>
<rect width="1080" height="1080" fill="url(#bg)"/>
<rect width="1080" height="1080" fill="url(#fire2)"/>
${embers}
<g transform="translate(300,230) scale(1.25)">${rimmed(hero, "#06080a", "#ff8a2b", "rim", -16, -6)}</g>
</svg>`;
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1080, height: 1080 } });
await page.setContent(`<html><body style="margin:0;background:#000">${svg}</body></html>`);
await page.screenshot({ path: path.join(ROOT, "account", "profilbild.png") });
await browser.close();
console.log("account/profilbild.png");
