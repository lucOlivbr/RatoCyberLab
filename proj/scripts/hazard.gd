extends Node2D
## Perigos de ambiente: faixas elétricas, jatos de vapor, lasers e gás. Desenhados por código (neon).

var world
var d: Dictionary = {}
var kind: String = ""
var area: Rect2 = Rect2()
var t: float = 0.0
var on_t: float = 0.0
var off_t: float = 0.0
var phase: float = 0.0
var clear_flag: String = ""
var dmg: int = 1
var tick: float = 0.0
var knock: float = 150.0
var gas_t: float = 0.0
var fade: float = 1.0
var safe_rects: Array = []     # veneno: zonas seguras em pixels (inclui os caminhos de rato)
var path_rects: Array = []
var gas_cells: Array = []
var puffs: Array = []
var orbit_n: int = 2
var orbit_speed: float = 0.7
var orbit_r: Vector2 = Vector2(80, 56)
var orbit_pts: Array = []


func setup(data: Dictionary, w) -> void:
	d = data
	world = w
	kind = str(data["kind"])
	area = Rect2(float(data["x"]) * 32.0, float(data["y"]) * 32.0, float(data["w"]) * 32.0, float(data["h"]) * 32.0)
	on_t = float(data.get("on", 0.0))
	off_t = float(data.get("off", 0.0))
	phase = float(data.get("phase", 0.0))
	clear_flag = str(data.get("clear_flag", ""))
	dmg = int(data.get("dmg", 1))
	tick = float(data.get("tick", 0.0))
	knock = float(data.get("knock", 150.0))
	z_index = -1
	if kind == "gas" or kind == "poison":
		z_index = 5
	if kind == "poison":
		for r in data.get("safe", []):
			safe_rects.append(_tile_rect(r))
		for r in data.get("paths", []):
			var pr := _tile_rect(r)
			path_rects.append(pr)
			safe_rects.append(pr)
		var rnd := RandomNumberGenerator.new()
		rnd.seed = 777
		var cx0 := int(area.position.x / 32.0)
		var cy0 := int(area.position.y / 32.0)
		for cy in range(cy0, cy0 + int(data["h"])):
			for cx in range(cx0, cx0 + int(data["w"])):
				var cr := Rect2(float(cx) * 32.0, float(cy) * 32.0, 32.0, 32.0)
				if not _in_safe(cr.get_center()) and not world.cell_solid(cx, cy):
					gas_cells.append(cr)
					for k in range(2):
						puffs.append([cr.position + Vector2(rnd.randf() * 32.0, rnd.randf() * 32.0), rnd.randf_range(0.4, 1.2), rnd.randf() * 6.0, rnd.randf_range(10.0, 22.0)])
	if kind == "orbit":
		orbit_n = int(data.get("n", 2))
		orbit_speed = float(data.get("speed", 0.7))
		orbit_r = Vector2(float(data.get("rx", 80.0)), float(data.get("ry", 56.0)))
		z_index = 8
	if kind == "flame":
		z_index = 3


func _tile_rect(r: Array) -> Rect2:
	return Rect2(float(r[0]) * 32.0, float(r[1]) * 32.0, float(r[2]) * 32.0, float(r[3]) * 32.0)


func _in_safe(p: Vector2) -> bool:
	for r in safe_rects:
		if r.has_point(p):
			return true
	return false


func orbit_center() -> Vector2:
	return area.get_center()


func orbit_positions() -> Array:
	var out: Array = []
	for i in range(orbit_n):
		var a: float = t * orbit_speed + float(i) * TAU / float(orbit_n)
		var p: Vector2 = orbit_center() + Vector2(cos(a) * orbit_r.x, sin(a) * orbit_r.y)
		var vis: bool = not world.cell_solid(int(p.x / 32.0), int(p.y / 32.0))
		out.append([p, vis])
	return out


func cleared() -> bool:
	return clear_flag != "" and Game.flag(clear_flag)


func cycle() -> float:
	return on_t + off_t


func is_active() -> bool:
	if cleared():
		return false
	if on_t <= 0.0:
		return true
	return fmod(t + phase, cycle()) < on_t


func is_warning() -> bool:
	if cleared() or on_t <= 0.0:
		return false
	var ph := fmod(t + phase, cycle())
	return ph >= on_t and ph > cycle() - 0.7


