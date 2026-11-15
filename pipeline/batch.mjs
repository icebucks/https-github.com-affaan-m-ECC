#!/usr/bin/env node
// Rendert alle Skripte in scripts/, für die es noch kein output/<id>.mp4 gibt.
// Jedes Video wird vorher gelintet (siehe build.mjs). Kein Upload – nur Upload-Paket.
//   npm run batch             alle fehlenden
//   npm run batch -- --force  alle neu
//   npm run batch -- --strict Abbruch bei ungeprüfter Aussprache (für die Automatisierung)
import fs from "node:fs";
import path from "node:path";
import { buildVideo } from "./build.mjs";
import { ROOT } from "./lib/tts.mjs";

const args = process.argv.slice(2);
const force = args.includes("--force");
const strict = args.includes("--strict");
const ids = fs.readdirSync(path.join(ROOT, "scripts")).filter((f) => f.endsWith(".json")).map((f) => f.slice(0, -5)).sort();
const todo = ids.filter((id) => force || !fs.existsSync(path.join(ROOT, "output", `${id}.mp4`)));
console.log(`${ids.length} Skripte, ${todo.length} zu rendern: ${todo.join(", ") || "–"}`);
const results = [];
for (const id of todo) {
  const t0 = Date.now();
  try {
    const r = await buildVideo(id, { strict });
    results.push({ id, ok: true, dur: r.dur, lufs: r.lufs, min: ((Date.now() - t0) / 60000).toFixed(1) });
  } catch (e) {
    console.error(`✗ ${id}: ${e.message}`);
    results.push({ id, ok: false, error: e.message.split("\n")[0] });
  }
}
console.log("\nErgebnis:");
for (const r of results) console.log(r.ok ? `  ✓ ${r.id}  ${r.dur.toFixed(1)} s  ${r.lufs} LUFS  (${r.min} min)` : `  ✗ ${r.id}  ${r.error}`);
process.exit(results.some((r) => !r.ok) ? 1 : 0);
