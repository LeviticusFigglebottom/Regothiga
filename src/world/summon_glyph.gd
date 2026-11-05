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

static var _sign_shader: Shader = null

static func _get_sign_shader() -> Shader:
	if _sign_shader == null:
		_sign_shader = Shader.new()
		_sign_shader.code = """
shader_type spatial;
render_mode cull_disabled, unshaded, blend_add, depth_draw_never;

uniform vec3 gold_tint : source_color = vec3(1.0, 0.84, 0.42);
uniform float energy = 2.6;

float hash12(vec2 p) {
	vec3 p3 = fract(vec3(p.xyx) * 0.1031);
	p3 += dot(p3, p3.yzx + 33.33);
	return fract((p3.x + p3.y) * p3.z);
}

void fragment() {
	// UV in -1..1 (elongated tablet aspect)
	vec2 p = UV * 2.0 - 1.0;
	p.y *= 1.85;
	float r = length(p);
	float pulse = 0.88 + 0.12 * sin(TIME * 3.2);

	// Soft golden aura underneath the inscription
	float aura = exp(-r * r * 3.2) * 0.42;

	// Outer double-ring border around the rune script
	float border = smoothstep(0.035, 0.0, abs(r - 0.78)) * 0.65
			+ smoothstep(0.022, 0.0, abs(r - 0.68)) * 0.45;

	// Archaic Dark Souls calligraphic rune lines along the sign
	float line_band = smoothstep(0.58, 0.42, abs(p.y)) * smoothstep(0.72, 0.56, abs(p.x));
	float row_y = p.y * 5.5;
	float row_id = floor(row_y + 3.0);
	float row_f = fract(row_y + 3.0);
	float row_mask = smoothstep(0.12, 0.28, row_f) * smoothstep(0.88, 0.72, row_f);

	float glyph_x = p.x * 16.0 + row_id * 7.3;
	float cell_id = floor(glyph_x);
	float gf = fract(glyph_x) - 0.5;
	float rf = row_f - 0.5;
	float h = hash12(vec2(cell_id, row_id));

	// Synthesize calligraphic strokes (vertical stem + diagonal + arc)
	float stem = smoothstep(0.14, 0.02, abs(gf - (h - 0.5) * 0.25));
	float diag = smoothstep(0.15, 0.02, abs(gf * (h > 0.5 ? 1.0 : -1.0) - rf * 0.85));
	float cross_bar = smoothstep(0.14, 0.02, abs(rf - (fract(h * 7.1) - 0.5) * 0.4));
	float gap = step(0.18, h); // natural word breaks
	float script = clamp((stem + diag * 0.85 + cross_bar * 0.7) * gap, 0.0, 1.0) * line_band * row_mask;

	// Shimmering wave travelling across the golden runes
	float shimmer = 0.75 + 0.45 * sin(TIME * 4.2 - p.x * 4.5 + p.y * 2.0);
	float total = (aura + (border + script * 1.65) * shimmer) * smoothstep(1.05, 0.72, r);

	vec3 col = mix(gold_tint, vec3(1.0, 0.98, 0.86), clamp(script * 0.75 + border * 0.4, 0.0, 1.0));
	ALBEDO = vec3(0.0);
	EMISSION = col * energy * total * pulse;
	ALPHA = clamp(total, 0.0, 1.0);
}
"""
	return _sign_shader

func _ready() -> void:
	add_to_group(VG.GROUP_RESPAWN_ON_REST)
	var smat := ShaderMaterial.new()
	smat.shader = _get_sign_shader()

	_disc = MeshInstance3D.new()
	var pm := PlaneMesh.new()
	pm.size = Vector2(1.35, 0.78)
	_disc.mesh = pm
	_disc.material_override = smat
	_disc.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	_disc.position.y = 0.04
	add_child(_disc)

	# Secondary inner glow layer (preserves _ring reference)
	_ring = MeshInstance3D.new()
	var pm2 := PlaneMesh.new()
	pm2.size = Vector2(0.82, 0.48)
	_ring.mesh = pm2
	_ring.material_override = smat
	_ring.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	_ring.position.y = 0.05
	add_child(_ring)

	_light = OmniLight3D.new()
	_light.light_color = Color(1.0, 0.84, 0.44)
	_light.light_energy = 1.25
	_light.omni_range = 3.6
	_light.omni_attenuation = 1.5
	_light.shadow_enabled = false
	_light.position.y = 0.45
	add_child(_light)

	Game.area_cleared.connect(func(aid: String) -> void:
		if aid == area_id:
			_set_active(false))
	_zone = Interactable.new()
	_zone.prompt = "Summon Ser Adalric — %d orisons" % COST
	_zone.setup_zone(1.5, 1.8)
	_zone.activated.connect(_on_use)
	add_child(_zone)

func _process(dt: float) -> void:
	_t += dt
	if _light != null and visible:
		_light.light_energy = 1.05 + 0.35 * sin(_t * 2.8)

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
		b.max_hp *= 2.0
		b.hp *= 2.0
		b.stagger_resist = 2.0   # honored by an audience, twice as hard to break
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
