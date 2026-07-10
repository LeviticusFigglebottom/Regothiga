class_name WickReveal
extends Node3D
## The parish's turn. The first time the vigil gutters here, the
## Immortalized walks the length of his ruined nave, says what he came to
## say, and the veil seals behind you. This node also owns the radiance
## swap his half-wax rite performs.

const LINE := "So... you've finally made it. Some things are better left forgotten, Latecomer. But since you've come this far, let me ensure you learn that, here and now — lest the wax claim another would-be crusader of a fallen kingdom. Prepare to join the memories of those so blissfully immortalized."

var _ran := false
var _finished := false
var _sub: CanvasLayer
var _cine: Node3D = null          # cutscene camera rig
var _cam: Camera3D = null
var _layer: CanvasLayer = null    # fade + letterbox + skip hint
var _black: ColorRect = null
var _bar_t: ColorRect = null
var _bar_b: ColorRect = null
var _boss_ref: Node3D = null
var _voice: AudioStreamPlayer3D = null
var _skipped := false

func _physics_process(_dt: float) -> void:
	# claim the veil once it exists (fog gates build after scripted nodes)
	var area = get_parent().get_parent() if get_parent() != null else null
	if area is Area:
		for n in (area as Area).ruin_layer.get_children():
			if n is FogGate and (n as FogGate).intercept == null:
				(n as FogGate).intercept = self
	set_physics_process(false)

## Called by the fog gate when the pale is parted. Returns true when the
## reveal stages the engagement itself (first meeting only).
func on_parted(_fog: FogGate, p) -> bool:
	if _ran or World.area_flag("wick_cathedral", "met_crusader"):
		return false
	_ran = true
	World.set_area_flag("wick_cathedral", "met_crusader")
	_cutscene.call_deferred(p)
	return true

## A proper cinematic, in the grammar of the ferry and the opening rite: its
## own camera tracking ahead of him down the nave, letterbox bars, a dip to
## black on either end, any input skips. The live area is the set.
func _cutscene(p) -> void:
	var area = Game.current_area
	var fog: FogGate = null
	for n in area.ruin_layer.get_children():
		if n is FogGate:
			fog = n
	var boss = fog.boss_spawner.current if (fog != null and fog.boss_spawner != null) else null
	if boss == null or not is_instance_valid(boss):
		return
	_boss_ref = boss
	p.lock_control(true)
	p.velocity = Vector3.ZERO
	boss.global_position = Vector3(0, 0.1, -1.5)
	boss.vis.rotation.y = 0.0            # facing the length of the nave
	_cine_begin(boss)
	boss.vis.play("walk", 0.2)
	var tw := create_tween()
	tw.tween_property(boss, "global_position", Vector3(0, 0.1, -19.0), 6.5)
	tw.tween_callback(func():
		if is_instance_valid(boss):
			boss.vis.play("idle", 0.3))
	tw.tween_interval(0.9)
	tw.tween_callback(func(): _speak(boss, fog, p))

## The rig: a camera that keeps station 5 m down-nave of him at chest height,
## framed over black bars; a hint in the corner; a dip from black on entry.
func _cine_begin(boss) -> void:
	_cine = Node3D.new()
	add_child(_cine)
	_cam = Camera3D.new()
	_cam.fov = 55
	_cine.add_child(_cam)
	_cam.global_position = boss.global_position + Vector3(0.9, 1.55, -5.0)
	_cam.look_at(boss.global_position + Vector3(0, 1.35, 0))
	_cam.make_current()
	_layer = CanvasLayer.new()
	_layer.layer = 24
	add_child(_layer)
	_black = ColorRect.new()
	_black.color = Color.BLACK
	_black.set_anchors_preset(Control.PRESET_FULL_RECT)
	_layer.add_child(_black)
	_bar_t = ColorRect.new()
	_bar_t.color = Color.BLACK
	_bar_t.set_anchors_preset(Control.PRESET_TOP_WIDE)
	_bar_t.offset_bottom = 110
	_layer.add_child(_bar_t)
	_bar_b = ColorRect.new()
	_bar_b.color = Color.BLACK
	_bar_b.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	_bar_b.offset_top = -110
	_layer.add_child(_bar_b)
	var hint := Label.new()
	hint.text = "press any key to skip"
	var hls := LabelSettings.new()
	hls.font = load("res://assets/fonts/DejaVuSerif.ttf")
	hls.font_size = 15
	hls.font_color = Color(0.6, 0.57, 0.5, 0.55)
	hint.label_settings = hls
	hint.set_anchors_preset(Control.PRESET_BOTTOM_RIGHT)
	hint.grow_horizontal = Control.GROW_DIRECTION_BEGIN
	hint.grow_vertical = Control.GROW_DIRECTION_BEGIN
	hint.offset_left = -240
	hint.offset_top = -40
	_layer.add_child(hint)
	create_tween().tween_property(_black, "color:a", 0.0, 0.9)
	set_process(true)
	set_process_unhandled_input(true)

