extends Node3D
## The unlit saint in the antechamber: a "Pray" hand at its feet. Kneel,
## and the Scion of Light comes down BEHIND the penitent — what she says
## depends on how much of the Amend is paid:
##   none    - she shuns: the 13th bell is open to you, but unatoned your
##             legacy tarnishes; heed the knight's missive, return to the
##             porch in the world's true ruin
##   partial - earn the rest
##   whole   - she is pleased; the insolence is spent
## Repeatable; each prayer speaks the tier the pilgrim has earned.
##   {"script": ".../pray_shrine.gd", "at": [0,0,70.6], "tag": "base"}

const AMENDS := ["amend_toll", "amend_bell", "amend_larks_thanked",
		"amend_psalm", "amend_ferry"]

const LINES_NONE := [
	"You kneel. How the bell does love to bow, once the ringing is done.",
	"Nothing is paid, Latecomer. Five wardens keep their quarters in the light, and not one has heard your voice. The path of redemption stands open — the THIRTEENTH bell is yours to ring — but ring it unatoned and your legacy is wax and tarnish, remembered only as the hand that silenced the morning.",
	"Heed the knight's missive. Go back down to the porch, stand in the world as it truly lies — in ruin — and read what was left for you. Then seek the wardens, every one.",
]
const LINES_PART := [
	"You kneel better than you did. Some of the debt has found its way home — I have heard them, the ones you answered.",
	"But an office half-sung is still a silence, Latecomer. Earn the rest. Every warden. Then come and kneel again.",
]
const LINES_WHOLE := [
	"...So. Every warden rests answered, every amend made whole. I confess, bell-hand: I did not believe the morning had that much patience in you.",
	"Rise. Whatever the Hour asks of you now, you meet it unashamed — your insolence is spent, and your name will ring clean.",
]


var _busy := false
var _zone: Interactable = null
var _player: Node3D = null
var _scion: CharVisual = null
var _shaft: MeshInstance3D = null
var _cine: Node3D = null
var _cam: Camera3D = null
var _layer: CanvasLayer = null
var _sub: Label = null
var _voice: AudioStreamPlayer3D = null
var _lines: Array = []
var _keys: Array = []
var _line := -1
var _line_t := 0.0

func _ready() -> void:
	_zone = Interactable.new()
	_zone.prompt = "Pray"
	_zone.setup_zone(1.9, 1.8, Vector3(0, 0, -1.3))
	_zone.activated.connect(func(_p): _begin())
	add_child(_zone)

func _amends_done() -> int:
	var n := 0
	for f in AMENDS:
		if World.flag(f):
			n += 1
	return n

## the tier the pilgrim has earned: [lines, voice keys]
func _tier() -> Array:
	var n := _amends_done()
	if n >= AMENDS.size():
		return [LINES_WHOLE, ["c1", "c2"]]
	if n > 0:
		return [LINES_PART, ["b1", "b2"]]
	return [LINES_NONE, ["a1", "a2", "a3"]]

func _begin() -> void:
	if _busy:
		return
	_busy = true
	_zone.enabled = false   # the "Pray" hand has no place inside the vision
	_player = Game.player
	_player.lock_control(true)
	_player.velocity = Vector3.ZERO
	# the penitent kneels facing the saint — the blade has no place in a
	# prayer, so the fist empties for the length of the vision
	var vis: Node3D = _player.get("vis")
	if vis != null:
		vis.rotation.y = atan2(-(global_position.x - _player.global_position.x),
				-(global_position.z - _player.global_position.z))
		vis.play("pray", 0.4)
		var wm: Node3D = vis.get("weapon_mount")
		if wm != null:
			wm.visible = false
	var tier := _tier()
	_lines = tier[0]
	_keys = tier[1]
	_line = -1
	# letterbox
	_layer = CanvasLayer.new()
	_layer.layer = 24
	add_child(_layer)
	for top in [true, false]:
		var bar := ColorRect.new()
		bar.color = Color(0, 0, 0)
		bar.anchor_left = 0.0
		bar.anchor_right = 1.0
		bar.anchor_top = 0.0 if top else 0.88
		bar.anchor_bottom = 0.12 if top else 1.0
		_layer.add_child(bar)
	_sub = Label.new()
	_sub.label_settings = LabelSettings.new()
	_sub.label_settings.font = load("res://assets/fonts/DejaVuSerif.ttf")
	_sub.label_settings.font_size = 26
	_sub.label_settings.font_color = Color(0.95, 0.9, 0.78)
	_sub.label_settings.shadow_color = Color(0, 0, 0, 0.9)
	_sub.label_settings.shadow_size = 4
	_sub.anchor_left = 0.14
	_sub.anchor_right = 0.86
	_sub.anchor_top = 0.76
	_sub.anchor_bottom = 0.87
	_sub.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_sub.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_layer.add_child(_sub)
	# the first shot: low quarter-front, CLOSE on the kneeling penitent — a
	# wide frame this deep in the antechamber catches patrolling guards at
	# the edges and they read as floating debris
	_cine = Node3D.new()
	add_child(_cine)
	_cam = Camera3D.new()
	_cine.add_child(_cam)
	var pp: Vector3 = _player.global_position
	_cam.global_position = pp + Vector3(1.2, 0.95, -1.5)
	_cam.look_at(pp + Vector3(-0.05, 1.0, 0.8))
	_cam.make_current()
	# a breath of stillness, then the light arrives at the penitent's back
	get_tree().create_timer(2.1, false).timeout.connect(_scion_arrives)

