"""Prop kit generators: the vigil lantern, lights, furniture, iron work,
statues, gargoyles, the great bell. Origins at floor contact, real scale."""
import math
import random
import bmesh
from mathutils import Vector, Matrix

import vglib as V
from kit_arch import bmesh_to_mesh


def _flame(name="flame", r=0.035, h=0.14):
    """Stylized teardrop flame; M_flame is emissive + flickers in-shader."""
    n = 6
    rings = [(r * 0.4, 0.0, n, 0), (r, h * 0.28, n, 0.2), (r * 0.55, h * 0.62, n, 0.4),
             (r * 0.18, h * 0.86, n, 0.6), (0.004, h, n, 0.8)]
    return V.loft_rings(name, rings, "M_flame")


def _candle(h=0.22, r=0.035, lit=True):
    objs = []
    n = 8
    drip = V.loft_rings("candle", [(r * 1.25, 0, n, 0), (r * 1.1, 0.02, n, 0.3),
                                   (r, 0.05, n, 0), (r, h - 0.01, n, 0), (r * 0.8, h, n, 0)],
                        "M_wax")
    objs.append(drip)
    if lit:
        f = _flame()
        f.location = (0, 0, h + 0.01)
        objs.append(f)
    return objs


def vigil_lantern():
    """THE rest site. Stone socle, wrought twisted post, caged lantern with a
    votive flame, kneeling step. Flame mesh named 'vigil_flame' so the state
    system can retint it (gold in glory, blue in ruin)."""
    objs = []
    # socle: two octagonal steps
    objs.append(V.loft_rings("socle", [(0.62, 0, 8, 0), (0.62, 0.14, 8, 0),
                                       (0.46, 0.14, 8, 0), (0.46, 0.3, 8, 0),
                                       (0.3, 0.3, 8, 0), (0.3, 0.42, 8, 0)],
                             "M_stone_dark", cap_top=True))
    # twisted iron post: square rings rotating with height
    rings = []
    for i in range(13):
        z = 0.42 + i * 0.10
        rings.append((0.052, z, 4, i * 0.42))
    rings.append((0.14, 1.72, 4, 13 * 0.42))       # flare under the cage
    objs.append(V.loft_rings("post", rings, "M_iron"))
    # cage: 4 corner ribs + roof pyramid + finial ring
    cage_r, cage_h0, cage_h1 = 0.24, 1.78, 2.3
    for k in range(4):
        a = k * math.pi / 2 + math.pi / 4
        p0 = (cage_r * math.cos(a), cage_r * math.sin(a), cage_h0)
        p1 = (cage_r * math.cos(a), cage_r * math.sin(a), cage_h1)
        objs.append(V.sweep_profile("cage_rib", [p0, p1], V.circle_profile(0.016, 5),
                                    "M_iron", up_hint=Vector((math.cos(a + 1.57), math.sin(a + 1.57), 0))))
    objs.append(V.loft_rings("cage_base", [(0.30, cage_h0 - 0.05, 8, 0), (0.24, cage_h0, 8, 0)], "M_iron"))
    objs.append(V.loft_rings("cage_roof", [(0.31, cage_h1, 8, 0), (0.02, cage_h1 + 0.26, 8, 0.4)], "M_iron"))
    # finial: the Vespergard sigil — a half-sunk sun disc over a bar
    objs.append(V.loft_rings("finial_disc", [(0.005, cage_h1 + 0.26, 8, 0), (0.07, cage_h1 + 0.34, 8, 0),
                                             (0.005, cage_h1 + 0.42, 8, 0)], "M_gold"))
    # votive flame inside the cage
    f = _flame("vigil_flame", 0.075, 0.3)
    f.location = (0, 0, cage_h0 + 0.02)
    objs.append(f)
    # candle stub under it
    stub = V.loft_rings("stub", [(0.09, cage_h0 - 0.04, 8, 0), (0.08, cage_h0 + 0.02, 8, 0)], "M_wax")
    objs.append(stub)
    # kneel step
    bm = bmesh.new()
    V.add_box(bm, (-0.4, 0.55, 0), (0.4, 1.05, 0.09))
    objs.append(V.bm_to_object(bm, "kneel_step", ("M_stone_dark",)))
    return objs, {"size": [1.3, 2.1, 2.8], "origin": "bottom-center"}


