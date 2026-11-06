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
    """Wrought-iron tripod brazier with hollow concave iron basin, open gilt
    lip ring, tripod stretcher ring, and glowing embers/flames (or cold ash)."""
    objs = []
    # Hollow concave iron basin (outer wall rises to z=0.85, then steps down inside to z=0.66)
    objs.append(
        V.loft_rings(
            "bowl",
            [
                (0.10, 0.48, 20, 0),
                (0.16, 0.54, 20, 0),
                (0.35, 0.63, 20, 0),
                (0.40, 0.78, 20, 0),
                (0.43, 0.81, 20, 0),
                (0.37, 0.85, 20, 0),
                (0.32, 0.85, 20, 0),
                (0.28, 0.70, 20, 0),
                (0.08, 0.66, 20, 0),
            ],
            "M_iron",
            cap_bottom=True,
            cap_top=True,
        )
    )
    # Uncapped hollow gold rim wrapping only the outer lip of the bowl
    objs.append(
        V.loft_rings(
            "bowl_rim",
            [
                (0.40, 0.78, 20, 0),
                (0.438, 0.815, 20, 0),
                (0.385, 0.852, 20, 0),
                (0.325, 0.852, 20, 0),
                (0.355, 0.78, 20, 0),
                (0.40, 0.78, 20, 0),
            ],
            "M_gold",
            cap_bottom=False,
            cap_top=False,
        )
    )
    # Tripod legs + horizontal iron stretcher ring at z=0.28
    objs.append(
        V.loft_rings(
            "leg_ring",
            [
                (0.23, 0.26, 18, 0),
                (0.23, 0.30, 18, 0),
                (0.195, 0.30, 18, 0),
                (0.195, 0.26, 18, 0),
                (0.23, 0.26, 18, 0),
            ],
            "M_iron",
            cap_bottom=False,
            cap_top=False,
        )
    )
    for k in range(3):
        a = k * 2 * math.pi / 3
        leg = V.sweep_profile(
            "leg",
            [
                (0.28 * math.cos(a), 0.28 * math.sin(a), 0),
                (0.22 * math.cos(a), 0.22 * math.sin(a), 0.28),
                (0.16 * math.cos(a), 0.16 * math.sin(a), 0.56),
            ],
            V.circle_profile(0.026, 10),
            "M_iron",
            up_hint=Vector((-math.sin(a), math.cos(a), 0)),
        )
        objs.append(leg)
    if lit:
        embers = V.loft_rings(
            "brazier_embers",
            [
                (0.31, 0.72, 18, 0),
                (0.29, 0.81, 18, 0.15),
                (0.22, 0.86, 18, 0.30),
                (0.11, 0.90, 18, 0.45),
                (0.03, 0.93, 18, 0.60),
            ],
            "M_ember",
        )
        objs.append(embers)
        for k in range(3):
            a = k * 2.094 + 0.4
            ff = _flame("brazier_flame%d" % k, 0.055, 0.22)
            ff.location = (0.1 * math.cos(a), 0.1 * math.sin(a), 0.88)
            objs.append(ff)
    else:
        ash = V.loft_rings(
            "ash",
            [
                (0.31, 0.72, 18, 0),
                (0.25, 0.82, 18, 0.2),
                (0.10, 0.86, 18, 0.4),
            ],
            "M_stone_dark",
        )
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
    """Carved Gothic hooded saint statue on a moulded pedestal, clasping a
    downward broadsword with stone halo disc behind the hood."""
    objs = []
    bm = bmesh.new()
    V.add_box(bm, (-0.52, -0.52, 0.0), (0.52, 0.52, 0.11))
    V.add_box(bm, (-0.45, -0.45, 0.11), (0.45, 0.45, 0.18))
    V.add_box(bm, (-0.40, -0.40, 0.18), (0.40, 0.40, 0.47))
    V.add_box(bm, (-0.46, -0.46, 0.47), (0.46, 0.46, 0.55))
    objs.append(V.bm_to_object(bm, "plinth", ("M_stone_dark",)))

    robe = _robe("saint", 1.9, 0.34, True, "M_stone_trim")
    robe.location = (0, 0, 0.55)
    objs.append(robe)

    # Draped stone sleeves clasping the sword hilt + carved stone halo disc + broadsword
    for sx in (-1, 1):
        arm = V.sweep_profile(
            f"saint_sleeve_{sx}",
            [
                (sx * 0.22, 0.02, 1.94),
                (sx * 0.21, 0.14, 1.74),
                (sx * 0.12, 0.25, 1.64),
                (sx * 0.04, 0.32, 1.62),
            ],
            V.chamfer_rect_profile(0.11, 0.13, 0.03),
            "M_stone_trim",
            up_hint=Vector((0, 0, 1)),
        )
        objs.append(arm)
    bm2 = bmesh.new()
    for sx in (-1, 1):
        V.add_box(bm2, (sx * 0.045 - 0.04, 0.29, 1.58), (sx * 0.045 + 0.04, 0.38, 1.70))
    # Tapered broadsword blade, arched quillons, grip, and wheel pommel
    V.add_box(bm2, (-0.042, 0.325, 0.55), (0.042, 0.355, 1.54))
    V.add_box(bm2, (-0.018, 0.312, 0.55), (0.018, 0.368, 1.54))
    V.add_box(bm2, (-0.21, 0.31, 1.52), (0.21, 0.37, 1.58))
    for sx in (-1, 1):
        V.add_box(bm2, (sx * 0.20 - 0.03, 0.305, 1.50), (sx * 0.20 + 0.03, 0.375, 1.59))
    V.add_box(bm2, (-0.028, 0.315, 1.58), (0.028, 0.365, 1.76))
    V.add_box(bm2, (-0.058, 0.305, 1.76), (0.058, 0.375, 1.86))
    sw = V.bm_to_object(bm2, "saint_sword", ("M_stone_trim",))
    objs.append(sw)

    halo = V.loft_rings(
        "saint_halo",
        [
            (0.02, -0.018, 20, 0),
            (0.28, -0.018, 20, 0),
            (0.30, 0.0, 20, 0),
            (0.28, 0.018, 20, 0),
            (0.02, 0.018, 20, 0),
        ],
        "M_stone_trim",
        cap_bottom=True,
        cap_top=True,
    )
    halo.rotation_euler = (math.pi / 2, 0, 0)
    halo.location = (0, -0.10, 2.32)
    objs.append(halo)
    return objs, {"size": [1, 1, 2.6], "origin": "bottom-center"}


