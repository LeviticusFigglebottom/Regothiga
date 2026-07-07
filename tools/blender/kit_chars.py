"""Character kit: robed figure parts assembled into node-rigs in Godot.
All characters share the robed silhouette family (DECISIONS D-005).

Origins: body parts at their joint. Robe body origin at floor between feet;
sleeves at the shoulder joint (arm hangs -Z); weapons at the grip (blade +Z).
"""
import math
import random
import bmesh
from mathutils import Vector

import vglib as V


def _robe_body(name, height, girth, mat, hood=True, hood_lean=0.09):
    """Humanoid read: spread hem, drawn waist, carried chest, squared
    shoulders, cinched neck, deep hood. (Painted-fantasy silhouette pass.)"""
    n = 14
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
    # rope belt
    belt = V.loft_rings("belt", [(0.255, 0.80, 10, 0), (0.27, 0.84, 10, 0), (0.25, 0.88, 10, 0)], "M_leather")
    objs.append(belt)
    # satchel
    bm = bmesh.new()
    V.add_box(bm, (-0.14, 0.16, 0.72), (0.10, 0.34, 0.95))
    objs.append(V.bm_to_object(bm, "satchel", ("M_leather",)))
    return objs, {"size": [0.8, 0.8, 1.75], "origin": "bottom-center"}


def char_sleeve(side):
    """Arm with an elbow: upper arm drops, forearm angles forward, cuff
    flares, hand closes. Origin at shoulder, hanging along -Z (blender)."""
    sgn = -1 if side == "l" else 1
    n = 8
    objs = []
    upper = V.loft_rings(f"sleeve_{side}", [(0.088, 0.0, n, 0), (0.078, -0.13, n, 0),
                                            (0.072, -0.24, n, 0)], "M_robe")
    objs.append(upper)
    # pauldron cap
    pauld = V.loft_rings("pauldron", [(0.115, 0.03, n, 0), (0.125, -0.03, n, 0),
                                      (0.09, -0.1, n, 0)], "M_leather")
    objs.append(pauld)
    # forearm: bent ~22 deg toward +Y (forward after import)
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
    """Cloistersword: austere longsword. Origin at grip center, blade +Z."""
    objs = []
    bm = bmesh.new()
    # blade with a shallow taper and point
    w0, w1, t = 0.045, 0.03, 0.008
    L = 0.98
    for (z0, z1, wa, wb) in ((0.12, L * 0.85, w0, w1),):
        a = [bm.verts.new(p) for p in ((-wa, -t, z0), (wa, -t, z0), (wa, t, z0), (-wa, t, z0))]
        b = [bm.verts.new(p) for p in ((-wb, -t * 0.7, z1), (wb, -t * 0.7, z1), (wb, t * 0.7, z1), (-wb, t * 0.7, z1))]
        for i in range(4):
            bm.faces.new((a[i], a[(i + 1) % 4], b[(i + 1) % 4], b[i]))
        bm.faces.new(list(reversed(a)))
        tip = bm.verts.new((0, 0, L))
        for i in range(4):
            bm.faces.new((b[i], b[(i + 1) % 4], tip))
    objs.append(V.bm_to_object(bm, "blade", ("M_steel",)))
    # cross guard: flared bar
    bm2 = bmesh.new()
    V.add_box(bm2, (-0.16, -0.016, 0.095), (0.16, 0.016, 0.13))
    objs.append(V.bm_to_object(bm2, "cross", ("M_iron",)))
    # grip + wheel pommel
    objs.append(V.loft_rings("grip", [(0.018, -0.09, 8, 0), (0.02, 0.095, 8, 0)], "M_leather"))
    objs.append(V.loft_rings("pommel", [(0.012, -0.14, 8, 0), (0.036, -0.115, 8, 0), (0.012, -0.085, 8, 0)], "M_iron"))
    return objs, {"size": [0.32, 0.05, 1.15], "origin": "grip"}


