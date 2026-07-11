class_name InventoryUI
extends CanvasLayer
## The Pilgrim's Satchel — Tab opens it. Two leaves: the SATCHEL (arms and
## relics; drag or click an arm onto a hand-slot 1-5) and the RITES (known
## spells; click or drop one to attune it to X). Fully mouse-driven — click
## rows, click slots, or drag between them — with W/S + 1-5 + Q/E still live.

const GOLD := Color(0.95, 0.8, 0.45)
const PARCH := Color(0.92, 0.88, 0.78)
const DIM := Color(0.6, 0.55, 0.45)

var player: Node
var _scroll: ScrollContainer
var _list: VBoxContainer
var _tab := "satchel"           # "satchel" | "rites"
var _tab_btns := {}
var _slots: Array = []          # hand-slot drop targets (satchel)
var _attune_slot: Panel = null  # the C-rite drop target (rites)
var _rows: Array = []           # [{id, kind, panel, head}] in view order
var _sel := 0
var _hint: Label = null
var _girdle_lbl: Label = null
var _attune_lbl: Label = null

static func open_for(p) -> void:
	if p == null or not p.get_tree().get_nodes_in_group("inventory_ui").is_empty():
		return
	p.get_tree().root.add_child(InventoryUI.new(p))

func _init(p) -> void:
	player = p

func _ready() -> void:
	layer = 22
	add_to_group("inventory_ui")
	player.lock_control(true)
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	var root := Control.new()
	root.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(root)
	var dim := ColorRect.new()
	dim.set_anchors_preset(Control.PRESET_FULL_RECT)
	dim.color = Color(0, 0, 0, 0.5)
	root.add_child(dim)

	var panel := Panel.new()
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0.045, 0.04, 0.035, 0.97)
	sb.border_color = Color(0.6, 0.5, 0.32)
	sb.set_border_width_all(1)
	panel.add_theme_stylebox_override("panel", sb)
	panel.set_anchors_preset(Control.PRESET_CENTER)
	panel.offset_left = -490; panel.offset_right = 490
	panel.offset_top = -360; panel.offset_bottom = 360
	root.add_child(panel)

	# ---- tab bar
	_add_tab(panel, "satchel", "The Satchel", 30)
	_add_tab(panel, "rites", "The Rites", 250)
	var rule := ColorRect.new()
	rule.color = Color(0.6, 0.5, 0.32, 0.6)
	rule.position = Vector2(30, 64); rule.size = Vector2(920, 1)
	panel.add_child(rule)

	# ---- scrolling list
	_scroll = ScrollContainer.new()
	_scroll.position = Vector2(30, 78); _scroll.size = Vector2(920, 520)
	_scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	panel.add_child(_scroll)
	_list = VBoxContainer.new()
	_list.custom_minimum_size = Vector2(900, 0)
	_list.add_theme_constant_override("separation", 8)
	_scroll.add_child(_list)

	# ---- hand-slot rail (satchel) + attune slot (rites) share the footer band
	_build_hand_rail(panel)
	_build_attune_slot(panel)

	_hint = Label.new()
	_hint.label_settings = _ls(16, DIM)
	_hint.set_anchors_preset(Control.PRESET_BOTTOM_LEFT)
	_hint.grow_vertical = Control.GROW_DIRECTION_BEGIN
	_hint.offset_left = 30; _hint.offset_top = -30; _hint.offset_bottom = -10
	panel.add_child(_hint)

	_show_tab("satchel")
	AudioDirector.sfx("res://assets/audio/ui_tick.wav", -8.0)

# ------------------------------------------------------------------ tabs

func _add_tab(panel: Panel, key: String, text: String, x: float) -> void:
	var b := Button.new()
	b.text = text
	b.flat = true
	b.position = Vector2(x, 18); b.size = Vector2(210, 40)
	b.add_theme_font_override("font", load("res://assets/fonts/DejaVuSerif-Bold.ttf"))
	b.add_theme_font_size_override("font_size", 26)
	b.add_theme_color_override("font_color", DIM)
	b.add_theme_color_override("font_hover_color", PARCH)
	b.pressed.connect(func(): _show_tab(key))
	panel.add_child(b)
	_tab_btns[key] = b

