class_name HUD
extends CanvasLayer
## The Latecomer's HUD: vitals top-left, flask bottom-left, orisons bottom-
## right, interact prompt center, boss bar bottom-center, death splash,
## diegetic toasts. Gothic restraint: thin serif, dark panels, gold accents.

const SERIF := "res://assets/fonts/DejaVuSerif.ttf"
const SERIF_B := "res://assets/fonts/DejaVuSerif-Bold.ttf"

var hp_fill: ColorRect
var mana_panel: Control
var mana_fill: ColorRect
var hp_ghost: ColorRect
var st_fill: ColorRect
var hp_panel: Control
var st_panel: Control
var flask_label: Label
var orisons_label: Label
var prompt_label: Label
var toast_label: Label
var splash: Control
var splash_label: Label
var vignette: ColorRect
var boss_root: Control
var boss_fill: ColorRect
var boss_name: Label

var _hp_ratio := 1.0
var _ghost_ratio := 1.0
var _st_ratio := 1.0
var _boss: Node = null

const HP_W := 420.0
const ST_W := 340.0

var lore_root: Control
var lore_text: Label
var _lore_panel: Panel
var _lore_hint: Label
var pose_label: Label

# the girdle: five slots along the bottom edge (1-4 arms, 5 the flask)
var hotbar_root: Control
var _slots: Array = []
var arrows_chip: Label
var rite_panel: Panel
var rite_icon: TextureRect
var rite_cost: Label
const SLOT_ICON := {
	"cloistersword": "res://assets/ui/icons/sword.png",
	"marsh_spear": "res://assets/ui/icons/spear.png",
	"lark_bow": "res://assets/ui/icons/bow.png",
	"pilgrim_greatsword": "res://assets/ui/icons/greatsword.png",
	"flask": "res://assets/ui/icons/flask.png",
	"torch": "res://assets/ui/icons/torch.png",
}

var _xhair: Control = null

## The archer's sight: a small gold ring-dot dead centre, shown only while
## the string is drawn or the eye is sighted.
func set_crosshair(on: bool) -> void:
	if _xhair == null:
		_xhair = Control.new()
		_xhair.set_anchors_preset(Control.PRESET_CENTER)
		_xhair.mouse_filter = Control.MOUSE_FILTER_IGNORE
		var dot := ColorRect.new()
		dot.color = Color(1.0, 0.88, 0.55, 0.9)
		dot.size = Vector2(5, 5)
		dot.position = Vector2(-2.5, -2.5)
		dot.rotation = PI / 4
		_xhair.add_child(dot)
		for off in [Vector2(-11, -1), Vector2(7, -1), Vector2(-1, -11), Vector2(-1, 7)]:
			var tick := ColorRect.new()
			tick.color = Color(1.0, 0.88, 0.55, 0.55)
			tick.size = Vector2(4, 2) if abs(off.x) > abs(off.y) else Vector2(2, 4)
			tick.position = off
			_xhair.add_child(tick)
		add_child(_xhair)
	_xhair.visible = on

func _ready() -> void:
	layer = 10
	add_to_group("hud")
	_build()
	Game.lore_panel.connect(show_lore)
	Game.orisons_changed.connect(_on_orisons)
	Game.player_forgotten.connect(_on_forgotten)
	Game.player_respawned.connect(func(): _fade_splash(false))
	Game.remembrance_reclaimed.connect(func(n): show_toast("Remembrance reclaimed — %d orisons." % n))
	Game.toast.connect(show_toast)
	StateDirector.transition_started.connect(_on_transition)
	if Game.player != null:
		_bind_player(Game.player)
	else:
		Game.player_registered.connect(_bind_player)

