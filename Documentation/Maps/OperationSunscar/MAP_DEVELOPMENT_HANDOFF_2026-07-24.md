# Operation Sunscar — Map Development Handoff

Last verified: 2026-07-24  
Unreal Engine: 5.8.0  
Project: TacticalMovement

## 1. Current status

Operation Sunscar is a complete **movement-ready gameplay graybox** inspired
by the Confrontation version of SOCOM's Desert Glory. It is not a final
art-dressed production environment.

The graybox currently provides:

- A 2,520 × 2,520 metre World Partition landscape.
- A dense Old Town infantry core.
- Six expanded outer combat districts.
- Traversable roads, tracks, wadis, canal crossings and district links.
- Prototype buildings, defensive compounds, ruins and industrial structures.
- Collision-tested cover and route geometry.
- Map-local objective, connection and spawn placeholders.
- A temporary overhead label layer for orientation.
- A tested level-only fall-safety boundary.

The current Unreal level is:

`/Game/Maps/Blockout/Lvl_Blockout_01`

This level does not replace or modify:

`/Game/ThirdPerson/Lvl_ThirdPerson`

The project's startup/default map was not changed.

## 2. Isolated development environment

Worktree:

`/Users/jasonteck/UnrealEngine/_worktrees/map-development`

Project file:

`/Users/jasonteck/UnrealEngine/_worktrees/map-development/TacticalMovement.uproject`

Branch:

`feature/map-development`

Production base:

`881c891df41ca4b7ad81ddd706baf6e22ff9da94`

Graybox checkpoint commit:

`a0c07027a573d886975c9903a99db3c5bc679332`

At the 2026-07-24 verification, the graybox checkpoint matched
`origin/feature/map-development`. Production `main` was not changed.

## 3. Git state

The completed graybox is committed in:

`a0c07027a573d886975c9903a99db3c5bc679332`

Its map assets are contained under:

- `Content/Maps/Blockout/Lvl_Blockout_01*`
- `Content/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/`
- `Content/__ExternalObjects__/Maps/Blockout/Lvl_Blockout_01/`

Protected file hashes remained unchanged:

| Protected file | Git object hash |
| --- | --- |
| `Config/DefaultEngine.ini` | `2989c1f3cb8dab8c23198f0c756c63aaa762d80c` |
| `Content/ThirdPerson/Lvl_ThirdPerson.umap` | `4846f4d1766808f7b106516143c5b5128e0f7cbd` |

The checkpoint was verified on `origin/feature/map-development`.

The detailed Old Town asset, material and execution planning set is stored
under:

`Documentation/Maps/OperationSunscar/Planning/`

Start with:

`Documentation/Maps/OperationSunscar/README.md`

## 4. Design intent

The design preserves the recognizable gameplay idea of Desert Glory:

- A dense, asymmetric town core.
- Several distinct approaches into the town.
- Courtyards, alleys, walls and raised positions.
- Clear but contestable long routes outside the town.
- Strong transitions between close combat and open terrain.

The map is significantly larger than the original. Its expanded geography is
influenced by the Kaka–Abiverd region of southern Turkmenistan:

- Dry Karakum desert and hardpan.
- Abiverd-style settlement ruins and caravan infrastructure.
- Irrigation and canal engineering.
- Quarry and exposed rock terrain.
- Agricultural and industrial edges.
- Historic east–west movement corridors.

Sunscar is fictional. It is geographically influenced by this region but is
not presented as an exact recreation of a real site.

## 5. Landscape specification

| Setting | Value |
| --- | --- |
| Heightmap | 2017 × 2017, 16-bit |
| Terrain coverage | 2,520 × 2,520 m |
| Landscape XY scale | 125 cm |
| Landscape Z scale | 29.296875 |
| Components | 16 × 16 |
| Sections per component | 2 × 2 |
| Quads per section | 63 |
| World origin | Old Town centre |
| East | Positive X |
| North | Positive Y |
| Designed elevation window | 300–450 m |
| Sampled playable terrain | approximately 310.7–405.8 m |
| Highest landscape bound | approximately 428 m |

The saved landscape bounds are:

- X: -1,260 to +1,260 m
- Y: -1,260 to +1,260 m

World Partition is active. There are 17 Landscape/Landscape Streaming Proxy
actors.

## 6. Playable districts

### Old Town Core

Actor tag: `SunscarCorePlayable`  
Verified actor count: 335

Purpose:

- Closest gameplay analogue to Desert Glory.
- Dense infantry combat.
- Short sightlines with intermittent cross-map views.
- Multiple independent routes through the town.

Key features:

- Water tower and accessible raised platform.
- Central courtyard.
- Bazaar quarter.
- Dry canal lane.
- North gate.
- Southwest entry.
- Multi-storey prototype buildings.
- Alleys, walls, ramps, rooftops and hard cover.

Primary tested routes:

- Alpha — Dry Canal
- Bravo — Courtyard
- Charlie — Bazaar

