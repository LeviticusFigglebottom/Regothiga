"""vglib — shared helpers for the Vespergard gothic kit generators.

Conventions (see DECISIONS.md D-004):
  * Real-world scale, meters. Module grid = 4 m.
  * Y is Blender-up here; the glTF exporter converts to Y-up-glTF so Godot
    receives pieces upright. All transforms applied on export.
  * Origins at logical snap points (floor level, grid corner or center).
  * Vertex colors pack per-vertex masks: R = wear, G = moss/dirt zone,
    B = ambient occlusion approximation, A = 1.
  * Material names are the contract with Godot's MaterialLib: M_stone,
    M_stone_trim, M_stone_dark, M_iron, M_wood, M_glass, M_gold, M_wax,
    M_cloth, M_flame, M_bell, M_chainmail, M_plate_dark, M_brass, M_steel, etc.
"""
import math
import random
import bpy
import bmesh
from mathutils import Vector, Matrix

# ---------------------------------------------------------------- scene mgmt

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def _ensure_material(name: str, color=(0.8, 0.8, 0.8, 1.0)):
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
        mat.diffuse_color = color
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Base Color"].default_value = color
            bsdf.inputs["Roughness"].default_value = 0.9
    return mat

MATERIAL_COLORS = {
    "M_stone":        (0.72, 0.68, 0.60, 1.0),
    "M_stone_trim":   (0.78, 0.74, 0.66, 1.0),
    "M_stone_dark":   (0.45, 0.43, 0.40, 1.0),
    "M_iron":         (0.14, 0.14, 0.17, 1.0),
    "M_steel":        (0.62, 0.65, 0.70, 1.0),
    "M_plate_dark":   (0.24, 0.26, 0.31, 1.0),
    "M_chainmail":    (0.38, 0.40, 0.45, 1.0),
    "M_brass":        (0.64, 0.48, 0.22, 1.0),
    "M_bronze":       (0.38, 0.27, 0.14, 1.0),
    "M_wood":         (0.26, 0.17, 0.10, 1.0),
    "M_glass":        (0.30, 0.40, 0.70, 1.0),
    "M_gold":         (0.85, 0.65, 0.25, 1.0),
    "M_wax":          (0.88, 0.84, 0.72, 1.0),
    "M_cloth":        (0.35, 0.08, 0.10, 1.0),
    "M_flame":        (1.00, 0.75, 0.30, 1.0),
    "M_bell":         (0.35, 0.28, 0.16, 1.0),
    "M_ember":        (0.90, 0.35, 0.12, 1.0),
    "M_gild":         (0.82, 0.60, 0.22, 1.0),
    "M_citywindow":   (0.95, 0.62, 0.25, 1.0),
    "M_marsh":        (0.10, 0.13, 0.11, 1.0),
    "M_habit":        (0.55, 0.51, 0.44, 1.0),
    "M_robe":         (0.23, 0.24, 0.28, 1.0),
    "M_robe_boss":    (0.24, 0.19, 0.26, 1.0),
    "M_shroud":       (0.62, 0.60, 0.54, 1.0),
    "M_wraith":       (0.20, 0.24, 0.33, 1.0),
    "M_leather":      (0.30, 0.20, 0.12, 1.0),
    "M_bone":         (0.72, 0.68, 0.56, 1.0),
    "M_mosaic":       (0.58, 0.46, 0.28, 1.0),
    "M_roof":         (0.14, 0.13, 0.14, 1.0),
    "M_marble":       (0.88, 0.86, 0.79, 1.0),
    "M_marble_floor": (0.78, 0.76, 0.70, 1.0),
    "M_cloud":        (0.96, 0.93, 0.87, 1.0),
}

def material(name: str):
    return _ensure_material(name, MATERIAL_COLORS.get(name, (0.8, 0.8, 0.8, 1.0)))

# ---------------------------------------------------------------- mesh build

def new_object(name: str, mesh=None):
    if mesh is None:
        mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj

def bm_to_object(bm, name: str, mat_names=("M_stone",)):
    """Finalize a bmesh into a linked object with material slots."""
    mesh = bpy.data.meshes.new(name)
    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()
    obj = new_object(name, mesh)
    for mn in mat_names:
        obj.data.materials.append(material(mn))
    return obj

def join(objs, name: str):
    """Join objects into one; returns the joined object."""
    objs = [o for o in objs if o is not None]
    ctx = bpy.context.copy()
    ctx["active_object"] = objs[0]
    ctx["selected_editable_objects"] = objs
    with bpy.context.temp_override(**ctx):
        bpy.ops.object.join()
    objs[0].name = name
    objs[0].data.name = name
    return objs[0]

# hash noise (deterministic, cheap) --------------------------------------

def _hash3(x, y, z):
    h = math.sin(x * 127.1 + y * 311.7 + z * 74.7) * 43758.5453
    return h - math.floor(h)

def value_noise(p: Vector, freq=1.0):
    x, y, z = p.x * freq, p.y * freq, p.z * freq
    xi, yi, zi = math.floor(x), math.floor(y), math.floor(z)
    xf, yf, zf = x - xi, y - yi, z - zi
    def lerp(a, b, t): return a + (b - a) * (t * t * (3 - 2 * t))
    c = [[[_hash3(xi + i, yi + j, zi + k) for k in (0, 1)] for j in (0, 1)] for i in (0, 1)]
    return lerp(
        lerp(lerp(c[0][0][0], c[0][0][1], zf), lerp(c[0][1][0], c[0][1][1], zf), yf),
        lerp(lerp(c[1][0][0], c[1][0][1], zf), lerp(c[1][1][0], c[1][1][1], zf), yf), xf)

# smooth normals + sharp edge split + box UVs ----------------------------

def finalize_mesh_shading(obj, angle_deg=42.0):
    """Enable smooth shading across curved surfaces while splitting sharp edges
    (> angle_deg) and generating box-projected UVs for MikkTSpace tangents.
    Returns a set of quantized (x,y,z) coordinates that lie on sharp edges so
    paint_masks can boost edge wear there."""
    if obj.type != 'MESH' or len(obj.data.polygons) == 0:
        return set()
    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.normal_update()

    # Generate box-projected UVs so glTF exports valid tangent frames
    uv_layer = bm.loops.layers.uv.verify()
    for f in bm.faces:
        f.smooth = True
        n = f.normal
        ax, ay, az = abs(n.x), abs(n.y), abs(n.z)
        for loop in f.loops:
            co = loop.vert.co
            if ax >= ay and ax >= az:
                loop[uv_layer].uv = (co.y * 0.5, co.z * 0.5)
            elif ay >= ax and ay >= az:
                loop[uv_layer].uv = (co.x * 0.5, co.z * 0.5)
            else:
                loop[uv_layer].uv = (co.x * 0.5, co.y * 0.5)

    thresh = math.radians(angle_deg)
    sharp_edges = []
    sharp_coords = set()
    for e in bm.edges:
        if len(e.link_faces) == 2:
            n0 = e.link_faces[0].normal
            n1 = e.link_faces[1].normal
            if n0.length > 1e-5 and n1.length > 1e-5:
                if n0.angle(n1, 0.0) > thresh:
                    sharp_edges.append(e)
                    for v in e.verts:
                        sharp_coords.add((round(v.co.x, 3), round(v.co.y, 3), round(v.co.z, 3)))

    if sharp_edges:
        bmesh.ops.split_edges(bm, edges=sharp_edges)

    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()
    return sharp_coords

# vertex color masks ------------------------------------------------------

