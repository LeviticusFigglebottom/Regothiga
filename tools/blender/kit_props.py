"""Prop kit generators: the vigil lantern, lights, furniture, iron work,
statues, gargoyles, the great bell. Origins at floor contact, real scale."""
import math
import random
import bmesh
from mathutils import Vector, Matrix

import vglib as V
from kit_arch import bmesh_to_mesh


def _flame(name="flame", r=0.020, h=0.11, z0=0.0):
    """Stylized slender teardrop flame; M_flame is emissive + flickers in-shader."""
    n = 10
    rings = [
        (r * 0.32, z0, n, 0),
        (r * 0.92, z0 + h * 0.22, n, 0.15),
        (r * 0.68, z0 + h * 0.50, n, 0.30),
        (r * 0.32, z0 + h * 0.78, n, 0.45),
        (0.002, z0 + h, n, 0.60),
    ]
    return V.loft_rings(name, rings, "M_flame")


def _candle(h=0.22, r=0.035, lit=True):
    objs = []
    n = 12
    # Melted wax column with recessed concave wax cup at top
    drip = V.loft_rings(
        "candle",
        [
            (r * 1.25, 0, n, 0),
            (r * 1.10, 0.02, n, 0.3),
            (r, 0.05, n, 0),
            (r * 0.96, h - 0.008, n, 0),
            (r * 0.88, h, n, 0),
            (r * 0.45, h - 0.012, n, 0),
        ],
        "M_wax",
    )
    objs.append(drip)
    wick = V.loft_rings("wick", [(0.0035, h - 0.012, 6, 0), (0.0025, h + 0.014, 6, 0)], "M_iron")
    objs.append(wick)
    if lit:
        f = _flame(z0=h + 0.006)
        objs.append(f)
    return objs


def vigil_lantern():
    """THE rest site. Ornate stepped octagonal stone socle, wrought twisted post
    with brass collars, caged lantern with filigree bands and a votive flame,
    and carved kneeling step. Flame mesh named 'vigil_flame'."""
    objs = []
    # socle: stepped octagonal pedestal with cornice moulding
    objs.append(V.loft_rings("socle", [(0.64, 0, 12, 0), (0.64, 0.12, 12, 0),
                                       (0.58, 0.15, 12, 0), (0.48, 0.15, 12, 0),
                                       (0.48, 0.28, 12, 0), (0.42, 0.31, 12, 0),
                                       (0.32, 0.31, 12, 0), (0.32, 0.42, 12, 0)],
                             "M_stone_dark", cap_top=True))
    # Gilt brass base collar
    objs.append(V.loft_rings("post_collar_low", [(0.14, 0.42, 14, 0), (0.11, 0.48, 14, 0),
                                                 (0.07, 0.52, 14, 0)], "M_gold"))
    # twisted iron post: 12-sided fluted iron rings rotating with height
    rings = []
    for i in range(13):
        z = 0.42 + i * 0.10
        r_mod = 0.056 + (0.014 if i == 6 else 0.0)
        rings.append((r_mod, z, 12, i * 0.42))
    rings.append((0.15, 1.72, 12, 13 * 0.42))       # flare under the cage
    objs.append(V.loft_rings("post", rings, "M_iron"))
    # Mid-shaft gilt ring
    objs.append(V.loft_rings("post_collar_mid", [(0.082, 1.00, 14, 0), (0.095, 1.03, 14, 0),
                                                 (0.082, 1.06, 14, 0)], "M_gold"))
    # cage: 8 corner ribs + roof pyramid + finial ring
    cage_r, cage_h0, cage_h1 = 0.24, 1.78, 2.30
    for k in range(8):
        a = k * math.pi / 4 + math.pi / 8
        rad = 0.016 if k % 2 == 0 else 0.010
        p0 = (cage_r * math.cos(a), cage_r * math.sin(a), cage_h0)
        p1 = (cage_r * math.cos(a), cage_r * math.sin(a), cage_h1)
        objs.append(V.sweep_profile("cage_rib", [p0, p1], V.circle_profile(rad, 8),
                                    "M_iron", up_hint=Vector((math.cos(a + 1.57), math.sin(a + 1.57), 0))))
    objs.append(V.loft_rings("cage_base", [(0.31, cage_h0 - 0.05, 16, 0), (0.25, cage_h0, 16, 0)], "M_iron"))
    objs.append(V.loft_rings("cage_roof", [(0.32, cage_h1, 16, 0), (0.18, cage_h1 + 0.14, 16, 0.2),
                                           (0.02, cage_h1 + 0.28, 16, 0.4)], "M_iron"))
    # finial: the Vespergard sigil — an eclipsed sun ring & spire in burnished gold
    objs.append(V.loft_rings("finial_disc", [(0.01, cage_h1 + 0.26, 16, 0), (0.085, cage_h1 + 0.35, 16, 0),
                                             (0.01, cage_h1 + 0.44, 16, 0)], "M_gold"))
    # votive flame inside the cage
    f = _flame("vigil_flame", 0.072, 0.30)
    f.location = (0, 0, cage_h0 + 0.02)
    objs.append(f)
    # candle stub under it
    stub = V.loft_rings("stub", [(0.095, cage_h0 - 0.04, 14, 0), (0.085, cage_h0 + 0.02, 14, 0)], "M_wax")
    objs.append(stub)
    # Clustered melted votive candles around the stepped stone socle (shrine offerings)
    for ang, rad_c, hc in ((0.4, 0.38, 0.16), (1.1, 0.41, 0.12), (2.3, 0.37, 0.18),
                           (3.6, 0.40, 0.14), (4.8, 0.39, 0.15), (5.5, 0.42, 0.11)):
        for c in _candle(hc, 0.030, lit=False):
            c.location = (rad_c * math.cos(ang), rad_c * math.sin(ang), 0.31)
            objs.append(c)
    # kneel step with bevelled coping
    bm = bmesh.new()
    V.add_box(bm, (-0.42, 0.54, 0), (0.42, 1.06, 0.08))
    V.add_box(bm, (-0.38, 0.58, 0.08), (0.38, 1.02, 0.11))
    objs.append(V.bm_to_object(bm, "kneel_step", ("M_stone_dark",)))
    return objs, {"size": [1.3, 2.1, 2.8], "origin": "bottom-center"}


