"""Open the verified map and set an Abiverd aerial review camera once."""

import unreal


EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
level = level_subsystem.get_current_level()
level_path = level.get_outermost().get_name() if level else ""
if level_path != EXPECTED_LEVEL:
    if not level_subsystem.load_level(EXPECTED_LEVEL):
        raise RuntimeError("ABIVERD_REVIEW_V2_LOAD_FAILED")

review_box = unreal.Box(
    min=unreal.Vector(-16000.0, -13000.0, -100000.0),
    max=unreal.Vector(16000.0, 24000.0, 100000.0),
)
descriptors = list(unreal.WorldPartitionBlueprintLibrary.get_intersecting_actor_descs(review_box))
unreal.WorldPartitionBlueprintLibrary.load_actors([item.guid for item in descriptors])
unreal.WorldPartitionBlueprintLibrary.pin_actors([item.guid for item in descriptors])

unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(
    unreal.Vector(0.0, 6500.0, 50000.0),
    unreal.Rotator(roll=0.0, pitch=-90.0, yaw=-90.0),
)
unreal.log("ABIVERD_REVIEW_V2_CAMERA_SET_ONE_SHOT")
