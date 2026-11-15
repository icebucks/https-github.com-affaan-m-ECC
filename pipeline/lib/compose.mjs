// Erzeugt aus Skript + Wortzeiten ein komplettes HyperFrames-Projekt.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { palette } from "./palettes.mjs";
import { motif } from "./motifs/index.mjs";
import { mulberry, hashSeed, CW, CH, FW, FH } from "./svg.mjs";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const RUNTIME = fs.readFileSync(path.join(HERE, "runtime.js"), "utf8");
const r3 = (n) => Math.round(n * 1000) / 1000;
const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

export function splitSentences(text) {
  return text.trim().split(/(?<=[.!?])\s+/).filter(Boolean);
}

// Gleiche Tokenisierung wie tts_piper.py, aber mit Satzzeichen (für Untertitel-Umbrüche)
export function tokensWithPunct(sentence) {
  return sentence.split(/\s+/).filter((w) => /[\p{L}\p{N}]/u.test(w));
}

// ------------------------------------------------------------------ Zeitplan
export function makePlan(script, wordsData) {
  const sentences = splitSentences(script.erzaehltext);
  const words = wordsData.words;
  const sentStart = sentences.map((_, i) => {
    const w = words.find((x) => x.satz === i);
    return w ? w.start : null;
  });
  const sentEnd = sentences.map((_, i) => {
    const ws = words.filter((x) => x.satz === i);
    return ws.length ? ws[ws.length - 1].end : null;
  });
  const last = sentences.length - 1;
  const hasEndcard = Boolean(script.endkarte);
  const endcardStart = hasEndcard ? r3(sentStart[last] - 0.12) : r3(sentEnd[last] + 0.3);
  const duration = r3(Math.max(endcardStart + 1.6, wordsData.duration + 0.35, sentEnd[last] + 0.9));

  const scenes = script.szenen.map((s, i) => {
    let start = s.start ?? (s.ab_satz != null ? sentStart[s.ab_satz] - 0.15 : null);
    if (start == null) throw new Error(`Szene ${i}: weder "start" noch gültiger "ab_satz"`);
    if (i === 0) start = 0;
    return { ...s, start: r3(Math.max(0, start)) };
  });
  scenes.forEach((s, i) => { s.end = i < scenes.length - 1 ? scenes[i + 1].start : duration; });
  // Lange Szenen in zwei Einstellungen teilen (Schnitt alle 3–5 s), bevorzugt an Satzgrenzen
  const MAX_SHOT = 5.2;
  for (let guard = 0; guard < 40; guard++) {
    const i = scenes.findIndex((s) => s.end - s.start > MAX_SHOT && !(s.end === duration && hasEndcard && s.end - s.start < MAX_SHOT + (duration - endcardStart)));
    if (i === -1) break;
    const s = scenes[i];
    const mid = (s.start + s.end) / 2;
    const cands = sentStart.filter((t) => t != null && t - 0.15 > s.start + 2.0 && t - 0.15 < Math.min(s.end, endcardStart) - 2.0).map((t) => t - 0.15);
    const cut = r3(cands.length ? cands.sort((a, b) => Math.abs(a - mid) - Math.abs(b - mid))[0] : mid);
    const second = { ...s, start: cut, variant: (s.variant || 0) + 1, origStart: s.origStart ?? s.start, origEnd: s.origEnd ?? s.end };
    s.origStart = s.origStart ?? s.start;
    s.origEnd = s.origEnd ?? s.end;
    s.end = cut;
    scenes.splice(i + 1, 0, second);
  }
  scenes.forEach((s, i) => { s.id = `s${String(i + 1).padStart(2, "0")}`; });
  const wende = scenes.find((s) => s.wendepunkt);
  return {
    sentences, sentStart, sentEnd, scenes, duration, endcardStart, hasEndcard,
    hookEnd: 2.2, wendeStart: wende ? wende.start : null,
    captionWords: words.filter((w) => !(hasEndcard && w.satz === last)),
  };
}