def paint_masks(obj, wear_freq=0.9, wear_amount=1.0, moss_below=0.5, moss_fade=1.8,
                ao_cavity=None, seed=0, sharp_coords=None):
    """Paint (wear, moss-zone, AO, 1) into the vertex color attribute.

    AO approximation: downward-facing and low-in-piece vertices darker;
    optional `ao_cavity` callable(v) -> extra occlusion 0..1.
    """
    mesh = obj.data
    attr = mesh.color_attributes.get("Col") or mesh.color_attributes.new(
        name="Col", type='BYTE_COLOR', domain='CORNER')
    mesh.color_attributes.active_color = attr
    rng = random.Random(seed)
    jitter = rng.random() * 37.0
    # bounds for height-relative AO
    zs = [v.co.z for v in mesh.vertices] or [0.0]
    zmin, zmax = min(zs), max(zs)
    span = max(zmax - zmin, 0.001)
    ncorner = len(mesh.loops)
    for li in range(ncorner):
        loop = mesh.loops[li]
        v = mesh.vertices[loop.vertex_index]
        n = v.normal
        co = v.co
        wear = value_noise(co + Vector((jitter, jitter, jitter)), wear_freq)
        wear = max(0.0, min(1.0, (wear - 0.35) * 1.6)) * wear_amount
        if sharp_coords and (round(co.x, 3), round(co.y, 3), round(co.z, 3)) in sharp_coords:
            wear = min(1.0, wear + 0.24 * wear_amount)
        moss = max(0.0, 1.0 - max(co.z - moss_below, 0.0) / moss_fade)
        moss *= 0.4 + 0.6 * value_noise(co + Vector((5 + jitter, 0, 3)), 1.3)
        ao = 0.62 + 0.38 * max(n.z, -0.2)                    # under-surfaces darker
        ao *= 0.82 + 0.18 * ((co.z - zmin) / span)           # bases slightly darker
        if ao_cavity is not None:
            ao *= 1.0 - 0.6 * max(0.0, min(1.0, ao_cavity(v)))
        attr.data[li].color = (wear, moss, max(0.0, min(1.0, ao)), 1.0)

# ---------------------------------------------------------------- primitives

def add_box(bm, min_co, max_co):
    """Axis-aligned box between two corners; returns its faces' verts."""
    x0, y0, z0 = min_co
    x1, y1, z1 = max_co
    vs = [bm.verts.new((x, y, z)) for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)]
    # vs index: x*4 + y*2 + z
    faces = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 2, 6, 4), (1, 5, 7, 3), (0, 4, 5, 1), (2, 3, 7, 6)]
    for f in faces:
        bm.faces.new([vs[i] for i in f])
    return vs

def add_cyl(bm, cx, cy, z0, h, r, n=12):
    """Vertical cylinder centered at (cx, cy) from z0 to z0 + h with radius r."""
    z1 = z0 + h
    r0 = [bm.verts.new((cx + r * math.cos(math.tau * i / n),
                        cy + r * math.sin(math.tau * i / n), z0)) for i in range(n)]
    r1 = [bm.verts.new((cx + r * math.cos(math.tau * i / n),
                        cy + r * math.sin(math.tau * i / n), z1)) for i in range(n)]
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((r0[i], r0[j], r1[j], r1[i]))
    bm.faces.new(list(reversed(r0)))
    bm.faces.new(r1)
    return r0 + r1

def box_object(name, size, mat="M_stone", origin='corner'):
    """Simple box; origin at floor center or corner."""
    bm = bmesh.new()
    sx, sy, sz = size
    if origin == 'center':
        add_box(bm, (-sx / 2, -sy / 2, 0), (sx / 2, sy / 2, sz))
    else:
        add_box(bm, (0, 0, 0), (sx, sy, sz))
    return bm_to_object(bm, name, (mat,))

# arch curves --------------------------------------------------------------

def pointed_arch(width, sharpness=1.0, segments=16, spring_y=0.0):
    """Polyline of a pointed arch intrados from left springer to right.

    sharpness: 1.0 = equilateral; >1 = steeper lancet. Radius = width*sharpness.
    Returns list[(x, y)] including both springers, apex in middle.
    """
    R = width * sharpness
    cx = -width / 2 + R          # center for the LEFT arc (offset right)
    apex_y = spring_y + math.sqrt(max(R * R - cx * cx, 0.0))
    pts = []
    # left arc: from (-w/2, s) to (0, apex). angle from pi to acos(-cx/R)
    a0 = math.pi
    a1 = math.acos(max(-1.0, min(1.0, -cx / R)))
    for i in range(segments + 1):
        t = i / segments
        a = a0 + (a1 - a0) * t
        pts.append((cx + R * math.cos(a), spring_y + R * math.sin(a)))
    # right arc mirrors, skip duplicate apex
    for i in range(1, segments + 1):
        x, y = pts[segments - i]
        pts.append((-x, y))
    return pts

