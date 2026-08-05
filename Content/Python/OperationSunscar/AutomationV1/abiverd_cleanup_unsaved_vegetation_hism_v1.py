"""Remove only an unsaved failed Abiverd HISM preview actor by exact tag/label."""

import unreal


PASS_TAG = unreal.Name("SunscarAbiverdVegetationHISMV1")
ACTOR_LABEL = "ABV_SS025_PoppyMeadow_HISM"
actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
matches = [
    actor for actor in actor_subsystem.get_all_level_actors()
    if PASS_TAG in list(actor.tags) and actor.get_actor_label() == ACTOR_LABEL
]
if len(matches) > 1:
    raise RuntimeError("ABIVERD_VEGETATION_CLEANUP_REFUSED count=%d" % len(matches))
if matches and not actor_subsystem.destroy_actor(matches[0]):
    raise RuntimeError("ABIVERD_VEGETATION_CLEANUP_FAILED")
unreal.log("ABIVERD_VEGETATION_CLEANUP removed=%d" % len(matches))
