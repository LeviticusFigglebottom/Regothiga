"""Ambient decor kit — the liveliness pass. Most pieces come in PAIRS
(glory form / ruin form) meant to occupy the SAME spot in both layers, so
the transformation reads as one world remembered two ways:

  candle_cluster (burning votives)  <->  candle_cluster_dead (melted mass)
  garden_bed (blooming)             <->  garden_bed_dead (withered)
  censer_hanging (swinging gold)    <->  censer_fallen (spilled on the floor)
  banner (bright)                   <->  banner_torn (rag on the same rod)
  statue/orans (saints standing)    <->  wax_husk (a penitent kneeling)
"""
import math
import random
import bmesh
from mathutils import Vector

import vglib as V
from kit_props import _flame, _robe


def candle_cluster(lit=True, seed=7):
    """Votive puddle: 7-9 candles of ragged heights fused in a drip mass."""
    rng = random.Random(seed)
    objs = []
    # drip base
    bm = bmesh.new()
    got = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=0.22)
    for v in got["verts"]:
        v.co.z *= 0.22
        v.co.x *= rng.uniform(0.85, 1.3)
        v.co.y *= rng.uniform(0.85, 1.3)
        if v.co.z < 0:
            v.co.z = 0
    objs.append(V.bm_to_object(bm, "drip_base", ("M_wax",)))
    n = rng.randint(7, 9)
    for i in range(n):
        a = 2 * math.pi * i / n + rng.uniform(-0.3, 0.3)
        r = rng.uniform(0.02, 0.16)
        h = rng.uniform(0.05, 0.3) if lit else rng.uniform(0.02, 0.12)
        cx, cy = r * math.cos(a), r * math.sin(a)
        c = V.loft_rings("votive", [(0.032, 0.0, 7, 0), (0.028, h * 0.85, 7, 0.2), (0.022, h, 7, 0)], "M_wax")
        c.location = (cx, cy, 0.02)
        objs.append(c)
        if lit and rng.random() < 0.85:
            f = _flame("cluster_flame", 0.022, 0.075)
            f.location = (cx, cy, h + 0.03)
            objs.append(f)
    return objs, {"size": [0.55, 0.55, 0.42], "origin": "bottom-center"}


def wax_husk(seed=13):
    """A penitent that never rose: kneeling melted figure, dead wick head.
    Place in ruin where a saint stands in glory."""
    rng = random.Random(seed)
    objs = []
    body = _robe("husk", 1.02, 0.34, hood=True, mat="M_wax")
    me = body.data
    for v in me.vertices:
        v.co.z *= 0.92
        w = V.value_noise(v.co * 2.4 + Vector((3, 1, 4)))
        v.co.x += (w - 0.5) * 0.16 * (0.2 + v.co.z)
        v.co.y += (V.value_noise(v.co * 2.0) - 0.5) * 0.12
        if v.co.z > 0.7:
            v.co.y += 0.16   # bowed head
    objs.append(body)
    for i in range(6):
        a = rng.uniform(0, 2 * math.pi)
        drip = V.loft_rings("drip", [(0.03, 0.14, 6, 0), (0.012, 0.0, 6, 0)], "M_wax")
        drip.location = (0.4 * math.cos(a), 0.4 * math.sin(a), 0)
        objs.append(drip)
    return objs, {"size": [0.9, 0.9, 1.1], "origin": "bottom-center"}


