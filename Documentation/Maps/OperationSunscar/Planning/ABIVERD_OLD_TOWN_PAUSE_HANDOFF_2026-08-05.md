# Abiverd Old Town pause handoff — 2026-08-05

## Purpose

This is the restart document for the isolated TacticalMovement map-development
work. It records the verified repository state, completed Old Town and Abiverd
work, known defects, safety constraints, and the agreed next execution order.

The detailed chronological record remains:

- `Documentation/Maps/OperationSunscar/Planning/ABIVERD_VISUAL_CONVERSION_PROGRESS_2026-08-04.md`
- `Documentation/Maps/OperationSunscar/Planning/ABIVERD_HERITAGE_EXPANSION_PLAN_V1.md`

## Verified repository state at pause

- Worktree: `/Users/jasonteck/UnrealEngine/_worktrees/map-development`
- Project: `/Users/jasonteck/UnrealEngine/_worktrees/map-development/TacticalMovement.uproject`
- Branch: `feature/map-development`
- Level: `/Game/Maps/Blockout/Lvl_Blockout_01`
- Checkpoint commit: `dfb9ebfb0dfbbf631bf2d95d0d6e35dbdd114692`
- Checkpoint parent: `483f6e1de7a48e79b2d13e5f17a06a563fc16a0d`
- Remote branch at pause: `origin/feature/map-development` at the same
  `dfb9ebfb0dfbbf631bf2d95d0d6e35dbdd114692` commit.
- Commit title: `Checkpoint Abiverd Old Town terrain and conformance`
- The checkpoint contains exactly 536 map-only files: 436 level external
  actors, six level external objects, 28 Sunscar assets, 58 automation scripts,
  and eight documentation/heightmap-source files.
- Git LFS uploaded 470 Unreal objects totaling approximately 297 MB.
- No committed file exceeded GitHub's 100 MB limit.
- No PR, merge, rebase, squash, force push, branch deletion, or production-main
  update was performed.
- `origin/main` had advanced to
  `bbacc8cc0494d9e1d6a79041a03c152b72edc090`; it was reported but not merged or
  rebased into map development.

The staged-file allowlist used for the checkpoint had SHA-256:

`719a4504aed0797e3a959e3e27272d2cb2faf8650b1bf92bd8536fa380d9ab31`

## Intentionally excluded local files

The following files were explicitly excluded from the checkpoint and must not
be swept into a later broad staging operation:

- `Config/DefaultEditor.ini` — an unintended shared asset-viewer/editor-profile
  serialization, not an authorized map setting.
- `Content/Python/OperationSunscar/AutomationV1/__pycache__/abiverd_wrinkled_tarp_import_post_audit_v1.cpython-314.pyc`
- `Content/Python/OperationSunscar/AutomationV1/__pycache__/abiverd_wrinkled_tarp_import_v1.cpython-314.pyc`

The two `.pyc` files are generated cache artifacts. The config change remains
local and uncommitted; do not restore, delete, or commit it without explicit
direction.

## Protected boundaries preserved

- No production movement, custom CMC, saved-move/network prediction, readiness
  replication, movement-profile, first-person rendering, Infima weapon,
  animation, weapon, or gameplay-source work was included.
- `/Game/ThirdPerson/Lvl_ThirdPerson` was not overwritten or modified.
- The project default startup map and `DefaultEngine.ini` were not changed.
- Diagnostic and movement worktrees were not opened, modified, cleaned,
  switched, reset, committed, or pushed by this map checkpoint.

## Completed environment foundation

### Original isolated blockout

- Created the new World Partition level at
  `/Game/Maps/Blockout/Lvl_Blockout_01` instead of modifying the Third Person
  level.
- Established the enlarged Old Town combat layout, districts, roads, compounds,
  checkpoints, objectives, landmarks, exterior cover and initial labels.
- Preserved the tested building shells as the principal gameplay and collision
  authority while visual conversion proceeded around them.

### Landscape visual conversion

- Replaced the visible overlapping ground-tile presentation with a real
  2017 x 2017 Landscape material/layer workflow.
- Established deterministic authored coverage for arid sand, compacted earth,
  weathered asphalt, stone hardstand, roadside silt and seasonal Abiverd meadow.
- Hid obsolete planning/debug visual-ground actors where appropriate rather
  than using them as the continuous terrain surface.
- Rebuilt the four Landscape streaming proxies that requested physical-material
  maintenance. The subsequent Map Check completed with zero errors and zero
  warnings.

### Landscape relief V1

