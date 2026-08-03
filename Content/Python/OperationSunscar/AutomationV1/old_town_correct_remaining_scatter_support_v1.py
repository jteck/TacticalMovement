"""Dry-run-first support correction for the single remaining-scatter grass overlap."""

import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


TARGET_LABEL = "OT_REMAIN_SS_020_VEGETATION_003"
TAG = "SunscarOldTownRemainingScatterV1"
FIX_TAG = unreal.Name("SunscarRemainingScatterSupportFixV1")
config = common.load_config()
apply_requested = bool(config["execution"].get("apply_changes", False))
context = common.require_safe_context(config, write_requested=apply_requested)
world = common.editor_world()
actors = list(common.actor_subsystem().get_all_level_actors())
targets = [actor for actor in actors if TAG in common.actor_tags(actor)]
by_label = {actor.get_actor_label(): actor for actor in targets}
actor = by_label.get(TARGET_LABEL)
if actor is None or len(targets) != 84:
    raise RuntimeError("SUNSCAR_REMAINING_SUPPORT_SCOPE actor_count=%d target=%s" % (len(targets), bool(actor)))

origin, extent = actor.get_actor_bounds(False)
bottom_z = origin.z - extent.z
hit = unreal.SystemLibrary.line_trace_single(
    world,
    unreal.Vector(origin.x, origin.y, bottom_z + 50.0),
    unreal.Vector(origin.x, origin.y, bottom_z - 500.0),
    unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
    True,
    targets,
    unreal.DrawDebugTrace.NONE,
    True,
)
result = hit.to_dict() if hit is not None else {}
if not result.get("blocking_hit"):
    raise RuntimeError("SUNSCAR_REMAINING_SUPPORT_TRACE_FAILED")
support_z = result["location"].z
delta_z = support_z - bottom_z
if not (15.0 <= delta_z <= 25.0):
    raise RuntimeError("SUNSCAR_REMAINING_SUPPORT_DELTA_REFUSED %.3f" % delta_z)

record = {
    "label": TARGET_LABEL,
    "before_location_z_cm": round(actor.get_actor_location().z, 3),
    "before_bottom_z_cm": round(bottom_z, 3),
    "support_z_cm": round(support_z, 3),
    "delta_z_cm": round(delta_z, 3),
    "support_actor": result.get("hit_actor").get_actor_label() if result.get("hit_actor") else "",
}
if apply_requested:
    location = actor.get_actor_location()
    actor.modify()
    actor.set_actor_location(
        unreal.Vector(location.x, location.y, location.z + delta_z),
        False,
        False,
    )
    if FIX_TAG not in list(actor.tags):
        actor.tags = list(actor.tags) + [FIX_TAG]
    after_origin, after_extent = actor.get_actor_bounds(False)
    record["after_location_z_cm"] = round(actor.get_actor_location().z, 3)
    record["after_bottom_z_cm"] = round(after_origin.z - after_extent.z, 3)
    record["after_support_gap_cm"] = round((after_origin.z - after_extent.z) - support_z, 3)

payload = {
    "schema_version": 1,
    "status": "apply_unsaved_complete" if apply_requested else "dry_run_complete",
    "context": context,
    "record": record,
    "changes_made": apply_requested,
    "level_saved": False,
}
filename = (
    "old_town_correct_remaining_scatter_support_apply_v1.json"
    if apply_requested
    else "old_town_correct_remaining_scatter_support_dry_run_v1.json"
)
report = common.write_json_report(config, filename, payload)
unreal.log("SUNSCAR_REMAINING_SUPPORT mode=%s report=%s" % ("APPLY_UNSAVED" if apply_requested else "DRY_RUN", report))
print("SUNSCAR_REMAINING_SUPPORT", report)
