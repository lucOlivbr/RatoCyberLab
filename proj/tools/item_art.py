# -*- coding: utf-8 -*-
"""Ícones em pixel art dos itens que não são moléculas químicas (e alguns produtos).
Uso: python3 tools/item_art.py  (escreve assets/icons/it_<id>.png e it_<id>_<n>.png para animados)"""
import math, os
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "assets", "icons")
S = 8
N = 48
OL = (14, 12, 20, 255)


def c(r, g, b, a=255):
    return (r, g, b, a)


STEEL = c(150, 166, 196); STEEL_HI = c(206, 220, 242); STEEL_LO = c(84, 96, 126); DARK = c(30, 34, 52)
ORANGE = c(255, 122, 58); ORANGE_HI = c(255, 200, 110); RED = c(255, 58, 85); RED_LO = c(150, 20, 44)
CYAN = c(77, 210, 255); CYAN_HI = c(190, 245, 255); CYAN_LO = c(30, 110, 160)
GREEN = c(77, 255, 154); GREEN_LO = c(24, 130, 80); GREEN_DK = c(14, 70, 52)
PURPLE = c(170, 92, 255); PURPLE_HI = c(214, 170, 255); PURPLE_LO = c(86, 40, 140)
YELLOW = c(255, 210, 58); YELLOW_HI = c(255, 244, 160); YELLOW_LO = c(160, 120, 20)
PINK = c(255, 92, 214); PINK_LO = c(140, 30, 110)
VIOLET = c(154, 140, 255); VIOLET_HI = c(220, 214, 255); VIOLET_LO = c(70, 56, 160)
GOLD = c(255, 200, 70); GOLD_HI = c(255, 240, 150); GOLD_LO = c(150, 100, 20)
WHITE = c(240, 250, 255)


class Cv:
    def __init__(self):
        self.im = Image.new("RGBA", (N * S, N * S), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.im)

    def P(self, pts):
        return [(x * S, y * S) for x, y in pts]

    def ell(self, cx, cy, rx, ry, col):
        self.d.ellipse(((cx - rx) * S, (cy - ry) * S, (cx + rx) * S, (cy + ry) * S), fill=col)

    def poly(self, pts, col):
        self.d.polygon(self.P(pts), fill=col)

    def rect(self, x0, y0, x1, y1, col):
        self.d.rectangle((x0 * S, y0 * S, x1 * S, y1 * S), fill=col)

    def rrect(self, x0, y0, x1, y1, r, col):
        self.d.rounded_rectangle((x0 * S, y0 * S, x1 * S, y1 * S), radius=r * S, fill=col)

    def line(self, pts, col, w):
        self.d.line(self.P(pts), fill=col, width=max(1, int(w * S)), joint="curve")
        r = w * S / 2
        for x, y in self.P(pts):
            self.d.ellipse((x - r, y - r, x + r, y + r), fill=col)

    def finish(self, glow=None):
        im = self.im.resize((N, N), Image.LANCZOS)
        a = im.split()[3].point(lambda v: 255 if v > 110 else 0)
        im.putalpha(a)
        mask = a.filter(ImageFilter.MaxFilter(3))
        ol = Image.new("RGBA", im.size, OL)
        ol.putalpha(mask)
        res = Image.new("RGBA", im.size, (0, 0, 0, 0))
        if glow is not None:
            g = Image.new("RGBA", im.size, glow)
            g.putalpha(a.filter(ImageFilter.GaussianBlur(3)).point(lambda v: int(v * 0.55)))
            res.alpha_composite(g)
        res.alpha_composite(ol)
        res.alpha_composite(im)
        return res


def gear(cv, cx, cy, r, teeth, col, hi, lo, hole=0.35):
    pts = []
    for i in range(teeth * 2):
        a0 = math.pi * i / teeth
        rr = r if i % 2 == 0 else r * 0.76
        for da in (-0.3, 0.3):
            aa = a0 + da * math.pi / teeth
            pts.append((cx + math.cos(aa) * rr, cy + math.sin(aa) * rr))
    cv.poly(pts, col)
    cv.ell(cx, cy, r * 0.62, r * 0.62, lo)
    cv.ell(cx, cy, r * 0.56, r * 0.56, col)
    cv.ell(cx - r * 0.12, cy - r * 0.12, r * 0.3, r * 0.3, hi)
    cv.ell(cx, cy, r * hole, r * hole, c(20, 24, 38))


