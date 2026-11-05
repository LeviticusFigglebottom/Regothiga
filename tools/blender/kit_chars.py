"""Character kit: robed figure parts and Dark Souls weapons/shields assembled
into node-rigs in Godot. All characters share the robed/armored silhouette
family (DECISIONS D-005).

Origins: body parts at their joint. Robe body origin at floor between feet;
sleeves at the shoulder joint (arm hangs -Z); weapons at the grip (blade +Z).
"""
import math
import random
import bmesh
from mathutils import Vector

import vglib as V


def _hex_blade(name, z0, z1, z_tip, w0, w1, t0, t1, fuller_z_end=0.0):
    """Build a 6-sided diamond/hexagonal cross-section sword blade with central
    ridge and beveled edges so light catches the fuller and bevels cleanly."""
    bm = bmesh.new()
    steps = 6
    rings = []
    for s in range(steps + 1):
        u = s / steps
        z = z0 + (z1 - z0) * u
        w = w0 * (1.0 - u) + w1 * u
        t = t0 * (1.0 - u) + t1 * u
        # 6-point hexagonal/diamond blade profile:
        # left edge, front-left bevel, front ridge, right edge, back-right bevel, back ridge
        fw = w * 0.34
        ft = t * (0.72 if z < fuller_z_end else 1.0)
        pts = [
            (-w, 0.0, z),
            (-fw, -ft, z),
            (fw, -ft, z),
            (w, 0.0, z),
            (fw, ft, z),
            (-fw, ft, z),
        ]
        ring = [bm.verts.new(p) for p in pts]
        rings.append(ring)
    n = 6
    for s in range(steps):
        for i in range(n):
            bm.faces.new((rings[s][i], rings[s][(i + 1) % n],
                          rings[s + 1][(i + 1) % n], rings[s + 1][i]))
    bm.faces.new(list(reversed(rings[0])))
    tip = bm.verts.new((0.0, 0.0, z_tip))
    for i in range(n):
        bm.faces.new((rings[-1][i], rings[-1][(i + 1) % n], tip))
    return V.bm_to_object(bm, name, ("M_steel",))


def _robe_body(name, height, girth, mat, hood=True, hood_lean=0.09):
    """Humanoid read: spread hem, drawn waist, carried chest, squared
    shoulders, cinched neck, deep hood. (Painted-fantasy silhouette pass.)"""
    n = 16
    h = height
    rings = [
        (girth * 1.34, 0.0, n, 0),          # hem
        (girth * 1.12, h * 0.06, n, 0),
        (girth * 0.92, h * 0.26, n, 0),     # knee-fall
        (girth * 0.78, h * 0.46, n, 0),
        (girth * 0.70, h * 0.55, n, 0),     # waist
        (girth * 0.88, h * 0.64, n, 0),     # ribcage
        (girth * 0.98, h * 0.72, n, 0),     # chest
        (girth * 1.02, h * 0.775, n, 0),    # shoulder shelf
        (girth * 0.86, h * 0.80, n, 0),
    ]
    if hood:
        rings += [
            (girth * 0.46, h * 0.835, n, 0),  # neck
            (girth * 0.60, h * 0.885, n, 0),  # hood bulk
            (girth * 0.50, h * 0.945, n, 0),
            (girth * 0.30, h * 0.99, n, 0),   # crown
            (girth * 0.08, h * 1.045, n, 0),  # peak
        ]
    else:
        rings += [(girth * 0.5, h * 0.82, n, 0), (girth * 0.2, h * 0.86, n, 0)]
    obj = V.loft_rings(name, rings, mat)
    if hood:
        me = obj.data
        zs = sorted({round(v.co.z, 4) for v in me.vertices})
        for v in me.vertices:
            if round(v.co.z, 4) in zs[-2:]:
                v.co.y += hood_lean * height / 1.8
            if v.co.z > h * 0.84 and v.co.y > girth * 0.1:
                v.co.y *= 0.35   # carve the face shadow
    return obj


def char_latecomer():
    """The player: hooded pilgrim. Slate robe, rope belt, satchel."""
    objs = []
    body = _robe_body("robe", 1.62, 0.30, "M_robe")
    objs.append(body)
    belt = V.loft_rings("belt", [(0.255, 0.80, 14, 0), (0.27, 0.84, 14, 0), (0.25, 0.88, 14, 0)], "M_leather")
    objs.append(belt)
    bm = bmesh.new()
    V.add_box(bm, (-0.14, 0.16, 0.72), (0.10, 0.34, 0.95))
    objs.append(V.bm_to_object(bm, "satchel", ("M_leather",)))
    return objs, {"size": [0.8, 0.8, 1.75], "origin": "bottom-center"}


