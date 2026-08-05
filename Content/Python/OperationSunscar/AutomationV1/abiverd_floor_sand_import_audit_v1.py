"""Read-only audit of the newly imported Historic Desert Ruin floor surface."""

import json
import os

import unreal


EXPECTED_PROJECT = "TacticalMovement"
EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development"
EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"


def package_name(package):
    try:
        return package.get_name()
    except Exception:
        return str(package)


project_name = os.path.splitext(os.path.basename(unreal.Paths.get_project_file_path()))[0]
project_directory = os.path.abspath(unreal.Paths.project_dir()).replace("\\", "/").rstrip("/")
level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).get_current_level()
level_path = level.get_outermost().get_name() if level else ""
if project_name != EXPECTED_PROJECT or not project_directory.endswith(EXPECTED_DIRECTORY_SUFFIX):
    raise RuntimeError("ABIVERD_FLOOR_SAND_AUDIT_WRONG_PROJECT")
if level_path != EXPECTED_LEVEL:
    raise RuntimeError("ABIVERD_FLOOR_SAND_AUDIT_WRONG_LEVEL " + level_path)

dirty_content = sorted(
    package_name(package) for package in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()
)
dirty_maps = sorted(
    package_name(package) for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
)

registry = unreal.AssetRegistryHelpers.get_asset_registry()
rows = []
for package in dirty_content:
    assets = list(registry.get_assets_by_package_name(unreal.Name(package), True))
    asset_rows = []
    for data in assets:
        asset = data.get_asset()
        asset_rows.append(
            {
                "asset_name": str(data.asset_name),
                "asset_class": str(data.asset_class_path.asset_name),
                "object_path": asset.get_path_name() if asset else "",
            }
        )
    rows.append({"package": package, "assets": asset_rows})

all_candidates = []
for data in registry.get_all_assets():
    searchable = (str(data.package_name) + " " + str(data.asset_name)).lower()
    if ("sand" in searchable and "coarse" in searchable) or "4efcffc7" in searchable:
        all_candidates.append(
            {
                "package": str(data.package_name),
                "asset_name": str(data.asset_name),
                "asset_class": str(data.asset_class_path.asset_name),
                "object_path": str(data.package_name) + "." + str(data.asset_name),
            }
        )

texture_settings = {}
material_settings = {}
for candidate in all_candidates:
    asset = unreal.EditorAssetLibrary.load_asset(candidate["package"])
    if isinstance(asset, unreal.Texture2D):
        texture_settings[candidate["asset_name"]] = {
            "dimensions": [int(asset.blueprint_get_size_x()), int(asset.blueprint_get_size_y())],
            "max_texture_size": int(asset.get_editor_property("max_texture_size")),
            "srgb": bool(asset.get_editor_property("srgb")),
            "virtual_texture_streaming": bool(asset.get_editor_property("virtual_texture_streaming")),
            "compression_settings": str(asset.get_editor_property("compression_settings")),
        }
    elif isinstance(asset, unreal.MaterialInstanceConstant):
        parent = asset.get_editor_property("parent")
        material_settings = {
            "path": asset.get_path_name(),
            "parent": parent.get_path_name() if parent else "",
        }

report = {
    "schema_version": 1,
    "status": "read_only_import_audit_complete",
    "context": {"project": project_name, "project_directory": project_directory, "level": level_path},
    "dirty_content_packages": dirty_content,
    "dirty_map_packages": dirty_maps,
    "dirty_content_assets": rows,
    "floor_sand_candidates": sorted(all_candidates, key=lambda item: item["package"]),
    "texture_settings": texture_settings,
    "material_settings": material_settings,
    "changes_made": False,
}
report_root = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
os.makedirs(report_root, exist_ok=True)
report_path = os.path.join(report_root, "abiverd_floor_sand_import_audit_v1.json")
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(report, handle, indent=2)
    handle.write("\n")

unreal.log(
    "ABIVERD_FLOOR_SAND_IMPORT_AUDIT dirty_content=%d dirty_maps=%d candidates=%d"
    % (len(dirty_content), len(dirty_maps), len(all_candidates))
)
print("ABIVERD_FLOOR_SAND_IMPORT_AUDIT", report_path)
