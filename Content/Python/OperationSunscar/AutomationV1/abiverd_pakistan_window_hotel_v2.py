"""DEPRECATED: rejected full-storey Pakistan window-module Hotel experiment.

The purchased scan is a complete 3.48 m-tall masonry wall module, not a window
insert. Visual review rejected this approach after the earlier civic placement
read as oversized brick slabs attached to plaster shells. This script is kept
only as an audit trail and is deliberately blocked from execution.
"""

import json
import os

import unreal


APPLY_CHANGES = False
DEPRECATED = True
DEPRECATED_REASON = (
    "Full-storey Historic Pakistan Street Window Brick Modular 04 is not suitable "
    "as a window insert; use opening-scale trim or rebuild a compatible wall bay."
)
EXPECTED_PROJECT = "TacticalMovement"
EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development"
EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
MESH_PATH = (
    "/Game/Maps/Sunscar/Art/Heritage/Architecture/PakistanWindowModular04/"
    "SM_wk0hehv_tier_1/StaticMeshes/SM_wk0hehv_tier_1"
)
ACTOR_LABEL = "ABV_OldTown_PakistanWindowFacade_HISM_V1"
PASS_TAG = unreal.Name("SunscarAbiverdPakistanWindowFacadeV1")
COMPONENT_NAME = "HISM_PakistanWindowModular04_Hotel"
UNIFORM_SCALE = 0.82
START_CULL_CM = 12000
END_CULL_CM = 30000
FACADE_PLAN = (
    # Four formal bays on both street-facing south storeys.
    ("Core_SS_007_F2_S_Wall", (-2450.0, -1750.0, -1050.0, -350.0)),
    ("Core_SS_007_F3_S_Wall", (-2450.0, -1750.0, -1050.0, -350.0)),
    # Three calmer service-side bays on both north storeys.
    ("Core_SS_007_F2_N_Wall", (-2250.0, -1400.0, -550.0)),
    ("Core_SS_007_F3_N_Wall", (-2250.0, -1400.0, -550.0)),
    # One three-bay vertical accent per side, staggered by storey.
    ("Core_SS_007_F2_E_Wall", (2050.0, 2700.0, 3350.0)),
    ("Core_SS_007_F3_W_Wall", (2050.0, 2700.0, 3350.0)),
)
EXPECTED_INSTANCE_COUNT = 20
REPORT_NAME = (
    "abiverd_pakistan_window_hotel_apply_v2.json"
    if APPLY_CHANGES
    else "abiverd_pakistan_window_hotel_dry_run_v2.json"
)

if DEPRECATED:
    raise RuntimeError("ABIVERD_PAK_WINDOW_HOTEL_V2_DEPRECATED " + DEPRECATED_REASON)


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


def actor_and_root_handles(subsystem, actor):
    actor_handle = None
    root_handle = None
    for handle in subsystem.k2_gather_subobject_data_for_instance(actor):
        data = unreal.SubobjectDataBlueprintFunctionLibrary.get_data(handle)
        if unreal.SubobjectDataBlueprintFunctionLibrary.is_actor(data):
            actor_handle = handle
        elif unreal.SubobjectDataBlueprintFunctionLibrary.is_root_component(data):
            root_handle = handle
    if actor_handle is None or root_handle is None:
        raise RuntimeError("ABIVERD_PAK_WINDOW_HOTEL_V2_HANDLES")
    return actor_handle, root_handle


project_name = os.path.splitext(os.path.basename(unreal.Paths.get_project_file_path()))[0]
project_directory = os.path.abspath(unreal.Paths.project_dir()).replace("\\", "/").rstrip("/")
if project_name != EXPECTED_PROJECT or not project_directory.endswith(EXPECTED_DIRECTORY_SUFFIX):
    raise RuntimeError("ABIVERD_PAK_WINDOW_HOTEL_V2_WRONG_PROJECT")
level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
level = level_subsystem.get_current_level()
level_path = level.get_outermost().get_name() if level else ""
if level_path != EXPECTED_LEVEL:
    raise RuntimeError("ABIVERD_PAK_WINDOW_HOTEL_V2_WRONG_LEVEL " + level_path)
if dirty_packages():
    raise RuntimeError("ABIVERD_PAK_WINDOW_HOTEL_V2_DIRTY_BEFORE " + "|".join(dirty_packages()))

