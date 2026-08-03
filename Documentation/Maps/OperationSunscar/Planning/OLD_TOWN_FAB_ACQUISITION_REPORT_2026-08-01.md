# Old Town Fab Acquisition Report

Date: 2026-08-01  
Account: existing signed-in Epic/Fab account `high-Tek`  
Scope: acquire and inventory the verified free official Old Town source set

## Outcome

- 40 exact listings inspected by listing ID.
- 38 listings verified as free and published by Epic Games or Quixel Megascans, then added to My Library.
- 2 Quixel tarp listings were not acquired because Fab now presents paid licenses from $0.99 to $9.99.
- 0 paid purchases.
- 0 unknown-publisher acquisitions.
- All 38 approved free listings are now downloaded locally: 35 direct Quixel
  archives and three official Unreal packs.
- The local inventory contains 24,793,643,127 bytes of source/staging content.
- No assets were imported into TacticalMovement during acquisition.
- Unreal Editor remained closed during the final Launcher download pass.

The authoritative item-by-item record is `OLD_TOWN_FAB_LIBRARY_STATUS_2026-08-01.csv`.

## Important interpretation

`added_to_library` in the original library ledger records the entitlement step.
Download completion and local metadata are now recorded separately in
`OldTown_DownloadedAssetInventory_v1.json` and
`OLD_TOWN_DOWNLOADED_ASSET_INVENTORY_V1.csv`. Downloaded still does not mean
approved for production collision, final appearance or dependency-safe
migration.

The source-acquisition phase is complete. The next controlled phase is UE 5.8
inspection and selective migration:

1. Inspect the exact candidates in `OldTown_ResolvedPlacementPlan_v1.json`.
2. Record Unreal bounds, pivots, material slots, dependencies, collision and
   Nanite state.
3. Import/migrate only accepted selections into the map-development worktree.
4. Resolve final production paths in `OldTown_AssetPathRegistry_v1.json`.
5. Run contact-sheet, collision and connected-slice review before the full
   automated placement pass.

## Deferred substitutions

The two paid tarp listings must remain deferred unless separately approved. The Old Town plan can proceed without them by using a map-owned simple shade-cloth mesh with an approved Quixel fabric material, or by selecting a different verified-free Quixel cloth listing during the download/staging pass.
