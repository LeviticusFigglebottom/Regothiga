extends OmniLight3D
## Every candle breathes: a slow multi-sine wobble on the flame light's
## energy, phase-scattered so a hall of votives never pulses in step and
## specular highlights dance subtly across stone and plate armor.
## Attached by KitLib.add_flame_lights to every flame it kindles.

var _base := 1.8
var _amp := 0.12
var _w := 7.0
var _p := 0.0

func _ready() -> void:
	_base = light_energy
	_p = randf() * TAU
	_w = randf_range(5.0, 9.0)
	_amp = randf_range(0.09, 0.15)

func _process(_dt: float) -> void:
	if not is_visible_in_tree():
		return
	var p = Game.player
	if p != null and global_position.distance_squared_to(p.global_position) > 1500.0:
		return
	var t := Time.get_ticks_msec() * 0.001
	var wave := sin(t * _w + _p) * 0.6 + sin(t * _w * 2.7 + _p * 1.7) * 0.4
	light_energy = _base * (1.0 + _amp * wave)
