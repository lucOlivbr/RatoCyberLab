extends Control
## Ícone de item reutilizável (inventário, bancada, HUD).

signal clicked(item_id: String, button: int)

var item_id: String = ""
var amount: int = 0
var show_count: bool = true
var dim: bool = false
var selectable: bool = false
var show_bg: bool = true
var icon_scale: float = 0.62
var draggable: bool = false


func setup(id: String, n: int, sz: float = 44.0, selectable_: bool = false) -> void:
	item_id = id
	amount = n
	selectable = selectable_
	custom_minimum_size = Vector2(sz, sz)
	size = Vector2(sz, sz)
	if Game.ITEMS.has(id):
		tooltip_text = "%s\n%s" % [Game.item_name(id), str(Game.ITEMS[id]["desc"])]
	mouse_filter = Control.MOUSE_FILTER_STOP if selectable_ else Control.MOUSE_FILTER_IGNORE
	queue_redraw()


func _process(_d: float) -> void:
	if Game.ITEMS.has(item_id) and int(Game.ITEMS[item_id].get("frames", 0)) > 0 and is_visible_in_tree():
		queue_redraw()


func _draw() -> void:
	var sz: float = minf(size.x, size.y)
	if selectable and show_bg:
		draw_rect(Rect2(Vector2.ZERO, size), Color(0.05, 0.09, 0.16, 0.9), true)
		draw_rect(Rect2(Vector2.ZERO, size), Color(0.1, 0.55, 0.7, 0.8), false, 1.0)
	Game.draw_icon(self, item_id, size / 2.0 - Vector2(0, 2), sz * icon_scale, dim)
	if show_count and amount > 0:
		var font := ThemeDB.fallback_font
		var txt := "x%d" % amount
		var fs: int = 11
		var w: float = font.get_string_size(txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
		draw_string(font, Vector2(size.x - w - 3, size.y - 3), txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Color(1, 1, 0.7))


func _gui_input(ev: InputEvent) -> void:
	if not selectable:
		return
	if ev is InputEventMouseButton:
		if ev.button_index == MOUSE_BUTTON_LEFT:
			# clique simples = soltar o botão sem arrastar (arrastar não passa por aqui)
			if not ev.pressed:
				clicked.emit(item_id, ev.button_index)
				accept_event()
		elif ev.pressed:
			clicked.emit(item_id, ev.button_index)
			accept_event()


func _get_drag_data(_pos: Vector2):
	if not draggable or item_id == "":
		return null
	var prev := Control.new()
	var ic = get_script().new()
	ic.setup(item_id, 0, 44.0, false)
	ic.show_count = false
	ic.position = Vector2(-22, -22)
	prev.add_child(ic)
	set_drag_preview(prev)
	return {"item": item_id}
