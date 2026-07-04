extends Node
## Juice — centralized game-feel: hitstop, camera shake requests, kick pulses.
## Systems ask for feel here so it stays tunable in one place.

signal shake_requested(strength: float, time: float)

var _hitstop_until_ms := 0

## Freeze gameplay briefly. Uses Engine.time_scale; stacked calls extend.
func hitstop(duration := 0.09, scale := 0.05) -> void:
	Engine.time_scale = scale
	var until := Time.get_ticks_msec() + int(duration * 1000.0)
	_hitstop_until_ms = max(_hitstop_until_ms, until)
	_restore_later()

func _restore_later() -> void:
	await get_tree().create_timer(0.02, true, false, true).timeout
	if Time.get_ticks_msec() >= _hitstop_until_ms:
		Engine.time_scale = 1.0
	else:
		_restore_later()

func shake(strength := 0.3, time := 0.25) -> void:
	shake_requested.emit(strength, time)
