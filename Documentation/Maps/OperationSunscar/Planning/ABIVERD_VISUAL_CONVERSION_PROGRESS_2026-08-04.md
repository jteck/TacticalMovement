# Abiverd Old Town visual-conversion progress — 2026-08-04

## Verified scope

- Project: `/Users/jasonteck/UnrealEngine/_worktrees/map-development/TacticalMovement.uproject`
- Branch/worktree purpose: isolated map development
- Level: `/Game/Maps/Blockout/Lvl_Blockout_01`
- Protected movement, animation, weapon, readiness and project-config assets were not modified.
- The project default map was not changed.

## Completed visual passes

### Landscape V2

- Replaced the overlapping visual ground-tile presentation with the real
  2017×2017 Landscape material/layer workflow.
- Imported deterministic masks for arid sand, compacted earth, weathered
  asphalt, stone hardstand, roadside silt and Abiverd spring meadow.
- Preserved but hid 422 planning/debug/ground-overlay actors.
- Report:
  `Saved/OperationSunscar/Reports/abiverd_landscape_visual_conversion_v2.json`
- Automation:
  `Content/Python/OperationSunscar/AutomationV1/abiverd_landscape_visual_conversion_v2.py`

### Heritage material repair V2

- Created lightweight map-owned PBR masters for heritage scans and masked
  foliage.
- Configured the carved arch, modular ruin wall and Structure Stone S 06.
- Enabled Nanite on the dense opaque heritage scans; intentionally kept it off
  the lightweight grass-card meshes.
- Repaired 16 poppy/grass material variants and capped runtime texture sizes.
- Report:
  `Saved/OperationSunscar/Reports/abiverd_heritage_material_repair_v2.json`
- Automation:
  `Content/Python/OperationSunscar/AutomationV1/abiverd_heritage_material_repair_v2.py`

### Abiverd meadow density V2

- Reused one HISM vegetation actor with 16 components.
- Placed 4,200 poppies and 2,400 grasses in deterministic terrain-conformed
  belts while preserving the main assault route and landmark courts.
- Disabled collision, navigation influence, replication and small-instance
  shadows; configured distance culling.
- Report:
  `Saved/OperationSunscar/Reports/abiverd_vegetation_density_v2.json`
- Automation:
  `Content/Python/OperationSunscar/AutomationV1/abiverd_vegetation_density_v2.py`

### Landmark completion V2

- Added the SS_023 masonry well court, four archaeological low walls, two stone
  fragments, four mosque buttresses and two eroded wall scans.
- All new pieces were terrain-conformed; scan dressing remains non-colliding.
- Report:
  `Saved/OperationSunscar/Reports/abiverd_landmark_completion_v2.json`
- Automation:
  `Content/Python/OperationSunscar/AutomationV1/abiverd_landmark_completion_v2.py`

### Old Town structural skin V3

- Preserved all tested gameplay shells and their existing openings.
- Converted 111 building surfaces across 190 building actors to a coherent
  mud-brick, plaster, secured-civic and industrial material hierarchy.
- Added 76 exterior structural-detail actors: grounded foundation skirts, roof
  parapets, restrained buttresses and limited non-colliding erosion accents.
- Foundation skirts and decorative buttresses do not affect collision.
- Roof parapets use normal static collision and require later route/roof
  playtesting.
- Report:
  `Saved/OperationSunscar/Reports/abiverd_structural_skin_v3.json`
- Automation:
  `Content/Python/OperationSunscar/AutomationV1/abiverd_structural_skin_v3.py`

### Quixel façade scan instancing V4

- Reused the verified 3.23 m × 3.26 m × 0.70 m Historic Desert Ruin Wall
  Modular Set 04 as non-colliding façade dressing.
- Added 75 instances over 25 uninterrupted P0 wall spans through one static,
  non-replicated HISM actor.
- Door/window-adjacent wall fragments and lintels were excluded.
- The first review detected that the imported mesh uses local Y—not local Z—as
  its height axis. The same HISM actor was corrected in place with +90° roll;
  no duplicate actor or geometry remains.
- Report:
  `Saved/OperationSunscar/Reports/abiverd_facade_scan_instancing_v4.json`
