extends Node3D
## The Bellkeeper's bell, before the Bellkeeper: it hangs whole over his
## quarters and speaks the hours while he still keeps them — a sound the
## whole cloister learns to dread. Once he is put to rest the bell is
## GONE (broken to the three fragments his radiant self will ask for).
##   {"script": ".../bell_toller.gd", "at": [20, 6.2, -8], "tag": "base",
##    "params": {"arena": "gray_cloister", "period": 26.0}}

var arena := "gray_cloister"
var period := 26.0

var _bell: Node3D = null

func _ready() -> void:
	# slain keeper, shattered bell: nothing hangs here any more
	if arena != "" and World.is_cleared(arena):
		queue_free()
		return
	if not KitLib.has_piece("bell_great"):
		return
	_bell = KitLib.instance("bell_great")
	_bell.scale = Vector3(0.85, 0.85, 0.85)
	add_child(_bell)
	var t := Timer.new()
	t.wait_time = maxf(period * randf_range(0.8, 1.2), 6.0)
	t.timeout.connect(func():
		_toll()
		t.wait_time = maxf(period * randf_range(0.8, 1.2), 6.0))
	add_child(t)
	t.start()
	# the first toll comes early: the house announces itself
	get_tree().create_timer(randf_range(4.0, 8.0), false).timeout.connect(_toll)

func _toll() -> void:
	if _bell == null or not is_instance_valid(_bell):
		return
	if arena != "" and World.is_cleared(arena):
		queue_free()
		return
	AudioDirector.sfx_at("res://assets/audio/bell_toll.wav", global_position,
			-4.0, randf_range(0.92, 1.0))
	var tw := _bell.create_tween()
	tw.tween_property(_bell, "rotation:z", 0.1, 0.5) \
		.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	tw.tween_property(_bell, "rotation:z", -0.07, 0.55) \
		.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	tw.tween_property(_bell, "rotation:z", 0.03, 0.5) \
		.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	tw.tween_property(_bell, "rotation:z", 0.0, 0.45) \
		.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
