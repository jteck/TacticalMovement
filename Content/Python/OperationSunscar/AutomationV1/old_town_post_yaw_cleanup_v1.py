"""Dry-run-first cleanup of four precise post-yaw support/occlusion findings."""

import math
import os
import sys

import unreal

SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


MARKET_LABELS = (
    "OT_MARKET_SS_008_DECAL_003",
    "OT_MARKET_SS_008_GROUND_018",
    "OT_MARKET_SS_008_GROUND_039",
)
GRASS_LABEL = "OT_AUTO_SS_008_VEGETATION_014"
BLOCKER_LABEL = "OT_STORE_SS_008_TACTICAL_008"
FIX_TAG = unreal.Name("SunscarPostYawCleanupV1")
config = common.load_config()
apply_requested = bool(config["execution"].get("apply_changes", False))
context = common.require_safe_context(config, write_requested=apply_requested)
world = common.editor_world()
actors = list(common.actor_subsystem().get_all_level_actors())
by_label = {actor.get_actor_label(): actor for actor in actors}
landscapes = [actor for actor in actors if "Landscape" in actor.get_class().get_name()]
non_landscapes = [actor for actor in actors if actor not in landscapes]
targets = [by_label.get(label) for label in MARKET_LABELS + (GRASS_LABEL, BLOCKER_LABEL)]
if any(actor is None for actor in targets):
    raise RuntimeError("SUNSCAR_POST_YAW_CLEANUP_REFUSED missing_exact_actor")


def surface_z(x, y, ignored, start_z=100000.0, end_z=-100000.0):
    hit = unreal.SystemLibrary.line_trace_single(
        world, unreal.Vector(x, y, start_z), unreal.Vector(x, y, end_z),
        unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, ignored,
        unreal.DrawDebugTrace.NONE, True,
    )
    if hit is None:
        return None, ""
    data = hit.to_dict()
    if not data.get("blocking_hit"):
        return None, ""
    support_actor = data.get("hit_actor")
    return data["location"].z, support_actor.get_actor_label() if support_actor else ""


records = []
market_targets = [by_label[label] for label in MARKET_LABELS]
for actor in market_targets:
    origin, extent = actor.get_actor_bounds(False)
    bottom = origin.z - extent.z
    location = actor.get_actor_location()
    support, support_label = surface_z(location.x, location.y, market_targets, bottom + 25.0, bottom - 100.0)
    if support is None:
        raise RuntimeError("SUNSCAR_POST_YAW_CLEANUP_REFUSED no_market_support=%s" % actor.get_actor_label())
    delta = support - bottom
    if not (5.0 <= delta <= 8.0):
        raise RuntimeError("SUNSCAR_POST_YAW_CLEANUP_REFUSED market_delta=%s:%.3f" % (actor.get_actor_label(), delta))
    if apply_requested:
        actor.modify()
        actor.add_actor_world_offset(unreal.Vector(0.0, 0.0, delta), False, False)
        if FIX_TAG not in list(actor.tags):
            actor.tags = list(actor.tags) + [FIX_TAG]
    records.append({"label": actor.get_actor_label(), "action": "align_support", "delta_z_cm": round(delta, 3), "support_actor": support_label})

grass = by_label[GRASS_LABEL]
blocker = by_label[BLOCKER_LABEL]
grass_location = grass.get_actor_location()
blocker_location = blocker.get_actor_location()
dx, dy = grass_location.x - blocker_location.x, grass_location.y - blocker_location.y
length = math.sqrt(dx * dx + dy * dy)
if length < 1.0:
    dx, dy, length = -1.0, 0.0, 1.0
new_x = grass_location.x + dx / length * 150.0
new_y = grass_location.y + dy / length * 150.0
ignored = [
    actor for actor in actors
    if actor is grass
    or actor is blocker
    or actor.get_actor_label().startswith(("OT_AUTO_", "OT_FURN_", "OT_STORE_", "OT_MARKET_"))
    or "Roof" in actor.get_actor_label()
]
terrain, _terrain_label = surface_z(new_x, new_y, non_landscapes)
if terrain is None:
    raise RuntimeError("SUNSCAR_POST_YAW_CLEANUP_REFUSED no_grass_support")
support, support_label = surface_z(new_x, new_y, ignored + landscapes, terrain + 150.0, terrain - 100.0)
if support is None:
    support, support_label = terrain, "Landscape"
origin, extent = grass.get_actor_bounds(False)
bottom = origin.z - extent.z
delta_z = support - bottom
if abs(delta_z) > 25.0:
    raise RuntimeError("SUNSCAR_POST_YAW_CLEANUP_REFUSED grass_delta=%.3f" % delta_z)
if apply_requested:
    grass.modify()
    grass.add_actor_world_offset(unreal.Vector(new_x - grass_location.x, new_y - grass_location.y, delta_z), False, False)
    if FIX_TAG not in list(grass.tags):
        grass.tags = list(grass.tags) + [FIX_TAG]
records.append({
    "label": GRASS_LABEL, "action": "move_clear_of_crate", "blocker": BLOCKER_LABEL,
    "delta_x_cm": round(new_x - grass_location.x, 3), "delta_y_cm": round(new_y - grass_location.y, 3),
    "delta_z_cm": round(delta_z, 3), "support_actor": support_label,
})

payload = {
    "schema_version": 1, "status": "apply_unsaved_complete" if apply_requested else "dry_run_complete",
    "context": context, "actor_count": 4, "records": records,
    "changes_made": apply_requested, "level_saved": False,
}
name = "old_town_post_yaw_cleanup_apply_v1.json" if apply_requested else "old_town_post_yaw_cleanup_dry_run_v1.json"
report = common.write_json_report(config, name, payload)
unreal.log("SUNSCAR_POST_YAW_CLEANUP mode=%s actors=4 report=%s" % ("APPLY_UNSAVED" if apply_requested else "DRY_RUN", report))
print("SUNSCAR_POST_YAW_CLEANUP", 4, report)
