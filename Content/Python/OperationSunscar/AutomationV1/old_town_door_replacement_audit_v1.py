"""Read-only audit of the 16 in-place Old Town pedestrian door replacements."""

import os
import sys

import unreal

SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


TAG = "SunscarOldTownDoorReplacementV1"
TARGET_MESH = "/Game/Maps/Sunscar/Art/Quixel/Downloaded/FAB_P1B_001_wbmgdcpdw/Old_Wooden_Door_wbmgdcpdw_High.Old_Wooden_Door_wbmgdcpdw_High"
config = common.load_config()
context = common.require_safe_context(config, write_requested=False)
targets = sorted(
    [actor for actor in common.actor_subsystem().get_all_level_actors() if TAG in common.actor_tags(actor)],
    key=lambda actor: actor.get_actor_label(),
)
records = []
review = []
for actor in targets:
    origin, extent = actor.get_actor_bounds(False)
    rotation = actor.get_actor_rotation()
    component = actor.static_mesh_component
    dimensions = extent * 2.0
    materials = [
        component.get_material(index).get_path_name() if component.get_material(index) else ""
        for index in range(component.get_num_materials())
    ]
    reasons = []
    if common.actor_mesh_path(actor) != TARGET_MESH:
        reasons.append("unexpected_mesh")
    if abs(dimensions.x - 125.0) > 1.0 or abs(dimensions.y - 18.0) > 1.0 or abs(dimensions.z - 240.0) > 1.0:
        reasons.append("proxy_dimensions_not_preserved")
    if abs(rotation.pitch) > 0.01 or abs(rotation.roll) > 0.01:
        reasons.append("unexpected_pitch_or_roll")
    if "QUERY_AND_PHYSICS" not in str(component.get_collision_enabled()):
        reasons.append("collision_not_query_and_physics")
    if not materials or any(not path for path in materials):
        reasons.append("missing_material")
    record = {
        "label": actor.get_actor_label(),
        "mesh_path": common.actor_mesh_path(actor),
        "origin_cm": [round(origin.x, 3), round(origin.y, 3), round(origin.z, 3)],
        "bottom_z_cm": round(origin.z - extent.z, 3),
        "dimensions_cm": [round(dimensions.x, 3), round(dimensions.y, 3), round(dimensions.z, 3)],
        "rotation": {"pitch": round(rotation.pitch, 3), "yaw": round(rotation.yaw, 3), "roll": round(rotation.roll, 3)},
        "collision": str(component.get_collision_enabled()),
        "materials": materials,
        "review_reasons": reasons,
    }
    records.append(record)
    if reasons:
        review.append(record)

payload = {
    "schema_version": 1,
    "status": "read_only_complete",
    "context": context,
    "actor_count": len(records),
    "review_required_count": len(review),
    "review_required": review,
    "records": records,
    "changes_made": False,
    "level_saved": False,
}
report = common.write_json_report(config, "old_town_door_replacement_audit_v1.json", payload)
unreal.log("SUNSCAR_DOOR_REPLACEMENT_AUDIT actors=%d review=%d report=%s" % (len(records), len(review), report))
print("SUNSCAR_DOOR_REPLACEMENT_AUDIT", len(records), len(review), report)
