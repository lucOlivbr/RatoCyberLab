extends CanvasLayer
## Telas de título, pausa, "recapturado" e final.

signal new_game
signal continue_game
signal resume
signal to_title
signal auth_done

var title_root: Control
var pause_root: Control
var end_root: Control
var caught_root: Control
var continue_btn: Button
var end_label: Label
var end_ready: bool = false
var t: float = 0.0
var title_label: Label
var title_rat: TextureRect
var title_bar: ColorRect
var auth_root: Control
var auth_title: Label
var auth_sub: Label
var auth_nome: LineEdit
var auth_email: LineEdit
var auth_senha: LineEdit
var auth_labels: Array = []
var auth_status: Label
var auth_primary: Button
var auth_toggle: Button
var auth_register: bool = false
var auth_busy: bool = false
var acct_label: Label
var acct_btn: Button
var report_btn: Button
var pause_summary: Label


func _ready() -> void:
	layer = 30
	_build_title()
	_build_pause()
	_build_end()
	_build_caught()
	_build_auth()
	hide_all()


func hide_all() -> void:
	title_root.visible = false
	pause_root.visible = false
	end_root.visible = false
	caught_root.visible = false
	auth_root.visible = false


func _btn(parent: Control, text: String, pos: Vector2, sz: Vector2, cb: Callable) -> Button:
	var b := Button.new()
	b.text = text
	b.position = pos
	b.size = sz
	b.focus_mode = Control.FOCUS_NONE
	b.add_theme_font_size_override("font_size", 18)
	Game.style_button(b)
	b.pressed.connect(cb)
	parent.add_child(b)
	return b


func _build_title() -> void:
	title_root = Control.new()
	title_root.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(title_root)
	var bg := TextureRect.new()
	bg.texture = Game.tex("res://assets/ui/title_bg.png")
	bg.set_anchors_preset(Control.PRESET_FULL_RECT)
	bg.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	bg.stretch_mode = TextureRect.STRETCH_SCALE
	bg.modulate = Color(0.8, 0.82, 0.95)
	title_root.add_child(bg)
	# véu escuro à esquerda para destacar o logo e o menu
	var veil := ColorRect.new()
	veil.color = Color(0.01, 0.01, 0.04, 0.62)
	veil.position = Vector2(0, 0)
	veil.size = Vector2(560, 540)
	title_root.add_child(veil)
	var edge := ColorRect.new()
	edge.color = Color(0.99, 0.93, 0.04, 0.9)
	edge.position = Vector2(558, 0)
	edge.size = Vector2(3, 540)
	title_root.add_child(edge)
	# rato grande em pé, à direita
	title_rat = TextureRect.new()
	title_rat.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	title_rat.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	title_rat.texture = Game.tex("res://assets/ui/menu_rat.png")
	title_rat.custom_minimum_size = Vector2(324, 528)
	title_rat.position = Vector2(620, 14)
	title_rat.size = Vector2(324, 528)
	title_root.add_child(title_rat)
	# logo PROJETO R-31
	var logo := TextureRect.new()
	logo.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	logo.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT
	logo.texture = Game.tex("res://assets/ui/title_logo.png")
	logo.custom_minimum_size = Vector2(520, 300)
	logo.position = Vector2(14, 4)
	logo.size = Vector2(520, 300)
	title_root.add_child(logo)
	title_label = Label.new()  # mantido só para o brilho animado da faixa
	title_label.visible = false
	title_root.add_child(title_label)
	title_bar = ColorRect.new()
	title_bar.color = Color(1.0, 0.15, 0.25)
	title_bar.position = Vector2(60, 316)
	title_bar.size = Vector2(300, 3)
	title_root.add_child(title_bar)
	_title_btn(title_root, "NOVO JOGO", Vector2(60, 332), func(): new_game.emit())
	continue_btn = _title_btn(title_root, "CONTINUAR", Vector2(60, 394), func(): continue_game.emit())
	_title_btn(title_root, "SAIR", Vector2(60, 456), func(): get_tree().quit())
	acct_label = Label.new()
	acct_label.position = Vector2(62, 512)
	acct_label.size = Vector2(250, 24)
	acct_label.add_theme_font_size_override("font_size", 14)
	acct_label.add_theme_color_override("font_color", Color(0.7, 0.82, 0.95))
	title_root.add_child(acct_label)
	acct_btn = Button.new()
	acct_btn.position = Vector2(318, 510)
	acct_btn.size = Vector2(150, 26)
	acct_btn.focus_mode = Control.FOCUS_NONE
	acct_btn.add_theme_font_size_override("font_size", 13)
	Game.style_button(acct_btn)
	acct_btn.pressed.connect(_on_account_pressed)
	title_root.add_child(acct_btn)


