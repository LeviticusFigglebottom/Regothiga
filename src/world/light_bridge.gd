extends Node3D
## The road the light makes. Once the reckoning is heard, the porch railing
## parts and a bridge of walkable light runs off the terrace toward the
## inner city's spires — the pilgrim way to the temple. Origin sits at the
## railing gap at deck level; the span extends along local -Z ("rot" in the
## area spec aims it at the city). The far end is barred by an unseen hand
## until the temple gate is raised.

var length := 90.0
var width := 5.2
var far_beacon := true

func _ready() -> void:
	_deck()
	_collision()
	_rails()
	_motes()
	if far_beacon:
		_beacon()
		_lightfall_door()

## Two planes make the glow: a soft wide wash and a brighter core strip that
## breathes. Additive, unshaded, shadowless — light, not masonry.
var _core: MeshInstance3D = null
var _pulse := 0.0

func _deck() -> void:
	# the body of the span: a translucent pale-gold ribbon (normal blend, so
	# grazing views don't integrate to a white sheet)...
	var wash := MeshInstance3D.new()
	var wm := BoxMesh.new()
	wm.size = Vector3(width, 0.1, length)
	wash.mesh = wm
	var wmat := _glow_mat(Color(0.86, 0.72, 0.42), 0.30)
	wmat.blend_mode = BaseMaterial3D.BLEND_MODE_MIX
	wash.material_override = wmat
	wash.position = Vector3(0, -0.07, -length * 0.5)
	wash.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(wash)
	# ...with a breathing additive core down its centre line...
	_core = MeshInstance3D.new()
	var cm := BoxMesh.new()
	cm.size = Vector3(width * 0.34, 0.06, length)
	_core.mesh = cm
	_core.material_override = _glow_mat(Color(1.0, 0.9, 0.62), 0.3)
	_core.position = Vector3(0, -0.03, -length * 0.5)
	_core.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(_core)
	# ...and bright running edges so the span reads at distance
	for sx in [-1.0, 1.0]:
		var edge := MeshInstance3D.new()
		var em := BoxMesh.new()
		em.size = Vector3(0.16, 0.14, length)
		edge.mesh = em
		edge.material_override = _glow_mat(Color(1.0, 0.9, 0.62), 0.55)
		edge.position = Vector3(sx * (width * 0.5 - 0.08), 0.0, -length * 0.5)
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
	var body := StaticBody3D.new()
	body.collision_layer = 1 << (VG.L_WORLD_BASE - 1)
	var cs := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = Vector3(width, 0.3, length)
	cs.shape = box
	cs.position = Vector3(0, -0.15, -length * 0.5)   # deck top flush with origin
	body.add_child(cs)
	add_child(body)
	# the far end refuses, quietly, until the temple gate stands
	var wall := StaticBody3D.new()
	wall.collision_layer = 1 << (VG.L_WORLD_BASE - 1)
	var wcs := CollisionShape3D.new()
	var wbox := BoxShape3D.new()
	wbox.size = Vector3(width + 1.0, 4.0, 0.4)
	wcs.shape = wbox
	wcs.position = Vector3(0, 2.0, -length + 0.6)
	wall.add_child(wcs)
	add_child(wall)

## Low walls of standing light along both edges: the road holds its own.
func _rails() -> void:
	for sx in [-1.0, 1.0]:
		var glow := MeshInstance3D.new()
		var gm := BoxMesh.new()
		gm.size = Vector3(0.1, 0.85, length)
		glow.mesh = gm
		glow.material_override = _glow_mat(Color(1.0, 0.9, 0.62), 0.22)
		glow.position = Vector3(sx * (width * 0.5 + 0.05), 0.42, -length * 0.5)
		glow.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		add_child(glow)
		var body := StaticBody3D.new()
		body.collision_layer = 1 << (VG.L_WORLD_BASE - 1)
		var cs := CollisionShape3D.new()
		var box := BoxShape3D.new()
		box.size = Vector3(0.3, 2.6, length)
		cs.shape = box
		cs.position = Vector3(sx * (width * 0.5 + 0.15), 1.3, -length * 0.5)
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
	add_child(door)
	door.position = Vector3(0, 0.0, -length + 2.4)

## Gold motes drift up off the span, sparse — the light is alive.
func _motes() -> void:
	var p := CPUParticles3D.new()
	p.amount = 110
	p.lifetime = 3.2
	p.emission_shape = CPUParticles3D.EMISSION_SHAPE_BOX
	p.emission_box_extents = Vector3(width * 0.5, 0.05, length * 0.5)
	p.direction = Vector3.UP
	p.spread = 12.0
	p.initial_velocity_min = 0.25
	p.initial_velocity_max = 0.7
	p.gravity = Vector3(0, 0.12, 0)
	p.scale_amount_min = 0.015
	p.scale_amount_max = 0.045
	p.color = Color(1.0, 0.88, 0.55, 0.8)
	p.position = Vector3(0, 0.1, -length * 0.5)
	add_child(p)
	p.emitting = true

## A soft standing shaft where the span meets the far dark: the promise of
## the gate to come.
func _beacon() -> void:
	var b := MeshInstance3D.new()
	var cm := CylinderMesh.new()
	cm.top_radius = 0.9
	cm.bottom_radius = 1.4
	cm.height = 14.0
	b.mesh = cm
	b.material_override = _glow_mat(Color(1.0, 0.9, 0.6), 0.16)
	b.position = Vector3(0, 7.0, -length + 0.4)
	b.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(b)

func _process(dt: float) -> void:
	_pulse += dt
	if _core != null:
		var k := 0.3 + 0.1 * sin(_pulse * 1.3) + 0.04 * sin(_pulse * 4.7)
		(_core.material_override as StandardMaterial3D).albedo_color.a = k
