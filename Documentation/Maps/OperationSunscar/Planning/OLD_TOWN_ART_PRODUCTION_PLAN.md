# Operation Sunscar — Old Town Art Production Plan

Status: planning only
Planning date: 2026-07-24
Target engine: Unreal Engine 5.8
Playable level: `/Game/Maps/Blockout/Lvl_Blockout_01`
Current focus: Old Town only

## 1. Purpose

This plan turns the verified Old Town gameplay graybox into a first complete,
viewable environment-art draft while preserving its tested movement, routes,
cover, objective flow, and collision.

Unreal development is paused while movement work is active. Nothing in this
planning package requires opening Unreal or modifying the TacticalMovement
repository.

The next environment-art session should be an execution session, not a design
session. Asset sourcing, visual roles, placement rules, performance guardrails,
folder structure, and exit tests are defined here in advance.

## 2. Scope freeze

### Included in the first Old Town art round

- The approximately 320 × 250 m Old Town combat core.
- The existing 335-actor playable graybox.
- The three tested routes:
  - Alpha — Dry Canal.
  - Bravo — Courtyard.
  - Charlie — Bazaar.
- The 20 macro sites recorded in the blockout manifest.
- Readable exterior architecture for every combat-facing building.
- Art treatment for the most important playable interiors.
- Landmark silhouettes, street surfaces, limited vegetation, props, decals,
  lighting, atmosphere, and a first optimization pass.
- Static vehicle cover.
- Temporary labels retained as a toggleable review layer.

### Deferred

- Art production for the six outer districts.
- Civilian crowds and AI population.
- Driveable vehicles.
- Destruction systems beyond visually prepared breach points.
- Final objective scripting.
- Final shipping optimization and full-map HLODs.
- Bespoke modeling, sculpting, or texturing unless the Epic-only library proves
  incapable of solving a verified gameplay need.

## 3. Non-negotiable gameplay rules

1. The graybox remains the source of truth for collision and playable space
   until each art replacement passes a side-by-side traversal test.
2. Art may skin, cap, trim, or selectively replace graybox geometry. It may not
   casually change door positions, stairs, cover heights, roof access, or route
   widths.
3. Primary doors and windows must remain visually obvious under gameplay
   lighting.
4. No new prop may narrow a combat alley below its verified clearance.
5. No decorative roof element may create an unintended new firing position.
6. No elevated location may gain control over more than two major combat
   spaces.
7. Foliage and cloth may provide concealment, but may not become unplanned hard
   cover.
8. Temporary review labels remain hideable and are never baked into production
   art.

## 4. Visual direction

Sunscar is a fictional settlement influenced by the Kaka–Abiverd region of
southern Turkmenistan. Old Town should read as a layered Central Asian frontier
town rather than a generic Middle Eastern ruin or a pristine historic site.

### Architectural layers

| Layer | Visual language | Where it appears |
| --- | --- | --- |
| Historic fabric | Eroded earthen masonry, stone foundations, shallow arches, patched plaster | Old walls, north gate, courtyard, selected landmark bases |
| Soviet civic layer | Squared plaster and brick masses, practical balconies, concrete stairs, painted metal | Hotel, clinic, detention, telecom, checkpoint |
| Residential layer | Timber doors and frames, enclosed yards, restrained carved details, patched roofs | Tea House, consulate, side alleys |
| Trade layer | Corrugated sheet, canvas shade, wood counters, crates, hand-painted signs | Bazaar and salvage edge |
| Utility layer | Concrete channels, pipework, electrical boxes, steel tanks, tires, fencing | Pump station, substation, motor pool, dry canal |
| Conflict layer | Sandbags, barriers, wire, checkpoint cover, impact damage | Detention, checkpoints, insertions and limited fortified positions |

### Palette

