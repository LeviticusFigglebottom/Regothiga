class_name Player
extends CharacterBody3D
## The Latecomer. Deliberate, stamina-gated soulslike controller.
## States are explicit; every action spends before it swings. Combat numbers
## come from data (game.json + weapons/movesets), visuals from PlayerVisual.

signal health_changed(hp: float, max_hp: float)
signal stamina_changed(st: float, max_st: float)
signal flasks_changed(n: int, max_n: int)
signal died
signal state_changed(s: int)
signal hit_landed(target, result: String)

enum S { MOVE, ROLL, BACKSTEP, ATTACK, BLOCK, PARRY, RIPOSTE, FLASK, STAGGER, REST, TALK, DEAD }

# --- attributes & derived -------------------------------------------------
var attributes := {"vitality": 8, "endurance": 8, "strength": 8, "grace": 8, "devotion": 8}
var level := 1
var max_hp := 100.0
var hp := 100.0
var max_stamina := 80.0
var stamina := 80.0
var max_poise := 30.0
var poise := 30.0
var flask_max := 3
var flasks := 3
var weapon_id := "cloistersword"
var weapon_level := 0
var inventory: Dictionary = {}    # item_id -> count

# --- state ------------------------------------------------------------------
var state: S = S.MOVE
var state_t := 0.0
var dead := false
var input_enabled := true
var _recap_cd := 0.0
## pointer-compat look: some machines (remote play, VMs, absolute-injected
## mice) never deliver RELATIVE motion to a captured window — m0 forever.
## Fallback: confine+hide the cursor, track its frame-to-frame movement in
## window pixels, warp it home only when it nears the rim. Auto-engages
## after 2.5 s of captured silence.
var look_compat := false
var _cap_dead_t := 0.0
var _cmp_last := Vector2(-1, -1)   # last cursor pos, WINDOW px; x<0 = resync
var _mo_n := 0           # motion events this window
var motion_rate := 0     # published events/second for the HUD diagnostics
var _mo_t := 0.0

# roll / iframes
var _iframe_from := 0.0
var _iframe_to := 0.0
var _roll_dir := Vector3.ZERO
var _roll_speed := 0.0

# attack
var _atk: Dictionary = {}
var _atk_is_heavy := false
var _combo_i := 0
var _atk_hit_open := false
var _queued: String = ""
var _lunge := 0.0

# blocking / parry
var _blocking := false
var _parry_from := 0.0
var _parry_to := 0.0

# regen bookkeeping
var _stam_delay := 0.0
var _poise_delay := 0.0

# riposte
var _riposte_target: Node3D = null

# out-of-bounds failsafe
var _last_ground := Vector3.ZERO

# brief interact lockout (in physics frames) so the key-press that closes a menu
# can't reopen it — only needs to outlast the closing press's one-frame bleed
var _interact_suppress := 0

var vis: PlayerVisual
var cam: CameraRig
var hitbox: Hitbox
var hitbox_shape: CollisionShape3D
var hurtbox: Hurtbox
var _interact_scan: Area3D

var sim_move := Vector3.ZERO      # sim driver writes camera-space intent here
var sim_active := false
var sim_block := false
var sim_sprint := false

@onready var T: Dictionary = DB.table("game")["player"]

func _ready() -> void:
	add_to_group("player")
	collision_layer = 1 << (VG.L_PLAYER - 1)
	collision_mask = VG.M_WORLD_ALL
	var cs := CollisionShape3D.new()
	var cap := CapsuleShape3D.new()
	cap.radius = 0.34
	cap.height = 1.65
	cs.shape = cap
	cs.position.y = 0.85
	add_child(cs)

	vis = PlayerVisual.new()
	vis.name = "Vis"
	add_child(vis)
	vis.build(DB.weapon(weapon_id).get("kit", "sword_cloister"))

	cam = CameraRig.new()
	cam.name = "CamRig"
	add_child(cam)

	hurtbox = Hurtbox.new()
	hurtbox.name = "Hurtbox"
	hurtbox.team = "player"
	var hcs := CollisionShape3D.new()
	var cyl := CylinderShape3D.new()
	cyl.radius = 0.38
	cyl.height = 1.6
	hcs.shape = cyl
	hcs.position.y = 0.85
	hurtbox.add_child(hcs)
	add_child(hurtbox)

	hitbox = Hitbox.new()
	hitbox.name = "Hitbox"
	hitbox.exclude = self
	hitbox.friendly_team = "player"   # a summoned comrade is never struck
	hitbox_shape = CollisionShape3D.new()
	hitbox_shape.shape = BoxShape3D.new()
	hitbox.add_child(hitbox_shape)
	vis.add_child(hitbox)
	hitbox.on_contact = _on_hit_contact

	_interact_scan = Area3D.new()
	_interact_scan.name = "InteractScan"
	_interact_scan.collision_layer = 0
	_interact_scan.collision_mask = 1 << (VG.L_INTERACT - 1)
	var ics := CollisionShape3D.new()
	var isph := SphereShape3D.new()
	isph.radius = 1.9
	ics.shape = isph
	ics.position.y = 0.9
	_interact_scan.add_child(ics)
	add_child(_interact_scan)

	recompute_derived()
	hp = max_hp
	stamina = max_stamina
	Game.register_player(self)
	_emit_all()
	look_compat = bool(PauseUI.settings.get("look_compat", false))
	if not sim_active:
		_grab_mouse(true)

