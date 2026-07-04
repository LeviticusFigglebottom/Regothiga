extends Node
## StateDirector — owns the glory↔ruin transformation: the wave, the
## environment/light lerp, layer swaps, navmesh switching, and population
## changes. The rest of the game only calls `transition()` or `snap()`.

signal transition_started(area_id: String, to_state: VG.WState)
signal transition_finished(area_id: String, to_state: VG.WState)

var transitioning := false

## Instant state application (used at area load / for tools). No spectacle.
func snap(area: Node, to_state: VG.WState) -> void:
	if area == null:
		return
	RenderingServer.global_shader_parameter_set("vg_state_blend", 1.0 if to_state == VG.WState.RUIN else 0.0)
	RenderingServer.global_shader_parameter_set("vg_wave_r", -1000.0)
	if area.has_method("apply_state"):
		area.apply_state(to_state)
	World.set_area_state(area.area_id, to_state)

## The spectacle. Sweeps a wave from `origin`, morphing the world.
func transition(area: Node, to_state: VG.WState, origin: Vector3) -> void:
	if transitioning or area == null:
		return
	transitioning = true
	transition_started.emit(area.area_id, to_state)
	# Placeholder v0: brief pause then snap. Replaced by the wave in the
	# state-system milestone — see ROADMAP.
	await get_tree().create_timer(0.5).timeout
	snap(area, to_state)
	transitioning = false
	transition_finished.emit(area.area_id, to_state)
