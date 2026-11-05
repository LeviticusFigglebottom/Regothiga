"""Larkspire kit: cages, perches and the great roost of the song-tower.

Glory pieces keep their birds and gilding; ruin variants are bent iron and
empty rails. All playable-scale. Z up, exporter maps Z->Y.
"""
import math
import random
import bmesh
from mathutils import Vector

import vglib as V


def _add_rod(bm, p0, p1, rad, segs=6):
    """Add a capped polygonal rod from p0 to p1 of radius rad into bm."""
    v0 = Vector(p0)
    v1 = Vector(p1)
    d = v1 - v0
    if d.length < 1e-5:
        return
    t = d.normalized()
    ref = Vector((0, 0, 1)) if abs(t.z) < 0.92 else Vector((1, 0, 0))
    u = t.cross(ref).normalized()
    w = t.cross(u).normalized()
    r0, r1 = [], []
    for i in range(segs):
        ang = math.tau * i / segs
        off = (u * math.cos(ang) + w * math.sin(ang)) * rad
        r0.append(bm.verts.new(v0 + off))
        r1.append(bm.verts.new(v1 + off))
    for i in range(segs):
        j = (i + 1) % segs
        try:
            bm.faces.new((r0[i], r0[j], r1[j], r1[i]))
        except ValueError:
            pass
    try:
        bm.faces.new(list(reversed(r0)))
        bm.faces.new(r1)
    except ValueError:
        pass


def _lark(name, mat="M_bone"):
    """A sculpted songbird, ~0.18 m long, sitting on its perch. Origin at feet."""
    objs = []
    bm = bmesh.new()
    # Multi-station organic avian profile along (y, z, rx, rz)
    stations = [
        (-0.125, 0.074, 0.022, 0.004),  # fanned tail tip
        (-0.085, 0.058, 0.016, 0.007),  # tail shaft
        (-0.050, 0.046, 0.020, 0.015),  # rump
        (-0.020, 0.052, 0.038, 0.030),  # belly / lower back
        ( 0.016, 0.062, 0.044, 0.036),  # plump breast
        ( 0.046, 0.080, 0.031, 0.027),  # throat / nape
        ( 0.062, 0.108, 0.028, 0.026),  # head crown
        ( 0.086, 0.116, 0.021, 0.020),  # brow / cheeks
        ( 0.100, 0.114, 0.010, 0.010),  # beak root
    ]
    n_seg = 10
    rings = []
    for (cy, cz, rx, rz) in stations:
        ring = []
        for i in range(n_seg):
            ang = math.tau * i / n_seg
            ring.append(bm.verts.new((rx * math.cos(ang), cy, cz + rz * math.sin(ang))))
        rings.append(ring)
    for k in range(len(rings) - 1):
        r0, r1 = rings[k], rings[k + 1]
        for i in range(n_seg):
            j = (i + 1) % n_seg
            bm.faces.new((r0[i], r0[j], r1[j], r1[i]))
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])

    # Folded wing shells hugging left/right flanks
    for sx in (-1, 1):
        w_stations = [
            (-0.055, 0.055, sx * 0.016, 0.005, 0.006),
            (-0.018, 0.064, sx * 0.038, 0.012, 0.022),
            ( 0.022, 0.070, sx * 0.040, 0.010, 0.020),
            ( 0.042, 0.074, sx * 0.028, 0.005, 0.010),
        ]
        w_rings = []
        for (wy, wz, wx, wrx, wrz) in w_stations:
            wr = []
            for i in range(6):
                ang = math.tau * i / 6
                wr.append(bm.verts.new((wx + wrx * math.cos(ang), wy, wz + wrz * math.sin(ang))))
            w_rings.append(wr)
        for k in range(len(w_rings) - 1):
            r0, r1 = w_rings[k], w_rings[k + 1]
            for i in range(6):
                j = (i + 1) % 6
                bm.faces.new((r0[i], r0[j], r1[j], r1[i]))
        bm.faces.new(list(reversed(w_rings[0])))
        bm.faces.new(w_rings[-1])

    # Slender legs + perched toes
    for sx in (-0.016, 0.016):
        _add_rod(bm, (sx, 0.002, 0.002), (sx, 0.010, 0.040), 0.0045, segs=5)
        _add_rod(bm, (sx, -0.012, 0.003), (sx, 0.018, 0.003), 0.0035, segs=4)

    body = V.bm_to_object(bm, name + "_body", (mat,))
    objs.append(body)
    # Conical golden beak
    bk = bmesh.new()
    _add_rod(bk, (0.0, 0.098, 0.114), (0.0, 0.142, 0.112), 0.002, segs=6)
    base_ring = [
        bk.verts.new((0.010 * math.cos(math.tau * i / 6), 0.098, 0.114 + 0.009 * math.sin(math.tau * i / 6)))
        for i in range(6)
    ]
    tip = bk.verts.new((0.0, 0.146, 0.111))
    for i in range(6):
        bk.faces.new((base_ring[i], base_ring[(i + 1) % 6], tip))
    bk.faces.new(list(reversed(base_ring)))
    objs.append(V.bm_to_object(bk, name + "_beak", ("M_gold",)))
    return objs


