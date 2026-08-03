"""Read-only grounding and AABB-overlap audit for planned static vehicles."""

import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


TAG = "SunscarOldTownVehicleReplacementV1"
config = common.load_config()
context = common.require_safe_context(config, write_requested=False)
world = common.editor_world()
actors = list(common.actor_subsystem().get_all_level_actors())
targets = [actor for actor in actors if TAG in common.actor_tags(actor)]
if len(targets) != 5:
    raise RuntimeError("SUNSCAR_STATIC_VEHICLE_AUDIT_SCOPE actor_count=%d" % len(targets))


def aabb_overlap(origin_a, extent_a, origin_b, extent_b):
    return (
        abs(origin_a.x - origin_b.x) < extent_a.x + extent_b.x
        and abs(origin_a.y - origin_b.y) < extent_a.y + extent_b.y
        and abs(origin_a.z - origin_b.z) < extent_a.z + extent_b.z
    )


records = []
review = []
for actor in sorted(targets, key=lambda value: value.get_actor_label()):
    origin, extent = actor.get_actor_bounds(False)
    bottom_z = origin.z - extent.z
    hit = unreal.SystemLibrary.line_trace_single(
        world,
        unreal.Vector(origin.x, origin.y, bottom_z + 40.0),
        unreal.Vector(origin.x, origin.y, bottom_z - 500.0),
        unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
        True,
        targets,
        unreal.DrawDebugTrace.NONE,
        True,
    )
    result = hit.to_dict() if hit is not None else {}
    support_z = result["location"].z if result.get("blocking_hit") else None
    gap = bottom_z - support_z if support_z is not None else None
    overlaps = []
    for other in actors:
        if other in targets or "Landscape" in other.get_class().get_name():
            continue
        other_label = other.get_actor_label()
        if (
            other_label.startswith("District_")
            or other_label.startswith("Route_")
            or other_label in {"SS_014_Salvage Yard", "SS_015_Motor Pool"}
        ):
            continue
        other_origin, other_extent = other.get_actor_bounds(False)
        if other_extent.z <= 35.0:
            continue
        if not aabb_overlap(origin, extent, other_origin, other_extent):
            continue
        # A support pad beneath the vehicle is not a blocking overlap.
        other_top = other_origin.z + other_extent.z
        if other_top <= bottom_z + 5.0:
            continue
        overlaps.append(other.get_actor_label())
    rotation = actor.get_actor_rotation()
    component = actor.static_mesh_component
    reasons = []
    if gap is None or gap < -3.0 or gap > 3.0:
        reasons.append("support_gap_out_of_tolerance")
    if abs(rotation.pitch) > 0.01 or abs(rotation.roll) > 0.01:
        reasons.append("unexpected_pitch_or_roll")
    if "QUERY_AND_PHYSICS" not in str(component.get_collision_enabled()):
        reasons.append("collision_not_query_and_physics")
    if overlaps:
        reasons.append("aabb_overlap_requires_visual_review")
    record = {
        "label": actor.get_actor_label(),
        "mesh_path": common.actor_mesh_path(actor),
        "location_cm": [round(origin.x, 3), round(origin.y, 3), round(origin.z, 3)],
        "extent_cm": [round(extent.x, 3), round(extent.y, 3), round(extent.z, 3)],
        "support_gap_cm": round(gap, 3) if gap is not None else None,
        "support_actor": result.get("hit_actor").get_actor_label() if result.get("hit_actor") else "",
        "rotation": {"pitch": round(rotation.pitch, 3), "yaw": round(rotation.yaw, 3), "roll": round(rotation.roll, 3)},
        "collision": str(component.get_collision_enabled()),
        "overlap_labels": sorted(set(overlaps)),
        "review_reasons": reasons,
    }
    records.append(record)
    if reasons:
        review.append(record)

payload = {
    "schema_version": 1,
    "status": "read_only_audit_complete",
    "context": context,
    "actor_count": len(records),
    "review_required_count": len(review),
    "review_required": review,
    "records": records,
    "changes_made": False,
}
report = common.write_json_report(config, "old_town_static_vehicle_audit_v1.json", payload)
unreal.log("SUNSCAR_STATIC_VEHICLE_AUDIT actors=%d review=%d report=%s" % (len(records), len(review), report))
print("SUNSCAR_STATIC_VEHICLE_AUDIT", len(records), len(review), report)