def banner_torn():
    """The same banner rod, but the cloth hangs in rags."""
    bm = bmesh.new()
    w, h = 0.85, 2.3
    nx, nz = 6, 14
    rng = random.Random(19)
    grid = {}
    # ragged bottom: per-column survival length
    keep = [rng.uniform(0.25, 0.7) for _ in range(nx + 1)]
    for i in range(nx + 1):
        for j in range(nz + 1):
            x = -w / 2 + w * i / nx
            t = j / nz
            z = -h * t
            y = 0.07 * math.sin(j * 0.9 + i) * t
            grid[(i, j)] = (x, y, z, t)
    verts = {}
    for i in range(nx):
        for j in range(nz):
            lim = min(keep[i], keep[i + 1])
            if j / nz > lim:
                continue
            for (ii, jj) in ((i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1)):
                if (ii, jj) not in verts:
                    x, y, z, t = grid[(ii, jj)]
                    verts[(ii, jj)] = bm.verts.new((x, y, z))
            try:
                bm.faces.new((verts[(i, j)], verts[(i + 1, j)], verts[(i + 1, j + 1)], verts[(i, j + 1)]))
            except ValueError:
                pass
    bmesh.ops.solidify(bm, geom=list(bm.faces) + list(bm.verts) + list(bm.edges), thickness=0.012)
    cloth = V.bm_to_object(bm, "rag", ("M_cloth",))
    cloth.location = (0, 0, 2.5)
    rod = V.sweep_profile("rod", [(-w / 2 - 0.12, 0, 2.52), (w / 2 + 0.12, 0, 2.52)],
                          V.circle_profile(0.02, 6), "M_iron")
    return [cloth, rod], {"size": [1.1, 0.3, 2.6], "origin": "top-center"}


def garden_bed(alive=True, seed=23):
    """Stone-curbed garth bed: blooming in glory, withered twigs in ruin."""
    rng = random.Random(seed)
    objs = []
    bm = bmesh.new()
    for (x0, x1) in ((-1.1, 1.1),):
        V.add_box(bm, (-1.1, -0.7, 0), (1.1, -0.56, 0.22))
        V.add_box(bm, (-1.1, 0.56, 0), (1.1, 0.7, 0.22))
        V.add_box(bm, (-1.1, -0.7, 0), (-0.96, 0.7, 0.22))
        V.add_box(bm, (0.96, -0.7, 0), (1.1, 0.7, 0.22))
        V.add_box(bm, (-1.0, -0.6, 0), (1.0, 0.6, 0.13))   # soil
    objs.append(V.bm_to_object(bm, "bed_curb", ("M_stone_dark",)))
    bm2 = bmesh.new()
    col_layer = []
    if alive:
        # leaf tufts + flower specks as vertex-colored fans
        for i in range(26):
            cx = rng.uniform(-0.85, 0.85)
            cy = rng.uniform(-0.45, 0.45)
            hh = rng.uniform(0.12, 0.3)
            green = (rng.uniform(0.12, 0.2), rng.uniform(0.3, 0.45), rng.uniform(0.12, 0.2))
            for k in range(3):
                a = rng.uniform(0, 2 * math.pi)
                p0 = bm2.verts.new((cx, cy, 0.12))
                p1 = bm2.verts.new((cx + 0.05 * math.cos(a), cy + 0.05 * math.sin(a), 0.12 + hh))
                p2 = bm2.verts.new((cx + 0.11 * math.cos(a + 0.5), cy + 0.11 * math.sin(a + 0.5), 0.12 + hh * 0.55))
                f = bm2.faces.new((p0, p1, p2))
                col_layer.append((f, green))
            if rng.random() < 0.6:
                fl = rng.choice([(0.9, 0.85, 0.4), (0.85, 0.5, 0.6), (0.9, 0.9, 0.85), (0.6, 0.5, 0.85)])
                q = bmesh.ops.create_icosphere(bm2, subdivisions=0, radius=0.035)
                for v in q["verts"]:
                    v.co += Vector((cx, cy, 0.12 + hh + 0.02))
                for face in bm2.faces[-len(q["verts"]):] if False else []:
                    pass
                # color the last created faces
                for f in bm2.faces:
                    if f.material_index == 0 and not any(f is ff for ff, _ in col_layer) and all((v.co - Vector((cx, cy, 0.12 + hh + 0.02))).length < 0.08 for v in f.verts):
                        col_layer.append((f, fl))
    else:
        for i in range(14):
            cx = rng.uniform(-0.85, 0.85)
            cy = rng.uniform(-0.45, 0.45)
            hh = rng.uniform(0.1, 0.34)
            a = rng.uniform(0, 2 * math.pi)
            p0 = bm2.verts.new((cx, cy, 0.12))
            p1 = bm2.verts.new((cx + 0.16 * math.cos(a), cy + 0.16 * math.sin(a), 0.12 + hh))
            p2 = bm2.verts.new((cx + 0.02 * math.cos(a), cy + 0.02 * math.sin(a), 0.12 + hh * 0.5))
            f = bm2.faces.new((p0, p1, p2))
            col_layer.append((f, (0.16, 0.12, 0.09)))
    mesh = __import__("bpy").data.meshes.new("growth")
    bm2.normal_update()
    bm2.to_mesh(mesh)
    bm2.free()
    attr = mesh.color_attributes.new(name="Col", type='BYTE_COLOR', domain='CORNER')
    mesh.color_attributes.active_color = attr
    # paint by nearest recorded face color via polygon order
    cols = [c for _, c in col_layer]
    for pi, poly in enumerate(mesh.polygons):
        c = cols[pi % len(cols)] if cols else (0.2, 0.3, 0.2)
        for li in poly.loop_indices:
            attr.data[li].color = (c[0], c[1], c[2], 1.0)
    growth = V.new_object("growth", mesh)
    growth.data.materials.append(V.material("M_foliage"))
    return objs + [growth], {"size": [2.2, 1.4, 0.5], "origin": "bottom-center"}


