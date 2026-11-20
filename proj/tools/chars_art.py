# -*- coding: utf-8 -*-
"""Personagens humanos: Dr. Voss (cientista) e Dra. Okoye (pesquisadora). Desenhados em alta resolução e reduzidos.
Gera: assets/world/npc_scientist.png / npc_researcher.png (sprites do jogo) e assets/cut/*.png (cena de abertura)."""
import math, os
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_W = os.path.join(HERE, "..", "assets", "world")
OUT_C = os.path.join(HERE, "..", "assets", "cut")
S = 8
OL = (14, 12, 20, 255)


def c(r, g, b, a=255):
    return (r, g, b, a)


VOSS = dict(skin=c(226, 186, 160), skin_lo=c(190, 142, 120), hair=c(150, 156, 170), hair_hi=c(214, 220, 232), hair_lo=c(92, 98, 116),
            coat=c(228, 232, 240), coat_lo=c(168, 176, 196), coat_dk=c(110, 120, 148), trim=c(0, 240, 255), trim2=c(255, 0, 150),
            shirt=c(30, 34, 52), pants=c(36, 40, 60), shoes=c(18, 18, 26), glove=c(34, 36, 50), glasses=True, brow=c(110, 116, 132),
            eye=c(60, 150, 200), beard=True, lips=c(176, 110, 104))
OKOYE = dict(skin=c(138, 92, 66), skin_lo=c(104, 66, 46), hair=c(30, 22, 26), hair_hi=c(64, 48, 52), hair_lo=c(16, 12, 16),
             coat=c(214, 240, 236), coat_lo=c(150, 196, 190), coat_dk=c(90, 140, 140), trim=c(60, 255, 170), trim2=c(255, 200, 70),
             shirt=c(224, 120, 90), pants=c(40, 52, 70), shoes=c(30, 24, 30), glove=c(138, 92, 66), glasses=True, brow=c(30, 22, 26),
             eye=c(50, 30, 24), beard=False, lips=c(186, 90, 90))


class Cv:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.im = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
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

    def finish(self, outline=True):
        im = self.im.resize((self.w, self.h), Image.LANCZOS)
        a = im.split()[3].point(lambda v: 255 if v > 110 else 0)
        im.putalpha(a)
        if not outline:
            return im
        mask = a.filter(ImageFilter.MaxFilter(3))
        ol = Image.new("RGBA", im.size, OL)
        ol.putalpha(mask)
        res = Image.new("RGBA", im.size, (0, 0, 0, 0))
        res.alpha_composite(ol)
        res.alpha_composite(im)
        return res