def candelabra():
    """Standing candelabra, three lit candles. Glory furniture."""
    objs = []
    objs.append(V.loft_rings("stand", [(0.22, 0, 8, 0), (0.2, 0.03, 8, 0), (0.05, 0.06, 8, 0),
                                       (0.028, 1.16, 8, 0), (0.06, 1.2, 8, 0)], "M_iron"))
    for (dx, h) in ((-0.18, 1.18), (0.0, 1.3), (0.18, 1.18)):
        if dx != 0.0:
            arm = V.sweep_profile("arm", [(0, 0, 1.14), (dx * 0.6, 0, 1.1 + abs(dx) * 0.1), (dx, 0, h - 0.06)],
                                  V.circle_profile(0.014, 5), "M_iron")
            objs.append(arm)
        cup = V.loft_rings("cup", [(0.05, h - 0.02, 8, 0), (0.055, h, 8, 0)], "M_iron")
        objs.append(cup)
        for c in _candle(0.16):
            c.location = (dx, 0, h)
            objs.append(c)
    return objs, {"size": [0.5, 0.5, 1.6], "origin": "bottom-center"}


def brazier(lit=True):
    name = "brazier_lit" if lit else "brazier_cold"
    objs = []
    objs.append(V.loft_rings("bowl", [(0.12, 0.52, 10, 0), (0.34, 0.62, 10, 0),
                                      (0.38, 0.78, 10, 0), (0.30, 0.84, 10, 0)], "M_iron"))
    for k in range(3):
        a = k * 2 * math.pi / 3
        leg = V.sweep_profile("leg", [(0.26 * math.cos(a), 0.26 * math.sin(a), 0),
                                      (0.16 * math.cos(a), 0.16 * math.sin(a), 0.56)],
                              V.circle_profile(0.02, 5), "M_iron")
        objs.append(leg)
    if lit:
        f = _flame("brazier_flame", 0.16, 0.34)
        f.location = (0, 0, 0.74)
        objs.append(f)
    else:
        ash = V.loft_rings("ash", [(0.26, 0.72, 10, 0), (0.1, 0.78, 10, 0)], "M_stone_dark")
        objs.append(ash)
    return objs, {"size": [0.8, 0.8, 1.1], "origin": "bottom-center"}


def _robe(name, height=1.8, girth=0.34, hood=True, mat="M_stone"):
    """The shared robed-figure silhouette (statues, and the base of every
    character archetype). Returns a single object."""
    n = 10
    h = height
    rings = [
        (girth * 1.25, 0.0, n, 0),          # hem spread
        (girth * 1.12, h * 0.06, n, 0),
        (girth * 0.86, h * 0.36, n, 0),
        (girth * 0.78, h * 0.52, n, 0),     # waist
        (girth * 0.95, h * 0.68, n, 0),     # chest
        (girth * 0.88, h * 0.78, n, 0),     # shoulders
    ]
    if hood:
        rings += [
            (girth * 0.52, h * 0.84, n, 0),   # neck cinch
            (girth * 0.62, h * 0.90, n, 0),   # hood bulge
            (girth * 0.40, h * 0.985, n, 0),  # hood crown
            (girth * 0.10, h * 1.06, n, 0),   # hood peak, slightly forward
        ]
    obj = V.loft_rings(name, rings, mat)
    if hood:
        # lean the hood peak forward
        me = obj.data
        zs = sorted({round(v.co.z, 4) for v in me.vertices})
        top = zs[-2:]
        for v in me.vertices:
            if round(v.co.z, 4) in top:
                v.co.y += 0.09
        # carve the face shadow: push front-upper verts inward
        for v in me.vertices:
            if v.co.z > h * 0.86 and v.co.y > 0:
                v.co.y *= 0.4
    return obj


