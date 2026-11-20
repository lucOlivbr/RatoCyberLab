"""Testes automatizados da API.  Execute dentro de backend/:  python3 -m unittest discover -s tests -v"""
import json
import sqlite3
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import server  # noqa: E402


class ApiTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.db = str(Path(cls.tmp.name) / "teste.db")
        cls.srv = server.criar_servidor("127.0.0.1", 0, cls.db, silencioso=True)
        cls.base = f"http://127.0.0.1:{cls.srv.server_address[1]}"
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()
        cls.srv.server_close()
        cls.tmp.cleanup()

    # -- auxiliar --
    def chamar(self, metodo, rota, corpo=None, token=None):
        dados = json.dumps(corpo).encode() if corpo is not None else None
        req = urllib.request.Request(self.base + rota, data=dados, method=metodo)
        if dados is not None:
            req.add_header("Content-Type", "application/json")
        if token:
            req.add_header("Authorization", "Bearer " + token)
        try:
            with urllib.request.urlopen(req) as r:
                raw = r.read()
                return r.status, (json.loads(raw) if raw and "json" in r.headers.get("Content-Type", "") else raw)
        except urllib.error.HTTPError as e:
            raw = e.read()
            try:
                return e.code, json.loads(raw)
            except ValueError:
                return e.code, raw

    def novo_jogador(self, nome="Rato Teste", email=None, senha="segredo123"):
        email = email or f"u{id(object())}@rato.lab"
        st, r = self.chamar("POST", "/api/cadastro", {"nome": nome, "email": email, "senha": senha})
        self.assertEqual(st, 201, r)
        return r["token"], r["jogador"], email, senha

    # -- cadastro e login --
    def test_cadastro_e_login(self):
        token, jog, email, senha = self.novo_jogador("Ana Lima", "ana@rato.lab")
        self.assertEqual(jog["nome"], "Ana Lima")
        st, r = self.chamar("POST", "/api/login", {"email": "ANA@rato.lab", "senha": senha})
        self.assertEqual(st, 200)
        self.assertTrue(r["token"])
        st, r = self.chamar("POST", "/api/login", {"email": email, "senha": "errada!"})
        self.assertEqual(st, 401)

    def test_senha_nao_fica_em_texto_puro(self):
        self.novo_jogador("Bia", "bia@rato.lab", "minhasenha99")
        con = sqlite3.connect(self.db)
        h, sal = con.execute("SELECT senha_hash, senha_salt FROM jogador WHERE email='bia@rato.lab'").fetchone()
        con.close()
        self.assertNotIn("minhasenha99", h)
        self.assertEqual(len(h), 64)
        self.assertEqual(len(sal), 32)

    def test_validacoes_do_cadastro(self):
        self.novo_jogador("Caio", "caio@rato.lab")
        casos = [
            ({"nome": "X", "email": "x@rato.lab", "senha": "123456"}, 400),        # nome curto
            ({"nome": "Xis", "email": "sem-arroba", "senha": "123456"}, 400),      # e-mail inválido
            ({"nome": "Xis", "email": "x@rato.lab", "senha": "123"}, 400),         # senha curta
            ({"nome": "Caio 2", "email": "CAIO@rato.lab", "senha": "123456"}, 409),  # e-mail repetido
            ({}, 400),
        ]
        for corpo, esperado in casos:
            st, _ = self.chamar("POST", "/api/cadastro", corpo)
            self.assertEqual(st, esperado, corpo)

    def test_exige_login(self):
        for metodo, rota in [("GET", "/api/progresso"), ("PUT", "/api/progresso"),
                             ("POST", "/api/eventos"), ("GET", "/api/relatorio")]:
            st, _ = self.chamar(metodo, rota, {})
            self.assertEqual(st, 401, rota)
        st, _ = self.chamar("GET", "/api/relatorio", token="token-falso")
        self.assertEqual(st, 401)

    def test_logout_invalida_token(self):
        token, *_ = self.novo_jogador("Duda", "duda@rato.lab")
        self.assertEqual(self.chamar("GET", "/api/progresso", token=token)[0], 200)
        self.assertEqual(self.chamar("POST", "/api/logout", {}, token)[0], 204)
        self.assertEqual(self.chamar("GET", "/api/progresso", token=token)[0], 401)

    def test_bloqueia_forca_bruta(self):
        _, _, email, _ = self.novo_jogador("Edu", "edu@rato.lab")
        codigos = [self.chamar("POST", "/api/login", {"email": email, "senha": f"x{i}"})[0] for i in range(12)]
        self.assertEqual(codigos[:10], [401] * 10)
        self.assertEqual(codigos[10], 429)

    # -- progresso --
    def test_progresso_ida_e_volta(self):
        token, *_ = self.novo_jogador("Fabi", "fabi@rato.lab")
        self.assertEqual(self.chamar("GET", "/api/progresso", token=token)[1], {"existe": False})
        save = {"room": 4, "hp": 2, "inv": {"h": 2, "o": 1, "gel": 1}, "learned": ["agua", "gel"],
                "flags": {"r3_power": True, "t_bench": True}, "taken": {"seen_4": True, "r3_l1": True}}
        self.assertEqual(self.chamar("PUT", "/api/progresso", save, token)[0], 204)
        st, r = self.chamar("GET", "/api/progresso", token=token)
        self.assertEqual(st, 200)
        self.assertTrue(r["existe"])
        for k in ("room", "hp", "inv", "flags", "taken"):
            self.assertEqual(r[k], save[k], k)
        self.assertEqual(sorted(r["learned"]), ["agua", "gel"])
        # segundo save substitui o primeiro
        save2 = dict(save, room=5, inv={"fe": 3}, flags={})
        self.chamar("PUT", "/api/progresso", save2, token)
        r = self.chamar("GET", "/api/progresso", token=token)[1]
        self.assertEqual((r["room"], r["inv"], r["flags"]), (5, {"fe": 3}, {}))

    def test_progresso_invalido(self):
        token, *_ = self.novo_jogador("Gabi", "gabi@rato.lab")
        base = {"room": 1, "hp": 3, "inv": {}, "learned": [], "flags": {}, "taken": {}}
        ruins = [dict(base, room=99), dict(base, hp=7), dict(base, inv={"item_fantasma": 1}),
                 dict(base, learned=["nao_existe"]), dict(base, inv={"h": -1}),
                 dict(base, flags={"chave com espaço": True})]
        for corpo in ruins:
            self.assertEqual(self.chamar("PUT", "/api/progresso", corpo, token)[0], 400, corpo)
        self.assertEqual(self.chamar("PUT", "/api/progresso", base, token)[0], 204)

    def test_progresso_isolado_entre_jogadores(self):
        t1, *_ = self.novo_jogador("Hugo", "hugo@rato.lab")
        t2, *_ = self.novo_jogador("Iara", "iara@rato.lab")
        self.chamar("PUT", "/api/progresso", {"room": 7, "hp": 1, "inv": {"c": 5}, "learned": [], "flags": {}, "taken": {}}, t1)
        self.assertFalse(self.chamar("GET", "/api/progresso", token=t2)[1]["existe"])

    # -- erros e relatório --
    def test_relatorio_de_erros(self):
        token, *_ = self.novo_jogador("Joao", "joao@rato.lab")
        evs = [
            {"tipo": "FORMULA_ERRADA", "sala": 2, "detalhe": "Armário r2_l1: montou NaCl2 (certa: NaCl)"},
            {"tipo": "FORMULA_ERRADA", "sala": 2, "detalhe": "Armário r2_l1: montou NaCl2 (certa: NaCl)"},
            {"tipo": "RECEITA_INVALIDA", "sala": 3, "detalhe": "Ferro + Cobre"},
            {"tipo": "DANO", "sala": 4, "detalhe": "Veneno"},
            {"tipo": "MORTE", "sala": 4, "detalhe": "Recapturado"},
        ]
        st, r = self.chamar("POST", "/api/eventos", {"eventos": evs}, token)
        self.assertEqual((st, r["registrados"]), (201, 5))
        st, r = self.chamar("POST", "/api/eventos", {"tipo": "DANO", "sala": 4, "detalhe": "Gás"}, token)
        self.assertEqual(st, 201)
        rel = self.chamar("GET", "/api/relatorio", token=token)[1]
        tot = {t["codigo"]: t["total"] for t in rel["resumo"]["por_tipo"]}
        self.assertEqual(tot, {"FORMULA_ERRADA": 2, "RECEITA_INVALIDA": 1, "DANO": 2, "MORTE": 1})
        self.assertEqual(rel["resumo"]["total"], 6)
        salas = {s["sala_id"]: s["total"] for s in rel["resumo"]["por_sala"]}
        self.assertEqual((salas[2], salas[3], salas[4], salas[0]), (2, 1, 3, 0))
        self.assertEqual(len(rel["eventos"]), 6)
        self.assertEqual(rel["resumo"]["mais_comuns"][0]["total"], 2)
        self.assertEqual(rel["jogador"]["nome"], "Joao")

    def test_relatorio_so_mostra_os_erros_do_proprio_jogador(self):
        t1, *_ = self.novo_jogador("Kiko", "kiko@rato.lab")
        t2, *_ = self.novo_jogador("Lia", "lia@rato.lab")
        self.chamar("POST", "/api/eventos", {"tipo": "DANO", "sala": 1, "detalhe": "x"}, t1)
        self.assertEqual(self.chamar("GET", "/api/relatorio", token=t2)[1]["resumo"]["total"], 0)

    def test_evento_invalido(self):
        token, *_ = self.novo_jogador("Mel", "mel@rato.lab")
        for corpo in [{"tipo": "INEXISTENTE", "sala": 1}, {"tipo": "DANO", "sala": 99}, {"tipo": "DANO"}, {"eventos": []}]:
            self.assertEqual(self.chamar("POST", "/api/eventos", corpo, token)[0], 400, corpo)

    def test_horario_informado_pelo_jogo(self):
        """Eventos guardados offline chegam com o horário em que aconteceram."""
        token, *_ = self.novo_jogador("Nando", "nando@rato.lab")
        antes = (datetime.now(timezone.utc) - timedelta(hours=3)).strftime("%Y-%m-%dT%H:%M:%SZ")
        futuro = (datetime.now(timezone.utc) + timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%SZ")
        self.chamar("POST", "/api/eventos", {"eventos": [
            {"tipo": "DANO", "sala": 1, "quando": antes},
            {"tipo": "DANO", "sala": 1, "quando": futuro},
            {"tipo": "DANO", "sala": 1, "quando": "lixo"}]}, token)
        quandos = sorted(e["quando"] for e in self.chamar("GET", "/api/relatorio", token=token)[1]["eventos"])
        self.assertEqual(quandos[0], antes)
        self.assertNotEqual(quandos[-1], futuro)  # futuro distante é descartado

    def test_sql_injection_vira_texto(self):
        token, *_ = self.novo_jogador("Otto", "otto@rato.lab")
        mal = "x'); DROP TABLE jogador;--"
        self.assertEqual(self.chamar("POST", "/api/eventos", {"tipo": "DANO", "sala": 1, "detalhe": mal}, token)[0], 201)
        rel = self.chamar("GET", "/api/relatorio", token=token)[1]
        self.assertEqual(rel["eventos"][0]["detalhe"], mal)
        st, _ = self.chamar("POST", "/api/login", {"email": "' OR 1=1 --", "senha": "x"})
        self.assertEqual(st, 401)

    # -- diversos --
    def test_saude_e_pagina_do_relatorio(self):
        self.assertEqual(self.chamar("GET", "/api/saude")[1]["ok"], True)
        st, html = self.chamar("GET", "/relatorio")
        self.assertEqual(st, 200)
        self.assertIn(b"Relat", html)
        self.assertEqual(self.chamar("GET", "/api/nao-existe")[0], 404)

    def test_catalogo_carregado(self):
        con = sqlite3.connect(self.db)
        n = [con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in ("sala", "item", "receita", "ingrediente_receita")]
        con.close()
        self.assertEqual(n[:3], [11, 27, 12])
        self.assertGreater(n[3], 12)


if __name__ == "__main__":
    unittest.main()
