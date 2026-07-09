class_name NPC
extends Node3D
## A living soul of the glory state. Faces the Latecomer when near; talk
## opens dialogue with lore + services.

var npc_id := "aveline"
var cfg: Dictionary = {}

var _vis: CharVisual

func _ready() -> void:
	cfg = DB.npc(npc_id)
	cfg["id"] = npc_id
	_vis = CharVisual.new()
	add_child(_vis)
	var body_id: String = cfg.get("body", "skel_sister")
	_vis.build_body(EnemyVisual.BODY_MAP.get(body_id, body_id), 0.8, 0.9)
	# carried prop: the Chandler's lit taper, the Sexton's maul…
	var carry: String = cfg.get("carry", "")
	if carry != "" and KitLib.has_piece(carry):
		var m := _vis.mount("hand_%s" % cfg.get("carry_hand", "l"))
		m.position = Vector3(0, 0.08, 0)
		var held := KitLib.instance(carry)
		if carry == "candle_cluster":
			held.scale = Vector3(0.4, 0.4, 0.4)
		m.add_child(held)
		KitLib.add_flame_lights(held, 1.2, 3.0)
	# the waxbound pray without rising; they do not turn for you
	if cfg.get("pose", "") == "kneel":
		_vis.play("kneel", 0.0)
		set_physics_process(false)
	# a body: you cannot walk through the Chandler
	var tag := String(get_meta("state_tag", "glory"))
	var bit: int = VG.L_WORLD_GLORY if tag == "glory" else (VG.L_WORLD_RUIN if tag == "ruin" else VG.L_WORLD_BASE)
	var body := StaticBody3D.new()
	body.collision_layer = 1 << (bit - 1)
	body.collision_mask = 0
	var bcs := CollisionShape3D.new()
	var bcap := CapsuleShape3D.new()
	bcap.radius = 0.36
	bcap.height = 1.6
	bcs.shape = bcap
	bcs.position.y = 0.85
	body.add_child(bcs)
	add_child(body)
	var zone := Interactable.new()
	zone.prompt = "Speak with %s" % cfg.get("short_name", cfg.get("name", "?"))
	zone.setup_zone(1.8, 1.8)
	zone.activated.connect(_on_talk)
	add_child(zone)

func _physics_process(dt: float) -> void:
	var p = Game.player
	if p != null and global_position.distance_to(p.global_position) < 5.0:
		var to: Vector3 = p.global_position - global_position
		var ty := atan2(-to.x, -to.z)
		# some bodies (char_ward) are authored turned about: flip so the
		# knight greets you with his face, not his pack
		if cfg.get("face_flip", false):
			ty += PI
		_vis.rotation.y = lerp_angle(_vis.rotation.y, ty, 1.0 - exp(-3.0 * dt))

func _on_talk(player) -> void:
	if player == null:
		return
	player.enter_dialogue()
	_vis.play("talk", 0.4)
	var ui := DialogueUI.new(cfg, self)
	ui.tree_exited.connect(func() -> void:
		if is_instance_valid(_vis):
			_vis.back_to_idle(0.4))
	get_tree().root.add_child(ui)
	AudioDirector.sfx("res://assets/audio/ui_tick.wav", -8.0)
