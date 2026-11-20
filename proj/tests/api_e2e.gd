extends SceneTree
## Teste ponta a ponta: jogo (Godot) <-> backend (Python) <-> banco SQLite.
## Precisa do backend rodando:  RATO_API=http://127.0.0.1:8123 godot --headless --path . --script res://tests/api_e2e.gd
## Depois confira o banco com backend/tests/e2e_check.py.

var main
var game
var api
var fails: int = 0


func _initialize() -> void:
	game = root.get_node("Game")
	api = root.get_node("Api")
	_run()


func check(cond: bool, msg: String) -> void:
	if cond:
		print("  ok   - ", msg)
	else:
		print("  FAIL - ", msg)
		fails += 1


func wait(sec: float) -> void:
	await create_timer(sec).timeout


func _run() -> void:
	await wait(0.5)
	print("== Cadastro e login")
	var email := "e2e%d@rato.lab" % Time.get_ticks_msec()
	var err: String = await api.register("Jogador E2E", email, "senha123")
	check(err == "", "cadastro pelo jogo (%s)" % err)
	check(api.logged_in() and api.player_name() == "Jogador E2E", "jogador logado")
	var dup: String = await api.register("Outro", email, "senha123")
	check(dup != "", "e-mail repetido é recusado: " + dup)
	var bad: String = await api.login(email, "errada")
	check(bad != "", "senha errada é recusada: " + bad)

	print("== Novo jogo com conta")
	var packed: PackedScene = load("res://scenes/main.tscn")
	main = packed.instantiate()
	root.add_child(main)
	await wait(0.5)
	main._on_new_game()
	for i in range(0, 11):
		game.taken["seen_%d" % i] = true
	await wait(1.0)
	check(main.state == "play", "jogo iniciou")

	print("== Erros que vão para o relatório")
	var rooms: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/rooms.json"))
	var locker: Dictionary = {}
	for r in rooms["rooms"]:
		for o in r["objects"]:
			if str(o.get("id", "")) == "r1_l2":
				locker = o
	main.puzzle.open(locker)
	var wrong: Array = []
	for tl in main.puzzle.tile_nodes:
		if wrong.size() < main.puzzle.slot_nodes.size():
			wrong.append(tl)
	for tl in wrong:
		main.puzzle._on_tile_click(tl)
	await wait(0.3)
	main.puzzle.close()
	# se por acaso a ordem sorteada fosse a certa, forçamos um erro garantido
	api.report_error("FORMULA_ERRADA", game.cur_room, "reforço do teste")

	game.inv = {"h": 1, "fe": 1}
	main.craft.open()
	main.craft._add_to_vessel(0, "h")
	main.craft._add_to_vessel(1, "fe")
	await wait(0.2)
	check(main.craft.last_err_sig != "", "bancada reconheceu combinação inválida")
	main.craft.refresh()
	main.craft.refresh()   # repetir a mesma mistura não deve duplicar o erro
	main.craft.close()

	var p = main.world.player
	p.invuln = 0.0
	p.hurt(1, Vector2.ZERO, 0.0, "Veneno no ar")
	await wait(0.2)
	p.invuln = 0.0
	game.hp = 1
	p.hurt(1, Vector2.ZERO, 0.0, "Drone de segurança")
	await wait(1.5)

	print("== Progresso no banco")
	game.inv = {"h": 2, "o": 1}
	game.set_flag("t_moved")
	game.save_game()
	await wait(1.0)
	check(api.queue.is_empty(), "fila de erros enviada ao servidor")
	check(not api.pending_progress, "progresso gravado no banco")

	var sm: Dictionary = await api.fetch_summary()
	print("  resumo: ", sm)
	check(int(sm.get("FORMULA_ERRADA", 0)) >= 1, "relatório tem erro de fórmula")
	check(int(sm.get("RECEITA_INVALIDA", 0)) == 1, "relatório tem 1 erro de receita (sem duplicar)")
	check(int(sm.get("DANO", 0)) == 2, "relatório tem 2 danos")
	check(int(sm.get("MORTE", 0)) == 1, "relatório tem 1 recaptura")

	print("== Logout e novo login restauram o save do banco")
	game.inv = {}
	await api.logout()
	check(not api.logged_in(), "logout")
	err = await api.login(email, "senha123")
	check(err == "", "login de novo")
	check(game.has_save(), "save baixado do banco")
	check(game.load_game(), "load_game ok")
	check(game.count("h") == 2 and game.count("o") == 1, "inventário veio do banco")
	check(game.flag("t_moved"), "flag veio do banco")

	print("== Sem servidor: jogo segue funcionando")
	api.base_url = "http://127.0.0.1:1"
	api.report_error("DANO", 0, "offline")
	game.save_game()
	await wait(1.5)
	check(api.queue.size() == 1, "erro fica na fila quando o servidor cai")
	check(api.pending_progress, "progresso marcado como pendente")

	print("")
	if fails == 0:
		print("TODOS OS TESTES E2E PASSARAM")
	else:
		print("FALHAS: %d" % fails)
	quit(1 if fails > 0 else 0)
