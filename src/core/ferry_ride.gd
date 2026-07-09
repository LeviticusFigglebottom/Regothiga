class_name FerryRide
extends Node3D
## The waterworks passage: the Ferryman's skiff poles down the great canal —
## out through the tunnel mouth of the Drowned Marches, then in along the
## outskirts water to the commoners' landing. Any input skips.

signal finished

## Each beat stages an area and glides the skiff from -> to; the camera
## rides at a fixed offset, watching the bow. Beat one runs the south
## channel beside the marches causeway — past the jetty, under the vault,
## and out the tunnel mouth onto the open west reach; beat two pulls in
## along the outskirts water toward the commoners' landing.
var beats := [
	{"area": "drowned_marches", "state": VG.WState.RUIN,
	 "from": Vector3(-10, -2.3, -11), "to": Vector3(-72, -2.3, -11),
	 "cam": Vector3(4.2, 2.6, -3.6), "dur": 12.0},
	{"area": "old_outskirts", "state": VG.WState.RUIN,
	 "from": Vector3(1.8, -2.3, 27.5), "to": Vector3(1.8, -2.3, 18.8),
	 "cam": Vector3(4.5, 3.6, 4.6), "dur": 7.0},
]

var _cam: Camera3D
var _layer: CanvasLayer
var _black: ColorRect
var _area: Area
var _skiff: Node3D
var _skipped := false
var _done := false

func _ready() -> void:
	_cam = Camera3D.new()
	_cam.fov = 66
	add_child(_cam)
	_cam.make_current()
	_layer = CanvasLayer.new()
	_layer.layer = 90
	add_child(_layer)
	_black = ColorRect.new()
	_black.color = Color.BLACK
	_black.set_anchors_preset(Control.PRESET_FULL_RECT)
	_layer.add_child(_black)
	_run.call_deferred()

func _unhandled_input(event: InputEvent) -> void:
	if _done:
		return
	if (event is InputEventKey and event.pressed) \
			or (event is InputEventMouseButton and event.pressed) \
			or (event is InputEventJoypadButton and event.pressed):
		_skipped = true

func _fade(to_a: float, dur: float) -> void:
	var tw := create_tween()
	tw.tween_property(_black, "color:a", to_a, dur)
	await tw.finished

func _stage(beat: Dictionary) -> void:
	if _area != null:
		_area.queue_free()
	if _skiff != null:
		_skiff.queue_free()
	_area = AreaBuilder.build(beat["area"])
	_strip_spawners(_area)
	add_child(_area)
	StateDirector.snap(_area, beat["state"])
	_skiff = KitLib.instance("ferry_skiff")
	add_child(_skiff)
	_skiff.position = beat["from"]
	# the ferryman's lantern still burns at the bow; it is what reads in the dark
	var lamp := OmniLight3D.new()
	lamp.light_color = Color(1.0, 0.82, 0.5)
	lamp.light_energy = 1.6
	lamp.omni_range = 7.0
	lamp.omni_attenuation = 1.4
	lamp.shadow_enabled = false
	lamp.position = Vector3(0, 1.5, -0.6)
	_skiff.add_child(lamp)

## The staged quarters are scenery for the passage, not live ground: no
## foe should stand in the shot. Freed before the area enters the tree,
## so the spawners never ready and nothing is ever spawned.
func _strip_spawners(root: Node) -> void:
	var stack: Array[Node] = [root]
	var doomed: Array[Node] = []
	while not stack.is_empty():
		var n: Node = stack.pop_back()
		if n is Spawner:
			doomed.append(n)
			continue
		for c in n.get_children():
			stack.append(c)
	for s in doomed:
		s.get_parent().remove_child(s)
		s.free()

func _run() -> void:
	AudioDirector.sfx("res://assets/audio/fog_enter.wav", -6.0, 0.7)
	for beat in beats:
		if _skipped:
			break
		_stage(beat)
		var from: Vector3 = beat["from"]
		var to: Vector3 = beat["to"]
		var off: Vector3 = beat["cam"]
		var travel := to - from
		_skiff.rotation.y = atan2(-travel.x, -travel.z)
		_cam.look_at_from_position(from + off, from + Vector3(0, 0.8, 0))
		await _fade(0.0, 0.8)
		var dur: float = beat["dur"]
		var t := 0.0
		while t < dur and not _skipped:
			t += get_process_delta_time()
			var k := clampf(t / dur, 0.0, 1.0)
			var ke := k * k * (3.0 - 2.0 * k)
			var pos := from.lerp(to, ke)
			pos.y += sin(t * 1.4) * 0.05   # the water carries it
			_skiff.position = pos
			_cam.look_at_from_position(pos + off, pos + Vector3(0, 1.0, 0) + travel.normalized() * 9.0)
			await get_tree().process_frame
		await _fade(1.0, 0.8)
	_done = true
	if _area != null:
		_area.queue_free()
		_area = null
	if _skiff != null:
		_skiff.queue_free()
		_skiff = null
	finished.emit()

## Called by the portal once travel has landed the Latecomer.
func reveal_and_free() -> void:
	var tw := create_tween()
	tw.tween_property(_black, "color:a", 0.0, 1.1)
	tw.tween_callback(queue_free)
