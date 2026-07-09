#!/usr/bin/env python3
"""Author data/areas/old_outskirts.json: the Old Outskirts, a half-timbered
hill town above the drowned canal — dense rowhouses with explorable
interiors, switchback streets climbing two terraces to a parish square,
and the gilded city ringing every horizon (the panorama sits centered
UNDER the district, so its middle rings crown every parapet line).

Deterministic; run after editing and re-audit:
    python3 tools/gen_outskirts.py && python3 tools/audit_areas.py old_outskirts

House module: 3 m storeys of burg_wall_3m panels; interior wooden stairs
run inside carved stairwell tiles, top edge flush with the tile's floor
edge (the last tread noses 0.4 m onto the slab), foot buried in the wall
base. Three-storey houses alternate flight direction per storey so no
flight climbs beneath its own ceiling slab.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "data", "areas", "old_outskirts.json")

P = []   # pieces
F = []   # fills
B = []   # extra boxes (terraces, parapets)
PR = []  # props
OA = []  # open_air_regions
SP = []  # spawners
PK = []  # pickups
ROWS = []


def wall_row(x0, x1, z0, z1, y, side, variants):
    """One storey of one house side. side letter = which face is exterior.
    variants: string or list, one of 'p'lain, 'w'indow, 'd'oor, '-' skip."""
    rot = {"N": 0, "S": 180, "W": 90, "E": -90}[side]
    kits = {"p": "burg_wall_3m", "w": "burg_wall_3m_win", "d": "burg_wall_3m_door"}
    if side in ("N", "S"):
        z = z0 if side == "N" else z1
        cs = [(x0 + 1.5 + 3 * i, z) for i in range(int(round((x1 - x0) / 3)))]
    else:
        x = x0 if side == "W" else x1
        cs = [(x, z0 + 1.5 + 3 * i) for i in range(int(round((z1 - z0) / 3)))]
    for i, (x, z) in enumerate(cs):
        v = variants[i]
        if v != "-":
            P.append({"kit": kits[v], "at": [x, y, z], "rot": rot})


def house(x0, z0, x1, z1, base, storeys, sides, stairwells=None, roof_rot=0,
          chimney=None):
    """A rowhouse. sides: dict side -> per-storey variant strings.
    stairwells: list of (tile_x0, tile_z0, axis) per storey gap; axis 'x'
    runs the flight west->east inside the tile (exit east), axis 'z' runs
    it south->north (exit north). Floors above each gap omit that tile."""
    for s in range(storeys):
        y = base + 3 * s
        for side, pat in sides.items():
            wall_row(x0, x1, z0, z1, y, side, pat[s])
    for s in range(1, storeys):
        y = base + 3 * s
        hole = stairwells[s - 1][:2] if stairwells and len(stairwells) >= s else None
        rects = []
        if hole:
            sx, sz = hole
            if sz > z0:
                rects.append(([x0, y, z0], [x1, y, sz]))
            if sz + 3 < z1:
                rects.append(([x0, y, sz + 3], [x1, y, z1]))
            if sx > x0:
                rects.append(([x0, y, sz], [sx, y, sz + 3]))
            if sx + 3 < x1:
                rects.append(([sx + 3, y, sz], [x1, y, sz + 3]))
        else:
            rects.append(([x0, y, z0], [x1, y, z1]))
        for mn, mx in rects:
            F.append({"kit": "burg_floor_3m", "min": mn, "max": mx, "step": 3})
            OA.append({"min": mn, "max": mx})
    if stairwells:
        for s, (sx, sz, axis) in enumerate(stairwells):
            y = base + 3 * s
            if axis == "x":   # ascend east, top flush at the tile's east edge
                P.append({"kit": "stair_wood_3m", "at": [sx - 0.31, y + 0.02, sz + 1.5], "rot": -90})
            else:             # ascend north, top flush at the tile's north edge
                P.append({"kit": "stair_wood_3m", "at": [sx + 1.5, y + 0.02, sz + 3.31], "rot": 0})
    top = base + 3 * storeys
    cx, cz = (x0 + x1) / 2, (z0 + z1) / 2
    if roof_rot in (0, 180):     # ridge along X
        sc = [round((x1 - x0 + 1) / 7.0, 3), 1, round((z1 - z0 + 1) / 7.0, 3)]
    else:                        # ridge along Z
        sc = [round((z1 - z0 + 1) / 7.0, 3), 1, round((x1 - x0 + 1) / 7.0, 3)]
    P.append({"kit": "roof_gable_7m", "at": [cx, top, cz], "rot": roof_rot, "scale": sc})
    if chimney:
        P.append({"kit": "chimney_stack", "at": [chimney[0], top + 0.9, chimney[1]], "rot": 0})


def main():
    d = json.load(open(PATH))

    # ---------------- terraces: two risers climbing away from the quay
    B_new = [b for b in d["boxes"]]
    B_new.append({"min": [-26, 0, -34], "max": [26, 2.4, -18], "mat": "M_stone",
                  "tag": "base", "walkable": True})
    B_new.append({"min": [-26, 0, -46], "max": [26, 4.8, -34], "mat": "M_stone",
                  "tag": "base", "walkable": True})
    # parapet along the plateau rim (three open sides; the quay wall holds the south)
    B_new.append({"min": [-60, 0, -50], "max": [60, 1.1, -49.6], "mat": "M_stone", "tag": "base"})
    B_new.append({"min": [-60, 0, -50], "max": [-59.6, 1.1, 12], "mat": "M_stone", "tag": "base"})
    B_new.append({"min": [59.6, 0, -50], "max": [60, 1.1, 12], "mat": "M_stone", "tag": "base"})
    OA.append({"min": [-26, 2.4, -34], "max": [26, 2.4, -18]})
    OA.append({"min": [-26, 4.8, -46], "max": [26, 4.8, -34]})

    # switchback grand stairs between the terraces, rails guarding each riser
    P.append({"kit": "stair_grand_4m", "at": [10, 2.42, -18], "rot": 180})
    P.append({"kit": "stair_grand_4m", "at": [-10, 4.82, -34], "rot": 180})
    ROWS.extend([
        {"kit": "balustrade_4m", "from": [-22, 2.4, -17.8], "dir": [1, 0, 0], "count": 8, "rot": 180},
        {"kit": "balustrade_4m", "from": [14, 2.4, -17.8], "dir": [1, 0, 0], "count": 3, "rot": 180},
        {"kit": "balustrade_4m", "from": [-4, 4.8, -33.8], "dir": [1, 0, 0], "count": 7, "rot": 180},
        {"kit": "balustrade_4m", "from": [-24, 4.8, -33.8], "dir": [1, 0, 0], "count": 3, "rot": 180},
    ])

    # ---------------- lower town (y0): plaza, Fisher Lane, north row
    # H1 warehouse on the plaza's east side (single tall storey, 6x9)
    house(12, -4, 18, 5, 0, 1,
          {"S": ["pwp"], "N": ["pwp"], "E": ["pwp"], "W": [["p", "d", "p"]]},
          roof_rot=90)
    PR.append({"kit": "crate_stack", "at": [16.6, 0, 3.2], "rot": 15, "tag": "base"})
    PR.append({"kit": "barrel", "at": [16.9, 0, 1.4], "rot": 0, "tag": "base"})
    PR.append({"kit": "barrel", "at": [13.2, 0, -2.6], "rot": 40, "tag": "base"})
    PR.append({"kit": "hand_cart", "at": [14.8, 0, -1.2], "rot": -75, "tag": "base"})
    SP.append({"enemy": "lantern_wretch", "id": "ware_wretch", "at": [15, 0, 2], "face": -90})
    PK.append({"id": "ware_tithe", "at": [16.8, 0, -2.2], "orisons": 70, "tag": "base",
               "label": "Gather the wharfinger's tithe"})

    # H2: two-storey rower's house, balcony over Fisher Lane (enterable)
    house(-16, -16, -10, -10, 0, 2,
          {"S": [["p", "d"], ["d", "p"]], "N": ["wp", "pw"], "E": ["ww", "pw"],
           "W": ["pw", "wp"]},
          stairwells=[(-16, -16, "x")], roof_rot=0, chimney=(-11, -15))
    P.append({"kit": "balcony_3m", "at": [-14.5, 3, -9.85], "rot": 180})
    PR.append({"kit": "candle_cluster", "at": [-12.2, 0, -14.6], "rot": 20, "tag": "glory"})
    PR.append({"kit": "candle_cluster_dead", "at": [-12.2, 0, -14.6], "rot": 20, "tag": "ruin"})
    PR.append({"kit": "barrel", "at": [-10.6, 0, -14.9], "rot": 10, "tag": "base"})
    PK.append({"id": "roper_savings", "at": [-11, 3, -14.5], "orisons": 95, "tag": "base",
               "label": "Gather the roper's savings"})

    # H3: three-storey tall house, climbable to the top room
    house(-6, -18, 0, -12, 0, 3,
          {"S": [["d", "p"], ["w", "p"], ["w", "w"]], "N": ["pw", "wp", "ww"],
           "E": ["wp", "pw", "ww"], "W": ["pp", "wp", "ww"]},
          stairwells=[(-6, -18, "x"), (-6, -15, "z")], roof_rot=90, chimney=(-1.2, -13))
    PR.append({"kit": "cobweb", "at": [-5.6, 6.4, -17.6], "rot": 45, "tag": "ruin"})
    PK.append({"id": "steeple_cache", "at": [-2, 6, -13.5], "orisons": 140, "tag": "base",
               "label": "Gather the steeplejack's cache"})

    # H4: facade row east of H3 (sealed homes, street dressing)
    house(2, -18, 8, -12, 0, 2,
          {"S": ["pw", "wp"], "N": ["wp", "pw"], "E": ["ww", "pw"], "W": ["pp", "ww"]},
          roof_rot=90, chimney=(6.4, -13.2))
    PR.append({"kit": "hand_cart", "at": [4, 0, -9.4], "rot": 100, "tag": "base"})
    PR.append({"kit": "barrel", "at": [7.2, 0, -10.6], "rot": 55, "tag": "base"})
    PR.append({"kit": "bone_pile", "at": [2.2, 0, -7.6], "rot": 30, "tag": "ruin"})

    # lane and plaza life
    SP.append({"enemy": "penitent", "id": "lane_p1", "at": [-6, 0, -8], "face": 90})
    SP.append({"enemy": "penitent", "id": "lane_p2", "at": [6, 0, -7], "face": -90})
    SP.append({"enemy": "penitent", "id": "plaza_p1", "at": [-10, 0, 2], "face": 0})
    PK.append({"id": "quay_alms", "at": [-14, 0, 7], "orisons": 45, "tag": "base",
               "label": "Gather the quay alms"})

    # ---------------- mid terrace (y2.4): Ropewalk Row
    # H5: two-storey, balcony overlooking the lower town's roofs
    house(-20, -32, -14, -26, 2.4, 2,
          {"S": [["d", "p"], ["d", "w"]], "N": ["wp", "pw"], "E": ["wp", "ww"],
           "W": ["pw", "wp"]},
          stairwells=[(-20, -32, "x")], roof_rot=0, chimney=(-15.2, -31))
    P.append({"kit": "balcony_3m", "at": [-18.5, 5.4, -25.85], "rot": 180})
    PK.append({"id": "ropewalk_purse", "at": [-15.4, 5.4, -30.6], "orisons": 110, "tag": "base",
               "label": "Gather the ropewalk purse"})
    PR.append({"kit": "candle_cluster", "at": [-19.4, 2.4, -30.8], "rot": -25, "tag": "glory"})
    PR.append({"kit": "candle_cluster_dead", "at": [-19.4, 2.4, -30.8], "rot": -25, "tag": "ruin"})

    # H6: single-storey cottage (enterable)
    house(-2, -32, 4, -26, 2.4, 1,
          {"S": [["p", "d"]], "N": ["ww"], "E": ["wp"], "W": ["pw"]},
          roof_rot=0, chimney=(2.8, -31))
    PR.append({"kit": "barrel", "at": [-0.8, 2.4, -30.9], "rot": 65, "tag": "base"})
    PR.append({"kit": "wax_husk", "at": [1.6, 2.4, -30.2], "rot": 200, "tag": "ruin"})
    PK.append({"id": "cottage_candle", "at": [2.6, 2.4, -30.6], "orisons": 60, "tag": "base",
               "label": "Gather the cold hearth's coins"})

    # H7: facade row, east half of the terrace
    house(8, -32, 17, -26, 2.4, 2,
          {"S": ["wpw", "pwp"], "N": ["pwp", "wpw"], "E": ["pw", "ww"], "W": ["wp", "pw"]},
          roof_rot=90, chimney=(15.4, -27.2))
    PR.append({"kit": "crate_stack", "at": [6.2, 2.4, -24.4], "rot": -30, "tag": "base"})
    PR.append({"kit": "banner", "at": [10, 2.8, -25.9], "rot": 0, "tag": "glory"})
    PR.append({"kit": "banner_torn", "at": [10, 2.8, -25.9], "rot": 0, "tag": "ruin"})
    SP.append({"enemy": "penitent", "id": "rope_p1", "at": [-4, 2.4, -23], "face": 90})
    SP.append({"enemy": "lantern_wretch", "id": "rope_wretch", "at": [10, 2.4, -22], "face": 180})

    # ---------------- parish square (y4.8)
    # parish front centered on the north rim (sealed grand door, rose window)
    P.append({"kit": "wall_4x4", "at": [-6, 4.8, -45], "rot": 0})
    P.append({"kit": "portal_4m", "at": [-2, 4.8, -45], "rot": 0, "scale": [1.2, 1.35, 1.2]})
    P.append({"kit": "door_leaf", "at": [-2, 4.8, -45], "rot": 0, "scale": [1.2, 1.35, 1.2], "tag": "base"})
    P.append({"kit": "wall_4x4", "at": [2, 4.8, -45], "rot": 0})
    P.append({"kit": "wall_4x4", "at": [-6, 9.6, -45], "rot": 0})
    P.append({"kit": "wall_4x4", "at": [-2, 9.6, -45], "rot": 0})
    P.append({"kit": "wall_4x4", "at": [2, 9.6, -45], "rot": 0})
    P.append({"kit": "rose_window", "at": [-2, 11.6, -44.55], "rot": 0, "collide": False})
    P.append({"kit": "buttress", "at": [-6.2, 4.8, -44.75], "rot": 0})
    P.append({"kit": "buttress", "at": [2.2, 4.8, -44.75], "rot": 0})

    # belfry: a solid three-band tower on the square's east side, iron-crowned
    for yy in (4.8, 9.6, 14.4):
        P.append({"kit": "wall_4x4", "at": [12, yy, -42], "rot": 90, "scale": [1, 1.2, 1]})
        P.append({"kit": "wall_4x4", "at": [16, yy, -42], "rot": -90, "scale": [1, 1.2, 1]})
        P.append({"kit": "wall_4x4", "at": [14, yy, -44], "rot": 0, "scale": [1, 1.2, 1]})
        P.append({"kit": "wall_4x4", "at": [14, yy, -40], "rot": 180, "scale": [1, 1.2, 1]})
    F.append({"kit": "floor_4x4", "min": [12, 19.2, -44], "max": [16, 19.2, -40]})
    OA.append({"min": [12, 19.2, -44], "max": [16, 19.2, -40]})
    ROWS.extend([
        {"kit": "fence_iron_4m", "from": [14, 19.2, -43.8], "dir": [1, 0, 0], "count": 1, "rot": 0},
        {"kit": "fence_iron_4m", "from": [14, 19.2, -40.2], "dir": [1, 0, 0], "count": 1, "rot": 180},
        {"kit": "fence_iron_4m", "from": [12.2, 19.2, -42], "dir": [0, 0, 1], "count": 1, "rot": 90},
        {"kit": "fence_iron_4m", "from": [15.8, 19.2, -42], "dir": [0, 0, 1], "count": 1, "rot": -90},
    ])
    P.append({"kit": "gargoyle", "at": [12.2, 14.4, -44.2], "rot": 45})
    P.append({"kit": "gargoyle", "at": [15.8, 14.4, -39.8], "rot": -135})

    # H8: square-side house (enterable, two storeys)
    house(-18, -44, -12, -38, 4.8, 2,
          {"E": [["p", "d"], ["w", "w"]], "N": ["pw", "ww"], "S": ["wp", "pw"],
           "W": ["ww", "pp"]},
          stairwells=[(-18, -44, "x")], roof_rot=0, chimney=(-13.2, -43))
    PK.append({"id": "parish_alms", "at": [-13.4, 7.8, -42.6], "orisons": 130, "tag": "base",
               "label": "Gather the parish alms"})

    # square dressing + hosts
    P.append({"kit": "wellhead", "at": [0, 4.8, -40], "rot": 15})
    PR.append({"kit": "hand_cart", "at": [5.4, 4.8, -37.6], "rot": -120, "tag": "base"})
    PR.append({"kit": "crate_stack", "at": [7, 4.8, -39], "rot": 10, "tag": "base"})
    PR.append({"kit": "barrel", "at": [6.4, 4.8, -40.6], "rot": 80, "tag": "base"})
    PR.append({"kit": "candle_cluster", "at": [-6.8, 4.8, -39.4], "rot": 45, "tag": "glory"})
    PR.append({"kit": "candle_cluster_dead", "at": [-6.8, 4.8, -39.4], "rot": 45, "tag": "ruin"})
    PR.append({"kit": "cobweb", "at": [13.8, 8.4, -43.8], "rot": -45, "tag": "ruin"})
    SP.append({"enemy": "vigilant_husk", "id": "square_husk", "at": [1, 4.8, -37], "face": 180})
    SP.append({"enemy": "penitent", "id": "square_p1", "at": [-8, 4.8, -36], "face": 90})
    PK.append({"id": "square_hoard", "at": [2.8, 4.8, -43.2], "orisons": 160, "tag": "base",
               "label": "Gather the sexton-square hoard"})

    # ---------------- quay dressing, lantern, lore
    d["lanterns"] = [{"id": "outskirts_quay", "name": "Quaylantern", "at": [7, 0, 7.5], "rot": -45}]
    d["plaques"] = [
        {"at": [-4.6, 0, 9.2], "rot": 160, "text":
         "THE OLD OUTSKIRTS\n\nBefore the kingdom banked its light, it lived here — "
         "rope and wax, fish and prayer, six families to a stair.\n\nThe city moved up "
         "the hill and the hill kept the houses. Mind the balconies; the timbers remember rain."},
        {"at": [4.5, 4.8, -37.4], "rot": -155, "text":
         "THE PARISH OF THE FIRST WICK\n\nHere the first vigil candle was dipped, "
         "long before the basilica raised its rock.\n\nThe parish door is sealed until "
         "someone remembers the words. Nobody remembers the words."},
    ]
    PR.append({"kit": "banner", "at": [-2, 0.4, 9.7], "rot": 0, "tag": "glory"})
    PR.append({"kit": "banner_torn", "at": [-2, 0.4, 9.7], "rot": 0, "tag": "ruin"})
    PR.append({"kit": "barrel", "at": [-9.4, 0, 9.2], "rot": 25, "tag": "base"})
    PR.append({"kit": "crate_stack", "at": [-11, 0, 8.6], "rot": -20, "tag": "base"})

    # ---------------- the city on every horizon
    d["skyline"] = [{"kit": "city_panorama", "at": [0, -16, -18]}]

    d["boxes"] = B_new
    d["pieces"] = [{"kit": "ferry_skiff", "at": [1.8, -2.32, 16.5], "rot": 205}] + P
    d["fills"] = F
    d["rows"] = ROWS
    d["props"] = PR
    d["spawners"] = SP
    d["pickups"] = PK
    d["open_air_regions"] = d.get("open_air_regions", [])[:3] + OA
    json.dump(d, open(PATH, "w"), indent=1)
    print("old_outskirts: pieces %d fills %d rows %d props %d spawners %d pickups %d oa %d"
          % (len(d["pieces"]), len(F), len(ROWS), len(PR), len(SP), len(PK), len(OA)))


if __name__ == "__main__":
    main()
