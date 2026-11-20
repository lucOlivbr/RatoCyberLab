extends CanvasLayer
## HUD inferior (vida, objetivo, componentes), avisos (toast) e faixa de título de sala.

const ItemIcon := preload("res://scripts/item_icon.gd")

var panel: Panel
var room_label: Label
var obj_label: Label
var hp_box: Control
var strip: HBoxContainer
var toast_box: VBoxContainer
var banner: Label
var cur_room: int = 1


func _ready() -> void:
	layer = 5
	panel = Panel.new()
	panel.position = Vector2(0, 480)
	panel.size = Vector2(960, 60)
	panel.add_theme_stylebox_override("panel", Game.panel_style(Color(0.1, 0.7, 0.85), Color(0.02, 0.04, 0.09, 1.0), 2))
	add_child(panel)

	room_label = Label.new()
	room_label.position = Vector2(12, 6)
	room_label.add_theme_font_size_override("font_size", 13)
	room_label.add_theme_color_override("font_color", Game.COL_CYAN)
	panel.add_child(room_label)

	hp_box = Control.new()
	hp_box.position = Vector2(12, 28)
	hp_box.size = Vector2(190, 28)
	hp_box.draw.connect(_draw_hp)
	panel.add_child(hp_box)

	var tag := Label.new()
	tag.text = "OBJETIVO"
	tag.position = Vector2(222, 4)
	tag.add_theme_font_size_override("font_size", 10)
	tag.add_theme_color_override("font_color", Game.COL_YELLOW)
	panel.add_child(tag)

	obj_label = Label.new()
	obj_label.position = Vector2(222, 16)
	obj_label.size = Vector2(400, 40)
	obj_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	obj_label.add_theme_font_size_override("font_size", 12)
	panel.add_child(obj_label)

	strip = HBoxContainer.new()
	strip.position = Vector2(636, 6)
	strip.size = Vector2(316, 30)
	strip.add_theme_constant_override("separation", 2)
	panel.add_child(strip)


	toast_box = VBoxContainer.new()
	toast_box.position = Vector2(180, 10)
	toast_box.size = Vector2(600, 10)
	toast_box.alignment = BoxContainer.ALIGNMENT_BEGIN
	toast_box.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(toast_box)

	banner = Label.new()
	banner.position = Vector2(0, 150)
	banner.size = Vector2(960, 60)
	banner.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	banner.add_theme_font_size_override("font_size", 30)
	banner.add_theme_color_override("font_color", Game.COL_CYAN)
	banner.add_theme_color_override("font_outline_color", Color(0.02, 0.0, 0.1))
	banner.add_theme_constant_override("outline_size", 8)
	banner.modulate.a = 0.0
	add_child(banner)

	Game.hp_changed.connect(func(): hp_box.queue_redraw())
	Game.inventory_changed.connect(_rebuild_strip)
	Game.flags_changed.connect(refresh_objective)
	Game.inventory_changed.connect(refresh_objective)
	Game.toast_requested.connect(show_toast)
	_rebuild_strip()


func set_room(room_id: int) -> void:
	cur_room = room_id
	var r: Dictionary = Game.room(room_id)
	room_label.text = "%02d  %s" % [room_id, str(r["name"]).to_upper()]
	panel.add_theme_stylebox_override("panel", Game.panel_style(Color(str(r["accent"])), Color(0.02, 0.04, 0.09, 1.0), 2))
	refresh_objective()


func refresh_objective() -> void:
	if obj_label == null:
		return
	var o := Game.objective(cur_room)
	obj_label.text = o["text"]


func _draw_hp() -> void:
	var n: int = Game.MAX_HP
	for i in range(n):
		var x: float = 2.0 + float(i) * 58.0
		var on: bool = i < Game.hp
		var col := Game.COL_GREEN if on else Color(0.2, 0.25, 0.3)
		var rc := Rect2(x, 2, 52, 20)
		hp_box.draw_rect(rc, col.darkened(0.6), true)
		hp_box.draw_rect(rc, col, false, 2.0)
		if on:
			hp_box.draw_rect(Rect2(x + 4, 6, 44, 5), col.lightened(0.2), true)


func _rebuild_strip() -> void:
	if strip == null:
		return
	for c in strip.get_children():
		c.queue_free()
	var shown := 0
	for id in Game.ITEM_ORDER:
		var n := Game.count(id)
		if n <= 0:
			continue
		if shown >= 10:
			break
		var ic := ItemIcon.new()
		ic.setup(id, n, 30.0, false)
		strip.add_child(ic)
		shown += 1


func show_toast(text: String, color: Color) -> void:
	var l := Label.new()
	l.text = text
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	l.custom_minimum_size = Vector2(600, 0)
	l.add_theme_font_size_override("font_size", 14)
	l.add_theme_color_override("font_color", color)
	l.add_theme_color_override("font_outline_color", Color(0.01, 0.02, 0.06))
	l.add_theme_constant_override("outline_size", 6)
	toast_box.add_child(l)
	while toast_box.get_child_count() > 4:
		var old := toast_box.get_child(0)
		toast_box.remove_child(old)
		old.queue_free()
	var tw := l.create_tween()
	tw.tween_interval(2.6)
	tw.tween_property(l, "modulate:a", 0.0, 0.6)
	tw.tween_callback(l.queue_free)


func show_banner(text: String, color: Color) -> void:
	banner.text = text
	banner.add_theme_color_override("font_color", color)
	banner.modulate.a = 0.0
	var tw := create_tween()
	tw.tween_property(banner, "modulate:a", 1.0, 0.4)
	tw.tween_interval(1.6)
	tw.tween_property(banner, "modulate:a", 0.0, 0.8)
