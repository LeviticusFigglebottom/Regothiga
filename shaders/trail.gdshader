shader_type spatial;
render_mode cull_disabled, unshaded, blend_add, depth_draw_never;

// Weapon swing trail: additive arc that fades along its length.

uniform vec3 tint : source_color = vec3(1.0, 0.9, 0.65);
uniform float energy = 1.4;

void fragment() {
	float fade = (1.0 - UV.x) * smoothstep(0.0, 0.15, UV.y) * smoothstep(1.0, 0.75, UV.y);
	ALBEDO = vec3(0.0);
	EMISSION = tint * energy * fade;
	ALPHA = fade * 0.85;
}
