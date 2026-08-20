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

- The environment is now a coherent first exterior art/design draft, not a
  final production-art pass. The bounded building-shell and grounded-exterior
  phase was completed on 2026-08-14; future work should treat vegetation,
  localized ground color, decals/storytelling and final lighting/composition as
  the next visible-quality categories rather than reopening every building.
- Tea House, Hotel, Bazaar, Motor Pool, Water Tower, Canal Pump Station,
  Freight Depot, Power Substation and Telecom Workshop now have reviewed
  exterior treatments. Final hero-asset replacement, bespoke cornices and
  selected complete wall-bay rebuilds remain optional later polish, not a
  blocker for proceeding to the next map category.
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
- Verified 2026-08-14: every master material rendered by an ISM or HISM must
  have **Used with Instanced Static Meshes** enabled and compiled before actor
  placement. `M_ABV_Foliage_Masked` had valid mesh instances, texture
  parameters and component settings, but rendered as dark/default cards while
  `used_with_instanced_static_meshes` was false because the required instanced
  vertex-factory shader permutation was unavailable. Recreating actors does not
  fix that material-level defect.
- Preflight the parent master material, not only its material instances and
  meshes. Verify `used_with_instanced_static_meshes == true`, apply/compile the
  material, save only that exact package, then independently read the saved
  property back and require zero dirty packages. Do not rely on
  `automatically_set_usage_in_editor`; it was true on this material while the
  required usage flag was still persisted false.
- After changing an instancing usage flag, validate a known existing HISM or a
  single unsaved preview instance before creating a full batch. Confirm that it
  no longer uses the default/dark fallback material and that the intended
  masked texture renders. This rule applies to `M_ABV_Foliage_Masked` and every
  future material used by ISM/HISM vegetation or repeated map geometry.
- The same 2026-08-14 validation found a second independent foliage-material
  defect. The imported Quixel mask packing is `R = Opacity`, `G = Roughness`,
  `B = Translucency`. Never route `Mask.B` to Opacity Mask: doing so exposes
  brown card/background fragments that can be mistaken for broken dirt below
  the plants. The exported opacity data occupies only approximately 0.0-0.31,
  so the prior 0.42 clip discarded the cards completely. The calibrated map-
  owned master uses `Mask.R` with an opacity-mask clip of 0.20; 0.10 admits
  excess antialiased fringe, while 0.20 preserves the authored silhouettes.
  Retain **Used with Instanced Static Meshes**, compile with zero errors, and
  validate both a player-height and elevated HISM capture before saving.
- For the field-edge pilot, `SM_WildGrass_VarE` is an approximately 18 cm low
  radial clump and reads as ground litter when used as the primary filler.
  `SM_WildGrass_VarA`, uniformly scaled to roughly 48-62 cm, is the validated
  tall meadow filler. A 16 m by 7 m reference-density pilot uses one actor,
  two HISM components, 960 poppies and 1,440 grass instances, with a 1.2 m
  movement corridor, 1.5 m static-geometry clearance, Landscape-only support,
  no collision/nav/overlaps/shadows/replication/tick, and 80-240 m culling.
- The remaining bare-dirt read under this pilot is not a foliage-card defect.
  Nine exact player-patch samples resolve to `LandscapeComponent_136` on
  `LandscapeStreamingProxy_2_2_0`, external-actor package
  `/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/7/PW/GCKDH3SJ6DMPX8ALJXPIKR`,
  and every sample returns `Grass` paint weight `0.0`. The saved Landscape
  material already contains the `Grass` / `AbiverdSpringMeadow` layer using
  the imported Wild Grass Ground base color and normal; the problem is local
  layer coverage, not a missing texture or material input.
- UE 5.8 exposes a safe read path for this diagnosis: trace to the
  `LandscapeHeightfieldCollisionComponent`, call `get_render_component()`,
  then call `editor_get_paint_layer_weight_by_name_at_location(Location,
  "Grass")`. For preservation, `Landscape.render_weightmap()` can export the
  existing proxy window before any edit. The validated proxy window is
  505x505 pixels covering world XY 0-63000 cm at 125 cm/pixel; exported pixel
  Y maps directly to world +Y. Never generate a replacement mask from zero or
  use a full-map import for this pilot.
- A proposed localized correction mask preserves the exported proxy weights
  and changes only 60 pixels around the 16x7 m meadow footprint, with feathered
  edges, peak Grass weight about 0.68, and a reduced-weight central trampled
  strip. Do **not** apply it through
  `LandscapeStreamingProxy.landscape_import_weightmap_from_render_target()`.
  A guarded 2026-08-14 preview proved that UE 5.8 requires a full 2017x2017
  Landscape render target even when the function is called on one streaming
  proxy; the call then dirtied all 16 loaded Landscape proxy packages while
  leaving the nine sampled pilot weights at `0.0`. No package was saved: all
  16 unsaved proxy packages were reloaded from disk and authoritative dirty
  state returned to zero. This is a proven wrong-scope import path, not a
  retryable transient failure. Use the native Landscape Paint tool for a
  localized Grass stroke and require the authoritative dirty scope to be
  exactly the proxy package above before saving; discard on any parent,
  material, other proxy, or mass-resave scope.
- Verified native-paint resolution on 2026-08-14: select the `Grass` target
  layer, set Painting Restriction to `None`, and use a bounded brush (strength
  0.22, size 800 cm, falloff 0.5). For deterministic single-dab automation,
  `Apply Without Moving` must be enabled; an instantaneous click otherwise
  produces no sample. Also re-check Painting Restriction after keyboard focus
  changes: an `End` key sent while that dropdown had focus changed it to
  `Component Allow List`, silently preventing the intended unrestricted
  stroke. The successful center dab changed only
  `LandscapeStreamingProxy_2_2_0` package
  `/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/7/PW/GCKDH3SJ6DMPX8ALJXPIKR`.
  Seven direct pre-save samples across the pilot returned Grass weights
  0.42745-0.75137 on `LandscapeComponent_136`. Leave active Paint mode (Manage
  is sufficient) before the exact save; otherwise the active paint tool can
  mark the proxy dirty again immediately after a successful write. The final
  exact proxy save remained clean, and nine post-save samples returned
  0.14118-0.75137 with authoritative Unreal dirty state still zero. Do not
  repeat the full render-target import now that the native-paint path is
  proven.
- Player-height review exposed an important visual limitation: the imported
  `Wild Grass Ground` base color used by the `Grass` Landscape branch reads
  tan/olive under the current lighting. Increasing the localized paint weights
  makes the blend measurable and somewhat greener, but it does not by itself
  create a lush seasonal meadow floor. After the bounded strengthening pass,
  the nine saved samples span 0.14118-0.89020 and only the intended
  `LandscapeStreamingProxy_2_2_0` package changed. Treat further repeated
  strokes as diminishing returns; a separately scoped material-selection or
  color-treatment decision is required if a substantially greener ground read
  is desired. Do not misdiagnose this as missing paint.
- Map-owned HISM actors created or structurally changed through editor Python
  may not build a render tree until their exact external-actor package is
  serialized and reloaded. Keep the actor root at the patch center and store
  instances relative to that local origin so World Partition bounds remain
  tight. For the field-edge pilot, unsaved bounds were a default 128 cm box;
  exact save/reload produced verified bounds of about 13.98 m by 6.87 m by
  2.99 m and activated both render components. Never leave a vegetation actor
  rooted at world origin with distant world-space instances.
- Exterior continuation on 2026-08-14 completed the first priority Hotel and
  Bazaar prototype-cue cleanup without changing either building shell. All 30
  `Hotel_F*_..._Glass` actors now use the already-approved
  `MI_OT_DustyWindowRecess` and have `NoCollision`; their timber frames and
  complete transforms are unchanged. The two cyan Hotel sign backings now use
  `MI_OT_Timber`, while `Hotel_Balcony_Rail` retains its authored transform and
  gameplay collision but uses `MI_ABV_CrackedMud_WorldAligned` as a repaired
  earthen civic parapet. The eight `Bazaar_[N/S]_Sign_*` backings likewise use
  timber and `NoCollision`; the verified Quixel cloth canopies and stall
  collision remain unchanged.
- The Hotel balcony shade pass reuses the existing Nanite Quixel wrinkled-tarp
  mesh at uniform scale 1.4 in three map-owned actors:
  `ABV_SS_007_HotelBalconyShade_West_V1`, `..._Center_V1` and `..._East_V1`.
  Their contiguous combined coverage stays within the authored balcony width,
  meets the facade within approximately 15.8 cm and preserves approximately
  251.9 cm clear height above the balcony deck. They have no collision,
  navigation, overlap events, replication or tick. Each actor serialized to
  exactly one external-actor package because the existing Municipal Hotel
  folder was reused.
- Four small Structure Stone S 06 fragments now dress the Hotel perimeter:
  `ABV_SS_007_GroundRubble_SouthWest_V1`, `..._NorthEast_V1`, `..._West_V1`
  and `..._East_V1`. Each fixed placement traced directly to a Landscape
  streaming proxy, is embedded exactly 3 cm, uses uniform scale 0.85-1.05 and
  has no collision/navigation/overlaps/replication/tick. They remain clear of
  the real south door, east opening and west access ramp. No Landscape or
  existing actor transform changed.
- The final held industrial shells were completed in four exact save batches.
  Eight `SS_003` Canal Pump Station walls and seven `SS_013` Freight Depot
  walls use `MI_OT_FlakedPaint_WorldAligned`; six `SS_016` Power Substation
  exterior wall panels now use `MI_OT_FlakedPaint_WorldAligned` and its two
  entrance lintels use `MI_OT_Metal`; and fourteen `SS_018` Telecom Workshop
  walls use `MI_OT_Stucco_WorldAligned`. The original bright Substation
  `MI_OT_WallPaint_WorldAligned` rollout was rejected during the second-pass
  player-height review because it read as sterile white blockout. Transforms,
  openings, collision, floors, roofs and traversal remained unchanged. The
  post-pass generic-shell audit returned zero remaining actors and zero dirty
  packages.
- Seven Motor Pool exterior shell actors now use
  `MI_OT_FlakedPaint_WorldAligned`, preserving the garage opening and all
  transforms/collision. The Water Tower received eight non-colliding,
  non-navigable steel cross braces plus a stucco finish on
  `Core_SS_006_TowerPillar`, making its structural silhouette readable without
  altering the four authoritative legs, tank or gameplay collision.
- `CoreWall_SouthSpawnSightbreak` remains the same authoritative tactical wall
  with the same transform and `QueryAndPhysics` collision, but its generic pale
  stone finish was replaced by `MI_ABV_RuinBrick_WorldAligned`. It now reads as
  Abiverd masonry instead of an unexplained white block in the Telecom approach.
- The final visual audit confirmed that the thin roofline rods around `SS_016`
  and `SS_018` are grounded or roof-supported utilities whose lower sections
  are merely occluded in the reviewed views; they were not moved. Previously
  verified wall-foot, scatter, furniture, storage/scrap, market-debris,
  sandbag, Hotel-rubble and SS_013 ruin systems retain their reviewed support
  state. No new grounded-transform defect was proven in the changed sites.
- Final review captures for this checkpoint are:
  `/private/tmp/abv_water_tower_after_player_v2.png`,
  `/private/tmp/abv_motor_pool_after_player.png`,
  `/private/tmp/abv_ss003_after_shell.png`,
  `/private/tmp/abv_ss013_after_shell.png`,
  `/private/tmp/abv_ss016_after_shell.png`,
  `/private/tmp/abv_ss018_after_sightbreak.png` and
  `/private/tmp/abv_old_town_exterior_final_aerial.png`.
- The second exterior-detail pass replaced the Freight Depot loading-bay cube
  on the existing `Depot_LoadingDoor` actor with the already owned Nanite
  Quixel corrugated-metal wall mesh. Its corrected 500 x 18 x 280 cm bounds
  remain exactly fitted to the authored opening, retain `QueryAndPhysics`
  collision, and now read as a deliberately sandbagged/corrugated loading-bay
  barricade. Only its existing external-actor package
  `7/MJ/BPRA9ZMO6G6ULKIKT925U3.uasset` was saved.
- Five owned Quixel wrinkled-tarp entrance awnings were added at the two Canal
  Pump Station doors, Freight Depot pedestrian door, Power Substation west
  entrance and Telecom Workshop entrance. Every awning is uniformly scaled,
  has approximately 80-90 cm clearance above its opening, meets the facade
  within approximately 10-15 cm, and has no collision, navigation, overlaps,
  replication or tick.
- Three owned Nanite Quixel electrical-box meshes now provide restrained
  facade detail at `SS_003`, `SS_016` and `SS_018`:
  `ABV_SS_003_PumpSouthElectricalBox_V1`,
  `ABV_SS_016_SubstationWestElectricalBox_V1` and
  `ABV_SS_018_TelecomSouthElectricalBox_V1`. They are shallow wall-mounted
  props with 386-449 cm clearance from the nearest opening, no collision or
  navigation, and use the established muted `MI_OT_Accent` finish so they read
  as intentional industrial equipment rather than white editor markers.
- A proposed eight-instance `Wall Modular Set 04` facade-depth batch was
  rejected and fully rolled back before final acceptance. The inherited
  `roll=90` transform assumption used the wrong asset axis/pivot and produced
  elevated L-shaped pieces. The existing HISM count was restored from 83 to 75,
  the exact package was re-saved with zero dirty packages, and no rejected
  instance remains. Future use of this heritage wall asset must validate one
  temporary instance's world bounds and visual orientation before any repeated
  placement; do not reuse that roll/pivot assumption blindly.
- Second-pass player-height review captures are:
  `/private/tmp/abv_ss013_loadingdoor_close_before.png`,
  `/private/tmp/abv_ss013_loadingdoor_close_after.png`,
  `/private/tmp/abv_ss003_detail_final.png`,
  `/private/tmp/abv_ss016_detail_final.png` and
  `/private/tmp/abv_ss018_accent_final.png`.
- UE 5.8 Python does not expose
  `StaticMeshComponent.set_generate_overlap_events()`. For map-owned static
  mesh actors, use
  `component.set_editor_property("generate_overlap_events", False)` and read
  the property back when overlap suppression is part of the performance gate.
  A method-name failure can leave the just-spawned actor dirty in memory; reuse
  and complete that exact actor only after proving its actor package is the sole
  dirty package, rather than spawning a duplicate.
- UE 5.8 Python also does not expose
  `StaticMeshComponent.set_can_ever_affect_navigation()`. Use
  `component.set_editor_property("can_ever_affect_navigation", False)` and read
  that property back. A method-name exception after spawning can leave the
  actor package dirty; recover and finish the exact actor instead of spawning a
  duplicate.
- `component.set_collision_enabled(NO_COLLISION)` alone is not a sufficient
  postcondition for newly spawned map actors when a collision profile remains
  active. For a decorative actor, set actor collision disabled, set the
  component profile to `NoCollision`, set collision enabled to
  `NO_COLLISION`, then verify `get_collision_enabled()` returns `NO_COLLISION`.
  `collision_profile_name` is not readable through `get_editor_property()` in
  this UE 5.8 Python build; use the supported profile setter and verify the
  effective collision mode instead.
- Epic Games Launcher crash-reporter popups observed during earlier asset work
  were separate from the isolated TacticalMovement editor process.

## 2026-08-14 all-building exterior completion checkpoint

- The authorized Old Town exterior first-art/design-draft pass is complete for
  all 13 building sites: `SS_003`, `SS_004`, `SS_005`, `SS_006`, `SS_007`,
  `SS_010`, `SS_011`, `SS_012`, `SS_013`, `SS_015`, `SS_016`, `SS_017` and
  `SS_018`. This means every site has a reviewed exterior shell or, for the
  `SS_006` water-tower landmark, a completed structural/detail treatment. It
  does not claim final-production decal, lighting, HLOD or multiplayer
  performance polish.
- The live completion matrix found zero generic materials on core building
  surfaces and nonzero exterior-detail coverage at every site. Core-building
  actor counts are 10/10/15/0/22/17/17/15/9/9/10/12/17 in site order above;
  `SS_006` intentionally has no conventional core roof/wall shell because it is
  the water-tower utility landmark.
- Four additional owned Quixel wrinkled-tarp entrance awnings complete the
  cross-site entrance-readability pass:
  `ABV_SS_005_ClinicMainAwning_V1`,
  `ABV_SS_011_CheckpointDoorAwning_V1`,
  `ABV_SS_012_ConsulateDoorAwning_A_V1` and
  `ABV_SS_012_ConsulateDoorAwning_B_V1`. Together with the five earlier
  industrial awnings, the verified total is nine. All are non-colliding and
  non-navigable and preserve at least approximately 82 cm clearance above the
  authored openings.
- The placeholder cube meters `OT_EXT_Meter_SS_004`,
  `OT_EXT_Meter_SS_010` and `OT_EXT_Meter_SS_012` now reuse the owned Nanite
  Quixel `Electric_Box_ullibjd_High` mesh with `MI_OT_Accent`, no collision and
  no navigation relevance. Together with the three earlier industrial
  electrical boxes, six exact utility-detail actors passed acceptance.
- The final proven building defect was the pair of `SS_015` Motor Pool garage
  panels. `MotorPool_Garage_A` and `MotorPool_Garage_B` were 400 x 18 x 350 cm
  cubes whose bottoms sat 175 cm above the south-wall bottom and whose tops
  extended 225 cm above that wall. They now reuse the owned Nanite Quixel
  corrugated-metal mesh, retain `QueryAndPhysics` collision, and fit exact
  400 x 18 x 300 cm facade bounds from Z 34794.1 to 35094.1. The supporting
  wall and all gameplay alignment remained unchanged.
- Final acceptance report:
  `/private/tmp/abv_all_buildings_final_acceptance_v1.json`. It verified the
  exact project/map, 13 sites, zero Unreal dirty packages, nine awnings, six
  utility details, both corrected Motor Pool panels, 75 heritage facade HISM
  instances, 288 hidden legacy overlays and 26 current review images.
- The 26 player-height/aerial review images and manifest are under
  `/private/tmp/abv_all_buildings_review_v1/`. The final `SS_015` player and
  aerial images were refreshed after the garage correction. Close custom
  captures that appeared to omit walls were rejected as camera clipping; the
  matrix-view recaptures proved the facade shells intact.
- The four old overlay-edge findings remain closed as stale/invalid. All 288
  `SunscarVisualConversionHiddenV2`/`VisualGroundOverlay` actors are still
  hidden and untouched, and the former cube-pivot audit assumption must not be
  reused.
- Unreal ended with authoritative zero dirty packages. Git is intentionally
  unstaged at 134 modified files plus 34 untracked files, with zero files
  outside the approved map external actor/object packages, the approved
  `M_ABV_Foliage_Masked` material and this handoff document. Local and remote
  `feature/map-development` remain
  `e0b856c20cdad11f7057248c851d4d344f43fbe1`; no commit, push, merge or rebase
  was performed.
- The next visible-quality category should be ground integration and restrained
  seasonal vegetation expansion around the now-stable building composition,
  followed by roads/edges, decals/storytelling and final lighting/performance
  validation. Do not reopen systematic building-shell conversion unless a new
  player-height defect is specifically proven.

## 2026-08-14 initial-launch playable-area building re-audit

- The building-completion claim is intentionally limited to the initial-launch
  playable area. Its exact 13-site scope is `SS_003`, `SS_004`, `SS_005`,
  `SS_006`, `SS_007`, `SS_010`, `SS_011`, `SS_012`, `SS_013`, `SS_015`,
  `SS_016`, `SS_017` and `SS_018`. It does **not** claim completion of the
  outer/future districts or every building planned for the full map.
- A stricter second pass reviewed the launch-area exteriors from west, east and
  north player-height approaches (36 new captures), reran exact-tag shell and
  detail coverage, and sampled all four building sides against authoritative
  terrain/support geometry. The final ground-contact matrix returned zero
  flagged sites and Unreal ended with zero authoritative dirty packages.
- The stricter pass found and corrected two previously missed, player-visible
  support gaps on the rear/north and east edges of the `SS_010` detention-yard
  terrace. They are now closed by the map-owned, colliding masonry plinth actors
  `ABV_SS_010_DetentionTerrace_FoundationSkirt_North_V1` and
  `ABV_SS_010_DetentionTerrace_FoundationSkirt_East_V1`; no Landscape or
  building transform changed.
- The `SS_006` water-tower landmark received the final launch-area exterior
  upgrade: `WaterTower_Tank` now uses the already owned Quixel
  `Metal_Water_Tank_wdklears_High` mesh and its source material at uniform
  scale 4.5, and the four existing tower legs were shortened to meet the new
  tank cleanly. Their original bases, XY placement and collision were
  preserved.
