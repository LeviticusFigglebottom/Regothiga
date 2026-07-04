class_name Pickup
extends Node3D
## A waxlight cache: floating candle-flame over the item. Grants orisons
## and/or items once; persistence via area flag.

var pickup_id := ""
var area_id := ""
var orisons := 0
var item_id := ""
var item_count := 1
var label := "Take"

func _ready() -> void:
	if World.area_flag(area_id, "took_" + pickup_id):
		queue_free()
		return
	var zone := Interactable.new()
	zone.prompt = label
	zone.setup_zone(1.2, 1.4)
	zone.activated.connect(_on_take)
	add_child(zone)
	var candle := KitLib.instance("candelabra")
	candle.scale = Vector3(0.55, 0.55, 0.55)
	add_child(candle)
	KitLib.add_flame_lights(candle, 1.4, 3.5)

func _on_take(player) -> void:
	World.set_area_flag(area_id, "took_" + pickup_id)
	if orisons > 0:
		Game.add_orisons(orisons)
	if item_id != "" and player != null:
		player.inventory[item_id] = int(player.inventory.get(item_id, 0)) + item_count
	var it := DB.item(item_id)
	var what := []
	if orisons > 0:
		what.append("%d orisons" % orisons)
	if item_id != "":
		what.append("%s ×%d" % [it.get("name", item_id), item_count])
	Game.toast.emit("Received: " + " · ".join(what))
	AudioDirector.sfx("res://assets/audio/orison.wav", -4.0)
	World.save_game()
	queue_free()
