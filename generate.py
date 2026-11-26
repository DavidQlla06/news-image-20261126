#!/usr/bin/env python3
"""Draw the 26 November 2026 world-news front page (1024x1024 PNG).

Reads stories.json next to this file and renders a newspaper-style
front page: masthead, lead story with a drawn refinery panel, a world
map with numbered pins, a markets strip, a 12-story grid and a wire
ticker. Fully deterministic: no network, no clock, no randomness.
"""
import json
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
W, H = 1024, 1024
MARGIN = 26

PAPER = (246, 241, 230)
INK = (24, 24, 22)
RED = (178, 38, 30)
NAVY = (18, 34, 56)
NAVY_SOFT = (38, 58, 84)
GOLD = (197, 150, 48)
OCEAN = (220, 232, 234)
LAND = (201, 189, 147)
LAND_EDGE = (125, 116, 96)
MUTED = (96, 92, 82)
RULE = (178, 38, 30)

FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")


def load_font(name, size):
    path = FONT_DIR / name
    try:
        return ImageFont.truetype(str(path), size)
    except OSError:
        return ImageFont.load_default(size)


SERIF_B = lambda s: load_font("DejaVuSerif-Bold.ttf", s)
SANS_B = lambda s: load_font("DejaVuSans-Bold.ttf", s)
SANS = lambda s: load_font("DejaVuSans.ttf", s)

# Coarse continent outlines (lon, lat). Equirectangular, good enough
# for a newspaper locator map.
CONTINENTS = [
    [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80), (-85, 70),
     (-80, 73), (-65, 60), (-55, 52), (-60, 46), (-70, 42), (-75, 35),
     (-80, 32), (-85, 30), (-90, 21), (-95, 19), (-97, 16), (-105, 20),
     (-110, 23), (-115, 28), (-125, 40), (-125, 48), (-135, 58),
     (-150, 60), (-165, 60)],
    [(-55, 60), (-45, 60), (-40, 65), (-30, 68), (-22, 70), (-30, 74),
     (-45, 76), (-58, 74), (-60, 70)],
    [(-80, 9), (-75, 11), (-62, 10), (-52, 5), (-50, 0), (-44, -3),
     (-35, -8), (-40, -20), (-48, -28), (-57, -38), (-65, -41),
     (-70, -50), (-73, -53), (-73, -40), (-70, -20), (-80, -5),
     (-81, 0), (-80, 5)],
    [(-17, 15), (-10, 30), (0, 36), (10, 37), (20, 32), (30, 31),
     (35, 28), (43, 12), (51, 11), (48, 0), (40, -10), (35, -20),
     (30, -29), (20, -35), (15, -27), (12, -18), (9, -1), (9, 4),
     (-8, 5), (-13, 8), (-17, 12)],
    [(-10, 36), (-9, 43), (-2, 48), (0, 50), (5, 53), (8, 57), (10, 59),
     (18, 56), (21, 55), (24, 59), (28, 71), (40, 68), (55, 69),
     (70, 72), (90, 75), (110, 76), (130, 72), (150, 70), (170, 67),
     (178, 65), (170, 60), (162, 56), (156, 51), (142, 50), (140, 40),
     (130, 42), (127, 35), (122, 30), (120, 25), (110, 20), (105, 10),
     (100, 8), (98, 12), (95, 16), (90, 22), (86, 20), (80, 15),
     (76, 8), (72, 20), (66, 25), (60, 25), (56, 26), (52, 28),
     (48, 29), (44, 29), (40, 31), (36, 36), (30, 36), (26, 38),
     (22, 37), (19, 40), (15, 44), (12, 44), (8, 44), (3, 43),
     (-2, 44), (-2, 48), (-5, 48), (-10, 43)],
    [(-5, 50), (-3, 53), (-5, 56), (-2, 58), (0, 53), (1, 51)],
    [(130, 31), (132, 33), (135, 34), (138, 35), (140, 38), (141, 42),
     (143, 44), (140, 39), (137, 36), (133, 34)],
    [(113, -22), (114, -30), (115, -35), (120, -34), (129, -32),
     (135, -35), (140, -38), (145, -38), (150, -37), (153, -32),
     (153, -27), (146, -19), (142, -11), (137, -12), (132, -12),
     (130, -13), (126, -14), (122, -17), (118, -20)],
    [(167, -45), (170, -42), (174, -38), (177, -38), (175, -41),
     (172, -43)],
]


def project(lon, lat, box):
    """Equirectangular projection into box (x0, y0, x1, y1)."""
    x0, y0, x1, y1 = box
    x = x0 + (lon + 180.0) / 360.0 * (x1 - x0)
    y = y0 + (78.0 - lat) / 134.0 * (y1 - y0)
    return x, y


