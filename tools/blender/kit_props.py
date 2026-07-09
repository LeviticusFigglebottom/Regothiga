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
        # a heaped mound of glowing embers (warm-emissive stone via the GOTHIC
        # shader — reliably bright; the flame shader renders dark at this scale)
        # crowns the bowl, so the brazier always reads as lit coals, not a cone
        embers = V.loft_rings("brazier_embers", [(0.34, 0.58, 12, 0), (0.33, 0.66, 12, 0),
                                                 (0.26, 0.76, 12, 0), (0.14, 0.85, 12, 0),
                                                 (0.04, 0.9, 12, 0)], "M_ember")
        objs.append(embers)
        # small candle-scale flames licking up from the coals (these DO glow)
        for k in range(3):
            a = k * 2.094 + 0.4
            ff = _flame("brazier_flame%d" % k, 0.05, 0.2)
            ff.location = (0.1 * math.cos(a), 0.1 * math.sin(a), 0.88)
            objs.append(ff)
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
    # double-side the cloth so it reads from both faces
    bmesh.ops.solidify(bm, geom=list(bm.faces) + list(bm.verts) + list(bm.edges), thickness=0.012)
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


def canal_vault(win: bool):
    """One 8 m segment of the great canal vault over the Drowned Marches: a
    semicircular barrel roof (r=20, sprung at z=2) with skirts running below
    the waterline. Faces point INWARD (it is only ever seen from inside).
    The window variant opens a barred 4 m light in both flanks."""
    R, CY, L, SEG = 20.0, 2.0, 8.0, 14
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
                continue   # the barred light
            a, b = grid[c][i], grid[c][i + 1]
            d, e = grid[c + 1][i], grid[c + 1][i + 1]
            bm.faces.new((a, b, e, d))
    objs = [V.bm_to_object(bm, "canal_vault", ("M_stone_dark",))]
    if win:
        # the aperture runs from the springing (z=2.0) up to the first arc
        # chord (~z 6.45): the grate must cover the WHOLE opening, sill to
        # crown — a short grate leaves a bare gap under the bars
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
        # dressed stone reveal: closes the slit between the sloped vault
        # face and the vertical grate plane, so the ironwork sits flush
        rv = bmesh.new()
        for sgn in (-1, 1):
            lo, hi = min(sgn * 18.9, sgn * 20.2), max(sgn * 18.9, sgn * 20.2)
            V.add_box(rv, (-2.15, lo, 1.85), (2.15, hi, 2.2))     # sill
            V.add_box(rv, (-2.15, lo, 6.3), (2.15, hi, 6.75))    # head
            V.add_box(rv, (-2.15, lo, 1.85), (-1.85, hi, 6.75))  # jamb
            V.add_box(rv, (1.85, lo, 1.85), (2.15, hi, 6.75))    # jamb
        objs.append(V.bm_to_object(rv, "vault_reveal", ("M_stone_dark",)))
    return objs, {"size": [8, 40, 25.2], "origin": "bottom-center"}


