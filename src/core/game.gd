extends Node
## Game — run orchestrator: knows the player, the current area, and drives
## high-level flows (death, respawn, vigils). Scene-facing counterpart to World.

signal orisons_changed(amount: int)
signal player_registered(player)
signal player_forgotten                  # death splash
signal player_respawned
signal remembrance_reclaimed(amount: int)
signal toast(text: String)               # short diegetic messages
signal lore_panel(text: String)          # plaque/lore reading
signal area_cleared(area_id: String)

var player: Node = null
var current_area: Node = null
var current_area_id := ""

var orisons := 0
var _death_flow_running := false

func _ready() -> void:
	player_registered.connect(func(p): p.died.connect(_on_player_died))

func _on_player_died() -> void:
	if _death_flow_running:
		return
	_death_flow_running = true
	player_forgotten.emit()
	# the drop: all carried orisons stay at the death site (replacing any
	# previous remembrance — that one is lost forever)
	if orisons > 0:
		World.set_remembrance(current_area_id, player.global_position, orisons)
	set_orisons(0)
	World.save_game()
	await get_tree().create_timer(float(DB.tuning("death/respawn_delay", 2.8)), false).timeout
	respawn_player()
	_death_flow_running = false

func respawn_player() -> void:
	# return to the last vigil kept
	var pos: Vector3 = player.global_position
	var lantern := find_lantern(World.last_vigil.get("lantern", ""))
	if lantern != null:
		pos = lantern.respawn_point()
	elif current_area != null and current_area.has_method("default_spawn"):
		pos = current_area.default_spawn()
	get_tree().call_group(VG.GROUP_RESPAWN_ON_REST, "respawn")
	player.revive_at(pos)
	refresh_remembrance()
	# dying mid-boss-fight left the boss theme looping forever; the world
	# music (and the ducked ambience) belongs to the area's state again
	if current_area != null:
		AudioDirector.end_boss_theme(current_area.env.music_for(World.get_area_state(current_area_id)), 2.5)
	player_respawned.emit()

## A warden has been put to rest: the area opens for free kindling.
func on_boss_slain(area_id: String) -> void:
	World.set_cleared(area_id)
	World.save_game()
	AudioDirector.play_music("", 2.0)
	AudioDirector.duck_ambience(false)
	toast.emit("The warden rests. The memory is yours to keep or quench.")
	area_cleared.emit(area_id)
	await get_tree().create_timer(2.0, false).timeout
	if current_area != null and current_area.area_id == area_id:
		AudioDirector.play_music(current_area.env.music_for(World.get_area_state(area_id)), 4.0)

func snapshot_player() -> void:
	if player == null:
		return
	World.player_data = player.to_save()
	World.player_data["orisons"] = orisons

func find_lantern(lantern_id: String) -> VigilLantern:
	for l in get_tree().get_nodes_in_group("lanterns"):
		if l.lantern_id == lantern_id:
			return l
	return null

## (Re)spawn the remembrance pickup for the current area from world data.
var _remembrance_node: Remembrance = null
func refresh_remembrance() -> void:
	if _remembrance_node != null and is_instance_valid(_remembrance_node):
		_remembrance_node.queue_free()
		_remembrance_node = null
	if World.remembrance == null or current_area == null:
		return
	if World.remembrance.get("area", "") != current_area_id:
		return
	_remembrance_node = Remembrance.new()
	_remembrance_node.amount = int(World.remembrance.get("amount", 0))
	current_area.add_child(_remembrance_node)
	_remembrance_node.global_position = World.remembrance_pos()

func register_player(p: Node) -> void:
	player = p
	player_registered.emit(p)

func register_area(area: Node, id: String) -> void:
	current_area = area
	current_area_id = id

func add_orisons(n: int) -> void:
	orisons = max(0, orisons + n)
	orisons_changed.emit(orisons)

func set_orisons(n: int) -> void:
	orisons = max(0, n)
	orisons_changed.emit(orisons)

func area_state() -> VG.WState:
	return World.get_area_state(current_area_id)