func recompute_derived() -> void:
	var base: Dictionary = T["base"]
	var per: Dictionary = T["per_level"]
	max_hp = float(base["hp"]) + (attributes["vitality"] - 8) * float(per["vitality_hp"])
	max_stamina = float(base["stamina"]) + (attributes["endurance"] - 8) * float(per["endurance_stamina"])
	max_poise = float(base["poise"])

func _emit_all() -> void:
	health_changed.emit(hp, max_hp)
	stamina_changed.emit(stamina, max_stamina)
	flasks_changed.emit(flasks, flask_max)

# --------------------------------------------------------------- input
## The camera only receives relative motion reliably while the mouse is
## captured. Capture engages on the first click (a user gesture — required
## by browsers for pointer-lock), Esc frees the cursor, clicking back in
## recaptures it. The recapturing click is swallowed so it doesn't also swing.
func _grab_mouse(on: bool) -> void:
	if not on:
		Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	else:
		Input.mouse_mode = Input.MOUSE_MODE_CONFINED_HIDDEN if look_compat \
				else Input.MOUSE_MODE_CAPTURED

func _captured() -> bool:
	return Input.mouse_mode == Input.MOUSE_MODE_CAPTURED \
			or Input.mouse_mode == Input.MOUSE_MODE_CONFINED_HIDDEN

## Mouse-bound combat actions (LMB swing / RMB block) stay quiet while the
## cursor is free, so clicking back into the window doesn't also attack.
func _mouse_ok() -> bool:
	return sim_active or _captured()

## True while a modal owns the keys (vigil rest menu / dialogue) — the pause
## menu refuses to open over these; they close on their own terms.
func busy_in_menu() -> bool:
	return state == S.REST or state == S.TALK

## Mouse-look lives in _input (fires before any UI) so no Control can eat the
## motion. Guarded on capture + control so it never fires during menus/talk.
## Esc belongs to PauseUI (opening the menu frees the cursor; closing it
## recaptures) — clicking back into the window still reclaims after any
## other focus loss.
func _input(event: InputEvent) -> void:
	if sim_active:
		return
	if event is InputEventMouseMotion:
		_mo_n += 1
		# look works from relative motion even if the OS refuses the capture
		# grab (remote desktop, overlays): degraded but never dead. Menus and
		# dialogue still own the cursor.
		if input_enabled and not look_compat and (_captured() or (not PauseUI.is_open()
				and state != S.REST and state != S.TALK)):
			cam.mouse_look(event.relative)
		return
	if event is InputEventMouseButton and event.pressed and not _captured() \
			and not PauseUI.is_open():
		# reclaim the cursor; consume the click so it isn't also an attack
		_grab_mouse(true)
		get_viewport().set_input_as_handled()

# ------------------------------------------------------ dialogue control
## Talking freezes the Latecomer in a dedicated state so no action (least of
## all a re-interact) can fire. Control is restored one frame LATE on exit so
## the same keypress that closed the menu can't reopen it.
func enter_dialogue() -> void:
	input_enabled = false
	velocity = Vector3.ZERO
	_set_state(S.TALK)

func exit_dialogue() -> void:
	_finish_dialogue.call_deferred()

func _finish_dialogue() -> void:
	if state == S.TALK:
		_set_state(S.MOVE)
	input_enabled = true
	# standard reopen prevention: the press that closed the dialogue (or an
	# eager follow-up tap) must not immediately re-enter it
	suppress_interact(10)
	vis.back_to_idle()

func _move_input() -> Vector3:
	if sim_active:
		return sim_move
	var v := Input.get_vector("move_left", "move_right", "move_forward", "move_back")
	return Vector3(v.x, 0, v.y)

