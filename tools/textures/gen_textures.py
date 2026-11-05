#!/usr/bin/env python3
"""High-Fidelity Dark Souls PBR Texture Synthesizer for Vespergard.

Generates 1024x1024 seamless multi-map texture suites in assets/textures/:
  * T_<name>.png     — High-contrast RGB detail/albedo modulation (centered ~0.5 per channel)
  * T_<name>_n.png   — Tangent-space Normal Map (RGB: X+, Y+, Z+ encoded, macro bevel + micro grit)
  * T_<name>_orm.png — Packed RGBA:
        R = Cavity / Micro-Ambient Occlusion (0..1)
        G = Micro-Roughness Multiplier (centered at 0.5)
        B = Metallic / Specular Reflectance Mask (0..1)
        A = Heightfield (0..1, for height-blended moss, cracks, and wetness)

Deterministic (fixed seeds), pure NumPy + PIL.
"""
import os
import numpy as np
from PIL import Image

OUT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "assets",
    "textures",
)
N = 1024


def blur_wrap(img, passes=1):
    for _ in range(passes):
        img = (
            img * 2.0
            + np.roll(img, 1, 0)
            + np.roll(img, -1, 0)
            + np.roll(img, 1, 1)
            + np.roll(img, -1, 1)
        ) / 6.0
    return img


