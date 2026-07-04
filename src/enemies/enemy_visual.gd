class_name EnemyVisual
extends Node3D
## Node-rig visual for any enemy archetype, assembled from kit pieces per
## enemies.json. Same scheme as the player: Pose + arm pivots + clips.

var pose: Node3D
var arm_l: Node3D
var arm_r: Node3D
var weapon_mount: Node3D
var anim: AnimationPlayer

func build(cfg: Dictionary) -> void:
	pose = Node3D.new(); pose.name = "Pose"; add_child(pose)
	var body := KitLib.instance(cfg.get("body", "char_penitent"))
	body.name = "Body"
	pose.add_child(body)
	var dx := float(cfg.get("arm_dx", 0.27))
	var h := float(cfg.get("arm_h", 1.2))

	arm_l = Node3D.new(); arm_l.name = "ArmL"; arm_l.position = Vector3(-dx, h, 0.03)
	pose.add_child(arm_l)
	if cfg.has("arm_l"):
		arm_l.add_child(KitLib.instance(cfg["arm_l"]))
	if cfg.has("shield"):
		var sm := Node3D.new(); sm.name = "ShieldMount"; sm.position = Vector3(-0.04, -0.34, 0.05)
		arm_l.add_child(sm)
		sm.add_child(KitLib.instance(cfg["shield"]))

	arm_r = Node3D.new(); arm_r.name = "ArmR"; arm_r.position = Vector3(dx, h, 0.03)
	pose.add_child(arm_r)
	if cfg.has("arm_r"):
		arm_r.add_child(KitLib.instance(cfg["arm_r"]))
	weapon_mount = Node3D.new(); weapon_mount.name = "WeaponMount"
	weapon_mount.position = Vector3(0.02, -0.9 if cfg.get("is_boss", false) else -0.5, 0)
	arm_r.add_child(weapon_mount)
	if cfg.has("weapon"):
		var w := KitLib.instance(cfg["weapon"])
		if cfg.get("weapon", "") == "bell_great":
			w.position = Vector3(0, -1.3, 0)   # bell dragged low from the fist
			w.rotation_degrees = Vector3(24, 0, 0)
		weapon_mount.add_child(w)
	if cfg.has("helm"):
		var helm := KitLib.instance(cfg["helm"])
		helm.position = Vector3(0, float(cfg.get("hurt_h", 1.8)) * 0.86, 0.02)
		pose.add_child(helm)

	anim = AnimationPlayer.new()
	anim.name = "Anim"
	add_child(anim)
	anim.root_node = anim.get_path_to(self)
	anim.add_animation_library("", _build_clips(cfg))
	anim.play("RESET")
	anim.advance(0.05)
	anim.play("idle")

func play(clip: String, blend := 0.12, speed := 1.0) -> void:
	if anim.has_animation(clip):
		anim.play(clip, blend, speed)

func idle(blend := 0.25) -> void:
	anim.play("idle", blend)

const REST_R := [10, -6, 0]
const REST_L := [10, 6, 0]