# --------------------------------------------------------------- physics
func _physics_process(dt: float) -> void:
	state_t += dt
	# capture watchdog: whenever the focused window should own the cursor and
	# doesn't — first frame after boot, alt-tab return, an OS quirk dropping
	# the grab — take it back. Interval-gated: on machines where capture is
	# refused outright, per-frame attempts would warp the pointer every frame.
	_mo_t += dt
	if _mo_t >= 1.0:
		motion_rate = _mo_n
		_mo_n = 0
		_mo_t = 0.0
	_recap_cd = maxf(0.0, _recap_cd - dt)
	var play_owns := not sim_active and not dead and input_enabled \
			and not PauseUI.is_open() and state != S.REST and state != S.TALK
	if play_owns and not _captured() and get_window().has_focus() and _recap_cd == 0.0:
		_grab_mouse(true)
		_recap_cd = 0.5
	# raw relative motion starved while captured -> engage pointer-compat look
	if play_owns and not look_compat and Input.mouse_mode == Input.MOUSE_MODE_CAPTURED \
			and get_window().has_focus():
		_cap_dead_t = 0.0 if (_mo_n > 0 or motion_rate > 0) else _cap_dead_t + dt
		if _cap_dead_t > 2.5:
			look_compat = true
			_grab_mouse(true)
	# compat look: frame-to-frame cursor movement is the look delta, all in
	# WINDOW pixels. Viewport coords are content-scaled and disagree with
	# warp_mouse's client pixels on a stretched/maximized window — mixing
	# the two spaces injected a phantom offset every frame (constant pitch
	# push + erratic yaw). The cursor roams an inner region and is only
	# warped home from the rim; after a warp we resync instead of trusting
	# it landed, since remote layers can apply warps a frame late.
	if look_compat and play_owns and _captured() and get_window().has_focus():
		var win := get_window()
		var c := Vector2(win.size) * 0.5
		var m := Vector2(DisplayServer.mouse_get_position() - win.position)
		var dmm := m - _cmp_last
		if _cmp_last.x >= 0.0 and dmm != Vector2.ZERO:
			cam.mouse_look(dmm)
		_cmp_last = m
		if absf(m.x - c.x) > c.x * 0.5 or absf(m.y - c.y) > c.y * 0.5:
			Input.warp_mouse(c)
			_cmp_last = Vector2(-1, -1)
	else:
		_cmp_last = Vector2(-1, -1)
	if _interact_suppress > 0:
		_interact_suppress -= 1
	if not is_on_floor():
		velocity.y -= 22.0 * dt
	else:
		velocity.y = maxf(velocity.y, -0.5)
		if state == S.MOVE and global_position.y > -20.0:
			_last_ground = global_position
	# failsafe: geometry should make this unreachable, but never fall forever
	if global_position.y < -25.0 and not dead:
		global_position = _last_ground + Vector3.UP * 0.6
		velocity = Vector3.ZERO
		hp = maxf(hp - max_hp * 0.25, 1.0)
		health_changed.emit(hp, max_hp)
		Juice.shake(0.4, 0.25)

	match state:
		S.MOVE: _st_move(dt)
		S.ROLL: _st_roll(dt)
		S.BACKSTEP: _st_backstep(dt)
		S.ATTACK: _st_attack(dt)
		S.BLOCK: _st_block(dt)
		S.PARRY: _st_parry(dt)
		S.RIPOSTE: _st_riposte(dt)
		S.FLASK: _st_flask(dt)
		S.STAGGER: _st_stagger(dt)
		S.REST, S.TALK, S.DEAD:
			velocity.x = move_toward(velocity.x, 0, 20 * dt)
			velocity.z = move_toward(velocity.z, 0, 20 * dt)

	_regen(dt)
	move_and_slide()
	_unwedge(dt)

	var gs := Vector2(velocity.x, velocity.z).length()
	var lean := Vector2.ZERO
	if state == S.MOVE:
		var lv := vis.global_transform.basis.inverse() * velocity
		lean = Vector2(lv.x, -lv.z) * 0.12
	# held poses (kneel at rest, death) must not blend back to idle
	if state != S.DEAD and state != S.REST and state != S.TALK:
		vis.locomotion(dt, gs, lean, is_on_floor())
	if not sim_active:
		cam.stick_look(Input.get_vector("cam_left", "cam_right", "cam_up", "cam_down"), dt)

func _set_state(s: S) -> void:
	state = s
	state_t = 0.0
	state_changed.emit(s)

