"""Ambient decor kit — the liveliness pass. Most pieces come in PAIRS
(glory form / ruin form) meant to occupy the SAME spot in both layers, so
the transformation reads as one world remembered two ways:

  candle_cluster (burning votives)  <->  candle_cluster_dead (melted mass)
  garden_bed (blooming)             <->  garden_bed_dead (withered)
  censer_hanging (swinging gold)    <->  censer_fallen (spilled on the floor)
  banner (bright)                   <->  banner_torn (rag on the same rod)
  statue/orans (saints standing)    <->  wax_husk (a penitent kneeling)
"""
import math
import random
import bmesh
from mathutils import Vector

import vglib as V
from kit_props import _flame, _robe


def candle_cluster(lit=True, seed=7):
    """Votive puddle: 7-9 concave-cupped candles of ragged heights fused in an
    organic multi-lobed wax drip mass, with charred wicks and wax drip ridges."""
    rng = random.Random(seed)
    objs = []
    # Pooled multi-lobed wax drip base
    bm = bmesh.new()
    got = bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.23)
    for v in got["verts"]:
        v.co.z = max(0.0, v.co.z * 0.20)
        ang = math.atan2(v.co.y, v.co.x)
        lobe = 1.0 + 0.14 * math.sin(ang * 4.0 + 0.4) + 0.08 * math.cos(ang * 7.0)
        v.co.x *= rng.uniform(0.90, 1.22) * lobe
        v.co.y *= rng.uniform(0.90, 1.22) * lobe
    objs.append(V.bm_to_object(bm, "drip_base", ("M_wax",)))

    bm_wicks = bmesh.new()
    n = rng.randint(7, 9)
    for i in range(n):
        a = 2 * math.pi * i / n + rng.uniform(-0.3, 0.3)
        r = rng.uniform(0.02, 0.16)
        h = rng.uniform(0.06, 0.30) if lit else rng.uniform(0.03, 0.13)
        cx, cy = r * math.cos(a), r * math.sin(a)
        c = V.loft_rings(
            "votive",
            [
                (0.034, 0.0, 10, 0),
                (0.029, h * 0.65, 10, 0.18),
                (0.025, h * 0.96, 10, 0.12),
                (0.024, h, 10, 0),
                (0.014, max(0.015, h - 0.014), 10, 0),
            ],
            "M_wax",
        )
        c.location = (cx, cy, 0.015)
        objs.append(c)
        # Charred cord wick inside each candle cup
        V.add_cyl(bm_wicks, cx, cy, 0.015 + max(0.01, h - 0.016), 0.024, 0.004, n=6)
        if lit and rng.random() < 0.85:
            f = _flame("cluster_flame", 0.022, 0.075)
            f.location = (cx, cy, h + 0.028)
            objs.append(f)
    objs.append(V.bm_to_object(bm_wicks, "cluster_wicks", ("M_iron",)))
    return objs, {"size": [0.55, 0.55, 0.42], "origin": "bottom-center"}


