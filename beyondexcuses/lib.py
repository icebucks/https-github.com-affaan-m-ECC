"""Baukasten für Strichfiguren-Metapher-Videos (1080x1920, 30 fps)."""
import math, sys, os, subprocess, json
import numpy as np
import skia

W, H, FPS = 1080, 1920, 30
F_SANS = skia.Typeface.MakeFromFile("/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf")
_HERE = os.path.dirname(os.path.abspath(__file__))
_POP = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
F_CAP = skia.Typeface.MakeFromFile(_POP if os.path.exists(_POP) else os.path.join(_HERE, "fonts", "Poppins-Bold.ttf"))
INK = (22, 24, 34)
WHITE = (244, 244, 240)
AMBER = (255, 196, 90)
GREY = (205, 212, 228)
RED = (255, 110, 100)


# ------------------------------------------------------------------ language
LANG = os.environ.get("VID_LANG", "de")
EN = {
    "PLANER": "PLANNER", "MACHER": "DOER", "DEMUT": "HUMILITY", "HILFE": "HELPER", "DISZIPLIN": "DISCIPLINE",
    "AUSREDEN": "EXCUSES", "NEID": "ENVY", "ZUFRIEDENHEIT": "CONTENTMENT", "KOMFORTZONE": "COMFORT ZONE",
    "WACHSTUM": "GROWTH", "GRENZEN": "BOUNDARIES", "KOLLEGE": "COWORKER", "CHEF": "BOSS", "FREUND": "FRIEND", "FAMILIE": "FAMILY",
    "Planen fühlt sich an": "Planning feels like", "wie Fortschritt.": "progress.", "Ist es aber nicht.": "But it isn't.",
    "Was, wenn ich ausrutsche?": "What if I slip?", "Ist das Wasser tief?": "Is the water deep?",
    "Was denken die anderen?": "What will people think?", "Vielleicht morgen…": "Maybe tomorrow…", "Was, wenn…": "What if…",
    "Und wenn…?": "But what if…?", "Bin ich bereit?": "Am I ready?", "Zu riskant.": "Too risky.",
    "Du musst nicht": "You don't have to", "alles durchdenken.": "overthink everything.", "Nur den nächsten Schritt.": "Just take the next step.",
    "Halt dich fest!": "Hold on tight!", "Komm, nimm das Seil!": "Come on, take the rope!", "Ich brauche niemanden.": "I don't need anyone.",
    "Hilfe annehmen": "Accepting help", "ist keine Schwäche.": "isn't weakness.", "Stolz hält dich unten.": "Pride keeps you down.",
    "Zu nass.": "Too wet.", "Zu kalt.": "Too cold.", "Zu müde.": "Too tired.", "Montag dann.": "Monday, then.", "Morgen.": "Tomorrow.",
    "Morgen fang ich an.": "I'll start tomorrow.", "Es wird nie": "There will never be", "den perfekten Tag geben.": "a perfect day.",
    "Fang trotzdem an.": "Start anyway.",
    "Warum er?": "Why him?", "Unfair.": "Not fair.", "Das will ich auch.": "I want that too.", "Seiner ist besser.": "His is better.",
    "Wieso nicht ich?": "Why not me?", "Mein Garten…?": "My garden…?", "Wer nur über den Zaun schaut,": "If you only look over the fence,",
    "gießt nie den eigenen Garten.": "you never water your own garden.", "Kümmer dich um deins.": "Tend to yours.",
    "Bleib doch hier!": "Just stay here!", "Draußen ist es kalt.": "It's cold out there.", "Hier ist es sicher.": "It's safe in here.",
    "Wird's hier enger…?": "Is it getting tighter…?", "Die Komfortzone ist gemütlich.": "The comfort zone is cozy.",
    "Aber nichts wächst darin.": "But nothing grows there.", "Geh raus.": "Step out.",
    "Trägst du meinen?": "Can you carry mine?", "Nein. Das schaffst du.": "No. You've got this.", "Und du?": "What about you?",
    "Klar!": "Sure!", "Machst du das noch?": "Can you take this too?", "Kein Problem!": "No problem!", "Nimmst du meins?": "Will you take mine?",
    "Na klar!": "Of course!", "Du schaffst das doch.": "You can handle it.", "Du kannst nicht": "You can't", "jeden tragen.": "carry everyone.",
    "Nein ist ein ganzer Satz.": "No is a complete sentence.",
}


EN.update({
    "Denkst du auch zu viel nach?": "Do you overthink too?", "Würdest du das Seil nehmen?": "Would you take the rope?",
    "Welche Ausrede nutzt du?": "Which excuse is yours?", "Schaust du auch ständig rüber?": "Always looking over the fence?",
    "Wie gemütlich ist deine Blase?": "How comfy is your bubble?", "Sagst du auch zu allem Ja?": "Do you say yes to everything?",
})


def tr(s):
    if LANG != "en" or not s: return s
    if s.startswith("TAG "): return "DAY " + s[4:]
    if s.startswith("MINDSET-SERIE #"): return "MINDSET SERIES #" + s[15:]
    if s.startswith("Folge für Teil "): return "Follow for part " + s[15:]
    return EN.get(s, s)


# ------------------------------------------------------------------ basics
def C(rgb, a=1.0): return skia.Color4f(rgb[0] / 255, rgb[1] / 255, rgb[2] / 255, a)


def P(rgb, a=1.0, stroke=0, blur=0):
    p = skia.Paint(AntiAlias=True); p.setColor4f(C(rgb, a))
    if stroke:
        p.setStyle(skia.Paint.kStroke_Style); p.setStrokeWidth(stroke)
        p.setStrokeJoin(skia.Paint.kRound_Join); p.setStrokeCap(skia.Paint.kRound_Cap)
    if blur: p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    return p


def poly(pts, close=True):
    path = skia.Path(); path.moveTo(*pts[0])
    for q in pts[1:]: path.lineTo(*q)
    if close: path.close()
    return path


