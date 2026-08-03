"""Dry-run-first correction of positional Rotator misuse across Old Town automation actors."""

import os
import sys

import unreal

SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


GROUPS = (
    ("OT_AUTO_", unreal.Name("SunscarOldTownConnectedSliceAutomationV1"), 60, 0.0),
    ("OT_FURN_", unreal.Name("SunscarOldTownFurnitureV1"), 62, 0.0),
    ("OT_STORE_", unreal.Name("SunscarOldTownStorageScrapV1"), 22, 0.0),
    ("OT_UTIL_", unreal.Name("SunscarOldTownElectricalBoxesV1"), 3, 90.0),
    ("OT_MARKET_", unreal.Name("SunscarOldTownMarketGroundDebrisV1"), 24, 0.0),
)
EXPECTED_TOTAL = 171
FIX_TAG = unreal.Name("SunscarAutomationYawCorrectionV1")
config = common.load_config()
apply_requested = bool(config["execution"].get("apply_changes", False))
context = common.require_safe_context(config, write_requested=apply_requested)
plan = common.read_csv(common.planning_file(config, "resolved_plan_file"))
plan_by_id = {row["candidate_id"]: row for row in plan}
actors = list(common.actor_subsystem().get_all_level_actors())

targets = []
group_counts = {}
for prefix, tag, expected_count, desired_pitch in GROUPS:
    group = [
        actor for actor in actors
        if tag in list(actor.tags) and actor.get_actor_label().startswith(prefix)
    ]
    group_counts[prefix] = len(group)
    if len(group) != expected_count:
        raise RuntimeError(
            "SUNSCAR_YAW_FIX_REFUSED group=%s expected=%d actual=%d"
            % (prefix, expected_count, len(group))
        )
    targets.extend((actor, prefix, desired_pitch) for actor in group)
if len(targets) != EXPECTED_TOTAL:
    raise RuntimeError("SUNSCAR_YAW_FIX_REFUSED expected_total=%d actual=%d" % (EXPECTED_TOTAL, len(targets)))

records = []
for actor, prefix, desired_pitch in sorted(targets, key=lambda item: item[0].get_actor_label()):
    label = actor.get_actor_label()
    candidate_id = label[len(prefix):]
    row = plan_by_id.get(candidate_id)
    if row is None:
        raise RuntimeError("SUNSCAR_YAW_FIX_REFUSED missing_plan=%s" % candidate_id)
    desired_yaw = float(row["yaw_deg"])
    before_rotation = actor.get_actor_rotation()
    before_origin, before_extent = actor.get_actor_bounds(False)
    before_bottom = before_origin.z - before_extent.z
    record = {
        "label": label,
        "candidate_id": candidate_id,
        "before_rotation": {"roll": round(before_rotation.roll, 3), "pitch": round(before_rotation.pitch, 3), "yaw": round(before_rotation.yaw, 3)},
        "desired_rotation": {"roll": 0.0, "pitch": desired_pitch, "yaw": round(desired_yaw, 3)},
        "preserved_bottom_z_cm": round(before_bottom, 3),
    }
    if apply_requested:
        actor.modify()
        actor.set_actor_rotation(
            unreal.Rotator(roll=0.0, pitch=desired_pitch, yaw=desired_yaw),
            False,
        )
        after_origin, after_extent = actor.get_actor_bounds(False)
        actor.add_actor_world_offset(
            unreal.Vector(0.0, 0.0, before_bottom - (after_origin.z - after_extent.z)),
            False,
            False,
        )
        if FIX_TAG not in list(actor.tags):
            actor.tags = list(actor.tags) + [FIX_TAG]
        final_rotation = actor.get_actor_rotation()
        final_origin, final_extent = actor.get_actor_bounds(False)
        record["after_rotation"] = {"roll": round(final_rotation.roll, 3), "pitch": round(final_rotation.pitch, 3), "yaw": round(final_rotation.yaw, 3)}
        record["bottom_error_cm"] = round((final_origin.z - final_extent.z) - before_bottom, 3)
    records.append(record)

payload = {
    "schema_version": 1,
    "status": "apply_unsaved_complete" if apply_requested else "dry_run_complete",
    "context": context,
    "actor_count": len(targets),
    "group_counts": group_counts,
    "records": records,
    "changes_made": apply_requested,
    "level_saved": False,
}
name = "old_town_correct_automation_yaw_apply_v1.json" if apply_requested else "old_town_correct_automation_yaw_dry_run_v1.json"
report = common.write_json_report(config, name, payload)
unreal.log("SUNSCAR_YAW_FIX mode=%s actors=%d report=%s" % ("APPLY_UNSAVED" if apply_requested else "DRY_RUN", len(targets), report))
print("SUNSCAR_YAW_FIX", len(targets), report)
