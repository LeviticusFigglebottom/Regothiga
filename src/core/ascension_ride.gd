class_name AscensionRide
extends Node3D
## The lightfall: stepping into the beacon at the bridge's end. The frame
## letterboxes, the Latecomer rises up the shaft of light amid gilt motes,
## the world whites out — and the Gilded Sanctum takes the other side.
## Same contract as FerryRide: `finished`, then reveal_and_free().

signal finished

var _cam: Camera3D
var _layer: CanvasLayer
var _white: ColorRect
var _done := false
var _player: Node3D

func _ready() -> void:
	_player = Game.player
	_cam = Camera3D.new()
	_cam.fov = 60
	add_child(_cam)
	_layer = CanvasLayer.new()
	_layer.layer = 90
	add_child(_layer)
	_white = ColorRect.new()
	_white.color = Color(1.0, 0.96, 0.86, 0.0)
	_white.set_anchors_preset(Control.PRESET_FULL_RECT)
	_layer.add_child(_white)
	for top in [true, false]:
		var bar := ColorRect.new()
		bar.color = Color.BLACK
		bar.set_anchors_preset(Control.PRESET_TOP_WIDE if top else Control.PRESET_BOTTOM_WIDE)
		if top: bar.offset_bottom = 110
		else: bar.offset_top = -110
		_layer.add_child(bar)
	_run.call_deferred()

func _run() -> void:
	if _player == null or not is_instance_valid(_player):
		_finish()
		return
	_player.set_physics_process(false)
	_player.velocity = Vector3.ZERO
	var base: Vector3 = _player.global_position
	_cam.global_position = base + Vector3(2.6, 1.2, 3.4)
	_cam.look_at(base + Vector3(0, 1.4, 0))
	_cam.make_current()
	# the shaft brightens around them
	var col := OmniLight3D.new()
	col.light_color = Color(1.0, 0.9, 0.62)
	col.light_energy = 2.2
	col.omni_range = 8.0
	col.shadow_enabled = false
	add_child(col)
	col.global_position = base + Vector3.UP * 2.0
	var motes := CPUParticles3D.new()
	motes.amount = 120
	motes.lifetime = 2.4
	motes.emission_shape = CPUParticles3D.EMISSION_SHAPE_SPHERE
	motes.emission_sphere_radius = 1.6
	motes.direction = Vector3.UP
	motes.spread = 14.0
	motes.initial_velocity_min = 2.0
	motes.initial_velocity_max = 4.5
	motes.gravity = Vector3.ZERO
	motes.scale_amount_min = 0.02
	motes.scale_amount_max = 0.06
	motes.color = Color(1.0, 0.88, 0.55)
	add_child(motes)
	motes.global_position = base + Vector3.UP * 0.4
	motes.emitting = true
	AudioDirector.sfx("res://assets/audio/swell_kindle.wav", 0.0, 0.8)
	# the rise: slow first breath, then taken
	var tw := create_tween()
	tw.tween_property(_player, "global_position", base + Vector3.UP * 2.2, 1.6) \
		.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN)
	tw.parallel().tween_property(col, "light_energy", 6.0, 1.6)
	tw.tween_property(_player, "global_position", base + Vector3.UP * 13.0, 1.4) \
		.set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_IN)
	tw.parallel().tween_property(_white, "color:a", 1.0, 1.3)
	tw.tween_callback(_finish)

func _process(dt: float) -> void:
	if _player == null or not is_instance_valid(_player) or _cam == null:
		return
	var pp: Vector3 = _player.global_position
	var want := pp + Vector3(2.6, 0.6, 3.4)
	_cam.global_position = _cam.global_position.lerp(want, 1.0 - exp(-2.4 * dt))
	_cam.look_at(pp + Vector3(0, 1.2, 0))

func _finish() -> void:
	if _done:
		return
	_done = true
	if _player != null and is_instance_valid(_player):
		_player.set_physics_process(true)
	finished.emit()

## The other side: hold the white over the arrival, then let it part. The
## ride's camera dies under full white so the player's own takes the frame —
## the light parts over the dais, not over the sky the ride left behind.
func reveal_and_free() -> void:
	set_process(false)
	if _cam != null and is_instance_valid(_cam):
		_cam.queue_free()
		_cam = null
	var tw := create_tween()
	tw.tween_interval(0.35)
	tw.tween_property(_white, "color:a", 0.0, 1.4)
	tw.tween_callback(queue_free)
