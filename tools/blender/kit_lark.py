"""Larkspire kit: cages, perches and the great roost of the song-tower.

Glory pieces keep their birds and gilding; ruin variants are bent iron and
empty rails. All playable-scale. Z up, exporter maps Z->Y.
"""
import math
import random
import bmesh

import vglib as V


def _lark(name, mat="M_bone"):
    """A chunky little songbird, ~0.18 long, sitting. Origin at its feet."""
    objs = []
    bm = bmesh.new()
    # body (plump box, tapered tail)
    V.add_box(bm, (-0.045, -0.05, 0.02), (0.045, 0.07, 0.10))
    # head
    V.add_box(bm, (-0.032, 0.045, 0.09), (0.032, 0.10, 0.15))
    # tail: thin slab angling up-back
    V.add_box(bm, (-0.022, -0.12, 0.05), (0.022, -0.04, 0.075))
    body = V.bm_to_object(bm, name + "_body", (mat,))
    objs.append(body)
    # beak
    bk = bmesh.new()
    a = bk.verts.new((-0.012, 0.10, 0.115)); b = bk.verts.new((0.012, 0.10, 0.115))
    c = bk.verts.new((0.0, 0.10, 0.135)); tip = bk.verts.new((0.0, 0.15, 0.118))
    bk.faces.new((a, b, tip)); bk.faces.new((b, c, tip)); bk.faces.new((c, a, tip))
    objs.append(V.bm_to_object(bk, name + "_beak", ("M_gold",)))
    return objs


def _cage_frame(bm_gold, r=0.24, z0=0.0, h=0.42, bars=10, bent_rng=None):
    """Dome-topped hanging cage frame built into bm_gold. Returns door info."""
    # base + crown rings
    for (rr, zz, th) in ((r, z0, 0.025), (r, z0 + h, 0.02)):
        seg = 12
        for i in range(seg):
            a0 = math.tau * i / seg
            a1 = math.tau * (i + 1) / seg
            x0, y0 = rr * math.cos(a0), rr * math.sin(a0)
            x1, y1 = rr * math.cos(a1), rr * math.sin(a1)
            V.add_box(bm_gold, (min(x0, x1) - th, min(y0, y1) - th, zz - th),
                      (max(x0, x1) + th, max(y0, y1) + th, zz + th))
    # vertical bars (one may be bent outward by bent_rng)
    for i in range(bars):
        a = math.tau * i / bars
        x, y = r * math.cos(a), r * math.sin(a)
        lean = 0.0
        if bent_rng is not None and bent_rng.random() < 0.3:
            lean = bent_rng.uniform(0.05, 0.14)
        V.add_box(bm_gold, (x - 0.012 - lean * 0.5, y - 0.012, z0),
                  (x + 0.012 + lean, y + 0.012, z0 + h))
    # dome ribs meeting at a finial point
    tip = z0 + h + r * 0.75
    for i in range(4):
        a = math.tau * i / 4
        x, y = r * math.cos(a), r * math.sin(a)
        V.add_box(bm_gold, (min(x, 0) - 0.012, min(y, 0) - 0.012, z0 + h - 0.01),
                  (max(x, 0) + 0.012, max(y, 0) + 0.012, tip))
    return tip


def lark_cage(drop=1.6):
    """Gilded hanging lark cage on a chain from a ceiling plate; a lark sits on
    the inner perch. Glory dressing for the spire shaft. Origin: ceiling-mount."""
    objs = []
    plate = V.loft_rings("mount", [(0.12, 0.04, 8, 0), (0.12, -0.02, 8, 0), (0.03, -0.09, 8, 0)], "M_iron")
    objs.append(plate)
    n = max(4, int(drop / 0.14))
    for i in range(n):
        z = -0.09 - i * 0.14
        link = V.loft_rings("link", [(0.028, z, 6, 0), (0.02, z - 0.1, 6, 0)], "M_iron")
        objs.append(link)
    cz = -0.09 - n * 0.14          # cage crown hangs here
    bm = bmesh.new()
    _cage_frame(bm, r=0.24, z0=cz - 0.75, h=0.42)
    # perch bar across the cage
    V.add_box(bm, (-0.22, -0.015, cz - 0.55), (0.22, 0.015, cz - 0.52))
    objs.append(V.bm_to_object(bm, "cage", ("M_gold",)))
    # floor disc of the cage
    disc = V.loft_rings("cage_floor", [(0.235, cz - 0.77, 12, 0), (0.235, cz - 0.75, 12, 0)], "M_iron")
    objs.append(disc)
    for o in _lark("lark"):
        o.location = (0.02, 0, cz - 0.52)
        objs.append(o)
    return objs, {"size": [0.55, 0.55, drop + 1.3], "origin": "ceiling-mount"}


