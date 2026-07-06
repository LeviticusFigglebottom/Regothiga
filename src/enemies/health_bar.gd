class_name EnemyHealthBar
extends Node3D
## Floating world-space health bar that rides above an enemy's head. It fades in
## when the enemy is struck or locked-on and bleeds back out a few seconds after
## the last hit. Upright billboard (faces the camera on the horizontal plane but
## never tips). Bosses use the big HUD bar instead, so they never get one.

const SHOW_TIME := 4.5
const _FADE := 5.0
const _DRAIN := 1.6          ## how fast the red fill chases the true ratio
const _GHOST := 0.5          ## how fast the pale "damage ghost" catches up

var _quads: Array[MeshInstance3D] = []
var _fill: MeshInstance3D
var _ghost: MeshInstance3D
var _fill_pivot: Node3D
var _ghost_pivot: Node3D

var _w := 0.9
var _h := 0.085
var _ratio := 1.0            ## displayed red fill
var _ghost_ratio := 1.0      ## displayed pale trail
var _target := 1.0           ## the enemy's true hp fraction
var _alpha := 0.0
var _show_t := 0.0
var _forced := false         ## kept visible (e.g. while locked-on)

func build(width := 0.9) -> void:
	_w = width
	# stacked back-to-front: key-line, trough, ghost, fill. Layers are separated
	# both in Z and by render_priority so the transparent quads never sort wrong
	# at range (which would drop the fill or the damage-ghost band).
	_add_quad(_w + 0.055, _h + 0.055, Color(0.02, 0.015, 0.015, 0.92), -0.03, 0)
	_add_quad(_w, _h, Color(0.11, 0.06, 0.05, 0.95), 0.0, 1)
	_ghost_pivot = Node3D.new()
	_ghost_pivot.position.x = -_w * 0.5
	add_child(_ghost_pivot)
	_ghost = _make_quad(_w, _h * 0.8, Color(0.86, 0.74, 0.5, 0.9), 2)
	_ghost.position = Vector3(_w * 0.5, 0.0, 0.03)
	_ghost_pivot.add_child(_ghost)
	_fill_pivot = Node3D.new()
	_fill_pivot.position.x = -_w * 0.5
	add_child(_fill_pivot)
	_fill = _make_quad(_w, _h * 0.8, Color(0.72, 0.16, 0.12, 1.0), 3)
	_fill.position = Vector3(_w * 0.5, 0.0, 0.06)
	_fill_pivot.add_child(_fill)
	_apply_alpha(0.0)
	visible = false

func _add_quad(w: float, h: float, col: Color, z: float, prio: int) -> void:
	var mi := _make_quad(w, h, col, prio)
	mi.position.z = z
	add_child(mi)

func _make_quad(w: float, h: float, col: Color, prio: int) -> MeshInstance3D:
	var mi := MeshInstance3D.new()
	var q := QuadMesh.new()
	q.size = Vector2(w, h)
	mi.mesh = q
	var m := StandardMaterial3D.new()
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m.albedo_color = col
	m.cull_mode = BaseMaterial3D.CULL_DISABLED
	m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	m.render_priority = prio
	mi.material_override = m
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	mi.gi_mode = GeometryInstance3D.GI_MODE_DISABLED
	_quads.append(mi)
	return mi

## Register a fresh hp fraction and pop the bar back to full visibility.
func hit(ratio: float) -> void:
	_target = clampf(ratio, 0.0, 1.0)
	_show_t = SHOW_TIME

func set_ratio(ratio: float) -> void:
	_target = clampf(ratio, 0.0, 1.0)
	_ratio = _target
	_ghost_ratio = _target

func set_forced(on: bool) -> void:
	_forced = on

## Fade the bar out now regardless of recent hits (used on death).
func dismiss() -> void:
	_show_t = 0.0
	_forced = false

func _process(dt: float) -> void:
	_show_t = maxf(0.0, _show_t - dt)
	var want := 1.0 if (_show_t > 0.0 or _forced) else 0.0
	_alpha = move_toward(_alpha, want, dt * _FADE)
	_ratio = move_toward(_ratio, _target, dt * _DRAIN)
	_ghost_ratio = maxf(_ratio, _ghost_ratio - dt * _GHOST)
	_fill_pivot.scale.x = maxf(_ratio, 0.0001)
	_ghost_pivot.scale.x = maxf(_ghost_ratio, 0.0001)
	visible = _alpha > 0.01
	if not visible:
		return
	_apply_alpha(_alpha)
	var cam := get_viewport().get_camera_3d()
	if cam != null:
		var to := cam.global_position - global_position
		to.y = 0.0
		if to.length_squared() > 0.0001:
			# upright billboard: +Z (quad front) points at the camera, stays level
			global_basis = Basis.looking_at(to, Vector3.UP, true)

func _apply_alpha(a: float) -> void:
	for mi in _quads:
		mi.transparency = 1.0 - a
