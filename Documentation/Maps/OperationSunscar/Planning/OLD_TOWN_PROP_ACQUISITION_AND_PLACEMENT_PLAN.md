# Old Town Prop Acquisition and Placement Plan

Date: 2026-07-26  
Scope: planning only; no Unreal Editor changes  
Target level: `/Game/Maps/Blockout/Lvl_Blockout_01`

## Outcome

Old Town now has a first-round budget of **2,350 placed environment instances** across its 20 sites. This is a production target, not a promise that every instance survives playtesting. The budget deliberately includes architecture caps, tactical objects, utilities, furniture, industrial scrap, decals, rubble, and vegetation so acquisition and import can be completed in controlled batches.

The plan uses:

1. map-owned modular pieces for gameplay-critical structure and exact opening sizes;
2. free Epic Games and Quixel Megascans sources already selected;
3. selected internal meshes from the free Military Trench, Junkyard, and City Sample Vehicles packs;
4. paid Quixel items only as deferred upgrades requiring separate approval.

No unknown third-party publisher is required for the first complete Old Town draft.

## Evidence labels

- **Verified fact:** the listing, dimensions, or current project condition was directly checked.
- **Documented behavior:** Epic or Fab documentation states the behavior.
- **Inference:** a reasonable production assumption that still needs staging confirmation.
- **Unknown:** information that cannot be known until the pack is downloaded or the asset is inspected.
- **Recommendation:** the planned implementation choice.

## What is fixed now

- **Verified fact:** all 20 site centers, footprints, heights, tactical constraints, and broad dressing recipes are recorded in `OLD_TOWN_SITE_RECIPES.csv`.
- **Verified fact:** the stand-alone Quixel scan listings in the existing P0/P1 shortlists have listing IDs, public dimensions, publisher, format, and preliminary Nanite/collision decisions.
- **Verified fact:** Military Trench Megascans Sample, City Sample Vehicles, and Junkyard were live and free on Fab on 2026-07-26.
- **Verified fact:** Military Trench describes logs, sandbags, planks, earthworks, and barbed wire. City Sample Vehicles contains 13 vehicle types. Junkyard contains 96 assets and supplies FBX files.
- **Recommendation:** acquire only the official listings in the import batches; mine only the planned subset from the three large packs.
- **Recommendation:** use the exact target counts in `OLD_TOWN_PROP_SITE_BUDGETS.csv` for the first automated placement pass.
- **Recommendation:** use deterministic seeds and exclusion rules from `OldTown_PropPlacementManifest_v1.json`.

## What cannot be truthfully fixed before staging

The following are intentionally recorded as staging gates rather than guessed:

- exact internal Unreal asset paths inside the three large packs;
- exact bounds and pivots for the selected Junkyard and City Sample meshes;
- which of several visually similar pack meshes becomes variant A, B, or C;
- final per-instance coordinates where a prop must conform to the finished terrain or a facade socket;
- final collision complexity, material dependencies, and Nanite suitability after import;
- whether an individual prop is removed because it harms movement, sightlines, readability, or performance.

These unknowns do **not** block acquisition. They create a short inspection task after each import batch. The target role, quantity, site, scale envelope, placement method, and fallback are already determined.

## Instance budget

| Class | Target | Placement strategy |
|---|---:|---|
| Architecture caps and modules | 566 | Manual/socket-driven; preserve graybox collision |
| Tactical cover and barriers | 178 | Manual only; retain approved cover topology |
| Utilities | 246 | Socket-driven/manual; no accidental climb chains |
| Furniture and market dressing | 118 | Manual clusters outside combat centerlines |
| Industrial scrap | 180 | Large pieces manual; small pieces deterministic scatter |
| Decals, signs, and markings | 338 | Deterministic facade/ground sockets |
| Rubble and ground breakup | 504 | PCG or scripted scatter with route exclusions |
| Sparse vegetation | 220 | Deterministic PCG with low density |
| **Total** | **2,350** | |