# --------------------------------------------------------------- itens
def engrenagem(p=0.0):
    cv = Cv()
    gear(cv, 22, 25, 16, 8, STEEL, STEEL_HI, STEEL_LO)
    gear(cv, 37, 12, 8, 6, STEEL_LO, STEEL, c(50, 58, 80), 0.32)
    return cv.finish()


def nucleo(p=0.0):
    cv = Cv()
    pulse = 0.5 + 0.5 * math.sin(p * 2 * math.pi)
    cv.rrect(10, 33, 38, 41, 3, STEEL_LO)
    cv.rrect(12, 34, 36, 37, 1.5, STEEL)
    cv.ell(24, 22, 14, 14, c(120, 40, 20))
    cv.ell(24, 22, 11.5 + pulse * 0.8, 11.5 + pulse * 0.8, ORANGE)
    cv.ell(24, 22, 7.5 + pulse * 0.8, 7.5 + pulse * 0.8, ORANGE_HI)
    cv.ell(22, 19, 3, 3, c(255, 250, 220))
    for a in range(4):
        ang = math.pi / 4 + a * math.pi / 2
        x0, y0 = 24 + math.cos(ang) * 12, 22 + math.sin(ang) * 12
        x1, y1 = 24 + math.cos(ang) * 17, 22 + math.sin(ang) * 17
        cv.line([(x0, y0), (x1, y1)], STEEL, 2.4)
    return cv.finish(glow=(255, 120, 40, 255))


def celula(p=0.0):
    cv = Cv()
    pulse = 0.5 + 0.5 * math.sin(p * 2 * math.pi)
    cv.rrect(14, 10, 34, 41, 4, STEEL_LO)
    cv.rect(20, 6, 28, 11, STEEL)
    cv.rrect(16, 13, 32, 38, 3, c(14, 40, 62))
    h = 20 + pulse * 3
    cv.rrect(18, 36 - h, 30, 36, 2, CYAN)
    cv.rrect(18, 36 - h, 30, 36 - h + 3, 1, CYAN_HI)
    cv.poly([(26, 15), (20, 26), (24, 26), (22, 35), (30, 23), (26, 23), (28, 15)], c(255, 250, 200))
    return cv.finish(glow=(77, 210, 255, 255))


def polimero(p=0.0):
    cv = Cv()
    cv.rrect(11, 17, 37, 41, 5, PURPLE_LO)
    cv.rrect(13, 22, 35, 39, 4, PURPLE)
    cv.ell(24, 22, 11, 3, PURPLE_HI)
    cv.rect(16, 11, 32, 18, STEEL)
    cv.rect(16, 11, 32, 13, STEEL_HI)
    cv.ell(19, 30, 2.4, 3.4, PURPLE_HI)
    cv.ell(29, 33, 1.6, 1.6, PURPLE_HI)
    cv.poly([(22, 22), (26, 22), (26, 34), (24, 38), (22, 34)], c(120, 60, 200))
    return cv.finish()


def catalisador(p=0.0):
    cv = Cv()
    cv.rect(21, 6, 27, 18, c(180, 210, 230, 255))
    cv.poly([(21, 17), (27, 17), (38, 40), (10, 40)], c(150, 190, 215, 255))
    cv.poly([(15, 31), (33, 31), (38, 40), (10, 40)], YELLOW)
    cv.poly([(15, 31), (33, 31), (34, 33), (14, 33)], YELLOW_HI)
    cv.rect(20, 5, 28, 8, STRAP) if False else cv.rect(20, 5, 28, 8, c(120, 80, 40))
    for (x, y) in ((20, 35), (27, 37), (24, 33)):
        cv.ell(x, y, 1.1, 1.1, YELLOW_HI)
    cv.poly([(36, 12), (37.5, 15), (41, 16), (37.5, 17), (36, 20), (34.5, 17), (31, 16), (34.5, 15)], YELLOW_HI)
    return cv.finish()


