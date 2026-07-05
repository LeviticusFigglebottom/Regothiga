class_name EnemyVisual
extends CharVisual
## Skeletal visual for any enemy archetype per enemies.json. Body ids map
## to skel_* archetypes; weapon/shield/helm ride bones. Bosses scale up.

const BODY_MAP := {
	"char_penitent": "skel_penitent",
	"char_ward": "skel_ward",
	"char_bellkeeper": "skel_giant",
	"char_latecomer": "skel_hero",
	"char_aveline": "skel_sister",
}

func build(cfg: Dictionary) -> void:
	var body_id: String = cfg.get("body", "skel_penitent")
	body_id = BODY_MAP.get(body_id, body_id)
	var vis_scale := float(cfg.get("vis_scale", 1.55 if cfg.get("is_boss", false) else 1.0))
	build_body(body_id, float(cfg.get("anim_amp", 1.0)), float(cfg.get("anim_sway", 1.0)), vis_scale)
	stride = float(cfg.get("stride", 2.3))
	run_stride = stride * 2.0
	footsteps = cfg.get("is_boss", false)
	step_volume = -6.0

	if cfg.has("weapon"):
		mount_weapon_hand()
		var w := KitLib.instance(cfg["weapon"])
		if cfg.get("weapon", "") == "bell_great":
			# crown gripped at the fist, mouth dragging low behind him
			w.rotation_degrees = Vector3(162, 0, 18)
			w.position = Vector3(0.18, 0.9, -0.5)
		weapon_mount.add_child(w)
	if cfg.has("shield"):
		shield_mount = mount("farm_l")
		shield_mount.position = Vector3(-0.06, 0.16, 0.0)
		shield_mount.rotation_degrees = Vector3(0, 90, 0)
		shield_mount.add_child(KitLib.instance(cfg["shield"]))
	if cfg.has("helm"):
		head_mount = mount("head")
		head_mount.position = Vector3(0, 0.14, 0.0)
		head_mount.add_child(KitLib.instance(cfg["helm"]))
