"""Dry-run-first HISM lintel and sill pass for 40 Old Town windows."""

import json
import os
import re

import unreal


APPLY_CHANGES = False
EXPECTED_PROJECT = "TacticalMovement"
EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development"
EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
CUBE_PATH = "/Engine/BasicShapes/Cube.Cube"
MATERIAL_PATHS = {
    "brick": "/Game/Maps/Sunscar/Art/Heritage/Materials/MI_ABV_RuinBrick_WorldAligned",
    "mud": "/Game/Maps/Sunscar/Art/Heritage/Materials/MI_ABV_CrackedMud_WorldAligned",
}
FRAME_PATTERN = re.compile(r"^(.*(?:_Win_|_Window_).*)_Frame$", re.IGNORECASE)
PASS_TAG = unreal.Name("SunscarAbiverdWindowTrimV1")
ACTOR_LABEL = "ABV_OldTown_WindowTrim_HISM_V1"
FOLDER = "OperationSunscar/AbiverdStructuralSkinV6/WindowTrim"
START_CULL_CM = 12000
END_CULL_CM = 30000
LINTEL_WIDTH_CM = 205.0
LINTEL_DEPTH_CM = 26.0
LINTEL_HEIGHT_CM = 24.0
SILL_WIDTH_CM = 185.0
SILL_DEPTH_CM = 30.0
SILL_HEIGHT_CM = 16.0
REPORT_NAME = (
    "abiverd_window_trim_instancing_apply_v1.json"
    if APPLY_CHANGES
    else "abiverd_window_trim_instancing_dry_run_v1.json"
)


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


def make_transform(location, dimensions):
    transform = unreal.Transform()
    transform.translation = location
    transform.rotation = unreal.MathLibrary.conv_rotator_to_quaternion(unreal.Rotator())
    transform.scale3d = unreal.Vector(dimensions.x / 100.0, dimensions.y / 100.0, dimensions.z / 100.0)
    return transform


def material_key_for_label(label):
    return "mud" if label.lower().startswith(("pump_", "tea_")) else "brick"


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
        raise RuntimeError("ABIVERD_WINDOW_TRIM_HANDLES")
    return actor_handle, root_handle


def add_hism_component(actor, component_name):
    subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
    _actor_handle, root_handle = actor_and_root_handles(subsystem, actor)
    component_handle, failure = subsystem.add_new_subobject(
        unreal.AddNewSubobjectParams(
            parent_handle=root_handle,
            new_class=unreal.HierarchicalInstancedStaticMeshComponent.static_class(),
        )
    )
    if not failure.is_empty():
        raise RuntimeError("ABIVERD_WINDOW_TRIM_COMPONENT " + str(failure))
    subsystem.rename_subobject(component_handle, unreal.Text(component_name))
    component_data = unreal.SubobjectDataBlueprintFunctionLibrary.get_data(component_handle)
    component = unreal.SubobjectDataBlueprintFunctionLibrary.get_associated_object(component_data)
    if not isinstance(component, unreal.HierarchicalInstancedStaticMeshComponent):
        raise RuntimeError("ABIVERD_WINDOW_TRIM_COMPONENT_CLASS")
    return component


project_name = os.path.splitext(os.path.basename(unreal.Paths.get_project_file_path()))[0]
project_directory = os.path.abspath(unreal.Paths.project_dir()).replace("\\", "/").rstrip("/")
level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).get_current_level()
level_path = level.get_outermost().get_name() if level else ""
if project_name != EXPECTED_PROJECT or not project_directory.endswith(EXPECTED_DIRECTORY_SUFFIX):
    raise RuntimeError("ABIVERD_WINDOW_TRIM_WRONG_PROJECT")
if level_path != EXPECTED_LEVEL:
    raise RuntimeError("ABIVERD_WINDOW_TRIM_WRONG_LEVEL " + level_path)
if dirty_packages():
    raise RuntimeError("ABIVERD_WINDOW_TRIM_DIRTY_BEFORE " + "|".join(dirty_packages()))

