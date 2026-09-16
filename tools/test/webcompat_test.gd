extends TestBase
## Guards the two things the browser build depends on that nothing else
## exercises: per-mesh shader values that do NOT go through instance uniforms,
## and the volumetric-fog fallback.
##
## Instance uniforms are what this replaced. The Compatibility backend the web
## build runs on spends 16 of its 4096 global-parameter slots on every instance
## whose shader declares one — about 256 kingdom-wide, where one area builds
## ~1400 — so the meshes that genuinely vary were the ones that lost their
## value. Re-adding `instance uniform` to a shared shader would bring that
## back silently on the desktop build; these checks fail instead.

func _ready() -> void:
	_run.call_deferred()

## A real declaration, not the word in a comment explaining its absence.
func _declares_instance_uniform(shader: Shader) -> bool:
	for line in shader.code.split("\n"):
		var t := line.strip_edges()
		if t.begins_with("//"):
			continue
		if t.begins_with("instance uniform"):
			return true
	return false

func _mesh(family: String) -> MeshInstance3D:
	var mi := MeshInstance3D.new()
	mi.mesh = BoxMesh.new()
	mi.set_surface_override_material(0, MaterialLib.get_mat(family))
	add_child(mi)
	return mi

func _run() -> void:
	print("== no shared shader declares an instance uniform")
	for path in ["res://shaders/gothic.gdshader", "res://shaders/gothic_ds.gdshader",
			"res://shaders/flame.gdshader", "res://shaders/glass.gdshader",
			"res://shaders/water.gdshader"]:
		check(not _declares_instance_uniform(load(path) as Shader),
			"%s has no instance uniform" % path.get_file())

	print("== a written mesh differs; its family does not")
	var shared := MaterialLib.get_mat("M_stone") as ShaderMaterial
	var a := _mesh("M_stone")
	var b := _mesh("M_stone")
	check(a.get_active_material(0) == shared, "meshes share the family material by default")

	MaterialLib.set_mesh_param(a, "death_diss", 0.75)
	var a_mat := a.get_active_material(0) as ShaderMaterial
	check(a_mat != shared, "a written mesh gets its own material")
	check(is_equal_approx(a_mat.get_shader_parameter("death_diss"), 0.75), "the value lands on it")
	check(shared.get_shader_parameter("death_diss") == null
			or is_equal_approx(shared.get_shader_parameter("death_diss"), 0.0),
		"the shared family material is untouched")
	check(b.get_active_material(0) == shared, "its neighbours keep sharing")

	print("== repeated writes reuse the one copy")
	MaterialLib.set_mesh_param(a, "death_diss", 0.25)
	check(a.get_active_material(0) == a_mat, "no second copy on the next write")
	check(is_equal_approx(a_mat.get_shader_parameter("death_diss"), 0.25), "the new value lands")

	print("== a dying enemy dissolves")
	# The path that actually matters: enemy fade-out walks its whole visual.
	var vis := Node3D.new()
	add_child(vis)
	var limb := MeshInstance3D.new()
	limb.mesh = BoxMesh.new()
	limb.set_surface_override_material(0, MaterialLib.get_mat("M_robe"))
	vis.add_child(limb)
	MaterialLib.set_mesh_param(vis, "death_diss", 1.0)
	var limb_mat := limb.get_active_material(0) as ShaderMaterial
	check(limb_mat != MaterialLib.get_mat("M_robe"), "a limb under the visual root is reached")
	check(is_equal_approx(limb_mat.get_shader_parameter("death_diss"), 1.0), "and dissolves fully")

	print("== the fog fallback follows the backend")
	var rig := EnvRig.new()
	add_child(rig)
	await ticks(2)
	var env := rig.world_env.environment
	rig.blend(1.0)   # ruin: the thickest air the kingdom has
	if rig.volumetric:
		check(env.volumetric_fog_enabled, "Forward+ keeps volumetric fog")
		check(env.fog_density < 0.01, "and leaves the depth fog thin")
	else:
		check(not env.volumetric_fog_enabled, "Compatibility turns volumetric fog off")
		check(env.fog_density > 0.0035,
			"and thickens the depth fog to stand in for it (%f)" % env.fog_density)

	finish()
