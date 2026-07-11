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


# ---------------------------------------------------------------- helpers

def _dentils(bm, x0, x1, z, y_front, depth=0.1, w=0.16, gap=0.17, h=0.2):
    """A run of little gold teeth under a cornice/frieze."""
    x = x0 + gap * 0.5
    while x + w < x1 - 0.02:
        V.add_box(bm, (x, y_front - depth, z), (x + w, y_front + 0.02, z + h))
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


def _panel_relief(bm, x0, x1, z0, z1, y_face, out, inset=0.05, frame=0.16):
    """Raised rectangular frame moulding — palace paneling instead of the
    cloister's rough ashlar. y_face is the wall face plane; `out` (+1/-1)
    is the outward direction, the frame stands proud by `inset`."""
    g = 0.012
    ya, yb = y_face - 0.02 * out, y_face + inset * out
    y0, y1 = min(ya, yb), max(ya, yb)
    V.add_box(bm, (x0, y0, z0), (x1, y1, z0 + frame))
    V.add_box(bm, (x0, y0, z1 - frame), (x1, y1, z1))
    V.add_box(bm, (x0, y0, z0 + frame - g), (x0 + frame, y1, z1 - frame + g))
    V.add_box(bm, (x1 - frame, y0, z0 + frame - g), (x1, y1, z1 - frame + g))


# ---------------------------------------------------------------- pieces

def palace_floor_4x4():
    """Polished marble paving, broad 2 m slabs with hairline joints and a
    thin gold inlay cross at the tile heart. Origin: center, top at z=0."""
    bm = bmesh.new()
    rng = random.Random(19)
    V.add_box(bm, (-2.0, -2.0, -0.22), (2.0, 2.0, -0.05))
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
    V.add_box(bm, (-2, -0.16, 0), (2, 0.16, 4.0))                  # core
    V.add_box(bm, (-2, -0.21, 0.0), (2, 0.21, 0.55))               # plinth
    V.add_box(bm, (-2, -0.19, 3.62), (2, 0.19, 4.0))               # head band
    for (yf, out) in ((-0.16, -1), (0.16, 1)):
        for (px0, px1) in ((-1.86, -0.1), (0.1, 1.86)):
            _panel_relief(bm, px0, px1, 0.75, 2.0, yf, out, frame=0.13)
            _panel_relief(bm, px0, px1, 2.5, 3.4, yf, out, frame=0.13)
    objs.append(V.bm_to_object(bm, "palace_wall", ("M_marble",)))
    bm = bmesh.new()
    V.add_box(bm, (-2, -0.20, 2.14), (2, 0.20, 2.30))              # string course
    _dentils(bm, -2.0, 2.0, 3.42, -0.17)                           # front dentils
    _dentils(bm, -2.0, 2.0, 3.42, 0.07, depth=-0.1)                # back dentils
    objs.append(V.bm_to_object(bm, "palace_wall_gild", ("M_gild",)))
    return objs, {"size": [4, 0.5, 4], "origin": "bottom-center"}


def palace_wall_low_4m():
    """Marble parapet, 1.05 m, gold coping. Origin bottom-center."""
    objs = []
    bm = bmesh.new()
    V.add_box(bm, (-2, -0.17, 0), (2, 0.17, 0.86))
    objs.append(V.bm_to_object(bm, "palace_parapet", ("M_marble",)))
    bm = bmesh.new()
    V.add_box(bm, (-2, -0.23, 0.86), (2, 0.23, 1.02))
    objs.append(V.bm_to_object(bm, "palace_parapet_gild", ("M_gild",)))
    return objs, {"size": [4, 0.5, 1.05], "origin": "bottom-center"}


