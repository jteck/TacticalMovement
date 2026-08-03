# Operation Sunscar — Old Town UE Execution Packet

Version: planning draft 1
Date: 2026-07-24
Unreal status during preparation: closed
Required paid asset budget: $0.00

## Purpose

This packet converts the approved Old Town design and exact Fab research into
an execution order. The later Unreal session should make bounded implementation
decisions only:

- Is the inspected source visually acceptable?
- Which exact mesh inside a source pack is selected?
- Does its measured scale and collision match the planned socket?
- Does the finished placement preserve gameplay?

Broad layout, asset-family selection and site roles are already fixed.

## Authoritative planning files

| File | Authority |
| --- | --- |
| `OLD_TOWN_SITE_RECIPES.csv` | Site centers, footprints, heights and density |
| `OLD_TOWN_EXACT_SITE_ASSIGNMENTS.csv` | Exact official source records per site |
| `OLD_TOWN_MASTER_ACQUISITION_PLAN.csv` | Free acquisition and deferred purchase order |
| `OLD_TOWN_UE_STAGING_MANIFEST.csv` | Exact staging destination, limits and exclusions for all 37 free sources |
| `OLD_TOWN_MAP_OWNED_MODULAR_KIT.csv` | Geometry created by the map project |
| `OLD_TOWN_MATERIAL_INSTANCE_PLAN.csv` | Material names, palette and coverage |
| `OLD_TOWN_BUILD_CHECKPOINTS.csv` | Stop/go validation gates |
| `OldTown_DownloadedAssetInventory_v1.json` | Verified local archives, checksums, pack contents and acquisition state |
| `OldTown_ResolvedPlacementPlan_v1.json` | All 2,350 candidate records joined to deterministic asset references |
| `OLD_TOWN_ASSET_SELECTION_MATRIX_V1.csv` | Site-by-site asset-family and planned-instance allocation |

## Unreal folder contract

Only intentionally selected assets enter the map project:

```text
/Game/Maps/Sunscar/
  Levels/
    Lvl_OldTown_ArtDraft
  Art/
    Architecture/
      Modular/
      Doors/
      Windows/
      Historic/
    Bazaar/
    Industrial/
    Props/
      Tactical/
      Dressing/
      Utility/
    Vehicles/
    Nature/
      Rocks/
      Debris/
      Foliage/
    Materials/
      Master/
      Instances/
      Decals/
  Blueprints/
    Assembly/
    Validation/
  PCG/
  Data/
  QA/
```

The existing blockout level remains the geometric authority. Art should be
placed in a new art-draft level or art Data Layers rather than destructively
replacing the blockout.

## Naming contract

- Static meshes: `SM_OT_[Category]_[Description]`
- Materials: `M_OT_[Description]`
- Material instances: `MI_OT_[Description]`
- Textures: `T_OT_[Description]_[Type]`
- Decals: `MI_D_OT_[Description]`
- Blueprint assemblies: `BP_OT_[Description]`
- PCG graphs: `PCG_OT_[Description]`
- Data assets/tables: `DA_OT_` or `DT_OT_`

Original source names may be retained inside a clearly named source folder
during staging. Selected project assets receive project naming only after
dependency-safe migration or duplication.

## Execution sequence

### Phase 0 — staging inspection and selective migration

The acquisition step is complete. The 35 direct archives and three official
packs are recorded in `OldTown_DownloadedAssetInventory_v1.json`. Do not
download or add the sources again.

1. Create or reuse a clean UE 5.8 staging copy outside TacticalMovement.
2. Inspect only the candidates referenced by
   `OldTown_ResolvedPlacementPlan_v1.json`.
3. Never import an entire sample scene into the production project.
4. For each selected source, record:
   - Unreal asset path.
   - Bounds in centimetres.
   - Pivot and forward axis.
   - Material-slot count.
   - Texture resolutions.
   - Nanite state.
   - Collision state.
   - Direct dependencies.
   - Approximate disk contribution.
5. Mark each inspected asset accepted, alternate, rejected or deferred.
6. Migrate only accepted assets and their dependency closure into dedicated
   Old Town art folders.

### Phase 1 — connected visual slice

Build this route first:

`Municipal Hotel → Central Courtyard → Tea House → Covered Bazaar → Detention approach`

Order:

1. Preserve and expose the verified graybox shell.
2. Add map-owned facade, parapet and opening modules.
3. Add doors, windows and shutters.
4. Apply the warm stucco, pale stucco and worn-ground family.
5. Construct Bazaar stalls and static tarp canopies.
6. Add only the planned large props.
7. Validate traversal and sightlines.
8. Add damage and low-risk dressing.
9. Capture one labeled and one clean high-resolution review image.

This slice becomes the look-development standard for the remaining sites.

### Phase 2 — civic and landmark sites

Complete:

- Old Clinic.
- Detention Annex.
- Water Tower Compound.
- Consulate Residence.
- Checkpoint Office.

The Water Tower remains a map-owned assembly. The free Metal Water Tank is
secondary detail only and must not be scaled into the hero tank.

### Phase 3 — industrial sites

