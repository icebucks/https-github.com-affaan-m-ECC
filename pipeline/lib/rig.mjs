// Menschliche Figuren mit Skelett (Rig): realistische Proportionen (~7,5 Kopflängen),
// konische Gliedmaßen mit Waden/Unterarmen, Hände, Schuhe, echtes Gesichtsprofil,
// Kleidung (Tunika, Umhang, Kleid, Hose, Schürze) und Posen inkl. Geh-/Laufzyklen.
// Koordinaten: Füße bei y=0, Scheitel bei y≈-400, Blick nach rechts (+x).

const f = (n) => Math.round(n * 10) / 10;
const D2R = Math.PI / 180;
const rot = ([x, y], a) => [x * Math.cos(a) - y * Math.sin(a), x * Math.sin(a) + y * Math.cos(a)];
const add = (a, b) => [a[0] + b[0], a[1] + b[1]];
const at = (p, len, deg) => [p[0] + len * Math.sin(deg * D2R), p[1] + len * Math.cos(deg * D2R)];

// ---------------------------------------------------------------- Grundformen
function capsule(p1, p2, r1, r2, c) {
  const dx = p2[0] - p1[0], dy = p2[1] - p1[1];
  const L = Math.hypot(dx, dy) || 1;
  const nx = -dy / L, ny = dx / L;
  const q = [[p1[0] + nx * r1, p1[1] + ny * r1], [p2[0] + nx * r2, p2[1] + ny * r2], [p2[0] - nx * r2, p2[1] - ny * r2], [p1[0] - nx * r1, p1[1] - ny * r1]];
  return `<path d="M${q.map(([x, y]) => `${f(x)},${f(y)}`).join(" L")}Z" fill="${c}"/><circle cx="${f(p1[0])}" cy="${f(p1[1])}" r="${f(r1)}" fill="${c}"/><circle cx="${f(p2[0])}" cy="${f(p2[1])}" r="${f(r2)}" fill="${c}"/>`;
}

// glatter Pfad durch Punkte (Catmull-Rom -> Bezier), geschlossen
function smooth(pts, c, extra = "") {
  const n = pts.length;
  let d = `M${f(pts[0][0])},${f(pts[0][1])}`;
  for (let i = 0; i < n; i++) {
    const p0 = pts[(i - 1 + n) % n], p1 = pts[i], p2 = pts[(i + 1) % n], p3 = pts[(i + 2) % n];
    const c1 = [p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6];
    const c2 = [p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6];
    d += ` C${f(c1[0])},${f(c1[1])} ${f(c2[0])},${f(c2[1])} ${f(p2[0])},${f(p2[1])}`;
  }
  return `<path d="${d}Z" fill="${c}" ${extra}/>`;
}

// Kopf aus dem Büsten-Profil (dieselbe Form wie in den Nahaufnahmen = Wiedererkennung)
const HEAD =
  "M300,120 C380,115 430,175 430,250 C430,300 410,330 400,360 L405,450 L245,450 L245,420 C225,410 205,400 200,385 C190,385 180,380 178,370 C168,362 166,350 172,342 " +
  "C168,335 170,328 176,324 C168,320 166,312 172,306 C166,300 166,294 172,290 C168,284 168,280 174,278 " +
  "C160,274 150,268 148,262 C146,256 152,250 160,246 C170,232 180,215 186,198 C182,190 182,184 186,178 C190,150 230,122 300,120Z";