def round_arch(width, segments=18, spring_y=0.0):
    R = width / 2
    return [(R * math.cos(math.pi - math.pi * i / segments),
             spring_y + R * math.sin(math.pi - math.pi * i / segments))
            for i in range(segments + 1)]

# panel builders -----------------------------------------------------------

def wall_panel_with_arch(name, width, height, thickness, opening_w, spring_h,
                         sharpness=1.0, mat="M_stone", segments=16, sill_h=0.0):
    """A wall panel (width x height x thickness, origin bottom-center,
    thickness along Y) pierced by a pointed-arch opening. Clean quad topology:
    jamb strips beside the opening, radial-projected quads above the arch.
    If sill_h > 0 the opening starts at sill height (window instead of door).
    """
    bm = bmesh.new()
    hw, ht = width / 2, thickness / 2
    ow = opening_w / 2
    arch = pointed_arch(opening_w, sharpness, segments, spring_h)
    apex_y = max(p[1] for p in arch)
    assert apex_y < height - 0.02, f"{name}: arch apex {apex_y} exceeds height {height}"

    def face_ring(pts2d):
        """Extrude a 2D outline (in XZ plane… here X=width axis, Z=up) through Y."""
        front = [bm.verts.new((x, -ht, y)) for (x, y) in pts2d]
        back = [bm.verts.new((x, ht, y)) for (x, y) in pts2d]
        return front, back

    def quad(a, b, c, d):
        try:
            bm.faces.new((a, b, c, d))
        except ValueError:
            pass  # duplicate face guard

    # Build as vertical slices: left jamb, opening span (above arch), right jamb.
    # Left jamb: x from -hw to -ow, full height.
    for (x0, x1) in ((-hw, -ow), (ow, hw)):
        f, b = face_ring([(x0, 0), (x1, 0), (x1, height), (x0, height)])
        quad(f[0], f[1], f[2], f[3]); quad(b[3], b[2], b[1], b[0])
        quad(f[3], f[2], b[2], b[3])   # top edge cap (merged later with center)
        quad(b[0], b[1], f[1], f[0])   # bottom
        # outer side edge
        if x0 == -hw:
            quad(f[0], f[3], b[3], b[0])
        else:
            quad(f[0], f[3], b[3], b[0])
        if x1 == hw:
            quad(f[2], f[1], b[1], b[2])
        else:
            quad(f[2], f[1], b[1], b[2])

    # Center: below sill (if window), above arch curve.
    if sill_h > 0.0:
        f, b = face_ring([(-ow, 0), (ow, 0), (ow, sill_h), (-ow, sill_h)])
        quad(f[0], f[1], f[2], f[3]); quad(b[3], b[2], b[1], b[0])
        quad(b[0], b[1], f[1], f[0])
        quad(f[3], f[2], b[2], b[3])  # sill top (opening bottom face)

    # Above arch: for each arch segment, a quad up to the top edge.
    af = [bm.verts.new((x, -ht, y)) for (x, y) in arch]
    ab = [bm.verts.new((x, ht, y)) for (x, y) in arch]
    tf = [bm.verts.new((x, -ht, height)) for (x, _) in arch]
    tb = [bm.verts.new((x, ht, height)) for (x, _) in arch]
    for i in range(len(arch) - 1):
        quad(af[i], af[i + 1], tf[i + 1], tf[i])          # front fill
        quad(tb[i], tb[i + 1], ab[i + 1], ab[i])          # back fill
        quad(af[i + 1], af[i], ab[i], ab[i + 1])          # intrados (arch soffit)
        quad(tf[i], tf[i + 1], tb[i + 1], tb[i])          # top cap strip
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0005)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    obj = bm_to_object(bm, name, (mat,))
    return obj

