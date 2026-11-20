# -*- coding: utf-8 -*-
"""Definição dos 10 mapas do Rato CyberLab. Gera data/rooms.json
Grade 30x15 tiles de 32px (960x480). Coordenadas de objetos em tiles."""
import json, os
W, H = 30, 15

def blank():
    g = [['.'] * W for _ in range(H)]
    for x in range(W):
        g[0][x] = '#'; g[1][x] = '#'; g[14][x] = '#'
    for y in range(H):
        g[y][0] = '#'; g[y][W - 1] = '#'
    return g

def wall(g, x, y, w=1, h=1):
    for j in range(y, y + h):
        for i in range(x, x + w):
            g[j][i] = '#'

def door_cells(g, x, y, w, h):
    for j in range(y, y + h):
        for i in range(x, x + w):
            g[j][i] = 'D'

def prev_door(to, x=14):
    return {"type": "door", "x": x, "y": 14, "w": 2, "h": 1, "to": to, "spawn": "next", "back": True}

def exit_door(to, x, needs=None, msg="", kind="door"):
    d = {"type": "door", "x": x, "y": 0, "w": 2, "h": 2, "to": to, "spawn": "prev", "kind": kind}
    if needs:
        d["needs_flag"] = needs
        d["locked_msg"] = msg
    return d

def decor(kind, x, y, w=1, h=1, solid=True, **kw):
    d = {"type": "decor", "kind": kind, "x": x, "y": y, "w": w, "h": h, "solid": solid}
    d.update(kw)
    return d

def terminal(id_, x, y, title, lines, learn=None):
    return {"type": "terminal", "id": id_, "x": x, "y": y, "title": title, "lines": lines, "learn": learn or []}

def locker(id_, x, y, items, puzzle=None, learn=None):
    d = {"type": "locker", "id": id_, "x": x, "y": y, "items": items}
    if puzzle:
        d["puzzle"] = puzzle
    if learn:
        d["learn"] = learn
    return d


def puzzle(formula, tokens, decoys, question, hint):
    return {"formula": formula, "tokens": tokens, "decoys": decoys, "question": question, "hint": hint}

def pickup(id_, x, y, item, qty=1):
    return {"type": "pickup", "id": id_, "x": x, "y": y, "item": item, "qty": qty}

def bench(x, y):
    return {"type": "bench", "x": x, "y": y, "w": 3, "h": 2}

def obstacle(id_, kind, x, y, w, h, needs, flag, consume, blocks, label, ok, fail):
    return {"type": "obstacle", "id": id_, "kind": kind, "x": x, "y": y, "w": w, "h": h, "needs": needs,
            "flag": flag, "consume": consume, "blocks": blocks, "label": label, "ok_msg": ok, "fail_msg": fail}

ROOMS = []

# ---------------------------------------------------------------- 0 (tutorial)
g = [['#'] * W for _ in range(H)]
for yy in range(4, 12):
    for xx in range(8, 22):
        g[yy][xx] = '.'
door_cells(g, 14, 2, 2, 2)
ROOMS.append({
    "id": 0, "name": "Gaiola Experimental", "theme": "cyan", "grid": g, "broken_bench": True,
    "spawn_prev": [14, 8], "spawn_next": [14, 8],
    "intro": ["A gaiola é pequena e as grades, firmes.", "Há frascos espalhados pelo chão e uma bancada velha, quebrada. Talvez dê para improvisar."],
    "needs": [["acido", "r0_open"]],
    "stages": [
        {"done": "flag:t_moved", "text": "Mova-se com WASD ou as setas (Shift corre)",
         "hint": "Use W A S D ou as setas para andar pela gaiola."},
        {"done": "item:h&item:o&item:so|item:acido|flag:r0_open", "text": "Colete os frascos do chão: 2 H, 3 O e 1 SO (chegue perto e aperte E)",
         "hint": "Os frascos brilham no chão: hidrogênio (H), oxigênio (O) e monóxido de enxofre (SO)."},
        {"done": "flag:t_inv|item:acido|flag:r0_open", "text": "Aperte I para ver o inventário",
         "hint": "A tecla I abre o inventário. Esc ou I fecha."},
        {"done": "flag:t_bench|item:acido|flag:r0_open", "text": "Vá até a bancada quebrada e aperte C (ou E)",
         "hint": "A bancada fica no canto direito da gaiola."},
        {"done": "item:acido|flag:r0_open", "text": "Na bancada: arraste 2 H, 1 SO e 3 O para os recipientes, acenda o maçarico (Espaço) e fabrique (Enter)",
         "hint": "Cada recipiente guarda um tipo de item: H num, SO em outro, O no terceiro. Acenda o maçarico e aperte FABRICAR. Se errar, nada é gasto."},
        {"done": "flag:r0_open", "text": "Use o ácido sulfúrico nas grades da jaula (E) para derretê-las",
         "hint": "Chegue perto das grades de cima, no meio, e aperte E."},
    ],
    "final": "As grades derreteram. Saia da jaula!",
    "objects": [
        {"type": "door", "x": 14, "y": 2, "w": 2, "h": 2, "to": 1, "spawn": "prev", "kind": "door", "needs_flag": "r0_open", "locked_msg": "As grades ainda bloqueiam a saída."},
        obstacle("r0_bars", "bars", 14, 4, 2, 2, "acido", "r0_open", True, True,
                 "Grades da jaula", "O ácido corrói o aço. As grades se desfazem em fumaça verde!",
                 "As grades são de aço reforçado. Só algo corrosivo as derreteria."),
        terminal("r0_t1", 11, 4, "ANOTAÇÃO // TÉCNICO", [
            "Lembrete do técnico: o rato R-31 rói qualquer coisa, menos aço reforçado.",
            "Se algum dia o bicho escapasse: ácido sulfúrico corrói o aço. Receita: 2 hidrogênios (H) + 1 monóxido de enxofre (SO) + 3 oxigênios (O).",
            "A mistura precisa de calor: acender o maçarico da bancada. A bancada daqui está quebrada, mas ainda funciona.",
        ], ["acido"]),
        bench(17, 8),
        pickup("r0_p1", 10, 7, "h", 2),
        pickup("r0_p2", 10, 10, "o", 3),
        pickup("r0_p3", 14, 10, "so", 1),
        decor("sign", 13, 3, 4, 1, False, text="JAULA R-31"),
        decor("lamp", 12, 5, 6, 6, False),
    ],
})

