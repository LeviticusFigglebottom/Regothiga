class_name FlagGate
extends Node3D
## A physical barrier that stands until a world flag comes true, then sinks
## away for good. Used by the votive locks and the Sexton's dug shortcut.

var flag := ""
var kit := "fence_iron_4m"
var open_sfx := "res://assets/audio/swell_kindle.wav"
var open_dir := "down"          # "down" sinks away; "up" hoists (portcullis)

var _piece: Node3D
var _body: StaticBody3D
var _open := false

func setup(spec: Dictionary, tag_bit: int) -> void:
	flag = spec.get("flag", "")
	kit = spec.get("kit", "fence_iron_4m")
	open_dir = spec.get("open_dir", "down")
	_piece = KitLib.instance(kit)
	add_child(_piece)
	_body = StaticBody3D.new()
	_body.collision_layer = 1 << (tag_bit - 1)
	_body.collision_mask = 0
	var cs := CollisionShape3D.new()
	var box := BoxShape3D.new()
	var sz: Array = KitLib.manifest().get(kit, {}).get("size", [4, 0.4, 3])
	box.size = Vector3(float(sz[0]), float(sz[2]), maxf(float(sz[1]), 0.4))
	cs.shape = box
	cs.position.y = float(sz[2]) * 0.5
	_body.add_child(cs)
	add_child(_body)

func _ready() -> void:
	if World.flag(flag):
		_snap_open()

func _physics_process(_dt: float) -> void:
	if not _open and flag != "" and World.flag(flag):
		_animate_open()

func _snap_open() -> void:
	_open = true
	_body.collision_layer = 0
	_piece.visible = false
	set_physics_process(false)

func _animate_open() -> void:
	_open = true
	_body.collision_layer = 0
	set_physics_process(false)
	AudioDirector.sfx_at(open_sfx, global_position, -4.0, 0.9)
	Juice.shake(0.2, 0.2)
	var tw := create_tween()
	tw.tween_property(_piece, "position:y", 3.6 if open_dir == "up" else -3.2, 1.6) \
		.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
	tw.tween_callback(func(): _piece.visible = false)
