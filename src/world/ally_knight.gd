class_name AllyKnight
extends CharacterBody3D
## Ser Adalric of the Morrow, answered: a radiant phantom comrade. He hunts
## the quarter's foes with sword and storm-glass, cannot leave the quarter,
## and cannot be dismissed. He fades when slain, when the Latecomer falls,
## or when the warden rests at last.

var max_hp := 320.0
var hp := 320.0
var dead := false

var vis: CharVisual
var hurtbox: Hurtbox
var hitbox: Hitbox
var target: Node3D = null

var _atk_cd := 0.0
var _bolt_cd := 2.5
var _retarget := 0.0
var _busy := false
var _fading := false
var _light: OmniLight3D

func _ready() -> void:
	add_to_group("allies")
	collision_layer = 1 << (VG.L_PLAYER - 1)
	collision_mask = VG.M_WORLD_ALL
	var cs := CollisionShape3D.new()
	var cap := CapsuleShape3D.new()
	cap.radius = 0.36
	cap.height = 1.7
	cs.shape = cap
	cs.position.y = 0.9
	add_child(cs)

	vis = CharVisual.new()
	vis.name = "Vis"
	add_child(vis)
	vis.build_body("skel_ward", 1.0, 1.0)
	var m := vis.mount("hand_r")
	if KitLib.has_piece("sword_cloister"):
		m.add_child(KitLib.instance("sword_cloister"))
	_set_ghost(0.35)
	_light = OmniLight3D.new()
	_light.light_color = Color(1.0, 0.86, 0.55)
	_light.light_energy = 1.2
	_light.omni_range = 4.5
	_light.shadow_enabled = false
	_light.position.y = 1.3
	add_child(_light)

	hurtbox = Hurtbox.new()
	hurtbox.team = "player"
	var hcs := CollisionShape3D.new()
	var cyl := CylinderShape3D.new()
	cyl.radius = 0.5
	cyl.height = 1.9
	hcs.shape = cyl
	hcs.position.y = 0.95
	hurtbox.add_child(hcs)
	add_child(hurtbox)

	hitbox = Hitbox.new()
	hitbox.exclude = self
	hitbox.friendly_team = "player"
	var hbs := CollisionShape3D.new()
	var bx := BoxShape3D.new()
	bx.size = Vector3(1.7, 1.5, 1.9)
	hbs.shape = bx
	hbs.position = Vector3(0, 1.1, -1.2)
	hitbox.add_child(hbs)
	vis.add_child(hitbox)

	Game.player_forgotten.connect(fade_out)
	Game.area_cleared.connect(_on_cleared)
	# a phantom passes the pale: the fog seals bar flesh, not him
	for g in get_tree().get_nodes_in_group(VG.GROUP_RESPAWN_ON_REST):
		if g is FogGate and g._seal != null:
			add_collision_exception_with(g._seal)

func _on_cleared(_aid: String) -> void:
	fade_out()

## The phantom look: translucent flesh, a votive glow.
func _set_ghost(v: float) -> void:
	var stack: Array[Node] = [vis]
	while not stack.is_empty():
		var n: Node = stack.pop_back()
		if n is GeometryInstance3D:
			(n as GeometryInstance3D).transparency = v
		for c in n.get_children():
			stack.append(c)

func take_hit(packet: DamagePacket) -> void:
	if dead:
		return
	hp -= packet.amount
	AudioDirector.sfx_at("res://assets/audio/impact_flesh.wav", global_position, -6.0, 1.2)
	if hp <= 0.0:
		fade_out()

func fade_out() -> void:
	if _fading:
		return
	_fading = true
	dead = true
	collision_layer = 0
	hurtbox.set_deferred("monitorable", false)
	set_physics_process(false)
	AudioDirector.sfx_at("res://assets/audio/fog_enter.wav", global_position, -4.0, 1.3)
	var tw := create_tween()
	tw.tween_method(_fade_step, 0.35, 1.0, 1.4)
	tw.tween_callback(queue_free)

func _fade_step(v: float) -> void:
	_set_ghost(v)
	if _light != null:
		_light.light_energy = 1.2 * (1.0 - v)

