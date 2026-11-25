"""Data-driven episode renderer for UNRANKED. Usage: python3 engine.py EP [scene_idx_for_preview]"""
import math, random, subprocess, sys, wave, os, importlib
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import render as R
from render import P, W, H, S, FPS, GY, INK, RED, CREAM, GRAY, WHITE, ease, font, vgrad, add_glow, ground, pine, wall_layer, \
    stick, draw_lantern, wraith, tag, pop, glitch_txt, capsule, fog_bands, finish, end_card

# ---------------- backgrounds ----------------
def bg_sumps():
    img = vgrad((86, 84, 82), (150, 136, 116))
    d = ImageDraw.Draw(img)
    # city above (rich district silhouette on top)
    for x, w, h in [(0, 120, 260), (110, 90, 330), (200, 140, 290), (340, 100, 360), (440, 130, 300), (570, 150, 340)]:
        d.rectangle([P(x), 0, P(x + w), P(h - 140)], fill=(120, 116, 112, 255))
        for k in range(3):
            d.rectangle([P(x + 15 + k * 30), P(h - 190), P(x + 30 + k * 30), P(h - 170)], fill=(230, 200, 140, 255))
    d.rectangle([0, P(220), P(W), P(250)], fill=(50, 46, 44, 255))  # overhang
    # drips
    for x in range(30, W, 55):
        d.line([(P(x), P(250)), (P(x), P(250 + (x * 7) % 60))], fill=(70, 66, 64, 255), width=P(2))
    # shacks
    for x, w, h in [(-10, 150, 300), (130, 120, 240), (240, 150, 320), (420, 130, 260), (540, 190, 310)]:
        c = (40, 37, 36, 255)
        d.rectangle([P(x), P(GY - h), P(x + w), P(GY)], fill=c)
        d.polygon([(P(x - 6), P(GY - h)), (P(x + w + 6), P(GY - h + 12)), (P(x + w + 6), P(GY - h - 6)), (P(x - 6), P(GY - h - 16))], fill=(30, 28, 27, 255))
        d.rectangle([P(x + w * 0.35), P(GY - h * 0.5), P(x + w * 0.55), P(GY - h * 0.3)], fill=(180, 110, 50, 255))
    # laundry line
    d.line([(P(0), P(500)), (P(W), P(470))], fill=INK, width=P(2))
    for i, x in enumerate(range(40, W, 90)):
        y = 500 - x * 30 / W
        d.rectangle([P(x), P(y), P(x + 34), P(y + 48)], fill=(200, 192, 176, 255) if i % 2 else (150, 60, 50, 255))
    # pipes
    d.rectangle([P(660), P(250), P(676), P(GY)], fill=(28, 26, 25, 255))
    ground(img, (120, 110, 96))
    d = ImageDraw.Draw(img)
    for x in (120, 400, 610):
        d.ellipse([P(x), P(GY + 18), P(x + 90), P(GY + 34)], fill=(90, 84, 78, 255))
    return img

def bg_home():
    img = vgrad((120, 110, 98), (160, 146, 124))
    d = ImageDraw.Draw(img)
    for x in range(0, W, 48):
        d.line([(P(x), 0), (P(x), P(GY))], fill=(110, 100, 88, 255), width=P(2))
    d.rectangle([P(470), P(GY - 330), P(600), P(GY)], fill=(30, 27, 26, 255))  # door
    d.rectangle([P(70), P(380), P(200), P(480)], fill=(70, 64, 58, 255))  # window
    d.line([(P(135), P(380)), (P(135), P(480))], fill=INK, width=P(4))
    d.line([(P(300), P(0)), (P(300), P(260))], fill=INK, width=P(2))
    add_glow(img, 300, 300, 160, (255, 190, 100), 0.5)
    d.ellipse([P(288), P(260), P(312), P(300)], fill=(255, 210, 130, 255))
    ground(img, (130, 118, 100))
    return img

def bg_drain():
    img = vgrad((26, 26, 28), (60, 60, 60))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, P(W), P(GY)], fill=(34, 33, 34, 255))
    d.ellipse([P(60), P(260), P(660), P(1100)], fill=(14, 14, 15, 255))
    for k in range(9):
        a = math.pi * (0.1 + 0.8 * k / 8)
        x1, y1 = 360 + 300 * math.cos(a), 680 - 420 * math.sin(a)
        d.line([(P(x1), P(y1)), (P(360 + 320 * math.cos(a)), P(680 - 440 * math.sin(a)))], fill=(50, 48, 48, 255), width=P(3))
    img2 = img
    band = vgrad((40, 46, 50), (20, 24, 26), W * S, (H - GY) * S)
    img2.alpha_composite(band, (0, P(GY)))
    d = ImageDraw.Draw(img2)
    for y in range(GY + 20, H, 40):
        d.line([(P(60), P(y)), (P(660), P(y + 4))], fill=(70, 80, 86, 255), width=P(2))
    d.line([(0, P(GY)), (P(W), P(GY))], fill=(80, 90, 96, 255), width=P(3))
    return img2

