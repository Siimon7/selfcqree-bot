"""Cartoon renderer (coloured characters with faces, game FX). Usage: python3 toon.py EP [preview idx,idx]"""
import math, random, sys, os, importlib, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import engine as E
from render import W, H, FPS, ease, font

S = 2
OUT = (28, 22, 30)            # outline colour
SKIN = (255, 218, 178)
GY = 960                      # ground line
CS = 1.3                      # character scale
YEL = (255, 214, 64)


def P(v): return int(round(v * S))


def oval(d, x, y, rx, ry, fill, ow=4):
    d.ellipse([P(x - rx - ow / 2), P(y - ry - ow / 2), P(x + rx + ow / 2), P(y + ry + ow / 2)], fill=OUT)
    d.ellipse([P(x - rx + ow / 2), P(y - ry + ow / 2), P(x + rx - ow / 2), P(y + ry - ow / 2)], fill=fill)


def limb(d, a, b, w, col):
    d.line([(P(a[0]), P(a[1])), (P(b[0]), P(b[1]))], fill=OUT, width=P(w + 5))
    for p in (a, b):
        d.ellipse([P(p[0] - (w + 5) / 2), P(p[1] - (w + 5) / 2), P(p[0] + (w + 5) / 2), P(p[1] + (w + 5) / 2)], fill=OUT)
    d.line([(P(a[0]), P(a[1])), (P(b[0]), P(b[1]))], fill=col, width=P(w))
    for p in (a, b):
        d.ellipse([P(p[0] - w / 2), P(p[1] - w / 2), P(p[0] + w / 2), P(p[1] + w / 2)], fill=col)


def poly(d, pts, fill, ow=4):
    d.polygon([(P(a), P(b)) for a, b in pts], fill=fill, outline=OUT)
    d.line([(P(a), P(b)) for a, b in pts + [pts[0]]], fill=OUT, width=P(ow), joint="curve")


# ---------------- backgrounds ----------------
def vgrad(top, bot):
    a = np.linspace(0, 1, H * S)[:, None, None]
    arr = (np.array(top)[None, None] * (1 - a) + np.array(bot)[None, None] * a)
    return Image.fromarray(np.repeat(arr, W * S, axis=1).astype(np.uint8), "RGB").convert("RGBA")


def peaks(d, base, col, n, hmin, hmax, seed):
    r = random.Random(seed); x = -60
    pts = [(P(-60), P(base))]
    while x < W + 80:
        w = r.randint(90, 170); h = r.randint(hmin, hmax)
        pts += [(P(x + w * 0.5), P(base - h)), (P(x + w), P(base))]
        x += w
    pts += [(P(W + 80), P(H)), (P(-60), P(H))]
    d.polygon(pts, fill=col)


def ground(d, top, bot_col):
    d.rectangle([0, P(GY), P(W), P(H)], fill=top)
    d.line([(0, P(GY)), (P(W), P(GY))], fill=OUT, width=P(4))
    d.rectangle([0, P(GY + 160), P(W), P(H)], fill=bot_col)


SKY = (178, 214, 236)
def flatbg(c): return Image.new("RGBA", (W * S, H * S), c + (255,))


def houses(d, base, wall=(226, 208, 172), roof=(176, 92, 72), win=(92, 104, 124), seed=1):
    rnd = random.Random(seed); x = -30
    while x < W + 30:
        w = rnd.choice([90, 100, 110]); hgt = rnd.choice([250, 280, 310])
        poly(d, [(x, base), (x + w, base), (x + w, base - hgt), (x, base - hgt)], wall, ow=3)
        poly(d, [(x - 6, base - hgt), (x + w + 6, base - hgt), (x + w / 2, base - hgt - 55)], roof, ow=3)
        for r in range(3):
            for c in range(2):
                wx = x + 18 + c * (w - 50); wy = base - hgt + 30 + r * 75
                if wy + 40 < base - 20:
                    d.rectangle([P(wx), P(wy), P(wx + 16), P(wy + 34)], fill=win)
        x += w


def flatground(d, col, line):
    d.rectangle([0, P(GY), P(W), P(H)], fill=col)
    d.line([(0, P(GY)), (P(W), P(GY))], fill=line, width=P(3))


def bg_village():
    img = flatbg(SKY); d = ImageDraw.Draw(img)
    houses(d, GY, seed=1)
    flatground(d, (208, 194, 162), (150, 135, 110))
    return img


