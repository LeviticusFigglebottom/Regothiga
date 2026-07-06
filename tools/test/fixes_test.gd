extends TestBase
## Pass-6/8 regression: dialogue leaves cleanly (no reopen cycle), convex
## props block without wedging, middle-mouse locks on and a hard flick releases.

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

func _push(dir: Vector3, frames: int) -> void:
	player.sim_move = dir
	await ticks(frames)
	player.sim_move = Vector3.ZERO
	await ticks(4)

func _run() -> void:
	World.reset()
	area = AreaBuilder.build("gray_cloister")
	add_child(area)
	Game.register_area(area, "gray_cloister")
	player = Player.new()
	add_child(player)
	player.global_position = Vector3(0, 0.3, 0)
	player.sim_active = true
	add_child(HUD.new())
	StateDirector.snap(area, VG.WState.GLORY)
	await ticks(25)

	print("== dialogue: Leave actually leaves, no reopen cycle")
	var npcs: Array = _find(area, NPC)
	check(npcs.size() == 1, "the Chandler stands")
	var npc: NPC = npcs[0]
	# sim drives dialogue via advance()/choose(); enter the conversation
	npc._on_talk(player)
	await ticks(2)
	check(player.state == player.S.TALK, "talking puts the Latecomer in TALK state")
	check(not player.input_enabled, "control is locked while talking")
	var uis: Array = _find(get_tree().root, DialogueUI)
	check(uis.size() == 1, "a dialogue panel opened")
	var ui: DialogueUI = uis[0]
	# choose() advances the lore lines first; a big index clamps to the last
	# option, which is always Leave
	ui.choose(999)
	await ticks(6)
	check(not is_instance_valid(ui) or ui.is_queued_for_deletion(), "the panel closed on Leave")
	check(player.state == player.S.MOVE, "control returns to MOVE after leaving")
	check(player.input_enabled, "input is re-enabled after leaving")
	check(_find(get_tree().root, DialogueUI).filter(func(u): return not u.is_queued_for_deletion()).is_empty(),
		"no dialogue lingered / reopened")
	# and talking again still works (not permanently locked out)
	npc._on_talk(player)
	await ticks(2)
	check(player.state == player.S.TALK, "the Chandler will speak again")
	var ui2: Array = _find(get_tree().root, DialogueUI)
	for u in ui2:
		if not u.is_queued_for_deletion():
			(u as DialogueUI).choose(999)
	await ticks(6)
	check(player.input_enabled, "second conversation also released control")

	print("== convex props block, and never trap")
	# the wellhead is freestanding in the open garth (-4.5,0,4.0): approach,
	# get blocked, then walk right back out — proving the capsule never wedges
	player.global_position = Vector3(-4.5, 0.3, 0.5)
	await ticks(3)
	await _push(Vector3(0, 0, 1), 60)
	check(player.global_position.z < 3.6, "convex wellhead blocks (z=%.2f)" % player.global_position.z)
	var wedged_z := player.global_position.z
	await _push(Vector3(0, 0, -1), 40)
	check(player.global_position.z < wedged_z - 1.5, "player walks back OUT — not wedged (z=%.2f)" % player.global_position.z)

	# an urn (small convex prop) also blocks rather than swallowing the capsule
	player.global_position = Vector3(7.3, 0.3, 5.6)
	await ticks(3)
	await _push(Vector3(0, 0, 1), 50)
	check(player.global_position.z < 7.05, "urn blocks the capsule (z=%.2f)" % player.global_position.z)
	var uz := player.global_position.z
	await _push(Vector3(0, 0, -1), 30)
	check(player.global_position.z < uz - 1.0, "and lets go again (z=%.2f)" % player.global_position.z)

	print("== the unwedge safety frees a body spawned inside a prop")
	player.global_position = Vector3(8, 0.3, -8)   # dead center of a solid column
	await ticks(30)
	var probe := player.move_and_collide(Vector3.ZERO, true, 0.001, true)
	check(probe == null or probe.get_depth() <= 0.13,
		"player was pushed clear of the column (depth=%.2f)" % (probe.get_depth() if probe else 0.0))

	print("== lock-on: middle mouse binds it, a hard flick releases")
	check(InputMap.action_has_event("lock_on", _mb(MOUSE_BUTTON_MIDDLE)),
		"middle mouse locks on again")
	player.cam.locked_target = player   # pretend we're locked
	player.cam.mouse_look(Vector2(120, 0))   # a hard flick
	check(player.cam.locked_target == null, "a hard mouse flick breaks the lock")

	print("== block: the guard HOLDS while held, and mitigates a frontal blow")
	player.global_position = Vector3(0, 0.3, 0)
	player._set_state(player.S.MOVE)
	player.hp = player.max_hp
	player.stamina = player.max_stamina
	player.vis.rotation.y = 0.0            # facing -Z
	player.sim_block = true
	await ticks(3)
	check(player.state == player.S.BLOCK, "holding block raises the guard")
	await ticks(60)                        # a full second later...
	check(player.state == player.S.BLOCK, "...the guard is still up (no drop to idle)")
	var hp_before := player.hp
	var pk := DamagePacket.new(30.0, 8.0, null)
	pk.origin = player.global_position + Vector3(0, 0, -2)   # a blow from the front
	var res: String = player.hurtbox.receive(pk)
	check(res == "blocked", "a frontal blow is blocked, not taken raw (%s)" % res)
	check(player.hp > hp_before - 15.0, "blocking cut the damage (hp %.0f -> %.0f)" % [hp_before, player.hp])
	player.sim_block = false
	await ticks(4)
	check(player.state == player.S.MOVE, "releasing block returns to move")

	print("== interact suppression: a menu's closing key-press can't re-open it")
	player.suppress_interact()
	check(not player.try_interact(), "interact is blocked for the frame the menu closed")
	await ticks(6)
	check(player.state == player.S.MOVE, "the suppression clears on its own")

	print("== enemies never strike through a wall (line of sight gates combat)")
	var foe := Enemy.new()
	foe.setup("penitent")
	add_child(foe)
	foe.global_position = Vector3(0, 0.1, 0)
	player.global_position = Vector3(4, 0.3, 0)
	foe.target = player
	await ticks(2)
	check(foe._los_clear(), "clear line of sight across the open")
	var wall := StaticBody3D.new()
	wall.collision_layer = 1 << (VG.L_WORLD_BASE - 1)
	var wcs := CollisionShape3D.new()
	var wb := BoxShape3D.new()
	wb.size = Vector3(0.4, 4.0, 4.0)
	wcs.shape = wb
	wall.add_child(wcs)
	add_child(wall)
	wall.global_position = Vector3(2, 1.5, 0)   # squarely between foe and player
	await ticks(2)
	check(not foe._los_clear(), "a wall between them blocks the strike")
	foe.queue_free()
	wall.queue_free()

	finish()

func _mb(btn: int) -> InputEventMouseButton:
	var e := InputEventMouseButton.new()
	e.button_index = btn
	return e