func _bind_player(p) -> void:
	p.health_changed.connect(_on_hp)
	p.stamina_changed.connect(_on_stamina)
	p.mana_changed.connect(_on_mana)
	p.flasks_changed.connect(_on_flasks)
	p.weapon_changed.connect(func(_id): _refresh_hotbar())
	p.inventory_changed.connect(_refresh_hotbar)
	p.attune_changed.connect(func(_id): _refresh_rite())
	p.hotbar_changed.connect(_refresh_hotbar)
	_on_hp(p.hp, p.max_hp)
	_on_stamina(p.stamina, p.max_stamina)
	_on_mana(p.mana, p.max_mana)
	_on_flasks(p.flasks, p.flask_max)
	_on_orisons(Game.orisons)
	_refresh_hotbar()

func _font(path: String, size: int, color: Color, shadow := true) -> LabelSettings:
	var ls := LabelSettings.new()
	ls.font = load(path)
	ls.font_size = size
	ls.font_color = color
	if shadow:
		ls.shadow_color = Color(0, 0, 0, 0.8)
		ls.shadow_size = 3
		ls.shadow_offset = Vector2(1, 2)
	return ls

func _bar(parent: Control, y: float, w: float, h: float, back: Color) -> Array:
	var panel := Panel.new()
	var sb := StyleBoxFlat.new()
	sb.bg_color = back
	sb.border_color = Color(0.62, 0.52, 0.34, 0.85)
	sb.set_border_width_all(1)
	sb.set_corner_radius_all(2)
	panel.add_theme_stylebox_override("panel", sb)
	panel.position = Vector2(24, y)
	panel.size = Vector2(w, h)
	parent.add_child(panel)
	var ghost := ColorRect.new()
	ghost.color = Color(0.85, 0.72, 0.5, 0.55)
	ghost.position = Vector2(2, 2)
	ghost.size = Vector2(w - 4, h - 4)
	panel.add_child(ghost)
	var fill := ColorRect.new()
	fill.position = Vector2(2, 2)
	fill.size = Vector2(w - 4, h - 4)
	panel.add_child(fill)
	return [panel, fill, ghost]