# ---------------------------------------------------------------- 1
g = blank()
door_cells(g, 23, 0, 2, 2)
ROOMS.append({
    "id": 1, "name": "Cela de Contenção", "theme": "cyan", "grid": g,
    "spawn_prev": [14, 6], "spawn_next": [23, 4],
    "intro": ["Estou fora da jaula, mas a sala continua trancada.", "Preciso de uma chave de manutenção para o painel ao lado da porta."],
    "needs": [["chave_manut", "r1_open"]],
    "stages": [
        {"done": "item:chave_manut|flag:r1_open", "text": "Reúna 1 ferro e 2 engrenagens nos armários (um está trancado) e fabrique a Chave de manutenção (bancada, C)",
         "hint": "Um armário está aberto. O outro, no canto direito, pede a fórmula do sal de cozinha."},
        {"done": "flag:r1_open", "text": "Use a chave no painel de manutenção ao lado da porta",
         "hint": "Chegue perto do painel e aperte E."},
    ],
    "final": "Atravesse a porta para o Laboratório de Misturas.",
    "objects": [
        exit_door(2, 23, "r1_open", "A porta está trancada. O painel de manutenção ao lado precisa de uma chave."),
        obstacle("r1_panel", "panel", 21, 2, 1, 1, "chave_manut", "r1_open", False, False,
                 "Painel de manutenção", "Os parafusos cedem. A porta destranca!",
                 "O painel exige uma Chave de manutenção. Fabrique uma na bancada."),
        terminal("r1_t1", 6, 2, "TERMINAL // CONTENÇÃO 01", [
            "REGISTRO 0147: Sujeito R-31 mantido na gaiola de contenção principal.",
            "NOTA DO TÉCNICO: perdi a chave dos painéis de novo. Dá pra montar outra na bancada: 2 engrenagens + 1 ferro, com o maçarico aceso para moldar.",
            "O armário da direita está trancado com código. Pista: é o nome químico do sal de cozinha, cloreto de sódio.",
            "Há outros sujeitos presos nos setores seguintes. Eles continuarão nos testes.",
        ], ["chave_manut"]),
        locker("r1_l1", 3, 2, {"fe": 1, "engrenagem": 1}),
        locker("r1_l2", 27, 2, {"engrenagem": 1, "gel": 1},
               puzzle("NaCl", ["N", "a", "C", "l"], ["H", "O", "K", "e", "S", "i"],
                      "Qual é a fórmula do SAL DE COZINHA (cloreto de sódio)?",
                      "Metal alcalino do 3º período mais o halogênio do mesmo período, na proporção de 1 para 1. A segunda letra de cada símbolo é minúscula.")),
        bench(17, 2),
        decor("cage_start", 13, 3, 3, 2),
        decor("shelf", 2, 10, 2, 2),
        decor("rack", 26, 7, 1, 2),
        decor("rack", 26, 9, 1, 2),
        decor("tank", 26, 11, 2, 2),
        decor("computer", 7, 5, 2, 1),
        decor("computer", 20, 5, 2, 1),
        decor("potions", 8, 9, 3, 2),
        decor("books", 22, 10, 2, 2),
        decor("desk", 16, 11, 3, 1),
        decor("potions", 12, 12, 2, 1),
        decor("sign", 9, 1, 3, 1, False, text="CONTENCAO 01"),
        decor("pipe", 1, 1, 8, 1, False),
        decor("pipe", 13, 1, 8, 1, False),
        decor("lamp", 14, 7, 3, 3, False),
        decor("machine", 2, 6, 2, 2),
    ],
})


def steam(x, y, w, h, on=1.5, off=2.5, phase=0.0):
    return {"type": "hazard", "kind": "steam", "x": x, "y": y, "w": w, "h": h, "on": on, "off": off, "phase": phase, "dmg": 1}

def electric_ring(lx, ly, phase0=0.0, on=1.4, off=2.8, top=False):
    """3 faixas elétricas em U ao redor de um armário (frente, esquerda e direita)."""
    return [
        {"type": "hazard", "kind": "electric", "x": lx - 1, "y": ly + 1, "w": 3, "h": 1, "on": on, "off": off, "phase": phase0, "dmg": 1},
        {"type": "hazard", "kind": "electric", "x": lx - 1, "y": ly, "w": 1, "h": 1, "on": on, "off": off, "phase": phase0 + on, "dmg": 1},
        {"type": "hazard", "kind": "electric", "x": lx + 1, "y": ly, "w": 1, "h": 1, "on": on, "off": off, "phase": phase0 + 2 * on, "dmg": 1},
    ] + ([{"type": "hazard", "kind": "electric", "x": lx - 1, "y": ly - 1, "w": 3, "h": 1, "on": on, "off": off, "phase": phase0 + 1.5 * on, "dmg": 1}] if top else [])

def laser(x, y, w, h, on=0.0, off=0.0, phase=0.0, clear=None, knock=60):
    d = {"type": "hazard", "kind": "laser", "x": x, "y": y, "w": w, "h": h, "dmg": 1, "knock": knock, "phase": phase}
    if on:
        d["on"] = on; d["off"] = off
    if clear:
        d["clear_flag"] = clear
    return d


