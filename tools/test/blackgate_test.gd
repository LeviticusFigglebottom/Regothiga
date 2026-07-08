extends TestBase
## The Black Gate: drowned-sun env override reaches the rig, the approach and
## battlements are real floor, the portcullis BLOCKS until both capstans are
## turned (then rises), the Tollkeeper binds/stands/falls/clears behind his
## fog gate, the Drowned Herald summons the tollbound dead, the Gilded Echo
## walks the wall only in glory, and the porch portal pair lands on floor.

var area: Area
var player: Player

func _ready() -> void:
	_run.call_deferred()

func _floor_under(p: Vector3, a: Area) -> float:
	var q := PhysicsRayQueryParameters3D.create(p + Vector3.UP * 0.5, p + Vector3.DOWN * 3.0, VG.M_WORLD_ALL)
	var hit := a.get_world_3d().direct_space_state.intersect_ray(q)
	return hit["position"].y if not hit.is_empty() else -999.0

func _blocked(from: Vector3, to: Vector3, a: Area) -> bool:
	var q := PhysicsRayQueryParameters3D.create(from, to, VG.M_WORLD_ALL)
	return not a.get_world_3d().direct_space_state.intersect_ray(q).is_empty()

func _run() -> void:
	World.reset()
	area = AreaBuilder.build("black_gate")
	add_child(area)
	Game.register_area(area, "black_gate")
	StateDirector.snap(area, VG.WState.RUIN)
	player = Player.new()
	add_child(player)
	player.sim_active = true
	player.global_position = Vector3(0, 0.3, 20)
	await ticks(12)

	# ---- the drowned sun: the area's env override reaches the rig
	var g: Dictionary = area.env._profile("glory")
	check(absf(float(g["sun_color"][0]) - 0.92) < 0.001, "the drowned sun overrides glory's sun")
	check(area.env._profile("ruin")["sun_energy"] < 0.3, "the black sun dims ruin")
	area.env.snap(VG.WState.GLORY)
	check(area.env.sun.light_color.r > 0.85 and area.env.sun.light_color.g < 0.45,
		"snap paints the sun blood-red (r=%.2f g=%.2f)" % [area.env.sun.light_color.r, area.env.sun.light_color.g])

	# ---- floors: street, plaza, both battlement halves, courtyard
	for wp in [[Vector3(0, 0, 16), 0.0, "approach street"],
			[Vector3(0, 0, 0), 0.0, "gate plaza"],
			[Vector3(-10, 2.5, -3), 2.4, "west plaza flight (mid-seam)"],
			[Vector3(-7, 0, -12), 0.0, "west winch room"],
			[Vector3(-10, 4.8, -10), 4.8, "west stairhead deck"],
			[Vector3(0, 4.8, -10), 4.8, "battlement deck"],
			[Vector3(0, 0, -24), 0.0, "boss courtyard"]]:
		var y := _floor_under(wp[0], area)
		check(absf(y - float(wp[1])) < 0.35, "floor under %s (y=%.2f)" % [wp[2], y])

	# ---- the portcullis bars the passage until the capstans are turned
	check(_blocked(Vector3(0, 1.2, -8.4), Vector3(0, 1.2, -10.5), area),
		"the portcullis bars the passage")
	var puzzle: WatcherPuzzle = null
	for n in area.base.get_children():
		if n is WatcherPuzzle:
			puzzle = n
	check(puzzle != null, "the winch capstans exist")
	puzzle._turn(0)
	await ticks(45)
	check(not World.flag("black_gate_winched"), "one wheel alone does not raise the gate")
	# west wheel started at 90: with the probe turn above it has had one of its
	# three quarter-turns — two more bring it home; east started at 180: two
	for i in 2:
		puzzle._turn(0)
		await ticks(40)
	for i in 2:
		puzzle._turn(1)
		await ticks(40)
	await ticks(30)
	check(World.flag("black_gate_winched"), "both wheels to the chain raise the flag")
	await ticks(30)
	var gates_open := true
	for n in area.base.get_children():
		if n is FlagGate and not n._open:
			gates_open = false
	check(gates_open, "the portcullis climbs")

	# ---- the Tollkeeper behind his fog gate
	var fog: FogGate = null
	for n in area.ruin_layer.get_children():
		if n is FogGate:
			fog = n
	check(fog != null and fog.boss_spawner != null, "the blackgate fog gate binds the Tollkeeper")
	var boss = fog.boss_spawner.current
	check(boss != null and boss.cfg.get("name", "") == "The Tollkeeper", "the Tollkeeper waits in the courtyard")
	await ticks(60)
	check(boss.global_position.distance_to(Vector3(0, 0, -24)) < 2.5, "he stands at his mark")
	var rings := false
	var summons := false
	for a_ in boss.cfg["attacks"]:
		if a_.get("id", "") == "last_toll" and a_.get("phase2_only", false):
			rings = true
		if a_.get("type", "") == "summon" and a_.get("enemy", "") == "drowned_herald":
			summons = true
	check(rings and summons, "phase 2 carries the last toll and the herald's call")
	fog._engage_boss()
	await ticks(3)
	boss.take_hit(DamagePacket.new(99999, 0, player))
	await ticks(30)
	check(boss.dead and World.is_cleared("black_gate"), "felling him clears the Black Gate")
	await ticks(10)
	check(not _blocked(Vector3(0, 1.2, -13.6), Vector3(0, 1.2, -16.4), area),
		"the breach in the Black Gate is walkable once the toll is settled")

	# ---- the herald tolls the dead
	var herald_cfg: Dictionary = DB.enemy("drowned_herald")
	var tolls := false
	for a_ in herald_cfg["attacks"]:
		if a_.get("type", "") == "summon" and a_.get("enemy", "") == "shroudbound":
			tolls = true
	check(tolls, "the Drowned Herald tolls the shroudbound up")

	# ---- the Gilded Echo walks the wall only in glory
	var echo: Enemy = null
	for n in area.glory_layer.get_children():
		if n is Spawner and n.enemy_id == "gilded_echo":
			echo = n.current
	check(echo != null, "an echo haunts the battlements")
	check(not echo.can_process(), "in ruin it is only a memory")
	StateDirector.snap(area, VG.WState.GLORY)
	await ticks(5)
	check(echo.can_process(), "in glory it hunts the wall")

	# ---- portal pair lands on floor both ways
	var up: AreaPortal = null
	for n in area.base.get_children():
		if n is AreaPortal and n.to_area == "basilica_porch":
			up = n
	check(up != null, "the pilgrim stair leads home")
	var porch := AreaBuilder.build("basilica_porch")
	add_child(porch)
	var down: AreaPortal = null
	for n in porch.base.get_children():
		if n is AreaPortal and n.to_area == "black_gate":
			down = n
	check(down != null, "the porch offers the descent")
	if down != null:
		var by := _floor_under(down.spawn_pos, area)
		check(absf(by - 0.0) < 0.35, "descending lands on the gate road (y=%.2f)" % by)
	if up != null:
		var py := _floor_under(up.spawn_pos, porch)
		check(absf(py - (-5.02)) < 0.35, "climbing home lands at the pilgrim stair foot (y=%.2f)" % py)

	for kit in ["portcullis_4m", "gate_black", "capstan_base", "capstan_bars",
			"battlement_4m", "toll_maul"]:
		check(KitLib.instance(kit) != null, "kit %s resolves" % kit)

	finish()
