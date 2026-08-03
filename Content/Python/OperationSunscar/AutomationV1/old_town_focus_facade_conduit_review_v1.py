"""Move the editor viewport to a read-only SS_004 conduit review angle."""

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
    unreal.Vector(-9000.0, -8500.0, 36500.0),
    unreal.Rotator(roll=0.0, pitch=-18.0, yaw=90.0),
)
payload = {
    "schema_version": 1,
    "status": "facade_conduit_review_camera_set",
    "context": context,
    "focus": "SS_004 south facade",
    "camera_location_cm": [-9000.0, -8500.0, 36500.0],
    "camera_rotation_deg": {"pitch": -18.0, "yaw": 90.0, "roll": 0.0},
    "changes_made": False,
}
report = common.write_json_report(config, "old_town_focus_facade_conduit_review_v1.json", payload)
unreal.log("SUNSCAR_FACADE_CONDUIT_REVIEW_CAMERA report=%s" % report)
print("SUNSCAR_FACADE_CONDUIT_REVIEW_CAMERA", report)
