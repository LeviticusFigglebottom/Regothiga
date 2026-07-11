#!/usr/bin/env python3
"""Author data/areas/gilded_sanctum.json: the Gilded Sanctum — the place the
lightfall carries the pilgrim, above the hours. The last place of true,
unfaltering light: a marble processional avenue between solid palace wings,
the great sealed Door of the Hour on its terrace, two cloister-courts (the
Offices of the Hour; the vigil garden) opening off the avenue through
gilded colonnades, and palaces beyond reach on every horizon.

Built from the palace kit (ivory marble + gold): every wall line is a real
building face — no free-standing stage flats — corners land on shared grid
points under marble piers, and both reward alcoves are sealed rooms whose
iron gate is the only way in.

No enemies, no wardens — lore, two puzzles (the Offices chime round; the
Keepers' Candles votive set), a rest-only vigil (the light here does not
falter), and a note in a knight's hand in the dim version. Ser Adalric
himself stays below, on the porch — no stair climbs this far.

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


def face(x, z0, count, rot, portal_at=None, filler=None):
    """One palace face: ground walls (one bay optionally a sealed portal),
    glazed windows above, cornice at the head. Runs along Z at fixed x."""
    for i in range(count):
        z = z0 + 4 * i
        if portal_at is not None and z == portal_at:
            piece("palace_portal_4m", (x, 0, z), rot)
            lean = 0.15 if rot < 0 else -0.15
            piece("door_leaf", (x + lean, 0, z), rot, scale=[1.2, 1.3, 1.2])
        else:
            piece("palace_wall_4x4", (x, 0, z), rot)
        piece("palace_window_4m", (x, 4, z), rot)
        piece("palace_cornice_4m", (x, 8, z), rot)
    if filler is not None:
        piece("palace_wall_4x4", (x, 0, filler), rot, scale=[0.5, 1, 1])
        piece("palace_wall_4x4", (x, 4, filler), rot, scale=[0.5, 1, 1])


def face_x(z, x0, count, rot, windows=True, filler=None, filler_scale=0.25, portal_at=None):
    """A palace face running along X at fixed z."""
    for i in range(count):
        x = x0 + 4 * i
        if portal_at is not None and abs(x - portal_at) < 0.01:
            piece("palace_portal_4m", (x, 0, z), rot)
            piece("palace_window_4m" if windows else "palace_wall_4x4", (x, 4, z), rot)
            piece("palace_cornice_4m", (x, 8, z), rot)
            continue
        piece("palace_wall_4x4", (x, 0, z), rot)
        if windows:
            piece("palace_window_4m", (x, 4, z), rot)
            piece("palace_cornice_4m", (x, 8, z), rot)
    if filler is not None:
        piece("palace_wall_4x4", (filler, 0, z), rot, scale=[filler_scale, 1, 1])
        if windows:
            piece("palace_wall_4x4", (filler, 4, z), rot, scale=[filler_scale, 1, 1])


# ---------------------------------------------------------------- floors
# One marble field for the whole walkable ward, plus the palace terrace.
F.append({"kit": "palace_floor_4x4", "min": [-22, 0, -12], "max": [22, 0, 30]})
F.append({"kit": "palace_floor_4x4", "min": [-16, 2, -24], "max": [16, 2, -12]})
# terrace body so the +2 m deck has a face, not a floating slab
B.append({"min": [-16, 0, -24], "max": [16, 2, -12], "tag": "base"})

# the grand stair up to the Door of the Hour (three flights abreast,
# descending SOUTH into the avenue — treads face the pilgrim; the outer
# flights carry their edge parapets so the drop is railed)
piece("stair_grand_4m_r", (-4, 2, -12), 180)
piece("stair_grand_4m", (0, 2, -12), 180)
piece("stair_grand_4m_l", (4, 2, -12), 180)

# ---------------------------------------------------------------- the Door of the Hour
# palace front along the terrace's north edge — marble and gold
row("palace_wall_4x4", (-14, 2, -24), (1, 0, 0), 3, rot=0)
row("palace_wall_4x4", (6, 2, -24), (1, 0, 0), 3, rot=0)
row("palace_wall_4x4", (-14, 6, -24), (1, 0, 0), 8, rot=0)
piece("palace_wall_4x4", (-3, 2, -24), 0, scale=[0.5, 1, 1])
piece("palace_wall_4x4", (3, 2, -24), 0, scale=[0.5, 1, 1])
piece("palace_portal_4m", (0, 2, -24), 0)
piece("door_leaf", (0, 2, -23.9), 0, scale=[1.25, 1.4, 1.2])
piece("rose_window", (0, 7.6, -23.7), 0, collide=False)
row("palace_cornice_4m", (-14, 10, -24), (1, 0, 0), 8, rot=0)
piece("palace_pediment_8m", (0, 10.3, -24), 0, collide=False)
for x in (-14, -10, -6, 6, 10, 14):
    piece("gilt_finial", (x, 10.3, -23.85), 0, collide=False)
for x in (-15.7, 15.7):
    piece("palace_pier", (x, 2, -23.6), 0)
for x in (-10, 10):
    piece("statue_saint", (x, 2, -22.6), 0)
# radiant spires crown the palace, unreachable
piece("radiant_spire_a", (0, 2, -32), 0, collide=False)
piece("radiant_spire_b", (-12, 2, -29), 40, collide=False)
piece("radiant_spire_b", (12, 2, -29), -70, collide=False)
blocker((-16.6, 2, -24.6), (16.6, 14, -23.6))
# terrace rim: gold-railed marble balustrades left and right of the stair
row("palace_balustrade_4m", (-14, 2, -12.2), (1, 0, 0), 2, rot=0)     # -16..-8
piece("palace_balustrade_4m", (-7.2, 2, -12.2), 0, scale=[0.4, 1, 1])  # -8..-6.4
row("palace_balustrade_4m", (10, 2, -12.2), (1, 0, 0), 2, rot=0)      # 8..16
piece("palace_balustrade_4m", (7.2, 2, -12.2), 0, scale=[0.4, 1, 1])   # 6.4..8
piece("palace_pier", (-6.7, 2, -12.3), 0)
piece("palace_pier", (6.7, 2, -12.3), 0)
blocker((-16.4, 2, -12.6), (-6.3, 4, -11.9))
blocker((6.3, 2, -12.6), (16.4, 4, -11.9))
# terrace flanks
blocker((-16.6, 2, -24.4), (-15.9, 4, -12.0))
blocker((15.9, 2, -24.4), (16.6, 4, -12.0))

# ---------------------------------------------------------------- the avenue
# candelabra procession down both flanks
for z in (20, 12, 4, -4):
    prop("candelabra", (-5.4, 0, z), 20)
    prop("candelabra", (5.4, 0, z), -20)
prop("mosaic_medallion", (0, 0.02, 8), 0)
prop("mosaic_medallion", (0, 0.02, -8), 0)

# ---------------------------------------------------------------- palace wings
# Solid blocks flanking the avenue (x 9..22 and -22..-9). Each court sits
# BETWEEN a north and a south wing; every wall is some building's face.
for s in (1, -1):
    xa, xw = 9 * s, 22 * s                 # avenue face line / ward edge line
    ra = -90 if s > 0 else 90              # faces the avenue (west/east)
    rw = 90 if s > 0 else -90              # faces outward at the ward edge
    x0 = 11 if s > 0 else -19              # x-runs walk +4: start at the low end
    # ---- north wing (z -12..0)
    face(xa, -10, 3, ra, portal_at=-6)                      # avenue face
    face(xw, -10, 3, rw)                                    # outer face
    face_x(-12, x0, 3, 0, filler=21.5 * s)                  # terrace-void face
    face_x(0, x0, 3, 180, filler=21.5 * s, portal_at=15 * s)   # court north wall + stair door
    piece("door_leaf", (15 * s, 0, 0.18), 180, scale=[1.2, 1.3, 1.2])
    BL.append({"min": [15 * s - 2.2, 0, -0.8], "max": [15 * s + 2.2, 4, 0.0], "tag": "base"})
    piece("gilt_finial", (15 * s, 4.3, 0.2), 0, collide=False)
    # ---- south wing (z 12..30)
    face(xa, 14, 4, ra, portal_at=18, filler=29)            # avenue face
    face(xw, 14, 4, rw, filler=29)                          # outer face
    face_x(12, x0, 3, 0, filler=21.5 * s)                   # court south wall
    face_x(30, x0, 3, 180, windows=False, filler=21.5 * s)  # south face
    # ---- the court mouth: gilded colonnade + glazed loggia above
    piece("palace_arcade_4m", (xa, 0, 4), ra)
    piece("palace_arcade_4m", (xa, 0, 8), ra)
    piece("palace_wall_4x4", (xa, 0, 1), ra, scale=[0.5, 1, 1])
    piece("palace_wall_4x4", (xa, 0, 11), ra, scale=[0.5, 1, 1])
    for z in (2, 6, 10):
        piece("palace_window_4m", (xa, 4, z), ra)
        piece("palace_cornice_4m", (xa, 8, z), ra)
    # ---- court outer wall at the ward edge
    for z in (2, 6, 10):
        piece("palace_wall_4x4", (xw, 0, z), rw)
        piece("palace_window_4m", (xw, 4, z), rw)
        piece("palace_cornice_4m", (xw, 8, z), rw)
    # ---- gold on the skyline
    for z in (-10, -2, 6, 14, 26):
        piece("gilt_finial", (xa - 0.2 * s, 8.35, z), 0, collide=False)
    piece("gargoyle", ((9 - 0.5) * s, 8.2, -4), ra)
    piece("gargoyle", ((9 - 0.5) * s, 8.2, 20), ra)
    # ---- marble piers stamp every junction
    for z in (-12, 0, 12, 30):
        piece("palace_pier", (xa, 0, z), 0)
    piece("palace_pier", (xw, 0, 0), 0)
    piece("palace_pier", (xw, 0, 12), 0)
    # ---- the sealed reward alcove (x 18..22 mirrored), gate is the ONLY way
    piece("palace_wall_4x4", (20 * s, 0, 6), 0)
    piece("palace_wall_4x4", (20 * s, 0, 10), 180)
    piece("palace_wall_4x4", (18 * s, 0, 6.4), ra, scale=[0.2, 1, 1])
    piece("palace_wall_4x4", (18 * s, 0, 9.6), ra, scale=[0.2, 1, 1])
    piece("palace_pier", (18 * s, 0, 6), 0)
    piece("palace_pier", (18 * s, 0, 10), 0)

# ---------------------------------------------------------------- east court: the Offices of the Hour
prop("brazier_lit", (16.2, 0, 5.4), 90, tag="glory")
prop("brazier_cold", (16.2, 0, 5.4), 90, tag="ruin")
prop("shrine_aedicule", (20.3, 0, 8), -90, tag="base")

# ---------------------------------------------------------------- west court: the vigil garden
for at, rot in [((-12, 0, 2.8), 15), ((-16, 0, 2.8), -20),
                ((-11.5, 0, 10.2), -160), ((-15.5, 0, 10.2), 160)]:
    prop("garden_bed", at, rot, tag="glory")
    prop("garden_bed_dead", at, rot, tag="ruin")
piece("statue_orans", (-13.5, 0, 4.8), 180)
prop("mosaic_medallion", (-13.5, 0.02, 8.4), 0)
prop("altar", (-20.7, 0, 8), 90, tag="base")

# ---------------------------------------------------------------- the Lightfall dais
for a, rot in [((-6.4, 0, 23.4), 40), ((6.4, 0, 23.4), -40), ((-6.4, 0, 29.4), 140), ((6.4, 0, 29.4), -140)]:
    prop("candelabra", a, rot)
prop("mosaic_medallion", (0, 0.02, 26.5), 0)

# ---------------------------------------------------------------- south rim (falls barred)
row("palace_balustrade_4m", (-8, 0, 30.2), (1, 0, 0), 5, rot=180, skip=[2])
blocker((-9, 0, 30.4), (-2.2, 3, 31.4))
blocker((2.2, 0, 30.4), (9, 3, 31.4))
# the lightfall landing: a railed marble balcony carrying the descent portal
# past the rim. Exactly as wide as the rim balustrade's gap, side rails
# running its full depth and the end rail overlapping their ends — the
# handrails meet at every corner instead of crossing or falling short.
B.append({"min": [-2.2, -0.8, 30], "max": [2.2, 0, 33.4], "tag": "base", "walkable": True})
piece("palace_balustrade_4m", (-2.05, 0, 31.8), 90, scale=[0.8, 1, 1])
piece("palace_balustrade_4m", (2.05, 0, 31.8), -90, scale=[0.8, 1, 1])
piece("palace_balustrade_4m", (0, 0, 33.4), 180, scale=[1.1, 1, 1])
blocker((-2.9, 0, 30.2), (-2.2, 3, 33.8))
blocker((2.2, 0, 30.2), (2.9, 3, 33.8))
blocker((-2.6, 0, 33.5), (2.6, 3, 34.1))

# ---------------------------------------------------------------- palaces beyond (inaccessible)
# A zone of its own, IN the sky: no mortal city below — only radiant marble
# castles and needle spires ringing the horizon, nested in the cloud sea.
import math as _m
import random as _random

SKY = []
_rng = _random.Random(7)
_CLOUDS = ["cloud_bank_a", "cloud_bank_b", "cloud_bank_c"]


def _cloud_bed(x, y, z, spread, n, s_lo=1.6, s_hi=2.6):
    """Cloud banks massed around a footing so no structure shows a bottom
    edge — everything RISES from the sea instead of floating in it."""
    for k in range(n):
        cs = _rng.uniform(s_lo, s_hi)
        SKY.append({"kit": _CLOUDS[(k + int(x)) % 3],
                    "at": [round(x + _rng.uniform(-spread, spread), 1),
                           round(y + _rng.uniform(-2.0, 1.5), 1),
                           round(z + _rng.uniform(-spread * 0.8, spread * 0.8), 1)],
                    "rot": int(_rng.uniform(0, 360)), "scale": [cs, cs * 0.8, cs]})


# the far ring: radiant castles and spires on every horizon, every one
# rising out of a bed of cloud that swallows its base
for i in range(11):
    ang = (i + 0.5) / 11 * 2 * _m.pi
    r = _rng.uniform(150, 240)
    x, z = r * _m.sin(ang), -r * _m.cos(ang)
    s = _rng.uniform(1.6, 2.4)
    y = _rng.uniform(-10, 2)
    rot = int(_rng.uniform(0, 360))
    SKY.append({"kit": "radiant_castle_a" if i % 2 else "radiant_castle_b",
                "at": [round(x, 1), round(y, 1), round(z, 1)],
                "rot": rot, "scale": [s, s, s * _rng.uniform(1.0, 1.2)]})
    st = _rng.uniform(1.6, 2.6)
    sx = x + 16 * s * _m.cos(ang)
    sz = z + 16 * s * _m.sin(ang)
    SKY.append({"kit": "radiant_spire_a" if i % 3 else "radiant_spire_b",
                "at": [round(sx, 1), round(y + _rng.uniform(-2, 2), 1), round(sz, 1)],
                "rot": (rot * 3) % 360, "scale": [st, st, st * 1.15]})
    _cloud_bed(x, y + 2.0, z, 20 * s * 0.8, 3, 1.8, 2.8)
    _cloud_bed(sx, y + 1.5, sz, 9 * st * 0.8, 2, 1.2, 1.9)

# mid-distance sentinels: lone radiant needles rising straight from the sea
for i in range(5):
    ang = i / 5 * 2 * _m.pi + 0.6
    r = _rng.uniform(72, 118)
    st = _rng.uniform(1.1, 1.7)
    x, z = r * _m.sin(ang), -r * _m.cos(ang)
    y = _rng.uniform(-14, -8)
    SKY.append({"kit": "radiant_spire_b" if i % 2 else "radiant_spire_a",
                "at": [round(x, 1), round(y, 1), round(z, 1)],
                "rot": int(_rng.uniform(0, 360)), "scale": [st, st, st]})
    _cloud_bed(x, y + 2.5, z, 8 * st, 2, 1.1, 1.7)

# streaming light + the living cloud sea (the clouds orbit, slow and stately)
SCRIPTED = [
    {"script": "res://src/world/god_rays.gd", "at": [0, 0, 6], "tag": "glory",
     "params": {"count": 7, "span_x": 26.0, "span_z": 22.0, "seed_v": 7, "sun": [-34, -40]}},
    {"script": "res://src/world/sky_clouds.gd", "at": [0, 0, 4], "tag": "base",
     "params": {"low_count": 26, "high_count": 10, "under_count": 8, "drift": 1.1, "seed_v": 5}},
]

# ---------------------------------------------------------------- lore
PLQ.append({"at": [2.2, 0, 25.4], "rot": -160, "text":
    "THE GILDED SANCTUM\n\nYou stand above the hours. This is the light the kingdom banked toward — undimmed, unforgetting, the vault where the morning is kept.\n\nWalk softly. Every palace you see was promised to someone."})
PLQ.append({"at": [-3.4, 2, -22.8], "rot": 20, "text":
    "THE DOOR OF THE HOUR\n\nThirteen bells were sworn to open it. Twelve rang true and one came late.\n\nIt does not open for grief. It does not open for gold. It opens for the hour — and the hour is yours to ring."})
PLQ.append({"at": [-15.4, 0, 6.4], "rot": 115, "text":
    "THE TWELVE'S GARDEN\n\nOne bed for each keeper who kept their hour. The soil remembers their names even here.\n\nThe thirteenth bed was never planted. There is still room."})
PLQ.append({"at": [12.4, 0, 6.2], "rot": -120, "text":
    "THE OFFICES OF THE HOUR\n\nSound the offices as the day was kept aloft: the dawn office first, then the noon, then the dusk.\n\nKeep the order and the reliquary opens. Break it and begin the day again."})
PLQ.append({"at": [-12.4, 0, 9.6], "rot": 25, "tag": "ruin", "text":
    "A NOTE, IN A KNIGHT'S HAND\n\nGone to do what can still be done. If you read this, Latecomer, then do not follow — AMEND.\n\nSeek the wardens you put to rest, every one, in the light their quarters remember. Kneel at their vigils. Kindle the glory. Speak to them, and hear what the dark never let you hear.\n\nWhen every one of them has forgiven you — or refused to — come back to the light, and ring what is owed.\n\n— A."})

# the Apostle's stall: a banquet table of wares under a hung banner, candles
# to read prices by (glory only, like its keeper)
PR.append({"kit": "banquet_table_6m", "at": [9.4, 0, 14.6], "rot": 55, "tag": "glory"})
PR.append({"kit": "book_stack", "at": [9.0, 0.9, 14.2], "rot": 30, "tag": "glory", "collide": False})
PR.append({"kit": "scroll_pile", "at": [10.0, 0.9, 15.2], "rot": -20, "tag": "glory", "collide": False})
PR.append({"kit": "candle_cluster", "at": [7.2, 0, 15.6], "rot": 10, "tag": "glory"})
PR.append({"kit": "candle_cluster", "at": [12.1, 0, 12.3], "rot": -35, "tag": "glory"})

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
            "glory": {"sun_rot": [-34, -40], "sun_color": [1.0, 0.95, 0.8],
                      "sun_energy": 1.5, "fog_density": 0.007,
                      "fog_color": [0.78, 0.62, 0.4],
                      "music": "res://assets/audio/theme_sanctum.mp3"},
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
        "scripted": SCRIPTED,
        # the Apostle of Light keeps his outdoor church by the palace door,
        # stall dressed to be found: table, wares, candles, a hung banner
        "npcs": [
            {"id": "apostle_light", "at": [8.4, 0, 12.6], "rot": -125, "tag": "glory"},
        ],
        "open_air_regions": [{"min": [-22, 0, -12], "max": [22, 0, 30]},
                             {"min": [-16, 2, -24], "max": [16, 2, -12]},
                             {"min": [-2.2, 0, 30], "max": [2.2, 0, 33.4]}],
        "plaques": PLQ,
        "lanterns": [
            {"id": "sanctum", "name": "The Unfaltering Vigil", "at": [-13.5, 0, 8.4], "rot": 180},
        ],
        "chime_puzzles": [{
            "flag": "sanctum_hours",
            "kit": "chime_stone",
            "verb": "Sound",
            "chimes": [
                {"id": "dawn", "label": "the dawn office", "at": [12.0, 0, 2.8], "rot": 140},
                {"id": "noon", "label": "the noon office", "at": [15.5, 0, 10.7], "rot": 15},
                {"id": "dusk", "label": "the dusk office", "at": [17.3, 0, 2.8], "rot": 230},
            ],
            "order": ["dawn", "noon", "dusk"],
        }],
        "votive_locks": [{
            "flag": "sanctum_candles",
            "votives": [
                {"at": [-7.0, 0, 22.6], "rot": 40},
                {"at": [7.0, 0, 22.6], "rot": -40},
                {"at": [-7.3, 0, -9.0], "rot": 150},
                {"at": [7.3, 0, -9.0], "rot": -150},
            ],
        }],
        "flag_gates": [
            {"flag": "sanctum_hours", "kit": "gate_iron", "at": [18, 0, 8.0],
             "rot": -90, "tag": "base"},
            {"flag": "sanctum_candles", "kit": "gate_iron", "at": [-18, 0, 8.0],
             "rot": 90, "tag": "base"},
        ],
        "pickups": [
            {"id": "sanctum_reliquary", "at": [19.6, 0, 9.6], "orisons": 900,
             "label": "Take up the reliquary tithe", "tag": "base"},
            {"id": "sanctum_chapel", "at": [-19.8, 0, 8.6], "orisons": 400,
             "item": "candleglass", "count": 2,
             "label": "Gather the keepers' candleglass", "tag": "base"},
        ],
        "portals": [
            {"to": "basilica_porch", "at": [0, 0, 31.0], "rot": 180,
             "spawn": [0, -2.42, 17.0], "spawn_yaw": 0,
             "prompt": "Descend the lightfall"},
            {"to": "hour_palace", "at": [0, 2, -23.0], "rot": 0,
             "spawn": [0, 0.2, 3.0], "spawn_yaw": 0,
             "prompt": "Enter the Door of the Hour",
             "locked_flag": "sanctum_hours",
             "locked_prompt": "The Door keeps its hour \u2014 sound the Offices"},
            {"to": "hour_palace", "at": [15, 0, 1.4], "rot": 180,
             "spawn": [36, 0.2, 37.0], "spawn_yaw": 180,
             "prompt": "Climb the bell-stair",
             "locked_flag": "scion_heard",
             "locked_prompt": "Barred from above"},
            {"to": "hour_palace", "at": [-15, 0, 1.4], "rot": 180,
             "spawn": [-36, 0.2, 37.0], "spawn_yaw": 180,
             "prompt": "Climb the candle-stair",
             "locked_flag": "scion_heard",
             "locked_prompt": "Barred from above"},
        ],
    }
    with open(PATH, "w") as f:
        json.dump(data, f, indent=1)
    print("wrote", PATH)


if __name__ == "__main__":
    main()