def lerp(a, b, u): return a + (b - a) * u
def lerpc(c1, c2, u): return tuple(lerp(x, y, u) for x, y in zip(c1, c2))
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)
def seg(t, a, b): return ease((t - a) / (b - a))


def text(c, s, x, y, tf, size, rgb, a=1.0, align="center", spacing=0, stroke=0):
    if a <= 0: return
    s = tr(s)
    f = skia.Font(tf, size)
    ws = [f.measureText(ch) + spacing for ch in s]; tw = sum(ws) - spacing
    if tw > 990 and align == "center":
        size = size * 990 / tw; f = skia.Font(tf, size)
        ws = [f.measureText(ch) + spacing for ch in s]; tw = sum(ws) - spacing
    if align == "center": x -= tw / 2
    elif align == "right": x -= tw
    def draw(p):
        xx = x
        for ch, wd in zip(s, ws): c.drawString(ch, xx, y, f, p); xx += wd
    if stroke: draw(P((0, 0, 0), a * 0.8, stroke=stroke))
    draw(P(rgb, a))


def label(c, s, x, y, col, a=1.0):
    text(c, s, x, y, F_SANS, 24, col, a, spacing=4, stroke=5)


def sky(c, t, top, mid, hor, horizon, stars=0.0, seed=4):
    sh = skia.GradientShader.MakeLinear([(0, -400), (0, horizon)], [C(top), C(mid), C(hor)], [0, 0.6, 1])
    c.drawRect(skia.Rect.MakeLTRB(-300, -500, W + 300, H + 300), skia.Paint(Shader=sh))
    if stars > 0:
        rng = np.random.default_rng(seed)
        for i in range(120):
            x, y = rng.uniform(-200, W + 200), rng.uniform(-400, horizon - 200); ph = rng.uniform(0, 6.3)
            a = (0.3 + 0.4 * (0.5 + 0.5 * math.sin(t * 2 + ph))) * stars * clamp((horizon - 300 - y) / 300)
            if a > 0.02: c.drawCircle(x, y, 1.5 + (ph > 5.6), P((230, 235, 255), a))


def moon(c, x, y, a=1.0):
    if a <= 0: return
    c.drawCircle(x, y, 150, P((240, 230, 190), 0.18 * a, blur=70))
    c.drawCircle(x, y, 52, P((250, 244, 215), a))
    c.drawCircle(x - 14, y - 10, 11, P((225, 218, 190), 0.5 * a))
    c.drawCircle(x + 18, y + 14, 7, P((225, 218, 190), 0.5 * a))


def sun(c, x, y, a=1.0, r=78):
    if a <= 0: return
    c.drawCircle(x, y, 520, P((255, 170, 90), 0.30 * a, blur=160))
    c.drawCircle(x, y, 200, P((255, 200, 120), 0.45 * a, blur=60))
    c.drawCircle(x, y, r, P((255, 236, 190), a))


def hills(c, base, col, amp=40, off=1.0, a=0.9, height=130):
    hp = skia.Path(); hp.moveTo(-300, base)
    for i in range(-300, W + 301, 60):
        hp.lineTo(i, base - height - amp * math.sin(i * 0.008 + off) - amp * 0.6 * math.sin(i * 0.021 + off))
    hp.lineTo(W + 300, base + 5); hp.lineTo(-300, base + 5); hp.close()
    c.drawPath(hp, P(col, a))


def ground(c, y, g1, g2, line):
    gs = skia.GradientShader.MakeLinear([(0, y), (0, H)], [C(g1), C(g2)])
    c.drawRect(skia.Rect.MakeLTRB(-300, y, W + 300, H + 300), skia.Paint(Shader=gs))
    c.drawPath(poly([(-300, y), (W + 300, y)], close=False), P(line, 0.7, stroke=3))


def vignette(c, amt=0.5):
    vg = skia.GradientShader.MakeRadial((540, 900), 1250, [C((0, 0, 0), 0), C((0, 0, 0), amt)])
    c.drawRect(skia.Rect.MakeWH(W, H), skia.Paint(Shader=vg))


def shadow(c, x, y, s=0.9, a=0.35, w=1.0):
    """weicher Kontaktschatten unter den Füßen"""
    c.drawOval(skia.Rect.MakeXYWH(x - 46 * s * w, y - 7 * s, 92 * s * w, 16 * s), P((0, 0, 0), a, blur=6))


def haze(c, y, col, a=0.35, h=260):
    """Dunst über dem Horizont (Tiefe)"""
    sh = skia.GradientShader.MakeLinear([(0, y - h), (0, y)], [C(col, 0), C(col, a)])
    c.drawRect(skia.Rect.MakeLTRB(-300, y - h, W + 300, y + 2), skia.Paint(Shader=sh))


def tufts(c, y, col, seed=3, n=26, a=0.8, x0=-100, x1=W + 100, size=1.0):
    """Grasbüschel/Bodendetails im Vordergrund"""
    rng = np.random.default_rng(seed)
    for _ in range(n):
        x = rng.uniform(x0, x1); yy = y + rng.uniform(4, 60); h = rng.uniform(10, 26) * size
        for k in (-1, 0, 1):
            c.drawLine(x, yy, x + k * 6 * size, yy - h * (1 - 0.2 * abs(k)), P(col, a, stroke=3))


_GRAIN = []
def grain(c, t, amt=0.05):
    """feines Filmkorn (vorberechnet, deterministisch)"""
    if not _GRAIN:
        rng = np.random.default_rng(11)
        for _ in range(4):
            g = (rng.random((480, 270)) * 255).astype(np.uint8)
            rgba = np.dstack([g, g, g, np.full_like(g, 255)])
            _GRAIN.append(skia.Image.fromarray(rgba, colorType=skia.kRGBA_8888_ColorType))
    img = _GRAIN[int(t * FPS) % 4]
    p = skia.Paint(); p.setAlphaf(amt); p.setBlendMode(skia.BlendMode.kOverlay)
    c.drawImageRect(img, skia.Rect.MakeWH(W, H), skia.SamplingOptions(), p)