def head_front(cv, st, cx, cy, s=1.0, mood="calm"):
    """Cabeça de frente; s = escala."""
    sk, sl = st["skin"], st["skin_lo"]
    cv.rect(cx - 3.4 * s, cy + 9 * s, cx + 3.4 * s, cy + 14 * s, sl)
    cv.ell(cx - 9.6 * s, cy + 0.5 * s, 1.8 * s, 2.6 * s, sk)
    cv.ell(cx + 9.6 * s, cy + 0.5 * s, 1.8 * s, 2.6 * s, sk)
    cv.ell(cx, cy, 9.6 * s, 11.2 * s, sk)
    cv.poly([(cx - 8 * s, cy + 3 * s), (cx + 8 * s, cy + 3 * s), (cx + 6 * s, cy + 9.5 * s), (cx, cy + 11.4 * s), (cx - 6 * s, cy + 9.5 * s)], sk)
    # barba por fazer / sombra
    if st["beard"]:
        cv.poly([(cx - 8.4 * s, cy + 3 * s), (cx - 6 * s, cy + 8 * s), (cx, cy + 11.6 * s), (cx + 6 * s, cy + 8 * s), (cx + 8.4 * s, cy + 3 * s), (cx + 5 * s, cy + 5 * s), (cx, cy + 6.5 * s), (cx - 5 * s, cy + 5 * s)], st["hair_lo"])
    # cabelo
    if st["hair"] == OKOYE["hair"]:
        # cabelo cacheado volumoso (afro)
        cv.ell(cx, cy - 6 * s, 13 * s, 12 * s, st["hair"])
        cv.ell(cx - 7 * s, cy - 3 * s, 6 * s, 8 * s, st["hair"])
        cv.ell(cx + 7 * s, cy - 3 * s, 6 * s, 8 * s, st["hair"])
        cv.poly([(cx - 9 * s, cy - 2 * s), (cx + 9 * s, cy - 2 * s), (cx + 8 * s, cy - 6 * s), (cx - 8 * s, cy - 6 * s)], st["hair"])
        for i in range(7):
            ang = math.pi * (0.1 + 0.8 * i / 6)
            cv.ell(cx + math.cos(ang + math.pi) * 9 * s, cy - 8 * s - math.sin(ang) * 8 * s, 1.6 * s, 1.6 * s, st["hair_hi"])
        cv.poly([(cx - 9 * s, cy - 4.4 * s), (cx + 9 * s, cy - 4.4 * s), (cx + 8.4 * s, cy - 1.4 * s), (cx - 8.4 * s, cy - 1.4 * s)], sk)
        cv.poly([(cx - 9.4 * s, cy - 5.5 * s), (cx - 4 * s, cy - 8.5 * s), (cx + 4 * s, cy - 8.5 * s), (cx + 9.4 * s, cy - 5.5 * s), (cx + 9 * s, cy - 4.2 * s), (cx - 9 * s, cy - 4.2 * s)], st["hair"])
    else:
        cv.poly([(cx - 10 * s, cy - 1 * s), (cx - 9 * s, cy - 8 * s), (cx - 4 * s, cy - 12 * s), (cx + 5 * s, cy - 12.4 * s), (cx + 10 * s, cy - 7 * s), (cx + 10 * s, cy - 1 * s),
                 (cx + 8 * s, cy - 4 * s), (cx + 2 * s, cy - 7.5 * s), (cx - 5 * s, cy - 6 * s), (cx - 8 * s, cy - 2 * s)], st["hair"])
        cv.poly([(cx - 3 * s, cy - 11.4 * s), (cx + 4 * s, cy - 11.8 * s), (cx + 8 * s, cy - 8 * s), (cx + 1 * s, cy - 8.4 * s)], st["hair_hi"])
        cv.poly([(cx - 10 * s, cy - 1 * s), (cx - 9.4 * s, cy + 3 * s), (cx - 8 * s, cy + 1 * s)], st["hair_lo"])
        cv.poly([(cx + 10 * s, cy - 1 * s), (cx + 9.4 * s, cy + 3 * s), (cx + 8 * s, cy + 1 * s)], st["hair_lo"])
    # sobrancelhas
    by = cy - 2.4 * s
    if mood == "worried":
        cv.line([(cx - 7 * s, by + 1.2 * s), (cx - 2 * s, by - 0.8 * s)], st["brow"], 1.1 * s)
        cv.line([(cx + 2 * s, by - 0.8 * s), (cx + 7 * s, by + 1.2 * s)], st["brow"], 1.1 * s)
    elif mood == "angry":
        cv.line([(cx - 7 * s, by - 0.8 * s), (cx - 2 * s, by + 1.2 * s)], st["brow"], 1.3 * s)
        cv.line([(cx + 2 * s, by + 1.2 * s), (cx + 7 * s, by - 0.8 * s)], st["brow"], 1.3 * s)
    else:
        cv.line([(cx - 7 * s, by), (cx - 2.4 * s, by - 0.4 * s)], st["brow"], 1.1 * s)
        cv.line([(cx + 2.4 * s, by - 0.4 * s), (cx + 7 * s, by)], st["brow"], 1.1 * s)
    # olhos
    ey = cy - 0.2 * s
    for sx in (-1, 1):
        ex = cx + sx * 4.4 * s
        cv.ell(ex, ey, 2.4 * s, 1.7 * s, c(246, 246, 250))
        cv.ell(ex + (0.4 * s if mood != "worried" else 0), ey + 0.1 * s, 1.15 * s, 1.35 * s, st["eye"])
        cv.ell(ex + 0.4 * s, ey + 0.1 * s, 0.55 * s, 0.7 * s, OL)
        cv.ell(ex + 0.9 * s, ey - 0.4 * s, 0.3 * s, 0.3 * s, c(255, 255, 255))
    # nariz
    cv.poly([(cx - 0.4 * s, cy + 0.6 * s), (cx + 1.6 * s, cy + 4.6 * s), (cx - 1.8 * s, cy + 4.6 * s)], st["skin_lo"])
    # boca
    my = cy + 7.4 * s
    if mood == "smile":
        cv.line([(cx - 3.6 * s, my - 0.4 * s), (cx, my + 1.6 * s), (cx + 3.6 * s, my - 0.4 * s)], st["lips"], 1.1 * s)
    elif mood == "angry" or mood == "worried":
        cv.line([(cx - 3 * s, my + 0.8 * s), (cx, my - 0.4 * s), (cx + 3 * s, my + 0.8 * s)], st["lips"], 1.2 * s)
    else:
        cv.line([(cx - 3 * s, my), (cx + 1 * s, my + 0.4 * s), (cx + 3.4 * s, my - 0.6 * s)], st["lips"], 1.1 * s)
    # óculos
    if st["glasses"]:
        gc = st["trim"]
        for sx in (-1, 1):
            gx = cx + sx * 4.4 * s
            cv.rrect(gx - 3.6 * s, ey - 2.6 * s, gx + 3.6 * s, ey + 2.6 * s, 0.8 * s, c(120, 200, 230, 70))
            cv.d.rounded_rectangle(((gx - 3.6 * s) * S, (ey - 2.6 * s) * S, (gx + 3.6 * s) * S, (ey + 2.6 * s) * S), radius=int(0.8 * s * S), outline=c(30, 34, 48), width=int(0.9 * s * S))
            cv.line([(gx - 2.6 * s, ey - 1.8 * s), (gx - 0.6 * s, ey - 2.0 * s)], c(255, 255, 255, 220), 0.5 * s)
        cv.line([(cx - 0.8 * s, ey - 0.4 * s), (cx + 0.8 * s, ey - 0.4 * s)], c(30, 34, 48), 0.9 * s)
        cv.line([(cx - 8 * s, ey - 0.8 * s), (cx - 9.8 * s, ey - 1.2 * s)], c(30, 34, 48), 0.8 * s)
        cv.line([(cx + 8 * s, ey - 0.8 * s), (cx + 9.8 * s, ey - 1.2 * s)], c(30, 34, 48), 0.8 * s)
        cv.line([(cx + 5.6 * s, ey + 2.3 * s), (cx + 8.4 * s, ey + 1.6 * s)], gc, 0.35 * s)


