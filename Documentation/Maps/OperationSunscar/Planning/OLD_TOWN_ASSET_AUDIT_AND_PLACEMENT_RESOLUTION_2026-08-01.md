# Old Town Asset Audit and Placement Resolution

Date: 2026-08-01
Scope: offline asset audit, deterministic placement resolution and Unreal execution preparation
Unreal Editor changes: none

## Outcome

The complete approved free acquisition set is now local and mapped into the
existing Old Town plan:

- 38 free official listings downloaded: 35 direct Quixel archives and three
  Epic/Quixel Unreal packs.
- 24,793,643,127 bytes of local source and staged-pack content inventoried.
- 2,350 pre-existing Old Town candidate placements retained.
- Every candidate now has a deterministic planned asset reference.
- Zero BOM roles lack an asset-selection mapping.
- Zero referenced downloaded/staged sources are missing locally.
- The two tarp listings that changed to paid remain excluded.

This does not claim that all 2,350 objects are final placements. XY, yaw,
scale, role, source and variant are now planned. Terrain/facade Z, exact pivot,
rendered appearance, dependency closure, collision, Nanite state and gameplay
acceptance remain Unreal validation gates.

## Evidence classification

### Verified facts

- Every direct archive exists locally and has a recorded byte size and SHA-256.
- Each direct archive contains Quixel metadata; 3D sources expose listed
  dimensions and tier triangle counts where present.
- Military Trench contains 2,001 `.uasset` files and 179 static-mesh files.
- City Sample Vehicles contains 1,404 `.uasset` files and 117 static-mesh files.
- Junkyard contains 472 `.uasset` files and 61 static-mesh files.
- The selected City, Junkyard and Military Trench candidate paths exist in the
  local staging copies.
- The existing candidate ledger contains 2,350 records across 20 sites.

### Offline selections—not yet visual approvals

- Five City Sample static render-mesh candidates are assigned to the Salvage
  Yard and Motor Pool budgets.
- Junkyard candidates are limited to large cover, barrels, containers, pallet,
  vehicle parts, wheels and low-profile scrap roles.
- Military Trench candidates are limited to sandbags, crates, rubble, small
  rocks and sparse grass roles.
- Direct Quixel archives are assigned by exact acquisition record and source
  identifier.

These selections are defensible from verified package structure and metadata,
but asset filenames do not prove appearance. Unreal visual inspection is still
required before migration or replacement of gameplay geometry.

## Important correction

`FAB_P1A_016` **Dried Grass** is a surface archive, not an instanced vegetation
mesh. It is now treated as a ground underlay. Actual instances for that role use
downloaded Military Trench dry-grass mesh candidates. This prevents the later
automation from trying to spawn a material as geometry.

## Source-state breakdown for the 2,350 planned instances

| Source state | Planned records |
| --- | ---: |
| Map-owned definition | 978 |
| Existing project asset | 208 |
| Downloaded direct source; UE import pending | 525 |
| Downloaded staged-pack asset | 639 |
| **Total** | **2,350** |

## Authoritative new files

- `OldTown_DownloadedAssetInventory_v1.json` — complete machine-readable
  download inventory, metadata, checksums, dimensions, pack statistics and
  deferred items.
- `OLD_TOWN_DOWNLOADED_ASSET_INVENTORY_V1.csv` — compact human-review version
  of the download inventory.
- `OldTown_ResolvedPlacementPlan_v1.json` — all 2,350 candidate records joined
  to exact staged paths, downloaded sources, existing assets or map-owned
  definitions.
- `OLD_TOWN_RESOLVED_PLACEMENT_PLAN_V1.csv` — flat automation ledger for all
  planned instances.
- `OLD_TOWN_ASSET_SELECTION_MATRIX_V1.csv` — 393 site/BOM/asset allocation
  rows showing precisely which candidate families go to each site.
- `OLD_TOWN_UE_IMPORT_QUEUE_V1.csv` — 121 unique assets and non-instance
  material/support dependencies ordered with the connected slice first.
- `../tools/generate_old_town_download_inventory.mjs` — reproducible local
  inventory generator.
- `../tools/generate_old_town_resolved_placement_plan.mjs` — reproducible join,
  validation and deterministic variant-assignment generator.

## Asset acquisition locations

```text
Assets/FabDownloads/
  Quixel_High_FBX/                         20 direct 3D archives
  Quixel_4K_Textures/                      15 direct surface/decal archives
  UnrealPacks/
    MilitaryTrenchMegascansSa/             Military Trench source project
    OfficialAssetStaging/
      Content/CitySampleVehicles/          City Sample Vehicles pack
      Content/Scene_Junkyard/              Junkyard pack
```