def candelabra():
    """Standing cathedral candelabra, three lit candles with scrolled ironwork & gilt cups."""
    objs = []
    objs.append(V.loft_rings("stand", [(0.24, 0, 16, 0), (0.21, 0.04, 16, 0), (0.07, 0.09, 16, 0),
                                       (0.032, 0.58, 16, 0), (0.055, 0.62, 16, 0), (0.030, 0.66, 16, 0),
                                       (0.028, 1.15, 16, 0), (0.065, 1.2, 16, 0)], "M_iron"))
    for (dx, h) in ((-0.19, 1.18), (0.0, 1.31), (0.19, 1.18)):
        if dx != 0.0:
            arm = V.sweep_profile("arm", [(0, 0, 1.12), (dx * 0.55, 0, 1.08 + abs(dx) * 0.12), (dx, 0, h - 0.05)],
                                  V.circle_profile(0.015, 10), "M_iron")
            objs.append(arm)
        cup = V.loft_rings("cup", [(0.025, h - 0.04, 14, 0), (0.062, h - 0.01, 14, 0), (0.058, h + 0.01, 14, 0)], "M_gold")
        cup.location = (dx, 0, 0)
        objs.append(cup)
        for c in _candle(0.17):
            c.location = (dx, 0, h)
            objs.append(c)
    return objs, {"size": [0.5, 0.5, 1.6], "origin": "bottom-center"}


def brazier(lit=True):
    objs = []
    objs.append(V.loft_rings("bowl", [(0.10, 0.48, 20, 0), (0.16, 0.54, 20, 0), (0.35, 0.63, 20, 0),
                                      (0.40, 0.78, 20, 0), (0.43, 0.81, 20, 0), (0.32, 0.85, 20, 0)], "M_iron"))
    objs.append(V.loft_rings("bowl_rim", [(0.40, 0.78, 20, 0), (0.435, 0.815, 20, 0), (0.39, 0.84, 20, 0)], "M_gold"))
    for k in range(3):
        a = k * 2 * math.pi / 3
        leg = V.sweep_profile("leg", [(0.28 * math.cos(a), 0.28 * math.sin(a), 0),
                                      (0.22 * math.cos(a), 0.22 * math.sin(a), 0.28),
                                      (0.16 * math.cos(a), 0.16 * math.sin(a), 0.56)],
                              V.circle_profile(0.024, 10), "M_iron")
        objs.append(leg)
    if lit:
        embers = V.loft_rings("brazier_embers", [(0.34, 0.58, 18, 0), (0.33, 0.66, 18, 0),
                                                 (0.26, 0.76, 18, 0), (0.14, 0.85, 18, 0),
                                                 (0.04, 0.9, 18, 0)], "M_ember")
        objs.append(embers)
        for k in range(3):
            a = k * 2.094 + 0.4
            ff = _flame("brazier_flame%d" % k, 0.055, 0.22)
            ff.location = (0.1 * math.cos(a), 0.1 * math.sin(a), 0.88)
            objs.append(ff)
    else:
        ash = V.loft_rings("ash", [(0.26, 0.72, 18, 0), (0.1, 0.78, 18, 0)], "M_stone_dark")
        objs.append(ash)
    return objs, {"size": [0.8, 0.8, 1.1], "origin": "bottom-center"}


def _robe(name, height=1.8, girth=0.34, hood=True, mat="M_stone"):
    """The shared robed-figure silhouette (statues, and the base of every
    character archetype). Returns a single object."""
    n = 16
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
            (girth * 0.62, h * 0.84, n, 0),   # neck / collar
            (girth * 0.64, h * 0.90, n, 0),   # hood bulge
            (girth * 0.46, h * 0.985, n, 0),  # hood crown
            (girth * 0.14, h * 1.05, n, 0),   # hood peak, slightly forward
        ]
    obj = V.loft_rings(name, rings, mat)
    if hood:
        me = obj.data
        for v in me.vertices:
            if v.co.z > h * 0.82:
                ht = max(0.0, min(1.0, (v.co.z - h * 0.82) / (h * 0.23)))
                v.co.y += 0.045 * (ht * ht)
        me.update()
    return obj


def statue_saint():
    """Hooded saint with a downward sword, on a plinth."""
    objs = []
    bm = bmesh.new()
    V.add_box(bm, (-0.42, -0.42, 0), (0.42, 0.42, 0.55))
    V.add_box(bm, (-0.5, -0.5, 0), (0.5, 0.5, 0.12))
    objs.append(V.bm_to_object(bm, "plinth", ("M_stone_dark",)))
    robe = _robe("saint", 1.9, 0.34, True, "M_stone")
    robe.location = (0, 0, 0.55)
    objs.append(robe)
    bm2 = bmesh.new()
    V.add_box(bm2, (-0.035, -0.012, 0.62), (0.035, 0.012, 1.55))    # blade
    V.add_box(bm2, (-0.16, -0.03, 1.52), (0.16, 0.03, 1.60))        # cross
    V.add_box(bm2, (-0.03, -0.03, 1.60), (0.03, 0.03, 1.78))        # grip
    sw = V.bm_to_object(bm2, "saint_sword", ("M_stone_trim",))
    sw.location = (0, 0.34, 0)
    objs.append(sw)
    return objs, {"size": [1, 1, 2.6], "origin": "bottom-center"}


def gargoyle():
    """Perched grotesque: hunched body, folded wings, horned skull."""
    objs = []
    bm = bmesh.new()
    for (c, r, sq) in (((0, -0.05, 0.22), 0.20, 0.8), ((0, 0.16, 0.30), 0.16, 0.9),
                       ((0, 0.32, 0.38), 0.13, 1.0)):
        got = bmesh.ops.create_icosphere(bm, subdivisions=2, radius=r)
        for v in got["verts"]:
            v.co.z *= sq
            v.co += Vector(c)
    body = V.bm_to_object(bm, "gargoyle_body", ("M_stone",))
    objs.append(body)
    bm2 = bmesh.new()
    V.add_box(bm2, (-0.09, 0.36, 0.42), (0.09, 0.56, 0.56))
    V.add_box(bm2, (-0.05, 0.52, 0.42), (0.05, 0.64, 0.50))
    head = V.bm_to_object(bm2, "gargoyle_head", ("M_stone",))
    objs.append(head)
    for sx in (-1, 1):
        horn = V.sweep_profile("horn", [(sx * 0.07, 0.42, 0.56), (sx * 0.13, 0.36, 0.66), (sx * 0.15, 0.28, 0.72)],
                               V.circle_profile(0.025, 8), "M_stone")
        objs.append(horn)
        bmw = bmesh.new()
        a = bmw.verts.new((sx * 0.16, 0.10, 0.42))
        b = bmw.verts.new((sx * 0.34, -0.16, 0.60))
        c = bmw.verts.new((sx * 0.30, -0.34, 0.24))
        d = bmw.verts.new((sx * 0.14, -0.18, 0.16))
        bmw.faces.new((a, b, c, d) if sx > 0 else (d, c, b, a))
        bmesh.ops.solidify(bmw, geom=list(bmw.faces), thickness=0.03)
        wing = V.bm_to_object(bmw, "wing", ("M_stone",))
        objs.append(wing)
    for sx in (-1, 1):
        leg = V.sweep_profile("leg", [(sx * 0.12, 0.30, 0.30), (sx * 0.15, 0.42, 0.12), (sx * 0.15, 0.46, 0.02)],
                              V.circle_profile(0.035, 8), "M_stone")
        objs.append(leg)
    return objs, {"size": [0.7, 1.0, 0.8], "origin": "bottom-center"}