def plate_label(c, s, x, y, col, a=1.0):
    """Name mit dezenter dunkler Platte (lesbar vor Bäumen/Himmel)"""
    s2 = tr(s); f = skia.Font(F_SANS, 24); tw = sum(f.measureText(ch) + 4 for ch in s2) - 4
    r = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - tw / 2 - 14, y - 26, tw + 28, 36), 18, 18)
    c.drawRRect(r, P((10, 12, 20), 0.42 * a))
    label(c, s, x, y, col, a)


END_Y_MAX = 1290   # the last line must stay above TikTok's caption/username area (y >= 1450)


END_MAXW = 660


def end_text(c, t, t0, l1, l2, l3, y=1420):
    """two white lines + one amber punchline in the ground area (kept above TikTok's caption zone)"""
    if t < t0: return
    y = min(y, END_Y_MAX)
    a = ease((t - t0) / 0.5)
    c.drawRect(skia.Rect.MakeWH(W, H), P((0, 0, 0), 0.35 * a))
    def fit(s_, size):   # keep every line clear of TikTok's button column (x > 880): max 680 px wide around x 540
        w_ = skia.Font(F_CAP, size).measureText(tr(s_))
        return size * min(1.0, END_MAXW / w_) if w_ > 0 else size
    text(c, l1, 540, y, F_CAP, fit(l1, 56), (255, 255, 255), a, stroke=12)
    if l2: text(c, l2, 540, y + 68, F_CAP, fit(l2, 56), (255, 255, 255), a, stroke=12)
    b = ease((t - t0 - 0.8) / 0.4)
    text(c, l3, 540, y + 152, F_CAP, fit(l3, 60), AMBER, b, stroke=12)


def bubble(c, x, y, s, a=1.0, kind="think", tail=None, size=30, col=(255, 255, 255), pop=1.0):
    """thought or speech bubble centred at x,y; tail=(tx,ty) points at the head"""
    if a <= 0: return
    s = tr(s)
    if pop != 1.0:
        c.save(); c.translate(x, y); c.scale(pop, pop); c.translate(-x, -y)
    f = skia.Font(F_SANS, size); tw = f.measureText(s)
    w, h = tw + 44, size + 30
    r = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h), h / 2, h / 2)
    if tail:
        tx, ty = tail
        if kind == "think":
            for k, rr in ((0.45, 9), (0.75, 6)):
                cx, cy = lerp(x, tx, k), lerp(y + h / 2, ty, k)
                c.drawCircle(cx, cy, rr + 3, P(INK, a)); c.drawCircle(cx, cy, rr, P(col, a))
        else:
            tri = poly([(x - 14, y + h / 2 - 4), (x + 14, y + h / 2 - 4), (lerp(x, tx, 0.6), lerp(y + h / 2, ty, 0.6))])
            c.drawPath(tri, P(INK, a, stroke=7)); c.drawPath(tri, P(col, a))
    c.drawRRect(r, P(INK, a, stroke=7)); c.drawRRect(r, P(col, a))
    c.drawString(s, x - tw / 2, y + size * 0.36, f, P(INK, a))
    if pop != 1.0: c.restore()


# ------------------------------------------------------------------ figure
L = dict(torso=72, neck=10, head=19, up=36, fore=34, thigh=42, shin=42)
# Joint convention (side view, facing = +1 means looking right). Angles in degrees, 0 = hanging straight down,
# +90 = pointing forward (where the figure looks), 180 = straight up, -90 = pointing backward.
#   arm_x  = upper-arm angle at the shoulder        elb_x = elbow FLEXION, 0 (straight) … 155 (fully bent): forearm angle = arm_x + elb_x
#   leg_x  = thigh angle at the hip                  knee_x = knee FLEXION, 0 … 160: shin angle = leg_x - knee_x
# A negative elb/knee would bend the joint backwards (broken-looking), so JOINT_LIMITS clamps it.
# fore_x (0.3 … 1) shortens a forearm that points toward/away from the camera (crossed arms, hands on hips, pockets).
JOINT_LIMITS = True
HEAD_TILT = 30.0        # head can look up/down at most this much relative to the torso
_WARNED = []


def _warn_joint(what):
    """printed once per run: a pose asked for a backwards elbow (it is clamped to straight)"""
    _WARNED.append(what)
    if len(_WARNED) > 1: return
    print(f"WARNING joint: {what} bends the elbow backwards – clamped to 0. Rewrite the pose with a positive elbow "
          f"(see episodes.md 'Joints bend only the right way').", file=sys.stderr)
ELBOW = (0.0, 155.0)
KNEE = (0.0, 160.0)
ARM_ROOT = 0.9          # arms attach at 90 % of the torso (real shoulder), not at the neck base


def V(a, facing):
    r = math.radians(a); return (math.sin(r) * facing, math.cos(r))


