#!/usr/bin/env python3
"""news-image-20261125: draw the poster (NOT the entrypoint).

Draws a 1024x1024 newspaper-style poster with PIL only, from scratch:
no photos, no downloaded assets, no network. Every shape is drawn with
PIL primitives. The output is fully deterministic: same bytes every run.

This script produced the entry.png shipped in the repository. The graded
entrypoint is main.py, which only copies that pre-rendered image: the
grader runs standard library only, so no Pillow at run time.

Run:  mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 draw_poster.py
"""

# How the four stories are laid out (top to bottom, two rows of two):
#  - Row one, left: the Gaza City airstrike, drawn as a dusk skyline
#    with an explosion burst over the rooftops.
#  - Row one, right: NATO's space pledge, drawn as a satellite above
#    the Earth, guarded by a shield.
#  - Row two, left: Pakistan's first astronaut, drawn as a rocket
#    climbing past the stars toward a ringed station.
#  - Row two, right: the AI stock slump, drawn as a chip under a
#    falling red chart line with the -6% figure.
# Headline text is wrapped to two lines and the standfirst to three,
# so no story overflows its card whatever the wording.

import math
import os

from PIL import Image, ImageDraw, ImageFont

SIZE = 1024

# ---- palette -------------------------------------------------------------
PAPER = (250, 247, 238)   # warm newsprint
CARD = (255, 255, 255)
INK = (26, 35, 50)        # near-black navy
RED = (178, 39, 30)
TEAL = (13, 110, 102)
SEA = (23, 92, 140)
NAVY = (30, 58, 95)
GOLD = (184, 134, 11)
GREY = (96, 102, 112)
LIGHT = (214, 232, 240)   # pale sky
SAND = (232, 222, 200)
GREEN = (46, 125, 50)
ORANGE = (230, 126, 34)
YELLOW = (244, 196, 48)
DUSK = (58, 52, 84)       # dusk sky over Gaza City
SMOKE = (120, 116, 128)


def typeface(size):
    """Pillow's bundled scalable font: identical on any machine with Pillow."""
    try:
        return ImageFont.load_default(size=size)
    except TypeError:  # very old Pillow without the size parameter
        return ImageFont.load_default()


def measure(pen, text, fnt, stroke=0):
    bounds = pen.textbbox((0, 0), text, font=fnt, stroke_width=stroke)
    return bounds[2] - bounds[0]


def wrap_lines(pen, text, fnt, max_w, stroke=0):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    out, current = [], ""
    for word in text.split(" "):
        trial = word if not current else current + " " + word
        if measure(pen, trial, fnt, stroke) <= max_w or not current:
            current = trial
        else:
            out.append(current)
            current = word
    if current:
        out.append(current)
    return out


def centred(pen, cx, y, text, fnt, fill, stroke=0):
    tw = measure(pen, text, fnt, stroke)
    pen.text((cx - tw / 2, y), text, font=fnt, fill=fill, stroke_width=stroke,
             stroke_fill=fill)


def burst(pen, cx, cy, r_out, r_in, points, fill):
    """A simple spiky burst polygon (explosion / sun)."""
    corners = []
    for i in range(points * 2):
        r = r_out if i % 2 == 0 else r_in
        a = math.pi * i / points - math.pi / 2
        corners.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    pen.polygon(corners, fill=fill)


# ---- illustrations (all original, drawn from zero) -----------------------

