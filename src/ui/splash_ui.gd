class_name SplashUI
extends CanvasLayer
## FIGGLEBOTTOM PRODUCTIONS PRESENTS — the house card. Plays on every
## startup before the difficulty rite or the load-in: black screen, the
## grinning patron fading slowly into view, the house name declaimed at
## full theatrical volume. Any key skips once it has had its moment.

signal finished

const FADE_IN := 3.4
const TOTAL := 5.6

var _t := 0.0
var _done := false
var _img: TextureRect
var _voice: AudioStreamPlayer

func _ready() -> void:
	layer = 40
	process_mode = Node.PROCESS_MODE_ALWAYS
	var root := Control.new()
	root.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(root)
	var black := ColorRect.new()
	black.set_anchors_preset(Control.PRESET_FULL_RECT)
	black.color = Color(0, 0, 0, 1)
	root.add_child(black)
	_img = TextureRect.new()
	_img.texture = load("res://assets/ui/figglebottom.png")
	_img.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	_img.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	_img.set_anchors_preset(Control.PRESET_FULL_RECT)
	_img.offset_top = 40
	_img.offset_bottom = -40
	_img.modulate = Color(1, 1, 1, 0)
	root.add_child(_img)
	_voice = AudioStreamPlayer.new()
	if ResourceLoader.exists("res://assets/audio/ui/figglebottom.mp3"):
		_voice.stream = load("res://assets/audio/ui/figglebottom.mp3")
		_voice.bus = "SFX"
		_voice.volume_db = 2.0
		add_child(_voice)
		_voice.play()

func _process(dt: float) -> void:
	_t += dt
	_img.modulate.a = clampf(_t / FADE_IN, 0.0, 1.0)
	if _t >= TOTAL:
		_finish()

func _input(event: InputEvent) -> void:
	if _t < 1.2 or _done or Shot._shot_path != "":
		return   # never skipped by harness captures or boot-noise events
	if event is InputEventKey and event.pressed and not event.is_echo():
		_finish()
		get_viewport().set_input_as_handled()
	elif event is InputEventMouseButton and event.pressed:
		_finish()
		get_viewport().set_input_as_handled()

func _finish() -> void:
	if _done:
		return
	_done = true
	var tw := create_tween()
	tw.tween_property(_img, "modulate:a", 0.0, 0.35)
	tw.tween_callback(func():
		finished.emit()
		queue_free())