- Final acceptance is recorded in
  `/private/tmp/abv_launch_buildings_final_acceptance_v2.json`; the strict
  ground-contact report is
  `/private/tmp/abv_launch_building_ground_contact_matrix_v2.json`; the 36
  approach images are in `/private/tmp/abv_launch_approach_review_v1/`.
- This is a verified **first-art/design-draft exterior completion gate** for
  the launch buildings: shells, openings, roof/parapet treatment, visible
  support/contact and primary exterior details are ready for the next outside
  category. It is not final-production decal, storytelling, lighting, HLOD or
  multiplayer-performance polish.
- After this checkpoint Git remains intentionally unstaged at 139 modified
  files plus 36 untracked files, with nothing staged. Scope remains limited to
  map external actor/object packages, the approved
  `M_ABV_Foliage_Masked` material and this handoff document. Local and remote
  `feature/map-development` both remain
  `e0b856c20cdad11f7057248c851d4d344f43fbe1`; no commit, push, merge or rebase
  was performed.
- Do not resume systematic building conversion in the outer districts during
  the initial-launch pass. The next launch-area outside work should be roads
  and ground transitions, followed by seasonal grass/flower integration,
  exterior props/decals/storytelling, then lighting, HLOD and representative
  performance validation.

## 2026-08-15 launch-area building exterior closeout

- The closeout remains limited to the initial-launch playable-area buildings:
  `SS_003`, `SS_004`, `SS_005`, `SS_006`, `SS_007`, `SS_010`, `SS_011`,
  `SS_012`, `SS_013`, `SS_015`, `SS_016`, `SS_017` and `SS_018`. It does not
  claim that future/outer-district buildings are finished.
- The 75-instance `ABV_OldTown_FacadeScan_HISM_V4` treatment was re-audited
  against the actual `Historic Desert Ruin Wall Modular Set 04` mesh. The
  asset is an L-shaped ruin fragment, not a flat facade panel. All 75 repeated
  instances produced oversized hook silhouettes and were removed from the
  HISM in reviewed batches. The exact HISM actor package was saved with an
  authoritative final instance count of zero; the actor remains available but
  empty. Do not repopulate this component unless one temporary instance first
  proves the mesh axis, pivot, world bounds and intended architectural role.
- The weak opening-free launch facades at `SS_003`, `SS_013`, `SS_015`,
  `SS_016` and `SS_017` first received one grounded masonry bay pier each by
  reusing the established `ABV_OldTown_PakistanWallFacade_HISM_V1`. A later
  route-facing refinement expanded the same component to 32 instances: six
  low piers articulate the `SS_010` detention-yard south wall, four
  full-height piers divide the `SS_011` north elevation, four full-height
  piers frame the `SS_018` north elevation and its doorway, and two additional
  end piers each complete the three-bay rhythm on the east elevations of
  `SS_015` and `SS_016`. The component uses the imported Nanite Pakistan Wall
  Modular 16 mesh and remains non-colliding/non-navigable. Every batch was
  reviewed at player height and obliquely before the same exact HISM package
  was saved.
- Twenty superseded cube parapets at `SS_004`, `SS_005`, `SS_007`, `SS_012`
  and `SS_018` are hidden in game, `NoCollision` and non-navigable. Their 20
  current `ABV_<site>_RoofParapet_<side>` replacements are visible and retain
  intended query/physics collision. The old actors were not deleted.
- The remaining placeholder facade meters at `SS_003`, `SS_013` and `SS_015`
  now reuse the owned Quixel `Electric_Box_ullibjd_High` mesh. Materials and
  scale were preserved for the source asset; all three remain decorative,
  non-colliding and non-navigable.
- The final runtime capture sweep proved seven narrow rooftop actors were
  floating because zero-based cylinder/cube pivots had been treated as
  centered: `Utility_Pipe_01`, `Utility_Pipe_02`, `Utility_Pipe_04`,
  `Utility_Pipe_05`, `Telecom_Antenna_01`, `Telecom_Antenna_02` and
  `Telecom_Antenna_03`. Exact roof/roof-box bounds showed 15-130 cm support
  gaps. Each actor was lowered without changing XY, rotation, scale, mesh or
  material and now has a verified 2 cm support embed. The four pipe packages
  and three antenna packages were saved as two bounded batches.
- Durable pivot rule: derive contact from the actor's post-transform world
  bounds (`bounds_bottom`) and the exact support actor's world top, not from
  actor location or an assumed centered mesh pivot. This applies to cylinders,
  modular ruin pieces and imported assets alike.
- UE 5.8 Python in this project does not expose
  `HierarchicalInstancedStaticMeshComponent.mark_render_state_dirty()`. The
  reviewed `add_instance` calls updated rendering without it. Treat the missing
  method as an API mismatch, verify the new instance count/transforms and
  viewport output, and do not retry by spawning duplicate instances.
- Verified in the later 32-instance refinement: `add_instance()` can update the
  in-memory HISM and viewport without adding the owning external-actor package
  to Unreal's authoritative dirty-package list. A zero-dirty result therefore
  does not prove that an HISM structural edit was serialized. After validating
  the exact component, instance count and transforms, explicitly save the one
  known owning package with
  `EditorLoadingAndSavingUtils.save_packages([actor.get_package()], False)`;
  then require a newer filesystem mtime, the expected instance count read back,
  and zero dirty packages. This is an exact-package save, not `Save All`.
- Final acceptance report:
  `/private/tmp/abv_launch_buildings_final_acceptance_v4.json`. It verifies the
  exact project/map, all 13 launch sites, nonzero shell/detail coverage, zero
  generic core materials, zero bad L-wall instances, 32 masonry-pier instances
  including the 18 exact route-facing additions,
  three upgraded meters, 20 disabled obsolete parapets, 20 visible replacement
  parapets and zero authoritative Unreal dirty packages. Current review images
  are under `/private/tmp/abv_launch_buildings_postpass_review_v1/`, with exact
  rooftop before/after evidence under
  `/private/tmp/abv_launch_rooftop_pipe_review_v1/` and
  `/private/tmp/abv_launch_telecom_antenna_review_v1/`.
- Git remains intentionally unstaged at 219 modified files plus 46 untracked
  files, with zero staged or out-of-scope paths. Local and remote
  `feature/map-development` both remain
  `e0b856c20cdad11f7057248c851d4d344f43fbe1`; no commit, push, merge or rebase
  was performed.
- This closes the launch-building **first-art/design-draft exterior gate**, not
  final-production art. Later building work should be driven by a specifically
  proven player-height defect or by the future decals/storytelling/lighting/
  HLOD passes rather than reopening systematic shell conversion. The next
  launch-area exterior category is roads and ground transitions, followed by
  restrained seasonal vegetation.

## 2026-08-15 launch-area sandstone shoulder dressing

- The first roads/ground-transition batch added 13 sparse, terrain-conformed
  sandstone shoulder/rubble pieces across the west approach, clinic lane,
  southwest lane, south spine, courtyard lane, east lane, freight edge and
  north lane. They reuse the already imported Quixel `Sandstone Rocky Ground`
  tier-2 mesh and its existing material. This is restrained roadside/open-ground
  breakup, not the final road-surface or Landscape-material pass.
- The pieces are ordinary `StaticMeshComponent`s owned by the existing
  map-only actor `ABV_OldTown_WallFoot_HISM_V1`, so the complete persisted
  scope is exactly its existing external-actor package
  `/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/E/4N/SLKIJA7PHN48GN1EYQ8W7K`.
  All 13 components are `NoCollision`, non-navigable, non-overlapping,
  non-replicated, non-ticking and non-shadow-casting. Uniform scales are
  0.58-0.72 and each piece has a 2 cm terrain embed.
- Five fixed Landscape traces were required per candidate. Thirteen candidates
  passed full Landscape support and <=11.02 cm sampled terrain variation. Three
  candidates were rejected before mutation: west approach A (18.16 cm
  variation), clinic lane A (24.45 cm) and freight edge A (one static-mesh hit
  and 234.4 cm variation).
- Two rejected implementation paths must not be repeated. Tiny trench-debris
  HISM instances read as isolated dark holes and were rolled back. Assigning
  this Quixel mesh to a HISM dirtied the shared `MI_vmjjfiv` material to add
  instanced-static-mesh usage, which was outside this batch; ordinary static
  components avoided that shared-material mutation.
- Durable editor-scripting warning: do **not** call
  `EditorLoadingAndSavingUtils.reload_packages()` in this project to clear an
  unsaved package. It stalled the editor at full CPU on both an external-actor
  package and a small material package. Recover by deleting only the known
  unsaved subobjects when safe, or close the exact isolated editor without
  saving and reopen. Never retry `reload_packages()` here.
- The exact package save changed the actor package from 54,944 to 71,272 bytes,
  advanced its filesystem mtime and returned Unreal to zero authoritative dirty
  packages. Review images are under
  `/private/tmp/abv_launch_road_sandstone_review_v1/`.
- Local and remote `feature/map-development` remain
  `e0b856c20cdad11f7057248c851d4d344f43fbe1`; nothing is staged and no commit,
  push, merge or rebase was performed. The next road pass should audit actual
  roadway boundaries and the existing visible Quixel-ground collision state,
  then return to restrained seasonal grass/flower integration.
- That collision audit then resolved all 16 exact actors in the existing
  `OldTown_QuixelPass/GroundV1` set: eight sandstone actors and eight small
  trench-patch actors were tagged `NoCollision` but were actually `BlockAll`,
  `QueryAndPhysics` and nav-relevant. This mismatch could create low invisible
  blockers and unintended navigation influence.
- The actors were corrected in two exact eight-package batches. Only the
  component collision profile/mode and navigation relevance changed:
  `BlockAll`/`QueryAndPhysics`/nav true became
  `NoCollision`/`NoCollision`/nav false. Overlap events were already false.
  Actor transforms, meshes, materials, scale, visibility and tags were
  preserved. Every package mtime advanced, both saves returned to zero dirty,
  and the repeated 16-actor audit reported `mismatch_count: 0` with all actors
  `NoCollision`, non-navigable and non-overlapping.
- UE 5.8 Python API note: this project's `StaticMeshComponent` wrapper does not
  expose `get_static_mesh()`. Read the source mesh with
  `component.get_editor_property("static_mesh")`. The first unsupported accessor
  stopped before saving and left only the first intended actor package dirty;
  the corrected idempotent script required that exact one-package subset,
  completed the eight-actor batch and saved only the expected packages.
- Collision reports are
  `/private/tmp/abv_launch_qx_ground_collision_audit_v1.json`,
  `/private/tmp/abv_launch_qx_ground_collision_fix_sandstone_v1.json` and
  `/private/tmp/abv_launch_qx_ground_collision_fix_trench_v1.json`.
- UE 5.8 Landscape-mode activation hazard observed on 2026-08-15: selecting
  `Landscape` through the editor mode combobox, without making a paint stroke,
  immediately marked both `LandscapeStreamingProxy_2_1_0`
  (`/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/1/CN/J2WBX0SOQD3OWMZSK0ZWHB`)
  and `LandscapeStreamingProxy_2_2_0`
  (`/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/7/PW/GCKDH3SJ6DMPX8ALJXPIKR`)
  dirty. This was treated as unintended in-memory scope: nothing was saved,
  the exact isolated editor was closed, and the disk/Git baseline remained
  unchanged. Before any future native Landscape paint, enter Landscape mode,
  run an authoritative package-level dirty query immediately, and proceed only
  if the result is zero or the exact intended proxy is already an explicitly
  approved target. Never accept or save proxy packages dirtied merely by mode
  activation, and never use `reload_packages()` to clear them.

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
- The 2026-08-14 second exterior-building pass ended with the exact
  map-development project and `Lvl_Blockout_01` open, zero authoritative Unreal
  dirty packages, five verified entrance awnings, three verified facade
  electrical boxes, the Freight Depot corrugated loading-bay finish, six
  weathered Substation wall panels and two metal Substation lintels. The
  rejected heritage-wall HISM test was fully rolled back to 75 instances, and
  all 288 hidden `VisualGroundOverlay` actors remain hidden and untouched.
- Final Git scope after the completed all-building pass is 134 modified files
  plus 34 untracked files, all unstaged. The scope classifier found zero files outside external
  actor/object packages, the approved `M_ABV_Foliage_Masked` master and this
  handoff document. Local and remote `feature/map-development` both remain at
  `e0b856c20cdad11f7057248c851d4d344f43fbe1`; no stage, commit, push, merge or
  rebase was performed.

## 2026-08-15 initial-launch exterior first-art acceptance

The bounded initial-launch playable-area exterior has completed its
first-art/design-draft gate. This closes the foundational exterior-conversion
pass for the launch area; it does not claim production-final art, final HLODs,
packaged multiplayer performance certification or map-wide polish outside the
launch scope.

- Thirteen launch-area building sites passed the final exterior acceptance:
  `SS_003`, `SS_004`, `SS_005`, `SS_006`, `SS_007`, `SS_010`, `SS_011`,
  `SS_012`, `SS_013`, `SS_015`, `SS_016`, `SS_017` and `SS_018`. The scoped
  building cores contain no generic prototype materials; upgraded meters,
  fourteen masonry piers and the previously corrected/disabled obsolete
  parapets were all reconfirmed.
- All fifty loaded `CoreRoute_*` roadway/route actors resolve to the approved
  world-aligned silt, earth or asphalt treatment, with no prototype route
  material. Thirteen sandstone road-shoulder components provide restrained
  route-edge breakup without collision, navigation relevance, overlaps or
  shadows.
- Sixteen Quixel decorative ground actors were reconfirmed as visual-only:
  `NoCollision`, non-navigable and with overlap events disabled. Their meshes,
  materials and transforms were not changed by the collision correction.
- Seasonal cover is instanced and bounded: the field-edge pilot contains 2,400
  HISM instances (1,440 low-grass and 960 poppy instances), and the north
  `SS_025` meadow contains 6,600 HISM instances. Both use collisionless,
  non-navigable, non-replicated, non-ticking, shadow-disabled components with
  8,000/24,000 cm culling. `M_ABV_Foliage_Masked` retains
  `Used with Instanced Static Meshes = true`; future instanced foliage masters
  must preserve that usage flag before compiling/saving.
- A final performance audit found twenty-two collisionless HISM components that
  still generated overlap events: six on `ABV_OldTown_WallFoot_HISM_V1` and
  sixteen on `ABV_SS025_PoppyMeadow_HISM`. Overlap generation was disabled and
  exactly these two external-actor packages were saved:
  `/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/E/4N/SLKIJA7PHN48GN1EYQ8W7K`
  and
  `/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/B/AY/QGFGMVNS6FJKQ2I5W97PS6`.
  The post-save authoritative dirty-package list was empty.
- Every loaded Landscape actor uses `M_OT_Landscape_Abiverd`. The 288 hidden
  legacy `SunscarVisualConversionHiddenV2` overlays remain hidden and
  untouched; none has blocking collision. Their earlier four-edge report is
  closed as stale because it inspected hidden superseded geometry with the
  wrong cube-pivot assumption.
- The saved `SS_013` historic ruin cluster remains a distinct three-piece
  landmark/cover fragment: one low wall plus two Structure Stone S 06 rubble
  actors. Its circulation and terrain contact remain clear.
- The consolidated read-only acceptance report is
  `/private/tmp/abv_launch_exterior_final_acceptance_v1.json`. It passed all
  checks: clean context, Landscape material, hidden overlays, field-edge
  vegetation, foliage instancing, wall-foot/road shoulders, north-meadow
  performance, `SS_013` ruin cluster, core-route materials and decorative-ground
  collision.
- Final deterministic review images are under
  `/private/tmp/abv_launch_exterior_final_review_v1/`: three aerial views, four
  cardinal player-height route views and one `SS_013` field-edge view. Game View
  was enabled before the final recapture so these contain no editor selection
  overlays.
- Final repository scope is 184 modified files plus 36 intentional untracked
  files, all unstaged. The scope classifier found no unexpected path: changes
  are limited to the map's external actor/object packages, the approved
  `M_ABV_Foliage_Masked` asset and this handoff. Local and remote
  `feature/map-development` remain
  `e0b856c20cdad11f7057248c851d4d344f43fbe1`. No stage, commit, push, merge,
  rebase or mainline change was performed.

If work resumes, the next category is production polish and optimization:
hero-facade uniqueness, secondary debris/decals/storytelling, final HLOD and
World Partition review, and packaged multiplayer/performance validation. It is
not another foundational launch-area exterior conversion pass.

## 2026-08-16 SS_017 bazaar frontage storytelling polish

- The first post-acceptance production-polish batch adds four restrained props
  along the south `SS_017` bazaar frontage:
  `ABV_SS_017_Story_MetalBarrel_A_V1`,
  `ABV_SS_017_Story_Stool_A_V1`,
  `ABV_SS_017_Story_Bench_A_V1` and
  `ABV_SS_017_Story_MetalBarrel_B_V1`. They are terrain-supported, remain
  162-265 cm from the nearest stall collision bounds, and do not narrow the
  main route. All four are `NoCollision`, non-navigable, non-overlapping,
  non-replicated and non-ticking.
- The stool and bench reuse the imported owned Quixel assets. The two barrels
  deliberately reuse the already-working local `SM_Cylinder` plus
  `MI_OT_Metal` combination from `Utility_Barrel_10/11`. The imported
  `Rusty_Metal_Barrel` and `Military_Trenches_Storage_Box_Wood_S` previews
  rendered with pale/white fallback-looking materials in the launch lighting;
  they were rejected before save and must not be assumed presentation-ready
  merely because their source assets load successfully.
- UE Python `unreal.Rotator` positional construction is ordered differently
  from the intuitive `(pitch, yaw, roll)` assumption used by the first unsaved
  preview: `Rotator(0, desired_yaw, 0)` put the value in pitch. The preview was
  corrected before save with complete verified rotations. For future scripts,
  either use explicit property assignment or verify `get_actor_rotation()` and
  require pitch/roll near zero plus the exact intended yaw before saving.
- Exactly four new external-actor packages were saved, with zero additional
  external-object packages because the existing
  `OldTown_ArtDraft/CoveredBazaar` folder hierarchy was reused. The exact-save
  report is `/private/tmp/abv_ss017_storytelling_exact_save_v1.json`; player
  and oblique review captures are
  `/private/tmp/abv_ss017_storytelling_south_finalpreview.png` and
  `/private/tmp/abv_ss017_storytelling_oblique_finalpreview.png`.
- Unreal returned to zero authoritative dirty packages. Git is intentionally
  unstaged at 219 modified plus 50 untracked files, with no unauthorized paths
  and no changed hidden-overlay package. Local and remote
  `feature/map-development` remain
  `e0b856c20cdad11f7057248c851d4d344f43fbe1`; no commit, push, merge or rebase
  was performed.

## 2026-08-16 SS_011 north-frontage storytelling polish

- The second production-polish batch adds three subtle scale/story cues between
  the established north-facade masonry bays:
  `ABV_SS_011_Story_Bench_North_V1`,
  `ABV_SS_011_Story_MetalBarrel_North_V1` and
  `ABV_SS_011_Story_Stool_North_V1`. They reuse the already-approved Quixel
  bench/stool and the working local metal-barrel combination. All five support
  samples per actor hit `LandscapeStreamingProxy_2_2_0` at the same saved
  terrain elevation, with a controlled approximately 2 cm embed.
- The three actors are visual-only: `NoCollision`, non-navigable,
  non-overlapping, non-replicated and non-ticking. They sit close to the blank
  north wall between the non-colliding facade piers and remain clear of the
  east upper ramp and the open route.
- Exactly three new external-actor packages were saved and Unreal returned to
  zero authoritative dirty packages. The exact-save report is
  `/private/tmp/abv_ss011_story_exact_save_v1.json`; before/after evidence is
  `/private/tmp/abv_ss011_story_north_before.png` and
  `/private/tmp/abv_ss011_story_north_preview.png`.
- The accumulated Git scope is now 219 modified plus 53 untracked files, all
  unstaged, with no unauthorized path and no changed hidden-overlay package.
  Local and remote `feature/map-development` remain
  `e0b856c20cdad11f7057248c851d4d344f43fbe1`; no commit, push, merge or rebase
  was performed.

## 2026-08-16 SS_012 consulate-residence frontage polish

- A third distinct frontage batch adds
  `ABV_SS_012_Story_ConsulateBench_V1` and
  `ABV_SS_012_Story_ServiceCrate_V1`. The bench marks the east waiting area;
  the medium military-trench crate provides a restrained service cue at the
  west end. Both are terrain-supported with approximately 2 cm embed, retain
  visible `BlockAll` collision, do not affect navigation, do not generate
  overlaps and remain non-replicated/non-ticking.
- The post-save exact-label verification reconfirmed that the actor and its
  static-mesh component serialize inside the same external-actor package. The
  exact-save report is
  `/private/tmp/abv_ss012_story_finish_exact_save_v1.json`; the readback is
  `/private/tmp/abv_ss012_story_postsave_verify_v1.json`; player-height review
  images are under `/private/tmp/abv_ss012_story_finish_review_v1/`.