def vnoise(freq, seed, octaves=4, gain=0.54):
    r = np.random.default_rng(seed)
    out = np.zeros((N, N), dtype=np.float32)
    amp, total = 1.0, 0.0
    for o in range(octaves):
        f = min(N // 2, freq * (2 ** o))
        small = r.random((f, f), dtype=np.float32)
        pil_s = Image.fromarray((small * 255).astype(np.uint8), mode="L")
        tiled = Image.new("L", (f * 2, f * 2))
        for tx in (0, f):
            for ty in (0, f):
                tiled.paste(pil_s, (tx, ty))
        up = tiled.resize((N * 2, N * 2), Image.Resampling.BICUBIC)
        half = N // 2
        cropped = up.crop((half, half, half + N, half + N))
        layer = np.asarray(cropped, dtype=np.float32) / 255.0
        out += layer * amp
        total += amp
        amp *= gain
    out /= max(total, 1e-9)
    lo, hi = out.min(), out.max()
    return (out - lo) / max(hi - lo, 1e-9)


def high_freq_grit(seed):
    """Crisp high-frequency granular stone/metal pore grit without bicubic blur."""
    r = np.random.default_rng(seed)
    g1 = vnoise(64, seed + 1, octaves=3, gain=0.6)
    g2 = vnoise(128, seed + 2, octaves=2, gain=0.65)
    fine = r.random((N // 2, N // 2), dtype=np.float32)
    pil_f = Image.fromarray((fine * 255).astype(np.uint8), mode="L").resize((N, N), Image.Resampling.BILINEAR)
    g3 = np.asarray(pil_f, dtype=np.float32) / 255.0
    grit = g1 * 0.48 + g2 * 0.34 + g3 * 0.18
    lo, hi = grit.min(), grit.max()
    return (grit - lo) / max(hi - lo, 1e-9)


def ridged_cracks(seed, freq=10):
    """Sharp ridged multifractal hairline fissures across stone/flagstone."""
    n1 = vnoise(freq, seed, octaves=4, gain=0.55)
    n2 = vnoise(freq * 2, seed + 7, octaves=3, gain=0.55)
    r1 = np.clip(1.0 - np.abs(n1 * 2.0 - 1.0) * 14.0, 0.0, 1.0) ** 2.2
    r2 = np.clip(1.0 - np.abs(n2 * 2.0 - 1.0) * 18.0, 0.0, 1.0) ** 2.4
    mask = np.clip((vnoise(freq // 2 + 2, seed + 19, octaves=2) - 0.38) * 2.2, 0.0, 1.0)
    return np.clip((r1 + r2 * 0.65) * mask, 0.0, 1.0)


def brush(img, angle_deg, length=9, passes=2):
    """Directional micro-stroke smear for hand-worked stone/metal grain."""
    a = np.deg2rad(angle_deg)
    dx, dy = np.cos(a), np.sin(a)
    for _ in range(passes):
        acc = img.copy()
        for i in range(1, length):
            acc += np.roll(np.roll(img, int(round(dy * i)), 0), int(round(dx * i)), 1)
        img = acc / length
    return img


def norm05(img, spread=0.68):
    img = img - img.mean()
    s = img.std() + 1e-9
    return np.clip(0.5 + img / s * 0.5 * spread * 0.44, 0.0, 1.0)


def tint_rgb(luma, hue_field, warm_shift=(0.07, 0.01, -0.06), cool_shift=(-0.05, 0.0, 0.06), crevice_mask=None, crevice_rgb=(0.16, 0.14, 0.12)):
    """Converts a grayscale detail map into a rich RGB detail map centered around ~0.5."""
    h = (hue_field - 0.5) * 2.0  # -1..1
    r = luma + np.where(h >= 0.0, h * warm_shift[0], -h * cool_shift[0])
    g = luma + np.where(h >= 0.0, h * warm_shift[1], -h * cool_shift[1])
    b = luma + np.where(h >= 0.0, h * warm_shift[2], -h * cool_shift[2])
    rgb = np.stack([r, g, b], axis=-1)
    if crevice_mask is not None:
        cm = np.clip(crevice_mask, 0.0, 1.0)[..., None]
        c_col = np.array(crevice_rgb, dtype=np.float32)[None, None, :]
        rgb = rgb * (1.0 - cm) + c_col * cm
    return np.clip(rgb, 0.04, 0.96)


def height_to_normal(h, strength=6.5, detail_h=None, detail_strength=2.8):
    """Multi-scale wrapped Sobel height-to-normal conversion with macro bevel & micro grit."""
    def sobel(field, scale):
        tl = np.roll(np.roll(field, 1, 0), 1, 1)
        t  = np.roll(field, 1, 0)
        tr = np.roll(np.roll(field, 1, 0), -1, 1)
        l  = np.roll(field, 1, 1)
        r  = np.roll(field, -1, 1)
        bl = np.roll(np.roll(field, -1, 0), 1, 1)
        b  = np.roll(field, -1, 0)
        br = np.roll(np.roll(field, -1, 0), -1, 1)
        dx = ((tr + 2.0 * r + br) - (tl + 2.0 * l + bl)) * 0.125 * scale
        dy = ((bl + 2.0 * b + br) - (tl + 2.0 * t + tr)) * 0.125 * scale
        return -dx, -dy

    nx, ny = sobel(h, strength)
    # Medium 2-pixel and broad 4-pixel stride bevel derivatives for deep chiseled masonry relief
    h_med = blur_wrap(h, 1)
    bx2 = (np.roll(h_med, 2, 1) - np.roll(h_med, -2, 1)) * 0.32 * strength
    by2 = (np.roll(h_med, 2, 0) - np.roll(h_med, -2, 0)) * 0.32 * strength
    h_broad = blur_wrap(h, 3)
    bx4 = (np.roll(h_broad, 4, 1) - np.roll(h_broad, -4, 1)) * 0.24 * strength
    by4 = (np.roll(h_broad, 4, 0) - np.roll(h_broad, -4, 0)) * 0.24 * strength
    nx += bx2 + bx4
    ny += by2 + by4

    if detail_h is not None:
        dnx, dny = sobel(detail_h, detail_strength)
        nx += dnx
        ny += dny

    nz = np.ones_like(nx)
    inv_len = 1.0 / np.sqrt(nx * nx + ny * ny + nz * nz + 1e-9)
    nx *= inv_len
    ny *= inv_len
    nz *= inv_len

    rgb = np.stack(
        [
            np.clip(nx * 0.5 + 0.5, 0.0, 1.0),
            np.clip(ny * 0.5 + 0.5, 0.0, 1.0),
            np.clip(nz * 0.5 + 0.5, 0.0, 1.0),
        ],
        axis=-1,
    )
    return (rgb * 255.0).astype(np.uint8)


def compute_cavity(h):
    """Multi-radius Laplacian concavity + height crevice detector -> AO / Cavity in [0, 1]."""
    lap = (
        np.roll(h, 1, 0)
        + np.roll(h, -1, 0)
        + np.roll(h, 1, 1)
        + np.roll(h, -1, 1)
        - 4.0 * h
    )
    lap_broad = (
        np.roll(h, 3, 0)
        + np.roll(h, -3, 0)
        + np.roll(h, 3, 1)
        + np.roll(h, -3, 1)
        - 4.0 * h
    )
    deep_groove = np.clip((0.42 - h) * 1.65, 0.0, 0.78)
    cav = np.clip(0.92 - np.maximum(lap * 4.2 + lap_broad * 2.8, 0.0) - deep_groove, 0.05, 1.0)
    return blur_wrap(cav, 1)


def save_pbr_suite(name, albedo_detail, height, rough_mod=None, metal_mask=None, n_strength=7.0, micro_h=None):
    os.makedirs(OUT, exist_ok=True)
    # 1. Albedo / Detail modulation PNG (RGB, centered ~0.5 for rich chromatic variation)
    alb_arr = np.clip(albedo_detail, 0.0, 1.0)
    if alb_arr.ndim == 2:
        alb_arr = np.stack([alb_arr, alb_arr, alb_arr], axis=-1)
    alb_u8 = (alb_arr * 255.0).astype(np.uint8)
    Image.fromarray(alb_u8, mode="RGB").save(os.path.join(OUT, f"{name}.png"), optimize=False)

    # 2. Tangent-space Normal map
    norm_u8 = height_to_normal(height, strength=n_strength, detail_h=micro_h, detail_strength=n_strength * 0.45)
    Image.fromarray(norm_u8, mode="RGB").save(os.path.join(OUT, f"{name}_n.png"), optimize=False)

    # 3. Packed ORM + Height map (R=AO/Cavity, G=Roughness mod, B=Metallic/Spec mask, A=Height)
    ao = compute_cavity(height)
    if rough_mod is None:
        rough_mod = np.clip(0.56 - (height - 0.5) * 0.38 + (1.0 - ao) * 0.28, 0.05, 0.98)
    if metal_mask is None:
        metal_mask = np.clip((height - 0.35) * 1.2 * ao, 0.0, 1.0)
    orm = np.stack(
        [
            np.clip(ao, 0.0, 1.0),
            np.clip(rough_mod, 0.0, 1.0),
            np.clip(metal_mask, 0.0, 1.0),
            np.clip(height, 0.0, 1.0),
        ],
        axis=-1,
    )
    orm_u8 = (orm * 255.0).astype(np.uint8)
    Image.fromarray(orm_u8, mode="RGBA").save(os.path.join(OUT, f"{name}_orm.png"), optimize=False)
    print(f"[tex] {name} (.png RGB, _n.png, _orm.png)")


def cell_grid(rows, cols, jitter_seed, stagger=True, mortar_w=0.036, mortar_h=0.058):
    """Per-cell id map + deep chiseled mortar profile + beveled ashlar block pillow."""
    r = np.random.default_rng(jitter_seed)
    y = np.linspace(0, rows, N, endpoint=False)
    ids = np.zeros((N, N), dtype=np.float32)
    mortar = np.zeros((N, N), dtype=np.float32)
    pillow = np.zeros((N, N), dtype=np.float32)
    bevel = np.zeros((N, N), dtype=np.float32)
    # Hand-laid stone course waviness and chipped edge irregularity
    warp_x = (vnoise(10, jitter_seed + 101, 3) - 0.5) * 0.032 + (vnoise(32, jitter_seed + 103, 2) - 0.5) * 0.012
    warp_y = (vnoise(10, jitter_seed + 102, 3) - 0.5) * 0.042 + (vnoise(32, jitter_seed + 104, 2) - 0.5) * 0.015
    y_w = (y[:, None] + warp_y) % rows
    row_i = np.floor(y_w).astype(int)
    fy = y_w - row_i

    for i in range(rows):
        band = row_i == i
        # Vary course offset so ashlar bond looks authentically medieval
        off = (0.48 if (i % 2) else 0.0) + (0.23 if (i % 3 == 1) else 0.0) if stagger else 0.0
        x_w = (np.linspace(0, cols, N, endpoint=False)[None, :] + off + warp_x) % cols
        col_i = np.floor(x_w).astype(int)
        fx = x_w - col_i
        ids = np.where(band, (i * 37 + col_i * 23 + r.integers(0, 11)) % 127, ids)
        # Sharp recessed mortar channel
        mx = np.maximum(0.0, 1.0 - np.minimum(fx, 1.0 - fx) / mortar_w)
        my = np.maximum(0.0, 1.0 - np.minimum(fy, 1.0 - fy) / mortar_h)
        m = np.clip(np.maximum(mx, my), 0.0, 1.0) ** 0.75
        mortar = np.where(band, m, mortar)
        # Steep chiseled block bevel (0 at mortar -> 1 quickly inside block face)
        px = np.clip((np.minimum(fx, 1.0 - fx) - mortar_w * 0.65) / (mortar_w * 2.1), 0.0, 1.0)
        py = np.clip((np.minimum(fy, 1.0 - fy) - mortar_h * 0.65) / (mortar_h * 2.0), 0.0, 1.0)
        p = (px * py) ** 0.42
        pillow = np.where(band, p, pillow)
        # Top-edge light-catching mason draft chisel rim
        b_top = np.clip(1.0 - np.abs(fy - mortar_h * 1.45) / 0.045, 0.0, 1.0)
        b_side = np.clip(1.0 - np.abs(fx - mortar_w * 1.45) / 0.035, 0.0, 1.0)
        b = np.maximum(b_top, b_side * 0.7) * (fx > mortar_w) * (fx < 1.0 - mortar_w) * (fy > mortar_h)
        bevel = np.where(band, b, bevel)

    return ids, mortar, pillow, blur_wrap(bevel, 1)


def tone_from_ids(ids, seed, spread=0.22):
    r = np.random.default_rng(seed)
    lut = (0.5 + (r.random(128) - 0.5) * spread * 2.0).astype(np.float32)
    return lut[(ids.astype(int)) % 128]


def make_stone():
    base = vnoise(8, 21, 5)
    strata = brush(vnoise(18, 35, 4), 3, 18, passes=3)
    grit = high_freq_grit(24)
    cracks = ridged_cracks(29, freq=12)
    ids, mortar, pillow, bevel = cell_grid(6, 3, 31, stagger=True, mortar_w=0.038, mortar_h=0.056)
    tone = tone_from_ids(ids, 32, 0.24)
    hue_id = tone_from_ids(ids, 39, 0.42)
    # Mason chisel marks per block (varied angle per block ID)
    u = np.arange(N, dtype=np.float32)
    angle_sel = (ids % 2) * 2.0 - 1.0
    hatch = 0.5 + 0.5 * np.sin((u[None, :] + u[:, None] * 0.42 * angle_sel) * 0.55 + ids * 2.1)
    chisel = (hatch > 0.68).astype(np.float32) * 0.048 * pillow
    pits = np.clip((vnoise(48, 33, 3) - 0.62) * 2.9, 0.0, 1.0) * 0.18 * pillow
    # Vertical damp/soot streaks across stone courses
    streaks = brush(vnoise(12, 37, 3), 90, 22, passes=3)

    height = np.clip(
        pillow * (0.62 + 0.18 * base + 0.10 * strata + 0.14 * (tone - 0.5) + 0.08 * (grit - 0.5))
        - mortar * 0.62
        - chisel * 0.75
        - pits
        - cracks * 0.32,
        0.0,
        1.0,
    )
    luma = (
        norm05(base * 0.42 + strata * 0.28 + grit * 0.30, 0.74) * 0.56
        + tone * 0.44
        - (1.0 - streaks) * 0.08
        - chisel * 0.85
        - pits * 0.55
        - cracks * 0.38
        + 0.09 * bevel
    )
    hue_field = np.clip(hue_id * 0.65 + base * 0.35, 0.0, 1.0)
    crevice = np.clip(mortar * 0.82 + cracks * 0.55 + pits * 0.40, 0.0, 0.90)
    alb_rgb = tint_rgb(
        luma,
        hue_field,
        warm_shift=(0.085, 0.025, -0.065),
        cool_shift=(-0.055, -0.005, 0.065),
        crevice_mask=crevice,
        crevice_rgb=(0.14, 0.12, 0.10),
    )
    rough = np.clip(0.62 + mortar * 0.34 + pits * 0.45 + cracks * 0.30 - bevel * 0.18 + (grit - 0.5) * 0.22, 0.12, 0.98)
    save_pbr_suite("T_stone", alb_rgb, height, rough_mod=rough, metal_mask=np.zeros_like(height), n_strength=8.6, micro_h=grit)


def make_trim():
    base = brush(vnoise(12, 41, 4), 4, 14, passes=3)
    grit = high_freq_grit(44)
    strata = brush(vnoise(20, 42, 4), 0, 20, passes=3)
    cracks = ridged_cracks(45, freq=14) * 0.6
    # Carved Gothic moulding flutes + recessed channel fillets
    x_norm = np.linspace(0, 8 * np.pi, N, endpoint=False)[None, :]
    flutes = 0.5 + 0.5 * np.cos(x_norm) * 0.12
    fillets = (np.abs(np.sin(x_norm)) > 0.92).astype(np.float32) * 0.14
    pits = np.clip((vnoise(48, 43, 3) - 0.66) * 2.8, 0.0, 1.0) * 0.12
    height = np.clip(
        0.58 + (base - 0.5) * 0.24 + (strata - 0.5) * 0.16 + (flutes - 0.5) * 0.42 - fillets - pits - cracks * 0.25 + (grit - 0.5) * 0.07,
        0.0,
        1.0,
    )
    luma = norm05(base * 0.55 + strata * 0.25 + grit * 0.20, 0.58) * 0.84 + 0.08 - pits * 0.42 - fillets * 0.45 - cracks * 0.30
    hue_field = vnoise(8, 46, 3)
    alb_rgb = tint_rgb(
        luma,
        hue_field,
        warm_shift=(0.06, 0.02, -0.05),
        cool_shift=(-0.04, 0.0, 0.05),
        crevice_mask=np.clip(fillets * 2.2 + pits * 1.5 + cracks, 0.0, 0.75),
        crevice_rgb=(0.18, 0.16, 0.14),
    )
    rough = np.clip(0.46 + pits * 0.38 + fillets * 0.32 + (grit - 0.5) * 0.18, 0.12, 0.95)
    save_pbr_suite("T_trim", alb_rgb, height, rough_mod=rough, n_strength=6.8, micro_h=grit)


def make_floor():
    base = brush(vnoise(10, 51, 4), 38, 10, passes=2)
    strata = brush(vnoise(18, 54, 4), 12, 16, passes=2)
    grit = high_freq_grit(56)
    cracks = ridged_cracks(58, freq=10)
    ids, mortar, pillow, bevel = cell_grid(4, 4, 52, stagger=True, mortar_w=0.032, mortar_h=0.032)
    tone = tone_from_ids(ids, 53, 0.22)
    hue_id = tone_from_ids(ids, 59, 0.40)
    wear = blur_wrap(vnoise(6, 54, 4), 4) * 0.10
    u = np.linspace(0, 1, N, dtype=np.float32)
    lane = np.exp(-((u[None, :] - 0.5) ** 2) / 0.08) * 0.07
    fx = np.linspace(0, 4, N, endpoint=False) % 1.0
    fy = np.linspace(0, 4, N, endpoint=False) % 1.0
    corner = np.clip(1.0 - np.minimum(fx, 1.0 - fx) / 0.10, 0.0, 1.0)[None, :] * np.clip(
        1.0 - np.minimum(fy, 1.0 - fy) / 0.10, 0.0, 1.0
    )[:, None]
    chips = corner * np.clip((vnoise(16, 55, 3) - 0.40) * 2.1, 0.0, 1.0) * 0.22

    height = np.clip(
        pillow * (0.64 + 0.18 * base + 0.09 * strata + 0.14 * (tone - 0.5) + 0.07 * (grit - 0.5))
        - mortar * 0.60
        - chips
        - cracks * 0.34
        - wear * 0.25,
        0.0,
        1.0,
    )
    luma = (
        norm05(base * 0.50 + strata * 0.28 + grit * 0.22, 0.68) * 0.54
        + tone * 0.46
        - wear
        + lane
        - chips * 0.60
        - cracks * 0.36
        + 0.07 * bevel
    )
    hue_field = np.clip(hue_id * 0.65 + base * 0.35, 0.0, 1.0)
    crevice = np.clip(mortar * 0.84 + chips * 0.65 + cracks * 0.55, 0.0, 0.90)
    alb_rgb = tint_rgb(
        luma,
        hue_field,
        warm_shift=(0.075, 0.02, -0.055),
        cool_shift=(-0.05, 0.005, 0.065),
        crevice_mask=crevice,
        crevice_rgb=(0.13, 0.12, 0.10),
    )
    rough = np.clip(0.56 - lane * 2.0 + mortar * 0.38 + chips * 0.38 + cracks * 0.28 + (grit - 0.5) * 0.20, 0.10, 0.98)
    save_pbr_suite("T_floor", alb_rgb, height, rough_mod=rough, n_strength=8.2, micro_h=grit)


def make_wood():
    g = vnoise(6, 61, 4)
    micro = brush(high_freq_grit(64), 90, 14, passes=2)
    grain = np.tile(np.linspace(0, 1, N // 8, endpoint=False), 8)[None, :]
    rings = 0.5 + 0.5 * np.sin((grain * 6.0 + g * 2.8) * np.pi * 2.0)
    img = 0.5 + (rings - 0.5) * 0.28
    img = brush(img + (vnoise(28, 62, 3) - 0.5) * 0.20, 90, 12, passes=2)
    r = np.random.default_rng(63)
    yy, xx = np.indices((N, N), dtype=np.float32)
    knots = np.zeros((N, N), dtype=np.float32)
    for _ in range(11):
        cx, cy = r.integers(40, N - 40), r.integers(40, N - 40)
        d = np.sqrt((xx - cx) ** 2 + ((yy - cy) * 0.65) ** 2)
        knots += np.exp(-d / 15.0) * 0.26 + np.clip(0.06 * np.sin(d * 0.55), 0, 1) * np.exp(-d / 38.0)
    planks = ((np.arange(N)[None, :] % (N // 4)) < 7).astype(np.float32)
    seam_y = ((np.arange(N)[:, None] + (np.arange(N)[None, :] // (N // 4)) * 73) % (N // 3) < 6).astype(np.float32)
    grooves = blur_wrap(np.clip(planks + seam_y, 0.0, 1.0), 1)
    # Per-plank tone variation
    plank_id = (np.arange(N)[None, :] // (N // 4)) * 7 + (np.arange(N)[:, None] // (N // 3)) * 3
    plank_tone = tone_from_ids(plank_id, 65, 0.16)
    height = np.clip(img * 0.75 + plank_tone * 0.25 - knots * 0.62 - grooves * 0.65 + (micro - 0.5) * 0.18, 0.0, 1.0)
    luma = norm05(img * 0.8 + plank_tone * 0.2 - knots, 0.86)
    alb_rgb = tint_rgb(
        luma,
        plank_tone,
        warm_shift=(0.08, 0.02, -0.06),
        cool_shift=(-0.04, -0.01, 0.03),
        crevice_mask=np.clip(grooves * 0.85 + knots * 0.55, 0.0, 0.90),
        crevice_rgb=(0.11, 0.08, 0.06),
    )
    rough = np.clip(0.54 + grooves * 0.38 + (1.0 - rings) * 0.20, 0.18, 0.95)
    save_pbr_suite("T_wood", alb_rgb, height, rough_mod=rough, n_strength=7.2, micro_h=micro)


def make_roof():
    y = np.linspace(0, 8, N, endpoint=False)
    fy = y - np.floor(y)
    row = np.floor(y).astype(int)
    x = np.linspace(0, 8, N, endpoint=False)
    alb = np.full((N, N), 0.5, dtype=np.float32)
    hue = np.full((N, N), 0.5, dtype=np.float32)
    height = np.full((N, N), 0.5, dtype=np.float32)
    crevice = np.zeros((N, N), dtype=np.float32)
    for i in range(8):
        band = row == i
        off = 0.5 if i % 2 else 0.0
        fx = (x + off) - np.floor(x + off)
        cell_idx = np.floor(x + off)[None, :] + i * 13
        tone = tone_from_ids(cell_idx, 72 + i, 0.20)
        h_id = tone_from_ids(cell_idx, 82 + i, 0.35)
        alb[band] = tone[0]
        hue[band] = h_id[0]
        lip = np.clip(1.0 - fy[band][:, None] * 0.65, 0.2, 1.0)
        drop = np.clip((fy[band][:, None] - 0.80) / 0.20, 0.0, 1.0) ** 1.35
        gap = ((fx < 0.042) | (fx > 0.958)).astype(np.float32)[None, :]
        height[band] = lip * (1.0 - gap * 0.72) - drop * 0.52
        alb[band] -= drop * 0.42 + gap * 0.32
        crevice[band] = np.clip(drop * 0.75 + gap * 0.80, 0.0, 1.0)
    slate_grain = vnoise(18, 73, 4)
    grit = high_freq_grit(74)
    height = np.clip(height + (slate_grain - 0.5) * 0.18 + (grit - 0.5) * 0.08, 0.0, 1.0)
    luma = np.clip(alb + (slate_grain - 0.5) * 0.16 + (grit - 0.5) * 0.08, 0.0, 1.0)
    alb_rgb = tint_rgb(
        luma,
        hue,
        warm_shift=(0.04, 0.05, -0.04),
        cool_shift=(-0.05, 0.0, 0.07),
        crevice_mask=crevice,
        crevice_rgb=(0.10, 0.11, 0.13),
    )
    save_pbr_suite("T_roof", alb_rgb, height, n_strength=8.0, micro_h=grit)


def make_cloth():
    idx = np.indices((N, N), dtype=np.float32)
    twill = 0.5 + 0.5 * np.sin((idx[0] * 1.6 + np.sin(idx[1] * 0.45) * 2.0) * 0.95) * np.cos(idx[1] * 1.6)
    u = np.linspace(0, 6, N, endpoint=False)
    diam = np.abs(((u[None, :] + u[:, None]) % 1.0) - 0.5) + np.abs(((u[None, :] - u[:, None]) % 1.0) - 0.5)
    damask = blur_wrap((np.abs(diam - 0.42) < 0.065).astype(np.float32), 1)
    folds = brush(vnoise(6, 81, 4), 90, 14, passes=2)
    grime = vnoise(14, 83, 3)
    height = np.clip(folds * 0.62 + twill * 0.20 + damask * 0.18, 0.0, 1.0)
    luma = np.clip(norm05(folds, 0.76) + (twill - 0.5) * 0.12 + damask * 0.11 - (1.0 - grime) * 0.08, 0.0, 1.0)
    alb_rgb = tint_rgb(
        luma,
        damask,
        warm_shift=(0.06, 0.04, -0.03),
        cool_shift=(-0.02, -0.02, 0.02),
    )
    rough = np.clip(0.76 + (1.0 - twill) * 0.16 - damask * 0.24, 0.28, 0.98)
    save_pbr_suite("T_cloth", alb_rgb, height, rough_mod=rough, n_strength=5.4, micro_h=twill)


def make_iron():
    base = brush(vnoise(18, 91, 4), 12, 12)
    hammer = vnoise(16, 93, 4)
    scratches = brush(high_freq_grit(94), -35, 16) * 0.5 + brush(high_freq_grit(95), 55, 16) * 0.5
    pits = np.clip((vnoise(42, 92, 3) - 0.64) * 3.6, 0.0, 1.0) * 0.34
    rust_patch = np.clip((vnoise(10, 96, 3) - 0.58) * 2.5, 0.0, 1.0)
    height = np.clip(0.55 + (hammer - 0.5) * 0.32 + (scratches - 0.5) * 0.22 - pits, 0.0, 1.0)
    luma = np.clip(norm05(base * 0.55 + hammer * 0.45, 0.68) - pits * 0.85 + (scratches - 0.5) * 0.18, 0.0, 1.0)
    alb_rgb = tint_rgb(
        luma,
        rust_patch,
        warm_shift=(0.09, 0.01, -0.07),
        cool_shift=(-0.04, 0.0, 0.05),
        crevice_mask=pits * 1.4,
        crevice_rgb=(0.12, 0.09, 0.08),
    )
    rough = np.clip(0.36 + pits * 0.58 + rust_patch * 0.22 - (scratches - 0.5) * 0.28, 0.10, 0.94)
    metal = np.clip(0.94 - pits * 0.70 - rust_patch * 0.35, 0.12, 1.0)
    save_pbr_suite("T_iron", alb_rgb, height, rough_mod=rough, metal_mask=metal, n_strength=6.8, micro_h=scratches)


def make_wax():
    blobs = blur_wrap(vnoise(6, 101, 4), 5)
    drips = brush(vnoise(18, 102, 3), 90, 20, passes=3)
    ridges = np.clip(np.sin(drips * np.pi * 7.0) * 0.5 + 0.5, 0.0, 1.0) * 0.18
    height = np.clip(blobs * 0.58 + drips * 0.28 + ridges, 0.0, 1.0)
    luma = norm05(height, 0.58)
    alb_rgb = tint_rgb(luma, height, warm_shift=(0.06, 0.03, -0.05), cool_shift=(-0.04, -0.02, 0.02))
    rough = np.clip(0.34 + (1.0 - height) * 0.28, 0.16, 0.78)
    save_pbr_suite("T_wax", alb_rgb, height, rough_mod=rough, n_strength=5.2)


def make_mosaic():
    cells = 24
    u = np.linspace(0, cells, N, endpoint=False)
    fx = u[None, :] - np.floor(u[None, :])
    fy = u[:, None] - np.floor(u[:, None])
    ids = np.floor(u)[None, :] * 53 + np.floor(u)[:, None] * 17
    tone = tone_from_ids(ids, 111, 0.26)
    hue = tone_from_ids(ids, 114, 0.45)
    r = np.random.default_rng(112)
    missing = r.random((cells, cells)) < 0.04
    miss = np.kron(missing, np.ones((N // cells + 1, N // cells + 1)))[:N, :N].astype(np.float32)
    grout = ((fx < 0.11) | (fx > 0.89) | (fy < 0.11) | (fy > 0.89)).astype(np.float32)
    grout = blur_wrap(grout, 1)
    cx = np.sqrt(np.linspace(-1, 1, N)[None, :] ** 2 + np.linspace(-1, 1, N)[:, None] ** 2)
    band = 0.5 + 0.5 * np.sin(cx * np.pi * 6.0)
    height = np.clip((0.72 + tone * 0.25) * (1.0 - 0.72 * grout) * (1.0 - 0.58 * miss), 0.0, 1.0)
    luma = (tone * 0.60 + band * 0.18 + 0.12) * (1.0 - 0.56 * grout) * (1.0 - 0.42 * miss)
    luma = np.clip(luma + (vnoise(14, 113, 3) - 0.5) * 0.10, 0.0, 1.0)
    alb_rgb = tint_rgb(
        luma,
        hue,
        warm_shift=(0.09, 0.04, -0.07),
        cool_shift=(-0.06, 0.01, 0.08),
        crevice_mask=np.clip(grout * 0.85 + miss * 0.75, 0.0, 0.90),
        crevice_rgb=(0.14, 0.13, 0.11),
    )
    rough = np.clip(0.24 + grout * 0.58 + miss * 0.48, 0.10, 0.95)
    metal = np.clip((band > 0.60).astype(np.float32) * (1.0 - grout) * 0.85, 0.0, 1.0)
    save_pbr_suite("T_mosaic", alb_rgb, height, rough_mod=rough, metal_mask=metal, n_strength=7.2)


def make_bronze():
    streaks = brush(vnoise(14, 121, 4), 90, 16)
    patina = blur_wrap((vnoise(8, 122, 3) > 0.54).astype(np.float32), 3)
    rubbed = blur_wrap((vnoise(6, 123, 3) > 0.68).astype(np.float32), 4)
    filigree = np.sin(np.linspace(0, 16 * np.pi, N, endpoint=False))[None, :] * np.sin(
        np.linspace(0, 16 * np.pi, N, endpoint=False)
    )[:, None]
    relief = np.clip(filigree, 0.0, 1.0) * 0.18
    micro = high_freq_grit(124)
    height = np.clip(0.52 + (streaks - 0.5) * 0.24 + relief + rubbed * 0.16 - patina * 0.20, 0.0, 1.0)
    luma = np.clip(norm05(streaks, 0.58) - patina * 0.18 + rubbed * 0.22 + relief * 0.42, 0.0, 1.0)
    alb_rgb = tint_rgb(
        luma,
        1.0 - patina,
        warm_shift=(0.09, 0.04, -0.07),
        cool_shift=(-0.08, 0.07, 0.04),  # Verdigris patina in cool regions
    )
    rough = np.clip(0.32 + patina * 0.50 - rubbed * 0.24, 0.10, 0.92)
    metal = np.clip(0.92 - patina * 0.58 + rubbed * 0.12, 0.18, 1.0)
    save_pbr_suite("T_bronze", alb_rgb, height, rough_mod=rough, metal_mask=metal, n_strength=6.6, micro_h=micro)


def make_bone():
    cells = 14
    u = np.linspace(0, cells, N, endpoint=False)
    fx = u[None, :] - np.floor(u[None, :])
    fy = u[:, None] - np.floor(u[:, None])
    dome = np.clip(1.0 - ((fx - 0.5) ** 2 + (fy - 0.5) ** 2) * 4.8, 0.0, 1.0) ** 0.65
    ids = np.floor(u)[None, :] * 31 + np.floor(u)[:, None] * 7
    tone = tone_from_ids(ids, 131, 0.18)
    r = np.random.default_rng(132)
    sockets = r.random((cells, cells)) < 0.20
    soc = np.kron(sockets, np.ones((N // cells + 1, N // cells + 1)))[:N, :N].astype(np.float32) * (dome > 0.50)
    soc = blur_wrap(soc, 2)
    noise = vnoise(14, 133, 4)
    grit = high_freq_grit(134)
    height = np.clip(dome * (0.75 + 0.25 * tone) - soc * 0.60 + (noise - 0.5) * 0.14, 0.0, 1.0)
    luma = np.clip(0.32 + dome * 0.38 + tone * 0.22 - soc * 0.42 + (noise - 0.5) * 0.12, 0.0, 1.0)
    alb_rgb = tint_rgb(
        luma,
        tone,
        warm_shift=(0.06, 0.03, -0.05),
        cool_shift=(-0.03, -0.01, 0.03),
        crevice_mask=np.clip((1.0 - dome) * 0.75 + soc * 0.85, 0.0, 0.90),
        crevice_rgb=(0.14, 0.12, 0.10),
    )
    save_pbr_suite("T_bone", alb_rgb, height, n_strength=7.8, micro_h=grit)


def make_marble():
    yy, xx = np.mgrid[0:N, 0:N].astype(np.float32) / N
    warp1 = blur_wrap(vnoise(4, 142, 4, gain=0.55), 6)
    warp2 = blur_wrap(vnoise(6, 143, 4, gain=0.55), 6)
    band1 = np.sin((xx * 3.0 + yy * 1.0) * 2.0 * np.pi + warp1 * 7.5)
    band2 = np.sin((xx * 1.0 - yy * 2.0) * 2.0 * np.pi + warp2 * 9.5)
    veins = blur_wrap(
        np.clip(1.0 - np.abs(band1) * 5.8, 0.0, 1.0) * 0.72
        + np.clip(1.0 - np.abs(band2) * 7.8, 0.0, 1.0) * 0.52,
        1,
    )
    ground = brush(blur_wrap(vnoise(16, 141, 3, gain=0.5), 2), 30, 12, passes=2)
    sheen = brush(vnoise(6, 145, 3), 25, 14)
    grit = high_freq_grit(146)
    height = np.clip(0.65 + (ground - 0.5) * 0.16 - veins * 0.22 + (grit - 0.5) * 0.05, 0.0, 1.0)
    luma = np.clip(norm05(ground, 0.24) + (norm05(sheen, 0.28) - 0.5) * 0.10 - veins * 0.24, 0.0, 1.0)
    alb_rgb = tint_rgb(
        luma,
        ground,
        warm_shift=(0.05, 0.02, -0.03),
        cool_shift=(-0.03, 0.0, 0.04),
        crevice_mask=veins * 0.65,
        crevice_rgb=(0.24, 0.22, 0.20),
    )
    rough = np.clip(0.20 + veins * 0.34 + (1.0 - sheen) * 0.14, 0.08, 0.68)
    save_pbr_suite("T_marble", alb_rgb, height, rough_mod=rough, n_strength=5.2, micro_h=grit)


def make_marble_floor():
    base = brush(blur_wrap(vnoise(14, 151, 3, gain=0.5), 2), 78, 12, passes=3)
    streaks = brush(vnoise(8, 152, 3), 78, 16)
    grit = high_freq_grit(156)
    ids, mortar, pillow, bevel = cell_grid(4, 4, 153, stagger=False, mortar_w=0.022, mortar_h=0.022)
    tone = tone_from_ids(ids, 154, 0.14)
    hue = tone_from_ids(ids, 157, 0.32)
    yy, xx = np.mgrid[0:N, 0:N].astype(np.float32) / N
    warp = blur_wrap(vnoise(5, 155, 4, gain=0.55), 6)
    band = np.sin((xx * 2.0 + yy * 2.0) * 2.0 * np.pi + warp * 8.0)
    veins = blur_wrap(np.clip(1.0 - np.abs(band) * 6.5, 0.0, 1.0), 1)
    height = np.clip(pillow * (0.72 + (base - 0.5) * 0.15 - veins * 0.16) - mortar * 0.52, 0.0, 1.0)
    luma = (norm05(base, 0.32) * 0.5 + tone * 0.5 + (norm05(streaks, 0.30) - 0.5) * 0.12 - veins * 0.18) * (
        1.0 - 0.45 * mortar
    ) + 0.05 * bevel
    alb_rgb = tint_rgb(
        luma,
        hue,
        warm_shift=(0.06, 0.02, -0.04),
        cool_shift=(-0.04, 0.01, 0.05),
        crevice_mask=np.clip(mortar * 0.80 + veins * 0.45, 0.0, 0.88),
        crevice_rgb=(0.16, 0.15, 0.14),
    )
    rough = np.clip(0.18 + mortar * 0.55 + veins * 0.26 + (1.0 - streaks) * 0.14, 0.06, 0.88)
    save_pbr_suite("T_marble_floor", alb_rgb, height, rough_mod=rough, n_strength=6.2, micro_h=grit)


def make_chainmail():
    """European 4-in-1 interlocking steel mail rings for Dark Souls hauberks."""
    rings_n = 32
    u = np.linspace(0, rings_n, N, endpoint=False)
    v = np.linspace(0, rings_n, N, endpoint=False)
    xx, yy = np.meshgrid(u, v)
    height = np.zeros((N, N), dtype=np.float32)
    for ox, oy, tilt in ((0.0, 0.0, 1.0), (0.5, 0.5, -1.0)):
        fx = ((xx + ox) % 1.0) - 0.5
        fy = ((yy + oy) % 1.0) - 0.5
        r = np.sqrt((fx * 1.15) ** 2 + (fy * 0.95) ** 2)
        torus = np.clip(1.0 - ((r - 0.34) / 0.13) ** 2, 0.0, 1.0)
        weave_z = np.sqrt(torus) * (0.82 + 0.18 * tilt * np.sin(fx * np.pi * 2.0))
        height = np.maximum(height, weave_z)
    wear = vnoise(16, 161, 3)
    height = np.clip(height * (0.88 + 0.12 * wear), 0.0, 1.0)
    luma = np.clip(0.24 + height * 0.58 + (wear - 0.5) * 0.14, 0.0, 1.0)
    alb_rgb = tint_rgb(
        luma,
        wear,
        warm_shift=(0.04, 0.01, -0.03),
        cool_shift=(-0.03, 0.0, 0.04),
        crevice_mask=np.clip((0.35 - height) * 2.2, 0.0, 0.85),
        crevice_rgb=(0.08, 0.08, 0.09),
    )
    rough = np.clip(0.62 - height * 0.38, 0.20, 0.92)
    metal = np.clip((height > 0.2).astype(np.float32) * 0.94, 0.0, 1.0)
    save_pbr_suite("T_chainmail", alb_rgb, height, rough_mod=rough, metal_mask=metal, n_strength=8.2)


def make_plate():
    """Hand-burnished & battle-scarred Lothric/Astora knight plate armor micro-detail."""
    base = brush(vnoise(14, 171, 4), 90, 16, passes=3)
    hammer = blur_wrap(vnoise(10, 175, 3), 2)
    scratches = brush(high_freq_grit(172), 28, 16) * 0.5 + brush(high_freq_grit(173), -38, 16) * 0.5
    dents = np.clip((vnoise(28, 174, 3) - 0.68) * 3.0, 0.0, 1.0) * 0.14
    height = np.clip(0.56 + (base - 0.5) * 0.14 + (hammer - 0.5) * 0.12 - dents + (scratches - 0.5) * 0.12, 0.0, 1.0)
    luma = np.clip(norm05(base * 0.65 + hammer * 0.35, 0.36) - dents * 0.45 + (scratches - 0.5) * 0.10, 0.0, 1.0)
    alb_rgb = tint_rgb(
        luma,
        hammer,
        warm_shift=(0.03, 0.015, -0.02),
        cool_shift=(-0.025, 0.0, 0.035),
        crevice_mask=np.clip(dents * 1.8, 0.0, 0.65),
        crevice_rgb=(0.18, 0.18, 0.20),
    )
    rough = np.clip(0.28 + dents * 0.65 + (1.0 - scratches) * 0.14, 0.12, 0.78)
    metal = np.clip(0.95 - dents * 0.35, 0.45, 1.0)
    save_pbr_suite("T_plate", alb_rgb, height, rough_mod=rough, metal_mask=metal, n_strength=3.8, micro_h=scratches)


if __name__ == "__main__":
    make_stone()
    make_trim()
    make_floor()
    make_wood()
    make_roof()
    make_cloth()
    make_iron()
    make_wax()
    make_mosaic()
    make_bronze()
    make_bone()
    make_marble()
    make_marble_floor()
    make_chainmail()
    make_plate()
    print("[tex] all 15 PBR texture suites generated at 1024x1024")
