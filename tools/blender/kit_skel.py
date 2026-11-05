"""Skeletal character bodies (the humanoid overhaul, D-005 superseded).

One shared 17-bone humanoid armature; per-archetype skinned bodies built
from overlapping parts rigidly weighted to their bones, with doll-joint
spheres at elbows/knees/shoulders so bending never tears. Animations are
authored in Godot on bone tracks (SkelAnim) — these files carry ONLY the
skeleton + skin, so pose iteration never round-trips through Blender.

Archetypes: hero (the Latecomer), ward, penitent, giant (Bellkeeper),
sister (Aveline), sexton, chorister, precentress, shroud, bellox, echo,
herald, mire, wretch, seraph. Forward = Blender +Y -> Godot -Z.
"""
import math
import random
import bpy
import bmesh
from mathutils import Vector

import vglib as V

# bone name -> (head, tail, parent)
# Blender +X maps to Godot +X; a character facing Godot -Z has its RIGHT
# side at +X, so the +X limbs are the *_r chain.
BONES = {
    "hips":    ((0, 0, 0.96), (0, 0, 1.08), None),
    "spine":   ((0, 0, 1.08), (0, 0, 1.24), "hips"),
    "chest":   ((0, 0, 1.24), (0, 0, 1.44), "spine"),
    "neck":    ((0, 0, 1.44), (0, 0.008, 1.5), "chest"),
    "head":    ((0, 0.008, 1.5), (0, 0.02, 1.76), "neck"),
    # arms hang with a relaxed elbow: upper arm drifts a touch back,
    # forearm returns forward — reads human instead of mannequin
    "uarm_r":  ((0.225, 0, 1.40), (0.262, -0.025, 1.15), "chest"),
    "farm_r":  ((0.262, -0.025, 1.15), (0.272, 0.045, 0.91), "uarm_r"),
    "hand_r":  ((0.272, 0.045, 0.91), (0.272, 0.075, 0.79), "farm_r"),
    "uarm_l":  ((-0.225, 0, 1.40), (-0.262, -0.025, 1.15), "chest"),
    "farm_l":  ((-0.262, -0.025, 1.15), (-0.272, 0.045, 0.91), "uarm_l"),
    "hand_l":  ((-0.272, 0.045, 0.91), (-0.272, 0.075, 0.79), "farm_l"),
    "thigh_r": ((0.11, 0, 0.96), (0.116, 0.018, 0.52), "hips"),
    "shin_r":  ((0.116, 0.018, 0.52), (0.116, -0.018, 0.10), "thigh_r"),
    "foot_r":  ((0.116, -0.018, 0.10), (0.116, 0.16, 0.03), "shin_r"),
    "thigh_l": ((-0.11, 0, 0.96), (-0.116, 0.018, 0.52), "hips"),
    "shin_l":  ((-0.116, 0.018, 0.52), (-0.116, -0.018, 0.10), "thigh_l"),
    "foot_l":  ((-0.116, -0.018, 0.10), (-0.116, 0.16, 0.03), "shin_l"),
}


def build_armature():
    arm_data = bpy.data.armatures.new("Skeleton")
    arm_obj = bpy.data.objects.new("Armature", arm_data)
    bpy.context.collection.objects.link(arm_obj)
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode='EDIT')
    ebs = {}
    for name, (h, t, parent) in BONES.items():
        eb = arm_data.edit_bones.new(name)
        eb.head = Vector(h)
        eb.tail = Vector(t)
        eb.roll = 0.0
        ebs[name] = eb
    for name, (h, t, parent) in BONES.items():
        if parent:
            ebs[name].parent = ebs[parent]
    bpy.ops.object.mode_set(mode='OBJECT')
    return arm_obj


# ---- part builders: each returns (bmesh_geometry appended, weight bone) ----

def _tube(bm, p0, p1, r0, r1, n=16, bulge=1.0, steps=5, flutes=0, flute_amp=0.055, squash=(1.0, 1.0), ridge_fwd=0.0):
    """High-resolution tapered tube from p0 to p1 with optional gothic fluting,
    anatomical oval squash, and forward tapul/shin ridge."""
    p0 = Vector(p0)
    p1 = Vector(p1)
    d = (p1 - p0)
    axis = d.normalized()
    up = Vector((0, 1, 0)) if abs(axis.z) > 0.9 else Vector((0, 0, 1))
    bx = axis.cross(up).normalized()
    by = axis.cross(bx).normalized()
    sx, sy = squash
    rings = []
    for s in range(steps + 1):
        t = s / steps
        r_base = (r0 * (1 - t) + r1 * t) * (1.0 + (bulge - 1.0) * math.sin(math.pi * t))
        c = p0 + d * t
        ring = []
        for i in range(n):
            a = 2 * math.pi * i / n
            r_mod = 1.0
            if flutes > 0:
                r_mod += flute_amp * math.cos(flutes * a)
            if ridge_fwd != 0.0:
                # Forward (+Y in Blender) tapul / shin crest
                fwd_dot = max(0.0, (bx * math.cos(a) + by * math.sin(a)).y)
                r_mod += ridge_fwd * (fwd_dot ** 3)
            r = r_base * r_mod
            ring.append(bm.verts.new(c + bx * (r * sx * math.cos(a)) + by * (r * sy * math.sin(a))))
        rings.append(ring)
    for s in range(steps):
        for i in range(n):
            bm.faces.new((rings[s][i], rings[s][(i + 1) % n],
                          rings[s + 1][(i + 1) % n], rings[s + 1][i]))
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])


def _ball(bm, c, r, sub=2, scale=(1.0, 1.0, 1.0)):
    got = bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=r)
    cx, cy, cz = c
    sx, sy, sz = scale
    for v in got["verts"]:
        v.co = Vector((v.co.x * sx + cx, v.co.y * sy + cy, v.co.z * sz + cz))


def _torus_ring(bm, c, major_r, minor_r, n_major=20, n_minor=8, squash=(1.0, 1.0)):
    """Hollow torus ring in the XY plane around center c."""
    cx, cy, cz = c
    sx, sy = squash
    rings = []
    for i in range(n_major):
        a = 2 * math.pi * i / n_major
        ca, sa = math.cos(a), math.sin(a)
        ring = []
        for j in range(n_minor):
            b_ang = 2 * math.pi * j / n_minor
            r = major_r + minor_r * math.cos(b_ang)
            z = cz + minor_r * math.sin(b_ang)
            ring.append(bm.verts.new((cx + r * sx * ca, cy + r * sy * sa, z)))
        rings.append(ring)
    for i in range(n_major):
        i2 = (i + 1) % n_major
        for j in range(n_minor):
            j2 = (j + 1) % n_minor
            bm.faces.new((rings[i][j], rings[i2][j], rings[i2][j2], rings[i][j2]))


