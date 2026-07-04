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
| Enemies + encounters | 🟡 | 2 archetypes + boss; deliberate telegraphs; placement-with-intent; wants more variety + ranged |
| Death / Orisons loop | ✅ | drop → one-chance remembrance → replacement rule; 22 checks green |
| Vigil lanterns + leveling | ✅ | rest menu, kindle/gutter choice when cleared, attribute leveling |
| The Gray Cloister (Area A) | ✅ | 9 rooms/spaces, both states authored, shortcut gate + 2 state-routes, 13 foes |
| Bellkeeper boss | 🟡 | fog gate, 2 phases, shockwaves, cameo-in-glory; moveset depth + arena drama wanted |
| NPC (Sister Aveline) | 🟡 | lore lines, weapon blessing, flask upgrade; questline absent |
| Basilica of Last Light (B) | 🩶 | porch + sunset terrace + skyline; interior sealed ("next passing") |
| Skyline / kingdom backdrop | 🟡 | tower/cathedral/arc/cluster ring in both areas; wants parallax layers + per-area composition pass |
| Save/persistence | ✅ | full world+player round-trip verified |
| HUD/UI | 🟡 | bars/prompts/boss bar/death splash/dialogue/rest menus; fixed-resolution layout, needs anchor pass |
| Audio | 🟡 | fully synthesized pack (bells motif); coherent but synth-grade |
| Characters | 🟡 | humanoid silhouette pass done (elbows, pauldrons, proportions); still node-rigs, no skeletal animation |
| Full-loop verification | ✅ | scripted end-to-end playthrough of the §11 loop (fullloop test) |

## Pass 2+ backlog (concrete)

**World & scale**
- Basilica interior as full Area C: rose-window nave, triforium walkway loop, the Unrung Bell arc.
- Ossuary Undercroft (Area D) linking Cloister and Basilica underground — first three-way interconnection.
- Skyline pass 2: silhouette LOD ring at 150–400 m, dusk haze layers, birds/bell-echo ambience; per-area skyline compositions.
- Traversable lower-city streets below the terrace (the stair already lands there).
- Fast travel between kindled lanterns.

**Art**
- Painted-texture pass: bake gradient/AO painterly maps in Blender (Cycles) for hero pieces; keep shader family.
- Skeletal characters + animation retarget seam (replaces node-rigs; combat data untouched).
- Weathering decals, ivy geometry, richer ruin deltas (collapsed vault bays, flooded walk).
- Transformation: rooted orbital camera option, debris geyser at wavefront, per-entity poof timing.

**Systems**
- Weight/encumbrance roll tiers; status effects (guttering/waxfire); talismans ("votive seals").
- Weapon upgrade depth +1..+5 with scaling growth; halberd + censer-flail movesets for the player.
- 3 more enemy types (ranged Chorister, glory-echo assassin, bell-ox miniboss).
- Aveline questline (missable, consequence-bearing); the Sexton NPC (armor, shortcut-digging).

**Tech debt / audits**
- HUD anchor-based layout (currently 1920×1080 logical coordinates).
- Roof piece UV/skirt so walk roofs read from the garth at all angles.
- Mesh merging per room + occlusion for perf on real GPUs; collision audit automation (nav-vs-collision diff report).
- Gamepad glyphs, remapping, accessibility sliders.