- The review also established that these two small props are secondary detail,
  not a substitute for architectural-scale facade readability. Later polish
  should prioritize lighting, entrance framing and large silhouette/detail
  hierarchy before repeating small furniture clusters.

## 2026-08-16 launch-area exterior daylight readability

- A bounded lighting audit found the unbound `Sunscar_PostProcessVolume`
  applying `-0.35 EV` exposure compensation while `Sunscar_SkyLight` used
  intensity `1.35`. Deterministic SS_005 and SS_018 captures showed the
  launch-area facade materials, opening trim and utility details collapsing
  into near-black on shadow-facing elevations.
- Two unsaved previews were compared. The accepted conservative daylight
  presentation uses Skylight intensity `2.5` and post-process exposure
  compensation `+0.15 EV`. Directional-light rotation/intensity, sky
  atmosphere, fog, Landscape, materials and geometry were not changed.
- Exactly two external-actor packages were saved:
  `/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/0/CH/4JX55GESZYZ2QOMZV08PED`
  (`Sunscar_SkyLight`) and
  `/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/9/V2/BUMGYMF2A40A1ZH2NHGIN0`
  (`Sunscar_PostProcessVolume`). The exact-save report is
  `/private/tmp/abv_launch_lighting_readability_exact_save_v1.json`; before,
  first-preview and accepted-refinement captures are
  `/private/tmp/abv_light_before_ss005.png`,
  `/private/tmp/abv_light_before_ss018.png`,
  `/private/tmp/abv_light_preview_ss005.png`,
  `/private/tmp/abv_light_preview_ss018.png`,
  `/private/tmp/abv_light_refine_ss005.png` and
  `/private/tmp/abv_light_refine_ss018.png`.
- UE 5.8 Python on this project does not expose
  `DirectionalLight.directional_light_component`, and the queried
  `SkyLightComponent` did not expose
  `lower_hemisphere_is_solid_color`. The read-only audit initially stopped on
  those accessor mismatches. Durable rule: obtain native components with
  `actor.get_component_by_class(...)` and treat nonessential version-specific
  editor properties as optional so an audit does not abort. Neither failed
  read-only attempt dirtied or saved a package.
- After the exact save, Unreal's authoritative dirty-package list was empty.
  The editor remains on the exact isolated map-development project and map.

## 2026-08-16 launch-area utility and plaza grounding polish

- The three plaza lamps now terminate naturally at the terrain and retain their
  intended lamp-head elevation. `Plaza_Lamp_02` moved from Z `35011.805` to
  `34857.6055` with Z scale `4.001995`; `Plaza_Lamp_03` moved to
  `34829.1179` with Z scale `4.286871`. `Plaza_Lamp_01` had already received
  the same bounded correction. No Landscape, road or lighting asset changed.
- The three `SS_016` roof cabinets (`Utility_Cabinet_03`, `_04` and `_05`)
  now use the owned Nanite Quixel
  `Electrical_Cabinet_ujzfde2_High` mesh at uniform scale `0.9`, with a
  controlled 2 cm roof embed, `BlockAll` collision, no navigation influence,
  no overlaps, no replication and no tick. Their saved Z is
  `35129.4151`; X positions remain `5200`, `6000` and `6800` at Y `-7200`.
- Exact reports are
  `/private/tmp/abv_plaza_lamps23_ground_exact_save_v1.json` and
  `/private/tmp/abv_ss016_roof_cabinet_upgrade_exact_save_v1.json`. Review
  images are under `/private/tmp/abv_ss016_roof_cabinet_review_v1/`.
- The refreshed 13-site completeness matrix at
  `/private/tmp/abv_all_buildings_completeness_matrix_v1.json` found zero
  generic core materials and zero sites without detail. `SS_006` remains an
  intentional water-tower form without a conventional roof; `SS_006`,
  `SS_015`, `SS_016` and `SS_017` intentionally use functional openings rather
  than standard exterior doors. This reconfirms the initial-launch building
  milestone is complete.

## 2026-08-16 SS_005 clinic frontage storytelling polish

- Two restrained, owned props now give the Old Clinic south facade a human
  service/waiting read: `ABV_SS_005_Story_ClinicBench_South_V1` and
  `ABV_SS_005_Story_ClinicServiceCrate_South_V1`. The Quixel wooden bench is
  at `(-6400,-1165,34760.5138)`; the Military Trench medium wooden crate is at
  `(-5350,-1165,34761.3397)`, yaw `8`, uniform scale `1.05`.
- Both actors are terrain-supported with exactly 2 cm embed, retain visible
  `BlockAll` collision, do not affect navigation, do not generate overlaps,
  and remain non-replicated/non-ticking. The nearest verified door clearance
  is `320.98` cm; neither approach is narrowed.
- Exactly two new external-actor packages were saved. The exact report is
  `/private/tmp/abv_ss005_clinic_story_exact_save_v1.json`; before/after
  captures are `/private/tmp/abv_ss005_clinic_story_before_v1.png` and
  `/private/tmp/abv_ss005_clinic_story_after_preview_v1.png`.

## 2026-08-16 SS_018 telecom frontage storytelling polish

- `ABV_SS_018_Story_TelecomCabinet_South_V1` adds one grounded telecom-service
  cue to the previously blank south wall. It reuses the owned Nanite Quixel
  `Electrical_Cabinet_ujzfde2_High` mesh at
  `(-6400,-10065,34779.6380)`, yaw `0`, uniform scale `0.55`, for final bounds
  about `144.10 x 48.03 x 76.32` cm.
- Five support traces hit `LandscapeStreamingProxy_1_1_0` at the same height;
  the cabinet has a controlled 2 cm embed, remains `627.95` cm from the main
  door and `77.03` cm from the existing small wall box. It uses `BlockAll`
  collision but no nav influence, overlaps, replication or tick.
- The Quixel source material read as a bright white block at ground level and
  the first `MI_OT_Accent` preview was too saturated. Only this actor's slot was
  therefore finalized with the existing weathered `MI_OT_Metal`; no shared
  mesh or material asset was edited. This preview-before-save sequence is the
  required precedent for future large utility props.
- Exactly one new external-actor package was saved. The exact report is
  `/private/tmp/abv_ss018_telecom_cabinet_exact_save_v1.json`; final review is
  `/private/tmp/abv_ss018_telecom_cabinet_metal_preview_v1.png`.

## 2026-08-16 field-edge ground-color finish and UE 5.8 material API hazard

- The saved localized `Grass` weights on `LandscapeStreamingProxy_2_2_0`
  remain unchanged. Repeated paint is still a diminishing-return path: the
  nine saved samples already span approximately `0.14118-0.89020`, and no
  additional Landscape package was dirtied in this finish pass.
- A safe targeted graph trace verified that `Grass_BaseColor` and
  `Grass_Tint` feed `MaterialExpressionMultiply_13`, whose output is the
  `Layer` input of the `Grass` `LandscapeLayerWeight` node. The tint control is
  connected; the tan/olive appearance was not a missing paint layer or broken
  material wire.
- The first tint experiments were captured before the landscape shader had
  visibly settled and therefore appeared ineffective. Durable preview rule:
  recompile the material, allow the Landscape components/shader to finish
  updating, then capture identical player-height and elevated views before
  saving. With that procedure, `Grass_Tint (0.30, 0.95, 0.28, 1.0)` produced a
  clearly greener but still semi-arid meadow footprint and preserved the
  feathered dirt transition. Exactly
  `/Game/Maps/Sunscar/Art/Materials/LandscapeV3/M_OT_Landscape_Abiverd` was
  saved; compile errors were zero and authoritative dirty state returned to
  zero. Exact report:
  `/private/tmp/abv_landscape_grass_color_exact_save_v1.json`. Saved-state and
  accepted-preview comparisons are under
  `/private/tmp/abv_field_saved_state_recovered_v1/` and
  `/private/tmp/abv_landscape_grass_color_preview_final_v1/`.
- **Do not call**
  `unreal.MaterialEditingLibrary.get_input_node_output_name_for_material_expression()`
  in UE 5.8 on this Mac/project. A read-only graph inspection caused a native
  `SIGSEGV` inside `libUnrealEditor-MaterialEditor.dylib` at
  `UMaterialEditingLibrary::GetInputNodeOutputNameForMaterialExpression`.
  Unreal was clean before the call; the post-crash process was terminated and
  the exact isolated project/map reopened with zero dirty packages. Use only
  `get_material_expression_input_names()` plus
  `get_inputs_for_material_expression()` for bounded graph tracing. The latter
  can return null entries, so filter them before dereferencing.
- The established launch-area exterior acceptance was rerun after the exact
  save and returned `verified` with 3,354 loaded actors and zero dirty
  packages. All ten gates passed: correct/clean context, Landscape material,
  288 hidden legacy overlays, field-edge HISM, foliage instancing usage,
  wall-foot/road shoulders, north-meadow performance, SS_013 ruin cluster,
  core-route materials and decorative-ground collision. Report:
  `/private/tmp/abv_launch_exterior_final_acceptance_v1.json`.

## 2026-08-16 initial-launch building interiors and thresholds complete

- The four production-critical interiors now have a restrained first playable
  art pass. `SS_010` has an intake desk, two correctly yawed stools, a holding
  bench and two warm practical lights. `SS_007` has lobby reception/guest
  furniture, one upper-room table/bench pair and three practical lights.
  `SS_004` retains its existing tea-house dressing and now has two low-intensity
  warm room lights. `SS_017` retains its market dressing and its six prototype
  stall blocks were replaced in place with the owned Quixel
  `Wooden_Table_veigfjmaw_High` mesh, producing a traversable covered-bazaar
  passage rather than six full-height white barriers.
- The other launch buildings were deliberately held to the production plan's
  readable-threshold standard rather than being over-furnished. `SS_003`,
  `SS_005`, `SS_011`, `SS_012`, `SS_013`, `SS_015`, `SS_016` and `SS_018`
  passed exact opening/furnishing inventory minima. `SS_016` remains an
  intentional functional substation without a conventional public doorway;
  `SS_006` remains the intentional water-tower traversal structure, represented
  by its loaded mid-landing rather than a conventional F1 floor.
- The final package-level launch-building gate returned `verified` with 3,370
  loaded actors and zero dirty packages. All gates passed: exact project/map,
  all 13 launch sites loaded, eight non-critical threshold treatments, seven
  critical practical lights, nine new critical furnishings, six upgraded
  bazaar stalls, clear/non-blocking `SS_003` threshold utility dressing and all
  288 hidden legacy overlays still hidden and collisionless. Reports:
  `/private/tmp/abv_launch_critical_interiors_acceptance_v1.json` and
  `/private/tmp/abv_launch_buildings_final_acceptance_v1.json`. Corrected
  threshold review captures are under
  `/private/tmp/abv_launch_threshold_review_v2/`.
- Durable UE Python rotation rule: never rely on positional construction for
  `unreal.Rotator`. Use named arguments such as
  `unreal.Rotator(pitch=0.0, yaw=15.0, roll=0.0)`, then read back and require
  the exact full rotation before saving. A positional call in the first
  `SS_010` stool preview put the intended yaw into pitch; both stools were
  corrected and exact-saved before acceptance.
- Durable external-actor mutation rule: changes to already-saved World
  Partition actors may not enter the authoritative dirty-package list unless
  both the actor and the affected component receive `modify()` before property
  mutation. The initial unsaved `SS_017` stall-mesh preview exposed this. The
  accepted pass called `actor.modify()` and `component.modify()`, required the
  exact six intended actor packages, saved only those packages and returned to
  zero dirty state.
- Deterministic `CaptureViewport` images can contain editor sprites, selection
  lines and helper visualization even with UI hidden. Do not classify those as
  runtime defects. Confirm suspicious objects by exact actor/component flags,
  collision and Game View/PIE evidence before changing map content.
- Final Git scope is intentionally unstaged: 232 modified plus 73 untracked
  files (305 total), staged count zero. Local and remote
  `feature/map-development` remain
  `e0b856c20cdad11f7057248c851d4d344f43fbe1`; no commit, push, merge or rebase
  was performed.

## 2026-08-16 launch-region optimization and HLOD readiness

- A loaded-region performance inventory covered 3,370 actors without invoking
  World Partition descriptor, intersection or scripted region-loading APIs.
  The map contains 31 HISM components and 9,321 HISM instances. Seasonal cover
  accounts for 9,000 instances; every vegetation component remains
  collisionless, non-navigable, non-overlapping, shadow-disabled,
  non-replicated and non-ticking with valid distance culling.
- Seven collisionless facade/trim HISM components still had overlap generation
  enabled. The bounded correction changed only those components across exactly
  five existing actor packages: door surrounds, Pakistan wall facade, window
  trim, Pakistan window facade and the empty facade-scan staging actor. Meshes,
  materials, instances, transforms, shadows, collision, navigation and culling
  were preserved. Exact report:
  `/private/tmp/abv_launch_facade_hism_overlap_fix_v1.json`.
- Post-save verification reduced collisionless overlap-enabled components from
  16 to nine. The nine remaining components are the eight `PlayerStart`
  collision capsules plus the unbound post-process volume brush; these are
  intentional gameplay/editor helpers and were not changed. Unreal returned to
  zero authoritative dirty packages.
- The loaded region has zero ticking actors and zero movable StaticMeshActors.
  The sole replicated actor is the engine-managed `WorldDataLayers`. Of 68
  unique StaticMeshActor meshes, 62 are Nanite-enabled. The six non-Nanite
  meshes are Engine cubes/cylinders/spheres and three CitySample vehicle LOD
  meshes; do not mutate those shared source assets merely to increase the
  Nanite count. Inventory:
  `/private/tmp/abv_launch_optimization_audit_v1.json`.
- HLOD configuration assets are present and valid:
  `Lvl_Blockout_01_HLODLayer_Instanced` is a spatial instancing layer
  (`25,600` cm cell, `76,800` cm loading range) whose parent is
  `Lvl_Blockout_01_HLODLayer_Merged`; the merged layer is a non-spatial
  mesh-merge layer (`25,600` cm cell, `51,200` cm loading range). However, the
  Asset Registry currently contains zero generated `WorldPartitionHLOD` assets
  for this map and loaded actors have no explicit per-actor HLOD override.
  Report: `/private/tmp/abv_hlod_readiness_audit_v1.json`.
- Do not run the unfiltered `WorldPartitionHLODsBuilder` on this accumulated
  uncommitted map scope. UE 5.8's full commandlet setup/build path generates
  HLOD actors for the whole world and would create a mass package delta. The
  editor supports selected-actor/selected-region HLOD filters, but the previous
  Mac failures prove scripted World Partition descriptor/filter paths can pin
  the editor. A launch-region HLOD build should be a separately controlled
  editor/UI operation after the current map checkpoint, with exact generated
  package enumeration before accepting the result.
- Current Git scope is intentionally unstaged: 235 modified plus 73 untracked
  files (308 total), staged count zero. Local and remote
  `feature/map-development` remain
  `e0b856c20cdad11f7057248c851d4d344f43fbe1`; no commit, push, merge or rebase
  was performed.

## 2026-08-16 launch PlayerStart terrain and obstruction correction

- A package-level launch-spawn audit found all eight `PlayerStart` capsules
  embedded in Landscape by approximately `0.7-46.1` cm. The north pair also
  occupied the same edge as `NorthSpawn_HistoricWall`; north start 02
  overlapped both that wall and `OT_REMAIN_SS_020_GROUND_008`. This was a
  genuine gameplay-start defect, not an editor-sprite artifact.
- `CorePlayerStart_DefenderNorth_01` and `_02` were moved from `Y=10400` to
  `Y=10180`, preserving their `X`, yaw, scale and `800` cm separation. Their
  final Z values are `34996.8632` and `34999.3364`. Five direct Landscape
  samples per capsule prove a `2` cm minimum bottom clearance; capsule overlap
  tests prove zero blockers. The final north pair has at least `180` cm
  clearance from the historic wall, and north 02 has `60.4` cm capsule-edge
  clearance from the nearby ground rock. Reports:
  `/private/tmp/abv_north_spawn_target_preflight_v1.json` and
  `/private/tmp/abv_north_spawn_fix_exact_save_v1.json`.
- The four attacker starts and two south defender starts retained their exact
  XY positions, rotations and scales. Only Z was corrected by `+8.10` to
  `+39.73` cm according to five direct Landscape samples per actor, targeting
  `2` cm clearance above each local maximum. Their only remaining overlap is
  the four attackers' intentional `CoreVolume_AttackerExtraction` trigger;
  no solid blockers remain. Reports:
  `/private/tmp/abv_remaining_spawn_z_preflight_v1.json` and
  `/private/tmp/abv_remaining_spawn_z_fix_exact_save_v1.json`.
- Final full acceptance verifies eight starts, Landscape support under every
  capsule, positive center-point bottom clearances of approximately
  `2.46-7.40` cm, minimum inter-start spacing above `800` cm and zero
  authoritative dirty packages. Report:
  `/private/tmp/abv_launch_spawn_nav_audit_v1.json`.
- No `NavMeshBoundsVolume` or `RecastNavMesh` is loaded for the launch region.
  This is recorded as an AI-navigation readiness gap, not addressed in this
  map-only spawn pass. Add/build navigation only as a separately bounded slice
  after confirming the launch AI requirements and intended traversal volume.
- The corrected north-spawn review exposed `NorthSpawn_HistoricWall` as a
  visually flat `20 m x 0.5 m x 3 m` prototype cube using warm stucco. Its
  material slot was upgraded, without any transform or collision change, to
  the existing world-aligned
  `MI_ABV_RuinBrick_WorldAligned`. This removes the stretched/plain slab read
  while preserving `BlockAll`, static mobility, navigation relevance, no
  overlap events and both corrected north spawn transforms. Exact report:
  `/private/tmp/abv_north_spawn_wall_material_exact_save_v1.json`; matching
  before/after views are under `/private/tmp/abv_north_spawn_review_v1/`.
- UE 5.8 Python can return `None` rather than an empty array from
  `SystemLibrary.capsule_overlap_actors()`. Every bounded audit must normalize
  that result with `or []` before iteration; the first acceptance attempt
  stopped read-only on this API behavior and changed nothing.
- Current Git scope is intentionally unstaged: 244 modified plus 73 untracked
  files (317 total), staged count zero. Local and remote
  `feature/map-development` remain
  `e0b856c20cdad11f7057248c851d4d344f43fbe1`; no commit, push, merge or rebase
  was performed.

## 2026-08-16 SS_007 Hotel hero-facade and decorative-collision pass

- A current player-height review confirmed that the Hotel's pale upper shell
  remains a useful civic-landmark cue, but the entire south ground storey read
  as another flat blue-white slab. Exactly the three south-facing F1 shell
  actors (`Core_SS_007_F1_S_Left`, `_Lintel` and `_Right`) now reuse the
  existing world-aligned `MI_ABV_RuinBrick_WorldAligned` material. Transforms,
  collision, navigation and the upper floors were preserved. This produces a
  believable repaired/exposed masonry base without moving the gameplay shell.
  Exact report:
  `/private/tmp/abv_ss007_south_groundstorey_material_exact_save_v1.json`;
  before/accepted preview captures:
  `/private/tmp/abv_hotel_hero_before_south.png` and
  `/private/tmp/abv_hotel_groundstorey_preview_south.png`.
- Four unsaved Pakistan Wall Modular 16 HISM instances were previewed on two
  uninterrupted Hotel side-wall spans. Visual review rejected them because
  the complete storey-height scans again read as attached tan slabs rather
  than integrated repairs. Indices `32-35` were removed, the component was
  restored to its exact 32-instance baseline, and no rejected instance was
  persisted. UE 5.8 Python does not expose `Package.set_dirty_flag(False)`, so
  the restored actor package was exact-saved solely to clear the stale preview
  dirty flag. Rollback report:
  `/private/tmp/abv_ss007_pakistan_side_facade_rollback_v1.json`.
- The live Hotel opening audit exposed a policy mismatch: all 15 decorative
  cube window frames still used Query-and-Physics collision, and all 30 south
  frame/recess cues were navigation-relevant despite the handoff's intended
  collisionless decorative treatment. Exactly those 30 actors now have actor
  collision disabled, component `NoCollision`, navigation relevance disabled
  and overlap events disabled. Every mesh, material, transform and visible cue
  was preserved; the building shell remains the only authoritative collision.
  Exact report:
  `/private/tmp/abv_ss007_window_cue_collision_exact_save_v1.json`.
