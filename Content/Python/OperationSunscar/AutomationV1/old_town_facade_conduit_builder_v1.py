"""Dry-run-first facade conduit accents for eight Old Town building sites."""

import math
import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


TAG = unreal.Name("SunscarOldTownFacadeConduitV1")
FOLDER = "OldTown_ArtDraft/FacadeConduitV1"
SITES = ("SS_004", "SS_005", "SS_007", "SS_010", "SS_011", "SS_012", "SS_017", "SS_018")
CUBE_PATH = "/Engine/BasicShapes/Cube.Cube"
MATERIAL_PATH = "/Game/Maps/Sunscar/Art/Materials/Instances/MI_OT_Metal"
config = common.load_config()
apply_requested = bool(config["execution"].get("apply_changes", False))
context = common.require_safe_context(config, write_requested=apply_requested)
plan = common.read_csv(common.planning_file(config, "resolved_plan_file"))
actor_system = common.actor_subsystem()
actors = list(actor_system.get_all_level_actors())
existing = [actor for actor in actors if TAG in list(actor.tags)]
if apply_requested and existing:
    raise RuntimeError("SUNSCAR_FACADE_CONDUIT_DUPLICATE existing=%d" % len(existing))

cube = unreal.EditorAssetLibrary.load_asset(CUBE_PATH)
material = unreal.EditorAssetLibrary.load_asset(MATERIAL_PATH)
if not isinstance(cube, unreal.StaticMesh) or material is None:
    raise RuntimeError("SUNSCAR_FACADE_CONDUIT_REQUIRED_ASSET_MISSING")

site_floors = {site: [] for site in SITES}
site_walls = {site: [] for site in SITES}
site_openings = {site: [] for site in SITES}
for actor in actors:
    label = actor.get_actor_label()
    site = next((value for value in SITES if value in label), None)
    if site is None:
        continue
    origin, extent = actor.get_actor_bounds(False)
    lowered = label.lower()
    if "floor" in lowered:
        site_floors[site].append((origin.z + extent.z, label, origin, extent))
    if "wall" in lowered:
        site_walls[site].append((label, origin, extent))
    if "door" in lowered or "window" in lowered or "gate" in lowered:
        site_openings[site].append((label, origin, extent))


def nearest_floor(site, x, y):
    values = []
    for top_z, label, origin, extent in site_floors[site]:
        dx = max(abs(x - origin.x) - extent.x, 0.0)
        dy = max(abs(y - origin.y) - extent.y, 0.0)
        values.append((math.hypot(dx, dy), top_z, label))
    values.sort()
    return values[0] if values else (None, None, "")


def nearest_wall(site, x, y):
    values = []
    for label, origin, extent in site_walls[site]:
        min_x, max_x = origin.x - extent.x, origin.x + extent.x
        min_y, max_y = origin.y - extent.y, origin.y + extent.y
        sx, sy = min(max(x, min_x), max_x), min(max(y, min_y), max_y)
        dx, dy = x - sx, y - sy
        distance = math.hypot(dx, dy)
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
        values.append((distance, label, sx + nx * 6.0, sy + ny * 6.0, nx, ny))
    values.sort()
    return values[0] if values else (None, "", None, None, None, None)


site_records = {}
for site in SITES:
    matches = [row for row in plan if row["site_id"] == site and row["bom_id"] == "OT_UTIL_005"]
    matches = sorted(matches, key=lambda row: row["candidate_id"])
    if site == "SS_017":
        matches = [row for row in matches if row["candidate_id"] in {"SS_017_UTILITY_004", "SS_017_UTILITY_005"}]
    site_records[site] = matches[:2]