def gargoyle():
    """Perched grotesque: hunched body, folded wings, horned skull."""
    objs = []
    bm = bmesh.new()
    # Perched stone plinth block under talons
    bm_plinth = bmesh.new()
    V.add_box(bm_plinth, (-0.24, -0.22, 0.0), (0.24, 0.50, 0.06))
    objs.append(V.bm_to_object(bm_plinth, "gargoyle_plinth", ("M_stone_dark",)))
    for (c, r, sq) in (((0, -0.05, 0.22), 0.20, 0.8), ((0, 0.16, 0.30), 0.16, 0.9),
                       ((0, 0.32, 0.38), 0.13, 1.0)):
        got = bmesh.ops.create_icosphere(bm, subdivisions=2, radius=r)
        for v in got["verts"]:
            v.co.z *= sq
            v.co += Vector(c)
    body = V.bm_to_object(bm, "gargoyle_body", ("M_stone_trim",))
    objs.append(body)
    # Sculpted horned skull + snout + lower jaw + brow ridges
    bm2 = bmesh.new()
    got_h = bmesh.ops.create_icosphere(bm2, subdivisions=2, radius=0.105)
    for v in got_h["verts"]:
        v.co.x *= 0.88
        v.co.y *= 1.15
        v.co.z *= 0.85
        v.co += Vector((0.0, 0.44, 0.49))
    V.add_box(bm2, (-0.055, 0.48, 0.43), (0.055, 0.65, 0.50))
    V.add_box(bm2, (-0.042, 0.48, 0.39), (0.042, 0.62, 0.43))
    for sx in (-1, 1):
        V.add_box(bm2, (sx * 0.055 - 0.025, 0.46, 0.51), (sx * 0.055 + 0.025, 0.56, 0.55))
    head = V.bm_to_object(bm2, "gargoyle_head", ("M_stone_trim",))
    objs.append(head)
    for sx in (-1, 1):
        horn = V.sweep_profile("horn", [(sx * 0.07, 0.42, 0.54), (sx * 0.13, 0.34, 0.66), (sx * 0.16, 0.24, 0.74)],
                               V.circle_profile(0.026, 8), "M_stone_trim")
        objs.append(horn)
        bmw = bmesh.new()
        a = bmw.verts.new((sx * 0.15, 0.12, 0.42))
        b = bmw.verts.new((sx * 0.36, -0.14, 0.64))
        c = bmw.verts.new((sx * 0.34, -0.36, 0.26))
        d = bmw.verts.new((sx * 0.14, -0.18, 0.16))
        bmw.faces.new((a, b, c, d) if sx > 0 else (d, c, b, a))
        bmesh.ops.solidify(bmw, geom=list(bmw.faces), thickness=0.032)
        wing = V.bm_to_object(bmw, "wing", ("M_stone_trim",))
        objs.append(wing)
        rib = V.sweep_profile("wing_rib", [(sx * 0.15, 0.12, 0.42), (sx * 0.36, -0.14, 0.64), (sx * 0.34, -0.36, 0.26)],
                              V.circle_profile(0.022, 8), "M_stone_trim")
        objs.append(rib)
    for sx in (-1, 1):
        leg = V.sweep_profile("leg", [(sx * 0.13, 0.26, 0.32), (sx * 0.16, 0.40, 0.16), (sx * 0.15, 0.44, 0.05)],
                              V.circle_profile(0.038, 8), "M_stone_trim")
        objs.append(leg)
        hind = V.sweep_profile("hind", [(sx * 0.16, -0.04, 0.22), (sx * 0.19, 0.10, 0.12), (sx * 0.17, 0.18, 0.05)],
                               V.circle_profile(0.044, 8), "M_stone_trim")
        objs.append(hind)
    return objs, {"size": [0.7, 1.0, 0.8], "origin": "bottom-center"}


def banner():
    """Hanging cloth banner with iron finial rod, brass suspension rings,
    gold border & bottom fringe, and double-sided eclipsed-sun sigil. Glory-only."""
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

    bm_iron = bmesh.new()
    V.add_box(bm_iron, (-w / 2 - 0.14, -0.018, 2.502), (w / 2 + 0.14, 0.018, 2.538))
    for sx in (-1, 1):
        x_end = sx * (w / 2 + 0.16)
        V.add_box(bm_iron, (x_end - 0.03, -0.028, 2.492), (x_end + 0.03, 0.028, 2.548))
    rod = V.bm_to_object(bm_iron, "rod", ("M_iron",))

    bm_gold = bmesh.new()
    # 5 suspension rings along top rod + bottom gold fringe band
    for rx in (-0.36, -0.18, 0.0, 0.18, 0.36):
        V.add_box(bm_gold, (rx - 0.016, -0.026, 2.47), (rx + 0.016, 0.026, 2.55))
    y_bot = 0.05 * math.sin(nz * 0.8)
    V.add_box(bm_gold, (-w / 2, y_bot - 0.022, 0.17), (w / 2, y_bot + 0.012, 0.23))
    fringe = V.bm_to_object(bm_gold, "banner_trim", ("M_gold",))

    objs = [obj, rod, fringe]
    # Double-sided gold sun-corona sigil on both -Y and +Y faces
    for sy in (-0.022, 0.014):
        disc = V.loft_rings(
            "sigil",
            [(0.08, -0.008, 16, 0), (0.175, 0.0, 16, 0), (0.08, 0.008, 16, 0)],
            "M_gold",
        )
        disc.location = (0, sy, 1.62)
        disc.rotation_euler = (math.pi / 2, 0, 0)
        objs.append(disc)
    return objs, {"size": [1.1, 0.3, 2.6], "origin": "top-center"}


def pew():
    """Carved Gothic oak church pew (1.86 m) with recessed wainscot back panels,
    muntin stiles, scrolled armrests, trefoil poppyhead bench-end finials,
    kneeler rail, and wrought-iron corner brackets."""
    objs = []
    bm = bmesh.new()
    # Base floor runners & central trestle support
    for sx in (-0.86, 0.0, 0.86):
        V.add_box(bm, (sx - 0.045, -0.22, 0.0), (sx + 0.045, 0.24, 0.07))
    V.add_box(bm, (-0.04, -0.18, 0.07), (0.04, 0.20, 0.40))
    # Contoured seat plank + under-seat apron rail
    V.add_box(bm, (-0.88, -0.21, 0.40), (0.88, 0.17, 0.46))
    V.add_box(bm, (-0.86, -0.18, 0.34), (0.86, -0.13, 0.40))
    # Recessed wainscot backrest field + raised Gothic stiles and rails
    V.add_box(bm, (-0.86, 0.17, 0.46), (0.86, 0.22, 1.00))
    for z0, z1 in ((0.46, 0.53), (0.71, 0.76), (0.96, 1.03)):
        V.add_box(bm, (-0.88, 0.15, z0), (0.88, 0.24, z1))
    for sx in (-0.82, -0.28, 0.28, 0.82):
        V.add_box(bm, (sx - 0.035, 0.15, 0.52), (sx + 0.035, 0.24, 0.97))
    # Molded top cresting rail
    V.add_box(bm, (-0.92, 0.135, 1.03), (0.92, 0.255, 1.09))
    # Bench-end standards with scrolled armrests & carved poppyhead finials
    for sx in (-0.86, 0.86):
        V.add_box(bm, (sx - 0.045, -0.22, 0.07), (sx + 0.045, 0.24, 0.62))
        V.add_box(bm, (sx - 0.045, 0.02, 0.62), (sx + 0.045, 0.25, 1.05))
        V.add_box(bm, (sx - 0.055, -0.25, 0.58), (sx + 0.055, 0.06, 0.65))  # armrest
        # Trefoil poppyhead finial
        V.add_box(bm, (sx - 0.038, 0.13, 1.08), (sx + 0.038, 0.25, 1.17))
        V.add_box(bm, (sx - 0.045, 0.10, 1.11), (sx + 0.045, 0.28, 1.15))
    # Front kneeler rail with end blocks
    V.add_box(bm, (-0.86, -0.34, 0.08), (0.86, -0.25, 0.15))
    for sx in (-0.82, 0.0, 0.82):
        V.add_box(bm, (sx - 0.035, -0.34, 0.0), (sx + 0.035, -0.22, 0.08))
    objs.append(V.bm_to_object(bm, "pew", ("M_wood",)))

    bm_iron = bmesh.new()
    for sx in (-0.91, 0.91):
        V.add_box(bm_iron, (sx - 0.008, -0.22, 0.39), (sx + 0.008, 0.24, 0.46))
        V.add_box(bm_iron, (sx - 0.008, 0.14, 0.96), (sx + 0.008, 0.25, 1.03))
    objs.append(V.bm_to_object(bm_iron, "pew_iron", ("M_iron",)))
    return objs, {"size": [1.86, 0.62, 1.18], "origin": "bottom-center"}


