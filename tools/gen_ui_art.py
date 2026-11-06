#!/usr/bin/env python3
"""Procedural UI art generator:
  - assets/ui/trollface.png  : 140x140 inked emblem for the credits sign-off
  - assets/ui/icons/*.png    : 25 painted 128x128 Dark Souls hotbar / satchel / HUD icons
                               (rendered at 256x256 and Lanczos-downsampled)
"""
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "ui"
ICONS = OUT / "icons"
OUT.mkdir(parents=True, exist_ok=True)
ICONS.mkdir(parents=True, exist_ok=True)

GOLD = (228, 198, 134, 255)
GOLD_BRIGHT = (255, 238, 184, 255)
GOLD_DIM = (158, 132, 84, 255)
GOLD_DARK = (92, 74, 44, 255)
STEEL = (204, 210, 222, 255)
STEEL_BRIGHT = (242, 246, 255, 255)
STEEL_DARK = (96, 102, 114, 255)
IRON_DARK = (54, 58, 66, 255)
LEATHER = (138, 94, 56, 255)
LEATHER_DARK = (82, 52, 30, 255)
AMBER = (244, 168, 64, 255)
FLAME = (255, 216, 112, 255)
CRIMSON = (176, 46, 42, 255)
CRIMSON_BRIGHT = (224, 78, 68, 255)
VERDIGRIS = (86, 148, 132, 255)
BRONZE = (168, 126, 74, 255)
PARCHMENT = (228, 214, 182, 255)
PARCHMENT_DIM = (176, 158, 124, 255)
INK = (14, 11, 9, 255)


def make_trollface():
    S = 280
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    parch = (232, 222, 198, 255)
    shade = (188, 174, 146, 255)

    jaw = [
        (54, 118), (38, 78), (62, 42), (118, 28), (186, 30),
        (232, 54), (248, 96), (254, 148), (244, 198), (216, 232),
        (162, 252), (96, 248), (52, 224), (34, 186), (40, 146),
    ]
    d.polygon(jaw, fill=parch, outline=INK)
    d.polygon([(52, 224), (96, 248), (162, 252), (216, 232), (236, 206),
               (184, 222), (108, 220), (62, 198)], fill=shade)
    d.line(jaw + [jaw[0]], fill=INK, width=7, joint="curve")

    d.arc([28, 122, 92, 196], start=110, end=290, fill=INK, width=6)
    d.arc([204, 102, 262, 178], start=280, end=95, fill=INK, width=6)

    d.line([(68, 86), (96, 70), (126, 84)], fill=INK, width=7)
    d.line([(152, 82), (186, 64), (222, 80)], fill=INK, width=7)

    d.polygon([(72, 102), (102, 92), (128, 104), (104, 114)], fill=(250, 246, 236, 255), outline=INK)
    d.polygon([(154, 98), (186, 86), (218, 98), (188, 110)], fill=(250, 246, 236, 255), outline=INK)
    d.ellipse([96, 95, 112, 111], fill=INK)
    d.ellipse([180, 91, 196, 107], fill=INK)
    d.line([(68, 102), (102, 90), (130, 104)], fill=INK, width=5)
    d.line([(152, 98), (186, 84), (220, 98)], fill=INK, width=5)
    d.arc([68, 96, 130, 126], start=10, end=170, fill=INK, width=3)
    d.arc([152, 92, 220, 122], start=10, end=170, fill=INK, width=3)

    d.line([(134, 98), (124, 134), (148, 140), (156, 128)], fill=INK, width=5)

    mouth_top = [(58, 156), (96, 146), (148, 144), (198, 136), (232, 118)]
    mouth_bot = [(232, 118), (226, 174), (196, 206), (144, 218), (88, 210), (56, 184), (58, 156)]
    d.polygon(mouth_top + mouth_bot[1:-1], fill=(252, 248, 238, 255))

    teeth_x = [74, 94, 114, 134, 154, 174, 194, 212]
    for tx in teeth_x:
        t = (tx - 58) / (232 - 58)
        ty_top = int(156 - 30 * t)
        ty_bot = int(196 + 18 * math.sin(t * math.pi) - 22 * t)
        d.line([(tx, ty_top), (tx - 2, ty_bot)], fill=INK, width=4)

    mid = [(60, 172), (104, 174), (154, 172), (198, 162), (228, 144)]
    d.line(mid, fill=INK, width=4)
    d.line(mouth_top, fill=INK, width=6)
    d.line(mouth_bot, fill=INK, width=6)

    for r in range(3):
        off = r * 7
        d.arc([196 + off, 96 - off, 246 + off, 168 + off], start=300, end=70, fill=INK, width=3)
        d.arc([38 - off, 126 - off, 86 - off, 196 + off], start=120, end=240, fill=INK, width=3)

    for dy in (0, 7, 14):
        d.arc([78, 48 + dy, 204, 76 + dy], start=195, end=345, fill=INK, width=3)
    d.arc([104, 212, 176, 242], start=20, end=160, fill=INK, width=4)

    out = img.resize((140, 140), Image.Resampling.LANCZOS)
    out.save(OUT / "trollface.png")


