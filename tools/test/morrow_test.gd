extends TestBase
## The Keep of the Morrow: the Stair of Light answers the first prayer,
## twelve trial rooms remember the twelve ringers, twelve kept flags ring
## the blessing, and the blessed hand alone rings the Thirteenth Bell.

var _area: Area

func _build(id: String) -> Area:
	if _area != null and is_instance_valid(_area):
		_area.queue_free()
	_area = AreaBuilder.build(id)
	add_child(_area)
	return _area

func _ready() -> void:
	_run.call_deferred()

func _run() -> void:
	World.reset()
	var player := Player.new()
	add_child(player)
	player.sim_active = true
	player.global_position = Vector3(0, 0.5, 0)
	await ticks(6)

	# ---- the stair answers the prayer, in place
	var sanctum := _build("gilded_sanctum")
	await ticks(6)
	var stair: Node3D = null
	for n in sanctum.glory_layer.get_children():
		if n.get_script() != null and String(n.get_script().resource_path).ends_with("light_stair.gd"):
			stair = n
	check(stair != null, "the stair waits over the west parapet")
	check(stair != null and not stair.visible, "unprayed, no light stands in the air")
	World.set_flag("scion_prayed")
	await ticks(45)
	check(stair != null and stair.visible, "the first prayer raises the stair, no rebuild needed")
	var sportal: AreaPortal = null
	for n in stair.get_children():
		if n is AreaPortal:
			sportal = n
	check(sportal != null and sportal.to_area == "morrow_keep",
			"and its landing opens on the Keep of the Morrow")
	check(sportal != null and sportal._zone.enabled, "the way is armed")

	# ---- the keep: twelve trials, twelve memories
	World.set_flag("amend_sworn")
	var keep := _build("morrow_keep")
	await ticks(8)
	var trial_nodes := 0
	for n in keep.base.get_children():
		if n.get_script() != null and String(n.get_script().resource_path).ends_with("trial_room.gd"):
			trial_nodes += 1
	check(trial_nodes == 7, "seven rooms fight, stand or hold vigil (%d)" % trial_nodes)
	var chimes := 0
	var votives := 0
	var watchers := 0
	for n in keep.base.get_children():
		if n is ChimePuzzle:
			chimes += 1
		elif n is VotiveLock:
			votives += 1
		elif n is WatcherPuzzle:
			watchers += 1
	check(chimes == 2 and votives == 1 and watchers == 2,
			"two songs, one debt of light, two turnings (%d/%d/%d)" % [chimes, votives, watchers])
	var ringers := 0
	var last_door := false
	for n in keep.base.get_children():
		if n is LorePlaque:
			if String(n.text).contains("RINGER"):
				ringers += 1
			if String(n.text).begins_with("THE LAST DOOR"):
				last_door = true
	check(ringers == 12, "twelve ringers are remembered, name and fate (%d)" % ringers)
	check(last_door, "and the last door says what it wants")
	var gate: FlagGate = null
	for n in keep.base.get_children():
		if n is FlagGate:
			gate = n
	check(gate != null and not gate._open, "the last door stands shut against the unblessed")

	# ---- an arena trial fought for real
	player.global_position = Vector3(12, 0.4, 26)   # R4, the Trial of Arms
	await ticks(30)
	var foes: Array = []
	for n in keep.base.get_children():
		if n is Enemy:
			foes.append(n)
	check(foes.size() == 2, "the Fourth's echoes answer the trespass (%d)" % foes.size())
	for e in foes:
		(e as Enemy).died.emit(e)
	await ticks(4)
	check(World.flag("morrow_trial_4"), "both down, the Fourth is satisfied")

	# ---- a vigil held for real (shortened by its own clock)
	var vigil: Node3D = null
	for n in keep.base.get_children():
		if n.get_script() != null and String(n.get_script().resource_path).ends_with("trial_room.gd") \
				and n.get("flag") == "morrow_trial_1":
			vigil = n
	check(vigil != null, "the First's light burns in her room")
	vigil.set("hold", 1.5)
	player.global_position = Vector3(-12, 0.4, 12)
	await ticks(120)
	check(World.flag("morrow_trial_1"), "standing in her light keeps the First's trial")

	# ---- twelve flags ring the blessing and draw the bolt
	for i in 12:
		World.set_flag("morrow_trial_%d" % (i + 1))
	await ticks(45)
	check(World.flag("bell_blessing"), "twelve kept trials ring the blessing")
	check(gate != null and gate._open, "and the last door lets go")

	# ---- the Thirteenth Bell refuses none but the unblessed
	var bell: Node3D = null
	for n in keep.base.get_children():
		if n.get_script() != null and String(n.get_script().resource_path).ends_with("bell_thirteen.gd"):
			bell = n
	check(bell != null, "the Thirteenth hangs at the end of every road")
	World.set_flag("bell_blessing", false)
	bell._try_ring()
	await ticks(4)
	check(not World.flag("bell_thirteen_rung"), "an unblessed hand is refused")
	World.set_flag("bell_blessing")
	bell._try_ring()
	await ticks(320)   # the swing and the whitening take their time
	check(World.flag("bell_thirteen_rung"), "the blessed hand rings the morning in")

	finish()