- Automation:
  `Content/Python/OperationSunscar/AutomationV1/abiverd_facade_scan_instancing_v4.py`

### Pakistan civic façade V1

- Purchased and downloaded Historic Pakistan Street Wall Brick Modular 16 as
  High glTF with 4K source textures.
- Verified in the disposable UE 5.8 staging project before map import:
  200.603 × 30.578 × 350.016 cm, one mesh, one material slot and Nanite enabled.
- Imported it into the dedicated map-owned architecture tree, replaced the
  source runtime material with a lightweight packed-ORM master, retained the
  4K sources while capping runtime texture resolution at 2K, and kept Nanite on.
- Added nine non-colliding HISM instances: three each on blank civic wall spans
  at SS_005 Clinic, SS_010 Detention Annex and SS_012 Consulate.
- Existing openings, shell collision, navigation and replication were not
  changed.
- Reports:
  `Saved/OperationSunscar/Reports/abiverd_pakistan_wall_import_v1.json` and
  `Saved/OperationSunscar/Reports/abiverd_pakistan_wall_facade_apply_v1.json`
- Automation:
  `Content/Python/OperationSunscar/AutomationV1/abiverd_pakistan_wall_import_v1.py`
  and
  `Content/Python/OperationSunscar/AutomationV1/abiverd_pakistan_wall_facade_v1.py`

### Pakistan opening façade V1

- Confirmed the exact purchased Historic Pakistan Street Window Brick Modular
  04 source from Fab listing `e5026e65` and imported its High glTF source.
- Verified imported bounds of 261.819 × 47.663 × 347.620 cm, one material
  slot and 1,812 LOD0 vertices.
- Replaced the source runtime material with the existing lightweight packed-ORM
  heritage master, retained 4K source textures while capping runtime texture
  resolution at 2K, and enabled Nanite.
- Historical first attempt: added 14 non-colliding full-storey scan instances
  through one static, non-replicated HISM actor. Later visual review established
  that these complete 3.48 m masonry wall modules read as oversized brick slabs
  attached to plaster shells, not as opening-scale window treatment.
- The 14 unsuitable instances were subsequently removed. The 28 original
  frame/glass visuals were restored as temporary opening cues with NoCollision.
  The building shells remain the gameplay and collision authority.
- Configured 12 m minimum and 30 m maximum HISM cull distances. A targeted
  follow-up save captured Unreal's asynchronously generated instancing material
  usage without broad-saving unrelated content.
- Reports:
  `Saved/OperationSunscar/Reports/abiverd_pakistan_window_import_v1.json`,
  `Saved/OperationSunscar/Reports/abiverd_pakistan_window_facade_dry_run_v1.json`,
  `Saved/OperationSunscar/Reports/abiverd_pakistan_window_facade_apply_v1.json`,
  `Saved/OperationSunscar/Reports/abiverd_pakistan_window_post_apply_audit_v1.json`
  and the corrective reports
  `Saved/OperationSunscar/Reports/abiverd_remove_unsuitable_window_slabs_apply_v1.json`
  and
  `Saved/OperationSunscar/Reports/abiverd_remove_unsuitable_window_slabs_post_audit_v1.json`
  and
  `Saved/OperationSunscar/Reports/abiverd_save_pakistan_window_material_v1.json`
- Automation:
  `Content/Python/OperationSunscar/AutomationV1/abiverd_pakistan_window_import_v1.py`,
  `Content/Python/OperationSunscar/AutomationV1/abiverd_pakistan_window_facade_v1.py`,
  `Content/Python/OperationSunscar/AutomationV1/abiverd_pakistan_window_post_apply_audit_v1.py`
  and
  `Content/Python/OperationSunscar/AutomationV1/abiverd_save_pakistan_window_material_v1.py`

### Corrective façade and roof review — 2026-08-05

- Identified the reviewed building as `SS_012` Consulate through a read-only
  camera/facade audit.
- Removed all 14 Historic Pakistan Street Window Brick Modular 04 full-storey
  HISM instances from the civic facades and restored all 28 original
  frame/glass opening cues. An independent post-audit verified zero remaining
  instances and an empty dirty-package list.
