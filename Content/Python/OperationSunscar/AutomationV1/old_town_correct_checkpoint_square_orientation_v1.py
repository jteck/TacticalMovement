"""Dry-run-first orientation correction for the grounded checkpoint square end."""

import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


LABELS = ("QX_Square_Checkpoint_Gate_End", "COL_QX_Square_Checkpoint_Gate_End")
FIX_TAG = unreal.Name("SunscarCheckpointSquareOrientationV1")
config = common.load_config()
apply_requested = bool(config["execution"].get("apply_changes", False))
context = common.require_safe_context(config, write_requested=apply_requested)
by_label = {actor.get_actor_label(): actor for actor in common.actor_subsystem().get_all_level_actors()}
world = common.editor_world()
all_actors = list(common.actor_subsystem().get_all_level_actors())
landscapes = [actor for actor in all_actors if "Landscape" in actor.get_class().get_name()]
non_landscapes = [actor for actor in all_actors if actor not in landscapes]
visual = by_label.get(LABELS[0])
collision = by_label.get(LABELS[1])
if visual is None or collision is None:
    raise RuntimeError("SUNSCAR_CHECKPOINT_SQUARE_MISSING_PAIR")
visual_location = visual.get_actor_location()
hit = unreal.SystemLibrary.line_trace_single(
    world,
    unreal.Vector(visual_location.x, visual_location.y, 100000.0),
    unreal.Vector(visual_location.x, visual_location.y, -100000.0),
    unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
    True,
    non_landscapes,
    unreal.DrawDebugTrace.NONE,
    True,
)
hit_result = hit.to_dict() if hit is not None else {}
if not hit_result.get("blocking_hit"):
    raise RuntimeError("SUNSCAR_CHECKPOINT_SQUARE_NO_TERRAIN")
terrain_z = hit_result["location"].z
desired_visual_z = terrain_z + 0.014
desired_collision_z = desired_visual_z + 25.986
records = []
for label in LABELS:
    actor = by_label.get(label)
    if actor is None:
        raise RuntimeError("SUNSCAR_CHECKPOINT_SQUARE_MISSING " + label)
    before = actor.get_actor_rotation()
    record = {
        "label": label,
        "before": {"pitch": before.pitch, "yaw": before.yaw, "roll": before.roll},
        "after": {"pitch": 0.0, "yaw": 180.0, "roll": 0.0},
        "terrain_support_z_cm": round(terrain_z, 3),
        "before_location_z_cm": round(actor.get_actor_location().z, 3),
        "after_location_z_cm": round(desired_visual_z if label == LABELS[0] else desired_collision_z, 3),
    }
    if apply_requested:
        actor.modify()
        actor.set_actor_rotation(unreal.Rotator(roll=0.0, pitch=0.0, yaw=180.0), False)
        location = actor.get_actor_location()
        actor.set_actor_location(
            unreal.Vector(location.x, location.y, desired_visual_z if label == LABELS[0] else desired_collision_z),
            False,
            False,
        )
        if FIX_TAG not in list(actor.tags):
            actor.tags = list(actor.tags) + [FIX_TAG]
    records.append(record)

payload = {
    "schema_version": 1,
    "status": "apply_unsaved_complete" if apply_requested else "dry_run_complete",
    "context": context,
    "actor_count": 2,
    "records": records,
    "changes_made": apply_requested,
    "level_saved": False,
}
name = "old_town_checkpoint_square_orientation_apply_v1.json" if apply_requested else "old_town_checkpoint_square_orientation_dry_run_v1.json"
report = common.write_json_report(config, name, payload)
unreal.log("SUNSCAR_CHECKPOINT_SQUARE mode=%s report=%s" % ("APPLY_UNSAVED" if apply_requested else "DRY_RUN", report))