def wrap_lines(draw, text, font, max_w):
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_one_line(draw, text, font, max_w):
    if draw.textlength(text, font=font) <= max_w:
        return text
    while text and draw.textlength(text + "…", font=font) > max_w:
        text = text[:-1]
    return text + "…"


def draw_refinery(draw, box):
    """Flat illustration: flare stacks, tanks and smoke at dusk."""
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=NAVY)
    # dusk glow band
    draw.rectangle([x0, y1 - 64, x1, y1], fill=(52, 42, 60))
    # sun glow behind stacks
    cx, cy = x0 + (x1 - x0) * 0.62, y0 + 52
    for r, col in ((46, (214, 120, 40)), (34, (232, 150, 50)),
                   (22, (244, 186, 74))):
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
    # storage tanks
    for tx, tw, th in ((x0 + 14, 74, 34), (x0 + 96, 58, 26),
                       (x0 + 158, 66, 30)):
        draw.rectangle([tx, y1 - 26 - th, tx + tw, y1 - 26], fill=(26, 48, 74),
                       outline=(90, 110, 140))
    # flare stacks
    for sx in (x0 + 216, x0 + 248, x0 + 282):
        draw.rectangle([sx, y0 + 58, sx + 9, y1 - 26], fill=(12, 22, 38))
        draw.polygon([(sx - 5, y0 + 58), (sx + 14, y0 + 58),
                      (sx + 4, y0 + 34)], fill=(240, 140, 40))
        draw.ellipse([sx - 6, y0 + 22, sx + 15, y0 + 42],
                     fill=(250, 190, 80))
    # smoke puffs drifting right
    puffs = [(x0 + 40, y0 + 26, 16), (x0 + 74, y0 + 14, 20),
             (x0 + 116, y0 + 22, 14), (x0 + 150, y0 + 10, 18)]
    for px, py, pr in puffs:
        draw.ellipse([px - pr, py - pr, px + pr, py + pr],
                     fill=(120, 118, 112))
    # ground line + caption
    draw.line([x0, y1 - 26, x1, y1 - 26], fill=GOLD, width=2)
    cap = SANS_B(13)
    draw.text((x0 + 10, y1 - 22), "RAS TANURA  •  550,000 BPD",
              font=cap, fill=(240, 220, 180))

