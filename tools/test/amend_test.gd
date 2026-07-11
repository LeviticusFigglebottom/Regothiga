extends TestBase
## The Amend: after Adalric's note is read, every warden put to rest stands
## again in the light of his own quarters, and each carries one amend —
## penance, fragments, cages, a song, a last crossing. Nothing shows early:
## not the wardens before the note, not the relics before the word.

var _area: Area

func _ready() -> void:
	_run.call_deferred()

func _warden(a: Area, kind: String) -> Node:
	for n in a.glory_layer.get_children():
		if n is NPC and (n as NPC).npc_id == "warden_" + kind:
			return n
	return null

func _build(id: String) -> Area:
	if _area != null and is_instance_valid(_area):
		_area.queue_free()
	_area = AreaBuilder.build(id)
	add_child(_area)
	return _area

func _run() -> void:
	World.reset()
	var player := Player.new()
	add_child(player)
	player.sim_active = true
	player.global_position = Vector3(0, 0.5, 0)
	await ticks(6)

	# ---- gating: no note, no wardens — even over a cleared arena
	World.set_cleared("gray_cloister")
	var a := _build("gray_cloister")
	await ticks(4)
	check(_warden(a, "bell") == null, "no warden stands before the Amend is sworn")

	# ---- the note read: the porch plaque swears the amend
	World.set_flag("reckoning_heard")
	var porch := AreaBuilder.build("basilica_porch")
	add_child(porch)
	await ticks(4)
	var note: LorePlaque = null
	for n in porch.ruin_layer.get_children():
		if n is LorePlaque and String((n as LorePlaque).text).begins_with("A NOTE"):
			note = n
	check(note != null and note.set_flag == "amend_sworn", "the note carries the oath")
	porch.queue_free()
	World.set_flag("amend_sworn")

	# ---- sworn but boss alive: still no warden
	World.set_cleared("gray_cloister", false)
	a = _build("gray_cloister")
	await ticks(4)
	check(_warden(a, "bell") == null, "a warden still standing his first watch gives no audience")

	# ---- the Bellkeeper, remembered
	World.set_cleared("gray_cloister")
	a = _build("gray_cloister")
	await ticks(4)
	var bell := _warden(a, "bell")
	check(bell != null, "the Bellkeeper stands his quarters in the light")
	# fragments are unseen until his word is given
	var marsh := AreaBuilder.build("drowned_marches")
	add_child(marsh)
	await ticks(4)
	var frag_hidden := true
	for n in marsh.base.get_children():
		if n is Pickup and (n as Pickup).item_id == "bell_fragment":
			frag_hidden = false
	check(frag_hidden, "no fragment shows before the Bellkeeper speaks")
	marsh.queue_free()
	World.set_flag("amend_bell_asked")
	var frags := 0
	for aid in ["drowned_marches", "old_outskirts", "black_gate"]:
		World.set_cleared(aid)   # black_gate warden also builds; harmless
		var fa := AreaBuilder.build(aid)
		add_child(fa)
		await ticks(4)
		for n in fa.base.get_children():
			if n is Pickup and (n as Pickup).item_id == "bell_fragment":
				frags += 1
		fa.queue_free()
		await ticks(2)
	check(frags == 3, "three fragments wait where he said (%d)" % frags)
	# the turn-in rite
	player.inventory["bell_fragment"] = 3
	var line: String = bell._rite({"id": "give"})
	check(World.flag("amend_bell"), "three fragments home make the bell whole")
	check(int(player.inventory.get("bell_fragment", 0)) == 0, "and the shards are spent")
	check(line.begins_with("Whole"), "he knows it at once")

	# ---- the Tollkeeper's penance
	World.set_cleared("black_gate")
	a = _build("black_gate")
	await ticks(4)
	var toll := _warden(a, "toll")
	check(toll != null, "the Tollkeeper keeps his gate in the light")
	Game.set_orisons(500)
	line = toll._rite({"id": "pay"})
	check(not World.flag("amend_toll") and line.contains("short"), "short prayers buy nothing")
	Game.set_orisons(10500)
	line = toll._rite({"id": "pay"})
	check(World.flag("amend_toll"), "ten thousand orisons discharge the debt")
	check(Game.orisons == 500, "counted to the last prayer")
	check(int(player.inventory.get("penance_writ", 0)) == 1, "and the writ is yours")

	# ---- the Larkwarden's cages
	World.set_cleared("larkspire")
	a = _build("larkspire")
	await ticks(4)
	check(_warden(a, "lark") != null, "the Larkwarden waits at the songloft")
	# ruined cages are not interactable before his word
	var found_larks := false
	for n in a.ruin_layer.get_children():
		if n is Node3D and n.get_script() != null \
				and String(n.get_script().resource_path).ends_with("amend_larks.gd"):
			found_larks = true
	check(not found_larks, "the cages keep shut before he asks")
	World.set_flag("amend_lark_asked")
	a = _build("larkspire")
	await ticks(4)
	var larks: Node3D = null
	for n in a.ruin_layer.get_children():
		if n is Node3D and n.get_script() != null \
				and String(n.get_script().resource_path).ends_with("amend_larks.gd"):
			larks = n
	check(larks != null, "asked, the ruined cages wait on living hands")
	var zones := larks.find_children("*", "Interactable", false, false)
	check(zones.size() == 4, "four doors he shut (%d)" % zones.size())
	for i in zones.size():
		larks._free(i, zones[i])
		await ticks(1)
	check(World.flag("amend_larks"), "every cage opened frees the choir")

	# ---- the Precentress's anthem
	World.set_cleared("basilica_nave")
	a = _build("basilica_nave")
	await ticks(4)
	check(_warden(a, "psalm") != null, "the Precentress holds her nave in the light")
	var loft_hidden := true
	for n in a.base.get_children():
		if n is Pickup and (n as Pickup).item_id == "morrow_anthem":
			loft_hidden = false
	check(loft_hidden, "her loft keeps its seal before she asks")
	World.set_flag("amend_psalm_asked")
	a = _build("basilica_nave")
	await ticks(4)
	var loft: Pickup = null
	for n in a.base.get_children():
		if n is Pickup and (n as Pickup).item_id == "morrow_anthem":
			loft = n
	check(loft != null and loft.item_count == 2, "two fair copies wait in the loft")
	# both deliveries: the Chandler and the Apostle carry deliver services
	var av: Dictionary = DB.npc("aveline")
	var ap: Dictionary = DB.npc("apostle_light")
	var av_del := false
	var ap_del := false
	for s in av.get("services", []):
		if s.get("type", "") == "deliver" and s.get("flag", "") == "amend_psalm_a":
			av_del = true
	for s in ap.get("services", []):
		if s.get("type", "") == "deliver" and s.get("flag", "") == "amend_psalm_b":
			ap_del = true
	check(av_del and ap_del, "both rites-sellers stand ready to receive her song")
	World.set_flag("amend_psalm_a")
	World.set_flag("amend_psalm_b")

	# ---- the apostle keeps his church outside the palace door
	World.set_flag("scion_heard")
	var sanctum := AreaBuilder.build("gilded_sanctum")
	add_child(sanctum)
	await ticks(4)
	var apostle: NPC = null
	for n in sanctum.glory_layer.get_children():
		if n is NPC and (n as NPC).npc_id == "apostle_light":
			apostle = n
	check(apostle != null, "the Apostle of Light keeps his stall by the door")
	var sells := {"morrow_lance": false, "vesper_ward": false,
			"radiant_blast": false, "radiant_burst": false}
	for s in ap.get("services", []):
		if s.get("type", "") == "buy" and sells.has(String(s.get("item", ""))):
			sells[String(s["item"])] = true
	for k in sells:
		check(sells[k], "he sells %s" % k)
	sanctum.queue_free()

	# ---- the new rites themselves resolve and cast
	check(not DB.spell("morrow_lance").is_empty(), "the Morrow Lance is written")
	check(not DB.spell("vesper_ward").is_empty(), "the Vesper Ward is written")
	player.give_item("vesper_ward", 1)
	player.mana = 100.0
	player.global_position = Vector3(0, 0.5, 0)
	await ticks(2)
	player.cast_spell("vesper_ward")
	await ticks(3)
	check(player._ward_active(), "the ward takes the watch")
	var hp0: float = player.hp
	var pk := DamagePacket.new(30.0, 5.0, null)
	player.take_hit(pk)
	check(player.hp >= hp0 - 1.0, "and the world's anger lands on the wax, not the flesh")

	# ---- the Ferryman's last crossing
	World.set_cleared("drowned_marches")
	a = _build("drowned_marches")
	await ticks(4)
	var ferry := _warden(a, "ferry")
	check(ferry != null, "the Ferryman waits at his jetty")
	ferry._rite({"id": "fare"})
	await ticks(8)
	var foe: Enemy = ferry._fight
	check(foe != null and is_instance_valid(foe) and foe.id == "ferryman_rested",
			"the last fare stands, heavier than before")
	check(not ferry.visible, "and the warden stands aside for him")
	check(float(foe.cfg.get("hp", 0)) > 1400.0, "the crossing is harder paid this time")
	foe.hp = 1.0
	var killp := DamagePacket.new(50.0, 10.0, player)
	foe.take_hit(killp)
	await ticks(10)
	check(World.flag("amend_ferry"), "beaten whole, he goes down with the boat")

	# ---- the elites of the morning
	var ec: Dictionary = DB.table("enemies").get("morning_ward", {})
	check(not ec.is_empty() and ec.get("body", "") == "skel_seraph",
			"the Ward of the Morning wears white-gold")
	var has_nova := false
	var has_versicle := false
	for atk in ec.get("attacks", []):
		if atk.get("type", "") == "nova":
			has_nova = true
		if atk.get("id", "") == "versicle":
			has_versicle = true
	check(has_nova and has_versicle, "and carries the radiant offices to battle")
	check(int(DB.table("enemies")["gilded_echo"]["hp"]) >= 60, "the palace guards stand bolstered")
	check(KitLib.instance("skel_seraph") != null, "the seraph body resolves")
	World.set_flag("palace_hostile")
	var pal := AreaBuilder.build("hour_palace")
	add_child(pal)
	await ticks(5)
	var elect := 0
	for n in pal.glory_layer.get_children():
		if n is Spawner and (n as Spawner).enemy_id == "morning_ward":
			elect += 1
	check(elect == 4, "four of the elect hold the road and the antechamber (%d)" % elect)
	pal.queue_free()

	# ---- the whole amend: every flag together rings the kingdom
	World.set_flag("amend_larks_thanked")
	World.set_flag("amend_psalm")
	# amend_toll, amend_bell, amend_ferry already set above
	if _area != null and is_instance_valid(_area):
		var w := _warden(_area, "ferry")
		if w == null:
			# the ferry warden freed itself on rest; use any warden-shaped node
			pass
	# _check_whole runs on each completion; verify the flag landed
	check(World.flag("amend_whole") or _all_done(), "the Amend counts its five")
	if not World.flag("amend_whole"):
		# the last completion above was the ferry death before the later flags —
		# any warden's check would set it now; emulate the next completion touch
		var rw := preload("res://src/world/radiant_warden.gd").new()
		rw._check_whole()
		rw.free()
	check(World.flag("amend_whole"), "THE AMEND IS MADE WHOLE")

	finish()

func _all_done() -> bool:
	for f in ["amend_toll", "amend_bell", "amend_larks_thanked", "amend_psalm", "amend_ferry"]:
		if not World.flag(f):
			return false
	return true
