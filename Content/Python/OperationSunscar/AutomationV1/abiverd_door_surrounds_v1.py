"""Dry-run-first masonry surrounds for verified Old Town door meshes.

The existing Quixel doors and gameplay collision stay authoritative. This pass
adds non-colliding jamb/lintel dressing through two material-batched HISM
components, using Epic's cube primitive and existing map-owned Quixel-derived
Abiverd materials.
"""

import json
import os

import unreal


APPLY_CHANGES = False
EXPECTED_PROJECT = "TacticalMovement"
EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development"
EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
CUBE_PATH = "/Engine/BasicShapes/Cube.Cube"
MATERIAL_PATHS = {
    "mud": "/Game/Maps/Sunscar/Art/Heritage/Materials/MI_ABV_CrackedMud_WorldAligned",
    "brick": "/Game/Maps/Sunscar/Art/Heritage/Materials/MI_ABV_RuinBrick_WorldAligned",
}
DOOR_SITES = {
    "Tea_MainDoor": ("SS_004", "mud"),
    "Clinic_MainDoor": ("SS_005", "brick"),
    "Clinic_ServiceDoor": ("SS_005", "brick"),
    "Detention_Door_12": ("SS_010", "brick"),
    "Detention_Door_22": ("SS_010", "brick"),
    "Detention_Door_32": ("SS_010", "brick"),
    "Consulate_Door_A": ("SS_012", "mud"),
    "Consulate_Door_B": ("SS_012", "mud"),
}
PASS_TAG = unreal.Name("SunscarAbiverdDoorSurroundsV1")
ACTOR_LABEL = "ABV_OldTown_DoorSurrounds_HISM_V1"
FOLDER = "OperationSunscar/AbiverdStructuralSkinV5/DoorSurrounds"
JAMB_WIDTH = 22.0
SURROUND_DEPTH = 34.0
JAMB_OVERHEAD = 18.0
LINTEL_HEIGHT = 28.0
REPORT_NAME = (
    "abiverd_door_surrounds_apply_v1.json"
    if APPLY_CHANGES
    else "abiverd_door_surrounds_dry_run_v1.json"
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


def actor_site(actor):
    for tag in actor.tags:
        value = str(tag)
        if value.startswith("Building_"):
            return value[len("Building_"):]
        if value.startswith("SS_") and len(value) == 6:
            return value
    return ""


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
        raise RuntimeError("ABIVERD_DOOR_SURROUNDS_ACTOR_HANDLE")
    if root_handle is None:
        root_handle, failure = subsystem.add_new_subobject(
            unreal.AddNewSubobjectParams(
                parent_handle=actor_handle,
                new_class=unreal.SceneComponent.static_class(),
            )
        )
        if not failure.is_empty():
            raise RuntimeError("ABIVERD_DOOR_SURROUNDS_ROOT " + str(failure))
        subsystem.rename_subobject(root_handle, unreal.Text("DefaultSceneRoot"))
    return actor_handle, root_handle


def make_transform(location, dimensions):
    transform = unreal.Transform()
    transform.translation = location
    transform.rotation = unreal.MathLibrary.conv_rotator_to_quaternion(
        unreal.Rotator(roll=0.0, pitch=0.0, yaw=0.0)
    )
    transform.scale3d = unreal.Vector(
        dimensions.x / 100.0,
        dimensions.y / 100.0,
        dimensions.z / 100.0,
    )
    return transform


project_name = os.path.splitext(os.path.basename(unreal.Paths.get_project_file_path()))[0]
project_directory = os.path.abspath(unreal.Paths.project_dir()).replace("\\", "/").rstrip("/")
if project_name != EXPECTED_PROJECT or not project_directory.endswith(EXPECTED_DIRECTORY_SUFFIX):
    raise RuntimeError("ABIVERD_DOOR_SURROUNDS_WRONG_PROJECT")

level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
level = level_subsystem.get_current_level()
level_path = level.get_outermost().get_name() if level else ""
if level_path != EXPECTED_LEVEL:
    if not level_subsystem.load_level(EXPECTED_LEVEL):
        raise RuntimeError("ABIVERD_DOOR_SURROUNDS_LOAD_FAILED")
    level = level_subsystem.get_current_level()
    level_path = level.get_outermost().get_name() if level else ""
if level_path != EXPECTED_LEVEL:
    raise RuntimeError("ABIVERD_DOOR_SURROUNDS_WRONG_LEVEL " + level_path)
if dirty_packages():
    raise RuntimeError("ABIVERD_DOOR_SURROUNDS_DIRTY_BEFORE " + "|".join(dirty_packages()))

working_box = unreal.Box(
    min=unreal.Vector(-12500.0, -11500.0, -100000.0),
    max=unreal.Vector(15500.0, 11500.0, 100000.0),
)
descriptors = list(unreal.WorldPartitionBlueprintLibrary.get_intersecting_actor_descs(working_box))
unreal.WorldPartitionBlueprintLibrary.load_actors([item.guid for item in descriptors])
unreal.WorldPartitionBlueprintLibrary.pin_actors([item.guid for item in descriptors])
if dirty_packages():
    raise RuntimeError("ABIVERD_DOOR_SURROUNDS_LOAD_DIRTY")

cube = unreal.EditorAssetLibrary.load_asset(CUBE_PATH)
materials = {key: unreal.EditorAssetLibrary.load_asset(path) for key, path in MATERIAL_PATHS.items()}
if not isinstance(cube, unreal.StaticMesh) or any(material is None for material in materials.values()):
    raise RuntimeError("ABIVERD_DOOR_SURROUNDS_ASSET_MISSING")

actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors = list(actor_subsystem.get_all_level_actors())
existing_matches = [
    actor
    for actor in actors
    if PASS_TAG in list(actor.tags) or actor.get_actor_label() == ACTOR_LABEL
]
if len(existing_matches) > 1:
    raise RuntimeError("ABIVERD_DOOR_SURROUNDS_DUPLICATE %d" % len(existing_matches))

door_actors = {
    actor.get_actor_label(): actor
    for actor in actors
    if isinstance(actor, unreal.StaticMeshActor) and actor.get_actor_label() in DOOR_SITES
}
if set(door_actors) != set(DOOR_SITES):
    raise RuntimeError(
        "ABIVERD_DOOR_SURROUNDS_MISSING_DOORS "
        + repr(sorted(set(DOOR_SITES) - set(door_actors)))
    )

site_samples = {}
for actor in actors:
    if not isinstance(actor, unreal.StaticMeshActor):
        continue
    if unreal.Name("CoreCategory_Building") not in list(actor.tags):
        continue
    site = actor_site(actor)
    if site not in {site for site, _material in DOOR_SITES.values()}:
        continue
    origin, _extent = actor.get_actor_bounds(False)
    site_samples.setdefault(site, []).append(origin)
site_centers = {
    site: unreal.Vector(
        sum(value.x for value in values) / len(values),
        sum(value.y for value in values) / len(values),
        sum(value.z for value in values) / len(values),
    )
    for site, values in site_samples.items()
}
expected_sites = {site for site, _material in DOOR_SITES.values()}
if set(site_centers) != expected_sites:
    raise RuntimeError("ABIVERD_DOOR_SURROUNDS_SITE_CENTERS " + repr(sorted(site_centers)))

transforms_by_material = {key: [] for key in materials}
rows = []
for label in sorted(DOOR_SITES):
    site, material_key = DOOR_SITES[label]
    door = door_actors[label]
    origin, extent = door.get_actor_bounds(False)
    dimensions = extent * 2.0
    if not (115.0 <= max(dimensions.x, dimensions.y) <= 135.0 and 230.0 <= dimensions.z <= 250.0):
        raise RuntimeError("ABIVERD_DOOR_SURROUNDS_DOOR_BOUNDS %s %s" % (label, dimensions))
    center = site_centers[site]
    along_x = extent.x >= extent.y
    bottom_z = origin.z - extent.z
    top_z = origin.z + extent.z
    jamb_height = dimensions.z + JAMB_OVERHEAD
    jamb_z = bottom_z + jamb_height * 0.5
    lintel_z = top_z + JAMB_OVERHEAD + LINTEL_HEIGHT * 0.5

    placements = []
    if along_x:
        outward = 1.0 if origin.y >= center.y else -1.0
        facade_y = origin.y + outward * (extent.y + SURROUND_DEPTH * 0.5 - 4.0)
        side_offset = extent.x + JAMB_WIDTH * 0.5 - 2.0
        placements.extend(
            [
                (unreal.Vector(origin.x - side_offset, facade_y, jamb_z), unreal.Vector(JAMB_WIDTH, SURROUND_DEPTH, jamb_height), "left_jamb"),
                (unreal.Vector(origin.x + side_offset, facade_y, jamb_z), unreal.Vector(JAMB_WIDTH, SURROUND_DEPTH, jamb_height), "right_jamb"),
                (unreal.Vector(origin.x, facade_y, lintel_z), unreal.Vector(dimensions.x + JAMB_WIDTH * 2.0 - 4.0, SURROUND_DEPTH, LINTEL_HEIGHT), "lintel"),
            ]
        )
    else:
        outward = 1.0 if origin.x >= center.x else -1.0
        facade_x = origin.x + outward * (extent.x + SURROUND_DEPTH * 0.5 - 4.0)
        side_offset = extent.y + JAMB_WIDTH * 0.5 - 2.0
        placements.extend(
            [
                (unreal.Vector(facade_x, origin.y - side_offset, jamb_z), unreal.Vector(SURROUND_DEPTH, JAMB_WIDTH, jamb_height), "left_jamb"),
                (unreal.Vector(facade_x, origin.y + side_offset, jamb_z), unreal.Vector(SURROUND_DEPTH, JAMB_WIDTH, jamb_height), "right_jamb"),
                (unreal.Vector(facade_x, origin.y, lintel_z), unreal.Vector(SURROUND_DEPTH, dimensions.y + JAMB_WIDTH * 2.0 - 4.0, LINTEL_HEIGHT), "lintel"),
            ]
        )

    for location, piece_dimensions, role in placements:
        transforms_by_material[material_key].append(make_transform(location, piece_dimensions))
        rows.append(
            {
                "door": label,
                "site": site,
                "material_key": material_key,
                "role": role,
                "location_cm": [round(location.x, 3), round(location.y, 3), round(location.z, 3)],
                "dimensions_cm": [round(piece_dimensions.x, 3), round(piece_dimensions.y, 3), round(piece_dimensions.z, 3)],
                "collision": "NoCollision",
            }
        )

if len(rows) != len(DOOR_SITES) * 3:
    raise RuntimeError("ABIVERD_DOOR_SURROUNDS_COUNT %d" % len(rows))

saved_packages = []
if APPLY_CHANGES:
    if existing_matches:
        surround_actor = existing_matches[0]
        components = list(
            surround_actor.get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent)
        )
        if len(components) != len(materials):
            raise RuntimeError("ABIVERD_DOOR_SURROUNDS_COMPONENTS %d" % len(components))
        components_by_name = {component.get_name(): component for component in components}
        surround_actor.modify()
    else:
        surround_actor = actor_subsystem.spawn_actor_from_class(
            unreal.Actor, unreal.Vector(), unreal.Rotator(), transient=False
        )
        if surround_actor is None:
            raise RuntimeError("ABIVERD_DOOR_SURROUNDS_SPAWN")
        surround_actor.set_actor_label(ACTOR_LABEL)
        surround_actor.set_folder_path(unreal.Name(FOLDER))
        surround_actor.tags = [PASS_TAG, unreal.Name("MapOwnedModularGeometry"), unreal.Name("QuixelDerivedMaterials")]
        surround_actor.set_replicates(False)
        subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
        _actor_handle, root_handle = actor_and_root_handles(subsystem, surround_actor)
        components_by_name = {}
        for material_key in sorted(materials):
            component_handle, failure = subsystem.add_new_subobject(
                unreal.AddNewSubobjectParams(
                    parent_handle=root_handle,
                    new_class=unreal.HierarchicalInstancedStaticMeshComponent.static_class(),
                )
            )
            if not failure.is_empty():
                raise RuntimeError("ABIVERD_DOOR_SURROUNDS_COMPONENT " + str(failure))
            component_name = "HISM_DoorSurround_%s" % material_key.title()
            subsystem.rename_subobject(component_handle, unreal.Text(component_name))
            component_data = unreal.SubobjectDataBlueprintFunctionLibrary.get_data(component_handle)
            components_by_name[component_name] = unreal.SubobjectDataBlueprintFunctionLibrary.get_associated_object(component_data)

    for material_key in sorted(materials):
        component_name = "HISM_DoorSurround_%s" % material_key.title()
        component = components_by_name.get(component_name)
        if component is None:
            raise RuntimeError("ABIVERD_DOOR_SURROUNDS_COMPONENT_MISSING " + component_name)
        component.modify()
        component.clear_instances()
        component.set_static_mesh(cube)
        component.set_material(0, materials[material_key])
        component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        component.set_cast_shadow(True)
        component.set_editor_property("instance_start_cull_distance", 12000)
        component.set_editor_property("instance_end_cull_distance", 30000)
        try:
            component.set_editor_property("can_ever_affect_navigation", False)
        except Exception:
            pass
        for transform in transforms_by_material[material_key]:
            component.add_instance(transform, world_space=True)
        if component.get_instance_count() != len(transforms_by_material[material_key]):
            raise RuntimeError("ABIVERD_DOOR_SURROUNDS_INSTANCE_COUNT " + material_key)

    before_save = dirty_packages()
    allowed_prefixes = (
        "/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/",
        "/Game/__ExternalObjects__/Maps/Blockout/Lvl_Blockout_01/",
    )
    unexpected = [name for name in before_save if not name.startswith(allowed_prefixes)]
    if unexpected:
        raise RuntimeError("ABIVERD_DOOR_SURROUNDS_UNEXPECTED_DIRTY " + "|".join(unexpected))
    packages = list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()) + list(
        unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()
    )
    saved_packages = [package_name(package) for package in packages]
    if not unreal.EditorLoadingAndSavingUtils.save_packages(packages, True):
        raise RuntimeError("ABIVERD_DOOR_SURROUNDS_SAVE_FAILED")
    if dirty_packages():
        raise RuntimeError("ABIVERD_DOOR_SURROUNDS_DIRTY_AFTER " + "|".join(dirty_packages()))

