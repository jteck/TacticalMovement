"""Read-only UE 5.8 probe for Landscape layer-info and mask staging APIs."""

import json
import os

import unreal


EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).get_current_level()
level_path = level.get_outermost().get_name() if level else ""
if level_path != EXPECTED_LEVEL:
    raise RuntimeError("ABIVERD_LAYER_SETUP_PROBE_CONTEXT")

actors = list(unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors())
parents = [actor for actor in actors if isinstance(actor, unreal.Landscape) and actor.get_actor_label() == "Landscape_Sunscar"]
if len(parents) != 1:
    raise RuntimeError("ABIVERD_LAYER_SETUP_PROBE_PARENT")
parent = parents[0]
target_layers = parent.get_editor_property("target_layers")
target_layer_rows = []
for key, value in target_layers.items():
    try:
        info = value.get_editor_property("layer_info_obj")
        info_path = info.get_path_name() if info else ""
    except Exception as exc:
        info_path = "ERROR: " + repr(exc)
    target_layer_rows.append({"key": str(key), "layer_info": info_path})

settings = unreal.LandscapeTargetLayerSettings()
settings_properties = {}
for property_name in (
    "layer_info_obj",
    "layer_info_object",
    "reimport_layer_file_path",
    "source_file_path",
):
    try:
        value = settings.get_editor_property(property_name)
        settings_properties[property_name] = {"readable": True, "value": str(value)}
    except Exception as exc:
        settings_properties[property_name] = {"readable": False, "error": repr(exc)}

symbols = {}
for symbol_name in ("ImageUtils", "TextureFactory", "Texture2D", "AssetImportTask", "MaterialInstanceDynamic"):
    symbol = getattr(unreal, symbol_name, None)
    symbols[symbol_name] = {
        "available": symbol is not None,
        "members": sorted(
            name for name in dir(symbol)
            if any(term in name.lower() for term in ("import", "file", "texture", "create", "load", "render"))
        ) if symbol is not None else [],
    }

payload = {
    "schema_version": 1,
    "status": "read_only_layer_setup_probe_complete",
    "level": level_path,
    "target_layer_names": [str(name) for name in parent.get_target_layer_names()],
    "edit_layers": str(parent.get_edit_layers_bp()),
    "parent_update_members": sorted(
        name for name in dir(parent)
        if any(term in name.lower() for term in ("post_edit", "refresh", "update", "target_layer", "register", "component"))
    ),
    "render_weightmap_doc": str(parent.render_weightmap.__doc__),
    "render_weightmaps_doc": str(parent.render_weightmaps.__doc__),
    "target_layers_type": str(type(target_layers)),
    "target_layers_value": str(target_layers),
    "target_layer_rows": target_layer_rows,
    "target_layers_members": sorted(
        name for name in dir(target_layers)
        if any(term in name.lower() for term in ("item", "set", "update", "key", "value", "add"))
    ),
    "settings_properties": settings_properties,
    "settings_members": sorted(name for name in dir(settings) if "layer" in name.lower() or "file" in name.lower()),
    "rendering_library_members": sorted(
        name for name in dir(unreal.RenderingLibrary)
        if any(term in name.lower() for term in ("texture", "file", "render", "target"))
    ),
    "import_file_as_texture2d_doc": str(unreal.RenderingLibrary.import_file_as_texture2d.__doc__),
    "read_render_target_doc": str(unreal.RenderingLibrary.read_render_target.__doc__),
    "canvas_members": sorted(
        name for name in dir(unreal.Canvas)
        if any(term in name.lower() for term in ("texture", "tile", "draw", "material"))
    ),
    "canvas_docs": {
        name: str(getattr(unreal.Canvas, name).__doc__)
        for name in ("draw_texture", "draw_material", "draw_tile")
        if hasattr(unreal.Canvas, name)
    },
    "symbols": symbols,
    "changes_made": False,
    "dirty_packages": sorted(
        {item.get_name() for item in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()}
        | {item.get_name() for item in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()}
    ),
}

report_path = os.path.join(
    unreal.Paths.project_saved_dir(),
    "OperationSunscar/Reports/abiverd_landscape_layer_setup_probe_v1.json",
)
os.makedirs(os.path.dirname(report_path), exist_ok=True)
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2)
    handle.write("\n")

unreal.log("ABIVERD_LAYER_SETUP_PROBE_COMPLETE report=%s" % report_path)
