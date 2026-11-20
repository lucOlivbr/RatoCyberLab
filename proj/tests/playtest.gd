extends SceneTree
## Playtest automático: percorre as 10 salas resolvendo todos os puzzles.
## Uso: godot --headless --path <projeto> --script res://tests/playtest.gd

var main
var game
var fails: int = 0


func _initialize() -> void:
	game = root.get_node("Game")
	var packed: PackedScene = load("res://scenes/main.tscn")
	main = packed.instantiate()
	root.add_child(main)
	_run()


func check(cond: bool, msg: String) -> void:
	if cond:
		print("  ok   - ", msg)
	else:
		print("  FAIL - ", msg)
		fails += 1


func wait(sec: float) -> void:
	await create_timer(sec).timeout


func world():
	return main.world


func tp_near(o: Dictionary) -> void:
	var w: float = float(o.get("w", 1))
	var h: float = float(o.get("h", 1))
	if str(o["type"]) == "bench":
		w = 3.0
		h = 2.0
	world().player.position = Vector2((float(o["x"]) + w / 2.0) * 32.0, (float(o["y"]) + h) * 32.0 + 12.0)
	world().player.invuln = 5.0
	world()._process(0.016)


func interact_obj(o: Dictionary) -> void:
	tp_near(o)
	world().try_interact()


func collect_all() -> void:
	for o in world().room["objects"]:
		var t: String = str(o["type"])
		if t == "pickup" or t == "locker":
			if t == "locker" and o.has("puzzle"):
				game.set_flag(str(o["id"]) + "_unlocked")
			interact_obj(o)


func find_obj(id: String) -> Dictionary:
	for o in world().room["objects"]:
		if str(o.get("id", "")) == id:
			return o
	return {}


func craft(rid: String) -> void:
	var slots: Array = []
	var req: Dictionary = game.RECIPES[rid]["req"]
	for k in req:
		for i in range(int(req[k])):
			slots.append(k)
	var fire: bool = bool(game.RECIPES[rid].get("fire", false))
	check(game.match_recipe(slots, not fire) == "", "fogo errado não fabrica " + rid)
	var made: String = game.craft(slots, fire)
	check(made == rid, "fabricou " + rid)


func use_door(x_tile: int, expect_room: int) -> void:
	world().player.position = Vector2(float(x_tile + 1) * 32.0, 70.0)
	world()._process(0.016)
	await wait(1.2)
	check(game.cur_room == expect_room, "porta levou à sala %d (está na %d)" % [expect_room, game.cur_room])


