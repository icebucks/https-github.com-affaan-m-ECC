#!/usr/bin/env node
// Kurzfilm: Teil 1 (ohne „Teil 2 folgt“-Endkarte) + Teil 2 = ein Film über 60 s
// (Creator-Programm, YouTube). Beispiel:  npm run film -- teutoburg
// Teile werden über ideen/backlog.json gefunden (teil1/teil2) oder direkt angegeben:
//   npm run film -- 01-teutoburg 04-teutoburg-teil2
import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { ROOT } from "./lib/tts.mjs";
import { measureLufs, writeUploadTxt } from "./build.mjs";

const args = process.argv.slice(2);
let ids = args.filter((a) => !a.startsWith("--"));
let slug = ids[0];
if (ids.length === 1) {
  const b = JSON.parse(fs.readFileSync(path.join(ROOT, "ideen", "backlog.json"), "utf8"));
  const e = b.ideen.find((x) => x.slug === slug);
  if (!e || !e.teil1 || !e.teil2) { console.error(`Für "${slug}" fehlen teil1/teil2 in ideen/backlog.json`); process.exit(1); }
  ids = [e.teil1, e.teil2];
} else slug = ids[0].replace(/^\d+-/, "");

const parts = ids.map((id) => {
  const mp4 = path.join(ROOT, "output", `${id}.mp4`);
  if (!fs.existsSync(mp4)) throw new Error(`${mp4} fehlt – erst rendern`);
  const plan = JSON.parse(fs.readFileSync(path.join(ROOT, "assets", id, "audio_plan.json"), "utf8"));
  return { id, mp4, plan, script: JSON.parse(fs.readFileSync(path.join(ROOT, "scripts", `${id}.json`), "utf8")) };
});

// Teil 1..n-1: bis kurz vor der Endkarte; letzter Teil komplett
const inputs = [], filters = [];
parts.forEach((p, i) => {
  const last = i === parts.length - 1;
  const end = last ? p.plan.duration : Math.max(1, p.plan.endcard_start - 0.05);
  inputs.push("-i", p.mp4);
  filters.push(`[${i}:v]trim=0:${end},setpts=PTS-STARTPTS[v${i}];[${i}:a]atrim=0:${end},asetpts=PTS-STARTPTS,afade=t=out:st=${Math.max(0, end - 0.25)}:d=0.25[a${i}]`);
});
const cat = parts.map((_, i) => `[v${i}][a${i}]`).join("") + `concat=n=${parts.length}:v=1:a=1[v][a]`;
const out = path.join(ROOT, "output", `film-${slug}.mp4`);
execFileSync("ffmpeg", ["-y", "-loglevel", "error", ...inputs, "-filter_complex", filters.join(";") + ";" + cat,
  "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "19", "-preset", "slow", "-pix_fmt", "yuv420p",
  "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out], { stdio: "inherit" });
const dur = parseFloat(execFileSync("ffprobe", ["-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", out]).toString());

const s = parts[0].script;
writeUploadTxt({
  titel: `${s.titel.split(" – ")[0]} – Der ganze Film`,
  bildunterschrift: `${s.jahr_ort}: Die ganze Geschichte in einem Film. Ich war dabei.`,
  frage: "Welche Geschichte soll ich als Nächstes erzählen?",
  hashtags: [...new Set(parts.flatMap((p) => p.script.hashtags))].slice(0, 8),
}, path.join(ROOT, "output", `film-${slug}_upload.txt`));
console.log(`Film: ${path.relative(ROOT, out)} (${dur.toFixed(1)} s, ${measureLufs(out)} LUFS)${dur < 61 ? " ⚠ unter 61 s – für das Creator-Programm zu kurz" : ""}`);