## Camera station-keeping: ahead of his walk, drifting to a slow push-in as
## he stands and speaks.
func _process(dt: float) -> void:
	if _cam == null or _boss_ref == null or not is_instance_valid(_boss_ref):
		return
	var bp: Vector3 = _boss_ref.global_position
	var want := bp + Vector3(0.9, 1.55, -5.0)
	_cam.global_position = _cam.global_position.lerp(want, 1.0 - exp(-3.0 * dt))
	_cam.look_at(bp + Vector3(0, 1.35, 0))

func _unhandled_input(event: InputEvent) -> void:
	if _cine == null or _skipped:
		return
	if (event is InputEventKey and event.pressed) \
			or (event is InputEventMouseButton and event.pressed) \
			or (event is InputEventJoypadButton and event.pressed):
		_skipped = true
		_skip_to_duel()

func _skip_to_duel() -> void:
	if _boss_ref != null and is_instance_valid(_boss_ref):
		_boss_ref.global_position = Vector3(0, 0.1, -19.0)
		_boss_ref.vis.play("idle", 0.1)
	if _voice != null and is_instance_valid(_voice):
		_voice.stop()
	var area = Game.current_area
	var fog: FogGate = null
	if area != null:
		for n in area.ruin_layer.get_children():
			if n is FogGate:
				fog = n
	finish(fog, Game.player)

func _speak(boss, fog, p) -> void:
	if _finished:
		return
	_show_sub(LINE)
	var a := AudioStreamPlayer3D.new()
	var path := "res://assets/audio/voice/crusader_intro.mp3"
	if ResourceLoader.exists(path):
		a.stream = load(path)
	a.unit_size = 16.0
	a.max_db = 3.0
	boss.add_child(a)
	_voice = a
	a.finished.connect(func(): finish(fog, p))
	if a.stream != null:
		a.play()
	else:
		finish(fog, p)      # headless / missing audio: no dead air

func finish(fog, p) -> void:
	if _finished:
		return
	_finished = true
	_close_sub()
	_cine_end()
	if p != null and is_instance_valid(p):
		p.lock_control(false)
	if fog != null and is_instance_valid(fog):
		fog._engage_boss()

## Hand the eye back: a short dip to black, the rig frees (the viewport
## falls back to the gameplay camera, as the ferry does it), then the dip
## lifts and the duel owns the frame.
func _cine_end() -> void:
	set_process(false)
	set_process_unhandled_input(false)
	if _layer != null and is_instance_valid(_layer):
		var l := _layer
		var b := _black
		var rig := _cine
		var tw := create_tween()
		tw.tween_property(b, "color:a", 1.0, 0.35)
		tw.tween_callback(func():
			if rig != null and is_instance_valid(rig):
				rig.queue_free())
		tw.tween_property(b, "color:a", 0.0, 0.55)
		tw.tween_callback(l.queue_free)
	elif _cine != null and is_instance_valid(_cine):
		_cine.queue_free()
	_cine = null
	_cam = null
	_layer = null

func _show_sub(text: String) -> void:
	_sub = CanvasLayer.new()
	_sub.layer = 25
	var l := Label.new()
	var ls := LabelSettings.new()
	ls.font = load("res://assets/fonts/DejaVuSerif.ttf")
	ls.font_size = 26
	ls.font_color = Color(0.92, 0.88, 0.78)
	ls.shadow_color = Color(0, 0, 0, 0.85)
	ls.shadow_offset = Vector2(1, 2)
	l.label_settings = ls
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	l.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	l.offset_left = 280
	l.offset_right = -280
	l.offset_top = -250
	l.offset_bottom = -26
	l.vertical_alignment = VERTICAL_ALIGNMENT_BOTTOM
	l.text = text
	_sub.add_child(l)
	add_child(_sub)

func _close_sub() -> void:
	if _sub != null and is_instance_valid(_sub):
		_sub.queue_free()
		_sub = null

## Phase-two radiance: the church remembers itself around the duel — light
## and dressing only. The praying dead and the pews stay out of the arena,
## the ruin's litter fades, and nothing regains collision.
static func radiance(area) -> void:
	if area == null:
		return
	area.env.snap(VG.WState.GLORY)
	area.glory_layer.visible = true
	for n in area.glory_layer.get_children():
		if n is NPC or n is Spawner:
			if n is Node3D:
				(n as Node3D).visible = false
		elif n is Node3D and String(n.get_meta("kit_id", "")) == "pew_3m":
			(n as Node3D).visible = false
	for n in area.ruin_layer.get_children():
		if n is Node3D and not (n is Spawner or n is FogGate or n is Enemy or n is SummonGlyph):
			(n as Node3D).visible = false
