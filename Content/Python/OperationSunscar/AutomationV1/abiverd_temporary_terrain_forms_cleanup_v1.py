"""Clear dirty flags on the three orphaned unsaved component packages."""

import json
import os

import unreal


PASS_TAG = "AbiverdTemporaryTerrainFormsV1"
EXPECTED_COUNT = 3


def package_name(package):
    try:
        return package.get_name()
    except Exception:
        return str(package)


actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
remaining = [
    actor.get_actor_label()
    for actor in actor_subsystem.get_all_level_actors()
    if PASS_TAG in [str(tag) for tag in actor.tags]
]
if remaining:
    raise RuntimeError("ABIVERD_TEMP_TERRAIN_CLEANUP_ACTORS_REMAIN " + "|".join(remaining))

dirty = list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()) + list(
    unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
)
names = sorted(package_name(item) for item in dirty)
if len(dirty) != EXPECTED_COUNT or any(
    not name.startswith("/Game/__ExternalObjects__/Maps/Blockout/Lvl_Blockout_01/") for name in names
):
    raise RuntimeError("ABIVERD_TEMP_TERRAIN_CLEANUP_SCOPE " + "|".join(names))

cleared = []
for package in dirty:
    package.set_dirty_flag(False)
    cleared.append(package_name(package))
unreal.SystemLibrary.collect_garbage()

dirty_after = sorted(
    package_name(item)
    for item in list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
    + list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
)
payload = {
    "schema_version": 1,
    "status": "orphaned_unsaved_component_packages_cleaned",
    "cleared_packages": sorted(cleared),
    "dirty_after": dirty_after,
}
root = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
os.makedirs(root, exist_ok=True)
path = os.path.join(root, "abiverd_temporary_terrain_forms_cleanup_v1.json")
with open(path, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2)
    handle.write("\n")
if dirty_after:
    raise RuntimeError("ABIVERD_TEMP_TERRAIN_CLEANUP_FAILED " + "|".join(dirty_after))
unreal.log("ABIVERD_TEMP_TERRAIN_CLEANUP_PASS packages=%d" % len(cleared))
print("ABIVERD_TEMP_TERRAIN_CLEANUP_PASS", path)