# ---------------------------------------------------------------- 2
g = blank()
wall(g, 25, 2, 1, 2); wall(g, 28, 2, 1, 2)
door_cells(g, 26, 0, 2, 2)
ROOMS.append({
    "id": 2, "name": "Laboratório de Misturas", "theme": "purple", "grid": g,
    "spawn_prev": [14, 12], "spawn_next": [26, 4],
    "intro": ["Bancadas de mistura, reagentes e uma passagem congelada.", "Um bom dispositivo térmico resolveria isso. Os armários devem ter a receita e os componentes."],
    "needs": [["termico", "r2_melt"]],
    "stages": [
        {"done": "item:termico|flag:r2_melt", "text": "Abra os 2 armários e fabrique o Dispositivo térmico: núcleo térmico + ferro + cobre",
         "hint": "O armário da esquerda está aberto e guarda a receita. O da direita guarda os componentes, mas pede a fórmula da água."},
        {"done": "flag:r2_melt", "text": "Derreta a barreira de gelo que bloqueia a saída (E)",
         "hint": "O dispositivo térmico funciona ao interagir com a parede congelada."},
    ],
    "final": "A passagem está livre. Siga para a Central de Energia.",
    "objects": [
        prev_door(1),
        exit_door(3, 26),
        obstacle("r2_ice", "ice", 26, 2, 2, 2, "termico", "r2_melt", False, True,
                 "Barreira de gelo", "O gelo evapora em uma nuvem de vapor.",
                 "Uma parede de gelo industrial. Precisa de calor intenso: um Dispositivo térmico."),
        terminal("r2_t1", 10, 2, "TERMINAL // MISTURAS", [
            "PROCEDIMENTO: o sistema de refrigeração congelou o corredor leste.",
            "A receita do Dispositivo térmico está guardada no armário aberto, perto da bancada.",
            "Os componentes ficam no armário trancado da direita. Código: a fórmula da substância mais comum do planeta (H, O e números).",
        ], []),
        bench(13, 2),
        locker("r2_l1", 7, 2, {}, learn=["termico"]),
        locker("r2_l2", 21, 2, {"nucleo": 1, "fe": 1, "cu": 1},
               puzzle("H2O", ["H", "2", "O"], ["N", "a", "C", "l", "K", "3"],
                      "Qual é a fórmula da ÁGUA?",
                      "O elemento mais leve do universo aparece duas vezes; o gás que sustenta a respiração, uma só. Não esqueça o índice.")),
        decor("tank", 2, 2, 2, 3),
        decor("shelf", 4, 2, 2, 1),
        decor("computer", 10, 3, 2, 1),
        decor("computer", 17, 2, 2, 1),
        decor("mixbench", 11, 6, 6, 2),
        decor("potions", 2, 6, 3, 2),
        decor("potions", 23, 6, 3, 2),
        decor("desk", 19, 9, 3, 1),
        decor("computer", 20, 8, 2, 1),
        decor("books", 2, 9, 2, 2),
        decor("tank", 5, 10, 2, 2),
        decor("potions", 8, 10, 3, 2),
        decor("shelf", 24, 10, 1, 3),
        decor("books", 26, 10, 2, 2),
        decor("rack", 27, 5, 1, 2),
        decor("rack", 1, 12, 2, 1),
        decor("sign", 14, 1, 3, 1, False, text="MISTURAS"),
        decor("pipe", 1, 1, 10, 1, False),
        decor("lamp", 12, 5, 4, 4, False),
    ],
})

# ---------------------------------------------------------------- 3
g = blank()
door_cells(g, 14, 0, 2, 2)
_o3 = [
    prev_door(2),
    exit_door(4, 14, "r3_power", "A porta está sem energia. O painel ao lado precisa de um Módulo elétrico."),
    obstacle("r3_panel", "panel", 17, 2, 1, 1, "modulo_eletrico", "r3_power", True, False,
             "Painel de energia", "O módulo se encaixa. A porta recebe energia!",
             "O painel está sem energia. Fabrique um Módulo elétrico."),
    terminal("r3_t1", 9, 2, "TERMINAL // ENERGIA", [
        "AVISO: as faixas de descarga ficam ativas em ciclos. O piso pisca antes de energizar.",
        "Cada armário é cercado por 3 faixas. Espere o clarão laranja de aviso e cruze quando apagar.",
        "Raios orbitam a bancada: não encoste neles. Dica de armário: o gás carbônico é CO e um número.",
    ], []),
    bench(4, 2),
    {"type": "hazard", "kind": "orbit", "x": 4, "y": 2, "w": 3, "h": 2, "n": 2, "speed": 0.7, "rx": 84, "ry": 60, "dmg": 1},
    locker("r3_l1", 24, 2, {}, learn=["modulo_eletrico"]),
    locker("r3_l2", 3, 12, {"cu": 1, "fe": 1},
           puzzle("CO2", ["C", "O", "2"], ["H", "N", "3", "S", "a", "l"],
                  "Qual é a fórmula do GÁS CARBÔNICO (dióxido de carbono)?",
                  "Sai dos pulmões e das chaminés, e as plantas o absorvem. Um átomo do elemento do carvão e dois do gás da respiração.")),
    locker("r3_l3", 26, 12, {"cu": 1, "gel": 1, "celula": 1}),
    decor("reactor", 13, 4, 4, 4),
    decor("rack", 1, 6, 2, 2),
    decor("rack", 27, 5, 1, 2),
    decor("machine", 7, 6, 2, 2),
    decor("machine", 21, 6, 2, 2),
    decor("computer", 11, 2, 2, 1),
    decor("computer", 20, 3, 2, 1),
    decor("shelf", 25, 5, 2, 1),
    decor("desk", 7, 9, 3, 1),
    decor("potions", 20, 9, 3, 2),
    decor("books", 1, 9, 2, 2),
    decor("tank", 11, 9, 2, 2),
    decor("sign", 20, 1, 3, 1, False, text="ENERGIA"),
    decor("pipe", 1, 1, 7, 1, False),
    decor("lamp", 12, 3, 6, 6, False),
]
_o3 += electric_ring(24, 2, 0.0) + electric_ring(3, 12, 1.0, top=True) + electric_ring(26, 12, 2.0, top=True)
ROOMS.append({
    "id": 3, "name": "Central de Energia", "theme": "blue", "grid": g,
    "spawn_prev": [14, 12], "spawn_next": [14, 3],
    "intro": ["O núcleo do complexo pulsa no centro da sala.", "Faixas elétricas cercam os armários e raios rondam a bancada. Preciso cronometrar cada passo."],
    "needs": [["modulo_eletrico", "r3_power"]],
    "stages": [
        {"done": "item:modulo_eletrico|flag:r3_power", "text": "Abra os 3 armários e fabrique o Módulo elétrico: 1 célula de energia + 2 cobres",
         "hint": "Armário do canto direito: receita. Canto esquerdo (CO2): cobre e ferro. Canto direito de baixo: cobre, gel e a célula."},
        {"done": "flag:r3_power", "text": "Instale o módulo no painel de energia ao lado da porta",
         "hint": "O painel fica no alto, perto da porta central."},
    ],
    "final": "Energia restaurada. Siga para o Laboratório de Mutação.",
    "objects": _o3,
})