// ------------------------------------------------------------------ Szenen
function sceneHtml(script, plan, scene, index, pal) {
  const sid = scene.id;
  const seed = hashSeed(script.id + (scene.origStart ?? scene.start));
  const r = mulberry(seed);
  // Eine Szene kann in mehrere Einstellungen geteilt sein: alles läuft auf der Zeitachse der
  // ganzen Szene (base..fullEnd), jede Einstellung zeigt nur ihren Ausschnitt ab "offset".
  const base = scene.origStart ?? scene.start;
  const fullEnd = scene.origEnd ?? scene.end;
  const tail = (end) => (end >= plan.duration - 0.001 ? 0 : 0.4);
  const slot = r3(scene.end - scene.start + tail(scene.end));
  const full = r3(fullEnd - base + tail(fullEnd));
  const offset = r3(scene.start - base);
  const satz = (i) => r3((plan.sentStart[i] ?? base) - base);
  const ctx = { pal, r, sid, dur: full, seed, scene, script, satz };
  const m = motif(scene.motiv)(ctx);
  let cam = m.camera || { from: { scale: 1, x: 0, y: 0 }, to: { scale: 1.08, x: 0, y: 0 } };
  if (scene.variant) {
    // zweite Einstellung derselben Szene: näher dran, Bewegung in Gegenrichtung
    const k = scene.variant % 2 ? 1 : -1;
    cam = { ease: cam.ease, from: { scale: cam.to.scale + 0.16, x: -cam.to.x - 50 * k, y: cam.to.y - 70 }, to: { scale: cam.to.scale + 0.3, x: -cam.to.x + 30 * k, y: cam.to.y - 30 } };
  }
  if (scene.wendepunkt && !m.shake) m.shake = 2.5;

  // Ebenen: hintere Ebenen, dann Nebel-Canvas + Lichter, dann vordere Ebenen
  const split = m.layers.findIndex((l) => l.depth >= 0.5);
  const at = split === -1 ? m.layers.length : split;
  const objHtml = (o) => `<div id="${sid}-${o.name}" class="${sid}-obj" style="width:${o.w}px;height:${o.h}px"><svg viewBox="${o.vb || `0 0 ${o.w} ${o.h}`}" width="${o.w}" height="${o.h}">${o.svg}</svg></div>`;
  // Objekte mit "before": "<ebene>" liegen hinter dieser Ebene (z. B. Tür hinter dem Türrahmen)
  const layerHtml = (l) => (m.objects || []).filter((o) => o.before === l.name).map(objHtml).join("") + `<div id="${sid}-L-${l.name}" class="${sid}-layer">${l.svg}</div>`;
  const lights = (m.lights || []).map((L, i) =>
    `<div id="${sid}-light${i}" class="${sid}-light" style="left:${L.x - L.r}px;top:${L.y - L.r}px;width:${2 * L.r}px;height:${2 * L.r}px;background:radial-gradient(circle, ${L.color} 0%, ${L.color}55 30%, transparent 70%);opacity:${L.intensity}"></div>`).join("");
  const spears = (m.spears || []).map((s, i) =>
    `<div id="${sid}-sp${i}" class="${sid}-spear"><svg viewBox="0 -20 540 40" width="540" height="40">${s.svg}</svg></div>`).join("");
  const labels = (m.labels || []).map((L, i) =>
    `<div id="${sid}-lab${i}" class="${sid}-label" style="left:${L.x - 300}px;top:${L.y}px">${esc(L.text)}</div>`).join("");

  const inner =
    m.layers.slice(0, at).map(layerHtml).join("") +
    `<canvas id="${sid}-back" class="${sid}-back" width="${CW / 2}" height="${CH / 2}"></canvas>` +
    lights +
    m.layers.slice(at).map(layerHtml).join("") +
    spears + (m.objects || []).filter((o) => !o.before).map(objHtml).join("") + labels;

  const dir = cam.to.x - cam.from.x >= 0 ? 1 : -1;
  const js = [];
  js.push(`tl.fromTo("#${sid}-cam", {scale:${cam.from.scale},x:${cam.from.x},y:${cam.from.y}}, {scale:${cam.to.scale},x:${cam.to.x},y:${cam.to.y},duration:${slot},ease:"${cam.ease || "sine.inOut"}"}, ${offset});`);
  for (const l of m.layers) {
    if (!l.depth) continue;
    const P = 46 * l.depth * dir;
    const extra = m.march && m.march.name === l.name ? m.march.dx * slot : 0;
    js.push(`tl.fromTo("#${sid}-L-${l.name}", {x:${r3(-P)}}, {x:${r3(P + extra)},duration:${full},ease:"none"}, 0);`);
  }
  if (index > 0) js.push(`tl.fromTo("#${sid}-fade", {opacity:0}, {opacity:1,duration:0.4,ease:"power1.out"}, ${offset});`);
  (m.spears || []).forEach((s, i) => {
    js.push(`tl.fromTo("#${sid}-sp${i}", {x:${r3(s.x0)},y:${r3(s.y0)},rotation:${r3(s.rot)},scale:${r3(s.s)}}, {x:${r3(s.x1)},y:${r3(s.y1)},duration:0.42,ease:"power2.in"}, ${r3(s.t0)});`);
  });
  (m.labels || []).forEach((_, i) => {
    js.push(`tl.fromTo("#${sid}-lab${i}", {opacity:0,y:20}, {opacity:1,y:0,duration:0.5,ease:"power2.out"}, ${0.35 + i * 0.35});`);
  });
  for (const a of m.anims || []) js.push(a);
  if (m.darken) js.push(`tl.fromTo("#${sid}-dark", {opacity:0}, {opacity:${m.darken},duration:${slot},ease:"none"}, 0);`);

  const lightSpec = JSON.stringify((m.lights || []).map((L) => ({ i: L.intensity, f: !!L.flicker, fast: !!L.fast })));
  const script_ = `
${RUNTIME}
(function () {
  const tl = gsap.timeline({ paused: true });
  ${js.join("\n  ")}
  const fxB = hfMakeFx(document.getElementById("${sid}-back"), ${JSON.stringify((m.fxBack || []).map((s) => scaleSpec(s, 0.5)))}, ${seed % 100000});
  const fxF = hfMakeFx(document.getElementById("${sid}-front"), ${JSON.stringify(m.fxFront || [])}, ${(seed % 100000) + 1});
  const lights = ${lightSpec}.map((L, i) => ({ ...L, el: document.getElementById("${sid}-light" + i) }));
  const shake = ${m.shake || 0}, shakeFrom = ${m.shakeFrom || 0};
  // Daumenkino-Figuren (Geh-/Lauf-/Arbeitszyklen): pro Bild genau ein Einzelbild sichtbar
  const walkers = ${JSON.stringify(m.walkers || [])}.map((w) => ({ ...w, frames: Array.from(document.getElementById(w.id)?.children || []) }));
  function render(t) {
    fxB(t);
    fxF(t);
    for (const w of walkers) {
      const n = w.frames.length;
      if (!n) continue;
      const k = Math.floor((((t * w.rate + (w.phase || 0)) % 1) + 1) % 1 * n) % n;
      w.frames.forEach((fr, j) => fr.setAttribute("opacity", j === k ? "1" : "0"));
    }
    lights.forEach((L, i) => { if (L.f) L.el.style.opacity = (L.i * hfFlicker(t * (L.fast ? 2.2 : 1), i + 1)).toFixed(3); });
    if (shake && t >= shakeFrom) {
      const k = shake * (0.6 + 0.4 * Math.abs(Math.sin(t * 2.1)));
      gsap.set("#${sid}-shake", { x: k * hfNoise(t * 9, 1), y: k * hfNoise(t * 8, 4), rotation: k * 0.04 * hfNoise(t * 6, 2) });
    }
  }
  const P = { t: 0 };
  tl.to(P, { t: ${full}, duration: ${full}, ease: "none", onUpdate: () => render(P.t) }, 0);
  ${offset > 0 || slot < full ? `// Einstellung = Ausschnitt ${offset}s..${r3(offset + slot)}s der ganzen Szene
  const shot = gsap.timeline({ paused: true });
  const Q = { t: ${offset} };
  shot.to(Q, { t: ${r3(offset + slot)}, duration: ${slot}, ease: "none", onUpdate: () => tl.seek(Q.t, false) }, 0);
  tl.seek(${offset}, false);
  window.__timelines["${sid}"] = shot;` : `render(0);
  window.__timelines["${sid}"] = tl;`}
})();`;

  const html = `<template>
<style>
#root { position: absolute; inset: 0; overflow: hidden; background: ${pal.fg}; }
#${sid}-fade, #${sid}-shake { position: absolute; inset: 0; }
#${sid}-cam { position: absolute; left: ${-(CW - FW) / 2}px; top: ${-(CH - FH) / 2}px; width: ${CW}px; height: ${CH}px; transform-origin: 50% 50%; }
.${sid}-layer { position: absolute; left: 0; top: 0; width: ${CW}px; height: ${CH}px; will-change: transform; }
.${sid}-layer svg { display: block; }
.${sid}-back { position: absolute; left: 0; top: 0; width: ${CW}px; height: ${CH}px; }
.${sid}-light { position: absolute; border-radius: 50%; mix-blend-mode: screen; pointer-events: none; }
.${sid}-obj { position: absolute; left: 0; top: 0; will-change: transform; }
.${sid}-spear { position: absolute; left: 0; top: 0; width: 540px; height: 40px; transform-origin: 50% 50%; }
.${sid}-label { position: absolute; width: 600px; text-align: center; font-family: "EB Garamond", serif; font-weight: 700; font-style: italic; font-size: 58px; color: ${pal.accent2}; text-shadow: 0 0 18px rgba(0,0,0,0.9), 0 2px 4px #000; letter-spacing: 0.04em; }
#${sid}-front { position: absolute; left: 0; top: 0; width: ${FW}px; height: ${FH}px; }
#${sid}-grade { position: absolute; inset: 0; background: ${pal.grade}; mix-blend-mode: multiply; }
#${sid}-dark { position: absolute; inset: 0; background: #000; opacity: 0; }
</style>
<div id="root" data-composition-id="${sid}" data-width="${FW}" data-height="${FH}" data-layout-allow-overflow data-layout-allow-overlap>
  <div id="${sid}-fade"><div id="${sid}-shake"><div id="${sid}-cam">${inner}</div></div>
  <canvas id="${sid}-front" width="${FW}" height="${FH}"></canvas>
  <div id="${sid}-grade"></div>
  <div id="${sid}-dark"></div></div>
</div>
<script>${script_}</script>
</template>
`;
  const events = (m.events || []).map((e) => ({ t: r3(base + e.dt), typ: e.typ, gain: e.gain })).filter((e) => e.t >= scene.start - 0.01 && e.t < scene.end);
  return { html, slot, events };
}

