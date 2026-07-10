extends TestBase
## The Parish of the First Wick: radiant by default with its praying dead,
## the Prior teaches the rites (mana bar wakes, heal/blast/burst all spend
## and strike), his meeting opens the lantern room, the first gutter stages
## the Immortalized's walk and address, and his half-wax rite turns the
## church radiant around a black-armored, gold-bladed second phase.

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
	area = AreaBuilder.build("wick_cathedral")
	add_child(area)
	Game.register_area(area, "wick_cathedral")
	StateDirector.snap(area, VG.WState.GLORY)
	player = Player.new()
	add_child(player)
	player.sim_active = true
	player.global_position = Vector3(0, 0.3, -2)
	await ticks(12)

	# ---- radiant by default, floored end to end
	check(World.get_area_state("wick_cathedral") == VG.WState.GLORY, "the parish defaults radiant")
	for wp in [[Vector3(0, 0, -2), "the narthex"], [Vector3(0, 0, -20), "the nave"],
			[Vector3(-6.5, 0, -20), "the north aisle"], [Vector3(0, 0, -34), "the chancel"],
			[Vector3(0, 0, -43), "the lantern room"]]:
		var y := _floor_under(wp[0], area)
		check(absf(y) < 0.35, "floor under %s (y=%.2f)" % [wp[1], y])

	# ---- the congregation
	var npcs := 0
	var prior: NPC = null
	for n in area.glory_layer.get_children():
		if n is NPC:
			npcs += 1
			if (n as NPC).npc_id == "wick_prior":
				prior = n
	check(npcs == 5, "the Prior and four waxbound pray here (%d)" % npcs)
	check(prior != null, "Prior Anselm stands at the chancel")

	# ---- the back room waits on his word
	var gate: FlagGate = null
	for n in area.base.get_children():
		if n is FlagGate:
			gate = n
	check(gate != null and not gate._unlocked(), "the lantern room starts sealed")
	World.set_flag("met_wick_prior")
	check(gate._unlocked(), "meeting the Prior opens the lantern room")

	# ---- the rites: mana wakes with the first spell
	check(player.max_mana == 0.0, "no rite, no wick-bar")
	player.give_item("mend")
	check(player.max_mana > 0.0, "learning Mend kindles the wick-bar")
	check(player.attuned_spell == "mend", "Mend attunes itself to X")
	# attune a different rite and confirm C would cast it
	player.give_item("radiant_blast")
	player.attune_spell("radiant_blast")
	check(player.attuned_spell == "radiant_blast", "the Rites tab re-attunes to X")
	player.attune_spell("mend")
	player.mana = player.max_mana
	player.hp = player.max_hp * 0.4
	player.cast_spell("mend")
	check(player.hp > player.max_hp * 0.6, "Mend closes the wound (hp=%.0f/%.0f)" % [player.hp, player.max_hp])
	check(player.mana < player.max_mana, "Mend spends the wick")
	player.give_item("radiant_blast")
	player.mana = player.max_mana
	player._cast_cd = 0.0
	player.cast_spell("radiant_blast")
	check(player.mana <= player.max_mana - 20.0, "the Blast spends the wick")
	var pen := Enemy.new()
	pen.setup("penitent")
	add_child(pen)
	pen.global_position = player.global_position + Vector3(2.5, 0, 0)
	await ticks(5)
	var php := pen.hp
	player.give_item("radiant_burst")
	player.mana = player.max_mana
	player._cast_cd = 0.0
	player.cast_spell("radiant_burst")
	await ticks(3)
	check(pen.hp < php, "the Burst scorches what stands near (%.0f -> %.0f)" % [php, pen.hp])
	pen.queue_free()
	player.mana = 0.0
	player.heal_full()
	check(player.mana == player.max_mana, "rest rekindles the wick")

	# ---- the gutter: his walk, his address, his veil
	var fog: FogGate = null
	for n in area.ruin_layer.get_children():
		if n is FogGate:
			fog = n
	check(fog != null and fog.boss_spawner != null, "the veil binds the Immortalized")
	var glyphs := 0
	for n in area.ruin_layer.get_children():
		if n is SummonGlyph:
			glyphs += 1
	check(glyphs == 0, "no summoning sign — this duel admits no phantom")
	StateDirector.snap(area, VG.WState.RUIN)
	player.global_position = Vector3(0, 0.3, -39.5)
	await ticks(10)
	check(fog.intercept != null, "the reveal owns the veil's first parting")
	fog._on_enter(player)
	await ticks(60)
	check(player.global_position.z > -37.5,
		"parting the pale steps INTO the nave (z=%.2f)" % player.global_position.z)
	check(World.area_flag("wick_cathedral", "met_crusader"), "the first parting stages his entrance")
	var boss = fog.boss_spawner.current
	check(boss != null and boss.cfg.get("name", "") == "The Immortalized", "the Immortalized answers")
	await ticks(90)
	check(boss.global_position.z < -4.0, "he walks the nave (z=%.2f)" % boss.global_position.z)
	var reveal: WickReveal = null
	for n in area.base.get_children():
		if n is WickReveal:
			reveal = n
	check(reveal != null, "the reveal owns the parish's turn")
	reveal.finish(fog, player)
	await ticks(5)
	check(boss.target == player, "the address ends and the duel begins")
	check(Game.arena_locked, "the duel bars the doors")
	var aux_up := false
	for w in fog._aux_walls:
		if (w as StaticBody3D).collision_layer != 0:
			aux_up = true
	check(aux_up, "a pale seal stands across the narthex at your back")

	# ---- his edge is the hitbox: the volume rides the sword, so a blade
	# short of you is no hit at all
	check(boss.blade_hitbox != null, "his sword carries its own hit volume")
	for a2 in boss.cfg["attacks"]:
		boss._cooldowns[a2["id"]] = 99.0   # stage-manage: his own AI swings nothing
	var cut: Dictionary = {}
	for a2 in boss.cfg["attacks"]:
		if a2["id"] == "cut_pair":
			cut = (a2 as Dictionary).duplicate()
	cut["lunge"] = 0.0   # measure the blade, not the stride
	player.heal_full()
	boss.global_position = Vector3(0, 0.3, -12)
	boss.velocity = Vector3.ZERO
	boss.vis.rotation.y = 0.0
	player.global_position = Vector3(0, 0.3, -15.1)   # 3.1 m: beyond the steel
	var hp_dry := player.hp
	boss._begin_attack(cut)
	await ticks(80)
	check(player.hp >= hp_dry - 0.01, "a swing that never crosses you never hits (hp %.0f)" % player.hp)
	boss.global_position = Vector3(0, 0.3, -12)
	boss.velocity = Vector3.ZERO
	boss.vis.rotation.y = 0.0
	player.global_position = Vector3(0, 0.3, -13.5)   # 1.5 m: in the sweep
	boss._begin_attack(cut)
	await ticks(29)   # ~0.48 s: inside the active window
	check(boss.blade_hitbox.monitoring and not boss.hitbox.monitoring,
		"the swing opens the steel itself, not a box off his chest")
	await ticks(51)
	check(player.hp < hp_dry, "and the same cut bites when it truly crosses you")
	player.heal_full()

	# ---- the mirror can be read: a true parry opens HIM, and the riposte
	# bites its full crit even through a raised guard
	await ticks(20)
	boss.on_parried(player)
	check(boss.state == Enemy.ES.STAGGER, "a true parry staggers even the Immortalized")
	check(player._riposte_target == boss, "and primes the riposte")
	boss._block_t = 0.9
	player.global_position = boss.global_position + Vector3(0, 0, 1.4)
	var bhp0: float = boss.hp
	check(player.try_riposte(), "the riposte answers within the breath")
	await ticks(40)
	check(boss.hp < bhp0 - 60.0, "the riposte bites its full crit, guard or no guard (%.0f -> %.0f)" % [bhp0, boss.hp])
	for k in boss._cooldowns:
		boss._cooldowns[k] = 0.0

	# ---- half his wax: the forced rite at the church's heart, then — once
	# the duel is handed back — the remembered light sweeps the parish
	var first_dmg := float(boss.cfg["attacks"][0]["dmg"])
	boss.take_hit(DamagePacket.new(boss.max_hp * 0.55, 0, player))
	await ticks(5)
	check(boss._seppuku, "at half his wax he turns the point on himself")
	var hp_mid = boss.hp
	boss.take_hit(DamagePacket.new(500, 0, player))
	check(boss.hp == hp_mid, "the rite cannot be interrupted")
	await ticks(620)
	check(boss._phase2, "the kindling takes")
	check(boss.global_position.distance_to(Vector3(0, 0.1, -20)) < 1.2,
		"the rite is performed at the church's heart (at %.1f,%.1f)" % [boss.global_position.x, boss.global_position.z])
	var p2 := 0
	for a in boss.cfg["attacks"]:
		if a.get("phase2_only", false):
			p2 += 1
	check(p2 >= 5, "the two-handed arsenal is his own (%d rites of the blade)" % p2)
	var pick: Dictionary = boss._pick_attack(3.0)
	check(pick.get("phase2_only", false) == true, "phase 2 swings only the two-handed arsenal (picked %s)" % pick.get("id", "none"))
	check(String(boss.vis.loco_override.get("walk", "")) == "twohand_walk", "he carries the golden blade in both hands")
	check(float(boss.cfg["attacks"][0]["dmg"]) > first_dmg, "his golden blade bites deeper")
	await ticks(460)
	check(area.glory_layer.visible, "the light sweeps, and the church remembers itself around the duel")
	var npc_hidden := true
	for n in area.glory_layer.get_children():
		if n is NPC and (n as Node3D).visible:
			npc_hidden = false
	check(npc_hidden, "the congregation does not return for the duel")
	boss.take_hit(DamagePacket.new(99999, 0, player))
	await ticks(30)
	check(boss.dead, "the Immortalized can be laid down")
	check(World.is_cleared("wick_cathedral"), "his fall clears the parish")
	check(not Game.arena_locked, "his fall opens the doors again")

	# ---- the light passes: the radiance drains back out of the parish (the
	# seeming hardens into the room) and the oath finds its last holder
	await ticks(400)
	check(not area.glory_layer.visible, "the remembered light drains out with him")
	check(area.ruin_layer.visible, "what remains is the true kingdom")
	check(World.flag("latecomer_radiant"), "the keeper's light passes to the Latecomer")
	check(player._radiant, "the Latecomer's armour kindles gold")

	# ---- portals land on floor both ways
	var down: AreaPortal = null
	for n in area.base.get_children():
		if n is AreaPortal:
			down = n
	check(down != null and down.to_area == "old_outskirts", "the door leads back to the town")
	var o := AreaBuilder.build("old_outskirts")
	add_child(o)
	var into: AreaPortal = null
	for n in o.base.get_children():
		if n is AreaPortal and n.to_area == "wick_cathedral":
			into = n
	check(into != null, "the parish door admits the pilgrim")
	if into != null:
		var ly := _floor_under(into.spawn_pos, area)
		check(absf(ly) < 0.35, "entering lands on the nave floor (y=%.2f)" % ly)

	# ---- Ser Adalric is waiting on the terrace with the truth
	var reck = null
	for n in o.base.get_children():
		if n.get_script() != null and String(n.get_script().resource_path).ends_with("adalric_reckoning.gd"):
			reck = n
	check(reck != null, "the reckoning waits outside the parish door")
	player.global_position = Vector3(0, 5.0, -43.5)
	await ticks(20)
	check(reck._staged, "he comes to meet you over the keeper's body")
	var guard := 0
	while not World.flag("reckoning_heard") and guard < 3000:
		guard += 15
		await ticks(15)
		reck.advance()
	check(World.flag("reckoning_heard"), "the reckoning is heard: what have you done")
	player.lock_control(false)   # the scene's own unlock dies with the area below
	o.queue_free()

	# ---- and the heard reckoning opens the road of light at the porch
	var porch := AreaBuilder.build("basilica_porch")
	add_child(porch)
	await ticks(5)
	var bridge = null
	var center_rails := 0
	for n in porch.base.get_children():
		if n.get_script() != null and String(n.get_script().resource_path).ends_with("light_bridge.gd"):
			bridge = n
		if n is Node3D and String(n.get_meta("kit_id", "")) == "balustrade_4m" \
				and absf((n as Node3D).position.z - 19.8) < 0.1 and absf((n as Node3D).position.x) < 3.0:
			center_rails += 1
	check(bridge != null, "the light makes its road off the porch")
	check(center_rails == 0, "the center railing has given way to it")
	porch.queue_free()

	for kit in ["pew_3m", "altar_wick"]:
		check(KitLib.instance(kit) != null, "kit %s resolves" % kit)

	finish()