def palace_cornice_4m():
    """Projecting marble cornice with a continuous gold bead. Bottom-center."""
    prof = [(0.0, 0.0), (0.18, 0.02), (0.22, 0.10), (0.12, 0.16), (0.18, 0.26), (0.0, 0.3)]
    path = [(-2, 0, 0), (2, 0, 0)]
    body = V.sweep_profile("palace_cornice", path, prof, "M_marble",
                           up_hint=Vector((0, 0, 1)))
    bm = bmesh.new()
    V.add_box(bm, (-2, 0.10, 0.02), (2, 0.24, 0.10))
    bead = V.bm_to_object(bm, "palace_cornice_gild", ("M_gild",))
    return [body, bead], {"size": [4, 0.3, 0.3], "origin": "bottom-center"}


def palace_portal_4m():
    """Palace doorway: marble panel, 1.9-wide arch, two GOLD archivolts and
    a gilt sunburst in the tympanum zone. Passage along Y, bottom-center."""
    objs = []
    panel = V.wall_panel_with_arch("palace_portal_wall", 4.0, 4.0, 0.5, 1.9, 2.1,
                                   sharpness=1.1, mat="M_marble", segments=12)
    objs.append(panel)
    arch = V.pointed_arch(1.9, 1.1, 12, 2.1)
    for k, (scale, depth) in enumerate(((1.12, 0.30), (1.28, 0.16))):
        path = [(x * scale, 0.0, y + (scale - 1) * 0.4) for (x, y) in arch]
        prof = V.chamfer_rect_profile(0.15 + k * 0.04, depth, 0.04)
        objs.append(V.sweep_profile(f"palace_archivolt{k}", path, prof, "M_gild",
                                    up_hint=Vector((0, 0, 1))))
    bm = bmesh.new()                                               # sunburst rays
    for a in range(7):
        ang = math.pi * (0.16 + 0.68 * a / 6)
        cx, cz = 0.0, 3.28
        dx, dz = math.cos(ang), math.sin(ang)
        x0, z0 = cx + dx * 0.14, cz + dz * 0.14
        x1, z1 = cx + dx * 0.5, cz + dz * 0.5
        V.add_box(bm, (min(x0, x1) - 0.03, -0.29, min(z0, z1) - 0.03),
                  (max(x0, x1) + 0.03, -0.24, max(z0, z1) + 0.03))
    V.add_box(bm, (-0.16, -0.30, 3.12), (0.16, -0.23, 3.44))       # sun heart
    objs.append(V.bm_to_object(bm, "palace_sunburst", ("M_gild",)))
    for sx in (-1.15, 1.15):                                       # jambs
        c = _marble_colonnette(0.12, 2.0)
        c.location = (sx, 0, 0)
        objs.append(c)
        cap = _gilt_cap(0.12, 0)
        cap.location = (sx, 0, 2.0)
        objs.append(cap)
    return objs, {"size": [4, 0.6, 4], "origin": "bottom-center", "opening": [1.9, 2.9]}


def palace_window_4m():
    """Palace bay with twin glazed lancets in GOLD tracery, matching the
    wall module (4 x 4, 0.5 thick, bottom-center)."""
    objs = []
    y = 0.25
    bm = bmesh.new()
    V.add_box(bm, (-2, -y, 0.0), (2, y, 0.9))                      # footing
    V.add_box(bm, (-2, -y, 0.0), (2, y + 0.04, 0.55))              # plinth
    V.add_box(bm, (-2, -y, 0.9), (-1.25, y, 4.0))                  # piers
    V.add_box(bm, (-0.35, -y, 0.9), (0.35, y, 4.0))
    V.add_box(bm, (1.25, -y, 0.9), (2, y, 4.0))
    V.add_box(bm, (-2, -y, 3.45), (2, y, 4.0))                     # head band
    for s in (-1, 1):                                              # stepped heads
        V.add_box(bm, (s * 1.25 - (0.2 if s > 0 else 0), -y, 3.0),
                  (s * 1.25 + (0.2 if s < 0 else 0), y, 3.45))
        V.add_box(bm, (s * 0.35 - (0.2 if s < 0 else 0), -y, 3.0),
                  (s * 0.35 + (0.2 if s > 0 else 0), y, 3.45))
    objs.append(V.bm_to_object(bm, "palace_win_wall", ("M_marble",)))
    bm = bmesh.new()
    V.add_box(bm, (-1.4, -y - 0.06, 0.78), (1.4, y + 0.06, 0.94))  # gold sill
    V.add_box(bm, (-1.4, -y - 0.06, 3.42), (1.4, y + 0.06, 3.58))  # gold hood
    for s in (-1, 1):                                              # tracery bars
        V.add_box(bm, (s * 0.78 - 0.04, -y + 0.02, 0.94), (s * 0.78 + 0.04, -y + 0.10, 3.0))
        V.add_box(bm, (s * 0.35, -y + 0.02, 1.9), (s * 1.25, -y + 0.10, 1.98))
    objs.append(V.bm_to_object(bm, "palace_win_gild", ("M_gild",)))
    bm = bmesh.new()
    for s in (-1, 1):
        V.add_box(bm, (s * 0.35, -0.04, 0.94), (s * 1.25, 0.04, 3.0))
        V.add_box(bm, (s * 0.55, -0.04, 3.0), (s * 1.05, 0.04, 3.42))
    # M_citywindow: warm lamplit panes in glory, dead-dark in ruin — the
    # palace glows from within instead of showing raw sky through the bay
    objs.append(V.bm_to_object(bm, "palace_win_panes", ("M_citywindow",)))
    return objs, {"size": [4, 0.5, 4], "origin": "bottom-center"}


