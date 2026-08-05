"""Plan/apply a restrained Pakistan Window Modular 04 facade pass.

The scan is a full one-storey facade module, not a small insert.  It replaces
selected prototype frame/glass pairs on ground-floor civic and social facades
while the existing building shells remain authoritative for collision.
"""

import json
import os

import unreal


APPLY_CHANGES = False
EXPECTED_PROJECT = "TacticalMovement"
EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development"
EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
MESH_PATH = (
    "/Game/Maps/Sunscar/Art/Heritage/Architecture/PakistanWindowModular04/"
    "SM_wk0hehv_tier_1/StaticMeshes/SM_wk0hehv_tier_1"
)
PASS_TAG = unreal.Name("SunscarAbiverdPakistanWindowFacadeV1")
ACTOR_LABEL = "ABV_OldTown_PakistanWindowFacade_HISM_V1"
FOLDER = "OperationSunscar/AbiverdStructuralSkinV5/CivicWindows"
SELECTED_PAIR_KEYS = {
    # Tea House: all three street-facing ground-floor bays.
    "tea_window_01",
    "tea_window_02",
    "tea_window_03",
    # Old Clinic: complete ground-floor public facade.
    "clinic_f1_win_01",
    "clinic_f1_win_02",
    "clinic_f1_win_03",
    "clinic_f1_win_04",
    # Detention Annex: spaced accents; retain visual restraint and sightline gaps.
    "detention_f1_win_01",
    "detention_f1_win_03",
    "detention_f1_win_05",
    # Consulate Residence: complete ground-floor formal facade.
    "consulate_f1_win_01",
    "consulate_f1_win_02",
    "consulate_f1_win_03",
    "consulate_f1_win_04",
}
EXPECTED_SITES = {"SS_004", "SS_005", "SS_010", "SS_012"}
REPORT_NAME = (
    "abiverd_pakistan_window_facade_apply_v1.json"
    if APPLY_CHANGES
    else "abiverd_pakistan_window_facade_dry_run_v1.json"
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


def window_role_and_key(label):
    lowered = label.lower()
    for suffix, role in (("_frame", "frame"), ("_glass", "glass")):
        if lowered.endswith(suffix):
            return role, lowered[:-len(suffix)]
    return "", ""


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
        raise RuntimeError("ABIVERD_PAK_WINDOW_FACADE_ACTOR_HANDLE")
    if root_handle is None:
        root_handle, failure = subsystem.add_new_subobject(
            unreal.AddNewSubobjectParams(
                parent_handle=actor_handle, new_class=unreal.SceneComponent.static_class()
            )
        )
        if not failure.is_empty():
            raise RuntimeError("ABIVERD_PAK_WINDOW_FACADE_ROOT " + str(failure))
        subsystem.rename_subobject(root_handle, unreal.Text("DefaultSceneRoot"))
    return actor_handle, root_handle


project_name = os.path.splitext(os.path.basename(unreal.Paths.get_project_file_path()))[0]
project_directory = os.path.abspath(unreal.Paths.project_dir()).replace("\\", "/").rstrip("/")
if project_name != EXPECTED_PROJECT or not project_directory.endswith(EXPECTED_DIRECTORY_SUFFIX):
    raise RuntimeError("ABIVERD_PAK_WINDOW_FACADE_WRONG_PROJECT")

level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
level = level_subsystem.get_current_level()
level_path = level.get_outermost().get_name() if level else ""
if level_path != EXPECTED_LEVEL:
    if not level_subsystem.load_level(EXPECTED_LEVEL):
        raise RuntimeError("ABIVERD_PAK_WINDOW_FACADE_LOAD_FAILED")
    level = level_subsystem.get_current_level()
    level_path = level.get_outermost().get_name() if level else ""
if level_path != EXPECTED_LEVEL:
    raise RuntimeError("ABIVERD_PAK_WINDOW_FACADE_WRONG_LEVEL " + level_path)
if dirty_packages():
    raise RuntimeError("ABIVERD_PAK_WINDOW_FACADE_DIRTY_BEFORE " + "|".join(dirty_packages()))

working_box = unreal.Box(
    min=unreal.Vector(-12500.0, -11500.0, -100000.0),
    max=unreal.Vector(15500.0, 11500.0, 100000.0),
)
descriptors = list(unreal.WorldPartitionBlueprintLibrary.get_intersecting_actor_descs(working_box))
unreal.WorldPartitionBlueprintLibrary.load_actors([item.guid for item in descriptors])
unreal.WorldPartitionBlueprintLibrary.pin_actors([item.guid for item in descriptors])
if dirty_packages():
    raise RuntimeError("ABIVERD_PAK_WINDOW_FACADE_LOAD_DIRTY")

mesh = unreal.EditorAssetLibrary.load_asset(MESH_PATH)
if not isinstance(mesh, unreal.StaticMesh):
    raise RuntimeError("ABIVERD_PAK_WINDOW_FACADE_MESH_MISSING")
bounds = mesh.get_bounds()
mesh_width = bounds.box_extent.x * 2.0
mesh_depth = bounds.box_extent.y * 2.0
mesh_height = bounds.box_extent.z * 2.0
local_min_z = bounds.origin.z - bounds.box_extent.z
if not (250.0 <= mesh_width <= 275.0 and 40.0 <= mesh_depth <= 55.0 and 335.0 <= mesh_height <= 360.0):
    raise RuntimeError("ABIVERD_PAK_WINDOW_FACADE_BOUNDS")

actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors = list(actor_subsystem.get_all_level_actors())
existing_matches = [
    actor for actor in actors
    if PASS_TAG in list(actor.tags) or actor.get_actor_label() == ACTOR_LABEL
]
if len(existing_matches) > 1:
    raise RuntimeError("ABIVERD_PAK_WINDOW_FACADE_DUPLICATE %d" % len(existing_matches))

site_samples = {}
for actor in actors:
    if not isinstance(actor, unreal.StaticMeshActor):
        continue
    if unreal.Name("CoreCategory_Building") not in list(actor.tags):
        continue
    site = actor_site(actor)
    if site not in EXPECTED_SITES:
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
if set(site_centers) != EXPECTED_SITES:
    raise RuntimeError("ABIVERD_PAK_WINDOW_FACADE_SITE_CENTERS " + repr(sorted(site_centers)))

pair_actors = {}
for actor in actors:
    if not isinstance(actor, unreal.StaticMeshActor):
        continue
    role, key = window_role_and_key(actor.get_actor_label())
    if key not in SELECTED_PAIR_KEYS:
        continue
    site = actor_site(actor)
    if site not in EXPECTED_SITES:
        continue
    pair_actors.setdefault(key, {})[role] = actor

if set(pair_actors) != SELECTED_PAIR_KEYS:
    missing = sorted(SELECTED_PAIR_KEYS - set(pair_actors))
    raise RuntimeError("ABIVERD_PAK_WINDOW_FACADE_MISSING_PAIRS " + repr(missing))
for key, roles in pair_actors.items():
    if set(roles) != {"frame", "glass"}:
        raise RuntimeError("ABIVERD_PAK_WINDOW_FACADE_PAIR_ROLES %s %s" % (key, sorted(roles)))

rows = []
transforms = []
for key in sorted(SELECTED_PAIR_KEYS):
    frame = pair_actors[key]["frame"]
    glass = pair_actors[key]["glass"]
    frame_origin, frame_extent = frame.get_actor_bounds(False)
    site = actor_site(frame)
    if site != actor_site(glass):
        raise RuntimeError("ABIVERD_PAK_WINDOW_FACADE_SITE_MISMATCH " + key)
    center = site_centers[site]
    along_x = frame_extent.x >= frame_extent.y
    if along_x:
        outward = 1.0 if frame_origin.y >= center.y else -1.0
        x = frame_origin.x
        y = frame_origin.y + outward * (frame_extent.y + mesh_depth * 0.5 - 6.0)
        yaw = 0.0 if outward < 0.0 else 180.0
    else:
        outward = 1.0 if frame_origin.x >= center.x else -1.0
        x = frame_origin.x + outward * (frame_extent.x + mesh_depth * 0.5 - 6.0)
        y = frame_origin.y
        yaw = 90.0 if outward > 0.0 else -90.0

    # The scan opening sits above the module midpoint.  Align that opening to
    # the prototype frame while keeping the scan base close to the floor line.
    target_base_z = frame_origin.z - mesh_height * 0.57
    z = target_base_z - local_min_z
    transform = unreal.Transform()
    transform.translation = unreal.Vector(x, y, z)
    transform.rotation = unreal.MathLibrary.conv_rotator_to_quaternion(
        unreal.Rotator(roll=0.0, pitch=0.0, yaw=yaw)
    )
    transform.scale3d = unreal.Vector(1.0, 1.0, 1.0)
    transforms.append(transform)
    rows.append(
        {
            "pair_key": key,
            "site": site,
            "frame_label": frame.get_actor_label(),
            "glass_label": glass.get_actor_label(),
            "frame_origin_cm": [round(frame_origin.x, 3), round(frame_origin.y, 3), round(frame_origin.z, 3)],
            "location_cm": [round(x, 3), round(y, 3), round(z, 3)],
            "yaw_deg": yaw,
            "source_actor_action": "hide_visuals_and_disable_collision" if APPLY_CHANGES else "planned",
        }
    )

if len(rows) != 14:
    raise RuntimeError("ABIVERD_PAK_WINDOW_FACADE_COUNT %d" % len(rows))

saved_packages = []
if APPLY_CHANGES:
    if existing_matches:
        facade_actor = existing_matches[0]
        components = list(
            facade_actor.get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent)
        )
        if len(components) != 1:
            raise RuntimeError("ABIVERD_PAK_WINDOW_FACADE_COMPONENTS %d" % len(components))
        component = components[0]
        facade_actor.modify()
        component.modify()
        component.clear_instances()
    else:
        facade_actor = actor_subsystem.spawn_actor_from_class(
            unreal.Actor, unreal.Vector(), unreal.Rotator(), transient=False
        )
        if facade_actor is None:
            raise RuntimeError("ABIVERD_PAK_WINDOW_FACADE_SPAWN")
        facade_actor.set_actor_label(ACTOR_LABEL)
        facade_actor.set_folder_path(unreal.Name(FOLDER))
        facade_actor.tags = [PASS_TAG, unreal.Name("QuixelMegascans"), unreal.Name("CivicWindowFacade")]
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
            raise RuntimeError("ABIVERD_PAK_WINDOW_FACADE_COMPONENT " + str(failure))
        subsystem.rename_subobject(component_handle, unreal.Text("HISM_PakistanWindowModular04"))
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
        component.add_instance(transform, world_space=True)
    if component.get_instance_count() != len(transforms):
        raise RuntimeError("ABIVERD_PAK_WINDOW_FACADE_INSTANCE_COUNT")

    for roles in pair_actors.values():
        for source_actor in roles.values():
            source_actor.modify()
            source_component = source_actor.static_mesh_component
            source_component.modify()
            source_component.set_visibility(False, True)
            source_component.set_hidden_in_game(True)
            source_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)

    before_save = dirty_packages()
    allowed_prefixes = (
        "/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/",
        "/Game/__ExternalObjects__/Maps/Blockout/Lvl_Blockout_01/",
    )
    unexpected = [name for name in before_save if not name.startswith(allowed_prefixes)]
    if unexpected:
        raise RuntimeError("ABIVERD_PAK_WINDOW_FACADE_UNEXPECTED_DIRTY " + "|".join(unexpected))
    packages = list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()) + list(
        unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()
    )
    saved_packages = [package_name(package) for package in packages]
    if not unreal.EditorLoadingAndSavingUtils.save_packages(packages, True):
        raise RuntimeError("ABIVERD_PAK_WINDOW_FACADE_SAVE_FAILED")
    if dirty_packages():
        raise RuntimeError("ABIVERD_PAK_WINDOW_FACADE_DIRTY_AFTER " + "|".join(dirty_packages()))

