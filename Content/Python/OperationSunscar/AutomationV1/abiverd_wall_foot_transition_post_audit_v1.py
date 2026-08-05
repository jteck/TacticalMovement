"""Read-only post-apply audit for the Old Town wall-foot HISM pass."""

import json
import os

import unreal


EXPECTED_PROJECT = "TacticalMovement"
EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development"
EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
ACTOR_LABEL = "ABV_OldTown_WallFoot_HISM_V1"
PASS_TAG = unreal.Name("SunscarAbiverdWallFootHISMV1")
WORKING_BOX = unreal.Box(
    min=unreal.Vector(-12500.0, -11500.0, -100000.0),
    max=unreal.Vector(15500.0, 11500.0, 100000.0),
)
EXPECTED_COMPONENTS = {
    "HISM_WallFoot_Rubble": {
        "mesh": "/Game/Maps/Sunscar/Art/Quixel/Downloaded/FAB_P1A_012_ydyqbjds/Military_Trenches_Debris_Patch_Rock_Corner_ydyqbjds_High",
        "instances": 53,
        "start_cull": 16000,
        "end_cull": 48000,
        "cast_shadow": True,
    },
    "HISM_WallFoot_RockPatch": {
        "mesh": "/Game/Maps/Sunscar/Art/Quixel/Downloaded/FAB_P1A_012_ydyqbjds/Military_Trenches_Debris_Patch_Rock_Corner_ydyqbjds_High",
        "instances": 31,
        "start_cull": 16000,
        "end_cull": 48000,
        "cast_shadow": True,
    },
    "HISM_WallFoot_GrassA": {
        "mesh": "/Game/Maps/Sunscar/Art/Quixel/Downloaded/FAB_P1A_015_tbbqejqr/Dry_Grass_tbbqejqr_High_tbbqejqr_VarA_LOD0",
        "instances": 28,
        "start_cull": 8000,
        "end_cull": 26000,
        "cast_shadow": False,
    },
    "HISM_WallFoot_GrassB": {
        "mesh": "/Game/Maps/Sunscar/Art/Quixel/Downloaded/FAB_P1A_015_tbbqejqr/Dry_Grass_tbbqejqr_High_tbbqejqr_VarA_LOD0",
        "instances": 16,
        "start_cull": 8000,
        "end_cull": 26000,
        "cast_shadow": False,
    },
    "HISM_WallFoot_GrassC": {
        "mesh": "/Game/Maps/Sunscar/Art/Quixel/Downloaded/FAB_P1A_015_tbbqejqr/Dry_Grass_tbbqejqr_High_tbbqejqr_VarA_LOD0",
        "instances": 20,
        "start_cull": 8000,
        "end_cull": 26000,
        "cast_shadow": False,
    },
    "HISM_WallFoot_GrassD": {
        "mesh": "/Game/Maps/Sunscar/Art/Quixel/Downloaded/FAB_P1A_015_tbbqejqr/Dry_Grass_tbbqejqr_High_tbbqejqr_VarA_LOD0",
        "instances": 19,
        "start_cull": 8000,
        "end_cull": 26000,
        "cast_shadow": False,
    },
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


def asset_path(asset):
    return asset.get_outermost().get_name() if asset else ""


project_name = os.path.splitext(os.path.basename(unreal.Paths.get_project_file_path()))[0]
project_directory = os.path.abspath(unreal.Paths.project_dir()).replace("\\", "/").rstrip("/")
level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).get_current_level()
level_path = level.get_outermost().get_name() if level else ""
if project_name != EXPECTED_PROJECT or not project_directory.endswith(EXPECTED_DIRECTORY_SUFFIX):
    raise RuntimeError("ABIVERD_WALL_FOOT_AUDIT_WRONG_PROJECT")
if level_path != EXPECTED_LEVEL:
    raise RuntimeError("ABIVERD_WALL_FOOT_AUDIT_WRONG_LEVEL " + level_path)
if dirty_packages():
    raise RuntimeError("ABIVERD_WALL_FOOT_AUDIT_DIRTY_BEFORE " + "|".join(dirty_packages()))

