extends CanvasLayer
## Caixa de diálogo com texto digitado, avanço por E/Enter/clique e escolhas (1, 2, ...).

signal advanced
signal chosen(index: int)

var active: bool = false
var panel: Panel
var name_label: Label
var text_label: Label
var hint_label: Label
var choice_box: VBoxContainer
var typing: bool = false
var tw: Tween
var waiting_choice: bool = false
var portrait: TextureRect


func _ready() -> void:
	layer = 20
	panel = Panel.new()
	panel.position = Vector2(40, 330)
	panel.size = Vector2(880, 140)
	panel.add_theme_stylebox_override("panel", Game.panel_style(Game.COL_CYAN, Color(0.02, 0.04, 0.1, 0.96), 2))
	panel.visible = false
	add_child(panel)

	name_label = Label.new()
	name_label.position = Vector2(16, 8)
	name_label.add_theme_font_size_override("font_size", 14)
	name_label.add_theme_color_override("font_color", Game.COL_YELLOW)
	panel.add_child(name_label)

	text_label = Label.new()
	text_label.position = Vector2(16, 32)
	text_label.size = Vector2(848, 76)
	text_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	text_label.add_theme_font_size_override("font_size", 16)
	panel.add_child(text_label)

	hint_label = Label.new()
	hint_label.text = "[E] continuar"
	hint_label.position = Vector2(750, 116)
	hint_label.add_theme_font_size_override("font_size", 11)
	hint_label.add_theme_color_override("font_color", Color(0.5, 0.7, 0.9))
	panel.add_child(hint_label)

	portrait = TextureRect.new()
	portrait.position = Vector2(12, 8)
	portrait.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	portrait.size = Vector2(120, 120)
	portrait.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	portrait.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	portrait.visible = false
	panel.add_child(portrait)

	choice_box = VBoxContainer.new()
	choice_box.position = Vector2(16, 70)
	choice_box.size = Vector2(848, 60)
	choice_box.visible = false
	panel.add_child(choice_box)


func _unhandled_input(ev: InputEvent) -> void:
	if not active:
		return
	if waiting_choice:
		if ev is InputEventKey and ev.pressed and not ev.echo:
			var idx: int = int(ev.keycode) - KEY_1
			if idx >= 0 and idx < choice_box.get_child_count():
				get_viewport().set_input_as_handled()
				chosen.emit(idx)
		return
	var go := ev.is_action_pressed("interact") or ev.is_action_pressed("ui_accept")
	if ev is InputEventMouseButton and ev.pressed and ev.button_index == MOUSE_BUTTON_LEFT:
		go = true
	if go:
		get_viewport().set_input_as_handled()
		_advance()


func _advance() -> void:
	if typing:
		if tw:
			tw.kill()
		text_label.visible_ratio = 1.0
		typing = false
	else:
		advanced.emit()


## Mostra as falas em sequência. Se houver escolhas, devolve o índice escolhido (senão -1).
func say(speaker: String, lines: Array, choices: Array = []) -> int:
	active = true
	panel.visible = true
	choice_box.visible = false
	hint_label.visible = true
	name_label.text = speaker
	var who := ""
	if speaker.contains("Voss"):
		who = "voss"
	elif speaker.contains("Okoye"):
		who = "okoye"
	var px: float = 134.0 if who != "" else 16.0
	portrait.visible = who != ""
	name_label.position.x = px
	text_label.position.x = px
	text_label.size.x = 864.0 - px
	choice_box.position.x = px
	choice_box.size.x = 864.0 - px
	for l in lines:
		if who != "":
			var ex := "calm"
			var ls := str(l)
			if who == "voss":
				if ls.contains("!") or ls.contains("Cuidado"):
					ex = "angry"
				elif ls.contains("orgulho"):
					ex = "smile"
				elif ls.contains("Sinto") or ls.contains("Desculpe"):
					ex = "worried"
			else:
				if ls.contains("!"):
					ex = "worried"
				elif ls.contains("Boa sorte"):
					ex = "smile"
			portrait.texture = Game.tex("res://assets/cut/%s_%s.png" % [who, ex])
		text_label.text = str(l)
		text_label.visible_ratio = 0.0
		typing = true
		tw = create_tween()
		tw.tween_property(text_label, "visible_ratio", 1.0, maxf(0.25, str(l).length() * 0.016))
		tw.finished.connect(func(): typing = false)
		await advanced
	var result := -1
	if choices.size() > 0:
		hint_label.visible = false
		for c in choice_box.get_children():
			c.queue_free()
		for i in range(choices.size()):
			var b := Button.new()
			b.text = "%d.  %s" % [i + 1, str(choices[i])]
			b.alignment = HORIZONTAL_ALIGNMENT_LEFT
			b.focus_mode = Control.FOCUS_NONE
			b.add_theme_font_size_override("font_size", 14)
			Game.style_button(b)
			var idx := i
			b.pressed.connect(func(): chosen.emit(idx))
			choice_box.add_child(b)
		text_label.size.y = 40.0
		choice_box.visible = true
		waiting_choice = true
		result = await chosen
		waiting_choice = false
		choice_box.visible = false
		text_label.size.y = 76.0
	panel.visible = false
	active = false
	Game.lock_input(0.2)
	return result
