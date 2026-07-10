extends TestBase
## THE PASS-1 LOOP, end to end (§11): glory exploration -> NPC -> shortcut ->
## vigil -> ruin gauntlet -> real sword kill -> death & remembrance -> level
## up -> boss behind the pale -> tower door -> Area B in glory -> stub vigil
## -> return -> free toggle -> persistence.

var player: Player

func _area() -> Area:
	return Game.current_area

func _ready() -> void:
	_run.call_deferred()

func _wait_transition(max_ticks := 1500) -> void:
	var w := 0
	while not StateDirector.transitioning and w < 300:
		w += 5
		await ticks(5)
	while StateDirector.transitioning and w < max_ticks:
		w += 10
		await ticks(10)

func _run() -> void:
	World.reset()
	# boot exactly like the game does
	var wr := Node3D.new()
	add_child(wr)
	Game.world_root = wr
	var area := AreaBuilder.build("gray_cloister")
	wr.add_child(area)
	Game.register_area(area, "gray_cloister")
	StateDirector.snap(area, World.get_area_state("gray_cloister"))
	player = Player.new()
	add_child(player)
	player.global_position = Vector3(-18, 0.3, -2)
	player.sim_active = true
	add_child(HUD.new())
	await ticks(25)

	print("== 1. we arrive in glory")
	check(World.get_area_state("gray_cloister") == VG.WState.GLORY, "the Cloister remembers itself for us")

	print("== 2. lore and the Chandler")
	var lore_got := [""]
	Game.lore_panel.connect(func(t): lore_got[0] = t)
	player.global_position = Vector3(-14.6, 0.3, -2.9)
	await ticks(5)
	check(player.try_interact(), "read the porch plaque")
	check(lore_got[0].contains("VESPERGARD"), "the kingdom speaks")
	get_tree().get_first_node_in_group("hud").lore_root.visible = false
	player.lock_control(false)
	player.global_position = Vector3(-15.2, 0.3, -8)
	await ticks(5)
	check(player.try_interact(), "spoke to Sister Aveline")
	await ticks(3)
	var dlg: DialogueUI = null
	for c in get_tree().root.get_children():
		if c is DialogueUI:
			dlg = c
	check(dlg != null, "dialogue opened")
	if dlg:
		dlg.close()
	await ticks(3)
	check(World.flag("met_aveline"), "she will remember us")

	print("== 3. the shortcut, learned in peace")
	player.global_position = Vector3(10, 0.3, -1.4)
	# outlast the dialogue-close interact suppression (10 physics frames) —
	# a human walking here takes far longer than the guard window
	await ticks(14)
	player.try_interact()
	await ticks(20)
	check(World.area_flag("gray_cloister", "gate_east_walk"), "east-walk gate unbarred from the far side")

	print("== 4. first vigil: the seeing ends")
	var lantern := Game.find_lantern("garth")
	player.global_position = lantern.respawn_point()
	await ticks(4)
	Game.vigil_flow(lantern, player)   # auto: uncleared+glory -> gutter
	await _wait_transition()
	check(World.get_area_state("gray_cloister") == VG.WState.RUIN, "the memory gutters — the gauntlet begins")
	await ticks(30)

	print("== 5. a real kill with the Cloistersword")
	var prey: Enemy = null
	for e in get_tree().get_nodes_in_group(VG.GROUP_ENEMIES):
		if e is Enemy and e.can_process() and e.id == "penitent" and not e.dead:
			prey = e
			break
	check(prey != null, "a penitent shambles in the ruin")
	var orisons0 := Game.orisons
	var swings := 0
	while prey != null and not prey.dead and swings < 30:
		var to: Vector3 = prey.global_position - player.global_position
		if to.length() > 1.5:
			player.global_position = prey.global_position + to.normalized() * -1.4 + Vector3(0, 0.1, 0)
		player.vis.rotation.y = atan2(-to.x, -to.z)
		player.velocity = Vector3.ZERO
		player.stamina = player.max_stamina
		player.try_attack(false)
		swings += 1
		await ticks(50)
	check(prey.dead, "cut down by the blade (%d swings)" % swings)
	check(Game.orisons > orisons0, "orisons gathered (%d)" % Game.orisons)

	print("== 6. we fall, and are FORGOTTEN — then reclaim")
	Game.set_orisons(90)
	player.global_position = Vector3(-4, 0.2, 4)
	await ticks(2)
	player.take_hit(DamagePacket.new(9999, 0, null))
	check(player.dead, "death takes us")
	await ticks(210)
	check(not player.dead, "the lantern calls us back")
	check(player.global_position.distance_to(lantern.global_position) < 4.0, "respawned at the last vigil")
	check(Game.orisons == 0, "our prayers stayed where we fell")
	player.global_position = Game._remembrance_node.global_position + Vector3(0.4, 0.1, 0.4)
	await ticks(5)
	check(player.try_interact(), "remembrance reclaimed at the death site")
	check(Game.orisons >= 90, "the orisons return (%d)" % Game.orisons)

	print("== 7. grow by prayer at the lantern")
	var vit0: int = player.attributes["vigor"]
	var ui := RestUI.new(lantern, player)
	get_tree().root.add_child(ui)
	await ticks(2)
	var li := -1
	for i in ui._options.size():
		if ui._options[i]["id"] == "level":
			li = i
	ui.choose(li)
	await ticks(2)
	ui.choose(0)   # vigor
	await ticks(2)
	ui.close()
	check(player.attributes["vigor"] == vit0 + 1, "vigor grown by prayer")
	check(player.level == 2, "level 2")

	print("== 8. the warden behind the pale")
	var fog: FogGate = null
	var stack: Array[Node] = [area.ruin_layer]
	while not stack.is_empty():
		var n: Node = stack.pop_back()
		if n is FogGate:
			fog = n
		for c in n.get_children():
			stack.append(c)
	player.global_position = Vector3(11.6, 0.3, -6.0)
	await ticks(5)
	check(player.try_interact(), "part the pale")
	await ticks(80)
	var boss: Enemy = fog.boss_spawner.current
	check(boss.target == player, "the Bellkeeper answers")
	while not boss.dead:
		boss.take_hit(DamagePacket.new(140, 0, player))
		await ticks(2)
	await ticks(40)
	check(World.is_cleared("gray_cloister"), "the Gray Cloister is cleared")

	print("== 9. through the tower door: Area B, in glory")
	player.global_position = Vector3(26.2, 0.3, -10)
	await ticks(6)
	check(player.try_interact(), "the tower door opens")
	await ticks(40)
	check(Game.current_area_id == "basilica_porch", "we stand in the Basilica porch")
	check(World.get_area_state("basilica_porch") == VG.WState.GLORY, "the next quarter waits in glory")

	print("== 10. the thin lantern, and the road back")
	var porch_lantern := Game.find_lantern("porch")
	check(porch_lantern != null, "the porch lantern burns")
	Game.vigil_flow(porch_lantern, player, "rest_only")
	await ticks(140)
	check(World.get_area_state("basilica_porch") == VG.WState.GLORY, "its memory is thin — no gutter (stub)")
	player.global_position = Vector3(7.2, 0.3, -2)
	await ticks(6)
	check(player.try_interact(), "return to the Cloister")
	await ticks(40)
	check(Game.current_area_id == "gray_cloister", "home again")
	check(World.get_area_state("gray_cloister") == VG.WState.RUIN, "Area A held its ruin state across travel")

	print("== 11. cleared: the memory turns at will, and it keeps")
	var lantern2 := Game.find_lantern("garth")
	player.global_position = lantern2.respawn_point()
	await ticks(6)
	Game.vigil_flow(lantern2, player, "toggle")
	await _wait_transition()
	check(World.get_area_state("gray_cloister") == VG.WState.GLORY, "kindled by choice")
	World.save_game()
	var snapshot := World.get_area_state("gray_cloister")
	World.reset()
	check(World.load_game(), "the vigil is written")
	check(World.get_area_state("gray_cloister") == snapshot, "and the kingdom remembers our choice")

	finish()
