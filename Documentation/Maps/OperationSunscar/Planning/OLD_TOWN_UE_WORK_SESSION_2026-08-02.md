# Old Town UE Work Session — 2026-08-02

This is the Git-worktree copy of the local planning handoff at:

`MapDesign/Desert_Glory_Inspired/Planning/OLD_TOWN_UE_WORK_SESSION_2026-08-02.md`

## Verified scope

- Worktree: `/Users/jasonteck/UnrealEngine/_worktrees/map-development`
- Branch: `feature/map-development`
- Project: `TacticalMovement.uproject`
- Level: `/Game/Maps/Blockout/Lvl_Blockout_01`
- Automation write gate is closed: `apply_changes=false`, empty approval token.
- No protected movement, weapon, animation, readiness, network, startup-map or
  project-config asset was intentionally changed.
- No commit, push, PR, merge or `main` update was performed in this session.

## Accepted and saved map work

Exact-package saves cover 60 connected-slice scatter actors, 62 furniture actors,
8 official MilitaryTrench grass replacements, 8 grounded checkpoint sandbag and
collision actors, 22 storage/scrap actors, 3 electrical boxes and 24 market ground
debris actors.

An orientation migration corrected 171 placed actors after verifying that Unreal
Python positional `Rotator` values are roll, pitch, yaw. The builders now use
keyword arguments. Post-correction audits recorded zero rotation mismatches and
zero maximum bottom-contact error.

Support corrections included lowering the four checkpoint sandbag visuals and
four collision proxies by approximately 3.0–3.6 metres, minor crate support
adjustments, relocating one grass actor occluded by a crate and raising three
market debris objects by 6.6 cm.

## Rejected visual test

A 44-instance Quixel plaster-damage preview looked like flat brown panels despite
passing geometry checks. All 44 `OT_DAMAGE_` actors were destroyed without saving.
Eight additional facade sites remain held. The existing facade-damage pass must
not be restored without a new decal, conforming-mesh or replacement-module visual
approach.

## Clean-state verification

After the Mac locked, a read-only headless UE 5.8 verification explicitly loaded
`/Game/Maps/Blockout/Lvl_Blockout_01` and succeeded with:

- World `/Game/Maps/Blockout/Lvl_Blockout_01.Lvl_Blockout_01`.
- Rejected `OT_DAMAGE_` actors: 0.
- Dirty content packages: 0.
- Dirty map packages: 0.
- Exit code: 0.

The editor remains closed because macOS would not complete interactive window
startup while locked. Reopen only this isolated worktree after the Mac is unlocked.

## Next UE sequence

1. Load the Old Town map and rerun the dirty-package audit.
2. Capture overview and street-level images of the accepted pass.
3. Review the 18 held Detention sandbag candidates before applying them.
4. Prototype three facade treatments and approve one visually before expansion.
5. Continue terrain, ground-material, elevation and support integration.

Generated reports remain under excluded
`Saved/OperationSunscar/Reports/old_town_save_*_v1.json` paths. The current map is
an improved first dressing pass, not the completed Old Town art pass.

## Continued editor work — accepted and saved

The isolated UE 5.8 editor was reopened on the same project and Old Town level.
A City Sample guideline prompt requested `r.VirtualTextures=True`; it was
dismissed. No project setting, config file or guideline asset was changed.

- Corrected the 32-actor sandbag set, seven visual/proxy pairs and the checkpoint
  square; grounded eight corrugated barrier/base assemblies. Final review: zero.
- Applied role-specific surfaces to 50 core routes and 20 original site proxies.
- Added 84 bounded official ground/vegetation instances at seven open sites. One
  SS_020 grass support error was corrected; final geometry review: zero.
- Reused five existing vehicle proxy actors in place for three City Sample
  Salvage Yard vehicles and two Motor Pool vehicles. Four support offsets were
  corrected; collision and actor identity were preserved; final review: zero.
- Added 13 support-resolved Quixel electrical boxes across six sites. Four
  candidates 8.6–19.1 m from a matching façade were deferred. Accepted boxes are
  8 cm from walls and 100 cm above floors, with no pair overlaps.
- Replaced 16 existing 125 × 18 × 240 cm pedestrian-door proxies in place with
  the Quixel Old Wooden Door. The 500 × 18 × 400 cm Depot loading door was
  excluded. Bounds, bottom datum, labels, identity and collision were preserved.

Exact saves covered five vehicle actor packages, 13 utility actor packages plus
seven required `ActorFolder` packages, and 16 door actor packages. No Save All was
used. The coverage audit was also corrected so `car` no longer falsely matches
the word `Sunscar`.

Important excluded reports under `Saved/OperationSunscar/Reports/` include:

- `old_town_static_vehicle_audit_v1.json`
- `old_town_save_vehicle_replacements_v1.json`
- `old_town_remaining_small_electrical_audit_v1.json`
- `old_town_remaining_small_electrical_scope_audit_v1.json`
- `old_town_save_remaining_small_electrical_v1.json`
- `old_town_door_proxy_audit_v1.json`
- `old_town_door_asset_probe_v1.json`
- `old_town_door_replacement_audit_v1.json`
- `old_town_save_door_replacements_v1.json`
- `old_town_site_coverage_audit_v1.json`
- `old_town_dirty_package_audit.json`

Current state: editor open on the isolated map-development project; automation
write gate closed; dirty content packages 0; dirty map packages 0. No commit,
push, PR, merge, rebase or `main` update was performed, and no protected system
or project configuration was intentionally changed.

Next controlled layer: audit existing window/shutter proxies for official-asset
replacement; otherwise place medium/large utility enclosures only where actual
façade/floor support resolves safely.

## Medium utility-enclosure continuation

The downloaded utility meshes were measured before placement: the medium box is
approximately 101.9 × 24.0 × 97.9 cm and the large cabinet is approximately
262.0 × 87.3 × 138.8 cm. Of 16 planned medium/large candidates, ten medium boxes
were accepted and six were deferred. Two medium SS_016 coordinates lacked a
nearby façade. All four large cabinets were removed from the unsaved preview
because one intersected a real Pump Station wall and the group requires a
separate tactical-clearance pass.

