// Motive für die Römerzeit (Germanien). Jedes Motiv liefert Ebenen, Licht,
// Partikel, Kamera und optionale Animationen/Ereignisse.
import { CW, CH, svg, linGrad, rect, treeline, trunk, ferns, hills, g, conifer, path } from "../svg.mjs";
import { legionary, officer, germanic, bustProfile, bustDetail, rimmed, rimFilter, spear, torch } from "../figures.mjs";

const sky = (ctx, id, stops) => svg(rect(`url(#${id})`), { defs: linGrad(id, stops || ctx.pal.sky) });

function forestBack(ctx, { y1 = 1150, y2 = 1380, blur1 = 7, blur2 = 3 } = {}) {
  const { pal, r, sid } = ctx;
  return [
    { name: "sky", depth: 0, svg: sky(ctx, `${sid}-sky`) },
    { name: "far", depth: 0.15, svg: svg(treeline(y1, 26, 380, 620, pal.far, r), { blur: blur1, id: `${sid}-far` }) },
    { name: "mid", depth: 0.35, svg: svg(treeline(y2, 18, 520, 900, pal.mid, r) + trunk(180, 46, pal.mid, r, 10) + trunk(1010, 54, pal.mid, r, -14), { blur: blur2, id: `${sid}-mid` }) },
  ];
}

const rain = (ctx, extra = {}) => ({ type: "regen", count: 420, angle: 14, speed: 2300, len: 80, alpha: 0.32, color: ctx.pal.rain, ...extra });
const fog = (ctx, extra = {}) => ({ type: "nebel", count: 9, size: 560, alpha: 0.16, rgb: ctx.pal.fog, y0: 900, y1: 1900, speed: 22, ...extra });

