# -*- coding: utf-8 -*-
"""Biblioteca de pixel art procedural para o Rato CyberLab (PIL)."""
import random, math
from PIL import Image, ImageDraw, ImageFilter, ImageChops

T = 32  # tamanho do tile

def hx(c, a=255):
    c = c.lstrip('#')
    return (int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16), a)

def mix(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(4))

def shade(c, f):
    return (max(0, min(255, int(c[0] * f))), max(0, min(255, int(c[1] * f))), max(0, min(255, int(c[2] * f))), c[3])

def new(w, h, col=(0, 0, 0, 0)):
    return Image.new("RGBA", (w, h), col)

def glow(base, draw_fn, color, radius=4, strength=1.0):
    """Desenha draw_fn(d) numa camada, borra e compõe (brilho neon)."""
    layer = new(base.width, base.height)
    d = ImageDraw.Draw(layer)
    draw_fn(d, color)
    bl = layer.filter(ImageFilter.GaussianBlur(radius))
    if strength != 1.0:
        a = bl.getchannel("A").point(lambda v: min(255, int(v * strength)))
        bl.putalpha(a)
    base.alpha_composite(bl)
    base.alpha_composite(layer)

def glow_only(base, draw_fn, color, radius=4, strength=1.0):
    layer = new(base.width, base.height)
    d = ImageDraw.Draw(layer)
    draw_fn(d, color)
    bl = layer.filter(ImageFilter.GaussianBlur(radius))
    if strength != 1.0:
        a = bl.getchannel("A").point(lambda v: min(255, int(v * strength)))
        bl.putalpha(a)
    base.alpha_composite(bl)

def radial(w, h, color, max_a=120):
    """Mancha de luz radial (para luzes no chão)."""
    im = new(w, h)
    px = im.load()
    cx, cy = (w - 1) / 2, (h - 1) / 2
    for y in range(h):
        for x in range(w):
            dx = (x - cx) / (w / 2); dy = (y - cy) / (h / 2)
            r = math.sqrt(dx * dx + dy * dy)
            if r < 1:
                a = int(max_a * (1 - r) ** 2)
                px[x, y] = (color[0], color[1], color[2], a)
    return im

# ---------------------------------------------------------------- fonte 3x5
FONT = {
 'A': [".#.", "#.#", "###", "#.#", "#.#"], 'B': ["##.", "#.#", "##.", "#.#", "##."],
 'C': [".##", "#..", "#..", "#..", ".##"], 'D': ["##.", "#.#", "#.#", "#.#", "##."],
 'E': ["###", "#..", "##.", "#..", "###"], 'F': ["###", "#..", "##.", "#..", "#.."],
 'G': [".##", "#..", "#.#", "#.#", ".##"], 'H': ["#.#", "#.#", "###", "#.#", "#.#"],
 'I': ["###", ".#.", ".#.", ".#.", "###"], 'J': ["..#", "..#", "..#", "#.#", ".#."],
 'K': ["#.#", "#.#", "##.", "#.#", "#.#"], 'L': ["#..", "#..", "#..", "#..", "###"],
 'M': ["#.#", "###", "###", "#.#", "#.#"], 'N': ["###", "#.#", "#.#", "#.#", "#.#"],
 'O': [".#.", "#.#", "#.#", "#.#", ".#."], 'P': ["##.", "#.#", "##.", "#..", "#.."],
 'Q': [".#.", "#.#", "#.#", "##.", ".##"], 'R': ["##.", "#.#", "##.", "#.#", "#.#"],
 'S': [".##", "#..", ".#.", "..#", "##."], 'T': ["###", ".#.", ".#.", ".#.", ".#."],
 'U': ["#.#", "#.#", "#.#", "#.#", "###"], 'V': ["#.#", "#.#", "#.#", "#.#", ".#."],
 'W': ["#.#", "#.#", "###", "###", "#.#"], 'X': ["#.#", "#.#", ".#.", "#.#", "#.#"],
 'Y': ["#.#", "#.#", ".#.", ".#.", ".#."], 'Z': ["###", "..#", ".#.", "#..", "###"],
 '0': ["###", "#.#", "#.#", "#.#", "###"], '1': [".#.", "##.", ".#.", ".#.", "###"],
 '2': ["##.", "..#", ".#.", "#..", "###"], '3': ["##.", "..#", ".#.", "..#", "##."],
 '4': ["#.#", "#.#", "###", "..#", "..#"], '5': ["###", "#..", "##.", "..#", "##."],
 '6': [".##", "#..", "###", "#.#", "###"], '7': ["###", "..#", ".#.", ".#.", ".#."],
 '8': ["###", "#.#", "###", "#.#", "###"], '9': ["###", "#.#", "###", "..#", "##."],
 '/': ["..#", "..#", ".#.", "#..", "#.."], '-': ["...", "...", "###", "...", "..."],
 '.': ["...", "...", "...", "...", ".#."], ' ': ["...", "...", "...", "...", "..."],
 ':': ["...", ".#.", "...", ".#.", "..."],
}

def text_width(s, scale=2):
    return len(s) * (4 * scale) - scale

def draw_text(d, x, y, s, col, scale=2):
    cx = x
    for ch in s.upper():
        g = FONT.get(ch, FONT[' '])
        for ry, row in enumerate(g):
            for rx, c in enumerate(row):
                if c == '#':
                    d.rectangle((cx + rx * scale, y + ry * scale, cx + rx * scale + scale - 1, y + ry * scale + scale - 1), fill=col)
        cx += 4 * scale