def bg_mine():
    img = vgrad((44, 40, 38), (96, 84, 72))
    d = ImageDraw.Draw(img)
    for x in range(-20, W, 60):
        L = 80 + (x * 13) % 120
        d.polygon([(P(x), 0), (P(x + 46), 0), (P(x + 23), P(L))], fill=(22, 20, 19, 255))
    for x in (90, 630):  # support beams
        d.rectangle([P(x - 12), P(260), P(x + 12), P(GY)], fill=(30, 26, 24, 255))
    d.rectangle([P(70), P(250), P(650), P(272)], fill=(30, 26, 24, 255))
    for x in (200, 520):
        d.line([(P(x), P(272)), (P(x), P(330))], fill=INK, width=P(2))
        d.rectangle([P(x - 9), P(330), P(x + 9), P(352)], fill=(255, 190, 90, 255))
        add_glow(img, x, 340, 120, (255, 170, 70), 0.45)
    ground(img, (100, 88, 74))
    return img

def bg_vault():
    img = vgrad((18, 17, 18), (54, 50, 48))
    d = ImageDraw.Draw(img)
    wall_layer(img, -40, crenel=False, col=(36, 34, 33, 255))
    d = ImageDraw.Draw(img)
    rng = random.Random(9)
    for i in range(40):
        x, y = rng.randint(20, 680), rng.randint(60, 700)
        d.line([(P(x), P(y)), (P(x + rng.randint(20, 70)), P(y))], fill=(56, 52, 50, 255), width=P(3))
    ground(img, (60, 56, 52))
    return img

def chains(img, n_whole=6, broken=False, lit=1.0, cx=360, cy=430):
    d = ImageDraw.Draw(img)
    for i in range(7):
        a = -math.pi / 2 + (i - 3) * 0.42
        L = 260
        for k in range(9):
            px = cx + math.cos(a) * (40 + k * 26); py = cy + math.sin(a) * (40 + k * 26) + 160
            col = RED if (i == 3) else (110, 104, 98, 255)
            if broken and i == 3 and k > 4: continue
            if k % 2: d.ellipse([P(px - 6), P(py - 10), P(px + 6), P(py + 10)], outline=col, width=P(3))
            else: d.ellipse([P(px - 10), P(py - 6), P(px + 10), P(py + 6)], outline=col, width=P(3))
    add_glow(img, cx, cy + 160, 70, (220, 40, 40), 0.5 * lit)

def bg_square():
    img = vgrad((150, 140, 128), (214, 196, 164))
    d = ImageDraw.Draw(img)
    for x, w, h in [(-10, 130, 420), (120, 100, 360), (520, 110, 380), (620, 120, 450)]:
        c = (96, 88, 80, 255)
        d.rectangle([P(x), P(GY - h), P(x + w), P(GY)], fill=c)
        d.polygon([(P(x - 8), P(GY - h)), (P(x + w + 8), P(GY - h)), (P(x + w / 2), P(GY - h - 60))], fill=c)
    # banners
    for x in (250, 470):
        d.rectangle([P(x), P(240), P(x + 36), P(400)], fill=RED)
        d.polygon([(P(x), P(400)), (P(x + 36), P(400)), (P(x + 18), P(380))], fill=(150, 140, 128, 255))
    # stage
    d.rectangle([P(230), P(GY - 70), P(560), P(GY)], fill=(46, 40, 38, 255))
    d.rectangle([P(220), P(GY - 80), P(570), P(GY - 66)], fill=(30, 26, 25, 255))
    ground(img, (205, 186, 152))
    return img

BGFN = dict(village=R.bg_village, dusk=R.bg_dusk, wall=R.bg_wall, wallclose=R.bg_wallclose, fog=R.bg_fog, void=R.bg_void,
            sumps=bg_sumps, home=bg_home, drain=bg_drain, mine=bg_mine, vault=bg_vault, square=bg_square)
BGS = {}

def getbg(name):
    if name not in BGS: BGS[name] = BGFN[name]()
    return BGS[name]

# ---------------- actors ----------------
def V(v, u):
    if isinstance(v, (tuple, list)) and len(v) == 2 and all(isinstance(q, (int, float)) for q in v):
        return v[0] + (v[1] - v[0]) * ease(u)
    return v

