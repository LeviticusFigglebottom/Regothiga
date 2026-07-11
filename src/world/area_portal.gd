class_name AreaPortal
extends Node3D
## A doorway to another area of the kingdom. Optionally sealed behind a
## world flag (the tower door opens only when the warden rests).

var to_area := ""
var spawn_pos := Vector3.ZERO
var spawn_yaw := 1e9             # camera yaw (deg) on arrival; unset = keep
var prompt := "Pass on"
var locked_flag := ""        # world flag that must be TRUE to pass
var locked_prompt := "Sealed"
var requires_items: Array = []   # item ids the Latecomer must carry to pass
var cutscene := ""               # "ferry": ride the canals before arriving

var _zone: Interactable
var _marker: OmniLight3D
var _disc: MeshInstance3D
var _pulse := 0.0

func _ready() -> void:
	_zone = Interactable.new()
	_zone.prompt = prompt
	_zone.setup_zone(1.6, 2.2)
	_zone.activated.connect(_on_use)
	add_child(_zone)
	_add_marker()

## A threshold marker: a soft glowing floor sigil + a gentle light, so a stair or
## door reads as usable from across the room instead of the prompt just popping.
func _add_marker() -> void:
	var disc := MeshInstance3D.new()
	var pm := PlaneMesh.new()
	pm.size = Vector2(2.4, 2.4)
	disc.mesh = pm
	var mat := StandardMaterial3D.new()
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mat.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	mat.albedo_color = Color(0.95, 0.8, 0.46)
	mat.albedo_texture = _radial_tex()
	disc.material_override = mat
	disc.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	disc.position = Vector3(0, 0.05, 0)
	add_child(disc)
	_disc = disc
	var light := OmniLight3D.new()
	light.light_color = Color(1.0, 0.83, 0.52)
	light.omni_range = 3.6
	light.omni_attenuation = 1.7
	light.position = Vector3(0, 0.7, 0)
	add_child(light)
	_marker = light

static func _radial_tex() -> GradientTexture2D:
	var grad := Gradient.new()
	grad.set_color(0, Color(1, 1, 1, 0.85))
	grad.set_color(1, Color(1, 1, 1, 0.0))
	var gt := GradientTexture2D.new()
	gt.gradient = grad
	gt.fill = GradientTexture2D.FILL_RADIAL
	gt.fill_from = Vector2(0.5, 0.5)
	gt.fill_to = Vector2(0.5, 0.0)
	gt.width = 48
	gt.height = 48
	return gt

func _unlocked() -> bool:
	if locked_flag != "":
		var ok := World.is_cleared(locked_flag.get_slice(":", 1)) \
				if locked_flag.begins_with("cleared:") else World.flag(locked_flag)
		if not ok:
			return false
	for it in requires_items:
		if Game.player == null or int(Game.player.inventory.get(it, 0)) < 1:
			return false
	return true

func _physics_process(dt: float) -> void:
	var open := _unlocked()
	if locked_flag != "" or not requires_items.is_empty():
		_zone.prompt = prompt if open else locked_prompt
	# breathe the marker; warm gold when open, cold and dim when sealed
	_pulse += dt
	var breathe := 0.62 + 0.38 * (0.5 + 0.5 * sin(_pulse * 2.2))
	if _marker != null:
		_marker.light_energy = (1.5 if open else 0.4) * breathe
		_marker.light_color = Color(1.0, 0.83, 0.52) if open else Color(0.5, 0.56, 0.72)
	if _disc != null:
		var base: Color = Color(0.95, 0.8, 0.46) if open else Color(0.42, 0.47, 0.62)
		_disc.material_override.albedo_color = base * breathe

func _on_use(player) -> void:
	if Game.arena_locked:
		Game.toast.emit("The pale holds. The duel is not done.")
		return
	if not _unlocked():
		Game.toast.emit(locked_prompt + ".")
		return
	if to_area == "" or player == null:
		return
	if cutscene == "ferry":
		_ferry_ride.call_deferred()
		return
	if cutscene == "ascend":
		_ascension.call_deferred()
		return
	Game.travel_to(to_area, spawn_pos, spawn_yaw)

## The lightfall: rise into the beacon, white out, arrive above the hours.
## A door may carry an "ascend_focus" meta (a door-local offset) naming the
## pillar's axis, so the ride lifts the pilgrim through the light itself.
func _ascension() -> void:
	if Game.player != null:
		Game.player.lock_control(true)
	var ride := AscensionRide.new()
	if has_meta("ascend_focus"):
		ride.focus = to_global(get_meta("ascend_focus"))
	get_tree().root.add_child(ride)
	await ride.finished
	Game.travel_to(to_area, spawn_pos, spawn_yaw)
	ride.reveal_and_free()

## The waterworks passage: ride the canal down to the destination, then arrive.
func _ferry_ride() -> void:
	if Game.player != null:
		Game.player.lock_control(true)
	var ride := FerryRide.new()
	get_tree().root.add_child(ride)
	await ride.finished
	Game.travel_to(to_area, spawn_pos, spawn_yaw)
	ride.reveal_and_free()