def bg_night():
    img = vgrad((10, 14, 30), (24, 32, 58)); d = ImageDraw.Draw(img)
    rnd = random.Random(5)
    for _ in range(90):
        sx, sy = rnd.randint(0, W), rnd.randint(0, 800)
        r = rnd.choice([1, 1, 1.5, 2]); d.ellipse([P(sx - r), P(sy - r), P(sx + r), P(sy + r)], fill=(200, 210, 230))
    for r, a in [(150, 18), (110, 30)]:
        ov = Image.new("RGBA", img.size, (0, 0, 0, 0)); ImageDraw.Draw(ov).ellipse([P(560 - r), P(230 - r), P(560 + r), P(230 + r)], fill=(230, 230, 210, a)); img.alpha_composite(ov)
    d = ImageDraw.Draw(img)
    d.ellipse([P(500), P(170), P(620), P(290)], fill=(236, 234, 214))
    houses(d, GY, wall=(30, 36, 60), roof=(22, 26, 46), win=(230, 190, 90), seed=2)
    flatground(d, (26, 32, 52), (50, 60, 90))
    return img


def bg_cave():
    img = vgrad((40, 38, 56), (62, 58, 80)); d = ImageDraw.Draw(img)
    for x in range(-60, W, 160):
        poly(d, [(x, GY), (x + 150, GY), (x + 150, 420), (x + 75, 340), (x, 420)], (52, 50, 70), ow=3)
    for x in range(30, W, 130):
        d.polygon([(P(x), 0), (P(x + 34), 0), (P(x + 17), P(90 + (x % 3) * 30))], fill=(52, 50, 70), outline=OUT)
    flatground(d, (58, 54, 74), (90, 85, 110))
    return img


def bg_sewer():
    img = flatbg((38, 52, 50)); d = ImageDraw.Draw(img)
    for x in range(-40, W, 180):
        d.chord([P(x), P(330), P(x + 170), P(560)], 180, 360, fill=(48, 64, 60), outline=OUT, width=P(3))
        d.rectangle([P(x), P(445), P(x + 170), P(GY)], fill=(48, 64, 60))
        d.line([(P(x), P(445)), (P(x), P(GY))], fill=OUT, width=P(3))
    d.ellipse([P(250), P(470), P(470), P(GY + 30)], fill=(14, 20, 20), outline=OUT, width=P(4))
    d.rectangle([0, P(GY), P(W), P(H)], fill=(44, 60, 52))
    d.rectangle([0, P(GY + 30), P(W), P(GY + 70)], fill=(70, 110, 80))
    d.line([(0, P(GY)), (P(W), P(GY))], fill=(90, 120, 100), width=P(3))
    return img


def bg_home():
    img = flatbg((150, 118, 90)); d = ImageDraw.Draw(img)
    for x in range(0, W, 70):
        d.line([(P(x), 0), (P(x), P(GY))], fill=(128, 98, 74), width=P(3))
    poly(d, [(80, 420), (240, 420), (240, 580), (80, 580)], SKY, ow=4)
    d.line([(P(160), P(420)), (P(160), P(580))], fill=OUT, width=P(4)); d.line([(P(80), P(500)), (P(240), P(500))], fill=OUT, width=P(4))
    poly(d, [(420, 700), (660, 700), (660, 725), (420, 725)], (110, 78, 54), ow=3)
    for xx in (440, 640): d.line([(P(xx), P(725)), (P(xx), P(GY))], fill=OUT, width=P(6))
    flatground(d, (120, 92, 70), (90, 68, 52))
    return img


def bg_dark():
    img = vgrad((14, 12, 22), (30, 26, 44)); d = ImageDraw.Draw(img)
    flatground(d, (26, 22, 38), (50, 44, 70))
    return img


def _stone(d, crack=False):
    poly(d, [(300, GY), (420, GY), (440, 640), (400, 560), (330, 560), (285, 650)], (150, 150, 175))
    for k in range(4):
        d.line([(P(320 + k * 22), P(640)), (P(330 + k * 22), P(600))], fill=(120, 220, 255), width=P(5))
    if crack:
        d.line([(P(365), P(560)), (P(350), P(640)), (P(385), P(720)), (P(360), P(820)), (P(390), P(GY))], fill=OUT, width=P(6))
        d.line([(P(350), P(640)), (P(310), P(690))], fill=OUT, width=P(5))


def bg_square(crack=False):
    img = bg_village(); d = ImageDraw.Draw(img)
    _stone(d, crack)
    return img


def bg_castle():
    img = vgrad((60, 30, 40), (120, 60, 60)); d = ImageDraw.Draw(img)
    poly(d, [(160, GY), (560, GY), (560, 420), (500, 420), (500, 380), (440, 380), (440, 420), (280, 420), (280, 380), (220, 380), (220, 420), (160, 420)], (50, 40, 55))
    poly(d, [(320, GY), (400, GY), (400, 700), (360, 650), (320, 700)], (20, 15, 20))
    ground(d, (60, 40, 45), (45, 30, 35))
    return img


BGF = dict(square=bg_square, crack=lambda: bg_square(True), night=bg_night, castle=bg_castle, village=bg_village, cave=bg_cave, sewer=bg_sewer, home=bg_home, dark=bg_dark)
BGS = {}