working_box = unreal.Box(
    min=unreal.Vector(-12500.0, -11500.0, -100000.0),
    max=unreal.Vector(15500.0, 11500.0, 100000.0),
)
descriptors = list(unreal.WorldPartitionBlueprintLibrary.get_intersecting_actor_descs(working_box))
unreal.WorldPartitionBlueprintLibrary.load_actors([item.guid for item in descriptors])
unreal.WorldPartitionBlueprintLibrary.pin_actors([item.guid for item in descriptors])
if dirty_packages():
    raise RuntimeError("ABIVERD_PAK_WINDOW_HOTEL_V2_LOAD_DIRTY")

mesh = unreal.EditorAssetLibrary.load_asset(MESH_PATH)
if not isinstance(mesh, unreal.StaticMesh):
    raise RuntimeError("ABIVERD_PAK_WINDOW_HOTEL_V2_MESH_MISSING")
bounds = mesh.get_bounds()
mesh_width = bounds.box_extent.x * 2.0
mesh_depth = bounds.box_extent.y * 2.0
mesh_height = bounds.box_extent.z * 2.0
local_min_z = bounds.origin.z - bounds.box_extent.z
if not (250.0 <= mesh_width <= 275.0 and 40.0 <= mesh_depth <= 55.0 and 335.0 <= mesh_height <= 360.0):
    raise RuntimeError("ABIVERD_PAK_WINDOW_HOTEL_V2_BOUNDS")

actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors = list(actor_subsystem.get_all_level_actors())
by_label = {actor.get_actor_label(): actor for actor in actors}
matches = [actor for actor in actors if actor.get_actor_label() == ACTOR_LABEL or PASS_TAG in list(actor.tags)]
if len(matches) != 1:
    raise RuntimeError("ABIVERD_PAK_WINDOW_HOTEL_V2_ACTOR_COUNT %d" % len(matches))
facade_actor = matches[0]
if bool(facade_actor.get_editor_property("replicates")):
    raise RuntimeError("ABIVERD_PAK_WINDOW_HOTEL_V2_REPLICATED")
existing_components = list(
    facade_actor.get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent)
)
hotel_components = [component for component in existing_components if component.get_name() == COMPONENT_NAME]
if len(hotel_components) > 1:
    raise RuntimeError("ABIVERD_PAK_WINDOW_HOTEL_V2_DUPLICATE_COMPONENT")
missing_walls = sorted(label for label, _positions in FACADE_PLAN if label not in by_label)
if missing_walls:
    raise RuntimeError("ABIVERD_PAK_WINDOW_HOTEL_V2_MISSING_WALLS " + repr(missing_walls))

rows = []
transforms = []
scaled_depth = mesh_depth * UNIFORM_SCALE
for wall_label, positions in FACADE_PLAN:
    wall = by_label[wall_label]
    if not isinstance(wall, unreal.StaticMeshActor):
        raise RuntimeError("ABIVERD_PAK_WINDOW_HOTEL_V2_WALL_CLASS " + wall_label)
    origin, extent = wall.get_actor_bounds(False)
    dimensions = extent * 2.0
    along_x = dimensions.x >= dimensions.y
    floor_base_z = origin.z - extent.z
    z = floor_base_z - local_min_z * UNIFORM_SCALE
    for position in positions:
        if along_x:
            outward = 1.0 if origin.y > 2700.0 else -1.0
            x = position
            y = origin.y + outward * (extent.y + scaled_depth * 0.5 - 6.0)
            yaw = 180.0 if outward > 0.0 else 0.0
        else:
            outward = 1.0 if origin.x > -1400.0 else -1.0
            x = origin.x + outward * (extent.x + scaled_depth * 0.5 - 6.0)
            y = position
            yaw = 90.0 if outward > 0.0 else -90.0
        transform = unreal.Transform()
        transform.translation = unreal.Vector(x, y, z)
        transform.rotation = unreal.MathLibrary.conv_rotator_to_quaternion(
            unreal.Rotator(roll=0.0, pitch=0.0, yaw=yaw)
        )
        transform.scale3d = unreal.Vector(UNIFORM_SCALE, UNIFORM_SCALE, UNIFORM_SCALE)
        transforms.append(transform)
        rows.append(
            {
                "wall": wall_label,
                "location_cm": [round(x, 3), round(y, 3), round(z, 3)],
                "yaw_deg": yaw,
                "uniform_scale": UNIFORM_SCALE,
                "scaled_bounds_cm": [
                    round(mesh_width * UNIFORM_SCALE, 3),
                    round(mesh_depth * UNIFORM_SCALE, 3),
                    round(mesh_height * UNIFORM_SCALE, 3),
                ],
            }
        )

