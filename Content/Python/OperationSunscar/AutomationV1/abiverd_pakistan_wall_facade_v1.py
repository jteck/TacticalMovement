"""Plan/apply restrained Pakistan Wall Modular 16 civic facade accents."""

import json
import math
import os

import unreal


APPLY_CHANGES = False
EXPECTED_PROJECT = "TacticalMovement"
EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development"
EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
MESH_PATH = (
    "/Game/Maps/Sunscar/Art/Heritage/Architecture/PakistanWallModular16/"
    "SM_wkzfbht_tier_1/StaticMeshes/SM_wkzfbht_tier_1"
)
PASS_TAG = unreal.Name("SunscarAbiverdPakistanWallFacadeV1")
ACTOR_LABEL = "ABV_OldTown_PakistanWallFacade_HISM_V1"
FOLDER = "OperationSunscar/AbiverdStructuralSkinV5/CivicFacades"
TARGET_SITES = {"SS_005", "SS_010", "SS_012"}
MAX_PER_SITE = 3
UNIFORM_SCALE = 1.0
REPORT_NAME = (
    "abiverd_pakistan_wall_facade_apply_v1.json"
    if APPLY_CHANGES
    else "abiverd_pakistan_wall_facade_dry_run_v1.json"
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
        raise RuntimeError("ABIVERD_PAK_FACADE_ACTOR_HANDLE")
    if root_handle is None:
        root_handle, failure = subsystem.add_new_subobject(
            unreal.AddNewSubobjectParams(
                parent_handle=actor_handle, new_class=unreal.SceneComponent.static_class()
            )
        )
        if not failure.is_empty():
            raise RuntimeError("ABIVERD_PAK_FACADE_ROOT " + str(failure))
        subsystem.rename_subobject(root_handle, unreal.Text("DefaultSceneRoot"))
    return actor_handle, root_handle


project_name = os.path.splitext(os.path.basename(unreal.Paths.get_project_file_path()))[0]
project_directory = os.path.abspath(unreal.Paths.project_dir()).replace("\\", "/").rstrip("/")
if project_name != EXPECTED_PROJECT or not project_directory.endswith(EXPECTED_DIRECTORY_SUFFIX):
    raise RuntimeError("ABIVERD_PAK_FACADE_WRONG_PROJECT")

level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
level = level_subsystem.get_current_level()
level_path = level.get_outermost().get_name() if level else ""
if level_path != EXPECTED_LEVEL:
    if not level_subsystem.load_level(EXPECTED_LEVEL):
        raise RuntimeError("ABIVERD_PAK_FACADE_LOAD_FAILED")
    level = level_subsystem.get_current_level()
    level_path = level.get_outermost().get_name() if level else ""
if level_path != EXPECTED_LEVEL:
    raise RuntimeError("ABIVERD_PAK_FACADE_WRONG_LEVEL " + level_path)
if dirty_packages():
    raise RuntimeError("ABIVERD_PAK_FACADE_DIRTY_BEFORE " + "|".join(dirty_packages()))

working_box = unreal.Box(
    min=unreal.Vector(-12500.0, -11500.0, -100000.0),
    max=unreal.Vector(15500.0, 11500.0, 100000.0),
)
descriptors = list(unreal.WorldPartitionBlueprintLibrary.get_intersecting_actor_descs(working_box))
unreal.WorldPartitionBlueprintLibrary.load_actors([item.guid for item in descriptors])
unreal.WorldPartitionBlueprintLibrary.pin_actors([item.guid for item in descriptors])
if dirty_packages():
    raise RuntimeError("ABIVERD_PAK_FACADE_LOAD_DIRTY")

mesh = unreal.EditorAssetLibrary.load_asset(MESH_PATH)
if not isinstance(mesh, unreal.StaticMesh):
    raise RuntimeError("ABIVERD_PAK_FACADE_MESH_MISSING")
bounds = mesh.get_bounds()
local_vertical_min = bounds.origin.z - bounds.box_extent.z
mesh_depth = bounds.box_extent.y * 2.0

actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors = list(actor_subsystem.get_all_level_actors())
existing_matches = [
    actor for actor in actors
    if PASS_TAG in list(actor.tags) or actor.get_actor_label() == ACTOR_LABEL
]
if len(existing_matches) > 1:
    raise RuntimeError("ABIVERD_PAK_FACADE_DUPLICATE %d" % len(existing_matches))

site_origins = {}
site_origin_samples = {}
for actor in actors:
    if not isinstance(actor, unreal.StaticMeshActor):
        continue
    if unreal.Name("CoreCategory_Building") not in list(actor.tags):
        continue
    site = actor_site(actor)
    if site not in TARGET_SITES:
        continue
    origin, _extent = actor.get_actor_bounds(False)
    site_origin_samples.setdefault(site, []).append(origin)
for site, samples in site_origin_samples.items():
    site_origins[site] = unreal.Vector(
        sum(value.x for value in samples) / len(samples),
        sum(value.y for value in samples) / len(samples),
        sum(value.z for value in samples) / len(samples),
    )

candidates = {site: [] for site in TARGET_SITES}
for actor in actors:
    if not isinstance(actor, unreal.StaticMeshActor):
        continue
    if unreal.Name("CoreCategory_Building") not in list(actor.tags):
        continue
    site = actor_site(actor)
    if site not in TARGET_SITES:
        continue
    label = actor.get_actor_label()
    if not label.endswith("_Wall"):
        continue
    origin, extent = actor.get_actor_bounds(False)
    along_x = extent.x >= extent.y
    length = extent.x * 2.0 if along_x else extent.y * 2.0
    height = extent.z * 2.0
    if length < 260.0 or height < 300.0:
        continue
    candidates[site].append(
        {
            "actor": actor,
            "label": label,
            "origin": origin,
            "extent": extent,
            "along_x": along_x,
            "length": length,
            "height": height,
        }
    )

rows = []
transforms = []
for site in sorted(TARGET_SITES):
    center = site_origins.get(site)
    if center is None:
        raise RuntimeError("ABIVERD_PAK_FACADE_SITE_CENTER " + site)
    ordered = sorted(candidates[site], key=lambda item: (-item["length"], item["label"]))
    chosen = []
    for candidate in ordered:
        # Keep accents on separate wall spans instead of repeating them along a
        # single facade. The existing opening actors remain untouched.
        if any(candidate["along_x"] == item["along_x"] for item in chosen) and len(chosen) >= 2:
            continue
        chosen.append(candidate)
        if len(chosen) >= MAX_PER_SITE:
            break
    if not chosen:
        raise RuntimeError("ABIVERD_PAK_FACADE_NO_CANDIDATES " + site)

    for candidate in chosen:
        origin = candidate["origin"]
        extent = candidate["extent"]
        along_x = candidate["along_x"]
        if along_x:
            outward = 1.0 if origin.y >= center.y else -1.0
            x = origin.x
            y = origin.y + outward * (extent.y + mesh_depth * 0.5 - 6.0)
            yaw = 0.0 if outward < 0.0 else 180.0
        else:
            outward = 1.0 if origin.x >= center.x else -1.0
            x = origin.x + outward * (extent.x + mesh_depth * 0.5 - 6.0)
            y = origin.y
            yaw = 90.0 if outward > 0.0 else -90.0
        wall_bottom = origin.z - extent.z
        z = wall_bottom - local_vertical_min * UNIFORM_SCALE
        transform = unreal.Transform()
        transform.translation = unreal.Vector(x, y, z)
        transform.rotation = unreal.MathLibrary.conv_rotator_to_quaternion(
            unreal.Rotator(roll=0.0, pitch=0.0, yaw=yaw)
        )
        transform.scale3d = unreal.Vector(UNIFORM_SCALE, UNIFORM_SCALE, UNIFORM_SCALE)
        transforms.append(transform)
        rows.append(
            {
                "site": site,
                "source_wall": candidate["label"],
                "source_wall_length_cm": round(candidate["length"], 3),
                "source_wall_height_cm": round(candidate["height"], 3),
                "location_cm": [round(x, 3), round(y, 3), round(z, 3)],
                "yaw_deg": yaw,
                "collision": "NoCollision",
            }
        )

if len(rows) < 6 or len(rows) > 9:
    raise RuntimeError("ABIVERD_PAK_FACADE_COUNT %d" % len(rows))

saved_packages = []
if APPLY_CHANGES:
    if existing_matches:
        facade_actor = existing_matches[0]
        components = list(
            facade_actor.get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent)
        )
        if len(components) != 1:
            raise RuntimeError("ABIVERD_PAK_FACADE_COMPONENTS %d" % len(components))
        component = components[0]
        facade_actor.modify()
        component.modify()
        component.clear_instances()
    else:
        facade_actor = actor_subsystem.spawn_actor_from_class(
            unreal.Actor, unreal.Vector(), unreal.Rotator(), transient=False
        )
        if facade_actor is None:
            raise RuntimeError("ABIVERD_PAK_FACADE_SPAWN")
        facade_actor.set_actor_label(ACTOR_LABEL)
        facade_actor.set_folder_path(unreal.Name(FOLDER))
        facade_actor.tags = [PASS_TAG, unreal.Name("QuixelMegascans"), unreal.Name("CivicFacade")]
        facade_actor.set_replicates(False)
        subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
        _actor_handle, root_handle = actor_and_root_handles(subsystem, facade_actor)
        component_handle, failure = subsystem.add_new_subobject(
            unreal.AddNewSubobjectParams(
                parent_handle=root_handle,
                new_class=unreal.HierarchicalInstancedStaticMeshComponent.static_class(),
            )
        )
        if not failure.is_empty():
            raise RuntimeError("ABIVERD_PAK_FACADE_COMPONENT " + str(failure))
        subsystem.rename_subobject(component_handle, unreal.Text("HISM_PakistanWallModular16"))
        component_data = unreal.SubobjectDataBlueprintFunctionLibrary.get_data(component_handle)
        component = unreal.SubobjectDataBlueprintFunctionLibrary.get_associated_object(component_data)
    component.set_static_mesh(mesh)
    component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    component.set_cast_shadow(True)
    component.set_editor_property("instance_start_cull_distance", 12000)
    component.set_editor_property("instance_end_cull_distance", 30000)
    try:
        component.set_editor_property("can_ever_affect_navigation", False)
    except Exception:
        pass
    for transform in transforms:
        component.add_instance_world_space(transform)
    if component.get_instance_count() != len(transforms):
        raise RuntimeError("ABIVERD_PAK_FACADE_INSTANCE_COUNT")

    before_save = dirty_packages()
    allowed_prefixes = (
        "/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/",
        "/Game/__ExternalObjects__/Maps/Blockout/Lvl_Blockout_01/",
    )
    unexpected = [name for name in before_save if not name.startswith(allowed_prefixes)]
    if unexpected:
        raise RuntimeError("ABIVERD_PAK_FACADE_UNEXPECTED_DIRTY " + "|".join(unexpected))
    packages = list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()) + list(
        unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()
    )
    saved_packages = [package_name(package) for package in packages]
    if not unreal.EditorLoadingAndSavingUtils.save_packages(packages, True):
        raise RuntimeError("ABIVERD_PAK_FACADE_SAVE_FAILED")
    if dirty_packages():
        raise RuntimeError("ABIVERD_PAK_FACADE_DIRTY_AFTER " + "|".join(dirty_packages()))

