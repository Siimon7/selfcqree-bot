import math, random, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, S, FPS = 720, 1280, 2, 30
GY = 820  # ground line (logical)
INK = (22, 18, 17, 255); RED = (200, 32, 38, 255); CREAM = (244, 236, 220, 255)
GRAY = (70, 66, 64, 255); WHITE = (255, 255, 255, 255)
FB = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
random.seed(7)

def P(v): return int(round(v * S))
_fc = {}
def font(sz):
    if sz not in _fc: _fc[sz] = ImageFont.truetype(FB, sz)
    return _fc[sz]

def ease(x): x = max(0, min(1, x)); return x * x * (3 - 2 * x)

# ---------- backgrounds (rendered once at 2x) ----------
def vgrad(top, bot, w=W * S, h=H * S):
    a = np.linspace(0, 1, h)[:, None, None]
    arr = (np.array(top)[None, None, :3] * (1 - a) + np.array(bot)[None, None, :3] * a)
    arr = np.repeat(arr, w, axis=1).astype(np.uint8)
    return Image.fromarray(arr, "RGB").convert("RGBA")

def glow_sprite(r, col, strength=1.0):
    y, x = np.mgrid[-r:r, -r:r]
    d = np.sqrt(x * x + y * y) / r
    a = np.clip(1 - d, 0, 1) ** 2 * 255 * strength
    arr = np.zeros((2 * r, 2 * r, 4), np.uint8)
    arr[..., 0], arr[..., 1], arr[..., 2] = col[0], col[1], col[2]
    arr[..., 3] = a.astype(np.uint8)
    return Image.fromarray(arr, "RGBA")

def add_glow(img, x, y, r, col, s=1.0):
    g = glow_sprite(P(r), col, s)
    img.alpha_composite(g, (P(x) - P(r), P(y) - P(r)))

def ground(img, base):
    d = ImageDraw.Draw(img)
    # below ground band
    band = vgrad(base, (150, 128, 100), W * S, (H - GY) * S)
    img.alpha_composite(band, (0, P(GY)))
    pts = [(P(x), P(GY + 2.5 * math.sin(x / 37) + 1.5 * math.sin(x / 11))) for x in range(0, W + 10, 8)]
    d.line(pts, fill=INK, width=P(5))
    d.line([(P(30), P(GY + 9)), (P(250), P(GY + 8))], fill=INK, width=P(2))
    d.line([(P(420), P(GY + 10)), (P(700), P(GY + 9))], fill=INK, width=P(2))

def pine(d, x, h, w, col):
    d.polygon([(P(x - w / 2), P(GY)), (P(x + w / 2), P(GY)), (P(x), P(GY - h))], fill=col)

def bg_village():
    img = vgrad((176, 168, 156), (222, 204, 172))
    add_glow(img, 600, 160, 120, (250, 240, 220), 0.6)
    d = ImageDraw.Draw(img)
    # far houses
    for x, w, h in [(-10, 110, 150), (95, 80, 120), (560, 90, 140), (650, 100, 170)]:
        c = (92, 84, 78, 255)
        d.rectangle([P(x), P(GY - h), P(x + w), P(GY)], fill=c)
        d.polygon([(P(x - 10), P(GY - h)), (P(x + w + 10), P(GY - h)), (P(x + w / 2), P(GY - h - 55))], fill=c)
        d.rectangle([P(x + w * 0.4), P(GY - h * 0.55), P(x + w * 0.6), P(GY - h * 0.35)], fill=(200, 120, 60, 255))
    ground(img, (205, 186, 152))
    return img

def bg_dusk():
    img = vgrad((112, 108, 104), (206, 190, 160))
    d = ImageDraw.Draw(img)
    d.ellipse([P(470), P(-60), P(690), P(160)], fill=(198, 190, 178, 255))
    pine(d, 40, 520, 150, (40, 36, 34, 255)); pine(d, 690, 600, 170, (52, 48, 45, 255))
    pine(d, 600, 300, 90, (78, 72, 68, 255))
    ground(img, (196, 178, 146))
    return img

