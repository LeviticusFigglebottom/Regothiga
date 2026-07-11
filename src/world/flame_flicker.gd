extends OmniLight3D
## Every candle breathes: a slow two-sine wobble on the flame light's
## energy, phase-scattered so a hall of votives never pulses in step.
## Attached by KitLib.add_flame_lights to every flame it kindles.

var _base := 1.8
var _amp := 0.11
var _w := 7.0
var _p := 0.0

func _ready() -> void:
	_base = light_energy
	_p = randf() * TAU
	_w = randf_range(5.0, 9.0)
	_amp = randf_range(0.08, 0.14)

func _process(_dt: float) -> void:
	var t := Time.get_ticks_msec() / 1000.0
	light_energy = _base * (1.0 + _amp * (sin(t * _w + _p) * 0.6
			+ sin(t * _w * 2.7 + _p * 1.7) * 0.4))
