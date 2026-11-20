# -*- coding: utf-8 -*-
"""Sprite do núcleo central (2x2 tiles = 64x64) em dois estados: normal (azul) e com a bomba armada (vermelho)."""
import os, math
from PIL import Image, ImageDraw, ImageFilter
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "world")
S = 6


def build(armed):
    W, H = 64, 64
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    col = (255, 70, 80) if armed else (70, 190, 255)
    dark = (8, 11, 20, 255)

    def r(x0, y0, x1, y1, fill, outline=None, w=1):
        d.rectangle((x0 * S, y0 * S, x1 * S, y1 * S), fill=fill, outline=outline, width=w * S if outline else 0)

    def e(x0, y0, x1, y1, fill, outline=None, w=1):
        d.ellipse((x0 * S, y0 * S, x1 * S, y1 * S), fill=fill, outline=outline, width=w * S if outline else 0)
    # base circular
    e(3, 46, 61, 63, (36, 44, 66, 255), dark, 1)
    e(7, 46, 57, 59, (52, 62, 90, 255), (100, 116, 156, 255), 1)
    e(14, 48, 50, 57, (20, 26, 42, 255))
    # anel luminoso no chão
    d.arc((9 * S, 47 * S, 55 * S, 60 * S), 0, 360, fill=col + (255,), width=2 * S)
    # coluna de vidro
    r(20, 14, 44, 52, (20, 34, 58, 150), (150, 190, 230, 255), 1)
    r(16, 10, 48, 15, (60, 72, 104, 255), dark, 1)
    r(16, 50, 48, 56, (60, 72, 104, 255), dark, 1)
    # orbe central
    e(22, 20, 42, 40, col + (230,))
    e(26, 24, 38, 36, (255, 255, 255, 235))
    # arcos de energia
    for a in range(0, 360, 60):
        ar = math.radians(a + (25 if armed else 0))
        d.line((32 * S, 30 * S, (32 + math.cos(ar) * 15) * S, (30 + math.sin(ar) * 15) * S), fill=col + (255,), width=S)
    # detalhes na base
    for x in (10, 18, 46, 54):
        r(x, 52, x + 2, 55, col + (255,))
    if armed:
        # bomba presa à frente do núcleo
        e(22, 34, 42, 56, (24, 26, 34, 255), (100, 100, 120, 255), 1)
        r(29, 31, 35, 36, (110, 110, 130, 255), dark, 1)
        r(25, 42, 39, 49, (6, 8, 14, 255), (255, 80, 90, 255), 1)
        # mostrador
        for k in range(3):
            r(27 + k * 4, 44, 28 + k * 4, 47, (255, 90, 100, 255))
        e(30, 37, 34, 41, (255, 40, 50, 255))
        d.line((32 * S, 31 * S, 36 * S, 24 * S), fill=(220, 180, 60, 255), width=S)
    im = im.resize((W, H), Image.LANCZOS)
    a = im.split()[3].point(lambda v: 255 if v > 90 else 0)
    im.putalpha(a)
    # contorno de 1px
    mask = a.filter(ImageFilter.MaxFilter(3))
    ol = Image.new("RGBA", (W, H), (8, 11, 20, 255))
    ol.putalpha(mask)
    ol.alpha_composite(im)
    # brilho
    gl = Image.new("RGBA", (W, H), col + (0,))
    gl.putalpha(a.filter(ImageFilter.GaussianBlur(3)).point(lambda v: int(v * 0.25)))
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    out.alpha_composite(gl)
    out.alpha_composite(ol)
    return out


if __name__ == "__main__":
    build(False).save(os.path.join(OUT, "console_core_0.png"))
    build(True).save(os.path.join(OUT, "console_core_1.png"))
    print("core ok")
