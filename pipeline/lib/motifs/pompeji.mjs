// Motive Pompeji (79 n. Chr.): Ocker + Aschgrau + Glutrot.
import { CW, CH, svg, linGrad, rect, hills, g, path, poly } from "../svg.mjs";
import { person, bustCivil, rimmed, rimFilter, millstone, loaf, amphora } from "../figures.mjs";

const sky = (id, stops) => svg(rect(`url(#${id})`), { defs: linGrad(id, stops) });
const night = (pal) => ["#0c0705", "#1e120b", "#2c1a10"];
const dark = (pal) => ["#1a1512", "#3a322c", "#4d433a"];
const baker = (c) => person(c, { tool: "brotschieber" });

// Vesuv: breiter Kegel mit zwei Gipfeln (Monte Somma)
function vesuv(c, y = 1250) {
  return path(`M-80,${y + 300} L150,${y + 40} C300,${y - 120} 420,${y - 260} 520,${y - 300} L600,${y - 270} L680,${y - 330} C800,${y - 250} 960,${y - 80} 1340,${y + 120} L1340,${y + 400}Z`, c);
}
// Dächer und Fassaden einer römischen Kleinstadt
function town(c, y, r, { n = 14, h = 220 } = {}) {
  let s = "";
  let x = -60;
  while (x < CW + 60) {
    const w = 90 + r() * 140, hh = h * (0.5 + r() * 0.6);
    s += `<rect x="${x}" y="${y - hh}" width="${w}" height="${hh + 400}" fill="${c}"/>`;
    if (r() > 0.4) s += poly([[x - 6, y - hh], [x + w / 2, y - hh - 36], [x + w + 6, y - hh]], c);
    if (r() > 0.7) s += `<rect x="${x + w * 0.3}" y="${y - hh - 70}" width="18" height="70" fill="${c}"/>`;
    x += w + 6;
  }
  return s;
}
function columns(c, x0, n, gap, y, h) {
  let s = `<rect x="${x0 - 30}" y="${y - h - 40}" width="${n * gap + 40}" height="44" fill="${c}"/>`;
  for (let i = 0; i < n; i++) s += `<rect x="${x0 + i * gap}" y="${y - h}" width="30" height="${h}" fill="${c}"/><rect x="${x0 + i * gap - 8}" y="${y - h}" width="46" height="14" fill="${c}"/>`;
  return s;
}