function scaleSpec(s, k) {
  // Nebel-Canvas läuft in halber Auflösung im Kamera-Raum
  const o = { ...s };
  for (const key of ["size", "y0", "y1", "speed"]) if (o[key] != null) o[key] = o[key] * k;
  if (o.region) o.region = o.region.map((v) => v * k);
  return o;
}

// ------------------------------------------------------------------ Hook
function hookHtml(script, pal) {
  const [a, b] = script.jahr_ort.split(/\s+[–-]\s+/);
  const size = Math.min(180, Math.floor(940 / (a.length * 0.56)));
  return `<template>
<style>
#root { position: absolute; inset: 0; }
#hook-scrim { position: absolute; left: 0; top: 0; width: 1080px; height: 1100px; background: linear-gradient(180deg, rgba(0,0,0,0.75) 0%, rgba(0,0,0,0.45) 55%, rgba(0,0,0,0) 100%); }
#hook-box { position: absolute; left: 60px; top: 330px; width: 860px; text-align: center; transform-origin: 50% 50%; }
#hook-year { font-family: "Playfair Display", serif; font-weight: 900; font-size: ${size}px; line-height: 1; color: #fff; text-shadow: 0 0 40px ${pal.accent}aa, 0 6px 20px rgba(0,0,0,0.8); }
#hook-line { width: 520px; height: 6px; margin: 34px auto 30px; background: ${pal.accent}; box-shadow: 0 0 24px ${pal.accent}; transform-origin: 50% 50%; }
#hook-place { font-family: "Montserrat", sans-serif; font-weight: 800; font-size: 68px; letter-spacing: 0.22em; color: ${pal.accent2}; text-transform: uppercase; text-shadow: 0 4px 16px rgba(0,0,0,0.9); }
</style>
<div id="root" data-composition-id="hook" data-width="${FW}" data-height="${FH}">
  <div id="hook-scrim"></div>
  <div id="hook-box">
    <div id="hook-year">${esc(a)}</div>
    <div id="hook-line"></div>
    <div id="hook-place">${esc(b || "")}</div>
  </div>
</div>
<script>
(function () {
  const tl = gsap.timeline({ paused: true });
  tl.fromTo("#hook-box", { scale: 1.14, y: 0, opacity: 1 }, { scale: 1, duration: 0.7, ease: "power3.out" }, 0);
  tl.fromTo("#hook-line", { scaleX: 0.1 }, { scaleX: 1, duration: 0.5, ease: "power2.out" }, 0.05);
  tl.fromTo("#hook-place", { scale: 1.25, opacity: 0.6 }, { scale: 1, opacity: 1, duration: 0.9, ease: "power3.out" }, 0);
  tl.to("#hook-box", { opacity: 0, y: -40, duration: 0.4, ease: "power2.in" }, 1.75);
  tl.fromTo("#hook-scrim", { opacity: 1 }, { opacity: 0, duration: 0.45, ease: "power1.in" }, 1.7);
  window.__timelines["hook"] = tl;
})();
</script>
</template>
`;
}

