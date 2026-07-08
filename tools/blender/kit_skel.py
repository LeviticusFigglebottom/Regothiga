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

    def joint(self, bone_a, bone_b, mat):
        """Chunk weighted 50/50 between two bones — smooth hinge skin."""
        bm = bmesh.new()
        self.chunks.append((bm, (bone_a, bone_b), mat))
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
        bm = b.joint("chest", f"uarm_{side}", robe_mat)
        _ball(bm, (s * 0.225, 0, 1.40), 0.075 * g)
        bm = b.part(f"uarm_{side}", robe_mat)
        h, t = _bone_vec(f"uarm_{side}")
        _tube(bm, h, t, 0.065 * g, 0.055 * g)
        bm = b.joint(f"uarm_{side}", f"farm_{side}", robe_mat)
        _ball(bm, tuple(t), 0.055 * g)
        bm = b.part(f"farm_{side}", robe_mat)
        h2, t2 = _bone_vec(f"farm_{side}")
        _tube(bm, h2, t2, 0.052 * g, 0.062 * g)   # sleeve cuff flare
        bm = b.part(f"hand_{side}", skin_mat)
        h3, t3 = _bone_vec(f"hand_{side}")
        _tube(bm, h3, t3, 0.045 * g, 0.035 * g, 7)
    # legs
    for side in ("l", "r"):
        bm = b.joint("hips", f"thigh_{side}", robe_mat)
        h, t = _bone_vec(f"thigh_{side}")
        _ball(bm, tuple(h + Vector((0, 0, -0.01))), 0.085 * g)
        bm = b.part(f"thigh_{side}", robe_mat)
        _tube(bm, h, t, 0.08 * g, 0.06 * g)
        bm = b.joint(f"thigh_{side}", f"shin_{side}", boot_mat)
        _ball(bm, tuple(t), 0.06 * g)
        bm = b.part(f"shin_{side}", boot_mat)
        h2, t2 = _bone_vec(f"shin_{side}")
        _tube(bm, h2, t2, 0.055 * g, 0.05 * g)
        bm = b.part(f"foot_{side}", boot_mat)
        h3, t3 = _bone_vec(f"foot_{side}")
        _tube(bm, h3 + Vector((0, 0.02, 0)), t3, 0.05 * g, 0.045 * g, 7)
    # neck + head + face
    bm = b.joint("chest", "head", skin_mat)
    _tube(bm, Vector((0, 0, 1.42)), Vector((0, 0.01, 1.52)), 0.055 * g, 0.05 * g, 7)
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


def sexton(arm):
    """The Sexton: stout gravedigger of the Basilica. Flat cap, leather
    apron, sleeves rolled (bare forearms), heavy boots."""
    b = BodyBuilder("sexton")
    common_body(b, "M_robe", "M_wax", "M_leather", hood=False, skirt=True,
                skirt_len=0.26, girth=1.18)
    # leather apron front
    bm = b.part("spine", "M_leather")
    V.add_box(bm, (-0.15, 0.13, 0.72), (0.15, 0.19, 1.3))
    # flat cap
    bm = b.part("head", "M_leather")
    _tube(bm, Vector((0, 0.01, 1.68)), Vector((0, 0.02, 1.735)), 0.135, 0.115, 9)
    _tube(bm, Vector((0, 0.06, 1.7)), Vector((0, 0.09, 1.71)), 0.06, 0.03, 7)
    # bare forearms: overwrite sleeves visually with skin-toned wraps
    for side in ("l", "r"):
        bm = b.part(f"farm_{side}", "M_wax")
        h, t = _bone_vec(f"farm_{side}")
        _tube(bm, h + (t - h) * 0.35, t, 0.055, 0.05, 7)
    return b.finalize(arm, lumpy=0.012, seed=19)


