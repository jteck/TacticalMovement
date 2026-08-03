"""Dry-run-first correction for the verified elevated checkpoint sandbag group."""

import os
import sys

import unreal

SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


PAIRS = (
    ("QX_Sandbag_Checkpoint_West_A", "COL_Sandbag_Checkpoint_West_A", 40.504),
    ("QX_Sandbag_Checkpoint_West_B", "COL_Sandbag_Checkpoint_West_B", 40.504),
    ("QX_Square_Checkpoint_West_End", "COL_QX_Square_Checkpoint_West_End", 25.986),
    ("QX_Square_Checkpoint_Gate_End", "COL_QX_Square_Checkpoint_Gate_End", 25.986),
)
FIX_TAG = unreal.Name("SunscarCheckpointSandbagGroundFixV1")
config = common.load_config()
apply_requested = bool(config["execution"].get("apply_changes", False))
context = common.require_safe_context(config, write_requested=apply_requested)
world = common.editor_world()
actors = list(common.actor_subsystem().get_all_level_actors())
by_label = {actor.get_actor_label(): actor for actor in actors}
landscapes = [actor for actor in actors if "Landscape" in actor.get_class().get_name()]
non_landscapes = [actor for actor in actors if actor not in landscapes]


def landscape_z(x, y):
    hit = unreal.SystemLibrary.line_trace_single(
        world,
        unreal.Vector(x, y, 100000.0),
        unreal.Vector(x, y, -100000.0),
        unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
        True,
        non_landscapes,
        unreal.DrawDebugTrace.NONE,
        True,
    )
    if hit is None:
        return None
    result = hit.to_dict()
    return result["location"].z if result.get("blocking_hit") else None


records = []
for visual_label, collision_label, collision_location_offset_z in PAIRS:
    visual = by_label.get(visual_label)
    collision = by_label.get(collision_label)
    if visual is None or collision is None:
        raise RuntimeError(
            "SUNSCAR_CHECKPOINT_GROUND_REFUSED missing_pair=%s|%s"
            % (visual_label, collision_label)
        )
    visual_origin, visual_extent = visual.get_actor_bounds(False)
    bottom_z = visual_origin.z - visual_extent.z
    location = visual.get_actor_location()
    support_z = landscape_z(location.x, location.y)
    if support_z is None:
        raise RuntimeError("SUNSCAR_CHECKPOINT_GROUND_REFUSED no_landscape=%s" % visual_label)
    delta_z = support_z - bottom_z
    if not ((-450.0 <= delta_z <= -250.0) or abs(delta_z) <= 4.0):
        raise RuntimeError(
            "SUNSCAR_CHECKPOINT_GROUND_REFUSED unexpected_delta=%s:%.3f"
            % (visual_label, delta_z)
        )
    desired_visual_location_z = location.z + delta_z
    collision_location = collision.get_actor_location()
    collision_delta_z = desired_visual_location_z + collision_location_offset_z - collision_location.z
    if not (-450.0 <= collision_delta_z <= 4.0):
        raise RuntimeError(
            "SUNSCAR_CHECKPOINT_GROUND_REFUSED unexpected_collision_delta=%s:%.3f"
            % (collision_label, collision_delta_z)
        )
    record = {
        "visual_label": visual_label,
        "collision_label": collision_label,
        "before_visual_bottom_z_cm": round(bottom_z, 3),
        "landscape_support_z_cm": round(support_z, 3),
        "delta_z_cm": round(delta_z, 3),
        "collision_delta_z_cm": round(collision_delta_z, 3),
    }
    if apply_requested:
        for actor, actor_delta_z in ((visual, delta_z), (collision, collision_delta_z)):
            actor.modify()
            actor.add_actor_world_offset(unreal.Vector(0.0, 0.0, actor_delta_z), False, False)
            if FIX_TAG not in list(actor.tags):
                actor.tags = list(actor.tags) + [FIX_TAG]
        after_origin, after_extent = visual.get_actor_bounds(False)
        record["after_visual_bottom_z_cm"] = round(after_origin.z - after_extent.z, 3)
        record["after_gap_cm"] = round((after_origin.z - after_extent.z) - support_z, 3)
    records.append(record)

payload = {
    "schema_version": 1,
    "status": "apply_unsaved_complete" if apply_requested else "dry_run_complete",
    "context": context,
    "pair_count": len(records),
    "actor_count": len(records) * 2,
    "records": records,
    "changes_made": apply_requested,
    "level_saved": False,
}
name = "old_town_ground_checkpoint_sandbags_apply_v1.json" if apply_requested else "old_town_ground_checkpoint_sandbags_dry_run_v1.json"
report = common.write_json_report(config, name, payload)
unreal.log(
    "SUNSCAR_CHECKPOINT_GROUND mode=%s actors=%d report=%s"
    % ("APPLY_UNSAVED" if apply_requested else "DRY_RUN", len(records) * 2, report)
)
print("SUNSCAR_CHECKPOINT_GROUND", len(records) * 2, report)
