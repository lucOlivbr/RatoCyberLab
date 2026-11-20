extends Node
## Cena principal: liga título, mundo, HUD, diálogo, bancada, inventário e final.

const WorldScript := preload("res://scripts/world.gd")
const HudScript := preload("res://scripts/hud.gd")
const DialogueScript := preload("res://scripts/dialogue.gd")
const CraftScript := preload("res://scripts/craft_ui.gd")
const InvScript := preload("res://scripts/inventory_ui.gd")
const MenusScript := preload("res://scripts/menus.gd")
const FormulaScript := preload("res://scripts/formula_ui.gd")
const CutsceneScript := preload("res://scripts/cutscene.gd")

const BOSS_REPLIES := [
	["Dr. Voss: Encerrar? Vinte anos da minha vida cabem nesse 'encerrar'?", "Dr. Voss: Sinto muito, pequeno. Eu não posso deixar. Mostre se consegue desviar disto!"],
	["Dr. Voss: Chame como quiser. Para mim, cada rato é uma pergunta que ainda não consegui responder.", "Dr. Voss: Mas não vou deixar você destruir tudo. Desculpe, R-31... Cuidado!"],
]

var holder: Node2D
var world
var hud
var dlg
var craft
var invui
var menus
var puzzle
var puzzle_cb: Callable
var count_layer: CanvasLayer
var count_label: Label
var count_flash: ColorRect
var count_red: ColorRect
var cut
var skip_cutscene: bool = false
var fade: ColorRect
var state: String = "title"
var paused: bool = false
var transitioning: bool = false
var dying: bool = false
var ending_started: bool = false
var ending_triggered: bool = false


const MUSIC_BY_ROOM := {0: "lab", 1: "lab", 2: "lab", 3: "energia", 4: "mutacao", 5: "mutacao", 6: "seguranca", 7: "seguranca", 8: "mutacao", 9: "seguranca", 10: "chefe"}
var music_player: AudioStreamPlayer
var music_name: String = ""
var music_cache: Dictionary = {}


func play_music(nm: String) -> void:
	if nm == music_name and music_player != null and music_player.playing:
		return
	if music_player == null:
		music_player = AudioStreamPlayer.new()
		music_player.volume_db = -9.0
		add_child(music_player)
	if not music_cache.has(nm):
		var st = load("res://assets/music/%s.ogg" % nm)
		if st != null and "loop" in st:
			st.loop = true
		music_cache[nm] = st
	music_name = nm
	music_player.stream = music_cache[nm]
	if music_player.stream != null:
		music_player.play()


func _ready() -> void:
	holder = Node2D.new()
	add_child(holder)
	hud = HudScript.new()
	add_child(hud)
	invui = InvScript.new()
	add_child(invui)
	craft = CraftScript.new()
	add_child(craft)
	puzzle = FormulaScript.new()
	add_child(puzzle)
	puzzle.solved.connect(_on_puzzle_solved)
	dlg = DialogueScript.new()
	add_child(dlg)
	menus = MenusScript.new()
	add_child(menus)
	cut = CutsceneScript.new()
	add_child(cut)
	count_layer = CanvasLayer.new()
	count_layer.layer = 45
	count_layer.visible = false
	add_child(count_layer)
	count_red = ColorRect.new()
	count_red.color = Color(1.0, 0.05, 0.1, 0.0)
	count_red.set_anchors_preset(Control.PRESET_FULL_RECT)
	count_red.mouse_filter = Control.MOUSE_FILTER_IGNORE
	count_layer.add_child(count_red)
	count_label = Label.new()
	count_label.position = Vector2(0, 150)
	count_label.size = Vector2(960, 200)
	count_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	count_label.add_theme_font_size_override("font_size", 150)
	count_label.add_theme_color_override("font_color", Color(1.0, 0.85, 0.1))
	count_label.add_theme_color_override("font_outline_color", Color(0.5, 0.0, 0.05))
	count_label.add_theme_constant_override("outline_size", 12)
	count_layer.add_child(count_label)
	var cap := Label.new()
	cap.text = "SOBRECARGA DO NÚCLEO CENTRAL"
	cap.position = Vector2(0, 110)
	cap.size = Vector2(960, 30)
	cap.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	cap.add_theme_font_size_override("font_size", 22)
	cap.add_theme_color_override("font_color", Color(1.0, 0.3, 0.35))
	count_layer.add_child(cap)
	count_flash = ColorRect.new()
	count_flash.color = Color(1, 1, 1, 0.0)
	count_flash.set_anchors_preset(Control.PRESET_FULL_RECT)
	count_flash.mouse_filter = Control.MOUSE_FILTER_IGNORE
	count_layer.add_child(count_flash)
	var fl := CanvasLayer.new()
	fl.layer = 50
	add_child(fl)
	fade = ColorRect.new()
	fade.color = Color(0, 0, 0, 0)
	fade.set_anchors_preset(Control.PRESET_FULL_RECT)
	fade.mouse_filter = Control.MOUSE_FILTER_IGNORE
	fl.add_child(fade)

	menus.new_game.connect(_on_new_game)
	menus.continue_game.connect(_on_continue)
	menus.resume.connect(_on_resume)
	menus.to_title.connect(_on_to_title)
	menus.auth_done.connect(_on_auth_done)
	Game.flags_changed.connect(_on_flags)
	show_title()
	_startup_auth()