def render():
    data = json.loads((HERE / "stories.json").read_text())
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    xL, xR = MARGIN, W - MARGIN

    # ---- masthead ---------------------------------------------------
    mast = SERIF_B(60)
    draw.text((xL, 24), "THE WORLD TODAY", font=mast, fill=INK)
    date_f = SANS_B(17)
    draw.text((xR, 30), "THURSDAY", font=date_f, fill=RED, anchor="ra")
    draw.text((xR, 52), "26 NOVEMBER 2026", font=SANS_B(19), fill=INK,
              anchor="ra")
    draw.text((xR, 76), "ONE DAY  •  ONE IMAGE", font=SANS(13),
              fill=MUTED, anchor="ra")
    draw.rectangle([xL, 104, xR, 108], fill=RULE)
    draw.text((xL, 114), "THE DAY IN ONE IMAGE  —  WORLD NEWS, THURSDAY 26 NOVEMBER 2026",
              font=SANS_B(14), fill=MUTED)

    # ---- lead story -------------------------------------------------
    lead = data["lead"]
    ly0, ly1 = 142, 322
    draw.text((xL, ly0), lead["kicker"], font=SANS_B(15), fill=RED)
    head_f = SERIF_B(37)
    lines = wrap_lines(draw, lead["headline"], head_f, 606)
    y = ly0 + 24
    for ln in lines[:2]:
        draw.text((xL, y), ln, font=head_f, fill=INK)
        y += 44
    deck_f = SANS(17)
    dy = ly0 + 116
    for ln in wrap_lines(draw, lead["deck"], deck_f, 606)[:2]:
        draw.text((xL, dy), ln, font=deck_f, fill=(52, 50, 44))
        dy += 22
    det = fit_one_line(draw, lead["detail"], SANS(14), 606)
    draw.text((xL, ly0 + 162), det, font=SANS(14), fill=MUTED)
    draw_refinery(draw, (xR - 330, ly0, xR, ly1))

    # ---- world map --------------------------------------------------
    my0 = 334
    draw.text((xL, my0), "WHERE THE NEWS HAPPENED", font=SANS_B(15),
              fill=INK)
    draw.text((xR, my0), "12 FLASH POINTS", font=SANS_B(13), fill=RED,
              anchor="ra")
    map_box = (xL, my0 + 26, xR, 596)
    draw.rectangle(map_box, fill=OCEAN, outline=LAND_EDGE)
    for poly in CONTINENTS:
        pts = [project(lon, lat, map_box) for lon, lat in poly]
        draw.polygon(pts, fill=LAND, outline=LAND_EDGE)
    # pin label offsets (dx, dy) to keep the Gulf readable
    offsets = {1: (6, -30), 2: (-70, 14), 3: (-60, -24), 4: (12, 24),
               5: (10, -26), 6: (-64, -6), 7: (-64, -12), 8: (-92, -10),
               9: (12, -22), 10: (-80, -28), 11: (14, 22), 12: (34, 28)}
    pin_f = SANS_B(13)
    lab_f = SANS_B(12)
    for pin in data["pins"]:
        px, py = project(pin["lon"], pin["lat"], map_box)
        dx, dy = offsets.get(pin["n"], (12, -22))
        draw.line([px, py, px + dx, py + dy], fill=(90, 60, 50), width=1)
        draw.text((px + dx, py + dy - 8), pin["label"], font=lab_f,
                  fill=INK, stroke_width=2, stroke_fill=PAPER)
        draw.ellipse([px - 11, py - 11, px + 11, py + 11], fill=RED,
                     outline=(255, 255, 255), width=2)
        num = str(pin["n"])
        tw = draw.textlength(num, font=pin_f)
        draw.text((px - tw / 2, py - 8), num, font=pin_f,
                  fill=(255, 255, 255))

    # ---- markets strip ----------------------------------------------
    mk_y0, mk_y1 = 608, 648
    col_w = (xR - xL) / 6
    for i, (label, value) in enumerate(data["markets"]):
        cx0 = xL + i * col_w
        draw.rectangle([cx0 + 1, mk_y0, cx0 + col_w - 1, mk_y1],
                       fill=NAVY if i % 2 == 0 else NAVY_SOFT)
        draw.text((cx0 + col_w / 2, mk_y0 + 6), label, font=SANS_B(12),
                  fill=(200, 205, 215), anchor="ma")
        down = value.startswith("-")
        vcol = (255, 120, 100) if down else (250, 210, 110)
        draw.text((cx0 + col_w / 2, mk_y0 + 21), value, font=SANS_B(16),
                  fill=vcol, anchor="ma")

    # ---- story grid -------------------------------------------------
    gy0 = 660
    draw.text((xL, gy0), "THE DAY'S NEWS", font=SANS_B(15), fill=INK)
    draw.line([xL, gy0 + 22, xR, gy0 + 22], fill=INK, width=1)
    stories = data["stories"]
    col_gap = 24
    col_w = (xR - xL - col_gap) / 2
    row_h = 44
    for idx, st in enumerate(stories):
        col = idx % 2
        row = idx // 2
        sx = xL + col * (col_w + col_gap)
        sy = gy0 + 30 + row * row_h
        tag = st["tag"]
        tag_f = SANS_B(11)
        tw = draw.textlength(tag, font=tag_f)
        draw.rectangle([sx, sy, sx + tw + 10, sy + 16], fill=RED)
        draw.text((sx + 5, sy + 2), tag, font=tag_f, fill=(255, 255, 255))
        hl_f = SANS_B(16)
        hl = fit_one_line(draw, st["headline"], hl_f,
                          col_w - tw - 18)
        draw.text((sx + tw + 16, sy), hl, font=hl_f, fill=INK)
        dt = fit_one_line(draw, st["detail"], SANS(13), col_w)
        draw.text((sx, sy + 20), dt, font=SANS(13), fill=MUTED)
        if row < 5:
            draw.line([sx, sy + row_h - 9, sx + col_w, sy + row_h - 9],
                      fill=(210, 204, 188), width=1)

    # ---- wire ticker ------------------------------------------------
    ty0, ty1 = 954, 996
    draw.rectangle([xL, ty0, xR, ty1], fill=NAVY)
    tick = "  •  ".join(data["ticker"])
    tick_f = SANS(12)
    tick_lines = wrap_lines(draw, "THE WIRE • " + tick, tick_f, xR - xL - 20)
    ty = ty0 + 5
    for ln in tick_lines[:2]:
        draw.text((xL + 10, ty), ln, font=tick_f, fill=(235, 232, 220))
        ty += 16

    out = HERE / "entry.png"
    img.save(out, "PNG")
    return out


if __name__ == "__main__":
    path = render()
    print(f"wrote {path} ({path.stat().st_size} bytes)")