def wax_husk(seed=13):
    """A penitent that never rose: kneeling melted figure, dead wick head.
    Place in ruin where a saint stands in glory."""
    rng = random.Random(seed)
    objs = []
    # Pooled melted wax base around the kneeling robe hem
    bm_base = bmesh.new()
    got = bmesh.ops.create_icosphere(bm_base, subdivisions=2, radius=0.44)
    for v in got["verts"]:
        v.co.z = max(0.0, v.co.z * 0.18)
        ang = math.atan2(v.co.y, v.co.x)
        lobe = 1.0 + 0.15 * math.sin(ang * 3.0 + 0.6) + 0.10 * math.cos(ang * 5.0)
        v.co.x *= lobe
        v.co.y *= lobe
    objs.append(V.bm_to_object(bm_base, "husk_pool", ("M_wax",)))

    body = _robe("husk", 1.04, 0.32, hood=True, mat="M_wax")
    me = body.data
    for v in me.vertices:
        v.co.z *= 0.94
        zt = max(0.0, min(1.0, (v.co.z - 0.20) / 0.80))
        bow = zt * zt * (3.0 - 2.0 * zt)
        w = V.value_noise(v.co * 2.0 + Vector((3, 1, 4)))
        v.co.x += (w - 0.5) * 0.05 * (0.2 + zt * 0.6)
        v.co.y += 0.16 * bow + (V.value_noise(v.co * 1.8) - 0.5) * 0.04
    me.update()
    objs.append(body)

    # Clasped praying sleeves folded across the chest
    for sx in (-1, 1):
        arm = V.sweep_profile(
            "husk_arm",
            [
                (sx * 0.24, 0.06, 0.68),
                (sx * 0.18, 0.22, 0.54),
                (sx * 0.05, 0.28, 0.58),
            ],
            V.circle_profile(0.072, 10, squash=0.85),
            "M_wax",
        )
        objs.append(arm)

    # Charred dead candle wick protruding from the bowed hood crown
    wick = V.sweep_profile(
        "husk_wick",
        [(0.0, 0.22, 0.96), (0.01, 0.26, 1.03), (0.02, 0.29, 1.06)],
        V.circle_profile(0.008, 6),
        "M_iron",
    )
    objs.append(wick)

    # Upright melted wax candle stubs & drip ridges fused around the base
    for i in range(7):
        a = 2.0 * math.pi * i / 7.0 + rng.uniform(-0.2, 0.2)
        dist = rng.uniform(0.28, 0.38)
        dh = rng.uniform(0.12, 0.26)
        dr = rng.uniform(0.026, 0.042)
        drip = V.loft_rings(
            "drip",
            [(dr * 1.35, 0.0, 8, 0), (dr, dh * 0.7, 8, 0.2), (dr * 0.65, dh, 8, 0)],
            "M_wax",
        )
        drip.location = (dist * math.cos(a), dist * math.sin(a), 0.0)
        objs.append(drip)
    return objs, {"size": [0.9, 0.9, 1.1], "origin": "bottom-center"}


def banner_torn():
    """The same banner rod, but the cloth hangs in rags."""
    bm = bmesh.new()
    w, h = 0.85, 2.3
    nx, nz = 6, 14
    rng = random.Random(19)
    grid = {}
    # ragged bottom: per-column survival length
    keep = [rng.uniform(0.25, 0.7) for _ in range(nx + 1)]
    for i in range(nx + 1):
        for j in range(nz + 1):
            x = -w / 2 + w * i / nx
            t = j / nz
            z = -h * t
            y = 0.07 * math.sin(j * 0.9 + i) * t
            grid[(i, j)] = (x, y, z, t)
    verts = {}
    for i in range(nx):
        for j in range(nz):
            lim = min(keep[i], keep[i + 1])
            if j / nz > lim:
                continue
            for (ii, jj) in ((i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1)):
                if (ii, jj) not in verts:
                    x, y, z, t = grid[(ii, jj)]
                    verts[(ii, jj)] = bm.verts.new((x, y, z))
            try:
                bm.faces.new((verts[(i, j)], verts[(i + 1, j)], verts[(i + 1, j + 1)], verts[(i, j + 1)]))
            except ValueError:
                pass
    bmesh.ops.solidify(bm, geom=list(bm.faces) + list(bm.verts) + list(bm.edges), thickness=0.012)
    cloth = V.bm_to_object(bm, "rag", ("M_cloth",))
    cloth.location = (0, 0, 2.5)
    bm_iron = bmesh.new()
    V.add_box(bm_iron, (-w / 2 - 0.14, -0.018, 2.502), (w / 2 + 0.14, 0.018, 2.538))
    for sx in (-1, 1):
        x_end = sx * (w / 2 + 0.16)
        V.add_box(bm_iron, (x_end - 0.03, -0.028, 2.492), (x_end + 0.03, 0.028, 2.548))
    for rx in (-0.36, -0.18, 0.0, 0.18, 0.36):
        V.add_box(bm_iron, (rx - 0.015, -0.025, 2.47), (rx + 0.015, 0.025, 2.55))
    rod = V.bm_to_object(bm_iron, "rod", ("M_iron",))
    return [cloth, rod], {"size": [1.1, 0.3, 2.6], "origin": "top-center"}