def _new_icon(aura_col=(52, 40, 24)):
    """Create a 256x256 Dark Souls painted icon canvas with radial chiaroscuro vignette,
    dark iron backing, and bevelled double-gold filigree border."""
    S = 256
    bg = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    px = bg.load()
    cx, cy = S * 0.5, S * 0.5
    for y in range(S):
        for x in range(S):
            if x < 6 or x >= S - 6 or y < 6 or y >= S - 6:
                continue
            dx = (x - cx) / (S * 0.5)
            dy = (y - cy) / (S * 0.5)
            r = math.sqrt(dx * dx + dy * dy)
            glow = max(0.0, 1.0 - r * 1.02) ** 1.65
            vign = max(0.16, 1.0 - max(0.0, r - 0.42) * 1.15)
            # Subtle diagonal canvas weave
            weave = 1.0 + 0.03 * math.sin((x + y) * 0.35) * math.cos((x - y) * 0.35)
            cr = int((12 + aura_col[0] * glow * 0.72) * vign * weave)
            cg = int((10 + aura_col[1] * glow * 0.72) * vign * weave)
            cb = int((9 + aura_col[2] * glow * 0.72) * vign * weave)
            px[x, y] = (min(255, cr), min(255, cg), min(255, cb), 244)

    fg = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(fg)
    return (bg, fg), d


def _save_icon(canvas_pair, name: str):
    bg, fg = canvas_pair
    S = 256
    # Extract alpha of foreground to cast a soft dark oil-paint drop shadow + warm rim halo
    alpha = fg.split()[3]
    shadow = Image.new("RGBA", (S, S), (4, 3, 2, 0))
    shadow.putalpha(alpha.filter(ImageFilter.GaussianBlur(radius=6)))
    comp = Image.alpha_composite(bg, shadow)
    comp = Image.alpha_composite(comp, fg)

    # Draw bevelled outer iron & gold double border on top so nothing clips the frame
    bd = ImageDraw.Draw(comp)
    bd.rectangle([6, 6, S - 7, S - 7], outline=GOLD_DARK, width=4)
    bd.rectangle([10, 10, S - 11, S - 11], outline=GOLD_DIM, width=2)
    bd.rectangle([14, 14, S - 15, S - 15], outline=(36, 28, 18, 215), width=2)
    # Corner filigree clasps
    for rx, ry, sx, sy in [(12, 12, 1, 1), (S - 13, 12, -1, 1), (12, S - 13, 1, -1), (S - 13, S - 13, -1, -1)]:
        bd.line([(rx, ry), (rx + sx * 18, ry)], fill=GOLD, width=3)
        bd.line([(rx, ry), (rx, ry + sy * 18)], fill=GOLD, width=3)
        bd.ellipse([rx - 4, ry - 4, rx + 4, ry + 4], fill=GOLD_BRIGHT, outline=INK)

    out = comp.resize((128, 128), Image.Resampling.LANCZOS)
    out.save(ICONS / f"{name}.png")


def icon_sword():
    c, d = _new_icon((64, 52, 36))
    # Diagonal knight longsword with fuller, curved quillons, and wheel pommel
    d.polygon([(202, 40), (216, 54), (104, 166), (86, 148)], fill=STEEL_DARK, outline=INK)
    d.polygon([(202, 40), (209, 47), (95, 157), (86, 148)], fill=STEEL_BRIGHT)
    d.line([(186, 64), (102, 148)], fill=(64, 70, 82, 255), width=5)
    d.line([(202, 40), (95, 157)], fill=GOLD_BRIGHT, width=2)
    # Crossguard quillons
    d.polygon([(60, 122), (134, 196), (122, 206), (50, 134)], fill=GOLD, outline=INK)
    d.line([(58, 128), (128, 198)], fill=GOLD_BRIGHT, width=3)
    # Grip + cord risers
    d.polygon([(84, 160), (98, 174), (66, 206), (52, 192)], fill=LEATHER, outline=INK)
    for k in range(3):
        off = k * 9
        d.line([(78 - off, 166 + off), (90 - off, 178 + off)], fill=GOLD_DIM, width=2)
    # Wheel pommel
    d.ellipse([36, 192, 68, 224], fill=GOLD, outline=INK, width=4)
    d.ellipse([45, 201, 59, 215], fill=GOLD_DARK, outline=GOLD_BRIGHT, width=2)
    _save_icon(c, "sword")


def icon_greatsword():
    c, d = _new_icon((76, 56, 32))
    # Cathedral Zweihander / Claymore with parrying lugs & ricasso
    d.polygon([(214, 30), (226, 42), (102, 166), (82, 146)], fill=STEEL, outline=INK)
    d.polygon([(214, 30), (220, 36), (92, 156), (82, 146)], fill=STEEL_BRIGHT)
    # Leather-wrapped ricasso
    d.polygon([(126, 102), (154, 130), (116, 168), (88, 140)], fill=LEATHER_DARK, outline=INK)
    # Parrying lugs (flukes)
    d.polygon([(134, 108), (110, 88), (102, 98), (124, 118)], fill=GOLD, outline=INK)
    d.polygon([(150, 124), (170, 148), (160, 156), (140, 134)], fill=GOLD, outline=INK)
    # Wide arched quillons with quatrefoil terminal rings
    d.line([(46, 114), (144, 212)], fill=GOLD, width=12)
    d.line([(48, 114), (142, 208)], fill=GOLD_BRIGHT, width=4)
    d.ellipse([34, 102, 58, 126], outline=GOLD_BRIGHT, width=4)
    d.ellipse([132, 200, 156, 224], outline=GOLD_BRIGHT, width=4)
    # Two-handed grip + heavy faceted plummet pommel
    d.line([(88, 164), (48, 204)], fill=LEATHER, width=14)
    d.ellipse([32, 194, 62, 224], fill=GOLD_BRIGHT, outline=INK, width=4)
    _save_icon(c, "greatsword")


