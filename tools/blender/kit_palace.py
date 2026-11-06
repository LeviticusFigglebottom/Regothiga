"""Gilded palace kit: the Sanctum's own architecture. Ivory marble bodies
with gold-encrusted trim — string courses, dentil friezes, archivolts,
tracery, finials — so the ward above the hours reads as a decadent palace,
not a parish in new clothes.

Module grid = 4 m. Z-up in Blender; origin bottom-center unless noted.
Materials: M_marble / M_marble_floor (new families), M_gild, M_glass.
"""
import math
import random
import bmesh
from mathutils import Vector

import vglib as V


def _pflame(name, r=0.03, h=0.1):
    """Stylized flame for the chandelier crowns (M_flame is emissive)."""
    n = 6
    rings = [(r * 0.4, 0.0, n, 0), (r, h * 0.28, n, 0.2), (r * 0.55, h * 0.62, n, 0.4),
             (r * 0.18, h * 0.86, n, 0.6), (0.004, h, n, 0.8)]
    return V.loft_rings(name, rings, "M_flame")


# ---------------------------------------------------------------- helpers

def _dentils(bm, x0, x1, z, y_face, out=-1, depth=0.06, w=0.16, gap=0.17, h=0.18):
    """A run of little gold teeth under a cornice/frieze on wall face `y_face`."""
    ya, yb = y_face - 0.02 * out, y_face + depth * out
    y0, y1 = min(ya, yb), max(ya, yb)
    x = x0 + gap * 0.5
    while x + w < x1 - 0.02:
        V.add_box(bm, (x, y0, z), (x + w, y1, z + h))
        x += w + gap


def _gilt_cap(r, z0, h=0.22):
    """Gold capital ring for a colonnette (loft)."""
    n = 8
    rings = [(r * 1.02, z0, n, 0), (r * 1.28, z0 + h * 0.45, n, 0),
             (r * 1.45, z0 + h * 0.8, n, 0), (r * 1.5, z0 + h, n, 0)]
    return V.loft_rings("gilt_cap", rings, "M_gild")


def _marble_colonnette(r, h):
    rings = [(r * 1.4, 0.0, 8, 0), (r * 1.05, 0.10, 8, 0), (r, 0.2, 8, 0),
             (r * 0.92, h * 0.75, 8, 0), (r * 0.9, h, 8, 0)]
    return V.loft_rings("palace_colonnette", rings, "M_marble")


def _panel_relief(bm, x0, x1, z0, z1, y_face, out, inset=0.055, frame=0.16, bm_gild=None, bm_field=None):
    """Raised rectangular frame moulding — palace paneling instead of the
    cloister's rough ashlar. y_face is the wall face plane; `out` (+1/-1)
    is the outward direction, the frame stands proud by `inset`."""
    ya, yb = y_face - 0.01 * out, y_face + inset * out
    y0, y1 = min(ya, yb), max(ya, yb)
    V.add_box(bm, (x0, y0, z0), (x1, y1, z0 + frame))
    V.add_box(bm, (x0, y0, z1 - frame), (x1, y1, z1))
    V.add_box(bm, (x0, y0, z0 + frame), (x0 + frame, y1, z1 - frame))
    V.add_box(bm, (x1 - frame, y0, z0 + frame), (x1, y1, z1 - frame))
    if bm_field is not None:
        fya, fyb = y_face - 0.005 * out, y_face + 0.014 * out
        fy0, fy1 = min(fya, fyb), max(fya, fyb)
        V.add_box(bm_field, (x0 + frame, fy0, z0 + frame), (x1 - frame, fy1, z1 - frame))
    if bm_gild is not None:
        gb = 0.022
        gya, gyb = y_face + 0.010 * out, y_face + (inset - 0.012) * out
        gy0, gy1 = min(gya, gyb), max(gya, gyb)
        ix0, ix1 = x0 + frame, x1 - frame
        iz0, iz1 = z0 + frame, z1 - frame
        V.add_box(bm_gild, (ix0, gy0, iz0), (ix1, gy1, iz0 + gb))
        V.add_box(bm_gild, (ix0, gy0, iz1 - gb), (ix1, gy1, iz1))
        V.add_box(bm_gild, (ix0, gy0, iz0 + gb), (ix0 + gb, gy1, iz1 - gb))
        V.add_box(bm_gild, (ix1 - gb, gy0, iz0 + gb), (ix1, gy1, iz1 - gb))


# ---------------------------------------------------------------- pieces

def palace_floor_4x4():
    """Polished marble paving, broad 2 m slabs with hairline joints and a
    thin gold inlay cross at the tile heart. Origin: center, top at z=0."""
    bm = bmesh.new()
    rng = random.Random(19)
    V.add_box(bm, (-2.0, -2.0, -0.25), (2.0, 2.0, -0.05))
    g = 0.008
    for i in range(2):
        for j in range(2):
            x0, y0 = -2 + i * 2.0, -2 + j * 2.0
            drop = rng.uniform(0.004, 0.014)
            xlo = x0 + (g if i > 0 else 0.0)
            xhi = x0 + 2.0 - (g if i < 1 else 0.0)
            ylo = y0 + (g if j > 0 else 0.0)
            yhi = y0 + 2.0 - (g if j < 1 else 0.0)
            V.add_box(bm, (xlo, ylo, -0.05), (xhi, yhi, -drop))
    floor = V.bm_to_object(bm, "palace_floor", ("M_marble_floor",))
    # a whisper of bronze in the slab joints — metal seams, not a gold grid
    bm2 = bmesh.new()
    V.add_box(bm2, (-2.0, -0.014, -0.010), (2.0, 0.014, -0.002))
    V.add_box(bm2, (-0.014, -2.0, -0.010), (0.014, 2.0, -0.002))
    inlay = V.bm_to_object(bm2, "palace_floor_inlay", ("M_bronze",))
    return [floor, inlay], {"size": [4, 0.25, 4], "origin": "top-center"}


def palace_wall_4x4():
    """Palace wall 4 x 4 x 0.45: smooth marble with recessed paneling both
    faces, a gold string course at the waist and a gilt dentil frieze under
    the head. Origin bottom-center."""
    objs = []
    bm = bmesh.new()
    bm_field = bmesh.new()
    bm_gild = bmesh.new()
    V.add_box(bm, (-2, -0.16, -0.006), (2, 0.16, 4.006))            # core
    V.add_box(bm, (-2, -0.21, -0.006), (2, 0.21, 0.55))             # plinth
    V.add_box(bm, (-2, -0.21, 3.62), (2, 0.21, 4.006))              # head band
    for (yf, out) in ((-0.16, -1), (0.16, 1)):
        for (px0, px1) in ((-1.86, -0.1), (0.1, 1.86)):
            _panel_relief(bm, px0, px1, 0.75, 2.0, yf, out, frame=0.13, bm_gild=bm_gild, bm_field=bm_field)
            _panel_relief(bm, px0, px1, 2.5, 3.4, yf, out, frame=0.13, bm_gild=bm_gild, bm_field=bm_field)
    objs.append(V.bm_to_object(bm, "palace_wall", ("M_marble",)))
    objs.append(V.bm_to_object(bm_field, "palace_wall_panels", ("M_marble_floor",)))
    V.add_box(bm_gild, (-2, -0.20, 2.14), (2, 0.20, 2.30))         # string course
    _dentils(bm_gild, -2.0, 2.0, 3.42, -0.16, out=-1)              # front dentils
    _dentils(bm_gild, -2.0, 2.0, 3.42, 0.16, out=1)                # back dentils
    objs.append(V.bm_to_object(bm_gild, "palace_wall_gild", ("M_gild",)))
    return objs, {"size": [4, 0.5, 4], "origin": "bottom-center"}


def palace_wall_low_4m():
    """Marble parapet, 1.05 m, recessed panels, gold base and coping. Origin bottom-center."""
    objs = []
    bm = bmesh.new()
    bm_field = bmesh.new()
    bm_gild = bmesh.new()
    V.add_box(bm, (-2, -0.17, 0.14), (2, 0.17, 0.86))
    V.add_box(bm, (-2, -0.21, 0.0), (2, 0.21, 0.18))                # stepped plinth
    for (yf, out) in ((-0.17, -1), (0.17, 1)):
        for (px0, px1) in ((-1.84, -0.12), (0.12, 1.84)):
            _panel_relief(bm, px0, px1, 0.24, 0.78, yf, out, inset=0.04, frame=0.09,
                          bm_gild=bm_gild, bm_field=bm_field)
    objs.append(V.bm_to_object(bm, "palace_parapet", ("M_marble",)))
    objs.append(V.bm_to_object(bm_field, "palace_parapet_panels", ("M_marble_floor",)))
    V.add_box(bm_gild, (-2, -0.22, 0.84), (2, 0.22, 0.90))
    V.add_box(bm_gild, (-2, -0.25, 0.90), (2, 0.25, 1.02))
    objs.append(V.bm_to_object(bm_gild, "palace_parapet_gild", ("M_gild",)))
    return objs, {"size": [4, 0.5, 1.05], "origin": "bottom-center"}


