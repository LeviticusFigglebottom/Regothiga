class_name Hitbox
extends Area3D
## A swing's active volume. Enable for the active window; hits each hurtbox
## at most once per swing. Reports back to the wielder via callback.

var packet: DamagePacket
var _struck: Array[Node] = []
var on_contact: Callable = Callable()   # func(hurtbox, result)
var exclude: Node = null                # wielder root — never self-hit
var friendly_team := ""                 # hurtboxes of this team are never struck

func _init() -> void:
	collision_layer = 0
	collision_mask = 1 << (VG.L_HURTBOX - 1)
	monitoring = false
	monitorable = false
	area_entered.connect(_on_area)

func begin_swing(p: DamagePacket) -> void:
	packet = p
	_struck.clear()
	monitoring = true
	# catch hurtboxes already overlapping when the window opens
	for a in get_overlapping_areas():
		_on_area(a)

func end_swing() -> void:
	set_deferred("monitoring", false)
	packet = null

func _on_area(a: Area3D) -> void:
	if packet == null or not (a is Hurtbox):
		return
	var host := a.owner if a.owner != null else a.get_parent()
	if host == exclude or host in _struck:
		return
	# no friendly fire
	if exclude != null and exclude.is_in_group(VG.GROUP_ENEMIES) and host.is_in_group(VG.GROUP_ENEMIES):
		return
	if friendly_team != "" and (a as Hurtbox).team == friendly_team:
		return
	_struck.append(host)
	var result: String = (a as Hurtbox).receive(packet)
	if on_contact.is_valid():
		on_contact.call(a, result)
