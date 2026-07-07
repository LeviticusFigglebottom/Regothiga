extends Node
## Shot — headless screenshot + scripted-run harness.
## User args (after `--` on the command line):
##   --shot=PATH            capture viewport to PATH then quit
##   --shot-frames=N        frames to wait before capture (default 30)
##   --shot-cam=x,y,z,yaw_deg,pitch_deg[,fov]   spawn a free camera for the shot
##   --state=glory|ruin     force initial world state for the loaded area
##   --quit-after=N         quit after N frames (no capture)

var _shot_path := ""
var _frames_left := -1
var _quit_after := -1
var _cam_spec := ""
var forced_state := ""   # read by boot/world setup
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
		elif arg.begins_with("--state="):
			forced_state = arg.get_slice("=", 1)
		elif arg.begins_with("--quit-after="):
			_quit_after = int(arg.get_slice("=", 1))
		elif arg.begins_with("--vigil-frame="):
			_vigil_frame = int(arg.get_slice("=", 1))
		elif arg.begins_with("--shot-seq="):
			for part in arg.get_slice("=", 1).split(","):
				_seq.append(float(part))
	if _shot_path != "" and _frames_left < 0:
		_frames_left = 30

func _process(_d: float) -> void:
	if _quit_after > 0:
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
	if _frames_left == 10 and _cam_spec != "":
		_spawn_cam()
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