The large binary download library is local source material and must not be
committed to Git. Planning files, manifests, validation outputs and generators
are suitable for the map-development documentation tree.

## UE 5.8 execution order

1. Reverify the isolated `feature/map-development` worktree and keep Unreal
   closed until the movement owner releases it.
2. Before art migration, audit every existing sandbag actor. The current map has
   user-observed sandbags attached to or floating beside a building at roughly
   second-floor elevation. Treat this as a placement defect unless a specific
   roof/upper-floor defensive position is intentionally approved. Record actor
   names, attachment parents, world transforms and ground/floor traces; move or
   remove incorrect actors rather than hiding the issue with materials.
3. Create or reuse a clean UE 5.8 staging copy; do not use the staging source as
   the gameplay project.
4. Inspect the connected visual-slice assets first: facade surfaces, door,
   table, stool, bench, bazaar modules, canopy fallback and damage decals.
5. Record actual Unreal bounds, pivots, material slots, dependencies, collision
   and Nanite state in the asset registry.
6. Import/migrate only accepted assets and dependencies into the dedicated map
   art folders. Never migrate whole sample scenes.
7. Execute the connected slice from Municipal Hotel through Central Courtyard,
   Tea House, Covered Bazaar and the Detention approach.
8. Resolve Z by terrain traces or facade sockets; reject floating objects.
9. Validate traversal, sightlines, mantle chains, cover heights and weapon
   clearance before expanding to the remaining sites.
10. Continue with civic, industrial, canal/perimeter and secondary dressing
   passes in the existing execution packet order.
11. Capture clean and labeled review images and replace offline-candidate status
    with accepted, alternate or rejected after the first playable review.

## Logged UE review defect

### OT-REVIEW-001 — elevated building-attached sandbags

- Reporter: user visual review of the current Old Town map.
- Observation: some sandbags appear attached to a building around second-floor
  height rather than seated on valid ground or an intentional defensive floor.
- Current classification: **unknown cause; presumed unintended until verified**.
- Possible causes to inspect: incorrect world Z, actor attachment inheritance,
  facade socket selection, trace hitting an upper floor/roof, or an earlier
  placement script using the wrong surface.
- Required review: isolate all sandbag actors, inspect world transforms and
  attachment parents, trace vertically against intended support geometry, and
  view each placement from street and overhead perspectives.
- Acceptance: each sandbag cluster is visibly supported, intentionally located,
  gameplay-safe and documented; otherwise move or remove it.
- Explicit note: terrain textures and ground materials cannot correct actor
  transforms or attachment errors.

## Stop conditions

- Wrong project, worktree or level.
- Module/version conversion warning or incompatible-module bypass.
- Migration attempts to overwrite existing assets.
- Unexpected dependency expansion or whole-sample import.
- Protected movement, animation, weapon, readiness or configuration changes.
- Existing level mass-resave or files outside intentional map scope.
- An asset changes approved cover, route, opening, spawn or mantle geometry
  before explicit gameplay validation.

## Current readiness statement

Planning and acquisition are complete enough to begin a fast UE 5.8 visual
draft. The remaining uncertainty is intentionally concentrated in a bounded
staging inspection—not in broad design, sourcing or placement decisions.

## Offline automation preparation update

The UE automation package is prepared under
`../UnrealAutomation/OperationSunscar/` and has not been executed.

- `old_town_preflight.py` — exact project/worktree/level verification and
  read-only actor/tag inventory.
- `old_town_sandbag_audit.py` — read-only transform, attachment, support and
  terrain-elevation report for every likely sandbag actor.
- `old_town_asset_inspector.py` — read-only bounds, materials, Nanite,
  collision and dependency inspection against the 121-row import queue.
- `old_town_connected_slice_builder.py` — dry-run-first resolver; version 1
  never saves, deletes or automatically changes tactical cover.
- `sunscar_automation_common.py` and `old_town_automation_config.json` — shared
  safety gates, path restrictions and report handling.
- `OldTown_FinalAssetRegistry_v1.json` — deliberately unresolved acceptance
  registry that blocks apply mode until staged assets receive approved final
  `/Game/...` paths.

The current configuration has `apply_changes: false`, an empty approval token,
`save_current_level: false`, and tagged-actor destruction disabled.

Inspection of the earlier sandbag scripts found that they select the first
actor whose label begins with each site ID, derive a base Z from that actor and
a hard-coded height, place without a ground/support trace, and immediately save
the level. This is a credible explanation for the elevated-looking sandbags,
but remains an inference until the new audit records actual actor transforms,
attachments and supporting surfaces.
