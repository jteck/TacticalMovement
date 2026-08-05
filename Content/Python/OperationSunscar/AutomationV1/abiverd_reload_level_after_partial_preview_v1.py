"""Reload only Lvl_Blockout_01 after verifying the dirty scope is orphaned preview objects."""

import unreal


EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
PREFIX = "/Game/__ExternalObjects__/Maps/Blockout/Lvl_Blockout_01/"
dirty = sorted(
    package.get_name()
    for package in list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
    + list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
)
if not dirty or any(not name.startswith(PREFIX) for name in dirty):
    raise RuntimeError("ABIVERD_LEVEL_RELOAD_REFUSED " + "|".join(dirty))
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
if any(
    unreal.Name("SunscarAbiverdVegetationHISMV1") in list(actor.tags)
    for actor in actors
):
    raise RuntimeError("ABIVERD_LEVEL_RELOAD_REFUSED_UNSAVED_VEGETATION_ACTOR_REMAINS")
unreal.log("ABIVERD_LEVEL_RELOAD_DISCARDING " + "|".join(dirty))
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(EXPECTED_LEVEL)