# ---------------------------------------------------------------- 4
g = blank()
door_cells(g, 26, 0, 2, 2)
ROOMS.append({
    "id": 4, "name": "Laboratório de Mutação", "theme": "green", "grid": g,
    "spawn_prev": [4, 12], "spawn_next": [26, 4],
    "intro": ["O ar está verde. O mapa inteiro está tomado por veneno!", "Só as zonas azuis brilhantes e as trilhas de rato são seguras."],
    "needs": [["filtro", "r4_gas"], ["chave_manut", "r4_rescue"]],
    "stages": [
        {"done": "item:filtro|flag:r4_gas", "text": "Siga os caminhos de rato e fabrique o Filtro experimental: 2 carbonos + 1 polímero",
         "hint": "As trilhas ciano ligam as zonas seguras. Armário do sul/esquerda: carbonos. Armário do sul/direita (NH3): polímero, oxigênio e gel."},
        {"done": "flag:r4_gas", "text": "Instale o filtro na válvula de ventilação (norte, direita)",
         "hint": "O gás se dissipa depois que o filtro é instalado."},
        {"done": "flag:r4_rescue", "text": "Com o gás dissipado, liberte o rato R-18 na gaiola do meio (Chave de manutenção)",
         "hint": "A gaiola do meio só abre depois que o veneno some."},
    ],
    "final": "O protocolo de contenção foi encerrado. Siga para a porta.",
    "objects": [
        prev_door(3, 4),
        exit_door(5, 26, "r4_rescue", "Protocolo de contenção ativo. Libere a gaiola do sujeito R-18 para destravar."),
        obstacle("r4_vent", "vent", 21, 2, 1, 1, "filtro", "r4_gas", True, False,
                 "Válvula de ventilação", "O filtro neutraliza o gás. O veneno se dissipa!",
                 "A válvula precisa de um Filtro experimental para neutralizar o gás."),
        {"type": "cage", "id": "r4_cage", "x": 14, "y": 7, "w": 2, "h": 2, "needs": "chave_manut", "flag": "r4_rescue",
         "requires": "flag:r4_gas", "req_msg": "O veneno ainda cobre a gaiola. Instale o filtro na válvula primeiro.",
         "label": "Gaiola do sujeito R-18", "ok_msg": "A trava cede. R-18 escapa pelas sombras. Obrigado!", "fail_msg": "A trava exige uma Chave de manutenção."},
        {"type": "hazard", "kind": "poison", "x": 1, "y": 2, "w": 28, "h": 12, "clear_flag": "r4_gas", "dmg": 1,
         "safe": [[1, 2, 8, 4], [9, 2, 5, 3], [19, 2, 5, 3], [24, 2, 5, 4], [2, 11, 6, 3], [8, 10, 6, 4], [18, 10, 6, 4]],
         "paths": [[5, 6, 1, 5], [14, 12, 4, 1], [14, 3, 5, 1], [24, 6, 1, 5], [12, 5, 1, 5]]},
        terminal("r4_t1", 11, 2, "TERMINAL // MUTAÇÃO", [
            "O veneno cobre o laboratório inteiro. Só as zonas seguras e as trilhas de rato estão protegidas.",
            "Filtro experimental = 2 Carbonos + 1 Polímero. Gel regenerativo = 1 Água (2 H + 1 O) + 1 Polímero.",
            "Depois do filtro na válvula, o gás se dissipa. Só então a gaiola do sujeito R-18 pode ser aberta.",
        ], ["filtro", "agua", "gel"]),
        bench(3, 2),
        locker("r4_l1", 11, 12, {"c": 2, "h": 2}),
        locker("r4_l2", 21, 12, {"polimero": 2, "o": 1, "gel": 1},
               puzzle("NH3", ["N", "H", "3"], ["C", "O", "2", "a", "l", "S"],
                      "Qual é a fórmula da AMÔNIA?",
                      "Gás de cheiro forte, usado em limpeza e fertilizantes. Elemento de número atômico 7 ligado a três átomos do mais leve de todos.")),
        decor("computer", 7, 2, 2, 1),
        decor("tank", 1, 7, 2, 3),
        decor("tank", 8, 7, 2, 3),
        decor("tank", 19, 6, 2, 3),
        decor("tank", 21, 6, 2, 3),
        decor("rack", 27, 7, 1, 2),
        decor("books", 27, 11, 2, 2),
        decor("potions", 16, 9, 3, 2),
        decor("desk", 26, 6, 3, 1),
        decor("pipe", 1, 1, 12, 1, False),
        decor("sign", 18, 1, 4, 1, False, text="MUTACAO 04"),
    ],
})

# ---------------------------------------------------------------- 5
g = blank()
wall(g, 13, 2, 1, 2); wall(g, 16, 2, 1, 2)
door_cells(g, 14, 0, 2, 2)
ROOMS.append({
    "id": 5, "name": "Complexo Químico", "theme": "yellow", "grid": g,
    "spawn_prev": [14, 12], "spawn_next": [14, 4],
    "intro": ["Tanques gigantes, vapor industrial e fogo na saída.", "Válvulas de vapor guardam os armários, a bancada e a porta. Uma barreira cristalizada selou o caminho."],
    "needs": [["solvente", "r5_open"]],
    "stages": [
        {"done": "item:agua|item:solvente|flag:r5_open", "text": "Pegue 2 H + 1 O no armário da direita (fórmula do metano) e fabrique Água",
         "hint": "O armário da direita (CH4) tem hidrogênios e oxigênio. Cuidado com as válvulas de vapor."},
        {"done": "item:solvente|flag:r5_open", "text": "Pegue Catalisador + Sódio no armário da esquerda e fabrique o Solvente: Água + Catalisador + Sódio",
         "hint": "O armário da esquerda está aberto. Misture na bancada (sem maçarico)."},
        {"done": "flag:r5_open", "text": "Dissolva a barreira cristalizada com o solvente",
         "hint": "Chegue perto do cristal e aperte E. Passe pela porta quando o vapor estiver parado."},
    ],
    "final": "A barreira se desfez. Siga para o Laboratório de Robótica.",
    "objects": [
        prev_door(4),
        exit_door(6, 14),
        obstacle("r5_crystal", "crystal", 14, 2, 2, 2, "solvente", "r5_open", True, True,
                 "Barreira cristalizada", "O cristal se dissolve em uma névoa brilhante.",
                 "O cristal é resistente demais. Um Solvente experimental pode dissolvê-lo."),
        terminal("r5_t1", 9, 6, "TERMINAL // QUÍMICA", [
            "Água = 2 Hidrogênios (H) + 1 Oxigênio (O). É a molécula H2O.",
            "Solvente experimental = 1 Água + 1 Catalisador fictício + 1 Sódio (Na). Fórmula inventada para a pesquisa.",
            "As válvulas de vapor protegem os armários, a bancada e a porta. O jato opera em ciclos: passe quando parar.",
            "Dica do armário da direita: o gás metano tem 1 carbono e 4 hidrogênios.",
        ], ["agua", "solvente"]),
        bench(24, 8),
        locker("r5_l1", 20, 2, {"h": 2, "o": 1},
               puzzle("CH4", ["C", "H", "4"], ["O", "N", "2", "3", "a", "l"],
                      "Qual é a fórmula do GÁS METANO?",
                      "É o principal componente do gás natural, o hidrocarboneto mais simples. Elemento de número atômico 6 com quatro átomos do mais leve.")),
        locker("r5_l2", 7, 2, {"catalisador": 1, "na": 1}),
        steam(19, 3, 3, 3, 1.5, 2.7, 0.0),
        steam(6, 3, 3, 3, 1.5, 2.7, 1.4),
        steam(23, 10, 5, 2, 1.5, 2.7, 2.2),
        steam(13, 4, 4, 2, 1.5, 3.0, 0.8),
        {"type": "hazard", "kind": "flame", "x": 12, "y": 3, "w": 1, "h": 1},
        {"type": "hazard", "kind": "flame", "x": 17, "y": 3, "w": 1, "h": 1},
        decor("tank", 2, 3, 3, 4),
        decor("tank", 25, 3, 3, 4),
        decor("tank", 13, 7, 4, 3),
        decor("computer", 10, 2, 2, 1),
        decor("computer", 23, 2, 2, 1),
        decor("potions", 9, 9, 3, 2),
        decor("desk", 19, 8, 3, 1),
        decor("computer", 20, 7, 2, 1),
        decor("books", 1, 8, 2, 2),
        decor("shelf", 1, 11, 3, 1),
        decor("rack", 28, 11, 1, 2),
        decor("tank", 5, 11, 2, 2),
        decor("potions", 20, 11, 3, 2),
        decor("pipe", 1, 1, 12, 1, False),
        decor("pipe", 17, 1, 12, 1, False),
        decor("sign", 8, 1, 4, 1, False, text="QUIMICA 05"),
    ],
})