func _process(delta: float) -> void:
	if world == null or world.main.ui_blocking():
		return
	t += delta
	gas_t += delta
	if cleared():
		fade = move_toward(fade, 0.0, delta * 0.8)
	queue_redraw()
	if world.player == null:
		return
	if kind == "poison":
		if is_active() and not _in_safe(world.player.position + Vector2(0, -3)):
			world.player.hurt(dmg, world.player.position + Vector2(0, 8), 0.0, source_name())
		return
	if kind == "orbit":
		var pc: Vector2 = world.player.position + Vector2(0, -6)
		for o in orbit_positions():
			if bool(o[1]) and (o[0] as Vector2).distance_to(pc) < 11.0:
				world.player.hurt(dmg, o[0], 120.0, source_name())
		return
	if kind == "flame":
		return
	if is_active():
		if area.intersects(world.player.box()):
			var c := area.get_center()
			var pp: Vector2 = world.player.position
			var dir := Vector2.ZERO
			if kind == "gas":
				dir = Vector2(-1, 0)
			elif area.size.x >= area.size.y:
				dir = Vector2(0, 1.0 if pp.y >= c.y else -1.0)
			else:
				dir = Vector2(1.0 if pp.x >= c.x else -1.0, 0)
			world.player.hurt(dmg, pp - dir * 10.0, knock, source_name())


## Nome do perigo, usado no relatório de erros.
func source_name() -> String:
	match kind:
		"electric": return "Descarga elétrica"
		"steam": return "Vapor quente"
		"laser": return "Campo laser"
		"gas": return "Gás"
		"poison": return "Veneno no ar"
		"orbit": return "Raio orbital"
		"flame": return "Chama"
	return "Perigo da sala"


func _draw() -> void:
	if fade <= 0.01:
		return
	match kind:
		"electric":
			_draw_electric()
		"steam":
			_draw_steam()
		"laser":
			_draw_laser()
		"gas":
			_draw_gas()
		"poison":
			_draw_poison()
		"orbit":
			_draw_orbit()
		"flame":
			_draw_flame()


func _draw_electric() -> void:
	var col := Color(0.35, 0.85, 1.0)
	var act := is_active()
	var warn := is_warning()
	if act:
		draw_rect(area, Color(col.r, col.g, col.b, 0.22), true)
		var horizontal := area.size.x >= area.size.y
		var n := int((area.size.x if horizontal else area.size.y) / 14.0)
		var rnd := RandomNumberGenerator.new()
		rnd.seed = int(t * 18.0)
		var pts := PackedVector2Array()
		for i in range(n + 1):
			var p: float = float(i) * 14.0
			var off: float = rnd.randf_range(-6.0, 6.0)
			if horizontal:
				pts.append(Vector2(area.position.x + p, area.get_center().y + off))
			else:
				pts.append(Vector2(area.get_center().x + off, area.position.y + p))
		draw_polyline(pts, Color(1, 1, 1, 0.95), 2.0)
		draw_polyline(pts, Color(col.r, col.g, col.b, 0.5), 6.0)
	elif warn:
		var a := 0.12 + 0.18 * float(int(t * 10.0) % 2)
		draw_rect(area, Color(1.0, 0.7, 0.2, a), true)
	else:
		draw_rect(area, Color(col.r, col.g, col.b, 0.05), true)
	# trilhos laterais
	var edge := Color(col.r, col.g, col.b, 0.5 if act else 0.25)
	if area.size.x >= area.size.y:
		draw_line(area.position, area.position + Vector2(area.size.x, 0), edge, 1.0)
		draw_line(area.position + Vector2(0, area.size.y), area.end, edge, 1.0)
	else:
		draw_line(area.position, area.position + Vector2(0, area.size.y), edge, 1.0)
		draw_line(area.position + Vector2(area.size.x, 0), area.end, edge, 1.0)


func _draw_steam() -> void:
	var act := is_active()
	var warn := is_warning()
	var cx := area.get_center().x
	if act:
		for i in range(clampi(int(area.size.x * area.size.y / 220.0), 12, 70)):
			var ph: float = fmod(t * 1.8 + float(i) * 0.37, 1.0)
			var r: float = 6.0 + ph * 14.0
			var px: float = cx + sin(float(i) * 2.1 + t * 3.0) * area.size.x * 0.3
			var py: float = area.end.y - ph * (area.size.y + 18.0)
			draw_circle(Vector2(px, py), r, Color(0.85, 0.92, 1.0, 0.45 * (1.0 - ph)))
		draw_rect(area, Color(0.85, 0.92, 1.0, 0.14), true)
	elif warn:
		for i in range(4):
			draw_circle(Vector2(cx + (float(i) - 1.5) * 8.0, area.get_center().y - float(i % 2) * 4.0), 5.0, Color(1, 1, 1, 0.15 + 0.1 * float(int(t * 8.0) % 2)))
	# bocal
	draw_rect(Rect2(area.position.x + 4, area.end.y - 4, area.size.x - 8, 4), Color(0.3, 0.35, 0.5, 0.9), true)


