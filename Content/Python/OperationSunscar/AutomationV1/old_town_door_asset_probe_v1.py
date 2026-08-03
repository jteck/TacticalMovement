"""Read-only bounds and material probe for the resolved Quixel Old Wooden Door mesh."""

import os
import sys

import unreal

SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


ASSET_REF = "source://FAB_P1B_001/old_wooden_door_wbmgdcpdw_high"
config = common.load_config()
context = common.require_safe_context(config, write_requested=False)
registry = common.read_json(common.planning_file(config, "final_registry_file"))
path = common.safe_asset_ref_to_path(ASSET_REF, registry)
asset = unreal.EditorAssetLibrary.load_asset(path) if path else None
if not isinstance(asset, unreal.StaticMesh):
    raise RuntimeError("SUNSCAR_DOOR_ASSET_PROBE missing_static_mesh path=%s" % path)
box = asset.get_bounding_box()
dimensions = box.max - box.min
materials = []
for index, material in enumerate(asset.static_materials):
    interface = material.material_interface
    materials.append({
        "slot": index,
        "slot_name": str(material.material_slot_name),
        "material_path": interface.get_path_name() if interface else "",
    })
payload = {
    "schema_version": 1,
    "status": "read_only_complete",
    "context": context,
    "asset_ref": ASSET_REF,
    "asset_path": path,
    "bounds_min_cm": {"x": box.min.x, "y": box.min.y, "z": box.min.z},
    "bounds_max_cm": {"x": box.max.x, "y": box.max.y, "z": box.max.z},
    "dimensions_cm": {"x": dimensions.x, "y": dimensions.y, "z": dimensions.z},
    "materials": materials,
    "changes_made": False,
}
report = common.write_json_report(config, "old_town_door_asset_probe_v1.json", payload)
unreal.log("SUNSCAR_DOOR_ASSET_PROBE path=%s report=%s" % (path, report))
print("SUNSCAR_DOOR_ASSET_PROBE", path, report)
