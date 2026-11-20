extends Node
## Autoload "Game": estado global, itens, receitas, flags, inventário e save.

signal inventory_changed
signal flags_changed
signal hp_changed
signal recipes_changed
signal toast_requested(text: String, color: Color)

const TILE := 32
const MAX_HP := 3
const SAVE_PATH := "user://rato_cyberlab_save.json"
const ROOMS_DATA := preload("res://data/rooms_data.gd")

const COL_CYAN := Color("#19e6ff")
const COL_GREEN := Color("#50ff82")
const COL_RED := Color("#ff3a55")
const COL_YELLOW := Color("#ffd23a")
const COL_BG := Color("#080b14")

# kind: elem = elemento químico real | fict = componente fictício | prod = item fabricado
const ITEMS := {
	"h": {"name": "Hidrogênio", "sym": "H", "kind": "elem", "col": "#7fd6ff", "desc": "Elemento químico real (H). Leve e reativo. Dois de H mais um de O formam água."},
	"o": {"name": "Oxigênio", "sym": "O", "kind": "elem", "col": "#ff7f8f", "desc": "Elemento químico real (O). Combina com o hidrogênio para formar água."},
	"c": {"name": "Carbono", "sym": "C", "kind": "elem", "col": "#9aa4b8", "desc": "Elemento químico real (C). Base de materiais filtrantes."},
	"fe": {"name": "Ferro", "sym": "Fe", "kind": "elem", "col": "#c8905a", "desc": "Elemento químico real (Fe). Metal resistente usado em ferramentas."},
	"cu": {"name": "Cobre", "sym": "Cu", "kind": "elem", "col": "#ff9a50", "desc": "Elemento químico real (Cu). Ótimo condutor elétrico."},
	"na": {"name": "Sódio", "sym": "Na", "kind": "elem", "col": "#ffe25a", "desc": "Elemento químico real (Na). Metal muito reativo."},
	"so": {"name": "Monóxido de enxofre", "sym": "SO", "kind": "elem", "col": "#e6e86a", "desc": "Molécula real (SO). Com hidrogênio e oxigênio forma o ácido sulfúrico."},
	"engrenagem": {"name": "Engrenagem", "sym": "EN", "kind": "fict", "col": "#9fb0d0", "desc": "Peça mecânica de máquinas do laboratório.", "icon": "res://assets/icons/it_engrenagem.png"},
	"nucleo": {"name": "Núcleo térmico", "sym": "NT", "kind": "fict", "col": "#ff7a3a", "desc": "Componente experimental inventado. Gera calor intenso.", "icon": "res://assets/icons/it_nucleo_%d.png", "frames": 4},
	"celula": {"name": "Célula de energia", "sym": "CE", "kind": "fict", "col": "#4dd2ff", "desc": "Componente experimental inventado. Armazena energia.", "icon": "res://assets/icons/it_celula_%d.png", "frames": 4},
	"polimero": {"name": "Polímero experimental", "sym": "PO", "kind": "fict", "col": "#c05cff", "desc": "Material experimental inventado. Flexível e filtrante.", "icon": "res://assets/icons/it_polimero.png"},
	"catalisador": {"name": "Catalisador", "sym": "CA", "kind": "fict", "col": "#ffd23a", "desc": "Reagente experimental inventado que acelera reações.", "icon": "res://assets/icons/it_catalisador.png"},
	"circuito": {"name": "Placa de circuito", "sym": "PC", "kind": "fict", "col": "#4dff9a", "desc": "Material eletrônico para módulos e dispositivos.", "icon": "res://assets/icons/it_circuito.png"},
	"cristal": {"name": "Cristal de contenção", "sym": "CC", "kind": "fict", "col": "#9a8cff", "desc": "Componente raro inventado. Estabiliza campos de energia.", "icon": "res://assets/icons/it_cristal.png"},
	"modulo_gen": {"name": "Módulo genético", "sym": "MG", "kind": "fict", "col": "#ff5cd6", "desc": "Componente raro inventado. Reconhece o material genético do protagonista.", "icon": "res://assets/icons/it_modulo_gen_%d.png", "frames": 4},
	"chave_manut": {"name": "Chave de manutenção", "sym": "CM", "kind": "prod", "col": "#8fd0ff", "desc": "Abre painéis de manutenção e travas simples.", "icon": "res://assets/icons/it_chave_manut_%d.png", "frames": 4},
	"termico": {"name": "Dispositivo térmico", "sym": "DT", "kind": "prod", "col": "#ff7a3a", "desc": "Derrete barreiras de gelo.", "icon": "res://assets/icons/it_termico_%d.png", "frames": 4},
	"modulo_eletrico": {"name": "Módulo elétrico", "sym": "ME", "kind": "prod", "col": "#4dd2ff", "desc": "Restaura energia de painéis e consoles.", "icon": "res://assets/icons/it_modulo_eletrico.png"},
	"filtro": {"name": "Filtro experimental", "sym": "FE", "kind": "prod", "col": "#50ff82", "desc": "Neutraliza gás em válvulas de ventilação.", "icon": "res://assets/icons/it_filtro.png"},
	"agua": {"name": "Água (H2O)", "sym": "H2O", "kind": "prod", "col": "#6ab8ff", "desc": "Molécula real: 2 hidrogênios e 1 oxigênio.", "icon": "res://assets/icons/ico_frasco.png"},
	"solvente": {"name": "Solvente experimental", "sym": "SE", "kind": "prod", "col": "#c05cff", "desc": "Dissolve barreiras cristalizadas.", "icon": "res://assets/icons/it_solvente.png"},
	"gel": {"name": "Gel regenerativo", "sym": "GR", "kind": "prod", "col": "#50ff82", "desc": "Recupera vida. Tecla F para usar.", "icon": "res://assets/icons/ico_cura.png"},
	"modulo_contencao": {"name": "Módulo de contenção", "sym": "MC", "kind": "prod", "col": "#ff3a55", "desc": "Desativa campos laser e sistemas de defesa.", "icon": "res://assets/icons/it_modulo_contencao.png"},
	"disp_resgate": {"name": "Dispositivo de resgate", "sym": "DR", "kind": "prod", "col": "#50ff82", "desc": "Abre gaiolas e cápsulas de contenção.", "icon": "res://assets/icons/it_disp_resgate.png"},
	"acido": {"name": "Ácido sulfúrico (H2SO4)", "sym": "AS", "kind": "prod", "col": "#e6e86a", "desc": "Molécula real: 2 hidrogênios, enxofre e 4 oxigênios. Corrói metal e grades.", "icon": "res://assets/icons/it_acido.png"},
	"bomba": {"name": "Bomba experimental", "sym": "BX", "kind": "prod", "col": "#ff3a55", "desc": "Dispositivo fictício de sobrecarga. Cuidado com o núcleo.", "icon": "res://assets/icons/it_bomba_%d.png", "frames": 4},
	"chave_mestra": {"name": "Chave mestra", "sym": "KM", "kind": "prod", "col": "#ffd23a", "desc": "Acesso total a painéis de segurança máxima.", "icon": "res://assets/icons/it_chave_mestra_%d.png", "frames": 4},
}

