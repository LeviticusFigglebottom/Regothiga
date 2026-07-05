extends TestBase
func _ready() -> void:
	_run.call_deferred()
func _run() -> void:
	World.reset()
	var area := AreaBuilder.build("basilica_porch")
	add_child(area)
	Game.register_area(area, "basilica_porch")
	StateDirector.snap(area, VG.WState.GLORY)
	await ticks(25)
	var space := area.get_world_3d().direct_space_state
	for probe in [Vector3(2, -2.4, 12.4), Vector3(2, -1.2, 10.2), Vector3(2, -0.1, 8.3)]:
		var q := PhysicsShapeQueryParameters3D.new()
		var s := SphereShape3D.new()
		s.radius = 0.25
		q.shape = s
		q.transform = Transform3D(Basis(), probe)
		q.collision_mask = 0x7FFFFFFF
		var names := []
		for hit in space.intersect_shape(q, 8):
			var col: Node3D = hit["collider"]
			names.append("%s@%s" % [col.get_parent().name, str(col.global_position.snapped(Vector3(0.1,0.1,0.1)))])
		print("probe ", probe, " -> ", names)
	# where is the ramp body?
	var stack: Array[Node] = [area]
	while not stack.is_empty():
		var n: Node = stack.pop_back()
		if n is CollisionShape3D and (n as CollisionShape3D).shape is BoxShape3D:
			var b := (n as CollisionShape3D).shape as BoxShape3D
			if absf(b.size.z - 5.15) < 0.01:
				print("RAMP shape gpos=", (n as Node3D).global_position.snapped(Vector3(0.01,0.01,0.01)),
					" grot=", (n as Node3D).global_rotation_degrees.snapped(Vector3(0.1,0.1,0.1)),
					" layer=", (n.get_parent() as CollisionObject3D).collision_layer)
		for c in n.get_children():
			stack.append(c)
	finish()