def getbg(n):
    if n not in BGS: BGS[n] = BGF[n]()
    return BGS[n]


# ---------------- characters ----------------
HAIR2 = {"milo": (70, 50, 35), "kid": (40, 32, 28), "hunter": (35, 35, 38), "mom": (110, 70, 45), "girl": (215, 165, 70), "sis": (110, 70, 45),
         "noble": (225, 225, 230), "rich": (235, 195, 90)}
CLOTH2 = {"milo": (120, 100, 80), "kid": (150, 120, 90), "hunter": (95, 110, 80), "mom": (140, 100, 120), "girl": (120, 160, 110), "sis": (200, 140, 160),
          "noble": (45, 40, 55), "rich": (205, 165, 70)}


def person(img, x, h=220, who="milo", face=1, mood="neutral", t=0, walk=0, arm=None, jit=0, gy=GY, tag=None):
    d = ImageDraw.Draw(img)
    h = h * 1.05
    x += jit * math.sin(t * 40)
    hr = h * 0.15
    leg = h * 0.27; tun = h * 0.36
    bob = 1.5 * math.sin(t * 2.5 + x) if not walk else 3 * abs(math.sin(t * 8))
    hem = gy - leg - bob; shy = hem - tun
    hy = shy - hr * 0.9
    sw = walk * 0.45 * math.sin(t * 9)
    col = CLOTH2.get(who, (150, 150, 150)); lw = max(4, h * 0.028)
    if who == "noble":
        poly(d, [(x - h * 0.1, shy + 4), (x + h * 0.1, shy + 4), (x + h * 0.2 - face * 10, gy), (x - h * 0.2 - face * 10, gy)], (150, 30, 40), ow=3)
    for s in (1, -1):
        a = s * (0.08 + sw)
        x0 = x + s * h * 0.045
        d.line([(P(x0), P(hem - 6)), (P(x0 + math.sin(a) * leg), P(hem + math.cos(a) * leg + bob))], fill=OUT, width=P(lw + 3))
        d.line([(P(x0), P(hem - 6)), (P(x0 + math.sin(a) * leg), P(hem + math.cos(a) * leg + bob))], fill=(85, 65, 55), width=P(lw))
    sh = (x, shy + 10); al = h * 0.27
    ends = [(x + h * 0.11 + sw * 18, sh[1] + al * 0.9), (x - h * 0.11 - sw * 18, sh[1] + al * 0.9)]
    if arm == "up": ends[0] = (x + face * h * 0.12, sh[1] - al * 0.9)
    if arm == "both": ends = [(x + h * 0.15, sh[1] - al * 0.85), (x - h * 0.15, sh[1] - al * 0.85)]
    if arm == "point": ends[0] = (x + face * al * 1.05, sh[1] + 2)
    for e in ends:
        st = (x + (1 if e[0] > x else -1) * h * 0.07, sh[1])
        d.line([(P(st[0]), P(st[1])), (P(e[0]), P(e[1]))], fill=OUT, width=P(lw + 3))
        d.line([(P(st[0]), P(st[1])), (P(e[0]), P(e[1]))], fill=SKIN, width=P(lw))
    # tunic
    poly(d, [(x - h * 0.085, shy), (x + h * 0.085, shy), (x + h * 0.12, hem), (x - h * 0.12, hem)], col, ow=3)
    if who in ("milo", "kid"):
        d.line([(P(x - h * 0.1), P(hem - tun * 0.45)), (P(x + h * 0.1), P(hem - tun * 0.45))], fill=(70, 55, 40), width=P(3))
        d.rectangle([P(x + h * 0.02), P(hem - tun * 0.3), P(x + h * 0.07), P(hem - tun * 0.12)], fill=tuple(max(0, c - 25) for c in col))
        for k in range(3):
            xx = x - h * 0.11 + k * h * 0.08
            d.polygon([(P(xx), P(hem)), (P(xx + h * 0.04), P(hem + 8)), (P(xx + h * 0.08), P(hem))], fill=col)
    if who == "noble":
        d.line([(P(x), P(shy)), (P(x), P(hem))], fill=(200, 170, 60), width=P(3))
    # head
    oval(d, x, hy, hr, hr * 1.02, SKIN, ow=3)
    hc = HAIR2.get(who, (60, 50, 40))
    if who in ("girl", "mom", "sis"):
        d.chord([P(x - hr - 2), P(hy - hr - 3), P(x + hr + 2), P(hy + hr * 0.2)], 180, 360, fill=hc, outline=OUT, width=P(3))
        oval(d, x - face * hr * 0.95, hy + hr * 0.25, hr * 0.25, hr * 0.5, hc, ow=3)
    else:
        d.chord([P(x - hr - 1), P(hy - hr - 2), P(x + hr + 1), P(hy + hr * 0.1)], 180, 360, fill=hc, outline=OUT, width=P(3))
        d.polygon([(P(x + face * hr * 0.2), P(hy - hr * 0.3)), (P(x + face * hr * 0.9), P(hy - hr * 0.1)), (P(x + face * hr * 0.6), P(hy - hr * 0.45))], fill=hc)
    if who == "milo":
        d.rectangle([P(x - hr - 1), P(hy - hr * 0.45), P(x + hr + 1), P(hy - hr * 0.25)], fill=(220, 180, 70), outline=OUT, width=P(2))
        d.polygon([(P(x - face * hr), P(hy - hr * 0.4)), (P(x - face * (hr + 22)), P(hy - hr * 0.1)), (P(x - face * (hr + 16)), P(hy + hr * 0.15))], fill=(220, 180, 70), outline=OUT)
    if who == "hunter":
        d.rectangle([P(x - hr), P(hy - hr * 0.4), P(x + hr), P(hy - hr * 0.22)], fill=(170, 45, 45))
    if who in ("noble", "rich"):
        cy0 = hy - hr * 0.82
        poly(d, [(x - hr * 0.55, cy0), (x + hr * 0.55, cy0), (x + hr * 0.6, cy0 - hr * 0.4), (x + hr * 0.25, cy0 - hr * 0.2), (x, cy0 - hr * 0.5), (x - hr * 0.25, cy0 - hr * 0.2), (x - hr * 0.6, cy0 - hr * 0.4)], YEL, ow=2)
    # face
    ex = hr * 0.36; ey = hy + hr * 0.12
    blink = ((t + x * 0.01) % 3.3) < 0.12
    for s in (-1, 1):
        cx = x + face * hr * 0.15 + s * ex
        if blink:
            d.line([(P(cx - 4), P(ey)), (P(cx + 4), P(ey))], fill=OUT, width=P(2))
        elif mood == "shock":
            d.ellipse([P(cx - 6), P(ey - 7), P(cx + 6), P(ey + 7)], fill=(255, 255, 255), outline=OUT, width=P(2))
            d.ellipse([P(cx - 2), P(ey - 2), P(cx + 2), P(ey + 2)], fill=OUT)
        else:
            d.ellipse([P(cx - 3.5), P(ey - 4), P(cx + 3.5), P(ey + 4)], fill=OUT)
        if mood == "angry":
            d.line([(P(cx - 7), P(ey - 11 - s * 3)), (P(cx + 7), P(ey - 11 + s * 3))], fill=OUT, width=P(3))
        if mood == "sad":
            d.line([(P(cx - 7), P(ey - 10 + s * 3)), (P(cx + 7), P(ey - 10 - s * 3))], fill=OUT, width=P(2))
    mx, my = x + face * hr * 0.15, hy + hr * 0.55
    if mood in ("happy", "laugh"):
        d.chord([P(mx - 10), P(my - 9), P(mx + 10), P(my + 8)], 0, 180, fill=(110, 40, 40), outline=OUT, width=P(2))
    elif mood == "shock":
        d.ellipse([P(mx - 5), P(my - 4), P(mx + 5), P(my + 8)], fill=(110, 40, 40), outline=OUT, width=P(2))
    elif mood in ("sad", "angry"):
        d.arc([P(mx - 8), P(my), P(mx + 8), P(my + 10)], 200, 340, fill=OUT, width=P(2))
    else:
        d.line([(P(mx - 6), P(my + 2)), (P(mx + 6), P(my + 2))], fill=OUT, width=P(2))
    if mood == "sad" and who in ("girl", "sis", "mom", "milo"):
        d.ellipse([P(mx + 12), P(ey + 6), P(mx + 18), P(ey + 16)], fill=(140, 200, 240))
    if mood == "laugh":
        for s in (-1, 1):
            d.text((P(x + s * hr * 1.6), P(hy - hr * 0.9)), "HA", font=font(P(16)), fill=OUT, anchor="mm")
    return hy - hr - 20


