"""Dry-run-first deterministic HISM dressing at Old Town wall feet.

The pass uses already-owned Epic/Quixel rubble and dry-grass meshes.  It
samples only ground-floor exterior wall segments, rejects door/threshold
clearances, traces every instance to real support geometry, and consolidates
the result into one non-gameplay actor with a small HISM component set.
"""

import json
import math
import os
import random
import re

import unreal


APPLY_CHANGES = False
EXPECTED_PROJECT = "TacticalMovement"
EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development"
EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
PASS_TAG = unreal.Name("SunscarAbiverdWallFootHISMV1")
ACTOR_LABEL = "ABV_OldTown_WallFoot_HISM_V1"
FOLDER = "OperationSunscar/AbiverdVisualConversion/WallFootV1"
SEED = 73931
TARGET_SITES = {"SS_004", "SS_005", "SS_007", "SS_010", "SS_011", "SS_012", "SS_017", "SS_018"}
REPORT_NAME = (
    "abiverd_wall_foot_transition_hism_apply_v1.json"
    if APPLY_CHANGES
    else "abiverd_wall_foot_transition_hism_dry_run_v1.json"
)
WORKING_BOX = unreal.Box(
    min=unreal.Vector(-12500.0, -11500.0, -100000.0),
    max=unreal.Vector(15500.0, 11500.0, 100000.0),
)
WALL_PATTERN = re.compile(r"^Core_(SS_\d{3})_F1_([NSEW])_(?!Lintel)(?!Floor)(.+)$")
MESHES = {
    "rubble": (
        "/Game/Maps/Sunscar/Art/Quixel/Downloaded/FAB_P1A_012_ydyqbjds/"
        "Military_Trenches_Debris_Patch_Rock_Corner_ydyqbjds_High"
    ),
    "rock_patch": (
        "/Game/Fab/Megascans/3D/Military_Trenches_Ground_Patch_Rock_S_04_yd0lfcq/"
        "Medium/SM_yd0lfcq_tier_2/StaticMeshes/SM_yd0lfcq_tier_2"
    ),
    "grass_a": (
        "/Game/MilitaryTrench/Assets/3D/Plants/Urb_Street_Grass_Dry_01/StaticMeshes/"
        "SM_Urb_Street_Grass_Dry_01_A"
    ),
    "grass_b": (
        "/Game/MilitaryTrench/Assets/3D/Plants/Urb_Street_Grass_Dry_01/StaticMeshes/"
        "SM_Urb_Street_Grass_Dry_01_B"
    ),
    "grass_c": (
        "/Game/MilitaryTrench/Assets/3D/Plants/Urb_Street_Grass_Dry_01/StaticMeshes/"
        "SM_Urb_Street_Grass_Dry_01_C"
    ),
    "grass_d": (
        "/Game/MilitaryTrench/Assets/3D/Plants/Urb_Street_Grass_Dry_01/StaticMeshes/"
        "SM_Urb_Street_Grass_Dry_01_D"
    ),
}


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


def actor_tags(actor):
    return [str(item) for item in actor.tags]


def actor_site(actor):
    for value in actor_tags(actor):
        if value.startswith("Building_SS_"):
            return value[len("Building_"):]
    for value in actor_tags(actor):
        if value.startswith("SS_") and len(value) == 6:
            return value
    return ""


def point_in_expanded_bounds(x, y, actor, expansion):
    origin, extent = actor.get_actor_bounds(False)
    return (
        origin.x - extent.x - expansion <= x <= origin.x + extent.x + expansion
        and origin.y - extent.y - expansion <= y <= origin.y + extent.y + expansion
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
    if actor_handle is None:
        raise RuntimeError("ABIVERD_WALL_FOOT_ACTOR_HANDLE_MISSING")
    if root_handle is None:
        root_handle, failure = subsystem.add_new_subobject(
            unreal.AddNewSubobjectParams(parent_handle=actor_handle, new_class=unreal.SceneComponent.static_class())
        )
        if not failure.is_empty():
            raise RuntimeError("ABIVERD_WALL_FOOT_ROOT_CREATE_FAILED " + str(failure))
        subsystem.rename_subobject(root_handle, unreal.Text("DefaultSceneRoot"))
    return actor_handle, root_handle


def world_transform(row):
    transform = unreal.Transform()
    transform.translation = unreal.Vector(*row["location_cm"])
    transform.rotation = unreal.MathLibrary.conv_rotator_to_quaternion(
        unreal.Rotator(roll=0.0, pitch=0.0, yaw=row["yaw"])
    )
    transform.scale3d = unreal.Vector(row["scale"], row["scale"], row["scale"])
    return transform


project_name = os.path.splitext(os.path.basename(unreal.Paths.get_project_file_path()))[0]
project_directory = os.path.abspath(unreal.Paths.project_dir()).replace("\\", "/").rstrip("/")
level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).get_current_level()
level_path = level.get_outermost().get_name() if level else ""
if project_name != EXPECTED_PROJECT or not project_directory.endswith(EXPECTED_DIRECTORY_SUFFIX):
    raise RuntimeError("ABIVERD_WALL_FOOT_WRONG_PROJECT")