# Safety net: convex prop colliders already prevent wedging, but if the
# player ever ends a frame DEEP inside a static body (spawn on a prop, a
# state-swap materializing geometry around them), push straight out. The
# depth gate keeps normal wall-resting (shallow contact) from triggering,
# so this never fights ordinary sliding.
var _wedge_t := 0.0
const _WEDGE_DEPTH := 0.12
func _unwedge(dt: float) -> void:
	if dead:
		return
	# zero-motion probe with recovery-as-collision reports a resting overlap
	var col := move_and_collide(Vector3.ZERO, true, 0.001, true)
	if col == null or col.get_depth() <= _WEDGE_DEPTH:
		_wedge_t = 0.0
		return
	_wedge_t += dt
	if _wedge_t < 0.2:
		return
	# resolve it fully this frame: push out along each contact normal
	for _i in 8:
		var c := move_and_collide(Vector3.ZERO, true, 0.001, true)
		if c == null or c.get_depth() <= _WEDGE_DEPTH:
			break
		var n := c.get_normal()
		n.y = 0.0
		if n.length_squared() < 0.01:
			n = (global_position - c.get_position()) * Vector3(1, 0, 1)
		if n.length_squared() < 0.001:
			n = Vector3(0.3, 0, 0.3)   # truly ambiguous — nudge diagonally
		global_position += n.normalized() * maxf(c.get_depth(), 0.15)
	velocity = Vector3.ZERO
	_wedge_t = 0.0

func _face(dir: Vector3, dt: float, speed := 11.0) -> void:
	if dir.length_squared() < 0.0001:
		return
	var target := atan2(-dir.x, -dir.z)
	vis.rotation.y = lerp_angle(vis.rotation.y, target, 1.0 - exp(-speed * dt))

func _desired_dir() -> Vector3:
	var mi := _move_input()
	if mi.length_squared() < 0.0001:
		return Vector3.ZERO
	return (cam.move_basis() * Vector3(mi.x, 0, mi.z)).normalized()

func _spend(amount: float) -> void:
	stamina = maxf(stamina - amount, 0.0)
	_stam_delay = float(T["stamina"]["regen_delay"])
	stamina_changed.emit(stamina, max_stamina)

func _regen(dt: float) -> void:
	# stamina
	if _stam_delay > 0.0:
		_stam_delay -= dt
	elif stamina < max_stamina and state != S.ROLL and state != S.ATTACK and state != S.RIPOSTE:
		var mult: float = float(T["stamina"]["regen_block_mult"]) if _blocking else 1.0
		stamina = minf(stamina + float(T["stamina"]["regen"]) * mult * dt, max_stamina)
		stamina_changed.emit(stamina, max_stamina)
	# poise
	if _poise_delay > 0.0:
		_poise_delay -= dt
	elif poise < max_poise:
		poise = minf(poise + float(T["poise_regen"]) * dt, max_poise)

# --------------------------------------------------------------- states
func _st_move(dt: float) -> void:
	if not input_enabled:
		velocity.x = move_toward(velocity.x, 0, 20 * dt)
		velocity.z = move_toward(velocity.z, 0, 20 * dt)
		return
	var dir := _desired_dir()
	if sim_active and sim_block and not _blocking:
		_enter_block()
		return
	var sprinting: bool = _pressed("sprint") and dir != Vector3.ZERO and stamina > 1.0 and cam.locked_target == null
	var mv: Dictionary = T["move"]
	var speed: float = float(mv["run"])
	if sprinting:
		speed = float(mv["sprint"])
		_spend(float(T["stamina"]["sprint_cost"]) * dt)
	elif cam.locked_target != null:
		speed = float(mv["strafe"]) * 1.35
	cam.set_sprinting(sprinting, dt)

	var acc: float = float(mv["accel"])
	velocity.x = move_toward(velocity.x, dir.x * speed, acc * dt * speed)
	velocity.z = move_toward(velocity.z, dir.z * speed, acc * dt * speed)

	if cam.locked_target != null and is_instance_valid(cam.locked_target):
		_face(cam.locked_target.global_position - global_position, dt)
	else:
		_face(dir, dt)

	if not sim_active:
		if Input.is_action_just_pressed("dodge"):
			_try_roll(dir)
		elif Input.is_action_just_pressed("attack_light") and _mouse_ok():
			if _pressed("sprint"):
				try_attack(false)  # sprint attack folded into light for pass 1
			else:
				try_attack(false)
		elif Input.is_action_just_pressed("attack_heavy"):
			try_attack(true)
		elif Input.is_action_just_pressed("parry"):
			try_parry()
		elif Input.is_action_pressed("block") and _mouse_ok():
			_enter_block()
		elif Input.is_action_just_pressed("flask"):
			try_flask()
		elif Input.is_action_just_pressed("interact"):
			try_interact()
		elif Input.is_action_just_pressed("lock_on"):
			cam.try_lock(get_tree().get_nodes_in_group("targetable"))