- Replaced the physically flat terrain with a real 2017 x 2017 UE 5.8
  Landscape height pass using a lossless RG16 transfer.
- Corrected the initial north/south orientation after a read-only audit showed
  the first foundation masks were mirrored.
- Added broad alluvial variation, low settlement mounds and shallow dry
  drainage forms while fading back into the authored outer terrain.
- Verified all 12 first-floor slab bottoms against the Landscape. The largest
  absolute support mismatch was 0.974 cm.
- A 195-point Old Town sample measured 32386.774–35687.894 cm: 33.0112 m of
  real terrain range.
- Saved exactly the 16 audited Landscape streaming-proxy packages.
- Preserved the rollback source at
  `Documentation/Maps/OperationSunscar/Source/Heightmaps/Sunscar_Height_2017_BaseBackup.png`.
- Final heightmap sources, previews and reports are under
  `Documentation/Maps/OperationSunscar/Source/Heightmaps`.
- The rejected temporary mesh/sphere terrain experiment was never saved.

### Ground-surface conversion and conformance

- Imported and configured the owned Quixel Historic Desert Ruin Floor Sand
  Coarse 01 source in the map-owned heritage tree.
- Reused that source for the existing `RoadsideSilt` Landscape regions at a
  verified 120 cm world-space scale without adding a redundant Landscape layer.
- Conformed exactly 288 existing road, courtyard and localized ground-overlay
  actors to the saved Landscape.
- All 288 conforming overlays use 0.8 cm visual thickness and `NoCollision`;
  the Landscape remains physical collision authority.
- Exact-saved only those 288 external-actor packages with the guarded utility
  `old_town_save_ground_overlay_conformance_v1.py`.
- The post-save audit verified 288 actors, 288 with collision disabled, zero
  dirty Unreal packages and no unexpected package.
- Authoritative local reports:
  `Saved/OperationSunscar/Reports/old_town_ground_overlay_conformance_apply_preview_v1.json`,
  `Saved/OperationSunscar/Reports/old_town_ground_overlay_conformance_audit_v1.json`,
  and
  `Saved/OperationSunscar/Reports/old_town_save_ground_overlay_conformance_v1.json`.

## Completed architecture and exterior conversion

### Structural skin

- Converted 111 building surfaces across 190 building actors to the first
  cohesive mud-brick, plaster, civic and industrial hierarchy.
- Added 76 structural-detail actors for foundation skirts, parapets,
  buttresses and restrained erosion dressing.
- Preserved the gameplay shells and their existing openings.

### Historic facade sources

- Imported and configured Historic Desert Ruin Wall Modular Set 04 and used 75
  non-colliding HISM facade instances across 25 uninterrupted P0 wall spans.
- Corrected the scan's source-axis orientation in place; no duplicate facade
  system remains.
- Imported Historic Pakistan Street Wall Brick Modular 16 as a map-owned,
  Nanite-enabled civic wall source with packed ORM and a 2K runtime texture cap.
- Added nine non-colliding HISM instances across the Clinic, Detention Annex and
  Consulate blank wall spans.
- Imported Historic Pakistan Street Window Brick Modular 04, but rejected its
  use as an opening insert after visual review showed that the complete 3.48 m
  wall bay appeared as an attached slab. All 14 unsuitable instances were
  removed and the original 28 opening cues were restored.
- The Pakistan window source remains available only for a future compatible
  complete wall-bay rebuild.

### Openings, roofs and wall transitions

- Removed 28 superseded offset prototype parapets only where complete replacement
  roof-parapet systems existed. This corrected the apparent floating-beam issue
  on seven reviewed sites.
- Added one shared warm world-aligned Consulate plaster material and applied it
  to exactly ten exterior shell pieces.
- Added the opening-surround system to nine verified doors and five open shell
  passages using 42 non-colliding HISM pieces.
- Hid two false Hotel door props that were positioned against solid walls.
- Converted 40 window recesses to a shared opaque dusty-recess treatment and
  set all 80 decorative frame/recess actors to `NoCollision`.
- Added 80 shallow lintel/sill pieces through one non-replicated two-component
  HISM actor.
- Added 167 terrain-conformed wall-foot rubble/grass instances at eight reviewed
  Old Town sites through six HISM components. Door clearance, collision,
  navigation, culling and shadow policies were audited.
- Replaced the Covered Bazaar's eight graybox canopy slabs with the owned Quixel
  Wrinkled Tarp source while preserving authored centres, a 273.092 cm minimum
  underside clearance and a 918.096 cm central passage.

