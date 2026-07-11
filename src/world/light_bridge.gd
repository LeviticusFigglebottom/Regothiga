extends Node3D
## The road the light makes. Once the reckoning is heard, the porch railing
## parts and a bridge of walkable light runs off the terrace to the saint's
## column on the plaza — the pilgrim way to the lightfall. Origin sits at
## the railing gap at deck level; the span extends along local -Z ("rot" in
## the area spec aims it). The deck runs a short apron PAST the torch, and
## a rail of standing light caps the far end behind it.

var length := 90.0        # railing gap -> the saint's column
var apron := 5.0          # the deck continues a little past the torch
var width := 5.2
var far_beacon := true

func _ready() -> void:
	_deck()
	_collision()
	_rails()
	_mouth_rails()
	_motes()
	if far_beacon:
		_beacon()
		_end_rail()
		_lightfall_door()

## Two planes make the glow: a soft wide wash and a brighter core strip that
## breathes. Additive, unshaded, shadowless — light, not masonry.
var _core: MeshInstance3D = null
var _pulse := 0.0

func _full() -> float:
	return length + apron

func _deck() -> void:
	var full := _full()
	# the body of the span: a translucent pale-gold ribbon (normal blend, so
	# grazing views don't integrate to a white sheet)...
	var wash := MeshInstance3D.new()
	var wm := BoxMesh.new()
	wm.size = Vector3(width, 0.1, full)
	wash.mesh = wm
	var wmat := _glow_mat(Color(0.86, 0.72, 0.42), 0.30)
	wmat.blend_mode = BaseMaterial3D.BLEND_MODE_MIX
	wash.material_override = wmat
	wash.position = Vector3(0, -0.07, -full * 0.5)
	wash.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(wash)
	# ...with a breathing additive core down its centre line...
	_core = MeshInstance3D.new()
	var cm := BoxMesh.new()
	cm.size = Vector3(width * 0.34, 0.06, full)
	_core.mesh = cm
	_core.material_override = _glow_mat(Color(1.0, 0.9, 0.62), 0.3)
	_core.position = Vector3(0, -0.03, -full * 0.5)
	_core.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(_core)
	# ...and bright running edges so the span reads at distance
	for sx in [-1.0, 1.0]:
		var edge := MeshInstance3D.new()
		var em := BoxMesh.new()
		em.size = Vector3(0.16, 0.14, full)
		edge.mesh = em
		edge.material_override = _glow_mat(Color(1.0, 0.9, 0.62), 0.55)
		edge.position = Vector3(sx * (width * 0.5 - 0.08), 0.0, -full * 0.5)
		edge.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		add_child(edge)

static func _glow_mat(col: Color, a: float) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	m.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	m.albedo_color = Color(col.r, col.g, col.b, a)
	m.cull_mode = BaseMaterial3D.CULL_DISABLED
	return m

func _collision() -> void:
	var full := _full()
	var body := StaticBody3D.new()
	body.collision_layer = 1 << (VG.L_WORLD_BASE - 1)
	var cs := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = Vector3(width, 0.3, full)
	cs.shape = box
	cs.position = Vector3(0, -0.15, -full * 0.5)   # deck top flush with origin
	body.add_child(cs)
	add_child(body)
	# the apron's far lip refuses, quietly, behind the torch
	var wall := StaticBody3D.new()
	wall.collision_layer = 1 << (VG.L_WORLD_BASE - 1)
	var wcs := CollisionShape3D.new()
	var wbox := BoxShape3D.new()
	wbox.size = Vector3(width + 1.0, 4.0, 0.4)
	wcs.shape = wbox
	wcs.position = Vector3(0, 2.0, -full + 0.5)
	wall.add_child(wcs)
	add_child(wall)
	# the saint's column is backdrop scenery (no collision of its own) but it
	# stands mid-apron now — walking through a monument breaks the spell
	var guard := StaticBody3D.new()
	guard.collision_layer = 1 << (VG.L_WORLD_BASE - 1)
	var gcs := CollisionShape3D.new()
	var gbox := BoxShape3D.new()
	gbox.size = Vector3(1.7, 3.2, 1.7)
	gcs.shape = gbox
	gcs.position = Vector3(0, 1.6, -length - 2.0)
	guard.add_child(gcs)
	add_child(guard)

## Low walls of standing light along both edges: the road holds its own.
func _rails() -> void:
	var full := _full()
	for sx in [-1.0, 1.0]:
		var glow := MeshInstance3D.new()
		var gm := BoxMesh.new()
		gm.size = Vector3(0.1, 0.85, full)
		glow.mesh = gm
		glow.material_override = _glow_mat(Color(1.0, 0.9, 0.62), 0.22)
		glow.position = Vector3(sx * (width * 0.5 + 0.05), 0.42, -full * 0.5)
		glow.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		add_child(glow)
		var body := StaticBody3D.new()
		body.collision_layer = 1 << (VG.L_WORLD_BASE - 1)
		var cs := CollisionShape3D.new()
		var box := BoxShape3D.new()
		box.size = Vector3(0.3, 2.6, full)
		cs.shape = box
		cs.position = Vector3(sx * (width * 0.5 + 0.15), 1.3, -full * 0.5)
		body.add_child(cs)
		add_child(body)

