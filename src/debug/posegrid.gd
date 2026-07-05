extends Node3D
## Pose-grid sandbox: skeletal characters frozen at key clip frames for
## animation sign-off. Run:
##   tools/shot.sh docs/wip/posegrid.png --sandbox=posegrid --shot-cam=...

var _row := -1   # --row=N shows one row only

func _ready() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--row="):
			_row = int(arg.get_slice("=", 1))
	var x := 0.0
	# row 0: archetype line-up, idling (gear where the game mounts it)
	_cell(x, 0, "hero", _player_vis(), "idle", 0.0); x += 2.2
	_cell(x, 0, "ward", _enemy_vis("ward"), "idle", 0.0); x += 2.2
	_cell(x, 0, "penitent", _enemy_vis("penitent"), "idle", 0.0); x += 2.2
	_cell(x, 0, "giant", _enemy_vis("bellkeeper"), "idle", 0.0); x += 3.4
	_cell(x, 0, "sister", _npc_vis(), "idle", 0.0); x += 2.2
	_cell(x, 0, "idle_mid", _player_vis(), "idle", 1.8)

	# row 1: walk phases
	x = 0.0
	for ph in [0.0, 0.25, 0.5, 0.75]:
		_cell(x, 3.2, "walk %.2f" % ph, _player_vis(), "walk", ph); x += 2.2
	for ph in [0.0, 0.155, 0.31, 0.465]:
		_cell(x, 3.2, "run %.2f" % ph, _player_vis(), "run", ph); x += 2.2

	# row 2: attack key frames
	x = 0.0
	for spec in [["attack_l1", 0.32], ["attack_l1", 0.47], ["attack_l2", 0.3], ["attack_l2", 0.45],
			["attack_h", 0.36], ["attack_h", 0.5], ["riposte", 0.25], ["riposte", 0.42]]:
		_cell(x, 6.6, "%s %.2f" % [spec[0], spec[1]], _player_vis(), spec[0], spec[1]); x += 2.2

	# row 3: enemy attacks (ward with halberd)
	x = 0.0
	for spec in [["atk_r", 0.4], ["atk_r", 0.56], ["atk_thrust", 0.42], ["atk_thrust", 0.58],
			["atk_over", 0.44], ["atk_over", 0.58], ["atk_back", 0.35], ["atk_back", 0.5]]:
		_cell(x, 10.0, "%s %.2f" % [spec[0], spec[1]], _enemy_vis("ward"), spec[0], spec[1]); x += 2.2

	# row 4: defense / reactions
	x = 0.0
	for spec in [["block", 0.5], ["parry", 0.1], ["parry", 0.26], ["flask", 0.5],
			["stagger", 0.12], ["kneel", 1.15], ["roll", 0.3], ["roll", 0.5], ["death", 1.45]]:
		_cell(x, 13.4, "%s %.2f" % [spec[0], spec[1]], _player_vis(), spec[0], spec[1]); x += 2.2

	_dress()

func _player_vis() -> CharVisual:
	var v := PlayerVisual.new()
	add_child(v)
	v.build()
	return v

func _enemy_vis(id: String) -> CharVisual:
	var v := EnemyVisual.new()
	add_child(v)
	v.build(DB.enemy(id))
	return v

func _npc_vis() -> CharVisual:
	var v := CharVisual.new()
	add_child(v)
	v.build_body("skel_sister", 0.8, 0.9)
	return v

const ROW_Z := {0: 0.0, 1: 3.2, 2: 6.6, 3: 10.0, 4: 13.4}

func _cell(x: float, z: float, label: String, v: CharVisual, clip: String, t: float) -> void:
	if _row >= 0 and absf(z - float(ROW_Z.get(_row, -99.0))) > 0.1:
		v.queue_free()
		return
	v.position = Vector3(x, 0, z)
	v.rotation.y = PI   # face the camera
	v.play(clip, 0.0)
	v.anim.advance(t)
	v.anim.pause()
	var l := Label3D.new()
	l.text = label
	l.font_size = 34
	l.pixel_size = 0.004
	l.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	l.position = Vector3(x, 2.35, z)
	add_child(l)

func _dress() -> void:
	var ground := MeshInstance3D.new()
	var pm := PlaneMesh.new()
	pm.size = Vector2(60, 60)
	ground.mesh = pm
	ground.position = Vector3(8, 0, 7)
	ground.set_surface_override_material(0, MaterialLib.get_mat("M_stone_dark"))
	add_child(ground)
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-40, 28, 0)
	sun.light_color = Color(1.0, 0.87, 0.7)
	sun.light_energy = 1.5
	sun.shadow_enabled = true
	add_child(sun)
	var env := WorldEnvironment.new()
	var e := Environment.new()
	e.background_mode = Environment.BG_COLOR
	e.background_color = Color(0.32, 0.35, 0.42)
	e.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	e.ambient_light_color = Color(0.55, 0.56, 0.62)
	e.ambient_light_energy = 0.85
	e.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	env.environment = e
	add_child(env)