def altar():
    """Carved Gothic stone high altar with stepped plinth, recessed blind-arcade
    chest panels, engaged corner/bay colonnettes, draped liturgical antependium
    cloth with gold fringe & sun-cross, and turned brass candlesticks."""
    objs = []
    bm = bmesh.new()
    # Stepped plinth & overhanging molded mensa slab (top at z = 1.02)
    V.add_box(bm, (-1.08, -0.58, 0.0), (1.08, 0.58, 0.10))
    V.add_box(bm, (-1.02, -0.52, 0.10), (1.02, 0.52, 0.18))
    V.add_box(bm, (-1.02, -0.52, 0.84), (1.02, 0.52, 0.91))
    V.add_box(bm, (-1.08, -0.58, 0.91), (1.08, 0.58, 1.02))
    # Pilaster dividers framing 3 bays on front/back and 1 bay on ends
    for sx in (-0.96, -0.34, 0.34, 0.96):
        for sy in (-0.49, 0.49):
            V.add_box(bm, (sx - 0.055, sy - 0.03, 0.18), (sx + 0.055, sy + 0.03, 0.84))
    objs.append(V.bm_to_object(bm, "altar_body", ("M_stone_trim",)))

    # Recessed dark stone chest core
    bm_core = bmesh.new()
    V.add_box(bm_core, (-0.96, -0.48, 0.18), (0.96, 0.48, 0.84))
    objs.append(V.bm_to_object(bm_core, "altar_core", ("M_stone_dark",)))

    # Draped liturgical altar cloth runner across the center & hanging front/back
    bm_cloth = bmesh.new()
    V.add_box(bm_cloth, (-0.36, -0.59, 0.90), (0.36, 0.59, 1.023))
    for sy in (-0.59, 0.59):
        y0, y1 = (sy - 0.015, sy + 0.005) if sy < 0 else (sy - 0.005, sy + 0.015)
        V.add_box(bm_cloth, (-0.36, y0, 0.28), (0.36, y1, 0.91))
    objs.append(V.bm_to_object(bm_cloth, "altar_cloth", ("M_cloth",)))

    # Gilt cornice molding, antependium fringe, and embossed front/back sun-crosses
    gm = bmesh.new()
    V.add_box(gm, (-1.085, -0.585, 0.885), (1.085, 0.585, 0.92))
    for sy in (-0.595, 0.595):
        y0, y1 = (sy - 0.016, sy + 0.004) if sy < 0 else (sy - 0.004, sy + 0.016)
        V.add_box(gm, (-0.37, y0, 0.25), (0.37, y1, 0.29))
        V.add_box(gm, (-0.022, y0, 0.44), (0.022, y1, 0.78))
        V.add_box(gm, (-0.14, y0, 0.60), (0.14, y1, 0.64))
    objs.append(V.bm_to_object(gm, "altar_gilt", ("M_gold",)))

    # Turned brass candlesticks + lit altar candles
    for (cx, cy, ch) in ((-0.72, 0.0, 0.24), (0.72, 0.08, 0.19)):
        holder = V.loft_rings(
            "altar_holder",
            [
                (0.085, 1.02, 12, 0),
                (0.068, 1.045, 12, 0),
                (0.026, 1.08, 12, 0),
                (0.058, 1.11, 12, 0),
                (0.052, 1.125, 12, 0),
            ],
            "M_gold",
        )
        holder.location = (cx, cy, 0)
        objs.append(holder)
        for c in _candle(ch):
            c.location = (cx, cy, 1.12)
            objs.append(c)
    return objs, {"size": [2.2, 1.2, 1.45], "origin": "bottom-center"}