def banner():
    """Hanging cloth banner with the setting-sun sigil zone. Glory-only."""
    bm = bmesh.new()
    w, h = 0.85, 2.3
    nx, nz = 8, 16
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
    bmesh.ops.solidify(bm, geom=list(bm.faces) + list(bm.verts) + list(bm.edges), thickness=0.012)
    obj = V.bm_to_object(bm, "banner_cloth", ("M_cloth",))
    obj.location = (0, 0, 2.5)
    rod = V.sweep_profile("rod", [(-w / 2 - 0.12, 0, 2.52), (w / 2 + 0.12, 0, 2.52)],
                          V.circle_profile(0.02, 10), "M_iron")
    disc = V.loft_rings("sigil", [(0.005, -0.015, 14, 0), (0.16, 0.0, 14, 0), (0.005, 0.015, 14, 0)], "M_gold")
    disc.location = (0, -0.025, 1.62)
    disc.rotation_euler = (math.pi / 2, 0, 0)
    return [obj, rod, disc], {"size": [1.1, 0.3, 2.6], "origin": "top-center"}


def pew():
    bm = bmesh.new()
    V.add_box(bm, (-0.9, -0.22, 0.0), (0.9, 0.22, 0.06))
    V.add_box(bm, (-0.9, -0.20, 0.40), (0.9, 0.02, 0.46))     # seat
    V.add_box(bm, (-0.9, 0.16, 0.40), (0.9, 0.24, 1.02))      # back
    V.add_box(bm, (-0.9, -0.20, 0.06), (-0.82, 0.22, 0.42))
    V.add_box(bm, (0.82, -0.20, 0.06), (0.9, 0.22, 0.42))
    V.add_box(bm, (-0.93, -0.24, 0.42), (-0.79, 0.26, 0.52))
    V.add_box(bm, (0.79, -0.24, 0.42), (0.93, 0.26, 0.52))
    V.add_box(bm, (-0.92, 0.14, 1.02), (0.92, 0.26, 1.08))
    V.add_box(bm, (-0.86, -0.34, 0.10), (0.86, -0.26, 0.16))
    obj = V.bm_to_object(bm, "pew", ("M_wood",))
    return [obj], {"size": [1.86, 0.62, 1.1], "origin": "bottom-center"}


def altar():
    objs = []
    bm = bmesh.new()
    V.add_box(bm, (-1.0, -0.5, 0), (1.0, 0.5, 0.92))
    V.add_box(bm, (-1.08, -0.58, 0.92), (1.08, 0.58, 1.02))
    V.add_box(bm, (-1.06, -0.56, 0), (1.06, 0.56, 0.1))
    objs.append(V.bm_to_object(bm, "altar_body", ("M_stone_trim",)))
    gm = bmesh.new()
    V.add_box(gm, (-1.085, -0.585, 0.89), (1.085, 0.585, 0.925))
    objs.append(V.bm_to_object(gm, "altar_gilt", ("M_gold",)))
    for c in _candle(0.26):
        c.location = (-0.7, 0, 1.02)
        objs.append(c)
    for c in _candle(0.2):
        c.location = (0.7, 0.1, 1.02)
        objs.append(c)
    return objs, {"size": [2.2, 1.2, 1.35], "origin": "bottom-center"}


def plaque():
    """Lore plaque: carved Gothic octagonal stone lectern with stepped moulded plinth,
    fluted shaft, wrought-iron scroll brackets, angled limestone desk, and inset bronze tablet."""
    objs = []
    # Stepped octagonal plinth & fluted column shaft + flared capital
    pedestal = V.loft_rings(
        "plaque_post",
        [
            (0.32, 0.00, 8, math.pi / 8),
            (0.32, 0.08, 8, math.pi / 8),
            (0.25, 0.12, 8, math.pi / 8),
            (0.25, 0.18, 8, math.pi / 8),
            (0.16, 0.22, 8, math.pi / 8),
            (0.14, 0.72, 8, math.pi / 8),
            (0.22, 0.80, 8, math.pi / 8),
            (0.28, 0.88, 8, math.pi / 8),
        ],
        "M_stone_dark",
        cap_bottom=True,
        cap_top=True,
    )
    objs.append(pedestal)
    # Wrought-iron gothic corbel brackets under the reading desk
    for sx in (-0.18, 0.18):
        brk = V.sweep_profile(
            "plaque_bracket",
            [(sx, -0.02, 0.58), (sx, -0.14, 0.72), (sx, -0.18, 0.88), (sx, 0.14, 0.92)],
            V.chamfer_rect_profile(0.018, 0.024, 0.004),
            "M_iron",
            up_hint=Vector((1, 0, 0)),
        )
        objs.append(brk)
    # Angled carved limestone desk with raised side bolsters
    bm2 = bmesh.new()
    lean = Matrix.Translation((0, 0.06, 0.98)) @ Matrix.Rotation(math.radians(32), 4, "X")
    V.add_box(bm2, (-0.34, -0.24, -0.035), (0.34, 0.24, 0.025))
    # Raised stone border frame & bottom book-stop lip
    V.add_box(bm2, (-0.36, -0.26, -0.02), (-0.30, 0.26, 0.055))
    V.add_box(bm2, (0.30, -0.26, -0.02), (0.36, 0.26, 0.055))
    V.add_box(bm2, (-0.36, -0.26, -0.02), (0.36, -0.20, 0.065))
    V.add_box(bm2, (-0.36, 0.20, -0.02), (0.36, 0.26, 0.050))
    bmesh.ops.transform(bm2, matrix=lean, verts=bm2.verts)
    slab = V.bm_to_object(bm2, "plaque_slab", ("M_stone_trim",))
    objs.append(slab)
    # Inset engraved bronze inscription plate + brass corner bosses
    bm3 = bmesh.new()
    V.add_box(bm3, (-0.27, -0.17, 0.022), (0.27, 0.17, 0.040))
    for cx in (-0.23, 0.23):
        for cy in (-0.13, 0.13):
            V.add_box(bm3, (cx - 0.022, cy - 0.022, 0.038), (cx + 0.022, cy + 0.022, 0.052))
    bmesh.ops.transform(bm3, matrix=lean, verts=bm3.verts)
    plate = V.bm_to_object(bm3, "plaque_bronze", ("M_bronze",))
    objs.append(plate)
    return objs, {"size": [0.74, 0.6, 1.2], "origin": "bottom-center"}


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
    """Two-leaf wrought gate for a 2.4 m opening."""
    objs = []
    for leaf, sgn in (("gate_leaf_l", -1), ("gate_leaf_r", 1)):
        bm = bmesh.new()
        x0, x1 = (0.02, 1.18) if sgn > 0 else (-1.18, -0.02)
        for x in (x0, x1):
            V.add_box(bm, (x - 0.022, -0.022, 0.02), (x + 0.022, 0.022, 2.2))
        for z in (0.09, 1.05, 2.05):
            V.add_box(bm, (x0, -0.018, z - 0.028), (x1, 0.018, z + 0.028))
        x = x0 + 0.12
        while x < x1 - 0.05:
            V.add_box(bm, (x - 0.014, -0.014, 0.04), (x + 0.014, 0.014, 2.3))
            x += 0.155
        obj = V.bm_to_object(bm, leaf, ("M_iron",))
        objs.append(obj)
    return objs, {"size": [2.4, 0.1, 2.35], "origin": "bottom-center"}


