extends Node
## World — persistent world model: per-area glory/ruin state, flags, the
## pending Remembrance, last vigil, and save/load. Pure data; no scene logic.

signal area_state_changed(area_id: String, state: VG.WState)

var areas: Dictionary = {}        # id -> {state:int, cleared:bool, flags:{}}
var flags: Dictionary = {}        # global story/npc flags
var remembrance = null            # {area:String, pos:Array[3], amount:int} or null
var last_vigil := {"area": "", "lantern": ""}
var player_data: Dictionary = {}  # written by Game on save

var _save_dir := "user://saves"

func _enter_tree() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--save-dir="):
			_save_dir = arg.get_slice("=", 1)

func _area(id: String) -> Dictionary:
	if not areas.has(id):
		areas[id] = {"state": VG.WState.GLORY, "cleared": false, "flags": {}}
	return areas[id]

func get_area_state(id: String) -> VG.WState:
	return _area(id)["state"] as VG.WState

func set_area_state(id: String, s: VG.WState) -> void:
	var a := _area(id)
	if a["state"] == s:
		return
	a["state"] = s
	area_state_changed.emit(id, s)

func is_cleared(id: String) -> bool:
	return _area(id)["cleared"]

func set_cleared(id: String, v := true) -> void:
	_area(id)["cleared"] = v

func area_flag(id: String, flag: String) -> bool:
	return _area(id)["flags"].get(flag, false)

func set_area_flag(id: String, flag: String, v := true) -> void:
	_area(id)["flags"][flag] = v

func flag(name: String) -> bool:
	return flags.get(name, false)

func flag_val(name: String, def = null):
	return flags.get(name, def)

func set_flag(name: String, v = true) -> void:
	flags[name] = v

func set_remembrance(area: String, pos: Vector3, amount: int) -> void:
	remembrance = {"area": area, "pos": [pos.x, pos.y, pos.z], "amount": amount}

func clear_remembrance() -> void:
	remembrance = null

func remembrance_pos() -> Vector3:
	if remembrance == null:
		return Vector3.ZERO
	var p = remembrance["pos"]
	return Vector3(p[0], p[1], p[2])

# ---------------- persistence ----------------

## Three vigils may be kept at once. Each slot file carries a small meta
## ledger (level, quarter, difficulty, hours walked) for the title's picker.
const SLOTS := 3
var active_slot := 1
var play_s := 0.0   # real seconds walked this playthrough (Game accumulates)

func save_path() -> String:
	return _save_dir.path_join("slot_%d.json" % active_slot)

## The single-file era becomes slot 1.
func migrate_legacy_save() -> void:
	var legacy := _save_dir.path_join("vigil.json")
	var s1 := _save_dir.path_join("slot_1.json")
	if FileAccess.file_exists(legacy) and not FileAccess.file_exists(s1):
		DirAccess.rename_absolute(legacy, s1)

func any_slot() -> bool:
	for i in range(1, SLOTS + 1):
		if FileAccess.file_exists(_save_dir.path_join("slot_%d.json" % i)):
			return true
	return false

## null for an empty slot, else {slot, level, area, difficulty, play_s}.
func slot_summary(i: int):
	var path := _save_dir.path_join("slot_%d.json" % i)
	if not FileAccess.file_exists(path):
		return null
	var parsed = JSON.parse_string(FileAccess.open(path, FileAccess.READ).get_as_text())
	if not (parsed is Dictionary):
		return null
	var m: Dictionary = parsed.get("meta", {})
	return {
		"slot": i,
		"level": int(m.get("level", parsed.get("player", {}).get("level", 1))),
		"area": String(m.get("area", parsed.get("last_vigil", {}).get("area", ""))),
		"difficulty": String(m.get("difficulty", parsed.get("flags", {}).get("difficulty", "vigil"))),
		"play_s": float(m.get("play_s", 0.0)),
	}

func delete_slot(i: int) -> void:
	var path := _save_dir.path_join("slot_%d.json" % i)
	if FileAccess.file_exists(path):
		DirAccess.remove_absolute(path)

func save_game() -> void:
	# a save is the whole truth: refresh the pilgrim's ledger before writing.
	# Without this, a pickup-triggered save pairs its new world flags
	# (took_...) with a player snapshotted at some earlier rest — quit and
	# continue would then find the cache consumed AND the item gone.
	if Game.player != null and is_instance_valid(Game.player):
		Game.snapshot_player()
	DirAccess.make_dir_recursive_absolute(_save_dir)
	var data := {
		"version": 1,
		"areas": areas,
		"flags": flags,
		"remembrance": remembrance,
		"last_vigil": last_vigil,
		"player": player_data,
		"play_s": play_s,
		"meta": {
			"level": int(player_data.get("level", 1)),
			"area": last_vigil.get("area", ""),
			"difficulty": str(flag_val("difficulty", "vigil")),
			"saved_at": Time.get_unix_time_from_system(),
			"play_s": play_s,
		},
	}
	var f := FileAccess.open(save_path(), FileAccess.WRITE)
	f.store_string(JSON.stringify(data, "\t"))

func has_save() -> bool:
	return FileAccess.file_exists(save_path())

func load_game() -> bool:
	if not has_save():
		return false
	var parsed = JSON.parse_string(FileAccess.open(save_path(), FileAccess.READ).get_as_text())
	if not (parsed is Dictionary):
		return false
	areas = {}
	# JSON round-trips ints as floats; normalize.
	for id in parsed.get("areas", {}):
		var a = parsed["areas"][id]
		areas[id] = {"state": int(a.get("state", 0)), "cleared": bool(a.get("cleared", false)), "flags": a.get("flags", {})}
	flags = parsed.get("flags", {})
	remembrance = parsed.get("remembrance", null)
	if remembrance != null:
		remembrance["amount"] = int(remembrance.get("amount", 0))
	last_vigil = parsed.get("last_vigil", {"area": "", "lantern": ""})
	player_data = parsed.get("player", {})
	play_s = float(parsed.get("play_s", 0.0))
	return true

func reset() -> void:
	play_s = 0.0
	areas = {}
	flags = {}
	remembrance = null
	last_vigil = {"area": "", "lantern": ""}
	player_data = {}