def _arc_tube(bm, p0, p1, r0, r1, n=14, gap=1.0, steps=5):
    """Cowl strip: a high-res tube whose rim skips an opening centered on model +Y
    (forward), so the face/visor shows through the hood."""
    p0 = Vector(p0)
    p1 = Vector(p1)
    d = (p1 - p0)
    axis = d.normalized()
    up = Vector((0, 1, 0)) if abs(axis.z) > 0.9 else Vector((0, 0, 1))
    bx = axis.cross(up).normalized()
    by = axis.cross(bx).normalized()
    fwd = Vector((0, 1, 0))
    ang0 = math.atan2(fwd.dot(by), fwd.dot(bx))
    rings = []
    for s in range(steps + 1):
        t = s / steps
        r = r0 * (1 - t) + r1 * t
        c = p0 + d * t
        ring = []
        for i in range(n + 1):
            a = ang0 + gap + (2 * math.pi - 2 * gap) * i / n
            ring.append(bm.verts.new(c + (bx * math.cos(a) + by * math.sin(a)) * r))
        rings.append(ring)
    faces = []
    for s in range(steps):
        for i in range(n):
            faces.append(bm.faces.new((rings[s][i], rings[s][i + 1],
                                       rings[s + 1][i + 1], rings[s + 1][i])))
    verts = [v for ring in rings for v in ring]
    edges = list({e for f in faces for e in f.edges})
    bmesh.ops.solidify(bm, geom=faces + edges + verts, thickness=0.014)
    return rings


def _pauldron(b, side, s, mat_plate, mat_trim=None, r=0.095, z=1.41):
    """Articulated 3-lame Dark Souls knight pauldron + upper-arm rerebrace weighted to uarm."""
    bm = b.part(f"uarm_{side}", mat_plate)
    # Main upper dome
    _ball(bm, (s * 0.238, 0.0, z), r, sub=2, scale=(1.08, 1.05, 0.88))
    # Two lower articulated lame skirts wrapping the deltoid
    _tube(bm, Vector((s * 0.235, 0, z - 0.01)), Vector((s * 0.252, -0.005, z - 0.075)),
          r * 0.98, r * 0.88, n=14, steps=2, ridge_fwd=0.08)
    _tube(bm, Vector((s * 0.248, -0.005, z - 0.068)), Vector((s * 0.260, -0.01, z - 0.125)),
          r * 0.92, r * 0.78, n=14, steps=2, ridge_fwd=0.08)
    # Fitted upper-arm rerebrace cannon down to the elbow couter
    uh, ut = _bone_vec(f"uarm_{side}")
    _tube(bm, uh + (ut - uh) * 0.36, ut, r * 0.74, r * 0.64, n=14, steps=3, bulge=1.04)
    # Upright haute-piece neck guard ridge on the inner shoulder
    V.add_box(bm, (s * 0.165 - 0.012, -0.045, z + 0.02), (s * 0.165 + 0.012, 0.045, z + 0.085))
    if mat_trim:
        bm_t = b.part(f"uarm_{side}", mat_trim)
        _tube(bm_t, Vector((s * 0.256, -0.008, z - 0.118)), Vector((s * 0.262, -0.01, z - 0.132)),
              r * 0.82, r * 0.80, n=14, steps=1)


def _hand(bm, side, s, h3, t3, g=1.0):
    """Sculpted palm, opposable thumb, and curled finger block (replaces peg cones)."""
    d = t3 - h3
    palm_end = h3 + d * 0.58
    # Metacarpal palm
    _tube(bm, h3, palm_end, 0.044 * g, 0.042 * g, n=10, steps=2, squash=(0.78, 1.15))
    # 4 curled fingers tapering & curling slightly inward (-X in side space)
    for fi, fy_off in enumerate((-0.024, -0.008, 0.008, 0.024)):
        f_base = palm_end + Vector((0, fy_off * g, 0.005))
        f_mid = f_base + Vector((-s * 0.008 * g, fy_off * 0.8 * g, -0.028 * g))
        f_tip = f_mid + Vector((-s * 0.020 * g, fy_off * 0.6 * g, -0.022 * g))
        _tube(bm, f_base, f_mid, 0.012 * g, 0.010 * g, n=6, steps=1)
        _tube(bm, f_mid, f_tip, 0.010 * g, 0.007 * g, n=6, steps=1)
    # Opposable thumb on the forward (+Y) side of the palm
    th_base = h3 + d * 0.28 + Vector((0, 0.028 * g, 0))
    th_tip = th_base + Vector((-s * 0.016 * g, 0.026 * g, -0.036 * g))
    _tube(bm, th_base, th_tip, 0.014 * g, 0.009 * g, n=6, steps=2)


def _gauntlet_and_couter(b, side, s, mat_plate, g=1.0):
    """Articulated elbow couter, hourglass vambrace, flared cuff, and armored gauntlet."""
    h, t = _bone_vec(f"uarm_{side}")
    bm_c = b.joint(f"uarm_{side}", f"farm_{side}", mat_plate)
    _ball(bm_c, tuple(t + Vector((s * 0.012, -0.015, 0))), 0.062 * g, sub=2, scale=(1.1, 1.15, 0.9))
    bm_f = b.part(f"farm_{side}", mat_plate)
    h2, t2 = _bone_vec(f"farm_{side}")
    _tube(bm_f, h2, t2, 0.058 * g, 0.064 * g, n=14, steps=4, bulge=0.95, ridge_fwd=0.08)
    # Flared gothic gauntlet cuff at wrist
    _tube(bm_f, h2 + (t2 - h2) * 0.72, t2 + Vector((0, 0, 0.01)), 0.068 * g, 0.056 * g, n=14, steps=2, squash=(0.92, 1.12))
    bm_h = b.part(f"hand_{side}", mat_plate)
    h3, t3 = _bone_vec(f"hand_{side}")
    _hand(bm_h, side, s, h3, t3, g=g * 1.04)


def _greave_and_sabaton(b, side, s, mat_plate, g=1.0):
    """Articulated thigh cuisse, knee poleyn, anatomical shin greave, and laminated sabaton."""
    h, t = _bone_vec(f"thigh_{side}")
    bm_th = b.part(f"thigh_{side}", mat_plate)
    _tube(bm_th, h, t, 0.088 * g, 0.070 * g, n=14, steps=4, bulge=1.06, ridge_fwd=0.10)
    bm_k = b.joint(f"thigh_{side}", f"shin_{side}", mat_plate)
    _ball(bm_k, tuple(t + Vector((0, 0.020, 0.01))), 0.072 * g, sub=2, scale=(0.96, 1.20, 1.06))
    bm_s = b.part(f"shin_{side}", mat_plate)
    h2, t2 = _bone_vec(f"shin_{side}")
    _tube(bm_s, h2, t2, 0.076 * g, 0.060 * g, n=14, steps=5, bulge=1.10, squash=(0.96, 1.08), ridge_fwd=0.16)
    _tube(bm_s, h2 + (t2 - h2) * 0.78, t2, 0.062 * g, 0.068 * g, n=14, steps=2, squash=(0.96, 1.10))
    bm_ft = b.part(f"foot_{side}", mat_plate)
    h3, t3 = _bone_vec(f"foot_{side}")
    _tube(bm_ft, h3 + Vector((0, -0.02, 0.01)), t3 + Vector((0, 0.03, -0.005)),
          0.062 * g, 0.046 * g, n=12, steps=4, squash=(1.0, 0.82), ridge_fwd=0.14)


