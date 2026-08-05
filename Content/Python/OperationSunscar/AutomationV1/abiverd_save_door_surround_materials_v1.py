"""Save only HISM usage metadata added to the two surround materials."""

import json
import os

import unreal


EXPECTED_PROJECT = "TacticalMovement"
EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development"
EXPECTED_PACKAGES = [
    "/Game/Maps/Sunscar/Art/Heritage/Materials/MI_ABV_CrackedMud_WorldAligned",
    "/Game/Maps/Sunscar/Art/Heritage/Materials/MI_ABV_RuinBrick_WorldAligned",
]
REPORT_NAME = "abiverd_save_door_surround_materials_v1.json"


def package_name(package):
    try:
        return package.get_name()
    except Exception:
        return str(package)


def dirty_packages():
    return sorted(
        {package_name(item) for item in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()}
        | {package_name(item) for item in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()}
    )


project_name = os.path.splitext(os.path.basename(unreal.Paths.get_project_file_path()))[0]
project_directory = os.path.abspath(unreal.Paths.project_dir()).replace("\\", "/").rstrip("/")
if project_name != EXPECTED_PROJECT or not project_directory.endswith(EXPECTED_DIRECTORY_SUFFIX):
    raise RuntimeError("ABIVERD_DOOR_MATERIAL_SAVE_WRONG_PROJECT")

before = dirty_packages()
if before != sorted(EXPECTED_PACKAGES):
    raise RuntimeError("ABIVERD_DOOR_MATERIAL_SAVE_SCOPE " + repr(before))
packages = [
    item
    for item in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()
    if package_name(item) in EXPECTED_PACKAGES
]
if sorted(package_name(item) for item in packages) != sorted(EXPECTED_PACKAGES):
    raise RuntimeError("ABIVERD_DOOR_MATERIAL_SAVE_PACKAGE_RESOLUTION")
if not unreal.EditorLoadingAndSavingUtils.save_packages(packages, True):
    raise RuntimeError("ABIVERD_DOOR_MATERIAL_SAVE_FAILED")
after = dirty_packages()
if after:
    raise RuntimeError("ABIVERD_DOOR_MATERIAL_SAVE_DIRTY_AFTER " + repr(after))

payload = {
    "schema_version": 1,
    "status": "intended_materials_saved",
    "context": {"project": project_name, "project_directory": project_directory},
    "dirty_before": before,
    "saved_packages": sorted(EXPECTED_PACKAGES),
    "dirty_after": after,
}
report_root = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
os.makedirs(report_root, exist_ok=True)
report_path = os.path.join(report_root, REPORT_NAME)
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2)
    handle.write("\n")

unreal.log("ABIVERD_DOOR_MATERIAL_SAVE_COMPLETE " + report_path)
print("ABIVERD_DOOR_MATERIAL_SAVE_COMPLETE", report_path)
