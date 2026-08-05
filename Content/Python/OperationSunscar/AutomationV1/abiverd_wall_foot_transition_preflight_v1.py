"""Read-only preflight for deterministic Old Town wall-foot transitions.

This script inventories structural building shells, door clearances, existing
ground dressing, and the already-owned rubble/grass meshes.  It deliberately
does not create, modify, move, or save any Unreal object.
"""

import json
import os

import unreal


EXPECTED_PROJECT = "TacticalMovement"
EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development"
EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
REPORT_NAME = "abiverd_wall_foot_transition_preflight_v1.json"
WORKING_BOX = unreal.Box(
    min=unreal.Vector(-12500.0, -11500.0, -100000.0),
    max=unreal.Vector(15500.0, 11500.0, 100000.0),
)
ASSET_PATHS = (
    "/Game/Maps/Sunscar/Art/Quixel/Downloaded/FAB_P1A_012_ydyqbjds/"
    "Military_Trenches_Debris_Patch_Rock_Corner_ydyqbjds_High",
    "/Game/Maps/Sunscar/Art/Quixel/Downloaded/FAB_P1A_015_tbbqejqr/"
    "Dry_Grass_tbbqejqr_High_tbbqejqr_VarA_LOD0",
    "/Game/Fab/Megascans/3D/Military_Trenches_Ground_Patch_Rock_S_04_yd0lfcq/"
    "Medium/SM_yd0lfcq_tier_2/StaticMeshes/SM_yd0lfcq_tier_2",
    "/Game/MilitaryTrench/Assets/3D/Plants/Urb_Street_Grass_Dry_01/StaticMeshes/"
    "SM_Urb_Street_Grass_Dry_01_A",
    "/Game/MilitaryTrench/Assets/3D/Plants/Urb_Street_Grass_Dry_01/StaticMeshes/"
    "SM_Urb_Street_Grass_Dry_01_B",
    "/Game/MilitaryTrench/Assets/3D/Plants/Urb_Street_Grass_Dry_01/StaticMeshes/"
    "SM_Urb_Street_Grass_Dry_01_C",
    "/Game/MilitaryTrench/Assets/3D/Plants/Urb_Street_Grass_Dry_01/StaticMeshes/"
    "SM_Urb_Street_Grass_Dry_01_D",
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


def asset_path(asset):
    return asset.get_outermost().get_name() if asset else ""


def tags(actor):
    return [str(item) for item in actor.tags]


def site_from_tags(actor):
    for value in tags(actor):
        if value.startswith("Building_SS_"):
            return value[len("Building_"):]
    for value in tags(actor):
        if value.startswith("SS_") and len(value) == 6:
            return value
    return ""


def bounds_row(actor):
    origin, extent = actor.get_actor_bounds(False)
    row = {
        "label": actor.get_actor_label(),
        "class": actor.get_class().get_name(),
        "site": site_from_tags(actor),
        "tags": sorted(tags(actor)),
        "origin_cm": [round(origin.x, 2), round(origin.y, 2), round(origin.z, 2)],
        "size_cm": [round(extent.x * 2.0, 2), round(extent.y * 2.0, 2), round(extent.z * 2.0, 2)],
        "rotation_deg": [
            round(actor.get_actor_rotation().roll, 2),
            round(actor.get_actor_rotation().pitch, 2),
            round(actor.get_actor_rotation().yaw, 2),
        ],
        "package": package_name(actor.get_package()),
    }
    if isinstance(actor, unreal.StaticMeshActor):
        component = actor.static_mesh_component
        row.update(
            {
                "mesh": asset_path(component.static_mesh),
                "materials": [
                    asset_path(component.get_material(index))
                    for index in range(component.get_num_materials())
                ],
                "collision": str(component.get_collision_enabled()),
                "visible": component.is_visible(),
            }
        )
    return row


project_name = os.path.splitext(os.path.basename(unreal.Paths.get_project_file_path()))[0]
project_directory = os.path.abspath(unreal.Paths.project_dir()).replace("\\", "/").rstrip("/")
level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).get_current_level()
level_path = level.get_outermost().get_name() if level else ""
if project_name != EXPECTED_PROJECT or not project_directory.endswith(EXPECTED_DIRECTORY_SUFFIX):
    raise RuntimeError("ABIVERD_WALL_FOOT_PREFLIGHT_WRONG_PROJECT")
if level_path != EXPECTED_LEVEL:
    raise RuntimeError("ABIVERD_WALL_FOOT_PREFLIGHT_WRONG_LEVEL " + level_path)
