class_name EnvRig
extends Node3D
## Owns the WorldEnvironment + sun for an area and blends between the glory
## and ruin lighting profiles (data/state_profiles.json). The blend runs
## during the transformation wave; at rest it sits at 0 or 1.

var world_env: WorldEnvironment
var sun: DirectionalLight3D
var sky_mat: ShaderMaterial

var profiles: Dictionary = {}

func _ready() -> void:
	var f := FileAccess.open("res://data/state_profiles.json", FileAccess.READ)
	profiles = JSON.parse_string(f.get_as_text())

	world_env = WorldEnvironment.new()
	var e := Environment.new()
	e.background_mode = Environment.BG_SKY
	sky_mat = ShaderMaterial.new()
	sky_mat.shader = preload("res://shaders/stylized_sky.gdshader")
	var sky := Sky.new()
	sky.radiance_size = Sky.RADIANCE_SIZE_128
	sky.sky_material = sky_mat
	e.sky = sky
	e.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	e.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	e.fog_enabled = true
	e.fog_sky_affect = 0.2
	e.volumetric_fog_enabled = true
	e.volumetric_fog_anisotropy = 0.62
	e.volumetric_fog_length = 80.0
	e.glow_enabled = true
	e.glow_bloom = 0.12
	e.glow_hdr_threshold = 1.0
	world_env.environment = e
	add_child(world_env)

	sun = DirectionalLight3D.new()
	sun.shadow_enabled = true
	sun.shadow_bias = 0.028
	sun.shadow_normal_bias = 1.2
	sun.shadow_blur = 1.2
	sun.directional_shadow_mode = DirectionalLight3D.SHADOW_PARALLEL_4_SPLITS
	sun.directional_shadow_max_distance = 120.0
	add_child(sun)

func _c(v: Array) -> Color:
	return Color(v[0], v[1], v[2])

## t: 0 = glory, 1 = ruin
func blend(t: float) -> void:
	var a: Dictionary = profiles["glory"]
	var b: Dictionary = profiles["ruin"]
	var e := world_env.environment
	var sc := _c(a["sun_color"]).lerp(_c(b["sun_color"]), t)
	sun.light_color = sc
	sun.light_energy = lerpf(a["sun_energy"], b["sun_energy"], t)
	var ra: Array = a["sun_rot"]
	var rb: Array = b["sun_rot"]
	sun.rotation_degrees = Vector3(lerpf(ra[0], rb[0], t), lerpf(ra[1], rb[1], t), 0)
	e.ambient_light_color = _c(a["ambient"]).lerp(_c(b["ambient"]), t)
	e.ambient_light_energy = lerpf(a["ambient_energy"], b["ambient_energy"], t)
	e.fog_light_color = _c(a["fog_color"]).lerp(_c(b["fog_color"]), t)
	e.fog_density = lerpf(a["fog_density"], b["fog_density"], t)
	e.volumetric_fog_density = lerpf(a["vol_density"], b["vol_density"], t)
	e.volumetric_fog_albedo = _c(a["vol_albedo"]).lerp(_c(b["vol_albedo"]), t)
	e.tonemap_exposure = lerpf(a["exposure"], b["exposure"], t)
	e.glow_intensity = lerpf(a["glow"], b["glow"], t)
	var top := _c(a["bg_top"]).lerp(_c(b["bg_top"]), t)
	var horizon := _c(a["bg_horizon"]).lerp(_c(b["bg_horizon"]), t)
	sky_mat.set_shader_parameter("top_color", top)
	sky_mat.set_shader_parameter("horizon_color", horizon)
	sky_mat.set_shader_parameter("sun_color", sc)
	sky_mat.set_shader_parameter("ground_color", horizon.darkened(0.72))
	sky_mat.set_shader_parameter("ruin", t)
	# place the sky's sun disc where the directional light streams from
	var sb := Basis.from_euler(Vector3(deg_to_rad(lerpf(ra[0], rb[0], t)),
			deg_to_rad(lerpf(ra[1], rb[1], t)), 0.0))
	sky_mat.set_shader_parameter("sun_dir", sb.z)

func snap(state: VG.WState) -> void:
	blend(1.0 if state == VG.WState.RUIN else 0.0)

func music_for(state: VG.WState) -> String:
	var p: Dictionary = profiles[VG.STATE_NAMES[state]]
	return p.get("music", "")

func ambience_for(state: VG.WState) -> String:
	var p: Dictionary = profiles[VG.STATE_NAMES[state]]
	return p.get("ambience", "")
