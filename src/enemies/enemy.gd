class_name Enemy
extends CharacterBody3D
## Data-driven enemy: deliberate, telegraphed, punishing. Lives in the ruin
## layer; navigates the active navmesh; drops orisons.

signal died(enemy)

enum ES { IDLE, ALERT, APPROACH, COMBAT, ATTACK, STAGGER, DEAD }

var id := "penitent"
var cfg: Dictionary = {}
var hp := 50.0
var max_hp := 50.0
var poise := 30.0
var dead := false

var state: ES = ES.IDLE
var state_t := 0.0
var target: Node3D = null
var home := Vector3.ZERO

var _atk: Dictionary = {}
var _atk_done := false
var _cooldowns: Dictionary = {}
var _think_t := 0.0
var _strafe_dir := 1.0
var _blocking := false
var phase := 1

var vis: EnemyVisual
var agent: NavigationAgent3D
var hitbox: Hitbox
var hitbox_shape: CollisionShape3D
var hurtbox: Hurtbox
var hpbar: EnemyHealthBar

func setup(enemy_id: String) -> void:
	id = enemy_id
	cfg = DB.enemy(id)

func _ready() -> void:
	if cfg.is_empty():
		cfg = DB.enemy(id)
	add_to_group("targetable")
	add_to_group(VG.GROUP_ENEMIES)
	collision_layer = 1 << (VG.L_ENEMY - 1)
	collision_mask = VG.M_WORLD_ALL | (1 << (VG.L_PLAYER - 1)) | (1 << (VG.L_ENEMY - 1))
	max_hp = float(cfg.get("hp", 50))
	hp = max_hp
	poise = float(cfg.get("poise", 30))
	home = global_position

	var cs := CollisionShape3D.new()
	var cap := CapsuleShape3D.new()
	cap.radius = float(cfg.get("col_r", 0.4))
	cap.height = maxf(float(cfg.get("hurt_h", 1.6)), 1.2)
	cs.shape = cap
	cs.position.y = cap.height * 0.5 + 0.05
	add_child(cs)

	vis = EnemyVisual.new()
	vis.name = "Vis"
	add_child(vis)
	vis.build(cfg)

	agent = NavigationAgent3D.new()
	agent.radius = float(cfg.get("col_r", 0.4))
	agent.path_desired_distance = 0.6
	agent.target_desired_distance = 1.2
	agent.path_max_distance = 3.0
	add_child(agent)

	hurtbox = Hurtbox.new()
	hurtbox.team = "enemy"
	var hcs := CollisionShape3D.new()
	var cyl := CylinderShape3D.new()
	cyl.radius = float(cfg.get("hurt_r", 0.45))
	cyl.height = float(cfg.get("hurt_h", 1.6))
	hcs.shape = cyl
	hcs.position.y = cyl.height * 0.5
	hurtbox.add_child(hcs)
	add_child(hurtbox)

	hitbox = Hitbox.new()
	hitbox.exclude = self
	hitbox_shape = CollisionShape3D.new()
	hitbox_shape.shape = BoxShape3D.new()
	hitbox.add_child(hitbox_shape)
	vis.add_child(hitbox)
	hitbox.on_contact = _on_hit_contact

	# floating health bar for regular foes; bosses ride the big HUD bar instead
	if not cfg.get("is_boss", false):
		hpbar = EnemyHealthBar.new()
		hpbar.name = "HPBar"
		add_child(hpbar)
		var vs := float(cfg.get("vis_scale", 1.0))
		hpbar.build(clampf(float(cfg.get("hurt_r", 0.45)) * 2.6, 0.7, 1.7))
		hpbar.position.y = maxf(float(cfg.get("hurt_h", 1.6)), 1.2) * vs + 0.42
		hpbar.set_ratio(1.0)

func _physics_process(dt: float) -> void:
	if dead:
		return
	state_t += dt
	if hpbar != null:
		hpbar.set_forced(_is_locked_target())
	if not is_on_floor():
		velocity.y -= 22.0 * dt
	match state:
		ES.IDLE: _st_idle(dt)
		ES.ALERT: _st_alert(dt)
		ES.APPROACH: _st_approach(dt)
		ES.COMBAT: _st_combat(dt)
		ES.ATTACK: _st_attack(dt)
		ES.STAGGER: _st_stagger(dt)
	move_and_slide()
	# stride cycles while moving; action clips own the rig during ATTACK/STAGGER
	vis.locomotion(dt, Vector2(velocity.x, velocity.z).length(), Vector2.ZERO, is_on_floor())

