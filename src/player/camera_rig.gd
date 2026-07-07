class_name CameraRig
extends Node3D
## Third-person orbit + soulslike lock-on. Lives on the player root.
## Chain: self (yaw, at neck height) -> Pitch -> SpringArm3D -> Camera3D.

var pitch_node: Node3D
var spring: SpringArm3D
var cam: Camera3D

var yaw := 0.0
var pitch := -0.22
var locked_target: Node3D = null
var sensitivity := 0.0035

var _shake_t := 0.0
var _shake_strength := 0.0
var _fov_base := 62.0

func _ready() -> void:
	position = Vector3(0, 1.55, 0)
	pitch_node = Node3D.new(); pitch_node.name = "Pitch"; add_child(pitch_node)
	spring = SpringArm3D.new()
	spring.spring_length = float(DB.tuning("camera/distance", 3.6))
	spring.margin = 0.25
	spring.collision_mask = VG.M_WORLD_ALL
	pitch_node.add_child(spring)
	cam = Camera3D.new()
	_fov_base = float(DB.tuning("camera/fov", 62))
	cam.fov = _fov_base
	cam.near = 0.1
	cam.far = 300.0
	spring.add_child(cam)
	cam.position = Vector3(0.35, 0.25, 0)   # over-the-shoulder bias
	cam.current = true
	sensitivity = float(DB.tuning("camera/sensitivity", 0.0035))
	Juice.shake_requested.connect(_on_shake)
	set_as_top_level(false)

func _on_shake(strength: float, time: float) -> void:
	_shake_strength = maxf(_shake_strength, strength)
	_shake_t = maxf(_shake_t, time)

## Settings-menu seams (PauseUI persists these across runs).
func set_sensitivity(v: float) -> void:
	sensitivity = v

func set_base_fov(f: float) -> void:
	_fov_base = f
	if cam != null:
		cam.fov = f

func mouse_look(rel: Vector2) -> void:
	if locked_target != null:
		# a hard flick breaks the lock so the camera can never feel "stuck"
		if absf(rel.x) > 60.0:
			locked_target = null
		return
	yaw -= rel.x * sensitivity
	pitch = clampf(pitch - rel.y * sensitivity, -1.15, 0.55)

func stick_look(v: Vector2, dt: float) -> void:
	if locked_target != null or v.length_squared() < 0.02:
		return
	yaw -= v.x * 2.6 * dt
	pitch = clampf(pitch - v.y * 1.8 * dt, -1.15, 0.55)

func try_lock(candidates: Array) -> void:
	if locked_target != null:
		locked_target = null
		return
	var best: Node3D = null
	var best_score := INF
	var fwd := -global_transform.basis.z
	for c in candidates:
		if not is_instance_valid(c):
			continue
		var to: Vector3 = c.global_position - global_position
		var d := to.length()
		if d > 16.0:
			continue
		var ang := fwd.angle_to(to.normalized())
		if ang > 1.1:
			continue
		if not _has_los(c):
			continue                      # never lock through a wall
		var score := d + ang * 6.0
		if score < best_score:
			best_score = score
			best = c
	locked_target = best

## True when nothing world-solid stands between the camera and the target's
## chest. Ray runs from the CAMERA (not the player) so a foe peeking past a
## pillar you can actually see is still lockable.
func _has_los(c: Node3D) -> bool:
	var space := get_world_3d().direct_space_state
	var from := cam.global_position if cam != null else global_position
	var to := c.global_position + Vector3.UP * 1.1
	var q := PhysicsRayQueryParameters3D.create(from, to, VG.M_WORLD_ALL)
	q.exclude = [get_parent()]
	return space.intersect_ray(q).is_empty()

func _physics_process(dt: float) -> void:
	if locked_target != null and (not is_instance_valid(locked_target) or locked_target.get("dead") == true):
		locked_target = null
	if locked_target != null:
		var to: Vector3 = locked_target.global_position - global_position
		var flat := Vector2(to.x, to.z)
		var target_yaw := atan2(-flat.x, -flat.y)
		yaw = lerp_angle(yaw, target_yaw, 1.0 - exp(-8.0 * dt))
		# aim at the target's CHEST from a comfortable over-shoulder line: the
		# old math aimed at its feet with an extra downward bias, which slammed
		# the camera toward the floor at close range. Distance is floored so a
		# point-blank foe can't fold the pitch either.
		var target_pitch := clampf(atan2(to.y + 1.1, maxf(flat.length(), 2.6)) - 0.14, -0.42, 0.22)
		pitch = lerpf(pitch, target_pitch, 1.0 - exp(-6.0 * dt))
	rotation.y = yaw
	pitch_node.rotation.x = pitch
	# shake
	if _shake_t > 0.0:
		_shake_t -= dt
		var s := _shake_strength * minf(_shake_t * 3.0, 1.0)
		cam.h_offset = (randf() - 0.5) * s * 0.3
		cam.v_offset = (randf() - 0.5) * s * 0.3
		if _shake_t <= 0.0:
			cam.h_offset = 0.0
			cam.v_offset = 0.0
			_shake_strength = 0.0

func set_sprinting(on: bool, dt: float) -> void:
	var target := _fov_base + (6.0 if on else 0.0)
	cam.fov = lerpf(cam.fov, target, 1.0 - exp(-6.0 * dt))

## Camera-relative movement basis on the ground plane.
func move_basis() -> Basis:
	return Basis(Vector3.UP, yaw)
