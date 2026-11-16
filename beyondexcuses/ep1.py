"""Folge 1: PLANER vs. MACHER – Strichfiguren-Metapher (Nacht -> Sonnenaufgang)."""
import math, os, sys, json, subprocess
import numpy as np
import skia

W, H, FPS = 1080, 1920, 30
T_END = 18.6
D = os.path.dirname(os.path.abspath(__file__))
F_SANS = skia.Typeface.MakeFromFile("/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf")
F_CAP = skia.Typeface.MakeFromFile("/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf")
INK = (22, 24, 34)


def C(rgb, a=1.0): return skia.Color4f(rgb[0] / 255, rgb[1] / 255, rgb[2] / 255, a)


def P(rgb, a=1.0, stroke=0, blur=0, cap=True):
    p = skia.Paint(AntiAlias=True); p.setColor4f(C(rgb, a))
    if stroke:
        p.setStyle(skia.Paint.kStroke_Style); p.setStrokeWidth(stroke)
        p.setStrokeJoin(skia.Paint.kRound_Join)
        p.setStrokeCap(skia.Paint.kRound_Cap if cap else skia.Paint.kButt_Cap)
    if blur: p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    return p


def poly(pts, close=True):
    path = skia.Path(); path.moveTo(*pts[0])
    for q in pts[1:]: path.lineTo(*q)
    if close: path.close()
    return path


def lerp(a, b, u): return a + (b - a) * u
def lerpc(c1, c2, u): return tuple(lerp(x, y, u) for x, y in zip(c1, c2))
def ease(x): x = min(1, max(0, x)); return x * x * (3 - 2 * x)
def clamp(x, a=0, b=1): return max(a, min(b, x))


from lib import text  # translated + auto-fit


# ------------------------------------------------------------------ figure
L = dict(torso=72, neck=10, head=19, up=36, fore=34, thigh=42, shin=42)


def V(a, facing):  # direction for angle (deg) measured from "down", positive = forward
    r = math.radians(a); return (math.sin(r) * facing, math.cos(r))


def pose_points(p, s, facing):
    """returns joints relative to hip (0,0)"""
    lean = p["lean"]
    ux, uy = math.sin(math.radians(lean)) * facing, -math.cos(math.radians(lean))
    sh = (ux * L["torso"] * s, uy * L["torso"] * s)
    nk = (sh[0] + ux * L["neck"] * s, sh[1] + uy * L["neck"] * s)
    ha = math.radians(lean + p.get("head", 0))
    hd = (nk[0] + math.sin(ha) * facing * L["head"] * s, nk[1] - math.cos(ha) * L["head"] * s)
    J = dict(hip=(0, 0), sh=sh, head=hd)
    for side in ("f", "b"):
        a = p[f"arm_{side}"]; e = p.get(f"elb_{side}", 10)
        d1 = V(a, facing); el = (sh[0] + d1[0] * L["up"] * s, sh[1] + d1[1] * L["up"] * s)
        d2 = V(a + e, facing); hn = (el[0] + d2[0] * L["fore"] * s, el[1] + d2[1] * L["fore"] * s)
        t = p[f"leg_{side}"]; k = p.get(f"knee_{side}", 0)
        d3 = V(t, facing); kn = (d3[0] * L["thigh"] * s, d3[1] * L["thigh"] * s)
        d4 = V(t - k, facing); ft = (kn[0] + d4[0] * L["shin"] * s, kn[1] + d4[1] * L["shin"] * s)
        J[f"el_{side}"], J[f"hand_{side}"], J[f"knee_{side}"], J[f"foot_{side}"] = el, hn, kn, ft
    return J


def draw_figure(c, x, y_ground, p, s=0.78, facing=1, rot=0.0, body=(244, 244, 240), light=None, ground_mode="feet"):
    J = pose_points(p, s, facing)
    if ground_mode == "feet":
        low = max(J["foot_f"][1], J["foot_b"][1])
        hx, hy = x, y_ground - low - 6 * s
    else:
        hx, hy = x, y_ground
    c.save(); c.translate(hx, hy); c.rotate(rot)
    lw = 17 * s; ow = lw + 7
    back = tuple(v * 0.80 for v in body)

    def limb(pts, col):
        path = poly(pts, close=False)
        c.drawPath(path, P(INK, stroke=ow)); c.drawPath(path, P(col, stroke=lw))
    # back limbs
    limb([J["sh"], J["el_b"], J["hand_b"]], back)
    limb([J["hip"], J["knee_b"], J["foot_b"]], back)
    # torso (tapered capsule)
    tp = poly([J["hip"], J["sh"]], close=False)
    c.drawPath(tp, P(INK, stroke=ow * 1.55)); c.drawPath(tp, P(body, stroke=lw * 1.55))
    # head
    c.drawCircle(J["head"][0], J["head"][1], L["head"] * s + 3.5, P(INK))
    c.drawCircle(J["head"][0], J["head"][1], L["head"] * s, P(body))
    # front limbs
    limb([J["hip"], J["knee_f"], J["foot_f"]], body)
    limb([J["sh"], J["el_f"], J["hand_f"]], body)
    if light:  # warm rim light on the side facing the sun
        col, amt = light
        for a, b in ((J["hip"], J["sh"]),):
            pass
        c.drawCircle(J["head"][0] + 5 * s, J["head"][1] - 5 * s, L["head"] * s * 0.55, P(col, 0.35 * amt, blur=4))
    c.restore()
    return (hx + J["head"][0], hy + J["head"][1])


