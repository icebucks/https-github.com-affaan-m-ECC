// Silhouetten-Figuren. Lokales Koordinatensystem: Füße bei (0,0), Kopf bei y≈-400,
// Blickrichtung nach rechts. Mit g({x,y,s,flip}) platzieren.
const f = (n) => Math.round(n * 10) / 10;
const line = (pts, w, c) =>
  `<polyline points="${pts.map(([x, y]) => `${f(x)},${f(y)}`).join(" ")}" fill="none" stroke="${c}" stroke-width="${w}" stroke-linecap="round" stroke-linejoin="round"/>`;
const poly = (pts, c) => `<polygon points="${pts.map(([x, y]) => `${f(x)},${f(y)}`).join(" ")}" fill="${c}"/>`;

// ---------------------------------------------------------------- Grundkörper
function legs(c, pose, phase = 0) {
  if (pose === "walk") {
    const a = Math.sin(phase) * 1, b = -a;
    return (
      line([[8, -172], [22 + a * 18, -92], [30 + a * 30, -12]], 27, c) +
      line([[-6, -172], [-8 + b * 18, -90], [-18 + b * 30, -14]], 27, c) +
      line([[30 + a * 30, -10], [52 + a * 30, -6]], 14, c) +
      line([[-18 + b * 30, -12], [4 + b * 30, -8]], 14, c)
    );
  }
  return (
    line([[10, -172], [14, -90], [16, -10]], 27, c) +
    line([[-10, -172], [-12, -90], [-14, -10]], 27, c) +
    line([[16, -8], [38, -5]], 14, c) +
    line([[-14, -8], [8, -5]], 14, c)
  );
}

function torso(c, { bulk = 1 } = {}) {
  return (
    `<path d="M${-36 * bulk},-312 Q0,-328 ${38 * bulk},-312 L${34 * bulk},-226 L${-34 * bulk},-226Z" fill="${c}"/>` +
    `<ellipse cx="-2" cy="-302" rx="${46 * bulk}" ry="22" fill="${c}"/>` +
    poly([[-38, -232], [38, -232], [50, -160], [-50, -160]], c) +
    `<rect x="-9" y="-340" width="20" height="34" fill="${c}"/>`
  );
}

function head(c, { helmet = null, hair = false } = {}) {
  let s = `<circle cx="6" cy="-354" r="24" fill="${c}"/>` + poly([[24, -362], [36, -350], [26, -342]], c); // Nase
  if (helmet === "legion" || helmet === "crest") {
    s += `<path d="M-25,-356 C-26,-392 34,-396 36,-358 L40,-354 L-20,-352Z" fill="${c}"/>`;
    s += poly([[-24, -362], [-44, -330], [-38, -326], [-14, -340]], c); // Nackenschutz
    s += poly([[8, -356], [24, -356], [22, -324], [10, -328]], c); // Wangenklappe
    s += `<rect x="2" y="-398" width="6" height="10" fill="${c}"/>`;
    if (helmet === "crest") {
      s += `<path d="M-30,-392 C-20,-440 40,-440 48,-392 L40,-388 C30,-418 -10,-418 -20,-386Z" fill="${c}"/>`;
    }
  }
  if (hair) {
    s += `<path d="M-22,-360 C-30,-395 30,-398 32,-366 C22,-378 0,-380 -8,-370 L-14,-330 L-30,-318 C-34,-336 -28,-350 -22,-360Z" fill="${c}"/>`;
  }
  return s;
}

function cloak(c, len = 120) {
  return `<path d="M-30,-318 C-60,-300 -76,-200 -80,${-200 + len} L-20,${-190 + len} L-30,-226Z" fill="${c}"/>`;
}

// ---------------------------------------------------------------- Römer
export function legionary(c, { pose = "walk", phase = 0, pack = true, shield = true, pilum = true, helmet = "legion" } = {}) {
  let s = "";
  if (pack) {
    s += line([[10, -312], [-80, -392]], 7, c);
    s += `<ellipse cx="-78" cy="-366" rx="26" ry="32" fill="${c}"/>` + `<circle cx="-60" cy="-338" r="16" fill="${c}"/>` + `<rect x="-96" y="-402" width="30" height="16" rx="4" fill="${c}"/>`;
  }
  if (shield) s += `<path d="M-66,-334 Q-50,-340 -34,-334 L-32,-168 Q-50,-162 -68,-168Z" fill="${c}"/>`;
  s += legs(c, pose, phase) + torso(c) + head(c, { helmet });
  if (pilum) {
    s += line([[36, -40], [74, -470]], 7, c) + line([[74, -470], [80, -540]], 3.5, c) + poly([[77, -560], [85, -536], [75, -537]], c);
  }
  s += line([[22, -302], [34, -252], [46, -238]], 20, c);
  return s;
}

export function officer(c, { crest = true } = {}) {
  // Feldherr: Helmbusch, langer Umhang, Schwert
  return cloak(c, 210) + legs(c, "stand") + torso(c, { bulk: 1.05 }) + head(c, { helmet: crest ? "crest" : "legion" }) +
    line([[24, -302], [42, -250], [36, -200]], 20, c) + line([[-24, -300], [-34, -250], [-26, -208]], 20, c) +
    line([[30, -200], [60, -110]], 8, c);
}

