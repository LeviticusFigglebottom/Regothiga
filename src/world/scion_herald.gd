extends Node3D
## The Scion of Light. The first soul to cross the palace threshold is met:
## a radiant figure descends the hall in a shaft of gold, reads the pilgrim,
## names them INFIDEL, and orders the wards of the morning to take up the
## debt on sight — then comes apart into motes. Unskippable in whole; each
## line may be advanced once it has had a breath. Sets "scion_heard".

const LINES := [
	"Be still in the light, pilgrim. You have climbed far above your hour. Let it read you.",
	"...Oh. Oh, no. Bellman. THIRTEENTH of the sworn. The light does not forget a voice, and yours rang twelve of ours to wax.",
	"INFIDEL. The hour you stole is not repaid by walking here in borrowed gold. This house keeps the morning you silenced.",
	"Wards of the morning — hear the light. No guest walks these halls tonight. A debt does. Take it up on sight.",
]
const VOICE_FMT := "res://assets/audio/voice/scion_%02d.mp3"

var trigger_radius := 7.0

var _staged := false
var _line := -1
var _line_at := 0.0
var _clock := 0.0
var _scion: CharVisual = null
var _shaft: MeshInstance3D = null
var _cine: Node3D = null
var _cam: Camera3D = null
var _layer: CanvasLayer = null
var _black: ColorRect = null
var _sub: Label = null
var _voice: AudioStreamPlayer3D = null
var _player: Node3D = null

func _physics_process(_dt: float) -> void:
	_clock += get_physics_process_delta_time()
	if _staged or World.flag("scion_heard"):
		return
	var p = Game.player
	if p == null or not is_instance_valid(p) or p.get("dead") == true:
		return
	if p.global_position.distance_to(global_position) > trigger_radius:
		return
	stage_now()

func stage_now() -> void:
	if _staged:
		return
	_staged = true
	_player = Game.player
	_player.lock_control(true)
	_player.velocity = Vector3.ZERO
	# the herald: a keeper's shape remade in gold, come down the hall's light
	_scion = CharVisual.new()
	add_child(_scion)
	_scion.build_body("skel_ward", 0.96, 1.04)
	var gold := MaterialLib.get_mat("M_gold", 0)
	for n in _scion.find_children("*", "MeshInstance3D", true, false):
		var mi := n as MeshInstance3D
		for s in (mi.mesh.get_surface_count() if mi.mesh != null else 0):
			mi.set_surface_override_material(s, gold)
	var lamp := OmniLight3D.new()
	lamp.light_color = Color(1.0, 0.9, 0.6)
	lamp.light_energy = 2.4
	lamp.omni_range = 7.0
	lamp.shadow_enabled = false
	lamp.position.y = 1.3
	_scion.add_child(lamp)
	# the shaft it rides down
	_shaft = MeshInstance3D.new()
	var cm := CylinderMesh.new()
	cm.top_radius = 0.7
	cm.bottom_radius = 1.1
	cm.height = 12.0
	_shaft.mesh = cm
	var sm := StandardMaterial3D.new()
	sm.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	sm.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	sm.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	sm.albedo_color = Color(1.0, 0.94, 0.7, 0.28)
	sm.cull_mode = BaseMaterial3D.CULL_DISABLED
	_shaft.material_override = sm
	_shaft.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(_shaft)
	var pp: Vector3 = _player.global_position
	var land := Vector3(pp.x, pp.y, pp.z + 3.2)
	_shaft.global_position = land + Vector3(0, 6.0, 0)
	_scion.global_position = land + Vector3(0, 8.0, 0)
	_scion.rotation.y = atan2(-(pp.x - land.x), -(pp.z - land.z))
	if _player.get("vis") != null:
		var face: Vector3 = land - pp
		(_player.get("vis") as Node3D).rotation.y = atan2(-face.x, -face.z)
	_cine_begin()
	AudioDirector.sfx("res://assets/audio/swell_kindle.wav", -2.0, 0.9)
	_scion.play("idle", 0.2)
	var tw := create_tween()
	tw.tween_interval(0.5)
	tw.tween_property(_scion, "global_position", land, 2.6) \
		.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)
	tw.parallel().tween_property(_shaft.material_override, "albedo_color:a", 0.1, 2.6)
	tw.tween_callback(_next_line)

func _cine_begin() -> void:
	_cine = Node3D.new()
	add_child(_cine)
	_cam = Camera3D.new()
	_cam.fov = 52
	_cine.add_child(_cam)
	var pp: Vector3 = _player.global_position
	_cam.global_position = pp + Vector3(3.2, 1.7, 3.0)
	_cam.look_at(pp + Vector3(0, 1.5, 2.2))
	_cam.make_current()
	_layer = CanvasLayer.new()
	_layer.layer = 24
	add_child(_layer)
	_black = ColorRect.new()
	_black.color = Color.BLACK
	_black.set_anchors_preset(Control.PRESET_FULL_RECT)
	_layer.add_child(_black)
	for top in [true, false]:
		var bar := ColorRect.new()
		bar.color = Color.BLACK
		bar.set_anchors_preset(Control.PRESET_TOP_WIDE if top else Control.PRESET_BOTTOM_WIDE)
		if top: bar.offset_bottom = 110
		else: bar.offset_top = -110
		_layer.add_child(bar)
	create_tween().tween_property(_black, "color:a", 0.0, 0.8)
	set_process(true)
	set_process_unhandled_input(true)