def char_sleeve(side):
    """Arm with an elbow: upper arm drops, forearm angles forward, cuff
    flares, hand closes. Origin at shoulder, hanging along -Z (blender)."""
    n = 12
    objs = []
    upper = V.loft_rings(f"sleeve_{side}", [(0.088, 0.0, n, 0), (0.078, -0.13, n, 0),
                                            (0.072, -0.24, n, 0)], "M_robe")
    objs.append(upper)
    pauld = V.loft_rings("pauldron", [(0.115, 0.03, n, 0), (0.125, -0.03, n, 0),
                                      (0.09, -0.1, n, 0)], "M_plate_dark")
    objs.append(pauld)
    fore_pts = []
    for (r, t) in ((0.07, 0.0), (0.082, 0.45), (0.105, 0.85), (0.112, 1.0)):
        z = -0.24 - 0.22 * t
        y = 0.10 * t
        fore_pts.append((r, y, z))
    bm = bmesh.new()
    prev = None
    for (r, y, z) in fore_pts:
        ring = []
        for i in range(n):
            a = 2 * math.pi * i / n
            ring.append(bm.verts.new((r * math.cos(a), y + r * math.sin(a) * 0.9, z)))
        if prev:
            for i in range(n):
                bm.faces.new((prev[i], prev[(i + 1) % n], ring[(i + 1) % n], ring[i]))
        prev = ring
    bm.verts.ensure_lookup_table()
    bm.faces.new(reversed(bm.verts[:n]))
    bm.faces.new(prev)
    objs.append(V.bm_to_object(bm, "forearm", ("M_robe",)))
    hand = V.loft_rings("hand", [(0.048, -0.46, n, 0), (0.052, -0.52, n, 0), (0.02, -0.575, n, 0)], "M_wax")
    hand.location = (0, 0.105, 0)
    objs.append(hand)
    return objs, {"size": [0.26, 0.3, 0.62], "origin": "shoulder"}


def sword_cloister():
    """Cloistersword: Dark Souls knight arming/longsword with hexagonal fullered
    blade, gothic quillons with flared terminals, ribbed cord grip, and wheel pommel.
    Origin at grip center, blade +Z."""
    objs = []
    objs.append(_hex_blade("blade", 0.12, 0.86, 1.00, 0.046, 0.028, 0.009, 0.005, fuller_z_end=0.68))
    # Swept gothic crossguard with flared quillon finials + rain-guard chappe
    q_path = [(-0.175, 0.0, 0.118), (-0.11, 0.0, 0.112), (0.0, 0.0, 0.112),
              (0.11, 0.0, 0.112), (0.175, 0.0, 0.118)]
    objs.append(V.sweep_profile("cross", q_path, V.chamfer_rect_profile(0.024, 0.028, 0.005), "M_iron"))
    bm_rg = bmesh.new()
    V.add_box(bm_rg, (-0.032, -0.015, 0.11), (0.032, 0.015, 0.155))
    objs.append(V.bm_to_object(bm_rg, "rainguard", ("M_brass",)))
    # Ribbed cord-wrapped leather grip
    grip_rings = []
    for i in range(9):
        t = i / 8.0
        z = -0.095 + 0.195 * t
        r = 0.019 + (0.0025 if i % 2 == 1 else 0.0) + 0.002 * math.sin(math.pi * t)
        grip_rings.append((r, z, 12, 0))
    objs.append(V.loft_rings("grip", grip_rings, "M_leather"))
    # Faceted wheel pommel with brass boss
    objs.append(V.loft_rings("pommel", [
        (0.010, -0.150, 14, 0),
        (0.038, -0.132, 14, 0),
        (0.040, -0.112, 14, 0),
        (0.016, -0.092, 14, 0),
    ], "M_iron"))
    objs.append(V.loft_rings("pommel_boss", [
        (0.022, -0.135, 12, 0),
        (0.022, -0.110, 12, 0),
    ], "M_brass"))
    return objs, {"size": [0.35, 0.05, 1.15], "origin": "grip"}