def censer_hanging():
    """Gold censer on a chain from the vault. Glory walks."""
    objs = []
    for i in range(6):
        link = V.loft_rings("link", [(0.028, -i * 0.14, 6, 0), (0.02, -i * 0.14 - 0.1, 6, 0)], "M_iron")
        objs.append(link)
    cens = V.loft_rings("censer", [(0.02, -0.9, 8, 0), (0.09, -1.0, 8, 0), (0.11, -1.12, 8, 0),
                                   (0.07, -1.22, 8, 0), (0.02, -1.26, 8, 0)], "M_gold")
    objs.append(cens)
    f = _flame("censer_flame", 0.03, 0.08)
    f.location = (0, 0, -0.92)
    objs.append(f)
    return objs, {"size": [0.3, 0.3, 1.3], "origin": "hang-point"}


def censer_fallen(seed=29):
    """The same censer, spilled on the flags with its chain."""
    rng = random.Random(seed)
    objs = []
    cens = V.loft_rings("censer_f", [(0.02, 0.0, 8, 0), (0.09, 0.1, 8, 0), (0.11, 0.22, 8, 0),
                                     (0.07, 0.32, 8, 0), (0.02, 0.36, 8, 0)], "M_gold")
    cens.rotation_euler = (0, math.radians(96), rng.uniform(0, 6))
    cens.location = (0, 0, 0.09)
    objs.append(cens)
    pts = [(0.15, 0, 0.02)]
    for i in range(7):
        pts.append((0.15 + (i + 1) * 0.12, rng.uniform(-0.1, 0.1), 0.02))
    objs.append(V.sweep_profile("chain_f", pts, V.circle_profile(0.018, 5), "M_iron"))
    return objs, {"size": [1.2, 0.4, 0.4], "origin": "bottom-center"}


