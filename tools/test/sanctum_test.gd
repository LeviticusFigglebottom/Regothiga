extends TestBase
## The Gilded Sanctum: the lightfall's far side. Radiant by default and
## floored end to end; a rest-only vigil (the light does not falter); Ser
## Adalric in the radiant version, his note in the dim one; the Offices of
## the Hour and the Keepers' Candles unbar their doors; the way back down.

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
	area = AreaBuilder.build("gilded_sanctum")
	add_child(area)
	Game.register_area(area, "gilded_sanctum")
	StateDirector.snap(area, VG.WState.GLORY)
	player = Player.new()
	add_child(player)
	player.sim_active = true
	player.global_position = Vector3(0, 0.3, 27)
	await ticks(12)

	# ---- radiant by default, floored across the ward
	check(World.get_area_state("gilded_sanctum") == VG.WState.GLORY, "the sanctum stands radiant")
	for wp in [[Vector3(0, 0, 27), "the lightfall dais"], [Vector3(0, 0, 6), "the avenue"],
			[Vector3(15, 0, 7), "the east court"], [Vector3(-15, 0, 7), "the vigil garden"],
			[Vector3(0, 2.2, -16), "the palace terrace"]]:
		var y := _floor_under(wp[0])
		check(y > -1.0, "floor under %s (y=%.2f)" % [wp[1], y])
	# the terrace stair climbs
	check(_floor_under(Vector3(0, 2.2, -16)) > 1.5, "the Door of the Hour keeps its high terrace")

	# ---- the rest-only vigil
	var lantern := Game.find_lantern("sanctum")
	check(lantern != null, "the Unfaltering Vigil stands in the garden")
	var ui := RestUI.new(lantern, player)
	get_tree().root.add_child(ui)
	await ticks(3)
	var has_toggle := false
	var rest_label := ""
	for o in ui._options:
		if String(o["id"]) == "toggle":
			has_toggle = true
		if String(o["id"]) == "rest":
			rest_label = String(o["label"])
	check(not has_toggle, "the light here cannot be guttered")
	check("does not falter" in rest_label, "and the vigil says so")
	ui.close()
	await ticks(3)

	# ---- the only soul above the hours is the Apostle at his stall
	# (Adalric stays on the porch; the wardens keep their own quarters)
	var others := 0
	var apostle_here := false
	for layer in [area.glory_layer, area.ruin_layer, area.base]:
		for n in layer.get_children():
			if n is NPC:
				if (n as NPC).npc_id == "apostle_light":
					apostle_here = true
				else:
					others += 1
	check(apostle_here, "the Apostle of Light keeps his stall by the door")
	check(others == 0, "and no one else stands the court (%d)" % others)
	var note_found := false
	for n in area.ruin_layer.get_children():
		if n is LorePlaque and "AMEND" in (n as LorePlaque).text:
			note_found = true
	check(note_found, "the knight's note waits in the dim version")

	# ---- the Offices of the Hour: dawn, noon, dusk
	var chime: ChimePuzzle = null
	for n in area.base.get_children():
		if n is ChimePuzzle:
			chime = n
	check(chime != null and chime.flag == "sanctum_hours", "the Offices wait in the east court")
	var hours_gate: FlagGate = null
	var candle_gate: FlagGate = null
	for n in area.base.get_children():
		if n is FlagGate:
			if (n as FlagGate).flag == "sanctum_hours":
				hours_gate = n
			elif (n as FlagGate).flag == "sanctum_candles":
				candle_gate = n
	check(hours_gate != null and not hours_gate._unlocked(), "the reliquary starts barred")
	# the alcove is a sealed room: the gate is the only way in, and the tithe
	# sits beyond arm's reach of every outside surface
	var space := area.get_world_3d().direct_space_state
	var rq := PhysicsRayQueryParameters3D.create(Vector3(15.5, 0.9, 8), Vector3(21.5, 0.9, 8), VG.M_WORLD_ALL)
	var rhit := space.intersect_ray(rq)
	check(not rhit.is_empty() and rhit["position"].x < 18.6, "the barred gate stops the reliquary road")
	rq = PhysicsRayQueryParameters3D.create(Vector3(20, 0.9, 3), Vector3(20, 0.9, 9), VG.M_WORLD_ALL)
	rhit = space.intersect_ray(rq)
	check(not rhit.is_empty() and rhit["position"].z < 6.4, "the alcove walls hold from the court side")
	chime._ring("noon")
	check(not World.flag("sanctum_hours"), "a broken order rings nothing")
	chime._ring("dawn")
	chime._ring("noon")
	chime._ring("dusk")
	check(World.flag("sanctum_hours"), "dawn, noon and dusk unbar the reliquary")
	check(hours_gate._unlocked(), "and the gate stands open")
	await ticks(3)
	rq = PhysicsRayQueryParameters3D.create(Vector3(15.5, 0.9, 8), Vector3(21.5, 0.9, 8), VG.M_WORLD_ALL)
	rhit = space.intersect_ray(rq)
	check(rhit.is_empty() or rhit["position"].x > 18.6, "the open gate clears the way to the tithe")

	# ---- the Keepers' Candles
	var votive: VotiveLock = null
	for n in area.glory_layer.get_children():
		if n is VotiveLock:
			votive = n
	check(votive != null and votive.flag == "sanctum_candles", "four candles wait for the keepers")
	check(candle_gate != null and not candle_gate._unlocked(), "the chapel starts barred")
	for i in votive._stands.size():
		votive._try_light(i)
	check(World.flag("sanctum_candles"), "every candle kindled opens the chapel")

	# ---- the way back down
	var down: AreaPortal = null
	for n in area.base.get_children():
		if n is AreaPortal and (n as AreaPortal).to_area == "basilica_porch":
			down = n
	check(down != null, "the lightfall descends to the porch")

	# ---- and the way UP exists at the porch once the reckoning is heard
	World.set_flag("reckoning_heard")
	var porch := AreaBuilder.build("basilica_porch")
	add_child(porch)
	await ticks(5)
	var door_up: AreaPortal = null
	var stack: Array[Node] = [porch.base]
	while not stack.is_empty():
		var n: Node = stack.pop_back()
		if n is AreaPortal and (n as AreaPortal).to_area == "gilded_sanctum":
			door_up = n
		for c in n.get_children():
			stack.append(c)
	check(door_up != null and door_up.cutscene == "ascend", "the beacon offers the ascent")
	porch.queue_free()

	for kit in ["statue_orans", "chime_stone",
			"votive_stand_lit", "palace_wall_4x4", "palace_portal_4m", "palace_arcade_4m",
			"palace_floor_4x4", "palace_window_4m", "palace_balustrade_4m",
			"palace_pier", "gilt_finial", "palace_pediment_8m",
			"radiant_spire_a", "radiant_spire_b", "radiant_castle_a", "radiant_castle_b",
			"cloud_bank_a", "cloud_bank_b", "cloud_bank_c"]:
		check(KitLib.instance(kit) != null, "kit %s resolves" % kit)

	finish()
