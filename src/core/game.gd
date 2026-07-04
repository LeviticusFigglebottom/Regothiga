extends Node
## Game — run orchestrator: knows the player, the current area, and drives
## high-level flows (death, respawn, vigils). Scene-facing counterpart to World.

signal orisons_changed(amount: int)
signal player_registered(player)

var player: Node = null
var current_area: Node = null
var current_area_id := ""

var orisons := 0

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

signal vigil_kept(lantern)

## The rest ceremony: kneel, heal, respawn the dead, and turn the world.
## D-009 rules: uncleared+glory -> gutter (committed); uncleared+ruin -> rest
## only; cleared -> free toggle.
func vigil_flow(lantern: VigilLantern, p) -> void:
	if StateDirector.transitioning:
		return
	var area := lantern.area if lantern.area != null else current_area
	var aid: String = area.area_id if area != null else current_area_id
	var cur := World.get_area_state(aid)
	var target := cur
	if World.is_cleared(aid):
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
		World.player_data = p.to_save()
	World.save_game()
	vigil_kept.emit(lantern)
	if p != null:
		p.exit_rest()
		p.lock_control(false)
