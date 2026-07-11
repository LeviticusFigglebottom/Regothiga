extends Node3D
## The game proper: loads the save (or begins the pilgrimage), shows the
## title over the drifting kingdom, builds the chosen area, places the
## Latecomer, raises the HUD.

const TITLE := preload("res://src/ui/title_screen.gd")

func _ready() -> void:
	Game.world_root = self
	World.migrate_legacy_save()
	var fresh := true
	var area_id := "gray_cloister"
	var harnessed := false
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--area="):
			area_id = arg.get_slice("=", 1)
			harnessed = true

	var interactive := not harnessed and Shot.forced_state == "" \
			and not DisplayServer.get_name().contains("headless")

	# harness/headless runs keep the old single-load behaviour (slot 1)
	if not interactive:
		if not harnessed:
			fresh = not World.load_game()
			if not fresh and World.last_vigil.get("area", "") != "":
				area_id = World.last_vigil["area"]
		Game.set_difficulty(str(World.flag_val("difficulty", "vigil")))

	# the house card first, on every startup — new pilgrimage or load-in
	if interactive:
		var splash := SplashUI.new()
		add_child(splash)
		await splash.finished

	# the title stands between the house card and the kingdom. A first
	# launch (no vigil kept anywhere) weighs the dark before it; otherwise
	# the weighing waits inside New Journey — and Esc there, or Back on the
	# slot ledger, returns to the title with nothing forgotten. Only a
	# confirmed weighing wipes the chosen slot.
	var intro: IntroDirector = null
	if interactive:
		var preweighed := not World.any_slot()
		if preweighed:
			var sel := DifficultyUI.new()
			add_child(sel)
			Game.set_difficulty(await sel.chosen)
		var picked := false
		while not picked:
			var title := TITLE.new()
			title.has_save = World.any_slot()
			add_child(title)
			var pick = await title.done   # [choice, slot]
			title.queue_free()
			var choice: String = pick[0]
			var slot: int = pick[1]
			if choice == "resume":
				World.active_slot = slot
				if World.load_game():
					fresh = false
					if World.last_vigil.get("area", "") != "":
						area_id = World.last_vigil["area"]
					Game.set_difficulty(str(World.flag_val("difficulty", "vigil")))
				picked = true
			else:
				var diff := str(World.flag_val("difficulty", "vigil"))
				if not preweighed:
					var sel2 := DifficultyUI.new()
					sel2.cancellable = true
					add_child(sel2)
					diff = await sel2.chosen
					if diff == "":
						continue   # Esc: back to the title, nothing forgotten
				World.active_slot = slot
				World.reset()
				World.delete_slot(slot)
				Game.set_orisons(0)
				Game.set_difficulty(diff)
				fresh = true
				area_id = "gray_cloister"
				picked = true
		if fresh:
			intro = IntroDirector.new()
			add_child(intro)
			await intro.finished

	for f in Shot.forced_flags:
		World.set_flag(String(f))   # shot harness: flag-conditional geometry
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
		_mend_ledger(player)
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
	# every arrival gets the house's name writ large — new pilgrimage or
	# a vigil resumed
	Game.area_title.emit(area.display_name)

## Older ledgers wrote world flags without the pilgrim: a cache could stand
## consumed (took_...) while the item it gave was rolled back to the last
## rest. For the quest relics that BLOCK an amend, make the count whole.
func _mend_ledger(player) -> void:
	if World.area_flag("basilica_nave", "took_morrow_anthem_loft"):
		var owed := (0 if World.flag("amend_psalm_a") else 1) \
				+ (0 if World.flag("amend_psalm_b") else 1)
		if int(player.inventory.get("morrow_anthem", 0)) < owed:
			player.inventory["morrow_anthem"] = owed
		# holding her anthem IS her errand: a ledger that took the loft
		# without the asking flag (older gating) stays coherent
		if not World.flag("amend_psalm_asked"):
			World.set_flag("amend_psalm_asked")
	if not World.flag("amend_bell"):
		var taken := 0
		for spot in [["drowned_marches", "took_bell_fragment_marsh"],
				["black_gate", "took_bell_fragment_gate"],
				["old_outskirts", "took_bell_fragment_ruins"]]:
			if World.area_flag(spot[0], spot[1]):
				taken += 1
		if int(player.inventory.get("bell_fragment", 0)) < taken:
			player.inventory["bell_fragment"] = taken