func try_roll() -> bool:
	return _try_roll(_desired_dir())

func _try_roll(dir: Vector3) -> bool:
	var cost := float(T["stamina"]["roll_cost"])
	if stamina < 1.0 or dead:
		return false
	var R: Dictionary = T["roll"]
	_spend(cost)
	if dir == Vector3.ZERO:
		# neutral backstep
		_set_state(S.BACKSTEP)
		_roll_dir = vis.global_transform.basis.z    # backwards
		_roll_speed = float(R["backstep_speed"])
		_iframe_from = float(R["backstep_iframe_start"])
		_iframe_to = float(R["backstep_iframe_end"])
		vis.play("backstep", 0.05)
		return true
	_set_state(S.ROLL)
	_roll_dir = dir.normalized()
	_roll_speed = float(R["speed"])
	_iframe_from = float(R["iframe_start"])
	_iframe_to = float(R["iframe_end"])
	vis.rotation.y = atan2(-_roll_dir.x, -_roll_dir.z)
	vis.play("roll", 0.03, float(vis.anim.get_animation("roll").length) / float(R["duration"]))
	AudioDirector.sfx_at("res://assets/audio/roll.wav", global_position, -6.0, randf_range(0.95, 1.05))
	return true

func _st_roll(dt: float) -> void:
	var R: Dictionary = T["roll"]
	var dur := float(R["duration"])
	var k := 1.0 - smoothstep(0.55, 1.0, state_t / dur) * 0.85
	velocity.x = _roll_dir.x * _roll_speed * k
	velocity.z = _roll_dir.z * _roll_speed * k
	if state_t >= dur:
		_set_state(S.MOVE)
		vis.back_to_idle()

func _st_backstep(dt: float) -> void:
	var R: Dictionary = T["roll"]
	var dur := float(R["backstep_duration"])
	var k := 1.0 - smoothstep(0.3, 1.0, state_t / dur)
	velocity.x = _roll_dir.x * _roll_speed * k
	velocity.z = _roll_dir.z * _roll_speed * k
	if state_t >= dur:
		_set_state(S.MOVE)
		vis.back_to_idle()

func is_invulnerable() -> bool:
	if state == S.ROLL or state == S.BACKSTEP:
		return state_t >= _iframe_from and state_t <= _iframe_to
	return state == S.REST or dead

# --- attacks ---------------------------------------------------------------
func weapon_data() -> Dictionary:
	return DB.weapon(weapon_id)

func _attack_damage(mult: float) -> float:
	var w := weapon_data()
	var scal: Dictionary = w.get("scaling", {})
	var s: float = 1.0 + attributes["strength"] * float(scal.get("strength", 0.0)) * 0.02 \
			+ attributes["grace"] * float(scal.get("grace", 0.0)) * 0.02
	var up := 1.0 + 0.14 * weapon_level
	return float(w.get("damage", 10)) * s * up * mult

func try_attack(heavy: bool) -> bool:
	if dead:
		return false
	if state == S.ATTACK:
		# queue combo link during recovery
		_queued = "heavy" if heavy else "light"
		return false
	if state != S.MOVE and state != S.BLOCK:
		return false
	return _chain_attack(heavy)

## Starts a swing regardless of current attack state (combo links use this).
func _chain_attack(heavy: bool) -> bool:
	var w := weapon_data()
	var cost: float = float(w["stamina"]["heavy" if heavy else "light"])
	if stamina < 1.0:
		return false
	var ms := DB.moveset(w.get("moveset", "longsword"))
	var m: Dictionary
	if heavy:
		m = ms["heavy"]
	else:
		var lights: Array = ms["lights"]
		_combo_i = _combo_i % lights.size()
		m = lights[_combo_i]
	_spend(cost)
	_begin_attack(m, heavy)
	return true

