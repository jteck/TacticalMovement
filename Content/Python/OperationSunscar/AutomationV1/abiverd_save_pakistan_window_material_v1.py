"""Save only the Pakistan window material after UE adds HISM usage metadata."""

import json
import os

import unreal


EXPECTED_PROJECT = "TacticalMovement"
EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development"
EXPECTED_PACKAGE = (
    "/Game/Maps/Sunscar/Art/Heritage/Architecture/PakistanWindowModular04/"
    "MI_ABV_PakistanWindowModular04"
)
REPORT_NAME = "abiverd_save_pakistan_window_material_v1.json"


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
    raise RuntimeError("ABIVERD_PAK_WINDOW_MATERIAL_SAVE_WRONG_PROJECT")

before = dirty_packages()
if before != [EXPECTED_PACKAGE]:
    raise RuntimeError("ABIVERD_PAK_WINDOW_MATERIAL_SAVE_SCOPE " + repr(before))
package = next(
    item
    for item in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()
    if package_name(item) == EXPECTED_PACKAGE
)
if not unreal.EditorLoadingAndSavingUtils.save_packages([package], True):
    raise RuntimeError("ABIVERD_PAK_WINDOW_MATERIAL_SAVE_FAILED")
after = dirty_packages()
if after:
    raise RuntimeError("ABIVERD_PAK_WINDOW_MATERIAL_SAVE_DIRTY_AFTER " + repr(after))

payload = {
    "schema_version": 1,
    "status": "intended_material_saved",
    "context": {"project": project_name, "project_directory": project_directory},
    "dirty_before": before,
    "saved_package": EXPECTED_PACKAGE,
    "dirty_after": after,
}
report_root = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
os.makedirs(report_root, exist_ok=True)
report_path = os.path.join(report_root, REPORT_NAME)
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2)
    handle.write("\n")

unreal.log("ABIVERD_PAK_WINDOW_MATERIAL_SAVE_COMPLETE " + report_path)
print("ABIVERD_PAK_WINDOW_MATERIAL_SAVE_COMPLETE", report_path)