func _build_clips(cfg: Dictionary) -> AnimationLibrary:
	var lib := AnimationLibrary.new()
	var A := AnimBuilder
	lib.add_animation("RESET", A.make("RESET", 0.05, {
		"Pose:position": [[0.0, Vector3.ZERO]],
		"Pose:rotation": [[0.0, [0, 0, 0]]],
		"Pose/ArmR:rotation": [[0.0, REST_R]],
		"Pose/ArmL:rotation": [[0.0, REST_L]],
	}))
	lib.add_animation("idle", A.make("idle", 3.6, {
		"Pose:position": [[0.0, Vector3.ZERO], [1.8, Vector3(0, 0.03, 0)], [3.6, Vector3.ZERO]],
		"Pose:rotation": [[0.0, [0, 0, 1.5]], [1.8, [1.5, 0, -1.5]], [3.6, [0, 0, 1.5]]],
	}, true))
	# telegraphed swings: the windup IS the tell — big, slow, readable
	for spec in cfg.get("attacks", []):
		var w: float = spec["windup"]
		var act: float = spec["active"]
		var rec: float = spec["recover"]
		var total := w + act + rec
		var nm: String = spec.get("anim", "atk_r")
		if lib.has_animation(nm):
			continue
		match nm:
			"atk_r", "atk_double":
				lib.add_animation(nm, A.make(nm, total, {
					"Pose/ArmR:rotation": [[0.0, REST_R], [w * 0.9, [150, -55, 20]],
						[w + act, [40, 60, -10]], [total, REST_R]],
					"Pose:rotation": [[0.0, [0, 0, 0]], [w * 0.9, [-8, 28, 0]],
						[w + act, [10, -26, 0]], [total, [0, 0, 0]]],
				}))
			"atk_thrust":
				lib.add_animation(nm, A.make(nm, total, {
					"Pose/ArmR:rotation": [[0.0, REST_R], [w * 0.9, [96, -30, 0]],
						[w + act, [88, 6, 0]], [total, REST_R]],
					"Pose:rotation": [[0.0, [0, 0, 0]], [w * 0.9, [-10, 18, 0]],
						[w + act, [14, -8, 0]], [total, [0, 0, 0]]],
					"Pose:position": [[0.0, Vector3.ZERO], [w, Vector3(0, 0, 0.14)],
						[w + act, Vector3(0, -0.04, -0.3)], [total, Vector3.ZERO]],
				}))
			"atk_over":
				lib.add_animation(nm, A.make(nm, total, {
					"Pose/ArmR:rotation": [[0.0, REST_R], [w * 0.9, [200, -6, 0]],
						[w + act, [60, 2, 0]], [total, REST_R]],
					"Pose:rotation": [[0.0, [0, 0, 0]], [w * 0.9, [-16, 0, 0]],
						[w + act, [18, 0, 0]], [total, [0, 0, 0]]],
					"Pose:position": [[0.0, Vector3.ZERO], [w * 0.9, Vector3(0, 0.08, 0.1)],
						[w + act, Vector3(0, -0.14, -0.12)], [total, Vector3.ZERO]],
				}))
			"atk_back":
				lib.add_animation(nm, A.make(nm, total, {
					"Pose/ArmR:rotation": [[0.0, REST_R], [w * 0.9, [60, 70, 0]],
						[w + act, [50, -70, 0]], [total, REST_R]],
					"Pose:rotation": [[0.0, [0, 0, 0]], [w * 0.9, [0, -40, 0]],
						[w + act, [0, 36, 0]], [total, [0, 0, 0]]],
				}))
			"atk_spin":
				lib.add_animation(nm, A.make(nm, total, {
					"Pose:rotation": [[0.0, [0, 0, 0]], [w, [0, -50, 0]],
						[w + act * 0.5, [0, 160, 0]], [w + act, [0, 340, 0]], [total, [0, 360, 0]]],
					"Pose/ArmR:rotation": [[0.0, REST_R], [w, [80, -40, 0]],
						[w + act, [80, -40, 0]], [total, REST_R]],
				}))
	lib.add_animation("stagger", A.make("stagger", 0.8, {
		"Pose:rotation": [[0.0, [0, 0, 0]], [0.1, [-20, 0, 7]], [0.5, [-10, 0, -4]], [0.8, [0, 0, 0]]],
		"Pose:position": [[0.0, Vector3.ZERO], [0.12, Vector3(0, -0.08, 0.2)], [0.8, Vector3.ZERO]],
	}))
	lib.add_animation("death", A.make("death", 1.6, {
		"Pose:rotation": [[0.0, [0, 0, 0]], [0.6, [-50, 0, 14]], [1.2, [-88, 0, 20]], [1.6, [-90, 0, 20]]],
		"Pose:position": [[0.0, Vector3.ZERO], [1.2, Vector3(0, -0.5, 0.3)], [1.6, Vector3(0, -0.62, 0.35)]],
	}))
	return lib
