# -*- coding: utf-8 -*-
"""Gera o logotipo PROJETO R-31 (letras angulares amarelas, R vermelho) e o rato grande do menu."""
import os
from PIL import Image, ImageDraw, ImageFilter, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "assets", "ui")
SRC = os.path.join(HERE, "src", "spr")

YELLOW = (252, 238, 10, 255)
YELLOW_DK = (190, 160, 0, 255)
RED = (255, 38, 58, 255)
RED_DK = (150, 10, 30, 255)
DARK = (14, 10, 6, 255)
CYAN = (0, 240, 255, 255)
MAGENTA = (255, 0, 140, 255)

# glifos em grade 4x6, com cantos chanfrados (traço = lista de polilinhas)
G = {
    "P": [[(0, 6), (0, 0), (3, 0), (4, 1), (4, 3), (3, 4), (0, 4)]],
    "R": [[(0, 6), (0, 0), (3, 0), (4, 1), (4, 3), (3, 4), (0, 4)], [(2, 4), (4, 6)]],
    "O": [[(1, 0), (3, 0), (4, 1), (4, 5), (3, 6), (1, 6), (0, 5), (0, 1), (1, 0)]],
    "J": [[(0, 5), (1, 6), (3, 6), (4, 5), (4, 0)]],
    "E": [[(4, 0), (0, 0), (0, 6), (4, 6)], [(0, 3), (3, 3)]],
    "T": [[(0, 0), (4, 0)], [(2, 0), (2, 6)]],
    "2": [[(0, 1), (1, 0), (3, 0), (4, 1), (4, 2), (0, 6), (4, 6)]],
    "3": [[(0, 1), (1, 0), (3, 0), (4, 1), (4, 2), (3, 3), (1.5, 3)], [(3, 3), (4, 4), (4, 5), (3, 6), (1, 6), (0, 5)]],
    "1": [[(0, 2), (2, 0), (2, 6)], [(0, 6), (4, 6)]],
    "-": [[(0.4, 3), (3.6, 3)]],
}


def draw_text(text, unit, stroke, colors, gap=1.5, shear=0.18):
    """Retorna (camada de cor, máscara) do texto. colors: função índice->cor."""
    n_w = sum((4 if c != "-" else 4) for c in text) + gap * (len(text) - 1)
    W = int(n_w * unit + stroke * 3 + 6 * unit * shear + 20)
    H = int(6 * unit + stroke * 3 + 10)
    S = 3
    col = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    x0 = stroke * 1.2
    for idx, ch in enumerate(text):
        d = ImageDraw.Draw(col)
        c = colors(idx)
        for line in G[ch]:
            pts = []
            for (gx, gy) in line:
                px = x0 + gx * unit + (6 - gy) * unit * shear
                py = stroke * 1.2 + gy * unit
                pts.append((px * S, py * S))
            d.line(pts, fill=c, width=int(stroke * S), joint="curve")
            # cantos vivos: quadradinho nas pontas para ficar angular
            for (px, py) in (pts[0], pts[-1]):
                r = stroke * S / 2
                d.rectangle((px - r, py - r, px + r, py + r), fill=c)
        x0 += (4 + gap) * unit
    col = col.resize((W, H), Image.LANCZOS)
    return col


def outline(im, r, color):
    a = im.split()[3]
    m = a.filter(ImageFilter.MaxFilter(r * 2 + 1))
    o = Image.new("RGBA", im.size, color)
    o.putalpha(m)
    return o


def glow(im, color, radius, strength):
    a = im.split()[3].filter(ImageFilter.GaussianBlur(radius))
    g = Image.new("RGBA", im.size, color)
    g.putalpha(a.point(lambda v: int(v * strength)))
    return g


def build_logo():
    pad = 26
    # linha 1: PROJETO (menor)
    t1 = draw_text("PROJETO", 15, 11, lambda i: YELLOW, gap=1.1, shear=0.2)
    # linha 2: R-31 (maior), R vermelho
    t2 = draw_text("R-31", 34, 25, lambda i: RED if i == 0 else YELLOW, gap=1.0, shear=0.2)
    W = max(t1.width, t2.width) + pad * 2
    H = t1.height + t2.height + pad * 2 + 8
    base = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    base.alpha_composite(t1, (pad, pad))
    base.alpha_composite(t2, (pad, pad + t1.height + 8))
    # sombra extrudada (profundidade amarelo escuro / vermelho escuro)
    shadow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    for k in range(8, 0, -1):
        layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
        layer.alpha_composite(base, (k, k))
        a = layer.split()[3]
        tint = Image.new("RGBA", base.size, (120, 98, 0, 255))
        tint.putalpha(a)
        shadow.alpha_composite(tint)
    res = Image.new("RGBA", base.size, (0, 0, 0, 0))
    res.alpha_composite(glow(base, (255, 220, 0, 255), 14, 0.55))
    res.alpha_composite(outline(shadow, 3, DARK))
    res.alpha_composite(shadow)
    # deslocamento "glitch" ciano e magenta
    cy = Image.new("RGBA", base.size, CYAN); cy.putalpha(base.split()[3].point(lambda v: int(v * 0.8)))
    mg = Image.new("RGBA", base.size, MAGENTA); mg.putalpha(base.split()[3].point(lambda v: int(v * 0.8)))
    res.alpha_composite(cy, (-3, -2))
    res.alpha_composite(mg, (3, 2))
    res.alpha_composite(outline(base, 2, DARK))
    res.alpha_composite(base)
    # brilho interno (faixa clara no topo das letras)
    hi = Image.new("RGBA", base.size, (255, 255, 255, 0))
    a = base.split()[3]
    band = Image.new("L", base.size, 0)
    ImageDraw.Draw(band).rectangle((0, 0, W, int(H * 0.28)), fill=70)
    band = ImageChops.multiply(band, a)
    hi.putalpha(band)
    hi = Image.composite(Image.new("RGBA", base.size, (255, 255, 255, 255)), hi, band.point(lambda v: 255 if v else 0))
    hi.putalpha(band)
    res.alpha_composite(hi)
    # cortes horizontais (glitch) em duas linhas finas
    px = res.load()
    for yy, off in ((int(H * 0.62), 6), (int(H * 0.66), -5)):
        row = res.crop((0, yy, W, yy + 3))
        res.paste((0, 0, 0, 0), (0, yy, W, yy + 3))
        res.alpha_composite(row, (off, yy))
    os.makedirs(OUT, exist_ok=True)
    res.save(os.path.join(OUT, "title_logo.png"))
    print("logo", res.size)


def build_menu_rat():
    im = Image.open(os.path.join(SRC, "front.png")).convert("RGBA")
    a0 = im.split()[3].point(lambda v: 255 if v > 90 else 0)
    im.putalpha(a0)
    k = 400.0 / im.height
    big = im.resize((int(im.width * k), 400), Image.LANCZOS)
    pad = 64
    canvas = Image.new("RGBA", (big.width + pad * 2, big.height + pad * 2), (0, 0, 0, 0))
    g = glow(big, (60, 255, 140, 255), 12, 0.6)
    canvas.alpha_composite(g, (pad, pad))
    canvas.alpha_composite(big, (pad, pad))
    canvas.save(os.path.join(OUT, "menu_rat.png"))
    print("rat", canvas.size)


if __name__ == "__main__":
    build_logo()
    build_menu_rat()
