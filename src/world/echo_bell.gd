extends Node3D
## The Bellman's Echo. The mother bell remembers the day; asked, she tolls
## a phrase — a handful of the four offices, glowing each chime as she
## names it — and the pilgrim must answer the phrase back on the chimes in
## her order. A wrong note scolds and she offers the phrase again. Each
## asking may draw a different phrase, so listen, don't memorise plaques.
##   {"script": ".../echo_bell.gd", "at": [0,0,0], "tag": "base", "params":
##     {"flag": "palace_hours", "bell_at": [34,0,20], "chimes": [
##        {"id": "dawn", "label": "the dawn office", "at": [14,0,12], "rot": 120}, ...]}}

var flag := "palace_hours"
var bell_at: Array = [0, 0, 0]
var chimes: Array = []
var sequences: Array = [
	["dusk", "dawn", "noon"],
	["noon", "midnight", "dawn"],
	["midnight", "dawn", "dusk", "noon"],
]

var _nodes := {}          # id -> {light, pitch}
var _seq: Array = []
var _progress := 0
var _asked := 0
var _playing := false

const RING := "res://assets/audio/bell_toll.wav"
const WRONG := "res://assets/audio/impact_blocked.wav"

func _ready() -> void:
	if World.flag(flag):
		return
	var bell := Interactable.new()
	bell.prompt = "Ask the mother bell for the phrase"
	bell.setup_zone(2.2, 2.4)
	bell.activated.connect(func(_p): _demonstrate())
	add_child(bell)
	bell.position = Vector3(bell_at[0], bell_at[1], bell_at[2]) - position
	var i := 0
	for spec in chimes:
		var id := String(spec.get("id", "c%d" % i))
		var holder := Node3D.new()
		add_child(holder)
		holder.position = Vector3(spec["at"][0], spec["at"][1], spec["at"][2]) - position
		holder.rotation.y = deg_to_rad(float(spec.get("rot", 0)))
		if KitLib.has_piece("chime_stone"):
			holder.add_child(KitLib.instance("chime_stone"))
		var l := OmniLight3D.new()
		l.light_color = Color(1.0, 0.88, 0.5)
		l.light_energy = 0.0
		l.omni_range = 4.0
		l.shadow_enabled = false
		l.position.y = 1.6
		holder.add_child(l)
		var z := Interactable.new()
		z.prompt = "Answer on %s" % String(spec.get("label", id))
		z.setup_zone(1.5, 2.0)
		z.activated.connect(func(_p): _answer(id))
		holder.add_child(z)
		_nodes[id] = {"light": l, "pitch": 0.8 + 0.14 * i}
		i += 1

func _demonstrate() -> void:
	if _playing or World.flag(flag):
		return
	_playing = true
	_progress = 0
	_seq = sequences[_asked % sequences.size()]
	_asked += 1
	Game.toast.emit("The mother bell hums the day's phrase...")
	var tw := create_tween()
	tw.tween_interval(0.7)
	for id in _seq:
		tw.tween_callback(_pulse.bind(id))
		tw.tween_interval(1.05)
	tw.tween_callback(func():
		_playing = false
		Game.toast.emit("Answer her, office by office."))

func _pulse(id: String) -> void:
	if not _nodes.has(id):
		return
	var l: OmniLight3D = _nodes[id]["light"]
	AudioDirector.sfx_at(RING, l.global_position, -4.0, float(_nodes[id]["pitch"]))
	var tw := create_tween()
	tw.tween_property(l, "light_energy", 3.2, 0.12)
	tw.tween_property(l, "light_energy", 0.0, 0.75)

func _answer(id: String) -> void:
	if World.flag(flag):
		return
	if _playing:
		Game.toast.emit("She is still singing. Listen.")
		return
	if _seq.is_empty():
		Game.toast.emit("Ask the mother bell first — the phrase is hers to give.")
		return
	_pulse(id)
	if id == _seq[_progress]:
		_progress += 1
		if _progress >= _seq.size():
			World.set_flag(flag)
			Game.toast.emit("The echo answers true — the day is rung.")
			AudioDirector.sfx("res://assets/audio/swell_kindle.wav", -3.0, 0.8)
	else:
		_progress = 0
		_seq = []
		AudioDirector.sfx(WRONG, -6.0)
		Game.toast.emit("The bell falls sour. Ask her again, and listen closer.")
