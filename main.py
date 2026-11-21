#!/usr/bin/env python3
"""VELARIS — where the sun sets through stone.

A travel poster for a place that does not exist: an island in the Arch
Islands whose one landmark is the Great Arch, a natural stone arch over
the lagoon. Every evening the sun drops exactly through the arch and
lights the calm turquoise water gold.

Drawn procedurally with Pillow only (stdlib + PIL), fully deterministic:
two runs produce identical bytes. Writes /output/entry.png, 1024x1024.
"""

import math
import os
import random
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1024, 1024
OUT = "/output/entry.png"

SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# Palette — dusk over a turquoise lagoon.
SKY_TOP = (38, 32, 78)        # deep indigo
SKY_MID = (108, 58, 110)      # violet dusk
SKY_LOW = (214, 104, 58)      # burnt orange
SKY_HORIZON = (242, 165, 65)  # gold at the horizon
SEA_TOP = (46, 127, 143)      # turquoise
SEA_DEEP = (24, 84, 102)      # deep teal
ARCH = (51, 38, 63)           # dark plum stone
ARCH_SHADOW = (38, 27, 48)
GOLD = (238, 176, 84)
CREAM = (247, 234, 208)
SUN = (252, 222, 138)
HOUSE = (244, 238, 222)
ROOF = (176, 84, 52)
WINDOW = (255, 196, 96)

HORIZON = 620
SUN_C = (512, 548)
SUN_R = 62


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def vgrad(img, y0, y1, stops):
    """Fill rows y0..y1 with a vertical gradient through `stops`.

    stops: list of (fraction 0..1, colour). Deterministic, no numpy.
    """
    d = ImageDraw.Draw(img)
    span = max(1, y1 - y0)
    for y in range(y0, y1):
        t = (y - y0) / span
        for i in range(len(stops) - 1):
            f0, c0 = stops[i]
            f1, c1 = stops[i + 1]
            if f0 <= t <= f1:
                lt = 0.0 if f1 == f0 else (t - f0) / (f1 - f0)
                d.line([(0, y), (W, y)], fill=lerp(c0, c1, lt))
                break
        else:
            d.line([(0, y), (W, y)], fill=stops[-1][1])


