#!/usr/bin/env python3
"""UI art: hotbar/inventory icons + the Figglebottom Productions splash card.
All drawn from primitives (PIL) — no external art. Deterministic.

Usage: python3 tools/gen_ui_art.py
"""
import math
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICONS = os.path.join(ROOT, "assets", "ui", "icons")
UI = os.path.join(ROOT, "assets", "ui")

GOLD = (222, 190, 120, 255)
GOLD_DIM = (150, 126, 82, 255)
STEEL = (200, 205, 215, 255)
DARK = (18, 15, 12, 160)


def _canvas():
    return Image.new("RGBA", (64, 64), (0, 0, 0, 0))


def _finish(img, name):
    os.makedirs(ICONS, exist_ok=True)
    img.save(os.path.join(ICONS, name + ".png"))
    print("[icon]", name)


def icon_sword():
    img = _canvas()
    d = ImageDraw.Draw(img)
    d.polygon([(32, 4), (37, 12), (36, 38), (28, 38), (27, 12)], fill=STEEL, outline=GOLD)
    d.rectangle([20, 38, 44, 42], fill=GOLD)                     # cross
    d.rectangle([30, 42, 34, 54], fill=(120, 90, 60, 255))       # grip
    d.ellipse([28, 53, 36, 61], fill=GOLD)                       # pommel
    return img


def icon_greatsword():
    img = _canvas()
    d = ImageDraw.Draw(img)
    d.polygon([(32, 2), (40, 10), (38, 36), (26, 36), (24, 10)], fill=STEEL, outline=GOLD)
    d.rectangle([14, 36, 50, 41], fill=GOLD)
    d.rectangle([29, 41, 35, 56], fill=(120, 90, 60, 255))
    d.ellipse([26, 55, 38, 63], fill=GOLD)
    d.ellipse([29, 33, 35, 39], outline=GOLD, width=2)           # sun disc
    return img


def icon_spear():
    img = _canvas()
    d = ImageDraw.Draw(img)
    d.line([(18, 58), (46, 14)], fill=(150, 110, 70, 255), width=4)
    d.polygon([(46, 14), (54, 2), (56, 16), (46, 22)], fill=STEEL, outline=GOLD)
    d.line([(44, 18), (48, 12)], fill=GOLD, width=2)             # collar
    return img


def icon_bow():
    img = _canvas()
    d = ImageDraw.Draw(img)
    d.arc([10, 6, 58, 58], start=-62, end=62, fill=(190, 160, 105, 255), width=4)
    tipx = 34 + 24 * math.cos(math.radians(62))
    d.line([(tipx, 32 - 24 * math.sin(math.radians(62))),
            (tipx, 32 + 24 * math.sin(math.radians(62)))], fill=(230, 225, 210, 255), width=2)
    d.line([(12, 32), (tipx, 32)], fill=STEEL, width=2)          # nocked arrow
    d.polygon([(8, 32), (16, 28), (16, 36)], fill=STEEL)
    d.line([(tipx - 8, 28), (tipx - 2, 32), (tipx - 8, 36)], fill=GOLD, width=2)
    return img


def icon_flask():
    img = _canvas()
    d = ImageDraw.Draw(img)
    d.rectangle([28, 8, 36, 18], fill=(120, 90, 60, 255))
    d.polygon([(28, 18), (36, 18), (44, 30), (44, 54), (20, 54), (20, 30)], outline=GOLD, fill=(40, 28, 16, 220))
    d.rectangle([23, 34, 41, 51], fill=(212, 150, 60, 235))      # the chrism
    d.ellipse([26, 6, 38, 12], fill=GOLD)
    return img


def icon_arrows():
    img = _canvas()
    d = ImageDraw.Draw(img)
    for i, x in enumerate((22, 32, 42)):
        d.line([(x, 56), (x, 14)], fill=(190, 160, 105, 255), width=3)
        d.polygon([(x - 4, 16), (x + 4, 16), (x, 6)], fill=STEEL)
        d.line([(x - 4, 52), (x, 44), (x + 4, 52)], fill=GOLD, width=2)
    return img


