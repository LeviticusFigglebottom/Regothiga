"""Vigil's End kit: the drowned shrine-isle across the mere, where the
kingdom's first lantern burns. Z up; exporter maps Z->Y.
"""
import math
import random
import bmesh
from mathutils import Vector

import vglib as V


def vigil_brazier():
    """Watchfire of the Nine: a squat shrine plinth bearing a wide bronze
    bowl, coals waiting for the flame (glory-gated ember glow reads as
    rekindled). The Watchfires puzzle interacts with these. Solid."""
    objs = []
    bm = bmesh.new()
    V.add_box(bm, (-0.6, -0.6, 0.0), (0.6, 0.6, 0.28))
    V.add_box(bm, (-0.42, -0.42, 0.28), (0.42, 0.42, 0.95))
    V.add_box(bm, (-0.52, -0.52, 0.95), (0.52, 0.52, 1.08))
    objs.append(V.bm_to_object(bm, "watch_plinth", ("M_stone_trim",)))
    bowl = V.loft_rings("watch_bowl", [(0.30, 1.06, 10, 0), (0.55, 1.22, 10, 0),
                                       (0.58, 1.34, 10, 0), (0.52, 1.38, 10, 0)],
                        "M_bronze", cap_bottom=True, cap_top=False)
    objs.append(bowl)
    coals = V.loft_rings("watch_coals", [(0.46, 1.3, 9, 0), (0.28, 1.42, 9, 0), (0.06, 1.46, 9, 0)],
                         "M_ember")
    objs.append(coals)
    return objs, {"size": [1.3, 1.3, 1.5], "origin": "bottom-center"}


def half_arch_sunk(seed=7):
    """A drowned processional arch: one standing jamb and a broken sweep
    reaching over the water, barnacled low. Solid. Origin bottom-center of
    the jamb; the sweep reaches toward +X."""
    rng = random.Random(seed)
    objs = []
    bm = bmesh.new()
    V.add_box(bm, (-0.45, -0.45, -1.2), (0.45, 0.45, 3.4))          # jamb (roots below floor)
    obj = V.bm_to_object(bm, "arch_jamb", ("M_stone",))
    obj.rotation_euler = (rng.uniform(-0.04, 0.04), rng.uniform(-0.02, 0.06), 0)
    objs.append(obj)
    arch = V.pointed_arch(3.6, 1.4, 10, 3.2)
    path = []
    for (x, y) in arch:
        if x <= 0.6:                                                # broken: only the near half
            path.append((x + 1.8, 0.0, y))
    prof = V.chamfer_rect_profile(0.34, 0.42, 0.06)
    sweep = V.sweep_profile("arch_sweep", path, prof, "M_stone_trim",
                            up_hint=Vector((0, 1, 0)))
    objs.append(sweep)
    return objs, {"size": [3.4, 1.0, 4.8], "origin": "bottom-center"}


def shrine_aedicule():
    """The First Light: a stepped shrine baldachin — four colonnettes under a
    pyramidal canopy, a gilt finial, and the flame core that never went out
    (M_ember + M_gold, glory-gated). The isle's centrepiece. Solid."""
    objs = []
    bm = bmesh.new()
    V.add_box(bm, (-1.5, -1.5, 0.0), (1.5, 1.5, 0.3))
    V.add_box(bm, (-1.15, -1.15, 0.3), (1.15, 1.15, 0.56))
    objs.append(V.bm_to_object(bm, "shrine_steps", ("M_stone",)))
    for sx in (-0.85, 0.85):
        for sy in (-0.85, 0.85):
            col = V.loft_rings("shrine_col", [(0.13, 0.56, 8, 0), (0.10, 0.7, 8, 0),
                                              (0.09, 2.5, 8, 0), (0.12, 2.66, 8, 0)],
                               "M_stone_trim")
            col.location = (sx, sy, 0)
            objs.append(col)
    bm = bmesh.new()
    V.add_box(bm, (-1.05, -1.05, 2.66), (1.05, 1.05, 2.9))
    objs.append(V.bm_to_object(bm, "shrine_cap", ("M_stone_trim",)))
    roof = V.loft_rings("shrine_roof", [(1.25, 2.9, 4, 0.785), (0.06, 3.9, 4, 0.785)],
                        "M_stone", cap_bottom=True, cap_top=True)
    objs.append(roof)
    fin = V.loft_rings("shrine_finial", [(0.05, 3.9, 6, 0), (0.14, 4.12, 6, 0), (0.02, 4.42, 6, 0)],
                       "M_gold")
    objs.append(fin)
    # the flame core on its altar block
    bm = bmesh.new()
    V.add_box(bm, (-0.4, -0.4, 0.56), (0.4, 0.4, 1.1))
    objs.append(V.bm_to_object(bm, "shrine_altar", ("M_stone_trim",)))
    core = V.loft_rings("first_light", [(0.16, 1.1, 8, 0), (0.3, 1.45, 8, 0.4),
                                        (0.1, 1.9, 8, 0.8), (0.02, 2.2, 8, 1.2)],
                        "M_ember")
    objs.append(core)
    halo = V.loft_rings("light_halo", [(0.36, 1.5, 10, 0), (0.38, 1.56, 10, 0)],
                        "M_gold", cap_bottom=False, cap_top=False)
    objs.append(halo)
    return objs, {"size": [3.0, 3.0, 4.5], "origin": "bottom-center"}


