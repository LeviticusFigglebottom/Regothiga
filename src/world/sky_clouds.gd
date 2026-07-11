extends Node3D
## The cloud sea the Sanctum floats on: banks of cloud orbiting the ward in
## a slow, stately drift — below the floor line all around, plus a higher
## scatter riding among the far castles. Motion is a gentle orbit (constant
## angular speed per bank) so the sky never empties and nothing ever pops.
## Placed from an area's "scripted" section:
##   {"script": ".../sky_clouds.gd", "at": [0,0,0], "tag": "base",
##    "params": {"low_count": 30, "high_count": 10, "drift": 0.9}}

var low_count := 26           # the sea ringing the ward
var high_count := 10          # drifting among the far spires
var under_count := 8          # the sea directly beneath the floor line
var r_lo_min := 96.0          # ward reaches r~37; a 2.4-scaled bank's long
var r_lo_max := 190.0         # axis pokes ~28 inward — nothing reads as a
                              # walkable shelf from the landing rail again
var r_hi_min := 110.0
var r_hi_max := 235.0
var drift := 1.1              # tangential metres per second, scaled by 1/r
var seed_v := 5

var _banks: Array = []

const KITS := ["cloud_bank_a", "cloud_bank_b", "cloud_bank_c"]

func _ready() -> void:
	var rng := RandomNumberGenerator.new()
	rng.seed = seed_v
	for i in low_count:
		_bank(rng, rng.randf_range(r_lo_min, r_lo_max),
				rng.randf_range(-20.0, -9.0), rng.randf_range(1.8, 2.4))
	for i in high_count:
		_bank(rng, rng.randf_range(r_hi_min, r_hi_max),
				rng.randf_range(8.0, 26.0), rng.randf_range(1.4, 2.6))
	for i in under_count:
		# deep beneath the ward: tops stay well below the floor slab
		_bank(rng, rng.randf_range(4.0, 46.0),
				rng.randf_range(-32.0, -24.0), rng.randf_range(2.4, 3.4))

func _bank(rng: RandomNumberGenerator, r: float, y: float, s: float) -> void:
	var n := KitLib.instance(KITS[rng.randi() % KITS.size()])
	n.scale = Vector3(s, s * rng.randf_range(0.7, 0.9), s)
	n.rotation.y = rng.randf_range(0.0, TAU)
	add_child(n)
	_banks.append({"n": n, "ang": rng.randf_range(0.0, TAU), "r": r, "y": y,
			"w": drift / r * (1.0 if rng.randf() < 0.85 else 0.6)})
	_apply(_banks[-1])

func _apply(b: Dictionary) -> void:
	var n: Node3D = b["n"]
	n.position = Vector3(cos(b["ang"]) * b["r"], b["y"], sin(b["ang"]) * b["r"])

func _process(dt: float) -> void:
	for b in _banks:
		b["ang"] = fmod(b["ang"] + b["w"] * dt, TAU)
		_apply(b)
