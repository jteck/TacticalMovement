"""Read-only preflight for a fast, reversible Abiverd terrain-relief pass."""

import json
import os

import unreal


EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development"
EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
OLD_TOWN_BOX = unreal.Box(
    min=unreal.Vector(-40000.0, -35000.0, -100000.0),
    max=unreal.Vector(40000.0, 35000.0, 100000.0),
)


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


def selected_members(value, terms):
    return sorted(name for name in dir(value) if any(term in name.lower() for term in terms))


project_directory = os.path.abspath(unreal.Paths.project_dir()).replace("\\", "/").rstrip("/")
level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).get_current_level()
level_path = level.get_outermost().get_name() if level else ""
if not project_directory.endswith(EXPECTED_DIRECTORY_SUFFIX) or level_path != EXPECTED_LEVEL:
    raise RuntimeError("ABIVERD_TERRAIN_RELIEF_PREFLIGHT_CONTEXT")
if dirty_packages():
    raise RuntimeError("ABIVERD_TERRAIN_RELIEF_PREFLIGHT_DIRTY " + "|".join(dirty_packages()))

descriptors = list(unreal.WorldPartitionBlueprintLibrary.get_intersecting_actor_descs(OLD_TOWN_BOX))
unreal.WorldPartitionBlueprintLibrary.load_actors([item.guid for item in descriptors])
actors = list(unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors())
parent = next(
    actor
    for actor in actors
    if isinstance(actor, unreal.Landscape) and actor.get_actor_label() == "Landscape_Sunscar"
)
proxies = sorted(
    [actor for actor in actors if isinstance(actor, unreal.LandscapeStreamingProxy)],
    key=lambda actor: actor.get_actor_label(),
)
floors = sorted(
    [
        actor
        for actor in actors
        if actor.get_actor_label().startswith("Core_SS_")
        and actor.get_actor_label().endswith("_F1_Floor")
    ],
    key=lambda actor: actor.get_actor_label(),
)

floor_records = []
for actor in floors:
    origin, extent = actor.get_actor_bounds(False)
    floor_records.append(
        {
            "label": actor.get_actor_label(),
            "origin_cm": list(origin.to_tuple()),
            "extent_cm": list(extent.to_tuple()),
            "bottom_z_cm": origin.z - extent.z,
            "top_z_cm": origin.z + extent.z,
            "package": actor.get_package().get_name(),
        }
    )

edit_layers = list(parent.get_edit_layers_bp())
payload = {
    "schema_version": 1,
    "status": "terrain_relief_preflight_complete",
    "context": {"project_directory": project_directory, "level": level_path},
    "world_partition": {
        "old_town_descriptor_count": len(descriptors),
        "loaded_actor_count": len(actors),
        "landscape_proxy_count": len(proxies),
        "landscape_component_count": sum(
            len(proxy.get_components_by_class(unreal.LandscapeComponent)) for proxy in proxies
        ),
    },
    "landscape": {
        "path": parent.get_path_name(),
        "location_cm": list(parent.get_actor_location().to_tuple()),
        "scale": list(parent.get_actor_scale3d().to_tuple()),
        "edit_layers": [
            {
                "name": layer.get_name(),
                "display_name": str(layer.get_name_bp()) if hasattr(layer, "get_name_bp") else "",
                "class": layer.get_class().get_name(),
                "members": selected_members(layer, ("name", "guid", "layer", "blend", "alpha")),
            }
            for layer in edit_layers
        ],
        "members": selected_members(
            parent, ("layer", "height", "import", "render", "edit", "create", "add", "delete")
        ),
        "heightmap_import_doc": str(parent.landscape_import_heightmap_from_render_target.__doc__),
    },
    "old_town": {
        "floor_count": len(floor_records),
        "floor_records": floor_records,
        "visual_ground_overlay_count": sum(
            1 for actor in actors if "VisualGroundOverlay" in [str(tag) for tag in actor.tags]
        ),
        "core_route_count": sum(1 for actor in actors if actor.get_actor_label().startswith("CoreRoute_")),
    },
    "available_patch_types": {
        "LandscapePatchComponent": getattr(unreal, "LandscapePatchComponent", None) is not None,
        "LandscapeTexturePatch": getattr(unreal, "LandscapeTexturePatch", None) is not None,
    },
    "dirty_after": dirty_packages(),
    "changes_made": False,
}
if payload["dirty_after"]:
    raise RuntimeError("ABIVERD_TERRAIN_RELIEF_PREFLIGHT_DIRTY_AFTER " + "|".join(payload["dirty_after"]))

report_root = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
os.makedirs(report_root, exist_ok=True)
report_path = os.path.join(report_root, "abiverd_terrain_relief_preflight_v1.json")
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2)
    handle.write("\n")
unreal.log("ABIVERD_TERRAIN_RELIEF_PREFLIGHT_PASS floors=%d" % len(floor_records))
print("ABIVERD_TERRAIN_RELIEF_PREFLIGHT_PASS", report_path)
