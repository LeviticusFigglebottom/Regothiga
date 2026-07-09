class_name WordStone
extends Node3D
## A graven wayside stone holding one of the parish's lost words. Reading
## it sets the word's flag; when every word in the group is known, the
## group flag comes true and the Parish of the First Wick unbars its door.

var word := "WAX"
var flag := "word_wax"
var line := ""
var all_of: Array = []          # flags of the whole word group
var sets := ""                  # group flag raised once all are known

func setup(spec: Dictionary) -> void:
	word = spec.get("word", "WAX")
	flag = spec.get("flag", "word_wax")
	line = spec.get("line", "")
	all_of = spec.get("all_of", [])
	sets = spec.get("sets", "")

func _ready() -> void:
	add_child(KitLib.instance("word_stone"))
	var zone := Interactable.new()
	zone.prompt = "Read the graven word"
	zone.setup_zone(1.4, 1.4)
	zone.activated.connect(_on_read)
	add_child(zone)

func _known() -> int:
	var n := 0
	for f in all_of:
		if World.flag(String(f)):
			n += 1
	return n

func _on_read(_p) -> void:
	World.set_flag(flag, true)
	var text := "THE GRAVEN WORD\n\n%s\n\n%s" % [word, line]
	if sets != "" and not all_of.is_empty():
		if _known() >= all_of.size():
			if not World.flag(sets):
				World.set_flag(sets, true)
			text += "\n\nThe three words are yours. Across the town, the parish door grinds off its bar."
		else:
			text += "\n\n(%d of %d words found. The parish listens for the rest.)" % [_known(), all_of.size()]
	Game.lore_panel.emit(text)
