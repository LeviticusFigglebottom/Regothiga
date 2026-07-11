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




# ------------------------------------------------------- palace furnishing

def banquet_table_6m():
    """Feast table: marble slab on carved legs, a gold runner down the
    middle, candle pairs riding it. Origin bottom-center. Solid."""
    objs = []
    bm = bmesh.new()
    V.add_box(bm, (-3.0, -0.62, 0.72), (3.0, 0.62, 0.86))          # top
    for sx in (-2.6, 2.6):
        for sy in (-0.44, 0.44):
            V.add_box(bm, (sx - 0.09, sy - 0.09, 0.0), (sx + 0.09, sy + 0.09, 0.72))
    V.add_box(bm, (-2.6, -0.06, 0.3), (2.6, 0.06, 0.42))           # stretcher
    objs.append(V.bm_to_object(bm, "table_body", ("M_marble",)))
    bm = bmesh.new()
    V.add_box(bm, (-3.0, -0.22, 0.861), (3.0, 0.22, 0.875))        # gold runner
    objs.append(V.bm_to_object(bm, "table_runner", ("M_gild",)))
    bm = bmesh.new()
    for cx in (-2.0, 0.0, 2.0):
        V.add_box(bm, (cx - 0.045, -0.045, 0.875), (cx + 0.045, 0.045, 1.06))
    objs.append(V.bm_to_object(bm, "table_candles", ("M_wax",)))
    return objs, {"size": [6, 1.25, 1.1], "origin": "bottom-center"}


def banquet_bench_6m():
    """Long bench for the feast table. Origin bottom-center. Solid."""
    bm = bmesh.new()
    V.add_box(bm, (-3.0, -0.19, 0.4), (3.0, 0.19, 0.5))
    for sx in (-2.6, 2.6):
        V.add_box(bm, (sx - 0.08, -0.15, 0.0), (sx + 0.08, 0.15, 0.4))
    obj = V.bm_to_object(bm, "bench", ("M_wood",))
    return [obj], {"size": [6, 0.4, 0.5], "origin": "bottom-center"}