def plaque():
    """Lore plaque: carved Gothic octagonal stone lectern with stepped moulded plinth,
    fluted shaft, wrought-iron scroll brackets, angled limestone desk, and inset bronze tablet."""
    objs = []
    # Stepped octagonal dark stone plinth + carved freestone fluted column shaft & capital
    plinth = V.loft_rings(
        "plaque_plinth",
        [
            (0.32, 0.00, 8, math.pi / 8),
            (0.32, 0.08, 8, math.pi / 8),
            (0.25, 0.12, 8, math.pi / 8),
            (0.25, 0.18, 8, math.pi / 8),
        ],
        "M_stone_dark",
        cap_bottom=True,
        cap_top=True,
    )
    objs.append(plinth)
    pedestal = V.loft_rings(
        "plaque_post",
        [
            (0.18, 0.18, 8, math.pi / 8),
            (0.16, 0.22, 8, math.pi / 8),
            (0.14, 0.72, 8, math.pi / 8),
            (0.22, 0.80, 8, math.pi / 8),
            (0.28, 0.88, 8, math.pi / 8),
        ],
        "M_stone_trim",
        cap_bottom=True,
        cap_top=True,
    )
    objs.append(pedestal)
    # Wrought-iron gothic corbel brackets under the forward overhang of the reading desk
    for sx in (-0.11, 0.11):
        brk = V.sweep_profile(
            "plaque_bracket",
            [(sx, 0.04, 0.62), (sx, 0.14, 0.74), (sx, 0.18, 0.88), (sx, 0.08, 0.91)],
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
    """Carved Gothic effigy tomb chest: stepped plinth, blind-arcade pilasters,
    overhanging ledger slab, stone bolster pillow, and recumbent robed effigy
    clasping a relief broadsword."""
    objs = []
    bm = bmesh.new()
    V.add_box(bm, (-0.60, -1.16, 0.0), (0.60, 1.16, 0.08))
    V.add_box(bm, (-0.54, -1.10, 0.08), (0.54, 1.10, 0.42))
    objs.append(V.bm_to_object(bm, "tomb", ("M_stone_dark",)))

    # Carved freestone ledger slab, pilaster colonnettes, head bolster pillow & relief sword
    bm_trim = bmesh.new()
    V.add_box(bm_trim, (-0.62, -1.18, 0.42), (0.62, 1.18, 0.52))
    for sx in (-0.54, 0.54):
        for sy in (-1.02, -0.34, 0.34, 1.02):
            V.add_box(bm_trim, (sx - 0.025, sy - 0.045, 0.08), (sx + 0.025, sy + 0.045, 0.42))
    # Carved stone pillow under the effigy's hood (+Y end)
    V.add_box(bm_trim, (-0.28, 0.62, 0.52), (0.28, 1.00, 0.60))
    # Carved pointed feet/sabatons & foot-rest bolster at -Y end
    V.add_box(bm_trim, (-0.22, -0.98, 0.52), (0.22, -0.84, 0.58))
    for sx in (-0.09, 0.09):
        V.add_box(bm_trim, (sx - 0.045, -0.86, 0.54), (sx + 0.045, -0.74, 0.68))
    # Relief broadsword & clasped hands along the effigy's chest
    V.add_box(bm_trim, (-0.025, -0.68, 0.65), (0.025, 0.36, 0.70))
    V.add_box(bm_trim, (-0.15, 0.20, 0.66), (0.15, 0.25, 0.71))
    V.add_box(bm_trim, (-0.09, 0.26, 0.65), (0.09, 0.40, 0.72))
    objs.append(V.bm_to_object(bm_trim, "tomb_trim", ("M_stone_trim",)))

    # Recumbent robed effigy tapering toward the ankles, rising onto the head pillow
    eff_rings = [
        (0.20, 0.00, 16, 0),   # ankles at y = -0.80
        (0.24, 0.35, 16, 0),   # shins/knees
        (0.26, 0.75, 16, 0),   # hips
        (0.25, 1.05, 16, 0),   # waist
        (0.32, 1.35, 16, 0),   # chest
        (0.30, 1.52, 16, 0),   # shoulders
        (0.21, 1.62, 16, 0),   # neck collar
        (0.23, 1.74, 16, 0),   # hood crown on pillow
        (0.16, 1.86, 16, 0),
        (0.05, 1.94, 16, 0),   # hood peak
    ]
    robe = V.loft_rings("effigy", eff_rings, "M_stone_trim")
    robe.scale = (0.88, 0.36, 0.90)
    robe.rotation_euler = (math.pi / 2 + 0.055, 0, math.pi)
    robe.location = (0, -0.80, 0.54)
    objs.append(robe)
    return objs, {"size": [1.24, 2.36, 0.75], "origin": "bottom-center"}


def gate_iron():
    """Two-leaf wrought-iron Gothic gate for a 2.4 m opening, with forged
    spearhead finials atop every bar, lock-plates, and hinge collars."""
    objs = []
    for leaf, sgn in (("gate_leaf_l", -1), ("gate_leaf_r", 1)):
        bm = bmesh.new()
        x0, x1 = (0.02, 1.18) if sgn > 0 else (-1.18, -0.02)
        for x in (x0, x1):
            V.add_box(bm, (x - 0.024, -0.024, 0.02), (x + 0.024, 0.024, 2.24))
            # Spearhead finial on outer & inner stiles
            V.add_box(bm, (x - 0.032, -0.030, 2.22), (x + 0.032, 0.030, 2.26))
            V.add_box(bm, (x - 0.020, -0.020, 2.26), (x + 0.020, 0.020, 2.34))
        for z in (0.09, 0.56, 1.05, 2.05):
            h_rail = 0.018 if z == 0.56 else 0.028
            V.add_box(bm, (x0, -0.020, z - h_rail), (x1, 0.020, z + h_rail))
        # Lockbox plate at central meeting stile & hinge collars at outer stile
        x_in = 0.06 if sgn > 0 else -0.06
        x_out = 1.18 if sgn > 0 else -1.18
        V.add_box(bm, (x_in - 0.04, -0.030, 0.94), (x_in + 0.04, 0.030, 1.16))
        for zh in (0.28, 1.86):
            V.add_box(bm, (x_out - 0.038, -0.038, zh - 0.035), (x_out + 0.038, 0.038, zh + 0.035))
        x = x0 + 0.12
        while x < x1 - 0.05:
            V.add_box(bm, (x - 0.014, -0.014, 0.04), (x + 0.014, 0.014, 2.24))
            # Forged spearhead collar + tapered point
            V.add_box(bm, (x - 0.024, -0.022, 2.21), (x + 0.024, 0.022, 2.24))
            V.add_box(bm, (x - 0.020, -0.016, 2.24), (x + 0.020, 0.016, 2.30))
            V.add_box(bm, (x - 0.010, -0.010, 2.30), (x + 0.010, 0.010, 2.36))
            # Lower dog-bar pickets between 0.09 and 0.56
            if x + 0.078 < x1 - 0.05:
                xm = x + 0.078
                V.add_box(bm, (xm - 0.010, -0.010, 0.09), (xm + 0.010, 0.010, 0.62))
                V.add_box(bm, (xm - 0.016, -0.014, 0.62), (xm + 0.016, 0.014, 0.67))
            x += 0.155
        obj = V.bm_to_object(bm, leaf, ("M_iron",))
        objs.append(obj)
    return objs, {"size": [2.4, 0.1, 2.36], "origin": "bottom-center"}


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
    """A working mini ferry for the waterworks passage: timber barge hull with
    gunwale rubbing strakes, internal ribs, planked deck, stern mooring frame,
    prow wrought-iron cresset lantern cage with teardrop ember flame, and
    angled wooden steering sweep oar."""
    objs = []
    bm = bmesh.new()
    V.add_box(bm, (-2.1, -0.85, 0.08), (1.7, 0.85, 0.34))
    V.add_box(bm, (-2.1, -0.85, 0.34), (-1.95, 0.85, 0.82))
    V.add_box(bm, (-2.1, -0.85, 0.34), (1.7, -0.7, 0.78))
    V.add_box(bm, (-2.1, 0.7, 0.34), (1.7, 0.85, 0.78))
    # Outer gunwale rubbing strakes & internal framing ribs
    for sy in (-1, 1):
        y_out = sy * 0.88
        y_in = sy * 0.83
        V.add_box(bm, (-2.12, min(y_in, y_out), 0.70), (1.72, max(y_in, y_out), 0.80))
    for rx in (-1.55, -0.85, -0.15, 0.55, 1.25):
        for sy in (-1, 1):
            y0, y1 = (0.64, 0.70) if sy > 0 else (-0.70, -0.64)
            V.add_box(bm, (rx - 0.035, y0, 0.38), (rx + 0.035, y1, 0.76))
    V.add_box(bm, (1.7, -0.62, 0.12), (2.15, 0.62, 0.74))
    V.add_box(bm, (2.15, -0.34, 0.18), (2.52, 0.34, 0.68))
    V.add_box(bm, (2.48, -0.12, 0.24), (2.64, 0.12, 0.72))  # prow stemhead post
    objs.append(V.bm_to_object(bm, "ferry_hull", ("M_wood",)))

    bm = bmesh.new()
    x = -1.92
    while x < 1.6:
        V.add_box(bm, (x, -0.68, 0.34), (x + 0.31, 0.68, 0.40))
        x += 0.36
    V.add_box(bm, (1.7, -0.5, 0.32), (2.12, 0.5, 0.40))
    objs.append(V.bm_to_object(bm, "ferry_deck", ("M_wood",)))

    # Stern mooring gallows + prow wrought-iron lantern post & octagonal cage
    bm = bmesh.new()
    for py in (-0.72, 0.72):
        V.add_box(bm, (-1.99, py - 0.05, 0.78), (-1.89, py + 0.05, 1.44))
    V.add_box(bm, (-1.98, -0.74, 1.32), (-1.9, 0.74, 1.42))
    V.add_cyl(bm, 1.87, 0.0, 0.68, 0.84, 0.042, n=10)
    V.add_cyl(bm, 1.87, 0.0, 1.50, 0.06, 0.145, n=10)
    V.add_cyl(bm, 1.87, 0.0, 1.84, 0.05, 0.155, n=10)
    V.add_cyl(bm, 1.87, 0.0, 1.89, 0.06, 0.085, n=10)
    for i in range(6):
        a = i * math.pi / 3.0
        V.add_cyl(bm, 1.87 + 0.125 * math.cos(a), 0.125 * math.sin(a), 1.55, 0.30, 0.013, n=6)
    objs.append(V.bm_to_object(bm, "ferry_iron", ("M_iron",)))

    flame = V.loft_rings(
        "ferry_flame",
        [
            (0.055, 1.56, 10, 0),
            (0.095, 1.66, 10, 0.3),
            (0.055, 1.76, 10, 0.6),
            (0.015, 1.83, 10, 0.9),
        ],
        "M_ember",
    )
    flame.location = (1.87, 0.0, 0.0)
    objs.append(flame)

    # Angled wooden steering sweep oar resting over the stern transom
    bm = bmesh.new()
    oar_m = Matrix.Translation((-2.02, 0.36, 0.66)) @ Matrix.Rotation(math.radians(-26), 4, "Y")
    V.add_box(bm, (-0.18, -0.025, -0.025), (0.68, 0.025, 0.025))   # loom shaft
    V.add_box(bm, (-0.82, -0.018, -0.085), (-0.16, 0.018, 0.085))  # tapered sweep blade
    bmesh.ops.transform(bm, matrix=oar_m, verts=bm.verts)
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
        ri = r_h - 0.022
        objs.append(V.loft_rings(
            "stump_hoop",
            [
                (ri, z_h, 12, 0),
                (r_h, z_h, 12, 0),
                (r_h, z_h + 0.035, 12, 0),
                (ri, z_h + 0.035, 12, 0),
                (ri, z_h, 12, 0),
            ],
            "M_iron",
            cap_bottom=False,
            cap_top=False,
        ))

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
    """4 m wrought-iron Gothic fence section on a chamfered stone curb with
    forged spearhead pickets, lower dog-bars, and finial-crowned end posts."""
    objs = []
    bm_curb = bmesh.new()
    V.add_box(bm_curb, (-2.04, -0.09, 0.0), (2.04, 0.09, 0.10))
    V.add_box(bm_curb, (-2.02, -0.07, 0.10), (2.02, 0.07, 0.14))
    objs.append(V.bm_to_object(bm_curb, "fence_curb", ("M_stone_trim",)))

    bm = bmesh.new()
    for z in (0.18, 0.72, 1.72):
        V.add_box(bm, (-2.0, -0.022, z - 0.028), (2.0, 0.022, z + 0.028))
    x = -1.87
    while x < 1.90:
        V.add_box(bm, (x - 0.015, -0.015, 0.14), (x + 0.015, 0.015, 1.90))
        # Forged spearhead collar + tapered point
        V.add_box(bm, (x - 0.025, -0.022, 1.87), (x + 0.025, 0.022, 1.90))
        V.add_box(bm, (x - 0.022, -0.016, 1.90), (x + 0.022, 0.016, 1.97))
        V.add_box(bm, (x - 0.011, -0.010, 1.97), (x + 0.011, 0.010, 2.03))
        if x + 0.085 < 1.90:
            xm = x + 0.085
            V.add_box(bm, (xm - 0.010, -0.010, 0.18), (xm + 0.010, 0.010, 0.78))
            V.add_box(bm, (xm - 0.016, -0.014, 0.78), (xm + 0.016, 0.014, 0.84))
        x += 0.17
    for px in (-2.0, 2.0):
        V.add_box(bm, (px - 0.048, -0.048, 0.14), (px + 0.048, 0.048, 1.98))
        V.add_box(bm, (px - 0.062, -0.062, 1.98), (px + 0.062, 0.062, 2.03))
        V.add_box(bm, (px - 0.036, -0.036, 2.03), (px + 0.036, 0.036, 2.12))
        V.add_box(bm, (px - 0.018, -0.018, 2.12), (px + 0.018, 0.018, 2.18))
    objs.append(V.bm_to_object(bm, "fence_iron_4m", ("M_iron",)))
    return objs, {"size": [4, 0.18, 2.18], "origin": "bottom-center"}


def bell_great():
    """The Bellkeeper's cracked great bell — also the tower bell. ~1.6 m tall."""
    n = 18
    rings = list(reversed([
        (0.02, 1.61, n, 0), (0.10, 1.62, n, 0), (0.16, 1.55, n, 0), (0.30, 1.45, n, 0),
        (0.44, 1.2, n, 0), (0.52, 0.9, n, 0), (0.56, 0.55, n, 0),
        (0.62, 0.28, n, 0), (0.72, 0.10, n, 0), (0.74, 0.0, n, 0),
        (0.68, 0.03, n, 0), (0.55, 0.24, n, 0), (0.49, 0.55, n, 0),
        (0.42, 0.9, n, 0), (0.32, 1.15, n, 0), (0.13, 1.38, n, 0),
        (0.02, 1.40, n, 0),
    ]))
    bell = V.loft_rings("bell_great", rings, "M_bell", cap_bottom=True, cap_top=True)
    clapper = V.loft_rings(
        "clapper",
        list(reversed([
            (0.035, 1.38, 12, 0), (0.05, 0.42, 12, 0),
            (0.115, 0.30, 12, 0), (0.12, 0.12, 12, 0),
            (0.03, 0.05, 12, 0),
        ])),
        "M_iron",
        cap_bottom=True,
        cap_top=True,
    )
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
    # Upper pipe-chest cornice & wooden pipe-tower pilasters + central mitre tower hood
    V.add_box(bm, (-1.38, -0.38, 1.12), (1.38, 0.48, 1.28))
    for sx in (-1.32, -0.78, -0.26, 0.26, 0.78, 1.32):
        h_pil = 4.02 if abs(sx) < 0.5 else 3.65
        V.add_box(bm, (sx - 0.05, -0.34, 1.28), (sx + 0.05, 0.20, h_pil))
    V.add_box(bm, (-1.40, -0.38, 3.60), (-0.72, 0.24, 3.78))
    V.add_box(bm, (0.72, -0.38, 3.60), (1.40, 0.24, 3.78))
    # Central pipe-tower cornice, side flat lintels, and solid rear soundboard backing
    V.add_box(bm, (-0.78, -0.35, 3.04), (-0.24, 0.22, 3.20))
    V.add_box(bm, (0.24, -0.35, 3.04), (0.78, 0.22, 3.20))
    V.add_box(bm, (-0.34, -0.38, 3.98), (0.34, 0.24, 4.16))
    V.add_box(bm, (-0.24, -0.34, 4.16), (0.24, 0.20, 4.26))
    V.add_box(bm, (-1.30, 0.14, 1.28), (1.30, 0.22, 3.62))
    V.add_box(bm, (-0.30, 0.14, 3.62), (0.30, 0.22, 4.02))
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
    V.add_box(bm_gild, (-0.76, -0.30, 2.90), (-0.28, -0.22, 3.04))
    V.add_box(bm_gild, (0.28, -0.30, 2.90), (0.76, -0.22, 3.04))
    V.add_box(bm_gild, (-0.24, -0.34, 3.84), (0.24, -0.26, 3.98))
    objs.append(V.bm_to_object(bm_gild, "organ_gild", ("M_gold",)))

    # 15 graduated bronze & steel flue pipes with conical feet and labium mouths
    n = 15
    for i in range(n):
        t = i / (n - 1.0)
        x = -1.18 + 2.36 * t
        in_tower = abs(x) > 0.78
        if in_tower:
            h = 1.95 + 0.22 * (1.0 - abs((abs(x) - 1.05) / 0.25))
            r = 0.068
            y_off = -0.14
        elif abs(x) < 0.24:
            # Central tower pipes capped cleanly below the z=3.98 central cornice
            u = abs(x) / 0.22
            h = 2.28 + 0.28 * (1.0 - u)
            r = 0.056 + 0.012 * (1.0 - u)
            y_off = -0.10
        else:
            # Side flats capped cleanly below the z=3.04 flat lintels
            u = (abs(x) - 0.26) / 0.50
            h = 1.35 + 0.28 * (1.0 - abs(u - 0.5) * 2.0)
            r = 0.048
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
    """High-backed 3-bay cathedral choir stall bench (faces -Y like the pews),
    with carved parclose stall dividers, misericord brackets, linenfold wainscot
    panels, overhanging coved canopy hood, and gilt brass cornice trim."""
    objs = []
    bm = bmesh.new()
    # Stepped podium base & front kneeler rail
    V.add_box(bm, (-1.18, -0.32, 0.0), (1.18, 0.32, 0.08))
    V.add_box(bm, (-1.15, -0.28, 0.14), (1.15, -0.19, 0.21))
    # Contoured seat plank + under-seat misericord corbel brackets in each of the 3 bays
    V.add_box(bm, (-1.15, -0.24, 0.43), (1.15, 0.15, 0.50))
    for bx in (-0.76, 0.0, 0.76):
        V.add_box(bm, (bx - 0.11, -0.18, 0.35), (bx + 0.11, 0.08, 0.43))
    # High wainscot dossal back field + horizontal rails + vertical bay stiles
    V.add_box(bm, (-1.14, 0.17, 0.08), (1.14, 0.26, 1.55))
    for z0, z1 in ((0.50, 0.57), (0.98, 1.04), (1.46, 1.55)):
        V.add_box(bm, (-1.16, 0.14, z0), (1.16, 0.29, z1))
    # 4 stall partition standards (parcloses) with elbow rests and poppyhead finials
    for sx in (-1.12, -0.38, 0.38, 1.12):
        V.add_box(bm, (sx - 0.04, -0.28, 0.08), (sx + 0.04, 0.16, 0.84))
        V.add_box(bm, (sx - 0.05, -0.30, 0.80), (sx + 0.05, 0.14, 0.88))  # elbow rest
        V.add_box(bm, (sx - 0.035, -0.26, 0.88), (sx + 0.035, -0.16, 0.98))  # poppyhead finial
        V.add_box(bm, (sx - 0.04, 0.13, 0.50), (sx + 0.04, 0.29, 1.56))      # back stile
    # Vertical linenfold ribs inside the 3 upper back panels
    for bx in (-0.75, 0.0, 0.75):
        for dx in (-0.16, 0.0, 0.16):
            V.add_box(bm, (bx + dx - 0.02, 0.145, 0.57), (bx + dx + 0.02, 0.175, 1.46))
    # Overhanging coved canopy cornice + pendant bosses
    V.add_box(bm, (-1.18, -0.02, 1.55), (1.18, 0.34, 1.65))
    V.add_box(bm, (-1.21, -0.10, 1.65), (1.21, 0.38, 1.75))
    for sx in (-1.12, -0.38, 0.38, 1.12):
        V.add_box(bm, (sx - 0.035, -0.08, 1.49), (sx + 0.035, 0.0, 1.55))
    objs.append(V.bm_to_object(bm, "choir_stall", ("M_wood",)))

    bm_brass = bmesh.new()
    V.add_box(bm_brass, (-1.215, -0.105, 1.64), (1.215, -0.085, 1.67))
    for bx in (-0.75, 0.0, 0.75):
        V.add_box(bm_brass, (bx - 0.04, 0.135, 1.22), (bx + 0.04, 0.155, 1.30))
    objs.append(V.bm_to_object(bm_brass, "choir_brass", ("M_brass",)))
    return objs, {"size": [2.4, 0.7, 1.75], "origin": "bottom-center"}


def chime_stone():
    """Vesper chime: stepped octagonal Gothic stone pillar with cantilevered oak
    gallows arm, wrought-iron scroll bracket, suspended cast-bronze tubular chime
    ('chime_bar'), and spherical iron clapper."""
    objs = []
    post = V.loft_rings(
        "chime_post",
        [
            (0.24, 0.0, 12, 0),
            (0.24, 0.10, 12, 0),
            (0.18, 0.14, 12, 0),
            (0.18, 0.24, 12, 0),
            (0.125, 0.28, 12, 0),
            (0.110, 1.88, 12, 0),
            (0.155, 1.98, 12, 0),
            (0.175, 2.08, 12, 0),
        ],
        "M_stone_trim",
        cap_bottom=True,
        cap_top=True,
    )
    objs.append(post)
    bm = bmesh.new()
    V.add_box(bm, (-0.055, -0.66, 1.98), (0.055, 0.14, 2.08))
    objs.append(V.bm_to_object(bm, "chime_arm", ("M_wood",)))
    # Continuous angled timber knee-brace supporting the gallows arm
    brace = V.sweep_profile(
        "chime_brace",
        [(0.0, -0.05, 1.62), (0.0, -0.23, 1.80), (0.0, -0.42, 1.99)],
        V.chamfer_rect_profile(0.072, 0.076, 0.014),
        "M_wood",
        up_hint=Vector((1, 0, 0)),
    )
    objs.append(brace)
    # Cast-bronze cylindrical tubular bell ('chime_bar' animated by ChimePuzzle._swing)
    bm_bar = bmesh.new()
    V.add_cyl(bm_bar, 0.0, -0.51, 1.92, 0.06, 0.022, n=10)
    V.add_cyl(bm_bar, 0.0, -0.51, 1.86, 0.06, 0.068, n=14)
    V.add_cyl(bm_bar, 0.0, -0.51, 1.12, 0.74, 0.054, n=14)
    V.add_cyl(bm_bar, 0.0, -0.51, 1.06, 0.06, 0.072, n=14)
    objs.append(V.bm_to_object(bm_bar, "chime_bar", ("M_bronze",)))
    # Wrought-iron hanger strap, suspension ring, and spherical clapper
    bm_iron = bmesh.new()
    V.add_box(bm_iron, (-0.062, -0.55, 1.97), (0.062, -0.47, 2.09))
    V.add_cyl(bm_iron, 0.0, -0.51, 0.96, 0.10, 0.030, n=10)
    objs.append(V.bm_to_object(bm_iron, "chime_clapper", ("M_iron",)))
    return objs, {"size": [0.5, 1.3, 2.1], "origin": "bottom-center"}


def votive_stand_tall(lit=True):
    """Tall wrought-iron votive stand with stepped stone socle, scrolled tripod
    spurs, mid-shaft brass collar, rimmed pricket tray, and 5 wax candles."""
    objs = []
    socle = V.loft_rings(
        "votive_socle",
        [
            (0.25, 0.0, 12, 0),
            (0.25, 0.06, 12, 0),
            (0.19, 0.09, 12, 0),
            (0.19, 0.14, 12, 0),
        ],
        "M_stone_dark",
    )
    objs.append(socle)
    objs.append(
        V.loft_rings(
            "votive_col",
            [
                (0.13, 0.14, 14, 0),
                (0.058, 0.22, 14, 0),
                (0.046, 0.68, 14, 0),
                (0.068, 0.72, 14, 0),
                (0.046, 0.76, 14, 0),
                (0.042, 1.16, 14, 0),
                (0.175, 1.24, 14, 0),
                (0.205, 1.28, 14, 0),
                (0.195, 1.32, 14, 0),
                (0.165, 1.32, 14, 0),
                (0.155, 1.29, 14, 0),
            ],
            "M_iron",
        )
    )
    objs.append(
        V.loft_rings(
            "votive_gilt",
            [
                (0.206, 1.275, 14, 0),
                (0.206, 1.315, 14, 0),
                (0.175, 1.315, 14, 0),
                (0.175, 1.275, 14, 0),
                (0.206, 1.275, 14, 0),
            ],
            "M_gold",
            cap_bottom=False,
            cap_top=False,
        )
    )
    import random as _random
    rng = _random.Random(9 if lit else 10)
    for i in range(5):
        a = 2 * math.pi * i / 5
        r = 0.115
        h = 0.14 + 0.1 * rng.random()
        cx, cy = r * math.cos(a), r * math.sin(a)
        c = V.loft_rings(
            "cand%d" % i,
            [
                (0.042, 1.29, 10, 0),
                (0.036, 1.31, 10, 0),
                (0.033, 1.30 + h, 10, 0),
                (0.018, 1.292 + h, 10, 0),
            ],
            "M_wax",
        )
        c.location = (cx, cy, 0)
        objs.append(c)
        if lit:
            f = _flame("votive_flame%d" % i, 0.024, 0.085)
            f.location = (cx, cy, 1.31 + h)
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
                                      (1.7, 0.016, 28, 0), (1.7, 0.0, 28, 0),
                                      (1.78, 0.0, 28, 0)], "M_stone_trim",
                       cap_bottom=False, cap_top=False)
    return [disc, rim], {"size": [3.6, 3.6, 0.02], "origin": "bottom-center"}