def icon_maul():
    c, d = _new_icon((78, 54, 28))
    # Sexton's Maul: heavy brass-and-iron cathedral warhammer with spiked faces & top finial
    # Long oak & iron-shod haft
    d.line([(42, 216), (178, 80)], fill=LEATHER_DARK, width=16)
    d.line([(44, 214), (176, 82)], fill=LEATHER, width=10)
    # Grip bands
    for off in (0, 22, 44):
        d.line([(50 + off, 196 - off), (62 + off, 208 - off)], fill=GOLD_DIM, width=4)
    # Top armor-piercing spike
    d.polygon([(216, 40), (186, 84), (172, 70)], fill=STEEL_BRIGHT, outline=INK)
    # Heavy octagonal hammer head block (perpendicular to haft)
    head = [(118, 54), (202, 138), (176, 164), (92, 80)]
    d.polygon(head, fill=IRON_DARK, outline=INK)
    head_hi = [(124, 60), (194, 130), (182, 142), (112, 72)]
    d.polygon(head_hi, fill=STEEL_DARK)
    # Gilt brass relief bands & striking crowns on the maul head
    d.polygon([(108, 64), (132, 40), (144, 52), (120, 76)], fill=GOLD, outline=INK)
    d.polygon([(180, 136), (214, 124), (202, 158), (168, 148)], fill=GOLD, outline=INK)
    # Striking studs
    for sx, sy in [(112, 46), (124, 34), (208, 136), (196, 148)]:
        d.ellipse([sx - 5, sy - 5, sx + 5, sy + 5], fill=GOLD_BRIGHT, outline=INK)
    # Center rosette medallion on the hammer cheek
    d.ellipse([136, 92, 164, 120], fill=GOLD, outline=INK, width=3)
    d.ellipse([144, 100, 156, 112], fill=GOLD_BRIGHT)
    _save_icon(c, "maul")


def icon_halberd():
    c, d = _new_icon((56, 62, 72))
    # Ward Halberd: towering cathedral polearm with crescent axe blade, top pike & rear fluke
    # Long ash polearm shaft
    d.line([(36, 220), (176, 80)], fill=LEATHER, width=12)
    d.line([(38, 218), (174, 82)], fill=GOLD_DIM, width=4)
    # Long needle pike tip
    d.polygon([(224, 32), (182, 88), (168, 74)], fill=STEEL_BRIGHT, outline=INK)
    # Crescent axe blade (upper-left wing)
    axe = [(156, 86), (118, 48), (82, 54), (72, 92), (104, 116), (134, 108)]
    d.polygon(axe, fill=STEEL, outline=INK)
    axe_edge = [(118, 48), (82, 54), (72, 92), (104, 116), (92, 86), (100, 62)]
    d.polygon(axe_edge, fill=STEEL_BRIGHT)
    # Cruciform cutout in axe blade
    d.ellipse([102, 74, 120, 92], fill=INK)
    # Rear armor-piercing beak fluke (lower-right wing)
    beak = [(152, 98), (196, 122), (208, 154), (174, 136), (138, 112)]
    d.polygon(beak, fill=STEEL_DARK, outline=INK)
    d.line([(156, 102), (204, 148)], fill=STEEL_BRIGHT, width=3)
    # Gilt socket collar & tassel
    d.polygon([(126, 116), (140, 130), (172, 98), (158, 84)], fill=GOLD, outline=INK)
    d.polygon([(122, 124), (146, 156), (130, 164)], fill=CRIMSON_BRIGHT, outline=INK)
    _save_icon(c, "halberd")


def icon_spear():
    c, d = _new_icon((44, 62, 50))
    # Winged Partizan spear
    d.line([(40, 216), (170, 86)], fill=LEATHER, width=12)
    d.line([(42, 214), (168, 88)], fill=GOLD_DIM, width=4)
    # Winged lugs at socket
    d.polygon([(148, 108), (118, 90), (132, 78), (158, 98)], fill=GOLD, outline=INK)
    d.polygon([(148, 108), (166, 138), (178, 124), (158, 98)], fill=GOLD, outline=INK)
    # Leaf spearhead with midrib
    d.polygon([(220, 36), (182, 104), (156, 98), (152, 74)], fill=STEEL, outline=INK)
    d.polygon([(220, 36), (185, 85), (152, 74)], fill=STEEL_BRIGHT)
    d.line([(218, 38), (158, 98)], fill=GOLD_BRIGHT, width=3)
    _save_icon(c, "spear")