// ------------------------------------------------------------------ Endkarte
function endcardHtml(script, pal, dur) {
  // "Teil 2 folgt" -> groß "Teil 2", klein "folgt"; sonst letztes Wort klein ("Neue Geschichte" / "morgen")
  const words = script.endkarte.trim().split(/\s+/);
  const m = /^(.*?\d+)\s+(.*)$/.exec(script.endkarte) || [null, words.length > 1 ? words.slice(0, -1).join(" ") : words[0], words.length > 1 ? words[words.length - 1] : ""];
  const bigSize = Math.min(210, Math.floor(920 / (Math.max(...m[1].split(" ").map((w) => w.length)) * 0.56)));
  return `<template>
<style>
#root { position: absolute; inset: 0; }
#end-dim { position: absolute; inset: 0; background: radial-gradient(ellipse at 50% 40%, rgba(0,0,0,0.55), rgba(0,0,0,0.92)); }
#end-box { position: absolute; left: 60px; top: 560px; width: 860px; text-align: center; transform-origin: 50% 50%; }
#end-big { font-family: "Playfair Display", serif; font-weight: 900; font-size: ${bigSize}px; line-height: 1; color: #fff; text-shadow: 0 0 50px ${pal.accent}99, 0 6px 20px #000; }
#end-small { font-family: "Montserrat", sans-serif; font-weight: 800; font-size: 82px; letter-spacing: 0.18em; text-transform: uppercase; color: ${pal.accent}; margin-top: 18px; }
#end-cta { font-family: "Montserrat", sans-serif; font-weight: 600; font-size: 38px; color: #e8e2d8; margin-top: 56px; }
</style>
<div id="root" data-composition-id="endcard" data-width="${FW}" data-height="${FH}">
  <div id="end-dim"></div>
  <div id="end-box">
    <div id="end-big">${esc(m[1])}</div>
    <div id="end-small">${esc(m[2])}</div>
    <div id="end-cta">Folgen, um ihn nicht zu verpassen</div>
  </div>
</div>
<script>
(function () {
  const tl = gsap.timeline({ paused: true });
  tl.fromTo("#end-dim", { opacity: 0 }, { opacity: 1, duration: 0.35, ease: "power1.out" }, 0);
  tl.fromTo("#end-box", { scale: 1.25, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.45, ease: "power3.out" }, 0.08);
  tl.fromTo("#end-cta", { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.4, ease: "power2.out" }, 0.55);
  tl.fromTo("#end-box", { y: 0 }, { y: -18, duration: ${r3(Math.max(0.5, dur - 0.5))}, ease: "none" }, 0.5);
  window.__timelines["endcard"] = tl;
})();
</script>
</template>
`;
}

