class_name PlayerVisual
extends Node3D
## Assembles the Latecomer's node rig from kit pieces and drives locomotion
## flavor procedurally (bob, lean); discrete actions play AnimationPlayer
## clips built by AnimBuilder.

var pose: Node3D
var trail: MeshInstance3D
var shoulder_r: Node3D
var shoulder_l: Node3D
var weapon_mount: Node3D
var shield_mount: Node3D
var anim: AnimationPlayer

var _bob_t := 0.0
var _lean := Vector2.ZERO
var _step_phase := 0.0
var _step_i := 0

func build(weapon_kit := "sword_cloister") -> void:
	pose = Node3D.new(); pose.name = "Pose"; add_child(pose)
	var body := KitLib.instance("char_latecomer")
	body.name = "Body"
	pose.add_child(body)

	shoulder_l = Node3D.new(); shoulder_l.name = "ShoulderL"
	shoulder_l.position = Vector3(-0.29, 1.22, 0.02)
	pose.add_child(shoulder_l)
	shoulder_l.add_child(KitLib.instance("char_sleeve_l"))
	shield_mount = Node3D.new(); shield_mount.name = "ShieldMount"
	shield_mount.position = Vector3(-0.05, -0.32, 0.05)
	shoulder_l.add_child(shield_mount)
	shield_mount.add_child(KitLib.instance("shield_kite"))

	shoulder_r = Node3D.new(); shoulder_r.name = "ShoulderR"
	shoulder_r.position = Vector3(0.29, 1.22, 0.02)
	pose.add_child(shoulder_r)
	shoulder_r.add_child(KitLib.instance("char_sleeve_r"))
	weapon_mount = Node3D.new(); weapon_mount.name = "WeaponMount"
	weapon_mount.position = Vector3(0.02, -0.5, 0)
	shoulder_r.add_child(weapon_mount)
	set_weapon(weapon_kit)
	trail = MeshInstance3D.new()
	trail.name = "Trail"
	var tq := PlaneMesh.new()
	tq.size = Vector2(0.55, 1.05)
	tq.orientation = PlaneMesh.FACE_Z
	trail.mesh = tq
	var tm := ShaderMaterial.new()
	tm.shader = load("res://shaders/trail.gdshader")
	trail.set_surface_override_material(0, tm)
	trail.position = Vector3(0, 0.72, 0)
	trail.visible = false
	weapon_mount.add_child(trail)

	anim = AnimationPlayer.new()
	anim.name = "Anim"
	add_child(anim)
	anim.root_node = anim.get_path_to(self)
	anim.add_animation_library("", AnimBuilder.build_library())
	anim.play("RESET")
	anim.advance(0.05)
	anim.play("idle")

func set_weapon(kit_id: String) -> void:
	for c in weapon_mount.get_children():
		c.queue_free()
	if kit_id != "":
		weapon_mount.add_child(KitLib.instance(kit_id))

func play(clip: String, blend := 0.12, speed := 1.0) -> void:
	if anim.has_animation(clip):
		anim.play(clip, blend, speed)

func back_to_idle(blend := 0.2) -> void:
	anim.play("idle", blend)

## Locomotion flavor: bob with stride, lean into acceleration, footfalls.
func locomotion(dt: float, ground_speed: float, accel_lean: Vector2, grounded := true) -> void:
	_bob_t += dt * (2.0 + ground_speed * 1.7)
	if grounded and ground_speed > 0.8:
		_step_phase += dt * (1.4 + ground_speed * 0.62)
		if _step_phase >= 1.0:
			_step_phase = 0.0
			_step_i = (_step_i + 1) % 2
			AudioDirector.sfx_at("res://assets/audio/step%d.wav" % (_step_i + 1),
					global_position, -14.0, randf_range(0.92, 1.08))
	_lean = _lean.lerp(accel_lean, 1.0 - exp(-8.0 * dt))
	if anim.current_animation == "idle" or anim.current_animation == "":
		var bob: float = sin(_bob_t) * clampf(ground_speed * 0.008, 0.0, 0.035)
		pose.position.y = bob
		pose.rotation.x = clampf(-_lean.y * 0.06, -0.14, 0.14)
		pose.rotation.z = clampf(_lean.x * 0.05, -0.12, 0.12)
