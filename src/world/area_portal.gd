class_name AreaPortal
extends Node3D
## A doorway to another area of the kingdom. Optionally sealed behind a
## world flag (the tower door opens only when the warden rests).

var to_area := ""
var spawn_pos := Vector3.ZERO
var prompt := "Pass on"
var locked_flag := ""        # world flag that must be TRUE to pass
var locked_prompt := "Sealed"

var _zone: Interactable

func _ready() -> void:
	_zone = Interactable.new()
	_zone.prompt = prompt
	_zone.setup_zone(1.6, 2.2)
	_zone.activated.connect(_on_use)
	add_child(_zone)

func _unlocked() -> bool:
	if locked_flag == "":
		return true
	if locked_flag.begins_with("cleared:"):
		return World.is_cleared(locked_flag.get_slice(":", 1))
	return World.flag(locked_flag)

func _physics_process(_dt: float) -> void:
	if locked_flag != "":
		_zone.prompt = prompt if _unlocked() else locked_prompt

func _on_use(player) -> void:
	if not _unlocked():
		Game.toast.emit(locked_prompt + ".")
		return
	if to_area == "" or player == null:
		return
	Game.travel_to(to_area, spawn_pos)
