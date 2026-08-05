"""Complete SS_023 well court and add grounded mosque silhouette details."""

import json
import math
import os

import unreal


EXPECTED_PROJECT = "TacticalMovement"
EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development"
EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
PASS_TAG = unreal.Name("SunscarAbiverdLandmarkCompletionV2")
FOLDER_ROOT = "OperationSunscar/AbiverdHeritageV2"
REPORT_NAME = "abiverd_landmark_completion_v2.json"
CUBE_PATH = "/Engine/BasicShapes/Cube"
WALL_SCAN_PATH = "/Game/Maps/Sunscar/Art/Heritage/Architecture/WallModularSet04/Historic_Desert_Ruin_Wall_Modular_Set_04_yjxsbaqyx_High"
STONE_PATH = "/Game/Maps/Sunscar/Art/Heritage/Architecture/StructureStoneS06/Historic_Desert_Ruin_Structure_Stone_S_06_xblnbfv_High"
MUD_MATERIAL_PATH = "/Game/Maps/Sunscar/Art/Heritage/Materials/MI_ABV_CrackedMud_WorldAligned"
BRICK_MATERIAL_PATH = "/Game/Maps/Sunscar/Art/Heritage/Materials/MI_ABV_RuinBrick_WorldAligned"


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


def load_asset(path, expected_class):
    value = unreal.EditorAssetLibrary.load_asset(path)
    if not isinstance(value, expected_class):
        raise RuntimeError("ABIVERD_LANDMARK_V2_ASSET " + path)
    return value


project_name = os.path.splitext(os.path.basename(unreal.Paths.get_project_file_path()))[0]
project_directory = os.path.abspath(unreal.Paths.project_dir()).replace("\\", "/").rstrip("/")
level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
level = level_subsystem.get_current_level()
level_path = level.get_outermost().get_name() if level else ""
if project_name != EXPECTED_PROJECT or not project_directory.endswith(EXPECTED_DIRECTORY_SUFFIX):
    raise RuntimeError("ABIVERD_LANDMARK_V2_WRONG_PROJECT")
if level_path != EXPECTED_LEVEL:
    if not level_subsystem.load_level(EXPECTED_LEVEL):
        raise RuntimeError("ABIVERD_LANDMARK_V2_LOAD_FAILED")
    level = level_subsystem.get_current_level()
    level_path = level.get_outermost().get_name() if level else ""
if level_path != EXPECTED_LEVEL:
    raise RuntimeError("ABIVERD_LANDMARK_V2_WRONG_LEVEL " + level_path)
if dirty_packages():
    raise RuntimeError("ABIVERD_LANDMARK_V2_DIRTY_BEFORE " + "|".join(dirty_packages()))

working_box = unreal.Box(
    min=unreal.Vector(-3000.0, 14000.0, -100000.0),
    max=unreal.Vector(6500.0, 23000.0, 100000.0),
)
descriptors = list(unreal.WorldPartitionBlueprintLibrary.get_intersecting_actor_descs(working_box))
unreal.WorldPartitionBlueprintLibrary.load_actors([item.guid for item in descriptors])
unreal.WorldPartitionBlueprintLibrary.pin_actors([item.guid for item in descriptors])
if dirty_packages():
    raise RuntimeError("ABIVERD_LANDMARK_V2_LOAD_DIRTY")

actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
actors = list(actor_subsystem.get_all_level_actors())
if any(PASS_TAG in list(actor.tags) for actor in actors):
    raise RuntimeError("ABIVERD_LANDMARK_V2_DUPLICATE")
landscapes = [actor for actor in actors if isinstance(actor, unreal.LandscapeProxy)]
ignored = [actor for actor in actors if actor not in landscapes]

cube = load_asset(CUBE_PATH, unreal.StaticMesh)
wall_scan = load_asset(WALL_SCAN_PATH, unreal.StaticMesh)
stone = load_asset(STONE_PATH, unreal.StaticMesh)
mud_material = load_asset(MUD_MATERIAL_PATH, unreal.MaterialInterface)
brick_material = load_asset(BRICK_MATERIAL_PATH, unreal.MaterialInterface)


def terrain_z(x, y):
    hit = unreal.SystemLibrary.line_trace_single(
        world,
        unreal.Vector(x, y, 100000.0),
        unreal.Vector(x, y, -100000.0),
        unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
        True,
        ignored,
        unreal.DrawDebugTrace.NONE,
        True,
    )
    if hit is None:
        return None
    data = hit.to_dict()
    if not data.get("blocking_hit") or data.get("location") is None:
        return None
    return float(data["location"].z)


placements = []

# SS_023: a 3.4 m outside-diameter polygonal masonry well at the eastern edge
# of the central route, leaving the main assault lane clear.
well_x, well_y = 1800.0, 20500.0
ring_segments = 16
ring_radius = 170.0
segment_length = 2.0 * ring_radius * math.tan(math.pi / ring_segments) + 8.0
for index in range(ring_segments):
    angle = 360.0 * index / ring_segments
    radians = math.radians(angle)
    placements.append(
        {
            "label": "ABV_SS023_WellRing_%02d" % (index + 1),
            "site": "SS_023",
            "mesh": cube,
            "x": well_x + math.cos(radians) * ring_radius,
            "y": well_y + math.sin(radians) * ring_radius,
            "yaw": angle + 90.0,
            "scale": unreal.Vector(segment_length / 100.0, 0.42, 0.72),
            "material": brick_material,
            "collision": True,
        }
    )

