"""Read-only UE 5.8 probe of Landscape edit-layer/component storage."""

import json
import os

import unreal


actors = list(unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors())
parent = next(
    actor for actor in actors
    if isinstance(actor, unreal.Landscape) and actor.get_actor_label() == "Landscape_Sunscar"
)
proxies = sorted(
    [actor for actor in actors if isinstance(actor, unreal.LandscapeProxy)],
    key=lambda actor: actor.get_actor_label(),
)
components = [
    component
    for proxy in proxies
    for component in proxy.get_components_by_class(unreal.LandscapeComponent)
]
edit_layers = list(parent.get_edit_layers_bp())


def property_probe(value, property_name):
    try:
        result = value.get_editor_property(property_name)
        return {"readable": True, "type": str(type(result)), "value": str(result)}
    except Exception as exc:
        return {"readable": False, "error": repr(exc)}


def selected_members(value, terms):
    return sorted(
        name for name in dir(value)
        if any(term in name.lower() for term in terms)
    )


payload = {
    "schema_version": 1,
    "status": "read_only_edit_layer_probe_complete",
    "parent_members": selected_members(
        parent,
        ("layer", "weight", "target", "import", "edit", "info", "component"),
    ),
    "proxy_members": selected_members(
        proxies[0],
        ("layer", "weight", "target", "import", "edit", "info", "component"),
    ) if proxies else [],
    "component_members": selected_members(
        components[0],
        ("layer", "weight", "target", "import", "edit", "data", "texture", "allocation"),
    ) if components else [],
    "component_properties": {
        property_name: property_probe(components[0], property_name)
        for property_name in (
            "layers_data",
            "obsolete_edit_layer_data",
            "weightmap_layer_allocations",
            "weightmap_textures",
            "section_base_x",
            "section_base_y",
        )
    } if components else {},
    "edit_layers": [
        {
            "name": layer.get_name(),
            "path": layer.get_path_name(),
            "class": layer.get_class().get_name(),
            "members": selected_members(layer, ("layer", "weight", "component", "data", "guid", "name")),
        }
        for layer in edit_layers
    ],
    "dirty_packages": sorted(
        {item.get_name() for item in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()}
        | {item.get_name() for item in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()}
    ),
    "changes_made": False,
}

report_path = os.path.join(
    unreal.Paths.project_saved_dir(),
    "OperationSunscar/Reports/abiverd_landscape_edit_layer_probe_v1.json",
)
os.makedirs(os.path.dirname(report_path), exist_ok=True)
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2)
    handle.write("\n")
unreal.log("ABIVERD_EDIT_LAYER_PROBE_COMPLETE")