- The three Quixel wrinkled-tarp balcony shades were re-reviewed at their saved
  `1.4` scale and at a smaller `1.1` preview. In both cases this particular
  scan read as dark rock-like debris overhead rather than fabric. The accepted
  correction restores their original transforms but hides only those three
  visual actors in editor/runtime; they remain collisionless, non-navigable
  and available for a later suitable awning replacement. The balcony deck,
  rail, sign and gameplay shell were not changed. Exact report:
  `/private/tmp/abv_ss007_balcony_shade_hide_exact_save_v1.json`; accepted
  player-height view:
  `/private/tmp/abv_hotel_shade_hidden_preview_south.png`.
- Durable UE 5.8 scripting notes: Python `Transform` wrapper equality is not a
  reliable transform-preservation check; compare the nine numeric
  location/rotation/scale components. A HISM component has no Python
  `get_static_mesh()` method in this build; read its `static_mesh` editor
  property instead.
- Current Git scope is intentionally unstaged: 262 modified plus 73 untracked
  files (335 total), staged count zero. Local and remote
  `feature/map-development` remain
  `e0b856c20cdad11f7057248c851d4d344f43fbe1`; no commit, push, merge or rebase
  was performed.

## 2026-08-16 SS_011 Checkpoint and SS_010 detention-perimeter polish

- Current player-height and oblique review of SS_011 proved that the two pale
  vertical pieces on its south approach are the intentional grounded vehicle
  gate posts, not floating facade geometry. Their transforms, collision and
  navigation behavior remain unchanged. Only their placeholder-looking pale
  metal finish was changed to the existing `MI_OT_Timber`, which reads as a
  weathered local checkpoint structure and no longer resembles two white
  editor markers. Exact report:
  `/private/tmp/abv_ss011_gatepost_timber_exact_save_v1.json`; accepted review
  captures are under `/private/tmp/abv_ss011_current_review_v1/`.
- The same SS_011 audit confirmed the long overhead shade edge belongs to the
  existing checkpoint composition and the two gate posts have valid terrain
  contact (actor bottoms about `2-3` cm above the sampled local ground). No
  crossbar, new collision or route obstruction was added.
- SS_010's six detention-yard perimeter wall actors still used the flat teal
  prototype `MI_OT_Detention` material and dominated every exterior approach.
  A bounded comparison tested both existing Abiverd cracked-mud and ruin-brick
  world-aligned materials. The accepted result uses
  `MI_ABV_RuinBrick_WorldAligned` on exactly
  `Core_DetentionYard_F1_E_Left`, `_E_Right`, `_N_Wall`, `_S_Left`, `_S_Right`
  and `_W_Wall`. It preserves all transforms, collision, navigation, openings,
  doors and traversal while giving the enclosure a credible historic masonry
  read. Exact report:
  `/private/tmp/abv_ss010_yard_wall_ruinbrick_exact_save_v1.json`; accepted
  current review captures are under `/private/tmp/abv_ss010_current_review_v1/`.
- Current Git scope is intentionally unstaged: 270 modified plus 73 untracked
  files (343 total), staged count zero. Local and remote
  `feature/map-development` remain
  `e0b856c20cdad11f7057248c851d4d344f43fbe1`; no commit, push, merge or rebase
  was performed.

## 2026-08-16 launch-building exterior consistency and bad-awning cleanup

- The imported Quixel `WrinkledTarp` scan was re-evaluated across the launch
  buildings. At several small entrance/balcony scales it reads as a dense black
  rock slab rather than fabric. Six individually verified bad instances are now
  hidden in editor/runtime with `NoCollision` and no navigation relevance while
  preserving their transforms for a later replacement: the SS_005 Clinic main
  awning, SS_010 detention-yard gate awning, SS_011 checkpoint door awning,
  both SS_012 Consulate door awnings and the SS_016 Substation west awning.
  Existing building shells, doors, traversal and shared source assets were not
  changed. Reports:
  `/private/tmp/abv_launch_bad_awning_hide_exact_save_v1.json`,
  `/private/tmp/abv_ss012_door_awning_hide_exact_save_v1.json` and
  `/private/tmp/abv_ss016_bad_awning_hide_exact_save_v1.json`.
- The SS_003 pump awnings, SS_013 depot awning and SS_018 telecom awning were
  retained after current visual review because their thin edge-on placement is
  plausible. The SS_017 Bazaar canopy system was deliberately excluded from
  blanket cleanup because it is a multi-piece market composition rather than
  the same isolated entrance defect.
- The Clinic now has a coherent weathered ground-storey band on every exterior
  side. Its three south F1 shell actors and the five remaining east, north and
  west F1 shell actors reuse the existing world-aligned
  `MI_OT_FlakedPaint_WorldAligned`; all upper-storey stucco, openings,
  transforms and authoritative collision remain unchanged. Reports:
  `/private/tmp/abv_ss005_south_groundstorey_flakedpaint_exact_save_v1.json`
  and
  `/private/tmp/abv_ss005_clinic_groundstorey_wrap_flaked_exact_save_v1.json`.
  Accepted wrap views are under
  `/private/tmp/abv_ss005_clinic_groundstorey_wrap_flaked_preview_v1/`.
- SS_004's previously featureless 18 m north wall now uses the existing
  `MI_ABV_CrackedMud_WorldAligned` material, matching its Abiverd mud-plaster
  character without changing its transform, collision or north foundation
  skirt. Exact report:
  `/private/tmp/abv_ss004_north_wall_crackedmud_exact_save_v1.json`; accepted
  view: `/private/tmp/abv_ss004_north_crackedmud_preview_v1.png`.
- Two blank service/rear elevations were upgraded with the existing
  `MI_ABV_RuinBrick_WorldAligned`: the SS_011 checkpoint north F1 wall and the
  SS_017 Bazaar south wall. The checkpoint now reads as a brick lower course
  below weathered plaster and its existing masonry parapet; the Bazaar keeps
  every stall and clearance while gaining a legible masonry service wall.
  Exact report:
  `/private/tmp/abv_launch_blank_rear_walls_ruinbrick_exact_save_v1.json`;
  accepted views are under
  `/private/tmp/abv_launch_rear_walls_ruinbrick_preview_v1/`.
- SS_018's north ground storey now uses
  `MI_OT_FlakedPaint_WorldAligned` on exactly its left, lintel and right F1
  shell actors, preserving the pale upper storey, entrance opening, facade
  piers, transforms and collision. Exact report:
  `/private/tmp/abv_ss018_north_groundstorey_flaked_exact_save_v1.json`;
  accepted view:
  `/private/tmp/abv_ss018_north_groundstorey_flaked_preview_v1.png`.
- Every accepted batch enumerated the authoritative package-level dirty scope,
  saved only the exact intended external-actor packages, confirmed filesystem
  writes and returned Unreal to zero dirty packages. Current Git scope is
  intentionally unstaged: 281 modified plus 73 untracked files (354 total),
  staged count zero. Local and remote `feature/map-development` remain
  `e0b856c20cdad11f7057248c851d4d344f43fbe1`; no commit, push, merge or rebase
  was performed.

## 2026-08-16 launch-building ground-storey completion and shell acceptance

- The SS_007 Hotel ground floor now has a coherent ruin-brick wrap on all four
  exterior sides. Exactly the remaining north, east-left, east-lintel,
  east-right and west F1 shell actors were changed from generic stucco to the
  existing `MI_ABV_RuinBrick_WorldAligned`; its already-correct south F1
  pieces, upper floor, openings, balcony, collision and traversal were not
  changed. Exact report:
  `/private/tmp/abv_ss007_hotel_groundstorey_wrap_ruinbrick_exact_save_v1.json`;
  accepted north/east/west player-height views are under
  `/private/tmp/abv_ss007_hotel_groundstorey_wrap_ruinbrick_preview_v1/`.
- A close four-side SS_016 Substation review proved the shell is complete and
  the earlier apparent missing elevation was only a distant camera/clipping
  artifact. No shell actor was changed. The thin roofline rods remain the
  previously audited intentional utility features whose lower sections are
  hidden by the roof. Exact read-only preflight:
  `/private/tmp/abv_ss016_shell_exact_preflight_v1.json`; accepted views are
  under `/private/tmp/abv_ss016_shell_review_v1/`.
- The flat teal prototype treatment on the SS_010 Detention Annex no longer
  dominates its principal building. Exactly its eight ground-storey shell
  actors (east left/lintel/right, north, south left/lintel/right and west) now
  use the existing `MI_ABV_RuinBrick_WorldAligned`, while the cleaner teal
  upper storey remains as a deliberate institutional accent. Openings,
  transforms, authoritative collision and the previously completed perimeter
  were preserved. Exact report:
  `/private/tmp/abv_ss010_annex_groundstorey_ruinbrick_exact_save_v1.json`;
  accepted close views are under
  `/private/tmp/abv_ss010_annex_groundstorey_ruinbrick_preview_v1/`.
- The SS_012 Consulate Residence now reads as a cleaner pale residence above a
  weathered earthen ground storey. Exactly its eight F1 shell pieces use the
  existing `MI_ABV_CrackedMud_WorldAligned`; the pale upper floor, roof,
  timber/brick accents, doors, windows, transforms and collision remain
  unchanged. Exact report:
  `/private/tmp/abv_ss012_consulate_groundstorey_crackedmud_exact_save_v1.json`;
  accepted south/north/oblique views are under
  `/private/tmp/abv_ss012_consulate_groundstorey_crackedmud_preview_v1/`.
- A targeted trace resolved the gray cube visible near SS_013 as
  `CoreCover_C10`, a tagged authoritative `HardCover` gameplay actor using
  `MI_OT_Metal`, not a stray exterior prop. It was deliberately preserved.
  Read-only evidence:
  `/private/tmp/abv_ss013_foreground_cube_trace_probe_v1.json`.
- Every accepted mutation above used exact package-level dirty gates and exact
  saves, then returned Unreal to zero dirty packages. Current Git scope is
  intentionally unstaged: 302 modified plus 73 untracked files (375 total),
  staged count zero. Local and remote `feature/map-development` remain
  `e0b856c20cdad11f7057248c851d4d344f43fbe1`; no commit, push, merge or rebase
  was performed.

## 2026-08-16 launch-building secondary-elevation composition closeout

- A new deterministic 16-view acceptance set across the 13 launch building
  sites and three aerial contexts is under
  `/private/tmp/abv_launch_buildings_acceptance_review_v3/`. Fixed cameras that
  clipped through nearby/open-sided structures were rejected as invalid
  evidence; no geometry was changed from those views. The close cardinal
  shell reviews and prior exact actor/package audits remain authoritative.
- SS_004's material-correct but compositionally blank 18 m north elevation now
  has four non-colliding, non-navigable instances of the already imported
  Pakistan Wall Modular 16 heritage piece. They divide the wall into readable
  structural bays without creating actors, changing openings, or adding
  gameplay collision. Accepted views are under
  `/private/tmp/abv_ss004_north_facade_piers_preview_v1/`; exact save report:
  `/private/tmp/abv_ss004_north_facade_piers_exact_save_v1.json`.
- SS_003's exposed west service wall now uses the same reuse-first system: two
  additional piers join its existing center pier to create a three-bay rhythm.
  The additions are visual-only HISM instances and preserve the pump station's
  shell, utilities, cover, collision and traversal. Accepted views are under
  `/private/tmp/abv_ss003_west_facade_piers_preview_v1/`; exact save report:
  `/private/tmp/abv_ss003_west_facade_piers_exact_save_v1.json`.
- Both additions serialize in the one existing
  `ABV_OldTown_PakistanWallFacade_HISM_V1` actor package
  `/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/4/XJ/GOWVSDB53YHV8I1OQ2ZTN7`.
  Its final instance count is 38, effective collision is `NoCollision`,
  navigation relevance is false, and Unreal returned to zero dirty packages
  after each exact save. These close the remaining obvious flat secondary
  elevations; continue with ground/road/placed-prop exterior integration rather
  than another systematic building-shell pass unless new player-height evidence
  proves a specific defect.

## 2026-08-16 field-edge vegetation and localized ground acceptance

- A fresh current-state review after the launch-building closeout confirms the
  SS_013-adjacent field-edge now reads as a seasonal Abiverd grass-and-poppy
  patch at player height. The accepted five-view set is under
  `/private/tmp/abv_fieldedge_current_acceptance_v2/`.
- The map-owned `ABV_OT_FieldEdge_PoppyPilot_V1` actor remains one optimized
  non-replicated, non-ticking HISM actor with exactly 1,440 low-grass instances
  and 960 poppy instances. Both components are `NoCollision`, non-navigable,
  generate no overlaps, cast no shadows, and cull from 80 m to 240 m.
- `M_ABV_Foliage_Masked` is compiled for instanced static meshes and retains an
  opacity-mask clip value of 0.20. Seven fixed samples on
  `LandscapeStreamingProxy_2_2_0` returned saved Grass weights from 0.4384 to
  0.8549, confirming that the localized green ground treatment remains on the
  terrain beneath the vegetation rather than being a transient editor preview.
- Exact read-only evidence is
  `/private/tmp/abv_launch_vegetation_acceptance_v1.json`. Unreal remained at
  zero dirty packages. The field-edge pilot is accepted for the initial-launch
  playable area; continue exterior ground/road/placed-prop integration rather
  than reopening the foliage material or density unless new player-height
  evidence proves a specific defect.

## 2026-08-16 launch-perimeter Abiverd material finish

- The conspicuous near-white linear element beside the accepted field-edge was
  resolved by labeled viewport evidence as `CoreWall_EastMid`, an intentional
  collidable `HardCover`/`CoreBoundary` actor, not an editor guide or stray
  prop. The geometry, transform, collision, navigation and gameplay tags were
  preserved.
- Exactly the 11 launch perimeter segments that still used the bright generic
  `MI_OT_Stone` finish now use the existing
  `MI_ABV_RuinBrick_WorldAligned`. The already-correct
  `CoreWall_SouthSpawnSightbreak` was left unchanged. This removes the clean
  white-slab reading and makes the playable boundary read as sun-baked Abiverd
  masonry while retaining authoritative hard-cover behavior.
- Accepted approach and aerial views are under
  `/private/tmp/abv_corewall_abiverd_finish_review_v1/`. The exact mutation and
  save evidence are
  `/private/tmp/abv_corewall_abiverd_finish_apply_v1.json` and
  `/private/tmp/abv_corewall_abiverd_finish_exact_save_v1.json`.
- All 11 expected external-actor packages were physically rewritten and Unreal
  returned to zero dirty packages. No transforms, collision, navigation,
  buildings, roads, Landscape, vegetation, config, Movement, UI or hidden
  legacy overlay packages were changed.

## 2026-08-16 dry-canal and launch-placeholders exterior finish

- The west dry-canal entrance was the next proven player-height exterior
  defect: both 24 m edge walls still read as bright blockout slabs and its six
  named rubble actors were chamfer-cube placeholders. Before/after evidence is
  under `/private/tmp/abv_canal_rubble_review_v1/` and
  `/private/tmp/abv_canal_rubble_review_v1_after/`.
- `Canal_Edge_E` and `Canal_Edge_W` now use the existing
  `MI_ABV_RuinBrick_WorldAligned` material without transform, collision or
  navigation changes. `Canal_Rubble_01` through `Canal_Rubble_06` now reuse the
  already imported Historic Desert Ruin Structure Stone S 06 mesh. Each stone
  has a distinct yaw/uniform scale, a direct Landscape support trace and an
  exact 3 cm natural embed. Their existing query-and-physics collision and
  navigation relevance remain active because these pieces participate in the
  canal approach's physical cover/readability.
- The dry-canal mutation and exact-save reports are
  `/private/tmp/abv_dry_canal_finish_apply_v1.json` and
  `/private/tmp/abv_dry_canal_finish_exact_save_v1.json`. Exactly eight
  external-actor packages were physically rewritten and Unreal returned to
  zero dirty packages.
- The remaining 26 visible launch-area actors that still used generic
  `MI_OT_Stone` were then split by intended function without changing geometry
  or gameplay dimensions. Twelve attacker/checkpoint/south-spawn barriers and
  five ground curbs now use the existing weathered-concrete world-aligned
  material. Eight current SS_003/SS_006 parapets plus
  `Courtyard_Low_Focus` now use the Abiverd ruin-brick world-aligned material.
  Transforms, collision and navigation were explicitly preserved on every
  actor. Accepted contextual views are under
  `/private/tmp/abv_launch_placeholder_material_review_v1/`; mutation and
  exact-save reports are
  `/private/tmp/abv_launch_stone_placeholder_material_finish_apply_v1.json`
  and
  `/private/tmp/abv_launch_stone_placeholder_material_finish_exact_save_v1.json`.
- A follow-up bounded inventory found zero visible StaticMeshActors carrying
  LevelPrototyping materials inside the initial-launch XY/Z envelope. Evidence:
  `/private/tmp/abv_launch_prototype_material_inventory_v1.json`. This closes
  the current launch-area generic/prototype exterior-material category; pursue
  only concrete player-height findings rather than another broad material
  rewrite.

## 2026-08-16 initial-launch barrier production-mesh finish

- The 12 remaining scaled chamfer-cube road-control barriers at the attacker
  spawn, checkpoint and south spawn now reuse the already imported Quixel
  `SM_ydxlcck_tier_2` long sandbag assembly and its existing `MI_ydxlcck`
  material. No new mesh, material, actor or package was created.
- Each four-actor site was handled as a separate dirty/save batch. Every actor
  uses uniform scale 1, query-and-physics `BlockAll` collision, navigation
  relevance, no overlap events, a direct Landscape support trace and exactly
  3 cm natural terrain embed. Center-route clearances remain approximately
  6.79 m at attacker spawn, 10.79 m at the checkpoint and 6.79 m at south
  spawn. The checkpoint trace explicitly ignored only the known existing
  `CoreCover_C11` sandbag after the first read-only support trace correctly hit
  that cover instead of Landscape; no mutation occurred during that rejected
  attempt.
- Accepted current-state views are under
  `/private/tmp/abv_barrier_sandbag_review_v1/`. The bounded apply and exact
  save reports are
  `/private/tmp/abv_launch_barrier_sandbag_group_apply_v1.json` and
  `/private/tmp/abv_launch_barrier_sandbag_group_exact_save_v1.json` (the files
  are overwritten per group; the Unreal log retains one preview/save marker per
  site). All 12 existing external-actor packages were physically rewritten in
  four-package batches, and Unreal returned to zero dirty packages after each
  exact save.

## 2026-08-16 initial-launch core-cover production-visual pass

- The authoritative `CoreCover_*` actors remain the gameplay collision and
  navigation proxies. Their transforms and query-and-physics collision are
  preserved; only the visible prototype cube components are hidden after a
  reviewed production-mesh replacement is present.
- `CoreCover_A01` through `CoreCover_A08` now have optimized map-owned HISM
  visuals in `ABV_OT_CoreCover_Visual_HISM_V1`. The actor contains six long
  Quixel sandbag instances and eight square Quixel sandbag instances; the
  HISM components are non-replicated, non-ticking, collisionless,
  navigation-irrelevant, overlap-disabled and distance-culled. Exact source
  proxy packages and the HISM actor package were saved in bounded batches,
  and Unreal returned to zero dirty packages after each save.
- Durable UE 5.8 material rule: every material used by ISM/HISM geometry must
  have **Used with Instanced Static Meshes = true**. Validate that usage before
  actor creation. The first HISM assignment may legitimately dirty the exact
  source material or material-instance package while Unreal adds the usage
  permutation; treat that as a bounded, reviewable material compile/save, not
  as unexplained map-package scope. This applies to foliage masters such as
  `M_ABV_Foliage_Masked` and to Quixel materials reused for instanced cover.
- Do not call a nonexistent Python `mark_render_state_dirty` method on an HISM
  component. Instance addition already updates the component; verify the
  viewport and authoritative dirty-package list instead. Also avoid accepting
  the first downward trace blindly: `CoreCover_A06` initially hit an overhead
  compound floor. That preview was rejected before save and the visual was
  conformed to the preserved authoritative proxy base with a 3 cm embed.
- Evidence is under `/private/tmp/abv_corecover_a_pilot_review_v1/` and
  `/private/tmp/abv_corecover_a05_a08_review_v1/`; apply/save reports are
  `/private/tmp/abv_corecover_a_pilot_apply_v1.json`,
  `/private/tmp/abv_corecover_a_pilot_exact_save_v1.json`,
  `/private/tmp/abv_corecover_a05_a08_apply_v1.json`, and
  `/private/tmp/abv_corecover_a05_a08_exact_save_v1.json`.

### Core-cover continuation and closeout

- `CoreCover_B01` through `CoreCover_B08` and the visible C-series proxies
  (`C01` through `C10`, plus `C12`) now follow the same production-visual
  pattern. Industrial-width envelopes use the imported corrugated Quixel
  barrier mesh; narrower masonry positions use stacked square Quixel
  sandbags; the low profile uses the imported Structure Stone S 06 rubble.
  Each placement was conformed to the exact visible support actor, with the
  C09 position correctly supported by `Core_SS_013_F1_Floor` rather than
  Landscape. The hidden valid `CoreCover_C11` proxy was not changed.