The ten accepted medium boxes span SS_003, SS_011, SS_016 and SS_018. Each is
upright, 40 cm above its supporting floor, aligned to the real wall normal, 4 cm
clear of the façade, collision-disabled to prevent an equipment climb chain, and
free of pair overlaps. Exactly ten actor packages and five verified `ActorFolder`
packages were saved. Final dirty content and map package counts were both zero.

There are 40 existing window frame/glass pairs, but no resolved official window
or shutter asset in the downloaded registry. They remain unchanged rather than
being replaced by an unrelated substitute.

Additional reports:

- `old_town_utility_asset_probe_v1.json`
- `old_town_utility_enclosure_dry_run_v1.json`
- `old_town_utility_enclosure_audit_v1.json`
- `old_town_medium_utility_scope_audit_v1.json`
- `old_town_save_medium_utility_enclosures_v1.json`

Fresh current-state overview exports were written outside the Unreal repository:

- `MapDesign/Desert_Glory_Inspired/Exports/2026-08-02/OldTown_Current_Overview_Clean.png`
- `MapDesign/Desert_Glory_Inspired/Exports/2026-08-02/OldTown_Current_Overview_Labeled.png`

The clean capture temporarily hid all 48 `Sunscar/TemporaryLabels` TextRender
actors and then restored them. Both visibility operations were transient and
left dirty content packages at 0 and dirty map packages at 0.

## Structural and route surface continuation

A read-only inventory identified 82 `Core_SS_*` structural actors still using
prototype materials: 47 walls, 19 floors, 12 roofs and 4 parapets across 13
building sites. A dry-run-first pass replaced only their material slot and added
an audit tag; geometry, transforms, openings and collision were unchanged.

- Walls and parapets use the established site palette: Pale Stucco, Warm Stucco,
  Stone, Detention or Metal according to site role.
- All 19 floor pieces use `MI_OT_Ground_Concrete`.
- Industrial roofs at SS_003, SS_006, SS_013, SS_015, SS_016 and SS_018 use
  `MI_OT_Metal`; the remaining roofs use `MI_OT_Stone`.
- Exactly 82 external-actor packages were saved. The post-save dirty count was 0.

The next exact pass covered all 50 `CoreRoute_*` actors after the dry run
confirmed they were still on prototype-grid materials: 10 Alpha Dry Canal, 10
Bravo Courtyard, 14 Charlie Bazaar and 16 alley/connectors.

- Alpha uses `MI_OT_Ground_Silt`.
- Bravo and the alley/connectors use `MI_OT_Ground_Earth`.
- Charlie uses the official Fab/Quixel crushed-asphalt material
  `MI_sjyjcbja`.
- Exactly 50 external-actor packages were saved. The post-save target dirty
  count was 0.

All 12 `CoreWall_*` perimeter segments were then dry-run verified and changed
from the remaining prototype-grid material to `MI_OT_Stone`. Exactly 12 actor
packages were saved. Final Unreal state: dirty content packages 0, dirty map
packages 0, unexpected packages 0, and automation write gate closed.

The material-master probe confirmed that the official Fab master
`/Game/Fab/Materials/Standard/M_MS_Srf` supports texture, tiling and surface
controls without changing the dismissed virtual-texture project setting. The
downloaded wall surfaces remain held for a later close-range façade prototype;
they were not stretched across all buildings without a visual-scale review.

New automation/audit scripts:

- `old_town_structural_material_audit_v1.py`
- `old_town_structural_material_pass_v1.py`
- `old_town_save_structural_materials_v1.py`
- `old_town_perimeter_wall_material_pass_v1.py`
- `old_town_save_perimeter_wall_materials_v1.py`

New excluded reports include the structural, route, perimeter and exact-save
JSON reports under `Saved/OperationSunscar/Reports/`.

Fresh surface-pass exports were written outside the Unreal repository:

- `MapDesign/Desert_Glory_Inspired/Exports/2026-08-02/OldTown_SurfacePass_Overview_Clean.png`
- `MapDesign/Desert_Glory_Inspired/Exports/2026-08-02/OldTown_SurfacePass_Overview_Labeled.png`

The clean capture temporarily hid the 48 label actors and restored them for the
labeled editor view. Neither visibility change dirtied a package. No commit,
push, PR, merge, rebase, startup-map change or project-config change was made.

## Landscape material continuation

A read-only large-ground audit confirmed that the remaining checkerboard was the
parent `Landscape_Sunscar` plus four Landscape Streaming Proxies, all with a blank
Landscape material slot. The visualization-route actors were not treated as
terrain.

A map-owned material instance was created at
`/Game/Maps/Sunscar/Art/Materials/Landscape/MI_OT_Landscape_Sandstone`. It reuses
the official Fab master `/Game/Fab/Materials/Standard/M_MS_Srf` and the downloaded
Quixel `Sandstone_Rocky_Ground_vmjjfiv` base-color and normal textures. Default Fab
mask/displacement textures avoid changing the dismissed virtual-texture project
setting. The selected first-draft controls are Tiling 256, Normal Intensity 0.65,
Specular 0.25, roughness 0.72-1.0, Saturation 0.78, Brightness 0.82 and Contrast
0.9.

The unsaved prototype was reviewed in top-down, oblique and courtyard views. It
removed the checkerboard without error shading or obvious district-scale texture
artifacts. The material and only the parent Landscape external-actor package were
saved. The four streaming-proxy preview packages were reloaded from disk instead
of being saved; they now inherit the parent material and retain no pass tags.
Read-only verification found five Landscape actors, the expected official parent
material, and zero dirty Unreal packages. The automation write gate was closed
again immediately after the exact save.

New automation/audit scripts:

- `old_town_large_ground_audit_v1.py`
- `old_town_landscape_material_pass_v1.py`
- `old_town_finalize_landscape_material_v1.py`
- `old_town_verify_landscape_material_v1.py`

