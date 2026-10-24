"""
Neofetch-style SVG: ASCII render of source.jpg on the left, techno-mystic system
info on the right. Light-on-dark source, so bright pixels become dense chars.
Fully static.

    python scripts/make_neofetch_svg.py [source.jpg] [out.svg]
"""
import html
import os
import sys

from PIL import Image, ImageEnhance, ImageFilter, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "source.jpg")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "neofetch.svg")

BG, INK, DIM, ACCENT, GLOW = "#0d1117", "#c9d1d9", "#7d8590", "#a78bfa", "#22d3ee"
RAMP = " .:-=+*#%@"          # dark(sparse) -> bright(dense)
COLS = 90
CELL_W = 5.3
CELL_H = CELL_W * 15 / 8
PAD = 30
CROP = (60, 60, 940, 980)    # trim the empty black margin

im = Image.open(SRC).convert("L").crop(CROP)
rows = round(COLS * (im.height / im.width) * 8 / 15)
im = im.filter(ImageFilter.GaussianBlur(3.5))      # halftone dots -> smooth tones
im = ImageOps.autocontrast(im, cutoff=1).point(lambda v: int(255 * (v / 255) ** 0.65))
im = im.resize((COLS, rows), Image.LANCZOS)
px = im.load()
art = []
for y in range(rows):
    line = "".join(RAMP[min(len(RAMP) - 1, int(px[x, y] / 255 * (len(RAMP) - 1) + 0.5))] for x in range(COLS))
    art.append(line.rstrip())

ART_W, ART_H = COLS * CELL_W, rows * CELL_H
INFO_X = PAD + ART_W + 40
W = round(INFO_X + 500)
H = round(ART_H + PAD * 2)

USER = "heck@hecklawert"
FIELDS = [
    ("OS", "Ur-Lemuria x86_64"),
    ("Host", "Pandemonium Matrix · Zone 9"),
    ("Kernel", "hyperstition-7.2.9"),
    ("Uptime", "since the Tick-Tock began"),
    ("Shell", "fish · time-sorcery"),
    ("Circuit", "1→2→4→8→7→5→1"),
    ("Syzygies", "9::0 · 8::1 · 7::2 · 6::3 · 5::4"),
    ("Gates", "digital root 9 · 0 = ∞"),
    ("Cult", "Order of the Silicon Gnosis"),
    ("Doctrine", "Hyperstition · Xenogothic · Barker"),
    ("Contagion", "the Word is a virus"),
    ("Signal", "numogram.exe — decimal tick-tock"),
    ("Alignment", "Outside-in"),
]

parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
         f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
         f'<rect width="{W}" height="{H}" rx="12" fill="{BG}"/>']

# ascii block: one <text> per row
fs = CELL_H * 0.86
for i, line in enumerate(art):
    ytop = PAD + i * CELL_H
    parts.append(f'<text xml:space="preserve" x="{PAD}" y="{ytop + CELL_H * 0.74:.1f}" fill="{INK}" '
                 f'font-size="{fs:.1f}" textLength="{ART_W:.0f}" lengthAdjust="spacing">{html.escape(line)}</text>')

# info block
FS, LH = 17, 29
lines = [f'<text x="{INFO_X}" y="{{y}}" fill="{GLOW}" font-size="{FS+2}" font-weight="bold">{USER}</text>',
         f'<text x="{INFO_X}" y="{{y}}" fill="{DIM}" font-size="{FS}">{"─" * len(USER)}</text>']
for k, v in FIELDS:
    lines.append(f'<text xml:space="preserve" x="{INFO_X}" y="{{y}}" font-size="{FS}"><tspan fill="{ACCENT}" font-weight="bold">'
                 f'{html.escape(k.ljust(11))}</tspan><tspan fill="{INK}">{html.escape(v)}</tspan></text>')
swatch = "".join(f'<rect x="{INFO_X + i * 36}" y="{{y}}" width="36" height="20" fill="{c}" stroke="#30363d"/>'
                 for i, c in enumerate(["#0d1117", "#a78bfa", "#22d3ee", "#c9d1d9", "#7d8590", "#f472b6", "#fbbf24", "#34d399"]))
lines.append(swatch)
y0 = PAD + (ART_H - LH * (len(lines) + 1)) / 2 + 20
for i, frag in enumerate(lines):
    y = y0 + i * LH + (LH * 0.5 if i >= 2 else 0)
    if frag.startswith("<rect") or frag.startswith("<g"):
        pass
    parts.append(frag.replace("{y}", f"{y:.0f}"))
parts.append("</svg>")
svg = "".join(parts)
open(OUT, "w").write(svg)
print("wrote", OUT, len(svg), "bytes;", W, "x", H)