def maul_sexton():
    """Sexton's Maul: gravedigger's great warhammer with iron-banded stone/steel
    head, striking faces, and reinforced ash haft. Origin at grip, head +Z."""
    objs = []
    objs.append(V.loft_rings("haft", [
        (0.028, -0.52, 12, 0), (0.024, -0.45, 12, 0),
        (0.027, 0.20, 12, 0), (0.032, 0.72, 12, 0),
        (0.014, 1.12, 12, 0),
    ], "M_wood"))
    # Iron langets & grip bands
    objs.append(V.loft_rings("ferrule", [(0.036, 0.62, 12, 0), (0.038, 0.73, 12, 0)], "M_iron"))
    bm = bmesh.new()
    V.add_box(bm, (-0.115, -0.115, 0.73), (0.115, 0.115, 1.01))
    objs.append(V.bm_to_object(bm, "head", ("M_stone_dark",)))
    bm_iron = bmesh.new()
    V.add_box(bm_iron, (-0.135, -0.135, 0.70), (0.135, 0.135, 0.76))
    V.add_box(bm_iron, (-0.135, -0.135, 0.98), (0.135, 0.135, 1.03))
    V.add_box(bm_iron, (-0.04, -0.142, 0.75), (0.04, 0.142, 0.99))
    objs.append(V.bm_to_object(bm_iron, "bands", ("M_iron",)))
    return objs, {"size": [0.3, 0.3, 1.55], "origin": "grip"}


def halberd_ward():
    """Ward's halberd: Lothric/Silver Knight poleaxe — ash haft with iron
    langets, crescent axe blade, rear armor-piercing fluke, and quadrangular spike."""
    objs = []
    objs.append(V.loft_rings("haft", [
        (0.028, -0.92, 12, 0), (0.022, -0.84, 12, 0),
        (0.025, 0.65, 12, 0), (0.028, 1.06, 12, 0)
    ], "M_wood"))
    objs.append(V.loft_rings("socket", [(0.034, 0.68, 12, 0), (0.032, 1.08, 12, 0)], "M_iron"))
    bm = bmesh.new()
    # Crescent axe blade + rear fluke beak
    pts = [
        (0.02, 0.0, 0.72), (0.23, 0.0, 0.78), (0.28, 0.0, 0.95),
        (0.24, 0.0, 1.14), (0.02, 0.0, 1.06)
    ]
    vs = [bm.verts.new(p) for p in pts]
    bm.faces.new(vs)
    fluke = [
        (-0.02, 0.0, 0.84), (-0.16, 0.0, 0.88),
        (-0.20, 0.0, 0.82), (-0.02, 0.0, 0.98)
    ]
    bm.faces.new([bm.verts.new(p) for p in fluke])
    bmesh.ops.solidify(bm, geom=list(bm.faces) + list(bm.verts) + list(bm.edges), thickness=0.014)
    objs.append(V.bm_to_object(bm, "axehead", ("M_steel",)))
    spike = V.loft_rings("spike", [(0.032, 1.05, 8, 0), (0.018, 1.24, 8, 0), (0.003, 1.40, 8, 0)], "M_steel")
    objs.append(spike)
    return objs, {"size": [0.5, 0.1, 2.3], "origin": "grip"}


