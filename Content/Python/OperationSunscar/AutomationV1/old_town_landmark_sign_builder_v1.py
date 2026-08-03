"""Dry-run-first readable landmark facade signs for Old Town."""

import math
import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


TAG = unreal.Name("SunscarOldTownLandmarkSignV1")
FOLDER = "OldTown_ArtDraft/LandmarkSignsV1"
SITE_TEXT = {
    "SS_004": "TEA HOUSE",
    "SS_005": "CLINIC",
    "SS_007": "HOTEL",
    "SS_010": "DETENTION",
    "SS_011": "CHECKPOINT",
    "SS_013": "FREIGHT",
    "SS_014": "SALVAGE",
    "SS_017": "BAZAAR",
    "SS_018": "TELECOM",
}
PRIMARY_DOOR_LABEL = {
    "SS_004": "Tea_MainDoor",
    "SS_005": "Clinic_MainDoor",
    "SS_007": "Hotel_Door_-14",
    "SS_010": "Detention_Door_12",
    "SS_011": "Checkpoint_Door",
    "SS_013": "Depot_PedDoor",
    "SS_018": "Telecom_MainDoor",
}
SPECIAL_WALL_LABEL = {
    "SS_014": ("SS_014_Fence_N", 0.0, 1.0),
    "SS_017": ("Core_SS_017_F1_S_Wall", 0.0, -1.0),
}
CUBE_PATH = "/Engine/BasicShapes/Cube.Cube"
BOARD_MATERIAL_PATH = "/Game/Maps/Sunscar/Art/Materials/Instances/MI_OT_Accent"
config = common.load_config()
apply_requested = bool(config["execution"].get("apply_changes", False))
context = common.require_safe_context(config, write_requested=apply_requested)
actor_system = common.actor_subsystem()
actors = list(actor_system.get_all_level_actors())
existing = [actor for actor in actors if TAG in list(actor.tags)]
if apply_requested and existing:
    raise RuntimeError("SUNSCAR_LANDMARK_SIGN_DUPLICATE existing=%d" % len(existing))

cube = unreal.EditorAssetLibrary.load_asset(CUBE_PATH)
board_material = unreal.EditorAssetLibrary.load_asset(BOARD_MATERIAL_PATH)
if not isinstance(cube, unreal.StaticMesh) or board_material is None:
    raise RuntimeError("SUNSCAR_LANDMARK_SIGN_REQUIRED_ASSET_MISSING")


def nearest_wall(site, origin):
    values = []
    for actor in actors:
        label = actor.get_actor_label()
        if site not in label or "wall" not in label.lower():
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
for site, text_value in SITE_TEXT.items():
    board_width, board_height, board_depth = 160.0, 45.0, 8.0
    if site in SPECIAL_WALL_LABEL:
        wall_label, nx, ny = SPECIAL_WALL_LABEL[site]
        wall_matches = [actor for actor in actors if actor.get_actor_label() == wall_label]
        if len(wall_matches) != 1:
            blockers.append({"site_id": site, "reason": "special_wall_not_found", "wall_actor": wall_label})
            continue
        wall = wall_matches[0]
        wall_origin, wall_extent = wall.get_actor_bounds(False)
        sx = wall_origin.x + nx * wall_extent.x
        sy = wall_origin.y + ny * wall_extent.y
        board_z = min(wall_origin.z + 45.0, wall_origin.z + wall_extent.z - board_height * 0.5 - 8.0)
        door_label = ""
        wall_distance = 0.0
        placement = "landmark_wall_center"
    else:
        door_label = PRIMARY_DOOR_LABEL[site]
        door_matches = [actor for actor in actors if actor.get_actor_label() == door_label]
        if len(door_matches) != 1:
            blockers.append({"site_id": site, "reason": "primary_door_not_found", "door_actor": door_label})
            continue
        door_origin, door_extent = door_matches[0].get_actor_bounds(False)
        wall_distance, wall, sx, sy, nx, ny = nearest_wall(site, door_origin)
        if wall is None or wall_distance > 250.0:
            blockers.append({"site_id": site, "reason": "nearby_wall_not_found", "wall_distance_cm": wall_distance})
            continue
        wall_origin, wall_extent = wall.get_actor_bounds(False)
        wall_top = wall_origin.z + wall_extent.z
        door_top = door_origin.z + door_extent.z
        board_z = door_top + 12.0 + board_height * 0.5
        if board_z + board_height * 0.5 > wall_top - 5.0:
            board_z = min(door_origin.z + 35.0, wall_top - board_height * 0.5 - 8.0)
            tx, ty = -ny, nx
            shift = door_extent.x + 100.0 if abs(tx) > abs(ty) else door_extent.y + 100.0
            candidate_a = (sx + tx * shift, sy + ty * shift)
            candidate_b = (sx - tx * shift, sy - ty * shift)
            candidates = [candidate_a, candidate_b]
            candidates.sort(
                key=lambda value: (
                    max(abs(value[0] - wall_origin.x) - wall_extent.x, 0.0)
                    + max(abs(value[1] - wall_origin.y) - wall_extent.y, 0.0)
                )
            )
            sx, sy = candidates[0]
            placement = "beside_door"
        else:
            placement = "above_door"
    board_x, board_y = sx + nx * 6.0, sy + ny * 6.0
    normal_yaw = math.degrees(math.atan2(ny, nx))
    if abs(nx) > abs(ny):
        dimensions = {"x": board_depth, "y": board_width, "z": board_height}
    else:
        dimensions = {"x": board_width, "y": board_depth, "z": board_height}
    ready.append({
        "site_id": site,
        "text": text_value,
        "door_actor": door_label,
        "wall_actor": wall.get_actor_label(),
        "wall_distance_cm": round(wall_distance, 3),
        "placement": placement,
        "board_location_cm": {"x": round(board_x, 3), "y": round(board_y, 3), "z": round(board_z, 3)},
        "board_dimensions_cm": dimensions,
        "normal": {"x": round(nx, 4), "y": round(ny, 4)},
        "normal_yaw_deg": round(normal_yaw, 3),
    })

