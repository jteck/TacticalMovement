"""Dry-run-first bounded Salvage Yard hand-tool and support-stand placement."""

import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


TAG = unreal.Name("SunscarOldTownHandToolV1")
FOLDER = "OldTown_ArtDraft/HandToolsV1/SS_014"
SELECTED_IDS = {
    "SS_014_INDUSTRIAL_011",
    "SS_014_INDUSTRIAL_016",
    "SS_014_INDUSTRIAL_024",
    "SS_014_INDUSTRIAL_032",
    "SS_014_INDUSTRIAL_045",
    "SS_014_INDUSTRIAL_051",
    "SS_014_INDUSTRIAL_054",
    "SS_014_INDUSTRIAL_055",
    "SS_014_INDUSTRIAL_063",
}

config = common.load_config()
apply_requested = bool(config["execution"].get("apply_changes", False))
context = common.require_safe_context(config, write_requested=apply_requested)
plan = common.read_csv(common.planning_file(config, "resolved_plan_file"))
registry = common.read_json(common.planning_file(config, "final_registry_file"))
actor_system = common.actor_subsystem()
world = common.editor_world()
actors = list(actor_system.get_all_level_actors())
existing = [actor for actor in actors if TAG in list(actor.tags)]
if apply_requested and existing:
    raise RuntimeError("SUNSCAR_HAND_TOOL_DUPLICATE existing=%d" % len(existing))

rows = [row for row in plan if row.get("candidate_id") in SELECTED_IDS]
rows.sort(key=lambda row: row["candidate_id"])
if len(rows) != len(SELECTED_IDS):
    raise RuntimeError("SUNSCAR_HAND_TOOL_PLAN_DRIFT expected=%d actual=%d" % (len(SELECTED_IDS), len(rows)))

trace_ignore = [actor for actor in actors if "Landscape" not in actor.get_class().get_name()]


def terrain_z(x, y):
    hit = unreal.SystemLibrary.line_trace_single(
        world,
        unreal.Vector(x, y, 100000.0),
        unreal.Vector(x, y, -100000.0),
        unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
        True,
        trace_ignore,
        unreal.DrawDebugTrace.NONE,
        True,
    )
    result = hit.to_dict() if hit is not None else {}
    return result["location"].z if result.get("blocking_hit") else None


ready = []
blockers = []
for row in rows:
    item = dict(row)
    path = common.safe_asset_ref_to_path(item["planned_asset_ref"], registry)
    asset = unreal.EditorAssetLibrary.load_asset(path) if common.asset_path_allowed(config, path) else None
    if not isinstance(asset, unreal.StaticMesh):
        blockers.append({"candidate_id": item["candidate_id"], "reason": "static_mesh_missing", "asset_path": path})
        continue
    scale = float(item["scale"])
    x, y = float(item["x_m"]) * 100.0, float(item["y_m"]) * 100.0
    support_z = terrain_z(x, y)
    if support_z is None:
        blockers.append({"candidate_id": item["candidate_id"], "reason": "landscape_support_not_found"})
        continue
    bounds = asset.get_bounds()
    local_min_z = (bounds.origin.z - bounds.box_extent.z) * scale
    kind = "shovel_flat" if "Shovel" in path else "support_stand_upright"
    ready.append({
        "candidate_id": item["candidate_id"],
        "site_id": item["site_id"],
        "asset_path": path,
        "asset_kind": kind,
        "asset": asset,
        "scale": scale,
        "yaw_deg": float(item["yaw_deg"]),
        "planned_location_cm": {
            "x": round(x, 3),
            "y": round(y, 3),
            "z": round(support_z - local_min_z, 3),
        },
        "landscape_support_z_cm": round(support_z, 3),
        "orientation_basis": "verified_mesh_bounds_default_rotation",
    })

if apply_requested and blockers:
    raise RuntimeError("SUNSCAR_HAND_TOOL_APPLY_BLOCKED blockers=%d" % len(blockers))

created = []
if apply_requested:
    for item in ready:
        loc = item["planned_location_cm"]
        actor = actor_system.spawn_actor_from_object(
            item["asset"],
            unreal.Vector(loc["x"], loc["y"], loc["z"]),
            unreal.Rotator(roll=0.0, pitch=0.0, yaw=item["yaw_deg"]),
            transient=False,
        )
        scale = item["scale"]
        actor.set_actor_scale3d(unreal.Vector(scale, scale, scale))
        origin, extent = actor.get_actor_bounds(False)
        actor.add_actor_world_offset(
            unreal.Vector(0.0, 0.0, item["landscape_support_z_cm"] - (origin.z - extent.z)),
            False,
            False,
        )
        actor.static_mesh_component.set_collision_profile_name("NoCollision")
        actor.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        actor.set_actor_label("OT_HANDTOOL_%s" % item["candidate_id"])
        actor.tags = [TAG, unreal.Name("SS_014"), unreal.Name("OT_SCRAP_004"), unreal.Name(item["candidate_id"]), unreal.Name(item["asset_kind"])]
        actor.set_folder_path(unreal.Name(FOLDER))
        created.append(actor.get_actor_label())

serial_ready = [{key: value for key, value in item.items() if key != "asset"} for item in ready]
payload = {
    "schema_version": 1,
    "status": "apply_unsaved_preview_complete" if apply_requested else "dry_run_complete",
    "context": context,
    "selected_count": len(ready),
    "blocker_count": len(blockers),
    "blockers": blockers,
    "selected": serial_ready,
    "created_actor_count": len(created),
    "created_actor_labels": created,
    "changes_made": bool(created),
    "level_saved": False,
    "collision_policy": "NoCollision decorative detail only",
}
name = "old_town_hand_tool_apply_preview_v1.json" if apply_requested else "old_town_hand_tool_dry_run_v1.json"
report = common.write_json_report(config, name, payload)
unreal.log("SUNSCAR_HAND_TOOL mode=%s selected=%d blockers=%d created=%d report=%s" % ("APPLY_UNSAVED" if apply_requested else "DRY_RUN", len(ready), len(blockers), len(created), report))
print("SUNSCAR_HAND_TOOL", len(ready), len(blockers), len(created), report)
