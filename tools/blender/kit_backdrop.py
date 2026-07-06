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


def _stringer(bm, x, run, rise, w=0.14):
    """A SOLID closed-string side wall running the length of a stair, at plane x:
    top follows the step nosings, bottom drops to the lower floor, so you can't
    see under or beside the stair. Profile in the Y(run)-Z(height) plane; Z up."""
    prof = [(-0.1, 0.15), (run + 0.1, -rise + 0.15), (run + 0.1, -rise - 0.35), (-0.1, -rise - 0.35)]
    fr = [bm.verts.new((x, py, pz)) for (py, pz) in prof]        # (y_run, z_height)
    bk = [bm.verts.new((x + w, py, pz)) for (py, pz) in prof]
    bm.faces.new(fr)
    bm.faces.new(list(reversed(bk)))
    for i in range(4):
        j = (i + 1) % 4
        bm.faces.new((fr[i], fr[j], bk[j], bk[i]))


def stair_grand_4m():
    """Grand stair: 4 m wide, DROPPING 2.4 m over a 4 m run, with side stringers.
    Z is UP in this kit (like every wall/column): the RISE is on Z, the RUN on Y
    (toward +Y, which becomes the ramp's -Z in Godot so the visual and the
    2.4-over-4 collision ramp descend the SAME way). Origin: top front-edge
    centre; the top tread sits flush with the upper floor, the foot 2.4 m below."""
    bm = bmesh.new()
    steps, run, rise = 12, 4.0, 2.4
    dy, dz = run / steps, rise / steps
    for i in range(steps):
        top = -dz * i                       # tread top height (Z), descending
        # x[-2.1,2.1]  y(run)[dy*i, dy*(i+1)]  z(height)[top-dz, top]
        _box(bm, -2.1, dy * i - 0.02, top - dz - 0.02, 2.1, dy * (i + 1), top)
    _stringer(bm, -2.24, run, rise)
    _stringer(bm, 2.10, run, rise)
    obj = V.bm_to_object(bm, "stair", ("M_stone",))
    return [obj], {"size": [4.68, rise, run], "origin": "top-center"}


def urn():
    u = V.loft_rings("urn", [(0.16, 0, 10, 0), (0.13, 0.05, 10, 0), (0.3, 0.34, 10, 0),
                             (0.34, 0.6, 10, 0), (0.2, 0.86, 10, 0), (0.26, 0.95, 10, 0)], "M_stone_trim")
    return [u], {"size": [0.7, 0.7, 1.0], "origin": "bottom-center"}


def wellhead():
    """Octagonal garth draw-well: a stone rim with a coping ring, a timber
    windlass on two short posts, an iron crank, and a bucket on a chain over the
    mouth. Open (no canopy) — the classic cloister-garth centrepiece, and nothing
    broad enough to read as a flat grey plate from below."""
    objs = []
    objs.append(V.loft_rings("well_wall", [(1.05, 0, 8, 0), (1.05, 0.85, 8, 0), (0.85, 0.85, 8, 0),
                                           (0.85, 0.0, 8, 0)], "M_stone", cap_bottom=False, cap_top=False))
    # a chamfered stone coping crowning the rim
    objs.append(V.loft_rings("well_coping", [(1.12, 0.85, 8, 0), (1.14, 0.9, 8, 0), (1.1, 0.99, 8, 0),
                                             (0.8, 0.99, 8, 0), (0.8, 0.85, 8, 0)], "M_stone_trim",
                             cap_bottom=False, cap_top=False))
    # two short posts + a wooden windlass roller-bar
    for sx in (-0.9, 0.9):
        p = V.loft_rings("post", [(0.08, 0.95, 6, 0), (0.07, 1.62, 6, 0)], "M_wood")
        p.location = (sx, 0, 0)
        objs.append(p)
    bar = V.box_object("well_bar", [2.0, 0.14, 0.14], "M_wood", origin="center")
    bar.location = (0, 0, 1.5)
    objs.append(bar)
    # an iron crank handle off one post
    crank = V.box_object("well_crank", [0.34, 0.06, 0.06], "M_iron", origin="center")
    crank.location = (1.0, -0.24, 1.5)
    objs.append(crank)
    handle = V.box_object("well_handle", [0.06, 0.06, 0.24], "M_iron", origin="center")
    handle.location = (1.15, -0.24, 1.28)
    objs.append(handle)
    # chain + bucket hanging over the mouth
    chain = V.box_object("well_chain", [0.04, 0.04, 0.72], "M_iron", origin="center")
    chain.location = (0.3, 0, 0.82)
    objs.append(chain)
    bucket = V.loft_rings("bucket", [(0.16, 0, 8, 0), (0.19, 0.3, 8, 0)], "M_wood",
                          cap_bottom=True, cap_top=False)
    bucket.location = (0.3, 0, 0.52)
    objs.append(bucket)
    return objs, {"size": [2.1, 1.0, 1.72], "origin": "bottom-center"}


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


