"""Dry-run-first placement of resolved Epic storage crates and junkyard scrap."""

import os
import sys

import unreal

SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


TAG = unreal.Name("SunscarOldTownStorageScrapV1")
FOLDER = "OldTown_AutomationPreview/StorageScrapV1"
ALLOWED_BOMS = {"OT_TAC_005", "OT_SCRAP_006"}
config = common.load_config()
apply_requested = bool(config["execution"].get("apply_changes", False))
context = common.require_safe_context(config, write_requested=apply_requested)
plan = common.read_csv(common.planning_file(config, "resolved_plan_file"))
registry = common.read_json(common.planning_file(config, "final_registry_file"))
sites = set(config["connected_slice_sites"])
records = [row for row in plan if row["site_id"] in sites and row["bom_id"] in ALLOWED_BOMS]
actor_system = common.actor_subsystem()
world = common.editor_world()
actors = list(actor_system.get_all_level_actors())
landscapes = [actor for actor in actors if "Landscape" in actor.get_class().get_name()]
non_landscapes = [actor for actor in actors if actor not in landscapes]
existing = [actor for actor in actors if TAG in list(actor.tags)]


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
    if hit is None:
        return None
    result = hit.to_dict()
    return result["location"].z if result.get("blocking_hit") else None


floor_bounds = {}
for site in sites:
    candidates = []
    for actor in actors:
        label = actor.get_actor_label()
        if site in label and "Floor" in label:
            origin, extent = actor.get_actor_bounds(False)
            candidates.append((origin.z + extent.z, label, origin, extent))
    floor_bounds[site] = candidates


def support_for(site, x, y):
    containing = []
    for top_z, label, origin, extent in floor_bounds.get(site, []):
        if abs(x - origin.x) <= extent.x + 10.0 and abs(y - origin.y) <= extent.y + 10.0:
            containing.append((top_z, label))
    if containing:
        containing.sort()
        return containing[0]
    z = terrain_z(x, y)
    return (z, "Landscape") if z is not None else (None, "")


ready = []
manual = []
blockers = []
for row in records:
    item = dict(row)
    path = common.safe_asset_ref_to_path(item["planned_asset_ref"], registry)
    item["resolved_asset_path"] = path
    if not path or not common.asset_path_allowed(config, path):
        item["reason"] = "unresolved_or_disallowed_asset"
        blockers.append(item)
        continue
    asset = unreal.EditorAssetLibrary.load_asset(path)
    if not isinstance(asset, unreal.StaticMesh):
        item["reason"] = "static_mesh_required"
        blockers.append(item)
        continue
    scale = float(item["scale"])
    bounds = asset.get_bounds()
    dimensions = bounds.box_extent * (2.0 * scale)
    item["dimensions_cm"] = {"x": round(dimensions.x, 3), "y": round(dimensions.y, 3), "z": round(dimensions.z, 3)}
    if max(dimensions.x, dimensions.y) > 650.0 or dimensions.z > 400.0:
        item["reason"] = "asset_dimensions_require_review"
        blockers.append(item)
        continue
    x = float(item["x_m"]) * 100.0
    y = float(item["y_m"]) * 100.0
    support_z, support_label = support_for(item["site_id"], x, y)
    if support_z is None:
        item["reason"] = "support_not_found"
        blockers.append(item)
        continue
    local_min_z = (bounds.origin.z - bounds.box_extent.z) * scale
    item["support_actor"] = support_label
    item["support_z_cm"] = round(support_z, 3)
    item["planned_location_cm"] = {"x": round(x, 3), "y": round(y, 3), "z": round(support_z - local_min_z, 3)}
    item["reason"] = ""
    ready.append((item, asset))

if apply_requested and blockers:
    raise RuntimeError("SUNSCAR_STORAGE_SCRAP_APPLY_BLOCKED blockers=%d" % len(blockers))
if apply_requested and existing:
    raise RuntimeError("SUNSCAR_STORAGE_SCRAP_DUPLICATE existing=%d" % len(existing))

created = []
if apply_requested:
    for item, asset in ready:
        loc = item["planned_location_cm"]
        scale = float(item["scale"])
        actor = actor_system.spawn_actor_from_object(
            asset,
            unreal.Vector(loc["x"], loc["y"], loc["z"]),
            unreal.Rotator(roll=0.0, pitch=0.0, yaw=float(item["yaw_deg"])),
            transient=False,
        )
        actor.set_actor_scale3d(unreal.Vector(scale, scale, scale))
        origin, extent = actor.get_actor_bounds(False)
        actor.add_actor_world_offset(unreal.Vector(0.0, 0.0, item["support_z_cm"] - (origin.z - extent.z)), False, False)
        actor.set_actor_label("OT_STORE_%s" % item["candidate_id"])
        actor.tags = [TAG, unreal.Name(item["site_id"]), unreal.Name(item["bom_id"]), unreal.Name("UnreviewedAutomationPlacement")]
        actor.set_folder_path(unreal.Name("%s/%s" % (FOLDER, item["site_id"])))
        created.append(actor.get_actor_label())

payload = {
    "schema_version": 1,
    "status": "apply_unsaved_preview_complete" if apply_requested else "dry_run_complete",
    "context": context,
    "record_count": len(records),
    "ready_count": len(ready),
    "manual_count": len(manual),
    "blocker_count": len(blockers),
    "created_actor_count": len(created),
    "created_actor_labels": created,
    "ready": [item for item, _asset in ready],
    "manual": manual,
    "blockers": blockers,
    "changes_made": bool(created),
    "level_saved": False,
}
name = "old_town_storage_scrap_apply_preview_v1.json" if apply_requested else "old_town_storage_scrap_dry_run_v1.json"
report = common.write_json_report(config, name, payload)
unreal.log(
    "SUNSCAR_STORAGE_SCRAP mode=%s ready=%d blockers=%d created=%d report=%s"
    % ("APPLY_UNSAVED" if apply_requested else "DRY_RUN", len(ready), len(blockers), len(created), report)
)
print("SUNSCAR_STORAGE_SCRAP", len(ready), len(blockers), len(created), report)
