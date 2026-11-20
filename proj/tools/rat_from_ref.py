# -*- coding: utf-8 -*-
"""Extrai os 4 frames da corrida de 4 patas (imagem de referência do usuário) e gera os sprites do jogo.
Uso: python3 tools/rat_from_ref.py   (lê tools/src/run_ref.png, escreve assets/sprites/rat_run_*.png)"""
import os
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "src", "run_ref.png")
OUT = os.path.join(HERE, "..", "assets", "sprites")
COLS = [(8, 425), (440, 870), (885, 1310), (1325, 1760)]
Y0, Y1 = 290, 546
SCALE = 0.20
CW, CH = 96, 56      # canvas final
NOSE_X, GROUND_Y = 88, 53


def keyed_frame(img, x0, x1):
    a = np.array(img.crop((x0, Y0, x1, Y1)).convert("RGB")).astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    border = np.concatenate([a[0], a[-1], a[:, 0], a[:, -1]])
    bgc = np.median(border, axis=0)
    diff = np.abs(a - bgc).max(axis=2)
    bg_like = diff < 13
    line = (b - r > 45) & (b - g > 15) & (b > 90)      # linha azul do chão
    # preenche o fundo a partir das bordas (preserva partes escuras do rato)
    lab, n = ndi.label(bg_like | line)
    edge_labels = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    bg = np.isin(lab, list(edge_labels))
    fg = ~bg
    fg = ndi.binary_opening(fg, iterations=1)
    lab2, n2 = ndi.label(ndi.binary_dilation(fg, iterations=2))
    sizes = ndi.sum(fg, lab2, range(1, n2 + 1))
    fg = fg & (lab2 == (int(np.argmax(sizes)) + 1))
    fg = ndi.binary_fill_holes(fg)
    rgba = np.zeros(a.shape[:2] + (4,), dtype=np.uint8)
    rgba[..., :3] = a.astype(np.uint8)
    rgba[..., 3] = (fg * 255).astype(np.uint8)
    im = Image.fromarray(rgba, "RGBA")
    return im.crop(im.getbbox())


def main():
    ref = Image.open(SRC)
    os.makedirs(OUT, exist_ok=True)
    frames = []
    for (x0, x1) in COLS:
        f = keyed_frame(ref, x0, x1)
        w, h = int(f.width * SCALE), int(f.height * SCALE)
        f = f.resize((max(1, w), max(1, h)), Image.LANCZOS)
        a = f.split()[3].point(lambda v: 255 if v > 110 else 0)
        f.putalpha(a)
        frames.append(f)
    for i, f in enumerate(frames):
        canvas = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
        top = f.crop((0, 0, f.width, max(1, int(f.height * 0.5))))
        nose = top.split()[3].getbbox()[2]
        canvas.alpha_composite(f, (NOSE_X - nose, GROUND_Y - f.height))
        canvas.save(os.path.join(OUT, f"rat_run_{i}.png"))
    # parado: usa o frame com as patas apoiadas
    canvas = Image.open(os.path.join(OUT, "rat_run_2.png"))
    canvas.save(os.path.join(OUT, "rat_stand.png"))
    print("frames", [f.size for f in frames])


if __name__ == "__main__":
    main()
