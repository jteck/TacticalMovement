"""Read-only audit of existing Old Town door proxy actors."""

import os
import sys

import unreal

SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


config = common.load_config()
context = common.require_safe_context(config, write_requested=False)
actors = list(common.actor_subsystem().get_all_level_actors())
targets = sorted(
    [actor for actor in actors if "door" in actor.get_actor_label().lower() and isinstance(actor, unreal.StaticMeshActor)],
    key=lambda actor: actor.get_actor_label(),
)
records = []
for actor in targets:
    origin, extent = actor.get_actor_bounds(False)
    location = actor.get_actor_location()
    rotation = actor.get_actor_rotation()
    scale = actor.get_actor_scale3d()
    component = actor.static_mesh_component
    mesh = component.static_mesh
    site_tags = sorted(tag for tag in common.actor_tags(actor) if tag.startswith("SS_"))
    records.append({
        "label": actor.get_actor_label(),
        "actor_path": actor.get_path_name(),
        "actor_package": actor.get_package().get_name(),
        "site_tags": site_tags,
        "folder": common.actor_folder(actor),
        "mesh_path": mesh.get_path_name() if mesh else "",
        "location_cm": {"x": round(location.x, 3), "y": round(location.y, 3), "z": round(location.z, 3)},
        "rotation_deg": {"pitch": round(rotation.pitch, 3), "yaw": round(rotation.yaw, 3), "roll": round(rotation.roll, 3)},
        "scale": {"x": round(scale.x, 5), "y": round(scale.y, 5), "z": round(scale.z, 5)},
        "dimensions_cm": {"x": round(extent.x * 2.0, 3), "y": round(extent.y * 2.0, 3), "z": round(extent.z * 2.0, 3)},
        "collision": str(component.get_collision_enabled()),
        "tags": sorted(common.actor_tags(actor)),
    })

payload = {
    "schema_version": 1,
    "status": "read_only_complete",
    "context": context,
    "actor_count": len(records),
    "records": records,
    "changes_made": False,
    "level_saved": False,
}
report = common.write_json_report(config, "old_town_door_proxy_audit_v1.json", payload)
unreal.log("SUNSCAR_DOOR_PROXY_AUDIT actors=%d report=%s" % (len(records), report))
print("SUNSCAR_DOOR_PROXY_AUDIT", len(records), report)