def garden_bed(alive=True, seed=23):
    """Stone-curbed cloister garth planter: carved Gothic coping & corner finials,
    mounded dark earth, woody shrub stems, layered fern/boxwood fronds & cloister lilies
    in Glory; gnarled skeletal briar bushes & dead bramble leaves in Ruin."""
    rng = random.Random(seed)
    objs = []
    # 1. Carved stone curb base
    bm = bmesh.new()
    V.add_box(bm, (-1.10, -0.70, 0.0), (1.10, -0.56, 0.20))
    V.add_box(bm, (-1.10, 0.56, 0.0), (1.10, 0.70, 0.20))
    V.add_box(bm, (-1.10, -0.56, 0.0), (-0.96, 0.56, 0.20))
    V.add_box(bm, (0.96, -0.56, 0.0), (1.10, 0.56, 0.20))
    objs.append(V.bm_to_object(bm, "bed_curb", ("M_stone_dark",)))

    # 2. Chamfered limestone coping lip & 4 carved corner bollards
    bm_t = bmesh.new()
    V.add_box(bm_t, (-1.13, -0.73, 0.20), (1.13, -0.54, 0.25))
    V.add_box(bm_t, (-1.13, 0.54, 0.20), (1.13, 0.73, 0.25))
    V.add_box(bm_t, (-1.13, -0.54, 0.20), (-0.94, 0.54, 0.25))
    V.add_box(bm_t, (0.94, -0.54, 0.20), (1.13, 0.54, 0.25))
    for cx in (-1.03, 1.03):
        for cy in (-0.63, 0.63):
            V.add_box(bm_t, (cx - 0.11, cy - 0.11, 0.0), (cx + 0.11, cy + 0.11, 0.30))
            V.add_box(bm_t, (cx - 0.08, cy - 0.08, 0.30), (cx + 0.08, cy + 0.08, 0.35))
    objs.append(V.bm_to_object(bm_t, "bed_coping", ("M_stone_trim",)))

    # 3. Mounded organic soil bed + gnarled woody shrub stems
    bm_w = bmesh.new()
    nx, ny = 8, 5
    grid = {}
    for ix in range(nx + 1):
        for iy in range(ny + 1):
            u = ix / float(nx) * 2.0 - 1.0
            v = iy / float(ny) * 2.0 - 1.0
            dome = max(0.0, (1.0 - u * u * 0.85) * (1.0 - v * v * 0.85))
            hz = 0.11 + 0.09 * dome + rng.uniform(-0.012, 0.012)
            grid[(ix, iy)] = bm_w.verts.new((u * 0.96, v * 0.56, hz))
    for ix in range(nx):
        for iy in range(ny):
            bm_w.faces.new((grid[(ix, iy)], grid[(ix + 1, iy)], grid[(ix + 1, iy + 1)], grid[(ix, iy + 1)]))
    objs.append(V.bm_to_object(bm_w, "bed_soil", ("M_wood",)))

    # Woody twisted stems/branches in both Glory and Ruin
    n_shrubs = 7 if alive else 9
    shrub_centers = []
    for i in range(n_shrubs):
        sx = -0.75 + 1.50 * (i / max(n_shrubs - 1, 1)) + rng.uniform(-0.08, 0.08)
        sy = rng.uniform(-0.32, 0.32)
        shrub_centers.append((sx, sy))
        for b_idx in range(3):
            ang = rng.uniform(0, 2 * math.pi)
            reach = rng.uniform(0.10, 0.22)
            top_z = rng.uniform(0.28, 0.44)
            pts = [
                (sx, sy, 0.14),
                (sx + reach * 0.45 * math.cos(ang), sy + reach * 0.45 * math.sin(ang), 0.22),
                (sx + reach * math.cos(ang + 0.3), sy + reach * math.sin(ang + 0.3), top_z),
            ]
            stem = V.sweep_profile(f"stem_{i}_{b_idx}", pts, V.circle_profile(0.014, 6), "M_wood")
            objs.append(stem)

    # 4. Foliage & blossoms mesh (vertex-colored M_foliage)
    bm2 = bmesh.new()
    face_cols = []

    def _add_leaf(origin, dir_xy, pitch, length, width, col):
        ox, oy, oz = origin
        dx, dy = dir_xy
        px, py = -dy, dx
        mid_z = oz + length * 0.55 * math.sin(pitch)
        tip_z = oz + length * math.sin(pitch) - 0.02
        r_mid = length * 0.52 * math.cos(pitch)
        r_tip = length * math.cos(pitch)
        pts = (
            (ox, oy, oz),
            (ox + dx * r_mid - px * width, oy + dy * r_mid - py * width, mid_z),
            (ox + dx * r_tip, oy + dy * r_tip, tip_z),
            (ox + dx * r_mid + px * width, oy + dy * r_mid + py * width, mid_z),
        )
        for wind in ((0, 1, 2, 3), (3, 2, 1, 0)):
            try:
                vs = [bm2.verts.new(pts[idx]) for idx in wind]
                bm2.faces.new(vs)
                face_cols.append(col)
            except ValueError:
                pass

    if alive:
        # Lush layered cloister boxwood/fern rosettes + white/gold/lavender lilies
        for sx, sy in shrub_centers:
            for k in range(14):
                a = k * (2 * math.pi / 14.0) + rng.uniform(-0.15, 0.15)
                pitch = rng.uniform(0.25, 0.95)
                length = rng.uniform(0.14, 0.26)
                width = rng.uniform(0.035, 0.058)
                g_val = rng.uniform(0.75, 1.15)
                col = (0.11 * g_val, 0.24 * g_val, 0.10 * g_val)
                _add_leaf((sx + rng.uniform(-0.06, 0.06), sy + rng.uniform(-0.06, 0.06), rng.uniform(0.16, 0.28)),
                          (math.cos(a), math.sin(a)), pitch, length, width, col)
            # Sculpted 5-petal cloister lily clusters atop the foliage
            for fl_i in range(2):
                fx = sx + rng.uniform(-0.10, 0.10)
                fy = sy + rng.uniform(-0.10, 0.10)
                fz = rng.uniform(0.30, 0.42)
                petal_col = rng.choice([
                    (0.92, 0.88, 0.74),  # ivory cloister lily
                    (0.94, 0.80, 0.42),  # golden vesper marigold
                    (0.76, 0.68, 0.88),  # pale bellflower
                ])
                for p_i in range(5):
                    pa = p_i * (2 * math.pi / 5.0) + fl_i * 0.4
                    _add_leaf((fx, fy, fz), (math.cos(pa), math.sin(pa)), 0.35, 0.065, 0.024, petal_col)
    else:
        # Withered dark bramble leaves & fallen dead foliage around the skeletal stems
        for sx, sy in shrub_centers:
            for k in range(8):
                a = rng.uniform(0, 2 * math.pi)
                pitch = rng.uniform(-0.15, 0.55)
                length = rng.uniform(0.10, 0.20)
                width = rng.uniform(0.025, 0.042)
                w_val = rng.uniform(0.75, 1.15)
                col = (0.16 * w_val, 0.13 * w_val, 0.09 * w_val)
                _add_leaf((sx + rng.uniform(-0.08, 0.08), sy + rng.uniform(-0.08, 0.08), rng.uniform(0.15, 0.26)),
                          (math.cos(a), math.sin(a)), pitch, length, width, col)

    mesh = __import__("bpy").data.meshes.new("growth")
    bm2.normal_update()
    bm2.to_mesh(mesh)
    bm2.free()
    attr = mesh.color_attributes.new(name="Col", type='BYTE_COLOR', domain='CORNER')
    mesh.color_attributes.active_color = attr
    for pi, poly in enumerate(mesh.polygons):
        c = face_cols[pi % len(face_cols)] if face_cols else (0.14, 0.24, 0.10)
        for li in poly.loop_indices:
            attr.data[li].color = (c[0], c[1], c[2], 1.0)
    growth = V.new_object("growth", mesh)
    growth.data.materials.append(V.material("M_foliage"))
    return objs + [growth], {"size": [2.26, 1.46, 0.5], "origin": "bottom-center"}