func _scion_arrives() -> void:
	var pp: Vector3 = _player.global_position
	var at := pp + Vector3(0, 0, -3.6)   # behind the kneeling pilgrim
	_scion = CharVisual.new()
	add_child(_scion)
	_scion.build_body("skel_ward", 0.92, 1.0)
	var gold := MaterialLib.get_mat("M_gold", 0)
	for mi in _scion.find_children("*", "MeshInstance3D", true, false):
		for s in ((mi as MeshInstance3D).mesh.get_surface_count() if (mi as MeshInstance3D).mesh != null else 0):
			(mi as MeshInstance3D).set_surface_override_material(s, gold)
	_scion.global_position = at + Vector3(0, 7.0, 0)
	_scion.rotation.y = atan2(-(pp.x - at.x), -(pp.z - at.z))
	var lamp := OmniLight3D.new()
	lamp.light_color = Color(1.0, 0.9, 0.6)
	lamp.light_energy = 2.2
	lamp.omni_range = 7.0
	lamp.shadow_enabled = false
	lamp.position.y = 1.3
	_scion.add_child(lamp)
	_shaft = MeshInstance3D.new()
	var cm := CylinderMesh.new()
	cm.top_radius = 0.5
	cm.bottom_radius = 0.85
	cm.height = 11.0
	var sm := StandardMaterial3D.new()
	sm.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	sm.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	sm.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	# thin enough that SHE reads through it — the light frames the herald,
	# it must not consume her
	sm.albedo_color = Color(1.0, 0.94, 0.7, 0.14)
	sm.cull_mode = BaseMaterial3D.CULL_DISABLED
	_shaft.material_override = sm
	_shaft.mesh = cm
	_shaft.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(_shaft)
	_shaft.global_position = at + Vector3(0, 5.5, 0)
	AudioDirector.sfx_at("res://assets/audio/swell_kindle.wav", at, -4.0, 0.85)
	var tw := _scion.create_tween()
	tw.tween_property(_scion, "global_position", at, 1.6) \
		.set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)
	# the second shot: over the penitent's shoulder, up into her light
	var pp2 := _player.global_position
	var ctw := _cam.create_tween()
	ctw.tween_interval(0.7)
	ctw.tween_property(_cam, "global_position", pp2 + Vector3(-1.1, 1.5, 1.9), 1.2) \
		.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	ctw.parallel().tween_method(func(t: float):
		_cam.look_at(pp2.lerp(at + Vector3(0, 1.5, 0), t) + Vector3(0, 1.0, 0)),
		0.0, 1.0, 1.2)
	ctw.tween_callback(_advance)
	set_process(true)

func _process(dt: float) -> void:
	if _line < 0:
		return
	# a line whose voice is still speaking owns the floor — the long
	# judgment (19 s) must never be cut off by an impatient clock
	if _voice != null and is_instance_valid(_voice) and _voice.playing:
		_line_t = 0.0
		return
	_line_t += dt
	# a line that finds no voice yields after a reading's worth of quiet
	if _line_t > maxf(4.0, _sub.text.length() * 0.06):
		_advance()

func _advance() -> void:
	_line += 1
	_line_t = 0.0
	if _line >= _lines.size():
		_end()
		return
	_sub.text = String(_lines[_line])
	if _voice != null and is_instance_valid(_voice):
		_voice.stop()
		_voice.queue_free()
	_voice = AudioStreamPlayer3D.new()
	var path := "res://assets/audio/voice/scion_pray/%s.mp3" % _keys[_line]
	if ResourceLoader.exists(path):
		_voice.stream = load(path)
		_voice.bus = "SFX"
		_voice.volume_db = 3.0
		_voice.max_distance = 40.0
		_scion.add_child(_voice)
		_voice.finished.connect(_advance)
		_voice.play()

func _end() -> void:
	_sub.text = ""
	if _voice != null and is_instance_valid(_voice):
		_voice.stop()
	# she comes apart into motes, upward
	if _scion != null and is_instance_valid(_scion):
		var motes := CPUParticles3D.new()
		motes.amount = 80
		motes.lifetime = 2.0
		motes.one_shot = true
		motes.explosiveness = 0.9
		motes.direction = Vector3.UP
		motes.gravity = Vector3(0, 1.6, 0)
		motes.initial_velocity_min = 0.8
		motes.initial_velocity_max = 2.6
		motes.scale_amount_min = 0.03
		motes.scale_amount_max = 0.07
		var mm := SphereMesh.new()
		mm.radius = 0.04
		mm.height = 0.08
		var mmat := StandardMaterial3D.new()
		mmat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		mmat.albedo_color = Color(1.0, 0.92, 0.66)
		mm.material = mmat
		motes.mesh = mm
		add_child(motes)
		motes.global_position = _scion.global_position + Vector3.UP * 1.1
		motes.emitting = true
		get_tree().create_timer(2.6, false).timeout.connect(motes.queue_free)
		VG.free_gently(_scion)
		_scion = null
	if _shaft != null and is_instance_valid(_shaft):
		var stw := _shaft.create_tween()
		stw.tween_property(_shaft, "scale", Vector3(0.02, 1.0, 0.02), 0.9)
		stw.tween_callback(_shaft.queue_free)
	AudioDirector.sfx("res://assets/audio/swell_kindle.wav", -6.0, 1.3)
	get_tree().create_timer(1.1, false).timeout.connect(func():
		if _cine != null and is_instance_valid(_cine):
			_cine.queue_free()
		if _layer != null and is_instance_valid(_layer):
			_layer.queue_free()
		if _player != null and is_instance_valid(_player):
			var vis: Node3D = _player.get("vis")
			if vis != null:
				vis.back_to_idle(0.5)
				var wm: Node3D = vis.get("weapon_mount")
				if wm != null:
					wm.visible = true
			_player.lock_control(false)
		_line = -1
		_busy = false
		_zone.enabled = true)
