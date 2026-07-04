# ROADMAP — Vespergard

Living map of what is real, what is shallow, what is stubbed, and what pass 2+ should take on. Updated at the end of every work session.

Legend: ✅ real · 🟡 shallow (works, thin) · 🩶 stub · ⬜ absent

## Pass 1 status

| System | Status | Notes |
|---|---|---|
| Glory↔ruin state system | ⬜ | in progress this pass |
| Transformation spectacle | ⬜ | in progress this pass |
| Blender→Godot kit pipeline | ⬜ | in progress this pass |
| Player combat core | ⬜ | in progress this pass |
| Enemies + encounters | ⬜ | in progress this pass |
| Death / Orisons loop | ⬜ | in progress this pass |
| Vigil lanterns + leveling | ⬜ | in progress this pass |
| The Gray Cloister (Area A) | ⬜ | in progress this pass |
| Bellkeeper boss | ⬜ | in progress this pass |
| NPC (Sister Aveline) | ⬜ | in progress this pass |
| Basilica of Last Light (Area B) | ⬜ | stub target |
| Save/persistence | ⬜ | in progress this pass |
| HUD/UI | ⬜ | in progress this pass |
| Audio | ⬜ | synthesized pack this pass |

(Statuses will be graded honestly at end of pass; "in progress" rows become ✅/🟡/🩶.)

## Pass 2+ backlog (concrete)

**World**
- Basilica of Last Light as a full area: rose-window nave, triforium loop, the Unrung Bell arc; interconnect back into the Cloister garth (door openable only from basilica side).
- 3rd area (Ossuary Undercroft) linking both — first true three-way interconnection; area-graph data already supports it.
- Fast travel between kindled lanterns (ceremony + map-less "bell peal" selection).
- Richer state-deltas: flooded-in-ruin passages, glory-only lift/bridge machinery, timed state-dependent events (processions in glory).

**Systems**
- Skeletal character rigs + animation retarget seam (replace node-rig visuals; combat data untouched).
- Weight/encumbrance tiers affecting roll (fat/medium/fast) — currently single tier with the hooks in place.
- Weapon upgrade tree depth (+1..+5, scaling growth), infusions; 2 more weapon classes (halberd, censer-flail).
- Poise-damage tuning pass across full bestiary; guard-break stance system.
- Status effects (bleed→"guttering", burn→"waxfire").
- Talismans/rings ("votive seals") — slot UI exists as roadmap stub.

**Content**
- Aveline questline (missable, consequence-bearing: she follows the pilgrim road; can be doomed by clearing areas before buying her wax).
- 2nd NPC (the Sexton — upgrades armor, digs shortcuts for pay).
- 3 more enemy types incl. ranged (Chorister) and glory-echo assassin (attacks even in glory — breaks the safety rule *once*, deliberately).
- 2nd boss (the Sexton's Bell-Ox) + optional duo fight.
- Item descriptions pass — every item carries a shard of the fall.

**Tech/quality**
- Recorded/pro audio replacing synth pack; adaptive layers (proximity-to-enemies stem mixing).
- Cutscene-grade transformation camera option (rooted orbital) with player-motion opt-out.
- Performance: mesh merging per room, occlusion culling, LOD on kit pieces.
- Gamepad glyphs, remapping UI, accessibility (subtitle scale, screen shake slider — sliders exist in data only).
- Proper blackletter display font (custom, licensed or drawn) replacing DejaVu Serif styling.