report = {
    "schema_version": 1,
    "status": "applied_and_saved" if APPLY_CHANGES else "dry_run_complete",
    "context": {"project": project_name, "project_directory": project_directory, "level": level_path},
    "source_mesh": MESH_PATH,
    "source_bounds_cm": [round(mesh_width, 3), round(mesh_depth, 3), round(mesh_height, 3)],
    "instance_count": len(rows),
    "site_counts": {site: sum(row["site"] == site for row in rows) for site in sorted(EXPECTED_SITES)},
    "placements": rows,
    "saved_packages": sorted(saved_packages),
    "dirty_after": dirty_packages(),
    "policies": {
        "scope": "ground-floor Tea House, Clinic, restrained Detention Annex, and Consulate facades",
        "collision": "scan HISM and replaced prototype window visuals use NoCollision; building shells remain authoritative",
        "replication": "static non-replicated HISM",
        "performance": "one HISM component, Nanite source mesh, 12m/30m cull distances, 2K runtime textures",
        "exclusions": "upper storeys, Checkpoint, Pump Station, and Telecom remain unchanged in this pass",
    },
}
report_root = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
os.makedirs(report_root, exist_ok=True)
report_path = os.path.join(report_root, REPORT_NAME)
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(report, handle, indent=2)
    handle.write("\n")

unreal.log("ABIVERD_PAK_WINDOW_FACADE_COMPLETE apply=%s count=%d" % (APPLY_CHANGES, len(rows)))
print("ABIVERD_PAK_WINDOW_FACADE_COMPLETE", report_path)
