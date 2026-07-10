class_name DifficultyUI
extends CanvasLayer
## The weight of the dark: chosen once, before the opening rite of a fresh
## pilgrimage. Keyboard-driven like the vigil menu; the middle way is the
## kingdom as it is remembered, and is the default.

signal chosen(id: String)

## From the title's New Journey, Esc backs out (emits ""): nothing is
## forgotten until the weight is actually chosen.
var cancellable := false

var _options := [
	{"id": "kindled", "label": "The Kindled Path",
	 "desc": "The dark bites softer. Your hand lands harder (deal 1.25x, take 0.75x)."},
	{"id": "vigil", "label": "The Vigil",
	 "desc": "The kingdom as it is remembered."},
	{"id": "guttered", "label": "The Guttered Path",
	 "desc": "The dark bites deeper. Your hand lands lighter (deal 0.75x, take 1.25x)."},
]
var _opt_i := 1   # The Vigil — the way it is now — is the default
var _rows: Array = []
var _desc: Label
var _done := false

func _ls(size: int, color: Color) -> LabelSettings:
	var ls := LabelSettings.new()
	ls.font = load("res://assets/fonts/DejaVuSerif.ttf")
	ls.font_size = size
	ls.font_color = color
	return ls

func _ready() -> void:
	layer = 85
	var back := ColorRect.new()
	back.color = Color.BLACK
	back.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(back)
	var panel := Panel.new()
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0.04, 0.035, 0.03, 0.96)
	sb.border_color = Color(0.6, 0.5, 0.32)
	sb.set_border_width_all(1)
	panel.add_theme_stylebox_override("panel", sb)
	panel.set_anchors_preset(Control.PRESET_CENTER)
	panel.offset_left = -350
	panel.offset_right = 350
	panel.offset_top = -240
	panel.offset_bottom = 240
	add_child(panel)
	var title := Label.new()
	title.label_settings = _ls(30, Color(0.9, 0.78, 0.55))
	title.position = Vector2(32, 24)
	title.text = "The Weight of the Dark"
	panel.add_child(title)
	var sub := Label.new()
	sub.label_settings = _ls(18, Color(0.6, 0.55, 0.46))
	sub.position = Vector2(32, 66)
	sub.text = "How hard a road will this pilgrimage be?"
	panel.add_child(sub)
	var box := VBoxContainer.new()
	box.position = Vector2(32, 120)
	box.size = Vector2(636, 220)
	box.add_theme_constant_override("separation", 18)
	panel.add_child(box)
	for opt in _options:
		var l := Label.new()
		box.add_child(l)
		_rows.append(l)
	_desc = Label.new()
	_desc.label_settings = _ls(19, Color(0.65, 0.6, 0.5))
	_desc.position = Vector2(32, 356)
	_desc.size = Vector2(636, 80)
	_desc.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	panel.add_child(_desc)
	var hint := Label.new()
	hint.label_settings = _ls(16, Color(0.45, 0.42, 0.36))
	hint.position = Vector2(32, 440)
	hint.text = "W/S to weigh, E or click to choose. This holds for the whole pilgrimage."
	panel.add_child(hint)
	_render()

func _render() -> void:
	for i in _rows.size():
		var sel: bool = i == _opt_i
		var l: Label = _rows[i]
		l.label_settings = _ls(25, Color(0.98, 0.88, 0.6) if sel else Color(0.7, 0.66, 0.58))
		l.text = ("»  " if sel else "    ") + _options[i]["label"] \
				+ ("      (default)" if _options[i]["id"] == "vigil" else "")
	_desc.text = _options[_opt_i]["desc"]

func _unhandled_input(event: InputEvent) -> void:
	if _done:
		return
	if cancellable and event.is_action_pressed("ui_cancel"):
		_done = true
		chosen.emit("")
		queue_free()
		return
	if event.is_action_pressed("move_forward"):
		_opt_i = max(0, _opt_i - 1)
		_render()
	elif event.is_action_pressed("move_back"):
		_opt_i = min(_options.size() - 1, _opt_i + 1)
		_render()
	elif event.is_action_pressed("interact") or event.is_action_pressed("attack_light") \
			or (event is InputEventMouseButton and event.pressed):
		_done = true
		AudioDirector.sfx("res://assets/audio/rest_chime.wav", -6.0)
		chosen.emit(_options[_opt_i]["id"])
		queue_free()