def palace_dome_12m():
    """Coffered crossing dome. Every lathe surface is built DOUBLE-SIDED
    (both windings) — the export chain normalises winding, so trusting a
    single orientation left the bowl backface-culled into open sky. Rim
    collar seats on the spring plane over a grid-aligned 12x8 hole
    (corner 7.21 < 7.45). The bowl is pale MARBLE, not attic stone: seen
    from the floor it must read as a dressed rotunda, and the dark brick
    read as a raw slab hanging in the room. The drum bottom is closed
    with a gilt washer — the open annulus was a black ring of attic."""
    import bmesh as _bmesh
    from mathutils import Matrix as _M
    objs = []
    n = 28

    def _loft2(name, prof, mat):
        rings = [(r, z, n, 0) for (r, z) in prof]
        a = V.loft_rings(name, rings, mat, cap_bottom=False, cap_top=False)
        b = V.loft_rings(name + "_in", list(reversed(rings)), mat,
                         cap_bottom=False, cap_top=False)
        return [a, b]

    prof = [(6.0, 0.0), (5.85, 0.62), (5.4, 1.3), (4.6, 2.05), (3.5, 2.7),
            (2.2, 3.2), (1.1, 3.42)]
    objs += _loft2("dome_shell", prof, "M_marble")
    objs += _loft2("dome_rim", [(7.45, -0.05), (7.5, 0.14), (7.28, 0.85),
                                (6.6, 1.12), (6.05, 1.18)], "M_gold")
    # the drum: a fascia ring dropping below the spring plane so grazing
    # sightlines through the hole meet gilt stone, never the open attic
    objs += _loft2("dome_drum", [(6.6, -0.85), (6.72, -0.2), (6.6, 0.05)], "M_gold")
    objs += _loft2("dome_drum_in", [(6.1, -0.8), (6.1, 0.05)], "M_marble")
    # the washer that closes the drum from below (6.06..6.74 at the fascia's
    # own depth) — without it the annulus between fascia and inner drum is
    # an open slot straight up into the dark
    objs += _loft2("dome_drum_seal", [(6.06, -0.82), (6.74, -0.82)], "M_gold")
    for (r, z) in ((5.63, 0.95), (4.75, 1.9), (2.9, 2.92)):
        objs += _loft2("dome_band", [(r + 0.05, z - 0.08), (r + 0.09, z), (r + 0.05, z + 0.08)], "M_gold")
    # eight meridian ribs: chains of gilt blocks following the profile
    bm = _bmesh.new()
    seg_pts = [(5.92, 0.3), (5.62, 0.97), (5.0, 1.7), (4.05, 2.4), (2.85, 2.95), (1.6, 3.32)]
    for i in range(8):
        a = math.tau * i / 8
        rot = _M.Rotation(a, 3, "Z")
        for (r, z) in seg_pts:
            c = rot @ Vector((r, 0, z))
            half = rot @ Vector((0.14, 0.14, 0))
            up = 0.34
            vs = []
            for sx in (-1, 1):
                for sy in (-1, 1):
                    for sz in (-up / 2, up / 2):
                        vs.append(bm.verts.new(Vector((c.x + sx * abs(half.x),
                                                       c.y + sx * half.y, c.z + sz))))
            bm.verts.ensure_lookup_table()
            f = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 2, 6, 4), (1, 5, 7, 3), (0, 4, 5, 1), (2, 3, 7, 6)]
            for q in f:
                bm.faces.new([vs[j] for j in q])
    objs.append(V.bm_to_object(bm, "dome_ribs", ("M_gold",)))
    objs += _loft2("dome_oculus", [(1.25, 3.25), (1.3, 3.45), (1.1, 3.58)], "M_gold")
    # the eye overlaps the oculus ring (1.14 > 1.1): with no attic lid
    # above, an open annulus here would be a ring of naked sky. DARK stone
    # sown with gilt stars — a big M_flame plate breathes with the flame
    # animator and the whole crown read as moving
    objs += _loft2("dome_eye_disc", [(1.14, 3.5), (0.5, 3.6), (0.08, 3.64)], "M_stone_dark")
    sbm = _bmesh.new()
    srng = random.Random(23)
    for _ in range(16):
        a = srng.uniform(0, math.tau)
        rr = srng.uniform(0.06, 0.95)
        sx, sy = rr * math.cos(a), rr * math.sin(a)
        sz = 3.5 + (1.0 - rr / 1.14) * 0.12 - 0.012
        st = srng.uniform(0.02, 0.04)
        V.add_box(sbm, (sx - st, sy - st, sz - st), (sx + st, sy + st, sz + st))
    objs.append(V.bm_to_object(sbm, "dome_stars", ("M_flame",)))
    return objs, {"size": [15.0, 15.0, 3.7], "origin": "rim-center"}


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
        m_in = (D - CROWN) * _ease(t)
        rx = W - m_in
        rz = D - m_in
        blend = 0.0 if t < 0.6 else ((t - 0.6) / 0.4) ** 2
        z = RISE * _ease(t)
        pts = []
        for i in range(N):
            a = math.tau * i / N
            c, s = math.cos(a), math.sin(a)
            # ray-to-rectangle-boundary point
            th = 1.0 / max(abs(c) / max(rx, 1e-3), abs(s) / max(rz, 1e-3))
            px, py = th * c, th * s
            # circle point at the crown radius
            qx, qy = CROWN * c, CROWN * s
            pts.append(Vector((px + (qx - px) * blend,
                               py + (qy - py) * blend, z)))
        return pts

    def _sheet(name, rings, mat, scale=1.0, drop=0.0):
        """Bridge consecutive rings into a quad shell — BOTH windings."""
        out = []
        for rev in (False, True):
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
            out.append(V.bm_to_object(bm, name + ("_in" if rev else ""), (mat,)))
        return out

    rings = [_ring(j / (STEPS - 1.0)) for j in range(STEPS)]
    objs += _sheet("cove_shell", rings, "M_marble")
    # base cornice: a gold course where the bowl leaves the walls
    objs += _sheet("cove_cornice", rings[0:2], "M_gold", scale=1.004, drop=-0.02)
    # latitude bands: gilt courses riding the bowl
    for j in (4, 7, 10):
        objs += _sheet("cove_band", rings[j:j + 2], "M_gold", scale=0.992, drop=-0.03)
    # meridian ribs: CONTINUOUS gilt runs following the slope — dashed
    # segments read as stitching, not structure
    bm = _bmesh.new()
    for i in range(0, N, 4):
        for j in range(1, STEPS - 1):
            p = rings[j][i]
            q = rings[j - 1][i]
            seg = p - q
            d = seg.normalized()
            c = (p + q) * 0.5
            hl = seg.length * 0.5 + 0.05
            side = d.cross(Vector((0, 0, 1)))
            if side.length < 0.01:
                side = Vector((1, 0, 0))
            side = side.normalized() * 0.12
            nrm = d.cross(side).normalized() * 0.09
            vs = []
            for sa in (-1, 1):
                for sb in (-1, 1):
                    for sc_ in (-1, 1):
                        vs.append(bm.verts.new(c + d * (hl * sa) + side * sb + nrm * sc_))
            for q4 in ((0, 1, 3, 2), (4, 6, 7, 5), (0, 2, 6, 4),
                       (1, 5, 7, 3), (0, 4, 5, 1), (2, 3, 7, 6)):
                try:
                    bm.faces.new([vs[k] for k in q4])
                except ValueError:
                    pass
    objs.append(V.bm_to_object(bm, "cove_ribs", ("M_gold",)))
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
    objs.append(V.loft_rings("cove_eye", [(1.32, zc + 0.14, 24, 0), (0.6, zc + 0.3, 24, 0),
                                          (0.08, zc + 0.36, 24, 0)], "M_stone_dark",
                             cap_bottom=True, cap_top=False))
    objs.append(V.loft_rings("cove_eye_in", [(0.08, zc + 0.36, 24, 0), (0.6, zc + 0.3, 24, 0),
                                             (1.32, zc + 0.14, 24, 0)], "M_stone_dark",
                             cap_bottom=False, cap_top=False))
    sbm = _bmesh.new()
    srng = random.Random(11)
    for _ in range(22):
        a = srng.uniform(0, math.tau)
        rr = srng.uniform(0.08, 1.12)
        sx, sy = rr * math.cos(a), rr * math.sin(a)
        sz = zc + 0.14 + (1.0 - rr / 1.32) * 0.2 - 0.015
        s = srng.uniform(0.022, 0.045)
        V.add_box(sbm, (sx - s, sy - s, sz - s), (sx + s, sy + s, sz + s))
    objs.append(V.bm_to_object(sbm, "cove_stars", ("M_flame",)))
    # no separate drop chain: the dome-variant chandelier carries ONE
    # unbroken rope from its ring to this crown
    return objs, {"size": [20.0, 16.0, RISE + 0.4], "origin": "rim-center"}