func _build() -> void:
	var root := Control.new()
	root.set_anchors_preset(Control.PRESET_FULL_RECT)
	root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(root)

	vignette = ColorRect.new()
	vignette.set_anchors_preset(Control.PRESET_FULL_RECT)
	vignette.color = Color(0.5, 0.05, 0.05, 0.0)
	vignette.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.add_child(vignette)

	var r1 := _bar(root, 26, HP_W, 16, Color(0.07, 0.05, 0.05, 0.88))
	hp_panel = r1[0]; hp_fill = r1[1]; hp_ghost = r1[2]
	hp_fill.color = Color(0.55, 0.12, 0.1)
	var r2 := _bar(root, 48, ST_W, 12, Color(0.05, 0.07, 0.05, 0.88))
	st_panel = r2[0]; st_fill = r2[1]
	st_fill.color = Color(0.35, 0.5, 0.25)
	(r2[2] as ColorRect).color = Color(0, 0, 0, 0)
	# the wick-bar: mana, kindled only once a rite is learned
	var r3 := _bar(root, 66, ST_W * 0.8, 10, Color(0.08, 0.065, 0.03, 0.88))
	mana_panel = r3[0]; mana_fill = r3[1]
	mana_fill.color = Color(0.92, 0.74, 0.3)
	(r3[2] as ColorRect).color = Color(0, 0, 0, 0)
	mana_panel.visible = false

	flask_label = Label.new()
	flask_label.label_settings = _font(SERIF_B, 26, Color(0.92, 0.86, 0.72))
	flask_label.set_anchors_preset(Control.PRESET_BOTTOM_LEFT)
	flask_label.grow_vertical = Control.GROW_DIRECTION_BEGIN
	flask_label.offset_left = 28
	flask_label.offset_top = -90
	flask_label.offset_bottom = -50
	flask_label.text = "Chrism ✕3"
	root.add_child(flask_label)

	orisons_label = Label.new()
	orisons_label.label_settings = _font(SERIF_B, 26, Color(0.95, 0.8, 0.45))
	orisons_label.set_anchors_preset(Control.PRESET_BOTTOM_RIGHT)
	orisons_label.grow_horizontal = Control.GROW_DIRECTION_BEGIN
	orisons_label.grow_vertical = Control.GROW_DIRECTION_BEGIN
	orisons_label.offset_left = -300
	orisons_label.offset_top = -95
	orisons_label.offset_right = -30
	orisons_label.offset_bottom = -55
	orisons_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	orisons_label.text = "0 orisons"

	# the surveyor's line: area, state and the live camera pose in exactly the
	# form tools/shot.sh --shot-cam takes, so any player screenshot can be
	# replayed 1:1 headlessly (dim, small, out of the composition's way)
	pose_label = Label.new()
	pose_label.label_settings = _font(SERIF_B, 13, Color(0.75, 0.72, 0.62, 0.55))
	pose_label.set_anchors_preset(Control.PRESET_BOTTOM_RIGHT)
	pose_label.grow_horizontal = Control.GROW_DIRECTION_BEGIN
	pose_label.grow_vertical = Control.GROW_DIRECTION_BEGIN
	pose_label.offset_left = -560
	pose_label.offset_top = -34
	pose_label.offset_right = -10
	pose_label.offset_bottom = -10
	pose_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	pose_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.add_child(pose_label)
	root.add_child(orisons_label)

	prompt_label = Label.new()
	prompt_label.label_settings = _font(SERIF, 24, Color(0.95, 0.92, 0.84))
	prompt_label.set_anchors_preset(Control.PRESET_CENTER)
	prompt_label.offset_left = -200
	prompt_label.offset_top = 100
	prompt_label.offset_right = 200
	prompt_label.offset_bottom = 140
	prompt_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	prompt_label.text = ""
	root.add_child(prompt_label)

	toast_label = Label.new()
	toast_label.label_settings = _font(SERIF, 28, Color(0.92, 0.88, 0.78))
	toast_label.set_anchors_preset(Control.PRESET_CENTER_TOP)
	toast_label.offset_left = -400
	toast_label.offset_top = 120
	toast_label.offset_right = 400
	toast_label.offset_bottom = 180
	toast_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	toast_label.modulate.a = 0.0
	root.add_child(toast_label)

	_build_hotbar(root)

	# boss bar
	boss_root = Control.new()
	boss_root.set_anchors_preset(Control.PRESET_FULL_RECT)
	boss_root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	boss_root.visible = false
	root.add_child(boss_root)
	boss_name = Label.new()
	boss_name.label_settings = _font(SERIF_B, 30, Color(0.93, 0.88, 0.8))
	boss_name.set_anchors_preset(Control.PRESET_CENTER_BOTTOM)
	boss_name.grow_vertical = Control.GROW_DIRECTION_BEGIN
	boss_name.offset_left = -400
	boss_name.offset_top = -174
	boss_name.offset_right = 400
	boss_name.offset_bottom = -134
	boss_name.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	boss_root.add_child(boss_name)
	var bp := Panel.new()
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0.06, 0.04, 0.04, 0.9)
	sb.border_color = Color(0.62, 0.52, 0.34, 0.9)
	sb.set_border_width_all(1)
	bp.set_anchors_preset(Control.PRESET_CENTER_BOTTOM)
	bp.grow_vertical = Control.GROW_DIRECTION_BEGIN
	bp.offset_left = -500
	bp.offset_top = -132
	bp.offset_right = 500
	bp.offset_bottom = -118
	bp.add_theme_stylebox_override("panel", sb)
	boss_root.add_child(bp)
	boss_fill = ColorRect.new()
	boss_fill.color = Color(0.6, 0.14, 0.1)
	boss_fill.position = Vector2(2, 2)
	boss_fill.size = Vector2(996, 10)
	bp.add_child(boss_fill)

	# lore panel (plaques, item descriptions)
	lore_root = Control.new()
	lore_root.set_anchors_preset(Control.PRESET_FULL_RECT)
	lore_root.visible = false
	root.add_child(lore_root)
	var ldim := ColorRect.new()
	ldim.set_anchors_preset(Control.PRESET_FULL_RECT)
	ldim.color = Color(0, 0, 0, 0.55)
	lore_root.add_child(ldim)
	_lore_panel = Panel.new()
	var lsb := StyleBoxFlat.new()
	lsb.bg_color = Color(0.05, 0.045, 0.04, 0.96)
	lsb.border_color = Color(0.6, 0.5, 0.32)
	lsb.set_border_width_all(1)
	_lore_panel.add_theme_stylebox_override("panel", lsb)
	_lore_panel.position = Vector2(510, 330)
	_lore_panel.size = Vector2(900, 400)
	lore_root.add_child(_lore_panel)
	lore_text = Label.new()
	lore_text.label_settings = _font(SERIF, 26, Color(0.9, 0.87, 0.78), false)
	lore_text.position = Vector2(46, 46)
	lore_text.size = Vector2(808, 260)
	lore_text.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_lore_panel.add_child(lore_text)
	_lore_hint = Label.new()
	_lore_hint.label_settings = _font(SERIF, 18, Color(0.6, 0.55, 0.45), false)
	_lore_hint.position = Vector2(46, 340)
	_lore_hint.text = "— press any key —"
	_lore_panel.add_child(_lore_hint)

	# death splash
	splash = Control.new()
	splash.set_anchors_preset(Control.PRESET_FULL_RECT)
	splash.mouse_filter = Control.MOUSE_FILTER_IGNORE
	splash.modulate.a = 0.0
	root.add_child(splash)
	var dim := ColorRect.new()
	dim.set_anchors_preset(Control.PRESET_FULL_RECT)
	dim.color = Color(0, 0, 0, 0.72)
	splash.add_child(dim)
	splash_label = Label.new()
	splash_label.label_settings = _font(SERIF_B, 84, Color(0.62, 0.1, 0.08), false)
	splash_label.set_anchors_preset(Control.PRESET_CENTER)
	splash_label.offset_left = -500
	splash_label.offset_top = -60
	splash_label.offset_right = 500
	splash_label.offset_bottom = 60
	splash_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	splash_label.text = "F O R G O T T E N"
	splash.add_child(splash_label)

