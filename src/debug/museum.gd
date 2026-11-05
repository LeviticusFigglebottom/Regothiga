extends Node3D
## Museum sandbox: lays out every kit piece on a grid for visual inspection.
## Run: godot --path . -- --sandbox=museum --shot=docs/museum.png

const MEGA_KITS := {
	"city_panorama": true,
	"canal_vault_8m": true,
	"canal_vault_8m_win": true,
	"cathedral_mass": true,
	"radiant_castle_a": true,
	"radiant_castle_b": true,
	"radiant_spire_a": true,
	"radiant_spire_b": true,
	"spire_tower_a": true,
	"spire_tower_b": true,
	"spire_tower_c": true,
	"cloud_bank_a": true,
	"cloud_bank_b": true,
	"cloud_bank_c": true,
	"palace_dome_12m": true,
	"palace_cove_dome": true,
	"buttress_arc": true,
	"city_cluster_a": true,
	"city_cluster_b": true,
	"clock_tower": true,
}

func _ready() -> void:
	RenderingServer.global_shader_parameter_set("vg_state_blend", 0.0)
	RenderingServer.global_shader_parameter_set("vg_wave_r", -1000.0)
	var all_ids := KitLib.manifest().keys()
	all_ids.sort()
	var std_ids: Array = []
	var mega_ids: Array = []
	for id in all_ids:
		if MEGA_KITS.has(id):
			mega_ids.append(id)
		else:
			std_ids.append(id)

	var cols := 6
	var spacing := 6.0
	for i in std_ids.size():
		var id: String = std_ids[i]
		var piece := KitLib.instance(id)
		add_child(piece)
		var cx := float(i % cols) * spacing
		var cz := floorf(float(i) / float(cols)) * spacing
		piece.position = Vector3(cx, 0, cz)
		var lbl := Label3D.new()
		lbl.text = "%d: %s" % [i, id]
		lbl.font_size = 28
		lbl.pixel_size = 0.0045
		lbl.modulate = Color(0.96, 0.88, 0.68)
		lbl.outline_size = 8
		lbl.outline_modulate = Color(0.05, 0.05, 0.06)
		lbl.billboard = BaseMaterial3D.BILLBOARD_ENABLED
		lbl.position = Vector3(cx, 0.32, cz + 1.85)
		add_child(lbl)

	# Place mega-scale skyline / vault shells on a distant exhibition line at z = -45
	for j in mega_ids.size():
		var id: String = mega_ids[j]
		if id == "city_panorama":
			continue
		var piece := KitLib.instance(id)
		add_child(piece)
		piece.position = Vector3(float(j - mega_ids.size() * 0.5) * 24.0 + 15.0, 0.0, -45.0)

	# Full stone exhibition floor spanning all rows
	var ground := MeshInstance3D.new()
	var pm := PlaneMesh.new()
	pm.size = Vector2(96, 240)
	ground.mesh = pm
	ground.position = Vector3(15, -0.02, 84)
	ground.set_surface_override_material(0, MaterialLib.get_mat("M_stone_dark"))
	add_child(ground)

	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-42, -32, 0)
	sun.light_color = Color(1.0, 0.89, 0.74)
	sun.light_energy = 1.65
	sun.shadow_enabled = true
	add_child(sun)

	var fill := DirectionalLight3D.new()
	fill.rotation_degrees = Vector3(-55, 145, 0)
	fill.light_color = Color(0.72, 0.78, 0.90)
	fill.light_energy = 0.48
	fill.shadow_enabled = false
	add_child(fill)

	var env := WorldEnvironment.new()
	var e := Environment.new()
	e.background_mode = Environment.BG_COLOR
	e.background_color = Color(0.22, 0.24, 0.30)
	e.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	e.ambient_light_color = Color(0.54, 0.56, 0.64)
	e.ambient_light_energy = 0.68
	e.tonemap_mode = Environment.TONE_MAPPER_ACES
	e.tonemap_white = 6.0
	env.environment = e
	add_child(env)

	var cam := Camera3D.new()
	cam.position = Vector3(15.0, 9.5, 24.0)
	cam.rotation_degrees = Vector3(-28.0, 0.0, 0.0)
	cam.fov = 62.0
	cam.current = true
	add_child(cam)
