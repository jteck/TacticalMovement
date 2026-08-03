"""Read-only inventory of large ground and terrain actors around Old Town."""

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
    origin, extent = actor.get_actor_bounds(False)
    if not (-50000.0 <= origin.x <= 50000.0 and -50000.0 <= origin.y <= 50000.0):
        continue
    if not isinstance(actor, unreal.LandscapeProxy) and max(extent.x, extent.y) < 4000.0:
        continue
    component = getattr(actor, "static_mesh_component", None)
    materials = []
    if component is not None:
        for index in range(component.get_num_materials()):
            material = component.get_material(index)
            materials.append(material.get_path_name() if material else "")
    landscape_material = ""
    landscape_hole_material = ""
    if isinstance(actor, unreal.LandscapeProxy):
        try:
            material = actor.get_editor_property("landscape_material")
            landscape_material = material.get_path_name() if material else ""
        except Exception as error:
            landscape_material = "ERROR:" + str(error)
        try:
            material = actor.get_editor_property("landscape_hole_material")
            landscape_hole_material = material.get_path_name() if material else ""
        except Exception as error:
            landscape_hole_material = "ERROR:" + str(error)
    records.append({
        "label": actor.get_actor_label(),
        "class": actor.get_class().get_name(),
        "folder": common.actor_folder(actor),
        "mesh_path": common.actor_mesh_path(actor),
        "material_paths": materials,
        "landscape_material": landscape_material,
        "landscape_hole_material": landscape_hole_material,
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
    "level_saved": False,
}
report = common.write_json_report(config, "old_town_large_ground_audit_v1.json", payload)
unreal.log("SUNSCAR_LARGE_GROUND_AUDIT actors=%d report=%s" % (len(records), report))
print("SUNSCAR_LARGE_GROUND_AUDIT", len(records), report)