def palace_arcade_4m():
    """Open palace colonnade bay: a true passage (no parapet) with a wide
    arch, gold archivolt edge and gilt-capped colonnettes. Bottom-center."""
    objs = []
    panel = V.wall_panel_with_arch("palace_arcade_panel", 4.0, 4.0, 0.4, 2.4, 2.0,
                                   sharpness=0.9, mat="M_marble", segments=12)
    objs.append(panel)
    arch = V.pointed_arch(2.4, 0.9, 12, 2.0)
    path = [(x * 1.1, 0.0, y + 0.08) for (x, y) in arch]
    prof = V.chamfer_rect_profile(0.14, 0.14, 0.035)
    objs.append(V.sweep_profile("palace_arcade_gild", path, prof, "M_gild",
                                up_hint=Vector((0, 0, 1))))
    for sx in (-1.35, 1.35):
        c = _marble_colonnette(0.13, 1.9)
        c.location = (sx, 0, 0)
        objs.append(c)
        cap = _gilt_cap(0.13, 0)
        cap.location = (sx, 0, 1.9)
        objs.append(cap)
    return objs, {"size": [4, 0.5, 4], "origin": "bottom-center", "opening": [2.4, 3.1]}


def palace_balustrade_4m():
    """Marble balustrade with a gold handrail. Origin bottom-center."""
    objs = []
    bm = bmesh.new()
    V.add_box(bm, (-2, -0.14, 0), (2, 0.14, 0.12))                 # base rail
    objs.append(V.bm_to_object(bm, "palace_bal_base", ("M_marble",)))
    for i in range(9):
        x = -1.78 + i * 0.445
        rings = [(0.085, 0.12, 8, 0), (0.11, 0.3, 8, 0), (0.065, 0.55, 8, 0),
                 (0.10, 0.78, 8, 0), (0.085, 0.9, 8, 0)]
        b = V.loft_rings("palace_baluster", rings, "M_marble")
        b.location = (x, 0, 0)
        objs.append(b)
    bm = bmesh.new()
    V.add_box(bm, (-2, -0.12, 0.9), (2, 0.12, 1.06))
    objs.append(V.bm_to_object(bm, "palace_bal_rail", ("M_gild",)))
    return objs, {"size": [4, 0.3, 1.06], "origin": "bottom-center"}


