"""Upgrade the saved Abiverd HISM meadow to a denser, gameplay-shaped layout."""

import json
import math
import os
import random

import unreal


EXPECTED_PROJECT = "TacticalMovement"
EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development"
EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
ACTOR_LABEL = "ABV_SS025_PoppyMeadow_HISM"
ACTOR_TAG = unreal.Name("SunscarAbiverdVegetationHISMV1")
PASS_TAG = unreal.Name("SunscarAbiverdVegetationDensityV2")
SEED = 48272
POPPY_PREFIX = "/Game/Maps/Sunscar/Art/Heritage/Foliage/FieldPoppy/SM_FieldPoppy_Var"
GRASS_PREFIX = "/Game/Maps/Sunscar/Art/Heritage/Foliage/WildGrass/SM_WildGrass_Var"
VARIANTS = tuple("ABCDEFGH")
REPORT_NAME = "abiverd_vegetation_density_v2.json"

# Six irregular cover belts flank the central north route. Each is large
# enough to interrupt prone/crouched sightlines without blocking the route.
BELTS = (
    {"id": "WestSouth", "center": (-4700.0, 15800.0), "radius": (2600.0, 1050.0), "yaw": 12.0},
    {"id": "WestMid", "center": (-4850.0, 18650.0), "radius": (2850.0, 1150.0), "yaw": -14.0},
    {"id": "WestNorth", "center": (-4550.0, 21400.0), "radius": (2500.0, 1000.0), "yaw": 7.0},
    {"id": "EastSouth", "center": (4700.0, 16000.0), "radius": (2600.0, 1050.0), "yaw": -10.0},
    {"id": "EastMid", "center": (4850.0, 18850.0), "radius": (2850.0, 1150.0), "yaw": 13.0},
    {"id": "EastNorth", "center": (4550.0, 21600.0), "radius": (2500.0, 1000.0), "yaw": -5.0},
)
POPPY_PER_BELT = 700
GRASS_PER_BELT = 400


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


project_name = os.path.splitext(os.path.basename(unreal.Paths.get_project_file_path()))[0]
project_directory = os.path.abspath(unreal.Paths.project_dir()).replace("\\", "/").rstrip("/")
level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
level = level_subsystem.get_current_level()
level_path = level.get_outermost().get_name() if level else ""
if project_name != EXPECTED_PROJECT or not project_directory.endswith(EXPECTED_DIRECTORY_SUFFIX):
    raise RuntimeError("ABIVERD_VEGETATION_V2_WRONG_PROJECT")
if level_path != EXPECTED_LEVEL:
    if not level_subsystem.load_level(EXPECTED_LEVEL):
        raise RuntimeError("ABIVERD_VEGETATION_V2_LOAD_FAILED")
    level = level_subsystem.get_current_level()
    level_path = level.get_outermost().get_name() if level else ""
if level_path != EXPECTED_LEVEL:
    raise RuntimeError("ABIVERD_VEGETATION_V2_WRONG_LEVEL " + level_path)
if dirty_packages():
    raise RuntimeError("ABIVERD_VEGETATION_V2_DIRTY_BEFORE " + "|".join(dirty_packages()))

full_box = unreal.Box(
    min=unreal.Vector(-130000.0, -130000.0, -100000.0),
    max=unreal.Vector(130000.0, 130000.0, 100000.0),
)
working_box = unreal.Box(
    min=unreal.Vector(-9000.0, 13500.0, -100000.0),
    max=unreal.Vector(9000.0, 23500.0, 100000.0),
)
full_descriptors = list(unreal.WorldPartitionBlueprintLibrary.get_intersecting_actor_descs(full_box))
landscape_descriptors = [
    item for item in full_descriptors if str(item.label).startswith("LandscapeStreamingProxy_")
]
working_descriptors = list(unreal.WorldPartitionBlueprintLibrary.get_intersecting_actor_descs(working_box))
guids = [item.guid for item in landscape_descriptors + working_descriptors]
unreal.WorldPartitionBlueprintLibrary.load_actors(guids)
unreal.WorldPartitionBlueprintLibrary.pin_actors(guids)
if dirty_packages():
    raise RuntimeError("ABIVERD_VEGETATION_V2_LOAD_DIRTY")

actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
actors = list(actor_subsystem.get_all_level_actors())
landscapes = [actor for actor in actors if isinstance(actor, unreal.LandscapeProxy)]
streaming_proxies = [actor for actor in landscapes if isinstance(actor, unreal.LandscapeStreamingProxy)]
if len(streaming_proxies) != 16:
    raise RuntimeError(
        "ABIVERD_VEGETATION_V2_LANDSCAPES total=%d proxies=%d"
        % (len(landscapes), len(streaming_proxies))
    )
matches = [
    actor for actor in actors
    if actor.get_actor_label() == ACTOR_LABEL and ACTOR_TAG in list(actor.tags)
]
if len(matches) != 1:
    raise RuntimeError("ABIVERD_VEGETATION_V2_ACTOR_SCOPE %d" % len(matches))
vegetation_actor = matches[0]
components = list(
    vegetation_actor.get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent)
)
if len(components) != 16:
    raise RuntimeError("ABIVERD_VEGETATION_V2_COMPONENT_SCOPE %d" % len(components))

mesh_by_key = {}
component_by_key = {}
for kind, prefix in (("poppy", POPPY_PREFIX), ("grass", GRASS_PREFIX)):
    for variant in VARIANTS:
        path = prefix + variant
        mesh = unreal.EditorAssetLibrary.load_asset(path)
        if not isinstance(mesh, unreal.StaticMesh):
            raise RuntimeError("ABIVERD_VEGETATION_V2_MESH " + path)
        key = (kind, variant)
        mesh_by_key[key] = mesh
        matching_components = [
            component for component in components
            if component.get_editor_property("static_mesh") is not None
            and component.get_editor_property("static_mesh").get_path_name() == mesh.get_path_name()
        ]
        if len(matching_components) != 1:
            raise RuntimeError("ABIVERD_VEGETATION_V2_COMPONENT_MESH %s %d" % (path, len(matching_components)))
        component_by_key[key] = matching_components[0]