def chorister(arm):
    """Chorister of the Last Choir: slender, pale, open cowl and a high
    collar. Ranged singer — the body sways more than it strides."""
    b = BodyBuilder("chorister")
    common_body(b, "M_wraith", "M_wax", "M_wraith", hood=True, skirt=True,
                skirt_len=0.6, girth=0.9)
    # high choir collar
    bm = b.part("chest", "M_habit")
    _tube(bm, Vector((0, 0, 1.4)), Vector((0, -0.01, 1.5)), 0.16, 0.17, 10)
    # hymnal chained to the belt
    bm = b.part("hips", "M_leather")
    V.add_box(bm, (-0.2, -0.14, 0.9), (-0.06, -0.05, 1.02))
    return b.finalize(arm, seed=43)


def precentress(arm):
    """The Precentress: mistress of the choir. Tall gilt wimple, boss robes,
    censer chains. Scaled up ~1.3x at runtime."""
    b = BodyBuilder("precentress")
    common_body(b, "M_robe_boss", "M_wax", "M_robe_boss", hood=True, skirt=True,
                skirt_len=0.62, girth=0.98)
    # tall two-horn wimple crown
    bm = b.part("head", "M_gold")
    _tube(bm, Vector((0, 0.0, 1.7)), Vector((0, -0.03, 2.02)), 0.09, 0.015, 8)
    _tube(bm, Vector((0, 0.0, 1.66)), Vector((0, 0.0, 1.72)), 0.125, 0.1, 8)
    # censer chains crossing the chest
    bm = b.part("chest", "M_bronze")
    _tube(bm, Vector((0.15, -0.1, 1.42)), Vector((-0.13, -0.12, 1.1)), 0.018, 0.018, 5)
    _tube(bm, Vector((-0.15, -0.1, 1.42)), Vector((0.13, -0.12, 1.1)), 0.018, 0.018, 5)
    return b.finalize(arm, seed=61)


