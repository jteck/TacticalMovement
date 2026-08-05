"""Save only the audited Abiverd Landscape relief proxy packages."""

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
    raise RuntimeError("ABIVERD_TERRAIN_RELIEF_SAVE_CONTEXT")

report_root = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
with open(os.path.join(report_root, IMPORT_REPORT_NAME), "r", encoding="utf-8") as handle:
    import_report = json.load(handle)
expected = sorted(import_report["dirty_landscape_packages"])
dirty = dirty_packages()
actual = sorted(package_name(item) for item in dirty)
if actual != expected or len(actual) != 16:
    raise RuntimeError(
        "ABIVERD_TERRAIN_RELIEF_SAVE_SCOPE expected=%s actual=%s"
        % ("|".join(expected), "|".join(actual))
    )
if not unreal.EditorLoadingAndSavingUtils.save_packages(dirty, True):
    raise RuntimeError("ABIVERD_TERRAIN_RELIEF_SAVE_FAILED")
dirty_after = sorted(package_name(item) for item in dirty_packages())
if dirty_after:
    raise RuntimeError("ABIVERD_TERRAIN_RELIEF_SAVE_DIRTY_AFTER " + "|".join(dirty_after))

payload = {
    "schema_version": 1,
    "status": "terrain_relief_saved",
    "saved_package_count": len(actual),
    "saved_packages": actual,
    "dirty_after": dirty_after,
}
path = os.path.join(report_root, "abiverd_terrain_relief_save_v1.json")
with open(path, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2)
    handle.write("\n")
unreal.log("ABIVERD_TERRAIN_RELIEF_SAVE_PASS packages=%d" % len(actual))
print("ABIVERD_TERRAIN_RELIEF_SAVE_PASS", path)
