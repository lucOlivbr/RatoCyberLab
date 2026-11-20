extends SceneTree
## Teste de alcance com a colisão real do jogador (caixa 14x10), passo de 8px.
## Uso: godot --headless --path <projeto> --script res://tests/reach.gd

var WorldScript
var StubScript
var fails: int = 0


func _initialize() -> void:
	WorldScript = load("res://scripts/world.gd")
	StubScript = load("res://tests/stub_main.gd")
	await process_frame
	var game = root.get_node("Game")
	var stub = StubScript.new()
	root.add_child(stub)
	for rid in range(1, 11):
		game.flags = {}
		game.taken = {}
		# resolve barreiras físicas para testar a saída
		for f in ["r2_melt", "r5_open"]:
			game.flags[f] = true
		var w = WorldScript.new()
		root.add_child(w)
		w.setup(stub, rid, "spawn_prev")
		_test_room(w, rid, game)
		w.queue_free()
	print("")
	print("RESULTADO ALCANCE: ", "TUDO OK" if fails == 0 else "%d FALHAS" % fails)
	quit(1 if fails > 0 else 0)


func _reachable(w, start: Vector2) -> Dictionary:
	var seen: Dictionary = {}
	var q: Array = [start]
	seen[Vector2i(int(start.x), int(start.y))] = true
	var step := 8
	var i := 0
	while i < q.size():
		var p: Vector2 = q[i]
		i += 1
		for d in [Vector2(step, 0), Vector2(-step, 0), Vector2(0, step), Vector2(0, -step)]:
			var np: Vector2 = p + d
			var key := Vector2i(int(np.x), int(np.y))
			if seen.has(key):
				continue
			var b := Rect2(np.x - 7.0, np.y - 10.0, 14.0, 10.0)
			if np.x < 0 or np.y < 0 or np.x > 960 or np.y > 480:
				continue
			if w.box_hits(b):
				continue
			seen[key] = true
			q.append(np)
	return seen


func _any_near(seen: Dictionary, r: Rect2, max_d: float) -> bool:
	for k in seen:
		var pp := Vector2(k.x, k.y - 6)
		var cx: float = clampf(pp.x, r.position.x, r.end.x)
		var cy: float = clampf(pp.y, r.position.y, r.end.y)
		if pp.distance_to(Vector2(cx, cy)) < max_d:
			return true
	return false


func _test_room(w, rid: int, game) -> void:
	var sp: Vector2 = w.player.position
	var seen = _reachable(w, sp)
	var bad := 0
	if w.box_hits(w.player.box()):
		print("  FAIL sala %d: spawn_prev dentro de colisão" % rid)
		bad += 1
	var sn: Array = w.room["spawn_next"]
	var snp := Vector2(float(sn[0]) * 32.0 + 16.0, float(sn[1]) * 32.0 + 24.0)
	if w.box_hits(Rect2(snp.x - 7, snp.y - 10, 14, 10)) or not seen.has(Vector2i(int(snp.x) - int(snp.x) % 8, int(snp.y) - int(snp.y) % 8)) and not _any_near(seen, Rect2(snp - Vector2(2, 2), Vector2(4, 4)), 10.0):
		print("  FAIL sala %d: spawn_next inalcançável/colidindo %s" % [rid, str(snp)])
		bad += 1
	for p in w.props:
		var t: String = p.type
		if t == "door":
			if not _any_near(seen, p.trigger_rect(), 0.5) and not _door_touch(seen, p):
				print("  FAIL sala %d: porta %s inalcançável" % [rid, str(p.d.get("to", "?"))])
				bad += 1
		elif p.interactable:
			if not _any_near(seen, p.rect(), 24.0):
				print("  FAIL sala %d: %s %s inalcançável" % [rid, t, str(p.d.get("id", ""))])
				bad += 1
	print("sala %02d: %d células alcançáveis, %d problemas" % [rid, seen.size(), bad])
	fails += bad


func _door_touch(seen: Dictionary, p) -> bool:
	var tr: Rect2 = p.trigger_rect().grow(8.0)
	for k in seen:
		var b := Rect2(float(k.x) - 7.0, float(k.y) - 10.0, 14.0, 10.0)
		if tr.intersects(b):
			return true
	return false