func _process(dt: float) -> void:
	if _cam == null or _scion == null or not is_instance_valid(_scion):
		return
	var pp: Vector3 = _player.global_position
	var kp: Vector3 = _scion.global_position
	var mid := (pp + kp) * 0.5 + Vector3(0, 1.5, 0)
	var side := (kp - pp).cross(Vector3.UP)
	side = side.normalized() if side.length() > 0.1 else Vector3.RIGHT
	var want := mid + side * 3.1 + Vector3(0, 0.4, 0)
	_cam.global_position = _cam.global_position.lerp(want, 1.0 - exp(-2.6 * dt))
	_cam.look_at(mid)

func _unhandled_input(event: InputEvent) -> void:
	if _line < 0 or _line >= LINES.size():
		return
	var pressed: bool = (event is InputEventKey and event.pressed) \
			or (event is InputEventMouseButton and event.pressed) \
			or (event is InputEventJoypadButton and event.pressed)
	if pressed and _clock - _line_at > 0.9:
		advance()

func _next_line() -> void:
	_line += 1
	if _line >= LINES.size():
		_end()
		return
	_line_at = _clock
	_show_sub(LINES[_line])
	if _voice != null and is_instance_valid(_voice):
		_voice.stop()
		_voice.queue_free()
		_voice = null
	var path := VOICE_FMT % (_line + 1)
	var idx := _line
	var watchdog := 6.0
	if ResourceLoader.exists(path):
		var a := AudioStreamPlayer3D.new()
		a.stream = load(path)
		a.unit_size = 14.0
		a.max_db = 3.0
		_scion.add_child(a)
		_voice = a
		a.finished.connect(func():
			if _line == idx:
				advance())
		a.play()
		watchdog = maxf(float(a.stream.get_length()) + 0.8, 3.0)
	get_tree().create_timer(watchdog, false).timeout.connect(func():
		if _line == idx:
			advance())

func advance() -> void:
	if _line < 0 or _line >= LINES.size():
		return
	_next_line()

## The judgement is given: the herald comes apart into rising motes and the
## house is hostile from here on.
func _end() -> void:
	World.set_flag("scion_heard")
	World.set_flag("palace_hostile")
	World.save_game()
	_close_sub()
	if _voice != null and is_instance_valid(_voice):
		_voice.stop()
	set_process_unhandled_input(false)
	var k := _scion
	if k != null and is_instance_valid(k):
		var motes := CPUParticles3D.new()
		motes.amount = 140
		motes.lifetime = 2.2
		motes.one_shot = true
		motes.emission_shape = CPUParticles3D.EMISSION_SHAPE_SPHERE
		motes.emission_sphere_radius = 0.8
		motes.direction = Vector3.UP
		motes.spread = 24.0
		motes.initial_velocity_min = 1.6
		motes.initial_velocity_max = 3.4
		motes.gravity = Vector3.ZERO
		motes.scale_amount_min = 0.02
		motes.scale_amount_max = 0.06
		motes.color = Color(1.0, 0.9, 0.6)
		add_child(motes)
		motes.global_position = k.global_position + Vector3.UP * 1.2
		motes.emitting = true
		var dtw := create_tween()
		dtw.tween_method(func(v: float):
			if k != null and is_instance_valid(k):
				_set_dissolve(k, v), 0.0, 1.0, 1.5)
		dtw.parallel().tween_property(_shaft.material_override, "albedo_color:a", 0.0, 1.5)
		dtw.tween_callback(func():
			if k != null and is_instance_valid(k):
				VG.free_gently(k)
			if _shaft != null and is_instance_valid(_shaft):
				_shaft.queue_free())
	var tw := create_tween()
	tw.tween_interval(1.7)
	tw.tween_callback(_cine_end)

func _cine_end() -> void:
	set_process(false)
	if _layer != null and is_instance_valid(_layer):
		var l := _layer
		var b := _black
		var rig := _cine
		var tw := create_tween()
		tw.tween_property(b, "color:a", 1.0, 0.4)
		tw.tween_callback(func():
			if rig != null and is_instance_valid(rig):
				rig.queue_free()
			if _player != null and is_instance_valid(_player):
				_player.lock_control(false))
		tw.tween_property(b, "color:a", 0.0, 0.55)
		tw.tween_callback(l.queue_free)
	_cine = null
	_cam = null
	_layer = null

func _set_dissolve(root: Node, v: float) -> void:
	var stack: Array[Node] = [root]
	while not stack.is_empty():
		var n: Node = stack.pop_back()
		if n is GeometryInstance3D:
			(n as GeometryInstance3D).set_instance_shader_parameter("death_diss", v)
		for c in n.get_children():
			stack.append(c)

func _show_sub(text: String) -> void:
	if _sub == null:
		_sub = Label.new()
		var ls := LabelSettings.new()
		ls.font = load("res://assets/fonts/DejaVuSerif.ttf")
		ls.font_size = 26
		ls.font_color = Color(0.95, 0.91, 0.78)
		ls.shadow_color = Color(0, 0, 0, 0.85)
		ls.shadow_offset = Vector2(1, 2)
		_sub.label_settings = ls
		_sub.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		_sub.vertical_alignment = VERTICAL_ALIGNMENT_BOTTOM
		_sub.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		_sub.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
		_sub.offset_left = 280
		_sub.offset_right = -280
		_sub.offset_top = -250
		_sub.offset_bottom = -26
		_layer.add_child(_sub)
	_sub.text = text
	_sub.visible = true

func _close_sub() -> void:
	if _sub != null and is_instance_valid(_sub):
		_sub.visible = false
