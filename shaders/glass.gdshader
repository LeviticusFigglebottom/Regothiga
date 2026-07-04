shader_type spatial;
render_mode cull_disabled, depth_draw_opaque;

// Stained glass: vertex colors are the jewel tones; glory makes them burn
// with light, ruin leaves them dead and dark. Participates in the wave.

uniform float glory_glow = 2.6;
uniform float ruin_glow = 0.12;
uniform int state_mode = 0;

global uniform float vg_wave_r;
global uniform vec3 vg_wave_origin;
global uniform float vg_wave_dir;
global uniform float vg_state_blend;
global uniform float vg_wave_band;
global uniform vec3 vg_wave_color;

varying vec3 v_world_pos;
varying vec4 v_col;

float hash13(vec3 p3) {
	p3 = fract(p3 * 0.1031);
	p3 += dot(p3, p3.zyx + 31.32);
	return fract((p3.x + p3.y) * p3.z);
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
	v_world_pos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	v_col = COLOR;
}

void fragment() {
	float ruin = local_ruin(v_world_pos);
	float presence = 1.0;
	if (state_mode == 1) {
		presence = 1.0 - ruin;
	} else if (state_mode == 2) {
		presence = ruin;
	}
	if (presence < 0.999 && presence < hash13(floor(v_world_pos * 14.0))) {
		discard;
	}
	ALBEDO = v_col.rgb * 0.5;
	ROUGHNESS = 0.2;
	METALLIC = 0.0;
	float glow = mix(glory_glow, ruin_glow, ruin);
	EMISSION = v_col.rgb * glow;

	if (vg_wave_r > -500.0) {
		float d = distance(v_world_pos, vg_wave_origin);
		float t = 1.0 - clamp(abs(vg_wave_r - d) / vg_wave_band, 0.0, 1.0);
		EMISSION += vg_wave_color * pow(t, 3.0) * 2.0;
	}
}