| Role | Color direction |
| --- | --- |
| Dominant walls | Dusty tan, muted ochre, warm gray plaster |
| Historic stone | Pale sandstone with darker eroded cuts |
| Civic accents | Faded turquoise, desaturated green, chalk white |
| Utility metal | Oxidized gray, rust brown, sun-bleached paint |
| Timber | Dark weathered brown |
| Route readability | Warm northern route, pale civic center, cooler industrial south |
| Foliage | Sparse gray-green and straw, never lush |

### Material ratio

- 55% plaster, adobe, and dusty brick.
- 15% stone foundations and historic fragments.
- 12% concrete and canal surfaces.
- 10% metal, corrugated sheet, fences, and utility parts.
- 5% wood, canvas, and market materials.
- 3% vegetation and loose organic material.

The ratios are composition targets, not material-instance counts.

## 5. Official-source policy

The first round uses only content whose Fab publisher is visibly:

- `Epic Games`
- `Quixel Megascans`

An asset being sold on Fab does not make it Epic-provided. Publisher identity
must be checked on every listing before acquisition.

Approved source families:

1. Quixel Megascans surfaces, decals, rocks, rubble, vegetation and scans.
2. Military Trench Megascans Sample for defensive props.
3. Historic Desert Ruin assets for selective historic architecture.
4. Historic Pakistan Street and Residential South Asian assets for restrained
   doors, windows, arches and masonry detail.
5. Urban Shanty Town and Urban Miscellaneous for the bazaar, salvage yard and
   utility dressing.
6. City Sample Vehicles for static vehicle cover.
7. Electric Dreams only as a reference for PCG construction patterns.

Current official references:

- Quixel Megascans:
  <https://www.fab.com/sellers/Quixel%20Megascans/about>
- Military Trench Megascans Sample:
  <https://www.fab.com/listings/f18c343f-b771-47b0-a02a-129771fd9804>
- Historic Desert Ruin search:
  <https://www.fab.com/sellers/Quixel%20Megascans?q=relic>
- Urban Megascans search:
  <https://www.fab.com/sellers/Quixel%20Megascans?q=urban>
- City Sample Vehicles:
  <https://www.fab.com/listings/2909157b-ddfa-4cef-a925-69dc2467021f>
- Electric Dreams Environment:
  <https://www.fab.com/listings/d79688f5-29be-4fb2-a650-2d4a813f5306>

Pricing and account entitlements must be checked while signed in. A search
result or price recorded during planning is not authorization to purchase.

## 6. Procurement target

The initial usable library should contain approximately 35–50 selected source
assets, not entire sample projects.

| Category | Unique source-asset target | Notes |
| --- | ---: | --- |
| Tiling surfaces | 8–10 | Walls, ground, concrete, brick, roof |
| Modular architecture | 8–12 | Walls, arches, stairs, frames, parapets |
| Landmark pieces | 4–6 | Tower, dome, carved arch, large ruin fragments |
| Defensive props | 5–7 | Sandbags, barriers, stakes, corrugated cover |
| Utility/industrial props | 6–10 | Boxes, pipes, lamps, tires, fencing, tanks |
| Bazaar/residential props | 6–10 | Doors, windows, crates, planks, stalls |
| Vehicles | 3–5 | Pickup, sedan/SUV, van or small truck |
| Natural dressing | 5–8 | Rocks, rubble, weeds and dry debris |

The acquisition ledger is:

`Planning/OLD_TOWN_ASSET_CATALOG.csv`

## 7. Old Town zone treatment

### Zone A — Detention and north compound

Includes:

- Detention Annex.
- Municipal Hotel north face.
- North Defender Insertion.
- North perimeter and gate approaches.

Treatment:

- More fortified and institutional than the rest of town.
- Plaster-over-brick civic structures with concrete stairs and parapets.
- Sandbags and barriers concentrated at entrances, not distributed everywhere.
- Historic wall fragments limited to the perimeter and older foundations.
- A faded turquoise or gray-green identification accent.

Asset families:

- Historic Desert Ruin wall and arch modules.
- Military Trench sandbags and barriers.
- Historic Pakistan Street damaged masonry.
- Urban utility boxes and lamps.

### Zone B — Civic center

Includes:

- Municipal Hotel.
- Old Clinic.
- Transit Plaza.
- Central Courtyard.

Treatment:

- The clearest and most legible part of the town.
- Restrained civic plaster, repaired concrete, tiled thresholds and balconies.
- The Hotel receives the strongest non-industrial silhouette after the water
  tower.
- Plaza and courtyard stay visually open; props gather at edges.
- Damage decals reveal age without turning the area into total ruins.

Asset families:

- Historic Pakistan Street walls, windows, doors and arches.
- Rough plaster, concrete and dusty brick surfaces.
- Limited Residential South Asian wood frames.
- Quixel rubble and surface decals.

### Zone C — Water tower and residential east

Includes:

- Water Tower Compound.
- Consulate Residence.
- Checkpoint Office.

Treatment:

- Enclosed compounds with cleaner walls than the bazaar.
- The water tower remains the primary navigation landmark.
- Residential wood and shallow ornamental detail stay concentrated at the
  consulate.
- The checkpoint uses practical steel and concrete, not medieval stone.

Asset families:

- Residential South Asian doors and windows.
- Urban Miscellaneous gates, lamps and utility props.
- Historic Desert Ruin stone only at wall bases.
- Military Trench barriers at the checkpoint.

### Zone D — Tea House and courtyard edge

Includes:

- Tea House.
- Central Courtyard edge structures.
- Connecting alleys.

Treatment:

- Warmest and most human-scaled sub-area.
- Timber frames, worn plaster, fabric shade, benches and small domestic props.
- Decorative detail is localized so the district does not become culturally
  incoherent.
- Maintain simple, high-contrast combat doorways.

Asset families:

- Residential South Asian frames, doors and limited furniture.
- Historic Pakistan Street arches and plaster.
- Urban Shanty Town fabric and patched materials.

### Zone E — Bazaar and southwest trade quarter

Includes:

- Covered Bazaar.
- Telecom Workshop.
- Southwest entry and checkpoints.

Treatment:

- Dense overhead rhythm without blocking the verified route.
- Corrugated sheet, canvas, shutters, wood counters, crates and hanging details.
- Strong sun/shade transitions.
- Reuse modular stall assemblies with controlled variation.
- Keep low clutter away from player foot placement.

Asset families:

- Urban Shanty Town sheet metal and patched construction.
- Urban Miscellaneous planks, crates, lamps and windows.
- Military Trench corrugated and wood elements where visually neutral.
- Quixel decals for grime, faded paint and repairs.

### Zone F — Salvage and motor-pool south

Includes:

- Salvage Yard.
- Motor Pool.
- Freight Depot.
- Power Substation.

Treatment:

- Most industrial and visually busy sub-area.
- Vehicle shells and large machinery provide deliberate hard cover.
- Tires, cable, sheet metal, pallets and utility components provide dressing.
- Repetition is acceptable if rotations, clustering and material accents vary.
- Do not import City Sample driving systems for the first round.

Asset families:

- City Sample Vehicles migrated as selected static art dependencies only.
- Urban Miscellaneous and industrial Quixel props.
- Shanty Town corrugated sheet and patched fencing.
- Concrete, dirt and faded asphalt surfaces.

### Zone G — Dry canal and pump infrastructure

Includes:

- Dry Canal Entrance.
- Canal Pump Station.
- Canal/culvert route edge.

Treatment:

- Pale concrete channel with accumulated silt, cracks and isolated weeds.
- Pipework and pump details identify the route without filling it.
- Culverts remain exposed and tactically readable.
- Water assets are not required for the first draft.

Asset families:

- Worn concrete and packed-silt surfaces.
- Urban Miscellaneous drains, pipes and utility boxes.
- Quixel rocks, rubble, dry weeds and litter.

