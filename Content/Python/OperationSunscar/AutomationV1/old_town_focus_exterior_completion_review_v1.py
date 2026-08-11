"""Focus the editor at approximate player height for Old Town exterior review."""

import os
import sys

import unreal


# Unreal's in-editor ``py exec(open(...).read())`` path does not define
# ``__file__``.  Resolve this known map-automation directory explicitly so the
# camera-only review helper is safe from both the editor console and Python.
SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(globals().get(
    "__file__",
    "/Users/jasonteck/UnrealEngine/_worktrees/map-development/Content/Python/OperationSunscar/AutomationV1/old_town_focus_exterior_completion_review_v1.py",
)))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


config = common.load_config()
common.require_safe_context(config, write_requested=False)
subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
subsystem.set_level_viewport_camera_info(
    unreal.Vector(-9800.0, -5000.0, 34960.0),
    unreal.Rotator(roll=0.0, pitch=-4.0, yaw=53.0),
)
unreal.log("SUNSCAR_EXTERIOR_COMPLETION_FOCUS player_height")
print("SUNSCAR_EXTERIOR_COMPLETION_FOCUS")