def icon_bow():
    c, d = _new_icon((52, 58, 38))
    # Recurve composite bow + nocked broadhead arrow
    d.arc([48, 34, 202, 222], start=250, end=110, fill=LEATHER, width=14)
    d.arc([52, 38, 198, 218], start=252, end=108, fill=GOLD, width=5)
    # Bowstring
    d.line([(106, 40), (66, 128), (106, 216)], fill=GOLD_DIM, width=4)
    # Nocked arrow + fletching
    d.line([(56, 128), (218, 128)], fill=GOLD_BRIGHT, width=6)
    d.polygon([(226, 128), (196, 112), (204, 128), (196, 144)], fill=STEEL_BRIGHT, outline=INK)
    d.polygon([(58, 128), (40, 114), (48, 128), (40, 142)], fill=GOLD, outline=INK)
    _save_icon(c, "bow")


def icon_torch():
    c, d = _new_icon((98, 56, 20))
    # Iron cresset torch with roaring golden-amber flame
    d.polygon([(114, 126), (142, 126), (136, 222), (120, 222)], fill=LEATHER, outline=INK)
    d.polygon([(98, 102), (158, 102), (146, 132), (110, 132)], fill=STEEL_DARK, outline=INK)
    d.line([(100, 106), (156, 106)], fill=GOLD, width=5)
    d.line([(108, 126), (148, 126)], fill=GOLD, width=5)
    outer = [(128, 26), (168, 68), (156, 104), (100, 104), (88, 68)]
    inner = [(128, 44), (152, 74), (142, 100), (114, 100), (104, 74)]
    core = [(128, 62), (138, 82), (134, 98), (122, 98), (118, 82)]
    d.polygon(outer, fill=AMBER, outline=INK)
    d.polygon(inner, fill=FLAME)
    d.polygon(core, fill=(255, 250, 224, 255))
    _save_icon(c, "torch")


def icon_flask():
    c, d = _new_icon((94, 66, 22))
    # Estus / Chrism Gourd — fluted golden-amber vessel with glowing liquid soul-core
    d.ellipse([66, 94, 190, 214], fill=(112, 76, 28, 255), outline=GOLD, width=6)
    d.ellipse([78, 110, 178, 204], fill=AMBER)
    d.ellipse([94, 128, 162, 192], fill=FLAME)
    d.ellipse([110, 144, 146, 178], fill=GOLD_BRIGHT)
    # Fluted ribs across vessel body
    for rx in (92, 128, 164):
        d.arc([rx - 22, 96, rx + 22, 212], start=70, end=110, fill=GOLD_DIM, width=3)
    # Neck & flared lip
    d.rectangle([108, 56, 148, 100], fill=GOLD_DARK, outline=GOLD, width=5)
    d.line([(96, 56), (160, 56)], fill=GOLD_BRIGHT, width=8)
    for mx, my, mr in [(128, 34, 6), (104, 44, 4), (152, 42, 5)]:
        d.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=GOLD_BRIGHT)
    _save_icon(c, "flask")


def icon_arrows():
    c, d = _new_icon((54, 48, 34))
    for off, col in [(-32, GOLD_DIM), (0, GOLD_BRIGHT), (32, GOLD)]:
        x0, y0 = 60 + off, 202
        x1, y1 = 172 + off, 54
        d.line([(x0, y0), (x1, y1)], fill=col, width=6)
        d.polygon([(x1 + 10, y1 - 14), (x1 - 12, y1 + 4), (x1 + 4, y1 + 12)], fill=STEEL_BRIGHT, outline=INK)
        d.line([(x0 - 10, y0 + 4), (x0 + 6, y0 - 16)], fill=GOLD, width=5)
    _save_icon(c, "arrows")


def icon_mend():
    c, d = _new_icon((82, 68, 30))
    d.ellipse([54, 54, 202, 202], outline=GOLD_DIM, width=5)
    d.ellipse([74, 74, 182, 182], outline=GOLD, width=4)
    d.polygon([(128, 32), (142, 114), (224, 128), (142, 142),
               (128, 224), (114, 142), (32, 128), (114, 114)], fill=FLAME, outline=GOLD_BRIGHT)
    d.ellipse([106, 106, 150, 150], fill=(255, 250, 224, 255), outline=GOLD, width=4)
    _save_icon(c, "mend")


def icon_blast():
    c, d = _new_icon((88, 60, 26))
    d.line([(36, 196), (156, 104)], fill=GOLD_DIM, width=8)
    d.line([(56, 160), (146, 92)], fill=AMBER, width=6)
    d.line([(72, 212), (170, 136)], fill=AMBER, width=6)
    pts = [(222, 54), (178, 108), (192, 126), (138, 134), (152, 154), (108, 144),
           (136, 102), (120, 86), (168, 82), (158, 62)]
    d.polygon(pts, fill=FLAME, outline=GOLD_BRIGHT)
    d.ellipse([156, 68, 198, 110], fill=(255, 252, 230, 255))
    _save_icon(c, "blast")


def icon_lance():
    c, d = _new_icon((96, 74, 28))
    d.line([(34, 222), (222, 34)], fill=FLAME, width=12)
    d.line([(34, 222), (222, 34)], fill=(255, 252, 232, 255), width=5)
    d.polygon([(226, 30), (176, 56), (200, 80)], fill=GOLD_BRIGHT, outline=INK)
    d.line([(92, 120), (136, 164)], fill=GOLD_BRIGHT, width=6)
    d.line([(122, 90), (166, 134)], fill=GOLD, width=5)
    _save_icon(c, "lance")


