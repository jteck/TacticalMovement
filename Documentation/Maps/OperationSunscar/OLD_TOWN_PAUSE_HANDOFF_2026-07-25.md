# Operation Sunscar — Old Town Pause Handoff

Pause date: 2026-07-25  
Status: Saved in Unreal; current Old Town art pass is not committed  
Authority: This document records the exact stopping point for the current map-development session.

## 1. Safe workspace

- Worktree:
  `/Users/jasonteck/UnrealEngine/_worktrees/map-development`
- Branch:
  `feature/map-development`
- Current committed branch tip:
  `f7c84efbd70cf7340f0a7ce14b4508ede2335403`
- Original production base:
  `881c891df41ca4b7ad81ddd706baf6e22ff9da94`
- Project:
  `/Users/jasonteck/UnrealEngine/_worktrees/map-development/TacticalMovement.uproject`
- Level:
  `/Game/Maps/Blockout/Lvl_Blockout_01`
- Current saved level actor count:
  `2,600`

The current visible Old Town state is newer than the committed branch tip.
The latest map packages, Fab assets, Python automation and documentation are
present in this worktree but have not been committed or pushed.

## 2. Isolation and protected scope

Work remained inside the dedicated map-development worktree. No movement,
weapon, animation, readiness or production configuration work was performed.

Protected items that were not modified:

- `/Game/ThirdPerson/Lvl_ThirdPerson`
- `Config/DefaultEngine.ini`
- the project's default startup map
- production `main`
- movement worktrees and branches
- diagnostic worktrees and branches

Do not open, clean, switch, reset, rebase or otherwise operate on those
worktrees when resuming this map task.

## 3. Current Old Town result

The Old Town graybox is now a readable first art/blockout draft rather than
only disconnected prototype buildings. It contains:

- the existing Old Town building and compound layout;
- terrain-aware site pads and foundation contact treatment;
- connected surface-road overlays through the district;
- dry-drainage indicators;
- a raised Detention Annex terrace with readable access;
- defensive sandbag and corrugated-barrier dressing;
- utility poles, wires and small utility dressing;
- Quixel asphalt and rocky-ground surface dressing;
- temporary location labels for orientation;
- gameplay collision on the original blockout and on the new Detention Annex
  access steps.

The latest saved level contains 2,600 actors. World Partition stores many of
these as individual external actor and external object packages; a large Git
file count is normal for this map state.

## 4. Grounding and elevation work

All 20 planned Old Town sites were audited against the Landscape.

- 17 primary foundations matched terrain within a few centimetres.
- The Detention Annex remains intentionally elevated by roughly 69 cm on its
  raised terrace.
- 16 Quixel sandbag render actors and their collision proxies were grounded.
- 81 replaceable visual ground/foundation actors were added in the first
  grounding pass.
- 44 non-colliding utility-dressing actors were added.
- The V2 terrain-following pass added 214 actors:
  - connected road tiles subdivided to no more than approximately 10 m;
  - terrain-following road elevations;
  - narrow dry-drainage strips;
  - one additional foundation skirt where daylight was visible;
  - five colliding steps at the Detention Annex south entrance.

Materials alone do not correct floating buildings. The visible contact
problems were handled with geometry placement, skirts and access geometry.
The ground surfaces then improved the visual contact.

The road, drainage and rocky-patch actors are visual overlays and do not
provide collision. They are intentionally replaceable by final Landscape
materials and Landscape Splines. The five new Detention Annex steps use query
and physics collision.

## 5. Reproducible automation

The following map-owned scripts record the current procedural work:

- `Content/Python/OperationSunscar/old_town_ground_elevation_pass_v2.py`
- `Content/Python/OperationSunscar/place_quixel_ground_v1.py`
- `Content/Python/OperationSunscar/import_quixel_defensive_v1.py`
- `Content/Python/OperationSunscar/import_quixel_sandbag.py`
- `Content/Python/OperationSunscar/import_quixel_surfaces_v1.py`
- `Content/Python/OperationSunscar/place_quixel_defensive_v1.py`
- `Content/Python/OperationSunscar/place_quixel_sandbags_v1.py`
- `Content/Python/OperationSunscar/place_quixel_surfaces_v1.py`

