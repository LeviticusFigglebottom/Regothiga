extends TestBase
## The Palace of the Hour: the great nave and its two wings, roofed end to
## end and doored at every mouth; the Bellman's Echo and the Unlit
## Procession unbar the Hour Gate together; the Scion's judgement meets the
## FIRST step across the threshold; the porch below remembers the reckoning.

var area: Area
var player: Player

func _ready() -> void:
	_run.call_deferred()

func _floor_under(p: Vector3) -> float:
	var q := PhysicsRayQueryParameters3D.create(p + Vector3.UP * 0.5, p + Vector3.DOWN * 4.0, VG.M_WORLD_ALL)
	var hit := area.get_world_3d().direct_space_state.intersect_ray(q)
	return hit["position"].y if not hit.is_empty() else -999.0

func _npc_ids(a: Area) -> Array:
	var out: Array = []
	for layer in [a.base, a.glory_layer, a.ruin_layer]:
		for n in layer.get_children():
			if n is NPC:
				out.append((n as NPC).npc_id)
	return out


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

	# ---- the Scion meets the FIRST crossing — no walk down the hall required
	var herald: Node3D = null
	for n in area.base.get_children():
		if n is Node3D and n.get_script() != null \
				and String(n.get_script().resource_path).ends_with("scion_herald.gd"):
			herald = n
	check(herald != null, "the Scion waits at the threshold")
	check(herald != null and float(herald.get("trigger_radius")) >= 6.5,
			"and his reach covers the door itself")
	check(herald != null and herald._staged, "the judgement begins the moment you enter")
	herald._line = 99
	herald._end()
	await ticks(6)
	check(World.flag("scion_heard"), "the judgement is spoken once")
	check(World.flag("palace_hostile"), "and the house is hostile after it")

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
	# 14 now: the nave runs 2 long vaults + 4 coffer-ring strips around its
	# crossing dome; the antechamber has NO fields at all (its whole
	# ceiling is the cove dome); the four wings keep their 8
	check(def2.get("vault_fields", []).size() == 14, "fourteen vault fields roof the house around its domes")
	var cove := false
	for pr in def2.get("props", []):
		if pr.get("kit", "") == "palace_cove_dome":
			cove = true
	check(cove, "and the antechamber's ceiling IS the cove dome")

	# ---- no mouth of the house lets you fall out of it
	var space := area.get_world_3d().direct_space_state
	var entry := space.intersect_ray(PhysicsRayQueryParameters3D.create(
			Vector3(0, 1.2, 2), Vector3(0, 1.2, -3), VG.M_WORLD_ALL))
	check(not entry.is_empty() and entry["position"].z > -1.0,
			"the entry keeps its door — the threshold cannot be fallen out of")
	for sx in [36.0, -36.0]:
		var stair := space.intersect_ray(PhysicsRayQueryParameters3D.create(
				Vector3(sx, 1.2, 38), Vector3(sx, 1.2, 43), VG.M_WORLD_ALL))
		check(not stair.is_empty() and stair["position"].z < 41.0,
				"the stair door at x=%d holds the gallery floor" % int(sx))

	# ---- the Hour Gate: barred until BOTH wing rites are done
	var gate: FlagGate = null
	for n in area.base.get_children():
		if n is FlagGate and (n as FlagGate).flag == "palace_gate_open":
			gate = n
	check(gate != null and not gate._unlocked(), "the Hour Gate starts barred")
	var rhit := space.intersect_ray(PhysicsRayQueryParameters3D.create(
			Vector3(0, 1.2, 52), Vector3(0, 1.2, 60), VG.M_WORLD_ALL))
	check(not rhit.is_empty() and rhit["position"].z < 56.5, "and its bars stop the nave road")

	# ---- the Bellman's Echo: hear her phrase, answer it in her order
	var bell: Node3D = null
	for n in area.base.get_children():
		if n is Node3D and n.get_script() != null \
				and String(n.get_script().resource_path).ends_with("echo_bell.gd"):
			bell = n
	check(bell != null and String(bell.get("flag")) == "palace_hours",
			"the mother bell keeps the east wing")
	bell._answer("dawn")
	check(not World.flag("palace_hours"), "answering unasked earns nothing — the phrase is hers")
	bell._demonstrate()
	var first_phrase: Array = (bell.get("_seq") as Array).duplicate()
	check(first_phrase.size() >= 3, "asked, she gives a phrase (%d offices)" % first_phrase.size())
	bell.set("_playing", false)
	bell._answer(String(first_phrase[(first_phrase.size() - 1)]))
	check(not World.flag("palace_hours") and (bell.get("_seq") as Array).is_empty(),
			"a sour note spends the phrase — she must be asked again")
	bell._demonstrate()
	var phrase: Array = (bell.get("_seq") as Array).duplicate()
	check(phrase != first_phrase, "and each asking may sing a different day")
	bell.set("_playing", false)
	for id in phrase:
		bell._answer(String(id))
	check(World.flag("palace_hours"), "the echo answered true is the first rite")
	check(gate != null and not gate._unlocked(), "one rite alone moves nothing")

	# ---- the Unlit Procession: each flame carries to both its neighbours
	var proc: Node3D = null
	for n in area.base.get_children():
		if n is Node3D and n.get_script() != null \
				and String(n.get_script().resource_path).ends_with("procession_lock.gd"):
			proc = n
	check(proc != null and String(proc.get("flag")) == "palace_candles",
			"the procession waits dark in the west")
	var lit0 := 0
	for v in (proc.get("_lit") as Array):
		if v:
			lit0 += 1
	check(lit0 == 0, "every stand starts unlit")
	proc._touch(0)
	var lit1 := 0
	for v in (proc.get("_lit") as Array):
		if v:
			lit1 += 1
	check(lit1 == 3, "one touch kindles a stand AND both its neighbours (%d)" % lit1)
	check(not World.flag("palace_candles"), "three flames are not the watch")
	var n_stands: int = (proc.get("_lit") as Array).size()
	for i in range(1, n_stands):
		proc._touch(i)
	check(World.flag("palace_candles"), "the ring walked once around burns whole — the second rite")

	# ---- the seal joins them and the gate stands open
	await ticks(6)
	check(World.flag("palace_gate_open"), "both rites together unbar the Hour Gate")
	check(gate._unlocked(), "and the gate knows it")

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
	check(want["basilica_porch"] == 0, "no road in the palace drops to the porch — the way home is the Door")

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
	await ticks(2)

	# ---- the porch below remembers the reckoning
	World.reset()
	var porch := AreaBuilder.build("basilica_porch")
	add_child(porch)
	await ticks(4)
	var before := _npc_ids(porch)
	check(before.has("knight_morrow") and not before.has("knight_morrow_grim"),
			"before the reckoning, Ser Adalric keeps his glad watch")
	porch.queue_free()
	await ticks(2)
	World.set_flag("reckoning_heard")
	var porch2 := AreaBuilder.build("basilica_porch")
	add_child(porch2)
	await ticks(4)
	var after := _npc_ids(porch2)
	check(after.has("knight_morrow_grim") and not after.has("knight_morrow"),
			"after it, a darker knight stands the same stones")
	var note := false
	for n in porch2.ruin_layer.get_children():
		if n is LorePlaque and String((n as LorePlaque).text).begins_with("A NOTE"):
			note = true
	check(note, "and when the light goes, only his note remains")
	porch2.queue_free()
	await ticks(2)

	# ---- the unlit saint hears prayers, and the Scion answers by the ledger
	var shrine: Node3D = null
	for n in area.base.get_children():
		if n is Node3D and n.get_script() != null \
				and String(n.get_script().resource_path).ends_with("pray_shrine.gd"):
			shrine = n
	check(shrine != null, "the unlit saint keeps the antechamber")
	check(shrine != null and shrine.find_children("*", "Interactable", false, false).size() == 1,
			"and offers the Pray hand")
	# every tier OPENS the way to the thirteenth bell; the wardens' amends
	# are graded as grace beside the road, never its toll
	var tu: Array = shrine._tier()
	check((tu[0] as Array).size() == 2 and String(tu[0][0]).contains("THIRTEENTH"),
			"unsworn, the way stands open all the same")
	check(String(tu[0][1]).contains("porch") and String(tu[0][1]).contains("ruin"),
			"and she points to the knight's letter — the porch, in ruin")
	World.set_flag("amend_sworn")
	var t0: Array = shrine._tier()
	check(String(t0[0][0]).contains("THIRTEENTH"), "sworn and unatoned, the way is open still")
	check(String(t0[0][1]).contains("grace beside it"),
			"and she names the wardens' grace, unearned")
	World.set_flag("amend_toll")
	World.set_flag("amend_bell")
	var t1: Array = shrine._tier()
	check(String(t1[0][0]).contains("THIRTEENTH"), "half-paid, the way is open still")
	check(String(t1[0][1]).contains("Finish what you began"),
			"and she marks the amends begun")
	World.set_flag("amend_larks_thanked")
	World.set_flag("amend_psalm")
	World.set_flag("amend_ferry")
	var t2: Array = shrine._tier()
	check(String(t2[0][0]).contains("amend made whole"), "amends whole, she is pleased")
	for f in ["amend_sworn", "amend_toll", "amend_bell", "amend_larks_thanked", "amend_psalm", "amend_ferry"]:
		World.set_flag(f, false)

	# ---- palace music is its own: the heavenly chorale
	check(area.env.music_for(VG.WState.GLORY).ends_with("theme_sanctum.mp3"),
			"the chorale keeps the palace")

	for kit in ["palace_wall_4x4", "palace_portal_4m", "palace_arcade_4m",
			"palace_pier", "chime_stone", "votive_stand_lit", "candle_cluster",
			"door_leaf", "wellhead", "gate_iron"]:
		check(KitLib.instance(kit) != null, "kit %s resolves" % kit)

	finish()
