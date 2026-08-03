"""Raise the unsaved industrial-detail preview onto its actual visible support."""

import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


TAG = "SunscarOldTownIndustrialDetailV1"
EXPECTED_ACTORS = 51
ALLOWED_SUPPORT_TERMS = ("landscape", "floor", "ground_", "terrain", "yard", "road", "courtyard", "plaza")
config = common.load_config()
apply_requested = bool(config["execution"].get("apply_changes", False))
context = common.require_safe_context(config, write_requested=apply_requested)
world = common.editor_world()
actors = list(common.actor_subsystem().get_all_level_actors())
targets = [actor for actor in actors if TAG in common.actor_tags(actor)]
if len(targets) != EXPECTED_ACTORS:
    raise RuntimeError("SUNSCAR_INDUSTRIAL_DETAIL_SUPPORT_SCOPE actor_count=%d" % len(targets))

corrections = []
blockers = []
for actor in sorted(targets, key=lambda value: value.get_actor_label()):
    origin, extent = actor.get_actor_bounds(False)
    bottom_z = origin.z - extent.z
    hit = unreal.SystemLibrary.line_trace_single(
        world,
        unreal.Vector(origin.x, origin.y, bottom_z + 35.0),
        unreal.Vector(origin.x, origin.y, bottom_z - 300.0),
        unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
        True,
        targets,
        unreal.DrawDebugTrace.NONE,
        True,
    )
    result = hit.to_dict() if hit is not None else {}
    support_actor = result.get("hit_actor") if result.get("blocking_hit") else None
    support_label = support_actor.get_actor_label() if support_actor else ""
    support_z = result["location"].z if result.get("blocking_hit") else None
    if support_z is None:
        blockers.append({"label": actor.get_actor_label(), "reason": "support_trace_failed"})
        continue
    if not any(term in support_label.lower() for term in ALLOWED_SUPPORT_TERMS):
        blockers.append({"label": actor.get_actor_label(), "reason": "unexpected_support", "support_actor": support_label})
        continue
    gap = bottom_z - support_z
    if gap < -2.0 or gap > 2.0:
        corrections.append({
            "actor": actor,
            "label": actor.get_actor_label(),
            "support_actor": support_label,
            "before_gap_cm": round(gap, 3),
            "delta_z_cm": round(-gap, 3),
        })

if apply_requested and blockers:
    raise RuntimeError("SUNSCAR_INDUSTRIAL_DETAIL_SUPPORT_BLOCKED blockers=%d" % len(blockers))

if apply_requested:
    for item in corrections:
        item["actor"].add_actor_world_offset(unreal.Vector(0.0, 0.0, item["delta_z_cm"]), False, False)

payload = {
    "schema_version": 1,
    "status": "support_fix_unsaved_complete" if apply_requested else "support_fix_dry_run_complete",
    "context": context,
    "actor_count": len(targets),
    "correction_count": len(corrections),
    "blocker_count": len(blockers),
    "blockers": blockers,
    "corrections": [{key: value for key, value in item.items() if key != "actor"} for item in corrections],
    "changes_made": bool(apply_requested and corrections),
    "level_saved": False,
}
name = "old_town_industrial_detail_support_fix_apply_v1.json" if apply_requested else "old_town_industrial_detail_support_fix_dry_run_v1.json"
report = common.write_json_report(config, name, payload)
unreal.log(
    "SUNSCAR_INDUSTRIAL_DETAIL_SUPPORT mode=%s corrections=%d blockers=%d report=%s"
    % ("APPLY_UNSAVED" if apply_requested else "DRY_RUN", len(corrections), len(blockers), report)
)
print("SUNSCAR_INDUSTRIAL_DETAIL_SUPPORT", len(corrections), len(blockers), report)