func _begin_attack(m: Dictionary, heavy: bool) -> void:
	_atk = m
	_atk_is_heavy = heavy
	_atk_hit_open = false
	_queued = ""
	_blocking = false
	_set_state(S.ATTACK)
	# face lock target or input dir instantly-ish
	var dir := _desired_dir()
	if cam.locked_target != null and is_instance_valid(cam.locked_target):
		dir = cam.locked_target.global_position - global_position
	if dir != Vector3.ZERO:
		vis.rotation.y = atan2(-dir.x, -dir.z)
	_lunge = float(m.get("lunge", 2.0))
	vis.play(m.get("anim", "attack_l1"), 0.05)
	AudioDirector.sfx_at("res://assets/audio/whoosh_h.wav" if heavy else "res://assets/audio/whoosh_l.wav",
			global_position, -8.0, randf_range(0.92, 1.08))

func _st_attack(dt: float) -> void:
	var wind := float(_atk["windup"])
	var act := float(_atk["active"])
	var rec := float(_atk["recovery"])
	var t := state_t
	# lunge through the active window
	if t >= wind and t < wind + act + 0.05:
		var fwd := -vis.global_transform.basis.z
		velocity.x = fwd.x * _lunge
		velocity.z = fwd.z * _lunge
	else:
		velocity.x = move_toward(velocity.x, 0, 26 * dt)
		velocity.z = move_toward(velocity.z, 0, 26 * dt)

	if not _atk_hit_open and t >= wind:
		_atk_hit_open = true
		_open_hitbox(_atk)
		vis.trail.visible = true
	if _atk_hit_open and t >= wind + act and hitbox.monitoring:
		hitbox.end_swing()
		vis.trail.visible = false

	# combo input capture during recovery
	if not sim_active and t > wind + act:
		if Input.is_action_just_pressed("attack_light") and _mouse_ok():
			_queued = "light"
		elif Input.is_action_just_pressed("attack_heavy"):
			_queued = "heavy"
		elif Input.is_action_just_pressed("dodge"):
			_queued = "roll"

	var total := wind + act + rec
	var chain_at := wind + act + rec * float(_atk.get("chain_from", 0.6))
	if t >= chain_at and _queued != "":
		var q := _queued
		_queued = ""
		hitbox.end_swing()
		match q:
			"light":
				_combo_i += 1
				if not _chain_attack(false):
					_set_state(S.MOVE)
			"heavy":
				if not _chain_attack(true):
					_set_state(S.MOVE)
			"roll":
				_combo_i = 0
				if not _try_roll(_desired_dir()):
					_set_state(S.MOVE)
		return
	if t >= total:
		_combo_i = 0
		hitbox.end_swing()
		vis.trail.visible = false
		_set_state(S.MOVE)
		vis.back_to_idle()

func _open_hitbox(m: Dictionary) -> void:
	var hb: Dictionary = m.get("hitbox", {})
	var reach := float(hb.get("reach", 1.7))
	var width := float(hb.get("width", 1.8))
	var height := float(hb.get("height", 1.5))
	(hitbox_shape.shape as BoxShape3D).size = Vector3(width, height, reach)
	hitbox.position = Vector3(0, 1.1, -reach * 0.5 - 0.2)
	var pk := DamagePacket.new(_attack_damage(float(m.get("dmg_mult", 1.0))),
			float(weapon_data().get("poise_damage", 20)) * float(m.get("poise_mult", 1.0)), self)
	pk.origin = global_position
	hitbox.begin_swing(pk)

func _on_hit_contact(_hb: Area3D, result: String) -> void:
	hit_landed.emit(_hb.owner, result)
	match result:
		"hit":
			Juice.hitstop(0.09 if _atk_is_heavy else 0.06)
			Juice.shake(0.35 if _atk_is_heavy else 0.2, 0.18)
			AudioDirector.sfx_at("res://assets/audio/impact_flesh.wav", global_position, -4.0, randf_range(0.9, 1.1))
		"blocked":
			Juice.hitstop(0.05)
			AudioDirector.sfx_at("res://assets/audio/impact_blocked.wav", global_position, -4.0)
		"parried":
			pass  # on_parried() handles our stagger

# --- block / parry ----------------------------------------------------------
func _enter_block() -> void:
	if stamina <= 0.0:
		return
	_blocking = true
	_set_state(S.BLOCK)
	vis.play("block", 0.08)

func _st_block(dt: float) -> void:
	if not input_enabled or not _pressed("block"):
		_blocking = false
		_set_state(S.MOVE)
		vis.back_to_idle()
		return
	var dir := _desired_dir()
	var mv: Dictionary = T["move"]
	velocity.x = move_toward(velocity.x, dir.x * float(mv["strafe"]), 10 * dt * float(mv["strafe"]))
	velocity.z = move_toward(velocity.z, dir.z * float(mv["strafe"]), 10 * dt * float(mv["strafe"]))
	if cam.locked_target != null and is_instance_valid(cam.locked_target):
		_face(cam.locked_target.global_position - global_position, dt)
	elif dir != Vector3.ZERO:
		_face(dir, dt, 6.0)
	if not sim_active:
		if Input.is_action_just_pressed("attack_light") and _mouse_ok():
			try_attack(false)
		elif Input.is_action_just_pressed("parry"):
			try_parry()
		elif Input.is_action_just_pressed("dodge"):
			_blocking = false
			_try_roll(dir)

