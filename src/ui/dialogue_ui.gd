class_name DialogueUI
extends CanvasLayer
## Minimal soulslike dialogue: name plate, line-by-line advance, then
## service options. Keyboard/gamepad driven; sim-drivable via advance()/choose().

signal closed

var npc_cfg: Dictionary
var npc_node: Node3D
var _lines: Array = []
var _line_i := 0
var _options: Array = []
var _opt_i := 0
var _phase := "lines"   # lines -> options

var text_label: Label
var name_label: Label
var options_box: VBoxContainer
var panel: Panel

func _init(cfg: Dictionary, node: Node3D) -> void:
	npc_cfg = cfg
	npc_node = node

func _ready() -> void:
	layer = 20
	var root := Control.new()
	root.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(root)
	panel = Panel.new()
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0.04, 0.035, 0.03, 0.92)
	sb.border_color = Color(0.6, 0.5, 0.32)
	sb.set_border_width_all(1)
	panel.add_theme_stylebox_override("panel", sb)
	panel.position = Vector2(360, 770)
	panel.size = Vector2(1200, 240)
	root.add_child(panel)
	name_label = Label.new()
	name_label.label_settings = _ls(26, Color(0.9, 0.78, 0.55))
	name_label.position = Vector2(24, 14)
	panel.add_child(name_label)
	text_label = Label.new()
	text_label.label_settings = _ls(24, Color(0.92, 0.9, 0.84))
	text_label.position = Vector2(24, 58)
	text_label.size = Vector2(1150, 120)
	text_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	panel.add_child(text_label)
	options_box = VBoxContainer.new()
	options_box.position = Vector2(24, 60)
	options_box.size = Vector2(1150, 160)
	panel.add_child(options_box)

	name_label.text = npc_cfg.get("name", "???")
	var first := not World.flag("met_" + npc_cfg.get("id", "npc"))
	World.set_flag("met_" + npc_cfg.get("id", "npc"))
	_lines = npc_cfg.get("lines_first" if first else "lines_repeat", [])
	_show_line()

func _ls(size: int, color: Color) -> LabelSettings:
	var ls := LabelSettings.new()
	ls.font = load("res://assets/fonts/DejaVuSerif.ttf")
	ls.font_size = size
	ls.font_color = color
	return ls

func _show_line() -> void:
	options_box.visible = false
	text_label.visible = true
	if _line_i < _lines.size():
		text_label.text = String(_lines[_line_i])
	else:
		_enter_options()

func _enter_options() -> void:
	_phase = "options"
	_options = npc_cfg.get("services", []).duplicate()
	_options.append({"id": "leave", "label": "Leave"})
	text_label.visible = false
	options_box.visible = true
	_opt_i = 0
	_render_options()

func _render_options() -> void:
	for c in options_box.get_children():
		c.queue_free()
	for i in _options.size():
		var o: Dictionary = _options[i]
		var l := Label.new()
		var selected := i == _opt_i
		l.label_settings = _ls(24, Color(0.98, 0.88, 0.6) if selected else Color(0.7, 0.66, 0.58))
		l.text = ("»  " if selected else "    ") + _option_label(o)
		options_box.add_child(l)

func _option_label(o: Dictionary) -> String:
	return o.get("label", o.get("id", "?"))

func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("interact") or event.is_action_pressed("attack_light"):
		advance()
		get_viewport().set_input_as_handled()
	elif _phase == "options" and event.is_action_pressed("move_forward"):
		_opt_i = max(0, _opt_i - 1)
		_render_options()
	elif _phase == "options" and event.is_action_pressed("move_back"):
		_opt_i = min(_options.size() - 1, _opt_i + 1)
		_render_options()

## advance current line, or activate the selected option
func advance() -> void:
	if _phase == "lines":
		_line_i += 1
		_show_line()
	else:
		_activate(_options[_opt_i])

func choose(idx: int) -> void:
	if _phase != "options":
		while _phase == "lines":
			advance()
	_opt_i = clampi(idx, 0, _options.size() - 1)
	_activate(_options[_opt_i])

func _activate(o: Dictionary) -> void:
	var p = Game.player
	match o.get("type", o.get("id", "")):
		"leave":
			close()
		"upgrade":
			var cost := int(o.get("orisons", 150))
			var have_glass := int(p.inventory.get("candleglass", 0))
			if p.weapon_level >= 5:
				text_label.text = "The blade holds all the light it can carry."
				_flash_line()
			elif have_glass < 1:
				text_label.text = "Bring me candleglass from the ruin, Latecomer. The dark grinds it out of the windows."
				_flash_line()
			elif Game.orisons < cost:
				text_label.text = "Prayers first. %d orisons, or the wax stays cold." % cost
				_flash_line()
			else:
				p.inventory["candleglass"] = have_glass - 1
				Game.add_orisons(-cost)
				p.weapon_level += 1
				Game.toast.emit("The blade drinks the light. %s +%d" % [p.weapon_data().get("name", "Weapon"), p.weapon_level])
				AudioDirector.sfx("res://assets/audio/levelup.wav", -4.0)
				text_label.text = "There. It remembers being a relic now. Try not to die somewhere I can't retrieve it."
				_flash_line()
		"flask_up":
			var cost2 := int(o.get("orisons", 300))
			if World.flag(o.get("once_flag", "bought_tallow")):
				text_label.text = "I had only the one heart to spare."
				_flash_line()
			elif Game.orisons < cost2:
				text_label.text = "The heart costs %d. Wax is cheap; what soaks it isn't." % cost2
				_flash_line()
			else:
				World.set_flag(o.get("once_flag", "bought_tallow"))
				Game.add_orisons(-cost2)
				p.flask_max += 1
				p.flasks = p.flask_max
				p.flasks_changed.emit(p.flasks, p.flask_max)
				Game.toast.emit("Chrism flask deepened (+1 draught).")
				AudioDirector.sfx("res://assets/audio/levelup.wav", -4.0)
				text_label.text = "Swallow it slowly. It was rendered from a saint's own votive."
				_flash_line()
		"dig":
			var cost3 := int(o.get("orisons", 180))
			var fl: String = o.get("flag", "sexton_dug")
			if World.flag(fl):
				text_label.text = "Dug is dug. Mind the tailings."
				_flash_line()
			elif Game.orisons < cost3:
				text_label.text = "Stone before sympathy: %d orisons buys the shovel's arc." % cost3
				_flash_line()
			else:
				Game.add_orisons(-cost3)
				World.set_flag(fl)
				World.save_game()
				Game.toast.emit("Somewhere below, rubble shifts.")
				AudioDirector.sfx("res://assets/audio/swell_kindle.wav", -4.0)
				text_label.text = o.get("done_line", "There. A door where the kingdom said wall.")
				_flash_line()
		_:
			close()

func _flash_line() -> void:
	_phase = "lines"
	_lines = [text_label.text]
	_line_i = 0
	text_label.visible = true
	options_box.visible = false

func close() -> void:
	if Game.player != null:
		Game.player.lock_control(false)
		Game.player.exit_rest()
	closed.emit()
	World.save_game()
	queue_free()