def canal_vault(win: bool):
    """One 8 m segment of the great canal vault over the Drowned Marches."""
    R, CY, L, SEG = 20.0, 2.0, 8.0, 18
    prof = [(-20.0, -3.2), (-20.0, CY)]
    for i in range(1, SEG):
        a = math.pi * i / SEG
        prof.append((-R * math.cos(a), CY + R * math.sin(a)))
    prof += [(20.0, CY), (20.0, -3.2)]
    xs = (-4.0, -2.0, 2.0, 4.0)
    bm = bmesh.new()
    grid = [[bm.verts.new((x, py, pz)) for (py, pz) in prof] for x in xs]
    for c in range(len(xs) - 1):
        mid_col = c == 1
        for i in range(len(prof) - 1):
            (y0, z0), (y1, z1) = prof[i], prof[i + 1]
            zm = (z0 + z1) * 0.5
            flank = abs((y0 + y1) * 0.5) > 17.0
            if win and mid_col and flank and 3.2 <= zm <= 6.8:
                continue
            a, b = grid[c][i], grid[c][i + 1]
            d, e = grid[c + 1][i], grid[c + 1][i + 1]
            bm.faces.new((a, b, e, d))
    objs = [V.bm_to_object(bm, "canal_vault", ("M_stone_dark",))]
    if win:
        bb = bmesh.new()
        for sgn in (-1, 1):
            for k in range(7):
                bx = -1.8 + 0.6 * k
                V.add_box(bb, (bx - 0.04, sgn * 19.05 - 0.04, 2.0),
                          (bx + 0.04, sgn * 19.05 + 0.04, 6.9))
            V.add_box(bb, (-2.1, sgn * 19.0 - 0.05, 1.85), (2.1, sgn * 19.0 + 0.05, 2.15))
            V.add_box(bb, (-2.1, sgn * 19.0 - 0.05, 4.35), (2.1, sgn * 19.0 + 0.05, 4.6))
            V.add_box(bb, (-2.1, sgn * 19.0 - 0.05, 6.8), (2.1, sgn * 19.0 + 0.05, 7.1))
        objs.append(V.bm_to_object(bb, "vault_bars", ("M_iron",)))
        rv = bmesh.new()
        for sgn in (-1, 1):
            lo, hi = min(sgn * 18.9, sgn * 20.2), max(sgn * 18.9, sgn * 20.2)
            V.add_box(rv, (-2.15, lo, 1.85), (2.15, hi, 2.2))
            V.add_box(rv, (-2.15, lo, 6.3), (2.15, hi, 6.75))
            V.add_box(rv, (-2.15, lo, 1.85), (-1.85, hi, 6.75))
            V.add_box(rv, (1.85, lo, 1.85), (2.15, hi, 6.75))
        objs.append(V.bm_to_object(rv, "vault_reveal", ("M_stone_dark",)))
    return objs, {"size": [8, 40, 25.2], "origin": "bottom-center"}


def ferry_boat():
    """A working mini ferry for the waterworks passage."""
    objs = []
    bm = bmesh.new()
    V.add_box(bm, (-2.1, -0.85, 0.08), (1.7, 0.85, 0.34))
    V.add_box(bm, (-2.1, -0.85, 0.34), (-1.95, 0.85, 0.82))
    V.add_box(bm, (-2.1, -0.85, 0.34), (1.7, -0.7, 0.78))
    V.add_box(bm, (-2.1, 0.7, 0.34), (1.7, 0.85, 0.78))
    V.add_box(bm, (1.7, -0.62, 0.12), (2.15, 0.62, 0.74))
    V.add_box(bm, (2.15, -0.34, 0.18), (2.52, 0.34, 0.68))
    objs.append(V.bm_to_object(bm, "ferry_hull", ("M_wood",)))
    bm = bmesh.new()
    x = -1.92
    while x < 1.6:
        V.add_box(bm, (x, -0.68, 0.34), (x + 0.31, 0.68, 0.40))
        x += 0.36
    V.add_box(bm, (1.7, -0.5, 0.32), (2.12, 0.5, 0.40))
    objs.append(V.bm_to_object(bm, "ferry_deck", ("M_wood",)))
    bm = bmesh.new()
    for py in (-0.72, 0.72):
        V.add_box(bm, (-1.99, py - 0.05, 0.78), (-1.89, py + 0.05, 1.44))
    V.add_box(bm, (-1.98, -0.74, 1.32), (-1.9, 0.74, 1.42))
    V.add_box(bm, (1.82, -0.05, 0.68), (1.92, 0.05, 1.5))
    V.add_box(bm, (1.74, -0.13, 1.5), (2.0, 0.13, 1.58))
    V.add_box(bm, (1.72, -0.15, 1.86), (2.02, 0.15, 1.94))
    for py in (-0.11, 0.11):
        V.add_box(bm, (1.75, py - 0.015, 1.58), (1.78, py + 0.015, 1.86))
        V.add_box(bm, (1.96, py - 0.015, 1.58), (1.99, py + 0.015, 1.86))
    objs.append(V.bm_to_object(bm, "ferry_iron", ("M_iron",)))
    bm = bmesh.new()
    V.add_box(bm, (1.79, -0.08, 1.6), (1.95, 0.08, 1.82))
    objs.append(V.bm_to_object(bm, "ferry_flame", ("M_ember",)))
    bm = bmesh.new()
    V.add_box(bm, (-2.78, 0.30, 0.30), (-2.05, 0.42, 0.44))
    V.add_box(bm, (-2.1, 0.30, 0.44), (-1.5, 0.38, 0.92))
    objs.append(V.bm_to_object(bm, "ferry_sweep", ("M_wood",)))
    return objs, {"size": [5.3, 1.7, 1.94], "origin": "bottom-center"}