def palace_cornice_4m():
    """Projecting marble cornice with carved marble modillion brackets, gilt
    dentil teeth, and continuous gold beads on both faces. Bottom-center."""
    bm = bmesh.new()
    V.add_box(bm, (-2, -0.26, 0.0), (2, 0.26, 0.08))
    V.add_box(bm, (-2, -0.32, 0.08), (2, 0.32, 0.18))
    V.add_box(bm, (-2, -0.38, 0.18), (2, 0.38, 0.30))
    for i in range(8):
        cx = -1.75 + i * 0.50
        V.add_box(bm, (cx - 0.075, -0.36, 0.04), (cx + 0.075, 0.36, 0.19))
    body = V.bm_to_object(bm, "palace_cornice", ("M_marble",))
    bm_g = bmesh.new()
    V.add_box(bm_g, (-2, -0.30, 0.03), (2, 0.30, 0.09))
    V.add_box(bm_g, (-2, -0.40, 0.22), (2, 0.40, 0.29))
    for i in range(8):
        cx = -1.75 + i * 0.50
        V.add_box(bm_g, (cx - 0.045, -0.375, 0.06), (cx + 0.045, 0.375, 0.17))
    _dentils(bm_g, -2.0, 2.0, 0.09, -0.30, out=-1, depth=0.05, w=0.12, gap=0.13, h=0.09)
    _dentils(bm_g, -2.0, 2.0, 0.09, 0.30, out=1, depth=0.05, w=0.12, gap=0.13, h=0.09)
    bead = V.bm_to_object(bm_g, "palace_cornice_gild", ("M_gild",))
    return [body, bead], {"size": [4, 0.8, 0.3], "origin": "bottom-center"}


def palace_portal_4m():
    """Palace doorway: marble panel, 1.9-wide arch, two GOLD archivolts,
    matching wainscoting side panels & dentil frieze, and a gilt sun-wheel
    medallion in the tympanum zone. Passage along Y, bottom-center."""
    objs = []
    panel = V.wall_panel_with_arch("palace_portal_wall", 4.0, 4.0, 0.36, 1.9, 1.60,
                                   sharpness=0.75, mat="M_marble", segments=12)
    objs.append(panel)
    bm_trim = bmesh.new()
    bm_field = bmesh.new()
    bm_gild = bmesh.new()
    for sx in (-1, 1):
        x0, x1 = (-2.0, -0.95) if sx < 0 else (0.95, 2.0)
        V.add_box(bm_trim, (x0, -0.21, -0.006), (x1, 0.21, 0.55))
        V.add_box(bm_gild, (sx * 1.18, -0.20, 2.14), (sx * 2.0, 0.20, 2.30))
        px0, px1 = (-1.88, -1.24) if sx < 0 else (1.24, 1.88)
        for (yf, out) in ((-0.18, -1), (0.18, 1)):
            _panel_relief(bm_trim, px0, px1, 0.75, 2.0, yf, out, frame=0.10, bm_gild=bm_gild, bm_field=bm_field)
            _panel_relief(bm_trim, px0, px1, 2.5, 3.4, yf, out, frame=0.10, bm_gild=bm_gild, bm_field=bm_field)
    V.add_box(bm_trim, (-2.0, -0.21, 3.62), (2.0, 0.21, 4.006))
    _dentils(bm_gild, -2.0, 2.0, 3.42, -0.18, out=-1)
    _dentils(bm_gild, -2.0, 2.0, 3.42, 0.18, out=1)
    objs.append(V.bm_to_object(bm_trim, "palace_portal_mould", ("M_marble",)))
    objs.append(V.bm_to_object(bm_field, "palace_portal_panels", ("M_marble_floor",)))
    arch = V.pointed_arch(1.9, 0.75, 12, 1.60)
    for k, (scale, depth) in enumerate(((1.07, 0.48), (1.16, 0.44))):
        path = [(x * scale, 0.0, 1.60 + (y - 1.60) * scale) for (x, y) in arch]
        prof = V.chamfer_rect_profile(0.11 - k * 0.015, depth, 0.03)
        objs.append(V.sweep_profile(f"palace_archivolt{k}", path, prof, "M_gild",
                                    up_hint=Vector((0, 1, 0))))
    # Gilded 12-point radiant sun-wheel medallion above the arch apex
    cx, cz = 0.0, 3.24
    for s_face in (-1, 1):
        y0, y1 = (-0.23, -0.17) if s_face < 0 else (0.17, 0.23)
        n_rays = 12
        for a in range(n_rays):
            ang = math.tau * a / n_rays
            dx, dz = math.cos(ang), math.sin(ang)
            nx, nz = -dz, dx
            r_in = 0.07
            r_out = 0.24 if (a % 2 == 0) else 0.17
            w_in, w_out = 0.016, 0.004
            p00 = (cx + dx * r_in - nx * w_in, cz + dz * r_in - nz * w_in)
            p01 = (cx + dx * r_in + nx * w_in, cz + dz * r_in + nz * w_in)
            p11 = (cx + dx * r_out + nx * w_out, cz + dz * r_out + nz * w_out)
            p10 = (cx + dx * r_out - nx * w_out, cz + dz * r_out - nz * w_out)
            vf = [bm_gild.verts.new((p[0], y0, p[1])) for p in (p00, p01, p11, p10)]
            vb = [bm_gild.verts.new((p[0], y1, p[1])) for p in (p00, p01, p11, p10)]
            bm_gild.faces.new(vf)
            bm_gild.faces.new(tuple(reversed(vb)))
            for i in range(4):
                j = (i + 1) % 4
                bm_gild.faces.new((vf[i], vf[j], vb[j], vb[i]))
        n_disc = 16
        r_disc = 0.095
        df = [bm_gild.verts.new((cx + r_disc * math.cos(math.tau * i / n_disc), y0 - 0.01,
                                 cz + r_disc * math.sin(math.tau * i / n_disc))) for i in range(n_disc)]
        db = [bm_gild.verts.new((cx + r_disc * math.cos(math.tau * i / n_disc), y1 + 0.01,
                                 cz + r_disc * math.sin(math.tau * i / n_disc))) for i in range(n_disc)]
        bm_gild.faces.new(df)
        bm_gild.faces.new(tuple(reversed(db)))
        for i in range(n_disc):
            j = (i + 1) % n_disc
            bm_gild.faces.new((df[i], df[j], db[j], db[i]))
    bmesh.ops.recalc_face_normals(bm_gild, faces=bm_gild.faces)
    objs.append(V.bm_to_object(bm_gild, "palace_sunburst", ("M_gild",)))
    bm_jamb = bmesh.new()
    for sx in (-1, 1):                                             # jamb colonnettes + continuous impost capitals
        x_jamb, x_wall = sx * 0.92, sx * 1.18
        V.add_box(bm_jamb, (x_jamb, -0.25, 0.0), (x_wall, 0.25, 0.14))
        V.add_box(bm_jamb, (x_jamb - 0.02 * sx, -0.24, 1.42), (x_wall + 0.01 * sx, 0.24, 1.50))
        V.add_box(bm_jamb, (x_jamb - 0.03 * sx, -0.26, 1.50), (x_wall + 0.02 * sx, 0.26, 1.60))
        for sy in (-0.19, 0.19):
            c = _marble_colonnette(0.085, 1.42)
            c.location = (sx * 1.03, sy, 0)
            objs.append(c)
    objs.append(V.bm_to_object(bm_jamb, "palace_portal_imposts", ("M_gild",)))
    return objs, {"size": [4, 0.6, 4], "origin": "bottom-center", "opening": [1.9, 2.9]}