func _set_state(s: ES) -> void:
	state = s
	state_t = 0.0

func _player() -> Node3D:
	return Game.player

func _can_see(p: Node3D) -> bool:
	var to := p.global_position - global_position
	if to.length() > float(cfg.get("aggro_sight", 10)):
		return false
	var fwd := -vis.global_transform.basis.z
	var half_fov: float = deg_to_rad(float(cfg.get("aggro_fov", 120)) * 0.5)
	if to.length() > float(cfg.get("aggro_hear", 4)) and fwd.angle_to(to.normalized()) > half_fov:
		return false
	# line of sight through world geometry
	var ray := PhysicsRayQueryParameters3D.create(
		global_position + Vector3.UP * 1.4, p.global_position + Vector3.UP * 1.0, VG.M_WORLD_ALL)
	return get_world_3d().direct_space_state.intersect_ray(ray).is_empty()

## Clear line of sight to the current target through world geometry — gates
## combat so foes never swing or fire through a wall. Cheap (one ray).
func _los_clear() -> bool:
	if target == null or not is_instance_valid(target):
		return false
	var ray := PhysicsRayQueryParameters3D.create(
		global_position + Vector3.UP * 1.4, target.global_position + Vector3.UP * 1.0, VG.M_WORLD_ALL)
	ray.exclude = [self]
	return get_world_3d().direct_space_state.intersect_ray(ray).is_empty()

func _face(dir: Vector3, dt: float, mult := 1.0) -> void:
	dir.y = 0
	if dir.length_squared() < 0.001:
		return
	var ty := atan2(-dir.x, -dir.z)
	vis.rotation.y = lerp_angle(vis.rotation.y, ty, 1.0 - exp(-float(cfg.get("turn", 5)) * mult * dt))

# ---------------------------------------------------------------- states
func _st_idle(dt: float) -> void:
	velocity.x = move_toward(velocity.x, 0, 8 * dt)
	velocity.z = move_toward(velocity.z, 0, 8 * dt)
	var p := _player()
	if p != null and not p.get("dead") and _can_see(p):
		target = p
		_set_state(ES.ALERT)
		if cfg.has("sfx_alert"):
			AudioDirector.sfx_at(cfg["sfx_alert"], global_position, -2.0, randf_range(0.9, 1.1))

func _st_alert(dt: float) -> void:
	_face(target.global_position - global_position, dt, 1.6)
	if state_t >= 0.42:
		_set_state(ES.APPROACH)

func _st_approach(dt: float) -> void:
	if not _target_valid():
		return
	var dist := global_position.distance_to(target.global_position)
	if global_position.distance_to(home) > float(cfg.get("leash", 30)):
		target = null
		_set_state(ES.IDLE)
		return
	if dist <= _max_attack_range() * 0.9 and _los_clear():
		_set_state(ES.COMBAT)
		return
	agent.target_position = target.global_position
	var next := agent.get_next_path_position()
	var dir := (next - global_position)
	dir.y = 0
	dir = dir.normalized()
	var sp := float(cfg.get("speed", 2.5))
	velocity.x = move_toward(velocity.x, dir.x * sp, 10 * dt * sp)
	velocity.z = move_toward(velocity.z, dir.z * sp, 10 * dt * sp)
	_face(dir, dt)

func _st_combat(dt: float) -> void:
	if not _target_valid():
		return
	var to := target.global_position - global_position
	var dist := to.length()
	_face(to, dt, 1.4)
	# tick cooldowns
	for k in _cooldowns:
		_cooldowns[k] = maxf(0.0, _cooldowns[k] - dt)
	_think_t -= dt
	if dist > _max_attack_range() * 1.25:
		_set_state(ES.APPROACH)
		return
	# a wall came between us — close in instead of swinging through it
	if not _los_clear():
		_set_state(ES.APPROACH)
		return
	# choose an attack that's off cooldown and in range
	var pick := _pick_attack(dist)
	if not pick.is_empty():
		_begin_attack(pick)
		return
	# reposition: slow strafe + keep spacing (singers back away instead)
	if _think_t <= 0.0:
		_think_t = randf_range(0.8, 1.6)
		_strafe_dir = -_strafe_dir if randf() < 0.4 else _strafe_dir
		_blocking = cfg.has("block_arc") and randf() < 0.45
	var fwd := to.normalized()
	var side := fwd.cross(Vector3.UP) * _strafe_dir
	var keep := float(cfg.get("keep_range", 0.0))
	var closing := clampf(dist - 2.0, -0.8, 0.7)
	if keep > 0.0:
		closing = clampf(dist - keep, -1.6, 0.5)
	var want := side * 1.1 + fwd * closing
	velocity.x = move_toward(velocity.x, want.x * float(cfg.get("speed", 2.5)) * 0.55, 6 * dt)
	velocity.z = move_toward(velocity.z, want.z * float(cfg.get("speed", 2.5)) * 0.55, 6 * dt)