def circuito(p=0.0):
    cv = Cv()
    cv.rrect(6, 10, 42, 38, 3, GREEN_LO)
    cv.rrect(8, 12, 40, 36, 2, GREEN_DK)
    for y in (16, 22, 28, 33):
        cv.line([(9, y), (18, y), (21, y + 3)], GREEN, 1.0)
    for y in (15, 21, 27, 32):
        cv.line([(39, y), (30, y), (28, y + 3)], GREEN, 1.0)
    cv.rrect(18, 17, 30, 29, 1.5, c(26, 26, 36))
    cv.rect(19, 18, 29, 19.5, c(70, 70, 96))
    cv.ell(21, 27, 1, 1, GOLD)
    for x in (9, 12, 36, 39):
        cv.ell(x, 12.5, 1.1, 1.1, GOLD)
        cv.ell(x, 35.5, 1.1, 1.1, GOLD)
    cv.ell(34, 22, 2.2, 2.2, YELLOW)
    return cv.finish()


def cristal(p=0.0):
    cv = Cv()
    cv.poly([(24, 4), (35, 14), (31, 40), (17, 40), (13, 14)], VIOLET)
    cv.poly([(24, 4), (35, 14), (24, 18)], VIOLET_HI)
    cv.poly([(24, 4), (13, 14), (24, 18)], c(190, 180, 255))
    cv.poly([(24, 18), (35, 14), (31, 40), (24, 40)], VIOLET_LO)
    cv.poly([(24, 18), (13, 14), (17, 40), (24, 40)], c(110, 96, 220))
    cv.line([(24, 18), (24, 38)], VIOLET_HI, 0.8)
    cv.poly([(38, 6), (39.5, 9), (43, 10), (39.5, 11), (38, 14), (36.5, 11), (33, 10), (36.5, 9)], WHITE)
    return cv.finish(glow=(154, 140, 255, 255))


def modulo_gen(p=0.0):
    cv = Cv()
    cv.rrect(7, 8, 41, 40, 4, c(40, 20, 52))
    cv.rrect(9, 10, 39, 38, 3, c(24, 12, 34))
    for i in range(10):
        t = i / 9
        y = 12 + t * 24
        x1 = 24 + math.sin(t * 6.0 + p * 6.28) * 9
        x2 = 24 - math.sin(t * 6.0 + p * 6.28) * 9
        cv.line([(x1, y), (x2, y)], PINK_LO, 1.0)
        cv.ell(x1, y, 1.8, 1.6, PINK)
        cv.ell(x2, y, 1.8, 1.6, CYAN)
    for x in (12, 18, 24, 30, 36):
        cv.rect(x - 1, 40, x + 1, 44, GOLD)
    return cv.finish(glow=(255, 92, 214, 255))


def key_shape(cv, col, hi, lo, head_r=9, teeth=3, rot=0.0, gem=None):
    cx, cy = 14 + rot, 14
    # haste
    cv.rrect(cx + 2, cy + 5, cx + 8, cy + 31, 2.5, col)
    cv.rect(cx + 2, cy + 5, cx + 4, cy + 31, hi)
    # dentes
    for i in range(teeth):
        y = cy + 18 + i * 5.5
        cv.rect(cx + 8, y, cx + 15 - (i % 2) * 3, y + 3.5, col)
    # cabeça (engrenagem vazada)
    gear(cv, cx + 5, cy + 3, head_r, 8, col, hi, lo, 0.38)
    if gem:
        cv.ell(cx + 5, cy + 3, 3.2, 3.2, gem)
        cv.ell(cx + 4, cy + 2, 1.2, 1.2, WHITE)


def chave_manut(p=0.0):
    cv = Cv()
    bob = math.sin(p * 2 * math.pi) * 1.2
    key_shape(cv, c(140, 205, 255), c(214, 240, 255), c(70, 120, 180), 9, 3, rot=bob)
    # brilho que passa
    gx = 8 + p * 30
    cv.poly([(gx, 6), (gx + 3, 6), (gx - 4, 44), (gx - 7, 44)], c(255, 255, 255, 90))
    return cv.finish(glow=(143, 208, 255, 255))


def chave_mestra(p=0.0):
    cv = Cv()
    bob = math.sin(p * 2 * math.pi) * 1.0
    key_shape(cv, GOLD, GOLD_HI, GOLD_LO, 10, 4, rot=bob, gem=c(255, 70, 120))
    gx = 8 + p * 30
    cv.poly([(gx, 6), (gx + 3, 6), (gx - 4, 44), (gx - 7, 44)], c(255, 255, 255, 100))
    return cv.finish(glow=(255, 210, 58, 255))


