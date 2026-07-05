"""Architecture kit generators: floors, walls, arcades, vaults, windows,
portals, buttresses, cornices — the bones of the Gray Cloister.

Every builder returns (objects, manifest_entry). Module grid = 4 m.
Origin convention: bottom-center of the piece's snap face unless noted.
"""
import math
import random
import bmesh
from mathutils import Vector

import vglib as V


# ------------------------------------------------------------------ floors

def floor_4x4():
    """4x4 m slab floor, per-slab jitter. Origin: center of tile, top at z=0.
    Slabs sit slightly below z=0 so props at y=0 rest on them cleanly."""
    bm = bmesh.new()
    rng = random.Random(11)
    n = 4
    s = 4.0 / n
    for i in range(n):
        for j in range(n):
            x0, y0 = -2 + i * s, -2 + j * s
            drop = rng.uniform(0.008, 0.03)
            g = 0.015
            V.add_box(bm, (x0 + g, y0 + g, -0.22), (x0 + s - g, y0 + s - g, -drop))
    obj = V.bm_to_object(bm, "floor_4x4", ("M_stone_dark",))
    return [obj], {"size": [4, 0.25, 4], "origin": "top-center"}


def _block_wall(bm, x0, x1, z0, z1, y_front, depth, rng, block_w=1.0, block_h=0.5):
    """Running-bond block relief between x0..x1, z0..z1 on a wall face."""
    rows = max(1, round((z1 - z0) / block_h))
    bh = (z1 - z0) / rows
    for r in range(rows):
        zb0 = z0 + r * bh
        offset = (block_w / 2) if r % 2 else 0.0
        x = x0 - offset
        while x < x1 - 0.01:
            bw = min(block_w, x1 - x)
            xs = max(x, x0)
            proud = rng.uniform(0.02, 0.055)
            g = 0.012
            V.add_box(bm, (xs + g, y_front - proud, zb0 + g),
                      (xs + bw - g, y_front + depth, zb0 + bh - g))
            x += block_w


def wall_4x4():
    """Solid wall 4 m wide, 4 m tall, ~0.45 thick, block relief both faces.
    Origin: bottom-center of the wall run (thickness centered on Y=0)."""
    bm = bmesh.new()
    rng = random.Random(7)
    V.add_box(bm, (-2, -0.14, 0), (2, 0.14, 4.0))          # core slab
    _block_wall(bm, -2, 2, 0.0, 4.0, -0.16, 0.02, rng)      # front blocks
    rng2 = random.Random(8)
    # back face blocks (mirror): build then flip by using positive Y proud
    rows = 8
    for r in range(rows):
        zb0 = r * 0.5
        offset = 0.5 if r % 2 else 0.0
        x = -2 - offset
        while x < 2 - 0.01:
            bw = min(1.0, 2 - max(x, -2))
            xs = max(x, -2)
            proud = rng2.uniform(0.02, 0.055)
            g = 0.012
            V.add_box(bm, (xs + g, -0.02, zb0 + g), (xs + bw - g, 0.16 + proud, zb0 + 0.5 - g))
            x += 1.0
    obj = V.bm_to_object(bm, "wall_4x4", ("M_stone",))
    return [obj], {"size": [4, 0.5, 4], "origin": "bottom-center"}


def wall_low_4m():
    """Parapet wall 1.0 m tall with coping, for garth edges. Origin bottom-center."""
    bm = bmesh.new()
    V.add_box(bm, (-2, -0.18, 0), (2, 0.18, 0.86))
    # coping: slightly wider cap with peaked top
    c0, c1 = -0.24, 0.24
    zs, zp = 0.86, 1.04
    vs = []
    for x in (-2, 2):
        a = bm.verts.new((x, c0, zs)); b = bm.verts.new((x, c1, zs))
        m = bm.verts.new((x, 0.0, zp))
        vs.append((a, b, m))
    (a0, b0, m0), (a1, b1, m1) = vs
    bm.faces.new((a0, m0, m1, a1))
    bm.faces.new((m0, b0, b1, m1))
    bm.faces.new((a0, a1, b1, b0))  # underside of coping overhang
    bm.faces.new((a0, b0, m0))
    bm.faces.new((b1, a1, m1))
    obj = V.bm_to_object(bm, "wall_low_4m", ("M_stone",))
    return [obj], {"size": [4, 0.5, 1.05], "origin": "bottom-center"}


