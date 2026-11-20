extends CanvasLayer
## Bancada científica interativa: arraste itens para os recipientes, acenda o maçarico e fabrique.

const ItemIcon := preload("res://scripts/item_icon.gd")
const Vessel := preload("res://scripts/vessel.gd")
const TABLE_SCALE := 0.8
const TABLE_POS := Vector2(14, 44)
const PRODUCT_CENTER := Vector2(665.0, 330.0)
const VESSEL_X := [190.0, 258.0, 326.0]
const VESSEL_Y := 236.0
const FIRE_RECT := Rect2(398.0, 222.0, 60.0, 76.0)
const ERLEN := Vector2(547.0, 239.0)   # base do erlenmeyer na tela

var vessels: Array = []        # nós Vessel
var order: Array = []          # histórico (índices) para "retirar último"
var temp: int = 0               # 0..4, ajustado pelas setinhas ▲▼ do painel TEMP
var fire: bool:                 # o maçarico só "esquenta" de verdade a partir do nível 2
	get:
		return temp >= 2
	set(v):
		temp = 2 if v else 0
const UP_RECT := Rect2(455.0, 309.0, 15.0, 13.0)
const DOWN_RECT := Rect2(455.0, 325.0, 15.0, 13.0)
const TEMPS := [25, 90, 220, 380, 540]
var arrows_node: Control
var arrow_hover: int = 0
var busy: bool = false
var broken: bool = false       # bancada estragada do tutorial
var fx_t: float = 0.0
var fx_col: Color = Color.WHITE
var fx_rid: String = ""
var root: Control
var inv_grid: GridContainer
var book_box: VBoxContainer
var status_label: Label
var desc_label: Label
var product_node: Control
var craft_btn: Button
var fire_btn: Button
var fire_node: Control
var erlen_node: Control
var fx_node: Control
var broken_node: Control
var title_label: Label
var current_rid: String = ""
var t: float = 0.0