def shield_kite():
    """Heraldic Gothic kite shield: curved timber/plate core, beveled steel rim,
    flush brass cross inlay, and low-profile embossed sun-boss. Origin at arm strap."""
    bm = bmesh.new()
    # Build a smoothly curved grid for the kite shield body (+Y is outer front face)
    z_rows = [-0.52, -0.40, -0.24, -0.06, 0.10, 0.22, 0.29]
    half_w = [0.00, 0.105, 0.168, 0.195, 0.185, 0.145, 0.00]
    nx = 6

    def _shield_y(x):
        return 0.048 * max(0.0, 1.0 - (x / 0.20) ** 2)

    rings_f = []
    rings_b = []
    thick = 0.018
    for r_i, (z, hw) in enumerate(zip(z_rows, half_w)):
        if hw < 1e-4:
            vf = [bm.verts.new((0.0, _shield_y(0.0), z)) for _ in range(nx + 1)]
            vb = [bm.verts.new((0.0, _shield_y(0.0) - thick, z)) for _ in range(nx + 1)]
        else:
            vf = []
            vb = []
            for ix in range(nx + 1):
                x = -hw + 2.0 * hw * (ix / float(nx))
                y = _shield_y(x)
                vf.append(bm.verts.new((x, y, z)))
                vb.append(bm.verts.new((x, y - thick, z)))
        rings_f.append(vf)
        rings_b.append(vb)

    for r_i in range(len(z_rows) - 1):
        for ix in range(nx):
            try:
                bm.faces.new((rings_f[r_i][ix], rings_f[r_i][ix + 1], rings_f[r_i + 1][ix + 1], rings_f[r_i + 1][ix]))
            except ValueError:
                pass
            try:
                bm.faces.new((rings_b[r_i][ix + 1], rings_b[r_i][ix], rings_b[r_i + 1][ix], rings_b[r_i + 1][ix + 1]))
            except ValueError:
                pass
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.002)
    shield = V.bm_to_object(bm, "shield", ("M_plate_dark",))

    # Beveled steel border rim hugging the exact curved perimeter
    perim_xz = [
        (0.0, -0.52), (0.105, -0.40), (0.168, -0.24), (0.195, -0.06),
        (0.185, 0.10), (0.145, 0.22), (0.0, 0.29), (-0.145, 0.22),
        (-0.185, 0.10), (-0.195, -0.06), (-0.168, -0.24), (-0.105, -0.40),
        (0.0, -0.52),
    ]
    rim_pts = [(x, _shield_y(x) - 0.005, z) for (x, z) in perim_xz]
    rim = V.sweep_profile("rim", rim_pts, V.chamfer_rect_profile(0.022, 0.026, 0.005), "M_steel")

    # Flush curved heraldic brass cross + low-profile central umbo on outer (+Y) face
    vert_arm = [(0.0, _shield_y(0.0) + 0.003, z) for z in (-0.38, -0.20, 0.0, 0.14, 0.24)]
    horiz_arm = [(x, _shield_y(x) + 0.003, 0.02) for x in (-0.15, -0.075, 0.0, 0.075, 0.15)]
    cross_v = V.sweep_profile("cross_v", vert_arm, V.chamfer_rect_profile(0.024, 0.008, 0.002), "M_brass")
    cross_h = V.sweep_profile("cross_h", horiz_arm, V.chamfer_rect_profile(0.024, 0.008, 0.002), "M_brass")

    boss = V.loft_rings(
        "boss_sun",
        [
            (0.054, 0.0, 16, 0),
            (0.040, 0.008, 16, 0),
            (0.016, 0.015, 16, 0),
            (0.002, 0.018, 16, 0),
        ],
        "M_brass",
    )
    boss.rotation_euler = (-math.pi / 2, 0, 0)
    boss.location = (0, _shield_y(0.0) + 0.002, 0.02)
    V.apply_all(boss)

    # Rear leather arm-straps (enarmes) recessed on the concave inner (-Y) face
    bm_s = bmesh.new()
    V.add_box(bm_s, (-0.06, 0.004, -0.08), (0.06, 0.024, -0.03))
    V.add_box(bm_s, (-0.06, 0.004, 0.05), (0.06, 0.024, 0.10))
    straps = V.bm_to_object(bm_s, "enarmes", ("M_leather",))
    return [shield, rim, cross_v, cross_h, boss, straps], {"size": [0.42, 0.14, 0.85], "origin": "strap"}


def helm_ward():
    """Great helm with sight slit for the Cloister Ward. Origin at neck."""
    n = 16
    helm = V.loft_rings("helm", [(0.115, 0.0, n, 0), (0.125, 0.10, n, 0), (0.125, 0.22, n, 0),
                                 (0.10, 0.30, n, 0), (0.02, 0.34, n, 0)], "M_plate_dark")
    objs = [helm]
    for sgn in (-1, 1):
        horn = V.sweep_profile("horn", [(sgn * 0.10, 0, 0.24), (sgn * 0.2, -0.02, 0.34), (sgn * 0.26, -0.06, 0.46)],
                               V.circle_profile(0.022, 10), "M_iron")
        objs.append(horn)
    return objs, {"size": [0.55, 0.3, 0.5], "origin": "neck"}