def statue_saint():
    """Hooded saint with a downward sword, on a plinth. Kit reuse: the robe
    silhouette is the character family silhouette in stone."""
    objs = []
    bm = bmesh.new()
    V.add_box(bm, (-0.42, -0.42, 0), (0.42, 0.42, 0.55))
    V.add_box(bm, (-0.5, -0.5, 0), (0.5, 0.5, 0.12))
    objs.append(V.bm_to_object(bm, "plinth", ("M_stone_dark",)))
    robe = _robe("saint", 1.9, 0.34, True, "M_stone")
    robe.location = (0, 0, 0.55)
    objs.append(robe)
    # sword held point-down before the figure
    bm2 = bmesh.new()
    V.add_box(bm2, (-0.035, -0.012, 0.62), (0.035, 0.012, 1.55))    # blade
    V.add_box(bm2, (-0.16, -0.03, 1.52), (0.16, 0.03, 1.60))        # cross
    V.add_box(bm2, (-0.03, -0.03, 1.60), (0.03, 0.03, 1.78))        # grip
    sw = V.bm_to_object(bm2, "saint_sword", ("M_stone_trim",))
    sw.location = (0, 0.34, 0)
    objs.append(sw)
    return objs, {"size": [1, 1, 2.6], "origin": "bottom-center"}


def gargoyle():
    """Perched grotesque: hunched body, folded wings, horned skull — chunky
    silhouette for cornice lines and the bell tower."""
    objs = []
    bm = bmesh.new()
    # haunches + body: overlapping deformed spheres
    for (c, r, sq) in (((0, -0.05, 0.22), 0.20, 0.8), ((0, 0.16, 0.30), 0.16, 0.9),
                       ((0, 0.32, 0.38), 0.13, 1.0)):
        got = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
        for v in got["verts"]:
            v.co.z *= sq
            v.co += Vector(c)
    body = V.bm_to_object(bm, "gargoyle_body", ("M_stone",))
    objs.append(body)
    # head: box skull + muzzle + horns
    bm2 = bmesh.new()
    V.add_box(bm2, (-0.09, 0.36, 0.42), (0.09, 0.56, 0.56))
    V.add_box(bm2, (-0.05, 0.52, 0.42), (0.05, 0.64, 0.50))
    head = V.bm_to_object(bm2, "gargoyle_head", ("M_stone",))
    objs.append(head)
    for sx in (-1, 1):
        horn = V.sweep_profile("horn", [(sx * 0.07, 0.42, 0.56), (sx * 0.13, 0.36, 0.66), (sx * 0.15, 0.28, 0.72)],
                               V.circle_profile(0.025, 5), "M_stone")
        objs.append(horn)
        # folded wing: bent plane
        bmw = bmesh.new()
        a = bmw.verts.new((sx * 0.16, 0.10, 0.42))
        b = bmw.verts.new((sx * 0.34, -0.16, 0.60))
        c = bmw.verts.new((sx * 0.30, -0.34, 0.24))
        d = bmw.verts.new((sx * 0.14, -0.18, 0.16))
        bmw.faces.new((a, b, c, d) if sx > 0 else (d, c, b, a))
        # thickness
        res = bmesh.ops.solidify(bmw, geom=list(bmw.faces), thickness=0.03)
        wing = V.bm_to_object(bmw, "wing", ("M_stone",))
        objs.append(wing)
    # forelegs
    for sx in (-1, 1):
        leg = V.sweep_profile("leg", [(sx * 0.12, 0.30, 0.30), (sx * 0.15, 0.42, 0.12), (sx * 0.15, 0.46, 0.02)],
                              V.circle_profile(0.035, 5), "M_stone")
        objs.append(leg)
    return objs, {"size": [0.7, 1.0, 0.8], "origin": "bottom-center"}


