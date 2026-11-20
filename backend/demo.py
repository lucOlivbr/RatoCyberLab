#!/usr/bin/env python3
"""Cria uma conta de demonstração com erros de exemplo, para mostrar o relatório.

    python3 demo.py            # conta: demo@rato.lab  senha: demo1234
O servidor não precisa estar rodando; o script grava direto no banco.
"""
import random
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import server  # noqa: E402

EMAIL, SENHA = "demo@rato.lab", "demo1234"

EXEMPLOS = [
    ("FORMULA_ERRADA", 1, ["Armário r1_l2: montou CaOi (certa: NaCl)", "Armário r1_l2: montou NaCl2 (certa: NaCl)"]),
    ("FORMULA_ERRADA", 2, ["Armário r2_l2: montou HO2 (certa: H2O)"]),
    ("FORMULA_ERRADA", 5, ["Armário r5_l1: montou CO (certa: CO2)", "Armário r5_l1: montou C2O (certa: CO2)"]),
    ("RECEITA_INVALIDA", 0, ["Combinação desconhecida: 1 Hidrogênio + 1 Ferro"]),
    ("RECEITA_INVALIDA", 2, ["Esta mistura não usa fogo: 2 Hidrogênio + 1 Oxigênio (maçarico aceso)"]),
    ("RECEITA_INVALIDA", 6, ["Combinação desconhecida: 2 Ferro + 1 Carbono"]),
    ("DANO", 3, ["Descarga elétrica"]),
    ("DANO", 4, ["Veneno no ar", "Mutante"]),
    ("DANO", 6, ["Drone de segurança"]),
    ("DANO", 9, ["Campo laser", "Drone de segurança"]),
    ("MORTE", 4, ["Recapturado pelos guardas"]),
    ("MORTE", 9, ["Recapturado pelos guardas"]),
]


def main() -> None:
    server.iniciar_banco(server.DB_PADRAO)
    con = server.conectar(server.DB_PADRAO)
    try:
        if con.execute("SELECT 1 FROM jogador WHERE email = ?", (EMAIL,)).fetchone():
            print("A conta de demonstração já existe:", EMAIL, "/", SENHA)
            return
        rnd = random.Random(31)
        r = server.cadastrar(con, {"nome": "Rato Demo", "email": EMAIL, "senha": SENHA})
        jid = r["jogador"]["id"]
        agora = datetime.now(timezone.utc)
        tipos = {x["codigo"]: x["id"] for x in con.execute("SELECT id, codigo FROM tipo_erro")}
        linhas = []
        for tipo, sala, detalhes in EXEMPLOS:
            for det in detalhes:
                for _ in range(rnd.randint(1, 3)):
                    quando = agora - timedelta(days=rnd.randint(0, 5), hours=rnd.randint(0, 5), minutes=rnd.randint(0, 59))
                    linhas.append((jid, tipos[tipo], sala, det, quando.strftime("%Y-%m-%dT%H:%M:%SZ")))
        con.executemany("INSERT INTO evento_erro (jogador_id, tipo_erro_id, sala_id, detalhe, ocorrido_em) VALUES (?,?,?,?,?)", linhas)
        server.gravar_progresso(con, jid, {"room": 6, "hp": 2, "inv": {"h": 2, "o": 1, "fe": 3}, "learned": ["agua", "gel"],
                                           "flags": {"r1_open": True, "r2_open": True}, "taken": {"seen_6": True}})
        con.commit()
        print(f"Conta criada: {EMAIL} / {SENHA}  ({len(linhas)} erros de exemplo)")
    finally:
        con.close()


if __name__ == "__main__":
    main()
