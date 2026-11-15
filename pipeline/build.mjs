#!/usr/bin/env node
// Baut EIN Video: Stimme → Zeitplan → HyperFrames-Komposition → Audio-Mix → Lint → Render → Upload-Paket.
// Aufruf:  npm run build -- <id>            (z. B. 01-teutoburg)
//          npm run build -- <id> --no-render (nur Komposition, z. B. für die Vorschau)
//          npm run build -- <id> --draft     (schnelles Test-Rendering)
import fs from "node:fs";
import path from "node:path";
import { execFileSync, spawnSync } from "node:child_process";
import { makePlan, writeProject } from "./lib/compose.mjs";
import { makeVoice, ROOT } from "./lib/tts.mjs";

const HF = path.join(ROOT, "node_modules", ".bin", "hyperframes");

export function hf(args, cwd, opts = {}) {
  const r = spawnSync(HF, args, { cwd, encoding: "utf8", stdio: opts.quiet ? "pipe" : "inherit", env: { ...process.env, HYPERFRAMES_NO_UPDATE_CHECK: "1" } });
  if (r.status !== 0) throw new Error(`hyperframes ${args[0]} fehlgeschlagen (Exit ${r.status})\n${r.stdout || ""}${r.stderr || ""}`);
  return r.stdout;
}

// Viral-Check: die wichtigsten TikTok-Faktoren für Wiedergabedauer und Reichweite
export function viralCheck(s, plan, words) {
  const out = [];
  const ok = (c, good, bad) => out.push(c ? `✓ ${good}` : `⚠ ${bad}`);
  const firstEnd = Math.max(...words.words.filter((w) => w.satz === 0).map((w) => w.end));
  ok(firstEnd <= 3.2, `Hook-Satz endet nach ${firstEnd.toFixed(1)} s`, `Erster Satz dauert ${firstEnd.toFixed(1)} s – Hook muss in ≤ 3 s sitzen (kürzer, Spannung zuerst)`);
  ok(!!s.hook_text, "Hook-Text im ersten Bild", 'Feld "hook_text" fehlt (Neugier-Zeile im ersten Bild, max. 6 Wörter)');
  const teil2 = /teil2|teil-2/.test(s.id);
  const [lo, hi] = s.lang ? [61, 95] : teil2 ? [25, 55] : [21, 40];
  ok(plan.duration >= lo && plan.duration <= hi, `Länge ${plan.duration.toFixed(1)} s`, `Länge ${plan.duration.toFixed(1)} s außerhalb ${lo}–${hi} s`);
  const avg = plan.duration / plan.scenes.length;
  ok(avg <= 3.8, `Bildwechsel alle ${avg.toFixed(1)} s`, `Bildwechsel nur alle ${avg.toFixed(1)} s – mehr Szenen`);
  ok(!!plan.wendeStart && plan.wendeStart / plan.duration <= 0.8, "Wendepunkt vor dem letzten Fünftel", "Wendepunkt fehlt oder kommt zu spät");
  ok(!!s.frage, "Frage an die Zuschauer (Kommentare)", 'Feld "frage" fehlt');
  ok(s.hashtags.length >= 3 && s.hashtags.length <= 8, `${s.hashtags.length} Hashtags`, "3–8 Hashtags verwenden");
  ok((s.betonung || []).length >= 2, "Schlüsselwörter betont", 'Feld "betonung" (2–5 Schlüsselwörter) fehlt');
  return out;
}

export function validateScript(s, file) {
  const need = ["id", "titel", "jahr_ort", "epoche", "erzaehltext", "szenen", "hashtags"];
  for (const k of need) if (s[k] == null) throw new Error(`${file}: Feld "${k}" fehlt`);
  if (/\d/.test(s.erzaehltext)) throw new Error(`${file}: Zahlen im Sprechtext bitte ausschreiben (TTS)`);
  if (!s.szenen.length) throw new Error(`${file}: keine Szenen`);
}