def paint_gaza_skyline(pen, x0, y0, x1, y1):
    """Gaza City: dusk skyline with an explosion burst over the rooftops."""
    pen.rectangle([x0, y0, x1, y1], fill=DUSK)
    # small stars in the dusk sky
    for sx, sy in [(x0 + 30, y0 + 18), (x0 + 90, y0 + 10), (x0 + 150, y0 + 24),
                   (x1 - 90, y0 + 12), (x1 - 40, y0 + 26), (x0 + 210, y0 + 14)]:
        pen.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=CARD)
    # explosion burst above the skyline, centre-left
    bx, by = (x0 + x1) // 2 - 40, y0 + 62
    burst(pen, bx, by, 44, 20, 10, ORANGE)
    burst(pen, bx, by, 28, 12, 10, YELLOW)
    burst(pen, bx, by, 14, 6, 8, CARD)
    # smoke curls rising from the burst
    for sx, sy, sr in [(bx - 30, by - 34, 12), (bx + 8, by - 44, 15),
                       (bx + 38, by - 30, 10)]:
        pen.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=SMOKE)
    # city skyline silhouettes along the bottom
    base = y1
    heights = [58, 84, 48, 96, 66, 78, 44, 88, 60, 72]
    bw = (x1 - x0) // len(heights)
    for i, hh in enumerate(heights):
        bx0 = x0 + i * bw
        pen.rectangle([bx0 + 2, base - hh, bx0 + bw - 2, base], fill=INK)
        # a lit window or two in each block
        pen.rectangle([bx0 + 8, base - hh + 10, bx0 + 16, base - hh + 18],
                      fill=YELLOW)
    # red banner carrying the strike label
    pen.rectangle([x0, y1 - 30, x1, y1], fill=RED)
    centred(pen, (x0 + x1) // 2, y1 - 26, "GAZA CITY", typeface(17), CARD,
            stroke=1)


def paint_space_shield(pen, x0, y0, x1, y1):
    """NATO space defence: a satellite above the Earth, guarded by a shield."""
    pen.rectangle([x0, y0, x1, y1], fill=(12, 18, 38))  # deep space
    for sx, sy in [(x0 + 24, y0 + 20), (x0 + 70, y0 + 44), (x0 + 130, y0 + 16),
                   (x1 - 70, y0 + 30), (x1 - 30, y0 + 60), (x0 + 180, y0 + 52)]:
        pen.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=CARD)
    # Earth dome peeking above the panel's bottom edge: only the cap of
    # the circle that lies inside the panel is drawn, so nothing spills
    # onto the card text below.
    ex, ey, er = (x0 + x1) // 2, y1 + 150, 190
    cap = []
    for deg in range(232, 309, 2):
        a = math.radians(deg)
        cap.append((ex + er * math.cos(a), ey + er * math.sin(a)))
    cap.append((cap[-1][0], y1))
    cap.append((cap[0][0], y1))
    pen.polygon(cap, fill=SEA)
    pen.arc([ex - er, ey - er, ex + er, ey + er], 232, 308, fill=TEAL, width=4)
    # satellite with solar panels, upper centre
    sx, sy = (x0 + x1) // 2 + 60, y0 + 62
    pen.rectangle([sx - 66, sy - 10, sx - 16, sy + 10], fill=NAVY,
                  outline=CARD, width=1)   # left panel
    pen.rectangle([sx + 16, sy - 10, sx + 66, sy + 10], fill=NAVY,
                  outline=CARD, width=1)   # right panel
    pen.rectangle([sx - 16, sy - 16, sx + 16, sy + 16], fill=GOLD,
                  outline=CARD, width=1)   # body
    pen.line([(sx, sy + 16), (sx, sy + 34)], fill=CARD, width=2)  # antenna
    pen.ellipse([sx - 3, sy + 34, sx + 3, sy + 40], fill=RED)
    # dotted orbit path
    for t in range(0, 13):
        a = math.pi * (0.15 + 0.07 * t)
        ox = (x0 + x1) // 2 + 150 * math.cos(a)
        oy = y0 + 118 - 62 * math.sin(a)
        pen.ellipse([ox - 2, oy - 2, ox + 2, oy + 2], fill=CARD)
    # shield guarding the lower left
    hx, hy = x0 + 74, y1 - 58
    pen.polygon([(hx, hy - 34), (hx + 30, hy - 24), (hx + 30, hy + 4),
                 (hx, hy + 30), (hx - 30, hy + 4), (hx - 30, hy - 24)],
                fill=TEAL, outline=CARD, width=2)
    centred(pen, hx, hy - 12, "NATO", typeface(15), CARD, stroke=1)


