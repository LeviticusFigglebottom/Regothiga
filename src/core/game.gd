extends Node
## Game — run orchestrator: knows the player, the current area, and drives
## high-level flows (death, respawn, vigils). Scene-facing counterpart to World.

signal orisons_changed(amount: int)
signal player_registered(player)

var player: Node = null
var current_area: Node = null
var current_area_id := ""

var orisons := 0

func register_player(p: Node) -> void:
	player = p
	player_registered.emit(p)

func register_area(area: Node, id: String) -> void:
	current_area = area
	current_area_id = id

func add_orisons(n: int) -> void:
	orisons = max(0, orisons + n)
	orisons_changed.emit(orisons)

func set_orisons(n: int) -> void:
	orisons = max(0, n)
	orisons_changed.emit(orisons)

func area_state() -> VG.WState:
	return World.get_area_state(current_area_id)
