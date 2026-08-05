"""Dry-run-first replacement of Bazaar graybox canopy slabs with Quixel cloth.

The pass adapts the eight existing SS_017 canopy actors.  Their authored
centres remain the spatial authority, the central passage stays open, and the
new cloth is decorative: no collision, no navigation contribution, no tick,
and no replication.
"""

import json
import math
import os

import unreal


APPLY_CHANGES = False
EXPECTED_PROJECT = "TacticalMovement"
EXPECTED_DIRECTORY_SUFFIX = "/UnrealEngine/_worktrees/map-development"
EXPECTED_LEVEL = "/Game/Maps/Blockout/Lvl_Blockout_01"
TARP_MESH_PATH = (
    "/Game/Maps/Sunscar/Art/Heritage/Props/WrinkledTarp/"
    "vieldbo_tier_1/StaticMeshes/vieldbo_tier_1"
)
SOURCE_MESH_PATH = "/Game/LevelPrototyping/Meshes/SM_Cube.SM_Cube"
CANOPY_LABELS = [
    "Bazaar_N_Canopy_01",
    "Bazaar_N_Canopy_02",
    "Bazaar_N_Canopy_03",
    "Bazaar_N_Canopy_04",
    "Bazaar_S_Canopy_01",
    "Bazaar_S_Canopy_02",
    "Bazaar_S_Canopy_03",
    "Bazaar_S_Canopy_04",
]
WORKING_BOX = unreal.Box(
    min=unreal.Vector(500.0, -10400.0, -100000.0),
    max=unreal.Vector(5100.0, -8200.0, 100000.0),
)
REPORT_NAME = (
    "abiverd_bazaar_tarp_canopy_apply_v1.json"
    if APPLY_CHANGES
    else "abiverd_bazaar_tarp_canopy_dry_run_v1.json"
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


def vector_row(value):
    return [round(float(value.x), 3), round(float(value.y), 3), round(float(value.z), 3)]


def rotated_scaled_offset(local_center, scale, yaw_degrees):
    angle = math.radians(yaw_degrees)
    scaled_x = local_center.x * scale
    scaled_y = local_center.y * scale
    return unreal.Vector(
        scaled_x * math.cos(angle) - scaled_y * math.sin(angle),
        scaled_x * math.sin(angle) + scaled_y * math.cos(angle),
        local_center.z * scale,
    )


project_name = os.path.splitext(os.path.basename(unreal.Paths.get_project_file_path()))[0]
project_directory = os.path.abspath(unreal.Paths.project_dir()).replace("\\", "/").rstrip("/")
level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).get_current_level()
level_path = level.get_outermost().get_name() if level else ""
if project_name != EXPECTED_PROJECT or not project_directory.endswith(EXPECTED_DIRECTORY_SUFFIX):
    raise RuntimeError("ABIVERD_BAZAAR_TARP_WRONG_PROJECT")
if level_path != EXPECTED_LEVEL:
    raise RuntimeError("ABIVERD_BAZAAR_TARP_WRONG_LEVEL " + level_path)
if dirty_packages():
    raise RuntimeError("ABIVERD_BAZAAR_TARP_DIRTY_BEFORE " + "|".join(dirty_packages()))

descriptors = list(unreal.WorldPartitionBlueprintLibrary.get_intersecting_actor_descs(WORKING_BOX))
unreal.WorldPartitionBlueprintLibrary.load_actors([item.guid for item in descriptors])
unreal.WorldPartitionBlueprintLibrary.pin_actors([item.guid for item in descriptors])
if dirty_packages():
    raise RuntimeError("ABIVERD_BAZAAR_TARP_LOAD_DIRTY")

tarp_mesh = unreal.EditorAssetLibrary.load_asset(TARP_MESH_PATH)
if not isinstance(tarp_mesh, unreal.StaticMesh):
    raise RuntimeError("ABIVERD_BAZAAR_TARP_MESH_MISSING")
if not bool(tarp_mesh.get_editor_property("nanite_settings").enabled):
    raise RuntimeError("ABIVERD_BAZAAR_TARP_NANITE_DISABLED")

tarp_box = tarp_mesh.get_bounding_box()
tarp_size = tarp_box.max - tarp_box.min
tarp_center = (tarp_box.max + tarp_box.min) * 0.5
if tarp_size.x < 250.0 or tarp_size.y < 130.0 or tarp_size.z > 20.0:
    raise RuntimeError("ABIVERD_BAZAAR_TARP_UNEXPECTED_BOUNDS " + repr(vector_row(tarp_size)))

actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actor_by_label = {actor.get_actor_label(): actor for actor in actor_subsystem.get_all_level_actors()}
missing = [label for label in CANOPY_LABELS if label not in actor_by_label]
if missing:
    raise RuntimeError("ABIVERD_BAZAAR_TARP_MISSING_ACTORS " + "|".join(missing))

