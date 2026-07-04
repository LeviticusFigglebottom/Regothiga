class_name NPC
extends Node3D
## A living soul of the glory state. Faces the Latecomer when near; talk
## opens dialogue with lore + services.

var npc_id := "aveline"
var cfg: Dictionary = {}

var _vis: Node3D

func _ready() -> void:
	cfg = DB.npc(npc_id)
	cfg["id"] = npc_id
	_vis = KitLib.instance(cfg.get("body", "char_aveline"))
	add_child(_vis)
	KitLib.add_flame_lights(_vis, 1.2, 3.0)
	var zone := Interactable.new()
	zone.prompt = "Speak with %s" % cfg.get("short_name", cfg.get("name", "?"))
	zone.setup_zone(1.8, 1.8)
	zone.activated.connect(_on_talk)
	add_child(zone)

func _physics_process(dt: float) -> void:
	var p = Game.player
	if p != null and global_position.distance_to(p.global_position) < 5.0:
		var to: Vector3 = p.global_position - global_position
		var ty := atan2(-to.x, -to.z)
		_vis.rotation.y = lerp_angle(_vis.rotation.y, ty, 1.0 - exp(-3.0 * dt))

func _on_talk(player) -> void:
	if player == null:
		return
	player.lock_control(true)
	player.velocity = Vector3.ZERO
	var ui := DialogueUI.new(cfg, self)
	get_tree().root.add_child(ui)
	AudioDirector.sfx("res://assets/audio/ui_tick.wav", -8.0)