export const motifs = {
  ofenglut(ctx) {
    const { pal, r, sid } = ctx;
    const rim = `${sid}-rim`;
    // Kuppelofen aus Ziegeln mit glühender Öffnung
    const oven = path(`M120,1900 L120,1350 C120,1050 820,1050 820,1350 L820,1900Z`, pal.near) +
      path(`M330,1900 L330,1560 C330,1420 610,1420 610,1560 L610,1900Z`, pal.accent) +
      path(`M370,1900 L370,1600 C370,1500 570,1500 570,1600 L570,1900Z`, pal.accent2, `opacity="0.85"`);
    let bricks = "";
    for (let row = 0; row < 9; row++) for (let k = 0; k < 7; k++) bricks += `<rect x="${140 + k * 98 + (row % 2) * 48}" y="${1380 + row * 58}" width="88" height="48" fill="none" stroke="${pal.mid}" stroke-width="4" opacity="0.6"/>`;
    return {
      layers: [
        { name: "sky", depth: 0, svg: sky(`${sid}-sky`, night(pal)) },
        { name: "mill", depth: 0.2, svg: svg(g(millstone(pal.mid), { x: 1050, y: 1700, s: 1.3 }) + rect(pal.mid, 0, 1880, CW, 400), { blur: 4, id: `${sid}-mill` }) },
        { name: "oven", depth: 0.4, svg: svg(oven + bricks) },
        { name: "hero", depth: 0.8, svg: svg(g(rimmed(baker, pal.fg, pal.accent, rim, -12, -4), { x: 960, y: 2300, s: 2.4, flip: true }), { defs: rimFilter(rim, 7) }) },
      ],
      lights: [
        { x: 470, y: 1700, r: 1000, color: pal.accent, intensity: 0.85, flicker: true },
        { x: 470, y: 1700, r: 420, color: pal.accent2, intensity: 0.5, flicker: true },
      ],
      fxBack: [{ type: "rauch", count: 10, region: [300, 1450, 300], speed: 70, size: 220, alpha: 0.3, rgb: "40,28,20" }],
      fxFront: [{ type: "funken", count: 60, region: [300, 1350, 340, 200], speed: 190, drift: 25, size: 3.4 }],
      camera: { from: { scale: 1.08, x: 30, y: 0 }, to: { scale: 1.0, x: -20, y: -30 } },
    };
  },

  brote(ctx) {
    const { pal, r, sid } = ctx;
    let loaves = "";
    const pos = [[230, 1480, 1.1], [470, 1440, 1.0], [720, 1470, 1.15], [960, 1430, 1.0], [350, 1620, 1.3], [640, 1600, 1.35], [920, 1630, 1.25]];
    for (const [x, y, s] of pos) loaves += g(loaf(pal.near, pal.accent2), { x, y, s });
    return {
      layers: [
        { name: "sky", depth: 0, svg: sky(`${sid}-sky`, night(pal)) },
        { name: "wall", depth: 0.2, svg: svg(g(amphora(pal.mid), { x: 200, y: 1250, s: 1.4 }) + g(amphora(pal.mid), { x: 360, y: 1250, s: 1.2 }) + g(millstone(pal.mid), { x: 1000, y: 1300, s: 1.0 }), { blur: 5, id: `${sid}-wall` }) },
        { name: "counter", depth: 0.6, svg: svg(loaves + rect(pal.fg, -40, 1680, CW + 80, 700) + rect(pal.near, -40, 1670, CW + 80, 26)) },
      ],
      lights: [
        { x: -40, y: 1500, r: 1100, color: pal.accent, intensity: 0.8, flicker: true },
        { x: 600, y: 1450, r: 700, color: pal.accent2, intensity: 0.25, flicker: true },
      ],
      fxBack: [],
      fxFront: [{ type: "staub", count: 90, alpha: 0.45, size: 2.6, color: "rgba(255,210,150,1)" }],
      camera: { from: { scale: 1.12, x: -60, y: 0 }, to: { scale: 1.02, x: 50, y: 20 } },
    };
  },

  gasse(ctx) {
    const { pal, r, sid } = ctx;
    // Straße mit Trittsteinen, Fassaden links/rechts, Vesuv am Ende
    const street = path(`M380,2400 L600,1320 L680,1320 L900,2400Z`, pal.mid);
    const stones = [0, 1, 2].map((k) => `<ellipse cx="${560 + k * 60}" cy="1900" rx="34" ry="16" fill="${pal.near}"/>`).join("");
    let left = path(`M-60,2400 L-60,700 L580,1250 L580,1330 L380,2400Z`, pal.mid) + [0, 1, 2].map((i) => `<rect x="${60 + i * 150}" y="${1150 + i * 90}" width="60" height="${110 - i * 20}" fill="${pal.accent2}" opacity="0.35"/>`).join("");
    let right = path(`M1320,2400 L1320,700 L700,1250 L700,1330 L900,2400Z`, pal.mid);
    let people = g(person(pal.fg, { dress: "stola", hat: "tuch" }), { x: 280, y: 2050, s: 1.0 }) +
      g(person(pal.fg, { pose: "walk", phase: 1 }), { x: 980, y: 2080, s: 1.05, flip: true }) +
      g(amphora(pal.fg), { x: 140, y: 2120, s: 1.1 }) + g(amphora(pal.fg), { x: 210, y: 2130, s: 0.9 }) +
      g(person(pal.near, { pose: "walk", phase: 2 }), { x: 620, y: 1500, s: 0.45 });
    return {
      layers: [
        { name: "sky", depth: 0, svg: sky(`${sid}-sky`, pal.sky) },
        { name: "vesuv", depth: 0.1, svg: svg(vesuv(pal.far, 1150), { blur: 3, id: `${sid}-ves` }) },
        { name: "street", depth: 0.4, svg: svg(street + stones + left + right) },
        { name: "people", depth: 0.7, svg: svg(people) },
      ],
      lights: [{ x: 640, y: 900, r: 900, color: pal.accent2, intensity: 0.3 }],
      fxBack: [{ type: "nebel", count: 6, size: 400, alpha: 0.1, rgb: "200,170,130", y0: 1100, y1: 1500 }],
      fxFront: [{ type: "staub", count: 60, alpha: 0.35, color: "rgba(255,225,180,1)" }],
      camera: { from: { scale: 1.0, x: 0, y: 30 }, to: { scale: 1.1, x: 0, y: -10 } },
      shake: 5,
      shakeFrom: Math.max(0, ctx.satz(2)),
      events: [{ dt: Math.max(0.1, ctx.satz(2)), typ: "beben", gain: 0.7 }],
    };
  },

  vesuv_wolke(ctx) {
    const { pal, r, sid } = ctx;
    // Aschesäule: Stamm + schirmförmige Krone („wie ein Baum“) – wächst über die Szene
    const cloud = `<path d="M560,1000 C540,800 590,600 600,420 C470,400 330,330 300,230 C280,120 420,60 520,90 C560,10 700,10 740,90 C860,50 980,130 940,240 C910,330 760,390 660,420 C670,600 720,800 700,1000Z" fill="#2b2420"/>` +
      `<path d="M600,420 C480,390 380,330 360,250 C430,300 520,330 620,330Z" fill="#4a3e35" opacity="0.7"/>`;
    return {
      layers: [
        { name: "sky", depth: 0, svg: sky(`${sid}-sky`, ["#3b2c22", "#8a6440", "#c08a50"]) },
        { name: "vesuv", depth: 0.15, svg: svg(vesuv(pal.mid, 1300)) },
        { name: "town", depth: 0.6, svg: svg(town(pal.fg, 1950, r) + columns(pal.fg, 820, 5, 80, 1950, 260)) },
      ],
      objects: [{ name: "cloud", w: 1260, h: 1100, svg: cloud }],
      anims: [
        `tl.fromTo("#${sid}-cloud", {x:0, y:420, scale:0.25, transformOrigin:"50% 95%"}, {scale:0.88, y:330, duration:${ctx.dur}, ease:"power1.out"}, 0);`,
        `tl.fromTo("#${sid}-L-sky", {filter:"brightness(1)"}, {filter:"brightness(0.45)", duration:${ctx.dur}, ease:"none"}, 0);`,
      ],
      lights: [{ x: 640, y: 1250, r: 700, color: pal.accent, intensity: 0.35, flicker: true }],
      fxBack: [],
      fxFront: [{ type: "asche", count: 60, speed: 50, size: 2.5, alpha: 0.4, sway: 40, color: "rgba(170,160,150,1)", ramp: [ctx.dur * 0.5, ctx.dur, 0, 1] }],
      camera: { from: { scale: 1.0, x: 0, y: 0 }, to: { scale: 1.06, x: 0, y: 40 } },
    };
  },

  ascheregen(ctx) {
    const { pal, r, sid } = ctx;
    const t8 = Math.max(0.5, ctx.satz(8));
    const people = g(person(pal.fg, { pose: "walk", arms: "up", phase: 0.5 }), { x: 380, y: 2060, s: 1.2 }) +
      g(person(pal.fg, { dress: "stola", hat: "tuch", arms: "up" }), { x: 860, y: 2080, s: 1.15, flip: true });
    return {
      layers: [
        { name: "sky", depth: 0, svg: sky(`${sid}-sky`, dark(pal)) },
        { name: "town", depth: 0.3, svg: svg(town(pal.mid, 1500, r, { h: 400 }), { blur: 3, id: `${sid}-town` }) },
        { name: "street", depth: 0.5, svg: svg(columns(pal.near, 60, 4, 150, 1900, 600) + rect(pal.near, -40, 1890, CW + 80, 500)) },
        { name: "people", depth: 0.75, svg: svg(people) },
      ],
      lights: [{ x: 1100, y: 1100, r: 900, color: pal.accent, intensity: 0.35, flicker: true }],
      fxBack: [{ type: "nebel", count: 8, size: 520, alpha: 0.22, rgb: "120,112,104", y0: 900, y1: 1900 }],
      fxFront: [
        { type: "asche", count: 520, speed: 110, size: 3.2, alpha: 0.75, sway: 45, color: "rgba(190,182,172,1)", ramp: [0, t8, 0.35, 1] },
        { type: "steine", rock: true, count: 70, speed: 900, size: 7, alpha: 0.95, sway: 6, color: "rgba(60,52,46,1)", ramp: [t8 - 0.05, t8 + 0.6, 0, 1] },
      ],
      camera: { from: { scale: 1.0, x: 0, y: 0 }, to: { scale: 1.12, x: -20, y: 20 } },
      shake: 3, shakeFrom: t8,
      events: [{ dt: t8 + 0.05, typ: "steine", gain: 0.8 }],
    };
  },

  flucht_hafen(ctx) {
    const { pal, r, sid } = ctx;
    let runners = "";
    for (let i = 0; i < 9; i++) {
      runners += g(person(i < 3 ? pal.fg : pal.near, { pose: "run", arms: "swing", phase: i * 1.7, dress: i % 3 === 1 ? "stola" : "tunika", hat: i % 3 === 1 ? "tuch" : null }), { x: 1100 - i * 120 + r() * 40, y: 2050 - (i > 2 ? 160 : 0) - (i > 5 ? 120 : 0), s: i < 3 ? 1.2 : i < 6 ? 0.8 : 0.55, flip: true, rot: -8 });
    }
    let masts = "";
    for (let i = 0; i < 4; i++) masts += `<rect x="${120 + i * 110}" y="${1300 - i * 30}" width="10" height="400" fill="${pal.mid}"/><path d="M${80 + i * 110},${1700} L${240 + i * 110},${1700} L${210 + i * 110},${1760} L${110 + i * 110},${1760}Z" fill="${pal.mid}"/>`;
    return {
      layers: [
        { name: "sky", depth: 0, svg: sky(`${sid}-sky`, ["#120d0b", "#2c2420", "#3d332c"]) },
        { name: "sea", depth: 0.15, svg: svg(rect("#2a2622", -40, 1700, CW + 80, 600) + masts, { blur: 3, id: `${sid}-sea` }) },
        { name: "runners", depth: 0.65, svg: svg(runners + rect(pal.fg, -40, 2040, CW + 80, 300)) },
      ],
      lights: [{ x: 1260, y: 1000, r: 1000, color: pal.accent, intensity: 0.4, flicker: true }],
      fxBack: [{ type: "nebel", count: 8, size: 520, alpha: 0.2, rgb: "110,100,92", y0: 1200, y1: 1900 }],
      fxFront: [{ type: "asche", count: 600, speed: 140, size: 3.4, alpha: 0.75, sway: 30, color: "rgba(180,172,162,1)" }],
      camera: { from: { scale: 1.06, x: 60, y: 0 }, to: { scale: 1.0, x: -80, y: 0 }, ease: "none" },
      march: { name: "runners", dx: -60 },
      shake: 3,
    };
  },

  baecker_tuer(ctx) {
    const { pal, sid } = ctx;
    const rim = `${sid}-rim`;
    const door = path(`M300,2400 L300,900 C300,760 960,760 960,900 L960,2400Z`, pal.accent) +
      path(`M360,2400 L360,940 C360,840 900,840 900,940 L900,2400Z`, pal.accent2, `opacity="0.35"`);
    const wall = path(`M-60,-60 L1320,-60 L1320,2400 L960,2400 L960,900 C960,760 300,760 300,900 L300,2400 L-60,2400Z`, pal.fg);
    return {
      layers: [
        { name: "inner", depth: 0.1, svg: svg(door + g(millstone(pal.near), { x: 760, y: 1900, s: 1.0 }), { blur: 4, id: `${sid}-in` }) },
        { name: "hero", depth: 0.45, svg: svg(g(rimmed((c) => person(c, {}), pal.fg, pal.accent, rim, 0, -8), { x: 630, y: 2250, s: 2.6 }), { defs: rimFilter(rim, 9) }) },
        { name: "wall", depth: 0.7, svg: svg(wall) },
      ],
      lights: [{ x: 630, y: 1300, r: 900, color: pal.accent, intensity: 0.7, flicker: true }],
      fxBack: [],
      fxFront: [{ type: "asche", count: 500, speed: 120, size: 3.3, alpha: 0.7, sway: 40, color: "rgba(185,178,168,1)" }, { type: "funken", count: 24, region: [400, 1500, 460, 200], speed: 120, size: 2.6 }],
      camera: { from: { scale: 1.0, x: 0, y: 0 }, to: { scale: 1.14, x: 0, y: -40 }, ease: "power1.inOut" },
    };
  },
};
