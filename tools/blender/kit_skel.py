"""Skeletal character bodies (the humanoid overhaul, D-005 superseded).

One shared 16-bone humanoid armature; per-archetype skinned bodies built
from overlapping parts rigidly weighted to their bones, with doll-joint
spheres at elbows/knees/shoulders so bending never tears. Animations are
authored in Godot on bone tracks (SkelAnim) — these files carry ONLY the
skeleton + skin, so pose iteration never round-trips through Blender.

Archetypes: hero (the Latecomer), ward, penitent, giant (Bellkeeper),
sister (Aveline). Forward = Blender +Y -> Godot -Z.
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
    "head":    ((0, 0, 1.47), (0, 0, 1.76), "chest"),
    "uarm_r":  ((0.225, 0, 1.40), (0.26, 0, 1.14), "chest"),
    "farm_r":  ((0.26, 0, 1.14), (0.27, 0.02, 0.90), "uarm_r"),
    "hand_r":  ((0.27, 0.02, 0.90), (0.27, 0.04, 0.78), "farm_r"),
    "uarm_l":  ((-0.225, 0, 1.40), (-0.26, 0, 1.14), "chest"),
    "farm_l":  ((-0.26, 0, 1.14), (-0.27, 0.02, 0.90), "uarm_l"),
    "hand_l":  ((-0.27, 0.02, 0.90), (-0.27, 0.04, 0.78), "farm_l"),
    "thigh_r": ((0.11, 0, 0.96), (0.115, 0.01, 0.52), "hips"),
    "shin_r":  ((0.115, 0.01, 0.52), (0.115, -0.01, 0.10), "thigh_r"),
    "foot_r":  ((0.115, -0.01, 0.10), (0.115, 0.17, 0.03), "shin_r"),
    "thigh_l": ((-0.11, 0, 0.96), (-0.115, 0.01, 0.52), "hips"),
    "shin_l":  ((-0.115, 0.01, 0.52), (-0.115, -0.01, 0.10), "thigh_l"),
    "foot_l":  ((-0.115, -0.01, 0.10), (-0.115, 0.17, 0.03), "shin_l"),
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

def _tube(bm, p0, p1, r0, r1, n=8, bulge=1.0):
    """Tapered tube from p0 to p1 (both Vector)."""
    d = (p1 - p0)
    L = d.length
    axis = d.normalized()
    # basis perpendicular to axis
    up = Vector((0, 1, 0)) if abs(axis.z) > 0.9 else Vector((0, 0, 1))
    bx = axis.cross(up).normalized()
    by = axis.cross(bx).normalized()
    rings = []
    steps = 3
    for s in range(steps + 1):
        t = s / steps
        r = (r0 * (1 - t) + r1 * t) * (1.0 + (bulge - 1.0) * math.sin(math.pi * t))
        c = p0 + d * t
        ring = []
        for i in range(n):
            a = 2 * math.pi * i / n
            ring.append(bm.verts.new(c + bx * (r * math.cos(a)) + by * (r * math.sin(a))))
        rings.append(ring)
    for s in range(steps):
        for i in range(n):
            bm.faces.new((rings[s][i], rings[s][(i + 1) % n],
                          rings[s + 1][(i + 1) % n], rings[s + 1][i]))
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])


def _ball(bm, c, r, sub=1):
    got = bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=r)
    for v in got["verts"]:
        v.co += Vector(c)


def _arc_tube(bm, p0, p1, r0, r1, n=10, gap=1.0):
    """Cowl strip: a tube whose rim skips an opening centered on model +Y
    (forward), so the face shows through the hood."""
    d = (p1 - p0)
    axis = d.normalized()
    up = Vector((0, 1, 0)) if abs(axis.z) > 0.9 else Vector((0, 0, 1))
    bx = axis.cross(up).normalized()
    by = axis.cross(bx).normalized()
    fwd = Vector((0, 1, 0))
    ang0 = math.atan2(fwd.dot(by), fwd.dot(bx))   # basis angle of +Y
    steps = 3
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
    for s in range(steps):
        for i in range(n):
            bm.faces.new((rings[s][i], rings[s][i + 1],
                          rings[s + 1][i + 1], rings[s + 1][i]))
    return rings


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

    def finalize(self, arm_obj, lumpy=0.0, seed=5):
        rng = random.Random(seed)
        meshes = []
        mats = []
        # merge chunks into one mesh, tracking vert ranges per bone
        merged = bmesh.new()
        ranges = []
        mat_ids = {}
        for bm, bone, mat in self.chunks:
            if mat not in mat_ids:
                mat_ids[mat] = len(mat_ids)
                mats.append(mat)
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
        # vertex groups: rigid per part
        for (start, end, bone) in ranges:
            vg = obj.vertex_groups.get(bone) or obj.vertex_groups.new(name=bone)
            vg.add(list(range(start, end)), 1.0, 'REPLACE')
        # bind
        mod = obj.modifiers.new("Armature", 'ARMATURE')
        mod.object = arm_obj
        obj.parent = arm_obj
        return obj


def common_body(b: BodyBuilder, robe_mat="M_robe", skin_mat="M_wax", boot_mat="M_leather",
                hood=True, skirt=True, skirt_len=0.34, girth=1.0):
    g = girth
    # pelvis + belt
    bm = b.part("hips", robe_mat)
    _tube(bm, Vector((0, 0, 0.9)), Vector((0, 0, 1.1)), 0.16 * g, 0.155 * g, 10, 1.05)
    bm = b.part("hips", "M_leather")
    _tube(bm, Vector((0, 0, 1.06)), Vector((0, 0, 1.11)), 0.165 * g, 0.165 * g, 10)
    # torso
    bm = b.part("spine", robe_mat)
    _tube(bm, Vector((0, 0, 1.06)), Vector((0, 0, 1.26)), 0.15 * g, 0.17 * g, 10)
    bm = b.part("chest", robe_mat)
    _tube(bm, Vector((0, 0, 1.24)), Vector((0, 0, 1.47)), 0.175 * g, 0.145 * g, 10, 1.06)
    # shoulders (doll joints)
    for side in ("l", "r"):
        s = 1 if side == "r" else -1
        bm = b.part(f"uarm_{side}", robe_mat)
        _ball(bm, (s * 0.225, 0, 1.40), 0.075 * g)
        h, t = _bone_vec(f"uarm_{side}")
        _tube(bm, h, t, 0.065 * g, 0.055 * g)
        bm = b.part(f"farm_{side}", robe_mat)
        _ball(bm, tuple(t), 0.055 * g)
        h2, t2 = _bone_vec(f"farm_{side}")
        _tube(bm, h2, t2, 0.052 * g, 0.062 * g)   # sleeve cuff flare
        bm = b.part(f"hand_{side}", skin_mat)
        h3, t3 = _bone_vec(f"hand_{side}")
        _tube(bm, h3, t3, 0.045 * g, 0.035 * g, 7)
    # legs
    for side in ("l", "r"):
        bm = b.part(f"thigh_{side}", robe_mat)
        h, t = _bone_vec(f"thigh_{side}")
        _ball(bm, tuple(h + Vector((0, 0, -0.01))), 0.085 * g)
        _tube(bm, h, t, 0.08 * g, 0.06 * g)
        bm = b.part(f"shin_{side}", boot_mat)
        _ball(bm, tuple(t), 0.06 * g)
        h2, t2 = _bone_vec(f"shin_{side}")
        _tube(bm, h2, t2, 0.055 * g, 0.05 * g)
        bm = b.part(f"foot_{side}", boot_mat)
        h3, t3 = _bone_vec(f"foot_{side}")
        _tube(bm, h3 + Vector((0, 0.02, 0)), t3, 0.05 * g, 0.045 * g, 7)
    # head + face: skin ball with a dark eye-shadow slit for depth
    bm = b.part("head", skin_mat)
    _ball(bm, (0, 0.02, 1.6), 0.105 * g)
    bm = b.part("head", "M_iron")
    V.add_box(bm, (-0.055 * g, 0.088 * g, 1.607), (0.055 * g, 0.13 * g, 1.64))
    if hood == "closed":
        # sealed wax cone — the faceless penitents
        bm = b.part("head", robe_mat)
        _tube(bm, Vector((0, -0.02, 1.46)), Vector((0, 0.0, 1.62)), 0.155 * g, 0.16 * g, 10, 1.05)
        _tube(bm, Vector((0, 0.0, 1.62)), Vector((0, 0.05, 1.82)), 0.15 * g, 0.02 * g, 10)
    elif hood:
        # open cowl: collar ring below the chin, arc strip around the face
        bm = b.part("head", robe_mat)
        _tube(bm, Vector((0, -0.02, 1.46)), Vector((0, 0.0, 1.53)), 0.155 * g, 0.148 * g, 10, 1.04)
        _arc_tube(bm, Vector((0, -0.01, 1.52)), Vector((0, 0.045, 1.80)), 0.148 * g, 0.03 * g, 9, gap=0.95)
    if skirt:
        # tabard skirt: short cone from hips — legs stay readable
        bm = b.part("hips", robe_mat)
        _tube(bm, Vector((0, 0, 0.92)), Vector((0, 0, 0.92 - skirt_len)), 0.175 * g, 0.24 * g, 12)
    return b


def hero(arm):
    b = BodyBuilder("hero")
    common_body(b, "M_robe", "M_wax", "M_leather")
    # satchel on hip
    bm = b.part("hips", "M_leather")
    V.add_box(bm, (0.10, -0.19, 0.86), (0.26, -0.05, 1.02))
    # pauldron caps
    for side, s in (("r", 1), ("l", -1)):
        bm = b.part(f"uarm_{side}", "M_leather")
        _ball(bm, (s * 0.235, 0, 1.41), 0.085)
    return b.finalize(arm)


def ward(arm):
    b = BodyBuilder("ward")
    common_body(b, "M_wraith", "M_wraith", "M_iron", hood=False, skirt=True, skirt_len=0.42, girth=1.08)
    # cuirass + pauldrons
    bm = b.part("chest", "M_iron")
    _tube(bm, Vector((0, 0, 1.22)), Vector((0, 0, 1.49)), 0.19, 0.16, 10, 1.05)
    for side, s in (("r", 1), ("l", -1)):
        bm = b.part(f"uarm_{side}", "M_iron")
        _ball(bm, (s * 0.24, 0, 1.42), 0.1)
    return b.finalize(arm)


def penitent(arm):
    b = BodyBuilder("penitent")
    common_body(b, "M_wax", "M_wax", "M_wax", hood="closed", skirt=True, skirt_len=0.5, girth=1.05)
    return b.finalize(arm, lumpy=0.045, seed=77)


def giant(arm):
    b = BodyBuilder("giant")
    common_body(b, "M_robe_boss", "M_wax", "M_leather", hood=True, skirt=True, skirt_len=0.55, girth=1.35)
    # bell-rope harness
    bm = b.part("chest", "M_leather")
    _tube(bm, Vector((0, 0, 1.3)), Vector((0, 0, 1.4)), 0.27, 0.25, 10)
    return b.finalize(arm, lumpy=0.02, seed=31)


def sister(arm):
    b = BodyBuilder("sister")
    common_body(b, "M_habit", "M_wax", "M_habit", hood=True, skirt=True, skirt_len=0.55)
    # long habit sleeves already; apron
    bm = b.part("spine", "M_leather")
    V.add_box(bm, (-0.12, 0.13, 0.95), (0.12, 0.18, 1.25))
    return b.finalize(arm)


ARCHETYPES = {
    "skel_hero": hero,
    "skel_ward": ward,
    "skel_penitent": penitent,
    "skel_giant": giant,
    "skel_sister": sister,
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