- Found two simultaneous parapet systems on seven sites. The older
  `SS_###_Parapet_*` actors were offset by half a roof span and produced the
  apparent floating beams. Exactly 28 superseded prototype parapets were hidden
  and set to NoCollision only where a complete, visible, colliding
  `ABV_SS_###_RoofParapet_*` replacement existed.
- An independent parapet audit passed for four sides each at `SS_004`, `SS_005`,
  `SS_007`, `SS_010`, `SS_011`, `SS_012` and `SS_018`.
- Created one shared world-aligned Consulate plaster instance using the owned
  Quixel wall-paint Base Color and Normal at a 200 cm projection scale,
  roughness 0.9 and specular 0.15. Applied it to exactly ten `SS_012` exterior
  wall-shell pieces while preserving Query-and-Physics collision.
- The plaster post-audit verified all ten assignments and parameters and
  confirmed that floors, roofs, interiors and lintels did not use the new
  material.
- The proposed Hotel V2 full-storey Pakistan-window script is now explicitly
  deprecated and blocked from execution. The scan may only be reused later as
  a compatible complete wall bay, never as an insert placed over an unrelated
  shell.
- Reports:
  `Saved/OperationSunscar/Reports/abiverd_current_facade_view_audit_v1.json`,
  `Saved/OperationSunscar/Reports/abiverd_remove_duplicate_parapets_apply_v1.json`,
  `Saved/OperationSunscar/Reports/abiverd_remove_duplicate_parapets_post_audit_v1.json`,
  `Saved/OperationSunscar/Reports/abiverd_consulate_warm_plaster_apply_v1.json`
  and
  `Saved/OperationSunscar/Reports/abiverd_consulate_warm_plaster_post_audit_v1.json`.
- Automation:
  `Content/Python/OperationSunscar/AutomationV1/abiverd_remove_unsuitable_window_slabs_v1.py`,
  `Content/Python/OperationSunscar/AutomationV1/abiverd_remove_unsuitable_window_slabs_post_audit_v1.py`,
  `Content/Python/OperationSunscar/AutomationV1/abiverd_remove_duplicate_parapets_v1.py`,
  `Content/Python/OperationSunscar/AutomationV1/abiverd_remove_duplicate_parapets_post_audit_v1.py`,
  `Content/Python/OperationSunscar/AutomationV1/abiverd_consulate_warm_plaster_v1.py`
  and
  `Content/Python/OperationSunscar/AutomationV1/abiverd_consulate_warm_plaster_post_audit_v1.py`.

### Abiverd opening surrounds V2

- Added a restrained map-owned opening language without replacing any tested
  gameplay shell or traversable opening.
- The first pass dressed eight verified doors at Tea House, Clinic, Detention
  Annex and Consulate with 24 cube instances split across two material-batched
  HISM components.
- A read-only Hotel/Bazaar audit then verified one real Hotel south door, two
  Hotel open shell passages and three Bazaar open shell passages. It also found
  two Hotel door props placed against solid wall shells.
- The V2 pass now covers nine real doors plus five open shell passages with 42
  non-colliding instances: 24 ruin-brick and 18 cracked-mud pieces.
- The two false Hotel door props (`Hotel_Door_-14` and `Hotel_Door_-8`) are
  hidden in editor/game and have collision disabled. The real Hotel door and
  the other eight real door props remain visible with their original
  Query-and-Physics collision.
- The surround actor is static and non-replicated, uses exactly two HISM
  components, does not affect navigation, and culls at 12 m/30 m.
- Reports:
  `Saved/OperationSunscar/Reports/abiverd_hotel_bazaar_opening_audit_v1.json`,
  `Saved/OperationSunscar/Reports/abiverd_opening_surrounds_v2_dry_run.json`,
  `Saved/OperationSunscar/Reports/abiverd_opening_surrounds_v2_apply.json` and
  `Saved/OperationSunscar/Reports/abiverd_opening_surrounds_post_apply_audit_v2.json`
- Automation:
  `Content/Python/OperationSunscar/AutomationV1/abiverd_hotel_bazaar_opening_audit_v1.py`,
  `Content/Python/OperationSunscar/AutomationV1/abiverd_opening_surrounds_v2.py`
  and
  `Content/Python/OperationSunscar/AutomationV1/abiverd_opening_surrounds_post_audit_v2.py`

