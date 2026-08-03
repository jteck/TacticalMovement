"""Dry-run-first side-mounted shutters for selected Old Town window pairs."""

import math
import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


TAG = unreal.Name("SunscarOldTownWindowShutterV1")
FOLDER = "OldTown_ArtDraft/WindowShuttersV1"
TARGETS = {
    "Tea_Window_01_Frame": "SS_004",
    "Tea_Window_03_Frame": "SS_004",
    "Clinic_F1_Win_01_Frame": "SS_005",
    "Clinic_F1_Win_04_Frame": "SS_005",
    "Detention_F1_Win_01_Frame": "SS_010",
    "Detention_F1_Win_05_Frame": "SS_010",
    "Checkpoint_Win_02_Frame": "SS_011",
    "Consulate_F1_Win_01_Frame": "SS_012",
    "Consulate_F1_Win_04_Frame": "SS_012",
    "Telecom_F1_Win_02_Frame": "SS_018",
}
METAL_SITES = {"SS_003", "SS_010", "SS_011", "SS_018"}
CUBE_PATH = "/Engine/BasicShapes/Cube.Cube"
METAL_PATH = "/Game/Maps/Sunscar/Art/Materials/Instances/MI_OT_Metal"
TIMBER_PATH = "/Game/Maps/Sunscar/Art/Materials/Instances/MI_OT_Timber"

config = common.load_config()
apply_requested = bool(config["execution"].get("apply_changes", False))
context = common.require_safe_context(config, write_requested=apply_requested)
actor_system = common.actor_subsystem()
actors = list(actor_system.get_all_level_actors())
existing = [actor for actor in actors if TAG in list(actor.tags)]
if apply_requested and existing:
    raise RuntimeError("SUNSCAR_WINDOW_SHUTTER_DUPLICATE existing=%d" % len(existing))

cube = unreal.EditorAssetLibrary.load_asset(CUBE_PATH)
metal = unreal.EditorAssetLibrary.load_asset(METAL_PATH)
timber = unreal.EditorAssetLibrary.load_asset(TIMBER_PATH)
if not isinstance(cube, unreal.StaticMesh) or metal is None or timber is None:
    raise RuntimeError("SUNSCAR_WINDOW_SHUTTER_REQUIRED_ASSET_MISSING")


def site_match(actor, site):
    return site in " ".join([actor.get_actor_label(), common.actor_folder(actor), *common.actor_tags(actor)])


def nearest_wall(site, origin):
    values = []
    for actor in actors:
        if not site_match(actor, site) or "wall" not in actor.get_actor_label().lower():
            continue
        wall_origin, wall_extent = actor.get_actor_bounds(False)
        min_x, max_x = wall_origin.x - wall_extent.x, wall_origin.x + wall_extent.x
        min_y, max_y = wall_origin.y - wall_extent.y, wall_origin.y + wall_extent.y
        sx, sy = min(max(origin.x, min_x), max_x), min(max(origin.y, min_y), max_y)
        dx, dy = origin.x - sx, origin.y - sy
        distance = math.hypot(dx, dy)
        if distance <= 0.001:
            edges = (
                (abs(origin.x - min_x), min_x, origin.y, -1.0, 0.0),
                (abs(max_x - origin.x), max_x, origin.y, 1.0, 0.0),
                (abs(origin.y - min_y), origin.x, min_y, 0.0, -1.0),
                (abs(max_y - origin.y), origin.x, max_y, 0.0, 1.0),
            )
            _edge, sx, sy, nx, ny = min(edges)
        else:
            nx, ny = dx / distance, dy / distance
        values.append((distance, actor, sx, sy, nx, ny))
    values.sort(key=lambda value: value[0])
    return values[0] if values else (None, None, None, None, None, None)


