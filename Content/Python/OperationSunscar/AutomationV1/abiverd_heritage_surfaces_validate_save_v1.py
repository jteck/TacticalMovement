"""Validate and save exactly the 20 approved Abiverd surface textures."""

import json
import os

import unreal


EXPECTED_PROJECT = "TacticalMovement"
EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development"
EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
ROOT = "/Game/Maps/Sunscar/Art/Heritage/Surfaces"
EXPECTED_COUNT = 20


def current_level_path():
    subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    level = subsystem.get_current_level()
    return level.get_outermost().get_name() if level else ""


project_name = os.path.splitext(os.path.basename(unreal.Paths.get_project_file_path()))[0]
project_directory = os.path.abspath(unreal.Paths.project_dir()).replace("\\", "/").rstrip("/")
level_path = current_level_path()
if project_name != EXPECTED_PROJECT or not project_directory.endswith(EXPECTED_DIRECTORY_SUFFIX):
    raise RuntimeError("ABIVERD_SURFACE_SAVE_WRONG_PROJECT")
if level_path != EXPECTED_LEVEL:
    raise RuntimeError("ABIVERD_SURFACE_SAVE_WRONG_LEVEL " + level_path)

paths = sorted(unreal.EditorAssetLibrary.list_assets(ROOT, recursive=True, include_folder=False))
assets = [unreal.EditorAssetLibrary.load_asset(path) for path in paths]
if len(assets) != EXPECTED_COUNT or any(not isinstance(asset, unreal.Texture2D) for asset in assets):
    raise RuntimeError("ABIVERD_SURFACE_SAVE_SCOPE expected=20 actual=%d" % len(assets))

records = []
for asset in assets:
    name = asset.get_name().lower()
    if "basecolor" in name:
        role = "BaseColor"
        expected_srgb = True
        expected_compression = "<TextureCompressionSettings.TC_DEFAULT: 0>"
    elif "_normal" in name:
        role = "Normal"
        expected_srgb = False
        expected_compression = "<TextureCompressionSettings.TC_NORMALMAP: 1>"
    elif "roughness" in name:
        role = "Roughness"
        expected_srgb = False
        expected_compression = "<TextureCompressionSettings.TC_MASKS: 2>"
    elif "_ao" in name:
        role = "AO"
        expected_srgb = False
        expected_compression = "<TextureCompressionSettings.TC_MASKS: 2>"
    else:
        raise RuntimeError("ABIVERD_SURFACE_SAVE_ROLE_UNKNOWN " + asset.get_path_name())
    size_x = int(asset.blueprint_get_size_x())
    size_y = int(asset.blueprint_get_size_y())
    srgb = bool(asset.get_editor_property("srgb"))
    compression = asset.get_editor_property("compression_settings")
    valid_dimensions = (size_x, size_y) in {(4096, 4096), (4096, 2048)}
    if not valid_dimensions or srgb != expected_srgb or str(compression) != expected_compression:
        raise RuntimeError(
            "ABIVERD_SURFACE_SAVE_VALIDATION_FAILED %s size=%dx%d srgb=%s compression=%s"
            % (asset.get_path_name(), size_x, size_y, srgb, str(compression))
        )
    records.append(
        {
            "path": asset.get_path_name(),
            "role": role,
            "size": [size_x, size_y],
            "srgb": srgb,
            "compression": str(compression),
            "virtual_texture_streaming": bool(asset.get_editor_property("virtual_texture_streaming")),
        }
    )

packages = [asset.get_package() for asset in assets]
target_names = {package.get_name() for package in packages}
dirty_content = {package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()}
dirty_maps = {package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()}
if dirty_content != target_names or dirty_maps:
    raise RuntimeError(
        "ABIVERD_SURFACE_SAVE_DIRTY_SCOPE content=%s maps=%s targets=%s"
        % (repr(sorted(dirty_content)), repr(sorted(dirty_maps)), repr(sorted(target_names)))
    )
preflight_root = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
os.makedirs(preflight_root, exist_ok=True)
preflight_path = os.path.join(preflight_root, "abiverd_heritage_surfaces_validate_save_preflight_v1.json")
with open(preflight_path, "w", encoding="utf-8") as handle:
    json.dump(
        {
            "status": "save_preflight_passed",
            "asset_count": len(records),
            "dirty_content": sorted(dirty_content),
            "dirty_maps": sorted(dirty_maps),
            "target_packages": sorted(target_names),
        },
        handle,
        indent=2,
    )
    handle.write("\n")
if not unreal.EditorLoadingAndSavingUtils.save_packages(packages, True):
    raise RuntimeError("ABIVERD_SURFACE_SAVE_FAILED")
remaining = sorted(
    package.get_name()
    for package in (
        list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
        + list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
    )
)
if remaining:
    raise RuntimeError("ABIVERD_SURFACE_SAVE_DIRTY_AFTER " + repr(remaining))

report_root = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
os.makedirs(report_root, exist_ok=True)
report_path = os.path.join(report_root, "abiverd_heritage_surfaces_validate_save_v1.json")
payload = {
    "schema_version": 1,
    "status": "validated_and_saved",
    "context": {"project": project_name, "project_directory": project_directory, "level": level_path},
    "asset_count": len(records),
    "records": records,
    "saved_packages": sorted(target_names),
    "dirty_packages_after": remaining,
    "level_saved": False,
}
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2)
    handle.write("\n")
unreal.log("ABIVERD_SURFACE_SAVE_COMPLETE assets=%d report=%s" % (len(records), report_path))
print("ABIVERD_SURFACE_SAVE_COMPLETE", len(records), report_path)