func is_blocking_toward(from_pos: Vector3) -> bool:
	if not _blocking or stamina <= 0.0:
		return false
	var to := from_pos - global_position
	to.y = 0
	var fwd := -vis.global_transform.basis.z
	return fwd.angle_to(to.normalized()) < 1.15

func on_blocked_hit(packet: DamagePacket) -> void:
	var stab_cost: float = packet.amount * 0.85
	_spend(stab_cost)
	hp = maxf(hp - packet.amount * 0.14, 1.0)
	health_changed.emit(hp, max_hp)
	Juice.shake(0.18, 0.12)
	if stamina <= 0.0:
		_guard_break()

func _guard_break() -> void:
	_blocking = false
	_stagger(0.9)

func try_parry() -> bool:
	if dead or (state != S.MOVE and state != S.BLOCK):
		return false
	var P: Dictionary = T["parry"]
	_spend(float(P["stamina"]))
	_blocking = false
	_set_state(S.PARRY)
	_parry_from = float(P["windup"])
	_parry_to = float(P["windup"]) + float(P["window"])
	vis.play("parry", 0.03)
	return true

func _st_parry(dt: float) -> void:
	velocity.x = move_toward(velocity.x, 0, 16 * dt)
	velocity.z = move_toward(velocity.z, 0, 16 * dt)
	var P: Dictionary = T["parry"]
	if state_t >= _parry_to + float(P["recovery"]):
		_set_state(S.MOVE)
		vis.back_to_idle()

func is_parrying_toward(from_pos: Vector3) -> bool:
	if state != S.PARRY or state_t < _parry_from or state_t > _parry_to:
		return false
	var to := from_pos - global_position
	to.y = 0
	var fwd := -vis.global_transform.basis.z
	return fwd.angle_to(to.normalized()) < 1.0

## Called by an enemy when we parried them; they enter a punishable state.
func on_parry_success(enemy: Node3D) -> void:
	_riposte_target = enemy
	Juice.hitstop(0.14, 0.03)
	Juice.shake(0.4, 0.2)
	AudioDirector.sfx_at("res://assets/audio/parry.wav", global_position, 0.0)

## Riposte / backstab entry (crit states).
func try_riposte() -> bool:
	if _riposte_target == null or not is_instance_valid(_riposte_target):
		return false
	if global_position.distance_to(_riposte_target.global_position) > 2.4:
		return false
	if not _riposte_target.has_method("receive_riposte"):
		return false
	_set_state(S.RIPOSTE)
	var dir: Vector3 = _riposte_target.global_position - global_position
	vis.rotation.y = atan2(-dir.x, -dir.z)
	vis.play("riposte", 0.05)
	var target := _riposte_target
	_riposte_target = null
	_do_riposte_damage.call_deferred(target)
	return true

func _do_riposte_damage(target: Node3D) -> void:
	await get_tree().create_timer(0.34, false).timeout
	if is_instance_valid(target) and state == S.RIPOSTE:
		var pk := DamagePacket.new(_attack_damage(2.6), 999.0, self)
		pk.can_be_blocked = false
		pk.can_be_parried = false
		pk.is_riposte = true
		target.receive_riposte(pk)
		Juice.hitstop(0.12, 0.04)
		Juice.shake(0.5, 0.25)

func _st_riposte(dt: float) -> void:
	velocity.x = 0
	velocity.z = 0
	if state_t >= 0.9:
		_set_state(S.MOVE)
		vis.back_to_idle()

# --- flask -------------------------------------------------------------------
func try_flask() -> bool:
	if flasks <= 0 or dead or state != S.MOVE:
		return false
	flasks -= 1
	flasks_changed.emit(flasks, flask_max)
	_set_state(S.FLASK)
	vis.play("flask", 0.08)
	AudioDirector.sfx("res://assets/audio/flask.wav", -6.0)
	return true

