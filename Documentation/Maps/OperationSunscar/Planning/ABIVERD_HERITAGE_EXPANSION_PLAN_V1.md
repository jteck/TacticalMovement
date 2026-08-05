# Abiverd Heritage Expansion Plan V1

Date: 2026-08-03
Status: Offline planning; four selected free Quixel sources acquired in Fab, with no Unreal project assets changed by this plan
Map: `/Game/Maps/Blockout/Lvl_Blockout_01`
Coordinate convention: east = positive X, north = positive Y, metres

## Purpose

Extend the north/northwest edge of Old Town with an Abiverd-influenced archaeological precinct, irrigated spring meadow, red field poppies, a ruined Juma mosque landmark, and dependable terrain/ruin cover. Vegetation supplements concealment and visual identity but is not treated as authoritative gameplay cover.

## Evidence classification

- Verified fact: Historical descriptions identify Abiverd as a fortified and irrigated North Khorasan trading city with productive agricultural land, bazaars, craft quarters, a central portal-domed mosque, fortified gates, and a defensive ditch.
- Verified fact: The surviving Abiverd mosque evidence is principally ruined masonry, including a brick portal; the supplied intact domed-building photograph is therefore regional architectural influence, not a literal reconstruction reference.
- Verified fact: Quixel Field Poppy and the selected Wild Grass are free Fab 3D plant listings published by Quixel Megascans.
- Documented behavior: UE 5.8 Static Mesh Foliage uses hardware instancing. Nanite supports masked materials and instanced foliage, but Nanite foliage does not use conventional foliage distance culling or per-instance fading.
- Recommendation: Use ordinary PCG only as an editor-time authoring tool, save the generated instances, and avoid runtime PCG generation for this competitive multiplayer map.
- Unknown until Unreal staging: Exact physical height, pivot, collision, material complexity, LOD quality, and practical instance cost of the selected Field Poppy and Wild Grass meshes.

## Initial spatial envelope

The coordinates below are an execution starting point and must be validated against the actual Landscape, North Defender Insertion, traversal, and sightline tests before final placement.

| Planning ID | Feature | Initial center | Initial envelope | Height | Function |
|---|---|---:|---:|---:|---|
| SS_021 | Juma Mosque Ruin | X 10, Y 165 | 18 x 16 m | 10-12 m | Heritage landmark, close combat anchor, navigation silhouette |
| SS_022 | Abiverd Ruins Field | X 5, Y 178 | 105 x 100 m | 0.4-4.5 m | Broken sightlines, archaeological identity, multiple traversal routes |
| SS_023 | Historic Well Court | X -20, Y 154 | 12 x 10 m | 1.0-2.4 m | Secondary landmark and hard-cover pocket |
| SS_024 | Fortification and Ditch | X -5, Y 218 | 90 x 12 m | 0.8-2.5 m | Northern sightline break and terrain-based cover |
| SS_025 | Poppy Meadow Network | X 5, Y 180 | Within SS_022 | Target 0.45-0.90 m after staging | Seasonal identity and non-authoritative concealment |

Protected constraints:

- Maintain at least 20 m of clear, reviewed space around North Defender Insertion.
- Do not create a protected firing position from the spawn toward Old Town.
- Preserve at least three readable routes through the heritage precinct.
- No route may depend on flowers or grass for protection from a standing sniper.
- Place dependable hard cover or terrain interruption every 15-20 m on exposed movement routes.

## Mosque construction recipe

Recommended footprint: 18 x 16 m.

- Structural shell: simple map-owned modular geometry with Nanite enabled after collision and silhouette validation.
- Primary exterior: Cracked Mud Wall material over large earthen wall areas.
- Exposed historic masonry: Historic Desert Ruin Wall Brick 03.
- Portal: one Historic Desert Ruin Arch Stone Carved 08, used as a sealed or partially blocked ceremonial portal rather than a gameplay-sized doorway.
- Small openings: four Historic Desert Ruin Structure Stone S 06 pieces.
- Foundations: four to six Historic Desert Ruin Wall Modular Set 04 pieces, partly buried.
- Repair/whitewash: Historic Pakistan Street Wall Brick White 01 on only 5-12 percent of the exterior.
- Dome: simple optimized shell, partially collapsed or visibly damaged; do not use the audited interior dome scans as an exterior dome.
- Interior: one main hall, one side chamber, one partially collapsed edge; avoid a maze of ornamental rooms in the first round.
- Gameplay openings: all traversable doors and windows remain clean map-owned geometry sized from the TacticalMovement character, not from decorative scans.

## Ruins-field recipe