def ossuary_wall_4m():
    """Crypt wall: carved Gothic stone frame with stepped plinth, bay piers,
    moulded stone shelf ledges, recessed dark-stone loculi niches, and two
    tiers of stacked skulls over corded femur bone beds."""
    import random as _random
    rng = _random.Random(5)
    objs = []
    bm = bmesh.new()
    V.add_box(bm, (-2.0, -0.20, 0.0), (2.0, 0.20, 4.0))
    # Stepped base plinth & upper cornice
    V.add_box(bm, (-2.0, -0.32, 0.0), (2.0, 0.22, 0.28))
    V.add_box(bm, (-2.0, -0.30, 3.76), (2.0, 0.22, 4.0))
    # 3 vertical dividing pilasters framing two 1.75 m ossuary bays
    for px in (-1.90, 0.0, 1.90):
        V.add_box(bm, (px - 0.10, -0.32, 0.28), (px + 0.10, -0.18, 3.76))
    objs.append(V.bm_to_object(bm, "oss_frame", ("M_stone",)))

    bm_shelf = bmesh.new()
    for band_z in (0.9, 2.1):
        V.add_box(bm_shelf, (-1.92, -0.28, band_z - 0.45), (1.92, -0.14, band_z + 0.45))
        # Moulded stone shelf ledges at bottom and top of each niche band
        V.add_box(bm_shelf, (-1.96, -0.35, band_z - 0.50), (1.96, -0.16, band_z - 0.42))
        V.add_box(bm_shelf, (-1.96, -0.34, band_z + 0.42), (1.96, -0.16, band_z + 0.49))
    objs.append(V.bm_to_object(bm_shelf, "oss_shelf", ("M_stone_dark",)))

    bm_bones = bmesh.new()
    for band_z in (0.9, 2.1):
        # Stacked femur bone ends lining the lower shelf of each niche
        for k in range(22):
            bx = -1.76 + 3.52 * k / 21.0
            if abs(bx) < 0.12:
                continue
            for row_z in (band_z - 0.38, band_z - 0.28):
                V.add_box(
                    bm_bones,
                    (bx - 0.032, -0.34, row_z - 0.028),
                    (bx + 0.032, -0.22, row_z + 0.028),
                )
        n = 11
        for i in range(n):
            x = -1.75 + 3.5 * i / (n - 1) + (rng.random() - 0.5) * 0.05
            if abs(x) < 0.14:
                x += 0.18 if x >= 0 else -0.18
            z = band_z + 0.02 + (rng.random() - 0.5) * 0.06
            r = 0.125 + rng.random() * 0.02
            got = bmesh.ops.create_icosphere(bm_bones, subdivisions=1, radius=r)
            for v in got["verts"]:
                v.co = Vector((v.co.x * 0.86 + x, v.co.y * 0.78 - 0.29, v.co.z * 0.88 + z))
            # Maxilla / upper jaw block beneath each cranium
            V.add_box(
                bm_bones,
                (x - r * 0.46, -0.37, z - r * 0.92),
                (x + r * 0.46, -0.26, z - r * 0.25),
            )
    objs.append(V.bm_to_object(bm_bones, "oss_skulls", ("M_bone",)))
    return objs, {"size": [4, 0.6, 4], "origin": "bottom-center"}


