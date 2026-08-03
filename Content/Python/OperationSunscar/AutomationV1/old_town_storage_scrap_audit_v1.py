"""Read-only geometry audit for the Old Town storage and scrap preview."""

import os
import sys

import unreal

SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


TAG = unreal.Name("SunscarOldTownStorageScrapV1")
config = common.load_config()
context = common.require_safe_context(config, write_requested=False)
world = common.editor_world()
all_actors = list(common.actor_subsystem().get_all_level_actors())
targets = [actor for actor in all_actors if TAG in list(actor.tags)]
others = [actor for actor in all_actors if actor not in targets]


def intersects(a_origin, a_extent, b_origin, b_extent, margin=2.0):
    return all(
        abs(a - b) < max(0.0, ae + be - margin)
        for a, ae, b, be in (
            (a_origin.x, a_extent.x, b_origin.x, b_extent.x),
            (a_origin.y, a_extent.y, b_origin.y, b_extent.y),
            (a_origin.z, a_extent.z, b_origin.z, b_extent.z),
        )
    )


records = []
flags = []
for actor in sorted(targets, key=lambda item: item.get_actor_label()):
    origin, extent = actor.get_actor_bounds(False)
    bottom = origin.z - extent.z
    location = actor.get_actor_location()
    site = next((str(tag) for tag in actor.tags if str(tag).startswith("SS_")), "")
    walls = []
    for other in others:
        label = other.get_actor_label()
        if site not in label or ("Wall" not in label and "Parapet" not in label):
            continue
        other_origin, other_extent = other.get_actor_bounds(False)
        if intersects(origin, extent, other_origin, other_extent):
            walls.append(label)
    hit = unreal.SystemLibrary.line_trace_single(
        world,
        unreal.Vector(location.x, location.y, bottom + 25.0),
        unreal.Vector(location.x, location.y, bottom - 100.0),
        unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
        True,
        targets,
        unreal.DrawDebugTrace.NONE,
        True,
    )
    gap = None
    support = ""
    if hit is not None:
        result = hit.to_dict()
        if result.get("blocking_hit"):
            gap = bottom - result["location"].z
            support_actor = result.get("hit_actor")
            support = support_actor.get_actor_label() if support_actor else ""
    actor_flags = []
    if gap is None or abs(gap) > 4.0:
        actor_flags.append("support_gap")
    if walls:
        actor_flags.append("wall_overlap")
    dimensions = extent * 2.0
    if max(dimensions.x, dimensions.y) > 700.0 or dimensions.z > 425.0:
        actor_flags.append("oversize")
    record = {
        "label": actor.get_actor_label(),
        "site_id": site,
        "support_actor": support,
        "support_gap_cm": round(gap, 3) if gap is not None else None,
        "wall_overlaps": walls,
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
report = common.write_json_report(config, "old_town_storage_scrap_audit_v1.json", payload)
unreal.log("SUNSCAR_STORAGE_SCRAP_AUDIT actors=%d flagged=%d report=%s" % (len(targets), len(flags), report))
print("SUNSCAR_STORAGE_SCRAP_AUDIT", len(targets), len(flags), report)