## The railing gap the bridge parts is wider than the deck: short wings of
## standing light close the open shoulders each side of the mouth, meeting
## the stone balustrade ends — no slipping off the terrace beside the road.
func _mouth_rails() -> void:
	for sx in [-1.0, 1.0]:
		var glow := MeshInstance3D.new()
		var gm := BoxMesh.new()
		gm.size = Vector3(1.8, 0.85, 0.12)
		glow.mesh = gm
		glow.material_override = _glow_mat(Color(1.0, 0.9, 0.62), 0.26)
		glow.position = Vector3(sx * (width * 0.5 + 0.85), 0.42, 0.2)
		glow.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		add_child(glow)
		var body := StaticBody3D.new()
		body.collision_layer = 1 << (VG.L_WORLD_BASE - 1)
		var cs := CollisionShape3D.new()
		var box := BoxShape3D.new()
		box.size = Vector3(2.0, 2.6, 0.3)
		cs.shape = box
		cs.position = Vector3(sx * (width * 0.5 + 0.9), 1.3, 0.2)
		body.add_child(cs)
		add_child(body)

## The beacon is the way: step into the light, and the light takes you.
func _lightfall_door() -> void:
	var door := AreaPortal.new()
	door.to_area = "gilded_sanctum"
	door.spawn_pos = Vector3(0, 0.2, 27)
	door.spawn_yaw = 0.0
	door.prompt = "Step into the light"
	door.cutscene = "ascend"
	# the ride centres its rise on the pillar, not on wherever the pilgrim
	# happened to stand: the shaft is 4.4 m past the door along local -Z
	door.set_meta("ascend_focus", Vector3(0, 0, -4.4))
	add_child(door)
	door.position = Vector3(0, 0.0, -length + 2.4)

## Gold motes drift up off the span, sparse — the light is alive.
func _motes() -> void:
	var full := _full()
	var p := CPUParticles3D.new()
	p.amount = 110
	p.lifetime = 3.2
	p.emission_shape = CPUParticles3D.EMISSION_SHAPE_BOX
	p.emission_box_extents = Vector3(width * 0.5, 0.05, full * 0.5)
	p.direction = Vector3.UP
	p.spread = 12.0
	p.initial_velocity_min = 0.25
	p.initial_velocity_max = 0.7
	p.gravity = Vector3(0, 0.12, 0)
	p.scale_amount_min = 0.015
	p.scale_amount_max = 0.045
	p.color = Color(1.0, 0.88, 0.55, 0.8)
	p.position = Vector3(0, 0.1, -full * 0.5)
	add_child(p)
	p.emitting = true

## The lightfall proper: a white-hot core sheathed in gold halos, rooted on
## the saint's column mid-apron. Nested additive shells read against bright
## sky and dark stone alike — the pillar must be unmissable, and dead-centred.
func _beacon() -> void:
	var base := Vector3(0, -4.0, -length - 2.0)
	for spec in [[0.38, 0.5, 28.0, Color(1.0, 0.98, 0.9), 0.6],
			[0.9, 1.3, 24.0, Color(1.0, 0.92, 0.66), 0.22],
			[1.7, 2.3, 19.0, Color(1.0, 0.88, 0.55), 0.08]]:
		var b := MeshInstance3D.new()
		var cm := CylinderMesh.new()
		cm.top_radius = spec[0]
		cm.bottom_radius = spec[1]
		cm.height = spec[2]
		b.mesh = cm
		b.material_override = _glow_mat(spec[3], spec[4])
		b.position = base + Vector3(0, float(spec[2]) * 0.5, 0)
		b.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		add_child(b)
	var l := OmniLight3D.new()
	l.light_color = Color(1.0, 0.9, 0.62)
	l.light_energy = 2.4
	l.omni_range = 9.0
	l.shadow_enabled = false
	l.position = Vector3(0, 1.6, -length - 2.0)
	add_child(l)
	# gilt motes rising in the shaft — the light is going somewhere
	var p := CPUParticles3D.new()
	p.amount = 60
	p.lifetime = 3.0
	p.emission_shape = CPUParticles3D.EMISSION_SHAPE_SPHERE
	p.emission_sphere_radius = 1.3
	p.direction = Vector3.UP
	p.spread = 8.0
	p.initial_velocity_min = 1.2
	p.initial_velocity_max = 2.6
	p.gravity = Vector3.ZERO
	p.scale_amount_min = 0.02
	p.scale_amount_max = 0.05
	p.color = Color(1.0, 0.9, 0.6)
	p.position = Vector3(0, 0.5, -length - 2.0)
	add_child(p)
	p.emitting = true

## A rail of standing light squares off the apron's far lip, behind the
## torch, spanning exactly rail to rail — the road ends, plainly.
func _end_rail() -> void:
	var glow := MeshInstance3D.new()
	var gm := BoxMesh.new()
	gm.size = Vector3(width + 0.2, 0.85, 0.1)
	glow.mesh = gm
	glow.material_override = _glow_mat(Color(1.0, 0.9, 0.62), 0.3)
	glow.position = Vector3(0, 0.42, -_full() + 0.5)
	glow.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(glow)

func _process(dt: float) -> void:
	_pulse += dt
	if _core != null:
		var k := 0.3 + 0.1 * sin(_pulse * 1.3) + 0.04 * sin(_pulse * 4.7)
		(_core.material_override as StandardMaterial3D).albedo_color.a = k