def palace_window_4m():
    """Palace bay with twin pointed-arch glazed lancets in GOLD tracery,
    engaged marble colonnettes, swept gold archivolts, and gilt dentil frieze,
    matching the wall module (4 x 4, bottom-center)."""
    objs = []
    # Two pointed-arch lancet sub-panels centered at x = -0.80 and +0.80
    arch = V.pointed_arch(0.90, 0.88, 12, 2.62)
    for s, tag in ((-1, "l"), (1, "r")):
        cx = s * 0.80
        sub = V.wall_panel_with_arch(f"palace_win_{tag}", 1.60, 4.0, 0.36, 0.90, 2.62,
                                     sharpness=0.88, mat="M_marble", segments=12, sill_h=0.90)
        sub.location = (cx, 0.0, 0.0)
        objs.append(sub)
        # Swept gold archivolt hood-mold around each pointed lancet head
        apath = [(cx + x * 1.06, 0.0, 2.62 + (y - 2.62) * 1.04) for (x, y) in arch]
        objs.append(V.sweep_profile(f"palace_win_arch_{tag}", apath,
                                    V.chamfer_rect_profile(0.085, 0.44, 0.024),
                                    "M_gild", up_hint=Vector((0, 1, 0))))
        # Engaged jamb colonnettes flanking each lancet
        for jx in (-0.47, 0.47):
            col = _marble_colonnette(0.055, 1.66)
            col.location = (cx + jx, 0.0, 0.92)
            objs.append(col)
    bm = bmesh.new()
    # Outer side piers (-2.0..-1.60 and 1.60..2.0), base plinth, and top head band
    V.add_box(bm, (-2.0, -0.18, -0.008), (-1.60, 0.18, 4.006))
    V.add_box(bm, (1.60, -0.18, -0.008), (2.0, 0.18, 4.006))
    V.add_box(bm, (-2.0, -0.21, -0.008), (2.0, 0.21, 0.55))
    V.add_box(bm, (-2.0, -0.21, 3.62), (2.0, 0.21, 4.006))
    objs.append(V.bm_to_object(bm, "palace_win_wall", ("M_marble",)))

    bm_gild = bmesh.new()
    V.add_box(bm_gild, (-1.42, -0.25, 0.78), (1.42, 0.25, 0.92))    # continuous gold sill
    _dentils(bm_gild, -2.0, 2.0, 3.42, -0.18, out=-1)               # front dentil frieze
    _dentils(bm_gild, -2.0, 2.0, 3.42, 0.18, out=1)                 # back dentil frieze
    for s in (-1, 1):
        cx = s * 0.80
        # Gold central mullion & transom cross-bars + impost blocks
        V.add_box(bm_gild, (cx - 0.035, -0.10, 0.92), (cx + 0.035, 0.10, 3.30))
        V.add_box(bm_gild, (cx - 0.45, -0.10, 1.88), (cx + 0.45, 0.10, 1.95))
        for jx in (-0.47, 0.47):
            V.add_box(bm_gild, (cx + jx - 0.08, -0.23, 2.56), (cx + jx + 0.08, 0.23, 2.63))
    objs.append(V.bm_to_object(bm_gild, "palace_win_gild", ("M_gild",)))

    # Pointed-arch window panes (M_citywindow: warm lamplit in glory, dark in ruin)
    bm_pane = bmesh.new()
    for s in (-1, 1):
        cx = s * 0.80
        pts2d = [(cx + 0.45, 0.90)] + [(cx + x, y) for (x, y) in reversed(arch)] + [(cx - 0.45, 0.90)]
        vf = [bm_pane.verts.new((px, -0.04, pz)) for (px, pz) in pts2d]
        vb = [bm_pane.verts.new((px, 0.04, pz)) for (px, pz) in pts2d]
        bm_pane.faces.new(vf)
        bm_pane.faces.new(list(reversed(vb)))
        n_p = len(pts2d)
        for i in range(n_p):
            j = (i + 1) % n_p
            bm_pane.faces.new((vf[i], vf[j], vb[j], vb[i]))
    bmesh.ops.recalc_face_normals(bm_pane, faces=bm_pane.faces)
    objs.append(V.bm_to_object(bm_pane, "palace_win_panes", ("M_citywindow",)))
    return objs, {"size": [4, 0.5, 4], "origin": "bottom-center"}


def palace_arcade_4m():
    """Open palace colonnade bay: a true passage (no parapet) with a wide
    arch, side-pier base plinths, waist gold stringcourses, top head band,
    front/back gilt dentil friezes, gold archivolt edge and gilt-capped
    colonnettes. Bottom-center."""
    objs = []
    panel = V.wall_panel_with_arch("palace_arcade_panel", 4.0, 4.0, 0.4, 2.4, 2.0,
                                   sharpness=0.9, mat="M_marble", segments=12)
    objs.append(panel)
    bm_trim = bmesh.new()
    bm_gild = bmesh.new()
    for sx in (-1, 1):
        x0, x1 = (-2.0, -1.20) if sx < 0 else (1.20, 2.0)
        V.add_box(bm_trim, (x0, -0.21, -0.006), (x1, 0.21, 0.55))
        V.add_box(bm_gild, (sx * 1.40, -0.21, 2.14), (sx * 2.0, 0.21, 2.30))
    V.add_box(bm_trim, (-2.0, -0.21, 3.62), (2.0, 0.21, 4.006))
    _dentils(bm_gild, -2.0, 2.0, 3.42, -0.20, out=-1)
    _dentils(bm_gild, -2.0, 2.0, 3.42, 0.20, out=1)
    objs.append(V.bm_to_object(bm_trim, "palace_arcade_mould", ("M_marble",)))
    objs.append(V.bm_to_object(bm_gild, "palace_arcade_frieze", ("M_gild",)))
    arch = V.pointed_arch(2.4, 0.9, 12, 2.0)
    path = [(x * 1.08, 0.0, y + 0.08) for (x, y) in arch]
    prof = V.chamfer_rect_profile(0.14, 0.46, 0.035)
    objs.append(V.sweep_profile("palace_arcade_gild", path, prof, "M_gild",
                                up_hint=Vector((0, 1, 0))))
    bm_jamb = bmesh.new()
    for sx in (-1, 1):
        x_jamb, x_wall = sx * 1.17, sx * 1.42
        V.add_box(bm_jamb, (x_jamb, -0.25, 0.0), (x_wall, 0.25, 0.14))
        V.add_box(bm_jamb, (x_jamb - 0.02 * sx, -0.24, 1.82), (x_wall + 0.01 * sx, 0.24, 1.90))
        V.add_box(bm_jamb, (x_jamb - 0.03 * sx, -0.26, 1.90), (x_wall + 0.02 * sx, 0.26, 2.00))
        for sy in (-0.19, 0.19):
            c = _marble_colonnette(0.085, 1.82)
            c.location = (sx * 1.28, sy, 0)
            objs.append(c)
    objs.append(V.bm_to_object(bm_jamb, "palace_arcade_imposts", ("M_gild",)))
    return objs, {"size": [4, 0.5, 4], "origin": "bottom-center", "opening": [2.4, 3.1]}


def palace_balustrade_4m():
    """Marble balustrade with corner newel posts and a gold handrail. Origin bottom-center."""
    objs = []
    bm = bmesh.new()
    V.add_box(bm, (-2, -0.14, 0), (2, 0.14, 0.12))                 # base rail
    for px in (-1.92, 1.92):
        V.add_box(bm, (px - 0.10, -0.15, 0.12), (px + 0.10, 0.15, 0.90))
    objs.append(V.bm_to_object(bm, "palace_bal_base", ("M_marble",)))
    for i in range(9):
        x = -1.56 + i * 0.39
        rings = [(0.085, 0.12, 10, 0), (0.11, 0.3, 10, 0), (0.065, 0.55, 10, 0),
                 (0.10, 0.78, 10, 0), (0.085, 0.9, 10, 0)]
        b = V.loft_rings("palace_baluster", rings, "M_marble")
        b.location = (x, 0, 0)
        objs.append(b)
    bm = bmesh.new()
    V.add_box(bm, (-2, -0.15, 0.90), (2, 0.15, 0.95))
    V.add_box(bm, (-2.02, -0.13, 0.95), (2.02, 0.13, 1.06))
    for px in (-1.92, 1.92):
        V.add_box(bm, (px - 0.12, -0.16, 0.10), (px + 0.12, 0.16, 0.15))
        V.add_box(bm, (px - 0.12, -0.16, 0.87), (px + 0.12, 0.16, 0.91))
    objs.append(V.bm_to_object(bm, "palace_bal_rail", ("M_gild",)))
    return objs, {"size": [4, 0.3, 1.06], "origin": "bottom-center"}


