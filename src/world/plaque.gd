class_name LorePlaque
extends Node3D
## Engraved lore stands — the kingdom speaks in inscriptions.

var text := "..."
var set_flag := ""      # a read that MEANS something: swearing the amend
var flag_toast := ""

func _ready() -> void:
	add_child(KitLib.instance("plaque"))
	var zone := Interactable.new()
	zone.prompt = "Read"
	zone.setup_zone(1.3, 1.4)
	zone.activated.connect(func(_p):
		Game.lore_panel.emit(text)
		if set_flag != "" and not World.flag(set_flag):
			World.set_flag(set_flag)
			World.save_game()
			if flag_toast != "":
				Game.toast.emit(flag_toast)
			AudioDirector.sfx("res://assets/audio/swell_kindle.wav", -8.0, 0.9))
	add_child(zone)
