extends Node
## The title: VESPERGARD over a slow drift through the kingdom's quarters —
## a shuffled deck of areas, radiant or ruined by coin-flip — while the
## title theme plays. Resume (when a vigil is kept somewhere), New Journey,
## Settings (the pause sheet, solo), Credits. Emits done("resume"|"new").

signal done(choice: String)

var has_save := false

const GOLD := Color(0.9, 0.78, 0.55)
const PARCHMENT := Color(0.82, 0.78, 0.68)
const ASH := Color(0.55, 0.52, 0.46)

## One stop per quarter: a slow dolly from -> to, eyes fixed on look.
const STOPS := [
	{"id": "wick_cathedral", "from": Vector3(2.5, 4.0, -3.0), "to": Vector3(-2.0, 2.6, -13.0), "look": Vector3(0, 1.6, -22)},
	{"id": "basilica_porch", "from": Vector3(-3.0, -1.0, 11.0), "to": Vector3(2.5, -0.4, 15.5), "look": Vector3(0, -2.0, 40)},
	{"id": "gray_cloister", "from": Vector3(-10.0, 5.5, 6.0), "to": Vector3(-2.0, 3.0, -1.0), "look": Vector3(4, 1.2, -6)},
	{"id": "basilica_nave", "from": Vector3(-6.0, 3.2, 9.0), "to": Vector3(0.0, 2.2, -2.0), "look": Vector3(0, 2.2, -14)},
	{"id": "larkspire", "from": Vector3(6.0, 4.0, 9.0), "to": Vector3(1.0, 2.6, 3.0), "look": Vector3(0, 3.0, -6)},
	{"id": "black_gate", "from": Vector3(-6.0, 3.0, 26.0), "to": Vector3(3.0, 2.2, 16.0), "look": Vector3(0, 2.0, -4)},
	{"id": "old_outskirts", "from": Vector3(-6.0, 4.0, 14.0), "to": Vector3(3.0, 2.4, 6.0), "look": Vector3(0, 1.4, -6)},
	{"id": "drowned_marches", "from": Vector3(27.0, 3.4, 6.0), "to": Vector3(16.0, 2.2, -2.0), "look": Vector3(4, 1.0, 0)},
	{"id": "ossuary_undercroft", "from": Vector3(-26.0, 5.0, 5.0), "to": Vector3(-17.0, 3.6, -2.0), "look": Vector3(-12, 2.0, 0)},
	{"id": "vigils_end", "from": Vector3(27.0, 3.4, -6.0), "to": Vector3(17.0, 2.0, 2.0), "look": Vector3(10, 1.0, 0)},
]
const STOP_T := 11.0

var _stage: Node3D
var _cam: Camera3D
var _area: Node = null
var _deck: Array = []
var _t := 0.0
var _from := Vector3.ZERO
var _to := Vector3.ZERO
var _look := Vector3.ZERO
var _dipping := false
var _layer: CanvasLayer
var _veil: ColorRect
var _done := false
var _credits: Node = null

func _ready() -> void:
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	AudioDirector.play_music("res://assets/audio/theme_title.mp3", 1.2)
	_stage = Node3D.new()
	add_child(_stage)
	_cam = Camera3D.new()
	_cam.fov = 58
	_stage.add_child(_cam)
	_build_ui()
	_deck = STOPS.duplicate()
	_deck.shuffle()
	_swap_stop()
	_veil.color.a = 1.0
	create_tween().tween_property(_veil, "color:a", 0.0, 1.1)