// ------------------------------------------------------------------ Untertitel
function captionGroups(words, sentences) {
  // Satzzeichen pro Wort aus dem Originaltext
  const punct = [];
  sentences.forEach((s, si) => tokensWithPunct(s).forEach((t) => punct.push({ si, raw: t })));
  const groups = [];
  let cur = [];
  words.forEach((w, i) => {
    const raw = (punct.find((p, k) => k === i) || {}).raw || w.text;
    cur.push({ ...w, raw });
    const next = words[i + 1];
    const brk = !next || next.satz !== w.satz || next.start - w.end > 0.18 || /[,:;–]$/.test(raw) || cur.length >= 3;
    if (brk) { groups.push(cur); cur = []; }
  });
  return groups;
}

function captionsHtml(plan, pal, dur) {
  const groups = captionGroups(plan.captionWords, plan.sentences);
  let html = "", js = "";
  groups.forEach((gw, gi) => {
    const start = r3(Math.max(0.1, gw[0].start - 0.06));
    const nextStart = gi < groups.length - 1 ? groups[gi + 1][0].start - 0.06 : gw[gw.length - 1].end + 0.5;
    const end = r3(Math.min(nextStart, gw[gw.length - 1].end + 0.6, dur));
    const longest = Math.max(...gw.map((w) => w.text.length));
    const total = gw.reduce((a, w) => a + w.text.length + 1, 0);
    const size = Math.max(58, Math.min(92, Math.floor(820 / (Math.max(longest, total / 2) * 0.66))));
    const gid = `cap-g${gi}`;
    html += `<div id="${gid}" class="clip cap-group" data-start="${start}" data-duration="${r3(end - start)}" data-track-index="0"><div id="${gid}-i" class="cap-inner" style="font-size:${size}px">` +
      gw.map((w, wi) => `<span id="${gid}-w${wi}" class="cap-w">${esc(w.raw.replace(/[,.:;–]+$/, ""))}</span>`).join(" ") + `</div></div>\n`;
    js += `tl.fromTo("#${gid}-i", {opacity:0, y:18, scale:0.96}, {opacity:1, y:0, scale:1, duration:0.12, ease:"power2.out"}, ${start});\n`;
    gw.forEach((w, wi) => {
      const ws = r3(Math.max(start, w.start));
      const we = r3(Math.max(ws + 0.1, Math.min(end - 0.02, wi < gw.length - 1 ? gw[wi + 1].start : w.end + 0.15)));
      js += `tl.fromTo("#${gid}-w${wi}", {color:"#ffffff", scale:1}, {color:"${pal.accent}", scale:1.1, duration:0.08, ease:"power2.out"}, ${ws});\n`;
      js += `tl.to("#${gid}-w${wi}", {color:"#ffffff", scale:1, duration:0.1, ease:"power1.out"}, ${we});\n`;
    });
    js += `tl.to("#${gid}-i", {opacity:0, duration:0.1, ease:"power2.in"}, ${r3(end - 0.1)});\n`;
  });
  return `<template>
<style>
#root { position: absolute; inset: 0; }
.cap-group { position: absolute; left: 50px; top: 1120px; width: 860px; height: 260px; display: flex; align-items: center; justify-content: center; text-align: center; overflow: visible; }
.cap-inner { font-family: "Montserrat", sans-serif; font-weight: 900; line-height: 1.08; color: #fff; -webkit-text-stroke: 14px #000; paint-order: stroke fill; text-shadow: 0 8px 22px rgba(0,0,0,0.7); }
.cap-w { display: inline-block; transform-origin: 50% 60%; margin: 0 0.13em; }
</style>
<div id="root" data-composition-id="captions" data-width="${FW}" data-height="${FH}">
${html}</div>
<script>
(function () {
  const tl = gsap.timeline({ paused: true });
${js}  window.__timelines["captions"] = tl;
})();
</script>
</template>
`;
}

