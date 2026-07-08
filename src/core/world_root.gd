extends Node3D
## The game proper: loads the save (or begins the pilgrimage), builds the
## current area, places the Latecomer, raises the HUD.

func _ready() -> void:
	Game.world_root = self
	var fresh := not World.load_game()

	var area_id := "gray_cloister"
	if not fresh and World.last_vigil.get("area", "") != "":
		area_id = World.last_vigil["area"]
	var harnessed := false
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--area="):
			area_id = arg.get_slice("=", 1)
			fresh = true
			harnessed = true

	# a fresh pilgrimage opens with the rite: story cards over the kingdom,
	# ending on the vigil-wave rolling across the porch city
	var intro: IntroDirector = null
	if fresh and not harnessed and Shot.forced_state == "" \
			and not DisplayServer.get_name().contains("headless"):
		intro = IntroDirector.new()
		add_child(intro)
		await intro.finished

	var area := AreaBuilder.build(area_id)
	add_child(area)
	Game.register_area(area, area_id)

	# state: saved state, or forced by the shot harness
	if Shot.forced_state != "":
		World.set_area_state(area_id, VG.state_from_name(Shot.forced_state))
	StateDirector.snap(area, World.get_area_state(area_id))

	var player := Player.new()
	player.name = "Player"
	add_child(player)
	if not fresh:
		player.from_save(World.player_data)
		Game.set_orisons(int(World.player_data.get("orisons", 0)))
	var def: Dictionary = area.get_meta("def")
	var spawn: Vector3 = AreaBuilder._v3(def.get("start", {}).get("pos", [0, 0.2, 0]))
	var lantern := Game.find_lantern(World.last_vigil.get("lantern", ""))
	if not fresh and lantern != null:
		spawn = lantern.respawn_point()
	player.global_position = spawn
	player.cam.yaw = deg_to_rad(float(def.get("start", {}).get("yaw", 0)))

	add_child(HUD.new())
	Game.refresh_remembrance()
	if intro != null:
		intro.reveal_and_free()
	if fresh:
		Game.toast.emit(area.display_name)
