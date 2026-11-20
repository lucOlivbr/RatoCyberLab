extends Node2D
## Uma sala do laboratório: fundo, colisões, objetos, perigos, inimigos e o jogador.

const PropScript := preload("res://scripts/prop.gd")
const HazardScript := preload("res://scripts/hazard.gd")
const MobScript := preload("res://scripts/mob.gd")
const PlayerScript := preload("res://scripts/player.gd")
const BossScript := preload("res://scripts/boss.gd")

var main
var room: Dictionary = {}
var rid: int = 1
var grid: Array = []
var solid_rects: Array = []
var props: Array = []
var crates: Array = []
var plates: Array = []
var doors: Array = []
var hazards: Array = []
var mobs: Array = []
var player
var ents: Node2D
var prompt_label: Label
var target = null
var door_cooldown: float = 0.0
var plates_latched: bool = false


func setup(m, room_id: int, spawn_key: String) -> void:
	main = m
	rid = room_id
	room = Game.room(room_id)
	grid = room["grid"]
	var bg := Sprite2D.new()
	bg.texture = Game.tex("res://assets/world/bg_%02d.png" % rid)
	bg.centered = false
	bg.z_index = -10
	add_child(bg)
	ents = Node2D.new()
	ents.y_sort_enabled = true
	add_child(ents)
	for o in room["objects"]:
		_build_object(o)
	player = PlayerScript.new()
	player.world = self
	var sp: Array = room[spawn_key]
	player.position = Vector2(float(sp[0]) * 32.0 + 16.0, float(sp[1]) * 32.0 + 24.0)
	ents.add_child(player)
	var dm := CanvasModulate.new()
	add_child(dm)
	dm.color = Color(1, 1, 1, 1)
	prompt_label = Label.new()
	prompt_label.z_index = 200
	prompt_label.add_theme_font_size_override("font_size", 12)
	prompt_label.add_theme_color_override("font_color", Color.WHITE)
	prompt_label.add_theme_color_override("font_outline_color", Color(0.02, 0.04, 0.1))
	prompt_label.add_theme_constant_override("outline_size", 5)
	prompt_label.visible = false
	add_child(prompt_label)
	Game.flags_changed.connect(_on_flags)
	_update_plates()


func _build_object(o: Dictionary) -> void:
	var t: String = str(o["type"])
	match t:
		"decor":
			if bool(o.get("solid", false)) and str(o["kind"]) != "lamp":
				solid_rects.append(Rect2(float(o["x"]) * 32.0, float(o["y"]) * 32.0, float(o["w"]) * 32.0, float(o["h"]) * 32.0))
		"hazard":
			var h := HazardScript.new()
			h.setup(o, self)
			add_child(h)
			hazards.append(h)
		"boss":
			var bs := BossScript.new()
			bs.setup(o, self)
			add_child(bs)
		"drone", "mutant":
			var m := MobScript.new()
			m.setup(o, self)
			ents.add_child(m)
			mobs.append(m)
		_:
			if t == "pickup" and Game.taken.has(str(o["id"])):
				return
			var p := PropScript.new()
			p.setup(o, self)
			ents.add_child(p)
			props.append(p)
			if t == "crate":
				crates.append(p)
			elif t == "plate":
				plates.append(p)
			elif t == "door":
				doors.append(p)


func remove_prop(p) -> void:
	props.erase(p)
	p.queue_free()


# ------------------------------------------------------------------ colisão
func cell_solid(cx: int, cy: int) -> bool:
	if cy < 0 or cy >= grid.size() or cx < 0 or cx >= str(grid[0]).length():
		return true
	var c: String = str(grid[cy])[cx]
	return c == "#" or c == "D"


func box_hits(b: Rect2, ignore = null) -> bool:
	var x0 := int(floor(b.position.x / 32.0))
	var x1 := int(floor((b.end.x - 0.01) / 32.0))
	var y0 := int(floor(b.position.y / 32.0))
	var y1 := int(floor((b.end.y - 0.01) / 32.0))
	for cy in range(y0, y1 + 1):
		for cx in range(x0, x1 + 1):
			if cell_solid(cx, cy):
				return true
	for r in solid_rects:
		if r.intersects(b):
			return true
	for p in props:
		if p != ignore and p.solid and p.rect().intersects(b):
			return true
	return false


func _try_move(a, dv: Vector2, half_w: float, h: float, pusher: bool) -> bool:
	var np: Vector2 = a.position + dv
	var b := Rect2(np.x - half_w, np.y - h, half_w * 2.0, h)
	if pusher:
		for c in crates:
			if c.rect().intersects(b):
				var cr: Rect2 = c.rect()
				var nr := Rect2(cr.position + dv, cr.size)
				if not box_hits(nr, c):
					c.position += dv
					_update_plates()
	if box_hits(b, a):
		return false
	a.position = np
	return true


func slide(a, dv: Vector2, half_w: float, h: float, pusher: bool) -> void:
	# passos pequenos para não atravessar paredes
	var steps: int = int(ceil(dv.length() / 3.0))
	if steps < 1:
		return
	var sv := dv / float(steps)
	for i in range(steps):
		if sv.x != 0.0:
			_try_move(a, Vector2(sv.x, 0.0), half_w, h, pusher)
		if sv.y != 0.0:
			_try_move(a, Vector2(0.0, sv.y), half_w, h, pusher)


