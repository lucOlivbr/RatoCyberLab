# -*- coding: utf-8 -*-
"""Arte do final: logotipo LIBERDADE (letras cyberpunk) e a cena do rato fugindo com vários ratos normais."""
import os, math, random
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import title_art as TA

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "assets")
SPR = os.path.join(OUT, "sprites")

TA.G.update({
    "L": [[(0, 0), (0, 6), (4, 6)]],
    "I": [[(0, 0), (4, 0)], [(2, 0), (2, 6)], [(0, 6), (4, 6)]],
    "B": [[(0, 6), (0, 0), (3, 0), (4, 1), (4, 2), (3, 3), (0, 3)], [(3, 3), (4, 4), (4, 5), (3, 6), (0, 6)]],
    "D": [[(0, 0), (0, 6), (3, 6), (4, 5), (4, 1), (3, 0), (0, 0)]],
    "A": [[(0, 6), (0, 1), (1, 0), (3, 0), (4, 1), (4, 6)], [(0, 3), (4, 3)]],
})


def build_liberdade():
    t = TA.draw_text("LIBERDADE", 22, 15, lambda i: TA.RED if i == 0 else TA.YELLOW, gap=0.9, shear=0.2)
    pad = 28
    W, H = t.width + pad * 2, t.height + pad * 2
    base = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    base.alpha_composite(t, (pad, pad))
    shadow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    for k in range(7, 0, -1):
        layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
        layer.alpha_composite(base, (k, k))
        tint = Image.new("RGBA", base.size, (120, 98, 0, 255))
        tint.putalpha(layer.split()[3])
        shadow.alpha_composite(tint)
    res = Image.new("RGBA", base.size, (0, 0, 0, 0))
    res.alpha_composite(TA.glow(base, (255, 220, 0, 255), 16, 0.6))
    res.alpha_composite(TA.outline(shadow, 3, TA.DARK))
    res.alpha_composite(shadow)
    cy = Image.new("RGBA", base.size, TA.CYAN); cy.putalpha(base.split()[3].point(lambda v: int(v * 0.8)))
    mg = Image.new("RGBA", base.size, TA.MAGENTA); mg.putalpha(base.split()[3].point(lambda v: int(v * 0.8)))
    res.alpha_composite(cy, (-3, -2))
    res.alpha_composite(mg, (3, 2))
    res.alpha_composite(TA.outline(base, 2, TA.DARK))
    res.alpha_composite(base)
    a = base.split()[3]
    band = Image.new("L", base.size, 0)
    ImageDraw.Draw(band).rectangle((0, 0, W, int(H * 0.3)), fill=70)
    band = ImageChops.multiply(band, a)
    hi = Image.new("RGBA", base.size, (255, 255, 255, 255))
    hi.putalpha(band)
    res.alpha_composite(hi)
    for yy, off in ((int(H * 0.60), 7), (int(H * 0.66), -6)):
        row = res.crop((0, yy, W, yy + 3))
        res.paste((0, 0, 0, 0), (0, yy, W, yy + 3))
        res.alpha_composite(row, (off, yy))
    res.save(os.path.join(OUT, "ui", "liberdade_logo.png"))
    print("logo", res.size)


# ---------------------------------------------------------------- ratos normais
S = 8


