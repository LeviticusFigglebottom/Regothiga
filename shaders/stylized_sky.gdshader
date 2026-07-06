shader_type sky;
// Stylized painterly sky for the world-shift kingdom. A banded gradient, a
// large soft "last light" sun low on the horizon, drifting cloud streaks that
// catch its glow, faint god-rays, and — as the world turns to ruin — a cold,
// darkened firmament pricked with stars. Driven per-state from EnvRig.blend().

uniform vec3 top_color : source_color = vec3(0.42, 0.30, 0.22);
uniform vec3 horizon_color : source_color = vec3(1.0, 0.66, 0.33);
uniform vec3 sun_color : source_color = vec3(1.0, 0.86, 0.55);
uniform vec3 ground_color : source_color = vec3(0.18, 0.13, 0.10);
uniform vec3 sun_dir = vec3(0.35, 0.16, -0.92);
uniform float ruin : hint_range(0.0, 1.0) = 0.0;

float hash(vec2 p) {
	return fract(sin(dot(p, vec2(41.31, 289.17))) * 43758.5453);
}
float vnoise(vec2 p) {
	vec2 i = floor(p), f = fract(p);
	f = f * f * (3.0 - 2.0 * f);
	float a = hash(i), b = hash(i + vec2(1.0, 0.0));
	float c = hash(i + vec2(0.0, 1.0)), d = hash(i + vec2(1.0, 1.0));
	return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
}
float fbm(vec2 p) {
	float v = 0.0, a = 0.55;
	for (int i = 0; i < 5; i++) { v += a * vnoise(p); p *= 2.03; a *= 0.5; }
	return v;
}

void sky() {
	vec3 dir = normalize(EYEDIR);
	float up = dir.y;

	// banded vertical gradient: ground -> hot horizon -> deep top
	vec3 col;
	if (up < 0.0) {
		col = mix(horizon_color * 0.5, ground_color, clamp(-up * 2.2, 0.0, 1.0));
	} else {
		float t = pow(clamp(up, 0.0, 1.0), 0.7);
		// a stylized mid-band gives the sky painterly color steps
		vec3 mid = mix(horizon_color, top_color, 0.45);
		col = mix(horizon_color, mid, smoothstep(0.0, 0.28, up));
		col = mix(col, top_color, smoothstep(0.22, 0.9, t));
	}

	// broad warm horizon bloom (fades in ruin)
	float hb = exp(-abs(up) * 5.0);
	col += horizon_color * hb * 0.45 * (1.0 - 0.8 * ruin);

	// the low sun: a large soft golden orb + wide halo + faint radial god-rays
	vec3 sd = normalize(sun_dir);
	float sun = max(dot(dir, sd), 0.0);
	float disc = smoothstep(0.985, 0.9965, sun);
	float halo = pow(sun, 20.0);
	float wide = pow(sun, 4.0);
	float rays = pow(sun, 7.0) * (0.6 + 0.4 * sin(atan(dir.x - sd.x, dir.y - sd.y) * 14.0));
	col = mix(col, sun_color * 1.6, disc * (1.0 - 0.25 * ruin));
	col += sun_color * (halo * 1.2 + wide * 0.3 + rays * 0.14 * (1.0 - ruin));

	// stylized cloud banks: big soft masses spread across the sky with finer
	// streaks riding them, all catching the low sun's light — painterly, not a
	// flat gradient. They drift slowly and thin out toward the zenith.
	vec2 cuv = vec2(atan(dir.x, dir.z), asin(clamp(up, -1.0, 1.0)));
	cuv.x = cuv.x * 1.05 + TIME * 0.005;
	float skyband = smoothstep(0.82, 0.04, up) * smoothstep(-0.02, 0.14, up);
	float mass = fbm(cuv * vec2(1.1, 2.1) + 2.0);
	mass = smoothstep(0.46, 0.76, mass);
	float streak = fbm(cuv * vec2(3.6, 1.5) - 4.0);
	streak = smoothstep(0.54, 0.86, streak);
	float clouds = clamp(mass * 0.9 + streak * 0.5, 0.0, 1.0) * skyband;
	float sunlit = pow(max(dot(dir, sd), 0.0), 2.5);
	// dark shadowed base so cloud masses read against the bright haze, warming
	// to a bright gold where the low sun rakes across them
	vec3 cloud_shadow = mix(top_color, horizon_color, 0.35) * 0.68;
	vec3 cloud_col = mix(cloud_shadow, sun_color * 1.4, sunlit);
	col = mix(col, cloud_col, clouds * (0.92 - 0.5 * ruin));
	// bright rims where the sun catches the cloud tops
	col += sun_color * streak * skyband * sunlit * 0.5 * (1.0 - ruin);

	// ruin: cold, darkened firmament pricked with stars
	if (ruin > 0.001) {
		vec3 night = col * 0.34 + vec3(0.10, 0.14, 0.22) * 0.5;
		float sky_mask = smoothstep(0.02, 0.35, up);
		vec2 sc = floor(dir.xz / max(up + 0.15, 0.05) * 90.0);
		float star = step(0.9975, hash(sc)) * sky_mask;
		float tw = 0.6 + 0.4 * sin(TIME * 2.0 + hash(sc) * 30.0);
		night += vec3(0.75, 0.82, 1.0) * star * tw;
		col = mix(col, night, ruin);
	}

	COLOR = col;
}
