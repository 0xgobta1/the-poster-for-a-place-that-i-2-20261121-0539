# VELARIS — where the sun sets through stone.
# A travel poster for a place that does not exist, rendered procedurally.
# makefun anchor: the-poster-for-a-place-that-i-2-20261121-0539 — VELARIS, where
# the sun sets through stone, fresh from-scratch build for @sunny-sparrow-40.
#
# The place: VELARIS, an island in the Arch Islands. Its one landmark is the
# Great Arch — a natural stone arch over the lagoon — and every evening at
# dusk the sun drops exactly through the arch, lighting the calm turquoise
# water gold. One landmark, one weather/light promise: warm dusk, still sea.
# No network, fully deterministic, stdlib + Pillow only.

import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

print("makefun anchor: the-poster-for-a-place-that-i-2-20261121-0539 — VELARIS")

S = 2                      # supersample factor; final image is 1024x1024
W = H = 1024 * S
OUT = "/output/entry.png"

SERIF_BLACK = "/usr/share/fonts/truetype/noto/NotoSerifDisplay-Black.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/noto/NotoSansDisplay-Bold.ttf"

CREAM = (255, 242, 208)
GOLD = (232, 169, 79)
AMBER = (246, 178, 94)
SUN_CORE = (255, 217, 138)
ARCH = (58, 42, 63)            # dark plum-brown stone silhouette
ARCH_RIM = (242, 166, 90)
CLIFF = (36, 26, 46)
HOUSE = (247, 234, 208)
WINDOW = (255, 180, 94)

rng = random.Random(20261121)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def vgrad(draw, x0, y0, x1, y1, top, bottom):
    """Vertical gradient band, drawn row by row (deterministic)."""
    h = y1 - y0
    for y in range(y0, y1):
        t = (y - y0) / max(h - 1, 1)
        draw.line([(x0, y), (x1, y)], fill=lerp(top, bottom, t))


