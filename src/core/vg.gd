class_name VG

## Build tag shown in the HUD pose line — proves WHICH code a screenshot ran
const BUILD := "U47"

## Renderer discipline for MASS teardown: freeing a subtree that carries
## lights (worst: cull-masked key rigs like the gilded player's or the
## radiant crusader's) in the same frame as its geometry churns can hit
## Godot's cull-pairing SIGSEGV ("did not unpair geometries from light").
## Quench every light first, give the cull a frame, then free.
static func quench_lights(root: Node) -> void:
	if root == null or not is_instance_valid(root):
		return
	var stack: Array[Node] = [root]
	while not stack.is_empty():
		var n: Node = stack.pop_back()
		if n is Light3D:
			(n as Light3D).visible = false
		for c in n.get_children():
			stack.append(c)

## quench + a breath + queue_free, for whole areas/stages.
static func free_gently(node: Node) -> void:
	if node == null or not is_instance_valid(node):
		return
	quench_lights(node)
	node.get_tree().create_timer(0.06, false).timeout.connect(func():
		if is_instance_valid(node):
			node.queue_free())
## Global constants and enums for Vespergard.

enum WState { GLORY, RUIN }

const STATE_NAMES := { WState.GLORY: "glory", WState.RUIN: "ruin" }

static func state_from_name(n: String) -> WState:
	return WState.RUIN if n == "ruin" else WState.GLORY

## Physics layers (bit indices, 1-based as in project settings)
const L_WORLD_BASE := 1
const L_WORLD_GLORY := 2
const L_WORLD_RUIN := 3
const L_PLAYER := 4
const L_ENEMY := 5
const L_HURTBOX := 6
const L_INTERACT := 7
const L_CAMERA_CLIP := 8

## Masks
const M_WORLD_ALL := (1 << 0) | (1 << 1) | (1 << 2)  # base|glory|ruin
const M_WORLD_BASE_ONLY := 1 << 0

## Node groups
const GROUP_STATE_LISTENERS := "state_listeners"   # notified on world state change
const GROUP_ENEMIES := "enemies"
const GROUP_RESPAWN_ON_REST := "respawn_on_rest"
const GROUP_NAV_GLORY := "nav_glory"
const GROUP_NAV_RUIN := "nav_ruin"
