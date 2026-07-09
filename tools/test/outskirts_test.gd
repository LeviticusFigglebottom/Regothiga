extends TestBase
## The Old Outskirts: the hill town builds in both states, the terraces
## climb on real stairs, the rowhouse interiors are enterable (door, wooden
## stair, upper room, balcony), the quay lantern and the ferry portal pair
## are wired, and the city panorama rings the district.

var area: Area
var player: Player

func _ready() -> void:
	_run.call_deferred()

func _floor_under(p: Vector3, area_ref: Area) -> float:
	var q := PhysicsRayQueryParameters3D.create(p + Vector3.UP * 0.5, p + Vector3.DOWN * 3.0, VG.M_WORLD_ALL)
	var hit := area_ref.get_world_3d().direct_space_state.intersect_ray(q)
	return hit["position"].y if not hit.is_empty() else -999.0

func _run() -> void:
	World.reset()
	area = AreaBuilder.build("old_outskirts")
	add_child(area)
	Game.register_area(area, "old_outskirts")
	StateDirector.snap(area, VG.WState.RUIN)
	player = Player.new()
	add_child(player)
	player.sim_active = true
	player.global_position = Vector3(0, 0.3, 8)
	await ticks(12)

	# ---- solid ground along the climb and inside the houses
	var route := [
		[Vector3(0, 0, 8), 0.0, "quay plaza"],
		[Vector3(-6, 0, -8), 0.0, "Fisher Lane"],
		[Vector3(-13, 0, -13), 0.0, "H2 ground room"],
		[Vector3(-11.5, 3, -14.5), 3.0, "H2 upper room"],
		[Vector3(-3, 0, -15), 0.0, "H3 ground room"],
		[Vector3(-1.5, 3, -16.5), 3.0, "H3 first floor"],
		[Vector3(-1.5, 6, -13.5), 6.0, "H3 top room"],
		[Vector3(0, 2.4, -26), 2.4, "Ropewalk Row"],
		[Vector3(-17, 2.4, -29), 2.4, "H5 ground room"],
		[Vector3(-16, 5.4, -30.5), 5.4, "H5 upper room"],
		[Vector3(0, 4.8, -40), 4.8, "the parish square"],
		[Vector3(-15, 4.8, -41), 4.8, "H8 ground room"],
		[Vector3(-13.4, 7.8, -42.6), 7.8, "H8 upper room"],
		[Vector3(-22.5, 3, -12), 3.0, "the corner house upstairs"],
		[Vector3(-32, 6, -11.5), 6.0, "the chandler-row gable room"],
		[Vector3(34.5, 3, -12.5), 3.0, "the wharf-row upper room"],
		[Vector3(-49, 0, -25), 0.0, "the chapel ruin floor"],
		[Vector3(-22, 7.8, -40), 7.8, "the square-west upper room"],
		[Vector3(12.5, 7.8, -39.5), 7.8, "the vestry-house upper room"],
		[Vector3(37, 0, -40), 0.0, "the back-row shell"],
	]
	for wp in route:
		var y := _floor_under(wp[0], area)
		check(absf(y - float(wp[1])) < 0.4, "floor under %s (y=%.2f)" % [wp[2], y])

	# ---- the terrace stairs climb for real
	player.global_position = Vector3(10, 0.3, -12)
	player.velocity = Vector3.ZERO
	await ticks(5)
	player.sim_move = Vector3(0, 0, -1)
	await ticks(160)
	player.sim_move = Vector3.ZERO
	await ticks(5)
	check(player.global_position.y > 2.2 and player.global_position.z < -18.5,
		"the lower stair gains Ropewalk Row (y=%.2f z=%.2f)" % [player.global_position.y, player.global_position.z])
	player.global_position = Vector3(-12, 2.7, -28)
	player.velocity = Vector3.ZERO
	await ticks(5)
	player.sim_move = Vector3(0, 0, -1)
	await ticks(160)
	player.sim_move = Vector3.ZERO
	await ticks(5)
	check(player.global_position.y > 4.6 and player.global_position.z < -34.5,
		"the upper stair gains the parish square (y=%.2f z=%.2f)" % [player.global_position.y, player.global_position.z])

	# ---- enter H2 through its lane door and climb the house stair
	player.global_position = Vector3(-11.5, 0.3, -8.4)
	player.velocity = Vector3.ZERO
	await ticks(5)
	player.sim_move = Vector3(0, 0, -1)
	await ticks(55)
	player.sim_move = Vector3.ZERO
	await ticks(5)
	print("    [leg] H2 entry -> %.2f %.2f %.2f" % [player.global_position.x,
			player.global_position.y, player.global_position.z])
	check(player.global_position.z < -10.4 and player.global_position.y < 1.0,
		"the lane door admits the Latecomer (z=%.2f)" % player.global_position.z)
	player.global_position = Vector3(-15.5, 0.3, -14.5)
	player.velocity = Vector3.ZERO
	await ticks(5)
	player.sim_move = Vector3(1, 0, 0)
	await ticks(75)
	player.sim_move = Vector3.ZERO
	await ticks(8)
	print("    [leg] H2 stair -> %.2f %.2f %.2f" % [player.global_position.x,
			player.global_position.y, player.global_position.z])
	check(player.global_position.y > 2.6,
		"the house stair reaches the upper room (y=%.2f x=%.2f)" % [player.global_position.y, player.global_position.x])
	# out the upper door onto the balcony over the lane
	player.global_position = Vector3(-14.5, 3.3, -11.5)
	player.velocity = Vector3.ZERO
	await ticks(5)
	player.sim_move = Vector3(0, 0, 1)
	await ticks(45)
	player.sim_move = Vector3.ZERO
	await ticks(8)
	print("    [leg] H2 balcony -> %.2f %.2f %.2f" % [player.global_position.x,
			player.global_position.y, player.global_position.z])
	check(player.global_position.z > -9.9 and player.global_position.y > 2.5,
		"the balcony holds over Fisher Lane (z=%.2f y=%.2f)" % [player.global_position.z, player.global_position.y])

	# ---- H3: two flights to the top room
	player.global_position = Vector3(-5.5, 0.3, -16.5)
	player.velocity = Vector3.ZERO
	await ticks(5)
	player.sim_move = Vector3(1, 0, 0)
	await ticks(75)
	player.sim_move = Vector3.ZERO
	await ticks(8)
	check(player.global_position.y > 2.6, "H3 first flight (y=%.2f)" % player.global_position.y)
	player.global_position = Vector3(-4.5, 3.35, -12.6)
	player.velocity = Vector3.ZERO
	await ticks(5)
	player.sim_move = Vector3(0, 0, -1)
	await ticks(75)
	player.sim_move = Vector3.ZERO
	await ticks(8)
	print("    [leg] H3 flight2 -> %.2f %.2f %.2f" % [player.global_position.x,
			player.global_position.y, player.global_position.z])
	check(player.global_position.y > 5.6, "H3 second flight tops out (y=%.2f)" % player.global_position.y)

	# ---- H5 and H8: the terrace houses' stairs climb for real
	player.global_position = Vector3(-19, 2.7, -30.5)
	player.velocity = Vector3.ZERO
	await ticks(5)
	player.sim_move = Vector3(1, 0, 0)
	await ticks(75)
	player.sim_move = Vector3.ZERO
	await ticks(8)
	print("    [leg] H5 stair -> %.2f %.2f %.2f" % [player.global_position.x,
			player.global_position.y, player.global_position.z])
	check(player.global_position.y > 5.0,
		"H5's stair reaches its upper room (y=%.2f)" % player.global_position.y)
	player.global_position = Vector3(-17, 5.1, -42.5)
	player.velocity = Vector3.ZERO
	await ticks(5)
	player.sim_move = Vector3(1, 0, 0)
	await ticks(75)
	player.sim_move = Vector3.ZERO
	await ticks(8)
	print("    [leg] H8 stair -> %.2f %.2f %.2f" % [player.global_position.x,
			player.global_position.y, player.global_position.z])
	check(player.global_position.y > 7.4,
		"H8's stair reaches its upper room (y=%.2f)" % player.global_position.y)

	# ---- the three graven words unbar the parish door
	var gate: FlagGate = null
	for n in area.base.get_children():
		if n is FlagGate:
			gate = n
	check(gate != null and gate.flag == "parish_words", "the parish door waits on the words")
	check(gate != null and not gate._unlocked(), "the door starts barred")
	var stones: Array = []
	for n in area.base.get_children():
		if n is WordStone:
			stones.append(n)
	check(stones.size() == 3, "three word-stones stand in the town (%d)" % stones.size())
	for s in stones:
		s._on_read(null)
	check(World.flag("word_wax") and World.flag("word_wick") and World.flag("word_flame"),
		"wax, wick and flame are all spoken")
	check(World.flag("parish_words"), "the three words unbar the parish")
	check(gate != null and gate._unlocked(), "the parish door stands open")

	# ---- wiring: lantern, portal pair, panorama on every horizon
	var lanterns := get_tree().get_nodes_in_group("lanterns")
	check(lanterns.size() >= 1, "the Quaylantern stands")
	var portal: AreaPortal = null
	for n in area.base.get_children():
		if n is AreaPortal:
			portal = n
	check(portal != null and portal.to_area == "drowned_marches", "the ferry poles back up the canal")
	var m := AreaBuilder.build("drowned_marches")
	add_child(m)
	var back: AreaPortal = null
	for n in m.base.get_children():
		if n is AreaPortal and n.to_area == "old_outskirts":
			back = n
	check(back != null, "the marches offer the ferry down")
	if back != null:
		var ly := _floor_under(back.spawn_pos, area)
		check(absf(ly - 0.0) < 0.4, "the ferry lands on the quay (y=%.2f)" % ly)
	m.queue_free()

	var pano_count := 0
	for n in area.base.get_children():
		if String(n.name).begins_with("city_panorama"):
			pano_count += 1
	check(pano_count == 1, "the city rings the district")

	# ---- both states build; the hollows haunt the ruin
	StateDirector.snap(area, VG.WState.GLORY)
	await ticks(5)
	StateDirector.snap(area, VG.WState.RUIN)
	await ticks(5)
	var foes := 0
	for n in get_tree().get_nodes_in_group(VG.GROUP_ENEMIES):
		foes += 1
	check(foes >= 6, "the outskirts keep their hollows (%d)" % foes)

	# ---- new kits resolve
	for kit in ["burg_wall_3m", "burg_wall_3m_door", "burg_wall_3m_win", "burg_floor_3m",
			"roof_gable_7m", "chimney_stack", "balcony_3m", "stair_wood_3m",
			"barrel", "crate_stack", "hand_cart", "burg_wall_3m_ruin_a",
			"burg_wall_3m_ruin_b", "parish_window_4m", "clock_tower", "word_stone"]:
		check(KitLib.instance(kit) != null, "kit %s resolves" % kit)

	finish()