def paint_rocket_launch(pen, x0, y0, x1, y1):
    """Shenzhou-24: a rocket climbs past the stars toward a ringed station."""
    pen.rectangle([x0, y0, x1, y1], fill=(10, 16, 40))  # night sky
    for sx, sy in [(x0 + 26, y0 + 18), (x0 + 90, y0 + 40), (x0 + 150, y0 + 12),
                   (x1 - 60, y0 + 22), (x1 - 120, y0 + 46), (x0 + 210, y0 + 34)]:
        pen.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=CARD)
    # ringed station, upper right
    sx, sy = x1 - 78, y0 + 44
    pen.ellipse([sx - 56, sy - 8, sx + 56, sy + 8], outline=CARD, width=2)
    pen.rectangle([sx - 26, sy - 10, sx + 26, sy + 10], fill=CARD,
                  outline=INK, width=1)
    pen.rectangle([sx - 44, sy - 6, sx - 26, sy + 6], fill=TEAL)
    pen.rectangle([sx + 26, sy - 6, sx + 44, sy + 6], fill=TEAL)
    centred(pen, sx, y0 + 66, "TIANGONG", typeface(14), CARD, stroke=1)
    # rocket body, centre, nose up
    rx, ry = (x0 + x1) // 2 - 30, y0 + 66
    pen.polygon([(rx, ry - 34), (rx - 12, ry - 6), (rx + 12, ry - 6)],
                fill=RED)                       # nose cone
    pen.rectangle([rx - 12, ry - 6, rx + 12, ry + 34], fill=CARD,
                  outline=INK, width=1)         # body
    pen.rectangle([rx - 12, ry + 8, rx + 12, ry + 20], fill=GREEN)  # band
    pen.polygon([(rx - 12, ry + 34), (rx - 26, ry + 48), (rx - 12, ry + 40)],
                fill=RED)                       # left fin
    pen.polygon([(rx + 12, ry + 34), (rx + 26, ry + 48), (rx + 12, ry + 40)],
                fill=RED)                       # right fin
    # flame and smoke trail below the rocket
    burst(pen, rx, ry + 56, 18, 8, 8, ORANGE)
    burst(pen, rx, ry + 56, 10, 4, 8, YELLOW)
    for wx in range(x0 + 30, x1 - 20, 40):
        pen.arc([wx, y1 - 34, wx + 30, y1 - 14], 200, 340, fill=SMOKE, width=3)
    centred(pen, (x0 + x1) // 2, y1 - 24, "SHENZHOU-24", typeface(17), CARD,
            stroke=1)


def paint_market_slump(pen, x0, y0, x1, y1):
    """AI slump: a chip under a falling red chart line, -6% in a banner."""
    pen.rectangle([x0, y0, x1, y1], fill=(238, 240, 242))
    # falling chart line across the panel
    pts = [(x0 + 14, y0 + 30), (x0 + 110, y0 + 44), (x0 + 190, y0 + 38),
           (x0 + 280, y0 + 78), (x0 + 360, y0 + 66), (x1 - 14, y0 + 118)]
    pen.line(pts, fill=RED, width=5, joint="curve")
    # red down arrow at the end of the line
    ax, ay = x1 - 20, y0 + 118
    pen.polygon([(ax, ay + 22), (ax - 14, ay + 2), (ax - 5, ay + 2),
                 (ax - 5, ay - 14), (ax + 5, ay - 14), (ax + 5, ay + 2),
                 (ax + 14, ay + 2)], fill=RED)
    # chip, lower centre
    cx, cy = (x0 + x1) // 2, y0 + 118
    pen.rectangle([cx - 52, cy - 30, cx + 52, cy + 30], fill=INK,
                  outline=GOLD, width=3)
    for i in range(4):
        px = cx - 36 + i * 24
        pen.rectangle([px, cy - 40, px + 10, cy - 30], fill=INK)
        pen.rectangle([px, cy + 30, px + 10, cy + 40], fill=INK)
    centred(pen, cx, cy - 12, "AI", typeface(26), GOLD, stroke=1)
    # -6% banner
    pen.rectangle([x0, y1 - 34, x1, y1], fill=RED)
    centred(pen, (x0 + x1) // 2, y1 - 28, "NVIDIA -6%  ·  NASDAQ -1.5%",
            typeface(18), CARD, stroke=1)


ARTWORK = [paint_gaza_skyline, paint_space_shield, paint_rocket_launch,
           paint_market_slump]

