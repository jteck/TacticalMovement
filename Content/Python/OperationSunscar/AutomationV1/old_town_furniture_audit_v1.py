"""Read-only geometry audit for the unsaved Old Town furniture preview."""

import os
import sys

import unreal

SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


TAG = unreal.Name("SunscarOldTownFurnitureV1")
config = common.load_config()
context = common.require_safe_context(config, write_requested=False)
actor_system = common.actor_subsystem()
actors = list(actor_system.get_all_level_actors())
furniture = [actor for actor in actors if TAG in list(actor.tags)]
other = [actor for actor in actors if actor not in furniture]


def intersects(a_origin, a_extent, b_origin, b_extent, margin=2.0):
    return (
        abs(a_origin.x - b_origin.x) < max(0.0, a_extent.x + b_extent.x - margin)
        and abs(a_origin.y - b_origin.y) < max(0.0, a_extent.y + b_extent.y - margin)
        and abs(a_origin.z - b_origin.z) < max(0.0, a_extent.z + b_extent.z - margin)
    )


records = []
flags = []
for actor in sorted(furniture, key=lambda item: item.get_actor_label()):
    origin, extent = actor.get_actor_bounds(False)
    bottom = origin.z - extent.z
    location = actor.get_actor_location()
    tags = [str(tag) for tag in actor.tags]
    site = next((tag for tag in tags if tag.startswith("SS_")), "")
    floor_hits = []
    wall_hits = []
    prop_hits = []
    for candidate in other:
        label = candidate.get_actor_label()
        if site and site not in label:
            continue
        candidate_origin, candidate_extent = candidate.get_actor_bounds(False)
        if not intersects(origin, extent, candidate_origin, candidate_extent):
            continue
        if "Floor" in label:
            floor_hits.append(label)
        elif "Wall" in label or "Parapet" in label:
            wall_hits.append(label)
        elif not label.startswith("Ground_") and not label.startswith("Landscape"):
            prop_hits.append(label)

    trace = unreal.SystemLibrary.line_trace_single(
        common.editor_world(),
        unreal.Vector(location.x, location.y, bottom + 25.0),
        unreal.Vector(location.x, location.y, bottom - 100.0),
        unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
        True,
        furniture,
        unreal.DrawDebugTrace.NONE,
        True,
    )
    support_gap = None
    support_label = ""
    if trace is not None:
        result = trace.to_dict()
        if result.get("blocking_hit"):
            support_gap = bottom - result["location"].z
            support_actor = result.get("hit_actor")
            support_label = support_actor.get_actor_label() if support_actor else ""

    dimensions = extent * 2.0
    actor_flags = []
    if support_gap is None or abs(support_gap) > 4.0:
        actor_flags.append("support_gap")
    if wall_hits:
        actor_flags.append("wall_overlap")
    if max(dimensions.x, dimensions.y) > 650.0 or dimensions.z > 375.0:
        actor_flags.append("oversize")
    record = {
        "label": actor.get_actor_label(),
        "site_id": site,
        "location_cm": {"x": round(location.x, 3), "y": round(location.y, 3), "z": round(location.z, 3)},
        "dimensions_cm": {"x": round(dimensions.x, 3), "y": round(dimensions.y, 3), "z": round(dimensions.z, 3)},
        "bottom_z_cm": round(bottom, 3),
        "support_actor": support_label,
        "support_gap_cm": round(support_gap, 3) if support_gap is not None else None,
        "floor_overlaps": floor_hits,
        "wall_overlaps": wall_hits,
        "other_overlaps": prop_hits,
        "flags": actor_flags,
    }
    records.append(record)
    if actor_flags:
        flags.append(record)

payload = {
    "schema_version": 1,
    "status": "read_only_complete",
    "context": context,
    "actor_count": len(furniture),
    "flagged_count": len(flags),
    "records": records,
    "flags": flags,
    "changes_made": False,
    "level_saved": False,
}
report = common.write_json_report(config, "old_town_furniture_audit_v1.json", payload)
unreal.log("SUNSCAR_FURNITURE_AUDIT actors=%d flagged=%d report=%s" % (len(furniture), len(flags), report))
print("SUNSCAR_FURNITURE_AUDIT", len(furniture), len(flags), report)
