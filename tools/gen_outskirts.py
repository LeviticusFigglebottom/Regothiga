#!/usr/bin/env python3
"""Author data/areas/old_outskirts.json: the Old Outskirts, a half-timbered
hill town above the drowned canal — dense rowhouses and burnt-out shells
covering the whole plateau, switchback streets climbing two terraces, and
the Parish of the First Wick walling the entire back of the district, its
clocktower stopped at nine over the sealed door. Three graven word-stones
hidden through the town (wax / wick / flame) unbar the parish door.

Deterministic and idempotent (owns every list it writes; the quay/canal
stub boxes are inlined below). Run after editing and re-audit:
    python3 tools/gen_outskirts.py && python3 tools/audit_areas.py old_outskirts

House module: 3 m storeys of burg_wall_3m panels; interior wooden stairs
run inside carved stairwell tiles, foot tucked into the wall base so the
top lands flush at the hole's edge (a top overhang head-bumps climbers on
the slab edge). The flight is solid to the floor and the stairwell tile's
flanks are decked over, so nothing floats and no seam-slits flank the head.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "data", "areas", "old_outskirts.json")

P = []   # pieces
F = []   # fills
B = []   # extra boxes (terraces, parapets, stairwell decks)
PR = []  # props
OA = []  # open_air_regions
SP = []  # spawners
PK = []  # pickups
WS = []  # word stones
ROWS = []

# the pre-town plateau: ground slab, quay wall + coping, canal bed, water,
# far shore backdrop (verbatim from the original stub — this script owns them)
STUB_BOXES = [
    {"min": [-60, -40.0, -50], "max": [60, 0, 12], "mat": "M_stone_dark", "tag": "base", "walkable": True},
    {"min": [-60, -2.5, 12], "max": [60, 0, 13], "mat": "M_stone_dark", "tag": "base"},
    {"min": [-60, 0, 12.7], "max": [60, 0.35, 13.05], "mat": "M_stone_dark", "tag": "base"},
    {"min": [-60, -3.0, 13], "max": [60, -2.45, 34], "mat": "M_marsh", "tag": "base", "walkable": True},
    {"min": [-60, -2.4, 13], "max": [60, -2.16, 34], "mat": "M_water", "tag": "base", "collide": False},
    {"min": [-60, -2.4, 34], "max": [60, 2.5, 35], "mat": "M_backdrop_dark", "tag": "base"},
]
STUB_OA = [
    {"min": [-60, 0, -50], "max": [60, 0, 12]},
    {"min": [-60, 0, 12.7], "max": [60, 0.35, 13.05]},
    {"min": [-60, -2.45, 13], "max": [60, -2.45, 34]},
]

KITS = {"p": "burg_wall_3m", "w": "burg_wall_3m_win", "d": "burg_wall_3m_door",
        "a": "burg_wall_3m_ruin_a", "b": "burg_wall_3m_ruin_b"}


def wall_row(x0, x1, z0, z1, y, side, variants):
    """One storey of one building side. side letter = which face is exterior.
    variants: string/list of 'p'lain, 'w'indow, 'd'oor, 'a'/'b' ruin, '-' skip."""
    rot = {"N": 0, "S": 180, "W": 90, "E": -90}[side]
    if side in ("N", "S"):
        z = z0 if side == "N" else z1
        cs = [(x0 + 1.5 + 3 * i, z) for i in range(int(round((x1 - x0) / 3)))]
    else:
        x = x0 if side == "W" else x1
        cs = [(x, z0 + 1.5 + 3 * i) for i in range(int(round((z1 - z0) / 3)))]
    for i, (x, z) in enumerate(cs):
        v = variants[i]
        if v != "-":
            P.append({"kit": KITS[v], "at": [x, y, z], "rot": rot})


def house(x0, z0, x1, z1, base, storeys, sides, stairwells=None, roof_rot=0,
          chimney=None):
    """A rowhouse. sides: dict side -> per-storey variant strings.
    stairwells: list of (tile_x0, tile_z0, axis) per storey gap; axis 'x'
    runs the flight west->east inside the tile (exit east), axis 'z' runs
    it south->north (exit north). Floors above each gap omit that tile,
    and the tile's flanks are decked so only the stair channel opens."""
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
        # the 3.31 m run overhangs the 3 m tile at the FOOT (tucked into the
        # wall base) so the top lands flush at the hole's edge — overhanging
        # the top instead head-bumps climbers on the slab edge. The flight
        # itself is solid to the floor, so nothing reads as floating.
        for s, (sx, sz, axis) in enumerate(stairwells):
            y = base + 3 * s
            yf = y + 3          # the floor the flight serves
            if axis == "x":   # ascend east, top flush at the tile's east edge
                P.append({"kit": "stair_wood_3m", "at": [sx - 0.31, y + 0.02, sz + 1.5], "rot": -90})
                for za, zb in ((sz, sz + 0.76), (sz + 2.24, sz + 3)):
                    B.append({"min": [sx, yf - 0.32, za], "max": [sx + 3, yf - 0.02, zb],
                              "mat": "M_wood", "walkable": True, "gen": True})
            else:             # ascend north, top flush at the tile's north edge
                P.append({"kit": "stair_wood_3m", "at": [sx + 1.5, y + 0.02, sz + 3.31], "rot": 0})
                for xa, xb in ((sx, sx + 0.76), (sx + 2.24, sx + 3)):
                    B.append({"min": [xa, yf - 0.32, sz], "max": [xb, yf - 0.02, sz + 3],
                              "mat": "M_wood", "walkable": True, "gen": True})
    top = base + 3 * storeys
    cx, cz = (x0 + x1) / 2, (z0 + z1) / 2
    if roof_rot in (0, 180):     # ridge along X
        sc = [round((x1 - x0 + 1) / 7.0, 3), 1, round((z1 - z0 + 1) / 7.0, 3)]
    else:                        # ridge along Z
        sc = [round((z1 - z0 + 1) / 7.0, 3), 1, round((x1 - x0 + 1) / 7.0, 3)]
    P.append({"kit": "roof_gable_7m", "at": [cx, top, cz], "rot": roof_rot, "scale": sc})
    if chimney:
        P.append({"kit": "chimney_stack", "at": [chimney[0], top + 0.9, chimney[1]], "rot": 0})


