shader_type spatial;
render_mode cull_disabled, depth_draw_opaque;

// ---------------------------------------------------------------------------
// gothic_ds.gdshader — GENERATED twin of gothic.gdshader (keep in sync):
// identical shading with cull_disabled + backface normal flip, for thin
// shell surfaces (roof planes) that must read from both sides.
// Provides: stylized ramp shading, per-fragment glory↔ruin morphing, and the
// transformation wavefront (dissolve + edge glow), driven by global uniforms
// set by StateDirector. See DECISIONS.md D-003.
// ---------------------------------------------------------------------------

// Surface family parameters (set by MaterialLib per family)
uniform vec4 albedo : source_color = vec4(0.7, 0.66, 0.58, 1.0);
uniform float roughness_v : hint_range(0.0, 1.0) = 0.92;
uniform float rim_strength : hint_range(0.0, 2.0) = 0.35;
uniform float detail_scale = 1.6;
uniform float detail_strength : hint_range(0.0, 1.0) = 0.35;
uniform float wear_strength : hint_range(0.0, 1.0) = 0.5;
uniform float moss_strength : hint_range(0.0, 1.0) = 0.85;
uniform float crack_strength : hint_range(0.0, 1.0) = 0.45;
uniform float ramp_quantize : hint_range(0.0, 1.0) = 0.34;

// painted detail overlay (triplanar, world-space — the kit has no UVs)
uniform sampler2D detail_tex : hint_default_white, filter_linear_mipmap, repeat_enable;
uniform float tex_scale = 0.5;
uniform float tex_strength : hint_range(0.0, 1.0) = 0.0;

// Emission (candle gold trim, etc). gate: 0 = always, 1 = glory only, 2 = ruin only
uniform vec3 emission_color : source_color = vec3(0.0);
uniform float emission_energy = 0.0;
uniform int emission_gate = 0;

// State behavior: 0 = base (present in both states, morphs)
//                 1 = glory-only (dissolves out as ruin arrives)
//                 2 = ruin-only  (dissolves in as ruin arrives)
uniform int state_mode = 0;
uniform int albedo_from_vc = 0;   // foliage: COLOR carries paint, not masks

// per-instance dissolve (deaths, pickups fading out)
instance uniform float death_diss : hint_range(0.0, 1.0) = 0.0;

// Transformation wave (global — one knob moves the whole world)
global uniform float vg_wave_r;
global uniform vec3 vg_wave_origin;
global uniform float vg_wave_dir;     // target state during wave: 0 glory, 1 ruin
global uniform float vg_state_blend;  // resting state: 0 glory, 1 ruin
global uniform float vg_wave_band;
global uniform vec3 vg_wave_color;

varying vec3 v_world_pos;
varying vec3 v_world_nrm;
varying vec4 v_col;

// cheap deterministic value noise -------------------------------------------
float hash13(vec3 p3) {
	p3 = fract(p3 * 0.1031);
	p3 += dot(p3, p3.zyx + 31.32);
	return fract((p3.x + p3.y) * p3.z);
}

float vnoise(vec3 p) {
	vec3 i = floor(p);
	vec3 f = fract(p);
	f = f * f * (3.0 - 2.0 * f);
	float n000 = hash13(i);
	float n100 = hash13(i + vec3(1, 0, 0));
	float n010 = hash13(i + vec3(0, 1, 0));
	float n110 = hash13(i + vec3(1, 1, 0));
	float n001 = hash13(i + vec3(0, 0, 1));
	float n101 = hash13(i + vec3(1, 0, 1));
	float n011 = hash13(i + vec3(0, 1, 1));
	float n111 = hash13(i + vec3(1, 1, 1));
	return mix(mix(mix(n000, n100, f.x), mix(n010, n110, f.x), f.y),
	           mix(mix(n001, n101, f.x), mix(n011, n111, f.x), f.y), f.z);
}

// how ruined is this fragment right now? ------------------------------------
float local_ruin(vec3 wp) {
	if (vg_wave_r < -500.0) {
		return vg_state_blend;
	}
	float d = distance(wp, vg_wave_origin);
	float w = smoothstep(0.0, 1.0, clamp((vg_wave_r - d) / vg_wave_band, 0.0, 1.0));
	return mix(vg_state_blend, vg_wave_dir, w);
}

float wave_edge(vec3 wp) {
	if (vg_wave_r < -500.0) {
		return 0.0;
	}
	float d = distance(wp, vg_wave_origin);
	float t = 1.0 - clamp(abs(vg_wave_r - d) / vg_wave_band, 0.0, 1.0);
	return pow(t, 3.0);
}

void vertex() {
	v_world_pos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	v_world_nrm = normalize((MODEL_MATRIX * vec4(NORMAL, 0.0)).xyz);
	v_col = COLOR;
}