func _st_flask(dt: float) -> void:
	velocity.x = move_toward(velocity.x, 0, 12 * dt)
	velocity.z = move_toward(velocity.z, 0, 12 * dt)
	var use_time := float(T["flask"]["use_time"])
	if state_t >= use_time * 0.62 and hp < max_hp and state_t - get_physics_process_delta_time() < use_time * 0.62:
		hp = minf(hp + float(T["flask"]["heal"]), max_hp)
		health_changed.emit(hp, max_hp)
	if state_t >= use_time:
		_set_state(S.MOVE)
		vis.back_to_idle()

# --- damage intake -----------------------------------------------------------
func take_hit(packet: DamagePacket) -> void:
	if dead:
		return
	hp = maxf(hp - packet.amount, 0.0)
	health_changed.emit(hp, max_hp)
	poise -= packet.poise_damage
	_poise_delay = 2.0
	Juice.shake(0.3, 0.2)
	AudioDirector.sfx_at("res://assets/audio/impact_flesh.wav", global_position, -6.0, 0.85)
	if hp <= 0.0:
		_die()
	elif poise <= 0.0:
		poise = max_poise
		_stagger(float(T["stagger_time"]))

func _stagger(dur: float) -> void:
	_set_state(S.STAGGER)
	_blocking = false
	hitbox.end_swing()
	vis.play("stagger", 0.03, 0.7 / maxf(dur, 0.2))

func _st_stagger(dt: float) -> void:
	velocity.x = move_toward(velocity.x, 0, 8 * dt)
	velocity.z = move_toward(velocity.z, 0, 8 * dt)
	if state_t >= float(T["stagger_time"]):
		_set_state(S.MOVE)
		vis.back_to_idle()

func _die() -> void:
	if dead:
		return
	dead = true
	_set_state(S.DEAD)
	hitbox.end_swing()
	vis.play("death", 0.1)
	AudioDirector.sfx("res://assets/audio/death.wav", 0.0, 1.0, "UI")
	died.emit()

## External control (rest ceremony, dialogue, respawn)
func lock_control(on: bool) -> void:
	input_enabled = not on
	if on:
		velocity = Vector3.ZERO

func enter_rest() -> void:
	_set_state(S.REST)
	vis.play("kneel", 0.2)

func exit_rest() -> void:
	_set_state(S.MOVE)
	vis.back_to_idle()

func revive_at(pos: Vector3) -> void:
	global_position = pos
	dead = false
	hp = max_hp
	stamina = max_stamina
	poise = max_poise
	flasks = flask_max
	velocity = Vector3.ZERO
	_set_state(S.MOVE)
	vis.play("RESET")
	vis.back_to_idle()
	_emit_all()

func heal_full() -> void:
	hp = max_hp
	flasks = flask_max
	_emit_all()

func _pressed(action: String) -> bool:
	if sim_active:
		match action:
			"block": return sim_block
			"sprint": return sim_sprint
		return false
	if action == "block" and not _mouse_ok():
		return false
	return input_enabled and Input.is_action_pressed(action)

# --- interaction ---------------------------------------------------------------
func nearest_interactable() -> Interactable:
	var best: Interactable = null
	var best_d := INF
	for a in _interact_scan.get_overlapping_areas():
		if a is Interactable and (a as Interactable).enabled:
			var d := global_position.distance_squared_to((a as Interactable).zone_global())
			if d < best_d:
				best_d = d
				best = a
	return best

## Suppress interaction for a few frames. Menus call this as they close so the
## same key-press that dismissed them can't immediately re-activate the prop —
## it only has to outlast that press's one-frame just_pressed bleed.
func suppress_interact(frames := 3) -> void:
	_interact_suppress = maxi(_interact_suppress, frames)

func try_interact() -> bool:
	if state != S.MOVE or _interact_suppress > 0:
		return false
	if _riposte_target != null and try_riposte():
		return true
	var it := nearest_interactable()
	if it == null:
		return false
	it.activate(self)
	return true

# --- save --------------------------------------------------------------------
func to_save() -> Dictionary:
	return {
		"attributes": attributes, "level": level, "flask_max": flask_max,
		"weapon": weapon_id, "weapon_level": weapon_level,
		"inventory": inventory,
		"pos": [global_position.x, global_position.y, global_position.z],
	}

func from_save(d: Dictionary) -> void:
	if d.is_empty():
		return
	for k in attributes:
		attributes[k] = int(d.get("attributes", {}).get(k, attributes[k]))
	level = int(d.get("level", 1))
	flask_max = int(d.get("flask_max", 3))
	weapon_id = d.get("weapon", "cloistersword")
	weapon_level = int(d.get("weapon_level", 0))
	inventory = d.get("inventory", {})
	recompute_derived()
	heal_full()