def banner():
    """Hanging cloth banner with the setting-sun sigil zone. Glory-only."""
    bm = bmesh.new()
    w, h = 0.85, 2.3
    nx, nz = 6, 14
    grid = {}
    for i in range(nx + 1):
        for j in range(nz + 1):
            x = -w / 2 + w * i / nx
            z = -h * j / nz
            y = 0.05 * math.sin(j * 0.8) * (j / nz)
            grid[(i, j)] = bm.verts.new((x, y, z))
    for i in range(nx):
        for j in range(nz):
            bm.faces.new((grid[(i, j)], grid[(i + 1, j)], grid[(i + 1, j + 1)], grid[(i, j + 1)]))
    # swallowtail cut at the bottom
    obj = V.bm_to_object(bm, "banner_cloth", ("M_cloth",))
    obj.location = (0, 0, 2.5)
    # rod + finials
    rod = V.sweep_profile("rod", [(-w / 2 - 0.12, 0, 2.52), (w / 2 + 0.12, 0, 2.52)],
                          V.circle_profile(0.02, 6), "M_iron")
    # sun-disc appliqué
    disc = V.loft_rings("sigil", [(0.005, 1.55, 10, 0), (0.16, 1.62, 10, 0), (0.005, 1.69, 10, 0)], "M_gold")
    disc.location = (0, -0.06, 0)
    disc.rotation_euler = (math.pi / 2, 0, 0)
    return [obj, rod, disc], {"size": [1.1, 0.3, 2.6], "origin": "top-center"}


def pew():
    bm = bmesh.new()
    V.add_box(bm, (-0.9, -0.22, 0.0), (0.9, 0.22, 0.06))
    V.add_box(bm, (-0.9, -0.20, 0.40), (0.9, 0.02, 0.46))     # seat
    V.add_box(bm, (-0.9, 0.16, 0.40), (0.9, 0.24, 1.02))      # back
    V.add_box(bm, (-0.9, -0.20, 0.06), (-0.82, 0.22, 0.42))
    V.add_box(bm, (0.82, -0.20, 0.06), (0.9, 0.22, 0.42))
    obj = V.bm_to_object(bm, "pew", ("M_wood",))
    return [obj], {"size": [1.8, 0.5, 1.05], "origin": "bottom-center"}


def altar():
    objs = []
    bm = bmesh.new()
    V.add_box(bm, (-1.0, -0.5, 0), (1.0, 0.5, 0.92))
    V.add_box(bm, (-1.08, -0.58, 0.92), (1.08, 0.58, 1.02))
    V.add_box(bm, (-1.06, -0.56, 0), (1.06, 0.56, 0.1))
    objs.append(V.bm_to_object(bm, "altar_body", ("M_stone_trim",)))
    for c in _candle(0.26):
        c.location = (-0.7, 0, 1.02)
        objs.append(c)
    for c in _candle(0.2):
        c.location = (0.7, 0.1, 1.02)
        objs.append(c)
    return objs, {"size": [2.2, 1.2, 1.35], "origin": "bottom-center"}


def plaque():
    """Lore plaque: lectern stand with an engraved slab face."""
    bm = bmesh.new()
    V.add_box(bm, (-0.28, -0.16, 0), (0.28, 0.16, 0.85))
    obj = V.bm_to_object(bm, "plaque_post", ("M_stone_dark",))
    bm2 = bmesh.new()
    vs = [(-0.34, -0.02, 0.82), (0.34, -0.02, 0.82), (0.34, 0.3, 1.18), (-0.34, 0.3, 1.18)]
    vv = [bm2.verts.new(v) for v in vs]
    bm2.faces.new(vv)
    bmesh.ops.solidify(bm2, geom=list(bm2.faces), thickness=0.05)
    slab = V.bm_to_object(bm2, "plaque_slab", ("M_stone_trim",))
    return [obj, slab], {"size": [0.7, 0.6, 1.2], "origin": "bottom-center"}


