extends TestBase
## Full 2-Zone Soulslike DLC Expansion ("The Chandlers' Hollow" + "The Sovereign Apiary")
## + base-game gap verification:
## - Verifies all 12 custom DLC 3D kit pieces (`tallow_vat`, `tallow_vat_cold`,
##   `apiary_skep`, `wax_wheel`, `censer_mace`, `skel_chandler`, `wax_press`,
##   `honey_amphora`, `comb_shrine`, `comb_pillar_4m`, `blade_sovereign`,
##   `skel_matriarch`) and all 5 custom DLC 2D UI icons.
## - Verifies all 10 chambers & split-level stairs (`y = 0.0` & `y = 2.4`) in
##   `chandlers_hollow`, reciprocal portal travel with `old_outskirts` and
##   `sovereign_apiary`, the 4-stand Apiary Votive Lock, the Chandler's
##   Censer-Mace, the Rite of the Golden Comb (`amber_benediction`) pickup &
##   casting, Tallow Melters, and Malakor, the Sovereign Chandler boss fight.
## - Verifies all 6 wings of `sovereign_apiary` (including the Open-Air
##   Botanical Garth and Elevated `y = 2.4` Chapter-House), Sister Melisande,
##   the 4-stand Sanctum Votive Lock (`apiary_sanctum_open`), the Sovereign
##   Comb-Blade (`sovereign_greatsword`), Gilded Comb-Warden elites, Aurelia,
##   the Vesper Matriarch boss fight (Phase 1, Phase 2, and Crown of the First
##   Comb drop), and Master Caelan's `forge_crown` delivery service.

var area: Area
var player: Player

func _ready() -> void:
	_run.call_deferred()

