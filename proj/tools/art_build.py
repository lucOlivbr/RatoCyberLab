# -*- coding: utf-8 -*-
"""Gera todos os assets visuais. Uso: python3 art_build.py  (rodar a partir da pasta tools)"""
import os, sys, json, random, math, shutil
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
from art_lib import *
from rooms_def import ROOMS, THEMES

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "assets")
SRC_SPR = os.environ.get("RATO_SPR_DIR", os.path.join(HERE, "src", "spr"))
SRC_TABLE = os.environ.get("RATO_TABLE", os.path.join(HERE, "src", "craft_table_src.png"))
for sub in ("world", "sprites", "icons", "ui"):
    os.makedirs(os.path.join(OUT, sub), exist_ok=True)

def save(im, sub, name):
    im.save(os.path.join(OUT, sub, name))

# ---------------------------------------------------------------- fundos das salas
import art_deco2 as D2


def build_room_bg0(r):
    """Gaiola do tutorial: interior pequeno, grades em volta e o laboratório escuro ao fundo."""
    theme = THEMES[r['theme']]
    acc = hx(theme['accent'])
    grid = [''.join(row) for row in r['grid']]
    Wt, Ht = len(grid[0]), len(grid)
    rnd = random.Random(404)
    bg = new(Wt * T, Ht * T, (6, 8, 16, 255))
    d = ImageDraw.Draw(bg)
    # silhuetas do laboratório lá fora
    for _ in range(26):
        x = rnd.randrange(0, Wt * T - 40); w = rnd.randrange(30, 120); h = rnd.randrange(60, 260)
        y = Ht * T - h - rnd.randrange(0, 60)
        d.rectangle((x, y, x + w, Ht * T), fill=(12 + rnd.randrange(8), 16 + rnd.randrange(8), 28 + rnd.randrange(10), 255))
        for wy in range(y + 6, y + h - 4, 9):
            for wx in range(x + 5, x + w - 4, 8):
                if rnd.random() < 0.22:
                    d.rectangle((wx, wy, wx + 2, wy + 3), fill=rnd.choice([shade(acc, 0.5), (120, 40, 90, 255), (140, 110, 30, 255)]))
    for _ in range(14):
        x, y = rnd.randrange(0, Wt * T), rnd.randrange(0, Ht * T // 2)
        bg.alpha_composite(radial(48, 48, rnd.choice([acc, (255, 60, 150, 255)]), 40), (x - 24, y - 24))
    # piso do interior
    for y in range(Ht):
        for x in range(Wt):
            if grid[y][x] == '.':
                bg.paste(floor_tile(theme, 5000 + y * 40 + x, (x + y) % 2 == 0), (x * T, y * T))
    # sombra da gaiola no piso
    bg.alpha_composite(radial(14 * T, 8 * T, (0, 0, 0, 255), 90), (8 * T, 4 * T))
    bg.alpha_composite(D2.cage_ring(theme, 7, 22, 3, 12), (0, 0))
    return bg


def build_room_bg(r):
    if r['id'] == 0:
        return build_room_bg0(r)
    theme = THEMES[r["theme"]]
    acc = hx(theme["accent"])
    grid = ["".join(row) for row in r["grid"]]
    Wt, Ht = len(grid[0]), len(grid)
    bg = new(Wt * T, Ht * T, (8, 11, 20, 255))
    rid = r["id"]
    # piso
    for y in range(Ht):
        for x in range(Wt):
            if grid[y][x] in ('.',):
                bg.paste(floor_tile(theme, rid * 1000 + y * 40 + x, (x + y) % 2 == 0), (x * T, y * T))
    # luzes (lamp) e plataformas no chão
    for o in r["objects"]:
        if o["type"] == "decor" and o["kind"] == "lamp":
            bg.alpha_composite(radial(o["w"] * T, o["h"] * T, acc, 70), (o["x"] * T, o["y"] * T))
        if o["type"] == "decor" and o["kind"] == "platform":
            bg.alpha_composite(deco_platform(o["w"], o["h"], theme), (o["x"] * T, o["y"] * T))
    # paredes: telhado primeiro
    for y in range(Ht):
        for x in range(Wt):
            c = grid[y][x]
            if c == '#':
                bg.paste(wall_roof_tile(theme, rid * 2000 + y * 40 + x), (x * T, y * T))
    # bordas brilhantes do telhado voltadas ao chão
    d = ImageDraw.Draw(bg)
    for y in range(Ht):
        for x in range(Wt):
            if grid[y][x] != '#':
                continue
            def fl(xx, yy):
                return 0 <= xx < Wt and 0 <= yy < Ht and grid[yy][xx] == '.'
            if fl(x - 1, y): d.line((x * T, y * T, x * T, y * T + T - 1), fill=shade(acc, 0.55))
            if fl(x + 1, y): d.line((x * T + T - 1, y * T, x * T + T - 1, y * T + T - 1), fill=shade(acc, 0.55))
            if fl(x, y - 1): d.line((x * T, y * T, x * T + T - 1, y * T), fill=shade(acc, 0.55))
    # faces frontais: parede (ou porta 'D' no topo) com chão abaixo
    for y in range(Ht):
        for x in range(Wt):
            c = grid[y][x]
            below = grid[y + 1][x] if y + 1 < Ht else '#'
            if c in ('#', 'D') and below in ('.',):
                face = wall_face_tile(theme, rid * 3000 + y * 40 + x)
                fy = y * T - (face.height - 32)
                if fy < 0:
                    face = face.crop((0, -fy, T, face.height)); fy = 0
                bg.alpha_composite(face, (x * T, fy))
    # porta (célula D): fundo escuro de corredor
    for y in range(Ht):
        for x in range(Wt):
            if grid[y][x] == 'D':
                if y < Ht - 1:
                    d.rectangle((x * T, y * T, x * T + T - 1, y * T + T - 1), fill=(6, 8, 14, 255))
    # parede inferior: bisel superior brilhante
    for x in range(Wt):
        if grid[Ht - 1][x] == '#':
            d.line((x * T, (Ht - 1) * T, x * T + T - 1, (Ht - 1) * T), fill=shade(acc, 0.5))
            d.line((x * T, (Ht - 1) * T + 1, x * T + T - 1, (Ht - 1) * T + 1), fill=(34, 44, 70, 255))
    # decorações não sólidas na parede (pipe, sign)
    for o in r["objects"]:
        if o["type"] != "decor":
            continue
        k = o["kind"]
        if k == "pipe":
            bg.alpha_composite(deco_pipe(o["w"], theme, rid + o["x"]), (o["x"] * T, o["y"] * T))
        elif k == "sign":
            bg.alpha_composite(deco_sign(o["w"], o.get("text", ""), theme), (o["x"] * T, o["y"] * T))
    # decorações sólidas ordenadas por y
    solids = [o for o in r["objects"] if o["type"] == "decor" and o["kind"] not in ("pipe", "sign", "lamp", "platform")]
    solids.sort(key=lambda o: o["y"] + o["h"])
    for o in solids:
        k, w, h = o["kind"], o["w"], o["h"]
        seed = rid * 77 + o["x"] * 3 + o["y"]
        if k == "tank":
            im = deco_tank(w, h, theme, creature=(r["theme"] in ("green", "teal")), seed=seed,
                           liquid=("#ffd23a" if (r["theme"] == "yellow" and o["x"] < 10) else ("#19e6ff" if r["theme"] == "yellow" else None)))
        elif k == "rack": im = deco_rack(w, h, theme, seed)
        elif k == "shelf": im = deco_shelf(w, h, theme, seed)
        elif k == "boxes": im = deco_boxes(w, h, theme, seed)
        elif k == "machine": im = deco_machine(w, h, theme, seed)
        elif k == "reactor": im = deco_reactor(w, h, theme)
        elif k == "aquarium": im = deco_aquarium(w, h, theme, seed)
        elif k == "forklift": im = deco_forklift(w, h, theme)
        elif k == "pod": im = deco_pod(w, h, theme, o.get("rats", 1), seed)
        elif k == "mixbench": im = deco_mixbench(w, h, theme, seed)
        elif k == "cage_start": im = deco_cage_start(w, h, theme)
        elif k == "emitter": im = deco_emitter(theme)
        elif k == "computer":
            im = D2.deco_computer(w, h, theme, seed); bg.alpha_composite(im, (o["x"] * T, o["y"] * T - 18)); continue
        elif k == "potions":
            im = D2.deco_potions(w, h, theme, seed); bg.alpha_composite(im, (o["x"] * T, o["y"] * T - 14)); continue
        elif k == "books": im = D2.deco_books(w, h, theme, seed)
        elif k == "desk":
            im = D2.deco_desk(w, h, theme, seed); bg.alpha_composite(im, (o["x"] * T, o["y"] * T - 10)); continue
        else: continue
        bg.alpha_composite(im, (o["x"] * T, o["y"] * T))
    return bg

# ---------------------------------------------------------------- sprites do rato
def hue_to_blue(im):
    """Água azul: desloca o matiz dos pixels esverdeados/ciano para o azul (~215 graus)."""
    import colorsys
    a = np.array(im.convert("RGBA")).astype(float) / 255.0
    out = a.copy()
    h_, w_ = a.shape[:2]
    for y in range(h_):
        for x in range(w_):
            r, g, b, al = a[y, x]
            if al < 0.05:
                continue
            hh, ss, vv = colorsys.rgb_to_hsv(r, g, b)
            if ss > 0.25 and 0.25 < hh < 0.55:
                nr, ng, nb = colorsys.hsv_to_rgb(0.6, min(1.0, ss * 1.1), vv)
                out[y, x] = (nr, ng, nb, al)
    return Image.fromarray((out * 255).astype("uint8"), "RGBA")


def fit_rat():
    rat_dir = os.path.join(OUT, "sprites")
    def load(n): return Image.open(os.path.join(SRC_SPR, n + ".png")).convert("RGBA")
    # lado: frames normalizados em tela 64x64, pés no centro-inferior
    def norm_side(names, k, prefix):
        frames = [load(n) for n in names]
        for i, f in enumerate(frames):
            s = f.resize((max(1, int(f.width * k)), max(1, int(f.height * k))), Image.LANCZOS)
            canvas = new(64, 56)
            canvas.alpha_composite(s, (32 - s.width // 2 - 2, 55 - s.height))
            canvas.save(os.path.join(rat_dir, f"{prefix}_{i}.png"))
    import rat_from_ref
    rat_from_ref.main()
    for n in ("front", "back"):
        f = load(n)
        k = 46 / f.height
        s = f.resize((int(f.width * k), 46), Image.LANCZOS)
        canvas = new(64, 56)
        canvas.alpha_composite(s, (32 - s.width // 2, 55 - s.height))
        canvas.save(os.path.join(rat_dir, f"rat_{n}.png"))
    # poses
    for n, k in (("pose_usar", 0.55), ("pose_morte", 0.7), ("pose_vitoria", 0.7)):
        f = load(n)
        s = f.resize((int(f.width * k), int(f.height * k)), Image.LANCZOS)
        s.save(os.path.join(rat_dir, "rat_" + n[5:] + ".png"))
    # ícones de itens (da ficha do personagem)
    for n in ("cura", "veneno", "bomba", "mochila", "frasco", "seringa", "granada"):
        f = load("ico_" + n)
        k = 28 / max(f.width, f.height)
        s = f.resize((max(1, int(f.width * k)), max(1, int(f.height * k))), Image.LANCZOS)
        if n == "frasco":
            s = hue_to_blue(s)
        s.save(os.path.join(OUT, "icons", f"ico_{n}.png"))

# ---------------------------------------------------------------- bancada (da imagem da CraftTable)
def build_table():
    im = Image.open(SRC_TABLE).convert("RGBA")
    # tela da CraftTable para a interface (768x512)
    ui = im.resize((768, 512), Image.LANCZOS)
    # remove vinheta semitransparente deixando o fundo escuro uniforme
    bgc = new(768, 512, (6, 9, 18, 255))
    bgc.alpha_composite(ui)
    rgb = bgc.convert("RGB")
    # tira a chama azul pintada na imagem (o jogo desenha a chama só quando o maçarico está ligado)
    px = rgb.load()
    for y in range(224, 249):
        l, r = np.array(px[494, y]), np.array(px[528, y])
        for x in range(495, 528):
            t = (x - 494) / 34.0
            px[x, y] = tuple(int(v) for v in (l * (1 - t) + r * t))
    rgb.save(os.path.join(OUT, "ui", "craft_table.png"))
    # versão pequena para o mundo: recorte do tampo
    a = np.array(im)
    ys, xs = np.where(a[..., 3] >= 250)
    box = (max(0, xs.min() - 4), max(0, ys.min() - 4), min(im.width, xs.max() + 4), min(im.height, ys.max() + 4))
    crop = im.crop(box)
    k = 96 / crop.width
    small = crop.resize((96, max(1, int(crop.height * k))), Image.LANCZOS)
    canvas = new(96, 64)
    canvas.alpha_composite(small, (0, 64 - small.height))
    canvas.save(os.path.join(OUT, "world", "bench.png"))

# ---------------------------------------------------------------- fundo do título / sobreposição CRT
def build_title():
    W_, H_ = 960, 540
    im = new(W_, H_, (6, 8, 18, 255))
    d = ImageDraw.Draw(im)
    for y in range(H_):
        t = y / H_
        d.line((0, y, W_, y), fill=mix((10, 6, 32, 255), (4, 20, 40, 255), t))
    rnd = random.Random(5)
    # skyline
    for layer, (col, hmin, hmax) in enumerate([((14, 18, 44, 255), 120, 260), ((20, 26, 60, 255), 80, 200)]):
        x = 0
        while x < W_:
            bw = rnd.randrange(36, 90); bh = rnd.randrange(hmin, hmax)
            d.rectangle((x, 380 - bh, x + bw, 380), fill=col)
            for wy in range(380 - bh + 8, 372, 12):
                for wx in range(x + 5, x + bw - 6, 10):
                    if rnd.random() < 0.28:
                        d.rectangle((wx, wy, wx + 3, wy + 4), fill=rnd.choice([(25, 230, 255, 255), (255, 60, 150, 255), (255, 210, 60, 255)]))
            x += bw + rnd.randrange(0, 8)
    # chão com grade em perspectiva
    d.rectangle((0, 380, W_, H_), fill=(8, 10, 26, 255))
    for i in range(-20, 21):
        d.line((W_ // 2 + i * 14, 380, W_ // 2 + i * 90, H_), fill=(120, 40, 200, 255))
    y = 380; step = 6
    while y < H_:
        d.line((0, y, W_, y), fill=(25, 150, 200, 255))
        y += step; step += 4
    glow(im, lambda dd, c: dd.line((0, 380, W_, 380), fill=c, width=2), (25, 230, 255, 255), 8, 1.0)
    # chuva neon
    for _ in range(140):
        x = rnd.randrange(W_); y0 = rnd.randrange(H_); l = rnd.randrange(8, 24)
        d.line((x, y0, x - 2, y0 + l), fill=(90, 160, 220, 120))
    # rato (pose de vitória) grande
    try:
        rat = Image.open(os.path.join(OUT, "sprites", "rat_vitoria.png"))
        k = 3.2
        rs = rat.resize((int(rat.width * k), int(rat.height * k)), Image.NEAREST)
        glow_only(im, lambda dd, c: dd.ellipse((660, 160, 900, 440), fill=c), (60, 255, 120, 255), 40, 0.5)
        im.alpha_composite(rs, (700, 540 - rs.height - 70))
    except Exception as e:
        print("sem rato no título", e)
    # escurece laterais
    ov = radial(W_, H_, (0, 0, 0, 255), 0)
    save(im.convert("RGB"), "ui", "title_bg.png")

def build_overlay():
    W_, H_ = 960, 540
    im = new(W_, H_)
    px = im.load()
    for y in range(H_):
        for x in range(W_):
            dx = (x - W_ / 2) / (W_ / 2); dy = (y - H_ / 2) / (H_ / 2)
            r = math.sqrt(dx * dx * 0.9 + dy * dy * 1.1)
            a = int(max(0, min(160, (r - 0.55) * 210)))
            if y % 3 == 0:
                a = min(255, a + 22)
            if a:
                px[x, y] = (2, 4, 12, a)
    save(im, "ui", "crt_overlay.png")

def build_props():
    th = THEMES["cyan"]
    for st in ("locked", "unlocked", "open", "shutter_closed", "shutter_open"):
        save(spr_door_top(th, st), "world", f"door_{st}.png")
    save(spr_door_back(th), "world", "door_back.png")
    save(spr_terminal(th, False), "world", "terminal_0.png")
    save(spr_terminal(th, True), "world", "terminal_1.png")
    for k in ("panel", "vent", "lasercon", "console"):
        save(spr_console(th, k, False), "world", f"console_{k}_0.png")
        save(spr_console(th, k, True), "world", f"console_{k}_1.png")
    save(spr_locker(th, False), "world", "locker_0.png"); save(spr_locker(th, True), "world", "locker_1.png")
    save(spr_ice(), "world", "ice.png"); save(spr_crystal(), "world", "crystal.png")
    save(D2.spr_bars(), "world", "bars.png")
    save(spr_cage(th, False), "world", "cage_0.png"); save(spr_cage(th, True), "world", "cage_1.png")
    save(spr_crate(th), "world", "crate.png")
    save(spr_plate(th, False), "world", "plate_0.png"); save(spr_plate(th, True), "world", "plate_1.png")
    for i in (0, 1):
        save(spr_drone(i), "world", f"drone_{i}.png"); save(spr_mutant(i), "world", f"mutant_{i}.png")
    save(spr_human("scientist"), "world", "npc_scientist.png"); save(spr_human("researcher"), "world", "npc_researcher.png")

if __name__ == "__main__":
    only = sys.argv[1:]
    fit_rat()
    build_table()
    build_props()
    build_title()
    build_overlay()
    for r in ROOMS:
        bg = build_room_bg(r)
        save(bg, "world", f"bg_{r['id']:02d}.png")
    print("assets ok")
