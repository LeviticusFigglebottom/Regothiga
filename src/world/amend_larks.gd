extends Node3D
## The Larkwarden's amend, done with living hands: down in the ruin, where
## the cages truly stand, every door he shut is opened. The cages are the
## Daily Offices' own stations — Matins, Sext, Vespers — the same gilded
## cages the puzzle rang. Built ALWAYS (the warden is spoken to in this same
## tower — no rebuild happens between his word and the deed), the cage doors
## arm themselves the moment his word is given; while armed, the offices'
## own "Open" hand yields the floor. Each opening cants the old cage in a
## burst of gold dust and lets its remembered lark climb out on beating
## wings. All open -> flag.
##   {"script": ".../amend_larks.gd", "at": [0,0,0], "tag": "ruin",
##    "params": {"flag": "amend_larks", "asked_flag": "amend_lark_asked",
##               "stations": ["matins", "sext", "vespers"]}}

var flag := "amend_larks"
var asked_flag := "amend_lark_asked"
var stations: Array = []

var _zones: Array = []
var _cages: Array = []   # station roots, shared with the offices puzzle
var _opened: Array = []
var _armed := false

func _ready() -> void:
	if World.flag(flag):
		return
	# the puzzle raises its stations in the same build pass — wait it out
	_setup.call_deferred()

func _setup() -> void:
	var root := get_parent()
	while root != null and not root is Area:
		root = root.get_parent()
	if root == null:
		return
	for id in stations:
		var st := (root as Area).find_child("Station_" + String(id), true, false)
		if st == null or not st is Node3D:
			continue
		var z := Interactable.new()
		z.prompt = "Free the lark"
		z.setup_zone(1.5, 1.6)
		var idx := _zones.size()
		z.activated.connect(func(_p): _free(idx))
		add_child(z)
		z.global_position = (st as Node3D).global_position
		z.enabled = false
		_zones.append(z)
		_cages.append(st)
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
	for i in _zones.size():
		(_zones[i] as Interactable).enabled = true
		# the offices are sung; while the amend stands open, their "Open"
		# hand steps aside so one cage never begs two answers
		for c in (_cages[i] as Node3D).get_children():
			if c is Interactable:
				(c as Interactable).enabled = false

func _free(i: int) -> void:
	if _opened[i] or World.flag(flag):
		return
	_opened[i] = true
	(_zones[i] as Interactable).enabled = false
	var st := _cages[i] as Node3D
	var at := st.global_position
	_open_cage(st, at)
	# the lark waits half a breath for the door, then goes
	get_tree().create_timer(0.25, false).timeout.connect(func(): _bird(at))
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

## the door made real: the gilded cage is knocked wide on its stand — it
## shudders, settles ajar, and its remembered occupant stops being caged
func _open_cage(st: Node3D, at: Vector3) -> void:
	AudioDirector.sfx_at("res://assets/audio/impact_blocked.wav", at, -14.0, 0.7)
	var cage := st.find_child("stand_cage*", true, false)
	if cage != null:
		var tw := create_tween()
		tw.tween_property(cage, "rotation:x", 0.45, 0.12)
		tw.tween_property(cage, "rotation:x", 0.12, 0.9) \
			.set_trans(Tween.TRANS_ELASTIC).set_ease(Tween.EASE_OUT)
	# the caged bird gives its shape to the one that flies
	for lark in st.find_children("stand_lark*", "", true, false):
		if lark is Node3D:
			(lark as Node3D).visible = false
	# a burst of gold dust where the door gives — the opening, made of light
	var puff := CPUParticles3D.new()
	puff.amount = 24
	puff.lifetime = 0.9
	puff.one_shot = true
	puff.explosiveness = 1.0
	puff.direction = Vector3.UP
	puff.spread = 70.0
	puff.gravity = Vector3(0, -1.2, 0)
	puff.initial_velocity_min = 0.6
	puff.initial_velocity_max = 1.6
	puff.scale_amount_min = 0.02
	puff.scale_amount_max = 0.05
	var pm := SphereMesh.new()
	pm.radius = 0.03
	pm.height = 0.06
	var pmat := StandardMaterial3D.new()
	pmat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	pmat.albedo_color = Color(1.0, 0.9, 0.6)
	pm.material = pmat
	puff.mesh = pm
	get_parent().add_child(puff)
	puff.global_position = at + Vector3(0, 1.25, 0)
	puff.emitting = true
	get_tree().create_timer(1.6, false).timeout.connect(puff.queue_free)

## a remembered lark: it hops from the cage mouth, beats its wings, and
## flies a true climbing arc away over the rail — banking, flapping, gone
func _bird(at: Vector3) -> void:
	AudioDirector.sfx_at("res://assets/audio/lark_trill.wav", at, -4.0,
			randf_range(0.95, 1.15))
	var bird := Node3D.new()
	get_parent().add_child(bird)
	bird.global_position = at + Vector3(0.1, 1.28, 0.1)
	var mat := StandardMaterial3D.new()
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mat.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	mat.albedo_color = Color(1.0, 0.9, 0.55, 0.95)
	var body := MeshInstance3D.new()
	var bm := PrismMesh.new()
	bm.size = Vector3(0.16, 0.11, 0.32)
	bm.material = mat
	body.mesh = bm
	body.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	bird.add_child(body)
	var wings: Array = []
	for s in [-1.0, 1.0]:
		var pivot := Node3D.new()
		pivot.position = Vector3(s * 0.08, 0.03, 0)
		bird.add_child(pivot)
		var wing := MeshInstance3D.new()
		var wm := PrismMesh.new()
		wm.size = Vector3(0.34, 0.02, 0.18)
		wm.material = mat
		wing.mesh = wm
		wing.position = Vector3(s * 0.19, 0, 0)
		wing.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		pivot.add_child(wing)
		wings.append(pivot)
	var l := OmniLight3D.new()
	l.light_color = Color(1.0, 0.9, 0.6)
	l.light_energy = 2.4
	l.omni_range = 4.5
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
	var away := bird.global_position + dir * 11.0 + Vector3(0, 9.5, 0)
	bird.look_at(bird.global_position + dir, Vector3.UP)
	var tw := bird.create_tween()
	tw.tween_property(bird, "global_position", hop, 0.35) \
		.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	tw.tween_property(bird, "global_position", away, 2.8) \
		.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
	tw.parallel().tween_property(bird, "rotation:z", randf_range(-0.5, 0.5), 2.8)
	tw.parallel().tween_property(mat, "albedo_color:a", 0.0, 1.2).set_delay(1.9)
	tw.tween_callback(bird.queue_free)
