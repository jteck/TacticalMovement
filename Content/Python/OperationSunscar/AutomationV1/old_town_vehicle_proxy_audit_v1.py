"""Read-only audit of the five authored Old Town vehicle proxy actors."""

import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


LABELS = (
    "Salvage_Vehicle_01",
    "Salvage_Vehicle_02",
    "Salvage_Vehicle_03",
    "MotorPool_Vehicle_A",
    "MotorPool_Vehicle_B",
)
config = common.load_config()
context = common.require_safe_context(config, write_requested=False)
by_label = {actor.get_actor_label(): actor for actor in common.actor_subsystem().get_all_level_actors()}
records = []
for label in LABELS:
    actor = by_label.get(label)
    if actor is None:
        raise RuntimeError("SUNSCAR_VEHICLE_PROXY_MISSING " + label)
    component = getattr(actor, "static_mesh_component", None)
    if component is None:
        raise RuntimeError("SUNSCAR_VEHICLE_PROXY_NO_COMPONENT " + label)
    origin, extent = actor.get_actor_bounds(False)
    location = actor.get_actor_location()
    rotation = actor.get_actor_rotation()
    scale = actor.get_actor_scale3d()
    material_paths = []
    for index in range(component.get_num_materials()):
        material = component.get_material(index)
        material_paths.append(material.get_path_name() if material else "")
    records.append({
        "label": label,
        "folder": common.actor_folder(actor),
        "mesh_path": common.actor_mesh_path(actor),
        "material_paths": material_paths,
        "location_cm": [round(location.x, 3), round(location.y, 3), round(location.z, 3)],
        "rotation": {"pitch": round(rotation.pitch, 3), "yaw": round(rotation.yaw, 3), "roll": round(rotation.roll, 3)},
        "scale": [round(scale.x, 4), round(scale.y, 4), round(scale.z, 4)],
        "bounds_origin_cm": [round(origin.x, 3), round(origin.y, 3), round(origin.z, 3)],
        "bounds_extent_cm": [round(extent.x, 3), round(extent.y, 3), round(extent.z, 3)],
        "collision": str(component.get_collision_enabled()),
        "tags": common.actor_tags(actor),
        "package": actor.get_package().get_name(),
    })

payload = {
    "schema_version": 1,
    "status": "read_only_audit_complete",
    "context": context,
    "actor_count": len(records),
    "records": records,
    "changes_made": False,
}
report = common.write_json_report(config, "old_town_vehicle_proxy_audit_v1.json", payload)
unreal.log("SUNSCAR_VEHICLE_PROXY_AUDIT actors=%d report=%s" % (len(records), report))
print("SUNSCAR_VEHICLE_PROXY_AUDIT", len(records), report)