func _show_tab(key: String) -> void:
	_tab = key
	for k in _tab_btns:
		(_tab_btns[k] as Button).add_theme_color_override("font_color", GOLD if k == key else DIM)
	_sel = 0
	_rebuild_list()
	for s in _slots:
		(s["panel"] as Control).visible = (key == "satchel")
	_attune_slot.visible = (key == "rites")
	if _girdle_lbl != null: _girdle_lbl.visible = (key == "satchel")
	if _attune_lbl != null: _attune_lbl.visible = (key == "rites")
	_hint.text = ("A/D — leaf     W/S — choose     1-5 or drag — set the arm in that hand-slot     Tab — close" \
		if key == "satchel" else \
		"A/D — leaf     W/S — choose     Enter/click/drag — attune the rite to  X     Tab — close")

# ------------------------------------------------------------------ list

func _rebuild_list() -> void:
	for c in _list.get_children():
		c.queue_free()
	_rows.clear()
	if _tab == "satchel":
		_fill_satchel()
	else:
		_fill_rites()
	_mark_selected.call_deferred()

func _fill_satchel() -> void:
	_section("ARMS")
	for id in DB.table("weapons"):
		if player.owns_weapon(id):
			var w: Dictionary = DB.table("weapons")[id]
			var nm: String = w.get("name", id)
			if id == player.weapon_id: nm += "   — in hand"
			if int(player.weapon_level) > 0: nm += "  (+%d)" % int(player.weapon_level)
			_row(id, "arm", _icon_for(id), nm, "", w.get("desc", ""))
	_row("flask", "flask", "res://assets/ui/icons/flask.png", "Chrism Flask",
		"✕%d / %d" % [player.flasks, player.flask_max], DB.item("chrism_flask").get("desc", ""))
	_section("RELICS & GOODS")
	var any := false
	for id in player.inventory:
		if not DB.weapon(id).is_empty() or not DB.spell(id).is_empty():
			continue
		var n := int(player.inventory[id])
		if n <= 0: continue
		any = true
		var it: Dictionary = DB.item(id)
		_relic_row(_icon_for(id), it.get("name", String(id).capitalize()), "✕%d" % n,
			it.get("desc", "A keepsake of the road. The kingdom has forgotten what it was for."))
	if not any:
		_note("    Nothing but road-dust and resolve.")

func _fill_rites() -> void:
	_section("KNOWN RITES")
	var any := false
	for id in DB.table("spells"):
		if int(player.inventory.get(id, 0)) < 1:
			continue
		any = true
		var sp: Dictionary = DB.table("spells")[id]
		var nm: String = sp.get("name", id)
		if id == player.attuned_spell: nm += "   — attuned  [X]"
		_row(id, "spell", _icon_for(id), nm,
			"%d wick" % int(sp.get("mana", 0)), sp.get("desc", ""))
	if not any:
		_note("    No rites yet. The Prior of the First Wick teaches them.")

# ------------------------------------------------------------------ rows

