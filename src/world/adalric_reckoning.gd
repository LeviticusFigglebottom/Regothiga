extends Node3D
## The reckoning. The first time the Latecomer walks out of the parish over
## the keeper's body, Ser Adalric is waiting on the terrace — come down from
## his beloved view to say what no one else is left to say. Unskippable in
## whole (each line may be advanced once it has had a breath), because this
## is the turn the whole pilgrimage stands on. Sets "reckoning_heard": the
## porch railing parts and the light makes its road.

const LINES := [
	"What have you done... Latecomer. What have you done?",
	"You were one of them. The THIRTEENTH. Twelve keepers rang their hours and waited on the last bell — yours. It never came. The dark found you on the road, Latecomer. It hollowed you out, and it turned your eyes, and the hour's own bellman forgot his name in the wax.",
	"So understand what you have walked through. The kingdom never fell. There was no ruin — not before tonight. The guttered streets, the monstrous wardens — the dark painted all of it over your eyes. They were keepers. Faithful. The living. And your blade fell on every one of them.",
	"And now the last Immortal is cold by your hand — and for the first time, truly, the dark has fallen on Vespergard. Not a vision. Not a seeming. Every soul the wax was keeping is sealed in it now, and there is no keeper left alive to call the morning.",
	"One hope remains, and heaven forgive the shape of it: you. The thirteenth bell — the one soul the dark could not quite finish. The temple stands at the city's heart, and the final flame waits on a soul freely given. Go, Latecomer. Ring your hour at last. The light itself will make you a road.",
]
const VOICE_FMT := "res://assets/audio/voice/adalric_reck_%02d.mp3"

var _staged := false
var _line := -1
var _line_at := 0.0            # scene clock when the line went up
var _clock := 0.0
var _knight: CharVisual = null
var _cine: Node3D = null
var _cam: Camera3D = null
var _layer: CanvasLayer = null
var _black: ColorRect = null
var _sub: Label = null
var _voice: AudioStreamPlayer3D = null
var _player: Node3D = null

func _physics_process(dt: float) -> void:
	_clock += dt
	if _staged:
		return
	if not World.is_cleared("wick_cathedral") or World.flag("reckoning_heard"):
		return
	var p = Game.player
	if p == null or not is_instance_valid(p) or p.get("dead") == true:
		return
	if p.global_position.distance_to(global_position) > 7.0:
		return
	stage_now()

var _hidden_props: Array = []

func stage_now() -> void:
	if _staged:
		return
	_staged = true
	_player = Game.player
	_player.lock_control(true)
	_player.velocity = Vector3.ZERO
	# the terrace wellhead sits on his walk line: it stands aside for the
	# scene and returns when the frame is handed back
	var area = Game.current_area
	if area != null and is_instance_valid(area):
		for n in area.base.get_children():
			if n is Node3D and String(n.get_meta("kit_id", "")) == "wellhead" \
					and (n as Node3D).global_position.distance_to(_player.global_position) < 16.0:
				(n as Node3D).visible = false
				_hidden_props.append(n)
	# he comes up the terrace from the town side, sword lowered
	_knight = CharVisual.new()
	add_child(_knight)
	_knight.build_body("skel_ward", 0.9, 0.9)
	var m := _knight.mount_weapon_hand()
	if KitLib.has_piece("sword_cloister"):
		m.add_child(KitLib.instance("sword_cloister"))
	var lamp := OmniLight3D.new()
	lamp.light_color = Color(1.0, 0.86, 0.55)
	lamp.light_energy = 1.1
	lamp.omni_range = 4.5
	lamp.shadow_enabled = false
	lamp.position.y = 1.4
	_knight.add_child(lamp)
	var pp: Vector3 = _player.global_position
	var from := Vector3(pp.x, pp.y, pp.z + 7.0)
	var to := Vector3(pp.x, pp.y, pp.z + 2.2)
	_knight.global_position = from
	_knight.rotation.y = atan2(-(to.x - from.x), -(to.z - from.z))
	# the player turns to meet him
	if _player.get("vis") != null:
		var face: Vector3 = from - pp
		(_player.get("vis") as Node3D).rotation.y = atan2(-face.x, -face.z)
	_cine_begin()
	_knight.play("walk", 0.2, 1.0)
	var tw := create_tween()
	tw.tween_interval(0.6)
	tw.tween_property(_knight, "global_position", to, 3.4) \
		.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	tw.tween_callback(func():
		if _knight != null and is_instance_valid(_knight):
			_knight.play("idle", 0.4)
		_next_line())

## A quiet two-shot: the camera stands off their shoulder-line, drifting in
## as he speaks; letterbox bars; no skip hint, because there is no skip.
func _cine_begin() -> void:
	_cine = Node3D.new()
	add_child(_cine)
	_cam = Camera3D.new()
	_cam.fov = 52
	_cine.add_child(_cam)
	var pp: Vector3 = _player.global_position
	_cam.global_position = pp + Vector3(3.4, 1.6, 3.6)
	_cam.look_at(pp + Vector3(0, 1.3, 2.4))
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
	if _cam == null or _knight == null or not is_instance_valid(_knight):
		return
	var pp: Vector3 = _player.global_position
	var kp: Vector3 = _knight.global_position
	var mid := (pp + kp) * 0.5 + Vector3(0, 1.35, 0)
	var side := (kp - pp).cross(Vector3.UP)
	side = side.normalized() if side.length() > 0.1 else Vector3.RIGHT
	var want := mid + side * 3.3 + Vector3(0, 0.35, 0)
	_cam.global_position = _cam.global_position.lerp(want, 1.0 - exp(-2.6 * dt))
	_cam.look_at(mid)

## Any input advances the standing line — once it has had a breath — but
## the scene itself cannot be skipped.
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
		_knight.add_child(a)
		_voice = a
		a.finished.connect(func():
			if _line == idx:
				advance())
		a.play()
		watchdog = maxf(float(a.stream.get_length()) + 0.8, 3.0)
	# headless and belt-and-braces: the line never hangs the scene
	get_tree().create_timer(watchdog, false).timeout.connect(func():
		if _line == idx:
			advance())

func advance() -> void:
	if _line < 0 or _line >= LINES.size():
		return
	_next_line()

## He said what he came to say. The flag opens the road; he goes back the
## way he came and the dark takes him gently.
func _end() -> void:
	World.set_flag("reckoning_heard")
	World.save_game()
	_close_sub()
	if _voice != null and is_instance_valid(_voice):
		_voice.stop()
	set_process_unhandled_input(false)
	var k := _knight
	var tw := create_tween()
	if k != null and is_instance_valid(k):
		tw.tween_callback(func():
			k.rotation.y += PI
			k.play("walk", 0.3, 0.9))
		tw.tween_property(k, "global_position",
				k.global_position + Vector3(0, 0, 6.5), 4.0)
	tw.tween_callback(_cine_end)
	# the phantom grace: he thins as he walks
	if k != null:
		var dtw := create_tween()
		dtw.tween_interval(2.2)
		dtw.tween_method(func(v: float):
			if k != null and is_instance_valid(k):
				_set_dissolve(k, v), 0.0, 1.0, 1.6)
		dtw.tween_callback(func():
			if k != null and is_instance_valid(k):
				k.queue_free())

func _cine_end() -> void:
	set_process(false)
	for n in _hidden_props:
		if is_instance_valid(n):
			(n as Node3D).visible = true
	_hidden_props.clear()
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
		ls.font_color = Color(0.92, 0.88, 0.78)
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
