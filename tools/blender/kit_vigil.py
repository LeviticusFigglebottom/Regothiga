"""Vigil's End kit: the drowned shrine-isle across the mere, where the
kingdom's first lantern burns. Z up; exporter maps Z->Y.
"""
import math
import random
import bmesh
from mathutils import Vector

import vglib as V


def vigil_brazier():
    """Watchfire of the Nine: a carved Gothic stone shrine plinth with stepped
    base, recessed dark-stone panels, corner pilasters, wrought-iron bowl
    brackets, and a wide fluted bronze bowl with gilt rim and glowing coals. Solid."""
    objs = []
    bm = bmesh.new()
    # Stepped chamfered stone plinth & cornice
    V.add_box(bm, (-0.62, -0.62, 0.0), (0.62, 0.62, 0.16))
    V.add_box(bm, (-0.54, -0.54, 0.16), (0.54, 0.54, 0.28))
    V.add_box(bm, (-0.50, -0.50, 0.88), (0.50, 0.50, 0.96))
    V.add_box(bm, (-0.56, -0.56, 0.96), (0.56, 0.56, 1.08))
    # 4 corner pilasters framing recessed blind-arcade sides
    for sx in (-0.38, 0.38):
        for sy in (-0.38, 0.38):
            V.add_box(bm, (sx - 0.06, sy - 0.06, 0.28), (sx + 0.06, sy + 0.06, 0.88))
    objs.append(V.bm_to_object(bm, "watch_plinth", ("M_stone_trim",)))

    # Recessed dark stone shaft core
    bm_core = bmesh.new()
    V.add_box(bm_core, (-0.39, -0.39, 0.28), (0.39, 0.39, 0.88))
    objs.append(V.bm_to_object(bm_core, "watch_core", ("M_stone_dark",)))

    # Wrought-iron corner scroll brackets supporting the bronze bowl
    bm_iron = bmesh.new()
    for sx, sy in ((-0.42, 0.0), (0.42, 0.0), (0.0, -0.42), (0.0, 0.42)):
        wx = 0.09 if sx != 0 else 0.035
        wy = 0.09 if sy != 0 else 0.035
        V.add_box(bm_iron, (sx - wx, sy - wy, 0.98), (sx + wx, sy + wy, 1.24))
    objs.append(V.bm_to_object(bm_iron, "watch_brackets", ("M_iron",)))

    bowl = V.loft_rings(
        "watch_bowl",
        [
            (0.26, 1.06, 16, 0),
            (0.34, 1.12, 16, 0),
            (0.56, 1.24, 16, 0),
            (0.60, 1.35, 16, 0),
            (0.54, 1.39, 16, 0),
            (0.49, 1.39, 16, 0),
            (0.45, 1.26, 16, 0),
        ],
        "M_bronze",
        cap_bottom=True,
        cap_top=True,
    )
    objs.append(bowl)
    rim = V.loft_rings(
        "watch_rim",
        [
            (0.54, 1.33, 16, 0),
            (0.618, 1.33, 16, 0),
            (0.618, 1.395, 16, 0),
            (0.54, 1.395, 16, 0),
            (0.54, 1.33, 16, 0),
        ],
        "M_gold",
        cap_bottom=False,
        cap_top=False,
    )
    objs.append(rim)
    coals = V.loft_rings(
        "watch_coals",
        [
            (0.49, 1.28, 14, 0),
            (0.36, 1.38, 14, 0.2),
            (0.18, 1.45, 14, 0.4),
            (0.04, 1.49, 14, 0.6),
        ],
        "M_ember",
    )
    objs.append(coals)
    return objs, {"size": [1.3, 1.3, 1.5], "origin": "bottom-center"}


