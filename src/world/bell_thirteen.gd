extends Node3D
## The THIRTEENTH BELL. It hangs at the end of every road the kingdom
## kept. A blessed hand may ring it; an unblessed one is refused. The
## ring is the morning: the bell swings, the world goes white, and the
## kingdom finally hears the hour it was owed.
##   {"script": ".../bell_thirteen.gd", "at": [0,0,100], "tag": "base",
##    "params": {"bless_flag": "bell_blessing", "rung_flag": "bell_thirteen_rung"}}

var bless_flag := "bell_blessing"
var rung_flag := "bell_thirteen_rung"

var _busy := false
var _zone: Interactable = null

func _ready() -> void:
	_zone = Interactable.new()
	_zone.prompt = "Ring the Thirteenth Bell"
	_zone.setup_zone(2.2, 2.2)
	_zone.activated.connect(func(_p): _try_ring())
	add_child(_zone)

func _try_ring() -> void:
	if _busy:
		return
	if not World.flag(bless_flag):
		Game.toast.emit("The bell refuses an unblessed hand. Twelve trials keep its voice.")
		AudioDirector.sfx("res://assets/audio/impact_blocked.wav", -8.0, 0.6)
		return
	_busy = true
	if _zone != null:
		_zone.enabled = false
	_ring()

func _ring() -> void:
	if Game.player != null and is_instance_valid(Game.player):
		Game.player.lock_control(true)
		Game.player.invulnerable = true
	# the bell above lends its body to the swing
	var root := get_parent()
	var bell: Node3D = null
	while root != null and not root is Area:
		root = root.get_parent()
	if root != null:
		var best := 8.0
		for n in (root as Area).find_children("*bell_great*", "", true, false):
			if n is Node3D:
				var d: float = (n as Node3D).global_position.distance_to(global_position)
				if d < best:
					best = d
					bell = n
	if bell != null:
		var tw := create_tween()
		for i in 5:
			tw.tween_property(bell, "rotation:z", 0.24 - 0.05 * i, 0.55 - 0.05 * i) \
				.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
			tw.tween_property(bell, "rotation:z", -0.24 + 0.05 * i, 0.55 - 0.05 * i) \
				.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
		tw.tween_property(bell, "rotation:z", 0.0, 0.5)
	AudioDirector.sfx("res://assets/audio/bell_toll.wav", 2.0, 0.55)
	var sfx_tw := create_tween()
	sfx_tw.tween_interval(1.4)
	sfx_tw.tween_callback(func():
		AudioDirector.sfx("res://assets/audio/bell_toll.wav", 0.0, 0.62))
	sfx_tw.tween_interval(1.5)
	sfx_tw.tween_callback(func():
		AudioDirector.sfx("res://assets/audio/remembrance.wav", -2.0, 0.8))
	# the world goes to morning (layer 9 sits beneath HUD layer 10 so the
	# ending lore plaque appears cleanly over the golden-white dawn)
	var layer := CanvasLayer.new()
	layer.layer = 9
	add_child(layer)
	var white := ColorRect.new()
	white.color = Color(1.0, 0.97, 0.88, 0.0)
	white.mouse_filter = Control.MOUSE_FILTER_IGNORE
	white.set_anchors_preset(Control.PRESET_FULL_RECT)
	layer.add_child(white)
	var wt := white.create_tween()
	wt.tween_property(white, "color:a", 1.0, 4.2) \
		.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN)
	wt.tween_callback(func():
		if not World.flag(rung_flag):
			World.set_flag(rung_flag)
			World.save_game()
		if Game.player != null and is_instance_valid(Game.player):
			Game.player.invulnerable = false
		Game.lore_panel.emit("THE THIRTEENTH HOUR\n\nThe bell you silenced twelve times answers once.\n\nSomewhere below, wax remembers being light. Somewhere below, a kingdom stirs in its sleep and does not reach for the snuffer.\n\nThe morning is not owed. It is GIVEN. Ring on, Latecomer — the hour is yours to keep now, and the keeping is the whole of it.")
		var ft := white.create_tween()
		ft.tween_interval(0.8)
		ft.tween_property(white, "color:a", 0.0, 3.0)
		ft.tween_callback(func():
			layer.queue_free()
			_busy = false
			if _zone != null:
				_zone.enabled = true))
