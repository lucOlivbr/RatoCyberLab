extends Node2D
## Jogador: o rato de laboratório. Origem do nó = pés.

const WALK_SPEED := 92.0
const RUN_SPEED := 142.0
const HALF_W := 7.0
const BOX_H := 10.0
const RUN_SCALE := 0.66

var world
var facing: Vector2 = Vector2.DOWN
var kb: Vector2 = Vector2.ZERO
var invuln: float = 0.0
var anim_t: float = 0.0
var moving: bool = false
var busy: bool = false      # animação especial (usar item etc.)
var spr: Sprite2D
var tex: Dictionary = {}     # "walk_f" -> [frames]  (f=frente b=costas r=direita l=esquerda)
var last_h: float = 1.0
var run_phase: float = 0.0
var walked: float = 0.0


func _ready() -> void:
	for kind in ["walk", "run"]:
		for d in ["f", "b", "r", "l"]:
			var arr: Array = []
			var i := 0
			while ResourceLoader.exists("res://assets/sprites/r31_%s_%s_%d.png" % [kind, d, i]):
				arr.append(Game.tex("res://assets/sprites/r31_%s_%s_%d.png" % [kind, d, i]))
				i += 1
			tex["%s_%s" % [kind, d]] = arr
	spr = Sprite2D.new()
	spr.centered = true
	add_child(spr)
	_show(tex["walk_f"][0])


func _show(t: Texture2D) -> void:
	spr.texture = t
	spr.flip_h = false
	spr.rotation = 0.0
	spr.scale = Vector2.ONE
	spr.position = Vector2(0.0, -t.get_height() * 0.5 + 2.0)


func _dir_key() -> String:
	if absf(facing.x) > 0.5:
		return "r" if facing.x > 0.0 else "l"
	return "f" if facing.y > 0.0 else "b"


func _draw() -> void:
	draw_set_transform(Vector2(0, -1), 0.0, Vector2(1.0, 0.35))
	draw_circle(Vector2.ZERO, 11.0, Color(0, 0, 0, 0.4))
	draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)


func box() -> Rect2:
	return Rect2(position.x - HALF_W, position.y - BOX_H, HALF_W * 2.0, BOX_H)


func hurt(dmg: int, from_pos: Vector2, push: float = 160.0, src: String = "") -> void:
	if invuln > 0.0 or Game.hp <= 0:
		return
	Game.damage(dmg)
	Api.report_error("DANO", Game.cur_room, src if src != "" else "Perigo da sala")
	invuln = 1.0
	var d := position - from_pos
	if d.length() < 1.0:
		d = Vector2.DOWN
	kb = d.normalized() * push
	var tw := create_tween()
	spr.modulate = Color(1.0, 0.3, 0.3)
	tw.tween_property(spr, "modulate", Color.WHITE, 0.35)
	if Game.hp <= 0:
		world.main.player_died()


func _process(delta: float) -> void:
	if world == null or world.main.ui_blocking():
		moving = false
		_animate(delta)
		return
	invuln = max(0.0, invuln - delta)
	var dir := Input.get_vector("move_left", "move_right", "move_up", "move_down")
	var running := Input.is_action_pressed("run")
	var spd := RUN_SPEED if running else WALK_SPEED
	moving = dir.length() > 0.1
	if moving:
		if absf(dir.x) > absf(dir.y) + 0.15:
			facing = Vector2(signf(dir.x), 0)
		elif absf(dir.y) > absf(dir.x) + 0.15:
			facing = Vector2(0, signf(dir.y))
		elif absf(facing.x) > 0.5:
			facing = Vector2(signf(dir.x) if dir.x != 0.0 else facing.x, 0)
		else:
			facing = Vector2(0, signf(dir.y) if dir.y != 0.0 else facing.y)
		world.slide(self, dir * spd * delta, HALF_W, BOX_H, true)
		walked += spd * delta
		if walked > 48.0:
			Game.set_flag("t_moved")
	if kb.length() > 4.0:
		world.slide(self, kb * delta, HALF_W, BOX_H, false)
		kb = kb.move_toward(Vector2.ZERO, 620.0 * delta)
	else:
		kb = Vector2.ZERO
	_animate(delta, running)


func _animate(delta: float, running: bool = false) -> void:
	anim_t += delta
	if invuln > 0.0 and Game.hp > 0:
		spr.visible = int(invuln * 14.0) % 2 == 0 or invuln > 0.7
	else:
		spr.visible = true
	var d := _dir_key()
	if not moving:
		_show(tex["walk_" + d][0])
		spr.position.y += sin(anim_t * 3.0) * 0.5
		return
	var kind := "run" if running else "walk"
	var frames: Array = tex["%s_%s" % [kind, d]]
	run_phase += delta * (13.0 if running else 8.0)
	_show(frames[int(run_phase) % frames.size()])