def ivy_sheet(seed=31):
    """Creeper sheet for ruin walls: drooping stems studded with leaf quads.
    Mount against a wall face (leaves spread in local XZ, wall at y=0)."""
    rng = random.Random(seed)
    bm = bmesh.new()
    col_entries = []
    for s in range(6):
        x0 = rng.uniform(-1.5, 1.5)
        top = rng.uniform(2.2, 3.4)
        length = rng.uniform(1.2, 2.6)
        sway = rng.uniform(-0.35, 0.35)
        n = int(length / 0.16)
        for i in range(n):
            t = i / max(n - 1, 1)
            x = x0 + sway * t * t + math.sin(t * 9 + s) * 0.06
            z = top - length * t
            size = rng.uniform(0.07, 0.13) * (1.0 - 0.3 * t)
            a = rng.uniform(0, 2 * math.pi)
            p0 = bm.verts.new((x, -0.02 - 0.03 * rng.random(), z))
            p1 = bm.verts.new((x + size * math.cos(a), -0.05, z + size * math.sin(a)))
            p2 = bm.verts.new((x + size * math.cos(a + 2.1), -0.05, z + size * math.sin(a + 2.1)))
            f = bm.faces.new((p0, p1, p2))
            g = rng.uniform(0.7, 1.0)
            col_entries.append((0.14 * g, 0.24 * g, 0.10 * g))
    mesh = __import__("bpy").data.meshes.new("ivy")
    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()
    attr = mesh.color_attributes.new(name="Col", type='BYTE_COLOR', domain='CORNER')
    mesh.color_attributes.active_color = attr
    for pi, poly in enumerate(mesh.polygons):
        c = col_entries[pi % len(col_entries)]
        for li in poly.loop_indices:
            attr.data[li].color = (c[0], c[1], c[2], 1.0)
    obj = V.new_object("ivy", mesh)
    obj.data.materials.append(V.material("M_foliage"))
    return [obj], {"size": [3.4, 0.15, 3.5], "origin": "wall-base"}


def book_stack(seed=37):
    rng = random.Random(seed)
    bm = bmesh.new()
    z = 0.0
    for i in range(rng.randint(4, 6)):
        w = rng.uniform(0.16, 0.24)
        d = rng.uniform(0.12, 0.18)
        h = rng.uniform(0.03, 0.055)
        a = rng.uniform(-0.4, 0.4)
        ca, sa = math.cos(a), math.sin(a)
        cx, cy = rng.uniform(-0.02, 0.02), rng.uniform(-0.02, 0.02)
        corners = []
        for (dx, dy) in ((-w, -d), (w, -d), (w, d), (-w, d)):
            corners.append((cx + dx * ca - dy * sa, cy + dx * sa + dy * ca))
        vs_b = [bm.verts.new((x, y, z)) for (x, y) in corners]
        vs_t = [bm.verts.new((x, y, z + h)) for (x, y) in corners]
        bm.faces.new(reversed(vs_b))
        bm.faces.new(vs_t)
        for k in range(4):
            bm.faces.new((vs_b[k], vs_b[(k + 1) % 4], vs_t[(k + 1) % 4], vs_t[k]))
        z += h
    obj = V.bm_to_object(bm, "books", ("M_leather",))
    return [obj], {"size": [0.5, 0.4, 0.35], "origin": "bottom-center"}


def scroll_pile(seed=41):
    rng = random.Random(seed)
    objs = []
    for i in range(5):
        a = rng.uniform(0, math.pi)
        sc = V.loft_rings("scroll", [(0.03, -0.16, 7, 0), (0.032, 0.16, 7, 0)], "M_wax")
        sc.rotation_euler = (math.radians(90), 0, a)
        sc.location = (rng.uniform(-0.1, 0.1), rng.uniform(-0.1, 0.1), 0.035 + (0.05 if i > 2 else 0))
        objs.append(sc)
    return objs, {"size": [0.5, 0.5, 0.15], "origin": "bottom-center"}


BUILDERS = {
    "candle_cluster": lambda: candle_cluster(True),
    "candle_cluster_dead": lambda: candle_cluster(False, seed=8),
    "wax_husk": wax_husk,
    "banner_torn": banner_torn,
    "garden_bed": lambda: garden_bed(True),
    "garden_bed_dead": lambda: garden_bed(False, seed=24),
    "censer_hanging": censer_hanging,
    "censer_fallen": censer_fallen,
    "ivy_sheet_a": lambda: ivy_sheet(31),
    "ivy_sheet_b": lambda: ivy_sheet(35),
    "book_stack": book_stack,
    "scroll_pile": scroll_pile,
}
