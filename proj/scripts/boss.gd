extends Node2D
## Dr. Voss em combate: a cada 2 segundos lança uma bolha de laser na direção do rato.
## Só começa depois da conversa e para quando a bomba é armada.

class Ball extends Node2D:
	var vel: Vector2 = Vector2.ZERO
	var life: float = 6.0
	var world
	var t: float = 0.0

	func _process(delta: float) -> void:
		if world == null or world.main.ui_blocking():
			return
		t += delta
		life -= delta
		position += vel * delta
		queue_redraw()
		if life <= 0.0 or world.cell_solid(int(position.x / 32.0), int(position.y / 32.0)):
			world.burst(position, Color(1.0, 0.3, 0.7), 6)
			queue_free()
			return
		var p = world.player
		if p != null and (p.position + Vector2(0, -6)).distance_to(position) < 11.0:
			p.hurt(1, position - vel.normalized() * 8.0, 150.0, "Bola de laser do Dr. Voss")
			world.burst(position, Color(1.0, 0.3, 0.7), 10)
			queue_free()

	func _draw() -> void:
		var pulse: float = 0.8 + 0.2 * sin(t * 18.0)
		draw_circle(Vector2.ZERO, 14.0 * pulse, Color(1.0, 0.2, 0.6, 0.18))
		draw_circle(Vector2.ZERO, 9.0 * pulse, Color(1.0, 0.3, 0.7, 0.55))
		draw_circle(Vector2.ZERO, 5.0, Color(1.0, 0.95, 1.0, 0.98))
		for i in range(3):
			draw_circle(-vel.normalized() * (7.0 + 6.0 * float(i)), 4.0 - float(i), Color(1.0, 0.3, 0.7, 0.5 - 0.15 * float(i)))


var world
var d: Dictionary = {}
var interval: float = 2.0
var timer: float = 1.2
var charge: float = 0.0
var shots: int = 0


func setup(data: Dictionary, w) -> void:
	d = data
	world = w
	interval = float(data.get("interval", 2.0))
	position = Vector2((float(data["x"]) + 0.5) * 32.0, (float(data["y"]) + 1.0) * 32.0)
	z_index = 30


func active() -> bool:
	return Game.flag("r10_boss_talked") and not Game.flag("r10_bomb") and Game.hp > 0


func _hand() -> Vector2:
	return position + Vector2(0, -34)


func _process(delta: float) -> void:
	if world == null or world.main.ui_blocking():
		return
	if not active():
		charge = 0.0
		queue_redraw()
		return
	timer -= delta
	if timer <= 0.5:
		charge = clampf(1.0 - timer / 0.5, 0.0, 1.0)
	if timer <= 0.0:
		_fire()
		timer = interval
		charge = 0.0
	queue_redraw()


func _fire() -> void:
	var p = world.player
	if p == null:
		return
	shots += 1
	var target: Vector2 = p.position + Vector2(0, -6)
	var b := Ball.new()
	b.world = world
	b.position = _hand()
	b.vel = (target - _hand()).normalized() * 130.0
	world.add_child(b)
	b.z_index = 30


func _draw() -> void:
	if charge > 0.0:
		var h := _hand() - position
		draw_circle(h, 6.0 + 10.0 * charge, Color(1.0, 0.3, 0.7, 0.25 + 0.3 * charge))
		draw_circle(h, 3.0 + 3.0 * charge, Color(1.0, 0.95, 1.0, 0.9))
