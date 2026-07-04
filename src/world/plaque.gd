class_name LorePlaque
extends Node3D
## Engraved lore stands — the kingdom speaks in inscriptions.

var text := "..."

func _ready() -> void:
	add_child(KitLib.instance("plaque"))
	var zone := Interactable.new()
	zone.prompt = "Read"
	zone.setup_zone(1.3, 1.4)
	zone.activated.connect(func(_p): Game.lore_panel.emit(text))
	add_child(zone)
