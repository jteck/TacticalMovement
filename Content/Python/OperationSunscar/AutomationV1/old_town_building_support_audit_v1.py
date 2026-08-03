"""Read-only support-gap audit for first-floor Old Town building slabs."""

import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


config = common.load_config()
context = common.require_safe_context(config, write_requested=False)
world = common.editor_world()
actors = list(common.actor_subsystem().get_all_level_actors())
building_actors = [actor for actor in actors if "CoreCategory_Building" in common.actor_tags(actor)]
floors = sorted(
    [
        actor
        for actor in building_actors
        if "_F1_Floor" in actor.get_actor_label()
        and common.actor_folder(actor).startswith("Sunscar/CorePlayable/Buildings/")
    ],
    key=lambda actor: actor.get_actor_label(),
)


def allowed_support(actor):
    if actor is None:
        return False
    label = actor.get_actor_label()
    tags = common.actor_tags(actor)
    folder = common.actor_folder(actor)
    class_name = actor.get_class().get_name()
    return (
        "Landscape" in class_name
        or "VisualGroundOverlay" in tags
        or folder.startswith("OldTown_GroundElevationPassV2/")
        or folder.startswith("OldTown_GroundSurfacePass/")
        or label.startswith("District_")
        or label.startswith("Ground_")
    )


records = []
flagged = []
for floor in floors:
    origin, extent = floor.get_actor_bounds(False)
    bottom_z = origin.z - extent.z
    hits = unreal.SystemLibrary.line_trace_multi(
        world,
        unreal.Vector(origin.x, origin.y, bottom_z - 0.1),
        unreal.Vector(origin.x, origin.y, bottom_z - 3000.0),
        unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
        True,
        building_actors,
        unreal.DrawDebugTrace.NONE,
        True,
    )
    support = None
    support_z = None
    for hit in hits or []:
        data = hit.to_dict()
        candidate = data.get("hit_actor")
        if data.get("blocking_hit") and allowed_support(candidate):
            support = candidate
            support_z = data["location"].z
            break
    gap = bottom_z - support_z if support_z is not None else None
    reasons = []
    if support_z is None:
        reasons.append("support_not_found")
    elif gap > 25.0:
        reasons.append("visible_support_gap")
    elif gap < -5.0:
        reasons.append("floor_below_support")
    record = {
        "label": floor.get_actor_label(),
        "folder": common.actor_folder(floor),
        "bottom_z_cm": round(bottom_z, 3),
        "support_z_cm": round(support_z, 3) if support_z is not None else None,
        "support_gap_cm": round(gap, 3) if gap is not None else None,
        "support_actor": support.get_actor_label() if support else "",
        "review_reasons": reasons,
        "package": floor.get_package().get_name(),
    }
    records.append(record)
    if reasons:
        flagged.append(record)

dirty = sorted(
    package.get_name()
    for package in list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
    + list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
)
payload = {
    "schema_version": 1,
    "status": "read_only_building_support_audit_complete",
    "context": context,
    "floor_count": len(records),
    "flagged_count": len(flagged),
    "records": records,
    "flagged": flagged,
    "dirty_packages": dirty,
    "changes_made": False,
}
report = common.write_json_report(config, "old_town_building_support_audit_v1.json", payload)
unreal.log("SUNSCAR_BUILDING_SUPPORT_AUDIT floors=%d flagged=%d report=%s" % (len(records), len(flagged), report))
print("SUNSCAR_BUILDING_SUPPORT_AUDIT", len(records), len(flagged), report)