func _process(dt: float) -> void:
	# the surveyor's line follows the live camera every frame
	var cam := get_viewport().get_camera_3d()
	if cam != null and Game.current_area_id != "":
		var st := "ruin" if Game.area_state() == VG.WState.RUIN else "glory"
		var p := cam.global_position
		var r := cam.global_rotation_degrees
		var cap := "free"
		if Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
			cap = "cap"
		elif Input.mouse_mode == Input.MOUSE_MODE_CONFINED_HIDDEN:
			cap = "cfn"
		var lock := ""
		if Game.player != null and Game.player.cam != null \
				and Game.player.cam.locked_target != null:
			lock = " lock"
		var mo := 0
		if Game.player != null:
			mo = Game.player.motion_rate
		pose_label.text = "%s | %s %s  %.1f,%.1f,%.1f,%.1f,%.1f,%.0f  s%.1f %s m%d%s" % [
			VG.BUILD, Game.current_area_id, st, p.x, p.y, p.z, r.y, r.x, cam.fov,
			float(PauseUI.settings.get("sensitivity", 5.0)), cap, mo, lock]
	elif pose_label != null:
		pose_label.text = ""
	# bar smoothing: fill snaps, ghost bleeds down slowly
	hp_fill.size.x = (HP_W - 4) * _hp_ratio
	_ghost_ratio = maxf(_hp_ratio, _ghost_ratio - dt * 0.25)
	hp_ghost.size.x = (HP_W - 4) * _ghost_ratio
	st_fill.size.x = (ST_W - 4) * _st_ratio
	if vignette.color.a > 0.0:
		vignette.color.a = maxf(0.0, vignette.color.a - dt * 1.6)
	# interact prompt
	if Game.player != null and not Game.player.dead:
		var it = Game.player.nearest_interactable()
		# a menu owns the screen: the world's prompts wait outside it
		if it == null or Game.player.busy_in_menu() or PauseUI.is_open():
			prompt_label.text = ""
		else:
			prompt_label.text = "[E]  %s" % it.prompt
	# boss bar track
	if _boss != null and is_instance_valid(_boss) and boss_root.visible:
		boss_fill.size.x = 996.0 * clampf(_boss.hp / _boss.max_hp, 0.0, 1.0)
		if _boss.dead:
			hide_boss()