def half_arch_sunk(seed=7):
    """A drowned processional arch: one standing jamb with stepped plinth,
    corner pilaster stiles, moulded impost capital, barnacled water-line crust,
    and a broken sweep reaching over the water. Solid. Origin bottom-center of
    the jamb; the sweep reaches toward +X."""
    rng = random.Random(seed)
    objs = []
    bm = bmesh.new()
    V.add_box(bm, (-0.54, -0.54, -1.2), (0.54, 0.54, 0.35))           # submerged plinth
    V.add_box(bm, (-0.48, -0.48, 0.35), (0.48, 0.48, 0.65))           # water-line plinth step
    V.add_box(bm, (-0.42, -0.42, 0.65), (0.42, 0.42, 3.12))           # shaft core
    for sx in (-0.38, 0.38):
        for sy in (-0.38, 0.38):
            V.add_box(bm, (sx - 0.07, sy - 0.07, 0.65), (sx + 0.07, sy + 0.07, 3.12))
    obj = V.bm_to_object(bm, "arch_jamb", ("M_stone",))
    tilt = (rng.uniform(-0.04, 0.04), rng.uniform(-0.02, 0.06), 0)
    obj.rotation_euler = tilt
    objs.append(obj)

    # Moulded impost capital & mid stringcourse band
    bm_trim = bmesh.new()
    V.add_box(bm_trim, (-0.47, -0.47, 1.85), (0.47, 0.47, 1.98))
    V.add_box(bm_trim, (-0.48, -0.48, 3.08), (0.48, 0.48, 3.24))
    V.add_box(bm_trim, (-0.54, -0.54, 3.24), (0.54, 0.54, 3.42))
    cap = V.bm_to_object(bm_trim, "arch_impost", ("M_stone_trim",))
    cap.rotation_euler = tilt
    objs.append(cap)

    # Barnacle and dark silt encrustation at the water-line
    bm_barn = bmesh.new()
    for _ in range(14):
        ang = rng.uniform(0, math.tau)
        rad = rng.uniform(0.42, 0.54)
        bx, by = math.cos(ang) * rad, math.sin(ang) * rad
        bz = rng.uniform(-0.15, 0.72)
        bw = rng.uniform(0.08, 0.16)
        bh = rng.uniform(0.08, 0.22)
        V.add_box(bm_barn, (bx - bw, by - bw, bz), (bx + bw, by + bw, bz + bh))
    barn = V.bm_to_object(bm_barn, "arch_barnacles", ("M_stone_dark",))
    barn.rotation_euler = tilt
    objs.append(barn)

    arch = V.pointed_arch(3.6, 1.4, 12, 3.2)
    path = []
    for (x, y) in arch:
        if x <= 0.6:                                                # broken: only the near half
            path.append((x + 1.8, 0.0, y))
    prof = V.chamfer_rect_profile(0.36, 0.44, 0.06)
    sweep = V.sweep_profile("arch_sweep", path, prof, "M_stone_trim",
                            up_hint=Vector((0, 1, 0)))
    objs.append(sweep)
    return objs, {"size": [3.4, 1.0, 4.8], "origin": "bottom-center"}


def shrine_aedicule():
    """The First Light: a stepped Gothic shrine ciborium — four fluted columns
    with moulded bases and capitals under a gabled canopy with corner pinnacles,
    a gilt sun-finial, and the eternal flame core above a carved altar. Solid."""
    objs = []
    bm = bmesh.new()
    # 3-step stone stylobate platform with bevelled coping
    V.add_box(bm, (-1.52, -1.52, 0.0), (1.52, 1.52, 0.20))
    V.add_box(bm, (-1.32, -1.32, 0.20), (1.32, 1.32, 0.38))
    V.add_box(bm, (-1.14, -1.14, 0.38), (1.14, 1.14, 0.56))
    objs.append(V.bm_to_object(bm, "shrine_steps", ("M_stone",)))

    # 4 fluted 12-sided columns with Attic bases and flared Gothic capitals
    for sx in (-0.86, 0.86):
        for sy in (-0.86, 0.86):
            col = V.loft_rings(
                "shrine_col",
                [
                    (0.16, 0.56, 12, 0),
                    (0.15, 0.66, 12, 0),
                    (0.105, 0.74, 12, 0),
                    (0.095, 2.42, 12, 0),
                    (0.135, 2.56, 12, 0),
                    (0.165, 2.66, 12, 0),
                ],
                "M_stone_trim",
            )
            col.location = (sx, sy, 0)
            objs.append(col)

    # Entablature architrave, frieze, overhanging cornice, and 4 corner pinnacles
    bm = bmesh.new()
    V.add_box(bm, (-1.04, -1.04, 2.66), (1.04, 1.04, 2.78))
    V.add_box(bm, (-1.12, -1.12, 2.78), (1.12, 1.12, 2.92))
    # Recessed dark frieze band & corner pinnacle spires
    for sx in (-1.02, 1.02):
        for sy in (-1.02, 1.02):
            V.add_box(bm, (sx - 0.08, sy - 0.08, 2.92), (sx + 0.08, sy + 0.08, 3.24))
            V.add_box(bm, (sx - 0.04, sy - 0.04, 3.24), (sx + 0.04, sy + 0.04, 3.42))
    objs.append(V.bm_to_object(bm, "shrine_cap", ("M_stone_trim",)))

    roof = V.loft_rings(
        "shrine_roof",
        [
            (1.32, 2.92, 4, math.pi / 4),
            (0.82, 3.32, 4, math.pi / 4),
            (0.36, 3.68, 4, math.pi / 4),
            (0.06, 3.96, 4, math.pi / 4),
        ],
        "M_stone",
        cap_bottom=True,
        cap_top=True,
    )
    objs.append(roof)
    fin = V.loft_rings(
        "shrine_finial",
        [
            (0.06, 3.94, 12, 0),
            (0.04, 4.06, 12, 0),
            (0.16, 4.18, 12, 0),
            (0.05, 4.30, 12, 0),
            (0.015, 4.46, 12, 0),
        ],
        "M_gold",
    )
    objs.append(fin)

    # Carved central shrine altar with pilaster corners & bronze fire-basin
    bm = bmesh.new()
    V.add_box(bm, (-0.46, -0.46, 0.56), (0.46, 0.46, 0.66))
    V.add_box(bm, (-0.38, -0.38, 0.66), (0.38, 0.38, 1.00))
    V.add_box(bm, (-0.45, -0.45, 1.00), (0.45, 0.45, 1.10))
    for sx in (-0.36, 0.36):
        for sy in (-0.36, 0.36):
            V.add_box(bm, (sx - 0.045, sy - 0.045, 0.66), (sx + 0.045, sy + 0.045, 1.00))
    objs.append(V.bm_to_object(bm, "shrine_altar", ("M_stone_trim",)))

    basin = V.loft_rings(
        "shrine_basin",
        [
            (0.24, 1.10, 14, 0),
            (0.34, 1.18, 14, 0),
            (0.34, 1.23, 14, 0),
            (0.28, 1.23, 14, 0),
            (0.22, 1.16, 14, 0),
        ],
        "M_bronze",
        cap_bottom=True,
        cap_top=True,
    )
    objs.append(basin)
    core = V.loft_rings(
        "first_light",
        [
            (0.18, 1.18, 12, 0),
            (0.32, 1.48, 12, 0.35),
            (0.16, 1.85, 12, 0.7),
            (0.06, 2.10, 12, 1.05),
            (0.015, 2.25, 12, 1.4),
        ],
        "M_ember",
    )
    objs.append(core)
    halo = V.loft_rings(
        "light_halo",
        [
            (0.38, 1.49, 16, 0),
            (0.41, 1.53, 16, 0),
            (0.38, 1.57, 16, 0),
            (0.35, 1.53, 16, 0),
            (0.38, 1.49, 16, 0),
        ],
        "M_gold",
        cap_bottom=False,
        cap_top=False,
    )
    objs.append(halo)
    return objs, {"size": [3.0, 3.0, 4.5], "origin": "bottom-center"}


