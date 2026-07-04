class_name VigilLantern
extends Node3D
## THE rest site and world-toggle. Keeping vigil here heals, respawns the
## dead, anchors the Latecomer's return — and turns the world over between
## its glory and its ruin. (DECISIONS D-008/D-009)

@export var lantern_id := "lantern"
@export var display_name := "Vigil Lantern"

var area: Area = null
var zone: Interactable
var _flame: GeometryInstance3D = null

var _light: OmniLight3D = null

func _ready() -> void:
	add_to_group(VG.GROUP_STATE_LISTENERS)
	add_to_group("lanterns")
	var vis := KitLib.instance("vigil_lantern")
	add_child(vis)
	_flame = _find_flame(vis)
	var lights := KitLib.add_flame_lights(vis, 2.6, 7.0)
	if lights.size() > 0:
		_light = lights[0]
	zone = Interactable.new()
	zone.prompt = "Keep vigil"
	zone.setup_zone(1.9, 1.8)
	zone.activated.connect(_on_activated)
	add_child(zone)
	_tint_for(World.get_area_state(_area_id()))

func _area_id() -> String:
	return area.area_id if area != null else Game.current_area_id

func _find_flame(root: Node) -> GeometryInstance3D:
	var stack: Array[Node] = [root]
	while not stack.is_empty():
		var n: Node = stack.pop_back()
		if n is GeometryInstance3D and String(n.name).contains("vigil_flame"):
			return n
		for c in n.get_children():
			stack.append(c)
	return null

func _on_activated(player) -> void:
	Game.vigil_flow(self, player)

func on_world_state(area_id: String, s: VG.WState) -> void:
	if area_id == _area_id():
		_tint_for(s)

func _tint_for(s: VG.WState) -> void:
	if _flame == null:
		return
	if s == VG.WState.RUIN:
		_flame.set_instance_shader_parameter("flame_tint", Vector3(0.45, 0.65, 1.0))
		_flame.set_instance_shader_parameter("flame_energy", 2.4)
		if _light:
			_light.light_color = Color(0.5, 0.68, 1.0)
			_light.light_energy = 2.0
	else:
		_flame.set_instance_shader_parameter("flame_tint", Vector3(1.0, 0.72, 0.30))
		_flame.set_instance_shader_parameter("flame_energy", 3.4)
		if _light:
			_light.light_color = Color(1.0, 0.72, 0.38)
			_light.light_energy = 2.6

func respawn_point() -> Vector3:
	return global_position + global_transform.basis.z * 1.4
