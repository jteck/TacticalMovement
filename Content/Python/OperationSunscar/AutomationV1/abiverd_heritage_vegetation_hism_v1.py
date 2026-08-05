"""Dry-run/apply deterministic, terrain-traced HISM poppy and grass belts."""

import json
import math
import os
import random

import unreal


APPLY_CHANGES = True
EXPECTED_PROJECT = "TacticalMovement"
EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development"
EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
PASS_TAG = unreal.Name("SunscarAbiverdVegetationHISMV1")
ACTOR_LABEL = "ABV_SS025_PoppyMeadow_HISM"
FOLDER = "OperationSunscar/AbiverdHeritageV1/SS_025"
SEED = 48271
REPORT_NAME = (
    "abiverd_heritage_vegetation_hism_apply_v1.json"
    if APPLY_CHANGES
    else "abiverd_heritage_vegetation_hism_dry_run_v1.json"
)

POPPY_PREFIX = "/Game/Maps/Sunscar/Art/Heritage/Foliage/FieldPoppy/SM_FieldPoppy_Var"
GRASS_PREFIX = "/Game/Maps/Sunscar/Art/Heritage/Foliage/WildGrass/SM_WildGrass_Var"
VARIANTS = tuple("ABCDEFGH")

# Irregular belts occupy both flanks but leave the central north route open.
BELTS = [
    {"id": "WestSouth", "center": (-4500.0, 16300.0), "radius": (1500.0, 720.0), "yaw": 12.0, "poppies": 120, "grass": 105},
    {"id": "WestMid", "center": (-4500.0, 18700.0), "radius": (1750.0, 760.0), "yaw": -14.0, "poppies": 145, "grass": 120},
    {"id": "WestNorth", "center": (-4300.0, 21100.0), "radius": (1550.0, 690.0), "yaw": 7.0, "poppies": 115, "grass": 100},
    {"id": "EastSouth", "center": (4400.0, 16900.0), "radius": (1600.0, 700.0), "yaw": -10.0, "poppies": 125, "grass": 105},
    {"id": "EastMid", "center": (4300.0, 19400.0), "radius": (1750.0, 780.0), "yaw": 13.0, "poppies": 150, "grass": 125},
    {"id": "EastNorth", "center": (4400.0, 21600.0), "radius": (1500.0, 650.0), "yaw": -5.0, "poppies": 110, "grass": 95},
]


def current_level_path():
    subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    level = subsystem.get_current_level()
    return level.get_outermost().get_name() if level else ""


def package_name(package):
    try:
        return package.get_name()
    except Exception:
        return str(package)


def dirty_packages():
    return sorted(
        {package_name(package) for package in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()}
        | {package_name(package) for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()}
    )


project_name = os.path.splitext(os.path.basename(unreal.Paths.get_project_file_path()))[0]
project_directory = os.path.abspath(unreal.Paths.project_dir()).replace("\\", "/").rstrip("/")
level_path = current_level_path()
if project_name != EXPECTED_PROJECT or not project_directory.endswith(EXPECTED_DIRECTORY_SUFFIX):
    raise RuntimeError("ABIVERD_VEGETATION_WRONG_PROJECT")
if level_path != EXPECTED_LEVEL:
    raise RuntimeError("ABIVERD_VEGETATION_WRONG_LEVEL " + level_path)
if dirty_packages():
    raise RuntimeError("ABIVERD_VEGETATION_DIRTY_BEFORE " + repr(dirty_packages()))

actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
actors = list(actor_subsystem.get_all_level_actors())
landscapes = [actor for actor in actors if isinstance(actor, unreal.LandscapeProxy)]
if len(landscapes) < 3:
    raise RuntimeError("ABIVERD_VEGETATION_REGION_NOT_LOADED landscapes=%d" % len(landscapes))
if any(PASS_TAG in list(actor.tags) or actor.get_actor_label() == ACTOR_LABEL for actor in actors):
    raise RuntimeError("ABIVERD_VEGETATION_DUPLICATE")
non_landscapes = [actor for actor in actors if actor not in landscapes]


def load_mesh(path):
    asset = unreal.EditorAssetLibrary.load_asset(path)
    if not isinstance(asset, unreal.StaticMesh):
        raise RuntimeError("ABIVERD_VEGETATION_MISSING_MESH " + path)
    return asset


meshes = {
    "poppy": [load_mesh(POPPY_PREFIX + variant) for variant in VARIANTS],
    "grass": [load_mesh(GRASS_PREFIX + variant) for variant in VARIANTS],
}


