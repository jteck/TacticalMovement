"""Focus the editor viewport above the Abiverd heritage precinct."""

import unreal


unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(
    unreal.Vector(0.0, 19000.0, 15000.0),
    unreal.Rotator(roll=0.0, pitch=-82.0, yaw=-90.0),
)
unreal.log("ABIVERD_FOCUS_AERIAL_REVIEW")
