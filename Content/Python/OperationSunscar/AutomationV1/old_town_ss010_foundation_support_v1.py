"""Add one reviewed stone support plinth below the unsupported west half of SS_010, unsaved."""

import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


PASS_TAG = unreal.Name("SunscarSS010FoundationSupportV1")
LABEL = "Foundation_SS_010_West_Support"
FOLDER = "OldTown_GroundSurfacePass/SS_010/DetentionTerrace"
CUBE_PATH = "/Game/LevelPrototyping/Meshes/SM_Cube.SM_Cube"
MATERIAL_PATH = "/Game/Maps/Sunscar/Art/Materials/Ground/WorldAligned/MI_OT_SandstoneStone_WorldAligned"
LOCATION = unreal.Vector(1350.0, 9100.0, 34954.8)
SCALE = unreal.Vector(17.0, 28.0, 0.6)
EXPECTED_EXTENT = unreal.Vector(850.0, 1400.0, 30.0)


config = common.load_config()
context = common.require_safe_context(config, write_requested=True)
surface_report = common.read_json(
    os.path.join(common.report_directory(config), "old_town_horizontal_surface_finish_v1.json")
)
expected_dirty_before = sorted(surface_report.get("dirty_map_packages", []))
existing = [
    actor
    for actor in common.actor_subsystem().get_all_level_actors()
    if actor.get_actor_label() == LABEL or str(PASS_TAG) in common.actor_tags(actor)
]
if len(existing) > 1:
    raise RuntimeError("SUNSCAR_SS010_SUPPORT_DUPLICATE_REFUSED count=%d" % len(existing))
expected_existing_packages = {actor.get_package().get_name() for actor in existing}
dirty_content_before = sorted(
    package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()
)
dirty_maps_before = sorted(
    package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
)
allowed_dirty_before = sorted(set(expected_dirty_before) | expected_existing_packages)
if dirty_content_before or dirty_maps_before != allowed_dirty_before or len(expected_dirty_before) != 44:
    raise RuntimeError(
        "SUNSCAR_SS010_SUPPORT_DIRTY_BEFORE_REFUSED content=%s maps=%s"
        % ("|".join(dirty_content_before), "|".join(dirty_maps_before))
    )

cube = common.load_asset_checked(config, CUBE_PATH)
material = common.load_asset_checked(config, MATERIAL_PATH)
actor = existing[0] if existing else common.actor_subsystem().spawn_actor_from_object(
    cube, LOCATION, unreal.Rotator(roll=0.0, pitch=0.0, yaw=0.0), transient=False
)
if not isinstance(actor, unreal.StaticMeshActor):
    raise RuntimeError("SUNSCAR_SS010_SUPPORT_SPAWN_FAILED")
actor.set_actor_scale3d(SCALE)
actor.set_actor_label(LABEL)
actor.set_folder_path(unreal.Name(FOLDER))
actor.tags = [
    PASS_TAG,
    unreal.Name("SunscarMapOwned"),
    unreal.Name("SS_010"),
    unreal.Name("FoundationSkirt"),
    unreal.Name("VisualGroundSupport"),
]
actor.static_mesh_component.set_material(0, material)
actor.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
origin, extent = actor.get_actor_bounds(False)
actor.add_actor_world_offset(LOCATION - origin, False, False)
origin, extent = actor.get_actor_bounds(False)
if (
    abs(origin.x - LOCATION.x) > 0.1
    or abs(origin.y - LOCATION.y) > 0.1
    or abs(origin.z - LOCATION.z) > 0.1
    or abs(extent.x - EXPECTED_EXTENT.x) > 0.1
    or abs(extent.y - EXPECTED_EXTENT.y) > 0.1
    or abs(extent.z - EXPECTED_EXTENT.z) > 0.1
):
    raise RuntimeError(
        "SUNSCAR_SS010_SUPPORT_BOUNDS_REFUSED origin=%s extent=%s" % (origin, extent)
    )

dirty_content_after = sorted(
    package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()
)
dirty_maps_after = sorted(
    package.get_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
)
actor_package = actor.get_package().get_name()
expected_after = sorted(set(expected_dirty_before) | {actor_package})
unexpected = sorted(set(dirty_maps_after) - set(expected_after))
missing = sorted(set(expected_after) - set(dirty_maps_after))
if dirty_content_after or unexpected or missing:
    raise RuntimeError(
        "SUNSCAR_SS010_SUPPORT_DIRTY_AFTER_REFUSED content=%s unexpected=%s missing=%s"
        % ("|".join(dirty_content_after), "|".join(unexpected), "|".join(missing))
    )

payload = {
    "schema_version": 1,
    "status": "unsaved_ss010_foundation_support_ready",
    "context": context,
    "actor_count": 1,
    "label": LABEL,
    "folder": FOLDER,
    "location_cm": [LOCATION.x, LOCATION.y, LOCATION.z],
    "scale": [SCALE.x, SCALE.y, SCALE.z],
    "extent_cm": [extent.x, extent.y, extent.z],
    "material": material.get_path_name(),
    "actor_package": actor_package,
    "prior_surface_package_count": len(expected_dirty_before),
    "dirty_content_packages": dirty_content_after,
    "dirty_map_packages": dirty_maps_after,
    "changes_made": True,
    "changes_saved": False,
}
report = common.write_json_report(config, "old_town_ss010_foundation_support_v1.json", payload)
unreal.log("SUNSCAR_SS010_SUPPORT actor=%s report=%s" % (LABEL, report))
print("SUNSCAR_SS010_SUPPORT", LABEL, report)