# ---------------------------------------------------------------- 6
g = blank()
door_cells(g, 26, 0, 2, 2)
_o6 = [
    prev_door(5),
    exit_door(7, 26),
    obstacle("r6_laser_t", "lasercon", 17, 3, 1, 1, "modulo_contencao", "r6_laser", True, False,
             "Terminal do campo laser", "A malha de lasers se desliga com um zumbido.",
             "O terminal pede um Módulo de contenção."),
    # malha do campo laser (some quando o módulo é instalado)
    laser(20.3, 2, 0.4, 12, clear="r6_laser"),
    laser(22.3, 2, 0.4, 12, clear="r6_laser"),
    laser(24.3, 2, 0.4, 12, clear="r6_laser"),
    laser(20, 5.3, 9, 0.4, clear="r6_laser"),
    laser(20, 8.3, 9, 0.4, clear="r6_laser"),
    laser(20, 11.3, 9, 0.4, clear="r6_laser"),
    # lasers cronometrados na metade oeste
    laser(10, 8.3, 7, 0.4, on=1.6, off=2.2, phase=0.0),
    laser(11.3, 2, 0.4, 4, on=1.6, off=2.2, phase=1.9),
    laser(2, 8.3, 6, 0.4, on=1.6, off=2.2, phase=1.1),
    {"type": "drone", "x": 8, "y": 5, "chase": True, "bench_safe": True, "speed": 56, "range": 300},
    {"type": "drone", "x": 17, "y": 7, "chase": True, "bench_safe": True, "speed": 52, "range": 300},
    terminal("r6_t1", 12, 2, "TERMINAL // ROBÓTICA", [
        "O campo laser corta a sala. Para desligar: Módulo de contenção = 2 Placas de circuito + 1 Cristal.",
        "ATENÇÃO: os drones de patrulha perseguem qualquer intruso. A zona da bancada é protegida: eles recuam enquanto você a usa.",
        "Dica do armário trancado: o ácido do estômago é HCl.",
    ], ["modulo_contencao"]),
    bench(6, 2),
    locker("r6_l1", 13, 6, {"circuito": 2}),
    locker("r6_l2", 6, 10, {"cristal": 1},
           puzzle("HCl", ["H", "C", "l"], ["O", "N", "a", "2", "S", "K"],
                  "Qual é a fórmula do ÁCIDO CLORÍDRICO?",
                  "Está presente no suco gástrico do estômago. O elemento mais leve ligado ao halogênio de número atômico 17.")),
    decor("machine", 2, 2, 2, 2),
    decor("machine", 2, 5, 2, 2),
    decor("emitter", 20, 2),
    decor("emitter", 20, 13),
    decor("desk", 3, 9, 3, 1),
    decor("computer", 4, 8, 2, 1),
    decor("computer", 14, 2, 2, 1),
    decor("books", 9, 11, 2, 2),
    decor("potions", 15, 10, 3, 2),
    decor("shelf", 10, 4, 1, 3),
    decor("machine", 27, 6, 2, 2),
    decor("machine", 27, 9, 2, 2),
    decor("rack", 18, 10, 1, 3),
    decor("rack", 1, 10, 1, 3),
    decor("pipe", 1, 1, 12, 1, False),
    decor("sign", 14, 1, 4, 1, False, text="ROBOTICA 06"),
]
ROOMS.append({
    "id": 6, "name": "Laboratório de Robótica", "theme": "red", "grid": g,
    "spawn_prev": [14, 12], "spawn_next": [26, 4],
    "intro": ["Braços robóticos, drones que perseguem e uma malha de lasers.", "Preciso desativar o campo de contenção. Perto da bancada os drones não me alcançam."],
    "needs": [["modulo_contencao", "r6_laser"]],
    "stages": [
        {"done": "item:modulo_contencao|flag:r6_laser", "text": "Pegue 2 placas de circuito e 1 cristal nos armários (o de baixo pede HCl) e fabrique o Módulo de contenção",
         "hint": "Os drones perseguem. Use a zona da bancada para fabricar em paz."},
        {"done": "flag:r6_laser", "text": "Instale o módulo no terminal do campo laser",
         "hint": "O terminal do campo fica ao lado das hastes do laser."},
    ],
    "final": "O campo laser caiu. Siga para o Armazém Geral.",
    "objects": _o6,
})

