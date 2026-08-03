"""Read-only audit of broad near-ground meshes in the Old Town region."""

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
    # Restrict to the Old Town design envelope and broad, low-profile geometry.
    if not (-18000.0 <= origin.x <= 18000.0 and -13000.0 <= origin.y <= 12500.0):
        continue
    if max(extent.x, extent.y) < 250.0 or extent.z > 180.0:
        continue
    if not (34300.0 <= origin.z <= 35350.0):
        continue
    mesh = component.get_editor_property("static_mesh")
    materials = []
    for index in range(component.get_num_materials()):
        material = component.get_material(index)
        materials.append(material.get_path_name() if material else "")
    records.append({
        "label": actor.get_actor_label(),
        "folder": common.actor_folder(actor),
        "mesh_path": mesh.get_path_name() if mesh else "",
        "material_paths": materials,
        "origin_cm": [round(origin.x, 3), round(origin.y, 3), round(origin.z, 3)],
        "extent_cm": [round(extent.x, 3), round(extent.y, 3), round(extent.z, 3)],
        "tags": common.actor_tags(actor),
    })

records.sort(key=lambda item: item["label"])
payload = {
    "schema_version": 1,
    "status": "read_only_audit_complete",
    "context": context,
    "actor_count": len(records),
    "records": records,
    "changes_made": False,
}
report = common.write_json_report(config, "old_town_ground_material_audit_v1.json", payload)
unreal.log("SUNSCAR_GROUND_MATERIAL_AUDIT actors=%d report=%s" % (len(records), report))