def icon_ward():
    c, d = _new_icon((48, 64, 82))
    pts = [(64, 52), (192, 52), (192, 132), (128, 216), (64, 132)]
    d.polygon(pts, fill=(38, 44, 56, 255), outline=GOLD_BRIGHT)
    d.line(pts + [pts[0]], fill=GOLD, width=8)
    pts_in = [(82, 70), (174, 70), (174, 126), (128, 190), (82, 126)]
    d.line(pts_in + [pts_in[0]], fill=GOLD_DIM, width=4)
    d.ellipse([104, 92, 152, 140], fill=FLAME, outline=GOLD_BRIGHT, width=4)
    _save_icon(c, "ward")


def icon_burst():
    c, d = _new_icon((98, 70, 26))
    cx, cy = 128, 128
    for i in range(16):
        a = i * math.pi / 8.0
        r0 = 32
        r1 = 104 if i % 2 == 0 else 72
        w = 8 if i % 2 == 0 else 5
        col = GOLD_BRIGHT if i % 2 == 0 else AMBER
        d.line([(cx + math.cos(a) * r0, cy + math.sin(a) * r0),
                (cx + math.cos(a) * r1, cy + math.sin(a) * r1)], fill=col, width=w)
    d.ellipse([76, 76, 180, 180], outline=GOLD, width=5)
    d.ellipse([98, 98, 158, 158], fill=FLAME, outline=GOLD_BRIGHT, width=4)
    _save_icon(c, "burst")


def icon_candleglass():
    c, d = _new_icon((96, 64, 24))
    # Shard of Candleglass — jagged multifaceted stained-glass shard glowing amber-gold within
    outer = [(134, 34), (188, 78), (174, 162), (118, 222), (72, 168), (82, 86)]
    d.polygon(outer, fill=(142, 78, 24, 255), outline=GOLD_BRIGHT)
    d.line(outer + [outer[0]], fill=GOLD, width=5)
    # Internal crystalline facets
    d.polygon([(134, 34), (188, 78), (132, 126), (82, 86)], fill=AMBER, outline=GOLD_DIM)
    d.polygon([(132, 126), (188, 78), (174, 162)], fill=(214, 122, 38, 255), outline=GOLD_DIM)
    d.polygon([(104, 96), (156, 108), (142, 166), (98, 148)], fill=FLAME)
    d.polygon([(118, 112), (142, 118), (134, 148), (114, 138)], fill=(255, 250, 224, 255))
    # Lead came fracture lines
    d.line([(82, 86), (132, 126), (174, 162)], fill=GOLD_DARK, width=4)
    d.line([(134, 34), (132, 126), (118, 222)], fill=GOLD_BRIGHT, width=3)
    _save_icon(c, "candleglass")


def icon_sun_creed_charm():
    c, d = _new_icon((92, 74, 28))
    # Sun-Creed Charm — brass pilgrim medallion on chain with 12-ray sunburst relief
    # Suspension chain V
    d.arc([84, 18, 172, 102], start=0, end=180, fill=GOLD_DIM, width=6)
    d.ellipse([116, 48, 140, 72], outline=GOLD, width=5)
    # Medallion disc
    cx, cy = 128, 142
    d.ellipse([cx - 66, cy - 66, cx + 66, cy + 66], fill=GOLD_DARK, outline=GOLD_BRIGHT, width=6)
    d.ellipse([cx - 54, cy - 54, cx + 54, cy + 54], fill=(64, 48, 26, 255), outline=GOLD, width=3)
    # 12 Sunburst rays
    for i in range(12):
        a = i * math.pi / 6.0
        r1 = 50 if i % 2 == 0 else 38
        col = GOLD_BRIGHT if i % 2 == 0 else FLAME
        d.line([(cx, cy), (cx + math.cos(a) * r1, cy + math.sin(a) * r1)], fill=col, width=5)
    d.ellipse([cx - 22, cy - 22, cx + 22, cy + 22], fill=FLAME, outline=GOLD_BRIGHT, width=4)
    _save_icon(c, "sun_creed_charm")


def icon_tallow_heart():
    c, d = _new_icon((88, 52, 32))
    # Tallow Heart — carved anatomical pale-wax heart bound in gold wire with a lit wick at the aorta
    heart = [(128, 214), (72, 152), (68, 102), (98, 78), (128, 98),
             (158, 78), (188, 102), (184, 152)]
    d.polygon(heart, fill=PARCHMENT_DIM, outline=INK)
    heart_hi = [(128, 198), (84, 146), (82, 106), (102, 90), (128, 108), (154, 92), (168, 116)]
    d.polygon(heart_hi, fill=PARCHMENT)
    # Gold wire bindings across the wax heart
    d.line([(76, 128), (178, 142)], fill=GOLD, width=5)
    d.line([(88, 164), (168, 120)], fill=GOLD_BRIGHT, width=4)
    # Aorta neck + burning candle wick
    d.rectangle([116, 62, 140, 92], fill=PARCHMENT, outline=GOLD_DARK, width=4)
    d.line([(128, 48), (128, 64)], fill=INK, width=4)
    d.polygon([(128, 22), (144, 44), (136, 58), (120, 58), (112, 44)], fill=AMBER)
    d.polygon([(128, 30), (136, 46), (128, 56), (120, 46)], fill=(255, 250, 220, 255))
    # Melted wax drips
    for wx, wy1, wy2 in [(96, 128, 166), (148, 118, 158), (124, 142, 184)]:
        d.line([(wx, wy1), (wx, wy2)], fill=(245, 236, 210, 255), width=5)
    _save_icon(c, "tallow_heart")