def tomb_slab():
    bm = bmesh.new()
    V.add_box(bm, (-0.55, -1.1, 0), (0.55, 1.1, 0.42))
    V.add_box(bm, (-0.6, -1.15, 0.42), (0.6, 1.15, 0.52))
    obj = V.bm_to_object(bm, "tomb", ("M_stone_dark",))
    robe = _robe("effigy", 1.9, 0.3, True, "M_stone_trim")
    robe.scale = (1, 1, 0.28)
    robe.rotation_euler = (-math.pi / 2, 0, math.pi)
    robe.location = (0, 0.85, 0.62)
    return [obj, robe], {"size": [1.2, 2.3, 0.75], "origin": "bottom-center"}


def gate_iron():
    """Two-leaf wrought gate for a 2.4 m opening. Named leaves let the game
    swing them. Spiked, with a lock plate."""
    objs = []
    for leaf, sgn in (("gate_leaf_l", -1), ("gate_leaf_r", 1)):
        bm = bmesh.new()
        x0, x1 = (0.02, 1.18) if sgn > 0 else (-1.18, -0.02)
        # frame
        for x in (x0, x1):
            V.add_box(bm, (x - 0.022, -0.022, 0.02), (x + 0.022, 0.022, 2.2))
        for z in (0.09, 1.05, 2.05):
            V.add_box(bm, (x0, -0.018, z - 0.028), (x1, 0.018, z + 0.028))
        # bars + spike tips
        x = x0 + 0.12
        while x < x1 - 0.05:
            V.add_box(bm, (x - 0.014, -0.014, 0.04), (x + 0.014, 0.014, 2.3))
            x += 0.155
        obj = V.bm_to_object(bm, leaf, ("M_iron",))
        objs.append(obj)
    return objs, {"size": [2.4, 0.1, 2.35], "origin": "bottom-center"}


def fence_iron_4m():
    bm = bmesh.new()
    V.add_box(bm, (-2, -0.03, 0.0), (2, 0.03, 0.08))
    for z in (0.75, 1.7):
        V.add_box(bm, (-2, -0.02, z - 0.03), (2, 0.02, z + 0.03))
    x = -1.9
    while x < 1.95:
        V.add_box(bm, (x - 0.015, -0.015, 0.08), (x + 0.015, 0.015, 1.95))
        x += 0.17
    for px in (-2, 2):
        V.add_box(bm, (px - 0.045, -0.045, 0), (px + 0.045, 0.045, 2.1))
    obj = V.bm_to_object(bm, "fence_iron_4m", ("M_iron",))
    return [obj], {"size": [4, 0.1, 2.1], "origin": "bottom-center"}


def bell_great():
    """The Bellkeeper's cracked great bell — also the tower bell. ~1.6 m tall."""
    n = 12
    rings = [(0.10, 1.62, n, 0), (0.16, 1.55, n, 0), (0.30, 1.45, n, 0),
             (0.44, 1.2, n, 0), (0.52, 0.9, n, 0), (0.56, 0.55, n, 0),
             (0.62, 0.28, n, 0), (0.72, 0.10, n, 0), (0.74, 0.0, n, 0),
             (0.70, 0.02, n, 0), (0.55, 0.24, n, 0)]  # rolled lip + inner return
    bell = V.loft_rings("bell_great", rings, "M_bell", cap_bottom=False, cap_top=True)
    crown = V.loft_rings("crown", [(0.05, 1.6, 6, 0), (0.08, 1.74, 6, 0), (0.03, 1.82, 6, 0)], "M_bell")
    return [bell, crown], {"size": [1.5, 1.5, 1.85], "origin": "bottom-center"}


BUILDERS = {
    "vigil_lantern": vigil_lantern,
    "candelabra": candelabra,
    "brazier_lit": lambda: brazier(True),
    "brazier_cold": lambda: brazier(False),
    "statue_saint": statue_saint,
    "gargoyle": gargoyle,
    "banner": banner,
    "pew": pew,
    "altar": altar,
    "plaque": plaque,
    "tomb_slab": tomb_slab,
    "gate_iron": gate_iron,
    "fence_iron_4m": fence_iron_4m,
    "bell_great": bell_great,
}