def pose_points(p, s, facing):
    lean = p.get("lean", 0)
    ux, uy = math.sin(math.radians(lean)) * facing, -math.cos(math.radians(lean))
    sh = (ux * L["torso"] * s, uy * L["torso"] * s)
    nk = (sh[0] + ux * L["neck"] * s, sh[1] + uy * L["neck"] * s)
    ha = math.radians(lean + p.get("head", 0))
    hd = (nk[0] + math.sin(ha) * facing * L["head"] * s, nk[1] - math.cos(ha) * L["head"] * s)
    sa = (ux * L["torso"] * s * ARM_ROOT, uy * L["torso"] * s * ARM_ROOT)     # shoulder joint, below the neck base
    J = dict(hip=(0, 0), sh=sh, sa=sa, head=hd)
    for side in ("f", "b"):
        a = p.get(f"arm_{side}", 0); e = p.get(f"elb_{side}", 10)
        if JOINT_LIMITS:                                                # elbows only bend one way
            if e < ELBOW[0] - 2: _warn_joint(f"elb_{side}={e:.0f}")
            e = clamp(e, ELBOW[0], ELBOW[1])
        fs = p.get(f"fore_{side}", 1.0)                                 # < 1: forearm points toward/away from the camera
        d1 = V(a, facing); el = (sa[0] + d1[0] * L["up"] * s, sa[1] + d1[1] * L["up"] * s)
        d2 = V(a + e, facing); hn = (el[0] + d2[0] * L["fore"] * s * fs, el[1] + d2[1] * L["fore"] * s * fs)
        cr = p.get("crossed", 0)
        if cr > 0:   # folded arms seen from the side: the forearm runs across the chest (out-of-plane, so no joint limit)
            dc = V(-84 if side == "f" else -78, facing); fc = L["fore"] * s * 0.62
            hc = (el[0] + dc[0] * fc, el[1] + dc[1] * fc)
            hn = (lerp(hn[0], hc[0], cr), lerp(hn[1], hc[1], cr))
        tt = p.get(f"leg_{side}", 0); k = p.get(f"knee_{side}", 0)
        if JOINT_LIMITS: k = clamp(k, KNEE[0], KNEE[1])                 # knees only bend one way
        d3 = V(tt, facing); kn = (d3[0] * L["thigh"] * s, d3[1] * L["thigh"] * s)
        d4 = V(tt - k, facing); ft = (kn[0] + d4[0] * L["shin"] * s, kn[1] + d4[1] * L["shin"] * s)
        J[f"el_{side}"], J[f"hand_{side}"], J[f"knee_{side}"], J[f"foot_{side}"] = el, hn, kn, ft
    return J


FACE_CUE = os.environ.get("FACE_CUE", "1") != "0"   # nose + eye show where a figure looks (from #12; set FACE_CUE=0 for the old faceless look)
FACE_CUE_NOSE_FILL = True
NOW = None   # current video time (set by render/stills) – used for idle breathing


def _round_paint(rgb, a, w):
    p = P(rgb, a, stroke=w); p.setStrokeCap(skia.Paint.kRound_Cap); p.setStrokeJoin(skia.Paint.kRound_Join); return p


def _op(a, b, op):
    """skia path boolean op that never crashes: falls back to a plain winding merge (union) or nothing (difference)"""
    try:
        return skia.Op(a, b, op)
    except RuntimeError:
        if op == skia.PathOp.kUnion_PathOp:
            out = skia.Path(a); out.addPath(b); out.setFillType(skia.PathFillType.kWinding); return out
        return skia.Path()


def _quad(a, b, wa, wb):
    """tapered capsule from a (width wa) to b (width wb) as a filled path"""
    dx, dy = b[0] - a[0], b[1] - a[1]; ln = math.hypot(dx, dy) or 1e-3
    nx, ny = -dy / ln, dx / ln
    pth = skia.Path()
    pth.moveTo(a[0] + nx * wa / 2, a[1] + ny * wa / 2); pth.lineTo(b[0] + nx * wb / 2, b[1] + ny * wb / 2)
    pth.lineTo(b[0] - nx * wb / 2, b[1] - ny * wb / 2); pth.lineTo(a[0] - nx * wa / 2, a[1] - ny * wa / 2); pth.close()
    ca = skia.Path(); ca.addCircle(a[0], a[1], wa / 2); cb = skia.Path(); cb.addCircle(b[0], b[1], wb / 2)
    return _op(_op(pth, ca, skia.PathOp.kUnion_PathOp), cb, skia.PathOp.kUnion_PathOp)


def _ik_angles(dx, dy, a, b, facing, knee=False):
    """2-bone IK in the side-view convention: returns (root_angle, flexion) so the chain end lands on (dx, dy)
    elbows flex forward (+), knees flex backward (shin = thigh - knee)"""
    f = 1 if facing >= 0 else -1
    b = max(b, 1e-3); d = max(abs(a - b) + 1e-3, min(a + b - 1e-3, math.hypot(dx, dy)))
    th = math.degrees(math.atan2(dx * f, dy))
    al = math.degrees(math.acos(max(-1, min(1, (a * a + d * d - b * b) / (2 * a * d)))))
    inner = math.degrees(math.acos(max(-1, min(1, (a * a + b * b - d * d) / (2 * a * b)))))
    flex = 180 - inner
    return (th + al, flex) if knee else (th - al, flex)