### Landscape physical-material maintenance

- Unreal reported four Landscape streaming proxies with physical-material data
  needing a rebuild after the material/layer conversion.
- Rebuilt exactly those four proxies and exact-saved only their four World
  Partition external-actor packages.
- The subsequent Map Check completed with 0 errors and 0 warnings.

### Opening-scale window recess and trim conversion — 2026-08-05

- Audited all 80 existing window-detail actors as 40 frame/recess pairs before
  changing them. The audit verified that all cues were visible, 40 actors used
  the earlier glass instance, and the decorative actors were split between
  NoCollision and Query-and-Physics.
- Replaced the 40 glass assignments with one shared opaque dusty-recess
  material instance. The material uses a near-black warm base color, roughness
  0.92 and metallic 0.0. It deliberately avoids translucent glazing cost and
  sorting while creating readable interior depth from normal combat distance.
- Set all 80 decorative frame/recess actors to NoCollision. The tested building
  wall shells remain the sole collision authority.
- Added exactly two shallow opening-scale masonry pieces per window: a 205 x 26
  x 24 cm lintel and a 185 x 30 x 16 cm sill. Existing frames, recesses and
  gameplay shells were preserved.
- The 80 trim instances are batched into one non-replicated actor with two HISM
  components: 70 ruin-brick instances and 10 cracked-mud instances. Both
  components use NoCollision, do not affect navigation and cull at 12 m/30 m.
- The first trim apply attempt stopped before component creation or saving when
  UE 5.8 rejected editing `bReplicates` on an actor instance. The empty unsaved
  actor was removed; the two remaining nonexistent World Partition subobject
  packages were explicitly discarded during a clean editor restart. The
  corrected script relies on the Actor default and the independent audit
  verifies `replicates=false`.
- The corrected apply saved exactly one external-actor package and two
  external-object packages. The independent post-audit passed with 80 pieces,
  two components and an empty dirty-package list.
- Reports:
  `Saved/OperationSunscar/Reports/abiverd_window_material_state_audit_v1.json`,
  `Saved/OperationSunscar/Reports/abiverd_window_recess_conversion_dry_run_v1.json`,
  `Saved/OperationSunscar/Reports/abiverd_window_recess_conversion_apply_v1.json`,
  `Saved/OperationSunscar/Reports/abiverd_window_recess_post_audit_v1.json`,
  `Saved/OperationSunscar/Reports/abiverd_window_trim_instancing_dry_run_v1.json`,
  `Saved/OperationSunscar/Reports/abiverd_window_trim_instancing_apply_v1.json`
  and
  `Saved/OperationSunscar/Reports/abiverd_window_trim_post_audit_v1.json`.
- Automation:
  `Content/Python/OperationSunscar/AutomationV1/abiverd_window_material_state_audit_v1.py`,
  `Content/Python/OperationSunscar/AutomationV1/abiverd_window_recess_conversion_v1.py`,
  `Content/Python/OperationSunscar/AutomationV1/abiverd_window_recess_post_audit_v1.py`,
  `Content/Python/OperationSunscar/AutomationV1/abiverd_window_trim_instancing_v1.py`
  and
  `Content/Python/OperationSunscar/AutomationV1/abiverd_window_trim_post_audit_v1.py`.

### Old Town wall-foot transitions — 2026-08-05

- Ran a read-only preflight over 1,699 loaded actor descriptors before changing
  the map. It identified 200 building-shell actors, 25 door-clearance actors
  and 154 existing dressing actors.
- Targeted the first eight reviewed Old Town sites: `SS_004`, `SS_005`,
  `SS_007`, `SS_010`, `SS_011`, `SS_012`, `SS_017` and `SS_018`.
- Evaluated 49 ground-floor exterior wall segments and protected door routes
  with a 165 cm clearance radius. Eleven candidate placements were rejected
  because they entered a door-clearance area.
- Added 167 deterministic, terrain-conformed instances through one static,
  non-replicated actor with six HISM components: 84 rubble/rock patches and 83
  dry-grass clumps.
