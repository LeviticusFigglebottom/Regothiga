"""Backdrop & grandeur kit: the kingdom beyond the walls.

Skyline masses (spire towers, cathedral silhouettes, buttress arcs, city
clusters) are scenery-scale, no-collision, base-tagged — they exist in both
states and morph with the world. Terrace pieces (balustrade, grand stair,
urns, wellhead, sconces) are playable-scale.
"""
import math
import random
import bmesh
from mathutils import Vector

import vglib as V


def _box(bm, x0, y0, z0, x1, y1, z1):
    V.add_box(bm, (x0, y0, z0), (x1, y1, z1))


def _pinnacle(bm, cx, cy, base_z, w, h):
    """Corner pinnacle: small shaft + pyramid."""
    _box(bm, cx - w, cy - w, base_z, cx + w, cy + w, base_z + h * 0.55)
    a = bm.verts.new((cx - w * 1.2, cy - w * 1.2, base_z + h * 0.55))
    b = bm.verts.new((cx + w * 1.2, cy - w * 1.2, base_z + h * 0.55))
    c = bm.verts.new((cx + w * 1.2, cy + w * 1.2, base_z + h * 0.55))
    d = bm.verts.new((cx - w * 1.2, cy + w * 1.2, base_z + h * 0.55))
    tip = bm.verts.new((cx, cy, base_z + h))
    for e0, e1 in ((a, b), (b, c), (c, d), (d, a)):
        bm.faces.new((e0, e1, tip))
    bm.faces.new((d, c, b, a))


def _spire(bm, cx, cy, base_z, w, h, tip_w=0.02):
    a = bm.verts.new((cx - w, cy - w, base_z))
    b = bm.verts.new((cx + w, cy - w, base_z))
    c = bm.verts.new((cx + w, cy + w, base_z))
    d = bm.verts.new((cx - w, cy + w, base_z))
    tip = bm.verts.new((cx, cy, base_z + h))
    for e0, e1 in ((a, b), (b, c), (c, d), (d, a)):
        bm.faces.new((e0, e1, tip))


def _niche_face(bm, x0, x1, y, z0, z1, count, depth=0.35):
    """Row of dark lancet-ish inset panels on a wall face at y (facing -Y)."""
    w = (x1 - x0) / count
    for i in range(count):
        nx0 = x0 + i * w + w * 0.25
        nx1 = x0 + (i + 1) * w - w * 0.25
        _box(bm, nx0, y - depth * 0.5, z0, nx1, y + 0.01, z1)


def spire_tower(seed=1):
    """Skyline tower: tapering tiers, niches, corner pinnacles, steep spire.
    ~28-40 m tall. Origin bottom-center."""
    rng = random.Random(seed)
    bm = bmesh.new()
    nbm = bmesh.new()   # niche (dark) mesh
    w = rng.uniform(3.2, 4.6)
    z = 0.0
    tiers = rng.randint(2, 3)
    for t in range(tiers):
        h = rng.uniform(6.5, 9.5) * (1.0 - t * 0.14)
        _box(bm, -w, -w, z, w, w, z + h)
        # string course
        _box(bm, -w - 0.3, -w - 0.3, z + h, w + 0.3, w + 0.3, z + h + 0.5)
        for face in range(4):
            # niches on each face via rotated helper: bake onto ±X/±Y by symmetry
            pass
        _niche_face(nbm, -w * 0.8, w * 0.8, -w, z + h * 0.25, z + h * 0.82, 2 + t % 2)
        _niche_face(nbm, -w * 0.8, w * 0.8, w, z + h * 0.25, z + h * 0.82, 2 + t % 2)
        z += h + 0.5
        w *= rng.uniform(0.8, 0.88)
    # crown pinnacles + spire
    for sx in (-1, 1):
        for sy in (-1, 1):
            _pinnacle(bm, sx * w * 0.95, sy * w * 0.95, z, w * 0.16, rng.uniform(2.6, 3.6))
    _spire(bm, 0, 0, z, w * 0.78, rng.uniform(8.0, 13.0))
    body = V.bm_to_object(bm, "tower_body", ("M_backdrop",))
    niches = V.bm_to_object(nbm, "tower_niches", ("M_backdrop_dark",))
    return [body, niches], {"size": [w * 2, w * 2, z + 12], "origin": "bottom-center"}


