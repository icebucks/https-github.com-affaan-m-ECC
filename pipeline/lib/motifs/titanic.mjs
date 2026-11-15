// Motive Titanic (1912): Stahlblau + Kesselorange.
import { CW, CH, svg, linGrad, rect, g, path, poly } from "../svg.mjs";
import { person, bustCivil, rimmed, rimFilter, boilerFront, chandelier } from "../figures.mjs";

const bg = (id, stops) => svg(rect(`url(#${id})`), { defs: linGrad(id, stops) });
const stoker = (c) => person(c, { hat: "kappe", tool: "schaufel", dress: "hose" });

function pipes(c, r) {
  let s = "";
  for (let i = 0; i < 6; i++) {
    const y = 200 + i * 90 + r() * 30;
    s += `<rect x="-40" y="${y}" width="${CW + 80}" height="${22 + r() * 18}" fill="${c}"/>`;
    for (let k = 0; k < 6; k++) s += `<rect x="${k * 230 + r() * 60}" y="${y - 8}" width="16" height="${48}" fill="${c}"/>`;
  }
  return s;
}
function plates(c, rivet, { cols = 4, rows = 7, x0 = -40, y0 = -40, w = 340, h = 340 } = {}) {
  let s = "";
  for (let i = 0; i < cols; i++) for (let j = 0; j < rows; j++) {
    const x = x0 + i * w, y = y0 + j * h;
    s += `<rect x="${x}" y="${y}" width="${w - 6}" height="${h - 6}" fill="${c}"/>`;
    for (let k = 0; k < 8; k++) s += `<circle cx="${x + 18 + k * ((w - 36) / 7)}" cy="${y + 16}" r="6" fill="${rivet}"/><circle cx="${x + 16}" cy="${y + 18 + k * ((h - 36) / 7)}" r="6" fill="${rivet}"/>`;
  }
  return s;
}