# ---------------------------------------------------------------- chão e paredes
def floor_tile(theme, seed, alt):
    rnd = random.Random(seed)
    base = hx(theme["floor2"] if alt else theme["floor"])
    im = new(T, T, base)
    d = ImageDraw.Draw(im)
    # pontos de ruído
    for _ in range(26):
        x, y = rnd.randrange(T), rnd.randrange(T)
        d.point((x, y), fill=shade(base, rnd.choice([0.86, 1.12, 1.2])))
    # bordas da placa
    d.line((0, T - 1, T - 1, T - 1), fill=shade(base, 0.62))
    d.line((T - 1, 0, T - 1, T - 1), fill=shade(base, 0.62))
    d.line((0, 0, T - 2, 0), fill=shade(base, 1.28))
    d.line((0, 0, 0, T - 2), fill=shade(base, 1.28))
    # rebites
    for (x, y) in ((3, 3), (T - 5, 3), (3, T - 5), (T - 5, T - 5)):
        d.point((x, y), fill=shade(base, 1.5)); d.point((x + 1, y + 1), fill=shade(base, 0.5))
    v = rnd.random()
    acc = hx(theme["accent"])
    if v < 0.10:   # grade de ventilação
        for yy in range(8, T - 8, 3):
            d.line((8, yy, T - 9, yy), fill=shade(base, 0.55))
    elif v < 0.16: # linha neon sutil
        d.line((6, T // 2, T - 7, T // 2), fill=mix(base, acc, 0.35))
    elif v < 0.20: # risco de manutenção
        d.line((4, T - 8, T - 6, T - 14), fill=shade(base, 0.7))
    return im

def wall_roof_tile(theme, seed):
    rnd = random.Random(seed)
    base = (11, 15, 26, 255)
    im = new(T, T, base)
    d = ImageDraw.Draw(im)
    for _ in range(16):
        d.point((rnd.randrange(T), rnd.randrange(T)), fill=shade(base, rnd.choice([0.8, 1.5, 1.9])))
    d.line((0, 0, T - 1, 0), fill=(20, 27, 44, 255))
    return im

def wall_face_tile(theme, seed, h=64):
    """Face frontal da parede (32x64): parede alta, cobre 32px do telhado acima."""
    rnd = random.Random(seed)
    acc = hx(theme["accent"])
    wallc = hx(theme["wall"])
    im = new(T, h, wallc)
    d = ImageDraw.Draw(im)
    # gradiente vertical
    for y in range(h):
        f = 0.78 + 0.5 * (y / h)
        c = shade(wallc, f)
        d.line((0, y, T - 1, y), fill=c)
    # painel superior escuro (telhado aparente)
    d.rectangle((0, 0, T - 1, 7), fill=(14, 19, 33, 255))
    d.line((0, 8, T - 1, 8), fill=shade(wallc, 1.6))
    d.line((0, 9, T - 1, 9), fill=shade(acc, 0.35))
    # painel intermediário com divisória
    d.line((0, 30, T - 1, 30), fill=shade(wallc, 0.6))
    d.line((0, 31, T - 1, 31), fill=shade(wallc, 1.35))
    # costuras
    d.line((0, 0, 0, h - 1), fill=shade(wallc, 0.55))
    d.line((T - 1, 0, T - 1, h - 1), fill=shade(wallc, 0.55))
    # faixa neon
    ny = h - 16
    d.rectangle((0, ny - 1, T - 1, ny + 3), fill=shade(wallc, 0.5))
    d.line((2, ny + 1, T - 3, ny + 1), fill=acc)
    # luzinhas / telas
    v = rnd.random()
    if v < 0.35:
        sx = rnd.randrange(4, 14)
        d.rectangle((sx, 14, sx + 12, 26), fill=(8, 12, 20, 255), outline=shade(wallc, 1.6))
        for i in range(3):
            lw = rnd.randrange(3, 9)
            d.line((sx + 2, 17 + i * 3, sx + 2 + lw, 17 + i * 3), fill=mix(acc, (255, 255, 255, 255), 0.2))
    elif v < 0.55:
        for i in range(4):
            d.rectangle((6 + i * 6, 16, 8 + i * 6, 18), fill=rnd.choice([acc, (255, 70, 90, 255), (255, 210, 70, 255), shade(wallc, 0.4)]))
    elif v < 0.70:
        for yy in range(14, 28, 3):
            d.line((6, yy, T - 7, yy), fill=shade(wallc, 0.5))
    # grade de ventilação na parte baixa
    if rnd.random() < 0.5:
        for yy in range(34, 44, 3):
            d.line((7, yy, T - 8, yy), fill=shade(wallc, 0.45))
    # rodapé
    d.rectangle((0, h - 4, T - 1, h - 1), fill=shade(wallc, 0.4))
    d.line((0, h - 4, T - 1, h - 4), fill=shade(wallc, 1.3))
    # brilho neon (halo sutil)
    glow_only(im, lambda dd, c: dd.line((2, ny + 1, T - 3, ny + 1), fill=c), acc, 3, 0.8)
    return im

# ---------------------------------------------------------------- decoração (desenhada no fundo)
def deco_tank(w, h, theme, creature=False, seed=1, liquid=None):
    rnd = random.Random(seed)
    W_, H_ = w * T, h * T
    im = new(W_, H_)
    d = ImageDraw.Draw(im)
    acc = hx(liquid or theme["accent"])
    d.ellipse((2, H_ - 14, W_ - 3, H_ - 2), fill=(10, 14, 22, 255))        # base
    d.rectangle((2, H_ - 24, W_ - 3, H_ - 8), fill=(34, 42, 62, 255), outline=(14, 18, 30, 255))
    d.line((3, H_ - 23, W_ - 4, H_ - 23), fill=(88, 102, 138, 255))
    # corpo de vidro
    gx0, gx1 = 5, W_ - 6
    gy0, gy1 = 10, H_ - 22
    d.rectangle((gx0, gy0, gx1, gy1), fill=shade(acc, 0.32), outline=(150, 180, 210, 255))
    # líquido com gradiente
    for y in range(gy0 + 5, gy1):
        t = (y - gy0) / max(1, (gy1 - gy0))
        d.line((gx0 + 1, y, gx1 - 1, y), fill=mix(shade(acc, 0.9), shade(acc, 0.35), t))
    # bolhas
    for _ in range(int(w * h * 3)):
        bx = rnd.randrange(gx0 + 4, gx1 - 3); by = rnd.randrange(gy0 + 8, gy1 - 2)
        d.ellipse((bx, by, bx + 1, by + 1), fill=mix(acc, (255, 255, 255, 255), 0.6))
    # criatura
    if creature:
        cx = (gx0 + gx1) // 2; cy = (gy0 + gy1) // 2 + 4
        d.ellipse((cx - 8, cy - 8, cx + 8, cy + 10), fill=shade(acc, 0.28))
        d.ellipse((cx - 5, cy - 3, cx - 2, cy), fill=(255, 250, 120, 255))
        d.ellipse((cx + 2, cy - 3, cx + 5, cy), fill=(255, 250, 120, 255))
        d.line((cx - 8, cy + 8, cx - 12, cy + 14), fill=shade(acc, 0.28))
        d.line((cx + 8, cy + 8, cx + 12, cy + 14), fill=shade(acc, 0.28))
    # reflexo vertical
    d.line((gx0 + 3, gy0 + 6, gx0 + 3, gy1 - 6), fill=(230, 245, 255, 150))
    d.line((gx0 + 4, gy0 + 8, gx0 + 4, gy1 - 10), fill=(230, 245, 255, 90))
    # tampa
    d.rectangle((2, 3, W_ - 3, 12), fill=(40, 50, 74, 255), outline=(12, 16, 28, 255))
    d.line((3, 4, W_ - 4, 4), fill=(100, 116, 150, 255))
    d.rectangle((W_ // 2 - 3, 0, W_ // 2 + 2, 4), fill=(28, 36, 56, 255))
    # luz
    glow_only(im, lambda dd, c: dd.rectangle((gx0 + 2, gy0 + 8, gx1 - 2, gy1 - 2), fill=c), acc, 6, 0.45)
    d.rectangle((6, H_ - 20, 9, H_ - 17), fill=acc)
    return im

def deco_rack(w, h, theme, seed=1):
    rnd = random.Random(seed)
    W_, H_ = w * T, h * T
    im = new(W_, H_)
    d = ImageDraw.Draw(im)
    acc = hx(theme["accent"])
    d.rectangle((1, 4, W_ - 2, H_ - 3), fill=(20, 26, 42, 255), outline=(8, 11, 20, 255))
    d.rectangle((1, 0, W_ - 2, 6), fill=(34, 42, 62, 255), outline=(8, 11, 20, 255))
    d.line((2, 1, W_ - 3, 1), fill=(96, 110, 146, 255))
    for yy in range(10, H_ - 6, 7):
        d.rectangle((4, yy, W_ - 5, yy + 4), fill=(12, 16, 28, 255), outline=(40, 50, 76, 255))
        for xx in range(6, W_ - 8, 5):
            d.point((xx, yy + 2), fill=rnd.choice([acc, acc, (80, 255, 130, 255), (255, 70, 90, 255), (255, 200, 60, 255), (30, 40, 60, 255)]))
        d.line((W_ - 14, yy + 2, W_ - 7, yy + 2), fill=(50, 62, 90, 255))
    glow_only(im, lambda dd, c: [dd.point((xx, yy + 2), fill=c) for yy in range(10, H_ - 6, 7) for xx in range(6, W_ - 8, 10)], acc, 2, 0.8)
    d.rectangle((1, H_ - 4, W_ - 2, H_ - 2), fill=(8, 11, 20, 255))
    return im

def deco_shelf(w, h, theme, seed=1):
    rnd = random.Random(seed)
    W_, H_ = w * T, h * T
    im = new(W_, H_)
    d = ImageDraw.Draw(im)
    acc = hx(theme["accent"])
    d.rectangle((0, 0, W_ - 1, H_ - 1), fill=(24, 30, 46, 255), outline=(8, 11, 20, 255))
    shelves = max(2, int(H_ / 20))
    for s in range(shelves):
        by = int(6 + (s + 1) * (H_ - 8) / shelves) - 2
        d.rectangle((1, by, W_ - 2, by + 2), fill=(60, 72, 104, 255))
        x = 4
        while x < W_ - 8:
            bw = rnd.choice([4, 5, 6]); bh = rnd.choice([8, 10, 12])
            col = rnd.choice([acc, (255, 80, 110, 255), (255, 200, 70, 255), (90, 255, 140, 255), (180, 100, 255, 255), (70, 170, 255, 255)])
            d.rectangle((x, by - bh, x + bw, by - 1), fill=shade(col, 0.55), outline=shade(col, 0.3))
            d.line((x + 1, by - bh + 1, x + 1, by - 3), fill=col)
            d.rectangle((x + 1, by - bh - 2, x + bw - 1, by - bh - 1), fill=(150, 160, 180, 255))
            x += bw + 3
    return im

def deco_boxes(w, h, theme, seed=1):
    rnd = random.Random(seed)
    W_, H_ = w * T, h * T
    im = new(W_, H_)
    d = ImageDraw.Draw(im)
    cols = [(176, 112, 54, 255), (150, 94, 46, 255), (196, 134, 66, 255), (112, 120, 140, 255)]
    # empilha caixas 28x28 em grade com variação
    for ty in range(h):
        for tx in range(w):
            if ty < h - 1 and rnd.random() < 0.18:  # buraco/desnível
                pass
            x0, y0 = tx * T + 1, ty * T + 1
            c = rnd.choice(cols)
            d.rectangle((x0, y0, x0 + T - 3, y0 + T - 3), fill=c, outline=shade(c, 0.45))
            d.line((x0 + 1, y0 + 1, x0 + T - 4, y0 + 1), fill=shade(c, 1.35))
            d.line((x0 + (T - 3) // 2, y0, x0 + (T - 3) // 2, y0 + T - 3), fill=shade(c, 0.7))
            d.rectangle((x0 + 4, y0 + 8, x0 + 12, y0 + 14), fill=(230, 230, 220, 255))
            d.line((x0 + 5, y0 + 10, x0 + 11, y0 + 10), fill=(60, 60, 70, 255))
            if rnd.random() < 0.35:
                d.rectangle((x0 + 16, y0 + 16, x0 + 24, y0 + 18), fill=hx(["#ff9a2a", "#19e6ff", "#ff3a55"][rnd.randrange(3)]))
    return im

def deco_machine(w, h, theme, seed=1):
    rnd = random.Random(seed)
    W_, H_ = w * T, h * T
    im = new(W_, H_)
    d = ImageDraw.Draw(im)
    acc = hx(theme["accent"])
    d.rectangle((1, 6, W_ - 2, H_ - 2), fill=(30, 38, 58, 255), outline=(8, 11, 20, 255))
    d.rectangle((1, 0, W_ - 2, 9), fill=(48, 58, 84, 255), outline=(8, 11, 20, 255))
    d.line((2, 1, W_ - 3, 1), fill=(110, 126, 164, 255))
    sx0, sy0, sx1, sy1 = 6, 14, W_ - 8, min(H_ - 20, 14 + 22)
    d.rectangle((sx0, sy0, sx1, sy1), fill=(6, 12, 20, 255), outline=(90, 104, 140, 255))
    pts = []
    for i in range(sx0 + 3, sx1 - 2, 3):
        pts.append((i, (sy0 + sy1) // 2 + rnd.randrange(-5, 6)))
    if len(pts) > 1: d.line(pts, fill=acc, width=1)
    glow_only(im, lambda dd, c: dd.rectangle((sx0, sy0, sx1, sy1), fill=shade(c, 0.5)), acc, 5, 0.5)
    for i in range(3):
        d.rectangle((6 + i * 8, H_ - 14, 10 + i * 8, H_ - 10), fill=rnd.choice([acc, (255, 70, 90, 255), (255, 200, 60, 255)]))
    for yy in range(H_ - 22, H_ - 6, 3):
        d.line((W_ - 18, yy, W_ - 6, yy), fill=(12, 16, 28, 255))
    return im

def deco_reactor(w, h, theme):
    W_, H_ = w * T, h * T
    im = new(W_, H_)
    d = ImageDraw.Draw(im)
    acc = hx(theme["accent"])
    # plataforma com listras de perigo
    d.ellipse((2, H_ - 52, W_ - 3, H_ - 2), fill=(26, 32, 50, 255), outline=(8, 11, 20, 255))
    d.ellipse((10, H_ - 46, W_ - 11, H_ - 10), outline=(255, 200, 60, 255), width=2)
    for i in range(0, 360, 20):
        a = math.radians(i)
        cx, cy = W_ / 2, H_ - 28
        rx, ry = (W_ - 24) / 2, 16
        x1 = cx + math.cos(a) * rx; y1 = cy + math.sin(a) * ry
        x2 = cx + math.cos(a) * (rx + 6); y2 = cy + math.sin(a) * (ry + 4)
        d.line((x1, y1, x2, y2), fill=(255, 200, 60, 255) if (i // 20) % 2 == 0 else (20, 20, 28, 255), width=2)
    # cilindro
    cx0, cx1 = W_ // 2 - 22, W_ // 2 + 22
    top, bot = 10, H_ - 30
    d.rectangle((cx0, top, cx1, bot), fill=(18, 36, 66, 255), outline=(150, 190, 230, 255))
    for y in range(top + 2, bot):
        t = (y - top) / (bot - top)
        d.line((cx0 + 2, y, cx1 - 2, y), fill=mix(shade(acc, 0.95), shade(acc, 0.35), t))
    # núcleo
    d.ellipse((W_ // 2 - 9, (top + bot) // 2 - 12, W_ // 2 + 9, (top + bot) // 2 + 12), fill=(210, 240, 255, 255))
    glow_only(im, lambda dd, c: dd.ellipse((W_ // 2 - 14, (top + bot) // 2 - 18, W_ // 2 + 14, (top + bot) // 2 + 18), fill=c), acc, 12, 1.0)
    for yy in (top, bot - 6):
        d.rectangle((cx0 - 6, yy, cx1 + 6, yy + 6), fill=(46, 56, 82, 255), outline=(8, 11, 20, 255))
        d.line((cx0 - 5, yy + 1, cx1 + 5, yy + 1), fill=(120, 136, 176, 255))
    # arcos de energia
    d.line((W_ // 2 - 22, top + 20, W_ // 2 - 30, top + 34, W_ // 2 - 26, top + 48), fill=(210, 240, 255, 255))
    d.line((W_ // 2 + 22, top + 28, W_ // 2 + 30, top + 40, W_ // 2 + 26, top + 56), fill=(210, 240, 255, 255))
    return im

def deco_aquarium(w, h, theme, seed=1):
    rnd = random.Random(seed)
    W_, H_ = w * T, h * T
    im = new(W_, H_)
    d = ImageDraw.Draw(im)
    acc = hx(theme["accent"])
    d.rectangle((0, 4, W_ - 1, H_ - 1), fill=(24, 32, 50, 255), outline=(8, 11, 20, 255))
    for y in range(8, H_ - 8):
        t = (y - 8) / max(1, (H_ - 16))
        d.line((4, y, W_ - 5, y), fill=mix(shade(acc, 0.8), shade(acc, 0.3), t))
    for _ in range(w * 6):
        bx = rnd.randrange(8, W_ - 8); by = rnd.randrange(12, H_ - 10)
        d.ellipse((bx, by, bx + 1, by + 1), fill=(220, 255, 250, 200))
    # silhuetas de criaturas
    for _ in range(max(1, w // 2)):
        cx = rnd.randrange(14, W_ - 14); cy = rnd.randrange(16, H_ - 16)
        c = shade(acc, 0.22)
        d.ellipse((cx - 7, cy - 4, cx + 7, cy + 4), fill=c)
        d.polygon([(cx + 6, cy), (cx + 12, cy - 5), (cx + 12, cy + 5)], fill=c)
        d.point((cx - 4, cy - 1), fill=(255, 255, 160, 255))
    d.rectangle((0, 0, W_ - 1, 8), fill=(40, 50, 74, 255), outline=(8, 11, 20, 255))
    d.line((1, 1, W_ - 2, 1), fill=(100, 116, 150, 255))
    d.line((6, 12, 6, H_ - 10), fill=(230, 245, 255, 90))
    glow_only(im, lambda dd, c: dd.rectangle((5, 10, W_ - 6, H_ - 8), fill=c), acc, 7, 0.4)
    return im

def deco_forklift(w, h, theme):
    W_, H_ = w * T, h * T
    im = new(W_, H_)
    d = ImageDraw.Draw(im)
    d.rectangle((6, 14, W_ - 7, H_ - 6), fill=(214, 150, 30, 255), outline=(60, 40, 8, 255))
    d.rectangle((10, 6, W_ - 20, 22), fill=(60, 70, 96, 255), outline=(12, 16, 28, 255))  # cabine
    d.rectangle((13, 9, W_ - 23, 18), fill=(120, 190, 230, 255))
    d.rectangle((W_ - 20, 4, W_ - 8, H_ - 8), fill=(90, 96, 112, 255), outline=(12, 16, 28, 255))  # mastro
    for yy in range(8, H_ - 10, 6):
        d.line((W_ - 19, yy, W_ - 9, yy), fill=(60, 66, 80, 255))
    for x in (8, W_ - 22):
        d.rectangle((x, H_ - 12, x + 12, H_ - 3), fill=(16, 18, 26, 255), outline=(60, 66, 80, 255))
    d.rectangle((16, 28, W_ - 26, 32), fill=(255, 235, 120, 255))
    d.line((8, 16, W_ - 9, 16), fill=(255, 200, 80, 255))
    return im

def deco_pod(w, h, theme, rats=1, seed=1):
    rnd = random.Random(seed)
    W_, H_ = w * T, h * T
    im = new(W_, H_)
    d = ImageDraw.Draw(im)
    acc = hx("#4fd6ff")
    d.rectangle((2, H_ - 14, W_ - 3, H_ - 2), fill=(34, 42, 62, 255), outline=(8, 11, 20, 255))
    d.rounded_rectangle((3, 4, W_ - 4, H_ - 12), radius=10, fill=shade(acc, 0.3), outline=(160, 200, 230, 255))
    for y in range(10, H_ - 14):
        t = (y - 10) / max(1, (H_ - 24))
        d.line((6, y, W_ - 7, y), fill=mix(shade(acc, 0.7), shade(acc, 0.25), t))
    # ratos presos (silhuetas)
    n = rats
    for i in range(n):
        cx = int(W_ * (i + 1) / (n + 1)); cy = H_ - 30 - i * 3
        c = (28, 24, 40, 255)
        d.ellipse((cx - 5, cy - 7, cx + 5, cy + 5), fill=c)
        d.ellipse((cx - 6, cy - 11, cx - 2, cy - 7), fill=c); d.ellipse((cx + 2, cy - 11, cx + 6, cy - 7), fill=c)
        d.point((cx - 2, cy - 4), fill=(255, 120, 150, 255)); d.point((cx + 2, cy - 4), fill=(255, 120, 150, 255))
        d.line((cx + 4, cy + 4, cx + 9, cy + 7), fill=(150, 70, 100, 255))
    d.rectangle((2, 0, W_ - 3, 7), fill=(44, 54, 80, 255), outline=(8, 11, 20, 255))
    d.line((3, 1, W_ - 4, 1), fill=(110, 126, 164, 255))
    d.line((7, 12, 7, H_ - 22), fill=(230, 245, 255, 120))
    glow_only(im, lambda dd, c: dd.rounded_rectangle((6, 10, W_ - 7, H_ - 16), radius=8, fill=c), acc, 6, 0.5)
    d.rectangle((6, H_ - 10, 9, H_ - 6), fill=(255, 70, 90, 255))
    return im

def deco_mixbench(w, h, theme, seed=1):
    rnd = random.Random(seed)
    W_, H_ = w * T, h * T
    im = new(W_, H_)
    d = ImageDraw.Draw(im)
    acc = hx(theme["accent"])
    d.rectangle((0, 18, W_ - 1, H_ - 2), fill=(38, 46, 70, 255), outline=(8, 11, 20, 255))
    d.rectangle((0, 12, W_ - 1, 24), fill=(70, 82, 116, 255), outline=(8, 11, 20, 255))
    d.line((1, 13, W_ - 2, 13), fill=(150, 166, 204, 255))
    # vidrarias
    x = 8
    while x < W_ - 24:
        kind = rnd.choice(["flask", "beaker", "tube"])
        col = rnd.choice([acc, (255, 80, 110, 255), (90, 255, 140, 255), (255, 200, 70, 255), (70, 170, 255, 255)])
        if kind == "flask":
            d.polygon([(x + 4, 2), (x + 8, 2), (x + 8, 8), (x + 14, 22), (x - 2, 22), (x + 4, 8)], fill=(150, 190, 220, 120), outline=(190, 220, 240, 255))
            d.polygon([(x + 1, 22), (x + 11, 22), (x + 13, 17), (x - 1, 17)], fill=col)
        elif kind == "beaker":
            d.rectangle((x, 6, x + 11, 22), fill=(150, 190, 220, 90), outline=(190, 220, 240, 255))
            d.rectangle((x + 1, 13, x + 10, 21), fill=col)
        else:
            for i in range(3):
                d.rectangle((x + i * 4, 4, x + i * 4 + 2, 22), fill=(150, 190, 220, 90), outline=(190, 220, 240, 255))
                d.rectangle((x + i * 4 + 1, 12 + i, x + i * 4 + 1, 21), fill=col)
        glow_only(im, lambda dd, c, col=col, x=x: dd.rectangle((x, 12, x + 12, 22), fill=col), col, 4, 0.6)
        x += 20 + rnd.randrange(0, 8)
    # queimador
    d.rectangle((W_ - 20, 12, W_ - 8, 24), fill=(18, 22, 36, 255), outline=(8, 11, 20, 255))
    d.ellipse((W_ - 17, 7, W_ - 11, 13), fill=(255, 140, 40, 255))
    glow_only(im, lambda dd, c: dd.ellipse((W_ - 20, 4, W_ - 8, 16), fill=c), (255, 140, 40, 255), 5, 0.8)
    for xx in range(6, W_ - 6, 24):
        d.rectangle((xx, H_ - 20, xx + 18, H_ - 6), fill=(20, 26, 42, 255), outline=(60, 72, 104, 255))
        d.rectangle((xx + 6, H_ - 16, xx + 12, H_ - 14), fill=acc)
    return im

def deco_cage_start(w, h, theme):
    W_, H_ = w * T, h * T
    im = new(W_, H_)
    d = ImageDraw.Draw(im)
    acc = hx(theme["accent"])
    d.rectangle((2, H_ - 14, W_ - 3, H_ - 2), fill=(30, 36, 54, 255), outline=(8, 11, 20, 255))
    d.rectangle((4, 4, W_ - 5, H_ - 12), fill=(8, 12, 22, 255))
    for x in range(8, W_ - 6, 8):
        d.line((x, 4, x, H_ - 14), fill=(120, 134, 168, 255), width=2)
    d.rectangle((2, 0, W_ - 3, 6), fill=(60, 70, 100, 255), outline=(8, 11, 20, 255))
    # porta aberta torta
    d.polygon([(W_ - 12, 10), (W_ - 2, 4), (W_ - 2, H_ - 20), (W_ - 12, H_ - 14)], outline=(160, 176, 210, 255))
    d.line((W_ - 12, 14, W_ - 4, 10), fill=(160, 176, 210, 255))
    # faíscas
    for (sx, sy) in ((W_ - 14, H_ - 22), (W_ - 18, H_ - 26), (W_ - 10, H_ - 28)):
        d.point((sx, sy), fill=(255, 240, 120, 255)); d.point((sx + 1, sy - 1), fill=(255, 255, 255, 255))
    d.rectangle((6, H_ - 12, 10, H_ - 9), fill=(255, 70, 90, 255))
    glow_only(im, lambda dd, c: dd.rectangle((6, H_ - 12, 10, H_ - 9), fill=c), (255, 70, 90, 255), 3, 0.9)
    return im

def deco_emitter(theme):
    im = new(T, T)
    d = ImageDraw.Draw(im)
    d.rectangle((6, 14, 25, 30), fill=(34, 42, 62, 255), outline=(8, 11, 20, 255))
    d.rectangle((9, 6, 22, 16), fill=(60, 72, 104, 255), outline=(8, 11, 20, 255))
    d.rectangle((13, 9, 18, 14), fill=(255, 60, 80, 255))
    glow_only(im, lambda dd, c: dd.rectangle((12, 8, 19, 15), fill=c), (255, 60, 80, 255), 5, 1.0)
    d.line((8, 26, 23, 26), fill=(255, 200, 60, 255))
    return im

def deco_sign(w, text, theme):
    W_, H_ = w * T, T
    im = new(W_, H_)
    acc = hx(theme["accent"])
    d = ImageDraw.Draw(im)
    tw = text_width(text, 2)
    x = (W_ - tw) // 2
    d.rounded_rectangle((x - 6, 6, x + tw + 5, 22), radius=2, fill=(8, 12, 22, 230), outline=shade(acc, 0.6))
    def f(dd, c): draw_text(dd, x, 9, text, c, 2)
    glow(im, f, acc, 3, 0.9)
    return im

def deco_pipe(w, theme, seed=1):
    rnd = random.Random(seed)
    W_ = w * T
    im = new(W_, T)
    d = ImageDraw.Draw(im)
    acc = hx(theme["accent"])
    for (y, col) in ((5, (60, 74, 104, 255)), (11, (48, 58, 84, 255))):
        d.rectangle((0, y, W_ - 1, y + 4), fill=col, outline=(10, 14, 24, 255))
        d.line((0, y + 1, W_ - 1, y + 1), fill=shade(col, 1.5))
    for x in range(10, W_ - 6, 38 + rnd.randrange(0, 12)):
        d.rectangle((x, 3, x + 4, 17), fill=(84, 98, 132, 255), outline=(10, 14, 24, 255))
        d.rectangle((x + 1, 8, x + 3, 10), fill=acc)
    return im

def deco_platform(w, h, theme):
    W_, H_ = w * T, h * T
    im = new(W_, H_)
    d = ImageDraw.Draw(im)
    acc = hx(theme["accent"])
    d.rounded_rectangle((0, 0, W_ - 1, H_ - 1), radius=14, fill=(18, 26, 46, 255), outline=shade(acc, 0.7), width=2)
    for x in range(8, W_ - 8, 16):
        d.line((x, 6, x, H_ - 7), fill=(30, 42, 70, 255))
    for y in range(8, H_ - 8, 16):
        d.line((6, y, W_ - 7, y), fill=(30, 42, 70, 255))
    d.ellipse((W_ // 2 - 26, H_ // 2 - 20, W_ // 2 + 26, H_ // 2 + 20), outline=acc, width=2)
    glow_only(im, lambda dd, c: dd.ellipse((W_ // 2 - 26, H_ // 2 - 20, W_ // 2 + 26, H_ // 2 + 20), outline=c, width=2), acc, 5, 1.0)
    return im

# ---------------------------------------------------------------- props dinâmicos
def spr_door_top(theme, state):
    """64x48. state: locked | unlocked | open | shutter_closed | shutter_open"""
    acc = hx(theme["accent"])
    im = new(64, 48)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 63, 47), fill=(40, 50, 76, 255), outline=(8, 11, 20, 255))
    d.rectangle((6, 6, 57, 47), fill=(8, 12, 22, 255))
    if state in ("open",):
        d.rectangle((8, 8, 55, 47), fill=(4, 6, 12, 255))
        for i in range(3):
            d.line((10 + i * 4, 10, 10 + i * 4, 47), fill=shade(acc, 0.4))
        glow_only(im, lambda dd, c: dd.rectangle((8, 8, 55, 47), fill=shade(c, 0.35)), acc, 8, 0.5)
        col = (80, 255, 130, 255)
    elif state == "shutter_open":
        d.rectangle((8, 8, 55, 47), fill=(4, 6, 12, 255))
        d.rectangle((8, 8, 55, 14), fill=(120, 126, 140, 255))
        for yy in range(8, 14, 2): d.line((8, yy, 55, yy), fill=(80, 86, 100, 255))
        col = (80, 255, 130, 255)
    elif state == "shutter_closed":
        d.rectangle((8, 8, 55, 47), fill=(100, 106, 122, 255))
        for yy in range(8, 47, 4): d.line((8, yy, 55, yy), fill=(66, 72, 86, 255)); d.line((8, yy + 1, 55, yy + 1), fill=(140, 146, 162, 255))
        for yy in range(30, 47, 4):
            d.rectangle((8, yy, 55, yy + 1), fill=(255, 200, 60, 255) if (yy // 4) % 2 == 0 else (30, 30, 36, 255))
        col = (255, 60, 80, 255)
    elif state == "locked":
        d.rectangle((8, 8, 55, 47), fill=(26, 30, 46, 255))
        d.line((32, 8, 32, 47), fill=(8, 11, 20, 255))
        for yy in range(12, 46, 6):
            d.line((10, yy, 30, yy), fill=(40, 48, 72, 255)); d.line((34, yy, 54, yy), fill=(40, 48, 72, 255))
        col = (255, 60, 80, 255)
    else:  # unlocked (fechada mas destrancada)
        d.rectangle((8, 8, 55, 47), fill=(26, 34, 52, 255))
        d.line((32, 8, 32, 47), fill=(8, 11, 20, 255))
        for yy in range(12, 46, 6):
            d.line((10, yy, 30, yy), fill=(46, 62, 92, 255)); d.line((34, yy, 54, yy), fill=(46, 62, 92, 255))
        col = acc
    # luzes laterais e indicador
    d.rectangle((2, 4, 5, 44), fill=shade(col, 0.55)); d.rectangle((58, 4, 61, 44), fill=shade(col, 0.55))
    d.rectangle((28, 2, 35, 5), fill=col)
    glow_only(im, lambda dd, c: [dd.rectangle((2, 4, 5, 44), fill=c), dd.rectangle((58, 4, 61, 44), fill=c), dd.rectangle((28, 2, 35, 5), fill=c)], col, 4, 0.9)
    return im

def spr_door_back(theme):
    im = new(64, 32)
    d = ImageDraw.Draw(im)
    g = (80, 255, 130, 255)
    d.rectangle((0, 8, 63, 31), fill=(34, 42, 64, 255), outline=(8, 11, 20, 255))
    d.rectangle((6, 12, 57, 31), fill=(6, 10, 18, 255))
    for i in range(3):
        x = 22 + i * 8
        d.polygon([(x, 16 + i), (x + 10, 16 + i), (x + 5, 24 + i)], fill=shade(g, 0.5 + i * 0.25))
    glow_only(im, lambda dd, c: dd.polygon([(22, 16), (42, 16), (32, 26)], fill=c), g, 5, 0.8)
    d.rectangle((2, 10, 5, 30), fill=shade(g, 0.5)); d.rectangle((58, 10, 61, 30), fill=shade(g, 0.5))
    return im

def spr_terminal(theme, active):
    acc = hx(theme["accent"])
    im = new(32, 44)
    d = ImageDraw.Draw(im)
    d.rectangle((3, 14, 28, 43), fill=(30, 38, 58, 255), outline=(8, 11, 20, 255))
    d.rectangle((2, 3, 29, 28), fill=(44, 54, 80, 255), outline=(8, 11, 20, 255))
    d.rectangle((5, 6, 26, 24), fill=(4, 10, 18, 255), outline=(100, 116, 156, 255))
    if active:
        for yy in range(8, 23, 3):
            d.line((7, yy, 7 + (yy * 7 % 14) + 4, yy), fill=acc)
    else:
        d.line((8, 10, 16, 10), fill=shade(acc, 0.7)); d.rectangle((8, 14, 10, 18), fill=acc)
    glow_only(im, lambda dd, c: dd.rectangle((5, 6, 26, 24), fill=shade(c, 0.5)), acc, 5, 0.7 if active else 0.45)
    for i in range(5):
        d.rectangle((6 + i * 4, 32, 8 + i * 4, 34), fill=(70, 84, 118, 255))
    d.rectangle((6, 37, 25, 40), fill=(14, 18, 30, 255))
    return im

def spr_console(theme, kind, on):
    """Console de parede (painel/vent/lasercon/console) 32x44."""
    acc = hx(theme["accent"])
    stc = (80, 255, 130, 255) if on else (255, 60, 80, 255)
    im = new(32, 44)
    d = ImageDraw.Draw(im)
    d.rectangle((3, 12, 28, 43), fill=(30, 38, 58, 255), outline=(8, 11, 20, 255))
    d.rectangle((2, 4, 29, 26), fill=(46, 56, 84, 255), outline=(8, 11, 20, 255))
    d.rectangle((5, 7, 26, 23), fill=(6, 10, 18, 255), outline=(100, 116, 156, 255))
    if kind == "panel":
        for i in range(3):
            d.rectangle((8 + i * 6, 11, 11 + i * 6, 19), fill=shade(stc, 0.5 + 0.25 * i))
    elif kind == "vent":
        d.ellipse((8, 9, 23, 22), outline=stc, width=2)
        for a in range(0, 360, 90):
            ar = math.radians(a + (20 if on else 0))
            d.line((15.5, 15.5, 15.5 + math.cos(ar) * 6, 15.5 + math.sin(ar) * 6), fill=stc)
    elif kind == "lasercon":
        d.line((8, 21, 23, 9), fill=stc, width=2)
        d.ellipse((6, 19, 10, 23), fill=stc); d.ellipse((21, 7, 25, 11), fill=stc)
    else:  # console
        d.polygon([(10, 12), (21, 12), (24, 18), (7, 18)], outline=stc)
        d.rectangle((13, 18, 18, 21), fill=stc)
    glow_only(im, lambda dd, c: dd.rectangle((5, 7, 26, 23), fill=shade(c, 0.45)), stc, 5, 0.7)
    d.rectangle((6, 30, 25, 33), fill=(14, 18, 30, 255))
    d.rectangle((13, 28, 18, 29), fill=stc)
    d.rectangle((7, 36, 24, 40), fill=(20, 26, 40, 255), outline=(60, 72, 104, 255))
    return im

def spr_locker(theme, opened):
    acc = hx(theme["accent"])
    im = new(32, 48)
    d = ImageDraw.Draw(im)
    d.rectangle((3, 4, 28, 46), fill=(44, 54, 82, 255), outline=(8, 11, 20, 255))
    d.line((4, 5, 27, 5), fill=(120, 136, 176, 255))
    if opened:
        d.rectangle((6, 8, 25, 44), fill=(6, 10, 18, 255))
        d.polygon([(25, 8), (31, 12), (31, 42), (25, 44)], fill=(60, 72, 104, 255), outline=(8, 11, 20, 255))
        for yy in (18, 28, 38): d.line((7, yy, 24, yy), fill=(30, 40, 62, 255))
    else:
        d.rectangle((6, 8, 25, 44), fill=(34, 42, 66, 255), outline=(70, 84, 120, 255))
        d.line((15, 8, 15, 44), fill=(10, 14, 24, 255))
        for yy in range(12, 40, 4):
            d.line((8, yy, 13, yy), fill=(20, 26, 42, 255)); d.line((18, yy, 23, yy), fill=(20, 26, 42, 255))
        d.rectangle((17, 24, 19, 28), fill=acc)
        glow_only(im, lambda dd, c: dd.rectangle((17, 24, 19, 28), fill=c), acc, 3, 0.9)
    d.rectangle((3, 44, 28, 47), fill=(14, 18, 30, 255))
    return im

def spr_ice(w=64, h=64):
    im = new(w, h)
    d = ImageDraw.Draw(im)
    rnd = random.Random(7)
    d.rectangle((0, 6, w - 1, h - 1), fill=(120, 190, 235, 255), outline=(30, 70, 120, 255))
    for y in range(6, h):
        t = (y - 6) / (h - 6)
        d.line((1, y, w - 2, y), fill=mix((190, 235, 255, 255), (70, 140, 210, 255), t))
    # cristais
    for i in range(8):
        x = rnd.randrange(4, w - 10); y = rnd.randrange(8, h - 20)
        d.polygon([(x, y + 14), (x + 4, y), (x + 8, y + 14)], fill=(225, 250, 255, 200), outline=(255, 255, 255, 220))
    for i in range(5):
        x1, y1 = rnd.randrange(w), rnd.randrange(6, h)
        d.line((x1, y1, x1 + rnd.randrange(-14, 14), y1 + rnd.randrange(-14, 14)), fill=(255, 255, 255, 150))
    d.line((2, 7, w - 3, 7), fill=(255, 255, 255, 255))
    glow_only(im, lambda dd, c: dd.rectangle((2, 8, w - 3, h - 3), fill=shade(c, 0.5)), (120, 210, 255, 255), 8, 0.6)
    return im

def spr_crystal(w=64, h=64, col=(255, 210, 60, 255)):
    im = new(w, h)
    d = ImageDraw.Draw(im)
    rnd = random.Random(9)
    base = [(2, h - 2), (8, 14), (16, 30), (22, 6), (30, 26), (38, 2), (44, 28), (52, 12), (58, 32), (w - 2, h - 2)]
    d.polygon(base, fill=shade(col, 0.55), outline=shade(col, 0.3))
    for i in range(7):
        x = rnd.randrange(4, w - 14); y = rnd.randrange(8, h - 24)
        d.polygon([(x, y + 22), (x + 6, y), (x + 12, y + 22)], fill=mix(col, (255, 255, 255, 255), 0.35), outline=shade(col, 0.4))
        d.line((x + 6, y + 2, x + 6, y + 20), fill=(255, 255, 255, 140))
    glow_only(im, lambda dd, c: dd.polygon(base, fill=c), col, 9, 0.7)
    return im

def spr_cage(theme, opened):
    w, h = 64, 64
    im = new(w, h)
    d = ImageDraw.Draw(im)
    d.rectangle((2, h - 12, w - 3, h - 2), fill=(34, 42, 62, 255), outline=(8, 11, 20, 255))
    d.rectangle((2, 0, w - 3, 8), fill=(60, 70, 100, 255), outline=(8, 11, 20, 255))
    d.line((3, 1, w - 4, 1), fill=(130, 146, 184, 255))
    for x in range(8, w - 6, 8):
        d.line((x, 8, x, h - 12), fill=(150, 166, 204, 255), width=2)
    if opened:
        d.rectangle((w // 2 - 8, 8, w // 2 + 8, h - 12), fill=(4, 8, 14, 255))
        d.polygon([(w // 2 + 8, 8), (w - 6, 14), (w - 6, h - 16), (w // 2 + 8, h - 12)], outline=(150, 166, 204, 255))
        col = (80, 255, 130, 255)
    else:
        col = (255, 60, 80, 255)
        d.rectangle((w // 2 - 4, h - 22, w // 2 + 4, h - 14), fill=(24, 30, 46, 255), outline=(8, 11, 20, 255))
    d.rectangle((6, h - 10, 10, h - 6), fill=col)
    glow_only(im, lambda dd, c: dd.rectangle((6, h - 10, 10, h - 6), fill=c), col, 3, 0.9)
    return im

def spr_crate(theme):
    acc = hx(theme["accent"])
    im = new(32, 32)
    d = ImageDraw.Draw(im)
    d.rectangle((1, 1, 30, 30), fill=(70, 82, 112, 255), outline=(8, 11, 20, 255))
    d.rectangle((4, 4, 27, 27), fill=(52, 62, 88, 255), outline=(100, 116, 156, 255))
    d.line((4, 4, 27, 27), fill=(34, 42, 64, 255)); d.line((27, 4, 4, 27), fill=(34, 42, 64, 255))
    d.rectangle((13, 13, 18, 18), fill=acc)
    for (x, y) in ((2, 2), (28, 2), (2, 28), (28, 28)):
        d.point((x, y), fill=(160, 176, 210, 255))
    glow_only(im, lambda dd, c: dd.rectangle((13, 13, 18, 18), fill=c), acc, 3, 0.9)
    return im

def spr_plate(theme, on):
    acc = hx(theme["accent"])
    col = (80, 255, 130, 255) if on else (255, 160, 40, 255)
    im = new(32, 32)
    d = ImageDraw.Draw(im)
    d.rectangle((3, 3, 28, 28), fill=(20, 26, 42, 255), outline=shade(col, 0.7), width=2)
    d.rectangle((9, 9, 22, 22), fill=shade(col, 0.5 if on else 0.28), outline=col)
    glow_only(im, lambda dd, c: dd.rectangle((8, 8, 23, 23), fill=c), col, 5, 0.9 if on else 0.4)
    return im

def spr_drone(frame):
    im = new(32, 32)
    d = ImageDraw.Draw(im)
    d.ellipse((6, 24, 26, 30), fill=(0, 0, 0, 90))  # sombra
    d.rounded_rectangle((7, 8, 24, 21), radius=4, fill=(60, 72, 104, 255), outline=(8, 11, 20, 255))
    d.rectangle((10, 11, 21, 17), fill=(10, 14, 24, 255))
    d.ellipse((13, 12, 18, 17), fill=(255, 50, 70, 255))
    glow_only(im, lambda dd, c: dd.ellipse((11, 10, 20, 19), fill=c), (255, 50, 70, 255), 5, 1.0)
    # hélices
    off = 2 if frame else 0
    d.line((2 + off, 9, 11, 9), fill=(160, 176, 210, 255)); d.line((20, 9, 29 - off, 9), fill=(160, 176, 210, 255))
    d.line((2 + off, 20, 11, 20), fill=(160, 176, 210, 255)); d.line((20, 20, 29 - off, 20), fill=(160, 176, 210, 255))
    d.line((9, 9, 9, 12), fill=(30, 36, 54, 255)); d.line((22, 9, 22, 12), fill=(30, 36, 54, 255))
    return im

def spr_mutant(frame):
    im = new(40, 40)
    d = ImageDraw.Draw(im)
    g = (80, 255, 120, 255)
    d.ellipse((6, 32, 34, 39), fill=(0, 0, 0, 90))
    wob = 1 if frame else 0
    d.ellipse((6, 8 - wob, 34, 34 + wob), fill=shade(g, 0.45), outline=shade(g, 0.2))
    d.ellipse((10, 10 - wob, 30, 24), fill=shade(g, 0.7))
    # olhos
    d.ellipse((12, 14, 18, 21), fill=(255, 255, 160, 255)); d.ellipse((22, 14, 28, 21), fill=(255, 255, 160, 255))
    d.point((15, 18), fill=(0, 0, 0, 255)); d.point((25, 18), fill=(0, 0, 0, 255))
    # boca com dentes
    d.line((12, 28, 28, 28), fill=(10, 30, 16, 255))
    for x in range(13, 28, 4):
        d.polygon([(x, 28), (x + 2, 28), (x + 1, 31)], fill=(230, 250, 230, 255))
    # tentáculos
    d.line((8, 30, 3, 36 + wob), fill=shade(g, 0.35), width=2); d.line((32, 30, 37, 36 + wob), fill=shade(g, 0.35), width=2)
    glow_only(im, lambda dd, c: dd.ellipse((6, 8, 34, 34), fill=c), g, 7, 0.55)
    return im

def spr_human(kind):
    """Pesquisador / cientista 32x56 (visto de frente)."""
    im = new(32, 56)
    d = ImageDraw.Draw(im)
    if kind == "scientist":
        coat = (230, 236, 246, 255); coat_s = (150, 160, 190, 255); trim = (255, 60, 80, 255); hair = (150, 150, 170, 255)
    else:
        coat = (200, 226, 244, 255); coat_s = (110, 150, 190, 255); trim = (60, 220, 255, 255); hair = (60, 40, 30, 255)
    d.ellipse((6, 50, 26, 56), fill=(0, 0, 0, 90))
    # pernas
    d.rectangle((10, 40, 14, 52), fill=(30, 34, 52, 255)); d.rectangle((17, 40, 21, 52), fill=(30, 34, 52, 255))
    d.rectangle((9, 51, 15, 53), fill=(12, 14, 24, 255)); d.rectangle((16, 51, 22, 53), fill=(12, 14, 24, 255))
    # jaleco
    d.polygon([(7, 20), (24, 20), (27, 46), (4, 46)], fill=coat, outline=(8, 11, 20, 255))
    d.line((16, 20, 16, 46), fill=coat_s)
    d.rectangle((12, 24, 14, 26), fill=trim)
    # braços
    d.rectangle((3, 22, 7, 38), fill=coat, outline=(8, 11, 20, 255)); d.rectangle((24, 22, 28, 38), fill=coat, outline=(8, 11, 20, 255))
    d.rectangle((3, 38, 7, 41), fill=(226, 180, 150, 255)); d.rectangle((24, 38, 28, 41), fill=(226, 180, 150, 255))
    # cabeça
    d.ellipse((9, 4, 23, 22), fill=(230, 188, 158, 255), outline=(8, 11, 20, 255))
    d.pieslice((8, 2, 24, 16), 180, 360, fill=hair)
    # óculos
    d.rectangle((10, 11, 15, 14), fill=(20, 24, 36, 255)); d.rectangle((17, 11, 22, 14), fill=(20, 24, 36, 255))
    d.line((15, 12, 17, 12), fill=(20, 24, 36, 255))
    d.point((12, 12), fill=(120, 230, 255, 255)); d.point((19, 12), fill=(120, 230, 255, 255))
    d.line((13, 18, 19, 18), fill=(150, 80, 70, 255))
    return im