func _on_hp(hp: float, max_hp: float) -> void:
	var r := clampf(hp / max_hp, 0.0, 1.0)
	if r < _hp_ratio:
		vignette.color.a = 0.28
	_hp_ratio = r

func _on_stamina(st: float, max_st: float) -> void:
	_st_ratio = clampf(st / max_st, 0.0, 1.0)

func _on_flasks(n: int, mx: int) -> void:
	flask_label.text = "Chrism ✕%d" % n
	_refresh_hotbar()

# ------------------------------------------------------------------ hotbar
## Five slots on the bottom edge: press 1-5 to draw that arm (5 drinks).
func _build_hotbar(root: Control) -> void:
	hotbar_root = Control.new()
	hotbar_root.set_anchors_preset(Control.PRESET_CENTER_BOTTOM)
	hotbar_root.grow_vertical = Control.GROW_DIRECTION_BEGIN
	hotbar_root.grow_horizontal = Control.GROW_DIRECTION_BOTH
	hotbar_root.offset_left = -170
	hotbar_root.offset_right = 170
	hotbar_root.offset_top = -86
	hotbar_root.offset_bottom = -22
	hotbar_root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.add_child(hotbar_root)
	_slots.clear()
	for i in 5:
		var panel := Panel.new()
		var sb := StyleBoxFlat.new()
		sb.bg_color = Color(0.05, 0.045, 0.04, 0.85)
		sb.border_color = Color(0.45, 0.38, 0.26, 0.8)
		sb.set_border_width_all(1)
		sb.set_corner_radius_all(3)
		panel.add_theme_stylebox_override("panel", sb)
		panel.position = Vector2(i * 70, 4)
		panel.size = Vector2(60, 60)
		panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
		hotbar_root.add_child(panel)
		var icon := TextureRect.new()
		icon.position = Vector2(6, 6)
		icon.size = Vector2(48, 48)
		icon.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		icon.stretch_mode = TextureRect.STRETCH_SCALE
		icon.mouse_filter = Control.MOUSE_FILTER_IGNORE
		panel.add_child(icon)
		var num := Label.new()
		num.label_settings = _font(SERIF_B, 13, Color(0.75, 0.66, 0.5))
		num.position = Vector2(4, 0)
		num.text = str(i + 1)
		panel.add_child(num)
		var count := Label.new()
		count.label_settings = _font(SERIF_B, 15, Color(0.95, 0.88, 0.7))
		count.set_anchors_preset(Control.PRESET_BOTTOM_RIGHT)
		count.grow_horizontal = Control.GROW_DIRECTION_BEGIN
		count.grow_vertical = Control.GROW_DIRECTION_BEGIN
		count.offset_left = -34
		count.offset_top = -22
		count.offset_right = -4
		count.offset_bottom = -2
		count.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
		count.text = ""
		panel.add_child(count)
		_slots.append({"panel": panel, "style": sb, "icon": icon, "count": count})
	arrows_chip = Label.new()
	arrows_chip.label_settings = _font(SERIF_B, 20, Color(0.92, 0.87, 0.72))
	arrows_chip.set_anchors_preset(Control.PRESET_CENTER_BOTTOM)
	arrows_chip.grow_vertical = Control.GROW_DIRECTION_BEGIN
	arrows_chip.grow_horizontal = Control.GROW_DIRECTION_BOTH
	arrows_chip.offset_left = -170
	arrows_chip.offset_right = 170
	arrows_chip.offset_top = -116
	arrows_chip.offset_bottom = -90
	arrows_chip.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	arrows_chip.visible = false
	root.add_child(arrows_chip)
	# the attuned rite: a gilt slot to the LEFT of the girdle, marked C
	rite_panel = Panel.new()
	rite_panel.set_anchors_preset(Control.PRESET_CENTER_BOTTOM)
	rite_panel.grow_vertical = Control.GROW_DIRECTION_BEGIN
	rite_panel.grow_horizontal = Control.GROW_DIRECTION_BEGIN
	rite_panel.offset_left = -250
	rite_panel.offset_right = -190
	rite_panel.offset_top = -84
	rite_panel.offset_bottom = -24
	var rsb := StyleBoxFlat.new()
	rsb.bg_color = Color(0.1, 0.085, 0.045, 0.9)
	rsb.border_color = Color(0.9, 0.75, 0.4, 0.9)
	rsb.set_border_width_all(1)
	rsb.set_corner_radius_all(3)
	rite_panel.add_theme_stylebox_override("panel", rsb)
	rite_panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.add_child(rite_panel)
	rite_icon = TextureRect.new()
	rite_icon.position = Vector2(6, 6)
	rite_icon.size = Vector2(48, 48)
	rite_icon.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	rite_icon.stretch_mode = TextureRect.STRETCH_SCALE
	rite_icon.mouse_filter = Control.MOUSE_FILTER_IGNORE
	rite_panel.add_child(rite_icon)
	var rkey := Label.new()
	rkey.label_settings = _font(SERIF_B, 13, Color(0.95, 0.82, 0.45))
	rkey.position = Vector2(4, 0)
	rkey.text = "X"
	rite_panel.add_child(rkey)
	rite_cost = Label.new()
	rite_cost.label_settings = _font(SERIF_B, 14, Color(0.92, 0.82, 0.5))
	rite_cost.set_anchors_preset(Control.PRESET_BOTTOM_RIGHT)
	rite_cost.grow_horizontal = Control.GROW_DIRECTION_BEGIN
	rite_cost.grow_vertical = Control.GROW_DIRECTION_BEGIN
	rite_cost.offset_left = -34
	rite_cost.offset_top = -22
	rite_cost.offset_right = -4
	rite_cost.offset_bottom = -2
	rite_cost.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	rite_panel.add_child(rite_cost)
	_refresh_rite()

