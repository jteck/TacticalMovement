"""Move the editor viewport to a read-only SS_017 tarp-canopy review."""

import json
import os

import unreal


EXPECTED_PROJECT = "TacticalMovement"
EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development"
EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"

project_name = os.path.splitext(os.path.basename(unreal.Paths.get_project_file_path()))[0]
project_directory = os.path.abspath(unreal.Paths.project_dir()).replace("\\", "/").rstrip("/")
level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).get_current_level()
level_path = level.get_outermost().get_name() if level else ""
if project_name != EXPECTED_PROJECT or not project_directory.endswith(EXPECTED_DIRECTORY_SUFFIX):
    raise RuntimeError("ABIVERD_BAZAAR_REVIEW_WRONG_PROJECT")
if level_path != EXPECTED_LEVEL:
    raise RuntimeError("ABIVERD_BAZAAR_REVIEW_WRONG_LEVEL " + level_path)

camera_location = unreal.Vector(0.0, -11000.0, 35320.0)
camera_rotation = unreal.Rotator(roll=0.0, pitch=-5.0, yaw=31.0)
unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(
    camera_location, camera_rotation
)

report = {
    "schema_version": 1,
    "status": "bazaar_tarp_review_camera_set",
    "context": {"project": project_name, "project_directory": project_directory, "level": level_path},
    "focus": "SS_017 central passage and north/south Quixel tarp rows",
    "camera_location_cm": [camera_location.x, camera_location.y, camera_location.z],
    "camera_rotation_deg": {"pitch": camera_rotation.pitch, "yaw": camera_rotation.yaw, "roll": camera_rotation.roll},
    "changes_made": False,
}
report_root = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
os.makedirs(report_root, exist_ok=True)
report_path = os.path.join(report_root, "abiverd_focus_bazaar_tarp_review_v1.json")
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(report, handle, indent=2)
    handle.write("\n")
unreal.log("ABIVERD_BAZAAR_TARP_REVIEW_CAMERA_SET")
print("ABIVERD_BAZAAR_TARP_REVIEW_CAMERA_SET", report_path)