def anvil():
    """Reliquary smith's anvil: iron-hooped 12-sided oak stump bearing a
    forged London-pattern steel anvil with conical bick (horn), stepped
    cutting table, cantilevered heel, and a blacksmith's cross-peen hammer."""
    objs = []
    # 12-sided gnarled oak anvil block
    stump = V.loft_rings(
        "stump",
        [
            (0.28, 0.00, 12, 0),
            (0.25, 0.08, 12, 0),
            (0.24, 0.36, 12, 0),
            (0.25, 0.44, 12, 0),
        ],
        "M_wood",
        cap_bottom=True,
        cap_top=True,
    )
    objs.append(stump)

    # Wrought-iron hoops & hold-down staples on the oak stump + hammer head
    bm_iron = bmesh.new()
    for sx in (-0.16, 0.16):
        V.add_box(bm_iron, (sx - 0.02, -0.18, 0.38), (sx + 0.02, 0.18, 0.48))
    # Cross-peen blacksmith hammer head resting atop the anvil face
    V.add_box(bm_iron, (-0.01, -0.055, 0.72), (0.06, 0.055, 0.77))
    objs.append(V.bm_to_object(bm_iron, "anvil_hoops", ("M_iron",)))
    for z_h, r_h in ((0.08, 0.258), (0.35, 0.248)):
        objs.append(V.loft_rings("stump_hoop", [(r_h, z_h, 12, 0), (r_h, z_h + 0.035, 12, 0)],
                                 "M_iron", cap_bottom=False, cap_top=False))

    # Forged steel anvil body: splayed base feet, waisted core, step table, flat face, and cantilevered heel
    bm_steel = bmesh.new()
    V.add_box(bm_steel, (-0.21, -0.17, 0.44), (0.21, 0.17, 0.50))   # splayed foot
    V.add_box(bm_steel, (-0.14, -0.11, 0.50), (0.15, 0.11, 0.59))   # waisted neck
    V.add_box(bm_steel, (-0.19, -0.135, 0.59), (0.31, 0.135, 0.72)) # upper face + heel (+X)
    V.add_box(bm_steel, (-0.25, -0.115, 0.58), (-0.18, 0.115, 0.69)) # cutting step (-X)
    objs.append(V.bm_to_object(bm_steel, "anvil_iron", ("M_steel",)))

    # Tapered conical bick (horn) projecting toward -X
    horn = V.loft_rings(
        "anvil_horn",
        [
            (0.085, 0.00, 12, 0),
            (0.068, 0.09, 12, 0),
            (0.042, 0.18, 12, 0),
            (0.012, 0.25, 12, 0),
        ],
        "M_steel",
        cap_bottom=False,
        cap_top=True,
    )
    horn.rotation_euler = (0, -math.pi / 2, 0)
    horn.location = (-0.24, 0.0, 0.645)
    objs.append(horn)

    # Ash hammer handle resting diagonally across the anvil face
    bm_haft = bmesh.new()
    V.add_box(bm_haft, (0.01, -0.22, 0.73), (0.04, 0.08, 0.755))
    objs.append(V.bm_to_object(bm_haft, "hammer_haft", ("M_wood",)))
    return objs, {"size": [0.8, 0.5, 0.77], "origin": "bottom-center"}


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
    n = 18
    rings = [(0.02, 1.61, n, 0), (0.10, 1.62, n, 0), (0.16, 1.55, n, 0), (0.30, 1.45, n, 0),
             (0.44, 1.2, n, 0), (0.52, 0.9, n, 0), (0.56, 0.55, n, 0),
             (0.62, 0.28, n, 0), (0.72, 0.10, n, 0), (0.74, 0.0, n, 0),
             (0.68, 0.03, n, 0), (0.55, 0.24, n, 0), (0.49, 0.55, n, 0),
             (0.42, 0.9, n, 0), (0.32, 1.15, n, 0), (0.13, 1.38, n, 0),
             (0.02, 1.40, n, 0)]
    bell = V.loft_rings("bell_great", rings, "M_bell", cap_bottom=True, cap_top=True)
    clapper = V.loft_rings("clapper", [(0.035, 1.38, 12, 0), (0.05, 0.42, 12, 0),
                                       (0.115, 0.30, 12, 0), (0.12, 0.12, 12, 0),
                                       (0.03, 0.05, 12, 0)], "M_iron",
                           cap_bottom=True, cap_top=True)
    crown = V.loft_rings("crown", [(0.05, 1.6, 10, 0), (0.08, 1.74, 10, 0), (0.03, 1.82, 10, 0)], "M_bell")
    return [bell, clapper, crown], {"size": [1.5, 1.5, 1.85], "origin": "bottom-center"}