The V2 elevation script is idempotent. It refuses to run outside
`Lvl_Blockout_01`, removes only actors carrying its own
`SunscarGroundElevationPassV2` tag, rebuilds the pass and saves only the
current map.

An initial V2 test exposed an Unreal Python positional `Rotator` mismatch that
pitched road tiles upright. It was detected immediately. The script was
corrected to use named yaw parameters and rerun after removing every actor
tagged by that pass. The saved level contains only the corrected, flat road
tiles.

Completion log lines from the corrected passes:

- `SUNSCAR_GROUND_ELEVATION_V2 actors=214 foundations=1 steps=5`
- `SUNSCAR_QX_GROUND imports_saved=14 asphalt=158 patches=16`

## 6. Official Quixel/Fab assets used

The current pass uses official Quixel Megascans content acquired through Fab.
The three latest ground listings were imported at Medium/2K:

1. Crushed Asphalt Ground  
   Fab listing: `88e41c55-6675-4872-ab19-e5757899e549`  
   Material:
   `/Game/Fab/Megascans/Surfaces/Crushed_Asphalt_Ground_sjyjcbja/Medium/sjyjcbja_tier_2/Materials/MI_sjyjcbja`

2. Sandstone Rocky Ground  
   Fab listing: `d6c87516-52ea-40d0-a3e5-c1e52d4ad88f`  
   Mesh:
   `/Game/Fab/Megascans/3D/Sandstone_Rocky_Ground_vmjjfiv/Medium/vmjjfiv_tier_2/StaticMeshes/vmjjfiv_tier_2`

3. Military Trenches Ground Patch Rock S 04  
   Fab listing: `d8aded40-25c6-40ec-9d10-6e5e15053222`  
   Mesh:
   `/Game/Fab/Megascans/3D/Military_Trenches_Ground_Patch_Rock_S_04_yd0lfcq/Medium/SM_yd0lfcq_tier_2/StaticMeshes/SM_yd0lfcq_tier_2`

The exact 14 packages saved for this latest import were:

- asphalt material instance plus `B`, `N` and `ORM` textures;
- sandstone material instance, static mesh, and `B`, `N` and `ORM` textures;
- military-trench patch material instance, static mesh, and `B`, `N` and
  `ORM` textures.

The real asphalt material is assigned to 158 existing asphalt overlay actors
without changing their transforms, collision or World Partition identity.
Sixteen visual-only rocky patches were placed around district edges and
dead-ground pockets. Nanite was enabled on the two imported 3D patch meshes
where supported.

Earlier official Quixel content already present in the same map scope
includes sandbag variants, corrugated defensive wall pieces, damaged plaster
and weathered concrete. Their required shared Fab materials, material
functions, parameter collection and default textures are also present in the
working tree and are map dependencies, not unrelated production changes.

## 7. Save and validation state

Completed checks:

- Unreal reported `All Saved`.
- Top-down inspection confirmed connected roads and drainage.
- Player-height inspection confirmed the road overlays read correctly.
- Close inspection confirmed the five Detention Annex steps align with the
  raised south entrance.
- Sandbags were visually grounded.
- Play-In-Editor started successfully with the player pawn and weapon.
- Play-In-Editor stopped normally and returned to the editor.
- The map remained saved after PIE.
- No protected movement, weapon, animation, readiness, configuration or
  `Lvl_ThirdPerson` path appeared in the scope audit.
- No current content file exceeded 50 MB.
- `git diff --check` passed before this handoff was created.

## 8. Current Git state

At the stopping audit:

- branch: `feature/map-development`;
- committed tip: `f7c84efbd70cf7340f0a7ce14b4508ede2335403`;
- the working tree was intentionally dirty with the current saved map pass;
- the fully expanded audit contained 675 entries before this pause document;
- those entries were concentrated in the new level, World Partition external
  packages, map-owned Sunscar assets, Fab dependencies, Python automation and
  map documentation;