const HEADWEAR = {
  helmet: "M168,196 L196,184 C200,118 262,84 322,88 C392,92 442,140 444,214 L448,252 C474,266 500,282 526,304 L516,316 C484,304 456,298 428,298 L404,300 L360,240 L330,236 L322,250 C312,280 304,316 296,352 C318,362 340,360 352,352 C356,300 356,262 350,236 L400,232 L420,262 Z M296,62 L318,62 L318,92 L296,92Z",
  crest: "M168,196 L196,184 C200,118 262,84 322,88 C392,92 442,140 444,214 L448,252 C474,266 500,282 526,304 L516,316 C484,304 456,298 428,298 L404,300 L360,240 L330,236 L322,250 C312,280 304,316 296,352 C318,362 340,360 352,352 C356,300 356,262 350,236 L400,232 L420,262 Z M196,126 C220,20 410,4 476,130 C440,112 400,100 330,96 C270,96 230,108 196,126Z M296,70 L318,70 L318,100 L296,100Z",
  hair: "M186,182 C192,130 250,100 316,102 C392,106 440,160 436,236 L428,262 C420,230 404,214 380,206 C330,186 260,178 186,182Z",
  longhair: "M186,182 C192,124 254,96 320,100 C398,106 446,164 444,250 C446,320 452,390 470,450 L400,450 C404,380 392,300 372,260 C350,214 280,186 186,182Z M176,318 C190,350 214,372 236,380 C214,400 196,404 178,396Z",
  cap: "M176,190 L250,176 C252,120 300,96 352,100 C414,108 446,156 444,226 L420,232 C400,200 340,190 250,198 L174,200Z",
  scarf: "M182,190 C180,110 270,78 340,86 C420,96 456,170 452,260 C458,340 470,400 500,450 L380,450 C390,380 380,320 360,280 C330,230 260,206 182,190Z",
};
function head(c, H, tilt, wear) {
  const s = 0.19;
  const tr = `translate(${f(H[0])},${f(H[1])}) rotate(${f(tilt)}) scale(${-s},${s}) translate(-300,-262)`;
  let inner = `<path d="${HEAD}" fill="${c}"/>`;
  if (wear && HEADWEAR[wear]) inner += `<path d="${HEADWEAR[wear]}" fill="${c}" fill-rule="nonzero"/>`;
  return `<g transform="${tr}">${inner}</g>`;
}

function hand(c, W, dirDeg, r = 7) {
  const tip = at(W, 13, dirDeg);
  return capsule(W, tip, r, r * 0.75, c);
}

function foot(c, A, shinDeg, flip = 1) {
  // Schuh: Ferse hinten, Spitze vorn, folgt leicht dem Unterschenkel
  const tilt = -(shinDeg * 0.35) * D2R;
  const pts = [[-11, -8], [-13, 2], [-6, 6], [26, 6], [34, 2], [30, -6], [12, -10], [0, -12]].map((p) => add(A, rot(p, tilt)));
  return smooth(pts, c);
}

// ---------------------------------------------------------------- Posen
// Winkel in Grad, 0 = senkrecht nach unten, positiv = nach vorn (Blickrichtung).
export function pose(name = "stand", phase = 0) {
  const P = { lean: 2, bob: 0, tilt: 0, legF: [4, 4], legB: [-4, 3], armF: [8, 14], armB: [-6, 12], headTurn: 0 };
  const s = Math.sin, cs = Math.cos;
  if (name === "walk" || name === "march") {
    const th = phase, tb = phase + Math.PI;
    const knee = (t) => 6 + 48 * Math.pow(Math.max(0, cs(t)), 1.5);
    P.legF = [24 * s(th), knee(th)];
    P.legB = [24 * s(tb), knee(tb)];
    P.armF = [-20 * s(th), 18 + 18 * Math.max(0, s(th))];
    P.armB = [-20 * s(tb), 18 + 18 * Math.max(0, s(tb))];
    P.bob = -4 * cs(2 * th);
    P.lean = name === "march" ? 5 : 4;
  } else if (name === "run") {
    const th = phase, tb = phase + Math.PI;
    const knee = (t) => 18 + 85 * Math.pow(Math.max(0, cs(t)), 1.2);
    P.legF = [10 + 42 * s(th), knee(th)];
    P.legB = [10 + 42 * s(tb), knee(tb)];
    P.armF = [-42 * s(th), 85];
    P.armB = [-42 * s(tb), 85];
    P.bob = -9 * Math.abs(cs(th));
    P.lean = 15;
  } else if (name === "arms_up") {
    P.armF = [150, 55]; P.armB = [140, 60]; P.lean = 6; P.tilt = 12; P.legF = [10, 14]; P.legB = [-6, 8];
  } else if (name === "carry") {
    P.armF = [22, 70]; P.armB = [10, 60];
  } else if (name === "shovel") {
    // phase 0..2π: ausholen -> werfen
    const k = (1 - cs(phase)) / 2;
    P.lean = 10 + 22 * k; P.armF = [30 + 50 * (1 - k), 20 + 20 * k]; P.armB = [10 + 55 * (1 - k), 30];
    P.legF = [24, 26]; P.legB = [-20, 8]; P.tilt = 8 * k;
  } else if (name === "brace") {
    P.lean = -6; P.armF = [70, 30]; P.armB = [55, 40]; P.legF = [22, 10]; P.legB = [-18, 6]; P.tilt = -8;
  } else if (name === "look_up") {
    P.tilt = -22; P.lean = -3; P.armF = [6, 18]; P.armB = [-4, 10];
  } else if (name === "idle") {
    P.lean = 2 + 1.5 * s(phase); P.armF = [6 + 3 * s(phase), 16]; P.tilt = 3 * s(phase * 0.5);
  }
  return P;
}