ready = []
blockers = []
for site in SITES:
    if len(site_records[site]) != 2:
        blockers.append({"site_id": site, "reason": "two_conduit_candidates_required"})
        continue
    for index, row in enumerate(site_records[site]):
        item = dict(row)
        x, y = float(item["x_m"]) * 100.0, float(item["y_m"]) * 100.0
        floor_distance, floor_z, floor_label = nearest_floor(site, x, y)
        wall_distance, wall_label, mount_x, mount_y, nx, ny = nearest_wall(site, x, y)
        if floor_z is None or wall_distance is None or wall_distance > 450.0:
            item["reason"] = "facade_floor_or_wall_not_found"
            item["floor_distance_cm"] = floor_distance
            item["wall_distance_cm"] = wall_distance
            blockers.append(item)
            continue
        vertical = index == 0
        if vertical:
            dimensions = unreal.Vector(9.0, 9.0, 180.0)
            center_z = floor_z + 185.0
        elif abs(nx) > abs(ny):
            dimensions = unreal.Vector(9.0, 170.0, 9.0)
            center_z = floor_z + 275.0
        else:
            dimensions = unreal.Vector(170.0, 9.0, 9.0)
            center_z = floor_z + 275.0
        opening_conflicts = []
        for opening_label, opening_origin, opening_extent in site_openings[site]:
            if (
                abs(mount_x - opening_origin.x) <= opening_extent.x + dimensions.x * 0.5 + 25.0
                and abs(mount_y - opening_origin.y) <= opening_extent.y + dimensions.y * 0.5 + 25.0
                and abs(center_z - opening_origin.z) <= opening_extent.z + dimensions.z * 0.5 + 25.0
            ):
                opening_conflicts.append(opening_label)
        if opening_conflicts:
            item["reason"] = "opening_conflict:" + "|".join(opening_conflicts)
            blockers.append(item)
            continue
        item["floor_actor"] = floor_label
        item["wall_actor"] = wall_label
        item["wall_distance_cm"] = round(wall_distance, 3)
        item["planned_location_cm"] = {"x": round(mount_x, 3), "y": round(mount_y, 3), "z": round(center_z, 3)}
        item["dimensions_cm"] = {"x": dimensions.x, "y": dimensions.y, "z": dimensions.z}
        item["orientation"] = "vertical" if vertical else "horizontal"
        item["reason"] = ""
        ready.append(item)

if apply_requested and blockers:
    raise RuntimeError("SUNSCAR_FACADE_CONDUIT_APPLY_BLOCKED blockers=%d" % len(blockers))

created = []
if apply_requested:
    for item in ready:
        location = item["planned_location_cm"]
        dimensions = item["dimensions_cm"]
        actor = actor_system.spawn_actor_from_object(
            cube,
            unreal.Vector(location["x"], location["y"], location["z"]),
            unreal.Rotator(roll=0.0, pitch=0.0, yaw=0.0),
            transient=False,
        )
        actor.set_actor_scale3d(unreal.Vector(dimensions["x"] / 100.0, dimensions["y"] / 100.0, dimensions["z"] / 100.0))
        component = actor.static_mesh_component
        component.set_material(0, material)
        component.set_collision_profile_name("NoCollision")
        component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        actor.set_actor_label("OT_CONDUIT_%s" % item["candidate_id"])
        actor.tags = [TAG, unreal.Name(item["site_id"]), unreal.Name("OT_UTIL_005"), unreal.Name(item["candidate_id"]), unreal.Name("ReviewedAutomationPlacement")]
        actor.set_folder_path(unreal.Name("%s/%s" % (FOLDER, item["site_id"])))
        created.append(actor.get_actor_label())

payload = {
    "schema_version": 1,
    "status": "apply_unsaved_preview_complete" if apply_requested else "dry_run_complete",
    "context": context,
    "site_count": len(SITES),
    "record_count": sum(len(values) for values in site_records.values()),
    "ready_count": len(ready),
    "blocker_count": len(blockers),
    "blockers": blockers,
    "ready": ready,
    "created_actor_count": len(created),
    "created_actor_labels": created,
    "changes_made": bool(created),
    "level_saved": False,
    "collision_policy": "NoCollision decorative facade accents",
}
name = "old_town_facade_conduit_apply_preview_v1.json" if apply_requested else "old_town_facade_conduit_dry_run_v1.json"
report = common.write_json_report(config, name, payload)
unreal.log(
    "SUNSCAR_FACADE_CONDUIT mode=%s ready=%d blockers=%d created=%d report=%s"
    % ("APPLY_UNSAVED" if apply_requested else "DRY_RUN", len(ready), len(blockers), len(created), report)
)
print("SUNSCAR_FACADE_CONDUIT", len(ready), len(blockers), len(created), report)
