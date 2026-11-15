// SVG-Grundformen für die gemalten Parallax-Ebenen.
// Koordinatensystem jeder Ebene: Kamera-Raum CW × CH (größer als das Bild, damit
// Zoom/Schwenk nie den Rand zeigt).
export const CW = 1260;
export const CH = 2240;
export const FW = 1080;
export const FH = 1920;

export function mulberry(seed) {
  let a = seed >>> 0;
  return () => {
    a |= 0; a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
export const hashSeed = (s) => [...String(s)].reduce((h, c) => (Math.imul(h, 31) + c.charCodeAt(0)) >>> 0, 7);

const f = (n) => Math.round(n * 10) / 10;

export function svg(inner, { defs = "", blur = 0, id = "" } = {}) {
  const filt = blur
    ? `<filter id="${id}-b" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="${blur}"/></filter>`
    : "";
  return `<svg viewBox="0 0 ${CW} ${CH}" width="${CW}" height="${CH}" xmlns="http://www.w3.org/2000/svg"><defs>${defs}${filt}</defs><g${blur ? ` filter="url(#${id}-b)"` : ""}>${inner}</g></svg>`;
}

export function linGrad(id, stops, vertical = true) {
  const s = stops.map((c, i) => `<stop offset="${f((i / (stops.length - 1)) * 100)}%" stop-color="${c}"/>`).join("");
  return `<linearGradient id="${id}" x1="0" y1="0" x2="${vertical ? 0 : 1}" y2="${vertical ? 1 : 0}">${s}</linearGradient>`;
}

export function radGrad(id, color, opacity = 1) {
  return `<radialGradient id="${id}"><stop offset="0%" stop-color="${color}" stop-opacity="${opacity}"/><stop offset="45%" stop-color="${color}" stop-opacity="${opacity * 0.35}"/><stop offset="100%" stop-color="${color}" stop-opacity="0"/></radialGradient>`;
}

export function rect(fill, x = 0, y = 0, w = CW, h = CH, extra = "") {
  return `<rect x="${f(x)}" y="${f(y)}" width="${f(w)}" height="${f(h)}" fill="${fill}" ${extra}/>`;
}

export function glow(x, y, r, gradId, opacity = 1) {
  return `<circle cx="${f(x)}" cy="${f(y)}" r="${f(r)}" fill="url(#${gradId})" opacity="${opacity}"/>`;
}

// Nadelbaum: gezackte Etagen
export function conifer(x, base, h, w, fill, r) {
  const tiers = 7 + Math.floor(r() * 4);
  const top = base - h;
  let left = [], right = [];
  for (let i = 0; i <= tiers; i++) {
    const q = i / tiers;
    const y = top + q * h * 0.92;
    const ww = w * (0.08 + q * 0.92) * (0.85 + r() * 0.3);
    const yIn = y + (h / tiers) * 0.35;
    left.push(`${f(x - ww / 2)},${f(y + (h / tiers) * 0.9)} ${f(x - ww * 0.22)},${f(yIn)}`);
    right.push(`${f(x + ww * 0.22)},${f(yIn)} ${f(x + ww / 2)},${f(y + (h / tiers) * 0.9)}`);
  }
  const trunkW = Math.max(3, w * 0.06);
  const pts = [`${f(x)},${f(top - h * 0.03)}`, ...right, `${f(x + trunkW)},${f(base)}`, `${f(x - trunkW)},${f(base)}`, ...left.reverse()];
  return `<polygon points="${pts.join(" ")}" fill="${fill}"/>`;
}

// Laubbaum: Stamm + Krone aus Kreisen
export function deciduous(x, base, h, fill, r) {
  const tw = h * 0.05;
  let s = `<path d="M${f(x - tw)},${f(base)} L${f(x - tw * 0.6)},${f(base - h * 0.55)} L${f(x + tw * 0.6)},${f(base - h * 0.55)} L${f(x + tw)},${f(base)}Z" fill="${fill}"/>`;
  const cy = base - h * 0.68, cr = h * 0.3;
  for (let i = 0; i < 9; i++) {
    const a = r() * Math.PI * 2, d = r() * cr * 0.6;
    s += `<circle cx="${f(x + Math.cos(a) * d)}" cy="${f(cy + Math.sin(a) * d * 0.8)}" r="${f(cr * (0.45 + r() * 0.35))}" fill="${fill}"/>`;
  }
  return s;
}

// Hoher Stamm im Vordergrund, über das ganze Bild
export function trunk(x, w, fill, r, lean = 0) {
  const top = -60, bot = CH + 60;
  const wt = w * 0.82;
  let d = `M${f(x - w / 2)},${f(bot)} C${f(x - w / 2 + lean * 0.3)},${f(bot * 0.6)} ${f(x - wt / 2 + lean * 0.7)},${f(bot * 0.3)} ${f(x - wt / 2 + lean)},${f(top)} L${f(x + wt / 2 + lean)},${f(top)} C${f(x + wt / 2 + lean * 0.7)},${f(bot * 0.3)} ${f(x + w / 2 + lean * 0.3)},${f(bot * 0.6)} ${f(x + w / 2)},${f(bot)}Z`;
  let s = `<path d="${d}" fill="${fill}"/>`;
  // Aststummel
  const n = 2 + Math.floor(r() * 3);
  for (let i = 0; i < n; i++) {
    const y = 150 + r() * (CH * 0.6);
    const side = r() > 0.5 ? 1 : -1;
    const len = w * (0.5 + r() * 0.7);
    const bx = x + lean * (1 - y / bot) + (side * wt) / 2.2;
    s += `<path d="M${f(bx)},${f(y)} Q${f(bx + side * len * 0.6)},${f(y - len * 0.1)} ${f(bx + side * len)},${f(y - len * 0.5)} L${f(bx + side * len * 0.95)},${f(y - len * 0.42)} Q${f(bx + side * len * 0.5)},${f(y - len * 0.05)} ${f(bx)},${f(y + w * 0.25)}Z" fill="${fill}"/>`;
  }
  return s;
}

export function treeline(y, n, hmin, hmax, fill, r, { x0 = -60, x1 = CW + 60, w = 0.32 } = {}) {
  let s = "";
  for (let i = 0; i < n; i++) {
    const x = x0 + ((i + r() * 0.8) / n) * (x1 - x0);
    const h = hmin + r() * (hmax - hmin);
    s += conifer(x, y + r() * 30, h, h * w * (0.8 + r() * 0.4), fill, r);
  }
  return s + rect(fill, x0, y + 10, x1 - x0, CH - y);
}

export function hills(y, amp, fill, r, { freq = 3, x0 = -40, x1 = CW + 40 } = {}) {
  const ph = r() * 6, ph2 = r() * 6;
  let d = `M${x0},${CH + 40} L${x0},${f(y)}`;
  for (let x = x0; x <= x1; x += 30) {
    const q = x / CW;
    const yy = y + Math.sin(q * Math.PI * freq + ph) * amp + Math.sin(q * Math.PI * freq * 2.7 + ph2) * amp * 0.35;
    d += ` L${f(x)},${f(yy)}`;
  }
  d += ` L${x1},${CH + 40}Z`;
  return `<path d="${d}" fill="${fill}"/>`;
}

// Farne/Unterholz: spitze Blätter entlang einer Linie
export function ferns(y, fill, r, { n = 34, h = 160, x0 = -40, x1 = CW + 40 } = {}) {
  let s = rect(fill, x0, y, x1 - x0, CH - y + 60);
  for (let i = 0; i < n; i++) {
    const x = x0 + r() * (x1 - x0);
    const hh = h * (0.5 + r() * 0.8);
    const lean = (r() - 0.5) * hh * 0.9;
    const w = 10 + r() * 16;
    s += `<path d="M${f(x - w)},${f(y + 20)} Q${f(x + lean * 0.4)},${f(y - hh * 0.6)} ${f(x + lean)},${f(y - hh)} Q${f(x + lean * 0.5 + w)},${f(y - hh * 0.5)} ${f(x + w)},${f(y + 20)}Z" fill="${fill}"/>`;
  }
  return s;
}

export function poly(points, fill, extra = "") {
  return `<polygon points="${points.map(([x, y]) => `${f(x)},${f(y)}`).join(" ")}" fill="${fill}" ${extra}/>`;
}

export function path(d, fill, extra = "") {
  return `<path d="${d}" fill="${fill}" ${extra}/>`;
}

export function g(inner, { x = 0, y = 0, s = 1, flip = false, rot = 0, extra = "" } = {}) {
  const sc = flip ? `${-s},${s}` : `${s}`;
  return `<g transform="translate(${f(x)},${f(y)}) rotate(${rot}) scale(${sc})" ${extra}>${inner}</g>`;
}