def icon_lark_plume():
    c, d = _new_icon((64, 68, 52))
    # Plume of the Lark — graceful golden-ivory pinion feather with barbs & luminous rachis
    vane = [(208, 38), (184, 96), (148, 152), (96, 186), (68, 178),
            (78, 134), (116, 82), (166, 48)]
    d.polygon(vane, fill=PARCHMENT_DIM, outline=GOLD_DARK)
    vane_hi = [(208, 38), (166, 48), (116, 82), (82, 132), (132, 138), (176, 88)]
    d.polygon(vane_hi, fill=GOLD_BRIGHT)
    # Notch cuts in feather barbs
    for nx, ny in [(178, 96), (154, 134), (104, 96)]:
        d.polygon([(nx, ny), (nx + 18, ny - 4), (nx + 8, ny + 12)], fill=(24, 22, 18, 255))
    # Central quill / rachis
    d.line([(44, 216), (206, 40)], fill=(255, 250, 232, 255), width=6)
    d.line([(44, 216), (206, 40)], fill=GOLD, width=2)
    _save_icon(c, "lark_plume")


def icon_choir_seal():
    c, d = _new_icon((88, 36, 34))
    # Seal of the Choir — crimson signet wax seal stamped with a golden choral lyre/crest
    cx, cy = 128, 128
    # Scalloped outer wax rim
    pts = []
    for i in range(24):
        a = i * math.pi / 12.0
        r = 82 + (6 if i % 2 == 0 else -4)
        pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
    d.polygon(pts, fill=CRIMSON, outline=GOLD_DARK)
    d.line(pts + [pts[0]], fill=CRIMSON_BRIGHT, width=4)
    # Recessed inner wax stamp ring
    d.ellipse([cx - 58, cy - 58, cx + 58, cy + 58], fill=(122, 26, 24, 255), outline=GOLD, width=5)
    # Golden Choir Lyre / Tuning Fork insignia
    d.arc([cx - 28, cy - 36, cx + 28, cy + 20], start=0, end=180, fill=GOLD_BRIGHT, width=6)
    d.line([(cx - 28, cy - 8), (cx - 28, cy - 34)], fill=GOLD_BRIGHT, width=6)
    d.line([(cx + 28, cy - 8), (cx + 28, cy - 34)], fill=GOLD_BRIGHT, width=6)
    d.line([(cx, cy - 38), (cx, cy + 40)], fill=GOLD_BRIGHT, width=6)
    d.line([(cx - 14, cy - 30), (cx - 14, cy + 12)], fill=GOLD, width=3)
    d.line([(cx + 14, cy - 30), (cx + 14, cy + 12)], fill=GOLD, width=3)
    _save_icon(c, "choir_seal")


def icon_bell_fragment():
    c, d = _new_icon((46, 68, 62))
    # Bell-Metal Fragment — fractured bronze & verdigris shard of the Great Bell with relief band
    shard = [(92, 42), (178, 56), (206, 138), (168, 212), (62, 194), (52, 118)]
    d.polygon(shard, fill=BRONZE, outline=INK)
    # Verdigris patina patches
    d.polygon([(92, 42), (156, 54), (132, 116), (64, 108)], fill=VERDIGRIS)
    d.polygon([(142, 148), (198, 138), (168, 212), (112, 198)], fill=(68, 116, 104, 255))
    # Raised decorative bell inscription band across the curve
    d.arc([36, 98, 224, 232], start=200, end=340, fill=GOLD_BRIGHT, width=10)
    d.arc([36, 112, 224, 246], start=200, end=340, fill=GOLD_DARK, width=4)
    # Jagged fracture highlight on left edge
    d.line([(92, 42), (52, 118), (62, 194)], fill=GOLD_BRIGHT, width=4)
    _save_icon(c, "bell_fragment")


def icon_morrow_anthem():
    c, d = _new_icon((76, 64, 38))
    # Leaf of the Morrow Anthem — illuminated vellum choir sheet with gilt drop-cap & neumes
    page = [(62, 38), (186, 46), (196, 212), (54, 218)]
    d.polygon(page, fill=PARCHMENT, outline=GOLD_DARK)
    d.polygon([(68, 44), (180, 52), (188, 204), (62, 210)], fill=(238, 226, 196, 255))
    # Illuminated Crimson & Gold Drop-Cap Box (top-left)
    d.rectangle([76, 58, 118, 102], fill=CRIMSON, outline=GOLD, width=4)
    d.ellipse([84, 66, 110, 94], outline=GOLD_BRIGHT, width=4)
    # 4 Staves of musical neume notation
    for sy in (72, 116, 152, 184):
        x0 = 126 if sy < 100 else 76
        d.line([(x0, sy), (176, sy)], fill=CRIMSON, width=2)
        d.line([(x0, sy + 7), (176, sy + 7)], fill=CRIMSON, width=2)
        for nx in range(x0 + 10, 172, 22):
            d.rectangle([nx, sy - 3, nx + 7, sy + 5], fill=INK)
    _save_icon(c, "morrow_anthem")


