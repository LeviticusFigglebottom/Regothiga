extends Node3D
## Watches a set of world flags; when every one is true, sets a target flag
## (once) and announces it. The Hour Gate's wing-objectives use this.
##   {"script": ".../seal_gate.gd", "at": [...], "params":
##     {"flags": ["palace_hours", "palace_candles"],
##      "target": "palace_gate_open", "notice": "The Hour Gate stirs."}}

var flags: Array = []
var target := ""
var notice := "Something ancient unbars."

var _done := false

func _physics_process(_dt: float) -> void:
	if _done:
		return
	if World.flag(target):
		_done = true
		return
	for f in flags:
		if not World.flag(String(f)):
			return
	World.set_flag(target)
	Game.toast.emit(notice)
	AudioDirector.sfx("res://assets/audio/swell_kindle.wav", -4.0, 0.7)
	_done = true