def char_ward():
    """Cloister Ward body: wraith-robe + cuirass + pauldrons."""
    objs = []
    body = _robe_body("ward_robe", 1.86, 0.34, "M_wraith")
    objs.append(body)
    cuir = V.loft_rings("cuirass", [(0.30, 1.06, 16, 0), (0.34, 1.26, 16, 0), (0.30, 1.44, 16, 0)], "M_plate_dark")
    objs.append(cuir)
    for sgn in (-1, 1):
        p = V.loft_rings("pauldron", [(0.11, 0.0, 12, 0), (0.13, 0.07, 12, 0), (0.07, 0.16, 12, 0)], "M_plate_dark")
        p.location = (sgn * 0.30, 0, 1.36)
        objs.append(p)
    return objs, {"size": [0.9, 0.9, 2.0], "origin": "bottom-center"}


def char_penitent():
    """Waxbound Penitent: a votive burned into a person-shape. Slumped,
    dripping, a dead wick where the face was."""
    rng = random.Random(77)
    objs = []
    n = 16
    rings = []
    profile = [(0.42, 0.0), (0.40, 0.06), (0.30, 0.35), (0.26, 0.7), (0.28, 0.95),
               (0.30, 1.15), (0.22, 1.32), (0.12, 1.45), (0.05, 1.5)]
    for (r, z) in profile:
        rings.append((r, z, n, 0))
    body = V.loft_rings("penitent", rings, "M_wax")
    me = body.data
    for v in me.vertices:
        w = V.value_noise(v.co * 2.0 + Vector((7, 7, 7)))
        v.co.x += (w - 0.5) * 0.12 * (0.3 + v.co.z)
        v.co.y += (V.value_noise(v.co * 1.7) - 0.5) * 0.1 * (0.3 + v.co.z)
        if v.co.z > 1.2:
            v.co.y += 0.08
    objs.append(body)
    for i in range(10):
        a = rng.uniform(0, 2 * math.pi)
        z = rng.choice((0.15, 0.2, 1.0, 1.1))
        r0 = 0.31 if z > 0.5 else 0.41
        drip = V.loft_rings("drip", [(0.028, z, 8, 0), (0.012, z - rng.uniform(0.1, 0.3), 8, 0)], "M_wax")
        drip.location = (r0 * math.cos(a), r0 * math.sin(a), 0)
        objs.append(drip)
    return objs, {"size": [0.9, 0.9, 1.6], "origin": "bottom-center"}


def penitent_arm():
    """Fused arm-club for the Penitent, origin at shoulder, hangs -Z."""
    n = 12
    arm = V.loft_rings("pen_arm", [(0.085, 0.0, n, 0), (0.11, -0.28, n, 0),
                                   (0.13, -0.5, n, 0), (0.06, -0.62, n, 0)], "M_wax")
    return [arm], {"size": [0.3, 0.3, 0.65], "origin": "shoulder"}


def char_aveline():
    """Sister Aveline: pale habit, wax-dripped candle crown (lit in glory)."""
    objs = []
    body = _robe_body("aveline", 1.66, 0.29, "M_habit", hood=True, hood_lean=0.04)
    objs.append(body)
    crown = V.loft_rings("crown", [(0.145, 1.52, 14, 0), (0.15, 1.60, 14, 0)], "M_wax")
    objs.append(crown)
    rng = random.Random(5)
    for i in range(6):
        a = 2 * math.pi * i / 6
        h = rng.uniform(0.07, 0.16)
        c = V.loft_rings("crown_candle", [(0.022, 1.58, 10, 0), (0.02, 1.58 + h, 10, 0)], "M_wax")
        c.location = (0.13 * math.cos(a), 0.13 * math.sin(a), 0)
        objs.append(c)
        fl = V.loft_rings("crown_flame", [(0.012, 0.0, 8, 0), (0.02, 0.02, 8, 0.3), (0.002, 0.05, 8, 0.6)], "M_flame")
        fl.location = (0.13 * math.cos(a), 0.13 * math.sin(a), 1.585 + h)
        objs.append(fl)
    bm = bmesh.new()
    V.add_box(bm, (-0.14, 0.20, 0.55), (0.14, 0.25, 1.05))
    objs.append(V.bm_to_object(bm, "apron", ("M_leather",)))
    return objs, {"size": [0.8, 0.8, 1.85], "origin": "bottom-center"}