def stand(): return dict(lean=0, arm_f=6, arm_b=-6, elb_f=8, elb_b=8, leg_f=3, leg_b=-3, knee_f=0, knee_b=0)


def walk(ph, lean=6, stride=24, arm=22):
    sn = math.sin(ph)
    return dict(lean=lean, head=-lean * 0.6, arm_f=-arm * sn + 4, arm_b=arm * sn + 4, elb_f=18, elb_b=18,
                leg_f=stride * sn + lean * 0.4, leg_b=-stride * sn + lean * 0.4,
                knee_f=max(0, 34 * math.sin(ph + 1.3)), knee_b=max(0, 34 * math.sin(ph + 1.3 + math.pi)))


def bend(t):  # planer leaning over table, drawing
    w = math.sin(t * 7) * 6
    return dict(lean=58, head=-12, arm_f=72 + w, elb_f=34, arm_b=60 - w * 0.5, elb_b=30, leg_f=-2, leg_b=-8, knee_f=4, knee_b=2)


def cheer(t):
    b = math.sin(t * 6) * 8
    return dict(lean=-4, head=-18, arm_f=168 + b, elb_f=-12, arm_b=-168 - b, elb_b=12, leg_f=10, leg_b=-10, knee_f=0, knee_b=0)


def mix_pose(a, b, u):
    return {k: lerp(a.get(k, 0), b.get(k, 0), u) for k in set(a) | set(b)}


# ------------------------------------------------------------------ world
GROUND = 1310
PATH = [(520, GROUND), (560, GROUND), (770, 1150), (610, 990), (800, 830), (680, 700), (790, 585)]
PEAK = (800, 520)


def seg_lengths():
    return [math.dist(PATH[i], PATH[i + 1]) for i in range(len(PATH) - 1)]


SEGL = seg_lengths(); TOT = sum(SEGL)


def along(d):
    d = clamp(d, 0, TOT)
    for i, l in enumerate(SEGL):
        if d <= l or i == len(SEGL) - 1:
            u = d / l; a, b = PATH[i], PATH[i + 1]
            return (lerp(a[0], b[0], u), lerp(a[1], b[1], u), 1 if b[0] >= a[0] else -1, b[1] < a[1])
        d -= l


# Macher timeline (distance along path as a function of time)
T_LEAVE, T_CLIMB, T_SLIP, T_UP, T_TOP = 2.2, 3.6, 7.0, 8.2, 12.4
SLIP_D0 = SEGL[0] + SEGL[1] + SEGL[2] * 0.55
SLIP_D1 = SEGL[0] + SEGL[1] + SEGL[2] * 0.12
START_X = 425


