"""Dry-run-first Old Town ground integration and small exterior completion pass."""

import math
import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


TAG = unreal.Name("SunscarOldTownExteriorCompletionV1")
FOLDER = "OldTown_ArtDraft/ExteriorCompletionV1"
BUILDING_SITES = ("SS_003", "SS_004", "SS_005", "SS_007", "SS_010", "SS_011", "SS_012", "SS_013", "SS_015", "SS_018")
ROOF_SITES = ("SS_005", "SS_007", "SS_010", "SS_011", "SS_012", "SS_018")
WALL_DECAL_SITES = ("SS_003", "SS_004", "SS_005", "SS_007", "SS_010", "SS_011", "SS_012", "SS_013", "SS_015", "SS_016", "SS_017", "SS_018")
ROUTE_FOLDERS = (
    "OldTown_GroundElevationPassV2/Roads/ClinicConnector",
    "OldTown_GroundElevationPassV2/Roads/CourtyardConnector",
    "OldTown_GroundElevationPassV2/Roads/FreightConnector",
    "OldTown_GroundElevationPassV2/Roads/MarketRoute",
    "OldTown_GroundElevationPassV2/Roads/NorthRoute",
    "OldTown_GroundElevationPassV2/Roads/SouthRoute",
)
CUBE_PATH = "/Engine/BasicShapes/Cube.Cube"
CYLINDER_PATH = "/Engine/BasicShapes/Cylinder.Cylinder"
METAL_MATERIAL_PATH = "/Game/Maps/Sunscar/Art/Materials/Instances/MI_OT_Metal"
GROUND_DECAL_PATHS = (
    "/Game/Scene_Junkyard/Assets/MS/Decals/Decal_Debris_Dirt_01/MI_Decal_Debris_Dirt_01_A",
    "/Game/Scene_Junkyard/Assets/MS/Decals/Decal_Debris_Dirt_01/MI_Decal_Debris_Dirt_01_B",
    "/Game/Scene_Junkyard/Assets/MS/Decals/Decal_Debris_Pile_Rubble_01/MI_Decal_Debris_Pile_Rubble_01",
    "/Game/Scene_Junkyard/Assets/MS/Decals/Decal_Debris_Pile_Rubble_02/MI_Decal_Debris_Pile_Rubble_02",
    "/Game/Scene_Junkyard/Assets/MS/Decals/Decal_Edge_Garbage_Tiling_01/MI_Decal_Edge_Garbage_Tiling_01_A",
    "/Game/Scene_Junkyard/Assets/MS/Decals/Decal_Pile_Wood_Splinters_01/MI_Decal_Pile_Wood_Splinters_01",
)
WALL_DECAL_PATHS = (
    "/Game/MilitaryTrench/Assets/Decals/Ind_Decal_Leak_02/MI_Ind_Decal_Leak_02_A",
    "/Game/MilitaryTrench/Assets/Decals/Ind_Decal_Leak_02/MI_Ind_Decal_Leak_02_B",
    "/Game/MilitaryTrench/Assets/Decals/Ind_Decal_Leak_10/MI_Ind_Decal_Leak_10",
    "/Game/Scene_Junkyard/Assets/MS/Decals/Decal_Leak_Dirt_01/MI_Decal_Leak_Dirt_01_A",
    "/Game/Scene_Junkyard/Assets/MS/Decals/Decal_Leak_Dirt_01/MI_Decal_Leak_Dirt_01_B",
)


config = common.load_config()
apply_requested = bool(config["execution"].get("apply_changes", False))
context = common.require_safe_context(config, write_requested=apply_requested)
actor_system = common.actor_subsystem()
actors = list(actor_system.get_all_level_actors())
existing = [actor for actor in actors if TAG in list(actor.tags)]
if apply_requested and existing:
    raise RuntimeError("SUNSCAR_EXTERIOR_COMPLETION_DUPLICATE existing=%d" % len(existing))

cube = unreal.EditorAssetLibrary.load_asset(CUBE_PATH)
cylinder = unreal.EditorAssetLibrary.load_asset(CYLINDER_PATH)
metal = common.load_asset_checked(config, METAL_MATERIAL_PATH)
ground_decals = [common.load_asset_checked(config, path) for path in GROUND_DECAL_PATHS]
wall_decals = [common.load_asset_checked(config, path) for path in WALL_DECAL_PATHS]
if not isinstance(cube, unreal.StaticMesh) or not isinstance(cylinder, unreal.StaticMesh):
    raise RuntimeError("SUNSCAR_EXTERIOR_COMPLETION_BASIC_MESH_MISSING")


