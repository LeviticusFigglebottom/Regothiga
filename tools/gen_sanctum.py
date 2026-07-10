#!/usr/bin/env python3
"""Author data/areas/gilded_sanctum.json: the Gilded Sanctum — the place the
lightfall carries the pilgrim, above the hours. The last place of true,
unfaltering light: a grand processional avenue between palace facades, a
great sealed Door of the Hour on its terrace, courts for the Offices and
the vigil garden, and gilded palaces beyond reach on every horizon.

No enemies, no wardens — lore, two puzzles (the Offices of the Hour chime
round; the Keepers' Candles votive set), a rest-only vigil (the light here
does not falter), Ser Adalric in the radiant version and a note in his
place in the dim one.

Deterministic and idempotent:
    python3 tools/gen_sanctum.py && python3 tools/audit_areas.py gilded_sanctum
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "data", "areas", "gilded_sanctum.json")

P = []    # pieces
F = []    # fills
B = []    # boxes
PR = []   # props
R = []    # rows
BL = []   # blockers
PLQ = []  # plaques


def piece(kit, at, rot=0, **kw):
    d = {"kit": kit, "at": list(at), "rot": rot}
    d.update(kw)
    P.append(d)


def prop(kit, at, rot=0, tag="base", **kw):
    d = {"kit": kit, "at": list(at), "rot": rot, "tag": tag}
    d.update(kw)
    PR.append(d)


def row(kit, frm, dirv, count, rot=0, **kw):
    d = {"kit": kit, "from": list(frm), "dir": list(dirv), "count": count, "rot": rot}
    d.update(kw)
    R.append(d)


def blocker(mn, mx):
    BL.append({"min": list(mn), "max": list(mx), "tag": "base"})


# ---------------------------------------------------------------- floors
# One marble field for the whole walkable ward, plus the palace terrace.
F.append({"kit": "floor_4x4", "min": [-22, 0, -12], "max": [22, 0, 30]})
F.append({"kit": "floor_4x4", "min": [-16, 2, -24], "max": [16, 2, -12]})
# terrace body so the +2 m deck has a face, not a floating slab
B.append({"min": [-16, 0, -24], "max": [16, 2, -12], "tag": "base"})

# the grand stair up to the Door of the Hour (three flights abreast)
for x in (-6, -2, 2):
    piece("stair_grand_4m", (x + 2, 2, -12), 0)

# ---------------------------------------------------------------- the Door of the Hour
# palace front along the terrace's north edge
row("wall_4x4", (-14, 2, -24), (1, 0, 0), 3, rot=0)
row("wall_4x4", (6, 2, -24), (1, 0, 0), 3, rot=0)
row("wall_4x4", (-14, 6, -24), (1, 0, 0), 8, rot=0)
piece("wall_4x4", (-3, 2, -24), 0, scale=[0.5, 1, 1])
piece("wall_4x4", (3, 2, -24), 0, scale=[0.5, 1, 1])
piece("portal_4m", (0, 2, -24), 0)
piece("door_leaf", (0, 2, -23.9), 0, scale=[1.25, 1.4, 1.2])
piece("rose_window", (0, 7.6, -23.7), 0, collide=False)
row("cornice_4m", (-14, 10, -24), (1, 0, 0), 8, rot=0)
for x in (-14, -7, 7, 14):
    piece("buttress", (x, 2, -23.4), 0)
for x in (-10, 10):
    piece("statue_saint", (x, 2, -22.6), 0)
# spires crown the palace, unreachable
piece("spire_tower_a", (0, 2, -30), 0, collide=False, flames=False)
piece("spire_tower_c", (-11, 2, -28), 0, collide=False, flames=False)
piece("spire_tower_c", (11, 2, -28), 0, collide=False, flames=False)
blocker((-16.6, 2, -24.6), (16.6, 14, -23.6))
# terrace rim (falls barred left and right of the stair)
row("balustrade_4m", (-14, 2, -12.2), (1, 0, 0), 2, rot=0)
row("balustrade_4m", (6, 2, -12.2), (1, 0, 0), 2, rot=0)
blocker((-16.4, 2, -12.6), (-8.2, 4, -11.9))
blocker((8.2, 2, -12.6), (16.4, 4, -11.9))
# terrace flanks
blocker((-16.6, 2, -24.4), (-15.9, 4, -12.0))
blocker((15.9, 2, -24.4), (16.6, 4, -12.0))

# ---------------------------------------------------------------- the avenue
# candelabra procession and banners down both flanks
for z in (20, 12, 4, -4):
    prop("candelabra", (-5.4, 0, z), 20)
    prop("candelabra", (5.4, 0, z), -20)
prop("mosaic_medallion", (0, 0.02, 8), 0)
prop("mosaic_medallion", (0, 0.02, -8), 0)

# avenue flank walls (palace facades) with lancet glass, north halves
for sx in (-1, 1):
    x = 13 * sx
    rot = 90 if sx < 0 else -90
    row("wall_4x4", (x, 0, -10), (0, 0, 1), 3, rot=rot)
    row("window_lancet_4m", (x, 4, -10), (0, 0, 1), 3, rot=rot)
    row("cornice_4m", (x, 8, -10), (0, 0, 1), 3, rot=rot)
    # south halves past the courts
    row("wall_4x4", (x, 0, 18), (0, 0, 1), 3, rot=rot)
    row("parish_window_4m", (x, 4, 18), (0, 0, 1), 3, rot=rot)
    row("cornice_4m", (x, 8, 18), (0, 0, 1), 3, rot=rot)
    for z in (-8, 18, 26):
        piece("buttress", (x - 0.6 * sx, 0, z), rot)
    piece("gargoyle", (x - 0.5 * sx, 8.2, -2), rot)

# court mouths: arcade colonnades where the courts open off the avenue
for sx in (-1, 1):
    x = 9.5 * sx
    rot = 90 if sx < 0 else -90
    piece("arcade_4m", (x, 0, 2), rot)
    piece("arcade_4m", (x, 0, 12), rot)

# ---------------------------------------------------------------- east court: the Offices of the Hour
row("wall_4x4", (22, 0, 0), (0, 0, 1), 4, rot=-90)
row("window_lancet_4m", (22, 4, 0), (0, 0, 1), 4, rot=-90)
row("wall_4x4", (14, 0, -0.5), (1, 0, 0), 2, rot=0)
row("wall_4x4", (14, 0, 14.5), (1, 0, 0), 2, rot=180)
prop("brazier_lit", (12.5, 0, 3.5), 0, tag="glory")
prop("brazier_cold", (12.5, 0, 3.5), 0, tag="ruin")
# the reliquary niche the round unbars
piece("wall_4x4", (19.4, 0, 5.4), 0, scale=[0.6, 1, 1])
piece("wall_4x4", (19.4, 0, 10.6), 180, scale=[0.6, 1, 1])
prop("shrine_aedicule", (21.2, 0, 8), -90, tag="base")

# ---------------------------------------------------------------- west court: the vigil garden
row("wall_4x4", (-22, 0, 0), (0, 0, 1), 4, rot=90)
row("parish_window_4m", (-22, 4, 0), (0, 0, 1), 4, rot=90)
row("wall_4x4", (-16, 0, -0.5), (1, 0, 0), 2, rot=0)
row("wall_4x4", (-16, 0, 14.5), (1, 0, 0), 2, rot=180)
for at, rot in [((-12, 0, 3), 15), ((-18, 0, 3), -20), ((-12, 0, 11), -160), ((-18, 0, 11), 160)]:
    prop("garden_bed", at, rot, tag="glory")
    prop("garden_bed_dead", at, rot, tag="ruin")
piece("statue_orans", (-15, 0, 11.4), 180)
# the keepers' chapel niche (the candles unbar it)
piece("wall_4x4", (-19.4, 0, 5.4), 0, scale=[0.6, 1, 1])
piece("wall_4x4", (-19.4, 0, 10.6), 180, scale=[0.6, 1, 1])
prop("altar", (-21.2, 0, 8), 90, tag="base")

# ---------------------------------------------------------------- the Lightfall dais
for a, rot in [((-6.4, 0, 23.4), 40), ((6.4, 0, 23.4), -40), ((-6.4, 0, 29.4), 140), ((6.4, 0, 29.4), -140)]:
    prop("candelabra", a, rot)
prop("mosaic_medallion", (0, 0.02, 26.5), 0)

# ---------------------------------------------------------------- perimeter rails + falls barred
row("balustrade_4m", (-20, 0, 30.2), (1, 0, 0), 11, rot=180, skip=[5])
blocker((-22.4, 0, 30.4), (22.4, 3, 31.2))
row("balustrade_4m", (-22.2, 0, 16), (0, 0, 1), 4, rot=90)
blocker((-23.0, 0, 14.2), (-22.2, 3, 30.6))
row("balustrade_4m", (22.2, 0, 16), (0, 0, 1), 4, rot=-90)
blocker((22.2, 0, 14.2), (23.0, 3, 30.6))
# avenue rails between courts and stair (gaps at the court mouths)
row("balustrade_4m", (-7, 0, -10), (0, 0, 1), 3, rot=90, skip=[])
row("balustrade_4m", (7, 0, -10), (0, 0, 1), 3, rot=-90, skip=[])
blocker((-22.6, 0, -12.6), (-16.2, 6, -11.8))
blocker((16.2, 0, -12.6), (22.6, 6, -11.8))

# ---------------------------------------------------------------- palaces beyond (inaccessible)
SKY = [{"kit": "city_panorama", "at": [0, -7, 0]}]
for at in [(48, -3, -46), (-54, -2, -32), (40, -5, 40), (-46, -6, 46), (-2, -9, -74), (66, -8, 6)]:
    SKY.append({"kit": "cathedral_mass", "at": [at[0], at[1], at[2]], "rot": (at[0] * 7) % 360})
    SKY.append({"kit": "spire_tower_b", "at": [at[0] + 7, at[1], at[2] + 5], "rot": (at[0] * 13) % 360})
    SKY.append({"kit": "spire_tower_c", "at": [at[0] - 6, at[1], at[2] - 4], "rot": (at[0] * 29) % 360})

# ---------------------------------------------------------------- lore
PLQ.append({"at": [2.2, 0, 25.4], "rot": -160, "text":
    "THE GILDED SANCTUM\n\nYou stand above the hours. This is the light the kingdom banked toward — undimmed, unforgetting, the vault where the morning is kept.\n\nWalk softly. Every palace you see was promised to someone."})
PLQ.append({"at": [-3.4, 2, -22.8], "rot": 20, "text":
    "THE DOOR OF THE HOUR\n\nThirteen bells were sworn to open it. Twelve rang true and one came late.\n\nIt does not open for grief. It does not open for gold. It opens for the hour — and the hour is yours to ring."})
PLQ.append({"at": [-13.2, 0, 6.2], "rot": 130, "text":
    "THE TWELVE'S GARDEN\n\nOne bed for each keeper who kept their hour. The soil remembers their names even here.\n\nThe thirteenth bed was never planted. There is still room."})
PLQ.append({"at": [12.6, 0, 6.4], "rot": -120, "text":
    "THE OFFICES OF THE HOUR\n\nSound the offices as the day was kept aloft: the dawn office first, then the noon, then the dusk.\n\nKeep the order and the reliquary opens. Break it and begin the day again."})
PLQ.append({"at": [-17.5, 0, 5.0], "rot": 120, "tag": "ruin", "text":
    "A NOTE, IN A KNIGHT'S HAND\n\nGone to do what can still be done. If you read this, Latecomer, then do not follow — AMEND.\n\nSeek the wardens you put to rest, every one, in the light their quarters remember. Kneel at their vigils. Kindle the glory. Speak to them, and hear what the dark never let you hear.\n\nWhen every one of them has forgiven you — or refused to — come back to the light, and ring what is owed.\n\n— A."})
PLQ.append({"at": [-8.5, 0, 29.0], "rot": 175, "text":
    "THE PALACES BEYOND\n\nThe wards of the light: promised halls for every soul the wax was keeping.\n\nNo road runs to them. Roads are for the unfinished. When the hour rings, no one here will need one."})

# ---------------------------------------------------------------- data
def main():
    data = {
        "id": "gilded_sanctum",
        "name": "The Gilded Sanctum",
        "start": {"pos": [0, 0.2, 27], "yaw": 0},
        "no_gutter": True,
        "stub_label": "Keep vigil  (rest — the light here does not falter)",
        "env": {
            "glory": {"sun_rot": [-34, -40], "sun_color": [1.0, 0.93, 0.74],
                      "sun_energy": 1.35, "fog_density": 0.008,
                      "fog_color": [0.74, 0.57, 0.32]},
            "ruin": {"sun_rot": [-30, -40], "sun_color": [0.9, 0.72, 0.5],
                     "sun_energy": 0.5, "fog_density": 0.012,
                     "fog_color": [0.34, 0.27, 0.19]},
        },
        "fills": F,
        "rows": R,
        "pieces": P,
        "props": PR,
        "boxes": B,
        "blockers": BL,
        "skyline": SKY,
        "open_air_regions": [{"min": [-22, 0, -12], "max": [22, 0, 30]},
                             {"min": [-16, 2, -24], "max": [16, 2, -12]}],
        "plaques": PLQ,
        "npcs": [
            {"id": "knight_sanctum", "at": [-17.5, 0, 5.0], "rot": 120, "tag": "glory"},
        ],
        "lanterns": [
            {"id": "sanctum", "name": "The Unfaltering Vigil", "at": [-15, 0, 7], "rot": 160},
        ],
        "chime_puzzles": [{
            "flag": "sanctum_hours",
            "kit": "chime_stone",
            "verb": "Sound",
            "chimes": [
                {"id": "dawn", "label": "the dawn office", "at": [11.5, 0, 3.0], "rot": 140},
                {"id": "noon", "label": "the noon office", "at": [15.0, 0, 12.2], "rot": 190},
                {"id": "dusk", "label": "the dusk office", "at": [18.5, 0, 3.0], "rot": 220},
            ],
            "order": ["dawn", "noon", "dusk"],
        }],
        "votive_locks": [{
            "flag": "sanctum_candles",
            "votives": [
                {"at": [-7.0, 0, 22.6], "rot": 40},
                {"at": [7.0, 0, 22.6], "rot": -40},
                {"at": [-5.6, 0, -9.4], "rot": 150},
                {"at": [5.6, 0, -9.4], "rot": -150},
            ],
        }],
        "flag_gates": [
            {"flag": "sanctum_hours", "kit": "gate_iron", "at": [19.4, 0, 8.0],
             "rot": -90, "tag": "base"},
            {"flag": "sanctum_candles", "kit": "gate_iron", "at": [-19.4, 0, 8.0],
             "rot": 90, "tag": "base"},
        ],
        "pickups": [
            {"id": "sanctum_reliquary", "at": [20.3, 0, 9.4], "orisons": 900,
             "label": "Take up the reliquary tithe", "tag": "base"},
            {"id": "sanctum_chapel", "at": [-20.3, 0, 9.4], "orisons": 400,
             "item": "candleglass", "count": 2,
             "label": "Gather the keepers' candleglass", "tag": "base"},
        ],
        "portals": [
            {"to": "basilica_porch", "at": [0, 0, 31.0], "rot": 180,
             "spawn": [0, -2.42, 17.0], "spawn_yaw": 0,
             "prompt": "Descend the lightfall"},
        ],
    }
    with open(PATH, "w") as f:
        json.dump(data, f, indent=1)
    print("wrote", PATH)


if __name__ == "__main__":
    main()
