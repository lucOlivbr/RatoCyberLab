# Rato CyberLab

Aventura 2D top-down cyberpunk: um rato foge de um laboratório secreto em 10 salas, usando a Bancada de Craft (12 slots), puzzles, NPCs e muita ciência.

## Como abrir
1. Abra o Godot 4.x (janela inicial 960x540; testado com 4.4.1; deve funcionar em versões 4.4+ mais novas).
2. Importar → selecione `project.godot`. Na primeira abertura o Godot importa os assets (alguns segundos).
3. F5 para jogar (cena principal: `scenes/main.tscn`).

## Controles
WASD/setas mover (o rato anda em pé, sobre duas pernas) · Shift corre sobre 4 patas, na mesma direção · E interagir · C bancada · I inventário · F usar gel · H dica · R resetar caixas · Esc pausa.
Bancada: coloque itens nos slots e clique FABRICAR. Nada é consumido se a receita for inválida. Botão direito em item fabricado = reciclar.

## Estrutura
- `scripts/` código (game.gd = autoload com estado, itens e receitas)
- `data/rooms_data.gd` salas (geradas por `tools/rooms_def.py`)
- `assets/` pixel art gerada
- `tests/` playtest headless: `godot --headless --path . --script res://tests/playtest.gd`
- `tools/` geradores de salas e arte (Python + PIL)

Save automático em `user://rato_cyberlab_save.json`.


## Versão completa (Projeto R-31)
- Abertura em quadrinhos (Esc pula), Fase 0 (tutorial na gaiola) e 10 salas.
- Bancada: arraste itens para os recipientes; o maçarico acende com clique/Espaço e esquenta pelas setas ▲▼ do painel TEMP (também ↑/↓). Receitas com fogo exigem 220°C ou mais.
- Armários trancados com minigame de fórmulas (NaCl, H2O, CO2, NH3, CH4, HCl, NaOH, CaO, H2O2) e armários com receitas.
- Sala 4: veneno em todo o mapa, zonas seguras e caminhos de rato. Sala 5: válvulas de vapor. Sala 6: drones perseguem (menos na zona da bancada). Sala 7: 5 caixas e 5 placas. Sala 8: 2 monstros. Sala 9: 3 robôs. Sala 10: Voss lança bolas de laser, bomba no núcleo central, contagem de 5 s e final.
- Tools: `tools/rooms_def.py` (mapas) -> `python3 tools/rooms_def.py` e `python3 tools/rooms_bg.py` regeram dados e fundos; `tools/end_art.py` gera a arte do final.
- Testes: `tests/playtest.gd`, `tests/reach.gd` (headless).

## Atualização R-31
- Protagonista renomeado para **R-31**; andar e correr nas 4 direções usam a folha enviada (`tools/r31_from_sheet.py`).
- Dr. Voss e Dra. Okoye refeitos a partir da folha de cientistas (Okoye não usa arma nem seringa) — `tools/sci_from_sheet.py`.
- Bancada: sem chama quando o maçarico está desligado; chama azul só quando ligado.
- Ratos libertados e cena final usam ratos normais (`tools/nrats_from_sheet.py`); quadrinhos com o novo Voss e rato normal.
- Sala final: o Dr. Voss faz o discurso e começa a atirar sozinho ao você entrar.

## Atualização: trilhas, raios e dicas
- **Trilhas sonoras chiptune** (assets/music, geradas por `tools/music_build.py`): `lab` (menu e salas 0–2), `energia` (sala 3), `mutacao` (salas 4, 5 e 8), `seguranca` (salas 6, 7 e 9) e `chefe` (sala 10). Tocam em loop e trocam sozinhas ao mudar de sala (`play_music` em scripts/main.gd).
- Sala 3: os dois armários de baixo agora também têm raios na parte de cima.
- As dicas das fórmulas dos armários foram reescritas, mais difíceis (charadas com número atômico, grupo e uso do composto).