def bone_pile(seed=3):
    """Drift of long bones (femurs/tibias with condyle ends) and jawed skulls
    against a wall or corner."""
    import random as _random
    rng = _random.Random(seed)
    bm = bmesh.new()
    # Crossed/scattered long bones with condyle joint knobs at both ends
    for i in range(10):
        x, y = (rng.random() - 0.5) * 0.82, (rng.random() - 0.5) * 0.66
        z = 0.028 + (i % 4) * 0.026
        a = rng.random() * math.pi
        pitch = (rng.random() - 0.5) * 0.18
        xf = Matrix.Translation((x, y, z)) @ Matrix.Rotation(a, 4, "Z") @ Matrix.Rotation(pitch, 4, "Y")
        bm_b = bmesh.new()
        V.add_box(bm_b, (-0.22, -0.018, -0.016), (0.22, 0.018, 0.016))
        for sx in (-0.22, 0.22):
            for sy in (-0.018, 0.018):
                V.add_box(bm_b, (sx - 0.024, sy - 0.016, -0.020), (sx + 0.024, sy + 0.016, 0.020))
        bmesh.ops.transform(bm_b, matrix=xf, verts=bm_b.verts)
        for f in bm_b.faces:
            bm.faces.new([bm.verts.new(v.co) for v in f.verts])
        bm_b.free()
    # Clustered crania with maxilla jaw blocks
    for i in range(8):
        x, y = (rng.random() - 0.5) * 0.78, (rng.random() - 0.5) * 0.62
        r = 0.095 + rng.random() * 0.035
        cz = 0.075 + (i % 3) * 0.045
        got = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
        for v in got["verts"]:
            v.co = Vector((v.co.x * 0.88 + x, v.co.y * 0.92 + y, v.co.z * 0.82 + cz))
        V.add_box(bm, (x - r * 0.45, y - r * 0.85, cz - r * 0.75), (x + r * 0.45, y - r * 0.20, cz - r * 0.15))
    obj = V.bm_to_object(bm, "bone_pile", ("M_bone",))
    return [obj], {"size": [1.2, 1.0, 0.6], "origin": "bottom-center"}