def plain_rat(color, pose=0):
    """Rato comum de lado, olhando para a direita, em galope. pose 0..3."""
    W, H = 72, 40
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    color = tuple(color[:3])
    body = color + (255,)
    dark = tuple(int(c * 0.65) for c in color) + (255,)
    belly = tuple(min(255, int(c * 1.25) + 15) for c in color) + (255,)
    ph = pose / 4.0 * math.tau
    ext = math.sin(ph)
    def E(x0, y0, x1, y1, f):
        d.ellipse((x0 * S, y0 * S, x1 * S, y1 * S), fill=f)
    # cauda
    pts = [(20, 24), (12, 26 + 2 * ext), (6, 22 + 3 * ext), (2, 17 + 4 * ext)]
    d.line([(x * S, y * S) for x, y in pts], fill=(228, 150, 160, 255), width=int(2.2 * S), joint="curve")
    # patas traseiras e dianteiras (galope)
    legs = [(24, 27, -1), (28, 28, 1), (44, 28, -1), (48, 27, 1)]
    for i, (lx, ly, sg) in enumerate(legs):
        sw = math.sin(ph + i * 1.6) * 5
        d.line([((lx) * S, ly * S), ((lx + sw) * S, (ly + 7) * S)], fill=dark, width=int(3.2 * S))
        E(lx + sw - 2, ly + 5, lx + sw + 3, ly + 9, dark)
    # corpo
    E(18, 13 + 0.6 * ext, 52, 32 + 0.6 * ext, body)
    E(22, 24, 48, 32, belly)
    # cabeça
    E(44, 12, 62, 28, body)
    d.polygon([(58 * S, 15 * S), (71 * S, 21 * S), (58 * S, 27 * S)], fill=body)
    E(68, 19, 72, 23, (240, 140, 160, 255))
    # orelha
    E(46, 6, 56, 17, (232, 150, 165, 255))
    E(47.5, 7.5, 54.5, 15.5, tuple(min(255, int(c * 1.1)) for c in color) + (255,))
    # olho
    E(56, 17, 59, 20, (10, 10, 14, 255))
    E(57, 17.2, 58.2, 18.4, (255, 255, 255, 255))
    im = im.resize((W, H), Image.LANCZOS)
    a = im.split()[3].point(lambda v: 255 if v > 100 else 0)
    im.putalpha(a)
    mask = a.filter(ImageFilter.MaxFilter(3))
    ol = Image.new("RGBA", (W, H), (10, 10, 18, 255))
    ol.putalpha(mask)
    ol.alpha_composite(im)
    return ol.crop(ol.getbbox())


def radial(w, h, col, a):
    im = Image.new("RGBA", (w, h), col + (0,))
    px = im.load()
    for y in range(h):
        for x in range(w):
            dx = (x - w / 2) / (w / 2); dy = (y - h / 2) / (h / 2)
            r = math.sqrt(dx * dx + dy * dy)
            px[x, y] = col + (int(max(0.0, 1 - r) ** 1.6 * a),)
    return im


