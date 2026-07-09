class_name CreditsUI
extends CanvasLayer
## The rolling credits, reached from Settings: a funeral-slow film crawl
## of the names, the bare troll face rising last of all; when it crests,
## it lunges forward to fill the screen, takes its blessing, and the
## shriek-and-flatulence finale plays the house out. Esc leaves any time.

const GOLD := Color(0.9, 0.78, 0.55)
const PARCHMENT := Color(0.82, 0.78, 0.68)
const ASH := Color(0.55, 0.52, 0.46)

const ROLL_SPEED := 90.0          # px/s — stately, not glacial
const FACE_STOP := 0.30           # the face's center rests at this height

var _reel: Control
var _face: TextureRect
var _zoom_face: TextureRect
var _audio: AudioStreamPlayer
var _music: AudioStreamPlayer
var _phase := "roll"              # roll -> zoom -> bless -> finale -> done
var _vp := Vector2(1920, 1080)

func _ready() -> void:
	layer = 40
	process_mode = Node.PROCESS_MODE_ALWAYS
	_vp = get_viewport().get_visible_rect().size
	var cover := ColorRect.new()
	cover.color = Color(0.004, 0.003, 0.006, 1.0)
	cover.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(cover)

	_reel = Control.new()
	_reel.size = Vector2(_vp.x, 0)
	add_child(_reel)
	var y := 0.0
	y = _line("VESPERGARD", 66, GOLD, y) + 36.0
	y = _line("— the vigil is over —", 20, ASH, y) + 210.0
	y = _line("conjured by", 20, ASH, y) + 8.0
	y = _line("CLAUDE", 48, PARCHMENT, y) + 210.0
	y = _line("of the house of", 20, ASH, y) + 8.0
	y = _line("ANTHROPIC", 48, PARCHMENT, y) + 210.0
	y = _line("on the engine of thought", 20, ASH, y) + 8.0
	y = _line("FABLE 5", 48, PARCHMENT, y) + 210.0
	y = _line("powered by the immortal", 20, ASH, y) + 8.0
	y = _line("FIGGLEBOTTOM MOJO", 48, GOLD, y) + 260.0
	_face = TextureRect.new()
	_face.texture = load("res://assets/ui/trollface.png")
	_face.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	_face.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT
	_face.size = Vector2(400, 539)
	_face.position = Vector2((_vp.x - 400.0) * 0.5, y)
	_reel.add_child(_face)
	_reel.position.y = _vp.y      # everything starts below the screen

	# the lunge target: the card blown up to cover the screen, crop biased
	# so the grin band fills the frame; the pivot pins the growth to where
	# the reel face came to rest
	_zoom_face = TextureRect.new()
	_zoom_face.texture = _face.texture
	_zoom_face.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	_zoom_face.stretch_mode = TextureRect.STRETCH_SCALE
	var cs := maxf(_vp.x / 920.0, _vp.y / 1240.0)
	var dsz := Vector2(920, 1240) * cs
	_zoom_face.size = dsz
	_zoom_face.position = Vector2((_vp.x - dsz.x) * 0.5, _vp.y * 0.5 - dsz.y * 0.52)
	_zoom_face.pivot_offset = Vector2(dsz.x * 0.5, _vp.y * FACE_STOP - _zoom_face.position.y)
	_zoom_face.visible = false
	add_child(_zoom_face)

	_audio = AudioStreamPlayer.new()
	_audio.bus = "Music"
	_audio.process_mode = Node.PROCESS_MODE_ALWAYS
	add_child(_audio)
	_music = AudioStreamPlayer.new()
	_music.bus = "Music"
	_music.process_mode = Node.PROCESS_MODE_ALWAYS
	_music.stream = load("res://assets/audio/ui/credits_epic.wav")
	add_child(_music)
	_music.play()

func _line(text: String, size: int, color: Color, y: float) -> float:
	var l := Label.new()
	var ls := LabelSettings.new()
	ls.font = load("res://assets/fonts/DejaVuSerif.ttf")
	ls.font_size = size
	ls.font_color = color
	ls.shadow_color = Color(0, 0, 0, 0.6)
	ls.shadow_offset = Vector2(1, 2)
	l.label_settings = ls
	l.text = text
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	l.position = Vector2(0, y)
	l.size = Vector2(_vp.x, size * 1.35)
	_reel.add_child(l)
	return y + size * 1.35

func _process(delta: float) -> void:
	if _phase != "roll":
		return
	_reel.position.y -= ROLL_SPEED * delta
	var face_cy := _reel.position.y + _face.position.y + _face.size.y * 0.5
	if face_cy <= _vp.y * FACE_STOP:
		_begin_zoom()

func _begin_zoom() -> void:
	_phase = "zoom"
	_music.stop()          # the epic cuts dead right before the lunge
	_zoom_face.visible = true
	_zoom_face.scale = Vector2(0.21, 0.21)
	_reel.visible = false
	var tw := create_tween()
	tw.set_pause_mode(Tween.TWEEN_PAUSE_PROCESS)
	tw.tween_property(_zoom_face, "scale", Vector2.ONE, 0.55) \
		.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
	tw.tween_callback(_bless)

func _bless() -> void:
	_phase = "bless"
	_audio.stream = load("res://assets/audio/ui/credits_bless.mp3")
	_audio.play()
	_audio.finished.connect(_finale, CONNECT_ONE_SHOT)

func _finale() -> void:
	if _phase != "bless":
		return
	_phase = "finale"
	_audio.stream = load("res://assets/audio/ui/credits_finale.mp3")
	_audio.play()
	_audio.finished.connect(close, CONNECT_ONE_SHOT)
	# the face leans in ever so slightly for the duration
	var tw := create_tween()
	tw.set_pause_mode(Tween.TWEEN_PAUSE_PROCESS)
	tw.tween_property(_zoom_face, "scale", Vector2(1.08, 1.08), 15.0)

func _input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel"):
		close()
		get_viewport().set_input_as_handled()

func close() -> void:
	if _phase == "done":
		return
	_phase = "done"
	_audio.stop()
	_music.stop()
	queue_free()
