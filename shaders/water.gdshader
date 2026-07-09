shader_type spatial;
render_mode specular_schlick_ggx, cull_back;
// Canal water: two counter-scrolling ripple fields perturb the normal so the
// dusk sky and torchlight break up across the surface; a fresnel term deepens
// the color at glancing angles so the flats read as standing water, not paint.

uniform int state_mode = 0;              // pipeline compat (base layer: unused)
uniform vec4 deep_color : source_color = vec4(0.045, 0.075, 0.085, 1.0);
uniform vec4 shallow_color : source_color = vec4(0.13, 0.185, 0.175, 1.0);
uniform float ripple_scale = 1.25;
uniform float ripple_speed = 0.055;
uniform float ripple_height = 1.05;
uniform float flow_x = 1.0;              // dominant drift direction (world x)

varying vec3 wpos;

float hash13(vec3 p3) {
	p3 = fract(p3 * 0.1031);
	p3 += dot(p3, p3.zyx + 31.32);
	return fract((p3.x + p3.y) * p3.z);
}

float vnoise2(vec2 p) {
	vec2 i = floor(p);
	vec2 f = fract(p);
	f = f * f * (3.0 - 2.0 * f);
	float a = hash13(vec3(i, 0.0));
	float b = hash13(vec3(i + vec2(1, 0), 0.0));
	float c = hash13(vec3(i + vec2(0, 1), 0.0));
	float d = hash13(vec3(i + vec2(1, 1), 0.0));
	return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
}

float ripple(vec2 p, float t) {
	float n = vnoise2(p + vec2(t * flow_x, t * 0.35)) * 0.55;
	n += vnoise2(p * 2.7 - vec2(t * 1.6 * flow_x, -t * 0.7)) * 0.3;
	n += vnoise2(p * 6.3 + vec2(t * 2.3 * flow_x, t * 1.1)) * 0.15;   // chop
	return n;
}

void vertex() {
	wpos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

void fragment() {
	float t = TIME * ripple_speed * 10.0;
	vec2 p = wpos.xz * ripple_scale;
	// finite-difference normal from the ripple height field
	float e = 0.35;
	float h0 = ripple(p, t);
	float hx = ripple(p + vec2(e, 0.0), t);
	float hz = ripple(p + vec2(0.0, e), t);
	vec3 n = normalize(vec3((h0 - hx) * ripple_height, 1.0, (h0 - hz) * ripple_height));
	NORMAL = normalize(mix(NORMAL, (VIEW_MATRIX * vec4(n, 0.0)).xyz, 0.85));

	float fres = pow(1.0 - clamp(dot(normalize(-VERTEX), NORMAL), 0.0, 1.0), 3.0);
	vec3 col = mix(shallow_color.rgb, deep_color.rgb, clamp(0.35 + fres * 0.65, 0.0, 1.0));
	// crest sheen: tight bands riding the ripple tops so lamplight breaks
	// into moving glints instead of a flat smear
	float sheen = smoothstep(0.66, 0.9, h0);
	col += vec3(0.11, 0.12, 0.11) * sheen * (0.4 + fres);
	ALBEDO = col;
	// a whisper of self-light so night water still glints as water
	EMISSION = vec3(0.05, 0.065, 0.075) * (sheen * 0.6 + fres * 0.5) * 0.6;
	ROUGHNESS = 0.035 + 0.16 * h0;
	SPECULAR = 0.62;
	METALLIC = 0.0;
}
