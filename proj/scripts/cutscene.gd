extends CanvasLayer
## Cena de abertura: a página em quadrinhos, mostrada quadro a quadro (câmera de cinema).
## Enter/Espaço/clique avança; Esc pula.

signal finished

const PAGE := "res://assets/cut/comic_page.png"
# regiões da página (em pixels da imagem) mostradas em sequência
const VIEWS := [
	Rect2(0, 0, 740, 520),        # laboratório secreto da Orion Biotech
	Rect2(765, 15, 335, 505),     # "Um único passo..."
	Rect2(1105, 15, 431, 505),    # "...e a modificação começa."
	Rect2(0, 535, 795, 480),      # "O processo está em andamento..."
	Rect2(800, 535, 395, 480),    # "...a nova forma de vida surge."
	Rect2(1200, 535, 336, 480),   # "Perfeito."
]

var idx: int = -1
var pt: float = 0.0
var running: bool = false
var busy: bool = false
var canvas: Control
var page: Texture2D
var black: ColorRect
var hint: Label


func _ready() -> void:
	layer = 40
	visible = false
	page = load(PAGE)
	canvas = Control.new()
	canvas.set_anchors_preset(Control.PRESET_FULL_RECT)
	canvas.mouse_filter = Control.MOUSE_FILTER_STOP
	canvas.draw.connect(_draw_scene)
	add_child(canvas)
	hint = Label.new()
	hint.text = "[Enter] avançar     [Esc] pular"
	hint.position = Vector2(640, 516)
	hint.add_theme_font_size_override("font_size", 12)
	hint.add_theme_color_override("font_color", Color(0.6, 0.75, 0.9))
	canvas.add_child(hint)
	black = ColorRect.new()
	black.color = Color(0, 0, 0, 0)
	black.set_anchors_preset(Control.PRESET_FULL_RECT)
	black.mouse_filter = Control.MOUSE_FILTER_IGNORE
	canvas.add_child(black)


func play() -> void:
	visible = true
	running = true
	idx = -1
	busy = false
	await _next()


func _next() -> void:
	if busy:
		return
	busy = true
	var tw := create_tween()
	tw.tween_property(black, "color:a", 1.0, 0.18)
	await tw.finished
	idx += 1
	if idx >= VIEWS.size():
		running = false
		visible = false
		black.color.a = 0.0
		busy = false
		finished.emit()
		return
	pt = 0.0
	var tw2 := create_tween()
	tw2.tween_property(black, "color:a", 0.0, 0.25)
	await tw2.finished
	busy = false


func _process(delta: float) -> void:
	if not running:
		return
	pt += delta
	canvas.queue_redraw()


func _input(ev: InputEvent) -> void:
	if not running or not visible:
		return
	if ev is InputEventKey and ev.pressed and not ev.echo:
		get_viewport().set_input_as_handled()
		if ev.keycode == KEY_ESCAPE:
			idx = VIEWS.size() - 1
			busy = false
			_next()
		elif ev.keycode in [KEY_ENTER, KEY_KP_ENTER, KEY_SPACE, KEY_E]:
			_advance()
	elif ev is InputEventMouseButton and ev.pressed and ev.button_index == MOUSE_BUTTON_LEFT:
		get_viewport().set_input_as_handled()
		_advance()


func _advance() -> void:
	if busy or not running:
		return
	_next()


func _draw_scene() -> void:
	canvas.draw_rect(Rect2(0, 0, 960, 540), Color(0.01, 0.01, 0.03))
	if idx < 0 or idx >= VIEWS.size() or page == null:
		return
	var v: Rect2 = VIEWS[idx]
	# aproximação lenta (6%) durante o quadro
	var z: float = 1.0 - minf(pt * 0.012, 0.06)
	var c: Vector2 = v.get_center()
	var src := Rect2(c - v.size * z * 0.5, v.size * z)
	var avail := Vector2(932, 484)
	var sc: float = minf(avail.x / v.size.x, avail.y / v.size.y)
	var dsz: Vector2 = v.size * sc
	var dst := Rect2((Vector2(960, 520) - dsz) * 0.5 + Vector2(0, 2), dsz)
	canvas.draw_texture_rect_region(page, dst, src)
	canvas.draw_rect(dst, Color(0.99, 0.93, 0.04), false, 3.0)
	canvas.draw_string(ThemeDB.fallback_font, Vector2(20, 524), "PROJETO R-31  //  %d / %d" % [idx + 1, VIEWS.size()], HORIZONTAL_ALIGNMENT_LEFT, -1, 12, Color(0.99, 0.93, 0.04))
