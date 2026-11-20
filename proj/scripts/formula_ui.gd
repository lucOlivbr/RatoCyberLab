extends CanvasLayer
## Computador de acesso dos armários trancados: arraste as letras para formar a fórmula química.

signal solved(locker_id: String)

var root: Control
var panel: Panel
var title_label: Label
var question: Label
var hint_label: Label
var status: Label
var slots_box: HBoxContainer
var tiles_box: GridContainer
var slot_nodes: Array = []
var tile_nodes: Array = []
var tokens: Array = []
var formula: String = ""
var locker_id: String = ""
var done: bool = false
var t: float = 0.0
var shake: float = 0.0


class Tile extends Control:
	signal clicked(tile)
	var text: String = ""
	var used: bool = false
	var hover: bool = false

	func _ready() -> void:
		custom_minimum_size = Vector2(54, 54)
		size = Vector2(54, 54)
		mouse_filter = Control.MOUSE_FILTER_STOP
		mouse_entered.connect(func(): hover = true; queue_redraw())
		mouse_exited.connect(func(): hover = false; queue_redraw())

	func _draw() -> void:
		var col := Color(0.99, 0.93, 0.04)
		var bg := Color(0.05, 0.1, 0.18, 0.95)
		if used:
			col = col.darkened(0.7)
			bg = Color(0.03, 0.05, 0.08, 0.8)
		elif hover:
			bg = Color(0.1, 0.2, 0.3, 0.98)
		draw_rect(Rect2(Vector2.ZERO, size), bg, true)
		draw_rect(Rect2(Vector2.ZERO, size), col, false, 2.0)
		var f := ThemeDB.fallback_font
		var w: float = f.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, 30).x
		draw_string(f, Vector2((size.x - w) / 2.0, 38), text, HORIZONTAL_ALIGNMENT_LEFT, -1, 30, col)

	func _gui_input(ev: InputEvent) -> void:
		if ev is InputEventMouseButton and ev.button_index == MOUSE_BUTTON_LEFT and not ev.pressed and not used:
			clicked.emit(self)
			accept_event()

	func _get_drag_data(_pos: Vector2):
		if used:
			return null
		var p := Control.new()
		var l := Label.new()
		l.text = text
		l.add_theme_font_size_override("font_size", 34)
		l.add_theme_color_override("font_color", Color(0.99, 0.93, 0.04))
		l.position = Vector2(-10, -22)
		p.add_child(l)
		set_drag_preview(p)
		return {"tile": self}


class Slot extends Control:
	signal dropped(slot, tile)
	signal clicked(slot)
	var tile = null
	var state: int = 0   # 0 neutro, 1 certo, 2 errado

	func _ready() -> void:
		custom_minimum_size = Vector2(62, 66)
		size = Vector2(62, 66)
		mouse_filter = Control.MOUSE_FILTER_STOP

	func _draw() -> void:
		var col := Color(0.1, 0.65, 0.8)
		if state == 1:
			col = Color(0.3, 1.0, 0.5)
		elif state == 2:
			col = Color(1.0, 0.25, 0.3)
		draw_rect(Rect2(Vector2.ZERO, size), Color(0.02, 0.05, 0.1, 0.95), true)
		draw_rect(Rect2(Vector2.ZERO, size), col, false, 2.0)
		if tile != null:
			var f := ThemeDB.fallback_font
			var w: float = f.get_string_size(tile.text, HORIZONTAL_ALIGNMENT_LEFT, -1, 34).x
			draw_string(f, Vector2((size.x - w) / 2.0, 44), tile.text, HORIZONTAL_ALIGNMENT_LEFT, -1, 34, Color(0.99, 0.93, 0.04) if state != 1 else Color(0.5, 1.0, 0.6))
		else:
			draw_line(Vector2(14, 52), Vector2(size.x - 14, 52), Color(col.r, col.g, col.b, 0.5), 2.0)

	func _can_drop_data(_p: Vector2, data) -> bool:
		return typeof(data) == TYPE_DICTIONARY and data.has("tile")

	func _drop_data(_p: Vector2, data) -> void:
		dropped.emit(self, data["tile"])

	func _gui_input(ev: InputEvent) -> void:
		if ev is InputEventMouseButton and ev.button_index == MOUSE_BUTTON_LEFT and ev.pressed and tile != null:
			clicked.emit(self)
			accept_event()


