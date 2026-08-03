"""Read-only audit for the three wall-mounted Old Town electrical boxes."""

import math
import os
import sys

import unreal

SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


TAG = unreal.Name("SunscarOldTownElectricalBoxesV1")
config = common.load_config()
context = common.require_safe_context(config, write_requested=False)
actors = list(common.actor_subsystem().get_all_level_actors())
targets = [actor for actor in actors if TAG in list(actor.tags)]
walls = []
floors = []
for actor in actors:
    label = actor.get_actor_label()
    if "SS_007" not in label:
        continue
    origin, extent = actor.get_actor_bounds(False)
    if "Wall" in label:
        walls.append((label, origin, extent))
    if "Floor" in label:
        floors.append((origin.z + extent.z, label, origin, extent))


def distance_to_wall(x, y):
    values = []
    for label, origin, extent in walls:
        dx = max(abs(x - origin.x) - extent.x, 0.0)
        dy = max(abs(y - origin.y) - extent.y, 0.0)
        values.append((math.sqrt(dx * dx + dy * dy), label))
    values.sort()
    return values[0] if values else (None, "")


records = []
flags = []
for actor in sorted(targets, key=lambda item: item.get_actor_label()):
    origin, extent = actor.get_actor_bounds(False)
    bottom = origin.z - extent.z
    location = actor.get_actor_location()
    containing = [
        (top_z, label)
        for top_z, label, floor_origin, floor_extent in floors
        if abs(location.x - floor_origin.x) <= floor_extent.x + 10.0
        and abs(location.y - floor_origin.y) <= floor_extent.y + 10.0
    ]
    containing.sort()
    floor_z = containing[0][0] if containing else None
    floor_label = containing[0][1] if containing else ""
    wall_distance, wall_label = distance_to_wall(location.x, location.y)
    dimensions = extent * 2.0
    actor_flags = []
    if floor_z is None or abs(bottom - (floor_z + 100.0)) > 3.0:
        actor_flags.append("mount_height")
    if wall_distance is None or wall_distance > 20.0:
        actor_flags.append("wall_distance")
    if max(dimensions.x, dimensions.y, dimensions.z) > 75.0:
        actor_flags.append("oversize")
    record = {
        "label": actor.get_actor_label(),
        "floor_actor": floor_label,
        "bottom_above_floor_cm": round(bottom - floor_z, 3) if floor_z is not None else None,
        "nearest_wall": wall_label,
        "nearest_wall_distance_cm": round(wall_distance, 3) if wall_distance is not None else None,
        "dimensions_cm": {"x": round(dimensions.x, 3), "y": round(dimensions.y, 3), "z": round(dimensions.z, 3)},
        "flags": actor_flags,
    }
    records.append(record)
    if actor_flags:
        flags.append(record)

payload = {
    "schema_version": 1,
    "status": "read_only_complete",
    "context": context,
    "actor_count": len(targets),
    "flagged_count": len(flags),
    "records": records,
    "flags": flags,
    "changes_made": False,
    "level_saved": False,
}
report = common.write_json_report(config, "old_town_electrical_box_audit_v1.json", payload)
unreal.log("SUNSCAR_ELECTRICAL_AUDIT actors=%d flagged=%d report=%s" % (len(targets), len(flags), report))
print("SUNSCAR_ELECTRICAL_AUDIT", len(targets), len(flags), report)