## A selectable, draggable row (arm / flask / spell). Click acts on it; drag
## carries {id, kind} to a hand-slot or the attune slot.
func _row(id: String, kind: String, icon_path: String, nm: String, tag: String, desc: String) -> void:
	var idx := _rows.size()
	var pc := PanelContainer.new()
	var st := StyleBoxFlat.new()
	st.bg_color = Color(0, 0, 0, 0)
	st.set_corner_radius_all(3)
	pc.add_theme_stylebox_override("panel", st)
	pc.mouse_filter = Control.MOUSE_FILTER_STOP
	pc.set_meta("box", st)
	pc.gui_input.connect(_on_row_input.bind(idx))
	pc.set_drag_forwarding(_drag_row.bind(pc, id, kind), Callable(), Callable())
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 14)
	pc.add_child(row)
	var icon := TextureRect.new()
	icon.custom_minimum_size = Vector2(40, 40)
	icon.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	icon.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	icon.mouse_filter = Control.MOUSE_FILTER_IGNORE
	if ResourceLoader.exists(icon_path): icon.texture = load(icon_path)
	row.add_child(icon)
	var col := VBoxContainer.new()
	col.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	col.mouse_filter = Control.MOUSE_FILTER_IGNORE
	row.add_child(col)
	var head := Label.new()
	head.label_settings = _ls(22, PARCH, "res://assets/fonts/DejaVuSerif-Bold.ttf")
	head.text = nm + ("      " + tag if tag != "" else "")
	head.mouse_filter = Control.MOUSE_FILTER_IGNORE
	col.add_child(head)
	var body := Label.new()
	body.label_settings = _ls(16, Color(0.66, 0.62, 0.54))
	body.text = desc
	body.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	body.custom_minimum_size = Vector2(820, 0)
	body.mouse_filter = Control.MOUSE_FILTER_IGNORE
	col.add_child(body)
	_list.add_child(pc)
	_rows.append({"id": id, "kind": kind, "panel": pc, "head": head})

func _relic_row(icon_path: String, nm: String, tag: String, desc: String) -> void:
	# unbindable lore items — no selection, no drag
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 14)
	_list.add_child(row)
	var icon := TextureRect.new()
	icon.custom_minimum_size = Vector2(40, 40)
	icon.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	icon.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	if ResourceLoader.exists(icon_path): icon.texture = load(icon_path)
	row.add_child(icon)
	var col := VBoxContainer.new()
	col.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_child(col)
	var head := Label.new()
	head.label_settings = _ls(22, PARCH, "res://assets/fonts/DejaVuSerif-Bold.ttf")
	head.text = nm + ("      " + tag if tag != "" else "")
	col.add_child(head)
	var body := Label.new()
	body.label_settings = _ls(16, Color(0.66, 0.62, 0.54))
	body.text = desc
	body.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	body.custom_minimum_size = Vector2(820, 0)
	col.add_child(body)

func _section(text: String) -> void:
	var l := Label.new()
	l.label_settings = _ls(19, Color(0.72, 0.6, 0.4), "res://assets/fonts/DejaVuSerif-Bold.ttf")
	l.text = text
	_list.add_child(l)

func _note(text: String) -> void:
	var l := Label.new()
	l.label_settings = _ls(19, DIM)
	l.text = text
	_list.add_child(l)

func _on_row_input(event: InputEvent, idx: int) -> void:
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		_sel = idx
		_mark_selected()
		_act_selected()   # click acts: spell attunes; arm awaits a slot

## Clicking a rite attunes it outright; clicking an arm only selects it (it
## still needs a hand-slot, by 1-5, click, or drag).
func _act_selected() -> void:
	if _sel >= _rows.size():
		return
	var r: Dictionary = _rows[_sel]
	if r["kind"] == "spell":
		player.attune_spell(r["id"])
		Game.toast.emit("%s is attuned. Cast with X." % _name_of(r["id"]))
		AudioDirector.sfx("res://assets/audio/ui_tick.wav", -8.0)
		_rebuild_list()

# ------------------------------------------------------------------ hand rail