# ---------------------------------------------------------------- 7
g = blank()
door_cells(g, 14, 0, 2, 2)
ROOMS.append({
    "id": 7, "name": "Armazém Geral", "theme": "orange", "grid": g,
    "spawn_prev": [14, 12], "spawn_next": [14, 3],
    "intro": ["Pilhas de caixas e uma empilhadeira parada.", "O portão de carga só abre com as cinco placas de pressão ativas."],
    "needs": [["disp_resgate", "r7_done"]],
    "stages": [
        {"done": "flag:r7_shutter", "text": "Empurre as 5 caixas até as 5 placas de pressão (R reinicia as caixas)",
         "hint": "Fique abaixo de cada caixa e empurre para cima até a placa."},
        {"done": "item:disp_resgate|flag:r7_done", "text": "Abra os 2 armários e fabrique o Dispositivo de resgate: circuito + engrenagem + célula",
         "hint": "Esquerda: soda cáustica (NaOH). Direita: cal virgem (CaO)."},
    ],
    "final": "Com o portão aberto e o dispositivo pronto, siga para a Área de Experimentos.",
    "objects": [
        prev_door(6),
        exit_door(8, 14, "r7_shutter", "O portão de carga está travado. Ative as cinco placas de pressão.", "shutter"),
        {"type": "crate", "id": "r7_c1", "x": 6, "y": 8},
        {"type": "crate", "id": "r7_c2", "x": 10, "y": 8},
        {"type": "crate", "id": "r7_c3", "x": 14, "y": 8},
        {"type": "crate", "id": "r7_c4", "x": 18, "y": 8},
        {"type": "crate", "id": "r7_c5", "x": 22, "y": 8},
        {"type": "plate", "id": "r7_pl1", "x": 6, "y": 4, "group": "r7_shutter"},
        {"type": "plate", "id": "r7_pl2", "x": 10, "y": 4, "group": "r7_shutter"},
        {"type": "plate", "id": "r7_pl3", "x": 14, "y": 4, "group": "r7_shutter"},
        {"type": "plate", "id": "r7_pl4", "x": 18, "y": 4, "group": "r7_shutter"},
        {"type": "plate", "id": "r7_pl5", "x": 22, "y": 4, "group": "r7_shutter"},
        {"type": "npc", "id": "r7_npc", "kind": "researcher", "x": 4, "y": 12, "name": "Dra. Okoye",
         "lines": ["Psiu... você é o rato modificado? Eu não aprovo o que fazem aqui.",
                   "Os outros ratos estão na Área de Experimentos, logo depois deste portão.",
                   "Um Dispositivo de resgate abre as gaiolas deles: 1 placa de circuito, 1 engrenagem e 1 célula de energia.",
                   "Empurre as caixas até as placas. Se travar uma caixa, aperte R para reiniciá-las.",
                   "Cuidado: são cinco caixas e cinco placas de pressão. O portão só abre quando todas estiverem ativas.",
                   "As peças do dispositivo estão nos dois armários desta sala, mas os dois têm código de acesso.",
                   "O armário da esquerda abre com a fórmula da soda cáustica, o hidróxido de sódio: sódio, oxigênio e hidrogênio.",
                   "O da direita usa a cal virgem, o óxido de cálcio: cálcio e oxigênio. Lembre das maiúsculas e minúsculas!",
                   "Eu trabalhei seis anos para o Dr. Voss e me calei. Não vou me calar mais. Boa sorte, pequeno."],
         "learn": ["disp_resgate"]},
        terminal("r7_t1", 12, 2, "TERMINAL // ARMAZÉM", [
            "INVENTÁRIO: circuitos, engrenagens e células de reserva trancados nos armários norte.",
            "O portão de carga usa cinco placas de pressão. Caixas sobre as placas liberam o trilho.",
        ], []),
        bench(24, 10),
        locker("r7_l1", 3, 2, {"circuito": 1, "engrenagem": 1},
               puzzle("NaOH", ["N", "a", "O", "H"], ["C", "l", "K", "2", "S", "e"],
                      "Qual é a fórmula da SODA CÁUSTICA (hidróxido de sódio)?",
                      "Base forte usada para fazer sabão: um metal alcalino de número atômico 11 seguido do grupo hidroxila. A Dra. Okoye sabe mais.")),
        locker("r7_l2", 26, 2, {"celula": 1},
               puzzle("CaO", ["C", "a", "O"], ["H", "N", "l", "2", "S", "K"],
                      "Qual é a fórmula da CAL VIRGEM (óxido de cálcio)?",
                      "Obtida ao queimar calcário e usada na construção. Metal alcalino-terroso de número atômico 20 mais o elemento da respiração, 1 para 1. A Dra. Okoye sabe mais.")),
        decor("boxes", 1, 5, 3, 3),
        decor("boxes", 26, 5, 3, 3),
        decor("shelf", 8, 6, 1, 3),
        decor("shelf", 12, 6, 1, 3),
        decor("shelf", 16, 6, 1, 3),
        decor("shelf", 20, 6, 1, 3),
        decor("forklift", 20, 11, 2, 2),
        decor("boxes", 1, 10, 2, 2),
        decor("computer", 7, 12, 2, 1),
        decor("potions", 9, 11, 3, 2),
        decor("books", 27, 10, 2, 2),
        decor("computer", 16, 2, 2, 1),
        decor("pipe", 1, 1, 12, 1, False),
        decor("sign", 18, 1, 4, 1, False, text="ARMAZEM 07"),
    ],
})

# ---------------------------------------------------------------- 8
g = blank()
door_cells(g, 14, 0, 2, 2)
ROOMS.append({
    "id": 8, "name": "Área de Experimentos", "theme": "teal", "grid": g,
    "spawn_prev": [14, 12], "spawn_next": [14, 3],
    "intro": ["Aquários, criaturas e duas gaiolas de ratos.", "Duas criaturas vigiam as gaiolas... e já me viram!"],
    "needs": [["disp_resgate", "r8_free"]],
    "stages": [
        {"done": "flag:r8_free", "text": "Liberte os 2 ratos nas gaiolas com o Dispositivo de resgate (cada gaiola tem um mutante por perto)",
         "hint": "Os mutantes perseguem, mas são lentos. Dê a volta pelos tanques. Gel regenerativo cura (F)."},
    ],
    "final": "Os ratos estão livres. Siga para a Segurança Máxima.",
    "objects": [
        prev_door(7),
        exit_door(9, 14, "r8_rat1&r8_rat2", "A porta de contenção só abre quando os dois ratos forem libertados."),
        {"type": "cage", "id": "r8_c1", "x": 3, "y": 5, "w": 2, "h": 2, "needs": "disp_resgate", "flag": "r8_rat1",
         "label": "Gaiola 08-A", "ok_msg": "A gaiola abre. O rato foge, livre!", "fail_msg": "A trava eletrônica exige um Dispositivo de resgate."},
        {"type": "cage", "id": "r8_c2", "x": 25, "y": 5, "w": 2, "h": 2, "needs": "disp_resgate", "flag": "r8_rat2",
         "label": "Gaiola 08-B", "ok_msg": "A gaiola abre. O rato agradece com um guincho!", "fail_msg": "A trava eletrônica exige um Dispositivo de resgate."},
        {"type": "mutant", "id": "r8_m1", "x": 7, "y": 6, "speed": 44, "range": 300},
        {"type": "mutant", "id": "r8_m2", "x": 22, "y": 6, "speed": 44, "range": 300},
        terminal("r8_t1", 10, 2, "TERMINAL // EXPERIMENTOS", [
            "REGISTRO: sujeitos R-31 e R-22 aguardam o procedimento de mutação final.",
            "As duas criaturas escaparam dos tanques e vigiam as gaiolas. Não respondem a comandos.",
            "O Dr. Voss pretende estender o programa a todo o complexo.",
        ], []),
        bench(18, 2),
        pickup("r8_p1", 8, 12, "gel"),
        pickup("r8_p2", 21, 12, "gel"),
        decor("aquarium", 2, 2, 6, 2),
        decor("aquarium", 22, 2, 6, 2),
        decor("tank", 11, 9, 2, 3),
        decor("tank", 17, 9, 2, 3),
        decor("rack", 1, 9, 1, 2),
        decor("rack", 28, 9, 1, 2),
        decor("computer", 12, 2, 2, 1),
        decor("desk", 10, 6, 3, 1),
        decor("potions", 19, 6, 3, 2),
        decor("books", 6, 10, 2, 2),
        decor("books", 22, 10, 2, 2),
        decor("shelf", 1, 12, 3, 1),
        decor("shelf", 26, 12, 3, 1),
        decor("tank", 14, 6, 2, 2),
        decor("pipe", 1, 1, 8, 1, False),
        decor("sign", 18, 1, 4, 1, False, text="EXPERIMENTOS"),
    ],
})