if level_path != EXPECTED_LEVEL:
    raise RuntimeError("ABIVERD_WALL_FOOT_WRONG_LEVEL " + level_path)
if dirty_packages():
    raise RuntimeError("ABIVERD_WALL_FOOT_DIRTY_BEFORE " + "|".join(dirty_packages()))

descriptors = list(unreal.WorldPartitionBlueprintLibrary.get_intersecting_actor_descs(WORKING_BOX))
unreal.WorldPartitionBlueprintLibrary.load_actors([item.guid for item in descriptors])
unreal.WorldPartitionBlueprintLibrary.pin_actors([item.guid for item in descriptors])
if dirty_packages():
    raise RuntimeError("ABIVERD_WALL_FOOT_LOAD_DIRTY")

actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
actors = list(actor_subsystem.get_all_level_actors())
if any(PASS_TAG in actor.tags or actor.get_actor_label() == ACTOR_LABEL for actor in actors):
    raise RuntimeError("ABIVERD_WALL_FOOT_DUPLICATE")

mesh_assets = {}
mesh_min_z = {}
for key, path in MESHES.items():
    asset = unreal.EditorAssetLibrary.load_asset(path)
    if not isinstance(asset, unreal.StaticMesh):
        raise RuntimeError("ABIVERD_WALL_FOOT_MISSING_MESH " + path)
    mesh_assets[key] = asset
    mesh_min_z[key] = float(asset.get_bounding_box().min.z)

door_actors = [
    actor
    for actor in actors
    if actor_site(actor) in TARGET_SITES
    and ("door" in actor.get_actor_label().lower() or "threshold" in actor.get_actor_label().lower())
]
wall_rows = []
for actor in actors:
    if not isinstance(actor, unreal.StaticMeshActor):
        continue
    match = WALL_PATTERN.match(actor.get_actor_label())
    if not match:
        continue
    site, side, suffix = match.groups()
    if site not in TARGET_SITES or "Interior" in actor.get_actor_label():
        continue
    origin, extent = actor.get_actor_bounds(False)
    length = extent.x * 2.0 if side in ("N", "S") else extent.y * 2.0
    if length < 300.0 or extent.z * 2.0 < 200.0:
        continue
    wall_rows.append({"actor": actor, "site": site, "side": side, "suffix": suffix, "origin": origin, "extent": extent, "length": length})
wall_rows.sort(key=lambda row: (row["site"], row["actor"].get_actor_label()))
if len(wall_rows) < 25:
    raise RuntimeError("ABIVERD_WALL_FOOT_WALL_SCOPE_TOO_SMALL %d" % len(wall_rows))

trace_ignored = [
    actor
    for actor in actors
    if not isinstance(actor, unreal.LandscapeProxy) and not actor.get_actor_label().startswith("Ground_")
]


def support_z(x, y):
    hit = unreal.SystemLibrary.line_trace_single(
        world,
        unreal.Vector(x, y, 100000.0),
        unreal.Vector(x, y, -100000.0),
        unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
        True,
        trace_ignored,
        unreal.DrawDebugTrace.NONE,
        True,
    )
    data = hit.to_dict() if hit is not None else {}
    if not data.get("blocking_hit") or data.get("location") is None:
        return None, ""
    support_actor = data.get("hit_actor")
    return float(data["location"].z), support_actor.get_actor_label() if support_actor else ""


