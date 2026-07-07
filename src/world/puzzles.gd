class_name ChimePuzzle
extends Node3D
## Ordered-station puzzle: activate the stations in the remembered order and
## a world flag is set (gates, portals and doors listen for it). A wrong note
## resets the round with a dissonant clang; once solved, stations play freely.
## Fully data-authored — the Vesper Chimes ring chime stones ("Ring …"), the
## Larkspire's Daily Offices open lark cages ("Open …", lark-trill voice):
##   kit:      station piece            (default "chime_stone")
##   verb:     interact verb            (default "Ring")
##   swing:    animated child name      (default "chime_bar"; absent = skip)
##   sfx_ring / sfx_wrong: voices       (default bell / dissonant clang)

var flag := "vesper_chimes"
var order: Array = []          # station ids in required order
var _progress := 0
var _stones: Dictionary = {}   # id -> visual root
var _kit := "chime_stone"
var _verb := "Ring"
var _swing_name := "chime_bar"
var _sfx_ring := "res://assets/audio/bell_toll.wav"
var _sfx_wrong := "res://assets/audio/impact_blocked.wav"

func setup(spec: Dictionary) -> void:
	flag = spec.get("flag", "vesper_chimes")
	order.assign(spec.get("order", []))
	_kit = spec.get("kit", "chime_stone")
	_verb = spec.get("verb", "Ring")
	_swing_name = spec.get("swing", "chime_bar")
	_sfx_ring = spec.get("sfx_ring", _sfx_ring)
	_sfx_wrong = spec.get("sfx_wrong", _sfx_wrong)
	for c in spec.get("chimes", []):
		var id: String = c.get("id", "chime")
		var root := Node3D.new()
		root.name = "Station_" + id
		add_child(root)
		root.position = AreaBuilder._v3(c.get("at", [0, 0, 0]))
		root.rotation.y = deg_to_rad(float(c.get("rot", 0)))
		var piece := KitLib.instance(c.get("kit", _kit))
		root.add_child(piece)
		KitLib.add_collision(piece, VG.L_WORLD_BASE)
		var zone := Interactable.new()
		zone.prompt = "%s %s" % [_verb, c.get("label", id)]
		zone.setup_zone(1.6, 1.5)
		zone.activated.connect(func(_p): _ring(id))
		root.add_child(zone)
		_stones[id] = root

func _ring(id: String) -> void:
	var idx := order.find(id)
	var pitch := 0.8 + 0.25 * maxf(idx, 0.0)
	AudioDirector.sfx_at(_sfx_ring, _stones[id].global_position, -6.0, pitch)
	_swing(_stones[id])
	if World.flag(flag):
		return   # already solved; ring for the joy of it
	if order.is_empty():
		return
	if id == order[_progress]:
		_progress += 1
		if _progress >= order.size():
			World.set_flag(flag)
			World.save_game()
			_fanfare()
	else:
		if _progress > 0:
			# dissonance: the round collapses
			AudioDirector.sfx_at(_sfx_wrong, _stones[id].global_position, -2.0, 0.5)
		_progress = 1 if id == order[0] else 0

func _swing(root: Node3D) -> void:
	var bar := root.find_child(_swing_name, true, false)
	if bar == null:
		return
	var tw := create_tween()
	tw.tween_property(bar, "rotation:x", 0.5, 0.12)
	tw.tween_property(bar, "rotation:x", 0.0, 0.9) \
		.set_trans(Tween.TRANS_ELASTIC).set_ease(Tween.EASE_OUT)

func _fanfare() -> void:
	for id in _stones:
		var burst := CPUParticles3D.new()
		burst.amount = 40
		burst.lifetime = 1.2
		burst.one_shot = true
		burst.explosiveness = 1.0
		burst.direction = Vector3.UP
		burst.spread = 40.0
		burst.initial_velocity_min = 1.5
		burst.initial_velocity_max = 3.5
		burst.gravity = Vector3(0, -2.0, 0)
		burst.scale_amount_min = 0.02
		burst.scale_amount_max = 0.06
		var q := QuadMesh.new()
		q.size = Vector2(0.2, 0.2)
		var qm := StandardMaterial3D.new()
		qm.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		qm.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
		qm.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
		qm.albedo_color = Color(1.0, 0.85, 0.45, 0.8)
		q.material = qm
		burst.mesh = q
		_stones[id].add_child(burst)
		burst.position.y = 2.0
		burst.emitting = true
	AudioDirector.sfx("res://assets/audio/remembrance.wav", 0.0, 0.8)
	await get_tree().create_timer(0.5, false).timeout
	AudioDirector.sfx("res://assets/audio/bell_toll.wav", -2.0, 1.5)
