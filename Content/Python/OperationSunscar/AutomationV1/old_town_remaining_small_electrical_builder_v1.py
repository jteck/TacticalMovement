"""Dry-run-first placement of 13 support-resolved small electrical boxes outside SS_007."""

import math
import os
import sys

import unreal

SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


TAG = unreal.Name("SunscarOldTownElectricalBoxesV2")
BASE_FOLDER = "OldTown_AutomationPreview/ElectricalBoxesV2"
EXCLUDED_SITES = {"SS_007"}
DEFERRED_CANDIDATES = {
    "SS_013_UTILITY_016",
    "SS_015_UTILITY_003",
    "SS_016_UTILITY_007",
    "SS_016_UTILITY_036",
}
config = common.load_config()
apply_requested = bool(config["execution"].get("apply_changes", False))
context = common.require_safe_context(config, write_requested=apply_requested)
plan = common.read_csv(common.planning_file(config, "resolved_plan_file"))
registry = common.read_json(common.planning_file(config, "final_registry_file"))
all_records = [
    row for row in plan
    if row["bom_id"] == "OT_UTIL_001" and row["site_id"] not in EXCLUDED_SITES
]
records = [row for row in all_records if row["candidate_id"] not in DEFERRED_CANDIDATES]
deferred = [dict(row, reason="planned_coordinate_has_no_nearby_matching_facade") for row in all_records if row["candidate_id"] in DEFERRED_CANDIDATES]
actor_system = common.actor_subsystem()
actors = list(actor_system.get_all_level_actors())
existing = [actor for actor in actors if TAG in list(actor.tags)]


def site_geometry(site_id):
    floors = []
    walls = []
    for actor in actors:
        label = actor.get_actor_label()
        if site_id not in label:
            continue
        origin, extent = actor.get_actor_bounds(False)
        if "Floor" in label:
            floors.append((origin.z + extent.z, label, origin, extent))
        if "Wall" in label:
            walls.append((label, origin, extent))
    return floors, walls


def containing_floor(floors, x, y):
    matches = []
    for top_z, label, origin, extent in floors:
        if abs(x - origin.x) <= extent.x + 10.0 and abs(y - origin.y) <= extent.y + 10.0:
            matches.append((top_z, label))
    matches.sort()
    return matches[0] if matches else (None, "")


def nearest_wall(walls, x, y):
    matches = []
    for label, origin, extent in walls:
        min_x, max_x = origin.x - extent.x, origin.x + extent.x
        min_y, max_y = origin.y - extent.y, origin.y + extent.y
        surface_x = min(max(x, min_x), max_x)
        surface_y = min(max(y, min_y), max_y)
        dx, dy = x - surface_x, y - surface_y
        distance = math.sqrt(dx * dx + dy * dy)
        if distance <= 0.001:
            edges = (
                (abs(x - min_x), min_x, y, -1.0, 0.0),
                (abs(max_x - x), max_x, y, 1.0, 0.0),
                (abs(y - min_y), x, min_y, 0.0, -1.0),
                (abs(max_y - y), x, max_y, 0.0, 1.0),
            )
            _edge_distance, surface_x, surface_y, normal_x, normal_y = min(edges)
        else:
            normal_x, normal_y = dx / distance, dy / distance
        matches.append((distance, label, surface_x + normal_x * 8.0, surface_y + normal_y * 8.0))
    matches.sort()
    return matches[0] if matches else (None, "", None, None)


geometry = {site_id: site_geometry(site_id) for site_id in sorted({row["site_id"] for row in records})}
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
    x = float(item["x_m"]) * 100.0
    y = float(item["y_m"]) * 100.0
    floors, walls = geometry[item["site_id"]]
    floor_z, floor_label = containing_floor(floors, x, y)
    wall_distance, wall_label, mount_x, mount_y = nearest_wall(walls, x, y)
    if floor_z is None or wall_distance is None or wall_distance > 200.0:
        item["reason"] = "floor_or_wall_mount_not_found"
        item["nearest_wall_distance_cm"] = wall_distance
        blockers.append(item)
        continue
    item["floor_actor"] = floor_label
    item["floor_z_cm"] = round(floor_z, 3)
    item["nearest_wall"] = wall_label
    item["nearest_wall_distance_cm"] = round(wall_distance, 3)
    item["mount_bottom_z_cm"] = round(floor_z + 100.0, 3)
    item["source_planned_xy_cm"] = {"x": round(x, 3), "y": round(y, 3)}
    item["planned_xy_cm"] = {"x": round(mount_x, 3), "y": round(mount_y, 3)}
    item["reason"] = ""
    ready.append((item, asset))

if len(all_records) != 17 or len(records) != 13 or len(deferred) != 4:
    raise RuntimeError(
        "SUNSCAR_REMAINING_ELECTRICAL_PLAN_DRIFT all=%d selected=%d deferred=%d"
        % (len(all_records), len(records), len(deferred))
    )
if apply_requested and blockers:
    raise RuntimeError("SUNSCAR_REMAINING_ELECTRICAL_APPLY_BLOCKED blockers=%d" % len(blockers))
if apply_requested and existing:
    raise RuntimeError("SUNSCAR_REMAINING_ELECTRICAL_DUPLICATE existing=%d" % len(existing))

created = []
if apply_requested:
    for item, asset in ready:
        xy = item["planned_xy_cm"]
        scale = float(item["scale"])
        actor = actor_system.spawn_actor_from_object(
            asset,
            unreal.Vector(xy["x"], xy["y"], item["mount_bottom_z_cm"] + 30.0),
            unreal.Rotator(roll=0.0, pitch=90.0, yaw=float(item["yaw_deg"])),
            transient=False,
        )
        actor.set_actor_scale3d(unreal.Vector(scale, scale, scale))
        origin, extent = actor.get_actor_bounds(False)
        actor.add_actor_world_offset(
            unreal.Vector(0.0, 0.0, item["mount_bottom_z_cm"] - (origin.z - extent.z)),
            False,
            False,
        )
        label = "OT_UTIL_%s" % item["candidate_id"]
        actor.set_actor_label(label)
        actor.tags = [
            TAG,
            unreal.Name(item["site_id"]),
            unreal.Name("OT_UTIL_001"),
            unreal.Name("UnreviewedAutomationPlacement"),
        ]
        actor.set_folder_path(unreal.Name("%s/%s" % (BASE_FOLDER, item["site_id"])))
        actor.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        created.append(label)

payload = {
    "schema_version": 1,
    "status": "apply_unsaved_preview_complete" if apply_requested else "dry_run_complete",
    "context": context,
    "planned_record_count": len(all_records),
    "record_count": len(records),
    "deferred_count": len(deferred),
    "deferred": deferred,
    "ready_count": len(ready),
    "blocker_count": len(blockers),
    "existing_actor_count": len(existing),
    "created_actor_count": len(created),
    "created_actor_labels": created,
    "sites": sorted({row["site_id"] for row in records}),
    "ready": [item for item, _asset in ready],
    "blockers": blockers,
    "changes_made": bool(created),
    "level_saved": False,
}
name = "old_town_remaining_small_electrical_apply_preview_v1.json" if apply_requested else "old_town_remaining_small_electrical_dry_run_v1.json"
report = common.write_json_report(config, name, payload)
unreal.log(
    "SUNSCAR_REMAINING_ELECTRICAL mode=%s ready=%d blockers=%d created=%d report=%s"
    % ("APPLY_UNSAVED" if apply_requested else "DRY_RUN", len(ready), len(blockers), len(created), report)
)
print("SUNSCAR_REMAINING_ELECTRICAL", len(ready), len(blockers), len(created), report)