- The shared `ABV_OT_CoreCover_Visual_HISM_V1` actor now contains exactly 6
  long-sandbag, 30 square-sandbag, 25 corrugated-barrier and 6 low-rubble
  instances before the freight component. All visual HISM components remain
  `NoCollision`, navigation-irrelevant, overlap-disabled, non-replicated,
  non-ticking and culled from 160 m to 480 m. The authoritative hidden proxy
  actors retain query-and-physics collision and navigation relevance.
- The final visible prototype, `CoreCover_FreightCrates`, was replaced by 12
  instances of the owned Scene Junkyard rusty metal storage crate, arranged
  as a compact three-by-two, two-course freight stack on the perfectly level
  `Core_SS_013_F1_Floor`. The final HISM actor therefore also contains
  `HISM_CoreCover_FreightCrates` with 12 visual-only instances. Close review
  evidence is under `/private/tmp/abv_freight_crates_review_v1/after_detail/`;
  exact save evidence is
  `/private/tmp/abv_freight_crates_exact_save_v1.json`.
- Final read-only inventory:
  `/private/tmp/abv_launch_corecover_visual_matrix_v1.json` records all 34
  `CoreCover_*` actors hidden and zero visible `CoreCover_*` prototype blocks,
  with authoritative Unreal dirty packages at zero. This closes the initial
  launch core-cover production-mesh category.
- A subsequent general basic-shape inventory found 415 visible Engine basic
  shapes, but every one already carries an intentional project material; the
  count primarily consists of the accepted modular building shells, floors,
  parapets, trims, thresholds and small exterior utilities. There are no
  remaining LevelPrototyping/default-material actors in the launch envelope.
  Use concrete player-height evidence and exact site labels for any further
  replacement rather than treating Engine basic-shape geometry itself as a
  defect.

## 2026-08-16 launch-area awning recovery pass

- Six authored exterior awnings had previously been hidden after their black
  `WrinkledTarp` presentation was rejected, leaving visible launch-area
  frontages incomplete. The safe replacement pattern is to reuse the already
  imported Quixel Historic Desert Ruins corrugated sheet
  `Military_Trenches_Wall_Metal_Corrugated_06_ydxnbdns_High`, with an
  actor-only `MI_OT_Timber` material override. The source Quixel material was
  rejected in the current launch lighting because its upper face rendered
  nearly white; `MI_OT_Metal` remained too reflective. Do not modify either
  shared source material to compensate.
- `ABV_SS_005_ClinicMainAwning_V1` is the first completed replacement. It now
  sits above `Clinic_MainDoor` at location `(-5700.65, -1065.3, 35139.7)`,
  rotation `(pitch 0, yaw 0, roll -95)`, scale `(1.3, 0.4, 1.1)`. It is visible,
  non-colliding, navigation-irrelevant and overlap-disabled. Accepted close
  views are under `/private/tmp/abv_ss005_corrugated_awning_review_v1/`; exact
  package-save evidence is
  `/private/tmp/abv_ss005_corrugated_awning_exact_save_v1.json`. Unreal was
  authoritative-zero-dirty after the exact single-package save.
- A facade-damage experiment using the imported flat damaged-plaster modules
  was rejected before mutation because the pieces read as tall pasted strips
  rather than integrated erosion. Do not repeat that treatment without a
  geometry-aware corner/opening composition.
- The awning recovery category is now complete for the six known launch-area
  gaps. `ABV_SS_010_YardGateAwning_V1`,
  `ABV_SS_011_CheckpointDoorAwning_V1`, both
  `ABV_SS_012_ConsulateDoorAwning_*` actors and
  `ABV_SS_016_SubstationWestAwning_V1` now use the same accepted corrugated
  sheet plus actor-only timber finish. SS_010 retains the authored roughly
  four-metre gate span; SS_016 was rotated and centered on its west lintel.
  All six remain visual-only (`NoCollision`, no navigation, no overlaps), and
  no new actors or packages were created. Review images are under
  `/private/tmp/abv_ss010_yard_gate_corrugated_awning_review_v1/`,
  `/private/tmp/abv_ss011_ss012_corrugated_awning_review_v1/`, and
  `/private/tmp/abv_ss016_west_corrugated_awning_review_v1/`. Exact-save
  reports are the correspondingly named `*_exact_save_v1.json` files in
  `/private/tmp`. Unreal returned to authoritative zero dirty after every
  bounded save.

## 2026-08-16 SS_011 checkpoint gatepost correction

- `Checkpoint_GatePost_W` and `Checkpoint_GatePost_E` were proven to float
  approximately 150 cm above Landscape and presented as oversized plain
  prototype columns. Both existing actors now use the already imported
  Historic Desert Ruin Structure Stone S 06 mesh and its existing material;
  no new actor or shared asset was created.
- The west post is at `(6983.1598, 3916.9722, 34914.2238)`, pitch `-90`, yaw
  `8`, uniform scale `2.1`. The east post is at
  `(7783.6417, 3930.7607, 34914.2238)`, pitch `-90`, yaw `-12`, uniform scale
  `2.1`. Both preserve the checkpoint spacing, sit 3 cm into
  `LandscapeStreamingProxy_2_2_0`, retain visible query-and-physics collision
  and navigation relevance, and have overlap generation disabled.
- Review evidence is under `/private/tmp/abv_ss011_gatepost_stone_review_v1/`;
  exact-save evidence is
  `/private/tmp/abv_ss011_gatepost_stone_exact_save_v1.json`. Unreal returned
  to authoritative zero dirty after save.

## 2026-08-16 SS_016 rooftop utility correction

- Three visibly suspended rooftop utilities were proven against the exact
  `Core_SS_016_Roof` top plane at Z `35131.3`: the former barrel floated 46 cm,
  `Utility_Pipe_06` floated 100 cm, and `Utility_Pipe_07` floated 120 cm. The
  two pipes were lowered in place and renamed as west/east roof vents. The
  barrel actor now uses the imported Quixel Rusty Metal Barrel and is named
  `ABV_SS_016_Roof_RustBarrel_V1`. All three bottoms sit at Z `35128.3`, a
  3 cm roof embed; collision remains visible query-and-physics while navigation
  and overlaps are disabled.
- The three SS_016 rooftop cabinet actors were also retained in place but
  changed to the imported Quixel `Electric_Box_ullibjd_High` at uniform scale
  `1.4`, renamed `ABV_SS_016_RoofSwitchgear_A/B/C_V1`, and conformed to the
  same roof plane. This replaces the oversized repeated cabinet silhouettes
  with smaller production switchgear without creating actor packages or
  changing the authored row layout.
- Review evidence is under
  `/private/tmp/abv_ss016_rooftop_contact_review_v1/` and
  `/private/tmp/abv_ss016_rooftop_switchgear_review_v1/`. Exact-save evidence
  is `/private/tmp/abv_ss016_rooftop_contact_exact_save_v1.json` and
  `/private/tmp/abv_ss016_rooftop_cabinets_exact_save_v1.json`. Each bounded
  three-package save physically advanced the expected mtimes and returned
  Unreal to authoritative zero dirty.

## 2026-08-16 remaining launch-roof barrel finish

- An exact-package follow-up resolved the four remaining visible barrel
  placeholders: `Utility_Barrel_01/02` on `Core_SS_013_Roof` and
  `Utility_Barrel_10/11` on `Core_SS_017_Roof`. All four were
  `SM_Cylinder` prototype actors floating `46.0`, `46.0`, `46.0`, and
  `66.0 cm` above their exact roof support planes.
- Their existing actors now reuse the imported Quixel
  `Rusty_Metal_Barrel_teufceuda_High` at uniform scale `1`, with slight yaw
  variation and `3 cm` roof embed. They are labeled
  `ABV_SS_013_Roof_RustBarrel_W/E_V1` and
  `ABV_SS_017_Roof_RustBarrel_W/E_V1`. Visible collision is retained;
  navigation and overlap events are disabled.
- Read-only, apply, and exact-save reports are
  `/private/tmp/abv_remaining_barrels_exact_preflight_v1.json`,
  `/private/tmp/abv_remaining_roof_barrels_apply_v1.json`, and
  `/private/tmp/abv_remaining_roof_barrels_exact_save_v1.json`. Review
  captures are under `/private/tmp/abv_remaining_barrels_review_v1/`. Exactly
  four external-actor packages were saved and Unreal returned to zero dirty.

## 2026-08-16 launch-area facade utility correction

- The two original SS_016 wall electrical-box actors were retained, but their
  chamfer-cube placeholder meshes were replaced with the already imported
  Quixel `Electrical_Box_tdgecegda_High`. They are now named
  `ABV_SS_016_WestElectricalBox_V1` and
  `ABV_SS_016_EastElectricalBox_V1`, use uniform scale `1.2`, preserve their
  exact wall centers, and remain visible query-and-physics collision with
  navigation and overlaps disabled. Review evidence is under
  `/private/tmp/abv_ss016_wall_boxes_review_v1/`; exact-save evidence is
  `/private/tmp/abv_ss016_wall_boxes_exact_save_v1.json`.
- The south SS_003 Quixel electrical enclosure overlapped the central opening.
  `ABV_SS_003_PumpSouthElectricalBox_V1` was moved laterally into the exact
  solid bay between `Pump_Door_A` and `Pump_Window_01_Frame`; its final X
  bounds are `-10938.45` to `-10836.55`, leaving about `36.55 cm` clearance
  from each adjacent opening. Review evidence is under
  `/private/tmp/abv_ss003_meter_reposition_review_v1/`; exact-save evidence is
  `/private/tmp/abv_ss003_south_meter_exact_save_v1.json`.
- A follow-up exact opening-clearance audit found `OT_EXT_Meter_SS_013`
  correctly placed between `Depot_PedDoor` and `Depot_LoadingDoor`, with more
  than 3.2 m clearance on either side, so it was not changed. In contrast,
  `OT_EXT_Meter_SS_015` overlapped `MotorPool_Garage_A` by about 52 cm. That
  existing actor was moved from X `12224` to X `12000` in the solid south-wall
  bay, leaving `188.24 cm` from the west utility and `171.96 cm` from the
  garage panel. Its mesh, Y/Z, rotation, scale and `NoCollision` behavior were
  preserved. Reports are
  `/private/tmp/abv_ss013_ss015_meter_clearance_preflight_v1.json`,
  `/private/tmp/abv_ss015_meter_reposition_v1.json`, and
  `/private/tmp/abv_ss015_meter_exact_save_v1.json`; review captures are under
  `/private/tmp/abv_ss013_ss015_meter_clearance_review_v1/`. Each exact save
  returned Unreal to authoritative zero dirty.

## 2026-08-16 SS_003 and SS_015 rooftop production-utility finish

- `Utility_Cabinet_01` on `SS_003` and `Utility_Cabinet_02` on `SS_015` were
  the remaining large chamfer-cube rooftop cabinet placeholders visible in
  close oblique review. Their existing actor packages and XY positions were
  retained, while both now reuse the imported Quixel
  `Electric_Box_ullibjd_High` mesh at uniform scale `1.4`. They are named
  `ABV_SS_003_RoofSwitchgear_V1` and
  `ABV_SS_015_RoofSwitchgear_V1`, sit 3 cm into their exact roof support
  planes, retain visible query-and-physics collision, and are non-navigable
  with overlaps disabled.
- The two SS_015 roof cylinders `Utility_Barrel_07` and
  `Utility_Barrel_08` were likewise retained as actors but replaced with the
  already imported Quixel `Rusty_Metal_Barrel_teufceuda_High`, renamed
  `ABV_SS_015_Roof_RustBarrel_W_V1` and
  `ABV_SS_015_Roof_RustBarrel_E_V1`. Both use uniform scale `1`, slight yaw
  variation, and a verified 3 cm roof embed. Their visible collision remains;
  navigation and overlaps are disabled.
- Review evidence is under
  `/private/tmp/abv_ss003_ss015_roof_cabinets_review_v1/`. Apply/save reports
  are `/private/tmp/abv_ss003_ss015_roof_cabinets_apply_v1.json`,
  `/private/tmp/abv_ss003_ss015_roof_cabinets_exact_save_v1.json`,
  `/private/tmp/abv_ss015_roof_barrels_apply_v1.json`, and
  `/private/tmp/abv_ss015_roof_barrels_exact_save_v1.json`. Each two-package
  exact save physically advanced the expected mtimes and returned Unreal to
  authoritative zero dirty.

## 2026-08-16 launch-area ground-barrel production finish

- `Utility_Barrel_03` through `Utility_Barrel_06` were exact-resolved as four
  visible launch-area `SM_Cylinder` placeholders. Direct downward traces hit
  `LandscapeStreamingProxy_2_1_0` at every actor. The placeholders floated
  about `7.6 cm`, `10.4 cm`, `45.6 cm`, and `46.3 cm`, respectively.
- The four existing actor packages and XY positions were retained. Each actor
  now reuses the imported Quixel
  `Rusty_Metal_Barrel_teufceuda_High` at uniform scale `1`, with restrained
  yaw variation, visible query-and-physics collision, navigation disabled,
  overlaps disabled, and a verified `3 cm` terrain embed. The final labels are
  `ABV_OT_RustBarrel_03_V1` through `ABV_OT_RustBarrel_06_V1`.
- Apply and exact-save evidence is
  `/private/tmp/abv_ground_barrels_03_06_apply_v1.json` and
  `/private/tmp/abv_ground_barrels_03_06_exact_save_v1.json`; review captures
  are under `/private/tmp/abv_ground_barrels_03_06_review_v2/`. The save
  advanced exactly the four intended external-actor mtimes and returned
  Unreal to authoritative zero dirty.

## 2026-08-16 SS_003 exterior wall-box recovery

- `Pump_ElectricalBox_01/02` were exact-resolved as small chamfer-cube
  placeholders positioned `110 cm` inward from the west/east wall faces. They
  were therefore absent from their intended exterior elevations. Fixed traces
  distinguished the core wall inner planes (`X=-11480/-9720`) from the actual
  exterior planes (`X=-11520/-9680`).
- Both existing actor packages now use the imported Quixel
  `Electrical_Box_tdgecegda_High` at uniform scale `1.2`. They are labeled
  `ABV_SS_003_WestElectricalBox_V1` and
  `ABV_SS_003_EastElectricalBox_V1`, sit `2 cm` proud of the verified exterior
  wall planes in solid wall bays at `Y=-6100`, retain visible collision, and
  have navigation and overlap events disabled.
- Evidence is in
  `/private/tmp/abv_ss003_wall_boxes_exact_preflight_v1.json`,
  `/private/tmp/abv_ss003_wall_boxes_support_trace_v1.json`,
  `/private/tmp/abv_ss003_wall_box_bay_trace_v1.json`,
  `/private/tmp/abv_ss003_wall_boxes_apply_v1.json`,
  `/private/tmp/abv_ss003_wall_boxes_outer_plane_fix_v1.json`, and
  `/private/tmp/abv_ss003_wall_boxes_exact_save_v1.json`; final views are under
  `/private/tmp/abv_ss003_wall_boxes_review_v1/`. Exactly two packages were
  saved and Unreal returned to zero dirty.

## 2026-08-16 remaining launch-area facade-meter finish

- A bounded follow-up resolved the four remaining `OT_EXT_Meter_*` launch-area
  actors (`SS_005`, `SS_007`, `SS_011`, and `SS_018`) as decorative
  `Engine/BasicShapes/Cube` placeholders with navigation relevance still
  enabled. Their actor packages were retained; no actors or shared assets were
  created.
- The four actors now reuse the imported Quixel
  `Electrical_Box_tdgecegda_High` at uniform scale `1.2` and are named
  `ABV_SS_005_NorthElectricalMeter_V1`,
  `ABV_SS_007_NorthElectricalMeter_V1`,
  `ABV_SS_011_NorthElectricalMeter_V1`, and
  `ABV_SS_018_SouthElectricalMeter_V1`. The first three are fitted 2 cm proud
  of their verified north facade planes; the SS_018 unit is fitted 2 cm proud
  of its south facade plane. All remain decorative `NoCollision` actors, with
  navigation relevance and overlap events disabled.
- Apply evidence is
  `/private/tmp/abv_remaining_facade_meters_apply_v1.json`; exact-save evidence
  is `/private/tmp/abv_remaining_facade_meters_exact_save_v1.json`; review
  captures are under
  `/private/tmp/abv_remaining_facade_meters_review_v1/`. Exactly four actor
  packages advanced on disk and authoritative Unreal dirty state returned to
  zero.
- `Pump_Utility_01/02` were separately checked read-only. Direct support traces
  hit `Core_SS_003_Roof` roughly 270–290 cm above their mesh bottoms, proving
  those two cube utilities are inside the building footprint/interior rather
  than exterior launch-area defects. They were intentionally left unchanged;
  evidence is `/private/tmp/abv_ss003_freestanding_utilities_preflight_v1.json`.

## 2026-08-16 SS_018 side-wall utility finish

- Player-height west/east elevation review proved
  `Telecom_ElectricalBox_12/13` were still visible chamfer-cube placeholders on
  the SS_018 telecom building. Both existing actors were retained and now use
  `Electrical_Box_tdgecegda_High` at uniform scale `1.2`.
- They are named `ABV_SS_018_WestElectricalBox_V1` and
  `ABV_SS_018_EastElectricalBox_V1`; each sits 2 cm proud of its exact outer
  facade plane in a solid wall bay. Existing visible query-and-physics
  collision was retained while navigation relevance and overlap events were
  disabled.
- Apply/save evidence is `/private/tmp/abv_ss018_side_boxes_apply_v1.json` and
  `/private/tmp/abv_ss018_side_boxes_exact_save_v1.json`; before/after views
  are under `/private/tmp/abv_ss018_side_boxes_review_v1/`. Exactly two actor
  packages advanced on disk and Unreal returned to authoritative zero dirty.

## 2026-08-16 SS_011 checkpoint side-wall utility finish

- Exact west/east player-height review proved
  `Checkpoint_ElectricalBox_07/08` were still chamfer-cube placeholders on
  solid SS_011 facade bays. Their existing packages were retained and now use
  `Electrical_Box_tdgecegda_High` at uniform scale `1.2`.
- The production labels are `ABV_SS_011_WestElectricalBox_V1` and
  `ABV_SS_011_EastElectricalBox_V1`. Each is fitted 2 cm proud of the verified
  outer wall plane, retains visible query-and-physics collision, and has
  navigation relevance and overlap events disabled.
- Apply/save evidence is `/private/tmp/abv_ss011_side_boxes_apply_v1.json` and
  `/private/tmp/abv_ss011_side_boxes_exact_save_v1.json`; review captures are
  under `/private/tmp/abv_ss011_side_boxes_review_v1/`. Exactly two packages
  advanced and authoritative dirty state returned to zero.

## 2026-08-16 SS_018 rooftop cabinet stale-inventory closure

- The offline launch inventory still classified `Utility_Cabinet_06` as an
  `SM_ChamferCube`, but the exact live actor package proved that record stale.
  The actor already uses imported Quixel
  `Electrical_Cabinet_ujzfde2_High` at scale `0.75`, is flush to the SS_018
  roof, has visible collision, and is already non-navigable with overlaps
  disabled. The mutation gate stopped before `modify()` and no save occurred.
- Exact evidence is
  `/private/tmp/abv_ss018_roof_cabinet_exact_preflight_v2.json`; review views
  are under `/private/tmp/abv_ss018_roof_cabinet_review_v1/`. Treat the rooftop
  cabinet as production-finished unless a new concrete visual defect is found.

## 2026-08-16 SS_006 water-tower utility support audit

- The four `Tower_Utility_01..04` actors were re-audited after a below-surface
  trace appeared to show a large gap. That apparent defect was invalid: the
  trace began below the Landscape and therefore struck buried decorative
  ground meshes (or returned no hit), not the visible authoritative surface.
- A final top-down trace from below the overhead platform, with all four boxes
  ignored, hit `LandscapeStreamingProxy_1_2_0` at every exact actor XY. Each
  imported `Electric_Box_ullibjd_High` bottom is exactly `2.0 cm` embedded in
  the Landscape. All four boxes are correctly grounded and were left
  unchanged; no package was saved and authoritative dirty state remained zero.
- Final evidence is
  `/private/tmp/abv_water_tower_utilities_support_final_v1.json`; player-height
  review views are under
  `/private/tmp/abv_water_tower_utilities_review_v1/`.
- Durable trace rule: for terrain contact, start above the expected Landscape
  surface while ignoring the audited actor and any overhead blocker already
  excluded by the chosen start height. A trace launched from `actor bottom -
  1 cm` can already be below a correctly embedded Landscape surface and must
  not be interpreted as proof of floating.

## 2026-08-16 SS_018 rooftop antenna-mast finish

