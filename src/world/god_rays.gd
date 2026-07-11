extends Node3D
## Streaming shafts of divine light. Thin parallel blades hung in the air,
## every one aligned to the area's sun, fading softly at both ends (a
## vertical alpha gradient — hard-edged bars read as scenery, not light),
## breathing slowly out of phase. Pure dressing — no collision, no shadows.
## Placed from an area's "scripted" section:
##   {"script": ".../god_rays.gd", "at": [x,y,z], "tag": "glory",
##    "params": {"count": 7, "span_x": 26, "span_z": 22, "sun": [-34, -40]}}

var count := 7
var span_x := 26.0
var span_z := 22.0
var seed_v := 7
var sun := [-34.0, -40.0]     # pitch/yaw of the light the blades stream from

var _blades: Array = []
var _t := 0.0

static func _fade_tex() -> GradientTexture2D:
	# bright waist, transparent ends — the shaft dissolves into the air
	var grad := Gradient.new()
	grad.set_color(0, Color(1, 1, 1, 0.0))
	grad.set_color(1, Color(1, 1, 1, 0.0))
	grad.add_point(0.28, Color(1, 1, 1, 1.0))
	grad.add_point(0.62, Color(1, 1, 1, 0.85))
	var gt := GradientTexture2D.new()
	gt.gradient = grad
	gt.fill_from = Vector2(0.5, 0.0)
	gt.fill_to = Vector2(0.5, 1.0)
	gt.width = 4
	gt.height = 128
	return gt

func _ready() -> void:
	var rng := RandomNumberGenerator.new()
	rng.seed = seed_v
	var sb := Basis.from_euler(Vector3(deg_to_rad(float(sun[0])), deg_to_rad(float(sun[1])), 0.0))
	var beam: Vector3 = (-sb.z).normalized()      # the direction the light travels
	var xb := beam.cross(Vector3.UP)
	if xb.length() < 0.3:
		xb = Vector3.RIGHT
	xb = xb.normalized()
	var zb := xb.cross(beam)
	var fade := _fade_tex()
	for i in count:
		var w := rng.randf_range(1.0, 2.8)
		var h := rng.randf_range(46.0, 64.0)
		var blade := MeshInstance3D.new()
		var qm := QuadMesh.new()
		qm.size = Vector2(w, h)
		blade.mesh = qm
		var m := StandardMaterial3D.new()
		m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
		m.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
		m.cull_mode = BaseMaterial3D.CULL_DISABLED
		m.albedo_color = Color(1.0, 0.94, 0.74, rng.randf_range(0.05, 0.09))
		m.albedo_texture = fade
		blade.material_override = m
		# quad faces +Z with height along Y: stand Y along the beam, keep all
		# blades in the same plane family so they stream parallel, never cross
		blade.basis = Basis(xb, beam, zb).rotated(beam, rng.randf_range(-0.06, 0.06))
		blade.position = Vector3(rng.randf_range(-span_x, span_x), 22.0,
				rng.randf_range(-span_z, span_z))
		blade.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		add_child(blade)
		_blades.append({"m": m, "a": m.albedo_color.a, "ph": rng.randf_range(0.0, TAU),
				"sp": rng.randf_range(0.1, 0.24)})
	# a thin drift of shining dust hanging in the beams
	var p := CPUParticles3D.new()
	p.amount = 90
	p.lifetime = 7.0
	p.emission_shape = CPUParticles3D.EMISSION_SHAPE_BOX
	p.emission_box_extents = Vector3(span_x, 9.0, span_z)
	p.direction = Vector3(0.2, -1, 0.1)
	p.spread = 30.0
	p.initial_velocity_min = 0.1
	p.initial_velocity_max = 0.4
	p.gravity = Vector3.ZERO
	p.scale_amount_min = 0.015
	p.scale_amount_max = 0.04
	p.color = Color(1.0, 0.92, 0.68, 0.75)
	p.position = Vector3(0, 9.0, 0)
	add_child(p)
	p.emitting = true

func _process(dt: float) -> void:
	_t += dt
	for b in _blades:
		var k: float = 0.65 + 0.35 * sin(_t * b["sp"] + b["ph"])
		(b["m"] as StandardMaterial3D).albedo_color.a = b["a"] * k
