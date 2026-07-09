class_name WickReveal
extends Node3D
## The parish's turn. The first time the vigil gutters here, the
## Immortalized walks the length of his ruined nave, says what he came to
## say, and the veil seals behind you. This node also owns the radiance
## swap his half-wax rite performs.

const LINE := "So... you've finally made it. Some things are better left forgotten, Latecomer. But since you've come this far, let me ensure you learn that, here and now — lest the wax claim another would-be crusader of a fallen kingdom. Prepare to join the memories of those so blissfully immortalized."

var _ran := false
var _sub: CanvasLayer

func _physics_process(_dt: float) -> void:
	if _ran or StateDirector.transitioning:
		return
	if Game.current_area_id != "wick_cathedral" or Game.current_area == null:
		return
	if int(Game.current_area.get("_applied")) != VG.WState.RUIN:
		return
	if World.area_flag("wick_cathedral", "met_crusader"):
		_ran = true
		return
	var p = Game.player
	if p == null or not is_instance_valid(p):
		return
	if p.global_position.z < -36.5:      # still in the lantern room
		return
	_ran = true
	World.set_area_flag("wick_cathedral", "met_crusader")
	_cutscene.call_deferred(p)

func _cutscene(p) -> void:
	var area = Game.current_area
	var fog: FogGate = null
	for n in area.ruin_layer.get_children():
		if n is FogGate:
			fog = n
	var boss = fog.boss_spawner.current if (fog != null and fog.boss_spawner != null) else null
	if boss == null or not is_instance_valid(boss):
		return
	p.lock_control(true)
	p.velocity = Vector3.ZERO
	boss.global_position = Vector3(0, 0.1, -1.5)
	boss.vis.rotation.y = 0.0            # facing the length of the nave
	if p.cam != null:
		p.cam.locked_target = boss
	boss.vis.play("walk", 0.2)
	var tw := create_tween()
	tw.tween_property(boss, "global_position", Vector3(0, 0.1, -19.0), 6.5)
	tw.tween_callback(func():
		if is_instance_valid(boss):
			boss.vis.play("idle", 0.3))
	tw.tween_interval(0.9)
	tw.tween_callback(func(): _speak(boss, fog, p))

func _speak(boss, fog, p) -> void:
	_show_sub(LINE)
	var a := AudioStreamPlayer3D.new()
	var path := "res://assets/audio/voice/crusader_intro.mp3"
	if ResourceLoader.exists(path):
		a.stream = load(path)
	a.unit_size = 16.0
	a.max_db = 3.0
	boss.add_child(a)
	a.finished.connect(func(): finish(fog, p))
	if a.stream != null:
		a.play()
	else:
		finish(fog, p)      # headless / missing audio: no dead air

func finish(fog, p) -> void:
	_close_sub()
	if p != null and is_instance_valid(p):
		p.lock_control(false)
	if fog != null and is_instance_valid(fog):
		fog._engage_boss()

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
	l.offset_left = 320
	l.offset_right = -320
	l.offset_top = -190
	l.offset_bottom = -110
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
