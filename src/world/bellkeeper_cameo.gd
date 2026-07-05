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
	_vis.build(DB.enemy("bellkeeper"))
	# bell frame beside him: two posts + beam + the great bell
	var bm_l := KitLib.instance("column_4m")
	bm_l.scale = Vector3(0.5, 0.62, 0.5)
	bm_l.position = Vector3(-1.6, 0, -1.8)
	add_child(bm_l)
	var bm_r := KitLib.instance("column_4m")
	bm_r.scale = Vector3(0.5, 0.62, 0.5)
	bm_r.position = Vector3(1.6, 0, -1.8)
	add_child(bm_r)
	var bell := KitLib.instance("bell_great")
	bell.position = Vector3(0, 1.35, -1.8)
	bell.scale = Vector3(1.2, 1.2, 1.2)
	add_child(bell)

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