## Ao abrir o jogo: reaproveita a última sessão ou pede cadastro/login.
func _startup_auth() -> void:
	if DisplayServer.get_name() == "headless" or Api.logged_in() or Api.guest:
		return
	if await Api.restore_session():
		menus.show_title()
		return
	menus.show_auth("" if Api.online else "Servidor indisponível. Inicie o backend ou jogue offline.")


func _on_auth_done() -> void:
	menus.show_title()


func ui_blocking() -> bool:
	return state != "play" or paused or transitioning or dying or ending_started or dlg.active or craft.visible or invui.visible or puzzle.visible


# ------------------------------------------------------------------ fluxo
func show_title() -> void:
	state = "title"
	paused = false
	ending_started = false
	ending_triggered = false
	if world != null:
		world.queue_free()
		world = null
	hud.visible = false
	play_music("lab")
	menus.show_title()


func _on_new_game() -> void:
	Game.new_game()
	if not skip_cutscene and DisplayServer.get_name() != "headless":
		state = "cutscene"
		menus.hide_all()
		await cut.play()
	_start_play(0)


func _on_continue() -> void:
	if Game.load_game():
		_start_play(Game.cur_room)


func _start_play(room_id: int) -> void:
	menus.hide_all()
	state = "play"
	paused = false
	ending_started = false
	ending_triggered = false
	dying = false
	hud.visible = true
	fade.color.a = 1.0
	_load_room(room_id, "spawn_prev")
	var tw := create_tween()
	tw.tween_property(fade, "color:a", 0.0, 0.5)
	await tw.finished
	_room_intro()


func _on_resume() -> void:
	paused = false
	menus.hide_all()
	Game.lock_input(0.2)


func _on_to_title() -> void:
	if state == "play":
		Game.save_game()
	show_title()


func _load_room(room_id: int, spawn_key: String) -> void:
	if world != null:
		world.queue_free()
		world = null
	Game.cur_room = room_id
	play_music(str(MUSIC_BY_ROOM.get(room_id, "lab")))
	world = WorldScript.new()
	holder.add_child(world)
	world.setup(self, room_id, spawn_key)
	hud.set_room(room_id)
	Game.save_game()
	var r: Dictionary = Game.room(room_id)
	hud.show_banner("%02d  %s" % [room_id, str(r["name"]).to_upper()], Color(str(r["accent"])))


func change_room(room_id: int, spawn_key: String) -> void:
	if transitioning:
		return
	transitioning = true
	var tw := create_tween()
	tw.tween_property(fade, "color:a", 1.0, 0.25)
	await tw.finished
	var key := "spawn_prev" if spawn_key == "prev" else "spawn_next"
	_load_room(room_id, key)
	var tw2 := create_tween()
	tw2.tween_property(fade, "color:a", 0.0, 0.3)
	await tw2.finished
	transitioning = false
	_room_intro()