def sarcophagus():
    """Carved Gothic stone sarcophagus chest with stepped plinth, recessed
    blind-arcade panels, pilaster colonnettes, molded cornice, and gabled lid
    with a relief cross (~2.2 m). Solid, climb-proof."""
    objs = []
    bm = bmesh.new()
    # Stepped plinth & upper cornice molding
    V.add_box(bm, (-1.14, -0.49, 0.0), (1.14, 0.49, 0.09))
    V.add_box(bm, (-1.10, -0.45, 0.09), (1.10, 0.45, 0.16))
    V.add_box(bm, (-1.12, -0.47, 0.64), (1.12, 0.47, 0.72))
    # 4 pilaster colonnette stiles framing 3 blind-arcade bays on each long side
    for sx in (-1.02, -0.34, 0.34, 1.02):
        for sy in (-0.43, 0.43):
            V.add_box(bm, (sx - 0.055, sy - 0.025, 0.16), (sx + 0.055, sy + 0.025, 0.64))
    # End pilasters on +/-X faces
    for sx in (-1.07, 1.07):
        for sy in (-0.36, 0.36):
            V.add_box(bm, (sx - 0.025, sy - 0.05, 0.16), (sx + 0.025, sy + 0.05, 0.64))
    objs.append(V.bm_to_object(bm, "sarc_body", ("M_stone_trim",)))

    # Recessed dark stone chest core
    bm_core = bmesh.new()
    V.add_box(bm_core, (-1.05, -0.42, 0.16), (1.05, 0.42, 0.64))
    objs.append(V.bm_to_object(bm_core, "sarc_core", ("M_stone_dark",)))

    # Gabled stone lid with corner acroteria & relief cross along the ridge
    bm = bmesh.new()
    V.add_box(bm, (-1.16, -0.50, 0.72), (1.16, 0.50, 0.77))
    a = [bm.verts.new(p) for p in ((-1.15, -0.48, 0.77), (1.15, -0.48, 0.77), (1.15, 0.48, 0.77), (-1.15, 0.48, 0.77))]
    r0 = bm.verts.new((-1.15, 0.0, 0.98))
    r1 = bm.verts.new((1.15, 0.0, 0.98))
    bm.faces.new((a[0], a[1], r1, r0))
    bm.faces.new((r0, r1, a[2], a[3]))
    bm.faces.new((a[0], r0, a[3]))
    bm.faces.new((a[1], a[2], r1))
    bm.faces.new(list(reversed(a)))
    # Carved relief cross & ridge bolster on the lid
    V.add_box(bm, (-0.92, -0.045, 0.93), (0.92, 0.045, 1.01))
    V.add_box(bm, (0.28, -0.26, 0.86), (0.40, 0.26, 1.01))
    for sx in (-1.12, 1.12):
        for sy in (-0.46, 0.46):
            V.add_box(bm, (sx - 0.04, sy - 0.04, 0.77), (sx + 0.04, sy + 0.04, 0.85))
    objs.append(V.bm_to_object(bm, "sarc_lid", ("M_stone_trim",)))
    return objs, {"size": [2.4, 1.0, 1.02], "origin": "bottom-center"}


def shroud_dead(seed=8):
    """A wrapped body at rest on the floor with cord bindings — undercroft set dressing."""
    bm = bmesh.new()
    L = 1.7
    for t4 in range(5):
        t = t4 / 4.0
        r = 0.16 * (1.0 - 0.55 * abs(t * 2 - 1)) + 0.04
        got = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
        for v in got["verts"]:
            v.co = Vector((v.co.x * 1.6 + (t - 0.5) * L, v.co.y, v.co.z * 0.72 + r * 0.7))
    obj = V.bm_to_object(bm, "shroud_dead", ("M_shroud",))
    bm_rope = bmesh.new()
    for bx, ry, rz in ((-0.56, 0.11, 0.16), (-0.18, 0.18, 0.25), (0.18, 0.17, 0.24), (0.58, 0.11, 0.16)):
        V.add_box(bm_rope, (bx - 0.018, -ry, 0.02), (bx + 0.018, ry, rz))
    ropes = V.bm_to_object(bm_rope, "shroud_ropes", ("M_leather",))
    return [obj, ropes], {"size": [1.9, 0.5, 0.35], "origin": "bottom-center"}