def body_front(cv, st, cx, top, arms="down", s=1.0):
    """Corpo de frente a partir do pescoço (top = y do ombro)."""
    y = top
    # pernas
    cv.rrect(cx - 11 * s, y + 52 * s, cx - 2 * s, y + 88 * s, 2 * s, st["pants"])
    cv.rrect(cx + 2 * s, y + 52 * s, cx + 11 * s, y + 88 * s, 2 * s, st["pants"])
    cv.rrect(cx - 12.5 * s, y + 84 * s, cx - 1 * s, y + 91 * s, 2.4 * s, st["shoes"])
    cv.rrect(cx + 1 * s, y + 84 * s, cx + 12.5 * s, y + 91 * s, 2.4 * s, st["shoes"])
    cv.rect(cx - 11 * s, y + 56 * s, cx - 9.4 * s, y + 84 * s, c(60, 66, 92))
    # camisa
    cv.poly([(cx - 8 * s, y), (cx + 8 * s, y), (cx + 10 * s, y + 44 * s), (cx - 10 * s, y + 44 * s)], st["shirt"])
    # jaleco
    cv.poly([(cx - 15 * s, y - 1 * s), (cx - 6 * s, y - 2 * s), (cx - 5 * s, y + 6 * s), (cx - 3 * s, y + 52 * s), (cx - 19 * s, y + 62 * s), (cx - 22 * s, y + 30 * s)], st["coat"])
    cv.poly([(cx + 15 * s, y - 1 * s), (cx + 6 * s, y - 2 * s), (cx + 5 * s, y + 6 * s), (cx + 3 * s, y + 52 * s), (cx + 19 * s, y + 62 * s), (cx + 22 * s, y + 30 * s)], st["coat"])
    cv.poly([(cx - 22 * s, y + 30 * s), (cx - 19 * s, y + 62 * s), (cx - 12 * s, y + 60 * s), (cx - 14 * s, y + 28 * s)], st["coat_lo"])
    cv.poly([(cx + 22 * s, y + 30 * s), (cx + 19 * s, y + 62 * s), (cx + 12 * s, y + 60 * s), (cx + 14 * s, y + 28 * s)], st["coat_lo"])
    # lapelas
    cv.poly([(cx - 6 * s, y - 2 * s), (cx - 1 * s, y + 10 * s), (cx - 5 * s, y + 22 * s), (cx - 9 * s, y + 6 * s)], st["coat_lo"])
    cv.poly([(cx + 6 * s, y - 2 * s), (cx + 1 * s, y + 10 * s), (cx + 5 * s, y + 22 * s), (cx + 9 * s, y + 6 * s)], st["coat_lo"])
    # detalhes neon
    cv.line([(cx - 3 * s, y + 24 * s), (cx - 3.4 * s, y + 52 * s)], st["trim"], 0.8 * s)
    cv.line([(cx + 3 * s, y + 24 * s), (cx + 3.4 * s, y + 52 * s)], st["trim"], 0.8 * s)
    cv.line([(cx - 19 * s, y + 61 * s), (cx - 4 * s, y + 52.6 * s)], st["trim2"], 0.9 * s)
    cv.line([(cx + 19 * s, y + 61 * s), (cx + 4 * s, y + 52.6 * s)], st["trim2"], 0.9 * s)
    # bolso com crachá
    cv.rect(cx + 8 * s, y + 20 * s, cx + 15 * s, y + 29 * s, st["coat_lo"])
    cv.rect(cx + 9 * s, y + 21 * s, cx + 13.5 * s, y + 24 * s, st["trim"])
    # cinto com frascos
    cv.rect(cx - 10 * s, y + 42 * s, cx + 10 * s, y + 45 * s, c(50, 38, 32))
    for i, col in enumerate([c(255, 80, 110), c(90, 255, 140), c(70, 170, 255)]):
        vx = cx - 7 * s + i * 4 * s
        cv.rrect(vx, y + 44 * s, vx + 2.6 * s, y + 49 * s, 0.8 * s, col)
    # braços
    if arms == "down":
        for sx in (-1, 1):
            ax = cx + sx * 21.5 * s
            cv.rrect(ax - 5 * s, y + 2 * s, ax + 5 * s, y + 46 * s, 4 * s, st["coat"])
            cv.rrect(ax - 5 * s, y + 38 * s, ax + 5 * s, y + 47 * s, 3 * s, st["coat_lo"])
            cv.ell(ax, y + 51 * s, 4.2 * s, 4.6 * s, st["glove"])
    return