def cathedral_mass(seed=5):
    """Skyline cathedral: long clerestory nave, twin west towers, rose disc,
    buttress fins, crossing fleche. ~55 m long. Origin: west front center."""
    rng = random.Random(seed)
    objs = []
    bm = bmesh.new()
    nave_l, nave_w, nave_h = 46.0, 9.0, 16.0
    aisle_h = 9.5
    # nave + aisles
    _box(bm, -nave_w / 2, 0, 0, nave_w / 2, nave_l, nave_h)
    _box(bm, -nave_w / 2 - 4, 0, 0, nave_w / 2 + 4, nave_l, aisle_h)
    # gable roof on nave
    for y0 in (0.0,):
        a = bm.verts.new((-nave_w / 2, 0, nave_h))
        b = bm.verts.new((nave_w / 2, 0, nave_h))
        c = bm.verts.new((nave_w / 2, nave_l, nave_h))
        d = bm.verts.new((-nave_w / 2, nave_l, nave_h))
        r1 = bm.verts.new((0, 0, nave_h + 3.4))
        r2 = bm.verts.new((0, nave_l, nave_h + 3.4))
        bm.faces.new((a, b, r1))
        bm.faces.new((c, d, r2))
        bm.faces.new((a, r1, r2, d))
        bm.faces.new((b, c, r2, r1))
    # buttress fins along the aisles
    for i in range(6):
        y = 6 + i * 6.5
        for sx in (-1, 1):
            x0 = sx * (nave_w / 2 + 4)
            _box(bm, x0 - 0.5 * sx if sx > 0 else x0, y - 0.5, 0, x0 + 0.5 if sx > 0 else x0 + 0.5 * -sx, y + 0.5, aisle_h + 3.5)
    # west towers
    for sx in (-1, 1):
        tx = sx * (nave_w / 2 + 6.5)
        _box(bm, tx - 3.4, -3.0, 0, tx + 3.4, 3.8, 22.0)
        _spire(bm, tx, 0.4, 22.0, 3.0, 10.0)
    # crossing fleche
    _spire(bm, 0, nave_l * 0.62, nave_h + 3.4, 2.0, 9.0)
    body = V.bm_to_object(bm, "cathedral_body", ("M_backdrop",))
    objs.append(body)
    # west front rose + portal insets (dark)
    nbm = bmesh.new()
    rose = 3.2
    n = 12
    prev = None
    ring0 = []
    for i in range(n):
        a = 2 * math.pi * i / n
        ring0.append(nbm.verts.new((math.cos(a) * rose, -0.3, nave_h * 0.62 + math.sin(a) * rose)))
    nbm.faces.new(ring0)
    _box(nbm, -2.2, -0.3, 0, 2.2, 0.05, 6.5)
    front = V.bm_to_object(nbm, "cathedral_dark", ("M_backdrop_dark",))
    objs.append(front)
    return objs, {"size": [30, nave_l, 36], "origin": "west-front"}


def buttress_arc():
    """Flying arc between skyline masses — the Anor-Londo bridge silhouette.
    Spans 22 m, rises 6. Origin at midpoint base."""
    pts = []
    n = 16
    for i in range(n + 1):
        t = i / n
        x = (t - 0.5) * 22.0
        z = 10.0 - 4.0 * (2 * t - 1) ** 2   # parabola
        pts.append((x, 0, z))
    prof = V.chamfer_rect_profile(1.0, 1.6, 0.2)
    arc = V.sweep_profile("arc", pts, prof, "M_backdrop", up_hint=Vector((0, 0, 1)))
    return [arc], {"size": [22, 2, 12], "origin": "mid-base"}


