"""Read-only inventory of static facade geometry around SS_005."""

import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


config = common.load_config()
context = common.require_safe_context(config, write_requested=False)
records = []
for actor in common.actor_subsystem().get_all_level_actors():
    component = getattr(actor, "static_mesh_component", None)
    if component is None:
        continue
    origin, extent = actor.get_actor_bounds(False)
    if abs(origin.x + 5600.0) > 1800.0 or abs(origin.y + 100.0) > 1550.0:
        continue
    if origin.z + extent.z < 34500.0 or origin.z - extent.z > 35700.0:
        continue
    materials = []
    for index in range(component.get_num_materials()):
        material = component.get_material(index)
        materials.append(material.get_path_name() if material else "")
    records.append({
        "label": actor.get_actor_label(),
        "class": actor.get_class().get_name(),
        "folder": common.actor_folder(actor),
        "mesh_path": common.actor_mesh_path(actor),
        "origin_cm": [round(origin.x, 3), round(origin.y, 3), round(origin.z, 3)],
        "extent_cm": [round(extent.x, 3), round(extent.y, 3), round(extent.z, 3)],
        "material_paths": materials,
        "tags": common.actor_tags(actor),
        "package": actor.get_package().get_name(),
    })
records.sort(key=lambda row: row["label"])
dirty = sorted(
    package.get_name()
    for package in (
        list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
        + list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
    )
)
payload = {
    "schema_version": 1,
    "status": "read_only_audit_complete",
    "context": context,
    "actor_count": len(records),
    "records": records,
    "dirty_packages": dirty,
    "changes_made": False,
}
report = common.write_json_report(config, "old_town_ss005_facade_audit_v1.json", payload)
unreal.log("SUNSCAR_SS005_FACADE_AUDIT actors=%d dirty=%d report=%s" % (len(records), len(dirty), report))
print("SUNSCAR_SS005_FACADE_AUDIT", len(records), len(dirty), report)
