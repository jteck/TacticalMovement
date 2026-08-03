"""Dry-run-first final support alignment for the storage and scrap preview."""

import os
import sys

import unreal

SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


TAG = unreal.Name("SunscarOldTownStorageScrapV1")
config = common.load_config()
apply_requested = bool(config["execution"].get("apply_changes", False))
context = common.require_safe_context(config, write_requested=apply_requested)
world = common.editor_world()
targets = [actor for actor in common.actor_subsystem().get_all_level_actors() if TAG in list(actor.tags)]
if len(targets) != 22:
    raise RuntimeError("SUNSCAR_STORAGE_ALIGN_REFUSED expected=22 actual=%d" % len(targets))

records = []
for actor in sorted(targets, key=lambda item: item.get_actor_label()):
    origin, extent = actor.get_actor_bounds(False)
    bottom = origin.z - extent.z
    location = actor.get_actor_location()
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
    if hit is None or not hit.to_dict().get("blocking_hit"):
        raise RuntimeError("SUNSCAR_STORAGE_ALIGN_REFUSED no_support=%s" % actor.get_actor_label())
    support_z = hit.to_dict()["location"].z
    delta = support_z - bottom
    if abs(delta) > 10.0:
        raise RuntimeError("SUNSCAR_STORAGE_ALIGN_REFUSED large_delta=%s:%.3f" % (actor.get_actor_label(), delta))
    if apply_requested and abs(delta) > 0.25:
        actor.modify()
        actor.add_actor_world_offset(unreal.Vector(0.0, 0.0, delta), False, False)
    records.append({"label": actor.get_actor_label(), "delta_z_cm": round(delta, 3)})

payload = {
    "schema_version": 1,
    "status": "apply_unsaved_complete" if apply_requested else "dry_run_complete",
    "context": context,
    "actor_count": len(targets),
    "adjustment_count": len([record for record in records if abs(record["delta_z_cm"]) > 0.25]),
    "records": records,
    "changes_made": apply_requested,
    "level_saved": False,
}
name = "old_town_align_storage_scrap_support_apply_v1.json" if apply_requested else "old_town_align_storage_scrap_support_dry_run_v1.json"
report = common.write_json_report(config, name, payload)
unreal.log("SUNSCAR_STORAGE_ALIGN mode=%s adjustments=%d report=%s" % ("APPLY_UNSAVED" if apply_requested else "DRY_RUN", payload["adjustment_count"], report))
print("SUNSCAR_STORAGE_ALIGN", payload["adjustment_count"], report)
