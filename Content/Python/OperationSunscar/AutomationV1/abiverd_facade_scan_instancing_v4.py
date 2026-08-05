"""Instance verified Quixel ruin-wall modules on selected Old Town façades."""

import hashlib
import json
import os

import unreal


EXPECTED_PROJECT = "TacticalMovement"
EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development"
EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
PASS_TAG = unreal.Name("SunscarAbiverdFacadeScanV4")
ACTOR_LABEL = "ABV_OldTown_FacadeScan_HISM_V4"
FOLDER = "OperationSunscar/AbiverdStructuralSkinV4/Facades"
REPORT_NAME = "abiverd_facade_scan_instancing_v4.json"
WALL_SCAN_PATH = "/Game/Maps/Sunscar/Art/Heritage/Architecture/WallModularSet04/Historic_Desert_Ruin_Wall_Modular_Set_04_yjxsbaqyx_High"
TARGET_SITES = {"SS_004", "SS_005", "SS_007", "SS_010", "SS_012", "SS_017", "SS_018"}
SOURCE_WIDTH_CM = 323.0
SOURCE_HEIGHT_CM = 326.0
UNIFORM_SCALE = 0.92


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


def actor_site(actor):
    for tag in actor.tags:
        value = str(tag)
        if value.startswith("Building_"):
            return value[len("Building_"):]
    return ""


def stable_bucket(value, modulo):
    digest = hashlib.sha1(value.encode("utf-8")).digest()
    return int.from_bytes(digest[:2], "big") % modulo


def actor_and_root_handles(subsystem, actor):
    actor_handle = None
    root_handle = None
    for handle in subsystem.k2_gather_subobject_data_for_instance(actor):
        data = unreal.SubobjectDataBlueprintFunctionLibrary.get_data(handle)
        if unreal.SubobjectDataBlueprintFunctionLibrary.is_actor(data):
            actor_handle = handle
        elif unreal.SubobjectDataBlueprintFunctionLibrary.is_root_component(data):
            root_handle = handle
    if actor_handle is None:
        raise RuntimeError("ABIVERD_FACADE_V4_ACTOR_HANDLE")
    if root_handle is None:
        root_handle, failure = subsystem.add_new_subobject(
            unreal.AddNewSubobjectParams(parent_handle=actor_handle, new_class=unreal.SceneComponent.static_class())
        )
        if not failure.is_empty():
            raise RuntimeError("ABIVERD_FACADE_V4_ROOT " + str(failure))
        subsystem.rename_subobject(root_handle, unreal.Text("DefaultSceneRoot"))
    return actor_handle, root_handle


project_name = os.path.splitext(os.path.basename(unreal.Paths.get_project_file_path()))[0]
project_directory = os.path.abspath(unreal.Paths.project_dir()).replace("\\", "/").rstrip("/")
level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
level = level_subsystem.get_current_level()
level_path = level.get_outermost().get_name() if level else ""
if project_name != EXPECTED_PROJECT or not project_directory.endswith(EXPECTED_DIRECTORY_SUFFIX):
    raise RuntimeError("ABIVERD_FACADE_V4_WRONG_PROJECT")
if level_path != EXPECTED_LEVEL:
    if not level_subsystem.load_level(EXPECTED_LEVEL):
        raise RuntimeError("ABIVERD_FACADE_V4_LOAD_FAILED")
    level = level_subsystem.get_current_level()
    level_path = level.get_outermost().get_name() if level else ""
if level_path != EXPECTED_LEVEL:
    raise RuntimeError("ABIVERD_FACADE_V4_WRONG_LEVEL " + level_path)
if dirty_packages():
    raise RuntimeError("ABIVERD_FACADE_V4_DIRTY_BEFORE " + "|".join(dirty_packages()))