def icon_penance_writ():
    c, d = _new_icon((66, 52, 40))
    # Penance Writ — tightly rolled parchment scroll bound with dark cord and hanging wax seal
    # Scroll cylinder (diagonal)
    d.polygon([(176, 42), (212, 78), (82, 208), (46, 172)], fill=PARCHMENT_DIM, outline=INK)
    d.polygon([(176, 42), (196, 62), (66, 192), (46, 172)], fill=PARCHMENT)
    # Rolled spiral ends
    d.ellipse([168, 36, 216, 84], fill=GOLD_DARK, outline=GOLD, width=4)
    d.ellipse([42, 166, 88, 212], fill=PARCHMENT_DIM, outline=INK, width=4)
    # Binding cord around waist
    d.line([(106, 108), (146, 148)], fill=LEATHER_DARK, width=10)
    d.line([(108, 110), (144, 146)], fill=GOLD, width=4)
    # Hanging ribbon + crimson seal
    d.line([(132, 134), (154, 182)], fill=CRIMSON, width=8)
    d.ellipse([136, 170, 176, 210], fill=CRIMSON_BRIGHT, outline=GOLD, width=4)
    d.ellipse([146, 180, 166, 200], fill=GOLD_BRIGHT)
    _save_icon(c, "penance_writ")


def icon_radiant_token():
    c, d = _new_icon((98, 78, 26))
    # Radiant Token — ancient struck gold sovereign coin bearing a crowned sun face
    cx, cy = 128, 128
    d.ellipse([cx - 76, cy - 76, cx + 76, cy + 76], fill=GOLD_DARK, outline=GOLD_BRIGHT, width=6)
    d.ellipse([cx - 66, cy - 66, cx + 66, cy + 66], fill=GOLD, outline=INK, width=3)
    d.ellipse([cx - 52, cy - 52, cx + 52, cy + 52], fill=(178, 142, 72, 255), outline=GOLD_BRIGHT, width=3)
    # Beaded coin rim dots
    for i in range(20):
        a = i * math.pi / 10.0
        px = cx + math.cos(a) * 59
        py = cy + math.sin(a) * 59
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=GOLD_BRIGHT)
    # Embossed Sun Face / Crown
    for i in range(8):
        a = i * math.pi / 4.0
        d.polygon([
            (cx + math.cos(a - 0.18) * 26, cy + math.sin(a - 0.18) * 26),
            (cx + math.cos(a) * 48, cy + math.sin(a) * 48),
            (cx + math.cos(a + 0.18) * 26, cy + math.sin(a + 0.18) * 26),
        ], fill=GOLD_BRIGHT, outline=GOLD_DARK)
    d.ellipse([cx - 26, cy - 26, cx + 26, cy + 26], fill=FLAME, outline=GOLD_DARK, width=4)
    _save_icon(c, "radiant_token")


def icon_censer_mace():
    c, d = _new_icon((96, 66, 26))
    # Chandler's Censer-Mace — flanged bronze liturgical mace with glowing amber wax core
    # Diagonal haft from bottom-left to top-right
    d.line([(42, 214), (168, 88)], fill=LEATHER_DARK, width=18)
    d.line([(42, 214), (168, 88)], fill=LEATHER, width=10)
    # Pommel & grip rings
    d.ellipse([28, 198, 56, 226], fill=GOLD, outline=INK, width=3)
    for gx, gy in [(68, 188), (94, 162), (120, 136)]:
        d.line([(gx - 7, gy - 7), (gx + 7, gy + 7)], fill=GOLD_BRIGHT, width=4)
    # Flanged bronze censer lantern cage head at top-right (174, 82)
    cx, cy = 172, 84
    d.ellipse([cx - 46, cy - 46, cx + 46, cy + 46], fill=(56, 40, 22, 255), outline=GOLD, width=6)
    # 6 radiating mace flanges
    for i in range(6):
        a = i * math.pi / 3.0 + math.pi / 12.0
        d.polygon([
            (cx + math.cos(a - 0.22) * 32, cy + math.sin(a - 0.22) * 32),
            (cx + math.cos(a) * 58, cy + math.sin(a) * 58),
            (cx + math.cos(a + 0.22) * 32, cy + math.sin(a + 0.22) * 32),
        ], fill=BRONZE, outline=GOLD_BRIGHT)
    # Glowing molten wax core inside the censer head
    d.ellipse([cx - 26, cy - 26, cx + 26, cy + 26], fill=AMBER, outline=GOLD_BRIGHT, width=4)
    d.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], fill=(255, 250, 220, 255))
    _save_icon(c, "censer_mace")