def figure(c, x, y, p, s=0.8, facing=1, rot=0.0, body=WHITE, mode="feet", lift=0.0, rim=None, light=(-1, -1),
           reach=None, plant=None):
    """draw figure; mode 'feet': lowest foot on y; 'hip': hip at (x,y). returns dict of world joints
    v2: tapered limbs, shaped torso, neck, hands, feet, soft shading, idle breathing
    reach={'f': (wx, wy), 'b': ...}: hands grab these WORLD points (IK, elbows bend the right way)
    plant={'f': (wx, wy), ...}: feet stand on these WORLD points (IK, only with mode='hip', e.g. on ladder rungs)
    facing may be fractional (-1 … 1): a figure turning around squeezes through 0 instead of flipping"""
    if NOW is not None:
        br = math.sin(NOW * 2.3 + x * 0.017)
        p = dict(p); p["arm_f"] = p.get("arm_f", 0) + 1.6 * br; p["arm_b"] = p.get("arm_b", 0) - 1.2 * br
        p["head"] = p.get("head", 0) + 1.0 * math.sin(NOW * 1.1 + x * 0.01)
    if abs(facing) < 0.12: facing = 0.12 if facing >= 0 else -0.12
    p = dict(p); p["head"] = clamp(p.get("head", 0), -HEAD_TILT, HEAD_TILT)     # no broken necks
    J = pose_points(p, s, facing)
    if mode == "feet":
        low = max(J["foot_f"][1], J["foot_b"][1]); hx, hy = x, y - low - 6 * s - lift
    else:
        hx, hy = x, y
    if reach or plant:
        cr, sr = math.cos(math.radians(-rot)), math.sin(math.radians(-rot))
        def local(wp):
            dx, dy = wp[0] - hx, wp[1] - hy
            return (dx * cr - dy * sr) / abs(facing), (dx * sr + dy * cr)
        if reach: p["crossed"] = 0                    # a grabbing hand cannot stay folded on the chest
        for side, wp in (reach or {}).items():
            lx_, ly_ = local(wp); sa = J["sa"]
            p[f"arm_{side}"], p[f"elb_{side}"] = _ik_angles(lx_ - sa[0], ly_ - sa[1], L["up"] * s, L["fore"] * s * p.get(f"fore_{side}", 1.0), facing)
        if mode != "feet":
            for side, wp in (plant or {}).items():
                lx_, ly_ = local(wp)
                p[f"leg_{side}"], p[f"knee_{side}"] = _ik_angles(lx_, ly_ - 6 * s, L["thigh"] * s, L["shin"] * s, facing, knee=True)
        J = pose_points(p, s, facing)
    c.save(); c.translate(hx, hy); c.rotate(rot)
    lw = 17 * s; OL = 7
    back = tuple(v * 0.80 for v in body)
    lx, ly = light; ln = math.hypot(lx, ly) or 1; lx, ly = lx / ln, ly / ln

    def shade(shape, col, w):
        """soft volume: dark core on the side away from the light, rim on the light side"""
        c.save(); c.clipPath(shape, doAntiAlias=True)
        m = skia.Matrix(); m.setTranslate(-lx * w * 0.42, -ly * w * 0.42)
        sh = skia.Path(); shape.transform(m, sh)
        q = P((20, 22, 40), 0.16, blur=w * 0.18)
        inv = skia.Path(); inv = _op(shape, sh, skia.PathOp.kDifference_PathOp)
        c.drawPath(inv, q)
        if rim:
            m2 = skia.Matrix(); m2.setTranslate(-lx * w * 0.30, -ly * w * 0.30)
            r2 = skia.Path(); shape.transform(m2, r2)
            rr = skia.Path(); rr = _op(shape, r2, skia.PathOp.kDifference_PathOp)
            c.drawPath(rr, P(rim[0], rim[1], blur=w * 0.06))
        c.restore()

    def limb(a, b, e, col, w0, w1, w2, end=None):
        """two tapered segments a-b-e, optional end knob ('hand' or 'foot')"""
        shape = skia.Path(); shape = _op(_quad(a, b, w0, w1), _quad(b, e, w1, w2), skia.PathOp.kUnion_PathOp)
        if end == "hand":
            hp_ = skia.Path(); hp_.addCircle(e[0], e[1], w2 * 0.72); shape = _op(shape, hp_, skia.PathOp.kUnion_PathOp)
        elif end == "foot":
            ang = math.atan2(e[1] - b[1], e[0] - b[0]) - math.pi / 2 * facing * 0.95
            tip = (e[0] + math.cos(ang) * 0 + facing * 13 * s, e[1] + 2 * s)
            shape = _op(shape, _quad(e, tip, w2 * 1.05, w2 * 0.8), skia.PathOp.kUnion_PathOp)
        c.drawPath(shape, _round_paint(INK, 1, OL)); c.drawPath(shape, P(col))
        shade(shape, col, w0)
        return shape

    sh, hip, hd = J["sh"], J["hip"], J["head"]
    limb(J["sa"], J["el_b"], J["hand_b"], back, lw * 1.0, lw * 0.86, lw * 0.74, "hand")
    limb(hip, J["knee_b"], J["foot_b"], back, lw * 1.12, lw * 0.92, lw * 0.78, "foot")
    # neck
    nk = skia.Path(); nk.addPath(_quad(sh, hd, lw * 0.62, lw * 0.5))
    c.drawPath(nk, _round_paint(INK, 1, OL)); c.drawPath(nk, P(body))
    limb(hip, J["knee_f"], J["foot_f"], body, lw * 1.12, lw * 0.92, lw * 0.78, "foot")
    # torso: broad chest, narrower waist, slightly wider hips
    tx, ty = sh[0] - hip[0], sh[1] - hip[1]
    chest = (hip[0] + tx * 0.72, hip[1] + ty * 0.72); waist = (hip[0] + tx * 0.35, hip[1] + ty * 0.35)
    torso = skia.Path(); torso = _op(_quad(hip, waist, lw * 1.55, lw * 1.38), _quad(waist, chest, lw * 1.38, lw * 1.78), skia.PathOp.kUnion_PathOp)
    torso = _op(torso, _quad(chest, sh, lw * 1.78, lw * 1.5), skia.PathOp.kUnion_PathOp)
    c.drawPath(torso, _round_paint(INK, 1, OL)); c.drawPath(torso, P(body)); shade(torso, body, lw * 1.6)
    # head: slightly egg-shaped, tilted with the neck
    hr = L["head"] * s
    hang = math.degrees(math.atan2(hd[0] - sh[0], -(hd[1] - sh[1])))
    head = skia.Path(); head.addOval(skia.Rect.MakeXYWH(hd[0] - hr * 0.93, hd[1] - hr * 1.06, hr * 1.86, hr * 2.08))
    m = skia.Matrix(); m.setRotate(hang, hd[0], hd[1]); head.transform(m)
    if FACE_CUE and abs(facing) >= 0.5:      # small nose bump on the facing side (drawn first, so the head covers its root)
        f = 1 if facing > 0 else -1
        c.save(); c.rotate(hang, hd[0], hd[1])
        nose = skia.Path(); nose.addOval(skia.Rect.MakeXYWH(hd[0] + f * hr * 1.0 - hr * 0.25, hd[1] - hr * 0.12, hr * 0.5, hr * 0.38))
        c.drawPath(nose, _round_paint(INK, 1, 6)); c.drawPath(nose, P(body))
        c.restore()
    c.drawPath(head, _round_paint(INK, 1, 7)); c.drawPath(head, P(body)); shade(head, body, hr * 1.6)
    if FACE_CUE and abs(facing) >= 0.5:      # one calm eye looking where the figure faces
        f = 1 if facing > 0 else -1
        c.save(); c.rotate(hang, hd[0], hd[1])
        if FACE_CUE_NOSE_FILL:
            c.drawOval(skia.Rect.MakeXYWH(hd[0] + f * hr * 0.86 - hr * 0.13, hd[1] - hr * 0.05, hr * 0.26, hr * 0.26), P(body))
        c.drawOval(skia.Rect.MakeXYWH(hd[0] + f * hr * 0.46 - hr * 0.13, hd[1] - hr * 0.42, hr * 0.26, hr * 0.32), P(INK, 0.9))
        c.restore()
    c.drawCircle(hd[0] + lx * hr * 0.38, hd[1] + ly * hr * 0.38, hr * 0.22, P((255, 255, 255), 0.28, blur=hr * 0.15))
    limb(J["sa"], J["el_f"], J["hand_f"], body, lw * 1.0, lw * 0.86, lw * 0.74, "hand")
    c.restore()
    m = skia.Matrix(); m.setTranslate(hx, hy); m.preRotate(rot)
    out = {k: m.mapXY(*v) for k, v in J.items()}
    out = {k: (v.x(), v.y()) for k, v in out.items()}
    if FIG_LOG is not None:
        FIG_LOG.append(dict(x=hx, y=hy, f=facing, j=out, reach=dict(reach or {}), plant=dict(plant or {}) if mode != "feet" else {}))
    return out