def censer_hanging(drop=1.5):
    """Gold cathedral thurible on a chain fixed to the vault by an iron ceiling-plate,
    with lower incense bowl, glowing ember core + flame, pierced gothic spire cover,
    and 3 suspension chains."""
    objs = []
    # Ceiling rose / mount plate + chain links
    bm_iron = bmesh.new()
    V.add_cyl(bm_iron, 0.0, 0.0, -0.02, 0.06, 0.12, n=10)
    V.add_cyl(bm_iron, 0.0, 0.0, -0.09, 0.07, 0.04, n=8)
    n = max(4, int(drop / 0.14))
    for i in range(n):
        z = -0.09 - i * 0.14
        wx = 0.028 if i % 2 else 0.012
        wy = 0.012 if i % 2 else 0.028
        V.add_box(bm_iron, (-wx, -wy, z - 0.11), (wx, wy, z))
    cz = -0.09 - n * 0.14
    # 3 diagonal suspension chains from central swivel (cz + 0.03) to bowl lugs (cz - 0.21)
    for k in range(3):
        a = k * 2 * math.pi / 3.0
        for s in range(5):
            u = s / 4.0
            r_u = 0.02 + 0.095 * u
            z_u = (cz + 0.03) - 0.24 * u
            cx, cy = r_u * math.cos(a), r_u * math.sin(a)
            V.add_box(bm_iron, (cx - 0.008, cy - 0.008, z_u - 0.028), (cx + 0.008, cy + 0.028, z_u + 0.028))
    objs.append(V.bm_to_object(bm_iron, "mount", ("M_iron",)))

    # Two-piece gold thurible: lower incense bowl + upper pierced spire canopy
    bowl = V.loft_rings(
        "censer",
        [
            (0.055, cz - 0.38, 12, 0),
            (0.038, cz - 0.35, 12, 0),
            (0.105, cz - 0.28, 12, 0),
            (0.120, cz - 0.21, 12, 0),
            (0.095, cz - 0.20, 12, 0),
        ],
        "M_gold",
    )
    objs.append(bowl)
    cover = V.loft_rings(
        "censer_cover",
        [
            (0.115, cz - 0.15, 12, 0),
            (0.085, cz - 0.09, 12, 0),
            (0.045, cz - 0.04, 12, 0),
            (0.012, cz + 0.01, 12, 0),
        ],
        "M_gold",
    )
    objs.append(cover)
    coals = V.loft_rings(
        "censer_coals",
        [(0.085, cz - 0.21, 10, 0), (0.055, cz - 0.175, 10, 0.3), (0.015, cz - 0.16, 10, 0.6)],
        "M_ember",
    )
    objs.append(coals)
    f = _flame("censer_flame", 0.032, 0.09)
    f.location = (0, 0, cz - 0.19)
    objs.append(f)
    return objs, {"size": [0.3, 0.3, drop + 0.6], "origin": "ceiling-mount"}