func _ready() -> void:
	layer = 15
	visible = false
	root = Control.new()
	root.set_anchors_preset(Control.PRESET_FULL_RECT)
	root.mouse_filter = Control.MOUSE_FILTER_STOP
	add_child(root)

	var dim := ColorRect.new()
	dim.color = Color(0.01, 0.02, 0.05, 1.0)
	dim.set_anchors_preset(Control.PRESET_FULL_RECT)
	dim.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.add_child(dim)

	title_label = Label.new()
	title_label.text = "BANCADA CIENTÍFICA // CRAFTTABLE"
	title_label.position = Vector2(14, 10)
	title_label.add_theme_font_size_override("font_size", 18)
	title_label.add_theme_color_override("font_color", Game.COL_CYAN)
	root.add_child(title_label)

	var tr := TextureRect.new()
	tr.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	tr.stretch_mode = TextureRect.STRETCH_SCALE
	tr.texture = Game.tex("res://assets/ui/craft_table.png")
	tr.position = TABLE_POS
	tr.custom_minimum_size = Vector2(768, 512) * TABLE_SCALE
	tr.size = Vector2(768, 512) * TABLE_SCALE
	tr.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.add_child(tr)

	broken_node = Control.new()
	broken_node.size = Vector2(960, 540)
	broken_node.mouse_filter = Control.MOUSE_FILTER_IGNORE
	broken_node.draw.connect(_draw_broken)
	root.add_child(broken_node)

	# painel de reação sobre a grade antiga
	var rp := Panel.new()
	rp.position = Vector2(182, 228)
	rp.size = Vector2(212, 124)
	rp.add_theme_stylebox_override("panel", Game.panel_style(Color(0.1, 0.6, 0.75), Color(0.02, 0.05, 0.1, 0.96), 1))
	rp.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.add_child(rp)
	var rl := Label.new()
	rl.text = "ÁREA DE REAÇÃO  (arraste os itens)"
	rl.position = Vector2(188, 213)
	rl.add_theme_font_size_override("font_size", 10)
	rl.add_theme_color_override("font_color", Game.COL_YELLOW)
	root.add_child(rl)
	for i in range(3):
		var v := Vessel.new()
		v.index = i
		v.position = Vector2(VESSEL_X[i], VESSEL_Y)
		v.dropped.connect(_on_drop)
		v.removed.connect(_on_vessel_remove)
		root.add_child(v)
		vessels.append(v)

	# maçarico (clicável) e erlenmeyer (mistura final)
	erlen_node = Control.new()
	erlen_node.position = Vector2.ZERO
	erlen_node.size = Vector2(960, 540)
	erlen_node.mouse_filter = Control.MOUSE_FILTER_IGNORE
	erlen_node.draw.connect(_draw_erlen)
	root.add_child(erlen_node)
	fire_node = Control.new()
	fire_node.position = FIRE_RECT.position
	fire_node.size = FIRE_RECT.size
	fire_node.mouse_filter = Control.MOUSE_FILTER_STOP
	fire_node.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	fire_node.tooltip_text = "Maçarico: clique para acender/apagar (Espaço). Esquente com as setas ▲▼ do painel TEMP (↑/↓)."
	fire_node.draw.connect(_draw_fire)
	fire_node.gui_input.connect(func(ev):
		if ev is InputEventMouseButton and ev.pressed and ev.button_index == MOUSE_BUTTON_LEFT:
			_toggle_fire())
	root.add_child(fire_node)

	arrows_node = Control.new()
	arrows_node.position = Vector2(452.0, 304.0)
	arrows_node.size = Vector2(22.0, 38.0)
	arrows_node.mouse_filter = Control.MOUSE_FILTER_STOP
	arrows_node.draw.connect(_draw_arrows)
	arrows_node.gui_input.connect(_arrows_input)
	arrows_node.mouse_exited.connect(func(): arrow_hover = 0)
	root.add_child(arrows_node)

	product_node = ItemIcon.new()
	product_node.setup("", 0, 44.0, false)
	product_node.show_count = false
	product_node.position = TABLE_POS + PRODUCT_CENTER * TABLE_SCALE - Vector2(22, 8)
	root.add_child(product_node)

	fx_node = Control.new()
	fx_node.size = Vector2(960, 540)
	fx_node.mouse_filter = Control.MOUSE_FILTER_IGNORE
	fx_node.draw.connect(_draw_fx)
	root.add_child(fx_node)

	status_label = Label.new()
	status_label.position = Vector2(14, 494)
	status_label.size = Vector2(612, 20)
	status_label.add_theme_font_size_override("font_size", 14)
	root.add_child(status_label)

	desc_label = Label.new()
	desc_label.position = Vector2(14, 512)
	desc_label.size = Vector2(612, 22)
	desc_label.add_theme_font_size_override("font_size", 11)
	desc_label.add_theme_color_override("font_color", Color(0.65, 0.78, 0.9))
	desc_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	root.add_child(desc_label)

	craft_btn = _button("FABRICAR (Enter)", Vector2(14, 458), Vector2(150, 30), _on_craft)
	fire_btn = _button("MAÇARICO: APAGADO", Vector2(172, 458), Vector2(170, 30), _toggle_fire)
	_button("LIMPAR (Backspace)", Vector2(350, 458), Vector2(150, 30), _on_clear)
	_button("FECHAR (C)", Vector2(508, 458), Vector2(118, 30), close)

	var ip := Panel.new()
	ip.position = Vector2(640, 44)
	ip.size = Vector2(310, 244)
	ip.add_theme_stylebox_override("panel", Game.panel_style(Color(0.1, 0.6, 0.75), Color(0.03, 0.06, 0.12, 0.95), 1))
	root.add_child(ip)
	var ilabel := Label.new()
	ilabel.text = "INVENTÁRIO  (arraste para um recipiente)"
	ilabel.position = Vector2(8, 2)
	ilabel.add_theme_font_size_override("font_size", 11)
	ilabel.add_theme_color_override("font_color", Game.COL_YELLOW)
	ip.add_child(ilabel)
	var sc := ScrollContainer.new()
	sc.position = Vector2(6, 20)
	sc.size = Vector2(298, 220)
	sc.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	ip.add_child(sc)
	inv_grid = GridContainer.new()
	inv_grid.columns = 5
	inv_grid.add_theme_constant_override("h_separation", 4)
	inv_grid.add_theme_constant_override("v_separation", 4)
	sc.add_child(inv_grid)

	var bp := Panel.new()
	bp.position = Vector2(640, 296)
	bp.size = Vector2(310, 238)
	bp.add_theme_stylebox_override("panel", Game.panel_style(Color(0.1, 0.6, 0.75), Color(0.03, 0.06, 0.12, 0.95), 1))
	root.add_child(bp)
	var blabel := Label.new()
	blabel.text = "LIVRO DE RECEITAS"
	blabel.position = Vector2(8, 2)
	blabel.add_theme_font_size_override("font_size", 11)
	blabel.add_theme_color_override("font_color", Game.COL_YELLOW)
	bp.add_child(blabel)
	var bsc := ScrollContainer.new()
	bsc.position = Vector2(6, 20)
	bsc.size = Vector2(298, 196)
	bsc.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	bp.add_child(bsc)
	book_box = VBoxContainer.new()
	book_box.custom_minimum_size = Vector2(290, 0)
	book_box.add_theme_constant_override("separation", 4)
	bsc.add_child(book_box)
	var tip := Label.new()
	tip.text = "Clique direito num item fabricado para desmontá-lo."
	tip.position = Vector2(8, 218)
	tip.add_theme_font_size_override("font_size", 9)
	tip.add_theme_color_override("font_color", Color(0.5, 0.62, 0.78))
	bp.add_child(tip)

	Game.inventory_changed.connect(func(): if visible and not busy: refresh())
	Game.recipes_changed.connect(func(): if visible and not busy: refresh())