def _knight_helm(b, mat_plate, mat_visor="M_iron", g=1.0, crest=True):
    """Sculpted Dark Souls knight bascinet/sallet with houndskull visor and eye slit."""
    bm = b.part("head", mat_plate)
    # Skullcap dome
    _ball(bm, (0, 0.01, 1.63), 0.118 * g, sub=2, scale=(0.96, 1.08, 1.08))
    # Gorget / bevelled neck guard
    _tube(bm, Vector((0, -0.005, 1.46)), Vector((0, 0.008, 1.56)),
          0.132 * g, 0.112 * g, n=16, steps=3, squash=(1.02, 1.06))
    # Angled visor plate below the eye-slit
    _tube(bm, Vector((0, 0.025, 1.53)), Vector((0, 0.045, 1.605)),
          0.112 * g, 0.118 * g, n=14, steps=2, ridge_fwd=0.22)
    # Brow plate above the eye-slit
    _tube(bm, Vector((0, 0.02, 1.622)), Vector((0, 0.015, 1.67)),
          0.118 * g, 0.112 * g, n=14, steps=2, ridge_fwd=0.14)
    if crest:
        # Sagittal helm crest
        V.add_box(bm, (-0.012 * g, -0.09 * g, 1.64), (0.012 * g, 0.11 * g, 1.765))
    # Recessed dark visor slit
    bm_v = b.part("head", mat_visor)
    V.add_box(bm_v, (-0.068 * g, 0.088 * g, 1.602), (0.068 * g, 0.138 * g, 1.626))


def _bone_vec(name):
    h, t, _ = BONES[name]
    return Vector(h), Vector(t)


class BodyBuilder:
    """Collects parts; each part is its own bmesh chunk with one bone weight."""

    def __init__(self, name):
        self.name = name
        self.chunks = []   # (bmesh, bone, material)

    def part(self, bone, mat):
        bm = bmesh.new()
        self.chunks.append((bm, bone, mat))
        return bm

    def joint(self, bone_a, bone_b, mat):
        """Chunk weighted 50/50 between two bones — smooth hinge skin."""
        bm = bmesh.new()
        self.chunks.append((bm, (bone_a, bone_b), mat))
        return bm

    def finalize(self, arm_obj, lumpy=0.0, seed=5):
        mats = []
        merged = bmesh.new()
        uv_layer = merged.loops.layers.uv.verify()
        ranges = []
        mat_ids = {}
        thresh = math.radians(44.0)
        for bm, bone, mat in self.chunks:
            if mat not in mat_ids:
                mat_ids[mat] = len(mat_ids)
                mats.append(mat)
            bm.normal_update()
            # Split sharp edges (>44 deg) inside each chunk before recording
            # vertex group ranges so smooth normals never bleed across 90-deg boxes
            sharp = [
                e for e in bm.edges
                if len(e.link_faces) == 2
                and e.link_faces[0].normal.length > 1e-5
                and e.link_faces[1].normal.length > 1e-5
                and e.link_faces[0].normal.angle(e.link_faces[1].normal, 0.0) > thresh
            ]
            if sharp:
                bmesh.ops.split_edges(bm, edges=sharp)
            bm.normal_update()

            start = len(merged.verts)
            bm.verts.ensure_lookup_table()
            vmap = {}
            for v in bm.verts:
                co = v.co.copy()
                if lumpy > 0:
                    w = V.value_noise(co * 3.0 + Vector((seed, seed, 0)))
                    co += Vector(((w - 0.5) * lumpy, (V.value_noise(co * 2.3) - 0.5) * lumpy,
                                  (V.value_noise(co * 2.7 + Vector((9, 0, 0))) - 0.5) * lumpy * 0.5))
                vmap[v] = merged.verts.new(co)
            for f in bm.faces:
                try:
                    nf = merged.faces.new([vmap[v] for v in f.verts])
                    nf.material_index = mat_ids[mat]
                    nf.smooth = True
                    n = f.normal
                    ax, ay, az = abs(n.x), abs(n.y), abs(n.z)
                    for loop in nf.loops:
                        lco = loop.vert.co
                        if ax >= ay and ax >= az:
                            loop[uv_layer].uv = (lco.y, lco.z)
                        elif ay >= ax and ay >= az:
                            loop[uv_layer].uv = (lco.x, lco.z)
                        else:
                            loop[uv_layer].uv = (lco.x, lco.y)
                except ValueError:
                    pass
            bm.free()
            ranges.append((start, len(merged.verts), bone))
        mesh = bpy.data.meshes.new(self.name)
        merged.normal_update()
        merged.to_mesh(mesh)
        merged.free()
        for m in mats:
            mesh.materials.append(V.material(m))
        obj = bpy.data.objects.new(self.name, mesh)
        bpy.context.collection.objects.link(obj)
        # vertex groups: rigid per part, halved across joint chunks
        for (start, end, bone) in ranges:
            names = bone if isinstance(bone, tuple) else (bone,)
            w = 1.0 / len(names)
            for nm in names:
                vg = obj.vertex_groups.get(nm) or obj.vertex_groups.new(name=nm)
                vg.add(list(range(start, end)), w, 'ADD')
        # bind
        mod = obj.modifiers.new("Armature", 'ARMATURE')
        mod.object = arm_obj
        obj.parent = arm_obj
        return obj


