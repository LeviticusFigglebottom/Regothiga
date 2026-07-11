extends NPC
## A warden put to rest, standing again in the light his quarters remember.
## Appears only after the Amend is sworn (Adalric's note) AND his own veil
## has fallen (boss slain). Each carries one amend:
##   toll  — ten thousand orisons of penance
##   bell  — three fragments of his bell, carried home
##   lark  — the ruined cages below, opened at last
##   psalm — her anthem fetched down and delivered twice
##   ferry — one last crossing, paid in full
##   {"script": ".../radiant_warden.gd", "at": [...], "tag": "glory",
##    "require_flag": "amend_sworn",
##    "params": {"warden": "bell", "arena": "gray_cloister", "scale": 1.3}}

var warden := "bell"
var arena := ""
var scale_mult := 1.3
var fight_at: Array = []          # ferry only: where the refight stands

var _fight: Enemy = null

const DONE_FLAGS := ["amend_toll", "amend_bell", "amend_larks_thanked",
		"amend_psalm", "amend_ferry"]

func _ready() -> void:
	# a warden still standing his first watch cannot also stand his second
	if arena != "" and not World.is_cleared(arena):
		queue_free()
		return
	if warden == "ferry" and World.flag("amend_ferry"):
		queue_free()      # he got his rest; the jetty keeps only water now
		return
	npc_id = "warden_" + warden
	super._ready()
	_vis.scale = Vector3.ONE * scale_mult
	# the remembered echo yields to the true remembered soul: while the
	# radiant Bellkeeper stands his quarters, his glory-cameo stands down
	if warden == "bell":
		_clear_cameos.call_deferred()
	# the radiance: a halo's warmth, motes rising off the shoulders
	var l := OmniLight3D.new()
	l.light_color = Color(1.0, 0.9, 0.62)
	l.light_energy = 1.6
	l.omni_range = 5.0
	l.shadow_enabled = false
	l.position.y = 1.6 * scale_mult
	add_child(l)
	var motes := CPUParticles3D.new()
	motes.amount = 26
	motes.lifetime = 2.6
	motes.emission_shape = CPUParticles3D.EMISSION_SHAPE_SPHERE
	motes.emission_sphere_radius = 0.55 * scale_mult
	motes.direction = Vector3.UP
	motes.gravity = Vector3(0, 0.4, 0)
	motes.initial_velocity_min = 0.15
	motes.initial_velocity_max = 0.45
	motes.scale_amount_min = 0.02
	motes.scale_amount_max = 0.05
	var mm := SphereMesh.new()
	mm.radius = 0.03
	mm.height = 0.06
	var mmat := StandardMaterial3D.new()
	mmat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mmat.albedo_color = Color(1.0, 0.92, 0.66)
	mm.material = mmat
	motes.mesh = mm
	motes.position.y = 1.0 * scale_mult
	add_child(motes)
	Game.player_respawned.connect(_on_player_respawn)

func _clear_cameos() -> void:
	var root := get_parent()
	while root != null and not root is Area:
		root = root.get_parent()
	if root == null:
		return
	for n in (root as Area).find_children("*", "BellkeeperCameo", true, false):
		n.queue_free()

# ---------------------------------------------------------------- stages
func _asked_flag() -> String:
	return "amend_%s_asked" % warden

func _on_talk(player) -> void:
	if player == null:
		return
	var asked := World.flag(_asked_flag())
	var lines: Array
	var services: Array = []
	match warden:
		"toll":
			if World.flag("amend_toll"):
				lines = cfg.get("lines_done_repeat", [])
			elif asked:
				lines = cfg.get("lines_waiting", [])
				services = [{"type": "rite", "id": "pay",
					"label": "Pay the penance — 10,000 orisons"}]
			else:
				lines = cfg.get("lines_first", [])
		"bell":
			var frags := int(player.inventory.get("bell_fragment", 0))
			if World.flag("amend_bell"):
				lines = cfg.get("lines_done_repeat", [])
			elif asked:
				lines = cfg.get("lines_waiting", [])
				if frags >= 3:
					services = [{"type": "rite", "id": "give",
						"label": "Give the three fragments home"}]
			else:
				lines = cfg.get("lines_first", [])
		"lark":
			if World.flag("amend_larks_thanked"):
				lines = cfg.get("lines_done_repeat", [])
			elif World.flag("amend_larks"):
				lines = cfg.get("lines_done", [])
				World.set_flag("amend_larks_thanked")
				_grant(600, "radiant_token", "The Larkwarden's amend is made.")
			elif asked:
				lines = cfg.get("lines_waiting", [])
			else:
				lines = cfg.get("lines_first", [])
		"psalm":
			if World.flag("amend_psalm"):
				lines = cfg.get("lines_done_repeat", [])
			elif World.flag("amend_psalm_a") and World.flag("amend_psalm_b"):
				lines = cfg.get("lines_done", [])
				World.set_flag("amend_psalm")
				_grant(600, "radiant_token", "The Precentress's amend is made.")
			elif asked:
				lines = cfg.get("lines_waiting", [])
			else:
				lines = cfg.get("lines_first", [])
		"ferry":
			if asked:
				lines = cfg.get("lines_waiting", [])
			else:
				lines = cfg.get("lines_first", [])
			services = [{"type": "rite", "id": "fare", "close": true,
				"label": "Pay the last fare — face the Ferryman"}]
	if not asked:
		World.set_flag(_asked_flag())
		World.save_game()
	cfg["lines_first"] = lines
	cfg["lines_repeat"] = lines
	cfg["services"] = services
	super._on_talk(player)

