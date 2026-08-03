"""Read-only bounds/material probe for the resolved medium and large utility meshes."""

import os
import sys

import unreal

SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


ASSET_REFS = (
    "source://FAB_P1A_003/electric_box_ullibjd_high",
    "source://FAB_P1A_004/electrical_cabinet_ujzfde2_high",
)
config = common.load_config()
context = common.require_safe_context(config, write_requested=False)
registry = common.read_json(common.planning_file(config, "final_registry_file"))
records = []
for asset_ref in ASSET_REFS:
    path = common.safe_asset_ref_to_path(asset_ref, registry)
    asset = unreal.EditorAssetLibrary.load_asset(path) if path else None
    if not isinstance(asset, unreal.StaticMesh):
        raise RuntimeError("SUNSCAR_UTILITY_ASSET_PROBE missing_static_mesh path=%s" % path)
    box = asset.get_bounding_box()
    dimensions = box.max - box.min
    records.append({
        "asset_ref": asset_ref,
        "asset_path": path,
        "bounds_min_cm": {"x": box.min.x, "y": box.min.y, "z": box.min.z},
        "bounds_max_cm": {"x": box.max.x, "y": box.max.y, "z": box.max.z},
        "dimensions_cm": {"x": dimensions.x, "y": dimensions.y, "z": dimensions.z},
        "materials": [
            material.material_interface.get_path_name() if material.material_interface else ""
            for material in asset.static_materials
        ],
    })

payload = {
    "schema_version": 1,
    "status": "read_only_complete",
    "context": context,
    "asset_count": len(records),
    "records": records,
    "changes_made": False,
}
report = common.write_json_report(config, "old_town_utility_asset_probe_v1.json", payload)
unreal.log("SUNSCAR_UTILITY_ASSET_PROBE assets=%d report=%s" % (len(records), report))
print("SUNSCAR_UTILITY_ASSET_PROBE", len(records), report)
