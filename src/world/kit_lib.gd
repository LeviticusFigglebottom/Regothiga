class_name KitLib
## Instantiates gothic kit pieces (assets/kit/*.glb) with materials remapped
## to the shared MaterialLib families, and optional static trimesh collision.

static var _manifest: Dictionary = {}
static var _scene_cache: Dictionary = {}

static func manifest() -> Dictionary:
	if _manifest.is_empty():
		var f := FileAccess.open("res://assets/kit/manifest.json", FileAccess.READ)
		if f:
			_manifest = JSON.parse_string(f.get_as_text())
	return _manifest

static func has_piece(id: String) -> bool:
	return manifest().has(id)

## state_mode: 0 base / 1 glory-only / 2 ruin-only (drives dissolve behavior)
static func instance(id: String, state_mode := 0, mat_remap: Dictionary = {}) -> Node3D:
	var entry: Dictionary = manifest().get(id, {})
	if entry.is_empty():
		push_error("KitLib: unknown piece '%s'" % id)
		return Node3D.new()
	var path: String = "res://" + entry["file"]
	var scene: PackedScene = _scene_cache.get(path)
	if scene == null:
		scene = load(path)
		_scene_cache[path] = scene
	var node := scene.instantiate() as Node3D
	remap_materials(node, state_mode, mat_remap)
	node.set_meta("kit_id", id)
	node.set_meta("state_mode", state_mode)
	return node

static func remap_materials(node: Node, state_mode := 0, mat_remap: Dictionary = {}) -> void:
	for mi in _mesh_instances(node):
		var mesh := mi.mesh
		if mesh == null:
			continue
		for s in mesh.get_surface_count():
			var src := mesh.surface_get_material(s)
			var fam := "M_stone"
			if src != null and src.resource_name != "":
				fam = src.resource_name
			# glTF import may suffix duplicated materials ("M_stone.001")
			fam = fam.get_slice(".", 0)
			if mat_remap.has(fam):
				fam = String(mat_remap[fam])
			mi.set_surface_override_material(s, MaterialLib.get_mat(fam, state_mode))
			if fam == "M_flame":
				var aabb := mesh.get_aabb()
				mi.set_instance_shader_parameter("flame_base_y", aabb.position.y)
				mi.set_instance_shader_parameter("flame_height", maxf(aabb.size.y, 0.05))
				mi.set_instance_shader_parameter("flame_tint", Vector3(1.0, 0.76, 0.32))
				mi.set_instance_shader_parameter("flame_energy", 3.6)

static func _mesh_instances(node: Node) -> Array[MeshInstance3D]:
	var out: Array[MeshInstance3D] = []
	var stack: Array[Node] = [node]
	while not stack.is_empty():
		var n: Node = stack.pop_back()
		if n is MeshInstance3D:
			out.append(n)
		for c in n.get_children():
			stack.append(c)
	return out

## Attach a consolidated OmniLight3D per flame-bearing prop so multi-candle
## pieces (candelabras, votive stands, candle clusters, altars) don't stack 3-5
## overlapping dynamic lights onto the same wax & floor surfaces.
static func add_flame_lights(piece: Node3D, energy := 2.15, range_m := 7.6,
		color := Color(1.0, 0.68, 0.32)) -> Array[OmniLight3D]:
	var lights: Array[OmniLight3D] = []
	var flame_meshes: Array[MeshInstance3D] = []
	for mi in _mesh_instances(piece):
		if String(mi.name).to_lower().contains("flame"):
			flame_meshes.append(mi)
	if flame_meshes.is_empty():
		return lights
	# Compute average flame tip position in piece-local space
	var avg_pos := Vector3.ZERO
	for mi in flame_meshes:
		var aabb := mi.get_aabb()
		var tip_local := aabb.position + Vector3(aabb.size.x * 0.5, aabb.size.y * 0.85, aabb.size.z * 0.5)
		avg_pos += mi.transform * tip_local
	avg_pos /= float(flame_meshes.size())
	var count_boost := 1.0 + minf(float(flame_meshes.size() - 1) * 0.18, 0.54)
	var dy := 0.08
	if avg_pos.y < 0.55:
		count_boost = 0.52
		range_m = minf(range_m, 4.8)
		dy = 0.24
	var l := OmniLight3D.new()
	# the light breathes like the flame it serves
	l.set_script(load("res://src/world/flame_flicker.gd"))
	l.light_color = color
	l.light_energy = energy * count_boost
	l.omni_range = range_m
	l.omni_attenuation = 1.45
	l.shadow_enabled = false
	l.distance_fade_enabled = true
	l.distance_fade_begin = 28.0
	l.distance_fade_length = 10.0
	l.position = avg_pos + Vector3(0, dy, 0)
	piece.add_child(l)
	lights.append(l)
	return lights

## Wrap a piece's meshes in a StaticBody3D collider.
## Collision shapes are cached per (piece, mesh, mode) — cheap to instance many.
##
## convex=false → trimesh: an exact, hollow shell. Correct for ARCHITECTURE
##   with holes you must pass through (arcades, portals, windows, walls).
## convex=true  → convex hull: a SOLID blocker. Correct for freestanding
##   props (statues, urns, columns, sarcophagi…) — the player capsule can
##   never wedge inside a concave shell, so nothing traps you.
static var _shape_cache: Dictionary = {}

static func add_collision(piece: Node3D, layer_bit: int, convex := false) -> void:
	var kit_id := str(piece.get_meta("kit_id", "?"))
	for mi in _mesh_instances(piece):
		if mi.mesh == null:
			continue
		if not convex and kit_id.begins_with("burg_wall_") and str(mi.name) == "timbers":
			continue
		if not convex and str(mi.name) == "palace_floor_inlay":
			continue
		var key := kit_id + "/" + str(mi.name) + ("/cvx" if convex else "")
		var shape: Shape3D = _shape_cache.get(key)
		if shape == null:
			shape = mi.mesh.create_convex_shape() if convex else mi.mesh.create_trimesh_shape()
			_shape_cache[key] = shape
		var body := StaticBody3D.new()
		body.collision_layer = 1 << (layer_bit - 1)
		body.collision_mask = 0
		var cs := CollisionShape3D.new()
		cs.shape = shape
		body.add_child(cs)
		mi.add_child(body)
