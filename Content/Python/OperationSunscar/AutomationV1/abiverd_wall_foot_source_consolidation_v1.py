"""Dry-run-first swap of wall-foot HISMs onto stable map-owned sources.

The initial visual render showed that two shared pack materials auto-dirtied.
This pass changes only the newly created map actor's mesh references and never
saves those shared source packages.
"""

import json
import os

import unreal


APPLY_CHANGES = False
EXPECTED_PROJECT = "TacticalMovement"
EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development"
EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
ACTOR_LABEL = "ABV_OldTown_WallFoot_HISM_V1"
PASS_TAG = unreal.Name("SunscarAbiverdWallFootHISMV1")
RUBBLE_PATH = (
    "/Game/Maps/Sunscar/Art/Quixel/Downloaded/FAB_P1A_012_ydyqbjds/"
    "Military_Trenches_Debris_Patch_Rock_Corner_ydyqbjds_High"
)
GRASS_PATH = (
    "/Game/Maps/Sunscar/Art/Quixel/Downloaded/FAB_P1A_015_tbbqejqr/"
    "Dry_Grass_tbbqejqr_High_tbbqejqr_VarA_LOD0"
)
EXPECTED_AUTO_DIRTY = {
    "/Game/Fab/Megascans/3D/Military_Trenches_Ground_Patch_Rock_S_04_yd0lfcq/Medium/SM_yd0lfcq_tier_2/Materials/MI_yd0lfcq",
    "/Game/MilitaryTrench/Assets/3D/Plants/Urb_Street_Grass_Dry_01/Materials/MI_Urb_Street_Grass_Dry_01_Billboard",
}
SWAPS = {
    "HISM_WallFoot_RockPatch": RUBBLE_PATH,
    "HISM_WallFoot_GrassA": GRASS_PATH,
    "HISM_WallFoot_GrassB": GRASS_PATH,
    "HISM_WallFoot_GrassC": GRASS_PATH,
    "HISM_WallFoot_GrassD": GRASS_PATH,
}
REPORT_NAME = (
    "abiverd_wall_foot_source_consolidation_apply_v1.json"
    if APPLY_CHANGES
    else "abiverd_wall_foot_source_consolidation_dry_run_v1.json"
)


def package_name(package):
    try:
        return package.get_name()
    except Exception:
        return str(package)


def dirty_content_names():
    return sorted(package_name(item) for item in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())


def dirty_map_packages():
    return list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())


def dirty_names():
    return sorted(set(dirty_content_names()) | {package_name(item) for item in dirty_map_packages()})


def asset_path(asset):
    return asset.get_outermost().get_name() if asset else ""


project_name = os.path.splitext(os.path.basename(unreal.Paths.get_project_file_path()))[0]
project_directory = os.path.abspath(unreal.Paths.project_dir()).replace("\\", "/").rstrip("/")
level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).get_current_level()
level_path = level.get_outermost().get_name() if level else ""
if project_name != EXPECTED_PROJECT or not project_directory.endswith(EXPECTED_DIRECTORY_SUFFIX):
    raise RuntimeError("ABIVERD_WALL_FOOT_CONSOLIDATE_WRONG_PROJECT")
if level_path != EXPECTED_LEVEL:
    raise RuntimeError("ABIVERD_WALL_FOOT_CONSOLIDATE_WRONG_LEVEL " + level_path)
before_dirty = set(dirty_names())
if before_dirty != EXPECTED_AUTO_DIRTY:
    raise RuntimeError("ABIVERD_WALL_FOOT_CONSOLIDATE_DIRTY_SCOPE " + repr(sorted(before_dirty)))

actors = list(unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors())
matches = [actor for actor in actors if actor.get_actor_label() == ACTOR_LABEL or PASS_TAG in list(actor.tags)]
if len(matches) != 1:
    raise RuntimeError("ABIVERD_WALL_FOOT_CONSOLIDATE_ACTOR_COUNT %d" % len(matches))
actor = matches[0]
components = list(actor.get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent))
components_by_name = {component.get_name(): component for component in components}
if set(SWAPS) - set(components_by_name):
    raise RuntimeError("ABIVERD_WALL_FOOT_CONSOLIDATE_COMPONENTS " + repr(sorted(components_by_name)))

replacement_assets = {}
for path in (RUBBLE_PATH, GRASS_PATH):
    asset = unreal.EditorAssetLibrary.load_asset(path)
    if not isinstance(asset, unreal.StaticMesh):
        raise RuntimeError("ABIVERD_WALL_FOOT_CONSOLIDATE_MISSING " + path)
    replacement_assets[path] = asset

rows = []
for name, target_path in sorted(SWAPS.items()):
    component = components_by_name[name]
    rows.append(
        {
            "component": name,
            "instances": component.get_instance_count(),
            "source_mesh": asset_path(component.get_editor_property("static_mesh")),
            "target_mesh": target_path,
        }
    )

saved_packages = []
if APPLY_CHANGES:
    actor.modify()
    for name, target_path in sorted(SWAPS.items()):
        component = components_by_name[name]
        component.modify()
        component.set_static_mesh(replacement_assets[target_path])
    target_packages = dirty_map_packages()
    target_names = sorted(package_name(item) for item in target_packages)
    unexpected_map = [
        name
        for name in target_names
        if not name.startswith(
            (
                "/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/",
                "/Game/__ExternalObjects__/Maps/Blockout/Lvl_Blockout_01/",
            )
        )
    ]
    if unexpected_map:
        raise RuntimeError("ABIVERD_WALL_FOOT_CONSOLIDATE_UNEXPECTED_MAP " + repr(unexpected_map))
    if not target_packages:
        raise RuntimeError("ABIVERD_WALL_FOOT_CONSOLIDATE_NO_MAP_DIRTY")
    saved_packages = target_names
    if not unreal.EditorLoadingAndSavingUtils.save_packages(target_packages, True):
        raise RuntimeError("ABIVERD_WALL_FOOT_CONSOLIDATE_SAVE_FAILED")
    remaining = set(dirty_names())
    if remaining != EXPECTED_AUTO_DIRTY:
        raise RuntimeError("ABIVERD_WALL_FOOT_CONSOLIDATE_AFTER_SCOPE " + repr(sorted(remaining)))

report = {
    "schema_version": 1,
    "status": "applied_map_actor_only" if APPLY_CHANGES else "dry_run_complete",
    "context": {"project": project_name, "project_directory": project_directory, "level": level_path},
    "actor": ACTOR_LABEL,
    "rows": rows,
    "saved_packages": saved_packages,
    "explicitly_not_saved": sorted(EXPECTED_AUTO_DIRTY),
    "dirty_after": dirty_names(),
}
report_root = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
os.makedirs(report_root, exist_ok=True)
report_path = os.path.join(report_root, REPORT_NAME)
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(report, handle, indent=2)
    handle.write("\n")
unreal.log("ABIVERD_WALL_FOOT_CONSOLIDATE_COMPLETE apply=%s swaps=5" % APPLY_CHANGES)
print("ABIVERD_WALL_FOOT_CONSOLIDATE_COMPLETE", report_path)
