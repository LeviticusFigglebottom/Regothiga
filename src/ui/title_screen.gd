extends Node
## The title: VESPERGARD over a slow drift through the kingdom's quarters —
## a shuffled deck of areas, radiant or ruined by coin-flip — while the
## title theme plays. Resume (when a vigil is kept somewhere), New Journey,
## Settings (the pause sheet, solo), Credits. Emits done("resume"|"new").

signal done(choice: String, slot: int)

var has_save := false

const GOLD := Color(0.9, 0.78, 0.55)
const PARCHMENT := Color(0.82, 0.78, 0.68)
const ASH := Color(0.55, 0.52, 0.46)

## One stop per quarter: a slow dolly from -> to, eyes fixed on look.
const STOPS := [
	{"id": "wick_cathedral", "from": Vector3(2.5, 4.0, -3.0), "to": Vector3(-2.0, 2.6, -13.0), "look": Vector3(0, 1.6, -22)},
	{"id": "basilica_porch", "from": Vector3(-3.0, -1.0, 11.0), "to": Vector3(2.5, -0.4, 15.5), "look": Vector3(0, -2.0, 40)},
	{"id": "gray_cloister", "from": Vector3(0.0, 3.5, 3.0), "to": Vector3(-2.0, 3.0, -1.0), "look": Vector3(4, 1.2, -6)},
	{"id": "basilica_nave", "from": Vector3(3.5, 2.8, 4.0), "to": Vector3(-2.5, 2.0, -6.0), "look": Vector3(0, 2.2, -14)},
	{"id": "larkspire", "from": Vector3(4.5, 2.4, 6.0), "to": Vector3(1.0, 2.6, 3.0), "look": Vector3(0, 3.0, -6)},
	{"id": "black_gate", "from": Vector3(-2.0, 2.8, 24.0), "to": Vector3(3.0, 2.2, 16.0), "look": Vector3(0, 2.0, -4)},
	{"id": "old_outskirts", "from": Vector3(-6.0, 4.0, 14.0), "to": Vector3(3.0, 2.4, 6.0), "look": Vector3(0, 1.4, -6)},
	{"id": "drowned_marches", "from": Vector3(24.0, 3.4, 8.5), "to": Vector3(10.0, 2.8, 6.5), "look": Vector3(-4, 1.6, 0)},
	{"id": "ossuary_undercroft", "from": Vector3(-21.5, 2.8, 0.0), "to": Vector3(-17.0, 3.6, -2.0), "look": Vector3(-12, 2.0, 0)},
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
# the vigil picker: which playthrough to resume or begin
var _slots_box: VBoxContainer = null
var _main_box: VBoxContainer = null
var _slots_mode := ""      # "resume" | "new"
var _armed_slot := 0       # overwrite confirm: second press forgets

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
	box.set_anchors_preset(Control.PRESET_CENTER_LEFT)
	box.offset_left = 96
	box.offset_top = -110
	box.add_theme_constant_override("separation", 18)
	_layer.add_child(box)
	_main_box = box
	var first: Button = null
	if has_save:
		var b := _button("Resume the vigil", func(): _open_slots("resume"))
		box.add_child(b)
		first = b
	var nb := _button("New journey", func(): _open_slots("new"))
	box.add_child(nb)
	if first == null:
		first = nb
	box.add_child(_button("Settings", func(): PauseUI.open_settings_solo()))
	box.add_child(_button("Credits", _open_credits))
	first.grab_focus.call_deferred()
	_slots_box = VBoxContainer.new()
	_slots_box.set_anchors_preset(Control.PRESET_CENTER_LEFT)
	_slots_box.offset_left = 96
	_slots_box.offset_top = -130
	_slots_box.add_theme_constant_override("separation", 14)
	_slots_box.visible = false
	_layer.add_child(_slots_box)

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
		VG.free_gently(_area)   # the wick stop carries a cull-masked key rig
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

## The vigil ledger: pick which playthrough to resume, or where a new
## journey will be kept. Nothing is forgotten here — beginning over a kept
## vigil asks twice, and the weighing of the dark (with its own Esc) still
## stands between the choice and the wipe.
func _open_slots(mode: String) -> void:
	_slots_mode = mode
	_armed_slot = 0
	for c in _slots_box.get_children():
		c.queue_free()
	var head := Label.new()
	var hls := LabelSettings.new()
	hls.font = load("res://assets/fonts/DejaVuSerif.ttf")
	hls.font_size = 24
	hls.font_color = ASH
	head.label_settings = hls
	head.text = "Resume which vigil?" if mode == "resume" else "Keep the new vigil where?"
	_slots_box.add_child(head)
	var first: Button = null
	for i in range(1, World.SLOTS + 1):
		var sum = World.slot_summary(i)
		var b := _button(_slot_label(i, sum), _pick_slot.bind(i))
		b.add_theme_font_size_override("font_size", 24)
		if mode == "resume" and sum == null:
			b.disabled = true
			b.add_theme_color_override("font_disabled_color", Color(ASH.r, ASH.g, ASH.b, 0.4))
		elif first == null:
			first = b
		_slots_box.add_child(b)
	var back := _button("Back", _close_slots)
	back.add_theme_font_size_override("font_size", 24)
	_slots_box.add_child(back)
	_main_box.visible = false
	_slots_box.visible = true
	if first != null:
		first.grab_focus.call_deferred()
	else:
		back.grab_focus.call_deferred()

func _slot_label(i: int, sum) -> String:
	var name_ := "Vigil %s" % ["I", "II", "III"][i - 1]
	if sum == null:
		return "%s   —  unkept" % name_
	var area_name: String = DB.area_def(String(sum["area"])).get("name", "the Gray Cloister") 			if String(sum["area"]) != "" else "the Gray Cloister"
	var hours := int(sum["play_s"]) / 3600
	var mins := (int(sum["play_s"]) % 3600) / 60
	return "%s   Level %d  ·  %s  ·  %s  ·  %dh %02dm" % [
		name_, sum["level"], area_name, String(sum["difficulty"]), hours, mins]

func _pick_slot(i: int) -> void:
	if _slots_mode == "new" and World.slot_summary(i) != null and _armed_slot != i:
		# a kept vigil stands in the way: ask twice before it is forgotten
		_armed_slot = i
		for c in _slots_box.get_children():
			if c is Button and (c as Button).text.begins_with("Vigil %s " % ["I", "II", "III"][i - 1]):
				(c as Button).text = "Vigil %s   — forget this vigil forever?  (choose again)" % ["I", "II", "III"][i - 1]
		return
	_finish(_slots_mode, i)

func _close_slots() -> void:
	_slots_box.visible = false
	_main_box.visible = true
	_armed_slot = 0
	for c in _main_box.get_children():
		if c is Button:
			(c as Button).grab_focus.call_deferred()
			break

func _unhandled_input(event: InputEvent) -> void:
	if _slots_box != null and _slots_box.visible and event.is_action_pressed("ui_cancel"):
		_close_slots()
		get_viewport().set_input_as_handled()

func _open_credits() -> void:
	if _credits != null and is_instance_valid(_credits):
		return
	_credits = CreditsUI.new()
	add_child(_credits)
	_credits.tree_exited.connect(func(): _credits = null)

## A pick: dip to black, tear the stage down, hand the flow back.
func _finish(choice: String, slot: int) -> void:
	if _done:
		return
	_done = true
	var tw := create_tween()
	tw.tween_property(_veil, "color:a", 1.0, 0.7)
	tw.tween_callback(func():
		if _area != null and is_instance_valid(_area):
			VG.free_gently(_area)
			_area = null
		done.emit(choice, slot))