def _cage_frame(bm_gold, r=0.24, z0=0.0, h=0.42, bars=10, bent_rng=None):
    """Dome-topped hanging cage frame built into bm_gold. Returns finial tip Z."""
    # Base + mid-belly + crown rings (smooth 16-segment circular hoops)
    for (rr, zz, th) in ((r, z0, 0.016), (r, z0 + h * 0.18, 0.009), (r, z0 + h, 0.014)):
        seg = 16
        for i in range(seg):
            a0 = math.tau * i / seg
            a1 = math.tau * (i + 1) / seg
            p0 = (rr * math.cos(a0), rr * math.sin(a0), zz)
            p1 = (rr * math.cos(a1), rr * math.sin(a1), zz)
            _add_rod(bm_gold, p0, p1, th, segs=6)
    # Vertical bars (some bent outward if bent_rng is provided)
    for i in range(bars):
        a = math.tau * i / bars
        ca, sa = math.cos(a), math.sin(a)
        x, y = r * ca, r * sa
        lean = 0.0
        if bent_rng is not None and bent_rng.random() < 0.35:
            lean = bent_rng.uniform(0.06, 0.14)
        if lean > 0.0:
            xm, ym = (r + lean) * ca, (r + lean) * sa
            _add_rod(bm_gold, (x, y, z0), (xm, ym, z0 + h * 0.52), 0.0085, segs=5)
            _add_rod(bm_gold, (xm, ym, z0 + h * 0.52), (x + lean * 0.35 * ca, y + lean * 0.35 * sa, z0 + h), 0.0085, segs=5)
        else:
            _add_rod(bm_gold, (x, y, z0), (x, y, z0 + h), 0.0085, segs=5)
    # Arched dome ribs meeting at a finial crown
    dome_h = r * 0.75
    tip = z0 + h + dome_h
    n_ribs = max(6, bars // 2 * 2)
    rib_steps = 5
    for i in range(n_ribs):
        a = math.tau * i / n_ribs
        ca, sa = math.cos(a), math.sin(a)
        for s in range(rib_steps):
            t0 = (s / rib_steps) * (math.pi * 0.5)
            t1 = ((s + 1) / rib_steps) * (math.pi * 0.5)
            r0, zz0 = r * math.cos(t0), z0 + h + dome_h * math.sin(t0)
            r1, zz1 = r * math.cos(t1), z0 + h + dome_h * math.sin(t1)
            _add_rod(bm_gold, (r0 * ca, r0 * sa, zz0), (r1 * ca, r1 * sa, zz1), 0.009, segs=5)
    # Finial collar at dome apex
    _add_rod(bm_gold, (0.0, 0.0, tip - 0.015), (0.0, 0.0, tip + 0.035), 0.018, segs=8)
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
    """Office-cage station: a carved Gothic stone pedestal with stepped plinth,
    corner pilasters, and moulded cornice bearing a gilded cage with its lark.
    The Daily Offices puzzle interacts with these. Solid."""
    objs = []
    bm = bmesh.new()
    V.add_box(bm, (-0.36, -0.36, 0.0), (0.36, 0.36, 0.10))
    V.add_box(bm, (-0.30, -0.30, 0.10), (0.30, 0.30, 0.18))
    V.add_box(bm, (-0.21, -0.21, 0.18), (0.21, 0.21, 0.86))
    V.add_box(bm, (-0.28, -0.28, 0.86), (0.28, 0.28, 0.93))
    V.add_box(bm, (-0.33, -0.33, 0.93), (0.33, 0.33, 1.00))
    objs.append(V.bm_to_object(bm, "stand", ("M_stone_dark",)))

    bm_trim = bmesh.new()
    for sx in (-0.21, 0.21):
        for sy in (-0.21, 0.21):
            V.add_box(bm_trim, (sx - 0.035, sy - 0.035, 0.18), (sx + 0.035, sy + 0.035, 0.86))
    objs.append(V.bm_to_object(bm_trim, "stand_trim", ("M_stone_trim",)))

    gm = bmesh.new()
    tip = _cage_frame(gm, r=0.26, z0=1.0, h=0.46)
    V.add_box(gm, (-0.24, -0.015, 1.2), (0.24, 0.015, 1.23))     # perch
    objs.append(V.bm_to_object(gm, "stand_cage", ("M_gold",)))
    for o in _lark("stand_lark"):
        o.location = (0.02, 0, 1.23)
        objs.append(o)
    return objs, {"size": [0.7, 0.7, 2.1], "origin": "bottom-center"}


def perch_rail():
    """Aviary perch: a carved timber rail on two trestle-footed posts with
    iron bracket straps, three larks shoulder to shoulder. Glory dressing."""
    objs = []
    bm = bmesh.new()
    bm_iron = bmesh.new()
    for px in (-0.8, 0.8):
        V.add_box(bm, (px - 0.08, -0.20, 0.0), (px + 0.08, 0.20, 0.07))
        V.add_box(bm, (px - 0.06, -0.14, 0.07), (px + 0.06, 0.14, 0.12))
        V.add_box(bm, (px - 0.05, -0.05, 0.12), (px + 0.05, 0.05, 1.15))
        V.add_box(bm, (px - 0.065, -0.065, 1.23), (px + 0.065, 0.065, 1.31))
        V.add_box(bm, (px - 0.04, -0.04, 1.31), (px + 0.04, 0.04, 1.38))
        # Forged iron bracket straps & diagonal knee braces
        V.add_box(bm_iron, (px - 0.058, -0.058, 0.14), (px + 0.058, 0.058, 0.20))
        V.add_box(bm_iron, (px - 0.058, -0.058, 1.08), (px + 0.058, 0.058, 1.15))
        sx = -1 if px > 0 else 1
        _add_rod(bm_iron, (px, 0.0, 0.90), (px + sx * 0.22, 0.0, 1.15), 0.015, segs=6)
    V.add_box(bm, (-0.98, -0.04, 1.15), (0.98, 0.04, 1.23))
    V.add_box(bm, (-0.80, -0.03, 0.26), (0.80, 0.03, 0.33))
    objs.append(V.bm_to_object(bm, "perch", ("M_wood",)))
    objs.append(V.bm_to_object(bm_iron, "perch_iron", ("M_iron",)))
    rng = random.Random(7)
    for i, px in enumerate((-0.55, 0.0, 0.5)):
        for o in _lark("perch_lark%d" % i):
            o.location = (px, 0, 1.23)
            o.rotation_euler = (0, 0, rng.uniform(-0.6, 0.6))
            objs.append(o)
    return objs, {"size": [1.96, 0.40, 1.45], "origin": "bottom-center"}


def perch_rail_bare(seed=17):
    """The same rail in ruin: empty, leaning, one snapped chain swinging."""
    rng = random.Random(seed)
    objs = []
    bm = bmesh.new()
    bm_iron = bmesh.new()
    for px in (-0.8, 0.8):
        V.add_box(bm, (px - 0.08, -0.20, 0.0), (px + 0.08, 0.20, 0.07))
        V.add_box(bm, (px - 0.06, -0.14, 0.07), (px + 0.06, 0.14, 0.12))
        V.add_box(bm, (px - 0.05, -0.05, 0.12), (px + 0.05, 0.05, 1.15))
        V.add_box(bm, (px - 0.065, -0.065, 1.23), (px + 0.065, 0.065, 1.31))
        V.add_box(bm, (px - 0.04, -0.04, 1.31), (px + 0.04, 0.04, 1.38))
        V.add_box(bm_iron, (px - 0.058, -0.058, 0.14), (px + 0.058, 0.058, 0.20))
        V.add_box(bm_iron, (px - 0.058, -0.058, 1.08), (px + 0.058, 0.058, 1.15))
        sx = -1 if px > 0 else 1
        _add_rod(bm_iron, (px, 0.0, 0.90), (px + sx * 0.22, 0.0, 1.15), 0.015, segs=6)
    V.add_box(bm, (-0.98, -0.04, 1.15), (0.98, 0.04, 1.23))
    V.add_box(bm, (-0.80, -0.03, 0.26), (0.80, 0.03, 0.33))
    rail = V.bm_to_object(bm, "perch_b", ("M_wood",))
    rail.rotation_euler = (0, 0.06, 0)
    objs.append(rail)
    iron = V.bm_to_object(bm_iron, "perch_b_iron", ("M_iron",))
    iron.rotation_euler = (0, 0.06, 0)
    objs.append(iron)
    chain = V.loft_rings("perch_chain", [(0.02, 1.15, 6, 0), (0.016, 0.7, 6, 0)], "M_iron")
    chain.location = (rng.uniform(-0.4, 0.4), 0, 0)
    objs.append(chain)
    return objs, {"size": [1.96, 0.40, 1.45], "origin": "bottom-center"}


def great_perch():
    """The Larkwarden's roost: a tall gilded stand crowning the summit — stepped
    Gothic stone base with corner buttresses, iron-strapped pole, two finial-tipped
    crossbars with scroll braces, and a crowning sun-ring. Solid boss cover."""
    objs = []
    bm = bmesh.new()
    V.add_box(bm, (-0.92, -0.92, 0.0), (0.92, 0.92, 0.18))
    V.add_box(bm, (-0.72, -0.72, 0.18), (0.72, 0.72, 0.34))
    V.add_box(bm, (-0.52, -0.52, 0.34), (0.52, 0.52, 0.52))
    for sx, sy in ((-0.62, 0.0), (0.62, 0.0), (0.0, -0.62), (0.0, 0.62)):
        wx = 0.16 if sx != 0 else 0.11
        wy = 0.16 if sy != 0 else 0.11
        V.add_box(bm, (sx - wx, sy - wy, 0.18), (sx + wx, sy + wy, 0.50))
    objs.append(V.bm_to_object(bm, "roost_base", ("M_stone_dark",)))

    bm_trim = bmesh.new()
    V.add_box(bm_trim, (-0.95, -0.95, 0.15), (0.95, 0.95, 0.19))
    V.add_box(bm_trim, (-0.75, -0.75, 0.31), (0.75, 0.75, 0.35))
    V.add_box(bm_trim, (-0.56, -0.56, 0.48), (0.56, 0.56, 0.54))
    objs.append(V.bm_to_object(bm_trim, "roost_base_trim", ("M_stone_trim",)))

    pole = V.loft_rings(
        "roost_pole",
        [
            (0.18, 0.50, 14, 0),
            (0.14, 0.66, 14, 0),
            (0.12, 2.20, 14, 0),
            (0.105, 3.42, 14, 0),
        ],
        "M_wood",
    )
    objs.append(pole)
    gm = bmesh.new()
    for (w, z) in ((1.12, 2.20), (0.72, 3.00)):
        V.add_box(gm, (-w, -0.045, z), (w, 0.045, z + 0.085))
        for sx in (-1, 1):
            V.add_box(gm, (sx * w - 0.05, -0.06, z - 0.02), (sx * w + 0.05, 0.06, z + 0.14))
            V.add_box(gm, (sx * w - 0.03, -0.03, z + 0.14), (sx * w + 0.03, 0.03, z + 0.22))
            _add_rod(gm, (sx * 0.11, 0.0, z - 0.28), (sx * 0.42, 0.0, z + 0.02), 0.022, segs=6)
    for z_band in (0.68, 1.45, 2.22, 3.02):
        V.add_cyl(gm, 0.0, 0.0, z_band, 0.06, 0.135, n=14)
    # 8 radial sun-rays inside the crowning sun-ring + central apex spire
    for i in range(8):
        ang = math.tau * i / 8
        ca, sa = math.cos(ang), math.sin(ang)
        _add_rod(gm, (0.04 * ca, 0.0, 3.52 + 0.04 * sa), (0.28 * ca, 0.0, 3.52 + 0.28 * sa), 0.012, segs=6)
    _add_rod(gm, (0.0, 0.0, 3.62), (0.0, 0.0, 3.86), 0.022, segs=8)
    objs.append(V.bm_to_object(gm, "roost_bars", ("M_gold",)))
    # Closed 3D hollow sun-ring (outer + inner return wall)
    ring = V.loft_rings(
        "roost_ring",
        [
            (0.26, 3.38, 16, 0),
            (0.34, 3.40, 16, 0),
            (0.37, 3.52, 16, 0),
            (0.32, 3.64, 16, 0),
            (0.25, 3.62, 16, 0),
            (0.28, 3.52, 16, 0),
            (0.26, 3.38, 16, 0),
        ],
        "M_gold",
        cap_bottom=False,
        cap_top=False,
    )
    objs.append(ring)
    return objs, {"size": [2.2, 2.2, 3.86], "origin": "bottom-center"}


def aviary_screen():
    """4 m aviary lattice: moulded stone sill, wrought-iron frame with pointed
    Gothic top tracery arches, crossed timber slats, and gilded joint bosses."""
    objs = []
    # Moulded stone base sill
    bm_sill = bmesh.new()
    V.add_box(bm_sill, (-2.0, -0.09, 0.0), (2.0, 0.09, 0.14))
    objs.append(V.bm_to_object(bm_sill, "screen_sill", ("M_stone_trim",)))

    fm = bmesh.new()
    V.add_box(fm, (-2.0, -0.055, 0.14), (2.0, 0.055, 0.22))
    V.add_box(fm, (-2.0, -0.055, 3.88), (2.0, 0.055, 4.0))
    for px in (-1.95, 0.0, 1.95):
        w = 0.055 if px != 0.0 else 0.038
        V.add_box(fm, (px - w, -0.05, 0.14), (px + w, 0.05, 4.0))
    # Pointed Gothic arch ribs in the upper register (4 bays across the 4 m width)
    for bx in (-1.46, -0.49, 0.49, 1.46):
        pts = V.pointed_arch(0.86, 1.0, segments=6)
        for i in range(len(pts) - 1):
            (x0, z0), (x1, z1) = pts[i], pts[i + 1]
            _add_rod(fm, (bx + x0, 0.0, 3.02 + z0), (bx + x1, 0.0, 3.02 + z1), 0.018, segs=6)
    objs.append(V.bm_to_object(fm, "screen_frame", ("M_iron",)))

    sm = bmesh.new()
    x = -1.8
    while x < 1.9:
        if abs(x) > 0.05:
            V.add_box(sm, (x - 0.02, -0.022, 0.20), (x + 0.02, 0.022, 3.90))
        x += 0.36
    for z in (1.0, 2.0, 3.0):
        V.add_box(sm, (-1.96, -0.024, z - 0.024), (1.96, 0.024, z + 0.024))
    # Diagonal diamond lattice braces in the lower register (z = 0.20..1.00)
    for bx in (-1.44, -0.72, 0.0, 0.72, 1.44):
        _add_rod(sm, (bx - 0.34, 0.0, 0.22), (bx + 0.34, 0.0, 0.98), 0.015, segs=4)
        _add_rod(sm, (bx + 0.34, 0.0, 0.22), (bx - 0.34, 0.0, 0.98), 0.015, segs=4)
    objs.append(V.bm_to_object(sm, "screen_slats", ("M_wood",)))

    # Gilded joint bosses at transom intersections
    bm_gold = bmesh.new()
    for z in (1.0, 2.0, 3.0):
        for bx in (-1.44, -0.72, 0.0, 0.72, 1.44):
            V.add_box(bm_gold, (bx - 0.038, -0.034, z - 0.038), (bx + 0.038, 0.034, z + 0.038))
    objs.append(V.bm_to_object(bm_gold, "screen_bosses", ("M_gold",)))
    return objs, {"size": [4, 0.18, 4], "origin": "bottom-center"}


BUILDERS = {
    "lark_cage": lark_cage,
    "lark_cage_dead": lark_cage_dead,
    "cage_stand": cage_stand,
    "perch_rail": perch_rail,
    "perch_rail_bare": perch_rail_bare,
    "great_perch": great_perch,
    "aviary_screen": aviary_screen,
}
