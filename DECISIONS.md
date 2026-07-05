# DECISIONS — Vespergard

Architecture and direction decisions for the project, with rationale. Newest sections are appended; nothing is deleted, superseded decisions are struck through with a note.

---

## D-000 · What this is

**Vespergard** is a gothic soulslike built in **Godot 4.7** with a **stylized Blender (bpy) asset pipeline**. Its signature mechanic: the world shifts between the radiant **glory** of the fallen Evening Kingdom and its overrun **ruin**, toggled at rest sites. You explore each area in glory, then fight back through it in ruin.

---

## D-001 · Toolchain

| Piece | Choice | Why |
|---|---|---|
| Engine | Godot 4.7 stable (official binary) | Native glTF import, Forward+ renderer (volumetric fog, global shader uniforms — both load-bearing for the state system), text-based scene formats that can be authored and diffed headlessly. |
| Renderer | Forward+ (Vulkan) | Volumetric god-rays in glory, clustered lights for candle-dense interiors, global `uniform`s drive the transformation wave across every material at once. Verified working on CPU (lavapipe) for headless screenshot verification. |
| Assets | Blender 4.5 LTS via the `bpy` pip module | Fully headless, scriptable, deterministic. Procedural generators are the coherence engine: one gothic style encoded once, emitted uniformly across the whole kit. |
| Interchange | glTF 2.0 (`.glb`) | Godot-native import; bpy exporter handles Z-up→Y-up. Conventions in D-004. |
| Language | GDScript only | One language, no build step, headless-friendly. Perf is fine at this scope; hot paths (wave update) are shader-side anyway. |
| Verification | `bpy` render + `xvfb-run godot` screenshot harness | The author→render→**look**→refine loop. No visual work is authored blind. Logic is verified by headless sim tests that drive the player through the real game. |

**Why not C#/Rust/GDExtension:** iteration speed and headless simplicity dominate; nothing in pass 1 is CPU-bound enough to justify a second toolchain.

---

## D-002 · The two-state model: one area, three layer sets

An area is **not** two levels. It is:

- **Base** — architecture present in both states (walls, floors, vaults, columns). Base geometry never swaps; its *look* morphs (see D-003).
- **Glory layer** — warm lighting rig, NPCs, intact-only props (candles lit, banners, intact stained glass), glory-only routes/colliders.
- **Ruin layer** — cold lighting rig, enemies/spawners, rubble, damage overlays, broken variants, ruin-only routes/colliders.

Each layer owns its **navmesh** (two `NavigationRegion3D`s, baked at area load from state-tagged collision groups; toggling swaps the active region). Route differences are therefore *real* — a wall intact in glory and collapsed into a passage in ruin is two different collision + nav worlds.

Persistence: `WorldState` autoload holds per-area `{state, cleared, flags}` plus global flags, saved as JSON in `user://`. The state of every visited area persists; cleared areas toggle freely at their lantern (D-010).

**Why layers, not two scenes:** building one area yields both states (the economy the whole game depends on); the transformation can morph *in place* because both versions coexist in one scene tree; and diffs between states stay data (which layer a node belongs to), not code.

---

## D-003 · One shader to rule the look: `gothic.gdshader`

Every kit surface uses one shared shader family. It provides:

1. **Stylized shading** — half-Lambert ramp partially quantized (painterly-toon, not photoreal), rim light, triplanar detail noise so bare meshes read as stone without texture authoring.
2. **State morphing on base geometry** — a per-fragment `state` value lerps warm/intact ↔ cold/decayed: desaturation, moss growth (world-height + vertex-color masked), crack darkening (noise threshold), candle/window emission gating. One material, both looks — zero extra authoring per asset.
3. **The transformation wave** — global uniforms (`vg_wave_r`, `vg_wave_origin`, `vg_wave_dir`, `vg_state_blend`) let the rest-site wave sweep the *entire* world per-fragment: base geometry morphs at the wavefront with a glowing edge band; state-exclusive meshes dissolve in/out with burning edges. This is why the flip is a *moment*, not a hard cut — and why it costs one material parameter, not per-object scripting.

Vertex colors carry per-asset damage/AO masks painted by the bpy generators (R = wear, G = moss zone, B = AO) so decay lands where a human would put it, not uniformly.