func _process(delta: float) -> void:
	if not visible:
		return
	t += delta
	if broken:
		broken_node.queue_redraw()
	fire_node.queue_redraw()
	arrows_node.queue_redraw()
	erlen_node.queue_redraw()


func _button(text: String, pos: Vector2, sz: Vector2, cb: Callable) -> Button:
	var b := Button.new()
	b.text = text
	b.position = pos
	b.size = sz
	b.focus_mode = Control.FOCUS_NONE
	b.add_theme_font_size_override("font_size", 13)
	Game.style_button(b)
	b.pressed.connect(cb)
	root.add_child(b)
	return b


func open(is_broken: bool = false) -> void:
	broken = is_broken
	title_label.text = "BANCADA DANIFICADA // IMPROVISE" if broken else "BANCADA CIENTÍFICA // CRAFTTABLE"
	title_label.add_theme_color_override("font_color", Game.COL_YELLOW if broken else Game.COL_CYAN)
	broken_node.visible = broken
	visible = true
	_reset_state()
	refresh()


func close() -> void:
	if not visible or busy:
		return
	visible = false
	_reset_state()
	Game.lock_input(0.25)


func _reset_state() -> void:
	for v in vessels:
		v.item_id = ""
		v.amount = 0
		v.lit = false
	order.clear()
	fire = false
	fx_t = 0.0
	fx_rid = ""


# ------------------------------------------------------------------ entrada
func _unhandled_input(ev: InputEvent) -> void:
	if not visible:
		return
	if busy:
		get_viewport().set_input_as_handled()
		return
	if ev.is_action_pressed("craft") or ev.is_action_pressed("pause") or ev.is_action_pressed("ui_cancel"):
		get_viewport().set_input_as_handled()
		close()
	elif ev is InputEventKey and ev.pressed and not ev.echo and (ev.keycode == KEY_ENTER or ev.keycode == KEY_KP_ENTER):
		get_viewport().set_input_as_handled()
		_on_craft()
	elif ev is InputEventKey and ev.pressed and not ev.echo and ev.keycode == KEY_SPACE:
		get_viewport().set_input_as_handled()
		_toggle_fire()
	elif ev is InputEventKey and ev.pressed and not ev.echo and (ev.keycode == KEY_UP or ev.keycode == KEY_DOWN):
		get_viewport().set_input_as_handled()
		_change_temp(1 if ev.keycode == KEY_UP else -1)
	elif ev is InputEventKey and ev.pressed and not ev.echo and ev.keycode == KEY_BACKSPACE:
		get_viewport().set_input_as_handled()
		_on_undo()
	elif ev is InputEventKey and ev.pressed:
		get_viewport().set_input_as_handled()