def maul_sexton():
    """Sexton's Maul: gravedigger's great hammer. Origin at grip, head +Z."""
    objs = []
    objs.append(V.loft_rings("haft", [(0.025, -0.5, 8, 0), (0.03, 0.72, 8, 0)], "M_wood"))
    bm = bmesh.new()
    V.add_box(bm, (-0.11, -0.11, 0.72), (0.11, 0.11, 1.02))
    V.add_box(bm, (-0.13, -0.13, 0.70), (0.13, 0.13, 0.76))
    V.add_box(bm, (-0.13, -0.13, 0.98), (0.13, 0.13, 1.02))
    objs.append(V.bm_to_object(bm, "head", ("M_stone_dark",)))
    return objs, {"size": [0.3, 0.3, 1.55], "origin": "grip"}


def halberd_ward():
    """Ward's halberd: long haft, axe blade + spike. Origin at grip point."""
    objs = []
    objs.append(V.loft_rings("haft", [(0.022, -0.9, 8, 0), (0.025, 1.05, 8, 0)], "M_wood"))
    bm = bmesh.new()
    # axe blade: flat fan
    pts = [(0.0, 0.0, 0.72), (0.22, 0.0, 0.80), (0.26, 0.0, 0.98), (0.20, 0.0, 1.12), (0.0, 0.0, 1.05)]
    vs = [bm.verts.new(p) for p in pts]
    bm.faces.new(vs)
    bmesh.ops.solidify(bm, geom=list(bm.faces) + list(bm.verts) + list(bm.edges), thickness=0.015)
    objs.append(V.bm_to_object(bm, "axehead", ("M_steel",)))
    spike = V.loft_rings("spike", [(0.03, 1.05, 6, 0), (0.004, 1.38, 6, 0)], "M_steel")
    objs.append(spike)
    return objs, {"size": [0.5, 0.1, 2.3], "origin": "grip"}


def shield_kite():
    """Kite shield, worn face +Y outward. Origin at arm strap."""
    bm = bmesh.new()
    pts = [(0.0, -0.52), (0.16, -0.30), (0.19, 0.05), (0.13, 0.22), (0.0, 0.28),
           (-0.13, 0.22), (-0.19, 0.05), (-0.16, -0.30)]
    vs = [bm.verts.new((x, 0.0, z)) for (x, z) in pts]
    face = bm.faces.new(vs)
    # curve the face: push center out
    res = bmesh.ops.poke(bm, faces=[face])
    for v in res["verts"]:
        v.co.y += 0.07
    bmesh.ops.solidify(bm, geom=list(bm.faces) + list(bm.verts) + list(bm.edges), thickness=0.025)
    shield = V.bm_to_object(bm, "shield", ("M_wood",))
    boss = V.loft_rings("boss_sun", [(0.002, 0.0, 10, 0), (0.07, 0.05, 10, 0), (0.002, 0.1, 10, 0)], "M_gold")
    boss.rotation_euler = (math.pi / 2, 0, 0)
    boss.location = (0, 0.10, 0.02)
    return [shield, boss], {"size": [0.42, 0.2, 0.85], "origin": "strap"}


def helm_ward():
    """Great helm with sight slit for the Cloister Ward. Origin at neck."""
    n = 10
    helm = V.loft_rings("helm", [(0.115, 0.0, n, 0), (0.125, 0.10, n, 0), (0.125, 0.22, n, 0),
                                 (0.10, 0.30, n, 0), (0.02, 0.34, n, 0)], "M_iron")
    # horns of office (curved)
    objs = [helm]
    for sgn in (-1, 1):
        horn = V.sweep_profile("horn", [(sgn * 0.10, 0, 0.24), (sgn * 0.2, -0.02, 0.34), (sgn * 0.26, -0.06, 0.46)],
                               V.circle_profile(0.022, 6), "M_iron")
        objs.append(horn)
    return objs, {"size": [0.55, 0.3, 0.5], "origin": "neck"}


def char_ward():
    """Cloister Ward body: wraith-robe + cuirass + pauldrons."""
    objs = []
    body = _robe_body("ward_robe", 1.86, 0.34, "M_wraith")
    objs.append(body)
    cuir = V.loft_rings("cuirass", [(0.30, 1.06, 12, 0), (0.34, 1.26, 12, 0), (0.30, 1.44, 12, 0)], "M_iron")
    objs.append(cuir)
    for sgn in (-1, 1):
        p = V.loft_rings("pauldron", [(0.11, 0.0, 8, 0), (0.13, 0.07, 8, 0), (0.07, 0.16, 8, 0)], "M_iron")
        p.location = (sgn * 0.30, 0, 1.36)
        objs.append(p)
    return objs, {"size": [0.9, 0.9, 2.0], "origin": "bottom-center"}


