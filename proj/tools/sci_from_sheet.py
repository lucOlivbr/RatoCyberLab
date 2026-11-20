# -*- coding: utf-8 -*-
"""Cientistas (modelos enviados pelo usuário) -> sprites do mundo, retratos e arte do quadrinho.
Fonte: tools/src/sci_sheet.png (+ rats_sheet.png). Dra. Okoye NÃO usa arma nem seringa."""
import os, sys
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r31_from_sheet import frames_of
HERE = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(HERE, "..", "assets")
sheet = Image.open(os.path.join(HERE, "src", "sci_sheet.png")).convert("RGB")
rats = Image.open(os.path.join(HERE, "src", "rats_sheet.png"))


def world_sprite(f, h=60):
    k = h / f.height
    s = f.resize((max(1, round(f.width * k)), h), Image.LANCZOS)
    s.putalpha(s.split()[3].point(lambda v: 255 if v > 110 else 0))
    c = Image.new("RGBA", (48, 64), (0, 0, 0, 0))
    c.alpha_composite(s, (24 - s.width // 2, 63 - s.height))
    return c


def portrait(box, size=128):
    im = sheet.crop(box)
    w, h = im.size
    m = min(w, h)
    im = im.crop(((w - m) // 2, 0, (w - m) // 2 + m, m)).resize((size, size), Image.LANCZOS)
    return im


def main():
    os.makedirs(os.path.join(A, "cut"), exist_ok=True)
    for who, dy in (("voss", 0), ("okoye", 495)):
        idle = frames_of(sheet, 200, 555, 92 + dy, 192 + dy, 4, 150)
        walk = frames_of(sheet, 590, 1030, 92 + dy, 192 + dy, 5, 150)
        print(who, len(idle), len(walk))
        kind = "scientist" if who == "voss" else "researcher"
        world_sprite(idle[2] if who == 'voss' else idle[0]).save(os.path.join(A, "world", f"npc_{kind}.png"))
        for i, f in enumerate(walk):
            world_sprite(f).save(os.path.join(A, "world", f"npc_{kind}_walk_{i}.png"))
        p = portrait((28, 92 + dy + 2, 182, 258 + dy))
        for mood in ("calm", "smile", "worried", "angry"):
            p.save(os.path.join(A, "cut", f"{who}_{mood}.png"))
    # Voss irritado/armado: retrato "com arma"
    portrait((1058, 285, 1336, 455)).save(os.path.join(A, "cut", "voss_angry.png"))
    # Voss com seringa (quadrinho): quadro de ataque, mirando para a direita
    atk = frames_of(sheet, 590, 1030, 365, 470, 4, 150)
    atk[1].save(os.path.join(A, "cut", "voss_syringe.png"))
    # rato normal sentado (quadrinho)
    frames_of(rats, 1040, 1512, 478, 592, 4)[0].save(os.path.join(A, "cut", "nrat_sit.png"))
    print("sci ok", atk[1].size)


if __name__ == "__main__":
    main()