## Completed Abiverd identity pass

- Added the first Juma-mosque ruin composition, archaeology walls, well court,
  eroded wall fragments and heritage landmarks.
- Added 4,200 deterministic poppy instances and 2,400 grass instances through
  one HISM vegetation actor with 16 components.
- Vegetation is non-colliding, non-replicated, does not affect navigation, and
  uses distance-culling/shadow policy suitable for a multiplayer environment.
- The heritage plan protects North Defender Insertion, requires at least three
  readable routes and does not treat vegetation as authoritative ballistic
  cover.
- The map consistently uses the spelling **Abiverd**.

## Imported and verified owned sources

The map/project or local Fab source library contains the following verified
families used or reserved for Old Town and Abiverd:

- Historic Desert Ruin Arch Stone Carved 08
- Historic Desert Ruin Wall Modular Set 04
- Historic Desert Ruin Structure Stone S 06
- Historic Desert Ruin Wall Brick 03 surface
- Historic Desert Ruin Floor Sand Coarse 01 surface
- Historic Pakistan Street Wall Brick White 01 surface
- Historic Pakistan Street Wall Brick Modular 16
- Historic Pakistan Street Window Brick Modular 04
- Cracked Mud Wall
- Field Poppy and selected Wild Grass/Dry Grass families
- Quixel Wrinkled Tarp
- Approved Epic/Quixel military trench, junkyard, vehicle and environmental
  sources already included in the map-owned dependency closure

## Performance-oriented implementation already used

- World Partition external actors and external objects for the map.
- Map-owned lightweight material masters and material instances.
- Packed ORM textures and runtime texture-resolution caps where appropriate.
- Nanite on suitable dense opaque heritage scans; not automatically enabled on
  lightweight masked foliage cards.
- HISM batching for repeated facade pieces, vegetation, opening trim and
  wall-foot dressing.
- Decorative actors use no replication, no ticking, no navigation influence
  and usually no collision.
- Tested building shells remain collision authority instead of decorative
  scans using complex collision.
- Runtime PCG generation is not planned. Vegetation generation should be
  deterministic and baked to instancing output.

## Known defects and incomplete work

### Four overlay edge-fit reviews

The saved conformance is stable, but four large overlay pieces exceed the
18 cm edge-gap review threshold and need subdivision or localized refitting:

| Actor | Maximum audited edge gap |
|---|---:|
| `Ground_Asphalt_SS_019_R1C1` | 18.693 cm |
| `Ground_Asphalt_SS_019_R1C2` | 19.861 cm |
| `Ground_Concrete_SS_009_R2C1` | 30.120 cm |
| `NorthRoute_04_02` | 19.906 cm |

`Ground_Concrete_SS_009_R2C1` is the priority. These actors are decorative and
non-colliding, so the issue is visual rather than a physical traversal defect.

### Ground material

- The Landscape is structurally real and no longer physically flat, but its
  ground material will still benefit from later macro-scale color/roughness and
  distance-aware refinement.
- **The first production cell-bombing pass is implemented, visually approved
  and saved** in
  `/Game/Maps/Sunscar/Art/Materials/LandscapeV3/M_OT_Landscape_Abiverd`.
- It reuses UE 5.8's built-in
  `/Engine/Functions/Engine_MaterialFunctions01/Texturing/Texture_Bombing`
  material function. No custom bombing function was created.
- Bombing is intentionally limited to the dominant Sand base-color path. It
  preserves the existing world-space scale, uses a 1.0 tiling multiplier and
  0.75 offset, and does not add normal-map bombing or height lerp.
- Measured material cost changed from 121 to 192 pixel instructions and from 6
  to 9 pixel texture samples. Vertex instructions remain 99 and sampler count
  remains 4. This passed the bounded preview ceilings, but representative
  runtime/GPU profiling remains required before final art lock.
- The preview eliminated 50 unreachable legacy material expressions; the saved
  graph contains 83 expressions, all reachable from active material outputs.
- The continuous Landscape material should carry the broad surface; overlays,
  decals and mesh patches should remain localized detail only.

### Architecture and gameplay-art review

- The environment is a first structural-art draft, not a finished art pass.
- Tea House and Hotel shade/balcony language, district silhouette variation,
  cornices, selected compatible full wall bays and site-specific facade detail
  remain incomplete.
- Door/window readability, roof-parapet collision, Hotel silhouette and
  wall-foot visibility still require player-height PIE review.
- The mosque and ruins need a composition/sightline review before more ruin
  fragments are added.
