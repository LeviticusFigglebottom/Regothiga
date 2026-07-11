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

## Whatever the pilgrim has or hasn't done, the road itself is never
## refused: every audience OPENS with the way to the thirteenth bell.
## The wardens' amends are grace beside the road, not its toll — she
## marks their progress, or points to the knight's missive when even
## the asking hasn't been found yet.
const LINES_UNSWORN := [
	"You kneel. Good. The way to the THIRTEENTH bell stands open to you, Latecomer — it has stood open since your hand silenced the twelfth. That is the road, and no one bars it.",
	"But there is a letter you have not read. A knight left his last words for you on the Basilica's porch — stand there in the world as it truly lies, in ruin, and read them. What the light still hopes from you is written in a dead man's hand.",
]
const LINES_NONE := [
	"You kneel. Good. The way to the THIRTEENTH bell stands open, Latecomer — that road is yours, and I will not bar it.",
	"Yet five wardens keep their quarters in the light, and not one has heard your voice. Their amends are not the toll of the road — they are the grace beside it. Ring unatoned if you must; ring answered, and your name rings clean.",
]
const LINES_PART := [
	"You kneel, and the way to the THIRTEENTH bell stands open — as it has, as it will. But I have heard wardens speak your name, Latecomer, and speak it warmly.",
	"Some of the five stand answered. The rest still wait in the light. Finish what you began, or ring on regardless — the bell will not refuse you. Only the morning will remember which hand it was.",
]
const LINES_WHOLE := [
	"...So. Every warden rests answered, every amend made whole — and the way to the THIRTEENTH bell stands open before a clean name. I confess, bell-hand: I did not believe the morning had that much patience in you.",
	"Rise. Whatever the Hour asks of you now, you meet it unashamed. Your insolence is spent. Go and ring.",
]


var _busy := false
var _zone: Interactable = null
var _player: Node3D = null
var _scion: CharVisual = null
var _scion_exit := Vector3.ZERO
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
	if not World.flag("amend_sworn"):
		return [LINES_UNSWORN, ["u1", "u2"]]
	var n := _amends_done()
	if n >= AMENDS.size():
		return [LINES_WHOLE, ["c1", "c2"]]
	if n > 0:
		return [LINES_PART, ["b1", "b2"]]
	return [LINES_NONE, ["a1", "a2"]]

func _begin() -> void:
	if _busy:
		return
	_busy = true
	_zone.enabled = false   # the "Pray" hand has no place inside the vision
	if not World.flag("scion_prayed"):
		# the first prayer opens the sky-road: a stair of light stands up
		# from the Sanctum's west parapet toward the castle on the clouds
		World.set_flag("scion_prayed")
		World.save_game()
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
	# she does not descend — she WALKS, out of the dark of the hall, and
	# stops a few paces behind the kneeling pilgrim
	var pp: Vector3 = _player.global_position
	var stop := pp + Vector3(0, 0, -3.6)
	var from := pp + Vector3(0, 0, -11.0)
	_scion_exit = from
	_scion = CharVisual.new()
	add_child(_scion)
	_scion.build_body("skel_ward", 0.92, 1.0)
	var gold := MaterialLib.get_mat("M_gold", 0)
	for mi in _scion.find_children("*", "MeshInstance3D", true, false):
		for s in ((mi as MeshInstance3D).mesh.get_surface_count() if (mi as MeshInstance3D).mesh != null else 0):
			(mi as MeshInstance3D).set_surface_override_material(s, gold)
	_scion.global_position = from
	_scion.rotation.y = atan2(-(pp.x - from.x), -(pp.z - from.z))
	var lamp := OmniLight3D.new()
	lamp.light_color = Color(1.0, 0.9, 0.6)
	lamp.light_energy = 2.2
	lamp.omni_range = 7.0
	lamp.shadow_enabled = false
	lamp.position.y = 1.3
	_scion.add_child(lamp)
	AudioDirector.sfx_at("res://assets/audio/swell_kindle.wav", stop, -8.0, 0.85)
	_scion.play("walk", 0.3)
	var tw := _scion.create_tween()
	tw.tween_property(_scion, "global_position", stop, 3.6)
	tw.tween_callback(func():
		if _scion != null and is_instance_valid(_scion):
			_scion.back_to_idle(0.4))
	# the second shot: over the penitent's shoulder, meeting her approach
	var pp2 := _player.global_position
	var ctw := _cam.create_tween()
	ctw.tween_interval(1.0)
	ctw.tween_property(_cam, "global_position", pp2 + Vector3(-1.1, 1.5, 1.9), 1.4) \
		.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	ctw.parallel().tween_method(func(t: float):
		_cam.look_at(pp2.lerp(stop + Vector3(0, 1.4, 0), t) + Vector3(0, 1.0, 0)),
		0.0, 1.0, 1.4)
	ctw.tween_interval(1.2)   # she finishes the walk before she speaks
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
	# she turns, and walks back into the dark she came from
	if _scion != null and is_instance_valid(_scion):
		var sc := _scion
		_scion = null
		var ttw := sc.create_tween()
		ttw.tween_property(sc, "rotation:y", sc.rotation.y + PI, 0.5) \
			.set_trans(Tween.TRANS_SINE)
		ttw.tween_callback(func():
			if is_instance_valid(sc):
				sc.play("walk", 0.3))
		ttw.tween_property(sc, "global_position", _scion_exit, 3.2)
		ttw.tween_callback(func():
			if is_instance_valid(sc):
				VG.free_gently(sc))
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
