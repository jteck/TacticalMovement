"""Load only the central Abiverd/Old Town World Partition working region."""

import json
import os

import unreal


EXPECTED_PROJECT = "TacticalMovement"
EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development"
EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
REPORT_NAME = "abiverd_world_partition_load_region_v1.json"

REGION_BOX_CM = {
    "min": [-7000.0, 10000.0, -100000.0],
    "max": [7000.0, 25000.0, 100000.0],
}


def current_level_path():
    subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    level = subsystem.get_current_level()
    return level.get_outermost().get_name() if level else ""


def package_name(package):
    try:
        return package.get_name()
    except Exception:
        return str(package)


def dirty_packages():
    return sorted(
        {package_name(package) for package in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()}
        | {package_name(package) for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()}
    )


project_name = os.path.splitext(os.path.basename(unreal.Paths.get_project_file_path()))[0]
project_directory = os.path.abspath(unreal.Paths.project_dir()).replace("\\", "/").rstrip("/")
level_path = current_level_path()
if project_name != EXPECTED_PROJECT or not project_directory.endswith(EXPECTED_DIRECTORY_SUFFIX):
    raise RuntimeError("ABIVERD_WP_LOAD_WRONG_PROJECT")
if level_path != EXPECTED_LEVEL:
    raise RuntimeError("ABIVERD_WP_LOAD_WRONG_LEVEL " + level_path)

dirty_before = dirty_packages()
if dirty_before:
    raise RuntimeError("ABIVERD_WP_LOAD_DIRTY_SCOPE " + repr(dirty_before))

actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors_before = list(actor_subsystem.get_all_level_actors())
box = unreal.Box(
    min=unreal.Vector(*REGION_BOX_CM["min"]),
    max=unreal.Vector(*REGION_BOX_CM["max"]),
)
descriptors = list(unreal.WorldPartitionBlueprintLibrary.get_intersecting_actor_descs(box))
descriptor_rows = []
guids = []
for descriptor in descriptors:
    guids.append(descriptor.guid)
    descriptor_rows.append(
        {
            "label": str(descriptor.label),
            "name": str(descriptor.name),
            "actor_package": str(descriptor.actor_package),
            "is_spatially_loaded": bool(descriptor.is_spatially_loaded),
        }
    )

unreal.WorldPartitionBlueprintLibrary.load_actors(guids)
unreal.WorldPartitionBlueprintLibrary.pin_actors(guids)

actors_after = list(actor_subsystem.get_all_level_actors())
landscape_proxies = [actor for actor in actors_after if isinstance(actor, unreal.LandscapeStreamingProxy)]
dirty_after = dirty_packages()
if dirty_after:
    raise RuntimeError("ABIVERD_WP_LOAD_CREATED_DIRTY_SCOPE " + repr(dirty_after))

report_root = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
os.makedirs(report_root, exist_ok=True)
report_path = os.path.join(report_root, REPORT_NAME)
payload = {
    "schema_version": 1,
    "status": "region_loaded_and_pinned_for_editor_session",
    "changes_made": False,
    "context": {
        "project": project_name,
        "project_directory": project_directory,
        "level": level_path,
    },
    "region_box_cm": REGION_BOX_CM,
    "descriptor_count": len(descriptors),
    "actors_pinned_for_editor_session": True,
    "descriptors": sorted(descriptor_rows, key=lambda row: row["label"]),
    "actor_count_before": len(actors_before),
    "actor_count_after": len(actors_after),
    "landscape_streaming_proxy_count": len(landscape_proxies),
    "landscape_streaming_proxies": sorted(actor.get_actor_label() for actor in landscape_proxies),
    "dirty_packages_before": dirty_before,
    "dirty_packages_after": dirty_after,
}
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2)
    handle.write("\n")
unreal.log(
    "ABIVERD_WP_LOAD_COMPLETE descriptors=%d actors_before=%d actors_after=%d proxies=%d report=%s"
    % (len(descriptors), len(actors_before), len(actors_after), len(landscape_proxies), report_path)
)
print("ABIVERD_WP_LOAD_COMPLETE", len(descriptors), len(actors_after), len(landscape_proxies), report_path)