working_box = unreal.Box(
    min=unreal.Vector(-12500.0, -11500.0, -100000.0),
    max=unreal.Vector(15500.0, 11500.0, 100000.0),
)
descriptors = list(unreal.WorldPartitionBlueprintLibrary.get_intersecting_actor_descs(working_box))
unreal.WorldPartitionBlueprintLibrary.load_actors([item.guid for item in descriptors])
unreal.WorldPartitionBlueprintLibrary.pin_actors([item.guid for item in descriptors])
if dirty_packages():
    raise RuntimeError("ABIVERD_WINDOW_TRIM_LOAD_DIRTY")

cube = unreal.EditorAssetLibrary.load_asset(CUBE_PATH)
materials = {key: unreal.EditorAssetLibrary.load_asset(path) for key, path in MATERIAL_PATHS.items()}
if not isinstance(cube, unreal.StaticMesh) or any(value is None for value in materials.values()):
    raise RuntimeError("ABIVERD_WINDOW_TRIM_ASSET_MISSING")

actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors = list(actor_subsystem.get_all_level_actors())
by_label = {actor.get_actor_label(): actor for actor in actors}
frames = []
for actor in actors:
    if isinstance(actor, unreal.StaticMeshActor) and FRAME_PATTERN.match(actor.get_actor_label()):
        frames.append(actor)
frames.sort(key=lambda actor: actor.get_actor_label().lower())
if len(frames) != 40:
    raise RuntimeError("ABIVERD_WINDOW_TRIM_FRAME_COUNT %d" % len(frames))

transforms_by_material = {key: [] for key in materials}
rows = []
for frame in frames:
    label = frame.get_actor_label()
    key = FRAME_PATTERN.match(label).group(1)
    glass = by_label.get(key + "_Glass")
    if not isinstance(glass, unreal.StaticMeshActor):
        raise RuntimeError("ABIVERD_WINDOW_TRIM_GLASS " + label)
    frame_origin, frame_extent = frame.get_actor_bounds(False)
    glass_origin, _glass_extent = glass.get_actor_bounds(False)
    dimensions = frame_extent * 2.0
    if not (160.0 <= dimensions.x <= 170.0 and 12.0 <= dimensions.y <= 20.0 and 140.0 <= dimensions.z <= 150.0):
        raise RuntimeError("ABIVERD_WINDOW_TRIM_BOUNDS " + label)
    if abs(glass_origin.y - frame_origin.y) < 5.0:
        raise RuntimeError("ABIVERD_WINDOW_TRIM_FACADE_NORMAL " + label)
    outward_y = 1.0 if glass_origin.y > frame_origin.y else -1.0
    material_key = material_key_for_label(label)
    lintel_location = unreal.Vector(
        frame_origin.x,
        frame_origin.y + outward_y * (frame_extent.y + LINTEL_DEPTH_CM * 0.5 - 4.0),
        frame_origin.z + frame_extent.z + LINTEL_HEIGHT_CM * 0.5,
    )
    sill_location = unreal.Vector(
        frame_origin.x,
        frame_origin.y + outward_y * (frame_extent.y + SILL_DEPTH_CM * 0.5 - 4.0),
        frame_origin.z - frame_extent.z - SILL_HEIGHT_CM * 0.5,
    )
    pieces = (
        ("lintel", lintel_location, unreal.Vector(LINTEL_WIDTH_CM, LINTEL_DEPTH_CM, LINTEL_HEIGHT_CM)),
        ("sill", sill_location, unreal.Vector(SILL_WIDTH_CM, SILL_DEPTH_CM, SILL_HEIGHT_CM)),
    )
    for role, location, piece_dimensions in pieces:
        transforms_by_material[material_key].append(make_transform(location, piece_dimensions))
        rows.append(
            {
                "source_frame": label,
                "role": role,
                "material_key": material_key,
                "location_cm": [round(location.x, 3), round(location.y, 3), round(location.z, 3)],
                "dimensions_cm": [round(piece_dimensions.x, 3), round(piece_dimensions.y, 3), round(piece_dimensions.z, 3)],
                "collision": "NoCollision",
            }
        )

if len(rows) != 80 or len(transforms_by_material["brick"]) != 70 or len(transforms_by_material["mud"]) != 10:
    raise RuntimeError(
        "ABIVERD_WINDOW_TRIM_COUNTS total=%d brick=%d mud=%d"
        % (len(rows), len(transforms_by_material["brick"]), len(transforms_by_material["mud"]))
    )

