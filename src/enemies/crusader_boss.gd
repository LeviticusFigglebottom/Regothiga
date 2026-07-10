class_name CrusaderBoss
extends Enemy
## The Immortalized — the parish's radiant knight, wearing the Latecomer's
## own frame. He fights like you: rolls through blows, raises his blade to
## turn them, backs off when pressed, and punishes a flask like an insult.
## At half his wax he stops, turns the point on himself, and gives his own
## memory to the flame — the church remembers itself around him, his armor
## goes to black and his blade to gold, and he hits the harder for it.

var _iframes := 0.0
var _dodge_cd := 0.0
var _block_t := 0.0
var _retreat_t := 0.0
var _hits_recent := 0.0
var _seppuku := false          # mid-rite: untouchable, unmoving
var _phase2 := false

func _ready() -> void:
	super()
	cfg = cfg.duplicate(true)   # phase 2 rewrites his damage; never the table's
	# he arrives as the kingdom kept him: radiant, not yet yours
	_tint.call_deferred(Color(1.0, 0.84, 0.5), Color(0.78, 0.8, 0.88))

func _physics_process(dt: float) -> void:
	_iframes = maxf(_iframes - dt, 0.0)
	_dodge_cd = maxf(_dodge_cd - dt, 0.0)
	_block_t = maxf(_block_t - dt, 0.0)
	_retreat_t = maxf(_retreat_t - dt, 0.0)
	_hits_recent = maxf(_hits_recent - dt * 0.4, 0.0)
	if _seppuku:
		velocity = Vector3.ZERO
		move_and_slide()
		return
	super(dt)

func _st_combat(dt: float) -> void:
	if target is Player:
		var pl := target as Player
		var dist := global_position.distance_to(pl.global_position)
		# roll through an incoming swing, the way you would
		if _iframes <= 0.0 and _dodge_cd <= 0.0 and pl.state == Player.S.ATTACK \
				and dist < 4.2 and randf() < float(cfg.get("dodge_chance", 0.45)):
			_do_roll(pl)
			return
		# or take it on the blade
		if _block_t <= 0.0 and pl.state == Player.S.ATTACK \
				and randf() < float(cfg.get("block_chance", 0.35)) * dt * 9.0:
			_block_t = 0.9
			vis.play("block", 0.08)
		# a mid-fight drink is an insult: every cooldown forgiven at once
		if pl.state == Player.S.FLASK:
			for k in _cooldowns:
				_cooldowns[k] = 0.0
	if _retreat_t > 0.0 and target != null:
		var away := global_position - target.global_position
		away.y = 0.0
		away = away.normalized()
		var sp := float(cfg.get("speed", 4.0)) * 0.85
		velocity.x = away.x * sp
		velocity.z = away.z * sp
		_face(-away, dt)
		move_and_slide()
		return
	super(dt)

func _do_roll(pl: Player) -> void:
	_dodge_cd = 2.0 + randf() * 1.6
	_iframes = 0.42
	var lat := (global_position - pl.global_position).cross(Vector3.UP).normalized()
	if randf() < 0.5:
		lat = -lat
	var back := (global_position - pl.global_position).normalized() * 0.6
	velocity = (lat + back).normalized() * 9.5
	vis.play("roll", 0.05)

func take_hit(packet: DamagePacket) -> void:
	if _seppuku or _iframes > 0.0:
		return
	if _block_t > 0.0 and packet.source is Node3D:
		var to := ((packet.source as Node3D).global_position - global_position).normalized()
		var fwd := -vis.global_transform.basis.z
		if fwd.dot(to) > 0.2:
			packet.amount *= 0.25
			packet.poise_damage *= 0.35
			AudioDirector.sfx_at("res://assets/audio/impact_blocked.wav", global_position, -4.0, 1.0)
	_hits_recent += 1.0
	if _hits_recent >= 3.0 and _retreat_t <= 0.0:
		_retreat_t = 1.5
		_hits_recent = 0.0
	super(packet)

## Half his wax: instead of raging he performs the rite. Untouchable while
## it runs; then the kindling.
func _enrage() -> void:
	if _phase2 or _seppuku:
		return
	_seppuku = true
	vis.play("block", 0.25)          # both hands find the hilt
	var tw := create_tween()
	tw.tween_interval(1.2)
	tw.tween_callback(func():
		vis.play("atk_thrust", 0.05, 0.65)
		AudioDirector.sfx_at("res://assets/audio/guard_break.wav", global_position, 0.0, 0.7)
		Juice.shake(0.4, 0.4))
	tw.tween_interval(1.5)
	tw.tween_callback(_kindle)

func _kindle() -> void:
	_phase2 = true
	_seppuku = false
	stagger_resist = 3.0
	hp = maxf(hp, max_hp * 0.5)
	for a in cfg.get("attacks", []):
		a["dmg"] = float(a["dmg"]) * 1.35
	WickReveal.radiance(Game.current_area)
	_tint(Color(0.13, 0.12, 0.15), Color(1.0, 0.85, 0.42))
	Juice.shake(0.8, 0.7)
	AudioDirector.sfx_at("res://assets/audio/swell_kindle.wav", global_position, 2.0, 0.75)

## Repaint the knight: armor to the Latecomer's black, blade to gold.
func _tint(armor: Color, blade: Color) -> void:
	_tint_under(vis.skel, armor)
	if vis.weapon_mount != null:
		_tint_under(vis.weapon_mount, blade)

func _tint_under(root: Node, c: Color) -> void:
	if root == null:
		return
	for n in root.find_children("*", "MeshInstance3D", true, false):
		var mi := n as MeshInstance3D
		if mi.mesh == null:
			continue
		for i in mi.mesh.get_surface_count():
			var m := mi.get_active_material(i)
			if m is ShaderMaterial:
				var d := (m as ShaderMaterial).duplicate()
				d.set_shader_parameter("albedo", c)
				mi.set_surface_override_material(i, d)
			elif m is StandardMaterial3D:
				var d2 := (m as StandardMaterial3D).duplicate()
				d2.albedo_color = c
				mi.set_surface_override_material(i, d2)