- The three SS_018 rooftop equipment bases were exact-resolved as already
  imported production assets (Quixel metal tank, electrical cabinet, and
  electrical box). They were preserved unchanged. The three attached antenna
  masts were still long, square `SM_Cube` prototype columns and still affected
  navigation.
- Their existing actor packages now use `/Engine/BasicShapes/Cylinder` with
  `MI_OT_Metal`, yielding round `8 cm` diameter masts at the original intended
  heights (`250`, `320`, and `210 cm`). Each mast is centered on its own
  equipment base and embedded `2 cm` into the verified base top. Production
  labels are `ABV_SS_018_RoofAntennaMast_West_V1`,
  `ABV_SS_018_RoofAntennaMast_Center_V1`, and
  `ABV_SS_018_RoofAntennaMast_East_V1`.
- The thin decorative masts now use the `NoCollision` profile, do not affect
  navigation, and generate no overlaps. Evidence is in
  `/private/tmp/abv_ss018_rooftop_masts_plan_v1.json`,
  `/private/tmp/abv_ss018_rooftop_masts_collision_fix_v1.json`, and
  `/private/tmp/abv_ss018_rooftop_masts_exact_save_v1.json`; before/after views
  are under `/private/tmp/abv_ss018_rooftop_masts_review_v1/`. Exactly three
  actor packages advanced and authoritative Unreal dirty state returned to
  zero.
- UE detail: changing a StaticMeshComponent mesh can reapply the source
  collision profile. For guaranteed decorative collision, call
  `set_collision_profile_name("NoCollision")` as well as
  `set_collision_enabled(NO_COLLISION)` after `set_static_mesh()`.

## 2026-08-16 SS_012 freight-depot rooftop equipment closure

- The offline inventory still named `Depot_RoofVent_01..03` as cube roof
  vents. Exact live package resolution proved that record stale: the three
  actors already use the imported Quixel electrical cabinet, metal water tank,
  and electrical box meshes respectively. Every item is flush to the roof,
  uses `BlockAll` visible collision, is non-navigable, and generates no overlap
  events. No mutation or save was needed.
- Read-only evidence is
  `/private/tmp/abv_ss012_depot_roofvents_preflight_v1.json`. Treat these three
  rooftop actors as production-finished unless a new concrete visual defect is
  found.

## 2026-08-16 SS_004 Tea House facade-sign finish

- Exact live review proved `Tea_House_Sign` was still a bright cyan prototype
  slab above the Tea House frontage. Its existing external-actor package was
  retained and the actor is now named `ABV_SS_004_TeaHouseTimberSign_V1`.
- The board keeps its authored dimensions and placement but now uses the
  existing `MI_OT_Timber` material, reads as a restrained timber fascia/sign
  panel, and is decorative `NoCollision` with navigation relevance and overlap
  events disabled.
- Apply evidence is `/private/tmp/abv_teahouse_sign_finish_v1.json`; exact-save
  evidence is `/private/tmp/abv_teahouse_sign_exact_save_v1.json`; review views
  are under `/private/tmp/abv_sign_ladder_review_v1/`. Exactly one actor package
  advanced on disk and authoritative Unreal dirty state returned to zero.

## 2026-08-16 SS_006 water-tower ladder finish

- `WaterTower_Ladder` was a solid `25 x 100 x 1100 cm` prototype slab. Its
  existing external-actor package is now `ABV_SS_006_WaterTowerLadder_V1` and
  contains one `HISM_WaterTowerLadder` component: two narrow rails plus 31
  evenly spaced rungs, all instanced from `/Engine/BasicShapes/Cube`.
- The ladder uses the already imported rusted-metal crate material, which was
  already proven compatible with HISM rendering. Its 33 visible instances use
  `BlockAll` collision matching the rendered rails/rungs, do not affect
  navigation, generate no overlap events, do not tick, and do not replicate.
  The old slab root remains only as a hidden, non-colliding component.
- Preview evidence is `/private/tmp/abv_water_tower_ladder_preview_v1.json`;
  exact-save evidence is
  `/private/tmp/abv_water_tower_ladder_exact_save_v1.json`; review captures are
  under `/private/tmp/abv_water_tower_ladder_review_v1/`. Exactly the existing
  ladder actor package advanced on disk and Unreal returned to zero dirty.
- Durable UE 5.8 lessons from the rejected first preview:
  `HierarchicalInstancedStaticMeshComponent` has no Python
  `mark_render_state_dirty()` method. Also, assigning a material not yet marked
  for Instanced Static Mesh use can automatically dirty that shared material.
  Do not try to clear that live material mutation by reloading the material
  while a new HISM still references it; that package reload pinned this editor.
  The safe recovery was to discard the unsaved preview by restarting only the
  isolated editor, then retry with an already-HISM-compatible material. The
  original ladder and `MI_OT_Metal` files never advanced on disk during the
  rejected attempt.

## 2026-08-16 SS_003 and SS_015 rooftop vent-pipe finish

- Exact live resolution proved both roof cabinets and both SS_015 barrels were
  already imported production assets. Four remaining `SM_Cylinder` prototype
  pipes were the only live stale entries in this bounded roof-utility set.
- Their existing packages are now
  `ABV_SS_003_RoofVentPipe_W_V1`,
  `ABV_SS_003_RoofVentPipe_E_V1`,
  `ABV_SS_015_RoofVentPipe_W_V1`, and
  `ABV_SS_015_RoofVentPipe_E_V1`. Each uses the Engine cylinder at a cleaner
  `14 cm` diameter, preserves its original roof contact and height, and uses
  the already imported rusted-metal material.
- The thin decorative vents are now `NoCollision`, non-navigable, non-
  overlapping, non-replicated, and non-ticking. Apply/save evidence is
  `/private/tmp/abv_ss003_ss015_roof_pipes_apply_v1.json` and
  `/private/tmp/abv_ss003_ss015_roof_pipes_exact_save_v1.json`; before/after
  review captures are under `/private/tmp/abv_roof_pipe_review_v1/`. Exactly
  four actor packages advanced and Unreal returned to zero dirty.

## 2026-08-16 launch-sign live closure

- Exact package resolution rechecked the three remaining landmark boards and
  all eight Bazaar stall boards. The Bazaar boards already use the approved
  timber finish and `NoCollision`; their prior cleanup is still valid and they
  were not reopened. The three `OT_SIGNBOARD_SS_004`, `...SS_013`, and
  `...SS_017` actors remain explicitly tagged `LandmarkSignBoard`/
  `SunscarOldTownLandmarkSignV1` and use the authored accent finish. They are
  not accidental blockout geometry, so no speculative replacement was made.
- Read-only evidence is `/private/tmp/abv_launch_signs_live_v1.json`; review
  captures are under `/private/tmp/abv_launch_signs_review_v1/before/`.

## 2026-08-16 SS_015 Motor Pool repair-prop finish

- Four remaining `SM_ChamferCube` repair props were converted in place to the
  already owned Nanite Junkyard rusty-metal storage crate. Their existing
  actor packages are retained and now use production labels
  `ABV_SS_015_MotorPoolRepairCrate_A_V1` through `_D_V1`.
- Every crate is uniformly scaled to `0.9`, keeps the authored XY placement,
  preserves the original support bottom exactly, and receives a restrained
  yaw variation (`12`, `-17`, `8`, and `-25` degrees). The real ten-hull mesh
  collision remains `BlockAll`, navigation-relevant and non-overlapping so the
  authored low-cover behavior is retained.
- Apply/save evidence is
  `/private/tmp/abv_motorpool_repair_crates_apply_v1.json` and
  `/private/tmp/abv_motorpool_repair_crates_exact_save_v1.json`; review images
  are under `/private/tmp/abv_industrial_blocks_review_v1/motorpool_after/`.
  Exactly four existing external-actor packages advanced and Unreal returned
  to zero dirty.

## 2026-08-16 SS_016 Power Substation equipment finish

- Six visibly suspended `SM_Cube` equipment blocks were replaced in place by
  the already imported Nanite Quixel
  `Electrical_Cabinet_ujzfde2_High`, preserving the six authoritative actor
  packages and cover locations. Production labels are
  `ABV_SS_016_SubstationCabinet_01_V1` through `_06_V1`.
- The four principal cabinets use uniform scales `1.65`, `1.90`, `1.55`, and
  `1.80`; the rear pair use `1.25`. The front-row clear passages measure
  approximately `131.7`, `151.2`, and `158.1 cm`, retaining walkable tactical
  gaps. All six keep real convex `BlockAll` collision, navigation relevance,
  no overlap events, no replication and no tick.
- Six direct world traces hit only `Core_SS_016_F1_Floor` at
  `Z=34811.30 cm`. The cabinet bases were placed with a `0.5 cm` natural embed,
  eliminating the inherited cube-pivot suspension. Apply, trace, and save
  evidence is `/private/tmp/abv_substation_cabinets_apply_v1.json`,
  `/private/tmp/abv_substation_cabinets_ground_fix_v1.json`, and
  `/private/tmp/abv_substation_cabinets_exact_save_v1.json`; review captures
  are under `/private/tmp/abv_industrial_blocks_review_v1/substation_after/`.
  Exactly six existing external-actor packages advanced and Unreal returned
  to zero dirty.
- UE Python detail: `StaticMesh.get_material(0)` returns the material interface
  directly in this UE 5.8 wrapper; do not dereference a nonexistent
  `.material_interface` field. The rejected first call failed before any
  mutation and left the editor clean.

## 2026-08-16 SS_017 Covered Bazaar canopy-post finish

- Exact live resolution distinguished the already finished six Quixel wooden
  market tables from the eight authored north/south stall collision bodies.
  Those stall bodies remain unchanged because they preserve the approved
  low-cover and storefront layout.
- The four remaining visible square `SM_Cube` canopy poles were converted in
  place to Engine cylinder posts while retaining the original `12 x 12 x
  300 cm` occupied bounds and the existing Old Town metal finish. Production
  labels are `ABV_SS_017_BazaarCanopyPost_A_V1` through `_D_V1`.
- Visible `BlockAll` collision is retained, while navigation relevance is
  disabled for these thin posts; overlap events, replication and tick remain
  disabled. Apply/save evidence is
  `/private/tmp/abv_bazaar_posts_apply_v1.json` and
  `/private/tmp/abv_bazaar_posts_exact_save_v1.json`; review captures are
  under `/private/tmp/abv_bazaar_posts_review_v1/`. Exactly four existing
  external-actor packages advanced and Unreal returned to zero dirty.

## 2026-08-16 SS_016 Substation compound-wall finish

- The four `SS_016_Fence_*` actors were verified live as solid 20–26 metre
  `SM_Cube` metal slabs. The imported corrugated barrier was evaluated but its
  shared GLTF base material is not enabled for instanced static meshes; that
  source was not edited or forced into an unsafe per-panel actor expansion.
- The four existing authoritative perimeter actors are now named
  `ABV_SS_016_SubstationCompoundWall_{East,North,South,West}_V1` and use the
  existing world-aligned Abiverd ruin-brick finish. Their exact transforms,
  occupied bounds, `BlockAll` collision and navigation relevance are
  unchanged, so the approved site boundary and routes are preserved while the
  enclosure reads as a plausible local masonry compound rather than metal
  blockout slabs.
- Apply/save evidence is
  `/private/tmp/abv_substation_compound_walls_apply_v1.json` and
  `/private/tmp/abv_substation_compound_walls_exact_save_v1.json`; review
  captures are under `/private/tmp/abv_substation_compound_walls_review_v1/`.
  Exactly four actor packages advanced and Unreal returned to zero dirty.
## 2026-08-16 SS_004 Tea House furniture material finish

- Verified live that the four SS_004 tea benches and two tea tables had already been converted from blockout cubes to owned Quixel furniture meshes. The remaining defect was six generic `MI_OT_Timber` material overrides masking those imported assets' authored finishes.
- Restored each bench/table component to its matching imported Quixel material while preserving the existing mesh, full transform, collision envelope, navigation settings, and courtyard layout.
- Production labels are `ABV_SS_004_TeaBench_01A_V1`, `ABV_SS_004_TeaBench_01B_V1`, `ABV_SS_004_TeaBench_02A_V1`, `ABV_SS_004_TeaBench_02B_V1`, `ABV_SS_004_TeaTable_01_V1`, and `ABV_SS_004_TeaTable_02_V1`.
- Exact saved external-actor packages:
  - `/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/D/LZ/CWM9L7QJO0UF4FU1QNUSV9`
  - `/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/3/7Z/84X2BAF9N34UG6RW89UY82`
  - `/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/0/FJ/G96Q2MF7IYN9KKV0LXION7`
  - `/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/1/NP/DMEYN4DNRKLYJNBYLIUVGQ`
  - `/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/C/9H/J5CZ0O2HI2RVLR1JFEP9MG`
  - `/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/2/WQ/I2XHAT3DUBJ2L4R4O666FQ`
- Evidence: `/private/tmp/abv_tea_furniture_live_probe_v1.json`, `/private/tmp/abv_tea_furniture_material_apply_v1.json`, `/private/tmp/abv_tea_furniture_material_exact_save_v1.json`, and `/private/tmp/abv_tea_furniture_review_v1/`.
- Filesystem mtimes advanced for exactly the six intended packages and authoritative Unreal dirty-package state returned to zero after the exact save.
## 2026-08-16 SS_004 Tea House canopy finish

- Exact live audit confirmed `Tea_Canopy` was still a visible 650 x 360 x 10 cm LevelPrototyping cube with `BlockAll` collision/navigation, supported by four 12 x 12 x 290 cm square LevelPrototyping poles.
- Converted the existing canopy actor in place to the owned Nanite wrinkled-tarp mesh `/Game/Maps/Sunscar/Art/Heritage/Props/WrinkledTarp/vieldbo_tier_1/StaticMeshes/vieldbo_tier_1` at uniform scale `2.35`, retaining the original footprint center and exact underside elevation. Its authored material `MI_ABV_WrinkledTarp` is retained; decorative canopy collision/navigation are disabled.
- Converted the four existing square pole actors in place to `/Engine/BasicShapes/Cylinder`, retaining every pole's exact occupied bounds and `BlockAll` visible collision while disabling navigation relevance.
- Production labels: `ABV_SS_004_TeaCanopy_WrinkledTarp_V1` and `ABV_SS_004_TeaCanopyPost_A_V1` through `_D_V1`.
- Exact saved packages:
  - `/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/B/IH/34H0PQZSSOXR897P94LVES`
  - `/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/C/ED/POI1E3KOM10RTQOK1N31A7`
  - `/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/9/UY/RJK3QSTJ3AEPS76OF5H4DO`
  - `/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/D/W2/L0RCJFMQ1R37983RZXNJNK`
  - `/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/C/WF/QE7EGS4TU1KQGJN22HQ8J0`
- Evidence: `/private/tmp/abv_tea_canopy_live_probe_v1.json`, `/private/tmp/abv_tea_canopy_apply_v1.json`, `/private/tmp/abv_tea_canopy_exact_save_v1.json`, and `/private/tmp/abv_tea_canopy_review_v1/`.
- Player-height/elevated review confirms the tarp reads as a fabric shade, its poles meet the canopy and terrain, circulation and furniture remain unobstructed, exact five-file mtimes advanced, and authoritative dirty state returned to zero.
## 2026-08-16 SS_003 Pump Station utility finish

- Exact live audit found `Pump_Utility_01` and `Pump_Utility_02` were still solid LevelPrototyping control-box cubes with `BlockAll`/navigation, while `Pump_Utility_03` was an 18 x 18 x 240 cm square metal cue hanging in the south doorway.
- Converted the two control-box actors in place to the owned Nanite Quixel `Electrical_Box_tdgecegda_High` mesh with its authored material; decorative collision/navigation/overlaps are disabled.
- Converted the square mast to a round Engine cylinder, then moved it out of the doorway to the west wall as `ABV_SS_003_WestWallDownpipe_V1`, half-set into the facade and nonblocking. The south entrance is now visually and physically clear.
- Production labels: `ABV_SS_003_NorthPumpControlBox_V1`, `ABV_SS_003_SouthPumpControlBox_V1`, and `ABV_SS_003_WestWallDownpipe_V1`.
- Exact saved packages:
  - `/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/9/ES/X6MN4NF3ZXORLDXG3KBYHE`
  - `/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/E/0J/OML53APQGJOCRYZZ2988YI`
  - `/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/2/86/21BUOVJ4Z8IVVH4XKRYHR5`
- Evidence: `/private/tmp/abv_ss003_pump_utilities_live_v1.json`, `/private/tmp/abv_ss003_pump_utilities_apply_v1.json`, `/private/tmp/abv_ss003_service_mast_refit_v1.json`, `/private/tmp/abv_ss003_pump_utilities_exact_save_v1.json`, and before/after captures under `/private/tmp/abv_ss003_pump_utilities_*_v1/`.
- Exact three-file mtimes advanced and authoritative Unreal dirty-package state returned to zero.

## 2026-08-16 SS_017 Covered Bazaar stall-body finish

- Fresh player-height closure captures proved the eight intentional
  `Bazaar_[N/S]_Stall_01..04` low-cover bodies still read as dark blockout
  cubes even though their positions, dimensions and collision layout were
  valid. Each existing actor remains an exact `320 x 250 x 90 cm` market
  counter with its original transform and `BlockAll` gameplay collision.
- Finished the four north and four south actors in two separately gated
  four-package batches by applying the existing world-aligned Abiverd
  ruin-brick material. Production labels are
  `ABV_SS_017_BazaarMasonryStall_N01_V1` through `_N04_V1` and
  `ABV_SS_017_BazaarMasonryStall_S01_V1` through `_S04_V1`.
- Navigation relevance, overlap events, replication and tick are disabled;
  the intentional visible low-cover collision remains. No transforms,
  dimensions, building pieces, routes or shared materials were changed.
- UE 5.8 Python note: `Transform.equals()` accepts no tolerance argument in
  this wrapper. The first north actor was the sole dirty preview when that
  assertion failed; the recovery probe proved its exact ownership and state,
  and the batch resumed using explicit numeric transform comparisons before
  any save.
- Evidence: `/private/tmp/abv_ss017_stalls_finish_probe_v1.json`,
  `/private/tmp/abv_ss017_stalls_north_recovery_probe_v1.json`,
  `/private/tmp/abv_ss017_stalls_north_apply_v1.json`,
  `/private/tmp/abv_ss017_stalls_north_exact_save_v1.json`,
  `/private/tmp/abv_ss017_stalls_south_apply_v1.json`,
  `/private/tmp/abv_ss017_stalls_south_exact_save_v1.json`, and review images
  under `/private/tmp/abv_ss017_stalls_finish_review_v1/`.
- Exact mtimes advanced for the intended eight existing external-actor
  packages only, and authoritative Unreal dirty-package state returned to
  zero after both saves.

## 2026-08-16 Launch-building flat-roof material completion

- Exact live resolution confirmed five launch-area roof slabs were the only
  core flat roofs still using the generic `MI_OT_Metal` finish:
  `Core_SS_003_Roof`, `Core_SS_013_Roof`, `Core_SS_015_Roof`,
  `Core_SS_016_Roof`, and `Core_SS_018_Roof`.
- Changed only their material overrides to the existing authored
  `MI_OT_WeatheredConcreteGround_WorldAligned`, matching the already finished
  SS_004/005/007/010/011/012/017 roof system. Exact transforms, dimensions,
  `BlockAll` collision, navigation relevance and structural labels are
  unchanged. Added the existing horizontal-surface/review tags only.
- Review captures show the prior bright metallic slabs now read as restrained
  tan flat roofs while rooftop equipment remains untouched. Evidence:
  `/private/tmp/abv_launch_metal_roofs_probe_v1.json`,
  `/private/tmp/abv_launch_metal_roofs_apply_v1.json`,
  `/private/tmp/abv_launch_metal_roofs_exact_save_v1.json`, and images under
  `/private/tmp/abv_launch_metal_roofs_review_v1/`.
- Exactly five existing external-actor package mtimes advanced and
  authoritative Unreal dirty-package state returned to zero.

## 2026-08-16 Launch-building facade-conduit completion

- Sixteen remaining facade-conduit cues at SS_004, SS_005, SS_007, SS_010,
  SS_011, SS_012, SS_017 and SS_018 were verified live as thin square Engine
  cubes (`9 cm` section; `170–180 cm` runs), already nonblocking but still
  navigation-relevant.
- Converted the sixteen existing actors in place to Engine cylinders while
  preserving each exact occupied run length and center. The existing Old Town
  metal material is retained. Production labels follow
  `ABV_<site>_FacadeConduit_{Vertical,Horizontal}_V1`.
- All conduit components remain `NoCollision`; navigation relevance, overlap
  events, replication and tick are disabled. No building, route, material
  asset or structural actor was changed.
