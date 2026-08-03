"""Read-only geometry audit for SS_008 ground and asphalt-debris actors."""

import os
import sys

import unreal

SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


TAG = unreal.Name("SunscarOldTownMarketGroundDebrisV1")
config = common.load_config()
context = common.require_safe_context(config, write_requested=False)
world = common.editor_world()
actors = list(common.actor_subsystem().get_all_level_actors())
targets = [actor for actor in actors if TAG in list(actor.tags)]
walls = []
for actor in actors:
    label = actor.get_actor_label()
    if "SS_008" in label and ("Wall" in label or "Parapet" in label):
        origin, extent = actor.get_actor_bounds(False)
        walls.append((label, origin, extent))


def intersects(a_origin, a_extent, b_origin, b_extent):
    return (
        abs(a_origin.x - b_origin.x) < a_extent.x + b_extent.x - 2.0
        and abs(a_origin.y - b_origin.y) < a_extent.y + b_extent.y - 2.0
        and abs(a_origin.z - b_origin.z) < a_extent.z + b_extent.z - 2.0
    )


records = []
flags = []
for actor in sorted(targets, key=lambda item: item.get_actor_label()):
    origin, extent = actor.get_actor_bounds(False)
    bottom = origin.z - extent.z
    location = actor.get_actor_location()
    hit = unreal.SystemLibrary.line_trace_single(
        world, unreal.Vector(location.x, location.y, bottom + 25.0), unreal.Vector(location.x, location.y, bottom - 100.0),
        unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, targets, unreal.DrawDebugTrace.NONE, True,
    )
    gap = None
    support = ""
    if hit is not None:
        data = hit.to_dict()
        if data.get("blocking_hit"):
            gap = bottom - data["location"].z
            support_actor = data.get("hit_actor")
            support = support_actor.get_actor_label() if support_actor else ""
    overlaps = [label for label, wall_origin, wall_extent in walls if intersects(origin, extent, wall_origin, wall_extent)]
    dimensions = extent * 2.0
    actor_flags = []
    if gap is None or abs(gap) > 5.0:
        actor_flags.append("support_gap")
    if overlaps:
        actor_flags.append("wall_overlap")
    if max(dimensions.x, dimensions.y) > 950.0 or dimensions.z > 325.0:
        actor_flags.append("oversize")
    record = {
        "label": actor.get_actor_label(), "support_actor": support,
        "support_gap_cm": round(gap, 3) if gap is not None else None,
        "wall_overlaps": overlaps,
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
report = common.write_json_report(config, "old_town_market_ground_debris_audit_v1.json", payload)
unreal.log("SUNSCAR_MARKET_GROUND_AUDIT actors=%d flagged=%d report=%s" % (len(targets), len(flags), report))
print("SUNSCAR_MARKET_GROUND_AUDIT", len(targets), len(flags), report)