def icon_torch():
    img = _canvas()
    d = ImageDraw.Draw(img)
    d.polygon([(29, 26), (35, 26), (37, 56), (27, 56)], fill=(88, 62, 34, 255), outline=GOLD)
    d.rectangle([26, 20, 38, 28], fill=(120, 86, 44, 255), outline=GOLD)
    d.polygon([(32, 4), (41, 16), (36, 15), (38, 24), (26, 24), (28, 15), (23, 16)],
              fill=(244, 168, 54, 255), outline=(255, 214, 120, 255))
    return img


def icon_relic():
    img = _canvas()
    d = ImageDraw.Draw(img)
    d.polygon([(32, 6), (52, 20), (52, 50), (12, 50), (12, 20)], outline=GOLD, fill=(40, 32, 20, 210))
    d.ellipse([26, 24, 38, 36], outline=GOLD, width=2)
    d.line([(32, 36), (32, 46)], fill=GOLD, width=2)
    return img


# ------------------------------------------------------------------- rites
FLAME = (244, 168, 54, 255)
FLAME_HI = (255, 214, 120, 255)
WAX = (232, 222, 196, 255)


def icon_mend():
    """Mend the Wick: a votive candle, its flame ringed by a healing halo."""
    img = _canvas()
    d = ImageDraw.Draw(img)
    d.rectangle([26, 30, 38, 56], fill=WAX, outline=GOLD)             # the candle
    d.line([(27, 34), (25, 46)], fill=(210, 198, 168, 255), width=3)  # a run of wax
    d.ellipse([24, 52, 40, 60], fill=WAX, outline=GOLD)               # pooled foot
    d.line([(32, 30), (32, 24)], fill=(90, 70, 45, 255), width=2)     # the wick
    d.polygon([(32, 8), (38, 20), (32, 26), (26, 20)], fill=FLAME, outline=FLAME_HI)
    d.ellipse([30, 15, 34, 21], fill=FLAME_HI)
    for r in (14, 19):                                                # the halo, twice
        d.arc([32 - r, 17 - r, 32 + r, 17 + r], start=205, end=335, fill=GOLD, width=2)
    return img


def icon_lance():
    """Morrow Lance: a straight seam of morning driven through the frame."""
    img = _canvas()
    d = ImageDraw.Draw(img)
    d.line([(8, 56), (50, 14)], fill=FLAME, width=7)                  # the seam
    d.line([(8, 56), (50, 14)], fill=FLAME_HI, width=3)               # its core
    d.line([(16, 58), (44, 30)], fill=GOLD_DIM, width=2)              # trailing light
    star = []
    for i in range(8):                                                # the strike-head
        a = math.radians(i * 45 + 22)
        r = 11 if i % 2 == 0 else 4
        star.append((52 + r * math.cos(a), 12 + r * math.sin(a)))
    d.polygon(star, fill=FLAME, outline=FLAME_HI)
    d.ellipse([48, 8, 56, 16], fill=FLAME_HI)
    return img


def icon_ward():
    """Vesper Ward: a candle flame kept inside a veil of evening light."""
    img = _canvas()
    d = ImageDraw.Draw(img)
    d.arc([10, 8, 54, 62], start=-235, end=55, fill=GOLD, width=4)     # the veil
    d.arc([16, 14, 48, 56], start=-225, end=45, fill=GOLD_DIM, width=2)
    d.rectangle([29, 34, 35, 50], fill=WAX, outline=GOLD)              # the stub
    d.line([(32, 34), (32, 29)], fill=(90, 70, 45, 255), width=2)
    d.polygon([(32, 18), (37, 27), (32, 32), (27, 27)], fill=FLAME, outline=FLAME_HI)
    d.ellipse([30, 23, 34, 28], fill=FLAME_HI)
    return img


def icon_blast():
    """Radiant Blast: a thrown coal of daylight, streaking where grief aims."""
    img = _canvas()
    d = ImageDraw.Draw(img)
    for w, off in ((7, 0), (3, 0)):                                    # the tail, cored
        d.line([(10, 54 - off), (40, 24 - off)],
               fill=FLAME if w == 7 else FLAME_HI, width=w)
    d.line([(12, 44), (26, 30)], fill=GOLD_DIM, width=2)               # trailing embers
    d.line([(22, 56), (34, 44)], fill=GOLD_DIM, width=2)
    star = []
    for i in range(8):                                                 # the coal itself
        a = math.radians(i * 45)
        r = 13 if i % 2 == 0 else 6
        star.append((44 + r * math.cos(a), 20 + r * math.sin(a)))
    d.polygon(star, fill=FLAME, outline=FLAME_HI)
    d.ellipse([39, 15, 49, 25], fill=FLAME_HI)
    return img