def monolith(img, lit=1.0, x=430, base=GY, crack=False):
    d = ImageDraw.Draw(img)
    d.polygon([(P(x - 40), P(base)), (P(x + 40), P(base)), (P(x + 30), P(base - 230)), (P(x), P(base - 255)), (P(x - 30), P(base - 230))], fill=INK)
    if lit > 0:
        add_glow(img, x, base - 150, 110, (220, 40, 40), 0.6 * lit)
        c = (int(60 + 140 * lit), 30, 34, 255)
        d.ellipse([P(x - 12), P(base - 162), P(x + 12), P(base - 138)], fill=c)
        d.line([(P(x), P(base - 200)), (P(x), P(base - 100))], fill=c, width=P(3))
    if crack:
        pts = [(x - 2, base - 250), (x + 8, base - 200), (x - 6, base - 150), (x + 10, base - 90), (x - 4, base)]
        d.line([(P(a), P(b)) for a, b in pts], fill=(255, 220, 200, 255), width=P(3))
        add_glow(img, x, base - 130, 90, (255, 200, 160), 0.6)

def smoke_arm(img, x, y, amt, t):
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    for k in range(int(4 + amt * 8)):
        ox = math.sin(t * 2 + k) * 14 * amt; oy = -((t * 30 + k * 13) % 60)
        r = 6 + amt * 8
        d.ellipse([P(x + ox - r), P(y + oy - r), P(x + ox + r), P(y + oy + r)], fill=(60, 10, 14, 90))
    ov = ov.filter(ImageFilter.GaussianBlur(P(4)))
    img.alpha_composite(ov)

