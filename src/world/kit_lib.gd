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
static func instance(id: String, state_mode := 0) -> Node3D:
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
	remap_materials(node, state_mode)
	node.set_meta("kit_id", id)
	return node

static func remap_materials(node: Node, state_mode := 0) -> void:
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
			mi.set_surface_override_material(s, MaterialLib.get_mat(fam, state_mode))

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

## Wrap a piece's meshes in a StaticBody3D with trimesh collision.
## Collision shapes are cached per (piece, mesh) — cheap to instance many.
static var _shape_cache: Dictionary = {}

static func add_collision(piece: Node3D, layer_bit: int) -> void:
	for mi in _mesh_instances(piece):
		if mi.mesh == null:
			continue
		var key := str(piece.get_meta("kit_id", "?")) + "/" + str(mi.name)
		var shape: Shape3D = _shape_cache.get(key)
		if shape == null:
			shape = mi.mesh.create_trimesh_shape()
			_shape_cache[key] = shape
		var body := StaticBody3D.new()
		body.collision_layer = 1 << (layer_bit - 1)
		body.collision_mask = 0
		var cs := CollisionShape3D.new()
		cs.shape = shape
		body.add_child(cs)
		mi.add_child(body)