func _draw_laser() -> void:
	if area.size.x > area.size.y:
		_draw_laser_h()
		return
	var act := is_active()
	var warn := is_warning()
	var col := Color(1.0, 0.22, 0.32)
	var cx := area.get_center().x
	if act:
		var flick := 0.85 + 0.15 * sin(t * 40.0)
		draw_line(Vector2(cx, area.position.y), Vector2(cx, area.end.y), Color(col.r, col.g, col.b, 0.28 * flick), 10.0)
		draw_line(Vector2(cx, area.position.y), Vector2(cx, area.end.y), Color(col.r, col.g, col.b, 0.6 * flick), 5.0)
		draw_line(Vector2(cx, area.position.y), Vector2(cx, area.end.y), Color(1, 0.9, 0.9, 0.95), 2.0)
	elif warn:
		draw_line(Vector2(cx, area.position.y), Vector2(cx, area.end.y), Color(col.r, col.g, col.b, 0.18 + 0.3 * float(int(t * 10.0) % 2)), 2.0)
	else:
		draw_line(Vector2(cx, area.position.y), Vector2(cx, area.end.y), Color(col.r, col.g, col.b, 0.07), 1.0)
	# emissores nas pontas
	for yy in [area.position.y, area.end.y]:
		draw_rect(Rect2(cx - 5, yy - 3, 10, 6), Color(0.2, 0.22, 0.3), true)
		draw_circle(Vector2(cx, yy), 2.5, col if act else col.darkened(0.6))


func _draw_gas() -> void:
	var col := Color(0.25, 1.0, 0.4)
	draw_rect(area, Color(col.r, col.g, col.b, 0.16 * fade), true)
	var rnd := RandomNumberGenerator.new()
	rnd.seed = 12345
	for i in range(46):
		var bx: float = area.position.x + rnd.randf() * area.size.x
		var by: float = area.position.y + rnd.randf() * area.size.y
		var sp: float = 0.4 + rnd.randf() * 0.8
		var px: float = bx + sin(gas_t * sp + float(i)) * 14.0
		var py: float = by + cos(gas_t * sp * 0.8 + float(i) * 1.7) * 10.0
		var r: float = 10.0 + rnd.randf() * 16.0
		draw_circle(Vector2(px, py), r, Color(col.r, col.g, col.b, 0.07 * fade))
	draw_rect(area, Color(col.r, col.g, col.b, 0.28 * fade), false, 2.0)


func _draw_laser_h() -> void:
	var act := is_active()
	var warn := is_warning()
	var col := Color(1.0, 0.22, 0.32)
	var cy := area.get_center().y
	var a := Vector2(area.position.x, cy)
	var b := Vector2(area.end.x, cy)
	if act:
		var flick := 0.85 + 0.15 * sin(t * 40.0)
		draw_line(a, b, Color(col.r, col.g, col.b, 0.28 * flick), 10.0)
		draw_line(a, b, Color(col.r, col.g, col.b, 0.6 * flick), 5.0)
		draw_line(a, b, Color(1, 0.9, 0.9, 0.95), 2.0)
	elif warn:
		draw_line(a, b, Color(col.r, col.g, col.b, 0.18 + 0.3 * float(int(t * 10.0) % 2)), 2.0)
	else:
		draw_line(a, b, Color(col.r, col.g, col.b, 0.07), 1.0)
	for xx in [area.position.x, area.end.x]:
		draw_rect(Rect2(xx - 3, cy - 5, 6, 10), Color(0.2, 0.22, 0.3), true)
		draw_circle(Vector2(xx, cy), 2.5, col if act else col.darkened(0.6))


func _draw_poison() -> void:
	if fade <= 0.01:
		return
	var col := Color(0.25, 1.0, 0.4)
	for cr in gas_cells:
		draw_rect(cr, Color(col.r, col.g, col.b, 0.16 * fade), true)
	for pf in puffs:
		var bp: Vector2 = pf[0]
		var sp: float = pf[1]
		var ph: float = pf[2]
		var pos := bp + Vector2(sin(gas_t * sp + ph) * 8.0, cos(gas_t * sp * 0.8 + ph * 1.7) * 6.0)
		draw_circle(pos, float(pf[3]), Color(col.r, col.g, col.b, 0.07 * fade))
	# zonas seguras: borda ciano suave
	for r in safe_rects:
		if path_rects.has(r):
			continue
		draw_rect(r, Color(0.1, 0.9, 1.0, 0.45 * fade), false, 2.0)
	# caminhos de rato: trilha brilhante com pegadas animadas
	for r in path_rects:
		var rr: Rect2 = r
		draw_rect(rr, Color(0.1, 0.9, 1.0, 0.10 * fade), true)
		var horizontal: bool = rr.size.x >= rr.size.y
		var len_: float = rr.size.x if horizontal else rr.size.y
		var n: int = int(len_ / 20.0)
		for i in range(n):
			var q: float = fmod(float(i) * 20.0 + gas_t * 24.0, maxf(len_, 1.0))
			var pc: Vector2
			if horizontal:
				pc = Vector2(rr.position.x + q, rr.get_center().y + (4.0 if i % 2 == 0 else -4.0))
			else:
				pc = Vector2(rr.get_center().x + (4.0 if i % 2 == 0 else -4.0), rr.position.y + q)
			var al: float = (0.55 + 0.4 * sin(gas_t * 4.0 + float(i))) * fade
			draw_circle(pc, 3.0, Color(0.3, 1.0, 1.0, al * 0.5))
			draw_circle(pc + Vector2(3, -3), 1.4, Color(0.7, 1.0, 1.0, al))
			draw_circle(pc + Vector2(-3, -3), 1.4, Color(0.7, 1.0, 1.0, al))
		var c := Color(0.2, 0.95, 1.0, 0.55 * fade)
		if horizontal:
			draw_line(rr.position + Vector2(0, 1), rr.position + Vector2(rr.size.x, 1), c, 1.5)
			draw_line(rr.position + Vector2(0, rr.size.y - 1), rr.end - Vector2(0, 1), c, 1.5)
		else:
			draw_line(rr.position + Vector2(1, 0), rr.position + Vector2(1, rr.size.y), c, 1.5)
			draw_line(rr.position + Vector2(rr.size.x - 1, 0), rr.end - Vector2(1, 0), c, 1.5)