def build_scene():
    W, H = 960, 540
    rnd = random.Random(21)
    im = Image.new("RGBA", (W, H), (6, 6, 16, 255))
    d = ImageDraw.Draw(im)
    for y in range(H):
        t = y / H
        c = tuple(int(a + (b - a) * t) for a, b in zip((8, 6, 30), (60, 18, 40)))
        d.line((0, y, W, y), fill=c + (255,))
    for _ in range(120):
        d.point((rnd.randrange(W), rnd.randrange(0, 260)), fill=(255, 255, 255, rnd.randrange(80, 255)))
    # skyline distante (neon)
    x = 380
    while x < W:
        bw = rnd.randrange(30, 80); bh = rnd.randrange(80, 210)
        d.rectangle((x, 380 - bh, x + bw, 400), fill=(14, 12, 34, 255))
        for wy in range(380 - bh + 8, 392, 11):
            for wx in range(x + 5, x + bw - 6, 9):
                if rnd.random() < 0.25:
                    d.rectangle((wx, wy, wx + 3, wy + 4), fill=rnd.choice([(25, 230, 255, 255), (255, 60, 150, 255), (255, 210, 60, 255)]))
        x += bw + rnd.randrange(0, 6)
    # laboratório em chamas (esquerda)
    lab = (40, 130, 360, 400)
    im.alpha_composite(radial(700, 520, (255, 110, 20), 150), (-250, -40))
    d = ImageDraw.Draw(im)
    d.rectangle(lab, fill=(18, 20, 34, 255), outline=(60, 70, 100, 255), width=3)
    for wy in range(lab[1] + 18, lab[3] - 60, 34):
        for wx in range(lab[0] + 16, lab[2] - 16, 40):
            lit = rnd.random()
            d.rectangle((wx, wy, wx + 24, wy + 18), fill=(255, int(120 + 110 * lit), 30, 255) if lit > 0.3 else (40, 44, 64, 255))
    d.rectangle((180, 330, 230, 400), fill=(8, 6, 10, 255))   # porta por onde os ratos saem
    d.rectangle((lab[0] - 6, lab[1] - 10, lab[2] + 6, lab[1] + 4), fill=(40, 48, 70, 255))
    # fumaça e fogo
    for k in range(40):
        cx = rnd.randrange(30, 380); cy = rnd.randrange(30, 190)
        r = rnd.randrange(20, 55)
        im.alpha_composite(radial(r * 3, r * 3, (30, 26, 34), 150), (cx - r * 3 // 2, cy - r * 3 // 2))
    for k in range(9):
        cx = rnd.randrange(60, 360); cy = rnd.randrange(110, 260); r = rnd.randrange(24, 60)
        im.alpha_composite(radial(r * 3, r * 3, rnd.choice([(255, 150, 20), (255, 220, 70), (255, 90, 20)]), 230), (cx - r * 3 // 2, cy - r * 3 // 2))
    im.alpha_composite(radial(240, 200, (255, 240, 160), 255), (130, 80))
    d = ImageDraw.Draw(im)
    for k in range(70):
        sx = rnd.randrange(60, 420); sy = rnd.randrange(40, 330)
        d.rectangle((sx, sy, sx + 2, sy + 2), fill=rnd.choice([(255, 200, 60, 255), (255, 120, 30, 255), (255, 255, 200, 255)]))
    # chão
    d.rectangle((0, 400, W, H), fill=(10, 10, 24, 255))
    for i in range(-20, 21):
        d.line((W // 2 + i * 12, 400, W // 2 + i * 80, H), fill=(70, 30, 120, 255))
    y = 400; step = 6
    while y < H:
        d.line((0, y, W, y), fill=(20, 110, 160, 255))
        y += step; step += 4
    im.alpha_composite(radial(520, 120, (255, 120, 30), 120), (-40, 380))
    # ratos normais fugindo
    cols = [(150, 150, 165), (232, 232, 240), (142, 100, 70), (205, 172, 130), (96, 96, 112), (180, 140, 120), (240, 210, 190)]
    pack = []
    for i in range(22):
        pack.append((rnd.randrange(210, 780), rnd.randrange(405, 468), rnd.choice(cols), rnd.randrange(0, 4)))
    pack.sort(key=lambda p: p[1])
    for (px, py, c, pose) in pack:
        r = Image.open(os.path.join(SPR, "nrat_run_%d.png" % pose)).convert("RGBA")
        r = r.crop(r.getbbox())
        k = (0.85 + (py - 405) / 63.0 * 0.7) * 2.0
        r = r.resize((int(r.width * k), int(r.height * k)), Image.NEAREST)
        # sombra
        sh = Image.new("RGBA", (r.width, 10), (0, 0, 0, 0))
        ImageDraw.Draw(sh).ellipse((0, 0, r.width, 10), fill=(0, 0, 0, 110))
        im.alpha_composite(sh, (px, py + r.height - 6))
        # rastro de poeira
        for j in range(5):
            im.alpha_composite(radial(14, 10, (200, 180, 160), 70), (px - 16 - j * 12, py + r.height - 12))
        im.alpha_composite(r, (px, py))
    # protagonista à frente (da referência do usuário)
    main = Image.open(os.path.join(SPR, "r31_run_r_1.png")).convert("RGBA")
    main = main.crop(main.getbbox())
    k = 3
    main = main.resize((main.width * k, main.height * k), Image.NEAREST)
    mx, my = 640, 330
    im.alpha_composite(radial(main.width + 120, main.height + 80, (60, 255, 140), 90), (mx - 60, my - 40))
    sh = Image.new("RGBA", (main.width, 22), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse((0, 0, main.width, 22), fill=(0, 0, 0, 130))
    im.alpha_composite(sh, (mx, my + main.height - 14))
    for j in range(6):
        im.alpha_composite(radial(26, 18, (220, 200, 170), 90), (mx - 18 - j * 22, my + main.height - 24))
    im.alpha_composite(main, (mx, my))
    # vinheta
    vig = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vp = vig.load()
    for y in range(H):
        for x in range(W):
            dx = (x - W / 2) / (W / 2); dy = (y - H / 2) / (H / 2)
            r_ = math.sqrt(dx * dx * 0.8 + dy * dy)
            vp[x, y] = (0, 0, 0, int(max(0, min(150, (r_ - 0.7) * 260))))
    im.alpha_composite(vig)
    im.convert("RGB").save(os.path.join(OUT, "ui", "end_scene.png"))
    print("scene ok")


if __name__ == "__main__":
    build_liberdade()
    build_scene()