def terrain_z(x, y):
    hit = unreal.SystemLibrary.line_trace_single(
        world,
        unreal.Vector(x, y, 100000.0),
        unreal.Vector(x, y, -100000.0),
        unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
        True,
        non_landscapes,
        unreal.DrawDebugTrace.NONE,
        True,
    )
    if hit is None:
        return None
    data = hit.to_dict()
    if not data.get("blocking_hit") or data.get("location") is None:
        return None
    return float(data["location"].z)


def excluded(x, y):
    # Central road/town spine, mosque footprint, and wider route mouths.
    if -2100.0 <= x <= 1000.0:
        return True
    if 450.0 <= x <= 2800.0 and 15350.0 <= y <= 17550.0:
        return True
    if -1400.0 <= x <= 1400.0 and 21400.0 <= y <= 22800.0:
        return True
    return False


randomizer = random.Random(SEED)
instances = {"poppy": [[] for _ in VARIANTS], "grass": [[] for _ in VARIANTS]}
trace_failures = []
belts_summary = []
for belt in BELTS:
    belt_counts = {"poppy": 0, "grass": 0}
    angle = math.radians(belt["yaw"])
    cos_a, sin_a = math.cos(angle), math.sin(angle)
    for kind in ("poppy", "grass"):
        target = int(belt["poppies"] if kind == "poppy" else belt["grass"])
        attempts = 0
        while belt_counts[kind] < target and attempts < target * 20:
            attempts += 1
            radius = math.sqrt(randomizer.random())
            theta = randomizer.random() * math.tau
            local_x = math.cos(theta) * radius * belt["radius"][0]
            local_y = math.sin(theta) * radius * belt["radius"][1]
            x = belt["center"][0] + local_x * cos_a - local_y * sin_a
            y = belt["center"][1] + local_x * sin_a + local_y * cos_a
            if excluded(x, y):
                continue
            z = terrain_z(x, y)
            if z is None:
                trace_failures.append({"belt": belt["id"], "kind": kind, "x": x, "y": y})
                continue
            variant_index = randomizer.randrange(len(VARIANTS))
            scale = randomizer.uniform(0.86, 1.12) if kind == "poppy" else randomizer.uniform(0.78, 1.10)
            instances[kind][variant_index].append(
                {
                    "location_cm": [round(x, 3), round(y, 3), round(z, 3)],
                    "yaw": round(randomizer.uniform(0.0, 360.0), 3),
                    "scale": round(scale, 4),
                    "belt": belt["id"],
                }
            )
            belt_counts[kind] += 1
        if belt_counts[kind] != target:
            raise RuntimeError(
                "ABIVERD_VEGETATION_DENSITY_FAILED belt=%s kind=%s placed=%d target=%d"
                % (belt["id"], kind, belt_counts[kind], target)
            )
    belts_summary.append({"belt": belt["id"], **belt_counts})
if trace_failures:
    raise RuntimeError("ABIVERD_VEGETATION_TRACE_FAILURES %d" % len(trace_failures))


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
        raise RuntimeError("ABIVERD_VEGETATION_ACTOR_HANDLE_MISSING")
    if root_handle is None:
        root_handle, failure = subsystem.add_new_subobject(
            unreal.AddNewSubobjectParams(
                parent_handle=actor_handle,
                new_class=unreal.SceneComponent.static_class(),
            )
        )
        if not failure.is_empty():
            raise RuntimeError("ABIVERD_VEGETATION_ROOT_CREATE_FAILED " + str(failure))
        subsystem.rename_subobject(root_handle, unreal.Text("DefaultSceneRoot"))
    return actor_handle, root_handle


def transform_from_row(row):
    transform = unreal.Transform()
    transform.translation = unreal.Vector(*row["location_cm"])
    transform.rotation = unreal.MathLibrary.conv_rotator_to_quaternion(
        unreal.Rotator(roll=0.0, pitch=0.0, yaw=row["yaw"])
    )
    transform.scale3d = unreal.Vector(row["scale"], row["scale"], row["scale"])
    return transform