# Trace only against Landscape, not buildings, hidden ground overlays, or ruins.
ignored = [actor for actor in actors if actor not in landscapes]


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


def excluded(x, y):
    # Preserve the central assault lane, mosque court, and well/landmark court.
    if -1750.0 <= x <= 1250.0:
        return True
    if 350.0 <= x <= 3000.0 and 15150.0 <= y <= 17650.0:
        return True
    if -1600.0 <= x <= 1600.0 and 21000.0 <= y <= 23000.0:
        return True
    return False


randomizer = random.Random(SEED)
rows_by_key = {(kind, variant): [] for kind in ("poppy", "grass") for variant in VARIANTS}
belt_records = []
for belt in BELTS:
    angle = math.radians(belt["yaw"])
    cos_a, sin_a = math.cos(angle), math.sin(angle)
    record = {"belt": belt["id"], "poppy": 0, "grass": 0}
    for kind, target in (("poppy", POPPY_PER_BELT), ("grass", GRASS_PER_BELT)):
        attempts = 0
        while record[kind] < target and attempts < target * 30:
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
                continue
            variant = randomizer.choice(VARIANTS)
            if kind == "poppy":
                scale = randomizer.uniform(0.92, 1.22)
            else:
                scale = randomizer.uniform(0.86, 1.18)
            transform = unreal.Transform()
            transform.translation = unreal.Vector(x, y, z + 1.5)
            transform.rotation = unreal.MathLibrary.conv_rotator_to_quaternion(
                unreal.Rotator(roll=0.0, pitch=0.0, yaw=randomizer.uniform(0.0, 360.0))
            )
            transform.scale3d = unreal.Vector(scale, scale, scale)
            rows_by_key[(kind, variant)].append(transform)
            record[kind] += 1
        if record[kind] != target:
            raise RuntimeError(
                "ABIVERD_VEGETATION_V2_DENSITY %s %s %d/%d"
                % (belt["id"], kind, record[kind], target)
            )
    belt_records.append(record)

vegetation_actor.modify()
if PASS_TAG not in list(vegetation_actor.tags):
    vegetation_actor.tags = list(vegetation_actor.tags) + [PASS_TAG]
vegetation_actor.set_replicates(False)
component_records = []
for key, component in sorted(component_by_key.items()):
    component.modify()
    component.clear_instances()
    component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    component.set_cast_shadow(False)
    component.set_editor_property("instance_start_cull_distance", 8000)
    component.set_editor_property("instance_end_cull_distance", 24000)
    for transform in rows_by_key[key]:
        component.add_instance_world_space(transform)
    try:
        component.set_editor_property("can_ever_affect_navigation", False)
    except Exception:
        pass
    try:
        component.set_editor_property("enable_density_scaling", True)
    except Exception:
        pass
    component_records.append(
        {
            "kind": key[0],
            "variant": key[1],
            "mesh": mesh_by_key[key].get_path_name(),
            "instances": component.get_instance_count(),
            "collision": str(component.get_collision_enabled()),
            "cast_shadow": bool(component.cast_shadow),
            "start_cull_cm": int(component.instance_start_cull_distance),
            "end_cull_cm": int(component.instance_end_cull_distance),
        }
    )

dirty_before_save = dirty_packages()
allowed_prefixes = (
    "/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/",
    "/Game/__ExternalObjects__/Maps/Blockout/Lvl_Blockout_01/",
)
unexpected = [name for name in dirty_before_save if not name.startswith(allowed_prefixes)]
if unexpected:
    raise RuntimeError("ABIVERD_VEGETATION_V2_UNEXPECTED_DIRTY " + "|".join(unexpected))
packages = list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()) + list(
    unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()
)
if not unreal.EditorLoadingAndSavingUtils.save_packages(packages, True):
    raise RuntimeError("ABIVERD_VEGETATION_V2_SAVE_FAILED")
remaining = dirty_packages()
if remaining:
    raise RuntimeError("ABIVERD_VEGETATION_V2_DIRTY_AFTER " + "|".join(remaining))

report_root = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
os.makedirs(report_root, exist_ok=True)
report_path = os.path.join(report_root, REPORT_NAME)
total_poppy = sum(row["instances"] for row in component_records if row["kind"] == "poppy")
total_grass = sum(row["instances"] for row in component_records if row["kind"] == "grass")
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(
        {
            "schema_version": 2,
            "status": "vegetation_density_saved",
            "context": {"project": project_name, "project_directory": project_directory, "level": level_path},
            "actor": ACTOR_LABEL,
            "actor_package": package_name(vegetation_actor.get_package()),
            "seed": SEED,
            "total_poppy": total_poppy,
            "total_grass": total_grass,
            "total_instances": total_poppy + total_grass,
            "belt_records": belt_records,
            "component_records": component_records,
            "saved_packages": dirty_before_save,
            "dirty_packages_after": remaining,
        },
        handle,
        indent=2,
    )
    handle.write("\n")

unreal.log(
    "ABIVERD_VEGETATION_V2_COMPLETE total=%d poppy=%d grass=%d saved=%d report=%s"
    % (total_poppy + total_grass, total_poppy, total_grass, len(dirty_before_save), report_path)
)
print("ABIVERD_VEGETATION_V2_COMPLETE", total_poppy + total_grass, report_path)