### West Abiverd

Actor tag: `SunscarWestAbiverdPlayable`  
Verified actor count: 221

Key features:

- Caravan Court.
- Kiln Yard.
- Old Road Checkpoint.
- Historic west road.
- Earthen mounds, ruins and settlement cover.

### North Karakum

Actor tag: `SunscarNorthKarakumPlayable`  
Verified actor count: 338

Key features:

- Caravanserai.
- Well Compound.
- Desert Checkpoint.
- Dune-cut route.
- Outer desert traverse.
- Hardpan and dune cover.

### East Canal

Actor tag: `SunscarEastCanalPlayable`  
Verified actor count: 220

Key features:

- Pump Hall.
- Freight Platform.
- Canal banks and service routes.
- Sluices and crossings.
- Bridge and freight access ramps.
- Refined transition cover.

### South Quarry

Actor tag: `SunscarSouthQuarryPlayable`  
Verified actor count: 194

Key features:

- Quarry Bowl.
- Cave Store.
- Signal Mast.
- Wadi route.
- Rock faces, ramps and quarry infrastructure.

### Southeast Works

Actor tag: `SunscarSoutheastWorksPlayable`  
Verified actor count: 208

Key features:

- Rail Yard.
- Reservoir.
- Outer Depot.
- Freight rail spur.
- Canal service road.
- Signal-mast logistics link.
- Southern vehicle bypass.
- Refined transition cover and service berms.

### Southwest Approach

Actor tag: `SunscarSouthwestApproachPlayable`  
Verified actor count: 174

Key features:

- Wadi Junction.
- Border Outpost.
- Smuggler Camp.
- Foothill traverse.
- Historic-road connection.
- Outer ridge and approach cover.

### Map support

Actor tag: `SunscarMapSupport`  
Verified actor count: 5

These actors support map organization and World Partition behavior.

## 7. Gameplay placeholders

There are 46 map-local gameplay placeholders. They are intentionally
logic-free and always loaded.

They represent:

- Objective target points.
- Objective volumes.
- District connections.
- Forward-spawn anchors.

The forward-spawn layer contains 12 TargetPoint anchors:

- Two per outer sector.
- Six Team A anchors.
- Six Team B anchors.
- Six inner anchors.
- Six outer anchors.

Tags include:

- `SunscarSectorSpawnAnchor`
- `SpawnAnchor_TeamA`
- `SpawnAnchor_TeamB`
- `SpawnRole_Inner`
- `SpawnRole_Outer`
- `ModeSector_West`
- `ModeSector_North`
- `ModeSector_East`
- `ModeSector_South`
- `ModeSector_Southeast`
- `ModeSector_Southwest`

Important: these are **spawn-location placeholders**, not active PlayerStart
actors and not finished game-mode logic.

The eight original Old Town PlayerStart actors were left intact.

## 8. Temporary label layer

There are 48 collision-free TextRender labels grouped under:

`Sunscar/TemporaryLabels`

The label categories are:

| Category | Count | Intended colour |
| --- | ---: | --- |
| Sector titles | 7 | Cyan |
| Objectives | 17 | Yellow |
| Forward spawns | 12 | Team A blue / Team B red |
| Old Town landmarks | 6 | White |
| Major routes | 6 | Green |

The labels:

- Are map-local.
- Have collision disabled.
- Generate no overlaps.
- Are always loaded.
- Are intended for Top/aerial view.
- Can be hidden by toggling the `Sunscar/TemporaryLabels` folder in the World
  Outliner.

They are visualization guides and do not affect movement.

Saved overview image:

`/tmp/Sunscar_Labeled_Overview.png`

The `/tmp` image is only a local preview and should not be treated as a
durable project asset.

## 9. Movement and collision verification

The live `BP_ThirdPersonCharacter_C` runtime pawn was used for the regression
tests.

Test pawn measurements:

| Property | Value |
| --- | ---: |
| Capsule radius | 35 cm |
| Capsule half-height | 90 cm |
| Walk speed used for timing | 5 m/s |
| Walkable floor angle | approximately 44.765° |

Twenty-six representative routes passed without a blocking collision:

### Old Town

- Alpha — Dry Canal
- Bravo — Courtyard
- Charlie — Bazaar

### West

- Main Road to Checkpoint
- North Track to Caravan Court
- South Link to Kiln Yard
- Historic Road West

### North

- Old Town to Caravanserai
- Caravanserai to Northeast Checkpoint
- West Abiverd to Well and Northwest
- Well to Caravanserai Dune Cut
- Canal to Outer Desert
- Outer Desert Traverse

### East

- Central approach to Pump Hall
- North approach to Sluices
- South approach to Freight Platform

### South

- Core South to Quarry
- West Wadi to Cave
- Ridge to Signal Mast

### Southeast

- East Freight to Outer Spur
- Canal to Reservoir Spillway
- Signal Mast to Rail Yard
- Southern Vehicle Bypass

