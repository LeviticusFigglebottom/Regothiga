#!/usr/bin/env python3
"""Build data/areas/chandlers_hollow.json — The Chandlers' Hollow (bonus optional
DLC area accessed from the West Chandlers' Quarter of the Old Outskirts).

Layout (all at y=0, 100% vaulted subterranean & under-cliff guild-foundry):
  * East Entrance Vestibule:   x =  16.. 20, z =  -4..  4
  * Main Amber Foundry Hall:   x = -16.. 16, z = -12.. 12
  * South Apiary Cloister:     x = -12.. 12, z =  12.. 24
  * West Guild Reliquary:      x = -28..-16, z =  -8..  8
  * North Crucible Boss Vault: x = -12.. 12, z = -36..-12
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "data", "areas", "chandlers_hollow.json")


def build():
    fills = [
        {"kit": "floor_4x4", "min": [16, 0, -4], "max": [20, 0, 4]},
        {"kit": "floor_4x4", "min": [-16, 0, -12], "max": [16, 0, 12]},
        {"kit": "floor_4x4", "min": [-12, 0, 12], "max": [12, 0, 24]},
        {"kit": "floor_4x4", "min": [-28, 0, -8], "max": [-16, 0, 8]},
        {"kit": "floor_4x4", "min": [-12, 0, -36], "max": [12, 0, -12]},
    ]

    vault_fields = [
        {"min": [16, 0, -4], "max": [20, 0, 4], "tag": "base"},
        {"min": [-16, 0, -12], "max": [16, 0, 12], "spring_top": 4.4, "band_from": 4.0, "tag": "base"},
        {"min": [-12, 0, 12], "max": [12, 0, 24], "tag": "base"},
        {"min": [-28, 0, -8], "max": [-16, 0, 8], "tag": "base"},
        {"min": [-12, 0, -36], "max": [12, 0, -12], "spring_top": 4.6, "band_from": 4.0, "tag": "base"},
    ]

    pieces = []
    props = []
    boxes = []

    def add_lancet_dressing(cx, cz, rot):
        """Dress a subterranean lancet window with stained glass + dark cliff backing."""
        props.append({"kit": "glass_lancet", "at": [cx, 0, cz], "rot": rot, "tag": "glory"})
        props.append({"kit": "glass_lancet_broken", "at": [cx, 0, cz], "rot": rot, "tag": "ruin"})
        # Dark cliff-rock backing box just outside the window plane so no sky leaks underground
        if rot == 0:
            boxes.append({"min": [cx - 2.1, 0, cz - 0.65], "max": [cx + 2.1, 4.2, cz - 0.35], "mat": "M_stone_dark", "tag": "base"})
        elif rot == 180:
            boxes.append({"min": [cx - 2.1, 0, cz + 0.35], "max": [cx + 2.1, 4.2, cz + 0.65], "mat": "M_stone_dark", "tag": "base"})
        elif rot == 90:
            boxes.append({"min": [cx - 0.65, 0, cz - 2.1], "max": [cx - 0.35, 4.2, cz + 2.1], "mat": "M_stone_dark", "tag": "base"})
        elif rot == -90:
            boxes.append({"min": [cx + 0.35, 0, cz - 2.1], "max": [cx + 0.65, 4.2, cz + 2.1], "mat": "M_stone_dark", "tag": "base"})

    def add_wall_x(z, x0, x1, rot, openings=None):
        """Place 4m wall/window/portal/arcade segments along X at fixed Z."""
        openings = openings or {}
        for x in range(x0, x1, 4):
            cx = x + 2
            kit = openings.get(cx, "wall_4x4")
            pieces.append({"kit": kit, "at": [cx, 0, z], "rot": rot, "tag": "base"})
            if kit == "window_lancet_4m":
                add_lancet_dressing(cx, z, rot)

    def add_wall_z(x, z0, z1, rot, openings=None):
        """Place 4m wall/window/portal/arcade segments along Z at fixed X."""
        openings = openings or {}
        for z in range(z0, z1, 4):
            cz = z + 2
            kit = openings.get(cz, "wall_4x4")
            pieces.append({"kit": kit, "at": [x, 0, cz], "rot": rot, "tag": "base"})
            if kit == "window_lancet_4m":
                add_lancet_dressing(x, cz, rot)

    # 1. East Entrance Vestibule (x = 16..20, z = -4..4)
    add_wall_z(20, -4, 4, -90)
    add_wall_x(-4, 16, 20, 0)
    add_wall_x(4, 16, 20, 180)
    # Threshold between Vestibule and Main Hall at x = 16, z = -4..4
    add_wall_z(16, -4, 4, -90, openings={-2: "arcade_4m", 2: "arcade_4m"})
    # Return portal frame inside East wall
    pieces.append({"kit": "portal_4m", "at": [19.6, 0, 0], "rot": -90, "tag": "base"})

    # 2. Main Amber Foundry Hall perimeter (x = -16..16, z = -12..12)
    # East wall segments outside vestibule (z = -12..-4 and z = 4..12 at x = 16)
    add_wall_z(16, -12, -4, -90, openings={-10: "window_lancet_4m"})
    add_wall_z(16, 4, 12, -90, openings={10: "window_lancet_4m"})

    # North wall of Main Hall (z = -12): outer wings x = -16..-12 and 12..16,
    # plus partition wall x = -12..12 with central boss portal at cx = 0 (openings at -2, 2? No, portal is 4m centered at 0, or at cx = -2 / 2).
    # Wait: audit_walls checks 4m segments: (-4..0) has center -2, (0..4) has center +2!
    # So placing portal_4m at cx = -2 (or arcade_4m at -2 and 2) aligns cleanly with the 4m grid!
    # Let's place portal_4m at cx = 2 (or cx = -2) on z = -12, and wall_4x4 on all other 4m segments!
    add_wall_x(-12, -16, -12, 0)
    add_wall_x(-12, 12, 16, 0)
    add_wall_x(-12, -12, 12, 0, openings={-2: "portal_4m"})

    # South wall of Main Hall (z = 12): outer wings x = -16..-12 and 12..16,
    # plus arcade screen into the South Apiary Cloister at cx = -2 and cx = 2
    add_wall_x(12, -16, -12, 180)
    add_wall_x(12, 12, 16, 180)
    add_wall_x(12, -12, 12, 180, openings={-2: "arcade_4m", 2: "arcade_4m"})

    # West wall of Main Hall (x = -16): outer wings z = -12..-8 and 8..12,
    # plus partition into West Guild Reliquary (z = -8..8) with portal_4m at cz = 2 (votive-locked)
    # and portal_4m at cz = -6 (shortcut gate)
    add_wall_z(-16, -12, -8, 90)
    add_wall_z(-16, 8, 12, 90)
    add_wall_z(-16, -8, 8, 90, openings={-6: "portal_4m", 2: "portal_4m"})

    # 3. South Apiary Cloister perimeter (x = -12..12, z = 12..24)
    add_wall_z(-12, 12, 24, 90, openings={18: "window_lancet_4m"})
    add_wall_z(12, 12, 24, -90, openings={18: "window_lancet_4m"})
    add_wall_x(24, -12, 12, 180, openings={-6: "window_lancet_4m", 6: "window_lancet_4m"})

    # 4. West Guildmaster's Reliquary perimeter (x = -28..-16, z = -8..8)
    add_wall_z(-28, -8, 8, 90, openings={-2: "window_lancet_4m", 2: "window_lancet_4m"})
    add_wall_x(-8, -28, -16, 0)
    add_wall_x(8, -28, -16, 180)

    # 5. North Crucible Boss Vault perimeter (x = -12..12, z = -36..-12)
    add_wall_z(-12, -36, -12, 90, openings={-30: "window_lancet_4m", -18: "window_lancet_4m"})
    add_wall_z(12, -36, -12, -90, openings={-30: "window_lancet_4m", -18: "window_lancet_4m"})
    add_wall_x(-36, -12, 12, 0, openings={-6: "window_lancet_4m", 6: "window_lancet_4m"})

    # Structural columns in Main Hall and Boss Vault
    for cx in (-10, -2, 6):
        for cz in (-6, 6):
            pieces.append({"kit": "column_4m", "at": [cx, 0, cz], "rot": 0, "tag": "base"})
    for cx in (-8, 8):
        for cz in (-18, -30):
            pieces.append({"kit": "column_4m", "at": [cx, 0, cz], "rot": 0, "tag": "base"})

    # Props: Boiling Tallow Vats (Glory) / Cold Tallow Vats (Ruin), Golden Skeps, Dipping Wheels
    vat_spots = [
        (-6.0, -6.5), (10.0, -6.5),
        (-6.0, 6.5), (10.0, 6.5),
        (-7.5, -16.5), (7.5, -16.5),
        (-7.5, -31.5), (7.5, -31.5),
    ]
    for vx, vz in vat_spots:
        props.append({"kit": "tallow_vat", "at": [vx, 0, vz], "rot": 0, "tag": "glory"})
        props.append({"kit": "tallow_vat_cold", "at": [vx, 0, vz], "rot": 0, "tag": "ruin"})

    # Suspended Chandler's Dipping Wheels (hanging from vault_fields)
    wheel_spots = [
        (-6.0, 2.2, -3.0), (6.0, 2.2, -3.0),
        (-6.0, 2.2, 3.0), (6.0, 2.2, 3.0),
        (0.0, 2.0, 18.0),
        (-4.5, 2.4, -24.0), (4.5, 2.4, -24.0),
    ]
    for wx, wy, wz in wheel_spots:
        props.append({"kit": "wax_wheel", "at": [wx, wy, wz], "rot": 0, "tag": "base"})

    # Sacred Golden Skeps in the South Apiary Cloister + North Crucible Dais
    skep_spots = [
        (-9.0, 15.0, 90), (-9.0, 20.5, 90),
        (9.0, 15.0, -90), (9.0, 20.5, -90),
        (-4.0, 21.8, 180), (4.0, 21.8, 180),
        (-4.5, -33.2, 0), (4.5, -33.2, 0),
    ]
    for sx, sz, srot in skep_spots:
        props.append({"kit": "apiary_skep", "at": [sx, 0, sz], "rot": srot, "tag": "base"})

    # Master Caelan's workbench & smithing anvil in the East Foundry bay
    props.append({"kit": "anvil", "at": [12.5, 0, -4.5], "rot": 35, "tag": "base"})
    props.append({"kit": "brazier_lit", "at": [13.5, 0, -2.5], "rot": 0, "tag": "glory"})
    props.append({"kit": "brazier_cold", "at": [13.5, 0, -2.5], "rot": 0, "tag": "ruin"})
    props.append({"kit": "brazier_lit", "at": [13.5, 0, 2.5], "rot": 0, "tag": "glory"})
    props.append({"kit": "brazier_cold", "at": [13.5, 0, 2.5], "rot": 0, "tag": "ruin"})
    props.append({"kit": "crate_stack", "at": [13.2, 0, 9.2], "rot": -25, "tag": "base"})
    props.append({"kit": "barrel", "at": [11.2, 0, 9.8], "rot": 15, "tag": "base"})
    props.append({"kit": "hand_cart", "at": [-13.0, 0, 8.5], "rot": 55, "tag": "base"})

    # West Guildmaster's Reliquary dressing
    props.append({"kit": "altar", "at": [-24.5, 0, 0.0], "rot": 90, "tag": "base"})
    props.append({"kit": "statue_saint", "at": [-25.5, 0, -4.5], "rot": 90, "tag": "base"})
    props.append({"kit": "statue_saint", "at": [-25.5, 0, 4.5], "rot": 90, "tag": "base"})
    props.append({"kit": "candelabra", "at": [-23.5, 0, -2.5], "rot": 0, "tag": "glory"})
    props.append({"kit": "candelabra", "at": [-23.5, 0, 2.5], "rot": 0, "tag": "glory"})
    props.append({"kit": "candle_cluster", "at": [-21.5, 0, -2.2], "rot": 20, "tag": "glory"})
    props.append({"kit": "candle_cluster_dead", "at": [-21.5, 0, -2.2], "rot": 20, "tag": "ruin"})

    # North Crucible Vault Sovereign's Dais altar & banners
    props.append({"kit": "altar", "at": [0.0, 0, -33.5], "rot": 0, "tag": "base"})
    props.append({"kit": "candelabra", "at": [-2.5, 0, -33.0], "rot": 0, "tag": "glory"})
    props.append({"kit": "candelabra", "at": [2.5, 0, -33.0], "rot": 0, "tag": "glory"})
    for bx in (-8.0, 8.0):
        props.append({"kit": "banner", "at": [bx, 0.8, -35.85], "rot": 0, "tag": "glory"})
        props.append({"kit": "banner_torn", "at": [bx, 0.8, -35.85], "rot": 0, "tag": "ruin"})

    lanterns = [
        {"id": "hollow_foundry", "name": "Amber Foundry Vigil", "at": [11.5, 0, 0.0], "rot": -90}
    ]

    npcs = [
        {"id": "master_caelan", "at": [9.5, 0, -4.2], "rot": -115, "tag": "glory"}
    ]

    # Votive Lock in the South Apiary Cloister -> unbars the West Guild Reliquary
    votive_locks = [
        {
            "flag": "hollow_reliquary_open",
            "tag": "base",
            "votives": [
                {"at": [-4.5, 0, 15.0]},
                {"at": [4.5, 0, 15.0]},
                {"at": [-4.5, 0, 19.5]},
                {"at": [4.5, 0, 19.5]},
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
            "at": [2.0, 0, 4.5],
            "face": 180,
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
            "at": [-6.0, 0, 18.5],
            "face": 60,
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
            "id": "apiary_comb_cache",
            "at": [0.0, 0, 22.0],
            "item": "candleglass",
            "count": 1,
            "orisons": 180,
            "tag": "base",
            "label": "Gather the Queen-Skep candleglass",
        },
        {
            "id": "foundry_vat_purse",
            "at": [-13.5, 0, -9.5],
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
            "at": [13.8, 0, 3.2],
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
                "cored with an undying coal of royal wax. It answers strength of arm and "
                "devotion of spirit alike."
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
    ]

    portals = [
        {
            "to": "old_outskirts",
            "at": [18.5, 0, 0.0],
            "rot": -90,
            "spawn": [-54.0, 0.2, -15.0],
            "spawn_yaw": -90,
            "prompt": "Ascend to the Old Outskirts",
        }
    ]

    scripted = [
        {
            "script": "res://src/world/ambient_life.gd",
            "at": [0, 0, 18],
            "rot": 0,
            "tag": "glory",
            "params": {"kind": "motes_gold", "extent": [10, 3, 5], "count": 28},
        },
        {
            "script": "res://src/world/ambient_life.gd",
            "at": [0, 0, 0],
            "rot": 0,
            "tag": "glory",
            "params": {"kind": "motes_gold", "extent": [14, 4, 10], "count": 24},
        },
        {
            "script": "res://src/world/ambient_life.gd",
            "at": [0, 0, -24],
            "rot": 0,
            "tag": "ruin",
            "params": {"kind": "motes_ash", "extent": [10, 4, 10], "count": 26},
        },
    ]

    data = {
        "id": "chandlers_hollow",
        "name": "The Chandlers' Hollow",
        "free_kindle": True,
        "start": {"pos": [15.0, 0.2, 0.0], "yaw": 90},
        "env": {
            "glory": {
                "sun_color": [0.95, 0.68, 0.34],
                "sun_energy": 0.65,
                "sun_rot": [-25, -45],
                "ambient": [0.34, 0.25, 0.16],
                "fog_color": [0.42, 0.28, 0.15],
                "bg_top": [0.16, 0.11, 0.08],
                "bg_horizon": [0.48, 0.32, 0.18],
                "fog_density": 0.014,
            },
            "ruin": {
                "sun_color": [0.28, 0.34, 0.46],
                "sun_energy": 0.14,
                "fog_color": [0.05, 0.065, 0.09],
                "bg_top": [0.025, 0.035, 0.06],
                "bg_horizon": [0.06, 0.08, 0.12],
                "fog_density": 0.016,
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