def actor(img, a, t, T, glitching):
    u = t / T
    k = a.get("k", "fig")
    x = V(a.get("x", 360), u if a.get("x2") is None else 0)
    if a.get("x2") is not None:
        t0, t1 = a.get("tw", (0, 1))
        x = a["x"] + (a["x2"] - a["x"]) * ease((u - t0) / max(1e-6, t1 - t0))
    moving = a.get("x2") is not None and a.get("tw", (0, 1))[0] <= u <= a.get("tw", (0, 1))[1]
    h = a.get("h", 200); face = a.get("face", 1)
    walk = a.get("walk", 1.0 if moving else 0.0)
    ph = t * a.get("speed", 6) + a.get("ph", 0)
    kneel = V(a.get("kneel", 0.0), u)
    jit = a.get("jit", 0.0)
    gy = a.get("gy", GY)
    if not moving and k != "wraith":
        gy = gy + 1.2 * math.sin(t * 2.3 + x * 0.05)  # breathing bob
    col = a.get("col", INK)
    blink = ((t + x * 0.013) % 3.1) < 0.12
    if k == "wraith":
        top = wraith(img, x, rise=V(a.get("rise", 1.0), u), reach=V(a.get("reach", 0.0), u), kneel=kneel, face=face, h=h)
        head_top = top
    else:
        pose = a.get("pose", "idle")
        kw = dict(col=col, walk=walk, ph=ph, face=face, pose=pose, kneel=kneel, jitter=jit, gy=gy)
        if a.get("dig"):  # scavenging loop: kneel + reach cycling
            kw.update(kneel=0.55 + 0.25 * math.sin(t * 4), pose="reach")
        if k == "kai":
            kw.update(pose=a.get("pose", "lantern"), lantern=True)
        if k in ("guard", "brenn"):
            kw.update(pose="spear", helmet=True, spear=True, eye=RED)
        if k == "varrow":
            kw.update(eye=(220, 220, 230, 255))
        if k == "kid":
            kw.update(col=a.get("col", GRAY))
        if k == "mom":
            kw.update(col=a.get("col", (34, 30, 30, 255)))
        if k == "varrow":  # cape behind
            d = ImageDraw.Draw(img)
            d.polygon([(P(x - 22), P(gy - h * 0.82)), (P(x + 22), P(gy - h * 0.82)), (P(x + 46 - face * 10), P(gy)), (P(x - 46 - face * 10), P(gy))], fill=(40, 20, 22, 255))
        if blink: kw["eye"] = col
        head_top, lan = stick(img, x, h, **kw)
        d = ImageDraw.Draw(img)
        r = h * 0.1
        hx = x; hy = head_top + r
        if k == "nell":
            d.ellipse([P(hx - face * r * 1.4 - r * 0.5), P(hy - r * 0.2), P(hx - face * r * 1.4 + r * 0.5), P(hy + r * 0.9)], fill=col)
        if k == "mom":
            d.polygon([(P(hx - r * 1.2), P(hy + r * 0.3)), (P(hx + r * 1.2), P(hy + r * 0.3)), (P(hx), P(hy - r * 1.4))], fill=(120, 60, 50, 255))
        if k == "mira":
            d.polygon([(P(hx - r * 1.3), P(hy + r * 1.1)), (P(hx + r * 1.3), P(hy + r * 1.1)), (P(hx - face * r * 0.6), P(hy - r * 1.8))], fill=col)
            d.line([(P(hx - r * 1.3), P(hy + r * 1.1)), (P(hx - face * r * 0.6), P(hy - r * 1.8))], fill=RED, width=P(3))
            ex = hx + face * r * 0.45
            d.ellipse([P(ex - 2.5), P(hy - 2.5), P(ex + 2.5), P(hy + 2.5)], fill=WHITE)
            if a.get("knife"):
                sx, sy = x + face * h * 0.3, gy - h * 0.62
                d.line([(P(sx), P(sy)), (P(sx + face * 30), P(sy - 6))], fill=(210, 210, 215, 255), width=P(4))
        if k == "osk":
            for s in (-1, 1):
                for j in range(4):
                    yy = gy - h * 0.72 + j * h * 0.07
                    d.line([(P(x + s * h * 0.05), P(yy)), (P(x + s * h * 0.13), P(yy + 6))], fill=(170, 160, 144, 255), width=P(4))
        if k == "varrow":
            d.polygon([(P(hx - r * 1.1), P(hy + r * 1.3)), (P(hx - r * 0.3), P(hy + r * 0.2)), (P(hx - r * 0.2), P(hy + r * 1.4))], fill=(40, 20, 22, 255))
            d.polygon([(P(hx + r * 1.1), P(hy + r * 1.3)), (P(hx + r * 0.3), P(hy + r * 0.2)), (P(hx + r * 0.2), P(hy + r * 1.4))], fill=(40, 20, 22, 255))
        if k == "kai" and lan is not None:
            draw_lantern(img, lan, power=V(a.get("lp", 0.8), u), flick=math.sin(t * 17) if a.get("flick") else 0)
            if a.get("black"):
                smoke_arm(img, lan[0], lan[1] - 20, V(a["black"], u), t)
        if a.get("chair"):
            d.rectangle([P(x - 40), P(gy - h * 0.38), P(x + 30), P(gy - h * 0.32)], fill=(60, 50, 44, 255))
    tg = a.get("tag")
    if tg:
        l1, l2 = tg[0], tg[1]
        r1 = tg[2] if len(tg) > 2 else False; r2 = tg[3] if len(tg) > 3 else True
        if len(tg) > 4 and u >= tg[4][0]:  # swap at fraction
            l1, l2 = tg[4][1], tg[4][2]
        sc = pop(t, a["tp"]) if a.get("tp") is not None else 1.0
        if glitching:
            rng = random.Random(int(t * 15) + int(x))
            l1, l2 = glitch_txt(l1, rng), glitch_txt(l2, rng)
        ytop = head_top - (6 if k != "wraith" else 0)
        if k == "wraith": ytop = head_top
        tag(img, x, ytop, l1, l2, red2=r2, scale=sc, red1=r1)