# fire = precisa do maçarico aceso. Cada recipiente guarda UM tipo de item (até 5).
const RECIPES := {
	"chave_manut": {"req": {"fe": 1, "engrenagem": 2}, "fire": true},
	"termico": {"req": {"nucleo": 1, "fe": 1, "cu": 1}, "fire": true},
	"modulo_eletrico": {"req": {"celula": 1, "cu": 2}, "fire": true},
	"filtro": {"req": {"c": 2, "polimero": 1}, "fire": true},
	"agua": {"req": {"h": 2, "o": 1}, "fire": false},
	"solvente": {"req": {"agua": 1, "catalisador": 1, "na": 1}, "fire": false},
	"gel": {"req": {"agua": 1, "polimero": 1}, "fire": false},
	"modulo_contencao": {"req": {"circuito": 2, "cristal": 1}, "fire": true},
	"disp_resgate": {"req": {"circuito": 1, "engrenagem": 1, "celula": 1}, "fire": true},
	"chave_mestra": {"req": {"circuito": 1, "cristal": 1, "modulo_gen": 1}, "fire": true},
	"acido": {"req": {"h": 2, "so": 1, "o": 3}, "fire": true},
	"bomba": {"req": {"modulo_gen": 1, "celula": 1, "cristal": 1}, "fire": true},
}

const ITEM_ORDER := ["h", "o", "c", "fe", "cu", "na", "so", "engrenagem", "nucleo", "celula", "polimero", "catalisador", "circuito", "cristal", "modulo_gen",
	"agua", "chave_manut", "termico", "modulo_eletrico", "filtro", "solvente", "gel", "modulo_contencao", "disp_resgate", "chave_mestra", "acido", "bomba"]