**Stained glass is geometry, not texture:** panes are generated as leaded mosaics (colored facets + dark lead lines), vertex-colored, emissive in glory, replaced by shard remnants in ruin. Stylized, texture-free, and it makes the glory windows the showpiece they need to be.

---

## D-004 · Blender→Godot conventions

- Generators live in `tools/blender/`; `tools/gen_assets.py` rebuilds everything deterministically (fixed seeds).
- **Real-world scale** (4 m module grid), **all transforms applied**, origins at logical snap points, `-Z` forward per glTF (exporter converts Blender Z-up → glTF Y-up).
- Kit pieces export as individual `.glb` into `assets/kit/`; Godot imports them as scenes; materials are **remapped at instancing time to the shared shader library** by material-name convention (`M_stone`, `M_glass`, `M_iron`, `M_wax`, …) via `KitLib.instance()` → `MaterialLib`. (Chosen over an editor import plugin so the whole path works headless with zero editor dependency.) Blender materials are placeholders; the *Godot* material library is the single source of visual truth.
- Baking: where a procedural Blender material is used (stone albedo variation), it is baked to textures before export per glTF constraints; most of the kit instead relies on vertex color + shader detail, which keeps the repo light and the look unified.
- Generated assets are **committed** so the game runs without Blender installed; regeneration requires only `pip install bpy`.

---

## D-005 · Characters: articulated node rigs, not skeletal animation

Characters (player, enemies, NPCs, boss) are robed/hooded figures assembled from kit parts on a small node hierarchy (hips/torso/head/arm pivots/cloak), animated by Godot `AnimationPlayer` clips authored as text resources plus procedural motion (bob, lean, sway) in code. Robes read as full characters without legs; the ghostly glide fits a kingdom of memory.

**Why:** full skeletal round-trip through glTF is the highest-risk, lowest-leverage part of a headless pipeline. Node-rig clips are hand-tunable in text, diffable, and combat timing lives in *data* (D-006) rather than baked animation, so feel can be tuned without re-export. Skeletal characters are a roadmap item; the seam (a `CharacterVisual` scene per archetype) is isolated so swapping later touches nothing in combat code.

---

## D-006 · Combat timing is data, animation is flavor

Weapon movesets, attack windows (windup/active/recovery), stamina costs, poise damage, i-frame windows, and scaling live in `data/combat/*.json`. The combat state machine consumes data; `AnimationPlayer` clips are synchronized visuals. Hitboxes are code-driven shapes enabled during active windows.

**Why:** soulslike feel is 90% timing tuning. Numbers in JSON mean tuning passes never touch systems code, and the headless sim can assert frame-accurate behavior (i-frames, parry windows) deterministically.

---

## D-007 · Areas are compiled from data

`data/areas/<id>.json` describes an area in level-language: wall runs, arcades, floor fields, vault grids, props, lights, spawns, interactables — each tagged `base` / `glory` / `ruin`. `AreaBuilder` compiles this to the scene tree at load (instancing kit scenes, snapping to the module grid), then bakes both navmeshes.

**Why:** pass 2+ adds areas by writing JSON and new kit pieces, not by scene surgery. The area graph (connections, lantern ids, gates) is part of the same data, so world interconnection grows as data too.

---

## D-008 · Original IP glossary (genre furniture renamed)

| Genre term | Vespergard term |
|---|---|
| The kingdom / setting | **Vespergard**, the Evening Kingdom — fell on the night the sun set and did not rise |
| Player character | **The Latecomer** — a pilgrim who arrived after the end |
| Bonfire / checkpoint | **Vigil Lantern** — resting = **keeping vigil** |
| World-state toggle | **Kindle** (→ glory) / **Gutter** (→ ruin); lanterns hold the kingdom's memory — glory is the world *remembering itself* around you |
| Souls / currency | **Orisons** — prayers of the dead, gathered from the fallen |
| Bloodstain / corpse run | **Remembrance** — your dropped orisons; one chance to reclaim, lost if you fall again |
| Estus / healing flask | **Chrism Flask** — consecrated oil, charges restored by vigil |
| Death message | **FORGOTTEN** |
| Level-up stats | Vitality, Endurance, Strength, Grace, Devotion |
| Upgrade material | **Candleglass** — fused glass-and-wax shards found in ruin |
| Area A | **The Gray Cloister** |
| Area B (stub) | **Basilica of Last Light** |
| Boss A | **The Bellkeeper** — in glory he rings the cloister hours; in ruin he drags his cracked bell as a weapon |
| NPC A | **Sister Aveline, the Chandler** — candle-crowned nun; merchant + weapon blessing, met in glory |
| Enemies | **Waxbound Penitents** (melted votive wretches), **Cloister Wards** (spectral halberd knights) |

