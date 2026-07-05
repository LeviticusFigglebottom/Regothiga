# ROADMAP — Vespergard

Living map of what is real, what is shallow, what is stubbed, and what pass 2+ should take on.

Legend: ✅ real · 🟡 shallow (works, thin) · 🩶 stub · ⬜ absent

## Pass 1 status (honest grading)

| System | Status | Notes |
|---|---|---|
| Glory↔ruin state system | ✅ | per-area persistence, layer swaps, dual navmesh, route deltas verified by raycast tests |
| Transformation spectacle | ✅ | expanding wave, per-fragment morph, dissolve edges, env/sun lerp, particle front, swell audio; captured in-game from player POV |
| Blender→Godot kit pipeline | ✅ | 60 generated pieces, one shader family, headless author→render→verify loop |
| Player combat core | ✅ | stamina, i-frame rolls, combos, block/parry/riposte, poise, lock-on — 19 checks green |
| Enemies + encounters | ✅ | 3 archetypes + 2 bosses; ranged chorister (projectiles, keep-away AI), Precentress summons her choir; deliberate telegraphs |
| Death / Orisons loop | ✅ | drop → one-chance remembrance → replacement rule; 22 checks green |
| Vigil lanterns + leveling | ✅ | rest menu, kindle/gutter choice when cleared, attribute leveling |
| The Gray Cloister (Area A) | ✅ | 9 rooms/spaces, both states authored, shortcut gate + 2 state-routes, 13 foes |
| Bellkeeper boss | 🟡 | fog gate, 2 phases, shockwaves, cameo-in-glory; moveset depth + arena drama wanted |
| NPCs (Aveline, the Sexton) | 🟡 | lore, blessing/flask services, the Sexton digs a paid shortcut; questlines absent |
| Basilica of Last Light (B+C) | ✅ | porch, terrace, and now the full Nave: triforium gallery, rose window, the Unrung Bell, Precentress boss, Sexton NPC, two puzzles |
| Skyline / kingdom backdrop | 🟡 | tower/cathedral/arc/cluster ring in both areas; wants parallax layers + per-area composition pass |
| Save/persistence | ✅ | full world+player round-trip verified |
| HUD/UI | 🟡 | bars/prompts/boss bar/death splash/dialogue/rest menus; anchored layout; wants gamepad glyphs + menus polish |
| Audio | 🟡 | fully synthesized pack (bells motif) + larksong/crow ambiences; coherent but synth-grade |
| Painted texture pass | ✅ | 8 procedural painterly maps (masonry/slabs/planks/shingles/weave/iron/wax) triplanar-overlaid on every family |
| Paired glory/ruin decor | ✅ | votive clusters↔melted, gardens↔withered, censers hung↔fallen, banners↔rags, saints↔kneeling husks, ivy, books |
| Ambient life | 🟡 | birds+petals in glory, crows+ash in ruin; wants perch points, flock behavior, insects |
| Characters | ✅ | skeletal pass done: shared 16-bone armature, 5 skinned archetypes, bone-track clips (walk/run/attacks/roll/kneel/death…) built in-engine from the rest pose; weapons/shields/helms ride bones |
| Full-loop verification | ✅ | scripted end-to-end playthrough of the §11 loop (fullloop test) |

## Pass 2+ backlog (concrete)

**World & scale**
- ~~Basilica interior as full Area C~~ done pass 4 (nave + triforium + Unrung Bell + Precentress).
- Ossuary Undercroft (Area D) linking Cloister and Basilica underground — first three-way interconnection.
- Skyline pass 2: silhouette LOD ring at 150–400 m, dusk haze layers, birds/bell-echo ambience; per-area skyline compositions.
- Traversable lower-city streets below the terrace (the stair already lands there).
- Fast travel between kindled lanterns.

**Art**
- Painted-texture pass 2: per-piece UV bakes (Cycles AO/edge-wear) for hero props on top of the triplanar layer; trim sheets for portals.
- ~~Skeletal characters + animation retarget seam~~ done pass 3 (CharVisual + SkelAnim; node-rigs retired; combat data untouched).
- Animation polish: hand-keyed easing curves, additive hit-reacts, foot IK on stairs.
- Weathering decals, ivy geometry, richer ruin deltas (collapsed vault bays, flooded walk).
- Transformation: rooted orbital camera option, debris geyser at wavefront, per-entity poof timing.

**Systems**
- Weight/encumbrance roll tiers; status effects (guttering/waxfire); talismans ("votive seals").
- Weapon upgrade depth +1..+5 with scaling growth; halberd + censer-flail movesets for the player.
- ~~ranged Chorister~~ done pass 4; still wanted: glory-echo assassin, bell-ox miniboss.
- Aveline questline (missable, consequence-bearing); ~~the Sexton NPC~~ done pass 4 (dig service).

**Tech debt / audits**
- ~~HUD anchor-based layout~~ done (center/right elements anchored).
- ~~Mouse capture~~ done pass 3 (captured on spawn, Esc frees, click recaptures; LMB/RMB quiet while the cursor is free).
- ~~Perimeter audit~~ done pass 3 (`tools/audit_walls.py` rasterizes fills and flags unsealed boundary segments; east-walk hole walled, void arches blocked, porch under-stair sealed; kill-plane failsafe).
- ~~Decor/NPC collision~~ done pass 3 (solid props collide by kit policy, hangings/clutter stay passable; NPCs have bodies; walls_test guards it).
- ~~Row `skip` bug~~ done pass 3 (JSON floats vs int `Array.has`; phantom arcades stood in every skipped doorway).
- Roof piece UV/skirt so walk roofs read from the garth at all angles.
- Mesh merging per room + occlusion for perf on real GPUs.
- Gamepad glyphs, remapping, accessibility sliders.