var rooms: Array = []
var inv: Dictionary = {}
var flags: Dictionary = {}
var learned: Array = []
var taken: Dictionary = {}
var hp: int = MAX_HP
var cur_room: int = 1
var input_lock: int = 0
var tex_cache: Dictionary = {}


func _ready() -> void:
	rooms = ROOMS_DATA.DATA["rooms"]
	_setup_input()
	RenderingServer.set_default_clear_color(COL_BG)
	_fit_window()


# ------------------------------------------------------------------ janela
func _fit_window() -> void:
	## Ajusta a janela ao monitor (16:9), para nenhum controle ficar fora da tela.
	if DisplayServer.get_name() == "headless":
		return
	var usable: Rect2i = DisplayServer.screen_get_usable_rect()
	var max_w: int = int(usable.size.x * 0.92)
	var max_h: int = int(usable.size.y * 0.88)
	var w: int = mini(1280, max_w)
	var h: int = int(w * 9.0 / 16.0)
	if h > max_h:
		h = max_h
		w = int(h * 16.0 / 9.0)
	w = maxi(w, 640)
	h = maxi(h, 360)
	DisplayServer.window_set_size(Vector2i(w, h))
	DisplayServer.window_set_position(usable.position + (usable.size - Vector2i(w, h)) / 2)


# ------------------------------------------------------------------ input
func _add_key(action: String, keys: Array) -> void:
	if not InputMap.has_action(action):
		InputMap.add_action(action)
	for k in keys:
		var ev := InputEventKey.new()
		ev.physical_keycode = k
		InputMap.action_add_event(action, ev)


func _setup_input() -> void:
	_add_key("move_up", [KEY_W, KEY_UP])
	_add_key("move_down", [KEY_S, KEY_DOWN])
	_add_key("move_left", [KEY_A, KEY_LEFT])
	_add_key("move_right", [KEY_D, KEY_RIGHT])
	_add_key("run", [KEY_SHIFT])
	_add_key("interact", [KEY_E, KEY_SPACE])
	_add_key("craft", [KEY_C])
	_add_key("inventory", [KEY_I])
	_add_key("heal", [KEY_F])
	_add_key("hint", [KEY_H])
	_add_key("reset_crates", [KEY_R])
	_add_key("pause", [KEY_ESCAPE])


func lock_input(sec: float = 0.2) -> void:
	input_lock = Time.get_ticks_msec() + int(sec * 1000.0)


func input_locked() -> bool:
	return Time.get_ticks_msec() < input_lock


# ------------------------------------------------------------------ recursos
func tex(path: String) -> Texture2D:
	if tex_cache.has(path):
		return tex_cache[path]
	var t: Texture2D = null
	if ResourceLoader.exists(path):
		t = load(path)
	else:
		var img := Image.load_from_file(ProjectSettings.globalize_path(path))
		if img != null and not img.is_empty():
			t = ImageTexture.create_from_image(img)
	tex_cache[path] = t
	return t


func toast(text: String, color: Color = COL_CYAN) -> void:
	toast_requested.emit(text, color)


func panel_style(border: Color = COL_CYAN, fill: Color = Color(0.03, 0.05, 0.1, 0.94), width: int = 2) -> StyleBoxFlat:
	var sb := StyleBoxFlat.new()
	sb.bg_color = fill
	sb.border_color = border
	sb.set_border_width_all(width)
	sb.set_corner_radius_all(3)
	sb.content_margin_left = 10
	sb.content_margin_right = 10
	sb.content_margin_top = 8
	sb.content_margin_bottom = 8
	return sb


func style_button(b: Button) -> void:
	b.add_theme_stylebox_override("normal", panel_style(COL_CYAN.darkened(0.2), Color(0.04, 0.1, 0.18, 0.95), 1))
	b.add_theme_stylebox_override("hover", panel_style(COL_YELLOW, Color(0.08, 0.17, 0.27, 1.0), 2))
	b.add_theme_stylebox_override("pressed", panel_style(COL_GREEN, Color(0.04, 0.22, 0.17, 1.0), 2))
	b.add_theme_stylebox_override("disabled", panel_style(Color(0.2, 0.26, 0.36), Color(0.04, 0.06, 0.1, 0.9), 1))
	b.add_theme_color_override("font_color", Color(0.9, 0.97, 1.0))
	b.add_theme_color_override("font_hover_color", COL_YELLOW)
	b.add_theme_color_override("font_disabled_color", Color(0.38, 0.45, 0.56))


# ------------------------------------------------------------------ inventário
func count(id: String) -> int:
	return int(inv.get(id, 0))


