"""Read-only reflection probe for the UE 5.8 LandscapeLayerInfoObject API."""

import json
import os

import unreal


TARGET_PATH = "/Game/Maps/Sunscar/Art/Materials/LandscapeV3/Layers/LI_Meadow_NonWeight"
asset = unreal.EditorAssetLibrary.load_asset(TARGET_PATH)
if not isinstance(asset, unreal.LandscapeLayerInfoObject):
    raise RuntimeError("ABIVERD_LAYERINFO_PROPERTY_PROBE_TARGET")

properties = {}
for name in (
    "layer_name",
    "no_weight_blend",
    "is_blended_layer",
    "b_no_weight_blend",
    "phys_material",
    "hardness",
    "blend_method",
    "blend_group",
):
    try:
        properties[name] = {"readable": True, "value": str(asset.get_editor_property(name))}
    except Exception as exc:
        properties[name] = {"readable": False, "error": repr(exc)}

payload = {
    "schema_version": 1,
    "status": "read_only_layer_info_property_probe_complete",
    "asset": asset.get_path_name(),
    "members": sorted(
        name for name in dir(asset)
        if any(term in name.lower() for term in ("blend", "weight", "layer", "hard", "phys"))
    ),
    "properties": properties,
    "class_doc": str(unreal.LandscapeLayerInfoObject.__doc__),
    "unreal_layer_factory_symbols": sorted(
        name for name in dir(unreal)
        if "landscape" in name.lower() and ("layer" in name.lower() or "factory" in name.lower())
    ),
    "blend_enum_doc": str(unreal.LandscapeTargetLayerBlendMethod.__doc__),
    "dirty_packages": sorted(
        {item.get_name() for item in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()}
        | {item.get_name() for item in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()}
    ),
    "changes_made": False,
}
report_path = os.path.join(
    unreal.Paths.project_saved_dir(),
    "OperationSunscar/Reports/abiverd_landscape_layerinfo_property_probe_v1.json",
)
os.makedirs(os.path.dirname(report_path), exist_ok=True)
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2)
    handle.write("\n")
unreal.log("ABIVERD_LAYERINFO_PROPERTY_PROBE_COMPLETE")