func _build_hand_rail(panel: Panel) -> void:
	for i in 5:
		var pnl := Panel.new()
		var st := StyleBoxFlat.new()
		st.bg_color = Color(0.08, 0.07, 0.05, 0.9)
		st.border_color = Color(0.45, 0.38, 0.26)
		st.set_border_width_all(1); st.set_corner_radius_all(3)
		pnl.add_theme_stylebox_override("panel", st)
		pnl.position = Vector2(30 + i * 72, 620); pnl.size = Vector2(60, 60)
		pnl.set_drag_forwarding(Callable(), _can_drop_hand, _drop_hand.bind(i))
		pnl.gui_input.connect(_on_hand_input.bind(i))
		panel.add_child(pnl)
		var num := Label.new()
		num.label_settings = _ls(13, Color(0.75, 0.66, 0.5))
		num.position = Vector2(4, 0); num.text = str(i + 1)
		num.mouse_filter = Control.MOUSE_FILTER_IGNORE
		pnl.add_child(num)
		var icon := TextureRect.new()
		icon.position = Vector2(8, 10); icon.size = Vector2(44, 44)
		icon.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		icon.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		icon.mouse_filter = Control.MOUSE_FILTER_IGNORE
		pnl.add_child(icon)
		_slots.append({"panel": pnl, "icon": icon})
	var lbl := Label.new()
	lbl.label_settings = _ls(15, DIM)
	lbl.text = "the girdle"
	lbl.position = Vector2(408, 640)
	panel.add_child(lbl)
	_girdle_lbl = lbl
	_refresh_hand()

func _refresh_hand() -> void:
	for i in _slots.size():
		var id: String = String(player.hotbar[i])
		var icon: TextureRect = _slots[i]["icon"]
		icon.texture = load(_icon_for(id)) if (id != "" and ResourceLoader.exists(_icon_for(id))) else null

func _on_hand_input(event: InputEvent, i: int) -> void:
	# click a slot with an arm selected -> bind it there
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		if _tab == "satchel" and _sel < _rows.size() and _rows[_sel]["kind"] in ["arm", "flask"]:
			_bind_hand(i, _rows[_sel]["id"])

func _can_drop_hand(_at, data) -> bool:
	return data is Dictionary and data.get("kind", "") in ["arm", "flask"]

func _drop_hand(_at, data, i: int) -> void:
	_bind_hand(i, data["id"])

func _bind_hand(i: int, id: String) -> void:
	player.set_hotbar_slot(i, id)
	_refresh_hand()
	Game.toast.emit("%s rides in slot %d." % [_name_of(id), i + 1])
	AudioDirector.sfx("res://assets/audio/ui_tick.wav", -8.0)

# ------------------------------------------------------------------ attune slot

func _build_attune_slot(panel: Panel) -> void:
	_attune_slot = Panel.new()
	var st := StyleBoxFlat.new()
	st.bg_color = Color(0.1, 0.085, 0.04, 0.9)
	st.border_color = GOLD
	st.set_border_width_all(1); st.set_corner_radius_all(3)
	_attune_slot.add_theme_stylebox_override("panel", st)
	_attune_slot.position = Vector2(30, 620); _attune_slot.size = Vector2(60, 60)
	_attune_slot.set_drag_forwarding(Callable(), _can_drop_attune, _drop_attune)
	panel.add_child(_attune_slot)
	var c := Label.new()
	c.label_settings = _ls(22, GOLD, "res://assets/fonts/DejaVuSerif-Bold.ttf")
	c.text = "X"; c.position = Vector2(22, 14)
	c.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_attune_slot.add_child(c)
	var lbl := Label.new()
	lbl.label_settings = _ls(15, DIM)
	lbl.text = "the rite on your tongue  —  drop a spell here, or click it"
	lbl.position = Vector2(104, 640)
	panel.add_child(lbl)
	_attune_lbl = lbl

func _can_drop_attune(_at, data) -> bool:
	return data is Dictionary and data.get("kind", "") == "spell"

func _drop_attune(_at, data) -> void:
	player.attune_spell(data["id"])
	Game.toast.emit("%s is attuned. Cast with X." % _name_of(data["id"]))
	AudioDirector.sfx("res://assets/audio/ui_tick.wav", -8.0)
	_rebuild_list()

# ------------------------------------------------------------------ drag

