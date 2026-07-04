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

func _ready() -> void:
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
	if _shot_path != "" and _frames_left < 0:
		_frames_left = 30

func _process(_d: float) -> void:
	if _quit_after > 0:
		_quit_after -= 1
		if _quit_after == 0:
			get_tree().quit()
	if _shot_path == "" or _frames_left < 0:
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
