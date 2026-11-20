# -*- coding: utf-8 -*-
"""Ratos normais (fuga) extraídos de tools/src/rats_sheet.png -> assets/sprites/nrat_*"""
import os, sys
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r31_from_sheet import frames_of
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "assets", "sprites")
PAN = [("nrat_run", 1040, 1512, 145, 240, 4, 0.40), ("nrat_back", 1040, 1512, 300, 408, 4, 0.36),
       ("nrat_idle", 1040, 1512, 478, 592, 4, 0.40)]
img = Image.open(os.path.join(HERE, "src", "rats_sheet.png"))
for name, x0, x1, y0, y1, n, k in PAN:
    fr = frames_of(img, x0, x1, y0, y1, n)
    print(name, len(fr), [f.size for f in fr])
    for i, f in enumerate(fr):
        s = f.resize((max(1, round(f.width * k)), max(1, round(f.height * k))), Image.LANCZOS)
        s.putalpha(s.split()[3].point(lambda v: 255 if v > 110 else 0))
        c = Image.new("RGBA", (40, 32), (0, 0, 0, 0))
        c.alpha_composite(s, (20 - s.width // 2, 31 - s.height))
        c.save(os.path.join(OUT, f"{name}_{i}.png"))
