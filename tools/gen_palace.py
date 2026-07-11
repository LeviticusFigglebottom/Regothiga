#!/usr/bin/env python3
"""Author data/areas/hour_palace.json: the Palace of the Hour — the gilded
house behind the Door of the Hour, and the largest interior in the game.

A vaulted great nave runs the spine, colonnaded, lit by its own clerestory.
Two full wings branch off it — the Carillon (east: four chimes rung in the
day's order) and the Hundred Candles (west: five keepers' lights) — each a
loop of rooms with doors joining every neighbour, a guarded reward, and a
stair back down to the Sanctum. The west Waxworks hides the Lightwell, a
one-way leap all the way home to the porch. Both wing rites together unbar
the HOUR GATE at the nave's head; the antechamber beyond stands ready for
the one who keeps it (not yet — the room waits).

A Scion of Light meets the first crossing of the threshold, reads the
pilgrim, names them infidel, and orders the wards of the morning to attack
on sight. Gilded Echo guards hold every room thereafter.

Deterministic and idempotent:
    python3 tools/gen_palace.py && python3 tools/audit_areas.py hour_palace
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "data", "areas", "hour_palace.json")

P = []    # pieces
F = []    # fills
VF = []   # vault fields
PR = []   # props
BL = []   # blockers
PLQ = []  # plaques
SPAWN = []


def piece(kit, at, rot=0, **kw):
    d = {"kit": kit, "at": list(at), "rot": rot}
    d.update(kw)
    P.append(d)


def prop(kit, at, rot=0, tag="base", **kw):
    d = {"kit": kit, "at": list(at), "rot": rot, "tag": tag}
    d.update(kw)
    PR.append(d)


def wall_run_x(z, x0, x1, rot, y=0.0, doors=(), kit="palace_wall_4x4"):
    """Wall along X from x0..x1 at fixed z: 4 m pieces, scaled fillers, and
    a palace portal centred on each door mark (the run cuts around them)."""
    marks = sorted(doors)
    x = x0
    for dx in marks:
        seg_end = dx - 2.0
        while x < seg_end - 0.01:
            w = min(4.0, seg_end - x)
            c = x + w * 0.5
            if w >= 3.99:
                piece(kit, (c, y, z), rot)
            else:
                piece(kit, (c, y, z), rot, scale=[w / 4.0, 1, 1])
            x += w
        piece("palace_portal_4m", (dx, y, z), rot)
        x = dx + 2.0
    while x < x1 - 0.01:
        w = min(4.0, x1 - x)
        c = x + w * 0.5
        if w >= 3.99:
            piece(kit, (c, y, z), rot)
        else:
            piece(kit, (c, y, z), rot, scale=[w / 4.0, 1, 1])
        x += w


def wall_run_z(x, z0, z1, rot, y=0.0, doors=(), kit="palace_wall_4x4"):
    """Wall along Z from z0..z1 at fixed x. Doors as in wall_run_x. To land
    doors on their marks, the run is cut into segments around each door."""
    marks = sorted(doors)
    z = z0
    for dz in marks:
        seg_end = dz - 2.0
        while z < seg_end - 0.01:
            w = min(4.0, seg_end - z)
            c = z + w * 0.5
            if w >= 3.99:
                piece(kit, (x, y, c), rot)
            else:
                piece(kit, (x, y, c), rot, scale=[w / 4.0, 1, 1])
            z += w
        piece("palace_portal_4m", (x, y, dz), rot)
        z = dz + 2.0
    while z < z1 - 0.01:
        w = min(4.0, z1 - z)
        c = z + w * 0.5
        if w >= 3.99:
            piece(kit, (x, y, c), rot)
        else:
            piece(kit, (x, y, c), rot, scale=[w / 4.0, 1, 1])
        z += w


def window_run_z(x, z0, z1, rot):
    z = z0
    while z < z1 - 0.01:
        w = min(4.0, z1 - z)
        c = z + w * 0.5
        if w >= 3.99:
            piece("palace_window_4m", (x, 4, c), rot)
        else:
            piece("palace_wall_4x4", (x, 4, c), rot, scale=[w / 4.0, 1, 1])
        z += w


def window_run_x(z, x0, x1, rot):
    x = x0
    while x < x1 - 0.01:
        w = min(4.0, x1 - x)
        c = x + w * 0.5
        if w >= 3.99:
            piece("palace_window_4m", (c, 4, z), rot)
        else:
            piece("palace_wall_4x4", (c, 4, z), rot, scale=[w / 4.0, 1, 1])
        x += w


# ---------------------------------------------------------------- floors
F.append({"kit": "palace_floor_4x4", "min": [-10, 0, 0], "max": [10, 0, 72]})
F.append({"kit": "palace_floor_4x4", "min": [10, 0, 8], "max": [42, 0, 40]})
F.append({"kit": "palace_floor_4x4", "min": [-42, 0, 8], "max": [-10, 0, 40]})

# ---------------------------------------------------------------- vaults (roofs)
VF.append({"min": [-10, 0, 0], "max": [10, 0, 56], "spring_top": 8})    # great nave
VF.append({"min": [-10, 0, 56], "max": [10, 0, 72], "spring_top": 8})   # antechamber
for s in (1, -1):
    a, b = (10, 26) if s > 0 else (-26, -10)
    g0, g1 = (26, 42) if s > 0 else (-42, -26)
    VF.append({"min": [a, 0, 8], "max": [b, 0, 24]})                    # room 1
    VF.append({"min": [a, 0, 24], "max": [b, 0, 28]})                   # cross-corridor
    VF.append({"min": [a, 0, 28], "max": [b, 0, 40]})                   # room 3
    VF.append({"min": [g0, 0, 8], "max": [g1, 0, 40], "spring_top": 8}) # long gallery

# ---------------------------------------------------------------- the great nave
# south wall + the way back out
wall_run_x(0, -10, 10, 0, doors=(0,))
window_run_x(0, -10, 10, 0)
piece("door_leaf", (0, 0, 0.18), 0, scale=[1.2, 1.3, 1.2])   # the Door, shut
BL.append({"min": [-2.2, 0, -0.8], "max": [2.2, 4, 0.0], "tag": "base"})
# nave flanks: solid to the wings, one door + one colonnade mouth each side
for s in (1, -1):
    x = 10 * s
    rot = -90 if s > 0 else 90
    wall_run_z(x, 0, 8, rot)                                # before the wings
    wall_run_z(x, 8, 24, rot, doors=(12,))                  # room 1 shares this wall
    piece("palace_arcade_4m", (x, 0, 26), rot)              # the wing mouth
    wall_run_z(x, 28, 40, rot)                              # room 3 shares this wall
    wall_run_z(x, 40, 56, rot)
    window_run_z(x, 0, 56, rot)                             # glowing clerestory
    piece("palace_cornice_4m", (x, 8, 28), rot)
# the colonnade: stacked piers make full-height columns
for s in (1, -1):
    for z in (8, 16, 24, 32, 40, 48):
        piece("palace_pier", (6 * s, 0, z), 0)
        piece("palace_pier", (6 * s, 4.1, z), 0, collide=False)
# nave dressing: the feast that was never cleared — twin banquet rows,
# a processional runner the length of the hall, chandeliers under every
# other vault, banners on the clerestory
for z in (10, 26, 42):
    prop("carpet_runner_8m", (0, 0.02, z + 4), 90)
for z in (14, 34):
    for sd in (1, -1):
        prop("banquet_table_6m", (3.6 * sd, 0, z + 2), 90)
        prop("banquet_bench_6m", (2.2 * sd, 0, z + 2), 90)
        prop("banquet_bench_6m", (5.0 * sd, 0, z + 2), 90)
for z in (12, 24, 36, 48):
    prop("chandelier_gilt", (0, 6.9, z), 0, collide=False)
for z in (6, 20, 34, 48):
    for sd in (1, -1):
        prop("banner", (9.55 * sd, 4.4, z), -90 if sd > 0 else 90, collide=False)
for z in (12, 28, 44):
    prop("candelabra", (-6.5, 0, z), 20)
    prop("candelabra", (6.5, 0, z), -20)
for s in (1, -1):
    piece("statue_saint", (4 * s, 0, 52), 180)
for z in (20, 36):
    prop("candelabra", (-9.2, 0, z), 90)
    prop("candelabra", (9.2, 0, z), -90)
prop("censer_hanging", (0, 6.2, 18), 0, collide=False)
prop("censer_hanging", (0, 6.2, 40), 0, collide=False)

# ---------------------------------------------------------------- the Hour Gate
wall_run_x(56, -10, -2, 0)
wall_run_x(56, 2, 10, 0)
piece("palace_wall_4x4", (0, 4, 56), 0)   # y4 band over the gate bay
window_run_x(56, -10, -2, 0)
window_run_x(56, 2, 10, 0)
piece("palace_pier", (-2, 0, 56), 0)
piece("palace_pier", (2, 0, 56), 0)
piece("gilt_finial", (-2, 4.2, 56), 0, collide=False)
piece("gilt_finial", (2, 4.2, 56), 0, collide=False)

# ---------------------------------------------------------------- antechamber (the room that waits)
for s in (1, -1):
    wall_run_z(10 * s, 56, 72, -90 if s > 0 else 90)
    window_run_z(10 * s, 56, 72, -90 if s > 0 else 90)
wall_run_x(72, -10, 10, 180)
window_run_x(72, -10, 10, 180)
for a, r in [((-6.4, 0, 62), 40), ((6.4, 0, 62), -40), ((-6.4, 0, 70), 140), ((6.4, 0, 70), -140)]:
    prop("candelabra", a, r)
prop("mosaic_medallion", (0, 0.02, 65), 0)
prop("carpet_runner_8m", (0, 0.02, 61), 90)
prop("chandelier_gilt", (0, 6.9, 64), 0, collide=False)
piece("statue_orans", (0, 0, 70.4), 180)
piece("statue_saint", (-7.5, 0, 70.5), 160)
piece("statue_saint", (7.5, 0, 70.5), -160)

# ---------------------------------------------------------------- the wings
for s in (1, -1):
    rot_in = -90 if s > 0 else 90    # faces the nave / inward
    rot_out = 90 if s > 0 else -90
    xo = 42 * s                      # outer wall line
    xm = 26 * s                      # mid partition line
    # perimeter
    wall_run_x(8, min(10 * s, xo), max(10 * s, xo), 0)
    wall_run_x(40, min(10 * s, xo), max(10 * s, xo), 180,
               doors=(36 * s,))                              # the stair door
    piece("door_leaf", (36 * s, 0, 39.82), 180, scale=[1.2, 1.3, 1.2])
    BL.append({"min": [36 * s - 2.2, 0, 40.0], "max": [36 * s + 2.2, 4, 40.8], "tag": "base"})
    wall_run_z(xo, 8, 40, rot_out)
    window_run_z(xo, 8, 40, rot_out)                         # gallery glazing
    # gallery upper band on its inner wall + ends
    z = 8
    while z < 40 - 0.01:
        piece("palace_wall_4x4", (xm, 4, z + 2), rot_in)
        z += 4
    window_run_x(8, min(xm, xo), max(xm, xo), 0)
    window_run_x(40, min(xm, xo), max(xm, xo), 180)
    # mid partition with three doors (room1, corridor, room3 into the gallery)
    wall_run_z(xm, 8, 40, rot_in, doors=(16, 26, 34))
    # room partitions off the cross-corridor
    wall_run_x(24, min(10 * s, xm), max(10 * s, xm), 0, doors=(18 * s,))
    wall_run_x(28, min(10 * s, xm), max(10 * s, xm), 180, doors=(18 * s,))
    # junction piers
    for (px, pz) in [(10 * s, 8), (10 * s, 24), (10 * s, 28), (10 * s, 40),
                     (xm, 8), (xm, 24), (xm, 28), (xm, 40), (xo, 8), (xo, 40)]:
        piece("palace_pier", (px, 0, pz), 0)
    # shared wing dressing
    prop("candelabra", (18 * s, 0, 12), 0)
    prop("candelabra", (18 * s, 0, 36), 180)
    prop("candelabra", (34 * s, 0, 20), rot_in)
    prop("mosaic_medallion", (18 * s, 0.02, 16), 0)
    prop("chandelier_gilt", (18 * s, 4.6, 16), 0, collide=False)
    prop("chandelier_gilt", (34 * s, 6.9, 16), 0, collide=False)
    prop("chandelier_gilt", (34 * s, 6.9, 32), 0, collide=False)
    prop("carpet_runner_8m", (34 * s, 0.02, 24), 90)
    prop("banner", (41.55 * s, 4.4, 16), rot_out, collide=False)
    prop("banner", (41.55 * s, 4.4, 32), rot_out, collide=False)

# ---- east wing character: the ringers' house
prop("banquet_bench_6m", (18, 0, 19.5), 90, scale=[0.6, 1, 1])   # practice pews
prop("banquet_bench_6m", (21.5, 0, 19.5), 90, scale=[0.6, 1, 1])
prop("censer_hanging", (18, 3.6, 12), 0, collide=False)
prop("bell_great", (34, 5.4, 20), 0, collide=False)              # the mother bell
prop("carpet_runner_8m", (18, 0.02, 33), 0)
prop("shrine_aedicule", (22, 0, 36.5), 180)                      # reliquary shrine
prop("candle_cluster", (20, 0, 38.2), 0)
prop("candle_cluster", (24, 0, 38.4), 0)
prop("book_stack", (12.5, 0, 30.5), 20)

# ---- west wing character: the scribes' house and the wax
for sx in (-24.3, -21.5, -18.7, -15.9):
    prop("scriptorium_shelf", (sx, 0, 8.5), 0)                   # W1 south wall
prop("banquet_table_6m", (-18, 0, 16), 0)                        # copy desks
prop("book_stack", (-17.6, 0.9, 16.0), 15, collide=False)
prop("scroll_pile", (-18.9, 0.9, 16.0), -10, collide=False)
prop("banquet_bench_6m", (-18, 0, 14.6), 0)
for sz in (12.5, 20, 27.5, 35):
    prop("scriptorium_shelf", (-41.5, 0, sz), 90)                # W2: books face the room (+X)
for (cx, cz) in [(-30.5, 10.5), (-37.5, 15.5), (-30.5, 21), (-37.5, 27), (-30.5, 33), (-36.5, 38)]:
    prop("candle_cluster", (cx, 0, cz), (cx * 13) % 360)         # the long watch burns
prop("altar", (-18, 0, 30.5), 0)                                 # the waxworks
prop("candle_cluster", (-18.55, 1.35, 30.4), 70, collide=False)  # wax pooled on the slab
prop("book_stack", (-17.45, 1.35, 30.65), -25, collide=False)    # the chandler's ledger
prop("wellhead", (-20, 0, 36), 30)                               # the Lightwell itself
prop("candle_cluster", (-15.5, 0, 32.5), 40)
prop("candle_cluster", (-21, 0, 33), -30)
prop("censer_hanging", (-18, 3.6, 34), 0, collide=False)

# guards of the morning: they hold every room once the Scion has spoken
for (ex, ez, face) in [(6, 18, 180), (-6, 34, 0),
                       (18, 16, 90), (34, 24, -90), (18, 34, 90),
                       (-22, 20, -90), (-34, 24, 90), (-16, 31.5, -90)]:
    SPAWN.append({"id": "guard_%d_%d" % (int(ex), int(ez)), "enemy": "gilded_echo",
                  "at": [ex, 0, ez], "face": face, "tag": "glory"})

# ---------------------------------------------------------------- lore
PLQ.append({"at": [3.2, 0, 2.6], "rot": -150, "text":
    "THE PALACE OF THE HOUR\n\nHere the morning was kept before it was rung: twelve offices, one gate, one bell that never came.\n\nThe house is awake. Walk as a debt walks — quickly, and owing."})
PLQ.append({"at": [11.2, 0, 25.2], "rot": -110, "text":
    "THE BELLMAN'S ECHO\n\nThe mother bell remembers the day better than any plaque. ASK her, and she will sing a phrase of it — watch which offices take her light.\n\nAnswer the phrase back, office by office, in her order. She does not repeat herself kindly, but she will always sing again."})
PLQ.append({"at": [-11.2, 0, 25.2], "rot": 110, "text":
    "THE UNLIT PROCESSION\n\nSix keepers' stands walk a ring in the vault. Fire is not obedient here: carry the flame to any stand and its NEIGHBOURS take the change as well — lit gutters, dark kindles, three at every stroke.\n\nThe wing rests when the whole procession burns. Walk it with intent; an idle touch digs a hole your reason must climb out of."})
PLQ.append({"at": [3.4, 0, 54.2], "rot": -160, "text":
    "THE HOUR GATE\n\nTwo rites unbar it: the day rung true, the watch lit whole.\n\nBeyond, the Hour itself is kept. Nothing in this house wants you past this door."})
PLQ.append({"at": [0, 0, 66.5], "rot": 180, "text":
    "THE ANTECHAMBER\n\nA throne of light, empty. A floor swept for a duel no servant will name.\n\nWhoever keeps the Hour has not forgotten you are coming."})
PLQ.append({"at": [38.6, 0, 37.6], "rot": -140, "text":
    "THE BELL-STAIR\n\nDown, and down, and out by the Offices — the short way the ringers kept."})
PLQ.append({"at": [-20.5, 0, 37.4], "rot": 120, "text":
    "THE LIGHTWELL\n\nThe palace drops its spent light down this well, all the way to the porch of the Basilica.\n\nThe fall is long. The light remembers how to be a road."})

# ---------------------------------------------------------------- data
def main():
    data = {
        "id": "hour_palace",
        "name": "The Palace of the Hour",
        "start": {"pos": [0, 0.2, 3], "yaw": 0},
        "no_gutter": True,
        "stub_label": "Keep vigil  (rest — the light here does not falter)",
        "env": {
            "glory": {"sun_rot": [-38, -30], "sun_color": [1.0, 0.93, 0.76],
                      "sun_energy": 0.85, "fog_density": 0.014,
                      "fog_color": [0.6, 0.47, 0.28],
                      "music": "res://assets/audio/theme_sanctum.mp3"},
            "ruin": {"sun_rot": [-38, -30], "sun_color": [0.8, 0.68, 0.5],
                     "sun_energy": 0.45, "fog_density": 0.018,
                     "fog_color": [0.3, 0.24, 0.17],
                     "music": "res://assets/audio/theme_sanctum.mp3"},
        },
        "fills": F,
        "vault_fields": VF,
        "pieces": P,
        "props": PR,
        "blockers": BL,
        "plaques": PLQ,
        "spawners": SPAWN,
        "lanterns": [
            {"id": "palace", "name": "The Threshold Vigil", "at": [6.5, 0, 4], "rot": -140},
        ],

        "flag_gates": [
            {"flag": "palace_gate_open", "kit": "gate_iron", "at": [0, 0, 56],
             "rot": 0, "scale": [1.7, 1.8, 1.0], "tag": "base"},
        ],
        "scripted": [
            {"script": "res://src/world/scion_herald.gd", "at": [0, 0, 9], "tag": "base",
             "params": {"trigger_radius": 9.0}},
            {"script": "res://src/world/echo_bell.gd", "at": [26, 0, 24], "tag": "base",
             "params": {"flag": "palace_hours", "bell_at": [34, 0, 20], "chimes": [
                 {"id": "dawn", "label": "the dawn office", "at": [14, 0, 12], "rot": 120},
                 {"id": "noon", "label": "the noon office", "at": [38, 0, 12], "rot": -120},
                 {"id": "dusk", "label": "the dusk office", "at": [38, 0, 36], "rot": -60},
                 {"id": "midnight", "label": "the midnight office", "at": [14, 0, 36], "rot": 60}]}},
            {"script": "res://src/world/procession_lock.gd", "at": [-34, 0, 16], "tag": "base",
             "params": {"flag": "palace_candles", "stands": [
                 [-38, 0, 11], [-33, 0, 10], [-29.5, 0, 14],
                 [-29.5, 0, 19], [-33, 0, 22.5], [-38, 0, 21]]}},
            {"script": "res://src/world/seal_gate.gd", "at": [0, 0, 52], "tag": "base",
             "params": {"flags": ["palace_hours", "palace_candles"],
                        "target": "palace_gate_open",
                        "notice": "Far off, the Hour Gate grinds its bars open."}},
        ],
        "pickups": [
            {"id": "palace_carillon", "at": [22, 0, 38], "orisons": 1400,
             "label": "Take up the ringers' tithe", "tag": "base"},
            {"id": "palace_scriptorium", "at": [-22, 0, 10], "orisons": 800,
             "item": "candleglass", "count": 3,
             "label": "Gather the scribes' candleglass", "tag": "base"},
        ],
        "portals": [
            {"to": "gilded_sanctum", "at": [0, 0, 1.0], "rot": 180,
             "spawn": [0, 2.2, -21.5], "spawn_yaw": 180,
             "prompt": "Leave by the Door of the Hour"},
            {"to": "gilded_sanctum", "at": [36, 0, 39], "rot": 0,
             "spawn": [15, 0.2, 3.0], "spawn_yaw": 180,
             "prompt": "Descend the bell-stair"},
            {"to": "gilded_sanctum", "at": [-36, 0, 39], "rot": 0,
             "spawn": [-15, 0.2, 3.0], "spawn_yaw": 180,
             "prompt": "Descend the candle-stair"},
            {"to": "basilica_porch", "at": [-20, 0, 34], "rot": 90,
             "spawn": [0, -2.42, 17], "spawn_yaw": 0,
             "prompt": "Leap the lightwell"},
        ],
    }
    with open(PATH, "w") as f:
        json.dump(data, f, indent=1)
    print("wrote", PATH)


if __name__ == "__main__":
    main()
