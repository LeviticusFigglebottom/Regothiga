extends Node3D
## One trial of the Keep of the Morrow: a room-sized ordeal that pays a
## flag toward the bell's blessing. Three modes share the node:
##   "arena" — the room's foes wake when the pilgrim steps in; all down
##             pays the trial. "foes" ids spawn at "spots" (room-local).
##   "duel"  — an arena of one, announced a little louder.
##   "vigil" — a circle of light at the node: stand INSIDE it, unmoving
##             of purpose, for "hold" seconds. Leaving spills the wax.
## The chime / votive / watcher trials use their own data sections.
##   {"script": ".../trial_room.gd", "at": [cx, 0, cz], "tag": "base",
##    "params": {"flag": "morrow_trial_4", "mode": "arena",
##               "foes": ["gilded_echo", "gilded_echo"],
##               "spots": [[-2.5, 0, 0], [2.5, 0, 0]],
##               "radius": 6.0, "hold": 12.0,
##               "title": "the Trial of Arms"}}

var flag := ""
var mode := "arena"
var foes: Array = []
var spots: Array = []
var radius := 6.0
var hold := 12.0
var title := "the trial"

var _begun := false
var _left := 0
var _prog := 0.0
var _ring: MeshInstance3D = null
var _fill: MeshInstance3D = null

func _ready() -> void:
	if World.flag(flag):
		set_physics_process(false)
		return
	if mode == "vigil":
		_build_circle()

func _physics_process(dt: float) -> void:
	var p = Game.player
	if p == null or World.flag(flag):
		set_physics_process(false)
		return
	var d: float = global_position.distance_to(p.global_position)
	match mode:
		"arena", "duel":
			if not _begun and d < radius:
				_begin_fight()
		"vigil":
			if d < 1.7 and not bool(p.get("dead")):
				_prog = minf(_prog + dt, hold)
				if _prog >= hold:
					_complete()
			else:
				_prog = maxf(_prog - dt * 3.0, 0.0)
			if _fill != null:
				var k := _prog / hold
				_fill.scale = Vector3(maxf(k, 0.001), 1.0, maxf(k, 0.001))

func _begin_fight() -> void:
	_begun = true
	_left = foes.size()
	if _left == 0:
		_complete()
		return
	Game.toast.emit("%s begins." % title.capitalize())
	AudioDirector.sfx("res://assets/audio/bell_toll.wav", -10.0, 0.7)
	for i in foes.size():
		var e := Enemy.new()
		e.setup(String(foes[i]))
		get_parent().add_child(e)
		var off := Vector3(0, 0, 0)
		if i < spots.size():
			var s: Array = spots[i]
			off = Vector3(s[0], s[1], s[2])
		e.global_position = global_position + off
		e.target = Game.player
		e._set_state(Enemy.ES.ALERT)
		e.died.connect(func(_e): _foe_down())

func _foe_down() -> void:
	_left -= 1
	if _left <= 0 and not World.flag(flag):
		_complete()

func _build_circle() -> void:
	var mat := StandardMaterial3D.new()
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mat.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	mat.albedo_color = Color(1.0, 0.9, 0.55, 0.5)
	_ring = MeshInstance3D.new()
	var rm := TorusMesh.new()
	rm.inner_radius = 1.5
	rm.outer_radius = 1.7
	_ring.mesh = rm
	_ring.material_override = mat
	_ring.position.y = 0.06
	_ring.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(_ring)
	_fill = MeshInstance3D.new()
	var fm := CylinderMesh.new()
	fm.top_radius = 1.5
	fm.bottom_radius = 1.5
	fm.height = 0.04
	_fill.mesh = fm
	var fmat := mat.duplicate()
	fmat.albedo_color = Color(1.0, 0.9, 0.55, 0.22)
	_fill.material_override = fmat
	_fill.position.y = 0.05
	_fill.scale = Vector3(0.001, 1, 0.001)
	_fill.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(_fill)
	var l := OmniLight3D.new()
	l.light_color = Color(1.0, 0.9, 0.6)
	l.light_energy = 1.2
	l.omni_range = 4.0
	l.shadow_enabled = false
	l.position.y = 1.6
	add_child(l)

func _complete() -> void:
	World.set_flag(flag)
	World.save_game()
	Game.toast.emit("%s is kept. The bell remembers." % title.capitalize())
	AudioDirector.sfx("res://assets/audio/swell_kindle.wav", -4.0, 1.1)
	set_physics_process(false)