def icon_sovereign_wax():
    c, d = _new_icon((104, 76, 24))
    # Sovereign's Seal-Wax — hexagonal golden comb-wax cake stamped with a royal skep hive seal
    cx, cy = 128, 130
    hex_outer = []
    hex_inner = []
    for i in range(6):
        a = i * math.pi / 3.0 - math.pi / 6.0
        hex_outer.append((cx + math.cos(a) * 82, cy + math.sin(a) * 82))
        hex_inner.append((cx + math.cos(a) * 64, cy + math.sin(a) * 64))
    d.polygon(hex_outer, fill=GOLD_DARK, outline=GOLD_BRIGHT)
    d.line(hex_outer + [hex_outer[0]], fill=GOLD_BRIGHT, width=5)
    d.polygon(hex_inner, fill=(168, 118, 38, 255), outline=GOLD)
    # Stamped skep beehive dome + crown rays in the center
    d.polygon([(cx - 32, cy + 26), (cx - 24, cy - 12), (cx, cy - 32),
               (cx + 24, cy - 12), (cx + 32, cy + 26)], fill=FLAME, outline=GOLD_DARK)
    for ry in (-10, 4, 18):
        hw = 28 - abs(ry - 12) * 0.4
        d.line([(cx - hw, cy + ry), (cx + hw, cy + ry)], fill=GOLD_DARK, width=4)
    d.ellipse([cx - 10, cy + 10, cx + 10, cy + 26], fill=INK)
    _save_icon(c, "sovereign_wax")


def icon_relic():
    c, d = _new_icon((68, 56, 36))
    d.polygon([(128, 40), (200, 128), (128, 216), (56, 128)], fill=(54, 42, 26, 255), outline=GOLD, width=6)
    d.polygon([(128, 64), (176, 128), (128, 192), (80, 128)], outline=GOLD_DIM, width=4)
    d.ellipse([106, 106, 150, 150], fill=GOLD_BRIGHT, outline=INK, width=4)
    _save_icon(c, "relic")


def icon_crest():
    """Circular Covenant / Vigil Medallion for the top-left HUD beside HP/Stamina/Wick bars."""
    S = 256
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy = 128, 128
    # Outer ornate compass points
    for i in range(8):
        a = i * math.pi / 4.0
        r_tip = 120 if i % 2 == 0 else 102
        d.polygon([
            (cx + math.cos(a - 0.16) * 82, cy + math.sin(a - 0.16) * 82),
            (cx + math.cos(a) * r_tip, cy + math.sin(a) * r_tip),
            (cx + math.cos(a + 0.16) * 82, cy + math.sin(a + 0.16) * 82),
        ], fill=GOLD if i % 2 == 0 else GOLD_DIM, outline=INK)
    # Heavy bevelled dark-iron & gold ring
    d.ellipse([cx - 92, cy - 92, cx + 92, cy + 92], fill=(18, 15, 12, 245), outline=GOLD, width=7)
    d.ellipse([cx - 80, cy - 80, cx + 80, cy + 80], fill=(28, 22, 16, 255), outline=GOLD_DIM, width=3)
    # Eclipsed sun corona inside the crest
    for i in range(16):
        a = i * math.pi / 8.0
        r1 = 68 if i % 2 == 0 else 54
        d.line([(cx, cy), (cx + math.cos(a) * r1, cy + math.sin(a) * r1)], fill=AMBER, width=4)
    d.ellipse([cx - 42, cy - 42, cx + 42, cy + 42], fill=FLAME, outline=GOLD_BRIGHT, width=5)
    # Dark eclipse core with upright vigil flame
    d.ellipse([cx - 32, cy - 32, cx + 32, cy + 32], fill=(14, 11, 9, 255))
    d.polygon([(cx, cy - 22), (cx + 12, cy + 4), (cx, cy + 18), (cx - 12, cy + 4)], fill=GOLD_BRIGHT)
    out = img.resize((128, 128), Image.Resampling.LANCZOS)
    out.save(ICONS / "crest.png")


def icon_orisons():
    """Swirling golden soul-flame mote emblem for the bottom-right Orisons counter."""
    S = 256
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy = 128, 134
    d.ellipse([cx - 86, cy - 86, cx + 86, cy + 86], fill=(20, 16, 12, 230), outline=GOLD, width=6)
    d.ellipse([cx - 74, cy - 74, cx + 74, cy + 74], outline=GOLD_DIM, width=3)
    # Teardrop soul flame
    outer = [(128, 30), (176, 98), (168, 162), (128, 198), (88, 162), (80, 98)]
    inner = [(128, 56), (156, 108), (150, 154), (128, 180), (106, 154), (100, 108)]
    core = [(128, 86), (142, 122), (138, 150), (128, 164), (118, 150), (114, 122)]
    d.polygon(outer, fill=AMBER, outline=GOLD_BRIGHT)
    d.polygon(inner, fill=FLAME)
    d.polygon(core, fill=(255, 252, 232, 255))
    out = img.resize((128, 128), Image.Resampling.LANCZOS)
    out.save(ICONS / "orisons.png")


if __name__ == "__main__":
    make_trollface()
    icon_sword()
    icon_greatsword()
    icon_maul()
    icon_halberd()
    icon_spear()
    icon_bow()
    icon_torch()
    icon_flask()
    icon_arrows()
    icon_mend()
    icon_blast()
    icon_lance()
    icon_ward()
    icon_burst()
    icon_candleglass()
    icon_sun_creed_charm()
    icon_tallow_heart()
    icon_lark_plume()
    icon_choir_seal()
    icon_bell_fragment()
    icon_morrow_anthem()
    icon_penance_writ()
    icon_radiant_token()
    icon_censer_mace()
    icon_sovereign_wax()
    icon_relic()
    icon_crest()
    icon_orisons()
    print(f"wrote UI art (25 icons + trollface) -> {OUT}")
