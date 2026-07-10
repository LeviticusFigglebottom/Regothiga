class_name CharVisual
extends Node3D
## Shared skeletal visual driver for player, enemies and NPCs. Instances a
## skel_* glb (armature + skinned mesh), builds the SkelAnim clip library
## against its rest pose, cross-fades locomotion cycles to actual ground
## speed, and mounts gear on bones via BoneAttachment3D.

var body: Node3D
var skel: Skeleton3D
var anim: AnimationPlayer
var trail: MeshInstance3D
var weapon_mount: Node3D
var shield_mount: Node3D
var head_mount: Node3D

## ground speed (m/s) at which the walk / run cycles play at 1x
var stride := 2.6
var run_stride := 5.2
var footsteps := false
var step_volume := -14.0

var _step_i := 0
var _lean := Vector2.ZERO

## When set, standing rest plays this clip instead of "idle" (e.g. the
## Immortalized's two-handed vigil stance). Walk/run stay themselves.
var idle_override := ""

const LOCO := ["idle", "walk", "run", "twohand_idle", ""]

func build_body(skel_id: String, amp := 1.0, sway := 1.0, vis_scale := 1.0) -> void:
	body = KitLib.instance(skel_id)
	body.name = "Body"
	if vis_scale != 1.0:
		body.scale = Vector3.ONE * vis_scale
	add_child(body)
	skel = body.find_child("Skeleton3D", true, false) as Skeleton3D
	if skel == null:
		push_error("CharVisual: '%s' has no Skeleton3D" % skel_id)
		return
	anim = AnimationPlayer.new()
	anim.name = "Anim"
	add_child(anim)
	anim.root_node = anim.get_path_to(self)
	anim.add_animation_library("", SkelAnim.build_library(skel, get_path_to(skel), amp, sway))
	anim.play("idle")
	anim.advance(randf() * 1.7)   # desync crowds

## A gear mount that rides a bone. Returned node is a child of the
## BoneAttachment3D; offset/orient it freely, then parent kit pieces to it.
func mount(bone: String) -> Node3D:
	var att := BoneAttachment3D.new()
	att.name = "Att_" + bone
	skel.add_child(att)
	att.bone_name = bone
	var m := Node3D.new()
	m.name = "Mount"
	att.add_child(m)
	return m

## Standard right-hand weapon grip. Kit weapons extend blade +Y from the
## grip origin, and the hand bone's +Y runs past the fingers — so an
## identity mount carries the blade beyond the fist (down when relaxed).
func mount_weapon_hand() -> Node3D:
	weapon_mount = mount("hand_r")
	weapon_mount.position = Vector3(0, 0.05, 0)
	return weapon_mount

func set_weapon(kit_id: String) -> void:
	if weapon_mount == null:
		mount_weapon_hand()
	for c in weapon_mount.get_children():
		c.queue_free()
	if kit_id != "":
		weapon_mount.add_child(KitLib.instance(kit_id))

func add_trail() -> void:
	trail = MeshInstance3D.new()
	trail.name = "Trail"
	var tq := PlaneMesh.new()
	tq.size = Vector2(0.55, 1.05)
	tq.orientation = PlaneMesh.FACE_Z
	trail.mesh = tq
	var tm := ShaderMaterial.new()
	tm.shader = load("res://shaders/trail.gdshader")
	trail.set_surface_override_material(0, tm)
	trail.position = Vector3(0, 0.68, 0)   # centered along the blade (+Y)
	trail.visible = false
	# sibling of the weapon so set_weapon() never frees it
	weapon_mount.get_parent().add_child(trail)

func play(clip: String, blend := 0.12, speed := 1.0) -> void:
	if anim == null:
		return
	anim.speed_scale = 1.0
	if anim.has_animation(clip):
		anim.play(clip, blend, speed)

func back_to_idle(blend := 0.2) -> void:
	if anim == null:
		return
	anim.speed_scale = 1.0
	anim.play("idle", blend)

func idle(blend := 0.25) -> void:
	back_to_idle(blend)

## Locomotion: cross-fade idle/walk/run by ground speed and time the cycle
## to the actual stride so feet stop skating. Only touches the animation
## while a locomotion clip owns it — action clips play out untouched.
func locomotion(dt: float, ground_speed: float, accel_lean := Vector2.ZERO, grounded := true) -> void:
	if anim == null:
		return
	var cur := anim.current_animation
	if not (cur in LOCO):
		return
	var want := "idle" if idle_override == "" else idle_override
	if grounded and ground_speed > 0.55:
		want = "run" if ground_speed > stride * 1.5 else "walk"
	if want != cur:
		anim.play(want, 0.3)
	match want:
		"walk":
			anim.speed_scale = clampf(ground_speed / stride, 0.55, 1.75)
		"run":
			anim.speed_scale = clampf(ground_speed / run_stride, 0.7, 1.5)
		_:
			anim.speed_scale = 1.0
	# lean into acceleration (whole-rig, subtle)
	_lean = _lean.lerp(accel_lean if want != "idle" else Vector2.ZERO, 1.0 - exp(-7.0 * dt))
	rotation.x = clampf(-_lean.y * 0.05, -0.1, 0.1)
	rotation.z = clampf(_lean.x * 0.04, -0.09, 0.09)
	# footfalls at each half-cycle
	if footsteps and want != "idle" and grounded:
		var half: float = maxf(anim.current_animation_length * 0.5, 0.01)
		var idx := int(anim.current_animation_position / half)
		if idx != _step_i:
			_step_i = idx
			AudioDirector.sfx_at("res://assets/audio/step%d.wav" % ((idx % 2) + 1),
					global_position, step_volume, randf_range(0.9, 1.1))