def tracked(draw, cx, y, text, font, fill, tracking=0, shadow=None):
    """Draw `text` centred on cx with letter tracking; return its width."""
    widths = [draw.textlength(ch, font=font) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = cx - total / 2
    for ch, w in zip(text, widths):
        if shadow is not None:
            draw.text((x + shadow[0], y + shadow[1]), ch, font=font, fill=shadow[2])
        draw.text((x, y), ch, font=font, fill=fill)
        x += w + tracking
    return total


def glow_disc(base, cx, cy, radius, colour, alpha=110):
    """Soft radial glow: translucent concentric discs, blurred."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    steps = 14
    for i in range(steps, 0, -1):
        r = radius * i / steps
        a = int(alpha * (1 - i / steps) ** 2)
        ld.ellipse([cx - r, cy - r, cx + r, cy + r], fill=colour + (a,))
    layer = layer.filter(ImageFilter.GaussianBlur(radius / 6))
    base.alpha_composite(layer)


def main():
    rng = random.Random(7)
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)

    # --- Sky: indigo dusk down to a gold horizon.
    vgrad(img, 0, HORIZON, [
        (0.00, SKY_TOP), (0.38, SKY_MID), (0.72, SKY_LOW), (1.00, SKY_HORIZON),
    ])
    # --- Sea: turquoise down to deep teal.
    vgrad(img, HORIZON, H, [(0.00, SEA_TOP), (1.00, SEA_DEEP)])

    # --- Stars in the upper sky, fading out toward the horizon.
    for _ in range(110):
        x = rng.uniform(0, W)
        y = rng.uniform(0, 300)
        r = rng.uniform(0.6, 1.8)
        fade = 1 - y / 340
        if rng.random() < fade:
            a = int(140 * fade * rng.uniform(0.5, 1.0))
            d.ellipse([x - r, y - r, x + r, y + r],
                      fill=(255, 244, 220) if a > 90 else (200, 190, 220))

    # --- Sun glow + disc, low in the arch opening.
    img = img.convert("RGBA")
    glow_disc(img, SUN_C[0], SUN_C[1], 190, (250, 170, 80), 120)
    img = img.convert("RGB")
    d = ImageDraw.Draw(img)
    d.ellipse([SUN_C[0] - SUN_R, SUN_C[1] - SUN_R,
               SUN_C[0] + SUN_R, SUN_C[1] + SUN_R], fill=SUN)
    d.ellipse([SUN_C[0] - SUN_R + 7, SUN_C[1] - SUN_R + 7,
               SUN_C[0] + SUN_R - 7, SUN_C[1] + SUN_R - 7], fill=(253, 232, 160))

    # --- Sun path on the water: widening golden dashes toward the viewer.
    # Ends above the tagline so no dash ever crosses the type.
    for i, y in enumerate(range(HORIZON + 26, 820, 26)):
        t = (y - HORIZON) / 280
        half = 26 + t * 150
        alpha = max(0, 150 - int(t * 130))
        col = (250, 190, 100)
        d.line([(SUN_C[0] - half, y), (SUN_C[0] + half, y)],
               fill=col, width=3 if i % 2 == 0 else 2)
        d.line([(SUN_C[0] - half * 0.55, y + 9), (SUN_C[0] + half * 0.55, y + 9)],
               fill=(255, 214, 140), width=2)

    # --- Pale wave lines across the lagoon. They stay above the tagline
    # band (y 840..945) and below it, never crossing the type.
    for _ in range(38):
        x = rng.uniform(20, W - 20)
        y = rng.uniform(HORIZON + 14, 828)
        ln = rng.uniform(24, 90)
        tone = rng.choice([(120, 190, 200), (170, 215, 220), (90, 160, 175)])
        d.line([(x, y), (x + ln, y)], fill=tone, width=2)
    for _ in range(8):
        x = rng.uniform(20, W - 20)
        y = rng.uniform(958, 992)
        ln = rng.uniform(24, 80)
        tone = rng.choice([(120, 190, 200), (170, 215, 220)])
        d.line([(x, y), (x + ln, y)], fill=tone, width=2)

    # --- Birds crossing the dusk sky, clear of the title.
    for bx, by, bs in [(330, 330, 9), (372, 306, 7), (700, 322, 8),
                       (742, 296, 6), (650, 352, 7)]:
        d.arc([bx - bs, by - bs // 2, bx, by + bs // 2], 200, 340,
              fill=(40, 30, 52), width=2)
        d.arc([bx, by - bs // 2, bx + bs, by + bs // 2], 200, 340,
              fill=(40, 30, 52), width=2)

    # --- The Great Arch: two pillars and a curved crown, framing the sun.
    # Paint the stone through a mask with a hole, so the sky, sea and sun
    # already drawn show through the opening untouched (no flat fills).
    arch_mask = Image.new("L", (W, H), 0)
    ad = ImageDraw.Draw(arch_mask)
    ad.polygon([(128, 850), (128, 430), (896, 430), (896, 850)], fill=255)
    ad.pieslice([128, 180, 896, 700], 180, 360, fill=255)
    ad.polygon([(268, 850), (268, 470), (756, 470), (756, 850)], fill=0)
    ad.pieslice([268, 250, 756, 690], 180, 360, fill=0)
    stone = Image.new("RGB", (W, H), ARCH)
    img.paste(stone, (0, 0), arch_mask)
    d = ImageDraw.Draw(img)
    # Gold rim light along the crown's outer edge.
    d.arc([128, 180, 896, 700], 195, 345, fill=GOLD, width=7)
    # Warm light on the inner edges of the pillars.
    d.line([(268, 470), (268, 850)], fill=(214, 140, 80), width=5)
    d.line([(756, 470), (756, 850)], fill=(214, 140, 80), width=5)
    # Stone banding on the crown.
    d.arc([168, 220, 856, 660], 190, 350, fill=ARCH_SHADOW, width=4)
    d.arc([208, 260, 816, 620], 195, 345, fill=ARCH_SHADOW, width=3)

    # --- Headlands left and right, each with whitewashed houses.
    for side in (-1, 1):
        base_x = 0 if side < 0 else W
        d.polygon([(base_x, HORIZON - 22), (base_x + side * 250, HORIZON - 22),
                   (base_x + side * 210, HORIZON + 42), (base_x, HORIZON + 42)],
                  fill=(40, 30, 52))
        houses = [(36, 0), (86, -14), (140, -4), (186, 8)] if side < 0 else \
                 [(W - 66, 0), (W - 116, -14), (W - 170, -4), (W - 216, 8)]
        for hx, dy in houses:
            hy = HORIZON - 22 + dy
            d.rectangle([hx, hy - 34, hx + 44, hy], fill=HOUSE)
            d.polygon([(hx - 3, hy - 34), (hx + 22, hy - 52), (hx + 47, hy - 34)],
                      fill=ROOF)
            d.rectangle([hx + 8, hy - 20, hx + 16, hy - 8], fill=WINDOW)
            d.rectangle([hx + 28, hy - 20, hx + 36, hy - 8], fill=WINDOW)
        # A lit window or two on the headland face itself.
        for off, dy in ((46, 8), (96, 14)):
            x0 = base_x + side * off
            x1 = base_x + side * (off + 12)
            d.rectangle([min(x0, x1), HORIZON + dy, max(x0, x1), HORIZON + dy + 12],
                        fill=WINDOW)

    # --- Sailboats drifting on the lagoon.
    def boat(cx, cy, s, sail=(247, 240, 222)):
        d.polygon([(cx - 26 * s, cy), (cx + 26 * s, cy), (cx + 18 * s, cy + 10 * s),
                   (cx - 18 * s, cy + 10 * s)], fill=(52, 44, 62))
        d.polygon([(cx, cy - 44 * s), (cx, cy), (cx + 26 * s, cy)], fill=sail)
        d.polygon([(cx - 2 * s, cy - 34 * s), (cx - 2 * s, cy),
                   (cx - 20 * s, cy)], fill=(232, 220, 198))
        d.line([(cx, cy - 46 * s), (cx, cy)], fill=(60, 50, 66), width=2)

    boat(392, 700, 0.9)
    boat(662, 768, 1.05)
    boat(850, 690, 0.75, sail=(250, 226, 170))

    # --- Low rocks in the bottom corners, kept below the tagline.
    d.polygon([(0, H), (0, 968), (150, 936), (210, H)], fill=(40, 30, 52))
    d.polygon([(W, H), (W, 968), (874, 936), (814, H)], fill=(40, 30, 52))

    # --- Type: the place name, big and legible, carrying the mood.
    title_font = ImageFont.truetype(SERIF_BOLD, 148)
    tracked(d, W // 2, 92, "VELARIS", title_font, CREAM, tracking=26,
            shadow=(6, 7, (30, 20, 44)))
    # Gold rule + diamond under the name.
    d.line([(312, 268), (712, 268)], fill=GOLD, width=4)
    d.polygon([(512, 256), (526, 270), (512, 284), (498, 270)], fill=GOLD)

    tag_font = ImageFont.truetype(SANS_BOLD, 34)
    tracked(d, W // 2, 856, "WHERE THE SUN SETS THROUGH STONE",
            tag_font, CREAM, tracking=7, shadow=(2, 3, (20, 40, 52)))
    sub_font = ImageFont.truetype(SANS_BOLD, 28)
    tracked(d, W // 2, 908, "· THE ARCH ISLANDS ·",
            sub_font, GOLD, tracking=10)

    os.makedirs("/output", exist_ok=True)
    img.save(OUT, format="PNG", optimize=True)
    print(f"wrote {OUT}: {W}x{H}, {os.path.getsize(OUT)} bytes")


if __name__ == "__main__":
    main()