report = {
    "schema_version": 1,
    "status": "applied_and_saved" if APPLY_CHANGES else "dry_run_complete",
    "context": {"project": project_name, "project_directory": project_directory, "level": level_path},
    "source_mesh": MESH_PATH,
    "source_bounds_cm": [
        round(float(bounds.box_extent.x) * 2.0, 3),
        round(float(bounds.box_extent.y) * 2.0, 3),
        round(float(bounds.box_extent.z) * 2.0, 3),
    ],
    "instance_count": len(rows),
    "placements": rows,
    "saved_packages": sorted(saved_packages),
    "dirty_after": dirty_packages(),
    "policies": {
        "scope": "SS_005 Clinic, SS_010 Detention Annex, SS_012 Consulate only",
        "collision": "NoCollision; existing gameplay shells remain authoritative",
        "replication": "Static non-replicated HISM",
        "use": "restrained civic facade accents, not Abiverd archaeological ruins",
    },
}
report_root = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
os.makedirs(report_root, exist_ok=True)
report_path = os.path.join(report_root, REPORT_NAME)
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(report, handle, indent=2)
    handle.write("\n")

unreal.log("ABIVERD_PAK_FACADE_COMPLETE apply=%s count=%d" % (APPLY_CHANGES, len(rows)))
print("ABIVERD_PAK_FACADE_COMPLETE", report_path)