func _slots() -> Array:
	var out: Array = []
	for v in vessels:
		for i in range(v.amount):
			out.append(v.item_id)
	return out


func _placed(id: String) -> int:
	var n := 0
	for v in vessels:
		if v.item_id == id:
			n += v.amount
	return n


func _add_to_vessel(i: int, id: String) -> void:
	if busy or id == "":
		return
	var v = vessels[i]
	if Game.count(id) - _placed(id) <= 0:
		Game.toast("Você não tem mais %s." % Game.item_name(id), Game.COL_RED)
		return
	if v.amount > 0 and v.item_id != id:
		Game.toast("O recipiente %d já tem %s. Cada recipiente guarda um tipo de item." % [i + 1, Game.item_name(v.item_id)], Game.COL_YELLOW)
		v.shake = 0.3
		return
	if v.amount >= Vessel.MAX_N:
		Game.toast("Recipiente cheio.", Game.COL_YELLOW)
		return
	v.item_id = id
	v.amount += 1
	order.append(i)
	refresh()


func _on_drop(i: int, id: String) -> void:
	_add_to_vessel(i, id)


func _on_vessel_remove(i: int) -> void:
	if busy:
		return
	var v = vessels[i]
	if v.amount <= 0:
		return
	v.amount -= 1
	if v.amount == 0:
		v.item_id = ""
	var k: int = order.rfind(i)
	if k >= 0:
		order.remove_at(k)
	refresh()


func _on_inv_click(id: String, button: int) -> void:
	if busy:
		return
	if button == MOUSE_BUTTON_RIGHT:
		if Game.RECIPES.has(id) and Game.count(id) - _placed(id) > 0:
			Game.recycle(id)
			Game.toast("%s desmontado em componentes." % Game.item_name(id), Game.COL_YELLOW)
			refresh()
		return
	# clique simples: vai para o recipiente que já tem o item, senão para o primeiro vazio
	for i in range(3):
		if vessels[i].amount > 0 and vessels[i].item_id == id:
			_add_to_vessel(i, id)
			return
	for i in range(3):
		if vessels[i].amount == 0:
			_add_to_vessel(i, id)
			return
	Game.toast("Os 3 recipientes estão ocupados. Esvazie um deles.", Game.COL_RED)


func _on_undo() -> void:
	if busy or order.is_empty():
		return
	var i: int = int(order.pop_back())
	var v = vessels[i]
	v.amount -= 1
	if v.amount <= 0:
		v.amount = 0
		v.item_id = ""
	refresh()


func _on_clear() -> void:
	if busy:
		return
	for v in vessels:
		v.item_id = ""
		v.amount = 0
	order.clear()
	fire = false
	refresh()


func _toggle_fire() -> void:
	if busy:
		return
	temp = 1 if temp == 0 else 0     # acende só a chama-piloto; o calor sobe pelas setas ▲▼
	refresh()


func _change_temp(d: int) -> void:
	if busy:
		return
	temp = clampi(temp + d, 0, 4)
	refresh()


func _arrows_input(ev: InputEvent) -> void:
	if ev is InputEventMouseMotion:
		var p: Vector2 = ev.position + arrows_node.position
		arrow_hover = 1 if UP_RECT.grow(2).has_point(p) else (2 if DOWN_RECT.grow(2).has_point(p) else 0)
		arrows_node.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND if arrow_hover > 0 else Control.CURSOR_ARROW
	elif ev is InputEventMouseButton and ev.pressed and ev.button_index == MOUSE_BUTTON_LEFT:
		var p2: Vector2 = ev.position + arrows_node.position
		if UP_RECT.grow(2).has_point(p2):
			_change_temp(1)
			arrows_node.accept_event()
		elif DOWN_RECT.grow(2).has_point(p2):
			_change_temp(-1)
			arrows_node.accept_event()


