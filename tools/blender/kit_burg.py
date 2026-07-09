"""Burg kit: the Old Outskirts' half-timbered town family (DECISIONS D-005
silhouette rules still apply — chunky, painted-fantasy, no photorealism).

A 3 m module against the church kits' 4 m: plastered panels over timber
frames on stone base courses, plank floors, slate gables, steep house
stairs. Origins follow the church kits: wall panels bottom-center with
thickness across Y; floors bottom-center slabs; the gable's origin is the
eave-level center, ridge along X; the stair's origin is the FOOT center,
ascending +Y (in engine: rot 0 climbs toward -Z, like walking north).
"""
import math

import bmesh

import vglib as V

WALL_T = 0.24     # panel thickness
TIMBER = 0.09     # frame stick cross-section


def _frame_stick(bm, a, b, t=TIMBER):
    """Axis-aligned timber from a to b, square cross-section t, proud of
    the plaster on both faces."""
    lo = [min(a[i], b[i]) for i in range(3)]
    hi = [max(a[i], b[i]) for i in range(3)]
    for i in range(3):
        if hi[i] - lo[i] < 0.001:
            lo[i] -= t * 0.5
            hi[i] += t * 0.5
    V.add_box(bm, tuple(lo), tuple(hi))


def _burg_wall(door=False, win=False):
    objs = []
    y = WALL_T * 0.5
    # stone base course (parted at a doorway — a half-metre sill is a wall
    # to move_and_slide, and nobody steps half a metre up into a kitchen)
    bm = bmesh.new()
    if door:
        V.add_box(bm, (-1.5, -y, 0.0), (-0.6, y, 0.5))
        V.add_box(bm, (0.6, -y, 0.0), (1.5, y, 0.5))
    else:
        V.add_box(bm, (-1.5, -y, 0.0), (1.5, y, 0.5))
    objs.append(V.bm_to_object(bm, "base_course", ("M_stone",)))
    # plaster body (with openings carved by panel strips)
    bm = bmesh.new()
    py = y - 0.02
    if door:
        # door opening x -0.6..0.6, z 0..2.25: three plaster panels around it
        V.add_box(bm, (-1.5, -py, 0.5), (-0.6, py, 3.0))
        V.add_box(bm, (0.6, -py, 0.5), (1.5, py, 3.0))
        V.add_box(bm, (-0.6, -py, 2.25), (0.6, py, 3.0))
    elif win:
        # window opening x -0.55..0.55, z 1.4..2.5
        V.add_box(bm, (-1.5, -py, 0.5), (-0.55, py, 3.0))
        V.add_box(bm, (0.55, -py, 0.5), (1.5, py, 3.0))
        V.add_box(bm, (-0.55, -py, 0.5), (0.55, py, 1.4))
        V.add_box(bm, (-0.55, -py, 2.5), (0.55, py, 3.0))
    else:
        V.add_box(bm, (-1.5, -py, 0.5), (1.5, py, 3.0))
    objs.append(V.bm_to_object(bm, "plaster", ("M_wax",)))
    # timber frame: posts, rails, braces
    bm = bmesh.new()
    for x in (-1.5 + TIMBER, 1.5 - TIMBER):
        _frame_stick(bm, (x, 0, 0.5), (x, 0, 3.0))
    _frame_stick(bm, (-1.5, 0, 3.0 - TIMBER * 0.5), (1.5, 0, 3.0 - TIMBER * 0.5))
    if door:
        # the sill rail parts at the doorway: a knee-high timber across an
        # opening is a wall to the capsule, whatever the eye says
        _frame_stick(bm, (-1.5, 0, 0.5 + TIMBER * 0.5), (-0.66, 0, 0.5 + TIMBER * 0.5))
        _frame_stick(bm, (0.66, 0, 0.5 + TIMBER * 0.5), (1.5, 0, 0.5 + TIMBER * 0.5))
    else:
        _frame_stick(bm, (-1.5, 0, 0.5 + TIMBER * 0.5), (1.5, 0, 0.5 + TIMBER * 0.5))
    if door:
        for sx in (-0.66, 0.66):
            _frame_stick(bm, (sx, 0, 0.5), (sx, 0, 2.31))
        _frame_stick(bm, (-0.72, 0, 2.31), (0.72, 0, 2.31))
    elif win:
        for sx in (-0.61, 0.61):
            _frame_stick(bm, (sx, 0, 1.34), (sx, 0, 2.56))
        _frame_stick(bm, (-0.7, 0, 1.34), (0.7, 0, 1.34))
        _frame_stick(bm, (-0.7, 0, 2.56), (0.7, 0, 2.56))
        # shutters swung open on the +Y face
        V.add_box(bm, (-1.05, y, 1.42), (-0.62, y + 0.05, 2.48))
        V.add_box(bm, (0.62, y, 1.42), (1.05, y + 0.05, 2.48))
    else:
        # decorative diagonal brace (two chunky segments, painted-fantasy)
        _frame_stick(bm, (-1.35, 0, 0.68), (-0.1, 0, 1.7))
        _frame_stick(bm, (0.1, 0, 1.8), (1.35, 0, 2.85))
    objs.append(V.bm_to_object(bm, "timbers", ("M_wood",)))
    if win:
        bm = bmesh.new()
        V.add_box(bm, (-0.55, -0.03, 1.4), (0.55, 0.03, 2.5))
        objs.append(V.bm_to_object(bm, "pane", ("M_citywindow",)))
    kind = "door" if door else ("win" if win else "plain")
    return objs, {"size": [3, WALL_T, 3], "origin": "bottom-center",
                  "opening": [1.2, 2.25] if door else None, "variant": kind}