def organ_case():
    """Basilica organ: carved Gothic oak wainscot case with manual keyboard console,
    pedalboard, side tower pilasters, gilt pipe-shade fretwork, and 15 graduated
    bronze & steel flue pipes in a double-tower cathedral array."""
    objs = []
    bm = bmesh.new()
    # Main wainscot lower case + stepped plinth
    V.add_box(bm, (-1.34, -0.38, 0.0), (1.34, 0.46, 0.12))
    V.add_box(bm, (-1.30, -0.34, 0.12), (1.30, 0.44, 1.15))
    # Recessed front panel stiles (5 gothic bays across the lower case)
    for sx in (-1.28, -0.64, 0.0, 0.64, 1.28):
        V.add_box(bm, (sx - 0.05, -0.38, 0.12), (sx + 0.05, 0.45, 1.15))
    # Protruding manual keyboard desk + bench/pedalboard frame on -Y (front)
    V.add_box(bm, (-0.58, -0.58, 0.76), (0.58, -0.32, 0.94))
    V.add_box(bm, (-0.54, -0.56, 0.0), (-0.44, -0.34, 0.76))
    V.add_box(bm, (0.44, -0.56, 0.0), (0.54, -0.34, 0.76))
    # Upper pipe-chest cornice & outer wooden pipe-tower pilasters
    V.add_box(bm, (-1.38, -0.38, 1.12), (1.38, 0.48, 1.28))
    for sx in (-1.32, -0.78, 0.78, 1.32):
        V.add_box(bm, (sx - 0.05, -0.34, 1.28), (sx + 0.05, 0.20, 3.65))
    V.add_box(bm, (-1.40, -0.38, 3.60), (-0.72, 0.24, 3.78))
    V.add_box(bm, (0.72, -0.38, 3.60), (1.40, 0.24, 3.78))
    objs.append(V.bm_to_object(bm, "organ_case", ("M_wood",)))

    # Bone manual keys + gilt pipe-shade fretwork bands
    bm_keys = bmesh.new()
    V.add_box(bm_keys, (-0.48, -0.56, 0.84), (0.48, -0.36, 0.89))
    V.add_box(bm_keys, (-0.46, -0.50, 0.90), (0.46, -0.36, 0.95))
    objs.append(V.bm_to_object(bm_keys, "organ_keys", ("M_bone",)))

    bm_gild = bmesh.new()
    V.add_box(bm_gild, (-1.39, -0.39, 1.24), (1.39, 0.49, 1.30))
    V.add_box(bm_gild, (-1.30, -0.34, 3.45), (-0.80, -0.26, 3.60))
    V.add_box(bm_gild, (0.80, -0.34, 3.45), (1.30, -0.26, 3.60))
    V.add_box(bm_gild, (-0.76, -0.30, 2.75), (0.76, -0.22, 2.90))
    objs.append(V.bm_to_object(bm_gild, "organ_gild", ("M_gold",)))

    # 15 graduated bronze & steel flue pipes with conical feet and labium mouths
    n = 15
    for i in range(n):
        t = i / (n - 1.0)
        x = -1.18 + 2.36 * t
        in_tower = abs(x) > 0.78
        if in_tower:
            h = 2.15 + 0.35 * (1.0 - abs((abs(x) - 1.05) / 0.20))
            r = 0.068
            y_off = -0.14
        else:
            # Central V-mitre flat + rising center spire
            u = abs(x) / 0.75
            h = 1.45 + 1.35 * (1.0 - u) ** 1.15
            r = 0.048 + 0.018 * (1.0 - u)
            y_off = -0.06
        mat = "M_bronze" if i % 3 != 1 else "M_steel"
        pipe = V.loft_rings(
            "pipe%d" % i,
            [
                (r * 0.35, 1.26, 12, 0),
                (r * 1.02, 1.46, 12, 0),
                (r * 0.92, 1.50, 12, 0),
                (r, 1.54, 12, 0),
                (r, 1.26 + h, 12, 0),
                (r * 0.82, 1.32 + h, 12, 0),
            ],
            mat,
        )
        pipe.location = (x, y_off, 0)
        objs.append(pipe)
    return objs, {"size": [2.8, 1.05, 4.3], "origin": "bottom-center"}


def choir_stall():
    """High-backed choir stall bench, faces -Y like the pews."""
    objs = []
    bm = bmesh.new()
    V.add_box(bm, (-1.15, -0.24, 0.42), (1.15, 0.12, 0.5))
    V.add_box(bm, (-1.15, 0.12, 0.0), (1.15, 0.3, 1.55))
    V.add_box(bm, (-1.15, 0.24, 1.55), (1.15, 0.38, 1.72))
    V.add_box(bm, (-1.15, -0.3, 0.0), (-1.02, 0.12, 0.86))
    V.add_box(bm, (1.02, -0.3, 0.0), (1.15, 0.12, 0.86))
    V.add_box(bm, (-1.15, -0.26, 0.16), (1.15, -0.18, 0.2))
    objs.append(V.bm_to_object(bm, "choir_stall", ("M_wood",)))
    return objs, {"size": [2.4, 0.7, 1.75], "origin": "bottom-center"}


def chime_stone():
    """Vesper chime: a standing stone gallows with a hanging bronze bar."""
    objs = []
    post = V.loft_rings("chime_post", [(0.17, 0, 12, 0), (0.13, 0.2, 12, 0),
                                       (0.11, 1.9, 12, 0), (0.15, 2.05, 12, 0)], "M_stone_trim")
    objs.append(post)
    bm = bmesh.new()
    V.add_box(bm, (-0.05, -0.62, 1.98), (0.05, 0.1, 2.08))
    objs.append(V.bm_to_object(bm, "chime_arm", ("M_wood",)))
    bm = bmesh.new()
    V.add_box(bm, (-0.035, -0.55, 1.06), (0.035, -0.47, 1.96))
    objs.append(V.bm_to_object(bm, "chime_bar", ("M_bronze",)))
    bm = bmesh.new()
    V.add_box(bm, (-0.02, -0.53, 0.98), (0.02, -0.49, 1.06))
    objs.append(V.bm_to_object(bm, "chime_clapper", ("M_iron",)))
    return objs, {"size": [0.5, 1.3, 2.1], "origin": "bottom-center"}


def votive_stand_tall(lit=True):
    """Tall iron votive stand with a wax crown; lit variant carries flames."""
    objs = []
    objs.append(V.loft_rings("votive_col", [(0.2, 0, 12, 0), (0.06, 0.12, 12, 0),
                                            (0.05, 1.16, 12, 0), (0.17, 1.24, 12, 0),
                                            (0.19, 1.3, 12, 0)], "M_iron"))
    import random as _random
    rng = _random.Random(9 if lit else 10)
    for i in range(5):
        a = 2 * math.pi * i / 5
        r = 0.11
        h = 0.14 + 0.1 * rng.random()
        c = V.loft_rings("cand%d" % i, [(0.035, 1.3, 10, 0), (0.033, 1.3 + h, 10, 0)], "M_wax")
        c.location = (r * math.cos(a), r * math.sin(a), 0)
        objs.append(c)
        if lit:
            f = _flame("votive_flame%d" % i, 0.024, 0.085)
            f.location = (r * math.cos(a), r * math.sin(a), 1.33 + h)
            objs.append(f)
    return objs, {"size": [0.5, 0.5, 1.6], "origin": "bottom-center"}


