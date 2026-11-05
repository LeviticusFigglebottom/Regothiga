extends Node
## Shot — headless screenshot + scripted-run harness.
## User args (after `--` on the command line):
##   --shot=PATH            capture viewport to PATH then quit
##   --shot-frames=N        frames to wait before capture (default 30)
##   --shot-cam=x,y,z,yaw_deg,pitch_deg[,fov]   spawn a free camera for the shot
##   --state=glory|ruin     force initial world state for the loaded area
##   --shot-satchel         populate sample gear/relics and open InventoryUI
##   --quit-after=N         quit after N frames (no capture)

var _shot_path := ""
var _frames_left := -1
var _quit_after := -1
var _cam_spec := ""
var _open_satchel := false
var _trigger_flask := false
var forced_state := ""   # read by boot/world setup
var forced_flags: Array = []   # world flags applied before the area builds
var _vigil_frame := -1
var _seq: Array = []      # seconds after the vigil trigger
var _seq_t := -1.0
var _seq_i := 0

func _ready() -> void:
	# the shot harness must keep ticking while the tree is paused (e.g. to
	# photograph the pause menu itself)
	process_mode = Node.PROCESS_MODE_ALWAYS
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--shot="):
			_shot_path = arg.get_slice("=", 1)
		elif arg.begins_with("--shot-frames="):
			_frames_left = int(arg.get_slice("=", 1))
		elif arg.begins_with("--shot-cam="):
			_cam_spec = arg.get_slice("=", 1)
		elif arg == "--shot-satchel":
			_open_satchel = true
		elif arg == "--shot-flask":
			_trigger_flask = true
		elif arg.begins_with("--state="):
			forced_state = arg.get_slice("=", 1)
		elif arg.begins_with("--flag="):
			forced_flags.append(arg.get_slice("=", 1))
		elif arg.begins_with("--quit-after="):
			_quit_after = int(arg.get_slice("=", 1))
		elif arg.begins_with("--vigil-frame="):
			_vigil_frame = int(arg.get_slice("=", 1))
		elif arg.begins_with("--shot-seq="):
			for part in arg.get_slice("=", 1).split(","):
				_seq.append(float(part))
		elif arg == "--shot-seq-now":
			_seq_t = 0.0   # sequence clock runs from boot (filming the intro)
	if _shot_path != "" and _frames_left < 0:
		_frames_left = 30

func _process(_d: float) -> void:
	if _quit_after > 0:
		if _quit_after == 2:
			AudioDirector.shutdown()
		_quit_after -= 1
		if _quit_after == 0:
			get_tree().quit()
	if _vigil_frame > 0:
		_vigil_frame -= 1
		if _vigil_frame == 0:
			_trigger_vigil()
	if _seq_t >= 0.0 and _seq_i < _seq.size():
		_seq_t += get_process_delta_time()
		if _seq_t >= float(_seq[_seq_i]):
			var img := get_viewport().get_texture().get_image()
			var p := _shot_path.get_basename() + "_%d.png" % _seq_i
			DirAccess.make_dir_recursive_absolute(p.get_base_dir())
			img.save_png(p)
			print("[shot] saved ", p)
			_seq_i += 1
			if _seq_i >= _seq.size():
				get_tree().quit()
	if _shot_path == "" or _frames_left < 0 or not _seq.is_empty():
		return
	if _cam_spec != "" and not _trigger_flask and Game.player != null and Game.player.hurtbox != null:
		Game.player.hurtbox.monitorable = false
		Game.player.hurtbox.monitoring = false
	if _frames_left == 12 and _open_satchel and Game.player != null:
		for wid in ["marsh_spear", "pilgrim_greatsword", "sexton_maul", "ward_halberd", "lark_bow"]:
			Game.player.give_item(wid, 1)
		for rid in ["candleglass", "sun_creed_charm", "tallow_heart", "choir_seal", "radiant_token"]:
			Game.player.inventory[rid] = 1
		Game.player.set_hotbar_slot(1, "sexton_maul")
		Game.player.set_hotbar_slot(2, "ward_halberd")
		Game.player.set_hotbar_slot(3, "pilgrim_greatsword")
		InventoryUI.open_for(Game.player)
	if _frames_left == 120 and _trigger_flask and Game.player != null:
		Game.player.global_position = Vector3(0.0, 0.2, 3.2)
		Game.player.velocity = Vector3.ZERO
		Game.player.hp = Game.player.max_hp * 0.55
		Game.player.health_changed.emit(Game.player.hp, Game.player.max_hp)
		Game.player.vis.rotation.y = PI
		Game.player.try_flask()
		if _cam_spec == "":
			var ppos: Vector3 = Game.player.global_position
			_cam_spec = "%.2f,%.2f,%.2f,-8,-6,42" % [ppos.x - 0.28, ppos.y + 1.38, ppos.z + 2.25]
			_spawn_cam()
	if _trigger_flask and Game.player != null and Game.player.state == Player.S.FLASK and Game.player.state_t >= 0.76:
		_frames_left = min(_frames_left, 2)
	if _frames_left == 10 and _cam_spec != "":
		_spawn_cam()
	if _frames_left == 2:
		AudioDirector.shutdown()
	_frames_left -= 1
	if _frames_left == 0:
		var img := get_viewport().get_texture().get_image()
		var dir := _shot_path.get_base_dir()
		if dir != "" and not DirAccess.dir_exists_absolute(dir):
			DirAccess.make_dir_recursive_absolute(dir)
		img.save_png(_shot_path)
		print("[shot] saved ", _shot_path)
		get_tree().quit()

func _spawn_cam() -> void:
	var parts := _cam_spec.split(",")
	if parts.size() < 5:
		return
	var cam := Camera3D.new()
	cam.name = "ShotCam"
	get_tree().current_scene.add_child(cam)
	cam.global_position = Vector3(float(parts[0]), float(parts[1]), float(parts[2]))
	cam.rotation_degrees = Vector3(float(parts[4]), float(parts[3]), 0.0)
	if parts.size() >= 6:
		cam.fov = float(parts[5])
	cam.current = true

func _trigger_vigil() -> void:
	var lantern = Game.find_lantern("garth")
	if lantern == null or Game.player == null:
		push_warning("Shot: no lantern/player for vigil capture")
		return
	Game.player.global_position = lantern.respawn_point()
	Game.player.vis.rotation.y = PI
	Game.vigil_flow(lantern, Game.player)
	_seq_t = 0.0

func _exit_tree() -> void:
	AmbientLife._mote_tex = null
	SummonGlyph._sign_shader = null
	EnvRig.active_instance = null