def termico(p=0.0):
    cv = Cv()
    pulse = 0.5 + 0.5 * math.sin(p * 2 * math.pi)
    # corpo do dispositivo
    cv.rrect(6, 20, 30, 34, 4, c(70, 76, 98))
    cv.rrect(8, 22, 28, 27, 2, STEEL)
    cv.rrect(28, 22, 40, 32, 3, STEEL_LO)
    cv.rrect(38, 23, 43, 31, 2, c(60, 20, 20))
    # bocal incandescente
    cv.ell(42, 27, 3 + pulse, 5 + pulse, ORANGE)
    cv.ell(42, 27, 1.8, 3, ORANGE_HI)
    # cabo
    cv.rrect(10, 33, 20, 44, 3, c(50, 54, 74))
    cv.rrect(12, 35, 18, 42, 2, c(90, 96, 120))
    # visor de temperatura
    cv.rrect(10, 28, 24, 32, 1, c(20, 14, 18))
    cv.rect(11, 29, 11 + 11 * (0.4 + 0.6 * pulse), 31, ORANGE)
    # ondas de calor
    for i in range(3):
        y = 12 + i * 3
        cv.line([(33 + i, y + 5), (36 + i, y + 2), (39 + i, y + 5), (42 + i, y + 2)], c(255, 170, 90, 200), 0.9)
    return cv.finish(glow=(255, 122, 58, 255))


def modulo_eletrico(p=0.0):
    cv = Cv()
    cv.rrect(7, 10, 41, 38, 4, c(24, 52, 84))
    cv.rrect(9, 12, 39, 36, 3, c(14, 30, 54))
    cv.rect(9, 12, 39, 15, c(40, 90, 140))
    cv.poly([(26, 15), (17, 26), (23, 26), (20, 35), (31, 22), (25, 22), (28, 15)], c(255, 240, 120))
    for x in (11, 16, 21, 26, 31, 36):
        cv.rect(x - 1, 38, x + 1, 43, GOLD)
    cv.ell(13, 33, 1.3, 1.3, CYAN)
    cv.ell(35, 33, 1.3, 1.3, CYAN)
    return cv.finish(glow=(77, 210, 255, 255))


def filtro(p=0.0):
    cv = Cv()
    cv.rrect(12, 8, 36, 42, 5, c(30, 80, 62))
    cv.rrect(14, 12, 34, 38, 3, c(14, 40, 34))
    for y in range(15, 37, 4):
        cv.line([(15, y), (33, y)], GREEN, 1.0)
    for x in range(17, 33, 4):
        cv.line([(x, 14), (x, 37)], GREEN_LO, 0.7)
    cv.rect(10, 6, 38, 10, STEEL)
    cv.rect(10, 6, 38, 7.5, STEEL_HI)
    cv.rect(10, 40, 38, 44, STEEL_LO)
    cv.poly([(24, 20), (30, 26), (26, 26), (26, 33), (22, 33), (22, 26), (18, 26)], c(180, 255, 210))
    return cv.finish(glow=(80, 255, 130, 255))


def solvente(p=0.0):
    cv = Cv()
    cv.ell(24, 30, 14, 12, c(80, 40, 130))
    cv.rect(20, 8, 28, 20, c(180, 210, 230, 255))
    cv.rect(19, 5, 29, 9, c(120, 80, 40))
    cv.ell(24, 30, 12, 10, PURPLE)
    cv.ell(24, 33, 10, 7, c(130, 60, 220))
    cv.ell(19, 27, 3, 2, PURPLE_HI)
    cv.line([(30, 36), (34, 41)], PURPLE, 1.6)
    cv.ell(35, 43, 1.6, 2, PURPLE)
    cv.poly([(24, 22), (26, 26), (30, 26), (27, 29), (28, 33), (24, 31), (20, 33), (21, 29), (18, 26), (22, 26)], c(255, 255, 255, 140))
    return cv.finish(glow=(192, 92, 255, 255))


