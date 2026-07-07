class_name WatcherPuzzle
extends Node3D
## The Watchers: orans statues on rotating plinths. Each interact turns a
## watcher a quarter-turn. When every watcher faces the required bearing,
## the flag turns and iron lets go somewhere. The plaque tells you the
## bearing; the dead tell you nothing.

var flag := "watchers_east"
var target_deg := -90.0
var _statues: Array = []   # [{root, statue, deg}]
var _toast := "The watchers face the morning that is owed them."

func setup(spec: Dictionary) -> void:
	flag = spec.get("flag", "watchers_east")
	target_deg = float(spec.get("target", -90))
	# data-driven station: the Watchers turn statues on plinths, the Black
	# Gate turns capstan bar-crosses on winch drums — same machinery
	var base_kit: String = spec.get("base_kit", "watcher_base")
	var turn_kit: String = spec.get("turn_kit", "statue_orans")
	var turn_y := float(spec.get("turn_y", 0.34))
	var verb: String = spec.get("verb", "Turn the watcher")
	_toast = spec.get("done_toast", _toast)
	for w in spec.get("watchers", []):
		var root := Node3D.new()
		add_child(root)
		root.position = AreaBuilder._v3(w.get("at", [0, 0, 0]))
		var base := KitLib.instance(base_kit)
		root.add_child(base)
		KitLib.add_collision(base, VG.L_WORLD_BASE)
		var statue := KitLib.instance(turn_kit)
		statue.position.y = turn_y
		statue.rotation.y = deg_to_rad(float(w.get("rot", 0)))
		root.add_child(statue)
		var entry := {"root": root, "statue": statue, "deg": float(w.get("rot", 0))}
		_statues.append(entry)
		var idx := _statues.size() - 1
		var zone := Interactable.new()
		zone.prompt = verb
		zone.setup_zone(1.5, 1.6)
		zone.activated.connect(func(_p): _turn(idx))
		root.add_child(zone)

func _turn(idx: int) -> void:
	if World.flag(flag):
		return   # the dead have settled; let them be
	var e: Dictionary = _statues[idx]
	e["deg"] = fmod(e["deg"] + 90.0, 360.0)
	var tw := create_tween()
	tw.tween_property(e["statue"], "rotation:y", deg_to_rad(e["deg"]), 0.55) \
		.set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)
	AudioDirector.sfx_at("res://assets/audio/ui_tick.wav", e["root"].global_position, -6.0, 0.7)
	_check.call_deferred()

func _check() -> void:
	await get_tree().create_timer(0.6, false).timeout
	for e in _statues:
		var d := fmod(fmod(e["deg"] - target_deg, 360.0) + 360.0, 360.0)
		if d > 1.0 and d < 359.0:
			return
	World.set_flag(flag)
	World.save_game()
	AudioDirector.sfx("res://assets/audio/remembrance.wav", -2.0, 0.9)
	Game.toast.emit(_toast)