def censer_fallen(seed=29):
    """The same two-piece gold thurible, spilled on the flags with its chain and cold ash."""
    rng = random.Random(seed)
    objs = []
    cens = V.loft_rings(
        "censer_f",
        [
            (0.055, 0.0, 12, 0),
            (0.038, 0.03, 12, 0),
            (0.105, 0.10, 12, 0),
            (0.120, 0.17, 12, 0),
            (0.085, 0.22, 12, 0),
            (0.115, 0.24, 12, 0),
            (0.075, 0.31, 12, 0),
            (0.015, 0.38, 12, 0),
        ],
        "M_gold",
    )
    cens.rotation_euler = (0, math.radians(96), rng.uniform(0, 6))
    cens.location = (0, 0, 0.11)
    objs.append(cens)
    pts = [(0.15, 0, 0.02)]
    for i in range(7):
        pts.append((0.15 + (i + 1) * 0.12, rng.uniform(-0.1, 0.1), 0.02))
    objs.append(V.sweep_profile("chain_f", pts, V.circle_profile(0.018, 6), "M_iron", up_hint=Vector((0, 0, 1))))
    return objs, {"size": [1.2, 0.4, 0.4], "origin": "bottom-center"}


def ivy_sheet(seed=31):
    """Creeper sheet for ruin walls: drooping woody stems studded with two-sided
    leaf blades. Mount against a wall face (leaves spread in local XZ, wall at y=0)."""
    rng = random.Random(seed)
    objs = []
    bm = bmesh.new()
    col_entries = []
    for s in range(6):
        x0 = rng.uniform(-1.5, 1.5)
        top = rng.uniform(2.2, 3.4)
        length = rng.uniform(1.2, 2.6)
        sway = rng.uniform(-0.35, 0.35)
        n = int(length / 0.16)
        stem_pts = []
        for i in range(n):
            t = i / max(n - 1, 1)
            x = x0 + sway * t * t + math.sin(t * 9 + s) * 0.06
            z = top - length * t
            stem_pts.append((x, -0.02, z))
            size = rng.uniform(0.08, 0.14) * (1.0 - 0.3 * t)
            a = rng.uniform(0, 2 * math.pi)
            y0 = -0.02 - 0.03 * rng.random()
            c0 = (x, y0, z)
            c1 = (x + size * math.cos(a), -0.055, z + size * math.sin(a))
            c2 = (x + size * math.cos(a + 2.1), -0.055, z + size * math.sin(a + 2.1))
            g = rng.uniform(0.7, 1.0)
            col = (0.14 * g, 0.24 * g, 0.10 * g)
            p0, p1, p2 = bm.verts.new(c0), bm.verts.new(c1), bm.verts.new(c2)
            bm.faces.new((p0, p1, p2))
            col_entries.append(col)
            q0, q1, q2 = bm.verts.new(c0), bm.verts.new(c1), bm.verts.new(c2)
            bm.faces.new((q2, q1, q0))
            col_entries.append(col)
        if len(stem_pts) >= 2:
            objs.append(V.sweep_profile("ivy_stem_%d" % s, stem_pts, V.circle_profile(0.012, 6),
                                        "M_wood", up_hint=Vector((0, 1, 0))))
    mesh = __import__("bpy").data.meshes.new("ivy")
    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()
    attr = mesh.color_attributes.new(name="Col", type='BYTE_COLOR', domain='CORNER')
    mesh.color_attributes.active_color = attr
    for pi, poly in enumerate(mesh.polygons):
        c = col_entries[pi % len(col_entries)]
        for li in poly.loop_indices:
            attr.data[li].color = (c[0], c[1], c[2], 1.0)
    obj = V.new_object("ivy", mesh)
    obj.data.materials.append(V.material("M_foliage"))
    objs.append(obj)
    return objs, {"size": [3.4, 0.15, 3.5], "origin": "wall-base"}