func _title_btn(parent: Control, text: String, pos: Vector2, cb: Callable) -> Button:
	var b := Button.new()
	b.text = "  " + text
	b.alignment = HORIZONTAL_ALIGNMENT_LEFT
	b.position = pos
	b.size = Vector2(300, 50)
	b.focus_mode = Control.FOCUS_NONE
	b.add_theme_font_size_override("font_size", 22)
	b.add_theme_color_override("font_color", Color(0.99, 0.93, 0.04))
	b.add_theme_color_override("font_hover_color", Color.WHITE)
	b.add_theme_color_override("font_disabled_color", Color(0.4, 0.4, 0.45))
	var normal := Game.panel_style(Color(0.99, 0.93, 0.04, 0.55), Color(0.03, 0.03, 0.08, 0.85), 2)
	var hover := Game.panel_style(Color(1.0, 0.15, 0.25), Color(0.25, 0.04, 0.08, 0.95), 3)
	b.add_theme_stylebox_override("normal", normal)
	b.add_theme_stylebox_override("hover", hover)
	b.add_theme_stylebox_override("pressed", hover)
	b.add_theme_stylebox_override("disabled", Game.panel_style(Color(0.3, 0.3, 0.35, 0.5), Color(0.03, 0.03, 0.06, 0.7), 1))
	b.pressed.connect(cb)
	parent.add_child(b)
	return b


func show_title() -> void:
	hide_all()
	continue_btn.disabled = not Game.has_save()
	refresh_account()
	title_root.visible = true


func refresh_account() -> void:
	if Api.logged_in():
		acct_label.text = "Jogador: " + Api.player_name()
		acct_btn.text = "TROCAR CONTA"
	else:
		acct_label.text = "Modo convidado (sem relatório)"
		acct_btn.text = "ENTRAR"


func _on_account_pressed() -> void:
	if Api.logged_in():
		await Api.logout()
	show_auth()


func _build_pause() -> void:
	pause_root = Control.new()
	pause_root.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(pause_root)
	var dim := ColorRect.new()
	dim.color = Color(0.01, 0.02, 0.06, 0.82)
	dim.set_anchors_preset(Control.PRESET_FULL_RECT)
	pause_root.add_child(dim)
	var l := Label.new()
	l.text = "PAUSADO"
	l.position = Vector2(0, 150)
	l.size = Vector2(960, 50)
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	l.add_theme_font_size_override("font_size", 40)
	l.add_theme_color_override("font_color", Game.COL_CYAN)
	pause_root.add_child(l)
	_btn(pause_root, "CONTINUAR", Vector2(350, 212), Vector2(260, 44), func(): resume.emit())
	report_btn = _btn(pause_root, "RELATÓRIO DE ERROS (NAVEGADOR)", Vector2(330, 264), Vector2(300, 44), func(): Api.open_report())
	_btn(pause_root, "SALVAR E VOLTAR AO TÍTULO", Vector2(350, 316), Vector2(260, 44), func(): to_title.emit())
	pause_summary = Label.new()
	pause_summary.position = Vector2(60, 368)
	pause_summary.size = Vector2(840, 24)
	pause_summary.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	pause_summary.add_theme_font_size_override("font_size", 14)
	pause_summary.add_theme_color_override("font_color", Game.COL_YELLOW)
	pause_root.add_child(pause_summary)
	var ctrl := Label.new()
	ctrl.text = "CONTROLES\nWASD / setas: mover      Shift: correr\nE: interagir      C: bancada      I: inventário\nF: usar gel      H: dica      R: reiniciar caixas      Esc: pausa"
	ctrl.position = Vector2(0, 414)
	ctrl.size = Vector2(960, 100)
	ctrl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	ctrl.add_theme_font_size_override("font_size", 14)
	ctrl.add_theme_color_override("font_color", Color(0.7, 0.82, 0.95))
	pause_root.add_child(ctrl)