# ------------------------------------------------------------------ arcade

def arcade_4m():
    """Cloister arcade module: parapet, twin colonnettes, pointed arch.
    Open span faces the garth. Origin: bottom-center of the run."""
    objs = []
    # arch panel: opening 2.2 wide springing at 1.6 -> apex ~3.23 (below vault)
    panel = V.wall_panel_with_arch("arcade_panel", 4.0, 4.0, 0.34, 2.2, 1.6,
                                   sharpness=0.8, segments=12)
    objs.append(panel)
    # parapet under the opening (arcades are windows onto the garth;
    # passage is at the portals)
    bm = bmesh.new()
    V.add_box(bm, (-1.1, -0.15, 0), (1.1, 0.15, 0.9))
    objs.append(V.bm_to_object(bm, "arcade_parapet", ("M_stone",)))
    # colonnettes at the jambs
    for sx in (-1.1, 1.1):
        col = _colonnette(0.14, 1.72)
        col.location = (sx + (0.17 if sx < 0 else -0.17), 0, 0.86)
        objs.append(col)
    entry = {"size": [4, 0.5, 4], "origin": "bottom-center"}
    return objs, entry


def _colonnette(r, h):
    rings = []
    n = 8
    rings.append((r * 1.5, 0.0, n, 0))
    rings.append((r * 1.45, 0.06, n, 0))
    rings.append((r * 1.05, 0.12, n, 0))
    rings.append((r, 0.2, n, 0))
    rings.append((r * 0.92, h * 0.7, n, 0))
    rings.append((r * 0.9, h - 0.16, n, 0))
    rings.append((r * 1.3, h - 0.07, n, 0))
    rings.append((r * 1.42, h, n, 0))
    return V.loft_rings("colonnette", rings, "M_stone_trim")


def column_4m():
    """Freestanding compound pier for cloister corners. Origin: base center."""
    objs = []
    n = 8
    rings = [(0.46, 0, n, 0), (0.44, 0.10, n, 0), (0.34, 0.22, n, 0),
             (0.30, 0.3, n, 0), (0.28, 3.0, n, 0), (0.30, 3.55, n, 0),
             (0.42, 3.75, n, 0), (0.46, 3.98, n, 0)]
    objs.append(V.loft_rings("pier", rings, "M_stone_trim"))
    # four attached shafts
    for a in range(4):
        ang = a * math.pi / 2 + math.pi / 4
        sh = _colonnette(0.09, 3.4)
        sh.location = (0.30 * math.cos(ang), 0.30 * math.sin(ang), 0.16)
        objs.append(sh)
    return objs, {"size": [1, 1, 4], "origin": "bottom-center"}


# ------------------------------------------------------------------ vaults

