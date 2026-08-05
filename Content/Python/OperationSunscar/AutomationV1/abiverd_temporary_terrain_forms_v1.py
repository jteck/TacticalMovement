"""Create a fast, removable perimeter relief preview from map-owned mesh actors."""

import json
import math
import os

import unreal


APPLY_CHANGES = False
EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development"
EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
PASS_TAG = unreal.Name("AbiverdTemporaryTerrainFormsV1")
FOLDER = "Sunscar/Abiverd/Terrain/TemporaryReliefV1"
SPHERE_PATH = "/Engine/BasicShapes/Sphere.Sphere"
MATERIAL_PATH = "/Game/Maps/Sunscar/Art/Materials/Ground/WorldAligned/MI_OT_SandstoneEarth_WorldAligned.MI_OT_SandstoneEarth_WorldAligned"
TARGET_COUNT = 18

# x, y, width, length, visible rise, yaw. All dimensions are centimeters.
CANDIDATES = [
    (-34000, -27000, 6200, 4100, 260, 18), (-27000, -28500, 5100, 3300, 180, -22),
    (-19000, -29000, 6900, 3600, 310, 7), (-9000, -29200, 4800, 3000, 150, 33),
    (4000, -29500, 6000, 3400, 230, -12), (15000, -28800, 7200, 3900, 280, 24),
    (26000, -28200, 5200, 3100, 170, -34), (34500, -26000, 6600, 4000, 300, 9),
    (-36000, -17000, 5400, 3200, 190, 41), (-35500, -6000, 7000, 3900, 270, -16),
    (-36000, 7000, 5800, 3500, 220, 28), (-35000, 18500, 7400, 4100, 320, -8),
    (-32000, 27500, 6100, 3600, 230, 15), (-22000, 29000, 4900, 3000, 160, -27),
    (-11000, 29500, 6800, 3700, 290, 5), (2000, 29600, 5200, 3200, 180, 31),
    (14000, 29200, 7100, 3900, 310, -19), (25000, 28600, 5700, 3400, 210, 12),
    (34500, 27000, 6500, 3700, 270, -29), (36000, 17000, 5000, 3100, 170, 36),
    (36000, 6000, 7200, 4000, 300, -10), (35500, -7000, 5600, 3400, 200, 21),
    (35000, -17500, 6800, 3800, 280, -35), (-28000, 22500, 4500, 2900, 150, 44),
    (29000, 22500, 4700, 3000, 160, -42), (-28500, -22000, 5200, 3200, 190, 14),
    (28500, -22000, 5400, 3300, 200, -16), (-25000, 25000, 6000, 3500, 240, 6),
]


def package_name(package):
    try:
        return package.get_name()
    except Exception:
        return str(package)


def dirty_packages():
    return sorted(
        {package_name(item) for item in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()}
        | {package_name(item) for item in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()}
    )


project_directory = os.path.abspath(unreal.Paths.project_dir()).replace("\\", "/").rstrip("/")
level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).get_current_level()
level_path = level.get_outermost().get_name() if level else ""
if not project_directory.endswith(EXPECTED_DIRECTORY_SUFFIX) or level_path != EXPECTED_LEVEL:
    raise RuntimeError("ABIVERD_TEMP_TERRAIN_CONTEXT")
if dirty_packages():
    raise RuntimeError("ABIVERD_TEMP_TERRAIN_DIRTY_BEFORE " + "|".join(dirty_packages()))

actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors = list(actor_subsystem.get_all_level_actors())
if any(str(PASS_TAG) in [str(tag) for tag in actor.tags] for actor in actors):
    raise RuntimeError("ABIVERD_TEMP_TERRAIN_ALREADY_EXISTS")

overlays = []
obstacles = []
for actor in actors:
    tags = [str(tag) for tag in actor.tags]
    label = actor.get_actor_label()
    folder = str(actor.get_folder_path())
    origin, extent = actor.get_actor_bounds(False)
    if "VisualGroundOverlay" in tags:
        overlays.append((origin, extent, origin.z + extent.z))
    if (
        "CoreCategory_Building" in tags
        or label.startswith("CoreRoute_")
        or "/Roads/" in folder
        or folder.endswith("/Roads")
    ):
        obstacles.append((origin, extent))