- no content file exceeded 50 MB;
- `.uasset` and `.umap` do not currently have a Git LFS filter attribute.

The status includes deleted external-actor package names and new
external-actor package names. This can occur when World Partition actors are
replaced or resaved. These must be reviewed as one intentional map scope at
checkpoint time.

Do not use broad staging. A future checkpoint must enumerate and stage only:

- `Content/Maps/Blockout/Lvl_Blockout_01.umap`;
- its intentional `Content/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01`
  and `Content/__ExternalObjects__/Maps/Blockout/Lvl_Blockout_01` packages;
- intentional `Content/Maps/Sunscar` assets;
- required `Content/Fab` dependencies;
- `Content/Python/OperationSunscar` automation;
- `Documentation/Maps/OperationSunscar` documentation.

Generated folders such as `Saved`, `Intermediate`, `Binaries`,
`DerivedDataCache`, autosaves, logs, screenshots and temporary artifacts must
remain excluded.

No commit or push was made as part of creating this pause handoff. A separate
explicit checkpoint authorization is still required before committing or
pushing the current map state.

## 9. Known limitations

This is a first viewable Old Town art/blockout pass, not final environment
art.

- Roads are modular visual overlays, not final Landscape Splines.
- Ground coverage is not yet a final multilayer Landscape material.
- Rocky patches are non-colliding visual dressing.
- Several utility and architecture elements are still prototype geometry.
- Building shells have not received a full architectural replacement pass.
- Materials, decals, edge blending and dust accumulation need refinement.
- Combat-lane, traversal-time and cover-balance testing remains necessary.
- Labels are temporary navigation aids and should be hidden for final
  presentation captures.
- The rest of the larger Sunscar map remains future expansion; current work is
  intentionally focused on Old Town.

## 10. Safe resume procedure

1. Confirm no other Unreal instance is using this project.
2. Confirm the active worktree is:
   `/Users/jasonteck/UnrealEngine/_worktrees/map-development`
3. Confirm the branch is:
   `feature/map-development`
4. Record the current `git status` before opening Unreal. Do not clean or
   discard the existing map changes.
5. Open only:
   `/Users/jasonteck/UnrealEngine/_worktrees/map-development/TacticalMovement.uproject`
6. Open:
   `/Game/Maps/Blockout/Lvl_Blockout_01`
7. Confirm the level reports approximately 2,600 actors and visually contains
   the asphalt road network, rocky patches and Detention Annex steps.
8. Save only intentional map packages. Stop on unexpected dirty packages or
   mass resaves.
9. Do not change the default startup map, `DefaultEngine.ini` or
   `Lvl_ThirdPerson`.
10. Do not commit or push without a new explicit authorization.

## 11. Recommended next map pass

Resume in this order:

1. Replace the most visible remaining utility primitives with approved
   Epic/Quixel assets.
2. Apply the planned Old Town architecture surface set without changing the
   validated footprints or combat lanes.
3. Convert the modular road guides into editable Landscape Splines after
   confirming movement and vehicle needs.
4. Build the final Landscape material and blend road, dust, silt, stone and
   disturbed-ground zones.
5. Run a dedicated traversal, collision, sightline and cover-balance test.
6. Produce high-resolution labeled and unlabeled overview captures.
7. Perform a map-only Git scope audit and request checkpoint authorization.

## 12. Supporting documentation

Start with:

- `Documentation/Maps/OperationSunscar/README.md`
- `Documentation/Maps/OperationSunscar/MAP_DEVELOPMENT_HANDOFF_2026-07-24.md`
- `Documentation/Maps/OperationSunscar/Planning/OLD_TOWN_UE_EXECUTION_PACKET.md`
- `Documentation/Maps/OperationSunscar/Planning/OLD_TOWN_EXACT_SITE_ASSIGNMENTS.csv`
- `Documentation/Maps/OperationSunscar/Planning/OLD_TOWN_UE_STAGING_MANIFEST.csv`

The planning source is mirrored locally under:

`/Users/jasonteck/Documents/UE FPS Project/MapDesign/Desert_Glory_Inspired`