def _arch_y(pts, x):
    """Interpolate arch height at |x| from a pointed_arch polyline."""
    ax = abs(x)
    best = 0.0
    for i in range(len(pts) - 1):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        if x0 <= -ax <= x1 or x1 <= -ax <= x0 or x0 <= ax <= x1:
            # use symmetric half: fold to negative side
            pass
    # simpler: pts are symmetric; sample by folding to left half
    half = pts[:len(pts) // 2 + 1]
    xq = -ax
    for i in range(len(half) - 1):
        (x0, y0), (x1, y1) = half[i], half[i + 1]
        if (x0 <= xq <= x1) or (x1 <= xq <= x0):
            t = 0.0 if x1 == x0 else (xq - x0) / (x1 - x0)
            return y0 + (y1 - y0) * t
    return half[-1][1] if ax < 0.01 else 0.0


def vault_bay_4x4():
    """Quadripartite-ish rib vault bay over a 4x4 m cell. The web is the
    surface z = spring + min(arch(x), arch(z)); ribs sweep the diagonals and
    edges; a boss caps the crown. Origin: bay center at spring height z=0
    (place at wall spring height)."""
    spring = 0.0
    arch = V.pointed_arch(4.0, 0.55, 16, 0.0)
    apex = max(p[1] for p in arch)
    grid = 14
    bm = bmesh.new()
    verts = {}
    for i in range(grid + 1):
        for j in range(grid + 1):
            x = (-2 + 4 * i / grid) * 1.012
            z = (-2 + 4 * j / grid) * 1.012
            h = spring + min(_arch_y(arch, x), _arch_y(arch, z))
            verts[(i, j)] = bm.verts.new((x, z, h))
    for i in range(grid):
        for j in range(grid):
            bm.faces.new((verts[(i, j)], verts[(i, j + 1)],
                          verts[(i + 1, j + 1)], verts[(i + 1, j)]))
    web = V.bm_to_object(bm, "vault_web", ("M_stone",))
    objs = [web]

    prof = V.chamfer_rect_profile(0.16, 0.22, 0.05)
    # diagonal ribs
    for sgn in (1, -1):
        path = []
        for k in range(25):
            t = -2 + 4 * k / 24
            path.append((t, sgn * t, spring + _arch_y(arch, t) - 0.02))
        objs.append(V.sweep_profile("rib_diag", path, prof, "M_stone_trim",
                                    up_hint=Vector((0, 0, 1))))
    # transverse/wall ribs at the four edges
    for edge in range(4):
        path = []
        for k in range(25):
            t = -2 + 4 * k / 24
            h = spring + _arch_y(arch, t) - 0.02
            if edge == 0: path.append((t, -2 + 0.08, h))
            elif edge == 1: path.append((t, 2 - 0.08, h))
            elif edge == 2: path.append((-2 + 0.08, t, h))
            else: path.append((2 - 0.08, t, h))
        objs.append(V.sweep_profile("rib_edge", path, prof, "M_stone_trim",
                                    up_hint=Vector((0, 0, 1))))
    # boss at the crown
    boss = V.loft_rings("boss", [(0.02, apex - 0.3, 8, 0), (0.16, apex - 0.14, 8, 0),
                                 (0.13, apex + 0.02, 8, 0.3)], "M_stone_trim")
    objs.append(boss)
    return objs, {"size": [4, 4, apex + 0.1], "origin": "spring-center", "apex": apex}


# ------------------------------------------------------------------ windows

def _lancet_outline(w, sill, spring, apex_sharp, segs=10):
    """Closed outline polygon of a lancet opening (counter-clockwise)."""
    arch = V.pointed_arch(w, apex_sharp, segs, spring)
    pts = [(w / 2, sill)] + list(reversed(arch)) + [(-w / 2, sill)]
    return pts


def window_lancet_4m():
    """Wall panel 4x4 with a lancet window opening. Glass is a separate piece."""
    panel = V.wall_panel_with_arch("window_wall", 4.0, 4.0, 0.4, 1.5, 2.35,
                                   sharpness=1.15, segments=10, sill_h=1.15)
    # sill ledge
    bm = bmesh.new()
    V.add_box(bm, (-0.95, -0.3, 0.98), (0.95, 0.3, 1.15))
    sill = V.bm_to_object(bm, "window_sill", ("M_stone_trim",))
    return [panel, sill], {"size": [4, 0.6, 4], "origin": "bottom-center",
                           "glass": "glass_lancet", "glass_pos": [0, 0, 0]}


def _clip_convex(poly, clip):
    """Sutherland–Hodgman: clip polygon against convex clip polygon (CCW)."""
    out = poly
    n = len(clip)
    for i in range(n):
        a, b = Vector(clip[i]), Vector(clip[(i + 1) % n])
        edge = b - a
        res = []
        for j in range(len(out)):
            p, q = Vector(out[j]), Vector(out[(j + 1) % len(out)])
            side_p = edge.x * (p.y - a.y) - edge.y * (p.x - a.x)
            side_q = edge.x * (q.y - a.y) - edge.y * (q.x - a.x)
            if side_p >= 0:
                res.append(tuple(p))
            if (side_p >= 0) != (side_q >= 0) and abs(side_q - side_p) > 1e-9:
                t = side_p / (side_p - side_q)
                m = p + (q - p) * t
                res.append(tuple(m))
        out = res
        if not out:
            break
    return out


GLASS_PALETTE = {
    "pale":   [(0.38, 0.52, 0.50), (0.42, 0.52, 0.40), (0.48, 0.50, 0.36)],
    "blue":   [(0.06, 0.13, 0.48), (0.05, 0.18, 0.55)],
    "ruby":   [(0.46, 0.04, 0.07), (0.55, 0.06, 0.11)],
    "gold":   [(0.72, 0.46, 0.08), (0.78, 0.55, 0.12)],
    "violet": [(0.26, 0.07, 0.40)],
    "green":  [(0.06, 0.33, 0.15)],
}


def _mosaic(outline, pitch, rng, center, medallion_r):
    """Diamond-quarry mosaic clipped to a convex lancet outline.
    Returns list of (poly, color)."""
    xs = [p[0] for p in outline]; ys = [p[1] for p in outline]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    shards = []
    row = 0
    y = y0 - pitch
    while y < y1 + pitch:
        xoff = pitch / 2 if row % 2 else 0.0
        x = x0 - pitch + xoff
        while x < x1 + pitch:
            diamond = [(x, y - pitch * 0.7), (x + pitch / 2, y),
                       (x, y + pitch * 0.7), (x - pitch / 2, y)]
            clipped = _clip_convex(diamond, outline)
            if len(clipped) >= 3:
                cx = sum(p[0] for p in clipped) / len(clipped)
                cy = sum(p[1] for p in clipped) / len(clipped)
                d_med = math.hypot(cx - center[0], cy - center[1])
                # choose family: medallion core, border band, or pale field
                on_border = len(clipped) != 4  # got clipped => touches outline
                if d_med < medallion_r:
                    fam = "gold" if d_med < medallion_r * 0.5 else "ruby"
                elif on_border:
                    fam = "blue" if (row % 2 == 0) else "violet"
                else:
                    fam = "pale" if rng.random() > 0.16 else rng.choice(["blue", "green", "ruby", "gold"])
                col = rng.choice(GLASS_PALETTE[fam])
                shards.append((clipped, col))
            x += pitch
        y += pitch * 0.7
        row += 1
    return shards


def _glass_from_shards(name, shards, keep=1.0, rng=None, thickness=0.02):
    bm = bmesh.new()
    face_cols = []  # color per created face, in creation order
    for poly, col in shards:
        if rng is not None and rng.random() > keep:
            continue
        # shrink toward centroid to expose lead lines
        cx = sum(p[0] for p in poly) / len(poly)
        cy = sum(p[1] for p in poly) / len(poly)
        front = []
        for (px, py) in poly:
            sx = cx + (px - cx) * 0.86
            sy = cy + (py - cy) * 0.86
            front.append(bm.verts.new((sx, -thickness / 2, sy)))
        try:
            bm.faces.new(front)
            face_cols.append(col)
        except ValueError:
            continue
        back = [bm.verts.new((v.co.x, thickness / 2, v.co.z)) for v in front]
        try:
            bm.faces.new(list(reversed(back)))
            face_cols.append(col)
        except ValueError:
            pass
    mesh = bmesh_to_mesh(bm, name)
    # paint per-polygon jewel colors directly on the mesh attribute
    attr = mesh.color_attributes.new(name="Col", type='BYTE_COLOR', domain='CORNER')
    mesh.color_attributes.active_color = attr
    for pi, p in enumerate(mesh.polygons):
        col = face_cols[pi] if pi < len(face_cols) else (1, 0, 1)
        for li in p.loop_indices:
            attr.data[li].color = (col[0], col[1], col[2], 1.0)
    obj = V.new_object(name, mesh)
    obj.data.materials.append(V.material("M_glass"))
    return obj


def bmesh_to_mesh(bm, name):
    import bpy
    mesh = bpy.data.meshes.new(name)
    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()
    return mesh


def glass_lancet():
    """Intact stained-glass lancet: diamond quarries + medallion + backing lead
    sheet. Origin matches window_lancet_4m panel (plug into same transform)."""
    rng = random.Random(23)
    outline = _lancet_outline(1.44, 1.18, 2.35, 1.15, 10)
    shards = _mosaic(outline, 0.20, rng, (0.0, 2.35), 0.42)
    glass = _glass_from_shards("glass_lancet", shards)
    # lead backing: solid lancet sheet on the EXTERIOR side (blender -Y ->
    # local +Z after import), so the interior view sees the jewel shards
    bm = bmesh.new()
    verts = [bm.verts.new((x, -0.035, y)) for (x, y) in reversed(outline)]
    bm.faces.new(verts)
    back = V.new_object("glass_backing", bmesh_to_mesh(bm, "glass_backing"))
    back.data.materials.append(V.material("M_iron"))
    return [glass, back], {"size": [1.5, 0.1, 4], "origin": "bottom-center"}


def glass_lancet_broken():
    """Ruin variant: a few teeth of glass left, no backing — sky shows through."""
    rng = random.Random(29)
    outline = _lancet_outline(1.44, 1.18, 2.35, 1.15, 10)
    shards = _mosaic(outline, 0.20, rng, (0.0, 2.35), 0.42)
    # keep mostly border shards (they cling to the frame)
    kept = []
    for poly, col in shards:
        edge_touch = len(poly) != 4
        p = 0.55 if edge_touch else 0.06
        if rng.random() < p:
            kept.append((poly, col))
    glass = _glass_from_shards("glass_lancet_broken", kept)
    return [glass], {"size": [1.5, 0.1, 4], "origin": "bottom-center"}


# ------------------------------------------------------------------ portals

def portal_4m():
    """Doorway wall: 4x4 panel with a 1.9-wide arch opening and two nested
    archivolt sweeps. Origin bottom-center; passage along Y."""
    objs = []
    panel = V.wall_panel_with_arch("portal_wall", 4.0, 4.0, 0.5, 1.9, 2.1,
                                   sharpness=1.1, segments=12)
    objs.append(panel)
    arch = V.pointed_arch(1.9, 1.1, 12, 2.1)
    for k, (scale, depth) in enumerate(((1.12, 0.30), (1.26, 0.16))):
        path = []
        for (x, y) in arch:
            path.append((x * scale, 0.0, y + (scale - 1) * 0.4))
        prof = V.chamfer_rect_profile(0.16 + k * 0.04, depth, 0.045)
        objs.append(V.sweep_profile(f"archivolt{k}", path, prof, "M_stone_trim",
                                    up_hint=Vector((0, 0, 1))))
    # jamb columns
    for sx in (-1.15, 1.15):
        c = _colonnette(0.12, 2.1)
        c.location = (sx, 0, 0)
        objs.append(c)
    return objs, {"size": [4, 0.6, 4], "origin": "bottom-center", "opening": [1.9, 2.9]}


# ------------------------------------------------------------------ misc

def cornice_4m():
    prof = [(-0.0, 0.0), (0.16, 0.02), (0.2, 0.10), (0.10, 0.16), (0.16, 0.26), (0.0, 0.3)]
    path = [(-2, 0, 0), (2, 0, 0)]
    obj = V.sweep_profile("cornice_4m", path, prof, "M_stone_trim",
                          up_hint=Vector((0, 0, 1)))
    return [obj], {"size": [4, 0.3, 0.3], "origin": "bottom-center"}


def buttress():
    """Stepped buttress pier, ~4 m tall. Origin: bottom-center against wall
    (wall face at y=0, buttress extends -Y)."""
    bm = bmesh.new()
    V.add_box(bm, (-0.55, -1.15, 0.0), (0.55, 0.0, 1.6))
    V.add_box(bm, (-0.45, -0.95, 1.6), (0.45, 0.0, 3.0))
    V.add_box(bm, (-0.38, -0.7, 3.0), (0.38, 0.0, 3.98))
    obj = V.bm_to_object(bm, "buttress_body", ("M_stone",))
    # sloped weatherings: wedges at each step
    bm2 = bmesh.new()
    for (w, y_out, z0, rise) in ((0.45, -0.95, 1.6, 0.34), (0.38, -0.7, 3.0, 0.3), (0.34, -0.62, 3.98, 0.5)):
        a = bm2.verts.new((-w, y_out, z0)); b = bm2.verts.new((w, y_out, z0))
        c = bm2.verts.new((w, 0.0, z0 + rise)); d = bm2.verts.new((-w, 0.0, z0 + rise))
        e = bm2.verts.new((-w, 0.0, z0)); f = bm2.verts.new((w, 0.0, z0))
        bm2.faces.new((a, b, c, d))
        bm2.faces.new((a, d, e))
        bm2.faces.new((b, f, c))
        bm2.faces.new((a, e, f, b))
    slopes = V.bm_to_object(bm2, "buttress_slopes", ("M_stone_trim",))
    return [obj, slopes], {"size": [1.1, 1.2, 4.4], "origin": "bottom-center"}


def column_broken():
    """Ruin: pier snapped at ~1.6 m with a jagged crown."""
    rng = random.Random(31)
    n = 8
    rings = [(0.46, 0, n, 0), (0.44, 0.10, n, 0), (0.34, 0.22, n, 0), (0.30, 0.3, n, 0)]
    top = 1.0 + rng.random() * 0.9
    rings.append((0.30, top, n, 0))
    bm = bmesh.new()
    prev = None
    for (r, z, nsides, rot) in rings:
        ring = []
        for i in range(nsides):
            a = 2 * math.pi * i / nsides + rot
            rr = r
            zz = z
            if z == top:
                rr *= rng.uniform(0.7, 1.05)
                zz += rng.uniform(-0.16, 0.3)
            ring.append(bm.verts.new((rr * math.cos(a), rr * math.sin(a), zz)))
        if prev:
            for i in range(nsides):
                bm.faces.new((prev[i], prev[(i + 1) % nsides], ring[(i + 1) % nsides], ring[i]))
        prev = ring
    bm.verts.ensure_lookup_table()
    bm.faces.new(reversed(bm.verts[:n]))
    # jagged cap fan
    import statistics
    cz = statistics.mean(v.co.z for v in prev) + 0.1
    center = bm.verts.new((0, 0, cz))
    for i in range(n):
        bm.faces.new((prev[i], prev[(i + 1) % n], center))
    obj = V.bm_to_object(bm, "column_broken", ("M_stone",))
    return [obj], {"size": [1, 1, 2.2], "origin": "bottom-center"}


def rubble(size_key):
    """Rubble scatter piles: s / m / l."""
    rng = random.Random({"s": 41, "m": 42, "l": 43}[size_key])
    count = {"s": 5, "m": 11, "l": 20}[size_key]
    spread = {"s": 0.5, "m": 1.0, "l": 1.8}[size_key]
    bm = bmesh.new()
    for i in range(count):
        r = rng.uniform(0.12, 0.38) * (1.4 if size_key == "l" else 1.0)
        cx, cy = rng.uniform(-spread, spread), rng.uniform(-spread, spread)
        cz = r * rng.uniform(0.3, 0.7)
        mat = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
        vs = mat["verts"]
        for v in vs:
            v.co.x *= rng.uniform(0.7, 1.4)
            v.co.y *= rng.uniform(0.7, 1.4)
            v.co.z *= rng.uniform(0.5, 0.9)
            v.co += Vector((cx, cy, cz))
            v.co += Vector((V.value_noise(v.co, 3.0) * 0.08,) * 3)
    obj = V.bm_to_object(bm, f"rubble_{size_key}", ("M_stone_dark",))
    return [obj], {"size": [spread * 2, spread * 2, 0.8], "origin": "bottom-center"}


def fog_gate_frame():
    """Freestanding boss-arena threshold: two piers + pointed arch with
    chevron-carved archivolt. The fog plane itself is runtime."""
    objs = []
    for sx in (-1.6, 1.6):
        bm = bmesh.new()
        V.add_box(bm, (sx - 0.35, -0.35, 0), (sx + 0.35, 0.35, 3.1))
        V.add_box(bm, (sx - 0.45, -0.45, 0), (sx + 0.45, 0.45, 0.5))
        V.add_box(bm, (sx - 0.42, -0.42, 3.1), (sx + 0.42, 0.42, 3.4))
        objs.append(V.bm_to_object(bm, "fog_pier", ("M_stone_trim",)))
    arch = V.pointed_arch(3.2, 1.0, 14, 3.25)
    path = [(x, 0, y) for (x, y) in arch]
    objs.append(V.sweep_profile("fog_arch", path, V.chamfer_rect_profile(0.5, 0.34, 0.1),
                                "M_stone_trim", up_hint=Vector((0, 0, 1))))
    return objs, {"size": [4, 1, 5.2], "origin": "bottom-center", "opening": [3.2, 3.1]}


def roof_shed_4m():
    """Lean-to roof over a cloister walk: garth-side eave at ~4.05 m rising
    to 5.5 m against the outer wall. Origin: bottom-center of the garth eave;
    slopes toward local blender +Y (away from the garth)."""
    bm = bmesh.new()
    a = bm.verts.new((-2.04, -0.35, 4.02)); b = bm.verts.new((2.04, -0.35, 4.02))
    c = bm.verts.new((2.04, 4.4, 5.52)); d = bm.verts.new((-2.04, 4.4, 5.52))
    bm.faces.new((a, b, c, d))
    bmesh.ops.solidify(bm, geom=list(bm.faces) + list(bm.verts) + list(bm.edges), thickness=0.09)
    roof = V.bm_to_object(bm, "roof_slope", ("M_roof",))
    bm2 = bmesh.new()
    V.add_box(bm2, (-2, -0.42, 3.86), (2, -0.30, 4.10))
    fascia = V.bm_to_object(bm2, "roof_fascia", ("M_wood",))
    return [roof, fascia], {"size": [4, 4.8, 5.6], "origin": "eave-center"}


def rose_window():
    """Rose window: circular stone tracery wheel with jewel-glass petals.
    ~3.8 m across; origin at the wheel hub. Place high on a wall face; the
    glass survives both states — the last light lives in it."""
    import random as _random
    rng = _random.Random(77)
    objs = []
    R = 1.9
    n = 28
    outline = [(R * math.cos(2 * math.pi * i / n), R * math.sin(2 * math.pi * i / n))
               for i in range(n)]
    shards = _mosaic(outline, 0.24, rng, (0.0, 0.0), 0.55)
    objs.append(_glass_from_shards("rose_glass", shards))
    # stone rim: two concentric sweeps
    bm = bmesh.new()
    seg = 24
    for (r0, r1) in ((R * 1.0, R * 1.14), (0.16, 0.3)):
        ring0, ring1, ring0b, ring1b = [], [], [], []
        for i in range(seg):
            a = 2 * math.pi * i / seg
            ca, sa = math.cos(a), math.sin(a)
            ring0.append(bm.verts.new((r0 * ca, -0.12, r0 * sa)))
            ring1.append(bm.verts.new((r1 * ca, -0.12, r1 * sa)))
            ring0b.append(bm.verts.new((r0 * ca, 0.12, r0 * sa)))
            ring1b.append(bm.verts.new((r1 * ca, 0.12, r1 * sa)))
        for i in range(seg):
            j = (i + 1) % seg
            bm.faces.new((ring0[i], ring0[j], ring1[j], ring1[i]))
            bm.faces.new((ring1b[i], ring1b[j], ring0b[j], ring0b[i]))
            bm.faces.new((ring1[i], ring1[j], ring1b[j], ring1b[i]))
            bm.faces.new((ring0b[i], ring0b[j], ring0[j], ring0[i]))
    # spokes
    for i in range(12):
        a = 2 * math.pi * i / 12
        ca, sa = math.cos(a), math.sin(a)
        x0, y0 = 0.26 * ca, 0.26 * sa
        x1, y1 = R * ca, R * sa
        px, py = -sa * 0.045, ca * 0.045
        quad = [(x0 + px, y0 + py), (x1 + px, y1 + py), (x1 - px, y1 - py), (x0 - px, y0 - py)]
        front = [bm.verts.new((qx, -0.09, qy)) for (qx, qy) in quad]
        backv = [bm.verts.new((qx, 0.09, qy)) for (qx, qy) in quad]
        bm.faces.new(front)
        bm.faces.new(list(reversed(backv)))
        for k in range(4):
            m = (k + 1) % 4
            bm.faces.new((front[k], front[m], backv[m], backv[k]))
    objs.append(V.bm_to_object(bm, "rose_tracery", ("M_stone_trim",)))
    return objs, {"size": [4.4, 0.3, 4.4], "origin": "hub-center"}


BUILDERS = {
    "roof_shed_4m": roof_shed_4m,
    "floor_4x4": floor_4x4,
    "wall_4x4": wall_4x4,
    "wall_low_4m": wall_low_4m,
    "arcade_4m": arcade_4m,
    "column_4m": column_4m,
    "vault_bay_4x4": vault_bay_4x4,
    "window_lancet_4m": window_lancet_4m,
    "glass_lancet": glass_lancet,
    "glass_lancet_broken": glass_lancet_broken,
    "portal_4m": portal_4m,
    "rose_window": rose_window,
    "cornice_4m": cornice_4m,
    "buttress": buttress,
    "column_broken": column_broken,
    "rubble_s": lambda: rubble("s"),
    "rubble_m": lambda: rubble("m"),
    "rubble_l": lambda: rubble("l"),
    "fog_gate_frame": fog_gate_frame,
}
