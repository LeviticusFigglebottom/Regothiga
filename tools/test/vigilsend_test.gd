extends TestBase
## Vigil's End: the candle-dusk env override reaches the rig, jetty and
## processional and shrine crown are real floor (the shallows too), the
## Watchfires must be rekindled dusk->midnight->dawn to raise the shrine
## gate, the First Vigilant binds/stands/falls/clears, his phase 2 carries
## the last kindling and calls the watch, the ferry pair with the Drowned
## Marches is locked until the Ferryman rests, and every new kit resolves.

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
	area = AreaBuilder.build("vigils_end")
	add_child(area)
	Game.register_area(area, "vigils_end")
	StateDirector.snap(area, VG.WState.RUIN)
	player = Player.new()
	add_child(player)
	player.sim_active = true
	player.global_position = Vector3(22, 0.3, 0)
	await ticks(12)

	# ---- env override: candle-dusk west light reaches the rig
	check(absf(float(area.env._profile("glory")["sun_rot"][1]) - (-96.0)) < 0.1,
		"the last light hangs west of the isle")
	check(area.env._profile("ruin")["sun_energy"] < 0.2, "ruin all but drowns it")

	# ---- ground truth: jetty, processional, forecourt, crown, the shallows
	for wp in [[Vector3(22, 0, 0), 0.0, "the arrival jetty"],
			[Vector3(6, 0, 0), 0.0, "the processional"],
			[Vector3(-12, 0, 0), 0.0, "the shrine forecourt"],
			[Vector3(-24, 2.4, 0), 2.4, "the shrine crown"],
			[Vector3(0, -2.6, 12), -2.6, "the shallows"],
			[Vector3(-40, -2.6, -14), -2.6, "the far shallows"]]:
		var y := _floor_under(wp[0], area)
		check(absf(y - float(wp[1])) < 0.35, "floor under %s (y=%.2f)" % [wp[2], y])

	# ---- the shrine gate bars the stair until the watchfires burn in order
	check(_blocked(Vector3(-16.6, 3.4, 0), Vector3(-18.4, 3.4, 0), area),
		"the shrine gate is shut while the watchfires are cold")
	var puzzle: ChimePuzzle = null
	for n in area.base.get_children():
		if n is ChimePuzzle:
			puzzle = n
	check(puzzle != null, "the watchfires stand ready")
	puzzle._ring("dawn")
	puzzle._ring("midnight")
	puzzle._ring("dusk")
	check(not World.flag("vigil_watchfires"), "keeping the hours backwards does nothing")
	puzzle._ring("dusk")
	puzzle._ring("midnight")
	puzzle._ring("dawn")
	check(World.flag("vigil_watchfires"), "dusk, midnight, dawn keeps the night")
	await ticks(30)
	var opened := true
	for n in area.base.get_children():
		if n is FlagGate and not n._open:
			opened = false
	check(opened, "the shrine gate opens")

	# ---- the First Vigilant
	var fog: FogGate = null
	for n in area.ruin_layer.get_children():
		if n is FogGate:
			fog = n
	check(fog != null and fog.boss_spawner != null, "the firstlight veil binds the First Vigilant")
	var boss = fog.boss_spawner.current
	check(boss != null and boss.cfg.get("name", "") == "The First Vigilant",
		"the First Vigilant keeps his shift")
	await ticks(60)
	check(boss.global_position.distance_to(Vector3(-25.5, 2.4, 4.5)) < 2.5,
		"he stands his watch at the shrine")
	var kindling := false
	var calls := false
	for a_ in boss.cfg["attacks"]:
		if a_.get("id", "") == "last_kindling" and a_.get("phase2_only", false):
			kindling = true
		if a_.get("type", "") == "summon" and a_.get("enemy", "") == "lantern_wretch":
			calls = true
	check(kindling and calls, "phase 2 casts the last kindling and calls the watch")
	fog._engage_boss()
	await ticks(3)
	boss.take_hit(DamagePacket.new(99999, 0, player))
	await ticks(30)
	check(boss.dead and World.is_cleared("vigils_end"), "relieving him clears Vigil's End")

	# ---- the new foes are real
	var wr: Dictionary = DB.enemy("lantern_wretch")
	check(wr.get("body", "") == "skel_wretch" and wr.get("keep_range", 0.0) > 4.0,
		"the Lantern Wretch keeps its distance and casts flame")
	var hk: Dictionary = DB.enemy("vigilant_husk")
	check(hk.get("weapon", "") == "lantern_crook", "the Vigilant Husk carries the crook")

	# ---- ferry: the marches canal now runs to the Old Outskirts, owed the
	# Ferryman's rest AND the relics of the other wardens (plume + seal)
	var back: AreaPortal = null
	for n in area.base.get_children():
		if n is AreaPortal and n.to_area == "drowned_marches":
			back = n
	check(back != null, "the ferry waits to go back")
	var marsh := AreaBuilder.build("drowned_marches")
	add_child(marsh)
	var out: AreaPortal = null
	for n in marsh.base.get_children():
		if n is AreaPortal and n.to_area == "old_outskirts":
			out = n
	check(out != null, "the marches offer the canal down to the outskirts")
	if out != null:
		check(out.locked_flag == "cleared:drowned_marches", "the ferry needs the Ferryman at rest")
		check("lark_plume" in out.requires_items and "choir_seal" in out.requires_items,
			"and the relics of the spire and basilica wardens")
		check(out.cutscene == "ferry", "the crossing rides the waterworks")
		check(out._unlocked() == false, "and stays shut before all of it")
		var outs := AreaBuilder.build("old_outskirts")
		add_child(outs)
		var vy := _floor_under(out.spawn_pos, outs)
		check(absf(vy - 0.0) < 0.35, "crossing lands on the outskirts quay (y=%.2f)" % vy)
		outs.queue_free()
	if back != null:
		var my := _floor_under(back.spawn_pos, marsh)
		check(absf(my - 0.0) < 0.35, "returning lands on the marches jetty (y=%.2f)" % my)

	# ---- the vigil is safe ground (no camper within aggro of the lantern)
	var lant: VigilLantern = null
	for n in area.base.get_children():
		if n is VigilLantern:
			lant = n
	check(lant != null, "the Last Shore lantern stands")
	var camped := false
	for n in _spawners(area):
		var d2 := Vector2(n.global_position.x - lant.global_position.x,
				n.global_position.z - lant.global_position.z).length()
		if d2 < 9.0 and absf(n.global_position.y - lant.global_position.y) < 2.5:
			camped = true
	check(not camped, "no foe camps the vigil")

	for kit in ["vigil_brazier", "half_arch_sunk", "shrine_aedicule",
			"lantern_crook", "ferry_skiff", "skel_wretch"]:
		check(KitLib.instance(kit) != null, "kit %s resolves" % kit)

	finish()

func _spawners(a: Area) -> Array:
	var out: Array = []
	var stack: Array[Node] = [a]
	while not stack.is_empty():
		var n: Node = stack.pop_back()
		if n is Spawner:
			out.append(n)
		for c in n.get_children():
			stack.append(c)
	return out
