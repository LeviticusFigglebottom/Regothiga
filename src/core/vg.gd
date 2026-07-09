class_name VG

## Build tag shown in the HUD pose line — proves WHICH code a screenshot ran
const BUILD := "U7"
## Global constants and enums for Vespergard.

enum WState { GLORY, RUIN }

const STATE_NAMES := { WState.GLORY: "glory", WState.RUIN: "ruin" }

static func state_from_name(n: String) -> WState:
	return WState.RUIN if n == "ruin" else WState.GLORY

## Physics layers (bit indices, 1-based as in project settings)
const L_WORLD_BASE := 1
const L_WORLD_GLORY := 2
const L_WORLD_RUIN := 3
const L_PLAYER := 4
const L_ENEMY := 5
const L_HURTBOX := 6
const L_INTERACT := 7
const L_CAMERA_CLIP := 8

## Masks
const M_WORLD_ALL := (1 << 0) | (1 << 1) | (1 << 2)  # base|glory|ruin
const M_WORLD_BASE_ONLY := 1 << 0

## Node groups
const GROUP_STATE_LISTENERS := "state_listeners"   # notified on world state change
const GROUP_ENEMIES := "enemies"
const GROUP_RESPAWN_ON_REST := "respawn_on_rest"
const GROUP_NAV_GLORY := "nav_glory"
const GROUP_NAV_RUIN := "nav_ruin"