def macher(t):
    """returns dict(x, y, pose, facing, rot, mode)"""
    if t < T_LEAVE:  # looking at the map next to planer
        p = mix_pose(stand(), dict(lean=28, head=-10, arm_f=40, elb_f=30, arm_b=30, elb_b=20, leg_f=2, leg_b=-4), 1)
        p["head"] = -10 + 10 * ease((t - 1.4) / 0.6)  # lifts head, looks at mountain
        return dict(x=START_X, y=GROUND, pose=p, facing=1, rot=0)
    if t < T_CLIMB:
        u = (t - T_LEAVE) / (T_CLIMB - T_LEAVE)
        x = lerp(START_X, PATH[0][0], u)
        return dict(x=x, y=GROUND, pose=walk(t * 9), facing=1, rot=0, walking=True, ph=t * 9)
    speed = (SLIP_D0) / (T_SLIP - T_CLIMB)
    if t < T_SLIP:
        d = (t - T_CLIMB) * speed
        x, y, f, up = along(d)
        return dict(x=x, y=y, pose=walk(t * 8, lean=22 if up else 6, stride=28), facing=f, rot=0, walking=True, ph=t * 8)
    if t < T_UP:  # slip: slide back down, fall, get up
        k = (t - T_SLIP)
        if k < 0.5:
            u = ease(k / 0.5); d = lerp(SLIP_D0, SLIP_D1, u)
            x, y, f, _ = along(d)
            p = dict(lean=-30 * u, head=20, arm_f=110 * u, arm_b=-120 * u, elb_f=10, elb_b=10, leg_f=40 * u, leg_b=20 * u, knee_f=10, knee_b=10)
            return dict(x=x, y=y, pose=p, facing=f, rot=-70 * u * f, slip=True)
        x, y, f, _ = along(SLIP_D1)
        u = ease((k - 0.6) / 0.6)
        lying = dict(lean=-30, head=20, arm_f=110, arm_b=-120, elb_f=10, elb_b=10, leg_f=40, leg_b=20, knee_f=10, knee_b=10)
        p = mix_pose(lying, dict(lean=30, head=-20, arm_f=20, arm_b=-10, elb_f=20, elb_b=20, leg_f=30, leg_b=-10, knee_f=60, knee_b=10), u)
        return dict(x=x, y=y, pose=p, facing=f, rot=-70 * (1 - u) * f)
    if t < T_TOP:
        d = lerp(SLIP_D1, TOT, (t - T_UP) / (T_TOP - T_UP))
        x, y, f, up = along(d)
        return dict(x=x, y=y, pose=walk(t * 8.5, lean=24, stride=28), facing=f, rot=0, walking=True, ph=t * 8.5)
    x, y, f, _ = along(TOT)
    u = ease((t - T_TOP) / 0.6)
    p = mix_pose(stand(), cheer(t), u)
    return dict(x=x, y=y, pose=p, facing=-1, rot=0)


def sky_u(t):  # 0 night -> 1 sunrise
    return ease((t - 6.0) / 7.5)