- 25-35 total ruin remnants.
- 6-8 substantial wall groups providing real ballistic cover.
- 8-12 low wall/foundation groups providing partial crouched protection or traversal definition.
- 10-15 small collapsed fragments used only for silhouette and environmental storytelling.
- One well court and two shallow irrigation cuts.
- One broken fortification/ditch band at the northern edge.
- Ruin spacing should be irregular, generally 6-14 m, with intentionally open lanes retained between clusters.
- Avoid parallel walls that accidentally create uninterrupted head-glitch firing lanes.

## Landscape and vegetation recipe

Landscape surface composition inside the heritage envelope:

- 45-60 percent muted green meadow ground.
- 20-30 percent dry trampled soil along routes and inside ruins.
- 15-25 percent existing sandstone/arid ground on higher or exposed areas.
- 5-10 percent rocky debris and foundation transitions.

Vegetation distribution:

- Four to six irregular poppy belts, approximately 12-25 m long and 5-10 m deep.
- Do not cover the entire precinct uniformly.
- Use the selected Wild Grass as the main 3D filler and the already-owned Dry Grass on field edges, disturbed soil, ditch lips, and ruined interiors.
- Keep 1.5-2.0 m vegetation-clear margins around primary paths and gameplay openings.
- Keep 4-6 m vegetation-clear review zones around objectives and spawn protection areas.
- Use low-density poppies within Old Town itself; the strongest red-field identity belongs outside the dense street core.

## UE 5.8 implementation rules

- Generate vegetation in editor with a deterministic PCG graph and fixed seed.
- Save generated static-mesh instances; do not regenerate the meadow at runtime.
- Use Static Mesh Foliage or PCG Static Mesh Spawner output, not Actor Foliage.
- Disable collision, navigation influence, ticking, replication, and individual actor creation for poppies and grass.
- Use masked materials, not translucent materials.
- Begin with non-Nanite legacy Quixel plant meshes so Start/End Cull Distance, PerInstanceFadeAmount, and foliage density scaling remain usable.
- A/B profile Nanite only after the non-Nanite baseline is captured.
- Enable Nanite on high-detail ruin scans, major rocks, mosque geometry, and suitable static architecture.
- Clamp wind World Position Offset and reduce or disable it for distant vegetation.
- Use 2K runtime vegetation textures initially. Reserve 4K for the mosque portal and hero close-view masonry only where profiling supports it.
- Use landscape macro variation and layer blending to eliminate visible texture tiling.
- Foliage scalability may reduce cosmetic density, so terrain and ruins must remain sufficient cover at the lowest supported foliage setting.

## Validation gates before final placement

1. Import only the selected plants into a staging folder and record exact bounds, pivot, LODs, material count, texture sizes, collision, and Nanite state.
2. Place the TacticalMovement player beside each plant and capture standing, crouched, and prone comparisons.
3. Establish the minimum supported foliage density and verify that reducing density does not reveal a route that was designed as safe cover.
4. Measure GPU cost in representative near, middle, and far heritage-field views.
5. Validate North Defender Insertion protection before adding mosque or fortification hard cover.
6. Perform a first-pass sightline review from every accessible roof and elevated ruin.
7. Commit only after Map Check, multiplayer PIE traversal, and exact Git-scope review pass.

## Acquisition decision

New definite selections:

