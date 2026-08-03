"""Dry-run-first Quixel damaged-plaster facade pass for connected Old Town sites."""

import math
import os
import sys

import unreal

SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


TAG = unreal.Name("SunscarOldTownFacadeDamageV1")
FOLDER = "OldTown_AutomationPreview/FacadeDamageV1"
config = common.load_config()
apply_requested = bool(config["execution"].get("apply_changes", False))
context = common.require_safe_context(config, write_requested=apply_requested)
plan = common.read_csv(common.planning_file(config, "resolved_plan_file"))
registry = common.read_json(common.planning_file(config, "final_registry_file"))
sites = set(config["connected_slice_sites"])
records = [row for row in plan if row["site_id"] in sites and row["bom_id"] == "OT_DECAL_001"]
actor_system = common.actor_subsystem()
actors = list(actor_system.get_all_level_actors())
existing = [actor for actor in actors if TAG in list(actor.tags)]

site_floors = {}
site_walls = {}
for site in sites:
    floors, walls = [], []
    for actor in actors:
        label = actor.get_actor_label()
        if site not in label:
            continue
        origin, extent = actor.get_actor_bounds(False)
        if "Floor" in label:
            floors.append((origin.z + extent.z, label, origin, extent))
        if "Wall" in label:
            walls.append((label, origin, extent))
    site_floors[site] = floors
    site_walls[site] = walls


def floor_for(site, x, y):
    values = []
    for top_z, label, origin, extent in site_floors.get(site, []):
        dx = max(abs(x - origin.x) - extent.x, 0.0)
        dy = max(abs(y - origin.y) - extent.y, 0.0)
        values.append((math.sqrt(dx * dx + dy * dy), top_z, label))
    values.sort()
    return values[0] if values else (None, None, "")


def wall_mount(site, x, y):
    values = []
    for label, origin, extent in site_walls.get(site, []):
        min_x, max_x = origin.x - extent.x, origin.x + extent.x
        min_y, max_y = origin.y - extent.y, origin.y + extent.y
        sx, sy = min(max(x, min_x), max_x), min(max(y, min_y), max_y)
        dx, dy = x - sx, y - sy
        distance = math.sqrt(dx * dx + dy * dy)
        if distance <= 0.001:
            edges = (
                (abs(x - min_x), min_x, y, -1.0, 0.0),
                (abs(max_x - x), max_x, y, 1.0, 0.0),
                (abs(y - min_y), x, min_y, 0.0, -1.0),
                (abs(max_y - y), x, max_y, 0.0, 1.0),
            )
            _edge, sx, sy, nx, ny = min(edges)
        else:
            nx, ny = dx / distance, dy / distance
        values.append((distance, label, sx + nx * 2.0, sy + ny * 2.0, nx, ny))
    values.sort()
    return values[0] if values else (None, "", None, None, None, None)


ready = []
manual = []
blockers = []
for index, row in enumerate(records):
    item = dict(row)
    path = common.safe_asset_ref_to_path(item["planned_asset_ref"], registry)
    item["resolved_asset_path"] = path
    asset = unreal.EditorAssetLibrary.load_asset(path) if path else None
    if not isinstance(asset, unreal.StaticMesh) or not common.asset_path_allowed(config, path):
        item["reason"] = "missing_or_disallowed_static_mesh"
        blockers.append(item)
        continue
    x, y = float(item["x_m"]) * 100.0, float(item["y_m"]) * 100.0
    floor_distance, floor_z, floor_label = floor_for(item["site_id"], x, y)
    wall_distance, wall_label, mount_x, mount_y, normal_x, normal_y = wall_mount(item["site_id"], x, y)
    if floor_z is None or wall_distance is None or wall_distance > 350.0:
        item["reason"] = "facade_floor_or_wall_not_found"
        item["floor_distance_cm"] = floor_distance
        item["wall_distance_cm"] = wall_distance
        manual.append(item)
        continue
    height = 130.0 + float((index * 73) % 120)
    normal_yaw = math.degrees(math.atan2(normal_y, normal_x))
    in_plane_roll = (float(item["yaw_deg"]) % 30.0) - 15.0
    item["floor_actor"] = floor_label
    item["floor_z_cm"] = round(floor_z, 3)
    item["wall_actor"] = wall_label
    item["wall_distance_cm"] = round(wall_distance, 3)
    item["planned_location_cm"] = {"x": round(mount_x, 3), "y": round(mount_y, 3), "z": round(floor_z + height, 3)}
    item["planned_rotation"] = {"roll": round(in_plane_roll, 3), "pitch": 90.0, "yaw": round(normal_yaw, 3)}
    item["applied_scale"] = round(min(float(item["scale"]), 1.15), 4)
    item["reason"] = ""
    ready.append((item, asset))

if apply_requested and blockers:
    raise RuntimeError("SUNSCAR_FACADE_DAMAGE_APPLY_BLOCKED blockers=%d" % len(blockers))
if apply_requested and existing:
    raise RuntimeError("SUNSCAR_FACADE_DAMAGE_DUPLICATE existing=%d" % len(existing))
created = []
if apply_requested:
    for item, asset in ready:
        loc, rot, scale = item["planned_location_cm"], item["planned_rotation"], item["applied_scale"]
        actor = actor_system.spawn_actor_from_object(
            asset, unreal.Vector(loc["x"], loc["y"], loc["z"]),
            unreal.Rotator(roll=rot["roll"], pitch=rot["pitch"], yaw=rot["yaw"]), transient=False,
        )
        actor.set_actor_scale3d(unreal.Vector(scale, scale, scale))
        actor.set_actor_label("OT_DAMAGE_%s" % item["candidate_id"])
        actor.tags = [TAG, unreal.Name(item["site_id"]), unreal.Name("OT_DECAL_001"), unreal.Name("UnreviewedAutomationPlacement")]
        actor.set_folder_path(unreal.Name("%s/%s" % (FOLDER, item["site_id"])))
        actor.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        created.append(actor.get_actor_label())

payload = {
    "schema_version": 1, "status": "apply_unsaved_preview_complete" if apply_requested else "dry_run_complete",
    "context": context, "record_count": len(records), "ready_count": len(ready), "manual_count": len(manual), "blocker_count": len(blockers),
    "created_actor_count": len(created), "created_actor_labels": created,
    "ready": [item for item, _asset in ready], "manual": manual, "blockers": blockers,
    "changes_made": bool(created), "level_saved": False,
}
name = "old_town_facade_damage_apply_preview_v1.json" if apply_requested else "old_town_facade_damage_dry_run_v1.json"
report = common.write_json_report(config, name, payload)
unreal.log("SUNSCAR_FACADE_DAMAGE mode=%s ready=%d blockers=%d created=%d report=%s" % ("APPLY_UNSAVED" if apply_requested else "DRY_RUN", len(ready), len(blockers), len(created), report))
print("SUNSCAR_FACADE_DAMAGE", len(ready), len(blockers), len(created), report)