def char_bellkeeper():
    """The Bellkeeper: a tower of a man, hooded, one arm dragging the great
    bell (bell_great is a separate piece). Scale ~2.7 m."""
    objs = []
    body = _robe_body("bellkeeper", 2.7, 0.52, "M_robe_boss", hood=True, hood_lean=0.16)
    objs.append(body)
    harness = V.loft_rings("harness", [(0.50, 1.55, 16, 0), (0.53, 1.66, 16, 0), (0.49, 1.77, 16, 0)], "M_leather")
    objs.append(harness)
    cens = V.loft_rings("censer", [(0.02, 0.9, 12, 0), (0.07, 0.98, 12, 0), (0.05, 1.08, 12, 0), (0.02, 1.12, 12, 0)], "M_gold")
    cens.location = (0.45, 0.1, 0)
    objs.append(cens)
    return objs, {"size": [1.4, 1.4, 2.9], "origin": "bottom-center"}


def bellkeeper_arm():
    """Massive sleeve arm for the Bellkeeper. Origin shoulder, hangs -Z."""
    n = 14
    arm = V.loft_rings("bk_arm", [(0.16, 0.0, n, 0), (0.14, -0.35, n, 0),
                                  (0.19, -0.7, n, 0), (0.23, -0.95, n, 0)], "M_robe_boss")
    fist = V.loft_rings("bk_fist", [(0.1, -0.95, n, 0), (0.11, -1.1, n, 0), (0.04, -1.2, n, 0)], "M_wax")
    return [arm, fist], {"size": [0.5, 0.5, 1.25], "origin": "shoulder"}


def pell():
    """Training pell for the combat sandbox: heavy timber post in a braced
    cross-foot base, rope-lashed padded leather torso sack, iron-shod cross-spar
    arms, practice target buckler, and battered iron kettle-helm crown."""
    objs = []
    # Main vertical oak post
    objs.append(V.loft_rings("post", [(0.095, 0.0, 12, 0), (0.088, 0.85, 12, 0), (0.082, 1.82, 12, 0)], "M_wood"))
    # Crossed timber base sleepers + diagonal knee braces + cross-spar arms
    bm_wood = bmesh.new()
    V.add_box(bm_wood, (-0.42, -0.07, 0.0), (0.42, 0.07, 0.10))
    V.add_box(bm_wood, (-0.07, -0.42, 0.0), (0.07, 0.42, 0.10))
    for sx in (-1, 1):
        V.add_box(bm_wood, (sx * 0.10, -0.045, 0.10), (sx * 0.28, 0.045, 0.34))
    V.add_box(bm_wood, (-0.50, -0.055, 1.32), (0.50, 0.055, 1.43))
    objs.append(V.bm_to_object(bm_wood, "arms", ("M_wood",)))

    # Quilted/padded leather & burlap torso target sack
    objs.append(V.loft_rings(
        "torso",
        [
            (0.11, 0.84, 14, 0),
            (0.19, 0.92, 14, 0),
            (0.22, 1.15, 14, 0),
            (0.20, 1.30, 14, 0),
            (0.22, 1.46, 14, 0),
            (0.18, 1.60, 14, 0),
            (0.09, 1.68, 14, 0),
        ],
        "M_leather",
    ))
    # Hemp rope lashing bands cinching the sack
    for z_rope, r_rope in ((0.94, 0.202), (1.28, 0.212), (1.56, 0.195)):
        objs.append(V.loft_rings("rope_band", [(r_rope, z_rope, 14, 0), (r_rope, z_rope + 0.032, 14, 0)],
                                 "M_bone", cap_bottom=False, cap_top=False))

    # Iron base collar, spar end-ferrules, and battered kettle-helm on top of the post
    bm_iron = bmesh.new()
    V.add_box(bm_iron, (-0.11, -0.11, 0.10), (0.11, 0.11, 0.18))
    for sx in (-0.51, 0.44):
        V.add_box(bm_iron, (sx, -0.065, 1.31), (sx + 0.07, 0.065, 1.44))
    objs.append(V.bm_to_object(bm_iron, "pell_iron", ("M_iron",)))

    helm = V.loft_rings(
        "pell_helm",
        [
            (0.17, 1.74, 14, 0),
            (0.13, 1.78, 14, 0),
            (0.12, 1.88, 14, 0),
            (0.08, 1.94, 14, 0),
            (0.01, 1.96, 14, 0),
        ],
        "M_iron",
    )
    objs.append(helm)

    # Practice target buckler hung on the left cross-arm (-X, +Y front)
    buckler = V.loft_rings(
        "pell_buckler",
        [(0.18, 0.0, 14, 0), (0.18, 0.025, 14, 0), (0.06, 0.05, 14, 0), (0.01, 0.065, 14, 0)],
        "M_plate_dark",
    )
    buckler.rotation_euler = (-math.pi / 2, 0, 0)
    buckler.location = (-0.34, 0.065, 1.36)
    objs.append(buckler)
    return objs, {"size": [1.02, 0.84, 1.96], "origin": "bottom-center"}