def chandelier_gilt(chain_top=3.6):
    """Hanging gold chandelier, GRAND: two gilt tiers of candles, curtain
    chains between the rims, a pendant drop below, and ONE unbroken iron
    chain running all the way up into the vault, crowned with a gilt boss
    where it meets the ceiling. chain_top picks the ceiling: 3.6 reaches
    the flat coffer lids; the dome variants run 6.3 / 8.3 so the great
    ring hangs FROM the crown of its dome, visibly on the rope. Origin at
    the great ring's centre."""
    objs = []
    n = 12
    ring = V.loft_rings("chand_ring", [(1.3, -0.08, n, 0), (1.38, 0.0, n, 0),
                                       (1.3, 0.08, n, 0)], "M_gild")
    objs.append(ring)
    ring2 = V.loft_rings("chand_ring2", [(0.72, 0.9, n, 0), (0.8, 0.98, n, 0),
                                         (0.72, 1.06, n, 0)], "M_gild")
    objs.append(ring2)
    bm = bmesh.new()
    # the long chain to the vault (top reaches +chain_top over the ring)
    V.add_box(bm, (-0.035, -0.035, 1.0), (0.035, 0.035, chain_top))
    # curtain chains: upper rim down to the great ring
    for i in range(6):
        a = math.tau * i / 6
        x0, y0 = math.cos(a) * 0.76, math.sin(a) * 0.76
        x1, y1 = math.cos(a) * 1.3, math.sin(a) * 1.3
        for t in (0.0, 0.5, 1.0):
            cx, cy = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            cz = 0.94 - 0.94 * t
            V.add_box(bm, (cx - 0.015, cy - 0.015, cz - 0.18), (cx + 0.015, cy + 0.015, cz + 0.18))
    # the pendant drop under the great ring
    V.add_box(bm, (-0.03, -0.03, -0.55), (0.03, 0.03, 0.0))
    objs.append(V.bm_to_object(bm, "chand_chain", ("M_iron",)))
    drop = V.loft_rings("chand_drop", [(0.02, -0.55, 8, 0), (0.11, -0.42, 8, 0),
                                       (0.02, -0.3, 8, 0)], "M_gild")
    objs.append(drop)
    bm = bmesh.new()
    for i in range(12):
        a = math.tau * (i + 0.5) / 12
        cx, cy = math.cos(a) * 1.2, math.sin(a) * 1.2
        V.add_box(bm, (cx - 0.04, cy - 0.04, 0.02), (cx + 0.04, cy + 0.04, 0.34))
    for i in range(7):
        a = math.tau * i / 7
        cx, cy = math.cos(a) * 0.6, math.sin(a) * 0.6
        V.add_box(bm, (cx - 0.04, cy - 0.04, 1.0), (cx + 0.04, cy + 0.04, 1.3))
    objs.append(V.bm_to_object(bm, "chand_candles", ("M_wax",)))
    for i in range(12):
        a = math.tau * (i + 0.5) / 12
        f = _pflame("chand_flame%d" % i)
        f.location = (math.cos(a) * 1.2, math.sin(a) * 1.2, 0.34)
        objs.append(f)
    for i in range(7):
        a = math.tau * i / 7
        f = _pflame("chand_flame_u%d" % i)
        f.location = (math.cos(a) * 0.6, math.sin(a) * 0.6, 1.3)
        objs.append(f)
    boss = V.loft_rings("chand_boss", [(0.16, chain_top - 0.16, 8, 0),
                                       (0.19, chain_top - 0.05, 8, 0),
                                       (0.08, chain_top + 0.02, 8, 0)], "M_gold")
    objs.append(boss)
    return objs, {"size": [2.8, 2.8, chain_top + 0.6], "origin": "center"}



