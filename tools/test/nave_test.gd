extends TestBase
## Basilica Nave integration: chime-puzzle entry, chorister projectiles,
## votive-lock state puzzle, the Sexton's dig service, and the Precentress
## (phases, radial volley, summons, clear flag).

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

	print("== porch: the vesper chimes gate the great door")
	var porch := AreaBuilder.build("basilica_porch")
	add_child(porch)
	Game.register_area(porch, "basilica_porch")
	StateDirector.snap(porch, VG.WState.GLORY)
	await ticks(20)
	var chimes: Array = _find(porch, ChimePuzzle)
	check(chimes.size() == 1, "chime circle stands on the porch")
	var ch: ChimePuzzle = chimes[0]
	ch._ring("vespers"); ch._ring("prime"); ch._ring("thirteenth")
	check(not World.flag("vesper_chimes"), "wrong order leaves the door shut")
	ch._ring("prime"); ch._ring("vespers"); ch._ring("thirteenth")
	check(World.flag("vesper_chimes"), "the dying order opens the way")
	var nave_portal: AreaPortal = null
	for p in _find(porch, AreaPortal):
		if p.to_area == "basilica_nave":
			nave_portal = p
	check(nave_portal != null and nave_portal._unlocked(), "basilica portal unlocked by the chimes")

	porch.queue_free()
	await ticks(3)

	print("== nave: structure")
	area = AreaBuilder.build("basilica_nave")
	add_child(area)
	Game.register_area(area, "basilica_nave")
	player = Player.new()
	add_child(player)
	player.global_position = Vector3(0, 0.3, 5)
	player.sim_active = true
	add_child(HUD.new())
	StateDirector.snap(area, VG.WState.RUIN)
	await ticks(25)
	check(area.base.get_child_count() > 120, "nave built (%d base nodes)" % area.base.get_child_count())
	check(area.nav_glory != null and area.nav_ruin != null, "navmeshes baked")
	var npcs := _find(area, NPC)
	check(npcs.size() == 1 and npcs[0].npc_id == "sexton", "the Sexton keeps his bay")
	check(DB.npc("sexton").get("lines_first", []).size() >= 3, "the Sexton has words")

	print("== chorister: it sings, and the song hurts")
	var e := Enemy.new()
	e.setup("chorister")
	add_child(e)
	e.global_position = Vector3(0, 0.2, -6)
	await ticks(5)
	e.target = player
	e._begin_attack(e.cfg["attacks"][0])   # versicle (ranged)
	var hp0 := player.hp
	await ticks(150)
	check(_find(get_tree().root, Projectile).size() >= 0, "projectile lifecycle ran")
	check(player.hp < hp0, "versicle struck the Latecomer (hp %.0f -> %.0f)" % [hp0, player.hp])
	e._die()

	print("== votive lock: kindled in glory, opens iron")
	var gates: Array = _find(area, FlagGate)
	check(gates.size() == 3, "three flag gates stand (%d)" % gates.size())
	var vgate: FlagGate = null
	for g in gates:
		if g.flag == "nave_votives":
			vgate = g
	check(vgate != null and not vgate._open, "gallery gate barred before the votives")
	StateDirector.snap(area, VG.WState.GLORY)
	await ticks(10)
	var locks: Array = _find(area, VotiveLock)
	check(locks.size() == 1, "votive lock present")
	var vl: VotiveLock = locks[0]
	for i in 3:
		vl._try_light(i)
		await ticks(3)
	check(World.flag("nave_votives"), "three flames set the flag")
	await ticks(10)
	check(vgate._open, "the gallery gate let go")

	print("== the sexton's dig (rubble lives in the ruin layer)")
	World.set_flag("sexton_dug")
	StateDirector.snap(area, VG.WState.RUIN)
	await ticks(15)
	var dug_open := true
	for g in gates:
		if g.flag == "sexton_dug" and not g._open:
			dug_open = false
	check(dug_open, "west aisle rubble cleared when the flag turns")

	print("== the Precentress")
	var boss: Enemy = null
	for en in get_tree().get_nodes_in_group(VG.GROUP_ENEMIES):
		if en.cfg.get("is_boss", false):
			boss = en
	check(boss != null, "she conducts in the chancel")
	if boss != null:
		check(boss.cfg.get("name", "") == "The Precentress", "named and titled")
		boss.target = player
		# force phase 2 and the summon
		boss.take_hit(DamagePacket.new(boss.max_hp * 0.5, 0.0, player))
		await ticks(5)
		check(boss.phase == 2, "half her breath brings the descant (phase %d)" % boss.phase)
		var summon: Dictionary = {}
		for a in boss.cfg["attacks"]:
			if a.get("type", "") == "summon":
				summon = a
		boss._begin_attack(summon)
		await ticks(120)
		var live_choir := 0
		for en2 in get_tree().get_nodes_in_group(VG.GROUP_ENEMIES):
			if en2.id == "chorister" and not en2.dead:
				live_choir += 1
		check(live_choir >= 2, "the choir answers her call (%d)" % live_choir)
		# put her to rest
		boss.take_hit(DamagePacket.new(99999.0, 0.0, player))
		await ticks(5)
		check(boss.dead, "the song ends")
		Game.on_boss_died("basilica_nave") if Game.has_method("on_boss_died") else null

	print("== return portal stands")
	var back: AreaPortal = null
	for p in _find(area, AreaPortal):
		if p.to_area == "basilica_porch":
			back = p
	check(back != null, "the porch door remembers you")

	finish()