Complete:

- Freight Depot.
- Salvage Yard.
- Motor Pool.
- Power Substation.
- Telecom Workshop.

City Sample supplies static vehicle art only. Junkyard supplies selected
salvage pieces only. No traffic systems, vehicle gameplay, Mass AI, sample
maps or unrelated Blueprints migrate into TacticalMovement.

### Phase 4 — canal, spawns and perimeter

Complete:

- Dry Canal Entrance.
- Canal Pump Station.
- Attacker Spawn and Extraction.
- South Defender Insertion.
- North Defender Insertion.
- Transit Plaza edge integration.

Spawn envelopes stay visually sparse and mechanically clear.

### Phase 5 — dressing, lighting and handoff

1. Place deterministic rubble and dry vegetation.
2. Add utilities, signs and restrained domestic props.
3. Review material tiling and macro variation.
4. Review daylight, exposure and player silhouette.
5. Run all checkpoint tests.
6. Capture clean and labeled review images.
7. Update the source ledger with final Unreal paths and rejected candidates.

## Map-owned geometry policy

Map-owned modules are simple, reusable shapes—not bespoke sculpture. Their
dimensions come from the gameplay plan.

Rules:

- Structural dimensions are exact.
- Decorative thickness may change slightly for shading, but never clear width.
- Window and door art binds to the opening; it does not redefine the opening.
- Canopy undersides remain at least 2.5 m high.
- Roof equipment cannot form a mantle route.
- Fence and gate collision cannot intrude into service or vehicle lanes.
- The hero water tower is an assembly with explicit access and collision.

The complete module specification is in
`OLD_TOWN_MAP_OWNED_MODULAR_KIT.csv`.

## Material policy

- Runtime default: 2K textures.
- Hero exception: 4K only after a visible comparison.
- Use one shared Old Town master material where practical.
- Expose tint, roughness, normal strength, macro variation, dust amount and
  damage-mask parameters.
- Use vertex paint or masks for sand accumulation and facade wear.
- Do not use displacement that changes traversable geometry.
- Avoid one material per object when an instance can share the master.

The initial palette is intentionally muted:

- Warm sand/off-white plaster.
- Pale landmark plaster.
- Dusty concrete.
- Dark gray-brown worn asphalt.
- Muted galvanized metal.
- Tan and brown-gray canvas.

## Nanite policy

Enable provisionally for:

- Dense rock scans.
- Large rubble scans.
- Complex salvage meshes.
- Selected City Sample static vehicle render meshes.

Usually unnecessary for:

- Simple map-owned modules.
- Doors, windows, poles and pipes.
- Small furniture and tools.
- Barrels and electrical boxes unless their source complexity justifies it.

Test rather than assume for masked dry grass. Nanite never replaces collision
review, material review or instance-count control.

## Collision policy

| Asset class | Collision |
| --- | --- |
| Building shell and opening modules | Simple exact collision |
| Vehicles, large scrap and tactical rocks | Manual simple collision |
| Sandbags and tactical barriers | Custom simple collision matching cover |
| Large cabinet and barrel | Simple box/cylinder |
| Bazaar stalls and poles | Simple collision; canopy has none |
| Minor rubble, tools, signs and decals | None |
| Dry grass and tiny debris | None |
| Hero water tower | Purpose-built simple collision |

Never use a raw photogrammetry scan as complex player collision.

## First-round quantity limits

- Static vehicles: 4–6 across Old Town.
- Tactical scrap groups: 4–6 in Salvage Yard.
- Barrels: approximately 8–14 total, manually placed.
- Major electrical cabinets: 2–4 total.
- Small/medium electrical boxes: approximately 15–25 total.
- Bazaar stalls: 8–12.
- Bazaar/Tea House canopy panels: 5–7 total.
- Domestic furniture groups: 6–10 total.
- Sandbag clusters: 5–7 total.
- Large manual rocks: under 12 inside the Old Town scope.

These are visual-budget limits, not targets that must be filled.

## Stop conditions

Stop the Unreal session and report before saving broadly if:

- The wrong worktree or project is open.
- Unreal requests module conversion or incompatible-module bypass.
- A source attempts to overwrite an existing project asset.
- A migration pulls an unexpectedly large dependency tree.
- Protected movement, animation, weapon, readiness or configuration files
  appear modified.
- Existing levels are mass-resaved.
- Art changes a verified route, opening, sightline, spawn envelope or mantle.
- A paid asset appears necessary before the free alternative is reviewed.

## Definition of the first complete round

Old Town round one is complete when:

- All 20 sites have their assigned structural treatment.
- The selected facade and ground materials are coherent.
- Doors, windows, parapets, shade and landmark silhouettes are present.
- Required vehicles and tactical props are placed and validated.
- Utilities, sparse vegetation, rubble and decals establish local identity.
- Lighting supports clear player silhouettes.
- Labeled and clean high-resolution images are captured.
- The movement owner can traverse the full area without regression.
- Final source paths, dimensions and asset decisions are documented.

Fine storytelling props, interiors, final VFX and cinematic polish are later
rounds and do not block this milestone.
