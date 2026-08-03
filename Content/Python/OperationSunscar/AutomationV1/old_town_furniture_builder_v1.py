"""Dry-run-first furniture placement for the five-site Old Town connected slice."""

import os
import sys

import unreal

SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


TAG = unreal.Name("SunscarOldTownFurnitureV1")
FOLDER = "OldTown_AutomationPreview/FurnitureV1"
config = common.load_config()
execution = config["execution"]
apply_requested = bool(execution.get("apply_changes", False))
context = common.require_safe_context(config, write_requested=apply_requested)
plan = common.read_csv(common.planning_file(config, "resolved_plan_file"))
registry = common.read_json(common.planning_file(config, "final_registry_file"))
sites = set(config["connected_slice_sites"])
records = [row for row in plan if row["site_id"] in sites and row["class"] == "furniture"]
actor_system = common.actor_subsystem()
world = common.editor_world()
actors = list(actor_system.get_all_level_actors())
landscapes = [actor for actor in actors if "Landscape" in actor.get_class().get_name()]
non_landscapes = [actor for actor in actors if actor not in landscapes]
existing = [actor for actor in actors if TAG in list(actor.tags)]
scatter_tag = unreal.Name(config["execution"]["placement_tag"])
support_ignore = landscapes + existing + [actor for actor in actors if scatter_tag in list(actor.tags)]


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
            candidates.append((actor, origin, extent))
    floor_bounds[site] = candidates


def support_for(site, x, y):
    containing = []
    for actor, origin, extent in floor_bounds.get(site, []):
        if abs(x - origin.x) <= extent.x + 10.0 and abs(y - origin.y) <= extent.y + 10.0:
            containing.append((origin.z + extent.z, actor.get_actor_label()))
    if containing:
        containing.sort()
        return containing[0]
    z = terrain_z(x, y)
    if z is None:
        return None, ""
    hit = unreal.SystemLibrary.line_trace_single(
        world,
        unreal.Vector(x, y, z + 150.0),
        unreal.Vector(x, y, z - 100.0),
        unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
        True,
        support_ignore,
        unreal.DrawDebugTrace.NONE,
        True,
    )
    if hit is not None:
        result = hit.to_dict()
        if result.get("blocking_hit") and result["location"].z - z <= 120.0:
            support_actor = result.get("hit_actor")
            support_label = support_actor.get_actor_label() if support_actor else ""
            allowed_support = (
                support_label.startswith("Ground_")
                or support_label.startswith("MarketRoute_")
                or support_label.startswith("CourtyardConnector_")
                or (support_label.startswith("Core_") and "Floor" in support_label)
            )
            if allowed_support:
                return result["location"].z, support_label
    return z, "Landscape"


ready = []
manual = []
blockers = []
for row in records:
    item = dict(row)
    asset_ref = item["planned_asset_ref"]
    if asset_ref.startswith("map-owned://"):
        item["reason"] = "existing_map_owned_definition_retained"
        manual.append(item)
        continue
    path = common.safe_asset_ref_to_path(asset_ref, registry)
    item["resolved_asset_path"] = path
    if not path or not common.asset_path_allowed(config, path):
        item["reason"] = "unresolved_or_disallowed_asset"
        blockers.append(item)
        continue
    asset = unreal.EditorAssetLibrary.load_asset(path)
    if not isinstance(asset, unreal.StaticMesh):
        item["reason"] = "furniture_v1_requires_static_mesh"
        manual.append(item)
        continue
    scale = float(item["scale"])
    bounds = asset.get_bounds()
    dimensions = bounds.box_extent * (2.0 * scale)
    item["dimensions_cm"] = {
        "x": round(dimensions.x, 3),
        "y": round(dimensions.y, 3),
        "z": round(dimensions.z, 3),
    }
    if max(dimensions.x, dimensions.y) > 600.0 or dimensions.z > 350.0:
        item["reason"] = "asset_dimensions_require_manual_review"
        blockers.append(item)
        continue
    x = float(item["x_m"]) * 100.0
    y = float(item["y_m"]) * 100.0
    support_z, support_actor = support_for(item["site_id"], x, y)
    if support_z is None:
        item["reason"] = "support_not_found"
        blockers.append(item)
        continue
    local_min_z = (bounds.origin.z - bounds.box_extent.z) * scale
    item["support_actor"] = support_actor
    item["support_z_cm"] = round(support_z, 3)
    item["planned_location_cm"] = {
        "x": round(x, 3),
        "y": round(y, 3),
        "z": round(support_z - local_min_z, 3),
    }
    item["reason"] = ""
    ready.append((item, asset))

if apply_requested and blockers:
    raise RuntimeError("SUNSCAR_FURNITURE_APPLY_BLOCKED blockers=%d" % len(blockers))
if apply_requested and existing:
    raise RuntimeError("SUNSCAR_FURNITURE_DUPLICATE_PREVIEW existing=%d" % len(existing))

created = []
if apply_requested:
    for item, asset in ready:
        location = item["planned_location_cm"]
        scale = float(item["scale"])
        actor = actor_system.spawn_actor_from_object(
            asset,
            unreal.Vector(location["x"], location["y"], location["z"]),
            unreal.Rotator(roll=0.0, pitch=0.0, yaw=float(item["yaw_deg"])),
            transient=False,
        )
        actor.set_actor_scale3d(unreal.Vector(scale, scale, scale))
        origin, extent = actor.get_actor_bounds(False)
        actor.add_actor_world_offset(
            unreal.Vector(0.0, 0.0, item["support_z_cm"] - (origin.z - extent.z)),
            False,
            False,
        )
        actor.set_actor_label("OT_FURN_%s" % item["candidate_id"])
        actor.tags = [
            TAG,
            unreal.Name(item["site_id"]),
            unreal.Name(item["bom_id"]),
            unreal.Name("UnreviewedAutomationPlacement"),
        ]
        actor.set_folder_path(unreal.Name("%s/%s" % (FOLDER, item["site_id"])))
        actor.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
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
name = "old_town_furniture_apply_preview.json" if apply_requested else "old_town_furniture_dry_run.json"
report = common.write_json_report(config, name, payload)
unreal.log(
    "SUNSCAR_FURNITURE mode=%s ready=%d manual=%d blockers=%d created=%d report=%s"
    % ("APPLY_UNSAVED" if apply_requested else "DRY_RUN", len(ready), len(manual), len(blockers), len(created), report)
)
print("SUNSCAR_FURNITURE", len(ready), len(manual), len(blockers), len(created), report)
