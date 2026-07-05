class_name AreaBuilder
## Compiles data/areas/<id>.json into a live Area (DECISIONS D-007).
## Constructs: pieces, rows, fills, vault fields, props, and the entity
## lists (lanterns, gates, fog gates, spawners, npcs, plaques, pickups,
## portals, cameos). Everything carries a state tag: base | glory | ruin.

static func build(area_id: String) -> Area:
	var def := DB.area_def(area_id)
	if def.is_empty():
		push_error("AreaBuilder: no def for area '%s'" % area_id)
		return null
	var area := Area.new()
	area.area_id = area_id
	area.name = "Area_" + area_id
	area.display_name = def.get("name", area_id)
	area.set_meta("def", def)

	for spec in def.get("fills", []):
		_fill(area, spec)
	for spec in def.get("rows", []):
		_row(area, spec)
	for spec in def.get("pieces", []):
		_piece(area, spec, true)
	for spec in def.get("props", []):
		_piece(area, spec, _prop_collides(spec))
	for spec in def.get("skyline", []):
		var sk: Dictionary = spec.duplicate()
		sk["flames"] = false
		sk["collide"] = false
		_piece(area, sk, false)
	for spec in def.get("vault_fields", []):
		_vault_field(area, spec)
	for spec in def.get("blockers", []):
		_blocker(area, spec)

	for spec in def.get("lanterns", []):
		var l := VigilLantern.new()
		l.lantern_id = spec.get("id", "lantern")
		l.display_name = spec.get("name", "Vigil Lantern")
		l.area = area
		area.base.add_child(l)
		_place(l, spec)
	for spec in def.get("gates", []):
		var g := ShortcutGate.new()
		g.gate_id = spec.get("id", "gate")
		g.area_id = area_id
		g.locked_prompt = spec.get("locked_prompt", "Barred from the other side")
		area.base.add_child(g)
		_place(g, spec)
	for spec in def.get("spawners", []):
		var s := Spawner.new()
		s.enemy_id = spec.get("enemy", "penitent")
		s.face_deg = float(spec.get("face", 0))
		s.dead_once = spec.get("dead_once", false)
		s.spawn_flag = "slain_" + spec.get("id", spec.get("enemy", "e"))
		s.area_id = area_id
		var tag: String = spec.get("tag", "ruin")
		area.attach(s, tag)
		_place(s, spec)
		if spec.has("fog_gate_id"):
			s.set_meta("fog_gate_id", spec["fog_gate_id"])
	for spec in def.get("fog_gates", []):
		var f := FogGate.new()
		f.gate_id = spec.get("id", "fog")
		f.area_id = area_id
		area.attach(f, spec.get("tag", "ruin"))
		_place(f, spec)
		# bind its boss spawner
		for s in _all_spawners(area):
			if String(s.get_meta("fog_gate_id", "")) == f.gate_id:
				f.boss_spawner = s
	for spec in def.get("npcs", []):
		var n := NPC.new()
		n.npc_id = spec.get("id", "aveline")
		n.set_meta("state_tag", spec.get("tag", "glory"))
		area.attach(n, spec.get("tag", "glory"))
		_place(n, spec)
	for spec in def.get("plaques", []):
		var p := LorePlaque.new()
		p.text = spec.get("text", "…")
		area.attach(p, spec.get("tag", "base"))
		_place(p, spec)
	for spec in def.get("pickups", []):
		var k := Pickup.new()
		k.pickup_id = spec.get("id", "pickup")
		k.area_id = area_id
		k.orisons = int(spec.get("orisons", 0))
		k.item_id = spec.get("item", "")
		k.item_count = int(spec.get("count", 1))
		k.label = spec.get("label", "Take")
		area.attach(k, spec.get("tag", "base"))
		_place(k, spec)
	for spec in def.get("cameos", []):
		var c := BellkeeperCameo.new()
		area.attach(c, spec.get("tag", "glory"))
		_place(c, spec)
	for spec in def.get("chime_puzzles", []):
		var ch := ChimePuzzle.new()
		area.attach(ch, spec.get("tag", "base"))
		ch.setup(spec)
	for spec in def.get("votive_locks", []):
		var vl := VotiveLock.new()
		area.attach(vl, spec.get("tag", "glory"))
		vl.setup(spec)
	for spec in def.get("watcher_puzzles", []):
		var wp := WatcherPuzzle.new()
		area.attach(wp, spec.get("tag", "base"))
		wp.setup(spec)
	for spec in def.get("flag_gates", []):
		var fgate := FlagGate.new()
		var gtag: String = spec.get("tag", "base")
		area.attach(fgate, gtag)
		_place(fgate, spec)
		fgate.setup(spec, _tag_bit(gtag))
	for spec in def.get("portals", []):
		var pt := AreaPortal.new()
		pt.to_area = spec.get("to", "")
		pt.spawn_pos = _v3(spec.get("spawn", [0, 0, 0]))
		pt.prompt = spec.get("prompt", "Pass on")
		pt.locked_flag = spec.get("locked_flag", "")
		pt.locked_prompt = spec.get("locked_prompt", "Sealed")
		area.attach(pt, spec.get("tag", "base"))
		_place(pt, spec)

	# ambient mood: gold motes in glory, ash in ruin, sized to the area
	var ext := _extent(def)
	area.add_ambient(ext[0], ext[1])

	area.bake_navmeshes.call_deferred()
	return area

