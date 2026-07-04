extends TestBase
## The Orisons death loop: kill reward, drop at death site, one-chance
## recovery, replacement on second death, vigil respawns enemies.

var area: Area
var player: Player
var spawner: Spawner
var lantern: VigilLantern

func _ready() -> void:
	_run.call_deferred()

func _build_world() -> void:
	area = Area.new()
	area.area_id = "dl_test"
	add_child(area)
	Game.register_area(area, "dl_test")
	for i in range(4):
		for j in range(4):
			var f := KitLib.instance("floor_4x4")
			f.position = Vector3(i * 4 - 6, 0, j * 4 - 6)
			KitLib.add_collision(f, VG.L_WORLD_BASE)
			area.attach(f, "base")
	area.bake_navmeshes()
	World.set_area_state("dl_test", VG.WState.RUIN)
	StateDirector.snap(area, VG.WState.RUIN)

	lantern = VigilLantern.new()
	lantern.lantern_id = "dl_lantern"
	lantern.area = area
	area.base.add_child(lantern)
	lantern.position = Vector3(6, 0, 6)
	World.last_vigil = {"area": "dl_test", "lantern": "dl_lantern"}

	spawner = Spawner.new()
	spawner.enemy_id = "penitent"
	area.ruin_layer.add_child(spawner)
	spawner.position = Vector3(-6, 0.1, -6)

	player = Player.new()
	add_child(player)
	player.position = Vector3(2, 0.15, 2)
	player.sim_active = true
	add_child(HUD.new())

func _run() -> void:
	_build_world()
	await ticks(10)

	print("== kill grants orisons")
	var e: Enemy = spawner.current
	check(e != null and not e.dead, "penitent spawned")
	Game.set_orisons(0)
	# hit it until dead with direct packets (combat mechanics already covered)
	while not e.dead:
		e.take_hit(DamagePacket.new(30, 10, player))
		await ticks(2)
	check(e.dead, "penitent dies")
	check(Game.orisons == 21, "orisons granted on kill (21, got %d)" % Game.orisons)

	print("== aggro: fresh spawn hunts the player")
	get_tree().call_group(VG.GROUP_RESPAWN_ON_REST, "respawn")
	await ticks(3)
	e = spawner.current
	check(e != null and not e.dead, "respawned by vigil call")
	player.global_position = e.global_position + Vector3(2.2, 0.1, 0)
	await ticks(50)
	check(e.state != Enemy.ES.IDLE, "enemy noticed the player")
	var hp0 := player.hp
	var waited := 0
	while player.hp >= hp0 and waited < 420:
		waited += 10
		await ticks(10)
	check(player.hp < hp0, "enemy attacks landed after %d ticks (hp %.0f -> %.0f, state %d)" % [waited, hp0, player.hp, e.state])

	print("== death drops a remembrance, respawn at lantern")
	player.global_position = Vector3(-4, 0.15, 4)
	await ticks(2)
	var death_pos := player.global_position
	Game.set_orisons(40)
	player.take_hit(DamagePacket.new(9999, 0, null))
	check(player.dead, "player dies")
	await ticks(15)
	check(Game.orisons == 0, "orisons dropped on death")
	check(World.remembrance != null and int(World.remembrance["amount"]) == 40, "remembrance holds 40")
	# wait out the respawn delay
	await ticks(200)
	check(not player.dead, "player respawned")
	check(player.global_position.distance_to(lantern.global_position) < 4.0, "respawned at the lantern")
	check(Game._remembrance_node != null, "remembrance wisp exists in world")
	check(Game._remembrance_node.global_position.distance_to(death_pos) < 1.5, "wisp at death site")

	print("== second death replaces the drop (first is lost)")
	Game.set_orisons(30)
	player.global_position = Vector3(5, 0.15, -5)
	await ticks(2)
	var second_pos := player.global_position
	player.take_hit(DamagePacket.new(9999, 0, null))
	await ticks(220)
	check(World.remembrance != null and int(World.remembrance["amount"]) == 30, "remembrance replaced with 30 (40 lost)")
	check(Game._remembrance_node.global_position.distance_to(second_pos) < 1.5, "wisp moved to new site")

	print("== reclaim returns the orisons")
	var before := Game.orisons
	player.global_position = Game._remembrance_node.global_position + Vector3(0.5, 0.1, 0.5)
	await ticks(5)
	check(player.try_interact(), "interact reaches the wisp")
	await ticks(5)
	check(Game.orisons == before + 30, "orisons reclaimed")
	check(World.remembrance == null, "world drop cleared")

	print("== vigil: heals, respawns enemies")
	e = spawner.current
	while e != null and not e.dead:
		e.take_hit(DamagePacket.new(50, 10, player))
		await ticks(1)
	player.hp = 20
	Game.vigil_flow(lantern, player)
	await ticks(260)
	check(player.hp == player.max_hp, "vigil heals to full")
	check(spawner.current != null and not spawner.current.dead, "vigil raises the dead again")
	check(not StateDirector.transitioning, "no state flip (uncleared ruin stays ruin)")
	check(World.get_area_state("dl_test") == VG.WState.RUIN, "area still ruin")

	finish()
