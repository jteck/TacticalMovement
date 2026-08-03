"""Read-only UE 5.8 Python API probe for Landscape material expression construction."""

import json
import os

import unreal


EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development/"
EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"

project_directory = os.path.abspath(unreal.Paths.project_dir()).replace("\\", "/")
if not project_directory.endswith("/"):
    project_directory += "/"
if not project_directory.endswith(EXPECTED_DIRECTORY_SUFFIX):
    raise RuntimeError("SUNSCAR_UNSAFE_PROJECT_DIRECTORY " + project_directory)

world = unreal.UnrealEditorSubsystem().get_editor_world()
level_path = world.get_path_name().split(":", 1)[0].split(".", 1)[0]
if level_path != EXPECTED_LEVEL:
    raise RuntimeError("SUNSCAR_UNSAFE_LEVEL " + level_path)

classes = [
    "MaterialExpressionLandscapeLayerBlend",
    "MaterialExpressionLandscapeLayerCoords",
    "LandscapeLayerBlendInput",
]
payload = {
    "schema_version": 1,
    "status": "read_only_api_probe_complete",
    "project_directory": project_directory,
    "level": level_path,
    "classes": {},
    "changes_made": False,
}

for class_name in classes:
    value = getattr(unreal, class_name, None)
    row = {"available": value is not None}
    if value is not None:
        row["dir"] = sorted(name for name in dir(value) if not name.startswith("__"))
        try:
            instance = value()
            row["instance_dir"] = sorted(name for name in dir(instance) if not name.startswith("__"))
        except Exception as error:
            row["instance_error"] = str(error)
    payload["classes"][class_name] = row

report_directory = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
os.makedirs(report_directory, exist_ok=True)
report_path = os.path.join(report_directory, "old_town_landscape_v2_api_probe.json")
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2, default=str)
    handle.write("\n")

unreal.log("SUNSCAR_LANDSCAPE_V2_API_PROBE report=%s" % report_path)
print("SUNSCAR_LANDSCAPE_V2_API_PROBE", report_path)
