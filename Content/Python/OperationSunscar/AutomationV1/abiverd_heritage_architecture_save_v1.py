"""Save exactly the 18 reviewed Abiverd architecture staging packages."""

import json
import os

import unreal


EXPECTED_PROJECT = "TacticalMovement"
EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development"
EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
ROOT = "/Game/Maps/Sunscar/Art/Heritage/Architecture"
EXPECTED_PACKAGE_COUNT = 18


def current_level_path():
    subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    level = subsystem.get_current_level()
    return level.get_outermost().get_name() if level else ""


project_name = os.path.splitext(os.path.basename(unreal.Paths.get_project_file_path()))[0]
project_directory = os.path.abspath(unreal.Paths.project_dir()).replace("\\", "/").rstrip("/")
level_path = current_level_path()
if project_name != EXPECTED_PROJECT or not project_directory.endswith(EXPECTED_DIRECTORY_SUFFIX):
    raise RuntimeError("ABIVERD_ARCH_SAVE_WRONG_PROJECT")
if level_path != EXPECTED_LEVEL:
    raise RuntimeError("ABIVERD_ARCH_SAVE_WRONG_LEVEL " + level_path)

paths = sorted(unreal.EditorAssetLibrary.list_assets(ROOT, recursive=True, include_folder=False))
assets = [unreal.EditorAssetLibrary.load_asset(path) for path in paths]
if len(assets) != EXPECTED_PACKAGE_COUNT or any(asset is None for asset in assets):
    raise RuntimeError("ABIVERD_ARCH_SAVE_SCOPE expected=18 actual=%d" % len(assets))
packages = [asset.get_package() for asset in assets]
target_names = {package.get_name() for package in packages}
dirty_content = {package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()}
dirty_maps = {package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()}
if dirty_content != target_names or dirty_maps:
    raise RuntimeError(
        "ABIVERD_ARCH_SAVE_DIRTY_SCOPE content=%s maps=%s targets=%s"
        % (repr(sorted(dirty_content)), repr(sorted(dirty_maps)), repr(sorted(target_names)))
    )
if not unreal.EditorLoadingAndSavingUtils.save_packages(packages, True):
    raise RuntimeError("ABIVERD_ARCH_SAVE_FAILED")

remaining = sorted(
    package.get_name()
    for package in (
        list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
        + list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
    )
)
if remaining:
    raise RuntimeError("ABIVERD_ARCH_SAVE_DIRTY_AFTER " + repr(remaining))

report_root = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
os.makedirs(report_root, exist_ok=True)
report_path = os.path.join(report_root, "abiverd_heritage_architecture_save_v1.json")
payload = {
    "schema_version": 1,
    "status": "exact_architecture_packages_saved",
    "context": {"project": project_name, "project_directory": project_directory, "level": level_path},
    "saved_packages": sorted(target_names),
    "dirty_packages_after": remaining,
    "level_saved": False,
}
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2)
    handle.write("\n")
unreal.log("ABIVERD_ARCH_SAVE_COMPLETE packages=%d report=%s" % (len(target_names), report_path))
print("ABIVERD_ARCH_SAVE_COMPLETE", len(target_names), report_path)