def ruin(x0, z0, x1, z1, base, sides, rubble=()):
    """A roofless shell: one storey of snapped walls, rubble drifted inside."""
    for side, pat in sides.items():
        wall_row(x0, x1, z0, z1, base, side, pat)
    for r in rubble:
        kit = "rubble_" + (r[2] if len(r) > 2 else "m")
        PR.append({"kit": kit, "at": [r[0], base, r[1]], "rot": (r[0] * 7 + r[1] * 3) % 360,
                   "tag": "base"})


def main():
    d = json.load(open(PATH))

    # ---------------- terraces: two risers climbing away from the quay
    B.append({"min": [-26, 0, -34], "max": [26, 2.4, -18], "mat": "M_stone",
              "tag": "base", "walkable": True})
    B.append({"min": [-26, 0, -46], "max": [26, 4.8, -34], "mat": "M_stone",
              "tag": "base", "walkable": True})
    # plateau rim (the parish facade closes the back; these hold the sides)
    B.append({"min": [-60, 0, -50], "max": [60, 1.1, -49.6], "mat": "M_stone", "tag": "base"})
    B.append({"min": [-60, 0, -50], "max": [-59.6, 1.1, 12], "mat": "M_stone", "tag": "base"})
    B.append({"min": [59.6, 0, -50], "max": [60, 1.1, 12], "mat": "M_stone", "tag": "base"})
    OA.append({"min": [-26, 2.4, -34], "max": [26, 2.4, -18]})
    OA.append({"min": [-26, 4.8, -46], "max": [26, 4.8, -34]})

    # switchback grand stairs between the terraces; the rim rails sit ON the
    # slab (0.2 inside the edge — a fence past the lip floats over the drop)
    P.append({"kit": "stair_grand_4m", "at": [11, 2.42, -18], "rot": 180})
    P.append({"kit": "stair_grand_4m", "at": [-11, 4.82, -34], "rot": 180})
    ROWS.extend([
        {"kit": "balustrade_4m", "from": [-24, 2.4, -18.2], "dir": [1, 0, 0], "count": 8, "rot": 180},
        {"kit": "balustrade_4m", "from": [16, 2.4, -18.2], "dir": [1, 0, 0], "count": 3, "rot": 180},
        {"kit": "balustrade_4m", "from": [-24, 4.8, -34.2], "dir": [1, 0, 0], "count": 3, "rot": 180},
        {"kit": "balustrade_4m", "from": [-6, 4.8, -34.2], "dir": [1, 0, 0], "count": 8, "rot": 180},
        # side rails only along the OPEN terrace edges (houses hold the rest)
        {"kit": "balustrade_4m", "from": [-25.8, 2.4, -24], "dir": [0, 0, 1], "count": 2, "rot": 90},
        {"kit": "balustrade_4m", "from": [25.8, 2.4, -24], "dir": [0, 0, 1], "count": 2, "rot": -90},
        {"kit": "balustrade_4m", "from": [-25.8, 4.8, -36], "dir": [0, 0, 1], "count": 1, "rot": 90},
        {"kit": "balustrade_4m", "from": [25.8, 4.8, -44], "dir": [0, 0, 1], "count": 3, "rot": -90},
    ])
    # stone posts plugging the rail gaps the 4 m panels leave beside stairs
    for xa, xb in ((6, 9), (13, 14), (24, 26)):
        B.append({"min": [xa, 2.4, -18.4], "max": [xb, 3.35, -18.05],
                  "mat": "M_stone", "tag": "base", "gen": True})
    for xa, xb in ((-14, -13), (-9, -8), (24, 26)):
        B.append({"min": [xa, 4.8, -34.4], "max": [xb, 5.75, -34.05],
                  "mat": "M_stone", "tag": "base", "gen": True})

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

    # H3: three-storey tall house, climbable to the top room (WICK stone)
    house(-6, -18, 0, -12, 0, 3,
          {"S": [["d", "p"], ["w", "p"], ["w", "w"]], "N": ["pw", "wp", "ww"],
           "E": ["wp", "pw", "ww"], "W": ["pp", "wp", "ww"]},
          stairwells=[(-6, -18, "x"), (-6, -15, "z")], roof_rot=90, chimney=(-1.2, -13))
    PR.append({"kit": "cobweb", "at": [-5.6, 6.4, -17.6], "rot": 45, "tag": "ruin"})
    PK.append({"id": "steeple_cache", "at": [-2, 6, -13.5], "orisons": 140, "tag": "base",
               "label": "Gather the steeplejack's cache"})
    WS.append({"at": [-1.2, 6.0, -16.8], "rot": 200, "word": "WICK", "flag": "word_wick",
               "line": "Wound tight up the stair, the way a wick winds through the tallow."})

    # H4: facade row east of H3 (sealed homes, street dressing)
    house(2, -18, 8, -12, 0, 2,
          {"S": ["pw", "wp"], "N": ["wp", "pw"], "E": ["ww", "pw"], "W": ["pp", "ww"]},
          roof_rot=90, chimney=(6.4, -13.2))
    PR.append({"kit": "hand_cart", "at": [4, 0, -9.4], "rot": 100, "tag": "base"})
    PR.append({"kit": "barrel", "at": [7.2, 0, -10.6], "rot": 55, "tag": "base"})
    PR.append({"kit": "bone_pile", "at": [2.2, 0, -7.6], "rot": 30, "tag": "ruin"})

    # N3: rowhouse plugging the gap east of H4, backed onto the terrace riser
    house(14, -18, 20, -12, 0, 2,
          {"S": ["dp", "wp"], "N": ["wp", "pw"], "E": ["pw", "wp"], "W": ["wp", "ww"]},
          roof_rot=90, chimney=(18.6, -13.4))
    PR.append({"kit": "barrel", "at": [13, 0, -10.8], "rot": 75, "tag": "base"})

    # N1: west-corner house across the lane from H2 (enterable)
    house(-26, -16, -20, -10, 0, 2,
          {"S": ["pd", "ww"], "N": ["wp", "pw"], "E": ["pw", "wp"], "W": ["pp", "ww"]},
          stairwells=[(-26, -16, "x")], roof_rot=0, chimney=(-21, -15))
    PK.append({"id": "corner_till", "at": [-24.6, 3, -11.4], "orisons": 80, "tag": "base",
               "label": "Gather the corner-house till"})
    # the Bellkeeper's amend: one fragment lies in the old kingdom's broken
    # houses — an upper ruin room, unseen until his word is given
    PK.append({"id": "bell_fragment_ruins", "at": [-16.4, 5.4, -31.2],
               "item": "bell_fragment", "tag": "base",
               "label": "Take the bell fragment",
               "require_flag": "amend_bell_asked"})

    # R1: roofless shell between N1 and the plaza
    ruin(-26, -6, -20, 0, 0, {"S": "ab", "N": "ba", "E": "ap", "W": "b-"},
         rubble=((-23, -3), (-21.4, -1.4, "s")))

    # R2: burnt warehouse annex east of H1
    ruin(20, -4, 26, 2, 0, {"S": "b-", "N": "ab", "E": "pa", "W": "ba"},
         rubble=((23, -1),))

    # lane and plaza life
    SP.append({"enemy": "penitent", "id": "lane_p1", "at": [-6, 0, -8], "face": 90})
    SP.append({"enemy": "penitent", "id": "lane_p2", "at": [6, 0, -7], "face": -90})
    SP.append({"enemy": "penitent", "id": "plaza_p1", "at": [-10, 0, 2], "face": 0})
    PK.append({"id": "quay_alms", "at": [-14, 0, 7], "orisons": 45, "tag": "base",
               "label": "Gather the quay alms"})

    # ---------------- west quarter (the chandlers' end, mostly fallen)
    house(-36, -16, -30, -10, 0, 3,
          {"S": [["p", "d"], ["w", "p"], ["w", "w"]], "N": ["wp", "pw", "ww"],
           "E": ["pd", "ww", "ww"], "W": ["pp", "wp", "ww"]},
          stairwells=[(-36, -16, "x"), (-36, -13, "z")], roof_rot=90, chimney=(-31.2, -11.4))
    PK.append({"id": "gable_hoard", "at": [-32, 6, -11.5], "orisons": 150, "tag": "base",
               "label": "Gather the gable hoard"})
    house(-34, 0, -28, 6, 0, 1,
          {"S": ["pw"], "N": ["wp"], "E": ["dp"], "W": ["pw"]},
          roof_rot=0, chimney=(-29.2, 1))
    ruin(-44, -19, -38, -10, 0, {"E": "aba", "W": "bab", "S": "ab", "N": "ba"},
         rubble=((-41, -14), (-39.4, -17, "s")))
    # the chandlery chapel: the WAX stone stands by its rubble altar
    ruin(-52, -30, -46, -21, 0, {"E": "a-b", "W": "bap", "S": "db", "N": "ab"},
         rubble=((-49, -25.4), (-50.6, -22.6, "s")))
    WS.append({"at": [-48.6, 0, -26.2], "rot": 155, "word": "WAX", "flag": "word_wax",
               "line": "Where the chandlers boiled the comb, the first word set as it cooled."})
    PR.append({"kit": "candle_cluster_dead", "at": [-47.6, 0, -24.8], "rot": 80, "tag": "base"})
    PK.append({"id": "chapel_offering", "at": [-47.4, 0, -28.2], "orisons": 85, "tag": "base",
               "label": "Gather the chapel offering"})
    ruin(-56, -8, -50, -2, 0, {"S": "-a", "N": "b-", "E": "ab", "W": "pa"},
         rubble=((-53, -5, "l"),))
    ruin(-44, -42, -38, -36, 0, {"S": "ab", "N": "ba", "E": "-a", "W": "ab"},
         rubble=((-41, -39),))
    PR.append({"kit": "hand_cart", "at": [-28.5, 0, -8], "rot": 40, "tag": "base"})
    PR.append({"kit": "barrel", "at": [-30.2, 0, 4.6], "rot": 30, "tag": "base"})
    PR.append({"kit": "crate_stack", "at": [-44, 0, 6.8], "rot": -15, "tag": "base"})
    SP.append({"enemy": "penitent", "id": "west_lane_p", "at": [-28, 0, -12], "face": 90})
    SP.append({"enemy": "lantern_wretch", "id": "chapel_wretch", "at": [-49, 0, -23], "face": 0})
    SP.append({"enemy": "penitent", "id": "backrow_p", "at": [-40, 0, -32], "face": 180})
    PK.append({"id": "west_cache", "at": [-33.4, 0, -12.6], "orisons": 75, "tag": "base",
               "label": "Gather the wax-boiler's cache"})

    # ---------------- east quarter (the wharf end; the FLAME stone)
    house(30, -14, 36, -8, 0, 2,
          {"S": ["pw", "wp"], "N": ["wp", "pw"], "E": ["pw", "ww"], "W": ["pd", "ww"]},
          stairwells=[(30, -14, "x")], roof_rot=0, chimney=(35, -9.4))
    house(30, 0, 36, 6, 0, 1,
          {"S": ["wp"], "N": ["pw"], "E": ["wp"], "W": ["dp"]},
          roof_rot=90, chimney=(34.8, 4.6))
    ruin(40, -16, 49, -10, 0, {"S": "a-b", "N": "bab", "E": "ab", "W": "da"},
         rubble=((44, -12.6), (47.2, -14.8, "s")))
    WS.append({"at": [44.5, 0, -13.6], "rot": -35, "word": "FLAME", "flag": "word_flame",
               "line": "The fire that ate the roofbeams never once left this hearth."})
    PK.append({"id": "wharf_strongbox", "at": [46.4, 0, -14.6], "orisons": 120, "tag": "base",
               "label": "Gather the wharf strongbox"})
    ruin(52, -30, 58, -24, 0, {"S": "ba", "N": "ab", "E": "b-", "W": "ap"})
    ruin(44, -2, 50, 4, 0, {"S": "ab", "N": "-b", "E": "pa", "W": "b-"},
         rubble=((47, 1, "l"),))
    ruin(34, -42, 40, -36, 0, {"S": "ba", "N": "ab", "E": "a-", "W": "-b"})
    PK.append({"id": "backrow_tithe", "at": [37, 0, -40], "orisons": 90, "tag": "base",
               "label": "Gather the back-row tithe"})
    PR.append({"kit": "hand_cart", "at": [32, 0, -4.6], "rot": -60, "tag": "base"})
    PR.append({"kit": "barrel", "at": [28.4, 0, 6.2], "rot": 50, "tag": "base"})
    PR.append({"kit": "crate_stack", "at": [42, 0, 7], "rot": 25, "tag": "base"})
    SP.append({"enemy": "penitent", "id": "east_lane_p", "at": [28, 0, -4], "face": -90})
    SP.append({"enemy": "vigilant_husk", "id": "wharf_husk", "at": [44, 0, -11.8], "face": 90})

    # ---------------- mid terrace (y2.4): Ropewalk Row
    # H5: two-storey, balcony overlooking the lower town's roofs
    house(-20, -32, -14, -26, 2.4, 2,
          {"S": [["d", "p"], ["d", "w"]], "N": ["wp", "pw"], "E": ["wp", "ww"],
           "W": ["pw", "wp"]},
          stairwells=[(-20, -32, "x")], roof_rot=0, chimney=(-15.2, -31))
    P.append({"kit": "balcony_3m", "at": [-18.5, 5.4, -25.85], "rot": 180})
    PK.append({"id": "ropewalk_purse", "at": [-15.4, 5.4, -30.6], "orisons": 110, "tag": "base",
               "label": "Gather the ropewalk purse"})
    PR.append({"kit": "candle_cluster", "at": [-15.6, 2.4, -27.4], "rot": -25, "tag": "glory"})
    PR.append({"kit": "candle_cluster_dead", "at": [-15.6, 2.4, -27.4], "rot": -25, "tag": "ruin"})

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

    # N8: terrace-end house; R11: the sliver shell at the west end
    house(20, -32, 26, -26, 2.4, 2,
          {"S": ["pw", "wp"], "N": ["wp", "pw"], "E": ["pw", "ww"], "W": ["pd", "ww"]},
          roof_rot=90, chimney=(24.6, -31))
    ruin(-26, -32, -23, -26, 2.4, {"E": "ab", "W": "ba", "S": "a", "N": "b"},
         rubble=((-24.5, -28.6, "s"),))
    SP.append({"enemy": "lantern_wretch", "id": "midt_wretch", "at": [22, 2.4, -23], "face": 180})

    # ---------------- parish square (y4.8)
    # H8: square-side house (enterable, two storeys)
    house(-18, -44, -12, -38, 4.8, 2,
          {"E": [["p", "d"], ["w", "w"]], "N": ["pw", "ww"], "S": ["wp", "pw"],
           "W": ["ww", "pp"]},
          stairwells=[(-18, -44, "x")], roof_rot=0, chimney=(-13.2, -43))
    PK.append({"id": "parish_alms", "at": [-13.4, 7.8, -42.6], "orisons": 130, "tag": "base",
               "label": "Gather the parish alms"})

    # N9 and N10 flank the square; R12 is the shell east of it
    house(-26, -44, -20, -38, 4.8, 2,
          {"S": ["pw", "wp"], "N": ["wp", "ww"], "E": ["dp", "ww"], "W": ["pp", "ww"]},
          stairwells=[(-26, -44, "x")], roof_rot=0, chimney=(-21, -43))
    house(8, -44, 14, -38, 4.8, 2,
          {"S": ["wp", "pw"], "N": ["pw", "wp"], "E": ["pw", "ww"], "W": ["pd", "ww"]},
          stairwells=[(8, -44, "x")], roof_rot=0, chimney=(13, -39.4))
    PK.append({"id": "vestry_purse", "at": [12.6, 7.8, -42.4], "orisons": 125, "tag": "base",
               "label": "Gather the vestry purse"})
    ruin(16, -42, 22, -36, 4.8, {"S": "ab", "N": "b-", "E": "ap", "W": "-a"},
         rubble=((19, -39),))

    # square dressing + hosts
    P.append({"kit": "wellhead", "at": [0, 4.8, -40], "rot": 15})
    PR.append({"kit": "hand_cart", "at": [5.4, 4.8, -37.6], "rot": -120, "tag": "base"})
    PR.append({"kit": "crate_stack", "at": [7, 4.8, -39], "rot": 10, "tag": "base"})
    PR.append({"kit": "barrel", "at": [6.4, 4.8, -40.6], "rot": 80, "tag": "base"})
    PR.append({"kit": "candle_cluster", "at": [-6.8, 4.8, -39.4], "rot": 45, "tag": "glory"})
    PR.append({"kit": "candle_cluster_dead", "at": [-6.8, 4.8, -39.4], "rot": 45, "tag": "ruin"})
    SP.append({"enemy": "vigilant_husk", "id": "square_husk", "at": [1, 4.8, -37], "face": 180})
    SP.append({"enemy": "penitent", "id": "square_p1", "at": [-8, 4.8, -36], "face": 90})
    PK.append({"id": "square_hoard", "at": [2.8, 4.8, -43.2], "orisons": 160, "tag": "base",
               "label": "Gather the sexton-square hoard"})

    # ---------------- the Parish of the First Wick: the whole back wall
    # One façade plane at z=-45.7, rim to rim. Sides rise three banded
    # storeys from the ground aprons; the centre rises two from the square
    # terrace to the same 14.4 skyline. The door bay carries the rose and
    # the clocktower overhead.
    FZ = -45.7
    for sx in (-1, 1):
        for k in range(9):                     # side sections, ground-based
            cx = sx * (26 + 4 * k)
            for band, wy in ((0, 0.0), (1, 4.8), (2, 9.6)):
                kit = "wall_4x4"
                if band == 1 and k % 2 == 1:
                    kit = "parish_window_4m"
                P.append({"kit": kit, "at": [cx, wy, FZ], "rot": 180, "scale": [1, 1.2, 1]})
    for cx in range(-20, 21, 4):               # centre sections on the terrace
        if cx == 0:
            continue
        for wy in (4.8, 9.6):
            kit = "wall_4x4"
            if wy == 4.8 and (abs(cx) // 4) % 2 == 1:
                kit = "parish_window_4m"
            P.append({"kit": kit, "at": [cx, wy, FZ], "rot": 180, "scale": [1, 1.2, 1]})
    for sx in (-1, 1):                         # 2 m plugs squaring the grid
        for wy in (4.8, 9.6):
            P.append({"kit": "wall_4x4", "at": [sx * 23, wy, FZ], "rot": 180,
                      "scale": [0.5, 1.2, 1]})
    # the door bay: portal, barred leaf (the three words unbar it), rose
    P.append({"kit": "portal_4m", "at": [0, 4.8, FZ], "rot": 0, "scale": [1.2, 1.35, 1.2]})
    P.append({"kit": "wall_4x4", "at": [0, 9.6, FZ], "rot": 180, "scale": [1, 1.2, 1]})
    P.append({"kit": "rose_window", "at": [0, 11.9, -45.35], "rot": 0, "collide": False})
    d["flag_gates"] = [{"flag": "parish_words", "kit": "door_leaf", "at": [0, 4.8, FZ],
                        "rot": 0, "scale": [1.2, 1.35, 1.2], "tag": "base"}]
    for bx, by in ((-2.8, 4.8), (2.8, 4.8), (-6, 4.8), (6, 4.8), (-14, 4.8), (14, 4.8),
                   (-22, 4.8), (22, 4.8), (-28, 0), (28, 0), (-36, 0), (36, 0),
                   (-44, 0), (44, 0), (-52, 0), (52, 0)):
        P.append({"kit": "buttress", "at": [bx, by, -45.2], "rot": 0})
    B.append({"min": [-60, 14.35, -45.95], "max": [60, 15.15, -45.45],
              "mat": "M_stone_trim", "tag": "base", "gen": True})
    # the clocktower over the entrance, dial stopped at nine
    P.append({"kit": "clock_tower", "at": [0, 14.4, -47.45], "rot": 180})
    P.append({"kit": "gargoyle", "at": [-1.9, 24.1, -45.6], "rot": 135})
    P.append({"kit": "gargoyle", "at": [1.9, 24.1, -45.6], "rot": -135})
    # a bare dark vestibule so the opened door frames night, not sky
    B.append({"min": [-2.3, 4.5, -48.1], "max": [2.3, 4.8, -45.8],
              "mat": "M_stone_dark", "tag": "base", "gen": True})
    B.append({"min": [-2.3, 4.8, -48.5], "max": [2.3, 9.7, -48.05],
              "mat": "M_stone_dark", "tag": "base", "gen": True})
    B.append({"min": [-2.7, 4.8, -48.1], "max": [-2.3, 9.7, -45.8],
              "mat": "M_stone_dark", "tag": "base", "gen": True})
    B.append({"min": [2.3, 4.8, -48.1], "max": [2.7, 9.7, -45.8],
              "mat": "M_stone_dark", "tag": "base", "gen": True})
    B.append({"min": [-2.7, 9.6, -48.5], "max": [2.7, 10.0, -45.7],
              "mat": "M_stone_dark", "tag": "base", "gen": True})

    # ---------------- quay dressing, lantern, lore
    d["lanterns"] = [{"id": "outskirts_quay", "name": "Quaylantern", "at": [7, 0, 7.5], "rot": -45}]
    d["plaques"] = [
        {"at": [-4.6, 0, 9.2], "rot": 160, "text":
         "THE OLD OUTSKIRTS\n\nBefore the kingdom banked its light, it lived here — "
         "rope and wax, fish and prayer, six families to a stair.\n\nThe city moved up "
         "the hill and the hill kept the houses. Mind the balconies; the timbers remember rain."},
        {"at": [4.5, 4.8, -37.4], "rot": -155, "text":
         "THE PARISH OF THE FIRST WICK\n\nHere the first vigil candle was dipped, "
         "long before the basilica raised its rock.\n\nThe door is sealed until someone "
         "speaks the three graven words. One cooled with the chandlers' wax. One wound "
         "up the steeplejack's stair. One never left the burnt wharf-house hearth."},
    ]
    for w in WS:
        w.update({"all_of": ["word_wax", "word_wick", "word_flame"], "sets": "parish_words",
                  "tag": "base"})
    d["word_stones"] = WS
    PR.append({"kit": "banner", "at": [-2, 0.4, 9.7], "rot": 0, "tag": "glory"})
    PR.append({"kit": "banner_torn", "at": [-2, 0.4, 9.7], "rot": 0, "tag": "ruin"})
    PR.append({"kit": "barrel", "at": [-9.4, 0, 9.2], "rot": 25, "tag": "base"})
    PR.append({"kit": "crate_stack", "at": [-11, 0, 8.6], "rot": -20, "tag": "base"})

    # the parish door is a true threshold now: the vestibule leads inside
    d["portals"] = [pp for pp in d.get("portals", []) if pp.get("to") != "wick_cathedral"]
    d["portals"].append({"to": "wick_cathedral", "at": [0, 4.8, -47.0], "rot": 0,
                         "spawn": [0, 0.2, 0.2], "spawn_yaw": 0,
                         "prompt": "Enter the Parish of the First Wick"})

    # ---------------- the city on every horizon
    d["skyline"] = [{"kit": "city_panorama", "at": [0, -16, -18]}]

    d["boxes"] = STUB_BOXES + B
    d["pieces"] = [{"kit": "ferry_skiff", "at": [1.8, -2.32, 16.5], "rot": 205}] + P
    d["fills"] = F
    d["rows"] = ROWS
    d["props"] = PR
    d["spawners"] = SP
    d["pickups"] = PK
    d["open_air_regions"] = STUB_OA + OA
    json.dump(d, open(PATH, "w"), indent=1)
    print("old_outskirts: pieces %d fills %d rows %d props %d spawners %d pickups %d words %d oa %d"
          % (len(d["pieces"]), len(F), len(ROWS), len(PR), len(SP), len(PK), len(WS), len(OA)))


if __name__ == "__main__":
    main()
