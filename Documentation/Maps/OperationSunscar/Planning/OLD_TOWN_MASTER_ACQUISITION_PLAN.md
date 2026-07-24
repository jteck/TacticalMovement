# Operation Sunscar — Old Town Master Acquisition Plan

Snapshot: 2026-07-24
Scope: first complete Old Town art draft
Approved publishers: Epic Games and Quixel Megascans
Unreal status: closed and untouched
Purchases or library additions made: none

## Executive decision

The first complete visual draft can be built with a required paid budget of:

`$0.00 before tax`

The plan selects 37 free official sources. Ten paid listings remain deferred
upgrades with a combined regular public-price snapshot of:

`$33.90 before tax`

No paid item should be approved until the free source or map-owned replacement
is seen in the later Unreal staging pass.

The machine-readable acquisition order is in
`OLD_TOWN_MASTER_ACQUISITION_PLAN.csv`. Exact site use is in
`OLD_TOWN_EXACT_SITE_ASSIGNMENTS.csv`.

## What is acquired and what is built

### Official source content

Epic and Quixel provide:

- Three source packs: Military Trench Sample, City Sample Vehicles and
  Junkyard.
- Sandbags, corrugated sheet, doors, electrical equipment, barrels and small
  furniture.
- Plaster, stucco, concrete, asphalt, tarp and shutter surfaces.
- Damage, rubble, rock, grass and road-edge debris.
- Secondary water-tank and utility details.

### Map-owned modular geometry

The project builds simple geometry where exact control matters:

- Existing building shells and parapets.
- Window frames, shutters and glass at verified openings.
- Door collision and interaction shells.
- Bazaar stalls, canopy planes, poles and beams.
- Pipes, conduit, roof vent boxes and antenna silhouettes.
- Large water tower, 5–7 m primary tank, platform and ladder.
- Fences, gates, spawn barriers, signs and objective markings.

These pieces are not custom sculpted art. They are low-complexity modular
geometry dressed with the selected official materials.

## Acquisition and staging order

1. Add the three free source packs to the Epic/Fab library.
2. Add the individual free Quixel listings in CSV order.
3. Create a separate UE 5.8 staging project.
4. Import or add each source only to staging.
5. Record real Unreal asset paths, bounds, pivots, material count and disk size.
6. Select only the exact sub-assets named by the site ledger.
7. Migrate the selected dependencies into
   `/Game/Maps/Sunscar/Art/...`.
8. Build and validate map-owned modular geometry.
9. Apply materials, then props, then tactical collision.
10. Review visuals and performance before considering paid upgrades.

The complete City Sample, Junkyard sample scene and Military Trench sample map
must never be migrated into TacticalMovement.

## First visual slice

The fastest proof is one connected loop containing:

- Municipal Hotel.
- Central Courtyard.
- Tea House.
- Covered Bazaar.
- The approach toward Detention Annex.

This slice exercises the plaster family, doors/windows, shade, domestic props,
historic accents and combat readability before industrial sites consume time.

## Paid-upgrade gates

| Upgrade | Price snapshot | Approval condition |
| --- | ---: | --- |
| South Asian hero door | $2.99 | Free door looks culturally wrong at Tea House |
| Coarse ruin sand | $0.99 | Free ground blend cannot produce canal/courtyard silt |
| Pakistan white brick | $0.99 | Facades lack a convincing exposed-masonry layer |
| Ruin wall set | $2.99 | Map-owned historic edge lacks sufficient silhouette |
| Carved ruin arch | $2.99 | Detention socket fits and the arch improves landmarking |
| Full-height corrugated panel | $4.99 | Free panel plus Junkyard cannot produce clean 2–2.6 m fences |
| Medium slatted crate | $4.99 | Junkyard has no suitable stackable freight crate |
| Long scaffold plank | $4.99 | Junkyard has no safe shade/repair beam |
| Weathered drainpipe | $4.99 | Map-owned pipe fails close-view quality |
| Rusted roof vent | $2.99 | Roof silhouettes remain weak after map-owned vent pass |

The weathered paid window is not in the upgrade budget because its dimensions
are unverified. It remains blocked, not merely deferred.

## Scale and gameplay rules

- Imported static art targets real-world scale with no routine scale correction
  beyond approximately ±10 percent.
- Structural openings always obey the graybox dimensions.
- Art never narrows a verified route or creates a new climb chain.
- Large rocks, cabinets, barrels, vehicles and scrap receive manual placement
  and simple tactical collision.
- Small debris, decals and foliage receive no collision.
- Dense scans are provisional Nanite candidates; tiny props and materials do
  not need Nanite.
- Runtime source textures default to 2K unless a hero asset demonstrates a
  visible need for 4K.

## Planning completeness

Old Town now has:

- Fixed site centers, footprints, heights and density targets.
- A structural and opening recipe for all 20 sites.
- Exact official source listings with price and dimension evidence.
- A deduplicated acquisition order.
- Exact source-record assignments and quantity rules for every site.
- Defined map-owned replacements where the catalog fit is weak.
- Paid-upgrade gates rather than speculative purchases.

The remaining work is execution and in-engine measurement, not broad asset
research.
