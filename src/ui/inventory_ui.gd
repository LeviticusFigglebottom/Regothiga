class_name InventoryUI
extends CanvasLayer
## The Pilgrim's Satchel — Tab opens it. Every arm and relic the Latecomer
## carries, named and described, in the same dark-panel gothic dress as the
## dialogue. W/S scrolls; Tab or Esc closes.

var player: Node
var _scroll: ScrollContainer

static func open_for(p) -> void:
	if p == null or not p.get_tree().get_nodes_in_group("inventory_ui").is_empty():
		return
	var ui := InventoryUI.new(p)
	p.get_tree().root.add_child(ui)

func _init(p) -> void:
	player = p

func _ready() -> void:
	layer = 22
	add_to_group("inventory_ui")
	player.lock_control(true)
	var root := Control.new()
	root.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(root)
	var dim := ColorRect.new()
	dim.set_anchors_preset(Control.PRESET_FULL_RECT)
	dim.color = Color(0, 0, 0, 0.45)
	root.add_child(dim)

	var panel := Panel.new()
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0.045, 0.04, 0.035, 0.96)
	sb.border_color = Color(0.6, 0.5, 0.32)
	sb.set_border_width_all(1)
	panel.add_theme_stylebox_override("panel", sb)
	panel.set_anchors_preset(Control.PRESET_CENTER)
	panel.offset_left = -480
	panel.offset_right = 480
	panel.offset_top = -340
	panel.offset_bottom = 340
	root.add_child(panel)

	var title := Label.new()
	title.label_settings = _ls(30, Color(0.9, 0.78, 0.55), "res://assets/fonts/DejaVuSerif-Bold.ttf")
	title.text = "THE PILGRIM'S SATCHEL"
	title.position = Vector2(30, 18)
	panel.add_child(title)
	var rule := ColorRect.new()
	rule.color = Color(0.6, 0.5, 0.32, 0.6)
	rule.position = Vector2(30, 62)
	rule.size = Vector2(900, 1)
	panel.add_child(rule)

	_scroll = ScrollContainer.new()
	_scroll.position = Vector2(30, 76)
	_scroll.size = Vector2(900, 552)
	_scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	panel.add_child(_scroll)
	var list := VBoxContainer.new()
	list.custom_minimum_size = Vector2(880, 0)
	list.add_theme_constant_override("separation", 10)
	_scroll.add_child(list)

	_section(list, "ARMS")
	var weapons: Dictionary = DB.table("weapons")
	for id in weapons:
		if player.owns_weapon(id):
			var w: Dictionary = weapons[id]
			var name: String = w.get("name", id)
			if id == player.weapon_id:
				name += "   — in hand"
			if int(player.weapon_level) > 0:
				name += "  (+%d)" % int(player.weapon_level)
			_row(list, _icon_for(id), name, "", w.get("desc", ""))
	_row(list, "res://assets/ui/icons/flask.png", "Chrism Flask",
			"✕%d / %d" % [player.flasks, player.flask_max],
			DB.item("chrism_flask").get("desc", ""))

	_section(list, "RELICS & GOODS")
	var any := false
	for id in player.inventory:
		if not DB.weapon(id).is_empty():
			continue
		var n := int(player.inventory[id])
		if n <= 0:
			continue
		any = true
		var it: Dictionary = DB.item(id)
		_row(list, _icon_for(id), it.get("name", String(id).capitalize()), "✕%d" % n,
				it.get("desc", "A keepsake of the road. The kingdom has forgotten what it was for."))
	if not any:
		var none := Label.new()
		none.label_settings = _ls(20, Color(0.55, 0.52, 0.46))
		none.text = "    Nothing but road-dust and resolve."
		list.add_child(none)

	var hint := Label.new()
	hint.label_settings = _ls(17, Color(0.6, 0.55, 0.45))
	hint.text = "Tab — close      1-5 — the girdle      the Reliquary Smith sells arms"
	hint.set_anchors_preset(Control.PRESET_BOTTOM_LEFT)
	hint.grow_vertical = Control.GROW_DIRECTION_BEGIN
	hint.offset_left = 30
	hint.offset_top = -36
	hint.offset_bottom = -12
	panel.add_child(hint)
	AudioDirector.sfx("res://assets/audio/ui_tick.wav", -8.0)

func _icon_for(id: String) -> String:
	var by := {
		"cloistersword": "sword", "marsh_spear": "spear", "lark_bow": "bow",
		"pilgrim_greatsword": "greatsword", "arrows": "arrows",
		"sexton_maul": "greatsword", "ward_halberd": "spear",
	}
	return "res://assets/ui/icons/%s.png" % by.get(id, "relic")

func _section(list: VBoxContainer, text: String) -> void:
	var l := Label.new()
	l.label_settings = _ls(20, Color(0.72, 0.6, 0.4), "res://assets/fonts/DejaVuSerif-Bold.ttf")
	l.text = text
	list.add_child(l)

func _row(list: VBoxContainer, icon_path: String, name: String, count: String, desc: String) -> void:
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 14)
	list.add_child(row)
	var icon := TextureRect.new()
	icon.custom_minimum_size = Vector2(40, 40)
	icon.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	icon.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	if ResourceLoader.exists(icon_path):
		icon.texture = load(icon_path)
	row.add_child(icon)
	var col := VBoxContainer.new()
	col.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_child(col)
	var head := Label.new()
	head.label_settings = _ls(22, Color(0.92, 0.88, 0.78), "res://assets/fonts/DejaVuSerif-Bold.ttf")
	head.text = name + ("    " + count if count != "" else "")
	col.add_child(head)
	var body := Label.new()
	body.label_settings = _ls(17, Color(0.66, 0.62, 0.54))
	body.text = desc
	body.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	body.custom_minimum_size = Vector2(800, 0)
	col.add_child(body)

func _ls(size: int, color: Color, font := "res://assets/fonts/DejaVuSerif.ttf") -> LabelSettings:
	var ls := LabelSettings.new()
	ls.font = load(font)
	ls.font_size = size
	ls.font_color = color
	return ls

func _input(event: InputEvent) -> void:
	if event.is_action_pressed("inventory") or event.is_action_pressed("ui_cancel"):
		close()
		get_viewport().set_input_as_handled()
	elif event.is_action_pressed("move_forward"):
		_scroll.scroll_vertical -= 60
	elif event.is_action_pressed("move_back"):
		_scroll.scroll_vertical += 60

func close() -> void:
	if player != null and is_instance_valid(player):
		player.lock_control(false)
		player.suppress_interact(10)
	AudioDirector.sfx("res://assets/audio/ui_tick.wav", -10.0)
	queue_free()
