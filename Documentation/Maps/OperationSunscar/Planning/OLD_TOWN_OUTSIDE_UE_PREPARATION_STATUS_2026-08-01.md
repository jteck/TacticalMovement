# Old Town Outside-Unreal Preparation Status

Date: 2026-08-01  
Scope: planning and automation preparation only  
Unreal Editor changes: none

## Completed in this pass

- Audited the local planning set and existing map-development automation.
- Confirmed approximately 512 GiB of free disk space on the project volume.
- Confirmed no Old Town FBX, GLTF, GLB, or official pack download library exists in the expected local download locations.
- Reused the safety design of existing map scripts: exact-level verification, tagged cleanup, terrain tracing, simple collision proxies, restricted saves, and deterministic naming.
- Generated 2,350 deterministic candidate records across all 20 Old Town sites.
- Added source-role eligibility so asset roles can only be assigned to appropriate sites.
- Added exact forced allocations for vehicles, Tea House/Bazaar furniture and shade, utilities, road markings, oil stains, and tactical rocks.
- Corrected the first aggregate BOM where it was too repetitive or locally implausible.
- Generated an asset-path registry by comparing the BOM with files already present in the map-development worktree.

## Verified candidate result

- Candidate records: 2,350
- Site count: 20
- BOM role count: 49
- Mismatched BOM roles: 0
- Mismatched site totals: 0
- Status of every transform: `candidate_not_final`

Candidate XY locations are deterministic and useful for automation. They are not represented as final placements. Unreal must still resolve terrain/facade Z, sockets, collision, exclusions, and gameplay approval.

## Asset registry result

- Five BOM roles already resolve to existing project assets.
- Sixteen map-owned roles have complete dimensional definitions but still need their final project asset paths or assembly implementation.
- Twenty-eight official-source roles require acquisition or staging inspection.
- Existing support assets include the two sandbag meshes, corrugated barrier, rock ground patch, rocky ground, damaged plaster, crushed asphalt, weathered concrete, and the current Old Town material instances.

## Corrections made to the earlier BOM

- Static vehicles reduced from seven to five: three Salvage Yard and two Motor Pool.
- Road-barrier pieces reduced to twelve; approved graybox cover skins increased instead.
- Small electrical boxes reduced to twenty and distributed across utility-facing sites.
- Medium enclosures reduced to twelve and large cabinets reduced to four.
- Pipes and conduit increased because a pipe network contains many modular pieces without adding new tactical cover.
- Roof vents/antennae reduced and distributed among six appropriate roof sites.
- Oil/service stains reduced to twenty and locked to Pump, Freight, Salvage, Motor Pool, and Substation sites.
- Single-mesh rock patches reduced; multi-variant small rubble increased.
- Tea House and Bazaar shade, poles, seating, and goods now have explicit minimum allocations.

## Fab library acquisition result

- The existing `high-Tek` account was confirmed and used.
- Forty exact listings were inspected by listing ID.
- Thirty-eight verified free Epic Games or Quixel Megascans listings were added to My Library.
- Two Quixel tarp listings were deferred because Fab now presents paid licenses from $0.99 to $9.99.
- No purchases, unknown-publisher acquisitions, downloads, installs, or Unreal imports were performed.
- The exact record is in `OLD_TOWN_FAB_LIBRARY_STATUS_2026-08-01.csv` and `OLD_TOWN_FAB_ACQUISITION_REPORT_2026-08-01.md`.

## Files

- `OLD_TOWN_PROP_CANDIDATE_PLACEMENTS_V1.csv` — compact candidate ledger.
- `OldTown_PropCandidatePlacements_v1.json` — full machine-readable candidate manifest.
- `OLD_TOWN_PROP_CANDIDATE_VALIDATION_V1.json` — reconciliation report.
- `OldTown_AssetPathRegistry_v1.json` — resolved, map-owned, and unresolved asset-path ledger.
- `../tools/generate_old_town_prop_candidates.mjs` — deterministic candidate generator.
- `../tools/generate_old_town_asset_registry.mjs` — asset-registry generator.

## Acquisition and placement-resolution update

- All 38 approved free listings have been downloaded: 35 direct archives and
  three official packs.
- Local source/staging content totals 24,793,643,127 bytes.
- All 2,350 placement candidates now resolve to a staged pack asset, downloaded
  direct source, existing project asset or map-owned definition.
- Zero BOM mappings and zero referenced local sources are missing.
- The two paid tarp records remain excluded; the map-owned canopy plane and
  existing `MI_OT_Canvas` are the selected fallback.
- `FAB_P1A_016` Dried Grass was corrected from an instanced-plant assumption to
  a surface underlay; downloaded Military Trench grass meshes supply geometry.

See `OLD_TOWN_ASSET_AUDIT_AND_PLACEMENT_RESOLUTION_2026-08-01.md` for the full
handoff and `OldTown_ResolvedPlacementPlan_v1.json` for the machine-readable
execution plan.

## Next actions

1. Keep Unreal closed until the movement owner releases the editor.
2. Inspect only the exact offline candidates in UE 5.8 staging.
3. Record bounds, pivots, dependencies, collision, Nanite and visual acceptance.
4. Migrate only accepted assets and required dependencies.
5. Execute the connected visual slice before applying the full 2,350-record plan.
6. Resolve final production `/Game/...` paths after dependency-safe migration.
