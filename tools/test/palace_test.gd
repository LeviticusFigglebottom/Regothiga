extends TestBase
## The Palace of the Hour: the great nave and its two wings, roofed end to
## end; the Carillon and the Hundred Candles unbar the Hour Gate together;
## the Scion's judgement opens the shortcut stairs; every road out leads
## where it says. No warden yet — the antechamber waits.

var area: Area
var player: Player

func _ready() -> void:
	_run.call_deferred()

func _floor_under(p: Vector3) -> float:
	var q := PhysicsRayQueryParameters3D.create(p + Vector3.UP * 0.5, p + Vector3.DOWN * 4.0, VG.M_WORLD_ALL)
	var hit := area.get_world_3d().direct_space_state.intersect_ray(q)
	return hit["position"].y if not hit.is_empty() else -999.0


func _run() -> void:
	World.reset()
	area = AreaBuilder.build("hour_palace")
	add_child(area)
	Game.register_area(area, "hour_palace")
	StateDirector.snap(area, VG.WState.GLORY)
	player = Player.new()
	add_child(player)
	player.sim_active = true
	player.global_position = Vector3(0, 0.3, 3)
	await ticks(12)

	# ---- floored and roofed across the house
	for wp in [[Vector3(0, 0, 3), "the threshold"], [Vector3(0, 0, 30), "the great nave"],
			[Vector3(18, 0, 16), "the chime court"], [Vector3(34, 0, 24), "the bell gallery"],
			[Vector3(18, 0, 34), "the reliquary"], [Vector3(-18, 0, 16), "the scriptorium"],
			[Vector3(-34, 0, 24), "the candle vault"], [Vector3(-18, 0, 34), "the waxworks"],
			[Vector3(0, 0, 65), "the antechamber"]]:
		check(_floor_under(wp[0]) > -1.0, "floor under %s" % wp[1])
	# roofs are visual (vault bays carry no trimesh by design); the def must
	# still vault every floored region — the auditor enforces cell coverage,
	# here we hold the field count so a dropped wing roof can't slip through
	var def2: Dictionary = area.get_meta("def")
	check(def2.get("vault_fields", []).size() == 10, "ten vault fields roof the house")

	# ---- the Hour Gate: barred until BOTH wing rites are done
	var gate: FlagGate = null
	for n in area.base.get_children():
		if n is FlagGate and (n as FlagGate).flag == "palace_gate_open":
			gate = n
	check(gate != null and not gate._unlocked(), "the Hour Gate starts barred")
	var space := area.get_world_3d().direct_space_state
	var rq := PhysicsRayQueryParameters3D.create(Vector3(0, 1.2, 52), Vector3(0, 1.2, 60), VG.M_WORLD_ALL)
	var rhit := space.intersect_ray(rq)
	check(not rhit.is_empty() and rhit["position"].z < 56.5, "and its bars stop the nave road")

	# ---- the Carillon: dawn, noon, dusk, midnight in the day's order
	var chime: ChimePuzzle = null
	for n in area.base.get_children():
		if n is ChimePuzzle:
			chime = n
	check(chime != null and chime.flag == "palace_hours", "the Carillon keeps the east wing")
	chime._ring("noon")
	check(not World.flag("palace_hours"), "a broken order rings nothing")
	for id in ["dawn", "noon", "dusk", "midnight"]:
		chime._ring(id)
	check(World.flag("palace_hours"), "the day rung true is the first rite")
	check(gate != null and not gate._unlocked(), "one rite alone moves nothing")

	# ---- the Hundred Candles
	var votive: VotiveLock = null
	for n in area.glory_layer.get_children():
		if n is VotiveLock:
			votive = n
	check(votive != null and votive.flag == "palace_candles", "five keepers' lights wait in the west")
	for i in votive._stands.size():
		votive._try_light(i)
	check(World.flag("palace_candles"), "the watch lit whole is the second")

	# ---- the seal joins them and the gate stands open
	await ticks(6)
	check(World.flag("palace_gate_open"), "both rites together unbar the Hour Gate")
	check(gate._unlocked(), "and the gate knows it")

	# ---- the Scion's judgement
	var herald: Node3D = null
	for n in area.base.get_children():
		if n is Node3D and n.get_script() != null \
				and String(n.get_script().resource_path).ends_with("scion_herald.gd"):
			herald = n
	check(herald != null, "the Scion waits at the threshold")
	herald.stage_now()
	await ticks(4)
	check(herald._staged, "and meets the first crossing")
	herald._line = 99
	herald._end()
	await ticks(4)
	check(World.flag("scion_heard"), "the judgement is spoken once")
	check(World.flag("palace_hostile"), "and the house is hostile after it")

	# ---- guards of the morning hold the rooms
	var guards := 0
	for n in area.glory_layer.get_children():
		if n is Spawner and (n as Spawner).enemy_id == "gilded_echo":
			guards += 1
	check(guards >= 8, "eight wards keep the wings and nave (%d)" % guards)

	# ---- every road out leads where it says
	var want := {"gilded_sanctum": 0, "basilica_porch": 0}
	for n in area.base.get_children():
		if n is AreaPortal:
			var t: String = (n as AreaPortal).to_area
			if want.has(t):
				want[t] += 1
	check(want["gilded_sanctum"] == 3, "the Door and both stairs descend to the Sanctum (%d)" % want["gilded_sanctum"])
	check(want["basilica_porch"] == 1, "the Lightwell drops all the way home")

	# ---- the Door of the Hour opens for the hour (sanctum side)
	World.reset()
	var sanctum := AreaBuilder.build("gilded_sanctum")
	add_child(sanctum)
	await ticks(5)
	var door: AreaPortal = null
	var stairs := 0
	for n in sanctum.base.get_children():
		if n is AreaPortal and (n as AreaPortal).to_area == "hour_palace":
			if (n as AreaPortal).locked_flag == "sanctum_hours":
				door = n
			elif (n as AreaPortal).locked_flag == "scion_heard":
				stairs += 1
	check(door != null and not door._unlocked(), "the Door keeps its hour until the Offices ring")
	World.set_flag("sanctum_hours")
	check(door._unlocked(), "and opens for it")
	check(stairs == 2, "both shortcut stairs wait on the Scion (%d)" % stairs)
	sanctum.queue_free()

	# ---- palace music is its own: the heavenly chorale
	check(area.env.music_for(VG.WState.GLORY).ends_with("theme_sanctum.mp3"),
			"the chorale keeps the palace")

	for kit in ["palace_wall_4x4", "palace_portal_4m", "palace_arcade_4m",
			"palace_pier", "chime_stone", "votive_stand_lit", "gate_iron"]:
		check(KitLib.instance(kit) != null, "kit %s resolves" % kit)

	finish()
