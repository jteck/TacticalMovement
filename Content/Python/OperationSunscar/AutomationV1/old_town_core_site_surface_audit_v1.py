"""Read-only audit of the 20 original Old Town landmark proxy actors."""

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
    label = actor.get_actor_label()
    folder = common.actor_folder(actor)
    if not label.startswith("SS_") or folder != "Sunscar/Blockout/Landmarks/Old Town Core":
        continue
    component = getattr(actor, "static_mesh_component", None)
    origin, extent = actor.get_actor_bounds(False)
    materials = []
    if component is not None:
        for index in range(component.get_num_materials()):
            material = component.get_material(index)
            materials.append(material.get_path_name() if material else "")
    records.append({
        "label": label,
        "folder": folder,
        "mesh_path": common.actor_mesh_path(actor),
        "material_paths": materials,
        "origin_cm": [round(origin.x, 3), round(origin.y, 3), round(origin.z, 3)],
        "extent_cm": [round(extent.x, 3), round(extent.y, 3), round(extent.z, 3)],
        "tags": common.actor_tags(actor),
        "package": actor.get_package().get_name(),
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
report = common.write_json_report(config, "old_town_core_site_surface_audit_v1.json", payload)
unreal.log("SUNSCAR_CORE_SITE_SURFACE_AUDIT actors=%d report=%s" % (len(records), report))
print("SUNSCAR_CORE_SITE_SURFACE_AUDIT", len(records), report)
