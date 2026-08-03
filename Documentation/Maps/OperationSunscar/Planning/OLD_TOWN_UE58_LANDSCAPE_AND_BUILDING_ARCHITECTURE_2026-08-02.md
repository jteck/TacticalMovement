# Old Town UE 5.8 Landscape and Building Architecture

Date: 2026-08-02

## Outcome

The production architecture is now locked before further visible construction.
The current map is safe as a multiplayer blockout, but its building art is not
yet production geometry.

## Verified current state

- The loaded level is `/Game/Maps/Blockout/Lvl_Blockout_01` in the isolated
  `feature/map-development` worktree.
- The Old Town building audit found 200 visible structural Static Mesh Actors
  across 13 sites.
- All 200 use `/Engine/BasicShapes/Cube.Cube` and all 200 have a non-uniform
  scale ratio greater than 1.25.
- All 200 are Static mobility, non-replicated and non-ticking.
- None has an assigned HLOD layer.
- The visual roles include 47 walls, 27 lintels, 19 floors, 12 roofs, six
  ramps, five landings, four parapets and 80 additional structural pieces.
- The Landscape consists of one parent and four loaded Old Town streaming
  proxies. The accidentally deleted in-memory proxy was restored from its exact
  external-actor package and World Partition GUID. Nothing was saved during
  recovery.
- The unsaved Landscape V2 preview replaces the tiled overlay appearance with
  one continuous Landscape material and temporarily hides 288 legacy visual
  overlay actors.

## Production building model

Each building is split into two responsibilities:

1. **Gameplay shell** — simple invisible collision preserving doors, windows,
   traversal, cover, floor support and networking behavior.
2. **Visible art shell** — measured modular Epic/Quixel meshes, shared material
   instances and decorative details with collision disabled unless explicitly
   justified.

The gameplay shell must not be modified to accommodate art. The art must fit the
validated gameplay geometry.

Repeated approved modules are converted to Packed Level Actors or HISM/ISM only
after a building passes visual and gameplay review. World Partition HLOD is
built after the building is accepted. Static scenery never replicates or ticks.

## Nanite policy

Nanite is selective rather than global:

- Candidate: opaque high-detail static meshes after profiling.
- Excluded: simple collision, engine cubes, glass/translucency and tiny props.
- Landscape Nanite remains disabled until profiling because Epic documents that
  Nanite Landscape data streams alongside the normal Landscape representation,
  increasing resident and streaming data.

## Material policy

- Shared opaque masters and Material Instances.
- Packed masks and bounded texture families.
- Two-metre physical projection baseline for the existing world-aligned facade
  family, adjusted only after player-height inspection.
- No unique material per actor.
- No virtual-texture project-setting dependency in this conversion.
- Damage decals and vertex/macro variation are bounded rather than layered on
  every surface.

## Owned official-asset result

The current official Military Trench wall collection is unsuitable as the main
Old Town masonry kit. Its wall candidates are dirt, timber, corrugated metal or
sandbag construction; its roof candidates are timber trench frames. These are
valid for checkpoints, salvage structures and temporary additions, not for the
thirteen masonry building sites.

The free Epic Games City Sample Buildings pack is the current comprehensive
official modular source candidate. It contains more than 2,000 modules organized
as ground, wall, corner, entrance, pillar and roof/level pieces. Only generic
measured modules may be staged and visually tested; the complete pack must not
be migrated into the gameplay project, and New York-specific styling must not
be used merely because the source is official.

Quixel Historic Pakistan Street and compatible masonry scan pieces remain
high-fidelity visual candidates, but each listing must be measured, licensed and
reviewed before assignment. A surface texture does not replace a structural
module.

## First controlled conversion

`SS_005` Old Clinic is the first pilot because its facade material, openings,
doors, windows and support have already been audited. The pilot sequence is:

1. Record its exact existing shell and openings.
2. Review candidate modules in an isolated comparison area.
3. Build an unsaved visible art shell without deleting the current primitives.
4. Temporarily hide the old visible shell while retaining collision.
5. Validate player scale, doors, windows, sightlines, cover and terrain contact.
6. Capture street, oblique and overhead views.
7. Optimize repeated modules and assign HLOD.
8. Profile before any exact save.

The machine-readable gate is
`Content/Python/OperationSunscar/AutomationV1/old_town_ue58_building_conversion_config.json`.
It ships with apply and save disabled and contains no approved module paths.

## Continuation audit results

The broad filename-based architecture scan was replaced with a bounded set of
17 known owned Epic/Quixel candidates. All 17 exist and were measured in
Unreal. They are Nanite-enabled source meshes and include one 120 x 16.246 x
243.366 cm Quixel wooden door, corrugated wall pieces, timber roof frames,
timber walls, dirt trench walls and one rusted metal beam. This result does not
approve them as the primary Old Town kit. Their accepted scope is door art,
checkpoint/salvage construction and restrained industrial accents after visual
review. They do not provide the coherent masonry walls, corners, entrances,
windows and roof edges required for the main buildings.

The read-only `SS_005` pilot manifest found 45 site-linked actors, including 43
Static Mesh actors. Thirty-six currently show engine primitive geometry. No
site-linked actor replicates or ticks. The two verified first-floor openings
are each 140 cm wide by 200 cm clear height, measured from the finished floor
surface to the lintel underside:

- `Core_SS_005_F1_E`
- `Core_SS_005_F1_S`

The machine-readable report is generated locally at
`Saved/OperationSunscar/Reports/old_town_ss005_pilot_manifest_v1.json` and is
not tracked by Git.

The Message Log's six duplicate-location warnings were historical warnings
from two temporary facade comparison passes. A fresh read-only duplicate
location audit found zero duplicate transform groups in the currently loaded
scene. No actor deletion is required from that warning set.

The Landscape warning identified
`LandscapeStreamingProxy_1_1_0` and external package
`/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/9/EE/EFFLGT5PETOMG59WEAMRXF`.
During recovery Unreal synchronized `LandscapeMaterial` and repaired invalid
Landscape material instances in memory. The latest dirty-package audit does
not list that proxy package as dirty. It lists only the parent Landscape actor,
the unsaved Landscape V2 material, and the pre-existing `MarketRoute_01_04`
actor package. Nothing in this continuation was saved.

## Next conversion gate

Visible SS_005 conversion remains blocked until a coherent generic masonry
module family is actually present and explicitly assigned in the conversion
configuration. The next safe intake is a selective comparison set containing:

1. straight wall and short wall modules;
2. inner and outer corners;
3. door and window opening modules;
4. ground/roof/parapet edge modules;
5. one neutral masonry/plaster material family that supports shared instances.

City Sample Buildings is the preferred official source candidate, but modules
must be selectively staged and visually reviewed. Downloading or migrating that
pack is not authorized by this architecture pass. The apply gate and save gate
remain disabled.

## Epic references

- https://dev.epicgames.com/documentation/en-us/unreal-engine/world-partition-in-unreal-engine
- https://dev.epicgames.com/documentation/en-us/unreal-engine/level-instancing-in-unreal-engine
- https://dev.epicgames.com/documentation/unreal-engine/instanced-static-mesh-component-in-unreal-engine
- https://dev.epicgames.com/documentation/unreal-engine/using-nanite-with-landscapes-in-unreal-engine
- https://www.fab.com/listings/008fe959-5511-428e-93bd-f99b1179f6d5

## Save and Git state

This architecture pass does not authorize Save All, migration, commit, push,
merge or project-setting changes. Generated reports under `Saved/` are local
evidence and remain excluded from Git.