func _refresh_rite() -> void:
	var p = Game.player
	if p == null or not is_instance_valid(p) or rite_panel == null:
		return
	var sid: String = p.attuned_spell
	rite_panel.visible = sid != "" and not DB.spell(sid).is_empty()
	if rite_panel.visible:
		var by := {"mend": "mend", "radiant_blast": "blast", "radiant_burst": "burst",
				"morrow_lance": "lance", "vesper_ward": "ward"}
		rite_icon.texture = load("res://assets/ui/icons/%s.png" % by.get(sid, "relic"))
		rite_cost.text = str(int(DB.spell(sid).get("mana", 0)))

func _refresh_hotbar() -> void:
	var p = Game.player
	if p == null or not is_instance_valid(p) or _slots.is_empty():
		return
	for i in _slots.size():
		var slot: Dictionary = _slots[i]
		var id: String = String(p.hotbar[i])
		var icon_path: String = SLOT_ICON.get(id, "")
		var tex: Texture2D = null
		if icon_path != "" and ResourceLoader.exists(icon_path):
			tex = load(icon_path)
		(slot["icon"] as TextureRect).texture = tex
		var owned: bool = id != "" and (id == "flask" or p.owns_weapon(id))
		var selected: bool = id == p.weapon_id
		(slot["icon"] as TextureRect).modulate.a = 0.95 if owned else 0.22
		var sb: StyleBoxFlat = slot["style"]
		sb.border_color = Color(0.95, 0.8, 0.45, 0.95) if selected else Color(0.45, 0.38, 0.26, 0.8)
		sb.set_border_width_all(2 if selected else 1)
		sb.bg_color = Color(0.09, 0.075, 0.05, 0.9) if selected else Color(0.05, 0.045, 0.04, 0.85)
		var c: Label = slot["count"]
		if id == "flask":
			c.text = str(p.flasks)
		elif id == "lark_bow" and owned:
			c.text = str(int(p.inventory.get("arrows", 0)))
		else:
			c.text = ""
	var bow_up: bool = p.weapon_id == "lark_bow"
	arrows_chip.visible = bow_up
	if bow_up:
		arrows_chip.text = "Arrows ✕%d" % int(p.inventory.get("arrows", 0))