def palace_pier():
    """Square marble corner pier, 4.1 m, recessed vertical face panels, gold
    base and capital bands, mid waist ring, and gilt finial cap — makes wall
    junctions read deliberate. Origin bottom-center."""
    objs = []
    bm = bmesh.new()
    V.add_box(bm, (-0.34, -0.34, 0.0), (0.34, 0.34, 4.1))
    # Corner pilaster stiles framing all 4 faces
    for sx in (-0.30, 0.30):
        for sy in (-0.30, 0.30):
            V.add_box(bm, (sx - 0.06, sy - 0.06, 0.50), (sx + 0.06, sy + 0.06, 3.70))
    objs.append(V.bm_to_object(bm, "palace_pier", ("M_marble",)))
    bm_panels = bmesh.new()
    for z0, z1 in ((0.64, 2.04), (2.36, 3.56)):
        for sf in (-1, 1):
            V.add_box(bm_panels, (-0.20, sf * 0.34 - 0.015, z0), (0.20, sf * 0.34 + 0.015, z1))
            V.add_box(bm_panels, (sf * 0.34 - 0.015, -0.20, z0), (sf * 0.34 + 0.015, 0.20, z1))
    objs.append(V.bm_to_object(bm_panels, "palace_pier_panels", ("M_marble_floor",)))
    bm = bmesh.new()
    V.add_box(bm, (-0.42, -0.42, 0.0), (0.42, 0.42, 0.22))
    V.add_box(bm, (-0.39, -0.39, 0.22), (0.39, 0.39, 0.50))
    V.add_box(bm, (-0.38, -0.38, 2.14), (0.38, 0.38, 2.30))        # waist band matching palace_wall_4x4
    V.add_box(bm, (-0.39, -0.39, 3.70), (0.39, 0.39, 3.86))
    V.add_box(bm, (-0.43, -0.43, 3.86), (0.43, 0.43, 4.02))
    objs.append(V.bm_to_object(bm, "palace_pier_gild", ("M_gild",)))
    fin = _gilt_finial_obj(0.55)
    fin.location = (0, 0, 4.1)
    objs.append(fin)
    return objs, {"size": [0.8, 0.8, 4.7], "origin": "bottom-center"}


def _gilt_finial_obj(h):
    n = 12
    rings = [
        (0.18, 0.0, n, 0),
        (0.16, h * 0.10, n, 0),
        (0.21, h * 0.22, n, 0),
        (0.10, h * 0.40, n, 0),
        (0.15, h * 0.56, n, 0),
        (0.06, h * 0.76, n, 0),
        (0.015, h, n, 0),
    ]
    return V.loft_rings("gilt_finial", rings, "M_gild")


def gilt_finial():
    """Standalone gold pinnacle for parapets and gate piers. Bottom-center."""
    return [_gilt_finial_obj(1.3)], {"size": [0.45, 0.45, 1.3], "origin": "bottom-center"}


def palace_pediment_8m():
    """Triangular marble pediment, 8 m wide, gold raking edge and central
    gold sun disc — the crown over the Door of the Hour. Bottom-center."""
    objs = []
    w, h, d = 4.0, 2.1, 0.42
    bm = bmesh.new()
    vs_f = [bm.verts.new(p) for p in ((-w, -d, 0), (w, -d, 0), (0, -d, h))]
    vs_b = [bm.verts.new(p) for p in ((-w, d, 0), (w, d, 0), (0, d, h))]
    bm.faces.new(vs_f)
    bm.faces.new(tuple(reversed(vs_b)))
    for i in range(3):
        a, b = vs_f[i], vs_f[(i + 1) % 3]
        c, dd = vs_b[(i + 1) % 3], vs_b[i]
        bm.faces.new((a, b, c, dd))
    objs.append(V.bm_to_object(bm, "palace_pediment", ("M_marble",)))
    bm = bmesh.new()
    # Continuous raking gold cornice along (-w, 0) -> (0, h) -> (w, 0) + base geison
    V.add_box(bm, (-w - 0.08, -d - 0.06, -0.04), (w + 0.08, d + 0.06, 0.10))
    for s in (-1, 1):
        p_foot_in = (s * w, 0.0)
        p_foot_out = (s * (w + 0.08), 0.14)
        p_peak_in = (0.0, h)
        p_peak_out = (0.0, h + 0.15)
        pts = (p_foot_in, p_foot_out, p_peak_out, p_peak_in) if s < 0 else (p_peak_in, p_peak_out, p_foot_out, p_foot_in)
        vf = [bm.verts.new((px, -d - 0.06, pz)) for (px, pz) in pts]
        vb = [bm.verts.new((px, d + 0.06, pz)) for (px, pz) in pts]
        bm.faces.new(vf)
        bm.faces.new(tuple(reversed(vb)))
        for i in range(4):
            j = (i + 1) % 4
            bm.faces.new((vf[i], vf[j], vb[j], vb[i]))
    # 3D embossed sun disc + radial rays on the tympanum
    bm3 = bmesh.new()
    n_disc = 16
    cz_sun = 0.76
    for s_face in (-1, 1):
        yf = -d - 0.07 if s_face < 0 else d + 0.07
        yb = -d + 0.01 if s_face < 0 else d - 0.01
        y0, y1 = min(yf, yb), max(yf, yb)
        rf = [bm3.verts.new((0.46 * math.cos(math.tau * i / n_disc), y0,
                             cz_sun + 0.46 * math.sin(math.tau * i / n_disc))) for i in range(n_disc)]
        rb = [bm3.verts.new((0.46 * math.cos(math.tau * i / n_disc), y1,
                             cz_sun + 0.46 * math.sin(math.tau * i / n_disc))) for i in range(n_disc)]
        bm3.faces.new(rf)
        bm3.faces.new(tuple(reversed(rb)))
        for i in range(n_disc):
            j = (i + 1) % n_disc
            bm3.faces.new((rf[i], rf[j], rb[j], rb[i]))
        for r_i in range(12):
            ang = math.tau * r_i / 12
            dx, dz = math.cos(ang), math.sin(ang)
            nx, nz = -dz, dx
            r_out = 0.72 if (r_i % 2 == 0) else 0.58
            p00 = (dx * 0.44 - nx * 0.035, cz_sun + dz * 0.44 - nz * 0.035)
            p01 = (dx * 0.44 + nx * 0.035, cz_sun + dz * 0.44 + nz * 0.035)
            p11 = (dx * r_out + nx * 0.010, cz_sun + dz * r_out + nz * 0.010)
            p10 = (dx * r_out - nx * 0.010, cz_sun + dz * r_out - nz * 0.010)
            rvf = [bm3.verts.new((p[0], y0 + 0.01, p[1])) for p in (p00, p01, p11, p10)]
            rvb = [bm3.verts.new((p[0], y1 - 0.01, p[1])) for p in (p00, p01, p11, p10)]
            bm3.faces.new(rvf)
            bm3.faces.new(tuple(reversed(rvb)))
            for i in range(4):
                j = (i + 1) % 4
                bm3.faces.new((rvf[i], rvf[j], rvb[j], rvb[i]))
    objs.append(V.bm_to_object(bm, "palace_pediment_rake", ("M_gild",)))
    objs.append(V.bm_to_object(bm3, "palace_pediment_sun", ("M_gild",)))
    return objs, {"size": [8, 0.9, 2.1], "origin": "bottom-center"}


# ------------------------------------------------------- radiant skyline
# Backdrop-scale marble-and-gold silhouettes for the Sanctum's horizon:
# no mortal masonry above the hours. Warm-lit windows ride M_citywindow
# (lamplit in glory, dead-dark in ruin). No collision — skyline pieces.

def _radiant_tower(L, G, W, rng, cx, cy, base, w, h, cap=1.0):
    """One marble tower: shaft, gold string courses + eaves cornice, two-tier
    window strips, and a full-width gold pyramidal cap (returned as its own loft object)."""
    hw = w * 0.5
    V.add_box(L, (cx - hw, cy - hw, base), (cx + hw, cy + hw, base + h))
    for k in (0.35, 0.68):
        V.add_box(G, (cx - hw - 0.12, cy - hw - 0.12, base + h * k),
                  (cx + hw + 0.12, cy + hw + 0.12, base + h * k + 0.45))
    # Top gold eaves cornice crowning the marble shaft right under the pyramidal spire
    V.add_box(G, (cx - hw - 0.16, cy - hw - 0.16, base + h - 0.48),
              (cx + hw + 0.16, cy + hw + 0.16, base + h + 0.04))
    for (dx, dy) in ((0, -hw), (0, hw), (-hw, 0), (hw, 0)):
        ww = w * 0.16
        for (z_lo, z_hi) in ((0.40, 0.64), (0.73, 0.93)):
            if dx == 0:
                V.add_box(W, (cx - ww, cy + dy - 0.06, base + h * z_lo),
                          (cx + ww, cy + dy + 0.06, base + h * z_hi))
            else:
                V.add_box(W, (cx + dx - 0.06, cy - ww, base + h * z_lo),
                          (cx + dx + 0.06, cy + ww, base + h * z_hi))
    # For a 4-gon rotated by pi/4, circumradius r = hw * sqrt(2) * 1.05 covers +-hw with slight eaves overhang
    rings = [(hw * 1.485, base + h, 4, math.pi / 4), (0.06, base + h + w * 1.15 * cap, 4, math.pi / 4)]
    caps = V.loft_rings("radiant_cap", rings, "M_gild")
    caps.location = (cx, cy, 0)
    return caps