- All six components use `NoCollision`, do not affect navigation and preserve
  the tested building shells as the sole traversal/collision authority. Grass
  instances do not cast shadows and cull at 8 m/26 m; rubble instances cast
  shadows and cull at 16 m/48 m.
- The first apply detected that two shared source materials dirtied themselves
  during rendering. The pass was consolidated in place to map-owned, previously
  configured sources: `FAB_P1A_012_ydyqbjds` for both rubble components and
  `FAB_P1A_015_tbbqejqr` for all four grass components. The two unrelated shared
  material packages were explicitly discarded and were never saved.
- A clean editor reload and independent World Partition-aware post-audit
  verified exactly one `ABV_OldTown_WallFoot_HISM_V1` actor, six components,
  167 instances, the intended mesh references, culling/shadow policy,
  `replicates=false` and an empty dirty-package list.
- The final Map Check completed with 0 errors and 0 warnings.
- Reports:
  `Saved/OperationSunscar/Reports/abiverd_wall_foot_transition_preflight_v1.json`,
  `Saved/OperationSunscar/Reports/abiverd_wall_foot_transition_hism_dry_run_v1.json`,
  `Saved/OperationSunscar/Reports/abiverd_wall_foot_transition_hism_apply_v1.json`,
  `Saved/OperationSunscar/Reports/abiverd_wall_foot_source_consolidation_dry_run_v1.json`,
  `Saved/OperationSunscar/Reports/abiverd_wall_foot_source_consolidation_apply_v1.json`
  and
  `Saved/OperationSunscar/Reports/abiverd_wall_foot_transition_post_audit_v1.json`.
- Automation:
  `Content/Python/OperationSunscar/AutomationV1/abiverd_wall_foot_transition_preflight_v1.py`,
  `Content/Python/OperationSunscar/AutomationV1/abiverd_wall_foot_transition_hism_v1.py`,
  `Content/Python/OperationSunscar/AutomationV1/abiverd_wall_foot_source_consolidation_v1.py`
  and
  `Content/Python/OperationSunscar/AutomationV1/abiverd_wall_foot_transition_post_audit_v1.py`.

### Quixel cloth import and Covered Bazaar canopy conversion — 2026-08-05

- Located the already downloaded Quixel `Wrinkled Tarp` source directly in the
  local Fab/Vault cache without reopening Epic Games Launcher. The verified
  source is scan ID `vieldbo`, captured in Pakistan, with real dimensions of
  approximately 2.77 × 1.51 × 0.10 m.
- Imported the High glTF source into the map-owned heritage folder at
  `/Game/Maps/Sunscar/Art/Heritage/Props/WrinkledTarp`. The configured mesh is
  Nanite-enabled, uses an opaque two-sided packed-ORM material, caps runtime
  BaseColor/Normal/ORM textures at 2K and retains the unused Height texture at
  a 1K cap.
- The imported mesh independently audited at 276.886 × 151.093 × 10.339 cm.
  The import created no level change and ended with an empty dirty-package
  list.
- Reused the eight existing `SS_017` north/south canopy actors rather than
  creating a parallel canopy system. Each former graybox slab now references
  the Quixel tarp and uses one uniform 1.33629 scale, producing an approximate
  3.70 × 2.02 × 0.14 m cloth panel.
- Preserved the authored canopy centres and alternating orientation. The
  verified minimum underside clearance is 273.092 cm and the remaining central
  Bazaar passage is 918.096 cm wide.
- All eight cloth actors have actor collision disabled, component
  `NoCollision`, no navigation contribution, no simulation, no tick and no
  replication. Static shadows remain enabled so the canopy rows provide
  readable shade.
- The apply saved exactly eight World Partition external-actor packages. An
  independent post-audit verified every mesh reference, bounds, collision/nav
  flag and central-passage width; the map remained clean.