def burg_wall_3m():
    return _burg_wall()


def burg_wall_3m_door():
    return _burg_wall(door=True)


def burg_wall_3m_win():
    return _burg_wall(win=True)


def burg_floor_3m():
    """Plank floor tile 3x3, surface just under nominal like floor_4x4."""
    objs = []
    bm = bmesh.new()
    x = -1.5
    while x < 1.45:
        V.add_box(bm, (x + 0.015, -1.5, -0.2), (x + 0.36, 1.5, -0.02))
        x += 0.375
    objs.append(V.bm_to_object(bm, "planks", ("M_wood",)))
    bm = bmesh.new()
    for yb in (-1.0, 0.0, 1.0):
        V.add_box(bm, (-1.5, yb - 0.07, -0.34), (1.5, yb + 0.07, -0.2))
    objs.append(V.bm_to_object(bm, "joists", ("M_wood",)))
    return objs, {"size": [3, 3, 0.34], "origin": "bottom-center"}


def roof_gable_7m():
    """Gable roof for a 6 m house (7 m with overhang): ridge along X at
    +2.4, eaves at 0, spans Y -3.5..3.5. Origin: eave-level center."""
    objs = []
    for sgn in (-1, 1):
        bm = bmesh.new()
        a = bm.verts.new((-3.5, sgn * 3.5, -0.12))
        b = bm.verts.new((3.5, sgn * 3.5, -0.12))
        c = bm.verts.new((3.5, 0.0, 2.4))
        d = bm.verts.new((-3.5, 0.0, 2.4))
        f = bm.faces.new((a, b, c, d) if sgn > 0 else (d, c, b, a))
        bmesh.ops.solidify(bm, geom=list(bm.faces) + list(bm.verts) + list(bm.edges), thickness=0.1)
        objs.append(V.bm_to_object(bm, "slope", ("M_roof",)))
    # ridge beam + eave fascias
    bm = bmesh.new()
    V.add_box(bm, (-3.55, -0.14, 2.3), (3.55, 0.14, 2.52))
    for sgn in (-1, 1):
        V.add_box(bm, (-3.5, sgn * 3.5 - 0.08, -0.3), (3.5, sgn * 3.5 + 0.08, -0.06))
    objs.append(V.bm_to_object(bm, "ridge", ("M_wood",)))
    # gable-end infill: plastered triangles with a king post
    bm = bmesh.new()
    for ex in (-3.06, 3.06):
        v0 = bm.verts.new((ex, -3.0, 0.0))
        v1 = bm.verts.new((ex, 3.0, 0.0))
        v2 = bm.verts.new((ex, 0.0, 2.32))
        bm.faces.new((v0, v1, v2))
    bmesh.ops.solidify(bm, geom=list(bm.faces) + list(bm.verts) + list(bm.edges), thickness=0.16)
    objs.append(V.bm_to_object(bm, "gables", ("M_wax",)))
    bm = bmesh.new()
    for ex in (-3.0, 3.0):
        _frame_stick(bm, (ex, 0, 0.1), (ex, 0, 2.2), 0.11)
    objs.append(V.bm_to_object(bm, "kingposts", ("M_wood",)))
    return objs, {"size": [7.1, 7.16, 2.62], "origin": "eave-center"}


