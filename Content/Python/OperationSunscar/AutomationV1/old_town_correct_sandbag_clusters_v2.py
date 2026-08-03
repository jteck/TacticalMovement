"""Dry-run-first orientation and terrain support correction for sandbag clusters."""

import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


FIX_TAG = unreal.Name("SunscarSandbagClusterCorrectionV2")

# Visual, collision, intended yaw, visual upright bottom offset from actor origin,
# collision origin offset from the corrected visual origin.
PAIRS = (
    ("QX_Sandbag_Detention_West_A", "COL_Sandbag_Detention_West_A", 0.0, 0.496, 40.504),
    ("QX_Sandbag_Detention_West_Return", "COL_Sandbag_Detention_West_Return", 90.0, 0.496, 40.504),
    ("QX_Square_Detention_West_End", "COL_QX_Square_Detention_West_End", 0.0, 0.014, 25.986),
    ("QX_Sandbag_Detention_East_A", "COL_Sandbag_Detention_East_A", 0.0, 0.496, 40.504),
    ("QX_Sandbag_Detention_East_Return", "COL_Sandbag_Detention_East_Return", 90.0, 0.496, 40.504),
    ("QX_Square_Detention_East_End", "COL_QX_Square_Detention_East_End", 180.0, 0.014, 25.986),
    ("QX_Square_North_East_End", "COL_QX_Square_North_East_End", 180.0, 0.014, 25.986),
)

config = common.load_config()
apply_requested = bool(config["execution"].get("apply_changes", False))
context = common.require_safe_context(config, write_requested=apply_requested)
world = common.editor_world()
actors = list(common.actor_subsystem().get_all_level_actors())
by_label = {actor.get_actor_label(): actor for actor in actors}
landscapes = [actor for actor in actors if "Landscape" in actor.get_class().get_name()]
non_landscapes = [actor for actor in actors if actor not in landscapes]


def terrain_z(x, y):
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
    result = hit.to_dict() if hit is not None else {}
    return result["location"].z if result.get("blocking_hit") else None


records = []
for visual_label, collision_label, yaw, bottom_offset, collision_offset in PAIRS:
    visual = by_label.get(visual_label)
    collision = by_label.get(collision_label)
    if visual is None or collision is None:
        raise RuntimeError("SUNSCAR_SANDBAG_V2_MISSING %s|%s" % (visual_label, collision_label))

    location = visual.get_actor_location()
    support_z = terrain_z(location.x, location.y)
    if support_z is None:
        raise RuntimeError("SUNSCAR_SANDBAG_V2_NO_TERRAIN " + visual_label)

    desired_visual_z = support_z + bottom_offset
    visual_delta_z = desired_visual_z - location.z
    desired_collision_z = desired_visual_z + collision_offset
    collision_location = collision.get_actor_location()
    collision_delta_z = desired_collision_z - collision_location.z

    if not (-160.0 <= visual_delta_z <= 10.0):
        raise RuntimeError("SUNSCAR_SANDBAG_V2_VISUAL_DELTA %s %.3f" % (visual_label, visual_delta_z))
    if not (-160.0 <= collision_delta_z <= 10.0):
        raise RuntimeError("SUNSCAR_SANDBAG_V2_COLLISION_DELTA %s %.3f" % (collision_label, collision_delta_z))

    record = {
        "visual_label": visual_label,
        "collision_label": collision_label,
        "intended_yaw": yaw,
        "terrain_support_z_cm": round(support_z, 3),
        "before_visual_location_z_cm": round(location.z, 3),
        "before_visual_rotation": {
            "pitch": round(visual.get_actor_rotation().pitch, 3),
            "yaw": round(visual.get_actor_rotation().yaw, 3),
            "roll": round(visual.get_actor_rotation().roll, 3),
        },
        "visual_delta_z_cm": round(visual_delta_z, 3),
        "collision_delta_z_cm": round(collision_delta_z, 3),
    }

    if apply_requested:
        visual.modify()
        visual.set_actor_rotation(unreal.Rotator(roll=0.0, pitch=0.0, yaw=yaw), False)
        visual.set_actor_location(
            unreal.Vector(location.x, location.y, desired_visual_z), False, False
        )
        collision.modify()
        collision.set_actor_rotation(unreal.Rotator(roll=0.0, pitch=0.0, yaw=yaw), False)
        collision.set_actor_location(
            unreal.Vector(collision_location.x, collision_location.y, desired_collision_z),
            False,
            False,
        )
        for actor in (visual, collision):
            if FIX_TAG not in list(actor.tags):
                actor.tags = list(actor.tags) + [FIX_TAG]
        after_origin, after_extent = visual.get_actor_bounds(False)
        record["after_visual_bottom_z_cm"] = round(after_origin.z - after_extent.z, 3)
        record["after_support_gap_cm"] = round((after_origin.z - after_extent.z) - support_z, 3)
        record["after_visual_rotation"] = {
            "pitch": round(visual.get_actor_rotation().pitch, 3),
            "yaw": round(visual.get_actor_rotation().yaw, 3),
            "roll": round(visual.get_actor_rotation().roll, 3),
        }
    records.append(record)

payload = {
    "schema_version": 2,
    "status": "apply_unsaved_complete" if apply_requested else "dry_run_complete",
    "context": context,
    "pair_count": len(records),
    "actor_count": len(records) * 2,
    "records": records,
    "changes_made": apply_requested,
    "level_saved": False,
}
name = "old_town_correct_sandbag_clusters_apply_v2.json" if apply_requested else "old_town_correct_sandbag_clusters_dry_run_v2.json"
report = common.write_json_report(config, name, payload)
unreal.log("SUNSCAR_SANDBAG_V2 mode=%s actors=%d report=%s" % ("APPLY_UNSAVED" if apply_requested else "DRY_RUN", len(records) * 2, report))
print("SUNSCAR_SANDBAG_V2", len(records) * 2, report)
