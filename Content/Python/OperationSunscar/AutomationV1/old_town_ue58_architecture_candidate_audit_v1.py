"""Read-only bounds/performance audit of owned official architectural candidates."""

import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


# Intentionally bounded. A broad filename scan previously mixed architectural
# modules with props such as benches, sticks, and duckboards. These paths are a
# representative, locally owned Epic/Quixel set whose roles can be evaluated
# without loading an entire content pack or warming unrelated derived data.
CANDIDATE_PATHS = (
    "/Game/Maps/Sunscar/Art/Quixel/Downloaded/FAB_P1B_001_wbmgdcpdw/Old_Wooden_Door_wbmgdcpdw_High",
    "/Game/Maps/Sunscar/Art/Quixel/Downloaded/FAB_P0_005_ydxnbdns/Military_Trenches_Wall_Metal_Corrugated_06_ydxnbdns_High",
    "/Game/MilitaryTrench/Assets/3D/Mil_Trench_Frame_Roof_Wood_01/StaticMeshes/SM_Mil_Trench_Frame_Roof_Wood_01",
    "/Game/MilitaryTrench/Assets/3D/Mil_Trench_Frame_Roof_Wood_02/StaticMeshes/SM_Mil_Trench_Frame_Roof_Wood_02",
    "/Game/MilitaryTrench/Assets/3D/Mil_Trench_Frame_Roof_Wood_03/StaticMeshes/SM_Mil_Trench_Frame_Roof_Wood_03",
    "/Game/MilitaryTrench/Assets/3D/Mil_Trench_Emplacement_Roof_Wood/StaticMeshes/SM_Mil_Trench_Emplacement_Roof_Wood",
    "/Game/MilitaryTrench/Assets/3D/Mil_Trench_Wall_Metal_Corrugated_01/StaticMeshes/SM_Mil_Trench_Wall_Metal_Corrugated_01",
    "/Game/MilitaryTrench/Assets/3D/Mil_Trench_Wall_Metal_Corrugated_06/StaticMeshes/SM_Mil_Trench_Wall_Metal_Corrugated_06",
    "/Game/MilitaryTrench/Assets/3D/Mil_Trench_Wall_Metal_Corrugated_10/StaticMeshes/SM_Mil_Trench_Wall_Metal_Corrugated_10",
    "/Game/MilitaryTrench/Assets/3D/Mil_Trench_Wall_Metal_Corrugated_16/StaticMeshes/SM_Mil_Trench_Wall_Metal_Corrugated_16",
    "/Game/MilitaryTrench/Assets/3D/Mil_Trench_Wall_Dirt_Straight_02/StaticMeshes/SM_Mil_Trench_Wall_Dirt_Straight_02",
    "/Game/MilitaryTrench/Assets/3D/Mil_Trench_Wall_Dirt_Straight_03/StaticMeshes/SM_Mil_Trench_Wall_Dirt_Straight_03",
    "/Game/MilitaryTrench/Assets/3D/Mil_Trench_Wall_Dirt_Corner_01/StaticMeshes/SM_Mil_Trench_Wall_Dirt_Corner_01",
    "/Game/MilitaryTrench/Assets/3D/Mil_Trench_Wall_Dirt_Corner_04/StaticMeshes/SM_Mil_Trench_Wall_Dirt_Corner_04",
    "/Game/MilitaryTrench/Assets/3D/Mil_Trench_Wall_Wood_01/StaticMeshes/SM_Mil_Trench_Wall_Wood_01",
    "/Game/MilitaryTrench/Assets/3D/Mil_Trench_Wall_Wood_04/StaticMeshes/SM_Mil_Trench_Wall_Wood_04",
    "/Game/MilitaryTrench/Assets/3D/Mil_Trench_Beam_Metal_Rusted_02/StaticMeshes/SM_Mil_Trench_Beam_Metal_Rusted_02",
)


def property_value(obj, name, default=None):
    try:
        return obj.get_editor_property(name)
    except Exception:
        return default


def vector_dict(value):
    return {"x": round(value.x, 3), "y": round(value.y, 3), "z": round(value.z, 3)}


config = common.load_config()
context = common.require_safe_context(config, write_requested=False)
paths = []
missing_paths = []
for path in CANDIDATE_PATHS:
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        paths.append(path)
    else:
        missing_paths.append(path)

records = []
for path in paths:
    mesh = unreal.EditorAssetLibrary.load_asset(path)
    if not isinstance(mesh, unreal.StaticMesh):
        continue
    bounds = mesh.get_bounds()
    size = bounds.box_extent * 2.0
    materials = []
    for slot in property_value(mesh, "static_materials", []) or []:
        material = property_value(slot, "material_interface")
        materials.append(material.get_path_name() if material else "")
    body_setup = property_value(mesh, "body_setup")
    nanite = property_value(mesh, "nanite_settings")
    records.append({
        "asset_path": path,
        "publisher_scope": "Epic/Quixel owned project content",
        "review_state": "measured_candidate_viewport_review_required",
        "bounds_size_cm": vector_dict(size),
        "largest_dimension_cm": round(max(size.x, size.y, size.z), 3),
        "material_slot_count": len(materials),
        "material_paths": materials,
        "nanite_enabled": bool(property_value(nanite, "enabled", False)) if nanite else False,
        "lod_count": mesh.get_num_lods() if hasattr(mesh, "get_num_lods") else None,
        "body_setup_present": body_setup is not None,
        "collision_trace_flag": str(property_value(body_setup, "collision_trace_flag", "unknown")) if body_setup else "none",
        "recommended_use": "visual_art_only_until_viewport_and_gameplay_review",
    })

records.sort(key=lambda item: (item["asset_path"].split("/")[2], item["largest_dimension_cm"], item["asset_path"]))
payload = {
    "schema_version": 1,
    "status": "read_only_owned_official_architecture_candidate_audit_complete",
    "context": context,
    "selection_method": "bounded_representative_set",
    "requested_candidate_count": len(CANDIDATE_PATHS),
    "candidate_count": len(records),
    "missing_candidate_paths": missing_paths,
    "evidence": {
        "publisher_scope": "verified_from_owned project roots and acquisition records",
        "bounds_material_collision_nanite": "verified_from loaded Unreal assets",
        "visual_fit": "unknown_until_controlled viewport comparison",
        "selection": "bounded_candidate_set_only_not_approval",
    },
    "records": records,
    "changes_made": False,
    "level_saved": False,
}

report = common.write_json_report(config, "old_town_ue58_architecture_candidate_audit_v1.json", payload)
unreal.log("SUNSCAR_UE58_ARCH_CANDIDATES count=%d report=%s" % (len(records), report))
print("SUNSCAR_UE58_ARCH_CANDIDATES", len(records), report)
