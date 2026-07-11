extends Node3D
## The Unlit Procession. A ring of keepers' stands: kindling one carries
## the flame to BOTH its neighbours as well — lit goes out, out goes lit,
## three at a stroke. The wing rests only when the whole procession burns.
## (Lights-out on a ring: from all-dark, every stand touched exactly once
## solves it — but any wandering press digs a hole that must be reasoned
## back out, so the room punishes idle kindling.)
##   {"script": ".../procession_lock.gd", "at": [...], "tag": "base",
##    "params": {"flag": "palace_candles",
##               "stands": [[-38,0,12], [-34,0,10], ...]}}

var flag := "palace_candles"
var stands: Array = []

var _lit: Array = []
var _flames: Array = []
var _lights: Array = []

func _ready() -> void:
	if World.flag(flag):
		return
	for i in stands.size():
		var at: Array = stands[i]
		var holder := Node3D.new()
		add_child(holder)
		holder.position = Vector3(at[0], at[1], at[2]) - position
		holder.rotation.y = deg_to_rad(float(i) * 61.0)
		# the COLD stand — bare wax, no sculpted flames; the carried fire is
		# ours to grant (candle cluster + light), so unlit truly reads unlit
		if KitLib.has_piece("votive_stand_cold"):
			holder.add_child(KitLib.instance("votive_stand_cold"))
		elif KitLib.has_piece("votive_stand_lit"):
			holder.add_child(KitLib.instance("votive_stand_lit"))
		var flame: Node3D = null
		if KitLib.has_piece("candle_cluster"):
			flame = KitLib.instance("candle_cluster")
			flame.position.y = 1.28
			flame.scale = Vector3(0.55, 0.55, 0.55)
			holder.add_child(flame)
		var l := OmniLight3D.new()
		l.light_color = Color(1.0, 0.8, 0.45)
		l.light_energy = 0.0
		l.omni_range = 3.6
		l.shadow_enabled = false
		l.position.y = 1.7
		holder.add_child(l)
		var z := Interactable.new()
		z.prompt = "Carry the flame"
		z.setup_zone(1.4, 1.9)
		var idx := i
		z.activated.connect(func(_p): _touch(idx))
		holder.add_child(z)
		_lit.append(false)
		_flames.append(flame)
		_lights.append(l)
		_apply(i)

func _apply(i: int) -> void:
	var on: bool = _lit[i]
	if _flames[i] != null and is_instance_valid(_flames[i]):
		(_flames[i] as Node3D).visible = on
	(_lights[i] as OmniLight3D).light_energy = 1.6 if on else 0.0

func _touch(i: int) -> void:
	if World.flag(flag):
		return
	var n := _lit.size()
	for j in [((i - 1) + n) % n, i, (i + 1) % n]:
		_lit[j] = not _lit[j]
		_apply(j)
	AudioDirector.sfx_at("res://assets/audio/swell_kindle.wav",
			global_position + Vector3(stands[i][0], 1, stands[i][2]) - position, -8.0, 1.1)
	var burning := 0
	for v in _lit:
		if v:
			burning += 1
	if burning == n:
		World.set_flag(flag)
		Game.toast.emit("The procession burns whole — the watch is kept.")
		AudioDirector.sfx("res://assets/audio/swell_kindle.wav", -2.0, 0.7)
	elif burning > 0:
		Game.toast.emit("%d of %d flames stand." % [burning, n])
