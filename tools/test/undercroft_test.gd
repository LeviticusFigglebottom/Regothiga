extends TestBase
## Ossuary Undercroft: three-way links, the Watchers puzzle, the Shroudbound
## tempo, and Bourdon the Bell-Ox.

var area: Area
var player: Player

func _ready() -> void:
	_run.call_deferred()

func _find(root: Node, klass) -> Array:
	var out: Array = []
	var stack: Array[Node] = [root]
	while not stack.is_empty():
		var n: Node = stack.pop_back()
		if is_instance_of(n, klass):
			out.append(n)
		for c in n.get_children():
			stack.append(c)
	return out

func _run() -> void:
	World.reset()
	area = AreaBuilder.build("ossuary_undercroft")
	add_child(area)
	Game.register_area(area, "ossuary_undercroft")
	player = Player.new()
	add_child(player)
	player.global_position = Vector3(-21, 2.8, 0)
	player.sim_active = true
	add_child(HUD.new())
	StateDirector.snap(area, VG.WState.RUIN)
	await ticks(25)

	print("== structure & links")
	check(area.base.get_child_count() > 100, "undercroft built (%d nodes)" % area.base.get_child_count())
	var tos := []
	for p in _find(area, AreaPortal):
		tos.append(p.to_area)
	check("gray_cloister" in tos and "basilica_nave" in tos, "stairs rise to both quarters %s" % [tos])
	check(Game.find_lantern("ossuary") != null, "ossuary lantern kept")

	print("== the grand stair joins the floors flush (no float, no drop-in gap)")
	player.global_position = Vector3(-21, 2.8, 0)   # on the west landing
	await ticks(10)
	check(absf(player.global_position.y - 2.4) < 0.4, "stands on the upper landing (y=%.2f)" % player.global_position.y)
	player.sim_move = Vector3(1, 0, 0)              # walk east, DOWN the stair
	await ticks(95)
	player.sim_move = Vector3.ZERO
	await ticks(12)
	check(player.global_position.x > -15.5, "descended into the hall (x=%.2f)" % player.global_position.x)
	check(absf(player.global_position.y) < 0.45, "met the lower floor flush — no drop (y=%.2f)" % player.global_position.y)
	var low_y := player.global_position.y
	player.sim_move = Vector3(-1, 0, 0)             # and climb back up
	await ticks(120)
	player.sim_move = Vector3.ZERO
	await ticks(12)
	check(player.global_position.y > low_y + 1.6, "climbed back up the stair (y=%.2f)" % player.global_position.y)

	print("== raised landings clear a standing figure (vault springs from THEIR floor)")
	var space := player.get_world_3d().direct_space_state
	for probe in [Vector3(22, 2.5, -4), Vector3(-22, 2.5, 0), Vector3(16, 2.5, 6)]:
		var ray := PhysicsRayQueryParameters3D.create(probe, probe + Vector3.UP * 6.0, VG.M_WORLD_ALL)
		var hit := space.intersect_ray(ray)
		var clear: float = (hit["position"].y - probe.y) if not hit.is_empty() else 6.0
		check(clear > 3.0, "landing at %s clears the ceiling (%.1f m)" % [probe, clear])

	print("== the watchers")
	var wps: Array = _find(area, WatcherPuzzle)
	check(wps.size() == 1, "watchers stand")
	var wp: WatcherPuzzle = wps[0]
	var gate: FlagGate = null
	for g in _find(area, FlagGate):
		if g.flag == "watchers_east":
			gate = g
	check(gate != null and not gate._open, "reliquary barred while they look away")
	# statues start at 0/90/180; east is -90 => turns needed: 3/2/1
	for turns in [[0, 3], [1, 2], [2, 1]]:
		for i in turns[1]:
			wp._turn(turns[0])
			await ticks(45)
	check(World.flag("watchers_east"), "all three face the owed morning")
	await ticks(10)
	check(gate._open, "the reliquary opened its teeth")

	print("== shroudbound: quick in the dark")
	var e := Enemy.new()
	e.setup("shroudbound")
	add_child(e)
	e.global_position = Vector3(-10, 0.2, 0)
	await ticks(5)
	check(e.cfg.get("speed", 0) > 4.0, "it remembers the shape of running")
	e.target = player
	e._begin_attack(e.cfg["attacks"][1])   # grave_lunge
	await ticks(40)
	check(e.state == e.ES.ATTACK or e.state == e.ES.COMBAT, "the lunge plays out")
	e._die()

	print("== Bourdon, the Bell-Ox")
	var boss: Enemy = null
	for en in get_tree().get_nodes_in_group(VG.GROUP_ENEMIES):
		if en.cfg.get("is_boss", false):
			boss = en
	check(boss != null and boss.cfg["name"].begins_with("Bourdon"), "he has not left the bell")
	if boss != null:
		boss.target = player
		boss.take_hit(DamagePacket.new(boss.max_hp * 0.55, 0.0, player))
		await ticks(5)
		check(boss.phase == 2, "half his patience brings the stampede")
		boss.take_hit(DamagePacket.new(99999.0, 0.0, player))
		await ticks(5)
		check(boss.dead, "the stall is quiet")

	finish()
