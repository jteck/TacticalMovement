"""Discard only the failed unsaved Landscape relief preview packages."""

import json
import os

import unreal


EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development"
EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
IMPORT_REPORT_NAME = "abiverd_terrain_relief_rg16_import_apply_preview_v1.json"


def package_name(package):
    try:
        return package.get_name()
    except Exception:
        return str(package)


def dirty_packages():
    return list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()) + list(
        unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
    )


project_directory = os.path.abspath(unreal.Paths.project_dir()).replace("\\", "/").rstrip("/")
level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).get_current_level()
level_path = level.get_outermost().get_name() if level else ""
if not project_directory.endswith(EXPECTED_DIRECTORY_SUFFIX) or level_path != EXPECTED_LEVEL:
    raise RuntimeError("ABIVERD_TERRAIN_RELIEF_DISCARD_CONTEXT")

report_root = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
with open(os.path.join(report_root, IMPORT_REPORT_NAME), "r", encoding="utf-8") as handle:
    import_report = json.load(handle)

expected_names = sorted(import_report["dirty_landscape_packages"])
dirty_before = dirty_packages()
actual_names = sorted(package_name(item) for item in dirty_before)
if actual_names != expected_names:
    raise RuntimeError(
        "ABIVERD_TERRAIN_RELIEF_DISCARD_SCOPE expected=%s actual=%s"
        % ("|".join(expected_names), "|".join(actual_names))
    )

result, error_message = unreal.EditorLoadingAndSavingUtils.reload_packages(
    dirty_before,
    unreal.ReloadPackagesInteractionMode.ASSUME_POSITIVE,
)
dirty_after = sorted(package_name(item) for item in dirty_packages())
payload = {
    "schema_version": 1,
    "status": "failed_unsaved_terrain_preview_discarded",
    "packages_reloaded": expected_names,
    "reload_result": bool(result),
    "error_message": str(error_message),
    "dirty_after": dirty_after,
}
output_path = os.path.join(report_root, "abiverd_terrain_relief_discard_preview_v1.json")
with open(output_path, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2)
    handle.write("\n")
if not result or dirty_after:
    raise RuntimeError(
        "ABIVERD_TERRAIN_RELIEF_DISCARD_FAILED result=%s dirty=%s error=%s"
        % (result, "|".join(dirty_after), error_message)
    )
unreal.log("ABIVERD_TERRAIN_RELIEF_DISCARD_PASS packages=%d" % len(expected_names))
print("ABIVERD_TERRAIN_RELIEF_DISCARD_PASS", output_path)
