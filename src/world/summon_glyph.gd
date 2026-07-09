class_name SummonGlyph
extends Node3D
## A pale-gold summoning sign before an unbeaten warden's veil (ruin only).
## For a handful of orisons, Ser Adalric of the Morrow answers in phantom
## form — and the warden, honored by the audience, grows half again as
## mighty. The sign returns with the veil whenever the warden still stands.

const COST := 150

var fog_gate: FogGate = null
var area_id := ""

var _zone: Interactable
var _disc: MeshInstance3D
var _ring: MeshInstance3D
var _light: OmniLight3D
var _ally: AllyKnight = null
var _t := 0.0

func _ready() -> void:
	add_to_group(VG.GROUP_RESPAWN_ON_REST)
	_disc = MeshInstance3D.new()
	var pm := PlaneMesh.new()
	pm.size = Vector2(2.0, 2.0)
	_disc.mesh = pm
	var mat := StandardMaterial3D.new()
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mat.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	mat.albedo_color = Color(0.95, 0.88, 0.6)
	mat.albedo_texture = AreaPortal._radial_tex()
	_disc.material_override = mat
	_disc.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	_disc.position.y = 0.06
	add_child(_disc)

	_ring = MeshInstance3D.new()
	var tm := TorusMesh.new()
	tm.inner_radius = 0.66
	tm.outer_radius = 0.74
	_ring.mesh = tm
	var rm := StandardMaterial3D.new()
	rm.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	rm.albedo_color = Color(1.0, 0.92, 0.66)
	rm.emission_enabled = true
	rm.emission = Color(1.0, 0.88, 0.5)
	rm.emission_energy_multiplier = 1.6
	_ring.material_override = rm
	_ring.scale.y = 0.06
	_ring.position.y = 0.08
	add_child(_ring)

	_light = OmniLight3D.new()
	_light.light_color = Color(1.0, 0.9, 0.6)
	_light.light_energy = 1.0
	_light.omni_range = 3.4
	_light.omni_attenuation = 1.6
	_light.shadow_enabled = false
	_light.position.y = 0.6
	add_child(_light)

	_zone = Interactable.new()
	_zone.prompt = "Summon Ser Adalric — %d orisons" % COST
	_zone.setup_zone(1.5, 1.8)
	_zone.activated.connect(_on_use)
	add_child(_zone)

func _process(dt: float) -> void:
	_t += dt
	_ring.rotation.y = _t * 0.5
	if _light != null and visible:
		_light.light_energy = 0.8 + 0.35 * sin(_t * 2.6)

func _boss() -> Node:
	if fog_gate == null or fog_gate.boss_spawner == null:
		return null
	return fog_gate.boss_spawner.current

func _on_use(player) -> void:
	if player == null or (_ally != null and is_instance_valid(_ally)):
		return
	if Game.orisons < COST:
		Game.toast.emit("The sign asks %d orisons you do not carry." % COST)
		return
	Game.add_orisons(-COST)
	_ally = AllyKnight.new()
	add_sibling(_ally)
	_ally.global_position = global_position + Vector3(0.7, 0.1, 0.7)
	_ally.tree_exited.connect(_on_ally_gone)
	AudioDirector.sfx_at("res://assets/audio/swell_kindle.wav", global_position, -2.0, 1.2)
	Game.toast.emit("Ser Adalric of the Morrow answers the sign.")
	# the warden takes strength from the audience, as such bargains go
	var b := _boss()
	if b != null and is_instance_valid(b) and not b.get("dead"):
		b.max_hp *= 1.5
		b.hp *= 1.5
	_set_active(false)

func _on_ally_gone() -> void:
	_ally = null

func _set_active(on: bool) -> void:
	visible = on
	_zone.enabled = on
	set_process(on)

## Runs with the vigil/death respawns: the sign returns while the warden
## still stands; once the warden rests forever, it never re-forms.
func respawn() -> void:
	if fog_gate != null and fog_gate.boss_spawner != null \
			and fog_gate.boss_spawner.dead_once \
			and World.area_flag(area_id, fog_gate.boss_spawner.spawn_flag):
		_set_active(false)
		return
	if _ally == null:
		_set_active(true)