created_component_rows = []
created_actor_package = ""
if APPLY_CHANGES:
    vegetation_actor = actor_subsystem.spawn_actor_from_class(
        unreal.Actor, unreal.Vector(0.0, 0.0, 0.0), unreal.Rotator(), transient=False
    )
    if vegetation_actor is None:
        raise RuntimeError("ABIVERD_VEGETATION_ACTOR_SPAWN_FAILED")
    vegetation_actor.set_actor_label(ACTOR_LABEL)
    vegetation_actor.set_folder_path(unreal.Name(FOLDER))
    vegetation_actor.tags = [PASS_TAG, unreal.Name("SS_025"), unreal.Name("AbiverdHeritageV1")]
    vegetation_actor.set_replicates(False)
    created_actor_package = package_name(vegetation_actor.get_package())

    subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
    if subsystem is None:
        raise RuntimeError("ABIVERD_VEGETATION_SUBOBJECT_SUBSYSTEM_MISSING")
    _actor_handle, root_handle = actor_and_root_handles(subsystem, vegetation_actor)
    for kind in ("poppy", "grass"):
        for variant_index, variant in enumerate(VARIANTS):
            rows = instances[kind][variant_index]
            if not rows:
                continue
            component_handle, failure = subsystem.add_new_subobject(
                unreal.AddNewSubobjectParams(
                    parent_handle=root_handle,
                    new_class=unreal.HierarchicalInstancedStaticMeshComponent.static_class(),
                )
            )
            if not failure.is_empty():
                raise RuntimeError("ABIVERD_VEGETATION_COMPONENT_CREATE_FAILED " + str(failure))
            component_name = "HISM_%s_%s" % (kind.title(), variant)
            subsystem.rename_subobject(component_handle, unreal.Text(component_name))
            component_data = unreal.SubobjectDataBlueprintFunctionLibrary.get_data(component_handle)
            component = unreal.SubobjectDataBlueprintFunctionLibrary.get_associated_object(component_data)
            if not isinstance(component, unreal.HierarchicalInstancedStaticMeshComponent):
                raise RuntimeError("ABIVERD_VEGETATION_COMPONENT_TYPE_FAILED " + component_name)
            component.set_static_mesh(meshes[kind][variant_index])
            component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
            component.set_cast_shadow(False)
            component.set_editor_property("instance_start_cull_distance", 6000)
            component.set_editor_property("instance_end_cull_distance", 20000)
            for row in rows:
                component.add_instance_world_space(transform_from_row(row))
            created_component_rows.append(
                {
                    "component": component_name,
                    "mesh": meshes[kind][variant_index].get_path_name(),
                    "instance_count": component.get_instance_count(),
                    "collision": str(component.get_collision_enabled()),
                    "start_cull_distance": component.instance_start_cull_distance,
                    "end_cull_distance": component.instance_end_cull_distance,
                    "cast_shadow": component.cast_shadow,
                }
            )

dirty_after = dirty_packages()
if APPLY_CHANGES:
    unexpected = sorted(
        name for name in dirty_after
        if name != created_actor_package
        and not name.startswith("/Game/__ExternalObjects__/Maps/Blockout/Lvl_Blockout_01/")
    )
    if unexpected:
        raise RuntimeError("ABIVERD_VEGETATION_UNEXPECTED_DIRTY " + "|".join(unexpected))

instance_counts = {
    kind: sum(len(rows) for rows in instances[kind])
    for kind in ("poppy", "grass")
}
payload = {
    "schema_version": 1,
    "status": "unsaved_hism_preview_ready" if APPLY_CHANGES else "dry_run_complete",
    "context": {
        "project": project_name,
        "project_directory": project_directory,
        "level": level_path,
    },
    "apply_changes": APPLY_CHANGES,
    "seed": SEED,
    "belt_count": len(BELTS),
    "belts": belts_summary,
    "instance_counts": instance_counts,
    "total_instance_count": sum(instance_counts.values()),
    "component_count": sum(1 for kind in instances for rows in instances[kind] if rows),
    "route_and_mosque_exclusions_applied": True,
    "collision_enabled": False,
    "navigation_influence": False,
    "replication": False,
    "cast_shadow": False,
    "start_cull_distance_cm": 6000,
    "end_cull_distance_cm": 20000,
    "created_actor_label": ACTOR_LABEL if APPLY_CHANGES else "",
    "created_actor_package": created_actor_package,
    "created_components": created_component_rows,
    "dirty_packages_after": dirty_after,
    "changes_saved": False,
}
report_root = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
os.makedirs(report_root, exist_ok=True)
report_path = os.path.join(report_root, REPORT_NAME)
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2)
    handle.write("\n")
unreal.log(
    "ABIVERD_VEGETATION mode=%s instances=%d components=%d report=%s"
    % (
        "APPLY" if APPLY_CHANGES else "DRY_RUN",
        payload["total_instance_count"],
        payload["component_count"],
        report_path,
    )
)
print("ABIVERD_VEGETATION", payload["total_instance_count"], report_path)