matches = [actor for actor in actors if actor.get_actor_label() == ACTOR_LABEL or PASS_TAG in list(actor.tags)]
if len(matches) > 1:
    raise RuntimeError("ABIVERD_WINDOW_TRIM_ACTOR_COUNT %d" % len(matches))

saved_packages = []
if APPLY_CHANGES:
    if matches:
        trim_actor = matches[0]
    else:
        trim_actor = actor_subsystem.spawn_actor_from_class(unreal.Actor, unreal.Vector(), unreal.Rotator(), transient=False)
        if trim_actor is None:
            raise RuntimeError("ABIVERD_WINDOW_TRIM_SPAWN")
        trim_actor.set_actor_label(ACTOR_LABEL)
        trim_actor.tags = [PASS_TAG, unreal.Name("QuixelMegascans"), unreal.Name("ExteriorWindowDetail")]
        trim_actor.set_folder_path(unreal.Name(FOLDER))
    trim_actor.modify()
    existing_components = list(trim_actor.get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent))
    components_by_name = {component.get_name(): component for component in existing_components}
    expected_names = {"HISM_WindowTrim_Brick", "HISM_WindowTrim_Mud"}
    unexpected_components = sorted(set(components_by_name) - expected_names)
    if unexpected_components:
        raise RuntimeError("ABIVERD_WINDOW_TRIM_COMPONENT_SCOPE " + repr(unexpected_components))
    for material_key in sorted(materials):
        component_name = "HISM_WindowTrim_%s" % material_key.title()
        component = components_by_name.get(component_name)
        if component is None:
            component = add_hism_component(trim_actor, component_name)
        component.modify()
        component.clear_instances()
        component.set_static_mesh(cube)
        component.set_material(0, materials[material_key])
        component.set_collision_profile_name("NoCollision")
        component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        component.set_cast_shadow(True)
        component.set_editor_property("instance_start_cull_distance", START_CULL_CM)
        component.set_editor_property("instance_end_cull_distance", END_CULL_CM)
        try:
            component.set_editor_property("can_ever_affect_navigation", False)
        except Exception:
            pass
        for transform in transforms_by_material[material_key]:
            component.add_instance(transform, world_space=True)
        if component.get_instance_count() != len(transforms_by_material[material_key]):
            raise RuntimeError("ABIVERD_WINDOW_TRIM_INSTANCE_COUNT " + material_key)

    before_save = dirty_packages()
    allowed_prefixes = (
        "/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/",
        "/Game/__ExternalObjects__/Maps/Blockout/Lvl_Blockout_01/",
    )
    unexpected = [name for name in before_save if not name.startswith(allowed_prefixes)]
    if unexpected:
        raise RuntimeError("ABIVERD_WINDOW_TRIM_UNEXPECTED_DIRTY " + "|".join(unexpected))
    packages = list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()) + list(
        unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()
    )
    saved_packages = [package_name(package) for package in packages]
    if not unreal.EditorLoadingAndSavingUtils.save_packages(packages, True):
        raise RuntimeError("ABIVERD_WINDOW_TRIM_SAVE_FAILED")
    if dirty_packages():
        raise RuntimeError("ABIVERD_WINDOW_TRIM_DIRTY_AFTER " + "|".join(dirty_packages()))

report = {
    "schema_version": 1,
    "status": "applied_and_saved" if APPLY_CHANGES else "dry_run_complete",
    "context": {"project": project_name, "project_directory": project_directory, "level": level_path},
    "window_count": len(frames),
    "piece_count": len(rows),
    "material_instance_counts": {key: len(value) for key, value in sorted(transforms_by_material.items())},
    "placements": rows,
    "saved_packages": sorted(saved_packages),
    "dirty_after": dirty_packages(),
    "policies": {
        "geometry": "two shallow opening-scale pieces per window; existing frame and gameplay shell preserved",
        "collision": "NoCollision; building shells remain authoritative",
        "performance": "one non-replicated actor, two HISM components, 12m/30m culling, no navigation influence",
    },
}
report_root = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
os.makedirs(report_root, exist_ok=True)
report_path = os.path.join(report_root, REPORT_NAME)
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(report, handle, indent=2)
    handle.write("\n")
unreal.log("ABIVERD_WINDOW_TRIM_COMPLETE apply=%s windows=40 pieces=80" % APPLY_CHANGES)
print("ABIVERD_WINDOW_TRIM_COMPLETE", report_path)
