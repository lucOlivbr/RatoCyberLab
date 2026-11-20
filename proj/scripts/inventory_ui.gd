extends CanvasLayer
## Inventário completo (tecla I): ícone, nome, quantidade e descrição de cada material.

const ItemIcon := preload("res://scripts/item_icon.gd")

var root: Control
var list: VBoxContainer
var hp_label: Label


func _ready() -> void:
	layer = 14
	visible = false
	root = Control.new()
	root.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(root)
	var dim := ColorRect.new()
	dim.color = Color(0.01, 0.02, 0.05, 0.88)
	dim.set_anchors_preset(Control.PRESET_FULL_RECT)
	root.add_child(dim)
	var p := Panel.new()
	p.position = Vector2(150, 30)
	p.size = Vector2(660, 480)
	p.add_theme_stylebox_override("panel", Game.panel_style(Game.COL_CYAN, Color(0.03, 0.05, 0.1, 0.98), 2))
	root.add_child(p)
	var t := Label.new()
	t.text = "INVENTÁRIO"
	t.position = Vector2(16, 10)
	t.add_theme_font_size_override("font_size", 20)
	t.add_theme_color_override("font_color", Game.COL_CYAN)
	p.add_child(t)
	hp_label = Label.new()
	hp_label.position = Vector2(480, 14)
	hp_label.add_theme_font_size_override("font_size", 13)
	hp_label.add_theme_color_override("font_color", Game.COL_GREEN)
	p.add_child(hp_label)
	var sc := ScrollContainer.new()
	sc.position = Vector2(12, 46)
	sc.size = Vector2(636, 396)
	sc.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	p.add_child(sc)
	list = VBoxContainer.new()
	list.custom_minimum_size = Vector2(620, 0)
	list.add_theme_constant_override("separation", 6)
	sc.add_child(list)
	var f := Label.new()
	f.text = "I / Esc: fechar    F: usar Gel regenerativo    C: bancada (perto de uma)"
	f.position = Vector2(16, 450)
	f.add_theme_font_size_override("font_size", 11)
	f.add_theme_color_override("font_color", Color(0.55, 0.65, 0.8))
	p.add_child(f)


func open() -> void:
	visible = true
	refresh()


func close() -> void:
	if not visible:
		return
	visible = false
	Game.lock_input(0.25)


func refresh() -> void:
	hp_label.text = "VIDA  %d / %d" % [Game.hp, Game.MAX_HP]
	for c in list.get_children():
		c.queue_free()
		list.remove_child(c)
	var any := false
	for id in Game.ITEM_ORDER:
		var n := Game.count(id)
		if n <= 0:
			continue
		any = true
		var row := HBoxContainer.new()
		row.add_theme_constant_override("separation", 12)
		var ic := ItemIcon.new()
		ic.setup(id, 0, 44.0, true)
		ic.show_count = false
		row.add_child(ic)
		var col := VBoxContainer.new()
		var nm := Label.new()
		var kind: String = str(Game.ITEMS[id]["kind"])
		var tag := "elemento químico" if kind == "elem" else ("componente experimental (fictício)" if kind == "fict" else "item fabricado")
		nm.text = "%s  x%d   [%s]" % [Game.item_name(id), n, tag]
		nm.add_theme_font_size_override("font_size", 14)
		nm.add_theme_color_override("font_color", Game.item_color(id).lightened(0.35))
		col.add_child(nm)
		var ds := Label.new()
		ds.text = str(Game.ITEMS[id]["desc"])
		ds.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		ds.custom_minimum_size = Vector2(540, 0)
		ds.add_theme_font_size_override("font_size", 11)
		ds.add_theme_color_override("font_color", Color(0.7, 0.8, 0.92))
		col.add_child(ds)
		row.add_child(col)
		list.add_child(row)
	if not any:
		var l := Label.new()
		l.text = "Você ainda não carrega nada. Explore a sala e colete componentes."
		l.add_theme_font_size_override("font_size", 14)
		list.add_child(l)


func _unhandled_input(ev: InputEvent) -> void:
	if not visible:
		return
	if ev.is_action_pressed("inventory") or ev.is_action_pressed("pause") or ev.is_action_pressed("ui_cancel"):
		get_viewport().set_input_as_handled()
		close()
	elif ev.is_action_pressed("heal"):
		get_viewport().set_input_as_handled()
		Game.use_gel()
		refresh()