def char_penitent():
    """Waxbound Penitent: a votive burned into a person-shape. Slumped,
    dripping, a dead wick where the face was."""
    rng = random.Random(77)
    objs = []
    n = 12
    rings = []
    profile = [(0.42, 0.0), (0.40, 0.06), (0.30, 0.35), (0.26, 0.7), (0.28, 0.95),
               (0.30, 1.15), (0.22, 1.32), (0.12, 1.45), (0.05, 1.5)]
    for (r, z) in profile:
        rings.append((r, z, n, 0))
    body = V.loft_rings("penitent", rings, "M_wax")
    # slump + melt asymmetry
    me = body.data
    for v in me.vertices:
        w = V.value_noise(v.co * 2.0 + Vector((7, 7, 7)))
        v.co.x += (w - 0.5) * 0.12 * (0.3 + v.co.z)
        v.co.y += (V.value_noise(v.co * 1.7) - 0.5) * 0.1 * (0.3 + v.co.z)
        if v.co.z > 1.2:
            v.co.y += 0.08  # head droop
    objs.append(body)
    # drips: hanging cones around the base and shoulders
    for i in range(10):
        a = rng.uniform(0, 2 * math.pi)
        z = rng.choice((0.15, 0.2, 1.0, 1.1))
        r0 = 0.31 if z > 0.5 else 0.41
        drip = V.loft_rings("drip", [(0.028, z, 6, 0), (0.012, z - rng.uniform(0.1, 0.3), 6, 0)], "M_wax")
        drip.location = (r0 * math.cos(a), r0 * math.sin(a), 0)
        objs.append(drip)
    # arm clubs: fused-wax stumps (separate so they can swing)
    return objs, {"size": [0.9, 0.9, 1.6], "origin": "bottom-center"}


def penitent_arm():
    """Fused arm-club for the Penitent, origin at shoulder, hangs -Z."""
    n = 8
    arm = V.loft_rings("pen_arm", [(0.085, 0.0, n, 0), (0.11, -0.28, n, 0),
                                   (0.13, -0.5, n, 0), (0.06, -0.62, n, 0)], "M_wax")
    return [arm], {"size": [0.3, 0.3, 0.65], "origin": "shoulder"}


def char_aveline():
    """Sister Aveline: pale habit, wax-dripped candle crown (lit in glory)."""
    objs = []
    body = _robe_body("aveline", 1.66, 0.29, "M_habit", hood=True, hood_lean=0.04)
    objs.append(body)
    crown = V.loft_rings("crown", [(0.145, 1.52, 10, 0), (0.15, 1.60, 10, 0)], "M_wax")
    objs.append(crown)
    rng = random.Random(5)
    for i in range(6):
        a = 2 * math.pi * i / 6
        h = rng.uniform(0.07, 0.16)
        c = V.loft_rings("crown_candle", [(0.022, 1.58, 6, 0), (0.02, 1.58 + h, 6, 0)], "M_wax")
        c.location = (0.13 * math.cos(a), 0.13 * math.sin(a), 0)
        objs.append(c)
        fl = V.loft_rings("crown_flame", [(0.012, 0.0, 6, 0), (0.02, 0.02, 6, 0.3), (0.002, 0.05, 6, 0.6)], "M_flame")
        fl.location = (0.13 * math.cos(a), 0.13 * math.sin(a), 1.585 + h)
        objs.append(fl)
    # apron + waxing tools
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
    # bell-rope harness across the torso
    harness = V.loft_rings("harness", [(0.50, 1.55, 12, 0), (0.53, 1.66, 12, 0), (0.49, 1.77, 12, 0)], "M_leather")
    objs.append(harness)
    # censer chained at the hip (swings)
    cens = V.loft_rings("censer", [(0.02, 0.9, 8, 0), (0.07, 0.98, 8, 0), (0.05, 1.08, 8, 0), (0.02, 1.12, 8, 0)], "M_gold")
    cens.location = (0.45, 0.1, 0)
    objs.append(cens)
    return objs, {"size": [1.4, 1.4, 2.9], "origin": "bottom-center"}


