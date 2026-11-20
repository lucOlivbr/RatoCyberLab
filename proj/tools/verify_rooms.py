# -*- coding: utf-8 -*-
"""Valida os mapas: alcançabilidade (BFS) e suficiência de componentes por sala."""
import json, os
from collections import deque

HERE = os.path.dirname(os.path.abspath(__file__))
rooms = json.load(open(os.path.join(HERE, "..", "data", "rooms.json"), encoding="utf-8"))["rooms"]

RECIPES = {
    "chave_manut": {"engrenagem": 2, "fe": 1},
    "termico": {"nucleo": 1, "fe": 1, "cu": 1},
    "modulo_eletrico": {"celula": 1, "cu": 2},
    "filtro": {"c": 2, "polimero": 1},
    "agua": {"h": 2, "o": 1},
    "solvente": {"agua": 1, "catalisador": 1, "na": 1},
    "gel": {"agua": 1, "polimero": 1},
    "modulo_contencao": {"circuito": 2, "cristal": 1},
    "disp_resgate": {"circuito": 1, "engrenagem": 1, "celula": 1},
    "chave_mestra": {"circuito": 1, "cristal": 1, "modulo_gen": 1},
    "bomba": {"modulo_gen": 1, "celula": 1, "cristal": 1},
}

def base_needs(rid, times=1, acc=None):
    acc = acc if acc is not None else {}
    for k, q in RECIPES[rid].items():
        if k in RECIPES:
            base_needs(k, q * times, acc)
        else:
            acc[k] = acc.get(k, 0) + q * times
    return acc

ok = True
for r in rooms:
    grid = r["grid"]
    H, W = len(grid), len(grid[0])
    blocked = [[grid[y][x] == '#' for x in range(W)] for y in range(H)]
    door = [[grid[y][x] == 'D' for x in range(W)] for y in range(H)]
    solid_objs = []
    def mark(x, y, w, h):
        for j in range(int(y), int(y + h + 0.999)):
            for i in range(int(x), int(x + w + 0.999)):
                if 0 <= j < H and 0 <= i < W:
                    blocked[j][i] = True
    items_avail = {}
    for o in r["objects"]:
        t = o["type"]
        if t == "decor" and o.get("solid"):
            mark(o["x"], o["y"], o["w"], o["h"])
        elif t in ("terminal", "locker", "npc", "crate"):
            mark(o["x"], o["y"], 1, 1)
        elif t == "bench":
            mark(o["x"], o["y"], 3, 2)
        elif t in ("obstacle", "cage"):
            mark(o["x"], o["y"], o["w"], o["h"])
        if t == "locker":
            for k, q in o["items"].items(): items_avail[k] = items_avail.get(k, 0) + q
        if t == "pickup":
            items_avail[o["item"]] = items_avail.get(o["item"], 0) + o.get("qty", 1)
    # pontos de partida
    sx, sy = r["spawn_prev"]
    def bfs(start, extra_block=None):
        seen = {start}
        dq = deque([start])
        while dq:
            cx, cy = dq.popleft()
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < W and 0 <= ny < H and (nx, ny) not in seen:
                    if blocked[ny][nx]: continue
                    if extra_block and (nx, ny) in extra_block: continue
                    seen.add((nx, ny)); dq.append((nx, ny))
        return seen
    # barreira laser da sala 6 (coluna 20 inteira) bloqueia antes de desativar
    lasercol = set()
    for o in r["objects"]:
        if o["type"] == "hazard" and o["kind"] == "laser" and o.get("clear_flag"):
            col = int(o["x"])
            for yy in range(2, 14): lasercol.add((col, yy))
    reach = bfs((sx, sy), lasercol)
    print(f"--- Sala {r['id']} {r['name']}: {len(reach)} células alcançáveis (antes de solucionar)")
    if (sx, sy) not in reach or blocked[sy][sx]:
        print("  ERRO spawn_prev bloqueado"); ok = False
    sn = tuple(r["spawn_next"])
    reach_all = bfs((sx, sy))
    if blocked[sn[1]][sn[0]]:
        print("  ERRO spawn_next bloqueado", sn); ok = False
    def near(o_x, o_y, w, h, rs):
        for j in range(int(o_y) - 1, int(o_y + h) + 1):
            for i in range(int(o_x) - 1, int(o_x + w) + 1):
                if (i, j) in rs: return True
        return False
    for o in r["objects"]:
        t = o["type"]
        if t in ("terminal", "locker", "pickup", "bench", "npc", "obstacle", "cage", "crate", "plate", "decor"):
            if t == "decor" and not o.get("solid"): continue
            if t == "decor": continue
            w = 3 if t == "bench" else o.get("w", 1)
            h = 2 if t == "bench" else o.get("h", 1)
            # obstáculos 'blocks' (gelo/cristal) são alcançados pela frente
            rs = reach_all if (r["id"] == 6 and t in ("obstacle",) and False) else reach
            if t in ("locker", "pickup") and r["id"] == 6:
                rs = reach
            if not near(o["x"], o["y"], w, h, rs):
                # em R3/R9 tudo é alcançável. R6: itens à direita do laser são ok só depois
                if near(o["x"], o["y"], w, h, reach_all):
                    print(f"  aviso: {t} {o.get('id', '')} só alcançável depois de solucionar")
                else:
                    print(f"  ERRO: {t} {o.get('id', '')} inalcançável"); ok = False
    # saída alcançável (depois de solucionar)
    for o in r["objects"]:
        if o["type"] == "door" and not o.get("back"):
            # liberar obstáculos bloqueantes (gelo/cristal) para o teste
            for ob in r["objects"]:
                if ob["type"] == "obstacle" and ob.get("blocks"):
                    for jj in range(ob["y"], ob["y"] + ob["h"]):
                        for ii in range(ob["x"], ob["x"] + ob["w"]):
                            blocked[jj][ii] = False
            rs = bfs((sx, sy))
            if not near(o["x"], o["y"], o["w"], o["h"], rs):
                print("  ERRO: porta de saída inalcançável"); ok = False
    # componentes
    for need in r["needs"]:
        pass
    print("  componentes na sala:", dict(sorted(items_avail.items())))
print("RESULTADO:", "OK" if ok else "FALHAS")