def radiant_spire(seed=3):
    """A lone marble needle for the far sky, ~40 m. Origin bottom-center."""
    rng = random.Random(seed)
    L = bmesh.new()
    G = bmesh.new()
    W = bmesh.new()
    objs = []
    h = rng.uniform(30, 38)
    w_main = rng.uniform(5.5, 7.0)
    objs.append(_radiant_tower(L, G, W, rng, 0, 0, 0.0, w_main, h, cap=1.3))
    for sx in (-1, 1):
        w_sub = rng.uniform(2.5, 3.1)
        h_sub = h * rng.uniform(0.54, 0.64)
        tx = sx * (w_main * 0.5 + w_sub * 0.42)
        ty = -w_main * 0.10
        objs.append(_radiant_tower(L, G, W, rng, tx, ty, 0.0, w_sub, h_sub, cap=1.15))
    objs.insert(0, V.bm_to_object(L, "radiant_spire", ("M_marble",)))
    objs.insert(1, V.bm_to_object(G, "radiant_spire_gild", ("M_gild",)))
    objs.insert(2, V.bm_to_object(W, "radiant_spire_win", ("M_citywindow",)))
    return objs, {"size": [16, 16, 46], "origin": "bottom-center"}


def radiant_castle(seed=4):
    """A gleaming keep for the horizon: central tower over a corniced keep,
    four corner towers, all marble with gold caps and courses.
    ~30 x 30 x 44. Origin bottom-center."""
    rng = random.Random(seed)
    L = bmesh.new()
    G = bmesh.new()
    W = bmesh.new()
    objs = []
    kw, kh = rng.uniform(12, 15), rng.uniform(13, 17)
    V.add_box(L, (-kw * 0.5, -kw * 0.5, 0), (kw * 0.5, kw * 0.5, kh))
    V.add_box(G, (-kw * 0.5 - 0.2, -kw * 0.5 - 0.2, kh - 0.7), (kw * 0.5 + 0.2, kw * 0.5 + 0.2, kh))
    for s in (-1, 1):
        V.add_box(W, (s * (kw * 0.5 + 0.06) - 0.06, -kw * 0.2, kh * 0.35),
                  (s * (kw * 0.5 + 0.06) + 0.06, kw * 0.2, kh * 0.8))
    objs.append(_radiant_tower(L, G, W, rng, 0, 0, kh, rng.uniform(6, 7.5),
                               rng.uniform(16, 22), cap=1.2))
    for sx in (-1, 1):
        for sy in (-1, 1):
            objs.append(_radiant_tower(L, G, W, rng, sx * kw * 0.5, sy * kw * 0.5, 0.0,
                                       rng.uniform(3.4, 4.4), kh + rng.uniform(4, 8)))
    objs.insert(0, V.bm_to_object(L, "radiant_castle", ("M_marble",)))
    objs.insert(1, V.bm_to_object(G, "radiant_castle_gild", ("M_gild",)))
    objs.insert(2, V.bm_to_object(W, "radiant_castle_win", ("M_citywindow",)))
    return objs, {"size": [30, 30, 44], "origin": "bottom-center"}




# ------------------------------------------------------- palace furnishing

def banquet_table_6m():
    """Feast table: marble slab with under-apron rails on 6 carved trestle
    legs with stepped plinth feet, a gold runner with overhanging end drops,
    gilt edge molding, and candle pairs riding it. Origin bottom-center. Solid."""
    objs = []
    bm = bmesh.new()
    V.add_box(bm, (-3.0, -0.62, 0.72), (3.0, 0.62, 0.86))               # marble mensa slab
    V.add_box(bm, (-2.88, -0.52, 0.63), (2.88, 0.52, 0.72))             # recessed under-table apron
    for sx in (-2.6, 0.0, 2.6):
        V.add_box(bm, (sx - 0.12, -0.52, 0.0), (sx + 0.12, 0.52, 0.08)) # trestle floor runner
        V.add_box(bm, (sx - 0.09, -0.44, 0.26), (sx + 0.09, 0.44, 0.36))# cross-bar
        for sy in (-0.44, 0.44):
            V.add_box(bm, (sx - 0.09, sy - 0.09, 0.08), (sx + 0.09, sy + 0.09, 0.72))
            V.add_box(bm, (sx - 0.11, sy - 0.11, 0.56), (sx + 0.11, sy + 0.11, 0.64))
    V.add_box(bm, (-2.6, -0.06, 0.28), (2.6, 0.06, 0.38))               # longitudinal stretcher
    objs.append(V.bm_to_object(bm, "table_body", ("M_marble",)))
    bm = bmesh.new()
    V.add_box(bm, (-3.02, -0.635, 0.77), (3.02, 0.635, 0.81))           # gilt slab edge fillet
    V.add_box(bm, (-3.02, -0.22, 0.861), (3.02, 0.22, 0.875))           # gold runner
    for sx in (-3.02, 3.00):
        V.add_box(bm, (sx, -0.22, 0.52), (sx + 0.02, 0.22, 0.875))      # overhanging runner drops
    for sx in (-2.6, 0.0, 2.6):
        V.add_box(bm, (sx - 0.13, -0.53, 0.0), (sx + 0.13, 0.53, 0.035))
    for cx in (-2.0, 0.0, 2.0):
        V.add_cyl(bm, cx, 0.0, 0.875, 0.022, 0.072, n=12)
        V.add_cyl(bm, cx, 0.0, 0.895, 0.012, 0.052, n=10)
    objs.append(V.bm_to_object(bm, "table_runner", ("M_gild",)))
    bm = bmesh.new()
    for cx in (-2.0, 0.0, 2.0):
        V.add_cyl(bm, cx, 0.0, 0.905, 0.155, 0.038, n=12)
    objs.append(V.bm_to_object(bm, "table_candles", ("M_wax",)))
    for i, cx in enumerate((-2.0, 0.0, 2.0)):
        f = _pflame("table_flame%d" % i, r=0.024, h=0.09)
        f.location = (cx, 0.0, 1.06)
        objs.append(f)
    return objs, {"size": [6, 1.25, 1.15], "origin": "bottom-center"}


def banquet_bench_6m():
    """Long marble-and-gold bench for the feast table with under-seat apron,
    carved trestle standards, and a crimson velvet cushion pad. Origin bottom-center. Solid."""
    objs = []
    bm = bmesh.new()
    V.add_box(bm, (-3.0, -0.20, 0.40), (3.0, 0.20, 0.48))               # marble seat slab
    V.add_box(bm, (-2.88, -0.15, 0.33), (2.88, 0.15, 0.40))             # under-seat apron rail
    V.add_box(bm, (-2.6, -0.05, 0.16), (2.6, 0.05, 0.24))               # stretcher rail
    for sx in (-2.6, -1.3, 0.0, 1.3, 2.6):
        V.add_box(bm, (sx - 0.11, -0.19, 0.0), (sx + 0.11, 0.19, 0.07)) # plinth foot
        V.add_box(bm, (sx - 0.08, -0.14, 0.07), (sx + 0.08, 0.14, 0.40))# carved standard
    objs.append(V.bm_to_object(bm, "bench", ("M_marble",)))
    bm_c = bmesh.new()
    V.add_box(bm_c, (-2.92, -0.16, 0.48), (2.92, 0.16, 0.51))           # crimson velvet seat cushion
    objs.append(V.bm_to_object(bm_c, "bench_cushion", ("M_cloth",)))
    bm_g = bmesh.new()
    V.add_box(bm_g, (-3.02, -0.21, 0.43), (3.02, 0.21, 0.46))           # gilt molding band
    for sx in (-2.6, -1.3, 0.0, 1.3, 2.6):
        V.add_box(bm_g, (sx - 0.12, -0.20, 0.0), (sx + 0.12, 0.20, 0.03))
    objs.append(V.bm_to_object(bm_g, "bench_gild", ("M_gild",)))
    return objs, {"size": [6, 0.42, 0.51], "origin": "bottom-center"}