def common_body(b: BodyBuilder, robe_mat="M_robe", skin_mat="M_wax", boot_mat="M_leather",
                hood=True, skirt=True, skirt_len=0.34, girth=1.0, mail_mat=None):
    g = girth
    under_mat = mail_mat if mail_mat else robe_mat
    # pelvis + belt
    bm = b.part("hips", robe_mat)
    _tube(bm, Vector((0, 0, 0.90)), Vector((0, 0, 1.10)), 0.162 * g, 0.155 * g, 16, 1.05, squash=(1.08, 0.92))
    bm = b.part("hips", "M_leather")
    _tube(bm, Vector((0, 0, 1.05)), Vector((0, 0, 1.11)), 0.168 * g, 0.168 * g, 16, steps=2, squash=(1.08, 0.92))
    # belt buckle
    bm_b = b.part("hips", "M_brass")
    V.add_box(bm_b, (-0.032 * g, 0.142 * g, 1.055), (0.032 * g, 0.168 * g, 1.105))
    # torso (anatomical oval ribcage + waist taper)
    bm = b.part("spine", robe_mat)
    _tube(bm, Vector((0, 0, 1.06)), Vector((0, 0, 1.26)), 0.152 * g, 0.172 * g, 16, steps=4, flutes=8, flute_amp=0.03, squash=(1.10, 0.88))
    bm = b.part("chest", robe_mat)
    _tube(bm, Vector((0, 0, 1.24)), Vector((0, 0, 1.45)), 0.176 * g, 0.118 * g, 16, 1.06, steps=5, flutes=8, flute_amp=0.03, squash=(1.14, 0.86))
    # shoulders + arms
    for side in ("l", "r"):
        s = 1 if side == "r" else -1
        bm = b.joint("chest", f"uarm_{side}", robe_mat)
        _tube(bm, Vector((s * 0.105 * g, 0, 1.405)), Vector((s * 0.228, 0, 1.395)),
              0.072 * g, 0.068 * g, 12, steps=3, bulge=1.06)
        bm = b.joint("chest", f"uarm_{side}", under_mat)
        _ball(bm, (s * 0.225, 0, 1.40), 0.072 * g, sub=2)
        bm = b.part(f"uarm_{side}", under_mat)
        h, t = _bone_vec(f"uarm_{side}")
        _tube(bm, h, t, 0.066 * g, 0.056 * g, 14, steps=4, bulge=1.05)
        bm = b.joint(f"uarm_{side}", f"farm_{side}", robe_mat)
        _ball(bm, tuple(t), 0.056 * g, sub=2)
        bm = b.part(f"farm_{side}", robe_mat)
        h2, t2 = _bone_vec(f"farm_{side}")
        _tube(bm, h2, t2, 0.054 * g, 0.062 * g, 14, steps=4)
        bm = b.part(f"hand_{side}", skin_mat)
        h3, t3 = _bone_vec(f"hand_{side}")
        _hand(bm, side, s, h3, t3, g=g)
    # legs
    thigh_r0 = 0.068 * g if skirt else 0.084 * g
    thigh_r1 = 0.052 * g if skirt else 0.062 * g
    for side in ("l", "r"):
        bm = b.joint("hips", f"thigh_{side}", under_mat)
        h, t = _bone_vec(f"thigh_{side}")
        _ball(bm, tuple(h + Vector((0, 0, -0.01))), (0.072 if skirt else 0.086) * g, sub=2)
        bm = b.part(f"thigh_{side}", under_mat)
        _tube(bm, h, t, thigh_r0, thigh_r1, 14, steps=4, bulge=1.04)
        bm = b.joint(f"thigh_{side}", f"shin_{side}", boot_mat)
        _ball(bm, tuple(t), 0.062 * g, sub=2)
        bm = b.part(f"shin_{side}", boot_mat)
        h2, t2 = _bone_vec(f"shin_{side}")
        _tube(bm, h2, t2, 0.058 * g, 0.048 * g, 14, steps=4, bulge=1.05)
        bm = b.part(f"foot_{side}", boot_mat)
        h3, t3 = _bone_vec(f"foot_{side}")
        _tube(bm, h3 + Vector((0, -0.01, 0.01)), t3, 0.052 * g, 0.042 * g, 12, steps=3, squash=(1.0, 0.8))
    # neck + sculpted head + brow/jawline (closed-helm knights wear a dark mail
    # coif under the helm so pitching the head forward never exposes a pale chin)
    bm = b.joint("chest", "head", under_mat)
    _tube(bm, Vector((0, 0, 1.42)), Vector((0, 0.01, 1.53)), 0.062 * g, 0.056 * g, 12, steps=3)
    if (hood and hood != "closed") or (not hood and not mail_mat):
        # Deep shadowed upper cranium under the cowl/hat crown + sculpted lower face below the brow
        bm_eye = b.part("head", "M_iron")
        _ball(bm_eye, (0, 0.014 * g, 1.636), 0.098 * g, sub=2, scale=(0.91, 1.05, 0.88))
        bm = b.part("head", skin_mat)
        _ball(bm, (0, 0.022 * g, 1.566), 0.078 * g, sub=2, scale=(0.86, 1.08, 0.96))
    else:
        head_under_mat = mail_mat if mail_mat else skin_mat
        bm = b.part("head", head_under_mat)
        _ball(bm, (0, 0.012 * g, 1.620), 0.100 * g, sub=2, scale=(0.90, 1.04, 1.04))
    if hood == "closed":
        # sealed wax cone — the faceless penitents
        bm = b.part("head", robe_mat)
        _tube(bm, Vector((0, -0.02, 1.45)), Vector((0, 0.0, 1.62)), 0.158 * g, 0.162 * g, 16, 1.05, steps=4, flutes=10, flute_amp=0.04)
        _tube(bm, Vector((0, 0.0, 1.62)), Vector((0, 0.05, 1.84)), 0.155 * g, 0.018 * g, 16, steps=5, flutes=10, flute_amp=0.04)
    elif hood:
        # open cowl: pleated mantle collar below the chin, sculpted cheek cowls,
        # and a closed 360-deg upper hood dome & peak overhanging the brow so
        # the top of the inner skull sphere never pokes through the crown.
        bm = b.part("head", robe_mat)
        _tube(bm, Vector((0, -0.02, 1.45)), Vector((0, 0.0, 1.53)), 0.160 * g, 0.150 * g, 16, 1.04, steps=3, flutes=8, flute_amp=0.035)
        _arc_tube(bm, Vector((0, -0.01, 1.51)), Vector((0, 0.01, 1.65)), 0.150 * g, 0.142 * g, 14, gap=0.78, steps=4)
        _tube(bm, Vector((0, 0.012 * g, 1.628)), Vector((0, -0.02 * g, 1.72)), 0.146 * g, 0.108 * g, 16, steps=3, flutes=8, flute_amp=0.03, squash=(0.98, 1.08))
        _tube(bm, Vector((0, -0.02 * g, 1.71)), Vector((0, -0.075 * g, 1.80)), 0.106 * g, 0.020 * g, 16, steps=3, flutes=8, flute_amp=0.03)
    if skirt:
        # pleated surcoat/tabard skirt with gothic folds
        bm = b.part("hips", robe_mat)
        _tube(bm, Vector((0, 0, 0.94)), Vector((0, 0, 0.92 - skirt_len)),
              0.176 * g, 0.258 * g, 18, bulge=1.04, steps=5, flutes=10, flute_amp=0.045, squash=(1.06, 1.02))
        if mail_mat and skirt_len <= 0.50:
            # Chainmail hauberk hem peeking just below short surcoats
            bm_m = b.part("hips", mail_mat)
            z_hem = 0.92 - skirt_len
            _tube(bm_m, Vector((0, 0, z_hem + 0.04)), Vector((0, 0, z_hem - 0.04)),
                  0.215 * g, 0.225 * g, 16, steps=2, squash=(1.02, 0.96))
    return b