def bell_fragment():
    """A broken arc of the Bellkeeper's bell."""
    import bmesh as _bmesh
    from mathutils import Matrix as _M
    R = 0.34
    lean = _M.Rotation(math.radians(11), 3, "X")

    def _arc_boxes(bm, half_w, half_t, z0, z1, y_off):
        for i, ang in enumerate((-26, 0, 26)):
            a = math.radians(ang)
            rot = _M.Rotation(a, 3, "Z")
            cx = R * math.sin(a)
            cy = -R * (1 - math.cos(a)) + y_off
            top = z1 + (0.06 if i == 1 else 0.0)
            corners = []
            for sx in (-half_w, half_w):
                for sy in (-half_t, half_t):
                    for sz in (z0, top):
                        v = rot @ Vector((sx, sy, sz))
                        corners.append((v.x + cx, v.y + cy, v.z))
            vs = [bm.verts.new(lean @ Vector(c)) for c in corners]
            bm.verts.ensure_lookup_table()
            faces = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 2, 6, 4),
                     (1, 5, 7, 3), (0, 4, 5, 1), (2, 3, 7, 6)]
            for f in faces:
                bm.faces.new([vs[k] for k in f])

    objs = []
    bm = _bmesh.new()
    _arc_boxes(bm, 0.085, 0.025, 0.0, 0.46, 0.0)
    objs.append(V.bm_to_object(bm, "frag_wall", ("M_bronze",)))
    bm = _bmesh.new()
    _arc_boxes(bm, 0.095, 0.045, 0.0, 0.085, -0.012)
    objs.append(V.bm_to_object(bm, "frag_lip", ("M_iron",)))
    return objs, {"size": [0.6, 0.45, 0.55], "origin": "bottom-center"}


def mosaic_medallion():
    """Flat inlaid mosaic roundel, 3.4 m across."""
    disc = V.loft_rings("mosaic_disc", [(1.7, 0.0, 28, 0), (1.7, 0.012, 28, 0)], "M_mosaic")
    rim = V.loft_rings("mosaic_rim", [(1.78, 0.0, 28, 0), (1.78, 0.016, 28, 0),
                                      (1.7, 0.016, 28, 0), (1.7, 0.0, 28, 0)], "M_stone_trim",
                       cap_bottom=False, cap_top=False)
    return [disc, rim], {"size": [3.6, 3.6, 0.02], "origin": "bottom-center"}


def ossuary_wall_4m():
    """Crypt wall: stone frame with two shelf bands of stacked skulls."""
    import random as _random
    rng = _random.Random(5)
    objs = []
    bm = bmesh.new()
    V.add_box(bm, (-2, -0.2, 0), (2, 0.2, 4.0))
    objs.append(V.bm_to_object(bm, "oss_frame", ("M_stone",)))
    bm = bmesh.new()
    for band_z in (0.9, 2.1):
        V.add_box(bm, (-1.9, -0.26, band_z - 0.45), (1.9, -0.14, band_z + 0.45))
    objs.append(V.bm_to_object(bm, "oss_shelf", ("M_stone_dark",)))
    bm = bmesh.new()
    for band_z in (0.9, 2.1):
        n = 11
        for i in range(n):
            x = -1.75 + 3.5 * i / (n - 1) + (rng.random() - 0.5) * 0.06
            z = band_z + (rng.random() - 0.5) * 0.08
            got = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=0.14 + rng.random() * 0.03)
            for v in got["verts"]:
                v.co = Vector((v.co.x * 0.9 + x, v.co.y * 0.75 - 0.3, v.co.z * 0.8 + z))
    objs.append(V.bm_to_object(bm, "oss_skulls", ("M_bone",)))
    return objs, {"size": [4, 0.6, 4], "origin": "bottom-center"}


def bone_pile(seed=3):
    """Drift of long bones and skulls against a wall or corner."""
    import random as _random
    rng = _random.Random(seed)
    bm = bmesh.new()
    for i in range(9):
        x, y = (rng.random() - 0.5) * 0.9, (rng.random() - 0.5) * 0.7
        got = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=0.1 + rng.random() * 0.05)
        for v in got["verts"]:
            v.co = Vector((v.co.x + x, v.co.y + y, v.co.z * 0.7 + 0.09 + i * 0.04))
    for i in range(6):
        x, y = (rng.random() - 0.5) * 1.0, (rng.random() - 0.5) * 0.8
        a = rng.random() * math.pi
        dx, dy = math.cos(a) * 0.3, math.sin(a) * 0.3
        V.add_box(bm, (x - dx - 0.03, y - dy - 0.03, 0.02 + i * 0.03),
                  (x + dx + 0.03, y + dy + 0.03, 0.08 + i * 0.03))
    obj = V.bm_to_object(bm, "bone_pile", ("M_bone",))
    return [obj], {"size": [1.2, 1.0, 0.6], "origin": "bottom-center"}


def sarcophagus():
    """Stone chest with a gabled lid, ~2.2 m. Solid, climb-proof."""
    objs = []
    bm = bmesh.new()
    V.add_box(bm, (-1.1, -0.45, 0), (1.1, 0.45, 0.72))
    objs.append(V.bm_to_object(bm, "sarc_body", ("M_stone_trim",)))
    bm = bmesh.new()
    a = [bm.verts.new(p) for p in ((-1.16, -0.5, 0.72), (1.16, -0.5, 0.72), (1.16, 0.5, 0.72), (-1.16, 0.5, 0.72))]
    r0 = bm.verts.new((-1.16, 0.0, 0.98)); r1 = bm.verts.new((1.16, 0.0, 0.98))
    bm.faces.new((a[0], a[1], r1, r0))
    bm.faces.new((r0, r1, a[2], a[3]))
    bm.faces.new((a[0], r0, a[3]))
    bm.faces.new((a[1], a[2], r1))
    bm.faces.new(list(reversed(a)))
    objs.append(V.bm_to_object(bm, "sarc_lid", ("M_stone",)))
    return objs, {"size": [2.4, 1.0, 1.0], "origin": "bottom-center"}


def shroud_dead(seed=8):
    """A wrapped body at rest on the floor — undercroft set dressing."""
    bm = bmesh.new()
    L = 1.7
    for t4 in range(5):
        t = t4 / 4.0
        r = 0.16 * (1.0 - 0.55 * abs(t * 2 - 1)) + 0.04
        got = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
        for v in got["verts"]:
            v.co = Vector((v.co.x * 1.6 + (t - 0.5) * L, v.co.y, v.co.z * 0.72 + r * 0.7))
    obj = V.bm_to_object(bm, "shroud_dead", ("M_shroud",))
    return [obj], {"size": [1.9, 0.5, 0.35], "origin": "bottom-center"}