def ferry_boat():
    """A working mini ferry for the waterworks passage: raked bow, planked
    deck, bulwarks, an aft rail, a steering sweep and a caged bow lantern.
    Bow points +X. Origin bottom-center; deck top at z=0.40."""
    objs = []
    bm = bmesh.new()
    V.add_box(bm, (-2.1, -0.85, 0.08), (1.7, 0.85, 0.34))            # bottom
    V.add_box(bm, (-2.1, -0.85, 0.34), (-1.95, 0.85, 0.82))          # transom
    V.add_box(bm, (-2.1, -0.85, 0.34), (1.7, -0.7, 0.78))            # port bulwark
    V.add_box(bm, (-2.1, 0.7, 0.34), (1.7, 0.85, 0.78))              # starboard bulwark
    V.add_box(bm, (1.7, -0.62, 0.12), (2.15, 0.62, 0.74))            # bow rake step 1
    V.add_box(bm, (2.15, -0.34, 0.18), (2.52, 0.34, 0.68))           # bow rake step 2
    objs.append(V.bm_to_object(bm, "ferry_hull", ("M_wood",)))
    bm = bmesh.new()
    x = -1.92
    while x < 1.6:                                                    # deck planking
        V.add_box(bm, (x, -0.68, 0.34), (x + 0.31, 0.68, 0.40))
        x += 0.36
    V.add_box(bm, (1.7, -0.5, 0.32), (2.12, 0.5, 0.40))              # bow step
    objs.append(V.bm_to_object(bm, "ferry_deck", ("M_wood",)))
    bm = bmesh.new()
    for py in (-0.72, 0.72):                                          # aft posts
        V.add_box(bm, (-1.99, py - 0.05, 0.78), (-1.89, py + 0.05, 1.44))
    V.add_box(bm, (-1.98, -0.74, 1.32), (-1.9, 0.74, 1.42))          # aft rail
    V.add_box(bm, (1.82, -0.05, 0.68), (1.92, 0.05, 1.5))            # lantern post
    V.add_box(bm, (1.74, -0.13, 1.5), (2.0, 0.13, 1.58))             # lantern base
    V.add_box(bm, (1.72, -0.15, 1.86), (2.02, 0.15, 1.94))           # lantern cap
    for py in (-0.11, 0.11):                                          # cage bars
        V.add_box(bm, (1.75, py - 0.015, 1.58), (1.78, py + 0.015, 1.86))
        V.add_box(bm, (1.96, py - 0.015, 1.58), (1.99, py + 0.015, 1.86))
    objs.append(V.bm_to_object(bm, "ferry_iron", ("M_iron",)))
    bm = bmesh.new()
    V.add_box(bm, (1.79, -0.08, 1.6), (1.95, 0.08, 1.82))            # the flame
    objs.append(V.bm_to_object(bm, "ferry_flame", ("M_ember",)))
    bm = bmesh.new()
    V.add_box(bm, (-2.78, 0.30, 0.30), (-2.05, 0.42, 0.44))          # sweep blade
    V.add_box(bm, (-2.1, 0.30, 0.44), (-1.5, 0.38, 0.92))            # sweep loom
    objs.append(V.bm_to_object(bm, "ferry_sweep", ("M_wood",)))
    return objs, {"size": [5.3, 1.7, 1.94], "origin": "bottom-center"}


def anvil():
    """Reliquary smith's anvil: forged block with a squared horn, set on an
    oak stump so the working face lands at a smith's hip."""
    bm = bmesh.new()
    V.add_box(bm, (-0.22, -0.2, 0.0), (0.22, 0.2, 0.45))
    stump = V.bm_to_object(bm, "stump", ("M_wood",))
    bm2 = bmesh.new()
    V.add_box(bm2, (-0.16, -0.13, 0.45), (0.2, 0.13, 0.55))    # waist
    V.add_box(bm2, (-0.2, -0.16, 0.55), (0.28, 0.16, 0.72))    # body + face
    V.add_box(bm2, (-0.4, -0.06, 0.6), (-0.2, 0.06, 0.72))     # horn
    iron = V.bm_to_object(bm2, "anvil_iron", ("M_steel",))
    return [stump, iron], {"size": [0.8, 0.4, 0.72], "origin": "bottom-center"}


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
    """The Bellkeeper's cracked great bell — also the tower bell. ~1.6 m tall.
    The loft rolls under the lip and climbs back up to the crown as a true
    inner wall, so the shell reads CLOSED from every angle (the old open loft
    showed through itself and read as a hollow tent from below). A clapper
    hangs into the mouth for anyone who peers under the lip."""
    n = 12
    rings = [(0.02, 1.61, n, 0), (0.10, 1.62, n, 0), (0.16, 1.55, n, 0), (0.30, 1.45, n, 0),
             (0.44, 1.2, n, 0), (0.52, 0.9, n, 0), (0.56, 0.55, n, 0),
             (0.62, 0.28, n, 0), (0.72, 0.10, n, 0), (0.74, 0.0, n, 0),
             # rolled lip turns under, then the inner wall climbs home
             (0.68, 0.03, n, 0), (0.55, 0.24, n, 0), (0.49, 0.55, n, 0),
             (0.42, 0.9, n, 0), (0.32, 1.15, n, 0), (0.13, 1.38, n, 0),
             (0.02, 1.40, n, 0)]
    bell = V.loft_rings("bell_great", rings, "M_bell", cap_bottom=True, cap_top=True)
    clapper = V.loft_rings("clapper", [(0.035, 1.38, 8, 0), (0.05, 0.42, 8, 0),
                                       (0.115, 0.30, 8, 0), (0.12, 0.12, 8, 0),
                                       (0.03, 0.05, 8, 0)], "M_iron",
                           cap_bottom=True, cap_top=True)
    crown = V.loft_rings("crown", [(0.05, 1.6, 6, 0), (0.08, 1.74, 6, 0), (0.03, 1.82, 6, 0)], "M_bell")
    return [bell, clapper, crown], {"size": [1.5, 1.5, 1.85], "origin": "bottom-center"}