def hero(arm):
    """The Latecomer: Astora/Elite Knight pilgrim — dark fluted half-plate over
    riveted chainmail hauberk, crested knight bascinet helm with brass visor,
    cross-body baldric, articulated 3-lame pauldrons, gauntlets, and greaves."""
    b = BodyBuilder("hero")
    common_body(b, "M_robe", "M_wax", "M_plate_dark", hood=False, skirt=True,
                skirt_len=0.38, girth=1.02, mail_mat="M_chainmail")
    # Sculpted Gothic breastplate & plackart with tapul ridge
    bm = b.part("chest", "M_plate_dark")
    _tube(bm, Vector((0, 0, 1.22)), Vector((0, 0, 1.44)), 0.184, 0.136, n=16, bulge=1.06,
          steps=4, flutes=8, flute_amp=0.02, squash=(1.12, 0.90), ridge_fwd=0.12)
    # Draped pilgrim mantle collar around the shoulders (tucked below the helm chin)
    bm_m = b.part("chest", "M_robe")
    _tube(bm_m, Vector((0, -0.01, 1.38)), Vector((0, -0.005, 1.445)), 0.192, 0.124, n=16,
          steps=3, flutes=10, flute_amp=0.03, squash=(1.12, 0.88))
    # Gorget collar & brass chest trim
    bm_g = b.part("chest", "M_brass")
    _tube(bm_g, Vector((0, 0, 1.43)), Vector((0, 0, 1.465)), 0.136, 0.114, n=16, steps=2, squash=(1.02, 0.92))
    # Armored besagew rondels guarding the shoulder joints
    bm_rd = b.part("chest", "M_plate_dark")
    bm_rb = b.part("chest", "M_brass")
    for sx in (-1, 1):
        _tube(bm_rd, Vector((sx * 0.145, 0.125, 1.385)), Vector((sx * 0.150, 0.142, 1.390)), 0.038, 0.036, n=12, steps=1)
        _tube(bm_rb, Vector((sx * 0.148, 0.138, 1.388)), Vector((sx * 0.154, 0.148, 1.392)), 0.014, 0.004, n=10, steps=1)
    # Reliquary satchel + dagger scabbard at hip + articulated plate faulds/tassets
    bm_h = b.part("hips", "M_leather")
    V.add_box(bm_h, (0.11, -0.19, 0.86), (0.26, -0.05, 1.02))
    _tube(bm_h, Vector((-0.185, 0.08, 1.08)), Vector((-0.205, -0.06, 0.88)), 0.020, 0.012, n=8, steps=2)
    bm_tass = b.part("hips", "M_plate_dark")
    _tube(bm_tass, Vector((0, 0, 0.94)), Vector((0, 0, 1.07)), 0.186, 0.172, n=16, steps=3, flutes=6, flute_amp=0.04, squash=(1.10, 0.92))
    # Full Dark Souls Elite Knight bascinet helm with brass visor & crest
    _knight_helm(b, "M_plate_dark", "M_brass", g=1.04, crest=True)
    # Articulated 3-lame pauldrons, gauntlets, and greaves
    for side, s in (("r", 1), ("l", -1)):
        _pauldron(b, side, s, "M_plate_dark", "M_brass", r=0.094, z=1.41)
        _gauntlet_and_couter(b, side, s, "M_plate_dark", g=1.02)
        _greave_and_sabaton(b, side, s, "M_plate_dark", g=1.02)
    return b.finalize(arm)


def ward(arm):
    """Cloister Ward: full Gothic Lothric/Silver Knight plate over chainmail
    and wraith-blue surcoat, crested houndskull bascinet, and heavy pauldrons."""
    b = BodyBuilder("ward")
    common_body(b, "M_wraith", "M_wraith", "M_plate_dark", hood=False, skirt=True,
                skirt_len=0.44, girth=1.08, mail_mat="M_chainmail")
    # Fluted Gothic cuirass + plackart + hip faulds
    bm = b.part("chest", "M_plate_dark")
    _tube(bm, Vector((0, 0, 1.21)), Vector((0, 0, 1.45)), 0.198, 0.138, n=16, bulge=1.07,
          steps=5, flutes=10, flute_amp=0.025, squash=(1.12, 0.88), ridge_fwd=0.12)
    bm_s = b.part("spine", "M_plate_dark")
    _tube(bm_s, Vector((0, 0, 1.06)), Vector((0, 0, 1.24)), 0.168, 0.188, n=16, steps=3, squash=(1.10, 0.90))
    bm_f = b.part("hips", "M_plate_dark")
    _tube(bm_f, Vector((0, 0, 0.92)), Vector((0, 0, 1.07)), 0.198, 0.178, n=16, steps=3, flutes=8, flute_amp=0.04, squash=(1.10, 0.92))
    # Full knight bascinet helm with crest
    _knight_helm(b, "M_plate_dark", "M_iron", g=1.08, crest=True)
    # Articulated pauldrons, gauntlets, and greaves
    for side, s in (("r", 1), ("l", -1)):
        _pauldron(b, side, s, "M_plate_dark", "M_iron", r=0.104, z=1.42)
        _gauntlet_and_couter(b, side, s, "M_plate_dark", g=1.08)
        _greave_and_sabaton(b, side, s, "M_plate_dark", g=1.08)
    return b.finalize(arm)


def penitent(arm):
    """Wax Penitent: Dark Souls Hollow / Cathedral Thrall — dark tattered robe
    with bloodied crimson scapular, open pleated cowl with pointed drooping peak,
    wrought-iron penance collar & brow-circlet, and wax-seared chainmail."""
    b = BodyBuilder("penitent")
    common_body(b, "M_robe", "M_wax", "M_leather", hood=True, skirt=True,
                skirt_len=0.48, girth=1.00, mail_mat="M_chainmail")
    # Tattered crimson penance scapular contoured to the torso + dark mantle
    bm_sc = b.part("spine", "M_cloth")
    _tube(bm_sc, Vector((0, 0, 0.88)), Vector((0, 0, 1.28)), 0.168, 0.176, n=14,
          steps=3, flutes=6, flute_amp=0.04, squash=(0.86, 1.08), ridge_fwd=0.08)
    bm_m = b.part("chest", "M_robe")
    _tube(bm_m, Vector((0, 0, 1.26)), Vector((0, -0.01, 1.48)), 0.188, 0.158, n=14,
          steps=4, flutes=8, flute_amp=0.045, squash=(1.12, 0.92))
    # Heavy wrought-iron penance collar & spiked brow-band
    bm = b.part("chest", "M_iron")
    _tube(bm, Vector((0, 0, 1.43)), Vector((0, 0, 1.49)), 0.168, 0.148, n=14, steps=2)
    # Pointed, drooping Gothic penitent hood peak continuous with the hood crown
    bm_h = b.part("head", "M_robe")
    _tube(bm_h, Vector((0, -0.015, 1.66)), Vector((0, -0.15, 1.86)), 0.112, 0.014, n=12,
          steps=4, flutes=6, flute_amp=0.04)
    bm_fe = b.part("head", "M_iron")
    _tube(bm_fe, Vector((0, 0.016, 1.612)), Vector((0, 0.016, 1.634)), 0.104, 0.102, n=14,
          steps=1, flutes=7, flute_amp=0.04)
    for side in ("l", "r"):
        bm_w = b.part(f"farm_{side}", "M_iron")
        h, t = _bone_vec(f"farm_{side}")
        _tube(bm_w, t - (t - h) * 0.28, t, 0.064, 0.068, n=12, steps=2)
    return b.finalize(arm, lumpy=0.014, seed=77)


