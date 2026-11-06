"""Drowned Marches kit: reeds, beacons and waystones of the causeway out of
the remembered kingdom. Z up; exporter maps Z->Y.
"""
import math
import random
import bmesh
from mathutils import Vector, Matrix

import vglib as V


def _blade(bm, x, y, h, lean_x, lean_y, w=0.03):
    """One reed blade: a curved 3-segment tapering stalk leaning off vertical.
    Emitted in BOTH windings (fresh verts — bmesh refuses twin faces on
    shared ones) so the stem reads from every bank."""
    segs = 3
    for flip in (False, True):
        rings = []
        for s in range(segs + 1):
            t = s / float(segs)
            # Quadratic bend so reed curves gracefully toward its tip
            bx = x + lean_x * (t * t)
            by = y + lean_y * (t * t)
            bz = h * t
            hw = w * (1.0 - 0.85 * t)
            if s == segs:
                rings.append([bm.verts.new((bx, by, bz))])
            else:
                rings.append([bm.verts.new((bx - hw, by, bz)), bm.verts.new((bx + hw, by, bz))])
        for s in range(segs):
            r0, r1 = rings[s], rings[s + 1]
            if len(r1) == 1:
                tri = (r0[0], r0[1], r1[0]) if not flip else (r1[0], r0[1], r0[0])
                bm.faces.new(tri)
            else:
                quad = (r0[0], r0[1], r1[1], r1[0]) if not flip else (r0[0], r1[0], r1[1], r0[1])
                bm.faces.new(quad)


def reed_clump(seed=5):
    """Living marsh reeds: a stand of tall blades with cylindrical cattail
    seed spikes. Passable decor for the flats. Origin bottom-center."""
    rng = random.Random(seed)
    objs = []
    bm = bmesh.new()
    heads = []
    for i in range(11):
        a = rng.uniform(0, math.tau)
        r = rng.uniform(0.05, 0.42)
        x, y = math.cos(a) * r, math.sin(a) * r
        h = rng.uniform(0.9, 1.7)
        lx, ly = rng.uniform(-0.22, 0.22), rng.uniform(-0.22, 0.22)
        _blade(bm, x, y, h, lx, ly)
        if rng.random() < 0.6:
            heads.append((x + lx, y + ly, h))
    objs.append(V.bm_to_object(bm, "reeds", ("M_habit",)))
    hm = bmesh.new()
    for (hx, hy, hz) in heads:
        V.add_cyl(hm, hx, hy, hz - 0.17, 0.17, 0.028, n=8)
        V.add_cyl(hm, hx, hy, hz, 0.05, 0.008, n=6)
    objs.append(V.bm_to_object(hm, "reed_heads", ("M_wax",)))
    return objs, {"size": [1.1, 1.1, 1.8], "origin": "bottom-center"}


def reed_clump_dead(seed=9):
    """The same stand in ruin: fewer blades, bent low, headless."""
    rng = random.Random(seed)
    bm = bmesh.new()
    for i in range(7):
        a = rng.uniform(0, math.tau)
        r = rng.uniform(0.05, 0.42)
        x, y = math.cos(a) * r, math.sin(a) * r
        h = rng.uniform(0.5, 1.1)
        _blade(bm, x, y, h, rng.uniform(-0.45, 0.45), rng.uniform(-0.45, 0.45))
    obj = V.bm_to_object(bm, "reeds_dead", ("M_habit",))
    return [obj], {"size": [1.1, 1.1, 1.2], "origin": "bottom-center"}


def beacon_brazier():
    """Causeway beacon: wrought-iron tripod with solid forged legs and ring
    braces bearing a ribbed fire-basket on a stepped stone foot — the marker
    fires that once walked pilgrims out of the kingdom. Solid."""
    objs = []
    sm = bmesh.new()
    V.add_box(sm, (-0.56, -0.56, 0.0), (0.56, 0.56, 0.12))
    V.add_box(sm, (-0.48, -0.48, 0.12), (0.48, 0.48, 0.22))
    objs.append(V.bm_to_object(sm, "beacon_foot", ("M_stone_dark",)))

    sm_trim = bmesh.new()
    V.add_box(sm_trim, (-0.58, -0.58, 0.10), (0.58, 0.58, 0.13))
    V.add_box(sm_trim, (-0.50, -0.50, 0.20), (0.50, 0.50, 0.24))
    objs.append(V.bm_to_object(sm_trim, "beacon_foot_trim", ("M_stone_trim",)))

    for i in range(3):
        a = math.tau * i / 3
        ca, sa = math.cos(a), math.sin(a)
        pts = [
            (ca * 0.42, sa * 0.42, 0.22),
            (ca * 0.30, sa * 0.30, 0.85),
            (ca * 0.18, sa * 0.18, 1.54),
        ]
        leg = V.sweep_profile(
            "beacon_leg",
            pts,
            V.circle_profile(0.032, 8),
            "M_iron",
            up_hint=Vector((-sa, ca, 0)),
        )
        objs.append(leg)

    # Hollow 3D horizontal iron brace hoop & top rim hoop (never solid discs)
    brace_hoop = V.loft_rings(
        "beacon_brace",
        [
            (0.26, 0.83, 16, 0),
            (0.32, 0.83, 16, 0),
            (0.32, 0.88, 16, 0),
            (0.26, 0.88, 16, 0),
            (0.26, 0.83, 16, 0),
        ],
        "M_iron",
        cap_bottom=False,
        cap_top=False,
    )
    objs.append(brace_hoop)

    rim_hoop = V.loft_rings(
        "beacon_rim",
        [
            (0.36, 1.90, 16, 0),
            (0.43, 1.90, 16, 0),
            (0.43, 1.96, 16, 0),
            (0.36, 1.96, 16, 0),
            (0.36, 1.90, 16, 0),
        ],
        "M_iron",
        cap_bottom=False,
        cap_top=False,
    )
    objs.append(rim_hoop)

    # Vertical basket ribs with outward-flared finials
    bm_iron = bmesh.new()
    for i in range(8):
        a = math.tau * i / 8
        ca, sa = math.cos(a), math.sin(a)
        V.add_cyl(bm_iron, 0.38 * ca, 0.38 * sa, 1.50, 0.48, 0.016, n=6)
        V.add_box(bm_iron, (0.40 * ca - 0.022, 0.40 * sa - 0.022, 1.96), (0.40 * ca + 0.022, 0.40 * sa + 0.022, 2.02))
    objs.append(V.bm_to_object(bm_iron, "beacon_ribs", ("M_iron",)))

    # Double-walled 3D iron fire-basket
    basket = V.loft_rings(
        "beacon_basket",
        [
            (0.26, 1.48, 16, 0),
            (0.38, 1.76, 16, 0),
            (0.40, 1.94, 16, 0),
            (0.35, 1.94, 16, 0),
            (0.33, 1.74, 16, 0),
            (0.22, 1.54, 16, 0),
        ],
        "M_iron",
        cap_bottom=True,
        cap_top=True,
    )
    objs.append(basket)

    # Mounded coal bed rising visibly above the open basket rim (glory-gated ember glow)
    coals = V.loft_rings(
        "beacon_coals",
        [
            (0.34, 1.68, 14, 0),
            (0.36, 1.88, 14, 0.2),
            (0.24, 1.98, 14, 0.4),
            (0.06, 2.05, 14, 0.6),
        ],
        "M_ember",
    )
    objs.append(coals)
    return objs, {"size": [1.2, 1.2, 2.05], "origin": "bottom-center"}


