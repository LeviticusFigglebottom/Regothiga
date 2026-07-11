extends Node3D
## The Larkwarden's amend, done with living hands: down in the ruin, where
## the cages truly stand, every door he shut is opened. Built ALWAYS (the
## warden is spoken to in this same tower — no rebuild happens between his
## word and the deed), the cage doors arm themselves the moment his word
## is given. Each opening swings the grate, shakes the old cage, and lets
## a remembered lark climb out on beating wings. All open -> flag.
##   {"script": ".../amend_larks.gd", "at": [0,0,0], "tag": "ruin",
##    "params": {"flag": "amend_larks", "asked_flag": "amend_lark_asked",
##               "cages": [[0.8,9.59,-2], ...]}}

var flag := "amend_larks"
var asked_flag := "amend_lark_asked"
var cages: Array = []

var _zones: Array = []
var _opened: Array = []
var _armed := false

func _ready() -> void:
	if World.flag(flag):
		return
	for i in cages.size():
		var at: Array = cages[i]
		var z := Interactable.new()
		z.prompt = "Open the cage"
		z.setup_zone(1.5, 1.6)
		var idx := i
		z.activated.connect(func(_p): _free(idx, z))
		add_child(z)
		z.position = Vector3(at[0], at[1], at[2]) - position
		z.enabled = false
		_zones.append(z)
		_opened.append(false)
	_arm_when_asked()

## his word may come while we already stand built — listen for it
func _arm_when_asked() -> void:
	if World.flag(asked_flag):
		_arm()
		return
	var t := Timer.new()
	t.wait_time = 0.5
	t.timeout.connect(func():
		if not _armed and World.flag(asked_flag):
			_arm()
			t.queue_free())
	add_child(t)
	t.start()

func _arm() -> void:
	_armed = true
	for z in _zones:
		(z as Interactable).enabled = true

func _free(i: int, zone: Interactable) -> void:
	if _opened[i] or World.flag(flag):
		return
	_opened[i] = true
	zone.enabled = false
	var at := zone.global_position
	_open_cage(at)
	# the lark waits a breath for the door, then goes
	get_tree().create_timer(0.55, false).timeout.connect(func(): _bird(at))
	var freed := 0
	for v in _opened:
		if v:
			freed += 1
	if freed >= _opened.size():
		World.set_flag(flag)
		World.save_game()
		Game.toast.emit("The last cage stands open. Somewhere above, a warden hears the quiet.")
		AudioDirector.sfx("res://assets/audio/swell_kindle.wav", -4.0, 1.2)
	else:
		Game.toast.emit("%d of %d cages opened." % [freed, _opened.size()])

## the door made real: the old cage shudders on its hook and a grate panel
## swings wide on its hinge — the nearest cage prop lends its body to the
## shake so the opening reads on the actual bars
func _open_cage(at: Vector3) -> void:
	AudioDirector.sfx_at("res://assets/audio/impact_blocked.wav", at, -14.0, 0.7)
	var cage := _nearest_cage(at)
	if cage != null:
		var base_rot: Vector3 = cage.rotation
		var tw := cage.create_tween()
		tw.tween_property(cage, "rotation:z", base_rot.z + 0.06, 0.09)
		tw.tween_property(cage, "rotation:z", base_rot.z - 0.05, 0.09)
		tw.tween_property(cage, "rotation:z", base_rot.z + 0.02, 0.08)
		tw.tween_property(cage, "rotation:z", base_rot.z, 0.08)
	# the grate: a barred panel hinged at its edge, swinging open
	var hinge := Node3D.new()
	get_parent().add_child(hinge)
	hinge.global_position = at + Vector3(0.22, 0.55, 0.16)
	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color(0.2, 0.19, 0.18)
	mat.roughness = 0.7
	mat.metallic = 0.4
	for k in 4:
		var bar := MeshInstance3D.new()
		var bm := BoxMesh.new()
		bm.size = Vector3(0.025, 0.5, 0.02)
		bm.material = mat
		bar.mesh = bm
		bar.position = Vector3(-0.05 - 0.09 * k, 0, 0)
		hinge.add_child(bar)
	var rail := MeshInstance3D.new()
	var rm := BoxMesh.new()
	rm.size = Vector3(0.4, 0.03, 0.02)
	rm.material = mat
	rail.mesh = rm
	rail.position = Vector3(-0.185, 0.22, 0)
	hinge.add_child(rail)
	var tw2 := hinge.create_tween()
	tw2.tween_property(hinge, "rotation:y", deg_to_rad(-115), 0.5) \
		.set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	tw2.tween_interval(2.6)
	tw2.tween_property(hinge, "scale", Vector3(0.02, 0.02, 0.02), 0.6)
	tw2.tween_callback(hinge.queue_free)