Fresh exports outside the Unreal repository:

- `MapDesign/Desert_Glory_Inspired/Exports/2026-08-02/OldTown_LandscapePass_Overview_Clean.png`
- `MapDesign/Desert_Glory_Inspired/Exports/2026-08-02/OldTown_LandscapePass_Overview_Labeled.png`

No Save All, project-setting change, protected-system edit, commit, push, PR,
merge, rebase or `main` update was performed.

## Quixel facade look-development continuation

Three official Quixel surface families were reviewed on temporary panels and
retained as map-owned material instances:

- `/Game/Maps/Sunscar/Art/Materials/Facade/MI_OT_Stucco_Quixel` — baseline Old
  Town stucco.
- `/Game/Maps/Sunscar/Art/Materials/Facade/MI_OT_FlakedPaint_Quixel` — aged
  residential/civic variation.
- `/Game/Maps/Sunscar/Art/Materials/Facade/MI_OT_WallPaint_Quixel` — restricted
  industrial/accent variation.

Each instance reuses the official Fab `M_MS_Srf` master plus the already
migrated Quixel base-color and normal textures. Exactly those three content
packages were saved; the comparison actors were transient and no map package
was dirtied by the material review.

SS_005 Old Clinic became the first real-building facade standard. The initial
six-wall preview revealed that its door/window openings were separate core
pieces still using prototype grid. A 61-actor local audit resolved the complete
exterior scope without altering doors, windows, floors, roof, interior walls,
collision or transforms. Quixel stucco was then applied to exactly 16 exterior
wall/lintel/parapet actors. Street-level review confirmed a coherent facade and
preserved all openings. Exactly 16 external-actor packages were saved and the
post-save dirty-package count was zero.

New scripts:

- `old_town_facade_surface_showcase_v1.py`
- `old_town_discard_facade_surface_showcase_v1.py`
- `old_town_facade_material_preview_v1.py`
- `old_town_save_facade_materials_v1.py`
- `old_town_facade_site_prototype_v1.py`
- `old_town_ss005_facade_audit_v1.py`
- `old_town_complete_ss005_facade_preview_v1.py`
- `old_town_save_ss005_facade_v1.py`

Street-level export outside the Unreal repository:

- `MapDesign/Desert_Glory_Inspired/Exports/2026-08-02/OldTown_SS005_QuixelStucco_Facade.png`

The facade review did not change gameplay geometry or protected systems. No Save
All, project-setting change, commit, push, PR, merge, rebase or `main` update was
performed.

## Facade expansion continuation

A whole-Old-Town read-only exterior audit resolved 164 wall, split-opening,
lintel and parapet actors across twelve structural sites. It found 83 pieces still
using Level Prototyping materials, confirming that the earlier 82-piece structural
pass did not include every split facade component.

The approved SS_005 Quixel stucco standard was expanded to exactly 50 exterior
actors across SS_004, SS_007 and SS_012. The pass included the split wall and
lintel pieces that previously retained prototype grid. Street-level and top-down
reviews showed coherent facades without changing openings, collision, transforms,
floors, roofs or interior walls. Exactly 50 actor packages were saved and the
post-save dirty-package count was zero.

The next aged-facade branch was tested on all ten SS_017 exterior pieces with the
Quixel flaked-paint material. Street-level review rejected it because the source
UV treatment stretched visibly across the long wall. None of those changes were
saved. Exactly ten dirty preview packages were reloaded from disk, restoring the
prior SS_017 state and returning Unreal to zero dirty packages. Flaked paint is
therefore held for a world-aligned material or smaller modular-wall solution; it
must not be expanded with the current UV setup.

New scripts:

- `old_town_facade_expansion_audit_v1.py`
- `old_town_expand_stucco_facades_v1.py`
- `old_town_save_stucco_facades_v1.py`
- `old_town_flaked_facade_prototype_v1.py`
- `old_town_discard_flaked_facade_preview_v1.py`

Current verified state: automation write gate closed and Unreal dirty content/map
package counts both zero. No Save All, protected-system edit, project-setting
change, commit, push, PR, merge, rebase or `main` update was performed.

## World-aligned facade continuation

The rejected SS_017 stretched-UV result was replaced with a reusable map-owned
world-aligned material master:

- `/Game/Maps/Sunscar/Art/Materials/Facade/M_OT_WorldAlignedFacade`
- `/Game/Maps/Sunscar/Art/Materials/Facade/MI_OT_FlakedPaint_WorldAligned`
- `/Game/Maps/Sunscar/Art/Materials/Facade/MI_OT_Stucco_WorldAligned`

The master reuses the downloaded official Quixel base-color and normal textures
and Epic's built-in `WorldAlignedTexture` and `WorldAlignedNormal` material
functions. The selected first-draft physical projection size is 200 cm. This is
a map-owned adaptation of the official material inputs, required because the
graybox wall cubes have non-uniform scale and ordinary mesh UVs stretched the
flaked-paint surface across long walls.

SS_017 was the controlled prototype. All ten exterior wall/lintel pieces were
reviewed from front and oblique angles. The texture stayed at a consistent scale
across the long south wall and the perpendicular west wall. Exactly the two new
material packages and ten SS_017 external-actor packages were saved.

The validated treatment was then expanded to 66 stucco exterior pieces across
SS_004, SS_005, SS_007 and SS_012, plus 14 core SS_011 wall pieces using the
world-aligned flaked-paint instance. The four SS_011 stone parapets were
intentionally preserved. Exactly one new stucco material-instance package and
80 external-actor packages were saved. The post-save dirty-package count was
zero.

New scripts:

- `old_town_world_aligned_facade_prototype_v1.py`
- `old_town_save_world_aligned_facade_v1.py`
- `old_town_world_aligned_facade_rollout_v1.py`
- `old_town_save_world_aligned_facade_rollout_v1.py`

New excluded reports under `Saved/OperationSunscar/Reports/`:

- `old_town_world_aligned_facade_prototype_v1.json`
- `old_town_save_world_aligned_facade_v1.json`
- `old_town_world_aligned_facade_rollout_v1.json`
- `old_town_save_world_aligned_facade_rollout_v1.json`

## Deferred large-cabinet resolution

The four downloaded Quixel large electrical cabinets previously removed from
the utility preview were re-evaluated against actual floor, wall, door, prop and
source-footprint geometry. The resolver first produced a read-only result:

- `SS_003_UTILITY_008` moved 100 cm to clear the Pump Station south wall and
  `Pump_Door_B`.
- `SS_003_UTILITY_013` remained at its planned coordinate.
- `SS_016_UTILITY_020` moved 25 cm to clear the Power Substation west wall.
- `SS_016_UTILITY_027` remained at its planned coordinate.

All four accepted cabinets use the official Quixel
`Electrical_Cabinet_ujzfde2_High` mesh. They are bottom-aligned to their real
support floors, retain `Query And Physics` collision as intentional hard cover,
and have no scene overlaps or pair overlaps. Exactly four actor packages and
three required `ActorFolder` packages were saved; the post-save dirty-package
count was zero.

New scripts:

- `old_town_large_utility_resolver_v1.py`
- `old_town_large_utility_audit_v1.py`
- `old_town_save_large_utility_v1.py`

Fresh current-state exports outside the Unreal repository:

- `MapDesign/Desert_Glory_Inspired/Exports/2026-08-02/OldTown_WorldAlignedFacade_Round_Overview_Clean.png`
- `MapDesign/Desert_Glory_Inspired/Exports/2026-08-02/OldTown_WorldAlignedFacade_Round_Overview_Labeled.png`

The clean export temporarily hid only the 48 TextRender label actors and then
restored them for the labeled export. Neither visibility operation dirtied a
package. The editor viewport was also restored to Lit mode after a temporary
interior review. No Save All, protected-system edit, project-setting change,
commit, push, PR, merge, rebase or `main` update was performed.

## Full visible-surface and support cleanup continuation

The remaining Old Town facade and named-compound scope was completed without
changing building transforms, openings or collision. Forty prototype exterior
pieces across SS_003, SS_010, SS_013, SS_015, SS_016 and SS_018 received their
reviewed stone, detention or metal treatment. Twenty additional exterior walls
in Detention Yard, Salvage Yard and Water Tower Compound received the established
detention, world-aligned flaked-paint or world-aligned stucco materials. Exact
saves covered 60 external-actor packages and returned Unreal to zero dirty
packages.

A reusable Quixel/Epic world-aligned ground family was added under
`/Game/Maps/Sunscar/Art/Materials/Ground/WorldAligned`. It contains one master
and eight instances for fresh, crushed and cracked asphalt; weathered concrete;
and four sandstone variations. The materials reuse the already downloaded
official Quixel textures plus Epic's `WorldAlignedTexture` and
`WorldAlignedNormal` functions. The master was repaired on macOS by assigning
valid default base-color and normal texture objects before compilation. Exactly
nine material packages and 288 `VisualGroundOverlay` actor packages were saved.

A five-point support audit checked the center and four inset corners of every
available first-floor slab against both Landscape collision and overlapping
ground overlays. Eleven buildings were already supported within normal shallow
embed tolerance. SS_010 was the only verified gap: its raised detention terrace
covered the northeast portion while the remaining slab footprint was roughly
47-49 cm above Landscape. One map-owned stone support plinth was added beneath
the full 3,400 x 2,800 cm building footprint, with a 60 cm total height and its
top aligned to the floor bottom. The post-repair audit reports zero verified
support gaps and zero unknown samples. The two exact saves of the support actor
and its final expansion left no dirty packages.

The remaining large horizontal and internal blockout surfaces were then
finished:

- 19 floor slabs, seven masonry roof slabs and 11 exterior ramps/landings use
  the Quixel weathered-concrete world-aligned material.
- Seven Central Courtyard walls use the world-aligned stucco material.
- Fourteen interior partitions use world-aligned stucco.
- The SS_006 water-tower pillar uses the established metal treatment and its
  platform uses weathered concrete.

Exactly 44 horizontal/courtyard actor packages and 16 interior/tower actor
packages were saved. Industrial metal roofs were intentionally preserved rather
than homogenized.

The final Old Town core-cover pass preserved every gameplay collision footprint.
Twenty-eight hard-cover cubes were retained and resurfaced by district with
Quixel stone, weathered concrete or metal; the freight-crate proxy received the
timber treatment. The visually duplicated checkpoint cube and five vehicle
collision proxies were made invisible while retaining `Query And Physics`
collision. Five collision-disabled City Sample vehicle visuals were placed over
the Motor Pool and Salvage Yard proxies and bottom-aligned with 0 cm error.
Exactly 39 existing/new actor packages were saved.

The final remaining-prototype audit found 91 prototype-material actors:

- 22 are intentional invisible collision actors inside Old Town, all with
  `Query And Physics` collision and `visible=false`.
- 69 are infrastructure and route actors in future expansion regions outside
  Old Town and were intentionally left untouched.

Therefore no visible Old Town actor remains on a prototype-grid material. The
final support audit reports zero verified floating-floor gaps. Unreal Map Check
reports 0 errors and six same-location warnings (three symmetric pairs). A
read-only scan of all currently loaded StaticMesh actors found zero duplicate
transform groups, so the warnings were not changed without positive identity
evidence; they may belong to unloaded World Partition actors.

New automation and audit scripts in this continuation:

- `old_town_building_support_audit_v2.py`
- `old_town_horizontal_surface_audit_v1.py`
- `old_town_horizontal_surface_finish_v1.py`
- `old_town_save_horizontal_surface_finish_v1.py`
- `old_town_ss010_foundation_support_v1.py`
- `old_town_save_ss010_foundation_support_v1.py`
- `old_town_ss010_foundation_support_expand_v1.py`
- `old_town_save_ss010_foundation_support_expand_v1.py`
- `old_town_interior_and_tower_surface_v1.py`
- `old_town_save_interior_and_tower_surface_v1.py`
- `old_town_core_cover_proxy_audit_v1.py`
- `old_town_core_cover_finish_v1.py`
- `old_town_save_core_cover_finish_v1.py`
- `old_town_duplicate_location_audit_v1.py`