def slime(img, x, size=60, col=(120, 220, 120), t=0, mood="happy", teeth=False, crown=False, gy=GY, squash=0.0, eye=None):
    d = ImageDraw.Draw(img)
    wob = 0.06 * math.sin(t * 5) + squash
    rx = size * (1.15 + wob); ry = size * (0.85 - wob)
    cy = gy - ry + 4
    hl = tuple(min(255, c + 50) for c in col)
    oval(d, x, cy, rx, ry, col, ow=5)
    d.ellipse([P(x - rx * 0.6), P(cy - ry * 0.65), P(x - rx * 0.25), P(cy - ry * 0.35)], fill=hl)
    ey = cy - ry * 0.1
    for s in (-1, 1):
        ex = x + s * rx * 0.3
        d.ellipse([P(ex - size * 0.12), P(ey - size * 0.16), P(ex + size * 0.12), P(ey + size * 0.16)], fill=(255, 255, 255), outline=OUT, width=P(3))
        d.ellipse([P(ex - size * 0.06), P(ey - size * 0.06), P(ex + size * 0.06), P(ey + size * 0.1)], fill=eye or OUT)
    my = cy + ry * 0.3
    if mood == "chomp":
        d.ellipse([P(x - rx * 0.6), P(my - ry * 0.35), P(x + rx * 0.6), P(my + ry * 0.45)], fill=(60, 20, 30), outline=OUT, width=P(4))
    elif mood == "sad":
        d.arc([P(x - size * 0.2), P(my), P(x + size * 0.2), P(my + size * 0.2)], 200, 340, fill=OUT, width=P(3))
    else:
        d.arc([P(x - size * 0.2), P(my - size * 0.15), P(x + size * 0.2), P(my + size * 0.12)], 20, 160, fill=OUT, width=P(3))
    if teeth:
        for k in range(-2, 3):
            tx = x + k * size * 0.14
            d.polygon([(P(tx - 6), P(my + 2)), (P(tx + 6), P(my + 2)), (P(tx), P(my + 16))], fill=(255, 255, 255), outline=OUT)
    if crown:
        cyy = cy - ry - 6
        poly(d, [(x - 30, cyy), (x + 30, cyy), (x + 34, cyy - 34), (x + 15, cyy - 16), (x, cyy - 40), (x - 15, cyy - 16), (x - 34, cyy - 34)], YEL)
    return cy - ry - 22