func _room_intro() -> void:
	var key := "seen_%d" % Game.cur_room
	if not Game.taken.has(key):
		Game.taken[key] = true
		var r: Dictionary = Game.room(Game.cur_room)
		await dlg.say("Protagonista", r["intro"])
	await _boss_speech()


## Sala final: o Dr. Voss começa o discurso sozinho assim que o R-31 entra, e depois passa a atirar.
func _boss_speech() -> void:
	if Game.cur_room != 10 or Game.flag("r10_boss_talked") or Game.flag("r10_bomb"):
		return
	var boss: Dictionary = {}
	for o in Game.room(10)["objects"]:
		if str(o["type"]) == "npc" and str(o["id"]) == "r10_boss":
			boss = o
	if boss.is_empty():
		return
	await dlg.say("Dr. Voss", boss["lines"])
	await dlg.say("Dr. Voss", ["Chega de conversa! Defenda-se, R-31!"])
	Game.set_flag("r10_boss_talked")


func player_died() -> void:
	if dying:
		return
	dying = true
	Api.report_error("MORTE", Game.cur_room, "Recapturado pelos guardas")
	menus.show_caught(true)
	await get_tree().create_timer(2.0).timeout
	Game.hp = Game.MAX_HP
	Game.hp_changed.emit()
	menus.show_caught(false)
	_load_room(Game.cur_room, "spawn_prev")
	dying = false


# ------------------------------------------------------------------ diálogos e terminais
func _learn_list(ids: Array) -> void:
	var names: Array = []
	for rid in ids:
		if Game.learn(str(rid)):
			names.append(Game.item_name(str(rid)))
	if names.size() > 0:
		Game.toast("Receita registrada: " + ", ".join(names), Game.COL_YELLOW)


func read_terminal(d: Dictionary) -> void:
	await dlg.say(str(d["title"]), d["lines"])
	_learn_list(d.get("learn", []))


func talk(d: Dictionary) -> void:
	if str(d["id"]) == "r10_boss":
		await dlg.say("Dr. Voss", ["Chega de conversa! Defenda-se!"])
		return
	var choices: Array = d.get("choices", [])
	var pick: int = await dlg.say(str(d["name"]), d["lines"], choices)
	if pick >= 0 and str(d["id"]) == "r10_boss":
		await dlg.say("Dr. Voss", BOSS_REPLIES[pick])
	_learn_list(d.get("learn", []))
	Game.set_flag(str(d["id"]) + "_talked")


func near_bench() -> bool:
	if world == null:
		return false
	var pp: Vector2 = world.player.position + Vector2(0, -6)
	for p in world.props:
		if p.type == "bench":
			var r: Rect2 = p.rect()
			var cp := Vector2(clampf(pp.x, r.position.x, r.end.x), clampf(pp.y, r.position.y, r.end.y))
			if pp.distance_to(cp) < 40.0:
				return true
	return false


func open_craft() -> void:
	craft.open(bool(world.room.get("broken_bench", false)) if world != null else false)
	Game.set_flag("t_bench")


func open_puzzle(d: Dictionary, cb: Callable) -> void:
	puzzle_cb = cb
	puzzle.open(d)


func _on_puzzle_solved(locker_id: String) -> void:
	Game.set_flag(locker_id + "_unlocked")
	Game.toast("Armário destrancado!", Game.COL_GREEN)
	if puzzle_cb.is_valid():
		puzzle_cb.call()


# ------------------------------------------------------------------ final
func _on_flags() -> void:
	if state != "play" or ending_triggered:
		return
	if Game.flag("r10_bomb"):
		ending_triggered = true
		ending_started = true
		_run_ending()


func _shake(strength: float) -> void:
	holder.position = Vector2(randf_range(-strength, strength), randf_range(-strength, strength))