def palace_dome_12m():
    """Coffered crossing dome seated flush in the y=8.85 coffer ceiling plane
    (placed at y=8.0, so local z=+0.85 is the ceiling soffit). A 12x16 m
    pendentive collar plate (with matching gold coffer beams outside r=6.0)
    bridges the rectangular crossing bay (x=-6..6, z=20..36) to the circular
    r=6.0 gold cornice drum, and the pale marble bowl rises cleanly above the
    ceiling plane from z=+0.85 to z=+4.27 with zero beams crossing the bowl."""
    import bmesh as _bmesh
    from mathutils import Matrix as _M
    objs = []
    n = 32
    dz = 0.85

    def _loft2(name, prof, mat, dr=0.0, dz_off=0.012):
        rings_a = [(r + dr, z + dz_off, n, 0) for (r, z) in prof]
        rings_b = [(r, z, n, 0) for (r, z) in reversed(prof)]
        a = V.loft_rings(name, rings_a, mat, cap_bottom=False, cap_top=False)
        b = V.loft_rings(name + "_in", rings_b, mat,
                         cap_bottom=False, cap_top=False)
        return [a, b]

    prof_in = [(6.0, 0.0 + dz), (5.85, 0.62 + dz), (5.4, 1.3 + dz), (4.6, 2.05 + dz),
               (3.5, 2.7 + dz), (2.2, 3.2 + dz), (1.1, 3.42 + dz)]
    prof_out = [(r + 0.12, z + 0.10) for (r, z) in prof_in]
    objs.append(V.loft_rings("dome_shell_out", [(r, z, n, 0) for (r, z) in prof_out],
                             "M_marble", cap_bottom=False, cap_top=False))
    objs.append(V.loft_rings("dome_shell", list(reversed([(r, z, n, 0) for (r, z) in prof_in])),
                             "M_marble", cap_bottom=False, cap_top=False))
    # Pendentive collar bridging r=5.95 circle to the 12x16 crossing rectangle (r=10.4 covers corners)
    objs.append(V.loft_rings("dome_pendentive", [(10.4, dz + 0.02, n, 0), (5.95, dz + 0.02, n, 0)],
                             "M_marble", cap_bottom=False, cap_top=False))
    objs.append(V.loft_rings("dome_pendentive_top", [(5.95, dz + 0.28, n, 0), (10.4, dz + 0.28, n, 0)],
                             "M_marble", cap_bottom=False, cap_top=False))

    # Matching coffer beam segments on the pendentive soffit outside the circular drum (r >= 6.05)
    cbm = _bmesh.new()
    for bx in (-6.0, -4.0, -2.0, 0.0, 2.0, 4.0, 6.0):
        if abs(bx) >= 5.95:
            V.add_box(cbm, (bx - 0.15, -8.0, 0.44), (bx + 0.15, 8.0, 0.86))
        else:
            y_cut = math.sqrt(max(0.0, 6.02 * 6.02 - bx * bx))
            if y_cut < 7.95:
                V.add_box(cbm, (bx - 0.15, -8.0, 0.44), (bx + 0.15, -y_cut, 0.86))
                V.add_box(cbm, (bx - 0.15, y_cut, 0.44), (bx + 0.15, 8.0, 0.86))
    for by in (-8.0, -6.0, -4.0, -2.0, 0.0, 2.0, 4.0, 6.0, 8.0):
        if abs(by) >= 5.95:
            V.add_box(cbm, (-6.0, by - 0.15, 0.44), (6.0, by + 0.15, 0.86))
        else:
            x_cut = math.sqrt(max(0.0, 6.02 * 6.02 - by * by))
            if x_cut < 5.95:
                V.add_box(cbm, (-6.0, by - 0.15, 0.44), (-x_cut, by + 0.15, 0.86))
                V.add_box(cbm, (x_cut, by - 0.15, 0.44), (6.0, by + 0.15, 0.86))
    objs.append(V.bm_to_object(cbm, "dome_spandrel_beams", ("M_gold",)))

    # Circular gold cornice drum flush with the coffer beam soffit (z = 0.36..0.95)
    objs += _loft2("dome_drum", [(6.38, 0.36), (6.46, 0.62), (6.35, 0.90)], "M_gold")
    objs += _loft2("dome_drum_in", [(5.95, 0.36), (5.92, 0.62), (6.00, 0.90)], "M_gold")
    objs += _loft2("dome_drum_seal", [(5.92, 0.36), (6.40, 0.36)], "M_gold")
    # Three interior latitude gilt bands seated proud on the inner surface of the dome bowl
    for (r, z) in ((5.55, 1.00 + dz), (4.60, 2.00 + dz), (2.85, 2.95 + dz)):
        objs += _loft2("dome_band", [(r, z - 0.06), (r - 0.08, z - 0.02), (r - 0.04, z + 0.06)], "M_gold")
    # Eight continuous curved meridian ribs swept along the inner dome profile
    rib_prof = V.chamfer_rect_profile(0.16, 0.14, 0.03)
    for i in range(8):
        a = math.tau * i / 8
        ca, sa = math.cos(a), math.sin(a)
        rpath = [((r - 0.04) * ca, (r - 0.04) * sa, z - 0.02) for (r, z) in prof_in]
        objs.append(V.sweep_profile(f"dome_rib_{i}", rpath, rib_prof, "M_gold",
                                    up_hint=Vector((-sa, ca, 0))))
    objs += _loft2("dome_oculus", [(1.25, 3.25 + dz), (1.3, 3.45 + dz), (1.1, 3.58 + dz)], "M_gold")
    objs.append(V.loft_rings("dome_eye_disc", [(1.14, 3.52 + dz, n, 0), (0.5, 3.62 + dz, n, 0), (0.08, 3.66 + dz, n, 0)],
                             "M_stone_dark", cap_bottom=False, cap_top=True))
    objs.append(V.loft_rings("dome_eye_disc_in", [(0.08, 3.64 + dz, n, 0), (0.5, 3.6 + dz, n, 0), (1.14, 3.5 + dz, n, 0)],
                             "M_stone_dark", cap_bottom=True, cap_top=False))
    sbm = _bmesh.new()
    srng = random.Random(23)
    for _ in range(16):
        a = srng.uniform(0, math.tau)
        rr = srng.uniform(0.06, 0.95)
        sx, sy = rr * math.cos(a), rr * math.sin(a)
        sz = 3.5 + dz + (1.0 - rr / 1.14) * 0.12 - 0.012
        st = srng.uniform(0.02, 0.04)
        V.add_box(sbm, (sx - st, sy - st, sz - st), (sx + st, sy + st, sz + st))
    objs.append(V.bm_to_object(sbm, "dome_stars", ("M_citywindow",)))
    return objs, {"size": [12.4, 16.4, 4.5], "origin": "rim-center"}


