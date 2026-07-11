extends Node3D
## The Stair of Light: once the pilgrim has knelt to the Scion, golden
## steps stand out of the terrace air, climbing over the parapet toward
## the castle on the clouds. Built always, hidden and inert until
## "scion_prayed" comes true (polled, so the same visit that prays can
## walk back and find the road waiting). The top landing carries the
## portal to the Keep of the Morrow.
##   {"script": ".../light_stair.gd", "at": [bx, by, bz], "rot": yaw,
##    "tag": "glory", "params": {"steps": 14, "rise": 0.5, "run": 0.95,
##     "to": "morrow_keep", "spawn": [0, 0.3, -8], "spawn_yaw": 180,
##     "flag": "scion_prayed"}}
## Local frame: the stair climbs along -Z (rotate the node to aim it).

var steps := 14
var rise := 0.5
var run := 0.95
var to := "morrow_keep"
var spawn: Array = [0, 0.3, -8]
var spawn_yaw := 180.0
var flag := "scion_prayed"

var _shown := false
var _bodies: Array = []
var _portal: AreaPortal = null

func _ready() -> void:
	var mat := StandardMaterial3D.new()
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mat.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	mat.albedo_color = Color(1.0, 0.9, 0.55, 0.55)
	var core := StandardMaterial3D.new()
	core.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	core.albedo_color = Color(1.0, 0.97, 0.85)
	for i in steps:
		var s := MeshInstance3D.new()
		var bm := BoxMesh.new()
		bm.size = Vector3(2.6, 0.16, run + 0.35)
		s.mesh = bm
		s.material_override = mat
		s.position = Vector3(0, rise * (i + 1) - 0.08, -run * (i + 1))
		s.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		add_child(s)
		var glow := MeshInstance3D.new()
		var gm := BoxMesh.new()
		gm.size = Vector3(2.3, 0.05, run + 0.1)
		glow.mesh = gm
		glow.material_override = core
		glow.position = s.position + Vector3(0, 0.09, 0)
		glow.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		add_child(glow)
	# the landing at the top
	var top_y := rise * steps
	var top_z := -run * steps
	var land := MeshInstance3D.new()
	var lm := BoxMesh.new()
	lm.size = Vector3(4.6, 0.2, 4.6)
	land.mesh = lm
	land.material_override = mat
	land.position = Vector3(0, top_y - 0.06, top_z - 2.0)
	land.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(land)
	# one smooth ramp collider under the flight, one slab under the landing
	var bit := AreaBuilder._tag_bit("glory")
	var ramp := StaticBody3D.new()
	ramp.collision_layer = 1 << (bit - 1)
	ramp.collision_mask = 0
	var rcs := CollisionShape3D.new()
	var rbox := BoxShape3D.new()
	var length := sqrt(pow(run * steps, 2) + pow(rise * steps, 2)) + 0.6
	rbox.size = Vector3(2.6, 0.2, length)
	rcs.shape = rbox
	rcs.position = Vector3(0, top_y * 0.5, top_z * 0.5)
	rcs.rotation.x = -atan2(rise * steps, run * steps)
	ramp.add_child(rcs)
	add_child(ramp)
	_bodies.append(ramp)
	var slab := StaticBody3D.new()
	slab.collision_layer = 1 << (bit - 1)
	slab.collision_mask = 0
	var scs := CollisionShape3D.new()
	var sbox := BoxShape3D.new()
	sbox.size = Vector3(4.6, 0.2, 4.6)
	scs.shape = sbox
	scs.position = land.position
	slab.add_child(scs)
	add_child(slab)
	_bodies.append(slab)
	# the road's own light
	var l := OmniLight3D.new()
	l.light_color = Color(1.0, 0.9, 0.6)
	l.light_energy = 1.6
	l.omni_range = 9.0
	l.shadow_enabled = false
	l.position = Vector3(0, top_y * 0.6, top_z * 0.5)
	add_child(l)
	# the door at the top
	_portal = AreaPortal.new()
	_portal.to_area = to
	_portal.spawn_pos = Vector3(spawn[0], spawn[1], spawn[2])
	_portal.spawn_yaw = spawn_yaw
	_portal.prompt = "Climb to the Keep of the Morrow"
	add_child(_portal)
	_portal.position = Vector3(0, top_y, top_z - 2.0)
	_apply(World.flag(flag))
	if not _shown:
		var t := Timer.new()
		t.wait_time = 0.5
		t.timeout.connect(func():
			if not _shown and World.flag(flag):
				_apply(true)
				AudioDirector.sfx("res://assets/audio/swell_kindle.wav", -4.0, 1.15)
				Game.toast.emit("A stair of light stands over the parapet.")
				t.queue_free())
		add_child(t)
		t.start()

func _apply(on: bool) -> void:
	_shown = on
	visible = on
	for b in _bodies:
		(b as StaticBody3D).collision_layer = (1 << (AreaBuilder._tag_bit("glory") - 1)) if on else 0
	if _portal != null:
		_portal._zone.enabled = on