func has(id: String) -> bool:
	return count(id) > 0


func add_item(id: String, n: int = 1) -> void:
	inv[id] = count(id) + n
	inventory_changed.emit()


func remove_item(id: String, n: int = 1) -> bool:
	if count(id) < n:
		return false
	inv[id] = count(id) - n
	if inv[id] <= 0:
		inv.erase(id)
	inventory_changed.emit()
	return true


func item_name(id: String) -> String:
	return str(ITEMS[id]["name"]) if ITEMS.has(id) else id


func item_color(id: String) -> Color:
	return Color(ITEMS[id]["col"]) if ITEMS.has(id) else Color.WHITE


# ------------------------------------------------------------------ flags
func flag(name: String) -> bool:
	return flags.has(name)


func set_flag(name: String) -> void:
	if flags.has(name):
		return
	flags[name] = true
	flags_changed.emit()


func _token_ok(tok: String) -> bool:
	tok = tok.strip_edges()
	if tok.begins_with("item:"):
		return has(tok.substr(5))
	if tok.begins_with("flag:"):
		return flag(tok.substr(5))
	return flag(tok)


## expressão: grupos separados por "|" (OU); dentro de cada grupo, "&" (E).
func expr_ok(expr: String) -> bool:
	if expr == "":
		return true
	for group in expr.split("|"):
		var all_ok := true
		for tok in group.split("&"):
			if not _token_ok(tok):
				all_ok = false
				break
		if all_ok:
			return true
	return false


# ------------------------------------------------------------------ receitas
func recipe_text(rid: String) -> String:
	var parts: Array = []
	var req: Dictionary = RECIPES[rid]["req"]
	for k in req:
		parts.append("%d %s" % [req[k], item_name(k)])
	var t: String = " + ".join(parts)
	if bool(RECIPES[rid].get("fire", false)):
		t += "  [maçarico aceso]"
	return t


func match_recipe(slots: Array, fire: bool = false) -> String:
	var cnt: Dictionary = {}
	for s in slots:
		if str(s) != "":
			cnt[s] = int(cnt.get(s, 0)) + 1
	if cnt.is_empty():
		return ""
	for rid in RECIPES:
		var req: Dictionary = RECIPES[rid]["req"]
		if bool(RECIPES[rid].get("fire", false)) != fire:
			continue
		if req.size() != cnt.size():
			continue
		var ok := true
		for k in req:
			if int(cnt.get(k, 0)) != int(req[k]):
				ok = false
				break
		if ok:
			return rid
	return ""


func learn(rid: String) -> bool:
	if RECIPES.has(rid) and not learned.has(rid):
		learned.append(rid)
		recipes_changed.emit()
		return true
	return false


## consome os componentes dos slots e entrega o item. Retorna o id fabricado ou "".
func craft(slots: Array, fire: bool = false) -> String:
	var rid := match_recipe(slots, fire)
	if rid == "":
		return ""
	var req: Dictionary = RECIPES[rid]["req"]
	for k in req:
		if count(k) < int(req[k]):
			return ""
	for k in req:
		remove_item(k, int(req[k]))
	add_item(rid, 1)
	learn(rid)
	return rid


## desmonta um item fabricado de volta nos componentes (proteção contra soft-lock).
func recycle(rid: String) -> bool:
	if not RECIPES.has(rid) or not has(rid):
		return false
	remove_item(rid, 1)
	var req: Dictionary = RECIPES[rid]["req"]
	for k in req:
		add_item(k, int(req[k]))
	return true


# ------------------------------------------------------------------ vida
func damage(n: int) -> void:
	hp = max(0, hp - n)
	hp_changed.emit()


func heal(n: int) -> void:
	hp = min(MAX_HP, hp + n)
	hp_changed.emit()


func use_gel() -> bool:
	if not has("gel"):
		toast("Você não tem Gel regenerativo.", COL_RED)
		return false
	if hp >= MAX_HP:
		toast("Sua vida já está cheia.", COL_YELLOW)
		return false
	remove_item("gel", 1)
	heal(2)
	toast("Gel regenerativo usado: +2 de vida.", COL_GREEN)
	return true


# ------------------------------------------------------------------ salas
func room(room_id: int) -> Dictionary:
	for r in rooms:
		if int(r["id"]) == room_id:
			return r
	return rooms[0]


# ------------------------------------------------------------------ objetivos
func objective(room_id: int) -> Dictionary:
	var r: Dictionary = room(room_id)
	for st in r["stages"]:
		if not expr_ok(str(st["done"])):
			return {"text": str(st["text"]), "hint": str(st["hint"])}
	return {"text": str(r["final"]), "hint": "Siga em frente."}