def chimney_stack():
    objs = []
    bm = bmesh.new()
    V.add_box(bm, (-0.3, -0.3, 0.0), (0.3, 0.3, 2.0))
    V.add_box(bm, (-0.4, -0.4, 2.0), (0.4, 0.4, 2.25))
    V.add_box(bm, (-0.22, -0.22, 2.25), (0.22, 0.22, 2.4))
    objs.append(V.bm_to_object(bm, "stack", ("M_stone",)))
    return objs, {"size": [0.8, 0.8, 2.4], "origin": "bottom-center"}


def balcony_3m():
    """Timber balcony off an upper wall face: deck 3 x 1.25, rails on the
    three open sides, two struts beneath. Origin at the wall face, deck top
    at z=0; the deck extends +Y (away from the wall, like roof_shed)."""
    objs = []
    bm = bmesh.new()
    y = 0.06
    while y < 1.2:
        V.add_box(bm, (-1.5, y, -0.16), (1.5, y + 0.3, -0.02))
        y += 0.36
    # rails
    for sx in (-1.44, 1.44):
        _frame_stick(bm, (sx, 0.06, -0.02), (sx, 1.19, -0.02), 0.07)
    _frame_stick(bm, (-1.44, 1.19, 1.0), (1.44, 1.19, 1.0), 0.08)
    for sx in (-1.44, 1.44):
        _frame_stick(bm, (sx, 1.19, -0.02), (sx, 1.19, 1.0), 0.07)
        _frame_stick(bm, (sx, 0.66, -0.02), (sx, 0.66, 1.0), 0.06)
    _frame_stick(bm, (-1.44, 1.19, 0.55), (1.44, 1.19, 0.55), 0.06)
    # struts
    for sx in (-1.2, 1.2):
        _frame_stick(bm, (sx, 0.06, -1.0), (sx, 1.05, -0.1), 0.1)
    objs.append(V.bm_to_object(bm, "balcony", ("M_wood",)))
    return objs, {"size": [3, 1.25, 2.1], "origin": "wall-face-deck"}


def stair_wood_3m():
    """Steep house stair: 12 treads rising 3.0 over a 3.3 run, 1.4 wide.
    Origin at the FOOT center; ascends +Y (engine: rot 0 climbs -Z).
    Collides as a ramp (AreaBuilder special-cases it like the grand stair)."""
    objs = []
    bm = bmesh.new()
    rise, run, n = 0.25, 0.272, 12
    for i in range(n):
        y0 = i * run
        # each tread drops solid to the floor: an open-riser flight reads
        # as floating from below, and the player called it out
        V.add_box(bm, (-0.7, y0, 0.0), (0.7, y0 + run + 0.04, (i + 1) * rise))
    # foot winder on the open (+X) side: three side-steps turning into the
    # flight, the visible answer to the rolled entry bands in the collider
    V.add_box(bm, (1.3, 0.0, 0.0), (1.75, 1.5, 0.2))
    V.add_box(bm, (0.95, 0.0, 0.0), (1.3, 1.5, 0.45))
    V.add_box(bm, (0.7, 0.0, 0.0), (0.95, 1.5, 0.72))
    objs.append(V.bm_to_object(bm, "treads", ("M_wood",)))
    bm = bmesh.new()
    for sx in (-0.7, 0.66):
        a = bm.verts.new((sx, 0.0, 0.0))
        b = bm.verts.new((sx, n * run + 0.04, (n - 1) * rise))
        c = bm.verts.new((sx, n * run + 0.04, n * rise + 0.1))
        d = bm.verts.new((sx, 0.0, 0.35))
        bm.faces.new((a, b, c, d))
    bmesh.ops.solidify(bm, geom=list(bm.faces) + list(bm.verts) + list(bm.edges), thickness=0.04)
    objs.append(V.bm_to_object(bm, "stringers", ("M_wood",)))
    return objs, {"size": [1.4, 3.31, 3.1], "origin": "foot-center", "rise": 3.0}


def barrel():
    objs = []
    rings = [(0.26, 0.0, 10, 0), (0.32, 0.22, 10, 0), (0.34, 0.45, 10, 0),
             (0.32, 0.68, 10, 0), (0.26, 0.9, 10, 0)]
    objs.append(V.loft_rings("staves", rings, "M_wood"))
    for z in (0.16, 0.72):
        objs.append(V.loft_rings("hoop", [(0.345, z - 0.03, 10, 0), (0.345, z + 0.03, 10, 0)], "M_iron"))
    return objs, {"size": [0.7, 0.7, 0.9], "origin": "bottom-center"}