export const motifs = {
  legionaer_portrait(ctx) {
    const { pal, r, sid } = ctx;
    const rim = `${sid}-rim`;
    const hero = (c) => bustProfile(c, { helmet: "legion" }) + `<rect x="40" y="790" width="560" height="500" fill="${c}"/>`;
    return {
      layers: [
        ...forestBack(ctx),
        {
          name: "hero", depth: 0.8,
          svg: svg(g(rimmed(hero, pal.fg, pal.accent, rim, -12, -6) + bustDetail(pal.near), { x: 340, y: 640, s: 1.45 }) +
            g(torch(pal.fg, pal.accent), { x: 150, y: 1500, s: 1.5 }), { defs: rimFilter(rim, 7) }),
        },
      ],
      lights: [
        { x: 150, y: 1000, r: 900, color: pal.accent, intensity: 0.75, flicker: true },
        { x: 640, y: 300, r: 900, color: pal.cold, intensity: 0.18 },
      ],
      fxBack: [fog(ctx, { y0: 1100, y1: 1700 })],
      fxFront: [rain(ctx), { type: "funken", count: 26, region: [130, 520, 130, 90], speed: 140, drift: 40, size: 3 }],
      camera: { from: { scale: 1.0, x: 0, y: 20 }, to: { scale: 1.09, x: -30, y: -10 } },
    };
  },

  kolonne_wald(ctx) {
    const { pal, r, sid } = ctx;
    const rim = `${sid}-rim`;
    let col = "";
    const N = 16;
    for (let i = N - 1; i >= 1; i--) {
      const z = i / N; // 0 = nah, 1 = fern
      const s = 1.35 * Math.pow(1 - z, 1.4) + 0.14;
      const x = 720 - 330 * Math.pow(1 - z, 1.1) + Math.sin(z * 6) * 50;
      const y = 1300 + 800 * Math.pow(1 - z, 1.5);
      col += g(legionary(z > 0.55 ? pal.far : pal.mid, { phase: i * 1.3 }), { x, y, s });
    }
    const near = (c) => legionary(c, { phase: 0.4 });
    return {
      layers: [
        ...forestBack(ctx),
        { name: "road", depth: 0.45, svg: svg(path(`M250,2300 C380,1800 700,1500 700,1290 L760,1290 C800,1500 760,1900 1000,2300Z`, pal.cold, `opacity="0.16"`), { blur: 6, id: `${sid}-road` }) },
        { name: "col", depth: 0.55, svg: svg(col, { blur: 1.2, id: `${sid}-col` }) },
        { name: "hero", depth: 0.8, svg: svg(g(rimmed(near, pal.fg, pal.accent, rim, -10, -4), { x: 400, y: 2330, s: 2.3 }), { defs: rimFilter(rim, 6) }) },
        { name: "fg", depth: 1.0, svg: svg(trunk(30, 150, pal.fg, r, 30) + trunk(1230, 170, pal.fg, r, -40) + ferns(2150, pal.fg, r, { n: 28, h: 220 })) },
      ],
      lights: [
        { x: 120, y: 1500, r: 800, color: pal.accent, intensity: 0.45, flicker: true },
        { x: 800, y: 1250, r: 700, color: pal.cold, intensity: 0.25 },
      ],
      fxBack: [fog(ctx, { y0: 1150, y1: 1650, alpha: 0.22, count: 11 })],
      fxFront: [rain(ctx)],
      camera: { from: { scale: 1.06, x: 30, y: 0 }, to: { scale: 1.0, x: -40, y: -20 } },
      march: { name: "col", dx: -26 },
    };
  },

  gepaeck(ctx) {
    const { pal, r, sid } = ctx;
    const rim = `${sid}-rim`;
    const hero = (c) => legionary(c, { pose: "stand", pilum: true });
    return {
      layers: [
        ...forestBack(ctx, { blur1: 10, blur2: 6 }),
        { name: "hero", depth: 0.8, svg: svg(g(rimmed(hero, pal.fg, pal.accent, rim, -6, -3), { x: 690, y: 2420, s: 3.3, flip: true }), { defs: rimFilter(rim, 5) }) },
        { name: "fg", depth: 1.0, svg: svg(ferns(2180, pal.fg, r, { n: 20, h: 160 })) },
      ],
      lights: [
        { x: 1150, y: 1150, r: 900, color: pal.accent, intensity: 0.6, flicker: true },
        { x: 400, y: 600, r: 800, color: pal.cold, intensity: 0.2 },
      ],
      fxBack: [fog(ctx, { y0: 1000, y1: 1600 })],
      fxFront: [rain(ctx, { count: 480 })],
      camera: { from: { scale: 1.12, x: 0, y: 140 }, to: { scale: 1.02, x: 0, y: -60 } },
    };
  },

  nasser_helm(ctx) {
    const { pal, sid } = ctx;
    const rim = `${sid}-rim`;
    const hero = (c) => bustProfile(c, { helmet: "legion" }) + `<rect x="40" y="790" width="560" height="500" fill="${c}"/>`;
    return {
      layers: [
        ...forestBack(ctx, { blur1: 14, blur2: 10 }),
        {
          name: "hero", depth: 0.85,
          svg: svg(g(rimmed(hero, pal.fg, pal.cold, rim, -6, -10) + bustDetail(pal.mid), { x: -160, y: 260, s: 2.6 }), { defs: rimFilter(rim, 4) }),
        },
      ],
      lights: [
        { x: 700, y: 400, r: 900, color: pal.cold, intensity: 0.35 },
        { x: 60, y: 1300, r: 800, color: pal.accent, intensity: 0.35, flicker: true },
      ],
      fxBack: [fog(ctx, { y0: 700, y1: 1400, alpha: 0.12 })],
      fxFront: [
        rain(ctx, { count: 500, alpha: 0.38, len: 100 }),
        { type: "tropfen", count: 34, region: [300, 470, 820, 520], size: 7, alpha: 0.85, color: "rgba(225,238,240,1)" },
      ],
      camera: { from: { scale: 1.0, x: 40, y: 0 }, to: { scale: 1.1, x: -20, y: 30 } },
    };
  },

  langer_zug(ctx) {
    const { pal, r, sid } = ctx;
    let dots = "";
    // gewundener Pfad zwischen Hängen, darauf hunderte Marschierende
    let road = "M640,2400";
    for (let u = 0; u <= 1.0001; u += 0.02) {
      const x = 640 + 330 * Math.sin(u * 7) * (1 - u * 0.55);
      const y = 2400 - u * 1650;
      road += ` L${x.toFixed(1)},${y.toFixed(1)}`;
    }
    for (let k = 0; k < 420; k++) {
      const u = k / 420;
      const x = 640 + 330 * Math.sin(u * 7) * (1 - u * 0.55) + (r() - 0.5) * 30 * (1 - u);
      const y = 2400 - u * 1650;
      const s = 3.4 * Math.pow(1 - u, 1.3) + 0.35;
      dots += `<rect x="${(x - 4 * s).toFixed(1)}" y="${(y - 18 * s).toFixed(1)}" width="${(8 * s).toFixed(1)}" height="${(18 * s).toFixed(1)}" rx="${(3 * s).toFixed(1)}" fill="${pal.fg}"/>`;
      if (k % 3 === 0) dots += `<rect x="${(x + 3 * s).toFixed(1)}" y="${(y - 34 * s).toFixed(1)}" width="${(1.6 * s).toFixed(1)}" height="${(26 * s).toFixed(1)}" fill="${pal.fg}"/>`;
    }
    return {
      layers: [
        { name: "sky", depth: 0, svg: sky(ctx, `${sid}-sky`) },
        { name: "far", depth: 0.15, svg: svg(hills(700, 60, pal.far, r, { freq: 2 }) + treeline(760, 40, 120, 200, pal.far, r), { blur: 5, id: `${sid}-far` }) },
        { name: "mid", depth: 0.3, svg: svg(hills(1000, 90, pal.mid, r, { freq: 2.5 }) + treeline(1060, 34, 160, 300, pal.mid, r), { blur: 2, id: `${sid}-mid` }) },
        { name: "road", depth: 0.45, svg: svg(`<path d="${road}" fill="none" stroke="${pal.cold}" stroke-width="80" stroke-linecap="round" opacity="0.22"/>` + dots) },
        { name: "fg", depth: 1.0, svg: svg(treeline(2050, 10, 500, 800, pal.fg, r, { x0: -200, x1: 330 }) + treeline(2000, 10, 500, 900, pal.fg, r, { x0: 950, x1: 1500 })) },
      ],
      lights: [{ x: 640, y: 500, r: 1000, color: pal.cold, intensity: 0.28 }],
      fxBack: [fog(ctx, { y0: 700, y1: 1300, alpha: 0.24, count: 12, size: 700 })],
      fxFront: [rain(ctx, { count: 360, alpha: 0.26 })],
      camera: { from: { scale: 1.1, x: 0, y: 160 }, to: { scale: 1.02, x: 0, y: -120 } },
    };
  },

  varus_arminius(ctx) {
    const { pal, r, sid } = ctx;
    const tent = `<path d="M330,1760 L640,1240 L950,1760Z" fill="${pal.near}"/><path d="M590,1760 L640,1400 L690,1760Z" fill="${pal.accent}" opacity="0.55"/>`;
    return {
      layers: [
        ...forestBack(ctx, { blur1: 9, blur2: 5 }),
        { name: "tent", depth: 0.5, svg: svg(tent + hills(1740, 10, pal.near, r), { blur: 2, id: `${sid}-tent` }) },
        {
          name: "men", depth: 0.75,
          svg: svg(g(officer(pal.fg), { x: 340, y: 1980, s: 2.0 }) + g(germanic(pal.fg, { shield: false }), { x: 930, y: 1980, s: 2.0, flip: true }) + g(torch(pal.fg, pal.accent), { x: 640, y: 2060, s: 1.4 })),
        },
      ],
      labels: [
        { x: 340, y: 1060, text: "Varus" },
        { x: 930, y: 1060, text: "Arminius" },
      ],
      lights: [
        { x: 640, y: 1560, r: 900, color: pal.accent, intensity: 0.75, flicker: true },
        { x: 640, y: 1500, r: 420, color: pal.accent2, intensity: 0.35, flicker: true },
      ],
      fxBack: [fog(ctx, { y0: 1200, y1: 1800, alpha: 0.14 })],
      fxFront: [rain(ctx, { count: 300 }), { type: "funken", count: 30, region: [600, 1500, 80, 60], speed: 170, size: 3 }],
      camera: { from: { scale: 1.0, x: 0, y: 0 }, to: { scale: 1.1, x: 0, y: 40 } },
    };
  },

  stiller_wald(ctx) {
    const { pal, r, sid } = ctx;
    let trunks = "";
    for (let i = 0; i < 9; i++) trunks += trunk(80 + i * 140 + (r() - 0.5) * 60, 40 + r() * 50, pal.near, r, (r() - 0.5) * 40);
    return {
      layers: [
        { name: "sky", depth: 0, svg: sky(ctx, `${sid}-sky`, [pal.sky[0], pal.sky[1], pal.sky[0]]) },
        { name: "far", depth: 0.15, svg: svg(treeline(1250, 30, 400, 700, pal.far, r), { blur: 9, id: `${sid}-far` }) },
        { name: "mid", depth: 0.35, svg: svg(trunks, { blur: 2.5, id: `${sid}-mid` }) },
        { name: "fg", depth: 1.0, svg: svg(trunk(60, 190, pal.fg, r, 20) + trunk(1210, 210, pal.fg, r, -20) + ferns(2120, pal.fg, r, { n: 30, h: 260 })) },
      ],
      lights: [{ x: 640, y: 1200, r: 700, color: pal.cold, intensity: 0.22 }],
      fxBack: [fog(ctx, { y0: 1000, y1: 1900, alpha: 0.26, count: 12, speed: 4 })],
      fxFront: [rain(ctx, { ramp: [0, 0.8, 0.6, 0] })],
      camera: { from: { scale: 1.0, x: 0, y: 0 }, to: { scale: 1.16, x: 0, y: -40 }, ease: "power1.inOut" },
      darken: 0.25,
    };
  },

  speere(ctx) {
    const { pal, r, sid, dur } = ctx;
    let col = "";
    for (let i = 0; i < 7; i++) {
      const x = 200 + i * 140 + (r() - 0.5) * 40;
      col += g(legionary(pal.near, { pose: i % 2 ? "walk" : "stand", phase: i, pack: false }), { x, y: 1880 - (i % 2) * 30, s: 0.9 + r() * 0.2, flip: i % 3 === 0 });
    }
    // Speere: Startpunkt im Dickicht links/rechts, Ziel in der Kolonne
    const n = Math.max(6, Math.min(12, Math.round(dur * 2.2)));
    const spears = [];
    const events = [];
    for (let i = 0; i < n; i++) {
      const fromLeft = i % 2 === 0;
      const t0 = 0.15 + (i / n) * (dur - 0.8);
      const y0 = 700 + r() * 500, y1 = 1500 + r() * 350;
      const x0 = fromLeft ? -560 : CW + 60, x1 = fromLeft ? 380 + r() * 360 : 420 + r() * 380;
      const rot = (Math.atan2(y1 - y0, x1 - x0) * 180) / Math.PI;
      spears.push({ t0, x0, y0, x1, y1, rot, s: 0.8 + r() * 0.6 });
      if (i % 2 === 0) events.push({ dt: t0 + 0.28, typ: "speer" });
    }
    return {
      layers: [
        ...forestBack(ctx, { blur1: 8, blur2: 3 }),
        { name: "col", depth: 0.55, svg: svg(col + hills(1880, 8, pal.near, r)) },
        { name: "fg", depth: 1.0, svg: svg(trunk(40, 200, pal.fg, r, 40) + trunk(1220, 220, pal.fg, r, -50) + ferns(2000, pal.fg, r, { n: 30, h: 240 })) },
      ],
      spears: spears.map((s) => ({ ...s, svg: `<g transform="translate(0,-3)" opacity="0.9">${spear(pal.accent)}</g>` + spear(pal.fg) })),
      lights: [
        { x: 640, y: 1600, r: 1000, color: pal.accent, intensity: 0.55, flicker: true, fast: true },
      ],
      fxBack: [fog(ctx, { y0: 1100, y1: 1800, alpha: 0.18 })],
      fxFront: [rain(ctx, { count: 520, speed: 2700, alpha: 0.36 })],
      camera: { from: { scale: 1.12, x: 0, y: 0 }, to: { scale: 1.0, x: 0, y: 0 }, ease: "power2.out" },
      shake: 9,
      events,
    };
  },

  verrat(ctx) {
    const { pal, r, sid } = ctx;
    let warriors = "";
    const torches = [];
    for (let i = 0; i < 9; i++) {
      if (i === 4) continue;
      const x = 120 + i * 130 + (r() - 0.5) * 30;
      const y = 1500 + Math.abs(i - 4) * 46;
      warriors += g(germanic(pal.fg, { spear: i % 2 === 0, shield: i % 2 === 1, cloakLen: 100 }), { x, y, s: 0.75, flip: i > 4 });
      if (i % 2 === 1) {
        warriors += g(torch(pal.fg, pal.accent), { x: x + 30, y: y - 120, s: 0.5 });
        torches.push({ x: x + 30, y: y - 300 });
      }
    }
    return {
      layers: [
        { name: "sky", depth: 0, svg: sky(ctx, `${sid}-sky`, [pal.sky[0], pal.sky[2], pal.sky[1]]) },
        { name: "far", depth: 0.15, svg: svg(treeline(1450, 30, 200, 380, pal.far, r), { blur: 6, id: `${sid}-far` }) },
        { name: "ridge", depth: 0.5, svg: svg(path(`M-60,2300 L-60,1700 C300,1560 500,1460 640,1460 C780,1460 980,1560 1320,1700 L1320,2300Z`, pal.fg) + warriors + g(germanic(pal.fg, { shield: false, cloakLen: 190 }), { x: 640, y: 1470, s: 1.25 })) },
      ],
      lights: [
        ...torches.map((t) => ({ x: t.x, y: t.y, r: 260, color: pal.accent, intensity: 0.8, flicker: true })),
        { x: 640, y: 1100, r: 800, color: pal.cold, intensity: 0.25 },
      ],
      fxBack: [fog(ctx, { y0: 1300, y1: 1700, alpha: 0.12 })],
      fxFront: [rain(ctx, { count: 380 }), { type: "funken", count: 40, region: [100, 1100, 1000, 200], speed: 150 }],
      camera: { from: { scale: 1.0, x: 0, y: 60 }, to: { scale: 1.18, x: 0, y: 0 }, ease: "power1.in" },
      shake: 3,
    };
  },
};