def wall_layer(img, top, crenel=True, col=(54, 50, 48, 255)):
    d = ImageDraw.Draw(img)
    d.rectangle([0, P(top), P(W), P(GY)], fill=col)
    if crenel:
        for x in range(0, W, 60):
            d.rectangle([P(x), P(top - 34), P(x + 34), P(top)], fill=col)
    # stone lines
    lc = tuple(max(0, c - 14) for c in col[:3]) + (255,)
    for y in range(int(top) + 40, GY, 46):
        d.line([(0, P(y)), (P(W), P(y))], fill=lc, width=P(2))
        off = 0 if (y // 46) % 2 else 40
        for x in range(off, W, 80):
            d.line([(P(x), P(y)), (P(x), P(y + 46))], fill=lc, width=P(2))

def bg_wall():
    img = vgrad((92, 90, 92), (180, 166, 146))
    wall_layer(img, 300)
    d = ImageDraw.Draw(img)
    # gate arch
    d.rectangle([P(285), P(560), P(435), P(GY)], fill=(18, 15, 14, 255))
    d.ellipse([P(285), P(485), P(435), P(635)], fill=(18, 15, 14, 255))
    for x in (225, 495):  # torches
        d.rectangle([P(x - 5), P(520), P(x + 5), P(600)], fill=INK)
        d.polygon([(P(x - 14), P(522)), (P(x + 14), P(522)), (P(x), P(480))], fill=RED)
        add_glow(img, x, 505, 90, (230, 70, 40), 0.55)
    ground(img, (150, 138, 120))
    return img

def bg_wallclose():
    img = vgrad((70, 66, 66), (120, 112, 104))
    wall_layer(img, -60, crenel=False, col=(66, 61, 58, 255))
    d = ImageDraw.Draw(img)
    rng = random.Random(3)
    names = ["MIRA", "OSK", "LENA", "BRAM", "IVO", "TEO"]
    for i, n in enumerate(names):
        x = 380 + (i % 2) * 150 + rng.randint(-20, 20); y = 180 + i * 80
        f = font(P(34))
        col = (34, 30, 29, 255)
        d.text((P(x), P(y)), n, font=f, fill=col)
        for k in range(rng.randint(3, 6)):
            d.line([(P(x - 40 + k * 7), P(y + 8)), (P(x - 40 + k * 7), P(y + 40))], fill=col, width=P(2))
    d.line([(P(530), P(640 + 0)), (P(640), P(636))], fill=RED, width=P(4))  # under TEO (approx)
    ground(img, (112, 104, 96))
    return img

def bg_fog():
    img = vgrad((48, 46, 48), (120, 112, 104))
    d = ImageDraw.Draw(img)
    wall_layer(img, 420, col=(38, 36, 36, 255))
    pine(d, 70, 380, 120, (26, 24, 24, 255)); pine(d, 160, 250, 80, (30, 28, 28, 255))
    ground(img, (98, 92, 86))
    return img

def bg_void():
    img = vgrad((20, 19, 20), (70, 66, 64))
    ground(img, (60, 56, 54))
    return img

BGS = {}

def fog_bands(img, t, alpha=110, y0=560):
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for i in range(5):
        y = y0 + i * 55
        x = ((t * (14 + i * 6) + i * 170) % 900) - 300
        d.ellipse([P(x), P(y), P(x + 700), P(y + 110)], fill=(200, 196, 190, alpha // (i + 1) + 20))
    ov = ov.filter(ImageFilter.GaussianBlur(P(18)))
    img.alpha_composite(ov)

# ---------- characters ----------
def capsule(d, a, b, w, col):
    d.line([(P(a[0]), P(a[1])), (P(b[0]), P(b[1]))], fill=col, width=P(w))
    for p in (a, b):
        d.ellipse([P(p[0] - w / 2), P(p[1] - w / 2), P(p[0] + w / 2), P(p[1] + w / 2)], fill=col)

def stick(img, x, h, col=INK, walk=0.0, ph=0.0, face=1, pose="idle", kneel=0.0, eye=WHITE,
          lantern=False, helmet=False, spear=False, gy=GY, jitter=0.0):
    d = ImageDraw.Draw(img)
    x += jitter * math.sin(ph * 37)
    r = h * 0.1; lw = h * 0.075
    hip_y = gy - h * 0.46 + kneel * h * 0.2
    neck_y = gy - h + 2 * r + kneel * h * 0.2
    hx = x + face * kneel * h * 0.06
    head = (hx + face * kneel * h * 0.05, neck_y - r * 1.05 + kneel * h * 0.04)
    L = h * 0.46
    a = walk * 0.5 * math.sin(ph)
    if kneel > 0:
        k = kneel
        knee1 = (x + face * h * 0.18 * k, gy - h * 0.2 * (1 - k * 0.3))
        capsule(d, (x, hip_y), knee1, lw, col); capsule(d, knee1, (knee1[0], gy), lw, col)
        knee2 = (x - face * h * 0.05, gy - 4)
        capsule(d, (x, hip_y), knee2, lw, col); capsule(d, knee2, (x - face * h * 0.22 * k, gy), lw, col)
    else:
        for s in (1, -1):
            aa = a * s + s * 0.13
            capsule(d, (x, hip_y), (x + math.sin(aa) * L, hip_y + math.cos(aa) * L), lw, col)
    capsule(d, (hx, neck_y), (x, hip_y), lw * 1.15, col)
    sh = (hx, neck_y + h * 0.05)
    al = h * 0.36
    arms = []
    if pose == "reach":
        arms = [(sh[0] + face * al, sh[1] - h * 0.02), (sh[0] - face * al * 0.3, sh[1] + al * 0.9)]
    elif pose == "spear":
        arms = [(sh[0] + face * al * 0.8, sh[1] + al * 0.3), (sh[0] + face * al * 0.45, sh[1] + al * 0.55)]
    elif pose == "lantern":
        arms = [(sh[0] + face * al * 0.55, sh[1] + al * 0.6), (sh[0] - face * math.sin(-a) * al * 0.5, sh[1] + al * 0.9)]
    elif pose == "raise":
        arms = [(sh[0] + face * al * 0.6, sh[1] - al * 0.55), (sh[0] - face * al * 0.1, sh[1] + al * 0.9)]
    else:
        arms = [(sh[0] + math.sin(-a) * al * 0.6 + al * 0.22, sh[1] + al * 0.88), (sh[0] + math.sin(a) * al * 0.6 - al * 0.22, sh[1] + al * 0.88)]
    for e in arms: capsule(d, sh, e, lw * 0.85, col)
    d.ellipse([P(head[0] - r), P(head[1] - r), P(head[0] + r), P(head[1] + r)], fill=col)
    if helmet:
        d.chord([P(head[0] - r * 1.25), P(head[1] - r * 1.4), P(head[0] + r * 1.25), P(head[1] + r * 0.6)], 180, 360, fill=col)
        d.rectangle([P(head[0] - r * 0.15), P(head[1] - r * 2.1), P(head[0] + r * 0.15), P(head[1] - r * 0.9)], fill=RED)
    er = max(1.6, r * 0.2)
    ex = head[0] + face * r * 0.45
    d.ellipse([P(ex - er), P(head[1] - er), P(ex + er), P(head[1] + er)], fill=eye)
    if spear:
        hand = arms[0]
        tip = (hand[0] + face * h * 0.55, hand[1] - h * 0.32)
        tail = (hand[0] - face * h * 0.5, hand[1] + h * 0.3)
        d.line([(P(tail[0]), P(tail[1])), (P(tip[0]), P(tip[1]))], fill=col, width=P(lw * 0.35))
        dx, dy = tip[0] - tail[0], tip[1] - tail[1]; n = math.hypot(dx, dy); ux, uy = dx / n, dy / n
        d.polygon([(P(tip[0] + ux * 18), P(tip[1] + uy * 18)), (P(tip[0] - uy * 7), P(tip[1] + ux * 7)),
                   (P(tip[0] + uy * 7), P(tip[1] - ux * 7))], fill=col)
    head_top = head[1] - r
    if lantern:
        hand = arms[0]
        lx, ly = hand[0], hand[1] + h * 0.07
        return head_top, (lx, ly, h)
    return head_top, None

def draw_lantern(img, lan, power=1.0, flick=0.0):
    lx, ly, h = lan
    s = h / 210
    add_glow(img, lx, ly, 150 * s * power * (1 + 0.05 * flick), (255, 170, 70), 0.55)
    d = ImageDraw.Draw(img)
    d.line([(P(lx), P(ly - 22 * s)), (P(lx), P(ly - 12 * s))], fill=INK, width=P(2))
    d.rectangle([P(lx - 9 * s), P(ly - 12 * s), P(lx + 9 * s), P(ly + 12 * s)], fill=INK)
    d.rectangle([P(lx - 5 * s), P(ly - 7 * s), P(lx + 5 * s), P(ly + 8 * s)], fill=(255, 196, 90, 255))

def wraith(img, x, rise=1.0, reach=0.0, kneel=0.0, face=-1, h=430):
    d = ImageDraw.Draw(img)
    base = GY + (1 - rise) * h * 1.05 + kneel * h * 0.28
    top = base - h
    col = (14, 12, 12, 255)
    bw = h * 0.16
    body = [(x - bw * 0.35, top + h * 0.2), (x + bw * 0.35, top + h * 0.2), (x + bw * 0.9, base),
            (x + bw * 0.4, base - 18), (x, base + 6), (x - bw * 0.5, base - 14), (x - bw * 0.9, base)]
    d.polygon([(P(a), P(b)) for a, b in body], fill=col)
    # shoulders spikes
    for s in (-1, 1):
        d.polygon([(P(x + s * bw * 0.2), P(top + h * 0.2)), (P(x + s * bw * 1.0), P(top + h * 0.17)),
                   (P(x + s * bw * 0.4), P(top + h * 0.32))], fill=col)
    hx, hy = x + face * kneel * 20, top + h * 0.12 + kneel * 30
    d.ellipse([P(hx - h * 0.065), P(hy - h * 0.09), P(hx + h * 0.065), P(hy + h * 0.08)], fill=col)
    for s in (-0.3, 0.25):
        ex = hx + face * h * 0.025 + s * h * 0.05
        d.ellipse([P(ex - 3.2), P(hy - 4), P(ex + 3.2), P(hy + 2.4)], fill=RED)
    add_glow(img, hx + face * 6, hy - 1, 26, (230, 40, 40), 0.5)
    sh = (x + face * bw * 0.4, top + h * 0.24)
    back = (x - face * bw * 0.4, top + h * 0.24)
    # far arm hangs
    e2 = (back[0] - face * 20, top + h * 0.78)
    capsule(d, back, e2, 9, col)
    # near arm: hang -> reach
    a = reach
    end = (sh[0] + face * (25 + a * 190), sh[1] + (h * 0.55) * (1 - a) + a * 60)
    if kneel > 0: end = (sh[0] + face * 70, base - 6)
    capsule(d, sh, end, 9, col)
    for k in (-1, 0, 1):
        f = (end[0] + face * 22, end[1] + k * 10)
        capsule(d, end, f, 4, col)
    return top - 8

def tag(img, x, ytop, l1, l2, red2=True, scale=1.0, red1=False):
    if scale <= 0.02: return
    f1, f2 = font(P(15)), font(P(17))
    w = max(f1.getbbox(l1)[2], f2.getbbox(l2)[2] if l2 else 0) + P(22)
    hh = P(26) + (P(20) if l2 else 0)
    t = Image.new("RGBA", (w + P(6), hh + P(30)), (0, 0, 0, 0))
    d = ImageDraw.Draw(t)
    d.line([(t.width // 2, hh), (t.width // 2, hh + P(28))], fill=INK, width=P(2))
    d.rectangle([P(3), 0, w + P(3), hh], fill=CREAM, outline=INK, width=P(2))
    d.text((t.width // 2, P(14)), l1, font=f1, fill=RED if red1 else INK, anchor="mm")
    if l2: d.text((t.width // 2, P(35)), l2, font=f2, fill=RED if red2 else INK, anchor="mm")
    if scale != 1.0:
        t = t.resize((max(1, int(t.width * scale)), max(1, int(t.height * scale))), Image.BILINEAR)
    img.alpha_composite(t, (P(x) - t.width // 2, P(ytop) - t.height))

def pop(t, t0, d=0.18):
    if t < t0: return 0.0
    x = (t - t0) / d
    if x >= 1: return 1.0
    return 1.15 * math.sin(x * math.pi / 2) if x < 0.8 else 1.15 - 0.15 * (x - 0.8) / 0.2

GL = "!#%&?@$*<>/\\=+01"
def glitch_txt(s, rng): return "".join(rng.choice(GL) for _ in s)

# ---------- scenes ----------
def monolith(img, lit=1.0):
    d = ImageDraw.Draw(img)
    x = 430
    d.polygon([(P(x - 40), P(GY)), (P(x + 40), P(GY)), (P(x + 30), P(GY - 230)), (P(x), P(GY - 255)), (P(x - 30), P(GY - 230))], fill=INK)
    if lit > 0:
        add_glow(img, x, GY - 150, 110, (220, 40, 40), 0.6 * lit)
        d.ellipse([P(x - 12), P(GY - 162), P(x + 12), P(GY - 138)], fill=(int(60 + 140 * lit), 30, 34, 255))
        d.line([(P(x), P(GY - 200)), (P(x), P(GY - 100))], fill=(int(60 + 140 * lit), 30, 34, 255), width=P(3))

def s_crowd(img, t, T):
    xs = [60, 120, 180, 245, 560, 620, 680]; ranks = ["C", "B", "D", "C", "A", "C", "B"]
    monolith(img)
    for i, x in enumerate(xs):
        ht, _ = stick(img, x, 125 + (i % 3) * 8, col=GRAY, face=1 if x < 430 else -1, ph=t * 2 + i)
        tag(img, x, ht - 4, "RANK", ranks[i], red2=ranks[i] == "A", scale=pop(t, 0.3 + i * 0.28))

def s_three(img, t, T):
    for i, (x, c, r) in enumerate([(150, "KNIGHT", "RANK C"), (360, "MAGE", "RANK B"), (570, "ARCHER", "RANK C")]):
        ht, _ = stick(img, x, 240, col=(40, 36, 35, 255), face=1 if x < 360 else -1, ph=i)
        tag(img, x, ht - 6, c, r, red2=False, scale=pop(t, 0.35 + i * 0.6))

def side_crowd(img, t, spread=0.0):
    for i, x in enumerate([40, 95, 610, 665, 150]):
        dx = (-1 if x < 360 else 1) * spread * 60
        stick(img, x + dx, 120, col=GRAY, face=1 if x < 360 else -1, ph=i)

def s_turn(img, t, T):
    monolith(img); side_crowd(img, t)
    x = 120 + 150 * ease(t / (T * 0.7))
    walking = t < T * 0.7
    ht, lan = stick(img, x, 200, walk=1 if walking else 0, ph=t * 7, pose="lantern", lantern=True)
    draw_lantern(img, lan)
    dots = "." * (1 + int(t * 3) % 3) if t > T * 0.7 else ""
    if dots: tag(img, x, ht - 6, "RANK", dots, scale=pop(t, T * 0.7))

def s_unranked(img, t, T):
    monolith(img, lit=max(0, 1 - t * 2))
    side_crowd(img, t, spread=ease(t / 1.2))
    ht, lan = stick(img, 270, 200, pose="lantern", lantern=True)
    draw_lantern(img, lan, power=0.8)
    tag(img, 270, ht - 6, "UNRANKED", "LV —", scale=pop(t, 0.25), red1=True)

def s_alone(img, t, T):
    for i in range(3):
        stick(img, 470 + i * 70 + t * 70, 130, col=GRAY, walk=1, ph=t * 6 + i, face=1)
    ht, lan = stick(img, 300, 215, pose="lantern", lantern=True)
    draw_lantern(img, lan, power=0.7)
    tag(img, 300, ht - 6, "UNRANKED", "LV —", red1=True)

def s_guards(img, t, T):
    x = 140 + 120 * ease(t / T)
    for k, off in enumerate((90, 175)):
        stick(img, x - off, 235, walk=1, ph=t * 6 + k, pose="spear", helmet=True, spear=True, eye=RED)
    ht, lan = stick(img, x, 200, walk=1, ph=t * 6 + 1.5, pose="lantern", lantern=True)
    draw_lantern(img, lan, power=0.7)
    tag(img, x, ht - 6, "UNRANKED", "LV —", red1=True)

def s_gate(img, t, T):
    x = 300 + 60 * ease(t / T)
    ht, lan = stick(img, x, 100, walk=1, ph=t * 6, pose="lantern", lantern=True)
    draw_lantern(img, lan, power=0.6)

def s_names(img, t, T):
    ht, lan = stick(img, 240, 260, pose="raise", lantern=True, face=1)
    lan = (lan[0], lan[1] - 10, lan[2])
    draw_lantern(img, lan, power=1.3, flick=math.sin(t * 20))

def s_rise(img, t, T, show_tag=False):
    fog_bands(img, t + 3)
    ht, lan = stick(img, 210, 200, pose="lantern", lantern=True)
    draw_lantern(img, lan, power=0.9, flick=math.sin(t * 17))
    rise = ease(t / (T * 0.85)) if not show_tag else 1.0
    wt = wraith(img, 520, rise=rise)
    if show_tag:
        tag(img, 520, wt, "WRAITH", "LV 40", scale=pop(t, 0.2))
        tag(img, 210, ht - 6, "UNRANKED", "LV 0", red1=True, red2=False)
    fog_bands(img, t, alpha=60, y0=700)

def s_tag(img, t, T): s_rise(img, t, T, show_tag=True)

def s_run(img, t, T):
    fog_bands(img, t + 3)
    for i in range(4):
        stick(img, 330 - i * 40 - t * 260, 130, col=GRAY, walk=1.3, ph=t * 10 + i, face=-1)
    ht, lan = stick(img, 210, 200, pose="lantern", lantern=True)
    draw_lantern(img, lan, power=0.9, flick=math.sin(t * 17))
    wt = wraith(img, 520)
    tag(img, 520, wt, "WRAITH", "LV 40")
    fog_bands(img, t, alpha=60, y0=700)

def s_frozen(img, t, T):
    fog_bands(img, t + 3)
    ht, lan = stick(img, 210, 200, pose="lantern", lantern=True, jitter=1.6, ph=t * 9)
    draw_lantern(img, lan, power=0.9, flick=math.sin(t * 31))
    wraith(img, 520)
    fog_bands(img, t, alpha=60, y0=700)

def s_reach(img, t, T, hold=False):
    fog_bands(img, t + 3)
    ht, lan = stick(img, 210, 200, pose="lantern", lantern=True, jitter=0 if hold else 1.2, ph=t * 9)
    draw_lantern(img, lan, power=0.9)
    k = 1.0 if hold else ease(t / T)
    wraith(img, 520 - 150 * k, reach=k)
    fog_bands(img, t, alpha=60, y0=700)

def s_stop(img, t, T): s_reach(img, t, T, hold=True)

def s_glitch(img, t, T):
    fog_bands(img, t + 3)
    ht, lan = stick(img, 210, 200, pose="lantern", lantern=True)
    draw_lantern(img, lan, power=0.9 + 0.5 * ease(t / T))
    wt = wraith(img, 370, reach=1.0)
    rng = random.Random(int(t * 15))
    if t < T * 0.62:
        tag(img, 370, wt, glitch_txt("WRAITH", rng), glitch_txt("LV 40", rng))
        tag(img, 210, ht - 6, glitch_txt("UNRANKED", rng), glitch_txt("LV 0", rng), red1=True)
    else:
        tag(img, 370, wt, "WRAITH", "BOUND", scale=pop(t, T * 0.62))
        tag(img, 210, ht - 6, "???", "MASTER", scale=pop(t, T * 0.62 + 0.15))
    fog_bands(img, t, alpha=60, y0=700)

def s_kneel(img, t, T):
    fog_bands(img, t + 3)
    ht, lan = stick(img, 210, 200, pose="lantern", lantern=True)
    draw_lantern(img, lan, power=1.3)
    k = ease((t - 0.3) / 1.6)
    wt = wraith(img, 400, kneel=k, reach=1 - k)
    tag(img, 400, wt + k * 120, "WRAITH", "BOUND")
    tag(img, 210, ht - 6, "???", "MASTER")
    fog_bands(img, t, alpha=60, y0=700)

def s_close(img, t, T):
    fog_bands(img, t + 3)
    wraith(img, 560, kneel=1.0)
    ht, lan = stick(img, 300, 300, pose="lantern", lantern=True)
    draw_lantern(img, lan, power=1.4, flick=math.sin(t * 13))
    tag(img, 300, ht - 6, "???", "MASTER")
    fog_bands(img, t, alpha=50, y0=720)

def s_voice(img, t, T):
    fog_bands(img, t, alpha=90, y0=420)
    x = 560
    d = ImageDraw.Draw(img)
    h = 330
    c = (10, 9, 9, int(255 * ease(t / 2.2)))
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    od.polygon([(P(x - 30), P(GY - h + 60)), (P(x + 30), P(GY - h + 60)), (P(x + 70), P(GY)), (P(x - 70), P(GY))], fill=c)
    od.ellipse([P(x - 26), P(GY - h + 10), P(x + 26), P(GY - h + 70)], fill=c)
    img.alpha_composite(ov)
    if t > 1.4:
        od2 = ImageDraw.Draw(img)
        od2.ellipse([P(x - 11), P(GY - h + 33), P(x - 3), P(GY - h + 41)], fill=WHITE)
        add_glow(img, x - 7, GY - h + 37, 30, (255, 255, 255), 0.6)
    fog_bands(img, t + 5, alpha=80, y0=650)

def s_end(img, t, T): pass

SCENES = [
    ("village", s_crowd, "On my sixteenth birthday, the System *ranked* everyone.", (1.0, 1.05), (360, 700)),
    ("village", s_three, "Knight. Mage. Archer. Everyone got *something*.", (1.02, 1.07), (360, 650)),
    ("village", s_turn, "Then it was my turn.", (1.0, 1.06), (330, 700)),
    ("village", s_unranked, "The stone showed *nothing*.", (1.08, 1.16), (300, 680)),
    ("dusk", s_alone, "No class. No level. Just a *blank* tag.", (1.0, 1.08), (320, 650)),
    ("wall", s_guards, "In Ashford, blank tags get sent to the *Wall*.", (1.03, 1.08), (300, 650)),
    ("wall", s_gate, "Nobody comes *back* from the Wall.", (1.0, 1.12), (360, 640)),
    ("wallclose", s_names, "Not even my brother, *Teo*.", (1.0, 1.08), (480, 520)),
    ("fog", s_rise, "First night, something crawled out of the *fog*.", (1.0, 1.05), (380, 600)),
    ("fog", s_tag, "Level forty. I was level *zero*.", (1.06, 1.12), (380, 560)),
    ("fog", s_run, "The other exiles *ran*.", (1.0, 1.04), (360, 620)),
    ("fog", s_frozen, "I couldn't. My legs wouldn't *move*.", (1.05, 1.22), (230, 680)),
    ("fog", s_reach, "It reached for me...", (1.05, 1.12), (320, 640)),
    ("fog", s_stop, "...and *stopped*.", (1.2, 1.24), (300, 600)),
    ("fog", s_glitch, "Then both our tags started to *glitch*.", (1.06, 1.1), (300, 580)),
    ("fog", s_kneel, "It knelt. Like it had been *waiting* for me.", (1.04, 1.1), (320, 640)),
    ("fog", s_close, "Unranked doesn't mean nothing.", (1.0, 1.06), (380, 640)),
    ("fog", s_close, "It means the System can't *read* me.", (1.1, 1.16), (320, 600)),
    ("void", s_voice, "Deep in the fog, a voice whispered: \"*Finally*.\"", (1.0, 1.08), (500, 560)),
    ("end", s_end, "", (1, 1), (360, 640)),
]
SHAKE = {3: 0.5, 9: 0.5, 13: 0.6, 14: 0.4}
BOOM = {3, 6, 8, 9, 13, 18}

VOLEN = {}
def dur(cap):
    if not cap: return 3.2
    if cap in VOLEN: return max(2.4, VOLEN[cap] + 0.2 + 0.75)
    n = len(cap.split())
    return max(3.0, min(5.2, 2.0 + 0.36 * n))

# ---------- captions ----------
def caption(fr, cap, t):
    if not cap: return
    words = cap.split()
    f = font(40)
    toks = []
    for w in words:
        red = "*" in w
        toks.append((w.replace("*", ""), red))
    lines, cur, cw = [], [], 0
    sp = f.getlength(" ")
    for w, r in toks:
        wl = f.getlength(w)
        if cur and cw + sp + wl > 590:
            lines.append((cur, cw)); cur, cw = [], 0
        cw = cw + (sp if cur else 0) + wl; cur.append((w, r, wl))
    lines.append((cur, cw))
    d = ImageDraw.Draw(fr)
    y = 935 - (len(lines) - 1) * 26
    i = 0
    for ln, lw in lines:
        x = (W - lw) / 2
        for w, r, wl in ln:
            appear = 0.2 + i * (VOLEN.get(cap, 0.13 * len(words)) / len(words)) * 0.92
            if t >= appear:
                a = ease((t - appear) / 0.12)
                yy = y + (1 - a) * 8
                d.text((x, yy), w, font=f, fill=(RED if r else WHITE)[:3] + (int(255 * a),),
                       stroke_width=4, stroke_fill=(16, 13, 12, int(255 * a)), anchor="lm")
            x += wl + sp; i += 1
        y += 52

def end_card(t):
    fr = vgrad((222, 208, 180), (196, 176, 140), W, H)
    d = ImageDraw.Draw(fr)
    a = ease(t / 0.4)
    d.text((W / 2, 560), "UNRANKED", font=font(92), fill=(22, 18, 17, int(255 * a)), anchor="mm")
    d.line([(150, 625), (570, 620)], fill=RED[:3] + (int(255 * a),), width=7)
    b = ease((t - 0.4) / 0.3)
    d.rounded_rectangle([250, 660, 470, 718], 6, fill=RED[:3] + (int(255 * b),))
    d.text((W / 2, 690), "EPISODE 1", font=font(30), fill=(255, 255, 255, int(255 * b)), anchor="mm")
    c = ease((t - 0.8) / 0.3)
    d.text((W / 2, 765), "follow so you don't miss part 2", font=font(22), fill=(90, 80, 70, int(255 * c)), anchor="mm")
    return fr

# ---------- vignette ----------
yy, xx = np.mgrid[0:H, 0:W]
vd = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H * 0.45) / (H * 0.62)) ** 2)
VIG = np.clip((vd - 0.55) * 1.3, 0, 0.6)[..., None]

def finish(fr, glitch=0.0, redflash=0.0):
    arr = np.asarray(fr.convert("RGB")).astype(np.float32)
    arr *= (1 - VIG)
    if redflash > 0:
        arr = arr * (1 - 0.35 * redflash) + np.array([200, 20, 30]) * 0.35 * redflash
    if glitch > 0:
        rng = np.random.default_rng(int(glitch * 1e6) % 99991)
        for _ in range(6):
            y0 = rng.integers(0, H - 40); hh = rng.integers(6, 40); sh = rng.integers(-30, 30)
            arr[y0:y0 + hh] = np.roll(arr[y0:y0 + hh], sh, axis=1)
        arr[..., 0] = np.roll(arr[..., 0], 4, axis=1)
    return np.clip(arr, 0, 255).astype(np.uint8)

# ---------- audio ----------
def make_audio(total, cuts):
    sr = 44100; n = int(total * sr); t = np.arange(n) / sr
    lfo = 0.6 + 0.4 * np.sin(2 * np.pi * 0.07 * t)
    drone = (np.sin(2 * np.pi * 55 * t) * 0.5 + np.sin(2 * np.pi * 82.4 * t) * 0.3 + np.sin(2 * np.pi * 110.3 * t) * 0.15) * lfo
    rng = np.random.default_rng(1)
    wind = rng.standard_normal(n)
    k = np.ones(400) / 400
    wind = np.convolve(wind, k, mode="same") * 3.0 * (0.5 + 0.5 * np.sin(2 * np.pi * 0.05 * t + 1))
    out = drone * 0.18 + wind * 0.10
    def add(sig, at):
        i = int(at * sr); j = min(n, i + len(sig)); out[i:j] += sig[: j - i]
    for idx, (st, sc) in enumerate(cuts):
        if idx in BOOM:
            tt = np.arange(int(1.6 * sr)) / sr
            f = 70 * np.exp(-tt * 1.5) + 32
            add(np.sin(2 * np.pi * np.cumsum(f) / sr) * np.exp(-tt * 2.2) * 0.8, st)
        else:
            tt = np.arange(int(0.08 * sr)) / sr
            add(rng.standard_normal(len(tt)) * np.exp(-tt * 60) * 0.12, st)
    # heartbeat in frozen/reach scenes
    for idx in (11, 12):
        st, sc = cuts[idx]
        for b in np.arange(st, st + dur(SCENES[idx][2]), 0.75):
            for o in (0, 0.18):
                tt = np.arange(int(0.25 * sr)) / sr
                add(np.sin(2 * np.pi * 48 * tt) * np.exp(-tt * 18) * 0.7, b + o)
    # riser into glitch
    st = cuts[14][0]; L = dur(SCENES[14][2]) * 0.62
    tt = np.arange(int(L * sr)) / sr
    ns = rng.standard_normal(len(tt)); ns = ns - np.convolve(ns, np.ones(20) / 20, mode="same")
    add(ns * (tt / L) ** 2 * 0.25 + np.sin(2 * np.pi * (200 + 600 * (tt / L) ** 2) * tt) * (tt / L) ** 2 * 0.08, st)
    # silence dip before "stopped"
    i0, i1 = int(cuts[13][0] * sr), int((cuts[13][0] + 0.9) * sr)
    out[i0:i1] *= 0.25
    # voice-over, music ducked under voice
    vo = np.zeros(n)
    for idx, (st, sc) in enumerate(cuts):
        p = f"vo/{idx:02d}.wav"
        try:
            with wave.open(p) as w:
                v = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
        except FileNotFoundError:
            continue
        i = int((st + 0.2) * sr); j = min(n, i + len(v)); vo[i:j] += v[: j - i]
    env = np.convolve(np.abs(vo), np.ones(4410) / 4410, mode="same")
    duck = 1 - 0.55 * np.clip(env * 12, 0, 1)
    out = out / max(1e-6, np.abs(out).max()) * 0.5 * duck + vo / max(1e-6, np.abs(vo).max()) * 0.9
    # fade out
    fo = int(1.5 * sr); out[-fo:] *= np.linspace(1, 0, fo)
    out = out / max(1e-6, np.abs(out).max()) * 0.85
    st2 = np.stack([out, np.roll(out, 300)], 1)
    with wave.open("audio.wav", "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((st2 * 32767).astype(np.int16).tobytes())

def main():
    import os
    for i, sc in enumerate(SCENES):
        p = f"vo/{i:02d}.wav"
        if sc[2] and os.path.exists(p):
            with wave.open(p) as w: VOLEN[sc[2]] = w.getnframes() / w.getframerate()
    BGS.update(village=bg_village(), dusk=bg_dusk(), wall=bg_wall(), wallclose=bg_wallclose(), fog=bg_fog(), void=bg_void())
    cuts, total = [], 0.0
    for sc in SCENES:
        cuts.append((total, sc)); total += dur(sc[2])
    make_audio(total, cuts)
    only = int(sys.argv[1]) if len(sys.argv) > 1 else None
    if only is not None:
        st, sc = cuts[only]; T = dur(sc[2]); tt = T * 0.8
        frame(sc, tt, T, only).save(f"preview_{only}.png"); return
    ff = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                           "-i", "-", "-i", "audio.wav", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
                           "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", "unranked_ep1.mp4"], stdin=subprocess.PIPE)
    for idx, (st, sc) in enumerate(cuts):
        T = dur(sc[2])
        for k in range(int(round(T * FPS))):
            fr = frame(sc, k / FPS, T, idx)
            ff.stdin.write(fr.tobytes() if isinstance(fr, np.ndarray) else np.asarray(fr.convert("RGB")).tobytes())
        print("scene", idx, flush=True)
    ff.stdin.close(); ff.wait()

def frame(sc, t, T, idx):
    bgname, fn, cap, (z0, z1), (fx, fy) = sc
    if bgname == "end":
        return Image.fromarray(finish(end_card(t)))
    img = BGS[bgname].copy()
    fn(img, t, T)
    z = z0 + (z1 - z0) * (t / T)
    cw, ch = W * S / z, H * S / z
    sx = sy = 0.0
    if idx in SHAKE and t < SHAKE[idx]:
        a = (1 - t / SHAKE[idx]) * 14
        sx, sy = a * math.sin(t * 90), a * math.cos(t * 70)
    cx = min(max(P(fx) + sx * S, cw / 2), W * S - cw / 2)
    cy = min(max(P(fy) + sy * S, ch / 2), H * S - ch / 2)
    fr = img.crop((int(cx - cw / 2), int(cy - ch / 2), int(cx + cw / 2), int(cy + ch / 2))).resize((W, H), Image.BILINEAR)
    caption(fr, cap, t)
    gl = 0.0
    if idx == 14 and T * 0.3 < t < T * 0.62 and int(t * 12) % 2 == 0: gl = t + 0.123
    rf = max(0, 1 - t / 0.5) if idx in (13,) else 0.0
    return Image.fromarray(finish(fr, gl, rf))

if __name__ == "__main__":
    main()
