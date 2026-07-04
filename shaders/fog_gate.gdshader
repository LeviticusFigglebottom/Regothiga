shader_type spatial;
render_mode cull_disabled, unshaded, blend_mix, depth_draw_never;

// The pale: a slow-breathing veil of candle-smoke light.

uniform vec3 tint : source_color = vec3(0.82, 0.8, 0.72);
uniform float density : hint_range(0.0, 1.0) = 0.55;

varying vec3 v_lp;

float hash13(vec3 p3) {
	p3 = fract(p3 * 0.1031);
	p3 += dot(p3, p3.zyx + 31.32);
	return fract((p3.x + p3.y) * p3.z);
}

float vnoise(vec3 p) {
	vec3 i = floor(p);
	vec3 f = fract(p);
	f = f * f * (3.0 - 2.0 * f);
	return mix(mix(mix(hash13(i), hash13(i + vec3(1, 0, 0)), f.x),
		mix(hash13(i + vec3(0, 1, 0)), hash13(i + vec3(1, 1, 0)), f.x), f.y),
		mix(mix(hash13(i + vec3(0, 0, 1)), hash13(i + vec3(1, 0, 1)), f.x),
		mix(hash13(i + vec3(0, 1, 1)), hash13(i + vec3(1, 1, 1)), f.x), f.y), f.z);
}

void vertex() {
	v_lp = VERTEX;
}

void fragment() {
	vec2 uv = v_lp.xy;
	float n = vnoise(vec3(uv * 1.8, TIME * 0.22)) * 0.6
			+ vnoise(vec3(uv * 4.4 + 7.0, TIME * 0.4)) * 0.4;
	float body = smoothstep(0.18, 0.72, n);
	// soft edges toward the frame
	float edge_x = smoothstep(1.55, 1.0, abs(uv.x));
	float edge_y = smoothstep(0.0, 0.5, uv.y + 1.45) * smoothstep(3.2, 2.4, uv.y + 1.45);
	ALBEDO = tint * (0.55 + 0.45 * n);
	EMISSION = tint * body * 0.5;
	ALPHA = clamp(body * density * edge_x * edge_y + 0.12 * edge_x * edge_y, 0.0, 0.9);
}
