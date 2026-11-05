"""Drowned Marches kit: reeds, beacons and waystones of the causeway out of
the remembered kingdom. Z up; exporter maps Z->Y.
"""
import math
import random
import bmesh
from mathutils import Vector, Matrix

import vglib as V


def _blade(bm, x, y, h, lean_x, lean_y, w=0.03):
    """One reed blade: a thin tapering triangle leaning off vertical.
    Emitted in BOTH windings (fresh verts — bmesh refuses twin faces on
    shared ones) so the stem reads from every bank; one-sided blades left
    the seed heads floating when seen from the culled side."""
    a = bm.verts.new((x - w, y, 0.0))
    b = bm.verts.new((x + w, y, 0.0))
    tip = bm.verts.new((x + lean_x, y + lean_y, h))
    bm.faces.new((a, b, tip))
    a2 = bm.verts.new((x - w, y, 0.0))
    b2 = bm.verts.new((x + w, y, 0.0))
    tip2 = bm.verts.new((x + lean_x, y + lean_y, h))
    bm.faces.new((tip2, b2, a2))


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
    for i in range(3):
        a = math.tau * i / 3
        ca, sa = math.cos(a), math.sin(a)
        pts = [
            (ca * 0.42, sa * 0.42, 0.20),
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
    # Horizontal iron brace ring & vertical basket ribs
    bm_iron = bmesh.new()
    V.add_cyl(bm_iron, 0.0, 0.0, 0.84, 0.04, 0.31, n=12)
    V.add_cyl(bm_iron, 0.0, 0.0, 1.92, 0.045, 0.42, n=12)
    for i in range(8):
        a = math.tau * i / 8
        V.add_cyl(bm_iron, 0.36 * math.cos(a), 0.36 * math.sin(a), 1.52, 0.42, 0.014, n=6)
    objs.append(V.bm_to_object(bm_iron, "beacon_ribs", ("M_iron",)))

    basket = V.loft_rings(
        "beacon_basket",
        [(0.28, 1.48, 12, 0), (0.40, 1.76, 12, 0), (0.39, 1.94, 12, 0)],
        "M_iron",
        cap_bottom=True,
        cap_top=False,
    )
    objs.append(basket)
    # coal bed waiting for the flame (glory-gated ember glow reads as kindled)
    coals = V.loft_rings(
        "beacon_coals",
        [(0.32, 1.70, 12, 0), (0.20, 1.85, 12, 0.3), (0.05, 1.92, 12, 0.6)],
        "M_ember",
    )
    objs.append(coals)
    return objs, {"size": [1.2, 1.2, 2.0], "origin": "bottom-center"}


def waystone(seed=13):
    """A leaning pilgrim waystone: stepped stone base, gabled Gothic slab, and
    carved sun-ring sigil on both faces sharing the slab's lean. Solid."""
    rng = random.Random(seed)
    rx = rng.uniform(-0.07, 0.07)
    ry = rng.uniform(-0.11, 0.11)
    rz = rng.uniform(0, 0.4)
    objs = []
    bm = bmesh.new()
    V.add_box(bm, (-0.38, -0.20, 0.0), (0.38, 0.20, 0.16))
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
    slab = V.bm_to_object(bm, "waystone", ("M_stone",))
    slab.rotation_euler = (rx, ry, rz)
    objs.append(slab)

    # Carved relief sun-ring & stiles in M_stone_trim sharing the exact same lean
    bm_trim = bmesh.new()
    for sx in (-0.28, 0.28):
        V.add_box(bm_trim, (sx - 0.035, -0.165, 0.16), (sx + 0.035, 0.165, 1.48))
    for i in range(12):
        a0 = math.tau * i / 12
        a1 = math.tau * (i + 1) / 12
        xm = 0.18 * math.cos(0.5 * (a0 + a1))
        zm = 1.18 + 0.18 * math.sin(0.5 * (a0 + a1))
        V.add_box(bm_trim, (xm - 0.03, -0.175, zm - 0.03), (xm + 0.03, 0.175, zm + 0.03))
    V.add_box(bm_trim, (-0.04, -0.175, 1.14), (0.04, 0.175, 1.22))
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