- Evidence is in the four probe/apply/exact-save sets:
  `/private/tmp/abv_ss004_ss005_conduits_*_v1.json`,
  `/private/tmp/abv_ss007_ss010_conduits_*_v1.json`,
  `/private/tmp/abv_ss011_ss012_conduits_*_v1.json`, and
  `/private/tmp/abv_ss017_ss018_conduits_*_v1.json`; close review images for
  the first verified pattern are under
  `/private/tmp/abv_ss004_ss005_conduits_review_v1/`.
- Exact mtimes advanced for the intended sixteen existing actor packages, in
  four separately gated batches; authoritative Unreal dirty state returned to
  zero after every exact save.

## 2026-08-16 Launch-building electrical-meter material completion

- Exact live resolution proved the four apparent remaining utility-meter
  cubes at SS_005, SS_007, SS_011 and SS_018 had already been converted to
  the owned Nanite Quixel `Electrical_Box_tdgecegda_High`; the stale inventory
  reflected their prior state.
- The remaining defect was a generic `MI_OT_Metal` override masking the
  imported mesh's authored Quixel material. Restored the authored
  `MI_OT_FAB_P1A_002_tdgecegda` on the four existing actors only.
- Meshes, full transforms, occupied bounds, labels, `NoCollision` and disabled
  navigation are unchanged. Evidence:
  `/private/tmp/abv_launch_remaining_meters_probe_v1.json`,
  `/private/tmp/abv_launch_remaining_meters_material_apply_v1.json`, and
  `/private/tmp/abv_launch_remaining_meters_material_exact_save_v1.json`.
  Exact four-package mtimes advanced and Unreal returned to zero dirty.

## 2026-08-16 Launch-building stone-threshold completion

- Exact live resolution found eight launch-area doorway thresholds at SS_003,
  SS_004, SS_005 and SS_007 still rendered with the generic metal finish.
  Their existing `143 x 48 x 8 cm` forms, positions and doorway clearances
  were already valid.
- Finished the existing actors in two separately gated four-package batches
  using the authored world-aligned
  `MI_OT_WeatheredConcreteGround_WorldAligned` material. Production labels
  identify the exact site and doorway orientation, from
  `ABV_SS_003_StoneThreshold_West_V1` through
  `ABV_SS_007_StoneThreshold_East_V1`.
- Preserved every transform and occupied bound. The decorative sills remain
  `NoCollision`; navigation relevance, overlap events, replication and tick
  are disabled. No doorway, building, Landscape, material asset or route was
  modified.
- UE 5.8 Python note: `StaticMeshComponent` does not expose
  `set_generate_overlap_events()` in this wrapper; use
  `set_editor_property('generate_overlap_events', False)`. The initial call
  stopped after the first actor became dirty in memory; the recovery gate
  accepted only that exact package, resumed idempotently and verified the
  intended four-package scope before saving.
- Evidence: `/private/tmp/abv_launch_thresholds_probe_v1.json`,
  `/private/tmp/abv_launch_thresholds_batch_a_apply_v1.json`,
  `/private/tmp/abv_launch_thresholds_batch_a_exact_save_v1.json`,
  `/private/tmp/abv_launch_thresholds_batch_b_apply_v1.json`, and
  `/private/tmp/abv_launch_thresholds_batch_b_exact_save_v1.json`.
  Exact mtimes advanced for the intended eight existing actor packages and
  authoritative Unreal dirty-package state returned to zero after each save.

## 2026-08-16 Launch rooftop-switchgear authored-material recovery

- An exact six-actor live probe compared the component overrides on the
  launch-area rooftop switchgear with each imported mesh's authored material.
  SS_003 and SS_015 alone still carried the inherited generic
  `MI_OT_Metal` override; SS_016 A/B/C and the SS_018 cabinet already matched
  their authored materials and were left untouched.
- Restored the authored Quixel `FAB_P1A_003_ullibjd/MatID_1` material on only
  `ABV_SS_003_RoofSwitchgear_V1` and
  `ABV_SS_015_RoofSwitchgear_V1`. Meshes, full transforms, bounds, collision,
  navigation, labels and the source asset remained unchanged.
- Evidence: `/private/tmp/abv_launch_roof_switchgear_material_probe_v1.json`,
  `/private/tmp/abv_ss003_ss015_roof_switchgear_material_apply_v1.json`, and
  `/private/tmp/abv_ss003_ss015_roof_switchgear_material_exact_save_v1.json`.
  Exactly two external-actor package mtimes advanced and authoritative Unreal
  dirty state returned to zero.

## 2026-08-16 SS_006 water-tower compound wall finish

- Exact live resolution proved the eight perimeter wall/lintel actors around
  the SS_006 water-tower compound were valid structural Engine-cube geometry
  with working `QueryAndPhysics` collision and navigation, but their bright
  `MI_OT_Stucco_WorldAligned` finish still read as prototype geometry.
- Changed only the material override on the north, west, south-left,
  south-right, east-left, east-right, east lintel and south lintel actors to
  the existing `MI_ABV_RuinBrick_WorldAligned`. Full transforms, bounds,
  openings, collision, navigation and structural labels were preserved.
- The eight actors were processed and exact-saved in two separately gated
  four-package batches. Review captures confirm the perimeter now reads as a
  coherent Abiverd ruin-brick compound rather than a white blockout:
  `/private/tmp/abv_ss006_compound_walls_review_v1/southwest_oblique.png` and
  `/private/tmp/abv_ss006_compound_walls_review_v1/east_player.png`.
- Evidence: `/private/tmp/abv_ss006_compound_walls_material_probe_v1.json`,
  `/private/tmp/abv_ss006_compound_walls_batch_a_apply_v1.json`,
  `/private/tmp/abv_ss006_compound_walls_batch_a_exact_save_v1.json`,
  `/private/tmp/abv_ss006_compound_walls_batch_b_apply_v1.json`, and
  `/private/tmp/abv_ss006_compound_walls_batch_b_exact_save_v1.json`.
  Exact eight-package mtimes advanced and authoritative Unreal dirty state
  returned to zero after each save.

## 2026-08-16 SS_006 water-tower pillar finish

- A fresh post-fix 13-site oblique set under
  `/private/tmp/abv_launch_buildings_oblique_v3/` confirmed the remaining
  large SS_006 blockout read was the `400 x 400 x 1200 cm`
  `Core_SS_006_TowerPillar`, still using smooth facade stucco beneath the
  already finished tower platform, metal braces and ruin-brick perimeter.
- Changed only that existing actor's material override to the established
  `MI_OT_WeatheredConcreteGround_WorldAligned`, giving the modern utility
  tower a weathered structural-concrete read. Its exact transform, bounds,
  `BlockAll` query-and-physics collision, navigation and overlap state were
  numerically preserved.
- Review images are under
  `/private/tmp/abv_ss006_tower_pillar_finish_review_v1/`. Exact evidence:
  `/private/tmp/abv_ss006_tower_pillar_finish_probe_v1.json`,
  `/private/tmp/abv_ss006_tower_pillar_finish_apply_v1.json`, and
  `/private/tmp/abv_ss006_tower_pillar_finish_exact_save_v1.json`.
  The one intended actor package mtime advanced and authoritative Unreal dirty
  state returned to zero.
- The four bright small SS_006 ground units were separately resolved as the
  intentionally upgraded `Tower_Utility_01..04` Quixel electric boxes with
  saved terrain-conformed transforms, not leftover graybox cubes. A current
  player-height comparison nevertheless proved the source-white material still
  read like four editor blocks against the finished compound. Following the
  already accepted SS_018 ground-cabinet precedent, only their component
  material overrides now use the existing weathered `MI_OT_Metal`.
- The Quixel meshes, exact full transforms, `112.09 x 26.38 x 107.67 cm`
  occupied dimensions, query-and-physics collision, disabled navigation and
  source assets are unchanged. Review:
  `/private/tmp/abv_ss006_utility_finish_review_v1.png`; exact evidence:
  `/private/tmp/abv_ss006_utility_finish_apply_v1.json` and
  `/private/tmp/abv_ss006_utility_finish_exact_save_v1.json`. Exactly four
  actor-package mtimes advanced and authoritative Unreal dirty state returned
  to zero.

## 2026-08-16 SS_015 oil-stain decal experiment and rollback

- The scoped imported-content inventory found no existing project decal
  material, but did confirm the owned Quixel oil-stain texture set under
  `/Game/Maps/Sunscar/Art/Quixel/Downloaded/FAB_SUP_003_sdjmigi/`.
- Created and exact-saved the map-art material
  `/Game/Maps/Sunscar/Art/Heritage/Materials/M_ABV_OilStain_Decal` using the
  existing Quixel base-color and opacity textures, translucent deferred-decal
  domain, and constant roughness `0.82`. No source Quixel asset was edited.
- UE 5.8 Python/API lesson: `Material.decal_blend_mode` is deprecated and
  protected, and `Material.expressions` is also protected. Configure modern
  decals with `material_domain=MD_DEFERRED_DECAL`, a supported blend mode and
  explicit material-output connections; retain direct references to created
  expressions instead of attempting to read the protected expression array.
- A single unsaved preview actor,
  `ABV_SS_015_MotorPool_OilStain_A_V1`, was tested on the exactly traced
  `Core_SS_015_F1_Floor`. The floor support was level, but targeted top-down,
  oblique and player-height captures did not prove a readable decal on that
  receiver. The pilot therefore failed visual acceptance and was rolled back
  rather than saved.
- Rollback verification: the preview actor is absent, its proposed external
  actor package
  `/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/7/MM/6SCJ4YH0X0TACPRXHTL1EC`
  has no file on disk, and authoritative Unreal dirty state returned to zero.
  Do not repeat this exact SS_015 receiver test without first proving the
  floor's decal-receive/render path. Evidence:
  `/private/tmp/abv_decal_asset_inventory_v1.json`,
  `/private/tmp/abv_decal_api_probe_v1.json`,
  `/private/tmp/abv_oilstain_decal_material_apply_v1.json`,
  `/private/tmp/abv_oilstain_decal_material_exact_save_v1.json`,
  `/private/tmp/abv_ss015_oilstain_preflight_v1.json`,
  `/private/tmp/abv_ss015_oilstain_review_v2/`, and
  `/private/tmp/abv_ss015_oilstain_rollback_v1.json`.

## 2026-08-16 SS_013 Freight Depot east-facade production polish

- A fresh Game View/player-height review exposed the Freight Depot east
  approach as a concrete remaining flat-elevation defect: approximately
  24 m of flaked-plaster facade around the existing 2 m loading opening had no
  depth rhythm.
- Added three visual-only instances to the existing
  `ABV_OldTown_PakistanWallFacade_HISM_V1` actor's
  `HISM_PakistanWallModular16` component. World locations are
  `(12329.289,-850,34780.028)`, `(12329.289,-225,34780.028)` and
  `(12329.289,1000,34780.028)`, all yaw `90`, uniform scale `1`.
- Direct wall traces proved the three placements are on the two solid east
  shell bays; direct downward traces hit only Landscape at approximately
  Z `34779.5`. The closest pier remains 625 cm from the loading opening. The
  building shell, opening, routes, Landscape, collision and navigation were
  unchanged.
- The existing shared HISM component remains `NoCollision`, non-navigable and
  now contains 41 instances. Only its existing external-actor package
  `/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/4/XJ/GOWVSDB53YHV8I1OQ2ZTN7`
  was exact-saved; its mtime advanced and authoritative Unreal dirty state
  returned to zero.
- Before/after player-height evidence is under
  `/private/tmp/abv_ss013_east_facade_piers_review_v1/`; exact evidence:
  `/private/tmp/abv_ss013_east_facade_piers_preflight_v1.json`,
  `/private/tmp/abv_ss013_east_facade_piers_preview_v1.json`,
  `/private/tmp/abv_ss013_east_facade_piers_refine_v1.json`, and
  `/private/tmp/abv_ss013_east_facade_piers_exact_save_v1.json`.

## 2026-08-16 launch-area Landscape Rock-layer surface correction

- A six-view Game View review exposed oversized pale stone/shard repetition
  across the central initial-launch routes. A bounded nine-point direct trace
  and paint-weight readback proved the visible receiver was Landscape and that
  the dominant painted layer was `Rock` (generally weight `1.0`), not `Sand`.
  This explains why a compiled unsaved Historic Desert Ruin Floor Sand Coarse
  replacement on the Sand branch produced no meaningful visual improvement.
  That first one-material preview was discarded; the material package was
  reloaded and authoritative dirty state returned to zero.
- The accepted reuse-first correction changes only the existing
  `/Game/Maps/Sunscar/Art/Materials/LandscapeV3/M_OT_Landscape_Abiverd`
  material. The `Rock_BaseColor` and `Rock_Normal` defaults now use the already
  imported owned Dry Trampled Soil texture set, retaining the existing
  `Rock_TileCm=260`. `Rock_Tint` is `(0.88,0.80,0.68,1)`.
- The existing shared macro branch now also samples Dry Trampled Soil at
  `12000 cm`, with strength `0.12` and floor `(0.90,0.90,0.90,1)`. This keeps
  low-frequency variation while removing the previous 36 m rocky macro's dark
  repetition. No Landscape proxy, height, weightmap, Grass layer, texture
  bombing function, source texture, or shared source material was changed.
- Matched launch-route captures show the central surface now reads as compacted
  semi-arid soil rather than oversized trench rock. The accepted field-edge
  capture confirms the localized Grass/poppy presentation remains intact.
  Review: `/private/tmp/abv_landscape_rock_drysoil_preview_review_v1/`.
  Read-only cause evidence:
  `/private/tmp/abv_center_route_surface_probe_v1.json`; exact-save evidence:
  `/private/tmp/abv_landscape_rock_drysoil_exact_save_v1.json`.
- Compile errors were zero; only the material package was dirty/saved, its mtime
  advanced, and authoritative Unreal dirty state returned to zero.

## 2026-08-16 launch-area Sand/base harmonization and central furniture finish

- The Landscape material correction was completed across the remaining base
  branch: `Sand_BaseColor` and `Sand_Normal` now reuse the same imported Dry
  Trampled Soil set, with `Sand_TileCm=260` and `Sand_Tint=(0.92,0.84,0.72,1)`.
  The existing Sand texture-bombing graph remains connected and unchanged.
  The material compiled with zero errors, was exact-saved, and returned to zero
  authoritative dirty packages. Evidence:
  `/private/tmp/abv_landscape_sand_drysoil_preview_review_v1/` and
  `/private/tmp/abv_landscape_sand_drysoil_exact_save_v1.json`.
- The remaining pale courtyard island was proven to be the visible legacy
  decal `OT_EXT_Ground_CourtyardConnector_02`, not Landscape or a ground
  overlay. Its oversized `MI_Decal_Debris_Dirt_01_A` projection washed out the
  corrected terrain. The actor was preserved, while only its decal component
  was made invisible and hidden in game. Exact package
  `/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/9/U3/17IINK4HIYF2F4Q4E1C68M`
  was saved; zero dirty packages remained. Evidence:
  `/private/tmp/abv_courtyard_connector_decal_disabled_v1.png` and
  `/private/tmp/abv_courtyard_connector_decal_disable_exact_save_v1.json`.
- Replaced the four SS_009 plaza cube benches with the already owned Quixel
  `Wooden_Bench_vlroadt_High`, using its existing material, uniform scale
  `1.4`, original layout axes, and a verified `2 cm` Landscape embed. The four
  production labels are `ABV_SS_009_PlazaBench_01_V1` through `_04_V1`.
  Collision matches visible geometry; navigation and overlaps are disabled.
  Exactly four external-actor packages were saved. Evidence:
  `/private/tmp/abv_plaza_benches_preflight_v1.json`,
  `/private/tmp/abv_plaza_benches_before_v1/`,
  `/private/tmp/abv_plaza_benches_after_v1/`, and
  `/private/tmp/abv_plaza_benches_exact_save_v1.json`.
- Replaced all six SS_008 courtyard cube benches with the same proven Quixel
  bench and material. Labels are `ABV_SS_008_CourtyardBench_01_V1` through
  `_06_V1`; four retain the east-west arrangement and two retain the
  north-south arrangement. Each is uniformly scaled `1.4`, directly
  terrain-conformed with a verified `2 cm` embed, collision-enabled, and
  non-navigable/non-overlapping. Exactly six external-actor packages were
  saved and authoritative dirty state returned to zero. Evidence:
  `/private/tmp/abv_courtyard_benches_preflight_v1.json`,
  `/private/tmp/abv_courtyard_benches_before_v1/`,
  `/private/tmp/abv_courtyard_benches_after_v1/`, and
  `/private/tmp/abv_courtyard_benches_exact_save_v1.json`.
- Finished the four SS_009 plaza lamp assemblies without adding shared assets.
  Each square prototype shaft now uses `/Engine/BasicShapes/Cylinder` with the
  existing `MI_OT_Metal`, exact support contact, query-and-physics collision,
  disabled nav/overlaps/tick/replication, and a production label
  `ABV_SS_009_PlazaLampPole_01_V1` through `_04_V1`. The fourth pole's former
  234 cm overrun above its lamp head was removed; all four pole tops now meet
  their heads at Z `35257.805`. Existing head geometry/transforms were
  preserved, changed from bright Accent to Metal, renamed
  `ABV_SS_009_PlazaLampHead_01_V1` through `_04_V1`, and made non-colliding and
  non-navigable because they are overhead decorative housings. Exactly four
  pole and four head packages were exact-saved. Evidence:
  `/private/tmp/abv_plaza_lamp_poles_preflight_v1.json`,
  `/private/tmp/abv_plaza_lamp_poles_apply_v1.json`,
  `/private/tmp/abv_plaza_lamp_poles_exact_save_v1.json`,
  `/private/tmp/abv_plaza_lamp_heads_apply_v1.json`,
  `/private/tmp/abv_plaza_lamp_heads_exact_save_v1.json`, and
  `/private/tmp/abv_plaza_lamp_poles_review_v1/`.
- Converted the four nearly buried bright SS_008 courtyard planter blocks into
  grounded `120 x 120 x 55 cm` ruin-brick plinth/planters using the existing
  chamfered geometry and `MI_ABV_RuinBrick_WorldAligned`. Each has a verified
  `2 cm` embed, visible collision, and disabled nav/overlaps. Labels are
  `ABV_SS_008_CourtyardPlanter_01_V1` through `_04_V1`. Exactly four packages
  were exact-saved. Evidence:
  `/private/tmp/abv_courtyard_planters_preflight_v1.json`,
  `/private/tmp/abv_courtyard_planters_apply_v1.json`, and
  `/private/tmp/abv_courtyard_planters_exact_save_v1.json`.
- Material-finished all seven `Building_CentralCourtyard` perimeter pieces in
  two exact-save batches. The bright smooth facade stucco was replaced only on
  those wall actors with the established world-aligned Abiverd ruin brick.
  Geometry, gate openings, transforms, `BlockAll` collision and navigation
  remained unchanged. Evidence:
  `/private/tmp/abv_central_courtyard_shell_inventory_v1.json`,
  `/private/tmp/abv_central_courtyard_walls_batch_a_apply_v1.json`,
  `/private/tmp/abv_central_courtyard_walls_batch_a_exact_save_v1.json`,
  `/private/tmp/abv_central_courtyard_walls_batch_b_apply_v1.json`,
  `/private/tmp/abv_central_courtyard_walls_batch_b_exact_save_v1.json`, and
  the final courtyard views under
  `/private/tmp/abv_courtyard_benches_after_v1/`.
- A tag-scoped audit found 96 tiny SS_008/SS_009 ground debris, grass and
  market-scatter actors still had query-and-physics collision, navigation and
  overlap generation. They measured only about `2–104 cm` and are visual
  micro-dressing, not tactical cover. Corrected them in nine independently
  gated exact-save batches of 10–12 packages: collision `NoCollision`, nav and
  overlaps disabled, non-replicated, and tick disabled. Meshes, materials,
  transforms, bounds and visibility were numerically preserved. Consolidated
  re-audit proves all `96/96` have the intended settings and Unreal dirty state
  is zero. Evidence:
  `/private/tmp/abv_ss008_ss009_microprops_inventory_v1.json` and
  `/private/tmp/abv_microprops_cleanup_*_v1.json`.
- Finalized the six remaining SS_008 courtyard-furniture actors. Two existing
  Quixel benches retain visible collision and now use production labels
  `ABV_SS_008_CourtyardBench_07_V1` and `_08_V1`. Four oil-pack, storage-box
  and jerrycan micro-props are visual dressing only and now use `NoCollision`,
  no navigation, no overlaps, no tick and no replication. Their meshes,
  materials and transforms were preserved. Exactly six actor packages were
  saved and authoritative dirty state returned to zero. Evidence:
  `/private/tmp/abv_ss008_furniture_finalize_v1.json`.