def giant(arm):
    """The Bellkeeper: towering Cathedral Executioner boss with bronze-banded
    cuirass, iron-studded bell harness, colossal pauldrons, and cage-bell helm."""
    b = BodyBuilder("giant")
    common_body(b, "M_robe_boss", "M_wax", "M_plate_dark", hood=True, skirt=True,
                skirt_len=0.56, girth=1.35, mail_mat="M_chainmail")
    # Heavy bronze-banded executioner cuirass
    bm = b.part("chest", "M_plate_dark")
    _tube(bm, Vector((0, 0, 1.18)), Vector((0, 0, 1.49)), 0.255, 0.225, n=16, bulge=1.08,
          steps=5, squash=(1.12, 0.94), ridge_fwd=0.14)
    # Bell-rope harness & bronze chest bands
    bm_l = b.part("chest", "M_leather")
    _tube(bm_l, Vector((0, 0, 1.28)), Vector((0, 0, 1.40)), 0.275, 0.258, n=16, steps=3)
    bm_b = b.part("chest", "M_bronze")
    _tube(bm_b, Vector((0, 0, 1.44)), Vector((0, 0, 1.50)), 0.235, 0.215, n=16, steps=2)
    # Bronze executioner cage-helm inside the hood (scaled to girth=1.35 so skin never clips)
    bm_v = b.part("head", "M_iron")
    _tube(bm_v, Vector((0, 0.025, 1.52)), Vector((0, 0.025, 1.66)), 0.152, 0.148, n=14, steps=2, squash=(0.95, 1.08))
    bm_h = b.part("head", "M_bronze")
    _tube(bm_h, Vector((0, 0.025, 1.51)), Vector((0, 0.025, 1.555)), 0.168, 0.165, n=14, steps=2, squash=(0.96, 1.10))
    _tube(bm_h, Vector((0, 0.025, 1.615)), Vector((0, 0.025, 1.665)), 0.166, 0.158, n=14, steps=2, squash=(0.96, 1.10), ridge_fwd=0.12)
    for bx in (-0.075, -0.038, 0.0, 0.038, 0.075):
        V.add_box(bm_h, (bx - 0.008, 0.145, 1.545), (bx + 0.008, 0.185, 1.625))
    for side, s in (("r", 1), ("l", -1)):
        _pauldron(b, side, s, "M_plate_dark", "M_bronze", r=0.132, z=1.43)
        _gauntlet_and_couter(b, side, s, "M_plate_dark", g=1.35)
        _greave_and_sabaton(b, side, s, "M_plate_dark", g=1.35)
    return b.finalize(arm, lumpy=0.015, seed=31)


def sister(arm):
    """Sister Aveline: Firekeeper / Shrine Maiden in finely pleated monastic
    habit, contoured scapular, silver blindfold fillet, and golden reliquary."""
    b = BodyBuilder("sister")
    common_body(b, "M_habit", "M_wax", "M_habit", hood=True, skirt=True, skirt_len=0.56)
    # Contoured monastic scapular + shoulder capelet + gilt pectoral clasp
    bm = b.part("chest", "M_leather")
    _tube(bm, Vector((0, 0, 1.18)), Vector((0, 0, 1.43)), 0.168, 0.146, n=16,
          steps=3, flutes=8, flute_amp=0.025, squash=(0.94, 1.06), ridge_fwd=0.06)
    bm_cl = b.part("chest", "M_gold")
    _torus_ring(bm_cl, (0, 0.148, 1.36), 0.028, 0.007, n_major=14, n_minor=6)
    # Silver Firekeeper eye-fillet / crown band
    bm_f = b.part("head", "M_steel")
    _tube(bm_f, Vector((0, 0.02, 1.60)), Vector((0, 0.02, 1.645)), 0.112, 0.112, n=16, steps=2)
    # Golden votive reliquary at waist
    bm_g = b.part("hips", "M_gold")
    _ball(bm_g, (-0.16, 0.08, 0.98), 0.045, sub=2)
    return b.finalize(arm)


def sexton(arm):
    """The Sexton: stout gravedigger of the Basilica. Iron kettle-cap, heavy
    contoured leather jerkin/apron, cowl collar, muscular forearms with iron bracers."""
    b = BodyBuilder("sexton")
    common_body(b, "M_robe", "M_wax", "M_leather", hood=False, skirt=True,
                skirt_len=0.28, girth=1.18)
    # Contoured heavy leather work jerkin + draped cloth neck cowl
    bm = b.part("chest", "M_leather")
    _tube(bm, Vector((0, 0, 1.16)), Vector((0, 0, 1.43)), 0.212, 0.178, n=16,
          bulge=1.05, steps=4, flutes=8, flute_amp=0.025, squash=(1.08, 0.94), ridge_fwd=0.10)
    bm_c = b.part("chest", "M_robe")
    _tube(bm_c, Vector((0, -0.01, 1.38)), Vector((0, 0, 1.49)), 0.195, 0.132, n=16,
          steps=3, flutes=10, flute_amp=0.03, squash=(1.08, 0.94))
    # Iron kettle-hat / brimmed gravedigger cap with nasal guard
    bm = b.part("head", "M_iron")
    _tube(bm, Vector((0, 0.01, 1.64)), Vector((0, 0.015, 1.675)), 0.168, 0.138, n=16, steps=2)
    _tube(bm, Vector((0, 0.015, 1.675)), Vector((0, 0.02, 1.76)), 0.130, 0.085, n=16, bulge=1.08, steps=3)
    V.add_box(bm, (-0.011, 0.125, 1.585), (0.011, 0.146, 1.655))
    # Bare muscular forearms with iron wrist bracers
    for side in ("l", "r"):
        bm = b.part(f"farm_{side}", "M_wax")
        h, t = _bone_vec(f"farm_{side}")
        _tube(bm, h + (t - h) * 0.25, t, 0.062, 0.052, n=14, steps=3, bulge=1.08)
        bm_br = b.part(f"farm_{side}", "M_iron")
        _tube(bm_br, h + (t - h) * 0.72, t, 0.058, 0.060, n=14, steps=2)
    return b.finalize(arm, lumpy=0.010, seed=19)


