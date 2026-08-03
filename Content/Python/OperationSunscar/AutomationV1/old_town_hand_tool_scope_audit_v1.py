"""Read-only bounds, support and clearance resolution for deferred Salvage Yard tools."""

import math
import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


config = common.load_config()
context = common.require_safe_context(config, write_requested=False)
plan = common.read_csv(common.planning_file(config, "resolved_plan_file"))
registry = common.read_json(common.planning_file(config, "final_registry_file"))
world = common.editor_world()
actors = list(common.actor_subsystem().get_all_level_actors())
rows = [row for row in plan if row.get("bom_id") == "OT_SCRAP_004" and row.get("site_id") == "SS_014"]


def collision_enabled(actor):
    component = getattr(actor, "static_mesh_component", None)
    if component is None:
        return False
    try:
        return "NO_COLLISION" not in str(component.get_collision_enabled())
    except Exception:
        return False


ignored_terms = (
    "landscape", "groundoverlay", "ground_overlay", "groundpatch", "ground_patch",
    "debris", "rubble", "grass", "rock", "damage", "label", "marker", "spawn",
    "objective", "sign", "facadeconduit",
)
blockers = []
for actor in actors:
    search = " ".join([actor.get_actor_label(), common.actor_folder(actor), common.actor_mesh_path(actor)]).lower()
    if any(term in search for term in ignored_terms) or not collision_enabled(actor):
        continue
    try:
        origin, extent = actor.get_actor_bounds(False)
    except Exception:
        continue
    if extent.z > 20.0 and (extent.x > 35.0 or extent.y > 35.0):
        blockers.append((actor.get_actor_label(), origin, extent))


def terrain_z(x, y):
    ignore = [actor for actor in actors if "Landscape" not in actor.get_class().get_name()]
    hit = unreal.SystemLibrary.line_trace_single(
        world,
        unreal.Vector(x, y, 100000.0),
        unreal.Vector(x, y, -100000.0),
        unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
        True,
        ignore,
        unreal.DrawDebugTrace.NONE,
        True,
    )
    result = hit.to_dict() if hit is not None else {}
    return result["location"].z if result.get("blocking_hit") else None


def nearest_blocker(x, y, half_x, half_y):
    candidates = []
    for label, origin, extent in blockers:
        dx = max(abs(x - origin.x) - extent.x - half_x, 0.0)
        dy = max(abs(y - origin.y) - extent.y - half_y, 0.0)
        candidates.append((math.hypot(dx, dy), label))
    candidates.sort()
    return candidates[0] if candidates else (None, "")


mesh_records = {}
candidate_records = []
for row in rows:
    asset_path = common.safe_asset_ref_to_path(row["planned_asset_ref"], registry)
    asset = unreal.EditorAssetLibrary.load_asset(asset_path) if common.asset_path_allowed(config, asset_path) else None
    if not isinstance(asset, unreal.StaticMesh):
        candidate_records.append({"candidate_id": row["candidate_id"], "status": "asset_missing_or_invalid", "asset_path": asset_path})
        continue
    bounds = asset.get_bounds()
    mesh_records[asset_path] = {
        "origin_cm": {"x": round(bounds.origin.x, 3), "y": round(bounds.origin.y, 3), "z": round(bounds.origin.z, 3)},
        "dimensions_cm_unscaled": {
            "x": round(bounds.box_extent.x * 2.0, 3),
            "y": round(bounds.box_extent.y * 2.0, 3),
            "z": round(bounds.box_extent.z * 2.0, 3),
        },
    }
    scale = float(row["scale"])
    x, y = float(row["x_m"]) * 100.0, float(row["y_m"]) * 100.0
    dims = bounds.box_extent * (2.0 * scale)
    support = terrain_z(x, y)
    clearance, blocker = nearest_blocker(x, y, dims.x * 0.5, dims.y * 0.5)
    candidate_records.append({
        "candidate_id": row["candidate_id"],
        "cluster_id": row["cluster_id"],
        "asset_path": asset_path,
        "asset_kind": "shovel" if "Shovel" in asset_path else "support_stand",
        "x_cm": round(x, 3),
        "y_cm": round(y, 3),
        "terrain_support_z_cm": round(support, 3) if support is not None else None,
        "yaw_deg": float(row["yaw_deg"]),
        "scale": scale,
        "scaled_dimensions_cm_default_rotation": {"x": round(dims.x, 3), "y": round(dims.y, 3), "z": round(dims.z, 3)},
        "nearest_collision_clearance_cm": round(clearance, 3) if clearance is not None else None,
        "nearest_collision_actor": blocker,
        "status": "resolved" if support is not None else "support_failed",
    })

payload = {
    "schema_version": 1,
    "status": "read_only_scope_audit_complete",
    "context": context,
    "planned_record_count": len(rows),
    "resolved_record_count": len([row for row in candidate_records if row.get("status") == "resolved"]),
    "mesh_records": mesh_records,
    "candidates": candidate_records,
    "changes_made": False,
}
report = common.write_json_report(config, "old_town_hand_tool_scope_audit_v1.json", payload)
unreal.log("SUNSCAR_HAND_TOOL_SCOPE planned=%d resolved=%d report=%s" % (len(rows), payload["resolved_record_count"], report))
print("SUNSCAR_HAND_TOOL_SCOPE", len(rows), payload["resolved_record_count"], report)