func _target_valid() -> bool:
	if target == null or not is_instance_valid(target) or target.get("dead") == true:
		target = null
		_set_state(ES.IDLE)
		return false
	return true

func _max_attack_range() -> float:
	var m := 0.0
	for a in cfg.get("attacks", []):
		if a.get("phase2_only", false) and phase < 2:
			continue
		m = maxf(m, float(a.get("range", 2)))
	return m

func _pick_attack(dist: float) -> Dictionary:
	var pool: Array = []
	for a in cfg.get("attacks", []):
		if a.get("phase2_only", false) and phase < 2:
			continue
		if dist <= float(a.get("range", 2)) and _cooldowns.get(a["id"], 0.0) <= 0.0:
			pool.append(a)
	if pool.is_empty():
		return {}
	return pool[randi() % pool.size()]

## Where each attack clip's CONTACT beat sits (fraction of its 1.0 s length).
## The clip is played at a speed that lands that beat exactly when the hitbox
## opens (end of windup) — before this, clips ran at their authored duration
## while damage followed the data windup, so slow attacks (the Bellkeeper's
## 1.1-1.5 s slams) visibly struck half a second before the damage arrived.
const _CONTACT := {"atk_r": 0.56, "atk_thrust": 0.58, "atk_over": 0.58,
		"atk_back": 0.5, "atk_spin": 0.5, "atk_double": 0.56}

func _begin_attack(a: Dictionary) -> void:
	_atk = a
	_atk_done = false
	_blocking = false
	_cooldowns[a["id"]] = float(a.get("cooldown", 2.0))
	_set_state(ES.ATTACK)
	var speed_mult := 1.35 if phase >= 2 else 1.0
	var anim_name: String = a.get("anim", "atk_r")
	var w := float(a.get("windup", 0.5)) / speed_mult
	var contact := float(_CONTACT.get(anim_name, 0.56))
	vis.play(anim_name, 0.08, contact / maxf(w, 0.05))
	AudioDirector.sfx_at("res://assets/audio/whoosh_h.wav", global_position, -10.0, 0.8)

func _st_attack(dt: float) -> void:
	var speed_mult := 1.35 if phase >= 2 else 1.0
	var w: float = float(_atk["windup"]) / speed_mult
	var act: float = float(_atk["active"]) / speed_mult
	var rec: float = float(_atk["recover"]) / speed_mult
	var t := state_t
	# track the player through most of the windup, commit at the end
	if t < w * 0.7 and _target_valid():
		_face(target.global_position - global_position, dt, 1.2)
	if t >= w and t < w + act:
		var fwd := -vis.global_transform.basis.z
		var lunge := float(_atk.get("lunge", 1.5))
		velocity.x = fwd.x * lunge
		velocity.z = fwd.z * lunge
	else:
		velocity.x = move_toward(velocity.x, 0, 14 * dt)
		velocity.z = move_toward(velocity.z, 0, 14 * dt)
	if not _atk_done and t >= w:
		_atk_done = true
		match _atk.get("type", "melee"):
			"ranged": _fire_projectiles()
			"summon": _summon()
			_: _open_hitbox()
		if _atk.has("shockwave"):
			_shockwave.call_deferred(float(_atk["shockwave"]))
	if _atk_done and t >= w + act and hitbox.monitoring:
		hitbox.end_swing()
	if t >= w + act + rec:
		_set_state(ES.COMBAT)
		vis.idle()

func _open_hitbox() -> void:
	var reach := float(_atk.get("reach", 1.8))
	(hitbox_shape.shape as BoxShape3D).size = Vector3(float(_atk.get("width", 1.8)),
			float(_atk.get("height", 1.5)), reach)
	hitbox.position = Vector3(0, float(cfg.get("arm_h", 1.2)) * 0.9, -reach * 0.5 - 0.3)
	var pk := DamagePacket.new(float(_atk.get("dmg", 10)), float(_atk.get("poise_dmg", 10)), self)
	hitbox.begin_swing(pk)

