"""Move the editor viewport to a read-only overhead industrial-detail review."""

import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


config = common.load_config()
context = common.require_safe_context(config, write_requested=False)
subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
subsystem.set_level_viewport_camera_info(
    unreal.Vector(7600.0, -9000.0, 38500.0),
    unreal.Rotator(roll=0.0, pitch=-26.0, yaw=90.0),
)
payload = {
    "schema_version": 1,
    "status": "industrial_review_camera_set",
    "context": context,
    "focus": "SS_014 Salvage Yard",
    "camera_location_cm": [7600.0, -9000.0, 38500.0],
    "camera_rotation_deg": {"pitch": -26.0, "yaw": 90.0, "roll": 0.0},
    "changes_made": False,
}
report = common.write_json_report(config, "old_town_focus_industrial_review_v1.json", payload)
unreal.log("SUNSCAR_INDUSTRIAL_REVIEW_CAMERA report=%s" % report)
print("SUNSCAR_INDUSTRIAL_REVIEW_CAMERA", report)