static func _extent(def: Dictionary) -> Array:
	var mn := Vector3(1e9, 0, 1e9)
	var mx := Vector3(-1e9, 0, -1e9)
	for spec in def.get("fills", []):
		var a := _v3(spec["min"])
		var b := _v3(spec["max"])
		mn.x = minf(mn.x, a.x); mn.z = minf(mn.z, a.z)
		mx.x = maxf(mx.x, b.x); mx.z = maxf(mx.z, b.z)
	if mn.x > mx.x:
		mn = Vector3(-20, 0, -20); mx = Vector3(20, 0, 20)
	return [mn, mx]

static func _v3(a) -> Vector3:
	return Vector3(a[0], a[1], a[2]) if a is Array and a.size() >= 3 else Vector3.ZERO

static func _place(n: Node3D, spec: Dictionary) -> void:
	n.position = _v3(spec.get("at", [0, 0, 0]))
	n.rotation.y = deg_to_rad(float(spec.get("rot", 0)))

static func _tag_bit(tag: String) -> int:
	match tag:
		"glory": return VG.L_WORLD_GLORY
		"ruin": return VG.L_WORLD_RUIN
	return VG.L_WORLD_BASE

## Solid furniture blocks; cloth, hangings, wall dressing and ankle-high
## clutter stay passable. Explicit "collide" in the spec always wins.
const PASSABLE_PROPS := ["banner", "banner_torn", "ivy_sheet_a", "ivy_sheet_b",
	"censer_hanging", "censer_fallen", "sconce_torch", "glass_lancet",
	"glass_lancet_broken", "candle_cluster", "candle_cluster_dead",
	"book_stack", "scroll_pile", "rubble_s", "mosaic_medallion"]

static func _prop_collides(spec: Dictionary) -> bool:
	if spec.has("collide"):
		return bool(spec["collide"])
	return not (String(spec.get("kit", "")) in PASSABLE_PROPS)

static func _piece(area: Area, spec: Dictionary, collide: bool) -> Node3D:
	var tag: String = spec.get("tag", "base")
	var mode := 1 if tag == "glory" else (2 if tag == "ruin" else 0)
	var piece := KitLib.instance(spec["kit"], mode)
	_place(piece, spec)
	if spec.has("scale"):
		var sc = spec["scale"]
		piece.scale = _v3(sc) if sc is Array else Vector3.ONE * float(sc)
	if collide and spec.get("collide", true):
		if String(spec["kit"]) == "stair_grand_4m":
			_stair_ramp(piece, tag)   # ramp-only: step trimesh would wall off the climb
		else:
			KitLib.add_collision(piece, _tag_bit(tag))
	if spec.get("flames", true) and (tag != "ruin"):
		KitLib.add_flame_lights(piece)
	area.attach(piece, tag)
	return piece