Diegesis of the mechanic: lanterns hold the kingdom's memory. A first vigil in a new area **gutters** it — witnessing the truth collapses the dream, and the memory *will not rekindle while the area's warden endures* (bosses gate free toggling). Put the warden to rest and the lantern can kindle or gutter the area at will.

---

## D-009 · Progression rhythm (per area)

1. Enter in **glory** (default for unvisited areas — the memory still burns). Explore safely, meet NPCs, learn layout, unlock shortcuts.
2. First vigil at the area's lantern → **gutter** → ruin. Pre-clear, the lantern cannot rekindle glory (the warden's presence drowns the memory) — the gauntlet is committed.
3. Fight back through learned space; shortcuts from glory are lifelines; boss is the climax behind a fog gate.
4. Warden down → area **cleared** → free kindle/gutter at its lantern, persisted. The route onward opens toward the next area's lantern.

Dropped Remembrances persist across both states (they are *your* memory, not the kingdom's) — dying in ruin never strands your orisons in an unreachable state.

---

## D-010 · Save model

Single JSON save in `user://saves/` (override path via `--save-dir` for tests): player (stats, level, orisons, equipment, flask, position, last lantern), per-area (state, cleared, opened gates, taken items, dead-once entities), world flags (NPC progress), pending Remembrance (area, position, amount). Autosave at vigils, area transitions, and major flags. No manual save slots in pass 1 (roadmap).

---

## D-011 · Audio is synthesized, not sourced

All audio is generated by `tools/audio/synth.py` (pure Python, committed WAVs): state themes (glory choir-warmth / ruin drone), transformation swell, bells (the kingdom's motif), combat foley, UI. No licensing risk, deterministic rebuilds, and the bell-heavy palette *is* the identity. Quality ceiling is real (roadmap: recorded/pro audio) but coherence beats fidelity at this stage.

---

## D-013 · The Anor-Londo-scale direction (iteration-1.5 art brief)

The radiant state should feel like standing inside an entire kingdom at
sunset: expansive skyline, monumental terraces, dense propping. Implemented
as:

- **Skyline backdrop kit** — `spire_tower` (seeded variants), `cathedral_mass`,
  `buttress_arc`, `city_cluster`: scenery-scale, no-collision pieces placed by
  a `skyline` list in area data, ringing the playable space at 30–90 m. They
  are base-tagged, so the same skyline burns gold in glory and goes dead
  blue in ruin — the whole kingdom turns with the world.
- **Sunset glory profile** — low warm sun, blazing horizon, long shadows: the
  eternal golden hour the kingdom fell in.
- **Terrace grammar** — balustrades, grand stairs, urns, statue variants: the
  Basilica porch now opens onto an overlook terrace above the lower city.
- **Humanoid silhouette pass** — robe bodies rebuilt with waist/chest/
  shoulder structure, two-segment arms with elbows and pauldrons; painterly
  ramp softened (quantize 0.5 → 0.34) toward painted-fantasy shading.

**Assets are 100 % original.** A request to pull ripped Dark Souls models
(spriters-resource) was declined — those are FromSoftware's copyrighted
assets. The *style* (sunset palatial gothic) is pursued with our own
procedural kit instead.

## D-012 · Verification strategy

- **Visual:** `tools/shot.sh` renders deterministic screenshots (fixed camera paths, both states, key beats) via xvfb + lavapipe; iterated on until the Identity Checklist reads true *in the frame*.
- **Logic:** `tools/sim/` headless tests drive the real game — input-level scripted playthrough of the full pass-1 loop (glory explore → vigil → ruin gauntlet → death/recovery → boss → area B → toggle persistence) plus focused tests (stamina, i-frames, parry, poise, save round-trip, navmesh swap).
- CI-shaped: everything runs from a clean clone with `godot` + `xvfb-run` only.

## D-014 · Skeletal characters, animated in-engine (pass 3)

Node-rigs are retired. Every person in the kingdom — player, foes, the
Chandler, the remembrance ghost, the glory cameo — is now a skinned mesh on
one shared 16-bone humanoid armature (`tools/blender/kit_skel.py`:
hips/spine/chest/head + 3-bone limbs, doll-joint spheres so bends never
tear). Five archetypes ship: hero, ward, penitent (sealed wax cone), giant
(1.55×, drags the great bell), sister.

The split of responsibilities:

- **Blender carries only skeleton + skin.** glTF exports no clips.
- **Clips are authored in Godot** (`SkelAnim`): per-bone euler deltas in
  degrees composed onto the imported rest pose at build time. One table
  set serves every archetype, scaled per-enemy by `anim_amp`/`anim_sway`/
  `stride` in enemies.json. Every clip keys every bone, so cross-fades
  never inherit stale limbs and RESET is trivial.
- **Bone frames were derived, not guessed**: spine bones behave like
  Node3D (−X bows, +Y turns left); limb bones swing forward +X, elbows
  flex +X, knees −X, outward is −Z right / +Z left. The mirror-handed
  label bug (Blender +X had been tagged `_l`) was caught by satchel/shield
  placement in renders and fixed at the source.
- **Gear rides bones** via BoneAttachment3D: weapon in `hand_r` (kit blades
  extend +Y past the fingers — no mount rotation), shield strapped to
  `farm_l`, helms on `head`. Combat timing still lives in data (D-006);
  attack clips are time-scaled to weapon windup/active/recover.
- **Locomotion is measured, not faked**: idle/walk/run cross-fade by ground
  speed, playback rate = speed/stride so feet don't skate; footfalls fire
  at half-cycle boundaries.

`--sandbox=posegrid` renders every clip at its key frames (with `--row=N`
close-ups) for pose sign-off without launching the game.

## D-015 · Area C, puzzles, and the ranged register (pass 4)

The Basilica opens. Three systems joined the data grammar:

- **Puzzles are flags.** `chime_puzzles` (ordered-interact: ring the Vesper
  Chimes in the day's dying order — Prime, Vespers, the Thirteenth — the
  riddle is on a plaque, the wrong note resets the round), `votive_locks`
  (state puzzle: votive stands only take flame in glory; all lit sets the
  flag), and `flag_gates` (any kit piece + blocker that sinks when a world
  flag turns true — iron fences, rubble chokes). Portals already read
  flags, so the great door, the gallery gate and the Sexton's dug aisle
  all ride the same mechanism. Flags persist in the save.
- **Ranged combat.** Attack specs grew `type: ranged | summon` — slow
  glowing versicles (blockable, never parryable, light target lead,
  fan/radial counts) and capped minion summons. `keep_range` makes singers
  back away. The Chorister harasses; the Precentress conducts: triple
  lament, censer sweep, requiem shockwave, and in her half-breath phase a
  radial descant and the call that raises her dead choir.
- **The Nave itself**: aisled vessel with parapeted arcades, a west
  triforium gallery + bridge reached by twin ramped stairs (votive-locked),
  rose window over the chancel, the Unrung Bell hung above the boss floor,
  organ, choir stalls, and the Sexton keeping his bay in both states.
- **Retro charm**: mosaic medallions (new T_mosaic painterly map) inlaid at
  the garth lantern, the porch threshold and the nave crossing; all bells
  and the organ pipes re-skinned in new patina bronze (T_bronze).

The audit script grew overlap-based segment matching (half-offset walls no
longer false-flag) and it caught two real data bugs in the new area before
any human walked it. That is the audit working as designed.

## D-016 · Natural motion + the Undercroft (pass 5)

**Rig naturalization.** The armature gained a neck (17 bones); the rest
pose relaxed (upper arm drifts back, forearm returns — a standing human,
not a mannequin); joint spheres now weight 50/50 across their hinge so
elbows, knees, shoulders and hips deform smoothly instead of doll-balls.
Every animation track interpolates CUBIC, idle grew to a 5.6 s loop with
weight shift and head glances, walk/run gained neck counter-sway and head
stabilization, attacks gained anticipation and overshoot-settle keys, the
roll crouches before it commits. Same data tables, same combat timing.

**The Ossuary Undercroft (Area D)** joins the Cloister (sisters' stair)
and the Nave (sexton's stair) underground — the first three-way link.
Bone grammar: T_bone painterly map, M_bone/M_shroud families, ossuary
skull-shelf walls, bone piles, sarcophagi, shrouded dead, and its own
lantern. The Watchers puzzle (turn the orans statues to face the east
"owed morning" — quarter-turn interacts, plaque riddle) opens the raised
reliquary. Two newcomers: the Shroudbound (fast, low-poise lunger — the
tempo enemy the roster lacked) and Bourdon, the Bell-Ox — a yoked,
bone-masked hulk minibossing the vault where the cracked bell was
stabled: gore charges, yoke swings, slam shockwaves, and a phase-two
stampede.

## D-017 · Playtest fixes: dialogue, camera, collision (pass 6)

Three bugs from live play, each a clean root cause:

- **Dialogue "Leave" cycled.** `close()` re-enabled control the SAME frame the
  interact key was still `just_pressed`, so the player's `_st_move` polled it
  and re-opened the conversation. Fix: talking now puts the Latecomer in a
  real `S.TALK` state (during which `try_interact` — which requires `S.MOVE`
  — cannot fire), and control is restored one frame LATE via a deferred call.
  A `_closing` guard makes `close()` idempotent.
- **Camera "snapped," ignored the mouse.** `lock_on` was bound to MIDDLE
  MOUSE; an accidental middle-click locked onto a target, which snaps the
  camera and makes `mouse_look` early-return — reading as "broken." Fix:
  removed MB3 from `lock_on` (Tab + gamepad remain); a hard mouse flick now
  also breaks any lock. Mouse-look moved to `_input()` (fires before UI, so
  nothing can eat the motion) and capture engages on the first click (a user
  gesture — required by browsers for pointer-lock) as well as at spawn.
- **Player wedged inside props.** `add_collision` only ever built TRIMESH —
  a thin concave shell the capsule can slip inside and jam. Fix: freestanding
  props (statues, urns, columns, sarcophagi, organ, wellhead, chimes, votive
  stands, tombs…) now get a SOLID CONVEX hull; only true architecture with
  openings you pass through (walls, arcades, portals, windows, ossuary walls)
  keeps trimesh. Plus a depth-gated `_unwedge` safety net shoves the body out
  if it ever ends a frame deep inside a collider, and the vigil lantern got a
  proper post collider. Guarded by `fixes_test` (17 checks).

Charm: cobwebs (ruin corners) and hanging iron chains (both states) added as
kit pieces and scattered across all four areas, with denser candle/bone/husk
dressing.

## D-018 · The wrapping horizon + enclosed halls (pass 7)

Playtest note: the boss yard read as open-topped with a see-through barrier
onto empty sky, and the skyline was a sparse ring of floating boxes with
gaps of void between them. Both broke the Anor-Londo illusion.

- **city_panorama** (new backdrop generator): a continuous 360° city
  silhouette built as ONE mesh — four concentric bands of rooftops, gables,
  stepped blocks and spires, height-swelled into "downtown" clusters,
  receding to ~230 m. It fully wraps the horizon so no viewpoint ever sees a
  gap of empty sky. Base-tagged, so it burns gold in glory and goes dead
  blue in ruin — the whole kingdom turns with the world. Placed once per
  open-air area (Cloister garth, Basilica porch), centered, with a few hero
  cathedral/tower/arc silhouettes in the mid-ground for depth. The old
  floating city_cluster boxes are retired.
- **Roofed halls**: a roof-gap audit (floor cells minus vault_fields minus
  roof rows minus the intentionally-open garth) found the belfry boss yard
  and the north garden had no ceiling. Both now carry vault_fields — the
  boss yard at a grand spring of 4.6 m with a clerestory light band. The
  central cloister garth and the Basilica terrace stay open by design (a
  garth and an overlook ARE open-air) — the panorama makes them majestic
  rather than void.
- **The shut tower door**: a new door_leaf (banded oak) closes the Basilica
  portal in the glory layer — "During the Vespers the tower is shut" — so
  the radiant memory ends at a door, not a barrier onto nothing.