def crate_stack():
    objs = []
    bm = bmesh.new()
    V.add_box(bm, (-0.45, -0.45, 0.0), (0.45, 0.45, 0.8))
    V.add_box(bm, (-0.38, -0.05, 0.8), (0.42, 0.72, 1.44))
    for z in (0.03, 0.75, 0.84, 1.4):
        V.add_box(bm, (-0.47, -0.47, z), (0.47, 0.47, z + 0.05)) if z < 0.8 else \
            V.add_box(bm, (-0.4, -0.07, z), (0.44, 0.74, z + 0.04))
    objs.append(V.bm_to_object(bm, "crates", ("M_wood",)))
    return objs, {"size": [1.0, 1.0, 1.45], "origin": "bottom-center"}


def hand_cart():
    objs = []
    bm = bmesh.new()
    V.add_box(bm, (-0.55, -0.9, 0.5), (0.55, 0.9, 0.62))          # bed
    for sy in (-0.85, 0.85):
        V.add_box(bm, (-0.55, sy - 0.04, 0.62), (0.55, sy + 0.04, 0.95))
    objs.append(V.bm_to_object(bm, "cart", ("M_wood",)))
    # pull shafts: rooted under the bed, sloping to their resting grips
    bm = bmesh.new()
    for sx in (-0.5, 0.42):
        a = bm.verts.new((sx, 0.6, 0.56))
        b = bm.verts.new((sx, 2.0, 0.34))
        c = bm.verts.new((sx, 2.0, 0.24))
        d = bm.verts.new((sx, 0.6, 0.46))
        bm.faces.new((a, b, c, d))
    bmesh.ops.solidify(bm, geom=list(bm.faces) + list(bm.verts) + list(bm.edges), thickness=0.08)
    objs.append(V.bm_to_object(bm, "shafts", ("M_wood",)))
    for sx in (-0.62, 0.62):
        w = V.loft_rings("wheel", [(0.32, -0.03, 12, 0), (0.32, 0.03, 12, 0)], "M_wood")
        w.rotation_euler = (0, math.pi / 2, 0)
        w.location = (sx, 0.0, 0.32)
        objs.append(w)
    return objs, {"size": [1.4, 3.0, 0.95], "origin": "bottom-center"}


def _burg_wall_ruin(profile, posts, beam=None):
    """A fire-gutted panel: full base course, plaster snapped to a jagged
    profile, charred posts. profile: list of (x0, x1, top)."""
    objs = []
    y = WALL_T * 0.5
    bm = bmesh.new()
    V.add_box(bm, (-1.5, -y, 0.0), (1.5, y, 0.5))
    objs.append(V.bm_to_object(bm, "base_course", ("M_stone",)))
    bm = bmesh.new()
    py = y - 0.02
    for x0, x1, top in profile:
        V.add_box(bm, (x0, -py, 0.5), (x1, py, top))
    objs.append(V.bm_to_object(bm, "plaster", ("M_wax",)))
    bm = bmesh.new()
    for px, top in posts:
        _frame_stick(bm, (px, 0, 0.5), (px, 0, top))
    if beam:
        _frame_stick(bm, (beam[0], 0, beam[2]), (beam[1], 0, beam[2]))
    objs.append(V.bm_to_object(bm, "timbers", ("M_stone_dark",)))
    top_z = max(p[2] for p in profile)
    return objs, {"size": [3, WALL_T, top_z], "origin": "bottom-center"}


def burg_wall_3m_ruin_a():
    return _burg_wall_ruin(
        [(-1.5, -0.4, 1.25), (-0.4, 0.7, 0.85), (0.7, 1.5, 1.05)],
        [(-1.41, 1.6)])


def burg_wall_3m_ruin_b():
    return _burg_wall_ruin(
        [(-1.5, -0.9, 2.6), (-0.9, -0.1, 1.9), (-0.1, 0.6, 1.1), (0.6, 1.5, 2.3)],
        [(-1.41, 2.7), (1.41, 2.45)], beam=(-1.5, -0.2, 2.52))


