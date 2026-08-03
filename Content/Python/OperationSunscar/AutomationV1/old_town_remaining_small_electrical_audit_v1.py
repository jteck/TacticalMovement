"""Read-only geometry audit for 13 support-resolved Old Town electrical boxes."""

import math
import os
import sys

import unreal

SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


TAG = unreal.Name("SunscarOldTownElectricalBoxesV2")
config = common.load_config()
context = common.require_safe_context(config, write_requested=False)
actors = list(common.actor_subsystem().get_all_level_actors())
targets = sorted([actor for actor in actors if TAG in list(actor.tags)], key=lambda item: item.get_actor_label())


def tagged_site(actor):
    values = [str(tag) for tag in actor.tags if str(tag).startswith("SS_")]
    return values[0] if values else ""


def site_geometry(site_id):
    floors = []
    walls = []
    for actor in actors:
        label = actor.get_actor_label()
        if site_id not in label:
            continue
        origin, extent = actor.get_actor_bounds(False)
        if "Floor" in label:
            floors.append((origin.z + extent.z, label, origin, extent))
        if "Wall" in label:
            walls.append((label, origin, extent))
    return floors, walls


def distance_to_wall(walls, x, y):
    values = []
    for label, origin, extent in walls:
        dx = max(abs(x - origin.x) - extent.x, 0.0)
        dy = max(abs(y - origin.y) - extent.y, 0.0)
        values.append((math.sqrt(dx * dx + dy * dy), label))
    values.sort()
    return values[0] if values else (None, "")


records = []
flags = []
target_bounds = []
for actor in targets:
    site_id = tagged_site(actor)
    floors, walls = site_geometry(site_id)
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
    wall_distance, wall_label = distance_to_wall(walls, location.x, location.y)
    dimensions = extent * 2.0
    actor_flags = []
    if not site_id:
        actor_flags.append("missing_site_tag")
    if floor_z is None or abs(bottom - (floor_z + 100.0)) > 3.0:
        actor_flags.append("mount_height")
    if wall_distance is None or wall_distance > 20.0:
        actor_flags.append("wall_distance")
    if max(dimensions.x, dimensions.y, dimensions.z) > 75.0:
        actor_flags.append("oversize")
    record = {
        "label": actor.get_actor_label(),
        "actor_path": actor.get_path_name(),
        "site_id": site_id,
        "floor_actor": floor_label,
        "bottom_above_floor_cm": round(bottom - floor_z, 3) if floor_z is not None else None,
        "nearest_wall": wall_label,
        "nearest_wall_distance_cm": round(wall_distance, 3) if wall_distance is not None else None,
        "dimensions_cm": {"x": round(dimensions.x, 3), "y": round(dimensions.y, 3), "z": round(dimensions.z, 3)},
        "flags": actor_flags,
    }
    records.append(record)
    target_bounds.append((actor.get_actor_label(), origin, extent))
    if actor_flags:
        flags.append(record)

pair_overlaps = []
for index, (label_a, origin_a, extent_a) in enumerate(target_bounds):
    for label_b, origin_b, extent_b in target_bounds[index + 1:]:
        if (
            abs(origin_a.x - origin_b.x) < extent_a.x + extent_b.x
            and abs(origin_a.y - origin_b.y) < extent_a.y + extent_b.y
            and abs(origin_a.z - origin_b.z) < extent_a.z + extent_b.z
        ):
            pair_overlaps.append([label_a, label_b])

payload = {
    "schema_version": 1,
    "status": "read_only_complete",
    "context": context,
    "actor_count": len(targets),
    "expected_actor_count": 13,
    "flagged_count": len(flags),
    "pair_overlap_count": len(pair_overlaps),
    "pair_overlaps": pair_overlaps,
    "records": records,
    "flags": flags,
    "changes_made": False,
    "level_saved": False,
}
report = common.write_json_report(config, "old_town_remaining_small_electrical_audit_v1.json", payload)
unreal.log(
    "SUNSCAR_REMAINING_ELECTRICAL_AUDIT actors=%d flagged=%d overlaps=%d report=%s"
    % (len(targets), len(flags), len(pair_overlaps), report)
)
print("SUNSCAR_REMAINING_ELECTRICAL_AUDIT", len(targets), len(flags), len(pair_overlaps), report)