def book_stack(seed=37):
    """Stack of leather-bound monastic folios with overhanging cover boards,
    recessed parchment page blocks, raised spine cords, and brass clasps."""
    rng = random.Random(seed)
    bm_cov = bmesh.new()
    bm_pages = bmesh.new()
    bm_brass = bmesh.new()

    def _rot_box(bm, cx, cy, z0, z1, x0, x1, y0, y1, ca, sa):
        pts = ((x0, y0), (x1, y0), (x1, y1), (x0, y1))
        vb = [bm.verts.new((cx + px * ca - py * sa, cy + px * sa + py * ca, z0)) for (px, py) in pts]
        vt = [bm.verts.new((cx + px * ca - py * sa, cy + px * sa + py * ca, z1)) for (px, py) in pts]
        bm.faces.new(reversed(vb))
        bm.faces.new(vt)
        for k in range(4):
            bm.faces.new((vb[k], vb[(k + 1) % 4], vt[(k + 1) % 4], vt[k]))

    z = 0.0
    for i in range(rng.randint(4, 6)):
        w = rng.uniform(0.16, 0.24)
        d = rng.uniform(0.12, 0.18)
        h = rng.uniform(0.036, 0.058)
        bd = 0.006
        a = rng.uniform(-0.4, 0.4)
        ca, sa = math.cos(a), math.sin(a)
        cx, cy = rng.uniform(-0.02, 0.02), rng.uniform(-0.02, 0.02)
        # Bottom cover board, top cover board, and spine backstrip (-X side)
        _rot_box(bm_cov, cx, cy, z, z + bd, -w, w, -d, d, ca, sa)
        _rot_box(bm_cov, cx, cy, z + h - bd, z + h, -w, w, -d, d, ca, sa)
        _rot_box(bm_cov, cx, cy, z + bd, z + h - bd, -w, -w + 0.018, -d, d, ca, sa)
        # Raised spine bands
        for sy in (-d * 0.55, 0.0, d * 0.55):
            _rot_box(bm_cov, cx, cy, z + 0.002, z + h - 0.002, -w - 0.006, -w + 0.012, sy - 0.008, sy + 0.008, ca, sa)
        # Recessed cream parchment page block
        _rot_box(bm_pages, cx, cy, z + bd, z + h - bd, -w + 0.018, w - 0.012, -d + 0.010, d - 0.010, ca, sa)
        # Brass fore-edge clasps on +X side
        for sy in (-d * 0.45, d * 0.45):
            _rot_box(bm_brass, cx, cy, z + 0.003, z + h - 0.003, w - 0.016, w + 0.004, sy - 0.010, sy + 0.010, ca, sa)
        z += h
    objs = [
        V.bm_to_object(bm_cov, "books", ("M_leather",)),
        V.bm_to_object(bm_pages, "book_pages", ("M_wax",)),
        V.bm_to_object(bm_brass, "book_clasps", ("M_brass",)),
    ]
    return objs, {"size": [0.5, 0.4, 0.35], "origin": "bottom-center"}