## Ranged attacks sing projectiles: count/spread fan, aimed at the player's
## chest with light lead so strafing matters but walking works.
func _fire_projectiles() -> void:
	if not _target_valid():
		return
	var from := global_position + Vector3.UP * (float(cfg.get("arm_h", 1.3)) * float(cfg.get("vis_scale", 1.0)))
	from += -vis.global_transform.basis.z * 0.5
	var aim: Vector3 = target.global_position + Vector3.UP * 1.0
	if target is CharacterBody3D:
		aim += Vector3((target as CharacterBody3D).velocity.x, 0, (target as CharacterBody3D).velocity.z) * 0.22
	var dir := (aim - from).normalized()
	var count := int(_atk.get("count", 1))
	var spread := deg_to_rad(float(_atk.get("spread_deg", 14)))
	for i in count:
		var off := 0.0 if count == 1 else lerpf(-spread, spread, float(i) / float(count - 1))
		var d := dir.rotated(Vector3.UP, off)
		var pk := DamagePacket.new(float(_atk.get("dmg", 12)), float(_atk.get("poise_dmg", 8)), self)
		pk.can_be_parried = false
		# per-attack tint (the Larkwarden's song-rings burn gold; default choir-blue)
		var pc = _atk.get("proj_color", null)
		var tint := Color(0.62, 0.75, 1.0) if pc == null else Color(pc[0], pc[1], pc[2])
		Projectile.launch(get_parent(), from, d, float(_atk.get("proj_speed", 9.0)), pk, tint)
	AudioDirector.sfx_at(cfg.get("sfx_cast", "res://assets/audio/whoosh_l.wav"),
			global_position, -8.0, 1.4)

## Summons: raise minions around the caster, capped alive.
var _minions: Array = []

func _summon() -> void:
	_minions = _minions.filter(func(m): return is_instance_valid(m) and not m.dead)
	var max_alive := int(_atk.get("max_alive", 2))
	var want := int(_atk.get("count", 2))
	var placed := 0
	for i in want:
		if _minions.size() >= max_alive:
			break
		var e := Enemy.new()
		e.setup(_atk.get("enemy", "chorister"))
		get_parent().add_child(e)
		var a := TAU * float(i) / float(want) + randf() * 0.8
		e.global_position = global_position + Vector3(cos(a) * 2.6, 0.1, sin(a) * 2.6)
		e.target = target
		e._set_state(ES.ALERT)
		_minions.append(e)
		placed += 1
	if placed > 0:
		Juice.shake(0.3, 0.3)
		AudioDirector.sfx_at(cfg.get("sfx_alert", ""), global_position, -4.0, 1.3)

func _shockwave(radius: float) -> void:
	# ring burst on slam attacks (boss): damages if close to ground zero
	await get_tree().create_timer(0.05, false).timeout
	var p := _player()
	if p != null and not p.get("dead"):
		var d := global_position.distance_to(p.global_position)
		if d < radius and p.has_method("take_hit"):
			var hb: Hurtbox = p.get("hurtbox")
			var pk := DamagePacket.new(float(_atk.get("dmg", 20)) * 0.7, 20.0, self)
			pk.can_be_parried = false
			if hb != null:
				hb.receive(pk)
	_ring_vfx(radius)
	Juice.shake(0.5, 0.3)
	AudioDirector.sfx_at("res://assets/audio/bell_toll.wav", global_position, -2.0, 1.2)

func _ring_vfx(radius: float) -> void:
	var p := CPUParticles3D.new()
	p.amount = 160
	p.lifetime = 0.7
	p.one_shot = true
	p.explosiveness = 1.0
	p.emission_shape = CPUParticles3D.EMISSION_SHAPE_RING
	p.emission_ring_axis = Vector3.UP
	p.emission_ring_radius = 0.8
	p.emission_ring_inner_radius = 0.6
	p.emission_ring_height = 0.1
	p.direction = Vector3.UP
	p.initial_velocity_min = 2.0
	p.initial_velocity_max = 4.0
	p.gravity = Vector3(0, -8, 0)
	p.scale_amount_min = 0.05
	p.scale_amount_max = 0.16
	var mesh := SphereMesh.new()
	mesh.radius = 0.05
	mesh.height = 0.1
	var mm := StandardMaterial3D.new()
	mm.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mm.albedo_color = Color(0.8, 0.85, 1.0)
	mesh.material = mm
	p.mesh = mesh
	get_parent().add_child(p)
	p.global_position = global_position + Vector3.UP * 0.2
	p.emitting = true
	get_tree().create_timer(1.6).timeout.connect(p.queue_free)