def surface_z(x, y):
    covering = [
        top_z
        for origin, extent, top_z in overlays
        if abs(x - origin.x) <= extent.x + 25.0 and abs(y - origin.y) <= extent.y + 25.0
    ]
    if covering:
        return max(covering)
    nearest = min(
        overlays,
        key=lambda item: (item[0].x - x) ** 2 + (item[0].y - y) ** 2,
    )
    return nearest[2]


def intersects_obstacle(x, y, radius_x, radius_y):
    for origin, extent in obstacles:
        if (
            abs(x - origin.x) <= radius_x + extent.x + 750.0
            and abs(y - origin.y) <= radius_y + extent.y + 750.0
        ):
            return True
    return False


eligible = []
for x, y, width, length, rise, yaw in CANDIDATES:
    if intersects_obstacle(x, y, width * 0.5, length * 0.5):
        continue
    eligible.append((x, y, width, length, rise, yaw, surface_z(x, y)))
    if len(eligible) == TARGET_COUNT:
        break
if len(eligible) != TARGET_COUNT:
    raise RuntimeError("ABIVERD_TEMP_TERRAIN_INSUFFICIENT_CANDIDATES %d" % len(eligible))

report_root = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
os.makedirs(report_root, exist_ok=True)
if not APPLY_CHANGES:
    payload = {"schema_version": 1, "status": "dry_run", "eligible": eligible, "changes_made": False}
    report_path = os.path.join(report_root, "abiverd_temporary_terrain_forms_dry_run_v1.json")
else:
    mesh = unreal.load_asset(SPHERE_PATH)
    material = unreal.load_asset(MATERIAL_PATH)
    if mesh is None or material is None:
        raise RuntimeError("ABIVERD_TEMP_TERRAIN_ASSET_MISSING")
    created = []
    for index, (x, y, width, length, rise, yaw, ground_z) in enumerate(eligible, start=1):
        vertical_radius = 500.0
        center_z = ground_z - (vertical_radius - rise)
        actor = actor_subsystem.spawn_actor_from_class(
            unreal.StaticMeshActor,
            unreal.Vector(float(x), float(y), float(center_z)),
            unreal.Rotator(0.0, float(yaw), 0.0),
        )
        if actor is None:
            raise RuntimeError("ABIVERD_TEMP_TERRAIN_SPAWN_FAILED %d" % index)
        actor.set_actor_label("ABV_TerrainForm_%02d" % index)
        actor.set_folder_path(FOLDER)
        actor.tags = [PASS_TAG, unreal.Name("MapDevelopmentOnly"), unreal.Name("TerrainRelief")]
        component = actor.static_mesh_component
        component.set_static_mesh(mesh)
        component.set_material(0, material)
        component.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
        component.set_editor_property("cast_shadow", True)
        actor.set_actor_scale3d(unreal.Vector(width / 100.0, length / 100.0, 10.0))
        created.append(
            {
                "label": actor.get_actor_label(),
                "path": actor.get_path_name(),
                "location_cm": list(actor.get_actor_location().to_tuple()),
                "scale": list(actor.get_actor_scale3d().to_tuple()),
                "rise_cm": rise,
                "ground_z_cm": ground_z,
                "package": actor.get_package().get_name(),
            }
        )
    payload = {
        "schema_version": 1,
        "status": "unsaved_preview_created",
        "actor_count": len(created),
        "actors": created,
        "dirty_packages": dirty_packages(),
        "rollback": "delete actors tagged AbiverdTemporaryTerrainFormsV1 before save, or reload their unsaved packages",
        "changes_made": True,
    }
    report_path = os.path.join(report_root, "abiverd_temporary_terrain_forms_apply_preview_v1.json")

with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2)
    handle.write("\n")
unreal.log("ABIVERD_TEMP_TERRAIN_%s count=%d" % (payload["status"].upper(), len(eligible)))
print("ABIVERD_TEMP_TERRAIN", report_path)
