class_name AnimBuilder
## Builds the player/NPC animation clips in code. Combat timing lives in data
## (movesets.json); these clips are the matching visual arcs, generated with
## the same durations so pose and window never drift apart. (DECISIONS D-006)

const D2R := PI / 180.0

static func _track(anim: Animation, path: String, keys: Array) -> void:
	var t := anim.add_track(Animation.TYPE_VALUE)
	anim.track_set_path(t, NodePath(path))
	anim.track_set_interpolation_type(t, Animation.INTERPOLATION_CUBIC)
	for k in keys:
		var v = k[1]
		if v is Array:   # euler degrees -> radians Vector3
			v = Vector3(v[0] * D2R, v[1] * D2R, v[2] * D2R)
		anim.track_insert_key(t, k[0], v)

static func make(name: StringName, length: float, tracks: Dictionary, loop := false) -> Animation:
	var a := Animation.new()
	a.resource_name = name
	a.length = length
	a.loop_mode = Animation.LOOP_LINEAR if loop else Animation.LOOP_NONE
	for path in tracks:
		_track(a, path, tracks[path])
	return a

## The rest pose every clip returns to.
const REST_R := [12, -8, 0]        # ShoulderR rotation degrees (arm slightly out)
const REST_L := [10, 10, 0]
const REST_WEAPON := [196, 0, 8]   # blade along the arm line, tip down-forward
const REST_SHIELD := [-4, -14, 0]

static func build_library() -> AnimationLibrary:
	var lib := AnimationLibrary.new()

	lib.add_animation("RESET", make("RESET", 0.05, {
		"Pose:position": [[0.0, Vector3.ZERO]],
		"Pose:rotation": [[0.0, [0, 0, 0]]],
		"Pose/ShoulderR:rotation": [[0.0, REST_R]],
		"Pose/ShoulderL:rotation": [[0.0, REST_L]],
		"Pose/ShoulderR/WeaponMount:rotation": [[0.0, REST_WEAPON]],
		"Pose/ShoulderL/ShieldMount:rotation": [[0.0, REST_SHIELD]],
	}))

	lib.add_animation("idle", make("idle", 3.2, {
		"Pose:position": [[0.0, Vector3.ZERO], [1.6, Vector3(0, 0.018, 0)], [3.2, Vector3.ZERO]],
		"Pose/ShoulderR:rotation": [[0.0, REST_R], [1.6, [15, -8, 0]], [3.2, REST_R]],
		"Pose/ShoulderL:rotation": [[0.0, REST_L], [1.6, [13, 10, 0]], [3.2, REST_L]],
	}, true))

	lib.add_animation("kneel", make("kneel", 1.2, {
		"Pose:position": [[0.0, Vector3.ZERO], [0.9, Vector3(0, -0.46, 0.05)], [1.2, Vector3(0, -0.46, 0.05)]],
		"Pose:rotation": [[0.0, [0, 0, 0]], [0.9, [14, 0, 0]], [1.2, [14, 0, 0]]],
		"Pose/ShoulderR:rotation": [[0.0, REST_R], [1.0, [52, -6, 0]], [1.2, [52, -6, 0]]],
	}))

	lib.add_animation("stagger", make("stagger", 0.7, {
		"Pose:rotation": [[0.0, [0, 0, 0]], [0.1, [-16, 0, 5]], [0.45, [-8, 0, -3]], [0.7, [0, 0, 0]]],
		"Pose:position": [[0.0, Vector3.ZERO], [0.12, Vector3(0, -0.06, 0.14)], [0.7, Vector3.ZERO]],
	}))

	lib.add_animation("death", make("death", 1.4, {
		"Pose:rotation": [[0.0, [0, 0, 0]], [0.5, [-42, 0, 6]], [1.0, [-84, 0, 10]], [1.4, [-86, 0, 10]]],
		"Pose:position": [[0.0, Vector3.ZERO], [1.0, Vector3(0, -0.55, 0.3)], [1.4, Vector3(0, -0.72, 0.38)]],
	}))

	lib.add_animation("block", make("block", 0.6, {
		"Pose/ShoulderL:rotation": [[0.0, REST_L], [0.16, [64, 26, 0]], [0.6, [64, 26, 0]]],
		"Pose/ShoulderL/ShieldMount:rotation": [[0.0, REST_SHIELD], [0.16, [-18, -30, 0]], [0.6, [-18, -30, 0]]],
		"Pose:position": [[0.0, Vector3.ZERO], [0.2, Vector3(0, -0.05, 0)], [0.6, Vector3(0, -0.05, 0)]],
	}))

	lib.add_animation("parry", make("parry", 0.6, {
		"Pose/ShoulderL:rotation": [[0.0, REST_L], [0.08, [78, 40, 0]], [0.24, [58, -24, 0]], [0.6, REST_L]],
		"Pose/ShoulderL/ShieldMount:rotation": [[0.0, REST_SHIELD], [0.08, [-30, -60, 0]], [0.24, [0, 20, 0]], [0.6, REST_SHIELD]],
	}))

	lib.add_animation("flask", make("flask", 1.1, {
		"Pose/ShoulderL:rotation": [[0.0, REST_L], [0.3, [118, -18, 0]], [0.8, [118, -18, 0]], [1.1, REST_L]],
		"Pose:rotation": [[0.0, [0, 0, 0]], [0.5, [-7, 0, 0]], [1.1, [0, 0, 0]]],
	}))

	lib.add_animation("roll", _roll(0.46))
	lib.add_animation("backstep", make("backstep", 0.32, {
		"Pose:position": [[0.0, Vector3.ZERO], [0.14, Vector3(0, -0.16, 0)], [0.32, Vector3.ZERO]],
		"Pose:rotation": [[0.0, [0, 0, 0]], [0.14, [8, 0, 0]], [0.32, [0, 0, 0]]],
	}))

	# attack clips from moveset data so visuals track the numbers
	var ms: Dictionary = DB.moveset("longsword")
	if not ms.is_empty():
		var l1: Dictionary = ms["lights"][0]
		var l2: Dictionary = ms["lights"][1]
		var hv: Dictionary = ms["heavy"]
		lib.add_animation("attack_l1", _slash(l1, false))
		lib.add_animation("attack_l2", _slash(l2, true))
		lib.add_animation("attack_h", _overhead(hv))
	lib.add_animation("riposte", _riposte(0.9))
	return lib

