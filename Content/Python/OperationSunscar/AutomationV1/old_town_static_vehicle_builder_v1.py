"""Dry-run-first placement of the five planned City Sample static vehicles."""

import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


TAG = unreal.Name("SunscarOldTownStaticVehiclesV1")
FOLDER = "OldTown_AutomationPreview/StaticVehiclesV1"
config = common.load_config()
apply_requested = bool(config["execution"].get("apply_changes", False))
context = common.require_safe_context(config, write_requested=apply_requested)
plan = common.read_csv(common.planning_file(config, "resolved_plan_file"))
records = [
    row
    for row in plan
    if row["bom_id"] == "OT_TAC_003"
    and row["planned_asset_ref"].startswith("/Game/CitySampleVehicles/")
]
if len(records) != 5:
    raise RuntimeError("SUNSCAR_STATIC_VEHICLE_PLAN_SCOPE record_count=%d" % len(records))

actor_system = common.actor_subsystem()
world = common.editor_world()
actors = list(actor_system.get_all_level_actors())
landscapes = [actor for actor in actors if "Landscape" in actor.get_class().get_name()]
existing = [actor for actor in actors if TAG in list(actor.tags)]
support_ignore = landscapes + [actor for actor in actors if actor.get_actor_label().startswith("OT_")]


def visible_support(x, y):
    hit = unreal.SystemLibrary.line_trace_single(
        world,
        unreal.Vector(x, y, 100000.0),
        unreal.Vector(x, y, -100000.0),
        unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
        True,
        support_ignore,
        unreal.DrawDebugTrace.NONE,
        True,
    )
    result = hit.to_dict() if hit is not None else {}
    if not result.get("blocking_hit"):
        return None, ""
    actor = result.get("hit_actor")
    return result["location"].z, actor.get_actor_label() if actor else ""


ready = []
blockers = []
for row in records:
    item = dict(row)
    path = item["planned_asset_ref"]
    if not common.asset_path_allowed(config, path):
        item["reason"] = "disallowed_asset_path"
        blockers.append(item)
        continue
    asset = unreal.EditorAssetLibrary.load_asset(path)
    if not isinstance(asset, unreal.StaticMesh):
        item["reason"] = "missing_static_mesh"
        blockers.append(item)
        continue
    scale = float(item["scale"])
    size = asset.get_bounds().box_extent * (2.0 * scale)
    if not (400.0 <= size.x <= 700.0 and 180.0 <= size.y <= 300.0 and 150.0 <= size.z <= 300.0):
        item["reason"] = "vehicle_dimensions_out_of_range"
        item["dimensions_cm"] = {"x": size.x, "y": size.y, "z": size.z}
        blockers.append(item)
        continue
    x = float(item["x_m"]) * 100.0
    y = float(item["y_m"]) * 100.0
    support_z, support_label = visible_support(x, y)
    if support_z is None:
        item["reason"] = "support_trace_failed"
        blockers.append(item)
        continue
    bounds = asset.get_bounds()
    local_min_z = (bounds.origin.z - bounds.box_extent.z) * scale
    item["dimensions_cm"] = {"x": round(size.x, 3), "y": round(size.y, 3), "z": round(size.z, 3)}
    item["support_z_cm"] = round(support_z, 3)
    item["support_actor"] = support_label
    item["planned_location_cm"] = {
        "x": round(x, 3),
        "y": round(y, 3),
        "z": round(support_z - local_min_z, 3),
    }
    item["reason"] = ""
    ready.append((item, asset))

if apply_requested and blockers:
    raise RuntimeError("SUNSCAR_STATIC_VEHICLE_APPLY_BLOCKED blockers=%d" % len(blockers))
if apply_requested and existing:
    raise RuntimeError("SUNSCAR_STATIC_VEHICLE_DUPLICATE existing=%d" % len(existing))

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
        actor.set_actor_label("OT_VEH_%s" % item["candidate_id"])
        actor.tags = [
            TAG,
            unreal.Name(item["site_id"]),
            unreal.Name("OT_TAC_003"),
            unreal.Name("StaticVehicleCover"),
            unreal.Name("UnreviewedAutomationPlacement"),
        ]
        actor.set_folder_path(unreal.Name("%s/%s" % (FOLDER, item["site_id"])))
        actor.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
        created.append(actor.get_actor_label())

payload = {
    "schema_version": 1,
    "status": "apply_unsaved_preview_complete" if apply_requested else "dry_run_complete",
    "context": context,
    "record_count": len(records),
    "ready_count": len(ready),
    "blocker_count": len(blockers),
    "created_actor_count": len(created),
    "created_actor_labels": created,
    "ready": [item for item, _asset in ready],
    "blockers": blockers,
    "changes_made": bool(created),
    "level_saved": False,
}
filename = (
    "old_town_static_vehicle_apply_preview_v1.json"
    if apply_requested
    else "old_town_static_vehicle_dry_run_v1.json"
)
report = common.write_json_report(config, filename, payload)
unreal.log(
    "SUNSCAR_STATIC_VEHICLE mode=%s ready=%d blockers=%d created=%d report=%s"
    % ("APPLY_UNSAVED" if apply_requested else "DRY_RUN", len(ready), len(blockers), len(created), report)
)
print("SUNSCAR_STATIC_VEHICLE", len(ready), len(blockers), len(created), report)
