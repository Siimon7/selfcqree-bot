"""Ustvari sliko v stilu @selfcqree (bel 'tweet' z besedilom)."""
from PIL import Image, ImageDraw, ImageFont
import os, random

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1080, 1350
AVATAR_COLORS = [(255, 224, 204), (214, 236, 214), (255, 214, 226), (222, 214, 255), (210, 232, 250)]


def _font(name, size):
    return ImageFont.truetype(os.path.join(ROOT, "fonts", f"Poppins-{name}.ttf"), size)


def _wrap(draw, text, font, maxw):
    lines, cur = [], ""
    for word in text.split():
        test = (cur + " " + word).strip()
        if draw.textlength(test, font=font) <= maxw:
            cur = test
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def render(text, out_path, seed=0):
    rnd = random.Random(seed)
    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)

    size = 54 if len(text) < 90 else 48 if len(text) < 140 else 42
    body = _font("Regular", size)
    line_h = int(size * 1.38)
    lines = _wrap(d, text, body, W - 180)

    header_h = 110
    block_h = header_h + 40 + len(lines) * line_h
    top = (H - block_h) // 2

    d.ellipse([90, top, 200, top + 110], fill=rnd.choice(AVATAR_COLORS))
    d.text((225, top + 8), "ig: selfcqree", font=_font("Bold", 40), fill=(20, 20, 20))
    d.text((225, top + 58), "@selfcqree", font=_font("Regular", 32), fill=(110, 118, 125))

    y = top + header_h + 40
    for line in lines:
        d.text((90, y), line, font=body, fill=(20, 20, 20))
        y += line_h

    img.save(out_path, "JPEG", quality=95)
    return out_path


if __name__ == "__main__":
    import sys
    render(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "test.jpg")