export const motifs = {
  kessel(ctx) {
    const { pal, r, sid } = ctx;
    const rim = `${sid}-rim`;
    return {
      layers: [
        { name: "sky", depth: 0, svg: bg(`${sid}-bg`, ["#05090d", "#0d1824", "#111c28"]) },
        { name: "pipes", depth: 0.15, svg: svg(pipes(pal.mid, r), { blur: 3, id: `${sid}-p` }) },
        { name: "boilers", depth: 0.35, svg: svg(g(boilerFront(pal.mid, pal.accent, pal.cold), { x: 230, y: 1150, s: 1.0 }) + g(boilerFront(pal.mid, pal.accent, pal.cold), { x: 1030, y: 1150, s: 1.0 }) + rect(pal.near, -40, 1480, CW + 80, 900)) },
        { name: "hero", depth: 0.8, svg: svg(g(rimmed(stoker, pal.fg, pal.accent, rim, -10, -4), { x: 560, y: 2330, s: 2.9 }) + rect(pal.fg, -40, 2290, CW + 80, 200), { defs: rimFilter(rim, 7) }) },
      ],
      lights: [
        { x: 230, y: 1300, r: 700, color: pal.accent, intensity: 0.8, flicker: true },
        { x: 1030, y: 1300, r: 700, color: pal.accent, intensity: 0.75, flicker: true },
      ],
      fxBack: [{ type: "rauch", count: 8, region: [0, 1500, CW], speed: 60, size: 260, alpha: 0.25, rgb: "30,30,34" }],
      fxFront: [{ type: "funken", count: 70, region: [80, 1300, 920, 200], speed: 170, size: 3 }, { type: "staub", count: 80, alpha: 0.3, color: "rgba(140,140,150,1)" }],
      camera: { from: { scale: 1.08, x: -40, y: 0 }, to: { scale: 1.0, x: 40, y: -20 } },
    };
  },

  russgesicht(ctx) {
    const { pal, sid } = ctx;
    const rim = `${sid}-rim`;
    const hero = (c) => bustCivil(c, { cap: "stoker" }) + `<rect x="40" y="790" width="560" height="500" fill="${c}"/>`;
    // Rußspuren als feine helle Kratzer auf der Wange (nur angedeutet)
    return {
      layers: [
        { name: "sky", depth: 0, svg: bg(`${sid}-bg`, ["#04070a", "#0b1520", "#0f1b28"]) },
        { name: "hero", depth: 0.8, svg: svg(g(rimmed(hero, pal.fg, pal.accent, rim, -14, -2), { x: 360, y: 520, s: 1.6 }), { defs: rimFilter(rim, 8) }) },
      ],
      lights: [
        { x: 0, y: 1100, r: 1000, color: pal.accent, intensity: 0.85, flicker: true, fast: true },
        { x: 1100, y: 500, r: 700, color: pal.cold, intensity: 0.12 },
      ],
      fxBack: [],
      fxFront: [{ type: "staub", count: 160, alpha: 0.5, size: 2.2, color: "rgba(60,60,64,1)" }, { type: "funken", count: 30, region: [0, 1300, 300, 300], speed: 140, drift: 60, size: 3 }],
      camera: { from: { scale: 1.0, x: 0, y: 0 }, to: { scale: 1.1, x: -30, y: 20 } },
    };
  },

  oben_luxus(ctx) {
    const { pal, r, sid } = ctx;
    // Prunktreppe mit Geländer und Kronleuchter – warm und leer
    let rail = "";
    for (let i = 0; i < 14; i++) rail += `<rect x="${140 + i * 30}" y="${1620 - i * 34}" width="9" height="150" fill="#2a1a0c"/>`;
    for (let i = 0; i < 14; i++) rail += `<rect x="${1110 - i * 30}" y="${1620 - i * 34}" width="9" height="150" fill="#2a1a0c"/>`;
    const stairs = poly([[100, 2400], [560, 1150], [700, 1150], [1160, 2400]], "#3a2410") +
      path(`M130,1640 L560,1160`, "none", `stroke="#2a1a0c" stroke-width="16"`) + path(`M1130,1640 L700,1160`, "none", `stroke="#2a1a0c" stroke-width="16"`) + rail;
    let steps = "";
    for (let i = 0; i < 18; i++) steps += `<rect x="${560 - i * 26}" y="${1160 + i * 68}" width="${140 + i * 52}" height="6" fill="#5a3a18" opacity="0.7"/>`;
    const dome = path(`M240,700 C300,320 960,320 1020,700Z`, "#c8a060", `opacity="0.35"`);
    return {
      layers: [
        { name: "sky", depth: 0, svg: bg(`${sid}-bg`, ["#1a0f06", "#4a2e12", "#6b4520"]) },
        { name: "dome", depth: 0.1, svg: svg(dome + rect("#2a1a0c", 0, 690, CW, 40), { blur: 2, id: `${sid}-d` }) },
        { name: "stairs", depth: 0.4, svg: svg(stairs + steps) },
        { name: "chand", depth: 0.7, svg: svg(g(chandelier("#1a0f06", pal.accent2), { x: 630, y: 760, s: 1.4 })) },
      ],
      lights: [
        { x: 630, y: 820, r: 900, color: pal.accent2, intensity: 0.6, flicker: false },
        { x: 630, y: 1500, r: 900, color: "#ffcf80", intensity: 0.25 },
      ],
      fxBack: [],
      fxFront: [{ type: "staub", count: 90, alpha: 0.55, size: 2.4, color: "rgba(255,225,170,1)" }],
      camera: { from: { scale: 1.0, x: 0, y: -60 }, to: { scale: 1.08, x: 0, y: 40 } },
    };
  },

  kessel_schaufeln(ctx) {
    const { pal, sid } = ctx;
    const rim = `${sid}-rim`;
    const coal = path(`M-60,2400 L-60,1950 C100,1880 260,1900 420,1980 C520,2040 600,2150 640,2400Z`, pal.fg);
    // Schaufel als eigenes Objekt (schwingt im Takt)
    const shovel = `<rect x="0" y="-8" width="420" height="16" rx="6" fill="${pal.fg}"/><path d="M400,-50 L520,-40 L530,40 L400,50Z" fill="${pal.fg}"/>`;
    const swings = Math.max(1, Math.floor(ctx.dur / 1.1));
    return {
      layers: [
        { name: "sky", depth: 0, svg: bg(`${sid}-bg`, ["#05090d", "#0b1520", "#101b27"]) },
        { name: "boiler", depth: 0.3, svg: svg(g(boilerFront(pal.mid, pal.accent, pal.cold), { x: 760, y: 1150, s: 1.5 })) },
        { name: "hero", depth: 0.7, svg: svg(g(rimmed((c) => person(c, { hat: "kappe", dress: "hose", arms: "swing", pose: "walk", phase: 1 }), pal.fg, pal.accent, rim, -10, 0), { x: 280, y: 2250, s: 2.2 }) + coal, { defs: rimFilter(rim, 7) }) },
      ],
      objects: [{ name: "shovel", w: 540, h: 120, vb: "0 -60 540 120", svg: shovel }],
      anims: [
        `tl.fromTo("#${sid}-shovel", {x:380, y:1640, rotation:30, transformOrigin:"0% 50%"}, {rotation:-25, x:460, y:1560, duration:0.55, ease:"power2.inOut", repeat:${swings * 2 - 1}, yoyo:true}, 0);`,
      ],
      lights: [
        { x: 760, y: 1400, r: 900, color: pal.accent, intensity: 0.9, flicker: true, fast: true },
        { x: 760, y: 1400, r: 400, color: pal.accent2, intensity: 0.5, flicker: true, fast: true },
      ],
      fxBack: [],
      fxFront: [{ type: "funken", count: 90, region: [500, 1300, 520, 200], speed: 220, drift: -30, size: 3.2 }],
      camera: { from: { scale: 1.0, x: 0, y: 0 }, to: { scale: 1.08, x: 20, y: 0 } },
    };
  },

  bordwand(ctx) {
    const { pal, r, sid } = ctx;
    const t7 = Math.max(0.6, ctx.satz(7));
    return {
      layers: [
        { name: "hull", depth: 0.3, svg: svg(plates(pal.near, pal.far)) },
        { name: "frames", depth: 0.6, svg: svg([0, 1, 2].map((i) => `<rect x="${120 + i * 480}" y="-60" width="70" height="${CH + 120}" fill="${pal.fg}"/>`).join("")) },
      ],
      anims: [
        // Ruck: Kamera springt; die Bordwand wölbt sich während des Kratzens nach innen
        `tl.fromTo("#${sid}-L-hull", {scaleX:1, scaleY:1, transformOrigin:"20% 50%"}, {scaleX:1.04, scaleY:1.02, duration:${(ctx.dur - t7).toFixed(2)}, ease:"power2.in"}, ${t7.toFixed(2)});`,
        `tl.fromTo("#${sid}-dark", {opacity:0}, {opacity:0.55, duration:0.08, yoyo:true, repeat:5, ease:"none"}, 0.05);`,
      ],
      lights: [
        { x: 640, y: 300, r: 600, color: "#ffe2a8", intensity: 0.35, flicker: true, fast: true },
        { x: 200, y: 1400, r: 800, color: pal.accent, intensity: 0.4, flicker: true },
      ],
      fxBack: [],
      fxFront: [
        { type: "funken", count: 80, region: [100, 900, 900, 700], speed: 60, drift: 140, size: 3.4, ramp: [t7, t7 + 0.4, 0, 1] },
        { type: "staub", count: 120, alpha: 0.4, color: "rgba(150,160,170,1)" },
      ],
      camera: { from: { scale: 1.12, x: 0, y: 0 }, to: { scale: 1.02, x: 0, y: 0 }, ease: "power3.out" },
      shake: 10,
      events: [{ dt: 0.02, typ: "boom", gain: 0.6 }, { dt: t7, typ: "kratzen", gain: 0.8 }],
    };
  },

  wassereinbruch(ctx) {
    const { pal, sid } = ctx;
    const rim = `${sid}-rim`;
    const water = `<rect x="0" y="0" width="1260" height="900" fill="#0e2a3d" opacity="0.92"/><rect x="0" y="0" width="1260" height="10" fill="${pal.cold}" opacity="0.7"/>`;
    return {
      layers: [
        { name: "hull", depth: 0.2, svg: svg(plates(pal.near, pal.far, { x0: -40, y0: -40 }) + path(`M760,1180 L1300,1120 L1300,1200 L760,1210Z`, "#000")) },
        { name: "hero", depth: 0.7, svg: svg(g(rimmed((c) => person(c, { hat: "kappe", dress: "hose", arms: "up" }), pal.fg, pal.cold, rim, 8, -6), { x: 330, y: 2200, s: 2.0, rot: -6 }), { defs: rimFilter(rim, 6) }) },
      ],
      objects: [{ name: "water", w: 1260, h: 900, svg: water }],
      anims: [`tl.fromTo("#${sid}-water", {x:0, y:2240}, {y:1820, duration:${ctx.dur}, ease:"power1.in"}, 0);`],
      lights: [
        { x: 900, y: 1200, r: 700, color: pal.cold, intensity: 0.45, flicker: true, fast: true },
        { x: 0, y: 1600, r: 900, color: pal.accent, intensity: 0.35, flicker: true },
      ],
      fxBack: [],
      fxFront: [
        { type: "gischt", count: 260, origin: [880, 1050], dir: 190, spread: 0.5, speed: 1500, size: 5, alpha: 0.75, color: "rgba(200,225,240,1)" },
        { type: "gischt", count: 120, origin: [880, 1080], dir: 160, spread: 0.9, speed: 900, size: 3, alpha: 0.6, color: "rgba(220,240,250,1)" },
      ],
      camera: { from: { scale: 1.04, x: 0, y: 0 }, to: { scale: 1.12, x: 30, y: 0 } },
      shake: 5,
      events: [{ dt: 0.05, typ: "einbruch", gain: 0.8 }],
    };
  },

  stahltuer(ctx) {
    const { pal, sid } = ctx;
    const rim = `${sid}-rim`;
    const t10 = Math.max(0.4, ctx.satz(10));
    const frame = path(`M-60,-60 L1320,-60 L1320,2400 L-60,2400Z M380,700 L880,700 L880,1800 L380,1800Z`, pal.near, `fill-rule="evenodd"`);
    const beyond = rect("#2a1408", 380, 700, 500, 1100) + rect(pal.accent, 380, 700, 500, 1100, `opacity="0.35"`);
    const door = `<rect x="0" y="0" width="520" height="1120" fill="${pal.fg}"/>` + [0, 1, 2, 3].map((i) => `<rect x="20" y="${60 + i * 260}" width="480" height="18" fill="${pal.far}" opacity="0.6"/>`).join("");
    const doorTime = Math.max(1.2, ctx.dur - t10 - 0.3);
    return {
      layers: [
        { name: "beyond", depth: 0.1, svg: svg(beyond) },
        { name: "frame", depth: 0.3, svg: svg(frame) },
        { name: "hero", depth: 0.8, svg: svg(g(rimmed((c) => person(c, { hat: "kappe", dress: "hose" }), pal.fg, "#ff3b2f", rim, 0, -6), { x: 630, y: 2400, s: 2.6, flip: true }), { defs: rimFilter(rim, 8) }) },
      ],
      objects: [{ name: "door", w: 520, h: 1120, svg: door, before: "frame" }],
      anims: [
        `tl.fromTo("#${sid}-door", {x:370, y:-480}, {y:-480, duration:${t10.toFixed(2)}, ease:"none"}, 0);`,
        `tl.to("#${sid}-door", {y:690, duration:${doorTime.toFixed(2)}, ease:"power1.inOut"}, ${t10.toFixed(2)});`,
        `tl.fromTo("#${sid}-light0", {scale:1}, {scale:1.15, duration:0.35, ease:"sine.inOut", yoyo:true, repeat:${Math.max(1, Math.floor(ctx.dur / 0.35) - 1)}}, 0);`,
      ],
      lights: [
        { x: 630, y: 400, r: 800, color: "#ff2a1a", intensity: 0.55, flicker: true, fast: true },
        { x: 630, y: 1300, r: 600, color: pal.accent, intensity: 0.4, flicker: true },
      ],
      fxBack: [],
      fxFront: [{ type: "gischt", count: 120, origin: [1100, 1700], dir: 200, spread: 0.6, speed: 700, size: 4, alpha: 0.5 }, { type: "staub", count: 60, alpha: 0.3, color: "rgba(160,170,180,1)" }],
      camera: { from: { scale: 1.0, x: 0, y: 0 }, to: { scale: 1.15, x: 0, y: -60 }, ease: "power1.in" },
      shake: 2.5,
      events: [{ dt: 0.05, typ: "glocke", gain: 0.45 }, { dt: t10 + 0.1, typ: "boom", gain: 0.4 }],
    };
  },
};