Current verified state: editor open on the isolated map-development worktree;
automation write gate closed; dirty content packages 0; dirty map packages 0.
No Save All, protected-system edit, project-setting change, commit, push, PR,
merge, rebase or `main` update was performed in this continuation.

Fresh 4K review exports from the completed visible-surface, support and core-cover
round are stored outside the Unreal repository:

- `MapDesign/Desert_Glory_Inspired/Exports/2026-08-02/OldTown_SurfaceSupportCover_Round_Overview_Labeled_4K.png`
- `MapDesign/Desert_Glory_Inspired/Exports/2026-08-02/OldTown_SurfaceSupportCover_Round_Overview_Clean_4K.png`

Both images are 3840 x 2160. The clean export hid only the temporary TextRender
labels and the labeled state was restored afterward without dirtying any package.

## Bounded industrial-detail continuation

The resolved placement plan was reconciled against the already placed Old Town
actors before adding further clutter. Large `OT_TAC_006` cover pieces were
deferred because they would alter combat lanes, `OT_SCRAP_004` hand tools were
deferred for explicit pitch/lean review, and `OT_UTIL_008` was deferred until its
existing large-utility placements are reconciled. The retained decorative batch
uses only downloaded official Epic/Quixel content and adds 51 collision-disabled
actors:

- 14 vehicle-part details (`OT_SCRAP_001`) in SS_013 Motor Pool.
- 16 weathered tires (`OT_SCRAP_002`) in SS_014 Salvage Yard.
- 10 rusty barrels (`OT_SCRAP_003`) across SS_003, SS_011 and SS_014.
- 11 crates and pallets (`OT_SCRAP_005`) in SS_015 Storage Depot.

The dry run rejected candidates that were too tightly spaced or overlapped
existing vehicle, fence, utility, crate or hard-cover collision. After placement,
44 actors were raised 2.894-22.958 cm from raw Landscape height to the actual
finished floor or asphalt support. The final read-only audit reports 51 actors,
zero support exceptions, a -0.002 to 0.003 cm support-gap range, zero pair
overlaps and `NoCollision` on every actor. An angled Salvage Yard review also
showed the clutter seated on the finished surface and spaced around the vehicle
cover.

Exactly 57 World Partition packages were saved: 51 actor packages and six
required folder-object packages. No content package, level package, protected
asset or unrelated package was saved. The post-save audit reports zero dirty
packages, the 48 temporary labels are visible again, and the automation gate is
closed.

New scripts:

- `old_town_industrial_detail_builder_v1.py`
- `old_town_industrial_detail_support_fix_v1.py`
- `old_town_industrial_detail_audit_v1.py`
- `old_town_save_industrial_detail_v1.py`
- `old_town_focus_industrial_review_v1.py`

New review export outside the Unreal repository:

- `MapDesign/Desert_Glory_Inspired/Exports/2026-08-02/OldTown_IndustrialDetail_Round_SalvageYard_Angled_2560x1440.png`

No Save All, project-setting change, commit, push, PR, merge, rebase or `main`
update was performed in this continuation.


## Ground, collision persistence and first-complete-round validation

This continuation completed the recommended ground → architecture → exterior
dressing → gameplay validation → presentation sequence for the first viewable
Old Town draft.

### Verified ground facts

- A read-only audit resolved 138 broad ground actors: 82 supports, 50 routes and
  six site grounds. Fifty-seven still used the older inconsistent ground family.
- Those 57 actors were changed to the existing map-owned world-aligned Quixel
  ground family. Geometry, transforms and collision were preserved.
- The five Landscape actors were assigned the sandstone-earth treatment.
- The original `M_OT_WorldAlignedGround` failed Metal SM5 because the
  `WorldAlignedNormal` branch sampled the default color texture as a normal.
  The master was rebuilt as a Mac-safe world-XY material using
  `AbsoluteWorldPosition.XY / TextureSizeCm.XY`. It continues to reuse the
  downloaded official Quixel base-color textures. The normal branch remains
  intentionally deferred until a cross-platform-safe implementation is tested.
- The master and eight ground instances were saved exactly. A lighting-calibrated
  palette differentiates fresh, cracked and crushed asphalt; sandstone dust,
  earth, silt and stone; and weathered concrete.
- Exactly 62 external-actor packages were saved for the 57 ground-material
  conversions and five Landscape bindings. No content or unrelated map package
  remained dirty afterward.
- Final conformance remains 288 of 288 visual overlays at `NoCollision`, with
  zero review items and a maximum sampled fit error of 8.137 cm.

Relevant generated reports under `Saved/OperationSunscar/Reports/` include:

- `old_town_ground_coherence_audit_v1.json`
- `old_town_ground_coherence_apply_v1.json`
- `old_town_landscape_coherence_apply_v1.json`
- `old_town_world_aligned_texture_audit_v1.json`
- `old_town_world_xy_ground_rebuild_v1.json`
- `old_town_save_ground_material_repair_v1.json`
- `old_town_ground_palette_calibration_v2.json`
- `old_town_save_ground_coherence_maps_v1.json`

### Verified architecture facts

- Twelve first-floor slabs report zero verified support gaps and zero unknown
  samples.
- All 40 window frame/glass pairs remain valid, with zero opening issues.
- All 16 Quixel wooden-door replacements remain valid and retain
  `Query And Physics` collision.
- Thirty-four core cover/proxy actors remain present with their intended
  gameplay role.
- The duplicate-transform audit reports zero groups.
- No visible actor inside Old Town remains on a prototype-grid material. The 91
  records still found by the whole-map prototype scan are either intentional
  invisible collision or future expansion-region infrastructure.

### Persistent decorative-collision repair

Reload validation exposed that the earlier component-only
`set_collision_enabled(NoCollision)` calls did not remain serialized after a
later editor reload. A dry run resolved exactly 460 visual-only StaticMesh
components across these tags:

- 288 `VisualGroundOverlay` actors.
- 58 static-mesh actors from the exterior-completion pass.
- 19 window shutters.
- 51 industrial-detail actors.
- Nine hand-tool actors.
- Ten rooftop-utility actors.
- Nine landmark sign boards.
- 16 facade-conduit actors.

The bounded repair set both the serialized `NoCollision` profile and collision
enabled state on those exact 460 components. Doors, walls, floors, hard cover,
vehicle collision proxies and all 32 sandbag actors were excluded. Exactly 460
external-actor packages were saved. Post-save audits report zero collision
review items for every affected category.

Disabling visual-overlay collision also revealed two genuinely floating
SS_014 decorations that had previously traced against the non-gameplay overlay
surface. `OT_INDDETAIL_SS_014_INDUSTRIAL_004` and
`OT_INDDETAIL_SS_014_INDUSTRIAL_009` were lowered 6.881 cm and 4.361 cm to their
Landscape support. Exactly two actor packages were saved. The final industrial
and hand-tool audits both report zero review items and zero overlaps.

New persistent-collision and validation scripts:

- `old_town_persistent_decorative_collision_v1.py`
- `old_town_save_persistent_decorative_collision_v1.py`
- `old_town_industrial_detail_landscape_support_fix_v2.py`
- `old_town_save_industrial_detail_landscape_support_v2.py`
- `old_town_gameplay_route_audit_v1.py`

The industrial-detail and hand-tool audits were also updated to treat
collision-disabled visual overlays as visual support by bounds rather than by a
physics trace. This keeps the audit aligned with the intended gameplay model:
Landscape/structural floors provide collision; overlays provide appearance.

### Gameplay validation facts

- PIE launched successfully with the TacticalMovement first-person pawn and
  weapon at expected player height. The session ended cleanly with Escape.
- The UI automation could not produce a reliable continuous held-key traversal,
  so rapid key taps were not claimed as a movement playtest.
- All 50 `CoreRoute_*` actors pass the route audit. The narrowest measured route
  is 300 cm, above the 250 cm first-draft review threshold, and no route uses a
  prototype material.
- The ground, building-support, door, cover, sandbag, window, exterior,
  industrial, hand-tool, rooftop, sign, facade-conduit, duplicate and lighting
  audits all complete with zero current review items.
- Unreal reports zero dirty content packages and zero dirty map packages.
- `MapCheck` accepted the command but did not emit a new completion summary in
  the active log. The bounded audits above are the authoritative validation for
  this continuation.

### Final presentation exports

The fresh presentation files are outside the Unreal repository at:

- `MapDesign/Desert_Glory_Inspired/Exports/2026-08-02/FinalOldTownRound/OldTown_FinalRound_Overhead_Clean_8K.png`
- `MapDesign/Desert_Glory_Inspired/Exports/2026-08-02/FinalOldTownRound/OldTown_FinalRound_Overhead_Labeled_8K.png`
- `MapDesign/Desert_Glory_Inspired/Exports/2026-08-02/FinalOldTownRound/OldTown_FinalRound_PlayerHeight_Clean_4K.png`

The 48 temporary navigation labels are restored and visible in the editor after
capture. Their visibility changes are transient and did not dirty packages.

### Current handoff state

Verified fact: this is the first complete, viewable Old Town round, not final
shipping art. Ground, building shells, facade materials, openings, roofs,
exterior props, utilities, collision roles and first-draft gameplay widths are
all present and validated. Further work is a polish/playtest pass: continuous
human traversal, sightline tuning, canopy/pole silhouette review, lighting and
material refinement, Nanite/LOD/performance profiling, and replacement of any
remaining map-owned proxy geometry only when a demonstrably better Epic/Quixel
asset exists.

The automation write gate is closed (`apply_changes=false`, empty approval
token). No protected movement, weapon, animation, readiness, network,
startup-map or project-config asset was changed. No Save All, commit, push, PR,
merge, rebase or `main` update was performed in this continuation.


## Player-height ground and exterior-completion continuation

A playable PIE session was started with the TacticalMovement pawn and weapon so
the Old Town draft could be judged from the actual player camera. The first
player-height review verified that the imported ground textures were present,
but it also exposed two separate issues that were not obvious from the high
editor camera:

1. distant surfaces and façades were being washed out by exposure; and
2. the visual ground-overlay tiles were acting as collision and showing raised
   slab edges instead of remaining visual-only over the Landscape.

The map-local `Sunscar_PostProcessVolume` now overrides only exposure bias at
`-0.75` and remains unbound. No project setting, camera asset, game mode,
movement asset or configuration file was changed. A second PIE comparison
confirmed better material definition while retaining readable shadows.

A complete first-draft small-exterior pass added 112 actors:

- 18 proper projected debris/rubble/garbage decals on the connected roads;
- 24 paired narrow dirt-wear decals for vehicle-readable route breakup;
- 10 drainpipes and 10 drain outlets;
- 10 exterior utility meters;
- 12 proper wall-projected leak/grime decals, replacing the previously rejected
  flat-panel damage approach;
- eight door thresholds;
- six rooftop mast bases and six rooftop masts; and
- eight short roadside posts.

The decals reuse Epic-owned Military Trench and Scene Junkyard materials. The
static-mesh details reuse Epic basic shapes and the existing map-owned metal
material. Every new mesh detail is `NoCollision`; none changes combat cover,
vehicle clearance or traversal. Large tanks, route-affecting tactical scrap and
other playtest-dependent objects remain intentionally deferred.

The ground-conformance audit found a verified foundation problem: all 288 actors
tagged `VisualGroundOverlay` were set to `QueryAndPhysics`, despite the
documented design that they should be visual-only. Thirty-nine overlays also had
sampled visual gaps above 20 cm, with a worst fit of 41.55 cm. The bounded
correction:

- disabled collision on all 288 visual overlays;
- reduced their visible thickness from 2.5 cm to 0.8 cm;
- fitted pitch, roll and center height to five Landscape samples per tile;
- clamped six steep fits to a maximum of six degrees; and
- preserved every existing material, actor identity and World Partition
  package.

The post-apply audit reports:

- 288 of 288 overlays are `NoCollision`;
- zero overlays exceed the 18 cm review threshold;
- 275 overlays are within 5 cm of the sampled Landscape;
- the remaining 13 are between 5 and 8.137 cm;
- maximum fit error is 8.137 cm; and
- zero unexpected dirty packages.

The final exterior audit reports 112 actors and zero review items. The lighting
audit reports zero review items. The fresh sandbag audit also reports zero review
items, confirming that the earlier upper-floor sandbag correction remains clean.
A final PIE pass confirmed that the player now stands on the Landscape and the
large raised-slab behavior is gone from the start sector.

Exactly 412 verified map packages were saved:

- 401 intentional external-actor packages, exactly matching 112 exterior actors,
  288 corrected ground overlays and one post-process actor; and
- 11 required World Partition external-object packages.

No content package, level package, source file, configuration asset, protected
movement/weapon/animation asset or unrelated map package was saved. The final
Unreal dirty-package audit reports zero dirty packages and the automation write
gate is closed. The latest `MapCheck` command was accepted but did not emit a
new completion summary in the log; the bounded audits and PIE validation above
are the authoritative checks for this pass.

New scripts:

- `old_town_start_pie_v1.py`
- `old_town_end_pie_v1.py`
- `old_town_exterior_completion_audit_v1.py`
- `old_town_exterior_completion_builder_v1.py`
- `old_town_exterior_completion_audit_v2.py`
- `old_town_focus_exterior_completion_review_v1.py`
- `old_town_lighting_balance_v1.py`
- `old_town_lighting_balance_audit_v1.py`
- `old_town_ground_overlay_conformance_v1.py`
- `old_town_ground_overlay_conformance_audit_v1.py`
- `old_town_save_exterior_completion_v1.py`

No commit, push, PR, merge, rebase or `main` update was performed in this
continuation.


## Exterior openings, ground and roadway continuation

A fresh completion audit verified that Old Town already has a finished ground
and roadway layer, so it was preserved rather than rebuilt. The loaded level
contains 560 broad near-ground actors and 288 visual ground-overlay actors using
the established world-aligned asphalt, weathered concrete, sandstone dust,
earth, silt and stone materials. The Landscape uses
`MI_OT_Landscape_Sandstone`. The remaining prototype-grid scan found no visible
prototype actor inside Old Town: its 69 visible records belong to future
expansion routes and transition walls outside the Old Town core, while the
remaining records are intentional invisible collision actors.

The building-support audit sampled the center and four inset corners of all 12
first-floor slabs against the finished overlays and Landscape. It reports zero
verified gaps and zero unknown samples. Shallow 4–6 cm floor embed beneath
visual ground overlays is intentional and prevents visible floating seams.

The opening audit confirmed that all 16 pedestrian doors remain valid Quixel Old
Wooden Door replacements with preserved dimensions, actor identity and
`Query And Physics` collision. The Freight Depot loading door remains the
map-owned 5 x 0.18 x 4 m loading-panel assembly because the downloaded garage
door source is a surface treatment rather than a structural door mesh.

All 40 existing window frame/glass pairs were re-audited and pair correctly:

- 29 timber frames.
- 11 metal frames.
- 40 map-owned glass inserts.
- Zero missing or mismatched pairs.

A restrained exterior-shutter pass then added 19 side-mounted panels across ten
selected windows at SS_004, SS_005, SS_010, SS_011, SS_012 and SS_018. Timber
panels are used on civic/domestic facades and metal panels on detention,
checkpoint and telecom facades. One Detention right-hand panel was removed
before save because the audit detected overlap with `Detention_Door_12`; its
remaining left panel is an intentional asymmetric detail. The final audit
reports 19 actors, zero opening overlaps, zero pair overlaps, clean wall mounts
and `NoCollision` throughout.

Exactly 26 World Partition packages were saved for the shutter pass: 19 actor
packages and seven required folder-object packages. No content package, level
package, protected asset or unrelated package was saved. The 48 temporary labels
were restored, the automation write gate is closed, and the final Unreal
dirty-package count is zero.

New scripts:

- `old_town_window_opening_audit_v1.py`
- `old_town_window_shutter_builder_v1.py`
- `old_town_window_shutter_conflict_fix_v1.py`
- `old_town_window_shutter_audit_v1.py`
- `old_town_save_window_shutter_v1.py`
- `old_town_focus_window_shutter_review_v1.py`

New review export outside the Unreal repository:

- `MapDesign/Desert_Glory_Inspired/Exports/2026-08-02/OldTown_WindowShutters_Round_TeaHouse_2560x1440.png`

No Save All, project-setting change, protected-system edit, commit, push, PR,
merge, rebase or `main` update was performed in this continuation.


## Salvage Yard hand-tool continuation

The deferred `OT_SCRAP_004` scope was resolved against actual Unreal mesh bounds
and the finished SS_014 yard. The MilitaryTrench shovel mesh is natively a flat,
ground-oriented prop (approximately 98.5 x 22.2 x 14.4 cm unscaled), so no
artificial pitch or lean was required. The Scene Junkyard rusty support stand is
natively upright (approximately 226.5 x 73.4 x 113.2 cm unscaled).

Nine of the 18 planned candidates were accepted: five flat shovels and four
upright support stands. Candidates with zero or marginal clearance against
existing vehicle, hard-cover or scrap geometry were rejected rather than forced
into the yard. Every accepted actor is decorative and uses `NoCollision`.

Seven actors were lifted 4.515–8.038 cm from raw Landscape height to the visible
asphalt overlay. The final audit reports nine actors, zero support exceptions,
0–0.002 cm final support gaps, zero pair overlaps, expected flat/upright
orientation and `NoCollision` on every actor. The angled yard review confirms
that the repair-equipment silhouette and small ground tools do not obstruct
vehicle paths or cover.