// ------------------------------------------------------------------ Filmkorn + Vignette
function fxHtml(dur) {
  return `<template>
<style>
#root { position: absolute; inset: 0; pointer-events: none; }
#fx-vig { position: absolute; inset: 0; background: radial-gradient(ellipse 75% 62% at 50% 45%, rgba(0,0,0,0) 55%, rgba(0,0,0,0.78) 100%); }
#fx-grain { position: absolute; left: 0; top: 0; width: ${FW}px; height: ${FH}px; opacity: 0.11; mix-blend-mode: overlay; }
</style>
<div id="root" data-composition-id="fx" data-width="${FW}" data-height="${FH}">
  <div id="fx-vig"></div>
  <canvas id="fx-grain" width="540" height="960"></canvas>
</div>
<script>
${RUNTIME}
(function () {
  const tl = gsap.timeline({ paused: true });
  const cv = document.getElementById("fx-grain");
  const ctx = cv.getContext("2d");
  const tiles = [];
  for (let k = 0; k < 4; k++) {
    const rnd = hfMulberry(1000 + k);
    const tile = document.createElement("canvas");
    tile.width = 270; tile.height = 270;
    const tc = tile.getContext("2d");
    const img = tc.createImageData(270, 270);
    for (let i = 0; i < img.data.length; i += 4) {
      const v = Math.floor(rnd() * 255);
      img.data[i] = img.data[i + 1] = img.data[i + 2] = v; img.data[i + 3] = 255;
    }
    tc.putImageData(img, 0, 0);
    tiles.push(tile);
  }
  function render(t) {
    const fr = Math.floor(t * 30);
    const tile = tiles[fr % 4];
    const ox = (fr * 97) % 270, oy = (fr * 61) % 270;
    for (let x = -ox; x < 540; x += 270) for (let y = -oy; y < 960; y += 270) ctx.drawImage(tile, x, y);
  }
  const P = { t: 0 };
  tl.to(P, { t: ${dur}, duration: ${dur}, ease: "none", onUpdate: () => render(P.t) }, 0);
  render(0);
  window.__timelines["fx"] = tl;
})();
</script>
</template>
`;
}