func show_pause() -> void:
	pause_root.visible = true
	_refresh_pause_summary()


func _refresh_pause_summary() -> void:
	if not Api.logged_in():
		report_btn.disabled = true
		pause_summary.text = "Modo convidado: entre com uma conta para registrar e ver seus erros."
		return
	report_btn.disabled = false
	pause_summary.text = "Carregando seus erros..."
	var sm: Dictionary = await Api.fetch_summary()
	if not pause_root.visible:
		return
	if sm.is_empty():
		pause_summary.text = "Sem conexão com o servidor: seus erros serão enviados quando ele voltar."
	else:
		pause_summary.text = "Seus erros: %d no total  |  %d fórmulas  |  %d receitas  |  %d danos  |  %d recapturas" % [
			int(sm["total"]), int(sm.get("FORMULA_ERRADA", 0)), int(sm.get("RECEITA_INVALIDA", 0)),
			int(sm.get("DANO", 0)), int(sm.get("MORTE", 0))]


func _build_caught() -> void:
	caught_root = Control.new()
	caught_root.set_anchors_preset(Control.PRESET_FULL_RECT)
	caught_root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(caught_root)
	var dim := ColorRect.new()
	dim.color = Color(0.3, 0.0, 0.05, 0.85)
	dim.set_anchors_preset(Control.PRESET_FULL_RECT)
	dim.mouse_filter = Control.MOUSE_FILTER_IGNORE
	caught_root.add_child(dim)
	var l := Label.new()
	l.text = "RECAPTURADO"
	l.position = Vector2(0, 210)
	l.size = Vector2(960, 60)
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	l.add_theme_font_size_override("font_size", 44)
	l.add_theme_color_override("font_color", Game.COL_RED)
	caught_root.add_child(l)
	var s := Label.new()
	s.text = "Os guardas te levaram de volta ao início da sala. Seus materiais foram mantidos."
	s.position = Vector2(0, 275)
	s.size = Vector2(960, 30)
	s.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	s.add_theme_font_size_override("font_size", 15)
	caught_root.add_child(s)


# ------------------------------------------------------------------ cadastro / login
func _auth_label(parent: Control, text: String) -> Label:
	var l := Label.new()
	l.text = text
	l.size = Vector2(360, 18)
	l.add_theme_font_size_override("font_size", 12)
	l.add_theme_color_override("font_color", Color(0.6, 0.75, 0.9))
	parent.add_child(l)
	auth_labels.append(l)
	return l


func _auth_field(parent: Control, placeholder: String, secret: bool, max_len: int) -> LineEdit:
	var e := LineEdit.new()
	e.size = Vector2(360, 34)
	e.placeholder_text = placeholder
	e.secret = secret
	e.max_length = max_len
	e.add_theme_font_size_override("font_size", 16)
	e.add_theme_stylebox_override("normal", Game.panel_style(Game.COL_CYAN.darkened(0.3), Color(0.02, 0.04, 0.09, 1.0), 1))
	e.add_theme_stylebox_override("focus", Game.panel_style(Game.COL_YELLOW, Color(0.04, 0.08, 0.14, 1.0), 2))
	e.text_submitted.connect(func(_t): _auth_submit())
	parent.add_child(e)
	return e