def carpet_runner_8m():
    """Processional runner: deep red field, gold borders, flat and passable.
    Origin bottom-center of the run (lies along X)."""
    objs = []
    bm = bmesh.new()
    V.add_box(bm, (-4.0, -1.1, 0.008), (4.0, 1.1, 0.028))
    objs.append(V.bm_to_object(bm, "carpet_field", ("M_cloth",)))
    bm = bmesh.new()
    for sy in (-1.0, 0.94):
        V.add_box(bm, (-3.94, sy, 0.03), (3.94, sy + 0.06, 0.042))
    V.add_box(bm, (-3.94, -1.0, 0.03), (-3.88, 1.0, 0.042))
    V.add_box(bm, (3.88, -1.0, 0.03), (3.94, 1.0, 0.042))
    objs.append(V.bm_to_object(bm, "carpet_border", ("M_gild",)))
    return objs, {"size": [8, 2.2, 0.05], "origin": "bottom-center"}


def scriptorium_shelf():
    """Tall book-press for the west wing: carved case, three laden shelves.
    Origin bottom-center against a wall (back at +Y). Solid."""
    rng = random.Random(23)
    objs = []
    bm = bmesh.new()
    V.add_box(bm, (-1.2, 0.16, 0.0), (1.2, 0.24, 2.3))             # back board
    for sx in (-1.2, 1.2):
        V.add_box(bm, (sx - 0.05, -0.2, 0.0), (sx + 0.05, 0.24, 2.3))
    for z in (0.08, 0.78, 1.48, 2.18):
        V.add_box(bm, (-1.2, -0.2, z), (1.2, 0.24, z + 0.06))
    objs.append(V.bm_to_object(bm, "shelf_case", ("M_wood",)))
    for (mat, jitter) in (("M_leather", 0), ("M_cloth", 1)):
        bm = bmesh.new()
        r2 = random.Random(31 + jitter)
        for z in (0.14, 0.84, 1.54):
            x = -1.1
            while x < 1.0:
                w = r2.uniform(0.08, 0.16)
                h = r2.uniform(0.4, 0.58)
                if r2.random() < 0.5:
                    V.add_box(bm, (x, -0.12, z), (x + w, 0.2, z + h))
                x += w + 0.015
        objs.append(V.bm_to_object(bm, "books_%d" % jitter, (mat,)))
    return objs, {"size": [2.5, 0.5, 2.3], "origin": "bottom-center"}


BUILDERS = {
    "palace_floor_4x4": palace_floor_4x4,
    "banquet_table_6m": banquet_table_6m,
    "banquet_bench_6m": banquet_bench_6m,
    "chandelier_gilt": chandelier_gilt,
    "palace_dome_12m": palace_dome_12m,
    "palace_cove_dome": palace_cove_dome,
    "chandelier_dome_low": lambda: chandelier_gilt(6.3),
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