- Closed the last ten `UnreviewedAutomationPlacement` storage actors in
  SS_008. The two genuinely knee-high crates (about 26–30 cm tall) retain
  visible `BlockAll` collision; eight flat lids/small debris pieces (about
  5–18 cm tall) are non-colliding visual dressing. All ten are non-navigable,
  non-overlapping, non-replicated and non-ticking, and now carry explicit
  `ABV_SS_008_Storage*` production labels plus `ReviewedProductionPlacement`.
  Geometry, source meshes, materials, transforms and bounds were preserved.
  Exactly ten external-actor packages were saved; mtimes advanced and
  authoritative dirty state returned to zero. Evidence:
  `/private/tmp/abv_ss008_ss009_remaining_unreviewed_v1.json` and
  `/private/tmp/abv_ss008_storage_finish_v1.json`.
- Completed the same production-state normalization for every remaining
  visible `UnreviewedAutomationPlacement` actor in the loaded launch sites:
  `110/110` actors across SS_003, SS_004, SS_005, SS_006, SS_007, SS_010,
  SS_011, SS_013, SS_015, SS_016, SS_017 and SS_018. Work was split into
  twelve independently gated batches of at most twelve packages. Tables,
  stools, benches, large electrical boxes/cabinets and substantial rocks
  retain visible `BlockAll` collision. Wall-mounted small utility boxes,
  loose containers, lids, tiny storage/scrap, ground patches and vegetation
  use `NoCollision`. All reviewed actors are non-navigable, non-overlapping,
  non-replicated and non-ticking, with production `ABV_<site>_*_V1` labels.
  Source meshes, materials, transforms and bounds were preserved numerically.
  Every package mtime advanced only in its authorized exact-save batch, and
  authoritative dirty state returned to zero after each batch. The closing
  exact-tag audit proves `count=0`, no remaining visible unreviewed launch-area
  actors, and zero dirty packages. Evidence:
  `/private/tmp/abv_launch_remaining_unreviewed_v1.json` and
  `/private/tmp/abv_unreviewed_*_v1.json`.

## 2026-08-17 launch-building exterior acceptance continuation

- Material-finished the seven remaining generic stucco shell pieces on
  `SS_004` Tea House with the already established
  `MI_ABV_CrackedMud_WorldAligned`. The north wall already used that finish;
  east left/lintel/right, south wall, and west left/lintel/right now match it.
  Geometry, transforms, collision, doors, windows, canopy and visible
  parapets were preserved. Exactly seven external-actor packages were saved,
  all mtimes advanced, and authoritative Unreal dirty state returned to zero.
  Evidence: `/private/tmp/abv_ss004_shell_preview_v2/` and
  `/private/tmp/abv_ss004_shell_crackedmud_exact_save_v2.json`.
- Recovery lesson: do not call `reload_packages` on a loaded World Partition
  external-actor package to discard a transient preview. In UE 5.8 this pinned
  the isolated editor at full CPU and made the bridge unresponsive. The exact
  editor PID was terminated only after command-line revalidation; the project
  reopened without restoring autosaves, and the affected package was proven
  clean from disk. Prefer an exact save after a validated gate, or a controlled
  editor close/reopen with Don't Save for transient preview rollback. Never use
  World Partition descriptor/intersection scripts as a substitute.
- Fresh current-state review accepted the `SS_018` Telecom Workshop exterior.
  The saved weathered/flaked north ground storey, heritage piers, blue telecom
  frontage, roof service equipment, ramp/landing and grounded facade contact
  are intact. No new change was required. Evidence:
  `/private/tmp/abv_ss018_current_review_v2/`.
- Finished the `SS_007` Municipal Hotel upper shell. Exact live audit proved
  all ten second/third-storey wall pieces still used the bright prototype
  `MI_OT_Stucco_WorldAligned`, while the ground storey was already finished in
  ruin brick. Changed only those ten material overrides to the established
  `MI_OT_FlakedPaint_WorldAligned`; transforms, floors, openings, collision,
  navigation, balconies, doors/windows and source geometry were preserved.
  Exactly ten external-actor packages were saved, every mtime advanced, and
  authoritative dirty state returned to zero. The hotel now reads as a
  coherent weathered masonry building from north/east/west approaches instead
  of exposing white blockout storeys. Evidence:
  `/private/tmp/abv_ss007_upper_shell_material_audit_v1.json`,
  `/private/tmp/abv_ss007_upper_shell_flaked_exact_save_v1.json`, and
  `/private/tmp/abv_ss007_current_close_review_v2/`.
- UE Python durability note: `Vector.equals` in this UE 5.8 Python binding does
  not accept a tolerance argument. Compare numeric transform components
  explicitly. Also call both `actor.modify()` and `component.modify()` before
  `set_material`; otherwise an in-memory material override can change without
  producing the expected external-actor dirty package. The first attempt was
  unsaved and was safely completed by the corrected exact-package script.
- Fresh close player-height, oblique and elevated review accepted the `SS_017`
  bazaar/market exterior after the production-state actor normalization. The
  north market bays retain grounded masonry counters, weathered plaster,
  opening shade pieces and a clear primary doorway; the south frontage retains
  the darker ruin-brick market identity and finished counter/stall composition.
  No runtime floating or embedded exterior defect was proven, so no actor was
  changed. The green wireframes visible in some editor captures are editor
  volume visualization, not runtime geometry. Evidence:
  `/private/tmp/abv_ss017_north_bazaar_storefront_review_v2/` and
  `/private/tmp/abv_ss017_stalls_finish_review_v2/`.
- With `SS_004`, `SS_007`, `SS_017` and `SS_018` rechecked in this continuation,
  the existing 13-site launch-building exterior first-art/design-draft gate
  remains valid. Further systematic building mutation is closed unless a new
  exact player-height defect is proven. Work continues directly into the
  launch-area road, ground-transition and placed-ground-asset finish rather
  than reopening completed shells.
- Added one bounded runtime storytelling decal to the `SS_015` motor-pool
  floor: `ABV_SS_015_MotorPool_OilStain_A_V2`, using the already saved
  `M_ABV_OilStain_Decal` deferred-decal material. The receiver floor was
  explicitly verified to receive decals, five direct support samples proved a
  flat `Z=34814.10 cm` surface, and player-height/top review proved the stain
  reads as a restrained irregular vehicle-service mark without collision or
  traversal impact. Exactly one new LFS-managed external-actor package was
  saved; authoritative dirty state returned to zero. Evidence:
  `/private/tmp/abv_ss015_oilstain_retry_gate_v2.json`,
  `/private/tmp/abv_ss015_oilstain_review_v3/`, and
  `/private/tmp/abv_ss015_oilstain_retry_exact_save_v2.json`.
- Decal rotation durability note: the earlier apparently invisible SS_015
  preview did **not** prove a receiver/material incompatibility. It used a
  positional `unreal.Rotator(...)` call whose argument ordering did not match
  the intended pitch/yaw/roll. For downward UE decals in this workflow, use
  named fields and verify the readback, e.g.
  `unreal.Rotator(pitch=-90.0, yaw=12.0, roll=0.0)`. The corrected named-field
  rotation made the same saved decal material render correctly.
- Broke the repeated launch-area roof treatment without changing gameplay
  geometry. An exact twelve-roof audit proved every principal roof used the
  same weathered-concrete surface. Modern/service buildings keep that finish;
  only the heritage-led `Core_SS_004_Roof`, `Core_SS_013_Roof`, and
  `Core_SS_017_Roof` now use the existing packed-earth
  `MI_OT_SandstoneSilt_WorldAligned`. Oblique and aerial review shows these
  three roofs now read as earthen Abiverd construction while the remaining
  concrete roofs retain their intended identity. Transforms, bounds,
  collision, navigation and source meshes were preserved. Exactly three
  external-actor packages were saved, all mtimes advanced, and authoritative
  dirty state returned to zero. Evidence:
  `/private/tmp/abv_launch_roof_finish_audit_v1.json`,
  `/private/tmp/abv_launch_wall_material_profile_v1.json`,
  `/private/tmp/abv_heritage_roofs_preview_v1/`, and
  `/private/tmp/abv_heritage_roofs_silt_exact_save_v1.json`.
- Added a restrained Tea House ground-transition treatment using one new
  map-owned deferred-decal wrapper and one non-colliding map actor. The wrapper
  reuses the imported Quixel mud-stain base color but uses the already verified
  irregular Quixel stain opacity silhouette at a `0.35` strength; the original
  Quixel mud opacity texture was visually rejected because it produced a hard
  rectangular boundary even after global opacity reduction. The accepted actor
  is `ABV_SS_004_TeaHouse_MudStain_A_V1`, terrain-supported on four fixed
  Landscape samples with zero measured variation and clear of doors/gates.
  The separate SS_017 candidate was rejected without mutation because one
  corner traced onto `ABV_SS_017_BazaarMasonryStall_S01_V1`. Exact-save scope
  was the new `M_ABV_MudStain_Decal` material plus the one Tea House external
  actor; both are LFS-managed and authoritative dirty state returned to zero.
  Evidence: `/private/tmp/abv_mudstain_transition_gate_v1.json`,
  `/private/tmp/abv_ss004_mudstain_preview_v3/`, and
  `/private/tmp/abv_ss004_mudstain_exact_save_v1.json`.
- Completed the launch-window navigation-cost cleanup without changing the
  buildings' appearance or gameplay collision. The exact audit covered 140
  visible window-frame/recess actors. Ninety-five collisionless decorative
  frame/glass actors incorrectly retained `CanEverAffectNavigation=true`; all
  95 now have it disabled while preserving transforms, source meshes,
  materials, visibility, collision, overlaps, component/actor tick and
  replication. The 15 remaining navigation-relevant actors are the colliding
  `SS_007` hotel window frames and were intentionally left unchanged. Work was
  exact-saved in batches of at most 12 packages; every authorized mtime
  advanced and authoritative dirty state returned to zero after every batch.
  Final audit: 140 reviewed, zero collisionless actors still navigation
  relevant, 15 intentionally colliding frames retained. Evidence:
  `/private/tmp/abv_launch_window_performance_audit_v1.json`,
  `/private/tmp/abv_window_nav_cleanup_recover_first_two_exact_save_v1.json`,
  and `/private/tmp/abv_window_nav_cleanup_batch02_exact_save_v1.json` through
  `/private/tmp/abv_window_nav_cleanup_batch09_exact_save_v1.json`.
- UE 5.8 Python durability note: changing
  `StaticMeshComponent.can_ever_affect_navigation` through
  `set_editor_property` updates the loaded component but may not mark its World
  Partition external-actor package dirty. After full property/ownership gates,
  use `EditorLoadingAndSavingUtils.save_packages(exact_packages, False)` to
  force-save only the explicitly authorized packages, then prove every mtime
  advanced and authoritative dirty state is zero. Also serialize transforms as
  numeric translation/quaternion/scale values for preservation checks; the
  string representation embeds a temporary struct address and cannot be
  compared reliably.
- Completed a second structural-material closeout across 353 visible launch-
  area structural actors. The exact audit found 15 exterior shell pieces still
  using the plain `MI_OT_Stucco_WorldAligned` finish: the four second-storey
  walls of `SS_005` Clinic and eleven first/second-storey exterior wall pieces
  of `SS_018` Telecom Workshop. Those 15 pieces now use the already accepted
  `MI_OT_FlakedPaint_WorldAligned`, producing a visibly weathered finish that
  matches the established lower-storey treatment. Meshes, transforms,
  openings, collision and navigation were preserved. The four clinic packages
  and eleven telecom packages were exact-saved; every mtime advanced and dirty
  state returned to zero. Player-height, oblique and elevated evidence:
  `/private/tmp/abv_ss005_upper_finish_preview_v1/` and
  `/private/tmp/abv_ss018_shell_finish_preview_v1/`. Exact-save evidence:
  `/private/tmp/abv_ss005_upper_finish_exact_save_v1.json` and
  `/private/tmp/abv_ss018_shell_finish_exact_save_v1.json`.
- The post-save structural audit leaves exactly 14 stucco candidates, all named
  `Core_<site>_Interior_A/B`. They are intentional interior/occlusion pieces,
  not exposed exterior shell; there are zero remaining exterior stucco
  candidates. Evidence:
  `/private/tmp/abv_launch_structural_material_closeout_audit_v1.json`.
- Deterministic review-capture note: teleporting the editor viewport can feed
  the temporal motion-blur history and produce unusably smeared captures. For
  review only, set the editor-session cvars `r.MotionBlurQuality 0` and
  `r.MotionBlur.Amount 0`, then capture a warm-up frame before the retained
  frame. This changes no project config or asset.
- Closed the launch-area default/prototype-material category. An exact-tag
  read-only audit reviewed 904 visible runtime static-mesh actors across the 13
  launch sites and found zero actors using WorldGrid, DefaultMaterial,
  BasicShapeMaterial, LevelPrototyping materials, prototype materials or null
  material slots (intentional interior A/B pieces and editor/collision helpers
  excluded). No mutation was required. Evidence:
  `/private/tmp/abv_launch_visible_default_material_audit_v1.json`.
- Completed the remaining visible static-actor performance policy. The
  read-only gate covered the same 904 visible launch-area static actors and
  found zero replicated, ticking or overlap-generating actors, but 108
  collisionless exterior details still had navigation relevance enabled. The
  affected set was limited to decorative signs, shutters, drains/outlets, mast
  bases, small roof utilities and industrial dressing. Collisionless state and
  exact ownership were revalidated per actor; only
  `CanEverAffectNavigation=false` changed. Work was force-saved in nine exact
  12-package batches because this UE 5.8 component flag does not reliably mark
  external-actor packages dirty. Every authorized mtime advanced and dirty
  state remained zero. The post-save audit proves `no_collision_nav_count=0`
  and `runtime_overhead_count=0`. Evidence:
  `/private/tmp/abv_launch_static_actor_performance_policy_audit_v1.json` and
  `/private/tmp/abv_launch_static_nav_cleanup_batch01_exact_save_v1.json`
  through `/private/tmp/abv_launch_static_nav_cleanup_batch09_exact_save_v1.json`.
- Coverage correction: the original launch list includes `SS_006`; a draft of
  the second-pass query accidentally included `SS_020` in its place. Before
  closeout, `SS_006` was added back to every gate and all three audits were
  rerun. Its nine structural actors and 40 visible static actors produced zero
  exposed-stucco, default/prototype-material, collisionless-nav, tick,
  replication or overlap findings. The retained audit reports above contain
  the corrected 353-structural/904-visible totals.
- Reconfirmed launch-region HLOD participation without invoking World
  Partition descriptor, intersection, region-loading or builder APIs. All 885
  loaded visible launch-site actors are spatially loaded, use the default
  runtime grid, have automatic HLOD generation enabled and have no explicit
  per-actor HLOD override. This agrees with the existing valid instanced and
  merged HLOD-layer configuration. No generated HLOD build was started because
  an unfiltered builder would create a mass whole-world package delta against
  the accumulated unstaged map scope. Evidence:
  `/private/tmp/abv_launch_hlod_loaded_actor_audit_v1.json`.
- A visible duplicate-placement closeout reviewed the same 885 launch-site
  StaticMeshActors and found zero duplicate groups at 0.1 cm translation,
  0.01-degree rotation and 0.0001 scale precision. No actor was deleted or
  moved. Evidence:
  `/private/tmp/abv_launch_visible_duplicate_geometry_audit_v1.json`.
- Removed unnecessary full shadow casting from exactly 13 tiny (13.4-27.0 cm)
  collisionless industrial scrap/spring fragments at `SS_013` and `SS_017`.
  Meshes, transforms, materials, visibility, collision, navigation, overlap,
  tick and replication state were preserved. The component render flag did not
  mark World Partition actor packages dirty, so the two bounded batches used
  the established force-save rule on exactly eight then five owned packages;
  every mtime advanced and authoritative dirty state returned to zero. The
  post-save shadow audit reports zero remaining actors in the selected
  micro-scrap class. Evidence:
  `/private/tmp/abv_launch_small_decor_shadow_audit_v1.json`,
  `/private/tmp/abv_launch_micro_scrap_shadow_cleanup_batch01_exact_save_v1.json`
  and
  `/private/tmp/abv_launch_micro_scrap_shadow_cleanup_batch02_exact_save_v1.json`.
- Added two restrained localized ground-transition accents using the existing
  map-owned `M_ABV_MudStain_Decal`: `ABV_SS_005_Clinic_MudStain_A_V1` in the
  clinic forecourt and `ABV_SS_007_Hotel_MudStain_A_V1` on the hotel approach.
  Five fixed Landscape samples per site proved flat/near-flat support (0.0 cm
  and 0.19 cm variation) with 5.60 m and 3.84 m clearance from the nearest
  entrance actors. Both decals are non-replicated, non-ticking, non-colliding,
  use the established irregular 0.35-opacity treatment and remain outside the
  door thresholds. Each actor/component serializes in one new external-actor
  package; the two packages were exact-saved separately and both saves returned
  to authoritative zero dirty state. Evidence:
  `/private/tmp/abv_launch_entrance_mudstain_gate_v1.json`,
  `/private/tmp/abv_entrance_mudstain_review_v1/`,
  `/private/tmp/abv_ss005_clinic_mudstain_exact_save_v1.json` and
  `/private/tmp/abv_ss007_hotel_mudstain_exact_save_v1.json`.
- The complete launch-exterior acceptance gate was rerun after these changes
  and passed all checks: clean editor context, Landscape material, 288 hidden
  legacy overlays, field-edge and north-meadow HISM policy, foliage instancing
  usage, wall-foot/road shoulders, SS_013 ruin cluster, twelve launch sandbag
  barriers, fifty core-route materials and sixteen decorative Quixel ground
  actors. It covered 3,375 loaded actors and returned to zero dirty packages.
  Evidence: `/private/tmp/abv_launch_exterior_final_acceptance_v2.json`.
- UE's registered validators returned `Valid` with zero errors or warnings for
  the two new entrance decals, the existing Tea House and motor-pool decals,
  the field-edge HISM actor, all three SS_013 ruin actors, both map-owned decal/
  foliage materials and both HLOD-layer assets. Evidence:
  `/private/tmp/abv_launch_exact_object_validation_v1.json`.
- Current repository scope remains intentionally unstaged and map-only: 912
  modified plus 80 untracked files (992 total), staged count zero. A full path
  classifier found no paths outside the map's external actor/object packages,
  the already approved map-owned/Quixel materials and this handoff document.
  Local and remote `feature/map-development` remain
  `e0b856c20cdad11f7057248c851d4d344f43fbe1`; no stage, commit, push, merge or
  rebase was performed.
- The existing deterministic gameplay-route audit was rerun from its committed
  repository script after map closeout. All 50 audited Old Town routes passed;
  the narrowest retained route is 300 cm and no route requires review. Evidence:
  `Saved/OperationSunscar/Reports/old_town_gameplay_route_audit_v1.json`.
- A separate exact spawn/support audit resolved all eight loaded PlayerStarts.
  Every start is Landscape-supported, pairwise start spacing is at least 800 cm
  and support deltas are 2.46-7.40 cm. The four attacker-start overlap results
  resolve only to the intentional `CoreVolume_AttackerExtraction` TriggerBox,
  not physical blocking geometry. No NavMeshBoundsVolume/RecastNavMesh is
  loaded; navigation generation remains a separately scoped AI/navigation
  task rather than part of this player-route exterior pass. Evidence:
  `/private/tmp/abv_launch_spawn_nav_audit_v1.json`.
- UE's current-world validator also returned `Valid` with zero errors and zero
  warnings in 0.04 seconds, with zero authoritative dirty packages. Evidence:
  `/private/tmp/abv_current_world_validation_v1.json`.
- The final deterministic eight-view review is retained at
  `/private/tmp/abv_launch_exterior_final_review_v7/`. Three elevated views and
  five player-height approach/site views confirm the thirteen initial-launch
  building exteriors, perimeter walls, entrances, ground contacts and seasonal
  SS_013 field edge remain readable and coherent at the intended scale. Distant
  partially loaded/prototype silhouettes visible beyond the bounded playable
  launch area are not part of these thirteen accepted building sites and were
  not mutated during closeout; they remain a later world-vista/streaming scope,
  not an exterior-building regression.
- Git attributes were checked for the new material/map packages and resolve to
  LFS filter/diff/merge handling. `git lfs status` contains no staged work and
  no commit/push operation was performed. The next production-scale map step
  is a controlled HLOD build/checkpoint; do not run an unfiltered whole-world
  HLOD builder against this accumulated unstaged World Partition scope.
- Final hygiene check: the generated tracked Python bytecode cache
  `Content/Python/OperationSunscar/AutomationV1/__pycache__/sunscar_automation_common.cpython-311.pyc`
  was restored to its exact `HEAD` content after validation. The final Git
  classifier again reports 912 modified, 80 untracked, zero staged and zero
  unexpected paths; branch/local/remote hashes remain the required commit.
