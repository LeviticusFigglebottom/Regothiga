extends TestBase
## The Bellkeeper: fog gate engagement, phases, clear-unlock, free toggling
## with persistence — the back half of the pass-1 loop.

var area: Area
var player: Player

func _ready() -> void:
	_run.call_deferred()

func _run() -> void:
	World.reset()
	World.set_area_state("gray_cloister", VG.WState.RUIN)
	area = AreaBuilder.build("gray_cloister")
	add_child(area)
	Game.register_area(area, "gray_cloister")
	player = Player.new()
	add_child(player)
	player.global_position = Vector3(10, 0.3, -5.5)
	player.sim_active = true
	add_child(HUD.new())
	StateDirector.snap(area, VG.WState.RUIN)
	World.last_vigil = {"area": "gray_cloister", "lantern": "garth"}
	await ticks(25)

	print("== the pale gate")
	var fog: FogGate = null
	var stack: Array[Node] = [area.ruin_layer]
	while not stack.is_empty():
		var n: Node = stack.pop_back()
		if n is FogGate:
			fog = n
		for c in n.get_children():
			stack.append(c)
	check(fog != null, "fog gate stands in the ruin")
	check(fog.boss_spawner != null and fog.boss_spawner.current != null, "warden bound to the gate")
	var boss: Enemy = fog.boss_spawner.current
	check(boss.cfg.get("is_boss", false), "it is the Bellkeeper")
	check(boss.state == Enemy.ES.IDLE, "he grieves undisturbed before the pale is parted")

	player.global_position = Vector3(11.6, 0.3, -6.0)
	await ticks(6)
	var it := player.nearest_interactable()
	check(it != null and it.prompt == "Part the pale", "the pale offers passage")
	it.activate(player)
	await ticks(80)
	check(boss.target == player, "the warden wakes")
	check(fog._seal.collision_layer != 0, "the pale seals at your back")

	print("== he fights; the toll breaks poise")
	var hp0 := player.hp
	var waited := 0
	while player.hp >= hp0 and waited < 900:
		waited += 10
		await ticks(10)
	check(player.hp < hp0, "the bell lands (hp %.0f -> %.0f after %d ticks)" % [hp0, player.hp, waited])

	print("== phase two at half grief")
	boss.take_hit(DamagePacket.new(boss.max_hp * 0.5, 0, player))
	await ticks(5)
	check(boss.phase == 2, "the Bellkeeper is enraged")

	print("== the warden rests")
	var orisons0 := Game.orisons
	while not boss.dead:
		boss.take_hit(DamagePacket.new(160, 0, player))
		await ticks(2)
	await ticks(30)
	check(World.is_cleared("gray_cloister"), "the Gray Cloister is cleared")
	check(Game.orisons - orisons0 >= 1200, "his hoard of orisons passes on (%d)" % (Game.orisons - orisons0))
	check(fog._seal.collision_layer == 0, "the pale disperses")

	print("== the tower door opens")
	player.global_position = Vector3(26.2, 0.3, -10)
	await ticks(6)
	it = player.nearest_interactable()
	check(it != null and it.prompt == "Enter the tower door", "the way to the basilica stands open")

	print("== free toggling, persisted")
	var lantern := Game.find_lantern("garth")
	player.global_position = lantern.respawn_point()
	await ticks(4)
	Game.vigil_flow(lantern, player, "toggle")
	var w2 := 0
	while not StateDirector.transitioning and w2 < 300:
		w2 += 5
		await ticks(5)
	while StateDirector.transitioning and w2 < 1500:
		w2 += 10
		await ticks(10)
	check(World.get_area_state("gray_cloister") == VG.WState.GLORY, "the memory kindles again")
	# and back
	Game.vigil_flow(lantern, player, "toggle")
	w2 = 0
	while not StateDirector.transitioning and w2 < 300:
		w2 += 5
		await ticks(5)
	while StateDirector.transitioning and w2 < 1500:
		w2 += 10
		await ticks(10)
	check(World.get_area_state("gray_cloister") == VG.WState.RUIN, "and gutters at will")

	print("== save round-trip")
	World.save_game()
	var st := World.get_area_state("gray_cloister")
	var cleared := World.is_cleared("gray_cloister")
	World.reset()
	check(World.load_game(), "save reloads")
	check(World.get_area_state("gray_cloister") == st, "state persisted")
	check(World.is_cleared("gray_cloister") == cleared, "cleared persisted")
	check(World.area_flag("gray_cloister", "slain_bellkeeper"), "the warden stays at rest")

	finish()