func _nearest_cage(at: Vector3) -> Node3D:
	var root := get_parent()
	while root != null and not root is Area:
		root = root.get_parent()
	if root == null:
		return null
	var best: Node3D = null
	var best_d := 2.2
	for n in (root as Area).find_children("*lark_cage*", "", true, false):
		if n is Node3D and n.is_visible_in_tree():
			var d: float = (n as Node3D).global_position.distance_to(at)
			if d < best_d:
				best_d = d
				best = n
	return best

## a remembered lark: it hops to the door, beats its wings, and flies a
## true climbing arc away over the rail — banking, flapping, gone to light
func _bird(at: Vector3) -> void:
	AudioDirector.sfx_at("res://assets/audio/lark_trill.wav", at, -4.0,
			randf_range(0.95, 1.15))
	var bird := Node3D.new()
	get_parent().add_child(bird)
	bird.global_position = at + Vector3(0.25, 0.55, 0.2)
	var mat := StandardMaterial3D.new()
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mat.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	mat.albedo_color = Color(1.0, 0.9, 0.55, 0.95)
	var body := MeshInstance3D.new()
	var bm := PrismMesh.new()
	bm.size = Vector3(0.1, 0.07, 0.2)
	bm.material = mat
	body.mesh = bm
	body.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	bird.add_child(body)
	var wings: Array = []
	for s in [-1.0, 1.0]:
		var pivot := Node3D.new()
		pivot.position = Vector3(s * 0.05, 0.02, 0)
		bird.add_child(pivot)
		var wing := MeshInstance3D.new()
		var wm := PrismMesh.new()
		wm.size = Vector3(0.2, 0.015, 0.11)
		wm.material = mat
		wing.mesh = wm
		wing.position = Vector3(s * 0.11, 0, 0)
		wing.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		pivot.add_child(wing)
		wings.append(pivot)
	var l := OmniLight3D.new()
	l.light_color = Color(1.0, 0.9, 0.6)
	l.light_energy = 1.0
	l.omni_range = 2.6
	l.shadow_enabled = false
	bird.add_child(l)
	# the wingbeat: both pivots flap in opposition, looped for the flight
	for wi in wings.size():
		var s := -1.0 if wi == 0 else 1.0
		var wtw := (wings[wi] as Node3D).create_tween()
		wtw.set_loops(14)
		wtw.tween_property(wings[wi], "rotation:z", s * 0.85, 0.09) \
			.set_trans(Tween.TRANS_SINE)
		wtw.tween_property(wings[wi], "rotation:z", s * -0.5, 0.09) \
			.set_trans(Tween.TRANS_SINE)
	# the flight: a hop up off the door, then a banking climb away
	var dir := Vector3(randf_range(-1.0, 1.0), 0, randf_range(-1.0, 1.0)).normalized()
	var hop := bird.global_position + Vector3(0, 0.5, 0) + dir * 0.4
	var away := bird.global_position + dir * 9.0 + Vector3(0, 8.5, 0)
	bird.look_at(bird.global_position + dir, Vector3.UP)
	var tw := bird.create_tween()
	tw.tween_property(bird, "global_position", hop, 0.35) \
		.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	tw.tween_property(bird, "global_position", away, 2.3) \
		.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
	tw.parallel().tween_property(bird, "rotation:z", randf_range(-0.5, 0.5), 2.3)
	tw.parallel().tween_property(mat, "albedo_color:a", 0.0, 1.4).set_delay(1.2)
	tw.tween_callback(bird.queue_free)