def human_front(st, mood="calm", w=96, h=128):
    cv = Cv(w, h)
    cx = w // 2
    body_front(cv, st, cx, 36)
    head_front(cv, st, cx, 20, 1.0, mood)
    return cv


def portrait(st, mood="calm"):
    """Busto grande para diálogos e quadros."""
    cv = Cv(128, 128)
    cx = 64
    # ombros / jaleco
    cv.poly([(8, 128), (14, 100), (36, 90), (92, 90), (114, 100), (120, 128)], st["coat"])
    cv.poly([(40, 90), (52, 128), (64, 100), (76, 128), (88, 90), (72, 88), (56, 88)], st["shirt"])
    cv.poly([(34, 90), (54, 92), (62, 128), (44, 128)], st["coat_lo"])
    cv.poly([(94, 90), (74, 92), (66, 128), (84, 128)], st["coat_lo"])
    cv.line([(40, 94), (50, 128)], st["trim"], 1.2)
    cv.line([(88, 94), (78, 128)], st["trim"], 1.2)
    head_front(cv, st, cx, 52, 2.3, mood)
    return cv


def side_pour(st, mood="calm", w=128, h=128, flask_col=c(90, 255, 140)):
    """Perfil à direita, braço estendido derramando uma poção."""
    cv = Cv(w, h)
    cx = 50
    # pernas
    cv.rrect(cx - 9, 94, cx + 1, 126, 2, st["pants"])
    cv.rrect(cx - 1, 94, cx + 9, 126, 2, st["pants"])
    cv.rrect(cx - 10, 122, cx + 6, 128, 2.5, st["shoes"])
    cv.rrect(cx - 2, 122, cx + 14, 128, 2.5, st["shoes"])
    # tronco (jaleco) inclinado para frente
    cv.poly([(cx - 12, 52), (cx + 6, 48), (cx + 14, 70), (cx + 10, 108), (cx - 14, 112), (cx - 18, 76)], st["coat"])
    cv.poly([(cx - 18, 76), (cx - 14, 112), (cx - 4, 110), (cx - 8, 74)], st["coat_lo"])
    cv.line([(cx - 14, 111), (cx + 10, 107)], st["trim2"], 1.2)
    cv.rect(cx + 2, 66, cx + 8, 72, st["coat_lo"])
    # cabeça de perfil
    hx, hy = cx + 8, 36
    cv.rect(hx - 4, hy + 9, hx + 3, hy + 17, st["skin_lo"])
    cv.ell(hx, hy, 9, 11, st["skin"])
    cv.poly([(hx + 6, hy - 2), (hx + 12.5, hy + 4), (hx + 6, hy + 5.4)], st["skin"])
    cv.poly([(hx + 5, hy + 6), (hx + 8, hy + 12), (hx + 2, hy + 14), (hx - 4, hy + 8)], st["skin"])
    cv.poly([(hx - 3, hy + 8), (hx + 6, hy + 8), (hx + 7, hy + 13), (hx - 2, hy + 14)], st["hair_lo"]) if st["beard"] else None
    cv.poly([(hx - 10, hy + 2), (hx - 9, hy - 8), (hx - 2, hy - 13), (hx + 7, hy - 11), (hx + 9, hy - 5), (hx + 2, hy - 7), (hx - 4, hy - 5), (hx - 6, hy + 2)], st["hair"])
    cv.poly([(hx - 6, hy - 11.5), (hx + 4, hy - 11.5), (hx + 8, hy - 7), (hx - 2, hy - 8)], st["hair_hi"])
    cv.ell(hx - 3, hy + 1, 2, 3, st["skin_lo"])
    # óculos perfil + olho
    cv.ell(hx + 5.4, hy - 0.4, 2.2, 1.4, c(246, 246, 250))
    cv.ell(hx + 6, hy - 0.3, 0.9, 1.1, st["eye"])
    cv.rrect(hx + 2.8, hy - 3.2, hx + 9.6, hy + 2.6, 0.8, c(120, 200, 230, 90))
    cv.line([(hx + 2.8, hy - 1.4), (hx - 6, hy - 1.8)], c(30, 34, 48), 0.8)
    cv.line([(hx + 4, hy - 3.8), (hx + 9, hy - 3.2)], st["brow"], 1.0)
    cv.line([(hx + 6.5, hy + 6.6), (hx + 10.4, hy + 6.4)], st["lips"], 0.9)
    # braço estendido + frasco inclinado
    sx0, sy0 = cx + 6, 58
    ex, ey = cx + 30, 62
    cv.line([(sx0, sy0), (ex, ey)], st["coat"], 9)
    cv.line([(sx0 + 2, sy0 + 3), (ex, ey + 3)], st["coat_lo"], 3)
    cv.ell(ex + 3, ey, 4.4, 4.6, st["glove"])
    # frasco
    fx, fy = ex + 12, ey - 6
    ang = math.radians(48)
    def rot(px, py):
        dx, dy = px - fx, py - fy
        return (fx + dx * math.cos(ang) - dy * math.sin(ang), fy + dx * math.sin(ang) + dy * math.cos(ang))
    body = [rot(fx - 7, fy - 2), rot(fx + 7, fy - 2), rot(fx + 9, fy + 12), rot(fx - 9, fy + 12)]
    cv.poly([rot(fx - 3, fy - 12), rot(fx + 3, fy - 12), rot(fx + 4, fy - 2), rot(fx - 4, fy - 2)], c(190, 220, 235))
    cv.poly(body, c(190, 220, 235))
    cv.poly([rot(fx - 6, fy + 3), rot(fx + 6, fy + 3), rot(fx + 8, fy + 11), rot(fx - 8, fy + 11)], flask_col)
    cv.poly([rot(fx - 3.4, fy - 16), rot(fx + 3.4, fy - 16), rot(fx + 3, fy - 12), rot(fx - 3, fy - 12)], c(150, 90, 40))
    # fio de líquido caindo
    px, py = rot(fx - 3, fy - 15)
    cv.line([(px, py), (px - 1, py + 20), (px - 1.5, py + 34)], flask_col, 2.4)
    # outro braço (segurando béquer)
    cv.line([(cx - 6, 62), (cx + 14, 82), (cx + 34, 86)], st["coat"], 8)
    cv.ell(cx + 36, 86, 4.2, 4.4, st["glove"])
    return cv


