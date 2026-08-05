"""Discard the unsaved temporary terrain-form preview after visual rejection."""

import json
import os

import unreal


EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development"
EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
PASS_TAG = "AbiverdTemporaryTerrainFormsV1"
EXPECTED_COUNT = 18


def package_name(package):
    try:
        return package.get_name()
    except Exception:
        return str(package)


def dirty_packages():
    return list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()) + list(
        unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
    )


project_directory = os.path.abspath(unreal.Paths.project_dir()).replace("\\", "/").rstrip("/")
level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).get_current_level()
level_path = level.get_outermost().get_name() if level else ""
if not project_directory.endswith(EXPECTED_DIRECTORY_SUFFIX) or level_path != EXPECTED_LEVEL:
    raise RuntimeError("ABIVERD_TEMP_TERRAIN_DISCARD_CONTEXT")

actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
forms = [
    actor
    for actor in actor_subsystem.get_all_level_actors()
    if PASS_TAG in [str(tag) for tag in actor.tags]
]
if len(forms) != EXPECTED_COUNT:
    raise RuntimeError("ABIVERD_TEMP_TERRAIN_DISCARD_SCOPE %d" % len(forms))

for actor in forms:
    if not actor_subsystem.destroy_actor(actor):
        raise RuntimeError("ABIVERD_TEMP_TERRAIN_DESTROY_FAILED")
unreal.SystemLibrary.collect_garbage()

remaining = [
    actor.get_actor_label()
    for actor in actor_subsystem.get_all_level_actors()
    if PASS_TAG in [str(tag) for tag in actor.tags]
]
dirty_after_destroy = dirty_packages()

# These packages were created only for the unsaved preview. Reloading discards
# their transient package state without touching any package that existed before.
reload_result = True
reload_error = ""
if dirty_after_destroy:
    reload_result, reload_error = unreal.EditorLoadingAndSavingUtils.reload_packages(
        dirty_after_destroy,
        unreal.ReloadPackagesInteractionMode.ASSUME_POSITIVE,
    )
unreal.SystemLibrary.collect_garbage()
dirty_after = sorted(package_name(item) for item in dirty_packages())

payload = {
    "schema_version": 1,
    "status": "temporary_terrain_preview_discarded",
    "destroyed_actor_count": len(forms),
    "remaining_tagged_actors": remaining,
    "reload_result": bool(reload_result),
    "reload_error": str(reload_error),
    "dirty_after": dirty_after,
}
root = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
os.makedirs(root, exist_ok=True)
path = os.path.join(root, "abiverd_temporary_terrain_forms_discard_v1.json")
with open(path, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2)
    handle.write("\n")
if remaining or dirty_after:
    raise RuntimeError(
        "ABIVERD_TEMP_TERRAIN_DISCARD_FAILED remaining=%s dirty=%s error=%s"
        % ("|".join(remaining), "|".join(dirty_after), reload_error)
    )
unreal.log("ABIVERD_TEMP_TERRAIN_DISCARD_PASS actors=%d" % len(forms))
print("ABIVERD_TEMP_TERRAIN_DISCARD_PASS", path)