def chorister(arm):
    """Chorister of the Last Choir: slender liturgical caster with pleated
    vestments, stiffened choir collar, brass trim, and chained hymnal."""
    b = BodyBuilder("chorister")
    common_body(b, "M_wraith", "M_wax", "M_wraith", hood=True, skirt=True,
                skirt_len=0.60, girth=0.90)
    # High choir collar + brass rim
    bm = b.part("chest", "M_habit")
    _tube(bm, Vector((0, 0, 1.39)), Vector((0, -0.01, 1.51)), 0.162, 0.175, n=16, steps=3, flutes=12, flute_amp=0.03)
    bm_b = b.part("chest", "M_brass")
    _tube(bm_b, Vector((0, 0, 1.38)), Vector((0, 0, 1.41)), 0.166, 0.164, n=16, steps=2)
    # Hymnal tome chained to the belt
    bm = b.part("hips", "M_leather")
    V.add_box(bm, (-0.20, -0.14, 0.89), (-0.06, -0.04, 1.03))
    bm_g = b.part("hips", "M_gold")
    V.add_box(bm_g, (-0.205, -0.145, 0.94), (-0.055, -0.035, 0.98))
    return b.finalize(arm, seed=43)


def precentress(arm):
    """The Precentress: mistress of the choir. Tall gilded twin-horn mitre crown,
    pleated boss vestments, golden mantle, and crossed bronze censer chains."""
    b = BodyBuilder("precentress")
    common_body(b, "M_robe_boss", "M_wax", "M_robe_boss", hood=True, skirt=True,
                skirt_len=0.64, girth=0.98)
    # Tall gilded mitre crown with twin horns
    bm = b.part("head", "M_gold")
    _tube(bm, Vector((0, 0.0, 1.65)), Vector((0, 0.0, 1.73)), 0.130, 0.115, n=16, steps=3, flutes=8, flute_amp=0.04)
    _tube(bm, Vector((0, 0.0, 1.70)), Vector((0, -0.03, 2.04)), 0.105, 0.018, n=16, steps=5, squash=(1.2, 0.85))
    for s in (-1, 1):
        _tube(bm, Vector((s * 0.05, 0.0, 1.72)), Vector((s * 0.14, -0.02, 1.98)), 0.035, 0.008, n=10, steps=4)
    # Censer chains + gilded shoulder stole
    bm = b.part("chest", "M_bronze")
    _tube(bm, Vector((0.16, -0.11, 1.43)), Vector((-0.14, -0.13, 1.08)), 0.020, 0.020, n=10, steps=4)
    _tube(bm, Vector((-0.16, -0.11, 1.43)), Vector((0.14, -0.13, 1.08)), 0.020, 0.020, n=10, steps=4)
    _tube(bm, Vector((0.16, 0.11, 1.43)), Vector((-0.14, 0.13, 1.08)), 0.020, 0.020, n=10, steps=4)
    _tube(bm, Vector((-0.16, 0.11, 1.43)), Vector((0.14, 0.13, 1.08)), 0.020, 0.020, n=10, steps=4)
    return b.finalize(arm, seed=61)


def shroud(arm):
    """Shroudbound: swift bound corpse assassin wrapped in burial linen with
    mortuary leather straps and iron forearm claws."""
    b = BodyBuilder("shroud")
    common_body(b, "M_shroud", "M_shroud", "M_shroud", hood="closed", skirt=True,
                skirt_len=0.66, girth=0.86)
    for z0 in (0.98, 1.14, 1.28, 1.40):
        bm = b.part("chest" if z0 > 1.2 else "spine", "M_leather")
        _tube(bm, Vector((0, 0, z0)), Vector((0, 0, z0 + 0.042)), 0.168 * 0.86, 0.168 * 0.86, 14, steps=2)
    for side, s in (("r", 1), ("l", -1)):
        bm_c = b.part(f"farm_{side}", "M_iron")
        h, t = _bone_vec(f"farm_{side}")
        _tube(bm_c, h + (t - h) * 0.5, t, 0.052, 0.056, n=12, steps=2)
    return b.finalize(arm, lumpy=0.025, seed=97)


def bellox(arm):
    """Bourdon, the Bell-Ox: yoked minotaur-hulk boss crowned with a sculpted
    horned bone skull-mask, contoured timber yoke, and bronze bell harness."""
    b = BodyBuilder("bellox")
    common_body(b, "M_robe_boss", "M_wax", "M_leather", hood=False, skirt=True,
                skirt_len=0.52, girth=1.50, mail_mat="M_chainmail")
    # Sculpted bone ox-skull cranium, tapered nasal snout & curved segmented horns
    bm = b.part("head", "M_bone")
    _ball(bm, (0, 0.03, 1.64), 0.145, sub=2, scale=(1.08, 1.15, 0.98))
    _tube(bm, Vector((0, 0.06, 1.62)), Vector((0, 0.26, 1.48)), 0.105, 0.062, n=12,
          steps=4, flutes=6, flute_amp=0.05, squash=(1.08, 0.82), ridge_fwd=0.15)
    for s in (1, -1):
        _tube(bm, Vector((s * 0.10, 0.01, 1.66)), Vector((s * 0.26, 0.04, 1.73)), 0.062, 0.040, n=12, steps=3)
        _tube(bm, Vector((s * 0.26, 0.04, 1.73)), Vector((s * 0.38, 0.15, 1.88)), 0.040, 0.010, n=12, steps=3)
    # Contoured heavy timber yoke beam + iron shackle bands + bronze harness
    bm = b.part("chest", "M_wood")
    _tube(bm, Vector((-0.62, -0.04, 1.50)), Vector((0.62, -0.04, 1.50)), 0.068, 0.068, n=12,
          steps=6, bulge=1.12, squash=(1.0, 0.82))
    bm_i = b.part("chest", "M_iron")
    for sx in (-0.48, -0.22, 0.22, 0.48):
        _tube(bm_i, Vector((sx - 0.025, -0.04, 1.50)), Vector((sx + 0.025, -0.04, 1.50)), 0.076, 0.076, n=12, steps=1)
    bm = b.part("chest", "M_bronze")
    _tube(bm, Vector((0, -0.06, 1.28)), Vector((0, -0.06, 1.44)), 0.30, 0.28, n=16, steps=3)
    for side, s in (("r", 1), ("l", -1)):
        _pauldron(b, side, s, "M_plate_dark", "M_bronze", r=0.135, z=1.44)
    return b.finalize(arm, lumpy=0.018, seed=53)


def echo(arm):
    """Gilded Echo: a singer's afterimage that haunts the REMEMBERED world —
    pleated wraith weave under a radiant gilt crown, collar, and girdle."""
    b = BodyBuilder("echo")
    common_body(b, "M_wraith", "M_wax", "M_wraith", hood=True, skirt=True,
                skirt_len=0.58, girth=0.84)
    # Floating hollow gold crown/halo ring above the hooded brow
    bm = b.part("head", "M_gold")
    _torus_ring(bm, (0, -0.01, 1.73), 0.125, 0.014, n_major=20, n_minor=8)
    # Fitted gilt gorget/collar on the upper chest (below the chin)
    bm = b.part("chest", "M_gold")
    _tube(bm, Vector((0, 0, 1.36)), Vector((0, -0.005, 1.43)), 0.148, 0.114, n=16, steps=2, squash=(1.14, 0.88))
    # Fitted gilt waist girdle
    bm = b.part("hips", "M_gold")
    _tube(bm, Vector((0, 0, 0.98)), Vector((0, 0, 1.045)), 0.146, 0.144, n=16, steps=2, squash=(1.08, 0.92))
    return b.finalize(arm, seed=131)