Exactly 11 World Partition packages were saved: nine actor packages and two
required folder-object packages. No content package, level package, protected
asset or unrelated package was saved. The 48 temporary labels were restored,
the automation write gate is closed, and the final Unreal dirty-package count is
zero.

New scripts:

- `old_town_hand_tool_scope_audit_v1.py`
- `old_town_hand_tool_builder_v1.py`
- `old_town_hand_tool_support_fix_v1.py`
- `old_town_hand_tool_audit_v1.py`
- `old_town_save_hand_tool_v1.py`
- `old_town_focus_hand_tool_review_v1.py`

New review export outside the Unreal repository:

- `MapDesign/Desert_Glory_Inspired/Exports/2026-08-02/OldTown_HandTools_Round_SalvageYard_2560x1440.png`

No Save All, project-setting change, protected-system edit, commit, push, PR,
merge, rebase or `main` update was performed in this continuation.


## Rooftop utility-detail continuation

A bounded rooftop pass added ten non-traversable silhouette and utility accents
across five Old Town landmarks: SS_003 Pump Station, SS_007 Hotel, SS_013 Motor
Pool, SS_015 Storage Depot and SS_018 Telecom. Each selected roof received one
official Scene Junkyard rusty fan and one Epic basic-cylinder metal mast. SS_006
Water Tower was intentionally excluded because it already has four tower-utility
actors and its landmark silhouette is protected from unnecessary clutter.

The final audit reports:

- Ten actors across five sites.
- Exact 0 cm contact with each verified roof surface.
- Minimum roof-edge clearance of 539.502 cm.
- Zero prop-to-prop overlaps.
- `NoCollision` on every rooftop detail actor.

Exactly 16 World Partition packages were saved: ten actor packages and six
required folder-object packages. No content package, level package, protected
asset or unrelated package was saved. The post-save dirty-package count was zero.

New scripts:

- `old_town_rooftop_utility_builder_v1.py`
- `old_town_rooftop_utility_audit_v1.py`
- `old_town_save_rooftop_utility_v1.py`
- `old_town_focus_rooftop_utility_review_v1.py`

New review export outside the Unreal repository:

- `MapDesign/Desert_Glory_Inspired/Exports/2026-08-02/OldTown_RooftopUtility_Round_SS013_2560x1440.png`

## Landmark-sign continuation

Nine readable navigation signs were added to the first-draft Old Town landmarks:
SS_004 Tea House, SS_005 Clinic, SS_007 Hotel, SS_010 Detention, SS_011
Checkpoint, SS_013 Freight, SS_014 Salvage, SS_017 Bazaar and SS_018 Telecom.
Each site uses one collision-disabled Epic basic-cube sign board with the existing
map-owned `MI_OT_Accent` material and one TextRender actor. No new content asset
was created.

The initial close Clinic review showed that the text was too small to read at a
useful viewing distance. Before saving, all nine text actors were centered on
their boards, raised from 18 cm to 28 cm world size and placed 7 cm outward from
the board origin. The second close review confirmed that `CLINIC` was centered,
outward-facing and readable.

The final audit reports:

- 18 actors across nine sites: nine boards and nine text actors.
- The expected text at every landmark.
- Board-to-wall mount gaps of 0–2 cm.
- Zero door, window or gate overlaps.
- The expected accent material on every board.
- `NoCollision` on every board.

Exactly 28 World Partition packages were saved: 18 actor packages and ten
required folder-object packages. No content package, level package, protected
asset or unrelated package was saved. The 48 temporary navigation labels were
then restored without dirtying packages. The final Unreal audit reports zero
dirty content packages and zero dirty map packages, and the automation write gate
is closed.

New scripts:

- `old_town_landmark_sign_builder_v1.py`
- `old_town_landmark_sign_text_finish_v1.py`
- `old_town_landmark_sign_audit_v1.py`
- `old_town_save_landmark_sign_v1.py`
- `old_town_focus_landmark_sign_review_v1.py`

New review export outside the Unreal repository:

- `MapDesign/Desert_Glory_Inspired/Exports/2026-08-02/OldTown_LandmarkSigns_Round_Clinic_2560x1440.png`

No Save All, project-setting change, protected-system edit, commit, push, PR,
merge, rebase or `main` update was performed in these continuations.


## Facade utility-detail continuation

A fresh 20-site coverage audit found electrical boxes and cabinets already in
place but no tagged `OT_UTIL_005` facade conduit treatment. A bounded map-owned
utility pass therefore added two accents to each of eight building sites:
SS_004, SS_005, SS_007, SS_010, SS_011, SS_012, SS_017 and SS_018. The 16 actors
reuse Epic's basic cube mesh and the existing `MI_OT_Metal` material; no new mesh
or material asset was created. Each building receives one vertical run and one
horizontal run, with all actors set to `NoCollision`.

The dry run resolved all 16 planned mounts after replacing one SS_017 candidate
that was 15.37 m from the relevant bazaar facade. The final audit reports:

- 16 actors across eight sites.
- Exactly 1.5 cm facade clearance for every actor.
- Zero door, window or gate overlaps.
- Zero conduit-to-conduit overlaps.
- The expected Old Town metal material on every actor.
- `NoCollision` on every actor.

Exactly 25 World Partition packages were saved: 16 actor packages plus nine
required folder-object packages. No content package, level package, protected
asset or unrelated package was saved. The final dirty-package audit reports zero
dirty packages and the automation write gate is closed.

New scripts:

- `old_town_facade_conduit_builder_v1.py`
- `old_town_facade_conduit_audit_v1.py`
- `old_town_save_facade_conduit_v1.py`
- `old_town_focus_facade_conduit_review_v1.py`

New review export outside the Unreal repository:

- `MapDesign/Desert_Glory_Inspired/Exports/2026-08-02/OldTown_FacadeConduit_Round_SS004_Angled_2560x1440.png`

No Save All, project-setting change, commit, push, PR, merge, rebase or `main`
update was performed in this continuation.
