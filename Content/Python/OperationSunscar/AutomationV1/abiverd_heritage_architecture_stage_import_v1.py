"""Stage the three approved Abiverd architectural scans without editing the map.

The import is deliberately narrow: one FBX plus BaseColor, Normal, Roughness,
and AO for each scan. Source materials, extra scan maps, and the current level
are not modified. Packages remain unsaved until a separate audit approves them.
"""

import json
import os
from datetime import datetime, timezone

import unreal


EXPECTED_PROJECT = "TacticalMovement"
EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development"
EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
DESTINATION_ROOT = "/Game/Maps/Sunscar/Art/Heritage/Architecture"
REPORT_NAME = "abiverd_heritage_architecture_stage_import_v1.json"

ASSETS = (
    {
        "record_id": "ABV_ASSET_009",
        "name": "Historic Desert Ruin Arch Stone Carved 08",
        "source_root": "/Users/Shared/UnrealEngine/Launcher/VaultCache/FabLibrary/Historic_Desert_Ruin_Arch_Stone_Carved_08-8b6404bf/fbx/high/historic_desert_ruin_arc_extracted",
        "destination": DESTINATION_ROOT + "/ArchStoneCarved08",
        "reference_bounds_m": [1.02, 2.9, 4.3],
    },
    {
        "record_id": "ABV_ASSET_010",
        "name": "Historic Desert Ruin Wall Modular Set 04",
        "source_root": "/Users/Shared/UnrealEngine/Launcher/VaultCache/FabLibrary/Historic_Desert_Ruin_Wall_Modular_Set_04-038f4719/fbx/high/historic_desert_ruin_wal_extracted",
        "destination": DESTINATION_ROOT + "/WallModularSet04",
        "reference_bounds_m": [3.23, 3.26, 0.7],
    },
    {
        "record_id": "ABV_ASSET_011",
        "name": "Historic Desert Ruin Structure Stone S 06",
        "source_root": "/Users/Shared/UnrealEngine/Launcher/VaultCache/FabLibrary/Historic_Desert_Ruin_Structure_Stone_S_06-0db909ab/fbx/high/historic_desert_ruin_str_extracted",
        "destination": DESTINATION_ROOT + "/StructureStoneS06",
        "reference_bounds_m": [0.34, 1.44, 0.4],
    },
)


def current_level_path():
    subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    level = subsystem.get_current_level()
    return level.get_outermost().get_name() if level else ""


def package_name(package):
    try:
        return package.get_name()
    except Exception:
        return str(package)


project_name = os.path.splitext(os.path.basename(unreal.Paths.get_project_file_path()))[0]
project_directory = os.path.abspath(unreal.Paths.project_dir()).replace("\\", "/").rstrip("/")
level_path = current_level_path()
if project_name != EXPECTED_PROJECT:
    raise RuntimeError("ABIVERD_ARCH_IMPORT_WRONG_PROJECT " + project_name)
if not project_directory.endswith(EXPECTED_DIRECTORY_SUFFIX):
    raise RuntimeError("ABIVERD_ARCH_IMPORT_WRONG_DIRECTORY " + project_directory)
if level_path != EXPECTED_LEVEL:
    raise RuntimeError("ABIVERD_ARCH_IMPORT_WRONG_LEVEL " + level_path)

dirty_before = sorted(
    {package_name(package) for package in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()}
    | {package_name(package) for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()}
)
if dirty_before:
    raise RuntimeError("ABIVERD_ARCH_IMPORT_PREEXISTING_DIRTY " + repr(dirty_before))

for asset in ASSETS:
    if not os.path.isdir(asset["source_root"]):
        raise RuntimeError("ABIVERD_ARCH_IMPORT_SOURCE_MISSING " + asset["source_root"])
    if unreal.EditorAssetLibrary.does_directory_exist(asset["destination"]):
        existing = unreal.EditorAssetLibrary.list_assets(asset["destination"], recursive=True)
        if existing:
            raise RuntimeError(
                "ABIVERD_ARCH_IMPORT_DESTINATION_NOT_EMPTY %s %s"
                % (asset["destination"], repr(existing))
            )

asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
results = []
for asset in ASSETS:
    files = sorted(os.listdir(asset["source_root"]))
    selected = []
    for filename in files:
        lower = filename.lower()
        if lower.endswith(".fbx"):
            selected.append(os.path.join(asset["source_root"], filename))
        elif lower.endswith((".jpg", ".jpeg", ".png", ".tif", ".tiff")) and any(
            token in lower for token in ("basecolor", "_normal", "roughness", "_ao")
        ):
            selected.append(os.path.join(asset["source_root"], filename))

    fbx_files = [path for path in selected if path.lower().endswith(".fbx")]
    if len(fbx_files) != 1 or len(selected) != 5:
        raise RuntimeError(
            "ABIVERD_ARCH_IMPORT_SOURCE_SCOPE %s selected=%s" % (asset["record_id"], repr(selected))
        )

    tasks = []
    for source_file in selected:
        task = unreal.AssetImportTask()
        task.filename = source_file
        task.destination_path = asset["destination"]
        task.automated = True
        task.replace_existing = False
        task.save = False
        if source_file.lower().endswith(".fbx"):
            options = unreal.FbxImportUI()
            options.import_as_skeletal = False
            options.import_mesh = True
            options.import_materials = False
            options.import_textures = False
            options.automated_import_should_detect_type = False
            options.mesh_type_to_import = unreal.FBXImportType.FBXIT_STATIC_MESH
            options.static_mesh_import_data.combine_meshes = True
            task.options = options
        tasks.append(task)

    asset_tools.import_asset_tasks(tasks)
    imported = []
    for task in tasks:
        imported.extend(str(path) for path in task.imported_object_paths)
    results.append(
        {
            "record_id": asset["record_id"],
            "name": asset["name"],
            "source_root": asset["source_root"],
            "destination": asset["destination"],
            "reference_bounds_m": asset["reference_bounds_m"],
            "selected_sources": selected,
            "imported_object_paths": sorted(imported),
        }
    )
    unreal.log("ABIVERD_ARCH_IMPORT_ITEM %s imported=%d" % (asset["record_id"], len(imported)))

dirty_after = sorted(
    {package_name(package) for package in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()}
    | {package_name(package) for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()}
)
unexpected_dirty = [name for name in dirty_after if not name.startswith(DESTINATION_ROOT + "/")]
if unexpected_dirty:
    raise RuntimeError("ABIVERD_ARCH_IMPORT_UNEXPECTED_DIRTY " + repr(unexpected_dirty))

report_root = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
os.makedirs(report_root, exist_ok=True)
report_path = os.path.join(report_root, REPORT_NAME)
payload = {
    "schema_version": 1,
    "status": "stage_import_unsaved_complete",
    "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "context": {
        "project": project_name,
        "project_directory": project_directory,
        "level": level_path,
    },
    "destination_root": DESTINATION_ROOT,
    "asset_count": len(results),
    "results": results,
    "dirty_packages_before": dirty_before,
    "dirty_packages_after": dirty_after,
    "unexpected_dirty_packages": unexpected_dirty,
    "level_changed": False,
    "level_saved": False,
    "asset_packages_saved": False,
    "replace_existing": False,
}
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2)
    handle.write("\n")

unreal.log("ABIVERD_ARCH_IMPORT_COMPLETE report=" + report_path)
print("ABIVERD_ARCH_IMPORT_COMPLETE", report_path)