var world_root: Node3D = null   # container that owns the current area

## Cross an AreaPortal: unload the region behind, build the one ahead.
## spawn_yaw (deg) turns the camera to face into the new room — arriving
## through a door should never leave you staring back at the wall you left.
func travel_to(area_id: String, spawn_pos: Vector3, spawn_yaw := 1e9) -> void:
	if world_root == null or player == null:
		return
	player.lock_control(true)
	var old := current_area
	var next := AreaBuilder.build(area_id)
	world_root.add_child(next)
	register_area(next, area_id)
	if old != null:
		old.queue_free()
	# entering an unvisited area finds it in glory (D-009)
	StateDirector.snap(next, World.get_area_state(area_id))
	player.global_position = spawn_pos
	player.velocity = Vector3.ZERO
	if abs(spawn_yaw) < 720.0:
		player.cam.yaw = deg_to_rad(spawn_yaw)
	refresh_remembrance()
	snapshot_player()
	World.save_game()
	toast.emit(next.display_name)
	player.lock_control(false)

signal vigil_kept(lantern)

## Sanctuary quarters (no warden to put down) may turn their memory freely:
## the area def opts in with "free_kindle": true. Everywhere else, the toggle
## is earned by clearing the warden (D-009).
## The weight of the dark, chosen when a pilgrimage begins.
## kindled: deal 1.25x, take 0.75x | vigil: as remembered | guttered:
## deal 0.75x, take 1.25x. Persisted in World.flags with the save.
const DIFF := {
	"kindled": {"out": 1.25, "in": 0.75},
	"vigil": {"out": 1.0, "in": 1.0},
	"guttered": {"out": 0.75, "in": 1.25},
}
var difficulty := "vigil"

func set_difficulty(id: String) -> void:
	difficulty = id if DIFF.has(id) else "vigil"
	World.set_flag("difficulty", difficulty)

func dmg_out_mult() -> float:
	return DIFF[difficulty]["out"]

func dmg_in_mult() -> float:
	return DIFF[difficulty]["in"]

func toggle_free(aid: String) -> bool:
	return World.is_cleared(aid) or bool(DB.area_def(aid).get("free_kindle", false))

## The rest ceremony: kneel, heal, respawn the dead, and turn the world.
## D-009 rules: uncleared+glory -> gutter (committed); uncleared+ruin -> rest
## only; cleared -> free choice (RestUI passes "toggle" or "rest_only").
func vigil_flow(lantern: VigilLantern, p, choice := "auto") -> void:
	if StateDirector.transitioning:
		return
	var area := lantern.area if lantern.area != null else current_area
	var aid: String = area.area_id if area != null else current_area_id
	var cur := World.get_area_state(aid)
	var target := cur
	match choice:
		"toggle":
			target = VG.WState.GLORY if cur == VG.WState.RUIN else VG.WState.RUIN
		"rest_only":
			target = cur
		_:
			if toggle_free(aid):
				target = VG.WState.GLORY if cur == VG.WState.RUIN else VG.WState.RUIN
			elif cur == VG.WState.GLORY:
				target = VG.WState.RUIN

	World.last_vigil = {"area": aid, "lantern": lantern.lantern_id}
	World.set_area_flag(aid, "lit_" + lantern.lantern_id)

	if p != null:
		p.lock_control(true)
		p.enter_rest()
	AudioDirector.sfx("res://assets/audio/rest_chime.wav", -4.0)

	# the dead return as the world turns
	get_tree().call_group(VG.GROUP_RESPAWN_ON_REST, "respawn")

	if target != cur and area != null:
		await get_tree().create_timer(1.3).timeout   # kneel beat first
		await StateDirector.transition(area, target, lantern.global_position)
	else:
		await get_tree().create_timer(1.6).timeout

	if p != null:
		p.heal_full()
		snapshot_player()
	World.save_game()
	vigil_kept.emit(lantern)
	if p != null:
		p.exit_rest()
		p.lock_control(false)
