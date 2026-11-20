extends SceneTree
## Captura o rato correndo em 4 direções e andando (para conferir orientação).
var main
func _initialize() -> void:
	var game = root.get_node("Game")
	main = load("res://scenes/main.tscn").instantiate()
	root.add_child(main)
	_run(game)
func _run(game) -> void:
	await create_timer(0.5).timeout
	skip(game)
	await create_timer(1.5).timeout
	var p = main.world.player
	p.position = Vector2(480, 300)
	p.set_process(false)
	var i := 0
	for f in [Vector2.UP, Vector2.DOWN, Vector2.LEFT, Vector2.RIGHT]:
		for running in [true, false]:
			p.facing = f
			p.moving = true
			p._animate(0.1, running)
			await process_frame
			await process_frame
			var img := root.get_viewport().get_texture().get_image()
			var c := img.get_region(Rect2i(int(480 * img.get_width() / 960.0) - 60, int(300 * img.get_height() / 540.0) - 90, 120, 110))
			c.save_png("/tmp/dir_%d.png" % i)
			i += 1
	quit(0)
func skip(game) -> void:
	main.skip_cutscene = true
	main._on_new_game()
	for k in range(0, 11):
		game.taken["seen_%d" % k] = true
