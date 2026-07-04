class_name Area
extends Node3D
## One region of the kingdom in both of its lives. Owns the Base geometry and
## the Glory/Ruin layers, both navmeshes, the env rig, lanterns and gates.
## AreaBuilder assembles these from data; sandboxes build them by hand.
## StateDirector drives apply_state(); nothing else touches layers directly.

var area_id := "area"
var display_name := "Somewhere"

var base: Node3D
var glory_layer: Node3D
var ruin_layer: Node3D
var env: EnvRig
var nav_glory: NavigationRegion3D
var nav_ruin: NavigationRegion3D

var _applied: int = -1

func _init() -> void:
	add_to_group("nav_src")   # navmesh bakes parse this subtree
	base = Node3D.new(); base.name = "Base"; add_child(base)
	glory_layer = Node3D.new(); glory_layer.name = "GloryLayer"; add_child(glory_layer)
	ruin_layer = Node3D.new(); ruin_layer.name = "RuinLayer"; add_child(ruin_layer)
	env = EnvRig.new(); env.name = "Env"; add_child(env)

func state() -> VG.WState:
	return World.get_area_state(area_id)

## Attach a kit piece (or any node) to a layer. state_tag: "base"|"glory"|"ruin"
func attach(node: Node3D, state_tag := "base") -> void:
	match state_tag:
		"glory": glory_layer.add_child(node)
		"ruin": ruin_layer.add_child(node)
		_: base.add_child(node)

## Hard-apply a state: layer visibility, collision, nav swap, env snap.
## The transformation wave calls this at its END; loads call it directly.
func apply_state(s: VG.WState) -> void:
	_applied = s
	var ruin_on := s == VG.WState.RUIN
	_set_layer_active(glory_layer, not ruin_on)
	_set_layer_active(ruin_layer, ruin_on)
	if nav_glory != null:
		nav_glory.enabled = not ruin_on
	if nav_ruin != null:
		nav_ruin.enabled = ruin_on
	env.snap(s)
	# state-aware entities (lantern flames, doors, spawners) react themselves
	get_tree().call_group(VG.GROUP_STATE_LISTENERS, "on_world_state", area_id, s)

## During the wave both layers are visible (shader dissolve owns pixel
## presence); collision swaps immediately to the target so routes change.
func pre_transition(target: VG.WState) -> void:
	glory_layer.visible = true
	ruin_layer.visible = true
	_set_layer_collision(glory_layer, target != VG.WState.RUIN)
	_set_layer_collision(ruin_layer, target == VG.WState.RUIN)

func _set_layer_active(layer: Node3D, on: bool) -> void:
	layer.visible = on
	_set_layer_collision(layer, on)
	layer.process_mode = Node.PROCESS_MODE_INHERIT if on else Node.PROCESS_MODE_DISABLED

func _set_layer_collision(layer: Node3D, on: bool) -> void:
	var stack: Array[Node] = [layer]
	while not stack.is_empty():
		var n: Node = stack.pop_back()
		if n is CollisionObject3D:
			var co := n as CollisionObject3D
			if not co.has_meta("orig_layer"):
				co.set_meta("orig_layer", co.collision_layer)
			co.collision_layer = int(co.get_meta("orig_layer")) if on else 0
		for c in n.get_children():
			stack.append(c)

## Ambient particle beds per state (motes / ashfall).
func add_ambient(mn: Vector3, mx: Vector3) -> void:
	var center := (mn + mx) * 0.5
	var size := mx - mn
	var motes := _ambient_emitter(size, Color(1.0, 0.85, 0.55, 0.5), 0.2, Vector3(0.12, 0.05, 0.0), 130)
	motes.position = center + Vector3(0, 2.2, 0)
	glory_layer.add_child(motes)
	var ash := _ambient_emitter(size, Color(0.62, 0.66, 0.75, 0.6), 0.3, Vector3(0.25, -0.5, 0.1), 200)
	ash.position = center + Vector3(0, 4.0, 0)
	ruin_layer.add_child(ash)

func _ambient_emitter(size: Vector3, color: Color, scale_max: float, drift: Vector3, amount: int) -> CPUParticles3D:
	var p := CPUParticles3D.new()
	p.amount = amount
	p.lifetime = 9.0
	p.preprocess = 9.0
	p.emission_shape = CPUParticles3D.EMISSION_SHAPE_BOX
	p.emission_box_extents = Vector3(size.x * 0.5, 3.2, size.z * 0.5)
	p.direction = drift.normalized() if drift.length() > 0.01 else Vector3.DOWN
	p.spread = 25.0
	p.initial_velocity_min = drift.length() * 0.5
	p.initial_velocity_max = drift.length() * 1.4
	p.gravity = Vector3.ZERO
	p.scale_amount_min = 0.012
	p.scale_amount_max = 0.028 * (1.0 + scale_max)
	var quad := QuadMesh.new()
	quad.size = Vector2(0.6, 0.6)
	var mat := StandardMaterial3D.new()
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mat.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	mat.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED
	var grad := Gradient.new()
	grad.set_color(0, Color(color, 1.0))
	grad.set_color(1, Color(color, 0.0))
	var gt := GradientTexture2D.new()
	gt.gradient = grad
	gt.fill = GradientTexture2D.FILL_RADIAL
	gt.fill_from = Vector2(0.5, 0.5)
	gt.fill_to = Vector2(0.5, 0.0)
	gt.width = 32
	gt.height = 32
	mat.albedo_texture = gt
	quad.material = mat
	p.mesh = quad
	return p

## Bake both navmeshes from the current geometry (on load, and again when
## base routes change — an opened gate, cleared rubble).
func bake_navmeshes() -> void:
	if nav_glory != null:
		nav_glory.queue_free()
	if nav_ruin != null:
		nav_ruin.queue_free()
	nav_glory = _bake_nav("NavGlory", false)
	nav_ruin = _bake_nav("NavRuin", true)
	if _applied >= 0:
		nav_glory.enabled = _applied != VG.WState.RUIN
		nav_ruin.enabled = _applied == VG.WState.RUIN
		_set_layer_collision(glory_layer, _applied != VG.WState.RUIN)
		_set_layer_collision(ruin_layer, _applied == VG.WState.RUIN)

func _bake_nav(name_: String, ruin_world: bool) -> NavigationRegion3D:
	var region := NavigationRegion3D.new()
	region.name = name_
	add_child(region)
	var mesh := NavigationMesh.new()
	mesh.agent_radius = 0.4
	mesh.agent_height = 1.8
	mesh.agent_max_climb = 0.42
	mesh.cell_size = 0.22
	mesh.cell_height = 0.2
	mesh.geometry_parsed_geometry_type = NavigationMesh.PARSED_GEOMETRY_STATIC_COLLIDERS
	mesh.geometry_source_geometry_mode = NavigationMesh.SOURCE_GEOMETRY_GROUPS_WITH_CHILDREN
	mesh.geometry_source_group_name = "nav_src"
	mesh.geometry_collision_mask = (1 << (VG.L_WORLD_BASE - 1)) \
		| (1 << ((VG.L_WORLD_RUIN if ruin_world else VG.L_WORLD_GLORY) - 1))
	region.navigation_mesh = mesh
	# make sure every layer's colliders carry their true layer bits for the
	# mask filter (they may have been zeroed by a previous apply_state)
	_set_layer_collision(glory_layer, true)
	_set_layer_collision(ruin_layer, true)
	region.bake_navigation_mesh(false)   # synchronous on load
	region.enabled = false
	return region