working_box = unreal.Box(
    min=unreal.Vector(-12500.0, -11500.0, -100000.0),
    max=unreal.Vector(15500.0, 11500.0, 100000.0),
)
descriptors = list(unreal.WorldPartitionBlueprintLibrary.get_intersecting_actor_descs(working_box))
unreal.WorldPartitionBlueprintLibrary.load_actors([item.guid for item in descriptors])
unreal.WorldPartitionBlueprintLibrary.pin_actors([item.guid for item in descriptors])
if dirty_packages():
    raise RuntimeError("ABIVERD_FACADE_V4_LOAD_DIRTY")

actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors = list(actor_subsystem.get_all_level_actors())
existing_matches = [
    actor for actor in actors
    if PASS_TAG in list(actor.tags) or actor.get_actor_label() == ACTOR_LABEL
]
if len(existing_matches) > 1:
    raise RuntimeError("ABIVERD_FACADE_V4_DUPLICATE %d" % len(existing_matches))

wall_scan = unreal.EditorAssetLibrary.load_asset(WALL_SCAN_PATH)
if not isinstance(wall_scan, unreal.StaticMesh):
    raise RuntimeError("ABIVERD_FACADE_V4_MISSING_SCAN")
source_bounds = wall_scan.get_bounds()
# Imported mesh axes are X=3.23 m width, Y=3.26 m height, Z=0.70 m depth.
# Roll +90 degrees maps local Y to world Z, so vertical grounding uses Y-min.
local_vertical_min = source_bounds.origin.y - source_bounds.box_extent.y

rows = []
site_counts = {}
candidate_walls = []
for actor in actors:
    if not isinstance(actor, unreal.StaticMeshActor):
        continue
    if unreal.Name("CoreCategory_Building") not in list(actor.tags):
        continue
    site = actor_site(actor)
    if site not in TARGET_SITES:
        continue
    label = actor.get_actor_label()
    # Use uninterrupted wall spans only; openings and their adjacent Left/Right
    # shell pieces remain visibly clear and retain their existing door/window art.
    if not label.endswith("_Wall"):
        continue
    if stable_bucket(label, 4) >= 3:
        continue
    origin, extent = actor.get_actor_bounds(False)
    if extent.z < 110.0:
        continue
    along_x = extent.x >= extent.y
    length = extent.x * 2.0 if along_x else extent.y * 2.0
    if length < 300.0:
        continue
    candidate_walls.append(label)

    count = min(3, max(1, int(length / 450.0)))
    spacing = length / float(count + 1)
    wall_bottom = origin.z - extent.z
    module_z = wall_bottom - local_vertical_min * UNIFORM_SCALE
    yaw = 0.0 if along_x else 90.0
    for index in range(count):
        offset = -length * 0.5 + spacing * float(index + 1)
        x = origin.x + offset if along_x else origin.x
        y = origin.y if along_x else origin.y + offset
        transform = unreal.Transform()
        transform.translation = unreal.Vector(x, y, module_z)
        transform.rotation = unreal.MathLibrary.conv_rotator_to_quaternion(
            unreal.Rotator(roll=90.0, pitch=0.0, yaw=yaw)
        )
        transform.scale3d = unreal.Vector(UNIFORM_SCALE, UNIFORM_SCALE, UNIFORM_SCALE)
        rows.append(transform)
        site_counts[site] = site_counts.get(site, 0) + 1

if len(rows) < 12:
    raise RuntimeError("ABIVERD_FACADE_V4_TOO_FEW_INSTANCES %d" % len(rows))

if existing_matches:
    facade_actor = existing_matches[0]
    components = list(
        facade_actor.get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent)
    )
    if len(components) != 1:
        raise RuntimeError("ABIVERD_FACADE_V4_EXISTING_COMPONENTS %d" % len(components))
    component = components[0]
    facade_actor.modify()
    component.modify()
    component.clear_instances()
