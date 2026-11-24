"""Story (1080x1920) z vprašanjem, na katerega sledilci odgovorijo v DM (polje za odgovor je na dnu storyja)."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os, random

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1080, 1920
INK, INK2, INK3 = (59, 47, 69), (107, 90, 120), (156, 138, 168)
THEMES = [
    ((253, 236, 242), (241, 235, 253), (232, 165, 189)),
    ((241, 235, 253), (230, 242, 251), (182, 163, 230)),
    ((230, 242, 251), (233, 246, 236), (147, 195, 227)),
    ((253, 240, 230), (253, 236, 242), (240, 180, 138)),
    ((233, 246, 236), (253, 246, 230), (159, 207, 169)),
]


def F(n, s):
    return ImageFont.truetype(os.path.join(ROOT, "fonts", n), s)


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


def center(d, y, text, font, fill):
    d.text(((W - d.textlength(text, font=font)) / 2, y), text, font=font, fill=fill)


def render_story(item, out_path, seed=0):
    top, bot, acc = THEMES[seed % len(THEMES)]
    im = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(im)
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)], fill=tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)))
    blob = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(blob)
    r = random.Random(seed)
    for _ in range(6):
        x, y, rad = r.randint(-100, W + 100), r.randint(-100, H + 100), r.randint(150, 300)
        bd.ellipse([x - rad, y - rad, x + rad, y + rad], fill=acc + (40,))
    blob = blob.filter(ImageFilter.GaussianBlur(70))
    im.paste(blob, (0, 0), blob)

    # kartica (varno območje: izogne se zgornjim 250 px in spodnjim 340 px, kjer je Instagram UI)
    card = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(card)
    qf = F("Lora-Variable.ttf", 76)
    lines = wrap(d, item["q"], qf, W - 300)
    is_ab = "a" in item
    ch = 200 + len(lines) * 96 + (300 if is_ab else 120)
    y0 = (H - ch) // 2 - 60
    cd.rounded_rectangle([110, y0, W - 110, y0 + ch], 56, fill=(255, 255, 255, 215))
    im.paste(card, (0, 0), card)
    d = ImageDraw.Draw(im)
    center(d, y0 + 70, "LET'S TALK", F("Poppins-Medium.ttf", 30), INK3)
    y = y0 + 140
    for l in lines:
        center(d, y, l, qf, INK)
        y += 96
    if is_ab:
        bf = F("Poppins-Medium.ttf", 40)
        y += 40
        for letter, opt in (("A", item["a"]), ("B", item["b"])):
            d.rounded_rectangle([200, y, W - 200, y + 100], 50, outline=acc, width=4, fill=(255, 255, 255))
            d.text((250, y + 24), letter, font=bf, fill=acc)
            center(d, y + 24, opt, bf, INK)
            y += 125
        hint = "reply A or B"
    else:
        hint = item.get("hint", "reply below")
        y += 30
        center(d, y, hint, F("Poppins-Regular.ttf", 38), INK2)
        hint = "reply here"

    # strelica proti polju za odgovor
    hf = F("Poppins-Medium.ttf", 40)
    hy = H - 470
    center(d, hy, hint, hf, acc)
    cx = W // 2
    d.line([(cx, hy + 70), (cx, hy + 150)], fill=acc, width=6)
    d.line([(cx - 26, hy + 124), (cx, hy + 152), (cx + 26, hy + 124)], fill=acc, width=6, joint="curve")
    im.save(out_path, "JPEG", quality=93)
    return out_path


if __name__ == "__main__":
    import json, sys
    items = json.load(open(os.path.join(ROOT, "stories.json")))
    i = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    print(render_story(items[i], f"/tmp/story_{i}.jpg", i))