## Grand stairs collide as a smooth 31-degree ramp (plus solid flank boxes),
## never as step trimesh: 0.24 m step faces are walls to move_and_slide, so
## the climb direction would be impassable. The ramp surface runs from the
## top edge (local origin) to the floor 0.2 below the stair base, meeting
## walkable ground flush at both ends.
static func _stair_ramp(piece: Node3D, tag: String) -> void:
	var body := StaticBody3D.new()
	body.collision_layer = 1 << (_tag_bit(tag) - 1)
	body.collision_mask = 0
	var cs := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = Vector3(3.9, 0.3, 5.15)
	cs.shape = box
	cs.rotation_degrees = Vector3(-30.96, 0, 0)   # rise 2.4 over run 4.0
	cs.position = Vector3(0, -1.45, -2.12)
	body.add_child(cs)
	for sx in [-2.17, 2.17]:
		var fs := CollisionShape3D.new()
		var fb := BoxShape3D.new()
		fb.size = Vector3(0.36, 2.85, 4.4)
		fs.shape = fb
		fs.position = Vector3(sx, -1.02, -2.02)
		body.add_child(fs)
	piece.add_child(body)

static func _row(area: Area, spec: Dictionary) -> void:
	var from := _v3(spec.get("from", [0, 0, 0]))
	var dir := _v3(spec.get("dir", [1, 0, 0]))
	var count := int(spec.get("count", 1))
	var step := float(spec.get("step", 4.0))
	# JSON numbers arrive as floats; Array.has() is type-strict, so an int
	# loop index never matches [1.0] — normalize to ints
	var skip := {}
	for s in spec.get("skip", []):
		skip[int(s)] = true
	for i in count:
		if skip.has(i):
			continue
		var sub := spec.duplicate()
		sub["at"] = [from.x + dir.x * step * i, from.y, from.z + dir.z * step * i]
		_piece(area, sub, spec.get("collide", true))

static func _fill(area: Area, spec: Dictionary) -> void:
	var mn := _v3(spec.get("min", [0, 0, 0]))
	var mx := _v3(spec.get("max", [4, 0, 4]))
	var step := float(spec.get("step", 4.0))
	var x := mn.x
	while x < mx.x - 0.01:
		var z := mn.z
		while z < mx.z - 0.01:
			var sub := spec.duplicate()
			sub["at"] = [x + step * 0.5, mn.y, z + step * 0.5]
			_piece(area, sub, spec.get("collide", true))
			z += step
		x += step

static func _vault_field(area: Area, spec: Dictionary) -> void:
	var sub := spec.duplicate()
	sub["kit"] = "vault_bay_4x4"
	sub["min"] = spec["min"]
	sub["max"] = spec["max"]
	var mn := _v3(spec.get("min", [0, 0, 0]))
	var mx := _v3(spec.get("max", [4, 0, 4]))
	var spring := float(spec.get("spring", 2.7))
	var x := mn.x
	while x < mx.x - 0.01:
		var z := mn.z
		while z < mx.z - 0.01:
			var p := spec.duplicate()
			p["kit"] = "vault_bay_4x4"
			p["at"] = [x + 2.0, spring, z + 2.0]
			p["collide"] = false      # ceilings don't need trimesh for gameplay
			_piece(area, p, false)
			z += 4.0
		x += 4.0

## Invisible impassable volume (collapsed debris etc.) — dress it with props.
static func _blocker(area: Area, spec: Dictionary) -> void:
	var tag: String = spec.get("tag", "base")
	var mn := _v3(spec["min"])
	var mx := _v3(spec["max"])
	var body := StaticBody3D.new()
	body.collision_layer = 1 << (_tag_bit(tag) - 1)
	body.collision_mask = 0
	var cs := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = mx - mn
	cs.shape = box
	body.add_child(cs)
	area.attach(body, tag)
	body.position = (mn + mx) * 0.5
	cs.position = Vector3.ZERO

static func _all_spawners(area: Area) -> Array:
	var out: Array = []
	var stack: Array[Node] = [area]
	while not stack.is_empty():
		var n: Node = stack.pop_back()
		if n is Spawner:
			out.append(n)
		for c in n.get_children():
			stack.append(c)
	return out