def bellkeeper_arm():
    """Massive sleeve arm for the Bellkeeper. Origin shoulder, hangs -Z."""
    n = 10
    arm = V.loft_rings("bk_arm", [(0.16, 0.0, n, 0), (0.14, -0.35, n, 0),
                                  (0.19, -0.7, n, 0), (0.23, -0.95, n, 0)], "M_robe_boss")
    fist = V.loft_rings("bk_fist", [(0.1, -0.95, n, 0), (0.11, -1.1, n, 0), (0.04, -1.2, n, 0)], "M_wax")
    return [arm, fist], {"size": [0.5, 0.5, 1.25], "origin": "shoulder"}


def pell():
    """Training pell for the combat sandbox."""
    objs = []
    objs.append(V.loft_rings("post", [(0.09, 0, 8, 0), (0.08, 1.9, 8, 0)], "M_wood"))
    objs.append(V.loft_rings("torso", [(0.16, 0.9, 10, 0), (0.22, 1.2, 10, 0), (0.18, 1.55, 10, 0), (0.08, 1.7, 10, 0)], "M_leather"))
    bm = bmesh.new()
    V.add_box(bm, (-0.5, -0.06, 1.32), (0.5, 0.06, 1.44))
    objs.append(V.bm_to_object(bm, "arms", ("M_wood",)))
    return objs, {"size": [1.0, 0.4, 1.95], "origin": "bottom-center"}




def crook_warden():
    """Cage-warden's crook: a long haft curling into an iron shepherd's hook —
    the tool that dragged larks (and worse) back to their cages. Origin grip."""
    objs = [V.loft_rings("haft", [(0.02, -0.85, 8, 0), (0.024, 1.0, 8, 0)], "M_wood")]
    pts = [(0, 0, 1.0), (0.02, 0, 1.18), (0.1, 0, 1.3), (0.2, 0, 1.32),
           (0.27, 0, 1.24), (0.28, 0, 1.12), (0.22, 0, 1.05)]
    objs.append(V.sweep_profile("hook", pts, V.circle_profile(0.022, 6), "M_iron"))
    return objs, {"size": [0.5, 0.1, 2.2], "origin": "grip"}


def crook_great():
    """The Larkwarden's great crook: a two-hand cage-hook, gilt at the curl."""
    objs = [V.loft_rings("haft_g", [(0.03, -1.1, 8, 0), (0.035, 1.35, 8, 0)], "M_wood")]
    pts = [(0, 0, 1.35), (0.03, 0, 1.6), (0.16, 0, 1.78), (0.34, 0, 1.8),
           (0.45, 0, 1.68), (0.46, 0, 1.5), (0.36, 0, 1.4)]
    objs.append(V.sweep_profile("hook_g", pts, V.circle_profile(0.035, 6), "M_gold"))
    objs.append(V.loft_rings("ferrule", [(0.045, 1.3, 8, 0), (0.04, 1.42, 8, 0)], "M_gold"))
    return objs, {"size": [0.9, 0.14, 3.0], "origin": "grip"}




def oar_glaive():
    """The Ferryman's oar-glaive: a pole arm ending in a broad steel-shod
    blade — half oar, half executioner's sweep. Origin at grip."""
    objs = [V.loft_rings("oar_haft", [(0.028, -1.15, 8, 0), (0.032, 1.2, 8, 0)], "M_wood")]
    bm = bmesh.new()
    pts = [(-0.04, 0.0, 1.15), (0.24, 0.0, 1.45), (0.3, 0.0, 1.95),
           (0.16, 0.0, 2.35), (-0.06, 0.0, 2.4)]
    vs = [bm.verts.new(p) for p in pts]
    bm.faces.new(vs)
    import bmesh as _bm
    _bm.ops.solidify(bm, geom=list(bm.faces) + list(bm.verts) + list(bm.edges), thickness=0.03)
    objs.append(V.bm_to_object(bm, "oar_blade", ("M_steel",)))
    return objs, {"size": [0.7, 0.12, 3.6], "origin": "grip"}


BUILDERS = {
    "char_latecomer": char_latecomer,
    "char_sleeve_l": lambda: char_sleeve("l"),
    "char_sleeve_r": lambda: char_sleeve("r"),
    "sword_cloister": sword_cloister,
    "maul_sexton": maul_sexton,
    "halberd_ward": halberd_ward,
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