func _ready() -> void:
	layer = 16
	visible = false
	root = Control.new()
	root.set_anchors_preset(Control.PRESET_FULL_RECT)
	root.mouse_filter = Control.MOUSE_FILTER_STOP
	add_child(root)
	var dim := ColorRect.new()
	dim.color = Color(0.0, 0.01, 0.03, 0.88)
	dim.set_anchors_preset(Control.PRESET_FULL_RECT)
	dim.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.add_child(dim)
	panel = Panel.new()
	panel.position = Vector2(120, 70)
	panel.size = Vector2(720, 400)
	panel.add_theme_stylebox_override("panel", Game.panel_style(Color(0.99, 0.93, 0.04), Color(0.02, 0.04, 0.09, 0.98), 2))
	root.add_child(panel)
	title_label = Label.new()
	title_label.text = "COMPUTADOR DE ACESSO  //  ARMÁRIO TRANCADO"
	title_label.position = Vector2(18, 12)
	title_label.add_theme_font_size_override("font_size", 16)
	title_label.add_theme_color_override("font_color", Game.COL_CYAN)
	panel.add_child(title_label)
	question = Label.new()
	question.position = Vector2(18, 46)
	question.size = Vector2(684, 50)
	question.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	question.add_theme_font_size_override("font_size", 17)
	panel.add_child(question)
	slots_box = HBoxContainer.new()
	slots_box.add_theme_constant_override("separation", 12)
	slots_box.alignment = BoxContainer.ALIGNMENT_CENTER
	slots_box.position = Vector2(18, 118)
	slots_box.size = Vector2(684, 70)
	panel.add_child(slots_box)
	var lbl := Label.new()
	lbl.text = "Arraste as letras para os espaços (ou clique nelas):"
	lbl.position = Vector2(18, 204)
	lbl.add_theme_font_size_override("font_size", 12)
	lbl.add_theme_color_override("font_color", Color(0.6, 0.75, 0.9))
	panel.add_child(lbl)
	tiles_box = GridContainer.new()
	tiles_box.columns = 8
	tiles_box.add_theme_constant_override("h_separation", 10)
	tiles_box.add_theme_constant_override("v_separation", 10)
	tiles_box.position = Vector2(80, 228)
	panel.add_child(tiles_box)
	status = Label.new()
	status.position = Vector2(18, 330)
	status.size = Vector2(684, 24)
	status.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	status.add_theme_font_size_override("font_size", 15)
	panel.add_child(status)
	hint_label = Label.new()
	hint_label.position = Vector2(18, 360)
	hint_label.size = Vector2(500, 30)
	hint_label.add_theme_font_size_override("font_size", 11)
	hint_label.add_theme_color_override("font_color", Color(0.55, 0.7, 0.85))
	panel.add_child(hint_label)
	var b1 := _btn("LIMPAR", Vector2(530, 356), Vector2(80, 30), _on_clear)
	var b2 := _btn("SAIR (Esc)", Vector2(618, 356), Vector2(88, 30), close)
	panel.add_child(b1)
	panel.add_child(b2)


func _btn(text: String, pos: Vector2, sz: Vector2, cb: Callable) -> Button:
	var b := Button.new()
	b.text = text
	b.position = pos
	b.size = sz
	b.focus_mode = Control.FOCUS_NONE
	b.add_theme_font_size_override("font_size", 12)
	Game.style_button(b)
	b.pressed.connect(cb)
	return b


