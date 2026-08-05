"""Focus the editor viewport toward the mosque from the south route."""

import unreal


unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(
    unreal.Vector(1600.0, 14000.0, 35050.0),
    unreal.Rotator(roll=0.0, pitch=-10.0, yaw=90.0),
)
unreal.log("ABIVERD_FOCUS_MOSQUE_REVIEW")