- Field Poppy: acquired in Fab as High-quality FBX; Launcher reports 41.43 MB on disk (listed archive size 41.44 MB).
- Wild Grass (`50d9a417-73ed-4132-9421-6be3d4f7432e`): acquired in Fab as High-quality FBX; Launcher reports 49.31 MB on disk (listed archive size 49.33 MB).
- Wild Grass ground material (`1a4cd0a2-cc9d-4ddf-95e1-6334c5cedb84`): acquired in Fab as the 4K texture set; Launcher reports 169.75 MB on disk (listed archive size 169.78 MB).
- Dry Trampled Soil (`e9c8521d-0d32-46ee-8607-bca13605159a`): acquired in Fab as the 4K texture set; Launcher reports 89.45 MB on disk (listed archive size 89.46 MB).
- Verified acquired total reported on disk: 349.94 MB. These are Fab source downloads only; they have not yet been imported into or validated inside TacticalMovement.
- Cracked Mud Wall (`381158fe-ea68-465a-b21d-05de2ea06045`): acquired in Epic's managed Fab library as the selected 4K texture set; verified on disk at approximately 94.64 MiB.
- Historic Desert Ruin Wall Brick 03 (`9d643c9c-b6f3-46ea-969b-702940ccc536`): acquired as the 4K texture set; verified on disk at approximately 52.59 MiB.
- Historic Desert Ruin Arch Stone Carved 08 (`8b6404bf-1081-4a7d-ac19-36f46bfd76fc`): acquired as High-quality FBX with 4K textures; verified on disk at approximately 95.38 MiB.
- Historic Desert Ruin Wall Modular Set 04 (`038f4719-7bd1-479f-94c1-ed7a191fff84`): acquired as High-quality FBX with 4K textures; verified on disk at approximately 113.40 MiB.
- Historic Desert Ruin Structure Stone S 06 (`0db909ab-188c-427b-a422-f69e49cc5b64`): acquired as High-quality FBX with 4K textures; verified on disk at approximately 81.80 MiB. This is the corrected small-opening asset; it replaces every prior reference to `Historic Desert Ruin Wall Modular Set 06`.
- Historic Pakistan Street Wall Brick White 01 (`f372a8f7-bc3d-4819-b8e7-5ffb1d270b7e`): acquired as the 4K texture set; verified on disk at approximately 10.73 MiB.
- Historic Pakistan Street Wall Brick Modular 16 (`9ecd80c7-2511-4b44-bab9-6de92e5200cd`): purchased and acquired as High glTF with 4K textures. UE 5.8 staging verified 200.603 × 30.578 × 350.016 cm bounds, 1,330 staging vertices, one material slot and Nanite enabled. The map-project import verified 1,325 built vertices, a map-owned packed-ORM material, a 2K runtime texture cap and nine non-colliding civic-facade instances across SS_005, SS_010 and SS_012.
- Historic Pakistan Street Window Brick Modular 04 (`e5026e65-304b-4ec5-a45e-4579e62dd141`): purchased and acquired as High glTF with 4K source textures. The exact Fab source is verified locally. The map import verified 261.819 × 47.663 × 347.620 cm bounds, 1,812 LOD0 vertices, one material slot, a map-owned packed-ORM material, a 2K runtime texture cap, Nanite enabled and 14 non-colliding HISM instances across SS_004, SS_005, SS_010 and SS_012.
- The earlier verified paid-source subtotal was approximately 448.55 MiB; Historic Pakistan Street Wall Brick Modular 16 was acquired later and is tracked separately because both High and Medium source tiers are cached. Selected heritage sources have now been imported selectively into TacticalMovement and validated per asset rather than copied wholesale.

Skip the paid Dry Soil Ground candidate because the selected free Dry Trampled Soil and already-owned ground materials cover that role.

The original definite paid heritage set was purchased at Personal tier for $11.94 before tax. The later Pakistan Wall Brick Modular 16 and Window Brick Modular 04 purchases expand that set for the civic Old Town facade pass. Both Pakistan modular assets are now verified in the map; every earlier statement that Window 04 was missing or not purchased is superseded by this record.

## Source links

- https://turkmenistan.gov.tm/en/post/57445/abiverd-city-crops-and-arable-land
- https://tourstoturkmenistan.com/en/sights/ashgabat/abiverd-settlement.html
- https://www.fab.com/listings/66cb2706-bc30-4f26-92ec-cad48723bd4a
- https://www.fab.com/listings/50d9a417-73ed-4132-9421-6be3d4f7432e
- https://www.fab.com/listings/1a4cd0a2-cc9d-4ddf-95e1-6334c5cedb84
- https://www.fab.com/listings/e9c8521d-0d32-46ee-8607-bca13605159a
- https://www.fab.com/listings/381158fe-ea68-465a-b21d-05de2ea06045
- https://www.fab.com/listings/9d643c9c-b6f3-46ea-969b-702940ccc536
- https://www.fab.com/listings/038f4719-7bd1-479f-94c1-ed7a191fff84
- https://www.fab.com/listings/8b6404bf-1081-4a7d-ac19-36f46bfd76fc
- https://www.fab.com/listings/0db909ab-188c-427b-a422-f69e49cc5b64
- https://www.fab.com/listings/f372a8f7-bc3d-4819-b8e7-5ffb1d270b7e
- https://www.fab.com/listings/9ecd80c7-2511-4b44-bab9-6de92e5200cd
- https://www.fab.com/listings/e5026e65-304b-4ec5-a45e-4579e62dd141
- https://dev.epicgames.com/documentation/en-us/unreal-engine/foliage-mode-in-unreal-engine
- https://dev.epicgames.com/documentation/en-us/unreal-engine/using-pcg-generation-modes-in-unreal-engine
- https://dev.epicgames.com/documentation/en-us/unreal-engine/nanite-virtualized-geometry-in-unreal-engine
- https://dev.epicgames.com/documentation/unreal-engine/procedural-vegetation-editor-pve-in-unreal-engine