def waystone(seed=13):
    """A leaning pilgrim waystone: stepped stone base, gabled Gothic slab, and
    carved sun-ring sigil on both faces sharing the slab's lean. Solid."""
    rng = random.Random(seed)
    rx = rng.uniform(-0.07, 0.07)
    ry = rng.uniform(-0.11, 0.11)
    rz = rng.uniform(0, 0.4)
    objs = []
    bm_base = bmesh.new()
    V.add_box(bm_base, (-0.38, -0.20, 0.0), (0.38, 0.20, 0.16))
    base = V.bm_to_object(bm_base, "way_base", ("M_stone_dark",))
    base.rotation_euler = (rx, ry, rz)
    objs.append(base)

    bm = bmesh.new()
    V.add_box(bm, (-0.32, -0.15, 0.16), (0.32, 0.15, 1.48))
    # Gabled pointed apex on the waystone
    a = [bm.verts.new(p) for p in ((-0.32, -0.15, 1.48), (0.32, -0.15, 1.48), (0.32, 0.15, 1.48), (-0.32, 0.15, 1.48))]
    r0 = bm.verts.new((0.0, -0.15, 1.72))
    r1 = bm.verts.new((0.0, 0.15, 1.72))
    bm.faces.new((a[0], a[1], r0))
    bm.faces.new((a[2], a[3], r1))
    bm.faces.new((a[0], r0, r1, a[3]))
    bm.faces.new((r0, a[1], a[2], r1))
    bm.faces.new(list(reversed(a)))
    slab = V.bm_to_object(bm, "waystone", ("M_stone_trim",))
    slab.rotation_euler = (rx, ry, rz)
    objs.append(slab)

    # Carved relief sun-ring & stiles in M_stone_trim sharing the exact same lean
    bm_trim = bmesh.new()
    for sx in (-0.28, 0.28):
        V.add_box(bm_trim, (sx - 0.035, -0.165, 0.16), (sx + 0.035, 0.165, 1.48))
    # Continuous 16-sided relief sun-ring in X-Z plane at z=1.18
    n_seg = 16
    r_in, r_out = 0.145, 0.205
    for sy in (-1, 1):
        y0, y1 = (-0.178, -0.148) if sy < 0 else (0.148, 0.178)
        ring_v = []
        for i in range(n_seg):
            a = math.tau * i / n_seg
            ca, sa = math.cos(a), math.sin(a)
            ring_v.append((
                bm_trim.verts.new((r_in * ca, y0, 1.18 + r_in * sa)),
                bm_trim.verts.new((r_out * ca, y0, 1.18 + r_out * sa)),
                bm_trim.verts.new((r_out * ca, y1, 1.18 + r_out * sa)),
                bm_trim.verts.new((r_in * ca, y1, 1.18 + r_in * sa)),
            ))
        for i in range(n_seg):
            v0 = ring_v[i]
            v1 = ring_v[(i + 1) % n_seg]
            bm_trim.faces.new((v0[0], v0[1], v1[1], v1[0]))
            bm_trim.faces.new((v0[3], v1[3], v1[2], v0[2]))
            bm_trim.faces.new((v0[1], v0[2], v1[2], v1[1]))
            bm_trim.faces.new((v0[0], v1[0], v1[3], v0[3]))
    V.add_box(bm_trim, (-0.045, -0.178, 1.135), (0.045, 0.178, 1.225))
    ring = V.bm_to_object(bm_trim, "way_ring", ("M_stone_trim",))
    ring.rotation_euler = (rx, ry, rz)
    objs.append(ring)
    return objs, {"size": [0.8, 0.45, 1.8], "origin": "bottom-center"}


BUILDERS = {
    "reed_clump": reed_clump,
    "reed_clump_dead": reed_clump_dead,
    "beacon_brazier": beacon_brazier,
    "waystone": waystone,
}