def crook_warden():
    """Cage-warden's crook: a long haft curling into an iron shepherd's hook —
    the tool that dragged larks (and worse) back to their cages. Origin grip."""
    objs = [V.loft_rings("haft", [(0.02, -0.85, 12, 0), (0.024, 1.0, 12, 0)], "M_wood")]
    pts = [(0, 0, 0.96), (-0.02, 0, 1.18), (-0.10, 0, 1.30), (-0.20, 0, 1.32),
           (-0.27, 0, 1.24), (-0.28, 0, 1.12), (-0.22, 0, 1.05)]
    objs.append(V.sweep_profile("hook", pts, V.circle_profile(0.022, 10), "M_iron",
                                up_hint=Vector((0, 1, 0))))
    return objs, {"size": [0.5, 0.1, 2.2], "origin": "grip"}


def crook_great():
    """The Larkwarden's great crook: a two-hand cage-hook, gilt at the curl."""
    objs = [V.loft_rings("haft_g", [(0.03, -1.1, 12, 0), (0.035, 1.35, 12, 0)], "M_wood")]
    pts = [(0, 0, 1.30), (-0.03, 0, 1.60), (-0.16, 0, 1.78), (-0.34, 0, 1.80),
           (-0.45, 0, 1.68), (-0.46, 0, 1.50), (-0.36, 0, 1.40)]
    objs.append(V.sweep_profile("hook_g", pts, V.circle_profile(0.035, 10), "M_gold",
                                up_hint=Vector((0, 1, 0))))
    objs.append(V.loft_rings("ferrule", [(0.045, 1.3, 12, 0), (0.04, 1.42, 12, 0)], "M_gold"))
    return objs, {"size": [0.9, 0.14, 3.0], "origin": "grip"}


def oar_glaive():
    """The Ferryman's oar-glaive: a pole arm ending in a broad steel-shod
    blade — half oar, half executioner's sweep. Origin at grip."""
    objs = [V.loft_rings("oar_haft", [(0.028, -1.15, 12, 0), (0.032, 1.2, 12, 0)], "M_wood")]
    bm = bmesh.new()
    pts = [(-0.04, 0.0, 1.15), (0.24, 0.0, 1.45), (0.3, 0.0, 1.95),
           (0.16, 0.0, 2.35), (-0.06, 0.0, 2.4)]
    vs = [bm.verts.new(p) for p in pts]
    bm.faces.new(vs)
    bmesh.ops.solidify(bm, geom=list(bm.faces) + list(bm.verts) + list(bm.edges), thickness=0.026)
    objs.append(V.bm_to_object(bm, "oar_blade", ("M_steel",)))
    return objs, {"size": [0.7, 0.12, 3.6], "origin": "grip"}


def spear_fen():
    """Fen-Ward Spear: marsh patrol partisan/pike. Origin at grip, point +Z."""
    objs = []
    objs.append(V.loft_rings("shaft", [(0.02, -0.6, 12, 0), (0.023, 1.72, 12, 0)], "M_wood"))
    objs.append(V.loft_rings("collar", [(0.032, 1.64, 12, 0), (0.026, 1.78, 12, 0)], "M_iron"))
    objs.append(V.loft_rings("butt", [(0.032, -0.66, 12, 0), (0.022, -0.58, 12, 0)], "M_iron"))
    objs.append(_hex_blade("leaf", 1.78, 2.12, 2.32, 0.052, 0.028, 0.008, 0.004, fuller_z_end=2.0))
    return objs, {"size": [0.11, 0.05, 2.96], "origin": "grip"}