def ratking(img, x, size=1.0, t=0, mood="angry", gy=GY, hit=0.0):
    d = ImageDraw.Draw(img)
    s = size
    col = (130, 120, 125) if hit <= 0 else (255, 255, 255)
    bx, by = x, gy - 95 * s
    # tail
    d.arc([P(bx + 60 * s), P(by - 40 * s), P(bx + 260 * s), P(by + 90 * s)], 200, 360, fill=OUT, width=P(14 * s))
    d.arc([P(bx + 60 * s), P(by - 40 * s), P(bx + 260 * s), P(by + 90 * s)], 200, 360, fill=(220, 160, 170), width=P(8 * s))
    oval(d, bx, by, 150 * s, 95 * s, col, ow=6)
    for k in range(4):
        lx = bx - 90 * s + k * 60 * s
        limb(d, (lx, by + 60 * s), (lx, gy - 6), 14 * s, col)
    hx, hy = bx - 140 * s, by - 30 * s
    poly(d, [(hx + 40 * s, hy - 60 * s), (hx + 40 * s, hy + 60 * s), (hx - 120 * s, hy + 20 * s)], col)
    for e in (-1, 1):
        oval(d, hx + 30 * s, hy - 60 * s + e * 6, 30 * s, 34 * s, (220, 160, 170))
    d.ellipse([P(hx - 10 * s), P(hy - 18 * s), P(hx + 10 * s), P(hy + 2 * s)], fill=(230, 40, 40), outline=OUT, width=P(3))
    oval(d, hx - 118 * s, hy + 18 * s, 10 * s, 9 * s, (40, 30, 30))
    # crown
    poly(d, [(bx - 40 * s, by - 90 * s), (bx + 40 * s, by - 90 * s), (bx + 46 * s, by - 135 * s), (bx + 18 * s, by - 110 * s),
             (bx, by - 145 * s), (bx - 18 * s, by - 110 * s), (bx - 46 * s, by - 135 * s)], YEL)
    for k in range(3):
        tx = hx - 70 * s + k * 18 * s
        d.polygon([(P(tx), P(hy + 30 * s)), (P(tx + 10 * s), P(hy + 30 * s)), (P(tx + 5 * s), P(hy + 46 * s))], fill=(255, 255, 255), outline=OUT)
    return by - 160 * s


def pet(img, x, kind, t=0, gy=GY, face=1):
    d = ImageDraw.Draw(img)
    if kind == "wolf":
        oval(d, x, gy - 50, 55, 32, (150, 150, 165))
        for k in (-35, 30): limb(d, (x + k, gy - 30), (x + k, gy - 4), 10, (150, 150, 165))
        poly(d, [(x + face * 40, gy - 90), (x + face * 95, gy - 60), (x + face * 40, gy - 45)], (150, 150, 165))
        poly(d, [(x + face * 45, gy - 85), (x + face * 55, gy - 115), (x + face * 65, gy - 80)], (150, 150, 165))
        d.ellipse([P(x + face * 62 - 5), P(gy - 76), P(x + face * 62 + 5), P(gy - 66)], fill=OUT)
    elif kind == "hawk":
        yy = gy - 330 + 10 * math.sin(t * 6)
        oval(d, x, yy, 34, 24, (180, 130, 80))
        poly(d, [(x - 10, yy - 10), (x - 70, yy - 40 - 20 * math.sin(t * 12)), (x + 10, yy)], (160, 110, 70))
        poly(d, [(x + face * 30, yy - 6), (x + face * 52, yy + 2), (x + face * 30, yy + 8)], YEL)
        d.ellipse([P(x + face * 18 - 4), P(yy - 10), P(x + face * 18 + 4), P(yy - 2)], fill=OUT)
    elif kind == "drake":
        oval(d, x, gy - 55, 50, 38, (220, 90, 70))
        poly(d, [(x - 10, gy - 80), (x - 60, gy - 140), (x + 10, gy - 90)], (240, 140, 90))
        oval(d, x + face * 45, gy - 95, 26, 22, (220, 90, 70))
        d.ellipse([P(x + face * 52 - 4), P(gy - 102), P(x + face * 52 + 4), P(gy - 94)], fill=OUT)
        for k in (-25, 25): limb(d, (x + k, gy - 30), (x + k, gy - 4), 10, (220, 90, 70))


