extends TestBase
## Gray Cloister integration: build from data, both-state routes, shortcut
## gate, NPC presence, pickups, vigil transition, portal lock.

var area: Area
var player: Player

func _ready() -> void:
	_run.call_deferred()

func _ray_hits(from: Vector3, to: Vector3) -> bool:
	var q := PhysicsRayQueryParameters3D.create(from, to, VG.M_WORLD_ALL)
	return not area.get_world_3d().direct_space_state.intersect_ray(q).is_empty()

func _run() -> void:
	World.reset()
	area = AreaBuilder.build("gray_cloister")
	add_child(area)
	Game.register_area(area, "gray_cloister")
	player = Player.new()
	add_child(player)
	player.global_position = Vector3(-18, 0.3, -2)
	player.sim_active = true
	add_child(HUD.new())
	StateDirector.snap(area, VG.WState.GLORY)
	await ticks(20)

	print("== structure")
	check(area.base.get_child_count() > 150, "base geometry built (%d nodes)" % area.base.get_child_count())
	check(area.nav_glory != null and area.nav_ruin != null, "both navmeshes baked")
	var lantern := Game.find_lantern("garth")
	check(lantern != null, "garth lantern present")
	var awake := get_tree().get_nodes_in_group(VG.GROUP_ENEMIES).filter(func(e): return e.can_process())
	check(awake.size() == 0, "no enemies awake in glory (layer disabled)")

	print("== state routes (glory)")
	check(_ray_hits(Vector3(-5.5, 1.2, -14), Vector3(-2.5, 1.2, -14)), "chapter-house east wall INTACT in glory")
	check(not _ray_hits(Vector3(-2, 1.0, -6.6), Vector3(-2, 1.0, -9.4)), "garth north portal CLEAR in glory")

	print("== the chandler, in glory")
	var npcs := []
	var stack: Array[Node] = [area.glory_layer]
	while not stack.is_empty():
		var n: Node = stack.pop_back()
		if n is NPC:
			npcs.append(n)
		for c in n.get_children():
			stack.append(c)
	check(npcs.size() == 1, "Aveline stands in the glory layer")

	print("== shortcut gate: barred south, opens north")
	player.global_position = Vector3(10, 0.3, 1.6)   # south side
	await ticks(4)
	var it := player.nearest_interactable()
	check(it != null and it.prompt.begins_with("Barred"), "south side is barred")
	player.global_position = Vector3(10, 0.3, -1.4)  # north side
	await ticks(4)
	it = player.nearest_interactable()
	check(it != null and it.prompt == "Unbar the gate", "north side offers to unbar")
	it.activate(player)
	await ticks(30)
	check(World.area_flag("gray_cloister", "gate_east_walk"), "gate flag persisted")

	print("== vigil at the garth: glory -> ruin, spectacle, spawns")
	player.global_position = lantern.respawn_point()
	await ticks(4)
	Game.vigil_flow(lantern, player)
	var waited := 0
	while not StateDirector.transitioning and waited < 300:
		waited += 5
		await ticks(5)
	check(StateDirector.transitioning, "transformation began after the kneel (%d ticks)" % waited)
	waited = 0
	while StateDirector.transitioning and waited < 1200:
		waited += 10
		await ticks(10)
	check(not StateDirector.transitioning, "transformation completed (%d ticks)" % waited)
	check(World.get_area_state("gray_cloister") == VG.WState.RUIN, "area now in ruin")
	await ticks(30)
	var foes := get_tree().get_nodes_in_group(VG.GROUP_ENEMIES).filter(func(e): return e.can_process() and not e.dead)
	check(foes.size() >= 10, "the ruin is populated (%d foes awake)" % foes.size())

	print("== state routes (ruin)")
	check(not _ray_hits(Vector3(-5.5, 1.2, -14), Vector3(-2.5, 1.2, -14)), "chapter-house wall FALLEN in ruin (bone garden opens)")
	check(_ray_hits(Vector3(-2, 1.0, -6.6), Vector3(-2, 1.0, -9.4)), "garth north portal CHOKED in ruin")

	print("== uncleared ruin cannot rekindle")
	player.global_position = lantern.respawn_point()
	await ticks(4)
	Game.vigil_flow(lantern, player)
	var flipped := false
	for i in 24:
		await ticks(10)
		flipped = flipped or StateDirector.transitioning
	check(not flipped, "no transformation (rest only)")
	check(World.get_area_state("gray_cloister") == VG.WState.RUIN, "still ruin — the warden endures")

	print("== tower door sealed before the warden rests")
	player.global_position = Vector3(26.2, 0.3, -10)
	await ticks(6)
	it = player.nearest_interactable()
	check(it != null and String(it.prompt).contains("shut"), "basilica door refuses (%s)" % (it.prompt if it else "none"))

	print("== candleglass pickup in the bone garden")
	player.global_position = Vector3(0.2, 0.3, -15.2)
	await ticks(6)
	check(player.try_interact(), "pried up the candleglass")
	check(int(player.inventory.get("candleglass", 0)) == 2, "2 candleglass held")

	finish()