def loft_rings(name, rings, mat="M_stone_trim", cap_bottom=True, cap_top=True):
    """Loft horizontal rings into a surface (columns, bells, finials).

    rings: list of (radius, z, nsides, rotation_offset) — consecutive rings
    are bridged. nsides must match between rings.
    """
    bm = bmesh.new()
    prev = None
    n = rings[0][2]
    for (r, z, nsides, rot) in rings:
        assert nsides == n
        ring = []
        for i in range(nsides):
            a = 2 * math.pi * i / nsides + rot
            ring.append(bm.verts.new((r * math.cos(a), r * math.sin(a), z)))
        if prev is not None:
            for i in range(nsides):
                bm.faces.new((prev[i], prev[(i + 1) % nsides],
                              ring[(i + 1) % nsides], ring[i]))
        prev = ring
        if cap_bottom and prev is not None and (r, z) == (rings[0][0], rings[0][1]):
            pass
    if cap_bottom:
        bm.verts.ensure_lookup_table()
        first = bm.verts[:n]
        bm.faces.new(reversed(first))
    if cap_top:
        bm.faces.new(prev)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0005)
    return bm_to_object(bm, name, (mat,))

def sweep_profile(name, path_pts, profile, mat="M_stone_trim", close_caps=True,
                  up_hint=Vector((0, 1, 0))):
    """Sweep a 2D profile (list[(u,v)]) along a 3D polyline.

    Frames: tangent from the path; profile 'v' axis aims along the binormal
    computed against up_hint (paths here mostly lie in vertical planes).
    """
    bm = bmesh.new()
    rings = []
    n = len(path_pts)
    for i, p in enumerate(path_pts):
        p = Vector(p)
        t = (Vector(path_pts[min(i + 1, n - 1)]) - Vector(path_pts[max(i - 1, 0)])).normalized()
        side = t.cross(up_hint)
        if side.length < 1e-4:
            side = t.cross(Vector((1, 0, 0)))
        side.normalize()
        up = side.cross(t).normalized()
        ring = [bm.verts.new(p + side * u + up * v) for (u, v) in profile]
        rings.append(ring)
    m = len(profile)
    for i in range(n - 1):
        for j in range(m):
            bm.faces.new((rings[i][j], rings[i + 1][j],
                          rings[i + 1][(j + 1) % m], rings[i][(j + 1) % m]))
    if close_caps:
        bm.faces.new(rings[0])
        bm.faces.new(reversed(rings[-1]))
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0005)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm_to_object(bm, name, (mat,))

def circle_profile(r, n=12, squash=1.0):
    return [(r * math.cos(2 * math.pi * i / n), r * squash * math.sin(2 * math.pi * i / n))
            for i in range(n)]

def chamfer_rect_profile(w, h, c):
    """Rectangle w×h with chamfered corners (rib/molding profile)."""
    hw, hh = w / 2, h / 2
    return [(-hw + c, -hh), (hw - c, -hh), (hw, -hh + c), (hw, hh - c),
            (hw - c, hh), (-hw + c, hh), (-hw, hh - c), (-hw, -hh + c)]

# ---------------------------------------------------------------- export

def apply_all(obj):
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    obj.select_set(False)

def export_glb(objs, filepath, paint=True, seed=0, **paint_kw):
    """Select objs, compute smooth normals + sharp edge split + box UVs,
    paint masks if not already painted, and export one .glb."""
    bpy.ops.object.select_all(action='DESELECT')
    for i, o in enumerate(objs):
        sharp_coords = finalize_mesh_shading(o, angle_deg=42.0)
        if paint and not o.data.color_attributes:
            paint_masks(o, seed=seed + i, sharp_coords=sharp_coords, **paint_kw)
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.export_scene.gltf(
        filepath=filepath,
        use_selection=True,
        export_format='GLB',
        export_apply=True,
        export_vertex_color='ACTIVE',
        export_yup=True,
        export_animations=False,
        export_skins=False,
        export_lights=False,
        export_cameras=False,
    )
    bpy.ops.object.select_all(action='DESELECT')