def organ_case():
    """Basilica organ: timber case with a rising rank of bronze pipes.
    ~2.6 m wide. Origin bottom-center, pipes face -Y (Godot +Z... interior)."""
    objs = []
    bm = bmesh.new()
    V.add_box(bm, (-1.3, -0.35, 0.0), (1.3, 0.45, 1.15))
    V.add_box(bm, (-1.36, -0.3, 1.1), (1.36, 0.5, 1.28))
    objs.append(V.bm_to_object(bm, "organ_case", ("M_wood",)))
    n = 9
    for i in range(n):
        t = i / (n - 1.0)
        x = -1.05 + 2.1 * t
        h = 1.5 + 1.5 * (1.0 - abs(t * 2 - 1)) ** 1.2 + 0.12 * ((i * 7) % 3)
        r = 0.085 - 0.02 * abs(t * 2 - 1)
        pipe = V.loft_rings("pipe%d" % i, [(r, 1.2, 8, 0), (r, 1.2 + h, 8, 0),
                                           (r * 0.8, 1.26 + h, 8, 0)], "M_bronze")
        pipe.location = (x, -0.12, 0)
        objs.append(pipe)
    return objs, {"size": [2.8, 1.0, 4.3], "origin": "bottom-center"}


def choir_stall():
    """High-backed choir stall bench, faces -Y like the pews."""
    objs = []
    bm = bmesh.new()
    V.add_box(bm, (-1.15, -0.24, 0.42), (1.15, 0.12, 0.5))      # seat
    V.add_box(bm, (-1.15, 0.12, 0.0), (1.15, 0.3, 1.55))        # tall back
    V.add_box(bm, (-1.15, 0.24, 1.55), (1.15, 0.38, 1.72))      # canopy rail
    V.add_box(bm, (-1.15, -0.3, 0.0), (-1.02, 0.12, 0.86))      # arms
    V.add_box(bm, (1.02, -0.3, 0.0), (1.15, 0.12, 0.86))
    V.add_box(bm, (-1.15, -0.26, 0.16), (1.15, -0.18, 0.2))     # kneeler
    objs.append(V.bm_to_object(bm, "choir_stall", ("M_wood",)))
    return objs, {"size": [2.4, 0.7, 1.75], "origin": "bottom-center"}


def chime_stone():
    """Vesper chime: a standing stone gallows with a hanging bronze bar.
    Interactable puzzle prop. Origin bottom-center."""
    objs = []
    post = V.loft_rings("chime_post", [(0.17, 0, 7, 0), (0.13, 0.2, 7, 0),
                                       (0.11, 1.9, 7, 0), (0.15, 2.05, 7, 0)], "M_stone_trim")
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
    objs.append(V.loft_rings("votive_col", [(0.2, 0, 8, 0), (0.06, 0.12, 8, 0),
                                            (0.05, 1.16, 8, 0), (0.17, 1.24, 8, 0),
                                            (0.19, 1.3, 8, 0)], "M_iron"))
    import random as _random
    rng = _random.Random(9 if lit else 10)
    for i in range(5):
        a = 2 * math.pi * i / 5
        r = 0.11
        h = 0.14 + 0.1 * rng.random()
        c = V.loft_rings("cand%d" % i, [(0.035, 1.3, 6, 0), (0.033, 1.3 + h, 6, 0)], "M_wax")
        c.location = (r * math.cos(a), r * math.sin(a), 0)
        objs.append(c)
        if lit:
            f = _flame("votive_flame%d" % i, 0.024, 0.085)
            f.location = (r * math.cos(a), r * math.sin(a), 1.33 + h)
            objs.append(f)
    return objs, {"size": [0.5, 0.5, 1.6], "origin": "bottom-center"}


def mosaic_medallion():
    """Flat inlaid mosaic roundel, 3.4 m across — floor charm for garths,
    thresholds and crossings. Passable (no collision policy)."""
    disc = V.loft_rings("mosaic_disc", [(1.7, 0.0, 22, 0), (1.7, 0.028, 22, 0)], "M_mosaic")
    rim = V.loft_rings("mosaic_rim", [(1.78, 0.0, 22, 0), (1.78, 0.02, 22, 0),
                                      (1.7, 0.02, 22, 0), (1.7, 0.0, 22, 0)], "M_stone_trim",
                       cap_bottom=False, cap_top=False)
    return [disc, rim], {"size": [3.6, 3.6, 0.03], "origin": "bottom-center"}


