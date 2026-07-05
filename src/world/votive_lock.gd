class_name VotiveLock
extends Node3D
## State puzzle: tall votive stands that can only be LIT in the glory —
## in the ruin they stand cold and refuse. When every stand in the set
## burns, a world flag comes true (a FlagGate elsewhere sinks). The stands
## are memory: what you kindle in the seeing stays kindled.

var flag := "nave_votives"
var _lit: Dictionary = {}      # idx -> bool
var _stands: Array = []

func setup(spec: Dictionary) -> void:
	flag = spec.get("flag", "nave_votives")
	var i := 0
	for v in spec.get("votives", []):
		var idx := i
		var root := Node3D.new()
		root.name = "Votive_%d" % idx
		add_child(root)
		root.position = AreaBuilder._v3(v.get("at", [0, 0, 0]))
		root.rotation.y = deg_to_rad(float(v.get("rot", 0)))
		_stands.append(root)
		_lit[idx] = false
		var zone := Interactable.new()
		zone.prompt = "Kindle the votive"
		zone.setup_zone(1.5, 1.5)
		zone.activated.connect(func(_p): _try_light(idx))
		root.add_child(zone)
		_rebuild(idx, World.flag(flag))
		i += 1

func _rebuild(idx: int, lit: bool) -> void:
	var root: Node3D = _stands[idx]
	for c in root.get_children():
		if c is not Interactable:
			c.queue_free()
	var piece := KitLib.instance("votive_stand_lit" if lit else "votive_stand_cold")
	root.add_child(piece)
	KitLib.add_collision(piece, VG.L_WORLD_BASE)
	if lit:
		KitLib.add_flame_lights(piece, 1.4, 4.0)
	_lit[idx] = lit

func _try_light(idx: int) -> void:
	if _lit[idx]:
		AudioDirector.sfx_at("res://assets/audio/ui_tick.wav",
				_stands[idx].global_position, -10.0)
		return
	# only the glory remembers fire
	var aid: String = Game.current_area_id
	if aid != "" and World.get_area_state(aid) == VG.WState.RUIN:
		AudioDirector.sfx_at("res://assets/audio/impact_blocked.wav",
				_stands[idx].global_position, -8.0, 0.6)
		Game.toast.emit("The wick is drowned. Nothing takes in this hour.")
		return
	_rebuild(idx, true)
	AudioDirector.sfx_at("res://assets/audio/swell_kindle.wav",
			_stands[idx].global_position, -6.0, 1.2)
	if _lit.values().all(func(v): return v):
		World.set_flag(flag)
		World.save_game()
		AudioDirector.sfx("res://assets/audio/remembrance.wav", -2.0, 1.1)
		Game.toast.emit("Somewhere, iron lets go.")
