class_name HUD
extends CanvasLayer
## The Latecomer's HUD: vitals top-left, flask bottom-left, orisons bottom-
## right, interact prompt center, boss bar bottom-center, death splash,
## diegetic toasts. Gothic restraint: thin serif, dark panels, gold accents.

const SERIF := "res://assets/fonts/DejaVuSerif.ttf"
const SERIF_B := "res://assets/fonts/DejaVuSerif-Bold.ttf"

var hp_fill: ColorRect
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

func _ready() -> void:
	layer = 10
	_build()
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
	p.flasks_changed.connect(_on_flasks)
	_on_hp(p.hp, p.max_hp)
	_on_stamina(p.stamina, p.max_stamina)
	_on_flasks(p.flasks, p.flask_max)
	_on_orisons(Game.orisons)

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

	flask_label = Label.new()
	flask_label.label_settings = _font(SERIF_B, 26, Color(0.92, 0.86, 0.72))
	flask_label.position = Vector2(28, 990)
	flask_label.text = "Chrism ✕3"
	root.add_child(flask_label)

	orisons_label = Label.new()
	orisons_label.label_settings = _font(SERIF_B, 26, Color(0.95, 0.8, 0.45))
	orisons_label.position = Vector2(1620, 985)
	orisons_label.size = Vector2(270, 40)
	orisons_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	orisons_label.text = "0 orisons"
	root.add_child(orisons_label)

	prompt_label = Label.new()
	prompt_label.label_settings = _font(SERIF, 24, Color(0.95, 0.92, 0.84))
	prompt_label.set_anchors_preset(Control.PRESET_CENTER)
	prompt_label.position = Vector2(760, 640)
	prompt_label.size = Vector2(400, 40)
	prompt_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	prompt_label.text = ""
	root.add_child(prompt_label)

	toast_label = Label.new()
	toast_label.label_settings = _font(SERIF, 28, Color(0.92, 0.88, 0.78))
	toast_label.set_anchors_preset(Control.PRESET_CENTER_TOP)
	toast_label.position = Vector2(560, 130)
	toast_label.size = Vector2(800, 60)
	toast_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	toast_label.modulate.a = 0.0
	root.add_child(toast_label)

	# boss bar
	boss_root = Control.new()
	boss_root.set_anchors_preset(Control.PRESET_FULL_RECT)
	boss_root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	boss_root.visible = false
	root.add_child(boss_root)
	boss_name = Label.new()
	boss_name.label_settings = _font(SERIF_B, 30, Color(0.93, 0.88, 0.8))
	boss_name.position = Vector2(560, 906)
	boss_name.size = Vector2(800, 40)
	boss_name.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	boss_root.add_child(boss_name)
	var bp := Panel.new()
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0.06, 0.04, 0.04, 0.9)
	sb.border_color = Color(0.62, 0.52, 0.34, 0.9)
	sb.set_border_width_all(1)
	bp.position = Vector2(460, 948)
	bp.size = Vector2(1000, 14)
	bp.add_theme_stylebox_override("panel", sb)
	boss_root.add_child(bp)
	boss_fill = ColorRect.new()
	boss_fill.color = Color(0.6, 0.14, 0.1)
	boss_fill.position = Vector2(2, 2)
	boss_fill.size = Vector2(996, 10)
	bp.add_child(boss_fill)

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
	splash_label.position = Vector2(460, 470)
	splash_label.size = Vector2(1000, 120)
	splash_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	splash_label.text = "F O R G O T T E N"
	splash.add_child(splash_label)

func _process(dt: float) -> void:
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
		prompt_label.text = "[E]  %s" % it.prompt if it != null else ""
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

func show_boss(boss: Node) -> void:
	_boss = boss
	boss_name.text = boss.cfg.get("name", "???")
	boss_root.visible = true

func hide_boss() -> void:
	boss_root.visible = false
	_boss = null
