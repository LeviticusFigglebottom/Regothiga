#!/usr/bin/env python3
"""Build data/areas/sovereign_apiary.json — The Sovereign Apiary (Zone 2 of the
two-part Sovereign Apiary DLC expansion, reached from the north postern of
The Chandlers' Hollow).

Architecture (Cliffside monastery-apiary combining an open-air sky-garth,
2-storey 8.0m vaulted cloister walks & halls, an elevated y=2.4 Chapter-House,
and the Cathedral of the First Comb):
  1. South Cliff-Stair Vestibule:        x =  -8..  8, z =   0.. 12, y = 0.0
  2. The Sun-Bees' Cloister & Garth:     x = -20.. 20, z = -28..  0, y = 0.0
     (Central Open-Air Botanical Garth:  x = -12.. 12, z = -20.. -8, y = 0.0)
  3. West Royal Press-House & Cellar:    x = -36..-20, z = -28.. -4, y = 0.0
  4. East Elevated Chapter-House:        x =  20.. 36, z = -28.. -4, y = 2.4
  5. North Queen-Comb Sanctuary Terrace: x = -16.. 16, z = -44..-28, y = 0.0
  6. Cathedral of the First Comb (Boss): x = -16.. 16, z = -72..-44, y = 0.0
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "data", "areas", "sovereign_apiary.json")


def build():
    fills = [
        # 1. South Cliff-Stair Vestibule (y=0.0)
        {"kit": "floor_4x4", "min": [-8, 0, 0], "max": [8, 0, 12]},
        # 2. The Sun-Bees' Cloister & Open-Air Botanical Garth (y=0.0)
        {"kit": "floor_4x4", "min": [-20, 0, -28], "max": [20, 0, 0]},
        # 3. West Royal Press-House & Mead-Cellar (y=0.0)
        {"kit": "floor_4x4", "min": [-36, 0, -28], "max": [-20, 0, -4]},
        # 4. East Elevated Chapter-House & Scriptorium (y=2.4)
        {"kit": "floor_4x4", "min": [20, 2.4, -28], "max": [36, 2.4, -4]},
        # 5. North Queen-Comb Sanctuary Terrace (y=0.0)
        {"kit": "floor_4x4", "min": [-16, 0, -44], "max": [16, 0, -28]},
        # 6. Cathedral of the First Comb (y=0.0)
        {"kit": "floor_4x4", "min": [-16, 0, -72], "max": [16, 0, -44]},
    ]

    # The central 24x12m Cloister Garth (x=-12..12, z=-20..-8) is open to the sky!
    open_air_regions = [
        {"min": [-12, 0, -20], "max": [12, 0, -8]},
    ]

    vault_fields = [
        # 1. South Cliff-Stair Vestibule
        {"min": [-8, 0, 0], "max": [8, 0, 12], "spring_top": 8.0, "band_from": 8.0, "skip_bands": ["N"], "tag": "base"},
        # 2a. South Cloister Walk (z = -8..0)
        {"min": [-20, 0, -8], "max": [20, 0, 0], "spring_top": 8.0, "band_from": 8.0, "skip_bands": ["N"], "tag": "base"},
        # 2b. North Cloister Walk (z = -28..-20)
        {"min": [-20, 0, -28], "max": [20, 0, -20], "spring_top": 8.0, "band_from": 8.0, "skip_bands": ["S", "N"], "tag": "base"},
        # 2c. West Cloister Walk (x = -20..-12, z = -20..-8)
        {"min": [-20, 0, -20], "max": [-12, 0, -8], "spring_top": 8.0, "band_from": 8.0, "skip_bands": ["N", "S", "W", "E"], "tag": "base"},
        # 2d. East Cloister Walk (x = 12..20, z = -20..-8)
        {"min": [12, 0, -20], "max": [20, 0, -8], "spring_top": 8.0, "band_from": 8.0, "skip_bands": ["N", "S", "W", "E"], "tag": "base"},
        # 3. West Royal Press-House (x = -36..-20, z = -28..-4)
        {"min": [-36, 0, -28], "max": [-20, 0, -4], "spring_top": 8.0, "band_from": 8.0, "skip_bands": ["E"], "tag": "base"},
        # 4. East Elevated Chapter-House (x = 20..36, z = -28..-4, y = 2.4)
        {"min": [20, 2.4, -28], "max": [36, 2.4, -4], "spring_top": 8.0, "band_from": 6.4, "skip_bands": ["W"], "tag": "base"},
        # 5. North Queen-Comb Sanctuary Terrace (x = -16..16, z = -44..-28)
        {"min": [-16, 0, -44], "max": [16, 0, -28], "spring_top": 8.0, "band_from": 8.0, "skip_bands": ["S", "N"], "tag": "base"},
        # 6. Cathedral of the First Comb (x = -16..16, z = -72..-44)
        {"min": [-16, 0, -72], "max": [16, 0, -44], "spring_top": 8.0, "band_from": 8.0, "skip_bands": ["S"], "tag": "base"},
    ]

    pieces = []
    props = []
    boxes = [
        # Substructure under East Elevated Chapter-House (x = 20..36, z = -28..-4, y = 0..2.4)
        {"min": [20.0, -0.4, -28.2], "max": [36.2, 2.4, -3.8], "mat": "M_stone_dark", "tag": "base"},
        # Raised Queen-Comb Chancel Dais in Cathedral of the First Comb (z = -71.5..-65.5)
        {"min": [-6.5, 0.0, -71.5], "max": [6.5, 0.14, -65.5], "mat": "M_marble", "tag": "base", "collide": False},
        {"min": [-6.8, 0.0, -65.8], "max": [6.8, 0.08, -65.4], "mat": "M_gold", "tag": "base", "collide": False},
    ]

    def add_lancet_dressing(cx, y, cz, rot, dark_back=True):
        """Dress a lancet window with stained glass (+ optional stone backing)."""
        props.append({"kit": "glass_lancet", "at": [cx, y, cz], "rot": rot, "tag": "glory"})
        props.append({"kit": "glass_lancet_broken", "at": [cx, y, cz], "rot": rot, "tag": "ruin"})
        if not dark_back:
            return
        if rot == 0:
            boxes.append({"min": [cx - 2.1, y, cz - 0.65], "max": [cx + 2.1, y + 4.1, cz - 0.35], "mat": "M_stone_dark", "tag": "base"})
        elif rot == 180:
            boxes.append({"min": [cx - 2.1, y, cz + 0.35], "max": [cx + 2.1, y + 4.1, cz + 0.65], "mat": "M_stone_dark", "tag": "base"})
        elif rot == 90:
            boxes.append({"min": [cx - 0.65, y, cz - 2.1], "max": [cx - 0.35, y + 4.1, cz + 2.1], "mat": "M_stone_dark", "tag": "base"})
        elif rot == -90:
            boxes.append({"min": [cx + 0.35, y, cz - 2.1], "max": [cx + 0.65, y + 4.1, cz + 2.1], "mat": "M_stone_dark", "tag": "base"})

    def add_wall_x(z, x0, x1, rot, y=0.0, openings=None, upper=True, upper_windows=None, cornice=True, dark_back=True):
        openings = openings or {}
        if upper_windows is None:
            upper_windows = set(range(x0 + 2, x1, 8))
        for x in range(x0, x1, 4):
            cx = x + 2
            kit = openings.get(cx, "wall_4x4")
            pieces.append({"kit": kit, "at": [cx, y, z], "rot": rot, "tag": "base"})
            if kit == "window_lancet_4m":
                add_lancet_dressing(cx, y, z, rot, dark_back=dark_back)
            if cornice:
                pieces.append({"kit": "cornice_4m", "at": [cx, y + 4.0, z], "rot": rot, "tag": "base", "collide": False})
            if upper:
                ukit = "window_lancet_4m" if cx in upper_windows else "wall_4x4"
                pieces.append({"kit": ukit, "at": [cx, y + 4.0, z], "rot": rot, "tag": "base"})
                if ukit == "window_lancet_4m":
                    add_lancet_dressing(cx, y + 4.0, z, rot, dark_back=dark_back)

    def add_wall_z(x, z0, z1, rot, y=0.0, openings=None, upper=True, upper_windows=None, cornice=True, dark_back=True):
        openings = openings or {}
        if upper_windows is None:
            upper_windows = set(range(z0 + 2, z1, 8))
        for z in range(z0, z1, 4):
            cz = z + 2
            kit = openings.get(cz, "wall_4x4")
            pieces.append({"kit": kit, "at": [x, y, cz], "rot": rot, "tag": "base"})
            if kit == "window_lancet_4m":
                add_lancet_dressing(x, y, cz, rot, dark_back=dark_back)
            if cornice:
                pieces.append({"kit": "cornice_4m", "at": [x, y + 4.0, cz], "rot": rot, "tag": "base", "collide": False})
            if upper:
                ukit = "window_lancet_4m" if cz in upper_windows else "wall_4x4"
                pieces.append({"kit": ukit, "at": [x, y + 4.0, cz], "rot": rot, "tag": "base"})
                if ukit == "window_lancet_4m":
                    add_lancet_dressing(x, y + 4.0, cz, rot, dark_back=dark_back)

    # =========================================================================
    # PERIMETER & CLOISTER WALLS
    # =========================================================================

    # 1. South Cliff-Stair Vestibule (x = -8..8, z = 0..12)
    add_wall_z(-8, 0, 12, 90, openings={6: "window_lancet_4m"})
    add_wall_z(8, 0, 12, -90, openings={6: "window_lancet_4m"})
    add_wall_x(12, -8, 8, 180, openings={-6: "window_lancet_4m", 6: "window_lancet_4m"})
    pieces.append({"kit": "portal_4m", "at": [0.0, 0, 11.6], "rot": 180, "tag": "base"})
    pieces.append({"kit": "rose_window", "at": [0.0, 5.6, 11.65], "rot": 180, "tag": "base", "collide": False})

    # Threshold between South Vestibule (z=0..12) and South Cloister Walk (z=-8..0) at z=0
    add_wall_x(0, -20, -8, 180, openings={-14: "window_lancet_4m"})
    add_wall_x(0, 8, 20, 180, openings={14: "window_lancet_4m"})
    add_wall_x(0, -8, 8, 180, openings={-2: "arcade_4m", 2: "arcade_4m"}, upper_windows=set())

    # 2. The Sun-Bees' Cloister Perimeter & Inner Open-Air Garth Colonnade
    # Outer South-West & South-East corners of Cloister (z = -4..0 at x = -20 and x = 20)
    add_wall_z(-20, -4, 0, 90, openings={}, upper_windows=set())
    add_wall_z(20, -4, 0, -90, openings={}, upper_windows=set())

    # Inner Garth Colonnade enclosing the Open-Air Courtyard (x=-12..12, z=-20..-8):
    # Ground floor is all open `arcade_4m` arches; upper storey (y=4..8) has lancets & walls!
    add_wall_x(-8, -12, 12, 0, openings={c: "arcade_4m" for c in range(-10, 12, 4)},
               upper_windows={-6, 6}, dark_back=False)
    add_wall_x(-20, -12, 12, 180, openings={c: "arcade_4m" for c in range(-10, 12, 4)},
               upper_windows={-6, 6}, dark_back=False)
    add_wall_z(-12, -20, -8, -90, openings={c: "arcade_4m" for c in range(-18, -8, 4)},
               upper_windows={-14}, dark_back=False)
    add_wall_z(12, -20, -8, 90, openings={c: "arcade_4m" for c in range(-18, -8, 4)},
               upper_windows={-14}, dark_back=False)

    # Partition between West Cloister Walk (x=-20..-12) and West Royal Press-House (x=-36..-20) at x=-20, z=-28..-4
    add_wall_z(-20, -28, -4, 90, openings={-22: "arcade_4m", -18: "arcade_4m", -14: "arcade_4m", -10: "arcade_4m"},
               upper_windows=set())

    # 3. West Royal Press-House & Mead-Cellar (x = -36..-20, z = -28..-4, y = 0.0)
    add_wall_x(-4, -36, -20, 180, openings={-28: "window_lancet_4m"})
    add_wall_x(-28, -36, -20, 0, openings={-28: "window_lancet_4m"})
    add_wall_z(-36, -28, -4, 90, openings={-22: "window_lancet_4m", -16: "window_lancet_4m", -10: "window_lancet_4m"})

    # 4. East Elevated Chapter-House & Scriptorium (x = 20..36, z = -28..-4, y = 2.4)
    pieces.append({"kit": "stair_grand_4m", "at": [20, 2.38, -16], "rot": 90, "tag": "base"})
    for cz in (-26, -22, -10, -6):
        pieces.append({"kit": "balustrade_4m", "at": [20.2, 2.4, cz], "rot": 90, "tag": "base"})
    add_wall_x(-4, 20, 36, 180, y=2.4, openings={28: "window_lancet_4m"}, upper=False)
    add_wall_x(-28, 20, 36, 0, y=2.4, openings={28: "window_lancet_4m"}, upper=False)
    add_wall_z(36, -28, -4, -90, y=2.4, openings={-22: "window_lancet_4m", -16: "window_lancet_4m", -10: "window_lancet_4m"}, upper=False)

    # Partition between North Cloister Walk (z=-28..-20, x=-20..20) and North Sanctuary Terrace (z=-44..-28, x=-16..16)
    add_wall_x(-28, -20, -16, 0, openings={}, upper_windows=set())
    add_wall_x(-28, 16, 20, 0, openings={}, upper_windows=set())
    # Central partition at z = -28, x = -16..16: shortcut gate at cx = -6, votive-locked door at cx = 2!
    add_wall_x(-28, -16, 16, 0, openings={-6: "portal_4m", 2: "portal_4m"}, upper_windows={-10, 10})
    pieces.append({"kit": "rose_window", "at": [2.0, 5.6, -27.65], "rot": 0, "tag": "base", "collide": False})

    # 5. North Queen-Comb Sanctuary Terrace (x = -16..16, z = -44..-28, y = 0.0)
    add_wall_z(-16, -44, -28, 90, openings={-38: "window_lancet_4m", -34: "window_lancet_4m"})
    add_wall_z(16, -44, -28, -90, openings={-38: "window_lancet_4m", -34: "window_lancet_4m"})
    # Partition into Cathedral of the First Comb at z = -44, x = -16..16 (boss fog gate at cx = -2)
    add_wall_x(-44, -16, 16, 0, openings={-2: "portal_4m"}, upper_windows={-10, 10})
    pieces.append({"kit": "rose_window", "at": [-2.0, 5.6, -43.65], "rot": 0, "tag": "base", "collide": False})

    # 6. Cathedral of the First Comb (x = -16..16, z = -72..-44, y = 0.0)
    add_wall_z(-16, -72, -44, 90, openings={-66: "window_lancet_4m", -58: "window_lancet_4m", -50: "window_lancet_4m"})
    add_wall_z(16, -72, -44, -90, openings={-66: "window_lancet_4m", -58: "window_lancet_4m", -50: "window_lancet_4m"})
    add_wall_x(-72, -16, 16, 0, openings={-10: "window_lancet_4m", -2: "window_lancet_4m", 2: "window_lancet_4m", 10: "window_lancet_4m"})
    pieces.append({"kit": "rose_window", "at": [0.0, 5.6, -71.65], "rot": 0, "tag": "base", "collide": False})

    # =========================================================================
    # 2-STOREY COLONNADES (comb_pillar_4m at y=0 + column_4m at y=4)
    # =========================================================================
    def add_tall_pier(px, pz, scons_rot=None):
        pieces.append({"kit": "comb_pillar_4m", "at": [px, 0, pz], "rot": 0, "tag": "base"})
        pieces.append({"kit": "column_4m", "at": [px, 4.0, pz], "rot": 0, "tag": "base", "collide": False})
        if scons_rot is not None:
            dx = 0.45 * (1 if scons_rot == 90 else (-1 if scons_rot == -90 else 0))
            dz = 0.45 * (1 if scons_rot == 0 else (-1 if scons_rot == 180 else 0))
            props.append({"kit": "sconce_torch", "at": [px + dx, 2.3, pz + dz], "rot": scons_rot, "tag": "glory"})

    # West Press-House colonnade
    for cz in (-22, -16, -10):
        add_tall_pier(-28, cz, 90)
    # North Sanctuary Terrace colonnade
    for cx in (-10, 10):
        add_tall_pier(cx, -36, 90 if cx < 0 else -90)
    # Cathedral of the First Comb nave colonnade
    for cx in (-10, 10):
        for cz in (-50, -58, -66):
            add_tall_pier(cx, cz, 90 if cx < 0 else -90)

    # =========================================================================
    # DENSE DECORATION & PROPS ACROSS ALL 6 WINGS
    # =========================================================================

    # Processional carpets & mosaic medallions
    for rx, ry, rz, rrot in [
        (0.0, 0, 5.0, 0), (0.0, 0, -4.0, 0), (0.0, 0, -24.0, 0),
        (0.0, 0, -36.0, 0), (-2.0, 0, -50.0, 0), (-2.0, 0, -58.0, 0), (-2.0, 0, -64.0, 0),
        (28.0, 2.4, -16.0, 90),
    ]:
        props.append({"kit": "carpet_runner_8m", "at": [rx, ry, rz], "rot": rrot, "tag": "base", "collide": False})
    for mx, my, mz in [(0.0, 0, -36.0), (-2.0, 0, -56.0), (28.0, 2.4, -16.0)]:
        props.append({"kit": "mosaic_medallion", "at": [mx, my, mz], "rot": 0, "tag": "base", "collide": False})

    # Open-Air Botanical Garth centerpiece & gardens (x = -12..12, z = -20..-8)
    props.append({"kit": "shrine_aedicule", "at": [0.0, 0, -14.0], "rot": 0, "tag": "base"})
    for gx, gz in [(-6.5, -11.5), (6.5, -11.5), (-6.5, -16.5), (6.5, -16.5)]:
        props.append({"kit": "garden_bed", "at": [gx, 0, gz], "rot": 0, "tag": "glory"})
        props.append({"kit": "garden_bed_dead", "at": [gx, 0, gz], "rot": 0, "tag": "ruin"})

    # Sacred Golden Skeps across the Garth, Cloister, Sanctuary & Cathedral
    skep_spots = [
        # Open-Air Garth
        (-9.5, 0, -10.5, 45), (9.5, 0, -10.5, -45),
        (-9.5, 0, -17.5, 135), (9.5, 0, -17.5, -135),
        (-3.8, 0, -11.0, 0), (3.8, 0, -11.0, 0),
        (-3.8, 0, -17.0, 180), (3.8, 0, -17.0, 180),
        # Cloister Ambulatories
        (-16.5, 0, -6.0, 0), (16.5, 0, -6.0, 0),
        (-16.5, 0, -24.0, 180), (16.5, 0, -24.0, 180),
        # Sanctuary Terrace
        (-13.2, 0, -32.0, 90), (-13.2, 0, -40.0, 90),
        (13.2, 0, -32.0, -90), (13.2, 0, -40.0, -90),
        # Cathedral of the First Comb
        (-13.2, 0, -48.0, 90), (-13.2, 0, -62.0, 90),
        (13.2, 0, -48.0, -90), (13.2, 0, -62.0, -90),
        (-5.0, 0, -69.2, 0), (5.0, 0, -69.2, 0),
    ]
    for sx, sy, sz, srot in skep_spots:
        props.append({"kit": "apiary_skep", "at": [sx, sy, sz], "rot": srot, "tag": "base"})

    # Apiary Reliquary Steles (comb_shrine)
    shrine_spots = [
        (-5.5, 0, 9.5, 180), (5.5, 0, 9.5, 180),
        (-16.0, 0, -14.0, 90), (16.0, 0, -14.0, -90),
        (-33.5, 0, -16.0, 90),
        (26.0, 2.4, -26.2, 0), (26.0, 2.4, -5.8, 180),
        (-6.0, 0, -42.0, 0), (6.0, 0, -42.0, 0),
        (-13.5, 0, -69.5, 45), (13.5, 0, -69.5, -45),
    ]
    for cx, cy, cz, crot in shrine_spots:
        props.append({"kit": "comb_shrine", "at": [cx, cy, cz], "rot": crot, "tag": "base"})

    # Royal Comb Screw-Presses (wax_press) in West Press-House & Cathedral
    press_spots = [
        (-33.0, 0, -8.5, 90), (-33.0, 0, -16.0, 90), (-33.0, 0, -23.5, 90),
        (-24.0, 0, -7.0, 180), (-24.0, 0, -25.0, 0),
        (-13.2, 0, -54.0, 90), (13.2, 0, -54.0, -90),
    ]
    for px, py, pz, prot in press_spots:
        props.append({"kit": "wax_press", "at": [px, py, pz], "rot": prot, "tag": "base"})

    # Boiling Tallow Vats (Glory) / Cold Tallow Vats (Ruin)
    vat_spots = [
        (-28.0, 0, -8.5), (-28.0, 0, -23.5),
        (-6.5, 0, -34.0), (6.5, 0, -34.0),
        (-7.5, 0, -48.5), (7.5, 0, -48.5),
        (-7.5, 0, -56.5), (7.5, 0, -56.5),
        (-7.5, 0, -64.5), (7.5, 0, -64.5),
    ]
    for vx, vy, vz in vat_spots:
        props.append({"kit": "tallow_vat", "at": [vx, vy, vz], "rot": 0, "tag": "glory"})
        props.append({"kit": "tallow_vat_cold", "at": [vx, vy, vz], "rot": 0, "tag": "ruin"})

    # Suspended Dipping Wheels & Gilt Chandeliers
    wheel_spots = [
        (0.0, 3.6, 6.0),
        (-16.0, 3.6, -14.0), (16.0, 3.6, -14.0),
        (-6.0, 3.6, -4.0), (6.0, 3.6, -4.0),
        (-6.0, 3.6, -24.0), (6.0, 3.6, -24.0),
        (-26.0, 3.6, -12.0), (-26.0, 3.6, -20.0),
        (-5.5, 3.8, -36.0), (5.5, 3.8, -36.0),
        (-5.5, 3.8, -52.0), (5.5, 3.8, -52.0),
        (-5.5, 3.8, -62.0), (5.5, 3.8, -62.0),
    ]
    for wx, wy, wz in wheel_spots:
        props.append({"kit": "wax_wheel", "at": [wx, wy, wz], "rot": 0, "tag": "base"})

    for gx, gy, gz in [(28.0, 5.2, -16.0), (0.0, 5.2, -36.0), (-2.0, 5.4, -56.0), (0.0, 5.4, -67.0)]:
        props.append({"kit": "chandelier_gilt", "at": [gx, gy, gz], "rot": 0, "tag": "glory"})

    # Fluted Honey Amphorae (honey_amphora), Barrels, Crates & Carts
    amphora_spots = [
        (-5.8, 0, 2.5), (5.8, 0, 2.5),
        (-18.2, 0, -2.5), (18.2, 0, -2.5),
        (-18.2, 0, -25.5), (18.2, 0, -25.5),
        (-34.2, 0, -5.8), (-34.2, 0, -12.2), (-34.2, 0, -19.8), (-34.2, 0, -26.2),
        (34.2, 2.4, -6.5), (34.2, 2.4, -25.5),
        (-13.8, 0, -30.2), (13.8, 0, -30.2),
        (-13.8, 0, -46.2), (13.8, 0, -46.2),
        (-8.5, 0, -69.5), (8.5, 0, -69.5),
    ]
    for ax, ay, az in amphora_spots:
        props.append({"kit": "honey_amphora", "at": [ax, ay, az], "rot": int((ax * 29 + az * 41) % 360), "tag": "base"})

    for cx, cy, cz, crot in [
        (-30.5, 0, -5.8, 20), (-30.5, 0, -26.2, -30),
        (-18.0, 0, -9.5, 15), (13.5, 0, -42.0, -25),
    ]:
        props.append({"kit": "crate_stack", "at": [cx, cy, cz], "rot": crot, "tag": "base"})
    for bx, by, bz in [
        (-28.8, 0, -5.8), (-28.8, 0, -26.2), (-22.0, 0, -5.8),
        (11.8, 0, -42.2), (-13.5, 0, -42.0),
    ]:
        props.append({"kit": "barrel", "at": [bx, by, bz], "rot": 10, "tag": "base"})
    props.append({"kit": "hand_cart", "at": [-23.0, 0, -25.0], "rot": 40, "tag": "base"})

    # East Elevated Chapter-House & Scriptorium (x = 20..36, z = -28..-4, y = 2.4)
    props.append({"kit": "altar_wick", "at": [32.5, 2.4, -16.0], "rot": -90, "tag": "base"})
    props.append({"kit": "statue_saint", "at": [34.2, 2.4, -11.0], "rot": -90, "tag": "base"})
    props.append({"kit": "statue_saint", "at": [34.2, 2.4, -21.0], "rot": -90, "tag": "base"})
    for sx, sz, srot in [
        (25.0, -26.8, 0), (29.0, -26.8, 0), (33.0, -26.8, 0),
        (25.0, -5.2, 180), (29.0, -5.2, 180), (33.0, -5.2, 180),
    ]:
        props.append({"kit": "scriptorium_shelf", "at": [sx, 2.4, sz], "rot": srot, "tag": "base"})
    for tx, tz in [(27.5, -10.5), (27.5, -21.5)]:
        props.append({"kit": "banquet_table_6m", "at": [tx, 2.4, tz], "rot": 0, "tag": "base"})
        props.append({"kit": "book_stack", "at": [tx - 1.2, 3.55, tz], "rot": 25, "tag": "base"})
        props.append({"kit": "scroll_pile", "at": [tx + 1.2, 3.55, tz], "rot": -20, "tag": "base"})
    for cz in (-12.5, -19.5):
        props.append({"kit": "choir_stall", "at": [22.8, 2.4, cz], "rot": -90, "tag": "base"})

    # Cathedral of the First Comb Chancel & Statuary
    props.append({"kit": "altar_wick", "at": [0.0, 0, -68.5], "rot": 0, "tag": "base"})
    props.append({"kit": "statue_orans", "at": [-13.5, 0, -58.0], "rot": 90, "tag": "base"})
    props.append({"kit": "statue_orans", "at": [13.5, 0, -58.0], "rot": -90, "tag": "base"})
    props.append({"kit": "statue_saint", "at": [-3.5, 0, -68.5], "rot": 0, "tag": "base"})
    props.append({"kit": "statue_saint", "at": [3.5, 0, -68.5], "rot": 0, "tag": "base"})

    # Braziers, Candelabras & Candle Clusters
    for bx, by, bz in [
        (-3.5, 0, 8.5), (3.5, 0, 8.5),
        (-4.5, 0, -2.5), (4.5, 0, -2.5),
        (-4.5, 0, -25.5), (4.5, 0, -25.5),
        (21.8, 2.4, -12.5), (21.8, 2.4, -19.5),
        (-4.5, 0, -41.5), (4.5, 0, -41.5),
        (-4.5, 0, -66.5), (4.5, 0, -66.5),
    ]:
        props.append({"kit": "brazier_lit", "at": [bx, by, bz], "rot": 0, "tag": "glory"})
        props.append({"kit": "brazier_cold", "at": [bx, by, bz], "rot": 0, "tag": "ruin"})

    for cx, cy, cz in [
        (31.5, 2.4, -13.5), (31.5, 2.4, -18.5),
        (-2.5, 0, -67.5), (2.5, 0, -67.5),
        (-8.0, 0, -38.0), (8.0, 0, -38.0),
    ]:
        props.append({"kit": "candelabra", "at": [cx, cy, cz], "rot": 0, "tag": "glory"})

    for cx, cy, cz in [
        (-2.2, 0, -14.0), (2.2, 0, -14.0),
        (31.0, 2.4, -15.0), (31.0, 2.4, -17.0),
        (-2.5, 0, -66.5), (2.5, 0, -66.5),
    ]:
        props.append({"kit": "candle_cluster", "at": [cx, cy, cz], "rot": 15, "tag": "glory"})
        props.append({"kit": "candle_cluster_dead", "at": [cx, cy, cz], "rot": 15, "tag": "ruin"})

    # Wall Banners
    banner_spots = [
        (-8.0, 2.6, -27.82, 0), (8.0, 2.6, -27.82, 0),
        (-8.0, 2.6, -43.82, 0), (8.0, 2.6, -43.82, 0),
        (-6.0, 2.6, -71.82, 0), (6.0, 2.6, -71.82, 0),
        (-15.82, 2.6, -54.0, 90), (15.82, 2.6, -54.0, -90),
        (35.82, 5.0, -13.0, -90), (35.82, 5.0, -19.0, -90),
    ]
    for bx, by, bz, brot in banner_spots:
        props.append({"kit": "banner", "at": [bx, by, bz], "rot": brot, "tag": "glory"})
        props.append({"kit": "banner_torn", "at": [bx, by, bz], "rot": brot, "tag": "ruin"})

    # Calcified Wax Husks in Ruin
    for hx, hy, hz, hrot in [
        (-4.5, 0, -14.0, 90), (-29.5, 0, -12.0, 45),
        (29.0, 2.4, -16.0, -90), (-11.5, 0, -52.0, 60), (11.5, 0, -62.0, -120),
    ]:
        props.append({"kit": "wax_husk", "at": [hx, hy, hz], "rot": hrot, "tag": "ruin"})

    # Distant Sea-Cliff & Cathedral Panorama visible above the Open-Air Cloister Garth
    skyline = [
        {"kit": "city_panorama", "at": [0, -18, -24]},
        {"kit": "spire_tower_a", "at": [-46, -4, -36]},
        {"kit": "spire_tower_b", "at": [48, -4, -38]},
        {"kit": "spire_tower_c", "at": [0, -6, -92]},
    ]

    # =========================================================================
    # VIGIL LANTERNS, NPCS, VOTIVE LOCKS, GATES, SPAWNERS, PICKUPS, PLAQUES
    # =========================================================================
    lanterns = [
        {"id": "apiary_entry", "name": "Cliff-Stair Threshold", "at": [-4.5, 0, 5.5], "rot": 90},
        {"id": "apiary_sanctum", "name": "Queen-Comb Sanctuary Vigil", "at": [10.5, 0, -36.0], "rot": -90},
    ]

    npcs = [
        {"id": "sister_melisande", "at": [10.5, 0, -32.2], "rot": -35, "tag": "glory"},
    ]

    # 4-Votive Lock (2 in West Press-House, 2 in East Chapter-House) -> unbars Sanctuary Terrace
    votive_locks = [
        {
            "flag": "apiary_sanctum_open",
            "tag": "base",
            "votives": [
                {"at": [-24.5, 0, -11.5]},
                {"at": [-24.5, 0, -20.5]},
                {"at": [24.5, 2.4, -13.5]},
                {"at": [24.5, 2.4, -18.5]},
            ],
        }
    ]

    flag_gates = [
        {
            "flag": "apiary_sanctum_open",
            "kit": "door_leaf",
            "at": [2.0, 0, -28.0],
            "rot": 0,
            "tag": "base",
        }
    ]

    gates = [
        {
            "id": "apiary_sanctum_shortcut",
            "at": [-6.0, 0, -28.0],
            "rot": 0,
            "locked_prompt": "Barred from the Queen-Comb Sanctuary side",
        }
    ]

    fog_gates = [
        {
            "id": "apiary_boss_fog",
            "at": [-2.0, 0, -44.0],
            "rot": 0,
            "tag": "ruin",
        }
    ]

    spawners = [
        {
            "id": "garth_melter_1",
            "enemy": "tallow_melter",
            "at": [-6.0, 0, -4.5],
            "face": 0,
            "tag": "ruin",
        },
        {
            "id": "garth_echo_1",
            "enemy": "gilded_echo",
            "at": [6.0, 0, -4.5],
            "face": 0,
            "tag": "ruin",
        },
        {
            "id": "garth_warden_1",
            "enemy": "comb_warden",
            "at": [0.0, 0, -23.5],
            "face": 0,
            "tag": "ruin",
        },
        {
            "id": "press_melter_1",
            "enemy": "tallow_melter",
            "at": [-26.0, 0, -11.5],
            "face": 90,
            "tag": "ruin",
        },
        {
            "id": "press_melter_2",
            "enemy": "tallow_melter",
            "at": [-26.0, 0, -20.5],
            "face": 90,
            "tag": "ruin",
        },
        {
            "id": "press_warden",
            "enemy": "comb_warden",
            "at": [-30.0, 0, -16.0],
            "face": 90,
            "tag": "ruin",
        },
        {
            "id": "chapter_echo",
            "enemy": "gilded_echo",
            "at": [25.5, 2.4, -16.0],
            "face": -90,
            "tag": "ruin",
        },
        {
            "id": "chapter_warden",
            "enemy": "comb_warden",
            "at": [30.0, 2.4, -16.0],
            "face": -90,
            "tag": "ruin",
        },
        {
            "id": "sanctum_warden",
            "enemy": "comb_warden",
            "at": [-2.0, 0, -37.5],
            "face": 0,
            "tag": "ruin",
        },
        {
            "id": "apiary_boss",
            "enemy": "vesper_matriarch",
            "at": [-2.0, 0, -60.0],
            "face": 180,
            "dead_once": True,
            "fog_gate_id": "apiary_boss_fog",
            "tag": "ruin",
        },
    ]

    pickups = [
        {
            "id": "apiary_sovereign_greatsword",
            "at": [30.8, 2.4, -16.0],
            "item": "sovereign_greatsword",
            "count": 1,
            "orisons": 350,
            "tag": "base",
            "label": "Claim the Sovereign Comb-Blade",
        },
        {
            "id": "garth_aedicule_offering",
            "at": [0.0, 0, -11.2],
            "item": "candleglass",
            "count": 1,
            "orisons": 220,
            "tag": "base",
            "label": "Gather the Sun-Bees' First Offering",
        },
        {
            "id": "press_house_cache",
            "at": [-31.0, 0, -16.0],
            "item": "candleglass",
            "count": 1,
            "orisons": 280,
            "tag": "base",
            "label": "Gather the Clarified Press-Cake",
        },
        {
            "id": "sanctum_pilgrim_cache",
            "at": [-10.5, 0, -36.0],
            "item": "radiant_token",
            "count": 1,
            "orisons": 300,
            "tag": "base",
            "label": "Claim the Beekeeper's Vigil Token",
        },
        {
            "id": "cathedral_matriarch_chest",
            "at": [0.0, 0, -66.2],
            "item": "candleglass",
            "count": 2,
            "orisons": 900,
            "tag": "base",
            "label": "Claim the First Comb Reliquary Coffer",
        },
    ]

    plaques = [
        {
            "at": [3.5, 0, 5.5],
            "rot": -45,
            "text": (
                "CLOISTER OF THE GOLDEN COMB\n\n"
                "Above the smoke of the kettles, the Sisters of the Skep tended the "
                "living hives in open noon. Look not into an unsealed skep without a veil; "
                "the bees gather the hour before it cools."
            ),
        },
        {
            "at": [0.0, 0, -6.5],
            "rot": 0,
            "text": (
                "THE FOUR SANCTUM VOTIVES\n\n"
                "Two flames are kept by the press-masters of the West Cellar; two by the "
                "scribes of the East Chapter-House. Only when all four burn together does "
                "the Queen-Comb Sanctuary unbar."
            ),
        },
        {
            "at": [-23.0, 0, -16.0],
            "rot": 90,
            "text": (
                "THE ROYAL SCREW-PRESSES\n\n"
                "Seven turns of the bronze spindle press the summer out of the comb. "
                "What runs clear ischrism for the lamps; what remains in the cake is "
                "harder than church-iron."
            ),
        },
        {
            "at": [23.5, 2.4, -10.0],
            "rot": -45,
            "text": (
                "THE SOVEREIGN COMB-BLADE\n\n"
                "Forged for the First Abbess of the Apiary, its fuller is hollowed into "
                "seven hexagonal cells of royal wax. Whoever bears it carries the warmth "
                "of the cliff-gardens into the dark."
            ),
        },
        {
            "at": [3.5, 0, -40.5],
            "rot": 20,
            "text": (
                "VOW OF MATRIARCH AURELIA\n\n"
                "They have taken the bells, the choir, and the six lower vats. They "
                "shall not have the Queen-Skep. I have drunk the boiling comb myself and "
                "barred the nave; let the Palace come and harvest it from my bones."
            ),
        },
    ]

    portals = [
        {
            "to": "chandlers_hollow",
            "at": [0.0, 0, 10.2],
            "rot": 180,
            "spawn": [0.0, 0.2, -44.0],
            "spawn_yaw": 180,
            "prompt": "Descend to the Chandlers' Hollow",
        }
    ]

    scripted = [
        {
            "script": "res://src/world/ambient_life.gd",
            "at": [0, 0, -14],
            "rot": 0,
            "tag": "glory",
            "params": {"kind": "motes_gold", "extent": [12, 5, 8], "count": 36},
        },
        {
            "script": "res://src/world/ambient_life.gd",
            "at": [28, 2.4, -16],
            "rot": 0,
            "tag": "glory",
            "params": {"kind": "motes_gold", "extent": [6, 4, 9], "count": 20},
        },
        {
            "script": "res://src/world/ambient_life.gd",
            "at": [0, 0, -58],
            "rot": 0,
            "tag": "glory",
            "params": {"kind": "motes_gold", "extent": [12, 5, 12], "count": 28},
        },
        {
            "script": "res://src/world/ambient_life.gd",
            "at": [0, 0, -58],
            "rot": 0,
            "tag": "ruin",
            "params": {"kind": "motes_ash", "extent": [12, 5, 12], "count": 32},
        },
    ]

    data = {
        "id": "sovereign_apiary",
        "name": "The Sovereign Apiary",
        "free_kindle": True,
        "start": {"pos": [0.0, 0.2, 8.5], "yaw": 0},
        "env": {
            "glory": {
                "sun_color": [1.0, 0.78, 0.42],
                "sun_energy": 0.92,
                "sun_rot": [-34, -38],
                "ambient": [0.38, 0.29, 0.18],
                "fog_color": [0.52, 0.36, 0.20],
                "bg_top": [0.22, 0.15, 0.10],
                "bg_horizon": [0.62, 0.42, 0.22],
                "fog_density": 0.009,
            },
            "ruin": {
                "sun_color": [0.30, 0.36, 0.50],
                "sun_energy": 0.18,
                "fog_color": [0.06, 0.08, 0.11],
                "bg_top": [0.03, 0.045, 0.075],
                "bg_horizon": [0.07, 0.095, 0.14],
                "fog_density": 0.012,
            },
        },
        "fills": fills,
        "open_air_regions": open_air_regions,
        "boxes": boxes,
        "vault_fields": vault_fields,
        "pieces": pieces,
        "props": props,
        "skyline": skyline,
        "lanterns": lanterns,
        "npcs": npcs,
        "votive_locks": votive_locks,
        "flag_gates": flag_gates,
        "gates": gates,
        "fog_gates": fog_gates,
        "spawners": spawners,
        "pickups": pickups,
        "plaques": plaques,
        "portals": portals,
        "scripted": scripted,
    }

    with open(PATH, "w") as f:
        json.dump(data, f, indent=1)
    print(
        f"sovereign_apiary: pieces {len(pieces)} fills {len(fills)} props {len(props)} "
        f"spawners {len(spawners)} pickups {len(pickups)}"
    )


if __name__ == "__main__":
    build()
