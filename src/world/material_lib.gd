class_name MaterialLib
## The single source of visual truth: every kit surface maps to one of these
## shared ShaderMaterials. Variants exist per state-mode (base / glory-only /
## ruin-only) so layer-exclusive meshes dissolve correctly during the wave.

const GOTHIC := preload("res://shaders/gothic.gdshader")
const GOTHIC_DS := preload("res://shaders/gothic_ds.gdshader")
## Thin-shell families rendered double-sided (backface normal flipped in the
## shader). Empty on purpose: cull-off shading washed out lit roof slopes
## (wrong shadow bias on what were backfaces) — the gable kits emit true
## two-sided GEOMETRY instead, which lights and shadows correctly.
const DOUBLE_SIDED := {}

const TEXTURES := {
	"M_stone":      ["T_stone", 0.5, 0.62],
	"M_stone_trim": ["T_trim", 0.7, 0.5],
	"M_stone_dark": ["T_floor", 0.5, 0.66],
	"M_wood":       ["T_wood", 0.9, 0.6],
	"M_roof":       ["T_roof", 0.5, 0.75],
	"M_cloth":      ["T_cloth", 1.4, 0.32],
	"M_iron":       ["T_iron", 1.2, 0.45],
	"M_wax":        ["T_wax", 1.1, 0.4],
	"M_bell":       ["T_bronze", 0.8, 0.6],
	"M_bronze":     ["T_bronze", 1.0, 0.55],
	"M_mosaic":     ["T_mosaic", 0.55, 0.72],
	"M_bone":       ["T_bone", 0.9, 0.7],
	"M_shroud":     ["T_cloth", 2.0, 0.35],
	"M_leather":    ["T_wax", 1.6, 0.35],
	"M_robe":       ["T_cloth", 1.8, 0.4],
	"M_robe_boss":  ["T_cloth", 1.4, 0.45],
	"M_habit":      ["T_cloth", 1.8, 0.45],
	"M_wraith":     ["T_cloth", 1.6, 0.3],
	"M_backdrop":   ["T_stone", 0.16, 0.5],
	"M_terrain":    ["T_stone", 0.45, 0.55],
	"M_steel":      ["T_iron", 1.4, 0.35],
}
const GLASS := preload("res://shaders/glass.gdshader")
const FLAME := preload("res://shaders/flame.gdshader")
const WATER := preload("res://shaders/water.gdshader")