def herald(arm):
    """Drowned Herald: Black Gate toll-crier in heraldic crimson tabard over
    chainmail, visored helm, and slung bronze war-horn."""
    b = BodyBuilder("herald")
    common_body(b, "M_robe", "M_wax", "M_plate_dark", hood="closed", skirt=True,
                skirt_len=0.64, girth=0.98, mail_mat="M_chainmail")
    # Contoured crimson heraldic tabard over chest & spine
    bm = b.part("chest", "M_cloth")
    _tube(bm, Vector((0, 0, 1.18)), Vector((0, 0, 1.44)), 0.184, 0.156, n=16,
          steps=3, flutes=8, flute_amp=0.03, squash=(1.06, 0.94), ridge_fwd=0.08)
    # Slung segmented bronze war-horn
    bm = b.part("chest", "M_bronze")
    _tube(bm, Vector((-0.21, -0.20, 1.04)), Vector((0.15, -0.26, 1.32)), 0.048, 0.095, n=14, steps=4, bulge=0.92)
    for side, s in (("r", 1), ("l", -1)):
        _pauldron(b, side, s, "M_plate_dark", "M_bronze", r=0.088, z=1.41)
    return b.finalize(arm, seed=173)


def mire(arm):
    """Mirebound: drowned marsh juggernaut in sodden peat-heavy mantle and
    rusted iron neck-shackles."""
    b = BodyBuilder("mire")
    common_body(b, "M_stone_dark", "M_leather", "M_stone_dark", hood="closed",
                skirt=True, skirt_len=0.72, girth=1.16)
    bm = b.part("chest", "M_leather")
    _tube(bm, Vector((0, 0, 1.32)), Vector((0, 0, 1.50)), 0.21, 0.245, n=16, steps=4, flutes=7, flute_amp=0.05)
    bm_i = b.part("chest", "M_iron")
    _tube(bm_i, Vector((0, 0, 1.45)), Vector((0, 0, 1.52)), 0.18, 0.175, n=14, steps=2)
    return b.finalize(arm, lumpy=0.042, seed=211)


def wretch(arm):
    """Lantern Wretch: gaunt hollow pilgrim of the Last Shore with an iron
    shackle collar and a wrought-iron hip lantern with a live ember core."""
    b = BodyBuilder("wretch")
    common_body(b, "M_wraith", "M_wax", "M_robe", hood="closed", skirt=True,
                skirt_len=0.60, girth=0.78)
    # Wrought-iron hip lantern + ember core
    bm = b.part("hips", "M_iron")
    V.add_box(bm, (0.16, -0.055, 0.78), (0.28, 0.055, 0.94))
    V.add_box(bm, (0.20, -0.018, 0.94), (0.24, 0.018, 1.05))
    bm = b.part("hips", "M_ember")
    V.add_box(bm, (0.182, -0.035, 0.805), (0.258, 0.035, 0.91))
    return b.finalize(arm, seed=307)


def seraph(arm):
    """Ward of the Morning: Sanctum paladin in fluted ivory-marble plate
    encrusted with gold, winged pauldrons, royal helm, and floating halo."""
    b = BodyBuilder("seraph")
    common_body(b, "M_marble", "M_wax", "M_marble", hood=False, skirt=True,
                skirt_len=0.46, girth=1.10, mail_mat="M_brass")
    # Fluted ivory-marble cuirass banded in gold
    bm = b.part("chest", "M_marble")
    _tube(bm, Vector((0, 0, 1.20)), Vector((0, 0, 1.47)), 0.202, 0.148, n=16, bulge=1.06,
          steps=5, flutes=10, flute_amp=0.025, squash=(1.12, 0.92), ridge_fwd=0.15)
    bm = b.part("chest", "M_gold")
    _tube(bm, Vector((0, 0, 1.31)), Vector((0, 0, 1.37)), 0.208, 0.204, n=16, steps=2, squash=(1.12, 0.92))
    _tube(bm, Vector((0, 0, 1.43)), Vector((0, 0, 1.465)), 0.152, 0.132, n=16, steps=2, squash=(1.04, 0.94))
    # Royal paladin helm
    _knight_helm(b, "M_marble", "M_gold", g=1.10, crest=True)
    # Articulated ivory-and-gold pauldrons, gauntlets, and greaves
    for side, s in (("r", 1), ("l", -1)):
        _pauldron(b, side, s, "M_marble", "M_gold", r=0.106, z=1.43)
        _gauntlet_and_couter(b, side, s, "M_marble", g=1.10)
        _greave_and_sabaton(b, side, s, "M_marble", g=1.10)
    # Gold girdle
    bm = b.part("hips", "M_gold")
    _tube(bm, Vector((0, 0, 0.99)), Vector((0, 0, 1.05)), 0.184, 0.184, n=16, steps=2)
    # Floating golden halo ring above the crown
    bm = b.part("head", "M_gold")
    _torus_ring(bm, (0, -0.01, 1.79), 0.148, 0.015, n_major=22, n_minor=8)
    return b.finalize(arm, seed=451)


ARCHETYPES = {
    "skel_hero": hero,
    "skel_ward": ward,
    "skel_penitent": penitent,
    "skel_giant": giant,
    "skel_sister": sister,
    "skel_sexton": sexton,
    "skel_chorister": chorister,
    "skel_precentress": precentress,
    "skel_shroud": shroud,
    "skel_bellox": bellox,
    "skel_echo": echo,
    "skel_herald": herald,
    "skel_mire": mire,
    "skel_wretch": wretch,
    "skel_seraph": seraph,
}


def build(name, out_path):
    V.reset_scene()
    arm = build_armature()
    body = ARCHETYPES[name](arm)
    V.paint_masks(body, seed=hash(name) % 1000, moss_below=-99.0)
    bpy.ops.object.select_all(action='DESELECT')
    arm.select_set(True)
    body.select_set(True)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.export_scene.gltf(
        filepath=out_path,
        use_selection=True,
        export_format='GLB',
        export_apply=False,          # armature binding must not be baked away
        export_vertex_color='ACTIVE',
        export_yup=True,
        export_animations=False,
        export_skins=True,
        export_lights=False,
        export_cameras=False,
    )
    tris = len(body.data.polygons)
    return {"file": None, "polys": tris, "size": [0.8, 0.8, 1.9], "origin": "feet", "skeletal": True}


BUILDERS = {}  # exported via gen_assets special-case below
