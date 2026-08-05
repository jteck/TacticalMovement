"""Read-only reflection probe for UE 5.8 Landscape weightmap automation APIs."""

import json
import os

import unreal


def members(value, terms):
    return sorted(
        name for name in dir(value)
        if any(term in name.lower() for term in terms)
    )


actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
landscapes = [
    actor for actor in actor_subsystem.get_all_level_actors()
    if isinstance(actor, unreal.LandscapeProxy)
]
if not landscapes:
    raise RuntimeError("ABIVERD_WEIGHTMAP_PROBE_NO_LANDSCAPE")

classes = {}
for class_name in (
    "LandscapeEditorSubsystem",
    "LandscapeSubsystem",
    "LandscapeProxy",
    "Landscape",
    "LandscapeComponent",
    "LandscapeLayerInfoObject",
    "LandscapeTexturePatch",
    "LandscapePatchComponent",
    "LandscapeWeightPatchTextureInfo",
):
    value = getattr(unreal, class_name, None)
    classes[class_name] = {
        "available": value is not None,
        "members": members(value, ("layer", "weight", "paint", "import", "patch", "texture", "edit")) if value else [],
    }

subsystems = {}
for class_name in ("LandscapeEditorSubsystem", "LandscapeSubsystem"):
    value = getattr(unreal, class_name, None)
    if value is None:
        continue
    try:
        instance = unreal.get_editor_subsystem(value)
    except Exception as exc:
        subsystems[class_name] = {"error": repr(exc)}
        continue
    subsystems[class_name] = {
        "available": instance is not None,
        "members": members(instance, ("layer", "weight", "paint", "import", "patch", "texture", "edit")) if instance else [],
    }

actor_rows = []
for actor in sorted(landscapes, key=lambda item: item.get_actor_label()):
    origin, extent = actor.get_actor_bounds(False)
    components = list(actor.get_components_by_class(unreal.LandscapeComponent))
    actor_rows.append(
        {
            "label": actor.get_actor_label(),
            "class": actor.get_class().get_name(),
            "actor_members": members(actor, ("layer", "weight", "paint", "import", "patch", "texture", "edit")),
            "component_count": len(components),
            "location_cm": list(actor.get_actor_location().to_tuple()),
            "scale": list(actor.get_actor_scale3d().to_tuple()),
            "bounds_origin_cm": list(origin.to_tuple()),
            "bounds_extent_cm": list(extent.to_tuple()),
            "weightmap_import_doc": str(actor.landscape_import_weightmap_from_render_target.__doc__),
        }
    )

parent = next((item for item in landscapes if isinstance(item, unreal.Landscape)), None)
target_layers_result = {}
if parent is not None:
    try:
        target_layers = parent.get_editor_property("target_layers")
        target_layers_result = {
            "readable": True,
            "type": str(type(target_layers)),
            "value": str(target_layers),
        }
    except Exception as exc:
        target_layers_result = {"readable": False, "error": repr(exc)}

registry = unreal.AssetRegistryHelpers.get_asset_registry()
try:
    layer_assets = registry.get_assets_by_class("LandscapeLayerInfoObject", True)
except Exception:
    layer_assets = registry.get_assets_by_class(
        unreal.TopLevelAssetPath("/Script/Landscape", "LandscapeLayerInfoObject"), True
    )

payload = {
    "schema_version": 1,
    "status": "read_only_weightmap_api_probe_complete",
    "classes": classes,
    "subsystems": subsystems,
    "landscapes": actor_rows,
    "target_layers_property": target_layers_result,
    "landscape_layer_info_assets": sorted(str(item.package_name) for item in layer_assets),
    "target_layer_settings_members": members(
        unreal.LandscapeTargetLayerSettings,
        ("layer", "info", "file", "edit", "set", "get"),
    ),
    "unreal_rendering_symbols": sorted(
        name for name in dir(unreal)
        if any(term in name.lower() for term in ("rendering", "render_target", "canvas"))
    ),
    "unreal_landscape_layer_symbols": sorted(
        name for name in dir(unreal)
        if "landscape" in name.lower() and "layer" in name.lower()
    ),
    "rendering_library_docs": {
        name: str(getattr(unreal.RenderingLibrary, name).__doc__)
        for name in (
            "create_render_target2d",
            "begin_draw_canvas_to_render_target",
            "end_draw_canvas_to_render_target",
            "draw_material_to_render_target",
        )
        if hasattr(unreal.RenderingLibrary, name)
    },
    "changes_made": False,
}
path = os.path.join(
    unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports", "abiverd_landscape_weightmap_api_probe_v1.json"
)
with open(path, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2)
    handle.write("\n")
unreal.log("ABIVERD_WEIGHTMAP_API_PROBE landscapes=%d" % len(actor_rows))
print("ABIVERD_WEIGHTMAP_API_PROBE", path)