# ---------------------------------------------------------------------------
# Panorama city: distinct Anor-Londo monuments, not brick prisms.
#
# Each building is modelled in a LOCAL frame — x tangential, y radial-OUT from
# the ring (so the front face at y=0 turns toward the viewer at the centre),
# z up — then emitted through a `place(x,y,z)` closure that rotates it onto its
# arc. Relief that actually reads at 30-200 m: buttress pilasters stand proud
# of the wall, window bays sink dark between them, cornices cap each stage.
# Two meshes: warm stone (bm) and shadowed openings (dbm).
# ---------------------------------------------------------------------------

def _placer(ang, R, z0=0.0):
    ca, sa = math.cos(ang), math.sin(ang)
    def place(x, y, z):                      # local (tangent, radial-out, up)
        r = R + y
        return Vector((r * ca - x * sa, r * sa + x * ca, z + z0))
    return place


def _ground_y(r):
    """The city stands on a hillside that falls away from the terrace: the
    ground descends steadily with radius so the vista reads as an overlook into
    a valley, never a flat plate hanging in the air."""
    return -0.5 - max(0.0, r - 14.0) * 0.22


def _tbox(bm, place, x0, y0, z0, x1, y1, z1):
    c = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
         (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    v = [bm.verts.new(place(*p)) for p in c]
    for f in ((0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1),
              (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)):
        bm.faces.new([v[i] for i in f])


def _tspire(bm, place, cx, cy, z, w, h):
    a = bm.verts.new(place(cx - w, cy - w, z)); b = bm.verts.new(place(cx + w, cy - w, z))
    c = bm.verts.new(place(cx + w, cy + w, z)); d = bm.verts.new(place(cx - w, cy + w, z))
    tip = bm.verts.new(place(cx, cy, z + h))
    for e0, e1 in ((a, b), (b, c), (c, d), (d, a)):
        bm.faces.new((e0, e1, tip))


def _tpin(bm, place, cx, cy, z, w, h):
    _tbox(bm, place, cx - w, cy - w, z, cx + w, cy + w, z + h * 0.5)
    _tspire(bm, place, cx, cy, z + h * 0.5, w * 1.15, h * 0.5)


def _tgable(bm, place, x0, x1, y0, y1, z, rise):
    xm = (x0 + x1) * 0.5
    a = bm.verts.new(place(x0, y0, z)); b = bm.verts.new(place(x1, y0, z))
    c = bm.verts.new(place(x1, y1, z)); d = bm.verts.new(place(x0, y1, z))
    r0 = bm.verts.new(place(xm, y0, z + rise)); r1 = bm.verts.new(place(xm, y1, z + rise))
    bm.faces.new((a, b, r0)); bm.faces.new((d, r1, c))
    bm.faces.new((a, r0, r1, d)); bm.faces.new((b, c, r1, r0))


def _tdisc(bm, place, cx, cy, cz, r, seg=10):
    ring = [bm.verts.new(place(cx + r * math.cos(math.tau * i / seg), cy,
            cz + r * math.sin(math.tau * i / seg))) for i in range(seg)]
    c = bm.verts.new(place(cx, cy - 0.05, cz))
    for i in range(seg):
        bm.faces.new((c, ring[i], ring[(i + 1) % seg]))


def _tdome(bm, place, cx, cy, z, r, h, seg=10, rings=4):
    prev = None
    for j in range(rings + 1):
        t = j / rings
        rr = r * math.cos(t * math.pi / 2)
        zz = z + h * math.sin(t * math.pi / 2)
        ring = [bm.verts.new(place(cx + rr * math.cos(math.tau * i / seg), cy + rr * math.sin(math.tau * i / seg), zz))
                for i in range(seg)]
        if prev:
            for i in range(seg):
                bm.faces.new((prev[i], prev[(i + 1) % seg], ring[(i + 1) % seg], ring[i]))
        prev = ring


def _facade(L, D, place, x0, x1, z0, z1, rng, bays=0, arched=True):
    """Buttress pilasters (proud, light) framing recessed dark window bays, with
    a cornice ledge at top — the detail that turns a wall into a cathedral flank."""
    span = x1 - x0
    if bays <= 0:
        bays = max(1, int(round(span / 3.4)))
    bw = span / bays
    _tbox(L, place, x0 - 0.3, -0.7, z1 - 0.5, x1 + 0.3, 0.12, z1)        # top cornice
    if z1 - z0 > 9:                                                       # mid string course
        zm = (z0 + z1) * 0.5
        _tbox(L, place, x0 - 0.2, -0.5, zm, x1 + 0.2, 0.08, zm + 0.35)
    for i in range(bays + 1):                                            # buttress pilasters
        bx = x0 + i * bw
        _tbox(L, place, bx - 0.34, -0.65, z0, bx + 0.34, 0.05, z1 - 0.1)
    for i in range(bays):                                                # dark window bays
        wx0 = x0 + i * bw + bw * 0.32
        wx1 = x0 + i * bw + bw * 0.68
        wz1 = z1 - 0.7
        wz0 = z0 + (z1 - z0) * 0.14
        _tbox(D, place, wx0, -0.14, wz0, wx1, 0.03, wz1)
        if arched:                                                        # lancet head
            _tspire(D, place, (wx0 + wx1) * 0.5, -0.05, wz1, (wx1 - wx0) * 0.5, (wx1 - wx0) * 0.7)


def _bld_hall(L, D, place, w, h, rng):
    d = w * rng.uniform(0.55, 0.95)
    _tbox(L, place, -w / 2, 0, 0, w / 2, d, h)
    _facade(L, D, place, -w / 2, w / 2, 1.0, h - 0.4, rng)
    if rng.random() < 0.6:
        _tgable(L, place, -w / 2, w / 2, 0, d, h, w * rng.uniform(0.24, 0.36))
        if rng.random() < 0.4:
            _tspire(L, place, 0, d * 0.5, h + w * 0.24, w * 0.06, h * rng.uniform(0.3, 0.5))
    else:
        _tbox(L, place, -w / 2 - 0.4, -0.4, h, w / 2 + 0.4, d + 0.4, h + 0.7)   # parapet
        for sx in (-1, 1):
            _tpin(L, place, sx * (w / 2 - 0.3), d * 0.5, h + 0.7, w * 0.07, h * 0.28)


def _bld_tower(L, D, place, w, h, rng):
    w = min(w, max(4.0, h * 0.26))
    d = w
    z, ww = 0.0, w
    while z < h * 0.82:
        th = min(h * 0.34, h - z)
        _tbox(L, place, -ww / 2, 0, z, ww / 2, d, z + th)
        _tbox(L, place, -ww / 2 - 0.35, -0.35, z + th, ww / 2 + 0.35, d + 0.1, z + th + 0.45)
        _facade(L, D, place, -ww * 0.42, ww * 0.42, z + th * 0.25, z + th * 0.9, rng, bays=1)
        z += th + 0.45
        ww *= 0.9
    # belfry openings + crown
    _tbox(D, place, -ww * 0.3, -0.12, z - h * 0.16, ww * 0.3, 0.03, z - h * 0.03)
    for sx in (-1, 1):
        for sy in (0, 1):
            _tpin(L, place, sx * ww * 0.46, sy * d, z, ww * 0.09, h * 0.16)
    _tspire(L, place, 0, d * 0.5, z, ww * 0.58, h * rng.uniform(0.42, 0.7))


def _bld_tiered(L, D, place, w, h, rng):
    tiers = rng.randint(2, 3)
    z, ww, dd = 0.0, w, w * 0.85
    for t in range(tiers):
        th = h * (0.5 if t == 0 else 0.34) * (1.0 - t * 0.08)
        _tbox(L, place, -ww / 2, 0, z, ww / 2, dd, z + th)
        _facade(L, D, place, -ww / 2, ww / 2, z + th * 0.2, z + th * 0.86, rng, arched=(t == 0))
        _tbox(L, place, -ww / 2 - 0.35, -0.35, z + th, ww / 2 + 0.35, dd + 0.35, z + th + 0.5)  # cornice
        for sx in (-1, 1):
            _tpin(L, place, sx * (ww / 2 - 0.2), dd * 0.5, z + th + 0.5, ww * 0.05, th * 0.35)
        z += th + 0.5
        ww *= 0.72
        dd *= 0.75
    _tspire(L, place, 0, dd * 0.5, z, ww * 0.4, h * 0.24)


def _bld_dome(L, D, place, w, h, rng):
    d = w * 0.85
    base = h * 0.55
    _tbox(L, place, -w / 2, 0, 0, w / 2, d, base)
    _facade(L, D, place, -w / 2, w / 2, 1.0, base - 0.5, rng)
    _tbox(L, place, -w / 2 - 0.3, -0.3, base, w / 2 + 0.3, d + 0.3, base + 0.5)
    r = min(w, d) * 0.34
    _tdome(L, place, 0, d * 0.5, base + 0.5, r * 1.05, r * 0.35, seg=8, rings=1)     # drum ring base
    _tbox(L, place, -r, d * 0.5 - r, base + 0.5, r, d * 0.5 + r, base + 0.5 + r * 0.5)  # drum
    _tdome(L, place, 0, d * 0.5, base + 0.5 + r * 0.5, r, r * rng.uniform(0.9, 1.2))
    _tspire(L, place, 0, d * 0.5, base + 0.5 + r * 0.5 + r, r * 0.16, r * 0.9)         # lantern finial
    for sx in (-1, 1):
        _tpin(L, place, sx * (w / 2 - 0.3), d * 0.5, base + 0.5, w * 0.05, base * 0.3)


def _bld_cathedral(L, D, place, w, h, rng):
    nave_w = w * 0.46
    d = w * 0.72
    _tbox(L, place, -nave_w / 2, 0, 0, nave_w / 2, d, h)
    _tgable(L, place, -nave_w / 2, nave_w / 2, 0, d, h, w * 0.22)
    _facade(L, D, place, -nave_w / 2, nave_w / 2, 2.0, h - 1.5, rng, bays=3)
    _tdisc(D, place, 0, -0.12, h * 0.78, w * 0.085)                       # rose window
    _tbox(D, place, -nave_w * 0.18, -0.14, 1.5, nave_w * 0.18, 0.03, h * 0.5)  # great portal
    for sx in (-1, 1):                                                    # aisle lean-tos
        _tbox(L, place, sx * nave_w / 2, 0, 0, sx * (nave_w / 2 + w * 0.13), d, h * 0.55)
        _facade(L, D, place, min(sx * nave_w / 2, sx * (nave_w / 2 + w * 0.13)),
                max(sx * nave_w / 2, sx * (nave_w / 2 + w * 0.13)), 1.0, h * 0.5, rng, bays=2, arched=True)
    for sx in (-1, 1):                                                    # twin west towers
        tx = sx * (nave_w / 2 + w * 0.2)
        tw = w * 0.2
        _tbox(L, place, tx - tw / 2, 0, 0, tx + tw / 2, d * 0.8, h * 1.18)
        _facade(L, D, place, tx - tw * 0.4, tx + tw * 0.4, h * 0.35, h * 1.1, rng, bays=1)
        for sy in (0, 1):
            for sxx in (-1, 1):
                _tpin(L, place, tx + sxx * tw * 0.42, sy * d * 0.8, h * 1.18, tw * 0.12, h * 0.2)
        _tspire(L, place, tx, d * 0.4, h * 1.18, tw * 0.5, h * rng.uniform(0.5, 0.75))
    _tspire(L, place, 0, d * 0.55, h + w * 0.22, w * 0.06, h * 0.4)        # crossing flèche


def _pano_building(bm, dbm, ang, R, w, h, kind, rng, z0=0.0):
    place = _placer(ang, R, z0)
    {"cathedral": _bld_cathedral, "tower": _bld_tower, "dome": _bld_dome,
     "tiered": _bld_tiered}.get(kind, _bld_hall)(bm, dbm, place, w, h, rng)


def city_panorama(seed=3):
    """The kingdom's horizon: a continuous 360 deg skyline of DISTINCT Anor-Londo
    monuments — buttressed cathedrals, belfry towers, domed halls and tiered
    palaces — ringed in concentric bands so no viewpoint sees a gap of sky.
    Built as two meshes (warm stone + shadowed openings). Huge (radius to
    ~230 m); place ONCE per open-air area, centred on it. Origin: centre."""
    rng = random.Random(seed)
    bm = bmesh.new()       # warm stone masses
    dbm = bmesh.new()      # shadowed windows / openings
    # (radius, base_h, height_range, hero_chance) — a LOW near ring of rooftops
    # frames the view; the grand cathedrals/towers/domes tower in the mid belts
    # behind it so the skyline reads as distant monuments, not a near brick wall.
    bands = [
        (30, 3, (2, 7), 0.03),      # rooftops on the near slope, just off the terrace
        (55, 9, (7, 20), 0.16),
        (90, 18, (16, 46), 0.28),   # grand belt: cathedrals + towers dominate here
        (140, 26, (24, 64), 0.24),
        (205, 20, (16, 50), 0.10),
    ]
    for bi, (R, base_h, hr, hero) in enumerate(bands):
        n = max(20, int(R * 0.30))
        crest_a, crest_b = rng.uniform(0, math.tau), rng.uniform(0, math.tau)
        a = 0.0
        while a < math.tau - 0.01:
            span = (math.tau / n) * rng.uniform(0.82, 1.35)
            mid = a + span * 0.5
            swell = 0.5 + 0.5 * (0.6 * math.sin(mid * 2 + crest_a) + 0.4 * math.sin(mid * 5 + crest_b))
            h = base_h + rng.uniform(*hr) * (0.35 + 1.15 * swell)
            w = span * R * rng.uniform(0.80, 0.95)          # arc-width of the plot
            w = max(6.0, min(w, R * 0.5))
            rr = R + rng.uniform(-R * 0.04, R * 0.06)
            roll = rng.random()
            slender = bi >= 2                                # grand belts get monuments
            if roll < hero or (swell > 0.78 and roll < hero + 0.16 and slender):
                kind = "cathedral"; h *= 1.2
            elif roll < hero + (0.28 if slender else 0.14):
                kind = "tower"; h *= 1.25
            elif roll < hero + 0.42:
                kind = "dome"
            elif roll < hero + 0.58:
                kind = "tiered"
            else:
                kind = "hall"
            _pano_building(bm, dbm, mid, rr, w, h, kind, rng, _ground_y(rr))
            a += span
    body = V.bm_to_object(bm, "city_panorama", ("M_backdrop",))
    dark = V.bm_to_object(dbm, "city_windows", ("M_backdrop_dark",))
    # the hillside the city stands on: a single continuous surface falling away
    # from the terrace rim so nothing floats and no bare plate is exposed
    gbm = bmesh.new()
    gn = 72
    radii = [14, 20, 28, 40, 58, 84, 122, 175, 260]
    prev = None
    for gr in radii:
        gy = _ground_y(gr)
        ring = [gbm.verts.new((gr * math.cos(math.tau * i / gn), gr * math.sin(math.tau * i / gn), gy))
                for i in range(gn)]
        if prev is None:
            c = gbm.verts.new((0, 0, _ground_y(0.0)))
            for i in range(gn):
                gbm.faces.new((c, ring[i], ring[(i + 1) % gn]))
        else:
            for i in range(gn):
                gbm.faces.new((prev[i], prev[(i + 1) % gn], ring[(i + 1) % gn], ring[i]))
        prev = ring
    ground = V.bm_to_object(gbm, "city_ground", ("M_backdrop",))
    return [body, dark, ground], {"size": [520, 520, 120], "origin": "center"}


BUILDERS = {
    "city_panorama": city_panorama,
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