func _on_hit_contact(_hb: Area3D, result: String) -> void:
	if result == "hit":
		Juice.shake(0.28, 0.2)
	elif result == "parried":
		_stagger(1.6)

func _st_stagger(dt: float) -> void:
	velocity.x = move_toward(velocity.x, 0, 10 * dt)
	velocity.z = move_toward(velocity.z, 0, 10 * dt)
	if state_t >= float(cfg.get("stagger_time", 0.9)):
		_set_state(ES.COMBAT if target != null else ES.IDLE)
		vis.idle()

func _stagger(mult := 1.0) -> void:
	hitbox.end_swing()
	_set_state(ES.STAGGER)
	vis.play("stagger", 0.05, 1.0 / mult)

# ---------------------------------------------------------------- damage
func is_invulnerable() -> bool:
	return dead

func is_blocking_toward(from_pos: Vector3) -> bool:
	if not _blocking or not cfg.has("block_arc") or state == ES.ATTACK or state == ES.STAGGER:
		return false
	var to := from_pos - global_position
	to.y = 0
	var fwd := -vis.global_transform.basis.z
	return fwd.angle_to(to.normalized()) < deg_to_rad(float(cfg["block_arc"]) * 0.5)

func on_blocked_hit(_packet: DamagePacket) -> void:
	AudioDirector.sfx_at("res://assets/audio/impact_blocked.wav", global_position, -6.0)

func _is_locked_target() -> bool:
	var p := Game.player
	if p == null or not is_instance_valid(p):
		return false
	var rig = p.get("cam")
	return rig != null and rig.locked_target == self

func take_hit(packet: DamagePacket) -> void:
	if dead:
		return
	hp -= packet.amount
	poise -= packet.poise_damage
	if hpbar != null:
		hpbar.hit(hp / max_hp)
	# aggro on pain even if unseen
	if target == null and packet.source != null and packet.source.is_in_group("player"):
		target = packet.source
		if state == ES.IDLE:
			_set_state(ES.ALERT)
	if hp <= 0.0:
		_die()
		return
	if poise <= 0.0:
		poise = float(cfg.get("poise", 30))
		_stagger()
	if cfg.get("is_boss", false) and phase == 1 and hp <= max_hp * float(cfg.get("phase2_at", 0.5)):
		phase = 2
		_enrage()

func _enrage() -> void:
	_stagger(0.6)
	AudioDirector.sfx_at(cfg.get("sfx_alert", ""), global_position, 2.0, 0.85)
	Juice.shake(0.6, 0.6)

func receive_riposte(packet: DamagePacket) -> void:
	take_hit(packet)
	if not dead:
		_stagger(1.4)

func on_parried(_host) -> void:
	if cfg.get("is_boss", false):
		return   # bosses shrug parries; they stagger via poise only
	hitbox.end_swing()
	var p := _player()
	if p != null and p.has_method("on_parry_success"):
		p.on_parry_success(self)
	_stagger(1.8)

func _die() -> void:
	dead = true
	_set_state(ES.DEAD)
	if hpbar != null:
		hpbar.set_ratio(0.0)
		hpbar.dismiss()
	hitbox.end_swing()
	hurtbox.set_deferred("monitorable", false)
	collision_layer = 0
	vis.play("death", 0.06)
	Game.add_orisons(int(cfg.get("orisons", 10)))
	AudioDirector.sfx_at("res://assets/audio/impact_flesh.wav", global_position, -2.0, 0.7)
	died.emit(self)
	_fade_out.call_deferred()

func _fade_out() -> void:
	await get_tree().create_timer(2.6, false).timeout
	var t := 0.0
	while t < 1.2 and is_instance_valid(self):
		t += get_process_delta_time()
		_set_dissolve(t / 1.2)
		await get_tree().process_frame
	queue_free()

func _set_dissolve(v: float) -> void:
	var stack: Array[Node] = [vis]
	while not stack.is_empty():
		var n: Node = stack.pop_back()
		if n is GeometryInstance3D:
			(n as GeometryInstance3D).set_instance_shader_parameter("death_diss", v)
		for c in n.get_children():
			stack.append(c)