ITEMS = [
    {
        "num": "1", "color": RED, "tag": "CONFLICT  |  GAZA CITY",
        "headline": "ISRAELI STRIKE KILLS HAMAS SECURITY CHIEF",
        "sub": "Naeem Abu Nahel, head of Hamas internal security, is "
               "killed in an Israeli airstrike on Gaza City.",
        "art": 0,
    },
    {
        "num": "2", "color": TEAL, "tag": "DEFENCE  |  NATO",
        "headline": "NATO VOWS TO DEFEND SPACE",
        "sub": "The alliance pledges to defend space as reports say "
               "Russia is preparing a nuclear-armed satellite.",
        "art": 1,
    },
    {
        "num": "3", "color": SEA, "tag": "SPACE  |  CHINA",
        "headline": "PAKISTAN'S FIRST ASTRONAUT BLASTS OFF",
        "sub": "Pakistan's first astronaut launches aboard China's "
               "Shenzhou-24 to the Tiangong space station.",
        "art": 2,
    },
    {
        "num": "4", "color": NAVY, "tag": "MARKETS  |  UNITED STATES",
        "headline": "AI STOCKS SLUMP AS TARIFF FEARS HIT",
        "sub": "Nvidia falls about 6% and the Nasdaq drops 1.5% after "
               "reports of a new US tariff plan.",
        "art": 3,
    },
]


def paint_story(pen, story, x0, y0, w, h):
    color = story["color"]
    pen.rectangle([x0, y0, x0 + w, y0 + h], fill=CARD, outline=INK, width=2)
    pen.rectangle([x0, y0, x0 + w, y0 + 8], fill=color)
    # illustration panel
    px0, py0, px1, py1 = x0 + 12, y0 + 20, x0 + w - 12, y0 + 188
    pen.rectangle([px0, py0, px1, py1], outline=(190, 192, 196), width=1)
    ARTWORK[story["art"]](pen, px0, py0, px1, py1)
    # story number badge
    bx, by = px0 + 16, py0 + 16
    pen.ellipse([bx, by, bx + 30, by + 30], fill=color, outline=CARD, width=2)
    centred(pen, bx + 15, by + 4, story["num"], typeface(18), CARD, stroke=1)
    # tag
    pen.text((x0 + 16, y0 + 200), story["tag"], font=typeface(17), fill=color,
             stroke_width=1, stroke_fill=color)
    # headline (up to 2 lines)
    hl = wrap_lines(pen, story["headline"], typeface(29), w - 32, stroke=1)
    y = y0 + 226
    for line in hl[:2]:
        pen.text((x0 + 16, y), line, font=typeface(29), fill=INK,
                 stroke_width=1, stroke_fill=INK)
        y += 36
    # subtext (up to 3 lines)
    sub = wrap_lines(pen, story["sub"], typeface(19), w - 32)
    y = y0 + 226 + 36 * len(hl[:2]) + 6
    for line in sub[:3]:
        pen.text((x0 + 16, y), line, font=typeface(19), fill=GREY)
        y += 25


def main():
    sheet = Image.new("RGB", (SIZE, SIZE), PAPER)
    pen = ImageDraw.Draw(sheet)

    # outer double border
    pen.rectangle([10, 10, SIZE - 11, SIZE - 11], outline=INK, width=3)
    pen.rectangle([18, 18, SIZE - 19, SIZE - 19], outline=INK, width=1)

    # masthead: the day, named loud and clear
    centred(pen, SIZE // 2, 34, "THE WORLD IN ONE DAY", typeface(26), INK, stroke=1)
    centred(pen, SIZE // 2, 68, "WEDNESDAY, 25 NOVEMBER 2026", typeface(46), RED, stroke=2)
    pen.line([(60, 128), (SIZE - 60, 128)], fill=INK, width=2)
    pen.line([(60, 134), (SIZE - 60, 134)], fill=INK, width=1)
    centred(pen, SIZE // 2, 142, "Four stories that defined the day",
            typeface(20), GREY)

    # 2 x 2 grid of stories
    cw, ch, gap = 476, 384, 16
    x0, y0 = 28, 172
    for i, story in enumerate(ITEMS):
        cx = x0 + (i % 2) * (cw + gap)
        cy = y0 + (i // 2) * (ch + gap)
        paint_story(pen, story, cx, cy, cw, ch)

    # footer repeats the date so the day is unmistakable
    centred(pen, SIZE // 2, 968, "News of Wednesday, 25 November 2026",
            typeface(18), GREY, stroke=1)

    target_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(target_dir, exist_ok=True)
    sheet.save(os.path.join(target_dir, "entry.png"), format="PNG")


if __name__ == "__main__":
    main()