func _draw_arrows() -> void:
	# a leitura de temperatura cobre o "0°C" da arte e as duas setinhas ficam interativas
	arrows_node.draw_set_transform(-arrows_node.position, 0.0, Vector2.ONE)
	var hot: bool = temp >= 2
	var col := Color(1.0, 0.55, 0.2) if hot else Color(0.35, 0.85, 0.95)
	arrows_node.draw_rect(Rect2(426.0, 321.0, 27.0, 13.0), Color(0.02, 0.07, 0.13), true)
	var f := ThemeDB.fallback_font
	arrows_node.draw_string(f, Vector2(427.0, 331.0), "%d°C" % TEMPS[temp], HORIZONTAL_ALIGNMENT_LEFT, -1, 9, col)
	for k in range(2):
		var r: Rect2 = UP_RECT if k == 0 else DOWN_RECT
		var on: bool = arrow_hover == k + 1
		var act: bool = (k == 0 and temp < 4) or (k == 1 and temp > 0)
		var bg := Color(0.05, 0.14, 0.22)
		if on:
			bg = Color(0.12, 0.28, 0.4)
		arrows_node.draw_rect(r, bg, true)
		arrows_node.draw_rect(r, col if act else Color(0.2, 0.35, 0.45), false, 1.0)
		var c: Vector2 = r.get_center()
		var pts: PackedVector2Array
		if k == 0:
			pts = PackedVector2Array([c + Vector2(-4, 3), c + Vector2(4, 3), c + Vector2(0, -4)])
		else:
			pts = PackedVector2Array([c + Vector2(-4, -3), c + Vector2(4, -3), c + Vector2(0, 4)])
		var ac := col if act else Color(0.25, 0.4, 0.5)
		if k == 0 and temp < 2:
			ac.a = 0.6 + 0.4 * sin(t * 5.0)   # convida a clicar para esquentar
		arrows_node.draw_colored_polygon(pts, ac)
	# calor subindo do maçarico até o painel pelas duas setas
	if temp > 0:
		for i in range(3):
			var q: float = fmod(t * 0.8 + float(i) * 0.33, 1.0)
			arrows_node.draw_circle(Vector2(446.0 + float(i) * 8.0, 300.0 - q * 18.0), 1.5 + 0.5 * float(temp), Color(1.0, 0.6, 0.2, (1.0 - q) * 0.5))


# ------------------------------------------------------------------ fabricar
func _on_craft() -> void:
	if busy or current_rid == "":
		return
	busy = true
	fx_rid = current_rid
	fx_col = Game.item_color(current_rid)
	craft_btn.disabled = true
	var heated: bool = fire
	status_label.text = "Fundindo os componentes..." if heated else "Misturando os componentes..."
	status_label.add_theme_color_override("font_color", Game.COL_YELLOW)
	desc_label.text = ""
	fx_t = 0.0
	var tw := create_tween()
	tw.tween_method(func(x: float): fx_t = x; fx_node.queue_redraw(), 0.0, 1.0, 1.7 if heated else 1.2)
	tw.tween_callback(_finish_craft)


func _finish_craft() -> void:
	var rid := fx_rid
	var was_new := not Game.learned.has(rid)
	var made := Game.craft(_slots(), fire)
	busy = false
	fx_t = 0.0
	fx_node.queue_redraw()
	if made == "":
		Game.toast("Faltam materiais para fabricar.", Game.COL_RED)
		refresh()
		return
	for v in vessels:
		v.item_id = ""
		v.amount = 0
	order.clear()
	fire = false
	var msg := "Fabricado: %s" % Game.item_name(made)
	if was_new:
		msg += "  (receita registrada no livro)"
	Game.toast(msg, Game.COL_GREEN)
	refresh()
	status_label.text = "Fabricado com sucesso: %s" % Game.item_name(made)
	status_label.add_theme_color_override("font_color", Game.COL_GREEN)
	desc_label.text = str(Game.ITEMS[made]["desc"])
	crafted.emit(made)


signal crafted(item_id: String)


