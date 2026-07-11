#!/usr/bin/env python3
"""Author data/areas/morrow_keep.json: THE KEEP OF THE MORROW — the final
house, a castle of white gold perched on a cloud, reached by the Stair of
Light off the Sanctum's west parapet after the pilgrim has knelt to the
Scion.

One grand coffered hallway runs the spine. SIX trial rooms flank it on
each side — twelve in all, one for each bell the Latecomer silenced, each
kept by the memory of the ringer who once raised that bell and the fate
that bought their worthiness. Each room holds a trial (arena, duel, vigil,
chime-order, votive, watcher) that pays one flag; twelve flags ring the
bell's blessing and the last door lets go — beyond it, under its own
cloister dome, hangs the THIRTEENTH BELL.

Deterministic and idempotent:
    python3 tools/gen_morrow.py && python3 tools/audit_areas.py morrow_keep
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "data", "areas", "morrow_keep.json")

P = []     # pieces
F = []     # fills
VF = []    # vault fields
PR = []    # props
BL = []    # blockers
PLQ = []   # plaques
SC = []    # scripted
CH = []    # chime puzzles
VL = []    # votive locks
WP = []    # watcher puzzles
FG = []    # flag gates
SKY = []   # skyline


def piece(kit, at, rot=0, **kw):
    d = {"kit": kit, "at": list(at), "rot": rot}
    d.update(kw)
    P.append(d)


def prop(kit, at, rot=0, tag="base", **kw):
    d = {"kit": kit, "at": list(at), "rot": rot, "tag": tag}
    d.update(kw)
    PR.append(d)


def wall_run_x(z, x0, x1, rot, y=0.0, doors=(), kit="palace_wall_4x4"):
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


COFFER = {"flat": True, "coffer": True, "lid_mat": "M_marble",
          "beam_mat": "M_gold", "band_mat": "M_marble"}

# ---------------------------------------------------------------- ground
# arrival terrace on the open cloud (z -12..0), the hall spine (0..92),
# the bell chamber (92..108). Trial rooms flank the hall at x 6..18 and
# x -18..-6, six a side.
F.append({"kit": "palace_floor_4x4", "min": [-10, 0, -12], "max": [10, 0, 0]})
F.append({"kit": "palace_floor_4x4", "min": [-6, 0, 0], "max": [6, 0, 92]})
F.append({"kit": "palace_floor_4x4", "min": [-10, 0, 92], "max": [10, 0, 108]})
# one floor slab per trial room — the slots between rooms are sealed
# voids, and a floored slot would demand a roof it doesn't have
for _k in range(6):
    _z0 = 6 + 14 * _k
    F.append({"kit": "palace_floor_4x4", "min": [-18, 0, _z0], "max": [-6, 0, _z0 + 12]})
    F.append({"kit": "palace_floor_4x4", "min": [6, 0, _z0], "max": [18, 0, _z0 + 12]})

# ---------------------------------------------------------------- ceilings
VF.append(dict(COFFER, min=[-6, 0, 0], max=[6, 0, 92], spring_top=8))     # hall
# each trial room gets its own cozy coffer lid (wall_top 4 -> lid 4.85)
for k in range(6):
    z0 = 6 + 14 * k
    VF.append(dict(COFFER, min=[-18, 0, z0], max=[-6, 0, z0 + 12]))
    VF.append(dict(COFFER, min=[6, 0, z0], max=[18, 0, z0 + 12]))
# the spans between rooms (z0+12 .. z0+14) are outside the fills — no roof
# needed; blockers seal them below. The bell chamber's ceiling is the dome.

# ---------------------------------------------------------------- terrace
# balustrade rim around the arrival cloud-porch; open sky above it
for x in (-8, -4, 0, 4, 8):
    piece("palace_balustrade_4m", (x, 0, -11.8), 0)
piece("palace_balustrade_4m", (-9.8, 0, -8), 90)
piece("palace_balustrade_4m", (9.8, 0, -8), -90)
piece("palace_balustrade_4m", (-9.8, 0, -4), 90)
piece("palace_balustrade_4m", (9.8, 0, -4), -90)
# keep front: a grand pedimented face with the one door
wall_run_x(0, -10, 10, 0, doors=(0,))
piece("palace_window_4m", (-6, 4, 0), 0)
piece("palace_window_4m", (6, 4, 0), 0)
piece("palace_pediment_8m", (0, 8, 0.2), 0)
piece("gilt_finial", (0, 10.6, 0.2), 0)
prop("candelabra", (-3.4, 0, -2.5), 20)
prop("candelabra", (3.4, 0, -2.5), -20)

# ---------------------------------------------------------------- the hall
# west/east hall walls with a door to each trial room; windows above
ROOM_DOORS = [12 + 14 * k for k in range(6)]      # door mark per room, on z
wall_run_z(-6, 0, 92, 90, doors=ROOM_DOORS)
wall_run_z(6, 0, 92, -90, doors=ROOM_DOORS)
for z in range(2, 92, 4):
    piece("palace_window_4m", (-6, 4, z), 90)
    piece("palace_window_4m", (6, 4, z), -90)
# north hall wall: the LAST DOOR into the bell chamber
wall_run_x(92, -10, 10, 180, doors=(0,))
piece("palace_window_4m", (-6, 4, 92), 180)
piece("palace_window_4m", (6, 4, 92), 180)
# the runner and the lights of the processional
for z in (10, 26, 42, 58, 74):
    prop("carpet_runner_8m", (0, 0.02, z), 90)
for z in (16, 44, 72):
    prop("chandelier_gilt", (0, 6.0, z), 0, collide=False)
for z in (8, 36, 64, 88):
    prop("candelabra", (-4.6, 0, z), 30)
    prop("candelabra", (4.6, 0, z), -30)

# ---------------------------------------------------------------- rooms
# shells: outer walls + dividers; each room 12x12, door already cut in the
# hall wall. Outer (x +-18) walls carry windows into the open sky.
for k in range(6):
    z0 = 6 + 14 * k
    for s in (1, -1):
        xo = 18 * s
        rot_o = -90 if s > 0 else 90
        wall_run_z(xo, z0, z0 + 12, rot_o)
        piece("palace_window_4m", (xo, 4, z0 + 2), rot_o)
        piece("palace_window_4m", (xo, 4, z0 + 10), rot_o)
        # south + north walls of each room
        x_in, x_out = (6, 18) if s > 0 else (-18, -6)
        wall_run_x(z0, x_in, x_out, 0)
        wall_run_x(z0 + 12, x_in, x_out, 180)

# seal the inter-room slots (z0+12..z0+14) at the outer edge so the keep
# reads as one mass from the hall; the slots are unwalkable voids
for k in range(5):
    zc = 18 + 14 * k + 1.0
    BL.append({"min": [-18, 0, zc - 1.0], "max": [-6, 8, zc + 1.0], "tag": "base"})
    BL.append({"min": [6, 0, zc - 1.0], "max": [18, 8, zc + 1.0], "tag": "base"})

# ---------------------------------------------------------------- trials
# room centres: left rooms (x -12), right rooms (x 12), z0+6
def room_c(k, side):
    return (12 * side, 0, 12 + 14 * k)

TRIALS = []   # (k, side, flag_idx)

# R1 (L,k0) — the Lampwright: vigil in the first light
c = room_c(0, -1)
SC.append({"script": "res://src/world/trial_room.gd", "at": list(c), "tag": "base",
           "params": {"flag": "morrow_trial_1", "mode": "vigil", "hold": 12.0,
                      "title": "the Trial of the First Light"}})
PLQ.append({"at": [c[0] - 4.5, 0, c[2] - 4.5], "rot": 135, "text":
    "THE FIRST RINGER — SERA, THE LAMPWRIGHT\n\nShe rang the First Bell with burned hands, having carried the vigil flame through a night the wind hated.\n\nHer fate: she never again stood in a light she had not made. She was deemed worthy because she STOOD STILL while it hurt.\n\nStand in her light. Do not leave it."})

# R2 (R,k0) — the Tollwright: votive owed in three stands
c = room_c(0, 1)
VL.append({"flag": "morrow_trial_2", "tag": "base", "votives": [
    {"at": [c[0] - 3, 0, c[2] - 3], "rot": 45},
    {"at": [c[0] + 3, 0, c[2] - 3], "rot": -45},
    {"at": [c[0], 0, c[2] + 3.6], "rot": 180}]})
PLQ.append({"at": [c[0] - 4.5, 0, c[2] - 4.5], "rot": 135, "text":
    "THE SECOND RINGER — HARLAN, THE TOLLWRIGHT\n\nHe rang the Second Bell only after every debt in the quarter was paid — most of them out of his own purse.\n\nHis fate: he died owning nothing but the rope. He was deemed worthy because the ledger balanced.\n\nKindle all three votives. Light is paid forward here."})

# R3 (L,k1) — the Chorister: chime order
c = room_c(1, -1)
CH.append({"flag": "morrow_trial_3", "order": ["dawn", "noon", "dusk"],
           "chimes": [
               {"id": "noon", "label": "the Noon stone", "at": [c[0] - 3.2, 0, c[2] + 2.8], "rot": -135},
               {"id": "dawn", "label": "the Dawn stone", "at": [c[0], 0, c[2] - 3.6], "rot": 0},
               {"id": "dusk", "label": "the Dusk stone", "at": [c[0] + 3.2, 0, c[2] + 2.8], "rot": 135}]})
PLQ.append({"at": [c[0] + 4.5, 0, c[2] - 4.5], "rot": -135, "text":
    "THE THIRD RINGER — BRIDE VESPERINE, THE CHORISTER\n\nShe rang the Third Bell as the last note of a psalm sung alone in an empty quire.\n\nHer fate: no choir would have her after — her voice made theirs sound like counting. She was deemed worthy for singing the day in its ORDER.\n\nRing her day: dawn, then noon, then dusk."})

# R4 (R,k1) — the Warden-at-arms: arena, two echoes
c = room_c(1, 1)
SC.append({"script": "res://src/world/trial_room.gd", "at": list(c), "tag": "base",
           "params": {"flag": "morrow_trial_4", "mode": "arena",
                      "foes": ["gilded_echo", "gilded_echo"],
                      "spots": [[-2.8, 0, 1.5], [2.8, 0, -1.5]], "radius": 5.5,
                      "title": "the Trial of Arms"}})
PLQ.append({"at": [c[0] + 4.5, 0, c[2] - 4.5], "rot": -135, "text":
    "THE FOURTH RINGER — SER ODILE, WARDEN-AT-ARMS\n\nShe rang the Fourth Bell with her shield arm, the right one being occupied with dying.\n\nHer fate: the wound kept her from every war after; she drilled children in the yard instead. Deemed worthy because she rang WHILE losing.\n\nHer echoes still drill. Put them down."})

# R5 (L,k2) — the Watcher: turn the watchers east
c = room_c(2, -1)
WP.append({"flag": "morrow_trial_5", "target": -90, "watchers": [
    {"at": [c[0] - 3, 0, c[2] - 2.5]},
    {"at": [c[0], 0, c[2] + 3]},
    {"at": [c[0] + 3, 0, c[2] - 2.5]}],
    "done_toast": "The watchers face the morrow. The Fifth is satisfied."})
PLQ.append({"at": [c[0] - 4.5, 0, c[2] - 4.5], "rot": 135, "text":
    "THE FIFTH RINGER — BROTHER CASSIAN, THE WATCHER\n\nHe rang the Fifth Bell at the exact instant dawn crossed the sill, having watched forty nights for it without once facing away.\n\nHis fate: his eyes never recovered the dark. Deemed worthy because he LOOKED where the light would come from.\n\nTurn every watcher to the east."})

# R6 (R,k2) — the Sellsword: duel, one morning ward
c = room_c(2, 1)
SC.append({"script": "res://src/world/trial_room.gd", "at": list(c), "tag": "base",
           "params": {"flag": "morrow_trial_6", "mode": "duel",
                      "foes": ["morning_ward"], "spots": [[0, 0, 1.0]],
                      "radius": 5.5, "title": "the Trial of the Hired Blade"}})
PLQ.append({"at": [c[0] + 4.5, 0, c[2] - 4.5], "rot": -135, "text":
    "THE SIXTH RINGER — VEY, WHO WAS PAID\n\nA sellsword rang the Sixth Bell for coin, because no believer was left standing that year.\n\nHis fate: he refused the purse at the rope's end and no one ever learned why. Deemed worthy the moment the coin stopped mattering.\n\nHis hired blade stands the room. Best it, without hiring one of your own."})

# R7 (L,k3) — the Gravedigger: arena, penitents
c = room_c(3, -1)
SC.append({"script": "res://src/world/trial_room.gd", "at": list(c), "tag": "base",
           "params": {"flag": "morrow_trial_7", "mode": "arena",
                      "foes": ["penitent", "penitent", "penitent"],
                      "spots": [[-3, 0, 0], [3, 0, 0], [0, 0, 3]], "radius": 5.5,
                      "title": "the Trial of the Spade"}})
PLQ.append({"at": [c[0] - 4.5, 0, c[2] - 4.5], "rot": 135, "text":
    "THE SEVENTH RINGER — MOTHER LOAM, THE GRAVEDIGGER\n\nShe rang the Seventh Bell once for every soul she had put down that winter — six hundred pulls, one grief at a time.\n\nHer fate: her hands forgot how to open. Deemed worthy because she counted every one and skipped none.\n\nThe unquiet she buried rise here. Return them, one at a time."})

# R8 (R,k3) — the Astronomer: five chimes in the heavens' order
c = room_c(3, 1)
CH.append({"flag": "morrow_trial_8", "order": ["east", "zenith", "west", "nadir", "north"],
           "chimes": [
               {"id": "east", "label": "the East star", "at": [c[0] + 3.6, 0, c[2]], "rot": -90},
               {"id": "zenith", "label": "the Zenith star", "at": [c[0], 0, c[2] - 3.6], "rot": 0},
               {"id": "west", "label": "the West star", "at": [c[0] - 3.6, 0, c[2]], "rot": 90},
               {"id": "nadir", "label": "the Nadir star", "at": [c[0], 0, c[2] + 3.6], "rot": 180},
               {"id": "north", "label": "the North star", "at": [c[0] + 2.6, 0, c[2] + 2.6], "rot": -135}]})
PLQ.append({"at": [c[0] + 4.5, 0, c[2] - 4.5], "rot": -135, "text":
    "THE EIGHTH RINGER — MASTER HALIARD, THE ASTRONOMER\n\nHe rang the Eighth Bell by arithmetic, at an hour he had computed nine years in advance, alone against every almanac.\n\nHis fate: he was right, and never forgiven for it. Deemed worthy because the heavens kept his appointment.\n\nRing his sky in its order: east, zenith, west, nadir, north."})

# R9 (L,k4) — the Midwife: the long vigil
c = room_c(4, -1)
SC.append({"script": "res://src/world/trial_room.gd", "at": list(c), "tag": "base",
           "params": {"flag": "morrow_trial_9", "mode": "vigil", "hold": 18.0,
                      "title": "the Trial of the Held Hour"}})
PLQ.append({"at": [c[0] - 4.5, 0, c[2] - 4.5], "rot": 135, "text":
    "THE NINTH RINGER — WREN, THE MIDWIFE\n\nShe rang the Ninth Bell one-handed. The other arm held a child born in the same minute, because neither task would wait.\n\nHer fate: every child she caught after was said to sleep through any bell. Deemed worthy for holding BOTH.\n\nHold her hour. It is longer than it looks."})

# R10 (R,k4) — the Gatewright: watchers to the north
c = room_c(4, 1)
WP.append({"flag": "morrow_trial_10", "target": 180, "watchers": [
    {"at": [c[0] - 3, 0, c[2] + 2.5]},
    {"at": [c[0] + 3, 0, c[2] + 2.5]},
    {"at": [c[0] - 3, 0, c[2] - 2.5]},
    {"at": [c[0] + 3, 0, c[2] - 2.5]}],
    "done_toast": "Four gates face the road home. The Tenth is satisfied."})
PLQ.append({"at": [c[0] + 4.5, 0, c[2] - 4.5], "rot": -135, "text":
    "THE TENTH RINGER — GORE THE GATEWRIGHT\n\nHe rang the Tenth Bell with the same pull that shut the flood-gates, one rope in each fist, because the river and the hour came at once.\n\nHis fate: the town kept dry and never knew. Deemed worthy for facing every gate HOME before himself.\n\nTurn all four to face the road home — south, where you came from."})

# R11 (L,k5) — the Ferrywright: arena, the drowned crew
c = room_c(5, -1)
SC.append({"script": "res://src/world/trial_room.gd", "at": list(c), "tag": "base",
           "params": {"flag": "morrow_trial_11", "mode": "arena",
                      "foes": ["vigilant_husk", "gilded_echo", "vigilant_husk"],
                      "spots": [[-3, 0, 1], [0, 0, -2.5], [3, 0, 1]], "radius": 5.5,
                      "title": "the Trial of the Crossing"}})
PLQ.append({"at": [c[0] - 4.5, 0, c[2] - 4.5], "rot": 135, "text":
    "THE ELEVENTH RINGER — THE FERRYWRIGHT ANSA\n\nShe rang the Eleventh Bell from mid-river, standing on the keel of her own capsized ferry, so the crossing bell would not miss its hour.\n\nHer fate: she never reached either bank; the river kept her fare. Deemed worthy because the hour arrived DRY.\n\nHer drowned crew still makes the crossing. See them over."})

# R12 (R,k5) — the Twelfth Bellhand: the mirror duel
c = room_c(5, 1)
SC.append({"script": "res://src/world/trial_room.gd", "at": list(c), "tag": "base",
           "params": {"flag": "morrow_trial_12", "mode": "duel",
                      "foes": ["wick_crusader"], "spots": [[0, 0, 0.5]],
                      "radius": 5.5, "title": "the Trial of the Twelfth Hand"}})
PLQ.append({"at": [c[0] + 4.5, 0, c[2] - 4.5], "rot": -135, "text":
    "THE TWELFTH RINGER — UNNAMED, THE LAST HAND\n\nThe Twelfth gave up their name at the rope, so the bell would carry NOTHING of them but the ring.\n\nTheir fate: no grave, no ballad, no face in the glass. Deemed worthy because nothing was kept back.\n\nWhat is left of them keeps this room. Give them rest, Thirteenth."})

# room dressing: a candle and a banner in every trial room
for k in range(6):
    for s in (1, -1):
        cx, _, cz = room_c(k, s)
        prop("candelabra", (cx - 3.8 * s, 0, cz + 4.6), 20 * s)
        prop("banner", (cx + 5.6 * s, 2.6, cz), 90 if s > 0 else -90, collide=False)

# the keep's air: gold adrift the length of the processional
SC.append({"script": "res://src/world/ambient_life.gd", "at": [0, 1, 46], "rot": 0,
           "tag": "base", "params": {"kind": "motes_gold", "extent": [10, 6, 80], "count": 30}})

# ---------------------------------------------------------------- the ledger
SC.append({"script": "res://src/world/blessing_keeper.gd", "at": [0, 0, 46], "tag": "base",
           "params": {"count": 12, "prefix": "morrow_trial_", "flag": "bell_blessing"}})

# ---------------------------------------------------------------- last door
FG.append({"at": [0, 0, 92], "flag": "bell_blessing", "kit": "gate_iron",
           "open_dir": "up", "tag": "base", "scale": [1.34, 1.0, 1.35]})
PLQ.append({"at": [3.4, 0, 90.2], "rot": -150, "text":
    "THE LAST DOOR\n\nTwelve rang before you. Twelve rooms remember how, and what it cost.\n\nKeep all twelve trials, and the bell itself will draw the bolt."})

# ---------------------------------------------------------------- the bell
# the chamber wears the cove dome whole (20 x 16, rim on the wall tops)
wall_run_x(108, -10, 10, 180)
wall_run_z(-10, 92, 108, 90)
wall_run_z(10, 92, 108, -90)
piece("palace_window_4m", (-10, 4, 96), 90)
piece("palace_window_4m", (-10, 4, 104), 90)
piece("palace_window_4m", (10, 4, 96), -90)
piece("palace_window_4m", (10, 4, 104), -90)
piece("palace_window_4m", (-4, 4, 108), 180)
piece("palace_window_4m", (4, 4, 108), 180)
prop("palace_cove_dome", (0, 8.0, 100), 0, collide=False, flames=False,
     glow=[3.0, 1.9, 11.0])
# the bell hangs from a gilt beam under the crown
prop("bell_great", (0, 7.3, 100), 0, collide=False)
SC.append({"script": "res://src/world/bell_thirteen.gd", "at": [0, 0, 100], "tag": "base",
           "params": {"bless_flag": "bell_blessing", "rung_flag": "bell_thirteen_rung"}})
prop("mosaic_medallion", (0, 0.02, 100), 0, collide=False)
prop("candelabra", (-6.5, 0, 96), 30)
prop("candelabra", (6.5, 0, 96), -30)
prop("candelabra", (-6.5, 0, 104), 150)
prop("candelabra", (6.5, 0, 104), -150)

# ---------------------------------------------------------------- sky
# the banks are ~70-90 m wide at these scales: they must hug BENEATH the
# keep's mass, never poke through a room — far out, well down
for (kit, at, rot, sc_) in [
        ("cloud_bank_a", (-62, -9.5, -20), 20, 1.6), ("cloud_bank_b", (60, -10.0, -6), -30, 1.8),
        ("cloud_bank_c", (-64, -10.5, 30), 70, 2.0), ("cloud_bank_a", (62, -9.8, 46), 130, 1.7),
        ("cloud_bank_b", (-62, -10.2, 70), -50, 1.9), ("cloud_bank_c", (60, -9.6, 92), 40, 1.6),
        ("cloud_bank_a", (0, -11.0, 140), 0, 2.2), ("cloud_bank_b", (-30, -10.6, -44), -70, 1.5)]:
    SKY.append({"kit": kit, "at": list(at), "rot": rot, "scale": [sc_, sc_, sc_]})
for (kit, at, rot) in [
        ("radiant_spire_a", (-70, -26, 40), 30), ("radiant_spire_b", (72, -30, 20), -40),
        ("radiant_castle_a", (-90, -34, 110), 60), ("radiant_castle_b", (80, -30, 90), 110)]:
    SKY.append({"kit": kit, "at": list(at), "rot": rot, "scale": [1.6, 1.6, 1.8]})

# ---------------------------------------------------------------- def
DEF = {
    "id": "morrow_keep",
    "name": "The Keep of the Morrow",
    "start": {"pos": [0, 0.3, -8], "yaw": 180},
    "env": {
        "glory": {
            "sun_rot": [-38, -30], "sun_color": [1.0, 0.97, 0.88], "sun_energy": 1.7,
            "fog_density": 0.006, "fog_color": [0.92, 0.84, 0.66],
            "music": "res://assets/audio/theme_sanctum.mp3",
        },
        "ruin": {
            "sun_rot": [-32, -30], "sun_color": [0.92, 0.8, 0.6], "sun_energy": 0.8,
            "fog_density": 0.009, "fog_color": [0.5, 0.42, 0.3],
            "music": "res://assets/audio/theme_sanctum.mp3",
        },
    },
    "free_kindle": True,
    "boxes": [{"min": [-2.6, 9.15, 99.7], "max": [2.6, 9.75, 100.3], "mat": "M_gold"}],
    "fills": F, "pieces": P, "props": PR, "vault_fields": VF, "blockers": BL,
    "plaques": PLQ, "scripted": SC, "chime_puzzles": CH, "votive_locks": VL,
    "watcher_puzzles": WP, "flag_gates": FG, "skyline": SKY,
    "open_air_regions": [{"min": [-10, 0, -12], "max": [10, 0, 0]}],
    "lanterns": [{"id": "morrow", "name": "The Morrow's Porch", "at": [-6.5, 0, -6], "rot": 120}],
    "portals": [{"to": "gilded_sanctum", "at": [0, 0, -11.2], "rot": 0,
                 "spawn": [-11.5, 2.3, -18], "spawn_yaw": 90,
                 "prompt": "Descend the Stair of Light"}],
}

with open(PATH, "w") as f:
    json.dump(DEF, f, indent=1)
print("wrote", PATH)
