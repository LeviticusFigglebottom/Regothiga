extends Node3D
## The world breathing: cheap ambient dressing that makes the glory feel
## inhabited and the ruin feel abandoned — which is the whole juxtaposition.
##   kind "motes_gold" — sunlit dust rising slowly through the air (glory)
##   kind "motes_ash"  — ash sifting downward (ruin)
##   kind "birds"      — a few ground birds pecking; they burst up and away
##                       when the pilgrim comes near
##   {"script": ".../ambient_life.gd", "at": [cx, y, cz], "tag": "glory",
##    "params": {"kind": "motes_gold", "extent": [20, 6, 20], "count": 26}}

var kind := "motes_gold"
var extent: Array = [20, 6, 20]
var count := 26

var _birds: Array = []   # [{root, wings: [l, r], home: Vector3, fled: bool}]

func _ready() -> void:
	match kind:
		"motes_gold", "motes_ash":
			_build_motes(kind == "motes_ash")
		"birds":
			_build_birds()

func _build_motes(ash: bool) -> void:
	var p := CPUParticles3D.new()
	p.amount = count
	p.lifetime = 11.0
	p.preprocess = 11.0
	p.emission_shape = CPUParticles3D.EMISSION_SHAPE_BOX
	p.emission_box_extents = Vector3(extent[0] * 0.5, extent[1] * 0.5, extent[2] * 0.5)
	p.direction = Vector3(0, -1, 0) if ash else Vector3(0, 1, 0)
	p.spread = 20.0
	p.gravity = Vector3(0, -0.06, 0) if ash else Vector3(0, 0.02, 0)
	p.initial_velocity_min = 0.05
	p.initial_velocity_max = 0.16
	p.scale_amount_min = 0.015
	p.scale_amount_max = 0.05 if ash else 0.035
	var m := QuadMesh.new()
	m.size = Vector2(0.06, 0.06)
	var mat := StandardMaterial3D.new()
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED
	if ash:
		mat.albedo_color = Color(0.32, 0.29, 0.26, 0.7)
	else:
		mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
		mat.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
		mat.albedo_color = Color(1.0, 0.9, 0.6, 0.5)
	m.material = mat
	p.mesh = m
	p.position.y = extent[1] * 0.5
	add_child(p)
	p.emitting = true

func _build_birds() -> void:
	var rng := RandomNumberGenerator.new()
	rng.seed = int(global_position.x * 13 + global_position.z * 7)
	for i in count:
		var home := Vector3(rng.randf_range(-extent[0] * 0.5, extent[0] * 0.5), 0.06,
				rng.randf_range(-extent[2] * 0.5, extent[2] * 0.5))
		var bird := Node3D.new()
		add_child(bird)
		bird.position = home
		bird.rotation.y = rng.randf_range(0, TAU)
		var mat := StandardMaterial3D.new()
		mat.albedo_color = Color(0.42, 0.38, 0.34) if rng.randf() < 0.5 \
				else Color(0.55, 0.5, 0.42)
		var body := MeshInstance3D.new()
		var bm := PrismMesh.new()
		bm.size = Vector3(0.12, 0.09, 0.24)
		bm.material = mat
		body.mesh = bm
		body.position.y = 0.07
		body.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		bird.add_child(body)
		var wings: Array = []
		for sd in [-1.0, 1.0]:
			var pivot := Node3D.new()
			pivot.position = Vector3(sd * 0.05, 0.1, 0)
			bird.add_child(pivot)
			var wing := MeshInstance3D.new()
			var wm := PrismMesh.new()
			wm.size = Vector3(0.22, 0.015, 0.13)
			wm.material = mat
			wing.mesh = wm
			wing.position = Vector3(sd * 0.12, 0, 0)
			wing.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
			pivot.add_child(wing)
			wings.append(pivot)
		# the peck: a little bow, now and then
		var tw := bird.create_tween()
		tw.set_loops(0)
		tw.tween_interval(rng.randf_range(0.8, 2.2))
		tw.tween_property(body, "rotation:x", 0.5, 0.16)
		tw.tween_property(body, "rotation:x", 0.0, 0.2)
		_birds.append({"root": bird, "wings": wings, "fled": false})

func _physics_process(_dt: float) -> void:
	if kind != "birds":
		set_physics_process(false)
		return
	var p = Game.player
	if p == null:
		return
	var all_fled := true
	for b in _birds:
		if b["fled"]:
			continue
		all_fled = false
		var root: Node3D = b["root"]
		if root.global_position.distance_to(p.global_position) < 3.4:
			b["fled"] = true
			_fly_off(root, b["wings"])
	if all_fled:
		set_physics_process(false)

func _fly_off(bird: Node3D, wings: Array) -> void:
	AudioDirector.sfx_at("res://assets/audio/lark_trill.wav", bird.global_position,
			-14.0, randf_range(1.1, 1.35))
	for wi in wings.size():
		var sd := -1.0 if wi == 0 else 1.0
		var wtw := (wings[wi] as Node3D).create_tween()
		wtw.set_loops(12)
		wtw.tween_property(wings[wi], "rotation:z", sd * 0.9, 0.08)
		wtw.tween_property(wings[wi], "rotation:z", sd * -0.45, 0.08)
	var away := Vector3(randf_range(-1, 1), 0, randf_range(-1, 1)).normalized()
	var to := bird.global_position + away * 9.0 + Vector3(0, 8.0, 0)
	bird.look_at(bird.global_position + away, Vector3.UP)
	var tw := bird.create_tween()
	tw.tween_property(bird, "global_position", to, 2.2) \
		.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
	tw.tween_callback(bird.queue_free)