func _draw_orbit() -> void:
	var pts := orbit_positions()
	var col := Color(0.45, 0.85, 1.0)
	var rnd := RandomNumberGenerator.new()
	rnd.seed = int(t * 20.0)
	# arcos de raio entre bolas vizinhas, acompanhando a elipse
	for i in range(pts.size()):
		var a0: float = t * orbit_speed + float(i) * TAU / float(pts.size())
		var a1: float = a0 + TAU / float(pts.size())
		var seg := PackedVector2Array()
		var steps := 14
		for k in range(steps + 1):
			var a: float = lerpf(a0, a1, float(k) / float(steps))
			var p: Vector2 = orbit_center() + Vector2(cos(a) * orbit_r.x, sin(a) * orbit_r.y)
			p += Vector2(rnd.randf_range(-3.0, 3.0), rnd.randf_range(-3.0, 3.0)) * (0.0 if k == 0 or k == steps else 1.0)
			if world.cell_solid(int(p.x / 32.0), int(p.y / 32.0)):
				if seg.size() > 1:
					draw_polyline(seg, Color(col.r, col.g, col.b, 0.35), 3.0)
					draw_polyline(seg, Color(1, 1, 1, 0.8), 1.0)
				seg = PackedVector2Array()
				continue
			seg.append(p)
		if seg.size() > 1:
			draw_polyline(seg, Color(col.r, col.g, col.b, 0.35), 3.0)
			draw_polyline(seg, Color(1, 1, 1, 0.8), 1.0)
	for o in pts:
		if not bool(o[1]):
			continue
		var p: Vector2 = o[0]
		draw_circle(p, 14.0, Color(col.r, col.g, col.b, 0.18))
		draw_circle(p, 8.0, Color(col.r, col.g, col.b, 0.5))
		draw_circle(p, 4.0, Color(1, 1, 1, 0.95))
		for k in range(5):
			var ang: float = rnd.randf() * TAU
			draw_line(p, p + Vector2(cos(ang), sin(ang)) * rnd.randf_range(8.0, 15.0), Color(1, 1, 1, 0.8), 1.0)


func _draw_flame() -> void:
	# fogo decorativo (sempre aceso): várias línguas de fogo ao longo da área
	var n: int = maxi(1, int(area.size.x / 14.0))
	for i in range(n):
		var bx: float = area.position.x + (float(i) + 0.5) * area.size.x / float(n)
		var by: float = area.end.y
		var h: float = minf(area.size.y, 30.0) * (0.75 + 0.25 * sin(t * 9.0 + float(i) * 1.7))
		var sway: float = sin(t * 7.0 + float(i)) * 2.5
		draw_circle(Vector2(bx, by - h * 0.4), 14.0, Color(1.0, 0.5, 0.1, 0.12))
		draw_colored_polygon(PackedVector2Array([Vector2(bx - 7, by), Vector2(bx - 5, by - h * 0.55), Vector2(bx + sway, by - h), Vector2(bx + 5, by - h * 0.55), Vector2(bx + 7, by)]), Color(1.0, 0.4, 0.08, 0.92))
		draw_colored_polygon(PackedVector2Array([Vector2(bx - 4, by), Vector2(bx - 3, by - h * 0.45), Vector2(bx + sway * 0.7, by - h * 0.75), Vector2(bx + 3, by - h * 0.45), Vector2(bx + 4, by)]), Color(1.0, 0.82, 0.2, 0.95))