FIG_LOG = None      # list while figure_qa() runs


def figure_qa(frame_fn, t_end, fps=15, t0=0.0):
    """automatic figure check before rendering. Runs the frame function at `fps` and reports
    flips (facing jumps instead of a turn), teleports (body/hand jumps), hands/feet that miss their IK target,
    and backwards joints. Returns a list of problems; empty = clean."""
    global FIG_LOG, NOW
    surf = skia.Surface(W, H); c = surf.getCanvas()
    probs, prev = [], None
    warned0 = len(_WARNED)
    n = int((t_end - t0) * fps)
    for i in range(n):
        t = t0 + i / fps; NOW = t
        FIG_LOG = []
        c.clear(skia.ColorBLACK); frame_fn(c, t)
        cur = FIG_LOG
        for k, fg in enumerate(cur):
            for side, wp in fg["reach"].items():
                hnd = fg["j"][f"hand_{side}"]; d = math.hypot(hnd[0] - wp[0], hnd[1] - wp[1])
                if d > 8: probs.append(f"{t:5.2f}s figure {k}: hand_{side} misses its target by {d:.0f} px (out of reach – move the figure closer)")
            for side, wp in fg["plant"].items():
                ft = fg["j"][f"foot_{side}"]; d = math.hypot(ft[0] - wp[0], ft[1] - wp[1])
                if d > 14: probs.append(f"{t:5.2f}s figure {k}: foot_{side} misses its step by {d:.0f} px")
            if prev is not None and k < len(prev):
                pf = prev[k]
                if abs(fg["f"] - pf["f"]) > 1.0: probs.append(f"{t:5.2f}s figure {k}: facing flips {pf['f']:+.1f} -> {fg['f']:+.1f} (use smooth() so it turns)")
                if math.hypot(fg["x"] - pf["x"], fg["y"] - pf["y"]) > 2400 / fps: probs.append(f"{t:5.2f}s figure {k}: body jumps {math.hypot(fg['x'] - pf['x'], fg['y'] - pf['y']):.0f} px")
                for side in ("f", "b"):
                    a_, b_ = fg["j"][f"hand_{side}"], pf["j"][f"hand_{side}"]
                    if math.hypot(a_[0] - b_[0], a_[1] - b_[1]) > 3000 / fps: probs.append(f"{t:5.2f}s figure {k}: hand_{side} teleports {math.hypot(a_[0] - b_[0], a_[1] - b_[1]):.0f} px")
        prev = cur
    FIG_LOG = None; NOW = None
    probs += [f"backwards joint requested: {w}" for w in _WARNED[warned0:]]
    return probs


def _first(vals, k):
    for v in vals:
        if k in v: return v[k]
    return 0


