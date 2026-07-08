class_name IntroDirector
extends Node3D
## The opening rite: stylized story cards over a slow camera drift through the
## kingdom's quarters — glory and ruin — ending on the vigil-wave cascading
## over the porch city. Plays once on a fresh pilgrimage; any input skips.

signal finished

const SERIF := "res://assets/fonts/DejaVuSerif.ttf"

## Each beat: area/state to stage, a camera rail (from -> to, aimed at look),
## the card text, and how long the drift holds.
var beats := [
	{"area": "basilica_porch", "state": VG.WState.GLORY,
	 "from": Vector3(-5, 5.5, 3), "to": Vector3(4, 7, 9), "look": Vector3(0, 2, 45), "dur": 8.0,
	 "text": "VESPERGARD.\nA kingdom raised to keep the Last Light —\nstreets of wax and bell-bronze,\nevery road running toward the sun."},
	{"area": "larkspire", "state": VG.WState.GLORY,
	 "from": Vector3(0, 2.5, 0.5), "to": Vector3(0, 16.5, 0.5), "look_from": Vector3(-6, 4, -4), "look_to": Vector3(-6, 18, -4), "dur": 8.0,
	 "text": "Its people prayed in vespers.\nTheir prayers cooled into ORISONS —\nsmall change of the soul,\nspent, hoarded, owed."},
	{"area": "black_gate", "state": VG.WState.RUIN,
	 "from": Vector3(3, 3.2, 19), "to": Vector3(-2, 5.5, 8), "look": Vector3(0, 4, -15), "dur": 8.0,
	 "text": "Then the Light guttered.\nVespergard did not burn.\nIt was FORGOTTEN —\nand what is forgotten falls to ruin."},
	{"area": "drowned_marches", "state": VG.WState.RUIN,
	 "from": Vector3(14, 3, 1), "to": Vector3(-8, 2.6, 0.5), "look": Vector3(-32.5, 2, 0), "dur": 8.0,
	 "text": "Only the vigil lanterns still remember.\nKneel, and they show the kingdom\nas it swore it would remain.\nRise, and the ruin returns."},
	{"area": "basilica_porch", "state": VG.WState.GLORY, "cascade": true,
	 "from": Vector3(-3, 7.5, 6), "to": Vector3(3, 8.5, 10), "look": Vector3(0, 1, 50), "dur": 10.0,
	 "text": "You are a LATECOMER —\ntoo late for the glory, too early for the mercy.\nWalk. Remember.\nPut the wardens to rest."},
]

var _cam: Camera3D
var _layer: CanvasLayer
var _black: ColorRect
var _label: Label
var _hint: Label
var _area: Area
var _orig := {}          # area_id -> state before the intro touched it
var _skipped := false
var _done := false

func _ready() -> void:
	_cam = Camera3D.new()
	_cam.fov = 68
	add_child(_cam)
	_cam.make_current()

	_layer = CanvasLayer.new()
	_layer.layer = 90
	add_child(_layer)
	_black = ColorRect.new()
	_black.color = Color.BLACK
	_black.set_anchors_preset(Control.PRESET_FULL_RECT)
	_layer.add_child(_black)

	_label = Label.new()
	_label.set_anchors_preset(Control.PRESET_FULL_RECT)
	_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	var f := load(SERIF)
	_label.add_theme_font_override("font", f)
	_label.add_theme_font_size_override("font_size", 30)
	_label.add_theme_color_override("font_color", Color(0.88, 0.84, 0.72))
	_label.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.9))
	_label.add_theme_constant_override("shadow_offset_y", 2)
	_label.modulate.a = 0.0
	_layer.add_child(_label)

	_hint = Label.new()
	_hint.text = "press any key to skip"
	_hint.set_anchors_preset(Control.PRESET_BOTTOM_RIGHT)
	_hint.position += Vector2(-260, -46)
	_hint.add_theme_font_override("font", f)
	_hint.add_theme_font_size_override("font_size", 15)
	_hint.add_theme_color_override("font_color", Color(0.6, 0.57, 0.5, 0.55))
	_layer.add_child(_hint)

	_run.call_deferred()

func _unhandled_input(event: InputEvent) -> void:
	if _done:
		return
	if (event is InputEventKey and event.pressed) \
			or (event is InputEventMouseButton and event.pressed) \
			or (event is InputEventJoypadButton and event.pressed):
		_skipped = true

func _stage(beat: Dictionary) -> void:
	if _area != null:
		_area.queue_free()
	_area = AreaBuilder.build(beat["area"])
	add_child(_area)
	if not _orig.has(beat["area"]):
		_orig[beat["area"]] = World.get_area_state(beat["area"])
	World.set_area_state(beat["area"], beat["state"])
	StateDirector.snap(_area, beat["state"])

func _fade(to_a: float, dur: float) -> void:
	var tw := create_tween()
	tw.tween_property(_black, "color:a", to_a, dur)
	await tw.finished

func _run() -> void:
	AudioDirector.play_music("res://assets/audio/theme_glory.wav", 2.0)
	for beat in beats:
		if _skipped:
			break
		_stage(beat)
		var from: Vector3 = beat["from"]
		var to: Vector3 = beat["to"]
		var lf: Vector3 = beat.get("look_from", beat.get("look", to + Vector3.FORWARD))
		var lt: Vector3 = beat.get("look_to", beat.get("look", to + Vector3.FORWARD))
		_cam.position = from
		_cam.look_at_from_position(from, lf)
		await _fade(0.0, 0.9)
		# card in
		var tw := create_tween()
		tw.tween_property(_label, "modulate:a", 1.0, 0.8)
		_label.text = beat["text"]
		# drift the rail; fire the vigil-wave mid-pan on the cascade beat
		var dur: float = beat["dur"]
		var t := 0.0
		var fired := false
		while t < dur and not _skipped:
			var dt := get_process_delta_time()
			t += dt
			var k := clampf(t / dur, 0.0, 1.0)
			var ke := k * k * (3.0 - 2.0 * k)
			var pos := from.lerp(to, ke)
			_cam.look_at_from_position(pos, lf.lerp(lt, ke))
			if beat.get("cascade", false) and not fired and t > dur * 0.28:
				fired = true
				StateDirector.transition(_area, VG.WState.RUIN, Vector3(0, 0, 14))
			await get_tree().process_frame
		# card out
		var tw2 := create_tween()
		tw2.tween_property(_label, "modulate:a", 0.0, 0.5)
		await _fade(1.0, 0.8)
	_done = true
	_hint.visible = false
	for aid in _orig:            # a fresh save must not inherit staged states
		World.set_area_state(aid, _orig[aid])
	if _area != null:
		_area.queue_free()
		_area = null
	finished.emit()

## Called by world_root once the real area and player stand ready.
func reveal_and_free() -> void:
	var tw := create_tween()
	tw.tween_property(_black, "color:a", 0.0, 1.2)
	tw.tween_callback(queue_free)