def watcher_base():
    """Octagonal rotating plinth for the Watcher statues."""
    b = V.loft_rings("watcher_base", [(0.62, 0, 8, 0), (0.56, 0.14, 8, 0),
                                      (0.5, 0.2, 8, 0), (0.52, 0.34, 8, 0)], "M_stone_trim")
    return [b], {"size": [1.3, 1.3, 0.36], "origin": "bottom-center"}


def cobweb():
    """Corner cobweb: a quarter fan of silk with radial threads."""
    bm = bmesh.new()
    import math as _m
    n = 6
    R = 1.05
    corner = bm.verts.new((0, 0, 0))
    rim = []
    for i in range(n + 1):
        a = _m.pi * 0.5 * i / n
        sag = 1.0 - 0.18 * _m.sin(_m.pi * i / n)
        rim.append(bm.verts.new((R * _m.cos(a) * sag, 0, R * _m.sin(a) * sag)))
    for band in (0.4, 0.72):
        ring = []
        for i in range(n + 1):
            a = _m.pi * 0.5 * i / n
            ring.append(bm.verts.new((R * band * _m.cos(a), 0.002, R * band * _m.sin(a))))
        for i in range(n):
            try:
                bm.faces.new((ring[i], ring[i + 1], corner))
            except ValueError:
                pass
    for i in range(n):
        try:
            bm.faces.new((corner, rim[i], rim[i + 1]))
        except ValueError:
            pass
    obj = V.bm_to_object(bm, "cobweb", ("M_shroud",))
    return [obj], {"size": [1.1, 0.05, 1.1], "origin": "corner"}


def hanging_chain(with_hook=True):
    """A length of iron chain dropping from a vault, ~1.6 m."""
    objs = []
    bm = bmesh.new()
    z = 0.0
    for i in range(9):
        wx = 0.05 if i % 2 else 0.02
        wy = 0.02 if i % 2 else 0.05
        V.add_box(bm, (-wx, -wy, z - 0.09), (wx, wy, z))
        z -= 0.16
    objs.append(V.bm_to_object(bm, "chain", ("M_iron",)))
    if with_hook:
        hook = V.loft_rings("hook", [(0.09, z - 0.02, 10, 0), (0.11, z - 0.1, 10, 0),
                                     (0.09, z - 0.18, 10, 0)], "M_iron")
        objs.append(hook)
    return objs, {"size": [0.2, 0.2, 1.7], "origin": "top-center"}


def door_leaf():
    """A shut double door of banded oak for a 1.9-wide portal opening."""
    objs = []
    bm = bmesh.new()
    for sx in (-1, 1):
        x0 = 0.02 * sx
        x1 = sx * 0.92
        lo, hi = (min(x0, x1), max(x0, x1))
        V.add_box(bm, (lo, -0.06, 0.02), (hi, 0.06, 2.82))
    objs.append(V.bm_to_object(bm, "door_oak", ("M_wood",)))
    bm = bmesh.new()
    for z in (0.5, 1.4, 2.3):
        V.add_box(bm, (-0.9, -0.08, z - 0.05), (0.9, 0.08, z + 0.05))
    for sx in (-1, 1):
        V.add_box(bm, (sx * 0.9 - 0.05, -0.08, 0.1), (sx * 0.9 + 0.05, 0.08, 2.75))
    objs.append(V.bm_to_object(bm, "door_bands", ("M_iron",)))
    tbm = bmesh.new()
    V.add_box(tbm, (-1.0, -0.07, 2.66), (1.0, 0.1, 3.98))
    objs.append(V.bm_to_object(tbm, "door_tympanum", ("M_stone",)))
    return objs, {"size": [2.0, 0.24, 3.98], "origin": "bottom-center"}


def chrism_flask():
    """The pilgrim's chrism flask: a fluted dark-bronze & leather liturgical
    vessel banded in filigree gold with a glowing golden chrism lip."""
    objs = []
    n = 16
    # Dark oiled leather & bronze belly vessel (capped at bottom in dark bronze)
    objs.append(V.loft_rings("body", [
        (0.036, 0.00, n, 0),
        (0.072, 0.035, n, 0.25),
        (0.082, 0.095, n, 0),
        (0.060, 0.148, n, 0.2),
        (0.028, 0.178, n, 0),
    ], "M_bronze", cap_bottom=True, cap_top=False))
    # Uncapped filigree gold trim rings around base, belly, and flared spout
    objs.append(V.loft_rings("foot_band", [
        (0.056, 0.016, n, 0),
        (0.068, 0.028, n, 0),
    ], "M_gold", cap_bottom=False, cap_top=False))
    objs.append(V.loft_rings("belly_band", [
        (0.084, 0.084, n, 0),
        (0.085, 0.104, n, 0),
    ], "M_gold", cap_bottom=False, cap_top=False))
    objs.append(V.loft_rings("neck_lip", [
        (0.031, 0.168, 14, 0),
        (0.026, 0.195, 14, 0),
        (0.036, 0.222, 14, 0.3),
        (0.038, 0.235, 14, 0),
    ], "M_gold", cap_bottom=False, cap_top=False))
    # Warm golden liquid chrism glowing inside the open mouth
    objs.append(V.loft_rings("chrism_glow", [
        (0.024, 0.220, 12, 0),
        (0.030, 0.236, 12, 0),
        (0.008, 0.244, 12, 0),
    ], "M_ember", cap_bottom=False, cap_top=True))
    return objs, {"size": [0.17, 0.17, 0.26], "origin": "bottom-center"}


BUILDERS = {
    "chrism_flask": chrism_flask,
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
    "anvil": anvil,
    "canal_vault_8m": lambda: canal_vault(False),
    "canal_vault_8m_win": lambda: canal_vault(True),
    "ferry_boat": ferry_boat,
    "fence_iron_4m": fence_iron_4m,
    "bell_great": bell_great,
    "organ_case": organ_case,
    "choir_stall": choir_stall,
    "chime_stone": chime_stone,
    "votive_stand_lit": lambda: votive_stand_tall(True),
    "votive_stand_cold": lambda: votive_stand_tall(False),
    "bell_fragment": bell_fragment,
    "mosaic_medallion": mosaic_medallion,
    "ossuary_wall_4m": ossuary_wall_4m,
    "bone_pile": bone_pile,
    "sarcophagus": sarcophagus,
    "shroud_dead": shroud_dead,
    "watcher_base": watcher_base,
    "cobweb": cobweb,
    "hanging_chain": lambda: hanging_chain(True),
    "hanging_chain_bare": lambda: hanging_chain(False),
    "door_leaf": door_leaf,
}