func _run() -> void:
	await wait(0.5)
	check(main.state == "title", "abre no título")
	main._on_new_game()
	for i in range(0, 11):
		game.taken["seen_%d" % i] = true
	await wait(1.0)
	check(main.state == "play" and game.cur_room == 0, "novo jogo começa na gaiola (tutorial)")

	print("== Sala 0 (tutorial)")
	check(str(game.objective(0)["text"]).begins_with("Mova-se"), "objetivo 1 do tutorial")
	game.set_flag("t_moved")
	check(str(game.objective(0)["text"]).begins_with("Colete"), "objetivo 2: coletar frascos")
	collect_all()
	check(game.count("h") == 2 and game.count("o") == 3 and game.count("so") == 1, "frascos do tutorial")
	check(str(game.objective(0)["text"]).begins_with("Aperte I"), "objetivo 3: inventário")
	game.set_flag("t_inv")
	game.set_flag("t_bench")
	interact_obj(find_obj("r0_bars"))
	check(not game.flag("r0_open"), "grades não cedem sem ácido")
	craft("acido")
	check(game.count("acido") == 1, "ácido fabricado")
	interact_obj(find_obj("r0_bars"))
	check(game.flag("r0_open"), "ácido derreteu as grades")
	await use_door(14, 1)

	print("== Sala 1")
	var l2: Dictionary = find_obj("r1_l2")
	interact_obj(l2)
	check(main.puzzle.visible, "armário trancado abre o minigame")
	var order: Array = ["N", "a", "C", "l"]
	for ch in order:
		for tl in main.puzzle.tile_nodes:
			if tl.text == ch and not tl.used:
				main.puzzle._on_tile_click(tl)
				break
	await wait(1.6)
	check(game.flag("r1_l2_unlocked") and game.has("gel"), "NaCl destrancou o armário")
	collect_all()
	craft("chave_manut")
	interact_obj(find_obj("r1_panel"))
	check(game.flag("r1_open"), "painel abriu a porta")
	await use_door(23, 2)

	print("== Sala 2")
	check(find_obj("r2_l1").get("learn", []).size() == 1, "armário da receita do dispositivo térmico")
	collect_all()
	check(game.learned.has("termico"), "receita do térmico aprendida no armário")
	check(game.flag("r2_l2_unlocked"), "armário H2O (testado via flag)")
	craft("termico")
	interact_obj(find_obj("r2_ice"))
	check(game.flag("r2_melt"), "gelo derreteu")
	await use_door(26, 3)

	print("== Sala 3")
	var hz3 := 0
	for h in world().hazards:
		if h.kind == "electric":
			hz3 += 1
	check(hz3 == 11, "faixas elétricas ao redor dos 3 armários (os 2 de baixo também cobrem o topo)")
	var has_orbit := false
	for h in world().hazards:
		if h.kind == "orbit":
			has_orbit = true
	check(has_orbit, "raios orbitando a bancada")
	collect_all()
	check(game.learned.has("modulo_eletrico"), "receita do módulo elétrico no armário")
	craft("modulo_eletrico")
	interact_obj(find_obj("r3_panel"))
	check(game.flag("r3_power"), "energia restaurada")
	await use_door(14, 4)

	print("== Sala 4")
	var pz = null
	for h in world().hazards:
		if h.kind == "poison":
			pz = h
	check(pz != null, "veneno cobrindo o mapa")
	if pz != null:
		check(pz._in_safe(Vector2(5 * 32 + 16, 12 * 32)), "zona de início é segura")
		check(pz._in_safe(Vector2(5 * 32 + 16, 8 * 32)), "caminho de rato é seguro")
		check(not pz._in_safe(Vector2(14 * 32, 5 * 32)), "centro do mapa é tóxico")
		world().player.invuln = 0.0
		world().player.position = Vector2(14 * 32.0, 5 * 32.0 + 20.0)
		var hp0: int = game.hp
		pz._process(0.016)
		check(game.hp == hp0 - 1, "veneno causa dano fora das zonas seguras")
		game.hp = game.MAX_HP
		world().player.invuln = 0.0
		world().player.position = Vector2(5 * 32.0 + 16.0, 8 * 32.0)
		pz._process(0.016)
		check(game.hp == game.MAX_HP, "sem dano sobre o caminho de rato")
	collect_all()
	craft("filtro")
	interact_obj(find_obj("r4_cage"))
	check(not game.flag("r4_rescue"), "gaiola não abre com o veneno ativo")
	interact_obj(find_obj("r4_vent"))
	check(game.flag("r4_gas"), "gás neutralizado")
	interact_obj(find_obj("r4_cage"))
	check(game.flag("r4_rescue"), "rato resgatado")
	await use_door(26, 5)

	print("== Sala 5")
	var steams := 0
	var flames := 0
	for h in world().hazards:
		if h.kind == "steam":
			steams += 1
		elif h.kind == "flame":
			flames += 1
	check(steams == 4 and flames == 2, "4 válvulas de vapor e fogo decorativo na porta")
	collect_all()
	craft("agua")
	craft("solvente")
	interact_obj(find_obj("r5_crystal"))
	check(game.flag("r5_open"), "cristal dissolvido")
	await use_door(14, 6)

	print("== Sala 6")
	var dr6: Array = []
	for m in world().mobs:
		dr6.append(m)
	check(dr6.size() == 2 and dr6[0].chase, "2 drones perseguidores")
	world().player.invuln = 99.0
	world().player.position = Vector2(3 * 32.0, 12 * 32.0)
	var d0: float = dr6[0].position.distance_to(world().player.position)
	for i in range(60):
		dr6[0]._process(0.05)
	check(dr6[0].position.distance_to(world().player.position) < d0 - 40.0, "drone persegue o rato")
	world().player.position = Vector2(7 * 32.0, 4 * 32.0 + 20.0)
	check(dr6[0]._player_safe(), "zona da bancada protege do drone")
	collect_all()
	craft("modulo_contencao")
	interact_obj(find_obj("r6_laser_t"))
	check(game.flag("r6_laser"), "laser desligado")
	await use_door(26, 7)

	print("== Sala 7 (caixas e placas)")
	var cs: Array = world().crates
	check(cs.size() == 5 and world().plates.size() == 5, "5 caixas e 5 placas na sala")
	for c in cs:
		world().player.position = Vector2(c.position.x, c.position.y + 8.0)
		world().slide(world().player, Vector2(0, -140.0), 7.0, 10.0, true)
	check(game.flag("r7_shutter"), "placas de pressão ativaram o portão")
	world().reset_crates()
	check(is_equal_approx(cs[0].position.y, cs[0].start_pos.y), "R reinicia as caixas")
	collect_all()
	craft("disp_resgate")
	await use_door(14, 8)

	print("== Sala 8")
	var mu := 0
	for m in world().mobs:
		if m.kind == "mutant":
			mu += 1
	check(mu == 2, "2 monstros perseguidores")
	collect_all()
	interact_obj(find_obj("r8_c1"))
	interact_obj(find_obj("r8_c2"))
	check(game.flag("r8_free"), "dois ratos libertados")
	await use_door(14, 9)

	print("== Sala 9")
	var rb := 0
	for m in world().mobs:
		if m.kind == "drone" and m.chase:
			rb += 1
	check(rb == 3, "3 robôs perseguidores")
	collect_all()
	craft("chave_mestra")
	interact_obj(find_obj("r9_panel"))
	check(game.flag("r9_open"), "porta mestra aberta")
	await use_door(14, 10)

	print("== Sala 10 (final)")
	await wait(1.0)
	check(main.dlg.active, "Voss começa o discurso sozinho ao entrar")
	for i in range(30):
		await wait(0.25)
		if main.dlg.active:
			main.dlg._advance()
		if game.flag("r10_boss_talked"):
			break
	check(game.flag("r10_boss_talked"), "discurso termina e o Voss começa a atirar (sem precisar falar)")
	game.flags.erase("r10_boss_talked")   # pausa o tiroteio enquanto o teste fabrica e coleta
	game.hp = game.MAX_HP
	await wait(0.5)
	var lk := 0
	for o in world().room["objects"]:
		if str(o["type"]) == "locker":
			lk += 1
	check(lk == 5, "5 armários na sala do cientista")
	collect_all()
	check(game.learned.has("bomba"), "receita da bomba num dos armários")
	craft("modulo_contencao")
	craft("modulo_eletrico")
	craft("disp_resgate")
	craft("bomba")
	interact_obj(find_obj("r10_core"))
	check(not game.flag("r10_bomb"), "núcleo não aceita a bomba antes dos consoles")
	game.hp = game.MAX_HP
	game.set_flag("r10_boss_talked")
	await wait(2.8)
	var balls := 0
	for c in world().get_children():
		if "shots" in c:
			balls = c.shots
	check(balls >= 1, "Voss lança bolas de laser a cada 2 s")
	interact_obj(find_obj("r10_ca"))
	interact_obj(find_obj("r10_cb"))
	interact_obj(find_obj("r10_cc"))
	check(game.flag("r10_def") and game.flag("r10_evac") and game.flag("r10_free"), "3 consoles ativados")
	interact_obj(find_obj("r10_core"))
	check(game.flag("r10_bomb"), "bomba colocada no núcleo central")
	for i in range(120):
		await wait(0.3)
		if main.dlg.active:
			main.dlg._advance()
		if main.state == "ending":
			break
	check(main.state == "ending", "contagem, explosão e final exibidos")

	print("== Receitas inválidas e proteção")
	game.inv = {"h": 1, "fe": 1}
	check(game.craft(["h", "fe"]) == "", "combinação inválida não fabrica")
	check(game.count("h") == 1 and game.count("fe") == 1, "combinação inválida não consome")
	check(game.craft(["h"]) == "", "combinação incompleta não fabrica")
	game.add_item("gel", 1)
	check(game.recycle("gel") and game.count("agua") == 1 and game.count("polimero") == 1, "desmontar devolve componentes")

	print("== Bancada interativa (UI)")
	game.inv = {"fe": 1, "engrenagem": 2, "h": 2, "o": 1}
	main.craft.open()
	main.craft._add_to_vessel(0, "fe")
	main.craft._add_to_vessel(1, "engrenagem")
	main.craft._add_to_vessel(1, "engrenagem")
	check(main.craft.current_rid == "", "sem fogo, a chave não fecha")
	main.craft._add_to_vessel(0, "engrenagem")
	check(main.craft.vessels[0].item_id == "fe", "recipiente aceita só um tipo")
	main.craft._toggle_fire()
	check(main.craft.current_rid == "", "chama-piloto (nível 1) ainda não esquenta")
	main.craft._change_temp(1)
	check(main.craft.current_rid == "chave_manut", "com fogo, a chave é reconhecida")
	main.craft._on_craft()
	await wait(2.2)
	check(game.count("chave_manut") == 1 and game.count("fe") == 0 and game.count("engrenagem") == 0, "fabricou pela UI e consumiu")
	main.craft._add_to_vessel(0, "h")
	main.craft._add_to_vessel(0, "h")
	main.craft._add_to_vessel(1, "o")
	check(main.craft.current_rid == "agua", "água sem fogo pela UI")
	main.craft._toggle_fire()
	main.craft._change_temp(1)
	check(main.craft.current_rid == "", "água com fogo não fecha")
	main.craft._toggle_fire()
	main.craft._on_craft()
	await wait(1.6)
	check(game.count("agua") == 1, "água fabricada pela UI")
	main.craft.close()

	print("== Save / load")
	game.save_game()
	var before: Dictionary = game.inv.duplicate()
	game.inv = {}
	check(game.load_game() and game.inv == before, "save e load preservam o inventário")

	print("")
	print("RESULTADO: ", "TUDO OK" if fails == 0 else "%d FALHAS" % fails)
	quit(1 if fails > 0 else 0)