def city_cluster(seed=9):
    """Mid-ground roofscape: gabled masses on a platform. ~18x18 m."""
    rng = random.Random(seed)
    bm = bmesh.new()
    _box(bm, -9, -9, 0, 9, 9, 1.2)
    for i in range(rng.randint(6, 9)):
        w = rng.uniform(1.8, 3.4)
        d = rng.uniform(2.2, 4.4)
        h = rng.uniform(3.0, 7.0)
        cx = rng.uniform(-7, 7)
        cy = rng.uniform(-7, 7)
        _box(bm, cx - w, cy - d, 1.2, cx + w, cy + d, 1.2 + h)
        a = bm.verts.new((cx - w, cy - d, 1.2 + h))
        b = bm.verts.new((cx + w, cy - d, 1.2 + h))
        c = bm.verts.new((cx + w, cy + d, 1.2 + h))
        dd = bm.verts.new((cx - w, cy + d, 1.2 + h))
        r1 = bm.verts.new((cx, cy - d, 1.2 + h + w * 0.8))
        r2 = bm.verts.new((cx, cy + d, 1.2 + h + w * 0.8))
        bm.faces.new((a, b, r1))
        bm.faces.new((c, dd, r2))
        bm.faces.new((a, r1, r2, dd))
        bm.faces.new((b, c, r2, r1))
        if rng.random() < 0.4:
            _spire(bm, cx, cy, 1.2 + h + w * 0.8, 0.5, rng.uniform(2, 4))
    obj = V.bm_to_object(bm, "city", ("M_backdrop",))
    return [obj], {"size": [18, 18, 10], "origin": "bottom-center"}


# ---------------------------------------------------------------- terrace

def balustrade_4m():
    """Stone balustrade: rail, plinth, turned balusters. Origin bottom-center."""
    objs = []
    bm = bmesh.new()
    _box(bm, -2, -0.14, 0, 2, 0.14, 0.14)
    _box(bm, -2, -0.16, 0.92, 2, 0.16, 1.1)
    for px in (-2.0, 2.0):
        _box(bm, px - 0.14, -0.18, 0, px + 0.14, 0.18, 1.1)
    frame = V.bm_to_object(bm, "balustrade_frame", ("M_stone_trim",))
    objs.append(frame)
    x = -1.7
    while x < 1.9:
        b = V.loft_rings("baluster", [(0.09, 0.14, 8, 0), (0.055, 0.3, 8, 0), (0.1, 0.52, 8, 0),
                                      (0.05, 0.74, 8, 0), (0.09, 0.92, 8, 0)], "M_stone_trim")
        b.location = (x, 0, 0)
        objs.append(b)
        x += 0.34
    return objs, {"size": [4, 0.4, 1.1], "origin": "bottom-center"}


def stair_grand_4m():
    """Grand stair: 4 m wide run descending 2.4 m over 4 m, solid flanks.
    Origin: top edge center (walk off the upper floor onto it)."""
    bm = bmesh.new()
    steps = 10
    for i in range(steps):
        z0 = -2.4 * (i + 1) / steps
        y0 = 0.4 * i
        _box(bm, -2, y0, z0, 2, y0 + 0.42, z0 + 2.4 / steps + 0.02)
    # flanks
    _box(bm, -2.35, 0, -2.4, -2.0, 4.0, 0.35)
    _box(bm, 2.0, 0, -2.4, 2.35, 4.0, 0.35)
    obj = V.bm_to_object(bm, "stair", ("M_stone",))
    return [obj], {"size": [4.7, 4, 2.8], "origin": "top-center"}


def urn():
    u = V.loft_rings("urn", [(0.16, 0, 10, 0), (0.13, 0.05, 10, 0), (0.3, 0.34, 10, 0),
                             (0.34, 0.6, 10, 0), (0.2, 0.86, 10, 0), (0.26, 0.95, 10, 0)], "M_stone_trim")
    return [u], {"size": [0.7, 0.7, 1.0], "origin": "bottom-center"}


