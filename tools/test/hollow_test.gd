extends TestBase
## The Chandlers' Hollow (bonus optional DLC area) + base-game gap verification:
## verifies all 5 chambers of the Amber Foundry, reciprocal portal travel with
## the Old Outskirts, all 6 new 3D kit pieces & 2 UI icons, the 4-stand Apiary
## Votive Lock unbarring the Guildmaster's Reliquary, the Chandler's Censer-Mace
## pickup/equip/Devotion scaling/light, Master Caelan's Sovereign Seal-Wax
## flask-deepening service, Tallow Melter foes, and Malakor, the Sovereign
## Chandler boss fight (Phase 1, Phase 2 enrage, and Sovereign's Seal-Wax drop).

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

	# ---- 1. Verify base-game design gap fixes (all weapons & spells obtainable/named)
	var ferrier_cfg := DB.npc("ferrier")
	var sold_items: Array = []
	for srv in ferrier_cfg.get("services", []):
		if srv.get("type", "") == "buy":
			sold_items.append(String(srv.get("item", "")))
	check("ward_halberd" in sold_items and "sexton_maul" in sold_items,
		"Reliquary Smith stocks Ward's Halberd and Sexton's Maul")
	check(DB.item("morrow_lance").get("name", "") == "Morrow Lance",
		"Morrow Lance has its item table entry")
	check(DB.item("vesper_ward").get("name", "") == "Vesper Ward",
		"Vesper Ward has its item table entry")
	check(DB.item("sovereign_wax").get("name", "") == "Sovereign's Seal-Wax",
		"Sovereign's Seal-Wax has its item table entry")

	# ---- 2. Verify all 6 new DLC 3D kit pieces and 2 new UI icons resolve
	for kit in ["tallow_vat", "tallow_vat_cold", "apiary_skep", "wax_wheel", "censer_mace", "skel_chandler"]:
		var inst := KitLib.instance(kit)
		check(inst != null, "DLC kit %s resolves" % kit)
		if inst != null:
			inst.free()
	check(ResourceLoader.exists("res://assets/ui/icons/censer_mace.png"), "censer_mace icon exists")
	check(ResourceLoader.exists("res://assets/ui/icons/sovereign_wax.png"), "sovereign_wax icon exists")

	# ---- 3. Build The Chandlers' Hollow in GLORY and verify floor across all 5 chambers
	area = AreaBuilder.build("chandlers_hollow")
	add_child(area)
	Game.register_area(area, "chandlers_hollow")
	StateDirector.snap(area, VG.WState.GLORY)
	player = Player.new()
	add_child(player)
	player.sim_active = true
	player.global_position = Vector3(15.0, 0.3, 0.0)
	await ticks(12)

	var chambers := [
		[Vector3(17.5, 0, 0), "East Entrance Vestibule"],
		[Vector3(0, 0, 0), "Main Amber Foundry Hall"],
		[Vector3(0, 0, 18), "South Apiary Cloister"],
		[Vector3(-22, 0, 0), "West Guildmaster's Reliquary"],
		[Vector3(-2, 0, -24), "North Crucible Boss Vault"],
	]
	for ch in chambers:
		var y := _floor_under(ch[0], area)
		check(absf(y) < 0.35, "solid floor in %s (y=%.2f)" % [ch[1], y])

	# ---- 4. Verify reciprocal portal wiring with Old Outskirts
	var to_outskirts: AreaPortal = null
	for n in area.base.get_children():
		if n is AreaPortal and (n as AreaPortal).to_area == "old_outskirts":
			to_outskirts = n
	check(to_outskirts != null, "return portal to Old Outskirts exists")
	var outskirts := AreaBuilder.build("old_outskirts")
	add_child(outskirts)
	var to_hollow: AreaPortal = null
	for n in outskirts.base.get_children():
		if n is AreaPortal and (n as AreaPortal).to_area == "chandlers_hollow":
			to_hollow = n
	check(to_hollow != null, "Old Outskirts west portal to Chandlers' Hollow exists")
	if to_hollow != null:
		var hy := _floor_under(to_hollow.spawn_pos, area)
		check(absf(hy) < 0.35, "arrival from Old Outskirts lands on solid floor (y=%.2f)" % hy)
	outskirts.queue_free()

	# ---- 5. Verify Master Caelan NPC in Glory & his Sovereign's Seal-Wax flask service
	var caelan: NPC = null
	for n in area.glory_layer.get_children():
		if n is NPC and (n as NPC).npc_id == "master_caelan":
			caelan = n
	check(caelan != null, "Master Caelan stands in the Amber Foundry in Glory")

	# ---- 6. Verify the 4-stand Apiary Votive Lock unbars the West Reliquary FlagGate
	var rel_gate: FlagGate = null
	var vlock: VotiveLock = null
	for n in area.base.get_children():
		if n is FlagGate and (n as FlagGate).flag == "hollow_reliquary_open":
			rel_gate = n
		elif n is VotiveLock and (n as VotiveLock).flag == "hollow_reliquary_open":
			vlock = n
	check(rel_gate != null and not rel_gate._unlocked(), "West Reliquary door starts barred")
	check(vlock != null and vlock._stands.size() == 4, "four votive stands guard the Apiary Cloister")
	for i in 4:
		vlock._try_light(i)
	check(World.flag("hollow_reliquary_open") and rel_gate._unlocked(),
		"kindling all four Apiary votives unbars the West Reliquary")

	# ---- 7. Claim the Chandler's Censer-Mace pickup & verify Devotion scaling + light
	var mace_pk: Pickup = null
	for n in area.base.get_children():
		if n is Pickup and (n as Pickup).pickup_id == "hollow_censer_mace":
			mace_pk = n
	check(mace_pk != null, "Chandler's Censer-Mace rests in the West Reliquary")
	mace_pk._on_take(player)
	check(player.owns_weapon("chandler_mace"), "taking the pickup grants chandler_mace via give_item")
	check(player.hotbar.has("chandler_mace"), "chandler_mace auto-seats into the girdle hotbar")
	player.equip_weapon("chandler_mace")
	check(player.weapon_id == "chandler_mace", "Latecomer equips the Chandler's Censer-Mace")
	check(player._torch_light != null, "Censer-Mace sheds a warm liturgical vigil light while carried")
	var dmg_base := player._attack_damage(1.0)
	player.attributes["devotion"] = int(player.attributes.get("devotion", 10)) + 10
	var dmg_devout := player._attack_damage(1.0)
	check(dmg_devout > dmg_base + 5.0,
		"Chandler's Censer-Mace scales with Devotion (%.1f -> %.1f)" % [dmg_base, dmg_devout])

	# ---- 8. Gutter into RUIN: verify Tallow Melters and Malakor, the Sovereign Chandler
	StateDirector.snap(area, VG.WState.RUIN)
	await ticks(10)
	var melters := 0
	for e in get_tree().get_nodes_in_group(VG.GROUP_ENEMIES):
		if e is Enemy and (e as Enemy).id == "tallow_melter":
			melters += 1
	check(melters >= 3, "Tallow Melters haunt the ruined foundry (%d)" % melters)

	var fog: FogGate = null
	for n in area.ruin_layer.get_children():
		if n is FogGate and (n as FogGate).gate_id == "hollow_boss_fog":
			fog = n
	check(fog != null and fog.boss_spawner != null, "the Crucible Vault fog gate binds the Sovereign Chandler")
	player.global_position = Vector3(-2.0, 0.3, -10.5)
	await ticks(5)
	fog._on_enter(player)
	await ticks(25)
	var boss: Enemy = fog.boss_spawner.current
	check(boss != null and boss.id == "sovereign_chandler",
		"Malakor, the Sovereign Chandler awakens in the Crucible Vault")
	check(boss.phase == 1, "Malakor begins in Phase 1")

	# Trigger Phase 2 at <= 55% HP
	var p1_dmg := DamagePacket.new(boss.max_hp * 0.5, 10.0, player)
	boss.take_hit(p1_dmg)
	check(boss.phase == 2, "Malakor enters Phase 2 when brought below 55% HP")

	# Slay Malakor and verify Sovereign's Seal-Wax drop + arena clear
	var kill_dmg := DamagePacket.new(boss.hp + 500.0, 100.0, player)
	boss.take_hit(kill_dmg)
	await ticks(10)
	check(boss.dead, "Malakor is slain")
	check(int(player.inventory.get("sovereign_wax", 0)) >= 1,
		"Malakor drops the Sovereign's Seal-Wax")

	# ---- 9. Return to GLORY and steep Sovereign's Seal-Wax with Master Caelan
	StateDirector.snap(area, VG.WState.GLORY)
	await ticks(8)
	var flask_before := player.flask_max
	var glass_before := int(player.inventory.get("candleglass", 0))
	var c_cfg := DB.npc("master_caelan")
	c_cfg["id"] = "master_caelan"
	var dlg := DialogueUI.new(c_cfg, caelan)
	add_child(dlg)
	await ticks(4)
	for srv in c_cfg.get("services", []):
		if srv.get("id", "") == "steep_sovereign":
			dlg._activate(srv)
			break
	check(player.flask_max == flask_before + 1,
		"Master Caelan steeps the Sovereign's Seal-Wax to deepen the Chrism Flask (%d -> %d)" % [flask_before, player.flask_max])
	check(int(player.inventory.get("candleglass", 0)) == glass_before + 1,
		"Master Caelan also grants skimmed Candleglass")
	dlg.close()
	await ticks(4)

	finish()