rows = []
modified_packages = []
for index, label in enumerate(CANOPY_LABELS):
    actor = actor_by_label[label]
    if not isinstance(actor, unreal.StaticMeshActor):
        raise RuntimeError("ABIVERD_BAZAAR_TARP_ACTOR_TYPE " + label)
    component = actor.static_mesh_component
    source_mesh = component.get_editor_property("static_mesh")
    source_path = source_mesh.get_path_name() if source_mesh else ""
    if source_path not in (SOURCE_MESH_PATH, TARP_MESH_PATH):
        raise RuntimeError("ABIVERD_BAZAAR_TARP_UNEXPECTED_SOURCE %s %s" % (label, source_path))

    old_origin, old_extent = actor.get_actor_bounds(False)
    old_size = old_extent * 2.0
    scale = float(old_size.x) / float(tarp_size.x)
    if not 1.20 <= scale <= 1.45:
        raise RuntimeError("ABIVERD_BAZAAR_TARP_SCALE_OUTSIDE_POLICY %s %.4f" % (label, scale))
    yaw = 180.0 if index % 2 else 0.0
    offset = rotated_scaled_offset(tarp_center, scale, yaw)
    target_location = old_origin - offset
    resulting_size = unreal.Vector(tarp_size.x * scale, tarp_size.y * scale, tarp_size.z * scale)
    underside = float(old_origin.z - resulting_size.z * 0.5)
    estimated_ground = float(old_origin.z - old_size.z * 0.5 - 275.0)
    estimated_clearance = underside - estimated_ground
    corridor_inner_edge = (
        old_origin.y - resulting_size.y * 0.5
        if "_N_" in label
        else old_origin.y + resulting_size.y * 0.5
    )
    row = {
        "label": label,
        "source_mesh": source_path,
        "target_mesh": TARP_MESH_PATH,
        "old_bounds_origin_cm": vector_row(old_origin),
        "old_bounds_size_cm": vector_row(old_size),
        "target_actor_location_cm": vector_row(target_location),
        "target_rotation_deg": [0.0, 0.0, yaw],
        "target_uniform_scale": round(scale, 5),
        "resulting_bounds_size_cm": vector_row(resulting_size),
        "estimated_underside_clearance_cm": round(estimated_clearance, 3),
        "corridor_inner_edge_y_cm": round(corridor_inner_edge, 3),
        "collision": "NoCollision",
        "navigation": False,
        "cast_shadow": True,
    }
    rows.append(row)

    if APPLY_CHANGES:
        component.set_static_mesh(tarp_mesh)
        actor.set_actor_rotation(unreal.Rotator(roll=0.0, pitch=0.0, yaw=yaw), False)
        actor.set_actor_scale3d(unreal.Vector(scale, scale, scale))
        actor.set_actor_location(target_location, False, False)
        component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        component.set_collision_profile_name("NoCollision")
        component.set_editor_property("can_ever_affect_navigation", False)
        component.set_editor_property("cast_shadow", True)
        actor.set_actor_enable_collision(False)
        actor.tags = list(actor.tags) + [unreal.Name("AbiverdBazaarTarpV1"), unreal.Name("MapArtOnly")]
        modified_packages.append(actor.get_package())

north_edges = [row["corridor_inner_edge_y_cm"] for row in rows if "_N_" in row["label"]]
south_edges = [row["corridor_inner_edge_y_cm"] for row in rows if "_S_" in row["label"]]
minimum_corridor_width = min(north_edges) - max(south_edges)
minimum_clearance = min(row["estimated_underside_clearance_cm"] for row in rows)
if minimum_corridor_width < 600.0:
    raise RuntimeError("ABIVERD_BAZAAR_TARP_CORRIDOR_TOO_NARROW %.3f" % minimum_corridor_width)
if minimum_clearance < 250.0:
    raise RuntimeError("ABIVERD_BAZAAR_TARP_CLEARANCE_TOO_LOW %.3f" % minimum_clearance)

saved_packages = []
if APPLY_CHANGES:
    before_save = dirty_packages()
    allowed_prefixes = (
        "/Game/__ExternalActors__/Maps/Blockout/Lvl_Blockout_01/",
        "/Game/__ExternalObjects__/Maps/Blockout/Lvl_Blockout_01/",
    )
    unexpected = [name for name in before_save if not name.startswith(allowed_prefixes)]
    if unexpected:
        raise RuntimeError("ABIVERD_BAZAAR_TARP_UNEXPECTED_DIRTY " + "|".join(unexpected))
    unique_packages = []
    seen = set()
    for package in modified_packages:
        name = package_name(package)
        if name not in seen:
            seen.add(name)
            unique_packages.append(package)
    saved_packages = sorted(package_name(package) for package in unique_packages)
    if not unreal.EditorLoadingAndSavingUtils.save_packages(unique_packages, True):
        raise RuntimeError("ABIVERD_BAZAAR_TARP_SAVE_FAILED")
    if dirty_packages():
        raise RuntimeError("ABIVERD_BAZAAR_TARP_DIRTY_AFTER_SAVE " + "|".join(dirty_packages()))

report = {
    "schema_version": 1,
    "status": "applied_and_saved" if APPLY_CHANGES else "dry_run_complete",
    "context": {"project": project_name, "project_directory": project_directory, "level": level_path},
    "mesh": TARP_MESH_PATH,
    "mesh_bounds_cm": vector_row(tarp_size),
    "nanite_enabled": True,
    "canopy_count": len(rows),
    "minimum_underside_clearance_cm": round(minimum_clearance, 3),
    "minimum_central_passage_width_cm": round(minimum_corridor_width, 3),
    "canopies": rows,
    "saved_packages": saved_packages,
    "policies": {
        "reuse": "adapt the eight existing authored Bazaar canopy actors; create no parallel canopy system",
        "gameplay": "decorative cloth only; NoCollision; no navigation contribution; central passage preserved",
        "performance": "eight static Nanite meshes; opaque two-sided material; no skeletal cloth, simulation, tick or replication",
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
    "ABIVERD_BAZAAR_TARP_COMPLETE apply=%s count=%d clearance=%.1f corridor=%.1f"
    % (APPLY_CHANGES, len(rows), minimum_clearance, minimum_corridor_width)
)
print("ABIVERD_BAZAAR_TARP_COMPLETE", report_path)