func _nearest_foe() -> Node3D:
	var best: Node3D = null
	var bd := 28.0
	for e in get_tree().get_nodes_in_group(VG.GROUP_ENEMIES):
		if e == null or not is_instance_valid(e) or e.get("dead"):
			continue
		var d: float = global_position.distance_to(e.global_position)
		if d < bd:
			bd = d
			best = e
	return best

func _los_to(n: Node3D) -> bool:
	var q := PhysicsRayQueryParameters3D.create(global_position + Vector3.UP * 1.4,
			n.global_position + Vector3.UP * 1.0, VG.M_WORLD_ALL)
	return get_world_3d().direct_space_state.intersect_ray(q).is_empty()

func _physics_process(dt: float) -> void:
	_atk_cd -= dt
	_bolt_cd -= dt
	_retarget -= dt
	if _retarget <= 0.0:
		_retarget = 0.5
		target = _nearest_foe()
	if not is_on_floor():
		velocity.y -= 22.0 * dt
	else:
		velocity.y = maxf(velocity.y, -0.5)

	# he keeps to the Latecomer's side first; the hunt only holds while
	# they walk together
	var far_from_player := Game.player != null and is_instance_valid(Game.player) \
			and global_position.distance_to(Game.player.global_position) > 14.0
	var goal := global_position
	var stop := 1.9
	if target != null and is_instance_valid(target) and not far_from_player:
		goal = target.global_position
	elif Game.player != null and is_instance_valid(Game.player):
		goal = Game.player.global_position
		stop = 3.2
	var flat := goal - global_position
	flat.y = 0.0
	var moving := flat.length() > stop and not _busy
	if moving:
		var dir := flat.normalized()
		velocity.x = dir.x * 4.4
		velocity.z = dir.z * 4.4
	else:
		velocity.x = move_toward(velocity.x, 0, 18 * dt)
		velocity.z = move_toward(velocity.z, 0, 18 * dt)
	if flat.length() > 0.4:
		var ty := atan2(-flat.x, -flat.z)
		vis.rotation.y = lerp_angle(vis.rotation.y, ty, 1.0 - exp(-7.0 * dt))
	move_and_slide()
	vis.locomotion(dt, Vector2(velocity.x, velocity.z).length())

	if _busy or far_from_player or target == null or not is_instance_valid(target):
		return
	var d := global_position.distance_to(target.global_position)
	if d <= 2.3 and _atk_cd <= 0.0:
		_melee()
	elif d >= 5.0 and d <= 16.0 and _bolt_cd <= 0.0 and _los_to(target):
		_bolt(target)

func _melee() -> void:
	_busy = true
	_atk_cd = 1.4
	vis.play("attack_l1", 0.1)
	await get_tree().create_timer(0.34, false).timeout
	if dead:
		return
	var pk := DamagePacket.new(34.0, 26.0, self)
	hitbox.begin_swing(pk)
	AudioDirector.sfx_at("res://assets/audio/swing.wav", global_position, -6.0, 1.05)
	await get_tree().create_timer(0.16, false).timeout
	if is_instance_valid(hitbox):
		hitbox.end_swing()
	_busy = false
	if is_instance_valid(vis):
		vis.back_to_idle(0.25)

## The storm-glass versicle: a thrown bolt of pale lightning.
func _bolt(at: Node3D) -> void:
	_busy = true
	_bolt_cd = 4.5
	vis.play("attack_l1", 0.1, 1.3)
	await get_tree().create_timer(0.3, false).timeout
	_busy = false
	if dead or at == null or not is_instance_valid(at):
		return
	var from := global_position + Vector3.UP * 1.5
	var dir := (at.global_position + Vector3.UP * 1.0) - from
	var pk := DamagePacket.new(44.0, 20.0, self)
	pk.can_be_parried = false
	pk.kind = "lightning"
	var pr := Projectile.launch(get_parent(), from, dir, 17.0, pk, Color(0.72, 0.84, 1.0))
	pr.team = "player"
	AudioDirector.sfx_at("res://assets/audio/swell_kindle.wav", from, -8.0, 1.6)
	if is_instance_valid(vis):
		vis.back_to_idle(0.25)