This is intentionally much larger than the current graybox dressing count. It is still a first-round budget: repetition is controlled by variants, rotation, scale windows, clustered placement, material instances, and site-specific palettes.

## Acquisition gates

### Gate A — no download required

Use the map-owned modular kit for walls, opening caps, doors, windows, parapets, bazaar stalls, shade frames, fences, gates, pipes, signs, water-tower assembly, and curbs. These pieces are sized to the verified graybox and are the gameplay-safe fallback.

### Gate B — free stand-alone Quixel listings

Acquire the exact free listings enumerated in `OLD_TOWN_MASTER_ACQUISITION_PLAN.csv`. These cover sandbags, corrugated panels, utilities, doors, tarps, furniture, surfaces, decals, rubble, rocks, vegetation, barrels, tools, and a secondary water tank.

### Gate C — free official packs

- Military Trench Megascans Sample: mine only defensive and construction variants required by the BOM.
- Junkyard: mine only tires, pallets/crates, scrap, barrels/tools, and selected industrial clutter.
- City Sample Vehicles: migrate static render meshes and required materials only. Do not migrate driving, traffic, Mass AI, or Chaos gameplay systems.

### Gate D — paid upgrades

Do not purchase automatically. Historic arch/wall pieces, hero door, tall corrugated sheet, large crate, long plank, drainpipe, and vent remain optional. The first round has map-owned or free fallbacks for all of them.

## Placement rules

1. Gameplay-critical cover, vehicles, gates, furniture near routes, and large rocks are manual placements.
2. Graybox collision remains authoritative until each replacement passes traversal and weapon-clearance checks.
3. PCG/scripted scatter may place only non-colliding small rubble, asphalt fragments, and sparse plants.
4. Every scatter group receives route, spawn, doorway, stair, ladder, objective, and mantle-edge exclusions.
5. No asset is scaled outside 0.90–1.10 unless its BOM row explicitly permits a different envelope.
6. Prop clusters use two to five variants before repeating a hero silhouette.
7. Damage is concentrated in authored zones rather than applied uniformly.
8. Roof props remain at least 1.5 m from climbable edges unless the blockout already supports the route.
9. Bazaar shade undersides stay at or above 2.5 m and the central passage remains fully readable.
10. Vehicle art is static and uses simple collision proxies.

## Automated first-pass workflow

1. Acquire and stage one import batch at a time.
2. Resolve the `staging_gate` rows in the BOM by recording real asset paths, bounds, pivots, material dependencies, collision, and Nanite status.
3. Create redirect-free destination folders under `/Game/Maps/OldTown/Art/`.
4. Run the architecture-cap pass.
5. Run manual tactical placement from the site budgets.
6. Run utility and furniture socket passes.
7. Run industrial-cluster placement.
8. Run decals, rubble, and vegetation last.
9. Perform route, spawn, sightline, collision, and performance validation.
10. Save only intentional Old Town assets and the level after scope review.

## Acceptance criteria for the first viewable draft

- all 20 sites have their assigned material language and landmark silhouette;
- all openings, stairs, ladders, gates, and three verified routes remain functional;
- no floating prop is accepted; each is terrain-, socket-, or facade-conformed;
- no small scatter mesh has gameplay collision;
- no tactical cover is added without a deliberate site assignment;
- Old Town reads as one coherent dry Central Asian settlement with civic, residential, trade, utility, and salvage subdistricts;
- a top-down review and a first-person movement pass both succeed before polish.

## Files produced by this planning pass

- `OLD_TOWN_PROP_MASTER_BOM.csv` — unique asset roles, exact sources, counts, and staging gates.
- `OLD_TOWN_PROP_SITE_BUDGETS.csv` — deterministic target count for every site and prop class.
- `OLD_TOWN_PROP_IMPORT_BATCHES.csv` — acquisition/import order and acceptance gates.
- `OLD_TOWN_PROP_SUPPLEMENTAL_EXACT_LISTINGS.csv` — exact official free listings added for rust, mud, and oil stains.
- `OldTown_PropPlacementManifest_v1.json` — machine-readable bounds, seeds, counts, and placement rules.

