extends Control
## Recipiente da bancada: recebe itens arrastados do inventário (um tipo por recipiente).

signal dropped(vessel_index: int, item_id: String)
signal removed(vessel_index: int)

const MAX_N := 5

var index: int = 0
var item_id: String = ""
var amount: int = 0
var lit: bool = false
var t: float = 0.0
var hover: bool = false
var shake: float = 0.0


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_STOP
	custom_minimum_size = Vector2(60, 104)
	size = Vector2(60, 104)
	mouse_entered.connect(func(): hover = true; queue_redraw())
	mouse_exited.connect(func(): hover = false; queue_redraw())


func _process(delta: float) -> void:
	t += delta
	shake = maxf(0.0, shake - delta)
	if amount > 0 or hover or shake > 0.0:
		queue_redraw()


func _can_drop_data(_pos: Vector2, data) -> bool:
	return typeof(data) == TYPE_DICTIONARY and data.has("item")


func _drop_data(_pos: Vector2, data) -> void:
	dropped.emit(index, str(data["item"]))


func _gui_input(ev: InputEvent) -> void:
	if ev is InputEventMouseButton and ev.pressed and amount > 0:
		removed.emit(index)
		accept_event()


func liquid_color() -> Color:
	if item_id == "" or not Game.ITEMS.has(item_id):
		return Color(0, 0, 0, 0)
	return Color(str(Game.ITEMS[item_id]["col"]))


func _draw() -> void:
	var w := size.x
	var h := size.y
	var ox := sin(t * 60.0) * 2.0 if shake > 0.0 else 0.0
	var body := Rect2(Vector2(6 + ox, 18), Vector2(w - 12, h - 24))
	var edge := Color(0.55, 0.85, 1.0, 0.95) if hover else Color(0.4, 0.7, 0.85, 0.85)
	# vidro
	draw_rect(body, Color(0.12, 0.22, 0.34, 0.55), true)
	# líquido
	if amount > 0:
		var col := liquid_color()
		var lvl: float = clampf(float(amount) / float(MAX_N), 0.2, 1.0)
		var lh: float = (body.size.y - 6.0) * (0.35 + 0.55 * lvl)
		var lrect := Rect2(body.position + Vector2(2, body.size.y - lh - 2), Vector2(body.size.x - 4, lh))
		draw_rect(lrect, Color(col.r, col.g, col.b, 0.55), true)
		draw_rect(Rect2(lrect.position, Vector2(lrect.size.x, 3)), col.lightened(0.35), true)
		# bolhas
		for i in range(4):
			var bt: float = fmod(t * 0.6 + float(i) * 0.27, 1.0)
			var bx: float = lrect.position.x + 8.0 + float(i) * (lrect.size.x - 16.0) / 3.0 + sin(t * 3.0 + float(i)) * 2.0
			var by: float = lrect.position.y + lrect.size.y - bt * lrect.size.y
			draw_circle(Vector2(bx, by), 1.6, col.lightened(0.5))
		# aquecimento
		if lit:
			draw_rect(Rect2(body.position + Vector2(0, body.size.y - 6), Vector2(body.size.x, 6)), Color(1.0, 0.55, 0.15, 0.55 + 0.25 * sin(t * 12.0)), true)
		# ícone do item
		Game.draw_icon(self, item_id, Vector2(w / 2.0 + ox, body.position.y + body.size.y * 0.42), 30.0)
		var font := ThemeDB.fallback_font
		var txt := "x%d" % amount
		draw_string(font, Vector2(w / 2.0 - 8 + ox, body.position.y + body.size.y - 8), txt, HORIZONTAL_ALIGNMENT_LEFT, -1, 12, Color(1, 1, 0.8))
	# contorno e boca do frasco
	draw_rect(body, edge, false, 2.0)
	draw_rect(Rect2(Vector2(3 + ox, 14), Vector2(w - 6, 5)), edge, true)
	draw_line(Vector2(10 + ox, 28), Vector2(10 + ox, h - 16), Color(1, 1, 1, 0.25), 2.0)
	# rótulo
	var f2 := ThemeDB.fallback_font
	var lab := "RECIP. %d" % (index + 1)
	draw_string(f2, Vector2(8, 11), lab, HORIZONTAL_ALIGNMENT_LEFT, -1, 9, Color(0.6, 0.78, 0.95))
	if hover and amount > 0:
		draw_string(f2, Vector2(2, h + 10), "clique: remover", HORIZONTAL_ALIGNMENT_LEFT, -1, 9, Color(0.9, 0.9, 0.6))
