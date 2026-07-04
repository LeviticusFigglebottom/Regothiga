class_name FogGate
extends Node3D
## The pale threshold before a warden. Ruin-layer entity: pass through to
## begin the fight; it seals at your back until the warden rests.

signal boss_engaged

var gate_id := "fog"
var area_id := ""
var boss_spawner: Spawner = null

var _plane: MeshInstance3D
var _zone: Interactable
var _seal: StaticBody3D
var _engaged := false

func _ready() -> void:
	add_child(KitLib.instance("fog_gate_frame"))
	_plane = MeshInstance3D.new()
	var quad := QuadMesh.new()
	quad.size = Vector2(3.4, 3.3)
	_plane.mesh = quad
	var m := ShaderMaterial.new()
	m.shader = load("res://shaders/fog_gate.gdshader")
	_plane.set_surface_override_material(0, m)
	_plane.position = Vector3(0, 1.65, 0)
	add_child(_plane)

	_seal = StaticBody3D.new()
	_seal.collision_layer = 1 << (VG.L_WORLD_RUIN - 1)
	var cs := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = Vector3(3.6, 3.4, 0.3)
	cs.shape = box
	cs.position.y = 1.7
	_seal.add_child(cs)
	add_child(_seal)

	_zone = Interactable.new()
	_zone.prompt = "Part the pale"
	_zone.setup_zone(1.4, 2.0, Vector3(0, 0, 1.2))
	_zone.activated.connect(_on_enter)
	add_child(_zone)

func _on_enter(player) -> void:
	if _engaged or player == null:
		return
	_engaged = true
	_zone.enabled = false
	# step through the veil
	var through: Vector3 = global_position - global_transform.basis.z * 2.2
	through.y = player.global_position.y
	var tw := create_tween()
	player.lock_control(true)
	tw.tween_property(player, "global_position", through, 0.7)
	tw.tween_callback(func():
		player.lock_control(false)
		_engage_boss())
	AudioDirector.sfx_at("res://assets/audio/fog_enter.wav", global_position, -2.0)

func _engage_boss() -> void:
	if boss_spawner != null and boss_spawner.current != null and not boss_spawner.current.dead:
		var boss := boss_spawner.current
		boss.target = Game.player
		boss._set_state(Enemy.ES.ALERT)
		AudioDirector.sfx_at(boss.cfg.get("sfx_alert", ""), boss.global_position, 2.0)
		AudioDirector.play_music("res://assets/audio/theme_boss.wav", 1.5)
		for hud in get_tree().get_nodes_in_group("hud"):
			hud.show_boss(boss)
		boss.died.connect(_on_boss_dead)
	boss_engaged.emit()

func _on_boss_dead(_e) -> void:
	Game.on_boss_slain(area_id)
	dissolve()

func dissolve() -> void:
	_seal.collision_layer = 0
	_zone.enabled = false
	var tw := create_tween()
	tw.tween_property(_plane, "transparency", 1.0, 2.0)
	tw.tween_callback(_plane.hide)