def scroll_pile(seed=41):
    """Pile of rolled parchment scrolls with turned wooden roller rods and
    crimson ribbon bands."""
    from mathutils import Matrix
    rng = random.Random(seed)
    bm_wax = bmesh.new()
    bm_wood = bmesh.new()
    bm_cloth = bmesh.new()
    for i in range(5):
        a = rng.uniform(0, math.pi)
        loc = Vector((rng.uniform(-0.1, 0.1), rng.uniform(-0.1, 0.1), 0.035 + (0.05 if i > 2 else 0)))
        xf = Matrix.Translation(loc) @ Matrix.Rotation(a, 4, "Z") @ Matrix.Rotation(math.radians(90), 4, "X")
        bm_tmp = bmesh.new()
        V.add_cyl(bm_tmp, 0.0, 0.0, -0.16, 0.32, 0.031, n=10)
        bmesh.ops.transform(bm_tmp, matrix=xf, verts=bm_tmp.verts)
        for f in bm_tmp.faces:
            bm_wax.faces.new([bm_wax.verts.new(v.co) for v in f.verts])
        bm_tmp.free()

        bm_tmp = bmesh.new()
        V.add_cyl(bm_tmp, 0.0, 0.0, -0.21, 0.42, 0.011, n=8)
        V.add_cyl(bm_tmp, 0.0, 0.0, -0.20, 0.025, 0.019, n=8)
        V.add_cyl(bm_tmp, 0.0, 0.0, 0.175, 0.025, 0.019, n=8)
        bmesh.ops.transform(bm_tmp, matrix=xf, verts=bm_tmp.verts)
        for f in bm_tmp.faces:
            bm_wood.faces.new([bm_wood.verts.new(v.co) for v in f.verts])
        bm_tmp.free()

        bm_tmp = bmesh.new()
        V.add_cyl(bm_tmp, 0.0, 0.0, -0.022, 0.044, 0.034, n=10)
        bmesh.ops.transform(bm_tmp, matrix=xf, verts=bm_tmp.verts)
        for f in bm_tmp.faces:
            bm_cloth.faces.new([bm_cloth.verts.new(v.co) for v in f.verts])
        bm_tmp.free()
    bmesh.ops.remove_doubles(bm_wax, verts=bm_wax.verts, dist=0.0005)
    bmesh.ops.remove_doubles(bm_wood, verts=bm_wood.verts, dist=0.0005)
    bmesh.ops.remove_doubles(bm_cloth, verts=bm_cloth.verts, dist=0.0005)
    objs = [
        V.bm_to_object(bm_wax, "scroll", ("M_wax",)),
        V.bm_to_object(bm_wood, "scroll_rods", ("M_wood",)),
        V.bm_to_object(bm_cloth, "scroll_bands", ("M_cloth",)),
    ]
    return objs, {"size": [0.5, 0.5, 0.15], "origin": "bottom-center"}


BUILDERS = {
    "candle_cluster": lambda: candle_cluster(True),
    "candle_cluster_dead": lambda: candle_cluster(False, seed=8),
    "wax_husk": wax_husk,
    "banner_torn": banner_torn,
    "garden_bed": lambda: garden_bed(True),
    "garden_bed_dead": lambda: garden_bed(False, seed=24),
    "censer_hanging": censer_hanging,
    "censer_fallen": censer_fallen,
    "ivy_sheet_a": lambda: ivy_sheet(31),
    "ivy_sheet_b": lambda: ivy_sheet(35),
    "book_stack": book_stack,
    "scroll_pile": scroll_pile,
}