def lark_cage_dead(drop=1.6, seed=41):
    """The same cage in ruin: rusted iron, bars bent outward, door fallen open,
    nothing inside. Origin: ceiling-mount."""
    rng = random.Random(seed)
    objs = []
    plate = V.loft_rings("mount_d", [(0.12, 0.04, 8, 0), (0.12, -0.02, 8, 0), (0.03, -0.09, 8, 0)], "M_iron")
    objs.append(plate)
    n = max(4, int(drop / 0.14))
    for i in range(n):
        z = -0.09 - i * 0.14
        link = V.loft_rings("link_d", [(0.028, z, 6, 0), (0.02, z - 0.1, 6, 0)], "M_iron")
        objs.append(link)
    cz = -0.09 - n * 0.14
    bm = bmesh.new()
    _cage_frame(bm, r=0.24, z0=cz - 0.75, h=0.42, bent_rng=rng)
    objs.append(V.bm_to_object(bm, "cage_d", ("M_iron",)))
    # the sprung door: a small barred quad hanging askew off the rim
    dbm = bmesh.new()
    V.add_box(dbm, (0.2, -0.09, cz - 0.72), (0.24, 0.09, cz - 0.5))
    door = V.bm_to_object(dbm, "cage_door", ("M_iron",))
    door.rotation_euler = (0.5, 0.15, 0.2)
    objs.append(door)
    return objs, {"size": [0.55, 0.55, drop + 1.3], "origin": "ceiling-mount"}


def cage_stand():
    """Office-cage station: a waist-high stone pedestal bearing a gilded cage
    with its lark. The Daily Offices puzzle interacts with these. Solid."""
    objs = []
    bm = bmesh.new()
    V.add_box(bm, (-0.34, -0.34, 0), (0.34, 0.34, 0.1))
    V.add_box(bm, (-0.22, -0.22, 0.1), (0.22, 0.22, 0.92))
    V.add_box(bm, (-0.3, -0.3, 0.92), (0.3, 0.3, 1.0))
    objs.append(V.bm_to_object(bm, "stand", ("M_stone_dark",)))
    gm = bmesh.new()
    tip = _cage_frame(gm, r=0.26, z0=1.0, h=0.46)
    V.add_box(gm, (-0.24, -0.015, 1.2), (0.24, 0.015, 1.23))     # perch
    objs.append(V.bm_to_object(gm, "stand_cage", ("M_gold",)))
    for o in _lark("stand_lark"):
        o.location = (0.02, 0, 1.23)
        objs.append(o)
    return objs, {"size": [0.7, 0.7, 2.1], "origin": "bottom-center"}


def perch_rail():
    """Aviary perch: a timber rail on two posts, three larks shoulder to
    shoulder. Glory dressing. Origin bottom-center."""
    objs = []
    bm = bmesh.new()
    for px in (-0.8, 0.8):
        V.add_box(bm, (px - 0.05, -0.05, 0), (px + 0.05, 0.05, 1.15))
    V.add_box(bm, (-0.95, -0.04, 1.15), (0.95, 0.04, 1.23))
    objs.append(V.bm_to_object(bm, "perch", ("M_wood",)))
    rng = random.Random(7)
    for i, px in enumerate((-0.55, 0.0, 0.5)):
        for o in _lark("perch_lark%d" % i):
            o.location = (px, 0, 1.23)
            o.rotation_euler = (0, 0, rng.uniform(-0.6, 0.6))
            objs.append(o)
    return objs, {"size": [1.9, 0.3, 1.45], "origin": "bottom-center"}