def wellhead():
    """Octagonal garth well with posts and a little roof."""
    objs = []
    objs.append(V.loft_rings("well_wall", [(1.05, 0, 8, 0), (1.05, 0.85, 8, 0), (0.85, 0.85, 8, 0),
                                           (0.85, 0.0, 8, 0)], "M_stone", cap_bottom=False, cap_top=False))
    for sx in (-0.95, 0.95):
        p = V.loft_rings("post", [(0.07, 0.8, 6, 0), (0.06, 2.1, 6, 0)], "M_wood")
        p.location = (sx, 0, 0)
        objs.append(p)
    bm = bmesh.new()
    a = bm.verts.new((-1.3, -0.7, 2.05)); b = bm.verts.new((1.3, -0.7, 2.05))
    c = bm.verts.new((1.3, 0.7, 2.05)); d = bm.verts.new((-1.3, 0.7, 2.05))
    r1 = bm.verts.new((-1.3, 0, 2.5)); r2 = bm.verts.new((1.3, 0, 2.5))
    bm.faces.new((a, b, r2, r1)); bm.faces.new((r1, r2, c, d))
    bm.faces.new((a, r1, d)); bm.faces.new((b, c, r2))
    objs.append(V.bm_to_object(bm, "well_roof", ("M_roof",)))
    return objs, {"size": [2.6, 1.5, 2.5], "origin": "bottom-center"}


def sconce_torch():
    """Wall sconce: bracket + candle + flame. Mount against wall (-Y face)."""
    objs = []
    arm = V.sweep_profile("bracket", [(0, 0.0, 0), (0, -0.22, 0.05), (0, -0.3, 0.12)],
                          V.circle_profile(0.02, 6), "M_iron")
    objs.append(arm)
    cup = V.loft_rings("cup", [(0.06, 0.1, 8, 0), (0.07, 0.16, 8, 0)], "M_iron")
    cup.location = (0, -0.3, 0)
    objs.append(cup)
    c = V.loft_rings("candle", [(0.045, 0.16, 8, 0), (0.04, 0.34, 8, 0)], "M_wax")
    c.location = (0, -0.3, 0)
    objs.append(c)
    f = V.loft_rings("sconce_flame", [(0.02, 0.0, 6, 0), (0.035, 0.05, 6, 0.3), (0.003, 0.13, 6, 0.6)], "M_flame")
    f.location = (0, -0.3, 0.35)
    objs.append(f)
    return objs, {"size": [0.2, 0.4, 0.5], "origin": "wall-mount"}


def statue_orans(seed=3):
    """Saint with arms raised in prayer — variation for garden/terrace."""
    import kit_props
    objs = []
    bm = bmesh.new()
    _box(bm, -0.42, -0.42, 0, 0.42, 0.42, 0.55)
    _box(bm, -0.5, -0.5, 0, 0.5, 0.5, 0.12)
    objs.append(V.bm_to_object(bm, "plinth", ("M_stone_dark",)))
    robe = kit_props._robe("saint_o", 1.9, 0.34, True, "M_stone")
    robe.location = (0, 0, 0.55)
    objs.append(robe)
    for sx in (-1, 1):
        arm = V.sweep_profile("arm", [(sx * 0.28, 0, 1.75), (sx * 0.44, 0.05, 2.05), (sx * 0.5, 0.08, 2.3)],
                              V.circle_profile(0.07, 6), "M_stone")
        objs.append(arm)
    return objs, {"size": [1, 1, 2.9], "origin": "bottom-center"}


BUILDERS = {
    "spire_tower_a": lambda: spire_tower(11),
    "spire_tower_b": lambda: spire_tower(23),
    "spire_tower_c": lambda: spire_tower(37),
    "cathedral_mass": lambda: cathedral_mass(5),
    "buttress_arc": buttress_arc,
    "city_cluster_a": lambda: city_cluster(9),
    "city_cluster_b": lambda: city_cluster(14),
    "balustrade_4m": balustrade_4m,
    "stair_grand_4m": stair_grand_4m,
    "urn": urn,
    "wellhead": wellhead,
    "sconce_torch": sconce_torch,
    "statue_orans": statue_orans,
}