func _build_ui() -> void:
	_layer = CanvasLayer.new()
	_layer.layer = 20
	add_child(_layer)
	_veil = ColorRect.new()
	_veil.color = Color(0, 0, 0, 0)
	_veil.set_anchors_preset(Control.PRESET_FULL_RECT)
	_veil.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_layer.add_child(_veil)
	# a soft dark gradient behind the words so they read on bright stops
	var shade := TextureRect.new()
	var grad := Gradient.new()
	grad.set_color(0, Color(0, 0, 0, 0.5))
	grad.set_color(1, Color(0, 0, 0, 0.0))
	var gt := GradientTexture2D.new()
	gt.gradient = grad
	gt.fill_from = Vector2(0, 0.5)
	gt.fill_to = Vector2(1, 0.5)
	gt.width = 64
	gt.height = 8
	shade.texture = gt
	shade.stretch_mode = TextureRect.STRETCH_SCALE
	shade.set_anchors_preset(Control.PRESET_LEFT_WIDE)
	shade.offset_right = 760
	shade.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_layer.add_child(shade)

	var title := Label.new()
	title.text = "VESPERGARD"
	var tls := LabelSettings.new()
	tls.font = load("res://assets/fonts/DejaVuSerif.ttf")
	tls.font_size = 88
	tls.font_color = GOLD
	tls.shadow_color = Color(0, 0, 0, 0.9)
	tls.shadow_offset = Vector2(2, 3)
	title.label_settings = tls
	title.position = Vector2(88, 96)
	_layer.add_child(title)
	var sub := Label.new()
	sub.text = "a vigil for the thirteenth hour"
	var sls := LabelSettings.new()
	sls.font = load("res://assets/fonts/DejaVuSerif.ttf")
	sls.font_size = 22
	sls.font_color = ASH
	sls.shadow_color = Color(0, 0, 0, 0.85)
	sls.shadow_offset = Vector2(1, 2)
	sub.label_settings = sls
	sub.position = Vector2(94, 208)
	_layer.add_child(sub)

	var box := VBoxContainer.new()
	box.position = Vector2(96, 430)
	box.add_theme_constant_override("separation", 18)
	_layer.add_child(box)
	var first: Button = null
	if has_save:
		var b := _button("Resume the vigil", func(): _choose("resume"))
		box.add_child(b)
		first = b
	var nb := _button("New journey", func(): _choose("new"))
	box.add_child(nb)
	if first == null:
		first = nb
	box.add_child(_button("Settings", func(): PauseUI.open_settings_solo()))
	box.add_child(_button("Credits", _open_credits))
	first.grab_focus.call_deferred()

	var ver := Label.new()
	ver.text = VG.BUILD
	var vls := LabelSettings.new()
	vls.font = load("res://assets/fonts/DejaVuSerif.ttf")
	vls.font_size = 14
	vls.font_color = Color(ASH.r, ASH.g, ASH.b, 0.6)
	ver.label_settings = vls
	ver.set_anchors_preset(Control.PRESET_BOTTOM_RIGHT)
	ver.grow_horizontal = Control.GROW_DIRECTION_BEGIN
	ver.grow_vertical = Control.GROW_DIRECTION_BEGIN
	ver.offset_left = -120
	ver.offset_top = -44
	_layer.add_child(ver)

func _button(text: String, on_press: Callable) -> Button:
	var b := Button.new()
	b.text = text
	b.flat = true
	b.alignment = HORIZONTAL_ALIGNMENT_LEFT
	b.custom_minimum_size = Vector2(360, 44)
	b.add_theme_font_override("font", load("res://assets/fonts/DejaVuSerif.ttf"))
	b.add_theme_font_size_override("font_size", 30)
	b.add_theme_color_override("font_color", PARCHMENT)
	b.add_theme_color_override("font_hover_color", GOLD)
	b.add_theme_color_override("font_focus_color", GOLD)
	b.add_theme_color_override("font_pressed_color", GOLD)
	var empty := StyleBoxEmpty.new()
	for st in ["normal", "hover", "pressed", "focus"]:
		b.add_theme_stylebox_override(st, empty)
	b.pressed.connect(on_press)
	return b

## The drift: build the next quarter under the dip, then dolly across it.
func _process(dt: float) -> void:
	if _done or _cam == null:
		return
	_t += dt
	var k: float = clampf(_t / STOP_T, 0.0, 1.0)
	k = k * k * (3.0 - 2.0 * k)   # ease both ends
	_cam.global_position = _from.lerp(_to, k)
	if _cam.global_position.distance_to(_look) > 0.5:
		_cam.look_at(_look)
	if _t >= STOP_T - 0.65 and not _dipping:
		_dipping = true
		var tw := create_tween()
		tw.tween_property(_veil, "color:a", 1.0, 0.55)
		tw.tween_callback(_swap_stop)
		tw.tween_property(_veil, "color:a", 0.0, 0.8)
		tw.tween_callback(func(): _dipping = false)

func _swap_stop() -> void:
	if _done:
		return
	if _area != null and is_instance_valid(_area):
		_area.queue_free()
		_area = null
	if _deck.is_empty():
		_deck = STOPS.duplicate()
		_deck.shuffle()
	var stop: Dictionary = _deck.pop_back()
	var area = AreaBuilder.build(stop["id"])
	_stage.add_child(area)
	_area = area
	# state dressing WITHOUT StateDirector.snap: the title track owns the
	# music, so the layers/env/shader globals are set by hand
	var st: int = VG.WState.RUIN if randf() < 0.5 else VG.WState.GLORY
	area.apply_state(st)
	area.env.snap(st)
	StateDirector._set_g("vg_state_blend", 1.0 if st == VG.WState.RUIN else 0.0)
	StateDirector._set_g("vg_wave_r", -1000.0)
	_from = stop["from"]
	_to = stop["to"]
	_look = stop["look"]
	_t = 0.0
	_cam.global_position = _from
	if _cam.global_position.distance_to(_look) > 0.5:
		_cam.look_at(_look)
	_cam.make_current()

func _open_credits() -> void:
	if _credits != null and is_instance_valid(_credits):
		return
	_credits = CreditsUI.new()
	add_child(_credits)
	_credits.tree_exited.connect(func(): _credits = null)

## A pick: dip to black, tear the stage down, hand the flow back.
func _choose(choice: String) -> void:
	if _done:
		return
	_done = true
	var tw := create_tween()
	tw.tween_property(_veil, "color:a", 1.0, 0.7)
	tw.tween_callback(func():
		if _area != null and is_instance_valid(_area):
			_area.queue_free()
			_area = null
		done.emit(choice))
