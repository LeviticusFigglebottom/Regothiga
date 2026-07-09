extends TestBase
## The Larkspire: the tower builds in both states, the switchback climb is
## walkable floor all the way to the summit, the Daily Offices puzzle gates
## the loft (wrong order resets, right order opens), the Larkwarden binds to
## his fog gate and clears the area when felled, the Gilded Echo is the first
## GLORY-state hostile (live in glory, frozen in ruin), and the undercroft
## portal pair lands on real floor both ways.

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
	area = AreaBuilder.build("larkspire")
	add_child(area)
	Game.register_area(area, "larkspire")
	StateDirector.snap(area, VG.WState.RUIN)
	player = Player.new()
	add_child(player)
	player.sim_active = true
	player.global_position = Vector3(0, 0.3, 5)
	await ticks(12)

	# ---- the climb: every waypoint of the square spiral has solid floor
	var route := [
		[Vector3(0, 0, 5), 0.0, "base hall"],
		[Vector3(-6, 2.4, -6), 2.4, "NW landing"],
		[Vector3(6, 4.8, -6), 4.8, "ring 1 arrival (NE)"],
		[Vector3(-2, 4.8, -2), 4.8, "matins platform"],
		[Vector3(5, 7.2, 6), 7.2, "SE landing"],
		[Vector3(-6, 9.6, 6), 9.6, "ring 2 arrival (SW)"],
		[Vector3(2, 9.6, -2), 9.6, "sext platform"],
		[Vector3(-6, 12.0, -6), 12.0, "NW landing high"],
		[Vector3(6, 14.4, -6), 14.4, "ring 3 arrival (NE)"],
		[Vector3(2, 14.4, 2), 14.4, "vespers platform"],
		[Vector3(5, 16.8, 6), 16.8, "office-gate landing"],
		[Vector3(-5, 2.4, -2), 2.4, "first gallery walk"],
		[Vector3(5, 7.2, 2), 7.2, "hall-overlook gallery"],
		[Vector3(-2, 9.6, 5), 9.6, "sext-ring gallery"],
		[Vector3(-6, 19.2, 6), 19.2, "summit arrival (SW)"],
		[Vector3(0, 19.2, 2), 19.2, "the gated overlook"],
		[Vector3(0, 19.2, -4), 19.2, "the Larkwarden's arena"],
	]
	for wp in route:
		var y := _floor_under(wp[0], area)
		check(absf(y - float(wp[1])) < 0.35, "floor under %s (y=%.2f)" % [wp[2], y])

	# ---- walk the first full level for real: north up the west flight,
	# across the NW landing, east up the north flight onto ring 1
	player.global_position = Vector3(-7, 0.3, 2)
	await ticks(5)
	player.sim_move = Vector3(0, 0, -1)
	await ticks(150)
	player.sim_move = Vector3.ZERO
	await ticks(5)
	check(player.global_position.y > 2.1 and player.global_position.z < -3.5,
		"walked up the west flight (y=%.2f z=%.2f)" % [player.global_position.y, player.global_position.z])
	player.sim_move = Vector3(1, 0, 0)
	await ticks(230)
	player.sim_move = Vector3.ZERO
	await ticks(10)
	check(player.global_position.y > 4.5 and player.global_position.x > 3.5,
		"walked up the north flight to ring 1 (y=%.2f x=%.2f)" % [player.global_position.y, player.global_position.x])

	# ---- walk to each birdcage platform from its ring arrival, for real
	var legs := [
		[Vector3(6, 5.1, -4.55), [[Vector3(-1, 0, 0), 155], [Vector3(0, 0, 1), 30],
			[Vector3(1, 0, 0), 65]],
			Vector3(-1.5, 4.8, -2), "matins platform walk"],
		[Vector3(-6, 9.9, 4.55), [[Vector3(1, 0, 0), 88], [Vector3(1, 0, 0.5), 42],
			[Vector3(1, 0, 0), 45], [Vector3(0, 0, -1), 158], [Vector3(-1, 0, 0), 62],
			[Vector3(0, 0, 1), 55]],
			Vector3(2, 9.6, -1.5), "sext platform walk"],
		[Vector3(6, 14.7, -4.55), [[Vector3(-1, 0, 0), 155], [Vector3(0, 0, 1), 145],
			[Vector3(1, 0, 0), 110], [Vector3(0, 0, -1), 60]],
			Vector3(2, 14.4, 1.6), "vespers platform walk"],
	]
	for leg in legs:
		player.global_position = leg[0] + Vector3.UP * 0.3
		player.velocity = Vector3.ZERO
		await ticks(5)
		for seg in leg[1]:
			player.sim_move = seg[0]
			await ticks(seg[1])
			print("    [leg] %s seg -> %.2f %.2f %.2f" % [leg[3], player.global_position.x,
					player.global_position.y, player.global_position.z])
		player.sim_move = Vector3.ZERO
		await ticks(8)
		var goal: Vector3 = leg[2]
		var d: float = player.global_position.distance_to(goal)
		check(d < 2.6 and absf(player.global_position.y - goal.y) < 0.6,
			"%s reaches the cage (d=%.2f y=%.2f)" % [leg[3], d, player.global_position.y])

	# ---- the office gate seals the last flight while the offices are unsung
	player.global_position = Vector3(5, 17.0, 6.8)
	await ticks(5)
	player.sim_move = Vector3(-1, 0, 0)
	await ticks(110)
	player.sim_move = Vector3.ZERO
	await ticks(5)
	check(player.global_position.x > 0.5,
		"the unsung gate holds the landing (x=%.2f)" % player.global_position.x)

	# ---- once the offices are sung, the same walk crests the summit
	World.set_flag("daily_offices", true)
	var area2 := AreaBuilder.build("larkspire")
	add_child(area2)
	StateDirector.snap(area2, VG.WState.RUIN)
	area.queue_free()
	await ticks(10)
	player.global_position = Vector3(5, 17.0, 6.8)
	player.velocity = Vector3.ZERO
	await ticks(5)
	player.sim_move = Vector3(-1, 0, 0)
	await ticks(210)
	player.sim_move = Vector3.ZERO
	await ticks(8)
	check(player.global_position.y > 18.9 and player.global_position.x < -3.5,
		"the sung gate opens the last flight to the summit (y=%.2f x=%.2f)"
		% [player.global_position.y, player.global_position.x])
	World.set_flag("daily_offices", false)
	area2.queue_free()
	area = AreaBuilder.build("larkspire")
	add_child(area)
	Game.register_area(area, "larkspire")
	StateDirector.snap(area, VG.WState.RUIN)
	await ticks(10)

	# ---- Daily Offices: wrong order resets, right order sets the flag
	var puzzle: ChimePuzzle = null
	for n in area.base.get_children():
		if n is ChimePuzzle:
			puzzle = n
	check(puzzle != null, "the Daily Offices puzzle exists")
	check(not World.flag("daily_offices"), "offices start unsung")
	puzzle._ring("vespers")
	puzzle._ring("matins")
	puzzle._ring("sext")
	check(not World.flag("daily_offices"), "dusk before dawn does not open the loft")
	puzzle._ring("matins")
	puzzle._ring("sext")
	puzzle._ring("vespers")
	check(World.flag("daily_offices"), "matins, sext, vespers opens the loft")

	# ---- boss wiring: gate binds spawner; felling him clears the area
	var fog: FogGate = null
	for n in area.ruin_layer.get_children():
		if n is FogGate:
			fog = n
	check(fog != null and fog.boss_spawner != null, "songloft fog gate binds the Larkwarden's spawner")
	var boss = fog.boss_spawner.current
	check(boss != null and boss.cfg.get("name", "") == "The Larkwarden", "the Larkwarden waits at the summit")
	check(boss.cfg.get("is_boss", false), "he carries a boss bar")
	await ticks(60)
	var bp: Vector3 = boss.global_position
	check(bp.distance_to(Vector3(0, 19.2, -4)) < 2.5 and bp.y > 18.5,
		"he STANDS at his mark after a second (at %.1f,%.1f,%.1f)" % [bp.x, bp.y, bp.z])
	fog._engage_boss()
	await ticks(3)
	check(boss.target == player, "parting the pale engages him")
	boss.take_hit(DamagePacket.new(99999, 0, player))
	await ticks(30)
	check(boss.dead, "the Larkwarden can be felled")
	check(World.is_cleared("larkspire"), "his fall clears the spire")
	check(World.area_flag("larkspire", "slain_larkwarden"), "he does not return")

	# ---- the Gilded Echo: alive in GLORY, frozen in ruin
	var echoes: Array = []
	for n in area.glory_layer.get_children():
		if n is Spawner and n.enemy_id == "gilded_echo":
			echoes.append(n)
	check(echoes.size() == 2, "two Gilded Echoes haunt the remembered spire")
	check(echoes[0].current != null, "an echo stands ready")
	var echo = echoes[0].current
	check(echo.process_mode == Node.PROCESS_MODE_DISABLED or not echo.can_process(),
		"in ruin the echo is only a memory (frozen)")
	StateDirector.snap(area, VG.WState.GLORY)
	await ticks(5)
	check(echo.can_process(), "in glory the echo hunts")
	check(String(echo.cfg.get("body", "")) == "skel_echo", "it wears the gilded body")

	# ---- portal pair lands on floor both ways
	var down: AreaPortal = null
	for n in area.base.get_children():
		if n is AreaPortal:
			down = n
	check(down != null and down.to_area == "ossuary_undercroft", "the way down leads to the ossuary")
	var u := AreaBuilder.build("ossuary_undercroft")
	add_child(u)
	var up: AreaPortal = null
	for n in u.base.get_children():
		if n is AreaPortal and n.to_area == "larkspire":
			up = n
	check(up != null, "the ossuary offers the climb")
	if up != null:
		var ly := _floor_under(up.spawn_pos, area)
		check(absf(ly - 0.0) < 0.35, "climbing in lands on the spire's floor (y=%.2f)" % ly)
	if down != null:
		var uy := _floor_under(down.spawn_pos, u)
		check(absf(uy - 0.0) < 0.35, "descending lands on the ossuary's floor (y=%.2f)" % uy)

	# ---- new kits all resolve
	for kit in ["lark_cage", "lark_cage_dead", "cage_stand", "perch_rail",
			"perch_rail_bare", "great_perch", "aviary_screen", "crook_warden", "crook_great"]:
		check(KitLib.instance(kit) != null, "kit %s resolves" % kit)

	finish()