ARCHETYPES = {
    "skel_hero": hero,
    "skel_ward": ward,
    "skel_penitent": penitent,
    "skel_giant": giant,
    "skel_sister": sister,
    "skel_sexton": sexton,
    "skel_chorister": chorister,
    "skel_precentress": precentress,
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


def shroud(arm):
    """Shroudbound: a swift dead thing still wrapped for burial. Bandage
    bands cross the sealed cowl; it runs low and quick."""
    b = BodyBuilder("shroud")
    common_body(b, "M_shroud", "M_shroud", "M_shroud", hood="closed", skirt=True,
                skirt_len=0.66, girth=0.86)
    for z0 in (1.0, 1.22, 1.38):
        bm = b.part("chest" if z0 > 1.1 else "spine", "M_leather")
        _tube(bm, Vector((0, 0, z0)), Vector((0, 0, z0 + 0.045)), 0.165 * 0.86, 0.165 * 0.86, 9)
    return b.finalize(arm, lumpy=0.03, seed=97)


def bellox(arm):
    """Bourdon, the Bell-Ox: a yoked hulk crowned with a horned bone mask.
    Runtime-scaled ~1.7x; drags a cracked bell by its harness."""
    b = BodyBuilder("bellox")
    common_body(b, "M_robe_boss", "M_wax", "M_leather", hood=False, skirt=True,
                skirt_len=0.5, girth=1.5)
    # bone ox-mask: muzzle + horn tubes
    bm = b.part("head", "M_bone")
    V.add_box(bm, (-0.09, 0.08, 1.5), (0.09, 0.24, 1.64))
    _ball(bm, (0, 0.03, 1.62), 0.13)
    for s in (1, -1):
        _tube(bm, Vector((s * 0.1, 0.0, 1.66)), Vector((s * 0.34, 0.1, 1.82)), 0.05, 0.012, 6)
    # yoke beam across the shoulders + harness ring
    bm = b.part("chest", "M_wood")
    V.add_box(bm, (-0.62, -0.1, 1.46), (0.62, 0.06, 1.58))
    bm = b.part("chest", "M_bronze")
    _tube(bm, Vector((0, -0.12, 1.3)), Vector((0, -0.12, 1.42)), 0.3, 0.28, 10)
    return b.finalize(arm, lumpy=0.02, seed=53)


ARCHETYPES["skel_shroud"] = shroud


def echo(arm):
    """Gilded Echo: a singer's afterimage that haunts the REMEMBERED world —
    pale wraith weave under gilt diadem, collar and belt. M_gold's glory-gated
    emission makes it shimmer exactly where it hunts."""
    b = BodyBuilder("echo")
    common_body(b, "M_wraith", "M_wax", "M_wraith", hood=True, skirt=True,
                skirt_len=0.58, girth=0.84)
    bm = b.part("head", "M_gold")            # gilt diadem
    _tube(bm, Vector((0, 0, 1.62)), Vector((0, 0, 1.68)), 0.145, 0.15, 10)
    bm = b.part("chest", "M_gold")           # high gilt collar
    _tube(bm, Vector((0, 0, 1.42)), Vector((0, -0.01, 1.5)), 0.15, 0.165, 10)
    bm = b.part("hips", "M_gold")            # belt
    _tube(bm, Vector((0, 0, 0.98)), Vector((0, 0, 1.04)), 0.17, 0.17, 10)
    return b.finalize(arm, seed=131)


ARCHETYPES["skel_echo"] = echo


def herald(arm):
    """Drowned Herald: the gate's crier, still calling the toll. Deep cowl,
    bronze horn slung across the chest, heavy tabard over drowned-dark weave."""
    b = BodyBuilder("herald")
    common_body(b, "M_robe", "M_wax", "M_robe", hood="closed", skirt=True,
                skirt_len=0.64, girth=0.95)
    # tabard front panel
    bm = b.part("chest", "M_cloth")
    V.add_box(bm, (-0.16, -0.2, 0.95), (0.16, -0.14, 1.45))
    # slung bronze horn (a curved tube across the chest)
    bm = b.part("chest", "M_bronze")
    _tube(bm, Vector((-0.2, -0.2, 1.05)), Vector((0.14, -0.26, 1.3)), 0.05, 0.09, 8)
    return b.finalize(arm, seed=173)


ARCHETYPES["skel_herald"] = herald


def mire(arm):
    """Mirebound: the marsh's drowned dead — broad, mud-heavy, dragging a
    weight of sodden grave-wrappings. Slow, and very hard to put down."""
    b = BodyBuilder("mire")
    common_body(b, "M_stone_dark", "M_leather", "M_stone_dark", hood="closed",
                skirt=True, skirt_len=0.72, girth=1.15)
    # sodden mantle plastered across the shoulders
    bm = b.part("chest", "M_leather")
    _tube(bm, Vector((0, 0, 1.34)), Vector((0, 0, 1.5)), 0.2, 0.24, 9)
    return b.finalize(arm, lumpy=0.05, seed=211)


ARCHETYPES["skel_mire"] = mire



ARCHETYPES["skel_bellox"] = bellox


def wretch(arm):
    """Lantern Wretch: a pilgrim who reached the Last Shore and kept walking
    the shallows — gaunt, salt-bleached weave, a little dead lantern chained
    at the hip that only the remembered world can light."""
    b = BodyBuilder("wretch")
    common_body(b, "M_wraith", "M_wax", "M_robe", hood="closed", skirt=True,
                skirt_len=0.6, girth=0.78)
    # the hip lantern: iron box + ember core, slung on a short chain
    bm = b.part("hips", "M_iron")
    V.add_box(bm, (0.16, -0.05, 0.78), (0.28, 0.05, 0.94))
    V.add_box(bm, (0.2, -0.015, 0.94), (0.24, 0.015, 1.05))
    bm = b.part("hips", "M_ember")
    V.add_box(bm, (0.185, -0.03, 0.81), (0.255, 0.03, 0.9))
    return b.finalize(arm, seed=307)


ARCHETYPES["skel_wretch"] = wretch