# Low remnants and scan fragments make the court read archaeologically while
# preserving movement around the well.
court_fragments = (
    ("NorthWest", 1050.0, 21150.0, 8.0, 520.0),
    ("NorthEast", 2550.0, 21150.0, -12.0, 470.0),
    ("SouthWest", 950.0, 19850.0, -18.0, 430.0),
    ("SouthEast", 2650.0, 19850.0, 14.0, 500.0),
)
for suffix, x, y, yaw, length in court_fragments:
    placements.append(
        {
            "label": "ABV_SS023_CourtWall_" + suffix,
            "site": "SS_023",
            "mesh": cube,
            "x": x,
            "y": y,
            "yaw": yaw,
            "scale": unreal.Vector(length / 100.0, 0.48, 0.85),
            "material": mud_material,
            "collision": True,
        }
    )
for index, (x, y, yaw, scale) in enumerate(
    ((800.0, 20550.0, 75.0, 0.92), (2850.0, 20480.0, 250.0, 1.05)), 1
):
    placements.append(
        {
            "label": "ABV_SS023_StoneDress_%02d" % index,
            "site": "SS_023",
            "mesh": stone,
            "x": x,
            "y": y,
            "yaw": yaw,
            "scale": unreal.Vector(scale, scale, scale),
            "material": None,
            "collision": False,
        }
    )

# SS_021: grounded buttresses and two eroded wall scans strengthen the mosque
# silhouette without replacing its playable collision shell.
for suffix, x, y in (
    ("SW", 700.0, 15700.0),
    ("SE", 2500.0, 15700.0),
    ("NW", 700.0, 17300.0),
    ("NE", 2500.0, 17300.0),
):
    placements.append(
        {
            "label": "ABV_SS021_Buttress_" + suffix,
            "site": "SS_021",
            "mesh": cube,
            "x": x,
            "y": y,
            "yaw": 0.0,
            "scale": unreal.Vector(1.15, 1.15, 4.20),
            "material": mud_material,
            "collision": True,
        }
    )
for suffix, x, y, yaw in (
    ("West", 635.0, 16600.0, 90.0),
    ("East", 2565.0, 16600.0, -90.0),
):
    placements.append(
        {
            "label": "ABV_SS021_ErodedWall_" + suffix,
            "site": "SS_021",
            "mesh": wall_scan,
            "x": x,
            "y": y,
            "yaw": yaw,
            "scale": unreal.Vector(1.05, 1.05, 1.05),
            "material": None,
            "collision": False,
        }
    )

created = []
created_packages = []
for item in placements:
    ground = terrain_z(item["x"], item["y"])
    if ground is None:
        raise RuntimeError("ABIVERD_LANDMARK_V2_TRACE " + item["label"])
    bounds = item["mesh"].get_bounds()
    local_bottom = (bounds.origin.z - bounds.box_extent.z) * item["scale"].z
    actor = actor_subsystem.spawn_actor_from_object(
        item["mesh"],
        unreal.Vector(item["x"], item["y"], ground - local_bottom),
        unreal.Rotator(roll=0.0, pitch=0.0, yaw=item["yaw"]),
        transient=False,
    )
    if actor is None:
        raise RuntimeError("ABIVERD_LANDMARK_V2_SPAWN " + item["label"])
    actor.set_actor_scale3d(item["scale"])
    actor.set_actor_label(item["label"])
    actor.set_folder_path(unreal.Name(FOLDER_ROOT + "/" + item["site"]))
    actor.tags = [PASS_TAG, unreal.Name(item["site"]), unreal.Name("AbiverdHeritageV2")]
    component = actor.static_mesh_component
    if item["material"] is not None:
        component.set_material(0, item["material"])
    component.set_collision_enabled(
        unreal.CollisionEnabled.QUERY_AND_PHYSICS
        if item["collision"]
        else unreal.CollisionEnabled.NO_COLLISION
    )
    created.append(item["label"])
    created_packages.append(package_name(actor.get_package()))

dirty_before_save = dirty_packages()
expected = set(created_packages)
unexpected = [
    name for name in dirty_before_save
    if name not in expected
    and not name.startswith("/Game/__ExternalObjects__/Maps/Blockout/Lvl_Blockout_01/")
]
if unexpected:
    raise RuntimeError("ABIVERD_LANDMARK_V2_UNEXPECTED_DIRTY " + "|".join(unexpected))
packages = list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()) + list(
    unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()
)
if not unreal.EditorLoadingAndSavingUtils.save_packages(packages, True):
    raise RuntimeError("ABIVERD_LANDMARK_V2_SAVE_FAILED")
remaining = dirty_packages()
if remaining:
    raise RuntimeError("ABIVERD_LANDMARK_V2_DIRTY_AFTER " + "|".join(remaining))

report_root = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
os.makedirs(report_root, exist_ok=True)
report_path = os.path.join(report_root, REPORT_NAME)
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(
        {
            "schema_version": 2,
            "status": "landmark_completion_saved",
            "context": {"project": project_name, "project_directory": project_directory, "level": level_path},
            "well_center_cm": [well_x, well_y],
            "well_outer_diameter_cm": 2.0 * ring_radius + 42.0,
            "created_actor_count": len(created),
            "created_actor_labels": created,
            "saved_packages": dirty_before_save,
            "dirty_packages_after": remaining,
        },
        handle,
        indent=2,
    )
    handle.write("\n")

unreal.log("ABIVERD_LANDMARK_V2_COMPLETE actors=%d report=%s" % (len(created), report_path))
print("ABIVERD_LANDMARK_V2_COMPLETE", len(created), report_path)
