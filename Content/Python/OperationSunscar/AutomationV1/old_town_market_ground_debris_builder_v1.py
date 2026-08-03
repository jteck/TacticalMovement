"""Dry-run-first exterior ground and asphalt-debris pass for SS_008."""

import os
import sys

import unreal

SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


TAG = unreal.Name("SunscarOldTownMarketGroundDebrisV1")
FOLDER = "OldTown_AutomationPreview/MarketGroundDebrisV1/SS_008"
ALLOWED_BOMS = {"OT_DECAL_003", "OT_GROUND_001", "OT_GROUND_004"}
config = common.load_config()
apply_requested = bool(config["execution"].get("apply_changes", False))
context = common.require_safe_context(config, write_requested=apply_requested)
plan = common.read_csv(common.planning_file(config, "resolved_plan_file"))
registry = common.read_json(common.planning_file(config, "final_registry_file"))
actor_system = common.actor_subsystem()
world = common.editor_world()
actors = list(actor_system.get_all_level_actors())
existing = [actor for actor in actors if TAG in list(actor.tags)]
already_placed_candidate_ids = {
    actor.get_actor_label()[len("OT_AUTO_"):]
    for actor in actors
    if actor.get_actor_label().startswith("OT_AUTO_")
}
records = [
    row for row in plan
    if row["site_id"] == "SS_008"
    and row["bom_id"] in ALLOWED_BOMS
    and row["candidate_id"] not in already_placed_candidate_ids
]
landscapes = [actor for actor in actors if "Landscape" in actor.get_class().get_name()]
non_landscapes = [actor for actor in actors if actor not in landscapes]


def terrain_z(x, y):
    hit = unreal.SystemLibrary.line_trace_single(
        world, unreal.Vector(x, y, 100000.0), unreal.Vector(x, y, -100000.0),
        unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, non_landscapes,
        unreal.DrawDebugTrace.NONE, True,
    )
    if hit is None:
        return None
    data = hit.to_dict()
    return data["location"].z if data.get("blocking_hit") else None


def exterior_support(x, y):
    z = terrain_z(x, y)
    if z is None:
        return None, ""
    ignored = landscapes + existing + [actor for actor in actors if "Roof" in actor.get_actor_label()]
    hit = unreal.SystemLibrary.line_trace_single(
        world, unreal.Vector(x, y, z + 150.0), unreal.Vector(x, y, z - 100.0),
        unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, ignored,
        unreal.DrawDebugTrace.NONE, True,
    )
    if hit is not None:
        data = hit.to_dict()
        if data.get("blocking_hit"):
            support_actor = data.get("hit_actor")
            label = support_actor.get_actor_label() if support_actor else ""
            allowed = label.startswith("Ground_") or label.startswith("MarketRoute_") or label.startswith("CourtyardConnector_")
            if allowed and data["location"].z - z <= 120.0:
                return data["location"].z, label
    return z, "Landscape"


ready = []
blockers = []
for row in records:
    item = dict(row)
    path = common.safe_asset_ref_to_path(item["planned_asset_ref"], registry)
    item["resolved_asset_path"] = path
    asset = unreal.EditorAssetLibrary.load_asset(path) if path else None
    if not isinstance(asset, unreal.StaticMesh) or not common.asset_path_allowed(config, path):
        item["reason"] = "missing_or_disallowed_static_mesh"
        blockers.append(item)
        continue
    scale = float(item["scale"])
    bounds = asset.get_bounds()
    dimensions = bounds.box_extent * (2.0 * scale)
    item["dimensions_cm"] = {"x": round(dimensions.x, 3), "y": round(dimensions.y, 3), "z": round(dimensions.z, 3)}
    if max(dimensions.x, dimensions.y) > 900.0 or dimensions.z > 300.0:
        item["reason"] = "asset_dimensions_require_review"
        blockers.append(item)
        continue
    x, y = float(item["x_m"]) * 100.0, float(item["y_m"]) * 100.0
    support_z, support_label = exterior_support(x, y)
    if support_z is None:
        item["reason"] = "exterior_support_not_found"
        blockers.append(item)
        continue
    local_min_z = (bounds.origin.z - bounds.box_extent.z) * scale
    item["support_actor"] = support_label
    item["support_z_cm"] = round(support_z, 3)
    item["planned_location_cm"] = {"x": round(x, 3), "y": round(y, 3), "z": round(support_z - local_min_z, 3)}
    item["reason"] = ""
    ready.append((item, asset))

if apply_requested and blockers:
    raise RuntimeError("SUNSCAR_MARKET_GROUND_APPLY_BLOCKED blockers=%d" % len(blockers))
if apply_requested and existing:
    raise RuntimeError("SUNSCAR_MARKET_GROUND_DUPLICATE existing=%d" % len(existing))
created = []
if apply_requested:
    for item, asset in ready:
        loc, scale = item["planned_location_cm"], float(item["scale"])
        actor = actor_system.spawn_actor_from_object(asset, unreal.Vector(loc["x"], loc["y"], loc["z"]), unreal.Rotator(roll=0.0, pitch=0.0, yaw=float(item["yaw_deg"])), transient=False)
        actor.set_actor_scale3d(unreal.Vector(scale, scale, scale))
        origin, extent = actor.get_actor_bounds(False)
        actor.add_actor_world_offset(unreal.Vector(0.0, 0.0, item["support_z_cm"] - (origin.z - extent.z)), False, False)
        actor.set_actor_label("OT_MARKET_%s" % item["candidate_id"])
        actor.tags = [TAG, unreal.Name("SS_008"), unreal.Name(item["bom_id"]), unreal.Name("UnreviewedAutomationPlacement")]
        actor.set_folder_path(unreal.Name(FOLDER))
        actor.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        created.append(actor.get_actor_label())

payload = {
    "schema_version": 1, "status": "apply_unsaved_preview_complete" if apply_requested else "dry_run_complete",
    "context": context, "record_count": len(records), "ready_count": len(ready), "blocker_count": len(blockers),
    "created_actor_count": len(created), "created_actor_labels": created,
    "ready": [item for item, _asset in ready], "blockers": blockers,
    "changes_made": bool(created), "level_saved": False,
}
name = "old_town_market_ground_debris_apply_preview_v1.json" if apply_requested else "old_town_market_ground_debris_dry_run_v1.json"
report = common.write_json_report(config, name, payload)
unreal.log("SUNSCAR_MARKET_GROUND mode=%s ready=%d blockers=%d created=%d report=%s" % ("APPLY_UNSAVED" if apply_requested else "DRY_RUN", len(ready), len(blockers), len(created), report))
print("SUNSCAR_MARKET_GROUND", len(ready), len(blockers), len(created), report)