report = {
    "schema_version": 1,
    "status": "applied_and_saved" if APPLY_CHANGES else "dry_run_complete",
    "context": {"project": project_name, "project_directory": project_directory, "level": level_path},
    "door_count": len(DOOR_SITES),
    "piece_count": len(rows),
    "material_instance_counts": {
        key: len(transforms) for key, transforms in sorted(transforms_by_material.items())
    },
    "placements": rows,
    "saved_packages": sorted(saved_packages),
    "dirty_after": dirty_packages(),
    "policies": {
        "door_authority": "existing Quixel door actors and their collision remain unchanged",
        "collision": "all surround dressing uses NoCollision",
        "replication": "one static non-replicated actor with two material-batched HISM components",
        "performance": "24 cube instances, 12m/30m cull distances, no navigation influence",
        "scope": "SS_004, SS_005, SS_010 and SS_012 verified ground-floor doors only",
    },
}
report_root = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
os.makedirs(report_root, exist_ok=True)
report_path = os.path.join(report_root, REPORT_NAME)
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(report, handle, indent=2)
    handle.write("\n")

unreal.log(
    "ABIVERD_DOOR_SURROUNDS_COMPLETE apply=%s doors=%d pieces=%d"
    % (APPLY_CHANGES, len(DOOR_SITES), len(rows))
)
print("ABIVERD_DOOR_SURROUNDS_COMPLETE", report_path)