# ------------------------------------------------------------------ save / load
func new_game() -> void:
	inv = {}
	flags = {}
	learned = []
	taken = {}
	hp = MAX_HP
	cur_room = 0
	inventory_changed.emit()
	flags_changed.emit()
	recipes_changed.emit()
	hp_changed.emit()


## Convidado usa o save antigo; quem tem conta usa um arquivo próprio (e o banco do backend).
func save_path() -> String:
	if Api.logged_in():
		return "user://rato_save_u%d.json" % int(Api.player.get("id", 0))
	return SAVE_PATH


func has_save() -> bool:
	return FileAccess.file_exists(save_path())


func save_game() -> void:
	var data := {"room": cur_room, "inv": inv, "flags": flags, "learned": learned, "taken": taken, "hp": hp}
	var f := FileAccess.open(save_path(), FileAccess.WRITE)
	if f:
		f.store_string(JSON.stringify(data))
		f.close()
	Api.push_progress(data.duplicate(true))


func load_game() -> bool:
	if not has_save():
		return false
	var txt := FileAccess.get_file_as_string(save_path())
	var data = JSON.parse_string(txt)
	if typeof(data) != TYPE_DICTIONARY:
		return false
	cur_room = int(data.get("room", 1))
	inv = {}
	for k in data.get("inv", {}):
		inv[k] = int(data["inv"][k])
	flags = data.get("flags", {})
	learned = data.get("learned", [])
	taken = data.get("taken", {})
	hp = clampi(int(data.get("hp", MAX_HP)), 0, MAX_HP)
	if hp <= 0:
		hp = MAX_HP
	inventory_changed.emit()
	flags_changed.emit()
	recipes_changed.emit()
	hp_changed.emit()
	return true


# ------------------------------------------------------------------ desenho de ícones
func draw_icon(ci: CanvasItem, id: String, c: Vector2, sz: float, dim: bool = false) -> void:
	if not ITEMS.has(id):
		return
	var it: Dictionary = ITEMS[id]
	var col := Color(it["col"])
	if dim:
		col = col.darkened(0.6)
	var kind: String = it["kind"]
	var icon_path: String = str(it.get("icon", ""))
	var nframes: int = int(it.get("frames", 0))
	if nframes > 0 and icon_path != "":
		icon_path = icon_path % (int(Time.get_ticks_msec() / 170) % nframes)
	if icon_path != "":
		var t := tex(icon_path)
		if t != null:
			var sz_t := Vector2(t.get_width(), t.get_height())
			var s: float = sz / max(sz_t.x, sz_t.y) * 1.1
			var mod := Color(1, 1, 1, 0.45) if dim else Color.WHITE
			ci.draw_texture_rect(t, Rect2(c - sz_t * s / 2.0, sz_t * s), false, mod)
			return
	var r := sz * 0.5
	if kind == "elem":
		ci.draw_circle(c, r, col.darkened(0.6))
		ci.draw_arc(c, r, 0.0, TAU, 28, col, 2.0)
		ci.draw_arc(c, r * 0.68, 0.5, 2.3, 12, col.lightened(0.35), 1.0)
		ci.draw_arc(c, r * 0.68, 3.6, 5.4, 12, col.lightened(0.35), 1.0)
	elif kind == "fict":
		var pts := PackedVector2Array()
		for i in range(6):
			var a := TAU * i / 6.0 + PI / 6.0
			pts.append(c + Vector2(cos(a), sin(a)) * r * 1.05)
		ci.draw_colored_polygon(pts, col.darkened(0.6))
		var closed := pts.duplicate()
		closed.append(pts[0])
		ci.draw_polyline(closed, col, 2.0)
	else:
		var rc := Rect2(c - Vector2(r, r) * 0.95, Vector2(r, r) * 1.9)
		ci.draw_rect(rc, col.darkened(0.65), true)
		ci.draw_rect(rc, col, false, 2.0)
		ci.draw_rect(Rect2(rc.position + Vector2(3, 3), Vector2(rc.size.x - 6, 3)), col.lightened(0.2), true)
	var font := ThemeDB.fallback_font
	var txt: String = it["sym"]
	var fs: int = int(sz * (0.36 if txt.length() > 2 else 0.44))
	var w: float = font.get_string_size(txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
	ci.draw_string(font, c + Vector2(-w / 2.0, fs * 0.36), txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Color.WHITE)