// ------------------------------------------------------------------ Projekt
export function writeProject({ script, plan, projDir, audioFile }) {
  const pal = palette(script.epoche);
  fs.mkdirSync(path.join(projDir, "compositions"), { recursive: true });
  fs.mkdirSync(path.join(projDir, "assets"), { recursive: true });
  const events = [];
  const hosts = [];
  let z = 1;
  plan.scenes.forEach((s, i) => {
    const { html, slot, events: ev } = sceneHtml(script, plan, s, i, pal);
    for (const e of ev) if (!events.some((x) => x.typ === e.typ && Math.abs(x.t - e.t) < 0.01)) events.push(e);
    fs.writeFileSync(path.join(projDir, "compositions", `${s.id}.html`), html);
    hosts.push(`<div id="${s.id}" data-composition-id="${s.id}" data-composition-src="compositions/${s.id}.html" data-start="${s.start}" data-duration="${slot}" data-track-index="1" data-track-kind="graphics" data-width="${FW}" data-height="${FH}" style="z-index:${z++}"></div>`);
  });
  const D = plan.duration;
  fs.writeFileSync(path.join(projDir, "compositions", "fx.html"), fxHtml(D));
  hosts.push(`<div id="fx" data-composition-id="fx" data-composition-src="compositions/fx.html" data-start="0" data-duration="${D}" data-track-index="2" data-track-kind="graphics" data-width="${FW}" data-height="${FH}" style="z-index:${z++}"></div>`);
  fs.writeFileSync(path.join(projDir, "compositions", "hook.html"), hookHtml(script, pal));
  hosts.push(`<div id="hook" data-composition-id="hook" data-composition-src="compositions/hook.html" data-start="0" data-duration="${plan.hookEnd}" data-track-index="3" data-track-kind="graphics" data-width="${FW}" data-height="${FH}" style="z-index:${z++}"></div>`);
  if (plan.hasEndcard) {
    const ed = r3(D - plan.endcardStart);
    fs.writeFileSync(path.join(projDir, "compositions", "endcard.html"), endcardHtml(script, pal, ed));
    hosts.push(`<div id="endcard" data-composition-id="endcard" data-composition-src="compositions/endcard.html" data-start="${plan.endcardStart}" data-duration="${ed}" data-track-index="4" data-track-kind="graphics" data-width="${FW}" data-height="${FH}" style="z-index:${z + 1}"></div>`);
  }
  fs.writeFileSync(path.join(projDir, "compositions", "captions.html"), captionsHtml(plan, pal, D));
  hosts.push(`<div id="captions" data-composition-id="captions" data-composition-src="compositions/captions.html" data-start="0" data-duration="${D}" data-track-index="5" data-track-kind="captions" data-width="${FW}" data-height="${FH}" style="z-index:${z++}"></div>`);

  const index = `<!doctype html>
<html lang="de">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=${FW}, height=${FH}" />
    <title>${esc(script.titel)}</title>
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      * { margin: 0; padding: 0; box-sizing: border-box; }
      html, body { width: ${FW}px; height: ${FH}px; overflow: hidden; background: #000; }
      #root { position: relative; width: ${FW}px; height: ${FH}px; overflow: hidden; background: #000; }
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="${D}" data-width="${FW}" data-height="${FH}">
      ${hosts.join("\n      ")}
      <audio id="mix" class="clip" src="assets/${path.basename(audioFile)}" data-start="0" data-duration="${D}" data-track-index="6" data-volume="1"></audio>
    </div>
    <script>
      window.__timelines = window.__timelines || {};
      window.__timelines["main"] = gsap.timeline({ paused: true });
    </script>
  </body>
</html>
`;
  fs.writeFileSync(path.join(projDir, "index.html"), index);
  fs.writeFileSync(path.join(projDir, "hyperframes.json"), JSON.stringify({
    $schema: "https://hyperframes.heygen.com/schema/hyperframes.json",
    paths: { blocks: "compositions", components: "compositions/components", assets: "assets" },
    media: { autoProxy: true },
    authoringSkill: "hyperframes",
  }, null, 2));
  fs.writeFileSync(path.join(projDir, "meta.json"), JSON.stringify({ id: script.id, name: script.titel }, null, 2));
  return { events };
}