func _drag_row(_at, ctrl: Control, id: String, kind: String) -> Variant:
	var prev := Panel.new()
	prev.size = Vector2(56, 56)
	var st := StyleBoxFlat.new()
	st.bg_color = Color(0.12, 0.1, 0.06, 0.95); st.border_color = GOLD
	st.set_border_width_all(1); st.set_corner_radius_all(3)
	prev.add_theme_stylebox_override("panel", st)
	var icon := TextureRect.new()
	icon.set_anchors_preset(Control.PRESET_FULL_RECT)
	icon.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	icon.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	var ip := _icon_for(id)
	if ResourceLoader.exists(ip): icon.texture = load(ip)
	prev.add_child(icon)
	ctrl.set_drag_preview(prev)
	return {"id": id, "kind": kind}

# ------------------------------------------------------------------ keyboard

func _input(event: InputEvent) -> void:
	if event.is_action_pressed("inventory") or event.is_action_pressed("ui_cancel"):
		close(); get_viewport().set_input_as_handled(); return
	if event.is_action_pressed("move_left"):
		_show_tab("satchel"); get_viewport().set_input_as_handled(); return
	if event.is_action_pressed("move_right"):
		_show_tab("rites"); get_viewport().set_input_as_handled(); return
	if event.is_action_pressed("move_forward"):
		_sel = maxi(_sel - 1, 0); _mark_selected(); _scroll.scroll_vertical -= 56; return
	if event.is_action_pressed("move_back"):
		_sel = mini(_sel + 1, _rows.size() - 1); _mark_selected(); _scroll.scroll_vertical += 56; return
	if event.is_action_pressed("interact") and _sel < _rows.size():
		_act_selected(); get_viewport().set_input_as_handled(); return
	for i in 5:
		if event.is_action_pressed("hotbar_%d" % (i + 1)) and _tab == "satchel" \
				and _sel < _rows.size() and _rows[_sel]["kind"] in ["arm", "flask"]:
			_bind_hand(i, _rows[_sel]["id"])
			get_viewport().set_input_as_handled(); return

func _mark_selected() -> void:
	for i in _rows.size():
		var st: StyleBoxFlat = _rows[i]["panel"].get_meta("box")
		st.bg_color = Color(0.16, 0.13, 0.07, 0.92) if i == _sel else Color(0, 0, 0, 0)
		(_rows[i]["head"] as Label).label_settings.font_color = GOLD if i == _sel else PARCH

# ------------------------------------------------------------------ helpers

func _name_of(id: String) -> String:
	if not DB.weapon(id).is_empty(): return DB.weapon(id).get("name", id)
	if not DB.spell(id).is_empty(): return DB.spell(id).get("name", id)
	if id == "flask": return "Chrism Flask"
	return String(id).capitalize()

func _icon_for(id: String) -> String:
	var by := {
		"cloistersword": "sword", "marsh_spear": "spear", "lark_bow": "bow",
		"pilgrim_greatsword": "greatsword", "arrows": "arrows", "torch": "torch",
		"flask": "flask", "sexton_maul": "greatsword", "ward_halberd": "spear",
		"mend": "mend", "radiant_blast": "blast", "radiant_burst": "burst",
		"morrow_lance": "lance", "vesper_ward": "ward",
	}
	return "res://assets/ui/icons/%s.png" % by.get(id, "relic")

func _ls(size: int, color: Color, font := "res://assets/fonts/DejaVuSerif.ttf") -> LabelSettings:
	var ls := LabelSettings.new()
	ls.font = load(font); ls.font_size = size; ls.font_color = color
	return ls

func close() -> void:
	if player != null and is_instance_valid(player):
		player.lock_control(false)
		player.suppress_interact(10)
		Input.mouse_mode = Input.MOUSE_MODE_CONFINED_HIDDEN if player.look_compat else Input.MOUSE_MODE_CAPTURED
	AudioDirector.sfx("res://assets/audio/ui_tick.wav", -10.0)
	queue_free()
