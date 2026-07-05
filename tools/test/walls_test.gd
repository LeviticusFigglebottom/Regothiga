extends TestBase
## Perimeter + collision regression: the east-walk hole is sealed, arch
## doorways to the void are blocked, solid decor and the NPC have bodies,
## and the kill-plane failsafe recovers a fall.

var area: Area
var player: Player

func _ready() -> void:
	_run.call_deferred()

func _push(dir: Vector3, frames: int) -> void:
	player.sim_move = dir
	await ticks(frames)
	player.sim_move = Vector3.ZERO
	await ticks(5)

func _ray_hits(from: Vector3, to: Vector3) -> bool:
	var q := PhysicsRayQueryParameters3D.create(from, to, VG.M_WORLD_ALL)
	return not area.get_world_3d().direct_space_state.intersect_ray(q).is_empty()

func _run() -> void:
	World.reset()
	area = AreaBuilder.build("gray_cloister")
	add_child(area)
	Game.register_area(area, "gray_cloister")
	player = Player.new()
	add_child(player)
	player.sim_active = true
	player.global_position = Vector3(0, 0.3, 0)
	StateDirector.snap(area, VG.WState.RUIN)
	await ticks(25)

	print("== the east-walk hole is a wall now")
	check(_ray_hits(Vector3(10, 1.2, 10.5), Vector3(10, 1.2, 13.5)), "wall stands at z=12, x 8..12")
	player.global_position = Vector3(10, 0.3, 9.5)
	await ticks(3)
	await _push(Vector3(0, 0, 1), 120)
	check(player.global_position.z < 12.6, "pushing south stops at the wall (z=%.1f)" % player.global_position.z)
	check(player.global_position.y > -1.0, "no fall out of bounds (y=%.2f)" % player.global_position.y)

	print("== boss yard side-slip sealed")
	player.global_position = Vector3(10.6, 0.3, -2)
	await ticks(3)
	await _push(Vector3(1, 0, 0), 90)
	check(player.global_position.x < 12.6, "lancet closes x=12, z -4..0 (x=%.1f)" % player.global_position.x)

	print("== tower arch blocked until travel")
	player.global_position = Vector3(26.5, 0.3, -10)
	await ticks(3)
	await _push(Vector3(1, 0, 0), 100)
	check(player.global_position.x < 28.6, "cannot walk through the tower arch (x=%.1f)" % player.global_position.x)
	check(player.global_position.y > -1.0, "still on the yard floor")

	print("== solid decor blocks (ruin: cold brazier)")
	player.global_position = Vector3(-3.4, 0.3, -4.6)
	await ticks(3)
	await _push(Vector3(0, 0, -1), 80)
	check(player.global_position.z > -6.55, "cold brazier has a body (z=%.2f)" % player.global_position.z)

	print("== solid decor blocks (glory: wellhead + the Chandler)")
	StateDirector.snap(area, VG.WState.GLORY)
	await ticks(10)
	player.global_position = Vector3(-4.5, 0.3, 2.0)
	await ticks(3)
	await _push(Vector3(0, 0, 1), 80)
	check(player.global_position.z < 3.95, "wellhead has a body (z=%.2f)" % player.global_position.z)
	player.global_position = Vector3(-16, 0.3, -6.2)
	await ticks(3)
	await _push(Vector3(0, 0, -1), 80)
	check(player.global_position.z > -7.75, "Aveline has a body (z=%.2f)" % player.global_position.z)

	print("== hangings stay passable")
	player.global_position = Vector3(-2, 0.3, -7.6)
	await ticks(3)
	await _push(Vector3(0, 0, -1), 70)
	check(player.global_position.z < -8.6, "glory banner does not block the garth portal (z=%.2f)" % player.global_position.z)

	print("== kill-plane failsafe")
	var hp_before := player.hp
	player.global_position = Vector3(10, -30.0, 5)
	await ticks(10)
	check(player.global_position.y > -2.0, "player recovered to last ground (y=%.2f)" % player.global_position.y)
	check(player.hp < hp_before and player.hp > 0.0, "fall cost a quarter of health, not the run")

	print("== porch: the grand stair actually descends (skip bug regression)")
	area.queue_free()
	await ticks(3)
	area = AreaBuilder.build("basilica_porch")
	add_child(area)
	Game.register_area(area, "basilica_porch")
	StateDirector.snap(area, VG.WState.GLORY)
	await ticks(25)
	# the twin runs sit at x ~±2 either side of a stone spine at x 0
	player.global_position = Vector3(-2, 0.3, 5)
	await ticks(3)
	await _push(Vector3(0, 0, 1), 220)
	check(player.global_position.z > 12.0, "walked down onto the terrace (z=%.1f)" % player.global_position.z)
	check(absf(player.global_position.y + 2.62) < 0.7, "landed at terrace height (y=%.2f)" % player.global_position.y)
	player.global_position = Vector3(2, -2.3, 13)
	await ticks(3)
	await _push(Vector3(0, 0, -1), 260)
	check(player.global_position.z < 8.0 and player.global_position.y > -0.7,
		"climbed back up the stair (z=%.1f y=%.2f)" % [player.global_position.z, player.global_position.y])
	player.global_position = Vector3(-6.5, -2.3, 16)
	await ticks(3)
	await _push(Vector3(-1, 0, 0), 90)
	check(player.global_position.x > -8.6, "terrace balustrade holds (x=%.1f)" % player.global_position.x)
	check(player.global_position.y > -4.0, "no fall off the terrace")

	finish()
