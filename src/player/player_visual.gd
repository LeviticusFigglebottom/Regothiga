class_name PlayerVisual
extends CharVisual
## The Latecomer's skeletal rig: skel_hero body, weapon in the right hand,
## kite shield strapped to the left forearm, swing trail.

func build(weapon_kit := "sword_cloister") -> void:
	build_body("skel_hero")
	stride = 2.7
	run_stride = 5.4
	footsteps = true

	mount_weapon_hand()
	set_weapon(weapon_kit)
	add_trail()

	shield_mount = mount("farm_l")
	shield_mount.position = Vector3(-0.06, 0.16, 0.0)
	shield_mount.rotation_degrees = Vector3(0, 90, 0)   # face out from the forearm
	shield_mount.add_child(KitLib.instance("shield_kite"))
