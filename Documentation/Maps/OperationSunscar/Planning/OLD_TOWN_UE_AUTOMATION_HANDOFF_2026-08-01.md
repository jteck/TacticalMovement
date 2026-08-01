# Old Town UE Automation Handoff — 2026-08-01

## Status

The first offline Unreal automation package is prepared and installed in the
isolated TacticalMovement map-development worktree. It has not been executed
in Unreal. No actor, level or Unreal asset was changed by this package during
offline preparation.

Target context:

- Branch: `feature/map-development`
- Project: `TacticalMovement`
- Required project directory suffix: `/UnrealEngine/_worktrees/map-development/`
- Required level: `/Game/Maps/Blockout/Lvl_Blockout_01`
- Repository package: `Content/Python/OperationSunscar/AutomationV1/`
- Report destination when executed: `Saved/OperationSunscar/Reports/`

## Prepared automation

- `old_town_preflight.py`: read-only verification of the project, worktree,
  level, actors, tags, sandbag inputs and planning files.
- `old_town_sandbag_audit.py`: read-only reporting of sandbag transforms,
  attachment parents, supporting surfaces, Landscape elevations, gaps and
  elevation outliers.
- `old_town_asset_inspector.py`: read-only inspection of asset class, bounds,
  material slots, Nanite state, collision and dependencies for the 121-row
  import queue.
- `old_town_connected_slice_builder.py`: dry-run-first resolver for Municipal
  Hotel, Central Courtyard, Tea House, Covered Bazaar and Detention Annex.
- `sunscar_automation_common.py`: shared exact-context validation, asset-path
  restrictions and report-writing helpers.
- `old_town_automation_config.json`: execution gates and allowed scope.
- `README.md`: safety rules and future execution order.

## Safety state

Verified facts:

- `apply_changes` is `false`.
- The approval token is empty.
- `save_current_level` is `false`.
- Tagged-actor destruction is disabled.
- The package contains no level-save, asset-save, actor-destroy or asset-delete
  API calls.
- Version 1 refuses the wrong project, worktree or level.
- Version 1 never saves its preview actors.
- Architecture, tactical cover, utilities, furniture, decals and specialized
  placements are excluded from automatic spawning.
- Protected movement, weapons, animation, readiness, networking and project
  configuration are outside the allowed asset paths.

Any future apply preview requires both changing `apply_changes` and supplying
the exact configured approval token after separate user approval. That preview
still remains unsaved until a separately authorized Unreal save operation.

## Offline validation result

- All Python files passed syntax compilation.
- Both configuration and asset-registry JSON passed parsing.
- The repository package byte-matched its local planning source at validation.
- No `__pycache__` or `.pyc` files were created in the repository.
- The connected slice contains 718 planned placements across five sites.
- 516 placements remain manual or specialized.
- 202 ground/vegetation scatter placements qualify for automatic preview.
- 155 of those 202 currently resolve directly to project asset paths.
- 47 remain blocked until accepted final `/Game/...` paths are recorded in
  `OldTown_FinalAssetRegistry_v1.json`.

These are offline syntax and data results, not an Unreal execution result.

## Sandbag review defect

`OT-REVIEW-001` records the user-observed sandbags appearing beside a building
at approximately second-floor elevation.

Verified from the earlier placement scripts: they select the first actor whose
label starts with a site ID, derive a base elevation from that actor and a
hard-coded height, do not trace the intended support surface, and immediately
save the level.

Inference: that placement method is a credible cause of the elevated-looking
sandbags. The sandbags' actual transforms, attachments and supporting surfaces
remain unknown until `old_town_sandbag_audit.py` is run in the correct level.
Ground textures or materials cannot correct an actor transform or attachment
error. Do not rerun the older sandbag-placement scripts before this audit.

## Required planning inputs

- `Documentation/Maps/OperationSunscar/Planning/OLD_TOWN_RESOLVED_PLACEMENT_PLAN_V1.csv`
- `Documentation/Maps/OperationSunscar/Planning/OLD_TOWN_UE_IMPORT_QUEUE_V1.csv`
- `Documentation/Maps/OperationSunscar/Planning/OldTown_FinalAssetRegistry_v1.json`
- `Documentation/Maps/OperationSunscar/Planning/OLD_TOWN_ASSET_AUDIT_AND_PLACEMENT_RESOLUTION_2026-08-01.md`

The final registry is deliberately incomplete. Unresolved entries are a safety
blocker, not missing work to bypass automatically.

## Authorized future execution order

1. Confirm no other task is using Unreal and open only the map-development
   TacticalMovement project.
2. Open `/Game/Maps/Blockout/Lvl_Blockout_01`.
3. Run `old_town_preflight.py`.
4. Run `old_town_sandbag_audit.py`.
5. Review the generated reports before authorizing any sandbag correction.
6. Run `old_town_asset_inspector.py` after intended assets are available in
   the project or staging context.
7. Record only reviewed and accepted asset paths in the final registry.
8. Run `old_town_connected_slice_builder.py` with apply mode still disabled.
9. Review blockers and manual/specialized placements.
10. Obtain separate approval before any unsaved apply preview and separate
    approval again before saving the reviewed result.

## Stop conditions

Stop without changes on the wrong project, worktree or level; any module or
version-conversion warning; unexpected dependency expansion; protected-file
changes; whole-sample migration; unexpected mass-resaves; or an attempt to
alter gameplay-critical cover before validation.
