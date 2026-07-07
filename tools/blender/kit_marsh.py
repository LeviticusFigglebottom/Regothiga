"""Drowned Marches kit: reeds, beacons and waystones of the causeway out of
the remembered kingdom. Z up; exporter maps Z->Y.
"""
import math
import random
import bmesh

import vglib as V


def _blade(bm, x, y, h, lean_x, lean_y, w=0.03):
    """One reed blade: a thin tapering triangle leaning off vertical."""
    a = bm.verts.new((x - w, y, 0.0))
    b = bm.verts.new((x + w, y, 0.0))
    tip = bm.verts.new((x + lean_x, y + lean_y, h))
    bm.faces.new((a, b, tip))


def reed_clump(seed=5):
    """Living marsh reeds: a stand of tall blades with pale seed heads.
    Passable decor for the flats. Origin bottom-center."""
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
        V.add_box(hm, (hx - 0.035, hy - 0.035, hz - 0.16), (hx + 0.035, hy + 0.035, hz + 0.04))
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
    """Causeway beacon: iron tripod bearing a barred fire-basket on a stone
    foot — the marker fires that once walked pilgrims out of the kingdom.
    The Kindling puzzle interacts with these. Solid. Origin bottom-center."""
    objs = []
    sm = bmesh.new()
    V.add_box(sm, (-0.55, -0.55, 0.0), (0.55, 0.55, 0.22))
    objs.append(V.bm_to_object(sm, "beacon_foot", ("M_stone_dark",)))
    bm = bmesh.new()
    for i in range(3):
        a = math.tau * i / 3
        x0, y0 = math.cos(a) * 0.42, math.sin(a) * 0.42
        x1, y1 = math.cos(a) * 0.16, math.sin(a) * 0.16
        # leaning leg from foot to basket rim
        leg = bmesh.new()
        lo = leg.verts.new((x0 - 0.04, y0 - 0.04, 0.2))
        lo2 = leg.verts.new((x0 + 0.04, y0 + 0.04, 0.2))
        hi = leg.verts.new((x1 + 0.03, y1 + 0.03, 1.55))
        hi2 = leg.verts.new((x1 - 0.03, y1 - 0.03, 1.55))
        leg.faces.new((lo, lo2, hi, hi2))
        objs.append(V.bm_to_object(leg, "beacon_leg", ("M_iron",)))
    basket = V.loft_rings("beacon_basket", [(0.30, 1.5, 9, 0), (0.42, 1.78, 9, 0), (0.40, 1.95, 9, 0)],
                          "M_iron", cap_bottom=True, cap_top=False)
    objs.append(basket)
    # coal bed waiting for the flame (glory-gated ember glow reads as kindled)
    coals = V.loft_rings("beacon_coals", [(0.30, 1.72, 9, 0), (0.18, 1.86, 9, 0), (0.05, 1.9, 9, 0)],
                         "M_ember")
    objs.append(coals)
    return objs, {"size": [1.2, 1.2, 2.0], "origin": "bottom-center"}


def waystone(seed=13):
    """A leaning pilgrim waystone: tall slab, carved ring sigil. Solid."""
    rng = random.Random(seed)
    objs = []
    bm = bmesh.new()
    V.add_box(bm, (-0.34, -0.16, 0.0), (0.34, 0.16, 1.7))
    slab = V.bm_to_object(bm, "waystone", ("M_stone",))
    slab.rotation_euler = (rng.uniform(-0.09, 0.09), rng.uniform(-0.14, 0.14), rng.uniform(0, 0.5))
    objs.append(slab)
    ring = V.loft_rings("way_ring", [(0.2, 1.2, 10, 0), (0.2, 1.24, 10, 0)], "M_stone_trim",
                        cap_bottom=False, cap_top=False)
    ring.rotation_euler = (math.pi / 2, 0, 0)
    ring.location = (0, -0.18, 0)
    objs.append(ring)
    return objs, {"size": [0.8, 0.4, 1.8], "origin": "bottom-center"}


BUILDERS = {
    "reed_clump": reed_clump,
    "reed_clump_dead": reed_clump_dead,
    "beacon_brazier": beacon_brazier,
    "waystone": waystone,
}
