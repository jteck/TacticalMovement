# Operation Sunscar — Exact Fab Shortlist, P1A

Research snapshot: 2026-07-24
Scope: Old Town utilities, salvage and natural dressing
Unreal status: not opened
Purchases made: none

## 1. Result

The second exact-source pass adds 22 official Quixel Megascans listings:

| Decision | Count |
| --- | ---: |
| Essential or useful free sources | 14 |
| Optional paid upgrade | 1 |
| Paid listings rejected because free alternatives exist or the fit is wrong | 4 |
| Held for later or pending a demonstrated need | 2 |
| Rejected for scale/style | 1 |

Detailed evidence:

`Planning/OLD_TOWN_EXACT_FAB_SHORTLIST_P1A.csv`

## 2. Main procurement conclusion

No paid purchase is currently necessary for this batch.

The only retained paid option is Urban Miscellaneous Pipe Drain Metal
Weathered at a public price snapshot of $4.99. It is dimensionally useful at
2.44 m long, but a simple map-owned pipe mesh with an official Quixel metal
material can solve the first draft at zero cost.

The paid electrical boxes, lamp and tire cluster are rejected for the first
round because:

- Three useful Quixel electrical assets are currently listed free.
- The paid lamp is only 1.70 m on its long dimension and does not fill the
  planned 4–7 m street-pole role.
- The free Quixel Junkyard pack should supply tire and scrap alternatives.

## 3. High-value free official sources

### Quixel Junkyard

The free Junkyard pack contains 96 assets and is the preferred source for:

- Salvage Yard scrap.
- Motor Pool clutter.
- Freight Depot industrial dressing.
- Tires, rims, vehicle fragments and discarded equipment.
- Corrugated and dilapidated structures where appropriate.

The listing's Unreal scene supports versions through 5.6 rather than explicitly
listing 5.8. The source also includes FBX. The safe plan is to inspect and
migrate only selected raw assets or test them in the later UE 5.8 staging
project. The complete example scene will not enter TacticalMovement.

### Electrical set

Three free Quixel assets cover different scales:

| Asset | Listed dimensions | Role |
| --- | --- | --- |
| Electrical Box | 0.43 × 0.38 × 0.26 m | Small wall fixture |
| Electric Box | 0.24 × 1.02 × 0.98 m | Medium enclosure |
| Electrical Cabinet | 0.87 × 2.62 × 1.39 m | Large pump/substation cabinet |

The large cabinet is manually placed because its dimensions can affect cover
and movement.

### Natural dressing set

The free set now includes:

- Military Trenches Ground Patch Rock S 04.
- Military Trenches Debris Patch Rock Corner.
- Sandstone Rocky Ground.
- Desert Western Rock Medium 08.
- Dry Grass.
- Dried Grass surface.
- Desert Debris atlas.

This covers the planned small rubble, wall-edge debris, sparse grass and
perimeter rock requirements without buying another environment pack.

## 4. Exact placement decisions

### Canal and Pump Station

- Round Drain Cover: no-collision ground detail.
- Electrical Box and Electric Box: wall-mounted.
- Electrical Cabinet: one manual equipment anchor.
- Ground Patch Rock and Debris Corner: edge-only dressing.
- Optional pipe: map-owned geometry first; paid Quixel pipe only if the free
  version looks inadequate.

### Salvage Yard

- Quixel Junkyard pack supplies the main scrap library.
- City Sample contributes selected whole static vehicles.
- Rusty Metal Barrel supplies deliberate waist-high industrial props.
- Desert Debris and small rock patches provide low-risk ground breakup.
- The paid race-track tire cluster is rejected until the Junkyard pack proves
  insufficient.

### Motor Pool

- One pickup and one van or SUV from City Sample.
- Selected Junkyard repair parts.
- Rusty Metal Barrel.
- Small and medium electrical enclosures.
- Old Shovel as one restrained storytelling detail.

### Power Substation

- One large Electrical Cabinet.
- Two to four small/medium electrical boxes.
- Round Drain Cover and map-owned conduit/pipe geometry.
- Existing verified fencing remains the structural source.
- Modular Metal Guardrail remains held for the canal or service-road edge.

### Historic and residential edges

- Military rubble corner patches.
- Dry Grass meshes with deterministic PCG.
- Dried Grass material beneath sparse tufts.
- Sandstone Rocky Ground and Desert Western Rock are manual perimeter pieces,
  not street scatter.

## 5. Vehicle role selection

The City Sample Vehicles listing confirms the following relevant categories:

- Pickup.
- SUV.
- Sedan.
- Delivery van.
- Semi and other large vehicles.

Planned P0/P1 selection:

| Vehicle role | Site | Quantity | Decision |
| --- | --- | ---: | --- |
| Pickup | Motor Pool | 1 | Required |
| Delivery van or practical SUV | Motor Pool/Freight edge | 1 | Required |
| Weathered sedan or SUV | Salvage Yard | 1–2 | Required |
| Additional damaged/static shell | Salvage Yard | 1 | Optional |
| Bus, semi, garbage truck and sports car | None in Old Town first round | 0 | Reject |

The exact internal mesh names and bounds are not published on the listing. They
remain a later staging-project measurement, but their roles and quantity are
now fixed.

## 6. Nanite and collision

- Dense rocks and debris scans: provisional Nanite, normally no collision.
- Medium 0.82 m rock: Nanite with simple collision if it skins verified cover.
- Electrical props: Nanite optional; simple collision only when reachable.
- Dry Grass: compare masked Nanite against traditional foliage during staging.
- Barrel: simple cylinder collision because it can behave as cover.
- Small shovel and minor debris: no collision; Nanite unnecessary.
- Junkyard pack: decide per selected mesh after inspection.

## 7. Cost effect

P0 paid candidates before this batch:

`$31.90 before tax`

New required paid cost from P1A:

`$0.00`

Optional pipe upgrade:

`$4.99 before tax`

The free Junkyard and electrical sources may also eliminate some previously
optional paid crate, tire and utility purchases after visual comparison.

## 8. Next research batch

The remaining exact web-only planning work is:

1. Plain civic doors and window alternatives.
2. Bazaar shade/canvas and signage solutions.
3. Roof equipment and small residential props.
4. Additional surface-material variants with a free-first bias.
5. A consolidated master acquisition list with duplicates removed.
6. A site-by-site source-ID assignment replacing broad catalog families with
   exact Fab record IDs.
