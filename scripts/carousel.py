"""Carousel (1080x1350): naslovni slide, 5 točk, zadnji slide s pozivom."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os, random

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1080, 1350
INK, INK2, INK3 = (59, 47, 69), (107, 90, 120), (156, 138, 168)
THEMES = [  # (svetla zgoraj, svetla spodaj, poudarek)
    ((253, 236, 242), (241, 235, 253), (232, 165, 189)),
    ((241, 235, 253), (230, 242, 251), (182, 163, 230)),
    ((230, 242, 251), (233, 246, 236), (147, 195, 227)),
    ((253, 240, 230), (253, 236, 242), (240, 180, 138)),
    ((233, 246, 236), (253, 246, 230), (159, 207, 169)),
]
PRODUCTS = {
    "quiet mind": "my overthinking workbook “quiet mind”",
    "coming home to yourself": "my 30-day journal “coming home to yourself”",
    "after you": "my healing journal “after you”",
    "soft reset": "my 12-week planner “soft reset”",
}


def F(name, size):
    return ImageFont.truetype(os.path.join(ROOT, "fonts", name), size)


def wrap(d, text, font, maxw):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= maxw:
            cur = t
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


def base(theme, seed):
    top, bot, acc = theme
    im = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(im)
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)], fill=tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)))
    # mehki "bokeh" krogi
    blob = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(blob)
    r = random.Random(seed)
    for _ in range(5):
        x, y, rad = r.randint(-100, W + 100), r.randint(-100, H + 100), r.randint(120, 260)
        bd.ellipse([x - rad, y - rad, x + rad, y + rad], fill=acc + (38,))
    blob = blob.filter(ImageFilter.GaussianBlur(60))
    im.paste(blob, (0, 0), blob)
    return im


def handle(d, acc):
    f = F("Poppins-Medium.ttf", 30)
    t = "@selfcqree"
    d.text(((W - d.textlength(t, font=f)) / 2, H - 95), t, font=f, fill=INK3)


def render_carousel(item, out_prefix, seed=0, shop_live=False):
    theme = THEMES[seed % len(THEMES)]
    acc = theme[2]
    paths = []

    # 1) naslov
    im = base(theme, seed)
    d = ImageDraw.Draw(im)
    card = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(card)
    cd.rounded_rectangle([90, 300, W - 90, 1000], 60, fill=(255, 255, 255, 200))
    im.paste(card, (0, 0), card)
    kf = F("Poppins-Medium.ttf", 30)
    k = "SAVE THIS ♡".replace(" ♡", "")
    d.text(((W - d.textlength(k, font=kf)) / 2, 390), k, font=kf, fill=INK3)
    tf = F("Lora-Variable.ttf", 92)
    lines = wrap(d, item["title"], tf, W - 300)
    y = 650 - len(lines) * 55
    for l in lines:
        d.text(((W - d.textlength(l, font=tf)) / 2, y), l, font=tf, fill=INK)
        y += 112
    sf = F("Poppins-Regular.ttf", 34)
    s = "swipe"
    sw = d.textlength(s, font=sf)
    x0 = (W - sw - 70) / 2
    d.text((x0, 895), s, font=sf, fill=acc)
    ax = x0 + sw + 20
    d.line([(ax, 918), (ax + 50, 918)], fill=acc, width=4)
    d.line([(ax + 36, 905), (ax + 50, 918), (ax + 36, 931)], fill=acc, width=4, joint="curve")
    handle(d, acc)
    paths.append(f"{out_prefix}_0.jpg")
    im.save(paths[-1], "JPEG", quality=93)

    # 2-6) točke
    for i, text in enumerate(item["slides"], 1):
        im = base(theme, seed * 10 + i)
        d = ImageDraw.Draw(im)
        nf = F("Lora-Variable.ttf", 220)
        n = f"{i:02d}"
        d.text((110, 230), n, font=nf, fill=acc)
        bf = F("Lora-Variable.ttf", 70)
        y = 560
        for l in wrap(d, text, bf, W - 220):
            d.text((110, y), l, font=bf, fill=INK)
            y += 92
        d.line([(110, y + 40), (260, y + 40)], fill=acc, width=5)
        pf = F("Poppins-Regular.ttf", 28)
        pg = f"{i} / {len(item['slides'])}"
        d.text((W - 110 - d.textlength(pg, font=pf), 140), pg, font=pf, fill=INK3)
        handle(d, acc)
        paths.append(f"{out_prefix}_{i}.jpg")
        im.save(paths[-1], "JPEG", quality=93)

    # 7) poziv
    im = base(theme, seed * 10 + 9)
    d = ImageDraw.Draw(im)
    tf = F("Lora-Italic-Variable.ttf", 72)
    if shop_live and item.get("product") in PRODUCTS:
        head = "want to go deeper?"
        body = f"{PRODUCTS[item['product']]} is linked in my bio ♡".replace(" ♡", "")
    else:
        head = "save this for later"
        body = "and follow @selfcqree for more gentle, relatable reminders"
    y = 520
    for l in wrap(d, head, tf, W - 240):
        d.text(((W - d.textlength(l, font=tf)) / 2, y), l, font=tf, fill=INK)
        y += 90
    bf = F("Poppins-Regular.ttf", 38)
    y += 40
    for l in wrap(d, body, bf, W - 260):
        d.text(((W - d.textlength(l, font=bf)) / 2, y), l, font=bf, fill=INK2)
        y += 56
    cx = W // 2
    d.ellipse([cx - 14, y + 50, cx + 14, y + 78], fill=acc)
    handle(d, acc)
    paths.append(f"{out_prefix}_9.jpg")
    im.save(paths[-1], "JPEG", quality=93)
    return paths


if __name__ == "__main__":
    import json, sys
    items = json.load(open(os.path.join(ROOT, "carousels.json")))
    print(render_carousel(items[int(sys.argv[1]) if len(sys.argv) > 1 else 0], "/tmp/car", int(sys.argv[1]) if len(sys.argv) > 1 else 0, shop_live="--shop" in sys.argv))
