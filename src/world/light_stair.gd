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
	var rail_mat := StandardMaterial3D.new()
	rail_mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	rail_mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	rail_mat.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	rail_mat.albedo_color = Color(1.0, 0.93, 0.68, 0.72)
	# starter threshold step at the parapet edge so the flight meets the terrace
	var s0 := MeshInstance3D.new()
	var bm0 := BoxMesh.new()
	bm0.size = Vector3(2.6, 0.14, 0.85)
	s0.mesh = bm0
	s0.material_override = mat
	s0.position = Vector3(0, 0.12, -0.25)
	s0.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(s0)
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
	land.position = Vector3(0, top_y - 0.08, top_z - 2.0)
	land.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(land)
	var land_core := MeshInstance3D.new()
	var lcm := BoxMesh.new()
	lcm.size = Vector3(4.1, 0.05, 4.1)
	land_core.mesh = lcm
	land_core.material_override = core
	land_core.position = land.position + Vector3(0, 0.11, 0)
	land_core.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(land_core)
	# glowing side-rail ribbons along the climb + landing rim
	var slope_len := sqrt(pow(run * steps, 2) + pow(rise * steps, 2)) + 0.5
	var slope_ang := atan2(rise * steps, run * steps)
	for sx in [-1.26, 1.26]:
		var rail := MeshInstance3D.new()
		var rbm := BoxMesh.new()
		rbm.size = Vector3(0.08, 0.08, slope_len)
		rail.mesh = rbm
		rail.material_override = rail_mat
		rail.position = Vector3(sx, top_y * 0.5 + 0.55, top_z * 0.5)
		rail.rotation.x = slope_ang
		rail.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		add_child(rail)
	for lrail_spec in [
		[Vector3(-2.22, top_y + 0.55, top_z - 2.0), Vector3(0.08, 0.08, 4.5)],
		[Vector3(2.22, top_y + 0.55, top_z - 2.0), Vector3(0.08, 0.08, 4.5)],
		[Vector3(0.0, top_y + 0.55, top_z - 4.22), Vector3(4.52, 0.08, 0.08)],
	]:
		var lrail := MeshInstance3D.new()
		var lrbm := BoxMesh.new()
		lrbm.size = lrail_spec[1]
		lrail.mesh = lrbm
		lrail.material_override = rail_mat
		lrail.position = lrail_spec[0]
		lrail.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		add_child(lrail)
	# beacon column over the landing portal
	var beacon := MeshInstance3D.new()
	var bcm := CylinderMesh.new()
	bcm.top_radius = 0.55
	bcm.bottom_radius = 0.85
	bcm.height = 6.5
	beacon.mesh = bcm
	beacon.material_override = mat
	beacon.position = Vector3(0, top_y + 3.25, top_z - 2.0)
	beacon.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(beacon)
	# rising golden motes along the stair
	var motes := CPUParticles3D.new()
	var qm := QuadMesh.new()
	qm.size = Vector2(0.09, 0.09)
	var mmat := StandardMaterial3D.new()
	mmat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mmat.billboard_mode = BaseMaterial3D.BILLBOARD_PARTICLES
	mmat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mmat.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	mmat.albedo_color = Color(1.0, 0.92, 0.62, 0.85)
	qm.material = mmat
	motes.mesh = qm
	motes.amount = 36
	motes.lifetime = 3.2
	motes.emission_shape = CPUParticles3D.EMISSION_SHAPE_BOX
	motes.emission_box_extents = Vector3(1.5, 2.5, 7.5)
	motes.position = Vector3(0, top_y * 0.5 + 0.5, top_z * 0.5 - 1.0)
	motes.direction = Vector3(0, 1, 0)
	motes.spread = 20.0
	motes.gravity = Vector3(0, 0.25, 0)
	motes.initial_velocity_min = 0.25
	motes.initial_velocity_max = 0.55
	add_child(motes)
	# one smooth ramp collider under the flight, one slab under the landing,
	# plus side guardrail colliders so the pilgrim cannot slip into the void
	var bit := AreaBuilder._tag_bit(String(get_meta("state_tag", "base")))
	var ramp := StaticBody3D.new()
	ramp.collision_layer = 1 << (bit - 1)
	ramp.collision_mask = 0
	var rcs := CollisionShape3D.new()
	var rbox := BoxShape3D.new()
	var length := slope_len + 0.3
	rbox.size = Vector3(2.6, 0.2, length)
	rcs.shape = rbox
	rcs.position = Vector3(0, top_y * 0.5 - 0.08, top_z * 0.5)
	rcs.rotation.x = slope_ang
	ramp.add_child(rcs)
	for sx in [-1.4, 1.4]:
		var gcs := CollisionShape3D.new()
		var gbox := BoxShape3D.new()
		gbox.size = Vector3(0.2, 1.4, length)
		gcs.shape = gbox
		gcs.position = Vector3(sx, top_y * 0.5 + 0.6, top_z * 0.5)
		gcs.rotation.x = slope_ang
		ramp.add_child(gcs)
	add_child(ramp)
	_bodies.append(ramp)
	var slab := StaticBody3D.new()
	slab.collision_layer = 1 << (bit - 1)
	slab.collision_mask = 0
	var scs := CollisionShape3D.new()
	var sbox := BoxShape3D.new()
	sbox.size = Vector3(4.6, 0.2, 4.3)
	scs.shape = sbox
	scs.position = Vector3(0, top_y - 0.08, top_z - 2.15)
	slab.add_child(scs)
	for gspec in [
		[Vector3(-2.4, top_y + 0.6, top_z - 2.0), Vector3(0.2, 1.4, 4.6)],
		[Vector3(2.4, top_y + 0.6, top_z - 2.0), Vector3(0.2, 1.4, 4.6)],
		[Vector3(0.0, top_y + 0.6, top_z - 4.4), Vector3(4.8, 1.4, 0.2)],
	]:
		var lcs := CollisionShape3D.new()
		var lbox := BoxShape3D.new()
		lbox.size = gspec[1]
		lcs.shape = lbox
		lcs.position = gspec[0]
		slab.add_child(lcs)
	add_child(slab)
	_bodies.append(slab)
	# the road's own light
	var l := OmniLight3D.new()
	l.light_color = Color(1.0, 0.9, 0.6)
	l.light_energy = 1.8
	l.omni_range = 11.0
	l.shadow_enabled = false
	l.position = Vector3(0, top_y * 0.6, top_z * 0.5)
	add_child(l)
	var l_top := OmniLight3D.new()
	l_top.light_color = Color(1.0, 0.93, 0.68)
	l_top.light_energy = 2.0
	l_top.omni_range = 9.0
	l_top.shadow_enabled = false
	l_top.position = Vector3(0, top_y + 1.8, top_z - 2.0)
	add_child(l_top)
	# the door at the top
	_portal = AreaPortal.new()
	_portal.to_area = to
	_portal.spawn_pos = Vector3(spawn[0], spawn[1], spawn[2])
	_portal.spawn_yaw = spawn_yaw
	_portal.prompt = "Climb to the Keep of the Morrow"
	add_child(_portal)
	_portal.position = Vector3(0, top_y, top_z - 2.0)
	_apply(World.flag(flag))
	if _shown and not World.flag("morrow_stair_seen"):
		World.set_flag("morrow_stair_seen")
		var stw := create_tween()
		stw.tween_interval(0.6)
		stw.tween_callback(func():
			AudioDirector.sfx("res://assets/audio/swell_kindle.wav", -4.0, 1.15)
			Game.toast.emit("To the west, a stair of light climbs over the Sanctum parapet."))
	elif not _shown:
		var t := Timer.new()
		t.wait_time = 0.5
		t.timeout.connect(func():
			if not _shown and World.flag(flag):
				World.set_flag("morrow_stair_seen")
				_apply(true)
				AudioDirector.sfx("res://assets/audio/swell_kindle.wav", -4.0, 1.15)
				Game.toast.emit("A stair of light stands over the parapet.")
				t.queue_free())
		add_child(t)
		t.start()

func _apply(on: bool) -> void:
	_shown = on
	visible = on
	var bit := AreaBuilder._tag_bit(String(get_meta("state_tag", "base")))
	for b in _bodies:
		(b as StaticBody3D).collision_layer = (1 << (bit - 1)) if on else 0
	if _portal != null:
		_portal._zone.enabled = on
	if on and get_parent() != null and get_parent().get_parent() != null:
		var area_node := get_parent().get_parent()
		var base_layer := area_node.get_node_or_null("Base")
		if base_layer != null:
			for c in base_layer.get_children():
				if c is Node3D and c.position.x < -15.5 and absf(c.position.z - position.z) < 1.2:
					c.visible = false
					if c is StaticBody3D:
						(c as StaticBody3D).collision_layer = 0
						c.set_meta("orig_layer", 0)
					for sb in c.find_children("*", "StaticBody3D", true, false):
						(sb as StaticBody3D).collision_layer = 0
						sb.set_meta("orig_layer", 0)
