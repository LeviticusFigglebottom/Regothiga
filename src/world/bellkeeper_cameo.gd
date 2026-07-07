class_name BellkeeperCameo
extends Node3D
## Glory-layer apparition: the Bellkeeper alive at his work, ringing the
## hours. He does not speak. If you come close, he pauses — and looks at you.

var _vis: EnemyVisual
var _t := 0.0
var _paused := false

func _ready() -> void:
	_vis = EnemyVisual.new()
	add_child(_vis)
	# Alive, he is only a man ringing the hours — no dragged war-bell, no
	# propped-up bell frame. (Both used to read as a hollow shell dumped on
	# the floor beside him.) The ruin boss keeps the dragging bell.
	var cfg: Dictionary = DB.enemy("bellkeeper").duplicate()
	cfg.erase("weapon")
	_vis.build(cfg)

func _physics_process(dt: float) -> void:
	_t += dt
	_vis.locomotion(dt, 0.0)   # breathe between tolls
	var p = Game.player
	var near: bool = p != null and global_position.distance_to(p.global_position) < 7.0
	if near and not _paused:
		_paused = true
		_t = 0.0
	elif not near and _paused and _t > 3.0:
		_paused = false
		_t = 0.0
	if _paused:
		# he stills, and the hood turns toward you
		if p != null:
			var to: Vector3 = p.global_position - global_position
			_vis.rotation.y = lerp_angle(_vis.rotation.y, atan2(-to.x, -to.z), 1.0 - exp(-1.6 * dt))
		return
	_vis.rotation.y = lerp_angle(_vis.rotation.y, PI, 1.0 - exp(-2.0 * dt))
	# toll the hour
	if fmod(_t, 9.0) < dt:
		_vis.play("atk_r", 0.3, 0.35)
		_toll.call_deferred()

func _toll() -> void:
	await get_tree().create_timer(1.5, false).timeout
	AudioDirector.sfx_at("res://assets/audio/bell_toll.wav", global_position, -6.0, 1.0)
