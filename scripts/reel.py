"""Ustvari kratek Reel (1080x1920, ~8 s): tweet kartica, tekst se izpiše, nežna glasbena podlaga."""
from PIL import Image, ImageDraw, ImageFont
import os, random, subprocess, math

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H, FPS = 1080, 1920, 30
AVATAR_COLORS = [(255, 224, 204), (214, 236, 214), (255, 214, 226), (222, 214, 255), (210, 232, 250)]
BG_COLORS = [(248, 244, 255), (255, 246, 240), (243, 249, 255), (255, 243, 247), (246, 252, 246)]


def _font(name, size):
    return ImageFont.truetype(os.path.join(ROOT, "fonts", f"Poppins-{name}.ttf"), size)


def _wrap(draw, text, font, maxw):
    lines, cur = [], ""
    for word in text.split():
        t = (cur + " " + word).strip()
        if draw.textlength(t, font=font) <= maxw:
            cur = t
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def _ease(t):
    return 1 - (1 - min(max(t, 0), 1)) ** 3


def render_reel(text, out_path, seed=0):
    rnd = random.Random(seed)
    bg = rnd.choice(BG_COLORS)
    avatar = rnd.choice(AVATAR_COLORS)

    probe = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    size = 58 if len(text) < 90 else 52 if len(text) < 140 else 46
    body = _font("Regular", size)
    lines = _wrap(probe, text, body, 860)
    line_h = int(size * 1.4)

    card_w = 980
    card_h = 140 + 50 + len(lines) * line_h + 90
    cx, cy = (W - card_w) // 2, (H - card_h) // 2

    total_chars = sum(len(l) for l in lines)
    t_card, t_type_start = 0.6, 0.8
    type_dur = min(4.0, max(1.8, total_chars / 28))
    duration = t_type_start + type_dur + 3.5
    frames = int(duration * FPS)

    # pripravljena kartica brez teksta
    card = Image.new("RGBA", (card_w, card_h), (0, 0, 0, 0))
    cd = ImageDraw.Draw(card)
    cd.rounded_rectangle([0, 0, card_w - 1, card_h - 1], 40, fill=(255, 255, 255, 255))
    cd.ellipse([50, 50, 160, 160], fill=avatar)
    cd.text((185, 58), "ig: selfcqree", font=_font("Bold", 42), fill=(20, 20, 20))
    cd.text((185, 110), "@selfcqree", font=_font("Regular", 34), fill=(110, 118, 125))

    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle([cx + 6, cy + 14, cx + card_w + 6, cy + card_h + 14], 40, fill=(0, 0, 0, 22))

    ff = subprocess.Popen([
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-f", "lavfi", "-t", f"{duration:.2f}", "-i",
        # nežna akordna podlaga (C - Am), lastna, brez avtorskih pravic
        "aevalsrc='0.05*(sin(2*PI*261.6*t)+sin(2*PI*329.6*t)+sin(2*PI*392*t))*(0.6+0.4*sin(2*PI*0.25*t))"
        "*if(lt(mod(t,4),2),1,0)+0.05*(sin(2*PI*220*t)+sin(2*PI*261.6*t)+sin(2*PI*329.6*t))"
        "*(0.6+0.4*sin(2*PI*0.25*t))*if(gte(mod(t,4),2),1,0)':s=44100",
        "-af", f"lowpass=f=1800,afade=t=in:d=0.8,afade=t=out:st={duration-1.2:.2f}:d=1.2",
        "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-crf", "20",
        "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", out_path,
    ], stdin=subprocess.PIPE)

    for i in range(frames):
        t = i / FPS
        frame = Image.new("RGBA", (W, H), bg + (255,))
        p = _ease(t / t_card)
        offset = int((1 - p) * 80)
        if p > 0:
            sh = shadow.copy()
            sh.putalpha(sh.getchannel("A").point(lambda a: int(a * p)))
            frame.alpha_composite(sh, (0, offset))
            c = card.copy()
            c.putalpha(c.getchannel("A").point(lambda a: int(a * p)))
            frame.alpha_composite(c, (cx, cy + offset))

        shown = int(total_chars * min(max((t - t_type_start) / type_dur, 0), 1))
        d = ImageDraw.Draw(frame)
        y = cy + offset + 190
        left = shown
        for line in lines:
            part = line[:max(left, 0)]
            if part:
                d.text((cx + 60, y), part, font=body, fill=(20, 20, 20))
            left -= len(line)
            y += line_h
        if t > t_type_start + type_dur + 0.6:
            fp = _ease((t - t_type_start - type_dur - 0.6) / 0.6)
            ft = _font("Regular", 40)
            label = "follow @selfcqree"
            d.text(((W - d.textlength(label, font=ft)) // 2, cy + card_h + 70), label,
                   font=ft, fill=tuple(int(c + (110 - c) * fp) for c in bg))
        ff.stdin.write(frame.convert("RGB").tobytes())

    ff.stdin.close()
    if ff.wait() != 0:
        raise RuntimeError("ffmpeg ni uspel")
    return out_path


if __name__ == "__main__":
    import sys
    render_reel(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "test.mp4")