func _build_auth() -> void:
	auth_root = Control.new()
	auth_root.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(auth_root)
	var dim := ColorRect.new()
	dim.color = Color(0.01, 0.02, 0.06, 0.92)
	dim.set_anchors_preset(Control.PRESET_FULL_RECT)
	auth_root.add_child(dim)
	var panel := Panel.new()
	panel.position = Vector2(280, 30)
	panel.size = Vector2(400, 476)
	panel.add_theme_stylebox_override("panel", Game.panel_style(Game.COL_CYAN, Color(0.03, 0.05, 0.1, 0.98), 2))
	auth_root.add_child(panel)
	auth_title = Label.new()
	auth_title.position = Vector2(0, 14)
	auth_title.size = Vector2(400, 40)
	auth_title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	auth_title.add_theme_font_size_override("font_size", 28)
	auth_title.add_theme_color_override("font_color", Game.COL_CYAN)
	panel.add_child(auth_title)
	auth_sub = Label.new()
	auth_sub.position = Vector2(20, 54)
	auth_sub.size = Vector2(360, 34)
	auth_sub.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	auth_sub.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	auth_sub.add_theme_font_size_override("font_size", 12)
	auth_sub.add_theme_color_override("font_color", Color(0.7, 0.82, 0.95))
	auth_sub.text = "Sua conta guarda o progresso no banco de dados e monta o relatório dos seus erros."
	panel.add_child(auth_sub)
	_auth_label(panel, "NOME DE JOGADOR")
	auth_nome = _auth_field(panel, "ex.: Maria", false, 60)
	_auth_label(panel, "E-MAIL")
	auth_email = _auth_field(panel, "voce@email.com", false, 120)
	_auth_label(panel, "SENHA (MÍNIMO 6 CARACTERES)")
	auth_senha = _auth_field(panel, "senha", true, 100)
	auth_status = Label.new()
	auth_status.position = Vector2(20, 276)
	auth_status.size = Vector2(360, 40)
	auth_status.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	auth_status.add_theme_font_size_override("font_size", 13)
	panel.add_child(auth_status)
	auth_primary = _btn(panel, "", Vector2(20, 322), Vector2(360, 44), func(): _auth_submit())
	auth_toggle = _btn(panel, "", Vector2(20, 370), Vector2(360, 34), func(): _set_auth_mode(not auth_register))
	_btn(panel, "JOGAR SEM CONTA (OFFLINE)", Vector2(20, 422), Vector2(360, 34), func(): _auth_guest())


## Reposiciona os campos conforme o modo: login (2 campos) ou cadastro (3 campos).
func _set_auth_mode(register: bool) -> void:
	auth_register = register
	auth_title.text = "CRIAR CONTA" if register else "ENTRAR"
	auth_primary.text = "CADASTRAR" if register else "ENTRAR"
	auth_toggle.text = "Já tenho conta: ENTRAR" if register else "Não tenho conta: CADASTRAR"
	var rows: Array = [auth_nome, auth_email, auth_senha] if register else [auth_email, auth_senha]
	var lbls: Array = [auth_labels[0], auth_labels[1], auth_labels[2]] if register else [auth_labels[1], auth_labels[2]]
	auth_nome.visible = register
	auth_labels[0].visible = register
	var y := 98.0
	for i in range(rows.size()):
		(lbls[i] as Label).position = Vector2(20, y)
		(rows[i] as LineEdit).position = Vector2(20, y + 18.0)
		y += 62.0
	auth_status.position = Vector2(20, y + 2.0)
	_auth_msg("", false)


func _auth_msg(text: String, bad: bool) -> void:
	auth_status.text = text
	auth_status.add_theme_color_override("font_color", Game.COL_RED if bad else Game.COL_YELLOW)


func show_auth(msg: String = "") -> void:
	auth_root.visible = true
	auth_busy = false
	auth_senha.text = ""
	_set_auth_mode(false)
	if msg != "":
		_auth_msg(msg, true)
	auth_email.grab_focus()


