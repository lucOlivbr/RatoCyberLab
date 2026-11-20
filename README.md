# Rato CyberLab (Projeto R-31)

Jogo 2D de aventura e ciência: um rato foge de um laboratório resolvendo fórmulas químicas e fabricando itens.
O projeto tem três camadas:

| Camada | Pasta | Tecnologia |
|---|---|---|
| Frontend (o jogo) | `proj/` | Godot 4.4 (GDScript) |
| Backend (API) | `backend/` | Python 3, só biblioteca padrão |
| Banco de dados | `backend/schema.sql` | SQLite |

O jogador **cria uma conta**, o progresso fica **no banco**, e cada erro (fórmula errada, receita inválida, dano, recaptura) é registrado para um **relatório** que mostra quando e onde ele errou.

## Como rodar

1. **Backend** (precisa só do Python 3.9+):
   - Windows: dê dois cliques em `iniciar_backend.bat`.
   - Linux/Mac: `./iniciar_backend.sh`
   - Ou: `cd backend && python3 server.py` (abre em http://127.0.0.1:8000).
2. **Jogo:** abra `proj/project.godot` no Godot 4.4+ e aperte F5.
   Na primeira tela, escolha **CADASTRAR**, ou **ENTRAR** se já tiver conta. **JOGAR SEM CONTA** funciona sem o backend.
3. **Relatório de erros:** no menu de pausa (Esc), botão *RELATÓRIO DE ERROS*. Ou abra http://127.0.0.1:8000/relatorio e entre com a mesma conta.

Para mostrar o relatório já cheio numa apresentação: `cd backend && python3 demo.py` cria a conta `demo@rato.lab` / `demo1234` com erros de exemplo.

Se o backend estiver em outro computador, defina a variável `RATO_API` (ex.: `http://192.168.0.10:8000`) ou crie o arquivo `rato_config.json` na pasta de dados do jogo com `{"api_url": "http://192.168.0.10:8000"}`. Inicie o servidor com `python3 server.py --host 0.0.0.0`.

## Testes

```
cd backend && python3 -m unittest discover -s tests -v          # 16 testes da API
cd proj && godot --headless --path . --script res://tests/playtest.gd   # as 11 salas
# ponta a ponta (jogo + backend + banco):
cd backend && RATO_DB=/tmp/e2e.db python3 server.py --port 8123 &
cd proj && RATO_API=http://127.0.0.1:8123 godot --headless --path . --script res://tests/api_e2e.gd
```

## Documentação

`docs/DOCUMENTACAO_BANCO_DE_DADOS.md` reúne a arquitetura, o caso de uso, o DER, o modelo relacional, o dicionário de dados, a normalização e a API. Os diagramas estão em `docs/diagramas/`.
O README do jogo (controles, salas, arte) está em `proj/README.md`.

## Equipe

Equipe R-31 · Projeto e Engenharia de Software · UNA Barreiro.
