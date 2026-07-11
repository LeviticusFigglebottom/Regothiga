extends Node3D
## Streaming shafts of divine light: additive blades hung in the air, all
## aligned to the area's sun, breathing slowly out of phase. Pure dressing —
## no collision, no shadows. Placed from an area's "scripted" section:
##   {"script": ".../god_rays.gd", "at": [x,y,z], "tag": "glory",
##    "params": {"count": 9, "span_x": 30, "span_z": 24, "sun": [-34, -40]}}

var count := 8
var span_x := 30.0
var span_z := 22.0
var seed_v := 7
var sun := [-34.0, -40.0]     # pitch/yaw of the light the blades stream from

var _blades: Array = []
var _t := 0.0

func _ready() -> void:
	var rng := RandomNumberGenerator.new()
	rng.seed = seed_v
	var sb := Basis.from_euler(Vector3(deg_to_rad(float(sun[0])), deg_to_rad(float(sun[1])), 0.0))
	var beam: Vector3 = -sb.z            # the direction the light travels
	for i in count:
		var yb := beam.normalized()
		var xb := yb.cross(Vector3.UP)
		if xb.length() < 0.3:
			xb = Vector3.RIGHT
		xb = xb.normalized()
		var zb := xb.cross(yb)
		var w := rng.randf_range(1.6, 4.6)
		var h := rng.randf_range(42.0, 60.0)
		var blade := MeshInstance3D.new()
		var bm := BoxMesh.new()
		bm.size = Vector3(w, h, 0.1)
		blade.mesh = bm
		var m := StandardMaterial3D.new()
		m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
		m.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
		m.cull_mode = BaseMaterial3D.CULL_DISABLED
		m.albedo_color = Color(1.0, 0.93, 0.72, rng.randf_range(0.045, 0.1))
		blade.material_override = m
		blade.basis = Basis(xb, yb, zb).rotated(yb, rng.randf_range(-0.5, 0.5))
		blade.position = Vector3(rng.randf_range(-span_x, span_x), 22.0,
				rng.randf_range(-span_z, span_z))
		blade.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		add_child(blade)
		_blades.append({"m": m, "a": m.albedo_color.a, "ph": rng.randf_range(0.0, TAU),
				"sp": rng.randf_range(0.12, 0.3)})
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
		var k: float = 0.7 + 0.3 * sin(_t * b["sp"] + b["ph"])
		(b["m"] as StandardMaterial3D).albedo_color.a = b["a"] * k
