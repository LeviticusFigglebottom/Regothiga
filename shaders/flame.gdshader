shader_type spatial;
render_mode cull_disabled, unshaded;

// Candle / lantern flames: emissive teardrop that sways and flickers.
// flame_tint is per-instance so the vigil flame can burn gold in glory
// and cold blue in ruin.

instance uniform vec3 flame_tint : source_color = vec3(1.0, 0.72, 0.30);
instance uniform float flame_energy = 3.2;
uniform int state_mode = 0;

global uniform float vg_wave_r;
global uniform vec3 vg_wave_origin;
global uniform float vg_wave_dir;
global uniform float vg_state_blend;
global uniform float vg_wave_band;

varying float v_h;
varying vec3 v_world_pos;

float hash11(float n) {
	return fract(sin(n) * 43758.5453);
}

float local_ruin(vec3 wp) {
	if (vg_wave_r < -500.0) {
		return vg_state_blend;
	}
	float d = distance(wp, vg_wave_origin);
	float w = smoothstep(0.0, 1.0, clamp((vg_wave_r - d) / vg_wave_band, 0.0, 1.0));
	return mix(vg_state_blend, vg_wave_dir, w);
}

void vertex() {
	v_h = VERTEX.y;
	vec3 wp = (MODEL_MATRIX * vec4(0.0, 0.0, 0.0, 1.0)).xyz;
	float phase = wp.x * 3.1 + wp.z * 5.7;
	float sway = sin(TIME * 7.0 + phase) * 0.06 + sin(TIME * 13.7 + phase * 2.0) * 0.03;
	VERTEX.x += sway * VERTEX.y * 4.0;
	VERTEX.z += cos(TIME * 9.3 + phase) * 0.04 * VERTEX.y * 4.0;
	VERTEX.y *= 1.0 + sin(TIME * 11.0 + phase) * 0.08;
	v_world_pos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

void fragment() {
	float ruin = local_ruin(v_world_pos);
	float presence = 1.0;
	if (state_mode == 1) {
		presence = 1.0 - ruin;
	} else if (state_mode == 2) {
		presence = ruin;
	}
	if (presence < 0.5) {
		discard;
	}
	float flicker = 0.85 + 0.15 * sin(TIME * 17.0 + v_world_pos.x * 20.0);
	vec3 core = mix(flame_tint, vec3(1.0, 0.98, 0.9), clamp(1.0 - v_h * 6.0, 0.0, 1.0) * 0.8);
	ALBEDO = vec3(0.0);
	EMISSION = core * flame_energy * flicker;
}
