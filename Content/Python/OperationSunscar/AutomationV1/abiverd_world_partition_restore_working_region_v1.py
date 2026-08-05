"""Unload temporary full-Landscape proxies while preserving the Abiverd working region."""

import json
import os

import unreal


EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development"
KEEP_LABELS = {
    "LandscapeStreamingProxy_1_2_0",
    "LandscapeStreamingProxy_2_2_0",
}
LANDSCAPE_BOX_CM = {
    "min": [-130000.0, -130000.0, -100000.0],
    "max": [130000.0, 130000.0, 100000.0],
}


def package_name(package):
    try:
        return package.get_name()
    except Exception:
        return str(package)


def dirty_packages():
    return sorted(
        {package_name(item) for item in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()}
        | {package_name(item) for item in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()}
    )


project_directory = os.path.abspath(unreal.Paths.project_dir()).replace("\\", "/").rstrip("/")
level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).get_current_level()
level_path = level.get_outermost().get_name() if level else ""
if not project_directory.endswith(EXPECTED_DIRECTORY_SUFFIX) or level_path != EXPECTED_LEVEL:
    raise RuntimeError("ABIVERD_RESTORE_REGION_CONTEXT")
if dirty_packages():
    raise RuntimeError("ABIVERD_RESTORE_REGION_DIRTY_BEFORE")

box = unreal.Box(
    min=unreal.Vector(*LANDSCAPE_BOX_CM["min"]),
    max=unreal.Vector(*LANDSCAPE_BOX_CM["max"]),
)
descriptors = [
    descriptor
    for descriptor in unreal.WorldPartitionBlueprintLibrary.get_intersecting_actor_descs(box)
    if str(descriptor.label).startswith("LandscapeStreamingProxy_")
]
if len(descriptors) != 16:
    raise RuntimeError("ABIVERD_RESTORE_REGION_DESCRIPTOR_COUNT %d" % len(descriptors))

extras = [descriptor for descriptor in descriptors if str(descriptor.label) not in KEEP_LABELS]
if len(extras) != 14:
    raise RuntimeError("ABIVERD_RESTORE_REGION_EXTRA_COUNT %d" % len(extras))
extra_guids = [descriptor.guid for descriptor in extras]
unreal.WorldPartitionBlueprintLibrary.unpin_actors(extra_guids)
unreal.WorldPartitionBlueprintLibrary.unload_actors(extra_guids)

actors = list(unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors())
proxies = sorted(
    [actor for actor in actors if isinstance(actor, unreal.LandscapeStreamingProxy)],
    key=lambda actor: actor.get_actor_label(),
)
component_count = sum(
    len(proxy.get_components_by_class(unreal.LandscapeComponent)) for proxy in proxies
)
if {proxy.get_actor_label() for proxy in proxies} != KEEP_LABELS or component_count != 32:
    raise RuntimeError(
        "ABIVERD_RESTORE_REGION_REGISTRATION proxies=%s components=%d"
        % ("|".join(proxy.get_actor_label() for proxy in proxies), component_count)
    )
if dirty_packages():
    raise RuntimeError("ABIVERD_RESTORE_REGION_DIRTY_AFTER")

payload = {
    "schema_version": 1,
    "status": "abiverd_working_region_restored",
    "level": level_path,
    "unloaded_landscape_proxy_count": len(extras),
    "remaining_landscape_proxy_count": len(proxies),
    "remaining_landscape_component_count": component_count,
    "remaining_landscape_proxies": [proxy.get_actor_label() for proxy in proxies],
    "dirty_packages_after": [],
    "changes_made": False,
}
report_path = os.path.join(
    unreal.Paths.project_saved_dir(),
    "OperationSunscar/Reports/abiverd_world_partition_restore_working_region_v1.json",
)
os.makedirs(os.path.dirname(report_path), exist_ok=True)
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2)
    handle.write("\n")
unreal.log("ABIVERD_RESTORE_REGION_COMPLETE proxies=%d components=%d" % (len(proxies), component_count))