def lantern_crook():
    """The First Vigilant's lantern-crook: a tall forged-iron staff with butt
    spike, brass grip rings, scrolled crook volute, and a cylindrical wrought-iron
    caged vigil-lantern swinging from the hook. Grip at origin, +Z up."""
    objs = []
    staff = V.loft_rings(
        "crook_staff",
        [
            (0.012, -0.62, 12, 0),
            (0.044, -0.50, 12, 0),
            (0.042, 0.40, 12, 0),
            (0.038, 1.46, 12, 0),
            (0.052, 1.52, 12, 0),
            (0.038, 1.56, 12, 0),
        ],
        "M_iron",
    )
    objs.append(staff)
    # Brass collar rings around the grip and neck
    bm_brass = bmesh.new()
    for z_ring in (-0.18, 0.18, 1.46):
        V.add_cyl(bm_brass, 0.0, 0.0, z_ring, 0.035, 0.048, n=12)
    objs.append(V.bm_to_object(bm_brass, "crook_brass", ("M_brass",)))

    # Scrolled crook hook breaking off the staff head toward -X
    path = [
        (0.0, 0, 1.52),
        (-0.02, 0, 1.66),
        (-0.08, 0, 1.78),
        (-0.19, 0, 1.82),
        (-0.30, 0, 1.75),
        (-0.34, 0, 1.60),
    ]
    prof = V.circle_profile(0.032, 10)
    objs.append(V.sweep_profile("crook_hook", path, prof, "M_iron", up_hint=Vector((0, 1, 0))))

    # Cylindrical wrought-iron caged vigil-lantern hanging from (-0.34, 0, 1.60)
    bm = bmesh.new()
    cx = -0.34
    V.add_cyl(bm, cx, 0.0, 1.46, 0.15, 0.014, n=8)    # suspension rod
    V.add_cyl(bm, cx, 0.0, 1.04, 0.04, 0.095, n=12)   # lantern floor pan
    V.add_cyl(bm, cx, 0.0, 1.08, 0.03, 0.115, n=12)   # lower cage ring
    V.add_cyl(bm, cx, 0.0, 1.36, 0.03, 0.118, n=12)   # upper cage ring
    V.add_cyl(bm, cx, 0.0, 1.39, 0.05, 0.085, n=12)   # conical roof tier 1
    V.add_cyl(bm, cx, 0.0, 1.44, 0.04, 0.042, n=12)   # conical roof tier 2
    for i in range(6):
        a = i * math.pi / 3.0
        bx = cx + 0.102 * math.cos(a)
        by = 0.102 * math.sin(a)
        V.add_cyl(bm, bx, by, 1.10, 0.27, 0.011, n=6)
    objs.append(V.bm_to_object(bm, "crook_cage", ("M_iron",)))

    flame = V.loft_rings(
        "crook_flame",
        [
            (0.045, 1.11, 10, 0),
            (0.078, 1.20, 10, 0.3),
            (0.048, 1.29, 10, 0.6),
            (0.012, 1.35, 10, 0.9),
        ],
        "M_ember",
    )
    flame.location = (cx, 0, 0)
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
