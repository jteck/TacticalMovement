# Operation Sunscar UE Automation Preparation

Status: prepared offline; not executed
Target: TacticalMovement `feature/map-development` only
Required level: `/Game/Maps/Blockout/Lvl_Blockout_01`

## Safety posture

Every script verifies the project name, exact worktree suffix and exact level.
The default configuration is read-only:

- `apply_changes` is `false`.
- The approval token is empty.
- Automatic level saving is disabled and explicitly rejected by shared preflight.
- The connected-slice builder never deletes actors in version 1.
- The connected-slice builder never saves the level in version 1.
- Reports go to `Saved/OperationSunscar/Reports`, not Content.

Do not change the execution gate until the user explicitly authorizes the
specific Unreal apply pass after reviewing the dry-run reports.

## Scripts

### `old_town_preflight.py`

Read-only session check. It verifies the project/worktree/level, counts actors
and tags, finds likely sandbags and confirms the planning inputs are present.

### `old_town_sandbag_audit.py`

Read-only audit of every actor whose label, mesh path or known placement tag
indicates a sandbag. It reports:

- World transform and bounds-derived bottom Z.
- Static-mesh path, tags and folder.
- Attachment parent, if any.
- First supporting hit and gap beneath the mesh.
- Landscape elevation beneath the actor.
- Elevated, unsupported, attached and global-Z-outlier flags.

It does not move, attach, delete or save actors.

### `old_town_asset_inspector.py`

Read-only inspection of the 121-row UE import queue. Resolved assets receive
class, bounds, material slots, Nanite, collision and dependency information.
Unresolved source and map-owned references remain blockers until
`OldTown_FinalAssetRegistry_v1.json` maps them to accepted `/Game/...` paths.

### `old_town_connected_slice_builder.py`

Dry-run resolver for Municipal Hotel, Central Courtyard, Tea House, Covered
Bazaar and Detention Annex. Default behavior produces a report only.

Even after the dual apply gate is intentionally enabled, version 1 can spawn
only accepted Static Mesh assets in the configured non-gameplay scatter classes
and policies. Architecture, tactical cover, utilities, furniture, decals and
manual placements remain reported for specialized/manual passes. Preview
actors receive an explicit unreviewed tag and remain unsaved.

## Existing sandbag-script finding

Verified from the current scripts:

- `place_quixel_sandbags_v1.py` and `place_quixel_defensive_v1.py` select the
  first actor whose label begins with a site ID.
- They derive a base Z from that actor and a hard-coded site height.
- They do not trace the intended support surface before placing sandbags.
- They automatically save the current level.

Inference: the second-floor-looking placements may result from selecting an
inappropriate site actor or using an invalid derived datum. The actors may only
look attached; the read-only audit must verify actual attachment parents.

Do not rerun those older placement scripts before the audit.

## Offline validation completed

- All five Python entry points and the shared module pass Python syntax
  compilation without writing bytecode into the repository.
- The repository copies byte-match this offline source package.
- The configuration and final asset-registry JSON parse successfully.
- A mutating-API scan found no level-save, asset-save, actor-destroy or
  asset-delete calls in this package.
- The connected slice contains 718 planned instances across five sites.
- Version 1 classifies 516 instances as manual or specialized work and only
  considers 202 ground/vegetation scatter instances for automatic preview.
- With the deliberately incomplete acceptance registry, 155 automatic
  candidates already resolve to project paths and 47 remain blocked until
  their accepted final `/Game/...` paths are recorded.

These are offline data and syntax checks. None of the scripts has been run in
Unreal, and no actor or asset has been changed by this package.

## Intended future run order

1. Open only the verified map-development TacticalMovement project and level.
2. Run `old_town_preflight.py`.
3. Run `old_town_sandbag_audit.py`.
4. Review the JSON/CSV reports and explicitly approve any correction pass.
5. Run `old_town_asset_inspector.py` in the appropriate staging/project context
   after accepted assets exist at their intended paths.
6. Populate the final asset registry with accepted production paths.
7. Run `old_town_connected_slice_builder.py` in dry-run mode.
8. Review blockers and manual/specialized records.
9. Only after a separate approval, enable the dual apply gate for an unsaved
    preview pass. Review the viewport before any separately authorized save.

## Files required in repository Planning

- `OLD_TOWN_RESOLVED_PLACEMENT_PLAN_V1.csv`
- `OLD_TOWN_UE_IMPORT_QUEUE_V1.csv`
- `OldTown_FinalAssetRegistry_v1.json`

## Explicit exclusions

- No startup-map or config changes.
- No movement, weapon, readiness, animation or protected-asset changes.
- No whole-sample migration.
- No automatic collision replacement.
- No automatic tactical-cover changes.
- No automatic save, commit, push or merge.