## d: {"id", "puzzle": {"title", "formula", "tokens", "decoys", "hint"}}
func open(d: Dictionary) -> void:
	var pz: Dictionary = d["puzzle"]
	locker_id = str(d["id"])
	formula = str(pz["formula"])
	tokens = pz["tokens"].duplicate()
	done = false
	question.text = str(pz["question"])
	hint_label.text = "Dica: " + str(pz.get("hint", ""))
	status.text = "Monte a fórmula usando as letras abaixo."
	status.add_theme_color_override("font_color", Color(0.7, 0.82, 0.95))
	for c in slots_box.get_children():
		c.queue_free()
		slots_box.remove_child(c)
	slot_nodes.clear()
	for i in range(tokens.size()):
		var s := Slot.new()
		s.dropped.connect(_on_drop)
		s.clicked.connect(_on_slot_click)
		slots_box.add_child(s)
		slot_nodes.append(s)
	for c in tiles_box.get_children():
		c.queue_free()
		tiles_box.remove_child(c)
	tile_nodes.clear()
	var all: Array = tokens.duplicate()
	for dc in pz["decoys"]:
		all.append(dc)
	# embaralha de forma determinística
	var rng := RandomNumberGenerator.new()
	rng.seed = hash(locker_id) + 7
	for i in range(all.size() - 1, 0, -1):
		var j := rng.randi_range(0, i)
		var tmp = all[i]
		all[i] = all[j]
		all[j] = tmp
	for tx in all:
		var tl := Tile.new()
		tl.text = str(tx)
		tl.clicked.connect(_on_tile_click)
		tiles_box.add_child(tl)
		tile_nodes.append(tl)
	visible = true


func close() -> void:
	if not visible:
		return
	visible = false
	Game.lock_input(0.25)


func _unhandled_input(ev: InputEvent) -> void:
	if not visible:
		return
	if ev.is_action_pressed("pause") or ev.is_action_pressed("ui_cancel") or ev.is_action_pressed("interact") and done:
		get_viewport().set_input_as_handled()
		close()
	elif ev is InputEventKey and ev.pressed:
		get_viewport().set_input_as_handled()


func _process(delta: float) -> void:
	if not visible:
		return
	t += delta
	if shake > 0.0:
		shake -= delta
		panel.position.x = 120.0 + sin(t * 80.0) * 5.0
	else:
		panel.position.x = 120.0


func _first_empty():
	for s in slot_nodes:
		if s.tile == null:
			return s
	return null


func _place(slot, tile) -> void:
	if done or slot.tile != null or tile.used:
		return
	slot.tile = tile
	tile.used = true
	tile.queue_redraw()
	slot.queue_redraw()
	_check()


func _on_drop(slot, tile) -> void:
	_place(slot, tile)


func _on_tile_click(tile) -> void:
	var s = _first_empty()
	if s != null:
		_place(s, tile)


func _on_slot_click(slot) -> void:
	if done or slot.tile == null:
		return
	slot.tile.used = false
	slot.tile.queue_redraw()
	slot.tile = null
	slot.queue_redraw()


func _on_clear() -> void:
	if done:
		return
	for s in slot_nodes:
		if s.tile != null:
			s.tile.used = false
			s.tile.queue_redraw()
			s.tile = null
		s.state = 0
		s.queue_redraw()


func _check() -> void:
	var txt := ""
	for s in slot_nodes:
		if s.tile == null:
			return
		txt += s.tile.text
	if txt == formula:
		done = true
		for s in slot_nodes:
			s.state = 1
			s.queue_redraw()
		status.text = "ACESSO LIBERADO!  Fórmula correta: %s" % formula
		status.add_theme_color_override("font_color", Color(0.4, 1.0, 0.55))
		await get_tree().create_timer(1.1).timeout
		var id := locker_id
		close()
		solved.emit(id)
	else:
		for s in slot_nodes:
			s.state = 2
			s.queue_redraw()
		status.text = "Fórmula incorreta. Tente de novo."
		Api.report_error("FORMULA_ERRADA", Game.cur_room, "Armário %s: montou %s (certa: %s)" % [locker_id, txt, formula])
		status.add_theme_color_override("font_color", Color(1.0, 0.35, 0.4))
		shake = 0.35
		await get_tree().create_timer(0.8).timeout
		if not done:
			_on_clear()
			status.text = "Monte a fórmula usando as letras abaixo."
			status.add_theme_color_override("font_color", Color(0.7, 0.82, 0.95))
