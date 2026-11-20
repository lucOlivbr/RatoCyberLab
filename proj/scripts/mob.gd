extends Node2D
## Inimigos do laboratório: drones de patrulha e o mutante. Origem do nó = pés.

var world
var d: Dictionary = {}
var kind: String = ""
var path: Array = []
var idx: int = 0
var speed: float = 50.0
var spr: Sprite2D
var anim_t: float = 0.0
var home: Vector2 = Vector2.ZERO
var cooldown: float = 0.0
var chase: bool = false
var chase_range: float = 9999.0
var bench_safe: bool = false
var chasing: bool = false


func setup(data: Dictionary, w) -> void:
	d = data
	world = w
	kind = str(data["type"])
	spr = Sprite2D.new()
	spr.centered = false
	add_child(spr)
	chase = bool(data.get("chase", false))
	chase_range = float(data.get("range", 9999.0))
	bench_safe = bool(data.get("bench_safe", false))
	if kind == "drone":
		speed = float(data.get("speed", 50.0))
		if data.has("path"):
			for p in data["path"]:
				path.append(Vector2(float(p[0]) * 32.0 + 16.0, float(p[1]) * 32.0 + 30.0))
		else:
			path.append(Vector2(float(data["x"]) * 32.0 + 16.0, float(data["y"]) * 32.0 + 30.0))
		position = path[0]
		idx = 1 % path.size()
		home = position
	else:
		position = Vector2(float(data["x"]) * 32.0 + 16.0, float(data["y"]) * 32.0 + 30.0)
		home = position
		speed = float(data.get("speed", 40.0))
		chase_range = float(data.get("range", 230.0))
	if data.has("tint"):
		spr.modulate = Color(str(data["tint"]))
	_set_frame(0)


func _set_frame(f: int) -> void:
	var t := Game.tex("res://assets/world/%s_%d.png" % [kind, f])
	spr.texture = t
	if t != null:
		spr.position = Vector2(-t.get_width() / 2.0, -t.get_height())


func _draw() -> void:
	draw_set_transform(Vector2(0, -1), 0.0, Vector2(1.0, 0.35))
	draw_circle(Vector2.ZERO, 11.0 if kind == "drone" else 14.0, Color(0, 0, 0, 0.35))
	draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)


func asleep() -> bool:
	return kind == "mutant" and Game.flag("r8_free")


func _process(delta: float) -> void:
	if world == null or world.main.ui_blocking():
		return
	anim_t += delta
	_set_frame(int(anim_t * 6.0) % 2)
	var hover: float = 0.0
	if kind == "drone":
		hover = sin(anim_t * 5.0) * 2.0 - 8.0
		_move_drone(delta)
	else:
		if asleep():
			spr.modulate = Color(0.5, 0.5, 0.5, 0.8)
			spr.position.y = -float(spr.texture.get_height()) if spr.texture != null else 0.0
			return
		_move_mutant(delta)
	spr.position.y = -float(spr.texture.get_height()) + hover if spr.texture != null else 0.0
	# contato
	var p = world.player
	if p == null:
		return
	var center := position + Vector2(0, -12)
	var pc: Vector2 = p.position + Vector2(0, -6)
	var rad: float = 12.0 if kind == "drone" else 15.0
	if center.distance_to(pc) < rad + 6.0:
		p.hurt(1, position, 170.0, "Drone de segurança" if kind == "drone" else "Mutante")


func _player_safe() -> bool:
	## a zona da bancada protege o rato: perseguidores desistem enquanto ele a usa
	if not bench_safe or world.player == null:
		return false
	if "craft" in world.main and world.main.craft.visible:
		return true
	var pp: Vector2 = world.player.position + Vector2(0, -6)
	for pr in world.props:
		if pr.type == "bench":
			var r: Rect2 = pr.rect()
			var cp := Vector2(clampf(pp.x, r.position.x, r.end.x), clampf(pp.y, r.position.y, r.end.y))
			if pp.distance_to(cp) < 86.0:
				return true
	return false


func _move_drone(delta: float) -> void:
	if path.is_empty():
		return
	if chase and world.player != null:
		var to: Vector2 = world.player.position - position
		if not _player_safe() and to.length() < chase_range:
			chasing = true
			spr.flip_h = to.x < 0.0
			if to.length() > 2.0:
				world.slide(self, to.normalized() * speed * delta, 10.0, 10.0, false)
			return
		chasing = false
		if _player_safe():
			# volta para perto de casa e espera
			var back: Vector2 = home - position
			if back.length() > 3.0:
				position += back.normalized() * minf(speed * delta, back.length())
			return
	var target: Vector2 = path[idx]
	var dir := target - position
	var step := speed * delta
	if dir.length() <= step:
		position = target
		idx = (idx + 1) % path.size()
	else:
		position += dir.normalized() * step


func _move_mutant(delta: float) -> void:
	var p = world.player
	if p == null:
		return
	var to: Vector2 = p.position - position
	var dist := to.length()
	if dist > chase_range or dist < 2.0:
		return
	spr.flip_h = to.x < 0.0
	world.slide(self, to.normalized() * speed * delta, 12.0, 12.0, false)