- The final Map Check completed with 0 errors and 0 warnings in 17.801 ms.
- Reports:
  `Saved/OperationSunscar/Reports/abiverd_wrinkled_tarp_import_v1_dry_run.json`,
  `Saved/OperationSunscar/Reports/abiverd_wrinkled_tarp_import_v1_apply.json`,
  `Saved/OperationSunscar/Reports/abiverd_wrinkled_tarp_import_post_audit_v1.json`,
  `Saved/OperationSunscar/Reports/abiverd_bazaar_tarp_canopy_dry_run_v1.json`,
  `Saved/OperationSunscar/Reports/abiverd_bazaar_tarp_canopy_apply_v1.json`,
  `Saved/OperationSunscar/Reports/abiverd_bazaar_tarp_canopy_post_audit_v1.json`
  and
  `Saved/OperationSunscar/Reports/abiverd_focus_bazaar_tarp_review_v1.json`.
- Automation:
  `Content/Python/OperationSunscar/AutomationV1/abiverd_wrinkled_tarp_import_v1.py`,
  `Content/Python/OperationSunscar/AutomationV1/abiverd_wrinkled_tarp_import_post_audit_v1.py`,
  `Content/Python/OperationSunscar/AutomationV1/abiverd_bazaar_tarp_canopy_v1.py`,
  `Content/Python/OperationSunscar/AutomationV1/abiverd_bazaar_tarp_canopy_post_audit_v1.py`
  and
  `Content/Python/OperationSunscar/AutomationV1/abiverd_focus_bazaar_tarp_review_v1.py`.

### Historic Desert Ruin Floor Sand Coarse Landscape integration — 2026-08-05

- Acquired, imported and saved the Quixel Megascans surface `Historic Desert
  Ruin Floor Sand Coarse 01` (scan ID `xbohccs`) directly from Fab. The import
  contains the material instance plus 4K BaseColor, Height, Normal and packed
  ORM textures.
- Reused the existing deterministic `RoadsideSilt` Landscape semantic layer,
  represented internally by the material's `Farm` parameters, instead of
  creating another Landscape target layer or changing any painted weightmap.
  This keeps the authored gameplay coverage intact and confines the coarse
  heritage sand to its already planned regions.
- Replaced the previous fine military-trench dirt references with the Quixel
  BaseColor and Normal textures. The new world-space tile size is 120 cm,
  appropriate to the scan's visible aggregate scale and substantially less
  repetitive than the former broad ground treatment.
- Set runtime maximum texture sizes to 2048 for BaseColor, Normal and ORM and
  1024 for the currently unused Height map. The source 4K assets remain
  available for later art-direction decisions without forcing 4K residency in
  the current multiplayer map draft.
- The material retained exactly 130 expressions. The conversion added zero
  Landscape layers and zero texture-sample expressions and did not modify the
  level, Landscape actors, collision or weightmaps.
- Because `/Game/Fab` is intentionally Git-ignored, the four runtime textures
  were promoted into the tracked map-owned folder
  `/Game/Maps/Sunscar/Art/Heritage/Surfaces/HistoricDesertRuinFloorSandCoarse01/Textures`.
  The Landscape now references those map-owned copies, making the committed
  map self-contained. The imported Fab material instance remains intact only
  as a local source reference.
- The final promotion saved exactly five content packages: the four map-owned
  `xbohccs` textures and
  `/Game/Maps/Sunscar/Art/Materials/LandscapeV3/M_OT_Landscape_Abiverd`.
- Independent post-audit verified two `Farm_BaseColor` parameter nodes, one
  `Farm_Normal` node, two `Farm_TileCm` nodes, the 120 cm scale, all texture
  references and caps, and an empty dirty-package list.
- The final Map Check completed with 0 errors and 0 warnings in 21.149 ms.
- Reports:
  `Saved/OperationSunscar/Reports/abiverd_floor_sand_import_audit_v1.json`,
  `Saved/OperationSunscar/Reports/abiverd_floor_sand_landscape_dry_run_v1.json`,
  `Saved/OperationSunscar/Reports/abiverd_floor_sand_landscape_apply_v1.json`,
  `Saved/OperationSunscar/Reports/abiverd_floor_sand_map_owned_dry_run_v1.json`,
  `Saved/OperationSunscar/Reports/abiverd_floor_sand_map_owned_apply_v1.json`
  and
  `Saved/OperationSunscar/Reports/abiverd_floor_sand_landscape_post_audit_v1.json`.
