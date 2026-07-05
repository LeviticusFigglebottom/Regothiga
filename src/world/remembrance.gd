class_name Remembrance
extends Node3D
## The Latecomer's dropped orisons: a kneeling wisp of candle-smoke and
## light. One chance — replaced (lost) if you fall again before reclaiming.

var amount := 0

func _ready() -> void:
	var zone := Interactable.new()
	zone.prompt = "Reclaim remembrance"
	zone.setup_zone(1.4, 1.4)
	zone.activated.connect(_on_reclaim)
	add_child(zone)
	# visual: a faint kneeling ghost of light + rising motes
	var ghost := CharVisual.new()
	add_child(ghost)
	ghost.build_body("skel_hero")
	ghost.scale = Vector3(0.95, 0.95, 0.95)
	ghost.play("kneel", 0.0)
	ghost.anim.advance(1.2)   # settle straight into the kneel
	for mi in KitLib._mesh_instances(ghost):
		mi.set_instance_shader_parameter("death_diss", 0.55)
	var p := CPUParticles3D.new()
	p.amount = 26
	p.lifetime = 2.2
	p.emission_shape = CPUParticles3D.EMISSION_SHAPE_SPHERE
	p.emission_sphere_radius = 0.4
	p.direction = Vector3.UP
	p.initial_velocity_min = 0.2
	p.initial_velocity_max = 0.6
	p.gravity = Vector3.ZERO
	p.scale_amount_min = 0.02
	p.scale_amount_max = 0.06
	var mesh := SphereMesh.new()
	mesh.radius = 0.05
	mesh.height = 0.1
	var mm := StandardMaterial3D.new()
	mm.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mm.albedo_color = Color(1.0, 0.85, 0.5)
	mesh.material = mm
	p.mesh = mesh
	p.position.y = 0.5
	add_child(p)
	var l := OmniLight3D.new()
	l.light_color = Color(1.0, 0.8, 0.45)
	l.light_energy = 1.2
	l.omni_range = 4.0
	l.position.y = 0.8
	add_child(l)

func _on_reclaim(_player) -> void:
	Game.add_orisons(amount)
	World.clear_remembrance()
	World.save_game()
	AudioDirector.sfx("res://assets/audio/remembrance.wav", -2.0)
	Game.remembrance_reclaimed.emit(amount)
	queue_free()
