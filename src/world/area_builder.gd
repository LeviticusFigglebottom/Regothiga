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

	area.env.set_overrides(def.get("env", {}))
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
	for spec in def.get("boxes", []):
		_solid_box(area, spec)

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
		if spec.has("spawn_yaw"):
			pt.spawn_yaw = float(spec["spawn_yaw"])
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
	"book_stack", "scroll_pile", "rubble_s", "mosaic_medallion",
	"cobweb", "hanging_chain", "hanging_chain_bare", "shroud_dead",
	"lark_cage", "lark_cage_dead", "perch_rail", "perch_rail_bare",
	"aviary_screen", "reed_clump", "reed_clump_dead"]

static func _prop_collides(spec: Dictionary) -> bool:
	if spec.has("collide"):
		return bool(spec["collide"])
	return not (String(spec.get("kit", "")) in PASSABLE_PROPS)

## Kits that are walls/openings you must pass through — these keep exact
## trimesh collision. Anything NOT here gets a solid convex blocker.
const STRUCTURAL_KITS := ["wall_4x4", "arcade_4m", "portal_4m", "window_lancet_4m",
	"ossuary_wall_4m", "balustrade_4m", "buttress", "rose_window", "roof_shed_4m",
	"vault_bay_4x4", "floor_4x4", "fence_iron_4m", "gate_iron", "cornice_4m",
	"gate_black"]   # trimesh keeps the walkable breach between the leaves

static func _is_structural(kit) -> bool:
	return String(kit) in STRUCTURAL_KITS

static func _piece(area: Area, spec: Dictionary, collide: bool) -> Node3D:
	var tag: String = spec.get("tag", "base")
	var mode := 1 if tag == "glory" else (2 if tag == "ruin" else 0)
	var piece := KitLib.instance(spec["kit"], mode)
	_place(piece, spec)
	if spec.has("scale"):
		var sc = spec["scale"]
		piece.scale = _v3(sc) if sc is Array else Vector3.ONE * float(sc)
	if collide and spec.get("collide", true):
		if String(spec["kit"]).begins_with("stair_grand_4m"):
			_stair_ramp(piece, tag, String(spec["kit"]))   # ramp-only: step trimesh would wall off the climb
		else:
			# architecture (walls, arcades, portals, windows) keeps its exact
			# hollow shell so you can pass through openings; everything else
			# is a solid convex blocker so the capsule never wedges inside it
			KitLib.add_collision(piece, _tag_bit(tag), not _is_structural(spec["kit"]))
	if spec.get("flames", true) and (tag != "ruin"):
		KitLib.add_flame_lights(piece)
	area.attach(piece, tag)
	return piece

## Grand stairs collide as a smooth 31-degree ramp, never as step trimesh:
## 0.24 m step faces are walls to move_and_slide, so the climb direction
## would be impassable. The ramp surface runs from the top edge (local
## origin) to the floor 0.2 below the stair base, meeting walkable ground
## flush at both ends. The sides carry RAKED parapet colliders that follow
## the slope and match the kit's visible parapets — the old full-height
## level boxes were invisible walls beside every open flight, and left the
## upper half of open flights unguarded.
static func _stair_ramp(piece: Node3D, tag: String, kit := "stair_grand_4m") -> void:
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
	# parapet flanks mirror the kit variant: _l keeps only x<0, _r only x>0
	var flanks: Array = [-2.17, 2.17]
	if kit.ends_with("_l"):
		flanks = [-2.17]
	elif kit.ends_with("_r"):
		flanks = [2.17]
	for sx in flanks:
		var fs := CollisionShape3D.new()
		var fb := BoxShape3D.new()
		fb.size = Vector3(0.36, 1.5, 5.15)
		fs.shape = fb
		fs.rotation_degrees = Vector3(-30.96, 0, 0)
		# ramp center lifted along the ramp normal so the parapet top rides
		# ~1.05 m above the treads the whole way down
		fs.position = Vector3(sx, -0.70, -2.57)
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

## Wall pieces are 4 m tall; a vault bay rises 2.19 m from its springline.
## Spring the vaults FROM the wall-top cornice so the web meets the walls and
## the apex sits inside the room, then cap with a watertight slab + a
## clerestory band closing the gap between wall-top and slab. Result: a fully
## roofed room, no vault poking above the walls, no sky leaking at the eaves.
const _WALL_TOP := 4.0
const _VAULT_APEX := 1.358