def actor_bounds(actor):
    return actor.get_actor_bounds(False)


def site_members(site):
    return [actor for actor in actors if site in (actor.get_actor_label() + " " + " ".join(common.actor_tags(actor)))]


def ground_floor(site):
    floors = [actor for actor in site_members(site) if "floor" in actor.get_actor_label().lower()]
    return min(floors, key=lambda actor: actor_bounds(actor)[0].z) if floors else None


def first_floor_walls(site):
    values = []
    for actor in site_members(site):
        label = actor.get_actor_label().lower()
        if "wall" in label and ("f1" in label or site in ("SS_016", "SS_017")):
            values.append(actor)
    return values


def site_openings(site):
    return [
        actor for actor in site_members(site)
        if any(term in actor.get_actor_label().lower() for term in ("door", "window", "_win_", "gate"))
    ]


def wall_frame(site, wall):
    floor = ground_floor(site)
    if floor is None:
        return None
    floor_origin, floor_extent = actor_bounds(floor)
    wall_origin, wall_extent = actor_bounds(wall)
    dx, dy = wall_origin.x - floor_origin.x, wall_origin.y - floor_origin.y
    length = math.hypot(dx, dy)
    if length < 1.0:
        if wall_extent.x < wall_extent.y:
            dx, dy = 1.0, 0.0
        else:
            dx, dy = 0.0, 1.0
        length = 1.0
    nx, ny = dx / length, dy / length
    tx, ty = -ny, nx
    half_span = wall_extent.y if wall_extent.x < wall_extent.y else wall_extent.x
    return floor, floor_origin, floor_extent, wall_origin, wall_extent, nx, ny, tx, ty, half_span


def overlaps_opening(site, x, y, z, hx, hy, hz):
    for opening in site_openings(site):
        origin, extent = actor_bounds(opening)
        if abs(x - origin.x) <= hx + extent.x + 20.0 and abs(y - origin.y) <= hy + extent.y + 20.0 and abs(z - origin.z) <= hz + extent.z + 20.0:
            return opening.get_actor_label()
    return ""


def choose_wall_position(site, wall, height_cm, half_width_cm):
    frame = wall_frame(site, wall)
    if frame is None:
        return None
    floor, floor_origin, floor_extent, wall_origin, wall_extent, nx, ny, tx, ty, half_span = frame
    floor_top = floor_origin.z + floor_extent.z
    z = floor_top + height_cm
    for fraction in (0.68, -0.68, 0.42, -0.42, 0.0):
        x = wall_origin.x + tx * half_span * fraction + nx * 10.0
        y = wall_origin.y + ty * half_span * fraction + ny * 10.0
        hx = 10.0 if abs(nx) > abs(ny) else half_width_cm
        hy = half_width_cm if abs(nx) > abs(ny) else 10.0
        if not overlaps_opening(site, x, y, z, hx, hy, height_cm * 0.5):
            return frame, x, y, z, fraction
    return None


