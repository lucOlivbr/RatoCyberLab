# -*- coding: utf-8 -*-
"""Extrai os frames do R-31 (andando/correndo nas 4 direções) de tools/src/r31_sheet.png."""
import os
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "assets", "sprites")
SRC = os.path.join(HERE, "src", "r31_sheet.png")
KD = {'f': 0.46, 'b': 0.38, 'r': 0.44, 'l': 0.44}
CW, CH = 72, 56
# nome, x0, x1, y0, y1, n frames
PANELS = [
    ("run_f", 25, 780, 455, 592, 6), ("walk_f", 800, 1285, 455, 592, 5),
    ("run_b", 25, 780, 645, 792, 6), ("walk_b", 800, 1285, 645, 792, 5),
    ("run_r", 25, 780, 850, 975, 5), ("walk_r", 800, 1285, 850, 975, 4),
    ("run_l", 25, 780, 1025, 1150, 5), ("walk_l", 800, 1285, 1025, 1150, 4),
]


def cut(a, bgc):
    diff = np.abs(a.astype(int) - bgc).max(axis=2)
    r, g, b = [a[..., i].astype(int) for i in range(3)]
    line = (b - r > 22) & (b - g > 6) & (b > 45) & (r < 90)
    bg_like = (diff < 16) | line
    lab, n = ndi.label(bg_like)
    edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    bg = np.isin(lab, list(edge))
    return ~bg


def frames_of(img, x0, x1, y0, y1, n, minarea=500):
    a = np.array(img.convert("RGB"))[y0:y1, x0:x1]
    bgc = np.median(a.reshape(-1, 3), axis=0)
    fg = cut(a, bgc)
    fg = ndi.binary_opening(fg, structure=np.ones((2, 1)))   # tira fios finos
    lab, k = ndi.label(ndi.binary_dilation(fg, iterations=5))
    lab = lab * fg
    ids = [i for i in range(1, k + 1) if (lab == i).sum() > 0]
    area = {i: int((lab == i).sum()) for i in ids}
    big = [i for i in ids if area[i] > minarea]
    big = sorted(big, key=lambda i: np.where(lab == i)[1].mean())
    if len(big) != n:
        print("  AVISO: %d componentes grandes (esperado %d)" % (len(big), n))
    groups = {i: [i] for i in big}
    cx = {i: np.where(lab == i)[1].mean() for i in big}
    for i in ids:
        if i in big or area[i] < 40:
            continue
        c = np.where(lab == i)[1].mean()
        j = min(big, key=lambda t: abs(cx[t] - c))
        groups[j].append(i)
    outs = []
    for j in big:
        m = np.isin(lab, groups[j])
        m = ndi.binary_fill_holes(m)
        rgba = np.zeros(a.shape[:2] + (4,), np.uint8)
        rgba[..., :3] = a; rgba[..., 3] = m * 255
        im = Image.fromarray(rgba, "RGBA")
        outs.append(im.crop(im.getbbox()))
    return outs


def main():
    img = Image.open(SRC)
    os.makedirs(OUT, exist_ok=True)
    for name, x0, x1, y0, y1, n in PANELS:
        name = name.replace("_f", "_f")
        fr = frames_of(img, x0, x1, y0, y1, n)
        print(name, len(fr), n, [f.size for f in fr])
        for i, f in enumerate(fr):
            s = f.resize((max(1, round(f.width * KD[name[-1]])), max(1, round(f.height * KD[name[-1]]))), Image.LANCZOS)
            s.putalpha(s.split()[3].point(lambda v: 255 if v > 110 else 0))
            c = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
            c.alpha_composite(s, (CW // 2 - s.width // 2, CH - 1 - s.height))
            c.save(os.path.join(OUT, f"r31_{name}_{i}.png"))


if __name__ == "__main__":
    main()