def _avg(vals, ws):
    v0 = vals[len(vals) // 2]
    if any(isinstance(v, (tuple, list)) for v in vals):     # IK targets: blend points, keep the current one if shapes differ
        if all(isinstance(v, (tuple, list)) and len(v) == len(v0) for v in vals):
            return tuple(sum(w * v[i] for v, w in zip(vals, ws)) for i in range(len(v0)))
        return v0
    if isinstance(v0, bool) or not isinstance(v0, (int, float, dict, tuple)): return v0
    if isinstance(v0, dict):
        if not all(isinstance(v, dict) for v in vals): return v0
        out = {}
        for k in set().union(*[v.keys() for v in vals]):
            if k not in v0 and not isinstance(_first(vals, k), (int, float)): continue   # a target the current frame does not use
            if isinstance(v0.get(k), (tuple, list)):                                   # IK target: blend only where it exists
                pts = [(v[k], w) for v, w in zip(vals, ws) if isinstance(v.get(k), (tuple, list)) and len(v[k]) == len(v0[k])]
                sw_ = sum(w for _, w in pts)
                out[k] = tuple(sum(w * q[i] for q, w in pts) / sw_ for i in range(len(v0[k])))
            else:
                out[k] = _avg([v.get(k, _pdef(k)) for v in vals], ws)
        return out
    if isinstance(v0, tuple): return v0
    return sum(w * v for v, w in zip(vals, ws))


def smooth(fn, t, w=0.12, n=7):
    """temporal low-pass of a character function fn(t) -> dict(x, y, p, ...):
    hard pose switches become ~0.2 s blends; numeric fields and poses are averaged"""
    ts = [t + w * (2 * i / (n - 1) - 1) for i in range(n)]
    ws = [1 - abs(2 * i / (n - 1) - 1) * 0.85 for i in range(n)]; sw = sum(ws); ws = [x / sw for x in ws]
    vals = [fn(tt) for tt in ts]
    mid = vals[n // 2]
    out = dict(mid)
    for k in mid:
        if k == "mode": continue                           # discrete: keep the current value
        if k in ("f", "facing"):                           # continuous turn: -1 … 1 through 0 (no flip, no ghosting)
            if all(k in v for v in vals): out[k] = sum(w * v[k] for v, w in zip(vals, ws))
            continue
        if all(k in v for v in vals): out[k] = _avg([v[k] for v in vals], ws)
    return out


def path_stroke(path, w):
    """Fläche eines dicken Strichs (für das Beschneiden des Lichtsaums)"""
    p = skia.Paint(AntiAlias=True); p.setStyle(skia.Paint.kStroke_Style); p.setStrokeWidth(w)
    p.setStrokeCap(skia.Paint.kRound_Cap); p.setStrokeJoin(skia.Paint.kRound_Join)
    out = skia.Path(); p.getFillPath(path, out); return out


def _pdef(k): return 1.0 if k.startswith("fore_") else 10 if k.startswith("elb") else 0   # "crossed" defaults to 0


def mix(a, b, u):
    return {k: lerp(a.get(k, _pdef(k)), b.get(k, _pdef(k)), u) for k in set(a) | set(b)}


def stand(): return dict(lean=0, arm_f=6, arm_b=-6, elb_f=8, elb_b=8, leg_f=3, leg_b=-3)


def walk(ph, lean=6, stride=24, arm=32):
    sn = math.sin(ph); sa = math.sin(ph - 0.35)          # arms trail the legs slightly (follow-through)
    def knee(q):  # lifts during the swing, slight flex at heel strike
        return 6 + 38 * max(0.0, math.sin(q)) ** 1.5
    return dict(lean=lean + 1.5 * math.sin(2 * ph), head=-lean * 0.6 - 1.5 * math.sin(2 * ph),
                arm_f=-arm * sa + 4, arm_b=arm * sa + 4, elb_f=14 + 26 * max(0, -sa), elb_b=14 + 26 * max(0, sa),
                leg_f=stride * sn + lean * 0.4, leg_b=-stride * sn + lean * 0.4,
                knee_f=knee(ph + 1.3), knee_b=knee(ph + 1.3 + math.pi))


def run(ph):
    sn = math.sin(ph)
    return dict(lean=16, head=-10, arm_f=-45 * sn + 5, arm_b=45 * sn + 5, elb_f=88, elb_b=88,
                leg_f=40 * sn + 10, leg_b=-40 * sn + 10,
                knee_f=max(10, 80 * math.sin(ph + 1.2)), knee_b=max(10, 80 * math.sin(ph + 1.2 + math.pi)))


def crouch(): return dict(lean=30, head=-20, arm_f=-30, elb_f=20, arm_b=-40, elb_b=20, leg_f=70, leg_b=50, knee_f=110, knee_b=100)


def airborne(): return dict(lean=10, head=-10, arm_f=150, elb_f=10, arm_b=-140, elb_b=10, leg_f=50, leg_b=-30, knee_f=70, knee_b=20)


def cheer(t):
    b = math.sin(t * 6) * 8
    return dict(lean=-4, head=-18, arm_f=150 + b, elb_f=12, arm_b=-150 - b, elb_b=12, leg_f=10, leg_b=-10)


def arms_crossed(head=0):
    return dict(lean=-4, head=head, arm_f=40, elb_f=0, arm_b=34, elb_b=0, crossed=1.0, leg_f=8, leg_b=-8)   # elbows forward, forearms across the chest


def hands_on_hips(): return dict(lean=-3, head=-4, arm_f=-8, elb_f=95, fore_f=0.45, arm_b=-14, elb_b=95, fore_b=0.45, leg_f=6, leg_b=-6)
def shrug(k=1.0):     # palms up, elbows at the waist, shoulders "up" via a small lean back
    return dict(lean=-3 * k, head=-10 * k, arm_f=12, elb_f=80 * k + 8, arm_b=6, elb_b=76 * k + 8, leg_f=6, leg_b=-6)
def offer(): return dict(lean=6, head=4, arm_f=72, elb_f=18, arm_b=-4, elb_b=12, leg_f=6, leg_b=-6)   # hand held out


def sit(t=0):  # on a bench, hip at bench height
    return dict(lean=4, head=0, arm_f=20, elb_f=40, arm_b=14, elb_b=40, leg_f=88, leg_b=82, knee_f=88, knee_b=84)


def think(t):  # hand on chin, slight sway
    sw = math.sin(t * 1.7) * 3
    return dict(lean=6 + sw, head=12, arm_f=20, elb_f=150, arm_b=8, elb_b=92, fore_b=0.42, leg_f=3, leg_b=-3)


def slump():
    return dict(lean=35, head=25, arm_f=8, elb_f=10, arm_b=4, elb_b=10, leg_f=-2, leg_b=-6)


def climb_rope(ph):  # hanging, hand over hand
    sn = math.sin(ph)
    return dict(lean=0, head=-25, arm_f=168 + 10 * sn, elb_f=14 + 12 * sn, arm_b=-172 + 10 * sn, elb_b=14 - 12 * sn,
                leg_f=30 + 15 * sn, leg_b=10 - 15 * sn, knee_f=50, knee_b=40)


# ------------------------------------------------------------------ render
def render(frame_fn, t_end, out):
    surf = skia.Surface(W, H); c = surf.getCanvas()
    tmp = out[:-4] + ".part.mp4"
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS),
                           "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", tmp],
                          stdin=subprocess.PIPE)
    global NOW
    sub = int(os.environ.get("MBLUR", "3"))
    for f in range(int(t_end * FPS)):
        acc = None
        for k in range(sub):
            t = (f + (k - (sub - 1) / 2) / sub * 0.5) / FPS if sub > 1 else f / FPS   # 180° shutter
            c.clear(skia.ColorBLACK); NOW = t
            frame_fn(c, max(0.0, t))
            arr = surf.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)
            acc = arr.astype(np.uint16) if acc is None else acc + arr
        out_f = (acc // sub).astype(np.uint8) if sub > 1 else acc.astype(np.uint8)
        ff.stdin.write(out_f.tobytes())
    ff.stdin.close()
    if ff.wait() == 0: os.replace(tmp, out)


def stills(frame_fn, ts, prefix):
    from PIL import Image
    ims = []
    for tt in ts:
        global NOW
        NOW = tt
        surf = skia.Surface(W, H); c = surf.getCanvas(); c.clear(skia.ColorBLACK); frame_fn(c, tt)
        arr = surf.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)
        ims.append(Image.fromarray(arr[:, :, :3]).resize((360, 640)))
    cols = 3; rows = (len(ims) + 2) // 3
    sheet = Image.new("RGB", (360 * cols, 640 * rows))
    for i, im in enumerate(ims): sheet.paste(im, ((i % cols) * 360, (i // cols) * 640))
    sheet.save(prefix + "_sheet.jpg", quality=86)


def series_overlay(c, t, num, hook, end_at, follow_y=380, series=None, cta=None):
    """hook (first seconds), series tag, call to action at the end.
    num = the part number SHOWN to viewers (TikTok numbering); cta = concrete cliffhanger text ("\n" = 2 lines),
    shown from end_at – keep at least 1.5 s on screen (default: "Follow for part num+1")"""
    text(c, f"{series} #{num}" if series else f"MINDSET-SERIE #{num}", 540, 300, F_SANS, 32, AMBER, 0.95, spacing=3, stroke=7)
    a = 1 - seg(t, 4.2, 4.8)
    if a > 0:
        pop = 1 + 0.12 * (1 - ease(t / 0.25))
        c.save(); c.translate(540, 380); c.scale(pop, pop)
        for i, ln in enumerate(hook.split("\n")):   # "\n" splits the hook into stacked lines
            text(c, ln, 0, i * 66, F_CAP, 62, (255, 255, 255), a, stroke=14)
        c.restore()
    b = seg(t, end_at, end_at + 0.4)
    if b > 0:
        pop = 1 + 0.15 * (1 - ease((t - end_at) / 0.3))
        c.save(); c.translate(540, follow_y); c.scale(pop, pop)
        lines = cta.split("\n") if cta else [f"Folge für Teil {num + 1}"]
        for i, ln in enumerate(lines):
            sz = 58 if i == 0 else 50
            w_ = skia.Font(F_CAP, sz).measureText(tr(ln)); sz *= min(1.0, 900 / w_) if w_ else 1   # y 380 is above the button column
            text(c, ln, 0, i * 64, F_CAP, sz, AMBER if i == 0 else (255, 255, 255), b, stroke=14)
        c.restore()


def _grade_paint(sat=1.12, lift=0.025):
    lr, lg, lb = 0.2126, 0.7152, 0.0722
    m = [lr * (1 - sat) + sat, lg * (1 - sat), lb * (1 - sat), 0, lift,
         lr * (1 - sat), lg * (1 - sat) + sat, lb * (1 - sat), 0, lift,
         lr * (1 - sat), lg * (1 - sat), lb * (1 - sat) + sat, 0, lift,
         0, 0, 0, 1, 0]
    return skia.Paint(ColorFilter=skia.ColorFilters.Matrix(m))


_GRADE = None


def finish_v2(name, frame_fn, t_end, events, turn, num, hook, off, end_at, follow_y=380, series=None, cta=None):
    """improved cut: skips the idle start, adds hook/series/follow overlay.
    v3 (audit fixes): punch-in camera at the start + slow drift (no dead seconds), light vibrance grade,
    sound with an audible opening hit (CC0 SFX via kanaele/data/dsound.py)"""
    global _GRADE
    if _GRADE is None: _GRADE = _grade_paint()
    dur = t_end - off

    def wrapped(c, t):
        z = 1 + 0.09 * (1 - ease(t / 0.7)) + 0.035 * t / max(1.0, dur)
        c.save(); c.translate(540, 1240); c.scale(z, z); c.translate(-540, -1240)
        c.saveLayer(None, _GRADE)
        frame_fn(c, t + off)
        c.restore(); c.restore()
        series_overlay(c, t, num, hook, end_at - off, follow_y, series, cta)
    ev = []
    for e in events:
        e = list(e); e[1] = e[1] - off
        if len(e) > 2 and e[0] == "rain": e[2] = e[2] - off
        if e[1] >= -0.05 or e[0] == "rain": e[1] = max(0.0, e[1]); ev.append(e)
    ev.append(["pop", 0.05])
    dsound = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "kanaele", "data", "dsound.py")
    if os.path.exists(dsound):
        os.environ.setdefault("SOUND_PY", dsound)
        ev += [["sfx", 0.02, "boom-hit-medium", -5], ["sfx", 0.06, "whoosh-medium-soft", -6], ["sfx", turn - off, "shimmer-medium-bright", -10]]
    finish(name, wrapped, t_end - off, ev, turn - off)


def finish(name, frame_fn, t_end, events, turn):
    """render video, build soundtrack, mux"""
    d = os.environ.get("OUT_DIR") or os.path.dirname(os.path.abspath(__file__))
    de_audio = f"{d}/{name}_a.wav"
    if LANG == "en":
        json.dump(events, open(f"{d}/{name}_events.json", "w"))
        render(frame_fn, t_end, f"{d}/{name}_EN_v.mp4")
        if os.path.exists(de_audio): os.remove(de_audio)          # never reuse a stale soundtrack
        if True:
            subprocess.run(["python3", (os.environ.get("SOUND_PY") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "sound.py")), f"{d}/{name}_events.json", str(t_end), str(turn), de_audio], check=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{d}/{name}_EN_v.mp4", "-i", de_audio, "-map", "0:v", "-map", "1:a",
                        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", f"{d}/{name}_EN.mp4"], check=True)
        return
    json.dump(events, open(f"{d}/{name}_events.json", "w"))
    render(frame_fn, t_end, f"{d}/{name}_v.mp4")
    subprocess.run(["python3", (os.environ.get("SOUND_PY") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "sound.py")), f"{d}/{name}_events.json", str(t_end), str(turn), f"{d}/{name}_a.wav"], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{d}/{name}_v.mp4", "-i", f"{d}/{name}_a.wav", "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", f"{d}/{name}.mp4"], check=True)