def lantern_crook():
    """The First Vigilant's lantern-crook: a tall iron staff hooked at the
    head, a caged vigil-lantern swinging from the hook. Grip at origin,
    business end +Z, like every weapon."""
    objs = []
    staff = V.loft_rings("crook_staff", [(0.045, -0.55, 7, 0), (0.04, 1.55, 7, 0)], "M_iron")
    objs.append(staff)
    # the hook: a swept curve breaking off the staff head (curling toward -X so
    # in hand_r it hangs outward away from the wielder's body)
    path = [(0.0, 0, 1.50), (-0.05, 0, 1.72), (-0.17, 0, 1.80), (-0.30, 0, 1.74), (-0.34, 0, 1.58)]
    prof = V.circle_profile(0.035, 7)
    objs.append(V.sweep_profile("crook_hook", path, prof, "M_iron",
                                up_hint=Vector((0, 1, 0))))
    # caged lantern hanging from the hook tip
    bm = bmesh.new()
    V.add_box(bm, (-0.37, -0.015, 1.42), (-0.31, 0.015, 1.60))        # hanger link
    V.add_box(bm, (-0.44, -0.1, 1.06), (-0.24, 0.1, 1.14))            # cage base
    V.add_box(bm, (-0.44, -0.1, 1.38), (-0.24, 0.1, 1.44))            # cage top
    for cx in (-0.42, -0.25):
        for cy in (-0.09, 0.09):
            V.add_box(bm, (cx - 0.012, cy - 0.012, 1.14), (cx + 0.012, cy + 0.012, 1.38))
    objs.append(V.bm_to_object(bm, "crook_cage", ("M_iron",)))
    flame = V.loft_rings("crook_flame", [(0.05, 1.14, 6, 0), (0.08, 1.22, 6, 0.3),
                                         (0.02, 1.34, 6, 0.7)], "M_ember")
    flame.location = (-0.34, 0, 0)
    objs.append(flame)
    return objs, {"size": [0.5, 0.25, 2.4], "origin": "grip"}


def ferry_skiff():
    """The Ferryman's flat skiff, moored and waiting: recessed planked punt hull
    with raked prow and stern, gunwale rails, floor duckboards, two thwart benches,
    prow iron lantern hook, and a shipped iron-shod punt pole. Solid dressing at
    the jetties. Origin bottom-center."""
    objs = []
    bm = bmesh.new()
    # Flat-bottomed recessed punt hull with raked bow (+X) and stern (-X)
    V.add_box(bm, (-1.45, -0.58, 0.14), (1.25, 0.58, 0.26))           # bilge floor
    V.add_box(bm, (-1.70, -0.46, 0.22), (-1.40, 0.46, 0.64))          # raked stern transom
    V.add_box(bm, (1.20, -0.46, 0.22), (1.56, 0.46, 0.66))            # raked bow swim-head
    V.add_box(bm, (1.52, -0.30, 0.30), (1.72, 0.30, 0.68))            # bow prow nose
    # Port and starboard hull strakes + raised gunwale rubbing strips
    for sy in (-1, 1):
        y_in, y_out = (sy * 0.50, sy * 0.62) if sy > 0 else (sy * 0.62, sy * 0.50)
        V.add_box(bm, (-1.50, y_in, 0.20), (1.35, y_out, 0.64))
        V.add_box(bm, (-1.58, y_in - 0.02 * sy, 0.60), (1.45, y_out + 0.03 * sy, 0.68))
    # Internal ribs & floor duckboards
    for rx in (-1.05, -0.35, 0.35, 0.95):
        V.add_box(bm, (rx - 0.04, -0.50, 0.26), (rx + 0.04, 0.50, 0.34))
    objs.append(V.bm_to_object(bm, "skiff_hull", ("M_wood",)))

    # Thwart benches & shipped ferryman's pole
    bm_fit = bmesh.new()
    for tx in (-0.65, 0.45):
        V.add_box(bm_fit, (tx - 0.18, -0.54, 0.48), (tx + 0.18, 0.54, 0.56))
    # Shipped punt pole resting diagonally across the thwarts
    V.add_box(bm_fit, (-1.58, -0.08, 0.57), (1.42, -0.01, 0.63))
    objs.append(V.bm_to_object(bm_fit, "skiff_fittings", ("M_wood",)))

    # Iron prow mooring ring, pole shoe, and low bow lantern post
    bm_iron = bmesh.new()
    V.add_box(bm_iron, (1.40, -0.09, 0.56), (1.54, 0.0, 0.64))        # pole iron shoe
    V.add_box(bm_iron, (1.58, -0.03, 0.66), (1.64, 0.03, 1.08))       # bow lantern post
    V.add_box(bm_iron, (1.54, -0.08, 1.04), (1.72, 0.08, 1.10))       # lantern cap
    objs.append(V.bm_to_object(bm_iron, "skiff_iron", ("M_iron",)))
    return objs, {"size": [3.4, 1.3, 1.1], "origin": "bottom-center"}


BUILDERS = {
    "vigil_brazier": vigil_brazier,
    "half_arch_sunk": half_arch_sunk,
    "shrine_aedicule": shrine_aedicule,
    "lantern_crook": lantern_crook,
    "ferry_skiff": ferry_skiff,
}
