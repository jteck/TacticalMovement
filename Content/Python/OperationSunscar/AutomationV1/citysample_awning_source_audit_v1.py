"""Read-only UE audit of the seven owned City Sample awning meshes and dependency closure."""

import json
import os
from collections import deque
from datetime import datetime, timezone

import unreal


EXPECTED_PROJECT = "OfficialAssetStaging"
EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_SampleAudit/OfficialAssetStaging"
REPORT_PATH = (
    "/Users/jasonteck/UnrealEngine/_worktrees/map-development/Saved/OperationSunscar/Reports/"
    "citysample_awning_source_audit_v1.json"
)
ROOT = "/Game/CitySampleBuildings/Building/NY/A/Kit_PROP_NYA"
MESH_PATHS = tuple(
    ROOT + "/Mesh/SM_PROP_NYA_A_Awning_%s_N1" % suffix
    for suffix in ("01", "02", "03", "05", "07", "08", "10")
)


def property_value(obj, name, default=None):
    try:
        return obj.get_editor_property(name)
    except Exception:
        return default


def vector_dict(vector):
    return {"x": round(float(vector.x), 3), "y": round(float(vector.y), 3), "z": round(float(vector.z), 3)}


def dependency_options():
    return unreal.AssetRegistryDependencyOptions(
        include_soft_package_references=True,
        include_hard_package_references=True,
        include_searchable_names=False,
        include_soft_management_references=False,
        include_hard_management_references=False,
    )


project_name = os.path.splitext(os.path.basename(unreal.Paths.get_project_file_path()))[0]
project_directory = os.path.abspath(unreal.Paths.project_dir()).replace("\\", "/").rstrip("/")
if project_name != EXPECTED_PROJECT or not project_directory.endswith(EXPECTED_DIRECTORY_SUFFIX):
    raise RuntimeError("CITYSAMPLE_AWNING_AUDIT_WRONG_PROJECT %s %s" % (project_name, project_directory))

registry = unreal.AssetRegistryHelpers.get_asset_registry()
registry.scan_paths_synchronous([ROOT], force_rescan=False, ignore_deny_list_scan_filters=False)
options = dependency_options()


def dependencies(package_name):
    try:
        return sorted(str(item) for item in registry.get_dependencies(package_name, options))
    except Exception:
        return sorted(str(item) for item in registry.get_dependencies(package_name))


records = []
for path in MESH_PATHS:
    mesh = unreal.EditorAssetLibrary.load_asset(path)
    if not isinstance(mesh, unreal.StaticMesh):
        raise RuntimeError("CITYSAMPLE_AWNING_AUDIT_MISSING " + path)
    bounds = mesh.get_bounds()
    size = bounds.box_extent * 2.0
    materials = []
    for slot in property_value(mesh, "static_materials", []) or []:
        material = property_value(slot, "material_interface")
        materials.append(
            {
                "slot": str(property_value(slot, "material_slot_name", "")),
                "material": material.get_path_name() if material else "",
            }
        )
    nanite = property_value(mesh, "nanite_settings")
    body_setup = property_value(mesh, "body_setup")
    records.append(
        {
            "asset_path": path,
            "bounds_origin_cm": vector_dict(bounds.origin),
            "bounds_size_cm": vector_dict(size),
            "largest_dimension_cm": round(max(size.x, size.y, size.z), 3),
            "sphere_radius_cm": round(float(bounds.sphere_radius), 3),
            "lod_count": mesh.get_num_lods() if hasattr(mesh, "get_num_lods") else None,
            "nanite_enabled": bool(property_value(nanite, "enabled", False)) if nanite else None,
            "material_slots": materials,
            "body_setup_present": body_setup is not None,
            "collision_trace_flag": str(property_value(body_setup, "collision_trace_flag", "unknown")) if body_setup else "none",
            "simple_collision_count": int(unreal.EditorStaticMeshLibrary.get_simple_collision_count(mesh)),
            "direct_dependencies": dependencies(path),
        }
    )

queue = deque(MESH_PATHS)
closure = set(MESH_PATHS)
while queue:
    package = queue.popleft()
    for dependency in dependencies(package):
        if not dependency.startswith("/Game/CitySampleBuildings/") or dependency in closure:
            continue
        closure.add(dependency)
        queue.append(dependency)
        if len(closure) > 500:
            raise RuntimeError("CITYSAMPLE_AWNING_AUDIT_DEPENDENCY_SCOPE_EXCEEDED")

package_files = []
missing_package_files = []
for package in sorted(closure):
    relative = package.removeprefix("/Game/")
    candidates = [
        os.path.join(project_directory, "Content", relative + ".uasset"),
        os.path.join(project_directory, "Content", relative + ".umap"),
    ]
    existing = next((path for path in candidates if os.path.isfile(path)), "")
    if existing:
        package_files.append(
            {
                "package": package,
                "source_file": existing,
                "size_bytes": os.path.getsize(existing),
            }
        )
    else:
        missing_package_files.append(package)

dirty_content = sorted(package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
dirty_maps = sorted(package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
payload = {
    "schema_version": 1,
    "status": "read_only_citysample_awning_source_audit_complete",
    "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "context": {"project": project_name, "project_directory": project_directory},
    "publisher_scope": "Epic Games City Sample Buildings owned project content",
    "mesh_count": len(records),
    "records": records,
    "dependency_package_count": len(closure),
    "dependency_packages": sorted(closure),
    "dependency_files": package_files,
    "missing_dependency_files": missing_package_files,
    "dependency_size_bytes": sum(item["size_bytes"] for item in package_files),
    "dirty_content_packages": dirty_content,
    "dirty_map_packages": dirty_maps,
    "changes_made": False,
}
os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
with open(REPORT_PATH, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2)
    handle.write("\n")
unreal.log(
    "CITYSAMPLE_AWNING_AUDIT_COMPLETE meshes=%d packages=%d bytes=%d"
    % (len(records), len(closure), payload["dependency_size_bytes"])
)
print("CITYSAMPLE_AWNING_AUDIT_COMPLETE", REPORT_PATH)
