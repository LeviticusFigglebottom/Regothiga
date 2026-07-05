class_name Projectile
extends Area3D
## A sung versicle / censer ember: slow, readable, dodgeable. Travels flat,
## hits the first opposing hurtbox, dies on world geometry or timeout.
## Blockable, never parryable.

var packet: DamagePacket
var velocity := Vector3.ZERO
var team := "enemy"
var _ttl := 6.0

static func launch(parent: Node, from: Vector3, dir: Vector3, speed: float,
		pk: DamagePacket, color := Color(0.62, 0.75, 1.0)) -> Projectile:
	var p := Projectile.new()
	p.packet = pk
	p.velocity = dir.normalized() * speed
	parent.add_child(p)
	p.global_position = from
	p._dress(color)
	return p

func _init() -> void:
	collision_layer = 0
	collision_mask = 1 << (VG.L_HURTBOX - 1)
	monitorable = false
	area_entered.connect(_on_area)
	var cs := CollisionShape3D.new()
	var sph := SphereShape3D.new()
	sph.radius = 0.22
	cs.shape = sph
	add_child(cs)

func _dress(color: Color) -> void:
	var mi := MeshInstance3D.new()
	var m := SphereMesh.new()
	m.radius = 0.14
	m.height = 0.28
	var mat := StandardMaterial3D.new()
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.albedo_color = color
	mat.emission_enabled = true
	mat.emission = color
	mat.emission_energy_multiplier = 2.4
	m.material = mat
	mi.mesh = m
	add_child(mi)
	var l := OmniLight3D.new()
	l.light_color = color
	l.light_energy = 1.4
	l.omni_range = 3.5
	l.shadow_enabled = false
	add_child(l)
	var tr := CPUParticles3D.new()
	tr.amount = 26
	tr.lifetime = 0.5
	tr.local_coords = false
	tr.direction = Vector3.ZERO
	tr.spread = 180.0
	tr.gravity = Vector3.ZERO
	tr.initial_velocity_min = 0.05
	tr.initial_velocity_max = 0.3
	tr.scale_amount_min = 0.02
	tr.scale_amount_max = 0.05
	var q := QuadMesh.new()
	q.size = Vector2(0.16, 0.16)
	var qm := StandardMaterial3D.new()
	qm.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	qm.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	qm.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	qm.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED
	qm.albedo_color = Color(color, 0.5)
	q.material = qm
	tr.mesh = q
	add_child(tr)

func _physics_process(dt: float) -> void:
	_ttl -= dt
	if _ttl <= 0.0:
		queue_free()
		return
	var from := global_position
	var to := from + velocity * dt
	# die on world geometry
	var ray := PhysicsRayQueryParameters3D.create(from, to, VG.M_WORLD_ALL)
	var hit := get_world_3d().direct_space_state.intersect_ray(ray)
	if not hit.is_empty():
		_poof(hit["position"])
		return
	global_position = to

func _on_area(a: Area3D) -> void:
	if packet == null or not (a is Hurtbox):
		return
	if (a as Hurtbox).team == team:
		return
	packet.origin = global_position - velocity   # block test faces the flight
	var result := (a as Hurtbox).receive(packet)
	if result != "immune":
		_poof(global_position)

func _poof(at: Vector3) -> void:
	set_deferred("monitoring", false)
	packet = null
	velocity = Vector3.ZERO
	var burst := CPUParticles3D.new()
	burst.amount = 30
	burst.lifetime = 0.4
	burst.one_shot = true
	burst.explosiveness = 1.0
	burst.spread = 180.0
	burst.initial_velocity_min = 1.0
	burst.initial_velocity_max = 2.6
	burst.gravity = Vector3.ZERO
	burst.scale_amount_min = 0.02
	burst.scale_amount_max = 0.06
	var q := QuadMesh.new()
	q.size = Vector2(0.14, 0.14)
	var qm := StandardMaterial3D.new()
	qm.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	qm.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	qm.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	qm.albedo_color = Color(0.7, 0.8, 1.0, 0.7)
	q.material = qm
	burst.mesh = q
	get_parent().add_child(burst)
	burst.global_position = at
	burst.emitting = true
	get_tree().create_timer(1.0).timeout.connect(burst.queue_free)
	AudioDirector.sfx_at("res://assets/audio/impact_blocked.wav", at, -14.0, 1.6)
	queue_free()