route_selections = []
for folder in ROUTE_FOLDERS:
    values = sorted([actor for actor in actors if common.actor_folder(actor) == folder], key=lambda actor: actor.get_actor_label())
    if len(values) < 6:
        raise RuntimeError("SUNSCAR_EXTERIOR_COMPLETION_ROUTE_TOO_SHORT %s %d" % (folder, len(values)))
    indices = sorted({len(values) // 4, len(values) // 2, (len(values) * 3) // 4})
    route_selections.append((folder, [values[index] for index in indices]))

planned = []


def plan(kind, label, site, location, rotation, dimensions, material_path="", support=""):
    planned.append({
        "kind": kind,
        "label": label,
        "site_id": site,
        "location_cm": [round(location.x, 3), round(location.y, 3), round(location.z, 3)],
        "rotation_deg": [round(rotation.roll, 3), round(rotation.pitch, 3), round(rotation.yaw, 3)],
        "dimensions_cm": [round(dimensions.x, 3), round(dimensions.y, 3), round(dimensions.z, 3)],
        "material_path": material_path,
        "support": support,
    })


# Proper projected decals break up roads at player height without collision or raised lips.
ground_index = 0
for folder, selected in route_selections:
    route_name = folder.rsplit("/", 1)[-1]
    for segment_index, segment in enumerate(selected):
        origin, extent = actor_bounds(segment)
        yaw = segment.get_actor_rotation().yaw
        material = ground_decals[ground_index % len(ground_decals)]
        ground_index += 1
        plan(
            "ground_debris_decal",
            "OT_EXT_Ground_%s_%02d" % (route_name, segment_index + 1),
            "",
            unreal.Vector(origin.x, origin.y, origin.z + extent.z + 70.0),
            unreal.Rotator(roll=0.0, pitch=-90.0, yaw=yaw),
            unreal.Vector(90.0, min(260.0, max(extent.x, extent.y) * 0.55), min(380.0, max(extent.x, extent.y) * 0.9)),
            material.get_path_name(),
            segment.get_actor_label(),
        )

    # Two selected route pieces receive parallel narrow dirt wear marks.
    for segment_index, segment in enumerate((selected[0], selected[2])):
        origin, extent = actor_bounds(segment)
        yaw = segment.get_actor_rotation().yaw
        radians = math.radians(yaw)
        px, py = -math.sin(radians), math.cos(radians)
        for side in (-1.0, 1.0):
            offset = 82.0 * side
            material = ground_decals[(ground_index + segment_index) % 2]
            plan(
                "worn_route_decal",
                "OT_EXT_Wear_%s_%02d_%s" % (route_name, segment_index + 1, "L" if side < 0 else "R"),
                "",
                unreal.Vector(origin.x + px * offset, origin.y + py * offset, origin.z + extent.z + 60.0),
                unreal.Rotator(roll=0.0, pitch=-90.0, yaw=yaw),
                unreal.Vector(80.0, 34.0, min(420.0, max(extent.x, extent.y) * 0.95)),
                material.get_path_name(),
                segment.get_actor_label(),
            )
    ground_index += 2

# Drainpipes, outlets, and utility meters fill the remaining repeated façade-detail gap.
for site in BUILDING_SITES:
    walls = first_floor_walls(site)
    if not walls:
        raise RuntimeError("SUNSCAR_EXTERIOR_COMPLETION_NO_WALL " + site)
    wall = max(walls, key=lambda actor: max(actor_bounds(actor)[1].x, actor_bounds(actor)[1].y))
    chosen = choose_wall_position(site, wall, 115.0, 8.0)
    if chosen is None:
        raise RuntimeError("SUNSCAR_EXTERIOR_COMPLETION_PIPE_BLOCKED " + site)
    frame, x, y, z, fraction = chosen
    floor, floor_origin, floor_extent, wall_origin, wall_extent, nx, ny, tx, ty, half_span = frame
    floor_top = floor_origin.z + floor_extent.z
    pipe_height = 220.0
    plan("drainpipe", "OT_EXT_Drain_%s" % site, site, unreal.Vector(x, y, floor_top + pipe_height * 0.5 + 6.0), unreal.Rotator(), unreal.Vector(8.0, 8.0, pipe_height), metal.get_path_name(), wall.get_actor_label())
    plan("drain_outlet", "OT_EXT_DrainOutlet_%s" % site, site, unreal.Vector(x + nx * 15.0, y + ny * 15.0, floor_top + 18.0), unreal.Rotator(roll=0.0, pitch=90.0, yaw=math.degrees(math.atan2(ny, nx))), unreal.Vector(8.0, 8.0, 38.0), metal.get_path_name(), wall.get_actor_label())
    meter_x = wall_origin.x - tx * half_span * 0.48 + nx * 11.0
    meter_y = wall_origin.y - ty * half_span * 0.48 + ny * 11.0
    meter_z = floor_top + 78.0
    if overlaps_opening(site, meter_x, meter_y, meter_z, 24.0, 24.0, 26.0):
        meter_x = wall_origin.x + tx * half_span * 0.18 + nx * 11.0
        meter_y = wall_origin.y + ty * half_span * 0.18 + ny * 11.0
    meter_dims = unreal.Vector(14.0, 42.0, 52.0) if abs(nx) > abs(ny) else unreal.Vector(42.0, 14.0, 52.0)
    plan("utility_meter", "OT_EXT_Meter_%s" % site, site, unreal.Vector(meter_x, meter_y, meter_z), unreal.Rotator(), meter_dims, metal.get_path_name(), wall.get_actor_label())

# Proper wall-projected leak and grime decals replace the rejected flat-panel damage approach.
for index, site in enumerate(WALL_DECAL_SITES):
    walls = first_floor_walls(site)
    if not walls:
        raise RuntimeError("SUNSCAR_EXTERIOR_COMPLETION_DECAL_NO_WALL " + site)
    wall = max(walls, key=lambda actor: max(actor_bounds(actor)[1].x, actor_bounds(actor)[1].y))
    chosen = choose_wall_position(site, wall, 135.0, 65.0)
    if chosen is None:
        raise RuntimeError("SUNSCAR_EXTERIOR_COMPLETION_DECAL_BLOCKED " + site)
    frame, x, y, z, fraction = chosen
    _floor, _fo, _fe, _wo, _we, nx, ny, _tx, _ty, _span = frame
    inward_yaw = math.degrees(math.atan2(-ny, -nx))
    material = wall_decals[index % len(wall_decals)]
    plan("wall_weathering_decal", "OT_EXT_Weather_%s" % site, site, unreal.Vector(x + nx * 20.0, y + ny * 20.0, z), unreal.Rotator(roll=0.0, pitch=0.0, yaw=inward_yaw), unreal.Vector(45.0, 95.0, 150.0), material.get_path_name(), wall.get_actor_label())

# Thresholds make exterior door grounding legible from the player camera.
door_candidates = []
for site in BUILDING_SITES:
    for actor in site_members(site):
        if "door" in actor.get_actor_label().lower():
            door_candidates.append((site, actor))
door_candidates.sort(key=lambda item: (item[0], item[1].get_actor_label()))
for index, (site, door) in enumerate(door_candidates[:8]):
    origin, extent = actor_bounds(door)
    if extent.x < extent.y:
        dims = unreal.Vector(48.0, min(170.0, extent.y * 2.0 + 18.0), 8.0)
    else:
        dims = unreal.Vector(min(170.0, extent.x * 2.0 + 18.0), 48.0, 8.0)
    plan("door_threshold", "OT_EXT_Threshold_%02d" % (index + 1), site, unreal.Vector(origin.x, origin.y, origin.z - extent.z + 4.0), unreal.Rotator(), dims, metal.get_path_name(), door.get_actor_label())

# Rooftop masts and bases add a restrained skyline layer without changing traversal.
for site in ROOF_SITES:
    members = site_members(site)
    floors = [actor for actor in members if "floor" in actor.get_actor_label().lower()]
    walls = first_floor_walls(site) + [actor for actor in members if "wall" in actor.get_actor_label().lower()]
    if not floors or not walls:
        raise RuntimeError("SUNSCAR_EXTERIOR_COMPLETION_ROOF_SUPPORT_MISSING " + site)
    floor = min(floors, key=lambda actor: actor_bounds(actor)[0].z)
    floor_origin, floor_extent = actor_bounds(floor)
    roof_z = max(actor_bounds(actor)[0].z + actor_bounds(actor)[1].z for actor in walls)
    x = floor_origin.x + floor_extent.x * 0.42
    y = floor_origin.y - floor_extent.y * 0.38
    plan("roof_mast_base", "OT_EXT_MastBase_%s" % site, site, unreal.Vector(x, y, roof_z + 6.0), unreal.Rotator(), unreal.Vector(46.0, 46.0, 12.0), metal.get_path_name(), "roofline")
    plan("roof_mast", "OT_EXT_Mast_%s" % site, site, unreal.Vector(x, y, roof_z + 101.0), unreal.Rotator(), unreal.Vector(6.0, 6.0, 190.0), metal.get_path_name(), "roofline")

# Eight short roadside posts help define route edges at eye height without blocking movement.
post_segments = [selected[1] for _folder, selected in route_selections]
post_segments += [route_selections[3][1][0], route_selections[5][1][2]]
for index, segment in enumerate(post_segments):
    origin, extent = actor_bounds(segment)
    yaw = segment.get_actor_rotation().yaw
    radians = math.radians(yaw)
    px, py = -math.sin(radians), math.cos(radians)
    edge = max(120.0, min(extent.x, extent.y) * 0.82)
    side = -1.0 if index % 2 else 1.0
    plan("roadside_post", "OT_EXT_RoadPost_%02d" % (index + 1), "", unreal.Vector(origin.x + px * edge * side, origin.y + py * edge * side, origin.z + extent.z + 45.0), unreal.Rotator(), unreal.Vector(9.0, 9.0, 90.0), metal.get_path_name(), segment.get_actor_label())

expected_counts = {
    "ground_debris_decal": 18,
    "worn_route_decal": 24,
    "drainpipe": 10,
    "drain_outlet": 10,
    "utility_meter": 10,
    "wall_weathering_decal": 12,
    "door_threshold": 8,
    "roof_mast_base": 6,
    "roof_mast": 6,
    "roadside_post": 8,
}
actual_counts = {}
for item in planned:
    actual_counts[item["kind"]] = actual_counts.get(item["kind"], 0) + 1
if actual_counts != expected_counts or len(planned) != 112:
    raise RuntimeError("SUNSCAR_EXTERIOR_COMPLETION_PLAN_COUNT_REFUSED %s total=%d" % (actual_counts, len(planned)))

created = []
created_actors = []
if apply_requested:
    material_by_path = {asset.get_path_name(): asset for asset in ground_decals + wall_decals + [metal]}
    try:
        for item in planned:
            location = unreal.Vector(*item["location_cm"])
            rotation = unreal.Rotator(roll=item["rotation_deg"][0], pitch=item["rotation_deg"][1], yaw=item["rotation_deg"][2])
            dimensions = unreal.Vector(*item["dimensions_cm"])
            if item["kind"].endswith("decal"):
                actor = actor_system.spawn_actor_from_class(unreal.DecalActor, location, rotation, transient=False)
                component = actor.get_editor_property("decal")
                component.set_editor_property("decal_material", material_by_path[item["material_path"]])
                component.set_editor_property("decal_size", dimensions)
            else:
                mesh = cylinder if item["kind"] in ("drainpipe", "drain_outlet", "roof_mast", "roadside_post") else cube
                actor = actor_system.spawn_actor_from_object(mesh, location, rotation, transient=False)
                actor.set_actor_scale3d(unreal.Vector(dimensions.x / 100.0, dimensions.y / 100.0, dimensions.z / 100.0))
                actor.static_mesh_component.set_material(0, metal)
                actor.static_mesh_component.set_collision_profile_name("NoCollision")
                actor.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
            actor.set_actor_label(item["label"])
            actor.tags = [TAG, unreal.Name(item["kind"]), unreal.Name(item["site_id"] or "OldTownRoute"), unreal.Name("ReviewedAutomationPlacement")]
            actor.set_folder_path(unreal.Name("%s/%s" % (FOLDER, item["kind"])))
            created.append(actor.get_actor_label())
            created_actors.append(actor)
    except Exception:
        for actor in reversed(created_actors):
            try:
                actor_system.destroy_actor(actor)
            except Exception:
                pass
        raise

payload = {
    "schema_version": 1,
    "status": "apply_unsaved_preview_complete" if apply_requested else "dry_run_complete",
    "context": context,
    "planned_actor_count": len(planned),
    "planned_counts": actual_counts,
    "created_actor_count": len(created),
    "created_actor_labels": created,
    "planned": planned,
    "collision_policy": "All new static-mesh details are NoCollision; decals never affect collision.",
    "route_policy": "No large prop or gameplay-cover placement; existing routes remain unchanged.",
    "changes_made": bool(created),
    "level_saved": False,
}
filename = "old_town_exterior_completion_apply_preview_v1.json" if apply_requested else "old_town_exterior_completion_dry_run_v1.json"
report = common.write_json_report(config, filename, payload)
unreal.log("SUNSCAR_EXTERIOR_COMPLETION mode=%s planned=%d created=%d report=%s" % ("APPLY_UNSAVED" if apply_requested else "DRY_RUN", len(planned), len(created), report))
print("SUNSCAR_EXTERIOR_COMPLETION", len(planned), len(created), report)
