"""Read-only inspection of the Old Town UE import queue in the current project."""

import os
import sys

import unreal

SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


config = common.load_config()
context = common.require_safe_context(config, write_requested=False)
queue_path = common.planning_file(config, "import_queue_file")
registry_path = common.planning_file(config, "final_registry_file")

if not os.path.exists(queue_path):
    raise RuntimeError("SUNSCAR_IMPORT_QUEUE_MISSING " + queue_path)

queue = common.read_csv(queue_path)
registry = common.read_json(registry_path) if os.path.exists(registry_path) else {"resolved_refs": {}}
asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()


def property_value(obj, name, default=None):
    try:
        return obj.get_editor_property(name)
    except Exception:
        return default


def vector_dict(vector):
    if vector is None:
        return None
    return {"x": round(vector.x, 4), "y": round(vector.y, 4), "z": round(vector.z, 4)}


def static_mesh_details(mesh):
    details = {}
    try:
        bounds = mesh.get_bounds()
        details["bounds_origin_cm"] = vector_dict(bounds.origin)
        details["bounds_extent_cm"] = vector_dict(bounds.box_extent)
        details["bounds_size_cm"] = vector_dict(bounds.box_extent * 2.0)
        details["sphere_radius_cm"] = round(bounds.sphere_radius, 4)
    except Exception as exc:
        details["bounds_error"] = str(exc)

    static_materials = property_value(mesh, "static_materials", []) or []
    material_slots = []
    for slot in static_materials:
        material = property_value(slot, "material_interface")
        slot_name = property_value(slot, "material_slot_name", "")
        material_slots.append(
            {
                "slot": str(slot_name),
                "material": material.get_path_name() if material else "",
            }
        )
    details["material_slots"] = material_slots
    details["material_slot_count"] = len(material_slots)

    nanite = property_value(mesh, "nanite_settings")
    details["nanite_enabled"] = bool(property_value(nanite, "enabled", False)) if nanite else None
    body_setup = property_value(mesh, "body_setup")
    details["body_setup_present"] = body_setup is not None
    if body_setup:
        details["collision_trace_flag"] = str(property_value(body_setup, "collision_trace_flag", "unknown"))
        aggregate_geometry = property_value(body_setup, "agg_geom")
        if aggregate_geometry:
            details["simple_collision_counts"] = {
                "boxes": len(property_value(aggregate_geometry, "box_elems", []) or []),
                "spheres": len(property_value(aggregate_geometry, "sphere_elems", []) or []),
                "capsules": len(property_value(aggregate_geometry, "sphyl_elems", []) or []),
                "convex": len(property_value(aggregate_geometry, "convex_elems", []) or []),
            }
    details["lod_count"] = mesh.get_num_lods() if hasattr(mesh, "get_num_lods") else None
    return details


def package_dependencies(asset_path):
    package_name = asset_path.split(".")[0]
    try:
        dependencies = asset_registry.get_dependencies(package_name)
        return sorted(str(dependency) for dependency in dependencies)
    except Exception as first_error:
        try:
            options = unreal.AssetRegistryDependencyOptions(
                include_soft_package_references=True,
                include_hard_package_references=True,
                include_searchable_names=False,
                include_soft_management_references=False,
                include_hard_management_references=False,
            )
            dependencies = asset_registry.get_dependencies(package_name, options)
            return sorted(str(dependency) for dependency in dependencies)
        except Exception as second_error:
            return ["DEPENDENCY_QUERY_ERROR: %s | %s" % (first_error, second_error)]


records = []
for item in queue:
    asset_ref = item["asset_ref"]
    resolved_path = common.safe_asset_ref_to_path(asset_ref, registry)
    record = dict(item)
    record.update(
        {
            "resolved_asset_path": resolved_path,
            "resolved": bool(resolved_path),
            "allowed_path": common.asset_path_allowed(config, resolved_path) if resolved_path else False,
            "asset_exists": False,
            "asset_class": "",
            "inspection": {},
            "dependencies": [],
            "inspection_status": "unresolved_reference" if not resolved_path else "pending_load",
        }
    )

    if not resolved_path:
        records.append(record)
        continue
    if not record["allowed_path"]:
        record["inspection_status"] = "blocked_asset_path"
        records.append(record)
        continue

    asset = unreal.EditorAssetLibrary.load_asset(resolved_path)
    if asset is None:
        record["inspection_status"] = "missing_in_current_project"
        records.append(record)
        continue

    record["asset_exists"] = True
    record["asset_class"] = asset.get_class().get_name()
    record["dependencies"] = package_dependencies(resolved_path)
    if isinstance(asset, unreal.StaticMesh):
        record["inspection"] = static_mesh_details(asset)
        record["inspection_status"] = "static_mesh_inspected_ue_visual_review_pending"
    elif isinstance(asset, unreal.MaterialInterface):
        record["inspection"] = {"material_interface": True}
        record["inspection_status"] = "material_found_rendered_review_pending"
    else:
        record["inspection"] = {"supported_for_automatic_placement": False}
        record["inspection_status"] = "asset_found_manual_class_review_required"
    records.append(record)

summary = {}
for record in records:
    summary[record["inspection_status"]] = summary.get(record["inspection_status"], 0) + 1

payload = {
    "schema_version": 1,
    "status": "read_only_asset_inspection_complete",
    "context": context,
    "queue_path": queue_path,
    "registry_path": registry_path,
    "queue_record_count": len(queue),
    "summary": summary,
    "records": records,
    "changes_made": False,
    "warning": "Filename and class inspection do not constitute visual approval. Review meshes and materials in the editor before registry acceptance.",
}

path = common.write_json_report(config, "old_town_asset_inspection.json", payload)
unreal.log("SUNSCAR_ASSET_INSPECTION records=%d report=%s" % (len(records), path))
print("SUNSCAR_ASSET_INSPECTION", len(records), summary, path)