func _run_ending() -> void:
	# contagem regressiva de 5 segundos: o núcleo entra em sobrecarga
	count_layer.visible = true
	for n in range(5, 0, -1):
		count_label.text = str(n)
		count_label.scale = Vector2.ONE
		count_label.pivot_offset = Vector2(480, 100)
		var tw := create_tween()
		tw.tween_property(count_label, "scale", Vector2(1.25, 1.25), 0.9)
		tw.parallel().tween_property(count_red, "color:a", 0.35, 0.45)
		tw.parallel().tween_property(count_red, "color:a", 0.0, 0.45).set_delay(0.45)
		var t_end: float = Time.get_ticks_msec() + 1000.0
		while Time.get_ticks_msec() < t_end:
			_shake(float(6 - n) * 1.2)
			if world != null and randf() < 0.3:
				world.burst(Vector2(randf_range(60, 900), randf_range(80, 420)), Color(1.0, 0.7, 0.2), 6)
			await get_tree().process_frame
	count_label.text = ""
	holder.position = Vector2.ZERO
	# explosão
	count_flash.color.a = 1.0
	if world != null:
		for i in range(10):
			world.burst(Vector2(randf_range(40, 920), randf_range(80, 430)), Color(1.0, randf_range(0.3, 0.8), 0.1), 30)
		for pr in world.props:
			if pr.type == "npc" and str(pr.d["id"]) == "r10_boss":
				var tv := create_tween()
				tv.tween_property(pr, "rotation", deg_to_rad(88.0), 0.5).set_trans(Tween.TRANS_BOUNCE)
				pr.spr.modulate = Color(0.55, 0.5, 0.5)
	var ft := create_tween()
	ft.tween_property(count_flash, "color:a", 0.0, 1.4)
	for i in range(18):
		_shake(8.0 * (1.0 - float(i) / 18.0))
		await get_tree().create_timer(0.05).timeout
	holder.position = Vector2.ZERO
	count_layer.visible = false
	await get_tree().create_timer(0.6).timeout
	ending_started = false
	await dlg.say("Dr. Voss", ["Meu laboratório... vinte anos... tudo em chamas.", "Eu só queria entender. Fui longe demais..."])
	await dlg.say("R-31", ["Corre! Todo mundo para a saída!"])
	ending_started = true
	var fade_tw := create_tween()
	fade_tw.tween_property(fade, "color:a", 1.0, 0.8)
	await fade_tw.finished
	state = "ending"
	hud.visible = false
	if world != null:
		world.queue_free()
		world = null
	fade.color.a = 0.0
	menus.show_end(
		"Os alarmes se calam e as luzes de evacuação guiam os ratos pelos corredores. Um a um, os sujeitos aprisionados deixam o complexo.\n\n" +
		"O Dr. Voss caiu junto com o seu império de experimentos. O Projeto R-31 chegou ao fim.\n\n" +
		"R-31 olha para trás uma última vez, ao lado de todos os ratos que salvou. Cada reagente foi uma pista; cada laboratório, um segredo. Agora o mundo lá fora é o próximo experimento.")


# ------------------------------------------------------------------ entrada
func _unhandled_input(ev: InputEvent) -> void:
	if state != "play" or paused or transitioning or dying or ending_started:
		return
	if dlg.active or craft.visible or invui.visible or puzzle.visible:
		return
	if ev.is_action_pressed("pause"):
		paused = true
		menus.show_pause()
		return
	if Game.input_locked() or world == null:
		return
	if ev.is_action_pressed("interact"):
		world.try_interact()
	elif ev.is_action_pressed("craft"):
		if near_bench():
			open_craft()
		else:
			Game.toast("Você precisa estar perto de uma bancada para usar a CraftTable.", Game.COL_YELLOW)
	elif ev.is_action_pressed("inventory"):
		invui.open()
		Game.set_flag("t_inv")
	elif ev.is_action_pressed("heal"):
		Game.use_gel()
	elif ev.is_action_pressed("hint"):
		var o := Game.objective(Game.cur_room)
		Game.toast("Dica: " + str(o["hint"]), Game.COL_YELLOW)
	elif ev.is_action_pressed("reset_crates"):
		world.reset_crates()
