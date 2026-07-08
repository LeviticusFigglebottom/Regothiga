extends TestBase
## The Drowned Marches: the causeway and peat flats are both real walkable
## ground, the drowned-sun override reaches the rig, the beacons must be
## kindled dawnward->midway->duskward to drop the jetty gate, the Ferryman
## binds/stands/falls/clears, the Mirebound rise for him in phase 2, and the
## postern pair with the Black Gate lands on floor both ways.

var area: Area
var player: Player

func _ready() -> void:
	_run.call_deferred()

func _floor_under(p: Vector3, a: Area) -> float:
	var q := PhysicsRayQueryParameters3D.create(p + Vector3.UP * 0.5, p + Vector3.DOWN * 4.0, VG.M_WORLD_ALL)
	var hit := a.get_world_3d().direct_space_state.intersect_ray(q)
	return hit["position"].y if not hit.is_empty() else -999.0

func _blocked(from: Vector3, to: Vector3, a: Area) -> bool:
	var q := PhysicsRayQueryParameters3D.create(from, to, VG.M_WORLD_ALL)
	return not a.get_world_3d().direct_space_state.intersect_ray(q).is_empty()

func _run() -> void:
	World.reset()
	area = AreaBuilder.build("drowned_marches")
	add_child(area)
	Game.register_area(area, "drowned_marches")
	StateDirector.snap(area, VG.WState.RUIN)
	player = Player.new()
	add_child(player)
	player.sim_active = true
	player.global_position = Vector3(21, 0.3, 0)
	await ticks(12)

	# ---- env override: the drowned sun hangs west
	check(absf(float(area.env._profile("glory")["sun_rot"][1]) - (-88.0)) < 0.1,
		"the drowned sun hangs in the west")
	check(area.env._profile("ruin")["sun_energy"] < 0.25, "ruin drowns the sun")

	# ---- ground truth: causeway, shelves, jetty, and the peat itself
	for wp in [[Vector3(21, 0, 0), 0.0, "entry landing"],
			[Vector3(0, 0, 0), 0.0, "the causeway"],
			[Vector3(2, 0, -6), 0.0, "south shelf"],
			[Vector3(-16, 0, 6), 0.0, "north shelf"],
			[Vector3(-26, 0, -6), 0.0, "beacon pad III"],
			[Vector3(-38, 0, 0), 0.0, "the jetty"],
			[Vector3(0, -2.2, 12), -2.2, "the peat flats"],
			[Vector3(-40, -2.2, -12), -2.2, "the far flats"]]:
		var y := _floor_under(wp[0], area)
		check(absf(y - float(wp[1])) < 0.35, "ground under %s (y=%.2f)" % [wp[2], y])

	# ---- the jetty gate bars the way until the beacons burn in order
	check(_blocked(Vector3(-31.4, 1.0, 0), Vector3(-32.6, 1.0, 0), area),
		"the jetty gate is shut while the beacons are cold")
	var puzzle: ChimePuzzle = null
	for n in area.base.get_children():
		if n is ChimePuzzle:
			puzzle = n
	check(puzzle != null, "the beacons stand ready")
	puzzle._ring("duskward")
	puzzle._ring("dawnward")
	puzzle._ring("midway")
	check(not World.flag("marches_beacons"), "kindling against the day does nothing")
	puzzle._ring("dawnward")
	puzzle._ring("midway")
	puzzle._ring("duskward")
	check(World.flag("marches_beacons"), "dawnward, midway, duskward lights the road")
	await ticks(30)
	var opened := true
	for n in area.base.get_children():
		if n is FlagGate and not n._open:
			opened = false
	check(opened, "the jetty gate sinks away")

	# ---- the Ferryman
	var fog: FogGate = null
	for n in area.ruin_layer.get_children():
		if n is FogGate:
			fog = n
	check(fog != null and fog.boss_spawner != null, "the jetty veil binds the Ferryman")
	var boss = fog.boss_spawner.current
	check(boss != null and boss.cfg.get("name", "") == "The Ferryman", "the Ferryman poles the flats")
	await ticks(60)
	check(boss.global_position.distance_to(Vector3(-38, 0, 0)) < 2.5, "he stands at the ferry stone")
	var undertow := false
	var tolls := false
	for a_ in boss.cfg["attacks"]:
		if a_.get("id", "") == "undertow" and a_.get("phase2_only", false):
			undertow = true
		if a_.get("type", "") == "summon" and a_.get("enemy", "") == "mirebound":
			tolls = true
	check(undertow and tolls, "phase 2 pulls the undertow and raises the Mirebound")
	fog._engage_boss()
	await ticks(3)
	boss.take_hit(DamagePacket.new(99999, 0, player))
	await ticks(30)
	check(boss.dead and World.is_cleared("drowned_marches"), "felling him clears the Marches")

	# ---- the Mirebound are real and heavy
	var mire: Dictionary = DB.enemy("mirebound")
	check(mire.get("body", "") == "skel_mire" and float(mire.get("poise", 0)) >= 60,
		"the Mirebound wear the marsh and refuse to stagger")

	# ---- postern pair lands on floor both ways
	var back: AreaPortal = null
	for n in area.base.get_children():
		if n is AreaPortal and n.to_area == "black_gate":
			back = n
	check(back != null, "the way back is the postern")
	var gate := AreaBuilder.build("black_gate")
	add_child(gate)
	var out: AreaPortal = null
	for n in gate.base.get_children():
		if n is AreaPortal and n.to_area == "drowned_marches":
			out = n
	check(out != null, "the Black Gate offers the marches")
	if out != null:
		var my := _floor_under(out.spawn_pos, area)
		check(absf(my - 0.0) < 0.35, "stepping out lands on the causeway (y=%.2f)" % my)
	if back != null:
		var gy := _floor_under(back.spawn_pos, gate)
		check(absf(gy - 0.0) < 0.35, "returning lands in the courtyard (y=%.2f)" % gy)

	for kit in ["reed_clump", "reed_clump_dead", "beacon_brazier", "waystone", "oar_glaive"]:
		check(KitLib.instance(kit) != null, "kit %s resolves" % kit)

	finish()