def draw_world(c, t):
    u = sky_u(t)
    top = lerpc((8, 14, 34), (34, 22, 52), u)
    mid = lerpc((26, 42, 82), (150, 70, 80), u)
    hor = lerpc((52, 78, 128), (250, 150, 90), u)
    sh = skia.GradientShader.MakeLinear([(0, 0), (0, GROUND)], [C(top), C(mid), C(hor)], [0, 0.6, 1])
    c.drawRect(skia.Rect.MakeLTRB(-200, -400, W + 200, H), skia.Paint(Shader=sh))
    # stars fade
    rng = np.random.default_rng(4)
    for i in range(110):
        x, y = rng.uniform(-100, W + 100), rng.uniform(-300, GROUND - 200); ph = rng.uniform(0, 6.3)
        a = (0.3 + 0.4 * (0.5 + 0.5 * math.sin(t * 2 + ph))) * (1 - u) * clamp((GROUND - 300 - y) / 300)
        if a > 0.02: c.drawCircle(x, y, 1.5 + (ph > 5.6), P((230, 235, 255), a))
    # moon sinks & fades
    mx, my = 230, lerp(330, 520, u)
    ma = 1 - ease((t - 9) / 3)
    if ma > 0:
        c.drawCircle(mx, my, 150, P((240, 230, 190), 0.18 * ma, blur=70))
        c.drawCircle(mx, my, 52, P((250, 244, 215), ma))
        c.drawCircle(mx - 14, my - 10, 11, P((225, 218, 190), 0.5 * ma))
        c.drawCircle(mx + 18, my + 14, 7, P((225, 218, 190), 0.5 * ma))
    # sun rising behind the peak
    sa = ease((t - 10.5) / 2.5)
    if sa > 0:
        sx, sy = PEAK[0] + 30, lerp(760, 470, ease((t - 10.5) / 3.2))
        c.drawCircle(sx, sy, 520, P((255, 170, 90), 0.30 * sa, blur=160))
        c.drawCircle(sx, sy, 200, P((255, 200, 120), 0.45 * sa, blur=60))
        c.drawCircle(sx, sy, 78, P((255, 236, 190), sa))
    # distant hills
    far = lerpc((22, 34, 66), (110, 60, 78), u)
    hp = skia.Path(); hp.moveTo(-20, GROUND - 120)
    for i in range(0, 1101, 60):
        hp.lineTo(i, GROUND - 130 - 40 * math.sin(i * 0.008 + 1) - 25 * math.sin(i * 0.021))
    hp.lineTo(W + 20, GROUND); hp.lineTo(-20, GROUND); hp.close()
    c.drawPath(hp, P(far, 0.9))
    # mountain
    rock = lerpc((40, 50, 78), (92, 56, 70), u)
    rock2 = lerpc((30, 38, 62), (70, 40, 58), u)
    mt = poly([(480, GROUND + 5), (585, 1150), (560, 1060), (640, 930), (620, 860), (720, 720), (700, 660), PEAK,
               (900, 700), (980, 860), (1010, 980), (1100, 1120), (1100, GROUND + 5)])
    c.drawPath(mt, P(rock)); c.drawPath(mt, P(INK, stroke=6))
    shade = poly([PEAK, (900, 700), (980, 860), (1010, 980), (1100, 1120), (1100, GROUND + 5), (860, GROUND + 5), (880, 1000), (840, 760)])
    c.drawPath(shade, P(rock2, 0.85))
    # rim light from sun on the peak edge
    if sa > 0:
        c.drawPath(poly([(700, 660), PEAK, (900, 700)], close=False), P((255, 190, 120), 0.8 * sa, stroke=6))
    # ledges (the path)
    for i in range(1, len(PATH) - 1):
        a, b = PATH[i], PATH[i + 1]
        c.drawPath(poly([a, b], close=False), P(lerpc((70, 84, 118), (180, 110, 100), u), stroke=10))
        c.drawPath(poly([(a[0], a[1] + 9), (b[0], b[1] + 9)], close=False), P(INK, 0.7, stroke=3))
    c.drawPath(poly([PATH[0], PATH[1]], close=False), P(INK, 0.0, stroke=1))
    # summit flag appears when macher arrives
    fa = ease((t - T_TOP - 0.3) / 0.4)
    if fa > 0:
        c.drawPath(poly([(PEAK[0] + 8, PEAK[1] + 60), (PEAK[0] + 8, PEAK[1] - 50 * fa)], close=False), P(INK, stroke=5))
        wv = math.sin(t * 8) * 6
        c.drawPath(poly([(PEAK[0] + 8, PEAK[1] - 50 * fa), (PEAK[0] + 55, PEAK[1] - 40 * fa + wv), (PEAK[0] + 8, PEAK[1] - 26 * fa)]), P((255, 200, 70), fa))
    # foreground ground
    g1 = lerpc((30, 44, 70), (120, 70, 66), u); g2 = lerpc((12, 16, 28), (40, 22, 30), u)
    gs = skia.GradientShader.MakeLinear([(0, GROUND), (0, H)], [C(g1), C(g2)])
    c.drawRect(skia.Rect.MakeLTRB(-200, GROUND, W + 200, H + 200), skia.Paint(Shader=gs))
    c.drawPath(poly([(-200, GROUND), (W + 200, GROUND)], close=False), P(lerpc((80, 110, 160), (255, 190, 140), u), 0.7, stroke=3))
    # mountain shadow over planer side grows at dawn (planer stays in the shade)
    return u


def draw_table(c, t, u):
    tx, ty = 200, GROUND
    wood = lerpc((120, 84, 58), (170, 110, 70), u)
    # legs
    for x in (tx + 12, tx + 150):
        c.drawPath(poly([(x, ty - 78), (x - 6, ty)], close=False), P(INK, stroke=13)); c.drawPath(poly([(x, ty - 78), (x - 6, ty)], close=False), P(wood, stroke=7))
    top = poly([(tx - 8, ty - 92), (tx + 172, ty - 92), (tx + 172, ty - 78), (tx - 8, ty - 78)])
    c.drawPath(top, P(wood)); c.drawPath(top, P(INK, stroke=5))
    # map on table
    mp = poly([(tx + 60, ty - 96), (tx + 150, ty - 96), (tx + 146, ty - 92), (tx + 64, ty - 92)])
    c.drawPath(mp, P((236, 226, 196))); c.drawPath(mp, P(INK, stroke=2))
    # growing paper pile next to the table
    n = int(clamp(t / 15) * 22)
    for i in range(n):
        y = ty - 8 - i * 7
        x = tx - 70 + (i * 37 % 11) - 5
        c.drawRect(skia.Rect.MakeXYWH(x, y, 56, 6), P((238, 236, 228)))
        c.drawRect(skia.Rect.MakeXYWH(x, y, 56, 6), P(INK, stroke=2))
    # small lamp glow on table (planer still in night mode)
    c.drawCircle(tx + 120, ty - 110, 70, P((255, 210, 140), 0.18 * (1 - 0.6 * u), blur=30))