// ---------------------------------------------------------------- Figur
// costume: { head, body: "tunika"|"lorica"|"stola"|"hose"|"mantel", cloak, apron, pack, shield, weapon, belt }
export function human(c, { pose: pname = "stand", phase = 0, costume = {}, detail = null, bulk = 1 } = {}) {
  const P = typeof pname === "object" ? pname : pose(pname, phase);
  const lean = P.lean * D2R;
  const pelvis = [0, -198 + P.bob];
  const T = (x, y) => add(pelvis, rot([x * bulk, y], lean)); // Rumpf-Koordinaten
  const neck = T(2, -132), shoulder = T(1, -118), hipF = T(4, -2), hipB = T(-4, -2);
  const H = add(neck, rot([6, -30], lean));
  const thighs = costume.body === "hose" ? 1.12 : 1;

  const leg = (hip, [a, b], col) => {
    const K = at(hip, 96, a), A = at(K, 94, a - b);
    const mid = add(at(K, 34, a - b), rot([-4, 0], (a - b) * D2R));
    return { K, A, svg: capsule(hip, K, 19 * thighs, 12.5 * thighs, col) + capsule(K, mid, 12, 12.5, col) + capsule(mid, A, 12.5, 6.5, col) + foot(col, A, a - b) };
  };
  const arm = (S, [a, b], col) => {
    const E = at(S, 62, a), W = at(E, 56, a + b);
    return { E, W, svg: capsule(S, E, 10.5 * bulk, 8.5, col) + capsule(E, W, 8.5, 5.8, col) + hand(col, W, a + b) };
  };
  const torso = () => smooth([
    T(8, 12), T(18, -22), T(13, -62), T(22, -98), T(19, -120), T(8, -134),
    T(-9, -132), T(-21, -114), T(-17, -80), T(-11, -50), T(-21, -14), T(-9, 12),
  ], c);

  const lb = leg(hipB, P.legB, c), lf = leg(hipF, P.legF, c);
  const ab = arm(T(-3, -116), P.armB, c), af = arm(shoulder, P.armF, c);
  let back = "", front = "";

  // Gepäck/Schild hinten
  if (costume.pack) {
    const top = T(-60, -205);
    back += capsule(T(6, -120), top, 3.2, 3, c) + smooth([add(top, [-24, 10]), add(top, [8, 6]), add(top, [12, 46]), add(top, [-6, 66]), add(top, [-30, 50])], c) + `<circle cx="${f(top[0] + 8)}" cy="${f(top[1] + 66)}" r="14" fill="${c}"/>`;
  }
  if (costume.shield === "scutum") back += smooth([T(-38, -130), T(-18, -136), T(-14, -10), T(-34, -4), T(-44, -66)], c);
  if (costume.cloak) {
    const L = costume.cloak; // Länge (Einheiten unterhalb der Schultern)
    back += smooth([T(-6, -134), T(-28, -120), T(-40, -60), T(-52, 10), T(-62, L - 120), T(-30, L - 112), T(-10, L - 126), T(-6, -40)], c);
  }

  let body = lb.svg + lf.svg + torso() + capsule(neck, add(neck, rot([4, -26], lean)), 9, 8.5, c);
  // Kleidung über dem Körper
  if (costume.body === "tunika" || costume.body === "lorica") {
    body += smooth([T(14, -60), T(26, 10), T(34, 52), T(10, 58), T(-14, 56), T(-36, 50), T(-26, 6), T(-14, -60)], c);
  }
  if (costume.body === "lorica") body += smooth([T(-26, -118), T(0, -134), T(28, -116), T(30, -92), T(-28, -92)], c); // Schulterschienen
  if (costume.body === "stola") {
    // langes Kleid: fällt vom Rumpf, Saum folgt den Knien etwas, schwingt beim Laufen nach hinten
    const swing = Math.max(0, P.lean - 4) * 2.2;
    const mix = (u, v, k) => [u[0] * (1 - k) + v[0] * k, u[1] * (1 - k) + v[1] * k];
    const hemF = mix(T(30, 168), add(lf.K, [22, 70]), 0.35), hemB = mix(T(-34 - swing, 164), add(lb.K, [-26, 66]), 0.35);
    body += smooth([T(14, -70), T(26, 30), hemF, add(hemF, [-8, 16]), [(hemF[0] + hemB[0]) / 2, Math.max(hemF[1], hemB[1]) + 10], add(hemB, [6, 14]), hemB, T(-28, 30), T(-14, -70)], c);
  }
  if (costume.body === "mantel") body += smooth([T(20, -110), T(28, 10), T(30, 100), T(-30, 100), T(-30, 10), T(-22, -110)], c);
  if (costume.apron) body += smooth([T(16, -50), T(30, 20), T(30, 90), T(4, 92), T(6, -50)], c);

  front += ab.svg; // hinterer Arm hinter dem Körper
  let weapon = "";
  const W = af.W;
  if (costume.weapon === "pilum" || costume.weapon === "speer") {
    const up = at(W, -250, 6), down = at(W, 190, 6);
    weapon = capsule(down, up, 3.2, 3.2, c) + (costume.weapon === "pilum"
      ? capsule(up, at(up, -80, 6), 1.8, 1.6, c) + `<path d="M${f(at(up, -80, 6)[0] - 5)},${f(at(up, -80, 6)[1])} L${f(at(up, -100, 6)[0])},${f(at(up, -100, 6)[1])} L${f(at(up, -80, 6)[0] + 5)},${f(at(up, -80, 6)[1])}Z" fill="${c}"/>`
      : `<path d="M${f(up[0] - 7)},${f(up[1])} Q${f(at(up, -30, 6)[0])},${f(at(up, -30, 6)[1])} ${f(at(up, -52, 6)[0])},${f(at(up, -52, 6)[1])} Q${f(at(up, -30, 6)[0] + 2)},${f(at(up, -30, 6)[1])} ${f(up[0] + 7)},${f(up[1])}Z" fill="${c}"/>`);
  }
  if (costume.weapon === "schaufel") {
    const dir = Math.max(28, P.armF[0] + P.armF[1] - 40);
    const tip = at(W, 150, dir);
    weapon = capsule(at(W, -30, dir), tip, 3.5, 3.5, c) + smooth([at(tip, -6, dir + 90), at(tip, 46, dir + 20), at(tip, 50, dir - 20), at(tip, -6, dir - 90)], c);
  }
  if (costume.weapon === "brotschieber") {
    const dir = P.armF[0] + P.armF[1] - 40;
    const tip = at(W, 210, dir);
    weapon = capsule(at(W, -20, dir), tip, 3, 3, c) + `<ellipse cx="${f(at(tip, 22, dir)[0])}" cy="${f(at(tip, 22, dir)[1])}" rx="34" ry="14" transform="rotate(${f(90 - dir)} ${f(at(tip, 22, dir)[0])} ${f(at(tip, 22, dir)[1])})" fill="${c}"/>`;
  }
  if (costume.weapon === "schwert") weapon = capsule(T(14, 4), T(40, 70), 3, 2, c);
  if (costume.shield === "rund") weapon += `<ellipse cx="${f(ab.W[0] + 6)}" cy="${f(ab.W[1] - 10)}" rx="17" ry="52" fill="${c}"/>`;

  const headSvg = head(c, H, P.tilt + P.lean, costume.head);
  let s = back + front + body + headSvg + weapon + af.svg;

  if (detail) {
    // feine hellere Linien: Gürtel, Saum, Schienen – geben Volumen, bleiben Silhouette
    const ln = (a, b, w = 2.5, o = 0.55) => `<line x1="${f(a[0])}" y1="${f(a[1])}" x2="${f(b[0])}" y2="${f(b[1])}" stroke="${detail}" stroke-width="${w}" stroke-linecap="round" opacity="${o}"/>`;
    s += ln(T(-14, -58), T(16, -58), 3);
    if (costume.body === "lorica") for (let k = 0; k < 4; k++) s += ln(T(-18, -104 + k * 11), T(22, -100 + k * 11), 2, 0.4);
    if (costume.cloak) s += ln(T(-10, -126), T(-48, 0), 2, 0.3);
  }
  return s;
}