func _auth_submit() -> void:
	if auth_busy:
		return
	var nome := auth_nome.text.strip_edges()
	var email := auth_email.text.strip_edges()
	var senha := auth_senha.text
	if auth_register and nome.length() < 2:
		_auth_msg("Informe seu nome (mínimo 2 letras).", true)
		return
	if email == "" or senha == "":
		_auth_msg("Preencha e-mail e senha.", true)
		return
	auth_busy = true
	_auth_msg("Conectando ao servidor...", false)
	var err: String
	if auth_register:
		err = await Api.register(nome, email, senha)
	else:
		err = await Api.login(email, senha)
	auth_busy = false
	if err != "":
		_auth_msg(err, true)
		return
	auth_senha.text = ""
	auth_root.visible = false
	auth_done.emit()


func _auth_guest() -> void:
	Api.play_as_guest()
	auth_root.visible = false
	auth_done.emit()


func show_caught(on: bool) -> void:
	caught_root.visible = on


var end_bg: TextureRect
var end_logo: TextureRect
var end_t: float = 0.0


func _build_end() -> void:
	end_root = Control.new()
	end_root.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(end_root)
	end_bg = TextureRect.new()
	end_bg.texture = Game.tex("res://assets/ui/end_scene.png")
	end_bg.position = Vector2.ZERO
	end_bg.size = Vector2(960, 540)
	end_bg.pivot_offset = Vector2(560, 380)
	end_bg.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	end_bg.stretch_mode = TextureRect.STRETCH_SCALE
	end_bg.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	end_root.add_child(end_bg)
	end_logo = TextureRect.new()
	end_logo.texture = Game.tex("res://assets/ui/liberdade_logo.png")
	end_logo.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	end_logo.size = Vector2(740, 164)
	end_logo.position = Vector2(110, 6)
	end_logo.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	end_logo.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
	end_root.add_child(end_logo)
	var panel := Panel.new()
	panel.position = Vector2(24, 262)
	panel.size = Vector2(520, 262)
	panel.add_theme_stylebox_override("panel", Game.panel_style(Game.COL_YELLOW, Color(0.02, 0.03, 0.08, 0.82), 2))
	end_root.add_child(panel)
	end_label = Label.new()
	end_label.position = Vector2(16, 12)
	end_label.size = Vector2(488, 216)
	end_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	end_label.add_theme_font_size_override("font_size", 14)
	panel.add_child(end_label)
	var k := Label.new()
	k.text = "FIM   //   [E] voltar ao título"
	k.position = Vector2(16, 234)
	k.add_theme_font_size_override("font_size", 12)
	k.add_theme_color_override("font_color", Game.COL_YELLOW)
	panel.add_child(k)


func show_end(text: String) -> void:
	end_label.text = text
	end_ready = false
	end_t = 0.0
	end_root.modulate.a = 0.0
	end_root.visible = true
	var tw := create_tween()
	tw.tween_property(end_root, "modulate:a", 1.0, 1.4)
	tw.tween_callback(func(): end_ready = true)


func _unhandled_input(ev: InputEvent) -> void:
	if end_root.visible and end_ready and (ev.is_action_pressed("interact") or ev.is_action_pressed("ui_accept")):
		get_viewport().set_input_as_handled()
		end_root.visible = false
		to_title.emit()
	elif pause_root.visible and ev.is_action_pressed("pause"):
		get_viewport().set_input_as_handled()
		resume.emit()


func _process(delta: float) -> void:
	if end_root.visible:
		end_t += delta
		var z: float = 1.0 + minf(end_t, 30.0) * 0.002
		end_bg.scale = Vector2(z, z)
		end_logo.modulate = Color(1, 1, 1, 0.9 + 0.1 * sin(end_t * 3.0))
		end_logo.position.y = 6.0 + sin(end_t * 1.6) * 3.0
	if title_root.visible:
		t += delta
		if title_rat != null:
			title_rat.position.y = 14.0   # rato parado
		if title_bar != null:
			var k := 0.5 + 0.5 * sin(t * 3.0)
			title_bar.color = Color(1.0, 0.15, 0.25).lerp(Color(0.99, 0.93, 0.04), k)