if dirty_packages():
    raise RuntimeError("ABIVERD_WALL_FOOT_PREFLIGHT_DIRTY_BEFORE " + "|".join(dirty_packages()))

descriptors = list(unreal.WorldPartitionBlueprintLibrary.get_intersecting_actor_descs(WORKING_BOX))
unreal.WorldPartitionBlueprintLibrary.load_actors([item.guid for item in descriptors])
unreal.WorldPartitionBlueprintLibrary.pin_actors([item.guid for item in descriptors])
if dirty_packages():
    raise RuntimeError("ABIVERD_WALL_FOOT_PREFLIGHT_LOAD_DIRTY")

actors = list(unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors())
building_shells = []
doors = []
existing_dressing = []
for actor in actors:
    actor_tags = tags(actor)
    label_lower = actor.get_actor_label().lower()
    if any(value.startswith("Building_SS_") for value in actor_tags):
        building_shells.append(bounds_row(actor))
    if "door" in label_lower or "threshold" in label_lower:
        if site_from_tags(actor):
            doors.append(bounds_row(actor))
    if (
        any(value.startswith("OT_GROUND_") or value.startswith("OT_VEG_") for value in actor_tags)
        or actor.get_actor_label().startswith(("OT_REMAIN_", "OT_AUTO_", "OT_MARKET_"))
    ):
        existing_dressing.append(bounds_row(actor))

building_shells.sort(key=lambda row: (row["site"], row["label"]))
doors.sort(key=lambda row: (row["site"], row["label"]))
existing_dressing.sort(key=lambda row: (row["site"], row["label"]))
asset_rows = []
for path in ASSET_PATHS:
    asset = unreal.EditorAssetLibrary.load_asset(path)
    if not isinstance(asset, unreal.StaticMesh):
        asset_rows.append({"path": path, "status": "missing_or_not_static_mesh"})
        continue
    box = asset.get_bounding_box()
    size = box.max - box.min
    try:
        nanite = bool(asset.get_editor_property("nanite_settings").enabled)
    except Exception:
        nanite = None
    asset_rows.append(
        {
            "path": path,
            "status": "loaded",
            "size_cm": [round(size.x, 2), round(size.y, 2), round(size.z, 2)],
            "material_slots": len(asset.get_editor_property("static_materials")),
            "nanite_enabled": nanite,
        }
    )

site_summary = {}
for row in building_shells:
    site_summary.setdefault(row["site"], {"building_shells": 0, "door_clearances": 0, "existing_dressing": 0})
    site_summary[row["site"]]["building_shells"] += 1
for row in doors:
    site_summary.setdefault(row["site"], {"building_shells": 0, "door_clearances": 0, "existing_dressing": 0})
    site_summary[row["site"]]["door_clearances"] += 1
for row in existing_dressing:
    site_summary.setdefault(row["site"], {"building_shells": 0, "door_clearances": 0, "existing_dressing": 0})
    site_summary[row["site"]]["existing_dressing"] += 1

dirty_after = dirty_packages()
if dirty_after:
    raise RuntimeError("ABIVERD_WALL_FOOT_PREFLIGHT_DIRTY_AFTER " + "|".join(dirty_after))
report = {
    "schema_version": 1,
    "status": "read_only_complete",
    "context": {"project": project_name, "project_directory": project_directory, "level": level_path},
    "loaded_descriptor_count": len(descriptors),
    "building_shell_count": len(building_shells),
    "door_clearance_count": len(doors),
    "existing_dressing_count": len(existing_dressing),
    "site_summary": site_summary,
    "asset_candidates": asset_rows,
    "building_shells": building_shells,
    "door_clearances": doors,
    "existing_dressing": existing_dressing,
    "policies": {
        "writes": "none",
        "future_placement": "deterministic HISM; terrain-traced; no collision, navigation, replication, or tick",
        "clearance": "exclude doors, thresholds, central routes, spawn envelopes, and climbable ledge approaches",
    },
    "dirty_after": dirty_after,
}
report_root = os.path.join(unreal.Paths.project_saved_dir(), "OperationSunscar", "Reports")
os.makedirs(report_root, exist_ok=True)
report_path = os.path.join(report_root, REPORT_NAME)
with open(report_path, "w", encoding="utf-8") as handle:
    json.dump(report, handle, indent=2)
    handle.write("\n")
unreal.log(
    "ABIVERD_WALL_FOOT_PREFLIGHT_COMPLETE shells=%d doors=%d dressing=%d"
    % (len(building_shells), len(doors), len(existing_dressing))
)
print("ABIVERD_WALL_FOOT_PREFLIGHT_COMPLETE", report_path)
