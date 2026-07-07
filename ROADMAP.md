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
- ~~Placement auditor + stair-flank skirts~~ done pass F (`tools/audit_areas.py` flags unroofed cells, floating/sunk/in-wall/duplicate props and floor holes, tag-aware so glory/ruin pairs don't false-positive; `open_air_regions` whitelists intentional courts). A modular 4 m wall grid can't tile a 4.68 m stair mouth flush, so the raised undercroft landings leaked a sliver of exposed drop beside each stair — sealed with a data-level `boxes` primitive (visible stone + collider).
- ~~Exterior-visibility audit~~ done pass G. Added an OVERLAP check (distinct co-present props merged within 0.5 m) to `audit_areas.py`; swept every room's corners, wall/roof seams, raised-floor edges and outward views — all watertight except the Basilica's locked nave doorway, which framed the city panorama through an open arch where the lore says the door is shut. Closed it with a banded-oak `door_leaf` (the transition is interact-driven, so the solid door dresses the portal without blocking travel).
- ~~City rooted to the ground + every threshold doored~~ done pass H. The skyline sat on a shallow slope so its flat-based buildings floated over their downhill edge — you could see under the city to the horizon. Each panorama building now sinks a foundation to a common floor well below the visible ground, so it roots into the hillside from every angle; the ground eases into a valley floor and a CLOSE ring of distinct buildings frames the balustrade (not just distant ones). Every wall-doorway transition (porch↔cloister, porch↔nave both ways) now carries a `door_leaf`, and the door grew a stone tympanum so the pointed arch above the leaves no longer leaks sky/city at its tip. Stair transitions (the sisters'/sexton's stairs) stay open — they read as natural passages. Areas remain separate scenes on purpose: the glory↔ruin shift is scoped per-area at each Vigil Lantern, and a merged world would force one global shift.
- ~~Skyline reads as a real kingdom~~ done pass F. `city_panorama` rebuilt from brick prisms into distinct Anor-Londo monuments (buttressed cathedrals, belfry towers, domes, tiered palaces, temple-fronts) on a hillside that falls away from the terrace — the vista is an overlook into a golden valley, not a flat plate floating in the void. New `stylized_sky.gdshader` replaces the plain gradient: banded sky, a low sun/moon orb with god-rays and drifting cloud banks in glory, a cold star-pricked firmament in ruin. Braziers burn glowing embers (`M_ember`) instead of a dark iron cone; hanging censers now bolt to the vault by a ceiling-plate.
- ~~Terrace is a solid promontory, not a floating shelf~~ done pass I. Pass H rooted the distant *city* but not the *terrace you stand on*: it was two thin 0.25 m floor slabs with nothing beneath, so any downward glance over the balustrade found void, and the lower-terrace railings were authored at y=-2.4 on a y=-2.62 floor (floating 0.22 m) with the side rails at x=±8.2 hanging past the x=±8 floor edge. Reseated every rail on its floor and inside the edge, and gave the porch a solid substructure (`boxes` dropping both levels to y=-40) so the overlook reads as rock — the city now rises immediately beyond a solid parapet, no seam, no exposed slab underside. **Audit gap that let this ship:** `audit_areas.py` had `balustrade_4m` in the ARCH skip-set ("rides at height on purpose") so it never checked railing grounding, and the float tolerance (0.6 m) was looser than the error. Fixed: railings are grounding-checked with a tight 0.18 m tolerance but a wide horizontal reach (so a gallery rail lining its floor's inner edge isn't a false positive); regression-verified it flags the exact terrace defect and stays clean on the nave triforium rails. The class is now checked systematically: an UNBACKED audit flags any open-air floor slab with a lower vantage in the area and no substructure (box/room) beneath its footprint — regression-verified against the pre-fix porch. Worst-case-angle photo sweep of the other areas (nave gallery soffit + mezzanine riser, undercroft landing risers, cloister) found the class porch-only.
- ~~Review pass over pass H/I claims~~ done pass J. Verified every prior "fix" against live renders from the player's angles; three porch defects survived the earlier passes and are now remediated: (1) every lower-terrace prop floated 0.2 m (authored at the phantom -2.42 level; the auditor's 0.6 m tolerance waved it through — now 0.15 m and pickups/lanterns/npcs/plaques/spawners join the grounding check); (2) the "incomplete/inverted stained glass" was a LAYOUT bug, not a kit bug — the z=-8 wall row buried half of each window (and the nave's window rows ran step 4 instead of 8, burying two panels per aisle). New WALL-OVERLAP audit catches see-through openings buried in same-plane walls; `expand_row` now carries rot/scale (dropping rot had hidden the nave hits); portal_4m is exempt by design (portal-against-sealing-wall is the intended dark-doorway transition dressing); (3) the porch roof lid/band ended unsupported mid-air at z=0 — a portico line (arcade bays + grand arched centre) now carries it as a narthex screen. Fallen censers nudged out of two enemy spawn points.
- ~~The kingdom below is a real city~~ done pass J. `city_panorama` rebuilt from ring-scattered prisms (nearest ring 6 m past the balustrade — unreadable, streetless) into a terraced pilgrim city: flat plateau rings behind retaining walls, a ring street per terrace lined with slate-roofed rowhouses (doors, lamplit-or-dark windows, chimneys, gilded ridges), radial lanes, a processional avenue stepped terrace-to-terrace under gilt lamp columns to a plaza (gilded saint's column, obelisks) and out the great gate of a crenellated city wall with drum towers; cathedrals/domes/belfries stand as mid-distance landmarks and the far spire-skyline keeps the horizon. New families: M_gild (glory-gated gold glint) and M_citywindow (lamplit in glory, dead in ruin).
- ~~Esc pause menu~~ done pass J. PauseUI autoload owns Esc (player keeps click-to-recapture): pauses the tree (music keeps playing), thematic panel (Return / Settings / Begin the Pilgrimage Anew / Abandon). Settings persist to user://settings.cfg and apply live: master/music/effects/ambience buses, mouse sensitivity, field of view, fullscreen. Begin Anew is a TRUE new game — save file destroyed, world/flags/orisons forgotten, scene rebuilt from the first bell (the old "restart" was just a respawn-in-place). 17-check menu_test covers open/pause/close, settings reaching the rig and buses, persistence, and the full wipe.
- Mesh merging per room + occlusion for perf on real GPUs.
- Gamepad glyphs, remapping, accessibility sliders.