// Daumenkino für Bewegung: n Einzelbilder, nur eines sichtbar (die Szene schaltet um)
export function cycle(id, drawFn, n = 8) {
  let s = `<g id="${id}">`;
  for (let i = 0; i < n; i++) s += `<g opacity="${i === 0 ? 1 : 0}">${drawFn((i / n) * Math.PI * 2)}</g>`;
  return s + "</g>";
}

// ---------------------------------------------------------------- Rollen (API wie bisher)
export function legionary(c, { pose: p = "walk", phase = 0, pack = true, shield = true, pilum = true, helmet = "legion", detail = null } = {}) {
  return human(c, { pose: p === "walk" ? "march" : p, phase, detail, costume: { head: helmet === "crest" ? "crest" : "helmet", body: "lorica", pack, shield: shield ? "scutum" : null, weapon: pilum ? "pilum" : null } });
}
export function officer(c, { crest = true, detail = null } = {}) {
  return human(c, { pose: "stand", detail, bulk: 1.05, costume: { head: crest ? "crest" : "helmet", body: "lorica", cloak: 260, weapon: "schwert" } });
}
export function germanic(c, { spear = true, shield = true, cloakLen = 150, pose: p = "stand", phase = 0, detail = null } = {}) {
  return human(c, { pose: p, phase, detail, costume: { head: "longhair", body: "tunika", cloak: cloakLen + 60, weapon: spear ? "speer" : null, shield: shield ? "rund" : null } });
}
// Zivilisten: dress tunika|stola|hose; hat null|kappe|tuch; tool null|schaufel|brotschieber; arms down|up|swing
export function person(c, { pose: p = "stand", phase = 0, dress = "tunika", hat = null, tool = null, arms = "down", apron = false, detail = null } = {}) {
  let pn = p;
  if (arms === "up") pn = "arms_up";
  if (p === "walk" && arms === "swing") pn = "walk";
  if (tool === "schaufel" && p === "stand") pn = "shovel";
  if (tool === "brotschieber" && p === "stand") pn = "carry";
  return human(c, { pose: pn, phase, detail, costume: { head: hat === "kappe" ? "cap" : hat === "tuch" ? "scarf" : "hair", body: dress, apron, weapon: tool } });
}
