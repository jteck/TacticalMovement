"""Read-only inspection of the candidate Old Town route materials."""

import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


MATERIAL_PATHS = (
    "/Game/Maps/Sunscar/Art/Materials/Ground/MI_OT_Ground_Asphalt",
    "/Game/Maps/Sunscar/Art/Materials/Ground/MI_OT_Ground_Earth",
    "/Game/Maps/Sunscar/Art/Materials/Ground/MI_OT_Ground_Silt",
    "/Game/Maps/Sunscar/Art/Materials/Ground/MI_OT_Ground_Dust",
    "/Game/Maps/Sunscar/Art/Materials/Ground/MI_OT_Ground_Concrete",
    "/Game/Fab/Megascans/Surfaces/Crushed_Asphalt_Ground_sjyjcbja/Medium/sjyjcbja_tier_2/Materials/MI_sjyjcbja",
)

config = common.load_config()
context = common.require_safe_context(config, write_requested=False)
records = []
for path in MATERIAL_PATHS:
    asset = unreal.EditorAssetLibrary.load_asset(path)
    record = {
        "path": path,
        "loaded": asset is not None,
        "class": asset.get_class().get_name() if asset else "",
    }
    if asset is not None:
        try:
            parent = asset.get_editor_property("parent")
            record["parent"] = parent.get_path_name() if parent else ""
        except Exception as exc:
            record["parent_error"] = str(exc)
        for kind, getter in (
            ("scalar", unreal.MaterialEditingLibrary.get_scalar_parameter_names),
            ("vector", unreal.MaterialEditingLibrary.get_vector_parameter_names),
            ("texture", unreal.MaterialEditingLibrary.get_texture_parameter_names),
        ):
            try:
                record[kind + "_parameters"] = [str(value) for value in getter(asset)]
            except Exception as exc:
                record[kind + "_parameter_error"] = str(exc)
    records.append(record)

payload = {
    "schema_version": 1,
    "status": "read_only_probe_complete",
    "context": context,
    "materials": records,
    "changes_made": False,
}
report = common.write_json_report(config, "old_town_route_material_probe_v1.json", payload)
unreal.log("SUNSCAR_ROUTE_MATERIAL_PROBE materials=%d report=%s" % (len(records), report))
print("SUNSCAR_ROUTE_MATERIAL_PROBE", len(records), report)