# ------------------------------------------------------------------ caixas e placas
func _update_plates() -> void:
	if plates.is_empty():
		return
	var all_on := true
	for pl in plates:
		var cell := Rect2(float(pl.d["x"]) * 32.0, float(pl.d["y"]) * 32.0, 32.0, 32.0)
		var on := false
		for c in crates:
			if cell.has_point(c.rect().get_center()):
				on = true
		pl.set_plate(on or plates_latched)
		if not on:
			all_on = false
	if all_on and not plates_latched:
		plates_latched = true
		var grp: String = str(plates[0].d["group"])
		Game.toast("As placas de pressão foram ativadas! O portão de carga destravou.", Game.COL_GREEN)
		Game.set_flag(grp)


func reset_crates() -> void:
	if crates.is_empty():
		return
	for c in crates:
		c.reset_to_start()
	plates_latched = Game.flag(str(plates[0].d["group"])) if not plates.is_empty() else false
	_update_plates()
	Game.toast("Caixas reiniciadas.", Game.COL_YELLOW)


# ------------------------------------------------------------------ efeitos
func burst(pos: Vector2, col: Color, amount: int = 16) -> void:
	var p := CPUParticles2D.new()
	p.position = pos
	p.emitting = true
	p.one_shot = true
	p.amount = amount
	p.lifetime = 0.8
	p.explosiveness = 1.0
	p.direction = Vector2(0, -1)
	p.spread = 180.0
	p.initial_velocity_min = 30.0
	p.initial_velocity_max = 110.0
	p.gravity = Vector2(0, 90)
	p.scale_amount_min = 2.0
	p.scale_amount_max = 4.0
	p.color = col
	p.z_index = 50
	add_child(p)
	get_tree().create_timer(1.4).timeout.connect(p.queue_free)


func freed_rat(pos: Vector2) -> void:
	var s := Sprite2D.new()
	s.texture = Game.tex("res://assets/sprites/nrat_run_0.png")
	s.centered = false
	s.scale = Vector2(1.0, 1.0)
	var go_right: bool = pos.x < 480.0
	s.flip_h = not go_right
	s.position = pos + Vector2(-20, -30)
	s.z_index = 40
	add_child(s)
	var dest := Vector2(930.0 if go_right else 10.0, s.position.y)
	var tw := create_tween()
	tw.tween_property(s, "position", dest, 1.8)
	tw.parallel().tween_method(func(t: float):
		s.texture = Game.tex("res://assets/sprites/nrat_run_%d.png" % (int(t * 12.0) % 4)), 0.0, 1.8, 1.8)
	tw.parallel().tween_property(s, "modulate:a", 0.0, 0.5).set_delay(1.3)
	tw.tween_callback(s.queue_free)


func _on_flags() -> void:
	if Game.flag("r10_free") and rid == 10 and not has_meta("pods_burst"):
		set_meta("pods_burst", true)
		for o in room["objects"]:
			if str(o["type"]) == "decor" and str(o["kind"]) == "pod":
				burst(Vector2((float(o["x"]) + float(o["w"]) / 2.0) * 32.0, (float(o["y"]) + 1.0) * 32.0), Game.COL_GREEN, 26)


# ------------------------------------------------------------------ loop
func _nearest_interactable():
	var best = null
	var bd: float = 26.0
	var pp: Vector2 = player.position + Vector2(0, -6)
	for p in props:
		if not p.interactable or not p.visible:
			continue
		if p.type == "obstacle" and p.resolved and (str(p.d["kind"]) == "ice" or str(p.d["kind"]) == "crystal"):
			continue
		var r: Rect2 = p.rect()
		var cx: float = clampf(pp.x, r.position.x, r.end.x)
		var cy: float = clampf(pp.y, r.position.y, r.end.y)
		var dist: float = pp.distance_to(Vector2(cx, cy))
		if dist < bd:
			bd = dist
			best = p
	return best


func try_interact() -> void:
	if target != null and is_instance_valid(target):
		target.interact()


func _process(delta: float) -> void:
	if main.ui_blocking():
		return
	door_cooldown = max(0.0, door_cooldown - delta)
	target = _nearest_interactable()
	if target != null:
		prompt_label.text = "[E] " + target.prompt_text()
		var w: float = prompt_label.get_minimum_size().x
		var pos: Vector2 = target.position + Vector2(-w / 2.0, -target.size.y - 26.0)
		if target.type == "pickup":
			pos = target.position + Vector2(-w / 2.0, -44.0)
		pos.x = clampf(pos.x, 4.0, 960.0 - w - 4.0)
		pos.y = clampf(pos.y, 4.0, 456.0)
		prompt_label.position = pos
		prompt_label.visible = true
	else:
		prompt_label.visible = false
	# portas
	var pb: Rect2 = player.box()
	for dr in doors:
		if dr.trigger_rect().intersects(pb):
			if dr.door_unlocked():
				main.change_room(int(dr.d["to"]), str(dr.d["spawn"]))
				return
			elif door_cooldown <= 0.0:
				door_cooldown = 2.5
				Game.toast(str(dr.d.get("locked_msg", "Trancado.")), Game.COL_RED)
