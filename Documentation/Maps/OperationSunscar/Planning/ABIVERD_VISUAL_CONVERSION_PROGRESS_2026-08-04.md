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

## Validation state

- Every completed pass ended with an empty Unreal dirty-package list.
- The latest level loads with Map Check: `0 Error(s), 0 Warning(s)`.
- The latest façade-axis correction saved one actor package.
- The editor status after visual review was `All Saved`.
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

## Current visual assessment

The Landscape seams and planning-label clutter are gone, Abiverd landmarks and
spring vegetation exist, and the Old Town shells now have an initial architectural
skin. The map is still a first structural-art draft rather than a finished art
pass. The largest remaining gap is varied, opening-aware modular façade geometry:
windows, door surrounds, arches, cornices, balconies/shade structures and less
repetitive district silhouettes.

## Remaining verified asset blocker

Historic Pakistan Street Wall Brick Modular 16 is no longer blocked: its High
source, UE bounds, material configuration and first nine placements are now
verified. Historic Pakistan Street Window Brick Modular 04 is user-confirmed
purchased and downloaded, correcting the earlier ownership record. However, the
current filesystem audit found no matching `e5026e65` source, Fab Vault folder,
Downloads file or project staging asset. It cannot be imported safely until its
High source is visible locally. No similarly named Pakistan window variation
will be substituted.

The project/Vault currently contains these verified heritage sources:

- Historic Desert Ruin Arch Stone Carved 08
- Historic Desert Ruin Wall Modular Set 04
- Historic Desert Ruin Structure Stone S 06
- Historic Desert Ruin Wall Brick 03 surface
- Historic Pakistan Street Wall Brick White 01 surface
- Historic Pakistan Street Wall Brick Modular 16 High glTF, map import and
  configured civic-facade instances

Window Brick Modular 04 should be reopened in Fab and its High glTF downloaded
again if necessary. Once its exact source appears locally, it will be staged,
bounds-audited and fitted only to compatible existing openings.

## Next execution order

1. Resolve and import the purchased Pakistan Window Brick Modular 04 High source.
2. Build opening-aware façade assemblies for Tea House, Clinic, Hotel,
   Detention Annex, Consulate and Bazaar.
3. Add cloth shade and balcony language to Tea House/Bazaar/Hotel without
   creating climb exploits.
4. Blend wall-foot rubble, weeds and silt transitions through deterministic
   instancing with route exclusions.
5. Validate door/window readability and roof parapet collision in PIE.
6. Run a performance capture with Old Town cells loaded before expanding the
   visual pass to P1 buildings.

No Git commit or push was performed for this progress entry.