# ---------------- scene frame ----------------
def scene_frame(sc, t, T, idx):
    if sc.get("end"):
        return end_card_ep(t, sc["end"])
    img = getbg(sc["bg"]).copy()
    u = t / T
    fx = sc.get("fx", {})
    if "fog" in fx: fog_bands(img, t + 3, alpha=fx["fog"], y0=fx.get("fogy", 560))
    if "stone" in fx: monolith(img, lit=V(fx["stone"], u), x=fx.get("stonex", 430), base=fx.get("stoneb", GY), crack=fx.get("crack", False) and u > 0.3)
    if "chains" in fx: chains(img, broken=fx.get("broken", False) and u > 0.4)
    if "fire" in fx:
        fxx = fx["fire"]; d = ImageDraw.Draw(img)
        add_glow(img, fxx, GY - 30, 160, (240, 110, 40), 0.6)
        for k in range(4):
            hh = 40 + 18 * math.sin(t * 9 + k * 2)
            d.polygon([(P(fxx - 30 + k * 16), P(GY)), (P(fxx - 16 + k * 16), P(GY)), (P(fxx - 23 + k * 16), P(GY - hh))], fill=RED)
        d.line([(P(fxx - 40), P(GY - 4)), (P(fxx + 40), P(GY - 8))], fill=INK, width=P(8))
    if "rainup" in fx or "dust" in fx or "embers" in fx:
        d = ImageDraw.Draw(img); rng = random.Random(5)
        if "rainup" in fx:
            for i in range(70):
                px = rng.uniform(0, W); sp = rng.uniform(120, 260); ph0 = rng.uniform(0, 900)
                py = GY - ((t * sp + ph0) % 700)
                d.line([(P(px), P(py)), (P(px), P(py + 10))], fill=(190, 196, 205, 150), width=P(1.5))
        if "dust" in fx:
            for i in range(40):
                px = (rng.uniform(0, W) + t * rng.uniform(-8, 8)) % W; py = rng.uniform(150, GY) + 10 * math.sin(t + i)
                rr = rng.uniform(1, 2.5)
                d.ellipse([P(px - rr), P(py - rr), P(px + rr), P(py + rr)], fill=(255, 235, 200, 110))
        if "embers" in fx:
            ex0 = fx["embers"]
            for i in range(25):
                sp = rng.uniform(30, 80); ph0 = rng.uniform(0, 300)
                py = GY - 20 - ((t * sp + ph0) % 300); px = ex0 + rng.uniform(-40, 40) + 15 * math.sin(t * 2 + i)
                d.ellipse([P(px - 2), P(py - 2), P(px + 2), P(py + 2)], fill=(255, 140, 60, 220))
    if "build" in fx:
        lv = V(fx["build"], u); d = ImageDraw.Draw(img)
        n = int(lv * 14)
        for i in range(n):  # palisade stakes
            sx = 20 + i * 50; hh = 120 + (i % 3) * 14
            d.polygon([(P(sx), P(GY)), (P(sx + 30), P(GY)), (P(sx + 30), P(GY - hh)), (P(sx + 15), P(GY - hh - 22)), (P(sx), P(GY - hh))], fill=(52, 40, 32, 255))
        if lv > 0.5:
            d.line([(P(10), P(GY - 80)), (P(20 + n * 50), P(GY - 80))], fill=(40, 30, 24, 255), width=P(6))
    if "forge" in fx:
        fx0 = fx["forge"]; d = ImageDraw.Draw(img)
        d.rectangle([P(fx0 - 50), P(GY - 70), P(fx0 + 50), P(GY)], fill=(34, 30, 28, 255))
        d.polygon([(P(fx0 - 30), P(GY - 70)), (P(fx0 + 30), P(GY - 70)), (P(fx0 + 20), P(GY - 160)), (P(fx0 - 20), P(GY - 160))], fill=(30, 26, 24, 255))
        add_glow(img, fx0, GY - 50, 110, (255, 120, 40), 0.55 + 0.1 * math.sin(t * 8))
        d.rectangle([P(fx0 - 30), P(GY - 60), P(fx0 + 30), P(GY - 30)], fill=(255, 140, 50, 255))
        d.polygon([(P(fx0 + 70), P(GY - 40)), (P(fx0 + 130), P(GY - 40)), (P(fx0 + 120), P(GY - 25)), (P(fx0 + 80), P(GY - 25))], fill=INK)
        d.rectangle([P(fx0 + 92), P(GY - 25), P(fx0 + 108), P(GY)], fill=INK)
    if "text" in fx:
        tx, txx, tyy, tsz, tcol = fx["text"]; d = ImageDraw.Draw(img)
        n = max(0, min(len(tx), int(len(tx) * ease(u / 0.6) + 0.999)))
        d.text((P(txx), P(tyy)), tx[:n], font=font(P(tsz)), fill=tcol, anchor="mm")
    if "hook" in fx:
        hx, hy, hs = fx["hook"]; d = ImageDraw.Draw(img)
        add_glow(img, hx, hy, hs * 1.6, (255, 240, 220), 0.35 * ease(u * 2))
        d.line([(P(hx), P(hy - hs)), (P(hx), P(hy + hs * 0.4))], fill=(235, 225, 210, 255), width=P(5))
        d.arc([P(hx - hs * 0.7), P(hy), P(hx + hs * 0.1), P(hy + hs * 0.8)], 0, 200, fill=(235, 225, 210, 255), width=P(5))
    if "smoke" in fx:
        ov = Image.new("RGBA", img.size, (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
        sx0 = fx["smoke"]
        for k in range(14):
            yy = 700 - k * 40 - (t * 20) % 40; rr = 20 + k * 4
            od.ellipse([P(sx0 + math.sin(k + t) * 12 - rr), P(yy - rr), P(sx0 + math.sin(k + t) * 12 + rr), P(yy + rr)], fill=(40, 38, 38, 120))
        img.alpha_composite(ov.filter(ImageFilter.GaussianBlur(P(10))))
    g = fx.get("glitch")
    glitching = g is not None and g[0] <= u < g[1]
    for a in sc.get("act", []):
        if a.get("from", 0) <= u <= a.get("to", 1.01):
            actor(img, a, t, T, glitching and a.get("tag") is not None)
    if "fog" in fx: fog_bands(img, t, alpha=int(fx["fog"] * 0.5), y0=700)
    if "light" in fx:
        add_glow(img, fx["light"][0], fx["light"][1], fx["light"][2] * (0.5 + 0.5 * ease(u * 2)), (255, 245, 210), 0.9)
    z0, z1 = sc.get("z", (1.0, 1.06)); fxp, fyp = sc.get("f", (360, 640))
    z = z0 + (z1 - z0) * u + 0.035 * (1 - ease(t / 0.35))  # punch-in at scene start
    pdx, pdy = sc.get("pan", (0, 0)); fxp += pdx * (u - 0.5); fyp += pdy * (u - 0.5)
    cw, ch = W * S / z, H * S / z
    sx = sy = 0.0
    shk = fx.get("shake")
    if shk and t < shk:
        am = (1 - t / shk) * 14
        sx, sy = am * math.sin(t * 90), am * math.cos(t * 70)
    cx = min(max(P(fxp) + sx * S, cw / 2), W * S - cw / 2)
    cy = min(max(P(fyp) + sy * S, ch / 2), H * S - ch / 2)
    fr = img.crop((int(cx - cw / 2), int(cy - ch / 2), int(cx + cw / 2), int(cy + ch / 2))).resize((W, H), Image.BILINEAR)
    if "blank" in fx and fx["blank"][0] <= u <= fx["blank"][1]:
        fr = Image.blend(fr.convert("RGB"), Image.new("RGB", (W, H), (235, 232, 225)), 0.35).convert("RGBA")
    if sc.get("ui"): draw_ui(fr, sc["ui"], t, T)
    caption(fr, sc["cap"], t, sc.get("_vol"))
    if t < 0.12:
        fr = Image.blend(Image.new("RGBA", (W, H), (0, 0, 0, 255)), fr, t / 0.12)
    gl = (t + 0.123) if glitching and int(t * 12) % 2 == 0 else 0.0
    rf = max(0, 1 - t / 0.5) if fx.get("redflash") else 0.0
    return finish(fr, gl, rf)

GOLD = (235, 190, 80)
def draw_ui(fr, items, t, T):
    d = ImageDraw.Draw(fr)
    for it in items:
        kind = it[0]
        if kind == "float":  # ("float", text, x, y, t0)
            _, txt, x, y, t0 = it
            if t < t0 or t > t0 + 1.4: continue
            q = min(1.0, max(0.0, (t - t0) / 1.4)); a = int(255 * (1 - q) ** 0.7)
            d.text((x, y - 70 * q), txt, font=font(30), fill=GOLD + (a,), stroke_width=3, stroke_fill=(20, 16, 14, a), anchor="mm")
        elif kind == "counter":  # ("counter", label, v0, v1, t0, t1[, suffix])
            _, lab, v0, v1, t0, t1 = it[:6]; suf = it[6] if len(it) > 6 else None
            v = int(round(v0 + (v1 - v0) * ease((t - t0) / max(0.01, t1 - t0))))
            d.rounded_rectangle([430, 60, 690, 116], 10, fill=(20, 17, 16, 210), outline=GOLD + (255,), width=2)
            d.text((448, 88), lab, font=font(22), fill=(230, 222, 205, 255), anchor="lm")
            d.text((672, 88), (f"{v}{suf}" if suf is not None else (f"{v}/40" if lab == "SCRAP" else str(v))), font=font(26), fill=GOLD + (255,), anchor="rm")
        elif kind == "window":  # ("window", title, [lines], t0)
            _, title, lines, t0 = it
            if t < t0: continue
            a = ease((t - t0) / 0.25); hgt = 70 + 46 * len(lines)
            y0 = 230; x0, x1 = 70, 650
            ov = Image.new("RGBA", fr.size, (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
            od.rounded_rectangle([x0, y0, x1, y0 + hgt * a], 8, fill=(14, 12, 12, int(225 * a)), outline=(200, 32, 38, int(255 * a)), width=3)
            fr.alpha_composite(ov); d = ImageDraw.Draw(fr)
            if a > 0.9:
                d.text(((x0 + x1) / 2, y0 + 32), title, font=font(26), fill=(200, 32, 38, 255), anchor="mm")
                d.line([(x0 + 30, y0 + 58), (x1 - 30, y0 + 58)], fill=(200, 32, 38, 180), width=2)
                chars = int((t - t0 - 0.25) * 40)
                for i, ln in enumerate(lines):
                    shown = ln[:max(0, chars)]; chars -= len(ln)
                    d.text((x0 + 34, y0 + 92 + i * 46), shown, font=font(28), fill=(240, 232, 215, 255), anchor="lm")
        elif kind == "item":  # ("item", name, rarity, stat, t0)
            _, name, rar, stat, t0 = it
            if t < t0: continue
            a = ease((t - t0) / 0.3); sc_ = 0.8 + 0.2 * a
            cx, cy = 360, 330
            w, h = 440 * sc_, 200 * sc_
            ov = Image.new("RGBA", fr.size, (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
            od.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], 12, fill=(18, 16, 15, int(230 * a)), outline=GOLD + (int(255 * a),), width=3)
            fr.alpha_composite(ov); d = ImageDraw.Draw(fr)
            if a > 0.9:
                d.text((cx, cy - 55), "NEW ITEM", font=font(20), fill=GOLD + (255,), anchor="mm")
                d.text((cx, cy - 10), name, font=font(36), fill=(245, 238, 222, 255), anchor="mm")
                d.text((cx, cy + 35), rar, font=font(22), fill=(160, 155, 150, 255), anchor="mm")
                d.text((cx, cy + 70), stat, font=font(24), fill=(120, 200, 120, 255), anchor="mm")

def caption(fr, cap, t, vol):
    if not cap: return
    words = cap.split(); n = len(words)
    per = (vol if vol else 0.32 * n) / n * 0.92
    f = font(40); sp = f.getlength(" ")
    toks = [(w.replace("*", ""), "*" in w) for w in words]
    lines, cur, cw = [], [], 0
    for w, r in toks:
        wl = f.getlength(w)
        if cur and cw + sp + wl > 600:
            lines.append((cur, cw)); cur, cw = [], 0
        cw += (sp if cur else 0) + wl; cur.append((w, r, wl))
    lines.append((cur, cw))
    d = ImageDraw.Draw(fr)
    y = 935 - (len(lines) - 1) * 26; i = 0
    for ln, lw in lines:
        x = (W - lw) / 2
        for w, r, wl in ln:
            ap = 0.2 + i * per
            if t >= ap:
                a = ease((t - ap) / 0.12)
                d.text((x, y + (1 - a) * 8), w, font=f, fill=(RED if r else WHITE)[:3] + (int(255 * a),),
                       stroke_width=4, stroke_fill=(16, 13, 12, int(255 * a)), anchor="lm")
            x += wl + sp; i += 1
        y += 52

def end_card_ep(t, ep):
    fr = vgrad((222, 208, 180), (196, 176, 140), W, H)
    d = ImageDraw.Draw(fr)
    a = ease(t / 0.4)
    d.text((W / 2, 560), "UNRANKED", font=font(92), fill=(22, 18, 17, int(255 * a)), anchor="mm")
    d.line([(150, 625), (570, 620)], fill=RED[:3] + (int(255 * a),), width=7)
    b = ease((t - 0.4) / 0.3)
    d.rounded_rectangle([240, 660, 480, 718], 6, fill=RED[:3] + (int(255 * b),))
    d.text((W / 2, 690), f"EPISODE {ep}", font=font(30), fill=(255, 255, 255, int(255 * b)), anchor="mm")
    c = ease((t - 0.8) / 0.3)
    msg = "follow so you don't miss part %d" % (ep + 1) if ep < 12 else "season 2 is coming. follow."
    d.text((W / 2, 765), msg, font=font(22), fill=(90, 80, 70, int(255 * c)), anchor="mm")
    return finish(fr)

# ---------------- audio ----------------
def build_audio(scenes, starts, total, ep):
    sr = 44100; n = int(total * sr); tt = np.arange(n) / sr
    lfo = 0.6 + 0.4 * np.sin(2 * np.pi * 0.07 * tt)
    base = [55, 49, 58.3, 52][ep % 4]
    drone = (np.sin(2 * np.pi * base * tt) * 0.5 + np.sin(2 * np.pi * base * 1.5 * tt) * 0.3 + np.sin(2 * np.pi * base * 2.005 * tt) * 0.15) * lfo
    rng = np.random.default_rng(ep)
    wind = np.convolve(rng.standard_normal(n), np.ones(400) / 400, mode="same") * 3.0 * (0.5 + 0.5 * np.sin(2 * np.pi * 0.05 * tt + 1))
    out = drone * 0.18 + wind * 0.1
    def add(sig, at):
        i = int(at * sr); j = min(n, i + len(sig))
        if i < n: out[i:j] += sig[: j - i]
    for sc, st in zip(scenes, starts):
        if sc.get("boom"):
            q = np.arange(int(1.6 * sr)) / sr
            add(np.sin(2 * np.pi * np.cumsum(70 * np.exp(-q * 1.5) + 32) / sr) * np.exp(-q * 2.2) * 0.8, st)
        else:
            q = np.arange(int(0.08 * sr)) / sr
            add(rng.standard_normal(len(q)) * np.exp(-q * 60) * 0.12, st)
        if sc.get("heart"):
            for b in np.arange(st, st + sc["_dur"], 0.75):
                for o in (0, 0.18):
                    q = np.arange(int(0.25 * sr)) / sr
                    add(np.sin(2 * np.pi * 48 * q) * np.exp(-q * 18) * 0.7, b + o)
        if sc.get("riser"):
            L = sc["_dur"] * 0.7; q = np.arange(int(L * sr)) / sr
            ns = rng.standard_normal(len(q)); ns = ns - np.convolve(ns, np.ones(20) / 20, mode="same")
            add(ns * (q / L) ** 2 * 0.25 + np.sin(2 * np.pi * (200 + 600 * (q / L) ** 2) * q) * (q / L) ** 2 * 0.08, st)
    vo = np.zeros(n)
    for i, (sc, st) in enumerate(zip(scenes, starts)):
        p = f"vo/ep{ep:02d}/{i:02d}.wav"
        if sc.get("cap") and os.path.exists(p):
            with wave.open(p) as w:
                v = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
            add_v = int((st + 0.2) * sr); j = min(n, add_v + len(v)); vo[add_v:j] += v[: j - add_v]
    env = np.convolve(np.abs(vo), np.ones(4410) / 4410, mode="same")
    duck = 1 - 0.55 * np.clip(env * 12, 0, 1)
    m = out / max(1e-6, np.abs(out).max()) * 0.5 * duck
    if np.abs(vo).max() > 0: m = m + vo / np.abs(vo).max() * 0.9
    fo = int(1.5 * sr); m[-fo:] *= np.linspace(1, 0, fo)
    m = m / max(1e-6, np.abs(m).max()) * 0.85
    st2 = np.stack([m, np.roll(m, 300)], 1)
    with wave.open(f"audio_ep{ep:02d}.wav", "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((st2 * 32767).astype(np.int16).tobytes())

def prepare(ep):
    mod = importlib.import_module(f"ep{ep:02d}")
    scenes = mod.SCENES + [dict(end=getattr(mod, "EPNUM", ep), cap="")]
    for i, sc in enumerate(scenes):
        p = f"vo/ep{ep:02d}/{i:02d}.wav"
        if sc.get("cap") and os.path.exists(p):
            with wave.open(p) as w: sc["_vol"] = w.getnframes() / w.getframerate()
        if sc.get("end"): sc["_dur"] = 3.2
        else:
            vol = sc.get("_vol") or (0.36 * len(sc["cap"].split()) + 0.6)
            sc["_dur"] = max(2.2, vol + 0.2 + sc.get("hold", 0.45))
    starts = list(np.cumsum([0] + [s["_dur"] for s in scenes[:-1]]))
    return scenes, starts, sum(s["_dur"] for s in scenes)

def render_part(ep, lo, hi, out):
    scenes, starts, total = prepare(ep)
    ff = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    # frame-accurate: global frame numbers
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
            Image.fromarray(scene_frame(sc, sc["_dur"] * 0.85, sc["_dur"], i)).save(f"pv_{ep:02d}_{i:02d}.png")
        return
    build_audio(scenes, starts, total, ep)
    mid = len(scenes) // 2
    import multiprocessing as mp
    ps = [mp.Process(target=render_part, args=(ep, 0, mid, f"p1_{ep:02d}.mp4")), mp.Process(target=render_part, args=(ep, mid, len(scenes), f"p2_{ep:02d}.mp4"))]
    for p in ps: p.start()
    for p in ps: p.join()
    with open(f"list_{ep:02d}.txt", "w") as f:
        f.write(f"file 'p1_{ep:02d}.mp4'\nfile 'p2_{ep:02d}.mp4'\n")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", f"list_{ep:02d}.txt", "-i", f"audio_ep{ep:02d}.wav",
                    "-c:v", "copy", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart",
                    f"UNRANKED_EP{ep:02d}.mp4"], check=True)
    print("done", total)

if __name__ == "__main__":
    main()