# ---------------------------------------------------------------- 9
g = blank()
wall(g, 9, 2, 1, 6); wall(g, 9, 10, 1, 4)
wall(g, 20, 2, 1, 6); wall(g, 20, 10, 1, 4)
door_cells(g, 14, 0, 2, 2)
ROOMS.append({
    "id": 9, "name": "Segurança Máxima", "theme": "red", "grid": g,
    "spawn_prev": [14, 12], "spawn_next": [14, 3],
    "intro": ["Alarmes, lasers que surgem e somem, e três robôs de segurança no meu rastro.", "A porta mestra está trancada. Preciso reunir três componentes das câmaras laterais."],
    "needs": [["chave_mestra", "r9_open"]],
    "stages": [
        {"done": "item:chave_mestra|flag:r9_open", "text": "Reúna circuito + cristal (câmara oeste) e módulo genético (câmara leste) e fabrique a Chave mestra",
         "hint": "Os lasers perto dos armários ligam e desligam. Os 3 robôs perseguem você: não pare!"},
        {"done": "flag:r9_open", "text": "Use a Chave mestra no painel de segurança ao lado da porta",
         "hint": "O painel fica no alto, à direita da porta."},
    ],
    "final": "A porta mestra se abriu. O laboratório do cientista está à frente.",
    "objects": [
        prev_door(8),
        exit_door(10, 14, "r9_open", "A porta mestra exige a Chave mestra do painel de segurança."),
        obstacle("r9_panel", "panel", 17, 2, 1, 1, "chave_mestra", "r9_open", True, False,
                 "Painel de segurança", "A Chave mestra é aceita. A porta se destranca!",
                 "O painel exige uma Chave mestra."),
        laser(9.3, 8, 0.4, 2, on=1.5, off=2.0, phase=0.0, knock=56),
        laser(20.3, 8, 0.4, 2, on=1.5, off=2.0, phase=1.8, knock=56),
        # lasers que aparecem e somem perto dos armários
        laser(1, 6.3, 8, 0.4, on=1.4, off=2.2, phase=0.0, knock=56),
        laser(5.3, 3, 0.4, 3, on=1.4, off=2.2, phase=1.9, knock=56),
        laser(21, 6.3, 8, 0.4, on=1.4, off=2.2, phase=1.1, knock=56),
        laser(24.3, 3, 0.4, 3, on=1.4, off=2.2, phase=3.0, knock=56),
        {"type": "drone", "x": 11, "y": 4, "chase": True, "speed": 40, "tint": "#ff7070"},
        {"type": "drone", "x": 18, "y": 4, "chase": True, "speed": 40, "tint": "#ff7070"},
        {"type": "drone", "x": 14, "y": 7, "chase": True, "speed": 38, "tint": "#ff7070"},
        terminal("r9_t1", 19, 2, "TERMINAL // SEGURANÇA", [
            "Chave mestra = 1 Placa de circuito + 1 Cristal de contenção + 1 Módulo genético.",
            "Os 3 robôs de segurança seguem o intruso. Os lasers das câmaras pulsam em ciclos de alguns segundos.",
        ], ["chave_mestra"]),
        bench(10, 2),
        locker("r9_l1", 3, 3, {"circuito": 1, "cristal": 1}),
        locker("r9_l2", 26, 3, {"modulo_gen": 1}),
        pickup("r9_p1", 5, 10, "gel"),
        decor("rack", 1, 11, 1, 2),
        decor("rack", 28, 11, 1, 2),
        decor("machine", 3, 11, 2, 2),
        decor("machine", 25, 11, 2, 2),
        decor("computer", 12, 2, 2, 1),
        decor("shelf", 12, 9, 2, 1),
        decor("potions", 16, 10, 3, 2),
        decor("pipe", 1, 1, 8, 1, False),
        decor("sign", 22, 1, 5, 1, False, text="SEGURANCA MAX"),
    ],
})