def parish_window_4m():
    """Parish nave bay: stone wall with a glowing twin lancet, matching
    wall_4x4's module (4 x 4, bottom-center, 0.5 thick)."""
    objs = []
    y = 0.25
    bm = bmesh.new()
    V.add_box(bm, (-2, -y, 0.0), (2, y, 0.9))                     # footing band
    V.add_box(bm, (-2, -y, 0.9), (-1.25, y, 4.0))                 # piers
    V.add_box(bm, (-0.35, -y, 0.9), (0.35, y, 4.0))
    V.add_box(bm, (1.25, -y, 0.9), (2, y, 4.0))
    V.add_box(bm, (-2, -y, 3.45), (2, y, 4.0))                    # head band
    for s in (-1, 1):                                             # stepped heads
        V.add_box(bm, (s * 1.25 - (0.2 if s > 0 else 0), -y, 3.0),
                  (s * 1.25 + (0.2 if s < 0 else 0), y, 3.45))
        V.add_box(bm, (s * 0.35 - (0.2 if s < 0 else 0), -y, 3.0),
                  (s * 0.35 + (0.2 if s > 0 else 0), y, 3.45))
    objs.append(V.bm_to_object(bm, "wall", ("M_stone",)))
    bm = bmesh.new()
    V.add_box(bm, (-1.4, -y - 0.06, 0.78), (1.4, y + 0.06, 0.94))  # sill
    V.add_box(bm, (-1.4, -y - 0.06, 3.42), (1.4, y + 0.06, 3.58))  # hood
    objs.append(V.bm_to_object(bm, "trim", ("M_stone_trim",)))
    bm = bmesh.new()
    for s in (-1, 1):
        V.add_box(bm, (s * 0.35, -0.04, 0.9), (s * 1.25, 0.04, 3.0))
        V.add_box(bm, (s * 0.55, -0.04, 3.0), (s * 1.05, 0.04, 3.42))
    objs.append(V.bm_to_object(bm, "panes", ("M_citywindow",)))
    return objs, {"size": [4, 0.5, 4], "origin": "bottom-center"}


def clock_tower():
    """The parish clocktower: stone shaft, pale dial stopped at nine on the
    +Y face (engine: faces south when placed rot 180), dark belfry stage,
    slate spire, gilt finial. Origin bottom-center."""
    objs = []
    bm = bmesh.new()
    V.add_box(bm, (-2, -2, 0.0), (2, 2, 7.6))                      # shaft
    V.add_box(bm, (-1.7, -1.7, 7.6), (1.7, 1.7, 9.6))              # belfry stage
    objs.append(V.bm_to_object(bm, "shaft", ("M_stone",)))
    bm = bmesh.new()
    for sx, sy in ((-1, -1), (-1, 1), (1, -1), (1, 1)):            # corner quoins
        V.add_box(bm, (sx * 2 - 0.14, sy * 2 - 0.14, 0.0),
                  (sx * 2 + 0.14, sy * 2 + 0.14, 7.75))
    V.add_box(bm, (-1.95, -1.95, 9.6), (1.95, 1.95, 9.95))         # cornice
    objs.append(V.bm_to_object(bm, "trim", ("M_stone_trim",)))
    bm = bmesh.new()                                               # sound louvres
    for face in range(4):
        ang = math.radians(90 * face)
        c, s = math.cos(ang), math.sin(ang)
        lo = (-0.5 * c - 1.705 * s, -0.5 * s + 1.705 * c)
        hi = (0.5 * c - 1.86 * s, 0.5 * s + 1.86 * c)
        V.add_box(bm, (min(lo[0], hi[0]), min(lo[1], hi[1]), 7.9),
                  (max(lo[0], hi[0]), max(lo[1], hi[1]), 9.3))
    objs.append(V.bm_to_object(bm, "louvres", ("M_stone_dark",)))
    # the dial: pale disc, iron rim ticks, hands stopped at nine
    dial = V.loft_rings("dial", [(0.95, -0.035, 18, 0), (0.95, 0.035, 18, 0)], "M_wax")
    dial.rotation_euler = (math.pi / 2, 0, 0)
    dial.location = (0, 2.06, 5.9)
    objs.append(dial)
    bm = bmesh.new()
    V.add_box(bm, (-0.05, 2.09, 5.9), (0.05, 2.15, 6.62))          # minute hand up
    V.add_box(bm, (-0.62, 2.09, 5.85), (0.0, 2.15, 5.95))          # hour hand west
    for tx, tz in ((0, 6.72), (0, 5.08), (-0.82, 5.9), (0.82, 5.9)):
        V.add_box(bm, (tx - 0.06, 2.09, tz - 0.06), (tx + 0.06, 2.15, tz + 0.06))
    objs.append(V.bm_to_object(bm, "hands", ("M_iron",)))
    # spire: four slate faces to an apex, gilt orb finial
    bm = bmesh.new()
    apex = bm.verts.new((0.0, 0.0, 13.4))
    ring = [bm.verts.new(p) for p in
            ((-1.9, -1.9, 9.95), (1.9, -1.9, 9.95), (1.9, 1.9, 9.95), (-1.9, 1.9, 9.95))]
    for i in range(4):
        bm.faces.new((ring[i], ring[(i + 1) % 4], apex))
    bmesh.ops.solidify(bm, geom=list(bm.faces) + list(bm.verts) + list(bm.edges), thickness=0.1)
    objs.append(V.bm_to_object(bm, "spire", ("M_roof",)))
    bm = bmesh.new()
    V.add_box(bm, (-0.06, -0.06, 13.3), (0.06, 0.06, 14.1))
    objs.append(V.bm_to_object(bm, "finial", ("M_iron",)))
    orb = V.loft_rings("orb", [(0.05, 14.05, 10, 0), (0.22, 14.22, 10, 0), (0.05, 14.4, 10, 0)], "M_gold")
    objs.append(orb)
    return objs, {"size": [4, 4, 14.4], "origin": "bottom-center"}


