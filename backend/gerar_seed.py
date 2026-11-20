#!/usr/bin/env python3
"""Gera backend/seed.sql (salas, itens e receitas) a partir do próprio jogo.

Lê proj/scripts/game.gd (ITEMS e RECIPES) e proj/data/rooms.json, para o banco
nunca ficar diferente do que existe no jogo.  Uso:  python3 gerar_seed.py
"""
import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
GAME_GD = RAIZ / "proj" / "scripts" / "game.gd"
ROOMS_JSON = RAIZ / "proj" / "data" / "rooms.json"
SAIDA = Path(__file__).resolve().parent / "seed.sql"

TIPOS = {"elem": "elemento", "fict": "ficticio", "prod": "fabricado"}


def sql(txt: str) -> str:
    return "'" + txt.replace("'", "''") + "'"


def bloco(src: str, nome: str) -> str:
    """Devolve o texto entre 'const NOME := {' e a chave que fecha."""
    ini = src.index(f"const {nome} := {{")
    ini = src.index("{", ini)
    nivel = 0
    for i in range(ini, len(src)):
        if src[i] == "{":
            nivel += 1
        elif src[i] == "}":
            nivel -= 1
            if nivel == 0:
                return src[ini + 1 : i]
    raise ValueError(nome)


def main() -> None:
    src = GAME_GD.read_text(encoding="utf-8")
    itens = []
    for m in re.finditer(r'^\t"(\w+)": \{(.*)\},?\s*$', bloco(src, "ITEMS"), re.M):
        iid, corpo = m.group(1), m.group(2)
        campo = lambda k: re.search(rf'"{k}": "((?:[^"\\]|\\.)*)"', corpo).group(1)
        itens.append((iid, campo("name"), campo("sym"), TIPOS[campo("kind")], campo("desc")))

    receitas = []
    for m in re.finditer(r'^\t"(\w+)": \{"req": \{(.*?)\}, "fire": (true|false)\}', bloco(src, "RECIPES"), re.M):
        ingr = [(k, int(v)) for k, v in re.findall(r'"(\w+)": (\d+)', m.group(2))]
        receitas.append((m.group(1), m.group(3) == "true", ingr))

    salas = [(int(r["id"]), r["name"]) for r in json.loads(ROOMS_JSON.read_text(encoding="utf-8"))["rooms"]]

    ids = {i[0] for i in itens}
    for rid, _, ingr in receitas:
        assert rid in ids, rid
        for k, _q in ingr:
            assert k in ids, k

    out = ["-- Gerado por backend/gerar_seed.py a partir do jogo. Não edite à mão.", ""]
    out.append("INSERT OR IGNORE INTO sala (id, nome) VALUES")
    out.append(",\n".join(f"    ({i}, {sql(n)})" for i, n in salas) + ";\n")
    out.append("INSERT OR IGNORE INTO item (id, nome, simbolo, tipo, descricao) VALUES")
    out.append(",\n".join(f"    ({sql(i)}, {sql(n)}, {sql(s)}, {sql(t)}, {sql(d)})" for i, n, s, t, d in itens) + ";\n")
    out.append("INSERT OR IGNORE INTO receita (item_id, requer_fogo) VALUES")
    out.append(",\n".join(f"    ({sql(r)}, {1 if f else 0})" for r, f, _ in receitas) + ";\n")
    out.append("INSERT OR IGNORE INTO ingrediente_receita (receita_id, item_id, quantidade) VALUES")
    out.append(",\n".join(f"    ({sql(r)}, {sql(k)}, {q})" for r, _, ingr in receitas for k, q in ingr) + ";\n")
    SAIDA.write_text("\n".join(out), encoding="utf-8")
    print(f"seed.sql: {len(salas)} salas, {len(itens)} itens, {len(receitas)} receitas")


if __name__ == "__main__":
    main()
