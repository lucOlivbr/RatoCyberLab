# -*- coding: utf-8 -*-
"""Decoração extra do laboratório: computadores, mesas de poções, estantes de livros, bancadas, grades da jaula."""
import random
from PIL import Image, ImageDraw
from art_lib import T, hx, mix, shade, new, glow_only

OL = (8, 11, 20, 255)
WOOD = (74, 54, 46, 255)
WOOD_HI = (112, 84, 66, 255)
METAL = (48, 58, 84, 255)
METAL_HI = (110, 126, 164, 255)
PAPER = (222, 216, 190, 255)
COLS = [(255, 80, 110, 255), (255, 200, 70, 255), (90, 255, 140, 255), (180, 100, 255, 255), (70, 170, 255, 255), (255, 140, 60, 255)]


def deco_computer(w, h, theme, seed=1):
    """Mesa com monitor antigo (desligado/fora de uso), teclado e papéis."""
    rnd = random.Random(seed)
    W_, H_ = w * T, h * T
    im = new(W_, H_ + 18)
    d = ImageDraw.Draw(im)
    acc = hx(theme["accent"])
    top = 22
    # mesa
    d.rectangle((1, top + 6, W_ - 2, top + H_ - 2), fill=METAL, outline=OL)
    d.rectangle((1, top, W_ - 2, top + 8), fill=(70, 82, 112, 255), outline=OL)
    d.line((2, top + 1, W_ - 3, top + 1), fill=METAL_HI)
    # monitor
    mx = 4
    for k in range(max(1, w // 2)):
        x0 = mx + k * 30
        d.rectangle((x0 + 3, 2, x0 + 25, top + 1), fill=(34, 40, 58, 255), outline=OL)
        d.rectangle((x0 + 5, 4, x0 + 23, top - 4), fill=(8, 14, 22, 255))
        if rnd.random() < 0.45:
            for yy in range(6, top - 5, 3):
                d.line((x0 + 7, yy, x0 + 7 + rnd.randrange(4, 13), yy), fill=shade(acc, 0.55))
        else:
            d.line((x0 + 6, 5, x0 + 22, top - 5), fill=(30, 36, 50, 255))
            d.line((x0 + 22, 5, x0 + 6, top - 5), fill=(30, 36, 50, 255))
        d.rectangle((x0 + 12, top - 2, x0 + 16, top + 2), fill=METAL)
    # teclado e papéis
    d.rectangle((W_ - 30, top + 10, W_ - 6, top + 15), fill=(30, 34, 48, 255), outline=OL)
    for x in range(W_ - 28, W_ - 8, 3):
        d.point((x, top + 12), fill=(110, 120, 150, 255))
    d.rectangle((6, top + 11, 20, top + 18), fill=PAPER, outline=(120, 110, 90, 255))
    d.line((8, top + 14, 17, top + 14), fill=(120, 110, 90, 255))
    return im


def deco_potions(w, h, theme, seed=1):
    """Mesa de poções: frascos borbulhando, tubos de ensaio, béqueres."""
    rnd = random.Random(seed)
    W_, H_ = w * T, h * T
    im = new(W_, H_ + 14)
    d = ImageDraw.Draw(im)
    top = 14 + (0 if h > 1 else -4)
    d.rectangle((1, top + 10, W_ - 2, top + H_ - 4), fill=(52, 38, 34, 255), outline=OL)
    d.rectangle((1, top + 4, W_ - 2, top + 13), fill=WOOD_HI, outline=OL)
    d.line((2, top + 5, W_ - 3, top + 5), fill=(150, 120, 96, 255))
    x = 6
    while x < W_ - 16:
        kind = rnd.choice(["flask", "beaker", "tube", "round"])
        col = rnd.choice(COLS)
        base = top + 12
        if kind == "flask":
            d.polygon([(x + 5, base - 16), (x + 9, base - 16), (x + 14, base - 1), (x, base - 1)], fill=shade(col, 0.45), outline=(150, 180, 210, 255))
            d.polygon([(x + 3, base - 7), (x + 11, base - 7), (x + 14, base - 1), (x, base - 1)], fill=col)
            d.rectangle((x + 5, base - 19, x + 9, base - 16), fill=(130, 90, 50, 255))
            x += 17
        elif kind == "beaker":
            d.rectangle((x, base - 13, x + 11, base - 1), fill=shade(col, 0.35), outline=(150, 180, 210, 255))
            d.rectangle((x + 1, base - 8, x + 10, base - 2), fill=col)
            d.line((x + 2, base - 7, x + 9, base - 7), fill=mix(col, (255, 255, 255, 255), 0.5))
            x += 15
        elif kind == "tube":
            for k in range(3):
                tx = x + k * 5
                c2 = rnd.choice(COLS)
                d.rectangle((tx, base - 15, tx + 3, base - 1), fill=shade(c2, 0.4), outline=(150, 180, 210, 255))
                d.rectangle((tx + 1, base - 9, tx + 2, base - 2), fill=c2)
            d.rectangle((x - 1, base - 3, x + 15, base - 1), fill=(60, 60, 80, 255))
            x += 19
        else:
            d.ellipse((x, base - 14, x + 13, base - 1), fill=shade(col, 0.4), outline=(150, 180, 210, 255))
            d.pieslice((x + 1, base - 9, x + 12, base - 1), 0, 180, fill=col)
            d.rectangle((x + 5, base - 18, x + 8, base - 13), fill=(150, 180, 210, 255))
            x += 17
    # bolhas luminosas
    for _ in range(3):
        bx, by = rnd.randrange(6, W_ - 6), rnd.randrange(0, top + 2)
        d.ellipse((bx, by, bx + 1, by + 1), fill=rnd.choice([(150, 255, 190, 255), (150, 220, 255, 255)]))
    return im


def deco_books(w, h, theme, seed=1):
    """Estante de livros e pastas."""
    rnd = random.Random(seed)
    W_, H_ = w * T, h * T
    im = new(W_, H_)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W_ - 1, H_ - 1), fill=(36, 26, 24, 255), outline=OL)
    rows = max(2, h * 2)
    rh = (H_ - 6) // rows
    for r in range(rows):
        by = 4 + (r + 1) * rh - 1
        d.rectangle((1, by, W_ - 2, by + 2), fill=WOOD_HI)
        x = 3
        while x < W_ - 8:
            bw = rnd.choice([3, 4, 5, 6])
            bh = rnd.randrange(rh - 8, rh - 2)
            col = rnd.choice([(150, 40, 50, 255), (40, 90, 150, 255), (50, 120, 70, 255), (150, 110, 40, 255), (110, 60, 140, 255), (200, 190, 160, 255), (60, 60, 80, 255)])
            if rnd.random() < 0.12:
                # livro deitado
                d.rectangle((x, by - 5, x + 11, by - 1), fill=col, outline=shade(col, 0.5))
                x += 13
                continue
            d.rectangle((x, by - bh, x + bw, by - 1), fill=col, outline=shade(col, 0.5))
            d.line((x + 1, by - bh + 2, x + 1, by - 3), fill=shade(col, 1.4))
            if rnd.random() < 0.4:
                d.line((x, by - bh // 2, x + bw, by - bh // 2), fill=(230, 210, 120, 255))
            x += bw + 1
    return im


def deco_desk(w, h, theme, seed=1):
    """Mesa de trabalho com papéis, pranchetas e lupa."""
    rnd = random.Random(seed)
    W_, H_ = w * T, h * T
    im = new(W_, H_ + 10)
    d = ImageDraw.Draw(im)
    top = 8
    d.rectangle((1, top + 8, W_ - 2, top + H_ - 2), fill=(56, 42, 38, 255), outline=OL)
    d.rectangle((1, top, W_ - 2, top + 10), fill=WOOD_HI, outline=OL)
    d.line((2, top + 1, W_ - 3, top + 1), fill=(160, 130, 104, 255))
    x = 6
    while x < W_ - 22:
        k = rnd.choice(["papers", "clip", "mug", "lamp"])
        if k == "papers":
            d.rectangle((x, top - 4, x + 14, top + 8), fill=PAPER, outline=(120, 110, 90, 255))
            for yy in range(top - 1, top + 7, 3):
                d.line((x + 2, yy, x + 11, yy), fill=(130, 120, 100, 255))
            x += 17
        elif k == "clip":
            d.rectangle((x, top - 6, x + 12, top + 8), fill=(110, 76, 50, 255), outline=OL)
            d.rectangle((x + 2, top - 4, x + 10, top + 6), fill=PAPER)
            d.rectangle((x + 4, top - 8, x + 8, top - 5), fill=METAL_HI)
            x += 16
        elif k == "mug":
            d.rectangle((x, top - 2, x + 6, top + 8), fill=(200, 80, 90, 255), outline=OL)
            d.line((x + 7, top, x + 9, top + 3), fill=(200, 80, 90, 255))
            x += 11
        else:
            d.line((x + 4, top + 8, x + 4, top - 8), fill=METAL_HI, width=2)
            d.polygon([(x - 2, top - 7), (x + 10, top - 7), (x + 7, top - 12), (x + 1, top - 12)], fill=(255, 220, 110, 255), outline=OL)
            x += 14
    return im


def spr_bars(w=64, h=64):
    """Grades da jaula: barras de aço com brilho verde-azulado."""
    im = new(w, h)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 2, w - 1, 9), fill=(70, 82, 112, 255), outline=OL)
    d.line((1, 3, w - 2, 3), fill=METAL_HI)
    d.rectangle((0, h - 9, w - 1, h - 2), fill=(70, 82, 112, 255), outline=OL)
    for x in range(4, w - 3, 9):
        d.rectangle((x, 8, x + 4, h - 8), fill=(120, 136, 168, 255), outline=OL)
        d.line((x + 1, 9, x + 1, h - 10), fill=(214, 226, 246, 255))
        d.line((x + 3, 9, x + 3, h - 10), fill=(70, 82, 112, 255))
    d.rectangle((w // 2 - 6, h // 2 - 5, w // 2 + 6, h // 2 + 5), fill=(60, 66, 90, 255), outline=OL)
    d.ellipse((w // 2 - 2, h // 2 - 2, w // 2 + 2, h // 2 + 2), fill=(255, 70, 90, 255))
    glow_only(im, lambda dd, c: dd.rectangle((1, 3, w - 2, h - 3), outline=c), (60, 255, 190, 255), 5, 0.55)
    return im


def cage_ring(theme, cx0, cx1, cy0, cy1):
    """Anel de grades (cx0..cx1, cy0..cy1 em tiles, inclusive) desenhado como camada RGBA do tamanho do mapa."""
    W_, H_ = 30 * T, 15 * T
    im = new(W_, H_)
    d = ImageDraw.Draw(im)
    acc = hx(theme["accent"])
    x0, x1 = cx0 * T, (cx1 + 1) * T
    y0, y1 = cy0 * T, (cy1 + 1) * T
    # topo (barras de frente, mais altas)
    top_h = 44
    d.rectangle((x0, y1 - 1, x1 - 1, y1 - 1), fill=OL)
    # barras laterais (vistas de cima: fileira de barras)
    for xx in (x0, x1 - 12):
        d.rectangle((xx, y0 - top_h + 8, xx + 11, y1 - 2), fill=(42, 50, 72, 255), outline=OL)
        for y in range(y0 - top_h + 12, y1 - 6, 7):
            d.rectangle((xx + 2, y, xx + 9, y + 3), fill=(110, 124, 156, 255))
        d.line((xx + 1, y0 - top_h + 9, xx + 1, y1 - 3), fill=(190, 206, 232, 255))
    # fundo escuro
    d.rectangle((x0, y0 - top_h, x1 - 1, y0 - top_h + 12), fill=(70, 82, 112, 255), outline=OL)
    d.line((x0 + 1, y0 - top_h + 2, x1 - 2, y0 - top_h + 2), fill=METAL_HI)
    for x in range(x0 + 14, x1 - 14, 12):
        d.rectangle((x, y0 - top_h + 12, x + 5, y0 + 2), fill=(112, 128, 160, 255), outline=OL)
        d.line((x + 1, y0 - top_h + 13, x + 1, y0 + 1), fill=(210, 224, 246, 255))
        d.line((x + 4, y0 - top_h + 13, x + 4, y0 + 1), fill=(66, 78, 106, 255))
    d.rectangle((x0, y0, x1 - 1, y0 + 10), fill=(70, 82, 112, 255), outline=OL)
    d.line((x0 + 1, y0 + 1, x1 - 2, y0 + 1), fill=METAL_HI)
    # frente (parte de baixo): barras verticais cobrindo o piso
    d.rectangle((x0, y1 - 10, x1 - 1, y1 + 8), fill=(70, 82, 112, 255), outline=OL)
    d.line((x0 + 1, y1 - 9, x1 - 2, y1 - 9), fill=METAL_HI)
    for x in range(x0 + 14, x1 - 14, 12):
        d.rectangle((x, y1 + 8, x + 5, y1 + 20), fill=(112, 128, 160, 255), outline=OL)
    return im
