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
var _tongues: Array = []

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
		l.omni_range = 4.2
		l.shadow_enabled = false
		l.position.y = 1.7
		holder.add_child(l)
		# the flame made unmistakable: a tall bright tongue over the wax,
		# there when lit, gone when cold — readable across the whole vault
		var tongue := MeshInstance3D.new()
		var tm := CylinderMesh.new()
		tm.top_radius = 0.01
		tm.bottom_radius = 0.09
		tm.height = 0.55
		var tmat := StandardMaterial3D.new()
		tmat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		tmat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
		tmat.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
		tmat.albedo_color = Color(1.0, 0.82, 0.4, 0.85)
		tm.material = tmat
		tongue.mesh = tm
		tongue.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		tongue.position.y = 1.62
		tongue.visible = false
		holder.add_child(tongue)
		var ttw := tongue.create_tween()
		ttw.set_loops(0)
		ttw.tween_property(tongue, "scale", Vector3(1.15, 1.25, 1.15), 0.5).set_trans(Tween.TRANS_SINE)
		ttw.tween_property(tongue, "scale", Vector3(0.9, 0.92, 0.9), 0.5).set_trans(Tween.TRANS_SINE)
		var z := Interactable.new()
		z.prompt = "Kindle the flame"
		z.setup_zone(1.4, 1.9)
		var idx := i
		z.activated.connect(func(_p): _touch(idx))
		holder.add_child(z)
		_lit.append(false)
		_flames.append(flame)
		_lights.append(l)
		_tongues.append(tongue)
		_apply(i)

func _apply(i: int) -> void:
	var on: bool = _lit[i]
	if _flames[i] != null and is_instance_valid(_flames[i]):
		(_flames[i] as Node3D).visible = on
	(_lights[i] as OmniLight3D).light_energy = 2.4 if on else 0.0
	if i < _tongues.size() and _tongues[i] != null and is_instance_valid(_tongues[i]):
		(_tongues[i] as Node3D).visible = on

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
