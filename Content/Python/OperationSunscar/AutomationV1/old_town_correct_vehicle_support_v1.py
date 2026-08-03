"""Dry-run-first support correction for four replaced vehicle proxies."""

import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


TAG = "SunscarOldTownVehicleReplacementV1"
FIX_TAG = unreal.Name("SunscarVehicleSupportFixV1")
TARGET_LABELS = {
    "Salvage_Vehicle_02",
    "Salvage_Vehicle_03",
    "MotorPool_Vehicle_A",
    "MotorPool_Vehicle_B",
}
config = common.load_config()
apply_requested = bool(config["execution"].get("apply_changes", False))
context = common.require_safe_context(config, write_requested=apply_requested)
world = common.editor_world()
actors = list(common.actor_subsystem().get_all_level_actors())
vehicles = [actor for actor in actors if TAG in common.actor_tags(actor)]
targets = [actor for actor in vehicles if actor.get_actor_label() in TARGET_LABELS]
if len(vehicles) != 5 or len(targets) != 4:
    raise RuntimeError("SUNSCAR_VEHICLE_SUPPORT_SCOPE vehicles=%d targets=%d" % (len(vehicles), len(targets)))

records = []
for actor in sorted(targets, key=lambda value: value.get_actor_label()):
    origin, extent = actor.get_actor_bounds(False)
    bottom_z = origin.z - extent.z
    hit = unreal.SystemLibrary.line_trace_single(
        world,
        unreal.Vector(origin.x, origin.y, bottom_z + 40.0),
        unreal.Vector(origin.x, origin.y, bottom_z - 500.0),
        unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
        True,
        vehicles,
        unreal.DrawDebugTrace.NONE,
        True,
    )
    result = hit.to_dict() if hit is not None else {}
    if not result.get("blocking_hit"):
        raise RuntimeError("SUNSCAR_VEHICLE_SUPPORT_TRACE_FAILED " + actor.get_actor_label())
    support_z = result["location"].z
    delta_z = support_z - bottom_z
    if not (3.0 <= delta_z <= 25.0):
        raise RuntimeError("SUNSCAR_VEHICLE_SUPPORT_DELTA_REFUSED %s %.3f" % (actor.get_actor_label(), delta_z))
    record = {
        "label": actor.get_actor_label(),
        "before_bottom_z_cm": round(bottom_z, 3),
        "support_z_cm": round(support_z, 3),
        "delta_z_cm": round(delta_z, 3),
        "support_actor": result.get("hit_actor").get_actor_label() if result.get("hit_actor") else "",
    }
    if apply_requested:
        location = actor.get_actor_location()
        actor.modify()
        actor.set_actor_location(unreal.Vector(location.x, location.y, location.z + delta_z), False, False)
        if FIX_TAG not in list(actor.tags):
            actor.tags = list(actor.tags) + [FIX_TAG]
        after_origin, after_extent = actor.get_actor_bounds(False)
        record["after_bottom_z_cm"] = round(after_origin.z - after_extent.z, 3)
        record["after_support_gap_cm"] = round((after_origin.z - after_extent.z) - support_z, 3)
    records.append(record)

payload = {
    "schema_version": 1,
    "status": "apply_unsaved_complete" if apply_requested else "dry_run_complete",
    "context": context,
    "actor_count": len(records),
    "records": records,
    "changes_made": apply_requested,
    "level_saved": False,
}
filename = (
    "old_town_correct_vehicle_support_apply_v1.json"
    if apply_requested
    else "old_town_correct_vehicle_support_dry_run_v1.json"
)
report = common.write_json_report(config, filename, payload)
unreal.log("SUNSCAR_VEHICLE_SUPPORT mode=%s actors=%d report=%s" % ("APPLY_UNSAVED" if apply_requested else "DRY_RUN", len(records), report))
print("SUNSCAR_VEHICLE_SUPPORT", len(records), report)