## 8. Macro-site art mapping

| ID | Site | First-round treatment | Priority |
| --- | --- | --- | --- |
| SS_001 | Attacker Spawn and Extraction | Sparse road edge, faded markings, barrier cluster | P1 |
| SS_002 | Dry Canal Entrance | Concrete/silt skin, culvert trim, sparse rubble | P0 |
| SS_003 | Canal Pump Station | Utility skin, pipes, electrical boxes, steel door | P1 |
| SS_004 | Tea House | Warm plaster, wood frames, fabric shade, seating edge | P0 |
| SS_005 | Old Clinic | Civic plaster, damaged brick reveals, clean entry | P1 |
| SS_006 | Water Tower Compound | Hero tower treatment, ladder/platform readability | P0 |
| SS_007 | Municipal Hotel | Hero civic facade, balcony/parapet language | P0 |
| SS_008 | Central Courtyard | Stone/dirt surface blend, edge props, central focus | P0 |
| SS_009 | Transit Plaza | Concrete/paver variation, light street dressing | P1 |
| SS_010 | Detention Annex | Fortified civic skin, historic perimeter, barriers | P0 |
| SS_011 | Checkpoint Office | Concrete/metal skin, barrier and lamp set | P1 |
| SS_012 | Consulate Residence | Cleaner plaster, wood door/window accents | P1 |
| SS_013 | Freight Depot | Brick/metal warehouse skin, loading clutter | P1 |
| SS_014 | Salvage Yard | Corrugated fence, tires, vehicle shells, scrap clusters | P0 |
| SS_015 | Motor Pool | Utility facade, parked pickup/van, repair props | P0 |
| SS_016 | Power Substation | Fence, boxes, poles, concrete pad, warning details | P1 |
| SS_017 | Covered Bazaar | Modular stalls, shade, shutters, crates | P0 |
| SS_018 | Telecom Workshop | Civic/industrial hybrid, roof equipment | P1 |
| SS_019 | South Defender Insertion | Industrial edge, road barrier, sparse props | P1 |
| SS_020 | North Defender Insertion | Fortified edge, wall fragments, sandbags | P1 |

`P0` sites form the first visual review slice. `P1` completes Old Town after
the P0 look is approved.

## 9. Construction methods

Every graybox element will be assigned one of four treatment modes:

| Mode | Meaning | Typical use |
| --- | --- | --- |
| Skin | Preserve graybox collision and cover it with materials or thin art meshes | Most walls, floors and roofs |
| Cap | Preserve the block and add parapets, trims, doors, frames or roof detail | Buildings and compounds |
| Replace | Swap visible graybox with art mesh while retaining a hidden collision shell until tested | Hero arches, selected stairs, tower pieces |
| Dress | Add non-structural props, decals, rubble or vegetation | Streets, courtyards, interiors |

This division is stored in:

`Planning/OldTown_ArtPlacementManifest_v1.json`

## 10. Unreal content layout for the later execution session

No folders are to be created until Unreal work resumes.

Planned destination:

```text
/Game/Maps/Sunscar/
  Art/
    Epic/
      Architecture/
      Materials/
      Props/
      Vehicles/
      Natural/
      Decals/
    Assemblies/
      Civic/
      Bazaar/
      Industrial/
      Residential/
      Defensive/
    PCG/
    Lighting/
  Data/
    ArtPlacement/
  Debug/
```

Selected source content should first enter a temporary UE 5.8 staging project.
Only reviewed assets and their required dependencies are migrated into
TacticalMovement.

Do not migrate:

- Complete City Sample or Electric Dreams projects.
- City Sample driving, traffic, crowd, Mass AI, Chaos, or gameplay systems.
- Demo maps, cinematic sequences, documentation maps or unused variants.
- Unselected 8K textures merely because a source project contains them.

## 11. Material strategy

The first draft should reuse a small family of parent materials:

1. Opaque building surface.
2. Opaque ground surface.
3. Opaque prop surface.
4. Masked foliage/cloth material.
5. Decal material.
6. Glass material used only where gameplay readability requires it.

Quixel materials may arrive with their own masters. During the staging audit,
identify which can remain intact and which should be normalized into map-owned
instances. Avoid duplicating identical texture sets under multiple names.

Texture guidance:

- 4K is permitted for hero surfaces and large scans.
- 2K is the default for repeated props and ordinary surfaces.
- 1K is adequate for minor clutter, small masks and distant elements.
- 8K source textures require an explicit visual justification.
- Packed masks and virtual textures should be preserved when supplied and
  compatible.

## 12. Nanite policy

Enable Nanite for:

- High-detail Quixel rock and rubble meshes.
- Historic ruin scans and dense masonry modules.
- High-detail static vehicle exteriors when compatible.
- Repeated dense opaque or masked static geometry that benefits from it.
- Large occluding architecture meshes.

Do not enable it automatically for:

- Simple graybox collision shells.
- Tiny low-poly props.
- Transparent glass.
- Cloth requiring unsupported deformation.
- Any mesh whose material or gameplay behavior is incompatible.

Collision remains intentionally simpler than render geometry. Nanite is a
rendering choice, not permission to use scan meshes as player collision.

Epic's UE 5.8 Nanite guidance:

<https://dev.epicgames.com/documentation/en-us/unreal-engine/nanite-virtualized-geometry-in-unreal-engine>

## 13. PCG policy

Manual placement:

- Cover.
- Door and window frames.
- Route-defining rubble.
- Vehicles.
- Landmark elements.
- Props affecting line of sight.
- Any object close enough to affect movement.

PCG or instanced placement:

- Small rubble.
- Dry weeds.
- Minor litter.
- Repeated wall-edge debris.
- Non-gameplay roof clutter.
- Surface decals where deterministic projection is verified.

PCG output must be deterministic, seeded, organized by zone, and manually
editable. Gameplay exclusion volumes protect routes, doors, stairs, objectives,
spawn space and traversal edges.

## 14. First-draft performance guardrails

These are planning guardrails, not final shipping budgets:

| Measure | First-round target |
| --- | --- |
| Old Town source-asset library | 35–50 selected assets |
| Old Town resident editor RAM | Aim below 12–16 GB with only its cells loaded |
| Unique surface families | 8–10 |
| Simultaneous local shadowed lights | 4 or fewer in a combat view |
| Small procedural dressing instances | Approximately 250–500 |
| Hero 4K texture sets | 12 or fewer before profiling |
| Unjustified 8K texture sets | 0 |
| Driveable vehicle systems | 0 |
| Imported sample-project maps | 0 |

The actual acceptance test is measured performance on the target hardware. A
visual feature that causes large memory or frame-time spikes is reduced before
expanding beyond Old Town.

## 15. Execution sequence after movement work pauses

### Phase 0 — Safety and baseline

1. Verify the correct map worktree, branch and clean scope.
2. Confirm movement work is stopped and no Unreal process is running.
3. Open only the map-development project.
4. Load only Old Town World Partition cells.
5. Record baseline memory, frame timing and screenshots.

### Phase 1 — Staging and acquisition

1. Create or reuse a temporary UE 5.8 staging project.
2. Verify publisher, price, license and engine compatibility for each candidate.
3. Acquire free approved packs first.
4. Inspect source assets and mark exact selected meshes/materials in the ledger.
5. Migrate only the selected assets and dependencies.
6. Stop on unexpected plugins, source code, excessive dependencies or very
   large packages.

### Phase 2 — Look-development slice

Complete these P0 sites first:

1. Central Courtyard.
2. Municipal Hotel exterior.
3. Water Tower Compound.
4. Covered Bazaar street edge.
5. A short Dry Canal section.

This single slice must prove:

- The material palette.
- Civic, residential, trade and infrastructure styles.
- Door and route readability.
- Nanite and texture policy.
- Lighting and atmosphere.
- Memory cost.

