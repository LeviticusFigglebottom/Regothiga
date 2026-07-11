extends Node3D
## The ledger of the twelve trials. Counts the kept flags; speaks the
## count as it grows; at twelve, the bell's blessing rings true and the
## last door lets go.
##   {"script": ".../blessing_keeper.gd", "at": [0,0,0], "tag": "base",
##    "params": {"count": 12, "prefix": "morrow_trial_",
##               "flag": "bell_blessing"}}

var count := 12
var prefix := "morrow_trial_"
var flag := "bell_blessing"

var _known := -1

func _ready() -> void:
	if World.flag(flag):
		return
	var t := Timer.new()
	t.wait_time = 0.5
	t.timeout.connect(func():
		var n := 0
		for i in count:
			if World.flag(prefix + str(i + 1)):
				n += 1
		if n != _known:
			if _known >= 0 and n > _known and n < count:
				Game.toast.emit("%d of %d trials kept." % [n, count])
			_known = n
		if n >= count and not World.flag(flag):
			World.set_flag(flag)
			World.save_game()
			Game.toast.emit("Twelve trials kept. The bell gives its blessing — the last door stands open.")
			AudioDirector.sfx("res://assets/audio/remembrance.wav", -2.0, 0.9)
			t.queue_free())
	add_child(t)
	t.start()