def icon_burst():
    """Radiant Burst: the whole candle at once — noon, in every direction."""
    img = _canvas()
    d = ImageDraw.Draw(img)
    d.ellipse([8, 8, 56, 56], outline=GOLD, width=2)                   # the shockwave
    for i in range(12):                                                # the rays
        a = math.radians(i * 30)
        r0, r1 = 12, (21 if i % 3 == 0 else 17)
        d.line([(32 + r0 * math.cos(a), 32 + r0 * math.sin(a)),
                (32 + r1 * math.cos(a), 32 + r1 * math.sin(a))],
               fill=FLAME_HI if i % 3 == 0 else FLAME, width=3)
    d.ellipse([23, 23, 41, 41], fill=FLAME, outline=FLAME_HI)          # the noon disc
    d.ellipse([28, 28, 36, 36], fill=FLAME_HI)
    return img


# ---------------------------------------------------------------- splash
def _skin(t):
    """Flesh ramp: t 0 (shadow) .. 1 (highlight)."""
    a = (196, 148, 118)
    b = (240, 205, 178)
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3)) + (255,)


def splash(w=920, h=1240):
    img = Image.new("RGBA", (w, h), (226, 220, 212, 255))
    d = ImageDraw.Draw(img)
    cx = w // 2

    # --- the head: a bald dome with a heavy jaw, painted in stacked ovals
    d.ellipse([cx - 290, 210, cx + 290, 980], fill=_skin(0.55))          # skull mass
    d.ellipse([cx - 262, 250, cx + 262, 760], fill=_skin(0.72))          # dome light
    d.ellipse([cx - 150, 265, cx + 110, 470], fill=_skin(0.9))           # crown sheen
    d.polygon([(cx - 265, 640), (cx + 265, 640), (cx + 190, 990), (cx - 190, 990)],
              fill=_skin(0.6))                                            # jaw block
    # ears, wide and proud
    for sgn in (-1, 1):
        d.ellipse([cx + sgn * 318 - 52, 470, cx + sgn * 318 + 52, 640], fill=_skin(0.5))
        d.ellipse([cx + sgn * 306 - 26, 505, cx + sgn * 306 + 26, 600], fill=_skin(0.78))

    # --- brow wrinkles on the dome
    for i, y in enumerate((330, 372, 416)):
        d.arc([cx - 190 + i * 12, y, cx + 190 - i * 12, y + 90], start=200, end=340,
              fill=(166, 118, 92, 255), width=5)

    # --- eyes: gleeful squint — lower lids pushed high by the grin
    for sgn in (-1, 1):
        ex = cx + sgn * 118
        d.ellipse([ex - 56, 470, ex + 56, 544], fill=(238, 232, 224, 255))
        d.ellipse([ex - 22, 480, ex + 22, 532], fill=(122, 128, 92, 255))
        d.ellipse([ex - 9, 490, ex + 9, 520], fill=(28, 22, 18, 255))
        d.ellipse([ex - 4, 492, ex + 5, 503], fill=(252, 252, 252, 255))
        # cheek pushes the lower lid up: skin wedge over the eye's lower third
        d.ellipse([ex - 62, 516, ex + 62, 584], fill=_skin(0.68))
        d.arc([ex - 58, 508, ex + 58, 566], start=180, end=360, fill=(150, 104, 82, 255), width=6)
        d.arc([ex - 60, 458, ex + 60, 536], start=180, end=360, fill=(150, 104, 82, 255), width=6)

    # nose: a soft wedge
    d.polygon([(cx - 26, 560), (cx + 26, 560), (cx + 44, 640), (cx - 44, 640)], fill=_skin(0.42))
    d.ellipse([cx - 52, 612, cx + 52, 668], fill=_skin(0.66))

    # --- THE GRIN: an ear-to-ear smile arc, corners hooked high
    mx0, mx1 = cx - 268, cx + 268
    y_corner, y_mid = 660, 790            # quadratic smile centerline

    def smile(k):
        return y_corner + (y_mid - y_corner) * math.sin(math.pi * k)

    up, dn = 66, 74                        # cavity half-heights around the line
    upper = [(mx0 + (mx1 - mx0) * i / 40.0, smile(i / 40.0) - up) for i in range(41)]
    lower = [(mx0 + (mx1 - mx0) * i / 40.0, smile(i / 40.0) + dn) for i in range(41)]
    # lip mass first (skin shadow), then the cavity
    lip = [(x, y - 26) for (x, y) in upper] + [(x, y + 30) for (x, y) in reversed(lower)]
    d.polygon(lip, fill=_skin(0.38))
    d.polygon(upper + list(reversed(lower)), fill=(88, 46, 40, 255))
    # teeth ride the curve, two rows
    n = 11
    for i in range(n):
        k0, k1 = i / n, (i + 1) / n
        km = (k0 + k1) * 0.5
        x0 = mx0 + (mx1 - mx0) * k0 + 3
        x1 = mx0 + (mx1 - mx0) * k1 - 3
        ym = smile(km)
        d.rounded_rectangle([x0, ym - up + 4, x1, ym - 2], radius=8,
                            fill=(246, 240, 226, 255), outline=(190, 176, 152, 255), width=2)
        d.rounded_rectangle([x0, ym + 2, x1, ym + dn - 6], radius=8,
                            fill=(238, 230, 214, 255), outline=(184, 170, 146, 255), width=2)
    # smile creases hooking around the corners, up toward the cheekbones
    for sgn in (-1, 1):
        bx = cx + sgn * 285
        d.arc([bx - 60, 560, bx + 60, 700], start=(250 if sgn > 0 else 110),
              end=(70 if sgn > 0 else 290), fill=(150, 104, 82, 255), width=7)
    # chin dimple
    d.arc([cx - 90, 930, cx + 90, 1010], start=200, end=340, fill=(166, 118, 92, 255), width=6)

    # neck + shoulders fading out the bottom
    d.rectangle([cx - 120, 980, cx + 120, 1090], fill=_skin(0.5))
    d.ellipse([cx - 340, 1040, cx + 340, 1240], fill=_skin(0.62))

    img = img.filter(ImageFilter.GaussianBlur(1.1))

    # the bare card (no words) — the credits reel wants the face alone
    os.makedirs(UI, exist_ok=True)
    img.convert("RGB").save(os.path.join(UI, "trollface.png"))
    print("[splash] trollface.png", img.size)

    # --- meme text, white with a black stroke
    d = ImageDraw.Draw(img)
    font_path = os.path.join(ROOT, "assets", "fonts", "DejaVuSerif-Bold.ttf")
    f_big = ImageFont.truetype(font_path, 92)
    f_mid = ImageFont.truetype(font_path, 84)

    def stroke_text(y, text, font):
        tw = d.textlength(text, font=font)
        x = (w - tw) / 2
        d.text((x, y), text, font=font, fill=(255, 255, 255, 255),
               stroke_width=8, stroke_fill=(0, 0, 0, 255))

    stroke_text(28, "FIGGLEBOTTOM", f_big)
    stroke_text(130, "PRODUCTIONS", f_mid)
    stroke_text(h - 130, "PRESENTS", f_big)

    os.makedirs(UI, exist_ok=True)
    img.convert("RGB").save(os.path.join(UI, "figglebottom.png"))
    print("[splash] figglebottom.png", img.size)


def main():
    _finish(icon_sword(), "sword")
    _finish(icon_greatsword(), "greatsword")
    _finish(icon_spear(), "spear")
    _finish(icon_bow(), "bow")
    _finish(icon_flask(), "flask")
    _finish(icon_arrows(), "arrows")
    _finish(icon_torch(), "torch")
    _finish(icon_relic(), "relic")
    _finish(icon_mend(), "mend")
    _finish(icon_blast(), "blast")
    _finish(icon_burst(), "burst")
    _finish(icon_lance(), "lance")
    _finish(icon_ward(), "ward")
    splash()


if __name__ == "__main__":
    main()