def watcher_base():
    """Octagonal rotating plinth for the Watcher statues with recessed dark
    stone core, carved corner pilasters, and bronze rotation collar."""
    objs = []
    b = V.loft_rings(
        "watcher_base",
        [
            (0.64, 0.0, 8, 0),
            (0.64, 0.09, 8, 0),
            (0.56, 0.13, 8, 0),
            (0.49, 0.13, 8, 0),
            (0.49, 0.25, 8, 0),
            (0.55, 0.28, 8, 0),
            (0.55, 0.34, 8, 0),
        ],
        "M_stone_trim",
    )
    objs.append(b)
    ring = V.loft_rings(
        "watcher_ring",
        [
            (0.57, 0.09, 8, 0),
            (0.57, 0.135, 8, 0),
            (0.50, 0.135, 8, 0),
            (0.50, 0.09, 8, 0),
            (0.57, 0.09, 8, 0),
        ],
        "M_bronze",
        cap_bottom=False,
        cap_top=False,
    )
    objs.append(ring)
    return objs, {"size": [1.3, 1.3, 0.36], "origin": "bottom-center"}


def cobweb():
    """Corner cobweb: a quarter fan of silk with radial threads and concentric rings."""
    bm = bmesh.new()
    import math as _m
    n = 8
    R = 1.05
    bands = (0.0, 0.28, 0.54, 0.78, 1.0)
    for flip in (False, True):
        y_off = 0.002 if not flip else -0.002
        rings = []
        for b_idx, b in enumerate(bands):
            ring = []
            for i in range(n + 1):
                a = _m.pi * 0.5 * i / n
                sag = 1.0 - 0.14 * _m.sin(_m.pi * i / n) * b
                rr = max(0.02, R * b * sag)
                ring.append(bm.verts.new((rr * _m.cos(a), y_off, rr * _m.sin(a))))
            rings.append(ring)
        for b_idx in range(len(bands) - 1):
            r0, r1 = rings[b_idx], rings[b_idx + 1]
            for i in range(n):
                quad = (r0[i], r1[i], r1[i + 1], r0[i + 1])
                if flip:
                    quad = tuple(reversed(quad))
                try:
                    bm.faces.new(quad)
                except ValueError:
                    pass
    obj = V.bm_to_object(bm, "cobweb", ("M_shroud",))
    return [obj], {"size": [1.1, 0.05, 1.1], "origin": "corner"}


def hanging_chain(with_hook=True):
    """A length of iron chain dropping from a vault (~1.6 m) with ceiling
    eyebolt plate and forged J-hook."""
    objs = []
    bm = bmesh.new()
    V.add_cyl(bm, 0.0, 0.0, -0.03, 0.03, 0.075, n=8)
    z = 0.0
    for i in range(9):
        wx = 0.048 if i % 2 else 0.018
        wy = 0.018 if i % 2 else 0.048
        V.add_box(bm, (-wx, -wy, z - 0.11), (wx, wy, z))
        z -= 0.16
    objs.append(V.bm_to_object(bm, "chain", ("M_iron",)))
    if with_hook:
        hook = V.sweep_profile(
            "hook",
            [
                (0.0, 0.0, z + 0.02),
                (0.0, 0.0, z - 0.08),
                (0.045, 0.0, z - 0.16),
                (0.10, 0.0, z - 0.13),
                (0.11, 0.0, z - 0.05),
            ],
            V.circle_profile(0.018, 8),
            "M_iron",
            up_hint=Vector((0, 1, 0)),
        )
        objs.append(hook)
    return objs, {"size": [0.24, 0.2, 1.7], "origin": "top-center"}


def door_leaf():
    """A shut double door of iron-banded oak for a 1.9-wide portal opening,
    with plank stiles, central astragal, wrought-iron strap hinges with rivets,
    ring knockers, and a pointed-arch oak & wrought-iron tympanum."""
    objs = []
    bm = bmesh.new()
    arch = V.pointed_arch(1.94, 1.1, 16, 2.1)
    for sx in (-1, 1):
        x0 = 0.015 * sx
        x1 = sx * 0.92
        lo, hi = (min(x0, x1), max(x0, x1))
        V.add_box(bm, (lo, -0.055, 0.02), (hi, 0.055, 2.12))
        # Vertical plank muntin stiles extending up to the pointed arch contour
        for px, z_top in ((0.08, 3.82), (0.34, 3.60), (0.60, 3.24), (0.86, 2.58)):
            V.add_box(bm, (sx * px - 0.022, -0.072, 0.04), (sx * px + 0.022, 0.072, z_top))
    # Pointed-arch oak upper leaves filling the portal arch (z = 2.10..3.94)
    pts2d = [(0.96, 2.08)] + list(reversed(arch)) + [(-0.96, 2.08)]
    vf = [bm.verts.new((px, -0.055, pz)) for (px, pz) in pts2d]
    vb = [bm.verts.new((px, 0.055, pz)) for (px, pz) in pts2d]
    bm.faces.new(vf)
    bm.faces.new(list(reversed(vb)))
    n_p = len(pts2d)
    for i in range(n_p):
        j = (i + 1) % n_p
        bm.faces.new((vf[i], vf[j], vb[j], vb[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    # Central meeting astragal & transom lintel beam
    V.add_box(bm, (-0.035, -0.082, 0.02), (0.035, 0.082, 3.90))
    V.add_box(bm, (-0.94, -0.088, 2.04), (0.94, 0.088, 2.16))
    V.add_box(bm, (-0.82, -0.086, 2.66), (0.82, 0.086, 2.76))
    objs.append(V.bm_to_object(bm, "door_oak", ("M_wood",)))

    bm = bmesh.new()
    for z, hw in ((0.46, 0.91), (1.38, 0.91), (2.10, 0.91), (2.71, 0.78), (3.28, 0.54)):
        V.add_box(bm, (-hw, -0.092, z - 0.042), (hw, 0.092, z + 0.042))
        for rx in (-0.76, -0.50, -0.24, 0.24, 0.50, 0.76):
            if abs(rx) < hw - 0.05:
                V.add_box(bm, (rx - 0.018, -0.104, z - 0.018), (rx + 0.018, 0.104, z + 0.018))
    # Central iron spine & tympanum cross-brace
    V.add_box(bm, (-0.042, -0.096, 2.10), (0.042, 0.096, 3.88))
    for sx in (-1, 1):
        V.add_box(bm, (sx * 0.90 - 0.045, -0.086, 0.08), (sx * 0.90 + 0.045, 0.086, 2.12))
        # Escutcheon plates & ring knockers on both faces
        V.add_box(bm, (sx * 0.22 - 0.045, -0.094, 1.12), (sx * 0.22 + 0.045, 0.094, 1.24))
        V.add_box(bm, (sx * 0.22 - 0.065, -0.105, 1.00), (sx * 0.22 + 0.065, 0.105, 1.13))
    objs.append(V.bm_to_object(bm, "door_bands", ("M_iron",)))

    # Swept wrought-iron perimeter band along the pointed arch
    apath = [(x * 0.96, 0.0, 2.1 + (y - 2.1) * 0.96) for (x, y) in arch]
    objs.append(V.sweep_profile("door_arch_iron", apath,
                                V.chamfer_rect_profile(0.075, 0.18, 0.016),
                                "M_iron", up_hint=Vector((0, 1, 0))))
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
    # Closed 3D filigree gold trim rings around base, belly, and flared spout
    objs.append(V.loft_rings("foot_band", [
        (0.050, 0.016, n, 0),
        (0.058, 0.016, n, 0),
        (0.070, 0.028, n, 0),
        (0.062, 0.028, n, 0),
        (0.050, 0.016, n, 0),
    ], "M_gold", cap_bottom=False, cap_top=False))
    objs.append(V.loft_rings("belly_band", [
        (0.078, 0.084, n, 0),
        (0.085, 0.084, n, 0),
        (0.086, 0.104, n, 0),
        (0.079, 0.104, n, 0),
        (0.078, 0.084, n, 0),
    ], "M_gold", cap_bottom=False, cap_top=False))
    objs.append(V.loft_rings("neck_lip", [
        (0.025, 0.168, 14, 0),
        (0.032, 0.168, 14, 0),
        (0.028, 0.195, 14, 0),
        (0.037, 0.222, 14, 0.3),
        (0.039, 0.235, 14, 0),
        (0.031, 0.235, 14, 0),
        (0.023, 0.195, 14, 0),
        (0.025, 0.168, 14, 0),
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
