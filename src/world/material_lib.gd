class_name MaterialLib
## The single source of visual truth: every kit surface maps to one of these
## shared ShaderMaterials. Variants exist per state-mode (base / glory-only /
## ruin-only) so layer-exclusive meshes dissolve correctly during the wave.

const GOTHIC := preload("res://shaders/gothic.gdshader")
const GLASS := preload("res://shaders/glass.gdshader")
const FLAME := preload("res://shaders/flame.gdshader")

## family -> {albedo, rough, rim, extras...}
const FAMILIES := {
	"M_stone":      {"albedo": Color(0.62, 0.57, 0.47), "rough": 0.93, "rim": 0.3},
	"M_stone_trim": {"albedo": Color(0.71, 0.66, 0.55), "rough": 0.9, "rim": 0.4},
	"M_stone_dark": {"albedo": Color(0.42, 0.40, 0.36), "rough": 0.95, "rim": 0.22, "moss": 1.0},
	"M_iron":       {"albedo": Color(0.10, 0.105, 0.13), "rough": 0.55, "rim": 0.9, "wear": 0.25, "moss": 0.0, "crack": 0.0},
	"M_wood":       {"albedo": Color(0.23, 0.15, 0.09), "rough": 0.85, "rim": 0.25, "moss": 0.3},
	"M_gold":       {"albedo": Color(0.78, 0.55, 0.18), "rough": 0.35, "rim": 1.1, "moss": 0.0, "crack": 0.0,
					 "emission": Color(1.0, 0.75, 0.3), "emission_energy": 0.35, "emission_gate": 1},
	"M_wax":        {"albedo": Color(0.85, 0.79, 0.62), "rough": 0.6, "rim": 0.8, "moss": 0.0, "crack": 0.0},
	"M_cloth":      {"albedo": Color(0.58, 0.13, 0.16), "rough": 0.95, "rim": 0.8, "moss": 0.0, "crack": 0.0},
	"M_bell":       {"albedo": Color(0.36, 0.28, 0.15), "rough": 0.5, "rim": 0.8, "moss": 0.2, "crack": 0.0},
	"M_wraith":     {"albedo": Color(0.20, 0.24, 0.33), "rough": 0.75, "rim": 1.5, "moss": 0.0, "crack": 0.0,
					 "emission": Color(0.25, 0.38, 0.62), "emission_energy": 0.1},
	"M_robe":       {"albedo": Color(0.23, 0.24, 0.28), "rough": 0.95, "rim": 0.5, "moss": 0.0, "crack": 0.0},
	"M_robe_boss":  {"albedo": Color(0.16, 0.13, 0.17), "rough": 0.95, "rim": 0.6, "moss": 0.0, "crack": 0.0},
	"M_habit":      {"albedo": Color(0.72, 0.68, 0.60), "rough": 0.95, "rim": 0.45, "moss": 0.0, "crack": 0.0},
	"M_leather":    {"albedo": Color(0.30, 0.20, 0.12), "rough": 0.8, "rim": 0.35, "moss": 0.0, "crack": 0.0},
	"M_roof":       {"albedo": Color(0.20, 0.22, 0.27), "rough": 0.9, "rim": 0.3, "moss": 0.6, "crack": 0.0},
	"M_steel":      {"albedo": Color(0.62, 0.65, 0.70), "rough": 0.35, "rim": 1.0, "moss": 0.0, "crack": 0.0, "wear": 0.3},
}

static var _cache: Dictionary = {}

static func get_mat(family: String, state_mode := 0) -> Material:
	var key := "%s|%d" % [family, state_mode]
	if _cache.has(key):
		return _cache[key]
	var mat := ShaderMaterial.new()
	if family == "M_glass":
		mat.shader = GLASS
		mat.set_shader_parameter("state_mode", state_mode)
	elif family == "M_flame":
		mat.shader = FLAME
		mat.set_shader_parameter("state_mode", state_mode)
	else:
		mat.shader = GOTHIC
		var f: Dictionary = FAMILIES.get(family, FAMILIES["M_stone"])
		mat.set_shader_parameter("albedo", f["albedo"])
		mat.set_shader_parameter("roughness_v", f.get("rough", 0.9))
		mat.set_shader_parameter("rim_strength", f.get("rim", 0.35))
		mat.set_shader_parameter("wear_strength", f.get("wear", 0.5))
		mat.set_shader_parameter("moss_strength", f.get("moss", 0.85))
		mat.set_shader_parameter("crack_strength", f.get("crack", 0.45))
		mat.set_shader_parameter("emission_color", f.get("emission", Color.BLACK))
		mat.set_shader_parameter("emission_energy", f.get("emission_energy", 0.0))
		mat.set_shader_parameter("emission_gate", f.get("emission_gate", 0))
		mat.set_shader_parameter("state_mode", state_mode)
	_cache[key] = mat
	return mat