def perch_rail_bare(seed=17):
    """The same rail in ruin: empty, leaning, one snapped chain swinging."""
    rng = random.Random(seed)
    objs = []
    bm = bmesh.new()
    for px in (-0.8, 0.8):
        V.add_box(bm, (px - 0.05, -0.05, 0), (px + 0.05, 0.05, 1.15))
    V.add_box(bm, (-0.95, -0.04, 1.15), (0.95, 0.04, 1.23))
    rail = V.bm_to_object(bm, "perch_b", ("M_wood",))
    rail.rotation_euler = (0, 0.06, 0)
    objs.append(rail)
    chain = V.loft_rings("perch_chain", [(0.02, 1.15, 6, 0), (0.016, 0.7, 6, 0)], "M_iron")
    chain.location = (rng.uniform(-0.4, 0.4), 0, 0)
    objs.append(chain)
    return objs, {"size": [1.9, 0.3, 1.45], "origin": "bottom-center"}


def great_perch():
    """The Larkwarden's roost: a tall gilded stand crowning the summit — stepped
    stone base, iron-strapped pole, two crossbars and a crowning ring. Bare in
    both states (the great lark is long flown); solid enough for boss cover."""
    objs = []
    bm = bmesh.new()
    V.add_box(bm, (-0.9, -0.9, 0), (0.9, 0.9, 0.22))
    V.add_box(bm, (-0.62, -0.62, 0.22), (0.62, 0.62, 0.44))
    objs.append(V.bm_to_object(bm, "roost_base", ("M_stone_dark",)))
    pole = V.loft_rings("roost_pole", [(0.14, 0.44, 8, 0), (0.11, 3.4, 8, 0)], "M_wood")
    objs.append(pole)
    gm = bmesh.new()
    for (w, z) in ((1.1, 2.2), (0.7, 3.0)):
        V.add_box(gm, (-w, -0.04, z), (w, 0.04, z + 0.08))
    objs.append(V.bm_to_object(gm, "roost_bars", ("M_gold",)))
    ring = V.loft_rings("roost_ring", [(0.30, 3.4, 10, 0), (0.34, 3.52, 10, 0), (0.28, 3.62, 10, 0)], "M_gold",
                        cap_bottom=False, cap_top=False)
    objs.append(ring)
    return objs, {"size": [2.2, 2.2, 3.7], "origin": "bottom-center"}


def aviary_screen():
    """4 m aviary lattice: iron frame, crossed timber slats — the songloft's
    airy wall dressing. Passable decor; place against openings."""
    objs = []
    fm = bmesh.new()
    V.add_box(fm, (-2.0, -0.05, 0), (2.0, 0.05, 0.12))
    V.add_box(fm, (-2.0, -0.05, 3.9), (2.0, 0.05, 4.0))
    for px in (-2.0, 2.0):
        V.add_box(fm, (px - 0.05, -0.05, 0), (px + 0.06, 0.05, 4.0))
    objs.append(V.bm_to_object(fm, "screen_frame", ("M_iron",)))
    sm = bmesh.new()
    x = -1.8
    while x < 1.9:
        V.add_box(sm, (x - 0.02, -0.02, 0.12), (x + 0.02, 0.02, 3.9))
        x += 0.36
    for z in (1.0, 2.0, 3.0):
        V.add_box(sm, (-2.0, -0.018, z - 0.02), (2.0, 0.018, z + 0.02))
    objs.append(V.bm_to_object(sm, "screen_slats", ("M_wood",)))
    return objs, {"size": [4, 0.12, 4], "origin": "bottom-center"}


BUILDERS = {
    "lark_cage": lark_cage,
    "lark_cage_dead": lark_cage_dead,
    "cage_stand": cage_stand,
    "perch_rail": perch_rail,
    "perch_rail_bare": perch_rail_bare,
    "great_perch": great_perch,
    "aviary_screen": aviary_screen,
}