def planer(t):
    p = bend(t)
    if t > 13.0:  # looks up to the summit, then slumps
        k = ease((t - 13.0) / 0.8)
        up = dict(lean=10, head=-40, arm_f=10, elb_f=30, arm_b=5, elb_b=20, leg_f=-2, leg_b=-6, knee_f=0, knee_b=0)
        p = mix_pose(p, up, k)
        if t > 15.0:
            k2 = ease((t - 15.0) / 0.8)
            p = mix_pose(p, dict(lean=35, head=25, arm_f=8, elb_f=10, arm_b=4, elb_b=10, leg_f=-2, leg_b=-6), k2)
    return p


def label(c, s, x, y, col, a=1.0):
    text(c, s, x, y, F_SANS, 24, col, a, spacing=4)


def frame(c, t):
    c.clear(skia.ColorBLACK)
    c.save(); c.translate(540, GROUND); c.scale(1.18, 1.18); c.translate(-540, -GROUND)
    u = draw_world(c, t)
    draw_table(c, t, u)
    body = lerpc((240, 242, 246), (255, 236, 220), u)
    # planer
    hp = draw_figure(c, 335, GROUND, planer(t), s=0.80, facing=-1, body=lerpc((236, 238, 244), (215, 205, 210), u))
    label(c, "PLANER", 310, hp[1] - 52, (205, 212, 228), 0.85)
    # macher
    m = macher(t)
    hm = draw_figure(c, m["x"], m["y"], m["pose"], s=0.80 if m["y"] >= GROUND - 1 else 0.72, facing=m["facing"], rot=m["rot"], body=body)
    label(c, "MACHER", hm[0], hm[1] - 48, (255, 196, 90), 0.95)
    # dust when slipping
    if T_SLIP < t < T_SLIP + 0.9:
        k = (t - T_SLIP) / 0.9
        rng = np.random.default_rng(3)
        for i in range(10):
            ang = rng.uniform(3.4, 6.0); r = 20 + 70 * k * rng.uniform(0.5, 1)
            c.drawCircle(m["x"] + math.cos(ang) * r, m["y"] + math.sin(ang) * r * 0.4, 9 * (1 - k) + 2, P((200, 200, 210), 0.6 * (1 - k)))
    c.restore()
    # ending text
    if t > 15.3:
        a = ease((t - 15.3) / 0.5)
        c.drawRect(skia.Rect.MakeWH(W, H), P((0, 0, 0), 0.35 * a))
        text(c, "Planen fühlt sich an", 540, 1290, F_CAP, 56, (255, 255, 255), a, stroke=12)
        text(c, "wie Fortschritt.", 540, 1358, F_CAP, 56, (255, 255, 255), a, stroke=12)
        b = ease((t - 16.1) / 0.4)
        text(c, "Ist es aber nicht.", 540, 1442, F_CAP, 60, (255, 200, 90), b, stroke=12)
    # vignette + fades
    vg = skia.GradientShader.MakeRadial((540, 900), 1250, [C((0, 0, 0), 0), C((0, 0, 0), 0.5)])
    c.drawRect(skia.Rect.MakeWH(W, H), skia.Paint(Shader=vg))
    if t < 0.6: c.drawRect(skia.Rect.MakeWH(W, H), P((0, 0, 0), 1 - t / 0.6))
    if t > T_END - 0.5: c.drawRect(skia.Rect.MakeWH(W, H), P((0, 0, 0), (t - (T_END - 0.5)) / 0.5))


def events():
    """footsteps / slip / summit for sound design"""
    ev = []; last = None
    for f in range(int(T_END * FPS)):
        t = f / FPS; m = macher(t)
        if m.get("walking"):
            k = math.floor(m["ph"] / math.pi)
            if last is not None and k != last: ev.append(("step", t, m["y"] < GROUND - 5))
            last = k
        else: last = None
    ev += [("slip", T_SLIP), ("thud", T_SLIP + 0.5), ("summit", T_TOP), ("sunrise", 10.5), ("text", 15.3), ("text2", 16.1)]
    return ev


def render(out):
    surf = skia.Surface(W, H); c = surf.getCanvas()
    tmp = out[:-4] + ".part.mp4"
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS),
                           "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    for f in range(int(T_END * FPS)):
        frame(c, f / FPS)
        ff.stdin.write(surf.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType).tobytes())
    ff.stdin.close()
    if ff.wait() == 0: os.replace(tmp, out)


if __name__ == "__main__":
    if sys.argv[1] == "still":
        for ts in sys.argv[2:]:
            surf = skia.Surface(W, H); frame(surf.getCanvas(), float(ts))
            surf.makeImageSnapshot().save(f"{D}/st_{ts}.jpg", skia.kJPEG)
    elif sys.argv[1] == "events":
        json.dump(events(), open(f"{D}/events.json", "w"))
    else:
        render(sys.argv[2])