- Vegetation density must be tested at the lowest supported scalability setting
  so no route depends on flowers or grass as its only protection.
- Small props, debris, decals, localized storytelling, final roads and final
  exterior dressing remain later passes.

## Stability lessons and required automation procedure

- Do not launch the editor with a persistent `-ExecutePythonScript` review
  helper or `set_keep_python_script_alive(True)`. Persistent Python execution
  repeatedly destabilized the editor.
- Use a normal editor launch and one-shot bounded scripts only.
- Prefer the following sequence for every material or actor batch:
  1. read-only preflight;
  2. bounded dry run or unsaved preview;
  3. visual and automated audit;
  4. explicit apply authorization;
  5. post-apply audit;
  6. exact-package save;
  7. Git scope audit and separately authorized checkpoint.
- Avoid monolithic scripts and large unsaved batches.
- Epic Games Launcher crash-reporter popups observed during earlier asset work
  were separate from the isolated TacticalMovement editor process.

## Agreed restart sequence

1. Reverify the map-development worktree, branch, current commit and current
   Unreal dirty state. Do not rebase onto the advanced `origin/main`.
2. Review the saved Landscape relief from annotated aerial and player-height
   views. Make only localized, non-destructive terrain refinements needed for
   routes, pads, drainage and sightline interruption.
3. Build the production Landscape ground-material pass, explicitly including
   world-space scale, macro variation and benchmarked cell bombing/stochastic
   variation.
4. Subdivide/refit the four flagged overlays, then re-audit roads, pads,
   building support and existing exterior actors against the final terrain.
5. Continue coherent architecture conversion in priority order: major combat
   lanes, Bazaar/Hotel, civic sites, residential compounds, perimeter structures
   and secondary utility buildings.
6. Complete doors, windows, roofs, parapets, tarps, awnings, utilities, fences,
   gates and ground transitions.
7. Review and expand the mosque/Abiverd ruins and vegetation concealment network
   without compromising spawn protection or lowest-density sightlines.
8. Add secondary props, debris, decals and storytelling after the primary
   composition is stable.
9. Run player-height PIE, collision, rooftop, sightline, traversal, shader,
   foliage, World Partition, HLOD and representative multiplayer-performance
   validation.
10. Produce high-resolution labelled and unlabelled review images, update this
    documentation and request a separate Git-checkpoint authorization.

## User review checkpoints

For efficient review, provide the user with:

- one high-resolution top-down image;
- four oblique aerial views;
- player-height views of major routes and landmarks;
- labelled and unlabelled variants;
- explicit questions about exposed routes, ridge placement, landmark position,
  historic character, entrance readability and vegetation concealment.

The user should approve large-scale composition, sightlines, landmarks and
atmosphere. Systematic micro-placement can remain automated and audited.

## Pause state

- The last verified Unreal state showed `All Saved` after saving exactly
  `M_OT_Landscape_Abiverd`. The log recorded
  `ABIVERD_EXACT_MATERIAL_SAVE True`.
- The post-save read-only audit found zero dirty packages and reconfirmed the
  saved 83-expression graph and 99/192 vertex/pixel instruction counts.
- The Landscape bombing work used a read-only preflight followed by one bounded
  unsaved preview, player-height visual review, cost/scope audit and exact-asset
  save. Unreal did not crash during this workflow.
- Added local map-only automation helpers:
  - `abiverd_landscape_cell_bombing_preflight_v1.py`
  - `abiverd_landscape_texture_bombing_preview_v1.py`
- Fixed `old_town_focus_exterior_completion_review_v1.py` so the camera-only
  helper also works when invoked through Unreal's `py exec(open(...).read())`,
  where `__file__` is not defined.
- Generated reports remain under
  `Saved/OperationSunscar/Reports/` and are not repository assets.
- No map actor, level, movement, animation, weapon, readiness, production config
  or protected gameplay asset was changed during this material pass.
- The next map work is: refit the four flagged ground-overlay edges, then resume
  Old Town exterior conversion using the already owned Quixel/Epic asset set.
- Current repository checkpoint remains
  `dfb9ebfb0dfbbf631bf2d95d0d6e35dbdd114692`; this material change, automation
  scripts and handoff update are local/uncommitted pending separate checkpoint
  authorization.
- `Config/DefaultEditor.ini` and the two Python `__pycache__` files remain
  intentionally excluded from map checkpoint scope.
- This handoff document was created after that checkpoint and is intentionally
  local/uncommitted until separate Git authorization is provided.
