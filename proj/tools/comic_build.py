# -*- coding: utf-8 -*-
"""Monta assets/cut/comic_page.png: a página em quadrinhos enviada pelo usuário, com o Dr. Voss (nosso sprite) no lugar do cientista do quadro 2."""
import os
from PIL import Image, ImageFilter, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
src = Image.open(os.path.join(HERE, "src", "comic_page_orig.png")).convert("RGBA")
OY = 350  # deslocamento do recorte do quadro 2 (coordenadas da página)

def P(x, y):  # coordenadas do recorte -> página
    return (x, y + OY)

page = src.copy()
# 1) apaga o cientista com preenchimento por difusão (cores do entorno) e borda suave
import numpy as np
from scipy.ndimage import gaussian_filter
arr = np.array(src.convert("RGB")).astype(np.float32)
mask = Image.new("L", src.size, 0)
md = ImageDraw.Draw(mask)
md.rectangle((300, 8 + OY, 602, 408 + OY), fill=255)
md.rectangle((228, 8 + OY, 302, 222 + OY), fill=255)
md.rectangle((128, 205 + OY, 300, 326 + OY), fill=255)   # rato branco antigo
mk = np.array(mask).astype(np.float32) / 255.0
known = 1.0 - (gaussian_filter(mk, 2) > 0.01).astype(np.float32)
fill = np.zeros_like(arr)
acc = np.zeros(arr.shape[:2], np.float32)
for sig in (6, 14, 30, 60):
    num = np.stack([gaussian_filter(arr[..., c] * known, sig) for c in range(3)], -1)
    den = gaussian_filter(known, sig)[..., None] + 1e-4
    est = num / den
    w = (den[..., 0] > 0.02).astype(np.float32)
    fill = np.where((acc[..., None] == 0) & (w[..., None] > 0), est, fill)
    acc = np.maximum(acc, w)
fill = fill * 0.8   # um pouco mais escuro: o fundo fica atrás do Voss
soft = gaussian_filter(mk, 5)[..., None]
out = arr * (1 - soft) + fill * soft
page = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).convert("RGBA")
# 2) estende a mesa: repete a faixa da frente da mesa
strip = src.crop((330, 300 + OY, 396, 408 + OY))
for x in range(396, 602, 66):
    page.paste(strip, (x, 300 + OY))
# 3) Dr. Voss (modelo do usuário, com a seringa) + rato normal (modelo do usuário)
voss = Image.open(os.path.join(HERE, "..", "assets", "cut", "voss_syringe.png")).convert("RGBA")
k = 3.3
voss = voss.resize((int(voss.width * k), int(voss.height * k)), Image.NEAREST).transpose(Image.FLIP_LEFT_RIGHT)
vx, vy = 262, 404 - voss.height
sh = Image.new("RGBA", page.size, (0, 0, 0, 0))
ImageDraw.Draw(sh).ellipse((vx + 30, 392 + OY, vx + voss.width - 10, 414 + OY), fill=(0, 0, 0, 120))
rat = Image.open(os.path.join(HERE, "..", "assets", "cut", "nrat_sit.png")).convert("RGBA")
rat = rat.resize((int(rat.width * 2.3), int(rat.height * 2.3)), Image.NEAREST)
rx, ry = 128, 324 - rat.height
ImageDraw.Draw(sh).ellipse((rx + 10, 312 + OY, rx + rat.width - 5, 330 + OY), fill=(0, 0, 0, 120))
page.alpha_composite(sh)
page.alpha_composite(rat, (rx, ry + OY))
page.alpha_composite(voss, (vx, vy + OY))
# 4) balão de fala original por cima (só o formato do balão)
from scipy.ndimage import binary_fill_holes, binary_dilation
bub = src.crop((478, 20 + OY, 684, 135 + OY))
ba = np.array(bub.convert("RGB")).astype(np.float32)
bright = (ba.min(axis=2) > 195)
shape = binary_fill_holes(binary_dilation(bright, iterations=2))
# mantém só o maior componente
from scipy.ndimage import label
lab, n = label(shape)
if n > 1:
    sizes = [(lab == i).sum() for i in range(1, n + 1)]
    shape = lab == (1 + int(np.argmax(sizes)))
m = Image.fromarray((shape * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8))
page.paste(bub, (478, 20 + OY), m)
page.convert("RGB").save(os.path.join(HERE, "..", "assets", "cut", "comic_page.png"))
print("comic ok", voss.size, (vx, vy))
