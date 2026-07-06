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
| Skyline / kingdom backdrop | ✅ | wrapping city_panorama (4 depth bands, no sky-gaps) + hero silhouettes; morphs gold↔dead-blue; boss yard roofed, tower door shut in glory |
| Save/persistence | ✅ | full world+player round-trip verified |
| HUD/UI | ✅ | bars/prompts/boss bar/floating enemy health bars (on-hit + lock-on, billboarded)/death splash/dialogue/rest menus; dialogue leave-cycle fixed; middle-mouse lock-on; wants gamepad glyphs + menus polish |
| Audio | 🟡 | fully synthesized pack (bells motif) + larksong/crow ambiences; coherent but synth-grade |
| Painted texture pass | ✅ | 8 procedural painterly maps (masonry/slabs/planks/shingles/weave/iron/wax) triplanar-overlaid on every family |
| Paired glory/ruin decor | ✅ | votive clusters↔melted, gardens↔withered, censers hung↔fallen, banners↔rags, saints↔kneeling husks, ivy, books |
| Ambient life | 🟡 | birds+petals in glory, crows+ash in ruin; wants perch points, flock behavior, insects |
| Characters | ✅ | 17-bone armature (neck), 10 archetypes, blended joint skinning, relaxed rest pose, cubic-eased clips with anticipation/settle; weapons/shields/helms ride bones |
| Full-loop verification | ✅ | scripted end-to-end playthrough of the §11 loop (fullloop test) |

## Pass 2+ backlog (concrete)

**World & scale**
- ~~Basilica interior as full Area C~~ done pass 4 (nave + triforium + Unrung Bell + Precentress).
- ~~Ossuary Undercroft~~ done pass 5 (three-way underground link, Watchers puzzle, Bell-Ox).
- ~~Skyline pass 2 (wrapping panorama, no gaps, per-state)~~ done pass 7; still wants dusk-haze parallax + bell-echo ambience.
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
- ~~ranged Chorister~~ pass 4; ~~bell-ox miniboss~~ + ~~fast assassin (Shroudbound)~~ pass 5; still wanted: a true glory-echo enemy.
- Aveline questline (missable, consequence-bearing); ~~the Sexton NPC~~ done pass 4 (dig service).

**Tech debt / audits**
- ~~HUD anchor-based layout~~ done (center/right elements anchored).
- ~~Mouse capture~~ done pass 3 (captured on spawn, Esc frees, click recaptures; LMB/RMB quiet while the cursor is free).
- ~~Perimeter audit~~ done pass 3 (`tools/audit_walls.py` rasterizes fills and flags unsealed boundary segments; east-walk hole walled, void arches blocked, porch under-stair sealed; kill-plane failsafe).
- ~~Decor/NPC collision~~ done pass 3 (solid props collide by kit policy, hangings/clutter stay passable; NPCs have bodies; walls_test guards it).
- ~~Row `skip` bug~~ done pass 3 (JSON floats vs int `Array.has`; phantom arcades stood in every skipped doorway).
- ~~Roof the garth + walks watertight~~ done pass 8 (decorative groin-vault bays spring from the wall cornice, capped by a stone slab + clerestory band; no eave sky-gaps). Ruin door-chokes rebuilt as a dense masonry mound over an opaque core (no see-through gaps). Still wants per-piece UV skirts on the outer walk roofs.
- Mesh merging per room + occlusion for perf on real GPUs.
- Gamepad glyphs, remapping, accessibility sliders.