if apply_requested and blockers:
    raise RuntimeError("SUNSCAR_LANDMARK_SIGN_APPLY_BLOCKED blockers=%d" % len(blockers))

created = []
if apply_requested:
    for item in ready:
        loc = item["board_location_cm"]
        dims = item["board_dimensions_cm"]
        board = actor_system.spawn_actor_from_object(
            cube,
            unreal.Vector(loc["x"], loc["y"], loc["z"]),
            unreal.Rotator(roll=0.0, pitch=0.0, yaw=0.0),
            transient=False,
        )
        board.set_actor_scale3d(unreal.Vector(dims["x"] / 100.0, dims["y"] / 100.0, dims["z"] / 100.0))
        board.static_mesh_component.set_material(0, board_material)
        board.static_mesh_component.set_collision_profile_name("NoCollision")
        board.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        board.set_actor_label("OT_SIGNBOARD_%s" % item["site_id"])
        board.tags = [TAG, unreal.Name(item["site_id"]), unreal.Name("OT_DECAL_004"), unreal.Name("LandmarkSignBoard")]
        board.set_folder_path(unreal.Name("%s/%s" % (FOLDER, item["site_id"])))
        nx, ny = item["normal"]["x"], item["normal"]["y"]
        tx, ty = -ny, nx
        text_x = loc["x"] + nx * 6.0 - tx * 66.0
        text_y = loc["y"] + ny * 6.0 - ty * 66.0
        text_z = loc["z"] - 9.0
        text_actor = actor_system.spawn_actor_from_class(
            unreal.TextRenderActor,
            unreal.Vector(text_x, text_y, text_z),
            unreal.Rotator(roll=0.0, pitch=0.0, yaw=item["normal_yaw_deg"]),
            transient=False,
        )
        component = text_actor.text_render
        component.set_text(item["text"])
        component.set_world_size(18.0)
        component.set_text_render_color(unreal.Color(238, 222, 178, 255))
        component.set_horizontal_alignment(unreal.HorizTextAligment.EHTA_LEFT)
        component.set_vertical_alignment(unreal.VerticalTextAligment.EVRTA_TEXT_CENTER)
        text_actor.set_actor_label("OT_SIGNTEXT_%s" % item["site_id"])
        text_actor.tags = [TAG, unreal.Name(item["site_id"]), unreal.Name("OT_DECAL_004"), unreal.Name("LandmarkSignText")]
        text_actor.set_folder_path(unreal.Name("%s/%s" % (FOLDER, item["site_id"])))
        created.extend([board.get_actor_label(), text_actor.get_actor_label()])

payload = {
    "schema_version": 1,
    "status": "apply_unsaved_preview_complete" if apply_requested else "dry_run_complete",
    "context": context,
    "site_count": len(SITE_TEXT),
    "ready_count": len(ready),
    "blocker_count": len(blockers),
    "blockers": blockers,
    "ready": ready,
    "created_actor_count": len(created),
    "created_actor_labels": created,
    "changes_made": bool(created),
    "level_saved": False,
    "collision_policy": "NoCollision environmental signage",
}
name = "old_town_landmark_sign_apply_preview_v1.json" if apply_requested else "old_town_landmark_sign_dry_run_v1.json"
report = common.write_json_report(config, name, payload)
unreal.log(
    "SUNSCAR_LANDMARK_SIGN mode=%s ready=%d blockers=%d created=%d report=%s"
    % ("APPLY_UNSAVED" if apply_requested else "DRY_RUN", len(ready), len(blockers), len(created), report)
)
print("SUNSCAR_LANDMARK_SIGN", len(ready), len(blockers), len(created), report)