def palace_pier():
    """Square marble corner pier, 4.1 m, gold base and capital bands, gilt
    finial cap — makes wall junctions read deliberate. Origin bottom-center."""
    objs = []
    bm = bmesh.new()
    V.add_box(bm, (-0.34, -0.34, 0.0), (0.34, 0.34, 4.1))
    objs.append(V.bm_to_object(bm, "palace_pier", ("M_marble",)))
    bm = bmesh.new()
    V.add_box(bm, (-0.4, -0.4, 0.0), (0.4, 0.4, 0.5))
    V.add_box(bm, (-0.4, -0.4, 3.7), (0.4, 0.4, 3.95))
    objs.append(V.bm_to_object(bm, "palace_pier_gild", ("M_gild",)))
    fin = _gilt_finial_obj(0.55)
    fin.location = (0, 0, 4.1)
    objs.append(fin)
    return objs, {"size": [0.8, 0.8, 4.7], "origin": "bottom-center"}


def _gilt_finial_obj(h):
    n = 8
    rings = [(0.16, 0.0, n, 0), (0.2, h * 0.18, n, 0), (0.11, h * 0.42, n, 0),
             (0.14, h * 0.55, n, 0), (0.015, h, n, 0)]
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
    for s in (-1, 1):                                              # raking gold edge
        steps = 8
        for i in range(steps):
            t0, t1 = i / steps, (i + 1) / steps
            x0, z0 = s * w * (1 - t0), h * t0
            x1, z1 = s * w * (1 - t1), h * t1
            V.add_box(bm, (min(x0, x1) - 0.05, -d - 0.04, min(z0, z1)),
                      (max(x0, x1) + 0.05, -d + 0.04, max(z0, z1) + 0.09))
    # sun disc
    bm3 = bmesh.new()
    ring = [bm3.verts.new((0.52 * math.cos(math.tau * i / 12), -d - 0.05,
                           0.72 + 0.52 * math.sin(math.tau * i / 12))) for i in range(12)]
    c = bm3.verts.new((0, -d - 0.05, 0.72))
    for i in range(12):
        bm3.faces.new((c, ring[i], ring[(i + 1) % 12]))
    objs.append(V.bm_to_object(bm, "palace_pediment_rake", ("M_gild",)))
    objs.append(V.bm_to_object(bm3, "palace_pediment_sun", ("M_gild",)))
    return objs, {"size": [8, 0.9, 2.1], "origin": "bottom-center"}


# ------------------------------------------------------- radiant skyline
# Backdrop-scale marble-and-gold silhouettes for the Sanctum's horizon:
# no mortal masonry above the hours. Warm-lit windows ride M_citywindow
# (lamplit in glory, dead-dark in ruin). No collision — skyline pieces.

def _radiant_tower(L, G, W, rng, cx, cy, base, w, h, cap=1.0):
    """One marble tower: shaft, gold string courses, window strips, and a
    gold pyramidal cap (returned as its own loft object)."""
    hw = w * 0.5
    V.add_box(L, (cx - hw, cy - hw, base), (cx + hw, cy + hw, base + h))
    for k in (0.35, 0.7):
        V.add_box(G, (cx - hw - 0.12, cy - hw - 0.12, base + h * k),
                  (cx + hw + 0.12, cy + hw + 0.12, base + h * k + 0.5))
    for (dx, dy) in ((0, -hw), (0, hw), (-hw, 0), (hw, 0)):
        ww = w * 0.16
        if dx == 0:
            V.add_box(W, (cx - ww, cy + dy - 0.06, base + h * 0.45),
                      (cx + ww, cy + dy + 0.06, base + h * 0.82))
        else:
            V.add_box(W, (cx + dx - 0.06, cy - ww, base + h * 0.45),
                      (cx + dx + 0.06, cy + ww, base + h * 0.82))
    rings = [(hw * 1.18, base + h, 4, 0.785), (0.06, base + h + w * 1.1 * cap, 4, 0.785)]
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
    objs.append(_radiant_tower(L, G, W, rng, 0, 0, 0.0, rng.uniform(5.5, 7.0), h, cap=1.3))
    for a in (0.9, -2.2):
        d = rng.uniform(4.5, 6.0)
        objs.append(_radiant_tower(L, G, W, rng, math.cos(a) * d, math.sin(a) * d,
                                   0.0, rng.uniform(2.4, 3.2), h * rng.uniform(0.45, 0.6)))
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


BUILDERS = {
    "palace_floor_4x4": palace_floor_4x4,
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