def save(cv, folder, name, scale=1):
    im = cv.finish()
    os.makedirs(folder, exist_ok=True)
    if scale != 1:
        im = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
    im.save(os.path.join(folder, name))
    return im


def main():
    # sprites do jogo (mesmo tamanho dos antigos: ~ 40x56)
    for name, st in (("scientist", VOSS), ("researcher", OKOYE)):
        cv = human_front(st, "calm", 96, 128)
        im = cv.finish()
        im = im.resize((48, 64), Image.LANCZOS)
        a = im.split()[3].point(lambda v: 255 if v > 120 else 0)
        im.putalpha(a)
        os.makedirs(OUT_W, exist_ok=True)
        im.save(os.path.join(OUT_W, f"npc_{name}.png"))
    for mood in ("calm", "smile", "worried", "angry"):
        save(portrait(VOSS, mood), OUT_C, f"voss_{mood}.png")
        save(portrait(OKOYE, mood), OUT_C, f"okoye_{mood}.png")
    save(side_pour(VOSS), OUT_C, "voss_pour.png")
    save(human_front(VOSS, "calm"), OUT_C, "voss_front.png")
    save(human_front(VOSS, "angry"), OUT_C, "voss_front_angry.png")
    print("chars ok")


if __name__ == "__main__":
    main()