def word_stone():
    """A graven wayside stone: one of the parish's three words sleeps in
    it. Gilt script strokes on the +Y face."""
    objs = []
    bm = bmesh.new()
    V.add_box(bm, (-0.3, -0.22, 0.0), (0.3, 0.22, 0.18))
    objs.append(V.bm_to_object(bm, "plinth", ("M_stone",)))
    bm = bmesh.new()
    V.add_box(bm, (-0.26, -0.09, 0.18), (0.26, 0.09, 1.05))
    objs.append(V.bm_to_object(bm, "tablet", ("M_stone_trim",)))
    bm = bmesh.new()
    for z0, x0, x1 in ((0.78, -0.16, 0.16), (0.6, -0.12, 0.19), (0.42, -0.17, 0.1)):
        V.add_box(bm, (x0, 0.09, z0), (x1, 0.125, z0 + 0.07))
    objs.append(V.bm_to_object(bm, "script", ("M_gold",)))
    stub = V.loft_rings("waxstub", [(0.06, 0.18, 8, 0), (0.05, 0.31, 8, 0)], "M_wax")
    stub.location = (0.0, -0.14, 0.0)
    objs.append(stub)
    return objs, {"size": [0.6, 0.45, 1.05], "origin": "bottom-center"}


def torch_held():
    """A hand torch: shaft up +Z from the grip origin (engine: blade +Y),
    iron collar, waxed head, a fat flame knot."""
    objs = []
    bm = bmesh.new()
    V.add_box(bm, (-0.03, -0.03, 0.0), (0.03, 0.03, 0.6))
    objs.append(V.bm_to_object(bm, "shaft", ("M_wood",)))
    bm = bmesh.new()
    V.add_box(bm, (-0.05, -0.05, 0.52), (0.05, 0.05, 0.6))
    objs.append(V.bm_to_object(bm, "collar", ("M_iron",)))
    head = V.loft_rings("head", [(0.05, 0.6, 8, 0), (0.075, 0.72, 8, 0), (0.05, 0.8, 8, 0)], "M_wax")
    objs.append(head)
    flame = V.loft_rings("flame", [(0.02, 0.78, 8, 0), (0.075, 0.88, 8, 0), (0.01, 1.02, 8, 0)], "M_gold")
    objs.append(flame)
    return objs, {"size": [0.16, 0.16, 1.02], "origin": "grip-center"}


BUILDERS = {
    "burg_wall_3m": burg_wall_3m,
    "burg_wall_3m_door": burg_wall_3m_door,
    "burg_wall_3m_win": burg_wall_3m_win,
    "burg_wall_3m_ruin_a": burg_wall_3m_ruin_a,
    "burg_wall_3m_ruin_b": burg_wall_3m_ruin_b,
    "burg_floor_3m": burg_floor_3m,
    "roof_gable_7m": roof_gable_7m,
    "chimney_stack": chimney_stack,
    "balcony_3m": balcony_3m,
    "stair_wood_3m": stair_wood_3m,
    "parish_window_4m": parish_window_4m,
    "clock_tower": clock_tower,
    "word_stone": word_stone,
    "barrel": barrel,
    "crate_stack": crate_stack,
    "hand_cart": hand_cart,
    "torch_held": torch_held,
}
