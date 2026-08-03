"""Focus the editor at approximate player height for Old Town exterior review."""

import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
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