# ---------------------------------------------------------------- 10
g = blank()
ROOMS.append({
    "id": 10, "name": "Sala do Cientista", "theme": "blue", "grid": g,
    "spawn_prev": [14, 12], "spawn_next": [14, 12],
    "intro": ["O laboratório do Dr. Voss. Cápsulas com ratos aprisionados cercam a sala.", "No centro, o núcleo que mantém tudo funcionando. Se ele explodir, o complexo vai junto."],
    "needs": [["modulo_contencao", "r10_def"], ["modulo_eletrico", "r10_evac"], ["disp_resgate", "r10_free"], ["bomba", "r10_bomb"]],
    "stages": [
        {"done": "flag:r10_def&flag:r10_evac&flag:r10_free", "text": "Ative os 3 consoles: defesas (módulo de contenção), evacuação (módulo elétrico) e cápsulas (disp. de resgate)",
         "hint": "5 armários guardam as peças (o do alto pede H2O2). Os módulos usam receitas que você já conhece. Desvie das bolas de laser do Voss!"},
        {"done": "item:bomba|flag:r10_bomb", "text": "Pegue a receita no armário e fabrique a Bomba experimental (módulo genético + célula + cristal)",
         "hint": "Na bancada, com o maçarico aceso. Enquanto você fabrica, nada te atinge."},
        {"done": "flag:r10_bomb", "text": "Coloque a bomba no núcleo central e fuja!",
         "hint": "O núcleo fica no meio da sala."},
    ],
    "final": "Corra!",
    "objects": [
        prev_door(9),
        obstacle("r10_ca", "lasercon", 6, 2, 1, 1, "modulo_contencao", "r10_def", True, False,
                 "Console de defesas", "As defesas do complexo são desativadas.",
                 "Este console precisa de um Módulo de contenção."),
        obstacle("r10_cb", "panel", 22, 2, 1, 1, "modulo_eletrico", "r10_evac", True, False,
                 "Console de evacuação", "As rotas de evacuação se acendem em ciano.",
                 "Este console precisa de um Módulo elétrico."),
        obstacle("r10_cc", "console", 14, 2, 1, 1, "disp_resgate", "r10_free", False, False,
                 "Console de contenção", "As cápsulas se abrem! Os ratos estão livres!",
                 "Este console precisa de um Dispositivo de resgate."),
        {"type": "obstacle", "id": "r10_core", "kind": "core", "x": 14, "y": 8, "w": 2, "h": 2, "needs": "bomba", "flag": "r10_bomb",
         "consume": True, "blocks": True, "label": "Núcleo central", "ok_msg": "A bomba está armada! Sobrecarga em 5 segundos... CORRA!",
         "fail_msg": "O núcleo central precisa de uma Bomba experimental.",
         "requires": "flag:r10_def&flag:r10_evac&flag:r10_free", "req_msg": "O núcleo está protegido. Ative os três consoles primeiro."},
        {"type": "npc", "id": "r10_boss", "kind": "scientist", "x": 14, "y": 5, "name": "Dr. Voss",
         "lines": ["Então foi você, R-31. O único que saiu da gaiola... Devia sentir raiva. Sinto, na verdade, um certo orgulho.",
                   "Passei vinte anos nesta sala. Perdi minha família, meus amigos, o sono. Tudo pela ciência. Você acha que foi fácil?",
                   "Cada rato aqui é uma resposta que ainda não encontrei. Eu não sou um monstro, pequeno. Sou um homem com pressa.",
                   "Mas não posso deixar você destruir tudo o que eu construí. Sinto muito."],
         "choices": ["Libertar os ratos e encerrar o projeto.", "Você chama isso de ciência?"]},
        {"type": "boss", "x": 14, "y": 5, "interval": 2.0},
        terminal("r10_t1", 10, 2, "TERMINAL // DR. VOSS", [
            "PROJETO CYBERLAB: fase final. Todos os sujeitos serão submetidos ao protocolo.",
            "Console de defesas: Módulo de contenção. Evacuação: Módulo elétrico. Cápsulas: Dispositivo de resgate.",
            "NOTA PRIVADA: se o núcleo central sofrer sobrecarga, o complexo inteiro vai pelos ares. Jamais deixe alguém chegar perto dele.",
        ], []),
        bench(3, 9),
        locker("r10_l1", 2, 12, {"circuito": 2}),
        locker("r10_l2", 27, 12, {"cristal": 1, "celula": 1}),
        locker("r10_l3", 18, 2, {"cu": 2, "engrenagem": 1, "cristal": 1},
               puzzle("H2O2", ["H", "2", "O", "2"], ["N", "a", "C", "l", "3", "S"],
                      "Qual é a fórmula da ÁGUA OXIGENADA (peróxido de hidrogênio)?",
                      "Desinfeta feridas e clareia cabelos. Parente da água, mas com um átomo de oxigênio a mais; confira os dois índices.")),
        locker("r10_l4", 8, 12, {"circuito": 1, "celula": 1, "modulo_gen": 1}),
        locker("r10_l5", 21, 12, {"celula": 1, "gel": 1}, learn=["bomba"]),
        decor("pod", 2, 4, 2, 3, True, rats=2),
        decor("pod", 26, 4, 2, 3, True, rats=2),
        decor("pod", 8, 9, 1, 2, True, rats=1),
        decor("pod", 21, 9, 1, 2, True, rats=1),
        decor("platform", 11, 5, 8, 5, False),
        decor("computer", 24, 2, 2, 1),
        decor("books", 6, 4, 2, 2),
        decor("potions", 23, 7, 3, 2),
        decor("shelf", 5, 12, 2, 1),
        decor("sign", 12, 1, 6, 1, False, text="DR VOSS // CYBERLAB"),
        decor("pipe", 1, 1, 4, 1, False),
        decor("pipe", 25, 1, 4, 1, False),
    ],
})

THEMES = {
    "cyan":   {"accent": "#19e6ff", "floor": "#171f33", "floor2": "#1b2540", "wall": "#26334f"},
    "purple": {"accent": "#c05cff", "floor": "#1c1a33", "floor2": "#211e3d", "wall": "#33294f"},
    "blue":   {"accent": "#3d8bff", "floor": "#151c33", "floor2": "#19223d", "wall": "#243357"},
    "green":  {"accent": "#3dff8a", "floor": "#14231f", "floor2": "#182b25", "wall": "#233f38"},
    "yellow": {"accent": "#ffd23a", "floor": "#1e1f2a", "floor2": "#232432", "wall": "#363846"},
    "red":    {"accent": "#ff3a55", "floor": "#241823", "floor2": "#2a1b2a", "wall": "#40253a"},
    "orange": {"accent": "#ff9a2a", "floor": "#221d1e", "floor2": "#282223", "wall": "#40342f"},
    "teal":   {"accent": "#2af0c8", "floor": "#122429", "floor2": "#162c32", "wall": "#1f4147"},
}

def export(path):
    rooms = []
    for r in ROOMS:
        rr = dict(r)
        rr["grid"] = ["".join(row) for row in r["grid"]]
        rr["accent"] = THEMES[r["theme"]]["accent"]
        rooms.append(rr)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"rooms": rooms}, f, ensure_ascii=False, indent=1)
    gd = os.path.join(os.path.dirname(path), "rooms_data.gd")
    with open(gd, "w", encoding="utf-8") as f:
        f.write("extends RefCounted\n# Gerado por tools/rooms_def.py - nao editar a mao\nconst DATA = ")
        f.write(json.dumps({"rooms": rooms}, ensure_ascii=False))
        f.write("\n")

if __name__ == "__main__":
    export(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "rooms.json"))
    print("rooms.json ok:", len(ROOMS), "salas")