static func _slash(m: Dictionary, mirror: bool) -> Animation:
	var w: float = m["windup"]; var a: float = m["active"]; var r: float = m["recovery"]
	var s := -1.0 if mirror else 1.0
	return make("slash", w + a + r, {
		"Pose/ShoulderR:rotation": [
			[0.0, REST_R],
			[w * 0.85, [148, s * -52, s * 18]],          # raised back
			[w + a, [46, s * 58, s * -12]],              # swept through
			[w + a + r * 0.6, [30, s * 20, 0]],
			[w + a + r, REST_R]],
		"Pose/ShoulderR/WeaponMount:rotation": [
			[0.0, REST_WEAPON],
			[w * 0.85, [230, s * -30, 0]],
			[w + a, [178, s * 34, 0]],
			[w + a + r, REST_WEAPON]],
		"Pose:rotation": [
			[0.0, [0, 0, 0]],
			[w * 0.85, [-6, s * 26, 0]],
			[w + a, [10, s * -30, 0]],
			[w + a + r, [0, 0, 0]]],
		"Pose:position": [
			[0.0, Vector3.ZERO],
			[w + a, Vector3(0, -0.05, -0.12)],
			[w + a + r, Vector3.ZERO]],
	})

static func _overhead(m: Dictionary) -> Animation:
	var w: float = m["windup"]; var a: float = m["active"]; var r: float = m["recovery"]
	return make("overhead", w + a + r, {
		"Pose/ShoulderR:rotation": [
			[0.0, REST_R],
			[w * 0.9, [196, -10, 0]],                    # high overhead
			[w + a, [64, 4, 0]],                         # brought down
			[w + a + r, REST_R]],
		"Pose/ShoulderR/WeaponMount:rotation": [
			[0.0, REST_WEAPON],
			[w * 0.9, [156, 0, 0]],
			[w + a, [200, 0, 0]],
			[w + a + r, REST_WEAPON]],
		"Pose:rotation": [
			[0.0, [0, 0, 0]],
			[w * 0.9, [-12, 0, 0]],
			[w + a, [16, 0, 0]],
			[w + a + r * 0.5, [10, 0, 0]],
			[w + a + r, [0, 0, 0]]],
		"Pose:position": [
			[0.0, Vector3.ZERO],
			[w * 0.9, Vector3(0, 0.04, 0.08)],
			[w + a, Vector3(0, -0.10, -0.16)],
			[w + a + r, Vector3.ZERO]],
	})

static func _riposte(dur: float) -> Animation:
	return make("riposte", dur, {
		"Pose/ShoulderR:rotation": [
			[0.0, REST_R], [0.18, [120, -40, 0]], [0.34, [86, 12, 0]],
			[0.62, [86, 12, 0]], [dur, REST_R]],
		"Pose/ShoulderR/WeaponMount:rotation": [
			[0.0, REST_WEAPON], [0.18, [150, -20, 0]], [0.34, [96, 0, 0]],
			[0.62, [96, 0, 0]], [dur, REST_WEAPON]],
		"Pose:position": [
			[0.0, Vector3.ZERO], [0.34, Vector3(0, -0.06, -0.3)],
			[0.62, Vector3(0, -0.06, -0.3)], [dur, Vector3.ZERO]],
	})

static func _roll(dur: float) -> Animation:
	return make("roll", dur, {
		"Pose:rotation": [
			[0.0, [0, 0, 0]], [dur * 0.25, [-95, 0, 0]], [dur * 0.5, [-185, 0, 0]],
			[dur * 0.75, [-272, 0, 0]], [dur, [-360, 0, 0]]],
		"Pose:position": [
			[0.0, Vector3.ZERO], [dur * 0.4, Vector3(0, -0.32, 0)],
			[dur * 0.8, Vector3(0, -0.1, 0)], [dur, Vector3.ZERO]],
	})
