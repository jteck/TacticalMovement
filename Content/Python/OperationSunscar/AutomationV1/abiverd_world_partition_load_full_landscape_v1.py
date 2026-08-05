"""Temporarily load/pin every Sunscar Landscape proxy for UE 5.8 edit-layer merging."""

import json
import os

import unreal


EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development"
EXPECTED_DIRTY = {
    "/Game/Maps/Sunscar/Art/Materials/LandscapeV3/Layers/LI_Meadow_NonWeight",
    "/Game/Maps/Sunscar/Art/Materials/LandscapeV3/M_OT_Landscape_Abiverd",
    "/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/7/PW/GCKDH3SJ6DMPX8ALJXPIKR",
    "/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/8/GT/L3TLG9CXADXV9PPFBSW6JX",
    "/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/D/PO/W2I3PIR4HKE2ZTVN9LNQ4K",
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
    raise RuntimeError("ABIVERD_FULL_LANDSCAPE_LOAD_CONTEXT")

dirty_before = dirty_packages()
if set(dirty_before) != EXPECTED_DIRTY:
    raise RuntimeError("ABIVERD_FULL_LANDSCAPE_LOAD_DIRTY " + "|".join(dirty_before))

box = unreal.Box(
    min=unreal.Vector(*LANDSCAPE_BOX_CM["min"]),
    max=unreal.Vector(*LANDSCAPE_BOX_CM["max"]),
)
descriptors = list(unreal.WorldPartitionBlueprintLibrary.get_intersecting_actor_descs(box))
landscape_descriptors = [
    descriptor for descriptor in descriptors
    if str(descriptor.label).startswith("LandscapeStreamingProxy_")
]
if len(landscape_descriptors) != 16:
    raise RuntimeError(
        "ABIVERD_FULL_LANDSCAPE_LOAD_DESCRIPTOR_COUNT expected=16 actual=%d"
        % len(landscape_descriptors)
    )

guids = [descriptor.guid for descriptor in landscape_descriptors]
unreal.WorldPartitionBlueprintLibrary.load_actors(guids)
unreal.WorldPartitionBlueprintLibrary.pin_actors(guids)

actors = list(unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors())
proxies = sorted(
    [actor for actor in actors if isinstance(actor, unreal.LandscapeStreamingProxy)],
    key=lambda actor: actor.get_actor_label(),
)
component_count = sum(
    len(proxy.get_components_by_class(unreal.LandscapeComponent)) for proxy in proxies
)
dirty_after = dirty_packages()
if len(proxies) != 16 or component_count != 256:
    raise RuntimeError(
        "ABIVERD_FULL_LANDSCAPE_LOAD_REGISTRATION proxies=%d components=%d"
        % (len(proxies), component_count)
    )
if dirty_after != dirty_before:
    raise RuntimeError("ABIVERD_FULL_LANDSCAPE_LOAD_CREATED_DIRTY " + "|".join(dirty_after))

payload = {
    "schema_version": 1,
    "status": "full_landscape_loaded_and_pinned_for_edit_layer_merge",
    "level": level_path,
    "landscape_box_cm": LANDSCAPE_BOX_CM,
    "intersecting_descriptor_count": len(descriptors),
    "landscape_descriptor_count": len(landscape_descriptors),
    "landscape_proxy_count": len(proxies),
    "landscape_component_count": component_count,
    "landscape_proxies": [proxy.get_actor_label() for proxy in proxies],
    "dirty_packages_before": dirty_before,
    "dirty_packages_after": dirty_after,
    "changes_made": False,
    "actors_pinned_for_editor_session": True,
}
report_path = os.path.join(
    unreal.Paths.project_saved_dir(),
    "OperationSunscar/Reports/abiverd_world_partition_load_full_landscape_v1.json",
)
os.makedirs(os.path.dirname(report_path), exist_ok=True)
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2)
    handle.write("\n")
unreal.log(
    "ABIVERD_FULL_LANDSCAPE_LOAD_COMPLETE proxies=%d components=%d"
    % (len(proxies), component_count)
)