### Southwest

- West Abiverd to Outer Border
- South Quarry to Outer Ridge
- Outer Foothill Traverse
- Historic Road to Smuggler Camp

The detailed Old Town connectivity test used a 0.5 m navigation grid and
actual 70 cm-wide pawn capsule traces. All three independent routes passed.

## 10. Combat-spacing refinement

Fifty-two additional transition pieces were added:

- 24 in East Canal.
- 28 in Southeast Works.

These include:

- Cover walls.
- Infrastructure boxes.
- Cargo clusters.
- Rock boundaries.
- Service berms.

The refinement reduced the worst measured open cover distance from
approximately 212 m to approximately 53–56 m.

A previously continuous exposed bypass run of approximately 619 m was broken
into tactical intervals of approximately 39–118 m while preserving the
vehicle route.

One berm initially obstructed a route during testing. It was moved off the
route and the regression was rerun successfully.

## 11. World safety

The map's level-only WorldSettings use:

| Setting | Value |
| --- | ---: |
| Kill Z | 25,000 cm / 250 m |
| World bounds checks | Enabled |
| World to metres | 100 |
| Default GameMode override | None |

The Kill Z is approximately 60 m below the lowest sampled terrain.

A runtime test moved the player pawn below the boundary and confirmed that
the pawn was removed as expected.

No project configuration file was changed to implement this.

## 12. Final validation state

Last saved validation:

- Total level actors: 1,849.
- Temporary labels: 48.
- Gameplay placeholders: 46.
- World Partition label and gameplay placeholders are always loaded.
- Temporary labels have no collision.
- Map Check: 0 errors, 0 warnings.
- No dirty map packages remained after the restricted save.
- No dirty content packages remained after the restricted save.
- No unexpected Git paths were present.

## 13. What is deliberately not finished

The following are later production phases:

- Final architecture and environment art.
- Final terrain materials and landscape-layer painting.
- PCG vegetation and rock dressing.
- Final road, rail and canal spline conversion.
- Final lighting, sky, fog and post processing.
- Audio and environmental effects.
- Finished game-mode objective logic.
- Finished spawn-selection logic.
- Navigation, AI encounter logic and vehicle gameplay.
- Optimization, HLOD generation and shipping performance passes.
- Final collision pass after art replacement.

Do not mistake the current prototype shapes for intended final visuals.

## 14. Durable source files

Terrain, mask and design source material is stored under:

`/Users/jasonteck/Documents/UE FPS Project/MapDesign/Desert_Glory_Inspired`

Important files:

- `Desert_Glory_Inspired_Map_Plan.md`
- `Sunscar_Topography_and_Site_Spec.md`
- `BuildPack_v1/README.md`
- `BuildPack_v1/Heightmaps/Sunscar_Height_2017.png`
- `BuildPack_v1/Heightmaps/Sunscar_Height_2017.r16`
- `BuildPack_v1/Manifests/Sunscar_BlockoutManifest.json`
- `BuildPack_v1/Manifests/Sunscar_SiteManifest.json`
- `BuildPack_v1/Manifests/Sunscar_SplineManifest.json`
- `BuildPack_v1/Masks/`
- `tools/generate_sunscar_buildpack.py`
- `tools/sunscar_build_config.json`

Warning: `BuildPack_v1/UNREAL_IMPORT_RUNBOOK.md` describes an earlier proposed
map path and workflow. The authoritative finished level path is
`/Game/Maps/Blockout/Lvl_Blockout_01`.

Some one-time Unreal Editor automation and regression scripts were executed
from `/tmp`. Those temporary scripts are not Git-backed and should not be
considered the durable source of truth. The saved Unreal map and this handoff
are the current authoritative implementation record.

## 15. Safe restart procedure for another Codex chat

1. Verify that no other Unreal Editor is editing the project.
2. Use only:
   `/Users/jasonteck/UnrealEngine/_worktrees/map-development`
3. Confirm the branch is:
   `feature/map-development`
4. Confirm HEAD is:
   `881c891df41ca4b7ad81ddd706baf6e22ff9da94`
5. Open only:
   `/Users/jasonteck/UnrealEngine/_worktrees/map-development/TacticalMovement.uproject`
6. Open:
   `/Game/Maps/Blockout/Lvl_Blockout_01`
7. Do not change `DefaultEngine.ini` or the startup/default map.
8. Do not modify `Lvl_ThirdPerson`.
9. Keep changes inside the dedicated map paths.
10. Before saving, check for unexpected dirty packages or mass resaves.
11. Do not commit or push without Jason's separate approval.

## 16. Recommended next decision

The map is ready for movement-system work.

Before beginning final art, the next map-specific decision should be one of:

1. Wire one sector into a real 4v4 game-mode prototype.
2. Convert the major route guides into editable Landscape Splines.
3. Begin a district-by-district environment-art pass, starting with Old Town.

Movement changes should remain outside this map-development worktree unless a
separate integration plan is approved.
