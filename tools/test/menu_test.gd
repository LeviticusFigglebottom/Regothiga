extends TestBase
## PauseUI regression: Esc menu opens/pauses/closes, settings reach the
## camera and the audio buses (and persist), and Begin Anew is a TRUE new
## game — save destroyed, world/flags/orisons forgotten — not a respawn.

var area: Area
var player: Player

func _ready() -> void:
	_run.call_deferred()

func _run() -> void:
	World.reset()
	area = AreaBuilder.build("gray_cloister")
	add_child(area)
	Game.register_area(area, "gray_cloister")
	player = Player.new()
	add_child(player)
	Game.register_player(player)
	player.global_position = Vector3(0, 0.3, 0)
	await ticks(5)

	# ---- open / pause / close
	check(not PauseUI.is_open(), "menu starts closed")
	PauseUI.open()
	await ticks(2)
	check(PauseUI.is_open(), "open() shows the menu")
	check(get_tree().paused, "world pauses behind the menu")
	PauseUI.close()
	await ticks(2)
	check(not PauseUI.is_open(), "close() hides the menu")
	check(not get_tree().paused, "world resumes on close")

	# ---- settings reach the camera + audio, and persist to disk
	PauseUI.settings["sensitivity"] = 8.0
	PauseUI.settings["fov"] = 74.0
	PauseUI._apply_camera()
	check(absf(player.cam.sensitivity - 8.0 * 0.0007) < 1e-6, "mouse sensitivity applies to the rig")
	check(absf(player.cam.cam.fov - 74.0) < 0.01, "field of view applies to the camera")
	PauseUI.settings["music"] = 0.25
	PauseUI._apply_audio()
	var mi := AudioServer.get_bus_index("Music")
	check(absf(AudioServer.get_bus_volume_db(mi) - linear_to_db(0.25)) < 0.01, "music volume reaches its bus")
	PauseUI._save_settings()
	check(FileAccess.file_exists(PauseUI.CFG_PATH), "settings persist to user://settings.cfg")

	# ---- Begin Anew: a true new game, not a respawn-in-place
	Game.set_orisons(777)
	World.set_flag("vesper_chimes")
	World.set_cleared("gray_cloister")
	World.last_vigil = {"area": "gray_cloister", "lantern": "porch"}
	World.save_game()
	check(FileAccess.file_exists(World.save_path()), "save exists before the reset")
	PauseUI.open()
	PauseUI.begin_anew(false)   # reload=false: reloading the scene would re-run this test
	await ticks(2)
	check(not FileAccess.file_exists(World.save_path()), "begin anew destroys the save file")
	check(Game.orisons == 0, "orisons are forgotten")
	check(not World.flag("vesper_chimes"), "story flags are forgotten")
	check(not World.is_cleared("gray_cloister"), "area clears are forgotten")
	check(World.last_vigil.get("area", "") == "", "the last vigil is forgotten")
	check(not PauseUI.is_open() and not get_tree().paused, "menu closes and the world unpauses")

	# fresh boot after the wipe finds the world in glory at the first area
	check(World.get_area_state("gray_cloister") == VG.WState.GLORY, "a new pilgrimage begins in glory")

	finish()
