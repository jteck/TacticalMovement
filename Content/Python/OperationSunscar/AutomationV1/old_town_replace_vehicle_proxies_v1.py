"""Dry-run-first replacement of five vehicle proxies with City Sample meshes."""

import os
import sys

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIRECTORY not in sys.path:
    sys.path.insert(0, SCRIPT_DIRECTORY)

import sunscar_automation_common as common


TAG = unreal.Name("SunscarOldTownVehicleReplacementV1")
PROXY_MESH = "/Game/LevelPrototyping/Meshes/SM_ChamferCube.SM_ChamferCube"
MAPPINGS = (
    (
        "Salvage_Vehicle_01",
        "/Game/CitySampleVehicles/vehicle13_Car/Mesh/SM_vehCar_vehicle13_LOD",
        0.8334,
        339.17,
    ),
    (
        "Salvage_Vehicle_02",
        "/Game/CitySampleVehicles/vehicle09_Van/Mesh/SM_vehVan_vehicle09_LOD",
        0.7196,
        306.85,
    ),
    (
        "Salvage_Vehicle_03",
        "/Game/CitySampleVehicles/vehicle09_Van/Mesh/SM_vehVan_vehicle09_LOD",
        0.7196,
        24.27,
    ),
    (
        "MotorPool_Vehicle_A",
        "/Game/CitySampleVehicles/vehicle13_Car/Mesh/SM_vehCar_vehicle13_LOD",
        0.8153,
        173.04,
    ),
    (
        "MotorPool_Vehicle_B",
        "/Game/CitySampleVehicles/vehicle01_Van/Mesh/SM_vehVan_vehicle01_LOD",
        0.9393,
        272.85,
    ),
)

config = common.load_config()
apply_requested = bool(config["execution"].get("apply_changes", False))
context = common.require_safe_context(config, write_requested=apply_requested)
if apply_requested:
    dirty_content = list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
    dirty_maps = list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
    if dirty_content or dirty_maps:
        raise RuntimeError(
            "SUNSCAR_VEHICLE_REPLACE_APPLY_REFUSED preexisting_content=%d preexisting_maps=%d"
            % (len(dirty_content), len(dirty_maps))
        )

by_label = {actor.get_actor_label(): actor for actor in common.actor_subsystem().get_all_level_actors()}
records = []
for label, mesh_path, target_scale, target_yaw in MAPPINGS:
    actor = by_label.get(label)
    if actor is None:
        raise RuntimeError("SUNSCAR_VEHICLE_REPLACE_MISSING " + label)
    component = getattr(actor, "static_mesh_component", None)
    if component is None:
        raise RuntimeError("SUNSCAR_VEHICLE_REPLACE_NO_COMPONENT " + label)
    source_path = common.actor_mesh_path(actor)
    target_mesh = common.load_asset_checked(config, mesh_path)
    if not isinstance(target_mesh, unreal.StaticMesh):
        raise RuntimeError("SUNSCAR_VEHICLE_REPLACE_TARGET_NOT_MESH " + mesh_path)
    if source_path not in (PROXY_MESH, target_mesh.get_path_name()):
        raise RuntimeError("SUNSCAR_VEHICLE_REPLACE_UNEXPECTED_SOURCE %s %s" % (label, source_path))
    before_origin, before_extent = actor.get_actor_bounds(False)
    before_bottom = before_origin.z - before_extent.z
    before_location = actor.get_actor_location()
    before_rotation = actor.get_actor_rotation()
    before_scale = actor.get_actor_scale3d()
    target_size = target_mesh.get_bounds().box_extent * (2.0 * target_scale)
    record = {
        "label": label,
        "source_mesh": source_path,
        "target_mesh": target_mesh.get_path_name(),
        "before_location_cm": [round(before_location.x, 3), round(before_location.y, 3), round(before_location.z, 3)],
        "before_bottom_z_cm": round(before_bottom, 3),
        "before_rotation": {"pitch": round(before_rotation.pitch, 3), "yaw": round(before_rotation.yaw, 3), "roll": round(before_rotation.roll, 3)},
        "before_scale": [round(before_scale.x, 4), round(before_scale.y, 4), round(before_scale.z, 4)],
        "target_scale": target_scale,
        "target_yaw": target_yaw,
        "target_unrotated_size_cm": [round(target_size.x, 3), round(target_size.y, 3), round(target_size.z, 3)],
        "package": actor.get_package().get_name(),
    }
    if apply_requested:
        actor.modify()
        component.modify()
        component.set_editor_property("override_materials", [])
        component.set_editor_property("static_mesh", target_mesh)
        actor.set_actor_scale3d(unreal.Vector(target_scale, target_scale, target_scale))
        actor.set_actor_rotation(unreal.Rotator(roll=0.0, pitch=0.0, yaw=target_yaw), False)
        after_origin, after_extent = actor.get_actor_bounds(False)
        after_bottom = after_origin.z - after_extent.z
        actor.add_actor_world_offset(
            unreal.Vector(0.0, 0.0, before_bottom - after_bottom),
            False,
            False,
        )
        component.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
        if TAG not in list(actor.tags):
            actor.tags = list(actor.tags) + [TAG, unreal.Name("CitySampleStaticVehicle")]
        final_origin, final_extent = actor.get_actor_bounds(False)
        record["after_location_cm"] = [round(value, 3) for value in (final_origin.x, final_origin.y, actor.get_actor_location().z)]
        record["after_bottom_z_cm"] = round(final_origin.z - final_extent.z, 3)
        record["after_extent_cm"] = [round(final_extent.x, 3), round(final_extent.y, 3), round(final_extent.z, 3)]
        record["after_materials"] = [
            component.get_material(index).get_path_name() if component.get_material(index) else ""
            for index in range(component.get_num_materials())
        ]
    records.append(record)

payload = {
    "schema_version": 1,
    "status": "apply_unsaved_preview_complete" if apply_requested else "dry_run_complete",
    "context": context,
    "actor_count": len(records),
    "records": records,
    "changes_made": apply_requested,
    "level_saved": False,
}
filename = (
    "old_town_replace_vehicle_proxies_apply_preview_v1.json"
    if apply_requested
    else "old_town_replace_vehicle_proxies_dry_run_v1.json"
)
report = common.write_json_report(config, filename, payload)
unreal.log("SUNSCAR_VEHICLE_REPLACE mode=%s actors=%d report=%s" % ("APPLY_UNSAVED" if apply_requested else "DRY_RUN", len(records), report))
print("SUNSCAR_VEHICLE_REPLACE", len(records), report)