descriptors = list(unreal.WorldPartitionBlueprintLibrary.get_intersecting_actor_descs(WORKING_BOX))
unreal.WorldPartitionBlueprintLibrary.load_actors([item.guid for item in descriptors])
unreal.WorldPartitionBlueprintLibrary.pin_actors([item.guid for item in descriptors])
if dirty_packages():
    raise RuntimeError("ABIVERD_WALL_FOOT_AUDIT_LOAD_DIRTY " + "|".join(dirty_packages()))

actors = list(unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors())
matches = [actor for actor in actors if actor.get_actor_label() == ACTOR_LABEL or PASS_TAG in list(actor.tags)]
if len(matches) != 1:
    raise RuntimeError("ABIVERD_WALL_FOOT_AUDIT_ACTOR_COUNT %d" % len(matches))
actor = matches[0]
if bool(actor.get_editor_property("replicates")):
    raise RuntimeError("ABIVERD_WALL_FOOT_AUDIT_REPLICATES")

components = list(actor.get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent))
components_by_name = {component.get_name(): component for component in components}
if set(components_by_name) != set(EXPECTED_COMPONENTS):
    raise RuntimeError("ABIVERD_WALL_FOOT_AUDIT_COMPONENTS " + repr(sorted(components_by_name)))

records = []
for name, expected in sorted(EXPECTED_COMPONENTS.items()):
    component = components_by_name[name]
    try:
        affects_navigation = bool(component.get_editor_property("can_ever_affect_navigation"))
    except Exception:
        affects_navigation = None
    row = {
        "component": name,
        "instances": component.get_instance_count(),
        "mesh": asset_path(component.get_editor_property("static_mesh")),
        "collision": str(component.get_collision_enabled()),
        "affects_navigation": affects_navigation,
        "cast_shadow": bool(component.get_editor_property("cast_shadow")),
        "start_cull_cm": int(component.get_editor_property("instance_start_cull_distance")),
        "end_cull_cm": int(component.get_editor_property("instance_end_cull_distance")),
    }
    if row["instances"] != expected["instances"] or row["mesh"] != expected["mesh"]:
        raise RuntimeError("ABIVERD_WALL_FOOT_AUDIT_CONTENT " + repr(row))
    if component.get_collision_enabled() != unreal.CollisionEnabled.NO_COLLISION:
        raise RuntimeError("ABIVERD_WALL_FOOT_AUDIT_COLLISION " + repr(row))
    if affects_navigation is True:
        raise RuntimeError("ABIVERD_WALL_FOOT_AUDIT_NAVIGATION " + repr(row))
    if row["cast_shadow"] != expected["cast_shadow"]:
        raise RuntimeError("ABIVERD_WALL_FOOT_AUDIT_SHADOW " + repr(row))
    if row["start_cull_cm"] != expected["start_cull"] or row["end_cull_cm"] != expected["end_cull"]:
        raise RuntimeError("ABIVERD_WALL_FOOT_AUDIT_CULL " + repr(row))
    records.append(row)

dirty_after = dirty_packages()
if dirty_after:
    raise RuntimeError("ABIVERD_WALL_FOOT_AUDIT_DIRTY_AFTER " + "|".join(dirty_after))
report = {
    "schema_version": 1,
    "status": "post_apply_audit_passed",
    "context": {"project": project_name, "project_directory": project_directory, "level": level_path},
    "actor": ACTOR_LABEL,
    "actor_package": package_name(actor.get_package()),
    "replicates": bool(actor.get_editor_property("replicates")),
    "component_count": len(records),
    "instance_count": sum(item["instances"] for item in records),
    "components": records,
    "dirty_after": dirty_after,
}
report_root = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
os.makedirs(report_root, exist_ok=True)
report_path = os.path.join(report_root, "abiverd_wall_foot_transition_post_audit_v1.json")
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(report, handle, indent=2)
    handle.write("\n")
unreal.log("ABIVERD_WALL_FOOT_POST_AUDIT_PASS instances=167 components=6")
print("ABIVERD_WALL_FOOT_POST_AUDIT_PASS", report_path)