# ------------------------------------------------------------------ análise
func _is_partial() -> bool:
	var cnt: Dictionary = {}
	for s in _slots():
		cnt[s] = int(cnt.get(s, 0)) + 1
	if cnt.is_empty():
		return false
	for rid in Game.RECIPES:
		var req: Dictionary = Game.RECIPES[rid]["req"]
		var ok := true
		for k in cnt:
			if int(cnt[k]) > int(req.get(k, 0)):
				ok = false
				break
		if ok:
			return true
	return false


var last_err_sig: String = ""


## Descreve a mistura dos recipientes, ex.: "2 Hidrogênio + 1 Cobre".
func _mix_text(slots: Array) -> String:
	var cnt: Dictionary = {}
	for s in slots:
		cnt[s] = int(cnt.get(s, 0)) + 1
	var parts: Array = []
	for k in cnt:
		parts.append("%d %s" % [cnt[k], Game.item_name(str(k))])
	return " + ".join(parts)


## Registra o erro no relatório uma única vez por mistura (refresh roda a cada clique).
func _report_craft_error(slots: Array, why: String) -> void:
	var sig := why + "|" + _mix_text(slots) + "|" + str(fire)
	if sig == last_err_sig:
		return
	last_err_sig = sig
	Api.report_error("RECEITA_INVALIDA", Game.cur_room, "%s: %s%s" % [why, _mix_text(slots), " (maçarico aceso)" if fire else ""])


func refresh() -> void:
	var slots := _slots()
	for v in vessels:
		v.lit = fire
		v.queue_redraw()
	# inventário (itens arrastáveis)
	for c in inv_grid.get_children():
		c.queue_free()
		inv_grid.remove_child(c)
	for id in Game.ITEM_ORDER:
		var avail: int = Game.count(id) - _placed(id)
		if avail <= 0:
			continue
		var ic := ItemIcon.new()
		ic.setup(id, avail, 56.0, true)
		ic.draggable = true
		ic.clicked.connect(_on_inv_click)
		inv_grid.add_child(ic)
	fire_btn.text = ("MAÇARICO: %d°C" % TEMPS[temp]) if temp > 0 else "MAÇARICO: APAGADO"
	# análise
	current_rid = Game.match_recipe(slots, fire)
	var alt: String = Game.match_recipe(slots, not fire) if current_rid == "" else ""
	var empty := slots.is_empty()
	if current_rid != "" or empty:
		last_err_sig = ""
	if current_rid != "":
		status_label.text = "Combinação válida: %s" % Game.item_name(current_rid)
		status_label.add_theme_color_override("font_color", Game.COL_GREEN)
		desc_label.text = "%s — %s" % [Game.recipe_text(current_rid), str(Game.ITEMS[current_rid]["desc"])]
		(product_node as Control).set("item_id", current_rid)
	else:
		(product_node as Control).set("item_id", "")
		if alt != "":
			if fire:
				_report_craft_error(slots, "Esta mistura não usa fogo")
				status_label.text = "Esta mistura não usa fogo. Desça a temperatura com ▼ até apagar."
			else:
				status_label.text = "Mistura correta! Falta esquentar: acenda o maçarico e suba a temperatura com ▲ (200°C+)."
			status_label.add_theme_color_override("font_color", Game.COL_YELLOW)
			desc_label.text = "Os componentes estão certos, mas o fogo não. Nada foi consumido."
		elif empty:
			status_label.text = "Arraste itens do inventário para os recipientes."
			status_label.add_theme_color_override("font_color", Color(0.6, 0.7, 0.85))
			desc_label.text = "Nada é consumido até você confirmar a fabricação. Algumas receitas precisam do maçarico."
		elif _is_partial():
			status_label.text = "Combinação incompleta. Nenhum material foi consumido."
			status_label.add_theme_color_override("font_color", Game.COL_YELLOW)
			desc_label.text = "Continue adicionando componentes ou consulte o livro de receitas."
		else:
			_report_craft_error(slots, "Combinação desconhecida")
			status_label.text = "Experimento não reconhecido."
			status_label.add_theme_color_override("font_color", Game.COL_RED)
			desc_label.text = "Esta combinação é desconhecida. Nenhum material foi consumido."
	product_node.queue_redraw()
	craft_btn.disabled = current_rid == "" or busy
	_rebuild_book()
	fire_node.queue_redraw()


