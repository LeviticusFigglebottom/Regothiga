class_name RestUI
extends CanvasLayer
## The vigil menu: keep vigil (rest / turn the world), grow by prayer
## (level attributes with orisons), rise. Keyboard-driven, sim-drivable.

var lantern: VigilLantern
var player

var _phase := "main"    # main | level
var _opt_i := 0
var _options: Array = []
var panel: Panel
var title_label: Label
var list_box: VBoxContainer
var info_label: Label

func _init(l: VigilLantern, p) -> void:
	lantern = l
	player = p

func _ls(size: int, color: Color) -> LabelSettings:
	var ls := LabelSettings.new()
	ls.font = load("res://assets/fonts/DejaVuSerif.ttf")
	ls.font_size = size
	ls.font_color = color
	return ls

func _ready() -> void:
	layer = 20
	var root := Control.new()
	root.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(root)
	panel = Panel.new()
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0.04, 0.035, 0.03, 0.94)
	sb.border_color = Color(0.6, 0.5, 0.32)
	sb.set_border_width_all(1)
	panel.add_theme_stylebox_override("panel", sb)
	panel.position = Vector2(660, 330)
	panel.size = Vector2(600, 420)
	root.add_child(panel)
	title_label = Label.new()
	title_label.label_settings = _ls(28, Color(0.9, 0.78, 0.55))
	title_label.position = Vector2(28, 18)
	title_label.text = lantern.display_name
	panel.add_child(title_label)
	list_box = VBoxContainer.new()
	list_box.position = Vector2(28, 74)
	list_box.size = Vector2(540, 260)
	panel.add_child(list_box)
	info_label = Label.new()
	info_label.label_settings = _ls(20, Color(0.65, 0.6, 0.5))
	info_label.position = Vector2(28, 360)
	info_label.size = Vector2(540, 50)
	info_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	panel.add_child(info_label)
	_enter_main()

func _aid() -> String:
	return lantern.area.area_id if lantern.area != null else Game.current_area_id

func _stub_lantern() -> bool:
	var def: Dictionary = lantern.area.get_meta("def", {}) if lantern.area != null else {}
	return def.get("no_gutter", false)

func _enter_main() -> void:
	_phase = "main"
	_options = []
	var aid := _aid()
	var cur := World.get_area_state(aid)
	if _stub_lantern():
		_options.append({"id": "rest", "label": "Keep vigil  (rest — the memory here is thin)"})
	elif World.is_cleared(aid):
		_options.append({"id": "rest", "label": "Keep vigil  (rest)"})
		_options.append({"id": "toggle", "label": "Turn the memory — " +
			("kindle the glory" if cur == VG.WState.RUIN else "let it gutter")})
	elif cur == VG.WState.GLORY:
		_options.append({"id": "rest", "label": "Keep vigil  — the seeing will end"})
	else:
		_options.append({"id": "rest", "label": "Keep vigil  (rest)"})
	_options.append({"id": "level", "label": "Grow by prayer  (%d orisons held)" % Game.orisons})
	_options.append({"id": "leave", "label": "Rise"})
	info_label.text = "The lantern holds this quarter's memory." if not World.is_cleared(aid) \
		else "The warden rests. Keep or quench the memory as you please."
	_opt_i = 0
	_render()

func _level_cost() -> int:
	var base := int(DB.tuning("levels/base_cost", 60))
	var growth := float(DB.tuning("levels/cost_growth", 1.22))
	return int(round(base * pow(growth, player.level - 1)))

func _enter_level() -> void:
	_phase = "level"
	_options = []
	var cost := _level_cost()
	for stat in DB.tuning("levels/stats", []):
		_options.append({"id": "stat:" + stat, "label": "%s  %d  →  %d      (%d orisons)" %
			[stat.capitalize(), player.attributes[stat], player.attributes[stat] + 1, cost]})
	_options.append({"id": "back", "label": "Back"})
	info_label.text = "Level %d.  Each prayer costs %d orisons.  You hold %d." % [player.level, cost, Game.orisons]
	_opt_i = 0
	_render()

func _render() -> void:
	for c in list_box.get_children():
		c.queue_free()
	for i in _options.size():
		var l := Label.new()
		var sel := i == _opt_i
		l.label_settings = _ls(23, Color(0.98, 0.88, 0.6) if sel else Color(0.7, 0.66, 0.58))
		l.text = ("»  " if sel else "    ") + _options[i]["label"]
		list_box.add_child(l)

func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("move_forward"):
		_opt_i = max(0, _opt_i - 1)
		_render()
		get_viewport().set_input_as_handled()
	elif event.is_action_pressed("move_back"):
		_opt_i = min(_options.size() - 1, _opt_i + 1)
		_render()
		get_viewport().set_input_as_handled()
	elif event.is_action_pressed("interact") or event.is_action_pressed("attack_light"):
		choose(_opt_i)
		get_viewport().set_input_as_handled()
	elif event.is_action_pressed("menu") or event.is_action_pressed("dodge"):
		close()
		get_viewport().set_input_as_handled()

func choose(idx: int) -> void:
	_opt_i = clampi(idx, 0, _options.size() - 1)
	var id: String = _options[_opt_i]["id"]
	if id == "leave":
		close()
	elif id == "rest":
		_do_vigil("rest_only" if (World.is_cleared(_aid()) or _stub_lantern()) else "auto")
	elif id == "toggle":
		_do_vigil("toggle")
	elif id == "level":
		_enter_level()
	elif id == "back":
		_enter_main()
	elif id.begins_with("stat:"):
		_buy_stat(id.get_slice(":", 1))

func _buy_stat(stat: String) -> void:
	var cost := _level_cost()
	if Game.orisons < cost:
		info_label.text = "Not enough orisons. The dead are patient; gather more."
		return
	Game.add_orisons(-cost)
	player.attributes[stat] += 1
	player.level += 1
	player.recompute_derived()
	player.hp = player.max_hp
	player.stamina = player.max_stamina
	player._emit_all()
	AudioDirector.sfx("res://assets/audio/levelup.wav", -3.0)
	Game.toast.emit("Grown by prayer — %s is now %d." % [stat.capitalize(), player.attributes[stat]])
	Game.snapshot_player()
	World.save_game()
	_enter_level()

func _do_vigil(choice: String) -> void:
	var l := lantern
	var p = player
	close()
	Game.vigil_flow(l, p, choice)

func close() -> void:
	if player != null:
		player.lock_control(false)
	queue_free()