void fragment() {
	if (!FRONT_FACING) {
		NORMAL = -NORMAL;
	}
	float ruin = local_ruin(v_world_pos);

	// presence / dissolve for state-exclusive meshes
	float presence = 1.0;
	if (state_mode == 1) {
		presence = 1.0 - ruin;
	} else if (state_mode == 2) {
		presence = ruin;
	}
	float diss_n = hash13(floor(v_world_pos * 6.0));
	if (presence < 0.999) {
		if (presence < diss_n) {
			discard;
		}
	}
	if (death_diss > 0.001) {
		float dn = hash13(floor(v_world_pos * 14.0));
		if (death_diss > dn) {
			discard;
		}
	}

	// masks: R wear, G moss zone, B ao (unless COLOR is the albedo itself)
	float wear = v_col.r * wear_strength;
	float mossm = v_col.g;
	float ao = mix(1.0, v_col.b, 0.85);
	if (albedo_from_vc == 1) {
		wear = 0.0;
		mossm = 0.0;
		ao = 1.0;
	}

	// detail noise breakup so bare stone reads
	float n1 = vnoise(v_world_pos * detail_scale);
	float n2 = vnoise(v_world_pos * detail_scale * 3.7 + 11.0);
	vec3 base = albedo.rgb * (1.0 - detail_strength * 0.5 + detail_strength * (n1 * 0.7 + n2 * 0.3));
	if (albedo_from_vc == 1) {
		base = v_col.rgb * (0.85 + 0.3 * n1);
	}

	// painterly texture overlay: 3-tap triplanar, value-centered at 0.5
	if (tex_strength > 0.001) {
		vec3 an = abs(v_world_nrm);
		vec3 tw = pow(an, vec3(4.0));
		tw /= (tw.x + tw.y + tw.z);
		float tx = texture(detail_tex, v_world_pos.zy * tex_scale).r;
		float ty = texture(detail_tex, v_world_pos.xz * tex_scale).r;
		float tz = texture(detail_tex, v_world_pos.xy * tex_scale).r;
		float td = tx * tw.x + ty * tw.y + tz * tw.z;
		base *= mix(1.0, td * 2.0, tex_strength);
	}

	// edge-chip highlight from wear mask (reads in both states)
	base = mix(base, base * 1.22 + vec3(0.03), wear * 0.5);

	// GLORY look: clean warm stone
	vec3 glory_col = base * vec3(1.05, 1.0, 0.92);

	// RUIN look: desaturated, cold, mossy, cracked
	float g = dot(base, vec3(0.3333));
	vec3 ruin_col = mix(base, vec3(g), 0.55) * vec3(0.80, 0.87, 1.04);
	float moss_up = clamp(v_world_nrm.y * 0.5 + 0.62, 0.0, 1.0);
	float moss = mossm * moss_strength * moss_up * smoothstep(0.35, 0.75, n1);
	ruin_col = mix(ruin_col, vec3(0.16, 0.21, 0.12), clamp(moss, 0.0, 0.85));
	float crack = smoothstep(0.79, 0.85, n2) * crack_strength;
	ruin_col *= 1.0 - crack * 0.5;

	ALBEDO = mix(glory_col, ruin_col, ruin);
	ROUGHNESS = clamp(roughness_v + ruin * 0.05 - wear * 0.1, 0.05, 1.0);
	AO = mix(1.0, ao, 0.9 + ruin * 0.1);
	AO_LIGHT_AFFECT = 0.35;

	// rim: warm candlelight kiss in glory, cold moon rim in ruin
	float fres = pow(1.0 - clamp(dot(normalize(v_world_nrm), normalize(CAMERA_POSITION_WORLD - v_world_pos)), 0.0, 1.0), 3.0);
	vec3 rim_c = mix(vec3(1.0, 0.82, 0.58), vec3(0.55, 0.68, 0.95), ruin);
	vec3 emis = rim_c * fres * rim_strength * 0.25;

	// surface emission (gold trim, wax glow) gated by state
	float gate = 1.0;
	if (emission_gate == 1) {
		gate = 1.0 - ruin;
	} else if (emission_gate == 2) {
		gate = ruin;
	}
	emis += emission_color * emission_energy * gate;

	// the wavefront: burning edge as the world remembers / forgets
	float edge = wave_edge(v_world_pos);
	float diss_edge = 0.0;
	if (state_mode != 0 && presence < 0.999) {
		diss_edge = 1.0 - smoothstep(0.0, 0.25, presence - diss_n);
	}
	emis += vg_wave_color * (edge * 5.5 + diss_edge * edge * 14.0);
	if (death_diss > 0.001) {
		float dn2 = hash13(floor(v_world_pos * 14.0));
		emis += vec3(0.6, 0.75, 1.2) * (1.0 - smoothstep(0.0, 0.2, dn2 - death_diss)) * 2.0;
	}

	EMISSION = emis;
	SPECULAR = 0.15;
}

void light() {
	// half-lambert, partially quantized: painterly, never flat
	float ndl = dot(normalize(NORMAL), normalize(LIGHT)) * 0.5 + 0.5;
	float band = floor(ndl * 3.0) / 3.0 + 0.1667;
	float ramp = mix(ndl, band, ramp_quantize);
	ramp *= ramp;
	DIFFUSE_LIGHT += ramp * ATTENUATION * LIGHT_COLOR * ALBEDO / PI;
}
