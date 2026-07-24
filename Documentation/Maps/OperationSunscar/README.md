# Operation Sunscar Documentation Index

Last updated: 2026-07-24
Repository branch: `feature/map-development`

## Current map

- Unreal level: `/Game/Maps/Blockout/Lvl_Blockout_01`
- Worktree:
  `/Users/jasonteck/UnrealEngine/_worktrees/map-development`
- Graybox checkpoint commit:
  `a0c07027a573d886975c9903a99db3c5bc679332`
- Production base:
  `881c891df41ca4b7ad81ddd706baf6e22ff9da94`

## Start here

1. `MAP_DEVELOPMENT_HANDOFF_2026-07-24.md` — graybox state, map scope,
   validation and safe reopening instructions.
2. `Planning/OLD_TOWN_UE_EXECUTION_PACKET.md` — build sequence, Unreal
   folder contract, naming, Nanite, collision and completion criteria.
3. `Planning/OLD_TOWN_MASTER_ACQUISITION_PLAN.md` — official Epic/Quixel
   source strategy and paid-upgrade gates.
4. `Planning/OLD_TOWN_EXACT_SITE_ASSIGNMENTS.csv` — exact source assignments
   for all 20 Old Town sites.
5. `Planning/OLD_TOWN_MAP_OWNED_MODULAR_KIT.csv` — 33 map-owned modules with
   dimensions and collision rules.
6. `Planning/OLD_TOWN_UE_STAGING_MANIFEST.csv` — staging limits and
   exclusions for all 37 selected free sources.

## Design and geography

- `Desert_Glory_Inspired_Map_Plan.md` — full design history and district plan.
- `Sunscar_Topography_and_Site_Spec.md` — terrain, regional influence,
  coordinates and topographic specification.
- `ResearchData/kaka_abiverd_srtm90m.csv`
- `ResearchData/kaka_abiverd_srtm90m.json`

Sunscar is a fictional map influenced by the Kaka–Abiverd region of southern
Turkmenistan. It is not an exact recreation of a real place.

## Old Town planning set

### Production design

- `Planning/OLD_TOWN_ART_PRODUCTION_PLAN.md`
- `Planning/OLD_TOWN_SPATIAL_ASSET_METHOD.md`
- `Planning/OLD_TOWN_SITE_RECIPES.csv`
- `Planning/OLD_TOWN_ASSET_CATALOG.csv`
- `Planning/OldTown_ArtPlacementManifest_v1.json`

### Exact official-source research

- `Planning/OLD_TOWN_EXACT_FAB_SHORTLIST_P0.md`
- `Planning/OLD_TOWN_EXACT_FAB_SHORTLIST_P0.csv`
- `Planning/OLD_TOWN_EXACT_FAB_SHORTLIST_P1A.md`
- `Planning/OLD_TOWN_EXACT_FAB_SHORTLIST_P1A.csv`
- `Planning/OLD_TOWN_EXACT_FAB_SHORTLIST_P1B.md`
- `Planning/OLD_TOWN_EXACT_FAB_SHORTLIST_P1B.csv`
- `Planning/OLD_TOWN_MASTER_ACQUISITION_PLAN.md`
- `Planning/OLD_TOWN_MASTER_ACQUISITION_PLAN.csv`

The research evaluates 64 unique official Epic Games and Quixel Megascans
source records. The master plan selects 37 free sources. Ten paid upgrades are
deferred behind explicit visual-review gates. Required paid cost for the first
complete Old Town draft is `$0.00`.

Prices and catalog availability are snapshots from 2026-07-24 and must be
rechecked before acquisition.

### Unreal execution data

- `Planning/OLD_TOWN_EXACT_SITE_ASSIGNMENTS.csv`
- `Planning/OLD_TOWN_MAP_OWNED_MODULAR_KIT.csv`
- `Planning/OLD_TOWN_MATERIAL_INSTANCE_PLAN.csv`
- `Planning/OLD_TOWN_UE_STAGING_MANIFEST.csv`
- `Planning/OLD_TOWN_BUILD_CHECKPOINTS.csv`
- `Planning/OLD_TOWN_UE_EXECUTION_PACKET.md`

## Build-pack reference

- `BuildPackReference/BUILD_PACK_README.md`
- `BuildPackReference/UNREAL_IMPORT_RUNBOOK.md`

These predate the finalized Old Town execution packet. When instructions
conflict, the Old Town execution packet and exact site-assignment ledger take
precedence.

## Safety boundaries

- Do not overwrite `/Game/ThirdPerson/Lvl_ThirdPerson`.
- Do not change the project startup map or `Config/DefaultEngine.ini`.
- Do not modify movement, animation, weapons or readiness systems during map
  work.
- Stage large Fab packs in a separate UE 5.8 project.
- Never migrate complete City Sample, Junkyard or Military Trench example
  projects into TacticalMovement.
- Save only intentional map assets and documentation.
- Stop on unexpected files, mass resaves or protected-file changes.

## Planning provenance

The canonical local working copies were prepared under:

`/Users/jasonteck/Documents/UE FPS Project/MapDesign/Desert_Glory_Inspired`

The copies in this repository are the Git-versioned handoff set. Future
changes should update both locations or clearly designate the repository copy
as the new authority.