func _rebuild_book() -> void:
	for c in book_box.get_children():
		c.queue_free()
		book_box.remove_child(c)
	for rid in Game.RECIPES:
		var l := Label.new()
		l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		l.custom_minimum_size = Vector2(286, 0)
		l.add_theme_font_size_override("font_size", 11)
		if Game.learned.has(rid):
			l.text = "%s\n   %s" % [Game.item_name(rid), Game.recipe_text(rid)]
			l.add_theme_color_override("font_color", Game.item_color(rid).lightened(0.3))
		else:
			l.text = "???  (receita desconhecida)\n   Ache pistas em terminais e pesquisadores, ou experimente."
			l.add_theme_color_override("font_color", Color(0.45, 0.52, 0.65))
		book_box.add_child(l)


# ------------------------------------------------------------------ desenho
func _mix_color() -> Color:
	var r := 0.0
	var g := 0.0
	var b := 0.0
	var n := 0
	for v in vessels:
		if v.amount > 0:
			var c: Color = v.liquid_color()
			r += c.r * v.amount
			g += c.g * v.amount
			b += c.b * v.amount
			n += v.amount
	if n == 0:
		return Color(0, 0, 0, 0)
	return Color(r / n, g / n, b / n)


func _draw_erlen() -> void:
	var total := 0
	for v in vessels:
		total += v.amount
	var col := _mix_color()
	if busy:
		col = col.lerp(fx_col, fx_t)
		total = maxi(total, 4)
	if total <= 0:
		return
	var lvl: float = clampf(float(total) / 6.0, 0.25, 1.0)
	var base_y: float = ERLEN.y + 4.0
	var h: float = 26.0 * lvl
	var wb: float = 30.0
	var wt: float = 30.0 - 16.0 * lvl
	var pts := PackedVector2Array([
		Vector2(ERLEN.x - wb * 0.5, base_y), Vector2(ERLEN.x + wb * 0.5, base_y),
		Vector2(ERLEN.x + wt * 0.5, base_y - h), Vector2(ERLEN.x - wt * 0.5, base_y - h)])
	erlen_node.draw_colored_polygon(pts, Color(col.r, col.g, col.b, 0.62))
	erlen_node.draw_line(pts[3], pts[2], col.lightened(0.4), 2.0)
	for i in range(3):
		var bt: float = fmod(t * 0.7 + float(i) * 0.33, 1.0)
		erlen_node.draw_circle(Vector2(ERLEN.x - 5.0 + float(i) * 5.0 + sin(t * 4.0 + float(i)) * 1.5, base_y - bt * h), 1.5, col.lightened(0.55))


func _draw_fire() -> void:
	var cx: float = 25.0                  # ponta do maçarico (onde a chama sempre esteve)
	var by: float = 28.0
	if temp == 0 and not (busy and fx_rid != "" and Game.RECIPES[fx_rid].get("fire", false)):
		return   # maçarico desligado: sem chama
	var flare: float = 1.0
	if busy:
		flare = 1.0 + 0.5 * sin(fx_t * PI)
	var h: float = [8.0, 20.0, 28.0, 35.0, 42.0][temp] * flare
	if busy and temp == 0:
		h = 28.0 * flare
	var sway: float = sin(t * 11.0) * 1.5
	fire_node.draw_circle(Vector2(cx, by - h * 0.4), 15.0 * flare, Color(0.2, 0.55, 1.0, 0.18))
	var outer := PackedVector2Array([Vector2(cx - 6, by), Vector2(cx - 4.5, by - h * 0.55), Vector2(cx + sway, by - h), Vector2(cx + 4.5, by - h * 0.55), Vector2(cx + 6, by)])
	fire_node.draw_colored_polygon(outer, Color(0.12, 0.38, 1.0, 0.92))
	var mid := PackedVector2Array([Vector2(cx - 4, by), Vector2(cx - 3, by - h * 0.45), Vector2(cx + sway * 0.7, by - h * 0.78), Vector2(cx + 3, by - h * 0.45), Vector2(cx + 4, by)])
	fire_node.draw_colored_polygon(mid, Color(0.25, 0.7, 1.0, 0.95))
	var core := PackedVector2Array([Vector2(cx - 3.5, by), Vector2(cx - 2, by - h * 0.3), Vector2(cx + sway * 0.4, by - h * 0.5), Vector2(cx + 2, by - h * 0.3), Vector2(cx + 3.5, by)])
	fire_node.draw_colored_polygon(core, Color(0.85, 0.98, 1.0, 0.97))


