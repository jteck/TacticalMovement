"""Read-only aerial camera for the temporary terrain-form preview."""

import unreal


unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(
    unreal.Vector(0.0, 0.0, 85000.0),
    unreal.Rotator(roll=0.0, pitch=-90.0, yaw=-90.0),
)
unreal.log("ABIVERD_TEMP_TERRAIN_REVIEW_CAMERA_SET")
