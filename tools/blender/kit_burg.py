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
    """Timber beam from a to b, cross-section t, proud of the plaster on both
    faces when placed on the wall plane (y=0), and properly oriented when
    diagonal (wall braces or balcony struts)."""
    dx, dy, dz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
    on_wall_plane = (abs(a[1]) < 0.001 and abs(b[1]) < 0.001 and abs(a[0]) < 2.0 and abs(b[0]) < 2.0)
    y_half = WALL_T * 0.5 if on_wall_plane else t * 0.5

    # Diagonal brace in X-Z plane (e.g. half-timber wall braces)
    if abs(dx) > 0.001 and abs(dz) > 0.001 and abs(dy) < 0.001:
        L = math.hypot(dx, dz)
        nx, nz = -dz / L * (t * 0.5), dx / L * (t * 0.5)
        y0, y1 = a[1] - y_half, a[1] + y_half
        pts_xz = [
            (a[0] - nx, a[2] - nz),
            (a[0] + nx, a[2] + nz),
            (b[0] + nx, b[2] + nz),
            (b[0] - nx, b[2] - nz),
        ]
        vf = [bm.verts.new((px, y0, pz)) for (px, pz) in pts_xz]
        vb = [bm.verts.new((px, y1, pz)) for (px, pz) in pts_xz]
        new_faces = [bm.faces.new(vf), bm.faces.new(tuple(reversed(vb)))]
        for i in range(4):
            j = (i + 1) % 4
            new_faces.append(bm.faces.new((vf[i], vf[j], vb[j], vb[i])))
        # winding depends on the brace's slope sign: let bmesh orient the
        # closed prism outward, or the broad faces cull and only the thin
        # sides render (a hairline brace)
        bmesh.ops.recalc_face_normals(bm, faces=new_faces)
        return

    # Diagonal strut in Y-Z plane (e.g. balcony under-struts)
    if abs(dy) > 0.001 and abs(dz) > 0.001 and abs(dx) < 0.001:
        L = math.hypot(dy, dz)
        ny, nz = -dz / L * (t * 0.5), dy / L * (t * 0.5)
        x0, x1 = a[0] - t * 0.5, a[0] + t * 0.5
        pts_yz = [
            (a[1] - ny, a[2] - nz),
            (a[1] + ny, a[2] + nz),
            (b[1] + ny, b[2] + nz),
            (b[1] - ny, b[2] - nz),
        ]
        vf = [bm.verts.new((x0, py, pz)) for (py, pz) in pts_yz]
        vb = [bm.verts.new((x1, py, pz)) for (py, pz) in pts_yz]
        new_faces = [bm.faces.new(tuple(reversed(vf))), bm.faces.new(vb)]
        for i in range(4):
            j = (i + 1) % 4
            new_faces.append(bm.faces.new((vf[i], vf[j], vb[j], vb[i])))
        bmesh.ops.recalc_face_normals(bm, faces=new_faces)
        return

    lo = [min(a[i], b[i]) for i in range(3)]
    hi = [max(a[i], b[i]) for i in range(3)]
    for i in range(3):
        if hi[i] - lo[i] < 0.001:
            half = y_half if i == 1 else t * 0.5
            lo[i] -= half
            hi[i] += half
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
        # shutters swung open on the +Y face, with cross-battens and wrought-iron strap hinges
        V.add_box(bm, (-1.05, y, 1.42), (-0.62, y + 0.05, 2.48))
        V.add_box(bm, (0.62, y, 1.42), (1.05, y + 0.05, 2.48))
        for zb in (1.56, 2.34):
            V.add_box(bm, (-1.04, y + 0.04, zb - 0.03), (-0.63, y + 0.075, zb + 0.03))
            V.add_box(bm, (0.63, y + 0.04, zb - 0.03), (1.04, y + 0.075, zb + 0.03))
    else:
        # decorative diagonal brace (two chunky segments, painted-fantasy)
        _frame_stick(bm, (-1.35, 0, 0.68), (-0.1, 0, 1.7))
        _frame_stick(bm, (0.1, 0, 1.8), (1.35, 0, 2.85))
    objs.append(V.bm_to_object(bm, "timbers", ("M_wood",)))
    if win:
        bm = bmesh.new()
        V.add_box(bm, (-0.55, -0.03, 1.4), (0.55, 0.03, 2.5))
        objs.append(V.bm_to_object(bm, "pane", ("M_citywindow",)))
        bm_munt = bmesh.new()
        V.add_box(bm_munt, (-0.025, -0.05, 1.4), (0.025, 0.05, 2.5))
        V.add_box(bm_munt, (-0.55, -0.05, 1.92), (0.55, 0.05, 1.97))
        for zb in (1.56, 2.34):
            V.add_box(bm_munt, (-0.82, y + 0.045, zb - 0.018), (-0.58, y + 0.082, zb + 0.018))
            V.add_box(bm_munt, (0.58, y + 0.045, zb - 0.018), (0.82, y + 0.082, zb + 0.018))
        objs.append(V.bm_to_object(bm_munt, "win_iron", ("M_iron",)))
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
        bm.faces.new((a, b, c, d) if sgn > 0 else (d, c, b, a))
        bmesh.ops.solidify(bm, geom=list(bm.faces) + list(bm.verts) + list(bm.edges), thickness=0.1)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        objs.append(V.bm_to_object(bm, "slope", ("M_roof",)))
    # ridge beam + eave fascias
    bm = bmesh.new()
    V.add_box(bm, (-3.55, -0.14, 2.3), (3.55, 0.14, 2.52))
    for sgn in (-1, 1):
        V.add_box(bm, (-3.5, sgn * 3.5 - 0.08, -0.3), (3.5, sgn * 3.5 + 0.08, -0.06))
    objs.append(V.bm_to_object(bm, "ridge", ("M_wood",)))
    # gable-end infill: plastered triangles recessed inside the half-timber frame
    bm = bmesh.new()
    px = WALL_T * 0.5 - 0.02
    for ex in (-3.0, 3.0):
        vf = [bm.verts.new((ex - px, -3.0, 0.0)), bm.verts.new((ex - px, 3.0, 0.0)), bm.verts.new((ex - px, 0.0, 2.32))]
        vb = [bm.verts.new((ex + px, -3.0, 0.0)), bm.verts.new((ex + px, 3.0, 0.0)), bm.verts.new((ex + px, 0.0, 2.32))]
        bm.faces.new(vf)
        bm.faces.new(tuple(reversed(vb)))
        for i in range(3):
            j = (i + 1) % 3
            bm.faces.new((vf[i], vf[j], vb[j], vb[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    objs.append(V.bm_to_object(bm, "gables", ("M_wax",)))
    # half-timber gable framing (proud of plaster on both faces): kingpost, collar beam, queen posts
    bm = bmesh.new()
    tx = WALL_T * 0.5
    for ex in (-3.0, 3.0):
        V.add_box(bm, (ex - tx, -0.055, 0.0), (ex + tx, 0.055, 2.30))
        V.add_box(bm, (ex - tx, -1.62, 1.00), (ex + tx, 1.62, 1.09))
        for sy in (-1.35, 1.35):
            V.add_box(bm, (ex - tx, sy - 0.045, 0.0), (ex + tx, sy + 0.045, 1.24))
    objs.append(V.bm_to_object(bm, "kingposts", ("M_wood",)))
    return objs, {"size": [7.1, 7.16, 2.62], "origin": "eave-center"}


def chimney_stack():
    """Masonry house chimney stack with stepped corbelled base, chamfered stone
    cornice cap, and cylindrical dark terracotta flue pot."""
    objs = []
    bm = bmesh.new()
    V.add_box(bm, (-0.34, -0.34, 0.0), (0.34, 0.34, 0.35))
    V.add_box(bm, (-0.30, -0.30, 0.35), (0.30, 0.30, 1.96))
    objs.append(V.bm_to_object(bm, "stack", ("M_stone",)))

    bm_trim = bmesh.new()
    V.add_box(bm_trim, (-0.33, -0.33, 1.42), (0.33, 0.33, 1.50))
    V.add_box(bm_trim, (-0.36, -0.36, 1.96), (0.36, 0.36, 2.06))
    V.add_box(bm_trim, (-0.42, -0.42, 2.06), (0.42, 0.42, 2.22))
    V.add_box(bm_trim, (-0.34, -0.34, 2.22), (0.34, 0.34, 2.28))
    objs.append(V.bm_to_object(bm_trim, "stack_trim", ("M_stone_trim",)))

    pot = V.loft_rings("stack_pot", [
        (0.18, 2.28, 12, 0),
        (0.16, 2.48, 12, 0),
        (0.20, 2.52, 12, 0),
        (0.17, 2.56, 12, 0),
        (0.125, 2.56, 12, 0),
        (0.115, 2.38, 12, 0),
    ], "M_stone_dark", cap_bottom=False, cap_top=True)
    objs.append(pot)
    return objs, {"size": [0.84, 0.84, 2.56], "origin": "bottom-center"}


def balcony_3m():
    """Timber balcony off an upper wall face: deck 3 x 1.25, rails and turned
    balusters on the three open sides, two struts beneath, and wrought-iron
    corner/wall bracket straps. Origin at the wall face, deck top at z=0; the
    deck extends +Y (away from the wall, like roof_shed)."""
    objs = []
    bm = bmesh.new()
    y = 0.06
    while y < 1.2:
        V.add_box(bm, (-1.5, y, -0.16), (1.5, y + 0.3, -0.02))
        y += 0.36
    # Outer deck fascia rim
    V.add_box(bm, (-1.52, 1.18, -0.20), (1.52, 1.24, 0.0))
    for sx in (-1.52, 1.46):
        V.add_box(bm, (sx, 0.04, -0.20), (sx + 0.06, 1.24, 0.0))
    # Top, mid, and bottom rails on all three open sides
    for sx in (-1.44, 1.44):
        _frame_stick(bm, (sx, 0.06, -0.02), (sx, 1.19, -0.02), 0.07)
        _frame_stick(bm, (sx, 0.06, 0.55), (sx, 1.19, 0.55), 0.055)
        _frame_stick(bm, (sx, 0.06, 1.0), (sx, 1.19, 1.0), 0.075)
    _frame_stick(bm, (-1.44, 1.19, -0.02), (1.44, 1.19, -0.02), 0.07)
    _frame_stick(bm, (-1.44, 1.19, 0.55), (1.44, 1.19, 0.55), 0.06)
    _frame_stick(bm, (-1.44, 1.19, 1.0), (1.44, 1.19, 1.0), 0.08)
    # Corner newel posts + finials, side balusters, and 7 front balusters
    for sx in (-1.44, 1.44):
        _frame_stick(bm, (sx, 0.08, -0.02), (sx, 0.08, 1.06), 0.075)
        _frame_stick(bm, (sx, 1.19, -0.02), (sx, 1.19, 1.08), 0.08)
        V.add_box(bm, (sx - 0.055, 1.19 - 0.055, 1.06), (sx + 0.055, 1.19 + 0.055, 1.12))
        for sy in (0.42, 0.80):
            _frame_stick(bm, (sx, sy, -0.02), (sx, sy, 1.0), 0.05)
    for bx in (-1.08, -0.72, -0.36, 0.0, 0.36, 0.72, 1.08):
        _frame_stick(bm, (bx, 1.19, -0.02), (bx, 1.19, 1.0), 0.052)
    # Under-deck knee struts
    for sx in (-1.2, 1.2):
        _frame_stick(bm, (sx, 0.06, -1.0), (sx, 1.05, -0.1), 0.1)
        _frame_stick(bm, (sx, 0.06, -1.02), (sx, 0.12, -0.02), 0.09)
    objs.append(V.bm_to_object(bm, "balcony", ("M_wood",)))

    bm_iron = bmesh.new()
    for sx in (-1.44, 1.44):
        V.add_box(bm_iron, (sx - 0.05, 1.14, 0.94), (sx + 0.05, 1.24, 1.02))
        V.add_box(bm_iron, (sx - 0.05, 1.14, 0.51), (sx + 0.05, 1.24, 0.58))
        V.add_box(bm_iron, (sx - 0.05, 0.02, 0.94), (sx + 0.05, 0.14, 1.02))
    for sx in (-1.2, 1.2):
        V.add_box(bm_iron, (sx - 0.06, 0.02, -0.98), (sx + 0.06, 0.14, -0.86))
    objs.append(V.bm_to_object(bm_iron, "balcony_iron", ("M_iron",)))
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
    """Coopers' oak cask: 14-sided swelled stave body with recessed top/bottom
    head lids inside raised chime rims, 4 wrought-iron hoops, and a belly bung."""
    objs = []
    n = 14
    rings = [
        (0.26, 0.0, n, 0),
        (0.28, 0.06, n, 0),
        (0.325, 0.24, n, 0),
        (0.345, 0.45, n, 0),
        (0.325, 0.66, n, 0),
        (0.28, 0.84, n, 0),
        (0.26, 0.90, n, 0),
        (0.235, 0.90, n, 0),
        (0.235, 0.86, n, 0),
    ]
    objs.append(V.loft_rings("staves", rings, "M_wood", cap_bottom=True, cap_top=True))
    for idx, (z, r) in enumerate(((0.06, 0.286), (0.24, 0.332), (0.66, 0.332), (0.84, 0.286))):
        nm = "hoop" if idx == 0 else ("hoop_%d" % idx)
        ri = r - 0.022
        objs.append(V.loft_rings(
            nm,
            [
                (ri, z - 0.024, n, 0),
                (r, z - 0.024, n, 0),
                (r, z + 0.024, n, 0),
                (ri, z + 0.024, n, 0),
                (ri, z - 0.024, n, 0),
            ],
            "M_iron",
            cap_bottom=False,
            cap_top=False,
        ))
    bm_iron = bmesh.new()
    V.add_box(bm_iron, (-0.048, 0.330, 0.402), (0.048, 0.352, 0.498))
    V.add_cyl(bm_iron, 0.0, 0.340, 0.43, 0.04, 0.032, n=8)
    objs.append(V.bm_to_object(bm_iron, "barrel_bung", ("M_iron",)))
    return objs, {"size": [0.7, 0.7, 0.9], "origin": "bottom-center"}


def crate_stack():
    """Two stacked merchant cargo crates with recessed plank sides, corner stiles,
    top/bottom frame rails, diagonal timber cross-braces, slatted lids, and
    wrought-iron corner brackets."""
    objs = []
    bm = bmesh.new()
    bm_iron = bmesh.new()

    def _build_crate(x0, x1, y0, y1, z0, z1, st=0.045):
        # Recessed plank core
        V.add_box(bm, (x0 + 0.02, y0 + 0.02, z0 + 0.02), (x1 - 0.02, y1 - 0.02, z1 - 0.02))
        # Top and bottom perimeter frame bands + slatted top lid planks
        for zb0, zb1 in ((z0, z0 + st), (z1 - st, z1)):
            V.add_box(bm, (x0, y0, zb0), (x1, y0 + st, zb1))
            V.add_box(bm, (x0, y1 - st, zb0), (x1, y1, zb1))
            V.add_box(bm, (x0, y0 + st, zb0), (x0 + st, y1 - st, zb1))
            V.add_box(bm, (x1 - st, y0 + st, zb0), (x1, y1 - st, zb1))
        # 4 vertical corner stiles
        for cx in (x0, x1 - st):
            for cy in (y0, y1 - st):
                V.add_box(bm, (cx, cy, z0 + st), (cx + st, cy + st, z1 - st))
        # Continuous diagonal cross-brace battens on all 4 vertical faces
        for fy in (y0 + 0.011, y1 - 0.011):
            _frame_stick(bm, (x0 + st, fy, z0 + st), (x1 - st, fy, z1 - st), 0.044)
        for fx in (x0 + 0.011, x1 - 0.011):
            _frame_stick(bm, (fx, y0 + st, z0 + st), (fx, y1 - st, z1 - st), 0.044)
        # Slatted top lid planks
        n_planks = 4
        pw = (x1 - x0 - 0.04) / n_planks
        for pi in range(n_planks):
            px0 = x0 + 0.02 + pi * pw + 0.006
            px1 = x0 + 0.02 + (pi + 1) * pw - 0.006
            V.add_box(bm, (px0, y0 + 0.02, z1 - 0.02), (px1, y1 - 0.02, z1 + 0.008))
        # Wrought-iron corner straps
        for cx in (x0 - 0.006, x1 - 0.054):
            for cy in (y0 - 0.006, y1 - 0.054):
                for cz in (z0 + 0.005, z1 - 0.045):
                    V.add_box(bm_iron, (cx, cy, cz), (cx + 0.06, cy + 0.06, cz + 0.04))

    _build_crate(-0.46, 0.46, -0.46, 0.46, 0.0, 0.80, st=0.05)
    _build_crate(-0.39, 0.43, -0.06, 0.73, 0.80, 1.44, st=0.042)
    objs.append(V.bm_to_object(bm, "crates", ("M_wood",)))
    objs.append(V.bm_to_object(bm_iron, "crate_iron", ("M_iron",)))
    return objs, {"size": [1.0, 1.0, 1.45], "origin": "bottom-center"}


def hand_cart():
    """Two-wheeled merchant hand-cart: planked bed with slatted side-rails and
    corner stakes, iron-tired 8-spoke wooden wheels on an under-axle, resting
    pull-shafts with prop legs, and a corded cloth cargo bale."""
    objs = []
    bm = bmesh.new()
    # Planked cart bed + cross-bolsters
    V.add_box(bm, (-0.55, -0.90, 0.50), (0.55, 0.90, 0.58))
    for sy in (-0.85, 0.0, 0.85):
        V.add_box(bm, (-0.56, sy - 0.05, 0.44), (0.56, sy + 0.05, 0.50))
    # Corner and mid stake-posts + slatted side & end rails
    for sx in (-0.53, 0.53):
        for sy in (-0.86, 0.0, 0.86):
            V.add_box(bm, (sx - 0.035, sy - 0.035, 0.56), (sx + 0.035, sy + 0.035, 0.96))
        for rz in (0.68, 0.86):
            V.add_box(bm, (sx - 0.025, -0.90, rz), (sx + 0.025, 0.90, rz + 0.06))
    for sy in (-0.86, 0.86):
        for rz in (0.66, 0.84):
            V.add_box(bm, (-0.55, sy - 0.025, rz), (0.55, sy + 0.025, rz + 0.07))
    # Pull shafts rooted under the bed, sloping to resting grips + front prop legs
    for sx in (-0.46, 0.46):
        a = bm.verts.new((sx - 0.035, 0.60, 0.54))
        b = bm.verts.new((sx - 0.035, 2.00, 0.32))
        c = bm.verts.new((sx - 0.035, 2.00, 0.24))
        d = bm.verts.new((sx - 0.035, 0.60, 0.46))
        bm.faces.new((a, b, c, d))
        V.add_box(bm, (sx - 0.03, 1.25, 0.0), (sx + 0.03, 1.31, 0.40))
    bmesh.ops.solidify(bm, geom=[f for f in bm.faces if len(f.verts) == 4 and abs(f.normal.x) > 0.9], thickness=0.07)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    # Spokes for both wheels (8 radial spokes per wheel in X = +-0.62 plane)
    for sx in (-0.62, 0.62):
        for k in range(4):
            ang = k * math.pi / 4.0
            cy, cz = math.cos(ang) * 0.28, math.sin(ang) * 0.28
            py, pz = -math.sin(ang) * 0.022, math.cos(ang) * 0.022
            vf = [
                bm.verts.new((sx - 0.02, -cy - py, 0.34 - cz - pz)),
                bm.verts.new((sx - 0.02, -cy + py, 0.34 - cz + pz)),
                bm.verts.new((sx - 0.02, cy + py, 0.34 + cz + pz)),
                bm.verts.new((sx - 0.02, cy - py, 0.34 + cz - pz)),
            ]
            vb = [bm.verts.new((sx + 0.02, v.co.y, v.co.z)) for v in vf]
            bm.faces.new(tuple(reversed(vf)))
            bm.faces.new(vb)
            for i in range(4):
                j = (i + 1) % 4
                bm.faces.new((vf[i], vf[j], vb[j], vb[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    objs.append(V.bm_to_object(bm, "cart", ("M_wood",)))

    # Iron under-axle and wheel hubs/tires
    bm_iron = bmesh.new()
    V.add_box(bm_iron, (-0.70, -0.04, 0.30), (0.70, 0.04, 0.38))
    objs.append(V.bm_to_object(bm_iron, "cart_axle", ("M_iron",)))

    for sx in (-0.62, 0.62):
        # Hollow wooden felloe rim
        rim = V.loft_rings(
            "wheel_rim",
            [
                (0.33, -0.035, 14, 0),
                (0.33, 0.035, 14, 0),
                (0.26, 0.035, 14, 0),
                (0.26, -0.035, 14, 0),
                (0.33, -0.035, 14, 0),
            ],
            "M_wood",
            cap_bottom=False,
            cap_top=False,
        )
        rim.rotation_euler = (0, math.pi / 2, 0)
        rim.location = (sx, 0.0, 0.34)
        objs.append(rim)
        # Outer 3D closed iron tire hoop + hub
        tire = V.loft_rings(
            "wheel_tire",
            [
                (0.328, -0.038, 14, 0),
                (0.344, -0.038, 14, 0),
                (0.344, 0.038, 14, 0),
                (0.328, 0.038, 14, 0),
                (0.328, -0.038, 14, 0),
            ],
            "M_iron",
            cap_bottom=False,
            cap_top=False,
        )
        tire.rotation_euler = (0, math.pi / 2, 0)
        tire.location = (sx, 0.0, 0.34)
        objs.append(tire)
        hub = V.loft_rings("wheel_hub", [(0.075, -0.06, 10, 0), (0.075, 0.06, 10, 0)], "M_wood")
        hub.rotation_euler = (0, math.pi / 2, 0)
        hub.location = (sx, 0.0, 0.34)
        objs.append(hub)

    # Corded cloth cargo bale resting on the cart bed
    bm_bale = bmesh.new()
    V.add_box(bm_bale, (-0.38, -0.58, 0.58), (0.38, 0.48, 0.90))
    V.add_box(bm_bale, (-0.34, -0.52, 0.90), (0.34, 0.42, 0.96))
    objs.append(V.bm_to_object(bm_bale, "cart_bale", ("M_cloth",)))

    bm_cord = bmesh.new()
    for cy in (-0.32, 0.18):
        V.add_box(bm_cord, (-0.395, cy - 0.022, 0.58), (0.395, cy + 0.022, 0.97))
    V.add_box(bm_cord, (-0.022, -0.595, 0.58), (0.022, 0.495, 0.97))
    objs.append(V.bm_to_object(bm_cord, "cart_cord", ("M_leather",)))
    return objs, {"size": [1.4, 3.0, 0.96], "origin": "bottom-center"}


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
    """Parish nave bay: stone wall with a glowing twin lancet, central stone
    mullion colonnette, chamfered jambs, and wrought-iron glazing saddle-bars,
    matching wall_4x4's module (4 x 4, bottom-center, 0.5 thick)."""
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
    V.add_box(bm, (-1.42, -y - 0.06, 0.78), (1.42, y + 0.06, 0.94))  # sill
    V.add_box(bm, (-1.42, -y - 0.06, 3.42), (1.42, y + 0.06, 3.58))  # hood
    # Chamfered jamb stiles & central engaged mullion colonnettes on both faces
    for sx in (-1.28, -0.32, 0.32, 1.28):
        V.add_box(bm, (sx - 0.06, -y - 0.04, 0.94), (sx + 0.06, y + 0.04, 3.42))
    for sy in (-y - 0.02, y + 0.02):
        V.add_cyl(bm, 0.0, sy, 0.94, 2.48, 0.065, n=10)
        V.add_cyl(bm, 0.0, sy, 0.94, 0.14, 0.095, n=10)
        V.add_cyl(bm, 0.0, sy, 3.28, 0.14, 0.095, n=10)
    objs.append(V.bm_to_object(bm, "trim", ("M_stone_trim",)))
    bm = bmesh.new()
    for s in (-1, 1):
        V.add_box(bm, (s * 0.35, -0.04, 0.9), (s * 1.25, 0.04, 3.0))
        V.add_box(bm, (s * 0.55, -0.04, 3.0), (s * 1.05, 0.04, 3.42))
    objs.append(V.bm_to_object(bm, "panes", ("M_citywindow",)))
    # Wrought-iron glazing muntins & saddle-bars across both lancets
    bm_iron = bmesh.new()
    for s in (-1, 1):
        cx = s * 0.80
        V.add_box(bm_iron, (cx - 0.018, -0.06, 0.92), (cx + 0.018, 0.06, 3.40))
        for zb in (1.45, 2.00, 2.55, 3.00):
            V.add_box(bm_iron, (s * 0.35, -0.06, zb - 0.016), (s * 1.25, 0.06, zb + 0.016))
    objs.append(V.bm_to_object(bm_iron, "window_bars", ("M_iron",)))
    return objs, {"size": [4, 0.5, 4], "origin": "bottom-center"}


def clock_tower():
    """The parish clocktower: stone shaft, pale dial stopped at nine on the
    +Y face (engine: faces south when placed rot 180) with wrought-iron bezel,
    12 radial hour markers, dark belfry stage, slate spire, and gilt finial."""
    objs = []
    bm = bmesh.new()
    V.add_box(bm, (-2, -2, 0.0), (2, 2, 7.6))                      # shaft
    V.add_box(bm, (-1.7, -1.7, 7.6), (1.7, 1.7, 9.6))              # belfry stage
    objs.append(V.bm_to_object(bm, "shaft", ("M_stone",)))
    bm = bmesh.new()
    for sx, sy in ((-1, -1), (-1, 1), (1, -1), (1, 1)):            # corner quoins
        V.add_box(bm, (sx * 2 - 0.14, sy * 2 - 0.14, 0.0),
                  (sx * 2 + 0.14, sy * 2 + 0.14, 7.75))
    V.add_box(bm, (-2.08, -2.08, 4.4), (2.08, 2.08, 4.62))         # mid stringcourse
    V.add_box(bm, (-2.06, -2.06, 7.45), (2.06, 2.06, 7.72))        # belfry stringcourse
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
    # the dial: pale disc, iron outer bezel ring, 12 hour markers, hands stopped at nine
    dial = V.loft_rings("dial", [(0.95, -0.035, 20, 0), (0.95, 0.035, 20, 0)], "M_wax")
    dial.rotation_euler = (math.pi / 2, 0, 0)
    dial.location = (0, 2.06, 5.9)
    objs.append(dial)
    bezel = V.loft_rings("dial_bezel", [
        (1.04, -0.06, 20, 0), (1.04, 0.06, 20, 0),
        (0.92, 0.06, 20, 0), (0.92, -0.06, 20, 0),
        (1.04, -0.06, 20, 0),
    ], "M_iron", cap_bottom=False, cap_top=False)
    bezel.rotation_euler = (math.pi / 2, 0, 0)
    bezel.location = (0, 2.07, 5.9)
    objs.append(bezel)
    bm = bmesh.new()
    V.add_box(bm, (-0.05, 2.09, 5.9), (0.05, 2.15, 6.64))          # minute hand up (12)
    V.add_box(bm, (-0.64, 2.09, 5.85), (0.0, 2.15, 5.95))          # hour hand west (9)
    for hr in range(12):
        ang = math.tau * hr / 12.0
        tx, tz = 0.80 * math.sin(ang), 5.9 + 0.80 * math.cos(ang)
        hw = 0.055 if (hr % 3 == 0) else 0.034
        V.add_box(bm, (tx - hw, 2.09, tz - hw), (tx + hw, 2.15, tz + hw))
    objs.append(V.bm_to_object(bm, "hands", ("M_iron",)))
    # spire: four slate faces to an apex, gilt orb finial + central dial boss
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
    hub = V.loft_rings("dial_hub", [(0.11, -0.02, 12, 0), (0.11, 0.05, 12, 0), (0.03, 0.09, 12, 0)], "M_gold")
    hub.rotation_euler = (math.pi / 2, 0, 0)
    hub.location = (0, 2.12, 5.9)
    objs.append(hub)
    return objs, {"size": [4, 4, 14.4], "origin": "bottom-center"}


def word_stone():
    """A graven wayside stele: one of the parish's three words sleeps in it.
    Stepped stone plinth, gabled Gothic tablet with recessed dark-stone niche,
    embossed gold sun-roundel + 3 gilt script strokes on the +Y face, and
    melted votive wax stubs at its foot."""
    objs = []
    bm = bmesh.new()
    V.add_box(bm, (-0.34, -0.25, 0.0), (0.34, 0.25, 0.11))
    V.add_box(bm, (-0.29, -0.20, 0.11), (0.29, 0.20, 0.20))
    objs.append(V.bm_to_object(bm, "plinth", ("M_stone",)))

    # Gabled Gothic stele with raised border stiles & pointed gable coping
    bm = bmesh.new()
    V.add_box(bm, (-0.26, -0.09, 0.20), (0.26, 0.07, 0.92))
    for sx in (-0.22, 0.22):
        V.add_box(bm, (sx - 0.04, -0.10, 0.20), (sx + 0.04, 0.10, 0.94))
    V.add_box(bm, (-0.26, -0.10, 0.20), (0.26, 0.10, 0.28))
    V.add_box(bm, (-0.27, -0.11, 0.90), (0.27, 0.11, 0.96))
    # Gabled coping hood
    a = [bm.verts.new(p) for p in ((-0.28, -0.11, 0.96), (0.28, -0.11, 0.96), (0.28, 0.11, 0.96), (-0.28, 0.11, 0.96))]
    r0 = bm.verts.new((0.0, -0.11, 1.12))
    r1 = bm.verts.new((0.0, 0.11, 1.12))
    bm.faces.new((a[0], a[1], r0))
    bm.faces.new((a[2], a[3], r1))
    bm.faces.new((a[0], r0, r1, a[3]))
    bm.faces.new((r0, a[1], a[2], r1))
    bm.faces.new(list(reversed(a)))
    objs.append(V.bm_to_object(bm, "tablet", ("M_stone_trim",)))

    # Recessed dark-stone inscription field on the +Y face
    bm_field = bmesh.new()
    V.add_box(bm_field, (-0.18, 0.06, 0.28), (0.18, 0.088, 0.90))
    objs.append(V.bm_to_object(bm_field, "tablet_field", ("M_stone_dark",)))

    # Gilt sun-disc & three engraved script lines on the +Y face
    bm = bmesh.new()
    V.add_box(bm, (-0.055, 0.086, 0.76), (0.055, 0.116, 0.87))
    for z0, x0, x1 in ((0.64, -0.15, 0.15), (0.50, -0.12, 0.16), (0.36, -0.15, 0.11)):
        V.add_box(bm, (x0, 0.086, z0), (x1, 0.118, z0 + 0.055))
    objs.append(V.bm_to_object(bm, "script", ("M_gold",)))

    for idx, (wx, wy, wh) in enumerate(((0.0, 0.15, 0.13), (-0.12, 0.14, 0.09), (0.11, -0.14, 0.11))):
        nm = "waxstub" if idx == 0 else ("waxstub_%d" % idx)
        stub = V.loft_rings(nm, [(0.048, 0.20, 10, 0), (0.040, 0.20 + wh, 10, 0)], "M_wax")
        stub.location = (wx, wy, 0.0)
        objs.append(stub)
    return objs, {"size": [0.68, 0.5, 1.12], "origin": "bottom-center"}


def pew_3m():
    """A 3 m parish pew: carved Gothic bench-end standards with poppyhead finials,
    4-bay recessed wainscot backrest, scrolled armrests, kneeler rail, and iron
    corner brackets. Origin bottom-center; back is on +Y."""
    objs = []
    bm = bmesh.new()
    # Floor runners & 3 support standards
    for sx in (-1.44, 0.0, 1.44):
        V.add_box(bm, (sx - 0.05, -0.14, 0.0), (sx + 0.05, 0.36, 0.08))
    V.add_box(bm, (-0.045, -0.06, 0.08), (0.045, 0.32, 0.42))
    # Contoured seat plank & under-seat apron rail
    V.add_box(bm, (-1.48, -0.06, 0.42), (1.48, 0.28, 0.49))
    V.add_box(bm, (-1.44, -0.03, 0.35), (1.44, 0.03, 0.42))
    # Recessed wainscot backrest field + horizontal rails + 5 vertical muntin stiles
    V.add_box(bm, (-1.45, 0.27, 0.49), (1.45, 0.33, 0.98))
    for z0, z1 in ((0.49, 0.55), (0.72, 0.77), (0.94, 1.01)):
        V.add_box(bm, (-1.48, 0.25, z0), (1.48, 0.35, z1))
    for sx in (-1.40, -0.70, 0.0, 0.70, 1.40):
        V.add_box(bm, (sx - 0.04, 0.25, 0.54), (sx + 0.04, 0.35, 0.95))
    # Molded top cresting rail
    V.add_box(bm, (-1.52, 0.235, 1.01), (1.52, 0.365, 1.07))
    # Outer bench-end standards with armrests & trefoil poppyhead finials
    for sx in (-1.44, 1.44):
        V.add_box(bm, (sx - 0.05, -0.10, 0.08), (sx + 0.05, 0.35, 0.64))
        V.add_box(bm, (sx - 0.05, 0.14, 0.64), (sx + 0.05, 0.36, 1.03))
        V.add_box(bm, (sx - 0.06, -0.14, 0.60), (sx + 0.06, 0.18, 0.67))
        V.add_box(bm, (sx - 0.04, 0.23, 1.06), (sx + 0.04, 0.36, 1.15))
        V.add_box(bm, (sx - 0.048, 0.20, 1.09), (sx + 0.048, 0.39, 1.13))
    # Kneeler rail with 3 support blocks
    V.add_box(bm, (-1.46, -0.42, 0.06), (1.46, -0.30, 0.13))
    for sx in (-1.40, 0.0, 1.40):
        V.add_box(bm, (sx - 0.04, -0.42, 0.0), (sx + 0.04, -0.28, 0.06))
    objs.append(V.bm_to_object(bm, "pew", ("M_wood",)))

    bm_iron = bmesh.new()
    for sx in (-1.49, 1.49):
        V.add_box(bm_iron, (sx - 0.008, -0.08, 0.41), (sx + 0.008, 0.35, 0.49))
        V.add_box(bm_iron, (sx - 0.008, 0.24, 0.94), (sx + 0.008, 0.36, 1.01))
    objs.append(V.bm_to_object(bm_iron, "pew_iron", ("M_iron",)))
    return objs, {"size": [3, 0.9, 1.15], "origin": "bottom-center"}


def altar_wick():
    """The First Wick's altar: carved stone mensa with pilaster arcading under a
    draped wax-white antependium cloth with gold galloon border, a Gothic gabled
    gold reliquary châsse housing the glowing First Wick ember, and two tall
    parish vigil candles in brass dishes. Origin bottom-center."""
    objs = []
    bm = bmesh.new()
    V.add_box(bm, (-1.24, -0.54, 0.0), (1.24, 0.54, 0.10))
    V.add_box(bm, (-1.18, -0.48, 0.10), (1.18, 0.48, 0.95))
    for sx in (-1.12, -0.42, 0.42, 1.12):
        for sy in (-0.48, 0.48):
            V.add_box(bm, (sx - 0.055, sy - 0.03, 0.10), (sx + 0.055, sy + 0.03, 0.95))
    objs.append(V.bm_to_object(bm, "mensa", ("M_stone_trim",)))

    # Draped wax-white altar cloth + hanging front/back antependium drops
    bm = bmesh.new()
    V.add_box(bm, (-1.26, -0.56, 0.95), (1.26, 0.56, 1.06))
    for sy in (-0.56, 0.56):
        y0, y1 = (sy - 0.018, sy + 0.005) if sy < 0 else (sy - 0.005, sy + 0.018)
        V.add_box(bm, (-0.42, y0, 0.24), (0.42, y1, 0.96))
    objs.append(V.bm_to_object(bm, "cloth", ("M_wax",)))

    # Sculpted Gothic architectural reliquary châsse + antependium gold border & brass candle dishes
    bm = bmesh.new()
    for sy in (-0.565, 0.565):
        y0, y1 = (sy - 0.018, sy + 0.004) if sy < 0 else (sy - 0.004, sy + 0.018)
        V.add_box(bm, (-0.43, y0, 0.21), (0.43, y1, 0.25))
        V.add_box(bm, (-0.024, y0, 0.42), (0.024, y1, 0.78))
        V.add_box(bm, (-0.15, y0, 0.58), (0.15, y1, 0.62))
    # Reliquary stepped plinth, chest, corner buttress colonnettes, and gabled roof
    V.add_box(bm, (-0.34, -0.24, 1.06), (0.34, 0.24, 1.12))
    V.add_box(bm, (-0.28, -0.19, 1.12), (0.28, 0.19, 1.42))
    for sx in (-0.28, 0.0, 0.28):
        for sy in (-0.19, 0.19):
            V.add_box(bm, (sx - 0.028, sy - 0.028, 1.12), (sx + 0.028, sy + 0.028, 1.45))
    # Gabled châsse roof prism + ridge cresting & finial cross
    a = [bm.verts.new(p) for p in ((-0.32, -0.22, 1.42), (0.32, -0.22, 1.42), (0.32, 0.22, 1.42), (-0.32, 0.22, 1.42))]
    r0 = bm.verts.new((-0.32, 0.0, 1.60))
    r1 = bm.verts.new((0.32, 0.0, 1.60))
    bm.faces.new((a[0], a[1], r1, r0))
    bm.faces.new((r0, r1, a[2], a[3]))
    bm.faces.new((a[0], r0, a[3]))
    bm.faces.new((a[1], a[2], r1))
    bm.faces.new(list(reversed(a)))
    V.add_box(bm, (-0.30, -0.015, 1.58), (0.30, 0.015, 1.64))
    V.add_box(bm, (-0.018, -0.018, 1.62), (0.018, 0.018, 1.74))
    V.add_box(bm, (-0.06, -0.015, 1.67), (0.06, 0.015, 1.70))
    # Molded candle dishes at (-0.85, 0) and (0.85, 0)
    for sx in (-0.85, 0.85):
        V.add_cyl(bm, sx, 0.0, 1.06, 0.04, 0.13, n=12)
    objs.append(V.bm_to_object(bm, "reliquary", ("M_gold",)))

    # Glowing First-Wick heart window inset on front and back of the reliquary
    bm_em = bmesh.new()
    for sy in (-0.195, 0.195):
        V.add_box(bm_em, (-0.11, sy - 0.012, 1.18), (0.11, sy + 0.012, 1.36))
    objs.append(V.bm_to_object(bm_em, "wick_heart", ("M_ember",)))

    for i, sx in enumerate((-0.85, 0.85)):
        c = V.loft_rings("candle%d" % i, [(0.095, 1.10, 12, 0), (0.082, 1.62, 12, 0)], "M_wax")
        c.location = (sx, 0.0, 0.0)
        objs.append(c)
        f = V.loft_rings("flame%d" % i, [
            (0.012, 1.62, 8, 0),
            (0.042, 1.67, 8, 0.15),
            (0.030, 1.74, 8, 0.30),
            (0.014, 1.80, 8, 0.45),
            (0.002, 1.85, 8, 0.60),
        ], "M_flame")
        f.location = (sx, 0.0, 0.0)
        objs.append(f)
    return objs, {"size": [2.52, 1.12, 1.85], "origin": "bottom-center"}


def torch_held():
    """A hand torch: tapered wooden shaft through the grip origin (engine: blade +Y),
    wrought-iron cresset collar & ribs, pitch-soaked head, and living flame."""
    objs = []
    shaft = V.loft_rings("shaft", [
        (0.020, -0.14, 10, 0),
        (0.024, 0.0, 10, 0),
        (0.028, 0.38, 10, 0),
        (0.034, 0.56, 10, 0),
    ], "M_wood")
    objs.append(shaft)
    bm = bmesh.new()
    V.add_box(bm, (-0.044, -0.044, 0.50), (0.044, 0.044, 0.57))
    V.add_box(bm, (-0.052, -0.052, 0.68), (0.052, 0.052, 0.72))
    for a in range(4):
        ang = a * math.pi * 0.5 + math.pi * 0.25
        cx, cy = math.cos(ang) * 0.044, math.sin(ang) * 0.044
        V.add_box(bm, (cx - 0.008, cy - 0.008, 0.54), (cx + 0.008, cy + 0.008, 0.74))
    objs.append(V.bm_to_object(bm, "collar", ("M_iron",)))
    head = V.loft_rings("head", [
        (0.036, 0.55, 10, 0),
        (0.054, 0.66, 10, 0),
        (0.042, 0.75, 10, 0),
    ], "M_charred")
    objs.append(head)
    flame = V.loft_rings("flame", [
        (0.018, 0.73, 8, 0),
        (0.052, 0.80, 8, 0.15),
        (0.038, 0.88, 8, 0.30),
        (0.018, 0.95, 8, 0.45),
        (0.003, 1.01, 8, 0.60),
    ], "M_flame")
    objs.append(flame)
    return objs, {"size": [0.14, 0.14, 1.02], "origin": "grip-center"}


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
    "pew_3m": pew_3m,
    "altar_wick": altar_wick,
}
