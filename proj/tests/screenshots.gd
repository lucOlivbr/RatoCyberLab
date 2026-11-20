extends SceneTree
## Tira capturas de tela de várias situações do jogo (precisa de renderização, ex.: xvfb-run).
## Uso: xvfb-run -a godot --path <projeto> --script res://tests/screenshots.gd -- <pasta_saida>

var main
var game
var outdir: String = "/tmp/shots"


func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() > 0:
		outdir = args[0]
	DirAccess.make_dir_recursive_absolute(outdir)
	game = root.get_node("Game")
	var packed: PackedScene = load("res://scenes/main.tscn")
	main = packed.instantiate()
	root.add_child(main)
	_run()


func shot(name: String) -> void:
	await process_frame
	await process_frame
	var img := root.get_viewport().get_texture().get_image()
	img.save_png("%s/%s.png" % [outdir, name])
	print("shot ", name, " ", img.get_size())


func tp(o: Dictionary) -> void:
	var w: float = float(o.get("w", 1))
	var h: float = float(o.get("h", 1))
	if str(o["type"]) == "bench":
		w = 3.0
		h = 2.0
	main.world.player.position = Vector2((float(o["x"]) + w / 2.0) * 32.0, (float(o["y"]) + h) * 32.0 + 12.0)
	main.world.player.invuln = 5.0
	main.world._process(0.016)


func find(id: String) -> Dictionary:
	for o in main.world.room["objects"]:
		if str(o.get("id", "")) == id:
			return o
	return {}


func goto_room(n: int, spawn: String = "prev") -> void:
	main.change_room(n, spawn)
	await create_timer(1.0).timeout


func _run() -> void:
	await create_timer(0.6).timeout
	await shot("00_title")
	main._on_new_game()
	for k in range(6):
		await create_timer(1.0).timeout
		await shot("cut_%d" % k)
		main.cut._advance()
		await create_timer(0.1).timeout
		main.cut._advance()
	await create_timer(1.5).timeout
	for i in range(0, 11):
		game.taken["seen_%d" % i] = true
	await create_timer(1.2).timeout
	await shot("00b_room0")
	main.world.player.position = Vector2(14 * 32 + 16, 9 * 32)
	main.craft.open(true)
	main.craft._add_to_vessel(0, "fe") if false else null
	await shot("00c_bench_broken")
	main.craft.close()
	await goto_room(1)
	main.world.player.position = Vector2(14 * 32 + 16, 6 * 32 + 20)
	await shot("01_room1")
	game.set_flag("r1_l2_unlocked")
	for o in main.world.room["objects"]:
		if str(o["type"]) == "pickup" or str(o["type"]) == "locker":
			tp(o)
			main.world.try_interact()
	tp(find("r1_t1"))
	await shot("02_prompt_terminal")
	main.craft.open()
	var inv: Dictionary = game.inv
	main.craft._add_to_vessel(0, "fe")
	main.craft._add_to_vessel(1, "engrenagem")
	main.craft._add_to_vessel(1, "engrenagem")
	main.craft._toggle_fire()
	main.craft._change_temp(1)
	main.dlg.panel.visible = false
	await shot("03_craft_valid")
	main.craft._change_temp(1)
	await shot("03b_bench_hot")
	main.craft.close()
	main.invui.open()
	await shot("04_inventory")
	main.invui.close()
	for r in [2, 3, 4, 5, 6, 7, 8, 9, 10]:
		await goto_room(r)
		main.world.player.position = Vector2(14 * 32 + 16, 12 * 32)
		if r == 4:
			main.world.player.position = Vector2(5 * 32 + 16, 8 * 32)
		main.world.player.invuln = 99.0
		await create_timer(0.4).timeout
		await shot("room_%02d" % r)
	main.world.player.position = Vector2(14 * 32 + 16, 10 * 32)
	game.set_flag("r10_boss_talked")
	await create_timer(2.4).timeout
	await shot("room_10_b")
	main.talk(find("r10_boss"))
	await create_timer(0.8).timeout
	await shot("05_dialogue")
	for i in range(12):
		main.dlg._advance()
		await create_timer(0.05).timeout
	await create_timer(0.3).timeout
	await shot("06_choices")
	main.dlg.chosen.emit(0)
	for i in range(8):
		main.dlg._advance()
		await create_timer(0.05).timeout
	main.menus.show_end("Os alarmes se calam e as luzes de evacuação guiam os ratos pelos corredores. Um a um, os sujeitos aprisionados deixam o complexo.\n\nO Dr. Voss caiu junto com o seu império de experimentos. O Projeto R-31 chegou ao fim.\n\nR-31 olha para trás uma última vez, ao lado de todos os ratos que salvou.")
	await create_timer(1.6).timeout
	await shot("end")
	quit(0)
