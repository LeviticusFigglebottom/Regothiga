class_name SwingTrail
extends MeshInstance3D
## The swoosh: while visible, the blade's base and tip are sampled every
## frame and stitched into a short-lived ribbon — the actual arc the swing
## swept, fading along its length — instead of a glowing card glued to the
## weapon (which is what the old static quad amounted to).

const LIFE := 0.14          # seconds of arc kept behind the blade
const BASE_UP := 0.12       # sample points along the blade (+Y from grip)
const TIP_UP := 1.05

var target: Node3D          # the weapon mount; kit blades run +Y from it
var _pts: Array = []        # newest-first: {b: Vector3, t: Vector3, at: float}
var _clock := 0.0
var _was_visible := false

func _init() -> void:
	top_level = true        # ribbon lives in world space, not on the hand
	mesh = ImmediateMesh.new()
	var m := ShaderMaterial.new()
	m.shader = load("res://shaders/trail.gdshader")
	material_override = m
	cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	visible = false

func _process(dt: float) -> void:
	_clock += dt
	if visible and not _was_visible:
		_pts.clear()        # a fresh swing sweeps a fresh arc
	_was_visible = visible
	if not visible:
		return
	global_transform = Transform3D.IDENTITY
	if target != null and is_instance_valid(target):
		var xf := target.global_transform
		_pts.push_front({"b": xf * Vector3(0, BASE_UP, 0),
				"t": xf * Vector3(0, TIP_UP, 0), "at": _clock})
	while _pts.size() > 2 and _clock - float(_pts[_pts.size() - 1]["at"]) > LIFE:
		_pts.pop_back()
	_rebuild()

func _rebuild() -> void:
	var im := mesh as ImmediateMesh
	im.clear_surfaces()
	if _pts.size() < 2:
		return
	im.surface_begin(Mesh.PRIMITIVE_TRIANGLE_STRIP)
	for i in _pts.size():
		var k := float(i) / float(_pts.size() - 1)   # 0 at the blade, 1 at the tail
		im.surface_set_uv(Vector2(k, 0.0))
		im.surface_add_vertex(_pts[i]["b"])
		im.surface_set_uv(Vector2(k, 1.0))
		im.surface_add_vertex(_pts[i]["t"])
	im.surface_end()