if len(transforms) != EXPECTED_INSTANCE_COUNT:
    raise RuntimeError("ABIVERD_PAK_WINDOW_HOTEL_V2_COUNT %d" % len(transforms))

saved_packages = []
if APPLY_CHANGES:
    facade_actor.modify()
    if hotel_components:
        component = hotel_components[0]
        component.modify()
        component.clear_instances()
    else:
        subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
        _actor_handle, root_handle = actor_and_root_handles(subsystem, facade_actor)
        component_handle, failure = subsystem.add_new_subobject(
            unreal.AddNewSubobjectParams(
                parent_handle=root_handle,
                new_class=unreal.HierarchicalInstancedStaticMeshComponent.static_class(),
            )
        )
        if not failure.is_empty():
            raise RuntimeError("ABIVERD_PAK_WINDOW_HOTEL_V2_COMPONENT " + str(failure))
        subsystem.rename_subobject(component_handle, unreal.Text(COMPONENT_NAME))
        component_data = unreal.SubobjectDataBlueprintFunctionLibrary.get_data(component_handle)
        component = unreal.SubobjectDataBlueprintFunctionLibrary.get_associated_object(component_data)

    component.set_static_mesh(mesh)
    component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    component.set_cast_shadow(True)
    component.set_editor_property("instance_start_cull_distance", START_CULL_CM)
    component.set_editor_property("instance_end_cull_distance", END_CULL_CM)
    try:
        component.set_editor_property("can_ever_affect_navigation", False)
    except Exception:
        pass
    for transform in transforms:
        component.add_instance(transform, world_space=True)
    if component.get_instance_count() != EXPECTED_INSTANCE_COUNT:
        raise RuntimeError("ABIVERD_PAK_WINDOW_HOTEL_V2_INSTANCE_COUNT")

    before_save = dirty_packages()
    allowed_prefixes = (
        "/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/",
        "/Game/__ExternalObjects__/Maps/Blockout/Lvl_Blockout_01/",
    )
    unexpected = [name for name in before_save if not name.startswith(allowed_prefixes)]
    if unexpected:
        raise RuntimeError("ABIVERD_PAK_WINDOW_HOTEL_V2_UNEXPECTED_DIRTY " + "|".join(unexpected))
    packages = list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()) + list(
        unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()
    )
    saved_packages = [package_name(package) for package in packages]
    if not unreal.EditorLoadingAndSavingUtils.save_packages(packages, True):
        raise RuntimeError("ABIVERD_PAK_WINDOW_HOTEL_V2_SAVE_FAILED")
    if dirty_packages():
        raise RuntimeError("ABIVERD_PAK_WINDOW_HOTEL_V2_DIRTY_AFTER " + "|".join(dirty_packages()))

report = {
    "schema_version": 2,
    "status": "applied_and_saved" if APPLY_CHANGES else "dry_run_complete",
    "context": {"project": project_name, "project_directory": project_directory, "level": level_path},
    "source_mesh": MESH_PATH,
    "source_bounds_cm": [round(mesh_width, 3), round(mesh_depth, 3), round(mesh_height, 3)],
    "uniform_scale": UNIFORM_SCALE,
    "instance_count": len(rows),
    "facade_counts": {
        "south": 8,
        "north": 6,
        "east": 3,
        "west": 3,
    },
    "placements": rows,
    "saved_packages": sorted(saved_packages),
    "dirty_after": dirty_packages(),
    "policies": {
        "scope": "Municipal Hotel upper storeys only",
        "gameplay_shell": "unchanged and authoritative for collision/navigation",
        "collision": "decorative Hotel HISM uses NoCollision",
        "replication": "existing static non-replicated facade actor",
        "performance": "one additional HISM component; Nanite source; 12m/30m culling; 2K runtime textures",
        "placement": "20 uniformly scaled modules; no non-uniform distortion",
    },
}
report_root = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
os.makedirs(report_root, exist_ok=True)
report_path = os.path.join(report_root, REPORT_NAME)
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(report, handle, indent=2)
    handle.write("\n")

unreal.log(
    "ABIVERD_PAK_WINDOW_HOTEL_V2_COMPLETE apply=%s instances=%d" % (APPLY_CHANGES, len(rows))
)
print("ABIVERD_PAK_WINDOW_HOTEL_V2_COMPLETE", report_path)