def greatsword_pilgrim():
    """Pilgrim's Greatsword: Dark Souls Zweihander / Cathedral Greatsword with
    hexagonal fullered blade, parrying lugs above a leather-wrapped ricasso,
    swept gothic crossguard, sun medallion, and faceted pommel. Origin at grip."""
    objs = []
    objs.append(_hex_blade("blade", 0.34, 1.34, 1.54, 0.076, 0.048, 0.014, 0.008, fuller_z_end=1.10))
    # Leather-wrapped ricasso + Zweihander parrying hooks (parierdolche)
    objs.append(V.loft_rings("ricasso", [(0.038, 0.19, 12, 0), (0.036, 0.35, 12, 0)], "M_leather"))
    lug_path = [(-0.14, 0.0, 0.39), (-0.06, 0.0, 0.35), (0.06, 0.0, 0.35), (0.14, 0.0, 0.39)]
    objs.append(V.sweep_profile("lugs", lug_path, V.chamfer_rect_profile(0.018, 0.022, 0.004), "M_iron"))
    # Wide Gothic crossguard
    q_path = [(-0.27, 0.0, 0.175), (-0.15, 0.0, 0.155), (0.0, 0.0, 0.155),
              (0.15, 0.0, 0.155), (0.27, 0.0, 0.175)]
    objs.append(V.sweep_profile("cross", q_path, V.chamfer_rect_profile(0.028, 0.036, 0.006), "M_iron"))
    objs.append(V.loft_rings("sun_disc", [
        (0.015, 0.145, 14, 0), (0.054, 0.160, 14, 0), (0.015, 0.175, 14, 0)
    ], "M_gold"))
    # Two-handed cord grip with central waist ring
    objs.append(V.loft_rings("grip", [
        (0.023, -0.26, 12, 0), (0.026, -0.14, 12, 0),
        (0.030, -0.07, 12, 0), (0.025, 0.0, 12, 0),
        (0.026, 0.13, 12, 0),
    ], "M_leather"))
    objs.append(V.loft_rings("pommel", [
        (0.014, -0.34, 14, 0), (0.048, -0.30, 14, 0), (0.016, -0.26, 14, 0)
    ], "M_iron"))
    return objs, {"size": [0.54, 0.05, 1.88], "origin": "grip"}


def bow_lark():
    """Larkbow: a birdkeeper's recurve of pale ash. Origin at grip."""
    objs = []
    path = []
    n = 18
    for i in range(n + 1):
        k = i / float(n) * 2.0 - 1.0
        z = k * 0.78
        y = 0.17 * (1.0 - k * k)
        if abs(k) > 0.82:
            y += 0.05 * (abs(k) - 0.82) / 0.18
        path.append((0.0, y, z))
    prof = V.chamfer_rect_profile(0.021, 0.03, 0.006)
    objs.append(V.sweep_profile("stave", path, prof, "M_wood", up_hint=Vector((1, 0, 0))))
    bm = bmesh.new()
    ty = path[0][1] - 0.005
    V.add_box(bm, (-0.0035, ty - 0.0035, -0.775), (0.0035, ty + 0.0035, 0.775))
    objs.append(V.bm_to_object(bm, "string", ("M_bone",)))
    objs.append(V.loft_rings("wrap", [(0.028, -0.09, 12, 0), (0.03, 0.09, 12, 0)], "M_leather"))
    for sgn in (-1, 1):
        objs.append(V.loft_rings("nock", [(0.012, sgn * 0.76, 10, 0), (0.008, sgn * 0.8, 10, 0)], "M_bone"))
    return objs, {"size": [0.08, 0.4, 1.62], "origin": "grip"}


BUILDERS = {
    "char_latecomer": char_latecomer,
    "char_sleeve_l": lambda: char_sleeve("l"),
    "char_sleeve_r": lambda: char_sleeve("r"),
    "sword_cloister": sword_cloister,
    "maul_sexton": maul_sexton,
    "halberd_ward": halberd_ward,
    "spear_fen": spear_fen,
    "greatsword_pilgrim": greatsword_pilgrim,
    "bow_lark": bow_lark,
    "crook_warden": crook_warden,
    "crook_great": crook_great,
    "oar_glaive": oar_glaive,
    "shield_kite": shield_kite,
    "helm_ward": helm_ward,
    "char_ward": char_ward,
    "char_penitent": char_penitent,
    "penitent_arm": penitent_arm,
    "char_aveline": char_aveline,
    "char_bellkeeper": char_bellkeeper,
    "bellkeeper_arm": bellkeeper_arm,
    "pell": pell,
}