- Automation:
  `Content/Python/OperationSunscar/AutomationV1/abiverd_floor_sand_import_audit_v1.py`,
  `Content/Python/OperationSunscar/AutomationV1/abiverd_floor_sand_landscape_v1.py`,
  `Content/Python/OperationSunscar/AutomationV1/abiverd_floor_sand_map_owned_v1.py`
  and
  `Content/Python/OperationSunscar/AutomationV1/abiverd_floor_sand_landscape_post_audit_v1.py`.

## Validation state

- Every completed pass ended with an empty Unreal dirty-package list.
- The latest level loads with Map Check: `0 Error(s), 0 Warning(s)` after the
  corrective window, parapet, Consulate plaster, dusty-recess, instanced
  window-trim, Old Town wall-foot transition and Covered Bazaar cloth-canopy
  work, including the localized Quixel heritage-sand Landscape substitution.
- The latest façade-axis correction saved one actor package.
- The editor status after visual review was `All Saved`.
- The original opening-facade audit verified the first attempt, but that visual
  treatment is now superseded. The corrective audit verifies zero remaining
  full-storey window HISM instances and all 28 temporary frame/glass cues
  restored with NoCollision.
- The independent opening-surround V2 audit verified 42 instances, two HISM
  material batches, no collision, no replication, 12 m/30 m culling, nine real
  doors preserved, two false Hotel door cues disabled and five shell passages
  preserved. Dirty-package lists were empty before and after the audit.
- A first-person PIE review placed the TacticalMovement pawn directly in front
  of Tea House, Clinic, Detention Annex and Consulate. Clinic, Detention Annex
  and Consulate passed the initial grounding, doorway-clearance and eye-line
  review. Tea House is grounded and non-blocking, but its low roof makes the
  full-height modules project above the roofline; this is retained as a
  site-specific silhouette-tuning item rather than a global scale change.
- One read-only audit initially encountered an Unreal 5.8 Python API naming
  difference while querying replication. No map modification occurred. The
  query was corrected and the full audit passed.
- The opening-placement helper now uses Unreal 5.8's current
  `add_instance(..., world_space=True)` API rather than the deprecated
  `add_instance_world_space` method.
- A reported editor crash during review was investigated. The process was still
  running, the current log contained no fatal error/assertion, and no new crash
  report had been created. The same isolated editor session was foregrounded and
  recovered. Later automation sessions exited normally.
- Follow-up correction: the three visual-review helpers had used
  `set_keep_python_script_alive(True)` so an `-ExecutePythonScript` launch would
  remain interactive. That persistent Python execution was removed after it
  repeatedly destabilized the editor. Review helpers are now one-shot camera
  setters. Future interactive review launches must open Unreal normally without
  a persistent Python script.
- Two later crash-reporter popups were independently identified as Epic Games
  Launcher/project-browser shutdown failures, not crashes of the isolated
  TacticalMovement map editor. The healthy editor process, project path and
  loaded map remained intact. Epic Games Launcher is therefore excluded from
  the remainder of this editor session.

## Current visual assessment

The Landscape seams and planning-label clutter are gone, Abiverd landmarks and
spring vegetation exist, and the Old Town shells now have an initial architectural
skin. The incorrect full-storey window slabs and offset duplicate parapets are
gone, and the Consulate has the first reviewed shared-plaster treatment. Verified
doors/open passages retain a consistent surround language. The map is still a
first structural-art draft rather than a finished art pass. The largest remaining
façade gaps are Tea House/Hotel shade, cornices and less repetitive district silhouettes.
The first deterministic wall-foot rubble/grass transition pass is complete at
the eight reviewed Old Town sites. The Covered Bazaar's eight graybox canopy
slabs are now real Quixel cloth with gameplay-safe clearance and no collision.
The previously generic `RoadsideSilt` regions now use the Quixel Historic Desert
Ruin Floor Sand Coarse surface at a verified 120 cm world-space scale without
adding a new Landscape layer or disturbing the authored coverage masks.
The new dark recesses and shallow masonry lintels/sills are
an opening-scale first draft; individual landmark façades can still receive
site-specific shutters or complete compatible wall-bay replacements after PIE
readability review.

## Verified heritage asset state

