extends Node
## AudioDirector — music/ambience per world state, one-shot SFX helpers.
## All streams are optional: missing files no-op so headless tests run silent.

var _music_a: AudioStreamPlayer
var _music_b: AudioStreamPlayer
var _ambience: AudioStreamPlayer
var _active_music := ""

func _ready() -> void:
	_music_a = AudioStreamPlayer.new(); _music_a.bus = "Music"; add_child(_music_a)
	_music_b = AudioStreamPlayer.new(); _music_b.bus = "Music"; add_child(_music_b)
	_ambience = AudioStreamPlayer.new(); _ambience.bus = "Ambience"; add_child(_ambience)

func _stream(path: String) -> AudioStream:
	if not ResourceLoader.exists(path):
		return null
	return load(path)

## Crossfade to a music track (by res path); pass "" to fade out.
func play_music(path: String, fade := 2.0) -> void:
	if _active_music == path:
		return
	_active_music = path
	var incoming := _music_b if _music_a.playing else _music_a
	var outgoing := _music_a if incoming == _music_b else _music_b
	var stream := _stream(path)
	if stream:
		incoming.stream = stream
		incoming.volume_db = -40.0
		incoming.play()
		create_tween().tween_property(incoming, "volume_db", 0.0, fade)
	if outgoing.playing:
		var t := create_tween()
		t.tween_property(outgoing, "volume_db", -40.0, fade)
		t.tween_callback(outgoing.stop)

func play_ambience(path: String, fade := 2.0) -> void:
	var stream := _stream(path)
	if stream == null:
		_ambience.stop()
		return
	_ambience.stream = stream
	_ambience.volume_db = -10.0
	if not _ambience.playing:
		_ambience.play()

## Fire-and-forget positional SFX.
func sfx_at(path: String, pos: Vector3, volume_db := 0.0, pitch := 1.0) -> void:
	var stream := _stream(path)
	if stream == null:
		return
	var p := AudioStreamPlayer3D.new()
	p.stream = stream
	p.bus = "SFX"
	p.volume_db = volume_db
	p.pitch_scale = pitch
	p.finished.connect(p.queue_free)
	get_tree().current_scene.add_child(p)
	p.global_position = pos
	p.play()

## Non-positional SFX (UI, stingers).
func sfx(path: String, volume_db := 0.0, pitch := 1.0, bus := "SFX") -> void:
	var stream := _stream(path)
	if stream == null:
		return
	var p := AudioStreamPlayer.new()
	p.stream = stream
	p.bus = bus
	p.volume_db = volume_db
	p.pitch_scale = pitch
	p.finished.connect(p.queue_free)
	add_child(p)
	p.play()
