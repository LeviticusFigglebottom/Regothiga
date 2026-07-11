extends Node3D
## The Larkwarden's amend, done with living hands: down in the ruin, where
## the cages truly stand, every door he shut is opened. Each freeing lets a
## last remembered lark climb out of the dark and go to the light it was
## raised for. All doors opened -> "amend_larks".
##   {"script": ".../amend_larks.gd", "at": [0,0,0], "tag": "ruin",
##    "require_flag": "amend_lark_asked",
##    "params": {"flag": "amend_larks", "cages": [[0.8,9.59,-2], ...]}}

var flag := "amend_larks"
var cages: Array = []

var _opened: Array = []

func _ready() -> void:
	if World.flag(flag):
		return
	for i in cages.size():
		var at: Array = cages[i]
		var z := Interactable.new()
		z.prompt = "Open the cage"
		z.setup_zone(1.5, 1.6)
		var idx := i
		z.activated.connect(func(_p): _free(idx, z))
		add_child(z)
		z.position = Vector3(at[0], at[1], at[2]) - position
		_opened.append(false)

func _free(i: int, zone: Interactable) -> void:
	if _opened[i] or World.flag(flag):
		return
	_opened[i] = true
	zone.enabled = false
	var at := zone.global_position
	AudioDirector.sfx_at("res://assets/audio/lark_trill.wav", at, -4.0,
			randf_range(0.95, 1.15))
	_bird(at)
	var freed := 0
	for v in _opened:
		if v:
			freed += 1
	if freed >= _opened.size():
		World.set_flag(flag)
		World.save_game()
		Game.toast.emit("The last cage stands open. Somewhere above, a warden hears the quiet.")
		AudioDirector.sfx("res://assets/audio/swell_kindle.wav", -4.0, 1.2)
	else:
		Game.toast.emit("%d of %d cages opened." % [freed, _opened.size()])

## a remembered lark: a scrap of gold that climbs, sings, and is gone
func _bird(at: Vector3) -> void:
	var bird := Node3D.new()
	get_parent().add_child(bird)
	bird.global_position = at + Vector3(0, 0.4, 0)
	var mat := StandardMaterial3D.new()
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mat.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	mat.albedo_color = Color(1.0, 0.9, 0.55, 0.95)
	var body := MeshInstance3D.new()
	var bm := PrismMesh.new()
	bm.size = Vector3(0.12, 0.08, 0.22)
	bm.material = mat
	body.mesh = bm
	body.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	bird.add_child(body)
	for s in [-1.0, 1.0]:
		var wing := MeshInstance3D.new()
		var wm := PrismMesh.new()
		wm.size = Vector3(0.22, 0.02, 0.12)
		wm.material = mat
		wing.mesh = wm
		wing.position = Vector3(s * 0.14, 0.02, 0)
		wing.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		bird.add_child(wing)
	var l := OmniLight3D.new()
	l.light_color = Color(1.0, 0.9, 0.6)
	l.light_energy = 1.0
	l.omni_range = 2.6
	l.shadow_enabled = false
	bird.add_child(l)
	# up and away, banking as it goes, gone into its own light
	var up := at + Vector3(randf_range(-1.4, 1.4), 7.0 + randf() * 3.0, randf_range(-1.4, 1.4))
	var tw := bird.create_tween()
	tw.set_parallel(true)
	tw.tween_property(bird, "global_position", up, 2.2) \
		.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
	tw.tween_property(bird, "rotation:y", randf_range(-2.0, 2.0), 2.2)
	tw.tween_property(mat, "albedo_color:a", 0.0, 2.2).set_delay(0.6)
	tw.chain().tween_callback(bird.queue_free)