def modulo_contencao(p=0.0):
    cv = Cv()
    pts = [(24 + math.cos(math.pi / 3 * i + math.pi / 6) * 18, 24 + math.sin(math.pi / 3 * i + math.pi / 6) * 18) for i in range(6)]
    cv.poly(pts, RED_LO)
    pts2 = [(24 + math.cos(math.pi / 3 * i + math.pi / 6) * 14.5, 24 + math.sin(math.pi / 3 * i + math.pi / 6) * 14.5) for i in range(6)]
    cv.poly(pts2, c(40, 14, 28))
    cv.ell(24, 24, 8.5, 8.5, RED)
    cv.ell(24, 24, 5.5, 5.5, c(255, 150, 160))
    cv.ell(22.5, 22.5, 2, 2, WHITE)
    for a in range(6):
        ang = math.pi / 3 * a
        cv.line([(24 + math.cos(ang) * 9, 24 + math.sin(ang) * 9), (24 + math.cos(ang) * 14, 24 + math.sin(ang) * 14)], c(255, 100, 120), 1.2)
    return cv.finish(glow=(255, 58, 85, 255))


def disp_resgate(p=0.0):
    cv = Cv()
    cv.rrect(10, 14, 38, 42, 5, c(30, 70, 60))
    cv.rrect(12, 16, 36, 40, 4, c(16, 36, 34))
    cv.rrect(15, 19, 33, 28, 2, c(10, 20, 24))
    cv.poly([(24, 20), (31, 25), (26, 25), (26, 27), (22, 27), (22, 25), (17, 25)], GREEN)
    cv.ell(19, 34, 2.4, 2.4, GREEN)
    cv.ell(29, 34, 2.4, 2.4, YELLOW)
    cv.line([(24, 14), (24, 7), (29, 4)], STEEL, 1.6)
    cv.ell(30, 3.5, 2.2, 2.2, GREEN)
    return cv.finish(glow=(80, 255, 130, 255))


def bomba(p=0.0):
    cv = Cv()
    pulse = 0.5 + 0.5 * math.sin(p * 2 * math.pi)
    cv.ell(24, 28, 15, 14, c(34, 36, 52))
    cv.ell(24, 28, 13, 12, c(52, 56, 78))
    cv.ell(19, 22, 4, 3, c(120, 128, 160))
    cv.rect(18, 8, 30, 15, STEEL_LO)
    cv.line([(24, 8), (28, 3), (33, 4)], c(150, 100, 50), 1.4)
    cv.ell(34, 4, 2 + pulse, 2 + pulse, ORANGE_HI)
    cv.rrect(15, 27, 33, 35, 2, c(10, 10, 16))
    cv.rect(17, 29, 17 + 14 * pulse, 33, RED)
    cv.line([(15, 22), (33, 22)], RED_LO, 1.0)
    return cv.finish(glow=(255, 58, 85, 255))


def acido(p=0.0):
    cv = Cv()
    cv.rect(20, 6, 28, 18, c(190, 220, 235, 255))
    cv.rect(19, 4, 29, 8, c(120, 80, 40))
    cv.ell(24, 31, 14, 12, c(110, 130, 60))
    cv.ell(24, 31, 12, 10, c(210, 232, 90))
    cv.ell(24, 34, 10, 7, c(150, 190, 40))
    cv.ell(19, 28, 3, 2, c(250, 255, 190))
    cv.poly([(24, 24), (28, 31), (20, 31)], c(30, 36, 20))
    cv.rect(23.2, 26, 24.8, 29, c(210, 232, 90))
    cv.ell(24, 30, 0.9, 0.9, c(210, 232, 90))
    return cv.finish(glow=(230, 232, 106, 255))


STATIC = {"engrenagem": engrenagem, "polimero": polimero, "catalisador": catalisador, "circuito": circuito, "cristal": cristal,
          "filtro": filtro, "solvente": solvente, "modulo_contencao": modulo_contencao, "disp_resgate": disp_resgate,
          "modulo_eletrico": modulo_eletrico, "acido": acido}
ANIM = {"chave_manut": chave_manut, "chave_mestra": chave_mestra, "nucleo": nucleo, "celula": celula,
        "modulo_gen": modulo_gen, "termico": termico, "bomba": bomba}


def main():
    os.makedirs(OUT, exist_ok=True)
    for k, f in STATIC.items():
        f(0.0).save(os.path.join(OUT, f"it_{k}.png"))
    for k, f in ANIM.items():
        for i in range(4):
            f(i / 4.0).save(os.path.join(OUT, f"it_{k}_{i}.png"))
    print("item art ok")


if __name__ == "__main__":
    main()