# ---------------- FX ----------------
def beam(img, x, col, t, t0=0.0, item=None):
    if t < t0: return
    a = ease((t - t0) / 0.3)
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    for k in range(10):
        w = 70 - k * 6
        od.rectangle([P(x - w / 2), 0, P(x + w / 2), P(GY)], fill=col + (int(28 * a),))
    img.alpha_composite(ov.filter(ImageFilter.GaussianBlur(P(6))))
    d = ImageDraw.Draw(img)
    if item:
        yy = GY - 60 - 10 * math.sin(t * 4)
        poly(d, [(x, yy - 26), (x + 22, yy), (x, yy + 26), (x - 22, yy)], col)


def hpbar(fr, name, frac, t):
    d = ImageDraw.Draw(fr)
    d.rounded_rectangle([150, 70, 570, 100], 6, fill=(30, 20, 25), outline=(255, 255, 255), width=2)
    d.rounded_rectangle([154, 74, 154 + 412 * max(0, frac), 96], 4, fill=(220, 40, 50))
    d.text((360, 125), name, font=font(22), fill=(255, 255, 255), stroke_width=3, stroke_fill=OUT, anchor="mm")


def big(fr, text, t, t0=0.0, col=YEL, y=230, size=86):
    if t < t0: return
    q = (t - t0)
    sc = 1.0 + 0.35 * max(0, 1 - q / 0.15)
    f = font(int(size * sc))
    ImageDraw.Draw(fr).text((360, y), text, font=f, fill=col, stroke_width=6, stroke_fill=OUT, anchor="mm")


def board(fr, b, t):
    # (label, v0, v1, t0, t1, col[, sub][, glitch])
    lab, v0, v1, t0, t1, col = b[:6]; sub = b[6] if len(b) > 6 else None; gl = b[7] if len(b) > 7 else False
    d = ImageDraw.Draw(fr)
    a = ease(t / 0.2); y0 = 150
    d.rounded_rectangle([200, y0, 520, y0 + 190 * a], 14, fill=(22, 20, 28), outline=(90, 90, 100), width=4)
    if a < 0.9: return
    d.text((360, y0 + 30), lab, font=font(22), fill=(200, 200, 210), anchor="mm")
    if gl and t > t1:
        txt = "???" ; c = (255, 80, 80)
    elif gl and t > t0:
        txt = str(random.randint(10 ** (len(str(v1)) - 1), 10 ** len(str(v1)))); c = random.choice([(255, 80, 80), YEL, (120, 230, 120)])
    else:
        v = int(round(v0 + (v1 - v0) * ease((t - t0) / max(0.01, t1 - t0)))) if t > t0 else v0
        txt = f"{v:,}"; c = col
    d.text((360, y0 + 105), txt, font=font(90), fill=c, stroke_width=4, stroke_fill=OUT, anchor="mm")
    if sub:
        d.rounded_rectangle([230, y0 + 160, 490, y0 + 182], 6, fill=c)
        d.text((360, y0 + 171), sub, font=font(16), fill=OUT, anchor="mm")


def label(fr, text, col=(255, 80, 80), y=110):
    ImageDraw.Draw(fr).text((360, y), text, font=font(36), fill=col, stroke_width=5, stroke_fill=OUT, anchor="mm")


def pill(fr, text, x, y, col=(255, 255, 255), border=(255, 255, 255)):
    d = ImageDraw.Draw(fr); f = font(24)
    w = f.getlength(text) + 30
    d.rounded_rectangle([x - w / 2, y - 22, x + w / 2, y + 22], 10, fill=(25, 20, 30, 230), outline=border, width=2)
    d.text((x, y), text, font=f, fill=col, anchor="mm")


def dmg(fr, text, x, y, t, t0, col=(255, 70, 70)):
    if t < t0 or t > t0 + 1.0: return
    q = (t - t0)
    ImageDraw.Draw(fr).text((x, y - 60 * q), text, font=font(40), fill=col + (int(255 * (1 - q)),), stroke_width=4, stroke_fill=OUT + (int(255 * (1 - q)),), anchor="mm")