def ossuary_wall_4m():
    """Crypt wall: stone frame with two shelf bands of stacked skulls.
    4x4 face, same footprint as wall_4x4."""
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
            got = bmesh.ops.create_icosphere(bm, subdivisions=0, radius=0.14 + rng.random() * 0.03)
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
        a = rng.random() * math.pi
        x, y = (rng.random() - 0.5) * 0.9, (rng.random() - 0.5) * 0.7
        got = bmesh.ops.create_icosphere(bm, subdivisions=0, radius=0.1 + rng.random() * 0.05)
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
    import random as _random
    rng = _random.Random(seed)
    bm = bmesh.new()
    L = 1.7
    for t4 in range(5):
        t = t4 / 4.0
        r = 0.16 * (1.0 - 0.55 * abs(t * 2 - 1)) + 0.04
        got = bmesh.ops.create_icosphere(bm, subdivisions=0, radius=r)
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
    """Corner cobweb: a quarter fan of silk with radial threads. Hangs in a
    wall corner (ruin dressing). Passable. Origin at the corner."""
    bm = bmesh.new()
    import math as _m
    n = 6
    R = 1.05
    corner = bm.verts.new((0, 0, 0))
    rim = []
    for i in range(n + 1):
        a = _m.pi * 0.5 * i / n
        # web sags: pull the rim inward slightly toward the middle angles
        sag = 1.0 - 0.18 * _m.sin(_m.pi * i / n)
        rim.append(bm.verts.new((R * _m.cos(a) * sag, 0, R * _m.sin(a) * sag)))
    # concentric silk arcs (thin quads between two radii)
    for band in (0.4, 0.72):
        prev = None
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
    """A length of iron chain dropping from a vault, ~1.6 m, with an optional
    ring hook at the bottom. Ambient verticality. Passable."""
    objs = []
    bm = bmesh.new()
    z = 0.0
    for i in range(9):
        # alternate link orientation for a real chain read
        wx = 0.05 if i % 2 else 0.02
        wy = 0.02 if i % 2 else 0.05
        V.add_box(bm, (-wx, -wy, z - 0.09), (wx, wy, z))
        z -= 0.16
    objs.append(V.bm_to_object(bm, "chain", ("M_iron",)))
    if with_hook:
        hook = V.loft_rings("hook", [(0.09, z - 0.02, 8, 0), (0.11, z - 0.1, 8, 0),
                                     (0.09, z - 0.18, 8, 0)], "M_iron")
        objs.append(hook)
    return objs, {"size": [0.2, 0.2, 1.7], "origin": "top-center"}


def door_leaf():
    """A shut double door of banded oak for a 1.9-wide portal opening. Solid.
    Origin bottom-center, faces +Y (drops into a portal_4m transform)."""
    objs = []
    bm = bmesh.new()
    for sx in (-1, 1):
        x0 = 0.02 * sx
        x1 = sx * 0.92
        lo, hi = (min(x0, x1), max(x0, x1))
        V.add_box(bm, (lo, -0.06, 0.02), (hi, 0.06, 2.82))
    objs.append(V.bm_to_object(bm, "door_oak", ("M_wood",)))
    bm = bmesh.new()
    # iron cross-bands + ring handles
    for z in (0.5, 1.4, 2.3):
        V.add_box(bm, (-0.9, -0.08, z - 0.05), (0.9, 0.08, z + 0.05))
    for sx in (-1, 1):
        V.add_box(bm, (sx * 0.9 - 0.05, -0.08, 0.1), (sx * 0.9 + 0.05, 0.08, 2.75))
    import math as _m
    for sx in (-1, 1):
        ring = V.loft_rings("ring", [(0.02, 0, 8, 0), (0.03, 0.0, 8, 0)], "M_iron")
    objs.append(V.bm_to_object(bm, "door_bands", ("M_iron",)))
    # stone tympanum backing the pointed arch above the leaves — a portal_4m
    # opening runs to a ~3.2 m point, so bare doors leave a sliver of sky/city
    # showing at the tip; this panel seals it (edges buried in the arch jambs)
    tbm = bmesh.new()
    V.add_box(tbm, (-1.0, -0.07, 2.66), (1.0, 0.1, 3.98))
    objs.append(V.bm_to_object(tbm, "door_tympanum", ("M_stone",)))
    return objs, {"size": [2.0, 0.24, 3.98], "origin": "bottom-center"}


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