static func _vault_field(area: Area, spec: Dictionary) -> void:
	var mn := _v3(spec.get("min", [0, 0, 0]))
	var mx := _v3(spec.get("max", [4, 0, 4]))
	var tag: String = spec.get("tag", "base")
	# the cornice sits a wall-height above THIS field's floor, so a raised room
	# (the undercroft landings at y=2.4) gets full headroom instead of a ceiling
	# pressed down to the hall's 4 m. spring_top still overrides absolutely.
	var wall_top := mn.y + _WALL_TOP
	var spring := float(spec.get("spring_top", wall_top))
	# "band_from" lifts the clerestory band's lower edge (absolute Y). Raised
	# rooms open onto these halls through doorways at the field edge; a band
	# starting at the 4 m wall-top crossed those doorways at head height. Any
	# strip left open below band_from must be sealed per-edge with boxes.
	var band_from := float(spec.get("band_from", wall_top))
	# some rooms read better with a plain timber-beamed flat ceiling than groin
	# vaults; "flat": true opts a field into that (vaults stay for grander halls)
	if spec.get("flat", false):
		_flat_ceiling(area, mn, mx, tag, wall_top)
		return
	var ceil_h := spring + _VAULT_APEX + 0.2
	# decorative groin vaults, springing from the cornice
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
	# watertight lid + clerestory band so no sky shows above the walls (absolute Y)
	var mat := MaterialLib.get_mat("M_stone", _state_mode(tag))
	_roof_box(area, tag, mat, Vector3((mn.x + mx.x) * 0.5, ceil_h + 0.15, (mn.z + mx.z) * 0.5),
			Vector3(mx.x - mn.x + 0.4, 0.3, mx.z - mn.z + 0.4))
	var cy := (band_from + ceil_h) * 0.5
	var ch := maxf(ceil_h - band_from, 0.1)
	# north / south (span x), east / west (span z)
	_roof_box(area, tag, mat, Vector3((mn.x + mx.x) * 0.5, cy, mn.z), Vector3(mx.x - mn.x + 0.4, ch, 0.4))
	_roof_box(area, tag, mat, Vector3((mn.x + mx.x) * 0.5, cy, mx.z), Vector3(mx.x - mn.x + 0.4, ch, 0.4))
	_roof_box(area, tag, mat, Vector3(mn.x, cy, (mn.z + mx.z) * 0.5), Vector3(0.4, ch, mx.z - mn.z + 0.4))
	_roof_box(area, tag, mat, Vector3(mx.x, cy, (mn.z + mx.z) * 0.5), Vector3(0.4, ch, mx.z - mn.z + 0.4))

## A flat, sensibly-high coffered ceiling: a stone lid a little above the wall
## cornice, crossed by warm timber beams, with a short clerestory band sealing
## the gap so no sky shows. Used where groin vaults would feel too busy.
static func _flat_ceiling(area: Area, mn: Vector3, mx: Vector3, tag: String, wall_top: float) -> void:
	var lid := wall_top + 0.85
	var mat := MaterialLib.get_mat("M_stone", _state_mode(tag))
	var wood := MaterialLib.get_mat("M_wood", _state_mode(tag))
	# the flat lid (absolute Y)
	_roof_box(area, tag, mat, Vector3((mn.x + mx.x) * 0.5, lid + 0.15, (mn.z + mx.z) * 0.5),
			Vector3(mx.x - mn.x + 0.4, 0.3, mx.z - mn.z + 0.4))
	# timber beams every 4 m across the shorter span, for a coffered read
	var span_x := mx.x - mn.x
	var span_z := mx.z - mn.z
	if span_x <= span_z:
		var bx := mn.x + 2.0
		while bx < mx.x - 0.01:
			_roof_box(area, tag, wood, Vector3(bx, lid - 0.13, (mn.z + mx.z) * 0.5),
					Vector3(0.24, 0.26, span_z))
			bx += 4.0
	else:
		var bz := mn.z + 2.0
		while bz < mx.z - 0.01:
			_roof_box(area, tag, wood, Vector3((mn.x + mx.x) * 0.5, lid - 0.13, bz),
					Vector3(span_x, 0.26, 0.24))
			bz += 4.0
	# clerestory band closing wall-top -> lid on all four sides
	var cy := (wall_top + lid) * 0.5
	var ch := maxf(lid - wall_top, 0.1)
	_roof_box(area, tag, mat, Vector3((mn.x + mx.x) * 0.5, cy, mn.z), Vector3(mx.x - mn.x + 0.4, ch, 0.4))
	_roof_box(area, tag, mat, Vector3((mn.x + mx.x) * 0.5, cy, mx.z), Vector3(mx.x - mn.x + 0.4, ch, 0.4))
	_roof_box(area, tag, mat, Vector3(mn.x, cy, (mn.z + mx.z) * 0.5), Vector3(0.4, ch, mx.z - mn.z + 0.4))
	_roof_box(area, tag, mat, Vector3(mx.x, cy, (mn.z + mx.z) * 0.5), Vector3(0.4, ch, mx.z - mn.z + 0.4))

static func _state_mode(tag: String) -> int:
	return 1 if tag == "glory" else (2 if tag == "ruin" else 0)

## A solid box of geometry (roof slab / clerestory strip) attached to a layer.
static func _roof_box(area: Area, tag: String, mat: Material, center: Vector3, size: Vector3) -> void:
	var mi := MeshInstance3D.new()
	var bm := BoxMesh.new()
	bm.size = size
	mi.mesh = bm
	mi.material_override = mat
	mi.position = center
	area.attach(mi, tag)

## A visible solid stone block with a matching collider: stair cheeks, landing
## skirts, plinths. A modular 4 m wall grid can't tile a 4.68 m stair opening
## flush, so raised-floor edges leave slivers of exposed drop beside the stairs;
## a skirt box seals the vertical face. min/max in world space; optional "mat"
## (defaults to the wall stone) and "tag".
static func _solid_box(area: Area, spec: Dictionary) -> void:
	var tag: String = spec.get("tag", "base")
	var mn := _v3(spec["min"])
	var mx := _v3(spec["max"])
	var center := (mn + mx) * 0.5
	var size := mx - mn
	var mat := MaterialLib.get_mat(spec.get("mat", "M_stone"), _state_mode(tag))
	var mi := MeshInstance3D.new()
	var bm := BoxMesh.new()
	bm.size = size
	mi.mesh = bm
	mi.material_override = mat
	mi.position = center
	area.attach(mi, tag)
	if spec.get("collide", true):
		var body := StaticBody3D.new()
		body.collision_layer = 1 << (_tag_bit(tag) - 1)
		body.collision_mask = 0
		var cs := CollisionShape3D.new()
		var cb := BoxShape3D.new()
		cb.size = size
		cs.shape = cb
		body.add_child(cs)
		body.position = center
		area.attach(body, tag)

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
