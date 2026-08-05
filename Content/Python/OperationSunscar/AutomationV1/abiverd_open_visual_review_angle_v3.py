"""Open the verified map at an oblique Old Town review camera."""

import unreal


EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
level = level_subsystem.get_current_level()
level_path = level.get_outermost().get_name() if level else ""
if level_path != EXPECTED_LEVEL:
    if not level_subsystem.load_level(EXPECTED_LEVEL):
        raise RuntimeError("ABIVERD_REVIEW_ANGLE_V3_LOAD_FAILED")

review_box = unreal.Box(
    min=unreal.Vector(-16000.0, -13000.0, -100000.0),
    max=unreal.Vector(16000.0, 24000.0, 100000.0),
)
descriptors = list(unreal.WorldPartitionBlueprintLibrary.get_intersecting_actor_descs(review_box))
unreal.WorldPartitionBlueprintLibrary.load_actors([item.guid for item in descriptors])
unreal.WorldPartitionBlueprintLibrary.pin_actors([item.guid for item in descriptors])

# View from the southeast toward the civic center. The camera is close enough
# to judge roof caps, façade breakup, and ground contact while retaining the
# complete playable Old Town footprint in frame.
unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(
    unreal.Vector(17000.0, -17500.0, 54000.0),
    unreal.Rotator(roll=0.0, pitch=-37.9, yaw=134.2),
)
unreal.log("ABIVERD_REVIEW_ANGLE_V3_CAMERA_SET_ONE_SHOT")