export async function buildVideo(id, { render = true, quality = "delivery", strict = false } = {}) {
  const file = path.join(ROOT, "scripts", `${id}.json`);
  const script = JSON.parse(fs.readFileSync(file, "utf8"));
  validateScript(script, file);
  console.log(`\n=== ${script.id}: ${script.titel} ===`);

  const assetDir = path.join(ROOT, "assets", id);
  const projDir = path.join(ROOT, "compositions", id);
  fs.mkdirSync(assetDir, { recursive: true });

  // 0) Aussprache prüfen (bei --strict Abbruch, wenn ungeprüfte Wörter übrig sind)
  const chk = spawnSync("python3", [path.join(ROOT, "pipeline", "aussprache_check.py"), file, ...(strict ? ["--strict"] : [])], { encoding: "utf8" });
  fs.writeFileSync(path.join(assetDir, "aussprache.txt"), chk.stdout);
  const offen = /(\d+) Wort\/Wörter prüfen: (.*)/.exec(chk.stdout);
  if (offen) console.log(`  ⚠ Aussprache prüfen: ${offen[2]} (Details: assets/${id}/aussprache.txt)`);
  if (chk.status === 2) throw new Error("Ungeprüfte Aussprache – erst pipeline/aussprache.json ergänzen (npm run aussprache -- " + id + ")");
  // 1) Stimme + Wort-Zeitstempel
  const words = await makeVoice(script, assetDir);
  // 2) Zeitplan (Szenen nach Sätzen)
  const plan = makePlan(script, words);
  console.log(`  Dauer ${plan.duration.toFixed(1)} s, ${plan.scenes.length} Szenen, Wendepunkt ab ${plan.wendeStart?.toFixed(1) ?? "–"} s`);
  const viral = viralCheck(script, plan, words);
  fs.writeFileSync(path.join(assetDir, "viral_check.txt"), viral.join("\n") + "\n");
  for (const v of viral) console.log(`  ${v}`);
  // 3) Komposition schreiben
  const { events } = writeProject({ script, plan, projDir, audioFile: "mix.wav" });
  // 4) Audio: Atmo + Musik + Effekte + Stimme, -14 LUFS
  const audioPlan = {
    seed: [...id].reduce((a, c) => a + c.charCodeAt(0), 0),
    duration: plan.duration,
    voice: path.join(assetDir, "voice.wav"),
    out: path.join(assetDir, "mix.wav"),
    atmo: script.atmo || [],
    musik: script.musik || "drone_moll",
    scenes: plan.scenes.map((s) => ({ start: s.start, end: s.end, wendepunkt: !!s.wendepunkt, ton: s.ton || null })),
    hook_hit: 0,
    wende_start: plan.wendeStart,
    endcard_start: plan.endcardStart,
    events,
  };
  fs.writeFileSync(path.join(assetDir, "audio_plan.json"), JSON.stringify(audioPlan, null, 1));
  console.log("  Audio mischen …");
  execFileSync("python3", [path.join(ROOT, "pipeline", "audio_mix.py"), path.join(assetDir, "audio_plan.json")], { stdio: ["ignore", "ignore", "inherit"] });
  fs.mkdirSync(path.join(projDir, "assets"), { recursive: true });
  fs.copyFileSync(path.join(assetDir, "mix.wav"), path.join(projDir, "assets", "mix.wav"));
  // 4b) Ist der Erzähler im fertigen Mix klar verständlich? (Whisper prüft)
  if (process.env.SKIP_MIX_CHECK !== "1") {
    console.log("  Verständlichkeit prüfen …");
    const mc = spawnSync("python3", [path.join(ROOT, "pipeline", "mix_check.py"), path.join(assetDir, "mix.wav"), file], { encoding: "utf8" });
    fs.writeFileSync(path.join(assetDir, "mix_check.txt"), (mc.stdout || "") + (mc.stderr || "").slice(-2000));
    console.log("  " + (mc.stdout || "").split("\n")[0]);
    if (mc.status === 3) throw new Error(`Erzähler im Mix nicht sauber verständlich – siehe assets/${id}/mix_check.txt`);
  }

  // 5) Lint (Pflicht vor dem Rendern)
  console.log("  Lint …");
  hf(["lint"], projDir);
  if (!render) return { projDir, plan };

  // 6) Rendern
  const outDir = path.join(ROOT, "output");
  fs.mkdirSync(outDir, { recursive: true });
  const raw = path.join(outDir, `${id}.render.mp4`);
  const out = path.join(outDir, `${id}.mp4`);
  console.log(`  Rendern (${quality}) …`);
  hf(["render", "--quality", quality, "--fps", "30", "-o", raw], projDir);
  // 7) Endfassung: Video in TikTok-taugliche Größe kodieren, normalisierten Mix (-14 LUFS) anlegen
  execFileSync("ffmpeg", ["-y", "-loglevel", "error", "-i", raw, "-i", path.join(assetDir, "mix.wav"),
    "-map", "0:v:0", "-map", "1:a:0", "-c:v", "libx264", "-crf", "19", "-preset", "slow", "-pix_fmt", "yuv420p", "-maxrate", "16M", "-bufsize", "32M", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest", "-movflags", "+faststart", out]);
  fs.rmSync(raw);
  const lufs = measureLufs(out);
  const dur = parseFloat(execFileSync("ffprobe", ["-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", out]).toString());
  console.log(`  Fertig: ${path.relative(ROOT, out)} (${dur.toFixed(1)} s, ${lufs} LUFS)`);
  writeUploadTxt(script, path.join(outDir, `${id}_upload.txt`));
  return { out, plan, lufs, dur };
}

export function measureLufs(file) {
  const r = spawnSync("ffmpeg", ["-hide_banner", "-i", file, "-af", "ebur128", "-f", "null", "-"], { encoding: "utf8" });
  const m = /I:\s+(-?[\d.]+) LUFS/.exec(r.stderr.slice(r.stderr.lastIndexOf("Summary")));
  return m ? parseFloat(m[1]) : null;
}

export function writeUploadTxt(script, file) {
  const tags = script.hashtags.slice(0, 8);
  const txt = [
    `TITEL (intern): ${script.titel}`,
    "",
    "BILDUNTERSCHRIFT:",
    `${script.bildunterschrift || script.titel} ${script.frage || ""}`.trim(),
    "",
    "HASHTAGS:",
    tags.join(" "),
    "",
    "WICHTIG: KI-Label beim Upload aktivieren (Stimme und Bilder sind KI-/computergeneriert).",
    "",
  ].join("\n");
  fs.writeFileSync(file, txt);
}

// CLI
if (import.meta.url === `file://${process.argv[1]}`) {
  const args = process.argv.slice(2);
  const id = args.find((a) => !a.startsWith("--"));
  if (!id) {
    console.error("Aufruf: npm run build -- <id> [--no-render] [--draft]");
    process.exit(1);
  }
  buildVideo(id.replace(/\.json$/, "").replace(/^scripts\//, ""), {
    render: !args.includes("--no-render"),
    quality: args.includes("--draft") ? "draft" : "delivery",
    strict: args.includes("--strict"),
  }).catch((e) => { console.error("FEHLER:", e.message); process.exit(1); });
}