# ---------------------------------------------------------------- rites
func _rite(o: Dictionary) -> String:
	var p = Game.player
	match String(o.get("id", "")):
		"pay":
			if Game.orisons < 10000:
				return "Ten thousand, Latecomer. You stand %d short. The gate has waited a kingdom's age; it can wait your errands too." % (10000 - Game.orisons)
			Game.add_orisons(-10000)
			World.set_flag("amend_toll")
			World.save_game()
			p.give_item("penance_writ", 1)
			p.give_item("radiant_token", 1)
			Game.toast.emit("Penance paid — the Tollkeeper's amend is made.")
			AudioDirector.sfx("res://assets/audio/bell_toll.wav", -4.0, 0.9)
			_check_whole()
			return "Weighed. Entered. Discharged. Take the writ — the last page of the old ledger, closed at last by your hand."
		"give":
			if int(p.inventory.get("bell_fragment", 0)) < 3:
				return "Three pieces make a bell. Count again."
			p.inventory["bell_fragment"] = int(p.inventory["bell_fragment"]) - 3
			p.inventory_changed.emit()
			World.set_flag("amend_bell")
			World.save_game()
			_assemble_bell()
			Game.toast.emit("The bell made whole — the Bellkeeper's amend is made.")
			_grant(800, "radiant_token", "")
			_check_whole()
			return "Whole. WHOLE. Do you hear it, Latecomer? The hour comes back to me like a name I misplaced."
		"fare":
			_begin_ferry_fight.call_deferred()
			return "Then stand off the boards, and come at me like the tide."
	return "..."

## every amend made: the kingdom notices
func _check_whole() -> void:
	for f in DONE_FLAGS:
		if not World.flag(f):
			return
	if World.flag("amend_whole"):
		return
	World.set_flag("amend_whole")
	World.save_game()
	Game.toast.emit("THE AMEND IS MADE WHOLE — every warden rests in the light.")
	AudioDirector.sfx("res://assets/audio/swell_kindle.wav", 0.0, 0.7)

func _grant(orisons: int, item: String, toast: String) -> void:
	if orisons > 0:
		Game.add_orisons(orisons)
	if item != "" and Game.player != null:
		Game.player.give_item(item, 1)
	if toast != "":
		Game.toast.emit(toast)
	_check_whole()

## the bell, remade: it settles over his stand and speaks once
func _assemble_bell() -> void:
	if not KitLib.has_piece("bell_great"):
		return
	var bell := KitLib.instance("bell_great")
	add_child(bell)
	bell.position = Vector3(0, 3.4, -1.2)
	bell.scale = Vector3(0.01, 0.01, 0.01)
	var tw := bell.create_tween()
	tw.tween_property(bell, "scale", Vector3(0.8, 0.8, 0.8), 1.2) \
		.set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	tw.tween_callback(func():
		AudioDirector.sfx_at("res://assets/audio/bell_toll.wav", global_position, 0.0, 1.0))

# ---------------------------------------------------------------- ferry
func _begin_ferry_fight() -> void:
	if _fight != null and is_instance_valid(_fight):
		return
	visible = false
	for z in find_children("*", "Interactable", true, false):
		(z as Interactable).enabled = false
	_fight = Enemy.new()
	_fight.setup("ferryman_rested")
	get_parent().add_child(_fight)
	var at := global_position
	if fight_at.size() == 3:
		at = Vector3(fight_at[0], fight_at[1], fight_at[2])
	_fight.global_position = at
	_fight.target = Game.player
	_fight._set_state(Enemy.ES.ALERT)
	AudioDirector.boss_theme("ferryman", 1.5)
	for hud in get_tree().get_nodes_in_group("hud"):
		hud.show_boss(_fight)
	_fight.died.connect(_ferry_rested)

func _ferry_rested(_e) -> void:
	World.set_flag("amend_ferry")
	World.save_game()
	for hud in get_tree().get_nodes_in_group("hud"):
		hud.hide_boss()
	AudioDirector.play_music("", 2.0)
	# the soul goes down with the boat: a column of fare-light off the water
	if _fight != null and is_instance_valid(_fight):
		var motes := CPUParticles3D.new()
		motes.amount = 90
		motes.lifetime = 2.4
		motes.one_shot = true
		motes.explosiveness = 0.9
		motes.direction = Vector3.UP
		motes.gravity = Vector3(0, 1.2, 0)
		motes.initial_velocity_min = 1.0
		motes.initial_velocity_max = 3.2
		motes.scale_amount_min = 0.03
		motes.scale_amount_max = 0.08
		var mm := SphereMesh.new()
		mm.radius = 0.04
		mm.height = 0.08
		var mmat := StandardMaterial3D.new()
		mmat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		mmat.albedo_color = Color(1.0, 0.92, 0.66)
		mm.material = mmat
		motes.mesh = mm
		get_parent().add_child(motes)
		motes.global_position = _fight.global_position + Vector3.UP * 1.2
		motes.emitting = true
		get_tree().create_timer(3.0, false).timeout.connect(motes.queue_free)
	if Game.player != null:
		Game.player.give_item("radiant_token", 1)
	Game.toast.emit("The Ferryman rests — his amend is made, and yours with it.")
	_check_whole()
	queue_free()

func _on_player_respawn() -> void:
	# the fare went unpaid: the fight resets and the warden keeps his jetty
	if _fight != null and is_instance_valid(_fight) and not _fight.dead:
		_fight.queue_free()
		_fight = null
		visible = true
		for z in find_children("*", "Interactable", true, false):
			(z as Interactable).enabled = true
		for hud in get_tree().get_nodes_in_group("hud"):
			hud.hide_boss()