def letterspaced(draw, cx, y, text, font, fill, tracking):
    """Draw text centred on cx, with fixed extra tracking between glyphs."""
    widths = [draw.textlength(ch, font=font) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = cx - total / 2
    for ch, w in zip(text, widths):
        draw.text((x, y), ch, font=font, fill=fill)
        x += w + tracking


def main():
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)

    # ---- sky: deep indigo dusk melting into warm amber at the horizon ----
    horizon = 620 * S
    vgrad(d, 0, 0, W, int(horizon * 0.55), (28, 34, 82), (140, 80, 105))
    vgrad(d, 0, int(horizon * 0.55), W, horizon, (140, 80, 105), (228, 145, 82))

    # ---- stars in the upper sky (fixed seed, deterministic) ----
    for _ in range(45):
        x = rng.randint(0, W)
        y = rng.randint(0, 260 * S)
        r = rng.choice([1, 1, 2]) * S // 2 + 1
        d.ellipse([x - r, y - r, x + r, y + r], fill=(235, 230, 250))

    # ---- soft warm clouds near the horizon ----
    cloud = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(cloud)
    for cx, cy, cw, chh, alpha in [
        (180, 520, 420, 26, 46), (820, 500, 380, 22, 40),
        (512, 560, 560, 20, 34), (120, 470, 260, 16, 30),
        (920, 545, 240, 18, 36),
    ]:
        cd.ellipse([cx * S - cw * S // 2, cy * S - chh * S // 2,
                    cx * S + cw * S // 2, cy * S + chh * S // 2],
                   fill=(255, 190, 130, alpha))
    cloud = cloud.filter(ImageFilter.GaussianBlur(14 * S))
    img.paste(Image.alpha_composite(img.convert("RGBA"), cloud).convert("RGB"),
              (0, 0))
    d = ImageDraw.Draw(img)

    # ---- sun: a smaller disc, low and sinking into the horizon ----
    sun_cx, sun_cy, sun_r = 512 * S, 556 * S, 58 * S
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for r, alpha in [(190, 20), (140, 30), (100, 48)]:
        gd.ellipse([sun_cx - r * S // 2, sun_cy - r * S // 2,
                    sun_cx + r * S // 2, sun_cy + r * S // 2],
                   fill=(255, 170, 80, alpha))
    glow = glow.filter(ImageFilter.GaussianBlur(10 * S))
    img.paste(Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB"),
              (0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([sun_cx - sun_r, sun_cy - sun_r, sun_cx + sun_r, sun_cy + sun_r],
              fill=SUN_CORE)
    d.ellipse([sun_cx - sun_r * 0.82, sun_cy - sun_r * 0.82,
               sun_cx + sun_r * 0.82, sun_cy + sun_r * 0.82],
              fill=(255, 228, 160))

    # ---- sea: teal gradient below the horizon ----
    vgrad(d, 0, horizon, W, H, (64, 140, 150), (22, 75, 100))

    # sun reflection: a few soft gold dashes, fading fast, never a ladder
    refl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rd = ImageDraw.Draw(refl)
    for i in range(12):
        y = horizon + 10 * S + i * 14 * S
        wdt = (110 - i * 7) * S
        jx = rng.randint(-14, 14) * S
        alpha = max(0, 210 - i * 18)
        rd.line([(sun_cx - wdt // 2 + jx, y), (sun_cx + wdt // 2 + jx, y)],
                fill=(255, 200, 130, alpha), width=3 * S)
    refl = refl.filter(ImageFilter.GaussianBlur(2 * S))
    img.paste(Image.alpha_composite(img.convert("RGBA"), refl).convert("RGB"),
              (0, 0))
    d = ImageDraw.Draw(img)

    # wave strokes across the sea
    for _ in range(40):
        y = rng.randint(horizon + 20 * S, H - 30 * S)
        if 1650 * S // 2 < y < 1830 * S // 2:
            continue  # keep the tagline band clean
        x = rng.randint(0, W - 120 * S)
        ln = rng.randint(30, 120) * S
        tone = rng.choice([(110, 180, 190), (40, 110, 130), (140, 200, 205)])
        d.line([(x, y), (x + ln, y)], fill=tone, width=max(1, S))

    # ---- the Great Arch: stone silhouette framing the sun ----
    # pillars
    d.polygon([(150 * S, 800 * S), (168 * S, 470 * S), (330 * S, 470 * S),
               (318 * S, 800 * S)], fill=ARCH)
    d.polygon([(874 * S, 800 * S), (856 * S, 470 * S), (694 * S, 470 * S),
               (706 * S, 800 * S)], fill=ARCH)
    # top ring of the arch (thick arc)
    d.arc([150 * S, 240 * S, 874 * S, 760 * S], start=180, end=360,
          fill=ARCH, width=130 * S)
    # warm rim light along the arch's outer top edge
    d.arc([158 * S, 248 * S, 866 * S, 752 * S], start=200, end=340,
          fill=ARCH_RIM, width=5 * S)
    # rim light on the inner edges of the pillars
    d.line([(330 * S, 480 * S), (322 * S, 620 * S)], fill=ARCH_RIM, width=4 * S)
    d.line([(694 * S, 480 * S), (702 * S, 620 * S)], fill=ARCH_RIM, width=4 * S)

    # ---- whitewashed town on the headlands, warm windows lit ----
    def house(x, y, w, h, roof=True):
        d.rectangle([x, y, x + w, y + h], fill=HOUSE)
        if roof:
            d.polygon([(x - 3 * S, y), (x + w // 2, y - 12 * S),
                       (x + w + 3 * S, y)], fill=(150, 70, 60))
        wx = x + w // 3
        wy = y + h // 3
        d.rectangle([wx, wy, wx + 6 * S, wy + 8 * S], fill=WINDOW)

    # left headland cluster
    d.polygon([(0, 640 * S), (0, 600 * S), (60 * S, 585 * S),
               (150 * S, 590 * S), (170 * S, 640 * S)], fill=CLIFF)
    house(28 * S, 560 * S, 34 * S, 30 * S)
    house(66 * S, 548 * S, 30 * S, 42 * S)
    house(100 * S, 566 * S, 36 * S, 26 * S)
    house(136 * S, 572 * S, 26 * S, 20 * S)
    # right headland cluster
    d.polygon([(W, 640 * S), (W, 600 * S), (964 * S, 585 * S),
               (874 * S, 590 * S), (854 * S, 640 * S)], fill=CLIFF)
    house(856 * S, 568 * S, 30 * S, 24 * S)
    house(890 * S, 552 * S, 34 * S, 40 * S)
    house(928 * S, 562 * S, 28 * S, 30 * S)
    house(958 * S, 572 * S, 30 * S, 22 * S)
    # tiny far-shore houses across the lagoon
    for fx in (60, 110, 880, 930, 965):
        d.rectangle([fx * S, 606 * S, fx * S + 14 * S, 620 * S], fill=HOUSE)
        d.rectangle([fx * S + 5 * S, 611 * S, fx * S + 9 * S, 615 * S],
                    fill=WINDOW)

    # ---- sailboats on the lagoon ----
    def boat(cx, cy, sc):
        hull = [(cx - 26 * sc, cy), (cx + 26 * sc, cy),
                (cx + 16 * sc, cy + 10 * sc), (cx - 16 * sc, cy + 10 * sc)]
        d.polygon([(x * S, y * S) for x, y in hull], fill=CLIFF)
        d.polygon([(cx * S, (cy - 34 * sc) * S), (cx * S, cy * S),
                   ((cx + 20 * sc) * S, cy * S)], fill=(255, 244, 220))
        d.polygon([(cx * S, (cy - 26 * sc) * S), (cx * S, cy * S),
                   ((cx - 14 * sc) * S, cy * S)], fill=(240, 200, 150))

    boat(420, 720, 1.0)
    boat(620, 800, 0.7)
    boat(925, 700, 0.8)

    # ---- gulls ----
    for gx, gy, gs in [(380, 300, 10), (420, 280, 8), (640, 310, 9),
                       (680, 285, 7)]:
        d.arc([(gx - gs) * S, (gy - gs // 2) * S, gx * S, (gy + gs // 2) * S],
              start=200, end=340, fill=(40, 30, 55), width=2 * S)
        d.arc([gx * S, (gy - gs // 2) * S, (gx + gs) * S, (gy + gs // 2) * S],
              start=200, end=340, fill=(40, 30, 55), width=2 * S)

    # ---- foreground cliffs framing the bottom corners ----
    d.polygon([(0, H), (0, 930 * S), (90 * S, 900 * S), (190 * S, 950 * S),
               (230 * S, H)], fill=CLIFF)
    d.polygon([(W, H), (W, 930 * S), (934 * S, 900 * S), (834 * S, 950 * S),
               (794 * S, H)], fill=CLIFF)

    # ---- type: the name carries the poster ----
    name_font = ImageFont.truetype(SERIF_BLACK, 148 * S)
    tag_font = ImageFont.truetype(SANS_BOLD, 34 * S)
    small_font = ImageFont.truetype(SANS_BOLD, 24 * S)

    # soft shadow then cream, so the name reads at thumbnail size
    letterspaced(d, 512 * S + 5 * S, 58 * S + 5 * S, "VELARIS", name_font,
                 (18, 12, 40), 22 * S)
    letterspaced(d, 512 * S, 58 * S, "VELARIS", name_font, CREAM, 22 * S)
    # gold rule with a diamond
    d.line([(312 * S, 222 * S), (712 * S, 222 * S)], fill=GOLD, width=3 * S)
    d.polygon([(512 * S, 212 * S), (522 * S, 222 * S), (512 * S, 232 * S),
               (502 * S, 222 * S)], fill=GOLD)

    # tagline + place line, bottom centre over the dark sea
    letterspaced(d, 512 * S, 838 * S, "WHERE THE SUN SETS THROUGH STONE",
                 tag_font, CREAM, 8 * S)
    letterspaced(d, 512 * S, 888 * S, "· THE ARCH ISLANDS ·",
                 small_font, GOLD, 6 * S)

    img = img.convert("RGB").resize((1024, 1024), Image.LANCZOS)
    os.makedirs("/output", exist_ok=True)
    img.save(OUT, "PNG", optimize=True)
    size = os.path.getsize(OUT)
    print(f"wrote {OUT} 1024x1024 PNG {size} bytes")
    assert size <= 1_048_576, "over the 1 MiB gate"


if __name__ == "__main__":
    main()
