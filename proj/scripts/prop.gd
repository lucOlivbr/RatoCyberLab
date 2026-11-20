extends Node2D
## Objeto genérico do mundo (porta, terminal, armário, item, bancada, obstáculo, gaiola, caixa, placa, NPC).
## Origem do nó = centro da base do objeto (para ordenação por Y).

var world
var d: Dictionary = {}
var type: String = ""
var size: Vector2 = Vector2(32, 32)
var solid: bool = false
var interactable: bool = false
var spr: Sprite2D
var start_pos: Vector2 = Vector2.ZERO
var pulse: float = 0.0
var is_read: bool = false
var plate_on: bool = false
var resolved: bool = false
var item_id: String = ""
var bob_t: float = 0.0


func setup(data: Dictionary, w) -> void:
	d = data
	world = w
	type = str(data["type"])
	var gx: float = float(data["x"])
	var gy: float = float(data["y"])
	var gw: float = float(data.get("w", 1))
	var gh: float = float(data.get("h", 1))
	if type == "bench":
		gw = 3.0
		gh = 2.0
	size = Vector2(gw * 32.0, gh * 32.0)
	position = Vector2((gx + gw / 2.0) * 32.0, (gy + gh) * 32.0)
	start_pos = position
	spr = Sprite2D.new()
	spr.centered = false
	add_child(spr)
	match type:
		"terminal", "locker", "bench", "npc", "obstacle", "cage":
			solid = true
			interactable = true
		"crate":
			solid = true
		"pickup":
			interactable = true
			item_id = str(data["item"])
		"plate":
			z_index = -2
		"door":
			pass
	if type == "obstacle":
		resolved = Game.flag(str(d["flag"]))
	if type == "cage":
		resolved = Game.flag(str(d["flag"]))
	Game.flags_changed.connect(refresh)
	refresh()


func rect() -> Rect2:
	return Rect2(position.x - size.x / 2.0, position.y - size.y, size.x, size.y)


func trigger_rect() -> Rect2:
	return Rect2(float(d["x"]) * 32.0, float(d["y"]) * 32.0, float(d["w"]) * 32.0, float(d["h"]) * 32.0).grow(6.0)


func door_unlocked() -> bool:
	var needs: String = str(d.get("needs_flag", ""))
	return needs == "" or Game.expr_ok(needs)


func _set_sprite(path: String) -> void:
	var t := Game.tex(path)
	spr.texture = t
	if t != null:
		spr.position = Vector2(-t.get_width() / 2.0, -t.get_height())


func refresh() -> void:
	queue_redraw()
	if spr == null:
		return
	match type:
		"door":
			if d.get("back", false):
				_set_sprite("res://assets/world/door_back.png")
			else:
				var kind: String = str(d.get("kind", "door"))
				var ok := door_unlocked()
				if kind == "shutter":
					_set_sprite("res://assets/world/door_shutter_open.png" if ok else "res://assets/world/door_shutter_closed.png")
				else:
					_set_sprite("res://assets/world/door_open.png" if ok else "res://assets/world/door_locked.png")
		"terminal":
			_set_sprite("res://assets/world/terminal_%d.png" % (1 if is_read else 0))
		"locker":
			_set_sprite("res://assets/world/locker_%d.png" % (1 if Game.taken.has(str(d["id"])) else 0))
		"bench":
			_set_sprite("res://assets/world/bench.png")
		"obstacle":
			var done := Game.flag(str(d["flag"]))
			var kind2: String = str(d["kind"])
			if kind2 == "ice" or kind2 == "crystal" or kind2 == "bars":
				_set_sprite("res://assets/world/%s.png" % kind2)
				if done and not resolved:
					resolved = true
					solid = false
					var tw := create_tween()
					tw.tween_property(self, "modulate:a", 0.0, 0.6)
					tw.tween_callback(func(): visible = false)
				elif done:
					solid = false
					visible = false
			else:
				_set_sprite("res://assets/world/console_%s_%d.png" % [kind2, 1 if done else 0])
		"cage":
			_set_sprite("res://assets/world/cage_%d.png" % (1 if Game.flag(str(d["flag"])) else 0))
		"crate":
			_set_sprite("res://assets/world/crate.png")
		"plate":
			_set_sprite("res://assets/world/plate_%d.png" % (1 if plate_on else 0))
		"npc":
			_set_sprite("res://assets/world/npc_%s.png" % str(d["kind"]))
		"pickup":
			pass


func prompt_text() -> String:
	match type:
		"terminal":
			return "Ler terminal"
		"locker":
			if locked():
				return "Armário trancado (resolver o código)"
			return "Armário (vazio)" if Game.taken.has(str(d["id"])) else "Abrir armário"
		"pickup":
			return "Coletar " + Game.item_name(item_id)
		"bench":
			return "Usar a bancada (CraftTable)"
		"obstacle":
			if Game.flag(str(d["flag"])):
				return str(d["label"]) + " (ok)"
			return "Usar: " + str(d["label"])
		"cage":
			if Game.flag(str(d["flag"])):
				return str(d["label"]) + " (aberta)"
			return "Abrir: " + str(d["label"])
		"npc":
			return "Falar com " + str(d["name"])
	return ""


func set_plate(on: bool) -> void:
	if on != plate_on:
		plate_on = on
		refresh()