func _draw_fx() -> void:
	if not busy:
		return
	var target: Vector2 = TABLE_POS + PRODUCT_CENTER * TABLE_SCALE
	var heated: bool = bool(Game.RECIPES[fx_rid].get("fire", false))
	for i in range(3):
		var v = vessels[i]
		if v.amount <= 0:
			continue
		var from: Vector2 = v.position + Vector2(30, 56)
		var col: Color = v.liquid_color()
		# partículas viajando do recipiente até o erlenmeyer e depois ao produto
		for k in range(7):
			var p: float = clampf(fx_t * 1.4 - float(k) * 0.07 - float(i) * 0.04, 0.0, 1.0)
			if p <= 0.0 or p >= 1.0:
				continue
			var mid: Vector2 = Vector2((from.x + ERLEN.x) * 0.5, minf(from.y, ERLEN.y) - 40.0)
			var a: Vector2 = from.lerp(mid, p)
			var b: Vector2 = mid.lerp(ERLEN + Vector2(0, -12), p)
			var pos: Vector2 = a.lerp(b, p)
			fx_node.draw_circle(pos, 3.0, col.lightened(0.3))
	# faíscas no produto no final
	if fx_t > 0.7:
		var q: float = (fx_t - 0.7) / 0.3
		for k in range(10):
			var ang: float = TAU * float(k) / 10.0 + t * 2.0
			var rr: float = 10.0 + q * 28.0
			var c := fx_col.lightened(0.4)
			c.a = 1.0 - q * 0.6
			fx_node.draw_circle(target + Vector2(cos(ang), sin(ang)) * rr + Vector2(0, 6), 2.4, c)
	if heated:
		var h := Color(1.0, 0.6, 0.2, 0.18 * sin(fx_t * PI))
		fx_node.draw_rect(Rect2(182, 228, 212, 124), h, true)


func _draw_broken() -> void:
	# rachaduras no vidro, faíscas e luz piscando: a bancada do tutorial está estragada
	var crack := Color(0.75, 0.9, 1.0, 0.75)
	var lines := [
		[Vector2(222, 112), Vector2(232, 128), Vector2(228, 142), Vector2(240, 160)],
		[Vector2(232, 128), Vector2(248, 126), Vector2(262, 136)],
		[Vector2(520, 224), Vector2(530, 214), Vector2(534, 198), Vector2(546, 186)],
		[Vector2(530, 214), Vector2(548, 218)],
		[Vector2(112, 300), Vector2(124, 312), Vector2(118, 330)],
	]
	for ln in lines:
		broken_node.draw_polyline(PackedVector2Array(ln), crack, 1.5)
	var phase: int = int(t * 6.0)
	var spots := [Vector2(112, 160), Vector2(300, 190), Vector2(470, 250), Vector2(600, 330)]
	for i in range(spots.size()):
		if (phase + i * 3) % 7 < 2:
			var sp: Vector2 = spots[i]
			for k in range(4):
				var a: float = float((phase * 37 + k * 90 + i * 50) % 360) * PI / 180.0
				broken_node.draw_line(sp, sp + Vector2(cos(a), sin(a)) * (6.0 + float(k) * 2.0), Color(1.0, 0.9, 0.4, 0.95), 1.5)
			broken_node.draw_circle(sp, 3.0, Color(1.0, 0.95, 0.6, 0.9))
	if (phase % 11) == 0:
		broken_node.draw_rect(Rect2(14, 44, 614, 410), Color(0.0, 0.0, 0.0, 0.25), true)
