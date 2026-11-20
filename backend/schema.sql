-- ============================================================================
-- Rato CyberLab (Projeto R-31) - Script de criação do banco de dados (SQLite)
-- Projeto e Engenharia de Software - UNA Barreiro
--
-- Como usar:  sqlite3 rato_cyberlab.db < schema.sql
-- (o backend/server.py executa este script sozinho na primeira inicialização)
--
-- Modelo em 3FN. Datas em UTC, formato ISO 8601 (texto).
-- ============================================================================

PRAGMA foreign_keys = ON;

-- ---------------------------------------------------------------------------
-- 1. CONTAS E SESSÕES (cadastro / login)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS jogador (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    nome        TEXT    NOT NULL CHECK (length(nome) BETWEEN 2 AND 60),
    email       TEXT    NOT NULL UNIQUE CHECK (email LIKE '%_@_%._%'),
    senha_hash  TEXT    NOT NULL,                 -- PBKDF2-HMAC-SHA256 (hex)
    senha_salt  TEXT    NOT NULL,                 -- sal aleatório por jogador (hex)
    criado_em   TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE TABLE IF NOT EXISTS sessao (
    token_hash  TEXT    PRIMARY KEY,              -- SHA-256 do token entregue ao jogo
    jogador_id  INTEGER NOT NULL REFERENCES jogador (id) ON DELETE CASCADE,
    criado_em   TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    expira_em   TEXT    NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_sessao_jogador ON sessao (jogador_id);

-- ---------------------------------------------------------------------------
-- 2. CATÁLOGO DO JOGO (dados fixos: salas, itens e receitas)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS sala (
    id    INTEGER PRIMARY KEY,                    -- 0 = tutorial (gaiola) ... 10 = chefe
    nome  TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS item (
    id         TEXT PRIMARY KEY,                  -- identificador usado pelo jogo (ex.: 'fe', 'agua')
    nome       TEXT NOT NULL,
    simbolo    TEXT NOT NULL,
    tipo       TEXT NOT NULL CHECK (tipo IN ('elemento', 'ficticio', 'fabricado')),
    descricao  TEXT NOT NULL
);

-- Cada receita produz exatamente um item fabricado.
CREATE TABLE IF NOT EXISTS receita (
    item_id      TEXT    PRIMARY KEY REFERENCES item (id),
    requer_fogo  INTEGER NOT NULL DEFAULT 0 CHECK (requer_fogo IN (0, 1))
);

CREATE TABLE IF NOT EXISTS ingrediente_receita (
    receita_id  TEXT    NOT NULL REFERENCES receita (item_id),
    item_id     TEXT    NOT NULL REFERENCES item (id),
    quantidade  INTEGER NOT NULL CHECK (quantidade > 0),
    PRIMARY KEY (receita_id, item_id)
);

-- ---------------------------------------------------------------------------
-- 3. PROGRESSO DO JOGADOR (substitui o save em JSON local)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS progresso (
    jogador_id     INTEGER PRIMARY KEY REFERENCES jogador (id) ON DELETE CASCADE,
    sala_atual     INTEGER NOT NULL REFERENCES sala (id),
    vida           INTEGER NOT NULL CHECK (vida BETWEEN 0 AND 3),
    atualizado_em  TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS inventario (
    jogador_id  INTEGER NOT NULL REFERENCES jogador (id) ON DELETE CASCADE,
    item_id     TEXT    NOT NULL REFERENCES item (id),
    quantidade  INTEGER NOT NULL CHECK (quantidade > 0),
    PRIMARY KEY (jogador_id, item_id)
);

CREATE TABLE IF NOT EXISTS receita_aprendida (
    jogador_id  INTEGER NOT NULL REFERENCES jogador (id) ON DELETE CASCADE,
    receita_id  TEXT    NOT NULL REFERENCES receita (item_id),
    PRIMARY KEY (jogador_id, receita_id)
);

-- Marcos da campanha: 'flag' = evento de história concluído (porta aberta,
-- animal resgatado, chefe derrotado...); 'coleta' = item/armário já recolhido
-- ou introdução de sala já vista.
CREATE TABLE IF NOT EXISTS marcador (
    jogador_id  INTEGER NOT NULL REFERENCES jogador (id) ON DELETE CASCADE,
    tipo        TEXT    NOT NULL CHECK (tipo IN ('flag', 'coleta')),
    chave       TEXT    NOT NULL,
    PRIMARY KEY (jogador_id, tipo, chave)
);

-- ---------------------------------------------------------------------------
-- 4. RELATÓRIO DE ERROS
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS tipo_erro (
    id         INTEGER PRIMARY KEY,
    codigo     TEXT    NOT NULL UNIQUE,
    descricao  TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS evento_erro (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    jogador_id    INTEGER NOT NULL REFERENCES jogador (id) ON DELETE CASCADE,
    tipo_erro_id  INTEGER NOT NULL REFERENCES tipo_erro (id),
    sala_id       INTEGER NOT NULL REFERENCES sala (id),
    detalhe       TEXT    NOT NULL DEFAULT '',
    ocorrido_em   TEXT    NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_erro_jogador_data ON evento_erro (jogador_id, ocorrido_em);

-- Tipos de erro registrados pelo jogo
INSERT OR IGNORE INTO tipo_erro (id, codigo, descricao) VALUES
    (1, 'FORMULA_ERRADA',  'Fórmula química incorreta no computador do armário'),
    (2, 'RECEITA_INVALIDA', 'Combinação inválida ou incompleta na bancada de craft'),
    (3, 'DANO',            'Dano sofrido por perigo, robô, monstro ou chefe'),
    (4, 'MORTE',           'Vida zerada: o jogador foi recapturado');