func _floor_under(p: Vector3, area_ref: Area) -> float:
	var q := PhysicsRayQueryParameters3D.create(p + Vector3.UP * 0.6, p + Vector3.DOWN * 3.0, VG.M_WORLD_ALL)
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
	check(DB.item("matriarch_comb").get("name", "") == "Crown of the First Comb",
		"Crown of the First Comb has its item table entry")
	check(DB.item("amber_benediction").get("name", "") == "Rite of the Golden Comb",
		"Rite of the Golden Comb has its item table entry")

	# ---- 2. Verify all 12 custom DLC 3D kit pieces and 5 UI icons resolve
	var dlc_kits := [
		"tallow_vat", "tallow_vat_cold", "apiary_skep", "wax_wheel",
		"censer_mace", "skel_chandler", "wax_press", "honey_amphora",
		"comb_shrine", "comb_pillar_4m", "blade_sovereign", "skel_matriarch",
	]
	for kit in dlc_kits:
		var inst := KitLib.instance(kit)
		check(inst != null, "DLC kit %s resolves" % kit)
		if inst != null:
			inst.free()
	for icon in ["censer_mace", "sovereign_wax", "sovereign_greatsword", "matriarch_comb", "amber_benediction"]:
		check(ResourceLoader.exists("res://assets/ui/icons/%s.png" % icon), "%s icon exists" % icon)

	# ---- 3. Build The Chandlers' Hollow in GLORY and verify floor across all 10 chambers (y=0 & y=2.4)
	area = AreaBuilder.build("chandlers_hollow")
	add_child(area)
	Game.register_area(area, "chandlers_hollow")
	StateDirector.snap(area, VG.WState.GLORY)
	player = Player.new()
	add_child(player)
	player.sim_active = true
	player.global_position = Vector3(22.0, 0.3, 0.0)
	await ticks(12)

	var hollow_chambers := [
		[Vector3(22.0, 0.0, 0.0), 0.0, "East Entrance Gallery & Forge"],
		[Vector3(0.0, 0.0, 0.0), 0.0, "Main Amber Foundry Nave"],
		[Vector3(0.0, 0.0, 18.0), 0.0, "South Apiary Conservatory"],
		[Vector3(22.0, 0.0, 18.0), 0.0, "South-East Smelting Cistern"],
		[Vector3(32.0, 2.4, 18.0), 2.4, "East Elevated Smelting Mezzanine (y=2.4)"],
		[Vector3(-22.0, 0.0, 0.0), 0.0, "West Reliquary Antechamber"],
		[Vector3(-34.0, 2.4, 0.0), 2.4, "West High Scriptorium & Sanctuary (y=2.4)"],
		[Vector3(-22.0, 0.0, 20.0), 0.0, "South-West Wax-Crypt & Ossuary"],
		[Vector3(-2.0, 0.0, -24.0), 0.0, "North Crucible Boss Vault"],
		[Vector3(0.0, 0.0, -42.0), 0.0, "North Sovereign Postern Sanctuary"],
	]
	for ch in hollow_chambers:
		var y := _floor_under(ch[0], area)
		check(absf(y - float(ch[1])) < 0.35, "solid floor in %s (y=%.2f)" % [ch[2], y])

	# ---- 4. Verify reciprocal portal wiring with Old Outskirts and Sovereign Apiary
	var to_outskirts: AreaPortal = null
	var to_apiary: AreaPortal = null
	for n in area.base.get_children():
		if n is AreaPortal:
			var ap := n as AreaPortal
			if ap.to_area == "old_outskirts":
				to_outskirts = ap
			elif ap.to_area == "sovereign_apiary":
				to_apiary = ap
	check(to_outskirts != null, "return portal to Old Outskirts exists")
	check(to_apiary != null, "north postern portal to The Sovereign Apiary exists")

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

	# ---- 5. Verify Master Caelan NPC in Glory & the 4-stand Apiary Votive Lock
	var caelan: NPC = null
	for n in area.glory_layer.get_children():
		if n is NPC and (n as NPC).npc_id == "master_caelan":
			caelan = n
	check(caelan != null, "Master Caelan stands in the Amber Foundry in Glory")

	var rel_gate: FlagGate = null
	var vlock: VotiveLock = null
	for n in area.base.get_children():
		if n is FlagGate and (n as FlagGate).flag == "hollow_reliquary_open":
			rel_gate = n
		elif n is VotiveLock and (n as VotiveLock).flag == "hollow_reliquary_open":
			vlock = n
	check(rel_gate != null and not rel_gate._unlocked(), "West Reliquary door starts barred")
	check(vlock != null and vlock._stands.size() == 4, "four votive stands guard the Apiary Conservatory")
	for i in 4:
		vlock._try_light(i)
	check(World.flag("hollow_reliquary_open") and rel_gate._unlocked(),
		"kindling all four Apiary votives unbars the West Reliquary")

	# ---- 6. Claim the Chandler's Censer-Mace (at y=2.4) & Rite of the Golden Comb (on East Mezzanine y=2.4)
	var mace_pk: Pickup = null
	var spell_pk: Pickup = null
	for n in area.base.get_children():
		if n is Pickup:
			var pk := n as Pickup
			if pk.pickup_id == "hollow_censer_mace":
				mace_pk = pk
			elif pk.pickup_id == "crypt_amber_rite":
				spell_pk = pk
	check(mace_pk != null, "Chandler's Censer-Mace rests in the West Reliquary")
	mace_pk._on_take(player)
	check(player.owns_weapon("chandler_mace"), "taking the pickup grants chandler_mace")
	player.equip_weapon("chandler_mace")
	check(player.weapon_id == "chandler_mace", "Latecomer equips the Chandler's Censer-Mace")
	check(player._torch_light != null, "Censer-Mace sheds a warm liturgical vigil light while carried")
	var dmg_base := player._attack_damage(1.0)
	player.attributes["devotion"] = int(player.attributes.get("devotion", 10)) + 10
	var dmg_devout := player._attack_damage(1.0)
	check(dmg_devout > dmg_base + 5.0,
		"Chandler's Censer-Mace scales with Devotion (%.1f -> %.1f)" % [dmg_base, dmg_devout])

	check(spell_pk != null, "Rite of the Golden Comb rests in the South-West Wax-Crypt")
	spell_pk._on_take(player)
	check(int(player.inventory.get("amber_benediction", 0)) >= 1, "taking the pickup grants amber_benediction")
	player.hp = player.max_hp * 0.5
	var hp_before_cast := player.hp
	player.cast_spell("amber_benediction")
	await ticks(6)
	check(player.hp > hp_before_cast + 5.0,
		"casting Rite of the Golden Comb restores HP while loosing golden comb bolts (%.1f -> %.1f)" % [hp_before_cast, player.hp])

	# ---- 7. Gutter into RUIN: verify Tallow Melters and Malakor, the Sovereign Chandler
	StateDirector.snap(area, VG.WState.RUIN)
	await ticks(10)
	var melters := 0
	for e in get_tree().get_nodes_in_group(VG.GROUP_ENEMIES):
		if e is Enemy and (e as Enemy).id == "tallow_melter":
			melters += 1
	check(melters >= 5, "Tallow Melters haunt the expanded foundry (%d)" % melters)

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
	boss.take_hit(DamagePacket.new(boss.max_hp * 0.5, 10.0, player))
	check(boss.phase == 2, "Malakor enters Phase 2 when brought below 55% HP")
	boss.take_hit(DamagePacket.new(boss.hp + 500.0, 100.0, player))
	await ticks(10)
	check(boss.dead and int(player.inventory.get("sovereign_wax", 0)) >= 1,
		"slaying Malakor drops the Sovereign's Seal-Wax")

	# Steep Sovereign's Seal-Wax with Master Caelan in Glory
	StateDirector.snap(area, VG.WState.GLORY)
	await ticks(6)
	var flask_before := player.flask_max
	var c_cfg := DB.npc("master_caelan")
	c_cfg["id"] = "master_caelan"
	var dlg := DialogueUI.new(c_cfg, caelan)
	add_child(dlg)
	await ticks(3)
	for srv in c_cfg.get("services", []):
		if srv.get("id", "") == "steep_sovereign":
			dlg._activate(srv)
			break
	check(player.flask_max == flask_before + 1,
		"Master Caelan steeps the Sovereign's Seal-Wax to deepen the Chrism Flask (%d -> %d)" % [flask_before, player.flask_max])
	dlg.close()
	await ticks(3)

	# =========================================================================
	# ---- 8. Zone 2: Build THE SOVEREIGN APIARY ("sovereign_apiary") & verify all 6 wings
	# =========================================================================
	var apiary_spawn_pos := to_apiary.spawn_pos
	area.queue_free()
	await ticks(4)
	area = AreaBuilder.build("sovereign_apiary")
	add_child(area)
	Game.register_area(area, "sovereign_apiary")
	StateDirector.snap(area, VG.WState.GLORY)
	player.global_position = apiary_spawn_pos
	await ticks(12)

	var apiary_wings := [
		[Vector3(0.0, 0.0, 6.0), 0.0, "South Cliff-Stair Vestibule"],
		[Vector3(-4.0, 0.0, -14.0), 0.0, "Open-Air Botanical Garth"],
		[Vector3(-15.0, 0.0, -10.0), 0.0, "West Cloister Walk"],
		[Vector3(-25.0, 0.0, -16.0), 0.0, "West Royal Press-House"],
		[Vector3(28.0, 2.4, -16.0), 2.4, "East Elevated Chapter-House & Scriptorium (y=2.4)"],
		[Vector3(0.0, 0.0, -36.0), 0.0, "North Queen-Comb Sanctuary Terrace"],
		[Vector3(-2.0, 0.0, -58.0), 0.0, "Cathedral of the First Comb"],
	]
	for w in apiary_wings:
		var y := _floor_under(w[0], area)
		check(absf(y - float(w[1])) < 0.35, "solid floor in %s (y=%.2f)" % [w[2], y])

	# Verify Sister Melisande NPC in Glory
	var melisande: NPC = null
	for n in area.glory_layer.get_children():
		if n is NPC and (n as NPC).npc_id == "sister_melisande":
			melisande = n
	check(melisande != null, "Sister Melisande, the Blind Beekeeper stands on the Sanctuary Terrace in Glory")

	# Verify 4-stand Sanctum Votive Lock unbars the Queen-Comb Sanctuary
	var sanctum_gate: FlagGate = null
	var sanctum_lock: VotiveLock = null
	for n in area.base.get_children():
		if n is FlagGate and (n as FlagGate).flag == "apiary_sanctum_open":
			sanctum_gate = n
		elif n is VotiveLock and (n as VotiveLock).flag == "apiary_sanctum_open":
			sanctum_lock = n
	check(sanctum_gate != null and not sanctum_gate._unlocked(), "Queen-Comb Sanctuary door starts barred")
	check(sanctum_lock != null and sanctum_lock._stands.size() == 4, "four votive stands span the West Press-House and East Chapter-House")
	for i in 4:
		sanctum_lock._try_light(i)
	check(World.flag("apiary_sanctum_open") and sanctum_gate._unlocked(),
		"kindling all four Sanctum votives unbars the Queen-Comb Sanctuary")

	# Claim the Sovereign Comb-Blade (`sovereign_greatsword`) in the East Chapter-House (y=2.4)
	var sword_pk: Pickup = null
	for n in area.base.get_children():
		if n is Pickup and (n as Pickup).pickup_id == "apiary_sovereign_greatsword":
			sword_pk = n
	check(sword_pk != null, "Sovereign Comb-Blade rests in the East Chapter-House (y=2.4)")
	sword_pk._on_take(player)
	check(player.owns_weapon("sovereign_greatsword"), "claiming the pickup grants sovereign_greatsword")
	player.equip_weapon("sovereign_greatsword")
	check(player.weapon_id == "sovereign_greatsword" and player._torch_light != null,
		"Sovereign Comb-Blade equips and sheds warm amber light")

	# ---- 9. Gutter into RUIN in The Sovereign Apiary: verify Gilded Comb-Wardens & Aurelia, the Vesper Matriarch
	StateDirector.snap(area, VG.WState.RUIN)
	await ticks(10)
	var wardens := 0
	for e in get_tree().get_nodes_in_group(VG.GROUP_ENEMIES):
		if e is Enemy and (e as Enemy).id == "comb_warden":
			wardens += 1
	check(wardens >= 4, "Gilded Comb-Wardens patrol the ruined Apiary (%d)" % wardens)

	var apiary_fog: FogGate = null
	for n in area.ruin_layer.get_children():
		if n is FogGate and (n as FogGate).gate_id == "apiary_boss_fog":
			apiary_fog = n
	check(apiary_fog != null and apiary_fog.boss_spawner != null,
		"Cathedral of the First Comb fog gate binds Aurelia, the Vesper Matriarch")
	player.global_position = Vector3(-2.0, 0.3, -42.5)
	await ticks(5)
	apiary_fog._on_enter(player)
	await ticks(25)
	var matriarch: Enemy = apiary_fog.boss_spawner.current
	check(matriarch != null and matriarch.id == "vesper_matriarch",
		"Aurelia, the Vesper Matriarch awakens in the Cathedral of the First Comb")
	check(matriarch.phase == 1, "Aurelia begins in Phase 1")
	matriarch.take_hit(DamagePacket.new(matriarch.max_hp * 0.45, 10.0, player))
	check(matriarch.phase == 2, "Aurelia enters Phase 2 when brought below 60% HP")
	matriarch.take_hit(DamagePacket.new(matriarch.hp + 500.0, 100.0, player))
	await ticks(10)
	check(matriarch.dead and int(player.inventory.get("matriarch_comb", 0)) >= 1,
		"slaying Aurelia drops the Crown of the First Comb (matriarch_comb)")

	# Verify Master Caelan's `forge_crown` delivery service with `matriarch_comb`
	var flask_pre_crown := player.flask_max
	var dlg2 := DialogueUI.new(c_cfg, null)
	add_child(dlg2)
	await ticks(3)
	for srv in c_cfg.get("services", []):
		if srv.get("id", "") == "forge_crown":
			dlg2._activate(srv)
			break
	check(player.flask_max == flask_pre_crown + 1,
		"Master Caelan melts the Crown of the First Comb into the Chrism Flask (%d -> %d)" % [flask_pre_crown, player.flask_max])
	dlg2.close()
	await ticks(4)

	finish()