randomizer = random.Random(SEED)
instances = {key: [] for key in MESHES}
rejected = []
wall_summary = []
for wall in wall_rows:
    length = wall["length"]
    sample_count = 1 if length < 850.0 else (2 if length < 1800.0 else 3)
    accepted_for_wall = 0
    for index in range(sample_count):
        fraction = (index + 1.0) / (sample_count + 1.0)
        fraction += randomizer.uniform(-0.08, 0.08) / max(sample_count, 1)
        origin = wall["origin"]
        extent = wall["extent"]
        side = wall["side"]
        offset = 42.0 + randomizer.uniform(0.0, 24.0)
        if side in ("N", "S"):
            x = origin.x - extent.x + fraction * extent.x * 2.0
            y = origin.y + (extent.y + offset) * (1.0 if side == "N" else -1.0)
        else:
            x = origin.x + (extent.x + offset) * (1.0 if side == "E" else -1.0)
            y = origin.y - extent.y + fraction * extent.y * 2.0
        nearest_door = [door.get_actor_label() for door in door_actors if point_in_expanded_bounds(x, y, door, 165.0)]
        if nearest_door:
            rejected.append({"wall": wall["actor"].get_actor_label(), "reason": "door_clearance", "doors": nearest_door})
            continue
        ground_z, support_actor = support_z(x, y)
        if ground_z is None:
            rejected.append({"wall": wall["actor"].get_actor_label(), "reason": "support_trace_failed"})
            continue
        hard_key = "rubble" if randomizer.random() < 0.62 else "rock_patch"
        hard_scale = randomizer.uniform(0.82, 1.08)
        hard_yaw = randomizer.uniform(0.0, 360.0)
        hard_z = ground_z - mesh_min_z[hard_key] * hard_scale
        hard_row = {
            "site": wall["site"],
            "wall": wall["actor"].get_actor_label(),
            "support_actor": support_actor,
            "location_cm": [round(x, 3), round(y, 3), round(hard_z, 3)],
            "yaw": round(hard_yaw, 3),
            "scale": round(hard_scale, 4),
        }
        instances[hard_key].append(hard_row)

        grass_key = randomizer.choice(("grass_a", "grass_b", "grass_c", "grass_d"))
        angle = math.radians(randomizer.uniform(0.0, 360.0))
        grass_x = x + math.cos(angle) * randomizer.uniform(28.0, 55.0)
        grass_y = y + math.sin(angle) * randomizer.uniform(28.0, 55.0)
        if not any(point_in_expanded_bounds(grass_x, grass_y, door, 165.0) for door in door_actors):
            grass_ground_z, grass_support = support_z(grass_x, grass_y)
            if grass_ground_z is not None:
                grass_scale = randomizer.uniform(0.72, 1.02)
                grass_z = grass_ground_z - mesh_min_z[grass_key] * grass_scale
                instances[grass_key].append(
                    {
                        "site": wall["site"],
                        "wall": wall["actor"].get_actor_label(),
                        "support_actor": grass_support,
                        "location_cm": [round(grass_x, 3), round(grass_y, 3), round(grass_z, 3)],
                        "yaw": round(randomizer.uniform(0.0, 360.0), 3),
                        "scale": round(grass_scale, 4),
                    }
                )
        accepted_for_wall += 1
    wall_summary.append(
        {"site": wall["site"], "wall": wall["actor"].get_actor_label(), "requested": sample_count, "accepted": accepted_for_wall}
    )

hard_count = len(instances["rubble"]) + len(instances["rock_patch"])
grass_count = sum(len(instances[key]) for key in ("grass_a", "grass_b", "grass_c", "grass_d"))
if hard_count < 40 or grass_count < 35:
    raise RuntimeError("ABIVERD_WALL_FOOT_DENSITY_TOO_SMALL hard=%d grass=%d" % (hard_count, grass_count))