def lvtag(fr, text, x, y, col=(255, 255, 255)):
    d = ImageDraw.Draw(fr); f = font(20)
    w = f.getlength(text) + 18
    d.rounded_rectangle([x - w / 2, y - 16, x + w / 2, y + 16], 6, fill=(25, 20, 30), outline=col, width=2)
    d.text((x, y), text, font=f, fill=col, anchor="mm")


# ---------------- caption ----------------
def caption(fr, cap, t, vol):
    if not cap: return
    words = cap.replace("*", "").split(); reds = ["*" in w for w in cap.split()]
    n = len(words); per = (vol or 0.3 * n) / n * 0.95
    # show phrase chunks of up to 4 words (fast, like the reference)
    k = min(n - 1, int(max(0, t - 0.1) / per))
    start = (k // 4) * 4
    chunk = list(range(start, min(n, start + 4)))
    f = font(46)
    toks = [(words[i].upper(), reds[i], i <= k) for i in chunk]
    total = sum(f.getlength(w) for w, _, _ in toks) + f.getlength(" ") * (len(toks) - 1)
    x = (W - total) / 2; y = 1120
    d = ImageDraw.Draw(fr)
    for w, r, on in toks:
        if on:
            d.text((x, y), w, font=f, fill=(YEL if r else (255, 255, 255)), stroke_width=5, stroke_fill=OUT, anchor="lm")
        x += f.getlength(w) + f.getlength(" ")


# ---------------- scene rendering ----------------
def scene_frame(sc, t, T, idx):
    if sc.get("end"):
        return end_card(t, sc["end"], sc.get("series", "MY SLIME EATS BOSSES"))
    img = getbg(sc["bg"]).copy()
    u = t / T
    for b in sc.get("beams", []):
        beam(img, b[0], b[1], t, b[2] if len(b) > 2 else 0, item=True)
    tags = []
    for a in sc.get("act", []):
        if not (a.get("from", 0) <= u <= a.get("to", 1.01)): continue
        k = a["k"]
        x = a["x"] if a.get("x2") is None else a["x"] + (a["x2"] - a["x"]) * ease(u)
        if k == "p":
            top = person(img, x, a.get("h", 220) * CS, a.get("who", "kid"), a.get("face", 1), a.get("mood", "neutral"), t + a.get("ph", 0),
                         walk=1 if a.get("x2") is not None else 0, arm=a.get("arm"), jit=a.get("jit", 0))
        elif k == "slime":
            sz = E.V(a.get("size", 60), u) * CS
            top = slime(img, x, sz, a.get("col", (120, 220, 120)), t, a.get("mood", "happy"), a.get("teeth", False), a.get("crown", False),
                        squash=a.get("squash", 0.0) * math.sin(t * 14), eye=a.get("eye"))
        elif k == "rat":
            top = ratking(img, x, a.get("size", 1.0) * 1.15, t, hit=1.0 if a.get("hitflash") and (t * 10) % 2 < 1 and t < 0.6 else 0)
        elif k == "pet":
            pet(img, x, a["kind"], t, face=a.get("face", 1)); top = GY - 160
        if a.get("tag"): tags.append((a["tag"], x, top, a.get("tagcol", (255, 255, 255))))
    fx = sc.get("fx", {})
    z0, z1 = sc.get("z", (1.14, 1.2)); fxp, fyp = sc.get("f", (360, 800))
    z = z0 + (z1 - z0) * u + 0.05 * (1 - ease(t / 0.3))
    cw, ch = W * S / z, H * S / z
    sx = sy = 0
    if fx.get("shake") and t < fx["shake"]:
        am = (1 - t / fx["shake"]) * 18; sx, sy = am * math.sin(t * 90), am * math.cos(t * 70)
    cx = min(max(P(fxp) + sx * S, cw / 2), W * S - cw / 2); cy = min(max(P(fyp) + sy * S, ch / 2), H * S - ch / 2)
    fr = img.crop((int(cx - cw / 2), int(cy - ch / 2), int(cx + cw / 2), int(cy + ch / 2))).resize((W, H), Image.BILINEAR)
    # screen-space overlays (tags mapped through camera)
    for txt, x, top, col in tags:
        X = (P(x) - (cx - cw / 2)) / cw * W; Y = (P(top) - (cy - ch / 2)) / ch * H
        lvtag(fr, txt, X, Y, col)
    if fx.get("bars"):
        dd = ImageDraw.Draw(fr)
        for bx in range(30, W, 80):
            dd.rectangle([bx, 0, bx + 16, H], fill=(40, 40, 46), outline=OUT, width=3)
        dd.rectangle([0, 330, W, 352], fill=(40, 40, 46), outline=OUT, width=3)
    if fx.get("flash") and t < 0.25:
        fr = Image.blend(fr, Image.new("RGBA", (W, H), (255, 255, 255, 255)), 0.7 * (1 - t / 0.25))
    if fx.get("dark"):
        fr = Image.blend(fr, Image.new("RGBA", (W, H), (10, 5, 20, 255)), fx["dark"])
    if "hp" in fx: hpbar(fr, fx["hp"][0], E.V(fx["hp"][1], u), t)
    for p in fx.get("pills", []): pill(fr, *p)
    for dd in fx.get("dmg", []): dmg(fr, *dd[:3], t, dd[3])
    if fx.get("board"): board(fr, fx["board"], t)
    if fx.get("label"): label(fr, *(fx["label"] if isinstance(fx["label"], tuple) else (fx["label"],)))
    if fx.get("big"): big(fr, *fx["big"][:1], t, *fx["big"][1:])
    if fx.get("ui"): E.draw_ui(fr, fx["ui"], t, T)
    caption(fr, sc["cap"], t, sc.get("_vol"))
    arr = np.asarray(fr.convert("RGB")).astype(np.float32)
    arr *= (1 - E.R.VIG * 0.6)
    return np.clip(arr, 0, 255).astype(np.uint8)


def end_card(t, ep, series):
    fr = Image.new("RGBA", (W, H), (30, 24, 40, 255)); d = ImageDraw.Draw(fr)
    a = ease(t / 0.4)
    slime(fr, 0, 0) if False else None
    d.text((360, 520), series, font=font(52), fill=(255, 255, 255, int(255 * a)), stroke_width=5, stroke_fill=OUT, anchor="mm")
    b = ease((t - 0.3) / 0.3)
    d.rounded_rectangle([240, 590, 480, 650], 10, fill=(220, 60, 70, int(255 * b)))
    d.text((360, 620), f"EPISODE {ep}", font=font(30), fill=(255, 255, 255, int(255 * b)), anchor="mm")
    c = ease((t - 0.7) / 0.3)
    d.text((360, 700), f"follow for episode {ep + 1}", font=font(26), fill=(255, 214, 64, int(255 * c)), anchor="mm")
    return np.asarray(fr.convert("RGB"))


# ---------------- driver (reuses engine's audio + timing) ----------------
def prepare(ep):
    mod = importlib.import_module(f"ep{ep:02d}")
    scenes = mod.SCENES + [dict(end=getattr(mod, "EPNUM", ep), cap="", series=getattr(mod, "SERIES", "MY SLIME EATS BOSSES"))]
    for i, sc in enumerate(scenes):
        p = f"vo/ep{ep:02d}/{i:02d}.wav"
        if sc.get("cap") and os.path.exists(p):
            with wave.open(p) as w: sc["_vol"] = w.getnframes() / w.getframerate()
        if sc.get("end"): sc["_dur"] = 2.6
        else:
            vol = sc.get("_vol") or (0.33 * len(sc["cap"].split()) + 0.4)
            sc["_dur"] = max(1.4, vol + 0.12 + sc.get("hold", 0.2))
    starts = list(np.cumsum([0] + [s["_dur"] for s in scenes[:-1]]))
    return scenes, starts, sum(s["_dur"] for s in scenes)


def render_part(ep, lo, hi, out):
    scenes, starts, total = prepare(ep)
    ff = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for idx in range(lo, hi):
        sc = scenes[idx]
        f0 = int(round(starts[idx] * FPS)); f1 = int(round((starts[idx] + sc["_dur"]) * FPS))
        for fn in range(f0, f1):
            ff.stdin.write(scene_frame(sc, fn / FPS - starts[idx], sc["_dur"], idx).tobytes())
    ff.stdin.close(); ff.wait()


def main():
    ep = int(sys.argv[1])
    scenes, starts, total = prepare(ep)
    if len(sys.argv) > 2:
        for s in sys.argv[2].split(","):
            i = int(s); sc = scenes[i]
            Image.fromarray(scene_frame(sc, sc["_dur"] * 0.8, sc["_dur"], i)).save(f"pv_{ep:02d}_{i:02d}.png")
        return
    E.build_audio(scenes, starts, total, ep)
    import multiprocessing as mp
    mid = len(scenes) // 2
    ps = [mp.Process(target=render_part, args=(ep, 0, mid, f"p1_{ep:02d}.mp4")), mp.Process(target=render_part, args=(ep, mid, len(scenes), f"p2_{ep:02d}.mp4"))]
    for p in ps: p.start()
    for p in ps: p.join()
    with open(f"list_{ep:02d}.txt", "w") as f:
        f.write(f"file 'p1_{ep:02d}.mp4'\nfile 'p2_{ep:02d}.mp4'\n")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", f"list_{ep:02d}.txt", "-i", f"audio_ep{ep:02d}.wav",
                    "-c:v", "copy", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart",
                    f"SLIME_EP{ep:02d}.mp4"], check=True)
    print("done", total)


if __name__ == "__main__":
    main()