func reset_to_start() -> void:
	position = start_pos


func _process(delta: float) -> void:
	if type == "locker" and locked():
		queue_redraw()
	if type == "pickup":
		if world == null or world.main.ui_blocking():
			return
		bob_t += delta
		queue_redraw()


func _draw() -> void:
	if type == "locker" and locked():
		# cadeado vermelho sobre o armário trancado
		var pulse: float = 0.6 + 0.4 * sin(Time.get_ticks_msec() / 260.0)
		draw_rect(Rect2(-6, -44, 12, 9), Color(0.9, 0.2, 0.25), true)
		draw_arc(Vector2(0, -44), 4.5, PI, TAU, 10, Color(0.9, 0.9, 0.95), 2.0)
		draw_rect(Rect2(-1, -41, 2, 4), Color(0.15, 0.02, 0.04), true)
		draw_circle(Vector2(0, -39), 12.0, Color(1.0, 0.2, 0.25, 0.12 * pulse))
		return
	if type != "pickup":
		return
	var col: Color = Game.item_color(item_id)
	var b: float = sin(bob_t * 3.0) * 2.0
	var cc := Vector2(0, -15.0 + b)
	var a: float = 0.18 + 0.1 * sin(bob_t * 4.0)
	draw_circle(cc, 15.0, Color(col.r, col.g, col.b, a))
	draw_set_transform(Vector2(0, -2), 0.0, Vector2(1.0, 0.35))
	draw_circle(Vector2.ZERO, 9.0, Color(0, 0, 0, 0.35))
	draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
	Game.draw_icon(self, item_id, cc, 20.0)


# ------------------------------------------------------------------ interações
func interact() -> void:
	match type:
		"terminal":
			is_read = true
			refresh()
			world.main.read_terminal(d)
		"locker":
			_open_locker()
		"pickup":
			_collect()
		"bench":
			world.main.open_craft()
		"obstacle":
			_use_obstacle()
		"cage":
			_use_cage()
		"npc":
			world.main.talk(d)


func locked() -> bool:
	return d.has("puzzle") and not Game.flag(str(d["id"]) + "_unlocked")


func _open_locker() -> void:
	var id: String = str(d["id"])
	if locked():
		world.main.open_puzzle(d, Callable(self, "_open_locker"))
		return
	if Game.taken.has(id):
		Game.toast("O armário está vazio.", Game.COL_YELLOW)
		return
	Game.taken[id] = true
	var learn: Array = d.get("learn", [])
	if learn.size() > 0:
		var names: Array = []
		for rid in learn:
			if Game.learn(str(rid)):
				names.append(Game.item_name(str(rid)))
		if names.size() > 0:
			Game.toast("Receita registrada: " + ", ".join(names), Game.COL_YELLOW)
		elif d["items"].is_empty():
			Game.toast("Você já conhece essa receita.", Game.COL_YELLOW)
	var items: Dictionary = d["items"]
	for k in items:
		Game.add_item(str(k), int(items[k]))
		Game.toast("+ %d %s" % [int(items[k]), Game.item_name(str(k))], Game.COL_YELLOW)
	refresh()
	world.burst(position + Vector2(0, -20), Game.COL_YELLOW, 10)


func _collect() -> void:
	Game.taken[str(d["id"])] = true
	Game.add_item(item_id, int(d.get("qty", 1)))
	Game.toast("+ %s" % Game.item_name(item_id), Game.item_color(item_id))
	world.burst(position + Vector2(0, -14), Game.item_color(item_id), 8)
	world.remove_prop(self)


func _use_obstacle() -> void:
	var flag_name: String = str(d["flag"])
	if Game.flag(flag_name):
		Game.toast("Já resolvido.", Game.COL_YELLOW)
		return
	if d.has("requires") and not Game.expr_ok(str(d["requires"])):
		Game.toast(str(d.get("req_msg", "Ainda não dá para usar isto.")), Game.COL_RED)
		return
	var need: String = str(d["needs"])
	if Game.has(need):
		if bool(d["consume"]):
			Game.remove_item(need, 1)
		Game.toast(str(d["ok_msg"]), Game.COL_GREEN)
		world.burst(position + Vector2(0, -size.y / 2.0), Game.COL_GREEN, 22)
		Game.set_flag(flag_name)
	else:
		Game.toast(str(d["fail_msg"]), Game.COL_RED)


func _use_cage() -> void:
	var flag_name: String = str(d["flag"])
	if Game.flag(flag_name):
		Game.toast("A gaiola já está aberta.", Game.COL_YELLOW)
		return
	if d.has("requires") and not Game.expr_ok(str(d["requires"])):
		Game.toast(str(d.get("req_msg", "Ainda não dá para abrir.")), Game.COL_RED)
		return
	var need: String = str(d["needs"])
	if Game.has(need):
		Game.toast(str(d["ok_msg"]), Game.COL_GREEN)
		world.burst(position + Vector2(0, -size.y / 2.0), Game.COL_GREEN, 22)
		world.freed_rat(position)
		Game.set_flag(flag_name)
		if Game.flag("r8_rat1") and Game.flag("r8_rat2"):
			Game.set_flag("r8_free")
	else:
		Game.toast(str(d["fail_msg"]), Game.COL_RED)