created_components = []
saved_packages = []
created_actor_package = ""
if APPLY_CHANGES:
    dressing_actor = actor_subsystem.spawn_actor_from_class(
        unreal.Actor, unreal.Vector(0.0, 0.0, 0.0), unreal.Rotator(), transient=False
    )
    if dressing_actor is None:
        raise RuntimeError("ABIVERD_WALL_FOOT_SPAWN_FAILED")
    dressing_actor.set_actor_label(ACTOR_LABEL)
    dressing_actor.set_folder_path(unreal.Name(FOLDER))
    dressing_actor.tags = [PASS_TAG, unreal.Name("AbiverdVisualConversionV1"), unreal.Name("MapArtOnly")]
    created_actor_package = package_name(dressing_actor.get_package())
    subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
    if subsystem is None:
        raise RuntimeError("ABIVERD_WALL_FOOT_SUBOBJECT_SUBSYSTEM_MISSING")
    _actor_handle, root_handle = actor_and_root_handles(subsystem, dressing_actor)
    for key in MESHES:
        rows = instances[key]
        if not rows:
            continue
        component_handle, failure = subsystem.add_new_subobject(
            unreal.AddNewSubobjectParams(
                parent_handle=root_handle,
                new_class=unreal.HierarchicalInstancedStaticMeshComponent.static_class(),
            )
        )
        if not failure.is_empty():
            raise RuntimeError("ABIVERD_WALL_FOOT_COMPONENT_CREATE_FAILED " + str(failure))
        component_name = "HISM_WallFoot_" + key.title().replace("_", "")
        subsystem.rename_subobject(component_handle, unreal.Text(component_name))
        component_data = unreal.SubobjectDataBlueprintFunctionLibrary.get_data(component_handle)
        component = unreal.SubobjectDataBlueprintFunctionLibrary.get_associated_object(component_data)
        if not isinstance(component, unreal.HierarchicalInstancedStaticMeshComponent):
            raise RuntimeError("ABIVERD_WALL_FOOT_COMPONENT_TYPE_FAILED " + component_name)
        component.set_static_mesh(mesh_assets[key])
        component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        component.set_collision_profile_name("NoCollision")
        try:
            component.set_editor_property("can_ever_affect_navigation", False)
        except Exception:
            pass
        is_grass = key.startswith("grass_")
        component.set_editor_property("cast_shadow", not is_grass)
        component.set_editor_property("instance_start_cull_distance", 8000 if is_grass else 16000)
        component.set_editor_property("instance_end_cull_distance", 26000 if is_grass else 48000)
        for row in rows:
            component.add_instance_world_space(world_transform(row))
        created_components.append(
            {
                "component": component_name,
                "mesh": MESHES[key],
                "instance_count": component.get_instance_count(),
                "collision": str(component.get_collision_enabled()),
                "cast_shadow": bool(component.cast_shadow),
                "start_cull_distance": int(component.instance_start_cull_distance),
                "end_cull_distance": int(component.instance_end_cull_distance),
            }
        )
    before_save = dirty_packages()
    allowed_prefixes = (
        "/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/",
        "/Game/__ExternalObjects__/Maps/Blockout/Lvl_Blockout_01/",
    )
    unexpected = [name for name in before_save if not name.startswith(allowed_prefixes)]
    if unexpected:
        raise RuntimeError("ABIVERD_WALL_FOOT_UNEXPECTED_DIRTY " + "|".join(unexpected))
    packages = list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
    saved_packages = sorted(package_name(package) for package in packages)
    if not unreal.EditorLoadingAndSavingUtils.save_packages(packages, True):
        raise RuntimeError("ABIVERD_WALL_FOOT_SAVE_FAILED")
    if dirty_packages():
        raise RuntimeError("ABIVERD_WALL_FOOT_DIRTY_AFTER_SAVE " + "|".join(dirty_packages()))

report = {
    "schema_version": 1,
    "status": "applied_and_saved" if APPLY_CHANGES else "dry_run_complete",
    "context": {"project": project_name, "project_directory": project_directory, "level": level_path},
    "seed": SEED,
    "target_sites": sorted(TARGET_SITES),
    "wall_segment_count": len(wall_rows),
    "door_clearance_actor_count": len(door_actors),
    "hard_instance_count": hard_count,
    "grass_instance_count": grass_count,
    "total_instance_count": hard_count + grass_count,
    "instance_counts": {key: len(rows) for key, rows in instances.items()},
    "instances": instances,
    "wall_summary": wall_summary,
    "rejected": rejected,
    "created_actor_label": ACTOR_LABEL if APPLY_CHANGES else "",
    "created_actor_package": created_actor_package,
    "created_components": created_components,
    "saved_packages": saved_packages,
    "policies": {
        "performance": "one actor and at most six HISM components; Nanite source meshes; distance culling; grass shadows disabled",
        "gameplay": "decorative only; NoCollision; no navigation contribution; default non-replicated actor; no tick",
        "placement": "deterministic seed; ground-floor exterior walls only; support traced; 165 cm door/threshold exclusion",
    },
    "dirty_after": dirty_packages(),
}
report_root = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
os.makedirs(report_root, exist_ok=True)
report_path = os.path.join(report_root, REPORT_NAME)
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(report, handle, indent=2)
    handle.write("\n")
unreal.log(
    "ABIVERD_WALL_FOOT_COMPLETE apply=%s walls=%d hard=%d grass=%d total=%d"
    % (APPLY_CHANGES, len(wall_rows), hard_count, grass_count, hard_count + grass_count)
)
print("ABIVERD_WALL_FOOT_COMPLETE", report_path)