export function germanic(c, { spear = true, shield = true, cloakLen = 150 } = {}) {
  let s = cloak(c, cloakLen) + legs(c, "stand") + torso(c) + head(c, { hair: true });
  s += line([[24, -302], [40, -250], [58, -240]], 20, c);
  if (spear) s += line([[50, -30], [64, -540]], 6, c) + `<path d="M64,-590 Q74,-560 65,-532 Q56,-560 64,-590Z" fill="${c}"/>`;
  if (shield) s += `<ellipse cx="-34" cy="-250" rx="20" ry="70" fill="${c}"/>`;
  return s;
}

// Große Profil-Büste (Blick nach links) – die „Ich-Figur“ in Nahaufnahmen.
// Lokale Box 600×800, Ursprung oben links.
export function bustProfile(c, { helmet = "legion", cap = null } = {}) {
  const face =
    "M300,120 C380,115 430,175 430,250 C430,300 410,330 400,360 L405,430 C470,450 560,480 600,560 L600,800 L40,800 L60,600 " +
    "C80,540 150,500 230,480 L245,420 C225,410 205,400 200,385 C190,385 180,380 178,370 C168,362 166,350 172,342 " +
    "C168,335 170,328 176,324 C168,320 166,312 172,306 C166,300 166,294 172,290 C168,284 168,280 174,278 " +
    "C160,274 150,268 148,262 C146,256 152,250 160,246 C170,232 180,215 186,198 C182,190 182,184 186,178 C190,150 230,122 300,120Z";
  let s = `<path d="${face}" fill="${c}"/>`;
  if (helmet === "legion") {
    s += `<path d="M168,196 L196,184 C200,118 262,84 322,88 C392,92 442,140 444,214 L448,252 C474,266 500,282 526,304 L516,316 C484,304 456,298 428,298 L404,300 L360,240 L330,236 L322,250 C312,280 304,316 296,352 C318,362 340,360 352,352 C356,300 356,262 350,236 L400,232 L420,262 Z" fill="${c}"/>`;
    s += `<rect x="296" y="62" width="22" height="30" rx="4" fill="${c}"/>`;
  }
  if (cap === "baker") {
    s += `<path d="M190,190 C190,120 260,90 330,92 C400,96 440,150 436,230 L190,210Z" fill="${c}"/>`;
  }
  if (cap === "stoker") {
    s += `<path d="M180,182 L240,170 C250,120 300,98 350,104 C410,112 440,160 438,224 L250,196 L176,196Z" fill="${c}"/>`;
  }
  return s;
}

// Detail-Linien (Helmrippen, Schulterschienen) – in einer helleren Tonfarbe
export function bustDetail(c) {
  return (
    `<path d="M206,186 C230,140 300,118 360,124" fill="none" stroke="${c}" stroke-width="5" stroke-linecap="round"/>` +
    `<path d="M444,230 C470,262 492,280 512,300" fill="none" stroke="${c}" stroke-width="4" stroke-linecap="round"/>` +
    [0, 1, 2, 3].map((i) => `<path d="M${120 + i * 40},${600 + i * 40} C${260 + i * 30},${520 + i * 30} ${430 + i * 10},${520 + i * 25} ${600},${590 + i * 32}" fill="none" stroke="${c}" stroke-width="5" stroke-linecap="round" opacity="${0.9 - i * 0.15}"/>`).join("")
  );
}

// Einfacher Speer (für fliegende Speere): Spitze zeigt nach rechts, Länge 520
export function spear(c) {
  return `<rect x="0" y="-4" width="470" height="8" rx="4" fill="${c}"/><path d="M462,-13 Q505,-6 530,0 Q505,6 462,13Z" fill="${c}"/>`;
}

// Fackel: Stab, Flamme kommt als Licht/Funken dazu
export function torch(c, flame) {
  return `<rect x="-7" y="-260" width="14" height="260" rx="5" fill="${c}"/><path d="M-16,-262 L16,-262 L12,-236 L-12,-236Z" fill="${c}"/>` +
    `<path d="M0,-370 C22,-320 30,-290 14,-262 L-14,-262 C-30,-290 -18,-320 0,-370Z" fill="${flame}"/>` +
    `<path d="M0,-330 C10,-305 14,-285 6,-264 L-6,-264 C-14,-285 -8,-305 0,-330Z" fill="#fff3c4"/>`;
}

// Rim-Light: Kopie der Figur in Lichtfarbe, verschoben und weichgezeichnet, darunter.
// Das ist das Erkennungszeichen der Ich-Figur in jeder Szene.
export function rimmed(drawFn, dark, rimColor, filterId, dx = -8, dy = -4) {
  return `<g transform="translate(${dx},${dy})" filter="url(#${filterId})" opacity="0.95">${drawFn(rimColor)}</g>${drawFn(dark)}`;
}

export function rimFilter(id, std = 5) {
  return `<filter id="${id}" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="${std}"/></filter>`;
}
