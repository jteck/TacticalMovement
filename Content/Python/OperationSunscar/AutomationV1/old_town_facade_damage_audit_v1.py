"""Read-only geometry audit for Quixel facade-damage actors."""

import math
import os
import sys

import unreal

SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


TAG = unreal.Name("SunscarOldTownFacadeDamageV1")
config = common.load_config()
context = common.require_safe_context(config, write_requested=False)
actors = list(common.actor_subsystem().get_all_level_actors())
targets = [actor for actor in actors if TAG in list(actor.tags)]

records = []
flags = []
for actor in sorted(targets, key=lambda item: item.get_actor_label()):
    site = next((str(tag) for tag in actor.tags if str(tag).startswith("SS_")), "")
    location = actor.get_actor_location()
    origin, extent = actor.get_actor_bounds(False)
    dimensions = extent * 2.0
    floor_values, wall_values = [], []
    for other in actors:
        label = other.get_actor_label()
        if site not in label:
            continue
        other_origin, other_extent = other.get_actor_bounds(False)
        dx = max(abs(location.x - other_origin.x) - other_extent.x, 0.0)
        dy = max(abs(location.y - other_origin.y) - other_extent.y, 0.0)
        distance = math.sqrt(dx * dx + dy * dy)
        if "Floor" in label:
            floor_values.append((distance, other_origin.z + other_extent.z, label))
        if "Wall" in label:
            wall_values.append((distance, label))
    floor_values.sort()
    wall_values.sort()
    floor_z = floor_values[0][1] if floor_values else None
    floor_label = floor_values[0][2] if floor_values else ""
    wall_distance = wall_values[0][0] if wall_values else None
    wall_label = wall_values[0][1] if wall_values else ""
    actor_flags = []
    if wall_distance is None or wall_distance > 5.0:
        actor_flags.append("wall_distance")
    height = location.z - floor_z if floor_z is not None else None
    if height is None or height < 100.0 or height > 275.0:
        actor_flags.append("mount_height")
    # Axis-aligned bounds project a thin, yawed vertical plane into both X and Y;
    # validate vertical extent and capped overall size rather than apparent thickness.
    if dimensions.z < 100.0 or max(dimensions.x, dimensions.y, dimensions.z) > 240.0:
        actor_flags.append("plane_orientation_or_scale")
    record = {
        "label": actor.get_actor_label(), "site_id": site,
        "nearest_wall": wall_label, "nearest_wall_distance_cm": round(wall_distance, 3) if wall_distance is not None else None,
        "floor_actor": floor_label, "center_above_floor_cm": round(height, 3) if height is not None else None,
        "dimensions_cm": {"x": round(dimensions.x, 3), "y": round(dimensions.y, 3), "z": round(dimensions.z, 3)},
        "flags": actor_flags,
    }
    records.append(record)
    if actor_flags:
        flags.append(record)

payload = {
    "schema_version": 1, "status": "read_only_complete", "context": context,
    "actor_count": len(targets), "flagged_count": len(flags), "records": records, "flags": flags,
    "changes_made": False, "level_saved": False,
}
report = common.write_json_report(config, "old_town_facade_damage_audit_v1.json", payload)
unreal.log("SUNSCAR_FACADE_DAMAGE_AUDIT actors=%d flagged=%d report=%s" % (len(targets), len(flags), report))
print("SUNSCAR_FACADE_DAMAGE_AUDIT", len(targets), len(flags), report)