def palace_cove_dome():
    """The antechamber's WHOLE ceiling: a cloister-vault dome. The
    perimeter springs from the wall tops on all four sides (exact 20x16
    rectangle, no corner gaps) and slopes continuously up, the plan
    melting from rectangle to circle, to a gilt ring and a starred-eye
    oculus. NO flat ceiling anywhere in the room. Gilt meridian ribs +
    latitude bands articulate the bowl; a drop chain hangs from the eye
    for the chandelier below. Both windings on every sheet. Origin
    rim-center: place at wall-top height, room centre."""
    import bmesh as _bmesh
    objs = []
    W, D, RISE = 10.0, 8.0, 5.5
    CROWN = 1.3
    N = 48          # verts per ring
    STEPS = 13      # rings base -> crown

    def _ease(t):
        return math.sin(t * math.pi / 2.0)

    def _ring(t):
        # equal inset all around (true cloister groins), blending to a
        # circle near the crown so the round oculus seats cleanly
        e = _ease(t)
        m_in = (D - CROWN) * e
        rx = W - m_in
        rz = D - m_in
        blend = 0.0 if t < 0.45 else min(1.0, (t - 0.45) / 0.50) ** 1.6
        z = RISE * e
        # Warp angle so i in (6, 18, 30, 42) land on the exact rectangle groin corners
        a_corn = math.atan2(rz, rx)
        anchors_in = [0.0, math.pi * 0.25, math.pi * 0.5, math.pi * 0.75,
                      math.pi, math.pi * 1.25, math.pi * 1.5, math.pi * 1.75, math.tau]
        anchors_out = [0.0, a_corn, math.pi * 0.5, math.pi - a_corn,
                       math.pi, math.pi + a_corn, math.pi * 1.5, math.tau - a_corn, math.tau]
        pts = []
        for i in range(N):
            a_raw = math.tau * i / N
            seg = min(int(i // 6), 7)
            u = (a_raw - anchors_in[seg]) / (anchors_in[seg + 1] - anchors_in[seg])
            a_rect = anchors_out[seg] + u * (anchors_out[seg + 1] - anchors_out[seg])
            a = a_rect + (a_raw - a_rect) * blend
            c, s = math.cos(a), math.sin(a)
            # ray-to-rectangle-boundary point
            th = 1.0 / max(abs(c) / max(rx, 1e-3), abs(s) / max(rz, 1e-3))
            px, py = th * c, th * s
            # circle point at the crown radius
            qx, qy = CROWN * c, CROWN * s
            pts.append(Vector((px + (qx - px) * blend,
                               py + (qy - py) * blend, z)))
        return pts

    def _sheet_one(name, rings, mat, scale=1.0, drop=0.0, rev=False):
        """Bridge consecutive rings into a single-winding quad shell."""
        bm = _bmesh.new()
        rows = []
        for pts in rings:
            row = [bm.verts.new(Vector((p.x * scale, p.y * scale, p.z + drop)))
                   for p in pts]
            rows.append(row)
        bm.verts.ensure_lookup_table()
        for j in range(len(rows) - 1):
            a, b = rows[j], rows[j + 1]
            for i in range(N):
                k = (i + 1) % N
                q = [a[i], a[k], b[k], b[i]]
                bm.faces.new(reversed(q) if rev else q)
        return V.bm_to_object(bm, name, (mat,))

    rings = [_ring(j / (STEPS - 1.0)) for j in range(STEPS)]
    # Separate outer and inner shells so backfaces never z-fight or poke through bands
    objs.append(_sheet_one("cove_shell_out", rings, "M_marble", scale=1.015, drop=0.06, rev=False))
    objs.append(_sheet_one("cove_shell_in", rings, "M_marble", scale=1.0, drop=0.0, rev=True))
    # Proud 3D rectangular perimeter entablature/cornice around the 20x16 m wall top
    cbm = _bmesh.new()
    for sx in (-1, 1):
        # East/West 16 m wall-top cornice beams
        V.add_box(cbm, (sx * (W - 0.28), -D - 0.16, -0.16), (sx * (W + 0.16), D + 0.16, 0.14))
    for sy in (-1, 1):
        # North/South 20 m wall-top cornice beams
        V.add_box(cbm, (-W - 0.16, sy * (D - 0.28), -0.16), (W + 0.16, sy * (D + 0.16), 0.14))
    objs.append(V.bm_to_object(cbm, "cove_perimeter_cornice", ("M_gold",)))
    # Interior lower gold springing course + latitude bands riding proud of the inner shell
    objs.append(_sheet_one("cove_cornice_in", rings[0:2], "M_gold", scale=0.988, drop=-0.028, rev=True))
    for j in (4, 7):
        objs.append(_sheet_one(f"cove_band_{j}", rings[j:j + 2], "M_gold", scale=0.986, drop=-0.032, rev=True))
    # Continuous gold crown collar spanning rings[10..12] right into the oculus ring
    objs.append(_sheet_one("cove_crown_collar", rings[10:13], "M_gold", scale=0.985, drop=-0.032, rev=True))
    # Continuous swept meridian ribs along all 4 cardinal midpoints + 4 diagonal cloister groins + intermediates
    rib_prof = V.chamfer_rect_profile(0.20, 0.14, 0.03)
    for i in range(0, N, 3):
        a = math.tau * i / N
        ca, sa = math.cos(a), math.sin(a)
        path = [(rings[j][i].x * 0.988, rings[j][i].y * 0.988, rings[j][i].z - 0.025)
                for j in range(STEPS)]
        objs.append(V.sweep_profile(f"cove_rib_{i}", path, rib_prof, "M_gold",
                                    up_hint=Vector((-sa, ca, 0))))
    # the oculus: gold ring + starred eye sealing the crown
    zc = RISE
    objs.append(V.loft_rings("cove_oculus", [(1.52, zc - 0.06, 24, 0), (1.58, zc + 0.1, 24, 0),
                                             (1.28, zc + 0.2, 24, 0)], "M_gold",
                             cap_bottom=False, cap_top=False))
    objs.append(V.loft_rings("cove_oculus_in", [(1.28, zc + 0.2, 24, 0), (1.58, zc + 0.1, 24, 0),
                                                (1.52, zc - 0.06, 24, 0)], "M_gold",
                             cap_bottom=False, cap_top=False))
    # the eye: a deep night disc behind the ring, sown with gilt stars —
    # an emissive orange plate read as a hovering sun, not an oculus
    objs.append(V.loft_rings("cove_eye", [(1.32, zc + 0.16, 24, 0), (0.6, zc + 0.32, 24, 0),
                                          (0.08, zc + 0.38, 24, 0)], "M_stone_dark",
                             cap_bottom=False, cap_top=True))
    objs.append(V.loft_rings("cove_eye_in", [(0.08, zc + 0.36, 24, 0), (0.6, zc + 0.3, 24, 0),
                                             (1.32, zc + 0.14, 24, 0)], "M_stone_dark",
                             cap_bottom=True, cap_top=False))
    sbm = _bmesh.new()
    srng = random.Random(11)
    for _ in range(22):
        a = srng.uniform(0, math.tau)
        rr = srng.uniform(0.08, 1.12)
        sx, sy = rr * math.cos(a), rr * math.sin(a)
        sz = zc + 0.14 + (1.0 - rr / 1.32) * 0.2 - 0.015
        s = srng.uniform(0.022, 0.045)
        V.add_box(sbm, (sx - s, sy - s, sz - s), (sx + s, sy + s, sz + s))
    objs.append(V.bm_to_object(sbm, "cove_stars", ("M_citywindow",)))
    # no separate drop chain: the dome-variant chandelier carries ONE
    # unbroken rope from its ring to this crown
    return objs, {"size": [20.0, 16.0, RISE + 0.4], "origin": "rim-center"}


def _add_hollow_wheel(bm, r_in, r_out, z0, z1, n=20):
    """Add a closed hollow polygonal wheel-crown (annular ring) to `bm`."""
    ring_ib = [bm.verts.new((r_in * math.cos(math.tau * i / n), r_in * math.sin(math.tau * i / n), z0)) for i in range(n)]
    ring_ob = [bm.verts.new((r_out * math.cos(math.tau * i / n), r_out * math.sin(math.tau * i / n), z0)) for i in range(n)]
    ring_it = [bm.verts.new((r_in * math.cos(math.tau * i / n), r_in * math.sin(math.tau * i / n), z1)) for i in range(n)]
    ring_ot = [bm.verts.new((r_out * math.cos(math.tau * i / n), r_out * math.sin(math.tau * i / n), z1)) for i in range(n)]
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((ring_ob[i], ring_ob[j], ring_ot[j], ring_ot[i]))  # outer face
        bm.faces.new((ring_ib[j], ring_ib[i], ring_it[i], ring_it[j]))  # inner face
        bm.faces.new((ring_it[i], ring_it[j], ring_ot[j], ring_ot[i]))  # top face
        bm.faces.new((ring_ob[i], ring_ib[i], ring_ib[j], ring_ob[j]))  # bottom face


def chandelier_gilt(chain_top=3.6):
    """Hanging gold wheel-chandelier (corona lucis), GRAND: two hollow gilt
    tiers of cylindrical wax candles in moulded bobeche drip dishes, 6 radial
    wheel spokes, 6 diagonal curtain chains between the rims, a pendant drop
    below, and ONE unbroken iron chain running all the way up into the vault,
    crowned with a gilt boss where it meets the ceiling. Origin at the great
    ring's centre."""
    objs = []
    bm_gild = bmesh.new()
    # Hollow lower wheel-crown (r = 1.12..1.34) with stepped rim moulding
    _add_hollow_wheel(bm_gild, 1.12, 1.34, -0.07, 0.07, n=20)
    _add_hollow_wheel(bm_gild, 1.10, 1.38, -0.025, 0.025, n=20)
    # Hollow upper wheel-crown (r = 0.52..0.72) with stepped rim moulding
    _add_hollow_wheel(bm_gild, 0.52, 0.72, 0.91, 1.05, n=16)
    _add_hollow_wheel(bm_gild, 0.50, 0.75, 0.96, 1.00, n=16)
    # Central hub collar + 6 continuous radial wheel spokes connecting hub to great ring
    V.add_cyl(bm_gild, 0.0, 0.0, -0.10, 0.20, 0.14, n=12)
    spoke_prof = V.chamfer_rect_profile(0.048, 0.044, 0.01)
    for i in range(6):
        a = math.tau * i / 6
        ca, sa = math.cos(a), math.sin(a)
        objs.append(V.sweep_profile(f"chand_spoke_{i}",
                                    [(ca * 0.12, sa * 0.12, 0.0), (ca * 1.15, sa * 1.15, 0.0)],
                                    spoke_prof, "M_gild", up_hint=Vector((0, 0, 1))))
    # Moulded gilt bobeche drip dishes under every candle
    for i in range(12):
        a = math.tau * (i + 0.5) / 12
        cx, cy = math.cos(a) * 1.22, math.sin(a) * 1.22
        V.add_cyl(bm_gild, cx, cy, 0.07, 0.025, 0.075, n=10)
        V.add_cyl(bm_gild, cx, cy, 0.095, 0.015, 0.052, n=10)
    for i in range(7):
        a = math.tau * i / 7
        cx, cy = math.cos(a) * 0.62, math.sin(a) * 0.62
        V.add_cyl(bm_gild, cx, cy, 1.05, 0.025, 0.072, n=10)
        V.add_cyl(bm_gild, cx, cy, 1.075, 0.015, 0.050, n=10)
    objs.append(V.bm_to_object(bm_gild, "chand_ring", ("M_gild",)))

    bm = bmesh.new()
    # The long vertical chain to the vault (top reaches +chain_top over the ring)
    V.add_cyl(bm, 0.0, 0.0, 0.98, chain_top - 0.98, 0.032, n=8)
    for z_link in range(1, int(chain_top - 0.8)):
        V.add_cyl(bm, 0.0, 0.0, z_link + 0.10, 0.07, 0.048, n=8)
    # 6 diagonal curtain chains from upper wheel (r=0.70, z=0.98) to lower wheel (r=1.28, z=0.06)
    for i in range(6):
        a = math.tau * i / 6
        x0, y0 = math.cos(a) * 0.68, math.sin(a) * 0.68
        x1, y1 = math.cos(a) * 1.26, math.sin(a) * 1.26
        for k in range(9):
            t = k / 8.0
            cx, cy = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            cz = 0.98 - 0.92 * t - 0.05 * math.sin(math.pi * t)
            V.add_box(bm, (cx - 0.020, cy - 0.020, cz - 0.065), (cx + 0.020, cy + 0.020, cz + 0.065))
    # The pendant drop rod under the great ring
    V.add_cyl(bm, 0.0, 0.0, -0.55, 1.55, 0.028, n=8)
    objs.append(V.bm_to_object(bm, "chand_chain", ("M_iron",)))

    drop = V.loft_rings("chand_drop", [(0.02, -0.58, 10, 0), (0.12, -0.42, 10, 0),
                                       (0.06, -0.26, 10, 0), (0.14, -0.16, 10, 0),
                                       (0.03, -0.06, 10, 0)], "M_gild")
    objs.append(drop)

    # Cylindrical wax candles on both tiers
    bm = bmesh.new()
    for i in range(12):
        a = math.tau * (i + 0.5) / 12
        cx, cy = math.cos(a) * 1.22, math.sin(a) * 1.22
        V.add_cyl(bm, cx, cy, 0.10, 0.28, 0.038, n=10)
    for i in range(7):
        a = math.tau * i / 7
        cx, cy = math.cos(a) * 0.62, math.sin(a) * 0.62
        V.add_cyl(bm, cx, cy, 1.08, 0.26, 0.036, n=10)
    objs.append(V.bm_to_object(bm, "chand_candles", ("M_wax",)))

    for i in range(12):
        a = math.tau * (i + 0.5) / 12
        f = _pflame("chand_flame%d" % i)
        f.location = (math.cos(a) * 1.22, math.sin(a) * 1.22, 0.38)
        objs.append(f)
    for i in range(7):
        a = math.tau * i / 7
        f = _pflame("chand_flame_u%d" % i)
        f.location = (math.cos(a) * 0.62, math.sin(a) * 0.62, 1.34)
        objs.append(f)
    boss = V.loft_rings("chand_boss", [(0.16, chain_top - 0.16, 10, 0),
                                       (0.20, chain_top - 0.05, 10, 0),
                                       (0.08, chain_top + 0.02, 10, 0)], "M_gold")
    objs.append(boss)
    return objs, {"size": [2.8, 2.8, chain_top + 0.6], "origin": "center"}



def carpet_runner_8m():
    """Processional runner: deep red field, gold borders, inner filigree frame,
    central woven gold medallion, and end fringe tassels — flat and passable.
    Origin bottom-center of the run (lies along X)."""
    objs = []
    bm = bmesh.new()
    V.add_box(bm, (-4.0, -1.1, 0.008), (4.0, 1.1, 0.028))
    objs.append(V.bm_to_object(bm, "carpet_field", ("M_cloth",)))
    bm = bmesh.new()
    for sy in (-1.0, 0.94):
        V.add_box(bm, (-3.94, sy, 0.03), (3.94, sy + 0.06, 0.042))
    V.add_box(bm, (-3.94, -0.94, 0.03), (-3.88, 0.94, 0.042))
    V.add_box(bm, (3.88, -0.94, 0.03), (3.94, 0.94, 0.042))
    # Inner filigree border lines
    for sy in (-0.78, 0.75):
        V.add_box(bm, (-3.68, sy, 0.029), (3.68, sy + 0.03, 0.038))
    for sx in (-3.68, 3.65):
        V.add_box(bm, (sx, -0.75, 0.029), (sx + 0.03, 0.75, 0.038))
    # Corner knot squares at all 4 inner corners
    for cx in (-3.66, 3.66):
        for cy in (-0.76, 0.76):
            V.add_box(bm, (cx - 0.08, cy - 0.08, 0.030), (cx + 0.08, cy + 0.08, 0.041))
    # Central woven gold spine & 3 lozenge medallions along the runner
    V.add_box(bm, (-3.50, -0.025, 0.029), (3.50, 0.025, 0.038))
    for mx in (-2.2, 0.0, 2.2):
        V.add_box(bm, (mx - 0.24, -0.20, 0.030), (mx + 0.24, 0.20, 0.040))
        V.add_box(bm, (mx - 0.12, -0.10, 0.031), (mx + 0.12, 0.10, 0.042))
    # Gold fringe tassels along the -X and +X ends
    for i in range(11):
        fy = -0.90 + i * 0.18
        V.add_box(bm, (-4.06, fy - 0.025, 0.008), (-3.94, fy + 0.025, 0.026))
        V.add_box(bm, (3.94, fy - 0.025, 0.008), (4.06, fy + 0.025, 0.026))
    objs.append(V.bm_to_object(bm, "carpet_border", ("M_gild",)))
    return objs, {"size": [8, 2.2, 0.05], "origin": "bottom-center"}


def scriptorium_shelf():
    """Tall book-press for the west wing: carved case, three laden shelves.
    Origin bottom-center against a wall (back at +Y). Solid."""
    objs = []
    bm = bmesh.new()
    V.add_box(bm, (-1.2, 0.16, 0.0), (1.2, 0.24, 2.3))             # back board
    V.add_box(bm, (-1.26, -0.24, 0.0), (1.26, 0.25, 0.10))         # base plinth
    V.add_box(bm, (-1.28, -0.26, 2.22), (1.28, 0.25, 2.34))        # crown cornice
    for sx in (-1.2, 0.0, 1.2):
        w_stile = 0.04 if sx == 0.0 else 0.06
        V.add_box(bm, (sx - w_stile, -0.22, 0.08), (sx + w_stile, 0.24, 2.24))
    for z in (0.08, 0.78, 1.48, 2.18):
        V.add_box(bm, (-1.2, -0.2, z), (1.2, 0.24, z + 0.06))
    objs.append(V.bm_to_object(bm, "shelf_case", ("M_wood",)))
    bm_g = bmesh.new()
    V.add_box(bm_g, (-1.29, -0.27, 2.28), (1.29, 0.25, 2.32))      # gilt cornice band
    for z in (0.10, 0.80, 1.50, 2.20):
        V.add_box(bm_g, (-1.21, -0.21, z), (1.21, -0.19, z + 0.025))
    objs.append(V.bm_to_object(bm_g, "shelf_gild", ("M_gild",)))
    for (mat, jitter) in (("M_leather", 0), ("M_cloth", 1)):
        bm = bmesh.new()
        r2 = random.Random(31 + jitter)
        for z in (0.14, 0.84, 1.54):
            x = -1.1
            while x < 1.0:
                w = r2.uniform(0.08, 0.16)
                h = r2.uniform(0.4, 0.58)
                if abs(x + w * 0.5) > 0.06 and r2.random() < 0.5:
                    V.add_box(bm, (x, -0.12, z), (x + w, 0.16, z + h))
                x += w + 0.015
        objs.append(V.bm_to_object(bm, "books_%d" % jitter, (mat,)))
    return objs, {"size": [2.5, 0.5, 2.35], "origin": "bottom-center"}


BUILDERS = {
    "palace_floor_4x4": palace_floor_4x4,
    "banquet_table_6m": banquet_table_6m,
    "banquet_bench_6m": banquet_bench_6m,
    "chandelier_gilt": chandelier_gilt,
    "palace_dome_12m": palace_dome_12m,
    "palace_cove_dome": palace_cove_dome,
    "chandelier_dome_low": lambda: chandelier_gilt(7.1),
    "chandelier_dome_high": lambda: chandelier_gilt(8.3),
    "carpet_runner_8m": carpet_runner_8m,
    "scriptorium_shelf": scriptorium_shelf,
    "radiant_spire_a": lambda: radiant_spire(3),
    "radiant_spire_b": lambda: radiant_spire(9),
    "radiant_castle_a": lambda: radiant_castle(4),
    "radiant_castle_b": lambda: radiant_castle(11),
    "palace_wall_4x4": palace_wall_4x4,
    "palace_wall_low_4m": palace_wall_low_4m,
    "palace_cornice_4m": palace_cornice_4m,
    "palace_portal_4m": palace_portal_4m,
    "palace_window_4m": palace_window_4m,
    "palace_arcade_4m": palace_arcade_4m,
    "palace_balustrade_4m": palace_balustrade_4m,
    "palace_pier": palace_pier,
    "gilt_finial": gilt_finial,
    "palace_pediment_8m": palace_pediment_8m,
}