Historic Pakistan Street Wall Brick Modular 16 is no longer blocked: its High
source, UE bounds, material configuration and first nine placements are now
verified. Historic Pakistan Street Window Brick Modular 04 is also no longer
blocked: its exact `e5026e65` High source, bounds, material configuration,
map-owned import and first 14 opening-aware placements are verified.

The project/Vault currently contains these verified heritage sources:

- Historic Desert Ruin Arch Stone Carved 08
- Historic Desert Ruin Wall Modular Set 04
- Historic Desert Ruin Structure Stone S 06
- Historic Desert Ruin Wall Brick 03 surface
- Historic Pakistan Street Wall Brick White 01 surface
- Historic Pakistan Street Wall Brick Modular 16 High glTF, map import and
  configured civic-facade instances
- Historic Pakistan Street Window Brick Modular 04 High glTF and map import.
  Its use as an overlaid window insert is rejected; it is retained only for a
  future complete wall-bay rebuild where its real scale and architecture fit.

## Next execution order

1. Add a restrained cloth-shade and balcony-language pass to Tea House and
   Hotel without creating climb exploits; the Covered Bazaar conversion is
   complete.
2. Validate door/window readability, Hotel silhouette, roof parapet collision
   and wall-foot visibility in PIE.
3. Replace only selected landmark wall bays with complete compatible modular
   bays after bounds and traversal verification; do not overlay the full-storey
   Pakistan window scan on unrelated shells.
4. Run a performance capture with Old Town cells loaded before expanding the
   visual pass to P1 buildings.

No Git commit or push was performed for this progress entry.

## 2026-08-05 — Established Landscape relief V1

- Replaced the flat Old Town physical terrain with a real 2017 x 2017 UE 5.8
  Landscape height pass. The final import uses a lossless RG16 transfer
  (`R=high byte`, `G=low byte`) through the editor's Landscape render-target
  API; the earlier single-channel experiment was rejected and its unsaved
  Landscape changes were reloaded from disk.
- The generated relief retains the authored regional terrain, adds broad
  alluvial variation, low settlement mounds and shallow dry drainage forms,
  and fades to the existing outer terrain before the authored districts.
- Corrected the heightmap's Unreal world-Y orientation after a read-only audit
  proved that the first foundation masks were mirrored north/south.
- The physical Landscape now matches all 12 verified first-floor slab bottoms.
  The final five-point trace audit found complete support at every slab; the
  largest absolute mismatch was 0.974 cm at `Core_SS_016_F1_Floor`, with the
  other slabs within 0.175 cm.
- A 195-point Old Town Landscape sample measured 32386.774–35687.894 cm,
  giving 3301.120 cm (33.0112 m) of real terrain range instead of a flat
  gameplay plane.
- Saved exactly the 16 audited Landscape streaming-proxy packages. The source
  heightmaps and their round-trip report live under
  `Documentation/Maps/OperationSunscar/Source/Heightmaps`; the original
  `Sunscar_Height_2017_BaseBackup.png` remains the rollback source.
- Map-owned transfer assets are under
  `/Game/Maps/Sunscar/Art/Terrain/ReliefV1`. The import switch was reset to
  dry-run after application.
- Final Unreal Map Check: 0 errors and 0 warnings.
- The rejected temporary sphere/mesh terrain experiment was never saved. Its
  actors and orphaned unsaved component packages were discarded before the
  final Landscape pass.
- Primary reports:
  `Saved/OperationSunscar/Reports/abiverd_terrain_relief_preflight_v1.json`,
  `Saved/OperationSunscar/Reports/abiverd_terrain_relief_rg16_import_apply_preview_v1.json`,
  `Saved/OperationSunscar/Reports/abiverd_terrain_relief_post_preview_audit_v1.json`
  and
  `Saved/OperationSunscar/Reports/abiverd_terrain_relief_save_v1.json`.
- Next terrain work is visual rather than structural: conform the 288 ground
  overlays and routes to the new physical grade, then add distance-aware
  texture variation/cell bombing to the Landscape material. Near-field
  microvariation should be limited to the playable Old Town cells; macro color
  breakup should cover the distant Landscape without multiplying texture
  samples at every distance.

No Git commit or push was performed for this terrain entry.
