#!/usr/bin/env python3
"""Build data/areas/chandlers_hollow.json — The Chandlers' Hollow (Zone 1 of the
two-part Sovereign Apiary DLC expansion, accessed from the West Chandlers'
Quarter of the Old Outskirts and leading north into The Sovereign Apiary).

Architecture (2-storey 8.0m vaulted cathedral-foundry across y=0.0 and y=2.4):
  1. East Entrance Gallery & Forge:      x =  16.. 28, z =  -8..  8, y = 0.0
  2. Great Amber Foundry Nave:           x = -16.. 16, z = -12.. 12, y = 0.0
  3. South Apiary Cloister & Garth:      x = -16.. 16, z =  12.. 28, y = 0.0
  4. South-East Smelting Cistern:        x =  16.. 28, z =   8.. 28, y = 0.0
  5. East Elevated Smelting Mezzanine:   x =  28.. 36, z =   8.. 28, y = 2.4
  6. West Guild Reliquary Antechamber:   x = -28..-16, z = -12.. 12, y = 0.0
  7. West High Scriptorium & Treasury:   x = -40..-28, z = -12.. 12, y = 2.4
  8. South-West Wax-Crypt & Ossuary:     x = -28..-16, z =  12.. 28, y = 0.0
  9. North Crucible Boss Vault:          x = -16.. 16, z = -36..-12, y = 0.0
 10. North Sovereign Postern Sanctuary:  x =  -8..  8, z = -48..-36, y = 0.0
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "data", "areas", "chandlers_hollow.json")


def build():
    fills = [
        # 1. East Entrance Gallery & Caelan's Forge (y=0.0)
        {"kit": "floor_4x4", "min": [16, 0, -8], "max": [28, 0, 8]},
        # 2. Great Amber Foundry Nave (y=0.0)
        {"kit": "floor_4x4", "min": [-16, 0, -12], "max": [16, 0, 12]},
        # 3. South Apiary Cloister & Conservatory (y=0.0)
        {"kit": "floor_4x4", "min": [-16, 0, 12], "max": [16, 0, 28]},
        # 4. South-East Smelting Cistern (y=0.0)
        {"kit": "floor_4x4", "min": [16, 0, 8], "max": [28, 0, 28]},
        # 5. East Elevated Smelting Mezzanine (y=2.4)
        {"kit": "floor_4x4", "min": [28, 2.4, 8], "max": [36, 2.4, 28]},
        # 6. West Guildmaster's Reliquary Antechamber (y=0.0)
        {"kit": "floor_4x4", "min": [-28, 0, -12], "max": [-16, 0, 12]},
        # 7. West High Scriptorium & Reliquary Sanctuary (y=2.4)
        {"kit": "floor_4x4", "min": [-40, 2.4, -12], "max": [-28, 2.4, 12]},
        # 8. South-West Guildmaster's Ossuary Crypt (y=0.0)
        {"kit": "floor_4x4", "min": [-28, 0, 12], "max": [-16, 0, 28]},
        # 9. North Crucible Boss Vault (y=0.0)
        {"kit": "floor_4x4", "min": [-16, 0, -36], "max": [16, 0, -12]},
        # 10. North Sovereign Postern Sanctuary (y=0.0)
        {"kit": "floor_4x4", "min": [-8, 0, -48], "max": [8, 0, -36]},
    ]

    vault_fields = [
        {"min": [16, 0, -8], "max": [28, 0, 8], "spring_top": 8.0, "band_from": 8.0, "skip_bands": ["W", "S"], "tag": "base"},
        {"min": [-16, 0, -12], "max": [16, 0, 12], "spring_top": 8.0, "band_from": 8.0, "tag": "base"},
        {"min": [-16, 0, 12], "max": [16, 0, 28], "spring_top": 8.0, "band_from": 8.0, "skip_bands": ["N"], "tag": "base"},
        {"min": [16, 0, 8], "max": [28, 0, 28], "spring_top": 8.0, "band_from": 8.0, "skip_bands": ["N", "W", "E"], "tag": "base"},
        {"min": [28, 2.4, 8], "max": [36, 2.4, 28], "spring_top": 8.0, "band_from": 6.4, "skip_bands": ["W"], "tag": "base"},
        {"min": [-28, 0, -12], "max": [-16, 0, 12], "spring_top": 8.0, "band_from": 8.0, "skip_bands": ["E", "W", "S"], "tag": "base"},
        {"min": [-40, 2.4, -12], "max": [-28, 2.4, 12], "spring_top": 8.0, "band_from": 6.4, "skip_bands": ["E"], "tag": "base"},
        {"min": [-28, 0, 12], "max": [-16, 0, 28], "spring_top": 8.0, "band_from": 8.0, "skip_bands": ["N", "E"], "tag": "base"},
        {"min": [-16, 0, -36], "max": [16, 0, -12], "spring_top": 8.0, "band_from": 8.0, "skip_bands": ["S"], "tag": "base"},
        {"min": [-8, 0, -48], "max": [8, 0, -36], "spring_top": 8.0, "band_from": 8.0, "skip_bands": ["S"], "tag": "base"},
    ]

    pieces = []
    props = []
    boxes = [
        # Substructure under West High Scriptorium (x = -40..-28, z = -12..12, y = 0..2.4)
        {"min": [-40.2, -0.4, -12.2], "max": [-28.0, 2.4, 12.2], "mat": "M_stone_dark", "tag": "base"},
        # Substructure under East Smelting Mezzanine (x = 28..36, z = 8..28, y = 0..2.4)
        {"min": [28.0, -0.4, 7.8], "max": [36.2, 2.4, 28.2], "mat": "M_stone_dark", "tag": "base"},
        # Raised Sovereign Altar Dais in North Crucible Vault
        {"min": [-5.5, 0.0, -35.2], "max": [5.5, 0.14, -30.5], "mat": "M_stone_trim", "tag": "base", "collide": False},
    ]

    def add_lancet_dressing(cx, y, cz, rot):
        """Dress a subterranean lancet window with stained glass + dark cliff backing."""
        props.append({"kit": "glass_lancet", "at": [cx, y, cz], "rot": rot, "tag": "glory"})
        props.append({"kit": "glass_lancet_broken", "at": [cx, y, cz], "rot": rot, "tag": "ruin"})
        if rot == 0:
            boxes.append({"min": [cx - 2.1, y, cz - 0.65], "max": [cx + 2.1, y + 4.1, cz - 0.35], "mat": "M_stone_dark", "tag": "base"})
        elif rot == 180:
            boxes.append({"min": [cx - 2.1, y, cz + 0.35], "max": [cx + 2.1, y + 4.1, cz + 0.65], "mat": "M_stone_dark", "tag": "base"})
        elif rot == 90:
            boxes.append({"min": [cx - 0.65, y, cz - 2.1], "max": [cx - 0.35, y + 4.1, cz + 2.1], "mat": "M_stone_dark", "tag": "base"})
        elif rot == -90:
            boxes.append({"min": [cx + 0.35, y, cz - 2.1], "max": [cx + 0.65, y + 4.1, cz + 2.1], "mat": "M_stone_dark", "tag": "base"})

    def add_wall_x(z, x0, x1, rot, y=0.0, openings=None, upper=True, upper_windows=None, cornice=True):
        """Place 4m wall segments along X at fixed Z, optionally with a second storey at y+4."""
        openings = openings or {}
        if upper_windows is None:
            upper_windows = set(range(x0 + 2, x1, 8))
        for x in range(x0, x1, 4):
            cx = x + 2
            kit = openings.get(cx, "wall_4x4")
            pieces.append({"kit": kit, "at": [cx, y, z], "rot": rot, "tag": "base"})
            if kit == "window_lancet_4m":
                add_lancet_dressing(cx, y, z, rot)
            if cornice:
                pieces.append({"kit": "cornice_4m", "at": [cx, y + 4.0, z], "rot": rot, "tag": "base", "collide": False})
            if upper:
                ukit = "window_lancet_4m" if cx in upper_windows else "wall_4x4"
                pieces.append({"kit": ukit, "at": [cx, y + 4.0, z], "rot": rot, "tag": "base"})
                if ukit == "window_lancet_4m":
                    add_lancet_dressing(cx, y + 4.0, z, rot)

    def add_wall_z(x, z0, z1, rot, y=0.0, openings=None, upper=True, upper_windows=None, cornice=True):
        """Place 4m wall segments along Z at fixed X, optionally with a second storey at y+4."""
        openings = openings or {}
        if upper_windows is None:
            upper_windows = set(range(z0 + 2, z1, 8))
        for z in range(z0, z1, 4):
            cz = z + 2
            kit = openings.get(cz, "wall_4x4")
            pieces.append({"kit": kit, "at": [x, y, cz], "rot": rot, "tag": "base"})
            if kit == "window_lancet_4m":
                add_lancet_dressing(x, y, cz, rot)
            if cornice:
                pieces.append({"kit": "cornice_4m", "at": [x, y + 4.0, cz], "rot": rot, "tag": "base", "collide": False})
            if upper:
                ukit = "window_lancet_4m" if cz in upper_windows else "wall_4x4"
                pieces.append({"kit": ukit, "at": [x, y + 4.0, cz], "rot": rot, "tag": "base"})
                if ukit == "window_lancet_4m":
                    add_lancet_dressing(x, y + 4.0, cz, rot)

    # =========================================================================
    # PERIMETER & INTERIOR PARTITION WALLS
    # =========================================================================

    # 1. East Entrance Gallery & Forge (x = 16..28, z = -8..8, y = 0)
    add_wall_x(-8, 16, 28, 0, openings={22: "window_lancet_4m"})
    add_wall_z(28, -8, 8, -90, openings={-6: "window_lancet_4m", 6: "window_lancet_4m"})
    # Return portal frame inside East wall at [27.6, 0, 0]
    pieces.append({"kit": "portal_4m", "at": [27.6, 0, 0], "rot": -90, "tag": "base"})
    pieces.append({"kit": "rose_window", "at": [27.65, 5.6, 0], "rot": -90, "tag": "base", "collide": False})

    # Partition between Entrance Gallery (x=16..28) and Main Foundry (x=-16..16) along x=16, z=-8..8
    add_wall_z(16, -8, 8, -90, openings={-2: "arcade_4m", 2: "arcade_4m"}, upper_windows=set())
    # Partition between Entrance Gallery (z=-8..8) and SE Smelting Cistern (z=8..28) along z=8, x=16..28
    add_wall_x(8, 16, 28, 180, openings={22: "arcade_4m"}, upper_windows=set())

    # 2. Main Amber Foundry Nave outer segments at x=16 (z=-12..-8 and z=8..12)
    add_wall_z(16, -12, -8, -90, openings={-10: "window_lancet_4m"})
    add_wall_z(16, 8, 12, -90, openings={10: "arcade_4m"}, upper_windows=set())

    # North wall of Main Foundry / South wall of Crucible Boss Vault at z=-12, x=-16..16
    add_wall_x(-12, -16, 16, 0, openings={-2: "portal_4m"}, upper_windows={-10, 10})
    pieces.append({"kit": "rose_window", "at": [-2.0, 5.6, -11.65], "rot": 0, "tag": "base", "collide": False})

    # South wall of Main Foundry / North wall of Apiary Cloister at z=12, x=-16..16
    add_wall_x(12, -16, 16, 180, openings={-6: "arcade_4m", -2: "arcade_4m", 2: "arcade_4m", 6: "arcade_4m"}, upper_windows={-10, 10})
    pieces.append({"kit": "rose_window", "at": [0.0, 5.6, 11.65], "rot": 180, "tag": "base", "collide": False})

    # West wall of Main Foundry / East wall of West Reliquary at x=-16, z=-12..12
    add_wall_z(-16, -12, 12, 90, openings={-6: "portal_4m", 2: "portal_4m"}, upper_windows=set())

    # 3. South Apiary Cloister & Conservatory (x = -16..16, z = 12..28)
    add_wall_x(28, -16, 16, 180, openings={-10: "window_lancet_4m", -2: "window_lancet_4m", 2: "window_lancet_4m", 10: "window_lancet_4m"})
    # West partition of Apiary Cloister into SW Ossuary Crypt at x=-16, z=12..28
    add_wall_z(-16, 12, 28, 90, openings={18: "portal_4m", 22: "arcade_4m"}, upper_windows=set())
    # East partition of Apiary Cloister into SE Smelting Cistern at x=16, z=12..28
    add_wall_z(16, 12, 28, -90, openings={18: "arcade_4m", 22: "arcade_4m"}, upper_windows=set())

    # 4. South-East Smelting Cistern (x = 16..28, z = 8..28, y = 0.0)
    add_wall_x(28, 16, 28, 180, openings={22: "window_lancet_4m"})
    # Step up at x = 28 (z = 8..28) to East Elevated Smelting Mezzanine (y = 2.4)
    pieces.append({"kit": "stair_grand_4m", "at": [28, 2.38, 18], "rot": 90, "tag": "base"})
    for cz in (10, 14, 22, 26):
        pieces.append({"kit": "balustrade_4m", "at": [28.2, 2.4, cz], "rot": 90, "tag": "base"})

    # 5. East Elevated Smelting Mezzanine (x = 28..36, z = 8..28, y = 2.4)
    add_wall_x(8, 28, 36, 0, y=2.4, openings={32: "window_lancet_4m"}, upper=False)
    add_wall_x(28, 28, 36, 180, y=2.4, openings={32: "window_lancet_4m"}, upper=False)
    add_wall_z(36, 8, 28, -90, y=2.4, openings={14: "window_lancet_4m", 22: "window_lancet_4m"}, upper=False)

    # 6. West Guildmaster's Reliquary Antechamber (x = -28..-16, z = -12..12, y = 0.0)
    add_wall_x(-12, -28, -16, 0, openings={-22: "window_lancet_4m"})
    # Partition between West Reliquary (z=-12..12) and SW Ossuary Crypt (z=12..28) at z=12
    add_wall_x(12, -28, -16, 180, openings={-22: "portal_4m"}, upper_windows=set())
    # Step up at x = -28 (z = -12..12) to West High Scriptorium & Treasury (y = 2.4)
    pieces.append({"kit": "stair_grand_4m", "at": [-28, 2.38, 0], "rot": -90, "tag": "base"})
    for cz in (-10, -6, 6, 10):
        pieces.append({"kit": "balustrade_4m", "at": [-28.2, 2.4, cz], "rot": -90, "tag": "base"})

    # 7. West High Scriptorium & Reliquary Sanctuary (x = -40..-28, z = -12..12, y = 2.4)
    add_wall_x(-12, -40, -28, 0, y=2.4, openings={-34: "window_lancet_4m"}, upper=False)
    add_wall_x(12, -40, -28, 180, y=2.4, openings={-34: "window_lancet_4m"}, upper=False)
    add_wall_z(-40, -12, 12, 90, y=2.4, openings={-6: "window_lancet_4m", 0: "window_lancet_4m", 6: "window_lancet_4m"}, upper=False)

    # 8. South-West Wax-Crypt & Ossuary (x = -28..-16, z = 12..28, y = 0.0)
    add_wall_z(-28, 12, 28, 90, openings={16: "ossuary_wall_4m", 20: "window_lancet_4m", 24: "ossuary_wall_4m"})
    add_wall_x(28, -28, -16, 180, openings={-26: "ossuary_wall_4m", -22: "window_lancet_4m", -18: "ossuary_wall_4m"})

    # 9. North Crucible Boss Vault (x = -16..16, z = -36..-12, y = 0.0)
    add_wall_z(-16, -36, -12, 90, openings={-30: "window_lancet_4m", -22: "window_lancet_4m", -18: "window_lancet_4m"})
    add_wall_z(16, -36, -12, -90, openings={-30: "window_lancet_4m", -22: "window_lancet_4m", -18: "window_lancet_4m"})
    # North wall of Crucible Vault at z = -36: outer wings x = -16..-8 and 8..16,
    # plus central archway screen at x = -8..8 into the North Sovereign Postern Sanctuary!
    add_wall_x(-36, -16, -8, 0, openings={-14: "window_lancet_4m"})
    add_wall_x(-36, 8, 16, 0, openings={14: "window_lancet_4m"})
    add_wall_x(-36, -8, 8, 0, openings={-2: "arcade_4m", 2: "arcade_4m"}, upper_windows=set())
    pieces.append({"kit": "rose_window", "at": [0.0, 5.6, -35.65], "rot": 0, "tag": "base", "collide": False})

    # 10. North Sovereign Postern Sanctuary (x = -8..8, z = -48..-36, y = 0.0)
    add_wall_z(-8, -48, -36, 90, openings={-42: "window_lancet_4m"})
    add_wall_z(8, -48, -36, -90, openings={-42: "window_lancet_4m"})
    add_wall_x(-48, -8, 8, 0, openings={-6: "window_lancet_4m", 6: "window_lancet_4m"})
    # Grand portal frame inside North wall at [0, 0, -47.6] leading to The Sovereign Apiary
    pieces.append({"kit": "portal_4m", "at": [0.0, 0, -47.6], "rot": 0, "tag": "base"})
    pieces.append({"kit": "rose_window", "at": [0.0, 5.6, -47.65], "rot": 0, "tag": "base", "collide": False})

    # =========================================================================
    # 2-STOREY STRUCTURAL COLONNADES (comb_pillar_4m at y=0 + column_4m at y=4)
    # =========================================================================
    def add_tall_pier(px, pz, scons_rot=None):
        pieces.append({"kit": "comb_pillar_4m", "at": [px, 0, pz], "rot": 0, "tag": "base"})
        pieces.append({"kit": "column_4m", "at": [px, 4.0, pz], "rot": 0, "tag": "base", "collide": False})
        if scons_rot is not None:
            dx = 0.45 * (1 if scons_rot == 90 else (-1 if scons_rot == -90 else 0))
            dz = 0.45 * (1 if scons_rot == 0 else (-1 if scons_rot == 180 else 0))
            props.append({"kit": "sconce_torch", "at": [px + dx, 2.3, pz + dz], "rot": scons_rot, "tag": "glory"})

    # Main Foundry Nave colonnade
    for cx in (-10, -2, 6):
        add_tall_pier(cx, -6, 0)
        add_tall_pier(cx, 6, 180)
    # South Apiary Cloister colonnade
    for cx in (-10, 10):
        add_tall_pier(cx, 16, 90 if cx < 0 else -90)
        add_tall_pier(cx, 24, 90 if cx < 0 else -90)
    # North Crucible Boss Vault colonnade
    for cx in (-10, 10):
        for cz in (-18, -26, -32):
            add_tall_pier(cx, cz, 90 if cx < 0 else -90)
    # East Entrance & SE Smelting Cistern piers
    for cz in (-4, 4, 14, 22):
        add_tall_pier(22, cz, -90)
    # West Reliquary Antechamber & SW Ossuary Crypt piers
    for cz in (-6, 6, 16, 24):
        add_tall_pier(-20, cz, 90)

    # =========================================================================
    # DENSE ENVIRONMENTAL DECORATION & GUILD PROPS
    # =========================================================================

    # Processional carpets & mosaic medallions down the Foundry, Apiary, and Crucible
    for rx, rz, rrot in [
        (22.0, 0.0, 90), (8.0, 0.0, 90), (-4.0, 0.0, 90),
        (-2.0, -18.0, 0), (-2.0, -26.0, 0), (0.0, -42.0, 0),
        (0.0, 20.0, 0),
    ]:
        props.append({"kit": "carpet_runner_8m", "at": [rx, 0, rz], "rot": rrot, "tag": "base", "collide": False})
    for mx, my, mz in [(2.0, 0, 0.0), (0.0, 0, 16.0), (-2.0, 0, -22.0), (-34.0, 2.4, 0.0)]:
        props.append({"kit": "mosaic_medallion", "at": [mx, my, mz], "rot": 0, "tag": "base", "collide": False})

    # Boiling Tallow Vats (Glory) / Cold Tallow Vats (Ruin)
    vat_spots = [
        # Main Foundry
        (-6.0, 0, -6.5), (10.0, 0, -6.5), (-6.0, 0, 6.5), (10.0, 0, 6.5),
        (-13.0, 0, -6.5), (-13.0, 0, 6.5),
        # East Forge & SE Smelting Cistern + Mezzanine
        (24.5, 0, -5.0), (19.0, 0, 12.5), (25.0, 0, 12.5),
        (19.0, 0, 24.5), (25.0, 0, 24.5),
        (32.5, 2.4, 12.0), (32.5, 2.4, 24.0),
        # North Crucible Vault
        (-7.5, 0, -16.5), (7.5, 0, -16.5),
        (-7.5, 0, -24.5), (7.5, 0, -24.5),
        (-7.5, 0, -31.5), (7.5, 0, -31.5),
    ]
    for vx, vy, vz in vat_spots:
        props.append({"kit": "tallow_vat", "at": [vx, vy, vz], "rot": 0, "tag": "glory"})
        props.append({"kit": "tallow_vat_cold", "at": [vx, vy, vz], "rot": 0, "tag": "ruin"})

    # Royal Comb Screw-Presses (wax_press)
    press_spots = [
        (2.0, 0, -9.2, 0), (2.0, 0, 9.2, 180),
        (20.0, 0, 18.0, 90), (25.2, 0, 18.0, -90),
        (33.2, 2.4, 18.0, -90),
        (-13.2, 0, -22.0, 90), (13.2, 0, -22.0, -90),
    ]
    for px, py, pz, prot in press_spots:
        props.append({"kit": "wax_press", "at": [px, py, pz], "rot": prot, "tag": "base"})

    # Suspended Chandler's Dipping Wheels + Gilt Chandeliers (hanging in the 8m vaults)
    wheel_spots = [
        (-8.0, 3.6, -4.0), (4.0, 3.6, -4.0),
        (-8.0, 3.6, 4.0), (4.0, 3.6, 4.0),
        (22.0, 3.6, 0.0), (22.0, 3.6, 18.0),
        (-6.0, 3.6, 20.0), (6.0, 3.6, 20.0),
        (-22.0, 3.6, 0.0), (-22.0, 3.6, 20.0),
        (-5.5, 3.8, -20.0), (5.5, 3.8, -20.0),
        (-5.5, 3.8, -29.0), (5.5, 3.8, -29.0),
        (0.0, 3.8, -42.0),
    ]
    for wx, wy, wz in wheel_spots:
        props.append({"kit": "wax_wheel", "at": [wx, wy, wz], "rot": 0, "tag": "base"})

    for gx, gy, gz in [(0.0, 5.2, 0.0), (0.0, 5.2, 20.0), (-2.0, 5.4, -24.0), (-34.0, 5.2, 0.0)]:
        props.append({"kit": "chandelier_gilt", "at": [gx, gy, gz], "rot": 0, "tag": "glory"})

    # Sacred Golden Skeps (apiary_skep)
    skep_spots = [
        (-13.2, 0, 15.0, 90), (-13.2, 0, 20.0, 90), (-13.2, 0, 25.0, 90),
        (13.2, 0, 15.0, -90), (13.2, 0, 20.0, -90), (13.2, 0, 25.0, -90),
        (-6.5, 0, 25.5, 180), (6.5, 0, 25.5, 180),
        (-4.5, 0, -33.2, 0), (4.5, 0, -33.2, 0),
        (-5.2, 0, -45.0, 45), (5.2, 0, -45.0, -45),
        (-37.0, 2.4, -9.0, 45), (-37.0, 2.4, 9.0, 135),
    ]
    for sx, sy, sz, srot in skep_spots:
        props.append({"kit": "apiary_skep", "at": [sx, sy, sz], "rot": srot, "tag": "base"})

    # Apiary Reliquary Steles (comb_shrine)
    shrine_spots = [
        (25.5, 0, 5.5, 180),
        (-13.5, 0, -10.2, 0), (13.5, 0, -10.2, 0),
        (0.0, 0, 26.2, 180),
        (-25.5, 0, -10.2, 0), (-25.5, 0, 10.2, 180),
        (-25.5, 0, 26.0, 180),
        (-13.5, 0, -34.0, 0), (13.5, 0, -34.0, 0),
        (-5.5, 0, -39.5, 90), (5.5, 0, -39.5, -90),
        (-31.0, 2.4, -10.2, 0), (-31.0, 2.4, 10.2, 180),
    ]
    for cx, cy, cz, crot in shrine_spots:
        props.append({"kit": "comb_shrine", "at": [cx, cy, cz], "rot": crot, "tag": "base"})

    # Fluted Honey Amphorae (honey_amphora) clusters
    amphora_spots = [
        (25.8, 0, -2.8), (26.2, 0, 2.8),
        (12.2, 0, -9.8), (10.8, 0, -10.2),
        (-8.8, 0, -9.8), (-10.2, 0, 9.8),
        (-8.2, 0, 14.2), (8.2, 0, 14.2),
        (17.8, 0, 9.8), (26.2, 0, 15.2), (26.2, 0, 21.2),
        (34.2, 2.4, 9.8), (34.2, 2.4, 26.2),
        (-22.5, 0, -9.8), (-22.5, 0, 9.8),
        (-38.0, 2.4, -8.5), (-38.0, 2.4, 8.5),
        (-18.0, 0, 14.2), (-25.8, 0, 14.2),
        (-13.2, 0, -14.5), (13.2, 0, -14.5),
        (-6.2, 0, -42.0), (6.2, 0, -42.0),
    ]
    for ax, ay, az in amphora_spots:
        props.append({"kit": "honey_amphora", "at": [ax, ay, az], "rot": int((ax * 37 + az * 19) % 360), "tag": "base"})

    # Botanical Garden Beds & Wellhead in the South Apiary Conservatory
    for gx, gz in [(-6.5, 17.5), (6.5, 17.5), (-6.5, 22.5), (6.5, 22.5)]:
        props.append({"kit": "garden_bed", "at": [gx, 0, gz], "rot": 0, "tag": "glory"})
        props.append({"kit": "garden_bed_dead", "at": [gx, 0, gz], "rot": 0, "tag": "ruin"})
    props.append({"kit": "wellhead", "at": [0.0, 0, 21.5], "rot": 0, "tag": "base"})
    props.append({"kit": "pew_3m", "at": [-3.2, 0, 16.5], "rot": 90, "tag": "base"})
    props.append({"kit": "pew_3m", "at": [3.2, 0, 16.5], "rot": -90, "tag": "base"})

    # East Entrance Gallery & Master Caelan's Forge Workbench
    props.append({"kit": "anvil", "at": [20.5, 0, -5.5], "rot": 35, "tag": "base"})
    props.append({"kit": "banquet_table_6m", "at": [19.5, 0, 5.5], "rot": 0, "tag": "base"})
    props.append({"kit": "book_stack", "at": [18.8, 1.15, 5.4], "rot": 15, "tag": "base"})
    props.append({"kit": "scroll_pile", "at": [20.2, 1.15, 5.6], "rot": -20, "tag": "base"})
    for bx, bz in [(25.5, -2.0), (25.5, 2.0), (13.8, -2.5), (13.8, 2.5), (-3.8, -38.0), (3.8, -38.0)]:
        props.append({"kit": "brazier_lit", "at": [bx, 0, bz], "rot": 0, "tag": "glory"})
        props.append({"kit": "brazier_cold", "at": [bx, 0, bz], "rot": 0, "tag": "ruin"})
    for bx, bz in [(-29.5, -3.2), (-29.5, 3.2), (29.5, 15.0), (29.5, 21.0)]:
        y_b = 2.4
        props.append({"kit": "brazier_lit", "at": [bx, y_b, bz], "rot": 0, "tag": "glory"})
        props.append({"kit": "brazier_cold", "at": [bx, y_b, bz], "rot": 0, "tag": "ruin"})

    # Barrels, Crates, and Hand-Carts across the Foundry & Cistern
    for cx, cy, cz, crot in [
        (13.2, 0, 9.2, -25), (25.5, 0, -6.2, 15), (26.2, 0, 26.0, 40),
        (34.0, 2.4, 14.5, -15), (-13.5, 0, 10.2, 20),
    ]:
        props.append({"kit": "crate_stack", "at": [cx, cy, cz], "rot": crot, "tag": "base"})
    for bx, by, bz in [
        (11.4, 0, 9.8), (24.0, 0, -6.5), (17.8, 0, 26.2),
        (34.2, 2.4, 21.5), (-11.8, 0, 10.2), (-18.0, 0, -9.8),
    ]:
        props.append({"kit": "barrel", "at": [bx, by, bz], "rot": 15, "tag": "base"})
    props.append({"kit": "hand_cart", "at": [-13.0, 0, 2.5], "rot": 75, "tag": "base"})
    props.append({"kit": "hand_cart", "at": [22.0, 0, 24.5], "rot": -35, "tag": "base"})

    # West Guildmaster's Reliquary Antechamber (y=0.0) & High Scriptorium (y=2.4)
    props.append({"kit": "statue_orans", "at": [-23.5, 0, -4.5], "rot": 90, "tag": "base"})
    props.append({"kit": "statue_orans", "at": [-23.5, 0, 4.5], "rot": 90, "tag": "base"})
    props.append({"kit": "choir_stall", "at": [-22.0, 0, -10.2], "rot": 0, "tag": "base"})
    props.append({"kit": "choir_stall", "at": [-22.0, 0, 10.2], "rot": 180, "tag": "base"})

    # High Scriptorium & Reliquary Sanctuary (x = -40..-28, y = 2.4)
    props.append({"kit": "altar_wick", "at": [-35.5, 2.4, 0.0], "rot": 90, "tag": "base"})
    props.append({"kit": "statue_saint", "at": [-37.8, 2.4, -4.5], "rot": 90, "tag": "base"})
    props.append({"kit": "statue_saint", "at": [-37.8, 2.4, 4.5], "rot": 90, "tag": "base"})
    for sx, sz, srot in [
        (-34.0, -10.8, 0), (-37.0, -10.8, 0),
        (-34.0, 10.8, 180), (-37.0, 10.8, 180),
    ]:
        props.append({"kit": "scriptorium_shelf", "at": [sx, 2.4, sz], "rot": srot, "tag": "base"})
    for tx, tz in [(-33.5, -5.5), (-33.5, 5.5)]:
        props.append({"kit": "banquet_table_6m", "at": [tx, 2.4, tz], "rot": 0, "tag": "base"})
        props.append({"kit": "book_stack", "at": [tx - 1.2, 3.55, tz], "rot": 20, "tag": "base"})
        props.append({"kit": "scroll_pile", "at": [tx + 1.1, 3.55, tz], "rot": -15, "tag": "base"})
    for cx, cy, cz in [
        (-34.5, 2.4, -2.5), (-34.5, 2.4, 2.5),
        (-23.5, 0, -2.5), (-23.5, 0, 2.5),
        (-2.5, 0, -33.0), (2.5, 0, -33.0),
        (-3.2, 0, -45.5), (3.2, 0, -45.5),
    ]:
        props.append({"kit": "candelabra", "at": [cx, cy, cz], "rot": 0, "tag": "glory"})

    # South-West Wax-Crypt & Ossuary (x = -28..-16, z = 12..28, y = 0.0)
    for sx, sz, srot in [(-24.5, 16.5, 90), (-24.5, 22.5, 90), (-19.5, 25.0, 180)]:
        props.append({"kit": "sarcophagus", "at": [sx, 0, sz], "rot": srot, "tag": "base"})
    for tx, tz, trot in [(-20.0, 16.0, 0), (-20.0, 21.5, 0)]:
        props.append({"kit": "tomb_slab", "at": [tx, 0, tz], "rot": trot, "tag": "base"})
    for ux, uz in [(-26.2, 18.5), (-26.2, 24.5), (-17.5, 26.2)]:
        props.append({"kit": "urn", "at": [ux, 0, uz], "rot": 0, "tag": "base"})
    for hx, hy, hz, hrot in [
        (-24.0, 0, 19.5, 65), (22.5, 0, 14.5, -110),
        (31.5, 2.4, 24.5, 140), (-11.5, 0, -18.5, 45), (11.5, 0, -28.5, -60),
    ]:
        props.append({"kit": "wax_husk", "at": [hx, hy, hz], "rot": hrot, "tag": "ruin"})

    # North Crucible Vault Sovereign's Dais altar & banners
    props.append({"kit": "altar", "at": [0.0, 0, -33.5], "rot": 0, "tag": "base"})
    props.append({"kit": "statue_saint", "at": [-13.5, 0, -26.0], "rot": 90, "tag": "base"})
    props.append({"kit": "statue_saint", "at": [13.5, 0, -26.0], "rot": -90, "tag": "base"})

    # Wall Banners across Foundry, Apiary, Reliquary, and Crucible
    banner_spots = [
        (-8.0, 2.6, -11.82, 0), (6.0, 2.6, -11.82, 0),
        (-10.0, 2.6, 11.82, 180), (10.0, 2.6, 11.82, 180),
        (-8.0, 2.6, -35.82, 0), (8.0, 2.6, -35.82, 0),
        (-15.82, 2.6, -24.0, 90), (15.82, 2.6, -24.0, -90),
        (-39.82, 5.0, -3.0, 90), (-39.82, 5.0, 3.0, 90),
        (-3.5, 2.6, -47.82, 0), (3.5, 2.6, -47.82, 0),
    ]
    for bx, by, bz, brot in banner_spots:
        props.append({"kit": "banner", "at": [bx, by, bz], "rot": brot, "tag": "glory"})
        props.append({"kit": "banner_torn", "at": [bx, by, bz], "rot": brot, "tag": "ruin"})

    # Candle clusters
    for cx, cy, cz in [
        (-21.5, 0, -2.2), (-33.5, 2.4, -1.8), (-33.5, 2.4, 1.8),
        (14.0, 0, -4.5), (-3.5, 0, 24.5), (3.5, 0, 24.5),
        (-3.5, 0, -32.5), (3.5, 0, -32.5),
    ]:
        props.append({"kit": "candle_cluster", "at": [cx, cy, cz], "rot": 20, "tag": "glory"})
        props.append({"kit": "candle_cluster_dead", "at": [cx, cy, cz], "rot": 20, "tag": "ruin"})

    # =========================================================================
    # VIGIL LANTERNS, NPCS, LOCKS, GATES, SPAWNERS, PICKUPS, PLAQUES, PORTALS
    # =========================================================================
    lanterns = [
        {"id": "hollow_foundry", "name": "Amber Foundry Vigil", "at": [18.5, 0, 0.0], "rot": -90},
        {"id": "hollow_postern", "name": "Crucible Postern Vigil", "at": [4.5, 0, -41.5], "rot": -90},
    ]

    npcs = [
        {"id": "master_caelan", "at": [21.5, 0, -3.5], "rot": -35, "tag": "glory"}
    ]

    # Votive Lock in the South Apiary Cloister -> unbars the West Guild Reliquary
    votive_locks = [
        {
            "flag": "hollow_reliquary_open",
            "tag": "base",
            "votives": [
                {"at": [-4.5, 0, 15.0]},
                {"at": [4.5, 0, 15.0]},
                {"at": [-4.5, 0, 24.0]},
                {"at": [4.5, 0, 24.0]},
            ],
        }
    ]

    flag_gates = [
        {
            "flag": "hollow_reliquary_open",
            "kit": "door_leaf",
            "at": [-16.0, 0, 2.0],
            "rot": 90,
            "tag": "base",
        }
    ]

    gates = [
        {
            "id": "hollow_reliquary_shortcut",
            "at": [-16.0, 0, -6.0],
            "rot": 90,
            "locked_prompt": "Barred from within the Guildmaster's Reliquary",
        }
    ]

    fog_gates = [
        {
            "id": "hollow_boss_fog",
            "at": [-2.0, 0, -12.0],
            "rot": 0,
            "tag": "ruin",
        }
    ]

    spawners = [
        {
            "id": "foundry_melter_1",
            "enemy": "tallow_melter",
            "at": [-2.0, 0, -2.5],
            "face": 90,
            "tag": "ruin",
        },
        {
            "id": "foundry_melter_2",
            "enemy": "tallow_melter",
            "at": [-10.0, 0, 2.5],
            "face": 110,
            "tag": "ruin",
        },
        {
            "id": "foundry_wax_1",
            "enemy": "waxbound",
            "at": [4.0, 0, 3.5],
            "face": 180,
            "tag": "ruin",
        },
        {
            "id": "cistern_melter_1",
            "enemy": "tallow_melter",
            "at": [22.0, 0, 16.0],
            "face": 0,
            "tag": "ruin",
        },
        {
            "id": "cistern_wax_1",
            "enemy": "waxbound",
            "at": [22.0, 0, 22.0],
            "face": 0,
            "tag": "ruin",
        },
        {
            "id": "mezzanine_melter",
            "enemy": "tallow_melter",
            "at": [31.5, 2.4, 18.0],
            "face": -90,
            "tag": "ruin",
        },
        {
            "id": "apiary_melter",
            "enemy": "tallow_melter",
            "at": [0.0, 0, 17.5],
            "face": 180,
            "tag": "ruin",
        },
        {
            "id": "apiary_echo",
            "enemy": "gilded_echo",
            "at": [-9.5, 0, 20.5],
            "face": 60,
            "tag": "ruin",
        },
        {
            "id": "apiary_echo_2",
            "enemy": "gilded_echo",
            "at": [9.5, 0, 20.5],
            "face": -60,
            "tag": "ruin",
        },
        {
            "id": "crypt_warden",
            "enemy": "comb_warden",
            "at": [-22.0, 0, 21.0],
            "face": 0,
            "tag": "ruin",
        },
        {
            "id": "reliquary_warden",
            "enemy": "comb_warden",
            "at": [-31.5, 2.4, 0.0],
            "face": 90,
            "tag": "ruin",
        },
        {
            "id": "hollow_boss",
            "enemy": "sovereign_chandler",
            "at": [-2.0, 0, -26.0],
            "face": 180,
            "dead_once": True,
            "fog_gate_id": "hollow_boss_fog",
            "tag": "ruin",
        },
    ]

    pickups = [
        {
            "id": "hollow_censer_mace",
            "at": [-22.2, 0, 0.0],
            "item": "chandler_mace",
            "count": 1,
            "orisons": 200,
            "tag": "base",
            "label": "Claim the Chandler's Censer-Mace",
        },
        {
            "id": "scriptorium_high_tome",
            "at": [-33.8, 2.4, 0.0],
            "item": "candleglass",
            "count": 1,
            "orisons": 320,
            "tag": "base",
            "label": "Gather the Guildmaster's Assay-Glass",
        },
        {
            "id": "crypt_amber_rite",
            "at": [-22.5, 0, 24.5],
            "item": "amber_benediction",
            "count": 1,
            "orisons": 220,
            "tag": "base",
            "label": "Claim the Rite of the Golden Comb",
        },
        {
            "id": "apiary_comb_cache",
            "at": [0.0, 0, 24.5],
            "item": "candleglass",
            "count": 1,
            "orisons": 180,
            "tag": "base",
            "label": "Gather the Queen-Skep candleglass",
        },
        {
            "id": "mezzanine_press_hoard",
            "at": [31.5, 2.4, 11.0],
            "item": "radiant_token",
            "count": 1,
            "orisons": 240,
            "tag": "base",
            "label": "Claim the Chief Skimmer's Token",
        },
        {
            "id": "foundry_vat_purse",
            "at": [-13.5, 0, -8.5],
            "orisons": 165,
            "tag": "base",
            "label": "Gather the skimmer's tally-purse",
        },
        {
            "id": "crucible_royal_hoard",
            "at": [0.0, 0, -31.2],
            "item": "candleglass",
            "count": 2,
            "orisons": 650,
            "tag": "base",
            "label": "Claim the Seventh Tithe Chest",
        },
    ]

    plaques = [
        {
            "at": [17.8, 0, 3.8],
            "rot": -135,
            "text": (
                "CHARTER OF THE AMBER FOUNDRY\n\n"
                "Let no tallow of flesh or beast enter these kettles. Here the Guild "
                "boils only the comb of the Golden Skeps, gathered from the cliff-meadows "
                "while the noon was whole.\n\n"
                "Four votives in the South Cloister keep the Reliquary unbarred."
            ),
        },
        {
            "at": [0.0, 0, 13.8],
            "rot": 0,
            "text": (
                "THE GOLDEN SKEPS\n\n"
                "The sun-bees do not sting the hand that smells of prayer. In glory their "
                "hives hum with remembered noon; in ruin the comb sets harder than bronze."
            ),
        },
        {
            "at": [-21.5, 0, 3.5],
            "rot": 150,
            "text": (
                "THE GUILDMASTER'S RELIQUARY\n\n"
                "Here rests the Censer-Mace of the First Chandler — flanged in vat-bronze, "
                "cored with an undying coal of royal wax. Above the western stair stands "
                "the High Scriptorium where the tithe-ledgers were sealed."
            ),
        },
        {
            "at": [-19.5, 0, 14.5],
            "rot": -45,
            "text": (
                "OSSUARY OF THE FIRST CHANDLERS\n\n"
                "Those who tended the Queen-Skeps were not buried in earth; their shrouds "
                "were steeped seven times in clarified comb until time could find no seam "
                "to enter. With them rests the Rite of the Golden Comb."
            ),
        },
        {
            "at": [-5.2, 0, -10.5],
            "rot": 20,
            "text": (
                "EDICT OF REFUSAL\n\n"
                "By hand of Malakor, Sovereign Chandler: The seventh wagon from the Hour "
                "Palace shall return empty. What light remains in the Queen-Combs belongs "
                "to the Parish and the bees. Let the Sovereign come down and skim the vats himself."
            ),
        },
        {
            "at": [-3.2, 0, -40.5],
            "rot": 25,
            "text": (
                "THE CLIFF-STAIR TO THE SOVEREIGN APIARY\n\n"
                "Beyond this postern climbs the cliff-path to the Cloister of the Golden Comb, "
                "where Matriarch Aurelia and her blind sisters tended the living hives in the "
                "salt wind above the sea."
            ),
        },
    ]

    portals = [
        {
            "to": "old_outskirts",
            "at": [26.2, 0, 0.0],
            "rot": -90,
            "spawn": [-54.0, 0.2, -15.0],
            "spawn_yaw": -90,
            "prompt": "Ascend to the Old Outskirts",
        },
        {
            "to": "sovereign_apiary",
            "at": [0.0, 0, -46.2],
            "rot": 0,
            "spawn": [0.0, 0.2, 8.5],
            "spawn_yaw": 0,
            "prompt": "Ascend to the Sovereign Apiary",
        },
    ]

    scripted = [
        {
            "script": "res://src/world/ambient_life.gd",
            "at": [0, 0, 20],
            "rot": 0,
            "tag": "glory",
            "params": {"kind": "motes_gold", "extent": [12, 4, 7], "count": 32},
        },
        {
            "script": "res://src/world/ambient_life.gd",
            "at": [0, 0, 0],
            "rot": 0,
            "tag": "glory",
            "params": {"kind": "motes_gold", "extent": [14, 5, 10], "count": 28},
        },
        {
            "script": "res://src/world/ambient_life.gd",
            "at": [-34, 2.4, 0],
            "rot": 0,
            "tag": "glory",
            "params": {"kind": "motes_gold", "extent": [5, 4, 8], "count": 18},
        },
        {
            "script": "res://src/world/ambient_life.gd",
            "at": [0, 0, -24],
            "rot": 0,
            "tag": "ruin",
            "params": {"kind": "motes_ash", "extent": [12, 5, 10], "count": 30},
        },
    ]

    data = {
        "id": "chandlers_hollow",
        "name": "The Chandlers' Hollow",
        "free_kindle": True,
        "start": {"pos": [24.0, 0.2, 0.0], "yaw": 90},
        "env": {
            "glory": {
                "sun_color": [0.95, 0.68, 0.34],
                "sun_energy": 0.68,
                "sun_rot": [-25, -45],
                "ambient": [0.35, 0.26, 0.16],
                "fog_color": [0.42, 0.28, 0.15],
                "bg_top": [0.16, 0.11, 0.08],
                "bg_horizon": [0.48, 0.32, 0.18],
                "fog_density": 0.012,
            },
            "ruin": {
                "sun_color": [0.28, 0.34, 0.46],
                "sun_energy": 0.14,
                "fog_color": [0.05, 0.065, 0.09],
                "bg_top": [0.025, 0.035, 0.06],
                "bg_horizon": [0.06, 0.08, 0.12],
                "fog_density": 0.014,
            },
        },
        "fills": fills,
        "boxes": boxes,
        "vault_fields": vault_fields,
        "pieces": pieces,
        "props": props,
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
        f"chandlers_hollow: pieces {len(pieces)} fills {len(fills)} props {len(props)} "
        f"spawners {len(spawners)} pickups {len(pickups)}"
    )


if __name__ == "__main__":
    build()