## family -> {albedo, rough, rim, extras...}
const FAMILIES := {
	"M_stone":      {"albedo": Color(0.62, 0.57, 0.47), "rough": 0.93, "rim": 0.3},
	"M_stone_trim": {"albedo": Color(0.71, 0.66, 0.55), "rough": 0.9, "rim": 0.4},
	"M_stone_dark": {"albedo": Color(0.42, 0.40, 0.36), "rough": 0.95, "rim": 0.22, "moss": 1.0},
	"M_iron":       {"albedo": Color(0.10, 0.105, 0.13), "rough": 0.55, "rim": 0.9, "wear": 0.25, "moss": 0.0, "crack": 0.0},
	"M_wood":       {"albedo": Color(0.23, 0.15, 0.09), "rough": 0.85, "rim": 0.25, "moss": 0.3},
	"M_gold":       {"albedo": Color(0.78, 0.55, 0.18), "rough": 0.35, "rim": 1.1, "moss": 0.0, "crack": 0.0,
					 "emission": Color(1.0, 0.75, 0.3), "emission_energy": 0.35, "emission_gate": 1},
	"M_ember":      {"albedo": Color(0.5, 0.14, 0.05), "rough": 0.8, "rim": 0.3, "moss": 0.0, "crack": 0.0,
					 "emission": Color(1.0, 0.42, 0.12), "emission_energy": 2.6, "emission_gate": 1},
	"M_wax":        {"albedo": Color(0.85, 0.79, 0.62), "rough": 0.6, "rim": 0.8, "moss": 0.0, "crack": 0.0},
	"M_cloth":      {"albedo": Color(0.44, 0.07, 0.10), "rough": 0.95, "rim": 0.5, "moss": 0.0, "crack": 0.0},
	"M_bell":       {"albedo": Color(0.38, 0.27, 0.13), "rough": 0.48, "rim": 0.85, "moss": 0.15, "crack": 0.0},
	"M_bronze":     {"albedo": Color(0.34, 0.24, 0.12), "rough": 0.45, "rim": 1.0, "moss": 0.0, "crack": 0.0,
					 "emission": Color(0.45, 0.3, 0.1), "emission_energy": 0.06},
	"M_mosaic":     {"albedo": Color(0.58, 0.46, 0.28), "rough": 0.7, "rim": 0.5, "moss": 0.15, "crack": 0.2},
	"M_bone":       {"albedo": Color(0.72, 0.68, 0.56), "rough": 0.85, "rim": 0.6, "moss": 0.1, "crack": 0.25},
	"M_shroud":     {"albedo": Color(0.62, 0.6, 0.54), "rough": 0.98, "rim": 0.4, "moss": 0.0, "crack": 0.0},
	"M_wraith":     {"albedo": Color(0.20, 0.24, 0.33), "rough": 0.75, "rim": 1.5, "moss": 0.0, "crack": 0.0,
					 "emission": Color(0.25, 0.38, 0.62), "emission_energy": 0.1},
	"M_robe":       {"albedo": Color(0.23, 0.24, 0.28), "rough": 0.95, "rim": 0.5, "moss": 0.0, "crack": 0.0},
	"M_robe_boss":  {"albedo": Color(0.24, 0.19, 0.26), "rough": 0.95, "rim": 1.1, "moss": 0.0, "crack": 0.0},
	"M_habit":      {"albedo": Color(0.55, 0.51, 0.44), "rough": 0.95, "rim": 0.45, "moss": 0.0, "crack": 0.0},
	"M_leather":    {"albedo": Color(0.30, 0.20, 0.12), "rough": 0.8, "rim": 0.35, "moss": 0.0, "crack": 0.0},
	# deep slate: lit slopes must stay dark enough to sit INTO the dusk grade
	# (the old 0.33-0.40 albedo read as flat white once lit sides became visible)
	"M_roof":       {"albedo": Color(0.14, 0.13, 0.14), "rough": 0.95, "rim": 0.25, "moss": 0.5, "crack": 0.0},
	"M_backdrop":   {"albedo": Color(0.72, 0.60, 0.47), "rough": 1.0, "rim": 0.15, "moss": 0.0, "crack": 0.0, "wear": 0.15},
	"M_backdrop_dark": {"albedo": Color(0.16, 0.12, 0.10), "rough": 1.0, "rim": 0.0, "moss": 0.0, "crack": 0.0},
	# city gilding: gold ridges/finials/domes on the panorama. Faint glory-gated
	# glow so the kingdom reads gilded at dusk; in ruin the gate kills it and the
	# cold grade tarnishes the albedo.
	"M_gild":       {"albedo": Color(0.82, 0.60, 0.22), "rough": 0.38, "rim": 1.0, "moss": 0.0, "crack": 0.0,
					 "emission": Color(1.0, 0.78, 0.32), "emission_energy": 0.22, "emission_gate": 1},
	# lit dwelling windows across the city — warm lamplight in glory, dead dark
	# panes in ruin (same gate the votive gold uses).
	"M_citywindow": {"albedo": Color(0.14, 0.10, 0.08), "rough": 0.9, "rim": 0.1, "moss": 0.0, "crack": 0.0,
					 "emission": Color(1.0, 0.66, 0.28), "emission_energy": 1.7, "emission_gate": 1},
	# the drowned flats: near-black wet peat with a low-rough sheen
	"M_marsh":      {"albedo": Color(0.10, 0.13, 0.11), "rough": 0.3, "rim": 0.5, "moss": 1.0, "crack": 0.0},
	# the valley floor between the panorama's terraces: dark packed earth, so
	# exposed ground reads as ground — not as a bright hole in the map
	"M_terrain":    {"albedo": Color(0.15, 0.12, 0.09), "rough": 1.0, "rim": 0.05, "moss": 0.45, "crack": 0.0},
	"M_steel":      {"albedo": Color(0.62, 0.65, 0.70), "rough": 0.35, "rim": 1.0, "moss": 0.0, "crack": 0.0, "wear": 0.3},
	"M_foliage":    {"albedo": Color(0.2, 0.32, 0.16), "rough": 0.95, "rim": 0.55, "moss": 0.0, "crack": 0.0, "vc": 1},
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
	elif family == "M_water":
		mat.shader = WATER
		mat.set_shader_parameter("state_mode", state_mode)
	elif family == "M_flame":
		mat.shader = FLAME
		mat.set_shader_parameter("state_mode", state_mode)
	else:
		mat.shader = GOTHIC_DS if DOUBLE_SIDED.has(family) else GOTHIC
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
		mat.set_shader_parameter("albedo_from_vc", f.get("vc", 0))
		if TEXTURES.has(family):
			var spec: Array = TEXTURES[family]
			var tex := load("res://assets/textures/%s.png" % spec[0])
			if tex != null:
				mat.set_shader_parameter("detail_tex", tex)
				mat.set_shader_parameter("tex_scale", spec[1])
				mat.set_shader_parameter("tex_strength", spec[2])
	_cache[key] = mat
	return mat