else:
    facade_actor = actor_subsystem.spawn_actor_from_class(
        unreal.Actor, unreal.Vector(0.0, 0.0, 0.0), unreal.Rotator(), transient=False
    )
    if facade_actor is None:
        raise RuntimeError("ABIVERD_FACADE_V4_SPAWN_ACTOR")
    facade_actor.set_actor_label(ACTOR_LABEL)
    facade_actor.set_folder_path(unreal.Name(FOLDER))
    facade_actor.tags = [PASS_TAG, unreal.Name("AbiverdStructuralSkinV4"), unreal.Name("QuixelMegascans")]
    facade_actor.set_replicates(False)

    subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
    if subsystem is None:
        raise RuntimeError("ABIVERD_FACADE_V4_SUBOBJECT_SYSTEM")
    _actor_handle, root_handle = actor_and_root_handles(subsystem, facade_actor)
    component_handle, failure = subsystem.add_new_subobject(
        unreal.AddNewSubobjectParams(
            parent_handle=root_handle,
            new_class=unreal.HierarchicalInstancedStaticMeshComponent.static_class(),
        )
    )
    if not failure.is_empty():
        raise RuntimeError("ABIVERD_FACADE_V4_COMPONENT " + str(failure))
    subsystem.rename_subobject(component_handle, unreal.Text("HISM_QuixelRuinWallFacade"))
    component_data = unreal.SubobjectDataBlueprintFunctionLibrary.get_data(component_handle)
    component = unreal.SubobjectDataBlueprintFunctionLibrary.get_associated_object(component_data)
    if not isinstance(component, unreal.HierarchicalInstancedStaticMeshComponent):
        raise RuntimeError("ABIVERD_FACADE_V4_COMPONENT_TYPE")
component.set_static_mesh(wall_scan)
component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
component.set_cast_shadow(True)
component.set_editor_property("instance_start_cull_distance", 12000)
component.set_editor_property("instance_end_cull_distance", 36000)
try:
    component.set_editor_property("can_ever_affect_navigation", False)
except Exception:
    pass
for transform in rows:
    component.add_instance_world_space(transform)
if component.get_instance_count() != len(rows):
    raise RuntimeError("ABIVERD_FACADE_V4_INSTANCE_COUNT")

dirty_before_save = dirty_packages()
allowed_prefixes = (
    "/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/",
    "/Game/__ExternalObjects__/Maps/Blockout/Lvl_Blockout_01/",
)
unexpected = [name for name in dirty_before_save if not name.startswith(allowed_prefixes)]
if unexpected:
    raise RuntimeError("ABIVERD_FACADE_V4_UNEXPECTED_DIRTY " + "|".join(unexpected))
packages = list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()) + list(
    unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()
)
if not unreal.EditorLoadingAndSavingUtils.save_packages(packages, True):
    raise RuntimeError("ABIVERD_FACADE_V4_SAVE_FAILED")
remaining = dirty_packages()
if remaining:
    raise RuntimeError("ABIVERD_FACADE_V4_DIRTY_AFTER " + "|".join(remaining))

report = {
    "schema_version": 4,
    "status": "abiverd_facade_scan_instances_saved",
    "context": {"project": project_name, "project_directory": project_directory, "level": level_path},
    "source_mesh": wall_scan.get_path_name(),
    "source_reference_dimensions_cm_xyz": [SOURCE_WIDTH_CM, SOURCE_HEIGHT_CM, 70.0],
    "axis_correction": "roll_90_maps_local_y_to_world_z",
    "uniform_scale": UNIFORM_SCALE,
    "candidate_wall_count": len(candidate_walls),
    "instance_count": len(rows),
    "site_instance_counts": dict(sorted(site_counts.items())),
    "actor_package": package_name(facade_actor.get_package()),
    "dirty_before_save": dirty_before_save,
    "dirty_after_save": remaining,
    "policies": {
        "collision": "NoCollision; existing gameplay shells retained",
        "replication": "Static non-replicated HISM actor",
        "nanite": "Source mesh retains verified Nanite configuration",
        "openings": "Door/window-adjacent Left/Right and lintel actors excluded",
    },
}
report_root = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
os.makedirs(report_root, exist_ok=True)
report_path = os.path.join(report_root, REPORT_NAME)
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(report, handle, indent=2)
    handle.write("\n")

unreal.log(
    "ABIVERD_FACADE_V4_COMPLETE walls=%d instances=%d saved=%d"
    % (len(candidate_walls), len(rows), len(packages))
)
