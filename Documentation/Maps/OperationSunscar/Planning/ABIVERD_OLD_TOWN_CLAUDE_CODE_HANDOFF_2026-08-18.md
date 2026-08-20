# Abiverd / Old Town map — Claude Code handoff — 2026-08-18

## Read this first

This document hands the current Abiverd / Old Town map-development work from
Codex to Claude Code. It is an orientation and safety document, not a claim
that the map is visually complete.

The most important current truth is:

- The phase-one playable-area buildings are **not in user-accepted pre-review
  condition**.
- Earlier automated audits called several categories "accepted" or
  "complete," but Jason's August 17 screenshots visibly disprove that as an
  art-quality conclusion. Those words only describe the outcome of the
  scripted checks that were run.
- There are obvious floating, detached, oversized, misaligned, repeated and
  prototype-looking architectural pieces. Jason is beginning a manual cleanup
  pass and wants the assistant to learn from his before/after examples, then
  correct the remaining phase-one playable area.
- Do not tell Jason that all buildings are finished merely because the older
  audit reports passed.

The full chronological Codex work log is in:

`Documentation/Maps/OperationSunscar/Planning/ABIVERD_OLD_TOWN_PAUSE_HANDOFF_2026-08-05.md`

That file is approximately 2,945 lines and contains exact actor names,
transforms, package behavior, script/report paths and dated batches through
August 17. It is currently modified and uncommitted. Read it after this file.

## Exact repository, worktree, project and map

### Main clone — do not use for map editing

- Path: `/Users/jasonteck/UnrealEngine/TacticalMovement_UE58`
- Current branch at handoff verification: `main`
- Current HEAD at handoff verification:
  `cf562a0e1eb88f04a3e02a504fbb2b33f54823a4`
- The main clone contains an untracked `AGENTS.md` that belongs to Jason. Do
  not move, edit, delete, stage or commit it.
- Movement and UI work stay outside this map task.

### Isolated map worktree — use this and only this

- Path: `/Users/jasonteck/UnrealEngine/_worktrees/map-development`
- Branch: `feature/map-development`
- Local HEAD: `e0b856c20cdad11f7057248c851d4d344f43fbe1`
- Remote tracking tip: `origin/feature/map-development`
- Remote hash: `e0b856c20cdad11f7057248c851d4d344f43fbe1`
- Project:
  `/Users/jasonteck/UnrealEngine/_worktrees/map-development/TacticalMovement.uproject`
- Level: `/Game/Maps/Blockout/Lvl_Blockout_01`
- Unreal Engine: 5.8.1
- Xcode selected for UE 5.8 work:
  `/Applications/Xcode_26.1.1.app/Contents/Developer`
- Selected Xcode version was verified as Xcode 26.1.1, build 17B100.

At the time this handoff was written, no real UnrealEditor process was running
for the project and nothing listened on TCP port 8000. Only Apple's
`UnrealEditorServices` helper process was present. Recheck live state rather
than assuming this remains true.

## Critical Git state — local work is not committed

Verified live in the isolated map worktree on 2026-08-18:

- Branch: `feature/map-development`
- Local/remote base hash: `e0b856c20cdad11f7057248c851d4d344f43fbe1`
- Staged files: **0**
- Tracked modified files: **927**
- Untracked files before adding this handoff: **80**
- Total status entries before adding this handoff: **1,007**
- Current tracked modified files after documentation work: **927**
- Current untracked files: **83**
- Current total status entries: **1,010**
- The three documentation additions above the 1,007-file map baseline are
  this consolidated handoff, its exhaustive live Git/LFS manifest, and the
  read-only phase-one defect register authored by Claude Code.
- No Codex stage, commit, push, merge, rebase, cherry-pick or PR was performed.

The current map exists in the unstaged working tree. Git cannot reconstruct
the current map from `e0b856...`; that commit is only the migration starting
checkpoint. Do not run checkout, reset, clean, restore, stash, destructive LFS
commands or any operation that discards local files. Do not switch branches.

The status count grew from the older 912-modified/80-untracked checkpoint to
927-modified/80-untracked after Jason used Unreal's requested physical-material
rebuild for the Landscape. Unreal had warned that 16 Landscape actors with
physical materials needed rebuilding. The rebuild completed, but its exact
new package subset has not been individually attributed beyond the current
live Git delta. Treat all current files as intentional until audited.

### Modified tracked non-external-actor files

Most modified files are World Partition external actor packages. The tracked
modified files outside `Content/__ExternalActors__` and
`Content/__ExternalObjects__` are:

1. `Content/Maps/Sunscar/Art/Heritage/Architecture/StructureStoneS06/MI_ABV_StructureStoneS06.uasset`
2. `Content/Maps/Sunscar/Art/Heritage/Materials/M_ABV_Foliage_Masked.uasset`
3. `Content/Maps/Sunscar/Art/Materials/LandscapeV3/M_OT_Landscape_Abiverd.uasset`
4. `Content/Maps/Sunscar/Art/Quixel/CorrugatedBarrier/SM_ydxnbdns_tier_2/Materials/MI_ydxnbdns.uasset`
5. `Content/Maps/Sunscar/Art/Quixel/Sandbags/SM_ydxlcck_tier_2/Materials/MI_ydxlcck.uasset`
6. `Content/Maps/Sunscar/Art/Quixel/SandbagsSquare/SM_ydznbff_tier_2/Materials/MI_ydznbff.uasset`
7. `Documentation/Maps/OperationSunscar/Planning/ABIVERD_OLD_TOWN_PAUSE_HANDOFF_2026-08-05.md`

### Untracked non-external-actor content

1. `Content/Maps/Sunscar/Art/Heritage/Materials/M_ABV_MudStain_Decal.uasset`
2. `Content/Maps/Sunscar/Art/Heritage/Materials/M_ABV_OilStain_Decal.uasset`
3. `Documentation/Maps/OperationSunscar/Planning/ABIVERD_OLD_TOWN_CLAUDE_CODE_HANDOFF_2026-08-18.md`
4. `Documentation/Maps/OperationSunscar/Planning/ABIVERD_OLD_TOWN_LIVE_GIT_MANIFEST_2026-08-18.txt`
5. `Documentation/Maps/OperationSunscar/Planning/ABIVERD_PHASE_ONE_DEFECT_REGISTER_2026-08-18.md`

The phase-one defect register was created read-only by Claude Code after the
first Codex handoff. It contains a more exact screenshot/data reconciliation:
it identifies 1,231 prototype primitives among 1,785 actors in the saved
preflight, a systematic obsolete-parapet placement pattern, unsupported
SS_010 detention-yard walls, roof-height buttresses and a numbered 40-item
site defect register. Its measurements come from an August 12 report and are
explicit hypotheses requiring live actor re-verification before mutation.

All `.uasset` map packages are covered by the repository's Git LFS
attributes. `git lfs status` showed no staged objects. Do not assume that an
untracked `.uasset` is disposable; many are intentional new external actor or
external object packages.

Recommended first read-only commands for Claude Code:

```sh
cd /Users/jasonteck/UnrealEngine/_worktrees/map-development
git branch --show-current
git rev-parse HEAD
git rev-parse origin/feature/map-development
git status --short
git diff --stat
git lfs status
```

Do not pipe the status into a cleanup or restore command.

## Protected boundaries

Do not modify:

- `main` or the main clone's working tree
- Movement, custom CMC, saved moves/network prediction, readiness,
  first-person weapon/animation, UI, diagnostics or production work
- gameplay authority, firing, reload, weapon, animation or camera systems
- `DefaultEngine.ini`, startup map or project configuration to make map work
  easier
- `/Game/ThirdPerson/Lvl_ThirdPerson`
- the 288 hidden legacy ground overlay actors
- unrelated World Partition cells or actors outside the initial launch
  playable area

Do not stage, commit, push, merge, rebase, cherry-pick or open a PR unless
Jason explicitly authorizes each action. His previous broad approval to edit
the isolated map does not authorize Git publication.

## Work completed by Codex — high-level chronology

The detailed actor/package record is in the long pause handoff. The following
is the practical summary.

### 1. New-Mac and isolated-worktree setup

- Verified the repository and created/reused the isolated
  `map-development` worktree on `feature/map-development` at the exact remote
  checkpoint `e0b856...`.
- Preserved the main clone and its untracked `AGENTS.md`.
- Pulled Git LFS content in the map worktree.
- Verified local/remote hash equality, upstream and initial cleanliness.
- Read the repository instructions and the committed Abiverd handoff.

### 2. Xcode / Metal / Unreal build recovery

- Unreal initially failed during MetalRHI initialization because the selected
  Apple toolchain was unsuitable/missing the optional Metal toolchain.
- Installed official Xcode 26.1.1 side by side as
  `/Applications/Xcode_26.1.1.app` without replacing the newer
  `/Applications/Xcode.app`.
- Selected Xcode 26.1.1 using `xcode-select`.
- Completed first-launch setup and installed Apple's Metal Toolchain with
  `xcodebuild -downloadComponent MetalToolchain`.
- Verified `xcrun --find metal` and `xcrun metal --version`.
- Built `TacticalMovementEditor` for Mac Development against this exact
  `.uproject`.
- Launched the isolated project once and verified it passed MetalRHI and
  opened `Lvl_Blockout_01` without module/version mismatch.

### 3. Landscape and ground foundation

- Preserved the existing real 2017-by-2017 Landscape and the map-owned
  `M_OT_Landscape_Abiverd` texture-bombing material rather than replacing it.
- Worked on saved relief, ground material transitions, road shoulders and
  surface conformance.
- The older four-overlay defect was closed as stale/invalid: all 288
  `SunscarVisualConversionHiddenV2` overlays are hidden, and the original
  audit used a wrong cube-pivot assumption. They were left untouched.
- Jason later manually approved localized Grass weight painting on
  `LandscapeStreamingProxy_2_2_0`. The safe intent was one localized proxy,
  not a global 16-proxy weightmap import.
- A global `landscape_import_weightmap_from_render_target()` route was
  rejected because it dirtied all 16 Landscape proxies.
- On August 17/18, Jason clicked Unreal's physical-material rebuild after the
  editor warned that 16 Landscape actors needed it. Reconfirm the warning is
  gone after the next load and inspect the dirty scope before any save.

### 4. Sandbags and collision counterparts

- Corrected terrain contact for the SS_020 west and east sandbag groups and
  their collision proxies.
- Corrected the SS_010 west and east endpoints in separate bounded batches.
- The original checkpoint summarized these as 24 modified LFS-managed
  sandbag/collision external actor packages.
- Preserved intentional stacking and targeted a small natural terrain embed.
- Added one detention-yard foundation skirt as an intentional new map actor.

### 5. Roof, parapet, canopy and facade audits

- Audited visible ramps; no true floating-ramp defect was proven in that
  bounded audit.
- Identified old white beam-like pieces as hidden/superseded prototype
  parapets in some cases.
- Corrected four visible SS_003 parapets.
- Corrected the SS_004 canopy and four support poles.
- Proved four invisible obsolete SS_004 parapets retained collision, then
  changed those obsolete components to `NoCollision` and disabled navigation
  relevance while leaving visible geometry unchanged.
- Audited hidden SS_003 parapet/beam candidates and retained current visible
  collision where it remained necessary.
- Audited all 17 visible doors and 40 frame/glass window pairs; the scripted
  transform/pair audit did not prove a door/window defect. This does not
  override Jason's later visual findings about the broader facades.
- Ran multiple exact-tag building-to-ground audits. SS_003, SS_013, SS_015 and
  SS_016 were reported flush by the trace method. Again, that conclusion is
  limited to the sampled floor/terrain contact and does not mean their whole
  exterior composition is good.

### 6. Heritage ruin pilot near SS_013

Created and saved a three-piece imported Epic/Quixel heritage cluster:

- `ABV_SS_013_Ruin_LowWall_V1`
- `ABV_SS_013_Ruin_Rubble_A_V1`
- `ABV_SS_013_Ruin_Rubble_B_V1`

The low wall uses the imported Historic Desert Ruin Wall Modular Set 04. The
rubble actors use the imported Structure Stone S 06 family. Existing source
materials and Nanite state were retained; source assets were not edited for
the placement.

A carved arch was evaluated but not placed because its single convex
collision shape made the opening unsuitable as a traversable landmark.

Important UE 5.8 package precedent learned here:

- A new StaticMeshActor placed in an existing ActorFolder commonly produces
  one new `__ExternalActors__` package with its component serialized inside.
- Creating a new ActorFolder hierarchy can also produce one or more
  `__ExternalObjects__` packages.
- One prior wall placement produced one actor package plus two external object
  packages. Rubble in the existing folder produced one actor package each.
- Always inspect outermost package ownership. Do not assume a fixed package
  count and do not save ambiguous dirty packages.

### 7. Seasonal poppy/grass field-edge pilot

Validated imported Epic/Quixel assets:

- `SM_FieldPoppy_VarA`, approximately 27 x 30 x 65 cm, four LODs
  919/524/242/7
- `SM_WildGrass_VarE`, approximately 41 x 36 x 18 cm, four LODs
  1538/728/540/6

Both were found non-Nanite, two-sided masked, WPO-free and collisionless.
The intended implementation is one map-owned actor with two HISM components,
never one actor per plant. The last recorded pilot used a 2,400-instance HISM
composition (960 poppies plus 1,440 grasses) and a localized ground treatment.
Reverify the live actor and actual instance counts before editing; do not rely
solely on this historical count.

Required performance policy for this vegetation:

- no collision
- no navigation influence
- no overlap events
- no replication
- no Tick
- shadows disabled for the tiny plants
- density scaling enabled when supported
- culling approximately 8,000–24,000 cm

Critical material fix:

- `M_ABV_Foliage_Masked` must have **Used with Instanced Static Meshes = true**.
- Jason manually enabled this in the Material Editor and applied/saved it.
- Without that usage flag, the same material can look valid on an ordinary
  mesh yet fail or render incorrectly on ISM/HISM foliage.
- The imported mask packing observed was R=Opacity, G=Roughness,
  B=Translucency. `Mask.R` was used for Opacity Mask with an approximately
  0.20 clip threshold.

The user correctly observed that sparse individual-looking poppies over bare
dirt did not match the reference. The desired read is seasonal red flowers
embedded in substantial low green/grass cover, with a ground surface that
belongs under the growth rather than a conspicuous bare dirt rectangle.

### 8. Large launch-area building and prop passes

Codex performed many automated batches across the initial launch sites,
including SS_003 through SS_018 site subsets. The long handoff records these
under dated headings on August 14–17. The operations included:

- shell material replacements using existing flaked paint, cracked mud,
  sandstone/silt, ruin brick and other map-owned materials
- roof material variation on selected heritage buildings
- parapets, canopy poles, thresholds and small foundation/contact treatments
- window-frame navigation cleanup
- collision/nav/overlap/tick/replication normalization on decorative props
- market/bazaar counters, awnings and stall pieces
- utilities, facade meters, conduits, rooftop vents, barrels, switchgear,
  antenna/ladder/water-tower pieces
- courtyard walls, benches, planters and micro-props
- road/ground-contact accents and restrained mud/oil decals
- replacement of several prototype materials and cleanup of small decorative
  shadow casting
- HLOD-participation read-only checks, duplicate checks and route/spawn checks

Many changes were applied in exact World Partition external-actor batches and
physically saved. However, the scale of the resulting working tree is now 927
tracked modifications plus 80 untracked files. Claude must audit the actual
visual result, not assume the high actor count represents quality.

### 9. Route, spawn and performance reports

The scripted closing reports claimed:

- 50 audited Old Town gameplay routes passed, narrowest 300 cm
- all eight loaded PlayerStarts had Landscape support and at least 800 cm
  pairwise spacing
- four attacker overlap results were the intentional attacker extraction
  trigger rather than physical blockers
- no loaded NavMeshBoundsVolume/RecastNavMesh was available; AI/navigation is
  therefore not proven by these reports
- loaded launch actors participated in the expected runtime grid/HLOD policy
- no duplicate visible launch geometry was found at the script's exact
  transform tolerance

These are useful technical checks, not a visual-quality acceptance.

## What the August 17 screenshots show is still wrong

Jason supplied 20 screenshots on the Desktop. Their exact paths begin with:

`/Users/jasonteck/Desktop/Screenshot 2026-08-17 at ...`

Times range from 8.10.38 AM through 8.26.01 AM. Inspect every image before
making another broad pass. The main visible defects are:

1. Interior ceiling/wall light leaks, a panel obstructing a doorway and very
   dark/unfinished interior composition.
2. Leaning or oversized doorway surrounds, floor/threshold gaps, floating
   white trim and dark placeholder-like window panels.
3. A long green/blue two-storey shell whose upper volume appears to float on
   repeated blocks, with exposed seams, scattered window trim, a cyan strip
   and an oversized roof cap.
4. Large gray wall/beam panels in the compound that float or cantilever far
   beyond plausible supports.
5. Market awnings and fabric pieces floating away from their supports;
   plinth/bench-like blocks do not align with the facade.
6. A blue two-storey building with a bad upper/lower seam, uneven roof edge,
   crooked awnings, an oversized roof post/chimney and a white side-wall
   overhang.
7. The checkpoint building has a very long roof beam extending far beyond the
   building, a detached long ramp/beam and front columns/supports that do not
   visually connect.
8. Numerous distant exploded-looking ramps, slabs and blocks appear above the
   landscape. Some may be outside the phase-one area or editor helpers; use
   Game View and runtime inspection to classify them. Do not dismiss nearby
   visible geometry as a helper without proving it.

Jason's immediate plan is:

1. Make a few small manual corrections himself.
2. Capture before/after screenshots.
3. Have Claude compare them to learn the intended visual standard.
4. Have Claude continue the remaining corrections in the phase-one playable
   area only.

Do not do another mass scripted "completion" pass before that visual feedback
loop.

## Manual Unreal controls already given to Jason

Jason is using a Mac trackpad.

- Mac immersive viewport: `Command+F11`; depending on keyboard settings,
  `Command+Fn+F11`.
- Trackpad secondary click: two-finger click.
- Fly navigation: hold secondary click and use W/A/S/D; Q/E down/up.
- Focus selected: `F`.
- Toggle Game View/editor helpers: `G`.
- Move: `W`; rotate: `E`; scale: `R`.
- Red/green/blue gizmo axes are X/Y/Z.
- Globe icon toggles world/local transform orientation.
- Duplicate while moving: hold `Option` and drag a move axis.
- Duplicate in place: `Command+W`.
- Flip a normal architectural piece by setting Yaw +180 degrees. Avoid
  negative scale unless mirror behavior has been verified.
- Undo: `Command+Z`.
- Save the explicitly intended package/level only; avoid Save All.

Recommended snap while manually correcting:

- 10 cm translation for large architectural placement
- 1 cm translation for final seams and contact
- 10 or 5 degrees rotation for coarse alignment
- 1 degree rotation for final alignment
- disable coarse 0.25 scale snapping for delicate fitting

## Unreal automation and stability hazards

These rules were learned through repeated real failures and must be preserved.

### Never use World Partition scripting to load or intersect regions

World Partition descriptor intersection, scripted region loading and similar
spatial descriptor APIs repeatedly pinned UnrealEditor at full CPU and killed
the local bridge. Do not use them.

Safe method:

- Jason manually loads a small region in the World Partition Editor UI.
- After the region is loaded, use ordinary already-loaded actor access.
- Resolve exact labels/tags immediately.
- Avoid a broad all-world actor query.

### Keep editor queries small

- Query no more than about 10 target actors at a time.
- Prefer one exact site/tag or exact actor list.
- Avoid broad combined roof/canopy/door/window scans.
- For terrain validation, use a tiny fixed set of direct world traces, usually
  no more than eight, and record returned actor/class/Z.
- Do not build a world-derived ignore list by enumerating everything.
- Stop after the first sign of a query stall; do not retry blindly.

### Use the existing bridge only

- The documented local editor/MCP bridge listens on `127.0.0.1:8000` when
  healthy.
- Do not create a new automation bridge.
- Do not send blind commands to Unreal's console or repeatedly attempt focus,
  backspace and Return combinations.
- Do not launch a second Unreal instance.

### Exact-save discipline

- Check authoritative package-level dirty state before every mutation.
- Mutate a small named batch.
- Enumerate the exact actor and external-object packages after mutation.
- Stop if any unrelated package is dirty.
- Save only the exact object paths/packages; never use Save All for automated
  batches.
- Confirm actual filesystem mtime/size changes and Git scope; a bridge success
  flag alone is insufficient.
- Recheck authoritative zero dirty after each exact save.

Some UE 5.8 component property setters modify the loaded object without
marking its external actor package dirty. For validated property-only changes,
the established fallback was
`EditorLoadingAndSavingUtils.save_packages(exact_packages, False)`, but only
after actor ownership and the exact package scope were proven.

### Rollback discipline

- Do not call `reload_packages` on a loaded World Partition external actor;
  it caused a full-CPU editor hang.
- If a preview is unsaved and must be discarded, close only the exact isolated
  editor and choose Don't Save for the known preview packages, then reopen.
- Never Save All to clear a stale dirty flag.
- In-memory orphan external-object packages may require a controlled editor
  close without saving.

### Other UE Python lessons

- `Vector.equals` in this UE 5.8 Python binding does not accept a tolerance
  argument; compare numeric components explicitly.
- Preserve full translation, rotation/quaternion and scale when changing a
  transform. Do not trust partial-transform helpers unless verified.
- Use named `unreal.Rotator` fields; positional argument ordering caused an
  incorrectly oriented decal preview.
- For material/property edits, call both `actor.modify()` and
  `component.modify()` where appropriate.
- Compare transforms using numeric values, not string representations that
  include temporary struct addresses.
- Disable motion blur in the editor session for deterministic captures and
  take a warm-up frame after teleporting the viewport. Do not persist those
  settings to config.

## Local documentation and data index

### Primary handoffs and plans

- `Documentation/Maps/OperationSunscar/Planning/ABIVERD_OLD_TOWN_PAUSE_HANDOFF_2026-08-05.md`
- `Documentation/Maps/OperationSunscar/Planning/ABIVERD_VISUAL_CONVERSION_PROGRESS_2026-08-04.md`
- `Documentation/Maps/OperationSunscar/Planning/ABIVERD_HERITAGE_EXPANSION_PLAN_V1.md`
- `Documentation/Maps/OperationSunscar/Planning/ABIVERD_HERITAGE_ASSET_AND_PLACEMENT_MANIFEST_V1.csv`
- `Documentation/Maps/OperationSunscar/Planning/ABIVERD_HERITAGE_UE_IMPORT_MANIFEST_V1.csv`
- `Documentation/Maps/OperationSunscar/Planning/OLD_TOWN_ART_PRODUCTION_PLAN.md`
- `Documentation/Maps/OperationSunscar/Planning/OLD_TOWN_ASSET_AUDIT_AND_PLACEMENT_RESOLUTION_2026-08-01.md`
- `Documentation/Maps/OperationSunscar/Planning/OLD_TOWN_EXACT_SITE_ASSIGNMENTS.csv`
- `Documentation/Maps/OperationSunscar/Planning/OLD_TOWN_SPATIAL_ASSET_METHOD.md`
- `Documentation/Maps/OperationSunscar/Planning/OLD_TOWN_UE58_LANDSCAPE_AND_BUILDING_ARCHITECTURE_2026-08-02.md`
- `Documentation/Maps/OperationSunscar/Planning/OLD_TOWN_UE_AUTOMATION_HANDOFF_2026-08-01.md`
- `Documentation/Maps/OperationSunscar/Planning/OLD_TOWN_UE_EXECUTION_PACKET.md`
- `Documentation/Maps/OperationSunscar/Planning/OldTown_AssetPathRegistry_v1.json`
- `Documentation/Maps/OperationSunscar/Planning/OldTown_FinalAssetRegistry_v1.json`
- `Documentation/Maps/OperationSunscar/Planning/OLD_TOWN_LEVEL_DEPENDENCY_CLOSURE_V1.json`

### Committed/local automation scripts

The repository contains many map automation scripts under:

`Content/Python/OperationSunscar/AutomationV1/`

The shared module is:

`Content/Python/OperationSunscar/AutomationV1/sunscar_automation_common.py`

Read scripts before running them. Do not execute a broad builder/auditor merely
because it exists. Several scripts assume a loaded region; World Partition
loading remains manual.

The generated tracked bytecode cache
`Content/Python/OperationSunscar/AutomationV1/__pycache__/sunscar_automation_common.cpython-311.pyc`
was restored to exact HEAD content after prior validation. Keep generated
cache changes out of the map delta.

### Persistent reports in the map worktree

Directory:

`/Users/jasonteck/UnrealEngine/_worktrees/map-development/Saved/OperationSunscar/Reports/`

Persistent files present at handoff:

- `abiverd_visual_conversion_preflight_v1.json`
- `abiverd_window_material_state_audit_v1.json`
- `abiverd_world_partition_load_diagnostic_v1.json`
- `abiverd_world_partition_load_region_v1.json`
- `old_town_door_proxy_audit_v1.json`
- `old_town_gameplay_route_audit_v1.json`
- `old_town_ground_overlay_conformance_audit_v1.json`
- `old_town_horizontal_surface_audit_v1.json`
- `old_town_sandbag_audit.csv`
- `old_town_sandbag_audit.json`
- `old_town_site_coverage_audit_v1.json`
- `old_town_window_opening_audit_v1.json`

### Temporary evidence

Many exact-save reports and deterministic captures were written under
`/private/tmp/abv_*` and are named throughout the long pause handoff. Examples
include:

- `/private/tmp/abv_launch_exterior_final_acceptance_v2.json`
- `/private/tmp/abv_launch_exterior_final_review_v7/`
- `/private/tmp/abv_current_world_validation_v1.json`
- `/private/tmp/abv_launch_spawn_nav_audit_v1.json`
- numerous `/private/tmp/abv_*_exact_save_v1.json` files

These paths are ephemeral. They may disappear after reboot or system cleanup.
The long handoff preserves their names, but missing `/private/tmp` evidence
does not mean the related package was never written. Revalidate from the live
map and Git status.

### Jason's visual evidence

The August 17 screenshots are on Jason's Desktop, including:

- `Screenshot 2026-08-17 at 8.10.38 AM.png`
- `Screenshot 2026-08-17 at 8.12.11 AM.png`
- `Screenshot 2026-08-17 at 8.12.49 AM.png`
- `Screenshot 2026-08-17 at 8.14.00 AM.png`
- `Screenshot 2026-08-17 at 8.15.04 AM.png`
- `Screenshot 2026-08-17 at 8.15.34 AM.png`
- `Screenshot 2026-08-17 at 8.16.12 AM.png`
- `Screenshot 2026-08-17 at 8.16.32 AM.png`
- `Screenshot 2026-08-17 at 8.16.57 AM.png`
- `Screenshot 2026-08-17 at 8.17.28 AM.png`
- `Screenshot 2026-08-17 at 8.18.32 AM.png`
- `Screenshot 2026-08-17 at 8.18.44 AM.png`
- `Screenshot 2026-08-17 at 8.19.08 AM.png`
- `Screenshot 2026-08-17 at 8.19.49 AM.png`
- `Screenshot 2026-08-17 at 8.20.20 AM.png`
- `Screenshot 2026-08-17 at 8.21.34 AM.png`
- `Screenshot 2026-08-17 at 8.22.29 AM.png`
- `Screenshot 2026-08-17 at 8.23.37 AM.png`
- `Screenshot 2026-08-17 at 8.24.11 AM.png`
- `Screenshot 2026-08-17 at 8.26.01 AM.png`

The filesystem may encode the displayed AM spacing with Unicode punctuation;
use `find /Users/jasonteck/Desktop -name 'Screenshot 2026-08-17*'` read-only if
an exact typed path does not resolve.

## Recommended Claude Code continuation

### First session — no mutation

1. Read `AGENTS.md` in the main clone and every repository instruction that
   applies to the map worktree.
2. Read this handoff.
3. Read the full August 5 pause handoff, especially the stability lessons and
   all August 16–17 sections.
4. Verify branch, local/remote hash, staged count, Git LFS and current status
   counts without modifying anything.
5. Confirm whether Unreal is closed. It was closed at this handoff.
6. Inspect all 20 August 17 screenshots.
7. Produce a phase-one-only defect register grouped by building/site and
   classify each item as:
   - verified runtime geometry defect
   - likely editor-only/helper visualization
   - outside phase-one playable area
   - needs in-editor inspection
8. Wait for Jason's manual before/after screenshots and use them to calibrate
   composition, alignment and finish quality.

### First correction pass

Use one building/site at a time. Start with the most visually broken launch
building visible in Jason's examples, not a broad category across 900 actors.

For each site:

1. Manually load only the required World Partition region if necessary.
2. Check authoritative dirty packages before changes.
3. Identify the exact actor labels, source meshes and packages for the pieces
   visible in the screenshot.
4. Capture a before view from the same player-height/facade-normal angle.
5. Fix at most a few related actors: align walls, roof pieces, supports,
   openings and awnings; remove floating and impossible cantilevers by moving
   or resizing only when the intended architecture is clear.
6. Do not delete an actor until runtime/editor-only status, package ownership
   and replacement coverage are proven. Prefer hide/rollback only with Jason's
   approval if the actor is a legacy prototype.
7. Preserve player routes, door openings, collision and cover intent.
8. Capture the same after angle plus one oblique/player-height context view.
9. Show Jason the comparison before moving to the next site.
10. Save only exact intended actor packages after dirty-scope review.

### Priority order suggested by the screenshots

1. Long green/blue two-storey facade: floating upper shell, repeated supports,
   windows/trim, roof cap and exposed seams.
2. Checkpoint exterior: oversized long roof beam/ramp and detached columns.
3. Blue two-storey building: roof edge, upper/lower seam, awnings and side-wall
   overhang.
4. Market/bazaar frontage: floating fabric awnings and misaligned plinths.
5. Compound gray wall/beam pieces: determine intended walls versus obsolete
   prototype actors, then ground/support them.
6. Interior doorway/light leak shown at 8.26.01 AM, after exterior shells are
   stable.

Keep the scope to the initial launch playable area. Do not chase distant
exploded silhouettes until exact site ownership proves they are inside that
area.

## Final accuracy statement

Verified facts in this document come from live Git/process checks, the saved
repository handoff and the work performed in the isolated editor. Historical
audit conclusions are explicitly labeled as such. The screenshots are the
strongest evidence of current visual quality, and they show that substantial
manual art/layout correction remains.

The branch has no commit containing the current work. Until Jason separately
authorizes a reviewed checkpoint commit, preserve the entire working tree and
make only small, auditable, exact-saved changes.


## Appendix A — full verbatim Codex chronology

The following is the complete prior handoff, reproduced verbatim so Claude Code does not need to reconstruct the history from references. Statements that call a category accepted or complete are historical automation conclusions and remain subordinate to Jason’s later visual review.

---

# Abiverd Old Town pause handoff — 2026-08-05

## Purpose

This is the restart document for the isolated TacticalMovement map-development
work. It records the verified repository state, completed Old Town and Abiverd
work, known defects, safety constraints, and the agreed next execution order.

The detailed chronological record remains:

- `Documentation/Maps/OperationSunscar/Planning/ABIVERD_VISUAL_CONVERSION_PROGRESS_2026-08-04.md`
- `Documentation/Maps/OperationSunscar/Planning/ABIVERD_HERITAGE_EXPANSION_PLAN_V1.md`

## Verified repository state at pause

- Worktree: `/Users/jasonteck/UnrealEngine/_worktrees/map-development`
- Project: `/Users/jasonteck/UnrealEngine/_worktrees/map-development/TacticalMovement.uproject`
- Branch: `feature/map-development`
- Level: `/Game/Maps/Blockout/Lvl_Blockout_01`
- Checkpoint commit: `dfb9ebfb0dfbbf631bf2d95d0d6e35dbdd114692`
- Checkpoint parent: `483f6e1de7a48e79b2d13e5f17a06a563fc16a0d`
- Remote branch at pause: `origin/feature/map-development` at the same
  `dfb9ebfb0dfbbf631bf2d95d0d6e35dbdd114692` commit.
- Commit title: `Checkpoint Abiverd Old Town terrain and conformance`
- The checkpoint contains exactly 536 map-only files: 436 level external
  actors, six level external objects, 28 Sunscar assets, 58 automation scripts,
  and eight documentation/heightmap-source files.
- Git LFS uploaded 470 Unreal objects totaling approximately 297 MB.
- No committed file exceeded GitHub's 100 MB limit.
- No PR, merge, rebase, squash, force push, branch deletion, or production-main
  update was performed.
- `origin/main` had advanced to
  `bbacc8cc0494d9e1d6a79041a03c152b72edc090`; it was reported but not merged or
  rebased into map development.

The staged-file allowlist used for the checkpoint had SHA-256:

`719a4504aed0797e3a959e3e27272d2cb2faf8650b1bf92bd8536fa380d9ab31`

## Intentionally excluded local files

The following files were explicitly excluded from the checkpoint and must not
be swept into a later broad staging operation:

- `Config/DefaultEditor.ini` — an unintended shared asset-viewer/editor-profile
  serialization, not an authorized map setting.
- `Content/Python/OperationSunscar/AutomationV1/__pycache__/abiverd_wrinkled_tarp_import_post_audit_v1.cpython-314.pyc`
- `Content/Python/OperationSunscar/AutomationV1/__pycache__/abiverd_wrinkled_tarp_import_v1.cpython-314.pyc`

The two `.pyc` files are generated cache artifacts. The config change remains
local and uncommitted; do not restore, delete, or commit it without explicit
direction.

## Protected boundaries preserved

- No production movement, custom CMC, saved-move/network prediction, readiness
  replication, movement-profile, first-person rendering, Infima weapon,
  animation, weapon, or gameplay-source work was included.
- `/Game/ThirdPerson/Lvl_ThirdPerson` was not overwritten or modified.
- The project default startup map and `DefaultEngine.ini` were not changed.
- Diagnostic and movement worktrees were not opened, modified, cleaned,
  switched, reset, committed, or pushed by this map checkpoint.

## Completed environment foundation

### Original isolated blockout

- Created the new World Partition level at
  `/Game/Maps/Blockout/Lvl_Blockout_01` instead of modifying the Third Person
  level.
- Established the enlarged Old Town combat layout, districts, roads, compounds,
  checkpoints, objectives, landmarks, exterior cover and initial labels.
- Preserved the tested building shells as the principal gameplay and collision
  authority while visual conversion proceeded around them.

### Landscape visual conversion

- Replaced the visible overlapping ground-tile presentation with a real
  2017 x 2017 Landscape material/layer workflow.
- Established deterministic authored coverage for arid sand, compacted earth,
  weathered asphalt, stone hardstand, roadside silt and seasonal Abiverd meadow.
- Hid obsolete planning/debug visual-ground actors where appropriate rather
  than using them as the continuous terrain surface.
- Rebuilt the four Landscape streaming proxies that requested physical-material
  maintenance. The subsequent Map Check completed with zero errors and zero
  warnings.

### Landscape relief V1

- Replaced the physically flat terrain with a real 2017 x 2017 UE 5.8
  Landscape height pass using a lossless RG16 transfer.
- Corrected the initial north/south orientation after a read-only audit showed
  the first foundation masks were mirrored.
- Added broad alluvial variation, low settlement mounds and shallow dry
  drainage forms while fading back into the authored outer terrain.
- Verified all 12 first-floor slab bottoms against the Landscape. The largest
  absolute support mismatch was 0.974 cm.
- A 195-point Old Town sample measured 32386.774–35687.894 cm: 33.0112 m of
  real terrain range.
- Saved exactly the 16 audited Landscape streaming-proxy packages.
- Preserved the rollback source at
  `Documentation/Maps/OperationSunscar/Source/Heightmaps/Sunscar_Height_2017_BaseBackup.png`.
- Final heightmap sources, previews and reports are under
  `Documentation/Maps/OperationSunscar/Source/Heightmaps`.
- The rejected temporary mesh/sphere terrain experiment was never saved.

### Ground-surface conversion and conformance

- Imported and configured the owned Quixel Historic Desert Ruin Floor Sand
  Coarse 01 source in the map-owned heritage tree.
- Reused that source for the existing `RoadsideSilt` Landscape regions at a
  verified 120 cm world-space scale without adding a redundant Landscape layer.
- Conformed exactly 288 existing road, courtyard and localized ground-overlay
  actors to the saved Landscape.
- All 288 conforming overlays use 0.8 cm visual thickness and `NoCollision`;
  the Landscape remains physical collision authority.
- Exact-saved only those 288 external-actor packages with the guarded utility
  `old_town_save_ground_overlay_conformance_v1.py`.
- The post-save audit verified 288 actors, 288 with collision disabled, zero
  dirty Unreal packages and no unexpected package.
- Authoritative local reports:
  `Saved/OperationSunscar/Reports/old_town_ground_overlay_conformance_apply_preview_v1.json`,
  `Saved/OperationSunscar/Reports/old_town_ground_overlay_conformance_audit_v1.json`,
  and
  `Saved/OperationSunscar/Reports/old_town_save_ground_overlay_conformance_v1.json`.

## Completed architecture and exterior conversion

### Structural skin

- Converted 111 building surfaces across 190 building actors to the first
  cohesive mud-brick, plaster, civic and industrial hierarchy.
- Added 76 structural-detail actors for foundation skirts, parapets,
  buttresses and restrained erosion dressing.
- Preserved the gameplay shells and their existing openings.

### Historic facade sources

- Imported and configured Historic Desert Ruin Wall Modular Set 04 and used 75
  non-colliding HISM facade instances across 25 uninterrupted P0 wall spans.
- Corrected the scan's source-axis orientation in place; no duplicate facade
  system remains.
- Imported Historic Pakistan Street Wall Brick Modular 16 as a map-owned,
  Nanite-enabled civic wall source with packed ORM and a 2K runtime texture cap.
- Added nine non-colliding HISM instances across the Clinic, Detention Annex and
  Consulate blank wall spans.
- Imported Historic Pakistan Street Window Brick Modular 04, but rejected its
  use as an opening insert after visual review showed that the complete 3.48 m
  wall bay appeared as an attached slab. All 14 unsuitable instances were
  removed and the original 28 opening cues were restored.
- The Pakistan window source remains available only for a future compatible
  complete wall-bay rebuild.

### Openings, roofs and wall transitions

- Removed 28 superseded offset prototype parapets only where complete replacement
  roof-parapet systems existed. This corrected the apparent floating-beam issue
  on seven reviewed sites.
- Added one shared warm world-aligned Consulate plaster material and applied it
  to exactly ten exterior shell pieces.
- Added the opening-surround system to nine verified doors and five open shell
  passages using 42 non-colliding HISM pieces.
- Hid two false Hotel door props that were positioned against solid walls.
- Converted 40 window recesses to a shared opaque dusty-recess treatment and
  set all 80 decorative frame/recess actors to `NoCollision`.
- Added 80 shallow lintel/sill pieces through one non-replicated two-component
  HISM actor.
- Added 167 terrain-conformed wall-foot rubble/grass instances at eight reviewed
  Old Town sites through six HISM components. Door clearance, collision,
  navigation, culling and shadow policies were audited.
- Replaced the Covered Bazaar's eight graybox canopy slabs with the owned Quixel
  Wrinkled Tarp source while preserving authored centres, a 273.092 cm minimum
  underside clearance and a 918.096 cm central passage.

## Completed Abiverd identity pass

- Added the first Juma-mosque ruin composition, archaeology walls, well court,
  eroded wall fragments and heritage landmarks.
- Added 4,200 deterministic poppy instances and 2,400 grass instances through
  one HISM vegetation actor with 16 components.
- Vegetation is non-colliding, non-replicated, does not affect navigation, and
  uses distance-culling/shadow policy suitable for a multiplayer environment.
- The heritage plan protects North Defender Insertion, requires at least three
  readable routes and does not treat vegetation as authoritative ballistic
  cover.
- The map consistently uses the spelling **Abiverd**.

## Imported and verified owned sources

The map/project or local Fab source library contains the following verified
families used or reserved for Old Town and Abiverd:

- Historic Desert Ruin Arch Stone Carved 08
- Historic Desert Ruin Wall Modular Set 04
- Historic Desert Ruin Structure Stone S 06
- Historic Desert Ruin Wall Brick 03 surface
- Historic Desert Ruin Floor Sand Coarse 01 surface
- Historic Pakistan Street Wall Brick White 01 surface
- Historic Pakistan Street Wall Brick Modular 16
- Historic Pakistan Street Window Brick Modular 04
- Cracked Mud Wall
- Field Poppy and selected Wild Grass/Dry Grass families
- Quixel Wrinkled Tarp
- Approved Epic/Quixel military trench, junkyard, vehicle and environmental
  sources already included in the map-owned dependency closure

## Performance-oriented implementation already used

- World Partition external actors and external objects for the map.
- Map-owned lightweight material masters and material instances.
- Packed ORM textures and runtime texture-resolution caps where appropriate.
- Nanite on suitable dense opaque heritage scans; not automatically enabled on
  lightweight masked foliage cards.
- HISM batching for repeated facade pieces, vegetation, opening trim and
  wall-foot dressing.
- Decorative actors use no replication, no ticking, no navigation influence
  and usually no collision.
- Tested building shells remain collision authority instead of decorative
  scans using complex collision.
- Runtime PCG generation is not planned. Vegetation generation should be
  deterministic and baked to instancing output.

## Known defects and incomplete work

### Four overlay edge-fit reviews

The saved conformance is stable, but four large overlay pieces exceed the
18 cm edge-gap review threshold and need subdivision or localized refitting:

| Actor | Maximum audited edge gap |
|---|---:|
| `Ground_Asphalt_SS_019_R1C1` | 18.693 cm |
| `Ground_Asphalt_SS_019_R1C2` | 19.861 cm |
| `Ground_Concrete_SS_009_R2C1` | 30.120 cm |
| `NorthRoute_04_02` | 19.906 cm |

`Ground_Concrete_SS_009_R2C1` is the priority. These actors are decorative and
non-colliding, so the issue is visual rather than a physical traversal defect.

### Ground material

- The Landscape is structurally real and no longer physically flat, but its
  ground material will still benefit from later macro-scale color/roughness and
  distance-aware refinement.
- **The first production cell-bombing pass is implemented, visually approved
  and saved** in
  `/Game/Maps/Sunscar/Art/Materials/LandscapeV3/M_OT_Landscape_Abiverd`.
- It reuses UE 5.8's built-in
  `/Engine/Functions/Engine_MaterialFunctions01/Texturing/Texture_Bombing`
  material function. No custom bombing function was created.
- Bombing is intentionally limited to the dominant Sand base-color path. It
  preserves the existing world-space scale, uses a 1.0 tiling multiplier and
  0.75 offset, and does not add normal-map bombing or height lerp.
- Measured material cost changed from 121 to 192 pixel instructions and from 6
  to 9 pixel texture samples. Vertex instructions remain 99 and sampler count
  remains 4. This passed the bounded preview ceilings, but representative
  runtime/GPU profiling remains required before final art lock.
- The preview eliminated 50 unreachable legacy material expressions; the saved
  graph contains 83 expressions, all reachable from active material outputs.
- The continuous Landscape material should carry the broad surface; overlays,
  decals and mesh patches should remain localized detail only.

### Architecture and gameplay-art review

- The environment is now a coherent first exterior art/design draft, not a
  final production-art pass. The bounded building-shell and grounded-exterior
  phase was completed on 2026-08-14; future work should treat vegetation,
  localized ground color, decals/storytelling and final lighting/composition as
  the next visible-quality categories rather than reopening every building.
- Tea House, Hotel, Bazaar, Motor Pool, Water Tower, Canal Pump Station,
  Freight Depot, Power Substation and Telecom Workshop now have reviewed
  exterior treatments. Final hero-asset replacement, bespoke cornices and
  selected complete wall-bay rebuilds remain optional later polish, not a
  blocker for proceeding to the next map category.
- Door/window readability, roof-parapet collision, Hotel silhouette and
  wall-foot visibility still require player-height PIE review.
- The mosque and ruins need a composition/sightline review before more ruin
  fragments are added.
- Vegetation density must be tested at the lowest supported scalability setting
  so no route depends on flowers or grass as its only protection.
- Small props, debris, decals, localized storytelling, final roads and final
  exterior dressing remain later passes.

## Stability lessons and required automation procedure

- Do not launch the editor with a persistent `-ExecutePythonScript` review
  helper or `set_keep_python_script_alive(True)`. Persistent Python execution
  repeatedly destabilized the editor.
- Use a normal editor launch and one-shot bounded scripts only.
- Prefer the following sequence for every material or actor batch:
  1. read-only preflight;
  2. bounded dry run or unsaved preview;
  3. visual and automated audit;
  4. explicit apply authorization;
  5. post-apply audit;
  6. exact-package save;
  7. Git scope audit and separately authorized checkpoint.
- Avoid monolithic scripts and large unsaved batches.
- Verified 2026-08-14: every master material rendered by an ISM or HISM must
  have **Used with Instanced Static Meshes** enabled and compiled before actor
  placement. `M_ABV_Foliage_Masked` had valid mesh instances, texture
  parameters and component settings, but rendered as dark/default cards while
  `used_with_instanced_static_meshes` was false because the required instanced
  vertex-factory shader permutation was unavailable. Recreating actors does not
  fix that material-level defect.
- Preflight the parent master material, not only its material instances and
  meshes. Verify `used_with_instanced_static_meshes == true`, apply/compile the
  material, save only that exact package, then independently read the saved
  property back and require zero dirty packages. Do not rely on
  `automatically_set_usage_in_editor`; it was true on this material while the
  required usage flag was still persisted false.
- After changing an instancing usage flag, validate a known existing HISM or a
  single unsaved preview instance before creating a full batch. Confirm that it
  no longer uses the default/dark fallback material and that the intended
  masked texture renders. This rule applies to `M_ABV_Foliage_Masked` and every
  future material used by ISM/HISM vegetation or repeated map geometry.
- The same 2026-08-14 validation found a second independent foliage-material
  defect. The imported Quixel mask packing is `R = Opacity`, `G = Roughness`,
  `B = Translucency`. Never route `Mask.B` to Opacity Mask: doing so exposes
  brown card/background fragments that can be mistaken for broken dirt below
  the plants. The exported opacity data occupies only approximately 0.0-0.31,
  so the prior 0.42 clip discarded the cards completely. The calibrated map-
  owned master uses `Mask.R` with an opacity-mask clip of 0.20; 0.10 admits
  excess antialiased fringe, while 0.20 preserves the authored silhouettes.
  Retain **Used with Instanced Static Meshes**, compile with zero errors, and
  validate both a player-height and elevated HISM capture before saving.
- For the field-edge pilot, `SM_WildGrass_VarE` is an approximately 18 cm low
  radial clump and reads as ground litter when used as the primary filler.
  `SM_WildGrass_VarA`, uniformly scaled to roughly 48-62 cm, is the validated
  tall meadow filler. A 16 m by 7 m reference-density pilot uses one actor,
  two HISM components, 960 poppies and 1,440 grass instances, with a 1.2 m
  movement corridor, 1.5 m static-geometry clearance, Landscape-only support,
  no collision/nav/overlaps/shadows/replication/tick, and 80-240 m culling.
- The remaining bare-dirt read under this pilot is not a foliage-card defect.
  Nine exact player-patch samples resolve to `LandscapeComponent_136` on
  `LandscapeStreamingProxy_2_2_0`, external-actor package
  `/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/7/PW/GCKDH3SJ6DMPX8ALJXPIKR`,
  and every sample returns `Grass` paint weight `0.0`. The saved Landscape
  material already contains the `Grass` / `AbiverdSpringMeadow` layer using
  the imported Wild Grass Ground base color and normal; the problem is local
  layer coverage, not a missing texture or material input.
- UE 5.8 exposes a safe read path for this diagnosis: trace to the
  `LandscapeHeightfieldCollisionComponent`, call `get_render_component()`,
  then call `editor_get_paint_layer_weight_by_name_at_location(Location,
  "Grass")`. For preservation, `Landscape.render_weightmap()` can export the
  existing proxy window before any edit. The validated proxy window is
  505x505 pixels covering world XY 0-63000 cm at 125 cm/pixel; exported pixel
  Y maps directly to world +Y. Never generate a replacement mask from zero or
  use a full-map import for this pilot.
- A proposed localized correction mask preserves the exported proxy weights
  and changes only 60 pixels around the 16x7 m meadow footprint, with feathered
  edges, peak Grass weight about 0.68, and a reduced-weight central trampled
  strip. Do **not** apply it through
  `LandscapeStreamingProxy.landscape_import_weightmap_from_render_target()`.
  A guarded 2026-08-14 preview proved that UE 5.8 requires a full 2017x2017
  Landscape render target even when the function is called on one streaming
  proxy; the call then dirtied all 16 loaded Landscape proxy packages while
  leaving the nine sampled pilot weights at `0.0`. No package was saved: all
  16 unsaved proxy packages were reloaded from disk and authoritative dirty
  state returned to zero. This is a proven wrong-scope import path, not a
  retryable transient failure. Use the native Landscape Paint tool for a
  localized Grass stroke and require the authoritative dirty scope to be
  exactly the proxy package above before saving; discard on any parent,
  material, other proxy, or mass-resave scope.
- Verified native-paint resolution on 2026-08-14: select the `Grass` target
  layer, set Painting Restriction to `None`, and use a bounded brush (strength
  0.22, size 800 cm, falloff 0.5). For deterministic single-dab automation,
  `Apply Without Moving` must be enabled; an instantaneous click otherwise
  produces no sample. Also re-check Painting Restriction after keyboard focus
  changes: an `End` key sent while that dropdown had focus changed it to
  `Component Allow List`, silently preventing the intended unrestricted
  stroke. The successful center dab changed only
  `LandscapeStreamingProxy_2_2_0` package
  `/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/7/PW/GCKDH3SJ6DMPX8ALJXPIKR`.
  Seven direct pre-save samples across the pilot returned Grass weights
  0.42745-0.75137 on `LandscapeComponent_136`. Leave active Paint mode (Manage
  is sufficient) before the exact save; otherwise the active paint tool can
  mark the proxy dirty again immediately after a successful write. The final
  exact proxy save remained clean, and nine post-save samples returned
  0.14118-0.75137 with authoritative Unreal dirty state still zero. Do not
  repeat the full render-target import now that the native-paint path is
  proven.
- Player-height review exposed an important visual limitation: the imported
  `Wild Grass Ground` base color used by the `Grass` Landscape branch reads
  tan/olive under the current lighting. Increasing the localized paint weights
  makes the blend measurable and somewhat greener, but it does not by itself
  create a lush seasonal meadow floor. After the bounded strengthening pass,
  the nine saved samples span 0.14118-0.89020 and only the intended
  `LandscapeStreamingProxy_2_2_0` package changed. Treat further repeated
  strokes as diminishing returns; a separately scoped material-selection or
  color-treatment decision is required if a substantially greener ground read
  is desired. Do not misdiagnose this as missing paint.
- Map-owned HISM actors created or structurally changed through editor Python
  may not build a render tree until their exact external-actor package is
  serialized and reloaded. Keep the actor root at the patch center and store
  instances relative to that local origin so World Partition bounds remain
  tight. For the field-edge pilot, unsaved bounds were a default 128 cm box;
  exact save/reload produced verified bounds of about 13.98 m by 6.87 m by
  2.99 m and activated both render components. Never leave a vegetation actor
  rooted at world origin with distant world-space instances.
- Exterior continuation on 2026-08-14 completed the first priority Hotel and
  Bazaar prototype-cue cleanup without changing either building shell. All 30
  `Hotel_F*_..._Glass` actors now use the already-approved
  `MI_OT_DustyWindowRecess` and have `NoCollision`; their timber frames and
  complete transforms are unchanged. The two cyan Hotel sign backings now use
  `MI_OT_Timber`, while `Hotel_Balcony_Rail` retains its authored transform and
  gameplay collision but uses `MI_ABV_CrackedMud_WorldAligned` as a repaired
  earthen civic parapet. The eight `Bazaar_[N/S]_Sign_*` backings likewise use
  timber and `NoCollision`; the verified Quixel cloth canopies and stall
  collision remain unchanged.
- The Hotel balcony shade pass reuses the existing Nanite Quixel wrinkled-tarp
  mesh at uniform scale 1.4 in three map-owned actors:
  `ABV_SS_007_HotelBalconyShade_West_V1`, `..._Center_V1` and `..._East_V1`.
  Their contiguous combined coverage stays within the authored balcony width,
  meets the facade within approximately 15.8 cm and preserves approximately
  251.9 cm clear height above the balcony deck. They have no collision,
  navigation, overlap events, replication or tick. Each actor serialized to
  exactly one external-actor package because the existing Municipal Hotel
  folder was reused.
- Four small Structure Stone S 06 fragments now dress the Hotel perimeter:
  `ABV_SS_007_GroundRubble_SouthWest_V1`, `..._NorthEast_V1`, `..._West_V1`
  and `..._East_V1`. Each fixed placement traced directly to a Landscape
  streaming proxy, is embedded exactly 3 cm, uses uniform scale 0.85-1.05 and
  has no collision/navigation/overlaps/replication/tick. They remain clear of
  the real south door, east opening and west access ramp. No Landscape or
  existing actor transform changed.
- The final held industrial shells were completed in four exact save batches.
  Eight `SS_003` Canal Pump Station walls and seven `SS_013` Freight Depot
  walls use `MI_OT_FlakedPaint_WorldAligned`; six `SS_016` Power Substation
  exterior wall panels now use `MI_OT_FlakedPaint_WorldAligned` and its two
  entrance lintels use `MI_OT_Metal`; and fourteen `SS_018` Telecom Workshop
  walls use `MI_OT_Stucco_WorldAligned`. The original bright Substation
  `MI_OT_WallPaint_WorldAligned` rollout was rejected during the second-pass
  player-height review because it read as sterile white blockout. Transforms,
  openings, collision, floors, roofs and traversal remained unchanged. The
  post-pass generic-shell audit returned zero remaining actors and zero dirty
  packages.
- Seven Motor Pool exterior shell actors now use
  `MI_OT_FlakedPaint_WorldAligned`, preserving the garage opening and all
  transforms/collision. The Water Tower received eight non-colliding,
  non-navigable steel cross braces plus a stucco finish on
  `Core_SS_006_TowerPillar`, making its structural silhouette readable without
  altering the four authoritative legs, tank or gameplay collision.
- `CoreWall_SouthSpawnSightbreak` remains the same authoritative tactical wall
  with the same transform and `QueryAndPhysics` collision, but its generic pale
  stone finish was replaced by `MI_ABV_RuinBrick_WorldAligned`. It now reads as
  Abiverd masonry instead of an unexplained white block in the Telecom approach.
- The final visual audit confirmed that the thin roofline rods around `SS_016`
  and `SS_018` are grounded or roof-supported utilities whose lower sections
  are merely occluded in the reviewed views; they were not moved. Previously
  verified wall-foot, scatter, furniture, storage/scrap, market-debris,
  sandbag, Hotel-rubble and SS_013 ruin systems retain their reviewed support
  state. No new grounded-transform defect was proven in the changed sites.
- Final review captures for this checkpoint are:
  `/private/tmp/abv_water_tower_after_player_v2.png`,
  `/private/tmp/abv_motor_pool_after_player.png`,
  `/private/tmp/abv_ss003_after_shell.png`,
  `/private/tmp/abv_ss013_after_shell.png`,
  `/private/tmp/abv_ss016_after_shell.png`,
  `/private/tmp/abv_ss018_after_sightbreak.png` and
  `/private/tmp/abv_old_town_exterior_final_aerial.png`.
- The second exterior-detail pass replaced the Freight Depot loading-bay cube
  on the existing `Depot_LoadingDoor` actor with the already owned Nanite
  Quixel corrugated-metal wall mesh. Its corrected 500 x 18 x 280 cm bounds
  remain exactly fitted to the authored opening, retain `QueryAndPhysics`
  collision, and now read as a deliberately sandbagged/corrugated loading-bay
  barricade. Only its existing external-actor package
  `7/MJ/BPRA9ZMO6G6ULKIKT925U3.uasset` was saved.
- Five owned Quixel wrinkled-tarp entrance awnings were added at the two Canal
  Pump Station doors, Freight Depot pedestrian door, Power Substation west
  entrance and Telecom Workshop entrance. Every awning is uniformly scaled,
  has approximately 80-90 cm clearance above its opening, meets the facade
  within approximately 10-15 cm, and has no collision, navigation, overlaps,
  replication or tick.
- Three owned Nanite Quixel electrical-box meshes now provide restrained
  facade detail at `SS_003`, `SS_016` and `SS_018`:
  `ABV_SS_003_PumpSouthElectricalBox_V1`,
  `ABV_SS_016_SubstationWestElectricalBox_V1` and
  `ABV_SS_018_TelecomSouthElectricalBox_V1`. They are shallow wall-mounted
  props with 386-449 cm clearance from the nearest opening, no collision or
  navigation, and use the established muted `MI_OT_Accent` finish so they read
  as intentional industrial equipment rather than white editor markers.
- A proposed eight-instance `Wall Modular Set 04` facade-depth batch was
  rejected and fully rolled back before final acceptance. The inherited
  `roll=90` transform assumption used the wrong asset axis/pivot and produced
  elevated L-shaped pieces. The existing HISM count was restored from 83 to 75,
  the exact package was re-saved with zero dirty packages, and no rejected
  instance remains. Future use of this heritage wall asset must validate one
  temporary instance's world bounds and visual orientation before any repeated
  placement; do not reuse that roll/pivot assumption blindly.
- Second-pass player-height review captures are:
  `/private/tmp/abv_ss013_loadingdoor_close_before.png`,
  `/private/tmp/abv_ss013_loadingdoor_close_after.png`,
  `/private/tmp/abv_ss003_detail_final.png`,
  `/private/tmp/abv_ss016_detail_final.png` and
  `/private/tmp/abv_ss018_accent_final.png`.
- UE 5.8 Python does not expose
  `StaticMeshComponent.set_generate_overlap_events()`. For map-owned static
  mesh actors, use
  `component.set_editor_property("generate_overlap_events", False)` and read
  the property back when overlap suppression is part of the performance gate.
  A method-name failure can leave the just-spawned actor dirty in memory; reuse
  and complete that exact actor only after proving its actor package is the sole
  dirty package, rather than spawning a duplicate.
- UE 5.8 Python also does not expose
  `StaticMeshComponent.set_can_ever_affect_navigation()`. Use
  `component.set_editor_property("can_ever_affect_navigation", False)` and read
  that property back. A method-name exception after spawning can leave the
  actor package dirty; recover and finish the exact actor instead of spawning a
  duplicate.
- `component.set_collision_enabled(NO_COLLISION)` alone is not a sufficient
  postcondition for newly spawned map actors when a collision profile remains
  active. For a decorative actor, set actor collision disabled, set the
  component profile to `NoCollision`, set collision enabled to
  `NO_COLLISION`, then verify `get_collision_enabled()` returns `NO_COLLISION`.
  `collision_profile_name` is not readable through `get_editor_property()` in
  this UE 5.8 Python build; use the supported profile setter and verify the
  effective collision mode instead.
- Epic Games Launcher crash-reporter popups observed during earlier asset work
  were separate from the isolated TacticalMovement editor process.

## 2026-08-14 all-building exterior completion checkpoint

- The authorized Old Town exterior first-art/design-draft pass is complete for
  all 13 building sites: `SS_003`, `SS_004`, `SS_005`, `SS_006`, `SS_007`,
  `SS_010`, `SS_011`, `SS_012`, `SS_013`, `SS_015`, `SS_016`, `SS_017` and
  `SS_018`. This means every site has a reviewed exterior shell or, for the
  `SS_006` water-tower landmark, a completed structural/detail treatment. It
  does not claim final-production decal, lighting, HLOD or multiplayer
  performance polish.
- The live completion matrix found zero generic materials on core building
  surfaces and nonzero exterior-detail coverage at every site. Core-building
  actor counts are 10/10/15/0/22/17/17/15/9/9/10/12/17 in site order above;
  `SS_006` intentionally has no conventional core roof/wall shell because it is
  the water-tower utility landmark.
- Four additional owned Quixel wrinkled-tarp entrance awnings complete the
  cross-site entrance-readability pass:
  `ABV_SS_005_ClinicMainAwning_V1`,
  `ABV_SS_011_CheckpointDoorAwning_V1`,
  `ABV_SS_012_ConsulateDoorAwning_A_V1` and
  `ABV_SS_012_ConsulateDoorAwning_B_V1`. Together with the five earlier
  industrial awnings, the verified total is nine. All are non-colliding and
  non-navigable and preserve at least approximately 82 cm clearance above the
  authored openings.
- The placeholder cube meters `OT_EXT_Meter_SS_004`,
  `OT_EXT_Meter_SS_010` and `OT_EXT_Meter_SS_012` now reuse the owned Nanite
  Quixel `Electric_Box_ullibjd_High` mesh with `MI_OT_Accent`, no collision and
  no navigation relevance. Together with the three earlier industrial
  electrical boxes, six exact utility-detail actors passed acceptance.
- The final proven building defect was the pair of `SS_015` Motor Pool garage
  panels. `MotorPool_Garage_A` and `MotorPool_Garage_B` were 400 x 18 x 350 cm
  cubes whose bottoms sat 175 cm above the south-wall bottom and whose tops
  extended 225 cm above that wall. They now reuse the owned Nanite Quixel
  corrugated-metal mesh, retain `QueryAndPhysics` collision, and fit exact
  400 x 18 x 300 cm facade bounds from Z 34794.1 to 35094.1. The supporting
  wall and all gameplay alignment remained unchanged.
- Final acceptance report:
  `/private/tmp/abv_all_buildings_final_acceptance_v1.json`. It verified the
  exact project/map, 13 sites, zero Unreal dirty packages, nine awnings, six
  utility details, both corrected Motor Pool panels, 75 heritage facade HISM
  instances, 288 hidden legacy overlays and 26 current review images.
- The 26 player-height/aerial review images and manifest are under
  `/private/tmp/abv_all_buildings_review_v1/`. The final `SS_015` player and
  aerial images were refreshed after the garage correction. Close custom
  captures that appeared to omit walls were rejected as camera clipping; the
  matrix-view recaptures proved the facade shells intact.
- The four old overlay-edge findings remain closed as stale/invalid. All 288
  `SunscarVisualConversionHiddenV2`/`VisualGroundOverlay` actors are still
  hidden and untouched, and the former cube-pivot audit assumption must not be
  reused.
- Unreal ended with authoritative zero dirty packages. Git is intentionally
  unstaged at 134 modified files plus 34 untracked files, with zero files
  outside the approved map external actor/object packages, the approved
  `M_ABV_Foliage_Masked` material and this handoff document. Local and remote
  `feature/map-development` remain
  `e0b856c20cdad11f7057248c851d4d344f43fbe1`; no commit, push, merge or rebase
  was performed.
- The next visible-quality category should be ground integration and restrained
  seasonal vegetation expansion around the now-stable building composition,
  followed by roads/edges, decals/storytelling and final lighting/performance
  validation. Do not reopen systematic building-shell conversion unless a new
  player-height defect is specifically proven.

## 2026-08-14 initial-launch playable-area building re-audit

- The building-completion claim is intentionally limited to the initial-launch
  playable area. Its exact 13-site scope is `SS_003`, `SS_004`, `SS_005`,
  `SS_006`, `SS_007`, `SS_010`, `SS_011`, `SS_012`, `SS_013`, `SS_015`,
  `SS_016`, `SS_017` and `SS_018`. It does **not** claim completion of the
  outer/future districts or every building planned for the full map.
- A stricter second pass reviewed the launch-area exteriors from west, east and
  north player-height approaches (36 new captures), reran exact-tag shell and
  detail coverage, and sampled all four building sides against authoritative
  terrain/support geometry. The final ground-contact matrix returned zero
  flagged sites and Unreal ended with zero authoritative dirty packages.
- The stricter pass found and corrected two previously missed, player-visible
  support gaps on the rear/north and east edges of the `SS_010` detention-yard
  terrace. They are now closed by the map-owned, colliding masonry plinth actors
  `ABV_SS_010_DetentionTerrace_FoundationSkirt_North_V1` and
  `ABV_SS_010_DetentionTerrace_FoundationSkirt_East_V1`; no Landscape or
  building transform changed.
- The `SS_006` water-tower landmark received the final launch-area exterior
  upgrade: `WaterTower_Tank` now uses the already owned Quixel
  `Metal_Water_Tank_wdklears_High` mesh and its source material at uniform
  scale 4.5, and the four existing tower legs were shortened to meet the new
  tank cleanly. Their original bases, XY placement and collision were
  preserved.
- Final acceptance is recorded in
  `/private/tmp/abv_launch_buildings_final_acceptance_v2.json`; the strict
  ground-contact report is
  `/private/tmp/abv_launch_building_ground_contact_matrix_v2.json`; the 36
  approach images are in `/private/tmp/abv_launch_approach_review_v1/`.
- This is a verified **first-art/design-draft exterior completion gate** for
  the launch buildings: shells, openings, roof/parapet treatment, visible
  support/contact and primary exterior details are ready for the next outside
  category. It is not final-production decal, storytelling, lighting, HLOD or
  multiplayer-performance polish.
- After this checkpoint Git remains intentionally unstaged at 139 modified
  files plus 36 untracked files, with nothing staged. Scope remains limited to
  map external actor/object packages, the approved
  `M_ABV_Foliage_Masked` material and this handoff document. Local and remote
  `feature/map-development` both remain
  `e0b856c20cdad11f7057248c851d4d344f43fbe1`; no commit, push, merge or rebase
  was performed.
- Do not resume systematic building conversion in the outer districts during
  the initial-launch pass. The next launch-area outside work should be roads
  and ground transitions, followed by seasonal grass/flower integration,
  exterior props/decals/storytelling, then lighting, HLOD and representative
  performance validation.

## 2026-08-15 launch-area building exterior closeout

- The closeout remains limited to the initial-launch playable-area buildings:
  `SS_003`, `SS_004`, `SS_005`, `SS_006`, `SS_007`, `SS_010`, `SS_011`,
  `SS_012`, `SS_013`, `SS_015`, `SS_016`, `SS_017` and `SS_018`. It does not
  claim that future/outer-district buildings are finished.
- The 75-instance `ABV_OldTown_FacadeScan_HISM_V4` treatment was re-audited
  against the actual `Historic Desert Ruin Wall Modular Set 04` mesh. The
  asset is an L-shaped ruin fragment, not a flat facade panel. All 75 repeated
  instances produced oversized hook silhouettes and were removed from the
  HISM in reviewed batches. The exact HISM actor package was saved with an
  authoritative final instance count of zero; the actor remains available but
  empty. Do not repopulate this component unless one temporary instance first
  proves the mesh axis, pivot, world bounds and intended architectural role.
- The weak opening-free launch facades at `SS_003`, `SS_013`, `SS_015`,
  `SS_016` and `SS_017` first received one grounded masonry bay pier each by
  reusing the established `ABV_OldTown_PakistanWallFacade_HISM_V1`. A later
  route-facing refinement expanded the same component to 32 instances: six
  low piers articulate the `SS_010` detention-yard south wall, four
  full-height piers divide the `SS_011` north elevation, four full-height
  piers frame the `SS_018` north elevation and its doorway, and two additional
  end piers each complete the three-bay rhythm on the east elevations of
  `SS_015` and `SS_016`. The component uses the imported Nanite Pakistan Wall
  Modular 16 mesh and remains non-colliding/non-navigable. Every batch was
  reviewed at player height and obliquely before the same exact HISM package
  was saved.
- Twenty superseded cube parapets at `SS_004`, `SS_005`, `SS_007`, `SS_012`
  and `SS_018` are hidden in game, `NoCollision` and non-navigable. Their 20
  current `ABV_<site>_RoofParapet_<side>` replacements are visible and retain
  intended query/physics collision. The old actors were not deleted.
- The remaining placeholder facade meters at `SS_003`, `SS_013` and `SS_015`
  now reuse the owned Quixel `Electric_Box_ullibjd_High` mesh. Materials and
  scale were preserved for the source asset; all three remain decorative,
  non-colliding and non-navigable.
- The final runtime capture sweep proved seven narrow rooftop actors were
  floating because zero-based cylinder/cube pivots had been treated as
  centered: `Utility_Pipe_01`, `Utility_Pipe_02`, `Utility_Pipe_04`,
  `Utility_Pipe_05`, `Telecom_Antenna_01`, `Telecom_Antenna_02` and
  `Telecom_Antenna_03`. Exact roof/roof-box bounds showed 15-130 cm support
  gaps. Each actor was lowered without changing XY, rotation, scale, mesh or
  material and now has a verified 2 cm support embed. The four pipe packages
  and three antenna packages were saved as two bounded batches.
- Durable pivot rule: derive contact from the actor's post-transform world
  bounds (`bounds_bottom`) and the exact support actor's world top, not from
  actor location or an assumed centered mesh pivot. This applies to cylinders,
  modular ruin pieces and imported assets alike.
- UE 5.8 Python in this project does not expose
  `HierarchicalInstancedStaticMeshComponent.mark_render_state_dirty()`. The
  reviewed `add_instance` calls updated rendering without it. Treat the missing
  method as an API mismatch, verify the new instance count/transforms and
  viewport output, and do not retry by spawning duplicate instances.
- Verified in the later 32-instance refinement: `add_instance()` can update the
  in-memory HISM and viewport without adding the owning external-actor package
  to Unreal's authoritative dirty-package list. A zero-dirty result therefore
  does not prove that an HISM structural edit was serialized. After validating
  the exact component, instance count and transforms, explicitly save the one
  known owning package with
  `EditorLoadingAndSavingUtils.save_packages([actor.get_package()], False)`;
  then require a newer filesystem mtime, the expected instance count read back,
  and zero dirty packages. This is an exact-package save, not `Save All`.
- Final acceptance report:
  `/private/tmp/abv_launch_buildings_final_acceptance_v4.json`. It verifies the
  exact project/map, all 13 launch sites, nonzero shell/detail coverage, zero
  generic core materials, zero bad L-wall instances, 32 masonry-pier instances
  including the 18 exact route-facing additions,
  three upgraded meters, 20 disabled obsolete parapets, 20 visible replacement
  parapets and zero authoritative Unreal dirty packages. Current review images
  are under `/private/tmp/abv_launch_buildings_postpass_review_v1/`, with exact
  rooftop before/after evidence under
  `/private/tmp/abv_launch_rooftop_pipe_review_v1/` and
  `/private/tmp/abv_launch_telecom_antenna_review_v1/`.
- Git remains intentionally unstaged at 219 modified files plus 46 untracked
  files, with zero staged or out-of-scope paths. Local and remote
  `feature/map-development` both remain
  `e0b856c20cdad11f7057248c851d4d344f43fbe1`; no commit, push, merge or rebase
  was performed.
- This closes the launch-building **first-art/design-draft exterior gate**, not
  final-production art. Later building work should be driven by a specifically
  proven player-height defect or by the future decals/storytelling/lighting/
  HLOD passes rather than reopening systematic shell conversion. The next
  launch-area exterior category is roads and ground transitions, followed by
  restrained seasonal vegetation.

## 2026-08-15 launch-area sandstone shoulder dressing

- The first roads/ground-transition batch added 13 sparse, terrain-conformed
  sandstone shoulder/rubble pieces across the west approach, clinic lane,
  southwest lane, south spine, courtyard lane, east lane, freight edge and
  north lane. They reuse the already imported Quixel `Sandstone Rocky Ground`
  tier-2 mesh and its existing material. This is restrained roadside/open-ground
  breakup, not the final road-surface or Landscape-material pass.
- The pieces are ordinary `StaticMeshComponent`s owned by the existing
  map-only actor `ABV_OldTown_WallFoot_HISM_V1`, so the complete persisted
  scope is exactly its existing external-actor package
  `/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/E/4N/SLKIJA7PHN48GN1EYQ8W7K`.
  All 13 components are `NoCollision`, non-navigable, non-overlapping,
  non-replicated, non-ticking and non-shadow-casting. Uniform scales are
  0.58-0.72 and each piece has a 2 cm terrain embed.
- Five fixed Landscape traces were required per candidate. Thirteen candidates
  passed full Landscape support and <=11.02 cm sampled terrain variation. Three
  candidates were rejected before mutation: west approach A (18.16 cm
  variation), clinic lane A (24.45 cm) and freight edge A (one static-mesh hit
  and 234.4 cm variation).
- Two rejected implementation paths must not be repeated. Tiny trench-debris
  HISM instances read as isolated dark holes and were rolled back. Assigning
  this Quixel mesh to a HISM dirtied the shared `MI_vmjjfiv` material to add
  instanced-static-mesh usage, which was outside this batch; ordinary static
  components avoided that shared-material mutation.
- Durable editor-scripting warning: do **not** call
  `EditorLoadingAndSavingUtils.reload_packages()` in this project to clear an
  unsaved package. It stalled the editor at full CPU on both an external-actor
  package and a small material package. Recover by deleting only the known
  unsaved subobjects when safe, or close the exact isolated editor without
  saving and reopen. Never retry `reload_packages()` here.
- The exact package save changed the actor package from 54,944 to 71,272 bytes,
  advanced its filesystem mtime and returned Unreal to zero authoritative dirty
  packages. Review images are under
  `/private/tmp/abv_launch_road_sandstone_review_v1/`.
- Local and remote `feature/map-development` remain
  `e0b856c20cdad11f7057248c851d4d344f43fbe1`; nothing is staged and no commit,
  push, merge or rebase was performed. The next road pass should audit actual
  roadway boundaries and the existing visible Quixel-ground collision state,
  then return to restrained seasonal grass/flower integration.
- That collision audit then resolved all 16 exact actors in the existing
  `OldTown_QuixelPass/GroundV1` set: eight sandstone actors and eight small
  trench-patch actors were tagged `NoCollision` but were actually `BlockAll`,
  `QueryAndPhysics` and nav-relevant. This mismatch could create low invisible
  blockers and unintended navigation influence.
- The actors were corrected in two exact eight-package batches. Only the
  component collision profile/mode and navigation relevance changed:
  `BlockAll`/`QueryAndPhysics`/nav true became
  `NoCollision`/`NoCollision`/nav false. Overlap events were already false.
  Actor transforms, meshes, materials, scale, visibility and tags were
  preserved. Every package mtime advanced, both saves returned to zero dirty,
  and the repeated 16-actor audit reported `mismatch_count: 0` with all actors
  `NoCollision`, non-navigable and non-overlapping.
- UE 5.8 Python API note: this project's `StaticMeshComponent` wrapper does not
  expose `get_static_mesh()`. Read the source mesh with
  `component.get_editor_property("static_mesh")`. The first unsupported accessor
  stopped before saving and left only the first intended actor package dirty;
  the corrected idempotent script required that exact one-package subset,
  completed the eight-actor batch and saved only the expected packages.
- Collision reports are
  `/private/tmp/abv_launch_qx_ground_collision_audit_v1.json`,
  `/private/tmp/abv_launch_qx_ground_collision_fix_sandstone_v1.json` and
  `/private/tmp/abv_launch_qx_ground_collision_fix_trench_v1.json`.
- UE 5.8 Landscape-mode activation hazard observed on 2026-08-15: selecting
  `Landscape` through the editor mode combobox, without making a paint stroke,
  immediately marked both `LandscapeStreamingProxy_2_1_0`
  (`/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/1/CN/J2WBX0SOQD3OWMZSK0ZWHB`)
  and `LandscapeStreamingProxy_2_2_0`
  (`/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/7/PW/GCKDH3SJ6DMPX8ALJXPIKR`)
  dirty. This was treated as unintended in-memory scope: nothing was saved,
  the exact isolated editor was closed, and the disk/Git baseline remained
  unchanged. Before any future native Landscape paint, enter Landscape mode,
  run an authoritative package-level dirty query immediately, and proceed only
  if the result is zero or the exact intended proxy is already an explicitly
  approved target. Never accept or save proxy packages dirtied merely by mode
  activation, and never use `reload_packages()` to clear them.

## Agreed restart sequence

1. Reverify the map-development worktree, branch, current commit and current
   Unreal dirty state. Do not rebase onto the advanced `origin/main`.
2. Review the saved Landscape relief from annotated aerial and player-height
   views. Make only localized, non-destructive terrain refinements needed for
   routes, pads, drainage and sightline interruption.
3. Build the production Landscape ground-material pass, explicitly including
   world-space scale, macro variation and benchmarked cell bombing/stochastic
   variation.
4. Subdivide/refit the four flagged overlays, then re-audit roads, pads,
   building support and existing exterior actors against the final terrain.
5. Continue coherent architecture conversion in priority order: major combat
   lanes, Bazaar/Hotel, civic sites, residential compounds, perimeter structures
   and secondary utility buildings.
6. Complete doors, windows, roofs, parapets, tarps, awnings, utilities, fences,
   gates and ground transitions.
7. Review and expand the mosque/Abiverd ruins and vegetation concealment network
   without compromising spawn protection or lowest-density sightlines.
8. Add secondary props, debris, decals and storytelling after the primary
   composition is stable.
9. Run player-height PIE, collision, rooftop, sightline, traversal, shader,
   foliage, World Partition, HLOD and representative multiplayer-performance
   validation.
10. Produce high-resolution labelled and unlabelled review images, update this
    documentation and request a separate Git-checkpoint authorization.

## User review checkpoints

For efficient review, provide the user with:

- one high-resolution top-down image;
- four oblique aerial views;
- player-height views of major routes and landmarks;
- labelled and unlabelled variants;
- explicit questions about exposed routes, ridge placement, landmark position,
  historic character, entrance readability and vegetation concealment.

The user should approve large-scale composition, sightlines, landmarks and
atmosphere. Systematic micro-placement can remain automated and audited.

## Pause state

- The last verified Unreal state showed `All Saved` after saving exactly
  `M_OT_Landscape_Abiverd`. The log recorded
  `ABIVERD_EXACT_MATERIAL_SAVE True`.
- The post-save read-only audit found zero dirty packages and reconfirmed the
  saved 83-expression graph and 99/192 vertex/pixel instruction counts.
- The Landscape bombing work used a read-only preflight followed by one bounded
  unsaved preview, player-height visual review, cost/scope audit and exact-asset
  save. Unreal did not crash during this workflow.
- Added local map-only automation helpers:
  - `abiverd_landscape_cell_bombing_preflight_v1.py`
  - `abiverd_landscape_texture_bombing_preview_v1.py`
- Fixed `old_town_focus_exterior_completion_review_v1.py` so the camera-only
  helper also works when invoked through Unreal's `py exec(open(...).read())`,
  where `__file__` is not defined.
- Generated reports remain under
  `Saved/OperationSunscar/Reports/` and are not repository assets.
- No map actor, level, movement, animation, weapon, readiness, production config
  or protected gameplay asset was changed during this material pass.
- The next map work is: refit the four flagged ground-overlay edges, then resume
  Old Town exterior conversion using the already owned Quixel/Epic asset set.
- Current repository checkpoint remains
  `dfb9ebfb0dfbbf631bf2d95d0d6e35dbdd114692`; this material change, automation
  scripts and handoff update are local/uncommitted pending separate checkpoint
  authorization.
- `Config/DefaultEditor.ini` and the two Python `__pycache__` files remain
  intentionally excluded from map checkpoint scope.
- This handoff document was created after that checkpoint and is intentionally
  local/uncommitted until separate Git authorization is provided.
- The 2026-08-14 second exterior-building pass ended with the exact
  map-development project and `Lvl_Blockout_01` open, zero authoritative Unreal
  dirty packages, five verified entrance awnings, three verified facade
  electrical boxes, the Freight Depot corrugated loading-bay finish, six
  weathered Substation wall panels and two metal Substation lintels. The
  rejected heritage-wall HISM test was fully rolled back to 75 instances, and
  all 288 hidden `VisualGroundOverlay` actors remain hidden and untouched.
- Final Git scope after the completed all-building pass is 134 modified files
  plus 34 untracked files, all unstaged. The scope classifier found zero files outside external
  actor/object packages, the approved `M_ABV_Foliage_Masked` master and this
  handoff document. Local and remote `feature/map-development` both remain at
  `e0b856c20cdad11f7057248c851d4d344f43fbe1`; no stage, commit, push, merge or
  rebase was performed.

## 2026-08-15 initial-launch exterior first-art acceptance

The bounded initial-launch playable-area exterior has completed its
first-art/design-draft gate. This closes the foundational exterior-conversion
pass for the launch area; it does not claim production-final art, final HLODs,
packaged multiplayer performance certification or map-wide polish outside the
launch scope.

- Thirteen launch-area building sites passed the final exterior acceptance:
  `SS_003`, `SS_004`, `SS_005`, `SS_006`, `SS_007`, `SS_010`, `SS_011`,
  `SS_012`, `SS_013`, `SS_015`, `SS_016`, `SS_017` and `SS_018`. The scoped
  building cores contain no generic prototype materials; upgraded meters,
  fourteen masonry piers and the previously corrected/disabled obsolete
  parapets were all reconfirmed.
- All fifty loaded `CoreRoute_*` roadway/route actors resolve to the approved
  world-aligned silt, earth or asphalt treatment, with no prototype route
  material. Thirteen sandstone road-shoulder components provide restrained
  route-edge breakup without collision, navigation relevance, overlaps or
  shadows.
- Sixteen Quixel decorative ground actors were reconfirmed as visual-only:
  `NoCollision`, non-navigable and with overlap events disabled. Their meshes,
  materials and transforms were not changed by the collision correction.
- Seasonal cover is instanced and bounded: the field-edge pilot contains 2,400
  HISM instances (1,440 low-grass and 960 poppy instances), and the north
  `SS_025` meadow contains 6,600 HISM instances. Both use collisionless,
  non-navigable, non-replicated, non-ticking, shadow-disabled components with
  8,000/24,000 cm culling. `M_ABV_Foliage_Masked` retains
  `Used with Instanced Static Meshes = true`; future instanced foliage masters
  must preserve that usage flag before compiling/saving.
- A final performance audit found twenty-two collisionless HISM components that
  still generated overlap events: six on `ABV_OldTown_WallFoot_HISM_V1` and
  sixteen on `ABV_SS025_PoppyMeadow_HISM`. Overlap generation was disabled and
  exactly these two external-actor packages were saved:
  `/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/E/4N/SLKIJA7PHN48GN1EYQ8W7K`
  and
  `/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/B/AY/QGFGMVNS6FJKQ2I5W97PS6`.
  The post-save authoritative dirty-package list was empty.
- Every loaded Landscape actor uses `M_OT_Landscape_Abiverd`. The 288 hidden
  legacy `SunscarVisualConversionHiddenV2` overlays remain hidden and
  untouched; none has blocking collision. Their earlier four-edge report is
  closed as stale because it inspected hidden superseded geometry with the
  wrong cube-pivot assumption.
- The saved `SS_013` historic ruin cluster remains a distinct three-piece
  landmark/cover fragment: one low wall plus two Structure Stone S 06 rubble
  actors. Its circulation and terrain contact remain clear.
- The consolidated read-only acceptance report is
  `/private/tmp/abv_launch_exterior_final_acceptance_v1.json`. It passed all
  checks: clean context, Landscape material, hidden overlays, field-edge
  vegetation, foliage instancing, wall-foot/road shoulders, north-meadow
  performance, `SS_013` ruin cluster, core-route materials and decorative-ground
  collision.
- Final deterministic review images are under
  `/private/tmp/abv_launch_exterior_final_review_v1/`: three aerial views, four
  cardinal player-height route views and one `SS_013` field-edge view. Game View
  was enabled before the final recapture so these contain no editor selection
  overlays.
- Final repository scope is 184 modified files plus 36 intentional untracked
  files, all unstaged. The scope classifier found no unexpected path: changes
  are limited to the map's external actor/object packages, the approved
  `M_ABV_Foliage_Masked` asset and this handoff. Local and remote
  `feature/map-development` remain
  `e0b856c20cdad11f7057248c851d4d344f43fbe1`. No stage, commit, push, merge,
  rebase or mainline change was performed.

If work resumes, the next category is production polish and optimization:
hero-facade uniqueness, secondary debris/decals/storytelling, final HLOD and
World Partition review, and packaged multiplayer/performance validation. It is
not another foundational launch-area exterior conversion pass.

## 2026-08-16 SS_017 bazaar frontage storytelling polish

- The first post-acceptance production-polish batch adds four restrained props
  along the south `SS_017` bazaar frontage:
  `ABV_SS_017_Story_MetalBarrel_A_V1`,
  `ABV_SS_017_Story_Stool_A_V1`,
  `ABV_SS_017_Story_Bench_A_V1` and
  `ABV_SS_017_Story_MetalBarrel_B_V1`. They are terrain-supported, remain
  162-265 cm from the nearest stall collision bounds, and do not narrow the
  main route. All four are `NoCollision`, non-navigable, non-overlapping,
  non-replicated and non-ticking.
- The stool and bench reuse the imported owned Quixel assets. The two barrels
  deliberately reuse the already-working local `SM_Cylinder` plus
  `MI_OT_Metal` combination from `Utility_Barrel_10/11`. The imported
  `Rusty_Metal_Barrel` and `Military_Trenches_Storage_Box_Wood_S` previews
  rendered with pale/white fallback-looking materials in the launch lighting;
  they were rejected before save and must not be assumed presentation-ready
  merely because their source assets load successfully.
- UE Python `unreal.Rotator` positional construction is ordered differently
  from the intuitive `(pitch, yaw, roll)` assumption used by the first unsaved
  preview: `Rotator(0, desired_yaw, 0)` put the value in pitch. The preview was
  corrected before save with complete verified rotations. For future scripts,
  either use explicit property assignment or verify `get_actor_rotation()` and
  require pitch/roll near zero plus the exact intended yaw before saving.
- Exactly four new external-actor packages were saved, with zero additional
  external-object packages because the existing
  `OldTown_ArtDraft/CoveredBazaar` folder hierarchy was reused. The exact-save
  report is `/private/tmp/abv_ss017_storytelling_exact_save_v1.json`; player
  and oblique review captures are
  `/private/tmp/abv_ss017_storytelling_south_finalpreview.png` and
  `/private/tmp/abv_ss017_storytelling_oblique_finalpreview.png`.
- Unreal returned to zero authoritative dirty packages. Git is intentionally
  unstaged at 219 modified plus 50 untracked files, with no unauthorized paths
  and no changed hidden-overlay package. Local and remote
  `feature/map-development` remain
  `e0b856c20cdad11f7057248c851d4d344f43fbe1`; no commit, push, merge or rebase
  was performed.

## 2026-08-16 SS_011 north-frontage storytelling polish

- The second production-polish batch adds three subtle scale/story cues between
  the established north-facade masonry bays:
  `ABV_SS_011_Story_Bench_North_V1`,
  `ABV_SS_011_Story_MetalBarrel_North_V1` and
  `ABV_SS_011_Story_Stool_North_V1`. They reuse the already-approved Quixel
  bench/stool and the working local metal-barrel combination. All five support
  samples per actor hit `LandscapeStreamingProxy_2_2_0` at the same saved
  terrain elevation, with a controlled approximately 2 cm embed.
- The three actors are visual-only: `NoCollision`, non-navigable,
  non-overlapping, non-replicated and non-ticking. They sit close to the blank
  north wall between the non-colliding facade piers and remain clear of the
  east upper ramp and the open route.
- Exactly three new external-actor packages were saved and Unreal returned to
  zero authoritative dirty packages. The exact-save report is
  `/private/tmp/abv_ss011_story_exact_save_v1.json`; before/after evidence is
  `/private/tmp/abv_ss011_story_north_before.png` and
  `/private/tmp/abv_ss011_story_north_preview.png`.
- The accumulated Git scope is now 219 modified plus 53 untracked files, all
  unstaged, with no unauthorized path and no changed hidden-overlay package.
  Local and remote `feature/map-development` remain
  `e0b856c20cdad11f7057248c851d4d344f43fbe1`; no commit, push, merge or rebase
  was performed.

## 2026-08-16 SS_012 consulate-residence frontage polish

- A third distinct frontage batch adds
  `ABV_SS_012_Story_ConsulateBench_V1` and
  `ABV_SS_012_Story_ServiceCrate_V1`. The bench marks the east waiting area;
  the medium military-trench crate provides a restrained service cue at the
  west end. Both are terrain-supported with approximately 2 cm embed, retain
  visible `BlockAll` collision, do not affect navigation, do not generate
  overlaps and remain non-replicated/non-ticking.
- The post-save exact-label verification reconfirmed that the actor and its
  static-mesh component serialize inside the same external-actor package. The
  exact-save report is
  `/private/tmp/abv_ss012_story_finish_exact_save_v1.json`; the readback is
  `/private/tmp/abv_ss012_story_postsave_verify_v1.json`; player-height review
  images are under `/private/tmp/abv_ss012_story_finish_review_v1/`.
- The review also established that these two small props are secondary detail,
  not a substitute for architectural-scale facade readability. Later polish
  should prioritize lighting, entrance framing and large silhouette/detail
  hierarchy before repeating small furniture clusters.

## 2026-08-16 launch-area exterior daylight readability

- A bounded lighting audit found the unbound `Sunscar_PostProcessVolume`
  applying `-0.35 EV` exposure compensation while `Sunscar_SkyLight` used
  intensity `1.35`. Deterministic SS_005 and SS_018 captures showed the
  launch-area facade materials, opening trim and utility details collapsing
  into near-black on shadow-facing elevations.
- Two unsaved previews were compared. The accepted conservative daylight
  presentation uses Skylight intensity `2.5` and post-process exposure
  compensation `+0.15 EV`. Directional-light rotation/intensity, sky
  atmosphere, fog, Landscape, materials and geometry were not changed.
- Exactly two external-actor packages were saved:
  `/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/0/CH/4JX55GESZYZ2QOMZV08PED`
  (`Sunscar_SkyLight`) and
  `/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/9/V2/BUMGYMF2A40A1ZH2NHGIN0`
  (`Sunscar_PostProcessVolume`). The exact-save report is
  `/private/tmp/abv_launch_lighting_readability_exact_save_v1.json`; before,
  first-preview and accepted-refinement captures are
  `/private/tmp/abv_light_before_ss005.png`,
  `/private/tmp/abv_light_before_ss018.png`,
  `/private/tmp/abv_light_preview_ss005.png`,
  `/private/tmp/abv_light_preview_ss018.png`,
  `/private/tmp/abv_light_refine_ss005.png` and
  `/private/tmp/abv_light_refine_ss018.png`.
- UE 5.8 Python on this project does not expose
  `DirectionalLight.directional_light_component`, and the queried
  `SkyLightComponent` did not expose
  `lower_hemisphere_is_solid_color`. The read-only audit initially stopped on
  those accessor mismatches. Durable rule: obtain native components with
  `actor.get_component_by_class(...)` and treat nonessential version-specific
  editor properties as optional so an audit does not abort. Neither failed
  read-only attempt dirtied or saved a package.
- After the exact save, Unreal's authoritative dirty-package list was empty.
  The editor remains on the exact isolated map-development project and map.

## 2026-08-16 launch-area utility and plaza grounding polish

- The three plaza lamps now terminate naturally at the terrain and retain their
  intended lamp-head elevation. `Plaza_Lamp_02` moved from Z `35011.805` to
  `34857.6055` with Z scale `4.001995`; `Plaza_Lamp_03` moved to
  `34829.1179` with Z scale `4.286871`. `Plaza_Lamp_01` had already received
  the same bounded correction. No Landscape, road or lighting asset changed.
- The three `SS_016` roof cabinets (`Utility_Cabinet_03`, `_04` and `_05`)
  now use the owned Nanite Quixel
  `Electrical_Cabinet_ujzfde2_High` mesh at uniform scale `0.9`, with a
  controlled 2 cm roof embed, `BlockAll` collision, no navigation influence,
  no overlaps, no replication and no tick. Their saved Z is
  `35129.4151`; X positions remain `5200`, `6000` and `6800` at Y `-7200`.
- Exact reports are
  `/private/tmp/abv_plaza_lamps23_ground_exact_save_v1.json` and
  `/private/tmp/abv_ss016_roof_cabinet_upgrade_exact_save_v1.json`. Review
  images are under `/private/tmp/abv_ss016_roof_cabinet_review_v1/`.
- The refreshed 13-site completeness matrix at
  `/private/tmp/abv_all_buildings_completeness_matrix_v1.json` found zero
  generic core materials and zero sites without detail. `SS_006` remains an
  intentional water-tower form without a conventional roof; `SS_006`,
  `SS_015`, `SS_016` and `SS_017` intentionally use functional openings rather
  than standard exterior doors. This reconfirms the initial-launch building
  milestone is complete.

## 2026-08-16 SS_005 clinic frontage storytelling polish

- Two restrained, owned props now give the Old Clinic south facade a human
  service/waiting read: `ABV_SS_005_Story_ClinicBench_South_V1` and
  `ABV_SS_005_Story_ClinicServiceCrate_South_V1`. The Quixel wooden bench is
  at `(-6400,-1165,34760.5138)`; the Military Trench medium wooden crate is at
  `(-5350,-1165,34761.3397)`, yaw `8`, uniform scale `1.05`.
- Both actors are terrain-supported with exactly 2 cm embed, retain visible
  `BlockAll` collision, do not affect navigation, do not generate overlaps,
  and remain non-replicated/non-ticking. The nearest verified door clearance
  is `320.98` cm; neither approach is narrowed.
- Exactly two new external-actor packages were saved. The exact report is
  `/private/tmp/abv_ss005_clinic_story_exact_save_v1.json`; before/after
  captures are `/private/tmp/abv_ss005_clinic_story_before_v1.png` and
  `/private/tmp/abv_ss005_clinic_story_after_preview_v1.png`.

## 2026-08-16 SS_018 telecom frontage storytelling polish

- `ABV_SS_018_Story_TelecomCabinet_South_V1` adds one grounded telecom-service
  cue to the previously blank south wall. It reuses the owned Nanite Quixel
  `Electrical_Cabinet_ujzfde2_High` mesh at
  `(-6400,-10065,34779.6380)`, yaw `0`, uniform scale `0.55`, for final bounds
  about `144.10 x 48.03 x 76.32` cm.
- Five support traces hit `LandscapeStreamingProxy_1_1_0` at the same height;
  the cabinet has a controlled 2 cm embed, remains `627.95` cm from the main
  door and `77.03` cm from the existing small wall box. It uses `BlockAll`
  collision but no nav influence, overlaps, replication or tick.
- The Quixel source material read as a bright white block at ground level and
  the first `MI_OT_Accent` preview was too saturated. Only this actor's slot was
  therefore finalized with the existing weathered `MI_OT_Metal`; no shared
  mesh or material asset was edited. This preview-before-save sequence is the
  required precedent for future large utility props.
- Exactly one new external-actor package was saved. The exact report is
  `/private/tmp/abv_ss018_telecom_cabinet_exact_save_v1.json`; final review is
  `/private/tmp/abv_ss018_telecom_cabinet_metal_preview_v1.png`.

## 2026-08-16 field-edge ground-color finish and UE 5.8 material API hazard

- The saved localized `Grass` weights on `LandscapeStreamingProxy_2_2_0`
  remain unchanged. Repeated paint is still a diminishing-return path: the
  nine saved samples already span approximately `0.14118-0.89020`, and no
  additional Landscape package was dirtied in this finish pass.
- A safe targeted graph trace verified that `Grass_BaseColor` and
  `Grass_Tint` feed `MaterialExpressionMultiply_13`, whose output is the
  `Layer` input of the `Grass` `LandscapeLayerWeight` node. The tint control is
  connected; the tan/olive appearance was not a missing paint layer or broken
  material wire.
- The first tint experiments were captured before the landscape shader had
  visibly settled and therefore appeared ineffective. Durable preview rule:
  recompile the material, allow the Landscape components/shader to finish
  updating, then capture identical player-height and elevated views before
  saving. With that procedure, `Grass_Tint (0.30, 0.95, 0.28, 1.0)` produced a
  clearly greener but still semi-arid meadow footprint and preserved the
  feathered dirt transition. Exactly
  `/Game/Maps/Sunscar/Art/Materials/LandscapeV3/M_OT_Landscape_Abiverd` was
  saved; compile errors were zero and authoritative dirty state returned to
  zero. Exact report:
  `/private/tmp/abv_landscape_grass_color_exact_save_v1.json`. Saved-state and
  accepted-preview comparisons are under
  `/private/tmp/abv_field_saved_state_recovered_v1/` and
  `/private/tmp/abv_landscape_grass_color_preview_final_v1/`.
- **Do not call**
  `unreal.MaterialEditingLibrary.get_input_node_output_name_for_material_expression()`
  in UE 5.8 on this Mac/project. A read-only graph inspection caused a native
  `SIGSEGV` inside `libUnrealEditor-MaterialEditor.dylib` at
  `UMaterialEditingLibrary::GetInputNodeOutputNameForMaterialExpression`.
  Unreal was clean before the call; the post-crash process was terminated and
  the exact isolated project/map reopened with zero dirty packages. Use only
  `get_material_expression_input_names()` plus
  `get_inputs_for_material_expression()` for bounded graph tracing. The latter
  can return null entries, so filter them before dereferencing.
- The established launch-area exterior acceptance was rerun after the exact
  save and returned `verified` with 3,354 loaded actors and zero dirty
  packages. All ten gates passed: correct/clean context, Landscape material,
  288 hidden legacy overlays, field-edge HISM, foliage instancing usage,
  wall-foot/road shoulders, north-meadow performance, SS_013 ruin cluster,
  core-route materials and decorative-ground collision. Report:
  `/private/tmp/abv_launch_exterior_final_acceptance_v1.json`.

## 2026-08-16 initial-launch building interiors and thresholds complete

- The four production-critical interiors now have a restrained first playable
  art pass. `SS_010` has an intake desk, two correctly yawed stools, a holding
  bench and two warm practical lights. `SS_007` has lobby reception/guest
  furniture, one upper-room table/bench pair and three practical lights.
  `SS_004` retains its existing tea-house dressing and now has two low-intensity
  warm room lights. `SS_017` retains its market dressing and its six prototype
  stall blocks were replaced in place with the owned Quixel
  `Wooden_Table_veigfjmaw_High` mesh, producing a traversable covered-bazaar
  passage rather than six full-height white barriers.
- The other launch buildings were deliberately held to the production plan's
  readable-threshold standard rather than being over-furnished. `SS_003`,
  `SS_005`, `SS_011`, `SS_012`, `SS_013`, `SS_015`, `SS_016` and `SS_018`
  passed exact opening/furnishing inventory minima. `SS_016` remains an
  intentional functional substation without a conventional public doorway;
  `SS_006` remains the intentional water-tower traversal structure, represented
  by its loaded mid-landing rather than a conventional F1 floor.
- The final package-level launch-building gate returned `verified` with 3,370
  loaded actors and zero dirty packages. All gates passed: exact project/map,
  all 13 launch sites loaded, eight non-critical threshold treatments, seven
  critical practical lights, nine new critical furnishings, six upgraded
  bazaar stalls, clear/non-blocking `SS_003` threshold utility dressing and all
  288 hidden legacy overlays still hidden and collisionless. Reports:
  `/private/tmp/abv_launch_critical_interiors_acceptance_v1.json` and
  `/private/tmp/abv_launch_buildings_final_acceptance_v1.json`. Corrected
  threshold review captures are under
  `/private/tmp/abv_launch_threshold_review_v2/`.
- Durable UE Python rotation rule: never rely on positional construction for
  `unreal.Rotator`. Use named arguments such as
  `unreal.Rotator(pitch=0.0, yaw=15.0, roll=0.0)`, then read back and require
  the exact full rotation before saving. A positional call in the first
  `SS_010` stool preview put the intended yaw into pitch; both stools were
  corrected and exact-saved before acceptance.
- Durable external-actor mutation rule: changes to already-saved World
  Partition actors may not enter the authoritative dirty-package list unless
  both the actor and the affected component receive `modify()` before property
  mutation. The initial unsaved `SS_017` stall-mesh preview exposed this. The
  accepted pass called `actor.modify()` and `component.modify()`, required the
  exact six intended actor packages, saved only those packages and returned to
  zero dirty state.
- Deterministic `CaptureViewport` images can contain editor sprites, selection
  lines and helper visualization even with UI hidden. Do not classify those as
  runtime defects. Confirm suspicious objects by exact actor/component flags,
  collision and Game View/PIE evidence before changing map content.
- Final Git scope is intentionally unstaged: 232 modified plus 73 untracked
  files (305 total), staged count zero. Local and remote
  `feature/map-development` remain
  `e0b856c20cdad11f7057248c851d4d344f43fbe1`; no commit, push, merge or rebase
  was performed.

## 2026-08-16 launch-region optimization and HLOD readiness

- A loaded-region performance inventory covered 3,370 actors without invoking
  World Partition descriptor, intersection or scripted region-loading APIs.
  The map contains 31 HISM components and 9,321 HISM instances. Seasonal cover
  accounts for 9,000 instances; every vegetation component remains
  collisionless, non-navigable, non-overlapping, shadow-disabled,
  non-replicated and non-ticking with valid distance culling.
- Seven collisionless facade/trim HISM components still had overlap generation
  enabled. The bounded correction changed only those components across exactly
  five existing actor packages: door surrounds, Pakistan wall facade, window
  trim, Pakistan window facade and the empty facade-scan staging actor. Meshes,
  materials, instances, transforms, shadows, collision, navigation and culling
  were preserved. Exact report:
  `/private/tmp/abv_launch_facade_hism_overlap_fix_v1.json`.
- Post-save verification reduced collisionless overlap-enabled components from
  16 to nine. The nine remaining components are the eight `PlayerStart`
  collision capsules plus the unbound post-process volume brush; these are
  intentional gameplay/editor helpers and were not changed. Unreal returned to
  zero authoritative dirty packages.
- The loaded region has zero ticking actors and zero movable StaticMeshActors.
  The sole replicated actor is the engine-managed `WorldDataLayers`. Of 68
  unique StaticMeshActor meshes, 62 are Nanite-enabled. The six non-Nanite
  meshes are Engine cubes/cylinders/spheres and three CitySample vehicle LOD
  meshes; do not mutate those shared source assets merely to increase the
  Nanite count. Inventory:
  `/private/tmp/abv_launch_optimization_audit_v1.json`.
- HLOD configuration assets are present and valid:
  `Lvl_Blockout_01_HLODLayer_Instanced` is a spatial instancing layer
  (`25,600` cm cell, `76,800` cm loading range) whose parent is
  `Lvl_Blockout_01_HLODLayer_Merged`; the merged layer is a non-spatial
  mesh-merge layer (`25,600` cm cell, `51,200` cm loading range). However, the
  Asset Registry currently contains zero generated `WorldPartitionHLOD` assets
  for this map and loaded actors have no explicit per-actor HLOD override.
  Report: `/private/tmp/abv_hlod_readiness_audit_v1.json`.
- Do not run the unfiltered `WorldPartitionHLODsBuilder` on this accumulated
  uncommitted map scope. UE 5.8's full commandlet setup/build path generates
  HLOD actors for the whole world and would create a mass package delta. The
  editor supports selected-actor/selected-region HLOD filters, but the previous
  Mac failures prove scripted World Partition descriptor/filter paths can pin
  the editor. A launch-region HLOD build should be a separately controlled
  editor/UI operation after the current map checkpoint, with exact generated
  package enumeration before accepting the result.
- Current Git scope is intentionally unstaged: 235 modified plus 73 untracked
  files (308 total), staged count zero. Local and remote
  `feature/map-development` remain
  `e0b856c20cdad11f7057248c851d4d344f43fbe1`; no commit, push, merge or rebase
  was performed.

## 2026-08-16 launch PlayerStart terrain and obstruction correction

- A package-level launch-spawn audit found all eight `PlayerStart` capsules
  embedded in Landscape by approximately `0.7-46.1` cm. The north pair also
  occupied the same edge as `NorthSpawn_HistoricWall`; north start 02
  overlapped both that wall and `OT_REMAIN_SS_020_GROUND_008`. This was a
  genuine gameplay-start defect, not an editor-sprite artifact.
- `CorePlayerStart_DefenderNorth_01` and `_02` were moved from `Y=10400` to
  `Y=10180`, preserving their `X`, yaw, scale and `800` cm separation. Their
  final Z values are `34996.8632` and `34999.3364`. Five direct Landscape
  samples per capsule prove a `2` cm minimum bottom clearance; capsule overlap
  tests prove zero blockers. The final north pair has at least `180` cm
  clearance from the historic wall, and north 02 has `60.4` cm capsule-edge
  clearance from the nearby ground rock. Reports:
  `/private/tmp/abv_north_spawn_target_preflight_v1.json` and
  `/private/tmp/abv_north_spawn_fix_exact_save_v1.json`.
- The four attacker starts and two south defender starts retained their exact
  XY positions, rotations and scales. Only Z was corrected by `+8.10` to
  `+39.73` cm according to five direct Landscape samples per actor, targeting
  `2` cm clearance above each local maximum. Their only remaining overlap is
  the four attackers' intentional `CoreVolume_AttackerExtraction` trigger;
  no solid blockers remain. Reports:
  `/private/tmp/abv_remaining_spawn_z_preflight_v1.json` and
  `/private/tmp/abv_remaining_spawn_z_fix_exact_save_v1.json`.
- Final full acceptance verifies eight starts, Landscape support under every
  capsule, positive center-point bottom clearances of approximately
  `2.46-7.40` cm, minimum inter-start spacing above `800` cm and zero
  authoritative dirty packages. Report:
  `/private/tmp/abv_launch_spawn_nav_audit_v1.json`.
- No `NavMeshBoundsVolume` or `RecastNavMesh` is loaded for the launch region.
  This is recorded as an AI-navigation readiness gap, not addressed in this
  map-only spawn pass. Add/build navigation only as a separately bounded slice
  after confirming the launch AI requirements and intended traversal volume.
- The corrected north-spawn review exposed `NorthSpawn_HistoricWall` as a
  visually flat `20 m x 0.5 m x 3 m` prototype cube using warm stucco. Its
  material slot was upgraded, without any transform or collision change, to
  the existing world-aligned
  `MI_ABV_RuinBrick_WorldAligned`. This removes the stretched/plain slab read
  while preserving `BlockAll`, static mobility, navigation relevance, no
  overlap events and both corrected north spawn transforms. Exact report:
  `/private/tmp/abv_north_spawn_wall_material_exact_save_v1.json`; matching
  before/after views are under `/private/tmp/abv_north_spawn_review_v1/`.
- UE 5.8 Python can return `None` rather than an empty array from
  `SystemLibrary.capsule_overlap_actors()`. Every bounded audit must normalize
  that result with `or []` before iteration; the first acceptance attempt
  stopped read-only on this API behavior and changed nothing.
- Current Git scope is intentionally unstaged: 244 modified plus 73 untracked
  files (317 total), staged count zero. Local and remote
  `feature/map-development` remain
  `e0b856c20cdad11f7057248c851d4d344f43fbe1`; no commit, push, merge or rebase
  was performed.

## 2026-08-16 SS_007 Hotel hero-facade and decorative-collision pass

- A current player-height review confirmed that the Hotel's pale upper shell
  remains a useful civic-landmark cue, but the entire south ground storey read
  as another flat blue-white slab. Exactly the three south-facing F1 shell
  actors (`Core_SS_007_F1_S_Left`, `_Lintel` and `_Right`) now reuse the
  existing world-aligned `MI_ABV_RuinBrick_WorldAligned` material. Transforms,
  collision, navigation and the upper floors were preserved. This produces a
  believable repaired/exposed masonry base without moving the gameplay shell.
  Exact report:
  `/private/tmp/abv_ss007_south_groundstorey_material_exact_save_v1.json`;
  before/accepted preview captures:
  `/private/tmp/abv_hotel_hero_before_south.png` and
  `/private/tmp/abv_hotel_groundstorey_preview_south.png`.
- Four unsaved Pakistan Wall Modular 16 HISM instances were previewed on two
  uninterrupted Hotel side-wall spans. Visual review rejected them because
  the complete storey-height scans again read as attached tan slabs rather
  than integrated repairs. Indices `32-35` were removed, the component was
  restored to its exact 32-instance baseline, and no rejected instance was
  persisted. UE 5.8 Python does not expose `Package.set_dirty_flag(False)`, so
  the restored actor package was exact-saved solely to clear the stale preview
  dirty flag. Rollback report:
  `/private/tmp/abv_ss007_pakistan_side_facade_rollback_v1.json`.
- The live Hotel opening audit exposed a policy mismatch: all 15 decorative
  cube window frames still used Query-and-Physics collision, and all 30 south
  frame/recess cues were navigation-relevant despite the handoff's intended
  collisionless decorative treatment. Exactly those 30 actors now have actor
  collision disabled, component `NoCollision`, navigation relevance disabled
  and overlap events disabled. Every mesh, material, transform and visible cue
  was preserved; the building shell remains the only authoritative collision.
  Exact report:
  `/private/tmp/abv_ss007_window_cue_collision_exact_save_v1.json`.
- The three Quixel wrinkled-tarp balcony shades were re-reviewed at their saved
  `1.4` scale and at a smaller `1.1` preview. In both cases this particular
  scan read as dark rock-like debris overhead rather than fabric. The accepted
  correction restores their original transforms but hides only those three
  visual actors in editor/runtime; they remain collisionless, non-navigable
  and available for a later suitable awning replacement. The balcony deck,
  rail, sign and gameplay shell were not changed. Exact report:
  `/private/tmp/abv_ss007_balcony_shade_hide_exact_save_v1.json`; accepted
  player-height view:
  `/private/tmp/abv_hotel_shade_hidden_preview_south.png`.
- Durable UE 5.8 scripting notes: Python `Transform` wrapper equality is not a
  reliable transform-preservation check; compare the nine numeric
  location/rotation/scale components. A HISM component has no Python
  `get_static_mesh()` method in this build; read its `static_mesh` editor
  property instead.
- Current Git scope is intentionally unstaged: 262 modified plus 73 untracked
  files (335 total), staged count zero. Local and remote
  `feature/map-development` remain
  `e0b856c20cdad11f7057248c851d4d344f43fbe1`; no commit, push, merge or rebase
  was performed.

## 2026-08-16 SS_011 Checkpoint and SS_010 detention-perimeter polish

- Current player-height and oblique review of SS_011 proved that the two pale
  vertical pieces on its south approach are the intentional grounded vehicle
  gate posts, not floating facade geometry. Their transforms, collision and
  navigation behavior remain unchanged. Only their placeholder-looking pale
  metal finish was changed to the existing `MI_OT_Timber`, which reads as a
  weathered local checkpoint structure and no longer resembles two white
  editor markers. Exact report:
  `/private/tmp/abv_ss011_gatepost_timber_exact_save_v1.json`; accepted review
  captures are under `/private/tmp/abv_ss011_current_review_v1/`.
- The same SS_011 audit confirmed the long overhead shade edge belongs to the
  existing checkpoint composition and the two gate posts have valid terrain
  contact (actor bottoms about `2-3` cm above the sampled local ground). No
  crossbar, new collision or route obstruction was added.
- SS_010's six detention-yard perimeter wall actors still used the flat teal
  prototype `MI_OT_Detention` material and dominated every exterior approach.
  A bounded comparison tested both existing Abiverd cracked-mud and ruin-brick
  world-aligned materials. The accepted result uses
  `MI_ABV_RuinBrick_WorldAligned` on exactly
  `Core_DetentionYard_F1_E_Left`, `_E_Right`, `_N_Wall`, `_S_Left`, `_S_Right`
  and `_W_Wall`. It preserves all transforms, collision, navigation, openings,
  doors and traversal while giving the enclosure a credible historic masonry
  read. Exact report:
  `/private/tmp/abv_ss010_yard_wall_ruinbrick_exact_save_v1.json`; accepted
  current review captures are under `/private/tmp/abv_ss010_current_review_v1/`.
- Current Git scope is intentionally unstaged: 270 modified plus 73 untracked
  files (343 total), staged count zero. Local and remote
  `feature/map-development` remain
  `e0b856c20cdad11f7057248c851d4d344f43fbe1`; no commit, push, merge or rebase
  was performed.

## 2026-08-16 launch-building exterior consistency and bad-awning cleanup

- The imported Quixel `WrinkledTarp` scan was re-evaluated across the launch
  buildings. At several small entrance/balcony scales it reads as a dense black
  rock slab rather than fabric. Six individually verified bad instances are now
  hidden in editor/runtime with `NoCollision` and no navigation relevance while
  preserving their transforms for a later replacement: the SS_005 Clinic main
  awning, SS_010 detention-yard gate awning, SS_011 checkpoint door awning,
  both SS_012 Consulate door awnings and the SS_016 Substation west awning.
  Existing building shells, doors, traversal and shared source assets were not
  changed. Reports:
  `/private/tmp/abv_launch_bad_awning_hide_exact_save_v1.json`,
  `/private/tmp/abv_ss012_door_awning_hide_exact_save_v1.json` and
  `/private/tmp/abv_ss016_bad_awning_hide_exact_save_v1.json`.
- The SS_003 pump awnings, SS_013 depot awning and SS_018 telecom awning were
  retained after current visual review because their thin edge-on placement is
  plausible. The SS_017 Bazaar canopy system was deliberately excluded from
  blanket cleanup because it is a multi-piece market composition rather than
  the same isolated entrance defect.
- The Clinic now has a coherent weathered ground-storey band on every exterior
  side. Its three south F1 shell actors and the five remaining east, north and
  west F1 shell actors reuse the existing world-aligned
  `MI_OT_FlakedPaint_WorldAligned`; all upper-storey stucco, openings,
  transforms and authoritative collision remain unchanged. Reports:
  `/private/tmp/abv_ss005_south_groundstorey_flakedpaint_exact_save_v1.json`
  and
  `/private/tmp/abv_ss005_clinic_groundstorey_wrap_flaked_exact_save_v1.json`.
  Accepted wrap views are under
  `/private/tmp/abv_ss005_clinic_groundstorey_wrap_flaked_preview_v1/`.
- SS_004's previously featureless 18 m north wall now uses the existing
  `MI_ABV_CrackedMud_WorldAligned` material, matching its Abiverd mud-plaster
  character without changing its transform, collision or north foundation
  skirt. Exact report:
  `/private/tmp/abv_ss004_north_wall_crackedmud_exact_save_v1.json`; accepted
  view: `/private/tmp/abv_ss004_north_crackedmud_preview_v1.png`.
- Two blank service/rear elevations were upgraded with the existing
  `MI_ABV_RuinBrick_WorldAligned`: the SS_011 checkpoint north F1 wall and the
  SS_017 Bazaar south wall. The checkpoint now reads as a brick lower course
  below weathered plaster and its existing masonry parapet; the Bazaar keeps
  every stall and clearance while gaining a legible masonry service wall.
  Exact report:
  `/private/tmp/abv_launch_blank_rear_walls_ruinbrick_exact_save_v1.json`;
  accepted views are under
  `/private/tmp/abv_launch_rear_walls_ruinbrick_preview_v1/`.
- SS_018's north ground storey now uses
  `MI_OT_FlakedPaint_WorldAligned` on exactly its left, lintel and right F1
  shell actors, preserving the pale upper storey, entrance opening, facade
  piers, transforms and collision. Exact report:
  `/private/tmp/abv_ss018_north_groundstorey_flaked_exact_save_v1.json`;
  accepted view:
  `/private/tmp/abv_ss018_north_groundstorey_flaked_preview_v1.png`.
- Every accepted batch enumerated the authoritative package-level dirty scope,
  saved only the exact intended external-actor packages, confirmed filesystem
  writes and returned Unreal to zero dirty packages. Current Git scope is
  intentionally unstaged: 281 modified plus 73 untracked files (354 total),
  staged count zero. Local and remote `feature/map-development` remain
  `e0b856c20cdad11f7057248c851d4d344f43fbe1`; no commit, push, merge or rebase
  was performed.

## 2026-08-16 launch-building ground-storey completion and shell acceptance

- The SS_007 Hotel ground floor now has a coherent ruin-brick wrap on all four
  exterior sides. Exactly the remaining north, east-left, east-lintel,
  east-right and west F1 shell actors were changed from generic stucco to the
  existing `MI_ABV_RuinBrick_WorldAligned`; its already-correct south F1
  pieces, upper floor, openings, balcony, collision and traversal were not
  changed. Exact report:
  `/private/tmp/abv_ss007_hotel_groundstorey_wrap_ruinbrick_exact_save_v1.json`;
  accepted north/east/west player-height views are under
  `/private/tmp/abv_ss007_hotel_groundstorey_wrap_ruinbrick_preview_v1/`.
- A close four-side SS_016 Substation review proved the shell is complete and
  the earlier apparent missing elevation was only a distant camera/clipping
  artifact. No shell actor was changed. The thin roofline rods remain the
  previously audited intentional utility features whose lower sections are
  hidden by the roof. Exact read-only preflight:
  `/private/tmp/abv_ss016_shell_exact_preflight_v1.json`; accepted views are
  under `/private/tmp/abv_ss016_shell_review_v1/`.
- The flat teal prototype treatment on the SS_010 Detention Annex no longer
  dominates its principal building. Exactly its eight ground-storey shell
  actors (east left/lintel/right, north, south left/lintel/right and west) now
  use the existing `MI_ABV_RuinBrick_WorldAligned`, while the cleaner teal
  upper storey remains as a deliberate institutional accent. Openings,
  transforms, authoritative collision and the previously completed perimeter
  were preserved. Exact report:
  `/private/tmp/abv_ss010_annex_groundstorey_ruinbrick_exact_save_v1.json`;
  accepted close views are under
  `/private/tmp/abv_ss010_annex_groundstorey_ruinbrick_preview_v1/`.
- The SS_012 Consulate Residence now reads as a cleaner pale residence above a
  weathered earthen ground storey. Exactly its eight F1 shell pieces use the
  existing `MI_ABV_CrackedMud_WorldAligned`; the pale upper floor, roof,
  timber/brick accents, doors, windows, transforms and collision remain
  unchanged. Exact report:
  `/private/tmp/abv_ss012_consulate_groundstorey_crackedmud_exact_save_v1.json`;
  accepted south/north/oblique views are under
  `/private/tmp/abv_ss012_consulate_groundstorey_crackedmud_preview_v1/`.
- A targeted trace resolved the gray cube visible near SS_013 as
  `CoreCover_C10`, a tagged authoritative `HardCover` gameplay actor using
  `MI_OT_Metal`, not a stray exterior prop. It was deliberately preserved.
  Read-only evidence:
  `/private/tmp/abv_ss013_foreground_cube_trace_probe_v1.json`.
- Every accepted mutation above used exact package-level dirty gates and exact
  saves, then returned Unreal to zero dirty packages. Current Git scope is
  intentionally unstaged: 302 modified plus 73 untracked files (375 total),
  staged count zero. Local and remote `feature/map-development` remain
  `e0b856c20cdad11f7057248c851d4d344f43fbe1`; no commit, push, merge or rebase
  was performed.

## 2026-08-16 launch-building secondary-elevation composition closeout

- A new deterministic 16-view acceptance set across the 13 launch building
  sites and three aerial contexts is under
  `/private/tmp/abv_launch_buildings_acceptance_review_v3/`. Fixed cameras that
  clipped through nearby/open-sided structures were rejected as invalid
  evidence; no geometry was changed from those views. The close cardinal
  shell reviews and prior exact actor/package audits remain authoritative.
- SS_004's material-correct but compositionally blank 18 m north elevation now
  has four non-colliding, non-navigable instances of the already imported
  Pakistan Wall Modular 16 heritage piece. They divide the wall into readable
  structural bays without creating actors, changing openings, or adding
  gameplay collision. Accepted views are under
  `/private/tmp/abv_ss004_north_facade_piers_preview_v1/`; exact save report:
  `/private/tmp/abv_ss004_north_facade_piers_exact_save_v1.json`.
- SS_003's exposed west service wall now uses the same reuse-first system: two
  additional piers join its existing center pier to create a three-bay rhythm.
  The additions are visual-only HISM instances and preserve the pump station's
  shell, utilities, cover, collision and traversal. Accepted views are under
  `/private/tmp/abv_ss003_west_facade_piers_preview_v1/`; exact save report:
  `/private/tmp/abv_ss003_west_facade_piers_exact_save_v1.json`.
- Both additions serialize in the one existing
  `ABV_OldTown_PakistanWallFacade_HISM_V1` actor package
  `/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/4/XJ/GOWVSDB53YHV8I1OQ2ZTN7`.
  Its final instance count is 38, effective collision is `NoCollision`,
  navigation relevance is false, and Unreal returned to zero dirty packages
  after each exact save. These close the remaining obvious flat secondary
  elevations; continue with ground/road/placed-prop exterior integration rather
  than another systematic building-shell pass unless new player-height evidence
  proves a specific defect.

## 2026-08-16 field-edge vegetation and localized ground acceptance

- A fresh current-state review after the launch-building closeout confirms the
  SS_013-adjacent field-edge now reads as a seasonal Abiverd grass-and-poppy
  patch at player height. The accepted five-view set is under
  `/private/tmp/abv_fieldedge_current_acceptance_v2/`.
- The map-owned `ABV_OT_FieldEdge_PoppyPilot_V1` actor remains one optimized
  non-replicated, non-ticking HISM actor with exactly 1,440 low-grass instances
  and 960 poppy instances. Both components are `NoCollision`, non-navigable,
  generate no overlaps, cast no shadows, and cull from 80 m to 240 m.
- `M_ABV_Foliage_Masked` is compiled for instanced static meshes and retains an
  opacity-mask clip value of 0.20. Seven fixed samples on
  `LandscapeStreamingProxy_2_2_0` returned saved Grass weights from 0.4384 to
  0.8549, confirming that the localized green ground treatment remains on the
  terrain beneath the vegetation rather than being a transient editor preview.
- Exact read-only evidence is
  `/private/tmp/abv_launch_vegetation_acceptance_v1.json`. Unreal remained at
  zero dirty packages. The field-edge pilot is accepted for the initial-launch
  playable area; continue exterior ground/road/placed-prop integration rather
  than reopening the foliage material or density unless new player-height
  evidence proves a specific defect.

## 2026-08-16 launch-perimeter Abiverd material finish

- The conspicuous near-white linear element beside the accepted field-edge was
  resolved by labeled viewport evidence as `CoreWall_EastMid`, an intentional
  collidable `HardCover`/`CoreBoundary` actor, not an editor guide or stray
  prop. The geometry, transform, collision, navigation and gameplay tags were
  preserved.
- Exactly the 11 launch perimeter segments that still used the bright generic
  `MI_OT_Stone` finish now use the existing
  `MI_ABV_RuinBrick_WorldAligned`. The already-correct
  `CoreWall_SouthSpawnSightbreak` was left unchanged. This removes the clean
  white-slab reading and makes the playable boundary read as sun-baked Abiverd
  masonry while retaining authoritative hard-cover behavior.
- Accepted approach and aerial views are under
  `/private/tmp/abv_corewall_abiverd_finish_review_v1/`. The exact mutation and
  save evidence are
  `/private/tmp/abv_corewall_abiverd_finish_apply_v1.json` and
  `/private/tmp/abv_corewall_abiverd_finish_exact_save_v1.json`.
- All 11 expected external-actor packages were physically rewritten and Unreal
  returned to zero dirty packages. No transforms, collision, navigation,
  buildings, roads, Landscape, vegetation, config, Movement, UI or hidden
  legacy overlay packages were changed.

## 2026-08-16 dry-canal and launch-placeholders exterior finish

- The west dry-canal entrance was the next proven player-height exterior
  defect: both 24 m edge walls still read as bright blockout slabs and its six
  named rubble actors were chamfer-cube placeholders. Before/after evidence is
  under `/private/tmp/abv_canal_rubble_review_v1/` and
  `/private/tmp/abv_canal_rubble_review_v1_after/`.
- `Canal_Edge_E` and `Canal_Edge_W` now use the existing
  `MI_ABV_RuinBrick_WorldAligned` material without transform, collision or
  navigation changes. `Canal_Rubble_01` through `Canal_Rubble_06` now reuse the
  already imported Historic Desert Ruin Structure Stone S 06 mesh. Each stone
  has a distinct yaw/uniform scale, a direct Landscape support trace and an
  exact 3 cm natural embed. Their existing query-and-physics collision and
  navigation relevance remain active because these pieces participate in the
  canal approach's physical cover/readability.
- The dry-canal mutation and exact-save reports are
  `/private/tmp/abv_dry_canal_finish_apply_v1.json` and
  `/private/tmp/abv_dry_canal_finish_exact_save_v1.json`. Exactly eight
  external-actor packages were physically rewritten and Unreal returned to
  zero dirty packages.
- The remaining 26 visible launch-area actors that still used generic
  `MI_OT_Stone` were then split by intended function without changing geometry
  or gameplay dimensions. Twelve attacker/checkpoint/south-spawn barriers and
  five ground curbs now use the existing weathered-concrete world-aligned
  material. Eight current SS_003/SS_006 parapets plus
  `Courtyard_Low_Focus` now use the Abiverd ruin-brick world-aligned material.
  Transforms, collision and navigation were explicitly preserved on every
  actor. Accepted contextual views are under
  `/private/tmp/abv_launch_placeholder_material_review_v1/`; mutation and
  exact-save reports are
  `/private/tmp/abv_launch_stone_placeholder_material_finish_apply_v1.json`
  and
  `/private/tmp/abv_launch_stone_placeholder_material_finish_exact_save_v1.json`.
- A follow-up bounded inventory found zero visible StaticMeshActors carrying
  LevelPrototyping materials inside the initial-launch XY/Z envelope. Evidence:
  `/private/tmp/abv_launch_prototype_material_inventory_v1.json`. This closes
  the current launch-area generic/prototype exterior-material category; pursue
  only concrete player-height findings rather than another broad material
  rewrite.

## 2026-08-16 initial-launch barrier production-mesh finish

- The 12 remaining scaled chamfer-cube road-control barriers at the attacker
  spawn, checkpoint and south spawn now reuse the already imported Quixel
  `SM_ydxlcck_tier_2` long sandbag assembly and its existing `MI_ydxlcck`
  material. No new mesh, material, actor or package was created.
- Each four-actor site was handled as a separate dirty/save batch. Every actor
  uses uniform scale 1, query-and-physics `BlockAll` collision, navigation
  relevance, no overlap events, a direct Landscape support trace and exactly
  3 cm natural terrain embed. Center-route clearances remain approximately
  6.79 m at attacker spawn, 10.79 m at the checkpoint and 6.79 m at south
  spawn. The checkpoint trace explicitly ignored only the known existing
  `CoreCover_C11` sandbag after the first read-only support trace correctly hit
  that cover instead of Landscape; no mutation occurred during that rejected
  attempt.
- Accepted current-state views are under
  `/private/tmp/abv_barrier_sandbag_review_v1/`. The bounded apply and exact
  save reports are
  `/private/tmp/abv_launch_barrier_sandbag_group_apply_v1.json` and
  `/private/tmp/abv_launch_barrier_sandbag_group_exact_save_v1.json` (the files
  are overwritten per group; the Unreal log retains one preview/save marker per
  site). All 12 existing external-actor packages were physically rewritten in
  four-package batches, and Unreal returned to zero dirty packages after each
  exact save.

## 2026-08-16 initial-launch core-cover production-visual pass

- The authoritative `CoreCover_*` actors remain the gameplay collision and
  navigation proxies. Their transforms and query-and-physics collision are
  preserved; only the visible prototype cube components are hidden after a
  reviewed production-mesh replacement is present.
- `CoreCover_A01` through `CoreCover_A08` now have optimized map-owned HISM
  visuals in `ABV_OT_CoreCover_Visual_HISM_V1`. The actor contains six long
  Quixel sandbag instances and eight square Quixel sandbag instances; the
  HISM components are non-replicated, non-ticking, collisionless,
  navigation-irrelevant, overlap-disabled and distance-culled. Exact source
  proxy packages and the HISM actor package were saved in bounded batches,
  and Unreal returned to zero dirty packages after each save.
- Durable UE 5.8 material rule: every material used by ISM/HISM geometry must
  have **Used with Instanced Static Meshes = true**. Validate that usage before
  actor creation. The first HISM assignment may legitimately dirty the exact
  source material or material-instance package while Unreal adds the usage
  permutation; treat that as a bounded, reviewable material compile/save, not
  as unexplained map-package scope. This applies to foliage masters such as
  `M_ABV_Foliage_Masked` and to Quixel materials reused for instanced cover.
- Do not call a nonexistent Python `mark_render_state_dirty` method on an HISM
  component. Instance addition already updates the component; verify the
  viewport and authoritative dirty-package list instead. Also avoid accepting
  the first downward trace blindly: `CoreCover_A06` initially hit an overhead
  compound floor. That preview was rejected before save and the visual was
  conformed to the preserved authoritative proxy base with a 3 cm embed.
- Evidence is under `/private/tmp/abv_corecover_a_pilot_review_v1/` and
  `/private/tmp/abv_corecover_a05_a08_review_v1/`; apply/save reports are
  `/private/tmp/abv_corecover_a_pilot_apply_v1.json`,
  `/private/tmp/abv_corecover_a_pilot_exact_save_v1.json`,
  `/private/tmp/abv_corecover_a05_a08_apply_v1.json`, and
  `/private/tmp/abv_corecover_a05_a08_exact_save_v1.json`.

### Core-cover continuation and closeout

- `CoreCover_B01` through `CoreCover_B08` and the visible C-series proxies
  (`C01` through `C10`, plus `C12`) now follow the same production-visual
  pattern. Industrial-width envelopes use the imported corrugated Quixel
  barrier mesh; narrower masonry positions use stacked square Quixel
  sandbags; the low profile uses the imported Structure Stone S 06 rubble.
  Each placement was conformed to the exact visible support actor, with the
  C09 position correctly supported by `Core_SS_013_F1_Floor` rather than
  Landscape. The hidden valid `CoreCover_C11` proxy was not changed.
- The shared `ABV_OT_CoreCover_Visual_HISM_V1` actor now contains exactly 6
  long-sandbag, 30 square-sandbag, 25 corrugated-barrier and 6 low-rubble
  instances before the freight component. All visual HISM components remain
  `NoCollision`, navigation-irrelevant, overlap-disabled, non-replicated,
  non-ticking and culled from 160 m to 480 m. The authoritative hidden proxy
  actors retain query-and-physics collision and navigation relevance.
- The final visible prototype, `CoreCover_FreightCrates`, was replaced by 12
  instances of the owned Scene Junkyard rusty metal storage crate, arranged
  as a compact three-by-two, two-course freight stack on the perfectly level
  `Core_SS_013_F1_Floor`. The final HISM actor therefore also contains
  `HISM_CoreCover_FreightCrates` with 12 visual-only instances. Close review
  evidence is under `/private/tmp/abv_freight_crates_review_v1/after_detail/`;
  exact save evidence is
  `/private/tmp/abv_freight_crates_exact_save_v1.json`.
- Final read-only inventory:
  `/private/tmp/abv_launch_corecover_visual_matrix_v1.json` records all 34
  `CoreCover_*` actors hidden and zero visible `CoreCover_*` prototype blocks,
  with authoritative Unreal dirty packages at zero. This closes the initial
  launch core-cover production-mesh category.
- A subsequent general basic-shape inventory found 415 visible Engine basic
  shapes, but every one already carries an intentional project material; the
  count primarily consists of the accepted modular building shells, floors,
  parapets, trims, thresholds and small exterior utilities. There are no
  remaining LevelPrototyping/default-material actors in the launch envelope.
  Use concrete player-height evidence and exact site labels for any further
  replacement rather than treating Engine basic-shape geometry itself as a
  defect.

## 2026-08-16 launch-area awning recovery pass

- Six authored exterior awnings had previously been hidden after their black
  `WrinkledTarp` presentation was rejected, leaving visible launch-area
  frontages incomplete. The safe replacement pattern is to reuse the already
  imported Quixel Historic Desert Ruins corrugated sheet
  `Military_Trenches_Wall_Metal_Corrugated_06_ydxnbdns_High`, with an
  actor-only `MI_OT_Timber` material override. The source Quixel material was
  rejected in the current launch lighting because its upper face rendered
  nearly white; `MI_OT_Metal` remained too reflective. Do not modify either
  shared source material to compensate.
- `ABV_SS_005_ClinicMainAwning_V1` is the first completed replacement. It now
  sits above `Clinic_MainDoor` at location `(-5700.65, -1065.3, 35139.7)`,
  rotation `(pitch 0, yaw 0, roll -95)`, scale `(1.3, 0.4, 1.1)`. It is visible,
  non-colliding, navigation-irrelevant and overlap-disabled. Accepted close
  views are under `/private/tmp/abv_ss005_corrugated_awning_review_v1/`; exact
  package-save evidence is
  `/private/tmp/abv_ss005_corrugated_awning_exact_save_v1.json`. Unreal was
  authoritative-zero-dirty after the exact single-package save.
- A facade-damage experiment using the imported flat damaged-plaster modules
  was rejected before mutation because the pieces read as tall pasted strips
  rather than integrated erosion. Do not repeat that treatment without a
  geometry-aware corner/opening composition.
- The awning recovery category is now complete for the six known launch-area
  gaps. `ABV_SS_010_YardGateAwning_V1`,
  `ABV_SS_011_CheckpointDoorAwning_V1`, both
  `ABV_SS_012_ConsulateDoorAwning_*` actors and
  `ABV_SS_016_SubstationWestAwning_V1` now use the same accepted corrugated
  sheet plus actor-only timber finish. SS_010 retains the authored roughly
  four-metre gate span; SS_016 was rotated and centered on its west lintel.
  All six remain visual-only (`NoCollision`, no navigation, no overlaps), and
  no new actors or packages were created. Review images are under
  `/private/tmp/abv_ss010_yard_gate_corrugated_awning_review_v1/`,
  `/private/tmp/abv_ss011_ss012_corrugated_awning_review_v1/`, and
  `/private/tmp/abv_ss016_west_corrugated_awning_review_v1/`. Exact-save
  reports are the correspondingly named `*_exact_save_v1.json` files in
  `/private/tmp`. Unreal returned to authoritative zero dirty after every
  bounded save.

## 2026-08-16 SS_011 checkpoint gatepost correction

- `Checkpoint_GatePost_W` and `Checkpoint_GatePost_E` were proven to float
  approximately 150 cm above Landscape and presented as oversized plain
  prototype columns. Both existing actors now use the already imported
  Historic Desert Ruin Structure Stone S 06 mesh and its existing material;
  no new actor or shared asset was created.
- The west post is at `(6983.1598, 3916.9722, 34914.2238)`, pitch `-90`, yaw
  `8`, uniform scale `2.1`. The east post is at
  `(7783.6417, 3930.7607, 34914.2238)`, pitch `-90`, yaw `-12`, uniform scale
  `2.1`. Both preserve the checkpoint spacing, sit 3 cm into
  `LandscapeStreamingProxy_2_2_0`, retain visible query-and-physics collision
  and navigation relevance, and have overlap generation disabled.
- Review evidence is under `/private/tmp/abv_ss011_gatepost_stone_review_v1/`;
  exact-save evidence is
  `/private/tmp/abv_ss011_gatepost_stone_exact_save_v1.json`. Unreal returned
  to authoritative zero dirty after save.

## 2026-08-16 SS_016 rooftop utility correction

- Three visibly suspended rooftop utilities were proven against the exact
  `Core_SS_016_Roof` top plane at Z `35131.3`: the former barrel floated 46 cm,
  `Utility_Pipe_06` floated 100 cm, and `Utility_Pipe_07` floated 120 cm. The
  two pipes were lowered in place and renamed as west/east roof vents. The
  barrel actor now uses the imported Quixel Rusty Metal Barrel and is named
  `ABV_SS_016_Roof_RustBarrel_V1`. All three bottoms sit at Z `35128.3`, a
  3 cm roof embed; collision remains visible query-and-physics while navigation
  and overlaps are disabled.
- The three SS_016 rooftop cabinet actors were also retained in place but
  changed to the imported Quixel `Electric_Box_ullibjd_High` at uniform scale
  `1.4`, renamed `ABV_SS_016_RoofSwitchgear_A/B/C_V1`, and conformed to the
  same roof plane. This replaces the oversized repeated cabinet silhouettes
  with smaller production switchgear without creating actor packages or
  changing the authored row layout.
- Review evidence is under
  `/private/tmp/abv_ss016_rooftop_contact_review_v1/` and
  `/private/tmp/abv_ss016_rooftop_switchgear_review_v1/`. Exact-save evidence
  is `/private/tmp/abv_ss016_rooftop_contact_exact_save_v1.json` and
  `/private/tmp/abv_ss016_rooftop_cabinets_exact_save_v1.json`. Each bounded
  three-package save physically advanced the expected mtimes and returned
  Unreal to authoritative zero dirty.

## 2026-08-16 remaining launch-roof barrel finish

- An exact-package follow-up resolved the four remaining visible barrel
  placeholders: `Utility_Barrel_01/02` on `Core_SS_013_Roof` and
  `Utility_Barrel_10/11` on `Core_SS_017_Roof`. All four were
  `SM_Cylinder` prototype actors floating `46.0`, `46.0`, `46.0`, and
  `66.0 cm` above their exact roof support planes.
- Their existing actors now reuse the imported Quixel
  `Rusty_Metal_Barrel_teufceuda_High` at uniform scale `1`, with slight yaw
  variation and `3 cm` roof embed. They are labeled
  `ABV_SS_013_Roof_RustBarrel_W/E_V1` and
  `ABV_SS_017_Roof_RustBarrel_W/E_V1`. Visible collision is retained;
  navigation and overlap events are disabled.
- Read-only, apply, and exact-save reports are
  `/private/tmp/abv_remaining_barrels_exact_preflight_v1.json`,
  `/private/tmp/abv_remaining_roof_barrels_apply_v1.json`, and
  `/private/tmp/abv_remaining_roof_barrels_exact_save_v1.json`. Review
  captures are under `/private/tmp/abv_remaining_barrels_review_v1/`. Exactly
  four external-actor packages were saved and Unreal returned to zero dirty.

## 2026-08-16 launch-area facade utility correction

- The two original SS_016 wall electrical-box actors were retained, but their
  chamfer-cube placeholder meshes were replaced with the already imported
  Quixel `Electrical_Box_tdgecegda_High`. They are now named
  `ABV_SS_016_WestElectricalBox_V1` and
  `ABV_SS_016_EastElectricalBox_V1`, use uniform scale `1.2`, preserve their
  exact wall centers, and remain visible query-and-physics collision with
  navigation and overlaps disabled. Review evidence is under
  `/private/tmp/abv_ss016_wall_boxes_review_v1/`; exact-save evidence is
  `/private/tmp/abv_ss016_wall_boxes_exact_save_v1.json`.
- The south SS_003 Quixel electrical enclosure overlapped the central opening.
  `ABV_SS_003_PumpSouthElectricalBox_V1` was moved laterally into the exact
  solid bay between `Pump_Door_A` and `Pump_Window_01_Frame`; its final X
  bounds are `-10938.45` to `-10836.55`, leaving about `36.55 cm` clearance
  from each adjacent opening. Review evidence is under
  `/private/tmp/abv_ss003_meter_reposition_review_v1/`; exact-save evidence is
  `/private/tmp/abv_ss003_south_meter_exact_save_v1.json`.
- A follow-up exact opening-clearance audit found `OT_EXT_Meter_SS_013`
  correctly placed between `Depot_PedDoor` and `Depot_LoadingDoor`, with more
  than 3.2 m clearance on either side, so it was not changed. In contrast,
  `OT_EXT_Meter_SS_015` overlapped `MotorPool_Garage_A` by about 52 cm. That
  existing actor was moved from X `12224` to X `12000` in the solid south-wall
  bay, leaving `188.24 cm` from the west utility and `171.96 cm` from the
  garage panel. Its mesh, Y/Z, rotation, scale and `NoCollision` behavior were
  preserved. Reports are
  `/private/tmp/abv_ss013_ss015_meter_clearance_preflight_v1.json`,
  `/private/tmp/abv_ss015_meter_reposition_v1.json`, and
  `/private/tmp/abv_ss015_meter_exact_save_v1.json`; review captures are under
  `/private/tmp/abv_ss013_ss015_meter_clearance_review_v1/`. Each exact save
  returned Unreal to authoritative zero dirty.

## 2026-08-16 SS_003 and SS_015 rooftop production-utility finish

- `Utility_Cabinet_01` on `SS_003` and `Utility_Cabinet_02` on `SS_015` were
  the remaining large chamfer-cube rooftop cabinet placeholders visible in
  close oblique review. Their existing actor packages and XY positions were
  retained, while both now reuse the imported Quixel
  `Electric_Box_ullibjd_High` mesh at uniform scale `1.4`. They are named
  `ABV_SS_003_RoofSwitchgear_V1` and
  `ABV_SS_015_RoofSwitchgear_V1`, sit 3 cm into their exact roof support
  planes, retain visible query-and-physics collision, and are non-navigable
  with overlaps disabled.
- The two SS_015 roof cylinders `Utility_Barrel_07` and
  `Utility_Barrel_08` were likewise retained as actors but replaced with the
  already imported Quixel `Rusty_Metal_Barrel_teufceuda_High`, renamed
  `ABV_SS_015_Roof_RustBarrel_W_V1` and
  `ABV_SS_015_Roof_RustBarrel_E_V1`. Both use uniform scale `1`, slight yaw
  variation, and a verified 3 cm roof embed. Their visible collision remains;
  navigation and overlaps are disabled.
- Review evidence is under
  `/private/tmp/abv_ss003_ss015_roof_cabinets_review_v1/`. Apply/save reports
  are `/private/tmp/abv_ss003_ss015_roof_cabinets_apply_v1.json`,
  `/private/tmp/abv_ss003_ss015_roof_cabinets_exact_save_v1.json`,
  `/private/tmp/abv_ss015_roof_barrels_apply_v1.json`, and
  `/private/tmp/abv_ss015_roof_barrels_exact_save_v1.json`. Each two-package
  exact save physically advanced the expected mtimes and returned Unreal to
  authoritative zero dirty.

## 2026-08-16 launch-area ground-barrel production finish

- `Utility_Barrel_03` through `Utility_Barrel_06` were exact-resolved as four
  visible launch-area `SM_Cylinder` placeholders. Direct downward traces hit
  `LandscapeStreamingProxy_2_1_0` at every actor. The placeholders floated
  about `7.6 cm`, `10.4 cm`, `45.6 cm`, and `46.3 cm`, respectively.
- The four existing actor packages and XY positions were retained. Each actor
  now reuses the imported Quixel
  `Rusty_Metal_Barrel_teufceuda_High` at uniform scale `1`, with restrained
  yaw variation, visible query-and-physics collision, navigation disabled,
  overlaps disabled, and a verified `3 cm` terrain embed. The final labels are
  `ABV_OT_RustBarrel_03_V1` through `ABV_OT_RustBarrel_06_V1`.
- Apply and exact-save evidence is
  `/private/tmp/abv_ground_barrels_03_06_apply_v1.json` and
  `/private/tmp/abv_ground_barrels_03_06_exact_save_v1.json`; review captures
  are under `/private/tmp/abv_ground_barrels_03_06_review_v2/`. The save
  advanced exactly the four intended external-actor mtimes and returned
  Unreal to authoritative zero dirty.

## 2026-08-16 SS_003 exterior wall-box recovery

- `Pump_ElectricalBox_01/02` were exact-resolved as small chamfer-cube
  placeholders positioned `110 cm` inward from the west/east wall faces. They
  were therefore absent from their intended exterior elevations. Fixed traces
  distinguished the core wall inner planes (`X=-11480/-9720`) from the actual
  exterior planes (`X=-11520/-9680`).
- Both existing actor packages now use the imported Quixel
  `Electrical_Box_tdgecegda_High` at uniform scale `1.2`. They are labeled
  `ABV_SS_003_WestElectricalBox_V1` and
  `ABV_SS_003_EastElectricalBox_V1`, sit `2 cm` proud of the verified exterior
  wall planes in solid wall bays at `Y=-6100`, retain visible collision, and
  have navigation and overlap events disabled.
- Evidence is in
  `/private/tmp/abv_ss003_wall_boxes_exact_preflight_v1.json`,
  `/private/tmp/abv_ss003_wall_boxes_support_trace_v1.json`,
  `/private/tmp/abv_ss003_wall_box_bay_trace_v1.json`,
  `/private/tmp/abv_ss003_wall_boxes_apply_v1.json`,
  `/private/tmp/abv_ss003_wall_boxes_outer_plane_fix_v1.json`, and
  `/private/tmp/abv_ss003_wall_boxes_exact_save_v1.json`; final views are under
  `/private/tmp/abv_ss003_wall_boxes_review_v1/`. Exactly two packages were
  saved and Unreal returned to zero dirty.

## 2026-08-16 remaining launch-area facade-meter finish

- A bounded follow-up resolved the four remaining `OT_EXT_Meter_*` launch-area
  actors (`SS_005`, `SS_007`, `SS_011`, and `SS_018`) as decorative
  `Engine/BasicShapes/Cube` placeholders with navigation relevance still
  enabled. Their actor packages were retained; no actors or shared assets were
  created.
- The four actors now reuse the imported Quixel
  `Electrical_Box_tdgecegda_High` at uniform scale `1.2` and are named
  `ABV_SS_005_NorthElectricalMeter_V1`,
  `ABV_SS_007_NorthElectricalMeter_V1`,
  `ABV_SS_011_NorthElectricalMeter_V1`, and
  `ABV_SS_018_SouthElectricalMeter_V1`. The first three are fitted 2 cm proud
  of their verified north facade planes; the SS_018 unit is fitted 2 cm proud
  of its south facade plane. All remain decorative `NoCollision` actors, with
  navigation relevance and overlap events disabled.
- Apply evidence is
  `/private/tmp/abv_remaining_facade_meters_apply_v1.json`; exact-save evidence
  is `/private/tmp/abv_remaining_facade_meters_exact_save_v1.json`; review
  captures are under
  `/private/tmp/abv_remaining_facade_meters_review_v1/`. Exactly four actor
  packages advanced on disk and authoritative Unreal dirty state returned to
  zero.
- `Pump_Utility_01/02` were separately checked read-only. Direct support traces
  hit `Core_SS_003_Roof` roughly 270–290 cm above their mesh bottoms, proving
  those two cube utilities are inside the building footprint/interior rather
  than exterior launch-area defects. They were intentionally left unchanged;
  evidence is `/private/tmp/abv_ss003_freestanding_utilities_preflight_v1.json`.

## 2026-08-16 SS_018 side-wall utility finish

- Player-height west/east elevation review proved
  `Telecom_ElectricalBox_12/13` were still visible chamfer-cube placeholders on
  the SS_018 telecom building. Both existing actors were retained and now use
  `Electrical_Box_tdgecegda_High` at uniform scale `1.2`.
- They are named `ABV_SS_018_WestElectricalBox_V1` and
  `ABV_SS_018_EastElectricalBox_V1`; each sits 2 cm proud of its exact outer
  facade plane in a solid wall bay. Existing visible query-and-physics
  collision was retained while navigation relevance and overlap events were
  disabled.
- Apply/save evidence is `/private/tmp/abv_ss018_side_boxes_apply_v1.json` and
  `/private/tmp/abv_ss018_side_boxes_exact_save_v1.json`; before/after views
  are under `/private/tmp/abv_ss018_side_boxes_review_v1/`. Exactly two actor
  packages advanced on disk and Unreal returned to authoritative zero dirty.

## 2026-08-16 SS_011 checkpoint side-wall utility finish

- Exact west/east player-height review proved
  `Checkpoint_ElectricalBox_07/08` were still chamfer-cube placeholders on
  solid SS_011 facade bays. Their existing packages were retained and now use
  `Electrical_Box_tdgecegda_High` at uniform scale `1.2`.
- The production labels are `ABV_SS_011_WestElectricalBox_V1` and
  `ABV_SS_011_EastElectricalBox_V1`. Each is fitted 2 cm proud of the verified
  outer wall plane, retains visible query-and-physics collision, and has
  navigation relevance and overlap events disabled.
- Apply/save evidence is `/private/tmp/abv_ss011_side_boxes_apply_v1.json` and
  `/private/tmp/abv_ss011_side_boxes_exact_save_v1.json`; review captures are
  under `/private/tmp/abv_ss011_side_boxes_review_v1/`. Exactly two packages
  advanced and authoritative dirty state returned to zero.

## 2026-08-16 SS_018 rooftop cabinet stale-inventory closure

- The offline launch inventory still classified `Utility_Cabinet_06` as an
  `SM_ChamferCube`, but the exact live actor package proved that record stale.
  The actor already uses imported Quixel
  `Electrical_Cabinet_ujzfde2_High` at scale `0.75`, is flush to the SS_018
  roof, has visible collision, and is already non-navigable with overlaps
  disabled. The mutation gate stopped before `modify()` and no save occurred.
- Exact evidence is
  `/private/tmp/abv_ss018_roof_cabinet_exact_preflight_v2.json`; review views
  are under `/private/tmp/abv_ss018_roof_cabinet_review_v1/`. Treat the rooftop
  cabinet as production-finished unless a new concrete visual defect is found.

## 2026-08-16 SS_006 water-tower utility support audit

- The four `Tower_Utility_01..04` actors were re-audited after a below-surface
  trace appeared to show a large gap. That apparent defect was invalid: the
  trace began below the Landscape and therefore struck buried decorative
  ground meshes (or returned no hit), not the visible authoritative surface.
- A final top-down trace from below the overhead platform, with all four boxes
  ignored, hit `LandscapeStreamingProxy_1_2_0` at every exact actor XY. Each
  imported `Electric_Box_ullibjd_High` bottom is exactly `2.0 cm` embedded in
  the Landscape. All four boxes are correctly grounded and were left
  unchanged; no package was saved and authoritative dirty state remained zero.
- Final evidence is
  `/private/tmp/abv_water_tower_utilities_support_final_v1.json`; player-height
  review views are under
  `/private/tmp/abv_water_tower_utilities_review_v1/`.
- Durable trace rule: for terrain contact, start above the expected Landscape
  surface while ignoring the audited actor and any overhead blocker already
  excluded by the chosen start height. A trace launched from `actor bottom -
  1 cm` can already be below a correctly embedded Landscape surface and must
  not be interpreted as proof of floating.

## 2026-08-16 SS_018 rooftop antenna-mast finish

- The three SS_018 rooftop equipment bases were exact-resolved as already
  imported production assets (Quixel metal tank, electrical cabinet, and
  electrical box). They were preserved unchanged. The three attached antenna
  masts were still long, square `SM_Cube` prototype columns and still affected
  navigation.
- Their existing actor packages now use `/Engine/BasicShapes/Cylinder` with
  `MI_OT_Metal`, yielding round `8 cm` diameter masts at the original intended
  heights (`250`, `320`, and `210 cm`). Each mast is centered on its own
  equipment base and embedded `2 cm` into the verified base top. Production
  labels are `ABV_SS_018_RoofAntennaMast_West_V1`,
  `ABV_SS_018_RoofAntennaMast_Center_V1`, and
  `ABV_SS_018_RoofAntennaMast_East_V1`.
- The thin decorative masts now use the `NoCollision` profile, do not affect
  navigation, and generate no overlaps. Evidence is in
  `/private/tmp/abv_ss018_rooftop_masts_plan_v1.json`,
  `/private/tmp/abv_ss018_rooftop_masts_collision_fix_v1.json`, and
  `/private/tmp/abv_ss018_rooftop_masts_exact_save_v1.json`; before/after views
  are under `/private/tmp/abv_ss018_rooftop_masts_review_v1/`. Exactly three
  actor packages advanced and authoritative Unreal dirty state returned to
  zero.
- UE detail: changing a StaticMeshComponent mesh can reapply the source
  collision profile. For guaranteed decorative collision, call
  `set_collision_profile_name("NoCollision")` as well as
  `set_collision_enabled(NO_COLLISION)` after `set_static_mesh()`.

## 2026-08-16 SS_012 freight-depot rooftop equipment closure

- The offline inventory still named `Depot_RoofVent_01..03` as cube roof
  vents. Exact live package resolution proved that record stale: the three
  actors already use the imported Quixel electrical cabinet, metal water tank,
  and electrical box meshes respectively. Every item is flush to the roof,
  uses `BlockAll` visible collision, is non-navigable, and generates no overlap
  events. No mutation or save was needed.
- Read-only evidence is
  `/private/tmp/abv_ss012_depot_roofvents_preflight_v1.json`. Treat these three
  rooftop actors as production-finished unless a new concrete visual defect is
  found.

## 2026-08-16 SS_004 Tea House facade-sign finish

- Exact live review proved `Tea_House_Sign` was still a bright cyan prototype
  slab above the Tea House frontage. Its existing external-actor package was
  retained and the actor is now named `ABV_SS_004_TeaHouseTimberSign_V1`.
- The board keeps its authored dimensions and placement but now uses the
  existing `MI_OT_Timber` material, reads as a restrained timber fascia/sign
  panel, and is decorative `NoCollision` with navigation relevance and overlap
  events disabled.
- Apply evidence is `/private/tmp/abv_teahouse_sign_finish_v1.json`; exact-save
  evidence is `/private/tmp/abv_teahouse_sign_exact_save_v1.json`; review views
  are under `/private/tmp/abv_sign_ladder_review_v1/`. Exactly one actor package
  advanced on disk and authoritative Unreal dirty state returned to zero.

## 2026-08-16 SS_006 water-tower ladder finish

- `WaterTower_Ladder` was a solid `25 x 100 x 1100 cm` prototype slab. Its
  existing external-actor package is now `ABV_SS_006_WaterTowerLadder_V1` and
  contains one `HISM_WaterTowerLadder` component: two narrow rails plus 31
  evenly spaced rungs, all instanced from `/Engine/BasicShapes/Cube`.
- The ladder uses the already imported rusted-metal crate material, which was
  already proven compatible with HISM rendering. Its 33 visible instances use
  `BlockAll` collision matching the rendered rails/rungs, do not affect
  navigation, generate no overlap events, do not tick, and do not replicate.
  The old slab root remains only as a hidden, non-colliding component.
- Preview evidence is `/private/tmp/abv_water_tower_ladder_preview_v1.json`;
  exact-save evidence is
  `/private/tmp/abv_water_tower_ladder_exact_save_v1.json`; review captures are
  under `/private/tmp/abv_water_tower_ladder_review_v1/`. Exactly the existing
  ladder actor package advanced on disk and Unreal returned to zero dirty.
- Durable UE 5.8 lessons from the rejected first preview:
  `HierarchicalInstancedStaticMeshComponent` has no Python
  `mark_render_state_dirty()` method. Also, assigning a material not yet marked
  for Instanced Static Mesh use can automatically dirty that shared material.
  Do not try to clear that live material mutation by reloading the material
  while a new HISM still references it; that package reload pinned this editor.
  The safe recovery was to discard the unsaved preview by restarting only the
  isolated editor, then retry with an already-HISM-compatible material. The
  original ladder and `MI_OT_Metal` files never advanced on disk during the
  rejected attempt.

## 2026-08-16 SS_003 and SS_015 rooftop vent-pipe finish

- Exact live resolution proved both roof cabinets and both SS_015 barrels were
  already imported production assets. Four remaining `SM_Cylinder` prototype
  pipes were the only live stale entries in this bounded roof-utility set.
- Their existing packages are now
  `ABV_SS_003_RoofVentPipe_W_V1`,
  `ABV_SS_003_RoofVentPipe_E_V1`,
  `ABV_SS_015_RoofVentPipe_W_V1`, and
  `ABV_SS_015_RoofVentPipe_E_V1`. Each uses the Engine cylinder at a cleaner
  `14 cm` diameter, preserves its original roof contact and height, and uses
  the already imported rusted-metal material.
- The thin decorative vents are now `NoCollision`, non-navigable, non-
  overlapping, non-replicated, and non-ticking. Apply/save evidence is
  `/private/tmp/abv_ss003_ss015_roof_pipes_apply_v1.json` and
  `/private/tmp/abv_ss003_ss015_roof_pipes_exact_save_v1.json`; before/after
  review captures are under `/private/tmp/abv_roof_pipe_review_v1/`. Exactly
  four actor packages advanced and Unreal returned to zero dirty.

## 2026-08-16 launch-sign live closure

- Exact package resolution rechecked the three remaining landmark boards and
  all eight Bazaar stall boards. The Bazaar boards already use the approved
  timber finish and `NoCollision`; their prior cleanup is still valid and they
  were not reopened. The three `OT_SIGNBOARD_SS_004`, `...SS_013`, and
  `...SS_017` actors remain explicitly tagged `LandmarkSignBoard`/
  `SunscarOldTownLandmarkSignV1` and use the authored accent finish. They are
  not accidental blockout geometry, so no speculative replacement was made.
- Read-only evidence is `/private/tmp/abv_launch_signs_live_v1.json`; review
  captures are under `/private/tmp/abv_launch_signs_review_v1/before/`.

## 2026-08-16 SS_015 Motor Pool repair-prop finish

- Four remaining `SM_ChamferCube` repair props were converted in place to the
  already owned Nanite Junkyard rusty-metal storage crate. Their existing
  actor packages are retained and now use production labels
  `ABV_SS_015_MotorPoolRepairCrate_A_V1` through `_D_V1`.
- Every crate is uniformly scaled to `0.9`, keeps the authored XY placement,
  preserves the original support bottom exactly, and receives a restrained
  yaw variation (`12`, `-17`, `8`, and `-25` degrees). The real ten-hull mesh
  collision remains `BlockAll`, navigation-relevant and non-overlapping so the
  authored low-cover behavior is retained.
- Apply/save evidence is
  `/private/tmp/abv_motorpool_repair_crates_apply_v1.json` and
  `/private/tmp/abv_motorpool_repair_crates_exact_save_v1.json`; review images
  are under `/private/tmp/abv_industrial_blocks_review_v1/motorpool_after/`.
  Exactly four existing external-actor packages advanced and Unreal returned
  to zero dirty.

## 2026-08-16 SS_016 Power Substation equipment finish

- Six visibly suspended `SM_Cube` equipment blocks were replaced in place by
  the already imported Nanite Quixel
  `Electrical_Cabinet_ujzfde2_High`, preserving the six authoritative actor
  packages and cover locations. Production labels are
  `ABV_SS_016_SubstationCabinet_01_V1` through `_06_V1`.
- The four principal cabinets use uniform scales `1.65`, `1.90`, `1.55`, and
  `1.80`; the rear pair use `1.25`. The front-row clear passages measure
  approximately `131.7`, `151.2`, and `158.1 cm`, retaining walkable tactical
  gaps. All six keep real convex `BlockAll` collision, navigation relevance,
  no overlap events, no replication and no tick.
- Six direct world traces hit only `Core_SS_016_F1_Floor` at
  `Z=34811.30 cm`. The cabinet bases were placed with a `0.5 cm` natural embed,
  eliminating the inherited cube-pivot suspension. Apply, trace, and save
  evidence is `/private/tmp/abv_substation_cabinets_apply_v1.json`,
  `/private/tmp/abv_substation_cabinets_ground_fix_v1.json`, and
  `/private/tmp/abv_substation_cabinets_exact_save_v1.json`; review captures
  are under `/private/tmp/abv_industrial_blocks_review_v1/substation_after/`.
  Exactly six existing external-actor packages advanced and Unreal returned
  to zero dirty.
- UE Python detail: `StaticMesh.get_material(0)` returns the material interface
  directly in this UE 5.8 wrapper; do not dereference a nonexistent
  `.material_interface` field. The rejected first call failed before any
  mutation and left the editor clean.

## 2026-08-16 SS_017 Covered Bazaar canopy-post finish

- Exact live resolution distinguished the already finished six Quixel wooden
  market tables from the eight authored north/south stall collision bodies.
  Those stall bodies remain unchanged because they preserve the approved
  low-cover and storefront layout.
- The four remaining visible square `SM_Cube` canopy poles were converted in
  place to Engine cylinder posts while retaining the original `12 x 12 x
  300 cm` occupied bounds and the existing Old Town metal finish. Production
  labels are `ABV_SS_017_BazaarCanopyPost_A_V1` through `_D_V1`.
- Visible `BlockAll` collision is retained, while navigation relevance is
  disabled for these thin posts; overlap events, replication and tick remain
  disabled. Apply/save evidence is
  `/private/tmp/abv_bazaar_posts_apply_v1.json` and
  `/private/tmp/abv_bazaar_posts_exact_save_v1.json`; review captures are
  under `/private/tmp/abv_bazaar_posts_review_v1/`. Exactly four existing
  external-actor packages advanced and Unreal returned to zero dirty.

## 2026-08-16 SS_016 Substation compound-wall finish

- The four `SS_016_Fence_*` actors were verified live as solid 20–26 metre
  `SM_Cube` metal slabs. The imported corrugated barrier was evaluated but its
  shared GLTF base material is not enabled for instanced static meshes; that
  source was not edited or forced into an unsafe per-panel actor expansion.
- The four existing authoritative perimeter actors are now named
  `ABV_SS_016_SubstationCompoundWall_{East,North,South,West}_V1` and use the
  existing world-aligned Abiverd ruin-brick finish. Their exact transforms,
  occupied bounds, `BlockAll` collision and navigation relevance are
  unchanged, so the approved site boundary and routes are preserved while the
  enclosure reads as a plausible local masonry compound rather than metal
  blockout slabs.
- Apply/save evidence is
  `/private/tmp/abv_substation_compound_walls_apply_v1.json` and
  `/private/tmp/abv_substation_compound_walls_exact_save_v1.json`; review
  captures are under `/private/tmp/abv_substation_compound_walls_review_v1/`.
  Exactly four actor packages advanced and Unreal returned to zero dirty.
## 2026-08-16 SS_004 Tea House furniture material finish

- Verified live that the four SS_004 tea benches and two tea tables had already been converted from blockout cubes to owned Quixel furniture meshes. The remaining defect was six generic `MI_OT_Timber` material overrides masking those imported assets' authored finishes.
- Restored each bench/table component to its matching imported Quixel material while preserving the existing mesh, full transform, collision envelope, navigation settings, and courtyard layout.
- Production labels are `ABV_SS_004_TeaBench_01A_V1`, `ABV_SS_004_TeaBench_01B_V1`, `ABV_SS_004_TeaBench_02A_V1`, `ABV_SS_004_TeaBench_02B_V1`, `ABV_SS_004_TeaTable_01_V1`, and `ABV_SS_004_TeaTable_02_V1`.
- Exact saved external-actor packages:
  - `/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/D/LZ/CWM9L7QJO0UF4FU1QNUSV9`
  - `/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/3/7Z/84X2BAF9N34UG6RW89UY82`
  - `/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/0/FJ/G96Q2MF7IYN9KKV0LXION7`
  - `/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/1/NP/DMEYN4DNRKLYJNBYLIUVGQ`
  - `/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/C/9H/J5CZ0O2HI2RVLR1JFEP9MG`
  - `/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/2/WQ/I2XHAT3DUBJ2L4R4O666FQ`
- Evidence: `/private/tmp/abv_tea_furniture_live_probe_v1.json`, `/private/tmp/abv_tea_furniture_material_apply_v1.json`, `/private/tmp/abv_tea_furniture_material_exact_save_v1.json`, and `/private/tmp/abv_tea_furniture_review_v1/`.
- Filesystem mtimes advanced for exactly the six intended packages and authoritative Unreal dirty-package state returned to zero after the exact save.
## 2026-08-16 SS_004 Tea House canopy finish

- Exact live audit confirmed `Tea_Canopy` was still a visible 650 x 360 x 10 cm LevelPrototyping cube with `BlockAll` collision/navigation, supported by four 12 x 12 x 290 cm square LevelPrototyping poles.
- Converted the existing canopy actor in place to the owned Nanite wrinkled-tarp mesh `/Game/Maps/Sunscar/Art/Heritage/Props/WrinkledTarp/vieldbo_tier_1/StaticMeshes/vieldbo_tier_1` at uniform scale `2.35`, retaining the original footprint center and exact underside elevation. Its authored material `MI_ABV_WrinkledTarp` is retained; decorative canopy collision/navigation are disabled.
- Converted the four existing square pole actors in place to `/Engine/BasicShapes/Cylinder`, retaining every pole's exact occupied bounds and `BlockAll` visible collision while disabling navigation relevance.
- Production labels: `ABV_SS_004_TeaCanopy_WrinkledTarp_V1` and `ABV_SS_004_TeaCanopyPost_A_V1` through `_D_V1`.
- Exact saved packages:
  - `/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/B/IH/34H0PQZSSOXR897P94LVES`
  - `/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/C/ED/POI1E3KOM10RTQOK1N31A7`
  - `/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/9/UY/RJK3QSTJ3AEPS76OF5H4DO`
  - `/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/D/W2/L0RCJFMQ1R37983RZXNJNK`
  - `/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/C/WF/QE7EGS4TU1KQGJN22HQ8J0`
- Evidence: `/private/tmp/abv_tea_canopy_live_probe_v1.json`, `/private/tmp/abv_tea_canopy_apply_v1.json`, `/private/tmp/abv_tea_canopy_exact_save_v1.json`, and `/private/tmp/abv_tea_canopy_review_v1/`.
- Player-height/elevated review confirms the tarp reads as a fabric shade, its poles meet the canopy and terrain, circulation and furniture remain unobstructed, exact five-file mtimes advanced, and authoritative dirty state returned to zero.
## 2026-08-16 SS_003 Pump Station utility finish

- Exact live audit found `Pump_Utility_01` and `Pump_Utility_02` were still solid LevelPrototyping control-box cubes with `BlockAll`/navigation, while `Pump_Utility_03` was an 18 x 18 x 240 cm square metal cue hanging in the south doorway.
- Converted the two control-box actors in place to the owned Nanite Quixel `Electrical_Box_tdgecegda_High` mesh with its authored material; decorative collision/navigation/overlaps are disabled.
- Converted the square mast to a round Engine cylinder, then moved it out of the doorway to the west wall as `ABV_SS_003_WestWallDownpipe_V1`, half-set into the facade and nonblocking. The south entrance is now visually and physically clear.
- Production labels: `ABV_SS_003_NorthPumpControlBox_V1`, `ABV_SS_003_SouthPumpControlBox_V1`, and `ABV_SS_003_WestWallDownpipe_V1`.
- Exact saved packages:
  - `/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/9/ES/X6MN4NF3ZXORLDXG3KBYHE`
  - `/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/E/0J/OML53APQGJOCRYZZ2988YI`
  - `/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/2/86/21BUOVJ4Z8IVVH4XKRYHR5`
- Evidence: `/private/tmp/abv_ss003_pump_utilities_live_v1.json`, `/private/tmp/abv_ss003_pump_utilities_apply_v1.json`, `/private/tmp/abv_ss003_service_mast_refit_v1.json`, `/private/tmp/abv_ss003_pump_utilities_exact_save_v1.json`, and before/after captures under `/private/tmp/abv_ss003_pump_utilities_*_v1/`.
- Exact three-file mtimes advanced and authoritative Unreal dirty-package state returned to zero.

## 2026-08-16 SS_017 Covered Bazaar stall-body finish

- Fresh player-height closure captures proved the eight intentional
  `Bazaar_[N/S]_Stall_01..04` low-cover bodies still read as dark blockout
  cubes even though their positions, dimensions and collision layout were
  valid. Each existing actor remains an exact `320 x 250 x 90 cm` market
  counter with its original transform and `BlockAll` gameplay collision.
- Finished the four north and four south actors in two separately gated
  four-package batches by applying the existing world-aligned Abiverd
  ruin-brick material. Production labels are
  `ABV_SS_017_BazaarMasonryStall_N01_V1` through `_N04_V1` and
  `ABV_SS_017_BazaarMasonryStall_S01_V1` through `_S04_V1`.
- Navigation relevance, overlap events, replication and tick are disabled;
  the intentional visible low-cover collision remains. No transforms,
  dimensions, building pieces, routes or shared materials were changed.
- UE 5.8 Python note: `Transform.equals()` accepts no tolerance argument in
  this wrapper. The first north actor was the sole dirty preview when that
  assertion failed; the recovery probe proved its exact ownership and state,
  and the batch resumed using explicit numeric transform comparisons before
  any save.
- Evidence: `/private/tmp/abv_ss017_stalls_finish_probe_v1.json`,
  `/private/tmp/abv_ss017_stalls_north_recovery_probe_v1.json`,
  `/private/tmp/abv_ss017_stalls_north_apply_v1.json`,
  `/private/tmp/abv_ss017_stalls_north_exact_save_v1.json`,
  `/private/tmp/abv_ss017_stalls_south_apply_v1.json`,
  `/private/tmp/abv_ss017_stalls_south_exact_save_v1.json`, and review images
  under `/private/tmp/abv_ss017_stalls_finish_review_v1/`.
- Exact mtimes advanced for the intended eight existing external-actor
  packages only, and authoritative Unreal dirty-package state returned to
  zero after both saves.

## 2026-08-16 Launch-building flat-roof material completion

- Exact live resolution confirmed five launch-area roof slabs were the only
  core flat roofs still using the generic `MI_OT_Metal` finish:
  `Core_SS_003_Roof`, `Core_SS_013_Roof`, `Core_SS_015_Roof`,
  `Core_SS_016_Roof`, and `Core_SS_018_Roof`.
- Changed only their material overrides to the existing authored
  `MI_OT_WeatheredConcreteGround_WorldAligned`, matching the already finished
  SS_004/005/007/010/011/012/017 roof system. Exact transforms, dimensions,
  `BlockAll` collision, navigation relevance and structural labels are
  unchanged. Added the existing horizontal-surface/review tags only.
- Review captures show the prior bright metallic slabs now read as restrained
  tan flat roofs while rooftop equipment remains untouched. Evidence:
  `/private/tmp/abv_launch_metal_roofs_probe_v1.json`,
  `/private/tmp/abv_launch_metal_roofs_apply_v1.json`,
  `/private/tmp/abv_launch_metal_roofs_exact_save_v1.json`, and images under
  `/private/tmp/abv_launch_metal_roofs_review_v1/`.
- Exactly five existing external-actor package mtimes advanced and
  authoritative Unreal dirty-package state returned to zero.

## 2026-08-16 Launch-building facade-conduit completion

- Sixteen remaining facade-conduit cues at SS_004, SS_005, SS_007, SS_010,
  SS_011, SS_012, SS_017 and SS_018 were verified live as thin square Engine
  cubes (`9 cm` section; `170–180 cm` runs), already nonblocking but still
  navigation-relevant.
- Converted the sixteen existing actors in place to Engine cylinders while
  preserving each exact occupied run length and center. The existing Old Town
  metal material is retained. Production labels follow
  `ABV_<site>_FacadeConduit_{Vertical,Horizontal}_V1`.
- All conduit components remain `NoCollision`; navigation relevance, overlap
  events, replication and tick are disabled. No building, route, material
  asset or structural actor was changed.
- Evidence is in the four probe/apply/exact-save sets:
  `/private/tmp/abv_ss004_ss005_conduits_*_v1.json`,
  `/private/tmp/abv_ss007_ss010_conduits_*_v1.json`,
  `/private/tmp/abv_ss011_ss012_conduits_*_v1.json`, and
  `/private/tmp/abv_ss017_ss018_conduits_*_v1.json`; close review images for
  the first verified pattern are under
  `/private/tmp/abv_ss004_ss005_conduits_review_v1/`.
- Exact mtimes advanced for the intended sixteen existing actor packages, in
  four separately gated batches; authoritative Unreal dirty state returned to
  zero after every exact save.

## 2026-08-16 Launch-building electrical-meter material completion

- Exact live resolution proved the four apparent remaining utility-meter
  cubes at SS_005, SS_007, SS_011 and SS_018 had already been converted to
  the owned Nanite Quixel `Electrical_Box_tdgecegda_High`; the stale inventory
  reflected their prior state.
- The remaining defect was a generic `MI_OT_Metal` override masking the
  imported mesh's authored Quixel material. Restored the authored
  `MI_OT_FAB_P1A_002_tdgecegda` on the four existing actors only.
- Meshes, full transforms, occupied bounds, labels, `NoCollision` and disabled
  navigation are unchanged. Evidence:
  `/private/tmp/abv_launch_remaining_meters_probe_v1.json`,
  `/private/tmp/abv_launch_remaining_meters_material_apply_v1.json`, and
  `/private/tmp/abv_launch_remaining_meters_material_exact_save_v1.json`.
  Exact four-package mtimes advanced and Unreal returned to zero dirty.

## 2026-08-16 Launch-building stone-threshold completion

- Exact live resolution found eight launch-area doorway thresholds at SS_003,
  SS_004, SS_005 and SS_007 still rendered with the generic metal finish.
  Their existing `143 x 48 x 8 cm` forms, positions and doorway clearances
  were already valid.
- Finished the existing actors in two separately gated four-package batches
  using the authored world-aligned
  `MI_OT_WeatheredConcreteGround_WorldAligned` material. Production labels
  identify the exact site and doorway orientation, from
  `ABV_SS_003_StoneThreshold_West_V1` through
  `ABV_SS_007_StoneThreshold_East_V1`.
- Preserved every transform and occupied bound. The decorative sills remain
  `NoCollision`; navigation relevance, overlap events, replication and tick
  are disabled. No doorway, building, Landscape, material asset or route was
  modified.
- UE 5.8 Python note: `StaticMeshComponent` does not expose
  `set_generate_overlap_events()` in this wrapper; use
  `set_editor_property('generate_overlap_events', False)`. The initial call
  stopped after the first actor became dirty in memory; the recovery gate
  accepted only that exact package, resumed idempotently and verified the
  intended four-package scope before saving.
- Evidence: `/private/tmp/abv_launch_thresholds_probe_v1.json`,
  `/private/tmp/abv_launch_thresholds_batch_a_apply_v1.json`,
  `/private/tmp/abv_launch_thresholds_batch_a_exact_save_v1.json`,
  `/private/tmp/abv_launch_thresholds_batch_b_apply_v1.json`, and
  `/private/tmp/abv_launch_thresholds_batch_b_exact_save_v1.json`.
  Exact mtimes advanced for the intended eight existing actor packages and
  authoritative Unreal dirty-package state returned to zero after each save.

## 2026-08-16 Launch rooftop-switchgear authored-material recovery

- An exact six-actor live probe compared the component overrides on the
  launch-area rooftop switchgear with each imported mesh's authored material.
  SS_003 and SS_015 alone still carried the inherited generic
  `MI_OT_Metal` override; SS_016 A/B/C and the SS_018 cabinet already matched
  their authored materials and were left untouched.
- Restored the authored Quixel `FAB_P1A_003_ullibjd/MatID_1` material on only
  `ABV_SS_003_RoofSwitchgear_V1` and
  `ABV_SS_015_RoofSwitchgear_V1`. Meshes, full transforms, bounds, collision,
  navigation, labels and the source asset remained unchanged.
- Evidence: `/private/tmp/abv_launch_roof_switchgear_material_probe_v1.json`,
  `/private/tmp/abv_ss003_ss015_roof_switchgear_material_apply_v1.json`, and
  `/private/tmp/abv_ss003_ss015_roof_switchgear_material_exact_save_v1.json`.
  Exactly two external-actor package mtimes advanced and authoritative Unreal
  dirty state returned to zero.

## 2026-08-16 SS_006 water-tower compound wall finish

- Exact live resolution proved the eight perimeter wall/lintel actors around
  the SS_006 water-tower compound were valid structural Engine-cube geometry
  with working `QueryAndPhysics` collision and navigation, but their bright
  `MI_OT_Stucco_WorldAligned` finish still read as prototype geometry.
- Changed only the material override on the north, west, south-left,
  south-right, east-left, east-right, east lintel and south lintel actors to
  the existing `MI_ABV_RuinBrick_WorldAligned`. Full transforms, bounds,
  openings, collision, navigation and structural labels were preserved.
- The eight actors were processed and exact-saved in two separately gated
  four-package batches. Review captures confirm the perimeter now reads as a
  coherent Abiverd ruin-brick compound rather than a white blockout:
  `/private/tmp/abv_ss006_compound_walls_review_v1/southwest_oblique.png` and
  `/private/tmp/abv_ss006_compound_walls_review_v1/east_player.png`.
- Evidence: `/private/tmp/abv_ss006_compound_walls_material_probe_v1.json`,
  `/private/tmp/abv_ss006_compound_walls_batch_a_apply_v1.json`,
  `/private/tmp/abv_ss006_compound_walls_batch_a_exact_save_v1.json`,
  `/private/tmp/abv_ss006_compound_walls_batch_b_apply_v1.json`, and
  `/private/tmp/abv_ss006_compound_walls_batch_b_exact_save_v1.json`.
  Exact eight-package mtimes advanced and authoritative Unreal dirty state
  returned to zero after each save.

## 2026-08-16 SS_006 water-tower pillar finish

- A fresh post-fix 13-site oblique set under
  `/private/tmp/abv_launch_buildings_oblique_v3/` confirmed the remaining
  large SS_006 blockout read was the `400 x 400 x 1200 cm`
  `Core_SS_006_TowerPillar`, still using smooth facade stucco beneath the
  already finished tower platform, metal braces and ruin-brick perimeter.
- Changed only that existing actor's material override to the established
  `MI_OT_WeatheredConcreteGround_WorldAligned`, giving the modern utility
  tower a weathered structural-concrete read. Its exact transform, bounds,
  `BlockAll` query-and-physics collision, navigation and overlap state were
  numerically preserved.
- Review images are under
  `/private/tmp/abv_ss006_tower_pillar_finish_review_v1/`. Exact evidence:
  `/private/tmp/abv_ss006_tower_pillar_finish_probe_v1.json`,
  `/private/tmp/abv_ss006_tower_pillar_finish_apply_v1.json`, and
  `/private/tmp/abv_ss006_tower_pillar_finish_exact_save_v1.json`.
  The one intended actor package mtime advanced and authoritative Unreal dirty
  state returned to zero.
- The four bright small SS_006 ground units were separately resolved as the
  intentionally upgraded `Tower_Utility_01..04` Quixel electric boxes with
  saved terrain-conformed transforms, not leftover graybox cubes. A current
  player-height comparison nevertheless proved the source-white material still
  read like four editor blocks against the finished compound. Following the
  already accepted SS_018 ground-cabinet precedent, only their component
  material overrides now use the existing weathered `MI_OT_Metal`.
- The Quixel meshes, exact full transforms, `112.09 x 26.38 x 107.67 cm`
  occupied dimensions, query-and-physics collision, disabled navigation and
  source assets are unchanged. Review:
  `/private/tmp/abv_ss006_utility_finish_review_v1.png`; exact evidence:
  `/private/tmp/abv_ss006_utility_finish_apply_v1.json` and
  `/private/tmp/abv_ss006_utility_finish_exact_save_v1.json`. Exactly four
  actor-package mtimes advanced and authoritative Unreal dirty state returned
  to zero.

## 2026-08-16 SS_015 oil-stain decal experiment and rollback

- The scoped imported-content inventory found no existing project decal
  material, but did confirm the owned Quixel oil-stain texture set under
  `/Game/Maps/Sunscar/Art/Quixel/Downloaded/FAB_SUP_003_sdjmigi/`.
- Created and exact-saved the map-art material
  `/Game/Maps/Sunscar/Art/Heritage/Materials/M_ABV_OilStain_Decal` using the
  existing Quixel base-color and opacity textures, translucent deferred-decal
  domain, and constant roughness `0.82`. No source Quixel asset was edited.
- UE 5.8 Python/API lesson: `Material.decal_blend_mode` is deprecated and
  protected, and `Material.expressions` is also protected. Configure modern
  decals with `material_domain=MD_DEFERRED_DECAL`, a supported blend mode and
  explicit material-output connections; retain direct references to created
  expressions instead of attempting to read the protected expression array.
- A single unsaved preview actor,
  `ABV_SS_015_MotorPool_OilStain_A_V1`, was tested on the exactly traced
  `Core_SS_015_F1_Floor`. The floor support was level, but targeted top-down,
  oblique and player-height captures did not prove a readable decal on that
  receiver. The pilot therefore failed visual acceptance and was rolled back
  rather than saved.
- Rollback verification: the preview actor is absent, its proposed external
  actor package
  `/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/7/MM/6SCJ4YH0X0TACPRXHTL1EC`
  has no file on disk, and authoritative Unreal dirty state returned to zero.
  Do not repeat this exact SS_015 receiver test without first proving the
  floor's decal-receive/render path. Evidence:
  `/private/tmp/abv_decal_asset_inventory_v1.json`,
  `/private/tmp/abv_decal_api_probe_v1.json`,
  `/private/tmp/abv_oilstain_decal_material_apply_v1.json`,
  `/private/tmp/abv_oilstain_decal_material_exact_save_v1.json`,
  `/private/tmp/abv_ss015_oilstain_preflight_v1.json`,
  `/private/tmp/abv_ss015_oilstain_review_v2/`, and
  `/private/tmp/abv_ss015_oilstain_rollback_v1.json`.

## 2026-08-16 SS_013 Freight Depot east-facade production polish

- A fresh Game View/player-height review exposed the Freight Depot east
  approach as a concrete remaining flat-elevation defect: approximately
  24 m of flaked-plaster facade around the existing 2 m loading opening had no
  depth rhythm.
- Added three visual-only instances to the existing
  `ABV_OldTown_PakistanWallFacade_HISM_V1` actor's
  `HISM_PakistanWallModular16` component. World locations are
  `(12329.289,-850,34780.028)`, `(12329.289,-225,34780.028)` and
  `(12329.289,1000,34780.028)`, all yaw `90`, uniform scale `1`.
- Direct wall traces proved the three placements are on the two solid east
  shell bays; direct downward traces hit only Landscape at approximately
  Z `34779.5`. The closest pier remains 625 cm from the loading opening. The
  building shell, opening, routes, Landscape, collision and navigation were
  unchanged.
- The existing shared HISM component remains `NoCollision`, non-navigable and
  now contains 41 instances. Only its existing external-actor package
  `/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/4/XJ/GOWVSDB53YHV8I1OQ2ZTN7`
  was exact-saved; its mtime advanced and authoritative Unreal dirty state
  returned to zero.
- Before/after player-height evidence is under
  `/private/tmp/abv_ss013_east_facade_piers_review_v1/`; exact evidence:
  `/private/tmp/abv_ss013_east_facade_piers_preflight_v1.json`,
  `/private/tmp/abv_ss013_east_facade_piers_preview_v1.json`,
  `/private/tmp/abv_ss013_east_facade_piers_refine_v1.json`, and
  `/private/tmp/abv_ss013_east_facade_piers_exact_save_v1.json`.

## 2026-08-16 launch-area Landscape Rock-layer surface correction

- A six-view Game View review exposed oversized pale stone/shard repetition
  across the central initial-launch routes. A bounded nine-point direct trace
  and paint-weight readback proved the visible receiver was Landscape and that
  the dominant painted layer was `Rock` (generally weight `1.0`), not `Sand`.
  This explains why a compiled unsaved Historic Desert Ruin Floor Sand Coarse
  replacement on the Sand branch produced no meaningful visual improvement.
  That first one-material preview was discarded; the material package was
  reloaded and authoritative dirty state returned to zero.
- The accepted reuse-first correction changes only the existing
  `/Game/Maps/Sunscar/Art/Materials/LandscapeV3/M_OT_Landscape_Abiverd`
  material. The `Rock_BaseColor` and `Rock_Normal` defaults now use the already
  imported owned Dry Trampled Soil texture set, retaining the existing
  `Rock_TileCm=260`. `Rock_Tint` is `(0.88,0.80,0.68,1)`.
- The existing shared macro branch now also samples Dry Trampled Soil at
  `12000 cm`, with strength `0.12` and floor `(0.90,0.90,0.90,1)`. This keeps
  low-frequency variation while removing the previous 36 m rocky macro's dark
  repetition. No Landscape proxy, height, weightmap, Grass layer, texture
  bombing function, source texture, or shared source material was changed.
- Matched launch-route captures show the central surface now reads as compacted
  semi-arid soil rather than oversized trench rock. The accepted field-edge
  capture confirms the localized Grass/poppy presentation remains intact.
  Review: `/private/tmp/abv_landscape_rock_drysoil_preview_review_v1/`.
  Read-only cause evidence:
  `/private/tmp/abv_center_route_surface_probe_v1.json`; exact-save evidence:
  `/private/tmp/abv_landscape_rock_drysoil_exact_save_v1.json`.
- Compile errors were zero; only the material package was dirty/saved, its mtime
  advanced, and authoritative Unreal dirty state returned to zero.

## 2026-08-16 launch-area Sand/base harmonization and central furniture finish

- The Landscape material correction was completed across the remaining base
  branch: `Sand_BaseColor` and `Sand_Normal` now reuse the same imported Dry
  Trampled Soil set, with `Sand_TileCm=260` and `Sand_Tint=(0.92,0.84,0.72,1)`.
  The existing Sand texture-bombing graph remains connected and unchanged.
  The material compiled with zero errors, was exact-saved, and returned to zero
  authoritative dirty packages. Evidence:
  `/private/tmp/abv_landscape_sand_drysoil_preview_review_v1/` and
  `/private/tmp/abv_landscape_sand_drysoil_exact_save_v1.json`.
- The remaining pale courtyard island was proven to be the visible legacy
  decal `OT_EXT_Ground_CourtyardConnector_02`, not Landscape or a ground
  overlay. Its oversized `MI_Decal_Debris_Dirt_01_A` projection washed out the
  corrected terrain. The actor was preserved, while only its decal component
  was made invisible and hidden in game. Exact package
  `/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/9/U3/17IINK4HIYF2F4Q4E1C68M`
  was saved; zero dirty packages remained. Evidence:
  `/private/tmp/abv_courtyard_connector_decal_disabled_v1.png` and
  `/private/tmp/abv_courtyard_connector_decal_disable_exact_save_v1.json`.
- Replaced the four SS_009 plaza cube benches with the already owned Quixel
  `Wooden_Bench_vlroadt_High`, using its existing material, uniform scale
  `1.4`, original layout axes, and a verified `2 cm` Landscape embed. The four
  production labels are `ABV_SS_009_PlazaBench_01_V1` through `_04_V1`.
  Collision matches visible geometry; navigation and overlaps are disabled.
  Exactly four external-actor packages were saved. Evidence:
  `/private/tmp/abv_plaza_benches_preflight_v1.json`,
  `/private/tmp/abv_plaza_benches_before_v1/`,
  `/private/tmp/abv_plaza_benches_after_v1/`, and
  `/private/tmp/abv_plaza_benches_exact_save_v1.json`.
- Replaced all six SS_008 courtyard cube benches with the same proven Quixel
  bench and material. Labels are `ABV_SS_008_CourtyardBench_01_V1` through
  `_06_V1`; four retain the east-west arrangement and two retain the
  north-south arrangement. Each is uniformly scaled `1.4`, directly
  terrain-conformed with a verified `2 cm` embed, collision-enabled, and
  non-navigable/non-overlapping. Exactly six external-actor packages were
  saved and authoritative dirty state returned to zero. Evidence:
  `/private/tmp/abv_courtyard_benches_preflight_v1.json`,
  `/private/tmp/abv_courtyard_benches_before_v1/`,
  `/private/tmp/abv_courtyard_benches_after_v1/`, and
  `/private/tmp/abv_courtyard_benches_exact_save_v1.json`.
- Finished the four SS_009 plaza lamp assemblies without adding shared assets.
  Each square prototype shaft now uses `/Engine/BasicShapes/Cylinder` with the
  existing `MI_OT_Metal`, exact support contact, query-and-physics collision,
  disabled nav/overlaps/tick/replication, and a production label
  `ABV_SS_009_PlazaLampPole_01_V1` through `_04_V1`. The fourth pole's former
  234 cm overrun above its lamp head was removed; all four pole tops now meet
  their heads at Z `35257.805`. Existing head geometry/transforms were
  preserved, changed from bright Accent to Metal, renamed
  `ABV_SS_009_PlazaLampHead_01_V1` through `_04_V1`, and made non-colliding and
  non-navigable because they are overhead decorative housings. Exactly four
  pole and four head packages were exact-saved. Evidence:
  `/private/tmp/abv_plaza_lamp_poles_preflight_v1.json`,
  `/private/tmp/abv_plaza_lamp_poles_apply_v1.json`,
  `/private/tmp/abv_plaza_lamp_poles_exact_save_v1.json`,
  `/private/tmp/abv_plaza_lamp_heads_apply_v1.json`,
  `/private/tmp/abv_plaza_lamp_heads_exact_save_v1.json`, and
  `/private/tmp/abv_plaza_lamp_poles_review_v1/`.
- Converted the four nearly buried bright SS_008 courtyard planter blocks into
  grounded `120 x 120 x 55 cm` ruin-brick plinth/planters using the existing
  chamfered geometry and `MI_ABV_RuinBrick_WorldAligned`. Each has a verified
  `2 cm` embed, visible collision, and disabled nav/overlaps. Labels are
  `ABV_SS_008_CourtyardPlanter_01_V1` through `_04_V1`. Exactly four packages
  were exact-saved. Evidence:
  `/private/tmp/abv_courtyard_planters_preflight_v1.json`,
  `/private/tmp/abv_courtyard_planters_apply_v1.json`, and
  `/private/tmp/abv_courtyard_planters_exact_save_v1.json`.
- Material-finished all seven `Building_CentralCourtyard` perimeter pieces in
  two exact-save batches. The bright smooth facade stucco was replaced only on
  those wall actors with the established world-aligned Abiverd ruin brick.
  Geometry, gate openings, transforms, `BlockAll` collision and navigation
  remained unchanged. Evidence:
  `/private/tmp/abv_central_courtyard_shell_inventory_v1.json`,
  `/private/tmp/abv_central_courtyard_walls_batch_a_apply_v1.json`,
  `/private/tmp/abv_central_courtyard_walls_batch_a_exact_save_v1.json`,
  `/private/tmp/abv_central_courtyard_walls_batch_b_apply_v1.json`,
  `/private/tmp/abv_central_courtyard_walls_batch_b_exact_save_v1.json`, and
  the final courtyard views under
  `/private/tmp/abv_courtyard_benches_after_v1/`.
- A tag-scoped audit found 96 tiny SS_008/SS_009 ground debris, grass and
  market-scatter actors still had query-and-physics collision, navigation and
  overlap generation. They measured only about `2–104 cm` and are visual
  micro-dressing, not tactical cover. Corrected them in nine independently
  gated exact-save batches of 10–12 packages: collision `NoCollision`, nav and
  overlaps disabled, non-replicated, and tick disabled. Meshes, materials,
  transforms, bounds and visibility were numerically preserved. Consolidated
  re-audit proves all `96/96` have the intended settings and Unreal dirty state
  is zero. Evidence:
  `/private/tmp/abv_ss008_ss009_microprops_inventory_v1.json` and
  `/private/tmp/abv_microprops_cleanup_*_v1.json`.
- Finalized the six remaining SS_008 courtyard-furniture actors. Two existing
  Quixel benches retain visible collision and now use production labels
  `ABV_SS_008_CourtyardBench_07_V1` and `_08_V1`. Four oil-pack, storage-box
  and jerrycan micro-props are visual dressing only and now use `NoCollision`,
  no navigation, no overlaps, no tick and no replication. Their meshes,
  materials and transforms were preserved. Exactly six actor packages were
  saved and authoritative dirty state returned to zero. Evidence:
  `/private/tmp/abv_ss008_furniture_finalize_v1.json`.
- Closed the last ten `UnreviewedAutomationPlacement` storage actors in
  SS_008. The two genuinely knee-high crates (about 26–30 cm tall) retain
  visible `BlockAll` collision; eight flat lids/small debris pieces (about
  5–18 cm tall) are non-colliding visual dressing. All ten are non-navigable,
  non-overlapping, non-replicated and non-ticking, and now carry explicit
  `ABV_SS_008_Storage*` production labels plus `ReviewedProductionPlacement`.
  Geometry, source meshes, materials, transforms and bounds were preserved.
  Exactly ten external-actor packages were saved; mtimes advanced and
  authoritative dirty state returned to zero. Evidence:
  `/private/tmp/abv_ss008_ss009_remaining_unreviewed_v1.json` and
  `/private/tmp/abv_ss008_storage_finish_v1.json`.
- Completed the same production-state normalization for every remaining
  visible `UnreviewedAutomationPlacement` actor in the loaded launch sites:
  `110/110` actors across SS_003, SS_004, SS_005, SS_006, SS_007, SS_010,
  SS_011, SS_013, SS_015, SS_016, SS_017 and SS_018. Work was split into
  twelve independently gated batches of at most twelve packages. Tables,
  stools, benches, large electrical boxes/cabinets and substantial rocks
  retain visible `BlockAll` collision. Wall-mounted small utility boxes,
  loose containers, lids, tiny storage/scrap, ground patches and vegetation
  use `NoCollision`. All reviewed actors are non-navigable, non-overlapping,
  non-replicated and non-ticking, with production `ABV_<site>_*_V1` labels.
  Source meshes, materials, transforms and bounds were preserved numerically.
  Every package mtime advanced only in its authorized exact-save batch, and
  authoritative dirty state returned to zero after each batch. The closing
  exact-tag audit proves `count=0`, no remaining visible unreviewed launch-area
  actors, and zero dirty packages. Evidence:
  `/private/tmp/abv_launch_remaining_unreviewed_v1.json` and
  `/private/tmp/abv_unreviewed_*_v1.json`.

## 2026-08-17 launch-building exterior acceptance continuation

- Material-finished the seven remaining generic stucco shell pieces on
  `SS_004` Tea House with the already established
  `MI_ABV_CrackedMud_WorldAligned`. The north wall already used that finish;
  east left/lintel/right, south wall, and west left/lintel/right now match it.
  Geometry, transforms, collision, doors, windows, canopy and visible
  parapets were preserved. Exactly seven external-actor packages were saved,
  all mtimes advanced, and authoritative Unreal dirty state returned to zero.
  Evidence: `/private/tmp/abv_ss004_shell_preview_v2/` and
  `/private/tmp/abv_ss004_shell_crackedmud_exact_save_v2.json`.
- Recovery lesson: do not call `reload_packages` on a loaded World Partition
  external-actor package to discard a transient preview. In UE 5.8 this pinned
  the isolated editor at full CPU and made the bridge unresponsive. The exact
  editor PID was terminated only after command-line revalidation; the project
  reopened without restoring autosaves, and the affected package was proven
  clean from disk. Prefer an exact save after a validated gate, or a controlled
  editor close/reopen with Don't Save for transient preview rollback. Never use
  World Partition descriptor/intersection scripts as a substitute.
- Fresh current-state review accepted the `SS_018` Telecom Workshop exterior.
  The saved weathered/flaked north ground storey, heritage piers, blue telecom
  frontage, roof service equipment, ramp/landing and grounded facade contact
  are intact. No new change was required. Evidence:
  `/private/tmp/abv_ss018_current_review_v2/`.
- Finished the `SS_007` Municipal Hotel upper shell. Exact live audit proved
  all ten second/third-storey wall pieces still used the bright prototype
  `MI_OT_Stucco_WorldAligned`, while the ground storey was already finished in
  ruin brick. Changed only those ten material overrides to the established
  `MI_OT_FlakedPaint_WorldAligned`; transforms, floors, openings, collision,
  navigation, balconies, doors/windows and source geometry were preserved.
  Exactly ten external-actor packages were saved, every mtime advanced, and
  authoritative dirty state returned to zero. The hotel now reads as a
  coherent weathered masonry building from north/east/west approaches instead
  of exposing white blockout storeys. Evidence:
  `/private/tmp/abv_ss007_upper_shell_material_audit_v1.json`,
  `/private/tmp/abv_ss007_upper_shell_flaked_exact_save_v1.json`, and
  `/private/tmp/abv_ss007_current_close_review_v2/`.
- UE Python durability note: `Vector.equals` in this UE 5.8 Python binding does
  not accept a tolerance argument. Compare numeric transform components
  explicitly. Also call both `actor.modify()` and `component.modify()` before
  `set_material`; otherwise an in-memory material override can change without
  producing the expected external-actor dirty package. The first attempt was
  unsaved and was safely completed by the corrected exact-package script.
- Fresh close player-height, oblique and elevated review accepted the `SS_017`
  bazaar/market exterior after the production-state actor normalization. The
  north market bays retain grounded masonry counters, weathered plaster,
  opening shade pieces and a clear primary doorway; the south frontage retains
  the darker ruin-brick market identity and finished counter/stall composition.
  No runtime floating or embedded exterior defect was proven, so no actor was
  changed. The green wireframes visible in some editor captures are editor
  volume visualization, not runtime geometry. Evidence:
  `/private/tmp/abv_ss017_north_bazaar_storefront_review_v2/` and
  `/private/tmp/abv_ss017_stalls_finish_review_v2/`.
- With `SS_004`, `SS_007`, `SS_017` and `SS_018` rechecked in this continuation,
  the existing 13-site launch-building exterior first-art/design-draft gate
  remains valid. Further systematic building mutation is closed unless a new
  exact player-height defect is proven. Work continues directly into the
  launch-area road, ground-transition and placed-ground-asset finish rather
  than reopening completed shells.
- Added one bounded runtime storytelling decal to the `SS_015` motor-pool
  floor: `ABV_SS_015_MotorPool_OilStain_A_V2`, using the already saved
  `M_ABV_OilStain_Decal` deferred-decal material. The receiver floor was
  explicitly verified to receive decals, five direct support samples proved a
  flat `Z=34814.10 cm` surface, and player-height/top review proved the stain
  reads as a restrained irregular vehicle-service mark without collision or
  traversal impact. Exactly one new LFS-managed external-actor package was
  saved; authoritative dirty state returned to zero. Evidence:
  `/private/tmp/abv_ss015_oilstain_retry_gate_v2.json`,
  `/private/tmp/abv_ss015_oilstain_review_v3/`, and
  `/private/tmp/abv_ss015_oilstain_retry_exact_save_v2.json`.
- Decal rotation durability note: the earlier apparently invisible SS_015
  preview did **not** prove a receiver/material incompatibility. It used a
  positional `unreal.Rotator(...)` call whose argument ordering did not match
  the intended pitch/yaw/roll. For downward UE decals in this workflow, use
  named fields and verify the readback, e.g.
  `unreal.Rotator(pitch=-90.0, yaw=12.0, roll=0.0)`. The corrected named-field
  rotation made the same saved decal material render correctly.
- Broke the repeated launch-area roof treatment without changing gameplay
  geometry. An exact twelve-roof audit proved every principal roof used the
  same weathered-concrete surface. Modern/service buildings keep that finish;
  only the heritage-led `Core_SS_004_Roof`, `Core_SS_013_Roof`, and
  `Core_SS_017_Roof` now use the existing packed-earth
  `MI_OT_SandstoneSilt_WorldAligned`. Oblique and aerial review shows these
  three roofs now read as earthen Abiverd construction while the remaining
  concrete roofs retain their intended identity. Transforms, bounds,
  collision, navigation and source meshes were preserved. Exactly three
  external-actor packages were saved, all mtimes advanced, and authoritative
  dirty state returned to zero. Evidence:
  `/private/tmp/abv_launch_roof_finish_audit_v1.json`,
  `/private/tmp/abv_launch_wall_material_profile_v1.json`,
  `/private/tmp/abv_heritage_roofs_preview_v1/`, and
  `/private/tmp/abv_heritage_roofs_silt_exact_save_v1.json`.
- Added a restrained Tea House ground-transition treatment using one new
  map-owned deferred-decal wrapper and one non-colliding map actor. The wrapper
  reuses the imported Quixel mud-stain base color but uses the already verified
  irregular Quixel stain opacity silhouette at a `0.35` strength; the original
  Quixel mud opacity texture was visually rejected because it produced a hard
  rectangular boundary even after global opacity reduction. The accepted actor
  is `ABV_SS_004_TeaHouse_MudStain_A_V1`, terrain-supported on four fixed
  Landscape samples with zero measured variation and clear of doors/gates.
  The separate SS_017 candidate was rejected without mutation because one
  corner traced onto `ABV_SS_017_BazaarMasonryStall_S01_V1`. Exact-save scope
  was the new `M_ABV_MudStain_Decal` material plus the one Tea House external
  actor; both are LFS-managed and authoritative dirty state returned to zero.
  Evidence: `/private/tmp/abv_mudstain_transition_gate_v1.json`,
  `/private/tmp/abv_ss004_mudstain_preview_v3/`, and
  `/private/tmp/abv_ss004_mudstain_exact_save_v1.json`.
- Completed the launch-window navigation-cost cleanup without changing the
  buildings' appearance or gameplay collision. The exact audit covered 140
  visible window-frame/recess actors. Ninety-five collisionless decorative
  frame/glass actors incorrectly retained `CanEverAffectNavigation=true`; all
  95 now have it disabled while preserving transforms, source meshes,
  materials, visibility, collision, overlaps, component/actor tick and
  replication. The 15 remaining navigation-relevant actors are the colliding
  `SS_007` hotel window frames and were intentionally left unchanged. Work was
  exact-saved in batches of at most 12 packages; every authorized mtime
  advanced and authoritative dirty state returned to zero after every batch.
  Final audit: 140 reviewed, zero collisionless actors still navigation
  relevant, 15 intentionally colliding frames retained. Evidence:
  `/private/tmp/abv_launch_window_performance_audit_v1.json`,
  `/private/tmp/abv_window_nav_cleanup_recover_first_two_exact_save_v1.json`,
  and `/private/tmp/abv_window_nav_cleanup_batch02_exact_save_v1.json` through
  `/private/tmp/abv_window_nav_cleanup_batch09_exact_save_v1.json`.
- UE 5.8 Python durability note: changing
  `StaticMeshComponent.can_ever_affect_navigation` through
  `set_editor_property` updates the loaded component but may not mark its World
  Partition external-actor package dirty. After full property/ownership gates,
  use `EditorLoadingAndSavingUtils.save_packages(exact_packages, False)` to
  force-save only the explicitly authorized packages, then prove every mtime
  advanced and authoritative dirty state is zero. Also serialize transforms as
  numeric translation/quaternion/scale values for preservation checks; the
  string representation embeds a temporary struct address and cannot be
  compared reliably.
- Completed a second structural-material closeout across 353 visible launch-
  area structural actors. The exact audit found 15 exterior shell pieces still
  using the plain `MI_OT_Stucco_WorldAligned` finish: the four second-storey
  walls of `SS_005` Clinic and eleven first/second-storey exterior wall pieces
  of `SS_018` Telecom Workshop. Those 15 pieces now use the already accepted
  `MI_OT_FlakedPaint_WorldAligned`, producing a visibly weathered finish that
  matches the established lower-storey treatment. Meshes, transforms,
  openings, collision and navigation were preserved. The four clinic packages
  and eleven telecom packages were exact-saved; every mtime advanced and dirty
  state returned to zero. Player-height, oblique and elevated evidence:
  `/private/tmp/abv_ss005_upper_finish_preview_v1/` and
  `/private/tmp/abv_ss018_shell_finish_preview_v1/`. Exact-save evidence:
  `/private/tmp/abv_ss005_upper_finish_exact_save_v1.json` and
  `/private/tmp/abv_ss018_shell_finish_exact_save_v1.json`.
- The post-save structural audit leaves exactly 14 stucco candidates, all named
  `Core_<site>_Interior_A/B`. They are intentional interior/occlusion pieces,
  not exposed exterior shell; there are zero remaining exterior stucco
  candidates. Evidence:
  `/private/tmp/abv_launch_structural_material_closeout_audit_v1.json`.
- Deterministic review-capture note: teleporting the editor viewport can feed
  the temporal motion-blur history and produce unusably smeared captures. For
  review only, set the editor-session cvars `r.MotionBlurQuality 0` and
  `r.MotionBlur.Amount 0`, then capture a warm-up frame before the retained
  frame. This changes no project config or asset.
- Closed the launch-area default/prototype-material category. An exact-tag
  read-only audit reviewed 904 visible runtime static-mesh actors across the 13
  launch sites and found zero actors using WorldGrid, DefaultMaterial,
  BasicShapeMaterial, LevelPrototyping materials, prototype materials or null
  material slots (intentional interior A/B pieces and editor/collision helpers
  excluded). No mutation was required. Evidence:
  `/private/tmp/abv_launch_visible_default_material_audit_v1.json`.
- Completed the remaining visible static-actor performance policy. The
  read-only gate covered the same 904 visible launch-area static actors and
  found zero replicated, ticking or overlap-generating actors, but 108
  collisionless exterior details still had navigation relevance enabled. The
  affected set was limited to decorative signs, shutters, drains/outlets, mast
  bases, small roof utilities and industrial dressing. Collisionless state and
  exact ownership were revalidated per actor; only
  `CanEverAffectNavigation=false` changed. Work was force-saved in nine exact
  12-package batches because this UE 5.8 component flag does not reliably mark
  external-actor packages dirty. Every authorized mtime advanced and dirty
  state remained zero. The post-save audit proves `no_collision_nav_count=0`
  and `runtime_overhead_count=0`. Evidence:
  `/private/tmp/abv_launch_static_actor_performance_policy_audit_v1.json` and
  `/private/tmp/abv_launch_static_nav_cleanup_batch01_exact_save_v1.json`
  through `/private/tmp/abv_launch_static_nav_cleanup_batch09_exact_save_v1.json`.
- Coverage correction: the original launch list includes `SS_006`; a draft of
  the second-pass query accidentally included `SS_020` in its place. Before
  closeout, `SS_006` was added back to every gate and all three audits were
  rerun. Its nine structural actors and 40 visible static actors produced zero
  exposed-stucco, default/prototype-material, collisionless-nav, tick,
  replication or overlap findings. The retained audit reports above contain
  the corrected 353-structural/904-visible totals.
- Reconfirmed launch-region HLOD participation without invoking World
  Partition descriptor, intersection, region-loading or builder APIs. All 885
  loaded visible launch-site actors are spatially loaded, use the default
  runtime grid, have automatic HLOD generation enabled and have no explicit
  per-actor HLOD override. This agrees with the existing valid instanced and
  merged HLOD-layer configuration. No generated HLOD build was started because
  an unfiltered builder would create a mass whole-world package delta against
  the accumulated unstaged map scope. Evidence:
  `/private/tmp/abv_launch_hlod_loaded_actor_audit_v1.json`.
- A visible duplicate-placement closeout reviewed the same 885 launch-site
  StaticMeshActors and found zero duplicate groups at 0.1 cm translation,
  0.01-degree rotation and 0.0001 scale precision. No actor was deleted or
  moved. Evidence:
  `/private/tmp/abv_launch_visible_duplicate_geometry_audit_v1.json`.
- Removed unnecessary full shadow casting from exactly 13 tiny (13.4-27.0 cm)
  collisionless industrial scrap/spring fragments at `SS_013` and `SS_017`.
  Meshes, transforms, materials, visibility, collision, navigation, overlap,
  tick and replication state were preserved. The component render flag did not
  mark World Partition actor packages dirty, so the two bounded batches used
  the established force-save rule on exactly eight then five owned packages;
  every mtime advanced and authoritative dirty state returned to zero. The
  post-save shadow audit reports zero remaining actors in the selected
  micro-scrap class. Evidence:
  `/private/tmp/abv_launch_small_decor_shadow_audit_v1.json`,
  `/private/tmp/abv_launch_micro_scrap_shadow_cleanup_batch01_exact_save_v1.json`
  and
  `/private/tmp/abv_launch_micro_scrap_shadow_cleanup_batch02_exact_save_v1.json`.
- Added two restrained localized ground-transition accents using the existing
  map-owned `M_ABV_MudStain_Decal`: `ABV_SS_005_Clinic_MudStain_A_V1` in the
  clinic forecourt and `ABV_SS_007_Hotel_MudStain_A_V1` on the hotel approach.
  Five fixed Landscape samples per site proved flat/near-flat support (0.0 cm
  and 0.19 cm variation) with 5.60 m and 3.84 m clearance from the nearest
  entrance actors. Both decals are non-replicated, non-ticking, non-colliding,
  use the established irregular 0.35-opacity treatment and remain outside the
  door thresholds. Each actor/component serializes in one new external-actor
  package; the two packages were exact-saved separately and both saves returned
  to authoritative zero dirty state. Evidence:
  `/private/tmp/abv_launch_entrance_mudstain_gate_v1.json`,
  `/private/tmp/abv_entrance_mudstain_review_v1/`,
  `/private/tmp/abv_ss005_clinic_mudstain_exact_save_v1.json` and
  `/private/tmp/abv_ss007_hotel_mudstain_exact_save_v1.json`.
- The complete launch-exterior acceptance gate was rerun after these changes
  and passed all checks: clean editor context, Landscape material, 288 hidden
  legacy overlays, field-edge and north-meadow HISM policy, foliage instancing
  usage, wall-foot/road shoulders, SS_013 ruin cluster, twelve launch sandbag
  barriers, fifty core-route materials and sixteen decorative Quixel ground
  actors. It covered 3,375 loaded actors and returned to zero dirty packages.
  Evidence: `/private/tmp/abv_launch_exterior_final_acceptance_v2.json`.
- UE's registered validators returned `Valid` with zero errors or warnings for
  the two new entrance decals, the existing Tea House and motor-pool decals,
  the field-edge HISM actor, all three SS_013 ruin actors, both map-owned decal/
  foliage materials and both HLOD-layer assets. Evidence:
  `/private/tmp/abv_launch_exact_object_validation_v1.json`.
- Current repository scope remains intentionally unstaged and map-only: 912
  modified plus 80 untracked files (992 total), staged count zero. A full path
  classifier found no paths outside the map's external actor/object packages,
  the already approved map-owned/Quixel materials and this handoff document.
  Local and remote `feature/map-development` remain
  `e0b856c20cdad11f7057248c851d4d344f43fbe1`; no stage, commit, push, merge or
  rebase was performed.
- The existing deterministic gameplay-route audit was rerun from its committed
  repository script after map closeout. All 50 audited Old Town routes passed;
  the narrowest retained route is 300 cm and no route requires review. Evidence:
  `Saved/OperationSunscar/Reports/old_town_gameplay_route_audit_v1.json`.
- A separate exact spawn/support audit resolved all eight loaded PlayerStarts.
  Every start is Landscape-supported, pairwise start spacing is at least 800 cm
  and support deltas are 2.46-7.40 cm. The four attacker-start overlap results
  resolve only to the intentional `CoreVolume_AttackerExtraction` TriggerBox,
  not physical blocking geometry. No NavMeshBoundsVolume/RecastNavMesh is
  loaded; navigation generation remains a separately scoped AI/navigation
  task rather than part of this player-route exterior pass. Evidence:
  `/private/tmp/abv_launch_spawn_nav_audit_v1.json`.
- UE's current-world validator also returned `Valid` with zero errors and zero
  warnings in 0.04 seconds, with zero authoritative dirty packages. Evidence:
  `/private/tmp/abv_current_world_validation_v1.json`.
- The final deterministic eight-view review is retained at
  `/private/tmp/abv_launch_exterior_final_review_v7/`. Three elevated views and
  five player-height approach/site views confirm the thirteen initial-launch
  building exteriors, perimeter walls, entrances, ground contacts and seasonal
  SS_013 field edge remain readable and coherent at the intended scale. Distant
  partially loaded/prototype silhouettes visible beyond the bounded playable
  launch area are not part of these thirteen accepted building sites and were
  not mutated during closeout; they remain a later world-vista/streaming scope,
  not an exterior-building regression.
- Git attributes were checked for the new material/map packages and resolve to
  LFS filter/diff/merge handling. `git lfs status` contains no staged work and
  no commit/push operation was performed. The next production-scale map step
  is a controlled HLOD build/checkpoint; do not run an unfiltered whole-world
  HLOD builder against this accumulated unstaged World Partition scope.
- Final hygiene check: the generated tracked Python bytecode cache
  `Content/Python/OperationSunscar/AutomationV1/__pycache__/sunscar_automation_common.cpython-311.pyc`
  was restored to its exact `HEAD` content after validation. The final Git
  classifier again reports 912 modified, 80 untracked, zero staged and zero
  unexpected paths; branch/local/remote hashes remain the required commit.



## Appendix B — exact live Git and local evidence inventories

The complete path-by-path Git/LFS snapshot is stored locally at:

`Documentation/Maps/OperationSunscar/Planning/ABIVERD_OLD_TOWN_LIVE_GIT_MANIFEST_2026-08-18.txt`

That manifest includes the worktree registry, branch, local and remote hashes,
every modified/untracked path, the full diff stat and the complete `git lfs
status` output. It is a snapshot, not a substitute for live verification.

### Planning/documentation inventory

- `Documentation/Maps/OperationSunscar/Planning/ABIVERD_HERITAGE_ASSET_AND_PLACEMENT_MANIFEST_V1.csv` | 6373 bytes | mtime 2026-08-12T13:06:15 | sha256 `8d7f95d7e73a8eb727f38c9d52d683b1a17af9f1b02576cf1e76930ee4aa9090`
- `Documentation/Maps/OperationSunscar/Planning/ABIVERD_HERITAGE_EXPANSION_PLAN_V1.md` | 13217 bytes | mtime 2026-08-12T13:06:15 | sha256 `e27e7f9e54446f2567832c5bffbb4c32286fa03b563f1b89382d742964798354`
- `Documentation/Maps/OperationSunscar/Planning/ABIVERD_HERITAGE_UE_IMPORT_MANIFEST_V1.csv` | 5508 bytes | mtime 2026-08-12T13:06:15 | sha256 `ece3f049fc4d99aaaea324cbee1b9675246b5b37821f7561992c1892f4ee3feb`
- `Documentation/Maps/OperationSunscar/Planning/ABIVERD_OLD_TOWN_CLAUDE_CODE_HANDOFF_2026-08-18.md` | 216439 bytes | mtime 2026-08-18T19:00:53 | sha256 `8531725bf9682c21d3b1d500fe8ae0ab5fe23c5cdd02afd9f2eaa151294bef20`
- `Documentation/Maps/OperationSunscar/Planning/ABIVERD_OLD_TOWN_LIVE_GIT_MANIFEST_2026-08-18.txt` | 278577 bytes | mtime 2026-08-18T19:02:37 | sha256 `6753bf57cc18470c16d27f3502aacce271c913af1b8032f9d79b5c1f133c72de`
- `Documentation/Maps/OperationSunscar/Planning/ABIVERD_OLD_TOWN_PAUSE_HANDOFF_2026-08-05.md` | 185828 bytes | mtime 2026-08-17T02:54:56 | sha256 `67b4b18f8e2661dbd6252d2cea320d2f5049ac0170a65ccf34fe78b594ae4e30`
- `Documentation/Maps/OperationSunscar/Planning/ABIVERD_PHASE_ONE_DEFECT_REGISTER_2026-08-18.md` | 16878 bytes | mtime 2026-08-18T18:55:45 | sha256 `8f6d8b77413abfb1f47bdf7997656c2c0258aef4d583df4cefd6d3f034b95341`
- `Documentation/Maps/OperationSunscar/Planning/ABIVERD_VISUAL_CONVERSION_PROGRESS_2026-08-04.md` | 32190 bytes | mtime 2026-08-12T13:06:15 | sha256 `a9ecf49810952806d69c5b13160873680aa16ee3708dc3f7d3149408d4422013`
- `Documentation/Maps/OperationSunscar/Planning/OLD_TOWN_ART_PRODUCTION_PLAN.md` | 23893 bytes | mtime 2026-08-12T13:06:15 | sha256 `471d93a3c92e90dc2c6c86af65fb3e54a7d7f0459f5a29ff1d94f897ddd2d505`
- `Documentation/Maps/OperationSunscar/Planning/OLD_TOWN_ASSET_AUDIT_AND_PLACEMENT_RESOLUTION_2026-08-01.md` | 9949 bytes | mtime 2026-08-12T13:06:15 | sha256 `ddcc8cf2a9fbecb51d1e4f00831c829859cebda33b0d5ed0f4909818860ea0fb`
- `Documentation/Maps/OperationSunscar/Planning/OLD_TOWN_ASSET_CATALOG.csv` | 10590 bytes | mtime 2026-08-12T13:06:15 | sha256 `f102b7381477a3ad7d36260d312a08c595da92bf94615355cfcf829e64fbad3f`
- `Documentation/Maps/OperationSunscar/Planning/OLD_TOWN_ASSET_SELECTION_MATRIX_V1.csv` | 101555 bytes | mtime 2026-08-12T13:06:15 | sha256 `c8139b05c3c10d478e36b5cc3128b05381a72d7939e80041fb88b19d2358e70b`
- `Documentation/Maps/OperationSunscar/Planning/OLD_TOWN_BUILD_CHECKPOINTS.csv` | 2939 bytes | mtime 2026-08-12T13:06:15 | sha256 `6ff86b24b392922496aae7ee0f06385f0f58fb25e77a6abd30dc15c9c51abf37`
- `Documentation/Maps/OperationSunscar/Planning/OLD_TOWN_DOWNLOADED_ASSET_INVENTORY_V1.csv` | 13188 bytes | mtime 2026-08-12T13:06:15 | sha256 `f97b22bf56b81b5835d8c54497d7b2c61db0cdda3f694c242a76ff58429e93fe`
- `Documentation/Maps/OperationSunscar/Planning/OLD_TOWN_EXACT_FAB_SHORTLIST_P0.csv` | 12294 bytes | mtime 2026-08-12T13:06:15 | sha256 `3c917174ae1eaf60fe5d2e419e571a787bfaa269510c0aeabb3299d4686b86e0`
- `Documentation/Maps/OperationSunscar/Planning/OLD_TOWN_EXACT_FAB_SHORTLIST_P0.md` | 6003 bytes | mtime 2026-08-12T13:06:15 | sha256 `f6e273c5774edfc7c7fe22e13418a294bf9e0c133e043602026c9daa5dae7aeb`
- `Documentation/Maps/OperationSunscar/Planning/OLD_TOWN_EXACT_FAB_SHORTLIST_P1A.csv` | 11583 bytes | mtime 2026-08-12T13:06:15 | sha256 `aba9898813aaf30a0a2a245e5704f57b7ece7b57acf041682f2b3699b63b5107`
- `Documentation/Maps/OperationSunscar/Planning/OLD_TOWN_EXACT_FAB_SHORTLIST_P1A.md` | 6386 bytes | mtime 2026-08-12T13:06:15 | sha256 `dad6f5721d0e0438bba7848172c1da897a9ba3998be091e7606fa99f96530dc2`
- `Documentation/Maps/OperationSunscar/Planning/OLD_TOWN_EXACT_FAB_SHORTLIST_P1B.csv` | 10120 bytes | mtime 2026-08-12T13:06:15 | sha256 `b61a24bd202d1551a518943b1b9be96beea73535735c36874a8dca51fe2f789f`
- `Documentation/Maps/OperationSunscar/Planning/OLD_TOWN_EXACT_FAB_SHORTLIST_P1B.md` | 3722 bytes | mtime 2026-08-12T13:06:15 | sha256 `467efc99bea89fff1ce6e6e69f6b04b367eb040ec0f0885be5bfcf97ae9b55e6`
- `Documentation/Maps/OperationSunscar/Planning/OLD_TOWN_EXACT_SITE_ASSIGNMENTS.csv` | 4531 bytes | mtime 2026-08-12T13:06:15 | sha256 `d66c2e4ea5d4751c37731ce77d28603f1fc8a63b55c28599a3df86cddc518a21`
- `Documentation/Maps/OperationSunscar/Planning/OLD_TOWN_FAB_ACQUISITION_REPORT_2026-08-01.md` | 2198 bytes | mtime 2026-08-12T13:06:15 | sha256 `65cb1038685ed8e64c01225088288338984164239ad4592070963ff334cf974d`
- `Documentation/Maps/OperationSunscar/Planning/OLD_TOWN_FAB_LIBRARY_STATUS_2026-08-01.csv` | 4607 bytes | mtime 2026-08-12T13:06:15 | sha256 `07666b12925c6e860711c8c01c9477b5037a7fe7b225840a97d807aa6bb4d68d`
- `Documentation/Maps/OperationSunscar/Planning/OLD_TOWN_LEVEL_DEPENDENCY_CLOSURE_V1.json` | 166440 bytes | mtime 2026-08-12T13:06:15 | sha256 `0ac1109541b4e75fedb4b4fa6eff09c29631b263492d16d4310cfe56c787836d`
- `Documentation/Maps/OperationSunscar/Planning/OLD_TOWN_MAP_OWNED_MODULAR_KIT.csv` | 5395 bytes | mtime 2026-08-12T13:06:15 | sha256 `bd5b7f5745407b6058a2d09fcdcffecd2ac7b27eb2b24bb015dfa88041e68922`
- `Documentation/Maps/OperationSunscar/Planning/OLD_TOWN_MASTER_ACQUISITION_PLAN.csv` | 7610 bytes | mtime 2026-08-12T13:06:15 | sha256 `1354646a7b272aec550c8c7754bdc33bd7a9b8861cdf1566fd3dbbff09f1a1aa`
- `Documentation/Maps/OperationSunscar/Planning/OLD_TOWN_MASTER_ACQUISITION_PLAN.md` | 5183 bytes | mtime 2026-08-12T13:06:15 | sha256 `432b12416fdfb19748e96328a837b9d0cb93bb9a47f29964b5d89c6da53831dd`
- `Documentation/Maps/OperationSunscar/Planning/OLD_TOWN_MATERIAL_INSTANCE_PLAN.csv` | 2836 bytes | mtime 2026-08-12T13:06:15 | sha256 `8d9d21db1d24728b22243d9643a58e9f60f5e14dce778d41e75f190d13f784c9`
- `Documentation/Maps/OperationSunscar/Planning/OLD_TOWN_OUTSIDE_UE_PREPARATION_STATUS_2026-08-01.md` | 5349 bytes | mtime 2026-08-12T13:06:15 | sha256 `c85c682d5134967ca90641c14ad5f2d4824da97e60b45c2e0fe792949006723f`
- `Documentation/Maps/OperationSunscar/Planning/OLD_TOWN_PROP_ACQUISITION_AND_PLACEMENT_PLAN.md` | 8454 bytes | mtime 2026-08-12T13:06:15 | sha256 `0e4ffccf7235c138be4ff01bccca85e15a67248623448b4f32e125053676e84d`
- `Documentation/Maps/OperationSunscar/Planning/OLD_TOWN_PROP_CANDIDATE_PLACEMENTS_V1.csv` | 690551 bytes | mtime 2026-08-12T13:06:15 | sha256 `aeb3391961775fe8084bf90362eabc4530e783788387039dd0f683536dc79d94`
- `Documentation/Maps/OperationSunscar/Planning/OLD_TOWN_PROP_CANDIDATE_VALIDATION_V1.json` | 711 bytes | mtime 2026-08-12T13:06:15 | sha256 `fefd403b2bc56aa7a536bbd14b73a8ddf48a7408eb7d91f656e52b83a3be0ad8`
- `Documentation/Maps/OperationSunscar/Planning/OLD_TOWN_PROP_IMPORT_BATCHES.csv` | 2744 bytes | mtime 2026-08-12T13:06:15 | sha256 `b6238cbc623efb917a2cb6d147cbdad982bd1ba5b8623d3681a6ba3e885e2695`
- `Documentation/Maps/OperationSunscar/Planning/OLD_TOWN_PROP_MASTER_BOM.csv` | 9284 bytes | mtime 2026-08-12T13:06:15 | sha256 `86bbfb711f9b8c01d12381fe44f308bbc6b36948ef73bd412ea28424e35809cb`
- `Documentation/Maps/OperationSunscar/Planning/OLD_TOWN_PROP_SITE_BUDGETS.csv` | 2328 bytes | mtime 2026-08-12T13:06:15 | sha256 `48dcce20a169ca949799dcb22f9401535093568011e531307cea4b5ff1dff1ca`
- `Documentation/Maps/OperationSunscar/Planning/OLD_TOWN_PROP_SUPPLEMENTAL_EXACT_LISTINGS.csv` | 899 bytes | mtime 2026-08-12T13:06:15 | sha256 `b660fb8a8f33efcf822b14d6efe303dd131e1d72831f259d199eb83833a91a25`
- `Documentation/Maps/OperationSunscar/Planning/OLD_TOWN_RESOLVED_PLACEMENT_PLAN_V1.csv` | 1142593 bytes | mtime 2026-08-12T13:06:15 | sha256 `b4b0e039f24f8f448ebdcda07c0ce79bccb5ed908c967a34082887e45707fb2c`
- `Documentation/Maps/OperationSunscar/Planning/OLD_TOWN_SITE_RECIPES.csv` | 8424 bytes | mtime 2026-08-12T13:06:15 | sha256 `1c79b16ace0637e1bdb8ea03f7ecd1237f67c8655d151ada080743a3034606e9`
- `Documentation/Maps/OperationSunscar/Planning/OLD_TOWN_SPATIAL_ASSET_METHOD.md` | 9206 bytes | mtime 2026-08-12T13:06:15 | sha256 `a4a4c7c0224f43d4c71e269d0e9b3685edf02c097f4aaca3fddf6f5523fc4218`
- `Documentation/Maps/OperationSunscar/Planning/OLD_TOWN_UE58_LANDSCAPE_AND_BUILDING_ARCHITECTURE_2026-08-02.md` | 8286 bytes | mtime 2026-08-12T13:06:15 | sha256 `79c7a5dbdb6d3fb8d4412e261ef3e27ff616e73c4c2a7da612624160406a12bf`
- `Documentation/Maps/OperationSunscar/Planning/OLD_TOWN_UE_AUTOMATION_HANDOFF_2026-08-01.md` | 5549 bytes | mtime 2026-08-12T13:06:15 | sha256 `abfc2dd08e03dbcaa2dee75ac94db90fc01dc81d73af8b6a9eddfad24b0d7e6b`
- `Documentation/Maps/OperationSunscar/Planning/OLD_TOWN_UE_EXECUTION_PACKET.md` | 10179 bytes | mtime 2026-08-12T13:06:15 | sha256 `cc19f3d624780e33691c9ef16402ce86b5c335f58955a6da65cd739045a2523e`
- `Documentation/Maps/OperationSunscar/Planning/OLD_TOWN_UE_IMPORT_QUEUE_V1.csv` | 39236 bytes | mtime 2026-08-12T13:06:15 | sha256 `2a68aba27ac3ba52de685c06e426b666dc50bd41cf8dd3ed4d2b4ffcfd726113`
- `Documentation/Maps/OperationSunscar/Planning/OLD_TOWN_UE_STAGING_MANIFEST.csv` | 9008 bytes | mtime 2026-08-12T13:06:15 | sha256 `4c844f209e815514b9a88a8e9c1a3b4b50705023a4bf1c2a87aa42110934220b`
- `Documentation/Maps/OperationSunscar/Planning/OLD_TOWN_UE_WORK_SESSION_2026-08-02.md` | 49197 bytes | mtime 2026-08-12T13:06:15 | sha256 `50b0efa2e8b5cb6ff454098b5865466afb34a7f0633d7d9b7d47f0b9e8058639`
- `Documentation/Maps/OperationSunscar/Planning/OldTown_ArtPlacementManifest_v1.json` | 10398 bytes | mtime 2026-08-12T13:06:15 | sha256 `866775dba5163c3bab44b6bf344a675d02be09d596ceb4ec4195824f7fa39d72`
- `Documentation/Maps/OperationSunscar/Planning/OldTown_AssetPathRegistry_v1.json` | 15503 bytes | mtime 2026-08-12T13:06:15 | sha256 `f90c4cccada0d938da8b1d01e81f8f3e56841901cb11ff7aaf47ab0f4fb6a4b9`
- `Documentation/Maps/OperationSunscar/Planning/OldTown_DownloadedAssetInventory_v1.json` | 43090 bytes | mtime 2026-08-12T13:06:15 | sha256 `5c641405c786117e9aa6b9ee8d8c0ea4f6bda912822eb261ff9d5dfb1a41ccdf`
- `Documentation/Maps/OperationSunscar/Planning/OldTown_FinalAssetRegistry_v1.json` | 3725 bytes | mtime 2026-08-12T13:06:15 | sha256 `8dd76a19bdf571669ddaebe78bf65ad52a649df1dad913af118243c64c8cac9f`
- `Documentation/Maps/OperationSunscar/Planning/OldTown_PropCandidatePlacements_v1.json` | 1644815 bytes | mtime 2026-08-12T13:06:15 | sha256 `6180660a7b5f30c182d1f9da9b40357b46485ae2547fe15a9b1b7f9ef2076253`
- `Documentation/Maps/OperationSunscar/Planning/OldTown_PropPlacementManifest_v1.json` | 8055 bytes | mtime 2026-08-12T13:06:15 | sha256 `cb337feb3fcf08927fb7d238051544420ec3089f833ecd8d63eaa6057062b392`
- `Documentation/Maps/OperationSunscar/Planning/OldTown_ResolvedPlacementPlan_v1.json` | 2533655 bytes | mtime 2026-08-12T13:06:15 | sha256 `dcfbaae2ea77a341012128f51fcc510330e88fdd4bff19d31569e0e6a8b95587`

### OperationSunscar Python source inventory

- `Content/Python/OperationSunscar/AutomationV1/abiverd_bazaar_tarp_canopy_post_audit_v1.py` | 5534 bytes | mtime 2026-08-12T13:06:13 | sha256 `6f6ff4ccef1400f99879925b1dd455ea6d166366cb306b3c803ef6c6d8d4cc7f`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_bazaar_tarp_canopy_v1.py` | 10109 bytes | mtime 2026-08-12T13:06:13 | sha256 `31ed92978eeb435775531cf0073593a8544e0a0e500c7c36a981db1ba0c9a27a`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_cleanup_unsaved_architecture_partial_v1.py` | 2705 bytes | mtime 2026-08-12T13:06:13 | sha256 `60614c095c8dcb9ac20471c3af6dbbbe7b09b8249e565bce87fdd5b22b59ccf1`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_cleanup_unsaved_meadow_material_v1.py` | 1132 bytes | mtime 2026-08-12T13:06:13 | sha256 `478f91f7124fb1c0af0e1185c4324df98aa6b127c3f1b66bb715f440c8bdfaf9`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_cleanup_unsaved_vegetation_hism_v1.py` | 725 bytes | mtime 2026-08-12T13:06:13 | sha256 `3bd768d29757e7a9bbb73dddb5f86f384033d4082fe531ac4e4bf76a08f5ea5d`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_consulate_warm_plaster_post_audit_v1.py` | 6382 bytes | mtime 2026-08-12T13:06:13 | sha256 `021f5b68771ebb990941d11e71db9fd7b8be27f482191159298c6e8e7b2ddd36`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_consulate_warm_plaster_v1.py` | 7647 bytes | mtime 2026-08-12T13:06:13 | sha256 `8e25d217565a570417a9baabbc7ae50c2c82b466bd092e83962e9e7a69cea0b0`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_current_facade_view_audit_v1.py` | 4922 bytes | mtime 2026-08-12T13:06:13 | sha256 `f7192f74c16fb065c11bbe9170212f07fd25048453cf058b2c117d4b910fb1d1`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_door_surrounds_post_apply_audit_v1.py` | 5432 bytes | mtime 2026-08-12T13:06:13 | sha256 `737efd4bacd8e1dc59383549ee82c30ec20ef66bdd3f03b91069096425e14b5f`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_door_surrounds_v1.py` | 15629 bytes | mtime 2026-08-12T13:06:13 | sha256 `a3a2532e5c1389f9ca8ee39ac1deb8f625ad7a892bdb4d7f69ae823f1b719ddb`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_export_facade_reference_textures_v1.py` | 2517 bytes | mtime 2026-08-12T13:06:13 | sha256 `462774eb4d2ccc7f371cd8cca24f2bd69c372128ec2f6c23c36848b35280c115`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_facade_scan_instancing_v4.py` | 11343 bytes | mtime 2026-08-12T13:06:13 | sha256 `4c4640af960bada53019a43fd3a6fad030a65269f23e641da538de99d186394c`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_floor_sand_import_audit_v1.py` | 4418 bytes | mtime 2026-08-12T13:06:13 | sha256 `f689dc0d7de1d7bec4785f57f318591bc615d80a1345533003c456e5654a42b5`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_floor_sand_landscape_post_audit_v1.py` | 4703 bytes | mtime 2026-08-12T13:06:13 | sha256 `5acfd4386f295bd80d5b9937352bae345effb4605292be3971c366697eba44de`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_floor_sand_landscape_v1.py` | 8175 bytes | mtime 2026-08-12T13:06:13 | sha256 `39e911db014b3c206afeaba475e0f88ff440974b00a9171e07f918c78c7a9738`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_floor_sand_map_owned_v1.py` | 6826 bytes | mtime 2026-08-12T13:06:13 | sha256 `bb896905b3f735c05429c82f73a0e9cf6659b92c8701ac0c9342bffd5155407d`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_focus_aerial_review_v1.py` | 316 bytes | mtime 2026-08-12T13:06:13 | sha256 `9f831cee94dd531f702811c3a8c705d71e934eff0a9a15a9e2254c555729d412`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_focus_bazaar_tarp_review_v1.py` | 2070 bytes | mtime 2026-08-12T13:06:13 | sha256 `86ca3ebae99c4709044668aa44e458da9c8a25f7bc923c5d42a17c90bd66945b`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_focus_mosque_review_v1.py` | 321 bytes | mtime 2026-08-12T13:06:13 | sha256 `eba66dde9c9f1d0f397540d66e26ba5db7fc72caf8b68a83b68e4af41e47b990`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_focus_temporary_terrain_forms_v1.py` | 324 bytes | mtime 2026-08-12T13:06:13 | sha256 `2d65bb4c56b81ca4163dd115020779f35d3c7faceb38757dbc739904f2db4fb2`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_foliage_master_graph_probe_v1.py` | 5389 bytes | mtime 2026-08-12T13:06:13 | sha256 `cb54b410862126f7daa5d1b72a1c40ce9c4b4dc9e94df6a1d30b357e12513f01`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_foliage_master_probe_v1.py` | 4976 bytes | mtime 2026-08-12T13:06:13 | sha256 `b6613c892a933e8176b6f16e6076ea3affeb8bda239018015978c6bfd9e6748c`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_generate_landscape_masks_v2.py` | 7653 bytes | mtime 2026-08-12T13:06:13 | sha256 `f5a7069468a64b7072a9fc60b7cbe5baa0edbc3815534e9d6f19bed90acf29e0`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_heritage_architecture_acceptance_v1.py` | 4814 bytes | mtime 2026-08-12T13:06:13 | sha256 `4187fd75c9367ca8e77771e010f738e44a9ba3ec0b0ca3cec4ad30a29790e82c`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_heritage_architecture_composition_v1.py` | 18189 bytes | mtime 2026-08-12T13:06:13 | sha256 `d50752118bdf16f4755017b55848656cb4114b12364963da450e0f05c821a70d`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_heritage_architecture_configure_v1.py` | 8087 bytes | mtime 2026-08-12T13:06:13 | sha256 `b9c7eb5279ba18f649a937fc4dc932740c63fc554caec89c384b600069612206`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_heritage_architecture_save_v1.py` | 3214 bytes | mtime 2026-08-12T13:06:13 | sha256 `72f9bf4cad574a428d45d97c460fdb85d4bf4f070a1eb13301f30145086e2f2e`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_heritage_architecture_stage_audit_v1.py` | 6250 bytes | mtime 2026-08-12T13:06:13 | sha256 `d04a011f05a767cbb5f20b7545c99500802d1db024eb51422e3c9b374be127b8`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_heritage_architecture_stage_import_v1.py` | 7520 bytes | mtime 2026-08-12T13:06:13 | sha256 `190f27410bcd5cc0937626f95753dbc07e66dcb0732f717873ef2654af5f7874`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_heritage_architecture_state_probe_v1.py` | 1723 bytes | mtime 2026-08-12T13:06:13 | sha256 `b54542d202a29a21859b3f985089ff3de494432ccc1fad1ae2bb77d208cb9986`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_heritage_foliage_stage_import_v1.py` | 16200 bytes | mtime 2026-08-12T13:06:13 | sha256 `3b9cbc1d326b7c061a7d97c0512225b44d2cf4dcecefe299670a5ae18fef5210`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_heritage_foliage_state_probe_v1.py` | 2570 bytes | mtime 2026-08-12T13:06:13 | sha256 `7b72a06d4efefe65c54d9ff2ea0b123479be1ed9bdbb542e08783497c612b0f7`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_heritage_foliage_validate_save_v1.py` | 11246 bytes | mtime 2026-08-12T13:06:13 | sha256 `1ab45561234b0ce60c4148a6370004c23d931c55890edfb0366e145fbed7eeaf`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_heritage_material_repair_v2.py` | 16120 bytes | mtime 2026-08-12T13:06:13 | sha256 `91e82d65c6ab4d1fc37445cae71e419153ff0ff024cee6533113142321a41c04`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_heritage_site_preflight_v1.py` | 7534 bytes | mtime 2026-08-12T13:06:13 | sha256 `6ffa3695bab65a62f18c6314f40355338926a39c1f4e29e237bedf677f5a9cdd`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_heritage_surfaces_stage_import_v1.py` | 7629 bytes | mtime 2026-08-12T13:06:13 | sha256 `176b9c4f9597547f162a0366da4d0fb8643d17890e16a13f4b3ac90b6e1569a3`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_heritage_surfaces_state_probe_v1.py` | 2187 bytes | mtime 2026-08-12T13:06:13 | sha256 `8c7372d05ac5982b4ec31acdaa863939268bfa64628915940be5794eaeab4e8f`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_heritage_surfaces_validate_save_v1.py` | 5638 bytes | mtime 2026-08-12T13:06:13 | sha256 `3456e2e74941161c37d178362a2923abfef7720e1ec62d7b9ae8b5b01efd8c22`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_heritage_vegetation_acceptance_v1.py` | 5689 bytes | mtime 2026-08-12T13:06:13 | sha256 `e2864d3f5865910dbd0b34491e355d8378c9b2ef71331aa26d8b434dc08085d8`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_heritage_vegetation_hism_v1.py` | 13474 bytes | mtime 2026-08-12T13:06:13 | sha256 `9d74a0a863c92e31108e393f98c7997e3ee9160a49d42900cc57e30fc3ce93df`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_hism_api_probe_v1.py` | 1229 bytes | mtime 2026-08-12T13:06:13 | sha256 `ea2e9a5fc4b6f38b2837bacfd987761eb044fedddb8b947e5d1e1bc22e3122dc`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_hotel_bazaar_opening_audit_v1.py` | 6775 bytes | mtime 2026-08-12T13:06:13 | sha256 `ff51dceb44b220899d1c2f624099db3dd13993dc78060d98fa2b41d9d1038cac`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_landmark_completion_v2.py` | 10530 bytes | mtime 2026-08-12T13:06:13 | sha256 `1fc78e991288687d8114e60239ef57e0f6ae284ae5f2b4ef2503530e94f07413`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_landscape_cell_bombing_preflight_v1.py` | 11163 bytes | mtime 2026-08-12T13:06:13 | sha256 `a575f539b5fd91b3e21590b6a166cc98623a256c0484d34fe14bae844a95784e`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_landscape_component_weight_probe_v1.py` | 2738 bytes | mtime 2026-08-12T13:06:13 | sha256 `629af82500776c184ac4dd81ddf3950aff8bc3550cdf46c801fca1e60b325b10`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_landscape_edit_layer_probe_v1.py` | 3016 bytes | mtime 2026-08-12T13:06:13 | sha256 `e009d291341827d9edb1ec72940ae3b97a00395dcd54bcea95e9767cb59f67e2`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_landscape_grass_sample_probe_v1.py` | 1761 bytes | mtime 2026-08-12T13:06:13 | sha256 `2c5420beb6f7f9bd792c06c4e812f3d4bfd6d7cd09e6951b2f6faf71cd3de0dd`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_landscape_layer_setup_probe_v1.py` | 4587 bytes | mtime 2026-08-12T13:06:13 | sha256 `3434537b8c2d7e7bbba49d8c7af4490b330b9d64e93caec5a58c94029b5f603e`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_landscape_layerinfo_property_probe_v1.py` | 2090 bytes | mtime 2026-08-12T13:06:13 | sha256 `759493d34f9640bc59ab40b19f354d2058524dc4da7708060079d8b6d7741795`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_landscape_meadow_layerinfo_v1.py` | 6833 bytes | mtime 2026-08-12T13:06:13 | sha256 `ab8bcaa2086f9ab088601a6f15b660ee937b8931cda85d71e83bf77063a54cb8`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_landscape_meadow_material_acceptance_v1.py` | 3191 bytes | mtime 2026-08-12T13:06:13 | sha256 `0530624d47e397b6229d5dd1e3ddd35dec2513aeddd186db1c6c453bfe666117`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_landscape_meadow_material_v1.py` | 13323 bytes | mtime 2026-08-12T13:06:13 | sha256 `01887af24c31e6d0e04ec6d58d2eed7c1847245103093180933fd1264a033739`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_landscape_meadow_preflight_v1.py` | 4903 bytes | mtime 2026-08-12T13:06:13 | sha256 `dea7961b22fa1fedd6f20a6174be176fc1dc9b0739d398c78e87604685ad4a6d`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_landscape_meadow_weightmap_acceptance_v1.py` | 4531 bytes | mtime 2026-08-12T13:06:13 | sha256 `dd980601958d61dab42d0a498a103da299a8bd4556967caa630953d35a890c78`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_landscape_meadow_weightmap_v1.py` | 7717 bytes | mtime 2026-08-12T13:06:13 | sha256 `4ac04348ef1db6b7743fdd87f8668a3a4c17bf4f0f15e46cce9c0064f7b969b4`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_landscape_texture_bombing_preview_v1.py` | 13331 bytes | mtime 2026-08-12T13:06:13 | sha256 `3102bd8239e7f7835693b314018196e698ccaaf0ef39ac07623e05038c61e331`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_landscape_visual_conversion_v2.py` | 23660 bytes | mtime 2026-08-12T13:06:13 | sha256 `c87905f16434c9996a4955672657157a01195b84d2da935b2a89bfde9e9d9c9b`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_landscape_weightmap_api_probe_v1.py` | 4866 bytes | mtime 2026-08-12T13:06:13 | sha256 `397009945018603dd4899e786d64edbf5e410bb0856da78d0269c0cfa8d5f8d7`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_meadow_mask_rt_probe_v1.py` | 3481 bytes | mtime 2026-08-12T13:06:13 | sha256 `d6b87343541a10fb58d6dd47af19aea80a7b2da0a69a4437b4e379b608f56a38`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_open_street_review_v3.py` | 1128 bytes | mtime 2026-08-12T13:06:13 | sha256 `5e5df3d719632a933450334f1a600f4fd240375800040c9393943e367aad9936`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_open_visual_review_angle_v3.py` | 1336 bytes | mtime 2026-08-12T13:06:13 | sha256 `8e7e0fd49ee6c2bb157d0fd2fc5beb15f2dcd864a2adec1d71a2c75b5b86b4db`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_open_visual_review_v2.py` | 1121 bytes | mtime 2026-08-12T13:06:13 | sha256 `b490507be3c14122ab9ddaf5eb3a9e2821780b621c48d4b1b2ecc49a2aa8229f`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_opening_surrounds_post_audit_v2.py` | 8600 bytes | mtime 2026-08-12T13:06:13 | sha256 `4ce7cf70cda20af8493305cd4521556bd8b69f81889c44bbe13fe09ba93a00d3`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_opening_surrounds_v2.py` | 14607 bytes | mtime 2026-08-12T13:06:13 | sha256 `061a94b89e2348402fb677dac736647b3387a377ede3bb8ccc5ef8bcf79f79c4`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_pakistan_wall_facade_v1.py` | 13221 bytes | mtime 2026-08-12T13:06:13 | sha256 `15a91144ed3f9f9678aba831a350d5e7252a061686d013faa1f8be899fa64ce1`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_pakistan_wall_import_v1.py` | 10461 bytes | mtime 2026-08-12T13:06:13 | sha256 `0a640fd522b9a9f49b08b64c9a942decdcbf8d2ddef4dd376ffa0ca3ebf5ec6b`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_pakistan_window_facade_v1.py` | 14976 bytes | mtime 2026-08-12T13:06:13 | sha256 `f068aad2aba073884d9f81f7ea7def4f3d0c3e4b0523b93dae1819599f04bbad`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_pakistan_window_hotel_v2.py` | 12072 bytes | mtime 2026-08-12T13:06:13 | sha256 `1492eba80330356792b7473ca18b122145e8d10f9380ad771e3e932f838e449c`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_pakistan_window_import_v1.py` | 7849 bytes | mtime 2026-08-12T13:06:13 | sha256 `6e93ebeeb6e41f7be820e16b85bc8d917df43009242547ddf8b49e9cbaedcec6`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_pakistan_window_post_apply_audit_v1.py` | 5375 bytes | mtime 2026-08-12T13:06:13 | sha256 `9a82e9a100d579f097ccc4be0cd343bec17ea9266222607be0b8341304ca0fd3`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_partial_scope_probe_v1.py` | 1187 bytes | mtime 2026-08-12T13:06:13 | sha256 `3940a7db22e349ad285cd377628a4c6fe16f8886708f211da8d59327c2ec9a75`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_reload_level_after_partial_preview_v1.py` | 1010 bytes | mtime 2026-08-12T13:06:13 | sha256 `6ddda1207db0fe9b34d207a806133e0946047cae6d8157c63d55519f9f140a02`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_reload_partial_external_objects_v1.py` | 1581 bytes | mtime 2026-08-12T13:06:13 | sha256 `2d979bc72af603c55e61d0a7ab631cd5e2f8e0935f9f27c8c5f996721112578e`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_remove_duplicate_parapets_post_audit_v1.py` | 5075 bytes | mtime 2026-08-12T13:06:13 | sha256 `cf41b5060f887da1a20bca35b8966e9e4f3eb35cd918a9bb5ff44965747e0fa1`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_remove_duplicate_parapets_v1.py` | 7798 bytes | mtime 2026-08-12T13:06:13 | sha256 `101e5ac1c55bd870645cd1d7f0d5e0a6b0fcd7e5d904ac2d290df7e9a949f7ae`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_remove_unsuitable_window_slabs_post_audit_v1.py` | 4722 bytes | mtime 2026-08-12T13:06:13 | sha256 `9404fb5f56b15df5d65b1a79a37dab7835117933d0c02a6625cd0d96d80df703`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_remove_unsuitable_window_slabs_v1.py` | 8209 bytes | mtime 2026-08-12T13:06:13 | sha256 `99a4cbde4ba93316b8537e1cc13bfc7e59036fe64e2aaf3c94ee65d37f22c851`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_run_architecture_composition_with_diagnostics_v1.py` | 1208 bytes | mtime 2026-08-12T13:06:13 | sha256 `8a2d22556b67640ed3cfbabeee2e2678dd2468899d7812afd0e468d6cedeefde`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_run_foliage_import_with_diagnostics_v1.py` | 1198 bytes | mtime 2026-08-12T13:06:13 | sha256 `3514858e5c4213943d9482b7e75deaee6e84cd9d29f191a7d51e66b347cf4010`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_run_foliage_save_with_diagnostics_v1.py` | 1209 bytes | mtime 2026-08-12T13:06:13 | sha256 `af81d0936c365455387ef41910659f2a14d58675729bf10603bb128770e6f617`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_run_site_preflight_with_diagnostics_v1.py` | 1182 bytes | mtime 2026-08-12T13:06:13 | sha256 `82e4854c448f912e9508571789ae1bddda024d3780818cedbae0c7a545d05add`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_run_surface_save_with_diagnostics_v1.py` | 1211 bytes | mtime 2026-08-12T13:06:13 | sha256 `b4140c3224aaae3afcc58bb85368b9ccf834f48c38fd5d47c83998e6e0e09a23`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_run_vegetation_hism_with_diagnostics_v1.py` | 1190 bytes | mtime 2026-08-12T13:06:13 | sha256 `30c501835a6586cdb52202174669142b9a97d7aaf5e8e03283d37d1ac5250d2d`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_run_world_partition_load_with_diagnostics_v1.py` | 1187 bytes | mtime 2026-08-12T13:06:13 | sha256 `049a836ae6cce0f279f7f7e964f78d1b2e709937eb405a03ce28a77a12d4df10`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_save_architecture_composition_v1.py` | 2792 bytes | mtime 2026-08-12T13:06:13 | sha256 `98ef831bc3976fa1d85221f7fc0e109e79d7c1f3ca35a58041a473d78fe8ee37`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_save_door_surround_materials_v1.py` | 2589 bytes | mtime 2026-08-12T13:06:13 | sha256 `5c8e3f1098bcec89a82cff9995e32cca2ebfccd0d26d68758254323fd28314a0`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_save_heritage_vegetation_v1.py` | 3083 bytes | mtime 2026-08-12T13:06:13 | sha256 `2efc898d070f33577e0bf7e1d75618dc015304a0222d31d7930d9a8433928f4e`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_save_landscape_material_v3.py` | 2994 bytes | mtime 2026-08-12T13:06:13 | sha256 `2a1e7b9300b0f7f5f885e2c393c6a171b73569dad45344c62f67b97f6fc8bcec`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_save_landscape_meadow_v1.py` | 4067 bytes | mtime 2026-08-12T13:06:13 | sha256 `5faa99994cc0788167438f0cc4102ba21bc959650d87f02ed40d838ed642ced4`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_save_pakistan_window_material_v1.py` | 2418 bytes | mtime 2026-08-12T13:06:13 | sha256 `4c3f5856016b8d8a0c74928b6a9850c2a09e8359ec2e9fc5ccc4aee5fbccd6a3`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_structural_skin_v3.py` | 15899 bytes | mtime 2026-08-12T13:06:13 | sha256 `f359523922a21c2745dc7a4fd7cec41b26f2cd836849dac3211e768ca3aa35b2`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_temporary_terrain_forms_blend_v1.py` | 3854 bytes | mtime 2026-08-12T13:06:13 | sha256 `4b7760103a3a472c7b5fe18dcee9a18db5d8c35b95b9edf1a015c2ac46d3f672`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_temporary_terrain_forms_cleanup_v1.py` | 2131 bytes | mtime 2026-08-12T13:06:13 | sha256 `d2257564e512e9edeb64ef34c2ef7b26d42721036d1c700569abf1aea9e29a27`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_temporary_terrain_forms_discard_v1.py` | 3145 bytes | mtime 2026-08-12T13:06:13 | sha256 `1f478dc159fd4f588a2d00afd3064f367e96a37f59ae7892c778c9c86551cf50`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_temporary_terrain_forms_v1.py` | 7325 bytes | mtime 2026-08-12T13:06:13 | sha256 `0574231ec03d36cdf0ff18c306db6c0d80b5e3b9d5a1afff4ced2957d40d16fa`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_terrain_relief_discard_preview_v1.py` | 2633 bytes | mtime 2026-08-12T13:06:13 | sha256 `8a9467ace01984a5016586fa1446501c8194d44f3f74491362221f2f2f4a0001`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_terrain_relief_import_v1.py` | 9608 bytes | mtime 2026-08-12T13:06:13 | sha256 `3fbaac00d177296f881dee31ce329c64af107616d06f6913af2a6c1bb2cd0af1`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_terrain_relief_post_preview_audit_v1.py` | 6735 bytes | mtime 2026-08-12T13:06:13 | sha256 `3d555efb3fd0e73a99a1c6c366354f53262f48a5928cc4923ba36d6887fa4b45`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_terrain_relief_preflight_v1.py` | 5316 bytes | mtime 2026-08-12T13:06:13 | sha256 `c127f96264f1dbd6bab897486f35325977b65205871aed956f3a37015ccfc227`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_terrain_relief_save_v1.py` | 2371 bytes | mtime 2026-08-12T13:06:13 | sha256 `5c0135fce62a386ea552852c6cd23d06e0fbf1f809abbbb4be51050ce0cec19d`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_vegetation_density_v2.py` | 12237 bytes | mtime 2026-08-12T13:06:13 | sha256 `7dd6b2f302a5220a2d01a8c60ca156a89f96cf9fe3e7c4870567be2fb75f856a`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_visual_conversion_preflight_v1.py` | 6029 bytes | mtime 2026-08-12T13:06:13 | sha256 `b1d50ba16775f8afafd42f734ede52109f7a01cc21eff92b04cce81e476b88b3`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_wall_foot_source_consolidation_v1.py` | 6293 bytes | mtime 2026-08-12T13:06:13 | sha256 `22febd64ea81e105bb170c07e733ddbf86073f52641161bbb805c4b81c2e6355`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_wall_foot_transition_hism_v1.py` | 17604 bytes | mtime 2026-08-12T13:06:13 | sha256 `e06a92fdec706b9a7f28c44d5fe5565385996bd0d7925c5651a4fc4ffd28504a`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_wall_foot_transition_post_audit_v1.py` | 7209 bytes | mtime 2026-08-12T13:06:13 | sha256 `c0067d10e97e5125ab4b4039dd11ec9c9317cba05a9f854744d164c079314855`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_wall_foot_transition_preflight_v1.py` | 8513 bytes | mtime 2026-08-12T13:06:13 | sha256 `f572572982085c1579765406df43ce6f0d97241da66bf1fc17ab0861dec7f780`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_window_material_state_audit_v1.py` | 5495 bytes | mtime 2026-08-12T13:06:13 | sha256 `480e0fb56d558160ece2eef9e71cdb2dbd780e03bc101fa9f277fabb84db72ac`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_window_recess_conversion_v1.py` | 8652 bytes | mtime 2026-08-12T13:06:13 | sha256 `5cb107f61e3fcc8bbdab59716ece8ac0dc70cdf4dd4c32cfeb0d0a7ab385ce85`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_window_recess_post_audit_v1.py` | 5616 bytes | mtime 2026-08-12T13:06:13 | sha256 `8b9628b0c298ddcb9e5971a47a0c00f1375c1c19af2d279db7cbb25be2abed1b`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_window_trim_instancing_v1.py` | 12627 bytes | mtime 2026-08-12T13:06:13 | sha256 `0eb44f36efcc4bf3ce52f555fb0c7443f690febbd0e23876d6b52fa259ad07cf`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_window_trim_post_audit_v1.py` | 4804 bytes | mtime 2026-08-12T13:06:13 | sha256 `1d6df3d4a76837bd2048d4459172831cdab6bcc6a533572c3a719a6c40f22351`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_world_partition_descriptor_probe_v1.py` | 2858 bytes | mtime 2026-08-12T13:06:13 | sha256 `20d98bdd5f319f35957d6a2c495af0a77c35752de591caff542ea4e0d9474f06`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_world_partition_load_full_landscape_v1.py` | 4245 bytes | mtime 2026-08-12T13:06:13 | sha256 `27fb2ccf2a2abfa0f4886259ae855ce5117cb0b2946468cc9dd70399dab6c433`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_world_partition_load_region_v1.py` | 4190 bytes | mtime 2026-08-12T13:06:13 | sha256 `82050f5f0d246017eedda8094b8db229700824210b3f07c2f028777253328b40`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_world_partition_restore_working_region_v1.py` | 3708 bytes | mtime 2026-08-12T13:06:13 | sha256 `a634c21697101e089b7266031fd2a5b07fcd2cebea28c13b820a53b4d8353e61`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_wrinkled_tarp_import_post_audit_v1.py` | 5745 bytes | mtime 2026-08-12T13:06:13 | sha256 `71b0ce34b2ec331696ee0174f77b25df97b28754ea9a5a606908b7f2b24d59cc`
- `Content/Python/OperationSunscar/AutomationV1/abiverd_wrinkled_tarp_import_v1.py` | 13448 bytes | mtime 2026-08-12T13:06:13 | sha256 `56b1653c6b389c941acf20d96efed62011826d67db9345bbe73f06bb9043d66c`
- `Content/Python/OperationSunscar/AutomationV1/citysample_awning_source_audit_v1.py` | 6253 bytes | mtime 2026-08-12T13:06:13 | sha256 `77b7be03b32184ed5ec7a2e9f01ced44277d622caf5ad9b17bf98957bdc06123`
- `Content/Python/OperationSunscar/AutomationV1/citysample_awning_visual_gallery_v1.py` | 3607 bytes | mtime 2026-08-12T13:06:13 | sha256 `14d8fd14b953edededdd9ddfd832ca39c59791cde5db6d19c9871a0063d6af50`
- `Content/Python/OperationSunscar/AutomationV1/generate_abiverd_terrain_relief_rg16_v1.py` | 1768 bytes | mtime 2026-08-12T13:06:13 | sha256 `302d7f497c41c9c52a09eaa7f5cd2cffe8d6870d4b2f0a0fae799f00bd35a293`
- `Content/Python/OperationSunscar/AutomationV1/generate_abiverd_terrain_relief_v1.py` | 8776 bytes | mtime 2026-08-12T13:06:13 | sha256 `8b48b675e472f66889efc47d546ab3c791a56a8c6e890d8311093ff64e364db9`
- `Content/Python/OperationSunscar/AutomationV1/inspect_package_reload_api_v1.py` | 1193 bytes | mtime 2026-08-12T13:06:13 | sha256 `c48d1047e694b51aeb4a184dacd443f902ce16eae46130b5536012642f759f51`
- `Content/Python/OperationSunscar/AutomationV1/old_town_align_storage_scrap_support_v1.py` | 2726 bytes | mtime 2026-08-12T13:06:13 | sha256 `3c6408f9bb90b3b1ac995043ab24d70423cea528591112025755edaec0161ba4`
- `Content/Python/OperationSunscar/AutomationV1/old_town_asset_inspector.py` | 6684 bytes | mtime 2026-08-12T13:06:13 | sha256 `f970a14a608fbc26fc2147ba73d67385810f882036ab5eb04cb6b024a97d6a1b`
- `Content/Python/OperationSunscar/AutomationV1/old_town_building_support_audit_v1.py` | 3751 bytes | mtime 2026-08-12T13:06:13 | sha256 `724d12dace630099255b9108644185e42842991f859b1ad4d5f4931660a14a73`
- `Content/Python/OperationSunscar/AutomationV1/old_town_building_support_audit_v2.py` | 6924 bytes | mtime 2026-08-12T13:06:13 | sha256 `068bbb7bbce08e4604780b36938457263ddb37bf233d0e09bb88351db4fa57f9`
- `Content/Python/OperationSunscar/AutomationV1/old_town_cleanup_rejected_preview_packages.py` | 1523 bytes | mtime 2026-08-12T13:06:13 | sha256 `857d17c7cb78e313c7fb6cd8eec6d5dc378d1d7b13bb6c10b4a1fa97804a8646`
- `Content/Python/OperationSunscar/AutomationV1/old_town_complete_prototype_facades_v1.py` | 5213 bytes | mtime 2026-08-12T13:06:13 | sha256 `b20b328b0db33e8d39402bdc49b33ad165445e86d618b478f2e6824681420e5c`
- `Content/Python/OperationSunscar/AutomationV1/old_town_complete_ss005_facade_preview_v1.py` | 4284 bytes | mtime 2026-08-12T13:06:13 | sha256 `8147a03222613f1a2de4b5655845aaada19062f0dfcf6846470c78273de60677`
- `Content/Python/OperationSunscar/AutomationV1/old_town_connected_slice_builder.py` | 9645 bytes | mtime 2026-08-12T13:06:13 | sha256 `752c6b69af98562d21ec93a4ed44cd239d04467f19ce7aadb7f105552a02d1a7`
- `Content/Python/OperationSunscar/AutomationV1/old_town_connected_slice_discard_preview.py` | 1471 bytes | mtime 2026-08-12T13:06:13 | sha256 `243c1bb2d85b81e350d0e528fd9f72bcf4ae34cfb8d3fa0d3547c02b78632e19`
- `Content/Python/OperationSunscar/AutomationV1/old_town_connected_slice_visibility_audit.py` | 4030 bytes | mtime 2026-08-12T13:06:13 | sha256 `063e6e9c34a3add046cdc136c6b4f8641af658194318305aa7a8161b9ffa37f5`
- `Content/Python/OperationSunscar/AutomationV1/old_town_core_cover_finish_v1.py` | 10046 bytes | mtime 2026-08-12T13:06:13 | sha256 `b4bc24e055a735425979b52fbbc859b4e0fb4af867d87f72be465d4260b4569a`
- `Content/Python/OperationSunscar/AutomationV1/old_town_core_cover_proxy_audit_v1.py` | 4361 bytes | mtime 2026-08-12T13:06:13 | sha256 `0c21da0ec07a228c20ccd71eec24176b961ef8a7d285c19293632c74d5fcc558`
- `Content/Python/OperationSunscar/AutomationV1/old_town_core_route_material_pass_v1.py` | 4324 bytes | mtime 2026-08-12T13:06:13 | sha256 `c0fc63432d8819731ea2f4ccee8b4d9d220927a0f74ca7159f61618906b7eb55`
- `Content/Python/OperationSunscar/AutomationV1/old_town_core_site_material_pass_v1.py` | 4997 bytes | mtime 2026-08-12T13:06:13 | sha256 `01a7b6975554e968241a108c3791ff4ef27b5856aec63c653df9a02d2c460e54`
- `Content/Python/OperationSunscar/AutomationV1/old_town_core_site_surface_audit_v1.py` | 1916 bytes | mtime 2026-08-12T13:06:13 | sha256 `9928d29a9e954c774591ee081499b1198423bc1231e6ada2f2ca90a9107e4626`
- `Content/Python/OperationSunscar/AutomationV1/old_town_correct_automation_yaw_v1.py` | 4355 bytes | mtime 2026-08-12T13:06:13 | sha256 `6eb562a23ac6d6897a2e459c0a3e00fd5b274b2f8c4d8074114d9bba6364a296`
- `Content/Python/OperationSunscar/AutomationV1/old_town_correct_checkpoint_square_orientation_v1.py` | 3510 bytes | mtime 2026-08-12T13:06:13 | sha256 `35568dc40d1d05cb4b32608363db2a8f9d9b0d7b5c6a422c1f9309d75250c72d`
- `Content/Python/OperationSunscar/AutomationV1/old_town_correct_remaining_scatter_support_v1.py` | 3325 bytes | mtime 2026-08-12T13:06:13 | sha256 `f5bbc663f8b9214994d82a7209494681b49a2224ff8dd943a1b0d52b96aaf89f`
- `Content/Python/OperationSunscar/AutomationV1/old_town_correct_sandbag_clusters_v2.py` | 5756 bytes | mtime 2026-08-12T13:06:13 | sha256 `ae3d99a9ed18ac5f45b2f8f01168ed09385ab718d25b62d785210e644d863d64`
- `Content/Python/OperationSunscar/AutomationV1/old_town_correct_vehicle_support_v1.py` | 3560 bytes | mtime 2026-08-12T13:06:13 | sha256 `a09e08c00e3aa15f68cde6d1e8fde4c1a10956abf752e0f25af0df235f7bba81`
- `Content/Python/OperationSunscar/AutomationV1/old_town_corrugated_support_audit_v1.py` | 2749 bytes | mtime 2026-08-12T13:06:13 | sha256 `c7d9b338e2f373217217fe0cbb1225c496b8e8bb4b718b67184665ed3459181f`
- `Content/Python/OperationSunscar/AutomationV1/old_town_dirty_package_audit.py` | 1828 bytes | mtime 2026-08-12T13:06:13 | sha256 `ee75a8ee2ca3b9dec0f0badabfd603f832dd95f559ea890b51c5f3f48c96dc7c`
- `Content/Python/OperationSunscar/AutomationV1/old_town_discard_facade_damage_preview_v1.py` | 1531 bytes | mtime 2026-08-12T13:06:13 | sha256 `890fa5e6f314c7dcdf6791e5b9cf413e76ae5a075f8e4cdfd89381071659f241`
- `Content/Python/OperationSunscar/AutomationV1/old_town_discard_facade_surface_showcase_v1.py` | 1566 bytes | mtime 2026-08-12T13:06:13 | sha256 `1c008ed03d8916a003f34fb001729c899479f057baccb0dc63ea249725acc154`
- `Content/Python/OperationSunscar/AutomationV1/old_town_discard_flaked_facade_preview_v1.py` | 2239 bytes | mtime 2026-08-12T13:06:13 | sha256 `ab1c8a8e8c7f58e757a84c3dd469ea9861c8679101e59235ac8c1fcd8bbb6605`
- `Content/Python/OperationSunscar/AutomationV1/old_town_discard_large_utility_preview_v1.py` | 1753 bytes | mtime 2026-08-12T13:06:13 | sha256 `afd66e7ff3c595b4ff83ce64a5af997d8d474e4fc4d03d0297f4e7c68d4bddaf`
- `Content/Python/OperationSunscar/AutomationV1/old_town_discard_material_showcase.py` | 1233 bytes | mtime 2026-08-12T13:06:13 | sha256 `0ed656191a407f8259931e353d94916d22fe565a8fb3a8c114f0134d29e2bd54`
- `Content/Python/OperationSunscar/AutomationV1/old_town_door_asset_probe_v1.py` | 1814 bytes | mtime 2026-08-12T13:06:13 | sha256 `fcfe5e4ce89c1c897a9693d3927ddc824cb4168cf07421a54b46d9f38541e7ab`
- `Content/Python/OperationSunscar/AutomationV1/old_town_door_proxy_audit_v1.py` | 2313 bytes | mtime 2026-08-12T13:06:13 | sha256 `9b6c37ebb5400295427d39fe67e48e002d4b08aec69c21e64db277eec408c866`
- `Content/Python/OperationSunscar/AutomationV1/old_town_door_replacement_audit_v1.py` | 3018 bytes | mtime 2026-08-12T13:06:13 | sha256 `e0b2907f4df4d0aaec3fa0455ce5ee2181b42b4a195822ec24b7a594df9defdb`
- `Content/Python/OperationSunscar/AutomationV1/old_town_duplicate_location_audit_v1.py` | 2682 bytes | mtime 2026-08-12T13:06:13 | sha256 `3fc2777e2226962e3cf70569467bbdf1438db920fc910795049169a596de10fe`
- `Content/Python/OperationSunscar/AutomationV1/old_town_electrical_box_audit_v1.py` | 3365 bytes | mtime 2026-08-12T13:06:13 | sha256 `7b265a6e6c4f4302ac70aa1af64ec0b8204894fbab7faacade2a695bd421d393`
- `Content/Python/OperationSunscar/AutomationV1/old_town_electrical_box_builder_v1.py` | 6244 bytes | mtime 2026-08-12T13:06:13 | sha256 `6e48bf59c81603a3b6cf549d73cfd88643d664b01c125504661c1301bfbb35c7`
- `Content/Python/OperationSunscar/AutomationV1/old_town_end_pie_v1.py` | 307 bytes | mtime 2026-08-12T13:06:13 | sha256 `e77e5610d27fce1e630212d2b7873f7a6f18a3b645a59afd3f46713af9ab487b`
- `Content/Python/OperationSunscar/AutomationV1/old_town_expand_stucco_facades_v1.py` | 4121 bytes | mtime 2026-08-12T13:06:13 | sha256 `c3c0e6d629b2bbca1379af9ca94e980cf31bb11a75ed2f533985c30bd2838f7a`
- `Content/Python/OperationSunscar/AutomationV1/old_town_exterior_completion_audit_v1.py` | 4891 bytes | mtime 2026-08-12T13:06:13 | sha256 `d8209be70808752ee907ac323f1d045762f49ee8b92f1d9fca99662f3aa3e15a`
- `Content/Python/OperationSunscar/AutomationV1/old_town_exterior_completion_audit_v2.py` | 6116 bytes | mtime 2026-08-12T13:06:13 | sha256 `d32cda7134467353d8f35dfb23ef4bbe4513d0882ab298b0e922d3c99e5b44d2`
- `Content/Python/OperationSunscar/AutomationV1/old_town_exterior_completion_builder_v1.py` | 18322 bytes | mtime 2026-08-12T13:06:13 | sha256 `3530ea978e29e34208f41743794c646f614a95823c720ec7ff2da2cdbbac0ef7`
- `Content/Python/OperationSunscar/AutomationV1/old_town_facade_conduit_audit_v1.py` | 4826 bytes | mtime 2026-08-12T13:06:13 | sha256 `827cf7142252d56b67b4e5a0e433429e95d37209b9211ca02215f044f0720f64`
- `Content/Python/OperationSunscar/AutomationV1/old_town_facade_conduit_builder_v1.py` | 8319 bytes | mtime 2026-08-12T13:06:13 | sha256 `cbc859d3aecdb8d7d8bc4a1c8b4421b90776be977a9dd10eaad05280c7143982`
- `Content/Python/OperationSunscar/AutomationV1/old_town_facade_damage_audit_v1.py` | 3424 bytes | mtime 2026-08-12T13:06:13 | sha256 `f301f19cff98d6a35629f84161d6a518f803919c5495276ddc9ceb341db0ed4d`
- `Content/Python/OperationSunscar/AutomationV1/old_town_facade_damage_builder_v1.py` | 6615 bytes | mtime 2026-08-12T13:06:13 | sha256 `e6a17b3fbaf8b81f286fd7c37a8a1f5e5817d08385b5372afe61bfef1486d68e`
- `Content/Python/OperationSunscar/AutomationV1/old_town_facade_expansion_audit_v1.py` | 3742 bytes | mtime 2026-08-12T13:06:13 | sha256 `f1475ff7f63796c9b9f9eddea435a66e1919f931f24c7d3b2b33d2dd5b086ce4`
- `Content/Python/OperationSunscar/AutomationV1/old_town_facade_material_preview_v1.py` | 6674 bytes | mtime 2026-08-12T13:06:13 | sha256 `0d61458865b0f439847fa4102c7b8c19e33f1510adc7cfdc5fb2ae2b748b7982`
- `Content/Python/OperationSunscar/AutomationV1/old_town_facade_site_prototype_v1.py` | 3334 bytes | mtime 2026-08-12T13:06:13 | sha256 `4c264f8a3061cde07bfbece5b70a331dd98ce8f51abdcdc6d582ceff762e4a76`
- `Content/Python/OperationSunscar/AutomationV1/old_town_facade_surface_showcase_v1.py` | 5263 bytes | mtime 2026-08-12T13:06:13 | sha256 `be174ba3cb311da794bc880965755cd4746948ab69894c50832f7db2b64f10cf`
- `Content/Python/OperationSunscar/AutomationV1/old_town_finalize_landscape_material_v1.py` | 5924 bytes | mtime 2026-08-12T13:06:13 | sha256 `a4f51f56c45f59ce80b8e97cbcd1580b4ef5b836d96cec9eb2310442d484acfe`
- `Content/Python/OperationSunscar/AutomationV1/old_town_flaked_facade_prototype_v1.py` | 3344 bytes | mtime 2026-08-12T13:06:13 | sha256 `856bacf8cbc71d7fb14d2065bf158de8823c6c23de75aa4e165307f02ca3315c`
- `Content/Python/OperationSunscar/AutomationV1/old_town_focus_exterior_completion_review_v1.py` | 1122 bytes | mtime 2026-08-12T13:06:13 | sha256 `84eb4cbdd4b966d5694a98699455d97eb582fcb2f26612a9f594c64205f31c72`
- `Content/Python/OperationSunscar/AutomationV1/old_town_focus_facade_conduit_review_v1.py` | 1137 bytes | mtime 2026-08-12T13:06:13 | sha256 `cb1cc8745c423d7ef14c157ecc075e2dc1ee21cb79317b8f6d931293fbec2023`
- `Content/Python/OperationSunscar/AutomationV1/old_town_focus_hand_tool_review_v1.py` | 1149 bytes | mtime 2026-08-12T13:06:13 | sha256 `a605b4fe97c4dd9913ab492ba48a7f51c583e3532392c314dcf5bd8f1d0cef41`
- `Content/Python/OperationSunscar/AutomationV1/old_town_focus_industrial_review_v1.py` | 1125 bytes | mtime 2026-08-12T13:06:13 | sha256 `3b1e203610f9097706b92e5b5b0e8cdcd222c4c90520576d8e7b275d2c922fe9`
- `Content/Python/OperationSunscar/AutomationV1/old_town_focus_landmark_sign_review_v1.py` | 1143 bytes | mtime 2026-08-12T13:06:13 | sha256 `4226709988540a0c95f6a7b0c2f24db5a0e19bdb33cd35325c003fdc2d8bcae2`
- `Content/Python/OperationSunscar/AutomationV1/old_town_focus_rooftop_utility_review_v1.py` | 1148 bytes | mtime 2026-08-12T13:06:13 | sha256 `62d5c0df4a7f91a0fb5b4500ad2ab1c91070d3d4445a71b25a6e2e7a9125bfe9`
- `Content/Python/OperationSunscar/AutomationV1/old_town_focus_window_shutter_review_v1.py` | 1151 bytes | mtime 2026-08-12T13:06:13 | sha256 `6b806f053ef69b19bfeba575851c5b09c3a02f5dcbedfe04fb55e193b6fade4e`
- `Content/Python/OperationSunscar/AutomationV1/old_town_furniture_audit_v1.py` | 4213 bytes | mtime 2026-08-12T13:06:13 | sha256 `bfffee0c9ef4d1d47c389d209e33b5aa51f3e93d90bd64a0ed911bd543bc997f`
- `Content/Python/OperationSunscar/AutomationV1/old_town_furniture_builder_v1.py` | 7818 bytes | mtime 2026-08-12T13:06:13 | sha256 `947d8533ccff717b4c9fb6b33885c60c360e8e758ac0c317d69df07229f05957`
- `Content/Python/OperationSunscar/AutomationV1/old_town_gameplay_route_audit_v1.py` | 3956 bytes | mtime 2026-08-12T13:06:13 | sha256 `83bec6b4b5f3e8763880e263defdc888692c82f762d0f8aa6e1f1fac4e1add49`
- `Content/Python/OperationSunscar/AutomationV1/old_town_ground_checkpoint_sandbags_v1.py` | 4684 bytes | mtime 2026-08-12T13:06:13 | sha256 `52f930a7e9652b28eb7c5d3a0798093fe5a037fbf17f9457c737140f74e378f7`
- `Content/Python/OperationSunscar/AutomationV1/old_town_ground_corrugated_assemblies_v1.py` | 3523 bytes | mtime 2026-08-12T13:06:13 | sha256 `16670f35782e3832e91d715f21f7f0549494b864cef4d2d5447967758b01bbb6`
- `Content/Python/OperationSunscar/AutomationV1/old_town_ground_material_audit_v1.py` | 2034 bytes | mtime 2026-08-12T13:06:13 | sha256 `e2defc6bcebdf6f844d2941daee311f959ffe47085fa0b26d7a2f20425f04218`
- `Content/Python/OperationSunscar/AutomationV1/old_town_ground_overlay_conformance_audit_v1.py` | 5815 bytes | mtime 2026-08-12T13:06:13 | sha256 `f536a0c67b7d2925689a9c242e472f8dfbe20f829600378aaff9ee442435ea5b`
- `Content/Python/OperationSunscar/AutomationV1/old_town_ground_overlay_conformance_v1.py` | 8499 bytes | mtime 2026-08-12T13:06:13 | sha256 `d9ebf7d0f32d6e4507d355cfa2e27eab2f254ba419150e354e6eb2fd1d17df5d`
- `Content/Python/OperationSunscar/AutomationV1/old_town_hand_tool_audit_v1.py` | 5914 bytes | mtime 2026-08-12T13:06:13 | sha256 `0174c99653650968f330147ecfd27363243cd575128f4656e513124081ac3bce`
- `Content/Python/OperationSunscar/AutomationV1/old_town_hand_tool_builder_v1.py` | 5833 bytes | mtime 2026-08-12T13:06:13 | sha256 `f80f1b4807fd844362b0c0e398c0b27b290c9d47c8fe4c7253116522712c8110`
- `Content/Python/OperationSunscar/AutomationV1/old_town_hand_tool_scope_audit_v1.py` | 5196 bytes | mtime 2026-08-12T13:06:13 | sha256 `5a49a2760781a9f5c11cf83948a60e9cc9a48d3690406290e41a073012fa16b4`
- `Content/Python/OperationSunscar/AutomationV1/old_town_hand_tool_support_fix_v1.py` | 3623 bytes | mtime 2026-08-12T13:06:13 | sha256 `ac9dce88eb549245c792d6244e6d5bb2a49a8d71d33e222ca5fd609cb214062d`
- `Content/Python/OperationSunscar/AutomationV1/old_town_hide_temporary_labels_v1.py` | 1739 bytes | mtime 2026-08-12T13:06:13 | sha256 `3b8223321d03b40189f1cf63b2507d30cd0cf9b7f217a7f99dba96ae2ab6e425`
- `Content/Python/OperationSunscar/AutomationV1/old_town_horizontal_surface_audit_v1.py` | 3899 bytes | mtime 2026-08-12T13:06:13 | sha256 `9fcb0ad35a349e1ea56221e37a2e848f7f3c82ebab4bae332e56800992bad511`
- `Content/Python/OperationSunscar/AutomationV1/old_town_horizontal_surface_finish_v1.py` | 5434 bytes | mtime 2026-08-12T13:06:13 | sha256 `7cad7dca61049a37700379ca6fb8c831d306bb4b487b28201a341bd562fbc9bf`
- `Content/Python/OperationSunscar/AutomationV1/old_town_industrial_detail_audit_v1.py` | 5577 bytes | mtime 2026-08-12T13:06:13 | sha256 `7438749f578d2c26dc8b1df835350aa842dbe2d90b531423785fabea29c8ee35`
- `Content/Python/OperationSunscar/AutomationV1/old_town_industrial_detail_builder_v1.py` | 8957 bytes | mtime 2026-08-12T13:06:13 | sha256 `493b8075dcec2a99859f405f6a0bb979d275d449afa785ffe41347728037e583`
- `Content/Python/OperationSunscar/AutomationV1/old_town_industrial_detail_landscape_support_fix_v2.py` | 3699 bytes | mtime 2026-08-12T13:06:13 | sha256 `8f57bbd04e2c49182eeae83bb314e68298e0afcfcc79e21adda4412c1cdd4be9`
- `Content/Python/OperationSunscar/AutomationV1/old_town_industrial_detail_support_fix_v1.py` | 3688 bytes | mtime 2026-08-12T13:06:13 | sha256 `e3c322bdffc7a49153173f9c0bf0cb05ae9b2cfb88ec832be9d6156c9dd061dc`
- `Content/Python/OperationSunscar/AutomationV1/old_town_interior_and_tower_surface_v1.py` | 4583 bytes | mtime 2026-08-12T13:06:13 | sha256 `849033e58c33e8682762fd139111582640e83b0906fd74ee47d312fe62414375`
- `Content/Python/OperationSunscar/AutomationV1/old_town_landmark_sign_audit_v1.py` | 5549 bytes | mtime 2026-08-12T13:06:13 | sha256 `c15c63b36d7ecc38836f2f48201d2a9808205f0978be5f85a1b345b2aadbb525`
- `Content/Python/OperationSunscar/AutomationV1/old_town_landmark_sign_builder_v1.py` | 9684 bytes | mtime 2026-08-12T13:06:13 | sha256 `99f372b4d52edfa2f45937e7482ceae30edf35fa8b38c75a74e3a0413716656c`
- `Content/Python/OperationSunscar/AutomationV1/old_town_landmark_sign_text_finish_v1.py` | 3803 bytes | mtime 2026-08-12T13:06:13 | sha256 `7e28c227f85978e8fb4c5af347b4fb8320ea4a4310981b3e7d4ef955d801dc65`
- `Content/Python/OperationSunscar/AutomationV1/old_town_landscape_material_pass_v1.py` | 6030 bytes | mtime 2026-08-12T13:06:13 | sha256 `d2c92c87909da1884b422cd94c699d1ee94b4a900a8159d10602807cda63ef76`
- `Content/Python/OperationSunscar/AutomationV1/old_town_landscape_probe.py` | 4087 bytes | mtime 2026-08-12T13:06:13 | sha256 `ee818670bf8fa65f9d6889b232c0222f5928d9e44fb9b99b89677f42f3b5c9c9`
- `Content/Python/OperationSunscar/AutomationV1/old_town_landscape_v2_api_probe.py` | 2093 bytes | mtime 2026-08-12T13:06:13 | sha256 `47208aa9442ea80a55066f1047888b4ee4ef5f0d77121b76cd58093c355d82c8`
- `Content/Python/OperationSunscar/AutomationV1/old_town_landscape_v2_preview.py` | 17426 bytes | mtime 2026-08-12T13:06:13 | sha256 `fa4a8396ef7982368e8b5b0c340a7fe654108a0eaf7b41b643459c096c76ade8`
- `Content/Python/OperationSunscar/AutomationV1/old_town_landscape_v2_preview_rollback.py` | 1881 bytes | mtime 2026-08-12T13:06:13 | sha256 `f4cd00796d2a11416725611838874c38334453535cd6e088560a51b0345b2f54`
- `Content/Python/OperationSunscar/AutomationV1/old_town_landscape_v2_preview_runner.py` | 383 bytes | mtime 2026-08-12T13:06:13 | sha256 `60897037c6cac9ebb819748829a74d2e2193309906508f22f9a8fc95aaf35728`
- `Content/Python/OperationSunscar/AutomationV1/old_town_large_ground_audit_v1.py` | 2777 bytes | mtime 2026-08-12T13:06:13 | sha256 `b7829f507e5b916cbed0ca053aae7babef5b2710b35e788c732e16a19a7b6751`
- `Content/Python/OperationSunscar/AutomationV1/old_town_large_utility_audit_v1.py` | 5685 bytes | mtime 2026-08-12T13:06:13 | sha256 `fc3b918e6f1ed9de7ac868acf7add424a6e01458fab1d8c1907ad7904ebc8240`
- `Content/Python/OperationSunscar/AutomationV1/old_town_large_utility_resolver_v1.py` | 9546 bytes | mtime 2026-08-12T13:06:13 | sha256 `a2ff04ff4c0f1be830b908d4d96aa83a275173ada52af35f9837431ddf28764b`
- `Content/Python/OperationSunscar/AutomationV1/old_town_level_dependency_closure_v1.py` | 7189 bytes | mtime 2026-08-12T13:06:13 | sha256 `d158b9cff1aaf1d26beb0d406fd8f989a3ecc375f2c975aa91e6b3d7ad8fb4d0`
- `Content/Python/OperationSunscar/AutomationV1/old_town_lighting_balance_audit_v1.py` | 2021 bytes | mtime 2026-08-12T13:06:13 | sha256 `d2732650a13d432dd6544643c0625ab031db20a4ccc066d5b2d3719545b78072`
- `Content/Python/OperationSunscar/AutomationV1/old_town_lighting_balance_v1.py` | 2809 bytes | mtime 2026-08-12T13:06:13 | sha256 `62e8cf63dbd98a4b94c2b1b624c85b98b3297ab68f33361b244e1aae545adb2d`
- `Content/Python/OperationSunscar/AutomationV1/old_town_market_ground_debris_audit_v1.py` | 3300 bytes | mtime 2026-08-12T13:06:13 | sha256 `9570048c2af58b5e6111dd58a36024f1e1be97b6e3edfc276467ecdd08ab10fa`
- `Content/Python/OperationSunscar/AutomationV1/old_town_market_ground_debris_builder_v1.py` | 6362 bytes | mtime 2026-08-12T13:06:13 | sha256 `9791eb3986a9b357251393a352c358d0a09ff87553f88037575441d200b2e66d`
- `Content/Python/OperationSunscar/AutomationV1/old_town_material_master_probe.py` | 4885 bytes | mtime 2026-08-12T13:06:13 | sha256 `0bd5bea91e3b9cca6d986de86c23209daff7060b0d1ac131cf1e4854ba55b361`
- `Content/Python/OperationSunscar/AutomationV1/old_town_material_showcase.py` | 2613 bytes | mtime 2026-08-12T13:06:13 | sha256 `f9005dfb499ed3bbf1760af16fd53368754a492453860d62369db8f44c7fa533`
- `Content/Python/OperationSunscar/AutomationV1/old_town_medium_utility_scope_audit_v1.py` | 2578 bytes | mtime 2026-08-12T13:06:13 | sha256 `caded81f34779e1742709f372c6b5329364356bbfcb3a722b5cfcceafa070231`
- `Content/Python/OperationSunscar/AutomationV1/old_town_named_compound_facades_v1.py` | 4704 bytes | mtime 2026-08-12T13:06:13 | sha256 `a0c507f638ede4f53ecfca6cabb316b7db90e2386af53f8fef80c531e4c79730`
- `Content/Python/OperationSunscar/AutomationV1/old_town_package_dirty_api_probe.py` | 546 bytes | mtime 2026-08-12T13:06:13 | sha256 `e9ee440b3499a9cdadb7b1449735c58b26fb5f5a0e52b081046b015fdfa4c429`
- `Content/Python/OperationSunscar/AutomationV1/old_town_perimeter_wall_material_pass_v1.py` | 3525 bytes | mtime 2026-08-12T13:06:13 | sha256 `2cca349cd6d5405241095dd9c0ef3b28b63355b7fb6135121a5b14c9cf2f159e`
- `Content/Python/OperationSunscar/AutomationV1/old_town_persistent_decorative_collision_v1.py` | 5188 bytes | mtime 2026-08-12T13:06:13 | sha256 `605c88238ea2cf30532b3b418b226b8e0eb38cbcd566de1d8e51cc02d1f5166d`
- `Content/Python/OperationSunscar/AutomationV1/old_town_post_yaw_cleanup_v1.py` | 5208 bytes | mtime 2026-08-12T13:06:13 | sha256 `adfd0dd7dfca08b5e6b565809f94dfc4c06a5d54a56e090611d46eaf5f5d5575`
- `Content/Python/OperationSunscar/AutomationV1/old_town_preflight.py` | 2852 bytes | mtime 2026-08-12T13:06:13 | sha256 `c465a8df8c8ce5c71620a9ea329c054abd09176886c102421c60810c2d0a8c82`
- `Content/Python/OperationSunscar/AutomationV1/old_town_reload_rejected_facade_packages.py` | 2639 bytes | mtime 2026-08-12T13:06:13 | sha256 `61b1d7f0ec0a0d7755115b20717169003d9a6ae74f4cdbe7480aabdb8b2830c0`
- `Content/Python/OperationSunscar/AutomationV1/old_town_remaining_prototype_material_audit_v1.py` | 3189 bytes | mtime 2026-08-12T13:06:13 | sha256 `05461de2230b903dcd095fcb951c45d752cd0a3c4070fb1cc6f9885bbd2bb4c6`
- `Content/Python/OperationSunscar/AutomationV1/old_town_remaining_scatter_builder_v1.py` | 7633 bytes | mtime 2026-08-12T13:06:13 | sha256 `7e3484f0c09d568d4c03cdf08f7de4233c48b9276322a651b9b69f5d2b047b29`
- `Content/Python/OperationSunscar/AutomationV1/old_town_remaining_scatter_geometry_audit_v1.py` | 3723 bytes | mtime 2026-08-12T13:06:13 | sha256 `8d3addb113bc6dba6b5270f5f63150760049215cda311fdce99833864c7ae270`
- `Content/Python/OperationSunscar/AutomationV1/old_town_remaining_scatter_scope_audit_v1.py` | 4194 bytes | mtime 2026-08-12T13:06:13 | sha256 `c67e3aa2cbeb7eade9f26b47dc1a3122a4c26a24ee06e3383e652edf4f981fbf`
- `Content/Python/OperationSunscar/AutomationV1/old_town_remaining_small_electrical_audit_v1.py` | 4577 bytes | mtime 2026-08-12T13:06:13 | sha256 `1eaaeecb4555b29c0d350bcde39319bc1fd8b3c5468a864846d854ad7fd3d8c3`
- `Content/Python/OperationSunscar/AutomationV1/old_town_remaining_small_electrical_builder_v1.py` | 7579 bytes | mtime 2026-08-12T13:06:13 | sha256 `ac6633be414e74c6d4eef52621dfb1b548fae5c7fc278a788bcf050cdf415aa0`
- `Content/Python/OperationSunscar/AutomationV1/old_town_remaining_small_electrical_scope_audit_v1.py` | 2819 bytes | mtime 2026-08-12T13:06:13 | sha256 `18447f1aec7ca114e35dafa501509dc57eab3056a742d4b0fcc5535f82d4bc96`
- `Content/Python/OperationSunscar/AutomationV1/old_town_repair_world_aligned_ground_v1.py` | 4178 bytes | mtime 2026-08-12T13:06:13 | sha256 `3d5ac8ec1abdc58d5504f477dd55b58c251a69bfac07b1527235f8535767b1e1`
- `Content/Python/OperationSunscar/AutomationV1/old_town_replace_door_proxies_v1.py` | 5685 bytes | mtime 2026-08-12T13:06:13 | sha256 `e1d71a88d721f25b05a8e94c3f9f4bb81dd1de395ff2a10f39d27f67eb0b2e39`
- `Content/Python/OperationSunscar/AutomationV1/old_town_replace_raw_grass_v1.py` | 4157 bytes | mtime 2026-08-12T13:06:13 | sha256 `7e2fde2d9ef98d041f102b4e8ffb7a97a0cbd242a707757d15f6913b244d41a9`
- `Content/Python/OperationSunscar/AutomationV1/old_town_replace_vehicle_proxies_v1.py` | 6037 bytes | mtime 2026-08-12T13:06:13 | sha256 `c7bcd430a3378e631f7a358a82bfdcc2830689794a0983a3cfba9f3276a162f9`
- `Content/Python/OperationSunscar/AutomationV1/old_town_rooftop_utility_audit_v1.py` | 4497 bytes | mtime 2026-08-12T13:06:13 | sha256 `270e1c54318ced561a9dfb2e77f0e3287acfb243d102f6e66124091ed003a42c`
- `Content/Python/OperationSunscar/AutomationV1/old_town_rooftop_utility_builder_v1.py` | 7263 bytes | mtime 2026-08-12T13:06:13 | sha256 `e177d6f4fe291c303d885c5af553de7658bfa267fa7dac16fa0cdab7bc630ac5`
- `Content/Python/OperationSunscar/AutomationV1/old_town_rotator_probe.py` | 275 bytes | mtime 2026-08-12T13:06:13 | sha256 `6f7b7e7b14013b768ba7f76c079a90e4fc63d4a8b1304bc83246aa65727fc008`
- `Content/Python/OperationSunscar/AutomationV1/old_town_route_material_probe_v1.py` | 2269 bytes | mtime 2026-08-12T13:06:13 | sha256 `cd35c22e034d728621eac54870918df264663d32943397fd00fb7894b85d6f14`
- `Content/Python/OperationSunscar/AutomationV1/old_town_sandbag_audit.py` | 7226 bytes | mtime 2026-08-12T13:06:13 | sha256 `76d0e856f775497cbe24c1313daf58ad872c144be6eacb691eeb560a6cc4557c`
- `Content/Python/OperationSunscar/AutomationV1/old_town_save_checkpoint_sandbag_fix_v1.py` | 2485 bytes | mtime 2026-08-12T13:06:13 | sha256 `75a8e6f975a3fa096e11229ad0a880b0ebd1c1b3627aecdcab397e1f879b8cf1`
- `Content/Python/OperationSunscar/AutomationV1/old_town_save_checkpoint_square_orientation_v1.py` | 1944 bytes | mtime 2026-08-12T13:06:13 | sha256 `4f3eec5c175de7522589f7441599f5f39422d0cb3a59a3eb6cfc0e92c263ec16`
- `Content/Python/OperationSunscar/AutomationV1/old_town_save_complete_prototype_facades_v1.py` | 4084 bytes | mtime 2026-08-12T13:06:13 | sha256 `e888c4a0d1f5feb2400d364892f9b35ab7766b70a15147ebf4e0a82cc42d39f0`
- `Content/Python/OperationSunscar/AutomationV1/old_town_save_connected_slice_packages.py` | 2865 bytes | mtime 2026-08-12T13:06:13 | sha256 `540f6aaa3294d38d58e5cce2183efdeeb708e96817a9dde117fc2febc46af2dc`
- `Content/Python/OperationSunscar/AutomationV1/old_town_save_core_cover_finish_v1.py` | 3763 bytes | mtime 2026-08-12T13:06:13 | sha256 `fcd104da377f3b1cb5f96157313f908839a41c77c1a1cc01205f1452b9d91376`
- `Content/Python/OperationSunscar/AutomationV1/old_town_save_core_route_materials_v1.py` | 2280 bytes | mtime 2026-08-12T13:06:13 | sha256 `0e5b5a87317fabe257e3700c8e37358cbf6720c4f7fd7337c01c87319cef7974`
- `Content/Python/OperationSunscar/AutomationV1/old_town_save_core_site_materials_v1.py` | 2297 bytes | mtime 2026-08-12T13:06:13 | sha256 `ed05a9c39b490771c46615528d462d66c779f99a28132f2867b5e1db3df464e2`
- `Content/Python/OperationSunscar/AutomationV1/old_town_save_corrugated_assemblies_v1.py` | 1900 bytes | mtime 2026-08-12T13:06:13 | sha256 `5a6a12fd98f1c129fdea0e9745052d5c5afc866e7ff1b8077486d90a77399278`
- `Content/Python/OperationSunscar/AutomationV1/old_town_save_door_replacements_v1.py` | 2328 bytes | mtime 2026-08-12T13:06:13 | sha256 `06abebfcfe50d1ea1367d0144160ae19601e56e8aaa96ecae0456414b2a6374f`
- `Content/Python/OperationSunscar/AutomationV1/old_town_save_electrical_boxes_v1.py` | 2454 bytes | mtime 2026-08-12T13:06:13 | sha256 `a5a6f43be2ba3f26700fa7760be095bb7236d8d521766e8c1532aea7b852af5b`
- `Content/Python/OperationSunscar/AutomationV1/old_town_save_exterior_completion_v1.py` | 4648 bytes | mtime 2026-08-12T13:06:13 | sha256 `d88a748714bccdd63b78eef2e686865c4bbd8ce136182fc05a0678705c53122a`
- `Content/Python/OperationSunscar/AutomationV1/old_town_save_facade_conduit_v1.py` | 3027 bytes | mtime 2026-08-12T13:06:13 | sha256 `eecea9c740e33b5fedce50f7fe3d16f3434c1d89436b6f10f06e347cbc994a44`
- `Content/Python/OperationSunscar/AutomationV1/old_town_save_facade_materials_v1.py` | 2305 bytes | mtime 2026-08-12T13:06:13 | sha256 `a042b18cba3ba160a9135243ada0bd4789d33ecec8061f5000f14b2c5f6d09e5`
- `Content/Python/OperationSunscar/AutomationV1/old_town_save_flaked_facade_v1.py` | 2581 bytes | mtime 2026-08-12T13:06:13 | sha256 `5d17cb0af9777da884cce632e997f876311e1c45a782dc580fc81155b3e8ec14`
- `Content/Python/OperationSunscar/AutomationV1/old_town_save_furniture_packages_v1.py` | 3102 bytes | mtime 2026-08-12T13:06:13 | sha256 `79f4fa9221f07d1776813d066b52b56014f138b65c5d2de670f056bcf8c0a9b0`
- `Content/Python/OperationSunscar/AutomationV1/old_town_save_grass_replacement_v1.py` | 2506 bytes | mtime 2026-08-12T13:06:13 | sha256 `7e3296a94570219a6e5ea0c64cf3d6ef919b2bdb3b306c2e0bd84f08963f47b9`
- `Content/Python/OperationSunscar/AutomationV1/old_town_save_ground_overlay_conformance_v1.py` | 6197 bytes | mtime 2026-08-12T13:06:13 | sha256 `303b6861d0454cffbe71012a478ed4fea945c403f2a70a3c1b5c3b2a7d2b024b`
- `Content/Python/OperationSunscar/AutomationV1/old_town_save_hand_tool_v1.py` | 2922 bytes | mtime 2026-08-12T13:06:13 | sha256 `f1dd569ca3e4380fdfe3bdc760a313d1c867f414bca2674de084e476d861b295`
- `Content/Python/OperationSunscar/AutomationV1/old_town_save_horizontal_surface_finish_v1.py` | 3703 bytes | mtime 2026-08-12T13:06:13 | sha256 `a662d7a17963410495a48369e53e00109aebb14c39e8f52c8ecc8d5dc45b27cd`
- `Content/Python/OperationSunscar/AutomationV1/old_town_save_industrial_detail_landscape_support_v2.py` | 2348 bytes | mtime 2026-08-12T13:06:13 | sha256 `a8f834e954738b3b82832bfe8137b33c1b5f78b5ff19fce07a491b948584960d`
- `Content/Python/OperationSunscar/AutomationV1/old_town_save_industrial_detail_v1.py` | 3066 bytes | mtime 2026-08-12T13:06:13 | sha256 `86b36c1c5f50b7ca8f8218ce5b843b40ff9aeacd5c2e1abcfe08ee4d59458a26`
- `Content/Python/OperationSunscar/AutomationV1/old_town_save_interior_and_tower_surface_v1.py` | 3040 bytes | mtime 2026-08-12T13:06:13 | sha256 `278015fd83931f435e865e743ec9bf8a9265e47a7d1715f0ea87c8578008abcd`
- `Content/Python/OperationSunscar/AutomationV1/old_town_save_landmark_sign_v1.py` | 3027 bytes | mtime 2026-08-12T13:06:13 | sha256 `51b48f587fe000d89b73b3cd0d9b56589baa4682f2b7bbd2cd7ea32ae436f731`
- `Content/Python/OperationSunscar/AutomationV1/old_town_save_landscape_material_v1.py` | 2783 bytes | mtime 2026-08-12T13:06:13 | sha256 `ab7e447632412c2f4eadab7d3df6bc6e17f7c43891ad80f427c75851fcde6dae`
- `Content/Python/OperationSunscar/AutomationV1/old_town_save_large_utility_v1.py` | 4033 bytes | mtime 2026-08-12T13:06:13 | sha256 `b16e6efaa9f64da8041af0be435cdb66c23c5708b8ccf2e646782010ba6fdd47`
- `Content/Python/OperationSunscar/AutomationV1/old_town_save_medium_utility_enclosures_v1.py` | 2603 bytes | mtime 2026-08-12T13:06:13 | sha256 `6eb790855dce1d56135dcadc80e9535461949dfdfb404d1c7d7d32569376a88f`
- `Content/Python/OperationSunscar/AutomationV1/old_town_save_named_compound_facades_v1.py` | 3643 bytes | mtime 2026-08-12T13:06:13 | sha256 `81cb0efa5a16064f699f79429dc331855270a2f73c8df7d219dd4aee744943f6`
- `Content/Python/OperationSunscar/AutomationV1/old_town_save_perimeter_wall_materials_v1.py` | 2313 bytes | mtime 2026-08-12T13:06:13 | sha256 `c92a32ba52c6ef517cd19300c2b75159c3006e835eb758cba4ea04f6f55559d4`
- `Content/Python/OperationSunscar/AutomationV1/old_town_save_persistent_decorative_collision_v1.py` | 3008 bytes | mtime 2026-08-12T13:06:13 | sha256 `8565889b399751bf486e2a68dc69793a67077d9382618d1e471c6e78b7c28637`
- `Content/Python/OperationSunscar/AutomationV1/old_town_save_remaining_scatter_v1.py` | 3345 bytes | mtime 2026-08-12T13:06:13 | sha256 `9a8cc61deccc3c25cb29f496b25a0d988d023887c9d222f9b88d3fe072c6cd80`
- `Content/Python/OperationSunscar/AutomationV1/old_town_save_remaining_small_electrical_v1.py` | 2673 bytes | mtime 2026-08-12T13:06:13 | sha256 `94590cb6f24507f75e969ed7263810dec66a5a69dc7155e3cf46d152694b2ace`
- `Content/Python/OperationSunscar/AutomationV1/old_town_save_rooftop_utility_v1.py` | 3040 bytes | mtime 2026-08-12T13:06:13 | sha256 `14c2aacbf8e86935a55ada3afb19303706cc883cbdfba789baaa7295626a19c1`
- `Content/Python/OperationSunscar/AutomationV1/old_town_save_sandbag_clusters_v2.py` | 2237 bytes | mtime 2026-08-12T13:06:13 | sha256 `25cbe3b2a93fc1cfabd5491e8b8a721429506088d3a5fb9a8af757a0efd2fffe`
- `Content/Python/OperationSunscar/AutomationV1/old_town_save_ss005_facade_v1.py` | 3298 bytes | mtime 2026-08-12T13:06:13 | sha256 `41948c344630e85e6c64826f2ade177eac3ee2bf30d3faadfa1b81d17e4dfa8e`
- `Content/Python/OperationSunscar/AutomationV1/old_town_save_ss010_foundation_support_expand_v1.py` | 2927 bytes | mtime 2026-08-12T13:06:13 | sha256 `4da5f8db05790cb7d78690f1aa2129cd3263a05646b3735b13a3c573195780fb`
- `Content/Python/OperationSunscar/AutomationV1/old_town_save_ss010_foundation_support_v1.py` | 3734 bytes | mtime 2026-08-12T13:06:13 | sha256 `6e5b4791fee6da8099ae218c108940ff7dca5d371a438659008bc90c154d7109`
- `Content/Python/OperationSunscar/AutomationV1/old_town_save_storage_scrap_v1.py` | 2539 bytes | mtime 2026-08-12T13:06:13 | sha256 `d82adad1a85e878d9ffb1db293690d648eecd2af80cec72500583b1754a9fade`
- `Content/Python/OperationSunscar/AutomationV1/old_town_save_structural_materials_v1.py` | 2307 bytes | mtime 2026-08-12T13:06:13 | sha256 `923775fa6a0f65ae94e455f8289497b8cbca46be1f5520f7677ddc99e296e7e6`
- `Content/Python/OperationSunscar/AutomationV1/old_town_save_stucco_facades_v1.py` | 2717 bytes | mtime 2026-08-12T13:06:13 | sha256 `585b2b6d298544fec0e7963c1b7dc5b2c30a48e5aeb30f59c452f16422f534d2`
- `Content/Python/OperationSunscar/AutomationV1/old_town_save_vehicle_replacements_v1.py` | 2252 bytes | mtime 2026-08-12T13:06:13 | sha256 `f035423ccd13155ca726e085e11cdaacd15c62eb83762e0ac0aba2310c778239`
- `Content/Python/OperationSunscar/AutomationV1/old_town_save_window_shutter_v1.py` | 2977 bytes | mtime 2026-08-12T13:06:13 | sha256 `613e6578ebefd61379d6619656d27471af3df775fbdab55985e92428c8eaac61`
- `Content/Python/OperationSunscar/AutomationV1/old_town_save_world_aligned_facade_rollout_v1.py` | 3624 bytes | mtime 2026-08-12T13:06:13 | sha256 `b1892e37e5de15542de8bebe2dda5b536eb56150d76e9a7327744a1e93e002d1`
- `Content/Python/OperationSunscar/AutomationV1/old_town_save_world_aligned_facade_v1.py` | 3798 bytes | mtime 2026-08-12T13:06:13 | sha256 `d3535a68dd31a2a323ea407dc1928f51b7a35c69f04e44cdefa8d1d386136a05`
- `Content/Python/OperationSunscar/AutomationV1/old_town_save_world_aligned_ground_surface_v1.py` | 4417 bytes | mtime 2026-08-12T13:06:13 | sha256 `16c0ad4869a117206c13eba7c601cfac9b44a777984586486cb0e5352996ddc0`
- `Content/Python/OperationSunscar/AutomationV1/old_town_save_yaw_and_market_v1.py` | 2829 bytes | mtime 2026-08-12T13:06:13 | sha256 `612e1585f2538ab6d340b72e741a1368540add592802f04b4fae5354076a8339`
- `Content/Python/OperationSunscar/AutomationV1/old_town_show_temporary_labels_v1.py` | 1742 bytes | mtime 2026-08-12T13:06:13 | sha256 `a28beba3e51f7b260aab04b0145150e9c97734b36876f61329e04b35a60eaacd`
- `Content/Python/OperationSunscar/AutomationV1/old_town_site_coverage_audit_v1.py` | 3559 bytes | mtime 2026-08-12T13:06:13 | sha256 `54ed263028228a17fb3226a8a0cd833ad4d87cf803562eb17580bf1eed22996f`
- `Content/Python/OperationSunscar/AutomationV1/old_town_ss005_facade_audit_v1.py` | 2256 bytes | mtime 2026-08-12T13:06:13 | sha256 `6212d31b11d018242d62e8db1b3a2ed3e242c2355d97f4ba013648224433682b`
- `Content/Python/OperationSunscar/AutomationV1/old_town_ss005_pilot_manifest_v1.py` | 8674 bytes | mtime 2026-08-12T13:06:13 | sha256 `b378005904156260d2f7d16324f024e44d48086798ad7e7c7403de027499a5e1`
- `Content/Python/OperationSunscar/AutomationV1/old_town_ss010_foundation_support_expand_v1.py` | 3589 bytes | mtime 2026-08-12T13:06:13 | sha256 `63d91bc8931f96d16dd17716ba70b1a955b8ff9dee23350c4ef7667b877b28a9`
- `Content/Python/OperationSunscar/AutomationV1/old_town_ss010_foundation_support_v1.py` | 5046 bytes | mtime 2026-08-12T13:06:13 | sha256 `42aeeec03b6fd2dc407678210bd42bc5c1cc4fd737315cae1b68d9763b7e79dd`
- `Content/Python/OperationSunscar/AutomationV1/old_town_start_pie_v1.py` | 636 bytes | mtime 2026-08-12T13:06:13 | sha256 `465f67a87f55764cdc28877c070dc62d133212c3d4e991d5f1e3b9d07793df15`
- `Content/Python/OperationSunscar/AutomationV1/old_town_static_vehicle_audit_v1.py` | 4422 bytes | mtime 2026-08-12T13:06:13 | sha256 `6fad0fa688633115bb5fbf07f68ed42092a4b9c239f6ac0f7f4aefed3eaef6c6`
- `Content/Python/OperationSunscar/AutomationV1/old_town_static_vehicle_builder_v1.py` | 5824 bytes | mtime 2026-08-12T13:06:13 | sha256 `3b3878301fe500c0bea167f11be55673143b9f2ea3f68628ba6fa01f93f388b6`
- `Content/Python/OperationSunscar/AutomationV1/old_town_storage_scrap_audit_v1.py` | 3610 bytes | mtime 2026-08-12T13:06:13 | sha256 `37e7ac8b59184e34ed7de1d0610e96ce5300da86fcfb28d9ebc4b84356310b55`
- `Content/Python/OperationSunscar/AutomationV1/old_town_storage_scrap_builder_v1.py` | 6215 bytes | mtime 2026-08-12T13:06:13 | sha256 `29f4d7d707eb5061e8ab1ca074ccd1a0d670d482039293321c7769dbe4762af1`
- `Content/Python/OperationSunscar/AutomationV1/old_town_structural_material_audit_v1.py` | 2908 bytes | mtime 2026-08-12T13:06:13 | sha256 `a74e017162dbad0b1b234e5c551088a775cde4d116695d9117578ae7783e653a`
- `Content/Python/OperationSunscar/AutomationV1/old_town_structural_material_pass_v1.py` | 5547 bytes | mtime 2026-08-12T13:06:13 | sha256 `cfe0a27f4ba1b13fbe07f5b04cc72251b9572722792d5d6af67266f78308f04d`
- `Content/Python/OperationSunscar/AutomationV1/old_town_ue58_architecture_candidate_audit_v1.py` | 5660 bytes | mtime 2026-08-12T13:06:13 | sha256 `c44352ea445ea0a97fb8106529fcb69ae5e4d7ad855604f4f78040e38614c57b`
- `Content/Python/OperationSunscar/AutomationV1/old_town_ue58_building_conversion_audit_v1.py` | 8293 bytes | mtime 2026-08-12T13:06:13 | sha256 `a53a35fa0740fe2afe3dc115fac812ebea585d8de293c35eda51c0806795e823`
- `Content/Python/OperationSunscar/AutomationV1/old_town_utility_asset_probe_v1.py` | 1935 bytes | mtime 2026-08-12T13:06:13 | sha256 `ca95321c439547eec3a2dcd4433e2ebcb88fde149f639cd65c3f22a736cde87c`
- `Content/Python/OperationSunscar/AutomationV1/old_town_utility_enclosure_audit_v1.py` | 6469 bytes | mtime 2026-08-12T13:06:13 | sha256 `87991e0213fdd94d61ca00bde0b6b548a2b151e24f0a8d80b5b859ea6bd587dd`
- `Content/Python/OperationSunscar/AutomationV1/old_town_utility_enclosure_builder_v1.py` | 8839 bytes | mtime 2026-08-12T13:06:13 | sha256 `a37b19bb5dc9900c7561958d66285999ef019cdb3375328bf5a124d651f7a280`
- `Content/Python/OperationSunscar/AutomationV1/old_town_vehicle_proxy_audit_v1.py` | 2585 bytes | mtime 2026-08-12T13:06:13 | sha256 `fea59a79e436cb3eb88dcec36bbe809ec76b21e9b7dc642a83baa54a304144f3`
- `Content/Python/OperationSunscar/AutomationV1/old_town_verify_landscape_material_v1.py` | 2035 bytes | mtime 2026-08-12T13:06:13 | sha256 `3d82871715e3e5ec73bdccbbad17a9d4659b9e4c283ebb83557a54c0960a182c`
- `Content/Python/OperationSunscar/AutomationV1/old_town_window_opening_audit_v1.py` | 3515 bytes | mtime 2026-08-12T13:06:13 | sha256 `fae0e85b281574228e652fffad16a9c1dea4648bd3e5920828450e402ff0c90b`
- `Content/Python/OperationSunscar/AutomationV1/old_town_window_shutter_audit_v1.py` | 5660 bytes | mtime 2026-08-12T13:06:13 | sha256 `e4adbe4633d320864aa092209dd2b00519f59eac2b074142e7a9a0f82827c4b4`
- `Content/Python/OperationSunscar/AutomationV1/old_town_window_shutter_builder_v1.py` | 7170 bytes | mtime 2026-08-12T13:06:13 | sha256 `55d05b92ae7ae9ec843eaa7018129a8d8568287057b2a2e97c38765a80dfb016`
- `Content/Python/OperationSunscar/AutomationV1/old_town_window_shutter_conflict_fix_v1.py` | 1944 bytes | mtime 2026-08-12T13:06:13 | sha256 `510eebabda60e41b05e12b5a35bcee027da54c9e053e5ab10981798c2c2be159`
- `Content/Python/OperationSunscar/AutomationV1/old_town_world_aligned_facade_prototype_v1.py` | 11562 bytes | mtime 2026-08-12T13:06:13 | sha256 `d7e368526359d252aeccb08fe7d48ede6032811d22bc7789291e412a87536587`
- `Content/Python/OperationSunscar/AutomationV1/old_town_world_aligned_facade_rollout_v1.py` | 7772 bytes | mtime 2026-08-12T13:06:13 | sha256 `7a6fb412cba1e92fbd94e02d52f4665e14e0053026e36dcd3ee04f51d3bce716`
- `Content/Python/OperationSunscar/AutomationV1/old_town_world_aligned_ground_surface_v1.py` | 15270 bytes | mtime 2026-08-12T13:06:13 | sha256 `1bacd281cb93a132bf70a5a1c4bf9a9bced88fd86b351a17b5a919b77567456c`
- `Content/Python/OperationSunscar/AutomationV1/sunscar_automation_common.py` | 5751 bytes | mtime 2026-08-12T13:06:13 | sha256 `7fda3cf7f71ab17a1079770f9c924c43242848b84b623b20f7cda4937cd65ce9`
- `Content/Python/OperationSunscar/build_old_town_artdraft_v1.py` | 7652 bytes | mtime 2026-08-12T13:06:13 | sha256 `279912392b2c174811d8dbfc00b0d09f8b91501d22fd408c4469a67421109451`
- `Content/Python/OperationSunscar/build_old_town_artdraft_v1_remaining.py` | 10060 bytes | mtime 2026-08-12T13:06:13 | sha256 `f18e19e9de32744188a674b3a84c9cb5ee8bf83c8b08f26ea4be0663e3be4240`
- `Content/Python/OperationSunscar/import_downloaded_quixel_library_v1.py` | 5410 bytes | mtime 2026-08-12T13:06:13 | sha256 `350cfa3a1609400576de648fc80d1a225ad98fed55c93bf87566e3962d775119`
- `Content/Python/OperationSunscar/import_quixel_defensive_v1.py` | 1081 bytes | mtime 2026-08-12T13:06:13 | sha256 `db7c8ea6223f65eae30a1920b48e5aa069420f7a886d1ec13512ba5f894e0590`
- `Content/Python/OperationSunscar/import_quixel_sandbag.py` | 563 bytes | mtime 2026-08-12T13:06:13 | sha256 `adc10db67a3692c1e7617f841b75172f0a7b056a7495b3ca64d1b35999f02420`
- `Content/Python/OperationSunscar/import_quixel_surfaces_v1.py` | 1053 bytes | mtime 2026-08-12T13:06:13 | sha256 `f1c39e1a48f0900b9362790dc2594cbfa31983e4eb2e896bc8a79eae480a7fa8`
- `Content/Python/OperationSunscar/old_town_ground_elevation_pass_v2.py` | 10603 bytes | mtime 2026-08-12T13:06:13 | sha256 `370cd1fa22bf21f89824f570a60922d559fe7c908540bba8483c239856ab2c28`
- `Content/Python/OperationSunscar/place_quixel_defensive_v1.py` | 5877 bytes | mtime 2026-08-12T13:06:13 | sha256 `2a135653192fad1f6945957ed9d0346b0eaedb2e68870b6eb63b0940bb7274c4`
- `Content/Python/OperationSunscar/place_quixel_ground_v1.py` | 6677 bytes | mtime 2026-08-12T13:06:13 | sha256 `7a8298a8f9d4b991c9330843897cfc985ed927f75b32a2db3ac21f2e8101a988`
- `Content/Python/OperationSunscar/place_quixel_sandbags_v1.py` | 4564 bytes | mtime 2026-08-12T13:06:13 | sha256 `b2eb5699fc42e5b9a5597dc3e50020929e4dc305c4165cd1d540a52808b49b21`
- `Content/Python/OperationSunscar/place_quixel_surfaces_v1.py` | 3919 bytes | mtime 2026-08-12T13:06:13 | sha256 `e17ae4041066a832bc3e15139676b2f581f831e871bfef5153f01398427d227d`
- `Content/Python/OperationSunscar/repair_downloaded_quixel_materials_v1.py` | 6018 bytes | mtime 2026-08-12T13:06:13 | sha256 `46bfd74b2ef80098ca51a310ab0aab899e285b75a6c8762e8ffe51297895851e`

### Persistent Saved report inventory

- `Saved/OperationSunscar/Reports/abiverd_visual_conversion_preflight_v1.json` | 1938763 bytes | mtime 2026-08-12T16:28:35 | sha256 `f859f1628c90f5a70fa012f61b629178f53d0e87fed6411a32e4a4217902a278`
- `Saved/OperationSunscar/Reports/abiverd_window_material_state_audit_v1.json` | 38382 bytes | mtime 2026-08-14T15:42:16 | sha256 `6b5a92705a0bf4ac12a122d4e7861f65e825a68cac330c105e93804272779242`
- `Saved/OperationSunscar/Reports/abiverd_world_partition_load_diagnostic_v1.json` | 27 bytes | mtime 2026-08-12T20:55:56 | sha256 `c53e9111a25e1bc7a3e3d99467432279ee5267848114b84deb069d59b0f8429d`
- `Saved/OperationSunscar/Reports/abiverd_world_partition_load_region_v1.json` | 39194 bytes | mtime 2026-08-12T20:55:56 | sha256 `84eea710143b842e317d1ff8e3f569678f8f8504912009011b0d6e376b71d928`
- `Saved/OperationSunscar/Reports/old_town_door_proxy_audit_v1.json` | 19991 bytes | mtime 2026-08-12T20:03:55 | sha256 `0de28843e3f5213af61ebae879a36d998a8acd8cedab9f9326262d7ac6972581`
- `Saved/OperationSunscar/Reports/old_town_gameplay_route_audit_v1.json` | 31620 bytes | mtime 2026-08-17T02:46:39 | sha256 `5055e63eb471d969b517cf4e45eca1e3d3a4d2e061e51d271b4345c28174f968`
- `Saved/OperationSunscar/Reports/old_town_ground_overlay_conformance_audit_v1.json` | 178114 bytes | mtime 2026-08-12T16:30:00 | sha256 `09eada09f455c4692ee68044acbe35c302de1725b5377a2a7e50239ec5bca4f1`
- `Saved/OperationSunscar/Reports/old_town_horizontal_surface_audit_v1.json` | 248858 bytes | mtime 2026-08-12T20:03:25 | sha256 `14c2693d12ece3e466821f8101b5b8c3d38d3aee61110b3543305023322a6db5`
- `Saved/OperationSunscar/Reports/old_town_sandbag_audit.csv` | 13458 bytes | mtime 2026-08-12T20:01:52 | sha256 `152aac4f63b16d494f7f683ac655f1f161d7cde1118b11755126e47e6d9862b9`
- `Saved/OperationSunscar/Reports/old_town_sandbag_audit.json` | 34522 bytes | mtime 2026-08-12T20:01:52 | sha256 `9f4ec9969210074b2c75010ab0586f9dcd216699ee5631350e68e336c854b464`
- `Saved/OperationSunscar/Reports/old_town_site_coverage_audit_v1.json` | 52506 bytes | mtime 2026-08-14T15:38:36 | sha256 `7fb541aa0fbb116a3893dbbe302b2c9b2790f125b04328ea94184a6104b412de`
- `Saved/OperationSunscar/Reports/old_town_window_opening_audit_v1.json` | 57202 bytes | mtime 2026-08-12T20:04:24 | sha256 `9fb3fcd23655df7f7b6e92dc6a5f90fd796a9334712cded82b41394a9ea6647c`

### August 17 screenshot inventory

- `/Users/jasonteck/Desktop/Screenshot 2026-08-17 at 8.10.38 AM.png` | 8031241 bytes | mtime 2026-08-17T08:10:44 | sha256 `6a0f6b540a30347f23566b977cd5099c336cb84ac190a668ffd3b66eb55f7695`
- `/Users/jasonteck/Desktop/Screenshot 2026-08-17 at 8.12.11 AM.png` | 7922337 bytes | mtime 2026-08-17T08:12:16 | sha256 `d816304d64dd588dc121ce6748ad8cf5093b1eef2c7c680aa2a3984a1e300400`
- `/Users/jasonteck/Desktop/Screenshot 2026-08-17 at 8.12.49 AM.png` | 7003430 bytes | mtime 2026-08-17T08:12:54 | sha256 `72a3fc2ebeb1b18f57489491a3024f114db2bd1fcb795bd42d193aaab8446498`
- `/Users/jasonteck/Desktop/Screenshot 2026-08-17 at 8.14.00 AM.png` | 3278126 bytes | mtime 2026-08-17T08:14:05 | sha256 `ab384ce9625088fb5ccca0372c74658539999ec2f5e66d0903b63d3aa5c4be87`
- `/Users/jasonteck/Desktop/Screenshot 2026-08-17 at 8.15.04 AM.png` | 6431171 bytes | mtime 2026-08-17T08:15:07 | sha256 `ede838f97c277f67ecc944b5f5a31193bb8aac692b7d54a635bbf55df2846591`
- `/Users/jasonteck/Desktop/Screenshot 2026-08-17 at 8.15.34 AM.png` | 3309530 bytes | mtime 2026-08-17T08:15:40 | sha256 `f984e4d98549518676bbdb900484e0607fd943ed63f1f45f02d4fa73aacb2caa`
- `/Users/jasonteck/Desktop/Screenshot 2026-08-17 at 8.16.12 AM.png` | 7535667 bytes | mtime 2026-08-17T08:16:18 | sha256 `5eb9b9015821b1575e1be49a882137afc6c1b9a9b6238a00aa92223f70a2eb93`
- `/Users/jasonteck/Desktop/Screenshot 2026-08-17 at 8.16.32 AM.png` | 7006042 bytes | mtime 2026-08-17T08:16:38 | sha256 `9f4e10f9774a357a0b968ff8cc71842040c0b2abfc88e1affae39042dba127b1`
- `/Users/jasonteck/Desktop/Screenshot 2026-08-17 at 8.16.57 AM.png` | 8011269 bytes | mtime 2026-08-17T08:17:05 | sha256 `a6075aad1953e8b6e474865397f815bac0f9ff2856b604f0c4c14c73d53fd7ea`
- `/Users/jasonteck/Desktop/Screenshot 2026-08-17 at 8.17.28 AM.png` | 7903486 bytes | mtime 2026-08-17T08:17:34 | sha256 `cb854ae8ae6a32ecf3f72dab0d9b348891dd3e220e1be94b0820d159b20ff083`
- `/Users/jasonteck/Desktop/Screenshot 2026-08-17 at 8.18.32 AM.png` | 7731164 bytes | mtime 2026-08-17T08:18:38 | sha256 `44420df0f36d1e885c7811f6b1a4dee4a0e65d240e0908bf4a9acf3c379f6d47`
- `/Users/jasonteck/Desktop/Screenshot 2026-08-17 at 8.18.44 AM.png` | 8153640 bytes | mtime 2026-08-17T08:18:49 | sha256 `025212e96a3158073adb639d43614651af16010391d064b1649c76078a9fa982`
- `/Users/jasonteck/Desktop/Screenshot 2026-08-17 at 8.19.08 AM.png` | 8044831 bytes | mtime 2026-08-17T08:19:14 | sha256 `14c1b0b0dc9521dd3a614a8288bec92bcb494677b7ce417ad6c2be93225c5956`
- `/Users/jasonteck/Desktop/Screenshot 2026-08-17 at 8.19.49 AM.png` | 7823368 bytes | mtime 2026-08-17T08:19:55 | sha256 `e1443678c3e7bb5a6dac6bbc679a770cdf820cd317d9f7fcf89426316ea34338`
- `/Users/jasonteck/Desktop/Screenshot 2026-08-17 at 8.20.20 AM.png` | 7878696 bytes | mtime 2026-08-17T08:20:25 | sha256 `0891e876a58c492338053338797e0776816e5400ea251b8f9fa1b37b1e32e64e`
- `/Users/jasonteck/Desktop/Screenshot 2026-08-17 at 8.21.34 AM.png` | 7770158 bytes | mtime 2026-08-17T08:21:38 | sha256 `2aeff156986f995ab4b1700577f17cfafa6a325de48469513b2ab49e9130e18f`
- `/Users/jasonteck/Desktop/Screenshot 2026-08-17 at 8.22.29 AM.png` | 7988778 bytes | mtime 2026-08-17T08:22:35 | sha256 `37fa836897a5a545a082dea48618159bfc24fff70d7e31bd21464de96495c7a7`
- `/Users/jasonteck/Desktop/Screenshot 2026-08-17 at 8.23.37 AM.png` | 7478866 bytes | mtime 2026-08-17T08:23:39 | sha256 `b524cad4d1becff25a36c02be3d0538b1ebea513801a499b3d3d4c782b53c508`
- `/Users/jasonteck/Desktop/Screenshot 2026-08-17 at 8.24.11 AM.png` | 7741455 bytes | mtime 2026-08-17T08:24:13 | sha256 `221652cd357aa231fae9a93307808c3b59a325fbe3b80ea1a45e65aabc8eed52`
- `/Users/jasonteck/Desktop/Screenshot 2026-08-17 at 8.26.01 AM.png` | 3764401 bytes | mtime 2026-08-17T08:26:02 | sha256 `b75748e935c6e7856b0cdf546df57ceda350d96008af1667b1852e5799bdbaa5`

### Surviving `/private/tmp/abv_*` evidence

- None present at handoff verification.

At handoff verification, most earlier `/private/tmp/abv_*` evidence had already
been removed by temporary-directory cleanup. Its historical path names remain
embedded in Appendix A. Treat those names as an audit trail, not guaranteed
live files.


## Appendix C — Claude Code phase-one defect register

This is the complete read-only defect register Claude Code produced from the twenty screenshots and saved reports after the initial handoff. It is reproduced verbatim for a single-file handoff.

---

# Abiverd / Old Town — phase-one defect register — 2026-08-18

Author: Claude Code, first session after the Codex handoff.
**No actor, package, material or Git state was modified to produce this
document.** Unreal was closed throughout; every finding below comes from the
20 August 17 screenshots plus read-only analysis of saved reports.

---

## 1. Session verification (read-only, live)

| Check | Expected per handoff | Live result 2026-08-18 |
|---|---|---|
| Branch | `feature/map-development` | `feature/map-development` ✅ |
| Local HEAD | `e0b856c2…` | `e0b856c20cdad11f7057248c851d4d344f43fbe1` ✅ |
| `origin/feature/map-development` | same | identical ✅ |
| Staged files | 0 | 0 ✅ |
| Tracked modified | 927 | 927 ✅ |
| Untracked | 80 (+1 handoff) | 81 ✅ |
| Non-external-actor modified | 7 named files | exactly those 7 ✅ |
| Untracked non-external content | 2 decal materials | exactly those 2 ✅ |
| `git lfs status` | nothing staged | nothing staged ✅ |
| UnrealEditor running | no | no — only Epic Launcher `EpicWebHelper` PIDs and Apple `UnrealEditorServices` |
| TCP 8000 | not listening | not listening ✅ |

Working tree preserved. No stage, commit, push, merge, rebase, checkout,
reset, restore, clean or stash was run.

This register adds one untracked documentation file, taking the status count
from 1,008 to 1,009.

---

## 2. The finding that reframes everything

I ran a read-only mesh census over the 1,785 actors indexed in
`Saved/OperationSunscar/Reports/abiverd_visual_conversion_preflight_v1.json`:

| Mesh | Actor count |
|---|---|
| `/Game/LevelPrototyping/Meshes/SM_Cube` | 590 |
| `/Engine/BasicShapes/Cube` | 552 |
| `/Game/LevelPrototyping/Meshes/SM_ChamferCube` | 61 |
| `/Engine/BasicShapes/Cylinder` | 40 |
| `/Game/LevelPrototyping/Meshes/SM_Cylinder` | 22 |
| `/Engine/BasicShapes/Sphere` | 1 |
| **Total prototype primitives** | **1,231 of 1,785 (69%)** |

**The launch buildings are still blockout geometry.** They are scaled
engine cubes named `Core_<site>_F<n>_<side>_<part>` — every wall is a 40 cm
thick stretched cube, floor by floor, plus cube floors, cube roofs, cube
lintels and cube ramps (227 `Core_*` actors in total).

This is why the earlier audits and the screenshots disagree, and neither is
lying:

- The audits asked *"is any actor using a prototype **material**?"* — answer
  genuinely zero, because the material passes painted map-owned materials
  **onto the prototype cubes**.
- Jason's eyes ask *"does this read as architecture?"* — answer no, because
  the **geometry** was never replaced.

So "shell material replacement complete" and "looks like a blockout" are both
true statements about the same map. Nothing needs to be un-done; the modelling
step simply has not happened yet. I am **not** going to tell you the buildings
are finished.

Two further consequences worth stating plainly:

- The duplicate-geometry audit passed at a 0.1 cm tolerance. The defects
  below are offset by **metres**, so that audit could never have caught them.
- The prototype-material audit swept for `MI_OT_Stucco_WorldAligned`,
  WorldGrid, DefaultMaterial and LevelPrototyping materials. The flat green
  and flat grey surfaces in your screenshots are **`MI_OT_Detention`**, which
  was on neither list, so it was never swept. It is a flat authored colour
  with no texture detail, not a missing material — there are **zero** actors
  with a mesh and no material.

---

## 3. Two systematic authoring bugs behind most of what you photographed

These are not scattered mistakes. They are two bugs, each applied uniformly,
and between them they account for the majority of the floating and
cantilevered geometry in the screenshots.

### Bug A — an obsolete parapet set survives on 8 of 13 sites, each half hanging in mid-air

Every site has a correct modern parapet set, `ABV_<site>_RoofParapet_{North,
South,East,West}`, fitted flush to the roof (measured overhang **0.0 cm**).

Eight sites *also* still carry the older `<site>_Parapet_{N,S,E,W}` set,
sitting exactly **20 cm higher**, and **mis-centred by half its own length**
so that half of every piece cantilevers off the building into open air:

| Site | Obsolete set overhang | Modern `ABV_` set present? |
|---|---|---|
| SS_010 Detention Annex | **1,700 cm** | yes (0.0 cm) |
| SS_007 Municipal Hotel | **1,400 cm** | yes (0.0 cm) |
| SS_005 Old Clinic | **1,200 cm** | yes (0.0 cm) |
| SS_012 Consulate Residence | **1,050 cm** | yes (0.0 cm) |
| SS_018 Telecom Workshop | **1,050 cm** | yes (0.0 cm) |
| SS_011 Checkpoint Office | **1,000 cm** | yes (0.0 cm) |
| SS_003 Canal Pump Station | **900 cm** | **no — no replacement** |
| SS_004 Tea House | **900 cm** | yes (0.0 cm) |

That is **32 obsolete actors**, 28 of which are safely superseded.

This single bug is your screenshot list items 4 and 7: the SS_011 pair
overhangs 10 m, which is the *"very long roof beam extending far beyond the
building"* at the checkpoint; the SS_010 pair overhangs 17 m, which is the
*"large gray wall/beam panels that float or cantilever far beyond plausible
supports"* in the compound.

**Caveat — SS_003 has no replacement parapet.** Deleting or hiding its set
would leave that building with no parapet at all. SS_003 and SS_004 also
received later Codex passes (SS_003 "four visible parapets corrected";
SS_004's four obsolete parapets set to `NoCollision` but **left visually
unchanged**), so their live state may differ from this Aug-12 index. Both
need live re-verification before any change.

### Bug B — the SS_010 detention yard perimeter is built at terrace height but stands over open sand

The six `Core_DetentionYard_F1_*` walls all start at **Z = 34,979.0** and are
250 cm tall. They enclose X −400…4,800 by Y 6,500…10,900 — a 52 m × 44 m
perimeter.

The only foundation under that perimeter is two slabs:

| Slab | X extent | Y extent | Top Z |
|---|---|---|---|
| `Foundation_SS_010_Detention_Terrace` | 2,200 → 5,600 | 9,100 → 11,900 | 35,034.3 |
| `Foundation_SS_010_West_Support` | 500 → 3,900 | 7,700 → 10,500 | 34,984.8 |

Combined coverage is roughly X 500…5,600 by Y 7,700…11,900. Therefore:

- the **entire south wall** (Y ≈ 6,500) sits ~12 m clear of any foundation;
- the **entire west wall** (X ≈ −400) sits ~9 m clear of any foundation;
- the lower east wall (Y 6,500…7,700) is likewise unsupported.

Surrounding grade is ~34,766 (SS_011's ground floor) to 34,794 (SS_015's), so
those wall runs hover roughly **185–215 cm above the sand**. That matches the
screenshots exactly — daylight and hard cast shadows visible underneath, and
the walls reading as a second, duplicate perimeter riding above the finished
textured compound wall.

**Note:** the two foundation slabs are the ones Codex added in the
2026-08-14 pass to close "two previously missed support gaps" on the rear and
east edges. That fix was real but scoped to the *building* terrace; the
*yard* perimeter was never in scope.

### Bug C (smaller) — six buttresses placed at roof height instead of on the ground

| Actor pair | Bottom Z | Site ground | Floating by |
|---|---|---|---|
| `ABV_SS_012_Buttress_NE` / `_SW` | 35,501.5 | 34,769.5 | **+732 cm** |
| `ABV_SS_005_Buttress_NE` / `_SW` | 35,494.9 | 34,762.9 | **+732 cm** |
| `ABV_SS_004_Buttress_NE` / `_SW` | 35,175.7 | 34,763.7 | **+412 cm** |

Each is a 55 × 55 × 220 cm post. They are meant to stand at the wall base and
are instead standing on the roof parapet — one full building height too high.
`ABV_SS_012_Buttress_NE` at XY (12850, 5800) is precisely the "oversized roof
post/chimney" you selected in the 8.23.37 screenshot.

(`ABV_SS021_Buttress_*` — a different, no-underscore naming — sits at Z
34,236–34,271, i.e. *buried*. SS_021 is outside phase one; noted only so it
is not mistaken for a phase-one item.)

---

## 4. Defect register by site

Classification key, per the handoff:
**[R]** verified runtime geometry defect · **[E]** likely editor-only/helper ·
**[O]** outside phase-one playable area · **[I]** needs in-editor inspection

### SS_010 Detention Annex + Detention Yard — worst site
*Screenshots: 8.12.11, 8.12.49, 8.14.00, 8.15.04, 8.15.34, 8.18.32, 8.18.44, 8.19.08, 8.19.49, 8.20.20*

| # | Defect | Class | Evidence |
|---|---|---|---|
| 1 | 6 yard perimeter walls float ~185–215 cm over sand | **R** | Bug B, measured |
| 2 | 4 obsolete parapets cantilever 17 m | **R** | Bug A, measured |
| 3 | Upper storey reads as one flat untextured mint-green plane spanning the whole elevation, overhanging the lower storey and extending past the building end | **R** | `MI_OT_Detention` on `Core_SS_010_F2_*`; 8.14.00 shows it as a single selected actor |
| 4 | Hard seam + dark void between upper and lower storeys; tan strips visible through the gap | **R** | 8.12.49 |
| 5 | Window sills/lintels misaligned — some float in the seam void detached from any window, some offset horizontally from their opening | **R** | 8.12.49, 8 selected slabs |
| 6 | Two cyan strips above the main doorway | **I** | 8.12.11, 8.12.49 — material or a stray actor; identify live |
| 7 | Blank pale panel jutting from the wall right of the lower-right window | **I** | 8.12.11, 8.12.49 |
| 8 | Oversized roof cap slab overhangs and floats above the green plane with a gap | **R** | 8.14.00, 8.15.04 |
| 9 | Grey untextured cubes and small red/green cubes loose in the yard | **R** | 8.18.32, 8.19.08 — prototype cover blocks |
| 10 | `Core_SS_010_UpperRamp` (958 × 280 × 344 cm) overhangs footprint by 1,004 cm | **I** | intended external ramp; verify it lands on something |
| 11 | Yellow polyline crossing the whole scene | **E** | landscape/road spline visualisation |

### SS_011 Checkpoint Office
*Screenshot: 8.24.11*

| # | Defect | Class | Evidence |
|---|---|---|---|
| 12 | "Very long roof beam" extending far past the building = `SS_011_Parapet_N`/`_S`, 10 m overhang | **R** | Bug A, measured |
| 13 | Long detached ramp landing in open sand = `Core_SS_011_UpperRamp`, 958 × 280 × 344 cm, 1,004 cm beyond footprint, from a 300 × 300 × 20 cm landing | **R** | measured; the landing is too small to read as an entrance |
| 14 | Three front pillars that connect to nothing | **R** | 8.24.11 |
| 15 | Long thin tan slab floating at mid-height to the west | **I** | 8.24.11 |

### SS_012 Consulate Residence
*Screenshots: 8.22.29, 8.23.37*

| # | Defect | Class | Evidence |
|---|---|---|---|
| 16 | Two buttresses on the roof, 732 cm too high | **R** | Bug C, measured |
| 17 | 4 obsolete parapets cantilever 10.5 m | **R** | Bug A, measured |
| 18 | Pale-blue upper storey (`MI_OT_WallPaint_WorldAligned`) overhangs the dark lower storey on all sides and projects past the building end | **R** | 8.22.29, 8.23.37 |
| 19 | 16 lintels/sills misaligned — top row embedded in the roof band detached from any window; one row floats between storeys | **R** | 8.22.29, all 16 selected |
| 20 | Two door awnings crooked, at differing heights and angles | **R** | 8.22.29 |
| 21 | Harsh material break between storeys; inconsistent window framing (outer two framed, inner two bare) | **R** | 8.22.29 |
| 22 | Actor pivot far from its geometry on the selected roof post | **R** | 8.23.37 — gizmo well above/left of the mesh |
| 23 | Conspicuous grey-green ground pad rectangle under the building | **R** | `Ground_Earth_SS_012_R*C*`, 4 slabs 1,092 × 936 × 1 cm |

### SS_017 Covered Bazaar
*Screenshots: 8.16.57, 8.17.28*

| # | Defect | Class | Evidence |
|---|---|---|---|
| 24 | Four fabric awnings float flat against the wall, ~1 m above and behind their counters, with **no posts at all** | **R** | 8.17.28 |
| 25 | Counters not aligned with the awnings above them | **R** | 8.16.57, 8.17.28 |
| 26 | Six `Core_SS_017_Stall_*` still on `MI_DefaultColorway` | **I** | preflight; verify live |
| 27 | Long flat roof slab overhangs the whole frontage | **R** | 8.16.57 |
| 28 | Unlit black interior visible through the central doorway | **R** | 8.16.57, 8.17.28 |

*SS_017 is the one site with a clean parapet set (modern only, 0.0 cm).*

### Unidentified phase-one facades — need in-editor ID
*Screenshots: 8.10.38, 8.16.12, 8.16.32, 8.21.34, 8.26.01*

| # | Defect | Class |
|---|---|---|
| 29 | Doorway surround visibly leaning off vertical, oversized for its opening, standing proud of the wall | **R** |
| 30 | Small repeated surround-like trim pieces scattered along the storey seam | **R** |
| 31 | Long tan brick wall floating clear of the ground, cantilevered and tilted | **R** |
| 32 | Grey untextured panel jammed diagonally into a building corner | **R** |
| 33 | ~8 actors with selection outlines but **no visible geometry** — invisible actors that may still carry collision | **I** — highest diagnostic value; matches the known "invisible obsolete parapets retained collision" pattern |
| 34 | Interior almost entirely black — no interior lighting | **R** |
| 35 | Bright light leak along the full ceiling/wall junction, and a second along the floor at the doorway | **R** |
| 36 | Cabinet/panel actor standing **inside** the doorway, blocking it | **R** |
| 37 | Small white plant sprites recurring across many sites | **I** — likely foliage rendering unlit/white; check `M_ABV_Foliage_Masked` instancing usage survived |

### Explicitly out of scope

| # | Item | Class |
|---|---|---|
| 38 | Large field of floating grey slabs, boxes and ribbons on the horizon | **O** — beyond the 13 sites; Codex recorded these as later world-vista/streaming scope |
| 39 | Black catenary arcs with regularly spaced hardware and a lattice tower | **O/I** — read as power-line spans; distant, classify before touching |
| 40 | `ABV_SS021_Buttress_*` buried ~500 cm below grade | **O** — SS_021 not in phase one |

---

## 5. Data provenance and required re-verification

The numeric findings come from
`abiverd_visual_conversion_preflight_v1.json`, dated **2026-08-12**. Codex ran
many mutation passes on 14–17 August after that snapshot. The measurements
are therefore **strong, specific hypotheses — not live truth**.

Before changing anything, each target must be re-read live:

1. Jason manually loads only the required World Partition region in the UI.
   No descriptor/intersection/region-loading scripts — that hang is documented
   and reproducible.
2. Query ≤10 actors at a time, by exact label.
3. Confirm label, transform, bounds, materials, visibility and collision.
4. Confirm authoritative dirty state is zero *before* mutating.

Items most likely to have moved since Aug 12: SS_003 and SS_004 parapets,
SS_005 and SS_018 wall materials, SS_007's upper shell, and anything touched
by the physical-material rebuild you ran on Aug 17/18.

---

## 6. Recommended first correction pass

The handoff's sequencing still holds, and I am not going to run a broad
scripted pass before your visual feedback loop.

**Highest value, lowest risk, in order:**

1. **SS_010 detention yard** — the worst site and the one with the clearest
   mechanical fix. Two bounded jobs: re-ground the six yard walls, and
   resolve the four obsolete parapets. Both are transform/visibility changes,
   not modelling.
2. **SS_011 checkpoint** — the parapet pair and the ramp/landing. Small,
   isolated, and it is the site whose silhouette reads worst on approach.
3. **SS_012 consulate** — drop the two buttresses to grade, resolve the
   parapets, then the storey overhang.
4. **SS_017 bazaar** — awning supports. This one is genuinely additive art
   (stall posts), not a correction, so it is slower.

Bug A is the single best first move: on 7 of the 8 sites a proven-good
replacement parapet already exists, so resolving the obsolete set is a
**hide-or-remove decision, not a modelling decision**, and it removes the most
visually alarming geometry in your screenshots. Per the handoff I will not
delete any actor until runtime-vs-editor status, package ownership and
replacement coverage are each proven, and I will not delete anything without
your explicit approval — hide-with-rollback is the default proposal.

**What I need from you to proceed:**

- The before/after screenshots of your manual corrections, so I can calibrate
  to your intended standard rather than guessing — this is the step the
  handoff asks for and I would rather not skip it.
- Confirmation of which site to open first.
- The editor launched and the region loaded manually, per the stability rules.

**Open question I could not resolve from the files:** whether the phase-one
plan intends the `Core_*` cubes to be replaced with modelled/modular
architecture, or to remain cubes dressed with materials for the beta. That
answer changes whether items 3, 18 and 21 are "fix the transform" or "replace
the geometry", and I did not want to assume. Everything above is written so
that it is useful either way.

---

## Appendix D — Answers to Claude Code's 20 scope, policy, and process questions (2026-08-18)

Evidence labels used below:

- **Documented intent** — stated in committed Operation Sunscar planning/architecture documents.
- **Verified fact** — established from saved packages, audits, screenshots, or live Git state.
- **Inference** — likely interpretation that must be rechecked live before mutation.
- **Decision / recommendation** — production direction unless Jason explicitly changes it.

### A. Scope and design intent

#### 1. The `Core_*` cubes — replaced, or dressed and kept?

**Answer: hybrid. Do not wholesale delete `Core_*`, but exposed raw cubes are not the phase-one beta art target.**

- **Documented intent:** `OLD_TOWN_SPATIAL_ASSET_METHOD.md` assigns existing graybox pieces one of four treatments: **Skin, Cap, Replace, or Dress**. Its Replace method explicitly permits a visible art mesh while the verified graybox collision shell remains hidden.
- **Documented intent:** `OLD_TOWN_UE58_LANDSCAPE_AND_BUILDING_ARCHITECTURE_2026-08-02.md` says the current building art is not production geometry and separates the **gameplay shell** from the **visible art shell**. Gameplay shells stay until replacement art passes traversal/collision validation.
- **Decision:** retain useful cubes as authoritative layout/collision shells. Skin/cap cubes whose massing works; replace visibly crude facade, opening, trim, roof-edge, and structural pieces with imported/map-owned modular art while retaining hidden collision where useful. Do not leave visibly raw Engine cubes on launch-area exteriors merely because their collision works.
- **Practical consequence:** correct a cube now when the fix restores gameplay alignment, closes a seam, or improves a deliberately retained shell. Do not spend detailed composition time polishing visible geometry scheduled for immediate replacement.

#### 2. If replaced — this phase or later?

**Answer: phase-one launch-area exterior conversion is this phase; wholesale hidden/internal shell replacement is later.**

- **Documented intent:** `OLD_TOWN_ART_PRODUCTION_PLAN.md` calls for a complete first art/design draft and says every visible graybox surface must receive an intentional art treatment or be deliberately retained.
- **Decision:** complete visible launch-area facades, openings, rooflines/parapets, exterior supports, ground contacts, and primary exterior props now. Retain hidden/non-visible gameplay shells and restrained non-critical interiors until later.
- Critical interiors—detention entry/objective space, hotel ground floor plus one upper route, tea room, and bazaar passage—need coherent thresholds/readability now, but every interior does not require final art in this pass.

#### 3. Is SS_010 a raised terrace or ground-level compound?

**Answer: treat it as a ground-level compound with localized raised foundation/terrace elements, not an unsupported compound floating about 2 m above terrain.**

- **Verified fact:** six audited detention-yard walls are approximately 185–215 cm above sampled Landscape. Only limited north/west foundations provide support; no continuous terrace carries the whole perimeter.
- **Documented intent:** SS_010 is the Detention Annex/objective site. Its entrances, extraction approach, fortified perimeter, and objective access must remain functional.
- **Inference:** no planning document establishes a full-yard elevated platform. The current geometry reads as terrace-height walls over open sand—a defect.
- **Decision:** re-ground/conform unsupported perimeter walls, or extend a fitted plinth only where a visible raised building/terrace truly requires it. Do not invent a continuous 2 m platform. Verify the live yard floor, gates, ramps, objective path, and player traversal first.

#### 4. Are rooftops playable/traversable in phase one?

**Answer: some are. Preserve every authored roof-access route until individually disproven.**

- **Documented intent:** planning repeatedly preserves roof access, roof positions, traversal, sightlines, and mantle constraints. It separately identifies non-traversal landmark roof positions, implying other roof routes are playable.
- **Verified fact:** repeated `UpperRamp`/landing actors exist, and SS_011 documentation explicitly references its east upper ramp and open route.
- **Decision:** roofs connected by ramps, stairs, landings, ladders, or obvious authored routes are phase-one gameplay space. Preserve collision, usable landings, parapet cover, headroom, and route width. Classify other roofs per site rather than assuming all roofs are playable or decorative.

#### 5. Four identical `UpperRamp` actors — intended or leftover?

**Answer: treat them as intended roof-access scaffolding until live route validation proves otherwise.**

- They occur at SS_007, SS_010, SS_011, and SS_018. Repetition suggests an auto-authored kit, not necessarily obsolescence.
- The prior 50-route audit focused on core ground routes and does not prove these ramps unused. SS_011's east ramp is explicitly documented as an open route.
- Audit each ramp's bottom contact, top landing, slope, headroom, collision, and destination. Retain/dress a working route; minimally correct a misaligned route; hide/remove only an individually proven orphan.

#### 6. Interior lighting — now or deferred?

**Answer: fix geometry-caused light leaks and blocked thresholds now; defer the full lighting pass.**

- Screenshot `8.26.01 AM` shows a doorway-obstructing panel and strong perimeter leaks. Correct misplaced/oversized geometry, wall/ceiling seams, and doorway clearance during building work.
- Defer fixtures, exposure balance, bounce/readability tuning, and comprehensive room lighting to the lighting/atmosphere pass.
- Exception: critical phase-one entrances/playable interiors must not remain unusably black. Provide enough readability to validate traversal without starting a broad redesign.

#### 7. SS_017 stall posts — now or later?

**Answer: necessary structural supports now; decorative stall enrichment later.**

- **Documented intent:** the map-owned kit includes bazaar stalls, canopy planes, poles, and beams. The execution plan expects tarp canopies with simple pole collision and non-colliding canopy fabric.
- Align awning/counter geometry and add only posts/beams needed to make visibly unsupported phase-one awnings plausible and safe. Keep doors and lanes clear. Defer ropes, hanging goods, and secondary storytelling props.

### B. Fix policy

#### 8. Obsolete parapets — hide or delete?

**Answer: hide/tag and disable gameplay effects; do not delete yet.**

- Use a dedicated tag such as `SunscarOldTownObsoleteArchitectureHiddenV1`. Do **not** reuse `SunscarVisualConversionHiddenV2`; that identifies the 288 legacy ground overlays and must remain untouched.
- Set obsolete components hidden as appropriate, `NoCollision`, navigation relevance off, and unnecessary overlaps off. Preserve transforms/materials for rollback.
- Delete only after a checkpoint exists and replacements pass traversal, projectile/collision, navigation, and visual review.

#### 9. SS_003 has no replacement parapets — a, b, or c?

**Answer: choose (c), re-center/correct the existing set, but first verify whether August's correction already solved it.**

- **Verified historical fact:** prior work reports four visible SS_003 parapets corrected and persisted. Claude's older measurement may predate that.
- Live-audit the four exact actors. If aligned, make no change. If still wrong, minimally re-center them while preserving rotation, scale, collision, and roof access.
- Do not hide/delete them because SS_003 lacks replacement coverage. A future `ABV_` art replacement is a separate controlled conversion.

#### 10. Buttresses — drop to grade or remove?

**Answer: drop to grade when architecturally connected; reversibly hide only proven experimental/duplicate pieces.**

- **Verified fact:** six SS_004/005/012 buttresses are approximately 4–7 m too high.
- Buttresses are credible in earthen/mudbrick Abiverd architecture.
- Verify each supports its intended wall, then lower it to roughly 2–8 cm natural terrain embed while preserving rotation, scale, material, and wall alignment. If it has no coherent wall relationship, duplicates another support, or blocks traversal, hide it under the obsolete-architecture policy instead of deleting it.

#### 11. SS_010's flat `MI_OT_Detention` material — intentional?

**Answer: the flat result is unfinished; retain a distinct detention identity but weather it.**

- **Documented intent:** the Soviet civic/detention layer uses squared plaster/brick masses and painted-metal cues, distinct from historic mudbrick.
- Preserve a muted/desaturated institutional green or painted-plaster accent, but replace the giant flat mint field with existing weathered/flaked plaster, masonry, dirt-edge, and trim treatment.
- Do not make the whole structure generic mudbrick and do not create a new shared material until existing map/owned masters and instances are exhausted.

### C. Process and authority

#### 12. Which site first?

**Answer: SS_010 detention yard.**

Bounded order:

1. Read-only live audit of exact SS_010 actors, routes, terrain contacts, materials, collision, and packages.
2. Ground/support correction for the six yard walls.
3. Obsolete parapet handling.
4. Upper-storey shell/overhang, facade, and material cleanup.
5. Ramp/landing correction only after validating its roof route.

Do not mutate all categories in one operation. Capture before/after views and exact dirty scope for every batch.

#### 13. Which site did Jason manually correct; where is the pair?

**Answer: no saved, verified manual before/after pair exists yet.**

- Jason supplied 20 defect screenshots and selected pieces, then requested manual-editing instructions. No corrected screenshot set followed.
- `8.26.01 AM` shows a selected doorway panel; it is defect evidence, not a verified after image.
- Jason later said the one unsaved manual change could be discarded, so it must not be treated as saved calibration.
- Claude may begin SS_010's read-only audit. When Jason completes one representative manual correction, capture the identical before/after angle plus actor names and complete transforms for calibration.

#### 14. Approval granularity?

**Answer: per-site for the first accepted site, then standing approval per proven defect class.**

- For SS_010: audit → propose exact actors/packages/transforms → correct a small batch → show comparison → Jason accepts/redirects.
- After SS_010 establishes the standard, standing approval may cover one defect class across phase-one sites, using batches of no more than six visible actors plus exact collision counterparts.
- Every batch still requires authoritative zero dirty before mutation, exact package-level dirty enumeration, and a stop on config/shared/protected/unexpected packages or mass resaves.
- This is map-editing authority only; it does not authorize stage, commit, push, merge, or rebase.

#### 15. Git checkpoint before mutation?

**Answer: yes, strongly recommended, but Jason must explicitly authorize the commit.**

- **Verified fact:** the branch remains based at `e0b856c20cdad11f7057248c851d4d344f43fbe1`, with 927 tracked modified files, a large intentional untracked map scope, zero staged files, and no recovery commit for accumulated August work.
- Before further map mutation, review the manifest, stage only intended map/docs/art packages, and create one local WIP checkpoint. Suggested message: `checkpoint(map): preserve Abiverd phase-one art draft before Claude corrections`.
- **Authority gate:** Jason must explicitly say **“Approve local checkpoint commit.”** That permits one local commit only—not push, PR, merge, or rebase. Until then, do not stage or commit.

#### 16. Editor operation?

**Answer: confirmed.**

- Launch only `/Users/jasonteck/UnrealEngine/_worktrees/map-development/TacticalMovement.uproject`, detached, and open `/Game/Maps/Blockout/Lvl_Blockout_01`.
- Jason manually loads only the required World Partition region. Scripted descriptor/intersection/selection/region-loading APIs previously pinned Unreal and are prohibited.
- Then use the documented bridge at `127.0.0.1:8000` for exact bounded operations.
- No blind console typing, broad world enumeration, `Save All`, or second Unreal instance.

#### 17. Read-only live verification first?

**Answer: yes; mandatory.**

- Claude's measurements are from August 12; Codex made substantial saved changes August 14–17.
- Reconfirm exact project/map, branch/hash, authoritative dirty packages, actor transforms/bounds/materials/visibility/collision/navigation, and external package paths before proposing a change.
- Use exact labels/tags and no more than about 10 actors per deterministic query. Capture facade-normal, player-height/oblique, and contextual views. Do not act on a stale register entry without re-verification.

### D. Confirm and move on

#### 18. White foliage sprites?

**Answer: log now; classify/fix in the vegetation/material pass after buildings.**

- Compare editor view with Game View/PIE to distinguish helpers/icons from runtime cards.
- If runtime, record exact mesh/material/actor or HISM component. Do not move/delete it during building correction.
- **Known requirement:** `M_ABV_Foliage_Masked` must have **Used with Instanced Static Meshes = true**. Jason enabled/applied this; verify it remains saved before blaming placement or textures.

#### 19. Conspicuous `Ground_Earth_*` pads?

**Answer: retain for now; audit in a dedicated visible-ground/transition pass after building structure.**

- A 1 cm slab may encode a surface route, old overlay, or current visible ground. Filenames/screenshots are insufficient.
- Resolve visibility, hidden tags, collision, material, ownership, and whether Landscape already supplies the surface.
- Visible rectangular borders in the launch area are defects and ultimately need blending/conformance/reshaping/replacement, but do not blanket-delete them or move buildings to conceal them. Leave the 288 hidden legacy overlays untouched.

#### 20. Distant exploded geometry and power-line arcs?

**Answer: out of the current building pass; track as world-vista/streaming cleanup.**

- Do not mutate while correcting phase-one buildings.
- Escalate only if visible from normal playable sightlines, colliding with the playable area, or materially affecting streaming/performance.
- Classify power-line arcs first: intended spline/catenary, stale preview actors, or unloaded-cell artifact. The screenshots alone do not authorize deletion or movement.

### Immediate handoff decision

Claude Code may begin a **read-only exact SS_010 live audit**. Before mutation, the recommended next gate is Jason's explicit approval for a reviewed local checkpoint commit. If Jason declines, preserve exact manifests and avoid destructive/broad operations.