ready = []
blockers = []
for frame_label, site in TARGETS.items():
    matches = [actor for actor in actors if actor.get_actor_label() == frame_label]
    if len(matches) != 1:
        blockers.append({"frame_label": frame_label, "reason": "frame_not_unique"})
        continue
    frame = matches[0]
    frame_origin, frame_extent = frame.get_actor_bounds(False)
    distance, wall, sx, sy, nx, ny = nearest_wall(site, frame_origin)
    if wall is None or distance > 100.0:
        blockers.append({"frame_label": frame_label, "reason": "nearby_wall_not_resolved", "distance_cm": distance})
        continue
    tx, ty = -ny, nx
    tangent_half = abs(tx) * frame_extent.x + abs(ty) * frame_extent.y
    panel_width = 62.0
    panel_height = max(frame_extent.z * 2.0, 120.0)
    panel_depth = 6.0
    offset = tangent_half + panel_width * 0.5 + 6.0
    if abs(nx) > abs(ny):
        dimensions = {"x": panel_depth, "y": panel_width, "z": panel_height}
    else:
        dimensions = {"x": panel_width, "y": panel_depth, "z": panel_height}
    for side, sign in (("L", -1.0), ("R", 1.0)):
        x = sx + nx * 5.0 + tx * offset * sign
        y = sy + ny * 5.0 + ty * offset * sign
        ready.append({
            "site_id": site,
            "frame_label": frame_label,
            "wall_label": wall.get_actor_label(),
            "wall_distance_cm": round(distance, 3),
            "side": side,
            "location_cm": {"x": round(x, 3), "y": round(y, 3), "z": round(frame_origin.z, 3)},
            "dimensions_cm": dimensions,
            "normal": {"x": round(nx, 4), "y": round(ny, 4)},
            "material_path": METAL_PATH if site in METAL_SITES else TIMBER_PATH,
        })

if apply_requested and blockers:
    raise RuntimeError("SUNSCAR_WINDOW_SHUTTER_APPLY_BLOCKED blockers=%d" % len(blockers))

created = []
if apply_requested:
    for item in ready:
        loc, dims = item["location_cm"], item["dimensions_cm"]
        actor = actor_system.spawn_actor_from_object(
            cube,
            unreal.Vector(loc["x"], loc["y"], loc["z"]),
            unreal.Rotator(roll=0.0, pitch=0.0, yaw=0.0),
            transient=False,
        )
        actor.set_actor_scale3d(unreal.Vector(dims["x"] / 100.0, dims["y"] / 100.0, dims["z"] / 100.0))
        actor.static_mesh_component.set_material(0, metal if item["site_id"] in METAL_SITES else timber)
        actor.static_mesh_component.set_collision_profile_name("NoCollision")
        actor.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        stem = item["frame_label"].replace("_Frame", "")
        actor.set_actor_label("OT_SHUTTER_%s_%s" % (stem, item["side"]))
        actor.tags = [TAG, unreal.Name(item["site_id"]), unreal.Name("MOD_WIN_03"), unreal.Name("ExteriorWindowDetail"), unreal.Name(item["frame_label"])]
        actor.set_folder_path(unreal.Name("%s/%s" % (FOLDER, item["site_id"])))
        created.append(actor.get_actor_label())

payload = {
    "schema_version": 1,
    "status": "apply_unsaved_preview_complete" if apply_requested else "dry_run_complete",
    "context": context,
    "target_window_count": len(TARGETS),
    "ready_actor_count": len(ready),
    "blocker_count": len(blockers),
    "blockers": blockers,
    "ready": ready,
    "created_actor_count": len(created),
    "created_actor_labels": created,
    "changes_made": bool(created),
    "level_saved": False,
    "collision_policy": "NoCollision side-mounted exterior detail; opening geometry unchanged",
}
name = "old_town_window_shutter_apply_preview_v1.json" if apply_requested else "old_town_window_shutter_dry_run_v1.json"
report = common.write_json_report(config, name, payload)
unreal.log("SUNSCAR_WINDOW_SHUTTER mode=%s ready=%d blockers=%d created=%d report=%s" % ("APPLY_UNSAVED" if apply_requested else "DRY_RUN", len(ready), len(blockers), len(created), report))
print("SUNSCAR_WINDOW_SHUTTER", len(ready), len(blockers), len(created), report)