Do not dress the rest of town until the slice passes review.

### Phase 3 — Structural skin

1. Apply the approved surface families across Old Town.
2. Cap roofs, parapets, doors and windows.
3. Add selected historic wall and arch pieces.
4. Preserve hidden graybox collision for replaced hero pieces.
5. Test all three routes after structural work.

### Phase 4 — Landmark completion

1. Detention Annex.
2. Municipal Hotel.
3. Water Tower.
4. Covered Bazaar.
5. Salvage Yard.
6. Motor Pool.

Each receives a unique silhouette, one readable accent color and one concise
player callout.

### Phase 5 — Zone dressing

1. Defensive north.
2. Civic center.
3. Residential east.
4. Tea House edge.
5. Bazaar southwest.
6. Industrial south.
7. Dry canal.

Manual tactical dressing comes before PCG decoration.

### Phase 6 — Procedural pass

1. Build exclusion volumes.
2. Scatter low-risk rubble, weeds and debris.
3. Review every route at walking eye height.
4. Convert suitable repeated clusters to instances.
5. Bake or lock deterministic output for the checkpoint.

### Phase 7 — Lighting, atmosphere and final review

1. Establish one clear time-of-day target.
2. Tune sun, sky and exposure before local lights.
3. Add restrained dust and atmospheric depth.
4. Capture labeled and clean overhead images.
5. Capture street-level images from each route and landmark.
6. Run traversal, sightline, collision, memory and frame-time checks.

## 16. Definition of the first complete Old Town round

The first round is complete when:

- Every visible graybox surface in the Old Town review area has intentional art
  treatment or is deliberately retained.
- All six major landmarks are visually distinct.
- The three routes remain traversable and readable.
- Critical doors, stairs, ladders, cover and roof positions still match the
  tested layout.
- The P0 and P1 macro sites have the treatments defined in this plan.
- No unapproved third-party content exists in the migrated map library.
- No full sample project or unrelated gameplay system has entered the main
  project.
- Old Town can be loaded and reviewed without the previous 40 GB editor-memory
  behavior.
- A clean and labeled overhead export plus route-level screenshots exist.
- The exact asset list, source publishers, licenses and migrated dependencies
  are recorded.
- Git scope contains only intentional map art, map-local automation and updated
  map documentation.

## 17. Decisions already made

- Old Town is the only current environment-art focus.
- The verified graybox is preserved.
- Pre-existing Epic Games and Quixel Megascans content is preferred.
- Random third-party Fab providers are excluded from the first round.
- Unreal is not opened while movement development is active.
- Asset acquisition occurs through a staging project.
- Nanite is used selectively on suitable art geometry.
- PCG handles low-risk repetition, not tactical design.
- Art approval begins with a representative P0 slice.

## 18. Provisional production decisions

The following defaults prevent these questions from blocking the asset plan.
They can be changed before Unreal work resumes:

1. **Daylight:** clear late-morning desert light with a moderately high sun.
   Shadows remain useful for depth but do not swallow alleys or entrances.
2. **Damage:** recently contested, not destroyed. Most buildings remain
   structurally intact; approximately 15–20% of visible facades receive
   concentrated damage or emergency repair.
3. **Acquisition:** build a complete zero-spend option first. Paid Quixel items
   form a separate optional upgrade list and are never purchased without
   approval.
4. **Performance:** use 1440p/60 fps as the provisional gameplay target, then
   replace it with a hardware-specific target when the intended minimum PC
   class is known.
5. **Interiors:** complete exteriors across Old Town and fully art-treat only
   the critical playable interior set:
   - Detention entry and objective spaces.
   - Municipal Hotel ground floor and one combat-relevant upper area.
   - Tea House playable room.
   - Covered Bazaar playable passage.
   Other interiors receive readable thresholds and a restrained first-pass
   treatment without dense furnishing.
