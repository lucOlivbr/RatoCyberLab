#!/usr/bin/env python3
"""Backend do Rato CyberLab (Projeto R-31).

API HTTP/JSON + banco SQLite, usando apenas a biblioteca padrão do Python 3.9+
(nada para instalar).  O jogo em Godot conversa com esta API; a página
/relatorio mostra ao jogador onde ele errou.

    python3 server.py                 # http://127.0.0.1:8000
    python3 server.py --port 9000
    python3 server.py --host 0.0.0.0  # aceita outros computadores da rede

Rotas
    GET  /api/saude                   verifica se o servidor está no ar
    POST /api/cadastro                {nome, email, senha}  -> cria conta e já loga
    POST /api/login                   {email, senha}
    POST /api/logout                  (autenticado)
    GET  /api/progresso               (autenticado) carrega o save do banco
    PUT  /api/progresso               (autenticado) grava o save no banco
    POST /api/eventos                 (autenticado) registra erro(s) do jogador
    GET  /api/relatorio               (autenticado) resumo + lista de erros
    GET  /relatorio                   página HTML do relatório
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import re
import secrets
import sqlite3
import sys
import threading
import time
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

AQUI = Path(__file__).resolve().parent
DB_PADRAO = os.environ.get("RATO_DB", str(AQUI / "rato_cyberlab.db"))
PBKDF2_ITER = 200_000
SESSAO_DIAS = 30
MAX_CORPO = 256 * 1024
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
CHAVE_RE = re.compile(r"^[\w:.\-]{1,80}$")

# tentativas de login erradas: (ip, email) -> [timestamps]
_falhas: dict[tuple[str, str], list[float]] = {}
_falhas_lock = threading.Lock()


# ----------------------------------------------------------------------------
# Banco de dados
# ----------------------------------------------------------------------------
def agora() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def conectar(caminho: str) -> sqlite3.Connection:
    con = sqlite3.connect(caminho, timeout=10)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con


def iniciar_banco(caminho: str) -> None:
    """Cria as tabelas (schema.sql) e carrega o catálogo do jogo (seed.sql)."""
    con = conectar(caminho)
    try:
        con.execute("PRAGMA journal_mode = WAL")
        con.executescript((AQUI / "schema.sql").read_text(encoding="utf-8"))
        seed = AQUI / "seed.sql"
        if seed.exists():
            con.executescript(seed.read_text(encoding="utf-8"))
        con.commit()
    finally:
        con.close()


# ----------------------------------------------------------------------------
# Senhas e sessões
# ----------------------------------------------------------------------------
def hash_senha(senha: str, sal_hex: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", senha.encode("utf-8"), bytes.fromhex(sal_hex), PBKDF2_ITER).hex()


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def criar_sessao(con: sqlite3.Connection, jogador_id: int) -> str:
    token = secrets.token_urlsafe(32)
    expira = (datetime.now(timezone.utc) + timedelta(days=SESSAO_DIAS)).strftime("%Y-%m-%dT%H:%M:%SZ")
    con.execute("DELETE FROM sessao WHERE expira_em < ?", (agora(),))
    con.execute(
        "INSERT INTO sessao (token_hash, jogador_id, expira_em) VALUES (?, ?, ?)",
        (hash_token(token), jogador_id, expira),
    )
    return token


class ErroAPI(Exception):
    def __init__(self, status: int, mensagem: str):
        super().__init__(mensagem)
        self.status = status
        self.mensagem = mensagem


# ----------------------------------------------------------------------------
# Regras de negócio (cada função recebe a conexão já aberta)
# ----------------------------------------------------------------------------
def texto(d: dict, campo: str, minimo: int, maximo: int, rotulo: str) -> str:
    v = d.get(campo)
    if not isinstance(v, str):
        raise ErroAPI(400, f"Informe {rotulo}.")
    v = v.strip()
    if not (minimo <= len(v) <= maximo):
        raise ErroAPI(400, f"{rotulo.capitalize()} deve ter entre {minimo} e {maximo} caracteres.")
    return v


def cadastrar(con: sqlite3.Connection, d: dict) -> dict:
    nome = texto(d, "nome", 2, 60, "o nome")
    email = texto(d, "email", 5, 120, "o e-mail").lower()
    if not EMAIL_RE.match(email):
        raise ErroAPI(400, "E-mail inválido.")
    senha = d.get("senha")
    if not isinstance(senha, str) or not (6 <= len(senha) <= 100):
        raise ErroAPI(400, "A senha deve ter de 6 a 100 caracteres.")
    sal = secrets.token_hex(16)
    try:
        cur = con.execute(
            "INSERT INTO jogador (nome, email, senha_hash, senha_salt) VALUES (?, ?, ?, ?)",
            (nome, email, hash_senha(senha, sal), sal),
        )
    except sqlite3.IntegrityError:
        raise ErroAPI(409, "Já existe uma conta com este e-mail.")
    jid = cur.lastrowid
    token = criar_sessao(con, jid)
    return {"token": token, "jogador": {"id": jid, "nome": nome, "email": email}}


def autenticar(con: sqlite3.Connection, d: dict, ip: str) -> dict:
    email = str(d.get("email", "")).strip().lower()
    senha = d.get("senha")
    if not email or not isinstance(senha, str):
        raise ErroAPI(400, "Informe e-mail e senha.")
    chave = (ip, email)
    with _falhas_lock:
        recentes = [t for t in _falhas.get(chave, []) if time.time() - t < 300]
        _falhas[chave] = recentes
        if len(recentes) >= 10:
            raise ErroAPI(429, "Muitas tentativas. Aguarde alguns minutos.")
    row = con.execute("SELECT * FROM jogador WHERE email = ?", (email,)).fetchone()
    # compara mesmo se o e-mail não existe, para não revelar quais contas existem
    sal = row["senha_salt"] if row else "00" * 16
    calc = hash_senha(senha, sal)
    if not row or not hmac.compare_digest(calc, row["senha_hash"]):
        with _falhas_lock:
            _falhas.setdefault(chave, []).append(time.time())
        raise ErroAPI(401, "E-mail ou senha incorretos.")
    with _falhas_lock:
        _falhas.pop(chave, None)
    token = criar_sessao(con, row["id"])
    return {"token": token, "jogador": {"id": row["id"], "nome": row["nome"], "email": row["email"]}}


def jogador_do_token(con: sqlite3.Connection, cabecalho: str) -> sqlite3.Row:
    if not cabecalho.startswith("Bearer "):
        raise ErroAPI(401, "Faça login.")
    token = cabecalho[7:].strip()
    row = con.execute(
        "SELECT j.* FROM sessao s JOIN jogador j ON j.id = s.jogador_id "
        "WHERE s.token_hash = ? AND s.expira_em > ?",
        (hash_token(token), agora()),
    ).fetchone()
    if not row:
        raise ErroAPI(401, "Sessão expirada. Faça login novamente.")
    return row


def carregar_progresso(con: sqlite3.Connection, jid: int) -> dict:
    p = con.execute("SELECT sala_atual, vida FROM progresso WHERE jogador_id = ?", (jid,)).fetchone()
    if not p:
        return {"existe": False}
    inv = {r["item_id"]: r["quantidade"] for r in con.execute(
        "SELECT item_id, quantidade FROM inventario WHERE jogador_id = ?", (jid,))}
    learned = [r["receita_id"] for r in con.execute(
        "SELECT receita_id FROM receita_aprendida WHERE jogador_id = ? ORDER BY rowid", (jid,))]
    flags, taken = {}, {}
    for r in con.execute("SELECT tipo, chave FROM marcador WHERE jogador_id = ?", (jid,)):
        (flags if r["tipo"] == "flag" else taken)[r["chave"]] = True
    return {"existe": True, "room": p["sala_atual"], "hp": p["vida"], "inv": inv,
            "flags": flags, "learned": learned, "taken": taken}


def gravar_progresso(con: sqlite3.Connection, jid: int, d: dict) -> None:
    sala = d.get("room")
    vida = d.get("hp")
    if not isinstance(sala, int) or isinstance(sala, bool):
        raise ErroAPI(400, "Campo 'room' inválido.")
    if not isinstance(vida, int) or isinstance(vida, bool) or not 0 <= vida <= 3:
        raise ErroAPI(400, "Campo 'hp' inválido (0 a 3).")
    if not con.execute("SELECT 1 FROM sala WHERE id = ?", (sala,)).fetchone():
        raise ErroAPI(400, "Sala inexistente.")
    inv, learned = d.get("inv", {}), d.get("learned", [])
    flags, taken = d.get("flags", {}), d.get("taken", {})
    if not (isinstance(inv, dict) and isinstance(learned, list) and isinstance(flags, dict) and isinstance(taken, dict)):
        raise ErroAPI(400, "Formato de progresso inválido.")
    if len(flags) > 2000 or len(taken) > 2000 or len(inv) > 100 or len(learned) > 100:
        raise ErroAPI(400, "Progresso grande demais.")
    itens = {r["id"] for r in con.execute("SELECT id FROM item")}
    receitas = {r["item_id"] for r in con.execute("SELECT item_id FROM receita")}
    for k, q in inv.items():
        if k not in itens:
            raise ErroAPI(400, f"Item desconhecido: {k}")
        if not isinstance(q, int) or isinstance(q, bool) or not 0 <= q <= 999:
            raise ErroAPI(400, f"Quantidade inválida para {k}.")
    for r in learned:
        if r not in receitas:
            raise ErroAPI(400, f"Receita desconhecida: {r}")
    for mapa in (flags, taken):
        for k in mapa:
            if not isinstance(k, str) or not CHAVE_RE.match(k):
                raise ErroAPI(400, "Chave de marcador inválida.")
    con.execute(
        "INSERT INTO progresso (jogador_id, sala_atual, vida, atualizado_em) VALUES (?, ?, ?, ?) "
        "ON CONFLICT(jogador_id) DO UPDATE SET sala_atual = excluded.sala_atual, "
        "vida = excluded.vida, atualizado_em = excluded.atualizado_em",
        (jid, sala, vida, agora()),
    )
    con.execute("DELETE FROM inventario WHERE jogador_id = ?", (jid,))
    con.executemany("INSERT INTO inventario (jogador_id, item_id, quantidade) VALUES (?, ?, ?)",
                    [(jid, k, q) for k, q in inv.items() if q > 0])
    con.execute("DELETE FROM receita_aprendida WHERE jogador_id = ?", (jid,))
    con.executemany("INSERT OR IGNORE INTO receita_aprendida (jogador_id, receita_id) VALUES (?, ?)",
                    [(jid, r) for r in learned])
    con.execute("DELETE FROM marcador WHERE jogador_id = ?", (jid,))
    con.executemany("INSERT INTO marcador (jogador_id, tipo, chave) VALUES (?, ?, ?)",
                    [(jid, "flag", k) for k in flags] + [(jid, "coleta", k) for k in taken])


def _instante(valor) -> str:
    """Aceita o horário informado pelo jogo (eventos guardados offline) se for plausível."""
    if isinstance(valor, str):
        try:
            dt = datetime.fromisoformat(valor.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            dt = dt.astimezone(timezone.utc)
            agora_dt = datetime.now(timezone.utc)
            if agora_dt - timedelta(days=30) <= dt <= agora_dt + timedelta(minutes=5):
                return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        except ValueError:
            pass
    return agora()


def registrar_eventos(con: sqlite3.Connection, jid: int, d: dict) -> int:
    lista = d.get("eventos") if isinstance(d.get("eventos"), list) else [d]
    if not 1 <= len(lista) <= 200:
        raise ErroAPI(400, "Envie de 1 a 200 eventos.")
    tipos = {r["codigo"]: r["id"] for r in con.execute("SELECT id, codigo FROM tipo_erro")}
    linhas = []
    for e in lista:
        if not isinstance(e, dict):
            raise ErroAPI(400, "Evento inválido.")
        tipo = tipos.get(e.get("tipo"))
        if tipo is None:
            raise ErroAPI(400, f"Tipo de erro desconhecido: {e.get('tipo')}")
        sala = e.get("sala")
        if not isinstance(sala, int) or isinstance(sala, bool) or not con.execute(
                "SELECT 1 FROM sala WHERE id = ?", (sala,)).fetchone():
            raise ErroAPI(400, "Sala inválida no evento.")
        detalhe = str(e.get("detalhe", ""))[:200]
        linhas.append((jid, tipo, sala, detalhe, _instante(e.get("quando"))))
    con.executemany(
        "INSERT INTO evento_erro (jogador_id, tipo_erro_id, sala_id, detalhe, ocorrido_em) VALUES (?, ?, ?, ?, ?)",
        linhas)
    return len(linhas)


def montar_relatorio(con: sqlite3.Connection, jogador: sqlite3.Row, limite: int) -> dict:
    jid = jogador["id"]
    por_tipo = [dict(r) for r in con.execute(
        "SELECT t.codigo, t.descricao, COUNT(e.id) AS total FROM tipo_erro t "
        "LEFT JOIN evento_erro e ON e.tipo_erro_id = t.id AND e.jogador_id = ? "
        "GROUP BY t.id ORDER BY t.id", (jid,))]
    por_sala = [dict(r) for r in con.execute(
        "SELECT s.id AS sala_id, s.nome, COUNT(e.id) AS total FROM sala s "
        "LEFT JOIN evento_erro e ON e.sala_id = s.id AND e.jogador_id = ? "
        "GROUP BY s.id ORDER BY s.id", (jid,))]
    total, primeiro, ultimo = con.execute(
        "SELECT COUNT(*), MIN(ocorrido_em), MAX(ocorrido_em) FROM evento_erro WHERE jogador_id = ?",
        (jid,)).fetchone()
    top = []
    for r in con.execute(
            "SELECT t.codigo, e.detalhe, COUNT(*) AS total FROM evento_erro e "
            "JOIN tipo_erro t ON t.id = e.tipo_erro_id WHERE e.jogador_id = ? AND e.detalhe <> '' "
            "GROUP BY t.codigo, e.detalhe ORDER BY total DESC, e.detalhe", (jid,)):
        if sum(1 for x in top if x["codigo"] == r["codigo"]) < 5:
            top.append(dict(r))
    eventos = [dict(r) for r in con.execute(
        "SELECT e.id, e.ocorrido_em AS quando, t.codigo AS tipo, t.descricao, e.sala_id, s.nome AS sala, e.detalhe "
        "FROM evento_erro e JOIN tipo_erro t ON t.id = e.tipo_erro_id JOIN sala s ON s.id = e.sala_id "
        "WHERE e.jogador_id = ? ORDER BY e.ocorrido_em DESC, e.id DESC LIMIT ?", (jid, limite))]
    prog = carregar_progresso(con, jid)
    return {
        "jogador": {"id": jid, "nome": jogador["nome"], "email": jogador["email"], "criado_em": jogador["criado_em"]},
        "progresso": {"sala": prog.get("room"), "vida": prog.get("hp")} if prog["existe"] else None,
        "resumo": {"total": total, "primeiro": primeiro, "ultimo": ultimo,
                   "por_tipo": por_tipo, "por_sala": por_sala, "mais_comuns": top},
        "eventos": eventos,
    }


# ----------------------------------------------------------------------------
# HTTP
# ----------------------------------------------------------------------------
class Handler(BaseHTTPRequestHandler):
    server_version = "RatoCyberLab/1.0"
    caminho_db = DB_PADRAO

    # -- utilidades --
    def log_message(self, fmt, *args):  # log curto no terminal
        if not getattr(self.server, "silencioso", False):
            sys.stderr.write("%s  %s\n" % (time.strftime("%H:%M:%S"), fmt % args))

    def _enviar(self, status: int, corpo: bytes, tipo: str, extra: dict | None = None) -> None:
        self.send_response(status)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(corpo)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Cache-Control", "no-store")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(corpo)

    def _json(self, status: int, obj) -> None:
        self._enviar(status, json.dumps(obj, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

    def _ler_json(self) -> dict:
        try:
            n = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            n = 0
        if n <= 0:
            return {}
        if n > MAX_CORPO:
            raise ErroAPI(413, "Corpo grande demais.")
        try:
            d = json.loads(self.rfile.read(n).decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            raise ErroAPI(400, "JSON inválido.")
        if not isinstance(d, dict):
            raise ErroAPI(400, "Esperava um objeto JSON.")
        return d

    # -- roteamento --
    def _tratar(self) -> None:
        url = urlparse(self.path)
        rota = url.path.rstrip("/") or "/"
        try:
            if self.command in ("GET", "HEAD") and rota in ("/", "/relatorio"):
                if rota == "/":
                    return self._enviar(302, b"", "text/plain", {"Location": "/relatorio"})
                html = (AQUI / "relatorio" / "index.html").read_bytes()
                return self._enviar(200, html, "text/html; charset=utf-8", {
                    "Content-Security-Policy": "default-src 'self'; style-src 'unsafe-inline'; "
                                               "script-src 'unsafe-inline'; connect-src 'self'"})
            if not rota.startswith("/api/"):
                raise ErroAPI(404, "Não encontrado.")
            con = conectar(self.caminho_db)
            try:
                resposta = self._api(con, rota, url.query)
                con.commit()
            except BaseException:
                con.rollback()
                raise
            finally:
                con.close()
            status, corpo = resposta
            if status == 204:
                self._enviar(204, b"", "application/json")
            else:
                self._json(status, corpo)
        except ErroAPI as e:
            self._json(e.status, {"erro": e.mensagem})
        except Exception as e:  # erro inesperado: não vaza detalhes para o cliente
            sys.stderr.write(f"ERRO interno: {e!r}\n")
            self._json(500, {"erro": "Erro interno do servidor."})

    def _api(self, con: sqlite3.Connection, rota: str, query: str):
        m = self.command
        if rota == "/api/saude" and m == "GET":
            return 200, {"ok": True, "hora": agora()}
        if rota == "/api/cadastro" and m == "POST":
            return 201, cadastrar(con, self._ler_json())
        if rota == "/api/login" and m == "POST":
            return 200, autenticar(con, self._ler_json(), self.client_address[0])
        if rota in ("/api/logout", "/api/progresso", "/api/eventos", "/api/relatorio"):
            jogador = jogador_do_token(con, self.headers.get("Authorization", ""))
            if rota == "/api/logout" and m == "POST":
                con.execute("DELETE FROM sessao WHERE token_hash = ?",
                            (hash_token(self.headers["Authorization"][7:].strip()),))
                return 204, None
            if rota == "/api/progresso" and m == "GET":
                return 200, carregar_progresso(con, jogador["id"])
            if rota == "/api/progresso" and m == "PUT":
                gravar_progresso(con, jogador["id"], self._ler_json())
                return 204, None
            if rota == "/api/eventos" and m == "POST":
                return 201, {"registrados": registrar_eventos(con, jogador["id"], self._ler_json())}
            if rota == "/api/relatorio" and m == "GET":
                try:
                    lim = int(parse_qs(query).get("limite", ["300"])[0])
                except ValueError:
                    lim = 300
                return 200, montar_relatorio(con, jogador, max(1, min(lim, 1000)))
        raise ErroAPI(404 if rota.startswith("/api/") else 405, "Rota ou método não suportado.")

    do_GET = do_POST = do_PUT = do_HEAD = _tratar


def criar_servidor(host: str, porta: int, caminho_db: str = DB_PADRAO, silencioso: bool = False) -> ThreadingHTTPServer:
    iniciar_banco(caminho_db)

    class H(Handler):
        pass

    H.caminho_db = caminho_db
    srv = ThreadingHTTPServer((host, porta), H)
    srv.silencioso = silencioso
    srv.daemon_threads = True
    return srv


def main() -> None:
    ap = argparse.ArgumentParser(description="Backend do Rato CyberLab")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--db", default=DB_PADRAO, help="arquivo SQLite (padrão: backend/rato_cyberlab.db)")
    a = ap.parse_args()
    srv = criar_servidor(a.host, a.port, a.db)
    print(f"Rato CyberLab - backend no ar em http://{a.host}:{a.port}")
    print(f"  Relatório de erros: http://{a.host}:{a.port}/relatorio")
    print(f"  Banco de dados:     {a.db}")
    print("  Ctrl+C para parar.")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor encerrado.")


if __name__ == "__main__":
    main()