func _on_mana(v: float, mx: float) -> void:
	mana_panel.visible = mx > 0.0
	if mx > 0.0:
		mana_fill.size.x = maxf((mana_panel.size.x - 4.0) * v / mx, 0.0)
	var p = Game.player
	if rite_cost != null and p != null and is_instance_valid(p) and p.attuned_spell != "":
		var cost := float(DB.spell(p.attuned_spell).get("mana", 0))
		rite_cost.label_settings.font_color = Color(0.92, 0.82, 0.5) if v >= cost else Color(0.7, 0.35, 0.3)

func _on_orisons(n: int) -> void:
	orisons_label.text = "%d orisons" % n

func _on_forgotten() -> void:
	_fade_splash(true)

func _fade_splash(on: bool) -> void:
	var tw := create_tween()
	tw.tween_property(splash, "modulate:a", 1.0 if on else 0.0, 0.9 if on else 0.5)

func _on_transition(_a: String, to_state: VG.WState) -> void:
	show_toast("The memory gutters." if to_state == VG.WState.RUIN else "The memory kindles.")

func show_toast(text: String) -> void:
	toast_label.text = text
	var tw := create_tween()
	tw.tween_property(toast_label, "modulate:a", 1.0, 0.4)
	tw.tween_interval(2.4)
	tw.tween_property(toast_label, "modulate:a", 0.0, 0.8)

func show_lore(text: String) -> void:
	lore_text.text = text
	# the panel fits the words, not the other way round: measure the wrapped
	# text and grow the frame so nothing spills past the border or the hint
	var f: Font = lore_text.label_settings.font
	var need := f.get_multiline_string_size(text, HORIZONTAL_ALIGNMENT_LEFT,
			808.0, lore_text.label_settings.font_size).y
	var h := clampf(need + 150.0, 400.0, 860.0)
	lore_text.size = Vector2(808, h - 140.0)
	_lore_panel.size = Vector2(900, h)
	var vp := get_viewport().get_visible_rect().size
	_lore_panel.position = Vector2((vp.x - 900.0) * 0.5, maxf((vp.y - h) * 0.5, 40.0))
	_lore_hint.position = Vector2(46, h - 60.0)
	lore_root.visible = true
	if Game.player:
		Game.player.lock_control(true)
	AudioDirector.sfx("res://assets/audio/ui_tick.wav", -6.0)

func _input(event: InputEvent) -> void:
	if lore_root != null and lore_root.visible and (event is InputEventKey or event is InputEventJoypadButton) and event.is_pressed():
		lore_root.visible = false
		if Game.player:
			Game.player.lock_control(false)

func show_boss(boss: Node) -> void:
	_boss = boss
	boss_name.text = boss.cfg.get("name", "???")
	boss_root.visible = true

func hide_boss() -> void:
	boss_root.visible = false
	_boss = null
