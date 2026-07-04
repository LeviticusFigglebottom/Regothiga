extends Node3D
## Museum sandbox: lays out every kit piece on a grid for visual inspection.
## Run: godot --path . -- --sandbox=museum --shot=docs/museum.png

func _ready() -> void:
	var ids := KitLib.manifest().keys()
	ids.sort()
	var cols := 6
	var spacing := 6.0
	for i in ids.size():
		var piece := KitLib.instance(ids[i])
		add_child(piece)
		var cx := float(i % cols) * spacing
		var cz := floorf(float(i) / float(cols)) * spacing
		piece.position = Vector3(cx, 0, cz)
	# ground
	var ground := MeshInstance3D.new()
	var pm := PlaneMesh.new()
	pm.size = Vector2(80, 80)
	ground.mesh = pm
	ground.position = Vector3(15, -0.26, 12)
	ground.set_surface_override_material(0, MaterialLib.get_mat("M_stone_dark"))
	add_child(ground)

	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-38, -35, 0)
	sun.light_color = Color(1.0, 0.87, 0.7)
	sun.light_energy = 1.6
	sun.shadow_enabled = true
	add_child(sun)

	var env := WorldEnvironment.new()
	var e := Environment.new()
	e.background_mode = Environment.BG_COLOR
	e.background_color = Color(0.35, 0.38, 0.45)
	e.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	e.ambient_light_color = Color(0.5, 0.52, 0.6)
	e.ambient_light_energy = 0.7
	e.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	env.environment = e
	add_child(env)
